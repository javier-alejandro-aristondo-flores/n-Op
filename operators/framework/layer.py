"""one layer of the iterated transform"""

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Literal, Protocol

import numpy as np
from numpy.typing import NDArray

from operators.framework.domain import Discretization
from operators.framework.inspectable import Inspectable
from operators.framework.representation import Coefficients, Representation

type Activation = Literal["pointwise", "alias_free"]


class LiftedKernel[In: Representation, Out: Representation](Inspectable, Protocol):
    """a kernel reachable through the lifted forward, differentiable on whichever engine lifted it"""

    parameter_values: dict[str, NDArray[np.float64]]


    @abstractmethod
    def Integrate(
        self,
        input_function: In,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> Out: ...


    @abstractmethod
    def Forward(self, lifted: dict[str, Any], input_values: Any, output_shape: tuple[int, int, int]) -> Any: ...


class LocalLinearMap(Inspectable, Protocol):
    """the layer's own weight-times-value term, learned and reachable through the lifted forward"""

    parameter_values: dict[str, NDArray[np.float64]]


    @abstractmethod
    def Forward(self, lifted: dict[str, Any], input_values: Any) -> Any: ...


@dataclass(slots=True)
class Layer[State: Representation]:
    """an activation over the sum of a local linear map and a kernel integral"""

    kernel: LiftedKernel[State, State]
    local_linear: LocalLinearMap
    activation: Activation = "pointwise"
    residual: bool = False
