"""every shared kernel against the dense reference integral"""

from collections.abc import Callable
from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.framework import (
    Array,
    Coefficients,
    CountingQuadrature,
    Dense_Reference_Integral,
    Domain,
    GridFunction,
    GridSpec,
    Layer,
    LiftedKernel,
    PointSet,
    PointSpec,
    UniformGridQuadrature,
)
from operators.kernels import (
    Cell_Heights,
    ContinuousDisplacementKernel,
    DenseKernel,
    Folded_Fractional_Gaps,
    Image_Reach,
    Lattice_Images,
    LowRankKernel,
    Periodic_Radius_Graph,
    Point_Spec_Over_Indices,
    Radial_Profile_Features,
    SpectralKernel,
    Stencil_From_Weights,
    TabulatedStencilKernel,
)
from operators.substrate import NumpyEngine, ParameterSet, Torch_Is_Available, TorchEngine

CUBE = Domain(lattice=np.eye(3) * 2.0)


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


def Test_The_Dense_Kernel_Matches_The_Oracle() -> None:
    """the dense index kernel equals the reference summation"""
    kernel = DenseKernel(output_count=3, input_count=4, seed=1)
    weights = kernel.parameter_values["weights"]
    coefficients = Coefficients(vector=np.asarray([0.5, -1.0, 2.0, 0.25]), domain=CUBE)

    def Pair_Kernel(targets: NDArray[np.float64], sources: NDArray[np.float64]) -> NDArray[np.float64]:
        target_indices = np.asarray(targets[:, 0], dtype=np.int64)
        source_indices = np.asarray(sources[:, 0], dtype=np.int64)
        return weights[np.ix_(target_indices, source_indices)]

    reference = Dense_Reference_Integral(Pair_Kernel, coefficients, Point_Spec_Over_Indices(3))
    produced = kernel.Integrate(coefficients, Point_Spec_Over_Indices(3))
    assert np.allclose(np.asarray(produced.vector), reference[:, 0], atol=1e-12)
    assert "weights" in kernel.Inspect()


def Fourier_Feature_Map(points: NDArray[np.float64]) -> NDArray[np.float64]:
    """a constant plus one wave per axis"""
    waves = np.cos(2.0 * np.pi * points)
    return np.concatenate([np.ones((points.shape[0], 1)), waves], axis=1)


def Test_The_Low_Rank_Kernel_Matches_The_Oracle_On_Points_And_Grids() -> None:
    """the feature-product kernel equals the reference, on grids and on points"""
    kernel = LowRankKernel(Fourier_Feature_Map, feature_count=4, seed=2)
    core = kernel.parameter_values["core"]

    def Pair_Kernel(targets: NDArray[np.float64], sources: NDArray[np.float64]) -> NDArray[np.float64]:
        return Fourier_Feature_Map(targets) @ core @ Fourier_Feature_Map(sources).T

    generator = np.random.default_rng(3)
    cloud = PointSet(
        positions=generator.random((7, 3)),
        domain=CUBE,
        values=generator.random((7, 1)),
        quadrature=CountingQuadrature(),
    )
    query = PointSpec(generator.random((5, 3)))
    reference = Dense_Reference_Integral(Pair_Kernel, cloud, query)
    produced = kernel.Integrate(cloud, query)
    assert np.allclose(np.asarray(produced.vector), reference.reshape(-1), atol=1e-12)

    field = GridFunction(
        values=generator.random((1, 4, 4, 4)),
        channel_labels=("charge_density",),
        domain=CUBE,
        quadrature=UniformGridQuadrature(cell_volume=8.0, point_count=64),
    )
    reference = Dense_Reference_Integral(Pair_Kernel, field, query)
    produced = kernel.Integrate(field, query)
    assert np.allclose(np.asarray(produced.vector), reference.reshape(-1), atol=1e-12)


