"""The root interface, and the template that assembles the anatomy.

Everything that maps a function object to a function object is an ``Operator`` — the
assembled neural operators, but also every encoder, every readout, and every wrapper. That
one interface is why encoders and readouts need no abstract classes of their own.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from operators.framework.composition import Composition
from operators.framework.domain import Discretization
from operators.framework.representation import Coefficients, Representation


class Operator(ABC):
    """input Representation → output Representation, evaluated where the caller asks.

    ``condition`` threads per-sample covariates (functional identity, exact-exchange
    fraction, strain parameters when they condition rather than drive) through the whole
    assembly: encoders may concatenate it, layers may modulate on it, wrappers may read it.
    It is in the root signature because two of the eight operators need it in two different
    ways, and every implementer would otherwise rediscover the hole.
    """

    @abstractmethod
    def __call__(
        self,
        v: Representation,
        out: Discretization,
        condition: Coefficients | None = None,
    ) -> Representation:
        raise NotImplementedError


class NeuralOperator(Operator):
    """The template: encoder → composition of layers → readout.

    encoder and readout are themselves Operators (pointwise lift, sensor encoder, basis
    projection, atom embedding, variable encoding; pointwise projection, basis expansion,
    nonlinear decoder). ``composition`` may hold zero layers — the parametric branch–trunk
    operators are encoder → dense layers → basis readout, and forcing a fake integral into
    them would be dishonest.
    """

    def __init__(
        self,
        encoder: Operator,
        composition: Composition,
        readout: Operator,
    ) -> None:
        self.encoder = encoder
        self.composition = composition
        self.readout = readout

    def __call__(
        self,
        v: Representation,
        out: Discretization,
        condition: Coefficients | None = None,
    ) -> Representation:
        raise NotImplementedError("assembled in the implementation phase")
