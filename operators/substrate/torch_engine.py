"""the torch-backed engine, automatic gradients behind the facet the reference obeys"""

import importlib.util
from collections.abc import Callable
from importlib import import_module
from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.substrate.engine import ParameterSet


def Torch_Is_Available() -> bool:
    """whether the torch package can be imported on this machine"""
    return importlib.util.find_spec("torch") is not None


def Torch_Module() -> Any:
    """torch as an untyped foreign surface, imported on demand"""
    return import_module("torch")


class TorchEngine:
    """parameterized computations evaluated and differentiated by torch autograd"""


    def __init__(self, device_name: str = "cpu") -> None:
        self.device_name = device_name


    def Lift(self, values: dict[str, NDArray[np.float64]], requires_gradient: bool) -> dict[str, Any]:
        torch = Torch_Module()
        # double precision throughout, to answer the reference engine number for number
        return {
            name: torch.tensor(value, dtype=torch.float64, device=self.device_name, requires_grad=requires_gradient)
            for name, value in values.items()
        }


    def Evaluate(self, parameters: ParameterSet, forward: Callable[[dict[str, Any]], Any]) -> float:
        torch = Torch_Module()
        with torch.no_grad():
            return float(forward(self.Lift(parameters.values, requires_gradient=False)))


    def Lift_Constant(self, value: NDArray[np.float64]) -> Any:
        torch = Torch_Module()
        return torch.tensor(value, dtype=torch.float64, device=self.device_name)


    def Gradients(
        self, parameters: ParameterSet, forward: Callable[[dict[str, Any]], Any]
    ) -> dict[str, NDArray[np.float64]]:
        lifted = self.Lift(parameters.values, requires_gradient=True)
        loss = forward(lifted)
        loss.backward()
        # the gradients come home as plain arrays, off whatever device they were computed on
        return {
            name: np.asarray(tensor.grad.detach().cpu().numpy(), dtype=np.float64)
            for name, tensor in lifted.items()
        }
