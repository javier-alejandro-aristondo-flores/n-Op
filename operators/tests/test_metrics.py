"""Checks the metrics on analytic cases and the gap walk against the census labels."""

from typing import cast

import numpy as np
import pytest

from operators.data.parsers import Read_Eigenvalues
from operators.data.spectra import Occupancy_Walk_Gap, Rebuild_Density_Of_States
from operators.data.store import POOL_ROOT, Read_Census
from operators.metrics import (
    Bootstrap_Confidence_Interval,
    Curve_L1,
    Fraction_Within,
    Frequency_Split_Relative_L2,
    Mean_Removed_Relative_L2,
    Median_And_Interquartile,
    Relative_L2,
    Structural_Similarity_3d,
    Wasserstein_1d,
)


def Test_Field_Errors_Have_Their_Analytic_Values() -> None:
    """Asserts the relative and mean-removed errors on closed-form cases."""
    truth = np.asarray([3.0, 4.0])
    assert Relative_L2(truth, truth) == 0.0
    assert abs(Relative_L2(2.0 * truth, truth) - 1.0) < 1e-12
    assert Mean_Removed_Relative_L2(truth + 5.0, truth) < 1e-12


def Test_The_Frequency_Split_Separates_Bands() -> None:
    """Asserts low-mode agreement survives high-mode contamination."""
    coordinates = np.arange(8) / 8.0
    x, y, _ = np.meshgrid(coordinates, coordinates, coordinates, indexing="ij")
    truth = np.cos(2.0 * np.pi * x)
    contaminated = truth + 0.5 * np.cos(2.0 * np.pi * 3.0 * (x + y))
    low_error, high_error = Frequency_Split_Relative_L2(contaminated, truth, cutoff_modes=2.0)
    assert low_error < 1e-12
    assert high_error > 0.0


def Test_Structural_Similarity_Ranks_Agreement() -> None:
    """Asserts identical fields score one and unrelated noise scores much lower."""
    generator = np.random.default_rng(7)
    field = generator.random((12, 12, 12))
    assert abs(Structural_Similarity_3d(field, field) - 1.0) < 1e-9
    other = generator.random((12, 12, 12))
    assert Structural_Similarity_3d(other, field) < 0.5


def Test_Curve_Distances_Have_Their_Analytic_Values() -> None:
    """Asserts the curve error and transport distance on shifted point masses."""
    first = np.zeros(64)
    second = np.zeros(64)
    first[10] = 1.0
    second[20] = 1.0
    spacing = 0.25
    assert abs(Wasserstein_1d(first, second, spacing) - 10 * spacing) < 1e-9
    assert abs(Curve_L1(first, second, spacing) - 2.0) < 1e-12


def Test_Aggregates_Behave() -> None:
    """Asserts the fraction, quartile, and bootstrap aggregates on tiny cases."""
    errors = np.asarray([0.05, 0.2, -0.08])
    assert abs(Fraction_Within(errors, 0.1) - 2.0 / 3.0) < 1e-12
    median, interquartile = Median_And_Interquartile(np.asarray([1.0, 2.0, 3.0, 4.0]))
    assert median == 2.5 and interquartile == 1.5
    low, high = Bootstrap_Confidence_Interval(np.full(8, 3.25))
    assert low == 3.25 and high == 3.25


def Test_The_Occupancy_Walk_And_Rebuild_Are_Consistent() -> None:
    """Asserts the synthetic gap and the state-count normalization of the rebuild."""
    energies = np.asarray([[[-1.0, 2.0]]])
    occupancies = np.asarray([[[1.0, 0.0]]])
    assert Occupancy_Walk_Gap(energies, occupancies) == 3.0
    grid = np.linspace(-8.0, 8.0, 4001)
    curve = Rebuild_Density_Of_States(energies, np.asarray([1.0]), 0.2, grid)
    integral = float(np.trapezoid(curve, grid))
    assert abs(integral - 2.0) < 1e-6


@pytest.mark.pool
def Test_The_Gap_Walk_Matches_The_Census_Labels() -> None:
    """Asserts the occupancy walk reproduces the census gap on sampled live runs."""
    if not POOL_ROOT.exists():
        pytest.fail("the corpus at /Pool/VASP_DATA is not mounted on this machine")
    rows = [
        row
        for row in Read_Census(POOL_ROOT)
        if isinstance(row.record.get("eig_gap"), float)
        and row.file_sizes.get("EIGENVAL", 0) > 0
        and row.record.get("o_complete")
    ]
    sampled = rows[:: max(1, len(rows) // 25)][:25]
    assert len(sampled) >= 20
    for row in sampled:
        eigenvalues = Read_Eigenvalues(POOL_ROOT / row.path / "EIGENVAL")
        walked = Occupancy_Walk_Gap(eigenvalues.energies, eigenvalues.occupancies)
        recorded = cast(float, row.record["eig_gap"])
        assert abs(walked - recorded) < 1e-3, (row.path, walked, recorded)
