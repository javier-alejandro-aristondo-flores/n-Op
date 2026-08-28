"""The floor suite: the physics and memorization baselines every operator must beat."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy
from numpy.typing import NDArray

from operators.data.orbits import Orbit_Map
from operators.data.spectra import Occupancy_Walk_Gap
from operators.data.store import POOL_ROOT, CensusRow, Run_Identifier

COULOMB_CONSTANT = 14.39964

type Field = NDArray[numpy.float64]


@dataclass(frozen=True, slots=True)
class FunctionalPair:
    """One same-geometry cheap and accurate run pair with its store identifiers."""

    point: str
    cheap_identifier: str
    accurate_identifier: str


def Archive_Path(campaign: str, identifier: str, pool_root: Path = POOL_ROOT) -> Path:
    """Returns the store archive path of one run."""
    return pool_root / "_derived" / campaign / f"{identifier}.npz"


def Load_Field(campaign: str, identifier: str, name: str, pool_root: Path = POOL_ROOT) -> Field:
    """Loads one named field of one run as float64."""
    with numpy.load(Archive_Path(campaign, identifier, pool_root)) as archive:
        return numpy.asarray(archive[name], dtype=numpy.float64)


def Strain_Pairs(census_rows: Sequence[CensusRow]) -> tuple[FunctionalPair, ...]:
    """Returns the strain atlas's same-geometry functional pairs."""
    by_point: dict[str, dict[str, str]] = {}
    for entry in Orbit_Map(census_rows):
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
) -> tuple[NDArray[numpy.float64], NDArray[numpy.float64], NDArray[numpy.float64]]:
    """Returns per-pair identity errors, affine errors, and affine slopes."""
    identity: list[float] = []
    affine: list[float] = []
    slopes: list[float] = []
    for functional_pair in functional_pairs:
        cheap = load_charge_density(functional_pair.cheap_identifier).ravel()
        accurate = load_charge_density(functional_pair.accurate_identifier).ravel()
        if cheap.shape != accurate.shape:
            continue
        scale = float(numpy.linalg.norm(accurate))
        identity.append(float(numpy.linalg.norm(cheap - accurate)) / scale)
        design = numpy.stack([cheap, numpy.ones_like(cheap)], axis=1)
        coefficients, *_ = numpy.linalg.lstsq(design, accurate, rcond=None)
        affine.append(float(numpy.linalg.norm(design @ coefficients - accurate)) / scale)
        slopes.append(float(coefficients[0]))
    return numpy.asarray(identity), numpy.asarray(affine), numpy.asarray(slopes)


def Shell_Index_Grid(shape: tuple[int, ...]) -> NDArray[numpy.int64]:
    """Returns the rounded integer-mode shell radius at every full-spectrum entry."""
    axes = [numpy.minimum(numpy.arange(extent), extent - numpy.arange(extent)) for extent in shape]
    grids = numpy.meshgrid(*axes, indexing="ij")
    radius = numpy.sqrt(sum(numpy.asarray(grid, dtype=numpy.float64) ** 2 for grid in grids))
    return numpy.asarray(numpy.rint(radius), dtype=numpy.int64)


def Fit_Per_Shell_Filter(
    train_inputs: Sequence[Field],
    train_targets: Sequence[Field],
) -> NDArray[numpy.float64]:
    """Fits one real gain per spectral shell by least squares over the training fields."""
    shells = Shell_Index_Grid(train_inputs[0].shape)
    shell_count = int(shells.max()) + 1
    cross = numpy.zeros(shell_count, dtype=numpy.float64)
    power = numpy.zeros(shell_count, dtype=numpy.float64)
    for input_field, target_field in zip(train_inputs, train_targets):
        input_modes = numpy.fft.fftn(input_field)
        target_modes = numpy.fft.fftn(target_field)
        cross += numpy.bincount(shells.ravel(), numpy.real(numpy.conj(input_modes) * target_modes).ravel(), minlength=shell_count)
        power += numpy.bincount(shells.ravel(), numpy.abs(input_modes.ravel()) ** 2, minlength=shell_count)
    gains = numpy.zeros(shell_count, dtype=numpy.float64)
    nonzero = power > 0
    gains[nonzero] = cross[nonzero] / power[nonzero]
    return gains


def Apply_Per_Shell_Filter(gains: NDArray[numpy.float64], input_field: Field) -> Field:
    """Applies a fitted per-shell gain to one input field."""
    shells = Shell_Index_Grid(input_field.shape)
    filtered = numpy.fft.fftn(input_field) * gains[shells]
    return numpy.real(numpy.fft.ifftn(filtered))


