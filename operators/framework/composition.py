"""Schemes for chaining layers, each owning its topology and its backward pass."""

from abc import abstractmethod
from typing import Protocol

from operators.framework.inspectable import Inspectable
from operators.framework.representation import Coefficients, Representation


class Composition[R: Representation](Inspectable, Protocol):
    """Applies a scheme's layers to a representation in channel space."""


    @abstractmethod
    def Apply(
        self,
        input_function: R,
        condition: Coefficients | None = None,
    ) -> R: ...
