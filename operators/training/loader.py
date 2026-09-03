"""split-aware loading from the derived store into framework representations"""

import json
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from itertools import islice
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from operators.data import (
    ARTIFACT_DIRECTORY,
    Archive_Path,
    Orbit_Map,
    POOL_ROOT,
    Read_Census,
    Run_Identifier,
    StrainAssignment,
)
from operators.framework import Coefficients, Domain, GridFunction, UniformGridQuadrature
from operators.tasks import TaskCard

LATTICE_FACTOR_NAMES = ("a", "b", "c", "alpha", "beta", "gamma")
AUXILIARY_PROBE_ROLE = "auxiliary_probe"


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


@dataclass(frozen=True, slots=True)
class ParameterExample:
    """one run's parameter vector, its target field and the covariates its card names"""

    identifier: str
    run_path: str
    unit_key: str
    parameters: Coefficients
    target_function: GridFunction
    covariate_values: dict[str, str]


def Lattice_Factors_Of(run_path: str) -> tuple[float, ...]:
    """the six length and angle factors a perovskite run name encodes"""
    tokens = run_path.rsplit("/", 1)[-1].split("_")
    named = dict(zip(tokens[::2], tokens[1::2], strict=True))
    # the run names write a decimal point as p, so 0p8 is eight tenths
    return tuple(float(named[factor_name].replace("p", ".")) for factor_name in LATTICE_FACTOR_NAMES)


def Strain_Assignments_By_Run(pool_root: Path = POOL_ROOT) -> dict[str, StrainAssignment]:
    """every strain-atlas run path mapped to the assignment carrying its own tensor"""
    return {assignment.run_path: assignment for assignment in Orbit_Map(Read_Census(pool_root))}


def Parameter_Example_From_Run(
    campaign: str,
    identifier: str,
    run_path: str,
    unit_key: str,
    parameter_values: Sequence[float],
    covariate_values: dict[str, str],
    target_names: tuple[str, ...],
    pool_root: Path,
) -> ParameterExample | None:
    """one run read into a parameter vector and its target field, or nothing if incomplete"""
    archive_path = Archive_Path(campaign, identifier, pool_root)
    if not archive_path.exists():
        return None
    with np.load(archive_path) as archive:
        target_function = Field_From_Archive(archive, target_names)
    if target_function is None:
        return None
    return ParameterExample(
        identifier=identifier,
        run_path=run_path,
        unit_key=unit_key,
        # the parameters share the run's own cell, so downstream parts read one domain
        parameters=Coefficients(vector=np.asarray(parameter_values, dtype=np.float64), domain=target_function.domain),
        target_function=target_function,
        covariate_values=covariate_values,
    )


def Strain_Atlas_Examples(card: TaskCard, role: str, pool_root: Path) -> Iterator[ParameterExample]:
    """strain tensors and their target fields for one holdout assignment or the probe"""
    holdout = json.loads((ARTIFACT_DIRECTORY / "strain_atlas_holdout.json").read_text())
    assignments = Strain_Assignments_By_Run(pool_root)
    wants_probe = role == AUXILIARY_PROBE_ROLE
    for orbit, orbit_record in sorted(holdout.items()):
        # the probe cuts across the assignments, every other role selects one of them
        if not wants_probe and orbit_record["assignment"] != role:
            continue
        auxiliary = set(orbit_record["auxiliary_run_paths"])
        run_pairs = zip(orbit_record["run_identifiers"], orbit_record["run_paths"], strict=True)
        for identifier, run_path in run_pairs:
            # the later sweep is exact rotational copies, so it probes equivariance and never trains
            if (run_path in auxiliary) != wants_probe:
                continue
            assignment = assignments.get(run_path)
            if assignment is None:
                continue
            example = Parameter_Example_From_Run(
                "strain_atlas",
                identifier,
                run_path,
                orbit,
                assignment.tensor,
                {"functional": assignment.functional},
                card.targets,
                pool_root,
            )
            if example is not None:
                yield example


def Perovskite_Examples(
    card: TaskCard,
    role: str,
    evaluation_fold: int,
    extrapolation_holdout: str | None,
    pool_root: Path,
) -> Iterator[ParameterExample]:
    """lattice factors and their target fields, by fold or by a factor holdout"""
    folds = json.loads((ARTIFACT_DIRECTORY / "perovskite_folds.json").read_text())
    for unit_key, unit_record in sorted(folds.items()):
        if extrapolation_holdout is not None:
            held_out = extrapolation_holdout in unit_record["extrapolation_tags"]
        else:
            held_out = int(unit_record["fold"]) == evaluation_fold
        if (role == "evaluation") != held_out:
            continue
        run_pairs = zip(unit_record["run_identifiers"], unit_record["run_paths"], strict=True)
        for identifier, run_path in run_pairs:
            example = Parameter_Example_From_Run(
                "perovskite_grid",
                identifier,
                run_path,
                unit_key,
                Lattice_Factors_Of(run_path),
                {},
                card.targets,
                pool_root,
            )
            if example is not None:
                yield example


def Parameter_Field_Examples(
    card: TaskCard,
    role: str,
    evaluation_fold: int = 0,
    extrapolation_holdout: str | None = None,
    pool_root: Path = POOL_ROOT,
    limit: int | None = None,
) -> Iterator[ParameterExample]:
    """parameter vectors and their target fields for one card, under its committed split"""
    if card.split == "strain_atlas_holdout":
        examples = Strain_Atlas_Examples(card, role, pool_root)
    elif card.split == "perovskite_folds":
        examples = Perovskite_Examples(card, role, evaluation_fold, extrapolation_holdout, pool_root)
    else:
        raise ValueError(f"card {card.name} is not split by a parameter sweep")
    return examples if limit is None else islice(examples, limit)
