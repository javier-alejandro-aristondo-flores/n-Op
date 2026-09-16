"""the three fold-0 floors: superposed-atomic-density, reduced-salted, and nearest-structure copy"""

from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from operators.data import Apply_Standardized_Ridge, Archive_Path, Fit_Standardized_Ridge, POOL_ROOT, StandardizedRidge
from operators.deep_dft.sampling import ATOM_CENTERED_SIGMA, Drawn_Probe_Points, Trilinear_Interpolate
from operators.deep_dft.species import Structure
from operators.kernels.compact_support import Folded_Fractional_Gaps, Image_Reach, Lattice_Images
from operators.metrics import Normalized_Mean_Absolute_Error

SHELL_WIDTHS = (0.3, 0.45, 0.65, 0.9, 1.25, 1.7, 2.3, 3.0)

SHELL_IMAGE_REACH_MARGIN = 4.0

PROBES_PER_TRAINING_RUN = 1000

EVALUATION_SAMPLE_SIZE = 5000

RIDGE_SEED = 20260916


def Deep_Dft_Superposed_Atomic_Density_Errors(
    structures: tuple[Structure, ...], pool_root: Path = POOL_ROOT
) -> dict[str, float]:
    """each structure's own normalized mean absolute error of the superposed-atomic-density floor"""
    errors: dict[str, float] = {}
    for structure in structures:
        archive_path = Archive_Path(structure.campaign, structure.identifier, pool_root)
        with np.load(archive_path) as archive:
            if "superposed_atomic_density" not in archive or "charge_density" not in archive:
                continue
            superposed = np.asarray(archive["superposed_atomic_density"], dtype=np.float64)
            density = np.asarray(archive["charge_density"], dtype=np.float64)
        errors[structure.identifier] = Normalized_Mean_Absolute_Error(superposed, density)
    return errors


def Species_Shell_Features(
    fractional_points: NDArray[np.float64],
    species_symbols: tuple[str, ...],
    atom_positions: NDArray[np.float64],
    lattice: NDArray[np.float64],
    element_vocabulary: tuple[str, ...],
    widths: tuple[float, ...] = SHELL_WIDTHS,
) -> NDArray[np.float64]:
    """one ridge feature column per (element, width) pair, summed over that structure's own atoms of that element"""
    feature_count = len(element_vocabulary) * len(widths)
    features = np.zeros((fractional_points.shape[0], feature_count), dtype=np.float64)
    element_column_of = {element: position for position, element in enumerate(element_vocabulary)}
    atom_columns = np.asarray([element_column_of.get(symbol, -1) for symbol in species_symbols], dtype=np.int64)
    kept_atoms = atom_columns >= 0
    if not np.any(kept_atoms):
        return features
    kept_positions = atom_positions[kept_atoms]
    kept_columns = atom_columns[kept_atoms]
    # every atom's gap to every probe is shared across all eight widths, so it is folded once here
    gaps = Folded_Fractional_Gaps(fractional_points, kept_positions)
    for width_index, width in enumerate(widths):
        reach = Image_Reach(lattice, SHELL_IMAGE_REACH_MARGIN * width)
        images = Lattice_Images(reach)
        normalizer = (2.0 * np.pi * width * width) ** 1.5
        per_atom_density = np.zeros((fractional_points.shape[0], kept_positions.shape[0]), dtype=np.float64)
        for image in images:
            displacement = (gaps + image) @ lattice
            squared_lengths = np.sum(displacement * displacement, axis=-1)
            per_atom_density += np.exp(-0.5 * squared_lengths / (width * width)) / normalizer
        for element_position in range(len(element_vocabulary)):
            atoms_of_element = kept_columns == element_position
            if np.any(atoms_of_element):
                features[:, element_position * len(widths) + width_index] = per_atom_density[:, atoms_of_element].sum(
                    axis=1
                )
    return features


def Element_Vocabulary(structures: tuple[Structure, ...]) -> tuple[str, ...]:
    """every element the given structures carry, sorted"""
    seen: set[str] = set()
    for structure in structures:
        seen.update(structure.species_symbols)
    return tuple(sorted(seen))


