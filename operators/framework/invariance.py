"""The discretization-invariance harness — framework-level, run against every operator.

Discretization invariance is the operator claim, so it is tested once, here, not privately
per architecture. The axes come from test-suite.md §9.5 and each carries its null:

    resolution   train coarse (Fourier truncation, never strided subsampling — that
                 aliases), evaluate fine; null = trigonometric upsampling of the coarse truth
    supercell    the 2-atom ↔ 64-atom twin shear grid; null = the measured block gap between
                 the two campaigns' own truths
    size         the held-out alloy cells; score = skill against the superposed-atomic-
                 densities floor
    symmetry     the 48 exact grid operations of the diamond group; report the median
                 equivariance error, plus a symmetrized-inference ablation line
"""

from __future__ import annotations

from operators.framework.operator import Operator


def discretization_invariance_report(operator: Operator, task: object) -> dict:
    """Run every applicable invariance axis for one operator on one task card."""
    raise NotImplementedError("implementation phase")
