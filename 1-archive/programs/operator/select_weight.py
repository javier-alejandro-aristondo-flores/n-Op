"""Choose the auxiliary gap weight without consulting an exam.

This replaces `gap_term_variant.py` as the selection instrument. That script compared three
weights directly against the two structured splits and the winner was read off -- which is
model selection on the exam, and is what §6.6 and §7.1 forbid. It survives as the record of
the diagnostic that motivated the term at all, and its numbers are development
observations.

Here the weight is chosen inside a three-way orbit-grouped split of each exam's **training**
mask alone: fit, stop, score. For cross-validation the selection is repeated per fold, which
is nested cross-validation and is the reason this costs what it costs -- a weight chosen once
on data that later appears in another fold's test set is leakage, cheaper and wrong.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold

import locations
from corpus import load
from models.branch_trunk import BranchTrunkOperator
from training import N_SPLITS, select_gap_weight

CANDIDATES = (0.0, 0.5, 2.0)


def main():
    corpus = load()

    def factory():
        return BranchTrunkOperator(latent=64, width=64)

    chosen: dict[str, float] = {}
    every: list[dict] = []

    print("== per-fold selection for grouped cross-validation (nested) ==", flush=True)
    for fold, (train, _) in enumerate(
            GroupKFold(n_splits=N_SPLITS).split(corpus.strains, groups=corpus.orbit)):
        mask = np.zeros(len(corpus), dtype=bool)
        mask[train] = True
        print(f"  fold {fold}", flush=True)
        best, records = select_gap_weight(corpus, factory, mask, CANDIDATES)
        chosen[f"cv_fold_{fold}"] = best
        every.extend(dict(exam=f"cv_fold_{fold}", **r) for r in records)

    print("\n== selection for the two structured splits ==", flush=True)
    for label, train_mask, _ in corpus.structured_splits():
        print(f"  {label}", flush=True)
        best, records = select_gap_weight(corpus, factory, train_mask, CANDIDATES)
        chosen[label] = best
        every.extend(dict(exam=label, **r) for r in records)

    results = locations.ensure_results()
    pd.DataFrame(every).to_csv(results / "weight_selection.csv", index=False)
    json.dump(chosen, open(results / "weight_selection.json", "w"), indent=1)

    print("\n== chosen ==")
    for exam, weight in chosen.items():
        print(f"  {exam:42s} gap_weight = {weight}")
    print(f"\nwrote weight_selection.csv / .json to {results}")


if __name__ == "__main__":
    main()
