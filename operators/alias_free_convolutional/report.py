"""the alias-free convolutional member's floors, pre-registered ladder and grid-shift check, then its own result"""

import dataclasses
import re
from pathlib import Path
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray

from operators.alias_free_convolutional import (
    AliasFreeConvolutional,
    Alias_Free_Convolutional_Network,
    Augmented_Training_Pair,
    StencilActivation,
)
from operators.data import Archive_Path, POOL_ROOT, STORE_NAME
from operators.evaluation import (
    CubicBlock,
    Elf_Ridge_Rows,
    FINE_SHAPE,
    Loaded_Density_And_Magnetization,
    LOCALIZATION_CHANNELS,
    MemberResults,
    MetricSummary,
    Nearest_Run_Rows,
    Recorded_Bars,
    RIDGE_TRAIN_RUN_COUNT,
    ScoredRun,
    Shell_Filter_Rows,
    Summarize,
    Summarize_By,
    Summary_Table,
    Training_Mean_Rows,
    Write_Member_Results,
)
from operators.factorized_fourier import Gram_Six, Gram_Statistics, Log_Compressed_Channels, Reference_Density, Standardized_Gram
from operators.framework import GridFunction, Layer
from operators.inspection import Render_Inspection_Suite, Render_Table
from operators.substrate import ParameterSet
from operators.training import BatchSource, Train, Training_Engine, TrainingBatch

REPORT_PATH = Path(__file__).parent / "report.md"
FIGURES_PATH = Path(__file__).parent / "figures"
RESULTS_PATH = Path(__file__).parent / "results.json"
# the inspection arrays are fields, and a field never leaves the pool -- only the drawing does
ARRAY_CACHE_PATH = POOL_ROOT / STORE_NAME / "_figures" / "alias_free_convolutional"
# checkpoints are scratch, not a corpus artifact, but they still hold no volumetric data either way
TRAINING_ARTIFACT_PATH = POOL_ROOT / STORE_NAME / "_training" / "alias_free_convolutional"

CARD_METRIC_NAMES = ("mean_absolute_error", "structural_similarity_3d", "relative_l2")

# fixed for both trained configurations, so the pointwise twin and the alias-free CNO differ by activation alone
MEMBER_SEED = 20260916

# the flagship's own staged schedule, reused verbatim (test-suite.md names no schedule of its own for I.2)
PEAK_LEARNING_RATE = 1e-3
DIVERGENCE_PROBE_STEPS = 200
VALIDATION_INTERVAL = 100
FINAL_STAGE_PATIENCE = 15
STAGE_FRACTIONS = (0.3, 0.3, 0.4)

TWIN_RUN_PREFIX = "elf_fold0_pointwise_twin"
CNO_RUN_PREFIX = "elf_fold0_cno"
TWIN_WALL_CLOCK_CAP_SECONDS = 8 * 3600
CNO_WALL_CLOCK_CAP_SECONDS = 12 * 3600
COST_PROBE_STEP_COUNT = 300

# the canon's own band (test-suite.md section 2, I.2); only the multiples of four inside it clear two halvings
GRID_SHIFT_PROBE_SEED = 20260917
GRID_SHIFT_PROBE_COUNT = 21
GRID_SHIFT_AXIS_CANDIDATES = (72, 76, 80, 84)


def Input_Statistics(
    block: CubicBlock, training_identifiers: list[str]
) -> tuple[float, NDArray[np.float64], NDArray[np.float64]]:
    """the reference density and Gram standardization one training population fixes, reused unchanged at evaluation"""
    density_sample: list[NDArray[np.float64]] = []
    magnetization_sample: list[NDArray[np.float64]] = []
    for identifier in training_identifiers[:RIDGE_TRAIN_RUN_COUNT]:
        density, magnetization, _ = Loaded_Density_And_Magnetization(block.campaign_of[identifier], identifier)
        density_sample.append(density)
        magnetization_sample.append(magnetization)
    reference_density = Reference_Density(density_sample, magnetization_sample)
    del density_sample, magnetization_sample

    lattices = [
        Loaded_Density_And_Magnetization(block.campaign_of[identifier], identifier)[2]
        for identifier in training_identifiers
    ]
    gram_mean, gram_scale = Gram_Statistics(lattices)
    return reference_density, gram_mean, gram_scale


