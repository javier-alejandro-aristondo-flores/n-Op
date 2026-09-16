"""charge density to electron localization, by alias-free convolution"""

# pyright: reportUnusedImport=false

from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray

from operators.alias_free_convolutional.activation import Alias_Free_Activation
from operators.compositions import Halved_Shape, MultiScale
from operators.encoders import PointwiseLift
from operators.factorized_fourier import (
    Combined_Coarse_Input,
    Gram_Six,
    INPUT_CHANNEL_COUNT,
    LOCALIZATION_CHANNEL_LABELS,
    Log_Compressed_Channels,
    Standardized_Gram,
)
from operators.framework import (
    Apply_Grid_Operation,
    Array,
    Coefficients,
    Diamond_Grid_Operations,
    Discretization,
    GridFunction,
    GridSpec,
    Layer,
    NeuralOperator,
    UniformGridQuadrature,
)
from operators.kernels import TabulatedStencilKernel
from operators.readouts import PointwiseProjection
from operators.substrate import Split_Batch_From_Grid

type StencilActivation = Literal["pointwise", "alias_free"]

# the tabulated stencil's own reach, one whole voxel on every axis, fixed across the whole member
STENCIL_HALF_WIDTHS = (1, 1, 1)

# the skip-connection width at each of the three scales, fine to coarse
HIDDEN_CHANNEL_WIDTHS = (32, 64, 128)


class AliasFreeConvolutional(NeuralOperator[GridFunction, GridFunction, GridFunction]):
    """pointwise lift, a multi-scale stack of alias-free convolutional layers, a bounded localization head"""


    def __init__(
        self,
        encoder: PointwiseLift,
        composition: MultiScale,
        readout: PointwiseProjection,
        reference_density: float,
        gram_mean: NDArray[np.float64],
        gram_scale: NDArray[np.float64],
    ) -> None:
        super().__init__(encoder, composition, readout)
        self.lift = encoder
        self.multi_scale = composition
        self.projection = readout
        self.reference_density = reference_density
        self.gram_mean = gram_mean
        self.gram_scale = gram_scale
        self.last_gram_vector: NDArray[np.float64] | None = None
        self.last_predicted_values: NDArray[np.float64] | None = None


    def Parameter_Values(self) -> dict[str, NDArray[np.float64]]:
        """every part's own arrays under one namespace, ready for the trainer"""
        collected = dict(self.lift.parameter_values)
        collected.update(self.multi_scale.Parameter_Values())
        collected.update(self.projection.parameter_values)
        return collected


    def Input_Channels(self, input_function: GridFunction) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """the log-compressed spin channels and the standardized Gram vector this run's own lattice carries"""
        values = np.asarray(input_function.values, dtype=np.float64)
        log_density_values = Log_Compressed_Channels(values[0], values[1], self.reference_density)
        raw_gram = Gram_Six(np.asarray(input_function.domain.lattice, dtype=np.float64))
        gram_vector = Standardized_Gram(raw_gram, self.gram_mean, self.gram_scale)
        return log_density_values, gram_vector


    def Forward_Field(
        self,
        lifted: dict[str, Any],
        log_density_values: Any,
        gram_vector: Any,
        fine_shape: tuple[int, int, int],
    ) -> Any:
        """the lifted path from the fine-grid channels through the multi-scale stack to the bounded head"""
        combined = Combined_Coarse_Input(log_density_values, gram_vector, fine_shape)
        hidden = self.lift.Forward(lifted, combined)
        carried = self.multi_scale.Forward(lifted, hidden)
        return self.projection.Forward(lifted, carried)


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        if not isinstance(output_discretization, GridSpec):
            raise TypeError("the alias-free convolutional operator evaluates on grids only")
        _, fine_shape = Split_Batch_From_Grid(np.asarray(input_function.values, dtype=np.float64))
        expected_output_shape = Halved_Shape(fine_shape)
        if output_discretization.shape != expected_output_shape:
            raise ValueError(
                f"a {fine_shape} input lands on the composition's own second scale {expected_output_shape}, "
                f"not the requested {output_discretization.shape}"
            )
        log_density_values, gram_vector = self.Input_Channels(input_function)
        produced = np.asarray(
            self.Forward_Field(self.Parameter_Values(), log_density_values, gram_vector, fine_shape),
            dtype=np.float64,
        )
        self.last_gram_vector = gram_vector
        self.last_predicted_values = produced
        point_count = produced.shape[1] * produced.shape[2] * produced.shape[3]
        quadrature = UniformGridQuadrature(input_function.quadrature.cell_volume, point_count)
        return GridFunction(produced, LOCALIZATION_CHANNEL_LABELS, input_function.domain, quadrature)


    def Inspect(self) -> dict[str, Array]:
        """every part's own arrays, plus the input transform constants and the last predicted field"""
        state = super().Inspect()
        state["reference_density"] = np.asarray(self.reference_density)
        state["gram_standardization_mean"] = self.gram_mean
        state["gram_standardization_scale"] = self.gram_scale
        if self.last_gram_vector is not None:
            state["last_gram_vector"] = self.last_gram_vector
        if self.last_predicted_values is not None:
            state["last_predicted_values"] = self.last_predicted_values
        return state


