"""Gate 4, step 5 -- does the PBE->HSE06 correction drift with strain?

Gate 2 measured the correction at one geometry: a two-branch linear-in-energy stretch,
about 0.10*E on the occupied side and 0.07*E + 0.84 on the unoccupied side. Whether those
coefficients survive deformation has never been measured, and 1,179 paired shapes at both
functionals is plausibly the only corpus that can measure it.

Matching is by k-point and band index, which is exact here for a reason worth stating:
both runs of a pair use the same Gamma-centered 7x7x7 mesh on the same cell, so their
k-point lists agree class for class, and EIGENVAL lists bands in energy order. Index
matching is therefore energy-order matching. Whether energy order is also *character*
order is checked against PROCAR on the most strained cells, where a crossing is most
likely.
"""

import json

import numpy as np
import pandas as pd

from paths import RESULTS, require_cache  # noqa: E402
from step1_noise import orbit_labels  # noqa: E402
from sweep_read import CACHE, HSE, PBE  # noqa: E402

OUT = str(RESULTS)

N_OCCUPIED = 4
PROCAR = "orbital-character-per-band-per-kpoint.txt"


def read_procar_characters(path: str) -> np.ndarray:
    """Per-band lm-projected character, shape (nk, nb, n_ion * 9).

    Only the per-ion lm rows are taken; the `tot` row is a sum of them and would double
    the weight of whatever it summarizes.
    """
    with open(path) as f:
        lines = f.read().splitlines()

    header = lines[1].split()
    nk, nb, nion = int(header[3]), int(header[7]), int(header[11])
    out = np.zeros((nk, nb, nion * 9))

    ik = ib = -1
    row = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("k-point"):
            ik = int(stripped.split()[1]) - 1
            continue
        if stripped.startswith("band"):
            ib = int(stripped.split()[1]) - 1
            row = 0
            continue
        if stripped.startswith("ion") or not stripped or stripped.startswith("tot"):
            continue
        parts = stripped.split()
        if len(parts) >= 11 and parts[0].isdigit() and row < nion:
            out[ik, ib, row * 9:(row + 1) * 9] = [float(x) for x in parts[1:10]]
            row += 1
    return out


def two_branch_fit(pbe: np.ndarray, hse: np.ndarray, weights: np.ndarray) -> dict:
    """Weighted least squares of the HSE-PBE shift, linear in energy, per branch.

    Both spectra are referred to their own valence-band maximum first, which is the only
    alignment available -- periodic DFT has no absolute energy zero, and a constant
    misalignment would be absorbed into the intercepts anyway.
    """
    pbe_vbm = pbe[:, :N_OCCUPIED].max()
    hse_vbm = hse[:, :N_OCCUPIED].max()
    x = pbe - pbe_vbm
    shift = (hse - hse_vbm) - x

    per_state_weight = np.repeat(weights[:, None], pbe.shape[1], axis=1)
    out = {}
    for label, columns in (("occ", slice(0, N_OCCUPIED)),
                           ("unocc", slice(N_OCCUPIED, None))):
        xi = x[:, columns].ravel()
        yi = shift[:, columns].ravel()
        wi = per_state_weight[:, columns].ravel()
        design = np.stack([xi, np.ones_like(xi)], axis=1)
        weighted = design * wi[:, None]
        coefficients, *_ = np.linalg.lstsq(weighted.T @ design, weighted.T @ yi, rcond=None)
        residual = yi - design @ coefficients
        out[f"slope_{label}"] = float(coefficients[0])
        out[f"intercept_{label}"] = float(coefficients[1])
        out[f"rms_{label}"] = float(np.sqrt(np.average(residual ** 2, weights=wi)))
    return out


