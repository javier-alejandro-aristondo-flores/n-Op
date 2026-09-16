"""the member measured against its floors, written as one committed markdown artifact"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.data import ARTIFACT_DIRECTORY, POOL_ROOT, STORE_NAME
from operators.deep_dft import Deep_Dft_Network, DeepDft
from operators.deep_dft.floors import (
    Deep_Dft_Superposed_Atomic_Density_Errors,
    Element_Vocabulary,
    Fitted_Salted_Floor,
    Magnetic_Identifiers,
    Nearest_Copy_Errors,
    Salted_Floor_Errors,
)
from operators.deep_dft.message_passing import MessagePassingLayer
from operators.deep_dft.sampling import (
    CachedDeepDftStructure,
    Cached_Structure,
    ProbeBatchSource,
    Trilinear_Interpolate,
)
from operators.deep_dft.species import Loaded_Structure, SpeciesKeys, Structure, Training_Vocabulary
from operators.encoders import AtomEmbedding
from operators.evaluation import (
    Block_Signature,
    MemberResults,
    MetricSummary,
    ResultKey,
    ResultRow,
    ScoredRun,
    Summarize,
    Summary_Table,
    Write_Member_Results,
)
from operators.framework import Coefficients, Domain, GridSpec, PointSet
from operators.inspection import Render_Inspection_Suite, Render_Table
from operators.substrate import Host_Array, ParameterSet
from operators.training import ForwardLoss, Train, Training_Engine, TrainingHook, TrainingProgress, TrainingResult

REPORT_PATH = Path(__file__).parent / "report.md"

RESULTS_PATH = Path(__file__).parent / "results.json"

FIGURES_PATH = Path(__file__).parent / "figures"

MEMBER_NAME = "deep_dft"

CONFIGURATION_NAME = "minimal"

TASK_NAME = "structure_to_density_and_magnetization"

SPLIT_NAME = "paired_fields_fivefold"

BLOCK_NAME = "fold_0"

REGENERATE_COMMAND = "python3 -m operators.deep_dft.report"

# the inspection arrays are derived from corpus fields, and a derived array never leaves the pool either
ARRAY_CACHE_PATH = POOL_ROOT / STORE_NAME / "_figures" / "deep_dft"

TRAINING_ARTIFACT_PATH = POOL_ROOT / STORE_NAME / "_training" / "deep_dft"

DEFECT_CAMPAIGN = "defect_set"

METRIC_NAME = "normalized_mean_absolute_error"

# gate a: ten times better than the superposed-atomic-density floor
GATE_A_REQUIRED_IMPROVEMENT = 0.9

# gate b: three times better than the reduced-salted floor
GATE_B_REQUIRED_IMPROVEMENT = 2.0 / 3.0

GATE_C_BAR = 0.90

MAGNETIC_TOTAL_MOMENT_EPSILON = 1e-3

DEMONSTRATION_GRID_SHAPE = (16, 16, 16)

# the canon's kill block is fold zero; this member's own early stopping draws on fold one instead,
# leaving folds two through four for the gradient steps themselves, mirroring the flagship's own split
DEEP_DFT_SEED = 20260916

TRAINING_CAP_HOURS = 12.0

STAGE_FRACTIONS = (0.3, 0.3, 0.4)

PEAK_LEARNING_RATE = 1e-3

DIVERGENCE_PROBE_STEPS = 200

VALIDATION_INTERVAL = 100

FINAL_STAGE_PATIENCE = 15

MOMENT_NORMALIZATION_FLOOR = 1e-6


def Defect_Fold_Identifiers() -> tuple[dict[str, str], list[str], list[str]]:
    """each defect run's own exchangeable unit key, and the training and fold-zero identifier lists"""
    payload = json.loads((ARTIFACT_DIRECTORY / "paired_fields_fivefold.json").read_text())
    unit_key_of: dict[str, str] = {}
    train_identifiers: list[str] = []
    fold_zero_identifiers: list[str] = []
    for unit_key, unit in payload.items():
        if unit["campaign"] != DEFECT_CAMPAIGN:
            continue
        for identifier in unit["run_identifiers"]:
            unit_key_of[identifier] = unit_key
        destination = fold_zero_identifiers if unit["fold"] == 0 else train_identifiers
        destination.extend(unit["run_identifiers"])
    return unit_key_of, train_identifiers, fold_zero_identifiers


