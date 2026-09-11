"""the shared encoders, readouts, compositions and wrappers"""

import tomllib
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.compositions import ExplicitStack
from operators.data import Gram_Pod, Project
from operators.encoders import AtomEmbedding, BasisProjectionEncoder, PointwiseLift, SensorEncoder, VariableEncoding
from operators.framework import (
    Array,
    Coefficients,
    Domain,
    Fractional_Grid_Coordinates,
    GridFunction,
    GridSpec,
    Layer,
    Operator,
    PointSet,
    PointSpec,
    UniformGridQuadrature,
)
from operators.kernels import SpectralKernel
from operators.readouts import (
    BasisExpansion,
    FixedModeExpansion,
    NonlinearDecoder,
    PeriodicCoordinateFeatures,
    PointwiseProjection,
    RampedCoordinateFeatures,
)
from operators.substrate import NumpyEngine, ParameterSet, Torch_Is_Available, TorchEngine
from operators.wrappers import (
    Conditioned,
    ConformalCalibrator,
    Conserving,
    Coverage_Deviation,
    Coverage_Guarantee,
    Nonconformity_Scores,
    Residual,
)

CONFIGURATION_DIRECTORY = Path(__file__).resolve().parent.parent / "residual_correction" / "configs"

CUBE = Domain(lattice=np.eye(3) * 2.0)

GRID_QUADRATURE = UniformGridQuadrature(cell_volume=8.0, point_count=64)


def Small_Field(channels: int, seed: int) -> GridFunction:
    """a random four-cubed field with the cube quadrature"""
    generator = np.random.default_rng(seed)
    labels = tuple(f"channel_{channel}" for channel in range(channels))
    return GridFunction(generator.random((channels, 4, 4, 4)), labels, CUBE, GRID_QUADRATURE)


def Labeled_Field(labels: tuple[str, ...], seed: int) -> GridFunction:
    """a random four-cubed field carrying the given physical channel labels"""
    generator = np.random.default_rng(seed)
    return GridFunction(generator.random((len(labels), 4, 4, 4)), labels, CUBE, GRID_QUADRATURE)


def Test_The_Lift_And_Projection_Mix_Channels() -> None:
    """channel counts change while the grid stays, and the bounded head stays in range"""
    field = Small_Field(2, seed=1)
    lift = PointwiseLift(hidden_channels=5, input_channels=2)
    lifted_field = lift(field, GridSpec((4, 4, 4)))
    assert np.asarray(lifted_field.values).shape == (5, 4, 4, 4)
    projection = PointwiseProjection(output_channels=1, hidden_channels=5, bounded=True)
    projected = projection(lifted_field, GridSpec((4, 4, 4)))
    produced = np.asarray(projected.values)
    assert produced.shape == (1, 4, 4, 4)
    assert float(produced.min()) >= 0.0 and float(produced.max()) <= 1.0
    assert "lift_weights" in lift.Inspect() and "projection_weights" in projection.Inspect()


def Test_The_Sensor_Encoder_Reads_Parameters() -> None:
    """a parameter vector reaches the latent width"""
    encoder = SensorEncoder(layer_widths=(3, 16, 8), seed=2)
    parameters = Coefficients(vector=np.asarray([0.1, -0.2, 0.3]), domain=CUBE)
    latent = encoder(parameters, PointSpec(np.zeros((1, 1))))
    assert np.asarray(latent.vector).shape == (8,)


ATOM_VOCABULARY = (
    ("C", "PAW_PBE C 08Apr2002"),
    ("C", "PAW_PBE C 06Sep2000"),
    ("Si", "PAW_PBE Si 05Jan2001"),
)


def Test_The_Atom_Embedding_Looks_Up_Each_Atom_By_Its_Pair() -> None:
    """the table row an atom gets depends on both its element and its pseudopotential title"""
    embedding = AtomEmbedding(ATOM_VOCABULARY, embedding_width=4, seed=41)
    species = np.asarray([["C", "PAW_PBE C 08Apr2002"], ["C", "PAW_PBE C 06Sep2000"]])
    point_set = PointSet(positions=np.zeros((2, 3)), domain=CUBE, species=species, roles=np.zeros(2))
    produced = embedding(point_set, PointSpec(np.zeros((1, 1))))
    assert np.asarray(produced.values).shape == (2, 4)
    assert produced.positions is point_set.positions
    assert produced.roles is point_set.roles
    # the same element under two pseudopotential titles must not share a row
    assert not np.allclose(np.asarray(produced.values)[0], np.asarray(produced.values)[1])
    assert "atom_embedding_table" in embedding.Inspect()


def Test_The_Atom_Embedding_Refuses_An_Unseen_Pair() -> None:
    """a pair the vocabulary never saw would otherwise silently reuse a stranger's row"""
    embedding = AtomEmbedding(ATOM_VOCABULARY, embedding_width=3, seed=42)
    species = np.asarray([["Si", "PAW_PBE Si 12Jan2000"]])
    point_set = PointSet(positions=np.zeros((1, 3)), domain=CUBE, species=species)
    with pytest.raises(ValueError):
        embedding(point_set, PointSpec(np.zeros((1, 1))))


def Test_The_Atom_Embedding_Paths_Agree() -> None:
    """the direct forward and the inference call produce the same numbers"""
    embedding = AtomEmbedding(ATOM_VOCABULARY, embedding_width=4, seed=43)
    species = np.asarray(
        [["Si", "PAW_PBE Si 05Jan2001"], ["C", "PAW_PBE C 08Apr2002"], ["Si", "PAW_PBE Si 05Jan2001"]]
    )
    point_set = PointSet(positions=np.zeros((3, 3)), domain=CUBE, species=species)
    through_call = np.asarray(embedding(point_set, PointSpec(np.zeros((1, 1)))).values)
    vocabulary_indices = embedding.Vocabulary_Indices(species)
    through_forward = np.asarray(embedding.Forward(embedding.parameter_values, vocabulary_indices))
    assert np.allclose(through_call, through_forward, atol=1e-12)


CHANNEL_VOCABULARY = ("charge_density", "magnetization", "local_potential_up")


def Test_The_Variable_Encoding_Widens_Each_Present_Channel() -> None:
    """every channel present becomes its own block of hidden_channels tokens"""
    encoding = VariableEncoding(CHANNEL_VOCABULARY, hidden_channels=4, condition_width=2, seed=44)
    field = Labeled_Field(("local_potential_up", "charge_density"), seed=45)
    produced = encoding(field, GridSpec((4, 4, 4)))
    assert np.asarray(produced.values).shape == (8, 4, 4, 4)
    assert len(produced.channel_labels) == 8
    assert "label_encodings" in encoding.Inspect()


def Test_The_Variable_Encoding_Refuses_An_Unknown_Channel_Label() -> None:
    """a channel outside the corpus vocabulary would otherwise silently borrow another label's row"""
    encoding = VariableEncoding(("charge_density",), hidden_channels=2, condition_width=1, seed=46)
    field = Labeled_Field(("electron_localization_up",), seed=47)
    with pytest.raises(ValueError):
        encoding(field, GridSpec((4, 4, 4)))


