"""how far an operator's output moves when its discretization changes"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from itertools import permutations, product

import numpy as np
from numpy.typing import NDArray

from operators.framework.domain import Array, GridSpec
from operators.framework.operator import Operator
from operators.framework.representation import GridFunction, UniformGridQuadrature
from operators.metrics import Relative_L2
from operators.tasks import TaskCard

CURVE_SUFFIX = "_curve"

QUARTER_CELL_DIVISOR = 4

TRAINING_SHAPE = (40, 40, 40)


def Spectral_Truncation_Resample(
    values: NDArray[np.float64], target_shape: tuple[int, int, int]
) -> NDArray[np.float64]:
    """grid to grid by exact Fourier truncation or zero-padding"""
    stacked = np.asarray(values, dtype=np.float64)
    spectrum = np.fft.fftn(stacked, axes=(1, 2, 3))
    result = np.zeros((stacked.shape[0], *target_shape), dtype=np.complex128)
    source_index: list[NDArray[np.int64]] = []
    target_index: list[NDArray[np.int64]] = []
    for source_extent, target_extent in zip(stacked.shape[1:], target_shape):
        # only the modes both grids can hold survive, wrapped to each one's transform positions
        largest_kept_mode = (min(source_extent, target_extent) - 1) // 2
        modes = np.arange(-largest_kept_mode, largest_kept_mode + 1, dtype=np.int64)
        source_index.append(np.mod(modes, source_extent))
        target_index.append(np.mod(modes, target_extent))
    channel_index = np.arange(stacked.shape[0], dtype=np.int64)
    result[np.ix_(channel_index, *target_index)] = spectrum[np.ix_(channel_index, *source_index)]
    # the transform is unnormalized, so the point-count ratio restores the amplitude
    scale = float(np.prod(target_shape)) / float(np.prod(stacked.shape[1:]))
    return np.real(np.fft.ifftn(result, axes=(1, 2, 3))) * scale


def Diamond_Conventional_Motif() -> tuple[tuple[float, float, float], ...]:
    """the eight diamond positions of the conventional cubic cell"""
    centering = ((0.0, 0.0, 0.0), (0.0, 0.5, 0.5), (0.5, 0.0, 0.5), (0.5, 0.5, 0.0))
    positions: list[tuple[float, float, float]] = []
    # the two-atom basis repeated on each face-centering translation
    for base in ((0.0, 0.0, 0.0), (0.25, 0.25, 0.25)):
        for offset in centering:
            combined = [
                float((base_component + offset_component) % 1.0)
                for base_component, offset_component in zip(base, offset)
            ]
            positions.append((combined[0], combined[1], combined[2]))
    return tuple(positions)


def Diamond_Grid_Operations() -> tuple[tuple[NDArray[np.int64], NDArray[np.float64]], ...]:
    """the 48 signed permutations with the fractional translation each needs"""
    motif = {tuple(np.round(position, 6)) for position in Diamond_Conventional_Motif()}
    candidate_translations = [np.asarray(position, dtype=np.float64) for position in Diamond_Conventional_Motif()]
    operations: list[tuple[NDArray[np.int64], NDArray[np.float64]]] = []
    for permutation in permutations((0, 1, 2)):
        for signs in product((1, -1), repeat=3):
            matrix = np.zeros((3, 3), dtype=np.int64)
            for output_axis, (input_axis, sign) in enumerate(zip(permutation, signs)):
                matrix[output_axis, input_axis] = sign
            # a signed permutation counts only once some glide translation maps the motif onto itself
            for translation in candidate_translations:
                mapped = {
                    tuple(np.mod(matrix @ np.asarray(atom) + translation, 1.0).round(6)) for atom in motif
                }
                if mapped == motif:
                    operations.append((matrix, translation))
                    break
    return tuple(operations)


def Apply_Grid_Operation(
    values: NDArray[np.float64], matrix: NDArray[np.int64], translation: NDArray[np.float64]
) -> NDArray[np.float64]:
    """one exact symmetry operation on a compatible cubic grid"""
    stacked = np.asarray(values)
    extent = stacked.shape[1]
    grid = np.indices((extent, extent, extent)).reshape(3, -1)
    # the half rounds the fractional translation to the nearest whole voxel
    shifts = np.asarray(np.asarray(translation, dtype=np.float64) * extent + 0.5, dtype=np.int64).reshape(3, 1)
    # gathering asks where each target voxel came from, which is the inverse map
    inverse = np.asarray(matrix, dtype=np.int64).T
    source = np.mod(inverse @ (grid - shifts), extent)
    gathered = stacked[:, source[0], source[1], source[2]]
    return gathered.reshape(stacked.shape)


def Equivariance_Errors(
    apply_model: Callable[[NDArray[np.float64]], NDArray[np.float64]],
    values: NDArray[np.float64],
    operations: tuple[tuple[NDArray[np.int64], NDArray[np.float64]], ...],
) -> NDArray[np.float64]:
    """relative equivariance error of a model under each operation"""
    base_output = np.asarray(apply_model(values), dtype=np.float64)
    scale = np.linalg.norm(base_output.ravel())
    errors: list[float] = []
    for matrix, translation in operations:
        # transform then apply, against apply then transform
        transformed_input = Apply_Grid_Operation(values, matrix, translation)
        output_of_transformed = np.asarray(apply_model(transformed_input), dtype=np.float64)
        transformed_output = Apply_Grid_Operation(base_output, matrix, translation)
        errors.append(float(np.linalg.norm((output_of_transformed - transformed_output).ravel()) / scale))
    return np.asarray(errors, dtype=np.float64)


def Block_Gap_Null(
    primitive_values: NDArray[np.float64], supercell_values: NDArray[np.float64], tiles: tuple[int, int, int]
) -> float:
    """relative distance between the tiled primitive truth and the supercell truth"""
    primitive = np.asarray(primitive_values, dtype=np.float64)
    supercell = np.asarray(supercell_values, dtype=np.float64)
    tiled = np.tile(primitive, (1, *tiles))
    # tiling need not land on the supercell's own grid
    if tiled.shape != supercell.shape:
        tiled = Spectral_Truncation_Resample(tiled, supercell.shape[1:])
    difference = np.linalg.norm((tiled - supercell).ravel())
    return float(difference / np.linalg.norm(supercell.ravel()))


def K_Quality_Tier(irreducible_kpoint_count: int) -> str:
    """the spectral-label tier an irreducible k-point count earns"""
    if irreducible_kpoint_count >= 64:
        return "high_fidelity"
    if irreducible_kpoint_count >= 50:
        return "recommended"
    if irreducible_kpoint_count >= 27:
        return "permissive"
    return "below_gate"


@dataclass(frozen=True, slots=True)
class InvarianceProbe:
    """one run's input field beside the truth an operator is scored against"""

    input_function: GridFunction
    truth_values: NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class SupercellTwin:
    """a supercell run beside the primitive truth its own truth is priced against"""

    input_function: GridFunction
    supercell_truth: NDArray[np.float64]
    primitive_truth: NDArray[np.float64]
    tiles: tuple[int, int, int]


