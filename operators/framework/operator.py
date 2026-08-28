"""The root interface, and the template chaining encoder, composition, and readout."""

from abc import abstractmethod
from typing import Protocol

from operators.framework.composition import Composition
from operators.framework.domain import Array, Discretization
from operators.framework.inspectable import Inspectable
from operators.framework.representation import Coefficients, Representation


class Operator[In: Representation, Out: Representation](Inspectable, Protocol):
    """Maps one representation to another, evaluated on a requested discretization."""


    @abstractmethod
    def __call__(
        self,
        input_function: In,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> Out: ...


class NeuralOperator[In: Representation, Hidden: Representation, Out: Representation](Operator[In, Out]):
    """An operator assembled from an encoder, a composition of layers, and a readout."""


    def __init__(
        self,
        encoder: Operator[In, Hidden],
        composition: Composition[Hidden],
        readout: Operator[Hidden, Out],
    ) -> None:
        self.encoder = encoder
        self.composition = composition
        self.readout = readout


    def __call__(
        self,
        input_function: In,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> Out:
        raise NotImplementedError


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = {}
        for prefix, inspected in (
            ("encoder", self.encoder.Inspect()),
            ("composition", self.composition.Inspect()),
            ("readout", self.readout.Inspect()),
        ):
            for name, value in inspected.items():
                state[f"{prefix}.{name}"] = value
        return state
