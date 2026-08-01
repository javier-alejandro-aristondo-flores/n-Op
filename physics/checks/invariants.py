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

from ..cert import CertEvidence, RefusalMode
from ..residual import (
    CategoryTag,
    ContributionFacets,
    Producer,
    ResidualKey,
    ResidualMap,
    axes,
)
from ..state import Frame


@dataclass(frozen=True)
class InvariantCheck:
    """One closed-form self-consistency check on a computed frame."""

    name: str
    #: frame attributes that must be non-None for the check to be evaluable
    reads: tuple[str, ...]
    #: frame -> raw deviation (never squared, never normalised, never thresholded)
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

    Calibrated against a known-good spin-polarised run: with two spin channels and
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
    """Spin parity -- "an odd electron count forces an odd integer magnetisation".

    The deviation is the distance from the reported moment to the nearest integer of the
    *required* parity: odd integers when the electron count is odd, even integers when it
    is even. Zero for a moment that satisfies the rule, and it grows smoothly with the
    violation rather than returning a bare boolean, because the consumer decides severity.
    """
    required_parity = round(frame.n_electrons) % 2
    m = frame.magnetic_moment
    candidates = [n for n in range(-12, 13) if abs(n) % 2 == required_parity]
    return float(min(abs(m - n) for n in candidates))


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
        written="an odd electron count forces an odd integer magnetisation",
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
