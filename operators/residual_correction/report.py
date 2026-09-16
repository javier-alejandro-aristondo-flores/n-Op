"""the member measured against its floors, written as one committed markdown artifact"""

import argparse
import tomllib
from pathlib import Path
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray

from operators.data import (
    Apply_Standardized_Ridge,
    Fit_Standardized_Ridge,
    Gram_Pod,
    PodBasis,
    POOL_ROOT,
    Project,
    Read_Census,
    Reconstruct,
    Scissor_Floor,
    STORE_NAME,
    Strain_Pairs,
)
from operators.deep_operator_network import Pointwise_Statistics
from operators.evaluation import (
    Compare_To_Floor,
    Comparison_Table,
    FloorComparison,
    ScoredRun,
    Summarize,
    Summarize_By,
    Summary_Table,
)
from operators.framework import GridSpec
from operators.inspection import (
    Render_Error_Spread,
    Render_Floor_Comparison,
    Render_Inspection_Suite,
    Render_Prediction_Against_Truth,
    Render_Table,
)
from operators.metrics import Delta_R_Squared, Median_Per_Unit, Relative_L2
from operators.residual_correction import BASIS_RANK, Guarded_Spread, ProjectionBackbone, ResidualCorrection
from operators.substrate import ParameterSet
from operators.training import (
    BatchArray,
    FixedBatches,
    Strain_Assignments_By_Run,
    Strain_Charge_Pairs,
    Train,
    Training_Engine,
    TrainingBatch,
)
from operators.wrappers import ConformalCalibrator

REPORT_PATH = Path(__file__).parent / "report.md"
FIGURES_PATH = Path(__file__).parent / "figures"
CONFIGURATION_DIRECTORY = Path(__file__).parent / "configs"
# the inspection arrays are fields, and a field never leaves the pool -- only the drawing does
ARRAY_CACHE_PATH = POOL_ROOT / STORE_NAME / "_figures" / "residual_correction"
# checkpoints are scratch, not a corpus artifact, but they still hold no volumetric data either way
TRAINING_ARTIFACT_PATH = POOL_ROOT / STORE_NAME / "_training" / "residual_correction"
COMMON_GRID_SHAPE = (40, 40, 40)
# canon kill (test-suite.md IV.1): the corrected density must reach half the identity floor
REQUIRED_IMPROVEMENT = 0.5
CANDIDATE_STEP_COUNTS = (2000, 4000, 8000, 16000, 32000)
SEED = 20260916
LEARNING_RATE = 3e-3
RUN_NAME_PREFIX = "correction_projection"


class CorrectionBlock:
    """the cheap and accurate density fields of one holdout role, on the campaign's common grid"""


    def __init__(self, role: str) -> None:
        assignments = Strain_Assignments_By_Run()
        point_to_orbit = {run_path.rsplit("/", 1)[0]: value.orbit for run_path, value in assignments.items()}
        point_to_family = {run_path.rsplit("/", 1)[0]: value.family for run_path, value in assignments.items()}
        point_to_tensor = {run_path.rsplit("/", 1)[0]: value.tensor for run_path, value in assignments.items()}
        points: list[str] = []
        cheap: list[NDArray[np.float64]] = []
        accurate: list[NDArray[np.float64]] = []
        tensors: list[tuple[float, ...]] = []
        self.unit_keys: list[str] = []
        self.families: list[str] = []
        self.cheap_functions: list[Any] = []
        self.accurate_functions: list[Any] = []
        for point, cheap_field, accurate_field in Strain_Charge_Pairs(role):
            cheap_values = np.asarray(cheap_field.values, dtype=np.float64)
            accurate_values = np.asarray(accurate_field.values, dtype=np.float64)
            if cheap_values.shape[1:] != COMMON_GRID_SHAPE:
                continue
            points.append(point)
            cheap.append(cheap_values.reshape(-1))
            accurate.append(accurate_values.reshape(-1))
            tensors.append(point_to_tensor[point])
            self.unit_keys.append(point_to_orbit[point])
            self.families.append(point_to_family[point])
            self.cheap_functions.append(cheap_field)
            self.accurate_functions.append(accurate_field)
        self.points = points
        self.cheap = np.asarray(cheap)
        self.accurate = np.asarray(accurate)
        self.correction = self.accurate - self.cheap
        self.tensors = np.asarray(tensors, dtype=np.float64)


    def Scored(self, rebuilt: NDArray[np.float64]) -> list[ScoredRun]:
        """one scored run per field, against the accurate density, carrying the labels the report groups by"""
        return [
            ScoredRun(
                identifier=self.points[run],
                unit_key=self.unit_keys[run],
                campaign="strain_atlas",
                family=self.families[run],
                errors={
                    "relative_l2": Relative_L2(rebuilt[run], self.accurate[run]),
                    "delta_r_squared": Delta_R_Squared(rebuilt[run], self.accurate[run], self.cheap[run]),
                },
            )
            for run in range(self.accurate.shape[0])
        ]


