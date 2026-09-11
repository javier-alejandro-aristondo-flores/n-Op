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
        output_channel_labels: tuple[str, ...] = ("predicted_field",),
        seed: int = 0,
    ) -> None:
        self.output_channel_labels = output_channel_labels
        self.coordinate_features = (
            coordinate_features if coordinate_features is not None else PeriodicCoordinateFeatures()
        )
        self.trunk = MultilayerPerceptron(
            (self.coordinate_features.feature_count, *trunk_widths, latent_width), "trunk", seed
        )
        self.parameter_values = self.trunk.parameter_values
        self.last_trunk_features: NDArray[np.float64] | None = None
        self.last_query_grid_shape: tuple[int, int, int] | None = None


    def Coordinate_Features(self, points: NDArray[np.float64]) -> NDArray[np.float64]:
        """the features the configured map reads off the points"""
        return self.coordinate_features(points)


    def Forward(self, lifted: dict[str, Any], branch_coefficients: Any, trunk_features: Any) -> Any:
        trunk_values = self.trunk.Forward(lifted, trunk_features)
        # one channel arrives as a bare latent vector, several as one latent row each
        if branch_coefficients.ndim == 1:
            return trunk_values @ branch_coefficients
        return trunk_values @ branch_coefficients.T


    def __call__(
        self,
        input_function: Coefficients,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> Representation:
        points = Output_Points(output_discretization)
        trunk_features = self.Coordinate_Features(points)
        self.last_trunk_features = trunk_features
        # whether the query was a grid decides whether a feature column is a field or a bare list
        self.last_query_grid_shape = (
            output_discretization.shape if isinstance(output_discretization, GridSpec) else None
        )
        branch_coefficients = np.asarray(input_function.vector, dtype=np.float64)
        channel_count = len(self.output_channel_labels)
        if branch_coefficients.ndim == 2 and branch_coefficients.shape[0] != channel_count:
            raise ValueError(
                f"the branch offered {branch_coefficients.shape[0]} channels for {channel_count} labels"
            )
        produced = np.asarray(
            self.Forward(self.parameter_values, branch_coefficients, trunk_features), dtype=np.float64
        )
        # every path below reads one column per output channel
        if produced.ndim == 1:
            produced = produced[:, None]
        # the same trunk answers a grid and a bare list of points, only the wrapper differs
        if isinstance(output_discretization, GridSpec):
            shape = output_discretization.shape
            point_count = shape[0] * shape[1] * shape[2]
            cell_volume = abs(float(np.linalg.det(np.asarray(input_function.domain.lattice))))
            quadrature = UniformGridQuadrature(cell_volume, point_count)
            return GridFunction(
                produced.T.reshape(channel_count, *shape),
                self.output_channel_labels,
                input_function.domain,
                quadrature,
            )
        return PointSet(positions=points, domain=input_function.domain, values=produced)


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = dict(self.parameter_values)
        if self.last_trunk_features is not None:
            features = self.last_trunk_features
            if self.last_query_grid_shape is not None:
                # a feature evaluated over a grid is a field, and is inspected with that shape
                features = features.reshape(*self.last_query_grid_shape, features.shape[1])
            state["last_trunk_features"] = features
        return state


class FixedModeExpansion(Operator[Coefficients, GridFunction]):
    """branch coefficients carried onto a field by fixed modes and the training mean"""


    def __init__(self, basis: PodBasis, grid_shape: tuple[int, int, int]) -> None:
        self.basis = basis
        self.grid_shape = grid_shape
        # the basis is given rather than learned, so the readout owns no parameters of its own
        self.parameter_values: dict[str, NDArray[np.float64]] = {}
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
        # a mode is a field, so it is inspected with the shape that makes it one
        state: dict[str, Array] = {
            "basis_modes": self.basis.modes.reshape(self.basis.modes.shape[0], *self.grid_shape),
            "basis_singular_values": self.basis.singular_values,
            "basis_mean": self.basis.mean.reshape(self.grid_shape),
        }
        if self.last_coefficients is not None:
            state["last_coefficients"] = self.last_coefficients
        return state


class BiasedModeExpansion(Operator[Coefficients, GridFunction]):
    """branch coefficients carried onto a field by fixed modes, the training mean and one learned offset"""


    def __init__(self, basis: PodBasis, grid_shape: tuple[int, int, int]) -> None:
        self.basis = basis
        self.grid_shape = grid_shape
        # the offset is the readout's only trained array, held apart from the fixed modes and mean
        self.parameter_values: dict[str, NDArray[np.float64]] = {"output_bias": np.zeros(1)}
        self.last_coefficients: NDArray[np.float64] | None = None


    def Forward(self, lifted: dict[str, Any], branch_vector: Any, basis_modes: Any, basis_mean: Any) -> Any:
        """the published form, modes weighted by the branch, the training mean and the learned offset"""
        return branch_vector @ basis_modes + basis_mean + lifted["output_bias"]


    def Lifted_Constants(self, engine: Engine) -> tuple[Any, Any]:
        """the modes and mean as engine constants, so gradients reach only the branch and the offset"""
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
            self.Forward(self.parameter_values, coefficients, self.basis.modes, self.basis.mean), dtype=np.float64
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
        # a mode is a field, so it is inspected with the shape that makes it one
        state: dict[str, Array] = {
            "basis_modes": self.basis.modes.reshape(self.basis.modes.shape[0], *self.grid_shape),
            "basis_singular_values": self.basis.singular_values,
            "basis_mean": self.basis.mean.reshape(self.grid_shape),
            "output_bias": self.parameter_values["output_bias"],
        }
        if self.last_coefficients is not None:
            state["last_coefficients"] = self.last_coefficients
        return state


class PointwiseStandardizedExpansion(Operator[Coefficients, GridFunction]):
    """fixed modes read in a per-voxel standardized field, carried back to the training block's scale"""


    def __init__(
        self,
        basis: PodBasis,
        grid_shape: tuple[int, int, int],
        voxel_mean: NDArray[np.float64],
        voxel_scale: NDArray[np.float64],
    ) -> None:
        self.basis = basis
        self.grid_shape = grid_shape
        # each voxel's own mean and spread across the training runs, fixed rather than trained
        self.voxel_mean = voxel_mean
        self.voxel_scale = voxel_scale
        # the offset is the readout's only trained array, held apart from every fixed statistic
        self.parameter_values: dict[str, NDArray[np.float64]] = {"output_bias": np.zeros(1)}
        self.last_coefficients: NDArray[np.float64] | None = None


    def Forward(
        self,
        lifted: dict[str, Any],
        branch_vector: Any,
        basis_modes: Any,
        basis_mean: Any,
        voxel_mean: Any,
        voxel_scale: Any,
    ) -> Any:
        """modes weighted by the branch and the learned offset, standardized, then carried back"""
        standardized = branch_vector @ basis_modes + basis_mean + lifted["output_bias"]
        return standardized * voxel_scale + voxel_mean


    def Lifted_Constants(self, engine: Engine) -> tuple[Any, Any, Any, Any]:
        """the modes, the standardized-space mean and the pointwise statistics, as engine constants"""
        return (
            engine.Lift_Constant(self.basis.modes),
            engine.Lift_Constant(self.basis.mean),
            engine.Lift_Constant(self.voxel_mean),
            engine.Lift_Constant(self.voxel_scale),
        )


    def __call__(
        self,
        input_function: Coefficients,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        coefficients = np.asarray(input_function.vector, dtype=np.float64)
        self.last_coefficients = coefficients
        produced = np.asarray(
            self.Forward(
                self.parameter_values,
                coefficients,
                self.basis.modes,
                self.basis.mean,
                self.voxel_mean,
                self.voxel_scale,
            ),
            dtype=np.float64,
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
        # a mode or a pointwise statistic is a field, so each is inspected with the shape that makes it one
        state: dict[str, Array] = {
            "basis_modes": self.basis.modes.reshape(self.basis.modes.shape[0], *self.grid_shape),
            "basis_singular_values": self.basis.singular_values,
            "basis_mean": self.basis.mean.reshape(self.grid_shape),
            "voxel_mean": self.voxel_mean.reshape(self.grid_shape),
            "voxel_scale": self.voxel_scale.reshape(self.grid_shape),
            "output_bias": self.parameter_values["output_bias"],
        }
        if self.last_coefficients is not None:
            state["last_coefficients"] = self.last_coefficients
        return state
