"""schemes for chaining layers, each owning its topology"""

import numpy as np
from numpy.typing import NDArray

from operators.framework import Array, Coefficients, Composition, GridFunction, GridSpec, Layer
from operators.substrate import Gaussian_Error_Linear_Unit


class ExplicitStack(Composition[GridFunction]):
    """layers one after another, each an activated kernel-plus-local sum"""


    def __init__(self, layers: tuple[Layer[GridFunction], ...]) -> None:
        self.layers = layers
        self.last_layer_norms: NDArray[np.float64] | None = None


    def Apply(self, input_function: GridFunction, condition: Coefficients | None = None) -> GridFunction:
        current = input_function
        norms: list[float] = []
        for layer in self.layers:
            # every layer answers on the grid it was handed
            grid_shape = np.asarray(current.values).shape[1:]
            grid_spec = GridSpec((grid_shape[0], grid_shape[1], grid_shape[2]))
            integrated = layer.kernel.Integrate(current, grid_spec, condition)
            summed = np.asarray(layer.local_linear(current.values)) + np.asarray(integrated.values)
            if layer.activation == "alias_free":
                raise NotImplementedError("the alias-free activation is the convolutional entry's own build")
            activated = np.asarray(Gaussian_Error_Linear_Unit(summed), dtype=np.float64)
            # a residual layer can only add its input back when the channel count survived
            if layer.residual and activated.shape == np.asarray(current.values).shape:
                activated = activated + np.asarray(current.values)
            norms.append(float(np.linalg.norm(activated)))
            current = GridFunction(activated, current.channel_labels, current.domain, current.quadrature)
        self.last_layer_norms = np.asarray(norms, dtype=np.float64)
        return current


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = {}
        for layer_index, layer in enumerate(self.layers):
            for name, value in layer.kernel.Inspect().items():
                state[f"layer_{layer_index}.kernel.{name}"] = value
        if self.last_layer_norms is not None:
            state["last_layer_norms"] = self.last_layer_norms
        return state
