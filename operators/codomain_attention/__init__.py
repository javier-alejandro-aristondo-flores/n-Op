"""any subset of the corpus fields to the fields left out"""

from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.codomain_attention.channels import (
    CHANNEL_VOCABULARY,
    ChannelStatistics,
    COARSE_SHAPE,
    ELF_GROUP,
    Functional_One_Hot,
    FUNCTIONAL_COVARIATE_WIDTH,
    Invert_Channel,
    Transform_Channel,
)
from operators.codomain_attention.readout import Per_Token_Heads, TokenSharedReadout
from operators.compositions import ExplicitStack
from operators.encoders import VariableEncoding
from operators.framework import (
    Array,
    Coefficients,
    Discretization,
    GridFunction,
    GridSpec,
    Layer,
    NeuralOperator,
    Spectral_Truncation_Resample,
    UniformGridQuadrature,
)
from operators.kernels.codomain_attention import CodomainAttentionKernel, TokenSharedLocalLinear
from operators.kernels.spectral import ModeMixing
from operators.wrappers import Renormalization_Scale

# the minimal configuration test-suite.md V.1 and IMPLEMENTATION.md pre-register
HIDDEN_CHANNELS = 32
KEPT_MODE = 19
HEAD_COUNT = 2
LAYER_COUNT = 4
MODE_MIXING: ModeMixing = "separable"

# a value clearly off every channel's own operating range in its transformed space, so the mask is never confusable
# with a visible channel that happens to sit near zero -- trained from here, never fixed
MASK_FLAG_INITIAL_VALUE = 3.0

CANONICAL_LABEL_INDICES = np.arange(len(CHANNEL_VOCABULARY), dtype=np.intp)


def Completion_Layers(
    hidden_channels: int,
    kept_modes: tuple[int, int, int],
    head_count: int,
    layer_count: int,
    seed: int,
    mode_mixing: ModeMixing,
) -> tuple[Layer[GridFunction], ...]:
    """the explicit stack's own layers, one codomain-attention kernel and one token-shared local linear term each"""
    return tuple(
        Layer(
            kernel=CodomainAttentionKernel(
                hidden_channels,
                kept_modes,
                head_count=head_count,
                seed=seed + 2 * layer_index,
                mode_mixing=mode_mixing,
            ),
            local_linear=TokenSharedLocalLinear(hidden_channels, seed=seed + 2 * layer_index + 1),
            residual=True,
        )
        for layer_index in range(layer_count)
    )


