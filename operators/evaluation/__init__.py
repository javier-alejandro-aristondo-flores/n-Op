"""scored runs grouped into the result rows a member reports, against the floors it must beat"""

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from operators.inspection import Table
from operators.metrics import Bootstrap_Confidence_Interval, Median_And_Interquartile

INTERPOLATION = "interpolation"
EXTRAPOLATION = "extrapolation"


@dataclass(frozen=True, slots=True)
class ScoredRun:
    """one run's measured errors beside every label a report groups it by"""

    identifier: str
    unit_key: str
    campaign: str
    family: str
    errors: dict[str, float]
    covariate_values: dict[str, str] = field(default_factory=dict[str, str])
    extrapolation: str = INTERPOLATION


@dataclass(frozen=True, slots=True)
class MetricSummary:
    """one metric over one group, carrying the count of exchangeable units behind it"""

    metric_name: str
    group_name: str
    unit_count: int
    run_count: int
    median: float
    interquartile: float
    confidence_low: float
    confidence_high: float


@dataclass(frozen=True, slots=True)
class FloorComparison:
    """a floor's error beside the member's, and whether the suite's margin was met"""

    floor_name: str
    metric_name: str
    group_name: str
    floor_median: float
    member_median: float
    required_improvement: float
    improvement: float
    verdict: str


def Label_Of(scored_run: ScoredRun, label_name: str) -> str:
    """the value a run carries under one grouping label"""
    if label_name == "campaign":
        return scored_run.campaign
    if label_name == "family":
        return scored_run.family
    if label_name == "extrapolation":
        return scored_run.extrapolation
    if label_name in scored_run.covariate_values:
        return scored_run.covariate_values[label_name]
    raise ValueError(f"run {scored_run.identifier} carries no label named {label_name}")


def Unit_Medians(scored_runs: list[ScoredRun], metric_name: str) -> NDArray[np.float64]:
    """each exchangeable unit's own median, so symmetry copies inside one orbit count once"""
    by_unit: dict[str, list[float]] = {}
    for scored_run in scored_runs:
        by_unit.setdefault(scored_run.unit_key, []).append(scored_run.errors[metric_name])
    return np.asarray([float(np.median(values)) for _, values in sorted(by_unit.items())], dtype=np.float64)


def Summarize(scored_runs: list[ScoredRun], metric_name: str, group_name: str = "all") -> MetricSummary:
    """one metric over one group, aggregated and bootstrapped over units rather than runs"""
    unit_medians = Unit_Medians(scored_runs, metric_name)
    median, interquartile = Median_And_Interquartile(unit_medians)
    low, high = Bootstrap_Confidence_Interval(unit_medians)
    return MetricSummary(
        metric_name=metric_name,
        group_name=group_name,
        unit_count=int(unit_medians.shape[0]),
        run_count=len(scored_runs),
        median=median,
        interquartile=interquartile,
        confidence_low=low,
        confidence_high=high,
    )


def Summarize_By(scored_runs: list[ScoredRun], metric_name: str, label_name: str) -> tuple[MetricSummary, ...]:
    """the same metric summarized once per value of a grouping label"""
    grouped: dict[str, list[ScoredRun]] = {}
    for scored_run in scored_runs:
        grouped.setdefault(Label_Of(scored_run, label_name), []).append(scored_run)
    return tuple(Summarize(members, metric_name, name) for name, members in sorted(grouped.items()))


def Compare_To_Floor(
    member_runs: list[ScoredRun],
    floor_runs: list[ScoredRun],
    metric_name: str,
    floor_name: str,
    required_improvement: float,
    group_name: str = "all",
) -> FloorComparison:
    """the member against one floor on the same runs, with the suite's margin applied"""
    floor_median = float(np.median(Unit_Medians(floor_runs, metric_name)))
    member_median = float(np.median(Unit_Medians(member_runs, metric_name)))
    # a floor that scores nothing cannot be improved on by a fraction of itself
    improvement = 1.0 - member_median / floor_median if floor_median > 0.0 else 0.0
    return FloorComparison(
        floor_name=floor_name,
        metric_name=metric_name,
        group_name=group_name,
        floor_median=floor_median,
        member_median=member_median,
        required_improvement=required_improvement,
        improvement=improvement,
        verdict="pass" if improvement >= required_improvement else "kill",
    )


def Summary_Table(summaries: tuple[MetricSummary, ...]) -> Table:
    """metric summaries as table rows, percentages where the metric is a relative error"""
    return tuple(
        {
            "group": summary.group_name,
            "metric": summary.metric_name,
            "units": summary.unit_count,
            "runs": summary.run_count,
            "median": f"{summary.median:.6f}",
            "interquartile": f"{summary.interquartile:.6f}",
            "mean_interval": f"[{summary.confidence_low:.6f}, {summary.confidence_high:.6f}]",
        }
        for summary in summaries
    )


def Comparison_Table(comparisons: tuple[FloorComparison, ...]) -> Table:
    """floor comparisons as table rows, each carrying its own verdict"""
    return tuple(
        {
            "group": comparison.group_name,
            "floor": comparison.floor_name,
            "floor_median": f"{comparison.floor_median:.6f}",
            "member_median": f"{comparison.member_median:.6f}",
            "improvement": f"{100.0 * comparison.improvement:.1f}%",
            "required": f"{100.0 * comparison.required_improvement:.1f}%",
            "verdict": comparison.verdict,
        }
        for comparison in comparisons
    )
