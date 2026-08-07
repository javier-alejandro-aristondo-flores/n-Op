"""Gate 4, step 4 -- the function-valued ladder.

The curve is what an operator would actually output, so the same question is asked of it
as of the scalars: can a cheap map from six numbers reproduce it?

Two things about this corpus's curves are stated rather than hidden. NBANDS = 8 means the
conduction side is complete only up to the lowest energy the eighth band reaches -- about
+12 eV above the valence maximum -- so the metric is reported over the full window *and*
over the sub-window where the band set is complete. And eight family-1 runs were computed
with 96 bands, which lets the cost of that truncation be measured instead of assumed.
"""

import json

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.neighbors import KNeighborsRegressor

from paths import RESULTS  # noqa: E402
from step1_noise import orbit_labels  # noqa: E402
from step3_ladder import features, m3b_features  # noqa: E402

OUT = str(RESULTS)

SIGMA = 0.3            # eV, the broadening gates 2 and 3 quote as the realistic figure
STEP = 0.05            # eV
LOW, HIGH = -25.0, 15.0
GRID = np.arange(LOW, HIGH + STEP / 2, STEP)
N_SPLITS = 5
ALPHAS = [1e-6, 1e-4, 1e-2, 1e-1, 1.0, 10.0]


def density_of_states(energies: np.ndarray, weights: np.ndarray,
                      reference: float) -> np.ndarray:
    """Gaussian-broadened DOS on the shared grid, referred to `reference`.

    Two electrons per band -- this sweep is spin-restricted -- so the occupied part
    integrates to the eight valence electrons without any further normalization.
    """
    shifted = energies - reference
    exponent = -((GRID[None, None, :] - shifted[:, :, None]) ** 2) / (2 * SIGMA ** 2)
    kernel = np.exp(exponent) / (SIGMA * np.sqrt(2 * np.pi))
    return 2.0 * np.einsum("k,kbe->e", weights, kernel)


def build_curves(energies: np.ndarray, weights: np.ndarray) -> np.ndarray:
    curves = np.empty((len(energies), len(GRID)))
    for i in range(len(energies)):
        vbm = energies[i, :, :4].max()
        curves[i] = density_of_states(energies[i], weights, vbm)
    return curves


def residual_percent(predicted: np.ndarray, truth: np.ndarray,
                     mask: np.ndarray | None = None) -> np.ndarray:
    """Integrated absolute difference as a percentage of the true curve's integral."""
    if mask is None:
        mask = np.ones(len(GRID), dtype=bool)
    numerator = np.abs(predicted[:, mask] - truth[:, mask]).sum(axis=1)
    denominator = truth[:, mask].sum(axis=1)
    return 100.0 * numerator / denominator


