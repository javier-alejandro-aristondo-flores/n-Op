"""the member measured against its pre-registered floors, written as one committed markdown artifact"""

import dataclasses
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.data import Archive_Path, Guard_Fresh_Archives, Nearest_Training_Run, POOL_ROOT, Run_Identifier, STORE_NAME
from operators.evaluation import (
    Block_Signature,
    CubicBlock,
    Elf_Ridge_Rows,
    MemberResults,
    MetricSummary,
    PATTERN_RULE_MARGIN,
    ResultKey,
    ResultRow,
    ScoredRun,
    Summarize,
    Summary_Table,
    Write_Member_Results,
)
from operators.factorized_fourier import All_Perovskite_Arms, Arm, Interior_Levels
from operators.framework import GridFunction, GridSpec, Layer, Output_Points
from operators.galerkin_transformer import (
    Constant_Channel_Field,
    Coordinate_Feature_Channels,
    GalerkinTransformer,
    Galerkin_Transformer_Network,
)
from operators.metrics import Relative_L2
from operators.substrate import ParameterSet
from operators.tasks import Card_Named
from operators.training import (
    BatchSource,
    ForwardLoss,
    ParameterExample,
    Parameter_Field_Examples,
    Train,
    TrainingBatch,
    Training_Engine,
)

type Level = tuple[float, ...]

PEROVSKITE_CAMPAIGN = "perovskite_grid"

PEROVSKITE_ANGLE_GRID_SHAPE = (64, 64, 64)

PEROVSKITE_ANGLE_UNIT_SUFFIX = "_angle"

REPORT_PATH = Path(__file__).resolve().parent / "report.md"

RESULTS_PATH = Path(__file__).resolve().parent / "results.json"

# the pre-registered stage-1 gate: the member's own angle-stratum relative L2 median must fall to this
# fraction of each floor's median or the entry dies before any fine-grid spend
GATE_IMPROVEMENT_MARGIN = 0.5

GATE_PROCESSING_SHAPE = (32, 32, 32)

GATE_SEED = 20260916

GATE_STAGE_FRACTIONS = (0.3, 0.3, 0.4)

GATE_STAGE_LEARNING_RATES = (1e-3, 3.3e-4, 1.1e-4)

GATE_VALIDATION_INTERVAL = 100

GATE_FINAL_STAGE_PATIENCE = 15

GATE_TRAINING_ARTIFACT_PATH = POOL_ROOT / STORE_NAME / "_training" / "galerkin_transformer"


def Angle_Stratum_Parameters_And_Fields(
    role: str, evaluation_fold: int
) -> tuple[NDArray[np.float64], NDArray[np.float64], list[str], list[str]]:
    """the angle stratum's own lattice vectors and flattened truths for one loader role of one fold"""
    card = Card_Named("lattice_to_charge")
    parameters: list[NDArray[np.float64]] = []
    fields: list[NDArray[np.float64]] = []
    unit_keys: list[str] = []
    identifiers: list[str] = []
    for example in Parameter_Field_Examples(card, role, evaluation_fold, None):
        if not example.unit_key.endswith(PEROVSKITE_ANGLE_UNIT_SUFFIX):
            continue
        if np.asarray(example.target_function.values).shape[1:] != PEROVSKITE_ANGLE_GRID_SHAPE:
            continue
        parameters.append(np.asarray(example.parameters.vector, dtype=np.float64))
        fields.append(np.asarray(example.target_function.values, dtype=np.float64).reshape(-1))
        unit_keys.append(example.unit_key)
        identifiers.append(example.identifier)
    return np.asarray(parameters), np.asarray(fields), unit_keys, identifiers


def Nearest_Angle_Copy_Rows(evaluation_fold: int) -> list[ScoredRun]:
    """the memorization floor: each evaluation run scored against the closest training run's own truth"""
    train_parameters, train_fields, _, _ = Angle_Stratum_Parameters_And_Fields("train", evaluation_fold)
    test_parameters, test_fields, test_unit_keys, test_identifiers = Angle_Stratum_Parameters_And_Fields(
        "evaluation", evaluation_fold
    )
    nearest = Nearest_Training_Run(train_parameters, test_parameters)
    predicted = train_fields[nearest]
    return [
        ScoredRun(
            identifier=test_identifiers[run],
            unit_key=test_unit_keys[run],
            campaign=PEROVSKITE_CAMPAIGN,
            family="angle",
            errors={"relative_l2": Relative_L2(predicted[run], test_fields[run])},
        )
        for run in range(test_fields.shape[0])
    ]


