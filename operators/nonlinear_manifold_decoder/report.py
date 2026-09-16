"""the member measured against its floors, written as one committed markdown artifact"""

import dataclasses
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from operators.data import (
    Apply_Standardized_Ridge,
    Archive_Path,
    Fit_Standardized_Ridge,
    Nearest_Training_Run,
    POOL_ROOT,
    Run_Identifier,
    STORE_NAME,
)
from operators.evaluation import MetricSummary, ScoredRun, Summarize, Summarize_By
from operators.factorized_fourier import All_Strain_Arms, Arm, Interior_Levels
from operators.framework import Spectral_Truncation_Resample
from operators.metrics import Relative_L2
from operators.training import Strain_Assignments_By_Run

REPORT_PATH = Path(__file__).parent / "report.md"
RESULTS_PATH = Path(__file__).parent / "results.json"
FIGURES_PATH = Path(__file__).parent / "figures"
# the inspection arrays are fields, and a field never leaves the pool -- only the drawing does
ARRAY_CACHE_PATH = POOL_ROOT / STORE_NAME / "_figures" / "nonlinear_manifold_decoder"
# checkpoints are scratch, not a corpus artifact, but they still hold no volumetric data either way
TRAINING_ARTIFACT_PATH = POOL_ROOT / STORE_NAME / "_training" / "nonlinear_manifold_decoder"

type Level = tuple[float, ...]

STRAIN_ATLAS_CAMPAIGN = "strain_atlas"
COMMON_GRID_SHAPE = (40, 40, 40)
COMMON_GRID_SHAPE_LABEL = "40x40x40"
CHARGE_DENSITY_FIELD_NAME = "charge_density"

# the canon's 1.5x kill margin restated as a fractional improvement: beat a floor's median by a third
IMPROVEMENT_MARGIN = 1.0 / 3.0
# the operator badge's own bar: at most 1.3x inflation moving from the dominant shape to an off-dominant one
TRANSFER_MARGIN = -0.3
RIDGE_REGULARIZATION = 1e-6
RADIAL_BASIS_REGULARIZATION = 1e-6


def Loaded_Strain_Charge_Density(
    run_path: str, shape: tuple[int, int, int] = COMMON_GRID_SHAPE
) -> NDArray[np.float64]:
    """one strain-atlas run's own charge density, resampled to the block's common shape (native shapes vary)"""
    identifier = Run_Identifier(run_path)
    with np.load(Archive_Path(STRAIN_ATLAS_CAMPAIGN, identifier)) as archive:
        density = np.asarray(archive[CHARGE_DENSITY_FIELD_NAME], dtype=np.float64)
    return Spectral_Truncation_Resample(density[None], shape)[0]


def Cached_Level_Field(
    arm: Arm, level: Level, cache: dict[tuple[str, Level], NDArray[np.float64]]
) -> NDArray[np.float64]:
    """one level's own mean charge density over every run sharing it (its functional variants), memoized"""
    key = (arm.name, level)
    if key not in cache:
        fields = [Loaded_Strain_Charge_Density(run_path) for run_path in arm.runs_by_level[level]]
        cache[key] = np.mean(np.stack(fields), axis=0)
    return cache[key]


def Multilinear_Interpolated_Field(
    level: Level, corners: tuple[Level, ...], field_of_corner: dict[Level, NDArray[np.float64]]
) -> NDArray[np.float64]:
    """the level's own field, multilinearly interpolated from its bracket corners' true fields"""
    dimension = len(level)
    bounds = [tuple(sorted({corner[axis] for corner in corners})) for axis in range(dimension)]
    total = np.zeros_like(next(iter(field_of_corner.values())))
    for corner in corners:
        weight = 1.0
        for axis in range(dimension):
            low, high = bounds[axis]
            fraction = (level[axis] - low) / (high - low)
            weight *= fraction if corner[axis] == high else (1.0 - fraction)
        total = total + weight * field_of_corner[corner]
    return total


def Strain_Tensor_By_Run_Path() -> dict[str, NDArray[np.float64]]:
    """every strain-atlas run's own full six-component tensor, keyed by run path"""
    return {
        run_path: np.asarray(assignment.tensor, dtype=np.float64)
        for run_path, assignment in Strain_Assignments_By_Run().items()
    }


