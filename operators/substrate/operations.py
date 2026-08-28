"""array mathematics that differs between engines, dispatched on the array's kind"""

from typing import Any

import numpy as np

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


def Sum_Over_Last_Axis(value: Any) -> Any:
    return Torch_Module().sum(value, dim=-1) if Is_Engine_Native(value) else np.sum(value, axis=-1)


def Mean_Over_Last_Axis(value: Any) -> Any:
    return Torch_Module().mean(value, dim=-1) if Is_Engine_Native(value) else np.mean(value, axis=-1)


def Concatenate_Channels(values: list[Any]) -> Any:
    if any(Is_Engine_Native(value) for value in values):
        return Torch_Module().cat(values, dim=0)
    return np.concatenate(values, axis=0)