class SaltedFloor:
    """the fitted reduced-salted ridge, applied to fresh structures at chosen points"""


    def __init__(self, fitted: StandardizedRidge, element_vocabulary: tuple[str, ...]) -> None:
        self.fitted = fitted
        self.element_vocabulary = element_vocabulary


    def Predicted_Correction(
        self,
        fractional_points: NDArray[np.float64],
        species_symbols: tuple[str, ...],
        atom_positions: NDArray[np.float64],
        lattice: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        """the ridge's own correction to the atomic superposition, at the given points"""
        features = Species_Shell_Features(
            fractional_points, species_symbols, atom_positions, lattice, self.element_vocabulary
        )
        return Apply_Standardized_Ridge(self.fitted, features)


def Fitted_Salted_Floor(
    training_structures: tuple[Structure, ...],
    element_vocabulary: tuple[str, ...],
    pool_root: Path = POOL_ROOT,
    probes_per_run: int = PROBES_PER_TRAINING_RUN,
    seed: int = RIDGE_SEED,
) -> SaltedFloor:
    """the standardized ridge from per-species gaussian shells onto density minus the atomic superposition"""
    generator = np.random.default_rng(seed)
    feature_rows: list[NDArray[np.float64]] = []
    target_rows: list[NDArray[np.float64]] = []
    for structure in training_structures:
        archive_path = Archive_Path(structure.campaign, structure.identifier, pool_root)
        if not archive_path.exists():
            continue
        with np.load(archive_path) as archive:
            if "superposed_atomic_density" not in archive or "charge_density" not in archive:
                continue
            superposed = np.asarray(archive["superposed_atomic_density"], dtype=np.float64)
            density = np.asarray(archive["charge_density"], dtype=np.float64)
        points, _ = Drawn_Probe_Points(
            structure.positions, structure.lattice, probes_per_run, ATOM_CENTERED_SIGMA, generator
        )
        features = Species_Shell_Features(
            points, structure.species_symbols, structure.positions, structure.lattice, element_vocabulary
        )
        superposed_at_points = Trilinear_Interpolate(superposed[:, :, :, None], points)[:, 0]
        density_at_points = Trilinear_Interpolate(density[:, :, :, None], points)[:, 0]
        feature_rows.append(features)
        target_rows.append(density_at_points - superposed_at_points)
    fitted = Fit_Standardized_Ridge(np.concatenate(feature_rows), np.concatenate(target_rows))
    return SaltedFloor(fitted, element_vocabulary)


def Evaluation_Points(
    grid_shape: tuple[int, int, int], sample_size: int, generator: np.random.Generator
) -> NDArray[np.float64]:
    """a fixed random subsample of a grid's own fractional coordinates"""
    axes = [np.arange(extent, dtype=np.float64) / extent for extent in grid_shape]
    grids = np.meshgrid(*axes, indexing="ij")
    all_points = np.stack([grid.reshape(-1) for grid in grids], axis=1)
    chosen = generator.choice(all_points.shape[0], size=min(sample_size, all_points.shape[0]), replace=False)
    return all_points[chosen]


def Salted_Floor_Errors(
    salted_floor: SaltedFloor,
    structures: tuple[Structure, ...],
    pool_root: Path = POOL_ROOT,
    sample_size: int = EVALUATION_SAMPLE_SIZE,
    seed: int = RIDGE_SEED,
) -> dict[str, float]:
    """each structure's own normalized mean absolute error of the reduced-salted floor, on a fixed point sample"""
    generator = np.random.default_rng(seed)
    errors: dict[str, float] = {}
    for structure in structures:
        archive_path = Archive_Path(structure.campaign, structure.identifier, pool_root)
        if not archive_path.exists():
            continue
        with np.load(archive_path) as archive:
            if "superposed_atomic_density" not in archive or "charge_density" not in archive:
                continue
            superposed = np.asarray(archive["superposed_atomic_density"], dtype=np.float64)
            density = np.asarray(archive["charge_density"], dtype=np.float64)
        points = Evaluation_Points(density.shape, sample_size, generator)
        correction = salted_floor.Predicted_Correction(
            points, structure.species_symbols, structure.positions, structure.lattice
        )
        superposed_at_points = Trilinear_Interpolate(superposed[:, :, :, None], points)[:, 0]
        density_at_points = Trilinear_Interpolate(density[:, :, :, None], points)[:, 0]
        predicted = superposed_at_points + correction
        errors[structure.identifier] = Normalized_Mean_Absolute_Error(predicted, density_at_points)
    return errors


def Composition_Vector(structure: Structure, element_vocabulary: tuple[str, ...]) -> NDArray[np.float64]:
    """one count per vocabulary element, how many of that element the structure carries"""
    counts = np.zeros(len(element_vocabulary), dtype=np.float64)
    index_of = {element: position for position, element in enumerate(element_vocabulary)}
    for symbol in structure.species_symbols:
        if symbol in index_of:
            counts[index_of[symbol]] += 1.0
    return counts


def Nearest_Copy_Errors(
    training_structures: tuple[Structure, ...],
    evaluation_structures: tuple[Structure, ...],
    pool_root: Path = POOL_ROOT,
) -> dict[str, float]:
    """each evaluation structure scored by copying the charge density of its nearest training structure"""
    element_vocabulary = Element_Vocabulary(training_structures + evaluation_structures)
    train_vectors = np.stack(
        [Composition_Vector(structure, element_vocabulary) for structure in training_structures]
    )
    errors: dict[str, float] = {}
    for structure in evaluation_structures:
        archive_path = Archive_Path(structure.campaign, structure.identifier, pool_root)
        if not archive_path.exists():
            continue
        with np.load(archive_path) as archive:
            if "charge_density" not in archive:
                continue
            truth = np.asarray(archive["charge_density"], dtype=np.float64)
        query_vector = Composition_Vector(structure, element_vocabulary)
        distances = np.linalg.norm(train_vectors - query_vector[None, :], axis=1)
        nearest_structure = training_structures[int(np.argmin(distances))]
        nearest_path = Archive_Path(nearest_structure.campaign, nearest_structure.identifier, pool_root)
        with np.load(nearest_path) as archive:
            if "charge_density" not in archive or archive["charge_density"].shape != truth.shape:
                continue
            copied = np.asarray(archive["charge_density"], dtype=np.float64)
        errors[structure.identifier] = Normalized_Mean_Absolute_Error(copied, truth)
    return errors


def Total_Moment(magnetization_grid: NDArray[np.float64], cell_volume: float) -> float:
    """the signed integral of a magnetization field over the cell"""
    return float(np.mean(magnetization_grid)) * cell_volume


def Moment_Gate_Row(
    predicted_totals: NDArray[np.float64], true_totals: NDArray[np.float64], tolerance: float = 0.05
) -> dict[str, float]:
    """gate c: the fraction of runs whose predicted total moment sits within tolerance and carries the true sign"""
    relative_error = np.abs(predicted_totals - true_totals) / np.abs(true_totals)
    correct_sign = np.sign(predicted_totals) == np.sign(true_totals)
    passed = (relative_error <= tolerance) & correct_sign
    return {
        "pass_fraction": float(np.mean(passed)),
        "run_count": float(true_totals.shape[0]),
        "median_relative_error": float(np.median(relative_error)),
    }