def Defect_Fold_Membership() -> dict[str, int]:
    """every defect-campaign run identifier's own fold number, read directly off the split file"""
    payload = json.loads((ARTIFACT_DIRECTORY / "paired_fields_fivefold.json").read_text())
    membership: dict[str, int] = {}
    for unit in payload.values():
        if unit["campaign"] != DEFECT_CAMPAIGN:
            continue
        for identifier in unit["run_identifiers"]:
            membership[identifier] = int(unit["fold"])
    return membership


def Loaded_Structures(identifiers: list[str]) -> tuple[Structure, ...]:
    """every identifier's own structure, skipping runs the store cannot answer for"""
    return tuple(
        structure
        for structure in (Loaded_Structure(DEFECT_CAMPAIGN, identifier) for identifier in identifiers)
        if structure is not None
    )


def Scored_Rows(
    errors: dict[str, float], unit_key_of: dict[str, str], family: str, held_out_identifiers: frozenset[str]
) -> list[ScoredRun]:
    """error values as scored rows under one metric name, held-out-chemistry runs tagged as extrapolation"""
    return [
        ScoredRun(
            identifier=identifier,
            unit_key=unit_key_of[identifier],
            campaign=DEFECT_CAMPAIGN,
            family=family,
            errors={METRIC_NAME: error},
            extrapolation="extrapolation" if identifier in held_out_identifiers else "interpolation",
        )
        for identifier, error in errors.items()
    ]


def Interpolation_Error_On_A_Synthetic_Field(seed: int = 20260916) -> float:
    """the trilinear interpolator's own root-mean-square error on a smooth field, at the campaign's grid shape"""

    def Field(points: NDArray[np.float64]) -> NDArray[np.float64]:
        """a smooth periodic scalar field with three fourier components"""
        return np.sin(2.0 * np.pi * points[:, 0]) * np.cos(4.0 * np.pi * points[:, 1]) + 0.3 * np.sin(
            6.0 * np.pi * points[:, 2]
        )

    shape = (80, 80, 80)
    axes = [np.arange(extent, dtype=np.float64) / extent for extent in shape]
    axis_grids = np.meshgrid(*axes, indexing="ij")
    grid_points = np.stack([axis_grid.reshape(-1) for axis_grid in axis_grids], axis=1)
    grid_values = Field(grid_points).reshape(*shape, 1)
    generator = np.random.default_rng(seed)
    query_points = generator.random((20000, 3))
    interpolated = Trilinear_Interpolate(grid_values, query_points)[:, 0]
    truth = Field(query_points)
    return float(np.sqrt(np.mean((interpolated - truth) ** 2)))


class LoadedBlock:
    """the defect campaign's own folds, loaded once and shared by the floors and the architecture sections"""


    def __init__(self) -> None:
        self.unit_key_of, train_identifiers, fold_zero_identifiers = Defect_Fold_Identifiers()
        self.train_structures = Loaded_Structures(train_identifiers)
        self.fold_zero_structures = Loaded_Structures(fold_zero_identifiers)
        self.training_vocabulary = Training_Vocabulary(self.train_structures)
        self.species_keys = SpeciesKeys(self.training_vocabulary)
        self.held_out_identifiers = frozenset(
            structure.identifier
            for structure in self.fold_zero_structures
            if self.species_keys.Held_Out_Chemistry(structure)
        )
        # fold one is the member's own early-stopping split, folds two through four its gradient steps,
        # mirroring the flagship's member_train/validation convention and leaving fold zero untouched
        fold_of = Defect_Fold_Membership()
        member_train_identifiers = [
            identifier for identifier in train_identifiers if fold_of.get(identifier) in (2, 3, 4)
        ]
        member_validation_identifiers = [
            identifier for identifier in train_identifiers if fold_of.get(identifier) == 1
        ]
        self.member_train_structures = Loaded_Structures(member_train_identifiers)
        self.member_validation_structures = Loaded_Structures(member_validation_identifiers)


@dataclass(slots=True)
class FloorMeasurements:
    """the four floor summaries, the pre-registered bars and the magnetic count, measured once and shared"""

    sad_summary_all: MetricSummary
    sad_summary_held_out: MetricSummary
    salted_summary: MetricSummary
    copy_summary: MetricSummary
    bars: dict[str, float]
    magnetic_identifiers: frozenset[str]
    interpolation_error: float


