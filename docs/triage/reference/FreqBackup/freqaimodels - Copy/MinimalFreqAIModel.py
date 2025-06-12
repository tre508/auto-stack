from freqtrade.freqai.base_models.BaseFreqaiModel import BaseFreqaiModel
from pandas import DataFrame
import numpy as np
from typing import Any, Dict

class MinimalFreqAIModel(BaseFreqaiModel):
    \"\"\"Minimal FreqAI model for testing hyperopt.\"\"\"

    def train(
        self,
        unfiltered_dataframe: DataFrame,
        stake_currency: str,
        hyperopt_params: Dict[str, Any],
        *args,
        **kwargs,
    ) -> Any:
        \"\"\"Minimal training: returns a dummy model artifact.\"\"\"
        # Use the hyperoptable parameter to show it's being passed
        freqai_param_value = hyperopt_params.get('freqai_hyperopt_param', 'default_value')
        print(f"MinimalFreqAIModel: Training with freqai_hyperopt_param = {freqai_param_value}")

        # Return a simple dictionary as a dummy model artifact
        return {"dummy_model": True, "param_received": freqai_param_value}

    def predict(
        self,
        unfiltered_dataframe: DataFrame,
        model: Any,
        *args,
        **kwargs,
    ) -> tuple[DataFrame, np.ndarray]:
        \"\"\"Minimal prediction: returns a constant prediction.\"\"\"
        # Create a prediction array (e.g., all zeros)
        num_predictions = len(unfiltered_dataframe)
        predictions = np.zeros(num_predictions)
        return unfiltered_dataframe, predictions 