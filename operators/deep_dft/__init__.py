"""Atomic structure → charge density field (and magnetization), queryable anywhere.

DeepDFT: Jørgensen & Bhowmik — npj Computational Materials 8, 183 (2022). The
structure-to-field anchor: atoms exchange messages, and probe points anywhere in the cell
join the graph as receive-only vertices — the layer state is one point set (atoms and
probes together, distinguished by roles), which is what forced the point-set representation
merge. The two-channel (density, magnetization) head is this suite's one honest novelty over
the literature. PaiNN-style vector features are the recorded stretch upgrade.
test-suite.md §4, entry III.1.
"""

from operators.framework import NeuralOperator


class DeepDft(NeuralOperator):
    """The assembly. Parts and their settings are fixed in the implementation phase."""

    def __init__(self) -> None:
        raise NotImplementedError("implementation phase — see IMPLEMENTATION.md")
