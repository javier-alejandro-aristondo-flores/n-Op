"""Gate 4, step 3 -- the scalar model ladder.

The cheap baseline here is not linear regression. Diamond's valence maximum is a
threefold-degenerate Gamma25' state and its conduction minimum is six equivalent Delta
valleys; under strain the triplet splits and the valleys move apart, so the gap is a
`min` over valleys minus a `max` over a 3x3 eigenvalue problem. That is piecewise-linear
and nonanalytic at zero strain, and a naive linear fit fails on shear cells for reasons
that were understood in the 1950s. M2 below is that theory, fitted properly. It is the
model to beat, and anything that only beats M1 has beaten nothing.

Cross-validation groups by **symmetry orbit**. Two shapes related by an octahedral
operation carry identical spectra, so splitting them across folds lets the model see a
test point's exact image during training. Gate 3 was burned by exactly this and found
grouped CV uniformly harsher; the same correction is applied here from the start.
"""

import itertools
import json

import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold, KFold

from paths import RESULTS  # noqa: E402
from step1_noise import orbit_labels  # noqa: E402

OUT = str(RESULTS)

N_SPLITS = 5
SEED = 0


def tensors(strains: np.ndarray) -> np.ndarray:
    """Voigt (engineering shear) -> strain tensors, shape (n, 3, 3)."""
    e = strains
    out = np.zeros((len(e), 3, 3))
    out[:, 0, 0], out[:, 1, 1], out[:, 2, 2] = e[:, 0], e[:, 1], e[:, 2]
    out[:, 1, 2] = out[:, 2, 1] = e[:, 3] / 2
    out[:, 0, 2] = out[:, 2, 0] = e[:, 4] / 2
    out[:, 0, 1] = out[:, 1, 0] = e[:, 5] / 2
    return out


# ---------------------------------------------------------------------------
# M2 -- deformation-potential theory with degeneracy splitting
# ---------------------------------------------------------------------------

def valence_matrix(eps: np.ndarray, beta: float, n: float) -> np.ndarray:
    """Bir-Pikus matrix for the Gamma25' triplet, hydrostatic part removed.

    Only the difference `l - m` and the shear potential `n` split the triplet; the
    combination that shifts it bodily is degenerate with the conduction hydrostatic
    term and is carried there instead, so nothing is double-counted.
    """
    out = np.zeros_like(eps)
    for i in range(3):
        out[:, i, i] = beta * eps[:, i, i]
    out[:, 0, 1] = out[:, 1, 0] = n * eps[:, 0, 1]
    out[:, 0, 2] = out[:, 2, 0] = n * eps[:, 0, 2]
    out[:, 1, 2] = out[:, 2, 1] = n * eps[:, 1, 2]
    return out


def m2_indirect(params, eps, trace):
    gap0, hydrostatic, xi_u, beta, n = params
    valleys = xi_u * np.stack([eps[:, i, i] for i in range(3)], axis=1)
    conduction = hydrostatic * trace + valleys.min(axis=1)
    valence = np.linalg.eigvalsh(valence_matrix(eps, beta, n))[:, -1]
    return gap0 + conduction - valence


def m2_direct(params, eps, trace):
    gap0, hydrostatic, beta_v, n_v, beta_c, n_c = params
    valence = np.linalg.eigvalsh(valence_matrix(eps, beta_v, n_v))[:, -1]
    conduction = np.linalg.eigvalsh(valence_matrix(eps, beta_c, n_c))[:, 0]
    return gap0 + hydrostatic * trace + conduction - valence


def m2_splitting(params, eps, trace):
    beta, n = params
    levels = np.linalg.eigvalsh(valence_matrix(eps, beta, n))
    return levels[:, -1] - levels[:, 0]


M2_MODELS = {
    "indirect_gap": (m2_indirect, [4.2, -5.0, 8.0, -2.0, -3.0]),
    "direct_gap_gamma": (m2_direct, [5.6, -8.0, -2.0, -3.0, 1.0, 1.0]),
    "valence_splitting_total": (m2_splitting, [-2.0, -3.0]),
}


