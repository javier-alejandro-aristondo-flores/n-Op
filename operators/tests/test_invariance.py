"""Checks the invariance axes: exact resampling, the diamond operations, and the nulls."""

import numpy as np

from numpy.typing import NDArray
from operators.framework.invariance import (
    Apply_Grid_Operation,
    Block_Gap_Null,
    Diamond_Grid_Operations,
    Equivariance_Errors,
    K_Quality_Tier,
    Spectral_Truncation_Resample,
)
from operators.tasks import CARDS, Card_Named

KNOWN_SPLITS = {
    "paired_fields_fivefold",
    "strain_atlas_holdout",
    "perovskite_folds",
    "supercell_defect_train_alloy_holdout",
}


def Band_Limited_Field(extent: int) -> NDArray[np.float64]:
    """Returns a two-channel field holding only modes below any test Nyquist."""
    coordinates = np.arange(extent) / extent
    x_coordinate, y_coordinate, z_coordinate = np.meshgrid(coordinates, coordinates, coordinates, indexing="ij")
    first = 1.0 + np.cos(2 * np.pi * x_coordinate) + np.sin(2 * np.pi * (y_coordinate - z_coordinate))
    second = 0.5 + np.sin(2 * np.pi * y_coordinate) * np.cos(2 * np.pi * x_coordinate)
    return np.stack([first, second])


def Test_Resampling_Is_Exact_On_Band_Limited_Fields() -> None:
    """Asserts downsample and the round trip reproduce band-limited fields exactly."""
    fine = Band_Limited_Field(8)
    coarse = Spectral_Truncation_Resample(fine, (6, 6, 6))
    reference = Band_Limited_Field(6)
    assert np.allclose(coarse, reference, atol=1e-12)
    round_trip = Spectral_Truncation_Resample(coarse, (8, 8, 8))
    assert np.allclose(round_trip, fine, atol=1e-12)


def Test_The_Diamond_Group_Has_Its_Recorded_Structure() -> None:
    """Asserts 48 operations, half translation-free and half glide-or-center shifted."""
    operations = Diamond_Grid_Operations()
    assert len(operations) == 48
    translation_free = sum(1 for _, translation in operations if float(np.abs(translation).sum()) == 0.0)
    assert translation_free == 24


def Test_Grid_Operations_Compose_Exactly() -> None:
    """Asserts an operation permutes voxels bijectively and preserves the multiset."""
    field = Band_Limited_Field(8)
    for matrix, shift in Diamond_Grid_Operations()[:6]:
        moved = Apply_Grid_Operation(field, matrix, shift)
        assert moved.shape == field.shape
        assert np.allclose(np.sort(moved.ravel()), np.sort(field.ravel()))


def Test_An_Equivariant_Model_Scores_Zero() -> None:
    """Asserts the identity model has zero equivariance error under every operation."""
    field = Band_Limited_Field(8)
    errors = Equivariance_Errors(lambda values: values, field, Diamond_Grid_Operations())
    assert errors.shape == (48,)
    assert float(errors.max()) < 1e-12


def Test_The_Block_Gap_Null_Is_Zero_For_Exact_Tiling() -> None:
    """Asserts a tiled primitive field has zero gap to itself and a real gap when perturbed."""
    primitive = Band_Limited_Field(4)
    supercell = np.tile(primitive, (1, 2, 2, 2))
    assert Block_Gap_Null(primitive, supercell, (2, 2, 2)) < 1e-12
    assert Block_Gap_Null(primitive, supercell + 0.05, (2, 2, 2)) > 0.0


def Test_The_K_Quality_Gate_Tiers() -> None:
    """Asserts the tier boundaries recorded in the suite."""
    assert K_Quality_Tier(4) == "below_gate"
    assert K_Quality_Tier(27) == "permissive"
    assert K_Quality_Tier(50) == "recommended"
    assert K_Quality_Tier(64) == "high_fidelity"


def Test_Task_Cards_Are_Unique_And_Point_At_Known_Splits() -> None:
    """Asserts card names are unique, retrievable, and their splits are defined."""
    names = [card.name for card in CARDS]
    assert len(names) == len(set(names))
    for card in CARDS:
        assert Card_Named(card.name) is card
        assert card.split in KNOWN_SPLITS