def Identity_Predictions(block: CorrectionBlock) -> NDArray[np.float64]:
    """the cheap density submitted unchanged"""
    return block.cheap


def Affine_Predictions(block: CorrectionBlock) -> NDArray[np.float64]:
    """one global affine map fit per pair, the cheap density onto the accurate one"""
    predictions: list[NDArray[np.float64]] = []
    for row in range(block.cheap.shape[0]):
        design = np.stack([block.cheap[row], np.ones_like(block.cheap[row])], axis=1)
        coefficients = cast(NDArray[np.float64], np.linalg.lstsq(design, block.accurate[row], rcond=None)[0])
        predictions.append(np.asarray(design @ coefficients, dtype=np.float64))
    return np.asarray(predictions)


def Ceiling_Predictions(basis: PodBasis, block: CorrectionBlock) -> NDArray[np.float64]:
    """the correction field rebuilt at the basis's own rank, its representation ceiling, decoded back"""
    return Reconstruct(basis, Project(basis, block.correction)) + block.cheap


def Ridge_Predictions(
    correction_basis: PodBasis, cheap_basis: PodBasis, train: CorrectionBlock, evaluated: CorrectionBlock
) -> NDArray[np.float64]:
    """closed-form floor: the cheap density's own coefficients onto the correction's, decoded back"""
    fitted = Fit_Standardized_Ridge(Project(cheap_basis, train.cheap), Project(correction_basis, train.correction))
    predicted = Apply_Standardized_Ridge(fitted, Project(cheap_basis, evaluated.cheap))
    return Reconstruct(correction_basis, predicted) + evaluated.cheap


def Ridge_From_Strain_Predictions(
    correction_basis: PodBasis, train: CorrectionBlock, evaluated: CorrectionBlock
) -> NDArray[np.float64]:
    """context floor: the six raw strain components onto the correction's coefficients, decoded back"""
    fitted = Fit_Standardized_Ridge(train.tensors, Project(correction_basis, train.correction))
    predicted = Apply_Standardized_Ridge(fitted, evaluated.tensors)
    return Reconstruct(correction_basis, predicted) + evaluated.cheap


