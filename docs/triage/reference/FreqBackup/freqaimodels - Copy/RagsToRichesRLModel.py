# --- Do not remove these imports ---
import logging
from typing import List, Dict, Any, Optional

# --- Add Pydantic imports ---
from pydantic import BaseModel, Field, PositiveInt, PositiveFloat, ValidationError

import numpy as np
import pandas as pd
from stable_baselines3.common.vec_env import DummyVecEnv

from freqtrade.freqai.prediction_models.ReinforcementLearner import ReinforcementLearner
from freqtrade.freqai.RL.Base5ActionRLEnv import Actions, Base5ActionRLEnv, Positions


logger = logging.getLogger(__name__)


# --- Pydantic Models for RL Configuration Validation ---
# Placed inside the model file for better encapsulation

class PolicyKwargs(BaseModel):
    net_arch: Optional[List[int]] = None
    activation_fn: Optional[str] = None
    dropout: Optional[PositiveFloat] = Field(None, ge=0.0, le=1.0)
    use_batch_norm: Optional[bool] = None
    # Add other potential policy kwargs based on actual usage

class RewardParams(BaseModel):
    rr: Optional[PositiveInt] = None
    profit_aim: Optional[PositiveFloat] = None
    # Add other custom reward params if defined/used

class RLConfigModel(BaseModel):
    train_cycles: Optional[PositiveInt] = None # Made optional as it might not always be present?
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
    model_training_parameters: Optional[Dict[str, Any]] = {} # Keep flexible

# --- End Pydantic Models ---


