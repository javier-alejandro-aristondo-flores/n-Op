"""the parametric variant's own arms: every run assigned once, every interior level fully bracketed"""

from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.compositions import ExplicitStack
from operators.encoders import PointwiseLift
from operators.factorized_fourier import Factorized_Fourier_Network, FactorizedFourier
from operators.factorized_fourier.parametric import (
    All_Perovskite_Arms,
    All_Strain_Arms,
    Bracket_Corners,
    Interior_Levels,
    PEROVSKITE_ARM_NAMES,
    STRAIN_ARM_NAMES,
)
from operators.factorized_fourier.report import (
    Card_Metric_Errors,
    Multilinear_Interpolated_Field,
    Strain_Bracketing_Floor_Rows,
    Strain_Ridge_Nearest_Mean_Floor_Rows,
)
from operators.framework import Coefficients, Domain, Fractional_Grid_Coordinates, GridSpec, Layer
from operators.kernels import SpectralKernel
from operators.readouts import PeriodicCoordinateFeatures, PointwiseProjection

PARAMETER_VALUES = np.array([0.3, -0.2, 0.7])


def Test_Bracket_Corners_Reads_A_Synthetic_One_Dimensional_Line() -> None:
    """a plain 1-D sweep brackets its interior points between immediate neighbors, and refuses the endpoints"""
    levels = [(0.0,), (1.0,), (2.0,), (3.0,)]
    assert Bracket_Corners((1.0,), levels) == ((0.0,), (2.0,))
    assert Bracket_Corners((0.0,), levels) is None
    assert Bracket_Corners((3.0,), levels) is None


def Test_Bracket_Corners_Reads_A_Synthetic_Two_Dimensional_Grid() -> None:
    """a plain 2-D grid brackets an interior point with all four corners, and a grid hole removes the bracket"""
    full_grid = [(first, second) for first in (0.0, 1.0, 2.0) for second in (0.0, 1.0, 2.0)]
    corners = Bracket_Corners((1.0, 1.0), full_grid)
    assert corners is not None
    assert set(corners) == {(0.0, 0.0), (0.0, 2.0), (2.0, 0.0), (2.0, 2.0)}
    with_a_hole = [level for level in full_grid if level != (0.0, 0.0)]
    assert Bracket_Corners((1.0, 1.0), with_a_hole) is None
    # an edge point (not interior on the x axis) never brackets, hole or not
    assert Bracket_Corners((0.0, 1.0), full_grid) is None


@pytest.mark.pool
def Test_Every_Strain_Atlas_Run_Lands_On_Exactly_One_Arm_And_Level() -> None:
    """every non-reference, non-auxiliary strain run is assigned to one family, at one level, with no run twice"""
    arms = All_Strain_Arms()
    assert {arm.name for arm in arms} == set(STRAIN_ARM_NAMES)
    seen: set[str] = set()
    for arm in arms:
        for level, run_paths in arm.runs_by_level.items():
            assert len(level) >= 1
            for run_path in run_paths:
                assert run_path not in seen, f"{run_path} assigned twice"
                seen.add(run_path)
    # 2680 total assignments, less the 2 reference runs and the later-sweep auxiliary runs
    assert 2300 <= len(seen) <= 2400


@pytest.mark.pool
def Test_Every_Strain_Arms_Interior_Levels_Have_A_Real_Bracket_In_The_Same_Arm() -> None:
    """every level this arm calls interior names corner levels that are themselves real levels of that arm"""
    arms = All_Strain_Arms()
    total_interior = 0
    for arm in arms:
        interior = Interior_Levels(arm)
        dimension = len(next(iter(arm.runs_by_level)))
        for level, corners in interior.items():
            assert len(corners) == 2**dimension
            for corner in corners:
                assert corner in arm.runs_by_level, f"{arm.name} bracket names a corner absent from its own levels"
                assert corner != level
        total_interior += len(interior)
    # measured directly off the real pool: 423 interior levels across the seven families combined
    assert 380 <= total_interior <= 460


@pytest.mark.pool
def Test_Every_Perovskite_Run_Lands_On_Exactly_One_Arm_And_Level() -> None:
    """every perovskite run is assigned to the length or angle arm, at one three-factor level, with no run twice"""
    arms = All_Perovskite_Arms()
    assert {arm.name for arm in arms} == set(PEROVSKITE_ARM_NAMES)
    seen: set[str] = set()
    for arm in arms:
        for level, run_paths in arm.runs_by_level.items():
            assert len(level) == 3
            for run_path in run_paths:
                assert run_path not in seen, f"{run_path} assigned twice"
                seen.add(run_path)
    assert 240 <= len(seen) <= 250


@pytest.mark.pool
def Test_Every_Perovskite_Arms_Interior_Levels_Have_A_Real_Bracket_In_The_Same_Arm() -> None:
    """the 0.8 and 1.2 factor endpoints never bracket, and every level this arm calls interior really does"""
    arms = All_Perovskite_Arms()
    total_interior = 0
    for arm in arms:
        interior = Interior_Levels(arm)
        for level, corners in interior.items():
            assert len(corners) == 8
            for corner in corners:
                assert corner in arm.runs_by_level
            # an interior level never itself carries the 0.8 or 1.2 extreme on any of its three factors
            assert all(0.8 < component < 1.2 for component in level)
        total_interior += len(interior)
    # measured directly off the real pool: 18 (length) + 27 (angle) = 45
    assert 35 <= total_interior <= 55


