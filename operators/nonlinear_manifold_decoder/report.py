"""the member measured against its floors, written as one committed markdown artifact"""

import dataclasses
from pathlib import Path
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray

from operators.data import (
    Apply_Standardized_Ridge,
    Archive_Path,
    Fit_Standardized_Ridge,
    Guard_Fresh_Archives,
    Nearest_Training_Run,
    POOL_ROOT,
    Run_Identifier,
    STORE_NAME,
)
from operators.evaluation import (
    Block_Signature,
    Compare_To_Floor,
    Comparison_Table,
    FloorComparison,
    MemberResults,
    MetricSummary,
    ResultKey,
    ResultRow,
    ScoredRun,
    Summarize,
    Summarize_By,
    Summary_Table,
    VerdictRow,
    Write_Member_Results,
)
from operators.factorized_fourier import All_Strain_Arms, Arm, Interior_Levels
from operators.framework import Coefficients, Domain, GridSpec, Spectral_Truncation_Resample
from operators.inspection import Render_Error_Spread, Render_Floor_Comparison, Render_Inspection_Suite, Render_Table
from operators.metrics import Relative_L2
from operators.nonlinear_manifold_decoder import Manifold_Network, NonlinearManifoldDecoder
from operators.substrate import ParameterSet
from operators.tasks import Card_Named
from operators.training import (
    Build_Field_Cache,
    CoordinateFeaturizedBatches,
    FieldCache,
    ForwardLoss,
    Global_Statistics,
    Parameter_Field_Examples,
    Parameter_Spreads,
    PointSampledBatches,
    Staged_Training,
    Strain_Assignments_By_Run,
    Training_Engine,
)

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

# the branch's seventh feature, beside the six standardized strain components
FUNCTIONAL_BRANCH_FEATURE = {"cheap": 0.0, "accurate": 1.0}

BRANCH_HIDDEN_WIDTHS = (256, 256)
LATENT_WIDTH = 128
DECODER_HIDDEN_WIDTHS = (256, 256, 256)
FOURIER_ORDERS = 4
RUNS_PER_BATCH = 8
POINTS_PER_RUN = 2048
VALIDATION_POINTS_PER_RUN = 512
# the staged protocol's own thirds (peak, peak/3, peak/9), sized against the entry's 1.5-hour card cap
PEAK_LEARNING_RATE = 3e-3
STEP_COUNT = 10000
DIVERGENCE_PROBE_STEPS = 200
VALIDATION_INTERVAL = 100
# early stopping is only meaningful on the final, lowest-rate stage, once the schedule stops moving the floor
FINAL_STAGE_PATIENCE = 15
SEED = 20260916

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


def Field_Cache_With_Functional_Feature(cache: FieldCache) -> FieldCache:
    """every cached field's own parameters, the run's functional appended as a seventh branch feature"""
    augmented = tuple(
        dataclasses.replace(
            cached_field,
            parameters=np.concatenate(
                [
                    cached_field.parameters,
                    [FUNCTIONAL_BRANCH_FEATURE[cached_field.covariate_values["functional"]]],
                ]
            ),
        )
        for cached_field in cache.fields
    )
    return FieldCache(cache.card_name, cache.role, augmented)


