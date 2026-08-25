"""Schemes for chaining layers, each owning its topology and its backward pass."""

from __future__ import annotations

from abc import ABC, abstractmethod

from operators.framework.representation import Coefficients, Representation


class Composition(ABC):
    """Applies a scheme's layers to a representation in channel space."""


    @abstractmethod
    def Apply(
        self,
        input_function: Representation,
        condition: Coefficients | None = None,
    ) -> Representation:
        raise NotImplementedError