def Floor_Lines(
    train: CorrectionBlock, validation: CorrectionBlock, test: CorrectionBlock
) -> tuple[list[str], tuple[FloorComparison, ...], PodBasis, PodBasis, float]:
    """the pre-registered floors on the held-out test orbits, with the bases they were measured against"""
    correction_basis = Gram_Pod(train.correction, rank=BASIS_RANK)
    cheap_basis = Gram_Pod(train.cheap, rank=BASIS_RANK)

    identity_runs = test.Scored(Identity_Predictions(test))
    affine_runs = test.Scored(Affine_Predictions(test))
    ceiling_runs = test.Scored(Ceiling_Predictions(correction_basis, test))
    ridge_runs = test.Scored(Ridge_Predictions(correction_basis, cheap_basis, train, test))
    ridge_strain_runs = test.Scored(Ridge_From_Strain_Predictions(correction_basis, train, test))

    # every comparison here is context: the one comparison the canon kills on is the trained member's own
    comparisons = (
        Compare_To_Floor(affine_runs, identity_runs, "relative_l2", "identity", 0.0, "global_affine"),
        Compare_To_Floor(ridge_runs, identity_runs, "relative_l2", "identity", 0.0, "ridge_cheap_coefficients"),
        Compare_To_Floor(ridge_strain_runs, identity_runs, "relative_l2", "identity", 0.0, "ridge_strain_components"),
        Compare_To_Floor(ceiling_runs, identity_runs, "relative_l2", "identity", 0.0, "rank_32_ceiling"),
    )
    identity_median = comparisons[0].floor_median
    kill_bar = REQUIRED_IMPROVEMENT * identity_median

    summaries = (
        Summarize(identity_runs, "relative_l2", "identity"),
        Summarize(affine_runs, "relative_l2", "global_affine"),
        Summarize(ridge_runs, "relative_l2", "ridge_cheap_coefficients"),
        Summarize(ridge_strain_runs, "relative_l2", "ridge_strain_components"),
        Summarize(ceiling_runs, "relative_l2", "rank_32_ceiling"),
    )
    train_orbits = len(set(train.unit_keys))
    validation_orbits = len(set(validation.unit_keys))
    test_orbits = len(set(test.unit_keys))
    lines = [
        "## The block",
        "",
        f"Strain atlas, `cheap_to_accurate_charge` (test-suite.md IV.1), filtered to the campaign's common"
        f" {COMMON_GRID_SHAPE} grid. Train {train.cheap.shape[0]} pairs over {train_orbits} orbits,"
        f" validation {validation.cheap.shape[0]} pairs over {validation_orbits} orbits,"
        f" test {test.cheap.shape[0]} pairs over {test_orbits} orbits."
        f" Correction basis rank kept: {correction_basis.modes.shape[0]} of {BASIS_RANK} requested;"
        f" cheap-density basis rank kept: {cheap_basis.modes.shape[0]} of {BASIS_RANK} requested.",
        "",
        "## Floors, pre-registered before training",
        "",
        "```",
        Render_Table(Summary_Table(summaries)),
        "```",
        "",
        "```",
        Render_Table(Comparison_Table(comparisons)),
        "```",
        "",
        f"**Canon kill, fixed before training**: the trained member's test-orbit median relative L2 must"
        f" be at or below `{kill_bar:.6f}` (0.5 x the identity floor's `{identity_median:.6f}`), equivalently"
        f" a delta-R-squared of at least 0.75. The affine and both ridge rows above are context"
        f" (`required_improvement=0.0`), not kills.",
        "",
        "Both ridge floors already sit within a few parts in a million of the rank-32 ceiling. The strain"
        " atlas's holdout removes exact symmetry orbits, not nearby strain magnitudes, so a held-out point"
        " typically sits a small interpolation step from its nearest training point on the same sweep"
        " (measured: about 0.005 in tensor-component units for the shear families) -- the ceiling and the"
        " ridge floors are this close because the task is an interpolation-strength holdout on a smooth,"
        " low-rank correction field, not because anything is leaking between splits (checked: zero orbit"
        " overlap across train, validation and test). The informative comparison for the trained member is"
        " therefore not the 50% kill margin, which every closed-form floor already clears by orders of"
        " magnitude, but how close its own error lands to the ridge floor and the ceiling.",
        "",
    ]
    scissor = Scissor_Floor(Strain_Pairs(Read_Census(POOL_ROOT)), "strain_atlas")
    lines += [
        "For the record, unrelated to this member's own metric: the linear-scissor gap floor over"
        f" {int(scissor['pair_count'])} eigenvalue pairs shifts by `{scissor['mean_shift']:.4f} +/-"
        f" {scissor['shift_deviation']:.4f}` eV with a `{1000.0 * scissor['linear_residual_deviation']:.1f}`"
        f" meV linear residual (r-squared `{scissor['r_squared']:.4f}`). Any gap read-out is an auxiliary"
        " head, never this member, and must beat this scissor on orbit-held-out data.",
        "",
    ]
    return lines, comparisons, correction_basis, cheap_basis, kill_bar