def Superposed_Atomic_Density_Errors(
    identifiers: Sequence[str],
    campaign: str,
    pool_root: Path = POOL_ROOT,
) -> NDArray[numpy.float64]:
    """Returns per-run normalized errors of the stored atomic superposition against the density."""
    errors: list[float] = []
    for identifier in identifiers:
        with numpy.load(Archive_Path(campaign, identifier, pool_root)) as archive:
            if "superposed_atomic_density" not in archive or "charge_density" not in archive:
                continue
            superposed = numpy.asarray(archive["superposed_atomic_density"], dtype=numpy.float64)
            density = numpy.asarray(archive["charge_density"], dtype=numpy.float64)
        errors.append(float(numpy.mean(numpy.abs(superposed - density)) / numpy.mean(numpy.abs(density))))
    return numpy.asarray(errors)


def Scissor_Floor(
    functional_pairs: Sequence[FunctionalPair],
    campaign: str,
    pool_root: Path = POOL_ROOT,
) -> dict[str, float]:
    """Recomputes the gap shift and the linear-scissor residual from stored eigenvalues."""
    cheap_gaps: list[float] = []
    accurate_gaps: list[float] = []
    for functional_pair in functional_pairs:
        gaps: list[float] = []
        for identifier in (functional_pair.cheap_identifier, functional_pair.accurate_identifier):
            with numpy.load(Archive_Path(campaign, identifier, pool_root)) as archive:
                if "eigenvalue_energies" not in archive:
                    break
                energies = numpy.asarray(archive["eigenvalue_energies"], dtype=numpy.float64)
                occupancies = numpy.asarray(archive["eigenvalue_occupancies"], dtype=numpy.float64)
            gaps.append(Occupancy_Walk_Gap(energies, occupancies))
        if len(gaps) == 2:
            cheap_gaps.append(gaps[0])
            accurate_gaps.append(gaps[1])
    cheap = numpy.asarray(cheap_gaps)
    accurate = numpy.asarray(accurate_gaps)
    shift = accurate - cheap
    design = numpy.stack([cheap, numpy.ones_like(cheap)], axis=1)
    coefficients, *_ = numpy.linalg.lstsq(design, accurate, rcond=None)
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


def Reciprocal_Rows(lattice: Field) -> Field:
    """Returns the reciprocal lattice vectors as rows, in inverse angstrom times two pi."""
    return numpy.asarray(2.0 * numpy.pi * numpy.linalg.inv(lattice).T, dtype=numpy.float64)


def Centered_Modes(extent: int) -> NDArray[numpy.int64]:
    """Returns each spectral index as its signed centered mode number."""
    indices = numpy.arange(extent, dtype=numpy.int64)
    return numpy.where(indices <= extent // 2, indices, indices - extent)


def Cartesian_Wavevectors(lattice: Field, shape: tuple[int, ...]) -> Field:
    """Returns the Cartesian wavevector at every full-spectrum entry."""
    reciprocal = Reciprocal_Rows(lattice)
    modes = numpy.meshgrid(*[Centered_Modes(extent) for extent in shape], indexing="ij")
    stacked = numpy.stack([numpy.asarray(grid, dtype=numpy.float64) for grid in modes], axis=-1)
    return stacked @ reciprocal


def Hartree_Potential(charge_density: Field, lattice: Field) -> Field:
    """Solves the periodic Poisson equation spectrally, pinning the uniform mode to zero."""
    wavevectors = Cartesian_Wavevectors(lattice, charge_density.shape)
    squared = numpy.sum(wavevectors**2, axis=-1)
    density_modes = numpy.fft.fftn(charge_density) / charge_density.size
    potential_modes = numpy.zeros_like(density_modes)
    nonzero = squared > 0
    potential_modes[nonzero] = 4.0 * numpy.pi * COULOMB_CONSTANT * density_modes[nonzero] / squared[nonzero]
    return numpy.real(numpy.fft.ifftn(potential_modes * charge_density.size))


def Spectral_Gradient_Magnitude_And_Laplacian(field: Field, lattice: Field) -> tuple[Field, Field]:
    """Returns the gradient magnitude and the Laplacian by spectral differentiation."""
    wavevectors = Cartesian_Wavevectors(lattice, field.shape)
    modes = numpy.fft.fftn(field)
    gradient_squared = numpy.zeros_like(field)
    for axis in range(3):
        component = numpy.real(numpy.fft.ifftn(1j * wavevectors[..., axis] * modes))
        gradient_squared = gradient_squared + component**2
    laplacian = numpy.real(numpy.fft.ifftn(-numpy.sum(wavevectors**2, axis=-1) * modes))
    return numpy.sqrt(gradient_squared), laplacian


def Ridge_Fit(features: Field, targets: Field, regularization: float = 1e-6) -> Field:
    """Fits ridge coefficients with an intercept column appended."""
    design = numpy.concatenate([features, numpy.ones((features.shape[0], 1))], axis=1)
    normal = design.T @ design + regularization * numpy.eye(design.shape[1])
    return numpy.asarray(numpy.linalg.solve(normal, design.T @ targets), dtype=numpy.float64)


def Ridge_Apply(coefficients: Field, features: Field) -> Field:
    """Applies fitted ridge coefficients to features."""
    design = numpy.concatenate([features, numpy.ones((features.shape[0], 1))], axis=1)
    return design @ coefficients
