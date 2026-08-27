"""Task cards naming the inputs, targets, loss, metrics, and split of one suite task."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TaskCard:
    """One suite task stated as data."""

    name: str
    suite_card: str
    inputs: tuple[str, ...]
    targets: tuple[str, ...]
    loss: str
    metrics: tuple[str, ...]
    conservation: str | None
    covariates: tuple[str, ...]
    split: str
