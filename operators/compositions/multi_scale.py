"""the U-shaped composition, descending scales joined to ascending scales by skip connections"""

from math import prod
from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.framework import Array, Coefficients, Composition, GridFunction, Layer, UniformGridQuadrature
from operators.substrate import (
    Concatenate_Channels,
    Gaussian_Error_Linear_Unit,
    GRID_AXES,
    Half_Spectrum_Extent,
    Inverse_Real_Fourier_Transform_3d,
    Join_Along_Axis,
    Real_Fourier_Transform_3d,
    Sliced_Along_Axis,
    Split_Batch_From_Grid,
    Zeros_Beside,
)


def Sliced_Lifted(lifted: dict[str, Any], prefix: str) -> dict[str, Any]:
    """the slice of a shared lifted dict that belongs to one part, its own names restored"""
    return {name[len(prefix):]: value for name, value in lifted.items() if name.startswith(prefix)}


def Layer_Applied(layer: Layer[GridFunction], lifted: dict[str, Any], input_values: Any) -> Any:
    """one layer's activation over its kernel-plus-local sum, run at the shape its input already carries"""
    _, spatial_shape = Split_Batch_From_Grid(input_values)
    kernel_output = layer.kernel.Forward(Sliced_Lifted(lifted, "kernel."), input_values, spatial_shape)
    local_output = layer.local_linear.Forward(Sliced_Lifted(lifted, "local_linear."), input_values)
    summed = local_output + kernel_output
    if layer.activation == "alias_free":
        raise NotImplementedError("the alias-free activation is the convolutional entry's own build")
    activated = Gaussian_Error_Linear_Unit(summed)
    # a residual layer can only add its input back when the channel count survived
    if layer.residual and activated.shape == input_values.shape:
        activated = activated + input_values
    return activated


def Resampled_Full_Spectral_Axis(spectrum: Any, axis: int, source_extent: int, target_extent: int) -> Any:
    """one full complex spectral axis truncated or zero-padded to a new length, its low modes kept exactly"""
    largest_kept_mode = (min(source_extent, target_extent) - 1) // 2
    non_negative = Sliced_Along_Axis(spectrum, axis, 0, largest_kept_mode + 1)
    negative = Sliced_Along_Axis(spectrum, axis, source_extent - largest_kept_mode, source_extent)
    pieces = [non_negative]
    middle_extent = target_extent - (2 * largest_kept_mode + 1)
    if middle_extent > 0:
        middle_shape = list(non_negative.shape)
        middle_shape[axis] = middle_extent
        pieces.append(Zeros_Beside(non_negative, tuple(middle_shape)))
    pieces.append(negative)
    return Join_Along_Axis(pieces, axis)


def Resampled_Half_Spectral_Axis(half_spectrum: Any, source_extent: int, target_extent: int) -> Any:
    """the last, half-stored spectral axis truncated or zero-padded to a new length, its low modes kept exactly"""
    largest_kept_mode = (min(source_extent, target_extent) - 1) // 2
    # a real field's last axis stores no negative mode, so only the non-negative count ever changes
    kept = Sliced_Along_Axis(half_spectrum, -1, 0, largest_kept_mode + 1)
    target_half_extent = Half_Spectrum_Extent(target_extent)
    filler_extent = target_half_extent - (largest_kept_mode + 1)
    if filler_extent > 0:
        filler_shape = list(kept.shape)
        filler_shape[-1] = filler_extent
        kept = Join_Along_Axis([kept, Zeros_Beside(kept, tuple(filler_shape))], -1)
    return kept


