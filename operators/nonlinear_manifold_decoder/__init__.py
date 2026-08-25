"""Strain or lattice parameters → charge density field, decoded point by point.

The nonlinear manifold decoder: Seidman, Kissas, Perdikaris, Pappas — NeurIPS 2022
(arXiv:2206.03551). Same entrance as the Deep Operator Network, but the output is a
nonlinear function of (latent, position) rather than a linear combination of basis
functions — the one readout in the suite that is not an integral, and the reason readouts
are plain Operators. Earns its operator badge on grid transfer: error inflation at most 1.3×
on the strain data's off-dominant grids. test-suite.md §3, entry II.3.
"""

from operators.framework import NeuralOperator


class NonlinearManifoldDecoder(NeuralOperator):
    """The assembly. Parts and their settings are fixed in the implementation phase."""

    def __init__(self) -> None:
        raise NotImplementedError("implementation phase — see IMPLEMENTATION.md")
