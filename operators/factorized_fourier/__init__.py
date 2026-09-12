"""charge density to electron localization or local potential, by factorized Fourier convolution"""

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
from operators.kernels.spectral import MODE_WAVEVECTOR_FEATURES_KEY, Mode_Wavevector_Features
from operators.readouts import PointwiseProjection
from operators.substrate import Concatenate_Channels, Zeros_Beside
from operators.wrappers import Conserving

type FourierComposition = ExplicitStack | WeightTied | FixedPoint

type FactorizedFourierConfiguration = Literal["explicit", "explicit_matched", "weight_tied", "fixed_point"]

type FactorizedFourierTask = Literal["localization", "potential"]

GRAM_CHANNEL_COUNT = 6

INPUT_CHANNEL_COUNT = 2 + GRAM_CHANNEL_COUNT

LOCALIZATION_CHANNEL_LABELS = ("electron_localization_up", "electron_localization_down")

POTENTIAL_CHANNEL_LABELS = ("local_potential_up", "local_potential_down")

# a positive floor under a training-block mean that would otherwise divide by zero
REFERENCE_DENSITY_FLOOR = 1e-12

# the fine grid every run in the cubic block shares; the potential task's target lives here, the localization
# field's does not, which is the one place the two tasks' own output shape parts company
FINE_SHAPE = (80, 80, 80)


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


def Combined_Coarse_Input(log_density_values: Any, gram_vector: Any, target_shape: tuple[int, int, int]) -> Any:
    """the eight-channel coarse input the lift reads, built once from the fine-grid channels and the gram vector"""
    # a pointwise affine lift commutes exactly with spectral truncation, so truncating first costs an eighth as much
    coarse_density = Spectral_Resampled(log_density_values, target_shape)
    gram_field = gram_vector.reshape(GRAM_CHANNEL_COUNT, 1, 1, 1) + Zeros_Beside(
        coarse_density, (GRAM_CHANNEL_COUNT, *target_shape)
    )
    return Concatenate_Channels([coarse_density, gram_field])


def Layer_Prefixes(composition: FourierComposition) -> tuple[str, ...]:
    """every layer-scoped prefix a composition's own kernels answer to, for injecting a shared lifted constant"""
    if isinstance(composition, ExplicitStack):
        return tuple(f"layer_{layer_index}.kernel." for layer_index in range(len(composition.layers)))
    return ("kernel.",)