def Measured_Floors(block: LoadedBlock) -> FloorMeasurements:
    """the three floors and the pre-registered claim ladder, measured before any training, on this exact block"""
    unit_key_of = block.unit_key_of
    train_structures = block.train_structures
    fold_zero_structures = block.fold_zero_structures
    held_out_identifiers = block.held_out_identifiers

    sad_errors = Deep_Dft_Superposed_Atomic_Density_Errors(fold_zero_structures)
    element_vocabulary = Element_Vocabulary(train_structures)
    salted_floor = Fitted_Salted_Floor(train_structures, element_vocabulary)
    salted_errors = Salted_Floor_Errors(salted_floor, fold_zero_structures)
    copy_errors = Nearest_Copy_Errors(train_structures, fold_zero_structures)

    sad_rows = Scored_Rows(sad_errors, unit_key_of, "superposed_atomic_density", held_out_identifiers)
    salted_rows = Scored_Rows(salted_errors, unit_key_of, "reduced_salted", held_out_identifiers)
    copy_rows = Scored_Rows(copy_errors, unit_key_of, "nearest_structure_copy", held_out_identifiers)
    sad_rows_held_out = [row for row in sad_rows if row.identifier in held_out_identifiers]
    magnetic_identifiers = Magnetic_Identifiers(fold_zero_structures, epsilon=MAGNETIC_TOTAL_MOMENT_EPSILON)

    sad_summary_all = Summarize(sad_rows, METRIC_NAME, "superposed_atomic_density_floor_all_42")
    sad_summary_held_out = Summarize(sad_rows_held_out, METRIC_NAME, "superposed_atomic_density_floor_held_out_18")
    salted_summary = Summarize(salted_rows, METRIC_NAME, "reduced_salted_floor_all_42")
    copy_summary = Summarize(copy_rows, METRIC_NAME, "nearest_structure_copy_context_all_42")

    bars = {
        "gate_a_bar_all_42": sad_summary_all.median * (1.0 - GATE_A_REQUIRED_IMPROVEMENT),
        "gate_a_bar_held_out_18": sad_summary_held_out.median * (1.0 - GATE_A_REQUIRED_IMPROVEMENT),
        "gate_b_bar_all_42": salted_summary.median * (1.0 - GATE_B_REQUIRED_IMPROVEMENT),
    }
    return FloorMeasurements(
        sad_summary_all=sad_summary_all,
        sad_summary_held_out=sad_summary_held_out,
        salted_summary=salted_summary,
        copy_summary=copy_summary,
        bars=bars,
        magnetic_identifiers=magnetic_identifiers,
        interpolation_error=Interpolation_Error_On_A_Synthetic_Field(),
    )


def Result_Rows(block: LoadedBlock, measurements: FloorMeasurements) -> tuple[ResultRow, ...]:
    """the four floor summaries as result rows, keyed to this exact block and its own exchangeable-unit signature"""
    unit_key_of = block.unit_key_of
    fold_zero_unit_keys = {unit_key_of[structure.identifier] for structure in block.fold_zero_structures}
    held_out_unit_keys = {
        unit_key_of[structure.identifier]
        for structure in block.fold_zero_structures
        if structure.identifier in block.held_out_identifiers
    }
    all_signature = Block_Signature(fold_zero_unit_keys)
    held_out_signature = Block_Signature(held_out_unit_keys)

    def Row(summary: MetricSummary, signature: str) -> ResultRow:
        """one floor summary keyed under this block's own signature"""
        key = ResultKey(
            member=MEMBER_NAME,
            configuration=CONFIGURATION_NAME,
            task=TASK_NAME,
            split=SPLIT_NAME,
            block=BLOCK_NAME,
            group=summary.group_name,
        )
        return ResultRow(key=key, summary=summary, block_signature=signature)

    return (
        Row(measurements.sad_summary_all, all_signature),
        Row(measurements.sad_summary_held_out, held_out_signature),
        Row(measurements.salted_summary, all_signature),
        Row(measurements.copy_summary, all_signature),
    )