def fit_m2(name, strains, target):
    model, seed = M2_MODELS[name]
    eps = tensors(strains)
    trace = strains[:, :3].sum(axis=1)

    def residual(p):
        return model(p, eps, trace) - target

    result = least_squares(residual, seed, method="lm", max_nfev=200000)
    return result.x, model


# ---------------------------------------------------------------------------
# Feature bases for the linear tiers
# ---------------------------------------------------------------------------

def features(strains: np.ndarray, kind: str) -> np.ndarray:
    trace = strains[:, :3].sum(axis=1)[:, None]
    if kind == "M1":
        return trace
    if kind == "M3":
        quadratic = np.stack([strains[:, i] * strains[:, j]
                              for i, j in itertools.combinations_with_replacement(range(6), 2)],
                             axis=1)
        return np.hstack([strains, quadratic])
    if kind == "M4":
        return strains
    raise ValueError(kind)


def m3b_features(strains: np.ndarray) -> np.ndarray:
    """Strain invariants to second order -- the closed-form step above M2.

    Not a generic quadratic: only combinations invariant under the cubic group can appear
    in an energy, so this basis has the symmetry built in and costs far fewer parameters
    than M3's 27.
    """
    eps = tensors(strains)
    trace = np.trace(eps, axis1=1, axis2=2)
    second = np.einsum("nij,nji->n", eps, eps)
    third = np.einsum("nij,njk,nki->n", eps, eps, eps)
    cubic_anisotropy = (eps[:, 0, 0] ** 2 + eps[:, 1, 1] ** 2 + eps[:, 2, 2] ** 2)
    shear_square = (eps[:, 0, 1] ** 2 + eps[:, 0, 2] ** 2 + eps[:, 1, 2] ** 2)
    return np.stack([trace, trace ** 2, second, third, cubic_anisotropy, shear_square,
                     trace * cubic_anisotropy, trace * shear_square], axis=1)


# ---------------------------------------------------------------------------

def evaluate(name, strains, target, groups, splitter):
    """Out-of-fold predictions for every rung, on identical folds."""
    predictions = {key: np.full(len(target), np.nan)
                   for key in ["M0", "M1", "M2", "M3b", "M3", "M4"]}

    for train, test in splitter:
        y = target[train]
        predictions["M0"][test] = np.median(y)

        for key, matrix in (("M1", features(strains, "M1")),
                            ("M3", features(strains, "M3")),
                            ("M3b", m3b_features(strains))):
            model = Ridge(alpha=1e-8).fit(matrix[train], y)
            predictions[key][test] = model.predict(matrix[test])

        params, model = fit_m2(name, strains[train], y)
        predictions["M2"][test] = model(params, tensors(strains[test]),
                                        strains[test, :3].sum(axis=1))

        forest = HistGradientBoostingRegressor(
            max_iter=500, learning_rate=0.05, random_state=SEED)
        forest.fit(strains[train], y)
        predictions["M4"][test] = forest.predict(strains[test])

    return predictions


