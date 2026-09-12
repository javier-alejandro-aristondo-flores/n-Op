"""the member measured against its floors, written as one committed markdown artifact"""

import dataclasses
import json
import re
from pathlib import Path
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray

from operators.compositions import ExplicitStack
from operators.data import (
    Apply_Per_Shell_Filter,
    Apply_Standardized_Ridge,
    Archive_Path,
    ARTIFACT_DIRECTORY,
    Fit_Per_Shell_Filter,
    Fit_Standardized_Ridge,
    Gram_Pod,
    Guard_Fresh_Archives,
    Hartree_Potential,
    Nearest_Training_Run,
    POOL_ROOT,
    Project,
    Reconstruct,
    Ridge_Apply,
    Ridge_Fit,
    Run_Identifier,
    Semilocal_Xc_Ridge_Features,
    Spectral_Gradient_Magnitude_And_Laplacian,
    STORE_NAME,
)
from operators.evaluation import (
    Compare_To_Floor,
    Comparison_Table,
    FloorComparison,
    MetricSummary,
    ScoredRun,
    Summarize,
    Summarize_By,
    Summary_Table,
)
from operators.factorized_fourier import (
    Combined_Coarse_Input,
    Factorized_Fourier_Network,
    FactorizedFourier,
    FactorizedFourierConfiguration,
    FactorizedFourierTask,
    GRAM_CHANNEL_COUNT,
    Gram_Six,
    Gram_Statistics,
    Log_Compressed_Channels,
    Reference_Density,
    Spin_Channels,
    Standardized_Gram,
)
from operators.factorized_fourier.parametric import All_Strain_Arms, Arm, Interior_Levels, Level
from operators.framework import GridFunction, GridSpec, Layer, Spectral_Truncation_Resample
from operators.kernels.spectral import Mode_Wavevector_Features
from operators.inspection import (
    Render_Error_Spread,
    Render_Floor_Comparison,
    Render_Inspection_Suite,
    Render_Prediction_Against_Truth,
    Render_Table,
)
from operators.metrics import (
    Mean_Absolute_Error,
    Mean_Discrepancy,
    Mean_Removed_Mean_Absolute_Error,
    Mean_Removed_Relative_L2,
    Relative_L2,
    Structural_Similarity_3d,
)
from operators.substrate import ParameterSet
from operators.tasks import Card_Named
from operators.training import (
    BatchSource,
    Field_From_Archive,
    Parameter_Field_Examples,
    Read_Checkpoint,
    Strain_Assignments_By_Run,
    Strain_Assignments_Of_Pool,
    Train,
    Training_Engine,
    TrainingBatch,
    TrainingProgress,
)

REPORT_PATH = Path(__file__).parent / "report.md"
FIGURES_PATH = Path(__file__).parent / "figures"
# the inspection arrays are fields, and a field never leaves the pool -- only the drawing does
ARRAY_CACHE_PATH = POOL_ROOT / STORE_NAME / "_figures" / "factorized_fourier"
# checkpoints are scratch, not a corpus artifact, but they still hold no volumetric data either way
TRAINING_ARTIFACT_PATH = POOL_ROOT / STORE_NAME / "_training" / "factorized_fourier"

CUBIC_CAMPAIGNS = ("supercell_strains", "defect_set")
COARSE_SHAPE = (40, 40, 40)
FINE_SHAPE = (80, 80, 80)
LOCALIZATION_CHANNELS = ("electron_localization_up", "electron_localization_down")
POTENTIAL_CHANNELS = ("local_potential_up", "local_potential_down")
POTENTIAL_METRIC_NAMES = ("mean_removed_relative_l2", "mean_removed_mean_absolute_error", "mean_discrepancy")

# stage zero's own choices, kept here so the recomputed numbers reproduce them
RIDGE_TRAIN_RUN_COUNT = 80
FILTER_TRAIN_RUN_COUNT = 120
RIDGE_VOXELS_PER_RUN = 2000
RIDGE_SEED = 20260828

CARD_METRIC_NAMES = ("mean_absolute_error", "structural_similarity_3d", "relative_l2")

# the pattern rule (test-suite.md section 2): every member on this task must clear this margin or leave the task
PATTERN_RULE_MARGIN = 0.20

# the flagship's own bar (IMPLEMENTATION.md): half the floor's error or the member is killed
FLAGSHIP_KILL_MARGIN = 0.50

# the assembly as built: width, depth and the full coarse Nyquist confirmed by Check_Modes_Fit
HIDDEN_CHANNELS = 64
LAYER_COUNT = 12
KEPT_MODE = 19
FLAGSHIP_SEED = 20260912

# the pre-authorized schedule: a peak rate, one allowed halving of the schedule if the probe diverges
PEAK_LEARNING_RATE = 1e-3
DIVERGENCE_PROBE_STEPS = 200
VALIDATION_INTERVAL = 100
FINAL_STAGE_PATIENCE = 15
STAGE_FRACTIONS = (0.3, 0.3, 0.4)


def Fold_Membership() -> dict[str, tuple[int, str, str, str]]:
    """every cubic-campaign run identifier with its fold, campaign, owning split unit and own run path"""
    payload = json.loads((ARTIFACT_DIRECTORY / "paired_fields_fivefold.json").read_text())
    membership: dict[str, tuple[int, str, str, str]] = {}
    for unit_key, unit in payload.items():
        if unit["campaign"] not in CUBIC_CAMPAIGNS:
            continue
        for identifier, run_path in zip(unit["run_identifiers"], unit["run_paths"], strict=True):
            membership[identifier] = (int(unit["fold"]), str(unit["campaign"]), unit_key, str(run_path))
    return membership


def Functional_Of_Run_Path(run_path: str) -> str:
    """the exchange-correlation functional a cubic-block run's own path names, cheap or accurate"""
    lowered = run_path.lower()
    return "accurate" if "hse06" in lowered or "hse" in lowered else "cheap"


class CubicBlock:
    """the kill block's identifiers, grouped by fold, campaign and split unit"""


    def __init__(self) -> None:
        membership = Fold_Membership()
        by_fold: dict[int, list[str]] = {fold: [] for fold in range(5)}
        campaign_of: dict[str, str] = {}
        unit_of: dict[str, str] = {}
        run_path_of: dict[str, str] = {}
        for identifier, (fold, campaign, unit_key, run_path) in membership.items():
            archive_path = Archive_Path(campaign, identifier)
            if not archive_path.exists():
                continue
            with np.load(archive_path) as archive:
                if "charge_density" not in archive or archive["charge_density"].shape != (80, 80, 80):
                    continue
                complete = "electron_localization_up" in archive and "local_potential_up" in archive
            if not complete:
                continue
            by_fold[fold].append(identifier)
            campaign_of[identifier] = campaign
            unit_of[identifier] = unit_key
            run_path_of[identifier] = run_path
        Guard_Fresh_Archives(identifier for fold_identifiers in by_fold.values() for identifier in fold_identifiers)
        self.by_fold = {fold: sorted(identifiers) for fold, identifiers in by_fold.items()}
        self.campaign_of = campaign_of
        self.unit_of = unit_of
        self.run_path_of = run_path_of


    def Functional_Of(self, identifier: str) -> str:
        """the identifier's own run path read for its exchange-correlation functional"""
        return Functional_Of_Run_Path(self.run_path_of[identifier])


    @property
    def evaluation(self) -> list[str]:
        """fold zero, the kill block every entry is finally judged against"""
        return self.by_fold[0]


    @property
    def validation(self) -> list[str]:
        """fold one, held out from the member's own training for early stopping"""
        return self.by_fold[1]


    @property
    def floor_train(self) -> list[str]:
        """folds one through four pooled, exactly stage zero's own training role"""
        return sorted(identifier for fold in (1, 2, 3, 4) for identifier in self.by_fold[fold])


    @property
    def member_train(self) -> list[str]:
        """folds two through four, fold one held out for the member's own early stopping"""
        return sorted(identifier for fold in (2, 3, 4) for identifier in self.by_fold[fold])


def Card_Metric_Errors(
    predicted: NDArray[np.float64], truth: NDArray[np.float64]
) -> dict[str, float]:
    """the task card's three metrics between one predicted and one true field"""
    return {
        "mean_absolute_error": Mean_Absolute_Error(predicted, truth),
        "structural_similarity_3d": Structural_Similarity_3d(predicted, truth),
        "relative_l2": Relative_L2(predicted, truth),
    }


def Elf_Ridge_Rows(block: CubicBlock) -> list[ScoredRun]:
    """the semilocal pointwise localization floor, per-spin ridge on density features, all three card metrics"""
    generator = np.random.default_rng(RIDGE_SEED)
    feature_rows: list[NDArray[np.float64]] = []
    target_rows: list[NDArray[np.float64]] = []
    for identifier in block.floor_train[:RIDGE_TRAIN_RUN_COUNT]:
        campaign = block.campaign_of[identifier]
        with np.load(Archive_Path(campaign, identifier)) as archive:
            density = np.asarray(archive["charge_density"], dtype=np.float64)
            magnetization = np.asarray(archive["magnetization_density"], dtype=np.float64)
            lattice = np.asarray(archive["lattice"], dtype=np.float64)
            up_target = np.asarray(archive["electron_localization_up"], dtype=np.float64)
            down_target = np.asarray(archive["electron_localization_down"], dtype=np.float64)
        for sign, target in ((1.0, up_target), (-1.0, down_target)):
            spin_density = Spectral_Truncation_Resample(((density + sign * magnetization) / 2.0)[None], COARSE_SHAPE)[0]
            gradient, laplacian = Spectral_Gradient_Magnitude_And_Laplacian(spin_density, lattice)
            chosen = generator.choice(spin_density.size, size=RIDGE_VOXELS_PER_RUN, replace=False)
            features = np.stack([spin_density.ravel(), gradient.ravel(), laplacian.ravel()], axis=1)
            feature_rows.append(features[chosen])
            target_rows.append(target.ravel()[chosen])
    features = np.concatenate(feature_rows)
    targets = np.concatenate(target_rows)
    scales = features.std(axis=0)
    coefficients = Ridge_Fit(features / scales, targets)

    scored: list[ScoredRun] = []
    for identifier in block.evaluation:
        campaign = block.campaign_of[identifier]
        with np.load(Archive_Path(campaign, identifier)) as archive:
            density = np.asarray(archive["charge_density"], dtype=np.float64)
            magnetization = np.asarray(archive["magnetization_density"], dtype=np.float64)
            lattice = np.asarray(archive["lattice"], dtype=np.float64)
            up_truth = np.asarray(archive["electron_localization_up"], dtype=np.float64)
            down_truth = np.asarray(archive["electron_localization_down"], dtype=np.float64)
        for sign, channel, truth in ((1.0, LOCALIZATION_CHANNELS[0], up_truth), (-1.0, LOCALIZATION_CHANNELS[1], down_truth)):
            spin_density = Spectral_Truncation_Resample(((density + sign * magnetization) / 2.0)[None], COARSE_SHAPE)[0]
            gradient, laplacian = Spectral_Gradient_Magnitude_And_Laplacian(spin_density, lattice)
            evaluated = np.stack([spin_density.ravel(), gradient.ravel(), laplacian.ravel()], axis=1) / scales
            predicted = np.clip(Ridge_Apply(coefficients, evaluated), 0.0, 1.0).reshape(COARSE_SHAPE)
            scored.append(
                ScoredRun(
                    identifier=f"{identifier}_{channel}",
                    unit_key=block.unit_of[identifier],
                    campaign=campaign,
                    family=channel,
                    errors=Card_Metric_Errors(predicted, truth),
                    covariate_values={"spin_channel": channel},
                )
            )
    return scored


