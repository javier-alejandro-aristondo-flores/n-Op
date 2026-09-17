"""charge density to electron localization, by softmax-free attention over grid points"""

from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray

from operators.compositions import ExplicitStack, Spectral_Resampled
from operators.encoders import PointwiseLift
from operators.framework import (
    Array,
    Coefficients,
    Discretization,
    Fractional_Grid_Coordinates,
    GridFunction,
    GridSpec,
    Kernel,
    Layer,
    NeuralOperator,
    Operator,
    Output_Points,
    UniformGridQuadrature,
)
from operators.readouts import PeriodicCoordinateFeatures, PointwiseProjection
from operators.substrate import Concatenate_Channels, Einstein_Summation, Mean_Over_Last_Axis
from operators.wrappers import Conserving

type GalerkinTransformerTask = Literal["parametric", "localization"]

HIDDEN_CHANNELS = 128

HEAD_COUNT = 4

ENCODER_LAYER_COUNT = 4

COORDINATE_FOURIER_ORDERS = 4

# keeps a channel's own spread from dividing by zero on a constant field of tokens
GALERKIN_NORM_EPSILON = 1e-5

# a chunk of this many query rows is answered per cross-attention pass, bounding decoder-side memory
DECODER_QUERY_CHUNK_SIZE = 16384

PEROVSKITE_LATTICE_FACTOR_COUNT = 6

LATTICE_GRAM_CHANNEL_COUNT = 6

LOG_COMPRESSED_SPIN_CHANNEL_COUNT = 2

LOCALIZATION_INPUT_FIELD_CHANNEL_COUNT = LOG_COMPRESSED_SPIN_CHANNEL_COUNT + LATTICE_GRAM_CHANNEL_COUNT

LOCALIZATION_CHANNEL_LABELS = ("electron_localization_up", "electron_localization_down")

PEROVSKITE_DENSITY_CHANNEL_LABELS = ("charge_density",)

# a positive floor under a training-block mean that would otherwise divide by zero
REFERENCE_DENSITY_FLOOR = 1e-12

COORDINATE_FEATURES = PeriodicCoordinateFeatures(fourier_orders=COORDINATE_FOURIER_ORDERS, axis_count=3)


def Sliced_Lifted(lifted: dict[str, Any], prefix: str) -> dict[str, Any]:
    """the slice of a shared lifted dict that belongs to one part, its own names restored"""
    return {name[len(prefix):]: value for name, value in lifted.items() if name.startswith(prefix)}


def Token_Axis_Normalized(values: Any, scale: Any, bias: Any) -> Any:
    """each channel standardized over the token axis, then given a learned per-channel affine"""
    mean = Mean_Over_Last_Axis(values)
    centered = values - mean[..., None]
    variance = Mean_Over_Last_Axis(centered * centered)
    standardized = centered / (variance[..., None] + GALERKIN_NORM_EPSILON) ** 0.5
    return standardized * (1.0 + scale[:, None]) + bias[:, None]


