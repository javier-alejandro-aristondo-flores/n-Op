"""Strain or lattice parameters → charge density field (and, by projection, density →
electron localization field).

The Deep Operator Network: Lu, Jin, Pang, Zhang, Karniadakis — Nature Machine Intelligence
3, 218 (2021). The cheapest build in the suite — no Fourier transforms, no convolutions, no
attention — and the designated interface shakedown together with the correction operator.
test-suite.md §3, entry II.1.

Assembly: sensor encoder (the branch) → dense layers on coefficients (zero kernel-integral
layers — legitimate) → basis-expansion readout (the trunk, integer-frequency Fourier
features, exact periodicity, queryable at any point).

Named configurations in ``configs/``: canonical; proper-orthogonal (fixed output basis from
the training fields); principal-component (fixed bases both sides); energy-trunk (the trunk
runs over energy instead of position — structure or strain → density-of-states curve).
"""

from operators.framework import NeuralOperator


class DeepOperatorNetwork(NeuralOperator):
    """The assembly. Parts and their settings are fixed in the implementation phase."""

    def __init__(self) -> None:
        raise NotImplementedError("implementation phase — see IMPLEMENTATION.md")
