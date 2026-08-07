"""Gate 4, step 1 -- the noise floor, by two independent routes.

No residual anywhere in this gate means anything until it is compared against numerical
noise, and this corpus can measure that twice over.

**(a) The triplicates.** 24 shapes appear three times. The dataset's own read-me says the
copies are bit-identical, which would make them worth nothing as a noise measure. That is
checked here rather than believed -- the previous gates were burned by a duplicate that
was assumed independent.

**(b) The symmetry twins.** Diamond's point group is m-3m, so the spectrum obeys
`E(R eps R^T) = E(eps)` for all 48 octahedral operations. Any two sampled shapes whose
strain tensors are related by one of them must have identical spectra, and their measured
difference is pure numerics. This route is independent of (a) and survives even if every
triplicate is a copy.

Only quantities invariant under the operation are compared. A rotation swapping y and z
swaps the corresponding valleys, so the three valley energies are compared as a sorted
triple, never valley-by-valley.
"""

import itertools
import json

import numpy as np
import pandas as pd

from paths import RESULTS, RUN_MANIFEST, require_cache  # noqa: E402
from sweep_read import CACHE, EIGENVAL, read_eigenval  # noqa: E402

OUT = str(RESULTS)

DIGEST_FILES = ["everything-machine-readable.xml", "charge-density-grid-full.txt",
                "wavefunctions-binary-restart-only.bin", "band-energies-per-kpoint.txt"]


def octahedral_group() -> list[np.ndarray]:
    """All 48 signed permutation matrices -- the point group m-3m."""
    group = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product([1, -1], repeat=3):
            matrix = np.zeros((3, 3))
            for row, column in enumerate(perm):
                matrix[row, column] = signs[row]
            group.append(matrix)
    assert len({m.tobytes() for m in group}) == 48
    return group


GROUP = octahedral_group()


def voigt_to_tensor(voigt: np.ndarray) -> np.ndarray:
    e1, e2, e3, e4, e5, e6 = voigt
    return np.array([[e1, e6 / 2, e5 / 2], [e6 / 2, e2, e4 / 2], [e5 / 2, e4 / 2, e3]])


def tensor_to_voigt(tensor: np.ndarray) -> np.ndarray:
    return np.array([tensor[0, 0], tensor[1, 1], tensor[2, 2],
                     2 * tensor[1, 2], 2 * tensor[0, 2], 2 * tensor[0, 1]])


def canonical_strain(voigt: np.ndarray) -> tuple:
    """Lexicographically smallest image of the strain under the 48 operations.

    Two shapes are symmetry twins exactly when this agrees, which is a statement about
    the crystal rather than about how the sweep happened to name its families.
    """
    tensor = voigt_to_tensor(voigt)
    images = [tuple(np.round(tensor_to_voigt(r @ tensor @ r.T), 9)) for r in GROUP]
    return min(images)


def orbit_labels(strains: np.ndarray) -> np.ndarray:
    """Integer label per point, equal exactly for symmetry twins.

    Used to group cross-validation folds: two shapes related by an octahedral operation
    carry the same spectrum, so letting one train while the other tests is leakage.
    """
    keys = [str(canonical_strain(row)) for row in strains]
    return pd.Series(keys).factorize()[0]