class RagsToRichesRLModel(ReinforcementLearner):
    """
    Custom RL model for FreqAI. Implements a reward function focused on profit and drawdown control.
    """

    class MyRLEnv(Base5ActionRLEnv):
        """
        Custom RL environment for RagsToRichesRLModel. Reward = realized profit - drawdown penalty.
        """

        def _get_regime(self):
            return self._current_obs.get("%-regime", 0) if hasattr(self, "_current_obs") else 0

        def _get_drawdown(self):
            return min(self._total_profit, self._total_unrealized_profit)

        def _get_trade_duration(self):
            return self._current_tick - (self._last_trade_tick or self._current_tick)

        def _penalize_drawdown(self, drawdown):
            if drawdown < -0.03:
                return -15.0 * abs(drawdown)
            return None

        def _penalize_unprofitable_hold(self, action, pnl, trade_duration, max_trade_duration):
            if (
                self._position in (Positions.Short, Positions.Long)
                and action == Actions.Neutral.value
                and pnl < 0
            ):
                return -3.0 * trade_duration / max_trade_duration
            return None

        def _reward_profitable_hold(self, pnl, trade_duration, max_trade_duration):
            if self._position in (Positions.Long, Positions.Short) and pnl > 0:
                return 2.0 * np.log1p(abs(pnl)) * (1 + 0.5 * trade_duration / max_trade_duration)
            return None

        def _reward_log_growth(self, realized):
            if realized > 1:
                log_growth = np.log(realized)
                return 7.0 * log_growth
            return None

        def _penalize_volatility(self, pnl):
            if self._position in (Positions.Long, Positions.Short):
                volatility = np.std([self._total_profit, self._total_unrealized_profit])
                return float(pnl * 0.3 - volatility * 0.7)
            return None

        def _reward_entry(self, action, regime):
            if action == Actions.Long_enter.value and self._position == Positions.Neutral:
                return 20.0 if regime == 1 else 5.0
            if action == Actions.Short_enter.value and self._position == Positions.Neutral:
                return 20.0 if regime == 0 else 5.0
            return None

        def _penalize_inaction(self, action):
            if action == Actions.Neutral.value and self._position == Positions.Neutral:
                return -2.0
            return None

        def _reward_exit(self, action, realized, drawdown):
            factor = 100.0
            if action == Actions.Long_exit.value and self._position == Positions.Long:
                reward = realized - drawdown
                return float(reward * factor)
            if action == Actions.Short_exit.value and self._position == Positions.Short:
                reward = realized - drawdown
                return float(reward * factor)
            return None

        def _penalize_consecutive_losses(self):
            if hasattr(self, "_consecutive_losses") and self._consecutive_losses > 2:
                return -5.0 * self._consecutive_losses
            return None

        def calculate_reward(self, action: int) -> float:
            if not self._is_valid(action):
                self.tensorboard_log("invalid", category="actions")
                return -2.0  # Mild penalty for invalid action
            pnl = self.get_unrealized_profit()
            drawdown = self._get_drawdown()
            regime = self._get_regime()
            max_trade_duration = self.rl_config.get("max_trade_duration_candles", 300)
            trade_duration = self._get_trade_duration()
            # Risk-adjusted return proxy (Sharpe-like)
            risk_adj = pnl / (np.std([self._total_profit, self._total_unrealized_profit]) + 1e-6)
            # Reward/penalty logic
            reward = 0.0
            # Reward profitable trades, scaled by risk-adjusted return
            if (action in (Actions.Long_exit.value, Actions.Short_exit.value)) and pnl > 0:
                reward += 10.0 * risk_adj
            # Penalize holding losing trades (scaled by duration)
            if self._position in (Positions.Long, Positions.Short) and pnl < 0:
                reward -= 2.0 * abs(pnl) * (1 + trade_duration / max_trade_duration)
            # Small penalty for inactivity (neutral action in neutral position)
            if action == Actions.Neutral.value and self._position == Positions.Neutral:
                reward -= 0.2
            # Penalize excessive trading (frequent entries/exits)
            if hasattr(self, "_consecutive_trades") and self._consecutive_trades > 3:
                reward -= 0.5 * self._consecutive_trades
            # Regime/context: only reward long entries in bull, shorts in bear
            if action == Actions.Long_enter.value and regime == 1:
                reward += 1.0
            if action == Actions.Short_enter.value and regime == 0:
                reward += 1.0
            # Mild penalty for drawdown
            if drawdown < -0.03:
                reward -= 5.0 * abs(drawdown)
            return reward

        def step(self, action):
            result = super().step(action)
            logger.info(
                f"RL Step: action={action}, position={self._position}, reward={self._last_reward}, profit={self._total_profit}"
            )
            return result

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # --- Validate rl_config using Pydantic ---
        try:
            # Assuming self.rl_config is populated by the parent class from config
            if not self.rl_config:
                raise ValueError("RL configuration (self.rl_config) is missing.")
            self.validated_rl_config = RLConfigModel(**self.rl_config)
            logger.info("Successfully validated RL configuration using Pydantic.")
        except ValidationError as e:
            logger.error(f"ERROR: Invalid RL configuration provided! Details:\n{e}")
            # Decide how to handle invalid config: raise error, use defaults, etc.
            # Raising an error is often safest during initialization.
            raise ValueError(f"Invalid RL configuration: {e}") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred during RL config validation: {e}")
            raise

        # Assign the custom environment
        self.ft_env = self.MyRLEnv
        # Now you can potentially use self.validated_rl_config.seed etc.
        # Or continue using self.rl_config dictionary if preferred,
        # knowing it has passed validation.

    def train(
        self,
        unfiltered_dataframe: pd.DataFrame,
        train_data: np.ndarray,
        train_labels: np.ndarray,
        metadata: dict,
        **kwargs,
    ) -> Any:
        """
        Train the RL model.
        """
        # Use validated config where needed, e.g.:
        # seed = self.validated_rl_config.seed if self.validated_rl_config.seed is not None else 42
        # policy_kwargs_dict = self.validated_rl_config.policy_kwargs.model_dump() if self.validated_rl_config.policy_kwargs else {}
        # Or continue using self.rl_config dictionary after validation in __init__
        seed = self.rl_config.get("seed", 42)
        policy_kwargs = self.rl_config.get("policy_kwargs", {})
        env = DummyVecEnv(
            [
                lambda: self.ft_env(
                    df=unfiltered_dataframe,
                    training_data=train_data,
                    trade_data=train_labels,
                    metadata=metadata,
                    window_size=self.window_size,
                    max_trade_duration_candles=self.max_trade_duration_candles,
                    exchange_info=self.exchange_info,
                    rl_config=self.rl_config,
                    current_model_path=self.current_model_path,
                    logger=logger,
                    feature_pipeline=self.feature_pipeline,
                    data_drawer=self.data_drawer,
                    seed=seed,
                )
            ]
        )
        model_class = self._find_model_class(self.rl_config.get("model_type", "PPO"))
        if self.live:
            model = model_class.load(self.current_model_path, env=env)
            logger.info(f"Reloaded model from {self.current_model_path}")
        else:
            model = model_class(
                self.rl_config.get("policy_type", "MlpPolicy"),
                env,
                verbose=1,
                tensorboard_log=self.tensorboard_logdir,
                policy_kwargs=policy_kwargs,
                **self.rl_config.get("model_training_parameters", {}),
                seed=seed,
            )
            logger.info(f"Initialized new {self.rl_config.get('model_type', 'PPO')} model.")
        total_timesteps = self.rl_config.get("total_timesteps", 100000)
        logger.info(f"Starting RL training for {total_timesteps} timesteps...")
        model.learn(
            total_timesteps=total_timesteps,
            callback=self.callbacks,
            tb_log_name=f"{self.identifier}",
        )
        logger.info("RL training finished.")
        model.save(self.current_model_path)
        logger.info(f"Saved trained model to {self.current_model_path}")
        return model

    def predict(
        self, unfiltered_dataframe: pd.DataFrame, data: np.ndarray, metadata: dict, **kwargs
    ) -> tuple[pd.DataFrame, np.ndarray]:
        if not hasattr(self, "rl_vec_env"):
            self.rl_vec_env = DummyVecEnv(
                [
                    lambda: self.ft_env(
                        df=unfiltered_dataframe,
                        training_data=data,
                        metadata=metadata,
                        window_size=self.window_size,
                        max_trade_duration_candles=self.max_trade_duration_candles,
                        exchange_info=self.exchange_info,
                        rl_config=self.rl_config,
                        logger=logger,
                        feature_pipeline=self.feature_pipeline,
                        data_drawer=self.data_drawer,
                        live_run=self.live,
                    )
                ]
            )
        if not hasattr(self, "rl_model"):
            model_class = self._find_model_class(self.rl_config.get("model_type", "PPO"))
            self.rl_model = model_class.load(self.current_model_path, env=self.rl_vec_env)
            logger.info(f"Loaded model for prediction from {self.current_model_path}")

        # Adjusted RL actions to &-s_close mapping for more distinct signals
        action_to_sclose = {
            0: 0.0,  # Neutral
            1: 0.05,  # Long
            2: -0.05,  # Exit long
            3: -0.05,  # Short
            4: 0.05,  # Exit short
        }

        actions = []
        for obs in data:
            act, _ = self.rl_model.predict(obs.reshape(1, -1), deterministic=True)
            actions.append(act[0])
        s_close_values = [action_to_sclose.get(a, 0.0) for a in actions]
        prediction_df = unfiltered_dataframe.copy()
        prediction_df["&-s_close"] = s_close_values
        action_array = np.array(actions)
        return prediction_df, action_array

    def _find_model_class(self, model_type_str: str) -> Any:
        try:
            if model_type_str == "PPO":
                from stable_baselines3 import PPO

                return PPO
            elif model_type_str == "A2C":
                from stable_baselines3 import A2C

                return A2C
            elif model_type_str == "DQN":
                from stable_baselines3 import DQN

                return DQN
            else:
                raise ValueError(f"Unsupported RL model type: {model_type_str}")
        except ImportError as e:
            logger.error(f"Please install stable-baselines3 to use RL models: {e}")
            raise
