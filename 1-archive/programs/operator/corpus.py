"""The frozen corpus, loaded once, with the conventions Gate 4 fixed.

Nothing here is a new definition. The strain convention, the de-duplication rule, the
symmetry orbits and the three frozen splits all come from Gate 4's code by import, so
this library and the exams it will be judged against cannot drift apart.

Three facts about the data that every consumer needs and none should re-derive:

* **1,179 rows, 1,131 distinct shapes.** Twenty-four shapes appear three times. Gate 4
  established that those copies are *parsed-content identical* -- the largest eigenvalue
  difference within any group is exactly 0 eV -- and therefore measure nothing. They are
  dropped, never split across a fold. (The dataset's read-me calls them bit-identical;
  the files are not, because the HSE `INCAR` writes `System = <directory name>`, so 72 of
  144 raw hashes differ while every number agrees. Gate 4's `METHOD.md` records the
  correction: compare content, not bytes, when the question is about content.)

* **No absolute energy reference exists across cells.** Periodic density-functional theory
  fixes the potential zero per calculation, so a raw eigenvalue from one strained cell
  cannot be compared with one from another. Every field this module hands out is referred
  to its own valence-band maximum, and every observable downstream is a difference.

* **k-weights are multiplicities, not decoration.** The 172 points are what survives
  folding 7x7x7 by time reversal, and they carry unequal weights. Any Brillouin-zone
  average that ignores them is averaging the wrong measure.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

import locations  # noqa: F401  -- puts Gate 4's code on the import path
from locations import GATE4_RESULTS
from symmetry import orbit_labels  # the signed-zero-corrected labeler; see symmetry.py

N_OCCUPIED = 4          # 8 electrons, spin-restricted, 2 per band
N_BANDS = 8
N_KPOINTS = 172

#: The families whose cells vary one or two axes, or skew. The general-stretch family is
#: held out against them: it is the only place all three normal strains move independently.
AXIS_AND_SKEW = (
    "2-stretch-one-axis-or-two-axes",
    "3-skew-one-plane",
    "4-skew-two-planes",
    "5-skew-three-planes",
)
GENERAL_STRETCH = "6-stretch-all-three-axes"


@dataclass(frozen=True)
class Corpus:
    """Every distinct shape, both functionals, with the shared mesh."""

    energies_pbe: np.ndarray     # (n, 172, 8) eV, as computed
    energies_hse: np.ndarray     # (n, 172, 8) eV, as computed
    strains: np.ndarray          # (n, 6) Green-Lagrange, Voigt, engineering shear
    strain_norm: np.ndarray      # (n,) Frobenius norm of the tensor
    volumes: np.ndarray          # (n,) cubic angstrom
    weights: np.ndarray          # (172,) time-reversal multiplicities
    kfrac: np.ndarray            # (172, 3) fractional coordinates
    grid: np.ndarray             # (172, 3) integer 7x7x7 coordinates
    orbit: np.ndarray            # (n,) symmetry-orbit label
    family: np.ndarray           # (n,) family directory name
    point: np.ndarray            # (n,) shape name
    wide: np.ndarray             # (n,) bool, the eight 96-band runs

    def __len__(self) -> int:
        return len(self.strains)

    # -- referencing --------------------------------------------------------

    def referenced(self, functional: str) -> np.ndarray:
        """The field with each shape referred to its own valence-band maximum.

        This is the representation the operator predicts, and the only one in which two
        differently-strained cells are comparable at all.
        """
        energies = self.field(functional)
        return energies - vbm_of(energies)[:, None, None]

    def field(self, functional: str) -> np.ndarray:
        if functional == "pbe":
            return self.energies_pbe
        if functional == "hse":
            return self.energies_hse
        raise ValueError(f"unknown functional {functional!r}; expected 'pbe' or 'hse'")

    def correction(self) -> np.ndarray:
        """The per-eigenvalue PBE->HSE residual field, both sides own-VBM referred.

        This is Mode 1's target. It is a ~1.2 eV object carrying ~325 meV of structured
        variation, which is why it is learned instead of the full ~40 eV HSE spectrum.
        """
        return self.referenced("hse") - self.referenced("pbe")

    # -- the three frozen splits -------------------------------------------

    def small_strain_mask(self) -> np.ndarray:
        """Lower half by strain magnitude. Train here, test on the upper half."""
        return self.strain_norm <= np.median(self.strain_norm)

    def axis_and_skew_mask(self) -> np.ndarray:
        return np.isin(self.family, AXIS_AND_SKEW)

    def general_stretch_mask(self) -> np.ndarray:
        return self.family == GENERAL_STRETCH

    def top_quartile_mask(self) -> np.ndarray:
        """The decision region: strain magnitude above the 75th percentile."""
        return self.strain_norm > np.quantile(self.strain_norm, 0.75)

    def structured_splits(self) -> list[tuple[str, np.ndarray, np.ndarray]]:
        small = self.small_strain_mask()
        return [
            ("small strain -> large strain", small, ~small),
            ("axis+skew families -> general stretch",
             self.axis_and_skew_mask(), self.general_stretch_mask()),
        ]


def vbm_of(energies: np.ndarray) -> np.ndarray:
    """Valence-band maximum per shape: the largest occupied eigenvalue over the mesh.

    Band 4 is unambiguously the highest occupied band -- 8 electrons, spin-restricted, no
    in-gap states, and Gate 4 measured zero partially-occupied points across the sweep.
    """
    return energies[..., :N_OCCUPIED].max(axis=(-2, -1))


def load() -> Corpus:
    """Gate 4's frozen tables, de-duplicated to the 1,131 distinct shapes."""
    data = np.load(GATE4_RESULTS / "spectra.npz")
    table = pd.read_csv(GATE4_RESULTS / "observables.csv").merge(
        pd.read_csv(GATE4_RESULTS / "step1_copies.csv"), on=["family", "point"])

    keep = ~table.is_copy.to_numpy()
    strains = data["strains"][keep]

    corpus = Corpus(
        energies_pbe=data["energies_pbe"][keep],
        energies_hse=data["energies_hse"][keep],
        strains=strains,
        strain_norm=table.strain_norm.to_numpy()[keep],
        volumes=data["volumes"][keep],
        weights=data["weights"],
        kfrac=data["kfrac"],
        grid=data["grid"],
        orbit=orbit_labels(strains),
        family=table.family.to_numpy()[keep],
        point=table.point.to_numpy()[keep],
        wide=data["wide"][keep],
    )

    assert corpus.energies_pbe.shape[1:] == (N_KPOINTS, N_BANDS), "unexpected field shape"
    assert len(corpus) == 1131, f"expected 1,131 distinct shapes, got {len(corpus)}"
    assert np.isfinite(corpus.energies_pbe).all(), "non-finite PBE eigenvalue"
    assert np.isfinite(corpus.energies_hse).all(), "non-finite HSE eigenvalue"
    return corpus


def truth_table() -> pd.DataFrame:
    """Gate 4's own observable table, de-duplicated, for checking against."""
    table = pd.read_csv(GATE4_RESULTS / "observables.csv").merge(
        pd.read_csv(GATE4_RESULTS / "step1_copies.csv"), on=["family", "point"])
    return table[~table.is_copy].reset_index(drop=True)


if __name__ == "__main__":
    corpus = load()
    print(f"shapes                {len(corpus)}")
    print(f"symmetry orbits       {len(set(corpus.orbit))}")
    print(f"field shape           {corpus.energies_pbe.shape}")
    print(f"strain magnitude      {corpus.strain_norm.min():.5f} .. "
          f"{corpus.strain_norm.max():.5f}")
    print(f"k-weights sum to      {corpus.weights.sum():.0f}")
    print(f"top-quartile shapes   {int(corpus.top_quartile_mask().sum())}")
    for label, train, test in corpus.structured_splits():
        print(f"{label:40s} train {int(train.sum()):5d}  test {int(test.sum()):5d}")
    correction = corpus.correction()
    print(f"correction field      mean {correction.mean():+.4f} eV, "
          f"sd {correction.std():.4f} eV")