def Stencil_Layer(
    output_channels: int, input_channels: int, activation: StencilActivation, residual: bool, seed: int
) -> Layer[GridFunction]:
    """one tabulated-stencil kernel at the member's fixed half-width, paired with its own pointwise local term"""
    kernel = TabulatedStencilKernel(STENCIL_HALF_WIDTHS, output_channels, input_channels, seed=seed)
    local_linear = PointwiseLift(output_channels, input_channels, seed=seed + 1)
    return Layer(kernel=kernel, local_linear=local_linear, activation=activation, residual=residual)


def Alias_Free_Convolutional_Network(
    reference_density: float,
    gram_mean: NDArray[np.float64],
    gram_scale: NDArray[np.float64],
    hidden_channel_widths: tuple[int, int, int] = HIDDEN_CHANNEL_WIDTHS,
    activation: StencilActivation = "alias_free",
    seed: int = 0,
) -> AliasFreeConvolutional:
    """the canon configuration: three scales, the tabulated stencil kernel throughout, a bounded localization head"""
    lift_width, middle_width, bottom_width = hidden_channel_widths
    lift = PointwiseLift(lift_width, INPUT_CHANNEL_COUNT, seed=seed)
    descending_layers = (
        Stencil_Layer(lift_width, lift_width, activation, residual=True, seed=seed + 1),
        Stencil_Layer(middle_width, lift_width, activation, residual=False, seed=seed + 3),
    )
    bottom_layer = Stencil_Layer(bottom_width, middle_width, activation, residual=False, seed=seed + 5)
    ascending_layers = (
        Stencil_Layer(lift_width, bottom_width + middle_width, activation, residual=False, seed=seed + 7),
    )
    composition = MultiScale(
        descending_layers,
        bottom_layer,
        ascending_layers,
        output_scale=1,
        activations={"alias_free": Alias_Free_Activation},
    )
    projection = PointwiseProjection(
        len(LOCALIZATION_CHANNEL_LABELS), lift_width, bounded=True, seed=seed + 9
    )
    return AliasFreeConvolutional(lift, composition, projection, reference_density, gram_mean, gram_scale)


def Random_Diamond_Operation(generator: np.random.Generator) -> tuple[NDArray[np.int64], NDArray[np.float64]]:
    """one of the 48 exact diamond grid operations, drawn uniformly by the given generator"""
    operations = Diamond_Grid_Operations()
    return operations[int(generator.integers(len(operations)))]


def Augmented_Training_Pair(
    input_values: NDArray[np.float64], target_values: NDArray[np.float64], generator: np.random.Generator
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """one exact grid symmetry, drawn once and applied identically to the input and its own target"""
    matrix, translation = Random_Diamond_Operation(generator)
    augmented_input = Apply_Grid_Operation(input_values, matrix, translation)
    augmented_target = Apply_Grid_Operation(target_values, matrix, translation)
    return augmented_input, augmented_target
