"""cheap-functional charge density to accurate-functional charge density"""

import dataclasses
from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.data import Gram_Pod, PodBasis, Project
from operators.deep_operator_network import Pointwise_Statistics
from operators.encoders import BasisProjectionEncoder, SensorEncoder
from operators.framework import Array, Coefficients, Discretization, GridFunction, Operator
from operators.readouts import PointwiseStandardizedExpansion
from operators.wrappers import Channel_Means, Conserving, Residual

BASIS_RANK = 32
BRANCH_HIDDEN_WIDTHS = (128, 128)


def Zero_Anchored(basis: PodBasis) -> PodBasis:
    """the same modes and singular values, with the ensemble mean forced through the origin"""
    return dataclasses.replace(basis, mean=np.zeros_like(basis.mean))


def Last_Layer_Zeroed(branch: SensorEncoder) -> None:
    """the branch's final weights and biases replaced by zeros, so an untrained branch outputs zero everywhere"""
    prefix = branch.network.name_prefix
    last_layer_index = len(branch.network.layer_widths) - 2
    weight_name = f"{prefix}_layer_{last_layer_index}_weights"
    bias_name = f"{prefix}_layer_{last_layer_index}_biases"
    branch.parameter_values[weight_name] = np.zeros_like(branch.parameter_values[weight_name])
    branch.parameter_values[bias_name] = np.zeros_like(branch.parameter_values[bias_name])


def Guarded_Spread(values: NDArray[np.float64]) -> NDArray[np.float64]:
    """each column's own standard deviation across a training block, spread guarded away from zero"""
    spread = np.asarray(values.std(axis=0), dtype=np.float64)
    spread[spread == 0.0] = 1.0
    return spread


class ProjectionBackbone(Operator[GridFunction, GridFunction]):
    """the cheap density projected onto a fixed basis and read through a zero-initialized branch"""


    def __init__(
        self,
        cheap_basis: PodBasis,
        correction_basis: PodBasis,
        grid_shape: tuple[int, int, int],
        voxel_scale: NDArray[np.float64],
        input_scale: NDArray[np.float64],
        seed: int = 0,
    ) -> None:
        self.cheap_basis = cheap_basis
        self.correction_basis = correction_basis
        self.encoder = BasisProjectionEncoder(cheap_basis.modes, cheap_basis.mean)
        cheap_rank = int(cheap_basis.modes.shape[0])
        correction_rank = int(correction_basis.modes.shape[0])
        self.branch = SensorEncoder((cheap_rank, *BRANCH_HIDDEN_WIDTHS, correction_rank), seed=seed)
        Last_Layer_Zeroed(self.branch)
        # a residual's natural reference is zero, not the corpus's own average correction shape
        self.operational_basis = Zero_Anchored(correction_basis)
        self.input_scale = input_scale
        self.readout = PointwiseStandardizedExpansion(
            self.operational_basis, grid_shape, np.zeros_like(voxel_scale), voxel_scale
        )


    def Forward_Correction(self, lifted: dict[str, Any], cheap_coefficients: Any) -> Any:
        """the raw predicted correction, a leading batch axis carrying each pair's own field"""
        standardized_input = cheap_coefficients / lifted["input_scale"]
        branch_output = self.branch.Forward(lifted, standardized_input)
        raw_correction = self.readout.Forward(
            lifted,
            branch_output,
            lifted["readout_basis_modes"],
            lifted["readout_basis_mean"],
            lifted["readout_voxel_mean"],
            lifted["readout_voxel_scale"],
        )
        # the batch axis stands in for the channel axis Channel_Means was written for, each
        # pair losing only its own mean, exactly the zero-mean law applied one field at a time
        return raw_correction - Channel_Means(raw_correction)


    def Parameter_Values(self) -> dict[str, NDArray[np.float64]]:
        """the branch's and the readout's own trained arrays, under one namespace"""
        collected = dict(self.branch.parameter_values)
        collected.update(self.readout.parameter_values)
        return collected


    def Constant_Values(self) -> dict[str, NDArray[np.float64]]:
        """every fixed array Forward_Correction reads by name, lifted once and reused every step"""
        return {
            "input_scale": self.input_scale,
            "readout_basis_modes": self.operational_basis.modes,
            "readout_basis_mean": self.operational_basis.mean,
            "readout_voxel_mean": self.readout.voxel_mean,
            "readout_voxel_scale": self.readout.voxel_scale,
        }


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        sensed = self.encoder(input_function, output_discretization, condition)
        standardized_vector = np.asarray(sensed.vector, dtype=np.float64) / self.input_scale
        branch_output = self.branch(
            Coefficients(vector=standardized_vector, domain=sensed.domain), output_discretization, condition
        )
        return self.readout(branch_output, output_discretization, condition)


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = {f"encoder.{name}": value for name, value in self.encoder.Inspect().items()}
        state.update({f"branch.{name}": value for name, value in self.branch.Inspect().items()})
        state.update({f"readout.{name}": value for name, value in self.readout.Inspect().items()})
        state["input_scale"] = self.input_scale
        return state