class FactorizedFourier(NeuralOperator[GridFunction, GridFunction, GridFunction]):
    """pointwise lift, factorized spectral layers, a task-shaped head"""


    def __init__(
        self,
        encoder: PointwiseLift,
        composition: FourierComposition,
        readout: PointwiseProjection,
        reference_density: float,
        gram_mean: NDArray[np.float64],
        gram_scale: NDArray[np.float64],
        processing_shape: tuple[int, int, int] = (40, 40, 40),
        task: FactorizedFourierTask = "localization",
        kept_modes: tuple[int, int, int] | None = None,
        metric_aware: bool = False,
        target_scale: float = 1.0,
    ) -> None:
        super().__init__(encoder, composition, readout)
        self.lift = encoder
        self.spectral_stack = composition
        self.projection = readout
        self.reference_density = reference_density
        self.gram_mean = gram_mean
        self.gram_scale = gram_scale
        self.processing_shape = processing_shape
        self.task: FactorizedFourierTask = task
        self.kept_modes = kept_modes
        self.metric_aware = metric_aware
        self.target_scale = target_scale
        # the whole-field conservation law: each spin's uniform mode pinned to zero, the potential task's own gauge
        self.conservation = Conserving(inner=self, law="zero_mean") if task == "potential" else None
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


    def Forward_From_Coarse_Input(
        self, lifted: dict[str, Any], combined_coarse_input: Any, mode_wavevector_features: Any | None = None
    ) -> Any:
        """the lifted path onward from the eight-channel coarse input, for a caller that has already built it"""
        layer_lifted = lifted
        if mode_wavevector_features is not None:
            layer_lifted = dict(lifted)
            for prefix in Layer_Prefixes(self.spectral_stack):
                layer_lifted[f"{prefix}{MODE_WAVEVECTOR_FEATURES_KEY}"] = mode_wavevector_features
        hidden = self.lift.Forward(lifted, combined_coarse_input)
        # a bare forward call would drop the solve, so resolved is used directly to capture it for inspection
        if isinstance(self.spectral_stack, FixedPoint):
            carried, solved = self.spectral_stack.Resolved(layer_lifted, hidden)
            self.last_fixed_point_iterations = solved.iterations_taken
            self.last_fixed_point_residual = solved.final_residual
            self.last_fixed_point_cap_was_hit = solved.cap_was_hit
            self.last_fixed_point_residual_history = np.asarray(solved.residual_norm_history, dtype=np.float64)
        else:
            carried = self.spectral_stack.Forward(layer_lifted, hidden)
        return self.projection.Forward(lifted, carried)


    def Forward_Field(
        self,
        lifted: dict[str, Any],
        log_density_values: Any,
        gram_vector: Any,
        target_shape: tuple[int, int, int] | None = None,
        mode_wavevector_features: Any | None = None,
        output_shape: tuple[int, int, int] | None = None,
    ) -> Any:
        """the whole lifted path, coarse throughout; the potential task resamples to the fine shape and pins the mean"""
        resolved_shape = self.processing_shape if target_shape is None else target_shape
        combined = Combined_Coarse_Input(log_density_values, gram_vector, resolved_shape)
        produced = self.Forward_From_Coarse_Input(lifted, combined, mode_wavevector_features)
        if self.task == "potential":
            resolved_output_shape = FINE_SHAPE if output_shape is None else output_shape
            produced = Spectral_Resampled(produced, resolved_output_shape)
            if self.conservation is None:
                raise ValueError("the potential task always carries its own conservation wrapper")
            produced = self.conservation.Forward(produced, weight_each=1.0)
        return produced


    def Input_Channels(self, input_function: GridFunction) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """the log-compressed spin channels and the standardized Gram vector this run's own lattice carries"""
        values = np.asarray(input_function.values, dtype=np.float64)
        log_density_values = Log_Compressed_Channels(values[0], values[1], self.reference_density)
        raw_gram = Gram_Six(np.asarray(input_function.domain.lattice, dtype=np.float64))
        gram_vector = Standardized_Gram(raw_gram, self.gram_mean, self.gram_scale)
        return log_density_values, gram_vector


    def Mode_Wavevector_Features_For(self, input_function: GridFunction) -> NDArray[np.float64] | None:
        """this run's own per-mode metric feature, or nothing when the member is not metric-aware"""
        if not self.metric_aware or self.kept_modes is None:
            return None
        lattice = np.asarray(input_function.domain.lattice, dtype=np.float64)
        return Mode_Wavevector_Features(lattice, self.kept_modes)


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        if not isinstance(output_discretization, GridSpec):
            raise TypeError("the factorized Fourier operator evaluates on grids only")
        log_density_values, gram_vector = self.Input_Channels(input_function)
        mode_wavevector_features = self.Mode_Wavevector_Features_For(input_function)
        if self.task == "potential":
            # the trunk always thinks at its own coarse shape; only the final resample answers the requested grid
            produced = np.asarray(
                self.Forward_Field(
                    self.Parameter_Values(),
                    log_density_values,
                    gram_vector,
                    target_shape=self.processing_shape,
                    mode_wavevector_features=mode_wavevector_features,
                    output_shape=output_discretization.shape,
                ),
                dtype=np.float64,
            )
            produced = produced * self.target_scale
        else:
            produced = np.asarray(
                self.Forward_Field(
                    self.Parameter_Values(),
                    log_density_values,
                    gram_vector,
                    target_shape=output_discretization.shape,
                    mode_wavevector_features=mode_wavevector_features,
                ),
                dtype=np.float64,
            )
        self.last_gram_vector = gram_vector
        self.last_predicted_values = produced
        point_count = produced.shape[1] * produced.shape[2] * produced.shape[3]
        quadrature = UniformGridQuadrature(input_function.quadrature.cell_volume, point_count)
        channel_labels = POTENTIAL_CHANNEL_LABELS if self.task == "potential" else LOCALIZATION_CHANNEL_LABELS
        return GridFunction(produced, channel_labels, input_function.domain, quadrature)


    def Inspect(self) -> dict[str, Array]:
        """every part's own arrays, plus the input transform constants and the last predicted field"""
        state = super().Inspect()
        state["reference_density"] = np.asarray(self.reference_density)
        state["gram_standardization_mean"] = self.gram_mean
        state["gram_standardization_scale"] = self.gram_scale
        if self.task == "potential":
            state["target_scale"] = np.asarray(self.target_scale)
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