def Test_The_Variable_Encoding_Shares_Weights_Across_Present_Channels() -> None:
    """a channel's own encoding cannot depend on which other channels rode along with it"""
    encoding = VariableEncoding(CHANNEL_VOCABULARY, hidden_channels=3, condition_width=2, seed=48)
    generator = np.random.default_rng(49)
    density = generator.random((4, 4, 4))
    magnetization = generator.random((4, 4, 4))
    potential = generator.random((4, 4, 4))
    full = GridFunction(np.stack([density, magnetization, potential]), CHANNEL_VOCABULARY, CUBE, GRID_QUADRATURE)
    partial = GridFunction(
        np.stack([density, potential]), ("charge_density", "local_potential_up"), CUBE, GRID_QUADRATURE
    )
    full_produced = np.asarray(encoding(full, GridSpec((4, 4, 4))).values)
    partial_produced = np.asarray(encoding(partial, GridSpec((4, 4, 4))).values)
    # charge_density sits first in both channel sets, whatever else rides along with it
    assert np.allclose(full_produced[0:3], partial_produced[0:3])
    # local_potential_up moves from the last slot to the second, and must carry the same values there
    assert np.allclose(full_produced[6:9], partial_produced[3:6])


def Test_The_Variable_Encoding_Places_The_Covariate_In_The_Encoding_Not_A_New_Channel() -> None:
    """the functional covariate enters the encoding slot, so the token count never grows for it"""
    encoding = VariableEncoding(CHANNEL_VOCABULARY, hidden_channels=2, condition_width=3, seed=50)
    field = Labeled_Field(("charge_density", "magnetization"), seed=51)
    plain = encoding(field, GridSpec((4, 4, 4)), None)
    modulated = encoding(field, GridSpec((4, 4, 4)), Coefficients(vector=np.asarray([0.4, -0.2, 0.9]), domain=CUBE))
    assert np.asarray(plain.values).shape == np.asarray(modulated.values).shape == (4, 4, 4, 4)
    assert plain.channel_labels == modulated.channel_labels
    assert not np.allclose(np.asarray(plain.values), np.asarray(modulated.values))


def Test_The_Variable_Encoding_Paths_Agree() -> None:
    """the direct forward and the inference call produce the same numbers"""
    encoding = VariableEncoding(CHANNEL_VOCABULARY, hidden_channels=3, condition_width=2, seed=52)
    field = Labeled_Field(("magnetization", "charge_density"), seed=53)
    condition = Coefficients(vector=np.asarray([0.3, -0.7]), domain=CUBE)
    through_call = np.asarray(encoding(field, GridSpec((4, 4, 4)), condition).values)
    label_indices = encoding.Label_Indices(field.channel_labels)
    through_forward = np.asarray(
        encoding.Forward(
            encoding.parameter_values,
            np.asarray(field.values, dtype=np.float64),
            label_indices,
            np.asarray(condition.vector, dtype=np.float64),
        )
    )
    assert np.allclose(through_call, through_forward, atol=1e-12)


def Test_The_Basis_Projection_Recovers_Exact_Coefficients() -> None:
    """a field built from the basis projects back to its own coefficients"""
    generator = np.random.default_rng(3)
    raw = generator.random((2, 64))
    orthonormal, _ = np.linalg.qr(raw.T)
    basis_modes = orthonormal.T[:2]
    basis_mean = np.zeros(64)
    true_coefficients = np.asarray([1.5, -0.75])
    field_values = (true_coefficients @ basis_modes).reshape(1, 4, 4, 4)
    field = GridFunction(field_values, ("charge_density",), CUBE, GRID_QUADRATURE)
    encoder = BasisProjectionEncoder(basis_modes, basis_mean)
    coefficients = encoder(field, PointSpec(np.zeros((1, 1))))
    assert np.allclose(np.asarray(coefficients.vector), true_coefficients, atol=1e-12)


def Test_The_Basis_Expansion_Queries_Anywhere() -> None:
    """the trunk answers identically on a grid and on the same explicit points"""
    features = PeriodicCoordinateFeatures(fourier_orders=2)
    readout = BasisExpansion(latent_width=6, trunk_widths=(16,), coordinate_features=features, seed=4)
    branch = Coefficients(vector=np.arange(6.0) / 6.0, domain=CUBE)
    on_grid = readout(branch, GridSpec((4, 4, 4)))
    assert isinstance(on_grid, GridFunction)
    grid_points = Fractional_Grid_Coordinates((4, 4, 4))
    at_points = readout(branch, PointSpec(grid_points))
    assert isinstance(at_points, PointSet)
    grid_values = np.asarray(on_grid.values).reshape(-1)
    point_values = np.asarray(at_points.values).reshape(-1)
    assert np.allclose(grid_values, point_values, atol=1e-12)


def Test_The_Explicit_Stack_Chains_And_Inspects() -> None:
    """the stack applies its layers, and exposes prefixed kernel state"""
    kernel = SpectralKernel(kept_modes=(1, 1, 1), output_channels=2, input_channels=2, seed=5)
    kernel.Hermitian_Symmetrize()

    def Halving_Local_Linear(values: Array) -> Array:
        return np.asarray(values) * 0.5

    stack = ExplicitStack((Layer(kernel=kernel, local_linear=Halving_Local_Linear),))
    field = Small_Field(2, seed=6)
    produced = stack.Apply(field)
    assert np.asarray(produced.values).shape == (2, 4, 4, 4)
    inspected = stack.Inspect()
    assert "layer_0.kernel.mode_magnitudes" in inspected
    assert "last_layer_norms" in inspected


class FieldIdentity:
    """an inner operator returning its input unchanged"""


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: object,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        return input_function


    def Inspect(self) -> dict[str, Array]:
        return {}


def Test_The_Wrappers_Enforce_Their_Laws() -> None:
    """zero mean, electron-count renormalization, and the residual start"""
    field = Small_Field(1, seed=7)
    zero_mean = Conserving(FieldIdentity(), law="zero_mean")
    balanced = zero_mean(field, GridSpec((4, 4, 4)))
    assert abs(float(np.asarray(balanced.values).mean())) < 1e-12

    renormalize = Conserving(FieldIdentity(), law="renormalize_to_electron_count")
    electron_count = Coefficients(vector=np.asarray([8.0]), domain=CUBE)
    conserved = renormalize(field, GridSpec((4, 4, 4)), electron_count)
    integral = float(np.asarray(conserved.values).sum()) * (8.0 / 64)
    assert abs(integral - 8.0) < 1e-9

    class ZeroInner(FieldIdentity):
        """an inner operator returning all zeros"""


        def __call__(
            self,
            input_function: GridFunction,
            output_discretization: object,
            condition: Coefficients | None = None,
        ) -> GridFunction:
            zeros = np.zeros_like(np.asarray(input_function.values))
            return GridFunction(zeros, input_function.channel_labels, input_function.domain, input_function.quadrature)

    residual = Residual(ZeroInner())
    unchanged = residual(field, GridSpec((4, 4, 4)))
    assert np.allclose(np.asarray(unchanged.values), np.asarray(field.values))

    conditioned = Conditioned(FieldIdentity(), channels=1, condition_width=2, seed=8)
    plain = conditioned(field, GridSpec((4, 4, 4)), None)
    assert np.allclose(np.asarray(plain.values), np.asarray(field.values))
    modulated = conditioned(field, GridSpec((4, 4, 4)), Coefficients(vector=np.asarray([1.0, -0.5]), domain=CUBE))
    assert not np.allclose(np.asarray(modulated.values), np.asarray(field.values))


