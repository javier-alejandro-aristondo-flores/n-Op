"""The 48 octahedral operations, acting jointly on strain and on the k-mesh.

Diamond's point group is m-3m. If R is one of its 48 operations then

    E_{R eps R^T}(R k) = E_eps(k)

exactly -- not approximately, and not only in the continuum. So one computed shape is 48
labeled training pairs, and two sampled shapes whose strain tensors are related by an R
are the *same physical calculation* seen twice.

Both consequences are used here: the orbit label groups cross-validation folds so a model
can never see a test shape's image while training, and the group action supplies exact
augmentation and the inference-time averaging that makes the delivered operator equivariant.

## The signed-zero correction

Gate 4's `orbit_labels` factorizes on `str(canonical_strain(row))`. `np.round` preserves
the sign of zero, and `str` distinguishes `-0.0` from `0.0` while `==` does not, so 156
orbits are split by a difference that is not a difference: the count comes out **658**
where the same file's own `groupby(canonical)` -- and the noise floor built on it -- gets
**348**. Gate 4's noise floor used the correct route; its cross-validation grouping used
the broken one, and was therefore weaker than it reported.

The corpus already specifies the fix. `learnable-structure-contract#seam-purity` requires
that hashing apply the float normalization of `representation-substrate#serialization`:
canonical quiet not-a-number, **negative zero mapped to positive zero**. Applying that rule
reproduces 348. It is applied here, and `calibrate()` below checks the result against the
independently-computed numbers Gate 4's step 1 published, because a labeler nobody has
watched fail is indistinguishable from one that cannot fire.

This matters far more here than it did there. A five-parameter deformation-potential model
cannot memorize a symmetry image; an operator trained with 48-fold augmentation is the
model class that can.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import locations  # noqa: F401  -- puts Gate 4's code on the import path
from step1_noise import GROUP, canonical_strain, tensor_to_voigt, voigt_to_tensor

__all__ = ["GROUP", "orbit_labels", "canonical_strain", "voigt_to_tensor",
           "tensor_to_voigt", "act_on_strain", "kpoint_permutations", "group_average",
           "calibrate"]

MESH = 7


def _normalise_zero(values: np.ndarray) -> np.ndarray:
    """Map -0.0 to +0.0, the corpus's float-normalization rule for identity.

    `-0.0 == 0.0` is true and `str(-0.0) != str(0.0)` is also true, so any identity built
    by stringifying a float must apply this first or it splits equal keys.
    """
    return values + 0.0


def orbit_labels(strains: np.ndarray) -> np.ndarray:
    """Integer label per shape, equal exactly for symmetry twins.

    Gate 4's version, with the signed-zero normalization the corpus requires. Two shapes
    share a label exactly when an octahedral operation carries one strain tensor to the
    other, which is a statement about the crystal rather than about how the sweep named
    its families.
    """
    keys = [str(tuple(_normalise_zero(np.asarray(canonical_strain(row), dtype=float))))
            for row in strains]
    return pd.Series(keys).factorize()[0]


def act_on_strain(strains: np.ndarray, rotation: np.ndarray) -> np.ndarray:
    """eps -> R eps R^T, in Voigt order with engineering shear preserved."""
    out = np.empty_like(strains)
    for i, row in enumerate(np.atleast_2d(strains)):
        out[i] = tensor_to_voigt(rotation @ voigt_to_tensor(row) @ rotation.T)
    return out


def _fold(coords: np.ndarray) -> tuple:
    """The representative of {k, -k} on the integer mesh, as Gate 4's table stores it."""
    forward = tuple(int(v) % MESH for v in coords)
    backward = tuple(int(-v) % MESH for v in coords)
    return forward if forward <= backward else backward


def fractional_action(rotation: np.ndarray, lattice: np.ndarray) -> np.ndarray:
    """A Cartesian operation, expressed on fractional reciprocal coordinates.

    **The cell is the two-atom face-centered-cubic primitive, not a cube.** Its lattice
    vectors are `(0,a/2,a/2)` and permutations, so an octahedral operation -- a signed
    permutation in Cartesian axes -- is *not* a signed permutation of fractional
    coordinates. With rows of `A` as lattice vectors, `k_cart = f @ B` and
    `B = 2*pi*inv(A).T`, so `f -> f @ (A R inv(A)).T`, i.e. column coordinates transform
    by `N = A R inv(A)`.

    `N` is integral for every operation of the lattice's own point group -- checked below
    rather than assumed, since a non-integral `N` would silently map mesh points off the
    mesh and the resulting permutation would be nonsense.
    """
    action = lattice @ rotation @ np.linalg.inv(lattice)
    rounded = np.rint(action)
    if np.abs(action - rounded).max() > 1e-9:
        raise ValueError("the operation does not map the reciprocal lattice to itself")
    return rounded.astype(int)


