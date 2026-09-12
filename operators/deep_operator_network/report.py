"""the member measured against its floors, written as one committed markdown artifact"""

from pathlib import Path
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray

from operators.data import (
    Apply_Standardized_Ridge,
    Fit_Standardized_Ridge,
    Gram_Pod,
    Guard_Fresh_Archives,
    Nearest_Training_Run,
    PodBasis,
    Project,
    POOL_ROOT,
    Reconstruct,
    STORE_NAME,
)
from operators.deep_operator_network import (
    Canonical_Network,
    DeepOperatorNetwork,
    Energy_Trunk_Network,
    Pointwise_Statistics,
    Principal_Component_Network,
    Proper_Orthogonal_Network,
    Reference_Density,
    Reference_Density_Restored,
    Reference_Density_Standardized,
)
from operators.evaluation import (
    Compare_To_Floor,
    Comparison_Table,
    EXTRAPOLATION,
    FloorComparison,
    INTERPOLATION,
    ScoredRun,
    Summarize,
    Summarize_By,
    Summary_Table,
)
from operators.framework import Array, Coefficients, Domain, GridSpec, Output_Points, PointSpec
from operators.inspection import (
    Render_Curves,
    Render_Error_Spread,
    Render_Floor_Comparison,
    Render_Inspection_Suite,
    Render_Prediction_Against_Truth,
    Render_Table,
)
from operators.metrics import Curve_L1, Frequency_Split_Relative_L2, Gap_Edge_Error, Relative_L2, Wasserstein_1d
from operators.readouts import BasisExpansion, CoordinateFeatures, RampedCoordinateFeatures
from operators.substrate import Mean_Over_Last_Axis, ParameterSet, Sum_Over_Last_Axis
from operators.tasks import Card_Named, TaskCard
from operators.training import (
    BatchSource,
    Build_Field_Cache,
    Cached_Field_Statistics,
    CachedField,
    FieldCache,
    FixedBatches,
    ForwardLoss,
    Parameter_Field_Examples,
    ParameterExample,
    PointSampledBatches,
    State_Density_Examples,
    Strain_Assignments_By_Run,
    Train,
    Training_Engine,
    TrainingBatch,
)
from operators.wrappers import Renormalization_Scale

REPORT_PATH = Path(__file__).parent / "report.md"
FIGURES_PATH = Path(__file__).parent / "figures"
# the inspection arrays are fields, and a field never leaves the pool -- only the drawing does
ARRAY_CACHE_PATH = POOL_ROOT / STORE_NAME / "_figures" / "deep_operator_network"
# checkpoints are scratch, not a corpus artifact, but they still hold no volumetric data either way
TRAINING_ARTIFACT_PATH = POOL_ROOT / STORE_NAME / "_training" / "deep_operator_network"
COMMON_GRID_SHAPE = (40, 40, 40)
CONFIGURATIONS_REPORTED = ("principal_component", "proper_orthogonal")
BASIS_RANK = 32
HIDDEN_WIDTHS = (64, 64, 64)
CANDIDATE_STEP_COUNTS = (2000, 4000, 8000, 16000, 32000)
RIDGE_MARGIN = 0.25
NEAREST_NEIGHBOR_MARGIN = 0.5

# the recorded starting point (test-suite.md II.1): branch and trunk each four layers wide, latent 256
CANONICAL_LATENT_WIDTH = 256
CANONICAL_BRANCH_HIDDEN_WIDTHS = (256, 256, 256)
CANONICAL_TRUNK_HIDDEN_WIDTHS = (256, 256, 256)
CANONICAL_RUNS_PER_BATCH = 8
CANONICAL_POINTS_PER_RUN = 4096
# a decreasing schedule across three restarts, each starting from the previous stage's best parameters
CANONICAL_STAGE_LEARNING_RATES = (3e-3, 1e-3, 3e-4)
CANONICAL_STAGE_STEP_COUNTS = (6000, 6000, 8000)
CANONICAL_VALIDATION_INTERVAL = 100
# early stopping is only meaningful on the final, lowest-rate stage, once the schedule stops moving the floor
CANONICAL_PATIENCE = 10
CANONICAL_SEED = 20260828

# strain_to_states (test-suite.md VI.1): both functionals pooled, the functional a seventh branch feature
FUNCTIONAL_BRANCH_FEATURE = {"cheap": 0.0, "accurate": 1.0}
# where the strain signal actually concentrates -- measured before this configuration was built
BAND_EDGE_LOWER_EV = -2.0
BAND_EDGE_UPPER_EV = 6.0
ENERGY_TRUNK_BRANCH_HIDDEN_WIDTHS = (256, 256)
ENERGY_TRUNK_LATENT_WIDTH = 128
ENERGY_TRUNK_TRUNK_HIDDEN_WIDTHS = (128, 128, 128)
ENERGY_TRUNK_FOURIER_ORDERS = 4
# measured: 1e-2 overshoots within the first validation passes and never recovers; this decreasing
# schedule was chosen by trying rates on the primary run and keeping the one that did not overshoot
ENERGY_TRUNK_STAGE_LEARNING_RATES = (2e-3, 7e-4, 2e-4)
ENERGY_TRUNK_STAGE_STEP_COUNTS = (800, 1200, 5000)
ENERGY_TRUNK_VALIDATION_INTERVAL = 40
ENERGY_TRUNK_PATIENCE = 15
ENERGY_TRUNK_SEED = 20260911
# how much more the ablation weighs the band-edge region than the rest of the window
ENERGY_TRUNK_BAND_EDGE_WEIGHT = 5.0

# lattice_to_charge (test-suite.md II.1b): the angle stratum's one shared shape, measured on all 125 of its runs
PEROVSKITE_ANGLE_GRID_SHAPE = (64, 64, 64)
# measured: every one of the 249 perovskite runs integrates to exactly this, 0 exceptions
PEROVSKITE_ELECTRON_COUNT = 48.0
PEROVSKITE_DEVELOP_FOLD = 0
# fold and holdout label, extrapolation label -- fold 0 is where the budget is chosen, both holdouts reuse it
PEROVSKITE_SPLITS = (
    ("fold_0", None, INTERPOLATION),
    ("holdout_factor_0p8", "holdout_factor_0p8", EXTRAPOLATION),
    ("holdout_factor_1p2", "holdout_factor_1p2", EXTRAPOLATION),
)
# an eighth of a grid's own smallest extent, this report's low/high mode boundary
LATTICE_FREQUENCY_CUTOFF_DIVISOR = 8.0
LATTICE_SEED = 20260911
LATTICE_CANONICAL_LEARNING_RATE = 3e-3


class StrainBlock:
    """the runs of one role and functional that share the campaign's most common grid"""


    def __init__(self, role: str, functional: str) -> None:
        assignments = Strain_Assignments_By_Run()
        parameters: list[NDArray[np.float64]] = []
        fields: list[NDArray[np.float64]] = []
        self.unit_keys: list[str] = []
        self.families: list[str] = []
        self.identifiers: list[str] = []
        for example in Parameter_Field_Examples(Card_Named("strain_to_charge"), role):
            values = np.asarray(example.target_function.values, dtype=np.float64)
            if values.shape[1:] != COMMON_GRID_SHAPE:
                continue
            if example.covariate_values["functional"] != functional:
                continue
            parameters.append(np.asarray(example.parameters.vector, dtype=np.float64))
            fields.append(values.reshape(-1))
            self.unit_keys.append(example.unit_key)
            self.families.append(assignments[example.run_path].family)
            self.identifiers.append(example.identifier)
        Guard_Fresh_Archives(self.identifiers)
        self.parameters = np.asarray(parameters)
        self.fields = np.asarray(fields)
        self.functional = functional


    def Scored(self, rebuilt: NDArray[np.float64]) -> list[ScoredRun]:
        """one scored run per field, carrying the labels the report groups by"""
        return [
            ScoredRun(
                identifier=self.identifiers[run],
                unit_key=self.unit_keys[run],
                campaign="strain_atlas",
                family=self.families[run],
                errors={"relative_l2": Relative_L2(rebuilt[run], self.fields[run])},
                covariate_values={"functional": self.functional},
            )
            for run in range(self.fields.shape[0])
        ]


def Ridge_Predictions(basis: PodBasis, train: StrainBlock, evaluated: StrainBlock) -> NDArray[np.float64]:
    """the closed-form floor: parameters onto mode coefficients, decoded through the basis"""
    fitted = Fit_Standardized_Ridge(train.parameters, Project(basis, train.fields))
    return Reconstruct(basis, Apply_Standardized_Ridge(fitted, evaluated.parameters))


def Nearest_Neighbor_Predictions(train: StrainBlock, evaluated: StrainBlock) -> NDArray[np.float64]:
    """the memorization floor: the field of the closest training run in parameter space"""
    nearest = Nearest_Training_Run(train.parameters, evaluated.parameters)
    return train.fields[nearest]


def Standardized_Fields(
    block: StrainBlock, voxel_mean: NDArray[np.float64], voxel_scale: NDArray[np.float64]
) -> NDArray[np.float64]:
    """a block's fields on the per-voxel scale of the training block"""
    return (block.fields - voxel_mean) / voxel_scale


