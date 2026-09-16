"""the mask patterns a training step draws between, and the exact grid augmentation applied before them"""

from typing import Literal

import numpy as np
from numpy.typing import NDArray

from operators.codomain_attention.channels import DENSITY_GROUP, ELF_GROUP, POTENTIAL_GROUP
from operators.framework import Apply_Grid_Operation, Diamond_Grid_Operations

type MaskPatternName = Literal[
    "density_to_elf_and_potential",
    "density_and_potential_to_elf",
    "elf_to_density",
    "potential_to_density",
    "random_subset",
]

# the four named patterns mirror the canon's own pairwise task cards exactly, density carrying magnetization beside it
NAMED_MASK_PATTERNS: tuple[MaskPatternName, ...] = (
    "density_to_elf_and_potential",
    "density_and_potential_to_elf",
    "elf_to_density",
    "potential_to_density",
)

ALL_MASK_PATTERNS: tuple[MaskPatternName, ...] = NAMED_MASK_PATTERNS + ("random_subset",)

RANDOM_SUBSET_VISIBLE_PROBABILITY = 0.5

DIAMOND_GRID_OPERATIONS = Diamond_Grid_Operations()


def Random_Subset(present_labels: tuple[str, ...], generator: np.random.Generator) -> tuple[str, ...]:
    """every present label independently visible or hidden, redrawn until both sides are non-empty"""
    while True:
        drawn = tuple(
            label for label in present_labels if generator.random() < RANDOM_SUBSET_VISIBLE_PROBABILITY
        )
        if drawn and len(drawn) < len(present_labels):
            return drawn


def Visible_Labels(
    pattern: MaskPatternName, present_labels: tuple[str, ...], generator: np.random.Generator
) -> tuple[str, ...]:
    """the present channel labels one mask pattern reveals, drawn fresh every call for the random pattern"""
    if pattern == "density_to_elf_and_potential":
        group = DENSITY_GROUP
    elif pattern == "density_and_potential_to_elf":
        group = DENSITY_GROUP + POTENTIAL_GROUP
    elif pattern == "elf_to_density":
        group = ELF_GROUP
    elif pattern == "potential_to_density":
        group = POTENTIAL_GROUP
    else:
        return Random_Subset(present_labels, generator)
    return tuple(label for label in group if label in present_labels)


def Hidden_Labels(visible_labels: tuple[str, ...], present_labels: tuple[str, ...]) -> tuple[str, ...]:
    """every present channel a pattern's own visible set does not reveal"""
    return tuple(label for label in present_labels if label not in visible_labels)


def Visible_And_Hidden_Labels(
    pattern: MaskPatternName, present_labels: tuple[str, ...], generator: np.random.Generator
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """one pattern's visible and hidden split, redrawn until both sides are non-empty"""
    while True:
        visible_labels = Visible_Labels(pattern, present_labels, generator)
        hidden_labels = Hidden_Labels(visible_labels, present_labels)
        if visible_labels and hidden_labels:
            return visible_labels, hidden_labels


def Drawn_Grid_Operation(generator: np.random.Generator) -> tuple[NDArray[np.int64], NDArray[np.float64]]:
    """one of the 48 exact diamond-group operations, chosen fresh"""
    matrix, translation = DIAMOND_GRID_OPERATIONS[int(generator.integers(0, len(DIAMOND_GRID_OPERATIONS)))]
    return matrix, translation


def Augmented_Channels(
    stacked_channels: NDArray[np.float64], matrix: NDArray[np.int64], translation: NDArray[np.float64]
) -> NDArray[np.float64]:
    """a channel-stacked field under one exact grid operation, every channel moved by the same symmetry"""
    return Apply_Grid_Operation(stacked_channels, matrix, translation)


def Visible_Mask(present_labels: tuple[str, ...], visible_labels: tuple[str, ...]) -> NDArray[np.float32]:
    """one flag per present channel in canonical order, one where visible and zero where hidden"""
    return np.asarray([1.0 if label in visible_labels else 0.0 for label in present_labels], dtype=np.float32)