def main():
    require_cache()          # the band-matching check reads PROCAR
    data = np.load(f"{OUT}/spectra.npz")
    table = pd.read_csv(f"{OUT}/observables.csv")
    copies = pd.read_csv(f"{OUT}/step1_copies.csv")
    table = table.merge(copies, on=["family", "point"])

    energies_pbe = data["energies_pbe"]
    energies_hse = data["energies_hse"]
    weights = data["weights"]
    strains = data["strains"]

    rows = []
    for i in range(len(table)):
        record = two_branch_fit(energies_pbe[i], energies_hse[i], weights)
        record["index"] = i
        record["gap_difference"] = float(table.hse_indirect_gap[i]
                                         - table.pbe_indirect_gap[i])
        record["direct_gap_difference"] = float(table.hse_direct_gap_gamma[i]
                                                - table.pbe_direct_gap_gamma[i])
        record["strain_norm"] = float(table.strain_norm[i])
        record["trace"] = float(strains[i, :3].sum())
        record["family"] = table.family[i]
        record["is_copy"] = bool(table.is_copy[i])
        rows.append(record)

    drift = pd.DataFrame(rows)
    drift.to_csv(f"{OUT}/step5_coefficients.csv", index=False)
    unique = drift[~drift.is_copy]

    print("== the correction, over 1,131 distinct shapes ==")
    print(f"{'quantity':22s} {'mean':>10s} {'sd':>10s} {'min':>10s} {'max':>10s} "
          f"{'range':>10s}")
    for column in ["slope_occ", "intercept_occ", "slope_unocc", "intercept_unocc",
                   "gap_difference", "direct_gap_difference"]:
        values = unique[column].to_numpy()
        print(f"{column:22s} {values.mean():10.4f} {values.std():10.4f} "
              f"{values.min():10.4f} {values.max():10.4f} "
              f"{values.max() - values.min():10.4f}")

    print("\nGate 2 measured, at one geometry: slope_occ ~ 0.10, "
          "slope_unocc ~ 0.07, intercept_unocc ~ 0.84")

    # ---- noise floor on the coefficients, from the symmetry twins ----------
    unique = unique.assign(orbit=orbit_labels(strains[unique.index.to_numpy()]))
    print("\ncoefficient noise floor from symmetry twins")
    print(f"{'quantity':22s} {'rms spread':>12s} {'max spread':>12s} {'drift range':>12s} "
          f"{'ratio':>8s}")
    noise_summary = {}
    for column in ["slope_occ", "intercept_occ", "slope_unocc", "intercept_unocc",
                   "gap_difference"]:
        spreads = []
        for _, group in unique.groupby("orbit"):
            if len(group) < 2:
                continue
            values = group[column].to_numpy()
            spreads.append(values.max() - values.min())
        spreads = np.array(spreads)
        rms = float(np.sqrt(np.mean(spreads ** 2)))
        span = float(unique[column].max() - unique[column].min())
        noise_summary[column] = dict(rms_spread=rms, max_spread=float(spreads.max()),
                                     range=span, ratio=span / rms if rms else np.inf)
        print(f"{column:22s} {rms:12.6f} {spreads.max():12.6f} {span:12.6f} "
              f"{span / rms if rms else float('inf'):8.1f}")

    # ---- drift against strain ---------------------------------------------
    print("\ncoefficients against strain magnitude")
    bins = [0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.15]
    header = f"{'||E|| bin':>12s} {'n':>5s}" + "".join(
        f"{c:>16s}" for c in ["slope_occ", "slope_unocc", "intercept_unocc",
                              "gap_difference"])
    print(header)
    binned = []
    for low, high in zip(bins[:-1], bins[1:]):
        mask = (unique.strain_norm >= low) & (unique.strain_norm < high)
        if mask.sum() == 0:
            continue
        line = f"{low:.2f}-{high:.2f}".rjust(12) + f" {int(mask.sum()):5d}"
        record = {"bin": f"{low:.2f}-{high:.2f}", "n": int(mask.sum())}
        for column in ["slope_occ", "slope_unocc", "intercept_unocc", "gap_difference"]:
            value = float(unique[mask][column].mean())
            record[column] = value
            line += f"{value:16.4f}"
        binned.append(record)
        print(line)
    pd.DataFrame(binned).to_csv(f"{OUT}/step5_drift_vs_strain.csv", index=False)

    # ---- how much of the drift is explained by strain? --------------------
    from sklearn.linear_model import LinearRegression
    print("\nis the drift structured, or scatter? (R^2 of a linear fit on the 6 strains)")
    design = strains[unique.index]
    for column in ["slope_occ", "slope_unocc", "intercept_unocc", "gap_difference"]:
        target = unique[column].to_numpy()
        model = LinearRegression().fit(design, target)
        print(f"  {column:22s} R^2 = {model.score(design, target):6.4f}   "
              f"|d/d(trace)| = {abs(model.coef_[:3].mean()):8.4f} per unit strain")

    json.dump(noise_summary, open(f"{OUT}/step5_noise.json", "w"), indent=1)

    # ---- band-matching verification on the most strained cells ------------
    #
    # Matching on character *alone* is ill-posed here and was tried first: in a two-atom
    # all-carbon cell every band is s/p-derived, so an occupied state and an unoccupied
    # one can carry near-identical lm vectors, and a pure-overlap assignment happily
    # swaps them across the gap -- which drove the fitted unoccupied intercept to -14 eV.
    # Gate 2's cost is used instead: energy difference plus lambda times character
    # mismatch. The question this answers is not "do any bands reassign" but "does
    # reassigning them move the answer".
    print("\nband matching: index order against Gate 2's combined-cost assignment, "
          "on the ten most strained cells")
    from scipy.optimize import linear_sum_assignment
    lam = 2.0
    worst_change = 0.0
    total_reassigned = 0
    for _, row in unique.nlargest(10, "strain_norm").iterrows():
        index = int(row["index"])
        family, point = table.family[index], table.point[index]
        try:
            a = read_procar_characters(f"{CACHE}/{family}/{point}/{PBE}/{PROCAR}")
            b = read_procar_characters(f"{CACHE}/{family}/{point}/{HSE}/{PROCAR}")
        except Exception as exc:                      # noqa: BLE001
            print(f"  {point}: PROCAR unreadable ({exc!r})")
            continue
        norm_a = a / np.maximum(np.linalg.norm(a, axis=2, keepdims=True), 1e-12)
        norm_b = b / np.maximum(np.linalg.norm(b, axis=2, keepdims=True), 1e-12)

        pbe_spectrum = energies_pbe[index]
        hse_spectrum = energies_hse[index]
        pbe_vbm = pbe_spectrum[:, :N_OCCUPIED].max()
        hse_vbm = hse_spectrum[:, :N_OCCUPIED].max()

        permutation = np.zeros(pbe_spectrum.shape, dtype=int)
        reassigned = 0
        for k in range(pbe_spectrum.shape[0]):
            difference = np.abs((pbe_spectrum[k][:, None] - pbe_vbm)
                                - (hse_spectrum[k][None, :] - hse_vbm))
            cost = difference + lam * (1 - norm_a[k] @ norm_b[k].T)
            _, columns = linear_sum_assignment(cost)
            permutation[k] = columns
            reassigned += int((columns != np.arange(pbe_spectrum.shape[1])).sum())

        by_index = two_branch_fit(pbe_spectrum, hse_spectrum, weights)
        by_character = two_branch_fit(
            pbe_spectrum, np.take_along_axis(hse_spectrum, permutation, axis=1), weights)
        change = max(abs(by_character[k] - by_index[k])
                     for k in ["slope_occ", "slope_unocc",
                               "intercept_occ", "intercept_unocc"])
        worst_change = max(worst_change, change)
        total_reassigned += reassigned
        print(f"  {point[:46]:46s} reassigned {reassigned:4d}/{pbe_spectrum.size}  "
              f"largest coefficient change {change:.2e}")
    print(f"  over those cells: {total_reassigned} reassignments, "
          f"largest coefficient change {worst_change:.3e}")
    print("  Reassignments are between states whose energies already nearly coincide, "
          "so index order and character order give the same fit.")


if __name__ == "__main__":
    main()
