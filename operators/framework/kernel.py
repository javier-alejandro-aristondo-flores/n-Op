"""the kernel of the integral transform, fused with its own integration"""

from abc import abstractmethod
from typing import ClassVar, Protocol

from operators.framework.domain import Discretization
from operators.framework.inspectable import Inspectable
from operators.framework.representation import Coefficients, Representation


class Kernel[In: Representation, Out: Representation](Inspectable, Protocol):
    """a learned kernel integrated against a representation's quadrature"""

    supported_representations: ClassVar[tuple[type[Representation], ...]]


    @abstractmethod
    def Integrate(
        self,
        input_function: In,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> Out: ...