def Test_The_Low_Rank_Kernel_Forward_And_Integrate_Agree() -> None:
    """the lifted forward, fed its own constants, produces the identical coefficients integrate returns"""
    kernel = LowRankKernel(Fourier_Feature_Map, feature_count=4, seed=36)
    generator = np.random.default_rng(37)
    cloud = PointSet(
        positions=generator.random((7, 3)),
        domain=CUBE,
        values=generator.random((7, 1)),
        quadrature=CountingQuadrature(),
    )
    query = PointSpec(generator.random((5, 3)))
    integrated = kernel.Integrate(cloud, query)
    constants = kernel.Lifted_Constants(NumpyEngine(), cloud, query)
    produced = np.asarray(kernel.Forward(kernel.parameter_values, *constants), dtype=np.float64)
    assert np.allclose(produced.reshape(-1), np.asarray(integrated.vector), atol=1e-12)


def Test_The_Low_Rank_Kernel_Forward_Matches_The_Dense_Oracle() -> None:
    """the lifted forward, called directly through its own constants, still lands on the dense reference"""
    kernel = LowRankKernel(Fourier_Feature_Map, feature_count=4, seed=34)
    core = kernel.parameter_values["core"]

    def Pair_Kernel(targets: NDArray[np.float64], sources: NDArray[np.float64]) -> NDArray[np.float64]:
        return Fourier_Feature_Map(targets) @ core @ Fourier_Feature_Map(sources).T

    generator = np.random.default_rng(35)
    cloud = PointSet(
        positions=generator.random((7, 3)),
        domain=CUBE,
        values=generator.random((7, 1)),
        quadrature=CountingQuadrature(),
    )
    query = PointSpec(generator.random((5, 3)))
    reference = Dense_Reference_Integral(Pair_Kernel, cloud, query)
    constants = kernel.Lifted_Constants(NumpyEngine(), cloud, query)
    produced = np.asarray(kernel.Forward(kernel.parameter_values, *constants), dtype=np.float64)
    assert np.allclose(produced.reshape(-1), reference.reshape(-1), atol=1e-12)


def Low_Rank_Loss(
    kernel: LowRankKernel, target_features: Any, source_features: Any, weighted_values: Any, target: Any
) -> Callable[[dict[str, Any]], Any]:
    """the summed squared gap between the low-rank kernel's lifted forward and a fixed target"""

    def Loss(lifted: dict[str, Any]) -> Any:
        difference = kernel.Forward(lifted, target_features, source_features, weighted_values) - target
        return (difference * difference).sum()

    return Loss


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_Gradients_Reach_The_Low_Rank_Kernel_Core() -> None:
    """a tape severed between the feature matrices and the core would leave it untrainable"""
    kernel = LowRankKernel(Fourier_Feature_Map, feature_count=4, seed=32)
    generator = np.random.default_rng(33)
    cloud = PointSet(
        positions=generator.random((7, 3)),
        domain=CUBE,
        values=generator.random((7, 1)),
        quadrature=CountingQuadrature(),
    )
    query = PointSpec(generator.random((5, 3)))
    target = generator.random((5, 1))
    parameters = ParameterSet(values={name: value.copy() for name, value in kernel.parameter_values.items()})
    engine = TorchEngine()
    engine_constants = kernel.Lifted_Constants(engine, cloud, query)
    numpy_constants = kernel.Lifted_Constants(NumpyEngine(), cloud, query)
    gradients = Agreeing_Gradients(
        parameters,
        Low_Rank_Loss(kernel, *engine_constants, engine.Lift_Constant(target)),
        Low_Rank_Loss(kernel, *numpy_constants, target),
    )
    assert float(np.abs(gradients["core"]).max()) > 1e-6


def Test_The_Spectral_Kernel_Matches_The_Dense_Oracle() -> None:
    """the fused spectral path equals the closed-form pair kernel summation"""
    kernel = SpectralKernel(kept_modes=(1, 1, 1), output_channels=2, input_channels=2, seed=4)
    kernel.Hermitian_Symmetrize()
    generator = np.random.default_rng(5)
    cell_volume = 2.0
    field = GridFunction(
        values=generator.random((2, 6, 6, 6)),
        channel_labels=("first_channel", "second_channel"),
        domain=CUBE,
        quadrature=UniformGridQuadrature(cell_volume=cell_volume, point_count=216),
    )
    reference = Dense_Reference_Integral(kernel.Dense_Kernel_Function(cell_volume), field, GridSpec((6, 6, 6)))
    produced = kernel.Integrate(field, GridSpec((6, 6, 6)))
    assert np.allclose(np.asarray(produced.values), reference, atol=1e-10)


