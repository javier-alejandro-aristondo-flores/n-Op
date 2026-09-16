"""precomputed completion examples held resident, and the masked-reconstruction batch source drawn from them"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.codomain_attention.channels import (
    CHANNEL_VOCABULARY,
    ChannelStatistics,
    COARSE_SHAPE,
    ELF_GROUP,
    FINE_GROUP_LABELS,
    Functional_One_Hot,
    STATISTIC_FLOOR,
    Transform_Channel,
)
from operators.codomain_attention.masking import (
    ALL_MASK_PATTERNS,
    Augmented_Channels,
    Drawn_Grid_Operation,
    MaskPatternName,
    Visible_And_Hidden_Labels,
    Visible_Mask,
)
from operators.codomain_attention.splits import CompletionBlock
from operators.data import Archive_Path, POOL_ROOT
from operators.framework import Spectral_Truncation_Resample
from operators.training import BatchSource, TrainingBatch

# how many training-block runs the reference density and the two scales are fixed from, mirroring the flagship's own sample size
STATISTICS_SAMPLE_SIZE = 80

# the seed the fixed validation masks are drawn from, so a validation score never depends on the trainer's own draw
VALIDATION_MASK_SEED = 20260916


@dataclass(frozen=True, slots=True)
class CompletionExample:
    """one run's own raw channels straight off its archive, each still at its own native resolution"""

    identifier: str
    unit_key: str
    campaign: str
    run_path: str
    raw_channels: dict[str, NDArray[np.float32]]


def Loaded_Completion_Example(
    identifier: str, block: CompletionBlock, pool_root: Path = POOL_ROOT
) -> CompletionExample:
    """one run's six raw channels straight off its archive, each at its own native resolution"""
    campaign = block.campaign_of[identifier]
    with np.load(Archive_Path(campaign, identifier, pool_root)) as archive:
        raw_channels = {label: np.asarray(archive[label], dtype=np.float32) for label in CHANNEL_VOCABULARY}
    return CompletionExample(
        identifier=identifier,
        unit_key=block.unit_of[identifier],
        campaign=campaign,
        run_path=block.run_path_of[identifier],
        raw_channels=raw_channels,
    )


def Loaded_Completion_Examples(
    identifiers: list[str], block: CompletionBlock, pool_root: Path = POOL_ROOT
) -> list[CompletionExample]:
    """every named run, held resident as its own raw channels"""
    return [Loaded_Completion_Example(identifier, block, pool_root) for identifier in identifiers]


def Truncated_Channel(
    raw_field: NDArray[np.float32], label: str, coarse_shape: tuple[int, int, int] = COARSE_SHAPE
) -> NDArray[np.float64]:
    """one channel's own values on the coarse grid, elf already native there and every other channel truncated down"""
    double_field = np.asarray(raw_field, dtype=np.float64)
    if label in ELF_GROUP:
        return double_field
    return Spectral_Truncation_Resample(double_field[None], coarse_shape)[0]


def Channel_Statistics_From_Examples(
    examples: list[CompletionExample], coarse_shape: tuple[int, int, int] = COARSE_SHAPE
) -> ChannelStatistics:
    """the training block's own reference density and channel scales, fixed once and reused unchanged at evaluation"""
    sampled = examples[:STATISTICS_SAMPLE_SIZE]
    density_means: list[float] = []
    magnetization_deviations: list[float] = []
    potential_deviations: list[float] = []
    for example in sampled:
        density_means.append(
            float(Truncated_Channel(example.raw_channels["charge_density"], "charge_density", coarse_shape).mean())
        )
        magnetization_deviations.append(
            float(
                Truncated_Channel(
                    example.raw_channels["magnetization_density"], "magnetization_density", coarse_shape
                ).std()
            )
        )
        for label in ("local_potential_up", "local_potential_down"):
            coarse_potential = Truncated_Channel(example.raw_channels[label], label, coarse_shape)
            potential_deviations.append(float((coarse_potential - coarse_potential.mean()).std()))
    return ChannelStatistics(
        reference_density=max(float(np.mean(density_means)), STATISTIC_FLOOR),
        magnetization_scale=max(float(np.mean(magnetization_deviations)), STATISTIC_FLOOR),
        potential_scale=max(float(np.mean(potential_deviations)), STATISTIC_FLOOR),
    )


