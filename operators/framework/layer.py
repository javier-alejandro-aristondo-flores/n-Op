"""One layer of the iterated transform: kernel integral + local linear term + activation.

Concrete and deliberately permissive — the residual flag and gating live here so that
DeepDFT's interaction blocks fit without abstract-class surgery. The activation is a mode,
not a class: ``pointwise`` is the default; ``alias_free`` applies the nonlinearity at a
doubled sampling rate with filtered resampling around it (the convolutional operator's
identity — and its fused kernel is the one place naive autodiff runs out of memory, so the
mode is declared here and implemented beside the kernels that need it).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from operators.framework.kernel import Kernel


@dataclass
class Layer:
    """activation( local_linear(v) + kernel.integrate(v) ), optionally residual."""

    kernel: Kernel
    local_linear: object  # pointwise linear map; typed when the backend lands
    activation: Literal["pointwise", "alias_free"] = "pointwise"
    residual: bool = False