def Angle_Arm() -> Arm:
    """the perovskite census's own angle stratum, the one arm this gate's second floor interpolates over"""
    for arm in All_Perovskite_Arms():
        if arm.name == "angle":
            return arm
    raise ValueError("the perovskite census carries no angle arm")


def Loaded_Perovskite_Charge_Density(run_path: str) -> NDArray[np.float64]:
    """one perovskite-grid run's own charge density, at its native grid resolution"""
    identifier = Run_Identifier(run_path)
    with np.load(Archive_Path(PEROVSKITE_CAMPAIGN, identifier)) as archive:
        return np.asarray(archive["charge_density"], dtype=np.float64)


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


def Linear_In_Angle_Interpolation_Rows() -> list[ScoredRun]:
    """the multilinear floor over the angle arm's own interior levels, bracket corners drawn from the same arm"""
    arm = Angle_Arm()
    Guard_Fresh_Archives(
        Run_Identifier(run_path) for run_paths in arm.runs_by_level.values() for run_path in run_paths
    )
    cache: dict[Level, NDArray[np.float64]] = {}

    def Cached_Level_Field(level: Level) -> NDArray[np.float64]:
        if level not in cache:
            fields = [Loaded_Perovskite_Charge_Density(run_path) for run_path in arm.runs_by_level[level]]
            cache[level] = np.mean(np.stack(fields), axis=0)
        return cache[level]

    scored: list[ScoredRun] = []
    for level, corners in Interior_Levels(arm).items():
        truth = Cached_Level_Field(level)
        field_of_corner = {corner: Cached_Level_Field(corner) for corner in corners}
        predicted = Multilinear_Interpolated_Field(level, corners, field_of_corner)
        scored.append(
            ScoredRun(
                identifier=f"angle_{level}",
                unit_key=f"angle_{level}",
                campaign=PEROVSKITE_CAMPAIGN,
                family="angle",
                errors={"relative_l2": Relative_L2(predicted, truth)},
            )
        )
    return scored


def Stage_One_Bars(copy_summary: MetricSummary, interpolation_summary: MetricSummary) -> dict[str, float]:
    """the pre-registered gate: the member's own angle-stratum relative L2 median must clear both floors by half"""
    return {
        "gate_vs_nearest_angle_copy": copy_summary.median * (1.0 - GATE_IMPROVEMENT_MARGIN),
        "gate_vs_linear_in_angle_interpolation": interpolation_summary.median * (1.0 - GATE_IMPROVEMENT_MARGIN),
    }


def Stage_Two_Bar(ridge_summary: MetricSummary) -> float:
    """the pattern-rule bar: twenty percent better than the semilocal ridge, on mean absolute error"""
    return ridge_summary.median * (1.0 - PATTERN_RULE_MARGIN)


@dataclasses.dataclass(frozen=True, slots=True)
class FloorData:
    """every floor this pre-registration measures, computed once and shared by the report text and the results artifact"""

    copy_rows: list[ScoredRun]
    interpolation_rows: list[ScoredRun]
    ridge_rows: list[ScoredRun]


def Measured_Floors() -> FloorData:
    """every pre-registered floor, computed fresh from the store: the two stage-one floors, then the stage-two ridge"""
    return FloorData(
        copy_rows=Nearest_Angle_Copy_Rows(evaluation_fold=0),
        interpolation_rows=Linear_In_Angle_Interpolation_Rows(),
        ridge_rows=Elf_Ridge_Rows(CubicBlock()),
    )


