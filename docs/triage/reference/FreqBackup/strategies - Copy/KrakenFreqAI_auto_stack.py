import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from functools import reduce

# --- Add Pydantic imports ---
from pydantic import BaseModel, Field, PositiveInt, PositiveFloat

import numpy as np
import talib.abstract as ta
from pandas import DataFrame
import pandas as pd

from freqtrade.strategy import CategoricalParameter, IntParameter, IStrategy, RealParameter
from freqtrade.freqai.prediction_models.ReinforcementLearner import ReinforcementLearner

logger = logging.getLogger(__name__)

# --- Pydantic Models for Configuration ---
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
    model_training_parameters: Dict[str, Any] = {}

class KrakenFreqAI_auto_stack(IStrategy):
    """
    Auto-Stack Integrated FreqAI strategy for Kraken/BTC markets.
    Features:
    - Multi-timeframe analysis (5m, 15m, 1h)
    - Advanced feature engineering
    - Risk management with dynamic position sizing
    - Integration with auto-stack logging
    - Sentiment analysis integration
    """

    # --- Strategy Configuration ---
    timeframe = "5m"
    can_short = False
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # --- Risk Management Parameters ---
    minimal_roi = {
        "0": 0.169,
        "40": 0.051,
        "66": 0.038,
        "171": 0
    }
    stoploss = -0.047
    trailing_stop = True
    trailing_stop_positive = 0.267
    trailing_stop_positive_offset = 0.315
    trailing_only_offset_is_reached = True

    # --- FreqAI Parameters ---
    max_trade_duration_candles = IntParameter(100, 500, default=300, space="freqai", optimize=True)

    # --- Plot Configuration ---
    plot_config = {
        "main_plot": {
            "%-ema8": {"color": "blue"},
            "%-ema21": {"color": "red"},
            "%-bb_width20": {"color": "green"},
        },
        "subplots": {
            "FreqAI": {
                "&-fut_ret": {"color": "purple"},
                "&-fut_ret_mean": {"color": "orange"},
                "&-fut_ret_std": {"color": "cyan", "plotly": {"opacity": 0.4}},
            },
            "Features": {
                "%-rsi": {"color": "blue"},
                "%-adx": {"color": "green"},
                "%-vol_ratio": {"color": "grey"},
                "%-sentiment_score": {"color": "magenta"},
            },
        },
    }

    startup_candle_count: int = 50

    def log_to_agent_logs(self, action: str, event_type: str, message: str, metadata: Dict = None):
        """Log strategy events to agent_logs table"""
        try:
            # This will be handled by the auto-stack logging system
            logger.info(f"Strategy Event: {action} - {event_type} - {message}")
            if metadata:
                logger.debug(f"Metadata: {metadata}")
        except Exception as e:
            logger.error(f"Failed to log to agent_logs: {str(e)}")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Populate standard indicators needed for feature engineering.
        """
        # --- Bollinger Bands ---
        for period in [20, 50]:
            bb = ta.BBANDS(dataframe["close"], timeperiod=period)
            dataframe[f"%-bb_width{period}"] = (bb['upperband'] - bb['lowerband']) / bb['middleband']
            dataframe[f"%-close_bb_lower{period}"] = dataframe["close"] / bb['lowerband']

        # --- Volume Analysis ---
        for period in [20, 50]:
            dataframe[f"%-rel_vol{period}"] = (
                dataframe["volume"] / dataframe["volume"].rolling(period).mean()
            )

        return dataframe

    def feature_engineering_expand_basic(self, dataframe: DataFrame, metadata: dict, **kwargs) -> DataFrame:
        """
        Basic feature engineering with proven indicators.
        """
        # --- Core Technical Indicators ---
        dataframe["%-ema8"] = ta.EMA(dataframe["close"], timeperiod=8)
        dataframe["%-ema21"] = ta.EMA(dataframe["close"], timeperiod=21)
        dataframe["%-rsi"] = ta.RSI(dataframe["close"], timeperiod=14)
        dataframe["%-adx"] = ta.ADX(dataframe)
        
        # --- Volume Features ---
        dataframe["%-volume"] = dataframe["volume"]
        dataframe["%-vol_ratio"] = dataframe["volume"] / dataframe["volume"].rolling(20).mean()
        
        # --- Market Regime ---
        dataframe["%-regime"] = (dataframe["%-ema8"] > dataframe["%-ema21"]).astype(int)
        
        # --- Volatility ---
        dataframe["%-volatility"] = dataframe["close"].pct_change().rolling(20).std()
        
        # --- Volume Spikes ---
        vol_mean = dataframe["volume"].rolling(20).mean()
        vol_std = dataframe["volume"].rolling(20).std()
        dataframe["%-vol_spike"] = (dataframe["volume"] - vol_mean) / vol_std

        # --- Multi-timeframe Features ---
        for tf in ["15m", "1h"]:
            if f"close_{tf}" in dataframe.columns:
                dataframe[f"%-ema8_{tf}"] = ta.EMA(dataframe[f"close_{tf}"], timeperiod=8)
                dataframe[f"%-rsi_{tf}"] = ta.RSI(dataframe[f"close_{tf}"], timeperiod=14)
                dataframe[f"%-adx_{tf}"] = ta.ADX({
                    "high": dataframe[f"high_{tf}"],
                    "low": dataframe[f"low_{tf}"],
                    "close": dataframe[f"close_{tf}"]
                })

        # --- Normalize Features ---
        feature_cols = [col for col in dataframe.columns if col.startswith("%-")]
        for col in feature_cols:
            if col in dataframe:
                mean = dataframe[col].mean()
                std = dataframe[col].std()
                if std > 0:
                    dataframe[col] = (dataframe[col] - mean) / std

        return dataframe

    def feature_engineering_standard(self, dataframe: DataFrame, metadata: dict, **kwargs) -> DataFrame:
        """
        Add time-based and sentiment features.
        """
        # --- Time Features ---
        dataframe["%-day_of_week"] = (dataframe["date"].dt.dayofweek + 1) / 7
        dataframe["%-hour_of_day"] = (dataframe["date"].dt.hour + 1) / 24

        # --- Sentiment Integration ---
        sentiment_file = "user_data/sentiment_latest.csv"
        try:
            sentiment_df = pd.read_csv(sentiment_file)
            pair_sentiment = sentiment_df[sentiment_df['pair'] == metadata['pair']]
            if not pair_sentiment.empty:
                latest_score = pair_sentiment['sentiment_score'].iloc[-1]
                dataframe['%-sentiment_score'] = latest_score
                self.log_to_agent_logs(
                    "sentiment_update",
                    "feature_engineering",
                    f"Updated sentiment score for {metadata['pair']}",
                    {"score": latest_score}
                )
            else:
                dataframe['%-sentiment_score'] = 0.0
        except Exception as e:
            logger.warning(f"Failed to load sentiment data: {str(e)}")
            dataframe['%-sentiment_score'] = 0.0

        return dataframe

    def set_freqai_targets(self, dataframe: DataFrame, metadata: dict, **kwargs) -> DataFrame:
        """
        Set the target variables for the FreqAI model.
        """
        # --- Future Returns ---
        dataframe["&-fut_ret"] = dataframe["close"].shift(-1) / dataframe["close"] - 1
        
        # --- Rolling Statistics ---
        dataframe["&-fut_ret_mean"] = dataframe["&-fut_ret"].rolling(20).mean()
        dataframe["&-fut_ret_std"] = dataframe["&-fut_ret"].rolling(20).std()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Entry signal generation with risk management.
        """
        # --- Portfolio Awareness ---
        current_balance = self._get_stake_balance()
        max_trades = self.config.get('max_open_trades', 5)
        current_trades = len(self.dp.get_open_trades())
        
        # --- Entry Conditions ---
        conditions = []
        
        # 1. FreqAI Prediction
        conditions.append(dataframe["&-fut_ret"] > 0.01)  # 1% expected return
        
        # 2. Technical Conditions
        conditions.append(dataframe["%-rsi"] < 30)  # Oversold
        conditions.append(dataframe["%-ema8"] > dataframe["%-ema21"])  # Uptrend
        
        # 3. Volume Conditions
        conditions.append(dataframe["%-vol_ratio"] > 1.2)  # Above average volume
        
        # 4. Risk Management
        conditions.append(current_trades < max_trades)  # Max trades check
        
        # --- Combine Conditions ---
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'enter_long'] = 1

        # --- Log Entry Signals ---
        if len(dataframe[dataframe['enter_long'] == 1]) > 0:
            self.log_to_agent_logs(
                "entry_signal",
                "strategy",
                f"Entry signal generated for {metadata['pair']}",
                {
                    "current_balance": current_balance,
                    "current_trades": current_trades,
                    "max_trades": max_trades
                }
            )

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Exit signal generation with trailing stops.
        """
        # --- Exit Conditions ---
        conditions = []
        
        # 1. FreqAI Prediction
        conditions.append(dataframe["&-fut_ret"] < -0.005)  # -0.5% expected return
        
        # 2. Technical Conditions
        conditions.append(dataframe["%-rsi"] > 70)  # Overbought
        conditions.append(dataframe["%-ema8"] < dataframe["%-ema21"])  # Downtrend
        
        # --- Combine Conditions ---
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'exit_long'] = 1

        # --- Log Exit Signals ---
        if len(dataframe[dataframe['exit_long'] == 1]) > 0:
            self.log_to_agent_logs(
                "exit_signal",
                "strategy",
                f"Exit signal generated for {metadata['pair']}",
                {"pair": metadata['pair']}
            )

        return dataframe

    def _get_stake_balance(self) -> float:
        """
        Get current stake balance for position sizing.
        """
        try:
            return self.wallets.get_free(self.config['stake_currency'])
        except Exception as e:
            logger.error(f"Failed to get stake balance: {str(e)}")
            return 0.0

    def custom_entry_price(self, pair: str, current_time: datetime, proposed_rate: float,
                         entry_tag: Optional[str], **kwargs) -> float:
        """
        Custom entry price calculation with slippage consideration.
        """
        try:
            # Get order book
            order_book = self.dp.get_order_book(pair, 1)
            if order_book and len(order_book['asks']) > 0:
                # Use the best ask price plus a small buffer
                return order_book['asks'][0][0] * 1.001
        except Exception as e:
            logger.error(f"Failed to get custom entry price: {str(e)}")
        
        return proposed_rate

    def custom_exit_price(self, pair: str, trade: 'Trade', current_time: datetime,
                        proposed_rate: float, current_profit: float, **kwargs) -> float:
        """
        Custom exit price calculation with slippage consideration.
        """
        try:
            # Get order book
            order_book = self.dp.get_order_book(pair, 1)
            if order_book and len(order_book['bids']) > 0:
                # Use the best bid price minus a small buffer
                return order_book['bids'][0][0] * 0.999
        except Exception as e:
            logger.error(f"Failed to get custom exit price: {str(e)}")
        
        return proposed_rate 