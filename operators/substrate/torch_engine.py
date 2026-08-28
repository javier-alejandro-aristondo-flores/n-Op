"""The torch-backed engine: automatic gradients behind the same facet the reference obeys."""

import importlib.util
from collections.abc import Callable
from importlib import import_module
from typing import Any

import numpy
from numpy.typing import NDArray

from operators.substrate.engine import ParameterSet


def Torch_Is_Available() -> bool:
    """Returns whether the torch package can be imported on this machine."""
    return importlib.util.find_spec("torch") is not None


def Torch_Module() -> Any:
    """Imports and returns the torch module as an untyped foreign surface."""
    return import_module("torch")


class TorchEngine:
    """Evaluates and differentiates parameterized computations with torch autograd."""


    def __init__(self, device_name: str = "cpu") -> None:
        self.device_name = device_name


    def Lift(self, values: dict[str, NDArray[numpy.float64]], requires_gradient: bool) -> dict[str, Any]:
        torch = Torch_Module()
        return {
            name: torch.tensor(value, dtype=torch.float64, device=self.device_name, requires_grad=requires_gradient)
            for name, value in values.items()
        }


    def Evaluate(self, parameters: ParameterSet, forward: Callable[[dict[str, Any]], Any]) -> float:
        torch = Torch_Module()
        with torch.no_grad():
            return float(forward(self.Lift(parameters.values, requires_gradient=False)))


    def Gradients(self, parameters: ParameterSet, forward: Callable[[dict[str, Any]], Any]) -> dict[str, NDArray[numpy.float64]]:
        lifted = self.Lift(parameters.values, requires_gradient=True)
        loss = forward(lifted)
        loss.backward()
        return {
            name: numpy.asarray(tensor.grad.detach().cpu().numpy(), dtype=numpy.float64)
            for name, tensor in lifted.items()
        }
