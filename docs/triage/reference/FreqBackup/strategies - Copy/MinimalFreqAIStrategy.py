from freqtrade.strategy import IStrategy, IntParameter
from pandas import DataFrame

class MinimalFreqAIStrategy(IStrategy):
    timeframe = '5m'
    minimal_roi = {"0": 1.0} # Needs some ROI table
    stoploss = -0.99 # Needs some stoploss

    # --- Minimal FreqAI Hyperopt Parameter ---
    # This single parameter in the 'freqai' space is what we want Optuna to handle.
    freqai_hyperopt_param = IntParameter(1, 10, default=5, space='freqai', optimize=True)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # No indicators needed for this minimal test
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Simple entry: Always enter long (for testing purposes)
        # FreqAI predictions would normally be used here.
        dataframe.loc[:, ['enter_long', 'enter_tag']] = (1, 'minimal_entry')
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Simple exit: Always exit long (for testing purposes)
        # FreqAI predictions would normally be used here.
        dataframe.loc[:, 'exit_long'] = 1
        return dataframe 