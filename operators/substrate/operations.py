"""array mathematics that differs between engines, dispatched on the array's kind"""

from typing import Any

import numpy as np
from numpy.typing import NDArray

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


def Detached(value: Any) -> Any:
    """the value with its gradient history cut, unchanged on the reference engine"""
    return value.detach() if Is_Engine_Native(value) else value
