"""array mathematics that differs between engines, dispatched on the array's kind"""

from collections.abc import Callable
from importlib import import_module
from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.substrate.linear_algebra import Largest_Singular_Values_Of_Stack
from operators.substrate.devices import Accelerator_Is_Available
from operators.substrate.torch_engine import Torch_Module


def Is_Engine_Native(value: Any) -> bool:
    """whether the value belongs to the foreign engine rather than numpy"""
    return not isinstance(value, (np.ndarray, np.generic, float, int))


def Exponential(value: Any) -> Any:
    return Torch_Module().exp(value) if Is_Engine_Native(value) else np.exp(value)


def Hyperbolic_Tangent(value: Any) -> Any:
    return Torch_Module().tanh(value) if Is_Engine_Native(value) else np.tanh(value)


def Softplus(value: Any) -> Any:
    if Is_Engine_Native(value):
        return Torch_Module().nn.functional.softplus(value)
    # log of one plus the exponential, computed without overflowing
    return np.logaddexp(0.0, value)


def Gaussian_Error_Linear_Unit(value: Any) -> Any:
    # the tanh form, so every engine returns the same numbers
    shaping = value + 0.044715 * value * value * value
    # 0.79788... is the square root of two over pi
    return 0.5 * value * (1.0 + Hyperbolic_Tangent(0.7978845608028654 * shaping))


def Gaussian_Error_Linear_Unit_Derivative(value: Any) -> Any:
    """the derivative of the tanh-form smooth unit with respect to its input"""
    shaping = value + 0.044715 * value * value * value
    shaping_derivative = 1.0 + 3.0 * 0.044715 * value * value
    hyperbolic_tangent_value = Hyperbolic_Tangent(0.7978845608028654 * shaping)
    envelope_derivative = (
        0.5 * value * (1.0 - hyperbolic_tangent_value * hyperbolic_tangent_value)
        * 0.7978845608028654 * shaping_derivative
    )
    return 0.5 * (1.0 + hyperbolic_tangent_value) + envelope_derivative


def Host_Array(value: Any) -> NDArray[np.float64]:
    """the value as a double array on the host, whichever engine and device hold it"""
    if Is_Engine_Native(value):
        return np.asarray(value.detach().cpu().numpy(), dtype=np.float64)
    return np.asarray(value, dtype=np.float64)


def Sum_Over_Last_Axis(value: Any) -> Any:
    return Torch_Module().sum(value, dim=-1) if Is_Engine_Native(value) else np.asarray(value).sum(axis=-1)


def Mean_Over_Last_Axis(value: Any) -> Any:
    return Torch_Module().mean(value, dim=-1) if Is_Engine_Native(value) else np.mean(value, axis=-1)


def Maximum_Over_Last_Axis(value: Any) -> Any:
    # the foreign engine returns the maxima paired with their positions, and only the maxima are wanted
    return Torch_Module().max(value, dim=-1).values if Is_Engine_Native(value) else np.asarray(value).max(axis=-1)


def Concatenate_Channels(values: list[Any]) -> Any:
    if any(Is_Engine_Native(value) for value in values):
        return Torch_Module().cat(values, dim=0)
    return np.concatenate(values, axis=0)


def Roll_Along_Axes(value: Any, shift: tuple[int, ...], axes: tuple[int, ...]) -> Any:
    """the array rolled by an offset per axis with torus wraparound, on whichever engine carries it"""
    if Is_Engine_Native(value):
        return Torch_Module().roll(value, shifts=shift, dims=axes)
    return np.roll(value, shift=shift, axis=axes)


def Contract_Channel_Axis(block: Any, values: Any) -> Any:
    """a channel-mixing block contracted against a value's leading channel axis, on whichever engine carries them"""
    if Is_Engine_Native(block) or Is_Engine_Native(values):
        return Torch_Module().tensordot(block, values, dims=([1], [0]))
    return np.tensordot(block, values, axes=([1], [0]))