def Test_The_Fixed_Mode_Expansion_Inverts_The_Projection() -> None:
    """coefficients projected out of a field expand back to it through the same basis"""
    generator = np.random.default_rng(11)
    shape = (4, 4, 4)
    snapshots = generator.normal(size=(12, 4 * 4 * 4))
    basis = Gram_Pod(snapshots)
    readout = FixedModeExpansion(basis, shape)
    for snapshot in snapshots[:3]:
        coefficients = Project(basis, snapshot[None, :])[0]
        rebuilt = readout(Coefficients(vector=coefficients, domain=CUBE), GridSpec(shape))
        assert isinstance(rebuilt, GridFunction)
        # a full-rank basis rebuilds its own snapshots exactly
        assert np.allclose(np.asarray(rebuilt.values).reshape(-1), snapshot, atol=1e-10)


def Test_The_Fixed_Mode_Expansion_Truncates_To_Its_Rank() -> None:
    """a rank-limited basis leaves exactly the error its singular values predict"""
    generator = np.random.default_rng(12)
    snapshots = np.asarray(generator.normal(size=(10, 64)) @ generator.normal(size=(64, 64)), dtype=np.float64)
    truncated = Gram_Pod(snapshots, rank=3)
    readout = FixedModeExpansion(truncated, (4, 4, 4))
    first_snapshot = np.asarray(snapshots[0], dtype=np.float64)
    coefficients = Project(truncated, first_snapshot[None, :])[0]
    rebuilt = readout(Coefficients(vector=coefficients, domain=CUBE), GridSpec((4, 4, 4)))
    residual = np.asarray(rebuilt.values, dtype=np.float64).reshape(-1) - first_snapshot
    assert coefficients.shape == (3,)
    assert 0.0 < float(np.linalg.norm(residual)) < float(np.linalg.norm(first_snapshot - truncated.mean))


def Test_The_Fixed_Mode_Expansion_Inspects_Its_Basis() -> None:
    """the modes, their singular values, the mean and the last coefficients are all reachable"""
    generator = np.random.default_rng(13)
    basis = Gram_Pod(generator.normal(size=(6, 64)), rank=4)
    readout = FixedModeExpansion(basis, (4, 4, 4))
    assert set(readout.Inspect()) == {"basis_modes", "basis_singular_values", "basis_mean"}
    readout(Coefficients(vector=np.ones(4), domain=CUBE), GridSpec((4, 4, 4)))
    inspected = readout.Inspect()
    # a mode is a field, and is inspected with the shape that makes it one
    assert inspected["basis_modes"].shape == (4, 4, 4, 4)
    assert inspected["basis_mean"].shape == (4, 4, 4)
    assert inspected["basis_singular_values"].shape == (4,)
    assert inspected["last_coefficients"].shape == (4,)
    # and the shaping must be a view of the same numbers, not a different quantity
    assert np.array_equal(np.asarray(inspected["basis_modes"]).reshape(4, 64), basis.modes)


def Test_The_Fixed_Mode_Expansion_Lifts_Its_Basis_As_Constants() -> None:
    """the modes and mean cross the engine facet unchanged, so only the branch carries gradient"""
    generator = np.random.default_rng(14)
    basis = Gram_Pod(generator.normal(size=(6, 64)), rank=4)
    readout = FixedModeExpansion(basis, (4, 4, 4))
    lifted_modes, lifted_mean = readout.Lifted_Constants(NumpyEngine())
    branch = np.ones(4)
    through_the_facet = readout.Forward(branch, lifted_modes, lifted_mean)
    directly = readout.Forward(branch, basis.modes, basis.mean)
    assert np.allclose(np.asarray(through_the_facet), np.asarray(directly))


def Test_The_Periodic_Features_Repeat_Where_The_Cell_Does() -> None:
    """the same physical point reached from either face reads identically, exactly"""
    features = PeriodicCoordinateFeatures(fourier_orders=4)
    # x = 0 and x = 1 are one place in a repeating cell, as are y = 0 and y = 1
    same_place = np.asarray([[0.0, 0.3, 0.7], [1.0, 0.3, 0.7], [0.0, 1.3, 0.7], [0.0, 0.3, -0.3]])
    read = features(same_place)
    assert read.shape == (4, features.feature_count)
    # a whole turn of a sine leaves floating dust, nothing a field could carry
    assert float(np.abs(read[1:] - read[0]).max()) < 1e-12


def Test_The_Periodic_Trunk_Cannot_Seam_At_The_Cell_Face() -> None:
    """a whole trunk answers one number at one point, whichever face names it"""
    readout = BasisExpansion(latent_width=8, trunk_widths=(32, 32), seed=0)
    branch = Coefficients(vector=np.arange(8.0) / 8.0, domain=CUBE)
    same_place = np.asarray([[0.0, 0.3, 0.7], [1.0, 0.3, 0.7]])
    values = np.asarray(
        readout.Forward(
            readout.parameter_values,
            np.asarray(branch.vector, dtype=np.float64),
            readout.Coordinate_Features(same_place),
        ),
        dtype=np.float64,
    )
    # the ramped map disagreed with itself by 0.079 here, fourteen orders of magnitude worse
    assert float(abs(values[1] - values[0])) < 1e-12


def Test_The_Ramped_Features_Keep_The_Axis_That_Does_Not_Repeat() -> None:
    """the ramped map carries the raw coordinate, which is what an energy axis needs"""
    energy_features = RampedCoordinateFeatures(fourier_orders=3, axis_count=1)
    assert energy_features.feature_count == 1 + 2 * 3 * 1
    read = energy_features(np.asarray([[0.0], [1.0]]))
    assert read.shape == (2, energy_features.feature_count)
    # the raw column is exactly what separates the two ends of a window that does not wrap
    assert float(read[1][0] - read[0][0]) == 1.0
    assert np.allclose(read[1][1:], read[0][1:])


def Test_The_Feature_Counts_Match_What_The_Trunk_Was_Built_For() -> None:
    """each map reports the width the perceptron's first layer is sized to"""
    for features in (
        PeriodicCoordinateFeatures(fourier_orders=2),
        RampedCoordinateFeatures(fourier_orders=2, axis_count=3),
        RampedCoordinateFeatures(fourier_orders=5, axis_count=1),
    ):
        points = np.zeros((3, features.axis_count), dtype=np.float64)
        assert features(points).shape[1] == features.feature_count
        readout = BasisExpansion(latent_width=4, trunk_widths=(8,), coordinate_features=features)
        first_layer = readout.parameter_values["trunk_layer_0_weights"]
        assert first_layer.shape[1] == features.feature_count


def Test_The_Trunk_Splits_The_Branch_Across_Output_Channels() -> None:
    """one shared trunk, one latent row per channel, each channel its own field"""
    labels = ("electron_localization_up", "electron_localization_down")
    readout = BasisExpansion(latent_width=6, trunk_widths=(16,), output_channel_labels=labels, seed=2)
    generator = np.random.default_rng(3)
    branch = np.asarray(generator.normal(size=(2, 6)), dtype=np.float64)
    produced = readout(Coefficients(vector=branch, domain=CUBE), GridSpec((4, 4, 4)))
    assert isinstance(produced, GridFunction)
    assert produced.channel_labels == labels
    values = np.asarray(produced.values, dtype=np.float64)
    assert values.shape == (2, 4, 4, 4)
    # the channels share a trunk but not a branch row, so they must not come out equal
    assert not np.allclose(values[0], values[1])


