import logging
from typing import List, Dict, Any, Optional

# --- Add Pydantic imports ---
from pydantic import BaseModel, Field, PositiveInt, PositiveFloat

import numpy as np
import talib.abstract as ta
from pandas import DataFrame
import pandas as pd

from freqtrade.strategy import CategoricalParameter, IntParameter, IStrategy, RealParameter
from freqtrade.freqai.prediction_models.ReinforcementLearner import ReinforcementLearner

logger = logging.getLogger(__name__)

# --- Pydantic Models kept inside for encapsulation ---
class PolicyKwargs(BaseModel):
    net_arch: Optional[List[int]] = None
    activation_fn: Optional[str] = None
    dropout: Optional[PositiveFloat] = Field(None, ge=0.0, le=1.0)
    use_batch_norm: Optional[bool] = None

class RewardParams(BaseModel):
    rr: Optional[PositiveInt] = None
    profit_aim: Optional[PositiveFloat] = None

class RLConfigModel(BaseModel):
    train_cycles: Optional[PositiveInt] = None
    add_state_info: Optional[bool] = None
    max_trade_duration_candles: PositiveInt
    max_training_drawdown_pct: PositiveFloat = Field(..., ge=0.0, le=1.0)
    cpu_count: Optional[PositiveInt] = None
    model_type: str
    policy_type: str
    seed: Optional[int] = None
    policy_kwargs: Optional[PolicyKwargs] = None
    total_timesteps: Optional[PositiveInt] = None
    model_reward_parameters: Optional[RewardParams] = None
    model_training_parameters: Optional[Dict[str, Any]] = {}

class RagsToRichesRLModel(ReinforcementLearner):
    # ... (Keep existing model code)
    pass # Placeholder if the RL model code was moved to a separate file as intended

