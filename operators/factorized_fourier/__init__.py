"""charge density to electron localization, by factorized Fourier convolution"""

from collections.abc import Sequence
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray

from operators.compositions import ExplicitStack, FixedPoint, Spectral_Resampled, WeightTied
from operators.encoders import PointwiseLift
from operators.framework import (
    Array,
    Coefficients,
    Discretization,
    GridFunction,
    GridSpec,
    Layer,
    NeuralOperator,
    UniformGridQuadrature,
)
from operators.kernels import SpectralKernel
from operators.readouts import PointwiseProjection
from operators.substrate import Concatenate_Channels, Zeros_Beside

type FourierComposition = ExplicitStack | WeightTied | FixedPoint

type FactorizedFourierConfiguration = Literal["explicit", "weight_tied", "fixed_point"]

GRAM_CHANNEL_COUNT = 6

INPUT_CHANNEL_COUNT = 2 + GRAM_CHANNEL_COUNT

LOCALIZATION_CHANNEL_LABELS = ("electron_localization_up", "electron_localization_down")

# a positive floor under a training-block mean that would otherwise divide by zero
REFERENCE_DENSITY_FLOOR = 1e-12


def Gram_Six(lattice: NDArray[np.float64]) -> NDArray[np.float64]:
    """the six independent entries of the lattice's own Gram matrix, upper triangle in row order"""
    gram = lattice @ lattice.T
    return np.asarray([gram[0, 0], gram[0, 1], gram[0, 2], gram[1, 1], gram[1, 2], gram[2, 2]], dtype=np.float64)


def Gram_Statistics(lattices: Sequence[NDArray[np.float64]]) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """a training block's own mean and spread of the six Gram entries, spread guarded away from zero"""
    stacked = np.stack([Gram_Six(np.asarray(lattice, dtype=np.float64)) for lattice in lattices])
    mean = stacked.mean(axis=0)
    scale = stacked.std(axis=0)
    # a cell parameter that never varies across the block would otherwise divide by zero
    scale[scale == 0.0] = 1.0
    return mean, scale


def Standardized_Gram(
    raw_six: NDArray[np.float64], gram_mean: NDArray[np.float64], gram_scale: NDArray[np.float64]
) -> NDArray[np.float64]:
    """one run's six Gram entries, centered and scaled by the training block's own statistics"""
    return (raw_six - gram_mean) / gram_scale


