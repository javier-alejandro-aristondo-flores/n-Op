"""maps from the channel space back to corpus fields, queryable anywhere"""

from abc import abstractmethod
from typing import Any, Protocol

import numpy as np
from numpy.typing import NDArray

from operators.framework import (
    Array,
    Coefficients,
    Discretization,
    GridFunction,
    GridSpec,
    Operator,
    Output_Points,
    PointSet,
    Representation,
    UniformGridQuadrature,
)
from operators.data import PodBasis
from operators.substrate import Engine, MultilayerPerceptron, Softplus


class PointwiseProjection(Operator[GridFunction, GridFunction]):
    """hidden channels mixed down to output channels, optionally through the bounded head"""


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
            # one over one plus a square lands in zero to one without ever touching either end
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
        labels = tuple(f"output_{output_channel}" for output_channel in range(produced.shape[0]))
        return GridFunction(produced, labels, input_function.domain, input_function.quadrature)


    def Inspect(self) -> dict[str, Array]:
        return dict(self.parameter_values)


class CoordinateFeatures(Protocol):
    """turns evaluation points into the numbers a trunk reads"""

    feature_count: int


    @abstractmethod
    def __call__(self, points: NDArray[np.float64]) -> NDArray[np.float64]: ...


def Integer_Frequency_Waves(points: NDArray[np.float64], fourier_orders: int) -> list[NDArray[np.float64]]:
    """cosine and sine blocks at whole numbers of cycles across the cell"""
    blocks: list[NDArray[np.float64]] = []
    for order in range(1, fourier_orders + 1):
        angle = 2.0 * np.pi * order * points
        blocks.append(np.cos(angle))
        blocks.append(np.sin(angle))
    return blocks


class PeriodicCoordinateFeatures(CoordinateFeatures):
    """a constant beside the waves, so every feature repeats where the cell does"""


    def __init__(self, fourier_orders: int = 4, axis_count: int = 3) -> None:
        self.fourier_orders = fourier_orders
        self.axis_count = axis_count
        self.feature_count = 1 + 2 * fourier_orders * axis_count


    def __call__(self, points: NDArray[np.float64]) -> NDArray[np.float64]:
        # a constant stands where the raw coordinate would, which is the one block that does not wrap
        constant = np.ones((points.shape[0], 1), dtype=np.float64)
        return np.concatenate([constant, *Integer_Frequency_Waves(points, self.fourier_orders)], axis=1)


class RampedCoordinateFeatures(CoordinateFeatures):
    """the raw coordinate beside the waves, for an axis that does not repeat"""


    def __init__(self, fourier_orders: int = 4, axis_count: int = 1) -> None:
        self.fourier_orders = fourier_orders
        self.axis_count = axis_count
        self.feature_count = axis_count + 2 * fourier_orders * axis_count


    def __call__(self, points: NDArray[np.float64]) -> NDArray[np.float64]:
        return np.concatenate([points, *Integer_Frequency_Waves(points, self.fourier_orders)], axis=1)


class BasisExpansion(Operator[Coefficients, Representation]):
    """a coordinate trunk evaluated against branch coefficients at any requested points"""


    def __init__(
        self,
        latent_width: int,
        trunk_widths: tuple[int, ...],
        coordinate_features: CoordinateFeatures | None = None,
        seed: int = 0,
    ) -> None:
        self.coordinate_features = (
            coordinate_features if coordinate_features is not None else PeriodicCoordinateFeatures()
        )
        self.trunk = MultilayerPerceptron(
            (self.coordinate_features.feature_count, *trunk_widths, latent_width), "trunk", seed
        )
        self.parameter_values = self.trunk.parameter_values
        self.last_trunk_features: NDArray[np.float64] | None = None


    def Coordinate_Features(self, points: NDArray[np.float64]) -> NDArray[np.float64]:
        """the features the configured map reads off the points"""
        return self.coordinate_features(points)


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
        # the same trunk answers a grid and a bare list of points, only the wrapper differs
        if isinstance(output_discretization, GridSpec):
            shape = output_discretization.shape
            point_count = shape[0] * shape[1] * shape[2]
            cell_volume = abs(float(np.linalg.det(np.asarray(input_function.domain.lattice))))
            quadrature = UniformGridQuadrature(cell_volume, point_count)
            return GridFunction(produced.reshape(1, *shape), ("predicted_field",), input_function.domain, quadrature)
        return PointSet(positions=points, domain=input_function.domain, values=produced.reshape(-1, 1))


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = dict(self.parameter_values)
        if self.last_trunk_features is not None:
            state["last_trunk_features"] = self.last_trunk_features
        return state


class FixedModeExpansion(Operator[Coefficients, GridFunction]):
    """branch coefficients carried onto a field by fixed modes and the training mean"""


    def __init__(self, basis: PodBasis, grid_shape: tuple[int, int, int]) -> None:
        self.basis = basis
        self.grid_shape = grid_shape
        self.last_coefficients: NDArray[np.float64] | None = None


    def Forward(self, branch_vector: Any, basis_modes: Any, basis_mean: Any) -> Any:
        """the published form, modes weighted by the branch with the training mean added back"""
        return branch_vector @ basis_modes + basis_mean


    def Lifted_Constants(self, engine: Engine) -> tuple[Any, Any]:
        """the modes and mean as engine constants, so gradients reach only the branch"""
        return engine.Lift_Constant(self.basis.modes), engine.Lift_Constant(self.basis.mean)


    def __call__(
        self,
        input_function: Coefficients,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        coefficients = np.asarray(input_function.vector, dtype=np.float64)
        self.last_coefficients = coefficients
        produced = np.asarray(
            self.Forward(coefficients, self.basis.modes, self.basis.mean), dtype=np.float64
        )
        cell_volume = abs(float(np.linalg.det(np.asarray(input_function.domain.lattice))))
        quadrature = UniformGridQuadrature(cell_volume, produced.size)
        return GridFunction(
            produced.reshape(1, *self.grid_shape),
            ("predicted_field",),
            input_function.domain,
            quadrature,
        )


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = {
            "basis_modes": self.basis.modes,
            "basis_singular_values": self.basis.singular_values,
            "basis_mean": self.basis.mean,
        }
        if self.last_coefficients is not None:
            state["last_coefficients"] = self.last_coefficients
        return state
