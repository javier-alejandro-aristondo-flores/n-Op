"""the layer's local linear term, one weight and bias shared identically across every channel token"""

from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.framework import Array
from operators.kernels.codomain_attention.tokens import Token_Count
from operators.substrate import Einstein_Summation


class TokenSharedLocalLinear:
    """one hidden-by-hidden weight and bias applied identically to every token's channel block"""


    def __init__(self, hidden_channels: int, seed: int = 0) -> None:
        self.hidden_channels = hidden_channels
        generator = np.random.default_rng(seed)
        spread = np.sqrt(1.0 / hidden_channels)
        self.parameter_values: dict[str, NDArray[np.float64]] = {
            "weights": generator.normal(0.0, spread, size=(hidden_channels, hidden_channels)),
            "biases": np.zeros(hidden_channels),
        }


    def Forward(self, lifted: dict[str, Any], input_values: Any) -> Any:
        token_count = Token_Count(input_values.shape[0], self.hidden_channels)
        grid_shape = input_values.shape[1:]
        unflattened = input_values.reshape(token_count, self.hidden_channels, *grid_shape)
        mixed = Einstein_Summation("oc,tcxyz->toxyz", lifted["weights"], unflattened)
        bias_shape = (1, self.hidden_channels) + (1,) * len(grid_shape)
        biased = mixed + lifted["biases"].reshape(bias_shape)
        return biased.reshape(token_count * self.hidden_channels, *grid_shape)


    def Inspect(self) -> dict[str, Array]:
        return dict(self.parameter_values)