def Spin_Channels(
    density: NDArray[np.float64], magnetization: NDArray[np.float64]
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """the up and down spin densities, half the sum and half the difference, clipped where the corpus goes negative"""
    # a quarter of defect_set runs carry a voxel where the stored magnetization locally exceeds the density
    # a spin-resolved density has no negative meaning, and log-compression cannot take a negative argument
    return np.maximum((density + magnetization) / 2.0, 0.0), np.maximum((density - magnetization) / 2.0, 0.0)


def Log_Compressed_Channels(
    density: NDArray[np.float64], magnetization: NDArray[np.float64], reference_density: float
) -> NDArray[np.float64]:
    """the two spin densities, each mapped through the dynamic-range compression"""
    spin_up, spin_down = Spin_Channels(density, magnetization)
    return np.stack([np.log1p(spin_up / reference_density), np.log1p(spin_down / reference_density)])


def Reference_Density(
    density_fields: Sequence[NDArray[np.float64]], magnetization_fields: Sequence[NDArray[np.float64]]
) -> float:
    """a training block's own mean spin density, the scale the log compression is centered on"""
    total = 0.0
    counted_entries = 0
    for density, magnetization in zip(density_fields, magnetization_fields):
        spin_up, spin_down = Spin_Channels(density, magnetization)
        total += float(spin_up.sum()) + float(spin_down.sum())
        counted_entries += spin_up.size + spin_down.size
    return max(total / counted_entries, REFERENCE_DENSITY_FLOOR)


class FactorizedFourier(NeuralOperator[GridFunction, GridFunction, GridFunction]):
    """pointwise lift, factorized spectral layers, bounded head"""


    def __init__(
        self,
        encoder: PointwiseLift,
        composition: FourierComposition,
        readout: PointwiseProjection,
        reference_density: float,
        gram_mean: NDArray[np.float64],
        gram_scale: NDArray[np.float64],
        processing_shape: tuple[int, int, int] = (40, 40, 40),
    ) -> None:
        super().__init__(encoder, composition, readout)
        self.lift = encoder
        self.spectral_stack = composition
        self.projection = readout
        self.reference_density = reference_density
        self.gram_mean = gram_mean
        self.gram_scale = gram_scale
        self.processing_shape = processing_shape
        self.last_gram_vector: NDArray[np.float64] | None = None
        self.last_predicted_values: NDArray[np.float64] | None = None
        self.last_fixed_point_iterations: int | None = None
        self.last_fixed_point_residual: float | None = None
        self.last_fixed_point_cap_was_hit: bool | None = None
        self.last_fixed_point_residual_history: NDArray[np.float64] | None = None


    def Parameter_Values(self) -> dict[str, NDArray[np.float64]]:
        """every part's own arrays under one namespace, ready for the trainer"""
        collected = dict(self.lift.parameter_values)
        collected.update(self.spectral_stack.Parameter_Values())
        collected.update(self.projection.parameter_values)
        return collected


    def Forward_Field(
        self,
        lifted: dict[str, Any],
        log_density_values: Any,
        gram_vector: Any,
        target_shape: tuple[int, int, int] | None = None,
    ) -> Any:
        """the whole lifted path, from fine-grid log-compressed channels to the bounded localization field"""
        resolved_shape = self.processing_shape if target_shape is None else target_shape
        # a pointwise affine lift commutes exactly with spectral truncation, so truncating first costs an eighth as much
        coarse_density = Spectral_Resampled(log_density_values, resolved_shape)
        gram_field = gram_vector.reshape(GRAM_CHANNEL_COUNT, 1, 1, 1) + Zeros_Beside(
            coarse_density, (GRAM_CHANNEL_COUNT, *resolved_shape)
        )
        combined = Concatenate_Channels([coarse_density, gram_field])
        hidden = self.lift.Forward(lifted, combined)
        # a bare forward call would drop the solve, so resolved is used directly to capture it for inspection
        if isinstance(self.spectral_stack, FixedPoint):
            carried, solved = self.spectral_stack.Resolved(lifted, hidden)
            self.last_fixed_point_iterations = solved.iterations_taken
            self.last_fixed_point_residual = solved.final_residual
            self.last_fixed_point_cap_was_hit = solved.cap_was_hit
            self.last_fixed_point_residual_history = np.asarray(solved.residual_norm_history, dtype=np.float64)
        else:
            carried = self.spectral_stack.Forward(lifted, hidden)
        return self.projection.Forward(lifted, carried)


    def Input_Channels(self, input_function: GridFunction) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """the log-compressed spin channels and the standardized Gram vector this run's own lattice carries"""
        values = np.asarray(input_function.values, dtype=np.float64)
        log_density_values = Log_Compressed_Channels(values[0], values[1], self.reference_density)
        raw_gram = Gram_Six(np.asarray(input_function.domain.lattice, dtype=np.float64))
        gram_vector = Standardized_Gram(raw_gram, self.gram_mean, self.gram_scale)
        return log_density_values, gram_vector


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        if not isinstance(output_discretization, GridSpec):
            raise TypeError("the factorized Fourier operator evaluates on grids only")
        log_density_values, gram_vector = self.Input_Channels(input_function)
        produced = np.asarray(
            self.Forward_Field(
                self.Parameter_Values(), log_density_values, gram_vector, output_discretization.shape
            ),
            dtype=np.float64,
        )
        self.last_gram_vector = gram_vector
        self.last_predicted_values = produced
        point_count = output_discretization.shape[0] * output_discretization.shape[1] * output_discretization.shape[2]
        quadrature = UniformGridQuadrature(input_function.quadrature.cell_volume, point_count)
        return GridFunction(produced, LOCALIZATION_CHANNEL_LABELS, input_function.domain, quadrature)


    def Inspect(self) -> dict[str, Array]:
        """every part's own arrays, plus the input transform constants and the last predicted field"""
        state = super().Inspect()
        state["reference_density"] = np.asarray(self.reference_density)
        state["gram_standardization_mean"] = self.gram_mean
        state["gram_standardization_scale"] = self.gram_scale
        if self.last_gram_vector is not None:
            state["last_gram_vector"] = self.last_gram_vector
        if self.last_predicted_values is not None:
            state["last_predicted_values"] = self.last_predicted_values
        if self.last_fixed_point_iterations is not None:
            state["last_fixed_point_iterations_taken"] = np.asarray(self.last_fixed_point_iterations)
        if self.last_fixed_point_residual is not None:
            state["last_fixed_point_final_residual"] = np.asarray(self.last_fixed_point_residual)
        if self.last_fixed_point_cap_was_hit is not None:
            state["last_fixed_point_cap_was_hit"] = np.asarray(self.last_fixed_point_cap_was_hit)
        if self.last_fixed_point_residual_history is not None:
            state["last_fixed_point_residual_history"] = self.last_fixed_point_residual_history
        return state


def Shared_Member_Layer(hidden_channels: int, kept_modes: tuple[int, int, int], seed: int) -> Layer[GridFunction]:
    """the one kernel-plus-local-linear layer the tied and fixed-point rungs apply repeatedly"""
    # no residual here, unlike the explicit stack's own layers: repeated or iterated application of x plus a
    # correction drifts rather than contracts, since the fixed point would then need the correction itself to vanish
    kernel = SpectralKernel(
        kept_modes=kept_modes,
        output_channels=hidden_channels,
        input_channels=hidden_channels,
        seed=seed,
        mode_mixing="separable",
    )
    local_linear = PointwiseLift(hidden_channels, hidden_channels, seed=seed + 1)
    return Layer(kernel=kernel, local_linear=local_linear, residual=False)


def Factorized_Fourier_Network(
    hidden_channels: int,
    kept_modes: tuple[int, int, int],
    layer_count: int,
    reference_density: float,
    gram_mean: NDArray[np.float64],
    gram_scale: NDArray[np.float64],
    processing_shape: tuple[int, int, int] = (40, 40, 40),
    seed: int = 0,
    configuration: FactorizedFourierConfiguration = "explicit",
    fixed_point_phantom_depth: int = 3,
) -> FactorizedFourier:
    """the flagship configuration: pointwise lift, a composition of factorized spectral layers, the bounded head"""
    lift = PointwiseLift(hidden_channels, INPUT_CHANNEL_COUNT, seed=seed)
    stack: FourierComposition
    if configuration == "explicit":
        layers = tuple(
            Layer(
                kernel=SpectralKernel(
                    kept_modes=kept_modes,
                    output_channels=hidden_channels,
                    input_channels=hidden_channels,
                    seed=seed + 2 * layer_index + 1,
                    mode_mixing="separable",
                ),
                local_linear=PointwiseLift(hidden_channels, hidden_channels, seed=seed + 2 * layer_index + 2),
                residual=True,
            )
            for layer_index in range(layer_count)
        )
        stack = ExplicitStack(layers)
    elif configuration == "weight_tied":
        stack = WeightTied(Shared_Member_Layer(hidden_channels, kept_modes, seed + 1), depth=layer_count)
    elif configuration == "fixed_point":
        stack = FixedPoint(
            Shared_Member_Layer(hidden_channels, kept_modes, seed + 1),
            backward="phantom",
            phantom_depth=fixed_point_phantom_depth,
        )
    else:
        raise ValueError(f"{configuration} is not one of the member's configurations")
    projection = PointwiseProjection(
        len(LOCALIZATION_CHANNEL_LABELS), hidden_channels, bounded=True, seed=seed + 2 * layer_count + 1
    )
    return FactorizedFourier(lift, stack, projection, reference_density, gram_mean, gram_scale, processing_shape)