def Test_Each_Channel_Matches_The_Trunk_Run_On_Its_Own() -> None:
    """a split branch agrees channel for channel with single-channel readouts sharing the trunk"""
    labels = ("first_channel", "second_channel")
    together = BasisExpansion(latent_width=6, trunk_widths=(16,), output_channel_labels=labels, seed=7)
    alone = BasisExpansion(latent_width=6, trunk_widths=(16,), seed=7)
    generator = np.random.default_rng(8)
    branch = np.asarray(generator.normal(size=(2, 6)), dtype=np.float64)
    both_channels = together(Coefficients(vector=branch, domain=CUBE), GridSpec((4, 4, 4)))
    assert isinstance(both_channels, GridFunction)
    joint = np.asarray(both_channels.values, dtype=np.float64)
    for channel_index in range(2):
        one_channel = alone(Coefficients(vector=branch[channel_index], domain=CUBE), GridSpec((4, 4, 4)))
        assert isinstance(one_channel, GridFunction)
        assert np.allclose(joint[channel_index], np.asarray(one_channel.values, dtype=np.float64)[0])


def Test_The_Trunk_Refuses_A_Branch_That_Miscounts_Its_Channels() -> None:
    """a branch offering the wrong number of rows is a mistake, not a broadcast"""
    readout = BasisExpansion(latent_width=6, trunk_widths=(16,), output_channel_labels=("only_one",), seed=1)
    branch = np.zeros((3, 6), dtype=np.float64)
    with pytest.raises(ValueError):
        readout(Coefficients(vector=branch, domain=CUBE), GridSpec((4, 4, 4)))


def Test_The_Multi_Channel_Trunk_Still_Queries_Anywhere() -> None:
    """both channels answer identically on a grid and on the same explicit points"""
    labels = ("first_channel", "second_channel")
    readout = BasisExpansion(latent_width=5, trunk_widths=(12,), output_channel_labels=labels, seed=5)
    branch = Coefficients(vector=np.arange(10.0).reshape(2, 5) / 10.0, domain=CUBE)
    on_grid = readout(branch, GridSpec((4, 4, 4)))
    at_points = readout(branch, PointSpec(Fractional_Grid_Coordinates((4, 4, 4))))
    assert isinstance(on_grid, GridFunction) and isinstance(at_points, PointSet)
    grid_values = np.asarray(on_grid.values, dtype=np.float64).reshape(2, -1)
    point_values = np.asarray(at_points.values, dtype=np.float64).T
    assert np.allclose(grid_values, point_values, atol=1e-12)


def Test_The_Sensor_Encoder_Captures_The_Latent_It_Produces() -> None:
    """the branch's output is the thing the member exists to make, so it must be reachable"""
    encoder = SensorEncoder((3, 8, 5), seed=1)
    assert "last_latent_vector" not in encoder.Inspect()
    produced = encoder(Coefficients(vector=np.asarray([0.2, -0.4, 0.6]), domain=CUBE), GridSpec((2, 2, 2)))
    inspected = encoder.Inspect()
    assert inspected["last_latent_vector"].shape == (5,)
    assert np.allclose(inspected["last_latent_vector"], np.asarray(produced.vector))


def Test_The_Trunk_Features_Carry_The_Grid_When_The_Query_Had_One() -> None:
    """a feature evaluated over a grid is a field, and a feature over loose points is not"""
    readout = BasisExpansion(latent_width=4, trunk_widths=(8,), seed=2)
    feature_count = readout.coordinate_features.feature_count
    branch = Coefficients(vector=np.ones(4), domain=CUBE)
    readout(branch, GridSpec((4, 4, 4)))
    assert readout.Inspect()["last_trunk_features"].shape == (4, 4, 4, feature_count)
    readout(branch, PointSpec(np.asarray([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])))
    assert readout.Inspect()["last_trunk_features"].shape == (2, feature_count)


def Test_The_Basis_Projection_Encoder_Regains_The_Grid_It_Was_Shown() -> None:
    """this encoder is handed the shape with the field, and keeps it once it has seen one"""
    generator = np.random.default_rng(15)
    orthonormal, _ = np.linalg.qr(generator.normal(size=(64, 64)))
    encoder = BasisProjectionEncoder(orthonormal.T[:3], np.zeros(64))
    # before any field it cannot know, and says so by leaving the mean flat
    assert encoder.Inspect()["basis_mean"].shape == (64,)
    field = GridFunction(
        generator.normal(size=(1, 4, 4, 4)), ("charge_density",), CUBE, UniformGridQuadrature(1.0, 64)
    )
    encoder(field, GridSpec((4, 4, 4)))
    inspected = encoder.Inspect()
    assert inspected["basis_mean"].shape == (4, 4, 4)
    assert inspected["basis_modes"].shape == (3, 4, 4, 4)


def Test_The_Conservation_Laws_Are_Named_Apart() -> None:
    """one key meaning a removed mean under one law and a scale under the other told nobody which"""
    generator = np.random.default_rng(16)
    values = generator.normal(size=(1, 4, 4, 4)) + 3.0
    field = GridFunction(values, ("charge_density",), CUBE, UniformGridQuadrature(8.0, 64))
    inner = PointwiseProjection(output_channels=1, hidden_channels=1, seed=0)

    zero_mean = Conserving(inner, "zero_mean")
    zero_mean(field, GridSpec((4, 4, 4)))
    removed = zero_mean.Inspect()
    assert "last_removed_mean" in removed and "last_renormalization_scale" not in removed
    # the doctrine asks for scalars as zero-dimensional arrays, and this is one
    assert np.asarray(removed["last_removed_mean"]).ndim == 0

    renormalizing = Conserving(inner, "renormalize_to_electron_count")
    renormalizing(field, GridSpec((4, 4, 4)), Coefficients(vector=np.asarray([8.0]), domain=CUBE))
    scaled = renormalizing.Inspect()
    assert "last_renormalization_scale" in scaled and "last_removed_mean" not in scaled
    assert np.asarray(scaled["last_renormalization_scale"]).ndim == 0


CONSERVATION_LAWS: tuple[Literal["renormalize_to_electron_count", "zero_mean"], ...] = (
    "renormalize_to_electron_count",
    "zero_mean",
)

SMALL_GRID = GridSpec((4, 4, 4))

WEIGHT_EACH = GRID_QUADRATURE.cell_volume / GRID_QUADRATURE.point_count

ELECTRON_COUNT = Coefficients(vector=np.asarray([8.0]), domain=CUBE)


def Residual_Loss(
    wrapper: Residual, inner: PointwiseLift, field_values: Any, target: Any
) -> Callable[[dict[str, Any]], Any]:
    """the squared gap between the residual wrapper's field and a fixed target, as a forward an engine drives"""

    def Loss(lifted: dict[str, Any]) -> Any:
        difference = wrapper.Forward(field_values, inner.Forward(lifted, field_values)) - target
        return (difference * difference).sum()

    return Loss


def Conserving_Loss(
    wrapper: Conserving, inner: PointwiseLift, field_values: Any, target: Any, condition_vector: Any
) -> Callable[[dict[str, Any]], Any]:
    """the same squared gap, taken after the conservation law has been imposed"""

    def Loss(lifted: dict[str, Any]) -> Any:
        corrected = wrapper.Forward(inner.Forward(lifted, field_values), WEIGHT_EACH, condition_vector)
        difference = corrected - target
        return (difference * difference).sum()

    return Loss


