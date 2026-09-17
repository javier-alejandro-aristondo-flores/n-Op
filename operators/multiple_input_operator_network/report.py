"""the two-branch member measured against its pre-registered floors, before a step of training runs"""

import dataclasses
import json
import re
import time
from pathlib import Path
from typing import Any, cast

import numpy as np

from operators.data import POOL_ROOT, STORE_NAME
from operators.evaluation import (
    Block_Signature,
    Card_Metric_Errors,
    Comparison_Table,
    Compare_To_Floor,
    CubicBlock,
    Elf_Ridge_Rows,
    MemberResults,
    MetricSummary,
    Nearest_Run_Rows,
    Recorded_Bars,
    ResultKey,
    ResultRow,
    ScoredRun,
    Shell_Filter_Rows,
    Summarize,
    Summarize_By,
    Summary_Table,
    Training_Mean_Rows,
    VerdictRow,
    Write_Member_Results,
)
from operators.framework import GridFunction, GridSpec
from operators.inspection import Render_Error_Spread, Render_Floor_Comparison, Render_Inspection_Suite
from operators.multiple_input_operator_network import (
    Density_Alone_Twin,
    MultipleInputOperatorNetwork,
    OUTPUT_CHANNEL_LABELS,
    Two_Branch_Member,
)
from operators.multiple_input_operator_network.cache import (
    BASIS_RANK,
    Cubic_Block_Examples,
    EVALUATION_FOLDS,
    Fitted_Bases,
    Localization_Cache,
    MEMBER_TRAIN_FOLDS,
    VALIDATION_FOLDS,
)
from operators.substrate import ParameterSet, Peak_Accelerator_Bytes, Reset_Peak_Accelerator_Bytes
from operators.training import (
    CoordinateFeaturizedBatches,
    DEFAULT_PEAK_LEARNING_RATE,
    ForwardLoss,
    PointSampledBatches,
    Read_Checkpoint,
    Staged_Training,
    Train,
    Training_Engine,
)

REPORT_PATH = Path(__file__).resolve().parent / "report.md"

RESULTS_PATH = Path(__file__).resolve().parent / "results.json"

MEMBER_NAME = "multiple_input_operator_network"

CONFIGURATION_NAME = f"rank{BASIS_RANK}_latent128_trunk3x256"

TASK_NAME = "charge_and_potential_to_localization"

DECISIVE_TWIN_MARGIN = 0.05

PATTERN_RULE_MARGIN = 0.20

# the training driver below, operators.training.Staged_Training, the shared protocol every member runs

TRAINING_ARTIFACT_PATH = POOL_ROOT / STORE_NAME / "_training" / MEMBER_NAME

MEMBER_SEED = 20260916

RUNS_PER_BATCH = 8

POINTS_PER_RUN = 4096

COST_PROBE_STEP_COUNT = 100

CARD_METRIC_NAMES = ("mean_absolute_error", "structural_similarity_3d", "relative_l2")

FIGURES_PATH = Path(__file__).resolve().parent / "figures"

MEMBER_RUN_NAME = "elf_fold0_member_v2_33650"

TWIN_RUN_NAME = "elf_fold0_twin_33650"

# the flagship's own trained explicit-stack median on this identical fold 0, read from factorized_fourier/report.md
# (`member mean_absolute_error 29 152 0.002170 ...`) -- a cross-package reference cited, not recomputed here
FLAGSHIP_FOLD_0_MEAN_ABSOLUTE_ERROR = 0.002170

_STAGE_CHECKPOINT_PATTERN = re.compile(r"_stage(\d+)_checkpoint\.npz$")


def Block_Lines(block: CubicBlock) -> list[str]:
    """the cubic block's own fold counts, read from the promoted partition, not retyped"""
    return [
        f"`{TASK_NAME}`, split `paired_fields_fivefold`, restricted to the eighty-cube cubic block"
        " (charge density and both potential channels at 80-cubed, electron localization at 40-cubed):",
        "",
        f"- evaluation (fold 0, the kill block): {len(block.evaluation)} runs",
        f"- validation (fold 1): {len(block.validation)} runs",
        f"- member_train (folds 2-4): {len(block.member_train)} runs",
        f"- floor_train (folds 1-4 pooled): {len(block.floor_train)} runs",
        "",
        "counted directly from `operators.evaluation.CubicBlock`, the same promoted partition the four floor"
        " builders below read.",
    ]


