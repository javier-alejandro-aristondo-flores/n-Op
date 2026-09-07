"""figures a member is judged by: predictions against truth, error spread, floors and verdicts"""

from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from operators.inspection.plots.backend import PYPLOT
from operators.inspection.plots.renderers import Centred_On_Zero


def Render_Prediction_Against_Truth(
    predicted: NDArray[np.float64],
    truth: NDArray[np.float64],
    path: Path,
    title: str,
) -> Path:
    """one run's prediction beside its truth and the signed difference between them"""
    figure, axes = PYPLOT.subplots(1, 3, figsize=(14.0, 4.2))
    centre = truth.shape[0] // 2
    truth_plane = np.take(truth, centre, axis=0)
    predicted_plane = np.take(predicted, centre, axis=0)
    difference = predicted_plane - truth_plane
    # prediction and truth share one scale, or the eye reads a difference that is not there
    shared_low, shared_high = float(np.min(truth)), float(np.max(truth))
    for axis, plane, panel, colours, limits in (
        (axes[0], truth_plane, "truth", "viridis", (shared_low, shared_high)),
        (axes[1], predicted_plane, "predicted", "viridis", (shared_low, shared_high)),
        (axes[2], difference, "predicted minus truth", "RdBu_r", Centred_On_Zero(difference)),
    ):
        image = axis.imshow(plane.T, origin="lower", cmap=colours, vmin=limits[0], vmax=limits[1])
        axis.set_title(panel)
        figure.colorbar(image, ax=axis, shrink=0.8)
    relative = float(np.linalg.norm(predicted - truth) / np.linalg.norm(truth))
    figure.suptitle(f"{title}   relative L2 {relative:.5f}")
    figure.tight_layout(rect=(0.0, 0.0, 1.0, 0.95))
    figure.savefig(path, dpi=120)
    PYPLOT.close(figure)
    return path


def Render_Error_Spread(
    errors_by_group: dict[str, NDArray[np.float64]],
    path: Path,
    title: str,
    vertical_label: str = "relative L2",
) -> Path:
    """one box per group with its own points beside it, so a small group cannot hide"""
    names = sorted(errors_by_group)
    figure, axes = PYPLOT.subplots(figsize=(1.6 * max(len(names), 3), 5.0))
    axes.boxplot([errors_by_group[name] for name in names], tick_labels=names, showfliers=False)
    generator = np.random.default_rng(0)
    for position, name in enumerate(names, start=1):
        values = errors_by_group[name]
        scatter = position + generator.uniform(-0.12, 0.12, size=values.shape[0])
        axes.plot(scatter, values, ".", markersize=5, alpha=0.7)
    axes.set_yscale("log")
    axes.set_ylabel(vertical_label)
    unit_count = sum(group.shape[0] for group in errors_by_group.values())
    axes.set_title(f"{title}   {unit_count} units")
    axes.tick_params(axis="x", labelrotation=30.0)
    figure.tight_layout()
    figure.savefig(path, dpi=120)
    PYPLOT.close(figure)
    return path


def Render_Floor_Comparison(
    floor_medians: dict[str, float],
    member_median: float,
    required_improvements: dict[str, float],
    path: Path,
    title: str,
) -> Path:
    """each floor as a bar with the level the member had to reach drawn across it"""
    names = sorted(floor_medians)
    figure, axes = PYPLOT.subplots(figsize=(2.4 * max(len(names), 2) + 2.0, 5.0))
    positions = np.arange(len(names), dtype=np.float64)
    axes.bar(positions, [floor_medians[name] for name in names], width=0.55, label="floor")
    for position, name in zip(positions, names):
        # the bar the member actually had to get under, not the floor itself
        target = floor_medians[name] * (1.0 - required_improvements[name])
        axes.plot([position - 0.34, position + 0.34], [target, target], linestyle="--", color="crimson")
    axes.axhline(member_median, color="seagreen", linewidth=2.0, label="member")
    axes.set_xticks(positions, labels=names)
    axes.set_yscale("log")
    axes.set_ylabel("relative L2")
    axes.set_title(f"{title}   dashed is the level required to pass")
    axes.legend()
    figure.tight_layout()
    figure.savefig(path, dpi=120)
    PYPLOT.close(figure)
    return path