@dataclasses.dataclass(frozen=True, slots=True)
class GaussianRadialBasis:
    """a fitted gaussian radial-basis interpolant: its training centers, their scale and its solved weights"""

    centers: NDArray[np.float64]
    spreads: NDArray[np.float64]
    length_scale: float
    weights: NDArray[np.float64]


def Fit_Gaussian_Radial_Basis(
    train_tensors: NDArray[np.float64], train_fields: NDArray[np.float64], regularization: float
) -> GaussianRadialBasis:
    """gaussian radial-basis weights solved against every training center, on standardized six-vectors"""
    spreads = np.asarray(train_tensors.std(axis=0), dtype=np.float64)
    # a strain component that never varies across the training centers would divide the distance by zero
    spreads[spreads == 0.0] = 1.0
    standardized = train_tensors / spreads
    pairwise = np.linalg.norm(standardized[:, None, :] - standardized[None, :, :], axis=2)
    off_diagonal = pairwise[~np.eye(pairwise.shape[0], dtype=np.bool_)]
    # the median distance between distinct centers is a standard, scale-free bandwidth choice
    length_scale = float(np.median(off_diagonal)) if off_diagonal.size else 1.0
    kernel_matrix = np.exp(-(pairwise**2) / (2.0 * length_scale**2))
    flattened_fields = train_fields.reshape(train_fields.shape[0], -1)
    weights = np.linalg.solve(kernel_matrix + regularization * np.eye(kernel_matrix.shape[0]), flattened_fields)
    return GaussianRadialBasis(standardized, spreads, length_scale, weights)


def Apply_Gaussian_Radial_Basis(
    fitted: GaussianRadialBasis, evaluation_tensors: NDArray[np.float64]
) -> NDArray[np.float64]:
    """a fitted gaussian radial-basis interpolant applied to fresh strain tensors"""
    standardized = evaluation_tensors / fitted.spreads
    pairwise = np.linalg.norm(standardized[:, None, :] - fitted.centers[None, :, :], axis=2)
    kernel = np.exp(-(pairwise**2) / (2.0 * fitted.length_scale**2))
    return kernel @ fitted.weights


@dataclasses.dataclass(frozen=True, slots=True)
class ArmFloorPopulation:
    """the arm-based leave-one-level-out split: every non-interior level trains, every interior level scores"""

    train_keys: list[tuple[str, Level]]
    eval_keys: list[tuple[str, Level]]
    field_of: dict[tuple[str, Level], NDArray[np.float64]]
    arm_by_name: dict[str, Arm]
    bracketing_rows: list[ScoredRun]


def Arm_Floor_Population(arms: tuple[Arm, ...]) -> ArmFloorPopulation:
    """every arm's own levels split by bracket completeness, the bracketing floor scored along the way"""
    arm_by_name = {arm.name: arm for arm in arms}
    cache: dict[tuple[str, Level], NDArray[np.float64]] = {}
    train_keys: list[tuple[str, Level]] = []
    eval_keys: list[tuple[str, Level]] = []
    bracketing_rows: list[ScoredRun] = []
    for arm in arms:
        interior = Interior_Levels(arm)
        for level in arm.runs_by_level:
            Cached_Level_Field(arm, level, cache)
            (eval_keys if level in interior else train_keys).append((arm.name, level))
        for level, corners in interior.items():
            truth = Cached_Level_Field(arm, level, cache)
            field_of_corner = {corner: Cached_Level_Field(arm, corner, cache) for corner in corners}
            predicted = Multilinear_Interpolated_Field(level, corners, field_of_corner)
            identifier = f"{arm.name}_{level}"
            bracketing_rows.append(
                ScoredRun(
                    identifier=identifier,
                    unit_key=identifier,
                    campaign=STRAIN_ATLAS_CAMPAIGN,
                    family=arm.name,
                    errors={"relative_l2": Relative_L2(predicted, truth)},
                )
            )
    return ArmFloorPopulation(sorted(train_keys), sorted(eval_keys), cache, arm_by_name, bracketing_rows)