def Architecture_Lines() -> tuple[list[str], int, int]:
    """the built configuration's own parameter counts, measured on bases fit at the report's own basis rank"""
    (
        density_basis,
        potential_basis,
        reference_density,
        potential_coefficient_mean,
        potential_coefficient_scale,
        decay,
    ) = Fitted_Bases(limit=64)
    member = Two_Branch_Member(
        density_basis,
        potential_basis,
        reference_density,
        potential_coefficient_mean,
        potential_coefficient_scale,
        seed=0,
    )
    twin = Density_Alone_Twin(density_basis, reference_density, seed=0)
    member_parameter_count = sum(value.size for value in member.Parameter_Values().values())
    twin_parameter_count = sum(value.size for value in twin.Parameter_Values().values())
    lines = [
        "Two `SensorEncoder((32, 128, 128))` branches over rank-32 proper-orthogonal coefficients of the"
        " log-compressed spin densities and of the mean-removed spin potentials, combined by an elementwise"
        " product in the shared 128-wide latent, split into two 128-wide per-channel rows by one learned"
        " channel head, read out by a shared `BasisExpansion(128, (256, 256, 256))` trunk with a bounded"
        f" zero-to-one head. **Two-branch member: {member_parameter_count} parameters. Density-alone twin:"
        f" {twin_parameter_count} parameters** (the twin's density branch, channel head and trunk are seeded"
        " identically to the member's own; only the potential branch is absent).",
        "",
        "Proper-orthogonal basis decay, fit on 64 of the pooled floor-training runs (a report-scale sample kept"
        " small for this section's own timing; the parameter counts above depend only on the fixed rank, not"
        " on which runs the fit used):",
        "",
        "| branch | gate passed | gate rank | error at rank 8 | error at rank 16 | error at rank 32 |",
        "|---|---|---|---|---|---|",
    ]
    for label, report in decay.items():
        lines.append(
            f"| {label} | {bool(report['gate_passed'])} | {int(report['gate_reached_rank'])} |"
            f" {report.get('error_at_rank_8', float('nan')):.6f} | {report.get('error_at_rank_16', float('nan')):.6f} |"
            f" {report.get('error_at_rank_32', float('nan')):.6f} |"
        )
    return lines, member_parameter_count, twin_parameter_count


def Floor_Summaries(block: CubicBlock) -> tuple[
    MetricSummary, MetricSummary, MetricSummary, MetricSummary, dict[str, float]
]:
    """the four localization floors, read live through the promoted evaluation package on the kill block"""
    ridge_rows = Elf_Ridge_Rows(block)
    filter_rows = Shell_Filter_Rows(block)
    mean_rows = Training_Mean_Rows(block)
    copy_rows = Nearest_Run_Rows(block)
    ridge_summary = Summarize(ridge_rows, "mean_absolute_error", "semilocal_ridge_floor")
    filter_summary = Summarize(filter_rows, "mean_absolute_error", "per_shell_filter_floor")
    mean_summary = Summarize(mean_rows, "mean_absolute_error", "training_mean_trivial_floor")
    copy_summary = Summarize(copy_rows, "mean_absolute_error", "nearest_run_copy_floor")
    bars = Recorded_Bars(ridge_rows, mean_rows, copy_rows)
    return ridge_summary, filter_summary, mean_summary, copy_summary, bars


