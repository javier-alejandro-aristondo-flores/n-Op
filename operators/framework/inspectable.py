"""the inspection contract, one dictionary of named arrays per part"""

from abc import abstractmethod
from typing import Protocol

from operators.framework.domain import Array


class Inspectable(Protocol):
    """learned arrays and last-forward intermediates under plain-word names"""


    @abstractmethod
    def Inspect(self) -> dict[str, Array]: ...
