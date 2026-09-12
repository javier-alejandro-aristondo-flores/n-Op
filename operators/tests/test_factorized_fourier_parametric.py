"""the parametric variant's own arms: every run assigned once, every interior level fully bracketed"""

from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.compositions import ExplicitStack
from operators.encoders import PointwiseLift
from operators.factorized_fourier.parametric import (
    All_Perovskite_Arms,
    All_Strain_Arms,
    Bracket_Corners,
    Interior_Levels,
    PEROVSKITE_ARM_NAMES,
    STRAIN_ARM_NAMES,
)
from operators.framework import Fractional_Grid_Coordinates, Layer
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
