"""the grid parametrization, weights tabulated at whole-voxel offsets and summed around the torus"""

from collections.abc import Callable
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
)
from operators.kernels.compact_support.geometry import Grid_Offsets, Voxel_Indices
from operators.substrate import Contract_Channel_Axis, Roll_Along_Axes


class TabulatedStencilKernel(Kernel[GridFunction, GridFunction]):
    """a learned channel-mixing block at every whole-voxel offset of a small box"""

    supported_representations = (GridFunction,)


    def __init__(
        self,
        half_widths: tuple[int, int, int],
        output_channels: int,
        input_channels: int,
        seed: int = 0,
    ) -> None:
        self.half_widths = half_widths
        self.output_channels = output_channels
        self.input_channels = input_channels
        # offsets run minus the half-width to plus it on every axis
        offset_extents = tuple(2 * half_width + 1 for half_width in half_widths)
        generator = np.random.default_rng(seed)
        scale = 1.0 / (input_channels * np.sqrt(float(np.prod(offset_extents))))
        self.parameter_values: dict[str, NDArray[np.float64]] = {
            "stencil_weights": generator.normal(
                0.0, scale, size=(*offset_extents, output_channels, input_channels)
            )
        }
        self.last_output_values: NDArray[np.float64] | None = None


    def Offsets(self) -> NDArray[np.int64]:
        """every whole-voxel offset the stencil holds, in the order its weights are stored"""
        return Grid_Offsets(self.half_widths)


    def Block_At(self, weights: Any, offset: NDArray[np.int64]) -> Any:
        """the channel-mixing block stored for one whole-voxel offset"""
        # the box is stored from zero, so an offset reaches its block shifted by the half-width
        return weights[
            int(offset[0]) + self.half_widths[0],
            int(offset[1]) + self.half_widths[1],
            int(offset[2]) + self.half_widths[2],
        ]


    def Forward(self, lifted: dict[str, Any], input_values: Any, output_shape: tuple[int, int, int]) -> Any:
        spatial_shape = tuple(int(extent) for extent in input_values.shape[1:])
        if output_shape != spatial_shape:
            raise ValueError("a tabulated stencil evaluates on the grid it was tabulated for, not another one")
        weights = lifted["stencil_weights"]
        produced: Any = None
        for offset in self.Offsets():
            shift = (int(offset[0]), int(offset[1]), int(offset[2]))
            # rolling forward by the offset brings the source voxel that offset names onto the target
            shifted = Roll_Along_Axes(input_values, shift, (1, 2, 3))
            contribution = Contract_Channel_Axis(self.Block_At(weights, offset), shifted)
            produced = contribution if produced is None else produced + contribution
        return produced


    def Integrate(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        if not isinstance(output_discretization, GridSpec):
            raise TypeError("the tabulated stencil evaluates on grids only")
        values = np.asarray(input_function.values, dtype=np.float64)
        produced = np.asarray(
            self.Forward(self.parameter_values, values, output_discretization.shape), dtype=np.float64
        )
        self.last_output_values = produced
        output_labels = tuple(f"channel_{output_channel}" for output_channel in range(self.output_channels))
        return GridFunction(
            values=produced,
            channel_labels=output_labels,
            domain=input_function.domain,
            quadrature=input_function.quadrature,
        )


    def Dense_Kernel_Function(
        self, shape: tuple[int, int, int], quadrature_weight: float
    ) -> Callable[[NDArray[np.float64], NDArray[np.float64]], NDArray[np.float64]]:
        """the closed-form pair kernel this shift and accumulate integrates"""
        extents = np.asarray(shape, dtype=np.int64)

        def Pair_Kernel(targets: NDArray[np.float64], sources: NDArray[np.float64]) -> NDArray[np.float64]:
            target_voxels = Voxel_Indices(targets, shape)
            source_voxels = Voxel_Indices(sources, shape)
            # a pair is reached by every stencil offset congruent to its voxel difference
            difference = np.mod(target_voxels[:, None, :] - source_voxels[None, :, :], extents)
            values = np.zeros(
                (targets.shape[0], sources.shape[0], self.output_channels, self.input_channels)
            )
            weights = self.parameter_values["stencil_weights"]
            for offset in self.Offsets():
                matched = np.all(difference == np.mod(offset, extents), axis=-1)
                # the stencil sum carries no quadrature, so the pair kernel divides the weight back out
                values[matched] += self.Block_At(weights, offset) / quadrature_weight
            return values

        return Pair_Kernel


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = dict(self.parameter_values)
        weights = self.parameter_values["stencil_weights"]
        # the size of each offset's whole channel block, which is a field over the stencil box
        state["stencil_magnitudes"] = np.sqrt((weights**2).sum(axis=(3, 4)))
        state["stencil_offsets"] = self.Offsets().reshape(*weights.shape[:3], 3)
        if self.last_output_values is not None:
            state["last_output_values"] = self.last_output_values
        return state


def Stencil_From_Weights(stencil_weights: NDArray[np.float64]) -> TabulatedStencilKernel:
    """a stencil kernel carrying weights that were computed rather than drawn"""
    offset_extents = stencil_weights.shape[:3]
    if any(int(extent) % 2 == 0 for extent in offset_extents):
        raise ValueError("a stencil box runs from minus a half-width to plus it, so every extent is odd")
    half_widths = tuple((int(extent) - 1) // 2 for extent in offset_extents)
    stencil = TabulatedStencilKernel(
        half_widths=(half_widths[0], half_widths[1], half_widths[2]),
        output_channels=int(stencil_weights.shape[3]),
        input_channels=int(stencil_weights.shape[4]),
    )
    stencil.parameter_values["stencil_weights"] = np.asarray(stencil_weights, dtype=np.float64)
    return stencil
