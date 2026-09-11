"""the invariance axes, exact resampling and the diamond operations and the nulls"""

import re
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from operators.framework import (
    Apply_Grid_Operation,
    Array,
    Block_Gap_Null,
    Coefficients,
    Diamond_Grid_Operations,
    Discretization,
    Discretization_Invariance_Report,
    Domain,
    Equivariance_Errors,
    GridFunction,
    GridSpec,
    InvarianceProbe,
    K_Quality_Tier,
    Spectral_Truncation_Resample,
    SupercellTwin,
    UniformGridQuadrature,
)
from operators.tasks import CARDS, Card_Named

KNOWN_SPLITS = {
    "paired_fields_fivefold",
    "strain_atlas_holdout",
    "perovskite_folds",
    "supercell_defect_train_alloy_holdout",
}


SUITE_PATH = Path(__file__).resolve().parent.parent.parent / "test-suite.md"

CUBE = Domain(lattice=np.eye(3))


class ResamplingOperator:
    """an operator that carries its input onto the requested grid and changes nothing else"""


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        """the input field, exactly, on whichever grid was asked for"""
        assert isinstance(output_discretization, GridSpec)
        values = Spectral_Truncation_Resample(
            np.asarray(input_function.values, dtype=np.float64), output_discretization.shape
        )
        return GridFunction(values, input_function.channel_labels, input_function.domain, input_function.quadrature)


    def Inspect(self) -> dict[str, Array]:
        """nothing is learned here, so nothing is exposed"""
        return {}


def Field_On_Grid(values: NDArray[np.float64]) -> GridFunction:
    """a two-channel field wrapped as a function on the unit cube"""
    point_count = int(np.prod(values.shape[1:]))
    labels = tuple(f"channel_{place}" for place in range(values.shape[0]))
    return GridFunction(values, labels, CUBE, UniformGridQuadrature(1.0, point_count))


def Named_Lines(report: dict[str, Array], name: str) -> list[str]:
    """one of the report's string arrays read back as plain strings"""
    return [str(line) for line in np.asarray(report[name])]


def Identity_Probes(extent: int) -> list[InvarianceProbe]:
    """probes whose truth is their own input, which is the map a resampler performs exactly"""
    field = Band_Limited_Field(extent)
    return [InvarianceProbe(Field_On_Grid(field), field)]


def Band_Limited_Field(extent: int) -> NDArray[np.float64]:
    """a two-channel field holding only modes below any test Nyquist"""
    coordinates = np.arange(extent) / extent
    x_coordinate, y_coordinate, z_coordinate = np.meshgrid(coordinates, coordinates, coordinates, indexing="ij")
    first = 1.0 + np.cos(2 * np.pi * x_coordinate) + np.sin(2 * np.pi * (y_coordinate - z_coordinate))
    second = 0.5 + np.sin(2 * np.pi * y_coordinate) * np.cos(2 * np.pi * x_coordinate)
    return np.stack([first, second])


def Test_Resampling_Is_Exact_On_Band_Limited_Fields() -> None:
    """downsampling and the round trip reproduce band-limited fields exactly"""
    fine = Band_Limited_Field(8)
    coarse = Spectral_Truncation_Resample(fine, (6, 6, 6))
    reference = Band_Limited_Field(6)
    assert np.allclose(coarse, reference, atol=1e-12)
    round_trip = Spectral_Truncation_Resample(coarse, (8, 8, 8))
    assert np.allclose(round_trip, fine, atol=1e-12)


def Test_The_Diamond_Group_Has_Its_Recorded_Structure() -> None:
    """48 operations, half translation-free and half glide or center shifted"""
    operations = Diamond_Grid_Operations()
    assert len(operations) == 48
    translation_free = sum(1 for _, translation in operations if float(np.abs(translation).sum()) == 0.0)
    assert translation_free == 24


def Test_Grid_Operations_Compose_Exactly() -> None:
    """an operation permutes voxels one to one, and keeps the multiset"""
    field = Band_Limited_Field(8)
    for matrix, shift in Diamond_Grid_Operations()[:6]:
        moved = Apply_Grid_Operation(field, matrix, shift)
        assert moved.shape == field.shape
        assert np.allclose(np.sort(moved.ravel()), np.sort(field.ravel()))


def Test_An_Equivariant_Model_Scores_Zero() -> None:
    """the identity model has zero equivariance error under every operation"""
    field = Band_Limited_Field(8)
    errors = Equivariance_Errors(lambda values: values, field, Diamond_Grid_Operations())
    assert errors.shape == (48,)
    assert float(errors.max()) < 1e-12


def Test_The_Block_Gap_Null_Is_Zero_For_Exact_Tiling() -> None:
    """zero gap to itself, and a real gap once perturbed"""
    primitive = Band_Limited_Field(4)
    supercell = np.tile(primitive, (1, 2, 2, 2))
    assert Block_Gap_Null(primitive, supercell, (2, 2, 2)) < 1e-12
    assert Block_Gap_Null(primitive, supercell + 0.05, (2, 2, 2)) > 0.0


def Test_The_K_Quality_Gate_Tiers() -> None:
    """the tier boundaries recorded in the suite"""
    assert K_Quality_Tier(4) == "below_gate"
    assert K_Quality_Tier(27) == "permissive"
    assert K_Quality_Tier(50) == "recommended"
    assert K_Quality_Tier(64) == "high_fidelity"


def Test_Task_Cards_Are_Unique_And_Point_At_Known_Splits() -> None:
    """card names are unique and retrievable, and their splits are defined"""
    names = [card.name for card in CARDS]
    assert len(names) == len(set(names))
    for card in CARDS:
        assert Card_Named(card.name) is card
        assert card.split in KNOWN_SPLITS