class ResidualCorrection(Operator[GridFunction, GridFunction]):
    """a projection backbone wrapped in exact zero-mean conservation and a residual connection"""


    def __init__(self, backbone: ProjectionBackbone) -> None:
        self.backbone = backbone
        self.conserving = Conserving(backbone, law="zero_mean")
        self.residual = Residual(self.conserving)
        # a fixed record of how this instance began, kept regardless of how far training moves it
        self.zero_initialized_at_construction = True
        self.last_correction_scale: NDArray[np.float64] | None = None


    def Forward_Correction(self, lifted: dict[str, Any], cheap_coefficients: Any) -> Any:
        """the conserved correction alone, differentiable through whichever engine lifted the dict"""
        return self.backbone.Forward_Correction(lifted, cheap_coefficients)


    def Parameter_Values(self) -> dict[str, NDArray[np.float64]]:
        """every trained array the backbone owns, ready for the trainer"""
        return self.backbone.Parameter_Values()


    def Constant_Values(self) -> dict[str, NDArray[np.float64]]:
        """every fixed array Forward_Correction reads by name, ready for the trainer to lift once"""
        return self.backbone.Constant_Values()


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        corrected = self.residual(input_function, output_discretization, condition)
        # exact subtraction recovers the correction without a second pass through the backbone
        correction_values = np.asarray(corrected.values, dtype=np.float64) - np.asarray(
            input_function.values, dtype=np.float64
        )
        self.last_correction_scale = np.asarray(float(np.linalg.norm(correction_values)))
        return corrected


    def Inspect(self) -> dict[str, Array]:
        """every part's own arrays under a prefix, plus the member-level record of how it started"""
        state: dict[str, Array] = {f"backbone.{name}": value for name, value in self.backbone.Inspect().items()}
        if self.conserving.last_removed_mean is not None:
            state["conservation.last_removed_mean"] = self.conserving.last_removed_mean
        state["cheap_basis_singular_values"] = self.backbone.cheap_basis.singular_values
        state["correction_basis_singular_values"] = self.backbone.correction_basis.singular_values
        state["zero_initialized_at_construction"] = np.asarray(self.zero_initialized_at_construction)
        if self.last_correction_scale is not None:
            state["last_correction_scale"] = self.last_correction_scale
        return state


def Projection_Backbone_Member(
    cheap_training_fields: NDArray[np.float64],
    correction_training_fields: NDArray[np.float64],
    grid_shape: tuple[int, int, int],
    seed: int = 0,
) -> ResidualCorrection:
    """the wave-1 member, its bases and statistics fit from one training block's flattened fields"""
    cheap_basis = Gram_Pod(cheap_training_fields, rank=BASIS_RANK)
    correction_basis = Gram_Pod(correction_training_fields, rank=BASIS_RANK)
    _, voxel_scale = Pointwise_Statistics(correction_training_fields)
    input_scale = Guarded_Spread(Project(cheap_basis, cheap_training_fields))
    backbone = ProjectionBackbone(cheap_basis, correction_basis, grid_shape, voxel_scale, input_scale, seed)
    return ResidualCorrection(backbone)
