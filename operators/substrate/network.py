"""The multilayer perceptron primitive: named weight matrices with a smooth unit between."""

from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.substrate.operations import Gaussian_Error_Linear_Unit


class MultilayerPerceptron:
    """Chained linear maps with the smooth unit between, parameters held as named arrays."""


    def __init__(self, layer_widths: tuple[int, ...], name_prefix: str, seed: int = 0) -> None:
        self.layer_widths = layer_widths
        self.name_prefix = name_prefix
        generator = np.random.default_rng(seed)
        self.parameter_values: dict[str, NDArray[np.float64]] = {}
        for layer_index in range(len(layer_widths) - 1):
            fan_in = layer_widths[layer_index]
            fan_out = layer_widths[layer_index + 1]
            scale = np.sqrt(2.0 / (fan_in + fan_out))
            self.parameter_values[f"{name_prefix}_layer_{layer_index}_weights"] = generator.normal(
                0.0, scale, size=(fan_out, fan_in)
            )
            self.parameter_values[f"{name_prefix}_layer_{layer_index}_biases"] = np.zeros(fan_out)


    def Forward(self, lifted: dict[str, Any], inputs: Any) -> Any:
        value = inputs
        last_layer_index = len(self.layer_widths) - 2
        for layer_index in range(len(self.layer_widths) - 1):
            weights = lifted[f"{self.name_prefix}_layer_{layer_index}_weights"]
            biases = lifted[f"{self.name_prefix}_layer_{layer_index}_biases"]
            value = value @ weights.T + biases
            if layer_index != last_layer_index:
                value = Gaussian_Error_Linear_Unit(value)
        return value


    def Apply(self, inputs: NDArray[np.float64]) -> NDArray[np.float64]:
        return np.asarray(self.Forward(self.parameter_values, inputs), dtype=np.float64)
