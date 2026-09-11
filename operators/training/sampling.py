"""batches drawn from the resident cache, one step at a time, out of a generator the trainer owns"""

from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Protocol

import numpy as np
from numpy.typing import NDArray

from operators.framework import Array, Fractional_Coordinates_Of_Flat_Indices, Inspectable
from operators.training.cache import CachedField, FieldCache

type BatchArray = NDArray[np.float32] | NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class TrainingBatch:
    """one step's arrays under plain-word names, each rectangular across the whole batch"""

    arrays: dict[str, BatchArray]


    def Inspect(self) -> dict[str, Array]:
        """the batch's own arrays, which are already the named arrays to look at"""
        return dict(self.arrays)


class BatchSource(Inspectable, Protocol):
    """one step's batch on demand, and the fixed batches a validation pass is scored on"""


    @abstractmethod
    def Next_Batch(self, generator: np.random.Generator) -> TrainingBatch: ...


    @abstractmethod
    def Validation_Batches(self) -> tuple[tuple[str, TrainingBatch], ...]: ...


def Evenly_Spaced_Flat_Indices(point_count: int, wanted_points: int) -> NDArray[np.intp]:
    """a fixed spread of flattened positions across a field, so a held batch needs no seed of its own"""
    if wanted_points >= point_count:
        return np.arange(point_count, dtype=np.intp)
    return np.floor(np.linspace(0.0, float(point_count), wanted_points, endpoint=False)).astype(np.intp)


def Batch_Of_Fields(
    fields: Sequence[CachedField],
    point_selections: Sequence[NDArray[np.integer[Any]]],
) -> TrainingBatch:
    """one rectangular batch out of chosen runs and the points chosen inside each of them"""
    chosen = list(zip(fields, point_selections, strict=True))
    return TrainingBatch(
        {
            "parameter_vectors": np.stack([cached_field.parameters for cached_field, _ in chosen]),
            # every run contributes the same number of points, so grids that differ leave no trace here
            "point_coordinates": np.stack(
                [
                    Fractional_Coordinates_Of_Flat_Indices(cached_field.grid_shape, flat_indices)
                    for cached_field, flat_indices in chosen
                ]
            ),
            "target_values": np.stack(
                [cached_field.Values_At(flat_indices) for cached_field, flat_indices in chosen]
            ),
            "cell_volumes": np.asarray([cached_field.cell_volume for cached_field, _ in chosen], dtype=np.float64),
            "point_weights": np.asarray(
                [cached_field.cell_volume / cached_field.Point_Count() for cached_field, _ in chosen],
                dtype=np.float64,
            ),
        }
    )


class FixedBatches(BatchSource):
    """one batch handed back on every step, for a caller holding its whole training set at once"""


    def __init__(self, batch: TrainingBatch, validation_batch: TrainingBatch | None = None) -> None:
        self.batch = batch
        self.validation_batch = batch if validation_batch is None else validation_batch
        self.held: tuple[tuple[str, TrainingBatch], ...] = (("whole_batch", self.validation_batch),)


    def Next_Batch(self, generator: np.random.Generator) -> TrainingBatch:
        """the one batch, handed back without spending the generator so a replay reaches the same place"""
        return self.batch


    def Validation_Batches(self) -> tuple[tuple[str, TrainingBatch], ...]:
        """the single unit this source can offer, which is the whole batch unless one was held out"""
        return self.held


    def Inspect(self) -> dict[str, Array]:
        """the fixed batch's own arrays, and the held-out batch's beside them"""
        state: dict[str, Array] = {f"batch_{name}": array for name, array in self.batch.Inspect().items()}
        for name, array in self.validation_batch.Inspect().items():
            state[f"validation_{name}"] = array
        return state


class PointSampledBatches(BatchSource):
    """runs drawn with replacement, and fresh points drawn inside each of them every step"""


    def __init__(
        self,
        training_cache: FieldCache,
        validation_cache: FieldCache,
        runs_per_batch: int,
        points_per_run: int,
        validation_points_per_run: int = 512,
    ) -> None:
        if not training_cache.fields:
            raise ValueError(f"the {training_cache.role} cache of {training_cache.card_name} holds no fields to draw")
        self.training_cache = training_cache
        self.validation_cache = validation_cache
        self.runs_per_batch = runs_per_batch
        self.points_per_run = points_per_run
        self.validation_points_per_run = validation_points_per_run
        self.last_batch: TrainingBatch | None = None
        # the held-out points are spaced rather than drawn, so the trainer's seed remains the only one
        self.validation_batches: tuple[tuple[str, TrainingBatch], ...] = tuple(
            (
                unit_key,
                Batch_Of_Fields(
                    unit_fields,
                    [
                        Evenly_Spaced_Flat_Indices(cached_field.Point_Count(), validation_points_per_run)
                        for cached_field in unit_fields
                    ],
                ),
            )
            for unit_key, unit_fields in validation_cache.fields_of_unit.items()
        )


    def Next_Batch(self, generator: np.random.Generator) -> TrainingBatch:
        """one step's batch, the generator passed in rather than held so one seed reproduces the run"""
        drawn_runs = generator.integers(0, len(self.training_cache.fields), size=self.runs_per_batch)
        drawn_fields = [self.training_cache.fields[int(run_position)] for run_position in drawn_runs]
        point_selections = [
            generator.integers(0, cached_field.Point_Count(), size=self.points_per_run)
            for cached_field in drawn_fields
        ]
        batch = Batch_Of_Fields(drawn_fields, point_selections)
        self.last_batch = batch
        return batch


    def Validation_Batches(self) -> tuple[tuple[str, TrainingBatch], ...]:
        """one fixed batch per exchangeable unit, so a score is a mean over units and not over points"""
        return self.validation_batches


    def Inspect(self) -> dict[str, Array]:
        """what the source draws from, and what it drew last"""
        state: dict[str, Array] = {
            "runs_per_batch": np.asarray([self.runs_per_batch], dtype=np.float64),
            "points_per_run": np.asarray([self.points_per_run], dtype=np.float64),
            "training_run_count": np.asarray([len(self.training_cache.fields)], dtype=np.float64),
            "validation_unit_count": np.asarray([len(self.validation_batches)], dtype=np.float64),
        }
        if self.last_batch is not None:
            for name, drawn_array in self.last_batch.Inspect().items():
                state[f"last_{name}"] = drawn_array
        return state
