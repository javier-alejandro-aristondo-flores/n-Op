"""the resident field cache, the batches drawn from it, and the reads that fill it"""

import json
from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.framework import Fractional_Grid_Coordinates
from operators.tasks import Card_Named
from operators.training import (
    Batch_Of_Fields,
    Build_Field_Cache,
    CachedField,
    Cached_Field_Statistics,
    Evenly_Spaced_Flat_Indices,
    Field_From_Archive,
    FieldCache,
    Parameter_Field_Examples,
    PointSampledBatches,
    Strain_Assignments_By_Run,
    Strain_Assignments_Of_Pool,
)

REFERENCE_RUN = "diamond/2_atoms_4-10-2026/reference_2_atoms/GGA-PBE"

STRAINED_RUN = "diamond/2_atoms_4-10-2026/uniax_x_eps0.01/GGA-PBE"


def Position_Marked_Field(
    identifier: str,
    unit_key: str,
    grid_shape: tuple[int, int, int],
    channel_count: int = 1,
) -> CachedField:
    """a cached field whose every value is its own flattened position, so a sample can be checked"""
    point_count = grid_shape[0] * grid_shape[1] * grid_shape[2]
    values = np.arange(channel_count * point_count, dtype=np.float32).reshape(channel_count, *grid_shape)
    return CachedField(
        identifier=identifier,
        run_path=f"made_up/{identifier}",
        unit_key=unit_key,
        parameters=np.asarray([0.1, -0.2, 0.3], dtype=np.float64),
        values=values,
        grid_shape=grid_shape,
        lattice=np.eye(3) * 2.0,
        cell_volume=8.0,
        covariate_values={"functional": "cheap"},
    )


def Made_Up_Cache(*fields: CachedField) -> FieldCache:
    """a cache of given fields, standing in for one a card and role would fill"""
    return FieldCache("made_up_card", "train", fields)


def Synthetic_Census(pool_root: Path) -> None:
    """the smallest census the orbit map accepts, a reference run and one strained run"""
    census_directory = pool_root / "_census"
    census_directory.mkdir(parents=True, exist_ok=True)
    lines = [
        json.dumps({"path": REFERENCE_RUN, "p_abc": [3.57, 3.57, 3.57], "files": {}}),
        json.dumps({"path": STRAINED_RUN, "p_abc": [3.6057, 3.57, 3.57], "files": {}}),
    ]
    (census_directory / "runs.jsonl").write_text("\n".join(lines) + "\n")


def Test_The_Orbit_Map_Is_Read_Once_Per_Pool(tmp_path: Path) -> None:
    """asserts a second call reuses the assignments of the first rather than walking the census again"""
    Synthetic_Census(tmp_path)
    first = Strain_Assignments_By_Run(tmp_path)
    second = Strain_Assignments_By_Run(tmp_path)
    assert set(first) == {REFERENCE_RUN, STRAINED_RUN}
    assert first is not second
    assert all(first[run_path] is second[run_path] for run_path in first)
    assert Strain_Assignments_Of_Pool(tmp_path) is Strain_Assignments_Of_Pool(tmp_path)


def Test_The_Shared_Orbit_Map_Cannot_Be_Emptied_By_A_Caller(tmp_path: Path) -> None:
    """asserts clearing what one call returned leaves the next call whole"""
    Synthetic_Census(tmp_path)
    Strain_Assignments_By_Run(tmp_path).clear()
    assert set(Strain_Assignments_By_Run(tmp_path)) == {REFERENCE_RUN, STRAINED_RUN}
    assert isinstance(Strain_Assignments_Of_Pool(tmp_path), tuple)


def Test_The_Precision_Word_Changes_Residency_And_Not_The_Numbers(tmp_path: Path) -> None:
    """asserts a single-precision read is the same numbers in half the bytes"""
    generator = np.random.default_rng(7)
    written = generator.random((3, 4, 5)).astype(np.float32)
    archive_path = tmp_path / "made_up.npz"
    np.savez(archive_path, charge_density=written, lattice=np.eye(3), cell_volume=np.asarray(8.0))
    with np.load(archive_path) as archive:
        single = Field_From_Archive(archive, ("charge_density",), "single")
        double = Field_From_Archive(archive, ("charge_density",))
        spin_pair = Field_From_Archive(archive, ("charge_density", "magnetization_density"), "single")
    assert single is not None and double is not None and spin_pair is not None
    single_values = np.asarray(single.values)
    double_values = np.asarray(double.values)
    assert single_values.dtype == np.float32 and double_values.dtype == np.float64
    assert np.array_equal(single_values.astype(np.float64), double_values)
    assert single_values.nbytes * 2 == double_values.nbytes
    # the standing-in magnetization follows the word the caller asked for
    assert np.asarray(spin_pair.values).dtype == np.float32
    assert not np.asarray(spin_pair.values)[1].any()


