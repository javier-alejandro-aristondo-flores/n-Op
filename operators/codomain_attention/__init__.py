"""Any subset of the fields → the missing fields.

The codomain-attention operator: Rahman, George, Elleithy, Leibovici, Li, Bonev, White,
Berner, Yeh, Kossaifi, Azizzadenesheli, Anandkumar — NeurIPS 2024 (arXiv:2403.12553).
Tokens are whole fields, not grid points: give it density and potential, it returns the
localization field; give it density alone, it returns the potential. The attention map is at
most eight by eight — the corpus's variable channel sets (five to eight under the spin-block
law) are this operator's selling point being tested, and only a variable-channel model can
consume the density-only campaigns as extra training material. Trained by masking fields and
reconstructing them; the alloy campaign is held out entirely as the transfer test.
test-suite.md §6, entry V.1.
"""

from operators.framework import NeuralOperator


class CodomainAttention(NeuralOperator):
    """The assembly. Parts and their settings are fixed in the implementation phase."""

    def __init__(self) -> None:
        raise NotImplementedError("implementation phase — see IMPLEMENTATION.md")