def Shared_Member_Layer(
    hidden_channels: int, kept_modes: tuple[int, int, int], seed: int, metric_aware: bool = False
) -> Layer[GridFunction]:
    """the one kernel-plus-local-linear layer the tied and fixed-point rungs apply repeatedly"""
    # no residual here, unlike the explicit stack's own layers: repeated or iterated application of x plus a
    # correction drifts rather than contracts, since the fixed point would then need the correction itself to vanish
    kernel = SpectralKernel(
        kept_modes=kept_modes,
        output_channels=hidden_channels,
        input_channels=hidden_channels,
        seed=seed,
        mode_mixing="separable",
        metric_aware=metric_aware,
    )
    local_linear = PointwiseLift(hidden_channels, hidden_channels, seed=seed + 1)
    return Layer(kernel=kernel, local_linear=local_linear, residual=False)


def Explicit_Layers(
    hidden_channels: int, kept_modes: tuple[int, int, int], layer_count: int, seed: int, metric_aware: bool
) -> tuple[Layer[GridFunction], ...]:
    """the explicit stack's own layers, one spectral kernel and one local linear term each, residual on"""
    return tuple(
        Layer(
            kernel=SpectralKernel(
                kept_modes=kept_modes,
                output_channels=hidden_channels,
                input_channels=hidden_channels,
                seed=seed + 2 * layer_index + 1,
                mode_mixing="separable",
                metric_aware=metric_aware,
            ),
            local_linear=PointwiseLift(hidden_channels, hidden_channels, seed=seed + 2 * layer_index + 2),
            residual=True,
        )
        for layer_index in range(layer_count)
    )


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
    task: FactorizedFourierTask = "localization",
    target_scale: float = 1.0,
) -> FactorizedFourier:
    """the flagship configuration: pointwise lift, a composition of factorized spectral layers, a task-shaped head"""
    # localization stays metric-blind, exactly as briefed; the potential task is the metric-aware kernel's own reason
    metric_aware = task == "potential"
    lift = PointwiseLift(hidden_channels, INPUT_CHANNEL_COUNT, seed=seed)
    stack: FourierComposition
    if configuration == "explicit":
        stack = ExplicitStack(Explicit_Layers(hidden_channels, kept_modes, layer_count, seed, metric_aware))
    elif configuration == "explicit_matched":
        # the matched-params comparator: one explicit layer at this width, carrying exactly the tied block's own count
        stack = ExplicitStack(Explicit_Layers(hidden_channels, kept_modes, 1, seed, metric_aware))
    elif configuration == "weight_tied":
        stack = WeightTied(
            Shared_Member_Layer(hidden_channels, kept_modes, seed + 1, metric_aware), depth=layer_count
        )
    elif configuration == "fixed_point":
        stack = FixedPoint(
            Shared_Member_Layer(hidden_channels, kept_modes, seed + 1, metric_aware),
            backward="phantom",
            phantom_depth=fixed_point_phantom_depth,
        )
    else:
        raise ValueError(f"{configuration} is not one of the member's configurations")
    channel_labels = POTENTIAL_CHANNEL_LABELS if task == "potential" else LOCALIZATION_CHANNEL_LABELS
    projection = PointwiseProjection(
        len(channel_labels), hidden_channels, bounded=(task == "localization"), seed=seed + 2 * layer_count + 1
    )
    return FactorizedFourier(
        lift,
        stack,
        projection,
        reference_density,
        gram_mean,
        gram_scale,
        processing_shape,
        task=task,
        kept_modes=kept_modes,
        metric_aware=metric_aware,
        target_scale=target_scale,
    )
