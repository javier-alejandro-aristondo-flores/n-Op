"""the function-space layer norm, each token standardized over its own channels and grid alone"""

from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.framework import Array
from operators.kernels.codomain_attention.tokens import Token_Count
from operators.substrate import Mean_Over_Last_Axis

# keeps a token's own spread from dividing by zero on a constant field
LAYER_NORM_EPSILON = 1e-5


class FunctionSpaceLayerNorm:
    """each token's function standardized over its hidden channels and grid, then one shared per-channel affine"""


    def __init__(self, hidden_channels: int) -> None:
        self.hidden_channels = hidden_channels
        # the affine starts at the identity: zero bias and a scale of one, stored zero-centered like the spectral gain
        self.parameter_values: dict[str, NDArray[np.float64]] = {
            "scale": np.zeros(hidden_channels),
            "bias": np.zeros(hidden_channels),
        }


    def Forward(self, lifted: dict[str, Any], input_values: Any) -> Any:
        token_count = Token_Count(input_values.shape[0], self.hidden_channels)
        grid_shape = input_values.shape[1:]
        unflattened = input_values.reshape(token_count, self.hidden_channels, *grid_shape)
        flattened_per_token = unflattened.reshape(token_count, -1)
        mean = Mean_Over_Last_Axis(flattened_per_token)
        centered = flattened_per_token - mean[..., None]
        variance = Mean_Over_Last_Axis(centered * centered)
        standardized = centered / (variance[..., None] + LAYER_NORM_EPSILON) ** 0.5
        reshaped = standardized.reshape(token_count, self.hidden_channels, *grid_shape)
        channel_shape = (1, self.hidden_channels) + (1,) * len(grid_shape)
        scale = 1.0 + lifted["scale"].reshape(channel_shape)
        bias = lifted["bias"].reshape(channel_shape)
        return (reshaped * scale + bias).reshape(token_count * self.hidden_channels, *grid_shape)


    def Inspect(self) -> dict[str, Array]:
        return dict(self.parameter_values)
