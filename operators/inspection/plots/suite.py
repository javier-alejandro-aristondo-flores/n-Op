"""every named array of an inspection dict drawn the way its rank and name ask for"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from operators.inspection.plots.renderers import (
    Render_Bars,
    Render_Field_Sheet,
    Render_Field_Slices,
    Render_Matrix,
    Render_Scalars,
    Render_Spectrum,
)

LONG_ENOUGH_TO_BE_A_CURVE = 256


@dataclass(frozen=True, slots=True)
class RenderedSuite:
    """the files a suite wrote, and any key it had no renderer for"""

    written: tuple[Path, ...]
    skipped: tuple[str, ...]


def File_Name_Of(key: str) -> str:
    """an inspection key as a file name, its owner path flattened into the name"""
    return key.replace(".", "__") + ".png"


def Render_One_Array(values: NDArray[np.float64], key: str, path: Path) -> Path | None:
    """one inspected array drawn by its rank and its name, or nothing if neither says how"""
    name = key.rsplit(".", 1)[-1]
    if values.ndim == 1:
        if name.endswith("singular_values"):
            return Render_Spectrum(values, path, key)
        if name.endswith("norms"):
            # these are a diagnostic that should read one everywhere, not a spectrum
            return Render_Bars(values, path, key, reference=1.0)
        if values.shape[0] > LONG_ENOUGH_TO_BE_A_CURVE:
            return Render_Matrix(values.reshape(1, -1), path, key)
        return Render_Bars(values, path, key)
    if values.ndim == 2:
        return Render_Matrix(values, path, key)
    if values.ndim == 3:
        return Render_Field_Slices(values, path, key)
    if values.ndim == 4:
        return Render_Field_Sheet(values, path, key)
    if values.ndim == 5:
        # the leading three axes are a mode cube and the trailing pair are channels
        stacked = values.reshape(values.shape[0], values.shape[1], values.shape[2], -1)
        return Render_Field_Sheet(np.moveaxis(stacked, 3, 0), path, key)
    return None


def Render_Inspection_Suite(
    inspected: dict[str, NDArray[np.float64]],
    directory: Path,
    title: str = "inspection",
) -> RenderedSuite:
    """a whole part or assembly drawn from its inspection dict alone"""
    directory.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    skipped: list[str] = []
    scalars: dict[str, float] = {}
    for key, value in sorted(inspected.items()):
        values = np.asarray(value, dtype=np.float64)
        if values.ndim == 0:
            scalars[key] = float(values)
            continue
        drawn = Render_One_Array(values, key, directory / File_Name_Of(key))
        if drawn is None:
            skipped.append(key)
        else:
            written.append(drawn)
    if scalars:
        # one dot per panel would be a page of nothing, so every scalar shares one
        written.append(Render_Scalars(scalars, directory / "scalars.png", f"{title} scalars"))
    return RenderedSuite(written=tuple(written), skipped=tuple(skipped))
