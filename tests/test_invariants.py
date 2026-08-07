"""The invariant checks, tested in both directions.

A check that only demonstrates it fires cannot tell you it fires *too often*. So every
check here is exercised twice: once on a well-formed diamond frame, where it must stay
silent, and once on a frame corrupted in exactly the way that check exists to catch,
where it must fire. That two-sided discipline is the corpus's own
(`check_the_checker.py` carries negative probes for the same reason).

These frames are synthetic and in-memory. Nothing here reads `/Pool`, so the suite runs
anywhere and cannot be broken by the dataset being unmounted -- the real-data path is
`test_ingest_pool.py`, which skips when the dataset is absent.

No VASP output is committed to this repository: every run directory on `/Pool` holds a
licensed pseudopotential and this remote is public.
"""

from __future__ import annotations

import numpy as np
import pytest

from physics.cert import CertEvidence, RefusalMode
from physics.checks.invariants import INVARIANT_CHECKS, run_invariants
from physics.residual import ResidualMap
from physics.state import CrystalState, Frame

# Diamond, primitive cell, at the experimental lattice constant.
# `mvp-system.md`: "primitive vectors in the (a/2)(0,1,1), (a/2)(1,0,1), (a/2)(1,1,0)
# convention -- i.e. component value 1.7835 A -- with carbon atoms at fractional
# (0,0,0) and (1/4,1/4,1/4)". Eight valence electrons give four occupied bands.
A0 = 3.567
HALF = A0 / 2.0
QUARTER = A0 / 4.0


def diamond_state() -> CrystalState:
    cell = HALF * np.array([[0.0, 1.0, 1.0],
                            [1.0, 0.0, 1.0],
                            [1.0, 1.0, 0.0]])
    positions = np.array([[0.0, 0.0, 0.0],
                          [QUARTER, QUARTER, QUARTER]])
    return CrystalState(cell=cell, positions=positions, species=np.array([6, 6]))


def good_frame(**overrides) -> Frame:
    """A frame that every check must pass. Overrides corrupt exactly one channel."""
    state = diamond_state()
    n_kpoints, n_occupied = 10, 4
    fields = dict(
        state=state,
        forces=np.zeros((2, 3)),
        stress=np.diag([-0.0503, -0.0503, -0.0503]),
        # one spin channel, fully occupied valence bands: the check doubles for spin
        occupations=[np.ones((n_kpoints, n_occupied))],
        kpoint_weights=np.full(n_kpoints, 1.0 / n_kpoints),
        n_electrons=8.0,
        magnetic_moment=0.0,
        reported_volume=state.volume,
    )
    fields.update(overrides)
    return Frame(**fields)


def scores(frame: Frame) -> tuple[dict[str, float], CertEvidence]:
    """Run every check; return {check name: value} for those that emitted, plus the cert."""
    residuals, cert = ResidualMap(), CertEvidence()
    run_invariants(frame, residuals, cert)
    emitted = {
        check.name: residuals.values[check.key]
        for check in INVARIANT_CHECKS
        if check.key in residuals
    }
    return emitted, cert


# ---------------------------------------------------------------------------
# Negative direction: a good frame must not make any check fire.
# ---------------------------------------------------------------------------

def test_good_frame_emits_every_check_at_zero():
    emitted, cert = scores(good_frame())
    assert len(emitted) == len(INVARIANT_CHECKS), (
        f"a well-formed frame should evaluate every check; got {sorted(emitted)}"
    )
    assert not cert.refusals, f"nothing should refuse on a complete frame: {cert.refusals}"
    for name, value in emitted.items():
        assert value == pytest.approx(0.0, abs=1e-12), f"{name} fired on a good frame: {value}"


def test_diamond_cell_reproduces_the_documented_volume():
    """V0 = a^3/4 = 11.345 A^3, per `mvp-system.md`. Guards the fixture itself."""
    assert diamond_state().volume == pytest.approx(A0 ** 3 / 4.0, rel=1e-12)
    assert diamond_state().volume == pytest.approx(11.345, abs=5e-3)


# ---------------------------------------------------------------------------
# Positive direction: one corruption per check, and it must be the *only* one that fires.
# ---------------------------------------------------------------------------

