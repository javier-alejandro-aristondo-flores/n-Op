"""the two-branch member measured against its pre-registered floors, before a step of training runs"""

import json
import time
from pathlib import Path
from typing import Any, cast

from operators.data import POOL_ROOT, STORE_NAME
from operators.evaluation import (
    Block_Signature,
    CubicBlock,
    Elf_Ridge_Rows,
    MemberResults,
    MetricSummary,
    Nearest_Run_Rows,
    Recorded_Bars,
    ResultKey,
    ResultRow,
    Shell_Filter_Rows,
    Summarize,
    Summary_Table,
    Training_Mean_Rows,
    Write_Member_Results,
)
from operators.multiple_input_operator_network import Density_Alone_Twin, MultipleInputOperatorNetwork, Two_Branch_Member
from operators.multiple_input_operator_network.cache import (
    BASIS_RANK,
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
    density_basis, potential_basis, reference_density, decay = Fitted_Bases(limit=64)
    member = Two_Branch_Member(density_basis, potential_basis, reference_density, seed=0)
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
) -> tuple[CoordinateFeaturizedBatches, int]:
    """the training and validation caches drawn point-sampled, their points already answered by the trunk's own map, beside the training run count -- one cache serves the member and its twin alike, since the twin simply ignores the potential columns"""
    training_cache = Localization_Cache(
        MEMBER_TRAIN_FOLDS, density_basis, potential_basis, reference_density, "training"
    )
    validation_cache = Localization_Cache(
        VALIDATION_FOLDS, density_basis, potential_basis, reference_density, "validation"
    )
    sampler = PointSampledBatches(training_cache, validation_cache, RUNS_PER_BATCH, POINTS_PER_RUN)
    batches = CoordinateFeaturizedBatches(sampler, member.trunk_readout.coordinate_features)
    return batches, len(training_cache.fields)


def Train_Configuration(step_count: int, run_name: str, twin: bool) -> dict[str, object]:
    """the staged run for either configuration through operators.training.Staged_Training, one code path so the twin cannot drift from the member, every stage resuming its own checkpoint -- the card holder's own driver, not invoked by this module; the card is scheduled by the integrator and this function trains nothing until it is called"""
    density_basis, potential_basis, reference_density, _ = Fitted_Bases()
    member = (
        Density_Alone_Twin(density_basis, reference_density, seed=0)
        if twin
        else Two_Branch_Member(density_basis, potential_basis, reference_density, seed=0)
    )
    batches, training_run_count = Batches_For(member, density_basis, potential_basis, reference_density)
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
    density_basis, potential_basis, reference_density, _ = Fitted_Bases()
    member = (
        Density_Alone_Twin(density_basis, reference_density, seed=0)
        if twin
        else Two_Branch_Member(density_basis, potential_basis, reference_density, seed=0)
    )
    batches, training_run_count = Batches_For(member, density_basis, potential_basis, reference_density)
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


def Main() -> int:
    """writes the pre-registration report and the results artifact -- no training has run yet"""
    started = time.monotonic()
    block = CubicBlock()
    architecture_lines, member_parameter_count, twin_parameter_count = Architecture_Lines()
    ridge_summary, filter_summary, mean_summary, copy_summary, bars = Floor_Summaries(block)
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
        "## Result",
        "",
        "Not yet run. Training is scheduled by the integrator on the shared card: the density-alone twin first"
        " (one hour), then the two-branch member (one hour), both under the flagship's staged protocol on the"
        " member_train fold, validated on the validation fold, evaluated on the evaluation fold above.",
        "",
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
        " deterministic toy training run, the full inspection surface, the exact cubic-block fold counts, and"
        " the built configuration's own parameter counts against the live corpus. Floors are pre-registered"
        " above, read live through the promoted `operators.evaluation` package. Not yet run: the twin's and the"
        " member's own training, scheduled on the card.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n")
    results = MemberResults(
        member=MEMBER_NAME,
        regenerate="python -m operators.multiple_input_operator_network.report",
        rows=Result_Rows(block, (ridge_summary, filter_summary, mean_summary, copy_summary)),
        verdicts=(),
    )
    Write_Member_Results(RESULTS_PATH, results)
    elapsed = time.monotonic() - started
    print(f"wrote {REPORT_PATH} and {RESULTS_PATH} in {elapsed:.1f}s")
    print(f"member parameters: {member_parameter_count}, twin parameters: {twin_parameter_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