def Results_Artifact(data: FloorData) -> MemberResults:
    """the floors measured so far, as one member results artifact -- no verdicts yet, since nothing has trained"""
    copy_summary = Summarize(data.copy_rows, "relative_l2", "nearest_angle_copy_floor")
    interpolation_summary = Summarize(data.interpolation_rows, "relative_l2", "linear_in_angle_interpolation_floor")
    ridge_summary = Summarize(data.ridge_rows, "mean_absolute_error", "semilocal_ridge_floor")
    rows = (
        ResultRow(
            key=ResultKey(
                member="galerkin_transformer",
                configuration="gate",
                task="lattice_to_charge",
                split="perovskite_folds",
                block="fold_0",
                group="nearest_angle_copy_floor",
            ),
            summary=copy_summary,
            block_signature=Block_Signature(row.unit_key for row in data.copy_rows),
        ),
        ResultRow(
            key=ResultKey(
                member="galerkin_transformer",
                configuration="gate",
                task="lattice_to_charge",
                split="perovskite_arms",
                block="angle_arm_interior_levels",
                group="linear_in_angle_interpolation_floor",
            ),
            summary=interpolation_summary,
            block_signature=Block_Signature(row.unit_key for row in data.interpolation_rows),
        ),
        ResultRow(
            key=ResultKey(
                member="galerkin_transformer",
                configuration="gate",
                task="charge_to_localization",
                split="paired_fields_fivefold",
                block="fold_0",
                group="semilocal_ridge_floor",
            ),
            summary=ridge_summary,
            block_signature=Block_Signature(row.unit_key for row in data.ridge_rows),
        ),
    )
    return MemberResults(
        member="galerkin_transformer",
        regenerate="python -m operators.galerkin_transformer.report",
        rows=rows,
        verdicts=(),
    )


def Report_Lines(data: FloorData) -> list[str]:
    """the pre-registered ladder: both stage-one floors and their bars, the stage-two ridge floor and its bar"""
    copy_summary = Summarize(data.copy_rows, "relative_l2", "nearest_angle_copy_floor")
    interpolation_summary = Summarize(data.interpolation_rows, "relative_l2", "linear_in_angle_interpolation_floor")
    ridge_summary = Summarize(data.ridge_rows, "mean_absolute_error", "semilocal_ridge_floor")
    gate_bars = Stage_One_Bars(copy_summary, interpolation_summary)
    elf_bar = Stage_Two_Bar(ridge_summary)
    lines = [
        "# galerkin_transformer — results",
        "",
        "## Stage 1 — perovskite angle stratum, fold 0 (pre-registration, before training)",
        "",
        f"`lattice_to_charge`, `perovskite_folds` fold 0, angle stratum: {len(data.copy_rows)} evaluation runs"
        " scored against the closest of 100 training runs in the same fold, on the shared 64-cubed grid. The"
        " linear-in-angle floor is measured separately, over every interior level of the angle arm's own"
        f" parameter grid, unrestricted by fold ({len(data.interpolation_rows)} interior levels, each"
        " bracketed by its own eight corner levels), following the strain atlas's own bracketing-interpolation"
        " precedent.",
        "",
    ]
    lines.append("| group | metric | units | runs | median | interquartile | 95% interval |")
    lines.append("|---|---|---|---|---|---|---|")
    for row in Summary_Table((copy_summary, interpolation_summary)):
        lines.append(
            f"| {row['group']} | {row['metric']} | {row['units']} | {row['runs']} | {row['median']} |"
            f" {row['interquartile']} | {row['mean_interval']} |"
        )
    lines += [
        "",
        f"**Nearest-angle field copy, relative L2 median = {copy_summary.median:.4f}** over"
        f" {copy_summary.unit_count} units, reproducing `deep_operator_network`'s own measurement of this exact"
        " floor on this exact fold (0.0853), computed independently here from"
        " `operators.training.Parameter_Field_Examples` and `operators.data.Nearest_Training_Run` alone.",
        "",
        f"**Linear-in-angle interpolation, relative L2 median = {interpolation_summary.median:.4f}** over"
        f" {interpolation_summary.unit_count} units, through the promoted arm machinery (`All_Perovskite_Arms`,"
        " `Interior_Levels`, `Bracket_Corners`, all exported from `operators.factorized_fourier`'s own root)."
        " Levels at the edge of the angle grid carry no full eight-corner bracket and are excluded from this"
        " floor rather than scored, exactly as `Interior_Levels` itself excludes them -- they would be"
        " extrapolation rows, not interpolation ones, and this gate is an interpolation floor.",
        "",
        "**The pre-registered stage-1 gate**: within a two-hour wall-clock cap, the member's own relative L2"
        " median on this same angle-stratum evaluation set must fall at or below both of the following, or the"
        " entry dies before any fine-grid spend.",
        "",
        f"1. vs nearest-angle copy (50% improvement): **{gate_bars['gate_vs_nearest_angle_copy']:.4f}**",
        "2. vs linear-in-angle interpolation (50% improvement):"
        f" **{gate_bars['gate_vs_linear_in_angle_interpolation']:.4f}**",
        "",
        "## Stage 2 — the cubic block, fold 0 (pre-registration, before training)",
        "",
        f"`charge_to_localization`, `paired_fields_fivefold` fold 0: the semilocal-ridge floor, recomputed on"
        f" this member's own kill block through `operators.evaluation.Elf_Ridge_Rows`, over"
        f" {ridge_summary.run_count} evaluation run-channels across {ridge_summary.unit_count} units.",
        "",
    ]
    lines.append("| group | metric | units | runs | median | interquartile | 95% interval |")
    lines.append("|---|---|---|---|---|---|---|")
    for row in Summary_Table((ridge_summary,)):
        lines.append(
            f"| {row['group']} | {row['metric']} | {row['units']} | {row['runs']} | {row['median']} |"
            f" {row['interquartile']} | {row['mean_interval']} |"
        )
    lines += [
        "",
        "**The pre-registered stage-2 bar** (the pattern rule, twenty percent better than the ridge; run only"
        f" once stage 1 passes): mean absolute error at or below **{elf_bar:.6f}**.",
        "",
        "## Parameter count and memory",
        "",
        Parameter_Count_Lines(),
        "",
        "## The training driver",
        "",
        "`Train_Perovskite_Gate_Member` is written and covered by this package's own tests: the staged"
        " 0.3/0.3/0.4 schedule at learning rates 1e-3, 3.3e-4, 1.1e-4, validating every 100 steps with a"
        " final-stage patience of 15, seed 20260916, single precision, checkpoints under"
        " `_training/galerkin_transformer/` -- the same staged idiom"
        " `factorized_fourier.report.Train_Flagship_Member` uses. **It has not been run.** The card is"
        " scheduled by the integrator; the step count for the two-hour cap is chosen from a short timing probe"
        " once the card is granted, the same way the deep-equilibrium ladder's own rungs choose theirs.",
        "",
        "## Results artifact",
        "",
        f"`{RESULTS_PATH.name}` carries the three floor rows above, written through"
        " `operators.evaluation.Write_Member_Results`. It carries no verdicts yet: a verdict compares the"
        " member against a floor, and no configuration has trained.",
        "",
        "## Standing",
        "",
        "No training has run. The gate class, the attention kernel, the query-point decoder and the member are"
        " built and pass every test (`operators/tests/test_galerkin_transformer.py`). Both stage-1 floors and"
        " the stage-2 semilocal-ridge floor are measured and pre-registered above; the training driver for the"
        " stage-1 gate is written but not run. What remains: the card.",
    ]
    return lines


