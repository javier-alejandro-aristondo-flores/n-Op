"""Measurement of how far an operator's output moves when its discretization changes."""

from collections.abc import Callable
from itertools import permutations, product

import numpy

from operators.framework.domain import Array
from operators.framework.operator import Operator
from operators.framework.representation import Representation
from operators.tasks import TaskCard


def Spectral_Truncation_Resample(values: Array, target_shape: tuple[int, int, int]) -> Array:
    """Resamples channel fields between grids by exact Fourier truncation or zero-padding."""
    stacked = numpy.asarray(values, dtype=numpy.float64)
    spectrum = numpy.fft.fftn(stacked, axes=(1, 2, 3))
    result = numpy.zeros((stacked.shape[0], *target_shape), dtype=numpy.complex128)
    source_index: list[Array] = []
    target_index: list[Array] = []
    for source_extent, target_extent in zip(stacked.shape[1:], target_shape):
        largest_kept_mode = (min(source_extent, target_extent) - 1) // 2
        modes = numpy.arange(-largest_kept_mode, largest_kept_mode + 1, dtype=numpy.int64)
        source_index.append(numpy.mod(modes, source_extent))
        target_index.append(numpy.mod(modes, target_extent))
    channel_index = numpy.arange(stacked.shape[0], dtype=numpy.int64)
    result[numpy.ix_(channel_index, *target_index)] = spectrum[numpy.ix_(channel_index, *source_index)]
    scale = float(numpy.prod(target_shape)) / float(numpy.prod(stacked.shape[1:]))
    return numpy.real(numpy.fft.ifftn(result, axes=(1, 2, 3))) * scale


def Diamond_Conventional_Motif() -> tuple[tuple[float, float, float], ...]:
    """Returns the eight diamond positions of the conventional cubic cell."""
    centering = ((0.0, 0.0, 0.0), (0.0, 0.5, 0.5), (0.5, 0.0, 0.5), (0.5, 0.5, 0.0))
    positions: list[tuple[float, float, float]] = []
    for base in ((0.0, 0.0, 0.0), (0.25, 0.25, 0.25)):
        for offset in centering:
            combined = [float((base_component + offset_component) % 1.0) for base_component, offset_component in zip(base, offset)]
            positions.append((combined[0], combined[1], combined[2]))
    return tuple(positions)


def Diamond_Grid_Operations() -> tuple[tuple[Array, Array], ...]:
    """Returns the 48 signed permutations with the fractional translation each needs."""
    motif = {tuple(numpy.round(position, 6)) for position in Diamond_Conventional_Motif()}
    candidate_translations = [numpy.asarray(position, dtype=numpy.float64) for position in Diamond_Conventional_Motif()]
    operations: list[tuple[Array, Array]] = []
    for permutation in permutations((0, 1, 2)):
        for signs in product((1, -1), repeat=3):
            matrix = numpy.zeros((3, 3), dtype=numpy.int64)
            for row, (column, sign) in enumerate(zip(permutation, signs)):
                matrix[row, column] = sign
            for translation in candidate_translations:
                mapped = {
                    tuple(numpy.mod(matrix @ numpy.asarray(atom) + translation, 1.0).round(6)) for atom in motif
                }
                if mapped == motif:
                    operations.append((matrix, translation))
                    break
    return tuple(operations)


def Apply_Grid_Operation(values: Array, matrix: Array, translation: Array) -> Array:
    """Applies one exact symmetry operation to channel fields on a compatible cubic grid."""
    stacked = numpy.asarray(values)
    extent = stacked.shape[1]
    grid = numpy.indices((extent, extent, extent)).reshape(3, -1)
    shifts = numpy.asarray(numpy.asarray(translation, dtype=numpy.float64) * extent + 0.5, dtype=numpy.int64).reshape(3, 1)
    inverse = numpy.asarray(matrix, dtype=numpy.int64).T
    source = numpy.mod(inverse @ (grid - shifts), extent)
    gathered = stacked[:, source[0], source[1], source[2]]
    return gathered.reshape(stacked.shape)


def Equivariance_Errors(
    apply_model: Callable[[Array], Array],
    values: Array,
    operations: tuple[tuple[Array, Array], ...],
) -> Array:
    """Returns the relative equivariance error of a model under each operation."""
    base_output = numpy.asarray(apply_model(values), dtype=numpy.float64)
    scale = numpy.linalg.norm(base_output.ravel())
    errors: list[float] = []
    for matrix, translation in operations:
        transformed_input = Apply_Grid_Operation(values, matrix, translation)
        output_of_transformed = numpy.asarray(apply_model(transformed_input), dtype=numpy.float64)
        transformed_output = Apply_Grid_Operation(base_output, matrix, translation)
        errors.append(float(numpy.linalg.norm((output_of_transformed - transformed_output).ravel()) / scale))
    return numpy.asarray(errors, dtype=numpy.float64)


def Block_Gap_Null(primitive_values: Array, supercell_values: Array, tiles: tuple[int, int, int]) -> float:
    """Returns the relative distance between the tiled primitive truth and the supercell truth."""
    primitive = numpy.asarray(primitive_values, dtype=numpy.float64)
    supercell = numpy.asarray(supercell_values, dtype=numpy.float64)
    tiled = numpy.tile(primitive, (1, *tiles))
    if tiled.shape != supercell.shape:
        tiled = Spectral_Truncation_Resample(tiled, supercell.shape[1:])
    difference = numpy.linalg.norm((tiled - supercell).ravel())
    return float(difference / numpy.linalg.norm(supercell.ravel()))


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