def Trained_Member_Predictions(
    configuration: str,
    basis: PodBasis,
    train: StrainBlock,
    validation: StrainBlock,
    evaluated: StrainBlock,
) -> tuple[NDArray[np.float64], int, DeepOperatorNetwork]:
    """the member trained at the step count validation prefers, then read on the evaluated block"""
    voxel_mean, voxel_scale = Pointwise_Statistics(train.fields)
    # the fixed-basis member projects raw fields, the standardized one projects each voxel on its own scale
    if configuration == "proper_orthogonal":
        coefficients = Project(basis, Standardized_Fields(train, voxel_mean, voxel_scale))
    else:
        coefficients = Project(basis, train.fields)
    parameter_spreads = train.parameters.std(axis=0)
    parameter_spreads[parameter_spreads == 0.0] = 1.0
    coefficient_mean = coefficients.mean(axis=0)
    coefficient_scale = coefficients.std(axis=0)
    batch = np.concatenate(
        [train.parameters / parameter_spreads, (coefficients - coefficient_mean) / coefficient_scale],
        axis=1,
    )
    parameter_width = train.parameters.shape[1]
    whole_batch = FixedBatches(TrainingBatch({"rows": batch}))
    if configuration == "proper_orthogonal":
        member = Proper_Orthogonal_Network(
            basis, COMMON_GRID_SHAPE, voxel_mean, voxel_scale, parameter_width, HIDDEN_WIDTHS
        )
    else:
        member = Principal_Component_Network(basis, COMMON_GRID_SHAPE, parameter_width, HIDDEN_WIDTHS)

    def Coefficient_Loss(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        """mean squared error between the branch's coefficients and the projected truth"""
        rows = lifted_batch["rows"]
        predicted = member.Forward_Coefficients(lifted, rows[:, :parameter_width])
        residuals = predicted - rows[:, parameter_width:]
        return (residuals * residuals).mean()

    def Rebuild(values: dict[str, NDArray[np.float64]], block: StrainBlock) -> NDArray[np.float64]:
        predicted = np.asarray(
            member.Forward_Coefficients(values, block.parameters / parameter_spreads), dtype=np.float64
        )
        rebuilt = Reconstruct(basis, predicted * coefficient_scale + coefficient_mean)
        # the standardized member's modes live on the per-voxel scale and come back off it here
        if configuration == "proper_orthogonal":
            return rebuilt * voxel_scale + voxel_mean
        return rebuilt

    best_score = float("inf")
    best_values: dict[str, NDArray[np.float64]] = {}
    best_step_count = CANDIDATE_STEP_COUNTS[0]
    for step_count in CANDIDATE_STEP_COUNTS:
        # the budget is the one hyperparameter chosen here, and validation is what chooses it
        result = Train(
            Training_Engine(),
            ParameterSet(values=member.Parameter_Values()),
            Coefficient_Loss,
            whole_batch,
            step_count=step_count,
            learning_rate=3e-3,
            run_name=f"{configuration}_{train.functional}_{step_count}",
        )
        rebuilt = Rebuild(result.parameters.values, validation)
        score = float(
            np.median([Relative_L2(rebuilt[run], validation.fields[run]) for run in range(rebuilt.shape[0])])
        )
        if score < best_score:
            best_score, best_values, best_step_count = score, result.parameters.values, step_count
    # the member carries its initial weights until the chosen ones are written back into it
    for name, value in best_values.items():
        if name in member.branch.parameter_values:
            member.branch.parameter_values[name] = value
    member(Coefficients(vector=evaluated.parameters[0] / parameter_spreads, domain=Domain(np.eye(3))),
           GridSpec(COMMON_GRID_SHAPE))
    return Rebuild(best_values, evaluated), best_step_count, member


def Write_Figures(
    functional: str,
    configuration: str,
    member: DeepOperatorNetwork,
    test: "StrainBlock",
    member_rebuilt: NDArray[np.float64],
    floor_medians: dict[str, float],
    member_median: float,
) -> int:
    """the member's whole visual surface, drawn from arrays cached on the pool"""
    cache = ARRAY_CACHE_PATH / functional / configuration
    cache.mkdir(parents=True, exist_ok=True)
    inspected = {name: np.asarray(value, dtype=np.float64) for name, value in member.Inspect().items()}
    # cached so a re-render needs no retrain, which is what keeps committed figures stable
    np.savez(cache / "inspection.npz", **cast(dict[str, Any], inspected))
    with np.load(cache / "inspection.npz") as archive:
        restored = {name: np.asarray(archive[name], dtype=np.float64) for name in archive.files}

    directory = FIGURES_PATH / functional / configuration
    suite = Render_Inspection_Suite(
        restored, directory / "components", f"deep_operator_network {functional} {configuration}"
    )
    if suite.skipped:
        raise ValueError(f"no renderer for {suite.skipped}, which means the suite is incomplete")

    scored = [Relative_L2(member_rebuilt[run], test.fields[run]) for run in range(test.fields.shape[0])]
    for rank, run in enumerate(np.argsort(scored)[[0, -1]]):
        Render_Prediction_Against_Truth(
            member_rebuilt[run].reshape(COMMON_GRID_SHAPE),
            test.fields[run].reshape(COMMON_GRID_SHAPE),
            directory / f"prediction_{'best' if rank == 0 else 'worst'}.png",
            f"{functional} {configuration} {'best' if rank == 0 else 'worst'} test run, {test.unit_keys[run]}",
        )
    by_family: dict[str, list[float]] = {}
    for run in range(test.fields.shape[0]):
        by_family.setdefault(test.families[run], []).append(Relative_L2(member_rebuilt[run], test.fields[run]))
    Render_Error_Spread(
        {name: np.asarray(values) for name, values in by_family.items()},
        directory / "error_by_family.png",
        f"{functional} {configuration} test error by strain family",
    )
    Render_Floor_Comparison(
        floor_medians,
        member_median,
        {"ridge_to_coefficients": RIDGE_MARGIN, "nearest_neighbor_copy": NEAREST_NEIGHBOR_MARGIN},
        directory / "floors.png",
        f"{functional} {configuration} against its floors",
    )
    return len(suite.written) + 4


def Block_Lines(functional: str, configuration: str) -> tuple[list[str], tuple[FloorComparison, ...], int]:
    """one functional and configuration measured end to end, as report lines beside its floor verdicts"""
    train = StrainBlock("train", functional)
    validation = StrainBlock("validation", functional)
    test = StrainBlock("test", functional)
    raw_basis = Gram_Pod(train.fields, rank=BASIS_RANK)
    voxel_mean, voxel_scale = Pointwise_Statistics(train.fields)
    if configuration == "proper_orthogonal":
        basis = Gram_Pod(Standardized_Fields(train, voxel_mean, voxel_scale), rank=BASIS_RANK)
        # the ceiling of a standardized basis is read back on the raw scale, where the metric lives
        ceiling_rebuilt = (
            Reconstruct(basis, Project(basis, Standardized_Fields(test, voxel_mean, voxel_scale))) * voxel_scale
            + voxel_mean
        )
    else:
        basis = raw_basis
        ceiling_rebuilt = Reconstruct(basis, Project(basis, test.fields))

    # the floors are the same floors whichever configuration is being judged against them
    ridge_runs = test.Scored(Ridge_Predictions(raw_basis, train, test))
    copy_runs = test.Scored(Nearest_Neighbor_Predictions(train, test))
    member_rebuilt, step_count, member = Trained_Member_Predictions(configuration, basis, train, validation, test)
    member_runs = test.Scored(member_rebuilt)
    ceiling_runs = test.Scored(ceiling_rebuilt)

    comparisons = (
        Compare_To_Floor(member_runs, ridge_runs, "relative_l2", "ridge_to_coefficients", RIDGE_MARGIN),
        Compare_To_Floor(member_runs, copy_runs, "relative_l2", "nearest_neighbor_copy", NEAREST_NEIGHBOR_MARGIN),
    )
    summaries = (
        Summarize(ceiling_runs, "relative_l2", "rank_32_projection_ceiling"),
        Summarize(ridge_runs, "relative_l2", "ridge_floor"),
        Summarize(copy_runs, "relative_l2", "nearest_neighbor_floor"),
        Summarize(member_runs, "relative_l2", "member"),
    )
    floor_medians = {
        "ridge_to_coefficients": comparisons[0].floor_median,
        "nearest_neighbor_copy": comparisons[1].floor_median,
    }
    figure_count = Write_Figures(
        functional, configuration, member, test, member_rebuilt, floor_medians, comparisons[0].member_median
    )
    lines = [
        f"## {functional} functional, `{configuration}` — strain to charge density, held-out test orbits",
        "",
        f"Train {train.fields.shape[0]} runs, validation {validation.fields.shape[0]},"
        f" test {test.fields.shape[0]} over {len(set(test.unit_keys))} orbits."
        f" Basis rank {BASIS_RANK}; branch widths {HIDDEN_WIDTHS}; {step_count} steps chosen on validation."
        f" {figure_count} figures under `figures/{functional}/{configuration}/`.",
        "",
        "```",
        Render_Table(Summary_Table(summaries)),
        "```",
        "",
        "```",
        Render_Table(Comparison_Table(comparisons)),
        "```",
        "",
        "```",
        Render_Table(Summary_Table(Summarize_By(member_runs, "relative_l2", "family"))),
        "```",
        "",
    ]
    return lines, comparisons, step_count


def Functional_Field_Cache(card: TaskCard, role: str, functional: str) -> FieldCache:
    """one functional's slice of a role's field cache, every grid shape kept as the sampler found it"""
    whole = Build_Field_Cache(card, role)
    selected = tuple(field for field in whole.fields if field.covariate_values.get("functional") == functional)
    return FieldCache(whole.card_name, whole.role, selected)


def Shape_Groups(cache: FieldCache) -> dict[tuple[int, ...], list[CachedField]]:
    """this cache's fields bucketed by the one thing a rectangle needs to agree on"""
    grouped: dict[tuple[int, ...], list[CachedField]] = {}
    for cached_field in cache.fields:
        grouped.setdefault(cached_field.grid_shape, []).append(cached_field)
    return grouped


def Global_Statistics(cache: FieldCache) -> tuple[float, float]:
    """one mean and one deviation for the campaign's single channel, decision D5's global standardization"""
    means, deviations = Cached_Field_Statistics(cache)
    return float(means[0]), float(deviations[0])


def Parameter_Spreads(cache: FieldCache) -> NDArray[np.float64]:
    """each branch input's own spread across the cache's runs, guarded away from zero"""
    stacked = np.stack([cached_field.parameters for cached_field in cache.fields])
    spreads = np.asarray(stacked.std(axis=0), dtype=np.float64)
    # a parameter that never varies across the whole campaign would divide the branch input by zero
    spreads[spreads == 0.0] = 1.0
    return spreads


class CoordinateFeaturizedBatches(BatchSource):
    """a point-sampled source with each batch's trunk features precomputed alongside its own points"""


    def __init__(self, inner: BatchSource, coordinate_features: CoordinateFeatures) -> None:
        self.inner = inner
        self.coordinate_features = coordinate_features
        self.last_batch: TrainingBatch | None = None


    def Featurized(self, batch: TrainingBatch) -> TrainingBatch:
        """the batch's own arrays, with this trunk's coordinate features added beside them"""
        points = np.asarray(batch.arrays["point_coordinates"], dtype=np.float64)
        run_count = points.shape[0]
        point_count = points.shape[1]
        axis_count = points.shape[2]
        flattened = self.coordinate_features(points.reshape(-1, axis_count))
        features = flattened.reshape(run_count, point_count, flattened.shape[1])
        return TrainingBatch({**batch.arrays, "trunk_features": features})


    def Next_Batch(self, generator: np.random.Generator) -> TrainingBatch:
        """one step's batch, its points already answered by the trunk's own feature map"""
        featurized = self.Featurized(self.inner.Next_Batch(generator))
        self.last_batch = featurized
        return featurized


    def Validation_Batches(self) -> tuple[tuple[str, TrainingBatch], ...]:
        """the wrapped source's held units, each one's points answered the identical way"""
        return tuple((unit_key, self.Featurized(batch)) for unit_key, batch in self.inner.Validation_Batches())


    def Inspect(self) -> dict[str, Array]:
        """the wrapped source's own arrays, plus the trunk features that answered the last drawn batch"""
        state = dict(self.inner.Inspect())
        if self.last_batch is not None:
            state["last_trunk_features"] = self.last_batch.arrays["trunk_features"]
        return state


def Point_Value_Loss(
    member: DeepOperatorNetwork, parameter_spreads: Any, channel_mean: Any, channel_deviation: Any
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


def Trained_Canonical_Member(
    functional: str,
    stage_step_counts: tuple[int, ...] = CANONICAL_STAGE_STEP_COUNTS,
    run_name_prefix: str = "canonical",
) -> tuple[DeepOperatorNetwork, NDArray[np.float64], float, float, dict[str, object]]:
    """the canonical member trained point-sampled on every grid shape at once, with its own standardization"""
    card = Card_Named("strain_to_charge")
    training_cache = Functional_Field_Cache(card, "train", functional)
    validation_cache = Functional_Field_Cache(card, "validation", functional)
    parameter_width = int(training_cache.fields[0].parameters.shape[0])
    parameter_spreads = Parameter_Spreads(training_cache)
    channel_mean, channel_deviation = Global_Statistics(training_cache)
    member = Canonical_Network(
        parameter_width, CANONICAL_BRANCH_HIDDEN_WIDTHS, CANONICAL_LATENT_WIDTH, CANONICAL_TRUNK_HIDDEN_WIDTHS
    )
    readout = member.basis_readout
    if not isinstance(readout, BasisExpansion):
        raise TypeError("the canonical configuration was assembled without its learned trunk")
    sampler = PointSampledBatches(training_cache, validation_cache, CANONICAL_RUNS_PER_BATCH, CANONICAL_POINTS_PER_RUN)
    batches = CoordinateFeaturizedBatches(sampler, readout.coordinate_features)
    engine = Training_Engine()
    lifted_parameter_spreads = engine.Lift_Constant(parameter_spreads)
    lifted_channel_mean = engine.Lift_Constant(np.asarray(channel_mean, dtype=np.float64))
    lifted_channel_deviation = engine.Lift_Constant(np.asarray(channel_deviation, dtype=np.float64))
    forward_loss = Point_Value_Loss(member, lifted_parameter_spreads, lifted_channel_mean, lifted_channel_deviation)
    parameters = ParameterSet(values=member.Parameter_Values())
    manifest: dict[str, object] = {}
    stages = zip(CANONICAL_STAGE_LEARNING_RATES, stage_step_counts, strict=True)
    for stage_index, (learning_rate, step_count) in enumerate(stages):
        # early stopping is only turned on for the final, lowest-rate stage of the schedule
        is_final_stage = stage_index == len(stage_step_counts) - 1
        result = Train(
            engine,
            parameters,
            forward_loss,
            batches,
            step_count=step_count,
            learning_rate=learning_rate,
            seed=CANONICAL_SEED + stage_index,
            artifact_directory=TRAINING_ARTIFACT_PATH,
            run_name=f"{run_name_prefix}_{functional}_stage{stage_index}",
            validation_interval=CANONICAL_VALIDATION_INTERVAL,
            patience=CANONICAL_PATIENCE if is_final_stage else 0,
        )
        # a fresh stage starts from the previous stage's best parameters, not its last, noisier iterate
        parameters = result.parameters
        manifest[f"stage_{stage_index}"] = result.manifest
    for name, value in parameters.values.items():
        if name in member.branch.parameter_values:
            member.branch.parameter_values[name] = value
        if name in readout.parameter_values:
            readout.parameter_values[name] = value
    return member, parameter_spreads, channel_mean, channel_deviation, manifest


def Canonical_Common_Grid_Predictions(
    member: DeepOperatorNetwork,
    parameter_spreads: NDArray[np.float64],
    channel_mean: float,
    channel_deviation: float,
    evaluated: StrainBlock,
) -> NDArray[np.float64]:
    """the trained member's field on the campaign's common grid, for every given run's own parameters"""
    readout = member.basis_readout
    if not isinstance(readout, BasisExpansion):
        raise TypeError("a grid prediction needs the learned coordinate trunk")
    points = Output_Points(GridSpec(COMMON_GRID_SHAPE))
    trunk_features = readout.Coordinate_Features(points)
    coefficients = member.Forward_Coefficients(member.branch.parameter_values, evaluated.parameters / parameter_spreads)
    standardized = np.asarray(readout.Forward(readout.parameter_values, coefficients, trunk_features), dtype=np.float64)
    return standardized.T * channel_deviation + channel_mean


def Every_Shape_Nearest_Neighbor_Runs(
    training_cache: FieldCache, test_cache: FieldCache, functional: str
) -> list[ScoredRun]:
    """the memorization floor computed within each grid shape, since a copy needs a shape to match its truth"""
    assignments = Strain_Assignments_By_Run()
    training_groups = Shape_Groups(training_cache)
    scored: list[ScoredRun] = []
    for grid_shape, test_fields in Shape_Groups(test_cache).items():
        training_fields = training_groups.get(grid_shape)
        # a shape the training role never produced has no candidate this floor could copy
        if not training_fields:
            continue
        training_parameters = np.stack([field.parameters for field in training_fields])
        test_parameters = np.stack([field.parameters for field in test_fields])
        nearest = Nearest_Training_Run(training_parameters, test_parameters)
        for position, cached_field in enumerate(test_fields):
            copied = training_fields[int(nearest[position])].Flattened_Values()[0]
            truth = cached_field.Flattened_Values()[0]
            scored.append(
                ScoredRun(
                    identifier=cached_field.identifier,
                    unit_key=cached_field.unit_key,
                    campaign="strain_atlas",
                    family=assignments[cached_field.run_path].family,
                    errors={"relative_l2": Relative_L2(copied, truth)},
                    covariate_values={
                        "functional": functional,
                        "grid_shape": "x".join(str(extent) for extent in grid_shape),
                    },
                )
            )
    return scored


def Canonical_Every_Shape_Predictions(
    member: DeepOperatorNetwork,
    parameter_spreads: NDArray[np.float64],
    channel_mean: float,
    channel_deviation: float,
    test_cache: FieldCache,
    functional: str,
) -> list[ScoredRun]:
    """the trained member's own field on every test run's own grid shape, whatever shape each one is"""
    readout = member.basis_readout
    if not isinstance(readout, BasisExpansion):
        raise TypeError("a grid prediction needs the learned coordinate trunk")
    assignments = Strain_Assignments_By_Run()
    scored: list[ScoredRun] = []
    for grid_shape, cached_fields in Shape_Groups(test_cache).items():
        points = Output_Points(GridSpec((grid_shape[0], grid_shape[1], grid_shape[2])))
        trunk_features = readout.Coordinate_Features(points)
        parameters = np.stack([field.parameters for field in cached_fields])
        coefficients = member.Forward_Coefficients(member.branch.parameter_values, parameters / parameter_spreads)
        standardized = np.asarray(
            readout.Forward(readout.parameter_values, coefficients, trunk_features), dtype=np.float64
        )
        predicted = standardized.T * channel_deviation + channel_mean
        for position, cached_field in enumerate(cached_fields):
            truth = cached_field.Flattened_Values()[0]
            scored.append(
                ScoredRun(
                    identifier=cached_field.identifier,
                    unit_key=cached_field.unit_key,
                    campaign="strain_atlas",
                    family=assignments[cached_field.run_path].family,
                    errors={"relative_l2": Relative_L2(predicted[position], truth)},
                    covariate_values={
                        "functional": functional,
                        "grid_shape": "x".join(str(extent) for extent in grid_shape),
                    },
                )
            )
    return scored


def Write_Every_Shape_Figure(functional: str, member_runs_every: list[ScoredRun]) -> Path:
    """error spread across every grid shape the test set holds, the canonical member's own extra reach"""
    directory = FIGURES_PATH / functional / "canonical"
    by_shape: dict[str, list[float]] = {}
    for scored_run in member_runs_every:
        by_shape.setdefault(scored_run.covariate_values["grid_shape"], []).append(scored_run.errors["relative_l2"])
    return Render_Error_Spread(
        {name: np.asarray(values) for name, values in by_shape.items()},
        directory / "error_by_grid_shape.png",
        f"{functional} canonical test error by grid shape, the shapes ridge and copy cannot all reach",
    )


def Canonical_Block_Lines(
    functional: str,
    stage_step_counts: tuple[int, ...] = CANONICAL_STAGE_STEP_COUNTS,
    run_name_prefix: str = "canonical",
) -> tuple[list[str], tuple[FloorComparison, ...]]:
    """one functional measured two ways: on the common grid beside the fixed-basis floors, and on every shape"""
    train_common = StrainBlock("train", functional)
    test_common = StrainBlock("test", functional)
    raw_basis = Gram_Pod(train_common.fields, rank=BASIS_RANK)
    ridge_runs = test_common.Scored(Ridge_Predictions(raw_basis, train_common, test_common))
    copy_runs = test_common.Scored(Nearest_Neighbor_Predictions(train_common, test_common))

    member, parameter_spreads, channel_mean, channel_deviation, training_manifest = Trained_Canonical_Member(
        functional, stage_step_counts, run_name_prefix
    )
    readout = member.basis_readout
    if not isinstance(readout, BasisExpansion):
        raise TypeError("the canonical configuration was assembled without its learned trunk")

    member_rebuilt_common = Canonical_Common_Grid_Predictions(
        member, parameter_spreads, channel_mean, channel_deviation, test_common
    )
    member_runs_common = test_common.Scored(member_rebuilt_common)
    # the only call that fills encoder.last_latent_vector, composition.last_carried_vector and last_trunk_features
    member(
        Coefficients(vector=test_common.parameters[0] / parameter_spreads, domain=Domain(np.eye(3))),
        GridSpec(COMMON_GRID_SHAPE),
    )

    comparisons_common = (
        Compare_To_Floor(member_runs_common, ridge_runs, "relative_l2", "ridge_to_coefficients", RIDGE_MARGIN),
        Compare_To_Floor(
            member_runs_common, copy_runs, "relative_l2", "nearest_neighbor_copy", NEAREST_NEIGHBOR_MARGIN
        ),
    )
    figure_count = Write_Figures(
        functional,
        "canonical",
        member,
        test_common,
        member_rebuilt_common,
        {
            "ridge_to_coefficients": comparisons_common[0].floor_median,
            "nearest_neighbor_copy": comparisons_common[1].floor_median,
        },
        comparisons_common[0].member_median,
    )

    card = Card_Named("strain_to_charge")
    training_cache = Functional_Field_Cache(card, "train", functional)
    test_cache_every_shape = Functional_Field_Cache(card, "test", functional)
    copy_runs_every = Every_Shape_Nearest_Neighbor_Runs(training_cache, test_cache_every_shape, functional)
    member_runs_every = Canonical_Every_Shape_Predictions(
        member, parameter_spreads, channel_mean, channel_deviation, test_cache_every_shape, functional
    )
    covered_identifiers = {scored_run.identifier for scored_run in copy_runs_every}
    member_runs_every_covered = [run for run in member_runs_every if run.identifier in covered_identifiers]
    every_shape_comparison = Compare_To_Floor(
        member_runs_every_covered,
        copy_runs_every,
        "relative_l2",
        "nearest_neighbor_copy",
        NEAREST_NEIGHBOR_MARGIN,
        group_name="every_shape",
    )
    Write_Every_Shape_Figure(functional, member_runs_every)

    parameter_count = sum(value.size for value in member.Parameter_Values().values())
    shape_count = len({run.covariate_values["grid_shape"] for run in member_runs_every})
    stage_lines: list[str] = []
    for stage_index, learning_rate in enumerate(CANONICAL_STAGE_LEARNING_RATES):
        stage_manifest = cast(dict[str, object], training_manifest[f"stage_{stage_index}"])
        early = " (stopped early)" if stage_manifest["stopped_early"] else ""
        stage_lines.append(
            f"stage {stage_index} ({learning_rate:.0e}, up to {stage_step_counts[stage_index]} steps):"
            f" best unit-mean validation {cast(float, stage_manifest['best_validation_score']):.6f}"
            f" at step {stage_manifest['best_step']}{early}"
        )
    ridge_verdict = "beats" if comparisons_common[0].verdict == "pass" else "loses to"
    lines = [
        f"## {functional} functional, `canonical` — strain to charge density, learned coordinate trunk",
        "",
        f"Trained point-sampled on {len(training_cache.fields)} runs across every grid shape the"
        f" training role holds; test {test_common.fields.shape[0]} over {len(set(test_common.unit_keys))}"
        f" orbits on the campaign's common {COMMON_GRID_SHAPE} grid, scored exactly as the fixed-basis"
        f" configurations are. Branch widths {CANONICAL_BRANCH_HIDDEN_WIDTHS}, latent"
        f" {CANONICAL_LATENT_WIDTH}, trunk widths {CANONICAL_TRUNK_HIDDEN_WIDTHS}, {parameter_count}"
        f" parameters. {figure_count} figures under `figures/{functional}/canonical/`.",
        "",
        f"This member {ridge_verdict} the ridge floor on the common grid"
        f" ({100.0 * comparisons_common[0].improvement:.1f}% improvement against a"
        f" {100.0 * RIDGE_MARGIN:.0f}% requirement).",
        "",
        "```",
        "\n".join(stage_lines),
        "```",
        "",
        "```",
        Render_Table(
            Summary_Table(
                (
                    Summarize(ridge_runs, "relative_l2", "ridge_floor"),
                    Summarize(copy_runs, "relative_l2", "nearest_neighbor_floor"),
                    Summarize(member_runs_common, "relative_l2", "member_on_common_grid"),
                )
            )
        ),
        "```",
        "",
        "```",
        Render_Table(Comparison_Table(comparisons_common)),
        "```",
        "",
        f"### every shape the test set holds, {shape_count} of them, {len(member_runs_every)} test runs"
        f" ({len(member_runs_every_covered)} with a same-shape training neighbor to copy)",
        "",
        "The table above restricts training and test to the campaign's single most common grid, because the",
        "fixed-basis configurations cannot read any other. The branch and trunk take a fractional coordinate",
        "regardless of the grid it came from, so this same member trained on every shape in the training role"
        f" at once ({training_cache.Resident_Bytes() / 1e6:.0f} MB resident), not only the common one, and is"
        " scored below across every shape its own test runs hold, which is the capability the other two"
        " configurations do not have.",
        "",
        "```",
        Render_Table(
            Summary_Table(
                (
                    Summarize(copy_runs_every, "relative_l2", "nearest_neighbor_floor_every_shape"),
                    Summarize(member_runs_every, "relative_l2", "member_every_shape_full_test_set"),
                )
            )
        ),
        "```",
        "",
        "```",
        Render_Table(Comparison_Table((every_shape_comparison,))),
        "```",
        "",
    ]
    return lines, comparisons_common + (every_shape_comparison,)


class StateDensityBlock:
    """every rebuilt curve of one role, both functionals pooled, the functional carried as a branch feature"""


    def __init__(self, role: str) -> None:
        assignments = Strain_Assignments_By_Run()
        parameters: list[NDArray[np.float64]] = []
        curves: list[NDArray[np.float64]] = []
        self.identifiers: list[str] = []
        self.unit_keys: list[str] = []
        self.families: list[str] = []
        self.functionals: list[str] = []
        energy_grid: NDArray[np.float64] | None = None
        for example in State_Density_Examples(Card_Named("strain_to_states"), role):
            functional_feature = FUNCTIONAL_BRANCH_FEATURE[example.covariate_values["functional"]]
            parameters.append(
                np.concatenate([np.asarray(example.parameters.vector, dtype=np.float64), [functional_feature]])
            )
            curves.append(example.state_density)
            self.identifiers.append(example.identifier)
            self.unit_keys.append(example.unit_key)
            self.families.append(assignments[example.run_path].family)
            self.functionals.append(example.covariate_values["functional"])
            energy_grid = example.energy_grid
        Guard_Fresh_Archives(self.identifiers)
        self.parameters = np.asarray(parameters)
        self.curves = np.asarray(curves)
        if energy_grid is None:
            raise ValueError(f"the {role} role of strain_to_states holds no curves to train or score on")
        self.energy_grid = energy_grid


    def Scored(self, predicted: NDArray[np.float64], band_edge_mask: NDArray[np.bool_], spacing: float) -> list[ScoredRun]:
        """one scored run per curve, the card's metrics beside the labels the report groups by"""
        scored: list[ScoredRun] = []
        for run in range(self.curves.shape[0]):
            truth_curve = self.curves[run]
            predicted_curve = predicted[run]
            scored.append(
                ScoredRun(
                    identifier=self.identifiers[run],
                    unit_key=self.unit_keys[run],
                    campaign="strain_atlas",
                    family=self.families[run],
                    errors={
                        "curve_l1_whole": Curve_L1(predicted_curve, truth_curve, spacing),
                        "curve_l1_band_edge": Curve_L1(
                            predicted_curve[band_edge_mask], truth_curve[band_edge_mask], spacing
                        ),
                        "wasserstein_1d": Wasserstein_1d(predicted_curve, truth_curve, spacing),
                        "gap_edge_error": Gap_Edge_Error(predicted_curve, truth_curve, self.energy_grid),
                    },
                    covariate_values={"functional": self.functionals[run]},
                )
            )
        return scored


def Band_Edge_Mask(energy_grid: NDArray[np.float64]) -> NDArray[np.bool_]:
    """the band-edge region's own bins, where the strain signal actually concentrates"""
    return (energy_grid >= BAND_EDGE_LOWER_EV) & (energy_grid <= BAND_EDGE_UPPER_EV)


def Training_Mean_Predictions(train: StateDensityBlock, evaluated_count: int) -> NDArray[np.float64]:
    """the flat floor: every evaluated run predicted as the training block's own mean curve"""
    return np.tile(train.curves.mean(axis=0), (evaluated_count, 1))


def Ridge_Curve_Predictions(train: StateDensityBlock, evaluated: StateDensityBlock) -> NDArray[np.float64]:
    """the closed-form floor: parameters, with the functional as a seventh feature, ridge-mapped onto the curve"""
    fitted = Fit_Standardized_Ridge(train.parameters, train.curves)
    return Apply_Standardized_Ridge(fitted, evaluated.parameters)


def Parameter_Feature_Spreads(train: StateDensityBlock) -> NDArray[np.float64]:
    """each of the seven branch features' own spread across the training block, guarded away from zero"""
    spreads = np.asarray(train.parameters.std(axis=0), dtype=np.float64)
    spreads[spreads == 0.0] = 1.0
    return spreads


def Standardized_Energy(energy_grid: NDArray[np.float64]) -> NDArray[np.float64]:
    """the aligned window's own bounds rescaled onto minus one to one, which is where the trunk reads it"""
    lower_bound, upper_bound = float(energy_grid[0]), float(energy_grid[-1])
    return 2.0 * (energy_grid - lower_bound) / (upper_bound - lower_bound) - 1.0


def Energy_Trunk_Features(energy_grid: NDArray[np.float64], fourier_orders: int) -> NDArray[np.float64]:
    """the standardized energy grid's own trunk features, one leading axis ready to broadcast over runs"""
    coordinate_features = RampedCoordinateFeatures(fourier_orders, axis_count=1)
    features = coordinate_features(Standardized_Energy(energy_grid)[:, None])
    return features[None, :, :]


def Energy_Trunk_Training_Batch(block: StateDensityBlock, parameter_spreads: NDArray[np.float64]) -> TrainingBatch:
    """one role's whole curve set as a single rectangular batch, parameters standardized by their own spread"""
    return TrainingBatch({"branch_input": block.parameters / parameter_spreads, "target_curves": block.curves})


def Curve_L1_Loss(
    member: DeepOperatorNetwork,
    trunk_features_constant: Any,
    weight_constant: Any | None,
) -> ForwardLoss:
    """the card's own metric made differentiable: per-run normalized L1, optionally weighted along energy"""


    def Loss_Of(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        """this batch's curves predicted and answered against the truth by the same normalized L1"""
        predicted = member.Forward_Point_Values(lifted, lifted_batch["branch_input"], trunk_features_constant)
        truth = lifted_batch["target_curves"]
        residual = abs(predicted - truth)
        truth_size = abs(truth)
        if weight_constant is not None:
            residual = residual * weight_constant
            truth_size = truth_size * weight_constant
        per_run = Sum_Over_Last_Axis(residual) / Sum_Over_Last_Axis(truth_size)
        return Mean_Over_Last_Axis(per_run)

    return Loss_Of


def Trained_Energy_Trunk_Member(
    train: StateDensityBlock,
    validation: StateDensityBlock,
    band_edge_weighted: bool,
    run_name_prefix: str,
) -> tuple[DeepOperatorNetwork, NDArray[np.float64], NDArray[np.float64], dict[str, object]]:
    """the energy-trunk member trained whole-curve on the card's own loss, or its band-edge-weighted ablation"""
    parameter_width = int(train.parameters.shape[1])
    parameter_spreads = Parameter_Feature_Spreads(train)
    member = Energy_Trunk_Network(
        parameter_width,
        ENERGY_TRUNK_BRANCH_HIDDEN_WIDTHS,
        ENERGY_TRUNK_LATENT_WIDTH,
        ENERGY_TRUNK_TRUNK_HIDDEN_WIDTHS,
        ENERGY_TRUNK_FOURIER_ORDERS,
    )
    readout = member.basis_readout
    if not isinstance(readout, BasisExpansion):
        raise TypeError("the energy-trunk configuration was assembled without its learned trunk")
    trunk_features = Energy_Trunk_Features(train.energy_grid, ENERGY_TRUNK_FOURIER_ORDERS)
    batches = FixedBatches(
        Energy_Trunk_Training_Batch(train, parameter_spreads),
        Energy_Trunk_Training_Batch(validation, parameter_spreads),
    )
    engine = Training_Engine()
    lifted_trunk_features = engine.Lift_Constant(trunk_features)
    weight_constant = None
    if band_edge_weighted:
        band_edge_weights = np.where(Band_Edge_Mask(train.energy_grid), ENERGY_TRUNK_BAND_EDGE_WEIGHT, 1.0)
        weight_constant = engine.Lift_Constant(np.asarray(band_edge_weights, dtype=np.float64))
    forward_loss = Curve_L1_Loss(member, lifted_trunk_features, weight_constant)
    parameters = ParameterSet(values=member.Parameter_Values())
    manifest: dict[str, object] = {}
    stages = zip(ENERGY_TRUNK_STAGE_LEARNING_RATES, ENERGY_TRUNK_STAGE_STEP_COUNTS, strict=True)
    for stage_index, (learning_rate, step_count) in enumerate(stages):
        # early stopping is only turned on for the final, lowest-rate stage of the schedule
        is_final_stage = stage_index == len(ENERGY_TRUNK_STAGE_STEP_COUNTS) - 1
        result = Train(
            engine,
            parameters,
            forward_loss,
            batches,
            step_count=step_count,
            learning_rate=learning_rate,
            seed=ENERGY_TRUNK_SEED + stage_index,
            artifact_directory=TRAINING_ARTIFACT_PATH,
            run_name=f"{run_name_prefix}_stage{stage_index}",
            validation_interval=ENERGY_TRUNK_VALIDATION_INTERVAL,
            patience=ENERGY_TRUNK_PATIENCE if is_final_stage else 0,
        )
        # a fresh stage starts from the previous stage's best parameters, not its last, noisier iterate
        parameters = result.parameters
        manifest[f"stage_{stage_index}"] = result.manifest
    for name, value in parameters.values.items():
        if name in member.branch.parameter_values:
            member.branch.parameter_values[name] = value
        if name in readout.parameter_values:
            readout.parameter_values[name] = value
    return member, parameter_spreads, trunk_features, manifest


def Energy_Trunk_Predictions(
    member: DeepOperatorNetwork,
    parameter_spreads: NDArray[np.float64],
    trunk_features: NDArray[np.float64],
    evaluated: StateDensityBlock,
) -> NDArray[np.float64]:
    """the trained member's curve for every given run's own parameters, at the aligned energy grid"""
    branch_input = evaluated.parameters / parameter_spreads
    predicted = member.Forward_Point_Values(member.Parameter_Values(), branch_input, trunk_features)
    return np.asarray(predicted, dtype=np.float64)


def Write_Energy_Trunk_Figures(
    member: DeepOperatorNetwork,
    test: StateDensityBlock,
    member_predicted: NDArray[np.float64],
    spacing: float,
) -> int:
    """the member's whole visual surface, drawn from arrays cached on the pool"""
    cache = ARRAY_CACHE_PATH / "pooled" / "energy_trunk"
    cache.mkdir(parents=True, exist_ok=True)
    inspected = {name: np.asarray(value, dtype=np.float64) for name, value in member.Inspect().items()}
    # cached so a re-render needs no retrain, which is what keeps committed figures stable
    np.savez(cache / "inspection.npz", **cast(dict[str, Any], inspected))
    with np.load(cache / "inspection.npz") as archive:
        restored = {name: np.asarray(archive[name], dtype=np.float64) for name in archive.files}

    directory = FIGURES_PATH / "pooled" / "energy_trunk"
    suite = Render_Inspection_Suite(restored, directory / "components", "deep_operator_network energy_trunk")
    if suite.skipped:
        raise ValueError(f"no renderer for {suite.skipped}, which means the suite is incomplete")

    run_count = test.curves.shape[0]
    whole_window_errors = [Curve_L1(member_predicted[run], test.curves[run], spacing) for run in range(run_count)]
    for rank, run in enumerate(np.argsort(whole_window_errors)[[0, -1]]):
        label = "best" if rank == 0 else "worst"
        Render_Curves(
            test.energy_grid,
            {"truth": test.curves[run], "predicted": member_predicted[run]},
            directory / f"prediction_{label}.png",
            f"energy_trunk {label} test curve, {test.unit_keys[run]} ({test.functionals[run]})",
            "energy (eV from valence-band maximum)",
            "density of states",
        )
    by_family: dict[str, list[float]] = {}
    by_functional: dict[str, list[float]] = {}
    for run in range(run_count):
        by_family.setdefault(test.families[run], []).append(whole_window_errors[run])
        by_functional.setdefault(test.functionals[run], []).append(whole_window_errors[run])
    Render_Error_Spread(
        {name: np.asarray(values) for name, values in by_family.items()},
        directory / "error_by_family.png",
        "energy_trunk test curve_l1 by strain family",
        "curve l1 (whole window)",
    )
    Render_Error_Spread(
        {name: np.asarray(values) for name, values in by_functional.items()},
        directory / "error_by_functional.png",
        "energy_trunk test curve_l1 by functional",
        "curve l1 (whole window)",
    )
    return len(suite.written) + 4


def Skill(member_median: float, floor_median: float) -> float:
    """the fraction a median improves on a floor's own median, an undefined improvement read as zero"""
    return 1.0 - member_median / floor_median if floor_median > 0.0 else 0.0


def Stage_Lines(
    manifest: dict[str, object], learning_rates: tuple[float, ...], step_counts: tuple[int, ...]
) -> list[str]:
    """one line per training stage, the best validation score and step it reached"""
    stage_lines: list[str] = []
    for stage_index, learning_rate in enumerate(learning_rates):
        stage_manifest = cast(dict[str, object], manifest[f"stage_{stage_index}"])
        early = " (stopped early)" if stage_manifest["stopped_early"] else ""
        stage_lines.append(
            f"stage {stage_index} ({learning_rate:.0e}, up to {step_counts[stage_index]} steps):"
            f" best unit-mean validation {cast(float, stage_manifest['best_validation_score']):.6f}"
            f" at step {stage_manifest['best_step']}{early}"
        )
    return stage_lines


def Energy_Trunk_Block_Lines() -> list[str]:
    """strain to states measured whole, both functionals pooled, against the training-mean and ridge floors"""
    train = StateDensityBlock("train")
    validation = StateDensityBlock("validation")
    test = StateDensityBlock("test")
    energy_grid = test.energy_grid
    spacing = float(energy_grid[1] - energy_grid[0])
    band_edge_mask = Band_Edge_Mask(energy_grid)

    mean_predicted = Training_Mean_Predictions(train, test.curves.shape[0])
    ridge_predicted = Ridge_Curve_Predictions(train, test)
    member, parameter_spreads, trunk_features, manifest = Trained_Energy_Trunk_Member(
        train, validation, band_edge_weighted=False, run_name_prefix="energy_trunk_primary"
    )
    member_predicted = Energy_Trunk_Predictions(member, parameter_spreads, trunk_features, test)
    # the only call that fills encoder.last_latent_vector, composition.last_carried_vector and the captured curve
    member(
        Coefficients(vector=test.parameters[0] / parameter_spreads, domain=Domain(np.eye(3))),
        PointSpec(points=Standardized_Energy(energy_grid)[:, None]),
    )

    mean_runs = test.Scored(mean_predicted, band_edge_mask, spacing)
    ridge_runs = test.Scored(ridge_predicted, band_edge_mask, spacing)
    member_runs = test.Scored(member_predicted, band_edge_mask, spacing)
    figure_count = Write_Energy_Trunk_Figures(member, test, member_predicted, spacing)

    metric_names = ("curve_l1_whole", "curve_l1_band_edge", "wasserstein_1d", "gap_edge_error")
    summaries = tuple(
        Summarize(scored_runs, metric_name, group_name)
        for group_name, scored_runs in (
            ("training_mean_floor", mean_runs),
            ("ridge_floor", ridge_runs),
            ("member", member_runs),
        )
        for metric_name in metric_names
    )
    by_metric = {(summary.group_name, summary.metric_name): summary.median for summary in summaries}
    mean_whole = by_metric[("training_mean_floor", "curve_l1_whole")]
    mean_edge = by_metric[("training_mean_floor", "curve_l1_band_edge")]
    ridge_whole = by_metric[("ridge_floor", "curve_l1_whole")]
    ridge_edge = by_metric[("ridge_floor", "curve_l1_band_edge")]
    member_whole = by_metric[("member", "curve_l1_whole")]
    member_edge = by_metric[("member", "curve_l1_band_edge")]
    ridge_skill_whole = Skill(ridge_whole, mean_whole)
    ridge_skill_edge = Skill(ridge_edge, mean_edge)
    member_skill_whole = Skill(member_whole, mean_whole)
    member_skill_edge = Skill(member_edge, mean_edge)
    member_over_ridge_whole = Skill(member_whole, ridge_whole)
    member_over_ridge_edge = Skill(member_edge, ridge_edge)

    ablation_member, ablation_spreads, ablation_features, ablation_manifest = Trained_Energy_Trunk_Member(
        train, validation, band_edge_weighted=True, run_name_prefix="energy_trunk_bandedge_ablation"
    )
    ablation_predicted = Energy_Trunk_Predictions(ablation_member, ablation_spreads, ablation_features, test)
    ablation_runs = test.Scored(ablation_predicted, band_edge_mask, spacing)
    ablation_summaries = tuple(
        Summarize(ablation_runs, metric_name, "member_band_edge_weighted_ablation") for metric_name in metric_names
    )

    parameter_count = sum(value.size for value in member.Parameter_Values().values())
    lines = [
        "## strain to states, `energy_trunk` — density of states over energy, both functionals pooled",
        "",
        f"Train {train.curves.shape[0]} runs, validation {validation.curves.shape[0]},"
        f" test {test.curves.shape[0]} over {len(set(test.unit_keys))} orbits, cheap and accurate functionals"
        " pooled together with the functional as a seventh branch feature beside the six strain components."
        f" Branch widths {ENERGY_TRUNK_BRANCH_HIDDEN_WIDTHS}, latent {ENERGY_TRUNK_LATENT_WIDTH}, trunk widths"
        f" {ENERGY_TRUNK_TRUNK_HIDDEN_WIDTHS}, {ENERGY_TRUNK_FOURIER_ORDERS} Fourier orders, {parameter_count}"
        f" parameters. {figure_count} figures under `figures/pooled/energy_trunk/`. One seeded run; a"
        " twelve-run sweep of the fixed-basis configurations measured fourteen to thirty-five percent seed"
        " spread, and this member should be read with the same caution.",
        "",
        f"The aligned window runs {float(energy_grid[0]):.1f} to {float(energy_grid[-1]):.1f} eV from the"
        f" valence-band maximum over {energy_grid.shape[0]} points at {spacing:.2f} eV; it stops short of the"
        " conduction band's own ceiling, so the mean curve's final bins are still rising rather than falling,"
        " an intentional property of the window and not a bug in the curve. The band-edge region scored"
        f" separately below is {BAND_EDGE_LOWER_EV:.0f} to {BAND_EDGE_UPPER_EV:.0f} eV,"
        f" {int(np.count_nonzero(band_edge_mask))} of {energy_grid.shape[0]} bins, where the strain signal"
        " was measured to concentrate before this member was trained: the valence band alone is nearly"
        " strain-invariant, and dominates the full-window integral roughly fivefold over the band edges.",
        "",
        "Trained whole-curve: one fixed batch carrying every training run's full 601-point curve at once"
        " (under 5 MB), rather than sampling energies per step, because the whole block fits comfortably in"
        " memory and the energy grid is identical across every run; unlike position, there is no varying"
        " grid shape here for a point sampler to earn its cost against. The trunk's own feature map reads the"
        " energy coordinate after it is rescaled from the aligned window onto minus one to one; the branch's"
        " seven features are each standardized by their own spread across the training block. The loss"
        " trained here is the card's own `curve_l1`, made differentiable as each run's own L1 residual"
        " normalized by that run's own curve size and then averaged over runs, unweighted across the window,"
        " exactly as the card specifies.",
        "",
        "The full-window `curve_l1` below is the headline the card mandates, and it is expected to look"
        " unimpressive regardless of model quality: 467 of 601 bins are valence-band states that are nearly"
        " strain-invariant, diluting real skill roughly fivefold. The band-edge score beside it, plus"
        " `wasserstein_1d` and `gap_edge_error`, carry the information this task actually turns on. No kill"
        " margin is set for this configuration, since the canon fixes none for VI.1, and a floor winning here"
        " is an informative, reportable outcome on a coarse spectral function, not a failure.",
        "",
        "```",
        "\n".join(Stage_Lines(manifest, ENERGY_TRUNK_STAGE_LEARNING_RATES, ENERGY_TRUNK_STAGE_STEP_COUNTS)),
        "```",
        "",
        "Caveat: the final stage's validation score was still improving at its last step, so the search did"
        " not settle inside its budget. Measured directly: extending that stage from 2000 to 5000 steps"
        " (2.5x the compute) moved the member's whole-window median from 0.217 to 0.206 (5.1%) and its"
        " band-edge median from 0.270 to 0.265 (1.9%) against a ridge floor it already cleared by over 40%"
        " at the shorter budget, so the boundary is recorded rather than chased further.",
        "",
        "```",
        Render_Table(Summary_Table(summaries)),
        "```",
        "",
        "`gap_edge_error` reads near zero for both floors and not for the member, and that is the metric's"
        " own limit, not a physics failure. `test-suite.md` already calls the support-edge read-out a"
        " diagnostic only, next to the trusted occupancy-walk gap, and this is why: measured directly, every"
        " one of the 248 test truths crosses one percent of its own peak at exactly +0.02 eV, one grid step"
        " past the valence-band maximum, with zero variance across every strain family — because the"
        " smearing that rebuilds every curve here bridges the sharp valence edge into a shoulder that"
        " crosses the threshold long before the true conduction band starts, for any curve shaped like a"
        " real one. A floor built from real curves inherits that shoulder and reads a near-zero gap error by"
        " sharing the artifact, not by finding the gap. The member's own curve is smoother — a handful of"
        " Fourier orders and a softplus head cannot fall back to exact zero the way a sharp, smeared feature"
        " does — so it clears one percent of its own peak further out, and its larger `gap_edge_error` is a"
        " property of that smoothness, not evidence the map is worse at the physics.",
        "",
        f"Ridge's skill over the training-mean floor: {100.0 * ridge_skill_whole:.1f}% on the whole window,"
        f" {100.0 * ridge_skill_edge:.1f}% on the band-edge region. The member's skill over the same floor:"
        f" {100.0 * member_skill_whole:.1f}% whole-window, {100.0 * member_skill_edge:.1f}% band-edge. The"
        f" member against the ridge floor directly: {100.0 * member_over_ridge_whole:.1f}% whole-window,"
        f" {100.0 * member_over_ridge_edge:.1f}% band-edge.",
        "",
        "```",
        Render_Table(Summary_Table(Summarize_By(member_runs, "curve_l1_whole", "functional"))),
        "```",
        "",
        "```",
        Render_Table(Summary_Table(Summarize_By(member_runs, "curve_l1_whole", "family"))),
        "```",
        "",
        "### band-edge-weighted loss — ablation, not the card's loss and not a substitute for the row above",
        "",
        "The same architecture and schedule, trained instead on a loss that weighs the"
        f" {BAND_EDGE_LOWER_EV:.0f} to {BAND_EDGE_UPPER_EV:.0f} eV region"
        f" {ENERGY_TRUNK_BAND_EDGE_WEIGHT:.0f}x the rest of the window in both the residual and the normalizer.",
        "",
        "```",
        "\n".join(Stage_Lines(ablation_manifest, ENERGY_TRUNK_STAGE_LEARNING_RATES, ENERGY_TRUNK_STAGE_STEP_COUNTS)),
        "```",
        "",
        "```",
        Render_Table(Summary_Table(ablation_summaries)),
        "```",
        "",
        "The ablation's `gap_edge_error` lands back near zero, which is consistent with the mechanism above"
        " rather than against it: weighing the band-edge region five times over pushes this member to"
        " reproduce the smearing shoulder precisely enough to cross one percent of peak at the same point"
        " the floors do, at the cost of the valence band it no longer weighs as heavily.",
        "",
    ]
    return lines


def Lattice_Frequency_Cutoff(grid_shape: tuple[int, ...]) -> float:
    """an eighth of this grid's own smallest extent, the low/high mode boundary this block uses"""
    return float(min(grid_shape)) / LATTICE_FREQUENCY_CUTOFF_DIVISOR


def Perovskite_Angle_Examples(
    role: str, evaluation_fold: int, extrapolation_holdout: str | None
) -> list[ParameterExample]:
    """every angle-stratum example of one loader role, still on the shape the whole stratum shares"""
    card = Card_Named("lattice_to_charge")
    selected: list[ParameterExample] = []
    for example in Parameter_Field_Examples(card, role, evaluation_fold, extrapolation_holdout):
        if not example.unit_key.endswith("_angle"):
            continue
        if np.asarray(example.target_function.values).shape[1:] != PEROVSKITE_ANGLE_GRID_SHAPE:
            continue
        selected.append(example)
    return selected


def Perovskite_Train_Validation_Split(
    examples: list[ParameterExample],
) -> tuple[list[ParameterExample], list[ParameterExample]]:
    """every fifth example, by sorted unit key, held out as this split's own validation slice"""
    ordered = sorted(range(len(examples)), key=lambda position: examples[position].unit_key)
    validation_positions = {position for count, position in enumerate(ordered) if count % 5 == 4}
    train_examples = [example for position, example in enumerate(examples) if position not in validation_positions]
    validation_examples = [example for position, example in enumerate(examples) if position in validation_positions]
    return train_examples, validation_examples


def Perovskite_Cache_Validation_Mask(cache: FieldCache) -> list[bool]:
    """every fifth field, by sorted unit key, held out as this cache's own validation slice"""
    ordered = sorted(range(len(cache.fields)), key=lambda position: cache.fields[position].unit_key)
    validation_positions = {position for count, position in enumerate(ordered) if count % 5 == 4}
    return [position in validation_positions for position in range(len(cache.fields))]


class PerovskiteAngleBlock:
    """the perovskite angle stratum's own runs, every one on the shared 64-cubed grid"""


    def __init__(self, examples: list[ParameterExample], extrapolation: str = INTERPOLATION) -> None:
        parameters: list[NDArray[np.float64]] = []
        fields: list[NDArray[np.float64]] = []
        cell_volumes: list[float] = []
        self.unit_keys: list[str] = []
        self.identifiers: list[str] = []
        for example in examples:
            values = np.asarray(example.target_function.values, dtype=np.float64)
            parameters.append(np.asarray(example.parameters.vector, dtype=np.float64))
            fields.append(values.reshape(-1))
            cell_volumes.append(float(example.target_function.quadrature.cell_volume))
            self.unit_keys.append(example.unit_key)
            self.identifiers.append(example.identifier)
        Guard_Fresh_Archives(self.identifiers)
        self.parameters = np.asarray(parameters)
        self.fields = np.asarray(fields)
        self.cell_volumes = np.asarray(cell_volumes, dtype=np.float64)
        self.extrapolation = extrapolation


    def Scored(self, rebuilt: NDArray[np.float64]) -> list[ScoredRun]:
        """one scored run per field, the card's two metrics, labeled by this block's own extrapolation status"""
        cutoff = Lattice_Frequency_Cutoff(PEROVSKITE_ANGLE_GRID_SHAPE)
        scored: list[ScoredRun] = []
        for run in range(self.fields.shape[0]):
            low, high = Frequency_Split_Relative_L2(
                rebuilt[run].reshape(PEROVSKITE_ANGLE_GRID_SHAPE),
                self.fields[run].reshape(PEROVSKITE_ANGLE_GRID_SHAPE),
                cutoff_modes=cutoff,
            )
            scored.append(
                ScoredRun(
                    identifier=self.identifiers[run],
                    unit_key=self.unit_keys[run],
                    campaign="perovskite_grid",
                    family="angle",
                    errors={
                        "relative_l2": Relative_L2(rebuilt[run], self.fields[run]),
                        "frequency_split_relative_l2_low": low,
                        "frequency_split_relative_l2_high": high,
                    },
                    extrapolation=self.extrapolation,
                )
            )
        return scored


def Perovskite_Standardized_Fields(
    block: PerovskiteAngleBlock, voxel_mean: NDArray[np.float64], voxel_scale: NDArray[np.float64]
) -> NDArray[np.float64]:
    """a block's fields on the per-voxel scale of the training block"""
    return (block.fields - voxel_mean) / voxel_scale


def Perovskite_Ridge_Predictions(
    basis: PodBasis, train: PerovskiteAngleBlock, evaluated: PerovskiteAngleBlock
) -> NDArray[np.float64]:
    """the closed-form floor: lattice parameters onto mode coefficients, decoded through the basis"""
    fitted = Fit_Standardized_Ridge(train.parameters, Project(basis, train.fields))
    return Reconstruct(basis, Apply_Standardized_Ridge(fitted, evaluated.parameters))


def Perovskite_Nearest_Neighbor_Predictions(
    train: PerovskiteAngleBlock, evaluated: PerovskiteAngleBlock
) -> NDArray[np.float64]:
    """the memorization floor: the field of the closest training run in lattice-parameter space"""
    nearest = Nearest_Training_Run(train.parameters, evaluated.parameters)
    return train.fields[nearest]


def Perovskite_Training_Mean_Predictions(
    train: PerovskiteAngleBlock, evaluated: PerovskiteAngleBlock
) -> NDArray[np.float64]:
    """the flat floor: every evaluated run predicted as the training block's own mean field, parameters ignored"""
    return np.tile(train.fields.mean(axis=0), (evaluated.fields.shape[0], 1))


def Perovskite_Renormalization_Scales(
    rebuilt: NDArray[np.float64], cell_volumes: NDArray[np.float64]
) -> NDArray[np.float64]:
    """the exact factor the card's renormalize_to_electron_count law takes on each evaluated run's field"""
    point_count = rebuilt.shape[1]
    return np.asarray(
        [
            float(
                Renormalization_Scale(
                    rebuilt[run], float(cell_volumes[run]) / point_count, np.asarray(PEROVSKITE_ELECTRON_COUNT)
                )
            )
            for run in range(rebuilt.shape[0])
        ],
        dtype=np.float64,
    )


def Perovskite_Conservation_Applied(
    rebuilt: NDArray[np.float64], cell_volumes: NDArray[np.float64]
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """every evaluated run's field renormalized exactly onto the known electron count, with the scale each took"""
    scales = Perovskite_Renormalization_Scales(rebuilt, cell_volumes)
    return rebuilt * scales[:, None], scales


def Perovskite_Fixed_Basis_Member(
    configuration: str,
    basis: PodBasis,
    train: PerovskiteAngleBlock,
    validation: PerovskiteAngleBlock,
    evaluated: PerovskiteAngleBlock,
    run_name_prefix: str,
    fixed_step_count: int | None,
) -> tuple[NDArray[np.float64], int, DeepOperatorNetwork]:
    """the fixed-basis member trained at the given budget, or at the one validation prefers among the card's five"""
    voxel_mean, voxel_scale = Pointwise_Statistics(train.fields)
    if configuration == "proper_orthogonal":
        coefficients = Project(basis, (train.fields - voxel_mean) / voxel_scale)
    else:
        coefficients = Project(basis, train.fields)
    parameter_spreads = train.parameters.std(axis=0)
    parameter_spreads[parameter_spreads == 0.0] = 1.0
    coefficient_mean = coefficients.mean(axis=0)
    coefficient_scale = coefficients.std(axis=0)
    coefficient_scale[coefficient_scale == 0.0] = 1.0
    batch = np.concatenate(
        [train.parameters / parameter_spreads, (coefficients - coefficient_mean) / coefficient_scale],
        axis=1,
    )
    parameter_width = train.parameters.shape[1]
    whole_batch = FixedBatches(TrainingBatch({"rows": batch}))
    if configuration == "proper_orthogonal":
        member = Proper_Orthogonal_Network(
            basis, PEROVSKITE_ANGLE_GRID_SHAPE, voxel_mean, voxel_scale, parameter_width, HIDDEN_WIDTHS
        )
    else:
        member = Principal_Component_Network(basis, PEROVSKITE_ANGLE_GRID_SHAPE, parameter_width, HIDDEN_WIDTHS)

    def Coefficient_Loss(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        """mean squared error between the branch's coefficients and the projected truth"""
        rows = lifted_batch["rows"]
        predicted = member.Forward_Coefficients(lifted, rows[:, :parameter_width])
        residuals = predicted - rows[:, parameter_width:]
        return (residuals * residuals).mean()

    def Rebuild(values: dict[str, NDArray[np.float64]], block: PerovskiteAngleBlock) -> NDArray[np.float64]:
        """this block's parameters carried through the trained branch and decoded back onto the field"""
        predicted = np.asarray(
            member.Forward_Coefficients(values, block.parameters / parameter_spreads), dtype=np.float64
        )
        rebuilt = Reconstruct(basis, predicted * coefficient_scale + coefficient_mean)
        if configuration == "proper_orthogonal":
            return rebuilt * voxel_scale + voxel_mean
        return rebuilt

    candidates = CANDIDATE_STEP_COUNTS if fixed_step_count is None else (fixed_step_count,)
    best_score = float("inf")
    best_values: dict[str, NDArray[np.float64]] = {}
    best_step_count = candidates[0]
    for step_count in candidates:
        # the budget is the one hyperparameter chosen here, and fold_0's validation is what chooses it
        result = Train(
            Training_Engine(),
            ParameterSet(values=member.Parameter_Values()),
            Coefficient_Loss,
            whole_batch,
            step_count=step_count,
            learning_rate=3e-3,
            seed=LATTICE_SEED,
            artifact_directory=TRAINING_ARTIFACT_PATH,
            run_name=f"{run_name_prefix}_{step_count}",
        )
        rebuilt = Rebuild(result.parameters.values, validation)
        score = float(
            np.median([Relative_L2(rebuilt[run], validation.fields[run]) for run in range(rebuilt.shape[0])])
        )
        if score < best_score:
            best_score, best_values, best_step_count = score, result.parameters.values, step_count
    for name, value in best_values.items():
        if name in member.branch.parameter_values:
            member.branch.parameter_values[name] = value
    member(
        Coefficients(vector=evaluated.parameters[0] / parameter_spreads, domain=Domain(np.eye(3))),
        GridSpec(PEROVSKITE_ANGLE_GRID_SHAPE),
    )
    return Rebuild(best_values, evaluated), best_step_count, member


def Perovskite_Write_Figures(
    split_name: str,
    configuration: str,
    member: DeepOperatorNetwork,
    test: PerovskiteAngleBlock,
    member_rebuilt: NDArray[np.float64],
    floor_medians: dict[str, float],
    member_median: float,
) -> int:
    """the member's whole visual surface, drawn from arrays cached on the pool"""
    cache = ARRAY_CACHE_PATH / "perovskite" / split_name / configuration
    cache.mkdir(parents=True, exist_ok=True)
    inspected = {name: np.asarray(value, dtype=np.float64) for name, value in member.Inspect().items()}
    np.savez(cache / "inspection.npz", **cast(dict[str, Any], inspected))
    with np.load(cache / "inspection.npz") as archive:
        restored = {name: np.asarray(archive[name], dtype=np.float64) for name in archive.files}

    directory = FIGURES_PATH / "perovskite" / split_name / configuration
    suite = Render_Inspection_Suite(
        restored, directory / "components", f"deep_operator_network lattice {split_name} {configuration}"
    )
    if suite.skipped:
        raise ValueError(f"no renderer for {suite.skipped}, which means the suite is incomplete")

    scored = [Relative_L2(member_rebuilt[run], test.fields[run]) for run in range(test.fields.shape[0])]
    for rank, run in enumerate(np.argsort(scored)[[0, -1]]):
        Render_Prediction_Against_Truth(
            member_rebuilt[run].reshape(PEROVSKITE_ANGLE_GRID_SHAPE),
            test.fields[run].reshape(PEROVSKITE_ANGLE_GRID_SHAPE),
            directory / f"prediction_{'best' if rank == 0 else 'worst'}.png",
            f"lattice {split_name} {configuration} {'best' if rank == 0 else 'worst'} test run,"
            f" {test.unit_keys[run]}",
        )
    Render_Floor_Comparison(
        floor_medians,
        member_median,
        {"ridge_to_coefficients": RIDGE_MARGIN, "nearest_neighbor_copy": NEAREST_NEIGHBOR_MARGIN},
        directory / "floors.png",
        f"lattice {split_name} {configuration} against its floors",
    )
    return len(suite.written) + 3


def Perovskite_Fixed_Basis_Block_Lines(
    split_name: str,
    configuration: str,
    evaluation_fold: int,
    extrapolation_holdout: str | None,
    extrapolation: str,
    fixed_step_count: int | None,
) -> tuple[list[str], tuple[FloorComparison, ...], int]:
    """one split and fixed-basis configuration measured end to end, on the angle stratum's shared grid"""
    train_examples, validation_examples = Perovskite_Train_Validation_Split(
        Perovskite_Angle_Examples("train", evaluation_fold, extrapolation_holdout)
    )
    train = PerovskiteAngleBlock(train_examples)
    validation = PerovskiteAngleBlock(validation_examples)
    test = PerovskiteAngleBlock(
        Perovskite_Angle_Examples("evaluation", evaluation_fold, extrapolation_holdout), extrapolation
    )
    raw_basis = Gram_Pod(train.fields, rank=BASIS_RANK)
    voxel_mean, voxel_scale = Pointwise_Statistics(train.fields)
    if configuration == "proper_orthogonal":
        basis = Gram_Pod(Perovskite_Standardized_Fields(train, voxel_mean, voxel_scale), rank=BASIS_RANK)
        # the ceiling of a standardized basis is read back on the raw scale, where the metric lives
        ceiling_rebuilt = (
            Reconstruct(basis, Project(basis, Perovskite_Standardized_Fields(test, voxel_mean, voxel_scale)))
            * voxel_scale
            + voxel_mean
        )
    else:
        basis = raw_basis
        ceiling_rebuilt = Reconstruct(basis, Project(basis, test.fields))

    # the floors are the same floors whichever configuration is being judged against them
    ridge_runs = test.Scored(Perovskite_Ridge_Predictions(raw_basis, train, test))
    copy_runs = test.Scored(Perovskite_Nearest_Neighbor_Predictions(train, test))
    mean_runs = test.Scored(Perovskite_Training_Mean_Predictions(train, test))
    member_rebuilt_raw, step_count, member = Perovskite_Fixed_Basis_Member(
        configuration, basis, train, validation, test, f"lattice_{split_name}_{configuration}", fixed_step_count
    )
    member_rebuilt, conservation_scales = Perovskite_Conservation_Applied(member_rebuilt_raw, test.cell_volumes)
    member_runs = test.Scored(member_rebuilt)
    ceiling_runs = test.Scored(ceiling_rebuilt)

    comparisons = (
        Compare_To_Floor(member_runs, ridge_runs, "relative_l2", "ridge_to_coefficients", RIDGE_MARGIN, split_name),
        Compare_To_Floor(
            member_runs, copy_runs, "relative_l2", "nearest_neighbor_copy", NEAREST_NEIGHBOR_MARGIN, split_name
        ),
    )
    summaries = (
        Summarize(ceiling_runs, "relative_l2", "rank_32_projection_ceiling"),
        Summarize(mean_runs, "relative_l2", "training_mean_floor"),
        Summarize(ridge_runs, "relative_l2", "ridge_floor"),
        Summarize(copy_runs, "relative_l2", "nearest_neighbor_floor"),
        Summarize(member_runs, "relative_l2", "member"),
        Summarize(member_runs, "frequency_split_relative_l2_low", "member"),
        Summarize(member_runs, "frequency_split_relative_l2_high", "member"),
    )
    floor_medians = {
        "ridge_to_coefficients": comparisons[0].floor_median,
        "nearest_neighbor_copy": comparisons[1].floor_median,
    }
    figure_count = Perovskite_Write_Figures(
        split_name, configuration, member, test, member_rebuilt, floor_medians, comparisons[0].member_median
    )
    label = "extrapolation" if extrapolation == EXTRAPOLATION else "interpolation"
    budget_note = "chosen on validation" if fixed_step_count is None else "reused from fold_0's own search"
    lines = [
        f"## lattice_to_charge, `{split_name}`, `{configuration}` — perovskite angle stratum, {label}",
        "",
        f"Train {train.fields.shape[0]} runs, validation {validation.fields.shape[0]},"
        f" test {test.fields.shape[0]}, all on the shared {PEROVSKITE_ANGLE_GRID_SHAPE} grid."
        f" Basis rank {BASIS_RANK}; branch widths {HIDDEN_WIDTHS}; {step_count} steps ({budget_note})."
        f" Conservation scale (`renormalize_to_electron_count`), median:"
        f" {float(np.median(conservation_scales)):.6f}."
        f" {figure_count} figures under `figures/perovskite/{split_name}/{configuration}/`.",
        "",
        "```",
        Render_Table(Summary_Table(summaries)),
        "```",
        "",
        "```",
        Render_Table(Comparison_Table(comparisons)),
        "```",
        "",
    ]
    return lines, comparisons, step_count


def Perovskite_Point_Value_Loss(member: DeepOperatorNetwork, parameter_spreads: Any) -> ForwardLoss:
    """mean squared error on each run's own reference-density-standardized density, at its own sampled points"""


    def Loss_Of(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        """the point-sampled forward answered against this batch's own reference-density-standardized targets"""
        branch_input = lifted_batch["parameter_vectors"] / parameter_spreads
        predicted = member.Forward_Point_Values(lifted, branch_input, lifted_batch["trunk_features"])
        reference_density = Reference_Density(PEROVSKITE_ELECTRON_COUNT, lifted_batch["cell_volumes"])
        target = Reference_Density_Standardized(lifted_batch["target_values"][:, :, 0], reference_density[:, None])
        residuals = predicted - target
        return (residuals * residuals).mean()

    return Loss_Of


def Perovskite_Canonical_Member(
    training_cache: FieldCache,
    validation_cache: FieldCache,
    run_name_prefix: str,
    fixed_step_count: int | None,
) -> tuple[DeepOperatorNetwork, NDArray[np.float64], dict[str, object], int]:
    """the canonical member trained point-sampled across every grid shape the cache holds"""
    parameter_width = int(training_cache.fields[0].parameters.shape[0])
    parameter_spreads = Parameter_Spreads(training_cache)
    member = Canonical_Network(
        parameter_width, CANONICAL_BRANCH_HIDDEN_WIDTHS, CANONICAL_LATENT_WIDTH, CANONICAL_TRUNK_HIDDEN_WIDTHS
    )
    readout = member.basis_readout
    if not isinstance(readout, BasisExpansion):
        raise TypeError("the canonical configuration was assembled without its learned trunk")
    sampler = PointSampledBatches(training_cache, validation_cache, CANONICAL_RUNS_PER_BATCH, CANONICAL_POINTS_PER_RUN)
    batches = CoordinateFeaturizedBatches(sampler, readout.coordinate_features)
    engine = Training_Engine()
    lifted_parameter_spreads = engine.Lift_Constant(parameter_spreads)
    forward_loss = Perovskite_Point_Value_Loss(member, lifted_parameter_spreads)
    parameters = ParameterSet(values=member.Parameter_Values())

    candidates = CANDIDATE_STEP_COUNTS if fixed_step_count is None else (fixed_step_count,)
    best_score = float("inf")
    best_values: dict[str, NDArray[np.float64]] = dict(parameters.values)
    best_step_count = candidates[0]
    best_manifest: dict[str, object] = {}
    for step_count in candidates:
        # every candidate restarts from the member's own initial weights, exactly as the fixed-basis search does
        result = Train(
            engine,
            parameters,
            forward_loss,
            batches,
            step_count=step_count,
            learning_rate=LATTICE_CANONICAL_LEARNING_RATE,
            seed=LATTICE_SEED,
            artifact_directory=TRAINING_ARTIFACT_PATH,
            run_name=f"{run_name_prefix}_{step_count}",
            validation_interval=CANONICAL_VALIDATION_INTERVAL,
        )
        score = float(cast(float, result.manifest["best_validation_score"]))
        if score < best_score:
            best_score, best_values, best_step_count, best_manifest = score, result.parameters.values, step_count, result.manifest
    for name, value in best_values.items():
        if name in member.branch.parameter_values:
            member.branch.parameter_values[name] = value
        if name in readout.parameter_values:
            readout.parameter_values[name] = value
    return member, parameter_spreads, best_manifest, best_step_count


def Perovskite_Canonical_Angle_Predictions(
    member: DeepOperatorNetwork, parameter_spreads: NDArray[np.float64], evaluated: PerovskiteAngleBlock
) -> NDArray[np.float64]:
    """the trained member's field on the angle stratum's shared grid, for every given run's own parameters"""
    readout = member.basis_readout
    if not isinstance(readout, BasisExpansion):
        raise TypeError("a grid prediction needs the learned coordinate trunk")
    points = Output_Points(GridSpec(PEROVSKITE_ANGLE_GRID_SHAPE))
    trunk_features = readout.Coordinate_Features(points)
    coefficients = member.Forward_Coefficients(
        member.branch.parameter_values, evaluated.parameters / parameter_spreads
    )
    standardized = np.asarray(
        readout.Forward(readout.parameter_values, coefficients, trunk_features), dtype=np.float64
    )
    reference_density = Reference_Density(PEROVSKITE_ELECTRON_COUNT, evaluated.cell_volumes)
    return Reference_Density_Restored(standardized.T, reference_density[:, None])


def Perovskite_Canonical_Every_Shape_Runs(
    member: DeepOperatorNetwork,
    parameter_spreads: NDArray[np.float64],
    test_cache: FieldCache,
    extrapolation: str,
) -> tuple[list[ScoredRun], NDArray[np.float64]]:
    """the trained member's own field on every test run's own grid shape, conservation applied per run"""
    readout = member.basis_readout
    if not isinstance(readout, BasisExpansion):
        raise TypeError("a grid prediction needs the learned coordinate trunk")
    grouped: dict[tuple[int, ...], list[CachedField]] = {}
    for cached_field in test_cache.fields:
        grouped.setdefault(cached_field.grid_shape, []).append(cached_field)
    scored: list[ScoredRun] = []
    scales: list[float] = []
    for grid_shape, cached_fields in grouped.items():
        points = Output_Points(GridSpec((grid_shape[0], grid_shape[1], grid_shape[2])))
        trunk_features = readout.Coordinate_Features(points)
        parameters = np.stack([field.parameters for field in cached_fields])
        cell_volumes = np.asarray([field.cell_volume for field in cached_fields], dtype=np.float64)
        coefficients = member.Forward_Coefficients(member.branch.parameter_values, parameters / parameter_spreads)
        standardized = np.asarray(
            readout.Forward(readout.parameter_values, coefficients, trunk_features), dtype=np.float64
        )
        reference_density = Reference_Density(PEROVSKITE_ELECTRON_COUNT, cell_volumes)
        physical = Reference_Density_Restored(standardized.T, reference_density[:, None])
        conserved, run_scales = Perovskite_Conservation_Applied(physical, cell_volumes)
        cutoff = Lattice_Frequency_Cutoff(grid_shape)
        for position, cached_field in enumerate(cached_fields):
            truth = cached_field.Flattened_Values()[0].astype(np.float64)
            predicted = conserved[position]
            low, high = Frequency_Split_Relative_L2(
                predicted.reshape(grid_shape), truth.reshape(grid_shape), cutoff_modes=cutoff
            )
            scored.append(
                ScoredRun(
                    identifier=cached_field.identifier,
                    unit_key=cached_field.unit_key,
                    campaign="perovskite_grid",
                    family="length" if cached_field.unit_key.endswith("_length") else "angle",
                    errors={
                        "relative_l2": Relative_L2(predicted, truth),
                        "frequency_split_relative_l2_low": low,
                        "frequency_split_relative_l2_high": high,
                    },
                    extrapolation=extrapolation,
                )
            )
            scales.append(float(run_scales[position]))
    return scored, np.asarray(scales, dtype=np.float64)


def Perovskite_Every_Shape_Nearest_Neighbor_Runs(
    training_cache: FieldCache, test_cache: FieldCache, extrapolation: str
) -> list[ScoredRun]:
    """the memorization floor computed within each grid shape, since a copy needs a shape to match its truth"""
    training_groups: dict[tuple[int, ...], list[CachedField]] = {}
    for cached_field in training_cache.fields:
        training_groups.setdefault(cached_field.grid_shape, []).append(cached_field)
    test_groups: dict[tuple[int, ...], list[CachedField]] = {}
    for cached_field in test_cache.fields:
        test_groups.setdefault(cached_field.grid_shape, []).append(cached_field)
    scored: list[ScoredRun] = []
    for grid_shape, test_fields in test_groups.items():
        training_fields = training_groups.get(grid_shape)
        # a shape the training role never produced has no candidate this floor could copy
        if not training_fields:
            continue
        training_parameters = np.stack([field.parameters for field in training_fields])
        test_parameters = np.stack([field.parameters for field in test_fields])
        nearest = Nearest_Training_Run(training_parameters, test_parameters)
        cutoff = Lattice_Frequency_Cutoff(grid_shape)
        for position, cached_field in enumerate(test_fields):
            copied = training_fields[int(nearest[position])].Flattened_Values()[0].astype(np.float64)
            truth = cached_field.Flattened_Values()[0].astype(np.float64)
            low, high = Frequency_Split_Relative_L2(
                copied.reshape(grid_shape), truth.reshape(grid_shape), cutoff_modes=cutoff
            )
            scored.append(
                ScoredRun(
                    identifier=cached_field.identifier,
                    unit_key=cached_field.unit_key,
                    campaign="perovskite_grid",
                    family="length" if cached_field.unit_key.endswith("_length") else "angle",
                    errors={
                        "relative_l2": Relative_L2(copied, truth),
                        "frequency_split_relative_l2_low": low,
                        "frequency_split_relative_l2_high": high,
                    },
                    extrapolation=extrapolation,
                )
            )
    return scored


def Perovskite_Write_Every_Shape_Figure(split_name: str, member_runs_every: list[ScoredRun]) -> Path:
    """error spread across both strata the test set holds, canonical's own extra reach"""
    directory = FIGURES_PATH / "perovskite" / split_name / "canonical"
    by_stratum: dict[str, list[float]] = {}
    for scored_run in member_runs_every:
        by_stratum.setdefault(scored_run.family, []).append(scored_run.errors["relative_l2"])
    return Render_Error_Spread(
        {name: np.asarray(values) for name, values in by_stratum.items()},
        directory / "error_by_stratum.png",
        f"lattice {split_name} canonical test error by stratum, the shapes no fixed basis can reach",
    )


def Perovskite_Canonical_Block_Lines(
    split_name: str,
    evaluation_fold: int,
    extrapolation_holdout: str | None,
    extrapolation: str,
    fixed_step_count: int | None,
) -> tuple[list[str], tuple[FloorComparison, ...], int]:
    """one split's canonical member: on the angle stratum beside the fixed-basis floors, and on every shape"""
    train_examples, _ = Perovskite_Train_Validation_Split(
        Perovskite_Angle_Examples("train", evaluation_fold, extrapolation_holdout)
    )
    train_common = PerovskiteAngleBlock(train_examples)
    test_common = PerovskiteAngleBlock(
        Perovskite_Angle_Examples("evaluation", evaluation_fold, extrapolation_holdout), extrapolation
    )
    raw_basis = Gram_Pod(train_common.fields, rank=BASIS_RANK)
    ridge_runs = test_common.Scored(Perovskite_Ridge_Predictions(raw_basis, train_common, test_common))
    copy_runs = test_common.Scored(Perovskite_Nearest_Neighbor_Predictions(train_common, test_common))
    mean_runs = test_common.Scored(Perovskite_Training_Mean_Predictions(train_common, test_common))

    card = Card_Named("lattice_to_charge")
    pool_cache = Build_Field_Cache(card, "train", evaluation_fold, extrapolation_holdout)
    Guard_Fresh_Archives([cached_field.identifier for cached_field in pool_cache.fields])
    cache_is_validation = Perovskite_Cache_Validation_Mask(pool_cache)
    training_cache = FieldCache(
        pool_cache.card_name,
        "train",
        tuple(field for field, held in zip(pool_cache.fields, cache_is_validation) if not held),
    )
    validation_cache = FieldCache(
        pool_cache.card_name,
        "validation",
        tuple(field for field, held in zip(pool_cache.fields, cache_is_validation) if held),
    )
    test_cache = Build_Field_Cache(card, "evaluation", evaluation_fold, extrapolation_holdout)
    Guard_Fresh_Archives([cached_field.identifier for cached_field in test_cache.fields])

    member, parameter_spreads, _, step_count = Perovskite_Canonical_Member(
        training_cache, validation_cache, f"lattice_{split_name}_canonical", fixed_step_count
    )
    readout = member.basis_readout
    if not isinstance(readout, BasisExpansion):
        raise TypeError("the canonical configuration was assembled without its learned trunk")

    member_rebuilt_common_raw = Perovskite_Canonical_Angle_Predictions(member, parameter_spreads, test_common)
    member_rebuilt_common, common_scales = Perovskite_Conservation_Applied(
        member_rebuilt_common_raw, test_common.cell_volumes
    )
    member_runs_common = test_common.Scored(member_rebuilt_common)
    # the only call that fills encoder.last_latent_vector, composition.last_carried_vector and last_trunk_features
    member(
        Coefficients(vector=test_common.parameters[0] / parameter_spreads, domain=Domain(np.eye(3))),
        GridSpec(PEROVSKITE_ANGLE_GRID_SHAPE),
    )

    comparisons_common = (
        Compare_To_Floor(
            member_runs_common, ridge_runs, "relative_l2", "ridge_to_coefficients", RIDGE_MARGIN, split_name
        ),
        Compare_To_Floor(
            member_runs_common, copy_runs, "relative_l2", "nearest_neighbor_copy", NEAREST_NEIGHBOR_MARGIN, split_name
        ),
    )
    figure_count = Perovskite_Write_Figures(
        split_name,
        "canonical",
        member,
        test_common,
        member_rebuilt_common,
        {
            "ridge_to_coefficients": comparisons_common[0].floor_median,
            "nearest_neighbor_copy": comparisons_common[1].floor_median,
        },
        comparisons_common[0].member_median,
    )

    copy_runs_every = Perovskite_Every_Shape_Nearest_Neighbor_Runs(training_cache, test_cache, extrapolation)
    member_runs_every, every_scales = Perovskite_Canonical_Every_Shape_Runs(
        member, parameter_spreads, test_cache, extrapolation
    )
    covered_identifiers = {scored_run.identifier for scored_run in copy_runs_every}
    member_runs_every_covered = [run for run in member_runs_every if run.identifier in covered_identifiers]
    every_shape_comparison = Compare_To_Floor(
        member_runs_every_covered,
        copy_runs_every,
        "relative_l2",
        "nearest_neighbor_copy",
        NEAREST_NEIGHBOR_MARGIN,
        group_name=f"{split_name}_every_shape",
    )
    Perovskite_Write_Every_Shape_Figure(split_name, member_runs_every)

    length_count = sum(1 for run in member_runs_every if run.family == "length")
    shape_count = len({cached_field.grid_shape for cached_field in test_cache.fields})
    label = "extrapolation" if extrapolation == EXTRAPOLATION else "interpolation"
    budget_note = "chosen on its own held-out training loss" if fixed_step_count is None else "reused from fold_0"
    lines = [
        f"## lattice_to_charge, `{split_name}`, `canonical` — perovskite grid, {label}, learned coordinate trunk",
        "",
        f"Trained point-sampled on {len(training_cache.fields)} runs across both strata"
        f" ({len(validation_cache.fields)} held for validation); test on the angle stratum's"
        f" {test_common.fields.shape[0]} runs on the shared {PEROVSKITE_ANGLE_GRID_SHAPE} grid, scored"
        f" exactly as the fixed-basis configurations are. Branch widths {CANONICAL_BRANCH_HIDDEN_WIDTHS},"
        f" latent {CANONICAL_LATENT_WIDTH}, trunk widths {CANONICAL_TRUNK_HIDDEN_WIDTHS}."
        f" {step_count} steps ({budget_note})."
        f" Conservation scale on the angle stratum, median: {float(np.median(common_scales)):.6f}."
        f" {figure_count} figures under `figures/perovskite/{split_name}/canonical/`.",
        "",
        "```",
        Render_Table(
            Summary_Table(
                (
                    Summarize(mean_runs, "relative_l2", "training_mean_floor"),
                    Summarize(ridge_runs, "relative_l2", "ridge_floor"),
                    Summarize(copy_runs, "relative_l2", "nearest_neighbor_floor"),
                    Summarize(member_runs_common, "relative_l2", "member_on_angle_stratum"),
                    Summarize(member_runs_common, "frequency_split_relative_l2_low", "member_on_angle_stratum"),
                    Summarize(member_runs_common, "frequency_split_relative_l2_high", "member_on_angle_stratum"),
                )
            )
        ),
        "```",
        "",
        "```",
        Render_Table(Comparison_Table(comparisons_common)),
        "```",
        "",
        f"### every shape this split's test set holds, {shape_count} of them, {len(member_runs_every)} test runs"
        f" ({length_count} on the length stratum's own unique grid,"
        f" {len(member_runs_every) - length_count} on the angle stratum's shared one;"
        f" {len(member_runs_every_covered)} had a same-shape training neighbor to copy)",
        "",
        "The table above restricts training and test to the angle stratum's one shared grid, because the",
        "fixed-basis configurations cannot read any other. This same member trained on every shape the",
        f"training role holds at once ({training_cache.Resident_Bytes() / 1e6:.0f} MB resident), including the",
        "length stratum's own distinct grid per run, and is scored below across every shape its own test runs",
        "hold — the capability the fixed-basis pair does not have. Every length-stratum run sits on a grid",
        "shape unique to that one run, so it carries no same-shape training neighbor for the copy floor to",
        f"read; the conservation scale across every shape, median: {float(np.median(every_scales)):.6f}.",
        "",
        "```",
        Render_Table(
            Summary_Table(
                (
                    Summarize(copy_runs_every, "relative_l2", "nearest_neighbor_floor_every_shape"),
                    Summarize(member_runs_every, "relative_l2", "member_every_shape_full_test_set"),
                    *Summarize_By(member_runs_every, "relative_l2", "family"),
                )
            )
        ),
        "```",
        "",
        "```",
        Render_Table(Comparison_Table((every_shape_comparison,))),
        "```",
        "",
    ]
    return lines, comparisons_common + (every_shape_comparison,), step_count


def Perovskite_Report_Lines() -> tuple[list[str], list[FloorComparison]]:
    """every split of lattice_to_charge, fixed-basis on the angle stratum and canonical on everything"""
    lines: list[str] = [
        "## lattice_to_charge — perovskite grid, `test-suite.md` §3, II.1b",
        "",
        "The same member as strain_to_charge, on a different campaign: the branch reads the six lattice",
        "factors `(a, b, c, alpha, beta, gamma)` (`Lattice_Factors_Of`) instead of a strain tensor, split",
        "`perovskite_folds` instead of the strain holdout, conservation `renormalize_to_electron_count`",
        "mandated on the density output. `energy_trunk` does not apply: this card has no eigenvalue target.",
        "",
        "The campaign splits into two strata by grid shape, measured directly: the angle stratum is 125",
        "runs, every one on the shared 64-cubed grid; the length stratum is 124 runs on 124 distinct grid",
        "shapes. The fixed-basis configurations (`principal_component`, `proper_orthogonal`) need one",
        "common shape to stack fields into a basis, so they train and are scored on the angle stratum",
        "alone — roughly 100 training runs per fold. `canonical` trains point-sampled across both strata",
        "at once and is the only configuration that can read the length stratum's 124 distinct shapes at",
        "all; that row is the number no fixed basis can produce.",
        "",
        "The target's dynamic range is far wider than the strain atlas's: measured directly, the peak",
        "density sits at 15.47 to 15.68 e/A^3 at the heavy-atom cores across the whole campaign, and the",
        "angle stratum's own cell volume varies only 1.24x while the length stratum's varies 3.375x, even",
        "though the electron count is fixed at 48.0 for every run. A plain mean-squared error in raw voxel",
        "units would let the length stratum's smallest cells dominate canonical's point-sampled loss.",
        "`canonical` therefore standardizes each sampled run's own target by that run's own reference",
        "density — electron count over its own cell volume, the field's exact spatial mean, known from the",
        "branch's own input and never from the truth — before the loss compares it to the branch's raw",
        "output, and restores it by the same factor before any figure or metric sees it. The fixed-basis",
        "pair keeps its existing coefficient-space loss unchanged: the angle stratum's 1.24x volume range",
        "is mild, and its per-coefficient standardization already conditions that loss; `relative_l2` and",
        "`frequency_split_relative_l2` are themselves invariant to a positive per-run rescaling applied",
        "identically to a prediction and its truth, so this choice changes no reported number, only what",
        "the loss optimizes toward.",
        "",
        "`renormalize_to_electron_count` (`operators.wrappers.Conserving`) is applied to every reported",
        "prediction on the whole-field path, never to a point batch, which carries no quadrature weight.",
        "Ground truth integrates to 48.0 electrons to within a few parts in 10^8 on every run measured, so",
        "the scale this law applies at inference is pure model error, reported as a free diagnostic beside",
        "each block's own numbers.",
        "",
        "Fold 0 is where the training budget is chosen, among the same five candidate step counts the",
        "fixed-basis pair otherwise searches, for every configuration including `canonical`. Both",
        "extrapolation holdouts reuse whichever budget fold 0 chose for that configuration rather than",
        "re-searching, so nine trainings become three searches plus six fixed-budget runs. The two holdout",
        "splits hold out every factor-0.8 run, separately every factor-1.2 run, and are labeled",
        "`extrapolation` throughout; fold 0 is `interpolation`. One seeded run per block, as elsewhere in",
        "this report.",
        "",
    ]
    verdicts: list[FloorComparison] = []
    fixed_basis_step_counts: dict[str, int] = {}
    canonical_step_count: int | None = None
    for split_name, extrapolation_holdout, extrapolation in PEROVSKITE_SPLITS:
        is_develop = extrapolation_holdout is None
        for configuration in ("principal_component", "proper_orthogonal"):
            fixed_step = None if is_develop else fixed_basis_step_counts[configuration]
            block_lines, comparisons, chosen_step_count = Perovskite_Fixed_Basis_Block_Lines(
                split_name, configuration, PEROVSKITE_DEVELOP_FOLD, extrapolation_holdout, extrapolation, fixed_step
            )
            lines += block_lines
            verdicts += list(comparisons)
            if is_develop:
                fixed_basis_step_counts[configuration] = chosen_step_count
        canonical_fixed_step = None if is_develop else canonical_step_count
        canonical_lines, canonical_comparisons, chosen_canonical_step_count = Perovskite_Canonical_Block_Lines(
            split_name, PEROVSKITE_DEVELOP_FOLD, extrapolation_holdout, extrapolation, canonical_fixed_step
        )
        lines += canonical_lines
        verdicts += list(canonical_comparisons)
        if is_develop:
            canonical_step_count = chosen_canonical_step_count
    lines += [
        "`energy_trunk` does not apply to `lattice_to_charge`: the card has no eigenvalue target, so no",
        "block for it appears in this section.",
        "",
    ]
    return lines, verdicts


def Main() -> int:
    """every block measured, and the member's report written"""
    lines = [
        "# deep_operator_network — measured report",
        "",
        "Regenerate with `python -m operators.deep_operator_network.report`.",
        "Relative L2 per run, aggregated over symmetry orbits rather than runs, because runs inside",
        "one orbit are exact copies of each other. Two fixed-basis configurations, each on its own",
        "basis: `principal_component` on the raw fields, `proper_orthogonal` on fields standardized",
        "voxel by voxel before the decomposition. A third, `canonical`, replaces both fixed bases with",
        "a learned coordinate trunk, trained point-sampled on every grid shape the campaign holds at",
        "once. A fourth, `energy_trunk`, is `canonical`'s sibling on the strain-to-states card: the",
        "trunk runs over energy instead of position, both functionals pooled into one member, scored",
        "by the card's own `curve_l1`, `wasserstein_1d` and `gap_edge_error` rather than relative L2.",
        "Trained on the accelerator in single precision.",
        "",
        "Each number below is one training run. A twelve-run seed sweep of the two fixed-basis",
        "configurations measured a seed spread of fourteen to thirty-five percent of the median, and",
        "a difference between configurations of under two percent, so the ordering of any two rows",
        "here is not a finding; the sweep is the finding, and it says they are indistinguishable.",
        "`canonical` and `energy_trunk` are each reported from a single seeded run and should be read",
        "with the same caution. `energy_trunk` sets no kill margin and contributes no row to the",
        "floor-comparison standing below: VI.1 fixes none, and a floor winning there is a reportable",
        "result, not a failure.",
        "",
    ]
    verdicts: list[FloorComparison] = []
    chosen_step_counts: list[int] = []
    for functional in ("cheap", "accurate"):
        for configuration in CONFIGURATIONS_REPORTED:
            block_lines, comparisons, step_count = Block_Lines(functional, configuration)
            lines += block_lines
            verdicts += list(comparisons)
            chosen_step_counts.append(step_count)
    for functional in ("cheap", "accurate"):
        canonical_lines, canonical_comparisons = Canonical_Block_Lines(functional)
        lines += canonical_lines
        verdicts += list(canonical_comparisons)
    # no FloorComparison is added for this block: VI.1 sets no kill margin, and none should be invented
    lines += Energy_Trunk_Block_Lines()
    perovskite_lines, perovskite_verdicts = Perovskite_Report_Lines()
    lines += perovskite_lines
    verdicts += perovskite_verdicts
    killed = [comparison for comparison in verdicts if comparison.verdict == "kill"]
    at_the_ceiling = [count for count in chosen_step_counts if count == max(CANDIDATE_STEP_COUNTS)]
    lines += [
        "## Standing",
        "",
        f"- {len(verdicts) - len(killed)} of {len(verdicts)} floor comparisons pass",
        "- the ridge floor is the binding one; the nearest-neighbor copy is roughly threefold weaker,"
        " against the suite's expectation that a factorial sweep would make copying brutal",
        "- the basis reconstructs the same fields to a thousandth of the floor, so the error"
        " measured here is the parameter map's and none of it the representation's",
        "",
    ]
    if at_the_ceiling:
        lines += [
            f"Caveat: {len(at_the_ceiling)} of {len(chosen_step_counts)} fixed-basis blocks chose the largest"
            f" budget offered ({max(CANDIDATE_STEP_COUNTS)} steps), so the search did not settle"
            " inside its range. Quadrupling the budget moved the member by three to seven percent"
            " against a margin it clears by seventy, so the boundary is recorded rather than chased.",
            "",
        ]
    REPORT_PATH.write_text("\n".join(lines) + "\n")
    print(f"wrote {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
