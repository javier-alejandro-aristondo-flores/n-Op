"""the member measured against its floors, written as one committed markdown artifact"""

import dataclasses
import json
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from operators.data import (
    ARTIFACT_DIRECTORY,
    Apply_Per_Shell_Filter,
    Archive_Path,
    Fit_Per_Shell_Filter,
    Guard_Fresh_Archives,
    POOL_ROOT,
    Ridge_Apply,
    Ridge_Fit,
    Spectral_Gradient_Magnitude_And_Laplacian,
    STORE_NAME,
)
from operators.evaluation import MetricSummary, ScoredRun, Summarize, Summarize_By, Summary_Table
from operators.factorized_fourier import Log_Compressed_Channels, Reference_Density
from operators.framework import Spectral_Truncation_Resample
from operators.inspection import Render_Table
from operators.metrics import Mean_Absolute_Error, Relative_L2, Structural_Similarity_3d

REPORT_PATH = Path(__file__).parent / "report.md"
FIGURES_PATH = Path(__file__).parent / "figures"
# the inspection arrays are fields, and a field never leaves the pool -- only the drawing does
ARRAY_CACHE_PATH = POOL_ROOT / STORE_NAME / "_figures" / "factorized_fourier"
# checkpoints are scratch, not a corpus artifact, but they still hold no volumetric data either way
TRAINING_ARTIFACT_PATH = POOL_ROOT / STORE_NAME / "_training" / "factorized_fourier"

CUBIC_CAMPAIGNS = ("supercell_strains", "defect_set")
COARSE_SHAPE = (40, 40, 40)
LOCALIZATION_CHANNELS = ("electron_localization_up", "electron_localization_down")

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


def Fold_Membership() -> dict[str, tuple[int, str, str]]:
    """every cubic-campaign run identifier with its fold, campaign and owning split unit"""
    payload = json.loads((ARTIFACT_DIRECTORY / "paired_fields_fivefold.json").read_text())
    membership: dict[str, tuple[int, str, str]] = {}
    for unit_key, unit in payload.items():
        if unit["campaign"] not in CUBIC_CAMPAIGNS:
            continue
        for identifier in unit["run_identifiers"]:
            membership[identifier] = (int(unit["fold"]), str(unit["campaign"]), unit_key)
    return membership


class CubicBlock:
    """the kill block's identifiers, grouped by fold, campaign and split unit"""


    def __init__(self) -> None:
        membership = Fold_Membership()
        by_fold: dict[int, list[str]] = {fold: [] for fold in range(5)}
        campaign_of: dict[str, str] = {}
        unit_of: dict[str, str] = {}
        for identifier, (fold, campaign, unit_key) in membership.items():
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
        Guard_Fresh_Archives(identifier for fold_identifiers in by_fold.values() for identifier in fold_identifiers)
        self.by_fold = {fold: sorted(identifiers) for fold, identifiers in by_fold.items()}
        self.campaign_of = campaign_of
        self.unit_of = unit_of


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


def Main() -> int:
    """the block, its floors and the claim ladder, written as the report's first committed section"""
    lines, bars = Floor_Block_Lines()
    header = [
        "# factorized_fourier — measured against its floors",
        "",
        "Regenerate with `python3 -m operators.factorized_fourier.report`.",
        "",
        "Training is not yet run (the accelerator was held by another stream while this section was written);",
        "this first commit records the block, all four floors and the pre-registered claim ladder the member will",
        "be judged against, exactly as the doctrine asks for before a single training step is taken. The member's",
        "own result, the per-functional rows, the super-resolution self-consistency check and the figure suite",
        "land in a later commit once training has run.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(header + lines) + "\n")
    print(f"wrote {REPORT_PATH}")
    print(bars)
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