def Conditioned_Loss(
    wrapper: Conditioned, inner: PointwiseLift, field_values: Any, target: Any, condition_vector: Any
) -> Callable[[dict[str, Any]], Any]:
    """the same squared gap, taken after the conditioning weights have modulated the channels"""

    def Loss(lifted: dict[str, Any]) -> Any:
        difference = wrapper.Forward(lifted, inner.Forward(lifted, field_values), condition_vector) - target
        return (difference * difference).sum()

    return Loss


def Atom_Embedding_Loss(
    embedding: AtomEmbedding, vocabulary_indices: Any, target: Any
) -> Callable[[dict[str, Any]], Any]:
    """the squared gap between the gathered rows and a fixed target, as a forward an engine drives"""

    def Loss(lifted: dict[str, Any]) -> Any:
        difference = embedding.Forward(lifted, vocabulary_indices) - target
        return (difference * difference).sum()

    return Loss


def Variable_Encoding_Loss(
    encoding: VariableEncoding, channel_values: Any, label_indices: Any, condition_vector: Any, target: Any
) -> Callable[[dict[str, Any]], Any]:
    """the squared gap between the produced tokens and a fixed target, as a forward an engine drives"""

    def Loss(lifted: dict[str, Any]) -> Any:
        difference = encoding.Forward(lifted, channel_values, label_indices, condition_vector) - target
        return (difference * difference).sum()

    return Loss


def Agreeing_Gradients(
    parameters: ParameterSet,
    lifted_loss: Callable[[dict[str, Any]], Any],
    reference_loss: Callable[[dict[str, Any]], Any],
) -> dict[str, NDArray[np.float64]]:
    """the differentiable engine's gradients, checked against the finite-difference oracle and handed back"""
    value, gradients = TorchEngine().Value_And_Gradients(parameters, lifted_loss)
    reference = NumpyEngine()
    assert abs(value - reference.Evaluate(parameters, reference_loss)) < 1e-10
    reference_gradients = reference.Gradients(parameters, reference_loss)
    assert set(gradients) == set(reference_gradients)
    for name, gradient in gradients.items():
        assert np.allclose(gradient, reference_gradients[name], rtol=1e-5, atol=1e-6), name
    return gradients