def Scatter_Add(row_count: int, receiving_points: Any, per_edge: Any) -> Any:
    """every row of per_edge summed into a fresh array of row_count rows at its own receiving row"""
    if Is_Engine_Native(per_edge):
        torch = Torch_Module()
        native_receiving_points = (
            receiving_points if Is_Engine_Native(receiving_points) else torch.as_tensor(receiving_points)
        )
        device_receiving_points = native_receiving_points.to(device=per_edge.device, dtype=torch.long)
        accumulated = torch.zeros((row_count, *per_edge.shape[1:]), dtype=per_edge.dtype, device=per_edge.device)
        return accumulated.index_add_(0, device_receiving_points, per_edge)
    accumulated = np.zeros((row_count, *per_edge.shape[1:]), dtype=per_edge.dtype)
    np.add.at(accumulated, np.asarray(receiving_points, dtype=np.int64), per_edge)
    return accumulated


def Periodic_Convolution_3d(values: Any, stencil_weights: Any) -> Any:
    """every whole-voxel offset's channel-mixing block applied to the shifted field and summed around the torus"""
    offset_extents = tuple(int(extent) for extent in stencil_weights.shape[:3])
    half_widths = tuple((extent - 1) // 2 for extent in offset_extents)
    if Is_Engine_Native(values) or Is_Engine_Native(stencil_weights):
        torch = Torch_Module()
        padded = values.unsqueeze(0)
        for spatial_axis, pad_width in zip((-3, -2, -1), half_widths):
            if pad_width == 0:
                continue
            head = padded.narrow(spatial_axis, padded.shape[spatial_axis] - pad_width, pad_width)
            tail = padded.narrow(spatial_axis, 0, pad_width)
            padded = torch.cat([head, padded, tail], dim=spatial_axis)
        # conv3d correlates rather than convolves, so the offset axes flip to land on the roll-and-accumulate sum
        kernel = torch.flip(stencil_weights, dims=(0, 1, 2)).permute(3, 4, 0, 1, 2).contiguous()
        return torch.nn.functional.conv3d(padded, kernel).squeeze(0)
    produced: Any = None
    for offset_index in np.ndindex(offset_extents):
        shift = (
            offset_index[0] - half_widths[0],
            offset_index[1] - half_widths[1],
            offset_index[2] - half_widths[2],
        )
        shifted = Roll_Along_Axes(values, shift, (1, 2, 3))
        contribution = Contract_Channel_Axis(stencil_weights[offset_index], shifted)
        produced = contribution if produced is None else produced + contribution
    return produced


def Detached(value: Any) -> Any:
    """the value with its gradient history cut, unchanged on the reference engine"""
    return value.detach() if Is_Engine_Native(value) else value


def Largest_Singular_Values(stack: Any) -> Any:
    """the largest singular value of every matrix in a stack, on whichever engine carries it"""
    if Is_Engine_Native(stack):
        return Torch_Module().linalg.svdvals(stack)[..., 0]
    return Largest_Singular_Values_Of_Stack(stack)


def Clipped_Above(value: Any, ceiling: float) -> Any:
    """the value capped at the ceiling from above, on whichever engine carries it"""
    if Is_Engine_Native(value):
        return Torch_Module().clamp(value, max=ceiling)
    return np.minimum(value, ceiling)


def Reset_Peak_Accelerator_Bytes() -> None:
    """the accelerator's peak-allocation counter set back to what is held right now, a no-op without one"""
    if Accelerator_Is_Available():
        Torch_Module().cuda.reset_peak_memory_stats()


def Peak_Accelerator_Bytes() -> int:
    """the most bytes the foreign engine has held on the accelerator since the last reset, zero without one"""
    if not Accelerator_Is_Available():
        return 0
    return int(Torch_Module().cuda.max_memory_allocated())


def Recomputed_In_Backward(function: Callable[[Any], Any], value: Any) -> Any:
    """the function's value with its intermediates dropped and rebuilt when the gradient is taken, plain on numpy"""
    if not Is_Engine_Native(value):
        return function(value)
    # the non-reentrant form tracks weights the function closes over, so a layer's lifted slices need no threading
    return import_module("torch.utils.checkpoint").checkpoint(function, value, use_reentrant=False)