def Test_The_Spectral_Kernel_Transfers_Discretization() -> None:
    """the same weights evaluate exactly on a finer output grid"""
    kernel = SpectralKernel(kept_modes=(1, 1, 1), output_channels=1, input_channels=1, seed=6)
    kernel.Hermitian_Symmetrize()
    generator = np.random.default_rng(7)
    cell_volume = 8.0
    field = GridFunction(
        values=generator.random((1, 6, 6, 6)),
        channel_labels=("charge_density",),
        domain=CUBE,
        quadrature=UniformGridQuadrature(cell_volume=cell_volume, point_count=216),
    )
    reference = Dense_Reference_Integral(kernel.Dense_Kernel_Function(cell_volume), field, GridSpec((8, 8, 8)))
    produced = kernel.Integrate(field, GridSpec((8, 8, 8)))
    assert np.asarray(produced.values).shape == (1, 8, 8, 8)
    assert np.allclose(np.asarray(produced.values), reference, atol=1e-10)
    inspected = kernel.Inspect()
    assert inspected["mode_magnitudes"].shape == (3, 3, 3, 1, 1)


def Test_The_Spectral_Kernel_Publishes_Its_Phase() -> None:
    """the two stored real arrays are one complex weight, and phase is half of what it means"""
    kernel = SpectralKernel(kept_modes=(1, 1, 1), output_channels=2, input_channels=2, seed=3)
    inspected = kernel.Inspect()
    real_part = np.asarray(inspected["mode_weights_real"], dtype=np.float64)
    imaginary_part = np.asarray(inspected["mode_weights_imaginary"], dtype=np.float64)
    magnitudes = np.asarray(inspected["mode_magnitudes"], dtype=np.float64)
    phases = np.asarray(inspected["mode_phases"], dtype=np.float64)
    assert phases.shape == real_part.shape
    # magnitude and phase must reconstruct the pair they were derived from
    assert np.allclose(magnitudes * np.cos(phases), real_part)
    assert np.allclose(magnitudes * np.sin(phases), imaginary_part)


SHEARED = Domain(lattice=np.asarray([[4.0, 0.0, 0.0], [1.6, 3.4, 0.0], [0.9, -1.2, 4.1]]))

SHEARED_VOLUME = float(abs(np.linalg.det(np.asarray(SHEARED.lattice))))

SHEARED_SLAB = Domain(lattice=np.asarray([[6.0, 0.0, 0.0], [0.0, 6.0, 0.0], [5.5, 0.0, 1.2]]))


def Test_The_Continuous_Kernel_Matches_The_Dense_Oracle() -> None:
    """the fused radius graph equals the closed-form pair kernel summed over a sheared slab"""
    kernel = ContinuousDisplacementKernel(
        cutoff_radius=2.5, basis_count=4, output_channels=3, input_channels=2, seed=8
    )
    lattice = np.asarray(SHEARED_SLAB.lattice, dtype=np.float64)
    # the cutoff crosses three cells along the short height, so the images are what is being checked
    assert Image_Reach(lattice, 2.5) == (2, 1, 3)
    generator = np.random.default_rng(9)
    cloud = PointSet(
        positions=generator.random((7, 3)),
        domain=SHEARED_SLAB,
        values=generator.random((7, 2)),
        quadrature=CountingQuadrature(),
    )
    query = PointSpec(generator.random((5, 3)))
    reference = Dense_Reference_Integral(kernel.Dense_Kernel_Function(lattice), cloud, query)
    produced = kernel.Integrate(cloud, query)
    assert isinstance(produced, PointSet)
    assert np.asarray(produced.values).shape == (5, 3)
    assert np.allclose(np.asarray(produced.values), reference, atol=1e-12)
    assert "last_edge_distances" in kernel.Inspect()