def Shell_Filter_Rows(block: CubicBlock) -> list[ScoredRun]:
    """the per-shell isotropic linear filter, gains fit on the up channel, applied to both, all three card metrics"""
    train_used = block.floor_train[:FILTER_TRAIN_RUN_COUNT]
    coarse_inputs: list[NDArray[np.float64]] = []
    localization_targets: list[NDArray[np.float64]] = []
    for identifier in train_used:
        campaign = block.campaign_of[identifier]
        with np.load(Archive_Path(campaign, identifier)) as archive:
            density = np.asarray(archive["charge_density"], dtype=np.float64)
            target = np.asarray(archive[LOCALIZATION_CHANNELS[0]], dtype=np.float64)
        coarse_inputs.append(Spectral_Truncation_Resample(density[None], COARSE_SHAPE)[0])
        localization_targets.append(target)
    gains = Fit_Per_Shell_Filter(coarse_inputs, localization_targets)
    del coarse_inputs, localization_targets

    scored: list[ScoredRun] = []
    for identifier in block.evaluation:
        campaign = block.campaign_of[identifier]
        with np.load(Archive_Path(campaign, identifier)) as archive:
            density = np.asarray(archive["charge_density"], dtype=np.float64)
            up_truth = np.asarray(archive[LOCALIZATION_CHANNELS[0]], dtype=np.float64)
            down_truth = np.asarray(archive[LOCALIZATION_CHANNELS[1]], dtype=np.float64)
        coarse = Spectral_Truncation_Resample(density[None], COARSE_SHAPE)[0]
        predicted = Apply_Per_Shell_Filter(gains, coarse)
        for channel, truth in ((LOCALIZATION_CHANNELS[0], up_truth), (LOCALIZATION_CHANNELS[1], down_truth)):
            scored.append(
                ScoredRun(
                    identifier=f"{identifier}_{channel}",
                    unit_key=block.unit_of[identifier],
                    campaign=campaign,
                    family=channel,
                    errors=Card_Metric_Errors(predicted, truth),
                    covariate_values={"spin_channel": channel},
                )
            )
    return scored


def Training_Mean_Rows(block: CubicBlock) -> list[ScoredRun]:
    """the trivial floor for scale: every evaluation run predicted as the training block's own mean field"""
    train_used = block.floor_train[:FILTER_TRAIN_RUN_COUNT]
    sums = {channel: np.zeros(COARSE_SHAPE, dtype=np.float64) for channel in LOCALIZATION_CHANNELS}
    for identifier in train_used:
        campaign = block.campaign_of[identifier]
        with np.load(Archive_Path(campaign, identifier)) as archive:
            for channel in LOCALIZATION_CHANNELS:
                sums[channel] += np.asarray(archive[channel], dtype=np.float64)
    means = {channel: total / len(train_used) for channel, total in sums.items()}

    scored: list[ScoredRun] = []
    for identifier in block.evaluation:
        campaign = block.campaign_of[identifier]
        with np.load(Archive_Path(campaign, identifier)) as archive:
            for channel in LOCALIZATION_CHANNELS:
                truth = np.asarray(archive[channel], dtype=np.float64)
                scored.append(
                    ScoredRun(
                        identifier=f"{identifier}_{channel}",
                        unit_key=block.unit_of[identifier],
                        campaign=campaign,
                        family=channel,
                        errors=Card_Metric_Errors(means[channel], truth),
                        covariate_values={"spin_channel": channel},
                    )
                )
    return scored


def Coarse_Log_Density_Representation(
    campaign: str, identifier: str, reference_density: float
) -> NDArray[np.float64]:
    """one run's two log-compressed spin channels, truncated to the coarse grid and flattened for a distance metric"""
    with np.load(Archive_Path(campaign, identifier)) as archive:
        density = np.asarray(archive["charge_density"], dtype=np.float64)
        magnetization = np.asarray(archive["magnetization_density"], dtype=np.float64)
    fine_channels = Log_Compressed_Channels(density, magnetization, reference_density)
    coarse_channels = Spectral_Truncation_Resample(fine_channels, COARSE_SHAPE)
    return coarse_channels.reshape(-1)


def Nearest_Run_Rows(block: CubicBlock) -> list[ScoredRun]:
    """the memorization floor: the nearest training run's own fields, in the member's own coarse representation"""
    sample_densities: list[NDArray[np.float64]] = []
    sample_magnetizations: list[NDArray[np.float64]] = []
    for identifier in block.floor_train[:RIDGE_TRAIN_RUN_COUNT]:
        campaign = block.campaign_of[identifier]
        with np.load(Archive_Path(campaign, identifier)) as archive:
            sample_densities.append(np.asarray(archive["charge_density"], dtype=np.float64))
            sample_magnetizations.append(np.asarray(archive["magnetization_density"], dtype=np.float64))
    # the same sample the ridge fits on, reused here only to fix the log compression's own scale
    reference_density = Reference_Density(sample_densities, sample_magnetizations)
    del sample_densities, sample_magnetizations

    train_used = block.floor_train
    train_representations = np.stack(
        [
            Coarse_Log_Density_Representation(block.campaign_of[identifier], identifier, reference_density)
            for identifier in train_used
        ]
    )
    scored: list[ScoredRun] = []
    for identifier in block.evaluation:
        campaign = block.campaign_of[identifier]
        evaluation_representation = Coarse_Log_Density_Representation(campaign, identifier, reference_density)
        distances = np.linalg.norm(train_representations - evaluation_representation[None, :], axis=1)
        nearest_identifier = train_used[int(np.argmin(distances))]
        nearest_campaign = block.campaign_of[nearest_identifier]
        with np.load(Archive_Path(nearest_campaign, nearest_identifier)) as archive:
            copied = {channel: np.asarray(archive[channel], dtype=np.float64) for channel in LOCALIZATION_CHANNELS}
        with np.load(Archive_Path(campaign, identifier)) as archive:
            truths = {channel: np.asarray(archive[channel], dtype=np.float64) for channel in LOCALIZATION_CHANNELS}
        for channel in LOCALIZATION_CHANNELS:
            scored.append(
                ScoredRun(
                    identifier=f"{identifier}_{channel}",
                    unit_key=block.unit_of[identifier],
                    campaign=campaign,
                    family=channel,
                    errors=Card_Metric_Errors(copied[channel], truths[channel]),
                    covariate_values={"spin_channel": channel},
                )
            )
    return scored


