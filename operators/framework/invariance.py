"""Measurement of how far an operator's output moves when its discretization changes."""

from operators.framework.operator import Operator
from operators.framework.representation import Representation
from operators.tasks import TaskCard


def Discretization_Invariance_Report[In: Representation, Out: Representation](
    operator: Operator[In, Out],
    task: TaskCard,
) -> dict[str, object]:
    """Runs every invariance axis that applies to one operator on one task card."""
    raise NotImplementedError
