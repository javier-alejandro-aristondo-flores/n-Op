"""the member measured against its pre-registered floors, and the staged training driver the card runs it through"""

import re
import time
from pathlib import Path
from typing import Any, cast

import numpy as np

from operators.codomain_attention import CodomainAttention, HEAD_COUNT, HIDDEN_CHANNELS, KEPT_MODE, LAYER_COUNT
from operators.codomain_attention.channels import CHANNEL_VOCABULARY, ChannelStatistics, COARSE_SHAPE
from operators.codomain_attention.loader import (
    Channel_Statistics_From_Examples,
    CompletionBatches,
    CompletionExample,
    Loaded_Completion_Examples,
)
from operators.codomain_attention.masking import MaskPatternName
from operators.codomain_attention.splits import CompletionBlock
from operators.compositions import ExplicitStack
from operators.data import POOL_ROOT, STORE_NAME
from operators.evaluation import (
    Block_Signature,
    CubicBlock,
    Elf_Ridge_Rows,
    MemberResults,
    MetricSummary,
    Potential_Floor_Rows,
    ResultKey,
    ResultRow,
    Summarize,
    Write_Member_Results,
)
from operators.inspection.plots import Render_Inspection_Suite, Render_Matrix, RenderedSuite
from operators.substrate import ParameterSet
from operators.training import Read_Checkpoint, Staged_Training, Train, Training_Engine, TrainingProgress

REPORT_PATH = Path(__file__).parent / "report.md"
FIGURES_PATH = Path(__file__).parent / "figures"
# inspection arrays are fields, and a field never leaves the pool -- only the drawing does
ARRAY_CACHE_PATH = POOL_ROOT / STORE_NAME / "_figures" / "codomain_attention"
# checkpoints are scratch, not a corpus artifact, but they still hold no volumetric data either way
TRAINING_ARTIFACT_PATH = POOL_ROOT / STORE_NAME / "_training" / "codomain_attention"

PRETRAIN_SEED = 20260916

PEAK_LEARNING_RATE = 1e-3
STAGE_FRACTIONS = (0.3, 0.3, 0.4)
VALIDATION_INTERVAL = 100
FINAL_STAGE_PATIENCE = 15
STEP_COST_PROBE_STEPS = 300
PRETRAIN_HOUR_CAP = 6.0

# the dedicated competitor's own measured number (factorized_fourier/report.md, fold 0 of the cubic block), a
# recorded reference cited by its source rather than recomputed here -- this member never trains that member
FLAGSHIP_LOCALIZATION_MAE_FOLD0 = 0.002170
FLAGSHIP_LOCALIZATION_HOURS = 3.94
# the flagship's own dedicated potential run is queued on the card ahead of this member's; its number is pending
FLAGSHIP_POTENTIAL_MEAN_REMOVED_RELATIVE_L2_FOLD0: float | None = None

K1_ZERO_SHOT_REQUIRED_IMPROVEMENT = -1.0
K1_FINE_TUNE_REQUIRED_IMPROVEMENT = -0.25
K2_ELF_REQUIRED_IMPROVEMENT = 0.20
K2_POTENTIAL_REQUIRED_IMPROVEMENT = 0.30

# the card's own measured usable budget and the flagship's own measured peak at batch one (execution log, both
# recorded references), pre-registered here as the ceiling the probe stops at rather than measured by this member
CARD_USABLE_MEMORY_GIGABYTES = 5.61
FLAGSHIP_PEAK_MEMORY_GIGABYTES_AT_BATCH_ONE = 3.6