@dataclasses.dataclass(frozen=True, slots=True)
class MemberExample:
    """one run's log-compressed spin channels and standardized Gram vector, cached beside its coarse target"""

    identifier: str
    unit_key: str
    campaign: str
    log_density_values: NDArray[np.float32]
    gram_vector: NDArray[np.float32]
    target_values: NDArray[np.float32]


def Member_Examples(
    identifiers: list[str],
    block: CubicBlock,
    reference_density: float,
    gram_mean: NDArray[np.float64],
    gram_scale: NDArray[np.float64],
) -> list[MemberExample]:
    """every named run, held resident as its own log-density channels, Gram vector and coarse target, single precision"""
    examples: list[MemberExample] = []
    for identifier in identifiers:
        campaign = block.campaign_of[identifier]
        density, magnetization, lattice = Loaded_Density_And_Magnetization(campaign, identifier)
        log_density_values = Log_Compressed_Channels(density, magnetization, reference_density)
        gram_vector = Standardized_Gram(Gram_Six(lattice), gram_mean, gram_scale)
        with np.load(Archive_Path(campaign, identifier)) as archive:
            target_values = np.stack(
                [np.asarray(archive[channel], dtype=np.float64) for channel in LOCALIZATION_CHANNELS]
            )
        examples.append(
            MemberExample(
                identifier=identifier,
                unit_key=block.unit_of[identifier],
                campaign=campaign,
                log_density_values=np.asarray(log_density_values, dtype=np.float32),
                gram_vector=np.asarray(gram_vector, dtype=np.float32),
                target_values=np.asarray(target_values, dtype=np.float32),
            )
        )
    return examples


