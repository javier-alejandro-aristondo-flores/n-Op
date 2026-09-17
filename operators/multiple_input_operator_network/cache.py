"""the fitted proper-orthogonal bases and the point-sampled cache built from them"""

import json
from collections.abc import Iterator
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from operators.data import (
    ARTIFACT_DIRECTORY,
    Basis_Decay_Gate,
    Gram_Pod,
    POOL_ROOT,
    PodBasis,
    Project,
    Reconstruction_Error_Curve,
)
from operators.factorized_fourier import Reference_Density
from operators.multiple_input_operator_network import (
    Density_Channels,
    Potential_Channels,
    Standardized_Potential_Coefficients,
)
from operators.tasks import Card_Named
from operators.training import CachedField, FieldCache, Paired_Field_Examples, TrainingExample

CARD_NAME = "charge_and_potential_to_localization"

# the shape a full cubic-block run's own four-channel input carries
CUBIC_INPUT_SHAPE = (4, 80, 80, 80)

EVALUATION_FOLDS = (0,)

VALIDATION_FOLDS = (1,)

MEMBER_TRAIN_FOLDS = (2, 3, 4)

FLOOR_TRAIN_FOLDS = (1, 2, 3, 4)

BASIS_RANK = 32


def Cubic_Block_Examples(
    role_folds: tuple[int, ...], pool_root: Path = POOL_ROOT, limit: int | None = None
) -> Iterator[TrainingExample]:
    """the paired-field card's own examples restricted to the eighty-cube cubic block, for the given folds"""
    card = Card_Named(CARD_NAME)
    for fold in role_folds:
        examples = Paired_Field_Examples(card, "evaluation", evaluation_fold=fold, pool_root=pool_root, limit=limit)
        for example in examples:
            if example.input_function.values.shape == CUBIC_INPUT_SHAPE:
                yield example


def Unit_Key_By_Identifier(artifact_directory: Path = ARTIFACT_DIRECTORY) -> dict[str, str]:
    """every paired-fields run identifier mapped to the exchangeable unit it belongs to"""
    payload = json.loads((artifact_directory / "paired_fields_fivefold.json").read_text())
    mapping: dict[str, str] = {}
    for unit_key, unit in payload.items():
        for identifier in unit["run_identifiers"]:
            mapping[identifier] = unit_key
    return mapping


def Density_Snapshot(example: TrainingExample, reference_density: float) -> NDArray[np.float64]:
    """one run's density-branch channels, flattened to the row a basis fit or projection reads"""
    return Density_Channels(example.input_function, reference_density).reshape(-1)


def Potential_Snapshot(example: TrainingExample) -> NDArray[np.float64]:
    """one run's potential-branch channels, flattened to the row a basis fit or projection reads"""
    return Potential_Channels(example.input_function).reshape(-1)


def Fitted_Reference_Density(examples: list[TrainingExample]) -> float:
    """the training block's own mean spin density, the density branch's log-compression scale"""
    density_fields = [np.asarray(example.input_function.values)[0] for example in examples]
    magnetization_fields = [np.asarray(example.input_function.values)[1] for example in examples]
    return Reference_Density(density_fields, magnetization_fields)


def Potential_Coefficient_Statistics(
    potential_basis: PodBasis, examples: list[TrainingExample]
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """each potential coefficient's own mean and spread across the training block, the branch's own standardization"""
    raw_coefficients = np.stack(
        [Project(potential_basis, Potential_Snapshot(example)[None, :])[0] for example in examples]
    )
    mean = raw_coefficients.mean(axis=0)
    spread = raw_coefficients.std(axis=0)
    # a coefficient that never varies across the whole training block would divide the branch input by zero
    spread[spread == 0.0] = 1.0
    return mean, spread


def Basis_Decay_Report(snapshots: NDArray[np.float64]) -> dict[str, float]:
    """reconstruction error at ranks eight, sixteen and thirty-two, beside the canon's own decay gate verdict"""
    curve = Reconstruction_Error_Curve(snapshots)
    passed, reached_rank = Basis_Decay_Gate(snapshots)
    report: dict[str, float] = {"gate_passed": float(passed), "gate_reached_rank": float(reached_rank)}
    # a block smaller than the gate's own rank still reports whichever of the three it can reach
    for rank in (8, 16, 32):
        if rank <= curve.shape[0]:
            report[f"error_at_rank_{rank}"] = float(curve[rank - 1])
    return report


def Fitted_Bases(
    pool_root: Path = POOL_ROOT, limit: int | None = None
) -> tuple[PodBasis, PodBasis, float, NDArray[np.float64], NDArray[np.float64], dict[str, dict[str, float]]]:
    """the two bases fit on the pooled training folds, the reference density, the potential standardization, decay"""
    examples = list(Cubic_Block_Examples(FLOOR_TRAIN_FOLDS, pool_root, limit))
    if not examples:
        raise ValueError("no cubic-block training examples were found to fit the bases on")
    reference_density = Fitted_Reference_Density(examples)
    density_snapshots = np.stack([Density_Snapshot(example, reference_density) for example in examples])
    potential_snapshots = np.stack([Potential_Snapshot(example) for example in examples])
    decay = {
        "density": Basis_Decay_Report(density_snapshots),
        "potential": Basis_Decay_Report(potential_snapshots),
    }
    density_basis = Gram_Pod(density_snapshots, rank=BASIS_RANK)
    potential_basis = Gram_Pod(potential_snapshots, rank=BASIS_RANK)
    potential_coefficient_mean, potential_coefficient_scale = Potential_Coefficient_Statistics(
        potential_basis, examples
    )
    return (
        density_basis,
        potential_basis,
        reference_density,
        potential_coefficient_mean,
        potential_coefficient_scale,
        decay,
    )


def Localization_Cache(
    role_folds: tuple[int, ...],
    density_basis: PodBasis,
    potential_basis: PodBasis,
    reference_density: float,
    potential_coefficient_mean: NDArray[np.float64],
    potential_coefficient_scale: NDArray[np.float64],
    role: str,
    pool_root: Path = POOL_ROOT,
    limit: int | None = None,
) -> FieldCache:
    """one role's cubic-block runs, each reduced to its two branch coefficient vectors beside its localization target"""
    unit_keys = Unit_Key_By_Identifier()
    cached_fields: list[CachedField] = []
    for example in Cubic_Block_Examples(role_folds, pool_root, limit):
        density_coefficients = Project(density_basis, Density_Snapshot(example, reference_density)[None, :])[0]
        raw_potential_coefficients = Project(potential_basis, Potential_Snapshot(example)[None, :])[0]
        potential_coefficients = Standardized_Potential_Coefficients(
            raw_potential_coefficients, potential_coefficient_mean, potential_coefficient_scale
        )
        parameters = np.concatenate([density_coefficients, potential_coefficients])
        target_values = np.ascontiguousarray(np.asarray(example.target_function.values), dtype=np.float32)
        cached_fields.append(
            CachedField(
                identifier=example.identifier,
                run_path=example.identifier,
                unit_key=unit_keys.get(example.identifier, example.identifier),
                parameters=parameters,
                values=target_values,
                grid_shape=tuple(int(extent) for extent in target_values.shape[1:]),
                lattice=np.asarray(example.target_function.domain.lattice, dtype=np.float64),
                cell_volume=float(example.target_function.quadrature.cell_volume),
                covariate_values={},
            )
        )
    return FieldCache(CARD_NAME, role, tuple(cached_fields))
