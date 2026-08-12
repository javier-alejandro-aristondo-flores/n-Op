"""The training section — fitting under the splits the exams will use.

Twins `journals/operator/training/`, whose page `training-stages` owns the stage
sequence. The invariant this section carries is that the exams are never fitted
on: selection happens on inner folds only.

The package name matches the module it replaced, so every existing
`from training import ...` keeps resolving after the move into a section
directory. That is deliberate — the reorganization is meant to change what the
paths say, not what the callers do.
"""

from .training import (  # noqa: F401
    INNER_SPLITS,
    N_SPLITS,
    SEED,
    FoldResult,
    choose,
    hse_field_from,
    hse_field_from_rows,
    on_split,
    out_of_fold,
    select_gap_weight,
)