def Largest_Gap(through_the_engine: Any, through_numpy: Any) -> float:
    """the worst the two paths disagree by anywhere, in the units the field is written in"""
    engine_values = np.asarray(through_the_engine, dtype=np.float64)
    numpy_values = np.asarray(through_numpy, dtype=np.float64)
    return float(np.abs(engine_values - numpy_values).max())


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_The_Residual_Wrapper_Carries_Gradients_To_The_Operator_Inside_It() -> None:
    """the member whose whole identity is wrappers over a backbone could not be trained through this one at all"""
    inner = PointwiseLift(hidden_channels=2, input_channels=2, seed=21)
    wrapper = Residual(inner)
    field_values = np.asarray(Small_Field(2, seed=22).values, dtype=np.float64)
    target = np.random.default_rng(23).random((2, 4, 4, 4))
    parameters = ParameterSet(values={name: value.copy() for name, value in inner.parameter_values.items()})
    engine = TorchEngine()
    gradients = Agreeing_Gradients(
        parameters,
        Residual_Loss(wrapper, inner, engine.Lift_Constant(field_values), engine.Lift_Constant(target)),
        Residual_Loss(wrapper, inner, field_values, target),
    )
    for name, gradient in gradients.items():
        # a tape severed anywhere between the weight and the loss reads here as an exactly zero gradient
        assert float(np.abs(gradient).max()) > 1e-6, name


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
@pytest.mark.parametrize("law", CONSERVATION_LAWS)
def Test_Each_Conservation_Law_Carries_Gradients_To_The_Operator_Inside_It(
    law: Literal["renormalize_to_electron_count", "zero_mean"],
) -> None:
    """the projection is part of the model, so the gradient has to come home through it"""
    inner = PointwiseLift(hidden_channels=2, input_channels=2, seed=24)
    wrapper = Conserving(inner, law)
    field_values = np.asarray(Small_Field(2, seed=25).values, dtype=np.float64)
    target = np.random.default_rng(26).random((2, 4, 4, 4))
    count_vector = np.asarray(ELECTRON_COUNT.vector, dtype=np.float64)
    parameters = ParameterSet(values={name: value.copy() for name, value in inner.parameter_values.items()})
    engine = TorchEngine()
    gradients = Agreeing_Gradients(
        parameters,
        Conserving_Loss(
            wrapper,
            inner,
            engine.Lift_Constant(field_values),
            engine.Lift_Constant(target),
            engine.Lift_Constant(count_vector),
        ),
        Conserving_Loss(wrapper, inner, field_values, target, count_vector),
    )
    assert float(np.abs(gradients["lift_weights"]).max()) > 1e-6
    if law == "zero_mean":
        # the law takes any uniform offset back off again, so a bias that only shifts cannot reach the loss
        assert float(np.abs(gradients["lift_biases"]).max()) < 1e-12
    else:
        assert float(np.abs(gradients["lift_biases"]).max()) > 1e-6


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_The_Conditioning_Weights_Are_Reached_Alongside_The_Operator_Inside() -> None:
    """these weights sat outside every parameter set, where nothing that trains the model could move them"""
    inner = PointwiseLift(hidden_channels=2, input_channels=2, seed=27)
    wrapper = Conditioned(inner, channels=2, condition_width=1, seed=28)
    field_values = np.asarray(Small_Field(2, seed=29).values, dtype=np.float64)
    target = np.random.default_rng(30).random((2, 4, 4, 4))
    count_vector = np.asarray(ELECTRON_COUNT.vector, dtype=np.float64)
    parameters = ParameterSet(
        values={
            name: value.copy()
            for source in (inner.parameter_values, wrapper.parameter_values)
            for name, value in source.items()
        }
    )
    engine = TorchEngine()
    gradients = Agreeing_Gradients(
        parameters,
        Conditioned_Loss(
            wrapper,
            inner,
            engine.Lift_Constant(field_values),
            engine.Lift_Constant(target),
            engine.Lift_Constant(count_vector),
        ),
        Conditioned_Loss(wrapper, inner, field_values, target, count_vector),
    )
    assert set(gradients) == {
        "lift_weights",
        "lift_biases",
        "condition_scale_weights",
        "condition_shift_weights",
    }
    for name, gradient in gradients.items():
        assert float(np.abs(gradient).max()) > 1e-6, name


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_The_Atom_Embedding_Carries_Gradients_To_Its_Table() -> None:
    """the table is what training moves, so a forward that could not reach it could not be trained"""
    embedding = AtomEmbedding(ATOM_VOCABULARY, embedding_width=3, seed=54)
    species = np.asarray(
        [["Si", "PAW_PBE Si 05Jan2001"], ["C", "PAW_PBE C 08Apr2002"], ["Si", "PAW_PBE Si 05Jan2001"]]
    )
    vocabulary_indices = embedding.Vocabulary_Indices(species)
    target = np.random.default_rng(55).random((3, 3))
    parameters = ParameterSet(values={name: value.copy() for name, value in embedding.parameter_values.items()})
    engine = TorchEngine()
    gradients = Agreeing_Gradients(
        parameters,
        Atom_Embedding_Loss(embedding, vocabulary_indices, engine.Lift_Constant(target)),
        Atom_Embedding_Loss(embedding, vocabulary_indices, target),
    )
    assert float(np.abs(gradients["atom_embedding_table"]).max()) > 1e-6
    # this vocabulary's second row never appears among these atoms, and must get exactly no gradient
    untouched_rows = sorted(set(range(len(ATOM_VOCABULARY))) - set(vocabulary_indices.tolist()))
    assert untouched_rows == [1]
    assert float(np.abs(gradients["atom_embedding_table"][1]).max()) < 1e-12


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_The_Variable_Encoding_Carries_Gradients_To_Its_Tables() -> None:
    """the lift, the per-label rows and the covariate projection are all what training moves"""
    encoding = VariableEncoding(CHANNEL_VOCABULARY, hidden_channels=2, condition_width=2, seed=56)
    field = Labeled_Field(("charge_density", "magnetization"), seed=57)
    label_indices = encoding.Label_Indices(field.channel_labels)
    channel_values = np.asarray(field.values, dtype=np.float64)
    condition_vector = np.asarray([0.5, -0.1], dtype=np.float64)
    target = np.random.default_rng(58).random((4, 4, 4, 4))
    parameters = ParameterSet(values={name: value.copy() for name, value in encoding.parameter_values.items()})
    engine = TorchEngine()
    gradients = Agreeing_Gradients(
        parameters,
        Variable_Encoding_Loss(
            encoding,
            engine.Lift_Constant(channel_values),
            label_indices,
            engine.Lift_Constant(condition_vector),
            engine.Lift_Constant(target),
        ),
        Variable_Encoding_Loss(encoding, channel_values, label_indices, condition_vector, target),
    )
    assert set(gradients) == {
        "token_lift_weights",
        "token_lift_biases",
        "label_encodings",
        "condition_projection_weights",
    }
    for name, gradient in gradients.items():
        assert float(np.abs(gradient).max()) > 1e-6, name
    # this vocabulary's third row, local_potential_up, never appears among these channels
    assert float(np.abs(gradients["label_encodings"][2]).max()) < 1e-12


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_The_Variable_Encoding_Trains_Without_A_Covariate() -> None:
    """the encoding slot's covariate is optional, so the rest of the table must not need it either"""
    encoding = VariableEncoding(CHANNEL_VOCABULARY, hidden_channels=2, condition_width=2, seed=59)
    field = Labeled_Field(("charge_density", "magnetization"), seed=60)
    label_indices = encoding.Label_Indices(field.channel_labels)
    channel_values = np.asarray(field.values, dtype=np.float64)
    target = np.random.default_rng(61).random((4, 4, 4, 4))
    trainable_names = ("token_lift_weights", "token_lift_biases", "label_encodings")
    parameters = ParameterSet(values={name: encoding.parameter_values[name].copy() for name in trainable_names})
    engine = TorchEngine()
    gradients = Agreeing_Gradients(
        parameters,
        Variable_Encoding_Loss(
            encoding, engine.Lift_Constant(channel_values), label_indices, None, engine.Lift_Constant(target)
        ),
        Variable_Encoding_Loss(encoding, channel_values, label_indices, None, target),
    )
    for name, gradient in gradients.items():
        assert float(np.abs(gradient).max()) > 1e-6, name


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_Each_Wrapper_Answers_The_Same_On_Either_Engine() -> None:
    """the differentiable engine is a way of differentiating the wrappers, not a different set of wrappers"""
    inner = PointwiseLift(hidden_channels=2, input_channels=2, seed=31)
    field = Small_Field(2, seed=32)
    count_vector = np.asarray(ELECTRON_COUNT.vector, dtype=np.float64)
    engine = TorchEngine()
    lifted = engine.Lift(inner.parameter_values, requires_gradient=False)
    lifted_field = engine.Lift_Constant(np.asarray(field.values, dtype=np.float64))
    lifted_count = engine.Lift_Constant(count_vector)
    produced = inner.Forward(lifted, lifted_field)

    residual = Residual(inner)
    inferred = residual(field, SMALL_GRID, ELECTRON_COUNT)
    assert Largest_Gap(residual.Forward(lifted_field, produced), inferred.values) < 1e-12

    for law in CONSERVATION_LAWS:
        conserving = Conserving(inner, law)
        inferred = conserving(field, SMALL_GRID, ELECTRON_COUNT)
        through_the_engine = conserving.Forward(produced, WEIGHT_EACH, lifted_count)
        assert Largest_Gap(through_the_engine, inferred.values) < 1e-12, law

    conditioned = Conditioned(inner, channels=2, condition_width=1, seed=33)
    lifted_conditioning = engine.Lift(conditioned.parameter_values, requires_gradient=False)
    inferred = conditioned(field, SMALL_GRID, ELECTRON_COUNT)
    through_the_engine = conditioned.Forward(lifted_conditioning, produced, lifted_count)
    assert Largest_Gap(through_the_engine, inferred.values) < 1e-12


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_The_Zero_Mean_Law_Holds_Channel_By_Channel_On_Both_Paths() -> None:
    """each channel's own mean, not the field's, and on the engine that trains as well as the one that infers"""
    inner = PointwiseLift(hidden_channels=3, input_channels=2, seed=34)
    field = Small_Field(2, seed=35)
    wrapper = Conserving(inner, "zero_mean")
    balanced = np.asarray(wrapper(field, SMALL_GRID).values, dtype=np.float64)
    assert float(np.abs(balanced.mean(axis=(1, 2, 3))).max()) < 1e-14
    # channels that already shared an offset would let a single global mean pass this unnoticed
    before = np.asarray(inner(field, SMALL_GRID).values, dtype=np.float64).mean(axis=(1, 2, 3))
    assert float(before.max() - before.min()) > 1e-3

    engine = TorchEngine()
    lifted = engine.Lift(inner.parameter_values, requires_gradient=False)
    produced = inner.Forward(lifted, engine.Lift_Constant(np.asarray(field.values, dtype=np.float64)))
    through_the_engine = np.asarray(wrapper.Forward(produced, WEIGHT_EACH), dtype=np.float64)
    assert float(np.abs(through_the_engine.mean(axis=(1, 2, 3))).max()) < 1e-14


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_The_Renormalized_Density_Lands_On_The_Requested_Count_On_Both_Paths() -> None:
    """the archived fields integrate to their own count within 2e-7, so a scale left over here is model error"""
    inner = PointwiseLift(hidden_channels=1, input_channels=1, seed=36)
    field = Small_Field(1, seed=37)
    wrapper = Conserving(inner, "renormalize_to_electron_count")
    conserved = np.asarray(wrapper(field, SMALL_GRID, ELECTRON_COUNT).values, dtype=np.float64)
    assert abs(float(conserved.sum()) * WEIGHT_EACH - 8.0) < 1e-13

    scale = float(np.asarray(wrapper.Inspect()["last_renormalization_scale"]))
    # a diagnostic that is not the factor actually applied diagnoses nothing
    unscaled = np.asarray(inner(field, SMALL_GRID, ELECTRON_COUNT).values, dtype=np.float64)
    assert Largest_Gap(conserved, unscaled * scale) < 1e-14

    engine = TorchEngine()
    lifted = engine.Lift(inner.parameter_values, requires_gradient=False)
    produced = inner.Forward(lifted, engine.Lift_Constant(np.asarray(field.values, dtype=np.float64)))
    lifted_count = engine.Lift_Constant(np.asarray(ELECTRON_COUNT.vector, dtype=np.float64))
    through_the_engine = np.asarray(wrapper.Forward(produced, WEIGHT_EACH, lifted_count), dtype=np.float64)
    assert abs(float(through_the_engine.sum()) * WEIGHT_EACH - 8.0) < 1e-13