def Test_A_Batch_Is_Rectangular_Across_Unequal_Grids() -> None:
    """asserts three runs on three different grids leave one rectangle behind"""
    fields = (
        Position_Marked_Field("first", "unit_one", (4, 5, 6)),
        Position_Marked_Field("second", "unit_one", (3, 3, 3)),
        Position_Marked_Field("third", "unit_two", (2, 7, 5)),
    )
    selections: list[NDArray[np.intp]] = [np.asarray([0, 1, 2, 3], dtype=np.intp) for _ in fields]
    batch = Batch_Of_Fields(fields, selections)
    assert np.asarray(batch.arrays["target_values"]).shape == (3, 4, 1)
    assert np.asarray(batch.arrays["point_coordinates"]).shape == (3, 4, 3)
    assert np.asarray(batch.arrays["parameter_vectors"]).shape == (3, 3)
    assert np.asarray(batch.arrays["cell_volumes"]).shape == (3,)
    assert set(batch.Inspect()) == set(batch.arrays)


def Test_A_Sampled_Value_Sits_At_Its_Own_Coordinate() -> None:
    """asserts a drawn point's value is the field value at the coordinate reported beside it"""
    grid_shape = (4, 5, 6)
    cache = Made_Up_Cache(Position_Marked_Field("only", "unit_one", grid_shape, channel_count=2))
    source = PointSampledBatches(cache, cache, runs_per_batch=3, points_per_run=11)
    batch = source.Next_Batch(np.random.default_rng(4))
    coordinates = np.asarray(batch.arrays["point_coordinates"])
    values = np.asarray(batch.arrays["target_values"])
    implied = np.rint(coordinates * np.asarray(grid_shape, dtype=np.float64)).astype(np.intp)
    flattened = np.ravel_multi_index((implied[..., 0], implied[..., 1], implied[..., 2]), grid_shape)
    assert values.shape == (3, 11, 2)
    assert np.array_equal(values[..., 0], flattened.astype(np.float32))
    # the second channel repeats the same positions one whole field later
    assert np.array_equal(values[..., 1], (flattened + grid_shape[0] * grid_shape[1] * grid_shape[2]).astype(np.float32))


def Test_The_Coordinates_Of_A_Whole_Field_Are_The_Whole_Grid() -> None:
    """asserts a batch that takes every point reproduces the framework's own grid, in its own order"""
    grid_shape = (3, 4, 5)
    cached_field = Position_Marked_Field("only", "unit_one", grid_shape)
    every_point = np.arange(cached_field.Point_Count(), dtype=np.intp)
    batch = Batch_Of_Fields([cached_field], [every_point])
    assert np.array_equal(np.asarray(batch.arrays["point_coordinates"])[0], Fractional_Grid_Coordinates(grid_shape))


def Test_One_Seed_Reproduces_The_Same_Batches() -> None:
    """asserts the generator is passed and never held, so one number replays a whole run"""
    cache = Made_Up_Cache(
        Position_Marked_Field("first", "unit_one", (4, 5, 6)),
        Position_Marked_Field("second", "unit_two", (3, 3, 3)),
    )
    source = PointSampledBatches(cache, cache, runs_per_batch=2, points_per_run=5)
    replayed = PointSampledBatches(cache, cache, runs_per_batch=2, points_per_run=5)
    first_generator = np.random.default_rng(20260910)
    second_generator = np.random.default_rng(20260910)
    first_run = [source.Next_Batch(first_generator) for _ in range(3)]
    second_run = [replayed.Next_Batch(second_generator) for _ in range(3)]
    for first_batch, second_batch in zip(first_run, second_run, strict=True):
        for name, drawn in first_batch.arrays.items():
            assert np.array_equal(np.asarray(drawn), np.asarray(second_batch.arrays[name]))
    apart = source.Next_Batch(np.random.default_rng(11))
    assert not np.array_equal(
        np.asarray(apart.arrays["target_values"]), np.asarray(first_run[0].arrays["target_values"])
    )


