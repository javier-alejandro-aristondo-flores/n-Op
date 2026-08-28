"""One layer of the iterated transform."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from operators.framework.domain import Array
from operators.framework.kernel import Kernel
from operators.framework.representation import Representation

type Activation = Literal["pointwise", "alias_free"]


@dataclass(slots=True)
class Layer[State: Representation]:
    """Applies an activation to the sum of a local linear map and a kernel integral."""

    kernel: Kernel[State, State]
    local_linear: Callable[[Array], Array]
    activation: Activation = "pointwise"
    residual: bool = False