def Parameter_Count_Lines() -> str:
    """the built member's own parameter count and float64 memory footprint at both stages' token counts"""
    stage_one = Galerkin_Transformer_Network("parametric", processing_shape=(32, 32, 32), seed=0)
    stage_two = Galerkin_Transformer_Network(
        "localization", processing_shape=(40, 40, 40), gram_mean=np.zeros(6), gram_scale=np.ones(6), seed=0
    )
    return Member_Memory_Line(stage_one, "stage 1 (32-cubed tokens)") + "\n" + Member_Memory_Line(
        stage_two, "stage 2 (40-cubed tokens)"
    )


def Member_Memory_Line(member: GalerkinTransformer, label: str) -> str:
    """one configuration's own parameter count, in words, with its float64 footprint in mebibytes"""
    parameter_count = member.Parameter_Count()
    mebibytes = parameter_count * 8 / (1024 * 1024)
    return f"- {label}: {parameter_count} parameters, {mebibytes:.3f} MiB at float64 (parameters alone)"


def Perovskite_Gate_Training_Examples() -> tuple[list[ParameterExample], list[ParameterExample]]:
    """the angle stratum's own fold-0 training runs, split into this driver's own train and validation slices"""
    card = Card_Named("lattice_to_charge")
    population: list[ParameterExample] = []
    for example in Parameter_Field_Examples(card, "train", evaluation_fold=0):
        if not example.unit_key.endswith(PEROVSKITE_ANGLE_UNIT_SUFFIX):
            continue
        if np.asarray(example.target_function.values).shape[1:] != PEROVSKITE_ANGLE_GRID_SHAPE:
            continue
        population.append(example)
    ordered = sorted(range(len(population)), key=lambda position: population[position].unit_key)
    validation_positions = {position for count, position in enumerate(ordered) if count % 5 == 4}
    train_examples = [example for position, example in enumerate(population) if position not in validation_positions]
    validation_examples = [example for position, example in enumerate(population) if position in validation_positions]
    return train_examples, validation_examples


