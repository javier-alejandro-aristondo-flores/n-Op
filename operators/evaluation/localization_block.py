"""the cubic block's identifiers, its per-run metric scorers, and every localization and potential floor"""

import dataclasses
import json

import numpy as np
from numpy.typing import NDArray

from operators.data import (
    Apply_Per_Shell_Filter,
    Archive_Path,
    ARTIFACT_DIRECTORY,
    Fit_Per_Shell_Filter,
    Guard_Fresh_Archives,
    Hartree_Potential,
    Ridge_Apply,
    Ridge_Fit,
    Semilocal_Xc_Ridge_Features,
    Spectral_Gradient_Magnitude_And_Laplacian,
)
from operators.evaluation.scoring import ScoredRun, Summarize
from operators.factorized_fourier import Log_Compressed_Channels, Reference_Density, Spin_Channels
from operators.framework import Spectral_Truncation_Resample
from operators.metrics import (
    Mean_Absolute_Error,
    Mean_Discrepancy,
    Mean_Removed_Mean_Absolute_Error,
    Mean_Removed_Relative_L2,
    Relative_L2,
    Structural_Similarity_3d,
)

CUBIC_CAMPAIGNS = ("supercell_strains", "defect_set")
COARSE_SHAPE = (40, 40, 40)
FINE_SHAPE = (80, 80, 80)
LOCALIZATION_CHANNELS = ("electron_localization_up", "electron_localization_down")
POTENTIAL_CHANNELS = ("local_potential_up", "local_potential_down")

# stage zero's own choices, kept here so the recomputed numbers reproduce them
RIDGE_TRAIN_RUN_COUNT = 80
FILTER_TRAIN_RUN_COUNT = 120
RIDGE_VOXELS_PER_RUN = 2000
RIDGE_SEED = 20260828

# the flagship's own bar (IMPLEMENTATION.md): half the floor's error or the member is killed
FLAGSHIP_KILL_MARGIN = 0.50

# the pattern rule (test-suite.md section 2): every member on this task must clear this margin or leave the task
PATTERN_RULE_MARGIN = 0.20


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
