"""(Charge density, local potential) → electron localization field.

The multiple-input operator network: Jin, Meng, Lu — SIAM Journal on Scientific Computing
44(6), A3490 (2022). Two branches, one for each input field, combined multiplicatively in the
latent space, read out by the shared trunk. Rides the Deep Operator Network stack; kept as
its own package because it is its own literature name with its own kill rule (if adding the
potential improves nothing over density alone, the task is dropped). test-suite.md §3,
entry II.2.
"""

from operators.framework import NeuralOperator


class MultipleInputOperatorNetwork(NeuralOperator):
    """The assembly. Parts and their settings are fixed in the implementation phase."""

    def __init__(self) -> None:
        raise NotImplementedError("implementation phase — see IMPLEMENTATION.md")
