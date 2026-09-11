"""the metrics on analytic cases, and the gap walk against the census labels"""

from typing import cast

import numpy as np
import pytest

from operators import metrics
from operators.data import Occupancy_Walk_Gap, POOL_ROOT, Read_Census, Read_Eigenvalues, Rebuild_Density_Of_States
from operators.metrics import (
    Bootstrap_Confidence_Interval,
    Curve_L1,
    Delta_Mean_Squared_Error,
    Delta_R_Squared,
    Fraction_Within,
    Frequency_Split_Relative_L2,
    Gap_Edge_Energies,
    Gap_Edge_Error,
    Masked_Mean_Squared_Error,
    Mean_Discrepancy,
    Mean_Removed_Mean_Absolute_Error,
    Mean_Removed_Mean_Squared_Error,
    Mean_Removed_Relative_L2,
    Mean_Squared_Error,
    Mean_Squared_Error_With_Moment_Normalized_Magnetization,
    Median_And_Interquartile,
    Relative_L2,
    Structural_Similarity_3d,
    Wasserstein_1d,
)
from operators.tasks import CARDS


def Test_Field_Errors_Have_Their_Analytic_Values() -> None:
    """the relative and mean-removed errors on closed-form cases"""
    truth = np.asarray([3.0, 4.0])
    assert Relative_L2(truth, truth) == 0.0
    assert abs(Relative_L2(2.0 * truth, truth) - 1.0) < 1e-12
    assert Mean_Removed_Relative_L2(truth + 5.0, truth) < 1e-12


def Test_The_Mean_Removed_Errors_Ignore_A_Constant_Offset() -> None:
    """a periodic cell has no absolute zero, so a shifted potential is the same potential"""
    truth = np.asarray([3.0, 4.0, 11.0])
    assert Mean_Squared_Error(truth, truth) == 0.0
    assert abs(Mean_Squared_Error(np.asarray([1.0, 3.0]), np.zeros(2)) - 5.0) < 1e-12
    assert Mean_Removed_Mean_Squared_Error(truth + 5.0, truth) < 1e-24
    assert Mean_Removed_Mean_Absolute_Error(truth - 2.5, truth) < 1e-12
    # the offset the mean removal threw away is exactly what this metric reports, with its sign
    assert abs(Mean_Discrepancy(truth + 5.0, truth) - 5.0) < 1e-12
    assert abs(Mean_Discrepancy(truth - 5.0, truth) + 5.0) < 1e-12


def Test_The_Masked_Loss_Scores_Only_The_Hidden_Entries() -> None:
    """a completion member is judged on what was taken away, never on what it was handed"""
    truth = np.zeros(4)
    prediction = np.asarray([100.0, 2.0, 100.0, 4.0])
    hidden = np.asarray([False, True, False, True], dtype=np.bool_)
    assert abs(Masked_Mean_Squared_Error(prediction, truth, hidden) - 10.0) < 1e-12
    with pytest.raises(ValueError):
        Masked_Mean_Squared_Error(prediction, truth, np.zeros_like(hidden))


def Test_The_Delta_Metrics_Sit_On_The_Identity_Floor() -> None:
    """submitting the cheap field unchanged explains nothing, and halving its error explains 75%"""
    generator = np.random.default_rng(21)
    truth = generator.normal(size=256)
    cheap_input = truth + generator.normal(size=256)
    assert abs(Delta_Mean_Squared_Error(cheap_input, truth, cheap_input) - 1.0) < 1e-12
    assert abs(Delta_R_Squared(cheap_input, truth, cheap_input)) < 1e-12
    assert abs(Delta_R_Squared(truth, truth, cheap_input) - 1.0) < 1e-12
    # the suite states the kill line twice: half the identity error, and 75% of the correction
    half_the_identity_error = truth + 0.5 * (cheap_input - truth)
    assert abs(Relative_L2(half_the_identity_error, truth) - 0.5 * Relative_L2(cheap_input, truth)) < 1e-12
    assert abs(Delta_R_Squared(half_the_identity_error, truth, cheap_input) - 0.75) < 1e-12
    with pytest.raises(ValueError):
        Delta_R_Squared(truth, truth, truth)


def Test_The_Moment_Normalized_Loss_Drops_The_Channel_A_Restricted_Run_Lacks() -> None:
    """the magnetization term is masked where there is none, and scaled by the moment where there is"""
    density = np.asarray([1.0, 2.0, 3.0])
    moved = density + 1.0
    magnetization = np.asarray([0.0, 0.5, -0.5])
    restricted = Mean_Squared_Error_With_Moment_Normalized_Magnetization(moved, density)
    assert abs(restricted - 1.0) < 1e-12
    polarized = Mean_Squared_Error_With_Moment_Normalized_Magnetization(
        moved, density, magnetization + 0.25, magnetization, absolute_moment=2.0
    )
    assert abs(polarized - (1.0 + 0.0625 / 4.0)) < 1e-12
    with pytest.raises(ValueError):
        Mean_Squared_Error_With_Moment_Normalized_Magnetization(moved, density, magnetization, magnetization)