def Floor_Block_Lines(block: LoadedBlock, measurements: FloorMeasurements) -> list[str]:
    """the block counts, the three floors and the pre-registered claim ladder, as report prose"""
    unit_key_of = block.unit_key_of
    train_structures = block.train_structures
    fold_zero_structures = block.fold_zero_structures
    training_vocabulary = block.training_vocabulary
    held_out_identifiers = block.held_out_identifiers
    sad_summary_all = measurements.sad_summary_all
    sad_summary_held_out = measurements.sad_summary_held_out
    salted_summary = measurements.salted_summary
    copy_summary = measurements.copy_summary
    bars = measurements.bars
    magnetic_identifiers = measurements.magnetic_identifiers
    interpolation_error = measurements.interpolation_error

    lines = [
        "## The block",
        "",
        f"Defect campaign, fold zero as the evaluation (kill) block: {len(fold_zero_structures)} runs across"
        f" {len({unit_key_of[structure.identifier] for structure in fold_zero_structures})} units, folds one"
        f" through four training the floors ({len(train_structures)} runs). {len(held_out_identifiers)} of the"
        f" {len(fold_zero_structures)} fold-zero runs carry an element absent from every training fold"
        " (held-out chemistry), scored as its own row beside the pooled one. Training vocabulary: "
        f"{len(training_vocabulary) - 1} (element, pseudopotential title) pairs plus the trained unknown row.",
        "",
        "## Floors, measured before training, on this exact block, normalized mean absolute error",
        "",
        "The superposed-atomic-density floor reads `superposed_atomic_density` directly off the store, no"
        " fitting. The reduced-salted floor is a standardized ridge from per-species isotropic gaussian shells"
        " (eight widths, periodic images by cell height) onto density minus the atomic superposition, fit on"
        " 1,000 mixture-sampled probes per training run and scored on a fixed 5,000-point random subsample of"
        " each fold-zero run's own grid (a deliberate approximation for the floor's own cost, not for the"
        " member, which is scored on the true full grid); it stands in for the canon's own reduced"
        " density-fitting floor. The nearest-structure copy is context, not a gate: it copies the full charge"
        " density of the training run closest in per-element atom-count composition.",
        "",
        "```",
        Render_Table(Summary_Table((sad_summary_all, sad_summary_held_out, salted_summary, copy_summary))),
        "```",
        "",
        "### the pre-registered ladder, absolute normalized mean absolute error",
        "",
        f"- **gate a** (>= 10x better than the superposed-atomic-density floor, `required_improvement=0.9`):"
        f" pooled bar {bars['gate_a_bar_all_42']:.6f}, held-out-chemistry bar {bars['gate_a_bar_held_out_18']:.6f}",
        f"- **gate b** (>= 3x better than the reduced-salted floor, `required_improvement=2/3`):"
        f" bar {bars['gate_b_bar_all_42']:.6f}",
        f"- **gate c** (spin row, member-local, not a floor comparison): on the {len(magnetic_identifiers)}"
        f" magnetic fold-zero runs (`|final_magnetization| > {MAGNETIC_TOTAL_MOMENT_EPSILON}`), fraction with"
        f" relative total-moment error <= 5% and the right sign, bar >= {GATE_C_BAR}",
        "",
        f"Trilinear interpolation error, measured on a smooth synthetic field at the campaign's own 80-cubed"
        f" grid resolution, 20,000 random query points: root-mean-square {interpolation_error:.6f}.",
        "",
        "**Not yet measured**: the member has not trained (floors are measured and pre-registered before"
        " training by policy, and the card is not this stream's yet), so no row above compares the member to"
        " these bars. The compact-support kernel and this composition's own caller-side seam both already"
        " differentiate on the foreign engine (`Test_Foreign_Engine_Forward_And_Gradient_Agree_On_A_Tiny_"
        "Structure`), so training itself is the only thing waiting. The figure suite below is the built,"
        " untrained architecture; this section will carry the member's own comparison against these bars and"
        " the gate c pass fraction once a checkpoint exists.",
        "",
    ]
    return lines


