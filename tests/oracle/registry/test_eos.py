"""The equation of state, against a fit somebody else already published.

This is the rare case where a computation has a known right answer that was not produced
by this code. `apparatus/data/diamond-strain-sweep/02-how-to-read-and-derive.md` carries a verified
Birch-Murnaghan fit of the same 47-point PBE series::

    | PBE | 11.4133 | 3.5740 | 434.2 | 3.66 | 0.15 meV |

So these tests are a re-derivation with the answer known in advance, not a measurement.
A fit that lands on 434.2 is right; one that lands on 443 has silently fitted experiment
instead of the data, which is exactly the failure mode a self-check cannot catch.

The synthetic half needs no data at all: round-tripping the closed form through the
fitter recovers its own parameters, and a corrupted curve must raise the residual. A fit
that only demonstrates it converges has not shown it discriminates.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

from programs.oracle.registry.eos import (
    EV_PER_ANGSTROM3_TO_GPA,
    birch_murnaghan_energy,
    equilibrium_volume_from_pressure,
    fit_energy_volume,
    pulay_bias_percent,
)

# The dataset's own verified PBE fit -- the oracle for the real-data tests.
PUBLISHED = dict(volume=11.4133, lattice=3.5740, bulk=434.2, bulk_prime=3.66, residual_mev=0.15)
PUBLISHED_PULAY_PERCENT = 0.109

DEFAULT_FAMILY = Path.home() / ".cache" / "n-op-vasp" / "1-scale-all-axes-uniformly"


# ---------------------------------------------------------------------------
# Synthetic: the fitter against its own closed form. No data required.
# ---------------------------------------------------------------------------

def _synthetic(v0=11.4133, b0=434.2, bp=3.66, e0=-18.2, n=25, spread=0.10):
    volumes = np.linspace(v0 * (1 - spread), v0 * (1 + spread), n)
    return volumes, birch_murnaghan_energy(volumes, e0, v0, b0, bp)


def test_fit_recovers_the_parameters_it_was_generated_from():
    volumes, energies = _synthetic()
    eos = fit_energy_volume(volumes, energies)
    assert eos.equilibrium_volume == pytest.approx(11.4133, rel=1e-6)
    assert eos.bulk_modulus == pytest.approx(434.2, rel=1e-6)
    assert eos.bulk_modulus_pressure_derivative == pytest.approx(3.66, rel=1e-6)
    assert eos.max_residual_ev < 1e-9, "an exact curve must fit exactly"


def test_a_corrupted_curve_raises_the_residual():
    """The discriminating direction. A fitter that always reports a small residual is useless."""
    volumes, energies = _synthetic()
    clean = fit_energy_volume(volumes, energies).max_residual_ev

    energies = np.asarray(energies).copy()
    energies[len(energies) // 2] += 0.05  # 50 meV on one point
    dirty = fit_energy_volume(volumes, energies).max_residual_ev

    assert dirty > 1e-3, "a 50 meV outlier must show up in the residual"
    assert dirty > 1000 * clean


def test_cubic_lattice_constant_inverts_the_fcc_volume_relation():
    volumes, energies = _synthetic(v0=3.5740 ** 3 / 4.0)
    assert fit_energy_volume(volumes, energies).cubic_lattice_constant == pytest.approx(
        3.5740, rel=1e-6
    )


def test_four_points_are_the_minimum_for_four_parameters():
    volumes, energies = _synthetic(n=3)
    with pytest.raises(ValueError, match="cannot determine"):
        fit_energy_volume(volumes, energies)


def test_pressure_root_is_exact_on_a_straight_line():
    volumes = np.array([11.30, 11.35, 11.40, 11.45, 11.50])
    pressures = -38.0 * (volumes - 11.4013)
    assert equilibrium_volume_from_pressure(volumes, pressures) == pytest.approx(11.4013, rel=1e-9)


def test_a_series_that_never_crosses_zero_refuses():
    """No extrapolating to a crossing the data does not reach."""
    volumes = np.array([11.0, 11.1, 11.2, 11.3])
    with pytest.raises(ValueError, match="do not bracket zero"):
        equilibrium_volume_from_pressure(volumes, np.array([5.0, 4.0, 3.0, 2.0]))


def test_the_unit_conversion_is_the_codata_value():
    """1 eV/A^3 in GPa. A wrong constant here scales every bulk modulus silently."""
    assert EV_PER_ANGSTROM3_TO_GPA == pytest.approx(1.602176634e-19 / 1e-30 / 1e9, rel=1e-9)


# ---------------------------------------------------------------------------
# Real data: against the published fit. Skips without an extracted family.
# ---------------------------------------------------------------------------

pytest.importorskip("pymatgen", reason="the VASP reader needs pymatgen")


@pytest.fixture(scope="module")
def series():
    from programs.oracle.seams.sweep import read_family

    family = Path(os.environ.get("NOP_SWEEP_FAMILY", DEFAULT_FAMILY))
    if not family.is_dir():
        pytest.skip(
            f"no extracted strain family at {family}; run apparatus/tools/extract_sweep_family.sh. "
            "The dataset is on /Pool and is never committed."
        )
    points = read_family(family)
    if len(points) < 10:
        pytest.skip(f"only {len(points)} points extracted; need the full family")
    return points


def test_energy_route_reproduces_the_published_fit(series):
    """All four parameters, against a fit this code did not produce."""
    from programs.oracle.seams.sweep import energy_volume_curve

    eos = fit_energy_volume(*energy_volume_curve(series))
    assert eos.equilibrium_volume == pytest.approx(PUBLISHED["volume"], abs=5e-4)
    assert eos.cubic_lattice_constant == pytest.approx(PUBLISHED["lattice"], abs=5e-4)
    assert eos.bulk_modulus == pytest.approx(PUBLISHED["bulk"], abs=0.5)
    assert eos.bulk_modulus_pressure_derivative == pytest.approx(PUBLISHED["bulk_prime"], abs=0.02)
    # The published residual is 0.15 meV; anything far above it means a bad point crept in.
    assert eos.max_residual_ev * 1000 < 0.25


def test_the_two_routes_disagree_by_the_published_pulay_bias(series):
    """The residual worth more than either route: it grades the basis, not the structure."""
    from programs.oracle.seams.sweep import energy_volume_curve, pressure_volume_curve

    energy_v0 = fit_energy_volume(*energy_volume_curve(series)).equilibrium_volume
    stress_v0 = equilibrium_volume_from_pressure(*pressure_volume_curve(series))

    assert energy_v0 > stress_v0, "an incomplete basis puts the energy route at larger volume"
    assert pulay_bias_percent(energy_v0, stress_v0) == pytest.approx(
        PUBLISHED_PULAY_PERCENT, abs=0.02
    )


def test_the_pressure_window_is_calibrated_not_arbitrary(series):
    """Widening the window biases the root monotonically, and past ~15 GPa inverts the sign.

    This is the calibration recorded in `equilibrium_volume_from_pressure`, kept executable
    so a later change to the default cannot quietly undo it.
    """
    from programs.oracle.seams.sweep import energy_volume_curve, pressure_volume_curve

    energy_v0 = fit_energy_volume(*energy_volume_curve(series)).equilibrium_volume
    volumes, pressures = pressure_volume_curve(series)

    biases = [
        pulay_bias_percent(energy_v0, equilibrium_volume_from_pressure(volumes, pressures, w))
        for w in (3.0, 7.5, 10.0, 20.0)
    ]
    assert biases == sorted(biases, reverse=True), "the bias must fall monotonically with width"
    assert biases[0] > 0.09, "the default window recovers the published bias"
    assert biases[-1] < 0, "a 20 GPa window inverts the sign of a physical effect"


def test_the_lattice_constant_meets_the_regime_the_ledger_now_declares(series):
    """Regime #60: +/-1% against experiment, in the computed currency.

    Also the negative half of that finding: the battery's own +/-0.001 A would refuse this
    frame, which is why the regime had to be stated in the currency the number is computed in.
    """
    from programs.oracle.seams.sweep import energy_volume_curve

    a0 = fit_energy_volume(*energy_volume_curve(series)).cubic_lattice_constant
    anchor, measurement_uncertainty = 3.567, 0.001

    assert abs(a0 - anchor) / anchor <= 0.01, "PBE must sit inside the +/-1% computed regime"
    assert abs(a0 - anchor) > 5 * measurement_uncertainty, (
        "and outside the measurement's uncertainty by several times -- the reason the "
        "regime cannot be the battery's error bar"
    )
