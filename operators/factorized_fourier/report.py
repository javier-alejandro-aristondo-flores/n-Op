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
    ARTIFACT_DIRECTORY,
    Apply_Per_Shell_Filter,
    Archive_Path,
    Fit_Per_Shell_Filter,
    Guard_Fresh_Archives,
    Hartree_Potential,
    POOL_ROOT,
    Ridge_Apply,
    Ridge_Fit,
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
from operators.training import (
    BatchSource,
    Field_From_Archive,
    Read_Checkpoint,
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

    def Loss(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        example_count = lifted_batch["combined_coarse_input"].shape[0]
        total = 0.0
        for example_index in range(example_count):
            predicted = member.Forward_From_Coarse_Input(lifted, lifted_batch["combined_coarse_input"][example_index])
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
    step_count: int, run_name: str, configuration: FactorizedFourierConfiguration = "explicit"
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
        "rung                       | steps | wall_clock_s | peak_memory_MiB | convergence_rate | seed",
        "explicit (same width)      |   --  |     --       |       --        |  n/a (not iterative)  |  --",
        "explicit (matched params)  |   --  |     --       |       --        |  n/a (not iterative)  |  --",
        "weight_tied                |   --  |     --       |       --        |  n/a (not iterative)  |  --",
        "fixed_point                |   --  |     --       |       --        |          --           |  --",
        "```",
        "",
    ]


# the member's own result on the localization task: loaded from whichever checkpoint the training driver above
# has written, scored against every floor above, on the exact evaluation block the floors themselves were fit
# and measured against -- host-only, the numpy inference path, no engine and no accelerator needed to read it

ELF_EXPLICIT_RUN_NAME = "elf_fold0_explicit_35505"
SUPER_RESOLUTION_SAMPLE_STRIDE = 12
COMPARABLE_CARD_METRIC_NAMES = ("mean_absolute_error", "relative_l2")
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
    cache_root: Path = ARRAY_CACHE_PATH,
    figures_root: Path = FIGURES_PATH,
) -> int:
    """the localization evaluation's whole visual surface, drawn from arrays cached under the given roots"""
    cache = cache_root / "fold_0" / "explicit"
    cache.mkdir(parents=True, exist_ok=True)
    inspected = {name: np.asarray(value, dtype=np.float64) for name, value in member.Inspect().items()}
    np.savez(cache / "inspection.npz", **cast(dict[str, Any], inspected))
    with np.load(cache / "inspection.npz") as archive:
        restored = {name: np.asarray(archive[name], dtype=np.float64) for name in archive.files}

    directory = figures_root / "fold_0" / "explicit"
    suite = Render_Inspection_Suite(
        restored, directory / "components", "factorized_fourier electron localization fold 0 explicit"
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
            f"electron localization fold 0 explicit {'best' if rank == 0 else 'worst'} evaluation run,"
            f" {row.identifier}",
        )
    by_campaign: dict[str, list[float]] = {}
    for row in member_rows:
        by_campaign.setdefault(row.campaign, []).append(row.errors["relative_l2"])
    Render_Error_Spread(
        {name: np.asarray(values) for name, values in by_campaign.items()},
        directory / "error_by_campaign.png",
        "electron localization fold 0 explicit evaluation error by campaign",
    )
    Render_Floor_Comparison(
        floor_medians,
        member_median,
        {name: 0.0 for name in floor_medians},
        directory / "floors.png",
        "electron localization fold 0 explicit against its floors (relative L2; the ladder itself is absolute"
        " mean absolute error, tabulated separately)",
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
    try:
        checkpoint_path = Latest_Stage_Checkpoint(artifact_directory, run_name)
    except FileNotFoundError:
        return [
            "## The member's own result (electron localization, fold 0, explicit stack)",
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
        member, member_rows, relative_l2_floor_medians, relative_l2_member_median, cache_root, figures_root
    )

    sampled_run_count = len(super_resolution_rows) // len(LOCALIZATION_CHANNELS)
    figures_directory = figures_root / "fold_0" / "explicit"
    cache_directory = cache_root / "fold_0" / "explicit"
    try:
        # a worktree's own absolute path is meaningless once this report is read from a different checkout
        figures_directory = figures_directory.relative_to(Path.cwd())
    except ValueError:
        pass
    return [
        "## The member's own result (electron localization, fold 0, explicit stack)",
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
        " training run already reaches a mean absolute error of 0.0062 without learning anything (the"
        " nearest-run-copy floor, above), and why the strain rows read roughly ten times better than the defect"
        " rows (mean absolute error 0.000704 against 0.002329, relative L2 0.26% against 1.35%): the supercell"
        " strains are small, smooth perturbations of one lattice, so a near neighbor is nearly the true answer,"
        " while the defect campaign varies impurity species and site by run. The defect rows, not the pooled"
        " median, are this member's real test.",
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


def Main() -> int:
    """the block, its floors, both ladders, the potential task's own floors and the member's own result, written"""
    floor_lines, bars = Floor_Block_Lines()
    evaluation_lines = Elf_Evaluation_Lines()
    deq_lines = Deep_Equilibrium_Ladder_Lines()
    potential_lines = Potential_Task_Lines()
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
        "\n".join(header + floor_lines + evaluation_lines + deq_lines + potential_lines) + "\n"
    )
    print(f"wrote {REPORT_PATH}")
    print(bars)
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
