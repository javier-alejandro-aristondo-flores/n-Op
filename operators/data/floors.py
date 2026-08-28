"""the physics and memorization baselines every operator must beat"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from operators.data.orbits import Orbit_Map
from operators.substrate import Cartesian_Wavevectors
from operators.data.spectra import Occupancy_Walk_Gap
from operators.data.store import POOL_ROOT, Archive_Path, CensusRow, Run_Identifier

COULOMB_CONSTANT = 14.39964

type Field = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class FunctionalPair:
    """one same-geometry cheap and accurate run pair, by store identifier"""

    point: str
    cheap_identifier: str
    accurate_identifier: str


def Load_Field(campaign: str, identifier: str, name: str, pool_root: Path = POOL_ROOT) -> Field:
    """one named field of one run, in double precision"""
    with np.load(Archive_Path(campaign, identifier, pool_root)) as archive:
        return np.asarray(archive[name], dtype=np.float64)


def Strain_Pairs(census_rows: Sequence[CensusRow]) -> tuple[FunctionalPair, ...]:
    """the strain atlas's same-geometry functional pairs"""
    by_point: dict[str, dict[str, str]] = {}
    for entry in Orbit_Map(census_rows):
        # the directory above the functional is the geometry the two runs share
        point = entry.run_path.rsplit("/", 1)[0]
        by_point.setdefault(point, {})[entry.functional] = entry.run_path
    functional_pairs: list[FunctionalPair] = []
    for point, sides in sorted(by_point.items()):
        if len(sides) == 2:
            functional_pairs.append(
                FunctionalPair(point, Run_Identifier(sides["cheap"]), Run_Identifier(sides["accurate"]))
            )
    return tuple(functional_pairs)