def Spectral_Resampled(values: Any, target_shape: tuple[int, int, int]) -> Any:
    """the field moved to a new grid shape by exact spectral truncation or zero-padding, lifted and differentiable"""
    _, source_shape = Split_Batch_From_Grid(values)
    half_spectrum = Real_Fourier_Transform_3d(values)
    for axis, source_extent, target_extent in zip(GRID_AXES[:2], source_shape[:2], target_shape[:2]):
        half_spectrum = Resampled_Full_Spectral_Axis(half_spectrum, axis, source_extent, target_extent)
    half_spectrum = Resampled_Half_Spectral_Axis(half_spectrum, source_shape[2], target_shape[2])
    resampled = Inverse_Real_Fourier_Transform_3d(half_spectrum, target_shape)
    # the transform is unnormalized, so the point-count ratio is what restores the amplitude
    scale = prod(target_shape) / prod(source_shape)
    return resampled * scale


def Halved_Shape(spatial_shape: tuple[int, int, int]) -> tuple[int, int, int]:
    """a grid shape's exact half on every axis, raised on rather than rounded when an extent is odd"""
    for extent in spatial_shape:
        if extent % 2 != 0:
            raise ValueError(f"a scale transition halves every extent exactly, and {spatial_shape} does not")
    return (spatial_shape[0] // 2, spatial_shape[1] // 2, spatial_shape[2] // 2)


def Doubled_Shape(spatial_shape: tuple[int, int, int]) -> tuple[int, int, int]:
    """a grid shape's exact double on every axis"""
    return (spatial_shape[0] * 2, spatial_shape[1] * 2, spatial_shape[2] * 2)


def Downsampled_By_Two(values: Any) -> Any:
    """the field moved one scale down, by exact spectral truncation on the lifted path"""
    _, spatial_shape = Split_Batch_From_Grid(values)
    return Spectral_Resampled(values, Halved_Shape(spatial_shape))


def Upsampled_By_Two(values: Any) -> Any:
    """the field moved one scale up, by exact spectral zero-padding on the lifted path"""
    _, spatial_shape = Split_Batch_From_Grid(values)
    return Spectral_Resampled(values, Doubled_Shape(spatial_shape))


def Collected_Layer_Parameters(
    collected: dict[str, NDArray[np.float64]], prefix: str, layer: Layer[GridFunction]
) -> None:
    """one layer's kernel and local linear arrays written into a shared dict under its own prefix"""
    for name, value in layer.kernel.parameter_values.items():
        collected[f"{prefix}.kernel.{name}"] = value
    for name, value in layer.local_linear.parameter_values.items():
        collected[f"{prefix}.local_linear.{name}"] = value


def Contributed_Layer_Inspection(state: dict[str, Array], prefix: str, layer: Layer[GridFunction]) -> None:
    """one layer's kernel and local linear inspection state written into a shared dict under its own prefix"""
    for name, value in layer.kernel.Inspect().items():
        state[f"{prefix}.kernel.{name}"] = value
    for name, value in layer.local_linear.Inspect().items():
        state[f"{prefix}.local_linear.{name}"] = value


class MultiScale(Composition[GridFunction]):
    """a directed graph of scales, descending then a bottom then ascending, output designated at one scale"""


    def __init__(
        self,
        descending_layers: tuple[Layer[GridFunction], ...],
        bottom_layer: Layer[GridFunction],
        ascending_layers: tuple[Layer[GridFunction], ...],
        output_scale: int,
    ) -> None:
        scale_count = len(descending_layers) + 1
        if not 0 <= output_scale < scale_count:
            raise ValueError(f"the output scale must be between 0 and {scale_count - 1}, not {output_scale}")
        expected_ascending_count = len(descending_layers) - output_scale
        if len(ascending_layers) != expected_ascending_count:
            raise ValueError(
                f"reaching output scale {output_scale} from {len(descending_layers)} descending layers needs "
                f"{expected_ascending_count} ascending layers, not {len(ascending_layers)}"
            )
        self.descending_layers = descending_layers
        self.bottom_layer = bottom_layer
        self.ascending_layers = ascending_layers
        self.output_scale = output_scale
        self.last_scale_norms: dict[str, float] | None = None
        self.last_scale_shapes: dict[str, tuple[int, int, int]] | None = None


    def Scale_Outputs(self, lifted: dict[str, Any], input_values: Any) -> list[tuple[str, Any]]:
        """every scale's output in turn, descending then bottom then ascending, ending at the designated scale"""
        named_outputs: list[tuple[str, Any]] = []
        descending_outputs: list[Any] = []
        current = input_values
        for descending_index, layer in enumerate(self.descending_layers):
            current = Layer_Applied(layer, Sliced_Lifted(lifted, f"descending_{descending_index}."), current)
            descending_outputs.append(current)
            named_outputs.append((f"descending_{descending_index}", current))
            current = Downsampled_By_Two(current)
        current = Layer_Applied(self.bottom_layer, Sliced_Lifted(lifted, "bottom."), current)
        named_outputs.append(("bottom", current))
        for ascending_index, layer in enumerate(self.ascending_layers):
            # the skip reads the newest descending scale first, mirroring the order the bottom was reached in
            skip_position = len(self.descending_layers) - 1 - ascending_index
            joined = Concatenate_Channels([Upsampled_By_Two(current), descending_outputs[skip_position]])
            current = Layer_Applied(layer, Sliced_Lifted(lifted, f"ascending_{ascending_index}."), joined)
            named_outputs.append((f"ascending_{ascending_index}", current))
        return named_outputs


    def Forward(self, lifted: dict[str, Any], input_values: Any) -> Any:
        """the field at the designated output scale, differentiable through whichever engine lifted the shared dict"""
        return self.Scale_Outputs(lifted, input_values)[-1][1]


    def Parameter_Values(self) -> dict[str, NDArray[np.float64]]:
        """every layer's kernel and local linear arrays, prefixed by path and position so none collide"""
        collected: dict[str, NDArray[np.float64]] = {}
        for descending_index, layer in enumerate(self.descending_layers):
            Collected_Layer_Parameters(collected, f"descending_{descending_index}", layer)
        Collected_Layer_Parameters(collected, "bottom", self.bottom_layer)
        for ascending_index, layer in enumerate(self.ascending_layers):
            Collected_Layer_Parameters(collected, f"ascending_{ascending_index}", layer)
        return collected


    def Apply(self, input_function: GridFunction, condition: Coefficients | None = None) -> GridFunction:
        values = np.asarray(input_function.values, dtype=np.float64)
        named_outputs = self.Scale_Outputs(self.Parameter_Values(), values)
        last_scale_norms: dict[str, float] = {}
        last_scale_shapes: dict[str, tuple[int, int, int]] = {}
        for name, output in named_outputs:
            produced_at_scale = np.asarray(output, dtype=np.float64)
            last_scale_norms[name] = float(np.linalg.norm(produced_at_scale))
            last_scale_shapes[name] = Split_Batch_From_Grid(produced_at_scale)[1]
        self.last_scale_norms = last_scale_norms
        self.last_scale_shapes = last_scale_shapes
        produced = np.asarray(named_outputs[-1][1], dtype=np.float64)
        leading_shape, output_shape = Split_Batch_From_Grid(produced)
        point_count = output_shape[0] * output_shape[1] * output_shape[2]
        quadrature = UniformGridQuadrature(input_function.quadrature.cell_volume, point_count)
        output_labels = tuple(f"channel_{output_channel}" for output_channel in range(leading_shape[0]))
        return GridFunction(produced, output_labels, input_function.domain, quadrature)


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = {}
        for descending_index, layer in enumerate(self.descending_layers):
            Contributed_Layer_Inspection(state, f"descending_{descending_index}", layer)
        Contributed_Layer_Inspection(state, "bottom", self.bottom_layer)
        for ascending_index, layer in enumerate(self.ascending_layers):
            Contributed_Layer_Inspection(state, f"ascending_{ascending_index}", layer)
        if self.last_scale_norms is not None:
            for name, norm in self.last_scale_norms.items():
                state[f"{name}_output_norm"] = np.asarray(norm)
        if self.last_scale_shapes is not None:
            for name, shape in self.last_scale_shapes.items():
                state[f"{name}_output_shape"] = np.asarray(shape)
        return state