def Test_Each_Wrapper_Inspects_The_Operator_It_Wraps() -> None:
    """a wrapper that swallowed its backbone's state would hide the whole model from every renderer"""
    inner = PointwiseLift(hidden_channels=2, input_channels=2, seed=38)
    field = Small_Field(2, seed=39)
    conditioned = Conditioned(inner, channels=2, condition_width=1, seed=40)
    wrappers: tuple[Operator[GridFunction, GridFunction], ...] = (
        Residual(inner),
        Conserving(inner, "zero_mean"),
        Conserving(inner, "renormalize_to_electron_count"),
        conditioned,
    )
    for wrapper in wrappers:
        wrapper(field, SMALL_GRID, ELECTRON_COUNT)
        inspected = wrapper.Inspect()
        assert set(inspected) >= {f"inner.{name}" for name in inner.Inspect()}
        for name, value in inner.Inspect().items():
            assert np.array_equal(np.asarray(inspected[f"inner.{name}"]), np.asarray(value))
    assert {"condition_scale_weights", "condition_shift_weights"} <= set(conditioned.Inspect())


def Lone_Orbits(count: int) -> list[str]:
    """one exchangeable unit per run, which is the loosest the calibrator is ever given"""
    return [f"orbit_{place}" for place in range(count)]


def Test_The_Offset_Sits_At_The_Rank_A_Finite_Calibration_Set_Needs() -> None:
    """the claim is distribution-free only at the rank the sample size pays for"""
    truth = np.arange(1.0, 61.0) / 60.0
    calibrator = ConformalCalibrator(level=0.90)
    # an interval pinned on zero makes each run's score its own truth, which is the rank we can read
    offset = calibrator.Calibrate(np.zeros(60), np.zeros(60), truth, Lone_Orbits(60))
    assert abs(offset - 55.0 / 60.0) < 1e-12
    widened = calibrator(np.zeros(4), np.zeros(4))
    assert np.allclose(widened.upper - widened.lower, 2.0 * offset)


def Test_The_Guarantee_Reproduces_The_Numbers_The_Suite_Recorded() -> None:
    """the suite states the arithmetic in the document, and this is it"""
    guarantee_low, guarantee_high = Coverage_Guarantee(60, 0.90)
    assert guarantee_low == 0.90
    assert round(guarantee_high, 3) == 0.916
    assert abs(Coverage_Deviation(60, 0.90) - 0.04) < 0.002
    assert abs(Coverage_Deviation(90, 0.90) - 0.032) < 0.001


def Test_A_Crowded_Orbit_Cannot_Buy_A_Wider_Interval() -> None:
    """1,291 points are 299 units, and a forty-copy orbit is one of them"""
    crowded = np.full(40, 10.0)
    lone = np.ones(20)
    truth = np.concatenate([crowded, lone])
    unit_keys = ["one_orbit"] * 40 + Lone_Orbits(20)
    calibrator = ConformalCalibrator(level=0.90)
    offset = calibrator.Calibrate(np.zeros(60), np.zeros(60), truth, unit_keys)
    assert int(np.asarray(calibrator.Inspect()["calibration_unit_count"])) == 21
    assert abs(offset - 1.0) < 1e-12
    # counting the points instead of the units would have read the crowded orbit's 10.0 here
    counted_by_point = ConformalCalibrator(level=0.90)
    assert abs(counted_by_point.Calibrate(np.zeros(60), np.zeros(60), truth, Lone_Orbits(60)) - 10.0) < 1e-12


def Test_The_Calibrated_Interval_Covers_Held_Out_Units_At_Its_Level() -> None:
    """a head whose own quantiles cover 38% of the time is dragged up to its stated 90%"""
    generator = np.random.default_rng(2026)
    unit_count = 299
    calibration_truth = generator.normal(size=unit_count)
    calibrator = ConformalCalibrator(level=0.90)
    calibrator.Calibrate(
        np.full(unit_count, -0.5), np.full(unit_count, 0.5), calibration_truth, Lone_Orbits(unit_count)
    )
    held_out = generator.normal(size=4000)
    widened = calibrator(np.full(4000, -0.5), np.full(4000, 0.5))
    covered = float(np.mean((widened.lower <= held_out) & (held_out <= widened.upper)))
    uncalibrated = float(np.mean(np.abs(held_out) <= 0.5))
    assert uncalibrated < 0.45
    guarantee_low, guarantee_high = Coverage_Guarantee(unit_count, 0.90)
    # one calibration draw scatters by its own deviation, and three of those is the honest band
    assert guarantee_low - 3.0 * Coverage_Deviation(unit_count, 0.90) <= covered <= guarantee_high + 0.03


def Test_A_Field_Score_Is_The_Largest_Miss_Anywhere_In_The_Run() -> None:
    """a band over a whole field is only honest if one bad voxel costs the whole run"""
    lower = np.zeros((2, 1, 2, 2, 2))
    upper = np.ones((2, 1, 2, 2, 2))
    truth = np.full((2, 1, 2, 2, 2), 0.7)
    truth[0, 0, 1, 1, 1] = 3.0
    scores = Nonconformity_Scores(lower, upper, truth)
    assert abs(float(scores[0]) - 2.0) < 1e-12
    assert abs(float(scores[1]) + 0.3) < 1e-12


def Test_Too_Few_Units_Cannot_Carry_The_Claim() -> None:
    """at five units no offset makes a 90 percent distribution-free statement true"""
    calibrator = ConformalCalibrator(level=0.90)
    with pytest.raises(ValueError):
        calibrator.Calibrate(np.zeros(5), np.zeros(5), np.arange(5.0), Lone_Orbits(5))


def Test_An_Uncalibrated_Calibrator_Widens_Nothing() -> None:
    """an interval with no calibration behind it carries no guarantee, so it is refused"""
    calibrator = ConformalCalibrator()
    assert set(calibrator.Inspect()) == {"requested_level", "exchangeable_unit"}
    with pytest.raises(ValueError):
        calibrator(np.zeros(3), np.ones(3))


def Test_The_Calibrator_Is_Built_From_The_Configuration_As_It_Is_Written() -> None:
    """the configuration files were written before the calibrator, and they name its arguments"""
    configurations = sorted(CONFIGURATION_DIRECTORY.glob("*.toml"))
    assert len(configurations) == 2
    for configuration_path in configurations:
        settings = tomllib.loads(configuration_path.read_text())
        calibrator = ConformalCalibrator(**settings["conformal"])
        assert calibrator.level == 0.90
        assert calibrator.unit == "symmetry_orbit"
        assert str(calibrator.Inspect()["exchangeable_unit"]) == "symmetry_orbit"


def Test_The_Nonlinear_Decoder_Queries_Anywhere() -> None:
    """the network answers identically on a grid and on the same explicit points"""
    features = PeriodicCoordinateFeatures(fourier_orders=2)
    readout = NonlinearDecoder(latent_width=6, hidden_widths=(16,), coordinate_features=features, seed=9)
    latent = Coefficients(vector=np.arange(6.0) / 6.0, domain=CUBE)
    on_grid = readout(latent, GridSpec((4, 4, 4)))
    assert isinstance(on_grid, GridFunction)
    grid_points = Fractional_Grid_Coordinates((4, 4, 4))
    at_points = readout(latent, PointSpec(grid_points))
    assert isinstance(at_points, PointSet)
    grid_values = np.asarray(on_grid.values).reshape(-1)
    point_values = np.asarray(at_points.values).reshape(-1)
    assert np.allclose(grid_values, point_values, atol=1e-12)


