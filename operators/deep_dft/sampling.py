"""the probe sampler: mixed uniform and atom-centered draws, de-biased, with trilinear targets"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from operators.data import Archive_Path, POOL_ROOT
from operators.deep_dft.species import SpeciesKeys, Structure
from operators.encoders import AtomEmbedding
from operators.framework import Array
from operators.kernels.compact_support import Folded_Fractional_Gaps, Image_Reach, Lattice_Images
from operators.training import BatchSource, TrainingBatch

ATOM_CENTERED_SIGMA = 0.7

GAUSSIAN_IMAGE_REACH_MARGIN = 5.0

ABSOLUTE_MOMENT_FLOOR = 1e-6


def Trilinear_Interpolate(
    grid_values: NDArray[np.float64], fractional_points: NDArray[np.float64]
) -> NDArray[np.float64]:
    """periodic trilinear interpolation of a channel-last grid at fractional points"""
    grid_shape = np.asarray(grid_values.shape[:3], dtype=np.int64)
    scaled = np.asarray(fractional_points, dtype=np.float64) * grid_shape.astype(np.float64)
    base = np.floor(scaled).astype(np.int64)
    fraction = scaled - base
    channel_count = grid_values.shape[3]
    accumulated = np.zeros((fractional_points.shape[0], channel_count), dtype=np.float64)
    for corner_x in (0, 1):
        for corner_y in (0, 1):
            for corner_z in (0, 1):
                offset = np.asarray([corner_x, corner_y, corner_z], dtype=np.int64)
                corner_index = (base + offset) % grid_shape
                weight = np.prod(np.where(offset[None, :] == 1, fraction, 1.0 - fraction), axis=1)
                gathered = grid_values[corner_index[:, 0], corner_index[:, 1], corner_index[:, 2]]
                accumulated += weight[:, None] * gathered
    return accumulated


def Gaussian_Density_3d(displacements: NDArray[np.float64], sigma: float) -> NDArray[np.float64]:
    """the isotropic three-dimensional normal density at the given cartesian displacements"""
    squared_lengths = np.sum(displacements * displacements, axis=-1)
    normalizer = (2.0 * np.pi * sigma * sigma) ** 1.5
    return np.exp(-0.5 * squared_lengths / (sigma * sigma)) / normalizer


def Atom_Centered_Component_Density(
    fractional_points: NDArray[np.float64],
    atom_positions: NDArray[np.float64],
    lattice: NDArray[np.float64],
    sigma: float,
) -> NDArray[np.float64]:
    """the atom-centered proposal's own cartesian density, periodic images summed"""
    atom_count = atom_positions.shape[0]
    reach = Image_Reach(lattice, GAUSSIAN_IMAGE_REACH_MARGIN * sigma)
    images = Lattice_Images(reach)
    gaps = Folded_Fractional_Gaps(fractional_points, atom_positions)
    density = np.zeros(fractional_points.shape[0], dtype=np.float64)
    for image in images:
        displacement = (gaps + image) @ lattice
        density += Gaussian_Density_3d(displacement, sigma).sum(axis=1)
    return density / atom_count


def Mixture_Proposal_Density(
    fractional_points: NDArray[np.float64],
    atom_positions: NDArray[np.float64],
    lattice: NDArray[np.float64],
    sigma: float,
) -> NDArray[np.float64]:
    """the cartesian density of the half-uniform, half-atom-centered probe proposal"""
    cell_volume = float(abs(np.linalg.det(lattice)))
    uniform_component = 1.0 / cell_volume
    atom_component = Atom_Centered_Component_Density(fractional_points, atom_positions, lattice, sigma)
    return 0.5 * uniform_component + 0.5 * atom_component


