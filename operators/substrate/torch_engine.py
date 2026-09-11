"""the torch-backed engine, automatic gradients behind the facet the reference obeys"""

import importlib.util
from collections.abc import Callable
from importlib import import_module
from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.substrate.arrays import NUMPY_DTYPE_BY_PRECISION, Precision
from operators.substrate.engine import ParameterSet


def Torch_Is_Available() -> bool:
    """whether the torch package can be imported on this machine"""
    return importlib.util.find_spec("torch") is not None


def Torch_Module() -> Any:
    """torch as an untyped foreign surface, imported on demand"""
    return import_module("torch")


class TorchEngine:
    """parameterized computations evaluated and differentiated by torch autograd"""


    def __init__(self, device_name: str = "cpu", working_precision: Precision = "double") -> None:
        self.device_name = device_name
        # without the annotation inference widens the literal to a bare string, and the protocol asks for the literal
        self.working_precision: Precision = working_precision


    def Host_Dtype(self) -> np.dtype[Any]:
        """the numpy type every array is narrowed to before it crosses to the device"""
        return NUMPY_DTYPE_BY_PRECISION[self.working_precision]


    def Lift(self, values: dict[str, NDArray[np.float64]], requires_gradient: bool) -> dict[str, Any]:
        torch = Torch_Module()
        host_dtype = self.Host_Dtype()
        # narrowed on the host, so the bus carries the graph's precision and not the master weights'
        return {
            name: torch.tensor(
                np.asarray(value, dtype=host_dtype), device=self.device_name, requires_grad=requires_gradient
            )
            for name, value in values.items()
        }


    def Evaluate(self, parameters: ParameterSet, forward: Callable[[dict[str, Any]], Any]) -> float:
        torch = Torch_Module()
        with torch.no_grad():
            return float(forward(self.Lift(parameters.values, requires_gradient=False)))


    def Lift_Constant(self, value: NDArray[np.float64]) -> Any:
        torch = Torch_Module()
        return torch.tensor(np.asarray(value, dtype=self.Host_Dtype()), device=self.device_name)


    def Value_And_Gradients(
        self, parameters: ParameterSet, forward: Callable[[dict[str, Any]], Any]
    ) -> tuple[float, dict[str, NDArray[np.float64]]]:
        lifted = self.Lift(parameters.values, requires_gradient=True)
        loss = forward(lifted)
        loss.backward()
        # a parameter the loss never touched has no gradient recorded, and its true derivative is zero
        gradients = {
            name: (
                np.zeros_like(parameters.values[name])
                if tensor.grad is None
                else np.asarray(tensor.grad.detach().cpu().numpy(), dtype=np.float64)
            )
            for name, tensor in lifted.items()
        }
        return float(loss.detach()), gradients


    def Gradients(
        self, parameters: ParameterSet, forward: Callable[[dict[str, Any]], Any]
    ) -> dict[str, NDArray[np.float64]]:
        return self.Value_And_Gradients(parameters, forward)[1]
