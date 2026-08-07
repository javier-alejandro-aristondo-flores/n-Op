"""Read every run once and cache the arrays the rest of the gate works from.

Two canonicalizations happen here, and both are needed before any run can be compared
with any other:

* **k-points.** VASP kept one of each time-reversal pair {k, -k}, and *which* one it kept
  varies with cell shape -- 19 different choices across this sweep. The set is the same
  every time (172 classes, verified), so each run's arrays are reordered onto one shared
  ordering of those classes.
* **Bands.** Eight PBE runs in family 1 carry NBANDS = 96 rather than 8. Everything is
  truncated to the common 8, and the wide runs are kept aside to measure what that
  truncation costs the density of states.
"""

import json
import os

import numpy as np
import pandas as pd

from paths import RESULTS, require_cache  # noqa: E402
from sweep_read import (CACHE, EIGENVAL, HSE, PBE, POSCAR, observables,  # noqa: E402
                        read_eigenval, read_poscar_lattice, strain_magnitude, strain_of,
                        valley_points)

OUT = str(RESULTS)

N_BANDS = 8


def grid_index(kpoints: np.ndarray) -> np.ndarray:
    """Integer 7x7x7 grid coordinates, folded onto a representative of {k, -k}."""
    n = np.rint(kpoints * 7).astype(int) % 7
    m = (-np.rint(kpoints * 7).astype(int)).astype(int) % 7
    out = np.empty_like(n)
    for i in range(len(n)):
        a, b = tuple(n[i]), tuple(m[i])
        out[i] = a if a <= b else b
    return out


def canonical_order(kpoints: np.ndarray, reference_keys: list) -> np.ndarray:
    """Permutation putting this run's k-points into the shared canonical order."""
    keys = [tuple(row) for row in grid_index(kpoints)]
    position = {key: i for i, key in enumerate(keys)}
    if len(position) != len(reference_keys):
        raise ValueError("k-point set is not the shared 172-class set")
    return np.array([position[key] for key in reference_keys])


def main():
    require_cache()          # every point is re-read from EIGENVAL here
    runs = pd.read_csv(f"{OUT}/step0_runs.csv")
    points = sorted({(r.family, r.point) for r in runs.itertuples()})

    first = read_eigenval(f"{CACHE}/{runs.iloc[0].run}/{EIGENVAL}")
    reference_keys = sorted(tuple(row) for row in grid_index(first["kpoints"]))
    order = canonical_order(first["kpoints"], reference_keys)
    weights = first["weights"][order]
    kfrac = first["kpoints"][order]
    valleys = valley_points(kfrac)

    n = len(points)
    energies = {PBE: np.full((n, 172, N_BANDS), np.nan),
                HSE: np.full((n, 172, N_BANDS), np.nan)}
    strains = np.full((n, 6), np.nan)
    volumes = np.full(n, np.nan)
    wide = np.zeros(n, dtype=bool)
    wide_energies = {}
    records = []

    for i, (family, point) in enumerate(points):
        record = dict(index=i, family=family, point=point)
        for subrun, tag in ((PBE, "pbe"), (HSE, "hse")):
            run = f"{family}/{point}/{subrun}"
            ev = read_eigenval(f"{CACHE}/{run}/{EIGENVAL}")
            perm = canonical_order(ev["kpoints"], reference_keys)
            if ev["nb"] > N_BANDS:
                wide[i] = True
                wide_energies[(i, tag)] = ev["energies"][perm]
            energies[subrun][i] = ev["energies"][perm][:, :N_BANDS]

            truncated = dict(ev)
            truncated["energies"] = ev["energies"][perm][:, :N_BANDS]
            truncated["occupations"] = ev["occupations"][perm][:, :N_BANDS]
            truncated["kpoints"] = kfrac
            for key, value in observables(truncated).items():
                record[f"{tag}_{key}"] = value
            for name, index in valleys.items():
                record[f"{tag}_{name}"] = float(
                    truncated["energies"][index, 4] - record[f"{tag}_vbm"])

            if subrun == PBE:
                lattice = read_poscar_lattice(f"{CACHE}/{run}/{POSCAR}")
                strains[i] = strain_of(lattice)
                volumes[i] = abs(np.linalg.det(lattice))

        record["strain_norm"] = float(strain_magnitude(strains[i]))
        record["max_abs_voigt"] = float(np.max(np.abs(strains[i])))
        record["volume"] = float(volumes[i])
        record["wide_bands"] = bool(wide[i])
        records.append(record)

        if (i + 1) % 200 == 0:
            print(f"  {i + 1}/{n}", flush=True)

    table = pd.DataFrame(records)
    for j, name in enumerate(["e1", "e2", "e3", "e4", "e5", "e6"]):
        table[name] = strains[:, j]
    table.to_csv(f"{OUT}/observables.csv", index=False)

    np.savez_compressed(
        f"{OUT}/spectra.npz",
        energies_pbe=energies[PBE], energies_hse=energies[HSE],
        strains=strains, volumes=volumes, weights=weights, kfrac=kfrac,
        grid=np.array(reference_keys), wide=wide,
    )
    np.savez_compressed(
        f"{OUT}/wide_bands.npz",
        **{f"{i}_{tag}": array for (i, tag), array in wide_energies.items()})
    json.dump({"valleys": valleys, "n_points": n,
               "reference_keys_hash": hash(str(reference_keys))},
              open(f"{OUT}/table_meta.json", "w"), indent=1)

    print(f"points {n}  wide-band points {int(wide.sum())}")
    print(f"metallic (partially occupied) PBE: "
          f"{int((table.pbe_partially_occupied > 0).sum())}  "
          f"HSE: {int((table.hse_partially_occupied > 0).sum())}")
    print(table[["pbe_indirect_gap", "hse_indirect_gap", "pbe_direct_gap_gamma",
                 "strain_norm"]].describe().to_string())


if __name__ == "__main__":
    main()
