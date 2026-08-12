"""Certification evidence, and the refusal enum -- finally enumerated.

The corpus states its headline principle forcefully:

    A check the oracle cannot stand behind for this instance -- inapplicable, outside the
    certified envelope, or refused by certification -- is not in the compiled kernel, so
    its key is simply not in any map. The *reason* is machine data in the certification
    record: a closed-enum refusal mode plus numeric witnesses. No prose, anywhere.

Auditor 3 found that enum never enumerated, and found the one admission that it is
unwritten scoped only to the evolver hand-off -- a narrow confession attached to a
system-wide dependency. Three separate findings from two auditors who never spoke
(`X9`, `X10`, `S10`) landed on it.

This module closes it. The three reasons named in the sentence above become three members;
a fourth is added for the case this slice actually meets in the wild.

**The discipline this module exists to enforce:** a refused check emits *no key*. Not a
zero, not a NaN, not a sentinel. The absence is the signal, and the reason lives here.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum

from ..laws.residual import ResidualKey


class RefusalMode(Enum):
    """Closed enum. The first three are the corpus's own three reasons, verbatim from
    `product.md`; the fourth is what a real frame forces and is stated rather than
    smuggled in as one of the others."""

    #: The check does not apply to this crystal identity at all -- pruned at compile time.
    INAPPLICABLE = "inapplicable"

    #: The runtime environment left the validity box the kernel was stamped with.
    OUTSIDE_CERTIFIED_ENVELOPE = "outside-certified-envelope"

    #: Certification declined to stand behind this check for this instance.
    CERTIFICATION_REFUSED = "certification-refused"

    #: A channel the check reads is not present in the supplied frame, so the check
    #: cannot be evaluated -- as distinct from evaluating to zero. The spin-parity
    #: check on a non-spin-polarized run is exactly this: no moment is reported, so
    #: there is nothing to test parity against. Reporting 0.0 here would assert that
    #: the frame *passed*, which is the specific lie this mode exists to prevent.
    INPUT_CHANNEL_ABSENT = "input-channel-absent"


@dataclass(frozen=True)
class Refusal:
    """One refused check: which key is absent, why, and the numbers that justify it.

    `witness` is required and must be non-empty. A refusal with no numeric witness is
    prose wearing an enum, and the corpus bars prose here.
    """

    key: ResidualKey
    mode: RefusalMode
    witness: dict[str, float]

    def __post_init__(self) -> None:
        if not self.witness:
            raise ValueError(
                f"refusal of {self.key} carries no numeric witness; "
                "a refusal without numbers is prose"
            )


@dataclass
class CertEvidence:
    """The fourth return of `Validate`.

    Holds the refusals -- the machine-readable account of every key that is *absent*
    from the residual map and why -- plus the identity of the kernel that produced it.
    """

    kernel_hash: str = ""
    refusals: list[Refusal] = field(default_factory=list)
    checks_compiled: int = 0

    def refuse(self, key: ResidualKey, mode: RefusalMode, **witness: float) -> None:
        self.refusals.append(Refusal(key=key, mode=mode, witness=dict(witness)))

    @property
    def checks_evaluated(self) -> int:
        return self.checks_compiled - len(self.refusals)

    def refused_keys(self) -> set[ResidualKey]:
        return {r.key for r in self.refusals}

    def by_mode(self, mode: RefusalMode) -> list[Refusal]:
        return [r for r in self.refusals if r.mode is mode]

    def assert_absence_discipline(self, emitted: set[ResidualKey]) -> None:
        """The invariant that makes "refusal is absence" true rather than aspirational.

        A refused key must not also appear in the residual map. Called by `Validate`
        before returning, so the two halves can never drift apart silently.
        """
        both = self.refused_keys() & emitted
        if both:
            raise AssertionError(
                "refusal-is-absence violated: these keys were both refused and emitted: "
                + ", ".join(sorted(str(k) for k in both))
            )


def content_hash(payload: bytes) -> str:
    """The one hash function. `product.md` requires file hash to equal kernel hash, so
    there must be exactly one of these and every caller must use it."""
    return hashlib.blake2b(payload, digest_size=32).hexdigest()