def Test_The_Continuous_Kernel_Transfers_Discretization() -> None:
    """the same weights read one field onto a coarse grid, a finer grid and loose probe points"""
    kernel = ContinuousDisplacementKernel(
        cutoff_radius=1.4, basis_count=3, output_channels=2, input_channels=1, seed=10
    )
    lattice = np.asarray(SHEARED.lattice, dtype=np.float64)
    generator = np.random.default_rng(11)
    field = GridFunction(
        values=generator.random((1, 6, 6, 6)),
        channel_labels=("charge_density",),
        domain=SHEARED,
        quadrature=UniformGridQuadrature(cell_volume=SHEARED_VOLUME, point_count=216),
    )
    pair_kernel = kernel.Dense_Kernel_Function(lattice)
    for requested in (GridSpec((6, 6, 6)), GridSpec((8, 8, 8))):
        reference = Dense_Reference_Integral(pair_kernel, field, requested)
        produced = kernel.Integrate(field, requested)
        assert isinstance(produced, GridFunction)
        assert np.asarray(produced.values).shape == (2, *requested.shape)
        assert np.allclose(np.asarray(produced.values), reference, atol=1e-12)
    probes = PointSpec(generator.random((9, 3)))
    reference = Dense_Reference_Integral(pair_kernel, field, probes)
    queried = kernel.Integrate(field, probes)
    assert isinstance(queried, PointSet)
    assert np.allclose(np.asarray(queried.values), reference, atol=1e-12)


def Test_Probe_Points_Receive_And_Never_Send() -> None:
    """a zero role keeps a point out of every message it would otherwise have sent"""
    kernel = ContinuousDisplacementKernel(
        cutoff_radius=2.0, basis_count=3, output_channels=2, input_channels=2, seed=12
    )
    lattice = np.asarray(SHEARED.lattice, dtype=np.float64)
    generator = np.random.default_rng(13)
    positions = generator.random((6, 3))
    values = generator.random((6, 2))
    roles = np.asarray([1, 1, 1, 1, 0, 0])
    with_probes = PointSet(
        positions=positions,
        domain=SHEARED,
        values=values,
        roles=roles,
        quadrature=CountingQuadrature(),
    )
    query = PointSpec(positions)
    reference = Dense_Reference_Integral(
        kernel.Dense_Kernel_Function(lattice, np.asarray(roles != 0, dtype=np.bool_)),
        with_probes,
        query,
    )
    produced = kernel.Integrate(with_probes, query)
    assert isinstance(produced, PointSet)
    assert np.allclose(np.asarray(produced.values), reference, atol=1e-12)
    everyone_sends = PointSet(
        positions=positions, domain=SHEARED, values=values, quadrature=CountingQuadrature()
    )
    undirected = kernel.Integrate(everyone_sends, query)
    assert isinstance(undirected, PointSet)
    # the control: if the roles were ignored the two probes would have changed every answer
    assert not np.allclose(np.asarray(produced.values), np.asarray(undirected.values))


