"""a per-mode Lipschitz budget, its post-step clip and its differentiable normalized counterpart"""

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.framework import Array
from operators.kernels.spectral import AXIS_NAMES
from operators.substrate import (
    Clipped_Above,
    Complex_From_Parts,
    Largest_Singular_Values,
    Largest_Singular_Values_Of_Stack,
    Singular_Values_Clipped,
)
from operators.training import TrainingProgress

# the smooth activation's own slope supremum (GELU), the constant the per-mode lipschitz bound is stated in terms of
GELU_LIPSCHITZ_SLOPE = 1.129

# the separable kernel's own three factor stems, in the names operators.kernels.spectral.SpectralKernel stores them
STEM_NAMES = tuple(f"{axis_name}_mode_weights" for axis_name in AXIS_NAMES)


@dataclass(frozen=True, slots=True)
class ContractionBudget:
    """the target Lipschitz constant split between the local matrix and the separable kernel's own three factors"""

    target_lipschitz: float = 0.9
    local_share: float = 0.2


    def Local_Bound(self) -> float:
        """the spectral-norm ceiling the local matrix alone carries, GELU's own slope divided back out"""
        return self.local_share * self.target_lipschitz / GELU_LIPSCHITZ_SLOPE


    def Mode_Bound(self, factor_count: int) -> float:
        """the spectral-norm ceiling every one of a separable kernel's own factors carries, split equally"""
        if factor_count < 1:
            raise ValueError(f"a separable kernel needs at least one factor to bound, not {factor_count}")
        return (1.0 - self.local_share) * self.target_lipschitz / (GELU_LIPSCHITZ_SLOPE * factor_count)


def Local_Matrix_Name(prefix: str) -> str:
    """the flat name a shared layer's own local matrix answers to under a composition's own prefix"""
    return f"{prefix}local_linear.lift_weights"


def Stem_Real_Imaginary_Names(prefix: str, stem: str) -> tuple[str, str]:
    """the flat names one separable factor's own stored halves answer to under a composition's own prefix"""
    return f"{prefix}kernel.{stem}_real", f"{prefix}kernel.{stem}_imaginary"


def Complex_Stem(parameters: dict[str, NDArray[np.float64]], prefix: str, stem: str) -> NDArray[np.complex128]:
    """one separable factor's stored halves read back off a flat parameter dict as the complex array they stand for"""
    real_name, imaginary_name = Stem_Real_Imaginary_Names(prefix, stem)
    return np.asarray(parameters[real_name] + 1j * parameters[imaginary_name], dtype=np.complex128)


def Nominal_Lipschitz(parameters: dict[str, NDArray[np.float64]], prefix: str = "") -> float:
    """1.129 times the local matrix's own spectral norm plus every factor's own worst slice, the layer's own bound"""
    local_norm = float(Largest_Singular_Values_Of_Stack(parameters[Local_Matrix_Name(prefix)]))
    factor_total = sum(
        float(np.max(Largest_Singular_Values_Of_Stack(Complex_Stem(parameters, prefix, stem))))
        for stem in STEM_NAMES
    )
    return GELU_LIPSCHITZ_SLOPE * (local_norm + factor_total)