def Test_The_Validation_Batches_Are_Fixed_And_Grouped_By_Unit() -> None:
    """asserts every unit answers with one batch, the same one on every call"""
    validation_cache = Made_Up_Cache(
        Position_Marked_Field("first", "unit_one", (4, 5, 6)),
        Position_Marked_Field("second", "unit_one", (3, 3, 3)),
        Position_Marked_Field("third", "unit_two", (2, 7, 5)),
    )
    source = PointSampledBatches(validation_cache, validation_cache, 2, 5, validation_points_per_run=9)
    held = source.Validation_Batches()
    assert [unit_key for unit_key, _ in held] == ["unit_one", "unit_two"]
    assert np.asarray(held[0][1].arrays["target_values"]).shape == (2, 9, 1)
    assert np.asarray(held[1][1].arrays["target_values"]).shape == (1, 9, 1)
    for (_, first_batch), (_, second_batch) in zip(held, source.Validation_Batches(), strict=True):
        assert np.array_equal(
            np.asarray(first_batch.arrays["target_values"]), np.asarray(second_batch.arrays["target_values"])
        )


def Test_A_Fixed_Spread_Covers_A_Field_And_Never_Repeats() -> None:
    """asserts the held-out positions are distinct, in range, and the whole field when it is small"""
    spread = Evenly_Spaced_Flat_Indices(1000, 64)
    assert spread.shape == (64,)
    assert len(set(spread.tolist())) == 64
    assert int(spread.min()) >= 0 and int(spread.max()) < 1000
    assert np.array_equal(Evenly_Spaced_Flat_Indices(12, 64), np.arange(12))


def Test_The_Cache_Groups_By_Unit_And_Reports_Its_Bytes() -> None:
    """asserts the cache indexes by unit key and costs four bytes a point"""
    cache = Made_Up_Cache(
        Position_Marked_Field("first", "unit_one", (4, 5, 6)),
        Position_Marked_Field("second", "unit_one", (3, 3, 3)),
        Position_Marked_Field("third", "unit_two", (2, 7, 5), channel_count=2),
    )
    assert cache.Unit_Keys() == ("unit_one", "unit_two")
    assert [cached_field.identifier for cached_field in cache.fields_of_unit["unit_one"]] == ["first", "second"]
    stored_points = 4 * 5 * 6 + 3 * 3 * 3 + 2 * (2 * 7 * 5)
    assert cache.Resident_Bytes() == 4 * stored_points
    reported = cache.Inspect()
    assert np.asarray(reported["point_counts"]).tolist() == [120.0, 27.0, 70.0]
    assert np.asarray(reported["unit_run_counts"]).tolist() == [2.0, 1.0]
    assert np.asarray(reported["grid_extents"]).shape == (3, 3)
    assert float(np.asarray(reported["resident_bytes"])[0]) == float(4 * stored_points)


def Test_The_Statistics_Accumulate_In_Double() -> None:
    """asserts a mean far from zero survives, which a single-precision sum would not"""
    generator = np.random.default_rng(13)
    raised = (1.0e4 + generator.random((1, 64, 64, 64))).astype(np.float32)
    cached_field = Position_Marked_Field("only", "unit_one", (64, 64, 64))
    cache = Made_Up_Cache(
        CachedField(
            identifier=cached_field.identifier,
            run_path=cached_field.run_path,
            unit_key=cached_field.unit_key,
            parameters=cached_field.parameters,
            values=raised,
            grid_shape=(64, 64, 64),
            lattice=cached_field.lattice,
            cell_volume=cached_field.cell_volume,
            covariate_values=cached_field.covariate_values,
        )
    )
    means, deviations = Cached_Field_Statistics(cache)
    widened = raised.astype(np.float64).reshape(-1)
    assert means.dtype == np.float64 and deviations.dtype == np.float64
    assert abs(float(means[0]) - float(widened.mean())) < 1e-9 * float(widened.mean())
    assert abs(float(deviations[0]) - float(widened.std())) < 1e-9 * float(widened.std())


def Test_A_Source_Over_An_Empty_Cache_Says_So() -> None:
    """asserts a cache with nothing in it is refused rather than drawn from"""
    with pytest.raises(ValueError):
        PointSampledBatches(Made_Up_Cache(), Made_Up_Cache(), 2, 5)


