"""the fused alias-free activation: exact upsample, gelu, exact downsample, streamed over channel chunks"""

from typing import Any

from operators.compositions import Downsampled_By_Two, Upsampled_By_Two
from operators.substrate import Concatenate_Channels, CustomGradient, Gaussian_Error_Linear_Unit, Hyperbolic_Tangent

# each chunk upsamples this many channels at once, so the doubled intermediate never covers the whole width
CHANNEL_CHUNK_SIZE = 4

# the tanh-form gelu's own constants, repeated from operators.substrate.operations until a dispatched
# derivative lands there -- operators.substrate is the only package allowed to define them once
GELU_CUBIC_COEFFICIENT = 0.044715

GELU_INNER_SCALE = 0.7978845608028654


def Gaussian_Error_Linear_Unit_Derivative(value: Any) -> Any:
    """the tanh-form gelu's own slope, engine-agnostic through the dispatched hyperbolic tangent"""
    cubic_shaping = value + GELU_CUBIC_COEFFICIENT * value * value * value
    inner = GELU_INNER_SCALE * cubic_shaping
    tanh_inner = Hyperbolic_Tangent(inner)
    inner_slope = GELU_INNER_SCALE * (1.0 + 3.0 * GELU_CUBIC_COEFFICIENT * value * value)
    return 0.5 * (1.0 + tanh_inner) + 0.5 * value * (1.0 - tanh_inner * tanh_inner) * inner_slope


def Channel_Chunks(channel_count: int) -> list[tuple[int, int]]:
    """the start and stop of every channel chunk the streamed activation visits in turn"""
    return [
        (start, min(start + CHANNEL_CHUNK_SIZE, channel_count))
        for start in range(0, channel_count, CHANNEL_CHUNK_SIZE)
    ]


def Streamed_Alias_Free_Value(values: Any) -> Any:
    """the activation's own value, one channel chunk upsampled, activated and downsampled at a time"""
    chunks = [
        Downsampled_By_Two(Gaussian_Error_Linear_Unit(Upsampled_By_Two(values[start:stop])))
        for start, stop in Channel_Chunks(values.shape[0])
    ]
    return Concatenate_Channels(chunks)


def Streamed_Alias_Free_Cotangent(values: Any, cotangent: Any) -> Any:
    """the input's own cotangent, the closed-form pullback recomputed one channel chunk at a time"""
    chunks: list[Any] = []
    for start, stop in Channel_Chunks(values.shape[0]):
        upsampled_input = Upsampled_By_Two(values[start:stop])
        upsampled_cotangent = Upsampled_By_Two(cotangent[start:stop])
        slope = Gaussian_Error_Linear_Unit_Derivative(upsampled_input)
        chunks.append(Downsampled_By_Two(slope * upsampled_cotangent))
    return Concatenate_Channels(chunks)


def Alias_Free_Activation_Forward(arguments: tuple[Any, ...]) -> Any:
    """the streamed value alone, the declared forward half of the custom gradient rule"""
    (values,) = arguments
    return Streamed_Alias_Free_Value(values)


def Alias_Free_Activation_Backward(cotangent: Any, output: Any, saved_arguments: tuple[Any, ...]) -> tuple[Any, ...]:
    """the streamed cotangent alone, the declared backward half of the custom gradient rule"""
    (values,) = saved_arguments
    return (Streamed_Alias_Free_Cotangent(values, cotangent),)


# one rule instance shared by every call, since it carries no state beyond the two functions above
ALIAS_FREE_ACTIVATION_RULE = CustomGradient(
    forward=Alias_Free_Activation_Forward, backward=Alias_Free_Activation_Backward
)


def Alias_Free_Activation(values: Any) -> Any:
    """upsample by two, gelu, downsample by two, so the nonlinearity acts band-limited and stays band-limited"""
    return ALIAS_FREE_ACTIVATION_RULE.Apply(values)
