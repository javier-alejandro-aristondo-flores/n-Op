"""The kernel of the integral transform, fused with its own integration."""

from abc import abstractmethod
from typing import ClassVar, Protocol

from operators.framework.domain import Discretization
from operators.framework.inspectable import Inspectable
from operators.framework.representation import Coefficients, Representation


class Kernel[In: Representation, Out: Representation](Inspectable, Protocol):
    """Integrates a learned kernel against the quadrature of a representation."""

    supported_representations: ClassVar[tuple[type[Representation], ...]]


    @abstractmethod
    def Integrate(
        self,
        input_function: In,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> Out: ...
