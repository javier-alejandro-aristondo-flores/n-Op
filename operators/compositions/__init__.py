"""Compositions: schemes for chaining layers, each owning its topology."""

import numpy
from numpy.typing import NDArray

from operators.framework import Coefficients, Composition, GridFunction, GridSpec, Layer
from operators.framework.domain import Array
from operators.substrate.operations import Gaussian_Error_Linear_Unit


class ExplicitStack(Composition[GridFunction]):
    """Applies layers one after another, each an activated kernel-plus-local sum."""


    def __init__(self, layers: tuple[Layer[GridFunction], ...]) -> None:
        self.layers = layers
        self.last_layer_norms: NDArray[numpy.float64] | None = None


    def Apply(self, input_function: GridFunction, condition: Coefficients | None = None) -> GridFunction:
        current = input_function
        norms: list[float] = []
        for layer in self.layers:
            grid_shape = numpy.asarray(current.values).shape[1:]
            integrated = layer.kernel.Integrate(current, GridSpec((grid_shape[0], grid_shape[1], grid_shape[2])), condition)
            summed = numpy.asarray(layer.local_linear(current.values)) + numpy.asarray(integrated.values)
            if layer.activation == "alias_free":
                raise NotImplementedError("the alias-free activation is the convolutional entry's own build")
            activated = numpy.asarray(Gaussian_Error_Linear_Unit(summed), dtype=numpy.float64)
            if layer.residual and activated.shape == numpy.asarray(current.values).shape:
                activated = activated + numpy.asarray(current.values)
            norms.append(float(numpy.linalg.norm(activated)))
            current = GridFunction(activated, current.channel_labels, current.domain, current.quadrature)
        self.last_layer_norms = numpy.asarray(norms, dtype=numpy.float64)
        return current


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = {}
        for layer_index, layer in enumerate(self.layers):
            for name, value in layer.kernel.Inspect().items():
                state[f"layer_{layer_index}.kernel.{name}"] = value
        if self.last_layer_norms is not None:
            state["last_layer_norms"] = self.last_layer_norms
        return state


__all__ = [
    "ExplicitStack",
]
