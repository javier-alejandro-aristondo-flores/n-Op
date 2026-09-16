"""the result rows a member reports, and the floor verdicts they carry"""

import re
from pathlib import Path

import numpy as np
import pytest

from operators.evaluation import (
    Block_Signature,
    Card_Metric_Errors,
    Compare_To_Floor,
    Comparison_Table,
    Cross_Member_Table,
    CubicBlock,
    EXTRAPOLATION,
    FloorComparison,
    Label_Of,
    MemberResults,
    Member_Results_Path,
    MetricSummary,
    PEROVSKITE_DEVELOP_FOLD,
    Perovskite_Angle_Examples,
    PerovskiteAngleBlock,
    Perovskite_Nearest_Neighbor_Predictions,
    Potential_Floor_Rows,
    Potential_Metric_Errors,
    Read_Member_Results,
    Recorded_Bars,
    ResultKey,
    ResultRow,
    ScoredRun,
    Summarize,
    Summarize_By,
    Summary_Table,
    Truncation_Ceiling_Rows,
    Unit_Medians,
    VerdictRow,
    Write_Member_Results,
)
from operators.compositions import Spectral_Resampled
from operators.framework import Spectral_Truncation_Resample
from operators.inspection import Render_Table


def Run(identifier: str, unit_key: str, error: float, **labels: str) -> ScoredRun:
    """one scored run with the labels a test cares about and defaults for the rest"""
    return ScoredRun(
        identifier=identifier,
        unit_key=unit_key,
        campaign=labels.get("campaign", "strain_atlas"),
        family=labels.get("family", "uniaxial"),
        errors={"relative_l2": error},
        covariate_values={"functional": labels.get("functional", "cheap")},
        extrapolation=labels.get("extrapolation", "interpolation"),
    )


def Test_Runs_Inside_One_Unit_Count_Once() -> None:
    """an orbit of symmetry copies weighs the same as an orbit of one, not four times as much"""
    crowded = [Run(f"crowded_{copy}", "orbit_a", 0.10) for copy in range(9)]
    lone = [Run("lone", "orbit_b", 0.20)]
    unit_medians = Unit_Medians(crowded + lone, "relative_l2")
    assert unit_medians.shape == (2,)
    assert np.allclose(sorted(unit_medians), [0.10, 0.20])
    # the run-level median would have been 0.10, the unit-level one sits between the two orbits
    summary = Summarize(crowded + lone, "relative_l2")
    assert abs(summary.median - 0.15) < 1e-12
    assert summary.unit_count == 2
    assert summary.run_count == 10


def Test_A_Summary_Carries_Its_Unit_Count_Beside_The_Aggregate() -> None:
    """the suite requires the test-unit count on every reported number"""
    runs = [Run(f"run_{place}", f"orbit_{place // 2}", 0.05 + 0.01 * place) for place in range(8)]
    summary = Summarize(runs, "relative_l2")
    assert summary.unit_count == 4
    assert summary.run_count == 8
    assert summary.confidence_low <= summary.median <= summary.confidence_high


def Test_Summaries_Split_By_Any_Label() -> None:
    """campaign, family, functional and the extrapolation label all group the same rows"""
    runs = [
        Run("a", "orbit_a", 0.1, functional="cheap", family="uniaxial"),
        Run("b", "orbit_b", 0.3, functional="accurate", family="uniaxial"),
        Run("c", "orbit_c", 0.5, functional="cheap", family="biaxial", extrapolation=EXTRAPOLATION),
    ]
    by_functional = Summarize_By(runs, "relative_l2", "functional")
    assert tuple(summary.group_name for summary in by_functional) == ("accurate", "cheap")
    by_family = Summarize_By(runs, "relative_l2", "family")
    assert tuple(summary.group_name for summary in by_family) == ("biaxial", "uniaxial")
    by_reach = Summarize_By(runs, "relative_l2", "extrapolation")
    assert tuple(summary.group_name for summary in by_reach) == ("extrapolation", "interpolation")


def Test_An_Unknown_Label_Is_An_Error_Not_An_Empty_Group() -> None:
    """asking to group by something no run carries is a mistake, never a silent nothing"""
    with pytest.raises(ValueError):
        Label_Of(Run("a", "orbit_a", 0.1), "temperature")


