"""The inspection contract: every part exposes its state as named plain-word arrays."""

from abc import abstractmethod
from typing import Protocol

from operators.framework.domain import Array


class Inspectable(Protocol):
    """Exposes learned arrays and last-forward intermediates under plain-word names."""


    @abstractmethod
    def Inspect(self) -> dict[str, Array]: ...
