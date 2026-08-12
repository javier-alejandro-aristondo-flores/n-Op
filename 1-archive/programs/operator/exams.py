"""The frozen exams, run once, for both architecture families.

§7.1 fixes three splits and §8 fixes what passing them means, both before any model was
trained. This runs them, and it is the only place that consults a test index.

**Both families run.** §4.4 requires the exams rather than the builder's taste to choose
between the branch-trunk operator and the spectral one, and until this file existed the
choice had been mine by default because only one family was built.

**Weights come from `weight_selection.json`**, chosen on inner folds inside each exam's own
training mask. The rule is stated in `training.choose`: minimize inner gap subject to the
inner field staying within 10% of the best any candidate reaches, because §8 requires both
metrics and a weight that buys the gap by wrecking the field fails the criterion it was
picked for.

**Disclosure, carried into the certificate.** Before that selection existed, three gap
weights were compared directly against these two structured splits and the winner read off.
That is model selection on the exam. It cannot be undone; it is recorded here and in the
certificate so a reader can discount these two numbers accordingly. The cross-validation
result is unaffected -- it was never used for selection.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

import locations
from baselines import (COEFFICIENTS, apply_stretch, equilibrium_gap_correction,
                       equilibrium_index, fit_stretch, gap_of, learned_stretch)
from conformal import calibrate, empirical_coverage, ensemble_mean, split_by_orbit
from corpus import load, truth_table
from equivariance import degeneracy_test, permutations_for, symmetrised_prediction
from evaluate import BAND_GROUPS, dos_residual, per_eigenvalue_table
from models.branch_trunk import BranchTrunkOperator
from models.spectral import SpectralOperator
from observables import complete_window, curves, residual_percent
from training import hse_field_from, on_split, out_of_fold

NOISE_FLOOR_MEV = 0.0105
SIGNIFICANCE_MEV = 20.0
ENSEMBLE = (0, 1, 2, 3, 4)

FAMILIES = {
    "branch-trunk": lambda: BranchTrunkOperator(latent=64, width=64),
    "spectral": lambda: SpectralOperator(channels=24, modes=2, layers=2),
}


def load_weights() -> dict:
    path = locations.RESULTS / "weight_selection.json"
    if not path.exists():
        raise SystemExit(
            f"no {path.name}. Run select_weight.py first -- the exam must not choose its "
            "own hyperparameter.")
    return json.load(open(path))


def main():
    import sys

    epochs = 60 if "--quick" in sys.argv else 300
    corpus = load()
    weights = load_weights()
    permutations = permutations_for(corpus)

    truth_field = corpus.referenced("hse")
    truth_gap = gap_of(truth_field, corpus.kfrac)
    pbe_field = corpus.referenced("pbe")
    pbe_gap = gap_of(pbe_field, corpus.kfrac)
    correction = corpus.correction()
    window = complete_window(
        truth_table().rename(columns={"pbe_complete_to": "complete_to"}))
    truth_curves = curves(truth_field, corpus.weights)
    top = corpus.top_quartile_mask()

    # -- the baselines the criteria name --------------------------------------
    per_shape = np.array([[fit_stretch(corpus, i)[k] for k in COEFFICIENTS]
                          for i in range(len(corpus))])
    equilibrium = np.array([fit_stretch(corpus, equilibrium_index(corpus))[k]
                            for k in COEFFICIENTS])
    baselines = {
        "B1 equilibrium stretch": gap_of(apply_stretch(pbe_field, equilibrium),
                                         corpus.kfrac),
        "B1gap equilibrium gap constant": pbe_gap + equilibrium_gap_correction(corpus),
        "B3 learned stretch": gap_of(
            apply_stretch(pbe_field, learned_stretch(corpus, per_shape)), corpus.kfrac),
    }
    baseline_fields = {
        "B1 equilibrium stretch": apply_stretch(pbe_field, equilibrium),
        "B3 learned stretch": apply_stretch(pbe_field, learned_stretch(corpus, per_shape)),
    }

    rows, split_rows, reports = [], [], {}

    for family, factory in FAMILIES.items():
        weight = weights.get("cv_fold_0", 0.0)
        print(f"\n=== {family}: grouped cross-validation "
              f"(gap_weight per fold from selection) ===", flush=True)

        predicted = np.full_like(correction, np.nan)
        for fold in range(5):
            fold_weight = weights.get(f"cv_fold_{fold}", weight)
            single, _ = out_of_fold(corpus, factory, n_splits=5, verbose=False,
                                    epochs=epochs, patience=30, gap_weight=fold_weight,
                                    only_fold=fold)
            mask = np.isfinite(single[:, 0, 0])
            predicted[mask] = single[mask]
            print(f"  fold {fold}: weight {fold_weight}", flush=True)

        field = hse_field_from(corpus, predicted)
        gap = gap_of(field, corpus.kfrac)
        full, complete = dos_residual(field, truth_field, corpus.weights, window)
        band_table = per_eigenvalue_table(predicted, correction, corpus.weights,
                                          truth_field)
        rows.append(dict(family=family, exam="grouped cross-validation",
                         gap_mev=np.abs(gap - truth_gap).mean() * 1000,
                         gap_top_quartile_mev=np.abs(gap - truth_gap)[top].mean() * 1000,
                         field_mev=float(band_table.iloc[0]["mae_mev"]),
                         dos_full_percent=full, dos_complete_percent=complete))
        band_table.insert(0, "family", family)
        reports[family] = band_table

        print(f"  gap {rows[-1]['gap_mev']:.1f} meV   field "
              f"{rows[-1]['field_mev']:.1f} meV   DOS {full:.2f}%", flush=True)

        # -- the two structured splits ---------------------------------------
        for label, train_mask, test_mask in corpus.structured_splits():
            fold_weight = weights.get(label, weight)
            prediction = on_split(corpus, factory, train_mask, test_mask,
                                  epochs=epochs, patience=30, gap_weight=fold_weight)
            test = np.where(test_mask)[0]
            split_field = hse_field_from(corpus, np.nan_to_num(prediction))[test]
            split_gap = np.abs(gap_of(split_field, corpus.kfrac)
                               - truth_gap[test]).mean() * 1000
            split_field_mae = np.abs(prediction[test] - correction[test]).mean() * 1000
            split_dos = float(residual_percent(curves(split_field, corpus.weights),
                                               truth_curves[test], window).mean())
            record = dict(family=family, split=label, gap_weight=fold_weight,
                          gap_mev=split_gap, field_mev=split_field_mae,
                          dos_percent=split_dos)
            for name, values in baselines.items():
                record[f"{name} gap_mev"] = np.abs(values[test]
                                                   - truth_gap[test]).mean() * 1000
            for name, values in baseline_fields.items():
                record[f"{name} field_mev"] = np.abs(
                    values[test] - truth_field[test]).mean() * 1000
            split_rows.append(record)
            print(f"  {label[:38]:38s} w={fold_weight:<4} gap {split_gap:7.1f}  "
                  f"field {split_field_mae:6.1f}  DOS {split_dos:5.2f}%", flush=True)

    results = locations.ensure_results()
    pd.DataFrame(rows).to_csv(results / "exam_cross_validation.csv", index=False)
    pd.DataFrame(split_rows).to_csv(results / "exam_structured_splits.csv", index=False)
    pd.concat(reports.values()).to_csv(results / "exam_band_groups.csv", index=False)

    # -- ensemble, conformal intervals, and the degeneracy test ---------------
    print("\n=== ensemble, conformal calibration, symmetry ===", flush=True)
    best_family = min(rows, key=lambda r: r["gap_mev"])["family"]
    factory = FAMILIES[best_family]
    print(f"  best on cross-validation: {best_family}", flush=True)

    fitting, calibration = split_by_orbit(corpus.orbit, np.arange(len(corpus)), 0.25)
    members = []
    for seed in ENSEMBLE:
        model = factory()
        model.seed = seed
        inner_fit, inner_stop = fitting[:int(0.8 * len(fitting))], \
            fitting[int(0.8 * len(fitting)):]
        model.train_on(corpus.strains, pbe_field, correction, corpus.kfrac,
                       corpus.weights, train_index=inner_fit,
                       validation_index=inner_stop, seed=seed, epochs=epochs,
                       patience=30, gap_weight=weights.get("cv_fold_0", 0.0))
        members.append(model)
        print(f"  ensemble member {seed} trained", flush=True)

    pooled = ensemble_mean([m.predict(corpus.strains, pbe_field) for m in members])
    pooled_field = hse_field_from(corpus, pooled)
    pooled_gap = gap_of(pooled_field, corpus.kfrac)

    interval = calibrate(np.abs(pooled_gap[calibration] - truth_gap[calibration]))
    coverage = empirical_coverage(pooled_gap[fitting], truth_gap[fitting], interval)
    print(f"  conformal half-width {interval.half_width * 1000:.1f} meV, "
          f"empirical coverage {coverage:.3f} (nominal 0.90, target 0.85-0.95)")

    symmetrised = symmetrised_prediction(members[0], corpus.strains, pbe_field,
                                         permutations)
    symmetrised_field = hse_field_from(corpus, symmetrised)
    degeneracy = degeneracy_test(symmetrised_field, corpus)
    raw_degeneracy = degeneracy_test(
        hse_field_from(corpus, members[0].predict(corpus.strains, pbe_field)), corpus)
    print(f"  Gamma degeneracy, symmetrised: {degeneracy['max_splitting_mev']:.3f} meV "
          f"(raw {raw_degeneracy['max_splitting_mev']:.3f}); "
          f"{'PASSES' if degeneracy['passes_1mev'] else 'FAILS'} the 1 meV test")

    json.dump(dict(best_family=best_family,
                   conformal_half_width_mev=interval.half_width * 1000,
                   conformal_coverage=coverage,
                   conformal_nominal=interval.nominal,
                   conformal_calibration_size=interval.calibration_size,
                   degeneracy_symmetrised=degeneracy, degeneracy_raw=raw_degeneracy,
                   ensemble_size=len(ENSEMBLE), epochs=epochs,
                   noise_floor_mev=NOISE_FLOOR_MEV,
                   significance_mev=SIGNIFICANCE_MEV,
                   weights_used=weights,
                   disclosure=("the two structured splits were compared at three gap "
                               "weights before the weight was reselected on inner folds; "
                               "their numbers are correspondingly optimistic")),
              open(results / "exam_summary.json", "w"), indent=1)
    np.savez_compressed(results / "exam_predictions.npz", pooled=pooled,
                        symmetrised=symmetrised)
    print(f"\nwrote exam tables to {results}")


if __name__ == "__main__":
    main()
