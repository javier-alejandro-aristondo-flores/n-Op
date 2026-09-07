"""the shared encoders, readouts, compositions and wrappers"""

import numpy as np

from operators.compositions import ExplicitStack
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
from operators.data import Gram_Pod, Project
from operators.readouts import BasisExpansion, FixedModeExpansion, PointwiseProjection
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
    readout = BasisExpansion(latent_width=6, trunk_widths=(16,), fourier_orders=2, seed=4)
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
    snapshots = generator.normal(size=(10, 64)) @ generator.normal(size=(64, 64))
    truncated = Gram_Pod(snapshots, rank=3)
    readout = FixedModeExpansion(truncated, (4, 4, 4))
    coefficients = Project(truncated, snapshots[0][None, :])[0]
    rebuilt = readout(Coefficients(vector=coefficients, domain=CUBE), GridSpec((4, 4, 4)))
    residual = np.asarray(rebuilt.values).reshape(-1) - snapshots[0]
    assert coefficients.shape == (3,)
    assert 0.0 < float(np.linalg.norm(residual)) < float(np.linalg.norm(snapshots[0] - truncated.mean))


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
