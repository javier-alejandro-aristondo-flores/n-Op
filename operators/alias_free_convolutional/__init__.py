"""Charge density → electron localization field (and → local potential; defect fields).

The alias-free convolutional operator: Raonić, Molinaro, De Ryck, Rohner, Bartolucci,
Alaifari, Mishra, de Bézenac — *Convolutional Neural Operators for robust and accurate
learning of PDEs*, NeurIPS 2023. The hedge against the Fourier lineage's ringing near sharp
features; no three-dimensional version exists in the literature — producing one is part of
this entry's value. test-suite.md §2, entry I.2.

Assembly: pointwise lift → multi-scale composition (U-shaped, filtered resampling, output at
the coarse scale per the half-grid law) of compact-support-kernel layers with the alias-free
activation mode → pointwise projection.
"""

from operators.framework import NeuralOperator


class AliasFreeConvolutional(NeuralOperator):
    """The assembly. Parts and their settings are fixed in the implementation phase."""

    def __init__(self) -> None:
        raise NotImplementedError("implementation phase — see IMPLEMENTATION.md")
