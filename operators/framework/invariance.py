"""Measurement of how far an operator's output moves when its discretization changes."""

from __future__ import annotations

from operators.framework.operator import Operator


def Discretization_Invariance_Report(operator: Operator, task: object) -> dict:
    """Runs every invariance axis that applies to one operator on one task card."""
    raise NotImplementedError