def Loaded_Density_And_Magnetization(
    campaign: str, identifier: str
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """one run's charge density, magnetization (zero-filled where the run is spin-restricted) and lattice"""
    with np.load(Archive_Path(campaign, identifier)) as archive:
        density = np.asarray(archive["charge_density"], dtype=np.float64)
        if "magnetization_density" in archive:
            magnetization = np.asarray(archive["magnetization_density"], dtype=np.float64)
        else:
            magnetization = np.zeros_like(density)
        lattice = np.asarray(archive["lattice"], dtype=np.float64)
    return density, magnetization, lattice


@dataclasses.dataclass(frozen=True, slots=True)
class LocalizationExample:
    """one run's eight-channel coarse input, precomputed once, cached beside its coarse localization target"""

    identifier: str
    unit_key: str
    campaign: str
    combined_coarse_input: NDArray[np.float32]
    target_values: NDArray[np.float32]


def Localization_Examples(
    identifiers: list[str],
    block: CubicBlock,
    reference_density: float,
    gram_mean: NDArray[np.float64],
    gram_scale: NDArray[np.float64],
) -> list[LocalizationExample]:
    """every named run, held resident as its own precomputed coarse input and coarse target, in single precision"""
    examples: list[LocalizationExample] = []
    for identifier in identifiers:
        campaign = block.campaign_of[identifier]
        density, magnetization, lattice = Loaded_Density_And_Magnetization(campaign, identifier)
        log_density_values = Log_Compressed_Channels(density, magnetization, reference_density)
        gram_vector = Standardized_Gram(Gram_Six(lattice), gram_mean, gram_scale)
        # the truncation this call pays happens once here, not once per step the cached example is drawn
        combined_coarse_input = Combined_Coarse_Input(log_density_values, gram_vector, COARSE_SHAPE)
        with np.load(Archive_Path(campaign, identifier)) as archive:
            target_values = np.stack(
                [np.asarray(archive[channel], dtype=np.float64) for channel in LOCALIZATION_CHANNELS]
            )
        examples.append(
            LocalizationExample(
                identifier=identifier,
                unit_key=block.unit_of[identifier],
                campaign=campaign,
                combined_coarse_input=np.asarray(combined_coarse_input, dtype=np.float32),
                target_values=np.asarray(target_values, dtype=np.float32),
            )
        )
    return examples


class LocalizationBatches(BatchSource):
    """one training example drawn uniformly with replacement every step, and every validation unit held fixed"""


    def __init__(self, training_examples: list[LocalizationExample], validation_examples: list[LocalizationExample]) -> None:
        self.training_examples = training_examples
        self.validation_by_unit: dict[str, list[LocalizationExample]] = {}
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


def Localization_Loss(member: FactorizedFourier) -> Any:
    """mean squared error over every example a batch carries, looped since the lifted path takes one at a time"""
    cap_hit_history: list[bool] = []
    iterations_history: list[int] = []

    def Loss(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        example_count = lifted_batch["combined_coarse_input"].shape[0]
        total = 0.0
        for example_index in range(example_count):
            predicted = member.Forward_From_Coarse_Input(lifted, lifted_batch["combined_coarse_input"][example_index])
            residual = predicted - lifted_batch["targets"][example_index]
            total = total + (residual * residual).mean()
            cap_was_hit = member.last_fixed_point_cap_was_hit
            iterations_taken = member.last_fixed_point_iterations
            if cap_was_hit is not None and iterations_taken is not None:
                cap_hit_history.append(cap_was_hit)
                iterations_history.append(iterations_taken)
                # the fixed-point health floor, visible while the run trains rather than only at evaluation;
                # this closure cannot tell a training solve from a validation one, so the window mixes both
                if len(cap_hit_history) % VALIDATION_INTERVAL == 0:
                    recent_hits = cap_hit_history[-100:]
                    recent_iterations = iterations_history[-100:]
                    cap_hit_fraction = sum(recent_hits) / len(recent_hits)
                    mean_iterations = sum(recent_iterations) / len(recent_iterations)
                    print(
                        f"solve {len(cap_hit_history)}: cap-hit fraction {cap_hit_fraction:.2f} over the last"
                        f" {len(recent_hits)} solves, mean iterations {mean_iterations:.1f}",
                        flush=True,
                    )
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
    # a single-example batch is noisy, so this asks only that nothing blew up, not that every step improved
    return bool(loss_curve[-1] < 10.0 * loss_curve[0] + 1.0) and bool(validation_curve[-1] < 10.0 * validation_curve[0] + 1.0)


def Input_Statistics(
    block: CubicBlock, training_identifiers: list[str]
) -> tuple[float, NDArray[np.float64], NDArray[np.float64]]:
    """the reference density and gram standardization one training population fixes, reused unchanged at evaluation"""
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


def Write_Back_Layer(layer: Layer[GridFunction], parameters: ParameterSet, prefix: str) -> None:
    """one layer's own kernel and local-linear arrays, read off their prefixed names in a flat parameter set"""
    for bare_name in list(layer.kernel.parameter_values):
        prefixed_name = f"{prefix}kernel.{bare_name}"
        if prefixed_name in parameters.values:
            layer.kernel.parameter_values[bare_name] = parameters.values[prefixed_name]
    for bare_name in list(layer.local_linear.parameter_values):
        prefixed_name = f"{prefix}local_linear.{bare_name}"
        if prefixed_name in parameters.values:
            layer.local_linear.parameter_values[bare_name] = parameters.values[prefixed_name]


def Write_Back_Parameters(member: FactorizedFourier, parameters: ParameterSet) -> None:
    """a flat trained parameter set folded back onto the member's own part-shaped storage, any composition kind"""
    for name, value in parameters.values.items():
        if name in member.lift.parameter_values:
            member.lift.parameter_values[name] = value
        if name in member.projection.parameter_values:
            member.projection.parameter_values[name] = value
    composition = member.spectral_stack
    if isinstance(composition, ExplicitStack):
        for layer_index, layer in enumerate(composition.layers):
            Write_Back_Layer(layer, parameters, f"layer_{layer_index}.")
    else:
        Write_Back_Layer(composition.layer, parameters, "")


def Train_Flagship_Member(
    step_count: int,
    run_name: str,
    configuration: FactorizedFourierConfiguration = "explicit",
    stage_fractions: tuple[float, float, float] = STAGE_FRACTIONS,
) -> dict[str, object]:
    """the full staged run: a divergence probe with one allowed restart at a lower rate, then the staged schedule"""
    block = CubicBlock()
    training_identifiers = block.member_train
    validation_identifiers = block.validation

    reference_density, gram_mean, gram_scale = Input_Statistics(block, training_identifiers)

    training_examples = Localization_Examples(training_identifiers, block, reference_density, gram_mean, gram_scale)
    validation_examples = Localization_Examples(validation_identifiers, block, reference_density, gram_mean, gram_scale)
    batches = LocalizationBatches(training_examples, validation_examples)

    member = Factorized_Fourier_Network(
        hidden_channels=HIDDEN_CHANNELS,
        kept_modes=(KEPT_MODE, KEPT_MODE, KEPT_MODE),
        layer_count=LAYER_COUNT,
        reference_density=reference_density,
        gram_mean=gram_mean,
        gram_scale=gram_scale,
        processing_shape=COARSE_SHAPE,
        seed=FLAGSHIP_SEED,
        configuration=configuration,
    )
    forward_loss = Localization_Loss(member)
    parameters = ParameterSet(values=member.Parameter_Values())
    engine = Training_Engine()

    stage_step_counts = Staged_Step_Counts(step_count, stage_fractions)
    probe_steps = min(DIVERGENCE_PROBE_STEPS, stage_step_counts[0])
    chosen_peak_rate = PEAK_LEARNING_RATE
    probe_result = Train(
        engine, parameters, forward_loss, batches, step_count=probe_steps, learning_rate=chosen_peak_rate,
        seed=FLAGSHIP_SEED, artifact_directory=TRAINING_ARTIFACT_PATH, run_name=f"{run_name}_stage0",
        validation_interval=probe_steps, patience=0,
    )
    if not Sane_Loss_Curve(probe_result.loss_curve, probe_result.validation_curve):
        chosen_peak_rate = PEAK_LEARNING_RATE * 0.3
        probe_result = Train(
            engine, ParameterSet(values=member.Parameter_Values()), forward_loss, batches, step_count=probe_steps,
            learning_rate=chosen_peak_rate, seed=FLAGSHIP_SEED, artifact_directory=TRAINING_ARTIFACT_PATH,
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
            seed=FLAGSHIP_SEED + stage_index, artifact_directory=TRAINING_ARTIFACT_PATH,
            run_name=f"{run_name}_stage{stage_index}", validation_interval=VALIDATION_INTERVAL,
            patience=FINAL_STAGE_PATIENCE if is_final_stage else 0, resume=(stage_index == 0),
        )
        parameters = result.parameters
        manifest[f"stage_{stage_index}"] = result.manifest
    Write_Back_Parameters(member, parameters)
    manifest["final_parameters"] = parameters
    manifest["member"] = member
    return manifest


def Recorded_Bars(
    ridge_rows: list[ScoredRun], mean_rows: list[ScoredRun], copy_rows: list[ScoredRun]
) -> dict[str, float]:
    """the whole claim ladder in absolute mean absolute error, the canon's two bars and this project's three added ones"""
    ridge_median = Summarize(ridge_rows, "mean_absolute_error", "semilocal_ridge_floor").median
    mean_median = Summarize(mean_rows, "mean_absolute_error", "training_mean_trivial_floor").median
    copy_median = Summarize(copy_rows, "mean_absolute_error", "nearest_run_copy_floor").median
    return {
        "canon_kill_semilocal_ridge_half": ridge_median * (1.0 - FLAGSHIP_KILL_MARGIN),
        "canon_pattern_rule_semilocal_ridge_twenty_percent": ridge_median * (1.0 - PATTERN_RULE_MARGIN),
        "added_beat_training_mean_template": mean_median,
        "added_beat_nearest_run_copy": copy_median,
        "added_stretch_half_the_template": mean_median * 0.5,
    }


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


def Floor_Block_Lines() -> tuple[list[str], dict[str, float]]:
    """the block counts, all four floors and the pre-registered claim ladder, measured before any training happens"""
    block = CubicBlock()
    ridge_rows = Elf_Ridge_Rows(block)
    filter_rows = Shell_Filter_Rows(block)
    mean_rows = Training_Mean_Rows(block)
    copy_rows = Nearest_Run_Rows(block)
    bars = Recorded_Bars(ridge_rows, mean_rows, copy_rows)

    summaries: list[MetricSummary] = []
    for floor_label, rows in (
        ("training_mean_trivial_floor", mean_rows),
        ("nearest_run_copy_floor", copy_rows),
        ("per_shell_linear_filter", filter_rows),
        ("semilocal_ridge_floor", ridge_rows),
    ):
        summaries.extend(Floor_Summaries(rows, floor_label))

    lines = [
        "## The block",
        "",
        f"Cubic block (`supercell_strains` and `defect_set`, 80³ charge density, full localization and potential):"
        f" {len(block.floor_train)} runs across folds one through four train the floors,"
        f" {len(block.evaluation)} runs in fold zero are the evaluation (kill) block."
        f" The member additionally holds out fold one ({len(block.validation)} runs) for its own early stopping"
        f" and trains on folds two through four ({len(block.member_train)} runs); the floors keep stage zero's"
        " own folds one through four as their training role, so their numbers reproduce stage zero's exactly.",
        "",
        "## Floors, measured before training, on this exact block, in the card's own metrics",
        "",
        "The ridge fits on the first 80 training runs at 2,000 voxels each, per spin channel; the per-shell filter"
        " fits on the first 120, its gains taken from the up channel alone and applied to both; the nearest-run"
        " copy searches all 261 training runs by plain L2 distance over the member's own coarse representation"
        " (the two log-compressed spin densities at 40³, the reference density fixed from the ridge's own first-80"
        " sample) and copies that run's localization fields verbatim. Every floor is scored per run on both spin"
        " channels, medians aggregated to the exchangeable split unit first, and broken out by campaign beside its"
        " pooled row, since a positional floor reads very differently on near-identical strains than on scattered"
        " defects.",
        "",
        "```",
        Render_Table(Summary_Table(tuple(summaries))),
        "```",
        "",
        "### the claim ladder, pre-registered before the member has seen this block",
        "",
        "Every level is absolute mean absolute error; a lower number is stricter. The first two are the canon's own"
        " bars (test-suite.md section 2's pattern rule and this entry's own IMPLEMENTATION.md kill), neither"
        " invented here. The rest are added before training, because the semilocal ridge turned out weaker than a"
        " purely positional floor on this block — the same mechanism as the Poisson climatology in"
        " stage0-report.md: a template beats a coordinate-blind fit on near-identical geometries, so the canon's"
        " own kill is, on this block, a weaker bar than the trivial template added here for scale.",
        "",
        f"1. **canon kill** (I.1, half the semilocal ridge): {bars['canon_kill_semilocal_ridge_half']:.6f}",
        f"2. **canon pattern rule** (at least 20% better than the ridge or the task is left):"
        f" {bars['canon_pattern_rule_semilocal_ridge_twenty_percent']:.6f}",
        f"3. **added, beat the training-mean template** (a member above this line has learned nothing beyond a"
        f" positional average): {bars['added_beat_training_mean_template']:.6f}",
        "4. **added, beat the nearest-run copy** (the memorization null this suite requires of every task):"
        f" {bars['added_beat_nearest_run_copy']:.6f}",
        "5. **added, the stretch level** (half the template's error — the level at which the member resolves the"
        f" run-to-run variation, per-voxel spread 0.021, rather than reproducing the average):"
        f" {bars['added_stretch_half_the_template']:.6f}",
        "",
        "**Measured out of order**: level 4 (beat the nearest-run copy) is *stricter* than level 5 (the stretch"
        " level) on this block — the nearest training run is close enough, on both campaigns, that copying it"
        " verbatim beats even half the template's error. The memorization null was not expected to be harder than"
        " the stretch goal designed to demand genuine operator behavior; on this block it is, so passing level 5"
        " without also passing level 4 is not possible here, and level 4 is the real hard bar to read as the"
        " stretch goal.",
        "",
    ]
    return lines, bars


# the potential task (charge_to_potential), host-only floor work: the fine-grid target changes what "coarse"
# means, so the truncation ceiling is measured before anything else, then every floor stage zero measured on
# the defect campaign alone and on the spin mean is remeasured here on the full cubic block, per spin


def Mean_Removed_Field(field: NDArray[np.float64]) -> NDArray[np.float64]:
    """the field with its own spatial mean removed"""
    return field - field.mean()


def Potential_Metric_Errors(predicted: NDArray[np.float64], truth: NDArray[np.float64]) -> dict[str, float]:
    """the potential card's three metrics between one predicted and one true field"""
    return {
        "mean_removed_relative_l2": Mean_Removed_Relative_L2(predicted, truth),
        "mean_removed_mean_absolute_error": Mean_Removed_Mean_Absolute_Error(predicted, truth),
        "mean_discrepancy": Mean_Discrepancy(predicted, truth),
    }


def Truncation_Ceiling_Rows(block: CubicBlock) -> list[ScoredRun]:
    """how much of the potential a 40-cubed trunk cannot carry: truncate to coarse, zero-pad back, mean-removed"""
    scored: list[ScoredRun] = []
    for identifier in block.evaluation:
        campaign = block.campaign_of[identifier]
        with np.load(Archive_Path(campaign, identifier)) as archive:
            truths = {channel: np.asarray(archive[channel], dtype=np.float64) for channel in POTENTIAL_CHANNELS}
        for channel, truth in truths.items():
            coarse = Spectral_Truncation_Resample(truth[None], COARSE_SHAPE)[0]
            back_to_fine = Spectral_Truncation_Resample(coarse[None], FINE_SHAPE)[0]
            scored.append(
                ScoredRun(
                    identifier=f"{identifier}_{channel}",
                    unit_key=block.unit_of[identifier],
                    campaign=campaign,
                    family=channel,
                    errors={"mean_removed_relative_l2": Mean_Removed_Relative_L2(back_to_fine, truth)},
                    covariate_values={"spin_channel": channel},
                )
            )
    return scored


@dataclasses.dataclass(frozen=True, slots=True)
class PotentialRunData:
    """one run's raw and per-spin densities beside its own Hartree potential and both spin potentials"""

    identifier: str
    campaign: str
    unit_key: str
    lattice: NDArray[np.float64]
    density: NDArray[np.float64]
    spin_up_density: NDArray[np.float64]
    spin_down_density: NDArray[np.float64]
    hartree: NDArray[np.float64]
    up_truth: NDArray[np.float64]
    down_truth: NDArray[np.float64]


def Loaded_Potential_Run(block: CubicBlock, identifier: str) -> PotentialRunData:
    """one run's density, per-spin split, Hartree potential and both spin potentials, loaded once"""
    campaign = block.campaign_of[identifier]
    density, magnetization, lattice = Loaded_Density_And_Magnetization(campaign, identifier)
    spin_up_density, spin_down_density = Spin_Channels(density, magnetization)
    hartree = Hartree_Potential(density, lattice)
    with np.load(Archive_Path(campaign, identifier)) as archive:
        up_truth = np.asarray(archive[POTENTIAL_CHANNELS[0]], dtype=np.float64)
        down_truth = np.asarray(archive[POTENTIAL_CHANNELS[1]], dtype=np.float64)
    return PotentialRunData(
        identifier=identifier,
        campaign=campaign,
        unit_key=block.unit_of[identifier],
        lattice=lattice,
        density=density,
        spin_up_density=spin_up_density,
        spin_down_density=spin_down_density,
        hartree=hartree,
        up_truth=up_truth,
        down_truth=down_truth,
    )


def Spin_Remainder(run: PotentialRunData, channel: str) -> NDArray[np.float64]:
    """one spin's own potential less the (spin-independent) Hartree part, both mean-removed first"""
    truth = run.up_truth if channel == POTENTIAL_CHANNELS[0] else run.down_truth
    return Mean_Removed_Field(truth) - Mean_Removed_Field(run.hartree)


def Climatology_Fields(train_runs: list[PotentialRunData]) -> dict[str, NDArray[np.float64]]:
    """the training block's own mean remainder per spin, the positional template the ridge is judged against"""
    sums = {channel: np.zeros(FINE_SHAPE, dtype=np.float64) for channel in POTENTIAL_CHANNELS}
    for run in train_runs:
        for channel in POTENTIAL_CHANNELS:
            sums[channel] += Spin_Remainder(run, channel)
    return {channel: total / len(train_runs) for channel, total in sums.items()}


def Potential_Ridge(ridge_runs: list[PotentialRunData]) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """standardized ridge coefficients fit on both spins' own density features against their own remainder"""
    generator = np.random.default_rng(RIDGE_SEED)
    feature_rows: list[NDArray[np.float64]] = []
    target_rows: list[NDArray[np.float64]] = []
    for run in ridge_runs:
        for channel, spin_density in (
            (POTENTIAL_CHANNELS[0], run.spin_up_density),
            (POTENTIAL_CHANNELS[1], run.spin_down_density),
        ):
            features = Semilocal_Xc_Ridge_Features(spin_density, run.lattice)
            remainder = Spin_Remainder(run, channel).ravel()
            chosen = generator.choice(features.shape[0], size=RIDGE_VOXELS_PER_RUN, replace=False)
            feature_rows.append(features[chosen])
            target_rows.append(remainder[chosen])
    scales = np.concatenate(feature_rows).std(axis=0)
    coefficients = Ridge_Fit(np.concatenate(feature_rows) / scales, np.concatenate(target_rows))
    return coefficients, scales


def Potential_Rows(
    evaluation_runs: list[PotentialRunData],
    predicted_by_channel: dict[str, dict[str, NDArray[np.float64]]],
) -> list[ScoredRun]:
    """one scored run per evaluation run and spin channel, for every named floor sharing this evaluation pass"""
    scored: list[ScoredRun] = []
    for run in evaluation_runs:
        for channel, truth in ((POTENTIAL_CHANNELS[0], run.up_truth), (POTENTIAL_CHANNELS[1], run.down_truth)):
            predicted = predicted_by_channel[channel][run.identifier]
            scored.append(
                ScoredRun(
                    identifier=f"{run.identifier}_{channel}",
                    unit_key=run.unit_key,
                    campaign=run.campaign,
                    family=channel,
                    errors=Potential_Metric_Errors(predicted, truth),
                    covariate_values={"spin_channel": channel},
                )
            )
    return scored


def Potential_Nearest_Run_Rows(block: CubicBlock, reference_density: float) -> list[ScoredRun]:
    """the memorization floor: the nearest training run's own potential fields, copied verbatim"""
    train_used = block.floor_train
    train_representations = np.stack(
        [
            Coarse_Log_Density_Representation(block.campaign_of[identifier], identifier, reference_density)
            for identifier in train_used
        ]
    )
    scored: list[ScoredRun] = []
    for identifier in block.evaluation:
        campaign = block.campaign_of[identifier]
        evaluation_representation = Coarse_Log_Density_Representation(campaign, identifier, reference_density)
        distances = np.linalg.norm(train_representations - evaluation_representation[None, :], axis=1)
        nearest_identifier = train_used[int(np.argmin(distances))]
        nearest_campaign = block.campaign_of[nearest_identifier]
        with np.load(Archive_Path(nearest_campaign, nearest_identifier)) as archive:
            copied = {channel: np.asarray(archive[channel], dtype=np.float64) for channel in POTENTIAL_CHANNELS}
        with np.load(Archive_Path(campaign, identifier)) as archive:
            truths = {channel: np.asarray(archive[channel], dtype=np.float64) for channel in POTENTIAL_CHANNELS}
        for channel, truth in truths.items():
            scored.append(
                ScoredRun(
                    identifier=f"{identifier}_{channel}",
                    unit_key=block.unit_of[identifier],
                    campaign=campaign,
                    family=channel,
                    errors=Potential_Metric_Errors(copied[channel], truth),
                    covariate_values={"spin_channel": channel},
                )
            )
    return scored


def Potential_Floor_Rows(block: CubicBlock) -> dict[str, list[ScoredRun]]:
    """every potential floor, sharing one load and one Hartree computation per run, scored on the kill block"""
    train_identifiers = block.floor_train[:FILTER_TRAIN_RUN_COUNT]
    train_runs = [Loaded_Potential_Run(block, identifier) for identifier in train_identifiers]
    ridge_runs = train_runs[:RIDGE_TRAIN_RUN_COUNT]
    evaluation_runs = [Loaded_Potential_Run(block, identifier) for identifier in block.evaluation]

    climatology = Climatology_Fields(train_runs)
    coefficients, scales = Potential_Ridge(ridge_runs)
    # the filter's gains are fit on the up channel alone and applied to both, matching the localization floor
    filter_gains = Fit_Per_Shell_Filter(
        [run.density for run in train_runs], [Mean_Removed_Field(run.up_truth) for run in train_runs]
    )
    training_mean = {
        channel: np.mean([Mean_Removed_Field(run.up_truth if channel == POTENTIAL_CHANNELS[0] else run.down_truth) for run in train_runs], axis=0)
        for channel in POTENTIAL_CHANNELS
    }

    hartree_only: dict[str, dict[str, NDArray[np.float64]]] = {channel: {} for channel in POTENTIAL_CHANNELS}
    climatology_only: dict[str, dict[str, NDArray[np.float64]]] = {channel: {} for channel in POTENTIAL_CHANNELS}
    hartree_plus_climatology: dict[str, dict[str, NDArray[np.float64]]] = {channel: {} for channel in POTENTIAL_CHANNELS}
    hartree_plus_ridge: dict[str, dict[str, NDArray[np.float64]]] = {channel: {} for channel in POTENTIAL_CHANNELS}
    shell_filter: dict[str, dict[str, NDArray[np.float64]]] = {channel: {} for channel in POTENTIAL_CHANNELS}
    training_mean_predicted: dict[str, dict[str, NDArray[np.float64]]] = {channel: {} for channel in POTENTIAL_CHANNELS}
    for run in evaluation_runs:
        # the card's own metrics remove each field's mean internally, so the raw Hartree term needs no pre-removal
        filtered = Apply_Per_Shell_Filter(filter_gains, run.density)
        for channel, spin_density in (
            (POTENTIAL_CHANNELS[0], run.spin_up_density),
            (POTENTIAL_CHANNELS[1], run.spin_down_density),
        ):
            hartree_only[channel][run.identifier] = run.hartree
            climatology_only[channel][run.identifier] = climatology[channel]
            hartree_plus_climatology[channel][run.identifier] = run.hartree + climatology[channel]
            features = Semilocal_Xc_Ridge_Features(spin_density, run.lattice) / scales
            predicted_remainder = Ridge_Apply(coefficients, features).reshape(FINE_SHAPE)
            hartree_plus_ridge[channel][run.identifier] = run.hartree + predicted_remainder
            shell_filter[channel][run.identifier] = filtered
            training_mean_predicted[channel][run.identifier] = training_mean[channel]

    return {
        "hartree_only": Potential_Rows(evaluation_runs, hartree_only),
        "climatology_only": Potential_Rows(evaluation_runs, climatology_only),
        "hartree_plus_climatology": Potential_Rows(evaluation_runs, hartree_plus_climatology),
        "hartree_plus_semilocal_xc_ridge": Potential_Rows(evaluation_runs, hartree_plus_ridge),
        "per_shell_linear_filter": Potential_Rows(evaluation_runs, shell_filter),
        "training_mean_trivial_floor": Potential_Rows(evaluation_runs, training_mean_predicted),
    }


def Potential_Target_Scale(runs: list[PotentialRunData]) -> float:
    """the training block's pooled standard deviation of the mean-removed spin potentials"""
    values = [Mean_Removed_Field(run.up_truth).ravel() for run in runs]
    values += [Mean_Removed_Field(run.down_truth).ravel() for run in runs]
    return float(np.std(np.concatenate(values)))


@dataclasses.dataclass(frozen=True, slots=True)
class PotentialExample:
    """one run's cached coarse input and metric feature, beside its own mean-removed, scaled fine-grid target"""

    identifier: str
    unit_key: str
    campaign: str
    combined_coarse_input: NDArray[np.float32]
    mode_wavevector_features: NDArray[np.float32]
    target_values: NDArray[np.float32]


def Potential_Examples(
    identifiers: list[str],
    block: CubicBlock,
    reference_density: float,
    gram_mean: NDArray[np.float64],
    gram_scale: NDArray[np.float64],
    kept_modes: tuple[int, int, int],
    target_scale: float,
) -> list[PotentialExample]:
    """every named run, held resident as its own precomputed coarse input, metric feature and scaled target"""
    examples: list[PotentialExample] = []
    for identifier in identifiers:
        campaign = block.campaign_of[identifier]
        density, magnetization, lattice = Loaded_Density_And_Magnetization(campaign, identifier)
        log_density_values = Log_Compressed_Channels(density, magnetization, reference_density)
        gram_vector = Standardized_Gram(Gram_Six(lattice), gram_mean, gram_scale)
        combined_coarse_input = Combined_Coarse_Input(log_density_values, gram_vector, COARSE_SHAPE)
        mode_wavevector_features = Mode_Wavevector_Features(lattice, kept_modes)
        with np.load(Archive_Path(campaign, identifier)) as archive:
            target_values = np.stack(
                [Mean_Removed_Field(np.asarray(archive[channel], dtype=np.float64)) for channel in POTENTIAL_CHANNELS]
            )
        examples.append(
            PotentialExample(
                identifier=identifier,
                unit_key=block.unit_of[identifier],
                campaign=campaign,
                combined_coarse_input=np.asarray(combined_coarse_input, dtype=np.float32),
                mode_wavevector_features=np.asarray(mode_wavevector_features, dtype=np.float32),
                target_values=np.asarray(target_values / target_scale, dtype=np.float32),
            )
        )
    return examples


class PotentialBatches(BatchSource):
    """one training example drawn uniformly with replacement every step, and every validation unit held fixed"""


    def __init__(self, training_examples: list[PotentialExample], validation_examples: list[PotentialExample]) -> None:
        self.training_examples = training_examples
        self.validation_by_unit: dict[str, list[PotentialExample]] = {}
        for example in validation_examples:
            self.validation_by_unit.setdefault(example.unit_key, []).append(example)
        self.last_drawn_identifier: str | None = None


    def Next_Batch(self, generator: np.random.Generator) -> TrainingBatch:
        drawn = self.training_examples[int(generator.integers(0, len(self.training_examples)))]
        self.last_drawn_identifier = drawn.identifier
        return TrainingBatch(
            {
                "combined_coarse_input": drawn.combined_coarse_input[None],
                "mode_wavevector_features": drawn.mode_wavevector_features[None],
                "targets": drawn.target_values[None],
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
                            "mode_wavevector_features": np.stack(
                                [example.mode_wavevector_features for example in examples]
                            ),
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


def Potential_Loss(member: FactorizedFourier) -> Any:
    """mean squared error, in scaled mean-removed units, looped since the lifted path takes one at a time"""

    def Loss(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        example_count = lifted_batch["combined_coarse_input"].shape[0]
        total = 0.0
        for example_index in range(example_count):
            predicted = member.Forward_From_Coarse_Input(
                lifted,
                lifted_batch["combined_coarse_input"][example_index],
                lifted_batch["mode_wavevector_features"][example_index],
                FINE_SHAPE,
            )
            residual = predicted - lifted_batch["targets"][example_index]
            total = total + (residual * residual).mean()
        return total / example_count

    return Loss


def Train_Potential_Member(step_count: int, run_name: str) -> dict[str, object]:
    """the full staged run for the potential task: coarse trunk, metric-aware kernels, the same probe discipline"""
    block = CubicBlock()
    training_identifiers = block.member_train
    validation_identifiers = block.validation

    reference_density, gram_mean, gram_scale = Input_Statistics(block, training_identifiers)

    scale_runs = [
        Loaded_Potential_Run(block, identifier) for identifier in training_identifiers[:RIDGE_TRAIN_RUN_COUNT]
    ]
    target_scale = Potential_Target_Scale(scale_runs)
    del scale_runs

    kept_modes = (KEPT_MODE, KEPT_MODE, KEPT_MODE)
    training_examples = Potential_Examples(
        training_identifiers, block, reference_density, gram_mean, gram_scale, kept_modes, target_scale
    )
    validation_examples = Potential_Examples(
        validation_identifiers, block, reference_density, gram_mean, gram_scale, kept_modes, target_scale
    )
    batches = PotentialBatches(training_examples, validation_examples)

    member = Factorized_Fourier_Network(
        hidden_channels=HIDDEN_CHANNELS,
        kept_modes=kept_modes,
        layer_count=LAYER_COUNT,
        reference_density=reference_density,
        gram_mean=gram_mean,
        gram_scale=gram_scale,
        processing_shape=COARSE_SHAPE,
        seed=FLAGSHIP_SEED,
        task="potential",
        target_scale=target_scale,
    )
    forward_loss = Potential_Loss(member)
    parameters = ParameterSet(values=member.Parameter_Values())
    engine = Training_Engine()

    stage_step_counts = Staged_Step_Counts(step_count)
    probe_steps = min(DIVERGENCE_PROBE_STEPS, stage_step_counts[0])
    chosen_peak_rate = PEAK_LEARNING_RATE
    probe_result = Train(
        engine, parameters, forward_loss, batches, step_count=probe_steps, learning_rate=chosen_peak_rate,
        seed=FLAGSHIP_SEED, artifact_directory=TRAINING_ARTIFACT_PATH, run_name=f"{run_name}_stage0",
        validation_interval=probe_steps, patience=0,
    )
    if not Sane_Loss_Curve(probe_result.loss_curve, probe_result.validation_curve):
        chosen_peak_rate = PEAK_LEARNING_RATE * 0.3
        probe_result = Train(
            engine, ParameterSet(values=member.Parameter_Values()), forward_loss, batches, step_count=probe_steps,
            learning_rate=chosen_peak_rate, seed=FLAGSHIP_SEED, artifact_directory=TRAINING_ARTIFACT_PATH,
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
        "reference_density": reference_density,
        "target_scale": target_scale,
        "probe_learning_rate": chosen_peak_rate,
        "probe_steps": probe_steps,
        "training_example_count": len(training_examples),
        "validation_unit_count": len(batches.validation_by_unit),
    }
    for stage_index, (rate, stage_steps) in enumerate(zip(stage_rates, stage_step_counts, strict=True)):
        is_final_stage = stage_index == len(stage_step_counts) - 1
        result = Train(
            engine, parameters, forward_loss, batches, step_count=stage_steps, learning_rate=rate,
            seed=FLAGSHIP_SEED + stage_index, artifact_directory=TRAINING_ARTIFACT_PATH,
            run_name=f"{run_name}_stage{stage_index}", validation_interval=VALIDATION_INTERVAL,
            patience=FINAL_STAGE_PATIENCE if is_final_stage else 0, resume=(stage_index == 0),
        )
        parameters = result.parameters
        manifest[f"stage_{stage_index}"] = result.manifest
    Write_Back_Parameters(member, parameters)
    manifest["final_parameters"] = parameters
    manifest["member"] = member
    return manifest


def Potential_Task_Lines() -> list[str]:
    """the potential task's truncation ceiling and every floor, host-only, before the metric-aware member is built"""
    block = CubicBlock()
    ceiling_rows = Truncation_Ceiling_Rows(block)
    ceiling_median = Summarize(ceiling_rows, "mean_removed_relative_l2", "truncation_ceiling").median

    floor_rows = Potential_Floor_Rows(block)
    sample_densities: list[NDArray[np.float64]] = []
    sample_magnetizations: list[NDArray[np.float64]] = []
    for identifier in block.floor_train[:RIDGE_TRAIN_RUN_COUNT]:
        density, magnetization, _ = Loaded_Density_And_Magnetization(block.campaign_of[identifier], identifier)
        sample_densities.append(density)
        sample_magnetizations.append(magnetization)
    reference_density = Reference_Density(sample_densities, sample_magnetizations)
    floor_rows["nearest_run_copy_floor"] = Potential_Nearest_Run_Rows(block, reference_density)

    summaries: list[MetricSummary] = []
    for floor_label, rows in floor_rows.items():
        for metric_name in POTENTIAL_METRIC_NAMES:
            summaries.append(Summarize(rows, metric_name, floor_label))
            for campaign_summary in Summarize_By(rows, metric_name, "campaign"):
                summaries.append(
                    dataclasses.replace(campaign_summary, group_name=f"{floor_label}__{campaign_summary.group_name}")
                )

    # stage zero's own numbers, defect campaign only, spin-mean potential -- the sanity check this recomputation owes
    defect_climatology = Summarize(
        [row for row in floor_rows["hartree_plus_climatology"] if row.campaign == "defect_set"],
        "mean_removed_relative_l2",
        "defect_only_check",
    ).median
    defect_ridge = Summarize(
        [row for row in floor_rows["hartree_plus_semilocal_xc_ridge"] if row.campaign == "defect_set"],
        "mean_removed_relative_l2",
        "defect_only_check",
    ).median
    canon_bar_median = Summarize(
        floor_rows["hartree_plus_semilocal_xc_ridge"], "mean_removed_relative_l2", "hartree_plus_semilocal_xc_ridge"
    ).median

    return [
        "## The potential task (`charge_to_potential`), host-only work",
        "",
        "**Truncation ceiling.** The target lives on the fine grid (80³), unlike the localization field's 40³, so"
        " truncate-early no longer matches the target as built for I.1. Measured on the evaluation block: each"
        " spin potential truncated to 40³ and zero-padded back to 80³, against its own untouched fine-grid"
        " original, mean-removed relative L2:"
        f" median **{100 * ceiling_median:.2f}%**. This is the fraction of the potential a coarse trunk cannot"
        " carry by construction, before any model is judged.",
        "",
        f"An earlier draft of this section pre-registered a flat 1% threshold on this number and stopped here,"
        f" against it: that threshold was the wrong stop condition, since what actually matters is the ceiling's"
        f" size relative to the bar a trained member must clear, not an arbitrary absolute figure. The canon's"
        f" own bar is half the Hartree + semilocal-XC floor's error (below); at {100 * canon_bar_median / 2.0:.2f}%"
        f" required against a {100 * ceiling_median:.2f}% ceiling, there is roughly an order of magnitude of"
        " headroom, so the design is the coarse trunk with the readout followed by a lifted, differentiable"
        " resample back to the fine shape. The fine-grid trunk question returns only if a trained member's own"
        " error approaches the ceiling -- it is the canon's 9 GB super-later ablation, never a default.",
        "",
        "**Floors**, all three card metrics, per spin, unit-aggregated and broken out by campaign, following"
        " stage zero's recipes (`Poisson_Lines`, `Shell_Filter_Lines`) but on the full cubic block rather than"
        " the defect campaign alone, and per spin rather than on the spin-mean potential:",
        "",
        "```",
        Render_Table(Summary_Table(tuple(summaries))),
        "```",
        "",
        "### sanity check against stage zero's own committed numbers",
        "",
        f"Stage zero (defect campaign only, spin-mean potential): Hartree + climatology 57.26%, Hartree +"
        f" semilocal-XC ridge 56.20%. Recomputed here (defect campaign only, but per spin rather than spin-mean):"
        f" Hartree + climatology {100 * defect_climatology:.2f}%, Hartree + semilocal-XC ridge"
        f" {100 * defect_ridge:.2f}%. The difference is the per-spin-versus-spin-mean gap: a spin-mean potential"
        " already averages away the part of the exchange-correlation remainder that differs between the two"
        " spins, which a per-spin score cannot, so the two numbers are expected to differ by roughly that"
        " averaged-away spread rather than agree exactly.",
        "",
        "### the ladder for this task, neither bar invented here",
        "",
        f"- **canon bar**: more than 2x better than the Hartree + semilocal-XC ridge floor (median"
        f" {100 * canon_bar_median:.2f}% mean-removed relative L2) -- required absolute:"
        f" **{100 * canon_bar_median / 2.0:.2f}%** -- or record that the physics floor suffices and keep this"
        " task as a pipeline unit test, a finding rather than a failure.",
        "- **added, as for ELF**: beat the training-mean template; beat the nearest-run copy.",
        "- **the per-shell linear filter is the linearity certificate, not a kill**: stage zero read 23.35% on the"
        " spin mean over cubic fold zero, 2.4x better than the physics floor; this recomputation's per-spin filter"
        f" row (above) tests that same hypothesis on this block.",
        "- **the DEQ cross-entry bar**: fixed-point's error on this task within 1.5x of I.1's own error on the"
        " same split.",
        "",
    ]


# the deep-equilibrium ladder (canon I.3): parameter counts of all three rungs, computed now; every trained
# number -- steps, wall-clock, peak memory, convergence rate, seed -- waits for the runs the integrator schedules


def Rung_Parameter_Count(configuration: FactorizedFourierConfiguration, layer_count: int) -> int:
    """one rung's total parameter count at the flagship's own width and mode budget, without training it"""
    member = Factorized_Fourier_Network(
        hidden_channels=HIDDEN_CHANNELS,
        kept_modes=(KEPT_MODE, KEPT_MODE, KEPT_MODE),
        layer_count=layer_count,
        reference_density=1.0,
        gram_mean=np.zeros(GRAM_CHANNEL_COUNT),
        gram_scale=np.ones(GRAM_CHANNEL_COUNT),
        processing_shape=COARSE_SHAPE,
        configuration=configuration,
    )
    return sum(value.size for value in member.Parameter_Values().values())


def Deep_Equilibrium_Ladder_Lines() -> list[str]:
    """the I.3 ladder pre-registered: parameter counts of every rung, the matched-params comparator, both bars"""
    explicit_same_width = Rung_Parameter_Count("explicit", LAYER_COUNT)
    tied_and_fixed_point = Rung_Parameter_Count("weight_tied", LAYER_COUNT)
    # one explicit layer at this width carries exactly the shared layer's own parameter count, an exact match
    matched_params_layer_count = 1
    explicit_matched_params = Rung_Parameter_Count("explicit", matched_params_layer_count)
    assert explicit_matched_params == tied_and_fixed_point
    return [
        "## The deep-equilibrium ladder (canon I.3), pre-registered before any rung is trained",
        "",
        "Three configurations of the same factory (`operators.factorized_fourier.Factorized_Fourier_Network`,"
        " `configuration=\"explicit\" | \"weight_tied\" | \"fixed_point\"`), differing only in composition and one"
        " design choice the weight-tied and fixed-point rungs share: their one applied-repeatedly layer carries no"
        " residual, unlike the explicit stack's twelve. A residual here would make repeated or iterated application"
        " drift rather than contract, since the fixed point would then need the correction term itself to vanish"
        " rather than the whole map to settle.",
        "",
        "```",
        f"explicit (same width, {LAYER_COUNT} layers):     {explicit_same_width:>10} parameters",
        f"weight_tied (depth {LAYER_COUNT}, one shared layer): {tied_and_fixed_point:>10} parameters"
        f" ({explicit_same_width / tied_and_fixed_point:.2f}x fewer than the same-width explicit stack)",
        f"fixed_point (one shared layer):        {tied_and_fixed_point:>10} parameters (identical to weight_tied,"
        " same one layer)",
        f"explicit, matched params ({matched_params_layer_count} layer):   {explicit_matched_params:>10} parameters"
        " (exact match to the tied block, not merely approximate: one explicit layer at this width has precisely"
        " the shared layer's own count)",
        "```",
        "",
        "**Stability escalation.** The primitive (`operators.compositions.fixed_point.FixedPoint`) implements"
        " damping and Anderson acceleration (history depth, regularization, a condition-number ceiling that"
        " declines a near-parallel history) and three backward rules (phantom at a chosen depth, jacobian-free as"
        " phantom depth one, and the exact implicit adjoint). It does **not** implement per-mode spectral clipping,"
        " a Hutchinson Jacobian penalty, or a monotone parametrization -- the canon's own further escalation. These"
        " are not built here, speculatively, against a convergence failure that has not happened: the toy audit"
        " below converges cleanly with damping and Anderson acceleration alone. If a real 80³ run fails to"
        " converge, that is the order to reach for them in.",
        "",
        "**The mandatory 8³ gradient audit** ran on this member's own separable layer (width 2, one kept mode,"
        " nonzero local bias so the origin is not the map's only fixed point), not a generic one, in"
        " `Test_The_Mandatory_Gradient_Audit_On_This_Members_Own_Layer`: phantom depth 1, phantom depth 3, the"
        " exact implicit adjoint, central finite differences and the depth-matched full unroll all agree --"
        " implicit within the finite-difference-versus-unroll disagreement itself, phantom depth 3 within an order"
        " of magnitude of that same disagreement. The convergence and health-metric tests"
        " (`Test_Fixed_Point_Inspect_Exposes_The_Health_Signals_After_A_Member_Call`,"
        " `Test_The_Health_Metric_Is_A_Fraction_Of_Inputs_Converged_Read_Off_Inspect`) confirm the health floor is"
        " readable off `Inspect()` after an ordinary member call, since the lifted forward path calls `Resolved`"
        " directly and the member records the solve itself -- `FixedPoint.Forward` alone never does.",
        "",
        "### the two bars (test-suite.md, I.3), neither invented here",
        "",
        "- **kill**: the explicit comparator, at *both* matchings above, beats fixed-point at matched seeds (3) and"
        " wall-clock (fixed-point is not judged the winner unless it is also at least 3x faster to train); the"
        " health floor kills below 80% of validation samples converging to 1e-3 within 32 iterations after tuning,"
        " and stands as a caution rather than a pass below 90%.",
        "- **the honest deliverable is the decomposition curve** explicit → weight-tied → FNO-DEQ. \"Weight-tying"
        " yes, DEQ no\" -- the middle rung matching the explicit comparator while the fixed-point rung does not"
        " clear the wall-clock bar -- is a legitimate verdict and will be reported as such if that is what the"
        " runs show.",
        "",
        "Every trained number below is the integrator's to schedule and this stream's to report once run: steps,"
        " wall-clock seconds, peak memory, the convergence rate (fraction of the evaluation block converging to"
        " 1e-3 within 32 iterations), and the seed -- for the explicit same-width comparator, the explicit"
        " matched-params comparator, weight-tied, and fixed-point, three seeds each.",
        "",
        "```",
        "rung                       | steps | wall_clock_s | peak_memory_MiB | convergence_rate     | seed",
        "explicit (same width)      | 24404 |    14183     |     ~3600       | n/a (not iterative)  | 20260912 (1 of 3)",
        "explicit (matched params)  | 35505 |     1872     |      ~700       | n/a (not iterative)  | 20260912 (1 of 3)",
        "weight_tied                | 23804 |     9670     |     ~3185       | n/a (not iterative)  | 20260912 (1 of 3)",
        "fixed_point                |   --  |     --       |       --        |          --           |  --",
        "```",
        "",
        "**Steps** are the sum actually completed across all three stages (the final stage's own patience can stop"
        " it short of the stage plan, as it did for the same-width explicit rung at 24,404 of 35,505 and"
        " weight-tied at 23,804; the matched-params explicit rung instead ran its full budget without stopping"
        " early at any of the three stages -- 10,652 / 10,652 / 14,201, all 35,505 requested -- so its number"
        " reflects the training budget rather than a convergence plateau, and a longer budget might read lower"
        " still). **Wall-clock** and **peak memory** are one seed's own measured run, the first of the three the"
        " kill bar needs -- peak memory is read from periodic `nvidia-smi` checks during the run, not a"
        " continuously logged maximum, so it is reported to the nearest hundred MiB rather than claimed exact.",
        "",
    ]


# the member's own result on the localization task: loaded from whichever checkpoint the training driver above
# has written, scored against every floor above, on the exact evaluation block the floors themselves were fit
# and measured against -- host-only, the numpy inference path, no engine and no accelerator needed to read it

ELF_EXPLICIT_RUN_NAME = "elf_fold0_explicit_35505"
SUPER_RESOLUTION_SAMPLE_STRIDE = 12
COMPARABLE_CARD_METRIC_NAMES = ("mean_absolute_error", "relative_l2")
_STAGE_CHECKPOINT_PATTERN = re.compile(r"_stage(\d+)_checkpoint\.npz$")

CONFIGURATION_LABELS: dict[FactorizedFourierConfiguration, str] = {
    "explicit": "explicit stack",
    "explicit_matched": "explicit stack, matched params",
    "weight_tied": "weight-tied",
    "weight_tied_injected": "weight-tied, input-injected",
    "fixed_point": "fixed-point",
}


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


def Fresh_Flagship_Member(
    block: CubicBlock,
    task: FactorizedFourierTask = "localization",
    configuration: FactorizedFourierConfiguration = "explicit",
    hidden_channels: int = HIDDEN_CHANNELS,
    layer_count: int = LAYER_COUNT,
    kept_mode: int = KEPT_MODE,
) -> tuple[FactorizedFourier, ParameterSet]:
    """an untrained member built exactly as its own training driver builds it, and the flat set its checkpoint names"""
    training_identifiers = block.member_train
    reference_density, gram_mean, gram_scale = Input_Statistics(block, training_identifiers)
    target_scale = 1.0
    if task == "potential":
        scale_runs = [
            Loaded_Potential_Run(block, identifier) for identifier in training_identifiers[:RIDGE_TRAIN_RUN_COUNT]
        ]
        target_scale = Potential_Target_Scale(scale_runs)
    member = Factorized_Fourier_Network(
        hidden_channels=hidden_channels,
        kept_modes=(kept_mode, kept_mode, kept_mode),
        layer_count=layer_count,
        reference_density=reference_density,
        gram_mean=gram_mean,
        gram_scale=gram_scale,
        processing_shape=COARSE_SHAPE,
        seed=FLAGSHIP_SEED,
        configuration=configuration,
        task=task,
        target_scale=target_scale,
    )
    return member, ParameterSet(values=member.Parameter_Values())


def Load_Trained_Member(
    checkpoint_path: Path,
    block: CubicBlock,
    task: FactorizedFourierTask = "localization",
    configuration: FactorizedFourierConfiguration = "explicit",
    hidden_channels: int = HIDDEN_CHANNELS,
    layer_count: int = LAYER_COUNT,
    kept_mode: int = KEPT_MODE,
) -> tuple[FactorizedFourier, TrainingProgress]:
    """the member a finished or in-progress run produced, its best checkpoint parameters written back onto it"""
    member, parameters = Fresh_Flagship_Member(block, task, configuration, hidden_channels, layer_count, kept_mode)
    progress = Read_Checkpoint(checkpoint_path, parameters)
    Write_Back_Parameters(member, progress.best_parameters)
    return member, progress


def Elf_Evaluation_Rows(member: FactorizedFourier, block: CubicBlock) -> list[ScoredRun]:
    """the trained member's own predictions on the kill block, scored per spin in every card metric"""
    scored: list[ScoredRun] = []
    for identifier in block.evaluation:
        campaign = block.campaign_of[identifier]
        with np.load(Archive_Path(campaign, identifier)) as archive:
            input_function = Field_From_Archive(archive, ("charge_density", "magnetization_density"))
            if input_function is None:
                raise ValueError(f"{identifier} carries neither a charge density nor a magnetization")
            truths = {channel: np.asarray(archive[channel], dtype=np.float64) for channel in LOCALIZATION_CHANNELS}
        predicted = np.asarray(member(input_function, GridSpec(COARSE_SHAPE)).values, dtype=np.float64)
        functional = block.Functional_Of(identifier)
        for channel_index, channel in enumerate(LOCALIZATION_CHANNELS):
            scored.append(
                ScoredRun(
                    identifier=f"{identifier}_{channel}",
                    unit_key=block.unit_of[identifier],
                    campaign=campaign,
                    family=channel,
                    errors=Card_Metric_Errors(predicted[channel_index], truths[channel]),
                    covariate_values={"spin_channel": channel, "functional": functional},
                )
            )
    return scored


def Evaluation_Summaries(rows: list[ScoredRun], label: str) -> list[MetricSummary]:
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


def Elf_Ladder_Verdicts(
    member_rows: list[ScoredRun], ridge_rows: list[ScoredRun], mean_rows: list[ScoredRun], copy_rows: list[ScoredRun]
) -> tuple[FloorComparison, ...]:
    """the five pre-registered ladder levels, the floor block's own margins, measured against the member's rows"""
    return (
        Compare_To_Floor(
            member_rows, ridge_rows, "mean_absolute_error", "semilocal_ridge_floor", FLAGSHIP_KILL_MARGIN,
            "1_canon_kill",
        ),
        Compare_To_Floor(
            member_rows, ridge_rows, "mean_absolute_error", "semilocal_ridge_floor", PATTERN_RULE_MARGIN,
            "2_canon_pattern_rule",
        ),
        Compare_To_Floor(
            member_rows, mean_rows, "mean_absolute_error", "training_mean_trivial_floor", 0.0,
            "3_added_beat_training_mean_template",
        ),
        Compare_To_Floor(
            member_rows, copy_rows, "mean_absolute_error", "nearest_run_copy_floor", 0.0,
            "4_added_beat_nearest_run_copy",
        ),
        Compare_To_Floor(
            member_rows, mean_rows, "mean_absolute_error", "training_mean_trivial_floor", 0.5,
            "5_added_stretch_half_the_template",
        ),
    )


def Elf_Floor_Comparisons(
    member_rows: list[ScoredRun], floors: dict[str, list[ScoredRun]]
) -> tuple[FloorComparison, ...]:
    """the member against every floor, on the two lower-is-better card metrics, at zero required improvement"""
    return tuple(
        Compare_To_Floor(member_rows, floor_rows, metric_name, floor_name, 0.0)
        for floor_name, floor_rows in floors.items()
        for metric_name in COMPARABLE_CARD_METRIC_NAMES
    )


def Super_Resolution_Self_Consistency_Rows(member: FactorizedFourier, block: CubicBlock) -> list[ScoredRun]:
    """the same weights answering an 80-cubed grid directly, spectrally truncated to 40, against the plain answer"""
    scored: list[ScoredRun] = []
    for identifier in block.evaluation[::SUPER_RESOLUTION_SAMPLE_STRIDE]:
        campaign = block.campaign_of[identifier]
        with np.load(Archive_Path(campaign, identifier)) as archive:
            input_function = Field_From_Archive(archive, ("charge_density", "magnetization_density"))
        if input_function is None:
            raise ValueError(f"{identifier} carries neither a charge density nor a magnetization")
        coarse_predicted = np.asarray(member(input_function, GridSpec(COARSE_SHAPE)).values, dtype=np.float64)
        fine_predicted = np.asarray(member(input_function, GridSpec(FINE_SHAPE)).values, dtype=np.float64)
        fine_truncated = Spectral_Truncation_Resample(fine_predicted, COARSE_SHAPE)
        for channel_index, channel in enumerate(LOCALIZATION_CHANNELS):
            scored.append(
                ScoredRun(
                    identifier=f"{identifier}_{channel}",
                    unit_key=block.unit_of[identifier],
                    campaign=campaign,
                    family=channel,
                    errors=Card_Metric_Errors(fine_truncated[channel_index], coarse_predicted[channel_index]),
                    covariate_values={"spin_channel": channel},
                )
            )
    return scored


def Write_Elf_Figures(
    member: FactorizedFourier,
    member_rows: list[ScoredRun],
    floor_medians: dict[str, float],
    member_median: float,
    configuration: FactorizedFourierConfiguration = "explicit",
    cache_root: Path = ARRAY_CACHE_PATH,
    figures_root: Path = FIGURES_PATH,
) -> int:
    """the localization evaluation's whole visual surface, drawn from arrays cached under the given roots"""
    configuration_label = CONFIGURATION_LABELS[configuration]
    cache = cache_root / "fold_0" / configuration
    cache.mkdir(parents=True, exist_ok=True)
    inspected = {name: np.asarray(value, dtype=np.float64) for name, value in member.Inspect().items()}
    np.savez(cache / "inspection.npz", **cast(dict[str, Any], inspected))
    with np.load(cache / "inspection.npz") as archive:
        restored = {name: np.asarray(archive[name], dtype=np.float64) for name in archive.files}

    directory = figures_root / "fold_0" / configuration
    suite = Render_Inspection_Suite(
        restored, directory / "components", f"factorized_fourier electron localization fold 0 {configuration_label}"
    )
    if suite.skipped:
        raise ValueError(f"no renderer for {suite.skipped}, which means the suite is incomplete")

    ranked_rows = sorted(member_rows, key=lambda scored_row: scored_row.errors["relative_l2"])
    for rank, row in ((0, ranked_rows[0]), (-1, ranked_rows[-1])):
        base_identifier = row.identifier.removesuffix(f"_{row.family}")
        with np.load(Archive_Path(row.campaign, base_identifier)) as archive:
            truth = np.asarray(archive[row.family], dtype=np.float64)
            input_function = Field_From_Archive(archive, ("charge_density", "magnetization_density"))
        if input_function is None:
            raise ValueError(f"{base_identifier} carries neither a charge density nor a magnetization")
        predicted_channels = np.asarray(member(input_function, GridSpec(COARSE_SHAPE)).values, dtype=np.float64)
        channel_index = LOCALIZATION_CHANNELS.index(row.family)
        Render_Prediction_Against_Truth(
            predicted_channels[channel_index],
            truth,
            directory / f"prediction_{'best' if rank == 0 else 'worst'}.png",
            f"electron localization fold 0 {configuration_label} {'best' if rank == 0 else 'worst'} evaluation"
            f" run, {row.identifier}",
        )
    by_campaign: dict[str, list[float]] = {}
    for row in member_rows:
        by_campaign.setdefault(row.campaign, []).append(row.errors["relative_l2"])
    Render_Error_Spread(
        {name: np.asarray(values) for name, values in by_campaign.items()},
        directory / "error_by_campaign.png",
        f"electron localization fold 0 {configuration_label} evaluation error by campaign",
    )
    Render_Floor_Comparison(
        floor_medians,
        member_median,
        {name: 0.0 for name in floor_medians},
        directory / "floors.png",
        f"electron localization fold 0 {configuration_label} against its floors (relative L2; the ladder itself"
        " is absolute mean absolute error, tabulated separately)",
    )
    return len(suite.written) + 4


def Elf_Evaluation_Lines(
    run_name: str = ELF_EXPLICIT_RUN_NAME,
    artifact_directory: Path = TRAINING_ARTIFACT_PATH,
    configuration: FactorizedFourierConfiguration = "explicit",
    hidden_channels: int = HIDDEN_CHANNELS,
    layer_count: int = LAYER_COUNT,
    kept_mode: int = KEPT_MODE,
    cache_root: Path = ARRAY_CACHE_PATH,
    figures_root: Path = FIGURES_PATH,
) -> list[str]:
    """the member's own result once a checkpoint exists, floors through the alloy row, or a placeholder before one"""
    configuration_label = CONFIGURATION_LABELS[configuration]
    try:
        checkpoint_path = Latest_Stage_Checkpoint(artifact_directory, run_name)
    except FileNotFoundError:
        return [
            f"## The member's own result (electron localization, fold 0, {configuration_label})",
            "",
            f"Training is not yet run (no checkpoint for `{run_name}` under `{artifact_directory}` yet); this"
            " section fills in from `Elf_Evaluation_Lines` alone once one exists, no other change to this report"
            " needed.",
            "",
        ]

    block = CubicBlock()
    member, progress = Load_Trained_Member(
        checkpoint_path, block, "localization", configuration, hidden_channels, layer_count, kept_mode
    )
    member_rows = Elf_Evaluation_Rows(member, block)

    ridge_rows = Elf_Ridge_Rows(block)
    filter_rows = Shell_Filter_Rows(block)
    mean_rows = Training_Mean_Rows(block)
    copy_rows = Nearest_Run_Rows(block)
    floors = {
        "training_mean_trivial_floor": mean_rows,
        "nearest_run_copy_floor": copy_rows,
        "per_shell_linear_filter": filter_rows,
        "semilocal_ridge_floor": ridge_rows,
    }

    summaries = Evaluation_Summaries(member_rows, "member")
    ladder = Elf_Ladder_Verdicts(member_rows, ridge_rows, mean_rows, copy_rows)
    floor_comparisons = Elf_Floor_Comparisons(member_rows, floors)

    super_resolution_rows = Super_Resolution_Self_Consistency_Rows(member, block)
    super_resolution_summary = Summarize(super_resolution_rows, "relative_l2", "super_resolution_self_consistency")

    relative_l2_floor_medians = {name: Summarize(rows, "relative_l2", name).median for name, rows in floors.items()}
    relative_l2_member_median = Summarize(member_rows, "relative_l2", "member").median
    figures_written = Write_Elf_Figures(
        member, member_rows, relative_l2_floor_medians, relative_l2_member_median, configuration, cache_root,
        figures_root,
    )

    sampled_run_count = len(super_resolution_rows) // len(LOCALIZATION_CHANNELS)
    figures_directory = figures_root / "fold_0" / configuration
    cache_directory = cache_root / "fold_0" / configuration
    try:
        # a worktree's own absolute path is meaningless once this report is read from a different checkout
        figures_directory = figures_directory.relative_to(Path.cwd())
    except ValueError:
        pass
    def Named_Median(group_name: str, metric_name: str) -> float:
        """one already-computed summary's own median, read back by the exact group and metric it was filed under"""
        for summary in summaries:
            if summary.group_name == group_name and summary.metric_name == metric_name:
                return summary.median
        raise ValueError(f"no summary named {group_name!r} for {metric_name!r} among this member's own rows")

    copy_floor_mae = Summarize(copy_rows, "mean_absolute_error", "nearest_run_copy_floor").median
    defect_mae = Named_Median("member__defect_set", "mean_absolute_error")
    strain_mae = Named_Median("member__supercell_strains", "mean_absolute_error")
    defect_relative_l2 = Named_Median("member__defect_set", "relative_l2")
    strain_relative_l2 = Named_Median("member__supercell_strains", "relative_l2")
    mae_ratio = defect_mae / strain_mae if strain_mae > 0.0 else float("inf")
    relative_l2_ratio = defect_relative_l2 / strain_relative_l2 if strain_relative_l2 > 0.0 else float("inf")

    return [
        f"## The member's own result (electron localization, fold 0, {configuration_label})",
        "",
        f"Loaded from `{checkpoint_path.name}`: {progress.completed_steps} completed steps, best validation score"
        f" {progress.best_score:.6f} at step {progress.best_step}.",
        "",
        "### three caveats before trusting this number",
        "",
        "This is one seeded run (seed 20260912): no few-percent difference among these numbers is resolvable from"
        " a single run alone, since the seed sweep that would put a confidence band on the member itself is"
        " scheduled together with the rest of the deep-equilibrium ladder, not yet run.",
        "",
        "The block's geometries are near-identical within a campaign, which is why a verbatim copy of the nearest"
        f" training run already reaches a mean absolute error of {copy_floor_mae:.4f} without learning anything"
        f" (the nearest-run-copy floor, above), and why the strain rows read markedly better than the defect"
        f" rows: {mae_ratio:.1f}x lower mean absolute error ({strain_mae:.6f} against {defect_mae:.6f}) and"
        f" {relative_l2_ratio:.1f}x lower relative L2 ({100 * strain_relative_l2:.2f}% against"
        f" {100 * defect_relative_l2:.2f}%). The supercell strains are small, smooth perturbations of one lattice,"
        " so a near neighbor is nearly the true answer, while the defect campaign varies impurity species and"
        " site by run. The defect rows, not the pooled median, are this member's real test.",
        "",
        "An external calibration point, not a competitor: the 2026 hydrogen-ELF network's published error of"
        " 0.019 is the nearest number in the literature, but it answers a single-element system, an easier"
        " problem than this six-family cubic block, so it is a reference point for scale, not a benchmark this"
        " member is being measured against.",
        "",
        "### scored on the kill block (fold zero, both spins, every card metric, by campaign and by functional)",
        "",
        "```",
        Render_Table(Summary_Table(tuple(summaries))),
        "```",
        "",
        "### the pre-registered claim ladder, measured",
        "",
        "```",
        Render_Table(Comparison_Table(ladder)),
        "```",
        "",
        "### every floor, on the two lower-is-better card metrics, beaten or not",
        "",
        "Structural similarity is higher-is-better and is reported only as a summary above (median per group), not"
        " as a floor-comparison ratio: `Compare_To_Floor`'s improvement formula assumes a lower-is-better error,"
        " which mean absolute error and relative L2 are and structural similarity is not.",
        "",
        "```",
        Render_Table(Comparison_Table(floor_comparisons)),
        "```",
        "",
        "### super-resolution self-consistency",
        "",
        "The same trained weights, asked to answer directly on an 80³ grid rather than the 40³ grid they trained"
        " on, then spectrally truncated back to 40³, against the direct 40³ answer, on every"
        f" {SUPER_RESOLUTION_SAMPLE_STRIDE}th evaluation run ({sampled_run_count} runs, both spins): median"
        f" relative L2 **{100 * super_resolution_summary.median:.3f}%**. A small number here means the learned"
        " Fourier modes carry the same answer at a resolution the member never trained at, which is what makes"
        " the coarse-trunk design's answer at the fine grid (the potential task's own finish) trustworthy rather"
        " than a coincidence of the training resolution.",
        "",
        "### the alloy every-shape row",
        "",
        "Not applicable: the `alloy_ensemble` fold-zero archives checked all carry `has_localization: False` and"
        " non-cubic shapes (for example `(48, 96, 216)`); this campaign has no localization target for the member"
        " to be scored against, on any shape.",
        "",
        f"Figures: {figures_written} files written under `{figures_directory}`, arrays cached at"
        f" `{cache_directory}`.",
        "",
    ]


# the parametric variant (canon II.4): strain or lattice parameters broadcast into the same backbone, floors
# measured host-only against real charge-density fields before any member is built; the decisive one interpolates
# multilinearly between an interior level's own bracket corners, on the leave-one-level-out block Bracket_Corners
# and Interior_Levels (operators.factorized_fourier.parametric) name

STRAIN_ATLAS_CAMPAIGN = "strain_atlas"
STRAIN_ATLAS_COMMON_SHAPE = (40, 40, 40)


def Loaded_Strain_Charge_Density(
    run_path: str, shape: tuple[int, int, int] = STRAIN_ATLAS_COMMON_SHAPE
) -> NDArray[np.float64]:
    """one strain-atlas run's own charge density, resampled to the block's common shape (native shapes vary)"""
    identifier = Run_Identifier(run_path)
    with np.load(Archive_Path(STRAIN_ATLAS_CAMPAIGN, identifier)) as archive:
        density = np.asarray(archive["charge_density"], dtype=np.float64)
    return Spectral_Truncation_Resample(density[None], shape)[0]


def Cached_Level_Field(
    arm: Arm, level: Level, shape: tuple[int, int, int], cache: dict[tuple[str, Level], NDArray[np.float64]]
) -> NDArray[np.float64]:
    """one level's own mean charge density over every run sharing it, memoized since brackets share corners"""
    key = (arm.name, level)
    if key not in cache:
        fields = [Loaded_Strain_Charge_Density(run_path, shape) for run_path in arm.runs_by_level[level]]
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


def Strain_Bracketing_Floor_Rows(
    arms: tuple[Arm, ...], shape: tuple[int, int, int] = STRAIN_ATLAS_COMMON_SHAPE
) -> list[ScoredRun]:
    """the decisive floor: every interior level's own field against its bracket corners' multilinear interpolation"""
    cache: dict[tuple[str, Level], NDArray[np.float64]] = {}
    scored: list[ScoredRun] = []
    for arm in arms:
        for level, corners in Interior_Levels(arm).items():
            truth = Cached_Level_Field(arm, level, shape, cache)
            field_of_corner = {corner: Cached_Level_Field(arm, corner, shape, cache) for corner in corners}
            predicted = Multilinear_Interpolated_Field(level, corners, field_of_corner)
            scored.append(
                ScoredRun(
                    identifier=f"{arm.name}_{level}",
                    unit_key=f"{arm.name}_{level}",
                    campaign="strain_atlas",
                    family=arm.name,
                    errors=Card_Metric_Errors(predicted, truth),
                )
            )
    return scored


def Strain_Tensor_By_Run_Path() -> dict[str, NDArray[np.float64]]:
    """every strain-atlas run's own full six-component tensor, keyed by run path, off the cached assignment map"""
    return {
        assignment.run_path: np.asarray(assignment.tensor, dtype=np.float64)
        for assignment in Strain_Assignments_Of_Pool(POOL_ROOT)
    }


def Strain_Floor_Population(
    arms: tuple[Arm, ...], shape: tuple[int, int, int] = STRAIN_ATLAS_COMMON_SHAPE
) -> tuple[
    list[tuple[str, Level]], list[tuple[str, Level]], dict[tuple[str, Level], NDArray[np.float64]], dict[str, Arm]
]:
    """every (arm, level) split into training (every level with no full bracket) and evaluation (every interior one)"""
    arm_by_name = {arm.name: arm for arm in arms}
    cache: dict[tuple[str, Level], NDArray[np.float64]] = {}
    train_keys: list[tuple[str, Level]] = []
    eval_keys: list[tuple[str, Level]] = []
    for arm in arms:
        interior = Interior_Levels(arm)
        for level in arm.runs_by_level:
            Cached_Level_Field(arm, level, shape, cache)
            (eval_keys if level in interior else train_keys).append((arm.name, level))
    return sorted(train_keys), sorted(eval_keys), cache, arm_by_name


def Strain_Ridge_Nearest_Mean_Floor_Rows(
    arms: tuple[Arm, ...], shape: tuple[int, int, int] = STRAIN_ATLAS_COMMON_SHAPE, pod_rank: int = 32
) -> dict[str, list[ScoredRun]]:
    """the ridge-to-POD, nearest-copy and training-mean floors, fit on the boundary levels, scored on the interior"""
    tensor_of_run = Strain_Tensor_By_Run_Path()
    train_keys, eval_keys, field_of, arm_by_name = Strain_Floor_Population(arms, shape)

    def Representative_Tensor(arm_name: str, level: Level) -> NDArray[np.float64]:
        run_path = arm_by_name[arm_name].runs_by_level[level][0]
        return tensor_of_run[run_path]

    train_tensors = np.stack([Representative_Tensor(name, level) for name, level in train_keys])
    train_fields = np.stack([field_of[(name, level)] for name, level in train_keys])
    eval_tensors = np.stack([Representative_Tensor(name, level) for name, level in eval_keys])
    eval_fields = np.stack([field_of[(name, level)] for name, level in eval_keys])

    flat_train_fields = train_fields.reshape(train_fields.shape[0], -1)
    mean_field = train_fields.mean(axis=0)
    nearest_indices = Nearest_Training_Run(train_tensors, eval_tensors)
    pod_basis = Gram_Pod(flat_train_fields, rank=pod_rank)
    train_coefficients = Project(pod_basis, flat_train_fields)
    ridge = Fit_Standardized_Ridge(train_tensors, train_coefficients)
    predicted_coefficients = Apply_Standardized_Ridge(ridge, eval_tensors)
    ridge_flat_fields = Reconstruct(pod_basis, predicted_coefficients)

    mean_rows: list[ScoredRun] = []
    copy_rows: list[ScoredRun] = []
    ridge_rows: list[ScoredRun] = []
    for evaluation_position, (arm_name, level) in enumerate(eval_keys):
        truth = eval_fields[evaluation_position]
        identifier = f"{arm_name}_{level}"
        mean_rows.append(
            ScoredRun(
                identifier=identifier, unit_key=identifier, campaign=STRAIN_ATLAS_CAMPAIGN, family=arm_name,
                errors=Card_Metric_Errors(mean_field, truth),
            )
        )
        copy_rows.append(
            ScoredRun(
                identifier=identifier, unit_key=identifier, campaign=STRAIN_ATLAS_CAMPAIGN, family=arm_name,
                errors=Card_Metric_Errors(train_fields[nearest_indices[evaluation_position]], truth),
            )
        )
        ridge_rows.append(
            ScoredRun(
                identifier=identifier, unit_key=identifier, campaign=STRAIN_ATLAS_CAMPAIGN, family=arm_name,
                errors=Card_Metric_Errors(ridge_flat_fields[evaluation_position].reshape(shape), truth),
            )
        )
    return {
        "training_mean_trivial_floor": mean_rows,
        "nearest_run_copy_floor": copy_rows,
        "ridge_to_pod_32_floor": ridge_rows,
    }


STRAIN_DEVELOPMENT_TRAIN_ROLE = "train"

STRAIN_DEVELOPMENT_TEST_ROLE = "test"


@dataclasses.dataclass(frozen=True, slots=True)
class StrainDevelopmentBlock:
    """one holdout role's own runs at the campaign's common grid shape, everything else set aside"""

    parameters: NDArray[np.float64]
    fields: NDArray[np.float64]
    identifiers: list[str]
    unit_keys: list[str]
    families: list[str]


def Loaded_Strain_Development_Block(role: str) -> StrainDevelopmentBlock:
    """the committed strain_atlas_holdout split's own runs for one role, filtered to the block's common 40-cubed grid"""
    parameters: list[NDArray[np.float64]] = []
    fields: list[NDArray[np.float64]] = []
    identifiers: list[str] = []
    unit_keys: list[str] = []
    families: list[str] = []
    assignments = Strain_Assignments_By_Run()
    for example in Parameter_Field_Examples(Card_Named("strain_to_charge"), role):
        values = np.asarray(example.target_function.values, dtype=np.float64)
        if values.shape[1:] != STRAIN_ATLAS_COMMON_SHAPE:
            continue
        parameters.append(np.asarray(example.parameters.vector, dtype=np.float64))
        fields.append(values.reshape(-1))
        identifiers.append(example.identifier)
        unit_keys.append(example.unit_key)
        families.append(assignments[example.run_path].family)
    Guard_Fresh_Archives(identifiers)
    return StrainDevelopmentBlock(
        parameters=np.asarray(parameters), fields=np.asarray(fields), identifiers=identifiers,
        unit_keys=unit_keys, families=families,
    )


def Strain_Development_Floor_Rows(pod_rank: int = 32) -> dict[str, list[ScoredRun]]:
    """the same three floors, on the committed strain_atlas_holdout split rather than the leave-one-level-out one"""
    train = Loaded_Strain_Development_Block(STRAIN_DEVELOPMENT_TRAIN_ROLE)
    test = Loaded_Strain_Development_Block(STRAIN_DEVELOPMENT_TEST_ROLE)
    basis = Gram_Pod(train.fields, rank=pod_rank)
    ridge = Fit_Standardized_Ridge(train.parameters, Project(basis, train.fields))
    ridge_predicted = Reconstruct(basis, Apply_Standardized_Ridge(ridge, test.parameters))
    nearest = Nearest_Training_Run(train.parameters, test.parameters)
    mean_predicted = np.broadcast_to(train.fields.mean(axis=0), test.fields.shape)

    def Scored(predicted: NDArray[np.float64]) -> list[ScoredRun]:
        return [
            ScoredRun(
                identifier=test.identifiers[run],
                unit_key=test.unit_keys[run],
                campaign=STRAIN_ATLAS_CAMPAIGN,
                family=test.families[run],
                errors=Card_Metric_Errors(
                    predicted[run].reshape(STRAIN_ATLAS_COMMON_SHAPE),
                    test.fields[run].reshape(STRAIN_ATLAS_COMMON_SHAPE),
                ),
            )
            for run in range(test.fields.shape[0])
        ]

    return {
        "training_mean_trivial_floor": Scored(mean_predicted),
        "nearest_run_copy_floor": Scored(train.fields[nearest]),
        "ridge_to_pod_32_floor": Scored(ridge_predicted),
    }


def Parametric_Floor_Summaries(floors: dict[str, list[ScoredRun]]) -> list[MetricSummary]:
    """each floor's pooled median beside its own per-family breakdown, in the card's own three metrics"""
    summaries: list[MetricSummary] = []
    for floor_label, rows in floors.items():
        for metric_name in CARD_METRIC_NAMES:
            summaries.append(Summarize(rows, metric_name, floor_label))
            for family_summary in Summarize_By(rows, metric_name, "family"):
                summaries.append(
                    dataclasses.replace(family_summary, group_name=f"{floor_label}__{family_summary.group_name}")
                )
    return summaries


def Parametric_Task_Lines() -> list[str]:
    """the parametric variant (canon II.4), host-only: arms and levels, every floor, the pre-registered kill"""
    arms = All_Strain_Arms()
    bracketing_rows = Strain_Bracketing_Floor_Rows(arms)
    other_rows = Strain_Ridge_Nearest_Mean_Floor_Rows(arms)
    leave_one_level_out_floors = {"bracketing_interpolation_floor": bracketing_rows, **other_rows}
    development_floors = Strain_Development_Floor_Rows()

    leave_one_level_out_summaries = Parametric_Floor_Summaries(leave_one_level_out_floors)
    development_summaries = Parametric_Floor_Summaries(development_floors)

    pooled_medians = {
        floor_label: Summarize(rows, "relative_l2", floor_label).median
        for floor_label, rows in leave_one_level_out_floors.items()
    }
    best_floor_label = min(pooled_medians, key=lambda label: pooled_medians[label])
    best_floor_median = pooled_medians[best_floor_label]
    kill_bar = best_floor_median * (1.0 - 0.3)

    arm_lines: list[str] = []
    for arm in arms:
        interior_count = len(Interior_Levels(arm))
        run_count = sum(len(paths) for paths in arm.runs_by_level.values())
        arm_lines.append(
            f"- **{arm.name}**: {len(arm.runs_by_level)} levels ({interior_count} interior, held out one at a"
            f" time), {run_count} runs"
        )

    return [
        "## The parametric variant (canon II.4, `strain_to_charge`), host-only work",
        "",
        "Parameters (the six-component strain tensor) broadcast as constant channels into the same lift, plus"
        " periodic coordinate features of the requested grid's own fractional coordinates -- without the"
        " coordinate channels a spectral-plus-pointwise stack fed nothing but constants can only answer a"
        " constant field, proven directly in `Test_A_Constant_Only_Input_Can_Only_Answer_A_Constant_Field` and"
        " `Test_Coordinate_Features_Break_The_Constant_Output_Degeneracy_And_Answer_Any_Grid`. The same trained"
        " weights answer any grid shape because the coordinate channels are rebuilt for whatever shape is asked,"
        " never cached for one; `Test_The_Same_Parametric_Weights_Answer_Two_Different_Grids` checks this"
        " directly on the production member. The electron count rides in `__call__`'s own `condition` argument,"
        " unused by the other two tasks, exactly the seam `Conserving(law=\"renormalize_to_electron_count\")` was"
        " built for.",
        "",
        "### arms and levels",
        "",
        "An arm is one strain family; a level is that family's own swept parameter vector (one component for"
        " uniaxial, biaxial, isotropic and one-angle shear; two for two-angle shear; three for triaxial and"
        " three-angle shear, confirmed against the real census as genuine multi-dimensional grids rather than"
        " single-factor lines). `Bracket_Corners` generalizes bracketing interpolation to any dimension: every"
        " one of a level's 2^D corner combinations must itself be a real level, which refuses a bracket across a"
        " grid hole (two-angle and three-angle shear both have real holes) rather than assuming a complete"
        " factorial design.",
        "",
        *arm_lines,
        "",
        "### floors, leave-one-level-out block (every interior level held out, its own arm's boundary training it)",
        "",
        "```",
        Render_Table(Summary_Table(tuple(leave_one_level_out_summaries))),
        "```",
        "",
        "### floors, development block (the committed `strain_atlas_holdout` split, `operators.data`'s own)",
        "",
        "The same three floors (training mean, nearest-run copy, ridge to a rank-32 POD basis), recomputed on the"
        " already-committed train/test split rather than the leave-one-level-out one, reported beside it as a"
        " second, independent read of the same block:",
        "",
        "```",
        Render_Table(Summary_Table(tuple(development_summaries))),
        "```",
        "",
        "### the pre-registered kill, neither bar invented here",
        "",
        f"**Canon bar**: kill unless the member's own relative L2 is under 0.7x the best of these four floors on"
        f" the leave-one-level-out block. The strongest floor measured is **{best_floor_label}**, pooled median"
        f" relative L2 **{100 * best_floor_median:.3f}%** -- required absolute: **{100 * kill_bar:.3f}%**.",
        "",
        "**The honesty note, stated before any member is trained**: the canon's own text calls this pattern's"
        " gate case the weakest in the suite, and says plainly that a linear-interpolation floor winning on a"
        " smooth factorial sweep is the *expected*, reportable outcome, not a failure to bury. Bracketing"
        f" interpolation measures under {100 * best_floor_median:.2f}% relative L2 pooled, and under 0.21% on"
        " every single family's own median (triaxial, the largest and least smooth arm, is the worst case). A"
        " trained member clearing a bar this tight, on a physical regime this close to linear, would be the"
        " genuinely informative result; one that does not is exactly what the canon predicted and precisely why"
        " this member is worth building anyway -- the parametric task is the suite's honest admission that not"
        " every gate is won by the network.",
        "",
    ]


def Main() -> int:
    """the block, its floors, both ladders, the potential task's own floors and the member's own result, written"""
    floor_lines, bars = Floor_Block_Lines()
    evaluation_lines = Elf_Evaluation_Lines()
    deq_lines = Deep_Equilibrium_Ladder_Lines()
    potential_lines = Potential_Task_Lines()
    parametric_lines = Parametric_Task_Lines()
    header = [
        "# factorized_fourier — measured against its floors",
        "",
        "Regenerate with `python3 -m operators.factorized_fourier.report`.",
        "",
        "The block, all four floors and the pre-registered claim ladder below were measured before a single"
        " training step was taken, exactly as the doctrine asks. The member's own result, per-campaign and"
        " per-functional rows, the super-resolution self-consistency check and the figure suite follow once a"
        " checkpoint exists for it; until then that section says so plainly and nothing else about this command"
        " changes.",
        "",
    ]
    REPORT_PATH.write_text(
        "\n".join(header + floor_lines + evaluation_lines + deq_lines + potential_lines + parametric_lines) + "\n"
    )
    print(f"wrote {REPORT_PATH}")
    print(bars)
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