class AugmentedMemberBatches(BatchSource):
    """one augmented training example drawn every step, every validation unit held fixed and unaugmented"""


    def __init__(self, training_examples: list[MemberExample], validation_examples: list[MemberExample]) -> None:
        self.training_examples = training_examples
        self.validation_by_unit: dict[str, list[MemberExample]] = {}
        for example in validation_examples:
            self.validation_by_unit.setdefault(example.unit_key, []).append(example)
        self.last_drawn_identifier: str | None = None


    def Next_Batch(self, generator: np.random.Generator) -> TrainingBatch:
        drawn = self.training_examples[int(generator.integers(0, len(self.training_examples)))]
        self.last_drawn_identifier = drawn.identifier
        augmented_density, augmented_target = Augmented_Training_Pair(
            np.asarray(drawn.log_density_values, dtype=np.float64),
            np.asarray(drawn.target_values, dtype=np.float64),
            generator,
        )
        return TrainingBatch(
            {
                "log_density_values": np.asarray(augmented_density, dtype=np.float32)[None],
                "gram_vector": drawn.gram_vector[None],
                "targets": np.asarray(augmented_target, dtype=np.float32)[None],
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
                            "log_density_values": np.stack([example.log_density_values for example in examples]),
                            "gram_vector": np.stack([example.gram_vector for example in examples]),
                            "targets": np.stack([example.target_values for example in examples]),
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


def Member_Loss(member: AliasFreeConvolutional, fine_shape: tuple[int, int, int] = FINE_SHAPE) -> Any:
    """mean squared error over every example a batch carries, looped since the lifted path takes one at a time"""

    def Loss(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        example_count = lifted_batch["log_density_values"].shape[0]
        total = 0.0
        for example_index in range(example_count):
            predicted = member.Forward_Field(
                lifted,
                lifted_batch["log_density_values"][example_index],
                lifted_batch["gram_vector"][example_index],
                fine_shape,
            )
            residual = predicted - lifted_batch["targets"][example_index]
            total = total + (residual * residual).mean()
        return total / example_count

    return Loss


def Staged_Step_Counts(step_count: int, fractions: tuple[float, float, float] = STAGE_FRACTIONS) -> tuple[int, int, int]:
    """a step budget split across three stages, the last absorbing whatever rounding leaves behind"""
    first_stage = round(fractions[0] * step_count)
    second_stage = round(fractions[1] * step_count)
    return first_stage, second_stage, step_count - first_stage - second_stage


def Sane_Loss_Curve(loss_curve: NDArray[np.float64], validation_curve: NDArray[np.float64]) -> bool:
    """every recorded loss and validation score stayed finite, and neither run away from where it started"""
    if loss_curve.size == 0 or validation_curve.size == 0:
        return False
    if not (bool(np.all(np.isfinite(loss_curve))) and bool(np.all(np.isfinite(validation_curve)))):
        return False
    return bool(loss_curve[-1] < 10.0 * loss_curve[0] + 1.0) and bool(validation_curve[-1] < 10.0 * validation_curve[0] + 1.0)


def Write_Back_Layer(layer: Layer[GridFunction], parameters: ParameterSet, prefix: str) -> None:
    """one layer's own kernel and local-linear arrays, read off their prefixed names in a flat parameter set"""
    for bare_name in list(layer.kernel.parameter_values):
        prefixed_name = f"{prefix}.kernel.{bare_name}"
        if prefixed_name in parameters.values:
            layer.kernel.parameter_values[bare_name] = parameters.values[prefixed_name]
    for bare_name in list(layer.local_linear.parameter_values):
        prefixed_name = f"{prefix}.local_linear.{bare_name}"
        if prefixed_name in parameters.values:
            layer.local_linear.parameter_values[bare_name] = parameters.values[prefixed_name]


def Write_Back_Parameters(member: AliasFreeConvolutional, parameters: ParameterSet) -> None:
    """a flat trained parameter set folded back onto the member's own part-shaped storage"""
    for name, value in parameters.values.items():
        if name in member.lift.parameter_values:
            member.lift.parameter_values[name] = value
        if name in member.projection.parameter_values:
            member.projection.parameter_values[name] = value
    composition = member.multi_scale
    for descending_index, layer in enumerate(composition.descending_layers):
        Write_Back_Layer(layer, parameters, f"descending_{descending_index}")
    Write_Back_Layer(composition.bottom_layer, parameters, "bottom")
    for ascending_index, layer in enumerate(composition.ascending_layers):
        Write_Back_Layer(layer, parameters, f"ascending_{ascending_index}")


def Train_Convolutional_Member(
    step_count: int,
    run_name: str,
    activation: StencilActivation,
    stage_fractions: tuple[float, float, float] = STAGE_FRACTIONS,
) -> dict[str, object]:
    """the staged run shared by the CNO and its pointwise twin: seed 20260916, batch one, augmentation on"""
    block = CubicBlock()
    training_identifiers = block.member_train
    validation_identifiers = block.validation

    reference_density, gram_mean, gram_scale = Input_Statistics(block, training_identifiers)
    training_examples = Member_Examples(training_identifiers, block, reference_density, gram_mean, gram_scale)
    validation_examples = Member_Examples(validation_identifiers, block, reference_density, gram_mean, gram_scale)
    batches = AugmentedMemberBatches(training_examples, validation_examples)

    member = Alias_Free_Convolutional_Network(
        reference_density=reference_density,
        gram_mean=gram_mean,
        gram_scale=gram_scale,
        activation=activation,
        seed=MEMBER_SEED,
    )
    forward_loss = Member_Loss(member)
    parameters = ParameterSet(values=member.Parameter_Values())
    engine = Training_Engine()

    stage_step_counts = Staged_Step_Counts(step_count, stage_fractions)
    probe_steps = min(DIVERGENCE_PROBE_STEPS, stage_step_counts[0])
    chosen_peak_rate = PEAK_LEARNING_RATE
    probe_result = Train(
        engine, parameters, forward_loss, batches, step_count=probe_steps, learning_rate=chosen_peak_rate,
        seed=MEMBER_SEED, artifact_directory=TRAINING_ARTIFACT_PATH, run_name=f"{run_name}_stage0",
        validation_interval=probe_steps, patience=0,
    )
    if not Sane_Loss_Curve(probe_result.loss_curve, probe_result.validation_curve):
        chosen_peak_rate = PEAK_LEARNING_RATE * 0.3
        probe_result = Train(
            engine, ParameterSet(values=member.Parameter_Values()), forward_loss, batches, step_count=probe_steps,
            learning_rate=chosen_peak_rate, seed=MEMBER_SEED, artifact_directory=TRAINING_ARTIFACT_PATH,
            run_name=f"{run_name}_stage0", validation_interval=probe_steps, patience=0, resume=False,
        )
        if not Sane_Loss_Curve(probe_result.loss_curve, probe_result.validation_curve):
            raise RuntimeError(
                "the loss is non-finite or diverging at both the peak and the reduced rate within the probe"
            )
    parameters = probe_result.parameters
    stage_rates = (chosen_peak_rate, chosen_peak_rate / 3.0, chosen_peak_rate / 9.0)

    manifest: dict[str, object] = {
        "run_name": run_name,
        "activation": activation,
        "reference_density": reference_density,
        "probe_learning_rate": chosen_peak_rate,
        "probe_steps": probe_steps,
        "training_example_count": len(training_examples),
        "validation_unit_count": len(batches.validation_by_unit),
    }
    for stage_index, (rate, stage_steps) in enumerate(zip(stage_rates, stage_step_counts, strict=True)):
        is_final_stage = stage_index == len(stage_step_counts) - 1
        result = Train(
            engine, parameters, forward_loss, batches, step_count=stage_steps, learning_rate=rate,
            seed=MEMBER_SEED + stage_index, artifact_directory=TRAINING_ARTIFACT_PATH,
            run_name=f"{run_name}_stage{stage_index}", validation_interval=VALIDATION_INTERVAL,
            patience=FINAL_STAGE_PATIENCE if is_final_stage else 0, resume=(stage_index == 0),
        )
        parameters = result.parameters
        manifest[f"stage_{stage_index}"] = result.manifest
    Write_Back_Parameters(member, parameters)
    manifest["final_parameters"] = parameters
    manifest["member"] = member
    return manifest


def Cost_Probe(activation: StencilActivation, step_count: int = COST_PROBE_STEP_COUNT) -> dict[str, object]:
    """seconds per step for one activation, measured on the real batch source; the wall-clock half of the cost probe"""
    block = CubicBlock()
    training_identifiers = block.member_train
    reference_density, gram_mean, gram_scale = Input_Statistics(block, training_identifiers)
    training_examples = Member_Examples(training_identifiers, block, reference_density, gram_mean, gram_scale)
    batches = AugmentedMemberBatches(training_examples, training_examples[:1])

    member = Alias_Free_Convolutional_Network(
        reference_density=reference_density,
        gram_mean=gram_mean,
        gram_scale=gram_scale,
        activation=activation,
        seed=MEMBER_SEED,
    )
    parameters = ParameterSet(values=member.Parameter_Values())
    result = Train(
        Training_Engine(), parameters, Member_Loss(member), batches, step_count=step_count,
        learning_rate=PEAK_LEARNING_RATE, seed=MEMBER_SEED, validation_interval=step_count, patience=0,
    )
    wall_clock_seconds = float(cast(float, result.manifest["wall_clock_seconds"]))
    seconds_per_step = wall_clock_seconds / step_count
    wall_clock_cap = TWIN_WALL_CLOCK_CAP_SECONDS if activation == "pointwise" else CNO_WALL_CLOCK_CAP_SECONDS
    return {
        "activation": activation,
        "step_count": step_count,
        "wall_clock_seconds": wall_clock_seconds,
        "seconds_per_step": seconds_per_step,
        "wall_clock_cap_seconds": wall_clock_cap,
        "capped_step_budget": int(wall_clock_cap / seconds_per_step),
    }


@dataclasses.dataclass(frozen=True, slots=True)
class GridShiftProbe:
    """one evaluation-block run paired with the axis-stretched shape the identity check resamples it to"""

    identifier: str
    campaign: str
    unit_key: str
    stretched_shape: tuple[int, int, int]


def Proportional_Probe_Counts(block: CubicBlock, total: int) -> dict[str, int]:
    """each campaign's own share of the probe count, apportioned by its evaluation-block population"""
    population: dict[str, int] = {}
    for identifier in block.evaluation:
        campaign = block.campaign_of[identifier]
        population[campaign] = population.get(campaign, 0) + 1
    exact_shares = {campaign: total * count / len(block.evaluation) for campaign, count in population.items()}
    counts = {campaign: int(share) for campaign, share in exact_shares.items()}
    remaining_seats = total - sum(counts.values())
    # the largest dropped fraction gets a leftover seat first, tie broken by campaign name for determinism
    ranked_campaigns = sorted(population, key=lambda campaign: (exact_shares[campaign] - counts[campaign], campaign))
    for campaign in reversed(ranked_campaigns[len(ranked_campaigns) - remaining_seats :]):
        counts[campaign] += 1
    return counts


def Strided_Sample(items: list[str], count: int) -> list[str]:
    """count items evenly spaced across the sorted list, first and last included whenever more than one is asked"""
    if count <= 0 or not items:
        return []
    if count >= len(items):
        return list(items)
    positions = [round(position * (len(items) - 1) / (count - 1)) for position in range(count)] if count > 1 else [0]
    chosen = sorted(set(positions))
    fallback_position = 0
    while len(chosen) < count:
        if fallback_position not in chosen:
            chosen = sorted(chosen + [fallback_position])
        fallback_position += 1
    return [items[position] for position in chosen[:count]]


def Grid_Shift_Probe_Set(block: CubicBlock) -> tuple[GridShiftProbe, ...]:
    """21 evaluation-block runs, apportioned across campaigns, each paired with its own axis-stretched shape"""
    generator = np.random.default_rng(GRID_SHIFT_PROBE_SEED)
    counts = Proportional_Probe_Counts(block, GRID_SHIFT_PROBE_COUNT)
    probes: list[GridShiftProbe] = []
    for campaign in sorted(counts):
        campaign_identifiers = sorted(
            identifier for identifier in block.evaluation if block.campaign_of[identifier] == campaign
        )
        for identifier in Strided_Sample(campaign_identifiers, counts[campaign]):
            drawn_axes = generator.integers(0, len(GRID_SHIFT_AXIS_CANDIDATES), size=3)
            stretched_shape = (
                int(GRID_SHIFT_AXIS_CANDIDATES[int(drawn_axes[0])]),
                int(GRID_SHIFT_AXIS_CANDIDATES[int(drawn_axes[1])]),
                int(GRID_SHIFT_AXIS_CANDIDATES[int(drawn_axes[2])]),
            )
            probes.append(GridShiftProbe(identifier, campaign, block.unit_of[identifier], stretched_shape))
    return tuple(sorted(probes, key=lambda probe: probe.identifier))


def Floor_Summaries(rows: list[ScoredRun], floor_label: str) -> list[MetricSummary]:
    """one floor's pooled summary beside its own per-campaign breakdown, for every card metric"""
    summaries: list[MetricSummary] = []
    for metric_name in CARD_METRIC_NAMES:
        summaries.append(Summarize(rows, metric_name, floor_label))
        for campaign_summary in Summarize_By(rows, metric_name, "campaign"):
            summaries.append(
                dataclasses.replace(campaign_summary, group_name=f"{floor_label}__{campaign_summary.group_name}")
            )
    return summaries


def Block_Lines(block: CubicBlock) -> list[str]:
    """the block counts, shared with the flagship and every other member this task pattern touches"""
    return [
        "## The block",
        "",
        "Cubic block (`supercell_strains` and `defect_set`, 80³ charge density, full localization and potential),"
        " the same block and the same folds the flagship measures on:"
        f" {len(block.floor_train)} runs across folds one through four train the floors,"
        f" {len(block.evaluation)} runs in fold zero are the evaluation (kill) block. The member additionally"
        f" holds out fold one ({len(block.validation)} runs) for its own early stopping and trains on folds two"
        f" through four ({len(block.member_train)} runs); this member trains at each run's own native 80³ grid"
        " rather than a fixed coarse trunk, so no truncate-early step and no processing-shape choice enter here.",
        "",
    ]


def Floor_Lines(
    ridge_rows: list[ScoredRun],
    filter_rows: list[ScoredRun],
    mean_rows: list[ScoredRun],
    copy_rows: list[ScoredRun],
    bars: dict[str, float],
) -> list[str]:
    """the four floors and the five-level claim ladder, measured before this member has seen the block"""
    summaries: list[MetricSummary] = []
    for floor_label, rows in (
        ("training_mean_trivial_floor", mean_rows),
        ("nearest_run_copy_floor", copy_rows),
        ("per_shell_linear_filter", filter_rows),
        ("semilocal_ridge_floor", ridge_rows),
    ):
        summaries.extend(Floor_Summaries(rows, floor_label))
    return [
        "## Floors, measured before training, on this exact block, in the card's own metrics",
        "",
        "The same four floor recipes the flagship measures on this block (`operators.evaluation`'s ridge,"
        " per-shell filter, training-mean and nearest-run-copy builders), shared rather than reimplemented; a"
        " floor-reproduction test checks the pooled mean absolute error below against the flagship's own"
        " committed 0.0976 / 0.0830 / 0.0160 / 0.0062 (semilocal ridge, per-shell filter, training mean,"
        " nearest-run copy) instead of remeasuring the recipe from scratch.",
        "",
        "```",
        Render_Table(Summary_Table(tuple(summaries))),
        "```",
        "",
        "### the claim ladder, pre-registered before the member has seen this block",
        "",
        "Absolute mean absolute error, lower stricter, the same recipe as the flagship's own ladder"
        " (`test-suite.md` §2's pattern rule, this entry's own `IMPLEMENTATION.md` kill, then three levels"
        " added for scale):",
        "",
        f"1. **canon kill** (I.1's own bar, half the semilocal ridge): {bars['canon_kill_semilocal_ridge_half']:.6f}",
        "2. **canon pattern rule** (at least 20% better than the ridge or the task is left):"
        f" {bars['canon_pattern_rule_semilocal_ridge_twenty_percent']:.6f}",
        f"3. **added, beat the training-mean template**: {bars['added_beat_training_mean_template']:.6f}",
        f"4. **added, beat the nearest-run copy**: {bars['added_beat_nearest_run_copy']:.6f}",
        f"5. **added, the stretch level** (half the template's error): {bars['added_stretch_half_the_template']:.6f}",
        "",
    ]


def Identity_Check_Lines(probes: tuple[GridShiftProbe, ...]) -> list[str]:
    """the entry's own two bars against the pointwise twin, and the pre-registered grid-shift probe set"""
    rows = tuple(
        cast(
            dict[str, object],
            {
                "identifier": probe.identifier,
                "campaign": probe.campaign,
                "shape": f"{probe.stretched_shape[0]}x{probe.stretched_shape[1]}x{probe.stretched_shape[2]}",
            },
        )
        for probe in probes
    )
    return [
        "### the identity check, pre-registered",
        "",
        "Two bars this entry alone carries, neither measured yet. Against the trained pointwise twin"
        ' (`activation="pointwise"`, same widths, same seeds, same augmentation, the canon\'s own width-matched'
        " plain U-Net stand-in): the CNO's own median error must match or beat the twin's, on both lower-is-better"
        " card metrics, at the native 80³ grid. And under the grid-shift probe below, the CNO's own error must"
        " inflate at most half as much as the twin's does when both answer on an axis-stretched input rather"
        " than the native grid. If the twin ties the CNO on both checks, the alias-free surcharge bought nothing"
        " and the entry is rejected regardless of how it scores against the floors above.",
        "",
        f"**The {len(probes)} axis-stretched grid-shift probe cells** (`test-suite.md` §2, I.2: \"the 21"
        ' axis-stretched 72–84 cells"), fixed here before either model trains. Each cell is one evaluation-block'
        " run, apportioned across the two campaigns by their own population in that block, paired with a shape"
        " drawn independently per axis from {72, 76, 80, 84} — the only lengths in the canon's 72-84 band"
        " divisible by four, which is what this composition's own two halvings require of every axis"
        " (`Halved_Shape` raises on an odd intermediate; verified directly against this exact assembly, not"
        " assumed: an axis of 78 fails at the second halving, landing on `(39, 40, 40)`). The input will be"
        " sinc-resampled (`Spectral_Resampled`) to the listed shape before either model sees it; the target is"
        " the same run's own coarse localization field, sinc-resampled to that shape's own second scale for"
        " comparison. Not yet measured — this table is the pre-registration; the inflation numbers land in the"
        " result section once both models are trained.",
        "",
        "```",
        Render_Table(rows),
        "```",
        "",
    ]


_STAGE_CHECKPOINT_PATTERN = re.compile(r"_stage(\d+)_checkpoint\.npz$")


def Latest_Stage_Checkpoint_For_Prefix(artifact_directory: Path, run_name_prefix: str) -> Path:
    """the furthest-along stage checkpoint among every run whose own name starts with the given prefix"""
    candidates: list[tuple[int, float, Path]] = []
    for path in artifact_directory.glob(f"{run_name_prefix}*_stage*_checkpoint.npz"):
        match = _STAGE_CHECKPOINT_PATTERN.search(path.name)
        if match is not None:
            candidates.append((int(match.group(1)), path.stat().st_mtime, path))
    if not candidates:
        raise FileNotFoundError(f"no stage checkpoint found for a run named {run_name_prefix!r}* under {artifact_directory}")
    newest_mtime = max(mtime for _, mtime, _ in candidates)
    newest_run_candidates = [(stage, path) for stage, mtime, path in candidates if mtime == newest_mtime]
    return max(newest_run_candidates, key=lambda pair: pair[0])[1]


def Result_Lines() -> list[str]:
    """the member's own result once both checkpoints exist, or the honest placeholder before either does"""
    lines = ["## The member's own result (electron localization, fold 0)", ""]
    for label, run_name_prefix in (("pointwise twin", TWIN_RUN_PREFIX), ("CNO (alias-free)", CNO_RUN_PREFIX)):
        try:
            Latest_Stage_Checkpoint_For_Prefix(TRAINING_ARTIFACT_PATH, run_name_prefix)
        except FileNotFoundError:
            lines += [
                f"**{label}** (`{run_name_prefix}_<steps>`): training is not yet run; no checkpoint under"
                f" `{TRAINING_ARTIFACT_PATH}` yet. This section fills in from a `Latest_Stage_Checkpoint_For_"
                "Prefix` lookup alone once one exists, no other change to this report needed.",
                "",
            ]
    return lines


def Write_Fresh_Inspection_Figures(
    cache_root: Path = ARRAY_CACHE_PATH, figures_root: Path = FIGURES_PATH
) -> tuple[int, Path, Path]:
    """the freshly built (untrained) member's own inspection suite, confirming the surface renders end to end"""
    block = CubicBlock()
    reference_density, gram_mean, gram_scale = Input_Statistics(block, block.member_train)
    member = Alias_Free_Convolutional_Network(
        reference_density=reference_density, gram_mean=gram_mean, gram_scale=gram_scale,
        activation="alias_free", seed=MEMBER_SEED,
    )
    cache = cache_root / "fold_0" / "alias_free" / "untrained"
    cache.mkdir(parents=True, exist_ok=True)
    inspected = {name: np.asarray(value, dtype=np.float64) for name, value in member.Inspect().items()}
    np.savez(cache / "inspection.npz", **cast(dict[str, Any], inspected))
    with np.load(cache / "inspection.npz") as archive:
        restored = {name: np.asarray(archive[name], dtype=np.float64) for name in archive.files}

    directory = figures_root / "fold_0" / "alias_free" / "untrained"
    suite = Render_Inspection_Suite(restored, directory, "alias_free_convolutional untrained (fold 0)")
    if suite.skipped:
        raise ValueError(f"no renderer for {suite.skipped}, which means the inspection surface is incomplete")
    return len(suite.written), directory, cache


def Inspection_Lines() -> list[str]:
    """the untrained member's own inspection surface, drawn now so the doctrine is checked before any run"""
    figure_count, figures_directory, cache_directory = Write_Fresh_Inspection_Figures()
    try:
        figures_directory = figures_directory.relative_to(Path.cwd())
    except ValueError:
        pass
    return [
        "## Inspection",
        "",
        "Every array `AliasFreeConvolutional.Inspect()` carries is listed in this package's own"
        " `IMPLEMENTATION.md`; drawn here on a freshly built (untrained, randomly initialized) member so the"
        " surface is confirmed end to end before either training run exists, not asserted from the table alone."
        f" {figure_count} files written under `{figures_directory}`, arrays cached at `{cache_directory}`. Once a"
        " checkpoint exists, this same call on the loaded member draws the trained state instead, no other"
        " change to this report needed.",
        "",
    ]


def Standing_Lines(probes: tuple[GridShiftProbe, ...]) -> list[str]:
    """the current state of this entry, for a reader who only wants to know what has and has not happened"""
    return [
        "## Standing",
        "",
        "Built and tested (`operators.alias_free_convolutional`, its own test file green including the fused"
        " activation's gradient and accelerator-memory checks). Floors measured on the real block above and"
        " pre-registered before training; the identity check's grid-shift probe set is fixed"
        f" ({len(probes)} cells, listed above) before either model has seen it. `Train_Convolutional_Member` and"
        " `Cost_Probe` (this module) are written and ready; neither has been run. Card plan once granted: a"
        f" 300-step cost probe for each activation, then the pointwise twin (cap {TWIN_WALL_CLOCK_CAP_SECONDS // 3600} h),"
        f" then the CNO (cap {CNO_WALL_CLOCK_CAP_SECONDS // 3600} h), both augmentation on, seed {MEMBER_SEED},"
        " batch one, validation every 100 steps on fold one, final-stage patience 15. Canon rungs on a miss,"
        " each tried once before a dead end: drop the Gram channels, then a per-campaign fallback.",
        "",
    ]


def Main() -> int:
    """the whole report: block, floors, the pre-registered ladder and grid-shift probe, inspection, standing"""
    block = CubicBlock()
    ridge_rows = Elf_Ridge_Rows(block)
    filter_rows = Shell_Filter_Rows(block)
    mean_rows = Training_Mean_Rows(block)
    copy_rows = Nearest_Run_Rows(block)
    bars = Recorded_Bars(ridge_rows, mean_rows, copy_rows)
    probes = Grid_Shift_Probe_Set(block)

    lines: list[str] = [
        "# alias_free_convolutional — charge density → electron localization field",
        "",
        "Convolutional Neural Operator (Raonić et al., NeurIPS 2023), alias-free formalism (Bartolucci et al.,"
        " ReNO, NeurIPS 2023). Suite entry `test-suite.md` §2, I.2. See `IMPLEMENTATION.md` for the assembly.",
        "",
    ]
    lines += Block_Lines(block)
    lines += Floor_Lines(ridge_rows, filter_rows, mean_rows, copy_rows, bars)
    lines += Identity_Check_Lines(probes)
    lines += Result_Lines()
    lines += Inspection_Lines()
    lines += Standing_Lines(probes)
    REPORT_PATH.write_text("\n".join(lines) + "\n")

    results = MemberResults(
        member="alias_free_convolutional",
        regenerate="python -m operators.alias_free_convolutional.report",
        rows=(),
        verdicts=(),
    )
    Write_Member_Results(RESULTS_PATH, results)
    print(f"wrote {REPORT_PATH}")
    print(f"wrote {RESULTS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
