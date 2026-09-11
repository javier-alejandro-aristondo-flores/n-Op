"""training fields held resident in memory, so a step assembles a batch instead of reading archives"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.data import POOL_ROOT
from operators.framework import Array
from operators.tasks import TaskCard
from operators.training.loader import Parameter_Field_Examples


@dataclass(frozen=True, slots=True)
class CachedField:
    """one run's target field in single precision, with everything a batch needs beside it"""

    identifier: str
    run_path: str
    unit_key: str
    parameters: NDArray[np.float64]
    values: NDArray[np.float32]
    grid_shape: tuple[int, ...]
    lattice: NDArray[np.float64]
    cell_volume: float
    covariate_values: dict[str, str]


    def Channel_Count(self) -> int:
        """how many channels the field carries, which is its leading extent"""
        return int(self.values.shape[0])


    def Point_Count(self) -> int:
        """how many grid points one channel holds"""
        return int(self.values.size) // self.Channel_Count()


    def Flattened_Values(self) -> NDArray[np.float32]:
        """the field as one row per channel, in the order the grid coordinates flatten"""
        return self.values.reshape(self.Channel_Count(), -1)


    def Values_At(self, flat_indices: NDArray[np.integer[Any]]) -> NDArray[np.float32]:
        """the field's channels at chosen flattened positions, one row per point"""
        return self.Flattened_Values()[:, flat_indices].T


    def Inspect(self) -> dict[str, Array]:
        """the field itself, and the numbers that place it in its own cell"""
        return {
            "values": self.values,
            "parameters": self.parameters,
            "lattice": self.lattice,
            "grid_extents": np.asarray(self.grid_shape, dtype=np.float64),
            "cell_volume": np.asarray([self.cell_volume], dtype=np.float64),
        }


class FieldCache:
    """every field of one card and role, resident in memory and grouped by exchangeable unit"""


    def __init__(self, card_name: str, role: str, fields: tuple[CachedField, ...]) -> None:
        self.card_name = card_name
        self.role = role
        self.fields = fields
        grouped: dict[str, list[CachedField]] = {}
        for cached_field in fields:
            grouped.setdefault(cached_field.unit_key, []).append(cached_field)
        self.fields_of_unit: dict[str, tuple[CachedField, ...]] = {
            unit_key: tuple(unit_fields) for unit_key, unit_fields in sorted(grouped.items())
        }


    def Unit_Keys(self) -> tuple[str, ...]:
        """every exchangeable unit the cache holds, in one fixed order"""
        return tuple(self.fields_of_unit)


    def Resident_Bytes(self) -> int:
        """what the cache costs in memory, which is what its field values occupy"""
        return sum(int(cached_field.values.nbytes) for cached_field in self.fields)


    def Inspect(self) -> dict[str, Array]:
        """what the cache holds, on what grids, at what cost"""
        parameter_widths = {int(cached_field.parameters.shape[0]) for cached_field in self.fields}
        axis_counts = {len(cached_field.grid_shape) for cached_field in self.fields}
        state: dict[str, Array] = {
            "point_counts": np.asarray([cached_field.Point_Count() for cached_field in self.fields], dtype=np.float64),
            "channel_counts": np.asarray(
                [cached_field.Channel_Count() for cached_field in self.fields], dtype=np.float64
            ),
            "cell_volumes": np.asarray([cached_field.cell_volume for cached_field in self.fields], dtype=np.float64),
            "unit_run_counts": np.asarray(
                [len(unit_fields) for unit_fields in self.fields_of_unit.values()], dtype=np.float64
            ),
            "resident_bytes": np.asarray([float(self.Resident_Bytes())], dtype=np.float64),
        }
        # runs that disagree on parameter width or on grid rank have no rectangle to be reported in
        if len(parameter_widths) == 1:
            state["parameter_vectors"] = np.stack([cached_field.parameters for cached_field in self.fields])
        if len(axis_counts) == 1:
            state["grid_extents"] = np.asarray(
                [cached_field.grid_shape for cached_field in self.fields], dtype=np.float64
            )
        return state


def Build_Field_Cache(
    card: TaskCard,
    role: str,
    evaluation_fold: int = 0,
    extrapolation_holdout: str | None = None,
    pool_root: Path = POOL_ROOT,
    limit: int | None = None,
) -> FieldCache:
    """every parameter and target field of one card and role, read once and kept in single precision"""
    cached_fields: list[CachedField] = []
    examples = Parameter_Field_Examples(
        card, role, evaluation_fold, extrapolation_holdout, pool_root, limit, precision="single"
    )
    for example in examples:
        # the store hands back fields laid out axis-first, and flattening one of those copies it whole
        values = np.ascontiguousarray(example.target_function.values, dtype=np.float32)
        cached_fields.append(
            CachedField(
                identifier=example.identifier,
                run_path=example.run_path,
                unit_key=example.unit_key,
                parameters=np.asarray(example.parameters.vector, dtype=np.float64),
                values=values,
                grid_shape=tuple(int(extent) for extent in values.shape[1:]),
                lattice=np.asarray(example.target_function.domain.lattice, dtype=np.float64),
                cell_volume=float(example.target_function.quadrature.cell_volume),
                covariate_values=dict(example.covariate_values),
            )
        )
    return FieldCache(card.name, role, tuple(cached_fields))


def Cached_Field_Statistics(cache: FieldCache) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """per-channel means and deviations over every cached field, summed in double"""
    if not cache.fields:
        raise ValueError(f"the {cache.role} cache of {cache.card_name} holds no fields to summarize")
    channel_counts = {cached_field.Channel_Count() for cached_field in cache.fields}
    if len(channel_counts) != 1:
        raise ValueError(f"the {cache.role} cache of {cache.card_name} holds fields of unequal channel counts")
    channel_count = channel_counts.pop()
    value_sums = np.zeros(channel_count, dtype=np.float64)
    counted_points = 0
    for cached_field in cache.fields:
        # the values stay resident in single, and only one field at a time is widened to be summed
        value_sums += cached_field.Flattened_Values().astype(np.float64).sum(axis=1)
        counted_points += cached_field.Point_Count()
    means = value_sums / float(counted_points)
    squared_deviations = np.zeros(channel_count, dtype=np.float64)
    # the spread takes a second pass over the resident values, so a mean far from zero cannot cancel it away
    for cached_field in cache.fields:
        widened: NDArray[np.float64] = cached_field.Flattened_Values().astype(np.float64)
        squared_deviations += np.square(widened - means[:, None]).sum(axis=1)
    return means, np.maximum(np.sqrt(squared_deviations / float(counted_points)), 1e-12)