class ManifoldBlock:
    """one committed-split role's own runs on the campaign's common grid, both functionals pooled"""


    def __init__(self, role: str) -> None:
        assignments = Strain_Assignments_By_Run()
        parameters: list[NDArray[np.float64]] = []
        fields: list[NDArray[np.float64]] = []
        self.unit_keys: list[str] = []
        self.families: list[str] = []
        self.identifiers: list[str] = []
        self.functionals: list[str] = []
        for example in Parameter_Field_Examples(Card_Named("strain_to_charge"), role):
            values = np.asarray(example.target_function.values, dtype=np.float64)
            if values.shape[1:] != COMMON_GRID_SHAPE:
                continue
            functional = example.covariate_values["functional"]
            branch_vector = np.concatenate(
                [np.asarray(example.parameters.vector, dtype=np.float64), [FUNCTIONAL_BRANCH_FEATURE[functional]]]
            )
            parameters.append(branch_vector)
            fields.append(values.reshape(-1))
            self.unit_keys.append(example.unit_key)
            self.families.append(assignments[example.run_path].family)
            self.identifiers.append(example.identifier)
            self.functionals.append(functional)
        Guard_Fresh_Archives(self.identifiers)
        self.parameters = np.asarray(parameters)
        self.fields = np.asarray(fields)


    def Scored(self, rebuilt: NDArray[np.float64]) -> list[ScoredRun]:
        """one scored run per field, carrying the labels the report groups by"""
        return [
            ScoredRun(
                identifier=self.identifiers[run],
                unit_key=self.unit_keys[run],
                campaign=STRAIN_ATLAS_CAMPAIGN,
                family=self.families[run],
                errors={"relative_l2": Relative_L2(rebuilt[run], self.fields[run])},
                covariate_values={"functional": self.functionals[run]},
            )
            for run in range(self.fields.shape[0])
        ]


def Manifold_Grid_Predictions(
    member: NonlinearManifoldDecoder,
    parameter_spreads: NDArray[np.float64],
    channel_mean: float,
    channel_deviation: float,
    block: ManifoldBlock,
    shape: tuple[int, int, int] = COMMON_GRID_SHAPE,
) -> NDArray[np.float64]:
    """the trained member's field on the campaign's common grid, for every given run's own branch vector"""
    predictions: list[NDArray[np.float64]] = []
    for run in range(block.parameters.shape[0]):
        branch_vector = block.parameters[run] / parameter_spreads
        produced = member(Coefficients(vector=branch_vector, domain=Domain(np.eye(3))), GridSpec(shape))
        standardized = np.asarray(produced.values, dtype=np.float64).reshape(-1)
        predictions.append(standardized * channel_deviation + channel_mean)
    return np.asarray(predictions)


def Manifold_Every_Shape_Predictions(
    member: NonlinearManifoldDecoder,
    parameter_spreads: NDArray[np.float64],
    channel_mean: float,
    channel_deviation: float,
    test_cache: FieldCache,
) -> list[ScoredRun]:
    """the trained member's own field on every test run's own grid shape, whatever shape each one is"""
    assignments = Strain_Assignments_By_Run()
    scored: list[ScoredRun] = []
    for cached_field in test_cache.fields:
        branch_vector = cached_field.parameters / parameter_spreads
        grid_shape = cast(tuple[int, int, int], cached_field.grid_shape)
        produced = member(Coefficients(vector=branch_vector, domain=Domain(np.eye(3))), GridSpec(grid_shape))
        standardized = np.asarray(produced.values, dtype=np.float64).reshape(-1)
        predicted = standardized * channel_deviation + channel_mean
        truth = cached_field.Flattened_Values()[0].astype(np.float64)
        scored.append(
            ScoredRun(
                identifier=cached_field.identifier,
                unit_key=cached_field.unit_key,
                campaign=STRAIN_ATLAS_CAMPAIGN,
                family=assignments[cached_field.run_path].family,
                errors={"relative_l2": Relative_L2(predicted, truth)},
                covariate_values={
                    "functional": cached_field.covariate_values["functional"],
                    "grid_shape": "x".join(str(extent) for extent in grid_shape),
                },
            )
        )
    return scored


def Transfer_Comparison(every_shape_runs: list[ScoredRun]) -> FloorComparison:
    """the member's own error off the dominant shape, against its own error on the dominant shape"""
    on_common = [run for run in every_shape_runs if run.covariate_values["grid_shape"] == COMMON_GRID_SHAPE_LABEL]
    off_dominant = [
        run for run in every_shape_runs if run.covariate_values["grid_shape"] != COMMON_GRID_SHAPE_LABEL
    ]
    return Compare_To_Floor(off_dominant, on_common, "relative_l2", "own_40_cubed_error", TRANSFER_MARGIN)


