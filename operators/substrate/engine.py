"""The differentiation facet: named parameters in, a scalar loss out, gradients back."""

from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

import numpy
from numpy.typing import NDArray


@dataclass(frozen=True, slots=True)
class ParameterSet:
    """Named parameter values held canonically as double-precision numpy arrays."""

    values: dict[str, NDArray[numpy.float64]]


class Engine(Protocol):
    """Evaluates and differentiates a forward computation over named parameters."""


    @abstractmethod
    def Evaluate(self, parameters: ParameterSet, forward: Callable[[dict[str, Any]], Any]) -> float: ...


    @abstractmethod
    def Gradients(
        self, parameters: ParameterSet, forward: Callable[[dict[str, Any]], Any]
    ) -> dict[str, NDArray[numpy.float64]]: ...


    @abstractmethod
    def Lift_Constant(self, value: NDArray[numpy.float64]) -> Any: ...


class NumpyEngine:
    """The reference engine: plain-array forwards, gradients by central differences."""


    def __init__(self, step_size: float = 1e-6) -> None:
        self.step_size = step_size


    def Evaluate(self, parameters: ParameterSet, forward: Callable[[dict[str, Any]], Any]) -> float:
        return float(forward(dict(parameters.values)))


    def Lift_Constant(self, value: NDArray[numpy.float64]) -> Any:
        return value


    def Gradients(
        self, parameters: ParameterSet, forward: Callable[[dict[str, Any]], Any]
    ) -> dict[str, NDArray[numpy.float64]]:
        gradients: dict[str, NDArray[numpy.float64]] = {}
        for name, value in parameters.values.items():
            gradient = numpy.zeros_like(value)
            flat_value = value.reshape(-1)
            flat_gradient = gradient.reshape(-1)
            for entry_index in range(flat_value.shape[0]):
                original = float(flat_value[entry_index])
                flat_value[entry_index] = original + self.step_size
                loss_above = float(forward(dict(parameters.values)))
                flat_value[entry_index] = original - self.step_size
                loss_below = float(forward(dict(parameters.values)))
                flat_value[entry_index] = original
                flat_gradient[entry_index] = (loss_above - loss_below) / (2.0 * self.step_size)
            gradients[name] = gradient
        return gradients