def Identity_And_Affine_Floors(
    functional_pairs: Sequence[FunctionalPair],
    load_charge_density: Callable[[str], Field],
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """per-pair identity errors, affine errors and affine slopes"""
    identity: list[float] = []
    affine: list[float] = []
    slopes: list[float] = []
    for functional_pair in functional_pairs:
        cheap = load_charge_density(functional_pair.cheap_identifier).ravel()
        accurate = load_charge_density(functional_pair.accurate_identifier).ravel()
        # a pair whose two runs used different grids has no pointwise comparison
        if cheap.shape != accurate.shape:
            continue
        scale = float(np.linalg.norm(accurate))
        identity.append(float(np.linalg.norm(cheap - accurate)) / scale)
        design = np.stack([cheap, np.ones_like(cheap)], axis=1)
        coefficients, *_ = np.linalg.lstsq(design, accurate, rcond=None)
        affine.append(float(np.linalg.norm(design @ coefficients - accurate)) / scale)
        slopes.append(float(coefficients[0]))
    return np.asarray(identity), np.asarray(affine), np.asarray(slopes)


def Shell_Index_Grid(shape: tuple[int, ...]) -> NDArray[np.int64]:
    """the rounded integer-mode shell radius at every full-spectrum entry"""
    # the distance to the nearest end of the axis, which is the mode's magnitude
    axes = [np.minimum(np.arange(extent), extent - np.arange(extent)) for extent in shape]
    grids = np.meshgrid(*axes, indexing="ij")
    radius = np.sqrt(sum(np.asarray(grid, dtype=np.float64) ** 2 for grid in grids))
    return np.asarray(np.rint(radius), dtype=np.int64)


def Fit_Per_Shell_Filter(
    train_inputs: Sequence[Field],
    train_targets: Sequence[Field],
) -> NDArray[np.float64]:
    """one real gain per spectral shell, by least squares over the training fields"""
    shells = Shell_Index_Grid(train_inputs[0].shape)
    shell_count = int(shells.max()) + 1
    cross = np.zeros(shell_count, dtype=np.float64)
    power = np.zeros(shell_count, dtype=np.float64)
    for input_field, target_field in zip(train_inputs, train_targets):
        input_modes = np.fft.fftn(input_field)
        target_modes = np.fft.fftn(target_field)
        # the counting sum accumulates each shell's cross term and power in one pass
        cross += np.bincount(shells.ravel(), np.real(np.conj(input_modes) * target_modes).ravel(), minlength=shell_count)
        power += np.bincount(shells.ravel(), np.abs(input_modes.ravel()) ** 2, minlength=shell_count)
    gains = np.zeros(shell_count, dtype=np.float64)
    nonzero = power > 0
    gains[nonzero] = cross[nonzero] / power[nonzero]
    return gains


def Apply_Per_Shell_Filter(gains: NDArray[np.float64], input_field: Field) -> Field:
    """a fitted per-shell gain applied to one input field"""
    shells = Shell_Index_Grid(input_field.shape)
    filtered = np.fft.fftn(input_field) * gains[shells]
    return np.real(np.fft.ifftn(filtered))


def Superposed_Atomic_Density_Errors(
    identifiers: Sequence[str],
    campaign: str,
    pool_root: Path = POOL_ROOT,
) -> NDArray[np.float64]:
    """per-run normalized error of the stored atomic superposition against the density"""
    errors: list[float] = []
    for identifier in identifiers:
        with np.load(Archive_Path(campaign, identifier, pool_root)) as archive:
            if "superposed_atomic_density" not in archive or "charge_density" not in archive:
                continue
            superposed = np.asarray(archive["superposed_atomic_density"], dtype=np.float64)
            density = np.asarray(archive["charge_density"], dtype=np.float64)
        errors.append(float(np.mean(np.abs(superposed - density)) / np.mean(np.abs(density))))
    return np.asarray(errors)


def Scissor_Floor(
    functional_pairs: Sequence[FunctionalPair],
    campaign: str,
    pool_root: Path = POOL_ROOT,
) -> dict[str, float]:
    """the gap shift and the linear-scissor residual, from stored eigenvalues"""
    cheap_gaps: list[float] = []
    accurate_gaps: list[float] = []
    for functional_pair in functional_pairs:
        gaps: list[float] = []
        for identifier in (functional_pair.cheap_identifier, functional_pair.accurate_identifier):
            with np.load(Archive_Path(campaign, identifier, pool_root)) as archive:
                if "eigenvalue_energies" not in archive:
                    break
                energies = np.asarray(archive["eigenvalue_energies"], dtype=np.float64)
                occupancies = np.asarray(archive["eigenvalue_occupancies"], dtype=np.float64)
            gaps.append(Occupancy_Walk_Gap(energies, occupancies))
        if len(gaps) == 2:
            cheap_gaps.append(gaps[0])
            accurate_gaps.append(gaps[1])
    cheap = np.asarray(cheap_gaps)
    accurate = np.asarray(accurate_gaps)
    shift = accurate - cheap
    design = np.stack([cheap, np.ones_like(cheap)], axis=1)
    coefficients, *_ = np.linalg.lstsq(design, accurate, rcond=None)
    residual = accurate - design @ coefficients
    return {
        "pair_count": float(cheap.shape[0]),
        "mean_shift": float(shift.mean()),
        "shift_deviation": float(shift.std()),
        "linear_slope": float(coefficients[0]),
        "linear_intercept": float(coefficients[1]),
        "linear_residual_deviation": float(residual.std()),
        "r_squared": float(1.0 - residual.var() / accurate.var()),
    }


def Hartree_Potential(charge_density: Field, lattice: Field) -> Field:
    """periodic Poisson solve, uniform mode pinned to zero"""
    wavevectors = Cartesian_Wavevectors(lattice, charge_density.shape)
    squared = np.sum(wavevectors**2, axis=-1)
    density_modes = np.fft.fftn(charge_density) / charge_density.size
    potential_modes = np.zeros_like(density_modes)
    # a periodic cell has no zero-mode potential, the neutralizing background cancels it
    nonzero = squared > 0
    potential_modes[nonzero] = 4.0 * np.pi * COULOMB_CONSTANT * density_modes[nonzero] / squared[nonzero]
    return np.real(np.fft.ifftn(potential_modes * charge_density.size))


def Spectral_Gradient_Magnitude_And_Laplacian(field: Field, lattice: Field) -> tuple[Field, Field]:
    """gradient magnitude and Laplacian, by spectral differentiation"""
    wavevectors = Cartesian_Wavevectors(lattice, field.shape)
    modes = np.fft.fftn(field)
    gradient_squared = np.zeros_like(field)
    for axis in range(3):
        component = np.real(np.fft.ifftn(1j * wavevectors[..., axis] * modes))
        gradient_squared = gradient_squared + component**2
    laplacian = np.real(np.fft.ifftn(-np.sum(wavevectors**2, axis=-1) * modes))
    return np.sqrt(gradient_squared), laplacian


def Ridge_Fit(features: Field, targets: Field, regularization: float = 1e-6) -> Field:
    """ridge coefficients, with an intercept column appended"""
    design = np.concatenate([features, np.ones((features.shape[0], 1))], axis=1)
    normal = design.T @ design + regularization * np.eye(design.shape[1])
    return np.asarray(np.linalg.solve(normal, design.T @ targets), dtype=np.float64)


def Ridge_Apply(coefficients: Field, features: Field) -> Field:
    """fitted ridge coefficients applied to features"""
    design = np.concatenate([features, np.ones((features.shape[0], 1))], axis=1)
    return design @ coefficients
