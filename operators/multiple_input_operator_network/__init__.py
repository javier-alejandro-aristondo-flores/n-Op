"""charge density and local potential to electron localization"""

import dataclasses
from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.compositions import Sliced_Lifted, WithoutIntegralLayers
from operators.data import PodBasis
from operators.encoders import BasisProjectionEncoder, SensorEncoder
from operators.factorized_fourier import Log_Compressed_Channels
from operators.framework import (
    Array,
    Coefficients,
    Discretization,
    GridFunction,
    NeuralOperator,
    Operator,
    PointSet,
    Representation,
)
from operators.readouts import BasisExpansion, PeriodicCoordinateFeatures
from operators.substrate import Softplus, Sum_Over_Last_Axis

CHANNEL_COUNT = 2

LATENT_WIDTH = 128

BRANCH_HIDDEN_WIDTH = 128

TRUNK_HIDDEN_WIDTHS = (256, 256, 256)

INPUT_DENSITY_LABELS = ("charge_density", "magnetization_density")

INPUT_POTENTIAL_LABELS = ("local_potential_up", "local_potential_down")

DERIVED_DENSITY_LABELS = ("log_spin_density_up", "log_spin_density_down")

DERIVED_POTENTIAL_LABELS = ("mean_removed_potential_up", "mean_removed_potential_down")

OUTPUT_CHANNEL_LABELS = ("electron_localization_up", "electron_localization_down")


def Labeled_Channel(input_function: GridFunction, label: str) -> NDArray[np.float64]:
    """one named channel's own values, refusing a field that carries no channel under that label"""
    if label not in input_function.channel_labels:
        raise ValueError(f"the field carries no channel labeled {label!r}, only {input_function.channel_labels}")
    position = input_function.channel_labels.index(label)
    return np.asarray(input_function.values, dtype=np.float64)[position]


def Density_Channels(input_function: GridFunction, reference_density: float) -> NDArray[np.float64]:
    """the two log-compressed spin-density channels the density branch reads, the flagship's own convention"""
    density = Labeled_Channel(input_function, INPUT_DENSITY_LABELS[0])
    magnetization = Labeled_Channel(input_function, INPUT_DENSITY_LABELS[1])
    return Log_Compressed_Channels(density, magnetization, reference_density)


def Potential_Channels(input_function: GridFunction) -> NDArray[np.float64]:
    """the two mean-removed spin-potential channels the potential branch reads, still in raw physical units"""
    potential_up = Labeled_Channel(input_function, INPUT_POTENTIAL_LABELS[0])
    potential_down = Labeled_Channel(input_function, INPUT_POTENTIAL_LABELS[1])
    return np.stack([potential_up - potential_up.mean(), potential_down - potential_down.mean()])


def Standardized_Potential_Coefficients(
    raw_coefficients: NDArray[np.float64],
    potential_coefficient_mean: NDArray[np.float64],
    potential_coefficient_scale: NDArray[np.float64],
) -> NDArray[np.float64]:
    """the potential basis's own raw coefficients centered and scaled per coefficient by training-fold statistics"""
    return (raw_coefficients - potential_coefficient_mean) / potential_coefficient_scale


def As_Grid_Function(values: NDArray[np.float64], labels: tuple[str, ...], like: GridFunction) -> GridFunction:
    """values wrapped as a grid function carrying another field's own domain and quadrature"""
    return GridFunction(values, labels, like.domain, like.quadrature)


def Basis_Projection_Inspection(
    projection: BasisProjectionEncoder, channel_labels: tuple[str, ...], grid_shape: tuple[int, ...] | None
) -> dict[str, Array]:
    """a fixed basis projection's own arrays, its mean and modes split back into one field per channel it was fit on"""
    state: dict[str, Array] = {"basis_mode_norms": np.linalg.norm(projection.basis_modes, axis=1)}
    if grid_shape is not None:
        channel_count = len(channel_labels)
        mean_by_channel = projection.basis_mean.reshape(channel_count, *grid_shape)
        modes_by_channel = projection.basis_modes.reshape(projection.basis_modes.shape[0], channel_count, *grid_shape)
        for channel_index, label in enumerate(channel_labels):
            state[f"basis_mean_{label}"] = mean_by_channel[channel_index]
            state[f"basis_modes_{label}"] = modes_by_channel[:, channel_index]
    else:
        state["basis_mean"] = projection.basis_mean
    if projection.last_coefficients is not None:
        state["last_coefficients"] = projection.last_coefficients
    return state