def Test_Every_Part_Of_The_Stream_Reports_Named_Arrays() -> None:
    """asserts the field, the cache, the batch and the source all answer with plain-word arrays"""
    cache = Made_Up_Cache(Position_Marked_Field("only", "unit_one", (4, 5, 6)))
    source = PointSampledBatches(cache, cache, runs_per_batch=2, points_per_run=5)
    source.Next_Batch(np.random.default_rng(1))
    for part in (cache.fields[0], cache, source, source.Validation_Batches()[0][1]):
        reported = part.Inspect()
        assert reported
        for name, reported_array in reported.items():
            assert name == name.lower() and " " not in name
            assert np.asarray(reported_array).size > 0
    assert "last_target_values" in source.Inspect()


@pytest.mark.pool
def Test_Point_Sampling_Erases_The_Perovskite_Grid_Spread() -> None:
    """asserts sixteen runs on sixteen distinct grids become one rectangular batch"""
    card = Card_Named("lattice_to_charge")
    training_cache = Build_Field_Cache(card, "train", limit=16)
    validation_cache = Build_Field_Cache(card, "evaluation", limit=4)
    assert len({cached_field.grid_shape for cached_field in training_cache.fields}) == 16
    source = PointSampledBatches(training_cache, validation_cache, runs_per_batch=8, points_per_run=512)
    batch = source.Next_Batch(np.random.default_rng(3))
    assert np.asarray(batch.arrays["target_values"]).shape == (8, 512, 1)
    assert np.asarray(batch.arrays["point_coordinates"]).shape == (8, 512, 3)
    assert np.asarray(batch.arrays["parameter_vectors"]).shape == (8, 6)
    assert len(source.Validation_Batches()) == 4


@pytest.mark.pool
def Test_The_Cache_Holds_In_Single_What_The_Archive_Holds() -> None:
    """asserts the resident values are the stored values, at four bytes a point"""
    card = Card_Named("strain_to_charge")
    cache = Build_Field_Cache(card, "validation", limit=4)
    read_again = list(Parameter_Field_Examples(card, "validation", limit=4))
    assert len(cache.fields) == 4
    resident_points = 0
    for cached_field, example in zip(cache.fields, read_again, strict=True):
        stored = np.asarray(example.target_function.values, dtype=np.float64)
        assert cached_field.identifier == example.identifier
        assert cached_field.values.dtype == np.float32
        assert np.array_equal(cached_field.values.astype(np.float64), stored)
        assert cached_field.grid_shape == stored.shape[1:]
        resident_points += cached_field.Point_Count()
    assert cache.Resident_Bytes() == 4 * resident_points


@pytest.mark.pool
def Test_A_Sampled_Value_Is_The_Stored_Value_In_Its_Own_Cell() -> None:
    """asserts a drawn point's value is what the archive holds at the cell the coordinate names"""
    cache = Build_Field_Cache(Card_Named("strain_to_charge"), "validation", limit=2)
    one_run = FieldCache(cache.card_name, cache.role, cache.fields[:1])
    source = PointSampledBatches(one_run, one_run, runs_per_batch=1, points_per_run=32)
    batch = source.Next_Batch(np.random.default_rng(2))
    cached_field = one_run.fields[0]
    coordinates = np.asarray(batch.arrays["point_coordinates"])[0]
    cells = np.rint(coordinates * np.asarray(cached_field.grid_shape, dtype=np.float64)).astype(np.intp)
    # indexing the three axes directly owes nothing to the flattening the sampler uses
    in_their_cells = cached_field.values[0][cells[:, 0], cells[:, 1], cells[:, 2]]
    assert np.array_equal(np.asarray(batch.arrays["target_values"])[0][:, 0], in_their_cells)
    # a field the store laid out axis-first would be copied whole on every draw from it
    assert cached_field.values.flags["C_CONTIGUOUS"]


@pytest.mark.pool
def Test_The_Statistics_Of_A_Real_Cache_Are_Charge_Densities() -> None:
    """asserts a mean and deviation come back per channel, in double, on live fields"""
    cache = Build_Field_Cache(Card_Named("strain_to_charge"), "validation", limit=8)
    means, deviations = Cached_Field_Statistics(cache)
    assert means.shape == (1,) and deviations.shape == (1,)
    assert means.dtype == np.float64 and deviations.dtype == np.float64
    # two carbon atoms of four valence electrons each, spread over the cell they sit in
    assert 0.1 < float(means[0]) < 2.0
    assert float(deviations[0]) > 0.0
