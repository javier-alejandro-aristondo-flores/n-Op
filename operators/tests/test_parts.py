"""the shared encoders, readouts, compositions and wrappers"""

import numpy as np
import pytest

from operators.compositions import ExplicitStack
from operators.data import Gram_Pod, Project
from operators.encoders import BasisProjectionEncoder, PointwiseLift, SensorEncoder
from operators.framework import (
    Array,
    Coefficients,
    Domain,
    Fractional_Grid_Coordinates,
    GridFunction,
    GridSpec,
    Layer,
    PointSet,
    PointSpec,
    UniformGridQuadrature,
)
from operators.kernels import SpectralKernel
from operators.readouts import (
    BasisExpansion,
    FixedModeExpansion,
    PeriodicCoordinateFeatures,
    PointwiseProjection,
    RampedCoordinateFeatures,
)
from operators.substrate import NumpyEngine
from operators.wrappers import Conditioned, Conserving, Residual

CUBE = Domain(lattice=np.eye(3) * 2.0)

GRID_QUADRATURE = UniformGridQuadrature(cell_volume=8.0, point_count=64)


def Small_Field(channels: int, seed: int) -> GridFunction:
    """a random four-cubed field with the cube quadrature"""
    generator = np.random.default_rng(seed)
    labels = tuple(f"channel_{channel}" for channel in range(channels))
    return GridFunction(generator.random((channels, 4, 4, 4)), labels, CUBE, GRID_QUADRATURE)


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
    assert inspected["basis_modes"].shape == (4, 64)
    assert inspected["basis_singular_values"].shape == (4,)
    assert inspected["last_coefficients"].shape == (4,)


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
