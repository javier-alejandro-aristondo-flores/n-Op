"""Using the symmetry: augmentation, group averaging, and the degeneracy test.

`symmetry.py` built and calibrated the machinery -- the 48 octahedral operations, the
corrected orbit labeler, the fcc-basis k-permutations. This module is what finally calls
it, which §5 makes REQUIRED in three parts.

The physical statement everything rests on, verified in `symmetry.calibrate` against the
data rather than assumed:

    E_{R eps R^T}(R k) = E_eps(k)      for all 48 operations R

So one computed shape is 48 labeled training pairs, and a prediction can be made exactly
equivariant by averaging over the group at inference.

## The honest multiplier

**Do not say "48x more data".** The images are exact but they are not independent: a model
that has seen one has seen most of what the other carries, and orbit-grouped
cross-validation already keeps a shape and its images in the same fold precisely because
they are the same calculation. The effective gain is real, unquantified, and far below 48.
"""

from __future__ import annotations

import numpy as np

import locations  # noqa: F401
from corpus import N_OCCUPIED, Corpus
from symmetry import GROUP, act_on_strain, kpoint_permutations

#: Isotropy tolerance. 1e-9 rather than 1e-12, because family 1's cells are written in an
#: a1-along-x frame whose residual shear survives at 1e-11 -- a 1e-12 test rejects 39 of the
#: 47 genuinely isotropic cells. Gate 4 paid for this lesson; the tolerance has to be one
#: the data can meet.
ISOTROPY_TOLERANCE = 1e-9


def permutations_for(corpus: Corpus) -> np.ndarray:
    from physics.formulas.elastic import reference_cell
    from sweep_read import A_EXPERIMENTAL

    return kpoint_permutations(corpus.grid, reference_cell(A_EXPERIMENTAL))