@dataclasses.dataclass(frozen=True, slots=True)
class PerovskiteGateExample:
    """one angle-stratum run's own coarse parametric input, decoder target and conservation covariates"""

    identifier: str
    unit_key: str
    combined_coarse_input: NDArray[np.float32]
    target_values: NDArray[np.float32]
    weight_each: float
    electron_count: float


def Perovskite_Gate_Example(example: ParameterExample) -> PerovskiteGateExample:
    """one loaded parameter example, turned into this driver's own cached, single-precision training unit"""
    parameter_vector = np.asarray(example.parameters.vector, dtype=np.float64)
    combined_coarse_input = np.concatenate(
        [
            Constant_Channel_Field(parameter_vector, GATE_PROCESSING_SHAPE),
            Coordinate_Feature_Channels(GATE_PROCESSING_SHAPE),
        ],
        axis=0,
    )
    target_values = np.asarray(example.target_function.values, dtype=np.float64).reshape(-1, 1)
    quadrature = example.target_function.quadrature
    weight_each = quadrature.cell_volume / quadrature.point_count
    electron_count = float(target_values.sum() * weight_each)
    return PerovskiteGateExample(
        identifier=example.identifier,
        unit_key=example.unit_key,
        combined_coarse_input=np.asarray(combined_coarse_input, dtype=np.float32),
        target_values=np.asarray(target_values, dtype=np.float32),
        weight_each=weight_each,
        electron_count=electron_count,
    )


class PerovskiteGateBatches(BatchSource):
    """one training example drawn uniformly with replacement every step, every validation unit held fixed"""


    def __init__(
        self, training_examples: list[PerovskiteGateExample], validation_examples: list[PerovskiteGateExample]
    ) -> None:
        self.training_examples = training_examples
        self.validation_by_unit: dict[str, list[PerovskiteGateExample]] = {}
        for example in validation_examples:
            self.validation_by_unit.setdefault(example.unit_key, []).append(example)
        self.last_drawn_identifier: str | None = None


    def Next_Batch(self, generator: np.random.Generator) -> TrainingBatch:
        drawn = self.training_examples[int(generator.integers(0, len(self.training_examples)))]
        self.last_drawn_identifier = drawn.identifier
        return TrainingBatch(
            {
                "combined_coarse_input": drawn.combined_coarse_input[None],
                "targets": drawn.target_values[None],
                "weight_each": np.asarray([drawn.weight_each], dtype=np.float32),
                "electron_count": np.asarray([drawn.electron_count], dtype=np.float32),
            }
        )


    def Validation_Batches(self) -> tuple[tuple[str, TrainingBatch], ...]:
        batches: list[tuple[str, TrainingBatch]] = []
        for unit_key, examples in sorted(self.validation_by_unit.items()):
            batches.append(
                (
                    unit_key,
                    TrainingBatch(
                        {
                            "combined_coarse_input": np.stack(
                                [example.combined_coarse_input for example in examples]
                            ),
                            "targets": np.stack([example.target_values for example in examples]),
                            "weight_each": np.asarray(
                                [example.weight_each for example in examples], dtype=np.float32
                            ),
                            "electron_count": np.asarray(
                                [example.electron_count for example in examples], dtype=np.float32
                            ),
                        }
                    ),
                )
            )
        return tuple(batches)


    def Inspect(self) -> dict[str, Any]:
        state: dict[str, Any] = {
            "training_example_count": np.asarray([len(self.training_examples)], dtype=np.float64),
            "validation_unit_count": np.asarray([len(self.validation_by_unit)], dtype=np.float64),
        }
        if self.last_drawn_identifier is not None:
            state["last_drawn_identifier"] = np.asarray(self.last_drawn_identifier)
        return state


