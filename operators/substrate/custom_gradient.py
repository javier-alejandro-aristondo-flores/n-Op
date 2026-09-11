"""a forward paired with the backward that replaces the chain rule through it"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np

from operators.substrate.operations import Is_Engine_Native
from operators.substrate.torch_engine import Torch_Module


@dataclass(frozen=True, slots=True)
class CustomGradient:
    """a forward over positional arguments, declared together with the backward that stands in for it"""

    forward: Callable[[tuple[Any, ...]], Any]
    backward: Callable[[Any, Any, tuple[Any, ...]], tuple[Any, ...]]


    def Apply(self, *arguments: Any) -> Any:
        """the forward value, by the declared backward on the foreign engine and by the plain call elsewhere"""
        if not any(Is_Engine_Native(argument) for argument in arguments):
            # the reference engine never reaches the declared backward, and differentiates the plain call on its own
            return self.forward(arguments)
        return Applied_Through_The_Foreign_Engine(self, arguments)


def Applied_Through_The_Foreign_Engine(rule: CustomGradient, arguments: tuple[Any, ...]) -> Any:
    """one call bound to a foreign-engine node whose backward is the declared rule and not the unrolled tape"""
    torch = Torch_Module()

    class Bridge(torch.autograd.Function):
        """the foreign engine's own node, standing in for whatever it would otherwise have traced"""

        @staticmethod
        def forward(context: Any, *raw_arguments: Any) -> Any:
            output = rule.forward(raw_arguments)
            context.save_for_backward(*raw_arguments, output)
            return output


        @staticmethod
        def backward(context: Any, cotangent: Any) -> tuple[Any, ...]:
            *saved_arguments, output = context.saved_tensors
            return rule.backward(cotangent, output, tuple(saved_arguments))

    return Bridge.apply(*arguments)


def Vector_Jacobian_Product(function: Callable[[Any], Any], point: Any, cotangent: Any) -> Any:
    """the cotangent pulled back through function's jacobian at point, exact on the foreign engine"""
    if not Is_Engine_Native(point):
        return Reference_Vector_Jacobian_Product(function, point, cotangent)
    torch = Torch_Module()
    # a declared backward runs with the ambient tape off, so this rebuilds one locally to reach into
    with torch.enable_grad():
        differentiable_point = point.detach().requires_grad_(True)
        output = function(differentiable_point)
        gradient = torch.autograd.grad(output, differentiable_point, grad_outputs=cotangent)[0]
    return gradient


def Reference_Vector_Jacobian_Product(
    function: Callable[[Any], Any], point: Any, cotangent: Any, step_size: float = 1e-6
) -> Any:
    """the same product by central differences of the scalar the cotangent's own dot product with output forms"""
    point_values = np.array(point, dtype=np.float64)
    cotangent_values = np.asarray(cotangent, dtype=np.float64)
    gradient = np.zeros_like(point_values)
    # the flat views alias point_values, so perturbing one is seen by the next call to function
    flat_point = point_values.reshape(-1)
    flat_gradient = gradient.reshape(-1)
    for perturbed_entry in range(flat_point.shape[0]):
        original = float(flat_point[perturbed_entry])
        flat_point[perturbed_entry] = original + step_size
        value_above = float(np.sum(np.asarray(function(point_values), dtype=np.float64) * cotangent_values))
        flat_point[perturbed_entry] = original - step_size
        value_below = float(np.sum(np.asarray(function(point_values), dtype=np.float64) * cotangent_values))
        flat_point[perturbed_entry] = original
        flat_gradient[perturbed_entry] = (value_above - value_below) / (2.0 * step_size)
    return gradient
