"""Gate 4, step 4b -- the DOS ladder under the structured splits.

Interpolation flattered one rung badly. A nearest-neighbor lookup reaches about 5% on
random folds, but this sweep is a dense grid, so a random fold almost always leaves a
near neighbor in the training set. That number says the grid is dense, not that the
curve is easy. The question an operator actually faces is what happens off the sampled
region, which is what these two splits ask:

* train on the small-strain half, test on the large-strain half;
* train on the axis and skew families, test on the 512-cell general-stretch family.

The second is the harder and more honest one: the general-stretch family is the only
place where all three normal strains vary independently, so a model trained without it
has never seen the cross-terms it must predict.
"""


import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor

from paths import RESULTS  # noqa: E402
from step3_ladder import features, m3b_features  # noqa: E402
from step4_dos import build_curves, residual_percent  # noqa: E402

OUT = str(RESULTS)


def main():
    data = np.load(f"{OUT}/spectra.npz")
    table = pd.read_csv(f"{OUT}/observables.csv").merge(
        pd.read_csv(f"{OUT}/step1_copies.csv"), on=["family", "point"])
    keep = ~table.is_copy.to_numpy()

    strains = data["strains"][keep]
    strain_norm = table.strain_norm.to_numpy()[keep]
    family = table.family.to_numpy()[keep]

    median = np.median(strain_norm)
    small = strain_norm <= median
    axis_and_skew = np.isin(family, [
        "2-stretch-one-axis-or-two-axes", "3-skew-one-plane",
        "4-skew-two-planes", "5-skew-three-planes"])
    general = family == "6-stretch-all-three-axes"

    splits = [("random half (interpolation control)", None, None),
              ("small strain -> large strain", small, ~small),
              ("axis+skew families -> general stretch", axis_and_skew, general)]

    for tag in ["pbe", "hse"]:
        curves = build_curves(data[f"energies_{tag}"][keep], data["weights"])
        print(f"\n== {tag.upper()} DOS residual (%) under structured splits ==")
        print(f"{'split':40s} {'n train':>8s} {'n test':>7s} "
              + "".join(f"{k:>9s}" for k in ["L0", "L0mean", "L1", "L2", "L3"]))
        rows = []
        for label, train, test in splits:
            if train is None:
                rng = np.random.default_rng(0)
                train = rng.random(len(strains)) < 0.5
                test = ~train
            equilibrium = curves[int(np.argmin(strain_norm))]
            predictions = {
                "L0": np.repeat(equilibrium[None], test.sum(), axis=0),
                "L0mean": np.repeat(curves[train].mean(axis=0)[None], test.sum(), axis=0),
            }
            for key, matrix in (("L1", features(strains, "M4")),
                                ("L2", m3b_features(strains))):
                model = Ridge(alpha=1e-4).fit(matrix[train], curves[train])
                predictions[key] = model.predict(matrix[test])
            knn = KNeighborsRegressor(n_neighbors=5, weights="distance")
            knn.fit(strains[train], curves[train])
            predictions["L3"] = knn.predict(strains[test])

            line = f"{label:40s} {int(train.sum()):8d} {int(test.sum()):7d} "
            row = {"functional": tag, "split": label}
            for key in ["L0", "L0mean", "L1", "L2", "L3"]:
                value = float(residual_percent(predictions[key], curves[test]).mean())
                row[key] = value
                line += f"{value:9.2f}"
            rows.append(row)
            print(line)
        pd.DataFrame(rows).to_csv(f"{OUT}/step4b_splits_{tag}.csv", index=False)


if __name__ == "__main__":
    main()
