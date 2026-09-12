"""strain or lattice parameters to a charge density field, by a branch read against a basis"""

import dataclasses
from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.compositions import WithoutIntegralLayers
from operators.data import PodBasis
from operators.encoders import SensorEncoder
from operators.framework import (
    Array,
    Coefficients,
    Discretization,
    GridFunction,
    NeuralOperator,
    PointSet,
    Representation,
)
from operators.readouts import (
    BasisExpansion,
    BiasedModeExpansion,
    FixedModeExpansion,
    PointwiseStandardizedExpansion,
    RampedCoordinateFeatures,
)
from operators.substrate import Softplus, Sum_Over_Last_Axis

CONFIGURATIONS = ("canonical", "proper_orthogonal", "principal_component", "energy_trunk")
# the one configuration whose readout is a pre-activation, never the physical quantity itself
NONNEGATIVE_HEAD_CONFIGURATION = "energy_trunk"


def Nonnegative_Curve(produced: Representation) -> tuple[Representation, NDArray[np.float64]]:
    """the readout's raw output carried through the non-negative head, paired with its flattened values"""
    if isinstance(produced, GridFunction):
        values = np.asarray(Softplus(np.asarray(produced.values, dtype=np.float64)), dtype=np.float64)
        return dataclasses.replace(produced, values=values), values.reshape(-1)
    if isinstance(produced, PointSet):
        if produced.values is None:
            raise ValueError("a point set with no values has nothing for the non-negative head to act on")
        values = np.asarray(Softplus(np.asarray(produced.values, dtype=np.float64)), dtype=np.float64)
        return dataclasses.replace(produced, values=values), values.reshape(-1)
    raise TypeError("the non-negative head only knows how to read a grid function or a point set")