def Test_The_Gap_Edges_Are_Read_Off_The_Curve_Support() -> None:
    """the smeared support ends a stated distance past each eigenvalue, and a scissor moves one edge"""
    energy_grid = np.linspace(-8.0, 8.0, 4001)
    smearing_width = 0.2
    weights = np.asarray([1.0])
    truth = Rebuild_Density_Of_States(np.asarray([[[-1.0, 2.0]]]), weights, smearing_width, energy_grid)
    valence_edge, conduction_edge = Gap_Edge_Energies(truth, energy_grid)
    # a gaussian falls to a hundredth of its peak exactly this far out
    tail = smearing_width * np.sqrt(2.0 * np.log(100.0))
    assert abs(valence_edge - (-1.0 + tail)) < 0.01
    assert abs(conduction_edge - (2.0 - tail)) < 0.01
    assert Gap_Edge_Error(truth, truth, energy_grid) == 0.0
    # the measured strain-atlas scissor, applied to the conduction manifold alone
    scissor = 1.2612
    warped = Rebuild_Density_Of_States(np.asarray([[[-1.0, 2.0 + scissor]]]), weights, smearing_width, energy_grid)
    assert abs(Gap_Edge_Error(warped, truth, energy_grid) - 0.5 * scissor) < 0.01
    with pytest.raises(ValueError):
        Gap_Edge_Energies(np.zeros_like(energy_grid), energy_grid)


def Test_The_Library_Holds_Every_Loss_And_Metric_The_Cards_Name() -> None:
    """a card naming a loss nobody wrote is a member that cannot be trained or reported"""
    unwritten = [
        f"{card.name}: {named}"
        for card in CARDS
        for named in (card.loss, *card.metrics)
        if not callable(getattr(metrics, "_".join(part.capitalize() for part in named.split("_")), None))
    ]
    assert unwritten == [], unwritten


def Test_The_Frequency_Split_Separates_Bands() -> None:
    """low-mode agreement survives high-mode contamination"""
    coordinates = np.arange(8) / 8.0
    x_coordinate, y_coordinate, _ = np.meshgrid(coordinates, coordinates, coordinates, indexing="ij")
    truth = np.cos(2.0 * np.pi * x_coordinate)
    contaminated = truth + 0.5 * np.cos(2.0 * np.pi * 3.0 * (x_coordinate + y_coordinate))
    low_error, high_error = Frequency_Split_Relative_L2(contaminated, truth, cutoff_modes=2.0)
    assert low_error < 1e-12
    assert high_error > 0.0


def Test_Structural_Similarity_Ranks_Agreement() -> None:
    """identical fields score one, unrelated noise scores far lower"""
    generator = np.random.default_rng(7)
    field = generator.random((12, 12, 12))
    assert abs(Structural_Similarity_3d(field, field) - 1.0) < 1e-9
    other = generator.random((12, 12, 12))
    assert Structural_Similarity_3d(other, field) < 0.5


def Test_Curve_Distances_Have_Their_Analytic_Values() -> None:
    """the curve error and the transport distance on shifted point masses"""
    first = np.zeros(64)
    second = np.zeros(64)
    first[10] = 1.0
    second[20] = 1.0
    spacing = 0.25
    assert abs(Wasserstein_1d(first, second, spacing) - 10 * spacing) < 1e-9
    assert abs(Curve_L1(first, second, spacing) - 2.0) < 1e-12


def Test_Aggregates_Behave() -> None:
    """the fraction, quartile and bootstrap aggregates on tiny cases"""
    errors = np.asarray([0.05, 0.2, -0.08])
    assert abs(Fraction_Within(errors, 0.1) - 2.0 / 3.0) < 1e-12
    median, interquartile = Median_And_Interquartile(np.asarray([1.0, 2.0, 3.0, 4.0]))
    assert median == 2.5 and interquartile == 1.5
    lower_bound, upper_bound = Bootstrap_Confidence_Interval(np.full(8, 3.25))
    assert lower_bound == 3.25 and upper_bound == 3.25


def Test_The_Occupancy_Walk_And_Rebuild_Are_Consistent() -> None:
    """the synthetic gap, and the state count the rebuild normalizes to"""
    energies = np.asarray([[[-1.0, 2.0]]])
    occupancies = np.asarray([[[1.0, 0.0]]])
    assert Occupancy_Walk_Gap(energies, occupancies) == 3.0
    grid = np.linspace(-8.0, 8.0, 4001)
    curve = Rebuild_Density_Of_States(energies, np.asarray([1.0]), 0.2, grid)
    integral = float(np.trapezoid(curve, grid))
    assert abs(integral - 2.0) < 1e-6


@pytest.mark.pool
def Test_The_Gap_Walk_Matches_The_Census_Labels() -> None:
    """the occupancy walk reproduces the census gap on sampled live runs"""
    census_rows = [
        census_row
        for census_row in Read_Census(POOL_ROOT)
        if isinstance(census_row.record.get("eig_gap"), float)
        and census_row.file_sizes.get("EIGENVAL", 0) > 0
        and census_row.record.get("o_complete")
    ]
    sampled = census_rows[:: max(1, len(census_rows) // 25)][:25]
    assert len(sampled) >= 20
    for census_row in sampled:
        eigenvalues = Read_Eigenvalues(POOL_ROOT / census_row.path / "EIGENVAL")
        walked = Occupancy_Walk_Gap(eigenvalues.energies, eigenvalues.occupancies)
        recorded = cast(float, census_row.record["eig_gap"])
        assert abs(walked - recorded) < 1e-3, (census_row.path, walked, recorded)