def Representative_Tensor(
    population: ArmFloorPopulation, tensor_of_run: dict[str, NDArray[np.float64]], arm_name: str, level: Level
) -> NDArray[np.float64]:
    """the strain tensor of one representative run sharing this arm's own level"""
    run_path = population.arm_by_name[arm_name].runs_by_level[level][0]
    return tensor_of_run[run_path]


def Arm_Host_Floors(
    population: ArmFloorPopulation, tensor_of_run: dict[str, NDArray[np.float64]]
) -> dict[str, list[ScoredRun]]:
    """the gaussian radial-basis floor beside ridge and nearest-copy context, on the arm population"""
    train_tensors = np.stack(
        [Representative_Tensor(population, tensor_of_run, name, level) for name, level in population.train_keys]
    )
    train_fields = np.stack([population.field_of[key] for key in population.train_keys])
    eval_tensors = np.stack(
        [Representative_Tensor(population, tensor_of_run, name, level) for name, level in population.eval_keys]
    )
    eval_fields = np.stack([population.field_of[key] for key in population.eval_keys])
    flat_train_fields = train_fields.reshape(train_fields.shape[0], -1)

    radial_basis = Fit_Gaussian_Radial_Basis(train_tensors, flat_train_fields, RADIAL_BASIS_REGULARIZATION)
    radial_basis_flat_fields = Apply_Gaussian_Radial_Basis(radial_basis, eval_tensors)
    ridge = Fit_Standardized_Ridge(train_tensors, flat_train_fields, RIDGE_REGULARIZATION)
    ridge_flat_fields = Apply_Standardized_Ridge(ridge, eval_tensors)
    nearest_indices = Nearest_Training_Run(train_tensors, eval_tensors)

    radial_basis_rows: list[ScoredRun] = []
    ridge_rows: list[ScoredRun] = []
    copy_rows: list[ScoredRun] = []
    for position, (arm_name, level) in enumerate(population.eval_keys):
        truth = eval_fields[position]
        identifier = f"{arm_name}_{level}"
        radial_basis_rows.append(
            ScoredRun(
                identifier=identifier, unit_key=identifier, campaign=STRAIN_ATLAS_CAMPAIGN, family=arm_name,
                errors={"relative_l2": Relative_L2(radial_basis_flat_fields[position].reshape(truth.shape), truth)},
            )
        )
        ridge_rows.append(
            ScoredRun(
                identifier=identifier, unit_key=identifier, campaign=STRAIN_ATLAS_CAMPAIGN, family=arm_name,
                errors={"relative_l2": Relative_L2(ridge_flat_fields[position].reshape(truth.shape), truth)},
            )
        )
        copy_rows.append(
            ScoredRun(
                identifier=identifier, unit_key=identifier, campaign=STRAIN_ATLAS_CAMPAIGN, family=arm_name,
                errors={"relative_l2": Relative_L2(train_fields[nearest_indices[position]], truth)},
            )
        )
    return {
        "gaussian_radial_basis_floor": radial_basis_rows,
        "ridge_to_tensor_floor": ridge_rows,
        "nearest_run_copy_floor": copy_rows,
    }


def Floor_Summaries(floors: dict[str, list[ScoredRun]]) -> list[MetricSummary]:
    """each floor's pooled median beside its own per-family breakdown"""
    summaries: list[MetricSummary] = []
    for floor_label, rows in floors.items():
        summaries.append(Summarize(rows, "relative_l2", floor_label))
        for family_summary in Summarize_By(rows, "relative_l2", "family"):
            renamed = f"{floor_label}__{family_summary.group_name}"
            summaries.append(dataclasses.replace(family_summary, group_name=renamed))
    return summaries


def Host_Floors() -> tuple[ArmFloorPopulation, dict[str, list[ScoredRun]]]:
    """the two kill floors beside ridge and nearest-copy context, all measured before the member trains"""
    arms = All_Strain_Arms()
    population = Arm_Floor_Population(arms)
    tensor_of_run = Strain_Tensor_By_Run_Path()
    host_floors = {
        "bracketing_interpolation_floor": population.bracketing_rows,
        **Arm_Host_Floors(population, tensor_of_run),
    }
    return population, host_floors