def Bounded_Values(raw_values: Any) -> Any:
    """the raw trunk output carried through the zero-to-one head, one over one plus a square"""
    softened = Softplus(raw_values)
    return 1.0 / (1.0 + softened * softened)


def Bounded_Field(produced: Representation) -> tuple[Representation, NDArray[np.float64]]:
    """the readout's raw output carried through the bounded head, paired with its flattened values"""
    if isinstance(produced, GridFunction):
        values = np.asarray(Bounded_Values(np.asarray(produced.values, dtype=np.float64)), dtype=np.float64)
        return dataclasses.replace(produced, values=values), values.reshape(-1)
    if isinstance(produced, PointSet):
        if produced.values is None:
            raise ValueError("a point set with no values has nothing for the bounded head to act on")
        values = np.asarray(Bounded_Values(np.asarray(produced.values, dtype=np.float64)), dtype=np.float64)
        return dataclasses.replace(produced, values=values), values.reshape(-1)
    raise TypeError("the bounded head only knows how to read a grid function or a point set")


class TwoBranchEncoder(Operator[GridFunction, Coefficients]):
    """two fixed-basis sensor branches combined multiplicatively, split into one coefficient row per output channel"""


    def __init__(
        self,
        density_projection: BasisProjectionEncoder,
        density_branch: SensorEncoder,
        potential: tuple[BasisProjectionEncoder, SensorEncoder, NDArray[np.float64], NDArray[np.float64]] | None,
        reference_density: float,
        seed: int = 0,
    ) -> None:
        self.density_projection = density_projection
        self.density_branch = density_branch
        self.potential = potential
        self.reference_density = reference_density
        # the ranks and the shared latent width are read off the branches themselves, never assumed
        self.density_rank = int(density_branch.network.layer_widths[0])
        self.latent_width = int(density_branch.network.layer_widths[-1])
        if potential is None:
            self.potential_rank = 0
        else:
            _, potential_branch, _, _ = potential
            if int(potential_branch.network.layer_widths[-1]) != self.latent_width:
                raise ValueError("the two branches must share one latent width for their product to be defined")
            self.potential_rank = int(potential_branch.network.layer_widths[0])
        generator = np.random.default_rng(seed)
        split_width = CHANNEL_COUNT * self.latent_width
        scale = np.sqrt(2.0 / (split_width + self.latent_width))
        self.parameter_values: dict[str, NDArray[np.float64]] = {
            "channel_head_weights": generator.normal(0.0, scale, size=(split_width, self.latent_width)),
            "channel_head_biases": np.zeros(split_width),
        }
        self.last_density_coefficients: NDArray[np.float64] | None = None
        self.last_potential_coefficients: NDArray[np.float64] | None = None
        self.last_combined_latent: NDArray[np.float64] | None = None
        self.last_density_grid_shape: tuple[int, ...] | None = None
        self.last_potential_grid_shape: tuple[int, ...] | None = None


    def Parameter_Values(self) -> dict[str, NDArray[np.float64]]:
        """every sub-part's own arrays, prefixed so the two branches' identically named layers never collide"""
        collected = {f"density_branch.{name}": value for name, value in self.density_branch.parameter_values.items()}
        if self.potential is not None:
            _, potential_branch, _, _ = self.potential
            collected.update(
                {f"potential_branch.{name}": value for name, value in potential_branch.parameter_values.items()}
            )
        collected.update(self.parameter_values)
        return collected


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> Coefficients:
        density_field = As_Grid_Function(
            Density_Channels(input_function, self.reference_density), DERIVED_DENSITY_LABELS, input_function
        )
        self.last_density_grid_shape = density_field.values.shape[1:]
        density_coefficients = self.density_projection(density_field, output_discretization, condition)
        density_latent = self.density_branch(density_coefficients, output_discretization, condition)
        self.last_density_coefficients = np.asarray(density_coefficients.vector, dtype=np.float64)
        density_vector = np.asarray(density_latent.vector, dtype=np.float64)
        if self.potential is None:
            combined = density_vector
        else:
            potential_projection, potential_branch, potential_coefficient_mean, potential_coefficient_scale = (
                self.potential
            )
            potential_field = As_Grid_Function(
                Potential_Channels(input_function), DERIVED_POTENTIAL_LABELS, input_function
            )
            self.last_potential_grid_shape = potential_field.values.shape[1:]
            raw_potential_coefficients = potential_projection(potential_field, output_discretization, condition)
            standardized_vector = Standardized_Potential_Coefficients(
                np.asarray(raw_potential_coefficients.vector, dtype=np.float64),
                potential_coefficient_mean,
                potential_coefficient_scale,
            )
            potential_coefficients = dataclasses.replace(raw_potential_coefficients, vector=standardized_vector)
            potential_latent = potential_branch(potential_coefficients, output_discretization, condition)
            self.last_potential_coefficients = standardized_vector
            combined = density_vector * np.asarray(potential_latent.vector, dtype=np.float64)
        self.last_combined_latent = combined
        split = self.parameter_values["channel_head_weights"] @ combined + self.parameter_values["channel_head_biases"]
        return Coefficients(vector=split.reshape(CHANNEL_COUNT, self.latent_width), domain=input_function.domain)


    def Inspect(self) -> dict[str, Array]:
        density_inspected = Basis_Projection_Inspection(
            self.density_projection, DERIVED_DENSITY_LABELS, self.last_density_grid_shape
        )
        state: dict[str, Array] = {f"density_projection.{name}": value for name, value in density_inspected.items()}
        state.update({f"density_branch.{name}": value for name, value in self.density_branch.Inspect().items()})
        if self.potential is not None:
            potential_projection, potential_branch, _, _ = self.potential
            potential_inspected = Basis_Projection_Inspection(
                potential_projection, DERIVED_POTENTIAL_LABELS, self.last_potential_grid_shape
            )
            state.update({f"potential_projection.{name}": value for name, value in potential_inspected.items()})
            state.update({f"potential_branch.{name}": value for name, value in potential_branch.Inspect().items()})
        state.update(self.parameter_values)
        if self.last_combined_latent is not None:
            state["last_combined_latent"] = self.last_combined_latent
        return state