def Grid_Shape_Of(values: Array) -> tuple[int, int, int]:
    """the three spatial extents of a channel-first field"""
    first_extent, second_extent, third_extent = np.asarray(values).shape[1:]
    return int(first_extent), int(second_extent), int(third_extent)


def Applied_On_Grid(
    operator: Operator[GridFunction, GridFunction],
    carried: GridFunction,
    output_shape: tuple[int, int, int],
) -> NDArray[np.float64]:
    """the operator's output values on one requested grid"""
    return np.asarray(operator(carried, GridSpec(output_shape)).values, dtype=np.float64)


def Carried_On_Grid(carried: GridFunction, output_shape: tuple[int, int, int]) -> GridFunction:
    """the same function on another grid, by exact Fourier truncation or zero-padding"""
    values = Spectral_Truncation_Resample(np.asarray(carried.values, dtype=np.float64), output_shape)
    point_count = output_shape[0] * output_shape[1] * output_shape[2]
    quadrature = UniformGridQuadrature(carried.quadrature.cell_volume, point_count)
    return GridFunction(values, carried.channel_labels, carried.domain, quadrature)


def Grid_Application(
    operator: Operator[GridFunction, GridFunction], carried: GridFunction
) -> Callable[[NDArray[np.float64]], NDArray[np.float64]]:
    """the operator as an array-to-array map on the grid its input already carries"""
    output_shape = Grid_Shape_Of(carried.values)

    def Apply_To_Values(values: NDArray[np.float64]) -> NDArray[np.float64]:
        """one field array in, one field array out"""
        moved = GridFunction(values, carried.channel_labels, carried.domain, carried.quadrature)
        return Applied_On_Grid(operator, moved, output_shape)

    return Apply_To_Values


def Exactly_Operable_Grid(shape: tuple[int, int, int]) -> bool:
    """whether the 48 operations land on whole voxels, which needs a quarter-divisible cube"""
    # the glide translations are quarter cells, and a quarter cell is whole voxels only here
    return len(set(shape)) == 1 and shape[0] % QUARTER_CELL_DIVISOR == 0


def Skill_Against_Null(
    model_errors: NDArray[np.float64], null_errors: NDArray[np.float64]
) -> NDArray[np.float64]:
    """the share of the null's error the operator removes, run by run"""
    # a null that scores nothing cannot be improved on by a fraction of itself
    divisible = np.where(null_errors > 0.0, null_errors, 1.0)
    return np.where(null_errors > 0.0, 1.0 - model_errors / divisible, 0.0)