class KrakenFreqAI(IStrategy):
    """
    Micro-trade FreqAI strategy on Kraken/BTC markets.
    Timeframes: 5m, 15m, 1h. Micro-stakes (~0.0002BTC), z-score gating.
    """

    timeframe = "5m"
    # --- Static assignments (used if not hyperopted) ---
    minimal_roi = {"0": 0.169, "40": 0.051, "66": 0.038, "171": 0}
    stoploss = -0.047
    trailing_stop = True
    trailing_stop_positive = 0.267
    trailing_stop_positive_offset = 0.315
    trailing_only_offset_is_reached = True

    # --- Dummy Hyperopt parameters REMOVED ---
    # minimal_roi_hyp = IntParameter(10, 100, default=int(minimal_roi["0"]*1000), space='roi', optimize=False, load=False)
    # stoploss_hyp = RealParameter(-0.10, -0.01, default=stoploss, space='stoploss', optimize=False, load=False)
    # trailing_stop_hyp = CategoricalParameter([True, False], default=trailing_stop, space='trailing', optimize=False, load=False)
    # trailing_stop_positive_hyp = RealParameter(0.01, 0.35, default=trailing_stop_positive, space='trailing', optimize=False, load=False)
    # trailing_stop_positive_offset_hyp = RealParameter(0.01, 0.1, default=trailing_stop_positive_offset, space='trailing', optimize=False, load=False)
    # trailing_only_offset_is_reached_hyp = CategoricalParameter([True, False], default=trailing_only_offset_is_reached, space='trailing', optimize=False, load=False)
    # buy_rsi = IntParameter(low=1, high=100, default=30, space='buy', optimize=False, load=False)
    # sell_rsi = IntParameter(low=1, high=100, default=70, space='sell', optimize=False, load=False)

    # FreqAI hyperoptable model training parameters
    # n_estimators = IntParameter(50, 500, default=100, space="freqai")
    max_trade_duration_candles = IntParameter(100, 500, default=300, space="freqai", optimize=True)

    # Define plot configuration
    plot_config = {
        "main_plot": {
            # Add any main plot customizations if needed later
        },
        "subplots": {
            "FreqAI": {
                "&-fut_ret": {"color": "purple"},
                "&-fut_ret_mean": {"color": "orange"},
                "&-fut_ret_std": {
                    "color": "cyan",
                    "plotly": {"opacity": 0.4},
                },  # Optional: make std dev lighter
            },
            "Features": {
                "%-rsi": {"color": "blue"},
                "%-ema": {"color": "green"},
                "%-vol_ratio": {"color": "grey"},
                "%-hour_sin": {"color": "red", "plotly": {"opacity": 0.6}},
                "%-hour_cos": {"color": "magenta", "plotly": {"opacity": 0.6}},
            },
        },
    }

    startup_candle_count: int = 50  # max period for indicators

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Populate standard indicators needed for feature engineering. Do NOT call self.freqai.start() here;
        FreqAI integration is handled by the framework. Only calculate indicators if required by feature engineering methods.
        """
        # Example: dataframe['%-rsi'] = ta.RSI(dataframe['close'], timeperiod=14)

        # --- Bollinger Bands and related features (corrected) ---
        for period in self.config.get("indicator_periods", {}).get("bb_periods", [20]):
            bb = ta.BBANDS(dataframe["close"], timeperiod=period)
            dataframe[f"%-bb_width{period}"] = (bb['upperband'] - bb['lowerband']) / bb['middleband']
            dataframe[f"%-close_bb_lower{period}"] = dataframe["close"] / bb['lowerband']

        # --- Relative Volume (ensure this was intended to be here) ---
        for period in self.config.get("indicator_periods", {}).get("vol_periods", [20]):
            dataframe[f"%-rel_vol{period}"] = (
                dataframe["volume"] / dataframe["volume"].rolling(period).mean()
            )

        return dataframe

    def feature_engineering_expand_basic(
        self, dataframe: DataFrame, metadata: dict, **kwargs
    ) -> DataFrame:
        # Plan B: EMA (8/21), RSI, ADX, Volume, regime/context features
        dataframe["%-ema8"] = ta.EMA(dataframe["close"], timeperiod=8)
        dataframe["%-ema21"] = ta.EMA(dataframe["close"], timeperiod=21)
        dataframe["%-rsi"] = ta.RSI(dataframe["close"], timeperiod=14)
        dataframe["%-adx"] = ta.ADX(dataframe)
        dataframe["%-volume"] = dataframe["volume"]
        # Regime/context: bull if ema8 > ema21, else bear
        dataframe["%-regime"] = (dataframe["%-ema8"] > dataframe["%-ema21"]).astype(int)
        logging.info(
            "[KrakenFreqAI] Regime distribution after calculation: %s",
            dataframe["%-regime"].value_counts().to_dict(),
        )
        # Z-score normalization for all engineered features
        feature_cols = [
            "%-ema8",
            "%-ema21",
            "%-rsi",
            "%-adx",
            "%-volume",
            "%-regime",
        ]
        for col in feature_cols:
            if col in dataframe:
                mean = dataframe[col].mean()
                std = dataframe[col].std()
                if std > 0:
                    dataframe[col] = (dataframe[col] - mean) / std
        # Add volatility (rolling std of returns)
        dataframe["%-volatility"] = dataframe["close"].pct_change().rolling(20).std()
        # Add volume spike (z-score of volume)
        vol_mean = dataframe["volume"].rolling(20).mean()
        vol_std = dataframe["volume"].rolling(20).std()
        dataframe["%-vol_spike"] = (dataframe["volume"] - vol_mean) / vol_std
        # Multi-timeframe features (example: 15m EMA8, RSI, ADX)
        if "15m" in dataframe.columns:
            dataframe["%-ema8_15m"] = ta.EMA(dataframe["close_15m"], timeperiod=8)
            dataframe["%-rsi_15m"] = ta.RSI(dataframe["close_15m"], timeperiod=14)
            dataframe["%-adx_15m"] = ta.ADX(
                {
                    "high": dataframe["high_15m"],
                    "low": dataframe["low_15m"],
                    "close": dataframe["close_15m"],
                }
            )
        if "1h" in dataframe.columns:
            dataframe["%-ema8_1h"] = ta.EMA(dataframe["close_1h"], timeperiod=8)
            dataframe["%-rsi_1h"] = ta.RSI(dataframe["close_1h"], timeperiod=14)
            dataframe["%-adx_1h"] = ta.ADX(
                {
                    "high": dataframe["high_1h"],
                    "low": dataframe["low_1h"],
                    "close": dataframe["close_1h"],
                }
            )
        # Update feature_cols for normalization
        feature_cols += [
            "%-volatility",
            "%-vol_spike",
            "%-ema8_15m",
            "%-rsi_15m",
            "%-adx_15m",
            "%-ema8_1h",
            "%-rsi_1h",
            "%-adx_1h",
        ]
        for col in feature_cols:
            if col in dataframe:
                mean = dataframe[col].mean()
                std = dataframe[col].std()
                if std > 0:
                    dataframe[col] = (dataframe[col] - mean) / std
        return dataframe

    def feature_engineering_expand_all(
        self, dataframe: DataFrame, period, metadata, **kwargs
    ) -> DataFrame:
        # Expanded: EMA, SMA, RSI, MFI, ADX, ROC, Bollinger Bands, volume, relative volume
        dataframe[f"%-ema{period}"] = ta.EMA(dataframe["close"], timeperiod=period)
        dataframe[f"%-sma{period}"] = ta.SMA(dataframe["close"], timeperiod=period)
        dataframe[f"%-rsi{period}"] = ta.RSI(dataframe["close"], timeperiod=period)
        dataframe[f"%-mfi{period}"] = ta.MFI(dataframe, timeperiod=period)
        dataframe[f"%-adx{period}"] = ta.ADX(dataframe, timeperiod=period)
        dataframe[f"%-roc{period}"] = ta.ROC(dataframe, timeperiod=period)
        # Bollinger Bands
        bb = ta.BBANDS(dataframe["close"], timeperiod=period)
        dataframe[f"%-bb_width{period}"] = (bb['upperband'] - bb['lowerband']) / bb['middleband']
        dataframe[f"%-close_bb_lower{period}"] = dataframe["close"] / bb['lowerband']
        # Relative volume
        dataframe[f"%-rel_vol{period}"] = (
            dataframe["volume"] / dataframe["volume"].rolling(period).mean()
        )
        return dataframe

    def feature_engineering_standard(
        self, dataframe: DataFrame, metadata: dict, **kwargs
    ) -> DataFrame:
        # Add day-of-week and hour-of-day context features
        dataframe["%-day_of_week"] = (dataframe["date"].dt.dayofweek + 1) / 7
        dataframe["%-hour_of_day"] = (dataframe["date"].dt.hour + 1) / 24

        # --- Load and Merge Sentiment Score --- #
        # CONCEPTUAL: Load pre-calculated sentiment data
        # In a real implementation, replace this with actual loading logic
        # (e.g., reading from a CSV/JSON updated periodically)
        sentiment_file = "user_data/sentiment_latest.csv" # Path updated to use the output of update_sentiment.py
        try:
            # Assuming CSV has 'timestamp' (ISO format or Unix) and 'sentiment_score' columns
            # --- Modified Logic: Read latest scores per pair --- #
            sentiment_df = pd.read_csv(sentiment_file)
            # Filter for the current pair
            pair_sentiment = sentiment_df[sentiment_df['pair'] == metadata['pair']]
            if not pair_sentiment.empty:
                # Get the single latest score for this pair
                latest_score = pair_sentiment['sentiment_score'].iloc[-1] # Get the last row's score
                # Assign this score to the entire dataframe column
                # This assumes the score remains constant until the next update
                dataframe['%-sentiment_score'] = latest_score
                logging.info(f"Applied latest sentiment score ({latest_score:.4f}) for {metadata['pair']}.")
            else:
                logging.warning(f"No sentiment data found for pair {metadata['pair']} in {sentiment_file}. Using neutral 0.0.")
                dataframe['%-sentiment_score'] = 0.0

            # --- Original merge_asof logic removed/commented as we now apply a single latest score ---
            # sentiment_df['timestamp'] = pd.to_datetime(sentiment_df['timestamp'], utc=True)
            # sentiment_df = sentiment_df.set_index('timestamp')
            # Merge sentiment score into the main dataframe
            # Ensure dataframe index is datetime first
            # if not pd.api.types.is_datetime64_any_dtype(dataframe.index):
            #      if 'date' in dataframe.columns:
            #         dataframe = dataframe.set_index('date', drop=False) # Keep 'date' column if needed
            #      else:
            #         raise ValueError("Dataframe index is not datetime and 'date' column missing.")
            # Use merge_asof for robust time-based joining (finds nearest sentiment before candle time)
            # dataframe = pd.merge_asof(
            #     dataframe.sort_index(),
            #     sentiment_df[['sentiment_score']].sort_index(),
            #     left_index=True,
            #     right_index=True,
            #     direction='backward', # Use last known sentiment before candle starts
            #     tolerance=pd.Timedelta('1h') # Optional: only use sentiment if within 1 hour
            # )
            # Rename and add prefix
            # dataframe.rename(columns={'sentiment_score': '%-sentiment_score'}, inplace=True)
            # Fill missing sentiment values (e.g., at the start or if tolerance exceeded)
            # dataframe['%-sentiment_score'] = dataframe['%-sentiment_score'].fillna(0.0) # Fill with neutral 0.0
            # logging.info(f"Successfully loaded and merged sentiment data for {metadata['pair']}.")

        except FileNotFoundError:
            logging.warning(f"Sentiment data file not found: {sentiment_file}. Adding neutral sentiment feature.")
            dataframe['%-sentiment_score'] = 0.0
        except Exception as e:
            logging.error(f"Error loading/merging sentiment data: {e}", exc_info=True)
            dataframe['%-sentiment_score'] = 0.0 # Add neutral feature on error

        # Optional: Normalize sentiment score here if needed, similar to other features.
        # mean = dataframe['%-sentiment_score'].mean()
        # std = dataframe['%-sentiment_score'].std()
        # if std > 0:
        #     dataframe['%-sentiment_score'] = (dataframe['%-sentiment_score'] - mean) / std

        # Add raw OHLCV for RL
        dataframe["%-raw_close"] = dataframe["close"]
        dataframe["%-raw_open"] = dataframe["open"]
        dataframe["%-raw_high"] = dataframe["high"]
        dataframe["%-raw_low"] = dataframe["low"]
        dataframe["%-raw_volume"] = dataframe["volume"]
        return dataframe

    def check_feature_consistency(self, dataframe: DataFrame, required_cols: list) -> None:
        missing = [col for col in required_cols if col not in dataframe.columns]
        if missing:
            raise ValueError(f"Missing required feature columns: {missing}")

    def set_freqai_targets(self, dataframe: DataFrame, metadata: dict, **kwargs) -> DataFrame:
        # For debugging, set &-s_close to random values between -0.05 and 0.05
        np.random.seed(42)
        dataframe["&-s_close"] = np.random.uniform(-0.05, 0.05, size=len(dataframe))
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # --- Fetch current balance (Example of Portfolio Awareness) ---
        current_balance = self._get_stake_balance()
        # TODO: Use current_balance for dynamic position sizing later
        # For now, just logging it
        logging.info(f"[{metadata['pair']}] Current stake currency balance: {current_balance}")
        # --- End Balance Fetch ---

        dataframe["do_predict"] = 1  # Force prediction for all rows
        if "&-s_close" not in dataframe:
            np.random.seed(42)
            dataframe["&-s_close"] = np.random.uniform(-0.05, 0.05, size=len(dataframe))
        for col in ["enter_long", "enter_short", "enter_tag"]:
            if col not in dataframe:
                dataframe[col] = None
        # Ensure '%-regime' exists; if missing, recalculate or fallback
        if "%-regime" not in dataframe:
            # Try to recalculate EMAs if missing
            if "%-ema8" not in dataframe:
                try:
                    dataframe["%-ema8"] = ta.EMA(dataframe["close"], timeperiod=8)
                except Exception as e:
                    logging.warning(f"[KrakenFreqAI] Could not recalculate '%-ema8': {e}")
            if "%-ema21" not in dataframe:
                try:
                    dataframe["%-ema21"] = ta.EMA(dataframe["close"], timeperiod=21)
                except Exception as e:
                    logging.warning(f"[KrakenFreqAI] Could not recalculate '%-ema21': {e}")
            # Now try to recalculate regime
            if "%-ema8" in dataframe and "%-ema21" in dataframe:
                dataframe["%-regime"] = (dataframe["%-ema8"] > dataframe["%-ema21"]).astype(int)
                logging.warning("[KrakenFreqAI] Recalculated '%-regime' in entry logic.")
            else:
                dataframe["%-regime"] = 1  # Fallback: assume bull regime
                logging.warning(
                    "[KrakenFreqAI] Fallback: set all '%-regime' to 1 (bull) in entry logic."
                )
        else:
            # Even if present, ensure regime is up to date
            if "%-ema8" in dataframe and "%-ema21" in dataframe:
                dataframe["%-regime"] = (dataframe["%-ema8"] > dataframe["%-ema21"]).astype(int)
                logging.info("[KrakenFreqAI] Updated '%-regime' in entry logic.")
        logging.info(
            "[KrakenFreqAI] Regime distribution before entry: %s",
            dataframe["%-regime"].value_counts().to_dict(),
        )
        # Regime/context gating: only allow long in bull regime, short in bear regime
        bull_regime = dataframe["%-regime"] == 1
        bear_regime = dataframe["%-regime"] == 0
        enter_long_cond = (
            (dataframe["do_predict"] == 1) & (dataframe["&-s_close"] > 0.01) & bull_regime
        )
        dataframe.loc[enter_long_cond, ["enter_long", "enter_tag"]] = (1, "long")
        enter_short_cond = (
            (dataframe["do_predict"] == 1) & (dataframe["&-s_close"] < -0.01) & bear_regime
        )
        dataframe.loc[enter_short_cond, ["enter_short", "enter_tag"]] = (1, "short")
        logging.info(
            "[KrakenFreqAI] entry signals: enter_long=%d, enter_short=%d",
            (dataframe["enter_long"] == 1).sum(),
            (dataframe["enter_short"] == 1).sum(),
        )
        # Log feature and action distributions for diagnostics
        logging.info("[KrakenFreqAI] &-s_close unique values: %s", dataframe["&-s_close"].unique())
        logging.info(
            "[KrakenFreqAI] regime distribution: %s", dataframe["%-regime"].value_counts().to_dict()
        )
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["do_predict"] = 1  # Force prediction for all rows
        if "&-s_close" not in dataframe:
            np.random.seed(42)
            dataframe["&-s_close"] = np.random.uniform(-0.05, 0.05, size=len(dataframe))
        for col in ["exit_long", "exit_short"]:
            if col not in dataframe:
                dataframe[col] = None
        # Exit logic: exit long if &-s_close < 0, exit short if &-s_close > 0
        exit_long_cond = (dataframe["do_predict"] == 1) & (dataframe["&-s_close"] < 0)
        dataframe.loc[exit_long_cond, "exit_long"] = 1
        exit_short_cond = (dataframe["do_predict"] == 1) & (dataframe["&-s_close"] > 0)
        dataframe.loc[exit_short_cond, "exit_short"] = 1
        logging.info(
            "[KrakenFreqAI] exit signals: exit_long=%d, exit_short=%d",
            (dataframe["exit_long"] == 1).sum(),
            (dataframe["exit_short"] == 1).sum(),
        )
        return dataframe

    # ++ Custom Methods ++
    def _get_stake_balance(self) -> float:
        """Helper to get the current available balance for the stake currency."""
        try:
            if self.wallets:
                balance = self.wallets.get_free(self.config['stake_currency'])
                if balance is not None:
                    logging.debug(f"Available balance for {self.config['stake_currency']}: {balance}")
                    return balance
                else:
                    logging.warning(f"Could not retrieve balance for {self.config['stake_currency']} from wallets.")
            else:
                logging.warning("Wallets object not available to fetch balance.")
        except Exception as e:
            logging.error(f"Error fetching wallet balance: {e}", exc_info=True)
        return 0.0 # Return 0 or appropriate default if balance fetch fails