def main():
    table = pd.read_csv(f"{OUT}/observables.csv")
    copies = pd.read_csv(f"{OUT}/step1_copies.csv")
    table = table.merge(copies, on=["family", "point"])
    table = table[~table.is_copy].reset_index(drop=True)
    print(f"points after de-duplication: {len(table)}")

    strains = table[["e1", "e2", "e3", "e4", "e5", "e6"]].to_numpy()
    orbit = orbit_labels(strains)
    print(f"symmetry orbits: {len(set(orbit))}")

    noise = pd.read_csv(f"{OUT}/step1_noise.csv")
    results = {}
    quartile = np.quantile(table.strain_norm, 0.75)
    print(f"top-quartile strain threshold: ||E|| > {quartile:.4f}")
    top = table.strain_norm.to_numpy() > quartile

    for tag in ["pbe", "hse"]:
        for name in ["indirect_gap", "direct_gap_gamma", "valence_splitting_total"]:
            column = f"{tag}_{name}"
            target = table[column].to_numpy()

            grouped = list(GroupKFold(n_splits=N_SPLITS).split(strains, target, orbit))
            plain = list(KFold(n_splits=N_SPLITS, shuffle=True,
                               random_state=SEED).split(strains))

            for scheme, splitter in (("grouped", grouped), ("plain", plain)):
                predictions = evaluate(name, strains, target, orbit, splitter)
                for key, values in predictions.items():
                    error = np.abs(values - target)
                    results[(tag, name, scheme, key)] = dict(
                        mae=float(error.mean()),
                        mae_top_quartile=float(error[top].mean()),
                        max_error=float(error.max()),
                    )
            print(f"  done {column}", flush=True)

    rows = []
    for (tag, name, scheme, model), value in results.items():
        rows.append(dict(functional=tag.upper(), observable=name, cv=scheme,
                         model=model, **value))
    frame = pd.DataFrame(rows)
    frame.to_csv(f"{OUT}/step3_ladder.csv", index=False)

    for tag in ["pbe", "hse"]:
        for name in ["indirect_gap", "direct_gap_gamma", "valence_splitting_total"]:
            sub = frame[(frame.functional == tag.upper()) & (frame.observable == name)
                        & (frame.cv == "grouped")]
            print(f"\n{tag.upper()} {name} -- grouped CV, MAE in meV")
            print(f"{'model':6s} {'all':>10s} {'top quartile':>14s} {'worst':>10s}")
            for _, row in sub.iterrows():
                print(f"{row.model:6s} {row.mae * 1000:10.2f} "
                      f"{row.mae_top_quartile * 1000:14.2f} {row.max_error * 1000:10.2f}")

    # residual against strain magnitude, the headline plot's numbers
    print("\nM2 and M4 residual against strain magnitude (PBE indirect gap, grouped CV)")
    target = table["pbe_indirect_gap"].to_numpy()
    grouped = list(GroupKFold(n_splits=N_SPLITS).split(strains, target, orbit))
    predictions = evaluate("indirect_gap", strains, target, orbit, grouped)
    bins = [0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.15]
    print(f"{'||E|| bin':>14s} {'n':>5s} " + " ".join(f"{k:>9s}" for k in predictions))
    binned = []
    for low, high in zip(bins[:-1], bins[1:]):
        mask = (table.strain_norm >= low) & (table.strain_norm < high)
        if mask.sum() == 0:
            continue
        row = {"bin": f"{low:.2f}-{high:.2f}", "n": int(mask.sum())}
        line = f"{low:.2f}-{high:.2f}".rjust(14) + f" {int(mask.sum()):5d} "
        for key, values in predictions.items():
            value = float(np.abs(values[mask] - target[mask]).mean()) * 1000
            row[key] = value
            line += f"{value:9.2f} "
        binned.append(row)
        print(line)
    pd.DataFrame(binned).to_csv(f"{OUT}/step3_residual_vs_strain.csv", index=False)

    # structured splits
    print("\nstructured splits (PBE indirect gap), MAE in meV")
    small = table.strain_norm.to_numpy() <= np.quantile(table.strain_norm, 0.5)
    axis_and_skew = table.family.isin([
        "2-stretch-one-axis-or-two-axes", "3-skew-one-plane",
        "4-skew-two-planes", "5-skew-three-planes"]).to_numpy()
    general = (table.family == "6-stretch-all-three-axes").to_numpy()

    for label, train, test in (
            ("small strain -> large strain", small, ~small),
            ("axis+skew families -> general stretch", axis_and_skew, general)):
        line = f"  {label:40s}"
        for key in ["M0", "M1", "M2", "M3b", "M3", "M4"]:
            fold = [(np.where(train)[0], np.where(test)[0])]
            prediction = evaluate("indirect_gap", strains, target, orbit, fold)[key]
            value = float(np.abs(prediction[test] - target[test]).mean()) * 1000
            line += f" {key}={value:8.1f}"
        print(line)

    json.dump({str(k): v for k, v in results.items()},
              open(f"{OUT}/step3_ladder.json", "w"), indent=1)


if __name__ == "__main__":
    main()
