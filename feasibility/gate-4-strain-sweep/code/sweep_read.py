"""Readers and observables for the diamond strain sweep.

Nothing here invents a convention. The strain tensor comes from the repository's own
`physics.formulas.elastic`, which was validated by reproducing the dataset's published
C44 (570.0 against 570.5 GPa) -- that fit is what pins down the transpose in F, which is
invisible for normal strains and wrong for every sheared cell.
"""

from __future__ import annotations

import os
import re

import numpy as np

from paths import CACHE as _CACHE
from physics.formulas.elastic import green_lagrange_voigt, reference_cell

#: `paths` puts the repository on the import path, so the line above resolves whether or
#: not this is run from the repository root.
CACHE = str(_CACHE)
PBE = "1-cheap-pbe-atoms-relaxed"
HSE = "2-accurate-hse06-atoms-fixed"

EIGENVAL = "band-energies-per-kpoint.txt"
POSCAR = "input-crystal-geometry.txt"
INCAR = "calculation-settings.txt"
OSZICAR = "energy-per-iteration-summary.txt"

#: The experimental lattice constant the sweep's strains are defined about.
A_EXPERIMENTAL = 3.567


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------

def read_poscar_lattice(path: str) -> np.ndarray:
    """The 3x3 lattice, rows as vectors, with VASP's scale rule applied.

    A *negative* scale is not a multiplier: it is a target for `|det A|`, and the whole
    matrix is rescaled uniformly to hit it. Family 1 uses this form exclusively, so
    reading the scale as a multiplier would put every volume point at the wrong volume.
    """
    with open(path) as f:
        lines = f.read().splitlines()
    scale = float(lines[1].split()[0])
    matrix = np.array([[float(x) for x in lines[2 + i].split()[:3]] for i in range(3)])
    if scale < 0.0:
        matrix = matrix * (abs(scale) / abs(np.linalg.det(matrix))) ** (1.0 / 3.0)
    else:
        matrix = matrix * scale
    return matrix


def read_eigenval(path: str) -> dict:
    """k-points (fractional), weights, band energies and occupations.

    Returns arrays shaped (nk, 3), (nk,), (nk, nb), (nk, nb). Spin-restricted only --
    this sweep has `ISPIN = 2` commented out in every INCAR, and the reader asserts the
    ISPIN field on line 1 rather than trusting that.
    """
    with open(path) as f:
        raw = f.read().split("\n")

    ispin = int(raw[0].split()[3])
    if ispin != 1:
        raise ValueError(f"{path}: ISPIN={ispin}, this reader is spin-restricted")

    nelect, nk, nb = (int(x) for x in raw[5].split())

    kpts = np.empty((nk, 3))
    weights = np.empty(nk)
    energies = np.empty((nk, nb))
    occupations = np.empty((nk, nb))

    line = 6
    for ik in range(nk):
        while raw[line].strip() == "":
            line += 1
        parts = raw[line].split()
        kpts[ik] = [float(x) for x in parts[:3]]
        weights[ik] = float(parts[3])
        line += 1
        for ib in range(nb):
            parts = raw[line].split()
            energies[ik, ib] = float(parts[1])
            occupations[ik, ib] = float(parts[2])
            line += 1

    return dict(nelect=nelect, nk=nk, nb=nb, kpoints=kpts, weights=weights,
                energies=energies, occupations=occupations)


def read_incar(path: str) -> dict:
    """INCAR tags, uppercased keys, comments and commented-out lines dropped.

    A leading `#` means the tag is *not set*. The distinction matters here: every PBE
    INCAR in this sweep carries `# ISPIN = 2`, so a reader that ignored the comment
    marker would report a spin-polarized sweep that does not exist.
    """
    tags = {}
    with open(path) as f:
        for raw_line in f:
            line = raw_line.split("#")[0].split("!")[0].strip()
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            tags[key.strip().upper()] = value.strip()
    return tags


def read_oszicar_history(path: str) -> list[float]:
    """The per-iteration total energies, as the run's own fingerprint.

    Two calculations that are bit-identical copies share this exactly; two independent
    reruns of the same physics agree in the converged value but differ in the path.
    """
    out = []
    with open(path) as f:
        for line in f:
            match = re.search(r"E0=\s*([-.\dE+]+)", line)
            if match:
                out.append(float(match.group(1)))
    return out


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

REFERENCE = reference_cell(A_EXPERIMENTAL)


def strain_of(lattice: np.ndarray) -> np.ndarray:
    """Green-Lagrange strain in Voigt order, referred to the experimental cell."""
    return green_lagrange_voigt(lattice, REFERENCE)


