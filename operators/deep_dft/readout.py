"""the per-probe head mapping message-passing features to density and magnetization"""

from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.framework import Array, Coefficients, Discretization, Operator, PointSet
from operators.substrate import MultilayerPerceptron

OUTPUT_CHANNEL_LABELS = ("charge_density", "magnetization_density")


class ProbeHead(Operator[PointSet, PointSet]):
    """a small perceptron read at every point, producing the density and magnetization channels"""


    def __init__(self, hidden_channels: int, seed: int = 0) -> None:
        widths = (hidden_channels, hidden_channels, len(OUTPUT_CHANNEL_LABELS))
        self.network = MultilayerPerceptron(widths, "probe_head", seed)
        self.parameter_values = self.network.parameter_values
        self.last_predicted_values: NDArray[np.float64] | None = None


    def Forward(self, lifted: dict[str, Any], probe_values: Any) -> Any:
        return self.network.Forward(lifted, probe_values)


    def __call__(
        self,
        input_function: PointSet,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> PointSet:
        if input_function.values is None:
            raise ValueError("the probe head needs point values to read")
        produced = self.network.Apply(np.asarray(input_function.values, dtype=np.float64))
        self.last_predicted_values = produced
        return PointSet(
            positions=input_function.positions,
            domain=input_function.domain,
            values=produced,
            quadrature=input_function.quadrature,
        )


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = dict(self.parameter_values)
        if self.last_predicted_values is not None:
            state["last_predicted_values"] = self.last_predicted_values
        return state