def Spin_Channels(
    density: NDArray[np.float64], magnetization: NDArray[np.float64]
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """the up and down spin densities, half the sum and half the difference, clipped where the corpus goes negative"""
    return np.maximum((density + magnetization) / 2.0, 0.0), np.maximum((density - magnetization) / 2.0, 0.0)


def Log_Compressed_Input_Channels(
    density: NDArray[np.float64], magnetization: NDArray[np.float64], reference_density: float
) -> NDArray[np.float64]:
    """the two spin densities, each mapped through the dynamic-range compression"""
    spin_up, spin_down = Spin_Channels(density, magnetization)
    return np.stack([np.log1p(spin_up / reference_density), np.log1p(spin_down / reference_density)])


def Lattice_Gram_Six(lattice: NDArray[np.float64]) -> NDArray[np.float64]:
    """the six independent entries of the lattice's own Gram matrix, upper triangle in row order"""
    gram = lattice @ lattice.T
    return np.asarray([gram[0, 0], gram[0, 1], gram[0, 2], gram[1, 1], gram[1, 2], gram[2, 2]], dtype=np.float64)


def Standardized_Lattice_Gram(
    lattice: NDArray[np.float64], gram_mean: NDArray[np.float64], gram_scale: NDArray[np.float64]
) -> NDArray[np.float64]:
    """one run's six Gram entries, centered and scaled by the training block's own statistics"""
    return (Lattice_Gram_Six(lattice) - gram_mean) / gram_scale


def Lattice_Gram_Statistics(lattices: list[NDArray[np.float64]]) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """a training block's own mean and spread of the six Gram entries, spread guarded away from zero"""
    stacked = np.stack([Lattice_Gram_Six(np.asarray(lattice, dtype=np.float64)) for lattice in lattices])
    mean = stacked.mean(axis=0)
    scale = stacked.std(axis=0)
    # a cell parameter that never varies across the block would otherwise divide by zero
    scale[scale == 0.0] = 1.0
    return mean, scale


def Reference_Density(
    density_fields: list[NDArray[np.float64]], magnetization_fields: list[NDArray[np.float64]]
) -> float:
    """a training block's own mean spin density, the scale the log compression is centered on"""
    total = 0.0
    counted_entries = 0
    for density, magnetization in zip(density_fields, magnetization_fields, strict=True):
        spin_up, spin_down = Spin_Channels(density, magnetization)
        total += float(spin_up.sum()) + float(spin_down.sum())
        counted_entries += spin_up.size + spin_down.size
    return max(total / counted_entries, REFERENCE_DENSITY_FLOOR)


def Constant_Channel_Field(vector: NDArray[np.float64], shape: tuple[int, int, int]) -> NDArray[np.float64]:
    """a parameter vector repeated identically at every point of the requested grid"""
    return np.broadcast_to(vector[:, None, None, None], (vector.shape[0], *shape)).astype(np.float64).copy()


def Coordinate_Feature_Channels(shape: tuple[int, int, int]) -> NDArray[np.float64]:
    """periodic sine-cosine features of the grid's own fractional coordinates, channel-first at the given shape"""
    points = Fractional_Grid_Coordinates(shape)
    features = COORDINATE_FEATURES(points)
    return np.asarray(features.T.reshape(features.shape[1], *shape), dtype=np.float64)


class GalerkinAttentionKernel(Kernel[GridFunction, GridFunction]):
    """softmax-free Petrov-Galerkin attention over grid-point tokens, two matrix products per head"""

    supported_representations = (GridFunction,)


    def __init__(self, hidden_channels: int, head_count: int = HEAD_COUNT, seed: int = 0) -> None:
        if hidden_channels % head_count != 0:
            raise ValueError(f"{hidden_channels} hidden channels do not split evenly into {head_count} heads")
        self.hidden_channels = hidden_channels
        self.head_count = head_count
        self.head_width = hidden_channels // head_count
        self.query_projection = PointwiseLift(hidden_channels, hidden_channels, seed=seed)
        self.key_projection = PointwiseLift(hidden_channels, hidden_channels, seed=seed + 1)
        self.value_projection = PointwiseLift(hidden_channels, hidden_channels, seed=seed + 2)
        self.output_projection = PointwiseLift(hidden_channels, hidden_channels, seed=seed + 3)
        self.parameter_values: dict[str, NDArray[np.float64]] = {
            "key_norm_scale": np.zeros(hidden_channels),
            "key_norm_bias": np.zeros(hidden_channels),
            "value_norm_scale": np.zeros(hidden_channels),
            "value_norm_bias": np.zeros(hidden_channels),
        }
        for prefix, part in self.Named_Parts():
            for name, value in part.parameter_values.items():
                self.parameter_values[f"{prefix}{name}"] = value
        self.last_attended_norm: NDArray[np.float64] | None = None


    def Named_Parts(self) -> tuple[tuple[str, PointwiseLift], ...]:
        """the four token-shared linear maps this kernel owns, each under its own namespace prefix"""
        return (
            ("query.", self.query_projection),
            ("key.", self.key_projection),
            ("value.", self.value_projection),
            ("output.", self.output_projection),
        )


    def Parameter_Count(self) -> int:
        """how many real numbers this kernel stores, the same at every token count it is ever asked to answer for"""
        return sum(int(value.size) for value in self.parameter_values.values())


    def Head_Split(self, values: Any, token_count: int) -> Any:
        """the hidden-channel axis split into heads, each head a contiguous block of the whole width"""
        return values.reshape(self.head_count, self.head_width, token_count)


    def Forward(self, lifted: dict[str, Any], input_values: Any, output_shape: tuple[int, int, int]) -> Any:
        grid_shape = input_values.shape[1:]
        token_count = int(grid_shape[0]) * int(grid_shape[1]) * int(grid_shape[2])
        flattened = input_values.reshape(self.hidden_channels, token_count)
        query_full = self.query_projection.Forward(Sliced_Lifted(lifted, "query."), flattened)
        key_full = self.key_projection.Forward(Sliced_Lifted(lifted, "key."), flattened)
        value_full = self.value_projection.Forward(Sliced_Lifted(lifted, "value."), flattened)
        key_normalized = Token_Axis_Normalized(key_full, lifted["key_norm_scale"], lifted["key_norm_bias"])
        value_normalized = Token_Axis_Normalized(value_full, lifted["value_norm_scale"], lifted["value_norm_bias"])
        query_heads = self.Head_Split(query_full, token_count)
        key_heads = self.Head_Split(key_normalized, token_count)
        value_heads = self.Head_Split(value_normalized, token_count)
        # contracted over the source-token axis first, so no token-by-token tensor is ever formed
        key_value = Einstein_Summation("hdn,hen->hde", key_heads, value_heads)
        attended_heads = Einstein_Summation("hde,hdm->hem", key_value, query_heads) / float(token_count)
        merged = attended_heads.reshape(self.hidden_channels, token_count)
        produced = self.output_projection.Forward(Sliced_Lifted(lifted, "output."), merged)
        return produced.reshape(self.hidden_channels, *output_shape)


    def Integrate(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        if not isinstance(output_discretization, GridSpec):
            raise TypeError("the Galerkin attention kernel evaluates on grids only")
        field = np.asarray(input_function.values, dtype=np.float64)
        produced = np.asarray(
            self.Forward(self.parameter_values, field, output_discretization.shape), dtype=np.float64
        )
        self.last_attended_norm = np.asarray(float(np.linalg.norm(produced)))
        labels = tuple(f"attended_{hidden_index}" for hidden_index in range(self.hidden_channels))
        return GridFunction(produced, labels, input_function.domain, input_function.quadrature)


    def Refreshed(self, part_parameter_values: dict[str, NDArray[np.float64]], prefix: str) -> None:
        """the part's own dict brought current from this kernel's aggregate, so inspecting it reflects training"""
        for name, value in Sliced_Lifted(self.parameter_values, prefix).items():
            part_parameter_values[name] = value


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = dict(self.parameter_values)
        for prefix, part in self.Named_Parts():
            self.Refreshed(part.parameter_values, prefix)
            for name, value in part.Inspect().items():
                state[f"{prefix}{name}"] = value
        if self.last_attended_norm is not None:
            state["last_attended_norm"] = self.last_attended_norm
        return state


class QueryPointDecoder(Operator[GridFunction, GridFunction]):
    """cross-attention from the encoder's own tokens onto output-coordinate queries, then a pointwise head"""


    def __init__(
        self,
        hidden_channels: int,
        output_channels: int,
        channel_labels: tuple[str, ...],
        head_count: int = HEAD_COUNT,
        bounded: bool = False,
        fourier_orders: int = COORDINATE_FOURIER_ORDERS,
        query_chunk_size: int = DECODER_QUERY_CHUNK_SIZE,
        condition_channel_count: int = 0,
        seed: int = 0,
    ) -> None:
        if hidden_channels % head_count != 0:
            raise ValueError(f"{hidden_channels} hidden channels do not split evenly into {head_count} heads")
        self.hidden_channels = hidden_channels
        self.head_count = head_count
        self.head_width = hidden_channels // head_count
        self.channel_labels = channel_labels
        self.query_chunk_size = query_chunk_size
        # a channel width the token-axis normalization can never wash out, since it is added to the query
        # branch alone and every query row carries the identical, un-normalized value
        self.condition_channel_count = condition_channel_count
        self.coordinate_features = PeriodicCoordinateFeatures(fourier_orders=fourier_orders, axis_count=3)
        self.query_projection = PointwiseLift(
            hidden_channels, self.coordinate_features.feature_count + condition_channel_count, seed=seed
        )
        self.key_projection = PointwiseLift(hidden_channels, hidden_channels, seed=seed + 1)
        self.value_projection = PointwiseLift(hidden_channels, hidden_channels, seed=seed + 2)
        self.final_projection = PointwiseProjection(output_channels, hidden_channels, bounded=bounded, seed=seed + 3)
        self.parameter_values: dict[str, NDArray[np.float64]] = {
            "key_norm_scale": np.zeros(hidden_channels),
            "key_norm_bias": np.zeros(hidden_channels),
            "value_norm_scale": np.zeros(hidden_channels),
            "value_norm_bias": np.zeros(hidden_channels),
        }
        for prefix, part in self.Named_Parts():
            for name, value in part.parameter_values.items():
                self.parameter_values[f"{prefix}{name}"] = value
        self.last_answered_query_count: NDArray[np.intp] | None = None


    def Named_Parts(self) -> tuple[tuple[str, PointwiseLift | PointwiseProjection], ...]:
        """the token-shared linear maps this decoder owns, each under its own namespace prefix"""
        return (
            ("query.", self.query_projection),
            ("key.", self.key_projection),
            ("value.", self.value_projection),
            ("final.", self.final_projection),
        )


    def Parameter_Count(self) -> int:
        """how many real numbers this decoder stores, the same at every query count it is ever asked to answer for"""
        return sum(int(value.size) for value in self.parameter_values.values())


    def Coordinate_Features(self, points: NDArray[np.float64]) -> NDArray[np.float64]:
        """the periodic features a query row's own fractional coordinates carry into the cross-attention"""
        return self.coordinate_features(points)


    def Forward(
        self, lifted: dict[str, Any], token_values: Any, query_features: Any, condition_channels: Any = None
    ) -> Any:
        """cross-attention from the encoder's final tokens onto every query row, evaluated in chunks"""
        # condition_channels, when given, is a flat per-example vector concatenated onto every query row
        # before query_projection -- the query branch never passes through Token_Axis_Normalized, so this
        # is the one channel a per-example condition can ride into the output on unwashed
        hidden_channels = token_values.shape[0]
        token_spatial_shape = token_values.shape[1:]
        token_count = int(token_spatial_shape[0]) * int(token_spatial_shape[1]) * int(token_spatial_shape[2])
        flat_tokens = token_values.reshape(hidden_channels, token_count)
        key_full = self.key_projection.Forward(Sliced_Lifted(lifted, "key."), flat_tokens)
        value_full = self.value_projection.Forward(Sliced_Lifted(lifted, "value."), flat_tokens)
        key_normalized = Token_Axis_Normalized(key_full, lifted["key_norm_scale"], lifted["key_norm_bias"])
        value_normalized = Token_Axis_Normalized(value_full, lifted["value_norm_scale"], lifted["value_norm_bias"])
        key_heads = key_normalized.reshape(self.head_count, self.head_width, token_count)
        value_heads = value_normalized.reshape(self.head_count, self.head_width, token_count)
        # built once, since every query chunk reuses the identical source-token contraction
        key_value = Einstein_Summation("hdn,hen->hde", key_heads, value_heads)
        query_row_count = query_features.shape[0]
        chunk_outputs: list[Any] = []
        for chunk_start in range(0, query_row_count, self.query_chunk_size):
            chunk_features = query_features[chunk_start : chunk_start + self.query_chunk_size].T
            chunk_count = chunk_features.shape[1]
            if condition_channels is not None:
                # a row of ones on the query branch's own engine, so the broadcast needs no engine dispatch
                ones_row = chunk_features[:1] * 0.0 + 1.0
                condition_block = condition_channels[:, None] * ones_row
                chunk_features = Concatenate_Channels([chunk_features, condition_block])
            query_full = self.query_projection.Forward(Sliced_Lifted(lifted, "query."), chunk_features)
            query_heads = query_full.reshape(self.head_count, self.head_width, chunk_count)
            attended_heads = Einstein_Summation("hde,hdm->hem", key_value, query_heads) / float(token_count)
            merged_chunk = attended_heads.reshape(hidden_channels, chunk_count)
            projected_chunk = self.final_projection.Forward(Sliced_Lifted(lifted, "final."), merged_chunk)
            chunk_outputs.append(projected_chunk.T)
        return Concatenate_Channels(chunk_outputs)


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        if not isinstance(output_discretization, GridSpec):
            raise TypeError("the query-point decoder answers grids at this gate's own contract")
        shape = output_discretization.shape
        points = Output_Points(output_discretization)
        query_features = self.Coordinate_Features(points)
        self.last_answered_query_count = np.asarray(points.shape[0])
        token_values = np.asarray(input_function.values, dtype=np.float64)
        produced = np.asarray(self.Forward(self.parameter_values, token_values, query_features), dtype=np.float64)
        point_count = shape[0] * shape[1] * shape[2]
        quadrature = UniformGridQuadrature(input_function.quadrature.cell_volume, point_count)
        return GridFunction(
            produced.T.reshape(len(self.channel_labels), *shape), self.channel_labels, input_function.domain, quadrature
        )


    def Refreshed(self, part_parameter_values: dict[str, NDArray[np.float64]], prefix: str) -> None:
        """the part's own dict brought current from this decoder's aggregate, so inspecting it reflects training"""
        for name, value in Sliced_Lifted(self.parameter_values, prefix).items():
            part_parameter_values[name] = value


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = dict(self.parameter_values)
        for prefix, part in self.Named_Parts():
            self.Refreshed(part.parameter_values, prefix)
            for name, value in part.Inspect().items():
                state[f"{prefix}{name}"] = value
        if self.last_answered_query_count is not None:
            state["last_answered_query_count"] = self.last_answered_query_count
        return state


class GalerkinTransformer(NeuralOperator[GridFunction, GridFunction, GridFunction]):
    """coordinate-featured grid tokens, linear attention layers, a cross-attention decoder over query points"""


    def __init__(
        self,
        encoder: PointwiseLift,
        composition: ExplicitStack,
        readout: QueryPointDecoder,
        task: GalerkinTransformerTask,
        processing_shape: tuple[int, int, int],
        reference_density: float = 1.0,
        gram_mean: NDArray[np.float64] | None = None,
        gram_scale: NDArray[np.float64] | None = None,
        density_voxel_mean: NDArray[np.float64] | None = None,
        density_voxel_scale: NDArray[np.float64] | None = None,
    ) -> None:
        super().__init__(encoder, composition, readout)
        self.lift = encoder
        self.attention_stack = composition
        self.decoder = readout
        self.task: GalerkinTransformerTask = task
        self.processing_shape = processing_shape
        self.reference_density = reference_density
        self.gram_mean = np.zeros(LATTICE_GRAM_CHANNEL_COUNT) if gram_mean is None else gram_mean
        self.gram_scale = np.ones(LATTICE_GRAM_CHANNEL_COUNT) if gram_scale is None else gram_scale
        # the parametric task's own training population, per-voxel statistics of the raw density, in the
        # decoder's own row-per-query-point layout (query_row_count, 1); fixed once and read only at
        # inference -- the lifted forward the training loss calls answers in this standardized space, never
        # renormalized, so predicting zero already is the training-mean field, and the cusp-dominated raw
        # squared error no longer owns the gradient. None means the identity (no standardization), which is
        # shape-agnostic; a set pair is grid-bound to the shape they were measured on (see Unstandardized_Target)
        self.density_voxel_mean = density_voxel_mean
        self.density_voxel_scale = density_voxel_scale
        self.channel_labels = PEROVSKITE_DENSITY_CHANNEL_LABELS if task == "parametric" else LOCALIZATION_CHANNEL_LABELS
        # the whole-field conservation law: the perovskite density's own electron count, the localization
        # task's bounded head carrying no conservation law of its own
        self.conservation = (
            Conserving(inner=self, law="renormalize_to_electron_count") if task == "parametric" else None
        )
        self.last_predicted_values: NDArray[np.float64] | None = None


    def Parameter_Values(self) -> dict[str, NDArray[np.float64]]:
        """every part's own arrays under one namespace, ready for the trainer"""
        collected = dict(self.lift.parameter_values)
        collected.update(self.attention_stack.Parameter_Values())
        collected.update(self.decoder.parameter_values)
        return collected


    def Parameter_Count(self) -> int:
        """how many real numbers this member stores"""
        return sum(int(value.size) for value in self.Parameter_Values().values())


    def Forward_From_Coarse_Input(self, lifted: dict[str, Any], combined_coarse_input: Any, query_features: Any) -> Any:
        """the lifted path from the coarse token input, through the attention stack, to the query-point decoder"""
        # never renormalized here: conservation is a whole-field, physical-units correction that belongs
        # only on the inference path in __call__, never inside a training loss built directly on this call
        hidden = self.lift.Forward(lifted, combined_coarse_input)
        carried = self.attention_stack.Forward(lifted, hidden)
        condition_channels = (
            combined_coarse_input[:PEROVSKITE_LATTICE_FACTOR_COUNT, 0, 0, 0] if self.task == "parametric" else None
        )
        return self.decoder.Forward(lifted, carried, query_features, condition_channels=condition_channels)


    def Unstandardized_Target(self, standardized: Any, query_row_count: int) -> Any:
        """the raw forward's output brought back to physical density units, grid-bound to the training shape"""
        if self.density_voxel_mean is None or self.density_voxel_scale is None:
            return standardized
        if self.density_voxel_mean.shape[0] != query_row_count:
            raise ValueError(
                f"the parametric task's per-voxel target statistics were measured on"
                f" {self.density_voxel_mean.shape[0]} query rows, not the requested {query_row_count} --"
                " un-standardization is grid-bound to the gate's own angle-stratum resolution"
            )
        return standardized * self.density_voxel_scale + self.density_voxel_mean


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        if not isinstance(output_discretization, GridSpec):
            raise TypeError("the Galerkin transformer evaluates on grids only")
        shape = output_discretization.shape
        query_points = Output_Points(output_discretization)
        query_features = self.decoder.Coordinate_Features(query_points)
        lattice = np.asarray(input_function.domain.lattice, dtype=np.float64)
        cell_volume = float(abs(np.linalg.det(lattice)))
        point_count = shape[0] * shape[1] * shape[2]
        if self.task == "parametric":
            if condition is None:
                raise ValueError("the parametric task reads the electron count off its own condition vector")
            # the input is constant, so any one point carries the whole parameter vector it was broadcast from
            parameter_vector = np.asarray(input_function.values, dtype=np.float64)[:, 0, 0, 0]
            combined = np.concatenate(
                [
                    Constant_Channel_Field(parameter_vector, self.processing_shape),
                    Coordinate_Feature_Channels(self.processing_shape),
                ],
                axis=0,
            )
            weight_each = cell_volume / point_count
            standardized = np.asarray(
                self.Forward_From_Coarse_Input(self.Parameter_Values(), combined, query_features), dtype=np.float64
            )
            physical = self.Unstandardized_Target(standardized, query_features.shape[0])
            if self.conservation is None:
                raise ValueError("the parametric task always carries its own conservation wrapper")
            produced = np.asarray(
                self.conservation.Forward(physical, weight_each, np.asarray(condition.vector, dtype=np.float64)),
                dtype=np.float64,
            )
        else:
            density_values = np.asarray(input_function.values, dtype=np.float64)
            log_density = Log_Compressed_Input_Channels(density_values[0], density_values[1], self.reference_density)
            gram_vector = Standardized_Lattice_Gram(lattice, self.gram_mean, self.gram_scale)
            coarse_density = np.asarray(Spectral_Resampled(log_density, self.processing_shape), dtype=np.float64)
            gram_field = Constant_Channel_Field(gram_vector, self.processing_shape)
            combined = np.concatenate(
                [coarse_density, gram_field, Coordinate_Feature_Channels(self.processing_shape)], axis=0
            )
            produced = np.asarray(
                self.Forward_From_Coarse_Input(self.Parameter_Values(), combined, query_features), dtype=np.float64
            )
        reshaped = produced.T.reshape(len(self.channel_labels), *shape)
        self.last_predicted_values = reshaped
        quadrature = UniformGridQuadrature(cell_volume, point_count)
        return GridFunction(reshaped, self.channel_labels, input_function.domain, quadrature)


    def Predict_Density(
        self, parameters: Coefficients, output_discretization: Discretization, electron_count: float
    ) -> GridFunction:
        """the parametric task's own convenience: builds a minimal constant field and calls __call__"""
        vector = np.asarray(parameters.vector, dtype=np.float64)
        minimal_shape = (1, 1, 1)
        values = Constant_Channel_Field(vector, minimal_shape)
        lattice = np.asarray(parameters.domain.lattice, dtype=np.float64)
        quadrature = UniformGridQuadrature(cell_volume=float(abs(np.linalg.det(lattice))), point_count=1)
        labels = tuple(f"parameter_{component_number}" for component_number in range(vector.shape[0]))
        input_function = GridFunction(values, labels, parameters.domain, quadrature)
        condition = Coefficients(vector=np.asarray([electron_count], dtype=np.float64), domain=parameters.domain)
        return self(input_function, output_discretization, condition)


    def Inspect(self) -> dict[str, Array]:
        state = super().Inspect()
        state["processing_shape"] = np.asarray(self.processing_shape)
        if self.task == "localization":
            state["reference_density"] = np.asarray(self.reference_density)
            state["gram_standardization_mean"] = self.gram_mean
            state["gram_standardization_scale"] = self.gram_scale
        if self.task == "parametric" and self.density_voxel_mean is not None and self.density_voxel_scale is not None:
            state["density_voxel_mean"] = self.density_voxel_mean
            state["density_voxel_scale"] = self.density_voxel_scale
        if self.last_predicted_values is not None:
            state["last_predicted_values"] = self.last_predicted_values
        return state


def Galerkin_Attention_Layers(
    hidden_channels: int, head_count: int, layer_count: int, seed: int
) -> tuple[Layer[GridFunction], ...]:
    """the explicit stack's own layers, one attention kernel and one local linear term each, residual on"""
    return tuple(
        Layer(
            kernel=GalerkinAttentionKernel(hidden_channels, head_count=head_count, seed=seed + 4 * layer_index + 1),
            local_linear=PointwiseLift(hidden_channels, hidden_channels, seed=seed + 4 * layer_index + 3),
            residual=True,
        )
        for layer_index in range(layer_count)
    )


def Galerkin_Transformer_Network(
    task: GalerkinTransformerTask,
    processing_shape: tuple[int, int, int],
    hidden_channels: int = HIDDEN_CHANNELS,
    head_count: int = HEAD_COUNT,
    layer_count: int = ENCODER_LAYER_COUNT,
    reference_density: float = 1.0,
    gram_mean: NDArray[np.float64] | None = None,
    gram_scale: NDArray[np.float64] | None = None,
    density_voxel_mean: NDArray[np.float64] | None = None,
    density_voxel_scale: NDArray[np.float64] | None = None,
    seed: int = 0,
) -> GalerkinTransformer:
    """the gate configuration: coordinate-featured tokens, softmax-free attention layers, a query-point decoder"""
    if task == "parametric":
        input_channel_count = PEROVSKITE_LATTICE_FACTOR_COUNT + COORDINATE_FEATURES.feature_count
        channel_labels: tuple[str, ...] = PEROVSKITE_DENSITY_CHANNEL_LABELS
        bounded = False
        condition_channel_count = PEROVSKITE_LATTICE_FACTOR_COUNT
    else:
        input_channel_count = LOCALIZATION_INPUT_FIELD_CHANNEL_COUNT + COORDINATE_FEATURES.feature_count
        channel_labels = LOCALIZATION_CHANNEL_LABELS
        bounded = True
        condition_channel_count = 0
    lift = PointwiseLift(hidden_channels, input_channel_count, seed=seed)
    attention_stack = ExplicitStack(Galerkin_Attention_Layers(hidden_channels, head_count, layer_count, seed))
    decoder = QueryPointDecoder(
        hidden_channels,
        len(channel_labels),
        channel_labels,
        head_count=head_count,
        bounded=bounded,
        condition_channel_count=condition_channel_count,
        seed=seed + 4 * layer_count + 1,
    )
    return GalerkinTransformer(
        lift,
        attention_stack,
        decoder,
        task=task,
        processing_shape=processing_shape,
        reference_density=reference_density,
        gram_mean=gram_mean,
        gram_scale=gram_scale,
        density_voxel_mean=density_voxel_mean,
        density_voxel_scale=density_voxel_scale,
    )
