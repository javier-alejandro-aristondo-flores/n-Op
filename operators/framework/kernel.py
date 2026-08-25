"""The kernel of the integral transform, fused with its own integration."""

from __future__ import annotations

from abc import ABC, abstractmethod

from operators.framework.domain import Discretization
from operators.framework.representation import Coefficients, Representation


class Kernel(ABC):
    """Integrates a learned kernel against the quadrature of a representation."""

    supported_representations: tuple[type[Representation], ...]


    @abstractmethod
    def Integrate(
        self,
        input_function: Representation,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> Representation:
        raise NotImplementedError