def Test_Every_Card_Cites_A_Section_And_Entry_The_Suite_Really_Has() -> None:
    """a card is a claim about canon, so its citation has to resolve to a heading that exists"""
    canon = SUITE_PATH.read_text()
    unresolved: list[str] = []
    for card in CARDS:
        for section in re.findall(r"§(\d+)", card.suite_card):
            if f"\n## {section}. " not in canon:
                unresolved.append(f"{card.name}: no section {section}")
        for entry in re.findall(r"\b([IVX]+\.\d+)[a-z]?\b", card.suite_card):
            if f"\n#### {entry} " not in canon:
                unresolved.append(f"{card.name}: no entry {entry}")
    assert unresolved == [], unresolved


def Test_The_Cross_Fidelity_Pattern_Has_Both_Of_Its_Members() -> None:
    """pattern IV names a field member and a spectral one, and the conformal entry is no member"""
    cross_fidelity = [card for card in CARDS if "§5" in card.suite_card]
    assert [card.name for card in cross_fidelity] == ["cheap_to_accurate_charge", "cheap_to_accurate_states"]
    for card in cross_fidelity:
        assert card.inputs == card.targets
        assert card.loss == "delta_mean_squared_error"
        assert card.split == "strain_atlas_holdout"
    assert Card_Named("cheap_to_accurate_states").metrics[0] == "gap_edge_error"


def Test_A_Resampler_Sits_Exactly_On_The_Truncation_Null() -> None:
    """an operator handed only the coarse input cannot beat carrying the coarse truth back up"""
    report = Discretization_Invariance_Report(
        ResamplingOperator(), Card_Named("charge_to_localization"), Identity_Probes(8), (6, 6, 6)
    )
    assert Named_Lines(report, "axes_reported") == ["resolution", "symmetry"]
    assert np.allclose(np.asarray(report["resolution_model_error"]), np.asarray(report["resolution_truncation_null"]))
    assert float(np.abs(np.asarray(report["resolution_skill"])).max()) < 1e-12
    assert tuple(np.asarray(report["resolution_training_shape"])) == (6, 6, 6)
    # the null is the floor of the axis, so a skill of zero is the honest reading, not a failure
    assert float(np.asarray(report["resolution_truncation_null"]).min()) > 0.0


def Test_A_Resampler_Is_Equivariant_Under_Every_Diamond_Operation() -> None:
    """resampling onto the same grid commutes with all 48 operations, exactly"""
    report = Discretization_Invariance_Report(
        ResamplingOperator(), Card_Named("charge_to_localization"), Identity_Probes(8), (8, 8, 8)
    )
    assert np.asarray(report["symmetry_equivariance_error"]).shape == (1, 48)
    assert float(np.asarray(report["symmetry_median_equivariance_error"])) < 1e-12


def Test_The_Symmetry_Axis_Stands_Down_Off_A_Quarter_Divisible_Cube() -> None:
    """the glide translations are whole voxels only on a quarter-divisible cube, and it says so"""
    field = Band_Limited_Field(6)
    report = Discretization_Invariance_Report(
        ResamplingOperator(),
        Card_Named("charge_to_localization"),
        [InvarianceProbe(Field_On_Grid(field), field)],
        (6, 6, 6),
    )
    assert Named_Lines(report, "axes_reported") == ["resolution"]
    assert any("symmetry" in line for line in Named_Lines(report, "axes_skipped"))


def Test_The_Supercell_Axis_Says_When_It_Cannot_Resolve_Model_Quality() -> None:
    """a model error at or under the block gap measures the campaigns' systematics, not the model"""
    primitive = Band_Limited_Field(4)
    exact_tiling = np.tile(primitive, (1, 2, 2, 2))
    close_truth = exact_tiling + 0.01
    far_truth = exact_tiling + 0.5
    twins = [
        SupercellTwin(Field_On_Grid(close_truth + 1.0), close_truth, primitive, (2, 2, 2)),
        SupercellTwin(Field_On_Grid(far_truth), far_truth, primitive, (2, 2, 2)),
    ]
    report = Discretization_Invariance_Report(ResamplingOperator(), Card_Named("charge_to_localization"), twins=twins)
    assert "supercell" in Named_Lines(report, "axes_reported")
    nulls = np.asarray(report["supercell_block_gap_null"])
    errors = np.asarray(report["supercell_model_error"])
    # the first twin's campaigns nearly agree, so its model error is the model's; the second's is not
    assert float(errors[0]) > float(nulls[0]) and float(errors[1]) <= float(nulls[1])
    assert list(np.asarray(report["supercell_resolves_model_quality"])) == [True, False]


def Test_A_Curve_Card_Reports_The_K_Gate_And_Withholds_The_Grid_Axes() -> None:
    """a spectral card has no field to resample or rotate, and the report names what it skipped"""
    report = Discretization_Invariance_Report(
        ResamplingOperator(),
        Card_Named("cheap_to_accurate_states"),
        irreducible_kpoint_counts=(4, 27, 50, 64),
    )
    assert Named_Lines(report, "axes_reported") == ["k_quality"]
    tiers = ["below_gate", "permissive", "recommended", "high_fidelity"]
    assert Named_Lines(report, "kpoint_quality_tier") == tiers
    skipped = " ".join(Named_Lines(report, "axes_skipped"))
    assert "resolution: the card's target is a curve" in skipped
    assert "symmetry: the card's target is a curve" in skipped
    assert "supercell: no twin runs supplied" in skipped
    assert str(report["task_name"]) == "cheap_to_accurate_states"
