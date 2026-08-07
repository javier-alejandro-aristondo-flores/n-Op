"""A logged variant: does an auxiliary gap term close the gap deficit?

The shipped configuration has no gap term. This script exists to answer a diagnostic
question the main result raises and cannot settle on its own: **is Mode 1's gap deficit a
consequence of the loss, or of the model?**

The primary loss is a k-weighted mean over 1,376 states per shape. The indirect gap is two
of them -- the extremal valence and conduction states -- so a field-averaged loss barely
weights the quantity the acceptance criterion measures. That is not speculation: the
per-shape two-branch stretch fitted *directly on the answer* leaves 127 meV of gap error
while a single scalar constant leaves 47.5, which is the same effect in a model with no
learning in it at all.

**This is permitted and it is not the prohibited thing.** §6.2 allows auxiliary
derived-observable losses provided every weight is logged and justified by inner-fold
improvement rather than test behavior. §6.4 prohibits something else -- up-weighting the
gap *region of the energy window* inside the per-eigenvalue loss -- on the argument that
doing so optimizes the exam. A term on the derived observable is a different mechanism.

Reported either way. If the gap term closes the deficit, the deficit was a loss-design
choice; if it does not, the deficit is the model's and the scalar-gap claim is dead.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import locations
from baselines import equilibrium_gap_correction, gap_of
from corpus import load, truth_table
from models.branch_trunk import BranchTrunkOperator
from observables import complete_window, curves, residual_percent
from training import hse_field_from, on_split

WEIGHTS = (0.0, 1.0, 5.0)
EPOCHS = 300


def main():
    corpus = load()
    truth_field = corpus.referenced("hse")
    truth_gap = gap_of(truth_field, corpus.kfrac)
    pbe_gap = gap_of(corpus.referenced("pbe"), corpus.kfrac)
    reference_gap = pbe_gap + equilibrium_gap_correction(corpus)
    window = complete_window(
        truth_table().rename(columns={"pbe_complete_to": "complete_to"}))
    truth_curves = curves(truth_field, corpus.weights)

    rows = []
    for label, train_mask, test_mask in corpus.structured_splits():
        test = np.where(test_mask)[0]
        baseline = np.abs(reference_gap[test] - truth_gap[test]).mean() * 1000
        for weight in WEIGHTS:
            correction = on_split(
                corpus, lambda: BranchTrunkOperator(latent=64, width=64),
                train_mask, test_mask, epochs=EPOCHS, patience=30, gap_weight=weight)
            field = hse_field_from(corpus, np.nan_to_num(correction))[test]
            gap_error = np.abs(gap_of(field, corpus.kfrac) - truth_gap[test]).mean() * 1000
            dos = float(residual_percent(curves(field, corpus.weights),
                                         truth_curves[test], window).mean())
            rows.append(dict(split=label, gap_weight=weight, gap_mev=gap_error,
                             b1gap_mev=baseline, dos_percent=dos))
            print(f"  {label[:38]:38s} w={weight:4.1f}  gap {gap_error:7.1f} meV  "
                  f"(B1gap {baseline:6.1f})   DOS {dos:5.2f}%", flush=True)

    table = pd.DataFrame(rows)
    table.to_csv(locations.ensure_results() / "gap_term_variant.csv", index=False)
    print("\nwrote gap_term_variant.csv")


if __name__ == "__main__":
    main()
