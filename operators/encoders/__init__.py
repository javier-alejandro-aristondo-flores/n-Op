"""maps from corpus representations into the channel space layers work in"""

from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.framework import Array, Coefficients, Discretization, GridFunction, Operator
from operators.substrate import MultilayerPerceptron


class PointwiseLift(Operator[GridFunction, GridFunction]):
    """input channels mixed into a wider channel space, alike at every grid point"""


    def __init__(self, hidden_channels: int, input_channels: int, seed: int = 0) -> None:
        generator = np.random.default_rng(seed)
        scale = np.sqrt(2.0 / (hidden_channels + input_channels))
        self.parameter_values: dict[str, NDArray[np.float64]] = {
            "lift_weights": generator.normal(0.0, scale, size=(hidden_channels, input_channels)),
            "lift_biases": np.zeros(hidden_channels),
        }


    def Forward(self, lifted: dict[str, Any], input_values: Any) -> Any:
        # flattening the grid lets one matrix multiply cover every point
        flattened = input_values.reshape(input_values.shape[0], -1)
        mixed = lifted["lift_weights"] @ flattened + lifted["lift_biases"][:, None]
        return mixed.reshape(lifted["lift_weights"].shape[0], *input_values.shape[1:])


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        produced = np.asarray(self.Forward(self.parameter_values, np.asarray(input_function.values)))
        labels = tuple(f"hidden_{hidden_channel}" for hidden_channel in range(produced.shape[0]))
        return GridFunction(produced, labels, input_function.domain, input_function.quadrature)


    def Inspect(self) -> dict[str, Array]:
        return dict(self.parameter_values)


class SensorEncoder(Operator[Coefficients, Coefficients]):
    """a parameter vector read through a perceptron into a latent vector"""


    def __init__(self, layer_widths: tuple[int, ...], seed: int = 0) -> None:
        self.network = MultilayerPerceptron(layer_widths, "sensor_encoder", seed)
        self.parameter_values = self.network.parameter_values
        self.last_latent_vector: NDArray[np.float64] | None = None


    def Forward(self, lifted: dict[str, Any], input_vector: Any) -> Any:
        return self.network.Forward(lifted, input_vector)


    def __call__(
        self,
        input_function: Coefficients,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> Coefficients:
        produced = self.network.Apply(np.asarray(input_function.vector, dtype=np.float64))
        self.last_latent_vector = produced
        return Coefficients(vector=produced, domain=input_function.domain)


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = dict(self.parameter_values)
        if self.last_latent_vector is not None:
            state["last_latent_vector"] = self.last_latent_vector
        return state


class BasisProjectionEncoder(Operator[GridFunction, Coefficients]):
    """a field projected onto a fixed orthonormal basis"""


    def __init__(self, basis_modes: NDArray[np.float64], basis_mean: NDArray[np.float64]) -> None:
        self.basis_modes = basis_modes
        self.basis_mean = basis_mean
        self.last_coefficients: NDArray[np.float64] | None = None
        self.last_grid_shape: tuple[int, ...] | None = None


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> Coefficients:
        # the shape arrives with the field and is the only place this encoder can learn it
        self.last_grid_shape = np.asarray(input_function.values).shape[1:]
        flattened = np.asarray(input_function.values, dtype=np.float64).reshape(-1)
        # the basis was built on mean-removed fields, so the mean comes off here too
        coefficients = self.basis_modes @ (flattened - self.basis_mean)
        self.last_coefficients = coefficients
        return Coefficients(vector=coefficients, domain=input_function.domain)


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = {"basis_mode_norms": np.linalg.norm(self.basis_modes, axis=1)}
        # until a field has been seen this encoder does not know the shape its mean lives on
        if self.last_grid_shape is not None:
            state["basis_mean"] = self.basis_mean.reshape(self.last_grid_shape)
            state["basis_modes"] = self.basis_modes.reshape(self.basis_modes.shape[0], *self.last_grid_shape)
        else:
            state["basis_mean"] = self.basis_mean
        if self.last_coefficients is not None:
            state["last_coefficients"] = self.last_coefficients
        return state