class ContractionProjection:
    """a training hook clipping the shared layer's local matrix and every kernel factor slice to a Lipschitz budget"""


    def __init__(self, layer: Any, budget: ContractionBudget, prefix: str = "") -> None:
        kernel = layer.kernel
        if not hasattr(kernel, "mode_mixing") or not hasattr(kernel, "metric_aware"):
            raise TypeError("the contraction projection only understands a spectral kernel's own stored factors")
        if kernel.metric_aware:
            raise ValueError("a metric-aware kernel's gain is unbounded, so the contraction projection refuses it")
        if kernel.mode_mixing != "separable":
            raise ValueError("the per-factor Lipschitz bound is stated for the separable kernel form alone")
        self.layer = layer
        self.budget = budget
        self.prefix = prefix
        self.local_bound = budget.Local_Bound()
        self.mode_bound = budget.Mode_Bound(len(STEM_NAMES))
        self.last_local_pre_clip_norm: float | None = None
        self.last_mode_pre_clip_norms: dict[str, NDArray[np.float64]] | None = None
        self.last_clipped_fraction: float | None = None
        self.last_nominal_lipschitz: float | None = None


    def After_Step(self, progress: TrainingProgress) -> None:
        """the exact per-slice euclidean clip, applied to the live parameters right after the step that grew them"""
        values = progress.parameters.values
        local_name = Local_Matrix_Name(self.prefix)
        local_matrix = values[local_name]
        local_pre_clip_norm = float(Largest_Singular_Values_Of_Stack(local_matrix))
        clipped_local = Singular_Values_Clipped(local_matrix, self.local_bound)
        values[local_name] = np.asarray(clipped_local, dtype=local_matrix.dtype)

        clipped_count = int(local_pre_clip_norm > self.local_bound)
        total_count = 1
        mode_pre_clip_norms: dict[str, NDArray[np.float64]] = {}
        for stem in STEM_NAMES:
            real_name, imaginary_name = Stem_Real_Imaginary_Names(self.prefix, stem)
            complex_stem = Complex_Stem(values, self.prefix, stem)
            pre_clip_norms = Largest_Singular_Values_Of_Stack(complex_stem)
            mode_pre_clip_norms[stem] = pre_clip_norms
            clipped_stem = Singular_Values_Clipped(complex_stem, self.mode_bound)
            values[real_name] = np.ascontiguousarray(np.real(clipped_stem)).astype(values[real_name].dtype)
            values[imaginary_name] = np.ascontiguousarray(np.imag(clipped_stem)).astype(values[imaginary_name].dtype)
            clipped_count += int(np.sum(pre_clip_norms > self.mode_bound))
            total_count += int(pre_clip_norms.size)

        self.last_local_pre_clip_norm = local_pre_clip_norm
        self.last_mode_pre_clip_norms = mode_pre_clip_norms
        self.last_clipped_fraction = clipped_count / total_count
        self.last_nominal_lipschitz = Nominal_Lipschitz(values, self.prefix)


    def After_Validation(self, progress: TrainingProgress) -> dict[str, float]:
        """the projection's own diagnostics, curved beside the run's loss once every validation pass"""
        if self.last_nominal_lipschitz is None or self.last_clipped_fraction is None:
            return {}
        return {
            "nominal_lipschitz": self.last_nominal_lipschitz,
            "clipped_fraction": self.last_clipped_fraction,
        }


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = {
            "local_bound": np.asarray(self.local_bound),
            "mode_bound": np.asarray(self.mode_bound),
        }
        if self.last_local_pre_clip_norm is not None:
            state["last_local_pre_clip_norm"] = np.asarray(self.last_local_pre_clip_norm)
        if self.last_mode_pre_clip_norms is not None:
            for stem, norms in self.last_mode_pre_clip_norms.items():
                state[f"last_{stem}_pre_clip_norms"] = norms
        if self.last_clipped_fraction is not None:
            state["last_clipped_fraction"] = np.asarray(self.last_clipped_fraction)
        if self.last_nominal_lipschitz is not None:
            state["last_nominal_lipschitz"] = np.asarray(self.last_nominal_lipschitz)
        return state


def Spectral_Norm_Scale(value: Any, ceiling: float) -> Any:
    """the per-slice scale bringing value's own largest singular value under the ceiling, differentiable, one or less"""
    sigma = Largest_Singular_Values(value)
    # a near-zero slice has nothing to normalize, and the floor keeps the divide finite rather than undefined
    return Clipped_Above(sigma, ceiling) / (sigma + 1e-12)


def Normalized_Local_Linear_Lifted(local_linear_lifted: dict[str, Any], budget: ContractionBudget) -> dict[str, Any]:
    """the local matrix rescaled toward the budget's own share inside the forward pass, its bias left untouched"""
    scale = Spectral_Norm_Scale(local_linear_lifted["lift_weights"], budget.Local_Bound())
    normalized = dict(local_linear_lifted)
    normalized["lift_weights"] = local_linear_lifted["lift_weights"] * scale[..., None, None]
    return normalized


def Normalized_Kernel_Lifted(kernel_lifted: dict[str, Any], budget: ContractionBudget) -> dict[str, Any]:
    """every separable factor's own slices rescaled toward the budget's own per-factor share, once per forward"""
    mode_bound = budget.Mode_Bound(len(STEM_NAMES))
    normalized = dict(kernel_lifted)
    for stem in STEM_NAMES:
        real_name, imaginary_name = f"{stem}_real", f"{stem}_imaginary"
        complex_stem = Complex_From_Parts(kernel_lifted[real_name], kernel_lifted[imaginary_name])
        scale = Spectral_Norm_Scale(complex_stem, mode_bound)
        broadcast_scale = scale[..., None, None]
        normalized[real_name] = kernel_lifted[real_name] * broadcast_scale
        normalized[imaginary_name] = kernel_lifted[imaginary_name] * broadcast_scale
    return normalized
