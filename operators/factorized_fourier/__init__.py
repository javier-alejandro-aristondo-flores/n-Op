"""Charge density → electron localization field (and → local potential).

The factorized Fourier operator: Tran, Mathews, Xie, Ong — *Factorized Fourier Neural
Operators*, ICLR 2023 (parent architecture: Li et al., ICLR 2021). The suite flagship;
test-suite.md §2, entry I.1.

Assembly: pointwise lift → spectral resample to the coarse grid ("truncate-early") →
explicit stack of spectral-kernel layers (factorized per-axis mode weights, full coarse
Nyquist) → pointwise projection with the bounded electron-localization head. The
deep-equilibrium variant is this same assembly with the fixed-point composition — a
configuration, not another package.
"""

from operators.framework import NeuralOperator


class FactorizedFourier(NeuralOperator):
    """The assembly. Parts and their settings are fixed in the implementation phase."""

    def __init__(self) -> None:
        raise NotImplementedError("implementation phase — see IMPLEMENTATION.md")
