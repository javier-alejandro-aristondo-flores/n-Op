"""the result rows a member reports, and the floor verdicts they carry"""

import numpy as np
import pytest

from operators.evaluation import (
    Card_Metric_Errors,
    Compare_To_Floor,
    Comparison_Table,
    CubicBlock,
    EXTRAPOLATION,
    Label_Of,
    Potential_Floor_Rows,
    Potential_Metric_Errors,
    Recorded_Bars,
    ScoredRun,
    Summarize,
    Summarize_By,
    Summary_Table,
    Truncation_Ceiling_Rows,
    Unit_Medians,
)
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