def augmented_training_set(corpus: Corpus, index: np.ndarray, permutations: np.ndarray,
                           copies: int = 2, seed: int = 0
                           ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Training arrays with `copies` random group images per shape, plus the originals.

    Acts on the *data*, not on model-specific features, so both architecture families take
    the result unchanged: the strain tensor rotates, and the two fields permute on their
    k axis by the same permutation.

    `copies = 2` by default rather than the full 48. Materializing all 48 would be 24 GB of
    trunk features for no proportionate gain, and sampling a fresh element per shape per
    fit covers the group in expectation. The identity is always included.
    """
    generator = np.random.default_rng(seed)
    strains = [corpus.strains[index]]
    pbe = corpus.referenced("pbe")
    correction = corpus.correction()
    fields = [pbe[index]]
    targets = [correction[index]]
    source = [index]

    for _ in range(copies):
        picks = generator.integers(0, len(GROUP), size=len(index))
        rotated = np.empty_like(corpus.strains[index])
        permuted_field = np.empty_like(pbe[index])
        permuted_target = np.empty_like(correction[index])
        for row, (shape, g) in enumerate(zip(index, picks)):
            rotated[row] = act_on_strain(corpus.strains[shape:shape + 1], GROUP[g])[0]
            permuted_field[row] = pbe[shape][permutations[g]]
            permuted_target[row] = correction[shape][permutations[g]]
        strains.append(rotated)
        fields.append(permuted_field)
        targets.append(permuted_target)
        source.append(index)

    return (np.concatenate(strains), np.concatenate(fields), np.concatenate(targets),
            np.concatenate(source))


def symmetrised_prediction(model, strains: np.ndarray, pbe_referenced: np.ndarray,
                           permutations: np.ndarray) -> np.ndarray:
    """Average the model over all 48 operations. Exactly equivariant, 48x inference cost.

    Transform the input by R, predict, transform the output back, average. Architecture
    agnostic -- it constrains the delivered operator without constraining the network.

    **It does not enforce every symmetry, and specifically not the one §5(iii) tests.**
    Under isotropic strain the strain tensor is invariant under all 48 operations, so all 48
    transformed inputs coincide; and every operation fixes Gamma, so the restored outputs
    coincide there too. The average collapses to the raw prediction exactly on the test case.
    Degeneracy at Gamma comes from the irreducible-representation structure of the states,
    and a sorted-eigenvalue field carries no group action on the band axis for averaging to
    exploit. That is why §5(iii) is an empirical test here and not a guarantee.
    """
    total = None
    for g, rotation in enumerate(GROUP):
        rotated = act_on_strain(strains, rotation)
        permuted = pbe_referenced[:, permutations[g], :]
        prediction = model.predict(rotated, permuted)
        restored = prediction[:, np.argsort(permutations[g]), :]
        total = restored if total is None else total + restored
    return total / len(GROUP)


def isotropic_mask(strains: np.ndarray) -> np.ndarray:
    """Shapes whose strain is a pure scaling -- the only ones cubic symmetry protects.

    Shear-free is *not* isotropic. A cell stretched unequally along x, y and z has no shear
    and still splits the Gamma triplet by up to 3 eV through the tetragonal deformation
    potential b, which is physics rather than error. Gate 4 first specified this check on
    shear-free cells and measured a 3064 meV "splitting" that was entirely real.
    """
    deviatoric = strains.copy()
    deviatoric[:, :3] -= strains[:, :3].mean(axis=1)[:, None]
    return np.abs(deviatoric).max(axis=1) < ISOTROPY_TOLERANCE


def gamma_triplet_splitting(field: np.ndarray, kfrac: np.ndarray) -> np.ndarray:
    """The spread of the top three valence states at Gamma, in eV, per shape."""
    from observables import gamma_index

    gamma = gamma_index(kfrac)
    triplet = np.sort(field[:, gamma, 1:N_OCCUPIED], axis=1)
    return triplet[:, -1] - triplet[:, 0]


def degeneracy_test(field: np.ndarray, corpus: Corpus) -> dict:
    """§5(iii): the Gamma valence triplet must stay degenerate under isotropic strain.

    Cubic symmetry forces the degeneracy exactly there and nowhere else. Gate 4 measured
    0.002 meV on the computed data, so anything the model adds is the model's.
    """
    mask = isotropic_mask(corpus.strains)
    splitting = gamma_triplet_splitting(field[mask], corpus.kfrac) * 1000
    anisotropic = gamma_triplet_splitting(field[~mask], corpus.kfrac) * 1000
    return {
        "isotropic_shapes": int(mask.sum()),
        "max_splitting_mev": float(splitting.max()),
        "median_splitting_mev": float(np.median(splitting)),
        "passes_1mev": bool(splitting.max() <= 1.0),
        # The control: if this is not large, the test is not testing anything, because a
        # model that predicts a constant would pass the degeneracy check trivially.
        "anisotropic_max_splitting_mev": float(anisotropic.max()),
    }


if __name__ == "__main__":
    from corpus import load

    corpus = load()
    permutations = permutations_for(corpus)

    print("== the degeneracy check on the ground truth (the control) ==")
    for tag in ("pbe", "hse"):
        report = degeneracy_test(corpus.referenced(tag), corpus)
        print(f"  {tag.upper():4s} isotropic shapes {report['isotropic_shapes']:3d}  "
              f"max {report['max_splitting_mev']:8.4f} meV  "
              f"anisotropic max {report['anisotropic_max_splitting_mev']:8.1f} meV")
    print("  (the anisotropic column is the control: it must be large, or the check is "
          "not testing the symmetry it names)")

    print("\n== augmentation ==")
    index = np.arange(64)
    strains, fields, targets, source = augmented_training_set(
        corpus, index, permutations, copies=2)
    print(f"  {len(index)} shapes -> {len(strains)} training rows (identity + 2 images)")

    # The augmented rows must carry the same physics. Check an invariant that the group
    # cannot change: the indirect gap of the underlying field.
    from observables import scalar_observables

    original = scalar_observables(corpus.referenced("pbe")[index],
                                  corpus.kfrac)["indirect_gap"].to_numpy()
    augmented = scalar_observables(fields, corpus.kfrac)["indirect_gap"].to_numpy()
    worst = np.abs(augmented - np.tile(original, 3)).max()
    print(f"  largest indirect-gap change across augmented copies: {worst:.3e} eV")
    assert worst < 1e-9, "augmentation changed the physics it is supposed to preserve"
    print("  augmentation preserves the observable it must")