def main():
    data = np.load(f"{OUT}/spectra.npz")
    table = pd.read_csv(f"{OUT}/observables.csv")
    copies = pd.read_csv(f"{OUT}/step1_copies.csv")
    table = table.merge(copies, on=["family", "point"])
    keep = ~table.is_copy.to_numpy()

    weights = data["weights"]
    strains = data["strains"][keep]
    orbit = orbit_labels(strains)
    strain_norm = table.strain_norm.to_numpy()[keep]
    print(f"points {len(strains)}, symmetry orbits {len(set(orbit))}")

    # completeness limit of the eight-band set
    complete = table.pbe_complete_to.to_numpy()[keep]
    print(f"band set complete to {complete.min():.2f} eV above the VBM at worst, "
          f"{np.median(complete):.2f} eV typically")
    complete_mask = GRID <= complete.min()

    results = {}
    for tag in ["pbe", "hse"]:
        curves = build_curves(data[f"energies_{tag}"][keep], weights)
        equilibrium = curves[int(np.argmin(strain_norm))]

        predictions = {key: np.zeros_like(curves)
                       for key in ["L0", "L0mean", "L1", "L2", "L3"]}
        for train, test in GroupKFold(n_splits=N_SPLITS).split(strains, groups=orbit):
            predictions["L0"][test] = equilibrium
            predictions["L0mean"][test] = curves[train].mean(axis=0)

            for key, matrix in (("L1", features(strains, "M4")),
                                ("L2", m3b_features(strains))):
                best, best_score = None, np.inf
                inner = GroupKFold(n_splits=3).split(
                    strains[train], groups=orbit[train])
                inner = list(inner)
                for alpha in ALPHAS:
                    scores = []
                    for a, b in inner:
                        model = Ridge(alpha=alpha).fit(matrix[train][a], curves[train][a])
                        scores.append(residual_percent(
                            model.predict(matrix[train][b]), curves[train][b]).mean())
                    if np.mean(scores) < best_score:
                        best, best_score = alpha, np.mean(scores)
                model = Ridge(alpha=best).fit(matrix[train], curves[train])
                predictions[key][test] = model.predict(matrix[test])

            knn = KNeighborsRegressor(n_neighbors=5, weights="distance")
            knn.fit(strains[train], curves[train])
            predictions["L3"][test] = knn.predict(strains[test])

        print(f"\n== {tag.upper()} density of states, sigma = {SIGMA} eV, grouped CV ==")
        print(f"{'model':8s} {'residual %':>12s} {'sd':>8s} "
              f"{'complete window':>17s} {'worst':>8s}")
        for key, predicted in predictions.items():
            full = residual_percent(predicted, curves)
            windowed = residual_percent(predicted, curves, complete_mask)
            results[(tag, key)] = dict(mean=float(full.mean()), sd=float(full.std()),
                                       complete=float(windowed.mean()),
                                       worst=float(full.max()))
            print(f"{key:8s} {full.mean():11.2f}% {full.std():8.2f} "
                  f"{windowed.mean():16.2f}% {full.max():8.2f}")

        # residual against strain magnitude
        print(f"\n{tag.upper()} residual against strain magnitude (%)")
        bins = [0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.15]
        print(f"{'||E|| bin':>12s} {'n':>5s}" + "".join(f"{k:>9s}" for k in predictions))
        rows = []
        for low, high in zip(bins[:-1], bins[1:]):
            mask = (strain_norm >= low) & (strain_norm < high)
            if mask.sum() == 0:
                continue
            line = f"{low:.2f}-{high:.2f}".rjust(12) + f" {int(mask.sum()):5d}"
            row = {"functional": tag, "bin": f"{low:.2f}-{high:.2f}",
                   "n": int(mask.sum())}
            for key, predicted in predictions.items():
                value = float(residual_percent(predicted[mask], curves[mask]).mean())
                row[key] = value
                line += f"{value:9.2f}"
            rows.append(row)
            print(line)
        pd.DataFrame(rows).to_csv(f"{OUT}/step4_residual_vs_strain_{tag}.csv", index=False)

        # where on the energy axis does the residual sit?
        profile = {}
        for key in ["L0", "L1", "L2"]:
            absolute = np.abs(predictions[key] - curves).mean(axis=0)
            profile[key] = absolute
        total = profile["L1"].sum()
        print(f"\n{tag.upper()} where the L1 residual concentrates "
              f"(share of total absolute residual)")
        regions = [("deep valence  < -10 eV", GRID < -10),
                   ("valence  -10..-2 eV", (GRID >= -10) & (GRID < -2)),
                   ("valence edge  -2..0", (GRID >= -2) & (GRID < 0)),
                   ("in gap  0..4 eV", (GRID >= 0) & (GRID < 4)),
                   ("conduction edge 4..7", (GRID >= 4) & (GRID < 7)),
                   ("conduction  > 7 eV", GRID >= 7)]
        for label, mask in regions:
            print(f"  {label:24s} {100 * profile['L1'][mask].sum() / total:6.2f}%")
        np.savez(f"{OUT}/step4_profile_{tag}.npz", grid=GRID,
                 **{k: v for k, v in profile.items()},
                 mean_curve=curves.mean(axis=0))

    # ---- what the eight-band truncation costs -----------------------------
    print("\n== cost of the NBANDS = 8 truncation, on the eight 96-band runs ==")
    wide = np.load(f"{OUT}/wide_bands.npz")
    differences = []
    for key in wide.files:
        index = int(key.split("_")[0])
        full_energies = wide[key]
        narrow = full_energies[:, :8]
        vbm = narrow[:, :4].max()
        curve_narrow = density_of_states(narrow, weights, vbm)
        curve_full = density_of_states(full_energies, weights, vbm)
        difference = 100 * np.abs(curve_full - curve_narrow).sum() / curve_full.sum()
        windowed = (100 * np.abs(curve_full - curve_narrow)[complete_mask].sum()
                    / curve_full[complete_mask].sum())
        differences.append((difference, windowed))
    differences = np.array(differences)
    print(f"  full window      mean {differences[:, 0].mean():.2f}%  "
          f"max {differences[:, 0].max():.2f}%")
    print(f"  complete window  mean {differences[:, 1].mean():.3f}%  "
          f"max {differences[:, 1].max():.3f}%")
    print("  (the first number is what truncation costs; the second is what remains "
          "inside the window the ladder is judged on)")

    json.dump({f"{k[0]}_{k[1]}": v for k, v in results.items()},
              open(f"{OUT}/step4_dos.json", "w"), indent=1)


if __name__ == "__main__":
    main()
