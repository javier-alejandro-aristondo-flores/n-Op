"""translation-invariant kernels as per-mode weights on the torus spectrum"""

from collections.abc import Callable
from math import prod
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray

from operators.framework import (
    Array,
    Coefficients,
    Discretization,
    GridFunction,
    GridSpec,
    Kernel,
    UniformGridQuadrature,
)
from operators.substrate import (
    GRID_AXES,
    Complex_From_Parts,
    Conjugate,
    Einstein_Summation,
    Exponential,
    Half_Spectrum_Extent,
    Hermitian_Mode_Part,
    Inverse_Real_Fourier_Transform_3d,
    Join_Along_Axis,
    MultilayerPerceptron,
    Precision,
    Real_Fourier_Transform_3d,
    Reciprocal_Rows,
    Reverse_Axes,
    Sliced_Along_Axis,
    Split_Batch_From_Grid,
    Zeros_Beside,
)

type ModeMixing = Literal["full", "separable"]

AXIS_NAMES = ("first_axis", "second_axis", "third_axis")

SEPARABLE_SUBSCRIPTS = ("...cxyz,xoc->...oxyz", "...cxyz,yoc->...oxyz", "...cxyz,zoc->...oxyz")

# the fixed name a composing member writes this kernel's per-mode wavevector feature under
MODE_WAVEVECTOR_FEATURES_KEY = "mode_wavevector_features"

GAIN_NAME_PREFIX = "gain"

GAIN_NETWORK_HIDDEN_WIDTH = 8

# one inverse angstrom squared, so the logarithm below takes a dimensionless argument
WAVEVECTOR_SQUARED_NORM_REFERENCE = 1.0

# keeps the origin mode's feature finite rather than a logarithm of zero
WAVEVECTOR_FEATURE_EPSILON = 1e-3


def Mode_Wavevector_Norms_Squared(
    lattice: NDArray[np.float64], kept_modes: tuple[int, int, int]
) -> NDArray[np.float64]:
    """the physical wavevector magnitude squared at every kept mode, ascending from minus kept to plus kept"""
    reciprocal = Reciprocal_Rows(lattice)
    # the ascending range Gathered_Modes lays its block out in, not the wrapped order a whole axis stores
    axis_modes = [np.arange(-kept, kept + 1, dtype=np.float64) for kept in kept_modes]
    mode_grids = np.meshgrid(*axis_modes, indexing="ij")
    stacked = np.stack(mode_grids, axis=-1)
    wavevectors = stacked @ reciprocal
    return np.asarray(np.sum(wavevectors**2, axis=-1), dtype=np.float64)


def Mode_Wavevector_Features(lattice: NDArray[np.float64], kept_modes: tuple[int, int, int]) -> NDArray[np.float64]:
    """the log-squared-wavevector feature at every kept mode, the gain perceptron's own input"""
    squared_norms = Mode_Wavevector_Norms_Squared(lattice, kept_modes)
    return np.asarray(
        np.log(squared_norms / WAVEVECTOR_SQUARED_NORM_REFERENCE + WAVEVECTOR_FEATURE_EPSILON), dtype=np.float64
    )