def Test_The_Nonlinear_Decoder_Paths_Agree() -> None:
    """the direct forward and the inference call produce the same numbers"""
    readout = NonlinearDecoder(latent_width=4, hidden_widths=(8,), seed=10)
    latent = Coefficients(vector=np.linspace(-1.0, 1.0, 4), domain=CUBE)
    through_call = np.asarray(readout(latent, GridSpec((4, 4, 4))).values)
    points = Fractional_Grid_Coordinates((4, 4, 4))
    point_features = readout.Coordinate_Features(points)
    through_forward = np.asarray(
        readout.Forward(readout.parameter_values, np.asarray(latent.vector, dtype=np.float64), point_features)
    )
    assert np.allclose(through_call.reshape(-1), through_forward, atol=1e-12)


def Test_The_Nonlinear_Decoder_Cannot_Be_Written_As_A_Linear_Map_Of_Its_Latent() -> None:
    """the branch-trunk readout is linear in its latent by construction, and this decoder must not be"""
    points = np.asarray([[0.1, 0.2, 0.3], [0.6, 0.4, 0.9]])
    generator = np.random.default_rng(60)
    first_latent = generator.normal(size=5)
    second_latent = generator.normal(size=5)
    summed_latent = first_latent + second_latent
    zero_latent = np.zeros(5)

    def Departure_From_Linearity(readout: Any) -> float:
        """the worst gap between the readout at a plus b and the sum of its readouts at a and at b"""
        features = readout.Coordinate_Features(points)
        zero_output = np.asarray(readout.Forward(readout.parameter_values, zero_latent, features), dtype=np.float64)
        first_output = (
            np.asarray(readout.Forward(readout.parameter_values, first_latent, features), dtype=np.float64)
            - zero_output
        )
        second_output = (
            np.asarray(readout.Forward(readout.parameter_values, second_latent, features), dtype=np.float64)
            - zero_output
        )
        summed_output = (
            np.asarray(readout.Forward(readout.parameter_values, summed_latent, features), dtype=np.float64)
            - zero_output
        )
        return float(np.abs(summed_output - (first_output + second_output)).max())

    nonlinear = NonlinearDecoder(latent_width=5, hidden_widths=(16, 16), seed=61)
    linear = BasisExpansion(latent_width=5, trunk_widths=(16,), seed=61)
    # a network with a smooth unit between its layers has no reason to land back on additivity here
    assert Departure_From_Linearity(nonlinear) > 1e-3
    # the branch-trunk product is linear in the branch by construction, exactly to numerical noise
    assert Departure_From_Linearity(linear) < 1e-10


def Test_The_Nonlinear_Decoder_Splits_The_Latent_Across_Output_Channels() -> None:
    """one shared network, one latent row per channel, each channel matching a decoder run on its own"""
    labels = ("electron_localization_up", "electron_localization_down")
    together = NonlinearDecoder(latent_width=5, hidden_widths=(12,), output_channel_labels=labels, seed=12)
    alone = NonlinearDecoder(latent_width=5, hidden_widths=(12,), seed=12)
    generator = np.random.default_rng(13)
    latent = np.asarray(generator.normal(size=(2, 5)), dtype=np.float64)
    produced = together(Coefficients(vector=latent, domain=CUBE), GridSpec((4, 4, 4)))
    assert isinstance(produced, GridFunction)
    assert produced.channel_labels == labels
    values = np.asarray(produced.values, dtype=np.float64)
    assert values.shape == (2, 4, 4, 4)
    # the channels share a network but not a latent row, so they must not come out equal
    assert not np.allclose(values[0], values[1])
    for channel_index in range(2):
        one_channel = alone(Coefficients(vector=latent[channel_index], domain=CUBE), GridSpec((4, 4, 4)))
        assert isinstance(one_channel, GridFunction)
        assert np.allclose(values[channel_index], np.asarray(one_channel.values, dtype=np.float64)[0], atol=1e-10)


def Test_The_Nonlinear_Decoder_Refuses_A_Latent_That_Miscounts_Its_Channels() -> None:
    """a latent offering the wrong number of rows is a mistake, not a broadcast"""
    readout = NonlinearDecoder(latent_width=4, hidden_widths=(8,), output_channel_labels=("only_one",), seed=14)
    latent = np.zeros((3, 4), dtype=np.float64)
    with pytest.raises(ValueError):
        readout(Coefficients(vector=latent, domain=CUBE), GridSpec((4, 4, 4)))


def Test_The_Nonlinear_Decoder_Inspects_Its_Network_And_Last_Features() -> None:
    """the network's layers and the last query's point features are both reachable by name"""
    readout = NonlinearDecoder(latent_width=3, hidden_widths=(8,), seed=11)
    assert "decoder_layer_0_weights" in readout.Inspect()
    assert "last_point_features" not in readout.Inspect()
    latent = Coefficients(vector=np.ones(3), domain=CUBE)
    readout(latent, GridSpec((2, 2, 2)))
    inspected = readout.Inspect()
    feature_count = readout.coordinate_features.feature_count
    assert inspected["last_point_features"].shape == (2, 2, 2, feature_count)
    readout(latent, PointSpec(np.asarray([[0.1, 0.2, 0.3]])))
    assert readout.Inspect()["last_point_features"].shape == (1, feature_count)


def Nonlinear_Decoder_Loss(
    decoder: NonlinearDecoder, latent_vector: Any, point_features: Any, target: Any
) -> Callable[[dict[str, Any]], Any]:
    """the squared gap between the decoder's field values and a fixed target, as a forward an engine drives"""

    def Loss(lifted: dict[str, Any]) -> Any:
        difference = decoder.Forward(lifted, latent_vector, point_features) - target
        return (difference * difference).sum()

    return Loss


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_Gradients_Reach_Every_Nonlinear_Decoder_Array_Through_Forward() -> None:
    """the network the decoder owns is what training moves, so a severed tape would show as an untouched array"""
    decoder = NonlinearDecoder(latent_width=4, hidden_widths=(8,), seed=62)
    points = np.asarray([[0.1, 0.2, 0.3], [0.4, 0.6, 0.8], [0.9, 0.1, 0.2]])
    point_features = decoder.Coordinate_Features(points)
    generator = np.random.default_rng(63)
    latent_vector = np.asarray(generator.normal(size=4), dtype=np.float64)
    target = np.asarray(generator.normal(size=points.shape[0]), dtype=np.float64)
    parameters = ParameterSet(values={name: value.copy() for name, value in decoder.parameter_values.items()})
    engine = TorchEngine()
    gradients = Agreeing_Gradients(
        parameters,
        Nonlinear_Decoder_Loss(
            decoder,
            engine.Lift_Constant(latent_vector),
            engine.Lift_Constant(point_features),
            engine.Lift_Constant(target),
        ),
        Nonlinear_Decoder_Loss(decoder, latent_vector, point_features, target),
    )
    for name, gradient in gradients.items():
        assert float(np.abs(gradient).max()) > 1e-6, name
