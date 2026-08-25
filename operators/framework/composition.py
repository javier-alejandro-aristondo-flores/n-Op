"""How layers chain. Each implementation owns its topology and its backward strategy.

    explicit stack   a chain of distinct layers — the default
    weight-tied      one layer applied a fixed number of times
    fixed point      one layer applied until the output stops changing; carries a solver
                     (Anderson acceleration) and its own differentiation rule (phantom
                     gradients or the implicit-function adjoint) — state the chain rule
                     cannot see, which is why composition is a class and not a for-loop
    multi-scale      a U-shaped directed graph with skip connections and filtered
                     resampling between scales; designates which scale the output leaves at

"Topology-owning" is load-bearing: the multi-scale composition is not a chain, and the base
class must not assume one.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from operators.framework.representation import Coefficients, Representation


class Composition(ABC):
    """Apply this composition's layers to a channel-space representation."""

    @abstractmethod
    def apply(
        self,
        v: Representation,
        condition: Coefficients | None = None,
    ) -> Representation:
        raise NotImplementedError
