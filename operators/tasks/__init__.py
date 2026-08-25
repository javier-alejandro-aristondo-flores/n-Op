"""Task cards — what is being predicted, from what, judged how.

One dataclass per suite task, mirroring test-suite.md entries. Without this module, task
logic (which fields in and out, which loss, which metrics, which conservation law, which
covariates, which split) smears into the operators — and that, not the abstraction count, is
what makes implementations hard. Conservation wrappers read the task card, which is why they
attach to task heads and not to operators.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TaskCard:
    """One task of the suite, stated as data.

    Fields are declarative names resolved by the data and training layers; the authoritative
    prose lives in test-suite.md, referenced by ``suite_card``.
    """

    name: str  # e.g. "density-to-electron-localization"
    suite_card: str  # e.g. "test-suite.md §2, Pattern I"
    inputs: tuple[str, ...]  # channel labels in
    targets: tuple[str, ...]  # channel labels out
    loss: str  # e.g. "relative-L2" | "mean-absolute-error"
    metrics: tuple[str, ...]
    conservation: str | None  # e.g. "renormalize-electron-count" | "zero-mean" | None
    covariates: tuple[str, ...]  # e.g. ("functional", "exact-exchange-fraction")
    split: str  # named split from operators.data.splits