def Drawn_Probe_Points(
    atom_positions: NDArray[np.float64],
    lattice: NDArray[np.float64],
    probe_count: int,
    sigma: float,
    generator: np.random.Generator,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """probe fractional points, half uniform and half atom-centered, with their inverse-proposal weights"""
    uniform_count = probe_count // 2
    atom_centered_count = probe_count - uniform_count
    uniform_points = generator.random((uniform_count, 3))
    chosen_atoms = generator.integers(0, atom_positions.shape[0], size=atom_centered_count)
    cartesian_offsets = generator.normal(0.0, sigma, size=(atom_centered_count, 3))
    fractional_offsets = cartesian_offsets @ np.linalg.inv(lattice)
    atom_centered_points = (atom_positions[chosen_atoms] + fractional_offsets) % 1.0
    points = np.concatenate([uniform_points, atom_centered_points], axis=0)
    density = Mixture_Proposal_Density(points, atom_positions, lattice, sigma)
    weights = 1.0 / density
    return points, weights


@dataclass(frozen=True, slots=True)
class CachedDeepDftStructure:
    """one structure's fixed arrays, ready for repeated probe draws"""

    identifier: str
    lattice: NDArray[np.float64]
    atom_positions: NDArray[np.float64]
    atom_vocabulary_index: NDArray[np.int64]
    density_grid: NDArray[np.float64]
    magnetization_grid: NDArray[np.float64] | None
    absolute_moment: float
    electron_count: float


def Cached_Structure(
    structure: Structure, species_keys: SpeciesKeys, encoder: AtomEmbedding, pool_root: Path = POOL_ROOT
) -> CachedDeepDftStructure | None:
    """one structure's grids read off the store and its atoms keyed against the training vocabulary"""
    archive_path = Archive_Path(structure.campaign, structure.identifier, pool_root)
    if not archive_path.exists():
        return None
    with np.load(archive_path) as archive:
        if "charge_density" not in archive:
            return None
        density_grid = np.asarray(archive["charge_density"], dtype=np.float64)
        magnetization_grid: NDArray[np.float64] | None = None
        if "magnetization_density" in archive:
            candidate = np.asarray(archive["magnetization_density"], dtype=np.float64)
            cell_volume = float(abs(np.linalg.det(structure.lattice)))
            absolute_moment = float(np.mean(np.abs(candidate))) * cell_volume
            if absolute_moment > ABSOLUTE_MOMENT_FLOOR:
                magnetization_grid = candidate
            else:
                absolute_moment = 1.0
        else:
            absolute_moment = 1.0
    resolved_keys = species_keys.Resolved(structure.species_keys)
    vocabulary_indices = encoder.Vocabulary_Indices(np.asarray(resolved_keys))
    return CachedDeepDftStructure(
        identifier=structure.identifier,
        lattice=structure.lattice,
        atom_positions=structure.positions,
        atom_vocabulary_index=vocabulary_indices,
        density_grid=density_grid,
        magnetization_grid=magnetization_grid,
        absolute_moment=absolute_moment,
        electron_count=structure.electron_count,
    )


def Structure_Batch(
    structures: tuple[CachedDeepDftStructure, ...],
    probes_per_structure: int,
    sigma: float,
    generator: np.random.Generator,
) -> TrainingBatch:
    """one rectangular batch of probes and their trilinear targets, atoms padded to the widest structure"""
    max_atom_count = max(structure.atom_positions.shape[0] for structure in structures)
    structure_count = len(structures)
    atom_positions = np.zeros((structure_count, max_atom_count, 3), dtype=np.float64)
    atom_vocabulary_index = np.zeros((structure_count, max_atom_count), dtype=np.float64)
    atom_count = np.zeros(structure_count, dtype=np.float64)
    lattice = np.zeros((structure_count, 3, 3), dtype=np.float64)
    probe_positions = np.zeros((structure_count, probes_per_structure, 3), dtype=np.float64)
    probe_weights = np.zeros((structure_count, probes_per_structure), dtype=np.float64)
    probe_target_density = np.zeros((structure_count, probes_per_structure), dtype=np.float64)
    probe_target_magnetization = np.zeros((structure_count, probes_per_structure), dtype=np.float64)
    has_magnetization = np.zeros(structure_count, dtype=np.float64)
    absolute_moment = np.ones(structure_count, dtype=np.float64)
    electron_count = np.zeros(structure_count, dtype=np.float64)
    for structure_index, structure in enumerate(structures):
        this_atom_count = structure.atom_positions.shape[0]
        atom_positions[structure_index, :this_atom_count] = structure.atom_positions
        atom_vocabulary_index[structure_index, :this_atom_count] = structure.atom_vocabulary_index
        atom_count[structure_index] = this_atom_count
        lattice[structure_index] = structure.lattice
        electron_count[structure_index] = structure.electron_count
        points, weights = Drawn_Probe_Points(
            structure.atom_positions, structure.lattice, probes_per_structure, sigma, generator
        )
        probe_positions[structure_index] = points
        probe_weights[structure_index] = weights
        density_channel = structure.density_grid[:, :, :, None]
        probe_target_density[structure_index] = Trilinear_Interpolate(density_channel, points)[:, 0]
        if structure.magnetization_grid is not None:
            has_magnetization[structure_index] = 1.0
            absolute_moment[structure_index] = structure.absolute_moment
            magnetization_channel = structure.magnetization_grid[:, :, :, None]
            probe_target_magnetization[structure_index] = Trilinear_Interpolate(magnetization_channel, points)[:, 0]
    return TrainingBatch(
        arrays={
            "atom_positions": atom_positions,
            "atom_vocabulary_index": atom_vocabulary_index,
            "atom_count": atom_count,
            "lattice": lattice,
            "probe_positions": probe_positions,
            "probe_weights": probe_weights,
            "probe_target_density": probe_target_density,
            "probe_target_magnetization": probe_target_magnetization,
            "has_magnetization": has_magnetization,
            "absolute_moment": absolute_moment,
            "electron_count": electron_count,
        }
    )


class ProbeBatchSource(BatchSource):
    """probe minibatches drawn fresh from cached structures, mixture-sampled and de-biased"""


    def __init__(
        self,
        training_structures: tuple[CachedDeepDftStructure, ...],
        validation_structures: tuple[CachedDeepDftStructure, ...],
        structures_per_batch: int = 2,
        probes_per_structure: int = 1000,
        validation_probes_per_structure: int = 2000,
        atom_centered_sigma: float = ATOM_CENTERED_SIGMA,
        validation_seed: int = 20260916,
    ) -> None:
        if not training_structures:
            raise ValueError("the probe sampler needs at least one training structure to draw from")
        self.training_structures = training_structures
        self.validation_structures = validation_structures
        self.structures_per_batch = structures_per_batch
        self.probes_per_structure = probes_per_structure
        self.atom_centered_sigma = atom_centered_sigma
        self.last_batch: TrainingBatch | None = None
        self.validation_batches: tuple[tuple[str, TrainingBatch], ...] = tuple(
            (
                structure.identifier,
                Structure_Batch(
                    (structure,),
                    validation_probes_per_structure,
                    atom_centered_sigma,
                    np.random.default_rng((validation_seed, structure_index)),
                ),
            )
            for structure_index, structure in enumerate(validation_structures)
        )


    def Next_Batch(self, generator: np.random.Generator) -> TrainingBatch:
        """a fresh draw of structures and probes, the generator spent so a seed reproduces the run"""
        drawn_indices = generator.integers(0, len(self.training_structures), size=self.structures_per_batch)
        drawn = tuple(self.training_structures[int(drawn_index)] for drawn_index in drawn_indices)
        batch = Structure_Batch(drawn, self.probes_per_structure, self.atom_centered_sigma, generator)
        self.last_batch = batch
        return batch


    def Validation_Batches(self) -> tuple[tuple[str, TrainingBatch], ...]:
        """one fixed batch per held-out structure, drawn once at construction with its own seed"""
        return self.validation_batches


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = {
            "training_structure_count": np.asarray(len(self.training_structures)),
            "validation_structure_count": np.asarray(len(self.validation_structures)),
            "probes_per_structure": np.asarray(self.probes_per_structure),
            "atom_centered_sigma": np.asarray(self.atom_centered_sigma),
        }
        if self.last_batch is not None:
            for name, array in self.last_batch.Inspect().items():
                state[f"last_{name}"] = array
        return state
