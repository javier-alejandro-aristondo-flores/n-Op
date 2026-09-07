"""translation-invariant kernels as per-mode weights on the torus spectrum"""

from collections.abc import Callable
from math import prod
from typing import Any

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


class SpectralKernel(Kernel[GridFunction, GridFunction]):
    """complex weights on a truncated centered-mode set, mixing channels per mode"""

    supported_representations = (GridFunction,)


    def __init__(
        self,
        kept_modes: tuple[int, int, int],
        output_channels: int,
        input_channels: int,
        seed: int = 0,
    ) -> None:
        self.kept_modes = kept_modes
        self.output_channels = output_channels
        self.input_channels = input_channels
        # modes run from minus kept to plus kept on every axis
        mode_extents = tuple(2 * kept + 1 for kept in kept_modes)
        generator = np.random.default_rng(seed)
        scale = 1.0 / (input_channels * np.sqrt(float(np.prod(mode_extents))))
        shape = (*mode_extents, output_channels, input_channels)
        # a complex weight is carried as two real arrays, so every engine can differentiate it
        self.parameter_values: dict[str, NDArray[np.float64]] = {
            "mode_weights_real": generator.normal(0.0, scale, size=shape),
            "mode_weights_imaginary": generator.normal(0.0, scale, size=shape),
        }
        self.last_output_values: NDArray[np.float64] | None = None


    def Kept_Mode_Positions(self, extents: tuple[int, ...]) -> list[NDArray[np.int64]]:
        """spectral positions of the kept centered modes on each axis"""
        positions: list[NDArray[np.int64]] = []
        for kept, extent in zip(self.kept_modes, extents):
            modes = np.arange(-kept, kept + 1, dtype=np.int64)
            positions.append(np.mod(modes, extent))
        return positions


    def Forward(self, lifted: dict[str, Any], input_values: Any, output_shape: tuple[int, int, int]) -> Any:
        input_array = np.asarray(input_values, dtype=np.float64)
        spectrum = np.fft.fftn(input_array, axes=(1, 2, 3))
        # gather the kept modes out of the input spectrum
        source_positions = self.Kept_Mode_Positions(input_array.shape[1:])
        channel_index = np.arange(self.input_channels, dtype=np.int64)
        gathered = spectrum[np.ix_(channel_index, *source_positions)]
        weights = lifted["mode_weights_real"] + 1j * lifted["mode_weights_imaginary"]
        # one channel mix per mode, no mode talks to another
        mixed = np.einsum("cxyz,xyzoc->oxyz", gathered, weights)
        # scatter them into the requested grid's spectrum, which may be a different size
        placed = np.zeros((self.output_channels, *output_shape), dtype=np.complex128)
        target_positions = self.Kept_Mode_Positions(output_shape)
        output_channel_index = np.arange(self.output_channels, dtype=np.int64)
        placed[np.ix_(output_channel_index, *target_positions)] = mixed
        # the point-count ratio carries the amplitude across that size change
        scale = prod(output_shape) / prod(input_array.shape[1:])
        return np.real(np.fft.ifftn(placed, axes=(1, 2, 3))) * scale


    def Integrate(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        if not isinstance(output_discretization, GridSpec):
            raise TypeError("the spectral kernel evaluates on grids only")
        produced = np.asarray(
            self.Forward(self.parameter_values, input_function.values, output_discretization.shape),
            dtype=np.float64,
        )
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
        weights = self.parameter_values["mode_weights_real"] + 1j * self.parameter_values["mode_weights_imaginary"]
        # reversing the centered axes pairs every mode with its negative
        mirrored = np.conj(weights[::-1, ::-1, ::-1])
        symmetric = (weights + mirrored) / 2.0
        self.parameter_values["mode_weights_real"] = np.real(symmetric)
        self.parameter_values["mode_weights_imaginary"] = np.imag(symmetric)


    def Dense_Kernel_Function(
        self, cell_volume: float
    ) -> Callable[[NDArray[np.float64], NDArray[np.float64]], NDArray[np.float64]]:
        """the closed-form pair kernel this spectral form integrates"""
        kept_modes = self.kept_modes

        def Pair_Kernel(targets: NDArray[np.float64], sources: NDArray[np.float64]) -> NDArray[np.float64]:
            # enumerated minus kept to plus kept, the order the weights are stored in
            axis_modes = [np.arange(-kept, kept + 1, dtype=np.int64) for kept in kept_modes]
            mode_grids = np.meshgrid(*axis_modes, indexing="ij")
            mode_list = np.stack([grid.reshape(-1) for grid in mode_grids], axis=1)
            weights = (
                self.parameter_values["mode_weights_real"] + 1j * self.parameter_values["mode_weights_imaginary"]
            ).reshape(mode_list.shape[0], self.output_channels, self.input_channels)
            displacement_phase = np.exp(
                2j * np.pi * ((targets[:, None, :] - sources[None, :, :]) @ mode_list.T.astype(np.float64))
            )
            kernel_values = np.einsum("mnk,koc->mnoc", displacement_phase, weights) / cell_volume
            return np.real(kernel_values)

        return Pair_Kernel


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = dict(self.parameter_values)
        real_part = self.parameter_values["mode_weights_real"]
        imaginary_part = self.parameter_values["mode_weights_imaginary"]
        state["mode_magnitudes"] = np.sqrt(real_part**2 + imaginary_part**2)
        # the pair is one complex weight, and its phase is half of what that weight means
        state["mode_phases"] = np.arctan2(imaginary_part, real_part)
        if self.last_output_values is not None:
            state["last_output_values"] = self.last_output_values
        return state