class MultipleInputOperatorNetwork(NeuralOperator[GridFunction, Coefficients, Representation]):
    """two sensor encoders, a multiplicative product, a shared trunk"""


    def __init__(self, encoder: TwoBranchEncoder, readout: BasisExpansion) -> None:
        super().__init__(encoder, WithoutIntegralLayers(), readout)
        self.branch_encoder = encoder
        self.trunk_readout = readout
        self.last_predicted_field: NDArray[np.float64] | None = None


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> Representation:
        latent = self.encoder(input_function, output_discretization, condition)
        carried = self.composition.Apply(latent, condition)
        produced = self.readout(carried, output_discretization, condition)
        bounded, flattened = Bounded_Field(produced)
        self.last_predicted_field = flattened
        return bounded


    def Inspect(self) -> dict[str, Array]:
        """every part's own arrays, plus the bounded field this member last produced"""
        state = super().Inspect()
        if self.last_predicted_field is not None:
            state["last_predicted_field"] = self.last_predicted_field
        return state


    def Parameter_Values(self) -> dict[str, NDArray[np.float64]]:
        """every part's own arrays under one namespace, ready for the trainer"""
        collected = dict(self.branch_encoder.Parameter_Values())
        collected.update(self.trunk_readout.parameter_values)
        return collected


    def Forward_Coefficients(self, lifted: dict[str, Any], parameter_vectors: Any) -> Any:
        """the two branches' own coefficient slices, combined multiplicatively and split into per-channel trunk rows"""
        # the potential slice arrives already standardized, concatenated that way by the cache that built it
        encoder = self.branch_encoder
        density_vector = parameter_vectors[:, : encoder.density_rank]
        density_latent = encoder.density_branch.network.Forward(
            Sliced_Lifted(lifted, "density_branch."), density_vector
        )
        if encoder.potential is None:
            combined = density_latent
        else:
            _, potential_branch, _, _ = encoder.potential
            potential_end = encoder.density_rank + encoder.potential_rank
            potential_vector = parameter_vectors[:, encoder.density_rank : potential_end]
            potential_latent = potential_branch.network.Forward(
                Sliced_Lifted(lifted, "potential_branch."), potential_vector
            )
            combined = density_latent * potential_latent
        split = combined @ lifted["channel_head_weights"].T + lifted["channel_head_biases"]
        return split.reshape(split.shape[0], CHANNEL_COUNT, encoder.latent_width)


    def Forward_Point_Values(self, lifted: dict[str, Any], parameter_vectors: Any, trunk_features: Any) -> Any:
        """predicted localization values at sampled points, each run reading only its own coefficients and points"""
        coefficients = self.Forward_Coefficients(lifted, parameter_vectors)
        trunk_values = self.trunk_readout.trunk.Forward(lifted, trunk_features)
        raw_values = Sum_Over_Last_Axis(trunk_values[:, :, None, :] * coefficients[:, None, :, :])
        return Bounded_Values(raw_values)


