"""Gate 4, step 0 -- coverage, pairing, mesh, files, and each functional's own a0.

Blocking by design: five unknowns here decide how the rest of the gate runs, and the
first of them -- how much strain the sweep actually reaches -- is the single biggest risk
to the target.
"""

import json
import os

import numpy as np

from paths import RESULTS, require_cache  # noqa: E402
from sweep_read import (CACHE, EIGENVAL, HSE, INCAR, OSZICAR, PBE, POSCAR,  # noqa: E402
                        read_eigenval, read_incar, read_oszicar_history,
                        read_poscar_lattice, strain_magnitude, strain_of, valley_points)

OUT = str(RESULTS)

FAMILIES = ["1-scale-all-axes-uniformly", "2-stretch-one-axis-or-two-axes",
            "3-skew-one-plane", "4-skew-two-planes", "5-skew-three-planes",
            "6-stretch-all-three-axes"]


def main():
    require_cache()          # reads POSCAR, INCAR, EIGENVAL and OSZICAR per run
    manifest = json.load(open(f"{OUT}/file_manifest.json"))

    # ---- what the run directories actually are -----------------------------
    points = {}          # (family, point) -> {subrun: rundir}
    stray = []
    for run in manifest:
        parts = run.split("/")
        if len(parts) == 3 and parts[2] in (PBE, HSE):
            points.setdefault((parts[0], parts[1]), {})[parts[2]] = run
        else:
            stray.append(run)

    print(f"run directories       {len(manifest)}")
    print(f"distortion points     {len(points)}")
    print(f"non-conforming dirs   {len(stray)}: {stray}")

    # ---- files present -----------------------------------------------------
    present = {}
    for run, files in manifest.items():
        for base, size in files.items():
            entry = present.setdefault(base, [0, 0])
            entry[0] += 1
            entry[1] += size == 0
    print("\nfile                                          runs   empty")
    for base in sorted(present, key=lambda b: -present[b][0]):
        print(f"  {base:42s} {present[base][0]:5d} {present[base][1]:7d}")

    # ---- per-run read ------------------------------------------------------
    rows = []
    failures = []
    mesh_signature = {}
    for (family, point), subruns in sorted(points.items()):
        for subrun, run in sorted(subruns.items()):
            record = dict(family=family, point=point, subrun=subrun, run=run)
            try:
                lattice = read_poscar_lattice(f"{CACHE}/{run}/{POSCAR}")
                voigt = strain_of(lattice)
                record["volume"] = float(abs(np.linalg.det(lattice)))
                for i, name in enumerate(["e1", "e2", "e3", "e4", "e5", "e6"]):
                    record[name] = float(voigt[i])
                record["strain_norm"] = float(strain_magnitude(voigt))
                record["max_abs_voigt"] = float(np.max(np.abs(voigt)))

                tags = read_incar(f"{CACHE}/{run}/{INCAR}")
                record["lhfcalc"] = tags.get("LHFCALC", "")
                record["aexx"] = tags.get("AEXX", "")
                record["ispin"] = tags.get("ISPIN", "")
                record["encut"] = tags.get("ENCUT", "")
                record["functional"] = "HSE" if tags.get("LHFCALC", "").upper().startswith(
                    ".T") else "PBE"

                ev = read_eigenval(f"{CACHE}/{run}/{EIGENVAL}")
                # `+ 0.0` collapses negative zero onto zero. Without it the ~1e-15 noise
                # components of the k-points hash differently run to run and every run
                # looks like its own mesh.
                key = (ev["nk"], ev["nb"], ev["nelect"],
                       hash((ev["kpoints"].round(6) + 0.0).tobytes()),
                       hash((ev["weights"].round(9) + 0.0).tobytes()))
                mesh_signature.setdefault(key, []).append(run)
                record["nk"] = ev["nk"]
                record["nb"] = ev["nb"]

                history = read_oszicar_history(f"{CACHE}/{run}/{OSZICAR}")
                record["energy"] = history[-1] if history else None
                record["ionic_steps"] = len(history)
            except Exception as exc:                      # noqa: BLE001
                failures.append((run, repr(exc)))
                continue
            rows.append(record)

    print(f"\nruns read             {len(rows)}")
    print(f"read failures         {len(failures)}")
    for run, exc in failures[:10]:
        print(f"    {run}: {exc}")

    # ---- the mesh ----------------------------------------------------------
    print(f"\ndistinct k-mesh signatures: {len(mesh_signature)}")
    for key, runs in mesh_signature.items():
        print(f"  nk={key[0]} nb={key[1]} nelect={key[2]}  runs={len(runs)}")

    any_ev = read_eigenval(f"{CACHE}/{rows[0]['run']}/{EIGENVAL}")
    valleys = valley_points(any_ev["kpoints"])
    print(f"Delta-line mesh points (6/7 of Gamma->X): {valleys}")
    print(f"weights sum to {any_ev['weights'].sum():.9f}")

    # ---- coverage ----------------------------------------------------------
    import pandas as pd
    frame = pd.DataFrame(rows)
    frame.to_csv(f"{OUT}/step0_runs.csv", index=False)

    print("\nstrain coverage, PBE runs only (Green-Lagrange, referred to a0 = 3.567 A)")
    print("family                            n   max|e_V|  max||E||  median||E||  "
          "max|e1..3|  max|e4..6|")
    pbe = frame[frame.functional == "PBE"]
    for family in FAMILIES:
        sub = pbe[pbe.family == family]
        if not len(sub):
            continue
        normal = sub[["e1", "e2", "e3"]].abs().to_numpy()
        shear = sub[["e4", "e5", "e6"]].abs().to_numpy()
        print(f"  {family:30s} {len(sub):4d}  {sub.max_abs_voigt.max():8.4f}  "
              f"{sub.strain_norm.max():8.4f}  {sub.strain_norm.median():10.4f}  "
              f"{normal.max():9.4f}  {shear.max():9.4f}")
    normal = pbe[["e1", "e2", "e3"]].abs().to_numpy()
    shear = pbe[["e4", "e5", "e6"]].abs().to_numpy()
    print(f"  {'ALL':30s} {len(pbe):4d}  {pbe.max_abs_voigt.max():8.4f}  "
          f"{pbe.strain_norm.max():8.4f}  {pbe.strain_norm.median():10.4f}  "
          f"{normal.max():9.4f}  {shear.max():9.4f}")

    print("\nstrain-magnitude distribution (PBE), fraction of points with ||E|| above:")
    for threshold in [0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15]:
        share = float((pbe.strain_norm > threshold).mean())
        print(f"  ||E|| > {threshold:4.2f}   {share * 100:5.1f}%   "
              f"({int((pbe.strain_norm > threshold).sum())} points)")

    # ---- pairing -----------------------------------------------------------
    pivot = frame.pivot_table(index=["family", "point"], columns="functional",
                              values="energy", aggfunc="first")
    both = pivot.dropna()
    print(f"\npoints with a readable run at both functionals: {len(both)} of {len(pivot)}")
    for family in FAMILIES:
        sub = pivot[pivot.index.get_level_values(0) == family]
        print(f"  {family:30s} {int(sub.notna().all(axis=1).sum()):4d} / {len(sub):4d}")

    # ---- each functional's own a0 -----------------------------------------
    from programs.oracle.registry.eos import fit_energy_volume
    print("\nequation of state on the uniform-scaling family")
    for functional in ["PBE", "HSE"]:
        sub = frame[(frame.family == FAMILIES[0]) & (frame.functional == functional)]
        sub = sub.dropna(subset=["energy"]).sort_values("volume")
        fit = fit_energy_volume(sub.volume.to_numpy(), sub.energy.to_numpy())
        print(f"  {functional:4s} n={fit.n_points:3d}  V0={fit.equilibrium_volume:.4f} A^3  "
              f"a0={fit.cubic_lattice_constant:.4f} A  B0={fit.bulk_modulus:.1f} GPa  "
              f"B0'={fit.bulk_modulus_pressure_derivative:.2f}  "
              f"max residual {fit.max_residual_ev * 1000:.2f} meV")

    json.dump({"n_points": len(points), "n_runs": len(rows), "failures": failures,
               "valleys": valleys, "stray": stray},
              open(f"{OUT}/step0_summary.json", "w"), indent=1)


if __name__ == "__main__":
    main()