def Completion_Loss(member: CodomainAttention) -> Any:
    """masked mean squared error over every example a batch carries, looped since the lifted path takes one at a time"""

    def Loss(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        example_count = lifted_batch["full_transformed_stack"].shape[0]
        total = 0.0
        for example_index in range(example_count):
            full_stack = lifted_batch["full_transformed_stack"][example_index]
            visible_mask = lifted_batch["visible_mask"][example_index]
            condition_vector = lifted_batch["condition_vector"][example_index]
            reconstruction = member.Forward_Tokens(lifted, full_stack, visible_mask, condition_vector)
            hidden_mask = 1.0 - visible_mask
            broadcast_hidden = hidden_mask[:, None, None, None]
            difference = (reconstruction - full_stack) * broadcast_hidden
            voxel_count_per_token = float(full_stack.shape[1] * full_stack.shape[2] * full_stack.shape[3])
            total = total + (difference * difference).sum() / (hidden_mask.sum() * voxel_count_per_token)
        return total / example_count

    return Loss


def Elf_Semilocal_Floor_Summary(block: CubicBlock) -> MetricSummary:
    """the pointwise semilocal ridge floor's own summary on the cubic block's kill fold, from the promoted rows"""
    return Summarize(Elf_Ridge_Rows(block), "mean_absolute_error", "semilocal_ridge_floor")


def Potential_Semilocal_Floor_Summary(block: CubicBlock) -> MetricSummary:
    """the hartree-plus-semilocal-xc ridge floor's own summary on the cubic block's kill fold, from the promoted rows"""
    rows = Potential_Floor_Rows(block)["hartree_plus_semilocal_xc_ridge"]
    return Summarize(rows, "mean_removed_relative_l2", "hartree_plus_semilocal_xc_ridge")


def Pre_Registered_Bars(
    elf_floor: MetricSummary, potential_floor: MetricSummary
) -> dict[str, dict[str, float | str | None]]:
    """every kill and pattern-rule bar this policy names, in absolute numbers, before any step of training runs"""
    return {
        "k1_localization_zero_shot": {
            "floor_name": "factorized_fourier_dedicated_localization",
            "floor_value": FLAGSHIP_LOCALIZATION_MAE_FOLD0,
            "metric": "mean_absolute_error",
            "required_improvement": K1_ZERO_SHOT_REQUIRED_IMPROVEMENT,
            "absolute_bar": FLAGSHIP_LOCALIZATION_MAE_FOLD0 * 2.0,
            "reads": "reject if the zero-shot completion error exceeds this on two or more pairwise tasks",
        },
        "k1_localization_fine_tuned": {
            "floor_name": "factorized_fourier_dedicated_localization",
            "floor_value": FLAGSHIP_LOCALIZATION_MAE_FOLD0,
            "metric": "mean_absolute_error",
            "required_improvement": K1_FINE_TUNE_REQUIRED_IMPROVEMENT,
            "absolute_bar": FLAGSHIP_LOCALIZATION_MAE_FOLD0 * 1.25,
            "reads": "reject only if still worse than this after the pairwise fine-tune",
        },
        "k1_potential_zero_shot": {
            "floor_name": "factorized_fourier_dedicated_potential",
            "floor_value": FLAGSHIP_POTENTIAL_MEAN_REMOVED_RELATIVE_L2_FOLD0,
            "metric": "mean_removed_relative_l2",
            "required_improvement": K1_ZERO_SHOT_REQUIRED_IMPROVEMENT,
            "absolute_bar": None,
            "reads": "pending: the dedicated potential run is queued on the card ahead of this member's",
        },
        "k2_localization_semilocal_floor": {
            "floor_name": "semilocal_ridge_floor",
            "floor_value": elf_floor.median,
            "metric": "mean_absolute_error",
            "required_improvement": K2_ELF_REQUIRED_IMPROVEMENT,
            "absolute_bar": elf_floor.median * (1.0 - K2_ELF_REQUIRED_IMPROVEMENT),
            "reads": "the completion flagship deflates if zero-shot elf lands within twenty percent of this",
        },
        "k2_potential_spectral_poisson_semilocal_xc": {
            "floor_name": "hartree_plus_semilocal_xc_ridge",
            "floor_value": potential_floor.median,
            "metric": "mean_removed_relative_l2",
            "required_improvement": K2_POTENTIAL_REQUIRED_IMPROVEMENT,
            "absolute_bar": potential_floor.median * (1.0 - K2_POTENTIAL_REQUIRED_IMPROVEMENT),
            "reads": "the v-read adds nothing over textbook physics if it does not clear this",
        },
    }


def Loaded_Population(
    block: CompletionBlock, training_identifiers: list[str], statistics: ChannelStatistics | None = None
) -> tuple[list[CompletionExample], list[CompletionExample], ChannelStatistics]:
    """one named training population against the fixed validation fold, statistics fixed from it unless handed one"""
    training_examples = Loaded_Completion_Examples(training_identifiers, block, block.pool_root)
    validation_examples = Loaded_Completion_Examples(block.validation, block, block.pool_root)
    resolved_statistics = statistics if statistics is not None else Channel_Statistics_From_Examples(training_examples)
    return training_examples, validation_examples, resolved_statistics


def Loaded_Training_Population(
    block: CompletionBlock,
) -> tuple[list[CompletionExample], list[CompletionExample], ChannelStatistics]:
    """the whole pretrain population, the validation population and the channel statistics fixed from the pretrain population"""
    return Loaded_Population(block, block.member_train)


def Fresh_Completion_Member(statistics: ChannelStatistics, seed: int = PRETRAIN_SEED) -> CodomainAttention:
    """the member built at its pre-registered minimal configuration, freshly initialized"""
    return CodomainAttention(
        statistics,
        hidden_channels=HIDDEN_CHANNELS,
        kept_modes=(KEPT_MODE, KEPT_MODE, KEPT_MODE),
        head_count=HEAD_COUNT,
        layer_count=LAYER_COUNT,
        seed=seed,
    )


def Step_Cost_Probe(
    member: CodomainAttention, batches: CompletionBatches, step_count: int = STEP_COST_PROBE_STEPS
) -> dict[str, float]:
    """wall-clock seconds per step over a short, uncheckpointed run, reported rather than trained from"""
    forward_loss = Completion_Loss(member)
    parameters = ParameterSet(values=member.Parameter_Values())
    engine = Training_Engine()
    started = time.perf_counter()
    result = Train(
        engine=engine,
        parameters=parameters,
        forward_loss=forward_loss,
        batch_source=batches,
        step_count=step_count,
        learning_rate=PEAK_LEARNING_RATE,
        seed=PRETRAIN_SEED,
        validation_interval=step_count,
        patience=0,
    )
    elapsed = time.perf_counter() - started
    return {
        "step_count": float(step_count),
        "elapsed_seconds": elapsed,
        "seconds_per_step": elapsed / step_count,
        "final_loss": float(result.loss_curve[-1]) if result.loss_curve.size else float("nan"),
    }


def Train_Completion_Member(
    step_count: int,
    run_name: str,
    restrict_to_pattern: MaskPatternName | None = None,
    seed: int = PRETRAIN_SEED,
    starting_parameters: ParameterSet | None = None,
    training_identifiers: list[str] | None = None,
    statistics_override: ChannelStatistics | None = None,
) -> dict[str, object]:
    """the staged schedule over a fresh member, or over a fine-tune's own starting weights and population when handed one"""
    block = CompletionBlock()
    chosen_identifiers = training_identifiers if training_identifiers is not None else block.member_train
    training_examples, validation_examples, statistics = Loaded_Population(block, chosen_identifiers, statistics_override)
    batches = CompletionBatches(training_examples, validation_examples, statistics, fixed_pattern=restrict_to_pattern)

    member = Fresh_Completion_Member(statistics, seed=seed)
    forward_loss = Completion_Loss(member)
    parameters = starting_parameters if starting_parameters is not None else ParameterSet(values=member.Parameter_Values())
    engine = Training_Engine()

    parameters, staged = Staged_Training(
        engine, parameters, lambda: ParameterSet(values=member.Parameter_Values()), forward_loss, batches,
        step_count, run_name, seed, TRAINING_ARTIFACT_PATH, stage_fractions=STAGE_FRACTIONS,
        peak_learning_rate=PEAK_LEARNING_RATE, validation_interval=VALIDATION_INTERVAL,
        final_stage_patience=FINAL_STAGE_PATIENCE,
    )
    manifest: dict[str, object] = {
        "run_name": run_name,
        "restricted_to_pattern": restrict_to_pattern,
        "training_example_count": len(training_examples),
        "validation_example_count": len(validation_examples),
        "reference_density": statistics.reference_density,
        "magnetization_scale": statistics.magnetization_scale,
        "potential_scale": statistics.potential_scale,
    }
    manifest.update(staged)
    Write_Back_Parameters(member, parameters)
    manifest["final_parameters"] = parameters
    manifest["member"] = member
    return manifest


def Write_Back_Parameters(member: CodomainAttention, parameters: ParameterSet) -> None:
    """a flat trained parameter set folded back onto the member's own part-shaped storage, any layer count"""
    for name, value in parameters.values.items():
        if name.startswith("layer_"):
            layer_token, part_name, bare_name = name.split(".", 2)
            layer = member.attention_stack.layers[int(layer_token.removeprefix("layer_"))]
            part = layer.kernel if part_name == "kernel" else layer.local_linear
            part.parameter_values[bare_name] = value
        elif name in member.channel_encoder.parameter_values:
            member.channel_encoder.parameter_values[name] = value
        elif name in member.token_readout.parameter_values:
            member.token_readout.parameter_values[name] = value
        elif name in member.parameter_values:
            member.parameter_values[name] = value
        else:
            raise KeyError(f"{name} matches no part of this member's own parameter storage")


_STAGE_CHECKPOINT_PATTERN = re.compile(r"_stage(\d+)_checkpoint\.npz$")


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


def Load_Trained_Completion_Member(
    checkpoint_path: Path, statistics: ChannelStatistics, seed: int = PRETRAIN_SEED
) -> tuple[CodomainAttention, TrainingProgress]:
    """the member a finished or in-progress run produced, its best checkpoint parameters written back onto it"""
    member = Fresh_Completion_Member(statistics, seed=seed)
    template = ParameterSet(values=member.Parameter_Values())
    progress = Read_Checkpoint(checkpoint_path, template)
    Write_Back_Parameters(member, progress.best_parameters)
    return member, progress


def Attention_Map_Figures(
    member: CodomainAttention, directory: Path, present_labels: tuple[str, ...]
) -> tuple[Path, ...]:
    """every layer's own attention map, one panel per head, axes labeled by the field name at each token position"""
    if not isinstance(member.composition, ExplicitStack):
        return ()
    directory.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    order_label = ", ".join(f"{position}={label}" for position, label in enumerate(present_labels))
    for layer_index, layer in enumerate(member.composition.layers):
        scores = layer.kernel.Inspect().get("last_attention_scores")
        if scores is None:
            continue
        scores_array = np.asarray(scores, dtype=np.float64)
        for head_index in range(scores_array.shape[0]):
            path = directory / f"layer_{layer_index}_head_{head_index}_attention.png"
            written.append(
                Render_Matrix(
                    scores_array[head_index],
                    path,
                    f"codomain attention layer {layer_index} head {head_index}, tokens [{order_label}]",
                )
            )
    return tuple(written)


def Write_Inspection_Suite(member: CodomainAttention, directory: Path) -> RenderedSuite:
    """the member's whole inspection surface, cached and rendered from arrays alone"""
    inspected = {name: np.asarray(value, dtype=np.float64) for name, value in member.Inspect().items()}
    directory.mkdir(parents=True, exist_ok=True)
    np.savez(directory / "inspection.npz", **cast(dict[str, Any], inspected))
    with np.load(directory / "inspection.npz") as archive:
        restored = {name: np.asarray(archive[name], dtype=np.float64) for name in archive.files}
    return Render_Inspection_Suite(restored, directory / "components", "codomain attention completion")


def Pre_Training_Report_Lines(
    parameter_count: int, master_weight_megabytes: float, bars: dict[str, dict[str, float | str | None]]
) -> list[str]:
    """the report's own pre-registration section: architecture, floors and every bar, before a step of training runs"""
    lines = [
        "# codomain_attention -- results",
        "",
        "Standing: **pre-training**. The member, the split, the loader, the masking scheme, the token-shared",
        "readout and the per-token conservation heads are built. Training has not started -- the card is",
        "scheduled by the integrator. This section pre-registers every floor and bar in absolute numbers, per",
        "house policy, before any step of training runs. The dedicated localization competitor",
        f"(`factorized_fourier`) trained in {FLAGSHIP_LOCALIZATION_HOURS} hours to"
        f" {FLAGSHIP_LOCALIZATION_MAE_FOLD0} mean absolute error on fold 0 of the same cubic block; its",
        "dedicated potential run is queued ahead of this member's own card slot.",
        "",
        "## Configuration",
        "",
        f"- hidden channels per token: {HIDDEN_CHANNELS}",
        f"- kept modes per axis: {KEPT_MODE} (mode extent {2 * KEPT_MODE + 1})",
        f"- attention heads: {HEAD_COUNT}",
        f"- explicit-stack layers: {LAYER_COUNT}",
        f"- processing grid: {COARSE_SHAPE}",
        f"- channel vocabulary: {', '.join(CHANNEL_VOCABULARY)}",
        f"- parameters: {parameter_count:,} ({master_weight_megabytes:.1f} MB at double precision,"
        f" {master_weight_megabytes / 2.0:.1f} MB at the single-precision working width)",
        f"- peak memory: not yet measured; pre-registered ceiling for the 300-step probe is"
        f" {CARD_USABLE_MEMORY_GIGABYTES:.2f} GB (the card's own measured usable budget), the probe stopping",
        f"  on exceedance -- for reference the flagship's explicit configuration held"
        f" {FLAGSHIP_PEAK_MEMORY_GIGABYTES_AT_BATCH_ONE:.1f} GB at batch 1",
        "",
        "## Floors and bars (fold 0 of the cubic block, freshly read through the promoted evaluation rows)",
        "",
    ]
    for name, bar in bars.items():
        absolute_bar = bar["absolute_bar"]
        floor_value = bar["floor_value"]
        bar_text = f"{absolute_bar:.6f}" if isinstance(absolute_bar, float) else "pending"
        floor_text = f"{floor_value:.6f}" if isinstance(floor_value, float) else "pending"
        lines.append(
            f"- **{name}**: floor `{bar['floor_name']}` = {floor_text}, metric `{bar['metric']}`,"
            f" required improvement {bar['required_improvement']}, absolute bar **{bar_text}** -- {bar['reads']}"
        )
    lines.append("")
    return lines


def Placeholder_Sized_Member() -> CodomainAttention:
    """a freshly built member at the pre-registered configuration, statistics not yet fixed from any real population"""
    return Fresh_Completion_Member(ChannelStatistics(reference_density=1.0, magnetization_scale=1.0, potential_scale=1.0))


CONFIGURATION_NAME = f"hidden{HIDDEN_CHANNELS}_modes{KEPT_MODE}_heads{HEAD_COUNT}_layers{LAYER_COUNT}"


def Floor_Result_Rows(
    block: CubicBlock, elf_floor: MetricSummary, potential_floor: MetricSummary
) -> tuple[ResultRow, ResultRow]:
    """the two pre-registered floor summaries as result rows, keyed to the cubic block's own evaluation fold"""
    block_signature = Block_Signature(block.unit_of[identifier] for identifier in block.evaluation)
    return (
        ResultRow(
            key=ResultKey(
                member="codomain_attention",
                configuration=CONFIGURATION_NAME,
                task="localization",
                split="fold_0_evaluation",
                block=block_signature,
                group="semilocal_ridge_floor",
            ),
            summary=elf_floor,
            block_signature=block_signature,
        ),
        ResultRow(
            key=ResultKey(
                member="codomain_attention",
                configuration=CONFIGURATION_NAME,
                task="potential",
                split="fold_0_evaluation",
                block=block_signature,
                group="hartree_plus_semilocal_xc_ridge_floor",
            ),
            summary=potential_floor,
            block_signature=block_signature,
        ),
    )


def Write_Results(path: Path, block: CubicBlock, elf_floor: MetricSummary, potential_floor: MetricSummary) -> None:
    """the promoted cross-member schema: the pre-registered floor rows now, no verdicts until a trained member exists"""
    results = MemberResults(
        member="codomain_attention",
        regenerate="python -m operators.codomain_attention.report",
        rows=Floor_Result_Rows(block, elf_floor, potential_floor),
        verdicts=(),
    )
    Write_Member_Results(path, results)


def Main() -> int:
    """the pre-training report: architecture, split counts and every bar, written before a step of training runs"""
    block = CompletionBlock()
    cubic_block = CubicBlock()
    elf_floor = Elf_Semilocal_Floor_Summary(cubic_block)
    potential_floor = Potential_Semilocal_Floor_Summary(cubic_block)
    bars = Pre_Registered_Bars(elf_floor, potential_floor)
    sized_member = Placeholder_Sized_Member()
    parameter_count = sized_member.Parameter_Count()
    master_weight_megabytes = sum(value.nbytes for value in sized_member.Parameter_Values().values()) / 1e6
    lines = Pre_Training_Report_Lines(parameter_count, master_weight_megabytes, bars)
    lines += [
        "## Split counts (measured against the committed paired-fields fold map)",
        "",
        f"- fold 0 (evaluation): {len(block.evaluation)} runs",
        f"- fold 1 (validation): {len(block.validation)} runs",
        f"- folds 2-4 (pretrain): {len(block.member_train)} runs",
        f"- alloy transfer set (zero-shot only): {len(block.Alloy_Transfer_Identifiers())} runs",
        f"- K3 low-data defect slice (a quarter of the pretraining defect-only identifiers):"
        f" {len(block.Low_Data_Defect_Identifiers())} runs",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n")
    Write_Results(REPORT_PATH.parent / "results.json", cubic_block, elf_floor, potential_floor)
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