def Architecture_Lines(block: LoadedBlock) -> list[str]:
    """the built configuration, its parameter count, and the figure suite rendered from a demonstration structure"""
    member = Deep_Dft_Network(block.training_vocabulary, seed=20260916)
    parameter_count = sum(value.size for value in member.Parameter_Values().values())

    demonstration = block.train_structures[0]
    resolved_keys = block.species_keys.Resolved(demonstration.species_keys)
    domain = Domain(lattice=demonstration.lattice)
    structure_point_set = PointSet(
        positions=demonstration.positions, domain=domain, species=np.asarray(resolved_keys)
    )
    condition = Coefficients(vector=np.asarray([demonstration.electron_count]), domain=domain)
    member(structure_point_set, GridSpec(DEMONSTRATION_GRID_SHAPE), condition)

    inspected: dict[str, NDArray[np.float64]] = {
        key: np.asarray(value, dtype=np.float64) for key, value in member.Inspect().items()
    }
    inspected_for_saving: dict[str, Any] = dict(inspected)
    cache_directory = ARRAY_CACHE_PATH / demonstration.identifier
    cache_directory.mkdir(parents=True, exist_ok=True)
    np.savez(cache_directory / "inspect.npz", **inspected_for_saving)
    suite = Render_Inspection_Suite(inspected, FIGURES_PATH, "deep_dft")

    return [
        "## Architecture, as built",
        "",
        "Atom embedding (member-local unknown-row policy) into a 64-wide channel space; three atom-atom"
        " `ContinuousDisplacementKernel` layers (cutoff 4.0 angstrom, 20-function sinc basis) plus a local"
        " linear term and a smooth unit each; the atoms then join the probe points into one point set and three"
        " more identically shaped atom-probe layers carry the joint state, probes marked receive-only; a"
        " two-layer perceptron head reads each probe's own features onto density and magnetization.",
        "",
        f"Parameter count: {parameter_count:,} (about 94% of it the six kernels' own radial weight tensors,"
        " basis_count x hidden x hidden each).",
        "",
        f"Figure suite: {len(suite.written)} files written under `operators/deep_dft/figures/`, "
        f"{len(suite.skipped)} inspection keys skipped ({', '.join(suite.skipped) if suite.skipped else 'none'})."
        " The atom-to-probe adjacency matrix (`composition__last_atom_to_probe_adjacency.png`) is this member's"
        " own figure: which probes fall inside which atoms' cutoff, on the demonstration structure"
        f" `{demonstration.identifier}`.",
        "",
    ]


def Deep_Dft_Cached_Structures(
    structures: tuple[Structure, ...], species_keys: SpeciesKeys, encoder: AtomEmbedding
) -> tuple[CachedDeepDftStructure, ...]:
    """every structure the store can still answer for, cached once for repeated probe draws"""
    return tuple(
        cached
        for cached in (Cached_Structure(structure, species_keys, encoder) for structure in structures)
        if cached is not None
    )


