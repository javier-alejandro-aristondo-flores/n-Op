"""Rendering: axis slices and curves drawn from inspection arrays alone."""

from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
from numpy.typing import NDArray

matplotlib.use("Agg")

from matplotlib import pyplot

PYPLOT: Any = pyplot


def Render_Field_Slices(field: NDArray[np.float64], path: Path, title: str) -> Path:
    """Draws the three central axis slices of one volumetric field to an image file."""
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
    """Draws named curves over one shared horizontal axis to an image file."""
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
