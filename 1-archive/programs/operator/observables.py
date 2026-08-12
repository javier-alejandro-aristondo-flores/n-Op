"""O1-O4 and the density of states, extracted from a field -- predicted or true.

**One procedure, both sides.** Every function here takes a `(n, 172, 8)` eigenvalue field
and knows nothing about where it came from. That is the point: the spec requires the gap
be taken from a predicted field by the same mesh-minimum procedure used on ground truth,
because with a fixed mesh the conduction minimum can hop between mesh points and a model
scored by a different extraction would be credited or blamed for the mesh.

The extraction itself is Gate 4's, imported rather than rewritten -- `sweep_read.observables`
for O1-O3, `sweep_read.valley_points` for O4's mesh points, `step4_dos.density_of_states`
for the curve. A second definition here could drift from the one the exams were
pre-registered against, and the drift would be invisible.

**Occupations are synthesized, and that is exact here.** Gate 4's extractor takes them from
`EIGENVAL` to count partially-occupied states, and measured **zero** across the sweep: 8
electrons, spin-restricted, four filled bands, no in-gap states. A predicted field carries
no occupations, so band 4 / band 5 is used directly. The one quantity that genuinely needs
them -- the metallicity count -- is therefore a property of the ground truth and is not
something the operator is asked to predict.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import locations  # noqa: F401  -- puts Gate 4's code on the import path
from corpus import N_BANDS, N_OCCUPIED, vbm_of
from step4_dos import GRID, SIGMA, density_of_states, residual_percent  # noqa: F401
from sweep_read import observables as _observables_of_one
from sweep_read import valley_points

__all__ = ["GRID", "SIGMA", "scalar_observables", "curves", "residual_percent",
           "valley_energies", "gamma_index", "density_of_states"]

#: Filled-band occupations for a spin-restricted 8-electron cell.
_OCCUPATIONS = np.concatenate([np.ones(N_OCCUPIED), np.zeros(N_BANDS - N_OCCUPIED)])


def gamma_index(kfrac: np.ndarray) -> int:
    index = int(np.argmin(np.abs(kfrac).sum(axis=1)))
    if np.abs(kfrac[index]).sum() > 1e-8:
        raise ValueError("no Gamma point in the mesh")
    return index


def scalar_observables(energies: np.ndarray, kfrac: np.ndarray) -> pd.DataFrame:
    """O1-O4 for every shape in a field, by Gate 4's own extraction.

    Columns match Gate 4's `observables.csv` without its `pbe_`/`hse_` prefix, so a
    prediction and the truth it is scored against are directly comparable.
    """
    valleys = valley_points(kfrac)
    occupations = np.repeat(_OCCUPATIONS[None], len(kfrac), axis=0)

    rows = []
    for spectrum in energies:
        record = _observables_of_one(
            {"energies": spectrum, "occupations": occupations, "kpoints": kfrac})
        for name, index in valleys.items():
            record[name] = float(spectrum[index, N_OCCUPIED] - record["vbm"])
        rows.append(record)
    return pd.DataFrame(rows)


def valley_energies(energies: np.ndarray, kfrac: np.ndarray) -> np.ndarray:
    """The three Delta mesh energies above the valence maximum, shape (n, 3).

    Returned sorted, because an octahedral operation permutes the three valleys: only the
    sorted triple is invariant, and comparing valley-by-valley across symmetry twins
    would measure the labeling rather than the physics.
    """
    valleys = valley_points(kfrac)
    indices = [valleys[name] for name in ("delta_x", "delta_y", "delta_z")]
    reference = vbm_of(energies)
    return np.sort(energies[:, indices, N_OCCUPIED] - reference[:, None], axis=1)


def curves(energies: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """Gaussian-broadened density of states, each shape referred to its own VBM.

    sigma = 0.3 eV on a -25..+15 eV grid, k-weighted, two electrons per band. With a
    coarse mesh the raw spectrum is a comb of spikes, so a smaller sigma would measure the
    comb rather than the physics.
    """
    reference = vbm_of(energies)
    out = np.empty((len(energies), len(GRID)))
    for i, spectrum in enumerate(energies):
        out[i] = density_of_states(spectrum, weights, reference[i])
    return out


def complete_window(truth: pd.DataFrame) -> np.ndarray:
    """The sub-window where the eight-band set is provably complete at every shape.

    Above the lowest energy the topmost computed band reaches, bands nobody calculated
    would contribute, so the metric there is reported but not relied on.
    """
    return GRID <= float(truth["complete_to"].min())


if __name__ == "__main__":
    from corpus import load, truth_table

    corpus = load()
    truth = truth_table()

    for tag in ("pbe", "hse"):
        mine = scalar_observables(corpus.field(tag), corpus.kfrac)
        worst = {}
        for column in ("indirect_gap", "direct_gap_gamma", "valence_splitting_total",
                       "delta_x", "delta_y", "delta_z", "complete_to"):
            difference = np.abs(mine[column].to_numpy()
                                - truth[f"{tag}_{column}"].to_numpy()).max()
            worst[column] = difference
        print(f"{tag.upper()}  largest disagreement with Gate 4's table, per observable:")
        for column, value in worst.items():
            print(f"    {column:26s} {value:.3e} eV")
        # A tolerance the data can meet. Gate 4's numbers came back through a CSV, so a
        # round-trip at the last bit of a ~5 eV double is the floor here -- about 1e-15 eV.
        # A picoelectronvolt is ten orders of magnitude below the 0.0105 meV noise floor
        # and still far above that floor, so it separates "identical" from any real
        # disagreement without rejecting arithmetic that is already exact.
        assert max(worst.values()) < 1e-12, "the extraction disagrees with Gate 4's"

    window = complete_window(truth.rename(columns={"pbe_complete_to": "complete_to"}))
    print(f"\nDOS grid {len(GRID)} bins, complete sub-window {int(window.sum())} bins "
          f"(<= {GRID[window].max():.2f} eV)")
    print(f"curve integral check: occupied states integrate to "
          f"{curves(corpus.field('pbe')[:1], corpus.weights)[0][GRID < 0].sum() * (GRID[1] - GRID[0]):.3f} "
          "electrons (expected 8)")