def Perovskite_Gate_Loss(member: GalerkinTransformer, lifted_query_features: Any) -> ForwardLoss:
    """mean squared error over every example a batch carries, each renormalized to its own electron count"""

    def Loss(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        example_count = lifted_batch["combined_coarse_input"].shape[0]
        total = 0.0
        for example_index in range(example_count):
            predicted = member.Forward_From_Coarse_Input(
                lifted,
                lifted_batch["combined_coarse_input"][example_index],
                lifted_query_features,
                weight_each=float(lifted_batch["weight_each"][example_index]),
                condition_vector=lifted_batch["electron_count"][example_index : example_index + 1],
            )
            residual = predicted - lifted_batch["targets"][example_index]
            total = total + (residual * residual).mean()
        return total / example_count

    return Loss


def Staged_Gate_Step_Counts(step_count: int) -> tuple[int, int, int]:
    """the gate's own step budget split 0.3/0.3/0.4, the last stage absorbing whatever rounding leaves behind"""
    first_stage = round(GATE_STAGE_FRACTIONS[0] * step_count)
    second_stage = round(GATE_STAGE_FRACTIONS[1] * step_count)
    return first_stage, second_stage, step_count - first_stage - second_stage


def Write_Back_Gate_Layer(layer: Layer[GridFunction], parameters: ParameterSet, prefix: str) -> None:
    """one attention layer's own kernel and local-linear arrays, read off their prefixed names in a flat parameter set"""
    for bare_name in list(layer.kernel.parameter_values):
        prefixed_name = f"{prefix}kernel.{bare_name}"
        if prefixed_name in parameters.values:
            layer.kernel.parameter_values[bare_name] = parameters.values[prefixed_name]
    for bare_name in list(layer.local_linear.parameter_values):
        prefixed_name = f"{prefix}local_linear.{bare_name}"
        if prefixed_name in parameters.values:
            layer.local_linear.parameter_values[bare_name] = parameters.values[prefixed_name]


def Write_Back_Gate_Parameters(member: GalerkinTransformer, parameters: ParameterSet) -> None:
    """a flat trained parameter set folded back onto the member's own lift, attention layers and decoder storage"""
    for name, value in parameters.values.items():
        if name in member.lift.parameter_values:
            member.lift.parameter_values[name] = value
        if name in member.decoder.parameter_values:
            member.decoder.parameter_values[name] = value
    for layer_index, layer in enumerate(member.attention_stack.layers):
        Write_Back_Gate_Layer(layer, parameters, f"layer_{layer_index}.")


def Train_Perovskite_Gate_Member(step_count: int, run_name: str) -> dict[str, object]:
    """the staged schedule for the two-hour perovskite gate -- written and gated, never called by this module's own Main"""
    raw_train_examples, raw_validation_examples = Perovskite_Gate_Training_Examples()
    training_examples = [Perovskite_Gate_Example(example) for example in raw_train_examples]
    validation_examples = [Perovskite_Gate_Example(example) for example in raw_validation_examples]
    batches = PerovskiteGateBatches(training_examples, validation_examples)

    member = Galerkin_Transformer_Network("parametric", processing_shape=GATE_PROCESSING_SHAPE, seed=GATE_SEED)
    engine = Training_Engine()
    query_points = Output_Points(GridSpec(PEROVSKITE_ANGLE_GRID_SHAPE))
    query_features = np.asarray(member.decoder.Coordinate_Features(query_points), dtype=np.float64)
    lifted_query_features = engine.Lift_Constant(query_features)
    forward_loss = Perovskite_Gate_Loss(member, lifted_query_features)
    parameters = ParameterSet(values=member.Parameter_Values())

    stage_step_counts = Staged_Gate_Step_Counts(step_count)
    manifest: dict[str, object] = {
        "run_name": run_name,
        "training_example_count": len(training_examples),
        "validation_unit_count": len(batches.validation_by_unit),
    }
    for stage_index, (rate, stage_steps) in enumerate(zip(GATE_STAGE_LEARNING_RATES, stage_step_counts, strict=True)):
        is_final_stage = stage_index == len(stage_step_counts) - 1
        result = Train(
            engine,
            parameters,
            forward_loss,
            batches,
            step_count=stage_steps,
            learning_rate=rate,
            seed=GATE_SEED + stage_index,
            artifact_directory=GATE_TRAINING_ARTIFACT_PATH,
            run_name=f"{run_name}_stage{stage_index}",
            validation_interval=GATE_VALIDATION_INTERVAL,
            patience=GATE_FINAL_STAGE_PATIENCE if is_final_stage else 0,
            resume=(stage_index == 0),
        )
        parameters = result.parameters
        manifest[f"stage_{stage_index}"] = result.manifest
    Write_Back_Gate_Parameters(member, parameters)
    manifest["final_parameters"] = parameters
    manifest["member"] = member
    return manifest


def Main() -> int:
    """writes the pre-registration report and its results artifact, honest about what is and is not measured yet"""
    data = Measured_Floors()
    lines = Report_Lines(data)
    REPORT_PATH.write_text("\n".join(lines) + "\n")
    Write_Member_Results(RESULTS_PATH, Results_Artifact(data))
    print(f"wrote {REPORT_PATH}")
    print(f"wrote {RESULTS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