def Built_Completion_Step(
    example: CompletionExample,
    pattern: MaskPatternName,
    statistics: ChannelStatistics,
    generator: np.random.Generator,
    coarse_shape: tuple[int, int, int] = COARSE_SHAPE,
) -> tuple[NDArray[np.float32], NDArray[np.float32], NDArray[np.float64]]:
    """one masked-reconstruction step's full transformed target stack, its visible mask and its functional covariate"""
    matrix, translation = Drawn_Grid_Operation(generator)
    fine_stack = np.stack([example.raw_channels[label] for label in FINE_GROUP_LABELS]).astype(np.float64)
    augmented_fine = Augmented_Channels(fine_stack, matrix, translation)
    truncated_fine = Spectral_Truncation_Resample(augmented_fine, coarse_shape)
    coarse_stack = np.stack([example.raw_channels[label] for label in ELF_GROUP]).astype(np.float64)
    augmented_coarse = Augmented_Channels(coarse_stack, matrix, translation)

    raw_by_label: dict[str, NDArray[np.float64]] = dict(zip(FINE_GROUP_LABELS, truncated_fine, strict=True))
    raw_by_label.update(zip(ELF_GROUP, augmented_coarse, strict=True))
    transformed_stack = np.stack(
        [Transform_Channel(label, raw_by_label[label], statistics) for label in CHANNEL_VOCABULARY]
    ).astype(np.float32)

    visible_labels, _ = Visible_And_Hidden_Labels(pattern, CHANNEL_VOCABULARY, generator)
    visible_mask = Visible_Mask(CHANNEL_VOCABULARY, visible_labels)
    condition_vector = Functional_One_Hot(example.run_path, example.campaign)
    return transformed_stack, visible_mask, condition_vector


class CompletionBatches(BatchSource):
    """one masked-reconstruction draw per step, and every fixed validation pattern held for early stopping"""


    def __init__(
        self,
        training_examples: list[CompletionExample],
        validation_examples: list[CompletionExample],
        statistics: ChannelStatistics,
        validation_seed: int = VALIDATION_MASK_SEED,
        coarse_shape: tuple[int, int, int] = COARSE_SHAPE,
        fixed_pattern: MaskPatternName | None = None,
    ) -> None:
        if not training_examples:
            raise ValueError("the completion batch source needs at least one training example to draw from")
        self.training_examples = training_examples
        self.validation_examples = validation_examples
        self.statistics = statistics
        self.coarse_shape = coarse_shape
        # a fine-tune restricts every draw to its own single pattern, a pretrain leaves this unset
        self.drawn_patterns = ALL_MASK_PATTERNS if fixed_pattern is None else (fixed_pattern,)
        self.last_drawn_identifier: str | None = None
        self.last_drawn_pattern: MaskPatternName | None = None
        self.validation_batches = self.Built_Validation_Batches(validation_seed)


    def Built_Validation_Batches(self, seed: int) -> tuple[tuple[str, TrainingBatch], ...]:
        """one fixed batch per mask pattern, every held-out run stacked under that pattern's own fixed draw"""
        generator = np.random.default_rng(seed)
        batches: list[tuple[str, TrainingBatch]] = []
        for pattern in ALL_MASK_PATTERNS:
            stacks: list[NDArray[np.float32]] = []
            masks: list[NDArray[np.float32]] = []
            conditions: list[NDArray[np.float64]] = []
            for example in self.validation_examples:
                stack, mask, condition = Built_Completion_Step(
                    example, pattern, self.statistics, generator, self.coarse_shape
                )
                stacks.append(stack)
                masks.append(mask)
                conditions.append(condition)
            if not stacks:
                continue
            batches.append(
                (
                    pattern,
                    TrainingBatch(
                        {
                            "full_transformed_stack": np.stack(stacks),
                            "visible_mask": np.stack(masks),
                            "condition_vector": np.stack(conditions),
                        }
                    ),
                )
            )
        return tuple(batches)


    def Next_Batch(self, generator: np.random.Generator) -> TrainingBatch:
        example = self.training_examples[int(generator.integers(0, len(self.training_examples)))]
        pattern = self.drawn_patterns[int(generator.integers(0, len(self.drawn_patterns)))]
        stack, mask, condition = Built_Completion_Step(example, pattern, self.statistics, generator, self.coarse_shape)
        self.last_drawn_identifier = example.identifier
        self.last_drawn_pattern = pattern
        return TrainingBatch(
            {
                "full_transformed_stack": stack[None],
                "visible_mask": mask[None],
                "condition_vector": condition[None],
            }
        )


    def Validation_Batches(self) -> tuple[tuple[str, TrainingBatch], ...]:
        return self.validation_batches


    def Inspect(self) -> dict[str, Any]:
        state: dict[str, Any] = {
            "training_example_count": np.asarray([len(self.training_examples)], dtype=np.float64),
            "validation_example_count": np.asarray([len(self.validation_examples)], dtype=np.float64),
        }
        if self.last_drawn_identifier is not None:
            state["last_drawn_identifier"] = np.asarray(self.last_drawn_identifier)
        if self.last_drawn_pattern is not None:
            state["last_drawn_pattern"] = np.asarray(self.last_drawn_pattern)
        return state