def Toy_Parametric_Backbone(
    input_channels: int, hidden_channels: int = 6, seed: int = 1
) -> tuple[PointwiseLift, ExplicitStack, PointwiseProjection]:
    """a tiny lift-spectral-project stack sized to whatever channel count the caller's own input carries"""
    lift = PointwiseLift(hidden_channels, input_channels, seed=seed)
    layers = tuple(
        Layer(
            kernel=SpectralKernel(
                kept_modes=(2, 2, 2),
                output_channels=hidden_channels,
                input_channels=hidden_channels,
                seed=seed + 2 * layer_index + 1,
                mode_mixing="separable",
            ),
            local_linear=PointwiseLift(hidden_channels, hidden_channels, seed=seed + 2 * layer_index + 2),
            residual=True,
        )
        for layer_index in range(2)
    )
    composition = ExplicitStack(layers)
    projection = PointwiseProjection(1, hidden_channels, bounded=False, seed=seed + 10)
    return lift, composition, projection


def Run_Backbone(
    lift: PointwiseLift, composition: ExplicitStack, projection: PointwiseProjection, channels: NDArray[np.float64]
) -> Any:
    """the backbone's own output field for one input channel stack, at whatever grid shape it was given"""
    lifted = dict(lift.parameter_values)
    lifted.update(composition.Parameter_Values())
    lifted.update(projection.parameter_values)
    hidden = lift.Forward(lifted, channels)
    carried = composition.Forward(lifted, hidden)
    return projection.Forward(lifted, carried)


def Constant_Channels(shape: tuple[int, int, int]) -> NDArray[np.float64]:
    """three parameter values broadcast as constant channels over the grid, nothing else"""
    return np.broadcast_to(PARAMETER_VALUES[:, None, None, None], (3, *shape)).astype(np.float64).copy()


def Constant_Plus_Coordinate_Channels(shape: tuple[int, int, int]) -> NDArray[np.float64]:
    """the same three constants, beside periodic coordinate features of the grid's own fractional coordinates"""
    constant = Constant_Channels(shape)
    points = Fractional_Grid_Coordinates(shape)
    features = PeriodicCoordinateFeatures(fourier_orders=2, axis_count=3)(points)
    feature_channels = features.T.reshape(features.shape[1], *shape)
    return np.concatenate([constant, feature_channels], axis=0)


def Test_A_Constant_Only_Input_Can_Only_Answer_A_Constant_Field() -> None:
    """a spectral-plus-pointwise stack fed nothing but constant channels stays constant to round-off"""
    shape = (8, 8, 8)
    channels = Constant_Channels(shape)
    lift, composition, projection = Toy_Parametric_Backbone(channels.shape[0], seed=7)
    output = np.asarray(Run_Backbone(lift, composition, projection, channels))
    assert output.shape == (1, *shape)
    assert float(np.ptp(output)) < 1e-9


def Test_Coordinate_Features_Break_The_Constant_Output_Degeneracy_And_Answer_Any_Grid() -> None:
    """coordinate features make the output vary over the grid, and the same weights answer 8cubed and 12cubed alike"""
    shape = (8, 8, 8)
    channels = Constant_Plus_Coordinate_Channels(shape)
    lift, composition, projection = Toy_Parametric_Backbone(channels.shape[0], seed=7)
    output = np.asarray(Run_Backbone(lift, composition, projection, channels))
    assert output.shape == (1, *shape)
    assert float(np.ptp(output)) > 1e-6

    other_shape = (12, 12, 12)
    other_channels = Constant_Plus_Coordinate_Channels(other_shape)
    other_output = np.asarray(Run_Backbone(lift, composition, projection, other_channels))
    assert other_output.shape == (1, *other_shape)
    assert float(np.ptp(other_output)) > 1e-6


def Test_Multilinear_Interpolated_Field_Matches_Hand_Computed_Weights() -> None:
    """one dimension linearly interpolates and two dimensions bilinearly interpolate, against known arithmetic"""
    one_dimensional = {(0.0,): np.zeros((2, 2)), (2.0,): np.full((2, 2), 4.0)}
    corners_1d = ((0.0,), (2.0,))
    assert np.allclose(Multilinear_Interpolated_Field((1.0,), corners_1d, one_dimensional), 2.0)
    assert np.allclose(Multilinear_Interpolated_Field((0.5,), corners_1d, one_dimensional), 1.0)

    two_dimensional = {
        (0.0, 0.0): np.full((1,), 0.0),
        (0.0, 2.0): np.full((1,), 10.0),
        (2.0, 0.0): np.full((1,), 20.0),
        (2.0, 2.0): np.full((1,), 30.0),
    }
    corners_2d = tuple(two_dimensional)
    assert np.allclose(Multilinear_Interpolated_Field((1.0, 1.0), corners_2d, two_dimensional), 15.0)
    assert np.allclose(Multilinear_Interpolated_Field((0.0, 0.0), corners_2d, two_dimensional), 0.0)
    assert np.allclose(Multilinear_Interpolated_Field((0.5, 0.0), corners_2d, two_dimensional), 5.0)


