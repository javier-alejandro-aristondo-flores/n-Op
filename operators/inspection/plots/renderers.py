"""the drawing primitives every operator's figure suite is built from"""

from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from operators.inspection.plots.backend import PYPLOT


def Render_Field_Slices(field: NDArray[np.float64], path: Path, title: str) -> Path:
    """the three central axis slices of one volumetric field, as an image file"""
    figure, axes = PYPLOT.subplots(1, 3, figsize=(12.0, 4.0))
    for sliced_axis in range(3):
        center = field.shape[sliced_axis] // 2
        plane = np.take(field, center, axis=sliced_axis)
        image = axes[sliced_axis].imshow(plane.T, origin="lower")
        axes[sliced_axis].set_title(f"{title}, axis {sliced_axis} center")
        figure.colorbar(image, ax=axes[sliced_axis], shrink=0.8)
    figure.tight_layout()
    figure.savefig(path, dpi=120)
    PYPLOT.close(figure)
    return path


def Render_Curves(
    horizontal: NDArray[np.float64],
    curves: dict[str, NDArray[np.float64]],
    path: Path,
    title: str,
    horizontal_label: str,
    vertical_label: str,
) -> Path:
    """named curves over one shared horizontal axis, as an image file"""
    figure, axes = PYPLOT.subplots(figsize=(8.0, 5.0))
    for name, values in curves.items():
        axes.plot(horizontal, values, label=name)
    axes.set_title(title)
    axes.set_xlabel(horizontal_label)
    axes.set_ylabel(vertical_label)
    axes.legend()
    figure.tight_layout()
    figure.savefig(path, dpi=120)
    PYPLOT.close(figure)
    return path


def Symmetric_Limits(values: NDArray[np.float64]) -> tuple[float, float]:
    """colour limits centred on zero when an array spans it, and widened when it is constant"""
    lowest, highest = float(np.min(values)), float(np.max(values))
    if lowest < 0.0 < highest:
        reach = max(abs(lowest), highest)
        return -reach, reach
    # a constant array would give a colour bar with no extent at all
    if lowest == highest:
        return lowest - 0.5, highest + 0.5
    return lowest, highest


def Render_Matrix(values: NDArray[np.float64], path: Path, title: str) -> Path:
    """a two-dimensional array as a heat map, centred on zero where it spans zero"""
    figure, axes = PYPLOT.subplots(figsize=(6.0, 5.0))
    lowest, highest = Symmetric_Limits(values)
    colours = "RdBu_r" if lowest < 0.0 < highest else "viridis"
    image = axes.imshow(values, aspect="auto", origin="lower", cmap=colours, vmin=lowest, vmax=highest)
    axes.set_title(f"{title}  {values.shape}")
    figure.colorbar(image, ax=axes, shrink=0.85)
    figure.tight_layout()
    figure.savefig(path, dpi=120)
    PYPLOT.close(figure)
    return path


def Render_Bars(values: NDArray[np.float64], path: Path, title: str, reference: float | None = None) -> Path:
    """a short one-dimensional array as bars, with an optional line the values should sit on"""
    figure, axes = PYPLOT.subplots(figsize=(8.0, 4.0))
    axes.bar(np.arange(values.shape[0]), values)
    if reference is not None:
        axes.axhline(reference, linestyle="--", linewidth=1.0, color="crimson")
    axes.set_title(f"{title}  {values.shape}")
    axes.set_xlabel("index")
    figure.tight_layout()
    figure.savefig(path, dpi=120)
    PYPLOT.close(figure)
    return path


def Render_Spectrum(values: NDArray[np.float64], path: Path, title: str) -> Path:
    """a descending spectrum on a logarithmic scale, beside the energy it accounts for"""
    figure, axes = PYPLOT.subplots(1, 2, figsize=(11.0, 4.0))
    ranks = np.arange(1, values.shape[0] + 1, dtype=np.int64)
    positive = values[values > 0.0]
    axes[0].semilogy(ranks, np.maximum(values, float(positive.min()) * 1e-3 if positive.size else 1e-12), marker="o")
    axes[0].set_title(f"{title}  {values.shape}")
    axes[0].set_xlabel("rank")
    energy = np.cumsum(values**2)
    axes[1].plot(ranks, energy / energy[-1] if energy[-1] > 0.0 else energy, marker="o")
    axes[1].set_title("cumulative energy")
    axes[1].set_xlabel("rank")
    axes[1].set_ylim(0.0, 1.05)
    figure.tight_layout()
    figure.savefig(path, dpi=120)
    PYPLOT.close(figure)
    return path


def Render_Field_Sheet(fields: NDArray[np.float64], path: Path, title: str, most: int = 16) -> Path:
    """a stack of three-dimensional fields as one sheet, each drawn on its own centre plane"""
    shown = min(fields.shape[0], most)
    columns = min(shown, 4)
    rows = (shown + columns - 1) // columns
    figure, axes = PYPLOT.subplots(rows, columns, figsize=(3.2 * columns, 3.0 * rows), squeeze=False)
    for panel in range(rows * columns):
        axis = axes[panel // columns][panel % columns]
        axis.set_axis_off()
        if panel >= shown:
            continue
        field = fields[panel]
        plane = np.take(field, field.shape[0] // 2, axis=0)
        lowest, highest = Symmetric_Limits(field)
        axis.imshow(plane.T, origin="lower", cmap="RdBu_r", vmin=lowest, vmax=highest)
        axis.set_title(f"{panel}", fontsize=9)
    # each panel autoscales to its own structure, so the overall range is stated rather than shown
    figure.suptitle(
        f"{title}  {fields.shape}, showing {shown}"
        f"   range [{float(np.min(fields)):.4g}, {float(np.max(fields)):.4g}]"
    )
    # the overall title needs its own band, or the last row is laid out under it
    figure.tight_layout(rect=(0.0, 0.0, 1.0, 0.96))
    figure.savefig(path, dpi=120)
    PYPLOT.close(figure)
    return path


def Render_Scalars(named_values: dict[str, float], path: Path, title: str) -> Path:
    """every zero-dimensional quantity of a part on one panel, since each alone is a dot"""
    names = sorted(named_values)
    figure, axes = PYPLOT.subplots(figsize=(8.0, 0.5 + 0.4 * max(len(names), 1)))
    axes.barh(np.arange(len(names)), [named_values[name] for name in names])
    axes.set_yticks(np.arange(len(names)), labels=names, fontsize=8)
    axes.set_title(title)
    figure.tight_layout()
    figure.savefig(path, dpi=120)
    PYPLOT.close(figure)
    return path