def main():
    require_cache()          # the triplicate test re-reads EIGENVAL to compare content
    table = pd.read_csv(f"{OUT}/observables.csv")
    digests = json.load(open(f"{OUT}/digests.json"))

    # ---------------------------------------------------------------- (a) ----
    print("== (a) the triplicates: reruns, or copies? ==")
    manifest = pd.read_csv(
        str(RUN_MANIFEST),
        sep="\t", comment="#")
    grouped = manifest.dropna(subset=["duplicate_group"])
    print(f"rows carrying a duplicate_group: {len(grouped)} "
          f"in {grouped.duplicate_group.nunique()} groups")

    identical = {name: 0 for name in DIGEST_FILES}
    differing = {name: 0 for name in DIGEST_FILES}
    comparisons = 0
    worst_energy_difference = 0.0
    for _, rows in grouped.groupby("duplicate_group"):
        directories = list(rows.run_directory_inside_archive)
        for a, b in itertools.combinations(directories, 2):
            comparisons += 1
            for subrun in ["1-cheap-pbe-atoms-relaxed", "2-accurate-hse06-atoms-fixed"]:
                da = digests.get(f"{a}/{subrun}", {})
                db = digests.get(f"{b}/{subrun}", {})
                for name in DIGEST_FILES:
                    if name in da and name in db:
                        if da[name] == db[name]:
                            identical[name] += 1
                        else:
                            differing[name] += 1
                # A checksum answers "are these the same bytes", which is not the
                # question. Two copies of one calculation differ in their header if the
                # run was named after its directory -- and the HSE INCAR does exactly
                # that, so every HSE file here has a different hash and identical
                # physics. Compare the numbers.
                ea = read_eigenval(f"{CACHE}/{a}/{subrun}/{EIGENVAL}")
                eb = read_eigenval(f"{CACHE}/{b}/{subrun}/{EIGENVAL}")
                worst_energy_difference = max(
                    worst_energy_difference,
                    float(np.max(np.abs(ea["energies"] - eb["energies"]))))
    print(f"pairwise comparisons within groups: {comparisons}")
    print(f"{'file':45s} {'identical':>10s} {'differing':>10s}")
    for name in DIGEST_FILES:
        print(f"{name:45s} {identical[name]:10d} {differing[name]:10d}")
    print(f"largest eigenvalue difference within any group: "
          f"{worst_energy_difference:.3e} eV")
    copies = worst_energy_difference == 0.0
    print("VERDICT: bit-identical physics -- the triplicates measure nothing, and the "
          "differing hashes are a run-name string in the header, not a rerun"
          if copies else
          "VERDICT: the triplicates differ numerically -- they are independent reruns")

    # ---------------------------------------------------------------- (b) ----
    print("\n== (b) the symmetry twins ==")
    strains = table[["e1", "e2", "e3", "e4", "e5", "e6"]].to_numpy()
    table["canonical"] = [canonical_strain(row) for row in strains]

    # Drop the bit-identical copies first: they would contribute an exact zero to every
    # spread and pull the estimate down for a reason that is not numerical stability.
    duplicate_of = {}
    for _, rows in grouped.groupby("duplicate_group"):
        keep = None
        for directory in rows.run_directory_inside_archive:
            family, _, point = directory.partition("/")
            if keep is None:
                keep = (family, point)
            else:
                duplicate_of[(family, point)] = keep
    table["is_copy"] = [(f, p) in duplicate_of for f, p in zip(table.family, table.point)]
    unique = table[~table.is_copy]
    print(f"points after dropping bit-identical copies: {len(unique)} of {len(table)}")

    orbits = unique.groupby("canonical")
    sizes = orbits.size()
    multi = sizes[sizes > 1]
    print(f"symmetry orbits with more than one sampled member: {len(multi)}")
    print(f"points inside them: {int(multi.sum())}")
    print(f"orbit sizes: {dict(multi.value_counts().sort_index())}")

    observables = {
        "pbe_indirect_gap": "PBE indirect gap",
        "hse_indirect_gap": "HSE indirect gap",
        "pbe_direct_gap_gamma": "PBE direct gap at Gamma",
        "hse_direct_gap_gamma": "HSE direct gap at Gamma",
        "pbe_valence_splitting_total": "PBE valence splitting at Gamma",
        "hse_valence_splitting_total": "HSE valence splitting at Gamma",
    }

    rows = []
    for column, label in observables.items():
        spreads = []
        for _, group in orbits:
            if len(group) < 2:
                continue
            values = group[column].to_numpy()
            spreads.append(values.max() - values.min())
        spreads = np.array(spreads)
        rows.append(dict(observable=label, orbits=len(spreads),
                         max_spread_mev=spreads.max() * 1000,
                         median_spread_mev=float(np.median(spreads)) * 1000,
                         p95_spread_mev=float(np.percentile(spreads, 95)) * 1000,
                         rms_mev=float(np.sqrt(np.mean(spreads ** 2))) * 1000))

    # The three Delta energies are permuted by the operation, so only the sorted triple
    # is comparable.
    for tag in ["pbe", "hse"]:
        spreads = []
        for _, group in orbits:
            if len(group) < 2:
                continue
            triples = np.sort(
                group[[f"{tag}_delta_x", f"{tag}_delta_y", f"{tag}_delta_z"]].to_numpy(),
                axis=1)
            spreads.append(float(np.max(triples.max(axis=0) - triples.min(axis=0))))
        spreads = np.array(spreads)
        rows.append(dict(observable=f"{tag.upper()} Delta energies (sorted triple)",
                         orbits=len(spreads), max_spread_mev=spreads.max() * 1000,
                         median_spread_mev=float(np.median(spreads)) * 1000,
                         p95_spread_mev=float(np.percentile(spreads, 95)) * 1000,
                         rms_mev=float(np.sqrt(np.mean(spreads ** 2))) * 1000))

    noise = pd.DataFrame(rows)
    print("\nspread within symmetry orbits, in meV")
    print(noise.to_string(index=False, float_format=lambda v: f"{v:9.4f}"))
    noise.to_csv(f"{OUT}/step1_noise.csv", index=False)

    # The degeneracy check. Cubic symmetry protects the Gamma valence triplet only under
    # *isotropic* strain -- not merely zero shear. A cell stretched unequally along x, y
    # and z has no shear and splits the triplet by up to 3 eV through the tetragonal
    # deformation potential b, which is physics, not error. Only the uniform-scaling
    # family tests the numerics.
    strain_tensor = table[["e1", "e2", "e3", "e4", "e5", "e6"]].to_numpy()
    # Isotropy is a statement about the deviatoric part, and it needs a tolerance the
    # data can meet: family 1 is written in an a1-along-x frame whose residual shear
    # survives at 1e-11, so a 1e-12 test rejects 39 of the 47 genuinely isotropic cells.
    deviatoric = strain_tensor.copy()
    deviatoric[:, :3] -= strain_tensor[:, :3].mean(axis=1)[:, None]
    isotropic_mask = np.abs(deviatoric).max(axis=1) < 1e-9
    shear_free = np.abs(strain_tensor[:, 3:]).max(axis=1) < 1e-9
    isotropic = table[isotropic_mask]
    print(f"\nisotropically strained points (the free correctness check): {len(isotropic)}")
    for tag in ["pbe", "hse"]:
        values = isotropic[f"{tag}_valence_splitting_total"].to_numpy() * 1000
        print(f"  {tag.upper()} Gamma valence triplet splitting: "
              f"max {values.max():.6f} meV, median {np.median(values):.6f} meV")
    anisotropic = table[shear_free & ~isotropic_mask]
    print(f"  for contrast, shear-free but anisotropic ({len(anisotropic)} points): "
          f"max {anisotropic['pbe_valence_splitting_total'].max() * 1000:.1f} meV "
          "-- the b deformation potential, not noise")

    json.dump({"triplicates_are_copies": bool(copies),
               "orbit_count": int(len(multi)),
               "noise": noise.to_dict("records")},
              open(f"{OUT}/step1_noise.json", "w"), indent=1)
    table[["family", "point", "is_copy"]].to_csv(f"{OUT}/step1_copies.csv", index=False)


if __name__ == "__main__":
    main()