@pytest.mark.pool
def Test_The_Bracketing_Floor_Scores_Every_Interior_Level_Against_Its_Own_Corners() -> None:
    """the decisive floor's multilinear interpolation reads as a strong, physically sane floor on real strain data"""
    arms = All_Strain_Arms()
    rows = Strain_Bracketing_Floor_Rows(arms)
    assert len(rows) == sum(len(Interior_Levels(arm)) for arm in arms)
    assert {row.family for row in rows} == set(STRAIN_ARM_NAMES)
    for row in rows:
        assert set(row.errors) == set(Card_Metric_Errors(np.zeros((2, 2, 2)), np.ones((2, 2, 2))))
        # a smooth strain sweep interpolates far better than one percent relative error, on every family
        assert 0.0 <= row.errors["relative_l2"] < 0.01
        assert row.errors["structural_similarity_3d"] > 0.999


def Toy_Parametric_Member(seed: int = 9) -> FactorizedFourier:
    """a small parametric-task member, built through the same factory the real one will use"""
    return Factorized_Fourier_Network(
        hidden_channels=4,
        kept_modes=(1, 1, 1),
        layer_count=2,
        reference_density=1.0,
        gram_mean=np.zeros(6),
        gram_scale=np.ones(6),
        processing_shape=(6, 6, 6),
        seed=seed,
        task="parametric",
    )


def Toy_Parameters(seed: int = 3) -> Coefficients:
    """a six-component parameter vector over a mildly sheared toy cell"""
    generator = np.random.default_rng(seed)
    lattice = np.eye(3) * 3.57 + generator.normal(0.0, 0.05, size=(3, 3))
    vector = generator.normal(0.0, 0.02, size=6)
    return Coefficients(vector=vector, domain=Domain(lattice=lattice))


def Test_The_Parametric_Member_Answers_At_The_Requested_Electron_Count() -> None:
    """the field Predict_Field answers integrates, under the grid's own quadrature, to the electron count given"""
    member = Toy_Parametric_Member()
    parameters = Toy_Parameters()
    output = member.Predict_Field(parameters, GridSpec((6, 6, 6)), electron_count=8.0)
    values = np.asarray(output.values, dtype=np.float64)
    assert values.shape == (1, 6, 6, 6)
    integral = float(values.sum()) * output.quadrature.cell_volume / values[0].size
    assert abs(integral - 8.0) < 1e-6


def Test_The_Parametric_Member_Refuses_A_Missing_Electron_Count() -> None:
    """__call__ raises rather than silently skipping the conservation law when no condition is given"""
    member = Toy_Parametric_Member()
    parameters = Toy_Parameters()
    input_function = member.Predict_Field(parameters, GridSpec((6, 6, 6)), electron_count=8.0)
    with pytest.raises(ValueError):
        member(input_function, GridSpec((6, 6, 6)), condition=None)


def Test_The_Same_Parametric_Weights_Answer_Two_Different_Grids() -> None:
    """the same trained weights renormalize correctly at an 8-cubed and a 10-cubed grid alike, from one parameter vector"""
    member = Toy_Parametric_Member()
    parameters = Toy_Parameters(seed=11)
    small = member.Predict_Field(parameters, GridSpec((8, 8, 8)), electron_count=8.0)
    large = member.Predict_Field(parameters, GridSpec((10, 10, 10)), electron_count=8.0)
    for output in (small, large):
        values = np.asarray(output.values, dtype=np.float64)
        integral = float(values.sum()) * output.quadrature.cell_volume / values[0].size
        assert abs(integral - 8.0) < 1e-6
    assert small.values.shape == (1, 8, 8, 8)
    assert large.values.shape == (1, 10, 10, 10)


@pytest.mark.pool
def Test_The_Ridge_Nearest_And_Mean_Floors_Score_The_Same_Interior_Levels_In_The_Expected_Order() -> None:
    """training mean is weakest, nearest copy beats it, ridge to POD beats both, on the identical evaluation rows"""
    arms = All_Strain_Arms()
    floors = Strain_Ridge_Nearest_Mean_Floor_Rows(arms)
    interior_count = sum(len(Interior_Levels(arm)) for arm in arms)
    identifiers = None
    for name, rows in floors.items():
        assert len(rows) == interior_count, name
        these_identifiers = {row.identifier for row in rows}
        if identifiers is None:
            identifiers = these_identifiers
        else:
            assert these_identifiers == identifiers, name
    mean_median = np.median([row.errors["relative_l2"] for row in floors["training_mean_trivial_floor"]])
    copy_median = np.median([row.errors["relative_l2"] for row in floors["nearest_run_copy_floor"]])
    ridge_median = np.median([row.errors["relative_l2"] for row in floors["ridge_to_pod_32_floor"]])
    assert copy_median < mean_median
    assert ridge_median < copy_median