def Deep_Dft_Loss(member: DeepDft) -> ForwardLoss:
    """the importance-weighted probe loss: density plus the masked, moment-normalized magnetization"""

    def Loss(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        # geometry and indices are fixed constants, never differentiated against, so they are read back to
        # the host for slicing; only the targets and weights stay on the training engine, beside `predicted`
        atom_positions = Host_Array(lifted_batch["atom_positions"])
        atom_vocabulary_index = Host_Array(lifted_batch["atom_vocabulary_index"])
        atom_count = Host_Array(lifted_batch["atom_count"])
        lattice = Host_Array(lifted_batch["lattice"])
        probe_positions = Host_Array(lifted_batch["probe_positions"])
        has_magnetization = Host_Array(lifted_batch["has_magnetization"])
        absolute_moment = Host_Array(lifted_batch["absolute_moment"])
        probe_weights = lifted_batch["probe_weights"]
        probe_target_density = lifted_batch["probe_target_density"]
        probe_target_magnetization = lifted_batch["probe_target_magnetization"]

        structure_count = atom_positions.shape[0]
        total: Any = 0.0
        for structure_index in range(structure_count):
            this_atom_count = int(atom_count[structure_index])
            vocabulary_indices = np.asarray(
                atom_vocabulary_index[structure_index, :this_atom_count], dtype=np.intp
            )
            predicted = member.Forward(
                lifted,
                lattice[structure_index],
                atom_positions[structure_index, :this_atom_count],
                vocabulary_indices,
                probe_positions[structure_index],
            )
            weights = probe_weights[structure_index]
            weight_total = weights.sum()
            density_residual = predicted[:, 0] - probe_target_density[structure_index]
            density_term = (weights * density_residual * density_residual).sum() / weight_total
            moment_scale = float(max(float(absolute_moment[structure_index]), MOMENT_NORMALIZATION_FLOOR))
            magnetization_residual = (predicted[:, 1] - probe_target_magnetization[structure_index]) / moment_scale
            magnetization_term = (weights * magnetization_residual * magnetization_residual).sum() / weight_total
            total = total + density_term + float(has_magnetization[structure_index]) * magnetization_term
        return total / structure_count

    return Loss


class SamplerStatisticsHook(TrainingHook):
    """no per-step projection; records the last drawn batch's own importance-weight health after each validation"""


    def __init__(self, batch_source: ProbeBatchSource) -> None:
        self.batch_source = batch_source


    def After_Step(self, progress: TrainingProgress) -> None:
        return None


    def After_Validation(self, progress: TrainingProgress) -> dict[str, float]:
        last_batch = self.batch_source.last_batch
        if last_batch is None:
            return {}
        weights = np.asarray(last_batch.arrays["probe_weights"], dtype=np.float64)
        mean_weight = float(np.mean(weights))
        if mean_weight <= 0.0:
            return {}
        # the effective-sample-size fraction: one when every weight agrees, falling toward zero when
        # a handful of probes carry nearly all of the mass and the rest contribute almost nothing
        effective_fraction = float((np.sum(weights) ** 2) / (weights.size * np.sum(weights * weights)))
        return {
            "sampler_mean_weight": mean_weight,
            "sampler_weight_max_over_mean": float(np.max(weights)) / mean_weight,
            "sampler_effective_sample_fraction": effective_fraction,
        }


def Staged_Step_Counts(
    step_count: int, fractions: tuple[float, float, float] = STAGE_FRACTIONS
) -> tuple[int, int, int]:
    """a step budget split across three stages, the last absorbing whatever rounding leaves behind"""
    first_stage = round(fractions[0] * step_count)
    second_stage = round(fractions[1] * step_count)
    return first_stage, second_stage, step_count - first_stage - second_stage


def Sane_Loss_Curve(loss_curve: NDArray[np.float64], validation_curve: NDArray[np.float64]) -> bool:
    """every recorded loss and validation score stayed finite, and neither ran away from where it started"""
    if loss_curve.size == 0 or validation_curve.size == 0:
        return False
    if not (bool(np.all(np.isfinite(loss_curve))) and bool(np.all(np.isfinite(validation_curve)))):
        return False
    loss_held = bool(loss_curve[-1] < 10.0 * loss_curve[0] + 1.0)
    validation_held = bool(validation_curve[-1] < 10.0 * validation_curve[0] + 1.0)
    return loss_held and validation_held


def Write_Back_Message_Passing_Layer(layer: MessagePassingLayer, parameters: ParameterSet, prefix: str) -> None:
    """one message-passing layer's kernel and local-linear arrays folded back in place, under its own prefix"""
    for name, value in parameters.values.items():
        if name == f"{prefix}kernel.radial_weights":
            layer.kernel.parameter_values["radial_weights"] = value
        elif name.startswith(f"{prefix}local_linear."):
            local_name = name.removeprefix(f"{prefix}local_linear.")
            if local_name in layer.local_linear.parameter_values:
                layer.local_linear.parameter_values[local_name] = value


def Write_Back_Deep_Dft_Parameters(member: DeepDft, parameters: ParameterSet) -> None:
    """a flat trained parameter set folded back onto the member's own part-shaped storage"""
    for name, value in parameters.values.items():
        if name in member.atom_embedding.parameter_values:
            member.atom_embedding.parameter_values[name] = value
        if name in member.probe_head.parameter_values:
            member.probe_head.parameter_values[name] = value
    for layer_index, layer in enumerate(member.message_passing.atom_atom_layers):
        Write_Back_Message_Passing_Layer(layer, parameters, f"atom_atom_layer_{layer_index}.")
    for layer_index, layer in enumerate(member.message_passing.atom_probe_layers):
        Write_Back_Message_Passing_Layer(layer, parameters, f"atom_probe_layer_{layer_index}.")


# not run by this stream: floors are pre-registered and measured, but training itself waits on the card
# grant; wired against the promoted Train/TrainingHook/Training_Engine names and the lifted kernel, single
# precision, a checkpoint every validation pass under _training/deep_dft/, the sampler's own proposal-weight
# statistics recorded through SamplerStatisticsHook, capped by TRAINING_CAP_HOURS
def Train_Deep_Dft_Member(step_count: int, run_name: str) -> dict[str, object]:
    """the full staged run: a divergence probe with one allowed restart at a lower rate, then the staged schedule"""
    block = LoadedBlock()
    member = Deep_Dft_Network(block.training_vocabulary, seed=DEEP_DFT_SEED)
    training_structures = Deep_Dft_Cached_Structures(
        block.member_train_structures, block.species_keys, member.atom_embedding
    )
    validation_structures = Deep_Dft_Cached_Structures(
        block.member_validation_structures, block.species_keys, member.atom_embedding
    )
    batch_source = ProbeBatchSource(training_structures, validation_structures)
    forward_loss = Deep_Dft_Loss(member)
    parameters = ParameterSet(values=member.Parameter_Values())
    engine = Training_Engine(precision="single")
    hook = SamplerStatisticsHook(batch_source)

    stage_step_counts = Staged_Step_Counts(step_count)
    probe_steps = min(DIVERGENCE_PROBE_STEPS, stage_step_counts[0])
    chosen_peak_rate = PEAK_LEARNING_RATE
    probe_result: TrainingResult = Train(
        engine, parameters, forward_loss, batch_source, step_count=probe_steps, learning_rate=chosen_peak_rate,
        seed=DEEP_DFT_SEED, artifact_directory=TRAINING_ARTIFACT_PATH, run_name=f"{run_name}_stage0",
        validation_interval=probe_steps, patience=0, hook=hook,
    )
    if not Sane_Loss_Curve(probe_result.loss_curve, probe_result.validation_curve):
        chosen_peak_rate = PEAK_LEARNING_RATE * 0.3
        probe_result = Train(
            engine, ParameterSet(values=member.Parameter_Values()), forward_loss, batch_source,
            step_count=probe_steps, learning_rate=chosen_peak_rate, seed=DEEP_DFT_SEED,
            artifact_directory=TRAINING_ARTIFACT_PATH, run_name=f"{run_name}_stage0",
            validation_interval=probe_steps, patience=0, resume=False, hook=hook,
        )
        if not Sane_Loss_Curve(probe_result.loss_curve, probe_result.validation_curve):
            raise RuntimeError(
                "the loss is non-finite or diverging at both the peak and the reduced rate within the probe"
            )
    parameters = probe_result.parameters
    stage_rates = (chosen_peak_rate, chosen_peak_rate / 3.0, chosen_peak_rate / 9.0)

    manifest: dict[str, object] = {
        "run_name": run_name,
        "probe_learning_rate": chosen_peak_rate,
        "probe_steps": probe_steps,
        "training_structure_count": len(training_structures),
        "validation_structure_count": len(validation_structures),
    }
    for stage_index, (rate, stage_steps) in enumerate(zip(stage_rates, stage_step_counts, strict=True)):
        is_final_stage = stage_index == len(stage_step_counts) - 1
        result = Train(
            engine, parameters, forward_loss, batch_source, step_count=stage_steps, learning_rate=rate,
            seed=DEEP_DFT_SEED + stage_index, artifact_directory=TRAINING_ARTIFACT_PATH,
            run_name=f"{run_name}_stage{stage_index}", validation_interval=VALIDATION_INTERVAL,
            patience=FINAL_STAGE_PATIENCE if is_final_stage else 0, resume=(stage_index == 0), hook=hook,
        )
        parameters = result.parameters
        manifest[f"stage_{stage_index}"] = result.manifest
    Write_Back_Deep_Dft_Parameters(member, parameters)
    manifest["final_parameters"] = parameters
    manifest["member"] = member
    return manifest


def Main() -> int:
    """the block, its floors and pre-registered ladder, and the built architecture, written to report.md"""
    block = LoadedBlock()
    measurements = Measured_Floors(block)
    floor_lines = Floor_Block_Lines(block, measurements)
    architecture_lines = Architecture_Lines(block)
    header = [
        "# deep_dft — measured against its floors",
        "",
        f"Regenerate with `{REGENERATE_COMMAND}`.",
        "",
        "The block, the three floors and the pre-registered claim ladder below were measured before a single"
        " training step was taken. The member's own result follows once training is possible; until then this"
        " section says so plainly and nothing else about this command changes.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(header + floor_lines + architecture_lines) + "\n")
    print(f"wrote {REPORT_PATH}")

    results = MemberResults(
        member=MEMBER_NAME, regenerate=REGENERATE_COMMAND, rows=Result_Rows(block, measurements), verdicts=()
    )
    Write_Member_Results(RESULTS_PATH, results)
    print(f"wrote {RESULTS_PATH}")
    print(measurements.bars)
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
