"""Fitting the operator under the splits the exams will use, and never on the exams.

Two rules govern everything here.

**Grouping is by symmetry orbit, always.** Two shapes related by one of the 48 octahedral
operations are the same physical calculation seen twice, so letting one train while the
other tests is leakage of the purest kind -- the model sees the test point's exact answer.
`symmetry.py` explains why the labeler had to be corrected before this was true; with Gate
4's labeler the gradient-boosted baseline gained 34 meV it had not earned, and an operator
trained with 48-fold augmentation is far better placed to exploit the same hole.

**Early stopping reads an inner fold, never an outer one.** Each outer training set is split
again, by orbit, into a fitting part and a stopping part. The frozen exams are untouched
until the final one-shot evaluation. A model selected against the exam is a model whose
exam score means nothing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from sklearn.model_selection import GroupKFold

import locations  # noqa: F401  -- puts Gate 4's code on the import path
from corpus import Corpus, vbm_of

N_SPLITS = 5
INNER_SPLITS = 4
SEED = 0

#: A factory rather than an instance, so every fold trains a model from scratch. Reusing
#: one object across folds would carry fitted weights into a fold that must not see them.
ModelFactory = Callable[[], "object"]


@dataclass
class FoldResult:
    fold: int
    n_train: int
    n_test: int
    parameters: int
    epochs_run: int
    best_validation: float


def _inner_split(orbit: np.ndarray, index: np.ndarray, seed: int
                 ) -> tuple[np.ndarray, np.ndarray]:
    """Carve a stopping fold out of a training fold, keeping orbits whole."""
    groups = orbit[index]
    splitter = GroupKFold(n_splits=INNER_SPLITS)
    fitting, stopping = next(iter(splitter.split(index, groups=groups)))
    return index[fitting], index[stopping]


def _three_way_inner(orbit: np.ndarray, index: np.ndarray
                     ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Fit / stop / score, all inside a training set, all orbit-whole.

    Three rather than two because early stopping and hyperparameter selection are separate
    decisions: scoring a weight on the same fold that chose when to stop would let the
    stopping rule flatter the weight. Both stay strictly inside the training mask, so no
    test index is ever consulted.
    """
    groups = orbit[index]
    folds = list(GroupKFold(n_splits=5).split(index, groups=groups))
    # GroupKFold is deterministic and unshuffled; the last two folds become stop and score.
    stopping = folds[3][1]
    scoring = folds[4][1]
    held = np.concatenate([stopping, scoring])
    fitting = np.setdiff1d(np.arange(len(index)), held)
    return index[fitting], index[stopping], index[scoring]


def choose(records: list[dict], baseline_field_mev: float,
           baseline_gap_mev: float) -> float:
    """The selection rule, applied to inner-fold scores only.

    §8 requires the per-eigenvalue MAE **and** the indirect-gap MAE each to beat their
    baseline by at least 20%. So the quantity to maximize is the **margin on whichever of
    the two is closest to failing** -- a maximin. That is not a taste; it is the direct
    reading of a criterion with two conjunctive clauses.

    This rule was arrived at by discarding two worse ones, and the discards are worth
    recording because each failed in an instructive way:

    * *Minimize the gap.* Picks weight 2.0, whose inner gap is best -- and whose field error
      is 62 meV against weight 0.5's 47, with the density-of-states residual going 3.2% to
      11.2%. It optimizes one clause of a two-clause criterion.
    * *Minimize the gap subject to the field staying within 10% of the best.* The 10% was
      mine, not the spec's, and it was brittle exactly where it mattered: two folds fell a
      hair outside it and flipped to weight 0.0, tripling their inner gap error on the
      strength of a constant nobody had justified.
    * *Minimize the gap among candidates that pass §8 on the field.* Better, because the
      threshold is the spec's -- but it takes the **worst** admissible field by construction,
      so a selection-time field estimate that is slightly optimistic hands the exam a model
      that fails.

    Maximin has none of those failure modes: it is scale-free, uses only the spec's own
    thresholds, and picks the candidate furthest from failing anything. Measured this way
    weight 0.0 scores **negative** on every exam -- without the auxiliary term the operator
    does not beat the gap baseline at all -- and the choice is 0.5 on cross-validation and
    2.0 on the two extrapolation splits, where the gap is the binding clause.
    """
    def margin(record: dict) -> float:
        return min(1.0 - record["inner_gap_mev"] / baseline_gap_mev,
                   1.0 - record["inner_field_mev"] / baseline_field_mev)

    return max(records, key=margin)["gap_weight"]


