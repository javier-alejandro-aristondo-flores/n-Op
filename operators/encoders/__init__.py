"""maps from corpus representations into the channel space layers work in"""

from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.framework import Array, Coefficients, Discretization, GridFunction, Operator, PointSet
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


class AtomEmbedding(Operator[PointSet, PointSet]):
    """atoms carrying a learned feature vector keyed by element and pseudopotential title"""


    def __init__(self, vocabulary: tuple[tuple[str, str], ...], embedding_width: int, seed: int = 0) -> None:
        generator = np.random.default_rng(seed)
        scale = 1.0 / np.sqrt(embedding_width)
        self.vocabulary = vocabulary
        self.index_by_key = {key: position for position, key in enumerate(vocabulary)}
        self.parameter_values: dict[str, NDArray[np.float64]] = {
            "atom_embedding_table": generator.normal(0.0, scale, size=(len(vocabulary), embedding_width)),
        }
        self.last_vocabulary_indices: NDArray[np.intp] | None = None


    def Forward(self, lifted: dict[str, Any], vocabulary_indices: Any) -> Any:
        # one table row gathered per atom, from whichever engine holds the table
        return lifted["atom_embedding_table"][vocabulary_indices]


    def Vocabulary_Indices(self, species: Any) -> NDArray[np.intp]:
        # a pair the vocabulary has never seen has no row to fall back to
        keys = [(str(element), str(title)) for element, title in species]
        unknown = sorted({key for key in keys if key not in self.index_by_key})
        if unknown:
            raise ValueError(f"atom embedding has no row for (element, pseudopotential title) pairs: {unknown}")
        return np.asarray([self.index_by_key[key] for key in keys], dtype=np.intp)


    def __call__(
        self,
        input_function: PointSet,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> PointSet:
        species = input_function.species
        # each row pairs the element symbol in column zero with its pseudopotential title in column one
        if species is None:
            raise ValueError("atom embedding needs a species column to key its lookup")
        vocabulary_indices = self.Vocabulary_Indices(np.asarray(species))
        produced = np.asarray(self.Forward(self.parameter_values, vocabulary_indices))
        self.last_vocabulary_indices = vocabulary_indices
        return PointSet(
            positions=input_function.positions,
            domain=input_function.domain,
            values=produced,
            species=input_function.species,
            roles=input_function.roles,
            quadrature=input_function.quadrature,
        )


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = dict(self.parameter_values)
        if self.last_vocabulary_indices is not None:
            state["last_vocabulary_indices"] = self.last_vocabulary_indices
        return state


class VariableEncoding(Operator[GridFunction, GridFunction]):
    """each channel lifted into a shared token width by one learned encoding per channel label"""


    def __init__(
        self, vocabulary: tuple[str, ...], hidden_channels: int, condition_width: int, seed: int = 0
    ) -> None:
        generator = np.random.default_rng(seed)
        scale = 1.0 / np.sqrt(hidden_channels)
        self.vocabulary = vocabulary
        self.index_by_label = {label: position for position, label in enumerate(vocabulary)}
        self.parameter_values: dict[str, NDArray[np.float64]] = {
            "token_lift_weights": generator.normal(0.0, scale, size=(hidden_channels,)),
            "token_lift_biases": np.zeros(hidden_channels),
            "label_encodings": generator.normal(0.0, scale, size=(len(vocabulary), hidden_channels)),
            "condition_projection_weights": generator.normal(0.0, scale, size=(hidden_channels, condition_width)),
        }
        self.last_label_indices: NDArray[np.intp] | None = None


    def Forward(self, lifted: dict[str, Any], channel_values: Any, label_indices: Any, condition_vector: Any) -> Any:
        hidden_channels = lifted["token_lift_weights"].shape[0]
        grid_rank = len(channel_values.shape) - 1
        token_shape = (1, hidden_channels) + (1,) * grid_rank
        lifted_weights = lifted["token_lift_weights"].reshape(token_shape)
        lifted_biases = lifted["token_lift_biases"].reshape(token_shape)
        channel_shape = (channel_values.shape[0], hidden_channels) + (1,) * grid_rank
        # every token is lifted by the same weights, and only this row says which token it is
        channel_encodings = lifted["label_encodings"][label_indices].reshape(channel_shape)
        tokens = channel_values[:, None] * lifted_weights + lifted_biases + channel_encodings
        if condition_vector is not None:
            # a run-level covariate, so every present token's encoding takes the same shift
            condition_shift = (lifted["condition_projection_weights"] @ condition_vector).reshape(token_shape)
            tokens = tokens + condition_shift
        return tokens.reshape(-1, *channel_values.shape[1:])


    def Label_Indices(self, channel_labels: tuple[str, ...]) -> NDArray[np.intp]:
        # a label the vocabulary has never seen has no row to fall back to
        unknown = sorted(label for label in channel_labels if label not in self.index_by_label)
        if unknown:
            raise ValueError(f"variable encoding has no row for channel labels: {unknown}")
        return np.asarray([self.index_by_label[label] for label in channel_labels], dtype=np.intp)


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        label_indices = self.Label_Indices(input_function.channel_labels)
        channel_values = np.asarray(input_function.values, dtype=np.float64)
        condition_vector = None if condition is None else np.asarray(condition.vector, dtype=np.float64)
        produced = np.asarray(self.Forward(self.parameter_values, channel_values, label_indices, condition_vector))
        hidden_channels = self.parameter_values["token_lift_weights"].shape[0]
        labels = tuple(
            f"{label}_{hidden_channel}"
            for label in input_function.channel_labels
            for hidden_channel in range(hidden_channels)
        )
        self.last_label_indices = label_indices
        return GridFunction(produced, labels, input_function.domain, input_function.quadrature)


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = dict(self.parameter_values)
        if self.last_label_indices is not None:
            state["last_label_indices"] = self.last_label_indices
        return state