# Some channels are legitimately read by more than one check, so a single-channel
# corruption can fire more than one. Where that happens it is declared, not waived: the
# `also` set is exact, so a corruption leaking into an *undeclared* check still fails.
CORRUPTIONS = [
    # (check that must fire, override, expected magnitude, other checks that must also fire)
    ("net-force-vanishes",
     dict(forces=np.array([[0.1, 0.0, 0.0], [0.0, 0.0, 0.0]])), 0.1, set()),
    ("stress-tensor-symmetric",
     dict(stress=np.array([[0.0, 0.7, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])), 0.7, set()),
    # Corrupt the occupations, not `n_electrons`: the electron count is read by the
    # parity check too. Three occupied bands instead of four gives 3 x 2 spin = 6
    # against a declared 8, and every occupancy stays inside [0, 1].
    ("occupations-sum-to-electron-count",
     dict(occupations=[np.ones((10, 3))]), 2.0, set()),
    ("lattice-determinant-equals-volume",
     dict(reported_volume=12.0), 12.0 - A0 ** 3 / 4.0, set()),
    # 8 electrons is even, so an even integer moment is required; 1.0 is distance 1 from 0 and 2
    ("spin-parity",
     dict(magnetic_moment=1.0), 1.0, set()),
    # Occupancies summing to 4 per k-point, so the electron count still balances, but
    # two of them sit above 1. Isolates the Pauli bound from the sum rule.
    ("occupations-within-unit-interval",
     dict(occupations=[np.tile([1.3, 1.3, 1.0, 0.4], (10, 1))]), 0.3, set()),
    # Weights are read by the electron count too, and no reweighting breaks the
    # normalization while leaving the count intact -- so this one is declared.
    ("kpoint-weights-sum-to-one",
     dict(kpoint_weights=np.full(10, 1.1 / 10)), 0.1,
     {"occupations-sum-to-electron-count"}),
]


@pytest.mark.parametrize("name,override,expected,also", CORRUPTIONS,
                         ids=[c[0] for c in CORRUPTIONS])
def test_corruption_fires_its_own_check_and_only_the_declared_others(name, override, expected, also):
    emitted, _ = scores(good_frame(**override))
    assert emitted[name] == pytest.approx(expected, rel=1e-9), f"{name} did not catch it"
    others = {k for k, v in emitted.items() if k != name and abs(v) > 1e-12}
    assert others == also, (
        f"corrupting {name} fired {sorted(others)}; declared {sorted(also)}"
    )


def test_spin_parity_accepts_the_right_parity_and_rejects_the_wrong_one():
    """An odd electron count forces an odd integer moment. Both directions on one check."""
    assert scores(good_frame(n_electrons=7.0, magnetic_moment=1.0))[0]["spin-parity"] == 0.0
    assert scores(good_frame(n_electrons=7.0, magnetic_moment=0.0))[0]["spin-parity"] == 1.0


# ---------------------------------------------------------------------------
# Refusal is absence: a missing channel must produce no key, not a zero.
# ---------------------------------------------------------------------------

def test_missing_channel_refuses_rather_than_scoring_zero():
    """The defect this exists to prevent: a check silently reporting 0.0 for absent input."""
    emitted, cert = scores(good_frame(magnetic_moment=None))
    assert "spin-parity" not in emitted, "an unevaluable check must emit no key at all"
    assert len(cert.refusals) == 1
    refusal = cert.refusals[0]
    assert refusal.mode is RefusalMode.INPUT_CHANNEL_ABSENT
    assert refusal.witness["channels_missing"] == 1.0
    assert refusal.witness["channels_required"] == 2.0


def test_an_empty_frame_refuses_everything_and_emits_nothing():
    emitted, cert = scores(Frame(state=diamond_state()))
    assert emitted == {}
    assert len(cert.refusals) == len(INVARIANT_CHECKS)
    assert cert.checks_evaluated == 0


def test_absence_discipline_holds():
    """No key may be both emitted and refused."""
    residuals, cert = ResidualMap(), CertEvidence()
    run_invariants(good_frame(magnetic_moment=None), residuals, cert)
    cert.assert_absence_discipline(set(residuals.values))