def select_gap_weight(corpus: Corpus, factory: ModelFactory, train_mask: np.ndarray,
                      candidates=(0.0, 0.5, 2.0), *, seed: int = SEED,
                      epochs: int = 120, verbose: bool = True, **options
                      ) -> tuple[float, list[dict]]:
    """Choose the auxiliary gap weight using only the training side of an exam.

    §6.2 permits an auxiliary derived-observable term provided its inclusion is justified by
    **inner-fold** improvement rather than by test behavior. An earlier diagnostic run
    compared three weights directly against the two structured splits and read off the
    winner; that was model selection on the exam, and this function is what replaces it.

    Fewer epochs than a final fit: selection only has to *rank* the candidates, and ranking
    stabilizes well before convergence. The chosen weight is refitted at full length.

    Scored on the indirect gap, because that is what the term targets. The field error is
    logged alongside so that a weight buying the gap at the field's expense is visible
    rather than hidden.
    """
    from baselines import gap_of

    pbe = corpus.referenced("pbe")
    truth = corpus.correction()
    fitting, stopping, scoring = _three_way_inner(corpus.orbit,
                                                  np.where(train_mask)[0])

    # The baseline the admissibility test measures against: the equilibrium stretch, on
    # this exam's own inner-scoring shapes. Cheap -- no training -- and it replaces the
    # invented budget with the threshold §8 actually applies.
    from baselines import (COEFFICIENTS, apply_stretch, equilibrium_gap_correction,
                           equilibrium_index, fit_stretch)

    equilibrium = np.array([fit_stretch(corpus, equilibrium_index(corpus))[k]
                            for k in COEFFICIENTS])
    baseline_field = float(np.abs(apply_stretch(pbe[scoring], equilibrium)
                                  - corpus.referenced("hse")[scoring]).mean()) * 1000

    truth_gap = gap_of(corpus.referenced("hse")[scoring], corpus.kfrac)
    baseline_gap = float(np.abs(
        gap_of(pbe[scoring], corpus.kfrac) + equilibrium_gap_correction(corpus)
        - truth_gap).mean()) * 1000
    records = []
    for weight in candidates:
        model = factory()
        model.train_on(corpus.strains, pbe, truth, corpus.kfrac, corpus.weights,
                       train_index=fitting, validation_index=stopping, seed=seed,
                       epochs=epochs, gap_weight=weight, **options)
        prediction = model.predict(corpus.strains[scoring], pbe[scoring])
        field_mae = float(np.abs(prediction - truth[scoring]).mean()) * 1000
        predicted = hse_field_from_rows(pbe[scoring], prediction)
        gap_mae = float(np.abs(gap_of(predicted, corpus.kfrac) - truth_gap).mean()) * 1000
        records.append(dict(gap_weight=weight, inner_gap_mev=gap_mae,
                            inner_field_mev=field_mae,
                            baseline_field_mev=baseline_field,
                            baseline_gap_mev=baseline_gap))
        if verbose:
            print(f"    weight {weight:4.2f}  inner gap {gap_mae:7.2f} meV  "
                  f"inner field {field_mae:6.2f} meV", flush=True)

    best = choose(records, baseline_field, baseline_gap)
    if verbose:
        print(f"    selected gap_weight = {best} on {len(scoring)} inner-scoring shapes",
              flush=True)
    return best, records


