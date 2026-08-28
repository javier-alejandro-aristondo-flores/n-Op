"""Measurement of how far an operator's output moves when its discretization changes."""

from collections.abc import Callable
from itertools import permutations, product

import numpy as np

from numpy.typing import NDArray

from operators.framework.operator import Operator
from operators.framework.representation import Representation
from operators.tasks import TaskCard


def Spectral_Truncation_Resample(values: NDArray[np.float64], target_shape: tuple[int, int, int]) -> NDArray[np.float64]:
    """Resamples channel fields between grids by exact Fourier truncation or zero-padding."""
    stacked = np.asarray(values, dtype=np.float64)
    spectrum = np.fft.fftn(stacked, axes=(1, 2, 3))
    result = np.zeros((stacked.shape[0], *target_shape), dtype=np.complex128)
    source_index: list[NDArray[np.int64]] = []
    target_index: list[NDArray[np.int64]] = []
    for source_extent, target_extent in zip(stacked.shape[1:], target_shape):
        largest_kept_mode = (min(source_extent, target_extent) - 1) // 2
        modes = np.arange(-largest_kept_mode, largest_kept_mode + 1, dtype=np.int64)
        source_index.append(np.mod(modes, source_extent))
        target_index.append(np.mod(modes, target_extent))
    channel_index = np.arange(stacked.shape[0], dtype=np.int64)
    result[np.ix_(channel_index, *target_index)] = spectrum[np.ix_(channel_index, *source_index)]
    scale = float(np.prod(target_shape)) / float(np.prod(stacked.shape[1:]))
    return np.real(np.fft.ifftn(result, axes=(1, 2, 3))) * scale


def Diamond_Conventional_Motif() -> tuple[tuple[float, float, float], ...]:
    """Returns the eight diamond positions of the conventional cubic cell."""
    centering = ((0.0, 0.0, 0.0), (0.0, 0.5, 0.5), (0.5, 0.0, 0.5), (0.5, 0.5, 0.0))
    positions: list[tuple[float, float, float]] = []
    for base in ((0.0, 0.0, 0.0), (0.25, 0.25, 0.25)):
        for offset in centering:
            combined = [float((base_component + offset_component) % 1.0) for base_component, offset_component in zip(base, offset)]
            positions.append((combined[0], combined[1], combined[2]))
    return tuple(positions)


def Diamond_Grid_Operations() -> tuple[tuple[NDArray[np.int64], NDArray[np.float64]], ...]:
    """Returns the 48 signed permutations with the fractional translation each needs."""
    motif = {tuple(np.round(position, 6)) for position in Diamond_Conventional_Motif()}
    candidate_translations = [np.asarray(position, dtype=np.float64) for position in Diamond_Conventional_Motif()]
    operations: list[tuple[NDArray[np.int64], NDArray[np.float64]]] = []
    for permutation in permutations((0, 1, 2)):
        for signs in product((1, -1), repeat=3):
            matrix = np.zeros((3, 3), dtype=np.int64)
            for output_axis, (input_axis, sign) in enumerate(zip(permutation, signs)):
                matrix[output_axis, input_axis] = sign
            for translation in candidate_translations:
                mapped = {
                    tuple(np.mod(matrix @ np.asarray(atom) + translation, 1.0).round(6)) for atom in motif
                }
                if mapped == motif:
                    operations.append((matrix, translation))
                    break
    return tuple(operations)


def Apply_Grid_Operation(values: NDArray[np.float64], matrix: NDArray[np.int64], translation: NDArray[np.float64]) -> NDArray[np.float64]:
    """Applies one exact symmetry operation to channel fields on a compatible cubic grid."""
    stacked = np.asarray(values)
    extent = stacked.shape[1]
    grid = np.indices((extent, extent, extent)).reshape(3, -1)
    shifts = np.asarray(np.asarray(translation, dtype=np.float64) * extent + 0.5, dtype=np.int64).reshape(3, 1)
    inverse = np.asarray(matrix, dtype=np.int64).T
    source = np.mod(inverse @ (grid - shifts), extent)
    gathered = stacked[:, source[0], source[1], source[2]]
    return gathered.reshape(stacked.shape)


def Equivariance_Errors(
    apply_model: Callable[[NDArray[np.float64]], NDArray[np.float64]],
    values: NDArray[np.float64],
    operations: tuple[tuple[NDArray[np.int64], NDArray[np.float64]], ...],
) -> NDArray[np.float64]:
    """Returns the relative equivariance error of a model under each operation."""
    base_output = np.asarray(apply_model(values), dtype=np.float64)
    scale = np.linalg.norm(base_output.ravel())
    errors: list[float] = []
    for matrix, translation in operations:
        transformed_input = Apply_Grid_Operation(values, matrix, translation)
        output_of_transformed = np.asarray(apply_model(transformed_input), dtype=np.float64)
        transformed_output = Apply_Grid_Operation(base_output, matrix, translation)
        errors.append(float(np.linalg.norm((output_of_transformed - transformed_output).ravel()) / scale))
    return np.asarray(errors, dtype=np.float64)


def Block_Gap_Null(primitive_values: NDArray[np.float64], supercell_values: NDArray[np.float64], tiles: tuple[int, int, int]) -> float:
    """Returns the relative distance between the tiled primitive truth and the supercell truth."""
    primitive = np.asarray(primitive_values, dtype=np.float64)
    supercell = np.asarray(supercell_values, dtype=np.float64)
    tiled = np.tile(primitive, (1, *tiles))
    if tiled.shape != supercell.shape:
        tiled = Spectral_Truncation_Resample(tiled, supercell.shape[1:])
    difference = np.linalg.norm((tiled - supercell).ravel())
    return float(difference / np.linalg.norm(supercell.ravel()))


def K_Quality_Tier(irreducible_kpoint_count: int) -> str:
    """Names the spectral-label quality tier an irreducible k-point count earns."""
    if irreducible_kpoint_count >= 64:
        return "high_fidelity"
    if irreducible_kpoint_count >= 50:
        return "recommended"
    if irreducible_kpoint_count >= 27:
        return "permissive"
    return "below_gate"


def Discretization_Invariance_Report(operator: Operator[Representation, Representation], task: TaskCard) -> dict[str, object]:
    """Runs every invariance axis that applies to one operator on one task card."""
    raise NotImplementedError