class CodomainAttention(NeuralOperator[GridFunction, GridFunction, GridFunction]):
    """variable channel encodings with attention over channel tokens"""


    def __init__(
        self,
        statistics: ChannelStatistics,
        hidden_channels: int = HIDDEN_CHANNELS,
        kept_modes: tuple[int, int, int] = (KEPT_MODE, KEPT_MODE, KEPT_MODE),
        head_count: int = HEAD_COUNT,
        layer_count: int = LAYER_COUNT,
        seed: int = 0,
        mode_mixing: ModeMixing = MODE_MIXING,
        coarse_shape: tuple[int, int, int] = COARSE_SHAPE,
    ) -> None:
        encoder = VariableEncoding(
            vocabulary=CHANNEL_VOCABULARY,
            hidden_channels=hidden_channels,
            condition_width=FUNCTIONAL_COVARIATE_WIDTH,
            seed=seed,
        )
        composition = ExplicitStack(
            Completion_Layers(hidden_channels, kept_modes, head_count, layer_count, seed + 1, mode_mixing)
        )
        readout = TokenSharedReadout(hidden_channels, seed=seed + 1000)
        super().__init__(encoder, composition, readout)
        # the base class stores these under the protocol type; these own-named aliases keep the concrete one
        self.channel_encoder = encoder
        self.attention_stack = composition
        self.token_readout = readout
        self.hidden_channels = hidden_channels
        self.kept_modes = kept_modes
        self.head_count = head_count
        self.layer_count = layer_count
        self.mode_mixing: ModeMixing = mode_mixing
        self.coarse_shape = coarse_shape
        self.statistics = statistics
        self.parameter_values: dict[str, NDArray[np.float64]] = {
            "mask_flag": np.asarray(MASK_FLAG_INITIAL_VALUE),
        }
        self.last_reconstruction: NDArray[np.float64] | None = None
        self.last_present_labels: tuple[str, ...] | None = None


    def Parameter_Values(self) -> dict[str, NDArray[np.float64]]:
        """every part's own arrays under one flat namespace, ready for the trainer"""
        collected: dict[str, NDArray[np.float64]] = dict(self.channel_encoder.parameter_values)
        collected.update(self.attention_stack.Parameter_Values())
        collected.update(self.token_readout.parameter_values)
        collected.update(self.parameter_values)
        return collected


    def Parameter_Count(self) -> int:
        """how many real numbers this member stores, at any token count it is ever asked to answer for"""
        return sum(int(value.size) for value in self.Parameter_Values().values())


    def Forward_Tokens(
        self, lifted: dict[str, Any], full_transformed_stack: Any, visible_mask: Any, condition_vector: Any
    ) -> Any:
        """the lifted masked-reconstruction forward: hidden channels replaced by the learned mask flag before encoding"""
        broadcast_visible = visible_mask[:, None, None, None]
        mask_flag = lifted["mask_flag"]
        channel_values = full_transformed_stack * broadcast_visible + mask_flag * (1.0 - broadcast_visible)
        tokens = self.channel_encoder.Forward(lifted, channel_values, CANONICAL_LABEL_INDICES, condition_vector)
        hidden = self.attention_stack.Forward(lifted, tokens)
        reconstruction = self.token_readout.Forward(lifted, hidden)
        return Per_Token_Heads(reconstruction, CHANNEL_VOCABULARY)


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        if not isinstance(output_discretization, GridSpec):
            raise TypeError("the codomain attention operator evaluates on grids only")
        present_labels = input_function.channel_labels
        raw_values = np.asarray(input_function.values, dtype=np.float64)
        full_stack = np.zeros((len(CHANNEL_VOCABULARY), *self.coarse_shape), dtype=np.float64)
        for position, label in enumerate(CHANNEL_VOCABULARY):
            if label not in present_labels:
                continue
            raw_field = raw_values[present_labels.index(label)]
            coarse_raw = (
                raw_field
                if label in ELF_GROUP
                else Spectral_Truncation_Resample(raw_field[None], self.coarse_shape)[0]
            )
            full_stack[position] = Transform_Channel(label, coarse_raw, self.statistics)
        visible_mask = np.asarray(
            [1.0 if label in present_labels else 0.0 for label in CHANNEL_VOCABULARY], dtype=np.float64
        )
        condition_vector = (
            np.asarray(condition.vector, dtype=np.float64)
            if condition is not None
            else Functional_One_Hot("", "other")
        )
        reconstruction = np.asarray(
            self.Forward_Tokens(self.Parameter_Values(), full_stack, visible_mask, condition_vector),
            dtype=np.float64,
        )
        physical_values = np.stack(
            [
                Invert_Channel(label, reconstruction[position], self.statistics)
                for position, label in enumerate(CHANNEL_VOCABULARY)
            ]
        )
        self.last_reconstruction = reconstruction
        self.last_present_labels = present_labels
        point_count = self.coarse_shape[0] * self.coarse_shape[1] * self.coarse_shape[2]
        quadrature = UniformGridQuadrature(input_function.quadrature.cell_volume, point_count)
        return GridFunction(physical_values, CHANNEL_VOCABULARY, input_function.domain, quadrature)


    def Renormalized_Density(
        self, predicted_density: NDArray[np.float64], cell_volume: float, electron_count: float
    ) -> NDArray[np.float64]:
        """the predicted charge density rescaled onto a target electron count, an explicit opt-in step at whole-field inference"""
        weight_each = cell_volume / predicted_density.size
        scale = Renormalization_Scale(predicted_density, weight_each, np.asarray(electron_count, dtype=np.float64))
        return predicted_density * scale


    def Inspect(self) -> dict[str, Array]:
        state = super().Inspect()
        state["mask_flag"] = self.parameter_values["mask_flag"]
        state["reference_density"] = np.asarray(self.statistics.reference_density)
        state["magnetization_scale"] = np.asarray(self.statistics.magnetization_scale)
        state["potential_scale"] = np.asarray(self.statistics.potential_scale)
        if self.last_reconstruction is not None:
            state["last_reconstruction"] = self.last_reconstruction
        return state