class DeepOperatorNetwork(NeuralOperator[Coefficients, Coefficients, Representation]):
    """a branch network over run parameters, read against a fixed or learned basis"""


    def __init__(
        self,
        branch: SensorEncoder,
        readout: BasisExpansion | FixedModeExpansion | BiasedModeExpansion | PointwiseStandardizedExpansion,
        configuration: str,
    ) -> None:
        if configuration not in CONFIGURATIONS:
            raise ValueError(f"{configuration} is not one of the member's configurations")
        super().__init__(branch, WithoutIntegralLayers(), readout)
        self.branch = branch
        self.basis_readout = readout
        self.configuration = configuration
        self.last_predicted_curve: NDArray[np.float64] | None = None


    def __call__(
        self,
        input_function: Coefficients,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> Representation:
        latent = self.encoder(input_function, output_discretization, condition)
        carried = self.composition.Apply(latent, condition)
        produced = self.readout(carried, output_discretization, condition)
        if self.configuration != NONNEGATIVE_HEAD_CONFIGURATION:
            return produced
        curve, flattened = Nonnegative_Curve(produced)
        self.last_predicted_curve = flattened
        return curve


    def Inspect(self) -> dict[str, Array]:
        """every part's own arrays, plus the physical curve the non-negative head last produced"""
        state = super().Inspect()
        if self.last_predicted_curve is not None:
            state["last_predicted_curve"] = self.last_predicted_curve
        return state


    def Parameter_Values(self) -> dict[str, NDArray[np.float64]]:
        """every learned array of the assembly under one namespace, ready for the trainer"""
        collected = dict(self.branch.parameter_values)
        collected.update(self.basis_readout.parameter_values)
        return collected


    def Forward_Coefficients(self, lifted: dict[str, Any], branch_input: Any) -> Any:
        """the branch's latent coefficients, differentiable through whichever engine lifted them"""
        return self.branch.network.Forward(lifted, branch_input)


    def Forward_Point_Values(self, lifted: dict[str, Any], branch_input: Any, trunk_features: Any) -> Any:
        """predicted values at sampled points, each run's own trunk features read against its own coefficients"""
        readout = self.basis_readout
        if not isinstance(readout, BasisExpansion):
            raise TypeError("a point-sampled forward needs the learned coordinate trunk")
        coefficients = self.Forward_Coefficients(lifted, branch_input)
        trunk_values = readout.trunk.Forward(lifted, trunk_features)
        # each run reads only its own points against its own coefficients, never another run's
        raw_values = Sum_Over_Last_Axis(trunk_values * coefficients[:, None, :])
        # a density of states is non-negative and unbounded above, never the localization range
        if self.configuration == NONNEGATIVE_HEAD_CONFIGURATION:
            return Softplus(raw_values)
        return raw_values


def Principal_Component_Network(
    basis: PodBasis,
    grid_shape: tuple[int, int, int],
    parameter_width: int,
    hidden_widths: tuple[int, ...],
    seed: int = 0,
) -> DeepOperatorNetwork:
    """the fixed-basis member: run parameters mapped onto stored mode coefficients"""
    rank = int(basis.modes.shape[0])
    branch = SensorEncoder((parameter_width, *hidden_widths, rank), seed=seed)
    return DeepOperatorNetwork(branch, FixedModeExpansion(basis, grid_shape), "principal_component")


def Pointwise_Statistics(training_fields: NDArray[np.float64]) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """each voxel's own mean and spread across a training block, spread guarded away from zero"""
    voxel_mean = training_fields.mean(axis=0)
    voxel_scale = training_fields.std(axis=0)
    # a voxel with no spread across every training run would otherwise divide by zero
    voxel_scale[voxel_scale == 0.0] = 1.0
    return voxel_mean, voxel_scale


def Reference_Density(electron_count: float, cell_volume: NDArray[np.float64]) -> NDArray[np.float64]:
    """the flat density one run's own electron count would give its own cell, its exact spatial mean"""
    return electron_count / cell_volume


def Reference_Density_Standardized(
    field: NDArray[np.float64], reference_density: NDArray[np.float64]
) -> NDArray[np.float64]:
    """a field divided by its own run's reference density, so every run's own spatial mean lands near one"""
    return field / reference_density


def Reference_Density_Restored(
    standardized: NDArray[np.float64], reference_density: NDArray[np.float64]
) -> NDArray[np.float64]:
    """a standardized field carried back onto physical density units by the same run's reference density"""
    return standardized * reference_density


def Proper_Orthogonal_Network(
    basis: PodBasis,
    grid_shape: tuple[int, int, int],
    voxel_mean: NDArray[np.float64],
    voxel_scale: NDArray[np.float64],
    parameter_width: int,
    hidden_widths: tuple[int, ...],
    seed: int = 0,
) -> DeepOperatorNetwork:
    """the fixed-basis member on a per-voxel standardized field: run parameters mapped onto its coefficients"""
    rank = int(basis.modes.shape[0])
    branch = SensorEncoder((parameter_width, *hidden_widths, rank), seed=seed)
    readout = PointwiseStandardizedExpansion(basis, grid_shape, voxel_mean, voxel_scale)
    return DeepOperatorNetwork(branch, readout, "proper_orthogonal")


def Canonical_Network(
    parameter_width: int,
    branch_hidden_widths: tuple[int, ...],
    latent_width: int,
    trunk_hidden_widths: tuple[int, ...],
    seed: int = 0,
) -> DeepOperatorNetwork:
    """the learned-trunk member: a branch latent read against a coordinate trunk at any query point"""
    branch = SensorEncoder((parameter_width, *branch_hidden_widths, latent_width), seed=seed)
    # the trunk is seeded one past the branch, so the two draws never share a stream
    readout = BasisExpansion(latent_width, trunk_hidden_widths, seed=seed + 1)
    return DeepOperatorNetwork(branch, readout, "canonical")


def Energy_Trunk_Network(
    parameter_width: int,
    branch_hidden_widths: tuple[int, ...],
    latent_width: int,
    trunk_hidden_widths: tuple[int, ...],
    fourier_orders: int = 4,
    seed: int = 0,
) -> DeepOperatorNetwork:
    """the energy-trunk member: a branch latent read against a trunk over energy, non-negative by construction"""
    branch = SensorEncoder((parameter_width, *branch_hidden_widths, latent_width), seed=seed)
    coordinate_features = RampedCoordinateFeatures(fourier_orders, axis_count=1)
    # the trunk is seeded one past the branch, so the two draws never share a stream
    readout = BasisExpansion(latent_width, trunk_hidden_widths, coordinate_features, seed=seed + 1)
    return DeepOperatorNetwork(branch, readout, "energy_trunk")
