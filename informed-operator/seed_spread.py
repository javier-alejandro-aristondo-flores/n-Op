"""How much of a reported number is the seed?

A residual means nothing until the instrument's own scatter is known -- the discipline Gate
4 applied when it measured a noise floor from symmetry twins before trusting any model
error. The same question applies to a trained model, and here it had a concrete answer that
was not being measured: the identical Mode 1 configuration scored **93.8 meV** as the sixth
model built in one script and **85.0 meV** as the first in another, because initialization
happened before the seed was set. That defect is fixed. This measures what remains.

Run on the **two structured splits**, not on cross-validation, because those are the runs
§8 gates acceptance on, and scatter should be measured where the decision is made. Five
seeds each.

Everything downstream quotes single-run numbers beside this spread. A model that beats a
threshold by less than its own seed scatter has not beaten it.
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

SEEDS = (0, 1, 2, 3, 4)
EPOCHS = 300


def main():
    import sys

    weight = float(sys.argv[sys.argv.index("--weight") + 1]) if "--weight" in sys.argv \
        else 0.0
    corpus = load()
    truth_field = corpus.referenced("hse")
    truth_gap = gap_of(truth_field, corpus.kfrac)
    reference = gap_of(corpus.referenced("pbe"), corpus.kfrac) \
        + equilibrium_gap_correction(corpus)
    window = complete_window(
        truth_table().rename(columns={"pbe_complete_to": "complete_to"}))
    truth_curves = curves(truth_field, corpus.weights)

    print(f"seed scatter at gap_weight = {weight}, {len(SEEDS)} seeds per split\n",
          flush=True)
    rows = []
    for label, train_mask, test_mask in corpus.structured_splits():
        test = np.where(test_mask)[0]
        baseline = float(np.abs(reference[test] - truth_gap[test]).mean()) * 1000
        for seed in SEEDS:
            correction = on_split(
                corpus, lambda: BranchTrunkOperator(latent=64, width=64),
                train_mask, test_mask, seed=seed, epochs=EPOCHS, patience=30,
                gap_weight=weight)
            field = hse_field_from(corpus, np.nan_to_num(correction))[test]
            gap = float(np.abs(gap_of(field, corpus.kfrac)
                               - truth_gap[test]).mean()) * 1000
            dos = float(residual_percent(curves(field, corpus.weights),
                                         truth_curves[test], window).mean())
            rows.append(dict(split=label, seed=seed, gap_mev=gap, dos_percent=dos,
                             b1gap_mev=baseline))
            print(f"  {label[:38]:38s} seed {seed}  gap {gap:7.2f} meV  "
                  f"DOS {dos:5.2f}%", flush=True)

    table = pd.DataFrame(rows)
    print("\n== scatter ==")
    print(f"{'split':40s} {'gap mean':>10s} {'gap sd':>8s} {'range':>8s} "
          f"{'DOS mean':>9s} {'DOS sd':>7s} {'B1gap':>8s}")
    summary = []
    for label, group in table.groupby("split", sort=False):
        gap, dos = group.gap_mev, group.dos_percent
        summary.append(dict(split=label, gap_mean=gap.mean(), gap_sd=gap.std(ddof=1),
                            gap_range=gap.max() - gap.min(), dos_mean=dos.mean(),
                            dos_sd=dos.std(ddof=1),
                            b1gap=group.b1gap_mev.iloc[0]))
        print(f"{label:40s} {gap.mean():10.2f} {gap.std(ddof=1):8.2f} "
              f"{gap.max() - gap.min():8.2f} {dos.mean():9.2f} {dos.std(ddof=1):7.2f} "
              f"{group.b1gap_mev.iloc[0]:8.1f}")

    results = locations.ensure_results()
    table.to_csv(results / f"seed_spread_w{weight:g}.csv", index=False)
    pd.DataFrame(summary).to_csv(results / f"seed_spread_summary_w{weight:g}.csv",
                                 index=False)
    print(f"\nwrote seed_spread_w{weight:g}.csv")


if __name__ == "__main__":
    main()