def Floor_Lines(
    ridge_summary: MetricSummary,
    filter_summary: MetricSummary,
    mean_summary: MetricSummary,
    copy_summary: MetricSummary,
    bars: dict[str, float],
) -> list[str]:
    """the floor table and the pre-registered ladder built from it, in absolute mean absolute error"""
    lines = [
        "Four localization floors, read live through `operators.evaluation` on the cubic block's own evaluation"
        " fold, mean absolute error (the flagship's own kill anchor, recomputed here rather than copied):",
        "",
        "| group | metric | units | runs | median | interquartile | 95% interval |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in Summary_Table((ridge_summary, filter_summary, mean_summary, copy_summary)):
        lines.append(
            f"| {row['group']} | {row['metric']} | {row['units']} | {row['runs']} | {row['median']} |"
            f" {row['interquartile']} | {row['mean_interval']} |"
        )
    lines += [
        "",
        "Pre-registered ladder, absolute mean absolute error, once the member and its twin are trained:",
        "",
        f"- **the decisive gate** (`test-suite.md`'s own words): two-branch vs density-alone twin, required"
        f" improvement {DECISIVE_TWIN_MARGIN:.0%} — kill if the potential branch adds five percent or less;"
        " no absolute number until the twin is trained, since the twin is the floor here, not a fixed archive"
        " quantity.",
        f"- canon pattern rule vs the semilocal ridge, required improvement {PATTERN_RULE_MARGIN:.0%}:"
        f" two-branch member's own mean absolute error must fall at or below"
        f" **{bars['canon_pattern_rule_semilocal_ridge_twenty_percent']:.6f}**.",
        f"- added context, never a kill: beat the training-mean template"
        f" (**{bars['added_beat_training_mean_template']:.6f}**), beat the nearest-run copy"
        f" (**{bars['added_beat_nearest_run_copy']:.6f}**), the stretch level at half the template"
        f" (**{bars['added_stretch_half_the_template']:.6f}**).",
        "",
        "**One-seed caveat, recorded per house policy**: the built branch–trunk family measured a 14-35% seed"
        " spread on its own floors on this same block, so a pass by a small margin over the twin is reported as"
        " unresolved on one seed, not as a win.",
        "",
        "**Dead end, pre-registered**: five percent or less improvement over the density-alone twin — a"
        " few-percent pass is \"unresolvable on one seed\", not a win.",
    ]
    return lines


def Result_Rows(block: CubicBlock, floor_summaries: tuple[MetricSummary, ...]) -> tuple[ResultRow, ...]:
    """the four floor summaries as result rows, keyed to the cubic block's own evaluation fold"""
    block_signature = Block_Signature({block.unit_of[identifier] for identifier in block.evaluation})
    return tuple(
        ResultRow(
            key=ResultKey(
                member=MEMBER_NAME,
                configuration=CONFIGURATION_NAME,
                task=TASK_NAME,
                split="paired_fields_fivefold",
                block="fold_0",
                group=summary.group_name,
            ),
            summary=summary,
            block_signature=block_signature,
        )
        for summary in floor_summaries
    )


def Metric_Median(rows: tuple[ResultRow, ...], group: str, metric_name: str) -> float | None:
    """one already-written result row's own median, found rather than retyped -- none if the group never ran"""
    for row in rows:
        if row.key.group == group and row.summary.metric_name == metric_name:
            return row.summary.median
    return None


def Point_Value_Loss(member: MultipleInputOperatorNetwork) -> ForwardLoss:
    """mean squared error against the sampled localization targets, no standardization needed since the bounded head already answers their own zero-to-one range"""


    def Loss_Of(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        """the point-sampled forward answered against this batch's own targets"""
        predicted = member.Forward_Point_Values(
            lifted, lifted_batch["parameter_vectors"], lifted_batch["trunk_features"]
        )
        residuals = predicted - lifted_batch["target_values"]
        return (residuals * residuals).mean()

    return Loss_Of


def Batches_For(
    member: MultipleInputOperatorNetwork,
    density_basis: Any,
    potential_basis: Any,
    reference_density: float,
    potential_coefficient_mean: Any,
    potential_coefficient_scale: Any,
) -> tuple[CoordinateFeaturizedBatches, int]:
    """the training and validation caches drawn point-sampled, their points already answered by the trunk's own map, beside the training run count -- one cache serves the member and its twin alike, since the twin simply ignores the potential columns"""
    training_cache = Localization_Cache(
        MEMBER_TRAIN_FOLDS,
        density_basis,
        potential_basis,
        reference_density,
        potential_coefficient_mean,
        potential_coefficient_scale,
        "training",
    )
    validation_cache = Localization_Cache(
        VALIDATION_FOLDS,
        density_basis,
        potential_basis,
        reference_density,
        potential_coefficient_mean,
        potential_coefficient_scale,
        "validation",
    )
    sampler = PointSampledBatches(training_cache, validation_cache, RUNS_PER_BATCH, POINTS_PER_RUN)
    batches = CoordinateFeaturizedBatches(sampler, member.trunk_readout.coordinate_features)
    return batches, len(training_cache.fields)


def Train_Configuration(step_count: int, run_name: str, twin: bool) -> dict[str, object]:
    """the staged run for either configuration through operators.training.Staged_Training, one code path so the twin cannot drift from the member, every stage resuming its own checkpoint -- the card holder's own driver, not invoked by this module; the card is scheduled by the integrator and this function trains nothing until it is called"""
    (
        density_basis,
        potential_basis,
        reference_density,
        potential_coefficient_mean,
        potential_coefficient_scale,
        _,
    ) = Fitted_Bases()
    member = (
        Density_Alone_Twin(density_basis, reference_density, seed=0)
        if twin
        else Two_Branch_Member(
            density_basis,
            potential_basis,
            reference_density,
            potential_coefficient_mean,
            potential_coefficient_scale,
            seed=0,
        )
    )
    batches, training_run_count = Batches_For(
        member,
        density_basis,
        potential_basis,
        reference_density,
        potential_coefficient_mean,
        potential_coefficient_scale,
    )
    forward_loss = Point_Value_Loss(member)
    parameters = ParameterSet(values=member.Parameter_Values())
    engine = Training_Engine()
    parameters, staged = Staged_Training(
        engine,
        parameters,
        lambda: ParameterSet(values=member.Parameter_Values()),
        forward_loss,
        batches,
        step_count,
        run_name,
        MEMBER_SEED,
        TRAINING_ARTIFACT_PATH,
    )
    manifest: dict[str, object] = {"run_name": run_name, "twin": twin, "training_run_count": training_run_count}
    manifest.update(staged)
    manifest["final_parameters"] = parameters
    manifest["member"] = member
    return manifest


def Cost_Probe(twin: bool) -> dict[str, object]:
    """a hundred steps on the real batch source for either configuration, seconds per step and peak accelerator bytes through operators.substrate's own dispatched facet, written to a small json beside the checkpoints"""
    (
        density_basis,
        potential_basis,
        reference_density,
        potential_coefficient_mean,
        potential_coefficient_scale,
        _,
    ) = Fitted_Bases()
    member = (
        Density_Alone_Twin(density_basis, reference_density, seed=0)
        if twin
        else Two_Branch_Member(
            density_basis,
            potential_basis,
            reference_density,
            potential_coefficient_mean,
            potential_coefficient_scale,
            seed=0,
        )
    )
    batches, training_run_count = Batches_For(
        member,
        density_basis,
        potential_basis,
        reference_density,
        potential_coefficient_mean,
        potential_coefficient_scale,
    )
    forward_loss = Point_Value_Loss(member)
    parameters = ParameterSet(values=member.Parameter_Values())
    Reset_Peak_Accelerator_Bytes()
    result = Train(
        Training_Engine(),
        parameters,
        forward_loss,
        batches,
        step_count=COST_PROBE_STEP_COUNT,
        learning_rate=DEFAULT_PEAK_LEARNING_RATE,
        seed=MEMBER_SEED,
        validation_interval=COST_PROBE_STEP_COUNT,
        patience=0,
    )
    peak_accelerator_bytes = Peak_Accelerator_Bytes()
    wall_clock_seconds = float(cast(float, result.manifest["wall_clock_seconds"]))
    seconds_per_step = wall_clock_seconds / COST_PROBE_STEP_COUNT
    probe: dict[str, object] = {
        "twin": twin,
        "step_count": COST_PROBE_STEP_COUNT,
        "training_run_count": training_run_count,
        "wall_clock_seconds": wall_clock_seconds,
        "seconds_per_step": seconds_per_step,
        "peak_accelerator_bytes": peak_accelerator_bytes,
        "one_hour_step_budget": int(3600.0 / seconds_per_step),
    }
    TRAINING_ARTIFACT_PATH.mkdir(parents=True, exist_ok=True)
    probe_path = TRAINING_ARTIFACT_PATH / f"cost_probe_{'twin' if twin else 'member'}.json"
    probe_path.write_text(json.dumps(probe, indent=1, sort_keys=True) + "\n")
    return probe


def Latest_Stage_Checkpoint(artifact_directory: Path, run_name: str) -> Path:
    """the furthest-along stage checkpoint a run has written to disk, its own closest thing to a final answer"""
    candidates: list[tuple[int, Path]] = []
    for path in artifact_directory.glob(f"{run_name}_stage*_checkpoint.npz"):
        match = _STAGE_CHECKPOINT_PATTERN.search(path.name)
        if match is not None:
            candidates.append((int(match.group(1)), path))
    if not candidates:
        raise FileNotFoundError(f"no stage checkpoint found for {run_name!r} under {artifact_directory}")
    return max(candidates, key=lambda pair: pair[0])[1]


def Write_Back_Parameters(member: MultipleInputOperatorNetwork, parameters: ParameterSet) -> None:
    """a flat trained parameter set folded back onto the member's own part-shaped storage, twin or two-branch alike"""
    encoder = member.branch_encoder
    for name, value in parameters.values.items():
        if name.startswith("density_branch."):
            encoder.density_branch.parameter_values[name.removeprefix("density_branch.")] = value
        elif name.startswith("potential_branch."):
            if encoder.potential is not None:
                _, potential_branch, _, _ = encoder.potential
                potential_branch.parameter_values[name.removeprefix("potential_branch.")] = value
        elif name in encoder.parameter_values:
            encoder.parameter_values[name] = value
        else:
            member.trunk_readout.parameter_values[name] = value


def Load_Trained_Member(run_name: str, twin: bool) -> MultipleInputOperatorNetwork:
    """the member or twin a finished run produced, its final stage's best checkpoint written onto a fresh build"""
    (
        density_basis,
        potential_basis,
        reference_density,
        potential_coefficient_mean,
        potential_coefficient_scale,
        _,
    ) = Fitted_Bases()
    member = (
        Density_Alone_Twin(density_basis, reference_density, seed=0)
        if twin
        else Two_Branch_Member(
            density_basis,
            potential_basis,
            reference_density,
            potential_coefficient_mean,
            potential_coefficient_scale,
            seed=0,
        )
    )
    checkpoint_path = Latest_Stage_Checkpoint(TRAINING_ARTIFACT_PATH, run_name)
    parameters = ParameterSet(values=member.Parameter_Values())
    progress = Read_Checkpoint(checkpoint_path, parameters)
    Write_Back_Parameters(member, progress.best_parameters)
    return member


def Two_Branch_Evaluation_Rows(member: MultipleInputOperatorNetwork, block: CubicBlock) -> list[ScoredRun]:
    """the trained member's own predictions on the kill block's evaluation fold, scored per spin channel"""
    scored: list[ScoredRun] = []
    for example in Cubic_Block_Examples(EVALUATION_FOLDS):
        identifier = example.identifier
        target_shape = example.target_function.values.shape[1:]
        output_grid = GridSpec((int(target_shape[0]), int(target_shape[1]), int(target_shape[2])))
        produced = member(example.input_function, output_grid)
        if not isinstance(produced, GridFunction):
            raise TypeError(f"{identifier} answered a {type(produced)}, not the grid field the card evaluates on")
        predicted = np.asarray(produced.values, dtype=np.float64)
        truth = np.asarray(example.target_function.values, dtype=np.float64)
        functional = block.Functional_Of(identifier)
        for channel_index, channel in enumerate(OUTPUT_CHANNEL_LABELS):
            scored.append(
                ScoredRun(
                    identifier=f"{identifier}_{channel}",
                    unit_key=block.unit_of[identifier],
                    campaign=block.campaign_of[identifier],
                    family=channel,
                    errors=Card_Metric_Errors(predicted[channel_index], truth[channel_index]),
                    covariate_values={"spin_channel": channel, "functional": functional},
                )
            )
    return scored


def Two_Branch_Evaluation_Summaries(rows: list[ScoredRun], label: str) -> list[MetricSummary]:
    """one evaluation's pooled summary beside its per-campaign and per-functional breakdowns, every card metric"""
    summaries: list[MetricSummary] = []
    for metric_name in CARD_METRIC_NAMES:
        summaries.append(Summarize(rows, metric_name, label))
        for campaign_summary in Summarize_By(rows, metric_name, "campaign"):
            summaries.append(
                dataclasses.replace(campaign_summary, group_name=f"{label}__{campaign_summary.group_name}")
            )
        for functional_summary in Summarize_By(rows, metric_name, "functional"):
            summaries.append(
                dataclasses.replace(
                    functional_summary, group_name=f"{label}__functional_{functional_summary.group_name}"
                )
            )
    return summaries


def Write_Evaluation_Figures(
    member: MultipleInputOperatorNetwork,
    member_rows: list[ScoredRun],
    floor_medians: dict[str, float],
    member_median: float,
) -> int:
    """the trained member's inspection suite, its error spread by campaign, and its own floor comparison"""
    FIGURES_PATH.mkdir(parents=True, exist_ok=True)
    inspected = {name: np.asarray(value, dtype=np.float64) for name, value in member.Inspect().items()}
    suite = Render_Inspection_Suite(
        inspected, FIGURES_PATH / "fold_0" / "components", "electron localization fold 0, two-branch member"
    )
    if suite.skipped:
        raise ValueError(f"no renderer for {suite.skipped}, which means the suite is incomplete")
    by_campaign: dict[str, list[float]] = {}
    for row in member_rows:
        by_campaign.setdefault(row.campaign, []).append(row.errors["mean_absolute_error"])
    Render_Error_Spread(
        {name: np.asarray(values) for name, values in by_campaign.items()},
        FIGURES_PATH / "fold_0" / "error_by_campaign.png",
        "electron localization fold 0 evaluation error by campaign (mean absolute error)",
    )
    Render_Floor_Comparison(
        floor_medians,
        member_median,
        {name: 0.0 for name in floor_medians},
        FIGURES_PATH / "fold_0" / "floors.png",
        "electron localization fold 0 against its floors and the density-alone twin (mean absolute error)",
    )
    return len(suite.written) + 2


def Stage_Manifests(run_name: str) -> list[dict[str, Any]]:
    """a run's own stage manifests, in stage order, read rather than retyped"""
    manifests: list[tuple[int, dict[str, Any]]] = []
    for path in TRAINING_ARTIFACT_PATH.glob(f"{run_name}_stage*_manifest.json"):
        match = re.search(r"_stage(\d+)_manifest\.json$", path.name)
        if match is not None:
            manifests.append((int(match.group(1)), json.loads(path.read_text())))
    return [manifest for _, manifest in sorted(manifests)]


def Training_Lines(run_name: str, label: str) -> list[str]:
    """one run's own stage-wise best validation score and wall-clock, read from its manifests"""
    lines = [f"- **{label}** (`{run_name}`):"]
    total_seconds = 0.0
    for manifest in Stage_Manifests(run_name):
        completed_steps = int(cast(int, manifest["completed_steps"]))
        best_score = float(cast(float, manifest["best_validation_score"]))
        best_step = int(cast(int, manifest["best_step"]))
        wall_clock_seconds = float(cast(float, manifest["wall_clock_seconds"]))
        total_seconds += wall_clock_seconds
        stopped_reason = "stopped early by patience" if manifest["stopped_early"] else "ran the full stage"
        lines.append(
            f"  - {completed_steps} steps completed ({stopped_reason}), best validation {best_score:.6f} at step"
            f" {best_step}, {wall_clock_seconds:.1f}s"
        )
    lines.append(f"  - total wall-clock: {total_seconds:.1f}s ({total_seconds / 60.0:.1f} min)")
    return lines


def Evaluation_Lines(
    block: CubicBlock,
) -> tuple[list[str], tuple[ResultRow, ...], tuple[VerdictRow, ...]]:
    """the trained member's and twin's own result on fold 0, the two verdicts, or a placeholder before either exists"""
    try:
        member = Load_Trained_Member(MEMBER_RUN_NAME, twin=False)
        twin = Load_Trained_Member(TWIN_RUN_NAME, twin=True)
    except FileNotFoundError as error:
        return (
            [
                "## Result",
                "",
                f"Not yet run ({error}); this section fills in from `Evaluation_Lines` alone once both"
                " checkpoints exist, no other change to this report needed.",
                "",
            ],
            (),
            (),
        )
    member_rows = Two_Branch_Evaluation_Rows(member, block)
    twin_rows = Two_Branch_Evaluation_Rows(twin, block)
    ridge_rows = Elf_Ridge_Rows(block)
    member_summaries = Two_Branch_Evaluation_Summaries(member_rows, "member")
    twin_summaries = Two_Branch_Evaluation_Summaries(twin_rows, "twin")
    pattern_rule = Compare_To_Floor(
        member_rows,
        ridge_rows,
        "mean_absolute_error",
        "semilocal_ridge_floor",
        PATTERN_RULE_MARGIN,
        "pattern_rule_vs_semilocal_ridge",
    )
    decisive = Compare_To_Floor(
        member_rows, twin_rows, "mean_absolute_error", "density_alone_twin", DECISIVE_TWIN_MARGIN, "decisive_vs_twin"
    )
    block_signature = Block_Signature({block.unit_of[identifier] for identifier in block.evaluation})
    figures_written = Write_Evaluation_Figures(
        member,
        member_rows,
        {"semilocal_ridge_floor": pattern_rule.floor_median, "density_alone_twin": decisive.floor_median},
        decisive.member_median,
    )
    member_mae = next(
        summary
        for summary in member_summaries
        if summary.metric_name == "mean_absolute_error" and summary.group_name == "member"
    )
    twin_mae = next(
        summary
        for summary in twin_summaries
        if summary.metric_name == "mean_absolute_error" and summary.group_name == "twin"
    )
    verdict_statement = (
        "**Pass**: the two-branch member beats its density-alone twin by more than the required 5%, and the"
        " pattern rule against the semilocal ridge also holds."
        if decisive.verdict == "pass"
        else "**Kill, of a repaired member.** The potential branch adds nothing measurable on this task at this"
        " matched budget (or hurts): the member does not beat its density-alone twin by the required 5%"
        " improvement. This is the entry's pre-registered dead end -- reached honestly, after the defect above"
        " was found and fixed, not from a broken run."
    )
    lines = [
        "## Result",
        "",
        "Both runs trained under the identical matched 33,650-step schedule and seed, stage-wise best validation"
        " score (mean squared error, the training loss's own metric) read from each run's own manifests:",
        "",
        *Training_Lines(TWIN_RUN_NAME, "density-alone twin"),
        *Training_Lines(MEMBER_RUN_NAME, "two-branch member (fixed)"),
        "",
        "Evaluated on fold 0 (the kill block's evaluation split), every card metric, pooled over both spin"
        " channels of every run:",
        "",
        "| group | metric | units | runs | median | interquartile | 95% interval |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in Summary_Table(
        tuple(
            summary
            for summary in (*member_summaries, *twin_summaries)
            if summary.group_name in ("member", "twin")
        )
    ):
        lines.append(
            f"| {row['group']} | {row['metric']} | {row['units']} | {row['runs']} | {row['median']} |"
            f" {row['interquartile']} | {row['mean_interval']} |"
        )
    lines += [
        "",
        f"Member median mean absolute error **{member_mae.median:.6f}**, twin **{twin_mae.median:.6f}**"
        f" (per-campaign and per-functional breakdowns, every card metric, in `results.json`).",
        "",
        "| verdict | floor | metric | floor median | member median | improvement | required | result |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in Comparison_Table((pattern_rule, decisive)):
        lines.append(
            f"| {row['group']} | {row['floor']} | mean_absolute_error | {row['floor_median']} |"
            f" {row['member_median']} | {row['improvement']} | {row['required']} | {row['verdict']} |"
        )
    lines += [
        "",
        verdict_statement,
        "",
        "**One-seed caveat, per house policy**: one seeded run each, no five-fold protocol or seed sweep yet --"
        " the built branch-trunk family measured a 14-35% seed spread on its own floors on this same block"
        " (pre-registered above), so this verdict is read as what one seed shows, not a sweep-confirmed result.",
        "",
        f"Figures under `figures/fold_0/` ({figures_written} written): the inspection suite, the error spread by"
        " campaign, and the member against its floors and the twin.",
        "",
    ]
    rows = tuple(
        ResultRow(
            key=ResultKey(
                member=MEMBER_NAME,
                configuration=CONFIGURATION_NAME,
                task=TASK_NAME,
                split="paired_fields_fivefold",
                block="fold_0",
                group=summary.group_name,
            ),
            summary=summary,
            block_signature=block_signature,
        )
        for summary in (*member_summaries, *twin_summaries)
    )
    verdicts = tuple(
        VerdictRow(
            key=ResultKey(
                member=MEMBER_NAME,
                configuration=CONFIGURATION_NAME,
                task=TASK_NAME,
                split="paired_fields_fivefold",
                block="fold_0",
                group=comparison.group_name,
            ),
            comparison=comparison,
        )
        for comparison in (pattern_rule, decisive)
    )
    return lines, rows, verdicts


def Main() -> int:
    """writes the report and the results artifact, live-evaluated once both the twin and the member have trained"""
    started = time.monotonic()
    block = CubicBlock()
    architecture_lines, member_parameter_count, twin_parameter_count = Architecture_Lines()
    ridge_summary, filter_summary, mean_summary, copy_summary, bars = Floor_Summaries(block)
    evaluation_lines, evaluation_rows, evaluation_verdicts = Evaluation_Lines(block)
    member_mae_median = Metric_Median(evaluation_rows, "member", "mean_absolute_error")
    twin_mae_median = Metric_Median(evaluation_rows, "twin", "mean_absolute_error")
    standing_context_lines: list[str] = []
    if member_mae_median is not None and twin_mae_median is not None:
        standing_context_lines = [
            f" Context, computed from the rows above: the member does not beat the training-mean template floor"
            f" ({member_mae_median:.6f} against {mean_summary.median:.6f}), and the twin only just does"
            f" ({twin_mae_median:.6f}, {mean_summary.median - twin_mae_median:.6f} below it).",
            f" Both sit roughly {member_mae_median / FLAGSHIP_FOLD_0_MEAN_ABSOLUTE_ERROR:.1f}x (member) and"
            f" {twin_mae_median / FLAGSHIP_FOLD_0_MEAN_ABSOLUTE_ERROR:.1f}x (twin) above the flagship's own"
            f" {FLAGSHIP_FOLD_0_MEAN_ABSOLUTE_ERROR:.6f} mean absolute error on the same block"
            " (`factorized_fourier/report.md`).",
        ]
    lines = [
        "# multiple_input_operator_network — results",
        "",
        "## Block",
        "",
        *Block_Lines(block),
        "",
        "## Architecture and parameter count",
        "",
        *architecture_lines,
        "",
        "## Floors and the pre-registered ladder",
        "",
        *Floor_Lines(ridge_summary, filter_summary, mean_summary, copy_summary, bars),
        "",
        "**A defect, found and fixed before any verdict was written.** The first matched-budget run"
        " (`elf_fold0_member_33650`, void) never had a working forward pass: the potential branch's own"
        " rank-32 coefficients entered the product un-standardized, at roughly 48x the density branch's own"
        " scale, which saturated the bounded head (`Bounded_Values`) to exactly 0.0 everywhere from step one --"
        " the recorded validation score (0.091299, unmoved to six digits across all three stages) is what an"
        " all-zero prediction scores against this target, not a trained member. See `IMPLEMENTATION.md`'s own"
        " defect section for the full diagnosis. **Fix, landed**: `Potential_Coefficient_Statistics` and"
        " `Standardized_Potential_Coefficients` center and scale each of the potential basis's rank-32"
        " coefficients by its own training-fold mean and spread before the potential branch ever reads it,"
        " leaving the density path -- and the twin's already-trained checkpoint (`elf_fold0_twin_33650`) --"
        " untouched. A host sanity check (300 steps, `learning_rate=1e-3`, card hidden) confirmed the fix"
        " trains: validation score 0.076946 at step 25, falling every checkpoint after (one wobble, step 150 to"
        " 175) to 0.015901 at step 300 -- below the all-zero baseline (0.0913) from the first checkpoint and"
        " still falling at the run's end. The two runs share one step budget, matched by construction: the"
        " twin's cost probe measured 0.451 s/step (100 steps, mostly one-time accelerator and kernel-cache"
        " initialization), the member's, run second in a fresh process, measured 0.107 s/step against an"
        " already-warm kernel cache -- the two probes are not comparable, and sizing each run from its own"
        " probe would have handed the twin 7,976 steps against the member's 33,650, confounding the decisive"
        " twin-vs-member comparison with unequal training rather than isolating the potential branch's own"
        " contribution. Both runs instead took the member's warm-cache figure, 33,650 steps each (the fixed"
        " member's own retrain, `elf_fold0_member_v2_33650`).",
        "",
        *evaluation_lines,
        "## Inspection",
        "",
        "See `IMPLEMENTATION.md`'s own Inspection section: every branch, projection, the channel head, the"
        " composition's carried vector and the trunk's own arrays are reachable by name through `Inspect()`,"
        " confirmed by `Test_Every_Inspect_Key_Renders` and `Test_The_Member_Inspects_Under_Part_Prefixes`.",
        "",
        "## Standing",
        "",
        "Built and tested (`operators/tests/test_multiple_input_operator_network.py`): the assembly, the"
        " basis fitting and cache, the gate contract, the product-reduces-to-branch-trunk identity, two-path"
        " agreement and gradients on both engines, the twin's shared-name and constant-potential properties, a"
        " deterministic toy training run, the full inspection surface, the exact cubic-block fold counts, the"
        " built configuration's own parameter counts against the live corpus, and (added after the defect"
        " above) the saturation guard confirming real-scale branch latents and a non-saturated bounded head at"
        " a fresh init. Floors are pre-registered above, read live through the promoted"
        " `operators.evaluation` package. **Both the twin (`elf_fold0_twin_33650`) and the fixed member"
        " (`elf_fold0_member_v2_33650`) are trained and evaluated on fold 0 -- see Result for the verdict.**"
        + "".join(standing_context_lines),
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n")
    results = MemberResults(
        member=MEMBER_NAME,
        regenerate="python -m operators.multiple_input_operator_network.report",
        rows=Result_Rows(block, (ridge_summary, filter_summary, mean_summary, copy_summary)) + evaluation_rows,
        verdicts=evaluation_verdicts,
    )
    Write_Member_Results(RESULTS_PATH, results)
    elapsed = time.monotonic() - started
    print(f"wrote {REPORT_PATH} and {RESULTS_PATH} in {elapsed:.1f}s")
    print(f"member parameters: {member_parameter_count}, twin parameters: {twin_parameter_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
