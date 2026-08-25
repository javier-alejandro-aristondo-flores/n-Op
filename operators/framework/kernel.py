"""The learned kernel and its fused integration — the one part where the operators differ.

A kernel owns two inseparable things: the learned function κ and the fast algorithm that
integrates it against the measures it supports. The pairing is the architecture:

    spectral            translation-invariant κ × uniform grid   → multiply in Fourier space
    compact support     small-support κ × uniform grid           → convolution
                        small-support κ × point set              → message passing
    low rank            κ(x,y) = Σ_j φ_j(x)·ψ_j(y) × any measure → inner products (universal)
    codomain attention  κ over the channel index                 → tiny attention map
    dense               κ over a finite index set                → matrix multiply

An abstract "Integral" in this forward path would either re-dispatch to these same fused
routines or permit arbitrary kernel-measure pairs at O(N·M) cost. Instead the measure is data
on the representation, and the dense O(N·M) evaluation lives once, in
``framework/integral.py``, as the correctness oracle: every implementation of this class must
match it on small problems before it is trusted at size.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from operators.framework.domain import Discretization
from operators.framework.representation import Coefficients, Representation


class Kernel(ABC):
    """∫ κ(x, y) · v(y) · dν(y), fused with the measures this kernel declares support for.

    ``supported_representations`` names the concrete Representation types this kernel's fast
    path accepts; handing it anything else is an error, never a silent slow path.
    """

    supported_representations: tuple[type[Representation], ...]

    @abstractmethod
    def integrate(
        self,
        v: Representation,
        out: Discretization,
        condition: Coefficients | None = None,
    ) -> Representation:
        raise NotImplementedError
