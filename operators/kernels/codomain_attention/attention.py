"""attention over channel tokens, query key and value each a token-shared spectral kernel"""

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
from operators.kernels.codomain_attention.layer_norm import FunctionSpaceLayerNorm
from operators.kernels.codomain_attention.tokens import Token_Count
from operators.kernels.spectral import ModeMixing, SpectralKernel
from operators.substrate import Einstein_Summation, Exponential, Mean_Over_Last_Axis, Precision, Sum_Over_Last_Axis


def Sliced_Lifted(lifted: dict[str, Any], prefix: str) -> dict[str, Any]:
    """the slice of a shared lifted dict that belongs to one part, its own names restored"""
    return {name[len(prefix):]: value for name, value in lifted.items() if name.startswith(prefix)}


class CodomainAttentionKernel(Kernel[GridFunction, GridFunction]):
    """attention over channel tokens packed token-major, channel index is token index times hidden channels plus hidden index"""

    supported_representations = (GridFunction,)


    def __init__(
        self,
        hidden_channels: int,
        kept_modes: tuple[int, int, int],
        head_count: int = 1,
        seed: int = 0,
        working_precision: Precision = "double",
        mode_mixing: ModeMixing = "full",
    ) -> None:
        if hidden_channels % head_count != 0:
            raise ValueError(f"{hidden_channels} hidden channels do not split evenly into {head_count} heads")
        self.hidden_channels = hidden_channels
        self.kept_modes = kept_modes
        self.head_count = head_count
        self.head_width = hidden_channels // head_count
        self.working_precision: Precision = working_precision
        self.mode_mixing: ModeMixing = mode_mixing
        self.pre_norm = FunctionSpaceLayerNorm(hidden_channels)
        # each inner kernel takes the base seed offset by its position, so all four differ
        self.query_kernel = SpectralKernel(
            kept_modes,
            hidden_channels,
            hidden_channels,
            seed=seed,
            mode_mixing=mode_mixing,
            working_precision=working_precision,
        )
        self.key_kernel = SpectralKernel(
            kept_modes,
            hidden_channels,
            hidden_channels,
            seed=seed + 1,
            mode_mixing=mode_mixing,
            working_precision=working_precision,
        )
        self.value_kernel = SpectralKernel(
            kept_modes,
            hidden_channels,
            hidden_channels,
            seed=seed + 2,
            mode_mixing=mode_mixing,
            working_precision=working_precision,
        )
        self.output_kernel = SpectralKernel(
            kept_modes,
            hidden_channels,
            hidden_channels,
            seed=seed + 3,
            mode_mixing=mode_mixing,
            working_precision=working_precision,
        )
        self.spectral_parts: tuple[tuple[str, SpectralKernel], ...] = (
            ("query.", self.query_kernel),
            ("key.", self.key_kernel),
            ("value.", self.value_kernel),
            ("output.", self.output_kernel),
        )
        self.parameter_values: dict[str, NDArray[np.float64]] = {"temperature": np.ones(head_count)}
        for name, value in self.pre_norm.parameter_values.items():
            self.parameter_values[f"norm.{name}"] = value
        for prefix, spectral_part in self.spectral_parts:
            for name, value in spectral_part.parameter_values.items():
                self.parameter_values[f"{prefix}{name}"] = value
        self.last_attention_scores: NDArray[np.float64] | None = None


    def Parameter_Count(self) -> int:
        """how many real numbers this kernel stores, the same at every token count it is ever asked to answer for"""
        return sum(int(value.size) for value in self.parameter_values.values())


    @staticmethod
    def Parameter_Count_For(
        hidden_channels: int, kept_modes: tuple[int, int, int], head_count: int, mode_mixing: ModeMixing
    ) -> int:
        """the same count without building the weights, so a configuration can be priced before it is paid"""
        spectral_count = SpectralKernel.Parameter_Count_For(kept_modes, hidden_channels, hidden_channels, mode_mixing)
        return 4 * spectral_count + 2 * hidden_channels + head_count


    def Head_Split(self, values: Any, token_count: int) -> Any:
        """the hidden-channel axis split into heads, each head a contiguous block of the whole width"""
        return values.reshape(token_count, self.head_count, self.head_width, *values.shape[2:])


    def Query_Key_Value(self, lifted: dict[str, Any], input_values: Any, token_count: int) -> tuple[Any, Any, Any]:
        """the head-split query key and value functions this kernel scores its attention over"""
        normalized = self.pre_norm.Forward(Sliced_Lifted(lifted, "norm."), input_values)
        input_shape = normalized.shape[-3:]
        unflattened = normalized.reshape(token_count, self.hidden_channels, *input_shape)
        query = self.query_kernel.Forward(Sliced_Lifted(lifted, "query."), unflattened, input_shape)
        key = self.key_kernel.Forward(Sliced_Lifted(lifted, "key."), unflattened, input_shape)
        value = self.value_kernel.Forward(Sliced_Lifted(lifted, "value."), unflattened, input_shape)
        return (
            self.Head_Split(query, token_count),
            self.Head_Split(key, token_count),
            self.Head_Split(value, token_count),
        )


    @staticmethod
    def Softmax_Over_Last_Axis(logits: Any) -> Any:
        """the last axis turned into a probability distribution, shifted first so a large logit cannot overflow"""
        # softmax is shift-invariant, so subtracting each row's own mean bounds the exponent by its spread alone
        shifted = logits - Mean_Over_Last_Axis(logits)[..., None]
        exponentiated = Exponential(shifted)
        return exponentiated / Sum_Over_Last_Axis(exponentiated)[..., None]


    def Attention_Weights(self, lifted: dict[str, Any], query_heads: Any, key_heads: Any, grid_point_count: int) -> Any:
        """softmax over source tokens of the temperature-scaled mean channel-summed inner product"""
        raw_scores = Einstein_Summation("thcxyz,shcxyz->hts", query_heads, key_heads) / float(grid_point_count)
        # temperature multiplies the raw score, so a zeroed temperature collapses attention to uniform
        logits = raw_scores * lifted["temperature"][:, None, None]
        return self.Softmax_Over_Last_Axis(logits)


    def Forward(self, lifted: dict[str, Any], input_values: Any, output_shape: tuple[int, int, int]) -> Any:
        token_count = Token_Count(input_values.shape[0], self.hidden_channels)
        grid_shape = input_values.shape[-3:]
        grid_point_count = int(grid_shape[0]) * int(grid_shape[1]) * int(grid_shape[2])
        query_heads, key_heads, value_heads = self.Query_Key_Value(lifted, input_values, token_count)
        attention_weights = self.Attention_Weights(lifted, query_heads, key_heads, grid_point_count)
        attended = Einstein_Summation("hts,shcxyz->thcxyz", attention_weights, value_heads)
        merged = attended.reshape(token_count, self.hidden_channels, *attended.shape[-3:])
        produced = self.output_kernel.Forward(Sliced_Lifted(lifted, "output."), merged, output_shape)
        return produced.reshape(token_count * self.hidden_channels, *output_shape)


    def Integrate(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        if not isinstance(output_discretization, GridSpec):
            raise TypeError("the codomain-attention kernel evaluates on grids only")
        field = np.asarray(input_function.values, dtype=np.float64)
        token_count = Token_Count(field.shape[0], self.hidden_channels)
        grid_point_count = int(field.shape[-3]) * int(field.shape[-2]) * int(field.shape[-1])
        query_heads, key_heads, _ = self.Query_Key_Value(self.parameter_values, field, token_count)
        self.last_attention_scores = np.asarray(
            self.Attention_Weights(self.parameter_values, query_heads, key_heads, grid_point_count), dtype=np.float64
        )
        produced = np.asarray(
            self.Forward(self.parameter_values, field, output_discretization.shape), dtype=np.float64
        )
        output_labels = tuple(
            f"token_{token_index}_channel_{hidden_index}"
            for token_index in range(token_count)
            for hidden_index in range(self.hidden_channels)
        )
        quadrature = input_function.quadrature
        return GridFunction(
            values=produced,
            channel_labels=output_labels,
            domain=input_function.domain,
            quadrature=UniformGridQuadrature(quadrature.cell_volume, int(np.prod(output_discretization.shape))),
        )


    def Refreshed(self, part_parameter_values: dict[str, NDArray[np.float64]], prefix: str) -> None:
        """the part's own dict brought current from this kernel's aggregate, so inspecting it reflects training"""
        for name, value in Sliced_Lifted(self.parameter_values, prefix).items():
            part_parameter_values[name] = value


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = dict(self.parameter_values)
        self.Refreshed(self.pre_norm.parameter_values, "norm.")
        for name, value in self.pre_norm.Inspect().items():
            state[f"norm.{name}"] = value
        for prefix, spectral_part in self.spectral_parts:
            self.Refreshed(spectral_part.parameter_values, prefix)
            for name, value in spectral_part.Inspect().items():
                state[f"{prefix}{name}"] = value
        if self.last_attention_scores is not None:
            state["last_attention_scores"] = self.last_attention_scores
        return state