def strain_magnitude(voigt: np.ndarray) -> float:
    """Frobenius norm of the strain tensor, shears counted once, not twice.

    The Voigt vector doubles the off-diagonal components, so summing its squares would
    over-weight shear by a factor of two relative to a true tensor norm.
    """
    normal = voigt[..., :3]
    shear = voigt[..., 3:] / 2.0
    return np.sqrt(np.sum(normal ** 2, axis=-1) + 2.0 * np.sum(shear ** 2, axis=-1))


# ---------------------------------------------------------------------------
# Observables
# ---------------------------------------------------------------------------

N_OCCUPIED = 4          # 8 electrons, spin-restricted, 2 per band
GAMMA_TOLERANCE = 1e-8


def observables(ev: dict) -> dict:
    """O1-O4 from one calculation.

    Every quantity is a difference *within* this calculation. Periodic DFT has no
    absolute energy reference across cells, so a raw eigenvalue compared between two
    differently-shaped cells means nothing.
    """
    energies = ev["energies"]
    occupations = ev["occupations"]
    kpts = ev["kpoints"]

    valence = energies[:, :N_OCCUPIED]
    conduction = energies[:, N_OCCUPIED:]

    vbm_k = int(np.argmax(valence[:, -1]))
    cbm_k = int(np.argmin(conduction[:, 0]))
    vbm = float(valence[vbm_k, -1])
    cbm = float(conduction[cbm_k, 0])

    gamma = int(np.argmin(np.sum(np.abs(kpts), axis=1)))
    if np.sum(np.abs(kpts[gamma])) > GAMMA_TOLERANCE:
        raise ValueError("no Gamma point in the mesh")

    # O3: the two gaps inside the top valence triplet at Gamma. Zero by cubic symmetry
    # at zero strain, so a nonzero value on the uniform-scaling family is pure noise.
    triplet = np.sort(energies[gamma, 1:N_OCCUPIED])
    splitting_low = float(triplet[1] - triplet[0])
    splitting_high = float(triplet[2] - triplet[1])

    # Metallicity: the band-4/band-5 split is only a gap if the occupations say so.
    partially_occupied = int(np.sum((occupations > 1e-3) & (occupations < 1.0 - 1e-3)))

    return dict(
        indirect_gap=cbm - vbm,
        direct_gap_gamma=float(energies[gamma, N_OCCUPIED] - energies[gamma, N_OCCUPIED - 1]),
        vbm=vbm,
        cbm=cbm,
        vbm_kpoint=vbm_k,
        cbm_kpoint=cbm_k,
        valence_splitting_low=splitting_low,
        valence_splitting_high=splitting_high,
        valence_splitting_total=float(triplet[2] - triplet[0]),
        partially_occupied=partially_occupied,
        # The band set is complete only below the lowest energy the topmost computed band
        # reaches; above that, bands VASP never calculated would contribute.
        complete_to=float(np.min(energies[:, -1]) - vbm),
        occupied_bandwidth=float(vbm - np.min(energies)),
    )


def valley_points(kpts: np.ndarray) -> dict:
    """Mesh points at 6/7 of the way from Gamma to each X, one per Cartesian axis.

    X sits at fractional (1/2,1/2,0) and its permutations, which an odd mesh never
    lands on; (3/7,3/7,0) is the closest sampled point along the same Delta line. These
    are *not* the valley minima -- diamond's is near 0.76 of Gamma-X -- but they lie on
    the same line, so they carry the same shear deformation potential and split the same
    way. Reported as what they are: a fixed mesh point, not a minimum.
    """
    targets = {
        "delta_z": np.array([3 / 7, 3 / 7, 0.0]),
        "delta_x": np.array([0.0, 3 / 7, 3 / 7]),
        "delta_y": np.array([3 / 7, 0.0, 3 / 7]),
    }

    def distance_to(target):
        # Minimum image in fractional space: k and k+G are the same point. Exact here,
        # because the target is itself a mesh point, so the match is at distance zero.
        difference = kpts - target
        return np.linalg.norm(difference - np.round(difference), axis=1)

    found = {}
    for name, target in targets.items():
        # Time reversal folded the grid, so only one of +/-k survives; try both.
        distance = np.minimum(distance_to(target), distance_to(-target))
        index = int(np.argmin(distance))
        # VASP prints k-points to seven significant digits, so 3/7 arrives as 0.4285714
        # and an exact-match tolerance rejects the very point it is looking for.
        if distance[index] > 1e-6:
            raise ValueError(f"{name} at {target} is not a mesh point")
        found[name] = index
    return found