def Two_Branch_Member(
    density_basis: PodBasis,
    potential_basis: PodBasis,
    reference_density: float,
    potential_coefficient_mean: NDArray[np.float64],
    potential_coefficient_scale: NDArray[np.float64],
    seed: int = 0,
) -> MultipleInputOperatorNetwork:
    """the built configuration: two fixed-basis branches combined multiplicatively, read against a shared trunk"""
    density_rank = int(density_basis.modes.shape[0])
    potential_rank = int(potential_basis.modes.shape[0])
    density_projection = BasisProjectionEncoder(density_basis.modes, density_basis.mean)
    density_branch = SensorEncoder((density_rank, BRANCH_HIDDEN_WIDTH, LATENT_WIDTH), seed=seed)
    potential_projection = BasisProjectionEncoder(potential_basis.modes, potential_basis.mean)
    # the potential branch is seeded one past the density branch, so the two draws never share a stream
    potential_branch = SensorEncoder((potential_rank, BRANCH_HIDDEN_WIDTH, LATENT_WIDTH), seed=seed + 1)
    encoder = TwoBranchEncoder(
        density_projection,
        density_branch,
        (potential_projection, potential_branch, potential_coefficient_mean, potential_coefficient_scale),
        reference_density,
        seed=seed + 2,
    )
    # the trunk is seeded two past the branches, so no two draws share a stream
    readout = BasisExpansion(
        LATENT_WIDTH, TRUNK_HIDDEN_WIDTHS, PeriodicCoordinateFeatures(), OUTPUT_CHANNEL_LABELS, seed=seed + 3
    )
    return MultipleInputOperatorNetwork(encoder, readout)


def Density_Alone_Twin(
    density_basis: PodBasis,
    reference_density: float,
    seed: int = 0,
) -> MultipleInputOperatorNetwork:
    """the kill comparator: the potential branch replaced by the multiplicative identity, everything else identical"""
    density_rank = int(density_basis.modes.shape[0])
    density_projection = BasisProjectionEncoder(density_basis.modes, density_basis.mean)
    density_branch = SensorEncoder((density_rank, BRANCH_HIDDEN_WIDTH, LATENT_WIDTH), seed=seed)
    encoder = TwoBranchEncoder(density_projection, density_branch, None, reference_density, seed=seed + 2)
    readout = BasisExpansion(
        LATENT_WIDTH, TRUNK_HIDDEN_WIDTHS, PeriodicCoordinateFeatures(), OUTPUT_CHANNEL_LABELS, seed=seed + 3
    )
    return MultipleInputOperatorNetwork(encoder, readout)