class SpectralKernel(Kernel[GridFunction, GridFunction]):
    """complex weights on a truncated centered-mode set, mixing channels per mode"""

    supported_representations = (GridFunction,)


    def __init__(
        self,
        kept_modes: tuple[int, int, int],
        output_channels: int,
        input_channels: int,
        seed: int = 0,
        mode_mixing: ModeMixing = "full",
        working_precision: Precision = "double",
        metric_aware: bool = False,
    ) -> None:
        self.kept_modes = kept_modes
        self.output_channels = output_channels
        self.input_channels = input_channels
        self.mode_mixing: ModeMixing = mode_mixing
        self.working_precision: Precision = working_precision
        self.metric_aware = metric_aware
        # modes run from minus kept to plus kept on every axis
        self.mode_extents = tuple(2 * kept + 1 for kept in kept_modes)
        generator = np.random.default_rng(seed)
        scale = 1.0 / (input_channels * np.sqrt(float(np.prod(self.mode_extents))))
        stored = self.Weight_Shapes()
        # the separable form adds its factors into one weight, so each factor is spread narrower to match
        spread = scale / np.sqrt(float(len(stored)))
        # a complex weight is carried as two real arrays, so every engine can differentiate it
        self.parameter_values: dict[str, NDArray[np.float64]] = {}
        for stem, shape in stored.items():
            self.parameter_values[f"{stem}_real"] = generator.normal(0.0, spread, size=shape)
            self.parameter_values[f"{stem}_imaginary"] = generator.normal(0.0, spread, size=shape)
        self.gain_network: MultilayerPerceptron | None = None
        if metric_aware:
            self.gain_network = MultilayerPerceptron(
                (1, GAIN_NETWORK_HIDDEN_WIDTH, output_channels), name_prefix=GAIN_NAME_PREFIX, seed=seed
            )
            last_layer_index = len(self.gain_network.layer_widths) - 2
            # a zeroed last layer starts every gain at exactly one, so an untrained feature moves nothing
            self.gain_network.parameter_values[f"{GAIN_NAME_PREFIX}_layer_{last_layer_index}_weights"] = np.zeros(
                (output_channels, GAIN_NETWORK_HIDDEN_WIDTH)
            )
            self.gain_network.parameter_values[f"{GAIN_NAME_PREFIX}_layer_{last_layer_index}_biases"] = np.zeros(
                output_channels
            )
            self.parameter_values.update(self.gain_network.parameter_values)
        self.last_output_values: NDArray[np.float64] | None = None
        self.last_mode_gains: NDArray[np.float64] | None = None
        self.last_mode_wavevector_features: NDArray[np.float64] | None = None


    def Weight_Shapes(self) -> dict[str, tuple[int, ...]]:
        """the shape of every stored complex weight, one entry for the full form and three for the separable"""
        channels = (self.output_channels, self.input_channels)
        if self.mode_mixing == "full":
            return {"mode_weights": (*self.mode_extents, *channels)}
        return {
            f"{axis_name}_mode_weights": (extent, *channels)
            for axis_name, extent in zip(AXIS_NAMES, self.mode_extents)
        }


    def Parameter_Count(self) -> int:
        """how many real numbers this kernel stores, the two halves of every complex weight counted apart"""
        return sum(int(value.size) for value in self.parameter_values.values())


    @staticmethod
    def Parameter_Count_For(
        kept_modes: tuple[int, int, int],
        output_channels: int,
        input_channels: int,
        mode_mixing: ModeMixing,
        metric_aware: bool = False,
    ) -> int:
        """the same count without building the weights, so a mode budget can be priced before it is paid"""
        mode_extents = tuple(2 * kept + 1 for kept in kept_modes)
        channel_pairs = output_channels * input_channels
        # two reals to a complex weight, and the separable form stores the axes added rather than multiplied out
        if mode_mixing == "full":
            count = 2 * prod(mode_extents) * channel_pairs
        else:
            count = 2 * sum(mode_extents) * channel_pairs
        if metric_aware:
            gain_network = MultilayerPerceptron(
                (1, GAIN_NETWORK_HIDDEN_WIDTH, output_channels), name_prefix=GAIN_NAME_PREFIX
            )
            count += sum(int(value.size) for value in gain_network.parameter_values.values())
        return count


    def Check_Modes_Fit(self, shape: tuple[int, int, int]) -> None:
        """every kept mode needs its own spectral entry on this grid, its negative included"""
        for kept, extent in zip(self.kept_modes, shape):
            if 2 * kept + 1 > extent:
                raise ValueError(f"modes minus {kept} to plus {kept} need at least {2 * kept + 1} points, not {extent}")


    def Complex_Weight(self, lifted: dict[str, Any], stem: str) -> Any:
        """the stored real pair read back as the one complex weight it stands for"""
        return Complex_From_Parts(lifted[f"{stem}_real"], lifted[f"{stem}_imaginary"])


    def Gathered_Modes(self, half_spectrum: Any, input_shape: tuple[int, int, int]) -> Any:
        """the kept modes of a half spectrum, centered from minus kept to plus kept on all three axes"""
        gathered = half_spectrum
        # a whole spectral axis stores mode minus one at its very end, so centered order is the tail then the head
        for whole_axis, kept, extent in zip(GRID_AXES[:2], self.kept_modes[:2], input_shape[:2]):
            negative = Sliced_Along_Axis(gathered, whole_axis, extent - kept, extent)
            non_negative = Sliced_Along_Axis(gathered, whole_axis, 0, kept + 1)
            gathered = Join_Along_Axis([negative, non_negative], whole_axis)
        kept_last = self.kept_modes[2]
        non_negative = Sliced_Along_Axis(gathered, -1, 0, kept_last + 1)
        # a real field stores no negative mode of the last axis: each is the conjugate of the mode opposite it
        opposite = Reverse_Axes(Sliced_Along_Axis(non_negative, -1, 1, kept_last + 1), GRID_AXES)
        return Join_Along_Axis([Conjugate(opposite), non_negative], -1)


    def Mixed_Channels(self, lifted: dict[str, Any], gathered: Any) -> Any:
        """one channel mix per mode, no mode talking to another"""
        if self.mode_mixing == "full":
            return Einstein_Summation("...cxyz,xyzoc->...oxyz", gathered, self.Complex_Weight(lifted, "mode_weights"))
        mixed = [
            Einstein_Summation(subscripts, gathered, self.Complex_Weight(lifted, f"{axis_name}_mode_weights"))
            for axis_name, subscripts in zip(AXIS_NAMES, SEPARABLE_SUBSCRIPTS)
        ]
        # the factorized form adds one mix per axis, which is the whole mode tensor without ever storing it
        return mixed[0] + mixed[1] + mixed[2]


    def Gained_Modes(self, lifted: dict[str, Any], mixed: Any) -> Any:
        """the mixed modes scaled by a learned per-mode gain, unchanged when no feature was handed in"""
        if self.gain_network is None or MODE_WAVEVECTOR_FEATURES_KEY not in lifted:
            return mixed
        feature = lifted[MODE_WAVEVECTOR_FEATURES_KEY]
        gain = Exponential(self.gain_network.Forward(lifted, feature[..., None]))
        # the gain is real and even in the mode, so applying it before or after Hermitian averaging agrees
        return Einstein_Summation("...oxyz,xyzo->...oxyz", mixed, gain)


    def Placed_Modes(self, mixed: Any, output_shape: tuple[int, int, int]) -> Any:
        """the mixed modes written into the half spectrum of the requested grid, every other mode zero"""
        kept_last = self.kept_modes[2]
        # only the non-negative modes of the last axis are stored, the rest being implied by conjugate symmetry
        placed = Sliced_Along_Axis(mixed, -1, kept_last, 2 * kept_last + 1)
        filler_extent = Half_Spectrum_Extent(output_shape[2]) - (kept_last + 1)
        if filler_extent > 0:
            placed = Join_Along_Axis([placed, Zeros_Beside(placed, (*placed.shape[:-1], filler_extent))], -1)
        for whole_axis, kept, extent in zip(GRID_AXES[:2], self.kept_modes[:2], output_shape[:2]):
            non_negative = Sliced_Along_Axis(placed, whole_axis, kept, 2 * kept + 1)
            negative = Sliced_Along_Axis(placed, whole_axis, 0, kept)
            pieces = [non_negative]
            middle_extent = extent - (2 * kept + 1)
            if middle_extent > 0:
                middle_shape = list(placed.shape)
                middle_shape[whole_axis] = middle_extent
                pieces.append(Zeros_Beside(placed, tuple(middle_shape)))
            pieces.append(negative)
            placed = Join_Along_Axis(pieces, whole_axis)
        return placed


    def Forward(self, lifted: dict[str, Any], input_values: Any, output_shape: tuple[int, int, int]) -> Any:
        _, input_shape = Split_Batch_From_Grid(input_values)
        self.Check_Modes_Fit(input_shape)
        self.Check_Modes_Fit(output_shape)
        half_spectrum = Real_Fourier_Transform_3d(input_values, self.working_precision)
        mixed = self.Mixed_Channels(lifted, self.Gathered_Modes(half_spectrum, input_shape))
        gained = self.Gained_Modes(lifted, mixed)
        # the inverse real transform reads one of each conjugate pair, so only what a real field carries is placed
        placed = self.Placed_Modes(Hermitian_Mode_Part(gained, GRID_AXES), output_shape)
        produced = Inverse_Real_Fourier_Transform_3d(placed, output_shape, self.working_precision)
        # the point-count ratio carries the amplitude across that size change
        return produced * (prod(output_shape) / prod(input_shape))


    def Integrate(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        if not isinstance(output_discretization, GridSpec):
            raise TypeError("the spectral kernel evaluates on grids only")
        field = np.asarray(input_function.values, dtype=np.float64)
        lifted = self.parameter_values
        if self.metric_aware and self.gain_network is not None:
            lattice = np.asarray(input_function.domain.lattice, dtype=np.float64)
            feature = Mode_Wavevector_Features(lattice, self.kept_modes)
            lifted = {**self.parameter_values, MODE_WAVEVECTOR_FEATURES_KEY: feature}
            self.last_mode_wavevector_features = feature
            raw_gain = self.gain_network.Forward(self.parameter_values, feature[..., None])
            self.last_mode_gains = np.asarray(Exponential(raw_gain), dtype=np.float64)
        produced = np.asarray(self.Forward(lifted, field, output_discretization.shape), dtype=np.float64)
        self.last_output_values = produced
        quadrature = input_function.quadrature
        output_labels = tuple(f"channel_{output_channel}" for output_channel in range(self.output_channels))
        return GridFunction(
            values=produced,
            channel_labels=output_labels,
            domain=input_function.domain,
            # the cell is unchanged, only how many points sample it
            quadrature=UniformGridQuadrature(quadrature.cell_volume, int(np.prod(output_discretization.shape))),
        )


    def Hermitian_Symmetrize(self) -> None:
        """conjugate mode symmetry, which makes the kernel and its dense form exactly real"""
        for stem, shape in self.Weight_Shapes().items():
            # every axis but the trailing output and input channel pair is a mode axis to be paired with its negative
            mode_axes = tuple(range(len(shape) - 2))
            symmetric = Hermitian_Mode_Part(self.Complex_Weight(self.parameter_values, stem), mode_axes)
            # a real view would hold the whole complex temporary alive, so each half is stored as its own array
            self.parameter_values[f"{stem}_real"] = np.ascontiguousarray(np.real(symmetric))
            self.parameter_values[f"{stem}_imaginary"] = np.ascontiguousarray(np.imag(symmetric))


    def Assembled_Mode_Weights(self) -> NDArray[np.complex128]:
        """the whole centered mode tensor this kernel acts by, assembled even when it is stored per axis"""
        if self.mode_mixing == "full":
            return np.asarray(self.Complex_Weight(self.parameter_values, "mode_weights"), dtype=np.complex128)
        spread: list[NDArray[np.complex128]] = []
        for spread_axis, axis_name in enumerate(AXIS_NAMES):
            factor = self.Complex_Weight(self.parameter_values, f"{axis_name}_mode_weights")
            # each factor knows one mode axis and is flat along the other two, which is what factorized means
            broadcast = [1, 1, 1, self.output_channels, self.input_channels]
            broadcast[spread_axis] = self.mode_extents[spread_axis]
            spread.append(np.asarray(factor, dtype=np.complex128).reshape(broadcast))
        return spread[0] + spread[1] + spread[2]


    def Dense_Kernel_Function(
        self, cell_volume: float, lattice: NDArray[np.float64] | None = None
    ) -> Callable[[NDArray[np.float64], NDArray[np.float64]], NDArray[np.float64]]:
        """the closed-form pair kernel this spectral form integrates, its gain folded in when metric-aware"""
        if self.metric_aware and lattice is None:
            raise ValueError("a metric-aware kernel's dense form needs the lattice its gain is a function of")
        kept_modes = self.kept_modes
        gain_network = self.gain_network
        metric_aware = self.metric_aware
        parameter_values = self.parameter_values
        output_channels = self.output_channels
        input_channels = self.input_channels

        def Pair_Kernel(targets: NDArray[np.float64], sources: NDArray[np.float64]) -> NDArray[np.float64]:
            # enumerated minus kept to plus kept, the order the weights are stored in
            axis_modes = [np.arange(-kept, kept + 1, dtype=np.int64) for kept in kept_modes]
            mode_grids = np.meshgrid(*axis_modes, indexing="ij")
            mode_list = np.stack([grid.reshape(-1) for grid in mode_grids], axis=1)
            weights = self.Assembled_Mode_Weights().reshape(mode_list.shape[0], output_channels, input_channels)
            if metric_aware and gain_network is not None and lattice is not None:
                feature = Mode_Wavevector_Features(lattice, kept_modes).reshape(-1, 1)
                gain = np.asarray(Exponential(gain_network.Forward(parameter_values, feature)), dtype=np.float64)
                # the gain depends on the output channel alone, so it scales every input channel's weight alike
                weights = weights * gain[:, :, None]
            displacement_phase = np.exp(
                2j * np.pi * ((targets[:, None, :] - sources[None, :, :]) @ mode_list.T.astype(np.float64))
            )
            kernel_values = np.einsum("mnk,koc->mnoc", displacement_phase, weights) / cell_volume
            return np.real(kernel_values)

        return Pair_Kernel


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = dict(self.parameter_values)
        for stem in self.Weight_Shapes():
            real_part = self.parameter_values[f"{stem}_real"]
            imaginary_part = self.parameter_values[f"{stem}_imaginary"]
            quantity = stem.removesuffix("_weights")
            state[f"{quantity}_magnitudes"] = np.sqrt(real_part**2 + imaginary_part**2)
            # the pair is one complex weight, and its phase is half of what that weight means
            state[f"{quantity}_phases"] = np.arctan2(imaginary_part, real_part)
        if self.last_output_values is not None:
            state["last_output_values"] = self.last_output_values
        if self.last_mode_gains is not None:
            state["last_mode_gains"] = self.last_mode_gains
        if self.last_mode_wavevector_features is not None:
            state["last_mode_wavevector_features"] = self.last_mode_wavevector_features
        return state
