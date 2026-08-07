"""Mode 1 against the ladder, on the splits that decide.

What is measured, and against what:

* **per-eigenvalue MAE**, k-weighted, reported by band group -- not by band index, because
  the sorted-eigenvalue representation swaps labels at crossings and an index is not a
  stable identity across shapes;
* **indirect-gap MAE**, extracted from the predicted field by the *same* mesh-minimum
  procedure used on ground truth, so model and truth are compared like for like and the
  argmin-hopping artifact lands on both equally;
* **density-of-states residual**, integrated absolute difference as a percentage of the
  curve's integral, on the full window and the provably-complete sub-window.

Every number sits beside the baseline it must beat and beside the measured noise floor:
0.0105 meV rms on the gap, 20 meV operative significance. A residual below 20 meV is
reported as at or below the floor rather than as an achievement.

This module runs **cross-validation and the two structured splits**. It is not the frozen
one-shot exam; it is the development instrument that the exam will later be run once
against, and it reads only inner folds for stopping.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

import locations
from baselines import (COEFFICIENTS, apply_stretch, equilibrium_gap_correction,
                       equilibrium_index, fit_stretch, gap_of, learned_stretch)
from corpus import load, truth_table
from models.branch_trunk import BranchTrunkOperator
from observables import GRID, complete_window, curves, residual_percent
from training import hse_field_from, on_split, out_of_fold

#: Gate 4's measured floors, carried so no residual is reported without one.
NOISE_FLOOR_MEV = 0.0105
SIGNIFICANCE_MEV = 20.0

BAND_GROUPS = (
    ("deep valence", lambda e: e < -10.0),
    ("valence edge", lambda e: (e >= -10.0) & (e < 0.5)),
    ("conduction edge", lambda e: (e >= 0.5) & (e < 7.0)),
    ("high conduction", lambda e: e >= 7.0),
)


def per_eigenvalue_table(predicted: np.ndarray, truth: np.ndarray, weights: np.ndarray,
                         energies: np.ndarray) -> pd.DataFrame:
    """k-weighted absolute error by band group, in meV.

    Groups are energy windows on the *eigenvalue*, `energies`, not on the correction being
    predicted -- a state is "deep valence" because of where it sits in the spectrum, not
    because of how large its correction is. Grouping by band *index* would be worse still:
    the sorted representation swaps labels at crossings, so index is not a stable identity
    across shapes.
    """
    error = np.abs(predicted - truth)
    weight = np.broadcast_to(weights[None, :, None], error.shape)
    rows = [dict(group="all", mae_mev=1000 * np.average(error, weights=weight),
                 share_of_states=1.0)]
    for name, predicate in BAND_GROUPS:
        mask = predicate(energies)
        if mask.sum() == 0:
            continue
        rows.append(dict(group=name,
                         mae_mev=1000 * np.average(error[mask], weights=weight[mask]),
                         share_of_states=float(mask.mean())))
    return pd.DataFrame(rows)


def dos_residual(predicted_field: np.ndarray, truth_field: np.ndarray,
                 weights: np.ndarray, window: np.ndarray) -> tuple[float, float]:
    predicted = curves(predicted_field, weights)
    truth = curves(truth_field, weights)
    return (float(residual_percent(predicted, truth).mean()),
            float(residual_percent(predicted, truth, window).mean()))


def main():
    import sys

    quick = "--quick" in sys.argv
    options = dict(epochs=20, patience=20) if quick else dict(epochs=300, patience=30)

    corpus = load()
    truth_field = corpus.referenced("hse")
    truth_gap = gap_of(truth_field, corpus.kfrac)
    truth = corpus.correction()
    window = complete_window(
        truth_table().rename(columns={"pbe_complete_to": "complete_to"}))
    top = corpus.top_quartile_mask()

    def factory():
        return BranchTrunkOperator(latent=64, width=64)

    print("== Mode 1, orbit-grouped cross-validation ==", flush=True)
    predicted_correction, folds = out_of_fold(corpus, factory, **options)
    predicted_field = hse_field_from(corpus, predicted_correction)
    predicted_gap = gap_of(predicted_field, corpus.kfrac)

    print("\nper-eigenvalue error by band group (k-weighted, meV)")
    print(per_eigenvalue_table(predicted_correction, truth, corpus.weights,
                               truth_field)
          .to_string(index=False, float_format=lambda v: f"{v:9.3f}"))

    # -- the gap, against every baseline ------------------------------------
    pbe_field = corpus.referenced("pbe")
    pbe_gap = gap_of(pbe_field, corpus.kfrac)
    per_shape = np.array([[fit_stretch(corpus, i)[k] for k in COEFFICIENTS]
                          for i in range(len(corpus))])
    ladder = {
        "B0 identity": pbe_gap,
        "B1 equilibrium stretch": gap_of(
            apply_stretch(pbe_field, np.array(
                [fit_stretch(corpus, equilibrium_index(corpus))[k]
                 for k in COEFFICIENTS])), corpus.kfrac),
        "B1gap equilibrium gap constant": pbe_gap + equilibrium_gap_correction(corpus),
        "B2 per-shape stretch (sees answer)": gap_of(
            apply_stretch(pbe_field, per_shape), corpus.kfrac),
        "B3 learned stretch": gap_of(
            apply_stretch(pbe_field, learned_stretch(corpus, per_shape)), corpus.kfrac),
        "operator (Mode 1)": predicted_gap,
    }

    print("\nindirect-gap MAE, meV  (noise floor 0.0105 meV, significance 20 meV)")
    print(f"{'model':38s} {'all':>10s} {'top quartile':>14s} {'worst':>10s}")
    gap_rows = []
    for label, values in ladder.items():
        error = np.abs(values - truth_gap) * 1000
        gap_rows.append(dict(model=label, mae_mev=error.mean(),
                             top_quartile_mev=error[top].mean(), worst_mev=error.max()))
        print(f"{label:38s} {error.mean():10.1f} {error[top].mean():14.1f} "
              f"{error.max():10.1f}")

    full, complete = dos_residual(predicted_field, truth_field, corpus.weights, window)
    print(f"\ndensity-of-states residual   full window {full:.2f}%   "
          f"complete sub-window {complete:.2f}%")

    # -- the two structured splits ------------------------------------------
    print("\n== the structured splits ==", flush=True)
    split_rows = []
    for label, train_mask, test_mask in corpus.structured_splits():
        correction = on_split(corpus, factory, train_mask, test_mask, **options)
        test = np.where(test_mask)[0]
        field = hse_field_from(corpus, np.nan_to_num(correction))
        gap_error = np.abs(gap_of(field[test], corpus.kfrac) - truth_gap[test]) * 1000
        reference = np.abs(ladder["B1gap equilibrium gap constant"][test]
                           - truth_gap[test]) * 1000
        full_split, complete_split = dos_residual(
            field[test], truth_field[test], corpus.weights, window)
        split_rows.append(dict(split=label, operator_gap_mev=gap_error.mean(),
                               b1gap_mev=reference.mean(),
                               relative_improvement=1 - gap_error.mean() / reference.mean(),
                               dos_full_percent=full_split,
                               dos_complete_percent=complete_split))
        print(f"  {label:40s} operator {gap_error.mean():7.1f} meV   "
              f"B1gap {reference.mean():7.1f} meV   "
              f"DOS {full_split:5.2f}%", flush=True)

    results = locations.ensure_results()
    pd.DataFrame(gap_rows).to_csv(results / "mode1_gap_ladder.csv", index=False)
    pd.DataFrame(split_rows).to_csv(results / "mode1_structured_splits.csv", index=False)
    per_eigenvalue_table(predicted_correction, truth, corpus.weights,
                         truth_field).to_csv(
        results / "mode1_band_groups.csv", index=False)
    json.dump(dict(dos_full_percent=full, dos_complete_percent=complete,
                   parameters=folds[0].parameters,
                   epochs=[f.epochs_run for f in folds],
                   noise_floor_mev=NOISE_FLOOR_MEV,
                   significance_mev=SIGNIFICANCE_MEV, quick=quick),
              open(results / "mode1_summary.json", "w"), indent=1)
    np.savez_compressed(results / "mode1_predictions.npz",
                        correction=predicted_correction)
    print(f"\nwrote Mode 1 tables to {results}")


if __name__ == "__main__":
    main()