def kpoint_permutations(grid: np.ndarray, lattice: np.ndarray) -> np.ndarray:
    """For each of the 48 operations, the k-index permutation it induces, shape (48, nk).

    `permutations[g][i]` is the index whose k-point R_g maps *onto* k_i, so a field is
    transformed by `field[..., permutations[g], :]`. Time reversal is already folded into
    the 172-point set; folding again after the rotation keeps the action closed on it,
    which is exact because `R(-k) = -(Rk)`.
    """
    index_of = {_fold(row): i for i, row in enumerate(grid)}
    if len(index_of) != len(grid):
        raise ValueError("the k-grid keys are not distinct after folding")

    permutations = np.empty((len(GROUP), len(grid)), dtype=int)
    for g, rotation in enumerate(GROUP):
        inverse = fractional_action(np.linalg.inv(rotation), lattice)
        for i, row in enumerate(grid):
            permutations[g, i] = index_of[_fold(inverse @ np.asarray(row, dtype=int))]
    return permutations


def group_average(predict, strains: np.ndarray, permutations: np.ndarray) -> np.ndarray:
    """Average a prediction over the 48 operations, making it exactly equivariant.

    Transform the input by R, predict, transform the output back, average. This is
    architecture-agnostic and costs 48 forward passes.

    **It does not enforce every symmetry.** Under isotropic strain the input is invariant
    under all 48 operations and every operation fixes Gamma, so all 48 terms coincide and
    the average is the raw prediction. The Gamma valence-triplet degeneracy therefore
    survives averaging only if the network already has it; that is why the degeneracy
    check is an empirical acceptance test here and not a guarantee.
    """
    total = None
    for g, rotation in enumerate(GROUP):
        prediction = predict(act_on_strain(strains, rotation))
        restored = prediction[..., np.argsort(permutations[g]), :]
        total = restored if total is None else total + restored
    return total / len(GROUP)


def calibrate() -> dict:
    """Check the labeler and the group action against facts computed another way.

    Three probes, each of which must fire if the machinery is wrong:

    1. the orbit count reproduces the 213 multi-member orbits over 996 points that Gate 4's
       step 1 published from an independent `groupby`;
    2. the k-permutations are genuine permutations, and the identity operation gives the
       identity permutation;
    3. every symmetry twin's spectra agree after the action -- the physical statement the
       whole module rests on, checked on the data rather than assumed.
    """
    from programs.oracle.registry.elastic import reference_cell
    from sweep_read import A_EXPERIMENTAL

    from corpus import load

    corpus = load()
    labels = orbit_labels(corpus.strains)
    sizes = pd.Series(labels).value_counts()
    multi = sizes[sizes > 1]

    permutations = kpoint_permutations(corpus.grid, reference_cell(A_EXPERIMENTAL))
    identity = next(g for g, r in enumerate(GROUP) if np.array_equal(r, np.eye(3)))

    worst = 0.0
    for _, members in pd.Series(labels).groupby(labels):
        index = members.index.to_numpy()
        if len(index) < 2:
            continue
        reference = corpus.strains[index[0]]
        for other in index[1:]:
            for g, rotation in enumerate(GROUP):
                if np.allclose(act_on_strain(corpus.strains[other:other + 1],
                                             rotation)[0], reference, atol=1e-9):
                    mapped = corpus.energies_pbe[other][permutations[g]]
                    worst = max(worst, float(np.abs(
                        mapped - corpus.energies_pbe[index[0]]).max()))
                    break

    report = {
        "orbits": int(len(sizes)),
        "multi_member_orbits": int(len(multi)),
        "points_in_multi_member": int(multi.sum()),
        "permutations_are_bijections": bool(
            all(len(set(p)) == len(p) for p in permutations)),
        "identity_is_identity": bool(
            np.array_equal(permutations[identity], np.arange(len(corpus.grid)))),
        "worst_twin_spectrum_difference_ev": worst,
    }
    assert report["multi_member_orbits"] == 213, (
        f"expected Gate 4's 213 multi-member orbits, got "
        f"{report['multi_member_orbits']} -- the labeler disagrees with step 1")
    assert report["points_in_multi_member"] == 996, (
        f"expected 996 points in them, got {report['points_in_multi_member']}")
    assert report["permutations_are_bijections"], "a k-permutation is not a bijection"
    assert report["identity_is_identity"], "the identity operation permutes the mesh"
    assert worst < 1e-3, f"symmetry twins disagree by {worst:.3e} eV after the action"
    return report


if __name__ == "__main__":
    from corpus import load

    corpus = load()
    print(f"Gate 4's labeler    {len(set(__import__('step1_noise').orbit_labels(corpus.strains)))} orbits")
    print(f"corrected labeler   {len(set(orbit_labels(corpus.strains)))} orbits")
    print()
    for key, value in calibrate().items():
        print(f"  {key:34s} {value}")
    print("\ncalibration passed -- every probe above fires if the machinery is wrong")
