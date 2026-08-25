"""One layer of the iterated transform."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from operators.framework.kernel import Kernel


@dataclass
class Layer:
    """Applies an activation to the sum of a local linear map and a kernel integral."""

    kernel: Kernel
    local_linear: object
    activation: Literal["pointwise", "alias_free"] = "pointwise"
    residual: bool = False
