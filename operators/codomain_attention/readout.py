"""the token-shared linear head that reduces every channel token to one scalar field, and the per-token heads after it"""

from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.codomain_attention.channels import ELF_GROUP, POTENTIAL_GROUP
from operators.framework import Array, Coefficients, Discretization, GridFunction
from operators.kernels.codomain_attention import Token_Count
from operators.substrate import Concatenate_Channels, Einstein_Summation, Softplus
from operators.wrappers import Channel_Means


class TokenSharedReadout:
    """one hidden-to-one linear map applied identically to every channel token, token count read off the shape"""


    def __init__(self, hidden_channels: int, seed: int = 0) -> None:
        self.hidden_channels = hidden_channels
        generator = np.random.default_rng(seed)
        scale = np.sqrt(2.0 / (hidden_channels + 1))
        self.parameter_values: dict[str, NDArray[np.float64]] = {
            "readout_weights": generator.normal(0.0, scale, size=(1, hidden_channels)),
            "readout_biases": np.zeros(1),
        }


    def Forward(self, lifted: dict[str, Any], input_values: Any) -> Any:
        token_count = Token_Count(input_values.shape[0], self.hidden_channels)
        grid_shape = input_values.shape[1:]
        unflattened = input_values.reshape(token_count, self.hidden_channels, *grid_shape)
        mixed = Einstein_Summation("oc,tcxyz->toxyz", lifted["readout_weights"], unflattened)
        bias_shape = (1, 1) + (1,) * len(grid_shape)
        biased = mixed + lifted["readout_biases"].reshape(bias_shape)
        return biased.reshape(token_count, *grid_shape)


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        # satisfies the operator protocol structurally; the member's own forward path calls Forward directly instead
        produced = np.asarray(self.Forward(self.parameter_values, np.asarray(input_function.values)))
        labels = tuple(f"token_{token_index}" for token_index in range(produced.shape[0]))
        return GridFunction(produced, labels, input_function.domain, input_function.quadrature)


    def Inspect(self) -> dict[str, Array]:
        return dict(self.parameter_values)


def Bounded_Unit_Interval(values: Any) -> Any:
    """values placed in the open interval zero to one, the same bounded form the pointwise projection head uses"""
    softened = Softplus(values)
    return 1.0 / (1.0 + softened * softened)


def Per_Token_Heads(reconstruction: Any, present_labels: tuple[str, ...]) -> Any:
    """the bounded head on every localization token and the zero-mean pin on every potential token, elsewhere untouched"""
    token_means = Channel_Means(reconstruction)
    zero_mean_version = reconstruction - token_means
    bounded_version = Bounded_Unit_Interval(reconstruction)
    per_token = [
        bounded_version[position:position + 1]
        if label in ELF_GROUP
        else zero_mean_version[position:position + 1]
        if label in POTENTIAL_GROUP
        else reconstruction[position:position + 1]
        for position, label in enumerate(present_labels)
    ]
    return Concatenate_Channels(per_token)
