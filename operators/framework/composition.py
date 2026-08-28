"""schemes for chaining layers, each owning its topology and backward pass"""

from abc import abstractmethod
from typing import Protocol

from operators.framework.inspectable import Inspectable
from operators.framework.representation import Coefficients, Representation


class Composition[State: Representation](Inspectable, Protocol):
    """a scheme's layers applied to a representation in channel space"""


    @abstractmethod
    def Apply(
        self,
        input_function: State,
        condition: Coefficients | None = None,
    ) -> State: ...