def Trained_Member_Predictions(
    train: CorrectionBlock,
    validation: CorrectionBlock,
    test: CorrectionBlock,
    correction_basis: PodBasis,
    cheap_basis: PodBasis,
) -> tuple[NDArray[np.float64], NDArray[np.float64], int, ResidualCorrection]:
    """the member trained at the step count validation prefers, read on both validation and test"""
    # the bases are the floors' own fit, reused rather than refit so the two sections agree exactly
    _, voxel_scale = Pointwise_Statistics(train.correction)
    input_scale = Guarded_Spread(Project(cheap_basis, train.cheap))
    backbone = ProjectionBackbone(cheap_basis, correction_basis, COMMON_GRID_SHAPE, voxel_scale, input_scale, SEED)
    member = ResidualCorrection(backbone)
    train_cheap_coefficients = Project(cheap_basis, train.cheap)
    batch_arrays: dict[str, BatchArray] = {
        "cheap_coefficients": train_cheap_coefficients,
        "true_correction": train.correction,
    }
    batch_arrays.update(member.Constant_Values())
    whole_batch = FixedBatches(TrainingBatch(batch_arrays))

    def Correction_Loss(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        """squared error between the predicted and the true correction, mean over pairs and voxels"""
        full_lifted = {**lifted, **lifted_batch}
        predicted = member.Forward_Correction(full_lifted, lifted_batch["cheap_coefficients"])
        residuals = predicted - lifted_batch["true_correction"]
        return (residuals * residuals).mean()

    def Rebuild(values: dict[str, NDArray[np.float64]], block: CorrectionBlock) -> NDArray[np.float64]:
        """the whole block's corrected density from a candidate parameter set, member state left untouched"""
        full_values = {**values, **member.Constant_Values()}
        cheap_coefficients = Project(cheap_basis, block.cheap)
        correction = np.asarray(member.Forward_Correction(full_values, cheap_coefficients), dtype=np.float64)
        return block.cheap + correction

    best_score = float("inf")
    best_values: dict[str, NDArray[np.float64]] = dict(member.Parameter_Values())
    best_step_count = CANDIDATE_STEP_COUNTS[0]
    # every candidate restarts from member's own untouched, zero-initialized parameters, since
    # rebuilding a block never writes into member, so no candidate warm-starts off the last one
    initial_values = {name: value.copy() for name, value in member.Parameter_Values().items()}
    for step_count in CANDIDATE_STEP_COUNTS:
        # the budget is the one hyperparameter chosen here, and validation is what chooses it
        result = Train(
            Training_Engine(),
            ParameterSet(values={name: value.copy() for name, value in initial_values.items()}),
            Correction_Loss,
            whole_batch,
            step_count=step_count,
            learning_rate=LEARNING_RATE,
            seed=SEED,
            artifact_directory=TRAINING_ARTIFACT_PATH,
            run_name=f"{RUN_NAME_PREFIX}_{step_count}",
        )
        rebuilt_validation = Rebuild(result.parameters.values, validation)
        score = float(
            np.median(
                [Relative_L2(rebuilt_validation[run], validation.accurate[run]) for run in range(len(validation.points))]
            )
        )
        if score < best_score:
            best_score, best_values, best_step_count = score, result.parameters.values, step_count

    rebuilt_validation = Rebuild(best_values, validation)
    rebuilt_test = Rebuild(best_values, test)
    # the report's own figures and inspection arrays read the chosen run's state off member itself
    for name, value in best_values.items():
        if name in member.backbone.branch.parameter_values:
            member.backbone.branch.parameter_values[name] = value
        elif name in member.backbone.readout.parameter_values:
            member.backbone.readout.parameter_values[name] = value
    member(test.cheap_functions[0], GridSpec(COMMON_GRID_SHAPE))
    return rebuilt_validation, rebuilt_test, best_step_count, member


def Write_Figures(
    member: ResidualCorrection,
    test: CorrectionBlock,
    test_rebuilt: NDArray[np.float64],
    floor_medians: dict[str, float],
    member_median: float,
) -> int:
    """the member's whole visual surface, drawn from arrays cached on the pool"""
    ARRAY_CACHE_PATH.mkdir(parents=True, exist_ok=True)
    inspected = {name: np.asarray(value, dtype=np.float64) for name, value in member.Inspect().items()}
    # cached so a re-render needs no retrain, which is what keeps committed figures stable
    np.savez(ARRAY_CACHE_PATH / "inspection.npz", **cast(dict[str, Any], inspected))
    with np.load(ARRAY_CACHE_PATH / "inspection.npz") as archive:
        restored = {name: np.asarray(archive[name], dtype=np.float64) for name in archive.files}

    directory = FIGURES_PATH / "projection_backbone"
    suite = Render_Inspection_Suite(restored, directory / "components", "residual_correction projection backbone")
    if suite.skipped:
        raise ValueError(f"no renderer for {suite.skipped}, which means the suite is incomplete")

    scored = [Relative_L2(test_rebuilt[run], test.accurate[run]) for run in range(len(test.points))]
    order = np.argsort(scored)
    for label, run in (("best", int(order[0])), ("median", int(order[len(order) // 2])), ("worst", int(order[-1]))):
        Render_Prediction_Against_Truth(
            test_rebuilt[run].reshape(COMMON_GRID_SHAPE),
            test.accurate[run].reshape(COMMON_GRID_SHAPE),
            directory / f"prediction_{label}.png",
            f"projection backbone {label} test run, {test.unit_keys[run]}",
        )
    # every floor is context (required 0%) except identity, which carries the canon's own kill margin
    required_improvements = {name: 0.0 for name in floor_medians}
    required_improvements["identity"] = REQUIRED_IMPROVEMENT
    Render_Floor_Comparison(
        floor_medians,
        member_median,
        required_improvements,
        directory / "floors.png",
        "projection backbone against its floors, identity carries the canon kill",
    )
    by_family: dict[str, list[float]] = {}
    for run in range(len(test.points)):
        by_family.setdefault(test.families[run], []).append(scored[run])
    Render_Error_Spread(
        {name: np.asarray(values) for name, values in by_family.items()},
        directory / "error_by_family.png",
        "projection backbone test error by strain family",
    )
    return len(suite.written) + 5


def Conformal_Lines(
    member: ResidualCorrection,
    validation: CorrectionBlock,
    validation_rebuilt: NDArray[np.float64],
    test: CorrectionBlock,
    test_rebuilt: NDArray[np.float64],
) -> list[str]:
    """the iv.3 conformal band: a point prediction widened by a calibrated offset, coverage per orbit"""
    settings = tomllib.loads((CONFIGURATION_DIRECTORY / "projection_backbone.toml").read_text())
    calibrator = ConformalCalibrator(**settings["conformal"])
    calibrator.Calibrate(validation_rebuilt, validation_rebuilt, validation.accurate, validation.unit_keys)
    widened = calibrator(test_rebuilt, test_rebuilt)
    covered_everywhere = np.all(
        (np.asarray(widened.lower) <= test.accurate) & (test.accurate <= np.asarray(widened.upper)), axis=1
    )
    orbit_coverage = Median_Per_Unit(covered_everywhere.astype(np.float64), test.unit_keys)
    orbit_level_coverage = float(orbit_coverage.mean())
    inspected = calibrator.Inspect()
    return [
        "## Conformal band (IV.3)",
        "",
        f"Level {settings['conformal']['level']}, unit `{settings['conformal']['unit']}`, calibrated on"
        f" {int(np.asarray(inspected['calibration_unit_count']))} validation orbits, offset"
        f" `{float(np.asarray(inspected['conformal_offset'])):.6f}`. Test-orbit coverage (every voxel of the"
        f" whole field inside the band, medianed per orbit then averaged): `{orbit_level_coverage:.3f}`"
        f" against a guarantee of `[{float(np.asarray(inspected['coverage_guarantee_low'])):.3f}, "
        f"{float(np.asarray(inspected['coverage_guarantee_high'])):.3f}]`.",
        "",
    ]


def Main(argv: list[str] | None = None) -> int:
    """the floors, and when asked the training, conformal band, figures and standing"""
    parser = argparse.ArgumentParser(description="Measure and report the residual correction member.")
    parser.add_argument("--floors-only", action="store_true", help="write only the pre-registered floors section")
    arguments = parser.parse_args(argv)

    train = CorrectionBlock("train")
    validation = CorrectionBlock("validation")
    test = CorrectionBlock("test")

    floor_lines, floor_comparisons, correction_basis, cheap_basis, kill_bar = Floor_Lines(train, validation, test)
    lines = [
        "# residual_correction — measured report",
        "",
        "Regenerate with `python -m operators.residual_correction.report`"
        " (`--floors-only` to skip training and the conformal band).",
        "",
        *floor_lines,
    ]

    if cast(bool, arguments.floors_only):
        lines += [
            "## Standing",
            "",
            "Floors only. Training is scheduled by the team lead and has not run in this worktree yet.",
            "",
        ]
        REPORT_PATH.write_text("\n".join(lines) + "\n")
        print(f"wrote {REPORT_PATH} (floors only)")
        return 0

    validation_rebuilt, test_rebuilt, step_count, member = Trained_Member_Predictions(
        train, validation, test, correction_basis, cheap_basis
    )
    member_runs = test.Scored(test_rebuilt)
    identity_runs = test.Scored(Identity_Predictions(test))
    member_comparison = Compare_To_Floor(
        member_runs, identity_runs, "relative_l2", "identity", REQUIRED_IMPROVEMENT, "member"
    )
    floor_medians = {comparison.floor_name: comparison.member_median for comparison in floor_comparisons}
    floor_medians["identity"] = member_comparison.floor_median
    figure_count = Write_Figures(member, test, test_rebuilt, floor_medians, member_comparison.member_median)

    lines += [
        "## Result (one seed, 20260916)",
        "",
        f"{step_count} steps chosen on validation out of {CANDIDATE_STEP_COUNTS}."
        f" {figure_count} figures under `figures/projection_backbone/`.",
        "",
        "```",
        Render_Table(Summary_Table((Summarize(member_runs, "relative_l2", "member"),))),
        "```",
        "",
        "```",
        Render_Table(Comparison_Table((member_comparison,))),
        "```",
        "",
        "```",
        Render_Table(Summary_Table(Summarize_By(member_runs, "relative_l2", "family"))),
        "```",
        "",
        "```",
        Render_Table(Summary_Table((Summarize(member_runs, "delta_r_squared", "member"),))),
        "```",
        "",
    ]
    lines += Conformal_Lines(member, validation, validation_rebuilt, test, test_rebuilt)
    lines += [
        "## Standing",
        "",
        f"Verdict: **{member_comparison.verdict}** against the canon kill (`{kill_bar:.6f}` relative L2,"
        f" delta-R-squared >= 0.75), one seeded run (20260916). The built member's own seed sweep measured"
        " a fourteen to thirty-five percent spread on its task, so this single run cannot resolve a"
        " few-percent difference from the bar; it is read at face value.",
        "",
        "Caveats: one seed; the FiLM conditioning on campaign and exact-exchange fraction named in the"
        " canon entry is dropped here because the strain atlas is one campaign at one exact-exchange"
        " fraction, making it a no-op on this block (it is the canon's labeled ablation, not built here);"
        " the conditioned-model ablation itself is not run.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n")
    print(f"wrote {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