def hse_field_from_rows(pbe_rows: np.ndarray, correction: np.ndarray) -> np.ndarray:
    """PBE plus a predicted correction for a subset of rows, re-referenced."""
    field = pbe_rows + correction
    return field - vbm_of(field)[:, None, None]


def out_of_fold(corpus: Corpus, factory: ModelFactory, *, target: str = "correction",
                n_splits: int = N_SPLITS, seed: int = SEED, verbose: bool = True,
                only_fold: int | None = None,
                **options) -> tuple[np.ndarray, list[FoldResult]]:
    """Orbit-grouped out-of-fold predictions of the residual field.

    Every shape is predicted by a model that saw neither it nor any of its symmetry
    images. Returns the predicted correction field, shape (n, n_k, n_band).
    """
    pbe = corpus.referenced("pbe")
    truth = corpus.correction() if target == "correction" else corpus.referenced("hse")

    prediction = np.full_like(truth, np.nan)
    results: list[FoldResult] = []

    splitter = GroupKFold(n_splits=n_splits)
    for fold, (train, test) in enumerate(splitter.split(corpus.strains,
                                                        groups=corpus.orbit)):
        # `only_fold` lets the caller run one fold at a time, which is what per-fold
        # hyperparameter selection needs: each fold has its own weight, chosen inside its
        # own training mask, and running them together would force one weight on all five.
        if only_fold is not None and fold != only_fold:
            continue
        fitting, stopping = _inner_split(corpus.orbit, train, seed)
        model = factory()
        report = model.train_on(corpus.strains, pbe, truth, corpus.kfrac, corpus.weights,
                                train_index=fitting, validation_index=stopping,
                                seed=seed, **options)
        prediction[test] = model.predict(corpus.strains[test], pbe[test])
        results.append(FoldResult(fold=fold, n_train=len(fitting), n_test=len(test),
                                  parameters=model.parameters,
                                  epochs_run=report.epochs_run,
                                  best_validation=report.best_validation))
        if verbose:
            print(f"  fold {fold}: fit {len(fitting):4d}  stop {len(stopping):4d}  "
                  f"test {len(test):4d}  epochs {report.epochs_run:4d}  "
                  f"inner {report.best_validation * 1000:7.2f} meV", flush=True)

    if only_fold is None:
        assert np.isfinite(prediction).all(), "a shape was never predicted"
    return prediction, results


def on_split(corpus: Corpus, factory: ModelFactory, train_mask: np.ndarray,
             test_mask: np.ndarray, *, target: str = "correction", seed: int = SEED,
             **options) -> np.ndarray:
    """Train on one mask, predict on another. For the two structured exams.

    The stopping fold comes out of the training mask, so the test side stays unseen --
    which is the whole point of an extrapolation split.
    """
    pbe = corpus.referenced("pbe")
    truth = corpus.correction() if target == "correction" else corpus.referenced("hse")

    train = np.where(train_mask)[0]
    fitting, stopping = _inner_split(corpus.orbit, train, seed)
    model = factory()
    model.train_on(corpus.strains, pbe, truth, corpus.kfrac, corpus.weights,
                   train_index=fitting, validation_index=stopping, seed=seed, **options)

    test = np.where(test_mask)[0]
    prediction = np.full_like(truth, np.nan)
    prediction[test] = model.predict(corpus.strains[test], pbe[test])
    return prediction


def hse_field_from(corpus: Corpus, correction: np.ndarray) -> np.ndarray:
    """The shipped HSE prediction: PBE plus the predicted correction, re-referenced.

    Re-referencing matters. The correction shifts the whole spectrum, so the valence
    maximum of the sum is not at zero, and every observable is defined against the field's
    own maximum.
    """
    field = corpus.referenced("pbe") + correction
    return field - vbm_of(field)[:, None, None]
