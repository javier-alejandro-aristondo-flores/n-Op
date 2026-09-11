"""schemes for chaining layers, each owning its topology"""

# pyright: reportUnusedImport=false

from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.compositions.multi_scale import MultiScale
from operators.framework import Array, Coefficients, Composition, GridFunction, Layer
from operators.substrate import Gaussian_Error_Linear_Unit

from operators.compositions.fixed_point import FixedPoint, WeightTied


def Sliced_Lifted(lifted: dict[str, Any], prefix: str) -> dict[str, Any]:
    """the slice of a shared lifted dict that belongs to one part, its own names restored"""
    return {name[len(prefix):]: value for name, value in lifted.items() if name.startswith(prefix)}


class ExplicitStack(Composition[GridFunction]):
    """layers one after another, each an activated kernel-plus-local sum"""


    def __init__(self, layers: tuple[Layer[GridFunction], ...]) -> None:
        self.layers = layers
        self.last_layer_norms: NDArray[np.float64] | None = None


    def Layer_Outputs(self, lifted: dict[str, Any], input_values: Any) -> list[Any]:
        """the value after each layer in turn, differentiable through whichever engine lifted the dict"""
        current = input_values
        outputs: list[Any] = []
        for layer_index, layer in enumerate(self.layers):
            kernel_lifted = Sliced_Lifted(lifted, f"layer_{layer_index}.kernel.")
            local_linear_lifted = Sliced_Lifted(lifted, f"layer_{layer_index}.local_linear.")
            # every layer answers on the grid it was handed
            spatial_shape = current.shape[1:]
            output_shape = (int(spatial_shape[0]), int(spatial_shape[1]), int(spatial_shape[2]))
            kernel_output = layer.kernel.Forward(kernel_lifted, current, output_shape)
            local_output = layer.local_linear.Forward(local_linear_lifted, current)
            summed = local_output + kernel_output
            if layer.activation == "alias_free":
                raise NotImplementedError("the alias-free activation is the convolutional entry's own build")
            activated = Gaussian_Error_Linear_Unit(summed)
            # a residual layer can only add its input back when the channel count survived
            if layer.residual and activated.shape == current.shape:
                activated = activated + current
            outputs.append(activated)
            current = activated
        return outputs


    def Forward(self, lifted: dict[str, Any], input_values: Any) -> Any:
        """the stack's final value, differentiable through whichever engine lifted the shared dict"""
        outputs = self.Layer_Outputs(lifted, input_values)
        return outputs[-1] if outputs else input_values


    def Parameter_Values(self) -> dict[str, NDArray[np.float64]]:
        """every layer's kernel and local linear arrays, prefixed so no two layers' names collide"""
        collected: dict[str, NDArray[np.float64]] = {}
        for layer_index, layer in enumerate(self.layers):
            for name, value in layer.kernel.parameter_values.items():
                collected[f"layer_{layer_index}.kernel.{name}"] = value
            for name, value in layer.local_linear.parameter_values.items():
                collected[f"layer_{layer_index}.local_linear.{name}"] = value
        return collected


    def Apply(self, input_function: GridFunction, condition: Coefficients | None = None) -> GridFunction:
        values = np.asarray(input_function.values, dtype=np.float64)
        outputs = self.Layer_Outputs(self.Parameter_Values(), values)
        self.last_layer_norms = np.asarray(
            [float(np.linalg.norm(np.asarray(output, dtype=np.float64))) for output in outputs], dtype=np.float64
        )
        produced = np.asarray(outputs[-1], dtype=np.float64) if outputs else values
        return GridFunction(produced, input_function.channel_labels, input_function.domain, input_function.quadrature)


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = {}
        for layer_index, layer in enumerate(self.layers):
            for name, value in layer.kernel.Inspect().items():
                state[f"layer_{layer_index}.kernel.{name}"] = value
            for name, value in layer.local_linear.Inspect().items():
                state[f"layer_{layer_index}.local_linear.{name}"] = value
        if self.last_layer_norms is not None:
            state["last_layer_norms"] = self.last_layer_norms
        return state


class WithoutIntegralLayers(Composition[Coefficients]):
    """the branch's latent vector carried through unchanged, for a map with no integral to take"""


    def __init__(self) -> None:
        self.last_carried_vector: NDArray[np.float64] | None = None


    def Apply(self, input_function: Coefficients, condition: Coefficients | None = None) -> Coefficients:
        self.last_carried_vector = np.asarray(input_function.vector, dtype=np.float64)
        return input_function


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = {}
        if self.last_carried_vector is not None:
            state["last_carried_vector"] = self.last_carried_vector
        return state
