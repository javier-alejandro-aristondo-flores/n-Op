"""Readouts: maps from the channel space back to corpus fields, queryable anywhere."""

from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.framework import (
    Coefficients,
    Discretization,
    GridFunction,
    GridSpec,
    Operator,
    PointSet,
    Representation,
    UniformGridQuadrature,
)
from operators.framework.domain import Array
from operators.framework.integral import Output_Points
from operators.substrate.network import MultilayerPerceptron
from operators.substrate.operations import Softplus


class PointwiseProjection(Operator[GridFunction, GridFunction]):
    """Mixes hidden channels down to output channels, optionally through the bounded head."""


    def __init__(self, output_channels: int, hidden_channels: int, bounded: bool = False, seed: int = 0) -> None:
        generator = np.random.default_rng(seed)
        scale = np.sqrt(2.0 / (output_channels + hidden_channels))
        self.bounded = bounded
        self.parameter_values: dict[str, NDArray[np.float64]] = {
            "projection_weights": generator.normal(0.0, scale, size=(output_channels, hidden_channels)),
            "projection_biases": np.zeros(output_channels),
        }


    def Forward(self, lifted: dict[str, Any], input_values: Any) -> Any:
        flattened = input_values.reshape(input_values.shape[0], -1)
        mixed = lifted["projection_weights"] @ flattened + lifted["projection_biases"][:, None]
        mixed = mixed.reshape(lifted["projection_weights"].shape[0], *input_values.shape[1:])
        if self.bounded:
            softened = Softplus(mixed)
            return 1.0 / (1.0 + softened * softened)
        return mixed


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        produced = np.asarray(self.Forward(self.parameter_values, np.asarray(input_function.values)))
        labels = tuple(f"output_{index}" for index in range(produced.shape[0]))
        return GridFunction(produced, labels, input_function.domain, input_function.quadrature)


    def Inspect(self) -> dict[str, Array]:
        return dict(self.parameter_values)


class BasisExpansion(Operator[Coefficients, Representation]):
    """Evaluates a coordinate trunk against branch coefficients at any requested points."""


    def __init__(self, latent_width: int, trunk_widths: tuple[int, ...], fourier_orders: int = 4, seed: int = 0) -> None:
        self.fourier_orders = fourier_orders
        feature_count = 3 + 6 * fourier_orders
        self.trunk = MultilayerPerceptron((feature_count, *trunk_widths, latent_width), "trunk", seed)
        self.parameter_values = self.trunk.parameter_values
        self.last_trunk_features: NDArray[np.float64] | None = None


    def Coordinate_Features(self, points: NDArray[np.float64]) -> NDArray[np.float64]:
        """Builds periodic coordinate features: raw fractions and integer-frequency waves."""
        feature_blocks = [points]
        for order in range(1, self.fourier_orders + 1):
            angle = 2.0 * np.pi * order * points
            feature_blocks.append(np.cos(angle))
            feature_blocks.append(np.sin(angle))
        return np.concatenate(feature_blocks, axis=1)


    def Forward(self, lifted: dict[str, Any], branch_vector: Any, trunk_features: Any) -> Any:
        trunk_values = self.trunk.Forward(lifted, trunk_features)
        return trunk_values @ branch_vector


    def __call__(
        self,
        input_function: Coefficients,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> Representation:
        points = Output_Points(output_discretization)
        trunk_features = self.Coordinate_Features(points)
        self.last_trunk_features = trunk_features
        branch_vector = np.asarray(input_function.vector, dtype=np.float64)
        produced = np.asarray(
            self.Forward(self.parameter_values, branch_vector, trunk_features), dtype=np.float64
        )
        if isinstance(output_discretization, GridSpec):
            shape = output_discretization.shape
            point_count = shape[0] * shape[1] * shape[2]
            quadrature = UniformGridQuadrature(abs(float(np.linalg.det(np.asarray(input_function.domain.lattice)))), point_count)
            return GridFunction(produced.reshape(1, *shape), ("predicted_field",), input_function.domain, quadrature)
        return PointSet(positions=points, domain=input_function.domain, values=produced.reshape(-1, 1))


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = dict(self.parameter_values)
        if self.last_trunk_features is not None:
            state["last_trunk_features"] = self.last_trunk_features
        return state


__all__ = [
    "PointwiseProjection",
    "BasisExpansion",
]