def Test_The_Floor_Comparison_Applies_The_Suites_Margin() -> None:
    """a member must clear the stated fraction, and sitting exactly on it counts as clearing"""
    floor = [Run("a", "orbit_a", 0.4), Run("b", "orbit_b", 0.4)]
    exactly_at_the_margin = [Run("a", "orbit_a", 0.3), Run("b", "orbit_b", 0.3)]
    just_short = [Run("a", "orbit_a", 0.31), Run("b", "orbit_b", 0.31)]
    passing = Compare_To_Floor(exactly_at_the_margin, floor, "relative_l2", "ridge", 0.25)
    failing = Compare_To_Floor(just_short, floor, "relative_l2", "ridge", 0.25)
    assert abs(passing.improvement - 0.25) < 1e-12
    assert passing.verdict == "pass"
    assert failing.verdict == "kill"


def Test_A_Doubling_Margin_Reads_As_Half_The_Error() -> None:
    """the nearest-neighbor floor asks for a factor of two, which is a 50 percent improvement"""
    floor = [Run("a", "orbit_a", 1.0)]
    twice_as_good = [Run("a", "orbit_a", 0.5)]
    comparison = Compare_To_Floor(twice_as_good, floor, "relative_l2", "nearest_neighbor", 0.5)
    assert comparison.verdict == "pass"
    assert abs(comparison.improvement - 0.5) < 1e-12


def Test_The_Tables_Render_Without_Losing_A_Column() -> None:
    """both table shapes reach the plain-text renderer with every field named"""
    runs = [Run("a", "orbit_a", 0.1), Run("b", "orbit_b", 0.2)]
    summary_rows = Summary_Table((Summarize(runs, "relative_l2"),))
    comparison_rows = Comparison_Table(
        (Compare_To_Floor(runs, [Run("a", "orbit_a", 0.4)], "relative_l2", "ridge", 0.25),)
    )
    for rows, expected in ((summary_rows, "units"), (comparison_rows, "verdict")):
        rendered = Render_Table(rows)
        assert expected in rendered
        assert len(rendered.splitlines()) >= 2


@pytest.mark.pool
def Test_The_Promoted_Localization_Block_Names_Answer_From_The_Root_And_Partition_The_Folds() -> None:
    """the flagship's kill block and its floors now live here, reachable from the package root, folds intact"""
    assert isinstance(CubicBlock, type)
    for promoted_scorer in (Card_Metric_Errors, Potential_Metric_Errors, Recorded_Bars, Truncation_Ceiling_Rows):
        assert callable(promoted_scorer)
    assert callable(Potential_Floor_Rows)

    block = CubicBlock()
    evaluation_identifiers = set(block.evaluation)
    validation_identifiers = set(block.validation)
    member_train_identifiers = set(block.member_train)
    # the kill block, the member's own early-stopping fold and its three training folds never share a run
    assert evaluation_identifiers.isdisjoint(validation_identifiers)
    assert evaluation_identifiers.isdisjoint(member_train_identifiers)
    assert validation_identifiers.isdisjoint(member_train_identifiers)
    every_identifier = {identifier for fold_identifiers in block.by_fold.values() for identifier in fold_identifiers}
    assert evaluation_identifiers | validation_identifiers | member_train_identifiers == every_identifier
    # fold zero is the kill block by definition, not by coincidence of construction order
    assert evaluation_identifiers == set(block.by_fold[0])
    assert evaluation_identifiers


@pytest.mark.pool
def Test_The_Promoted_Perovskite_Block_Reproduces_Its_Own_Copy_Floor() -> None:
    """the angle stratum's memorization floor, computed through the promoted names, lands on the page's own number"""
    train = PerovskiteAngleBlock(Perovskite_Angle_Examples("train", PEROVSKITE_DEVELOP_FOLD, None))
    evaluated = PerovskiteAngleBlock(Perovskite_Angle_Examples("evaluation", PEROVSKITE_DEVELOP_FOLD, None))
    assert train.fields.shape[0] == 100
    assert evaluated.fields.shape[0] == 25
    copy_runs = evaluated.Scored(Perovskite_Nearest_Neighbor_Predictions(train, evaluated))
    summary = Summarize(copy_runs, "relative_l2")
    assert f"{summary.median:.4f}" == "0.0853"


