"""The root interface, and the template chaining encoder, composition, and readout."""

from __future__ import annotations

from abc import ABC, abstractmethod

from operators.framework.composition import Composition
from operators.framework.domain import Discretization
from operators.framework.representation import Coefficients, Representation


class Operator(ABC):
    """Maps one representation to another, evaluated on a requested discretization."""


    @abstractmethod
    def __call__(
        self,
        input_function: Representation,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> Representation:
        raise NotImplementedError


class NeuralOperator(Operator):
    """An operator assembled from an encoder, a composition of layers, and a readout."""


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
        input_function: Representation,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> Representation:
        raise NotImplementedError
