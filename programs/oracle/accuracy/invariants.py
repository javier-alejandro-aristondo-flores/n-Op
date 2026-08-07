"""The reference-battery invariant checks.

`reference-battery.md` states five closed forms that any correct calculation already
satisfies, and makes the case for why they earn their place:

    Closed form, one pass per frame, and **no anchor is required** -- the calculation is
    checked against itself rather than against a curated value.

    They catch parser bugs and run failures together, and both are otherwise invisible

That is what makes them the right first residuals in the program: they need no curated
reference value, no compiled physics, and no gradient -- and they still say something true.

Each check declares the frame channels it reads. A check whose channels are not all present
does not score zero; it **refuses**, its key is absent from the residual map, and the reason
plus a numeric witness goes to the certificate. That is `refusal is absence`, made real.

One correction the corpus owes itself, recorded here rather than silently implemented:
`reference-battery.md` says each of the five "follows from a conservation law", and its own
table gives the law for `det(A) = V` as `arithmetic`. Arithmetic is not a conservation law.
The check is sound; the framing sentence over-claims by one row (auditor 2 finding).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from ..certification.cert import CertEvidence, RefusalMode
from ..laws.residual import (
    CategoryTag,
    ContributionFacets,
    Producer,
    ResidualKey,
    ResidualMap,
    axes,
)
from ..state.state import Frame


@dataclass(frozen=True)
class InvariantCheck:
    """One closed-form self-consistency check on a computed frame."""

    name: str
    #: frame attributes that must be non-None for the check to be evaluable
    reads: tuple[str, ...]
    #: frame -> raw deviation (never squared, never normalized, never thresholded)
    evaluate: Callable[[Frame], float]
    category: CategoryTag
    unit: str
    #: what the deviation means, for the static slot schema
    written: str

    @property
    def key(self) -> ResidualKey:
        return ResidualKey(producer=Producer("invariant", self.name), axis_tuple=axes())

    def missing_channels(self, frame: Frame) -> list[str]:
        return [c for c in self.reads if getattr(frame, c, None) is None]


# ---------------------------------------------------------------------------
# The five closed forms
# ---------------------------------------------------------------------------

def _net_force(frame: Frame) -> float:
    """`Sum_I f_I = 0` -- forces summed over ions vanish. Translational invariance."""
    return float(np.linalg.norm(np.sum(frame.forces, axis=0)))


def _stress_symmetry(frame: Frame) -> float:
    """`sigma_ij = sigma_ji` -- the stress tensor is symmetric. Angular momentum."""
    s = frame.stress
    return float(np.max(np.abs(s - s.T)))


def _electron_count(frame: Frame) -> float:
    """`Sum_nk w_k f_nk = NELECT` -- occupations sum to the electron count.

    Calibrated against a known-good spin-polarized run: with two spin channels and
    k-weights summing to 1, the raw weighted sum equals NELECT with no spin factor.
    A collinear run with a single channel carries a factor of two, applied here rather
    than assumed away.
    """
    w = frame.kpoint_weights[:, None]
    total = sum(float(np.sum(w * occ)) for occ in frame.occupations)
    if len(frame.occupations) == 1:
        total *= 2.0
    return float(abs(total - frame.n_electrons))


def _volume_consistency(frame: Frame) -> float:
    """`det(A) = V` -- the lattice determinant equals the reported volume.

    The corpus files this under a conservation law; it is arithmetic. It is still the
    cheapest parser-bug detector in the set, because a mis-parsed lattice and a correctly
    parsed volume disagree immediately.
    """
    return float(abs(abs(np.linalg.det(frame.state.cell)) - frame.reported_volume))


def _spin_parity(frame: Frame) -> float:
    """Spin parity -- "an odd electron count forces an odd integer magnetization".

    The deviation is the distance from the reported moment to the nearest integer of the
    *required* parity: odd integers when the electron count is odd, even integers when it
    is even. Zero for a moment that satisfies the rule, and it grows smoothly with the
    violation rather than returning a bare boolean, because the consumer decides severity.
    """
    required_parity = round(frame.n_electrons) % 2
    m = frame.magnetic_moment
    candidates = [n for n in range(-12, 13) if abs(n) % 2 == required_parity]
    return float(min(abs(m - n) for n in candidates))


def _occupation_bounds(frame: Frame) -> float:
    """`0 <= f_nk <= 1` -- the Pauli exclusion principle, per spin channel.

    The deviation is the largest excursion outside the unit interval, in either
    direction. A correct calculation satisfies this exactly, so any nonzero value is a
    parser bug (reading the wrong column, or a spin-degenerate occupancy of 2 recorded
    where the schema expects 1) rather than a physical result.
    """
    worst = 0.0
    for occ in frame.occupations:
        worst = max(worst, float(np.max(occ) - 1.0), float(-np.min(occ)))
    return max(worst, 0.0)


def _kpoint_weight_normalisation(frame: Frame) -> float:
    """`Sum_k w_k = 1` -- the Brillouin-zone measure integrates to one.

    Cheap, and it guards every k-integrated quantity at once: unnormalized weights make
    the electron count, the density of states and every transport integral wrong by the
    same silent factor, while each of them individually still looks plausible.

    **This check has a noise floor set by the producing file, not by the calculation,
    and it is the only one of these that does.** The weights are exact rationals -- `n/N`
    over the mesh -- but VASP prints them to eight decimals, so the parsed values sum to
    slightly under one. Measured on a 7x7x7 mesh with 172 irreducible points: the printed
    values sum to 0.99999935, a deviation of 6.5e-7, and the exact rationals sum to 1.
    The floor therefore grows with the k-point count, at roughly 4e-9 per point. Any
    tolerance placed on this residual must sit above that, and a value at the floor is
    the file's precision rather than a defect.
    """
    return float(abs(np.sum(frame.kpoint_weights) - 1.0))


INVARIANT_CHECKS: tuple[InvariantCheck, ...] = (
    InvariantCheck(
        name="net-force-vanishes",
        reads=("forces",),
        evaluate=_net_force,
        category=CategoryTag.CONSERVATION,
        unit="eV/angstrom",
        written="Sum_I f_I = 0",
    ),
    InvariantCheck(
        name="stress-tensor-symmetric",
        reads=("stress",),
        evaluate=_stress_symmetry,
        category=CategoryTag.CONSERVATION,
        unit="GPa",
        written="sigma_ij = sigma_ji",
    ),
    InvariantCheck(
        name="occupations-sum-to-electron-count",
        reads=("occupations", "kpoint_weights", "n_electrons"),
        evaluate=_electron_count,
        category=CategoryTag.CONSERVATION,
        unit="electrons",
        written="Sum_nk w_k f_nk = NELECT",
    ),
    InvariantCheck(
        name="lattice-determinant-equals-volume",
        reads=("reported_volume",),
        evaluate=_volume_consistency,
        category=CategoryTag.STATIC_SNAPSHOT,
        unit="angstrom^3",
        written="det(A) = V",
    ),
    InvariantCheck(
        name="spin-parity",
        reads=("magnetic_moment", "n_electrons"),
        evaluate=_spin_parity,
        category=CategoryTag.STATIC_SNAPSHOT,
        unit="bohr_magneton",
        written="an odd electron count forces an odd integer magnetization",
    ),
    InvariantCheck(
        name="occupations-within-unit-interval",
        reads=("occupations",),
        evaluate=_occupation_bounds,
        category=CategoryTag.POSITIVITY,
        unit="dimensionless",
        written="0 <= f_nk <= 1",
    ),
    InvariantCheck(
        name="kpoint-weights-sum-to-one",
        reads=("kpoint_weights",),
        evaluate=_kpoint_weight_normalisation,
        category=CategoryTag.ALGEBRAIC_SUM_RULES,
        unit="dimensionless",
        written="Sum_k w_k = 1",
    ),
)


def run_invariants(
    frame: Frame,
    residuals: ResidualMap,
    cert: CertEvidence,
    checks: tuple[InvariantCheck, ...] = INVARIANT_CHECKS,
) -> None:
    """Evaluate every check that can be evaluated; refuse the rest.

    Mutates `residuals` and `cert`. Emits nothing for a refused check -- that is the
    point -- and never emits a sentinel value.
    """
    cert.checks_compiled += len(checks)
    for check in checks:
        missing = check.missing_channels(frame)
        if missing:
            cert.refuse(
                check.key,
                RefusalMode.INPUT_CHANNEL_ABSENT,
                channels_missing=float(len(missing)),
                channels_required=float(len(check.reads)),
            )
            continue
        residuals.emit(
            check.key,
            check.evaluate(frame),
            ContributionFacets(category=check.category, bundle="reference-battery"),
        )