def Synthetic_Member_Results(unit_keys: tuple[str, ...]) -> MemberResults:
    """one small, hand-built results artifact, its own summary and comparison both clean decimal numbers"""
    key = ResultKey(
        member="factorized_fourier",
        configuration="explicit",
        task="charge_to_localization",
        split="paired_fields_fivefold",
        block="fold_0",
        group="all",
    )
    summary = MetricSummary(
        metric_name="relative_l2",
        group_name="all",
        unit_count=2,
        run_count=4,
        median=0.125,
        interquartile=0.05,
        confidence_low=0.1,
        confidence_high=0.15,
    )
    comparison = FloorComparison(
        floor_name="semilocal_ridge_floor",
        metric_name="relative_l2",
        group_name="all",
        floor_median=0.25,
        member_median=0.125,
        required_improvement=0.5,
        improvement=0.5,
        verdict="pass",
    )
    return MemberResults(
        member="factorized_fourier",
        regenerate="python -m operators.factorized_fourier.report",
        rows=(ResultRow(key=key, summary=summary, block_signature=Block_Signature(unit_keys)),),
        verdicts=(VerdictRow(key=key, comparison=comparison),),
    )


def Test_Member_Results_Round_Trip_Through_Json(tmp_path: Path) -> None:
    """a written artifact reads back with every row, verdict and key exactly reproduced"""
    results = Synthetic_Member_Results(("orbit_a", "orbit_b"))
    path = tmp_path / "results.json"
    Write_Member_Results(path, results)
    assert Read_Member_Results(path) == results


def Test_Block_Signatures_Agree_Only_When_The_Unit_Keys_Agree(tmp_path: Path) -> None:
    """two artifacts share a signature exactly when their own unit keys are the same set, order aside"""
    same_order = Synthetic_Member_Results(("orbit_a", "orbit_b"))
    reordered = Synthetic_Member_Results(("orbit_b", "orbit_a"))
    different = Synthetic_Member_Results(("orbit_a", "orbit_c"))

    same_order_path = tmp_path / "same_order.json"
    reordered_path = tmp_path / "reordered.json"
    different_path = tmp_path / "different.json"
    Write_Member_Results(same_order_path, same_order)
    Write_Member_Results(reordered_path, reordered)
    Write_Member_Results(different_path, different)

    same_order_signature = Read_Member_Results(same_order_path).rows[0].block_signature
    reordered_signature = Read_Member_Results(reordered_path).rows[0].block_signature
    different_signature = Read_Member_Results(different_path).rows[0].block_signature
    assert same_order_signature == reordered_signature
    assert same_order_signature != different_signature


def Synthetic_Cross_Member_Results(member: str, task: str, split: str, signature: str, median: float) -> MemberResults:
    """one small, hand-built artifact for one member on one task, its own summary and verdict clean decimals"""
    key = ResultKey(member=member, configuration="explicit", task=task, split=split, block="fold_0", group="all")
    summary = MetricSummary(
        metric_name="relative_l2",
        group_name="all",
        unit_count=2,
        run_count=4,
        median=median,
        interquartile=0.01,
        confidence_low=median - 0.01,
        confidence_high=median + 0.01,
    )
    comparison = FloorComparison(
        floor_name="ridge_floor",
        metric_name="relative_l2",
        group_name="all",
        floor_median=0.5,
        member_median=median,
        required_improvement=0.25,
        improvement=0.5,
        verdict="pass",
    )
    return MemberResults(
        member=member,
        regenerate=f"python -m operators.{member}.report",
        rows=(ResultRow(key=key, summary=summary, block_signature=signature),),
        verdicts=(VerdictRow(key=key, comparison=comparison),),
    )


def Test_Agreeing_Artifacts_Render_One_Table_Per_Task() -> None:
    """two members that agree on split and unit signature render side by side under their shared task"""
    first = Synthetic_Cross_Member_Results(
        "factorized_fourier", "charge_to_localization", "paired_fields_fivefold", "sig_a", 0.1
    )
    second = Synthetic_Cross_Member_Results(
        "alias_free_convolutional", "charge_to_localization", "paired_fields_fivefold", "sig_a", 0.2
    )
    rendered = Cross_Member_Table((first, second))
    assert "charge_to_localization" in rendered
    assert "factorized_fourier" in rendered
    assert "alias_free_convolutional" in rendered


def Test_A_Split_Mismatch_Refuses() -> None:
    """a row whose split differs from its own task card's split is refused, never silently rendered"""
    wrong_split = Synthetic_Cross_Member_Results(
        "factorized_fourier", "charge_to_localization", "not_the_cards_split", "sig_a", 0.1
    )
    with pytest.raises(ValueError):
        Cross_Member_Table((wrong_split,))


