"""the differentiation facet, named parameters in and gradients back"""

from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True, slots=True)
class ParameterSet:
    """named parameter values, held canonically in double precision"""

    values: dict[str, NDArray[np.float64]]


class Engine(Protocol):
    """evaluates and differentiates a forward computation over named parameters"""


    @abstractmethod
    def Evaluate(self, parameters: ParameterSet, forward: Callable[[dict[str, Any]], Any]) -> float: ...


    @abstractmethod
    def Gradients(
        self, parameters: ParameterSet, forward: Callable[[dict[str, Any]], Any]
    ) -> dict[str, NDArray[np.float64]]: ...


    @abstractmethod
    def Lift_Constant(self, value: NDArray[np.float64]) -> Any: ...


class NumpyEngine:
    """the reference engine, gradients by central differences"""


    def __init__(self, step_size: float = 1e-6) -> None:
        self.step_size = step_size


    def Evaluate(self, parameters: ParameterSet, forward: Callable[[dict[str, Any]], Any]) -> float:
        return float(forward(dict(parameters.values)))


    def Lift_Constant(self, value: NDArray[np.float64]) -> Any:
        return value


    def Gradients(
        self, parameters: ParameterSet, forward: Callable[[dict[str, Any]], Any]
    ) -> dict[str, NDArray[np.float64]]:
        gradients: dict[str, NDArray[np.float64]] = {}
        for name, value in parameters.values.items():
            gradient = np.zeros_like(value)
            # the flat views alias the parameter, so perturbing one is seen by the forward
            flat_value = value.reshape(-1)
            flat_gradient = gradient.reshape(-1)
            for perturbed_entry in range(flat_value.shape[0]):
                original = float(flat_value[perturbed_entry])
                flat_value[perturbed_entry] = original + self.step_size
                loss_above = float(forward(dict(parameters.values)))
                flat_value[perturbed_entry] = original - self.step_size
                loss_below = float(forward(dict(parameters.values)))
                # put the entry back before the next one moves
                flat_value[perturbed_entry] = original
                flat_gradient[perturbed_entry] = (loss_above - loss_below) / (2.0 * self.step_size)
            gradients[name] = gradient
        return gradients
