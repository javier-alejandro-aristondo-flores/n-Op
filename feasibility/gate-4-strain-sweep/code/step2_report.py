"""Gate 4, step 2 -- what the observables look like, including the artifact.

With a fixed coarse mesh the k-point holding the conduction minimum can hop from one mesh
point to another as strain deforms the bands, putting a kink in O1 that is an artifact of
sampling rather than a feature of the band structure. The gate's instruction is to report
those kinks, not to smooth them, so they are counted here and their size is measured
against O4, which cannot hop because its k-points are fixed by construction.
"""

import json

import numpy as np
import pandas as pd

from paths import RESULTS

OUT = str(RESULTS)


def main():
    table = pd.read_csv(f"{OUT}/observables.csv")
    copies = pd.read_csv(f"{OUT}/step1_copies.csv")
    table = table.merge(copies, on=["family", "point"])
    unique = table[~table.is_copy].reset_index(drop=True)
    meta = json.load(open(f"{OUT}/table_meta.json"))
    valley_indices = set(meta["valleys"].values())

    print("== observable ranges over 1,131 distinct shapes ==")
    print(f"{'observable':38s} {'min':>9s} {'median':>9s} {'max':>9s} {'span':>9s}")
    for tag in ["pbe", "hse"]:
        for name, label in [("indirect_gap", "indirect gap"),
                            ("direct_gap_gamma", "direct gap at Gamma"),
                            ("valence_splitting_total", "valence splitting at Gamma")]:
            values = unique[f"{tag}_{name}"].to_numpy()
            print(f"{tag.upper() + ' ' + label:38s} {values.min():9.4f} "
                  f"{np.median(values):9.4f} {values.max():9.4f} "
                  f"{values.max() - values.min():9.4f}")

    # ---- where the conduction minimum actually sits -----------------------
    print("\n== O1's argmin: does the conduction minimum stay on the Delta line? ==")
    for tag in ["pbe", "hse"]:
        column = unique[f"{tag}_cbm_kpoint"].to_numpy()
        on_delta = np.isin(column, list(valley_indices))
        print(f"  {tag.upper()}: conduction minimum on a sampled Delta point "
              f"{on_delta.sum()} of {len(column)} ({100 * on_delta.mean():.1f}%), "
              f"across {len(set(column))} distinct mesh points")
        counts = pd.Series(column).value_counts().head(6)
        print(f"     most-used k-indices: {dict(counts)}")

    # ---- the hop, measured along a one-parameter family -------------------
    print("\n== argmin hops along one-parameter families, and the kink each leaves ==")
    hops = []
    for family in sorted(unique.family.unique()):
        sub = unique[unique.family == family].copy()
        if family == "1-scale-all-axes-uniformly":
            sub = sub.sort_values("volume")
        else:
            sub = sub.sort_values("strain_norm")
        index = sub["pbe_cbm_kpoint"].to_numpy()
        gap = sub["pbe_indirect_gap"].to_numpy()
        changed = np.flatnonzero(index[1:] != index[:-1])
        # second difference of the gap: a kink shows up here, a smooth trend does not
        if len(gap) > 2:
            curvature = np.abs(np.diff(gap, 2))
            at_hop = curvature[np.clip(changed - 1, 0, len(curvature) - 1)] \
                if len(changed) else np.array([])
            hops.append(dict(
                family=family, points=len(sub), hops=int(len(changed)),
                median_curvature_mev=float(np.median(curvature)) * 1000,
                curvature_at_hops_mev=float(np.median(at_hop)) * 1000
                if len(at_hop) else float("nan")))
    frame = pd.DataFrame(hops)
    print(frame.to_string(index=False, float_format=lambda v: f"{v:9.3f}"))
    print("  (families other than 1 are not one-parameter, so their ordering by strain "
          "magnitude mixes directions; the count is indicative, not a derivative)")

    # ---- O4: the valleys split, and by how much ---------------------------
    print("\n== O4: the three sampled Delta energies, relative to each run's VBM ==")
    for tag in ["pbe", "hse"]:
        triple = unique[[f"{tag}_delta_x", f"{tag}_delta_y", f"{tag}_delta_z"]].to_numpy()
        spread = triple.max(axis=1) - triple.min(axis=1)
        print(f"  {tag.upper()}: valley splitting  median {np.median(spread) * 1000:8.1f} meV"
              f"  max {spread.max() * 1000:8.1f} meV")
        for family in sorted(unique.family.unique()):
            mask = (unique.family == family).to_numpy()
            print(f"      {family:32s} median {np.median(spread[mask]) * 1000:8.1f} meV"
                  f"  max {spread[mask].max() * 1000:8.1f} meV")

    # Under isotropic strain the three must stay degenerate -- a second free check.
    strain = unique[["e1", "e2", "e3", "e4", "e5", "e6"]].to_numpy()
    deviatoric = strain.copy()
    deviatoric[:, :3] -= strain[:, :3].mean(axis=1)[:, None]
    isotropic = np.abs(deviatoric).max(axis=1) < 1e-9
    triple = unique[["pbe_delta_x", "pbe_delta_y", "pbe_delta_z"]].to_numpy()[isotropic]
    print(f"\n  free check -- valley splitting under isotropic strain "
          f"({int(isotropic.sum())} points): "
          f"max {(triple.max(axis=1) - triple.min(axis=1)).max() * 1000:.4f} meV")

    print("\n== the gap against strain, by family (PBE indirect) ==")
    for family in sorted(unique.family.unique()):
        sub = unique[unique.family == family]
        print(f"  {family:32s} n={len(sub):4d}  gap "
              f"{sub.pbe_indirect_gap.min():.3f} .. {sub.pbe_indirect_gap.max():.3f} eV")


if __name__ == "__main__":
    main()