def Test_A_Signature_Mismatch_Refuses() -> None:
    """two members scored on different unit sets for the same task are refused, never averaged together"""
    first = Synthetic_Cross_Member_Results(
        "factorized_fourier", "charge_to_localization", "paired_fields_fivefold", "sig_a", 0.1
    )
    second = Synthetic_Cross_Member_Results(
        "alias_free_convolutional", "charge_to_localization", "paired_fields_fivefold", "sig_b", 0.2
    )
    with pytest.raises(ValueError):
        Cross_Member_Table((first, second))


def Test_The_Rendering_Is_Byte_Deterministic() -> None:
    """the same artifacts, pooled in either order, render to the identical bytes"""
    first = Synthetic_Cross_Member_Results(
        "factorized_fourier", "charge_to_localization", "paired_fields_fivefold", "sig_a", 0.1
    )
    second = Synthetic_Cross_Member_Results(
        "alias_free_convolutional", "charge_to_localization", "paired_fields_fivefold", "sig_a", 0.2
    )
    forward_render = Cross_Member_Table((first, second))
    reversed_render = Cross_Member_Table((second, first))
    assert forward_render == reversed_render


def Test_The_Host_Harness_Resample_Agrees_With_The_Lifted_Resample() -> None:
    """the invariance harness's numpy truncation and the composition's lifted resample land on the same field"""
    generator = np.random.default_rng(20260916)
    field = generator.normal(size=(3, 8, 8, 8))
    for target_shape in ((4, 4, 4), (16, 16, 16)):
        harness = Spectral_Truncation_Resample(field, target_shape)
        lifted = np.asarray(Spectral_Resampled(field, target_shape))
        assert np.max(np.abs(harness - lifted)) < 1e-10


RESULTS_PAGE_PATH = Path(__file__).resolve().parent.parent.parent / "operator-results.md"
SUMMARY_TABLE_HEADING = "## Summary, one row per canon entry"
HEADLINE_NUMBER = re.compile(r"\d+(?:\.\d+)?%?")
MEMBER_CELL = re.compile(r"`([a-z_]+)`")


def Summary_Table_Rows(document_text: str) -> list[dict[str, str]]:
    """the results page's own summary table, one dict per entry, keyed by its header cells"""
    start = document_text.index(SUMMARY_TABLE_HEADING)
    table_lines = [line for line in document_text[start:].splitlines() if line.startswith("|")]
    header = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
    return [dict(zip(header, (cell.strip() for cell in line.strip("|").split("|")))) for line in table_lines[2:]]


def Headline_Value_And_Precision(headline: str) -> tuple[float, int] | None:
    """the first decimal number a headline cell prints, as a plain fraction, with its own printed precision"""
    found = HEADLINE_NUMBER.search(headline)
    if found is None:
        return None
    digits = found.group().rstrip("%")
    precision = len(digits.split(".")[1]) if "." in digits else 0
    value = float(digits) / 100.0 if found.group().endswith("%") else float(digits)
    return value, precision


def Test_The_Results_Page_Headlines_Match_The_Member_Artifacts() -> None:
    """every summary-table headline with a results.json source reproduces that artifact at the page's precision"""
    rows = Summary_Table_Rows(RESULTS_PAGE_PATH.read_text())
    assert rows, "the summary table parsed no rows at all"
    skipped: list[str] = []
    mismatches: list[str] = []
    for row in rows:
        member_match = MEMBER_CELL.search(row["member"])
        results_path = Member_Results_Path(member_match.group(1)) if member_match else None
        if results_path is None or not results_path.is_file():
            skipped.append(row["entry"])
            continue
        parsed = Headline_Value_And_Precision(row["headline vs bar"])
        if parsed is None:
            skipped.append(row["entry"])
            continue
        value, precision = parsed
        artifact = Read_Member_Results(results_path)
        printed = {f"{result_row.summary.median:.{precision}f}" for result_row in artifact.rows}
        if f"{value:.{precision}f}" not in printed:
            mismatches.append(f"{row['entry']}: {value:.{precision}f} not among {sorted(printed)}")
    assert mismatches == [], mismatches
    assert skipped, "no row was ever checked or skipped, so the parser likely found nothing"
