"""a forward paired with the backward that replaces the chain rule through it"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

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