def Test_Image_Enumeration_Follows_Cell_Heights() -> None:
    """in a sheared cell the images a cutoff reaches come from the height, not the vector length"""
    lattice = np.asarray(SHEARED_SLAB.lattice, dtype=np.float64)
    cutoff_radius = 2.5
    vector_lengths = np.sqrt((lattice**2).sum(axis=-1))
    by_length = (
        int(np.ceil(cutoff_radius / float(vector_lengths[0]))),
        int(np.ceil(cutoff_radius / float(vector_lengths[1]))),
        int(np.ceil(cutoff_radius / float(vector_lengths[2]))),
    )
    by_height = Image_Reach(lattice, cutoff_radius)
    assert float(Cell_Heights(lattice)[2]) < float(vector_lengths[2])
    assert by_height[2] > by_length[2]
    kernel = ContinuousDisplacementKernel(
        cutoff_radius=cutoff_radius, basis_count=2, output_channels=1, input_channels=1, seed=14
    )
    generator = np.random.default_rng(15)
    targets = generator.random((3, 3))
    cloud = PointSet(
        positions=generator.random((4, 3)),
        domain=SHEARED_SLAB,
        values=generator.random((4, 1)),
        quadrature=CountingQuadrature(),
    )
    query = PointSpec(targets)

    def Shortened_Pair_Kernel(
        query_points: NDArray[np.float64], cloud_points: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        """the same profile with images enumerated from the lattice-vector lengths instead"""
        folded = Folded_Fractional_Gaps(query_points, cloud_points)
        values = np.zeros((query_points.shape[0], cloud_points.shape[0], 1, 1))
        for image in Lattice_Images(by_length):
            length = np.sqrt((((folded + image) @ lattice) ** 2).sum(axis=-1))
            inside = length <= cutoff_radius
            features = Radial_Profile_Features(length[inside], cutoff_radius, 2)
            values[inside] += np.einsum("eb,boc->eoc", features, kernel.parameter_values["radial_weights"])
        return values

    complete = Periodic_Radius_Graph(targets, np.asarray(cloud.positions), lattice, cutoff_radius)
    shortened_edges = 0
    for image in Lattice_Images(by_length):
        folded = Folded_Fractional_Gaps(targets, np.asarray(cloud.positions))
        length = np.sqrt((((folded + image) @ lattice) ** 2).sum(axis=-1))
        shortened_edges += int(np.count_nonzero(length <= cutoff_radius))
    # the control: the shorter reach really does drop edges that lie inside the cutoff
    assert complete.distances.shape[0] > shortened_edges
    produced = kernel.Integrate(cloud, query)
    assert isinstance(produced, PointSet)
    assert not np.allclose(
        np.asarray(produced.values), Dense_Reference_Integral(Shortened_Pair_Kernel, cloud, query)
    )


def Test_The_Tabulated_Stencil_Matches_The_Dense_Oracle() -> None:
    """the periodic shift and accumulate equals the reference summation over the same offsets"""
    kernel = TabulatedStencilKernel(
        half_widths=(1, 1, 1), output_channels=2, input_channels=2, seed=16
    )
    generator = np.random.default_rng(17)
    field = GridFunction(
        values=generator.random((2, 6, 6, 6)),
        channel_labels=("first_channel", "second_channel"),
        domain=SHEARED,
        quadrature=UniformGridQuadrature(cell_volume=SHEARED_VOLUME, point_count=216),
    )
    pair_kernel = kernel.Dense_Kernel_Function((6, 6, 6), SHEARED_VOLUME / 216.0)
    reference = Dense_Reference_Integral(pair_kernel, field, GridSpec((6, 6, 6)))
    produced = kernel.Integrate(field, GridSpec((6, 6, 6)))
    assert np.asarray(produced.values).shape == (2, 6, 6, 6)
    assert np.allclose(np.asarray(produced.values), reference, atol=1e-12)


def Test_The_Tabulated_Stencil_Carries_The_Continuous_Profile() -> None:
    """one continuous profile, tabulated at each grid's own offsets, reproduces its integral there"""
    kernel = ContinuousDisplacementKernel(
        cutoff_radius=1.0, basis_count=3, output_channels=2, input_channels=2, seed=18
    )
    generator = np.random.default_rng(19)
    tabulated_shapes: list[tuple[int, ...]] = []
    coarse_field: GridFunction | None = None
    coarse_stencil: TabulatedStencilKernel | None = None
    for shape in ((6, 6, 6), (8, 8, 8)):
        quadrature = UniformGridQuadrature(
            cell_volume=SHEARED_VOLUME, point_count=int(np.prod(shape))
        )
        field = GridFunction(
            values=generator.random((2, *shape)),
            channel_labels=("first_channel", "second_channel"),
            domain=SHEARED,
            quadrature=quadrature,
        )
        stencil = kernel.Tabulate_On_Grid(SHEARED, GridSpec(shape), quadrature)
        tabulated_shapes.append(tuple(int(extent) for extent in stencil.Inspect()["stencil_weights"].shape))
        continuous = kernel.Integrate(field, GridSpec(shape))
        assert isinstance(continuous, GridFunction)
        tabulated = stencil.Integrate(field, GridSpec(shape))
        assert np.allclose(np.asarray(tabulated.values), np.asarray(continuous.values), atol=1e-12)
        reference = Dense_Reference_Integral(
            kernel.Dense_Kernel_Function(np.asarray(SHEARED.lattice, dtype=np.float64)),
            field,
            GridSpec(shape),
        )
        assert np.allclose(np.asarray(tabulated.values), reference, atol=1e-12)
        if coarse_field is None:
            coarse_field, coarse_stencil = field, stencil
    # the physical support carried across, the table did not: a finer grid needs a wider box
    assert tabulated_shapes[0] != tabulated_shapes[1]
    assert coarse_field is not None and coarse_stencil is not None
    with pytest.raises(ValueError):
        coarse_stencil.Integrate(coarse_field, GridSpec((8, 8, 8)))


def Test_The_Compact_Support_Kernels_Publish_Their_Fields() -> None:
    """the stencil is inspected as a field over its offsets, the profile as a curve over the radius"""
    stencil = TabulatedStencilKernel(
        half_widths=(1, 2, 1), output_channels=3, input_channels=2, seed=20
    )
    inspected = stencil.Inspect()
    assert inspected["stencil_weights"].shape == (3, 5, 3, 3, 2)
    assert inspected["stencil_magnitudes"].shape == (3, 5, 3)
    assert inspected["stencil_offsets"].shape == (3, 5, 3, 3)
    kernel = ContinuousDisplacementKernel(
        cutoff_radius=2.0, basis_count=5, output_channels=2, input_channels=3, seed=21
    )
    inspected = kernel.Inspect()
    assert inspected["radial_weights"].shape == (5, 2, 3)
    assert inspected["basis_over_radius"].shape == (64, 5)
    assert inspected["profile_over_radius"].shape == (64, 2, 3)
    # compact support asks the profile to be flat into the cutoff, not merely zero at it
    profile = np.abs(np.asarray(inspected["profile_over_radius"]))
    assert float(profile[-4:].max()) < 1e-3 * float(profile.max())


def Test_The_Tabulated_Stencil_Refuses_What_It_Cannot_Represent() -> None:
    """the three shapes a whole-voxel table cannot carry are refused rather than approximated"""
    quadrature = UniformGridQuadrature(cell_volume=SHEARED_VOLUME, point_count=216)
    reaching = ContinuousDisplacementKernel(
        cutoff_radius=3.0, basis_count=2, output_channels=1, input_channels=1, seed=22
    )
    # a cutoff past half the cell would put two offsets of one box on the same voxel
    with pytest.raises(ValueError):
        reaching.Tabulate_On_Grid(SHEARED, GridSpec((6, 6, 6)), quadrature)
    stencil = TabulatedStencilKernel(half_widths=(1, 1, 1), output_channels=1, input_channels=1, seed=23)
    field = GridFunction(
        values=np.zeros((1, 6, 6, 6)),
        channel_labels=("charge_density",),
        domain=SHEARED,
        quadrature=quadrature,
    )
    with pytest.raises(TypeError):
        stencil.Integrate(field, PointSpec(np.zeros((2, 3))))
    with pytest.raises(ValueError):
        Stencil_From_Weights(np.zeros((3, 4, 3, 1, 1)))


class ZeroLocalLinear:
    """a local linear map that always returns zero, so a layer can be built around a kernel under test"""


    def __init__(self) -> None:
        self.parameter_values: dict[str, NDArray[np.float64]] = {}


    def Forward(self, lifted: dict[str, Any], input_values: Any) -> Any:
        return input_values * 0.0


    def Inspect(self) -> dict[str, Array]:
        return {}


def Test_The_Tabulated_Stencil_Satisfies_The_Lifted_Kernel_Protocol() -> None:
    """pyright strict is the judge of structural conformance, this exercises the assignment and layer it checks"""
    kernel = TabulatedStencilKernel(half_widths=(1, 1, 1), output_channels=2, input_channels=2, seed=25)
    lifted_kernel: LiftedKernel[GridFunction, GridFunction] = kernel
    layer = Layer(kernel=lifted_kernel, local_linear=ZeroLocalLinear())
    assert layer.kernel is kernel


def Test_The_Tabulated_Stencil_Forward_Refuses_A_Foreign_Shape() -> None:
    """a shape the table was not built for is refused by the lifted forward directly, not merely by integrate"""
    kernel = TabulatedStencilKernel(half_widths=(1, 1, 1), output_channels=1, input_channels=1, seed=26)
    values = np.random.default_rng(27).random((1, 6, 6, 6))
    with pytest.raises(ValueError):
        kernel.Forward(kernel.parameter_values, values, (8, 8, 8))


def Test_The_Tabulated_Stencil_Forward_And_Integrate_Agree() -> None:
    """the lifted forward and the numpy wrapper around it produce the identical field"""
    kernel = TabulatedStencilKernel(half_widths=(1, 1, 1), output_channels=2, input_channels=2, seed=38)
    generator = np.random.default_rng(39)
    field = GridFunction(
        values=generator.random((2, 6, 6, 6)),
        channel_labels=("first_channel", "second_channel"),
        domain=SHEARED,
        quadrature=UniformGridQuadrature(cell_volume=SHEARED_VOLUME, point_count=216),
    )
    integrated = kernel.Integrate(field, GridSpec((6, 6, 6)))
    values = np.asarray(field.values, dtype=np.float64)
    produced = np.asarray(kernel.Forward(kernel.parameter_values, values, (6, 6, 6)), dtype=np.float64)
    assert np.allclose(produced, np.asarray(integrated.values), atol=1e-12)


def Test_The_Tabulated_Stencil_Forward_Matches_The_Dense_Oracle() -> None:
    """the numpy lifted forward, called directly rather than through integrate, still lands on the oracle"""
    kernel = TabulatedStencilKernel(half_widths=(1, 1, 1), output_channels=2, input_channels=2, seed=28)
    generator = np.random.default_rng(29)
    field = GridFunction(
        values=generator.random((2, 6, 6, 6)),
        channel_labels=("first_channel", "second_channel"),
        domain=SHEARED,
        quadrature=UniformGridQuadrature(cell_volume=SHEARED_VOLUME, point_count=216),
    )
    pair_kernel = kernel.Dense_Kernel_Function((6, 6, 6), SHEARED_VOLUME / 216.0)
    reference = Dense_Reference_Integral(pair_kernel, field, GridSpec((6, 6, 6)))
    values = np.asarray(field.values, dtype=np.float64)
    produced = kernel.Forward(kernel.parameter_values, values, (6, 6, 6))
    assert np.allclose(np.asarray(produced, dtype=np.float64), reference, atol=1e-12)


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_The_Tabulated_Stencil_Forward_Matches_The_Dense_Oracle_On_The_Foreign_Engine() -> None:
    """the convolution facet dispatches correctly, landing on the oracle on the foreign engine too"""
    kernel = TabulatedStencilKernel(half_widths=(1, 1, 1), output_channels=2, input_channels=2, seed=28)
    generator = np.random.default_rng(29)
    field = GridFunction(
        values=generator.random((2, 6, 6, 6)),
        channel_labels=("first_channel", "second_channel"),
        domain=SHEARED,
        quadrature=UniformGridQuadrature(cell_volume=SHEARED_VOLUME, point_count=216),
    )
    pair_kernel = kernel.Dense_Kernel_Function((6, 6, 6), SHEARED_VOLUME / 216.0)
    reference = Dense_Reference_Integral(pair_kernel, field, GridSpec((6, 6, 6)))
    engine = TorchEngine()
    lifted = engine.Lift(kernel.parameter_values, requires_gradient=False)
    lifted_values = engine.Lift_Constant(np.asarray(field.values, dtype=np.float64))
    produced = kernel.Forward(lifted, lifted_values, (6, 6, 6))
    assert np.allclose(np.asarray(produced, dtype=np.float64), reference, atol=1e-10)


def Saved_Tensor_Count_Of_The_Tabulated_Stencil_Forward(half_widths: tuple[int, int, int]) -> int:
    """how many tensors the foreign engine saves for backward during one lifted forward at this stencil size"""
    import torch

    kernel = TabulatedStencilKernel(half_widths=half_widths, output_channels=4, input_channels=4, seed=44)
    generator = np.random.default_rng(45)
    field_values = generator.random((4, 8, 8, 8))
    engine = TorchEngine()
    lifted = engine.Lift(kernel.parameter_values, requires_gradient=True)
    lifted_values = engine.Lift_Constant(field_values)
    saved_tensor_count = 0

    def Count_Pack(saved_tensor: Any) -> Any:
        nonlocal saved_tensor_count
        saved_tensor_count += 1
        return saved_tensor

    def Unpack(saved_tensor: Any) -> Any:
        return saved_tensor

    with torch.autograd.graph.saved_tensors_hooks(Count_Pack, Unpack):
        produced = kernel.Forward(lifted, lifted_values, (8, 8, 8))
        produced.sum().backward()
    return saved_tensor_count


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_The_Tabulated_Stencil_Forward_Holds_No_Per_Offset_Intermediates() -> None:
    """the saved-tensor count of one lifted forward does not grow with the offset count behind it"""
    # a per-offset roll would have saved one shifted copy of the field for each of 27, then 125 offsets
    # the convolution facet instead saves the padded field and the assembled kernel once, whatever the offset count
    # so a hook counting every tensor the autograd graph actually saves is a size measure, not a proportional one
    twenty_seven_offsets = Saved_Tensor_Count_Of_The_Tabulated_Stencil_Forward((1, 1, 1))
    one_hundred_twenty_five_offsets = Saved_Tensor_Count_Of_The_Tabulated_Stencil_Forward((2, 2, 2))
    assert twenty_seven_offsets >= 1
    assert one_hundred_twenty_five_offsets < 2 * twenty_seven_offsets


def Tabulated_Stencil_Loss(
    kernel: TabulatedStencilKernel, field_values: Any, output_shape: tuple[int, int, int], target: Any
) -> Callable[[dict[str, Any]], Any]:
    """the summed squared gap between the stencil's lifted forward and a fixed target"""

    def Loss(lifted: dict[str, Any]) -> Any:
        difference = kernel.Forward(lifted, field_values, output_shape) - target
        return (difference * difference).sum()

    return Loss


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_Gradients_Reach_The_Tabulated_Stencil_Weights() -> None:
    """a tape severed at the roll or the channel contraction would leave the stencil weights untrainable"""
    kernel = TabulatedStencilKernel(half_widths=(1, 1, 1), output_channels=2, input_channels=2, seed=30)
    generator = np.random.default_rng(31)
    field_values = generator.random((2, 6, 6, 6))
    target = generator.random((2, 6, 6, 6))
    parameters = ParameterSet(values={name: value.copy() for name, value in kernel.parameter_values.items()})
    engine = TorchEngine()
    gradients = Agreeing_Gradients(
        parameters,
        Tabulated_Stencil_Loss(kernel, engine.Lift_Constant(field_values), (6, 6, 6), engine.Lift_Constant(target)),
        Tabulated_Stencil_Loss(kernel, field_values, (6, 6, 6), target),
    )
    assert float(np.abs(gradients["stencil_weights"]).max()) > 1e-6


def Test_The_Periodic_Geometry_Says_What_It_Carries() -> None:
    """gaps fold into the half cell and every edge's distance is the length of its displacement"""
    ahead = np.asarray([[0.02, 0.5, 0.99]])
    behind = np.asarray([[0.98, 0.5, 0.01]])
    folded = Folded_Fractional_Gaps(ahead, behind)
    assert np.all(np.abs(folded) <= 0.5 + 1e-12)
    assert np.allclose(folded[0, 0], [0.04, 0.0, -0.02])
    lattice = np.asarray(SHEARED_SLAB.lattice, dtype=np.float64)
    generator = np.random.default_rng(24)
    graph = Periodic_Radius_Graph(generator.random((4, 3)), generator.random((5, 3)), lattice, 2.5)
    assert graph.distances.shape[0] == graph.displacements.shape[0]
    assert np.allclose(graph.distances, np.sqrt((graph.displacements**2).sum(axis=-1)), atol=1e-12)
    assert bool(np.all(graph.distances <= 2.5))