def Point_Value_Loss(
    member: NonlinearManifoldDecoder, parameter_spreads: Any, channel_mean: Any, channel_deviation: Any
) -> ForwardLoss:
    """mean squared error on globally standardized density values at the sampled points"""


    def Loss_Of(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        """the point-sampled forward answered against this batch's own standardized targets"""
        branch_input = lifted_batch["parameter_vectors"] / parameter_spreads
        predicted = member.Forward_Point_Values(lifted, branch_input, lifted_batch["trunk_features"])
        target = (lifted_batch["target_values"][:, :, 0] - channel_mean) / channel_deviation
        residuals = predicted - target
        return (residuals * residuals).mean()

    return Loss_Of


def Trained_Manifold_Member() -> tuple[NonlinearManifoldDecoder, NDArray[np.float64], float, float, dict[str, object]]:
    """the member trained point-sampled on every grid shape at once, both functionals pooled as a branch feature"""
    card = Card_Named("strain_to_charge")
    training_cache = Field_Cache_With_Functional_Feature(Build_Field_Cache(card, "train"))
    validation_cache = Field_Cache_With_Functional_Feature(Build_Field_Cache(card, "validation"))
    parameter_width = int(training_cache.fields[0].parameters.shape[0])
    parameter_spreads = Parameter_Spreads(training_cache)
    channel_mean, channel_deviation = Global_Statistics(training_cache)
    member = Manifold_Network(
        parameter_width, BRANCH_HIDDEN_WIDTHS, LATENT_WIDTH, DECODER_HIDDEN_WIDTHS, FOURIER_ORDERS, seed=SEED
    )
    sampler = PointSampledBatches(
        training_cache, validation_cache, RUNS_PER_BATCH, POINTS_PER_RUN, VALIDATION_POINTS_PER_RUN
    )
    batches = CoordinateFeaturizedBatches(sampler, member.decoder.coordinate_features)
    engine = Training_Engine()
    lifted_parameter_spreads = engine.Lift_Constant(parameter_spreads)
    lifted_channel_mean = engine.Lift_Constant(np.asarray(channel_mean, dtype=np.float64))
    lifted_channel_deviation = engine.Lift_Constant(np.asarray(channel_deviation, dtype=np.float64))
    forward_loss = Point_Value_Loss(member, lifted_parameter_spreads, lifted_channel_mean, lifted_channel_deviation)
    parameters = ParameterSet(values=member.Parameter_Values())
    parameters, manifest = Staged_Training(
        engine,
        parameters,
        lambda: ParameterSet(values=member.Parameter_Values()),
        forward_loss,
        batches,
        STEP_COUNT,
        "manifold",
        SEED,
        TRAINING_ARTIFACT_PATH,
        peak_learning_rate=PEAK_LEARNING_RATE,
        probe_steps=DIVERGENCE_PROBE_STEPS,
        validation_interval=VALIDATION_INTERVAL,
        final_stage_patience=FINAL_STAGE_PATIENCE,
    )
    for name, value in parameters.values.items():
        if name in member.branch.parameter_values:
            member.branch.parameter_values[name] = value
        if name in member.decoder.parameter_values:
            member.decoder.parameter_values[name] = value
    return member, parameter_spreads, channel_mean, channel_deviation, manifest


def Manifold_Member_Arm_Predictions(
    member: NonlinearManifoldDecoder,
    parameter_spreads: NDArray[np.float64],
    channel_mean: float,
    channel_deviation: float,
    population: ArmFloorPopulation,
    tensor_of_run: dict[str, NDArray[np.float64]],
) -> list[ScoredRun]:
    """the trained member's own prediction at every interior level, averaged over the functionals it carries"""
    scored: list[ScoredRun] = []
    for arm_name, level in population.eval_keys:
        tensor = Representative_Tensor(population, tensor_of_run, arm_name, level)
        predictions: list[NDArray[np.float64]] = []
        for functional_feature in FUNCTIONAL_BRANCH_FEATURE.values():
            branch_vector = np.concatenate([tensor, [functional_feature]]) / parameter_spreads
            produced = member(Coefficients(vector=branch_vector, domain=Domain(np.eye(3))), GridSpec(COMMON_GRID_SHAPE))
            standardized = np.asarray(produced.values, dtype=np.float64).reshape(COMMON_GRID_SHAPE)
            predictions.append(standardized * channel_deviation + channel_mean)
        predicted = np.mean(predictions, axis=0)
        truth = population.field_of[(arm_name, level)]
        identifier = f"{arm_name}_{level}"
        scored.append(
            ScoredRun(
                identifier=identifier, unit_key=identifier, campaign=STRAIN_ATLAS_CAMPAIGN, family=arm_name,
                errors={"relative_l2": Relative_L2(predicted, truth)},
            )
        )
    return scored


def Write_Figures(
    member: NonlinearManifoldDecoder,
    test: ManifoldBlock,
    member_rebuilt: NDArray[np.float64],
    floor_medians: dict[str, float],
    member_median: float,
) -> int:
    """the member's whole visual surface, drawn from arrays cached on the pool"""
    cache = ARRAY_CACHE_PATH / "pooled"
    cache.mkdir(parents=True, exist_ok=True)
    inspected = {name: np.asarray(value, dtype=np.float64) for name, value in member.Inspect().items()}
    # cached so a re-render needs no retrain, which is what keeps committed figures stable
    np.savez(cache / "inspection.npz", **cast(dict[str, Any], inspected))
    with np.load(cache / "inspection.npz") as archive:
        restored = {name: np.asarray(archive[name], dtype=np.float64) for name in archive.files}

    directory = FIGURES_PATH / "pooled"
    suite = Render_Inspection_Suite(restored, directory / "components", "nonlinear_manifold_decoder pooled")
    if suite.skipped:
        raise ValueError(f"no renderer for {suite.skipped}, which means the suite is incomplete")

    scored = [Relative_L2(member_rebuilt[run], test.fields[run]) for run in range(test.fields.shape[0])]
    by_family: dict[str, list[float]] = {}
    for run in range(test.fields.shape[0]):
        by_family.setdefault(test.families[run], []).append(scored[run])
    Render_Error_Spread(
        {name: np.asarray(values) for name, values in by_family.items()},
        directory / "error_by_family.png",
        "nonlinear_manifold_decoder test error by strain family",
    )
    Render_Floor_Comparison(
        floor_medians,
        member_median,
        {name: IMPROVEMENT_MARGIN for name in floor_medians},
        directory / "floors.png",
        "nonlinear_manifold_decoder against its host floors",
    )
    return len(suite.written) + 2


def Report_Lines() -> tuple[list[str], MemberResults]:
    """the whole report: floors pre-registered, the member trained once, every bar checked against it"""
    population, host_floors = Host_Floors()
    tensor_of_run = Strain_Tensor_By_Run_Path()

    member, parameter_spreads, channel_mean, channel_deviation, training_manifest = Trained_Manifold_Member()

    member_arm_runs = Manifold_Member_Arm_Predictions(
        member, parameter_spreads, channel_mean, channel_deviation, population, tensor_of_run
    )
    interpolation_comparison = Compare_To_Floor(
        member_arm_runs, host_floors["bracketing_interpolation_floor"], "relative_l2",
        "bracketing_interpolation", IMPROVEMENT_MARGIN,
    )
    radial_basis_comparison = Compare_To_Floor(
        member_arm_runs, host_floors["gaussian_radial_basis_floor"], "relative_l2",
        "gaussian_radial_basis", IMPROVEMENT_MARGIN,
    )

    test_block = ManifoldBlock("test")
    member_rebuilt = Manifold_Grid_Predictions(member, parameter_spreads, channel_mean, channel_deviation, test_block)
    member_runs = test_block.Scored(member_rebuilt)

    card = Card_Named("strain_to_charge")
    every_shape_cache = Field_Cache_With_Functional_Feature(Build_Field_Cache(card, "test"))
    every_shape_runs = Manifold_Every_Shape_Predictions(
        member, parameter_spreads, channel_mean, channel_deviation, every_shape_cache
    )
    transfer_comparison = Transfer_Comparison(every_shape_runs)

    dead_end = interpolation_comparison.verdict == "kill"
    parameter_count = sum(value.size for value in member.Parameter_Values().values())

    floor_medians = {
        "bracketing_interpolation": interpolation_comparison.floor_median,
        "gaussian_radial_basis": radial_basis_comparison.floor_median,
    }
    figure_count = Write_Figures(
        member, test_block, member_rebuilt, floor_medians, interpolation_comparison.member_median
    )

    host_summaries = Floor_Summaries(host_floors)
    headline_summary = Summarize(member_runs, "relative_l2", "member_headline_committed_split")
    arm_member_summary = Summarize(member_arm_runs, "relative_l2", "member_arm_population")
    every_shape_summary = Summarize(every_shape_runs, "relative_l2", "member_every_shape")

    arm_signature = Block_Signature(f"{arm_name}_{level}" for arm_name, level in population.eval_keys)
    headline_signature = Block_Signature(test_block.unit_keys)
    every_shape_signature = Block_Signature(run.unit_key for run in every_shape_runs)

    def Result_Key(block: str, group: str) -> ResultKey:
        """this report's own member, configuration, task and split, beside the block and group asked for"""
        return ResultKey(
            member="nonlinear_manifold_decoder", configuration="canonical", task="strain_to_charge",
            split="strain_atlas_holdout", block=block, group=group,
        )

    rows = tuple(
        ResultRow(
            key=Result_Key("arm_leave_one_level_out", summary.group_name), summary=summary,
            block_signature=arm_signature,
        )
        for summary in (*host_summaries, arm_member_summary)
    ) + (
        ResultRow(
            key=Result_Key("committed_test_split", headline_summary.group_name), summary=headline_summary,
            block_signature=headline_signature,
        ),
        ResultRow(
            key=Result_Key("every_shape_test_split", every_shape_summary.group_name), summary=every_shape_summary,
            block_signature=every_shape_signature,
        ),
    )
    verdicts = (
        VerdictRow(
            key=Result_Key("arm_leave_one_level_out", "bracketing_interpolation"), comparison=interpolation_comparison
        ),
        VerdictRow(
            key=Result_Key("arm_leave_one_level_out", "gaussian_radial_basis"), comparison=radial_basis_comparison
        ),
        VerdictRow(key=Result_Key("every_shape_test_split", "own_40_cubed_error"), comparison=transfer_comparison),
    )
    results = MemberResults(
        member="nonlinear_manifold_decoder", regenerate="python -m operators.nonlinear_manifold_decoder.report",
        rows=rows, verdicts=verdicts,
    )

    verdict_line = (
        "**dead end**: the interpolation bar killed the entry (the canon's terminal clause for this member)"
        if dead_end else "**alive**: the interpolation bar passed"
    )
    lines = [
        "# nonlinear_manifold_decoder -- strain or lattice parameters to charge density, decoded point by point",
        "",
        f"`{card.name}` on the strain atlas holdout, one seeded run (seed {SEED}), {parameter_count} parameters.",
        "",
        "## floors, pre-registered on the arm leave-one-level-out population",
        "",
        "```",
        Render_Table(Summary_Table(tuple(host_summaries))),
        "```",
        "",
        "## the member against its floors and bars",
        "",
        "```",
        Render_Table(
            Comparison_Table((interpolation_comparison, radial_basis_comparison, transfer_comparison))
        ),
        "```",
        "",
        f"{verdict_line}. Grid transfer is reported regardless of the interpolation verdict, per the canon's own"
        " instruction for this entry.",
        "",
        "## the member's own headline, committed strain_atlas_holdout split",
        "",
        "```",
        Render_Table(Summary_Table((headline_summary, arm_member_summary, every_shape_summary))),
        "```",
        "",
        f"Training manifest: {list(training_manifest)}.",
        "",
        f"Figures: {figure_count} files written under `figures/pooled/`, arrays cached at `{ARRAY_CACHE_PATH}`.",
        "",
    ]
    return lines, results


def Main() -> None:
    """regenerate report.md, results.json and the figure suite from a fresh training run"""
    lines, results = Report_Lines()
    REPORT_PATH.write_text("\n".join(lines) + "\n")
    Write_Member_Results(RESULTS_PATH, results)


if __name__ == "__main__":
    Main()
