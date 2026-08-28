"""split-aware loading from the derived store into framework representations"""

import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from operators.data import ARTIFACT_DIRECTORY, Archive_Path, POOL_ROOT, Run_Identifier
from operators.framework import Domain, GridFunction, UniformGridQuadrature
from operators.tasks import TaskCard


@dataclass(frozen=True, slots=True)
class TrainingExample:
    """one run's input and target fields, with its store identifier"""

    identifier: str
    input_function: GridFunction
    target_function: GridFunction


def Field_From_Archive(
    archive: "np.lib.npyio.NpzFile",
    channel_names: tuple[str, ...],
) -> GridFunction | None:
    """one field from named channels, zeros standing in for an absent magnetization"""
    channels: list[NDArray[np.float64]] = []
    for name in channel_names:
        if name in archive:
            channels.append(np.asarray(archive[name], dtype=np.float64))
        # an unpolarized run wrote no magnetization because it is zero everywhere
        elif name == "magnetization_density" and "charge_density" in archive:
            channels.append(np.zeros_like(np.asarray(archive["charge_density"], dtype=np.float64)))
        else:
            return None
    stacked = np.stack(channels)
    lattice = np.asarray(archive["lattice"], dtype=np.float64)
    cell_volume = float(np.asarray(archive["cell_volume"], dtype=np.float64))
    point_count = int(stacked[0].size)
    return GridFunction(
        values=stacked,
        channel_labels=channel_names,
        domain=Domain(lattice=lattice),
        quadrature=UniformGridQuadrature(cell_volume=cell_volume, point_count=point_count),
    )


def Strain_Charge_Pairs(
    assignment: str,
    pool_root: Path = POOL_ROOT,
    limit: int | None = None,
) -> Iterator[tuple[str, GridFunction, GridFunction]]:
    """same-grid cheap and accurate charge fields, for one holdout assignment"""
    holdout = json.loads((ARTIFACT_DIRECTORY / "strain_atlas_holdout.json").read_text())
    produced = 0
    for orbit_record in holdout.values():
        if orbit_record["assignment"] != assignment:
            continue
        # the later sweep is reserved for the equivariance probe and never trains
        auxiliary = set(orbit_record["auxiliary_run_paths"])
        by_point: dict[str, dict[str, str]] = {}
        for run_path in orbit_record["run_paths"]:
            if run_path in auxiliary:
                continue
            point = run_path.rsplit("/", 1)[0]
            side = "accurate" if "HSE" in run_path.rsplit("/", 1)[-1] else "cheap"
            by_point.setdefault(point, {})[side] = run_path
        for point, sides in sorted(by_point.items()):
            if len(sides) != 2:
                continue
            fields: dict[str, GridFunction] = {}
            for side, run_path in sides.items():
                archive_path = Archive_Path("strain_atlas", Run_Identifier(run_path), pool_root)
                with np.load(archive_path) as archive:
                    field = Field_From_Archive(archive, ("charge_density",))
                if field is None:
                    break
                fields[side] = field
            if len(fields) != 2:
                continue
            # a pair on two different grids has no pointwise comparison to make
            if np.asarray(fields["cheap"].values).shape != np.asarray(fields["accurate"].values).shape:
                continue
            yield point, fields["cheap"], fields["accurate"]
            produced += 1
            if limit is not None and produced >= limit:
                return


def Paired_Field_Examples(
    card: TaskCard,
    role: str,
    evaluation_fold: int = 0,
    pool_root: Path = POOL_ROOT,
    limit: int | None = None,
) -> Iterator[TrainingExample]:
    """input and target fields for one task card, under the committed fold map"""
    folds = json.loads((ARTIFACT_DIRECTORY / "paired_fields_fivefold.json").read_text())
    produced = 0
    for unit in folds.values():
        in_evaluation = int(unit["fold"]) == evaluation_fold
        if (role == "evaluation") != in_evaluation:
            continue
        for identifier in unit["run_identifiers"]:
            archive_path = Archive_Path(unit["campaign"], identifier, pool_root)
            if not archive_path.exists():
                continue
            with np.load(archive_path) as archive:
                input_function = Field_From_Archive(archive, card.inputs)
                target_function = Field_From_Archive(archive, card.targets)
            # a run missing a channel the card asks for is simply not an example
            if input_function is None or target_function is None:
                continue
            yield TrainingExample(identifier, input_function, target_function)
            produced += 1
            if limit is not None and produced >= limit:
                return


def Per_Channel_Statistics(fields: list[GridFunction]) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """per-channel means and deviations over a list of same-channel fields"""
    stacked = np.stack(
        [np.asarray(field.values, dtype=np.float64).reshape(len(field.channel_labels), -1) for field in fields]
    )
    means = stacked.mean(axis=(0, 2))
    deviations = stacked.std(axis=(0, 2))
    return means, np.maximum(deviations, 1e-12)