def Resolution_Axis(
    operator: Operator[GridFunction, GridFunction],
    probes: Sequence[InvarianceProbe],
    training_shape: tuple[int, int, int],
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """every probe's coarse-input error beside the truncation floor it is judged against"""
    model_errors: list[float] = []
    null_errors: list[float] = []
    for probe in probes:
        evaluation_shape = Grid_Shape_Of(probe.truth_values)
        coarse_input = Carried_On_Grid(probe.input_function, training_shape)
        predicted = Applied_On_Grid(operator, coarse_input, evaluation_shape)
        model_errors.append(Relative_L2(predicted, probe.truth_values))
        # the null is the coarse truth carried back up, which no operator on coarse input can beat
        coarse_truth = Spectral_Truncation_Resample(probe.truth_values, training_shape)
        upsampled_truth = Spectral_Truncation_Resample(coarse_truth, evaluation_shape)
        null_errors.append(Relative_L2(upsampled_truth, probe.truth_values))
    return np.asarray(model_errors, dtype=np.float64), np.asarray(null_errors, dtype=np.float64)


def Symmetry_Axis(
    operator: Operator[GridFunction, GridFunction], probes: Sequence[InvarianceProbe]
) -> NDArray[np.float64]:
    """every probe's equivariance error under each of the 48 diamond operations"""
    operations = Diamond_Grid_Operations()
    return np.stack(
        [
            Equivariance_Errors(
                Grid_Application(operator, probe.input_function),
                np.asarray(probe.input_function.values, dtype=np.float64),
                operations,
            )
            for probe in probes
        ]
    )


def Supercell_Axis(
    operator: Operator[GridFunction, GridFunction], twins: Sequence[SupercellTwin]
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """every twin's supercell error beside the block gap between the two campaigns' own truths"""
    model_errors: list[float] = []
    null_errors: list[float] = []
    for twin in twins:
        predicted = Applied_On_Grid(operator, twin.input_function, Grid_Shape_Of(twin.supercell_truth))
        model_errors.append(Relative_L2(predicted, twin.supercell_truth))
        null_errors.append(Block_Gap_Null(twin.primitive_truth, twin.supercell_truth, twin.tiles))
    return np.asarray(model_errors, dtype=np.float64), np.asarray(null_errors, dtype=np.float64)


def Discretization_Invariance_Report(
    operator: Operator[GridFunction, GridFunction],
    task: TaskCard,
    probes: Sequence[InvarianceProbe] = (),
    training_shape: tuple[int, int, int] = TRAINING_SHAPE,
    twins: Sequence[SupercellTwin] = (),
    irreducible_kpoint_counts: Sequence[int] = (),
) -> dict[str, Array]:
    """every invariance axis that applies to one operator on one task card"""
    measured: dict[str, Array] = {}
    reported: list[str] = []
    skipped: list[str] = []
    on_a_curve = any(target.endswith(CURVE_SUFFIX) for target in task.targets)
    if on_a_curve or not probes:
        withheld = "the card's target is a curve, not a field on a grid" if on_a_curve else "no probes supplied"
        skipped += [f"resolution: {withheld}", f"symmetry: {withheld}"]
    else:
        model_errors, null_errors = Resolution_Axis(operator, probes, training_shape)
        measured["resolution_training_shape"] = np.asarray(training_shape)
        measured["resolution_model_error"] = model_errors
        measured["resolution_truncation_null"] = null_errors
        measured["resolution_skill"] = Skill_Against_Null(model_errors, null_errors)
        reported.append("resolution")
        if all(Exactly_Operable_Grid(Grid_Shape_Of(probe.input_function.values)) for probe in probes):
            equivariance_errors = Symmetry_Axis(operator, probes)
            measured["symmetry_equivariance_error"] = equivariance_errors
            measured["symmetry_median_equivariance_error"] = np.asarray(float(np.median(equivariance_errors)))
            reported.append("symmetry")
        else:
            skipped.append("symmetry: a probe grid is not a cube the 48 operations land on exactly")
    if twins:
        model_errors, null_errors = Supercell_Axis(operator, twins)
        measured["supercell_model_error"] = model_errors
        measured["supercell_block_gap_null"] = null_errors
        # an error at or under the block gap prices in the campaigns' own systematics, not the model
        measured["supercell_resolves_model_quality"] = model_errors > null_errors
        reported.append("supercell")
    else:
        skipped.append("supercell: no twin runs supplied")
    if irreducible_kpoint_counts:
        counts = np.asarray(irreducible_kpoint_counts, dtype=np.int64)
        measured["kpoint_irreducible_count"] = counts
        measured["kpoint_quality_tier"] = np.asarray([K_Quality_Tier(int(count)) for count in counts])
        reported.append("k_quality")
    else:
        skipped.append("k_quality: no irreducible k-point counts supplied")
    return {
        "task_name": np.asarray(task.name),
        "axes_reported": np.asarray(reported),
        "axes_skipped": np.asarray(skipped),
        **measured,
    }
