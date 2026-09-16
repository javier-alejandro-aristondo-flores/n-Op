"""the perovskite angle stratum: its examples, split, block, floor predictions and conservation law"""

import numpy as np
from numpy.typing import NDArray

from operators.data import (
    Apply_Standardized_Ridge,
    Fit_Standardized_Ridge,
    Guard_Fresh_Archives,
    Nearest_Training_Run,
    PodBasis,
    Project,
    Reconstruct,
)
from operators.evaluation.scoring import EXTRAPOLATION, INTERPOLATION, ScoredRun
from operators.metrics import Frequency_Split_Relative_L2, Relative_L2
from operators.tasks import Card_Named
from operators.training import FieldCache, Parameter_Field_Examples, ParameterExample
from operators.wrappers import Renormalization_Scale

# lattice_to_charge (test-suite.md II.1b): the angle stratum's one shared shape, measured on all 125 of its runs
PEROVSKITE_ANGLE_GRID_SHAPE = (64, 64, 64)
# measured: every one of the 249 perovskite runs integrates to exactly this, 0 exceptions
PEROVSKITE_ELECTRON_COUNT = 48.0
PEROVSKITE_DEVELOP_FOLD = 0
# fold and holdout label, extrapolation label -- fold 0 is where the budget is chosen, both holdouts reuse it
PEROVSKITE_SPLITS = (
    ("fold_0", None, INTERPOLATION),
    ("holdout_factor_0p8", "holdout_factor_0p8", EXTRAPOLATION),
    ("holdout_factor_1p2", "holdout_factor_1p2", EXTRAPOLATION),
)
# an eighth of a grid's own smallest extent, this report's low/high mode boundary
LATTICE_FREQUENCY_CUTOFF_DIVISOR = 8.0
NEAREST_NEIGHBOR_MARGIN = 0.5


def Lattice_Frequency_Cutoff(grid_shape: tuple[int, ...]) -> float:
    """an eighth of this grid's own smallest extent, the low/high mode boundary this block uses"""
    return float(min(grid_shape)) / LATTICE_FREQUENCY_CUTOFF_DIVISOR


def Perovskite_Angle_Examples(
    role: str, evaluation_fold: int, extrapolation_holdout: str | None
) -> list[ParameterExample]:
    """every angle-stratum example of one loader role, still on the shape the whole stratum shares"""
    card = Card_Named("lattice_to_charge")
    selected: list[ParameterExample] = []
    for example in Parameter_Field_Examples(card, role, evaluation_fold, extrapolation_holdout):
        if not example.unit_key.endswith("_angle"):
            continue
        if np.asarray(example.target_function.values).shape[1:] != PEROVSKITE_ANGLE_GRID_SHAPE:
            continue
        selected.append(example)
    return selected


def Perovskite_Train_Validation_Split(
    examples: list[ParameterExample],
) -> tuple[list[ParameterExample], list[ParameterExample]]:
    """every fifth example, by sorted unit key, held out as this split's own validation slice"""
    ordered = sorted(range(len(examples)), key=lambda position: examples[position].unit_key)
    validation_positions = {position for count, position in enumerate(ordered) if count % 5 == 4}
    train_examples = [example for position, example in enumerate(examples) if position not in validation_positions]
    validation_examples = [example for position, example in enumerate(examples) if position in validation_positions]
    return train_examples, validation_examples


def Perovskite_Cache_Validation_Mask(cache: FieldCache) -> list[bool]:
    """every fifth field, by sorted unit key, held out as this cache's own validation slice"""
    ordered = sorted(range(len(cache.fields)), key=lambda position: cache.fields[position].unit_key)
    validation_positions = {position for count, position in enumerate(ordered) if count % 5 == 4}
    return [position in validation_positions for position in range(len(cache.fields))]


class PerovskiteAngleBlock:
    """the perovskite angle stratum's own runs, every one on the shared 64-cubed grid"""


    def __init__(self, examples: list[ParameterExample], extrapolation: str = INTERPOLATION) -> None:
        parameters: list[NDArray[np.float64]] = []
        fields: list[NDArray[np.float64]] = []
        cell_volumes: list[float] = []
        self.unit_keys: list[str] = []
        self.identifiers: list[str] = []
        for example in examples:
            values = np.asarray(example.target_function.values, dtype=np.float64)
            parameters.append(np.asarray(example.parameters.vector, dtype=np.float64))
            fields.append(values.reshape(-1))
            cell_volumes.append(float(example.target_function.quadrature.cell_volume))
            self.unit_keys.append(example.unit_key)
            self.identifiers.append(example.identifier)
        Guard_Fresh_Archives(self.identifiers)
        self.parameters = np.asarray(parameters)
        self.fields = np.asarray(fields)
        self.cell_volumes = np.asarray(cell_volumes, dtype=np.float64)
        self.extrapolation = extrapolation


    def Scored(self, rebuilt: NDArray[np.float64]) -> list[ScoredRun]:
        """one scored run per field, the card's two metrics, labeled by this block's own extrapolation status"""
        cutoff = Lattice_Frequency_Cutoff(PEROVSKITE_ANGLE_GRID_SHAPE)
        scored: list[ScoredRun] = []
        for run in range(self.fields.shape[0]):
            low, high = Frequency_Split_Relative_L2(
                rebuilt[run].reshape(PEROVSKITE_ANGLE_GRID_SHAPE),
                self.fields[run].reshape(PEROVSKITE_ANGLE_GRID_SHAPE),
                cutoff_modes=cutoff,
            )
            scored.append(
                ScoredRun(
                    identifier=self.identifiers[run],
                    unit_key=self.unit_keys[run],
                    campaign="perovskite_grid",
                    family="angle",
                    errors={
                        "relative_l2": Relative_L2(rebuilt[run], self.fields[run]),
                        "frequency_split_relative_l2_low": low,
                        "frequency_split_relative_l2_high": high,
                    },
                    extrapolation=self.extrapolation,
                )
            )
        return scored


def Perovskite_Ridge_Predictions(
    basis: PodBasis, train: PerovskiteAngleBlock, evaluated: PerovskiteAngleBlock
) -> NDArray[np.float64]:
    """the closed-form floor: lattice parameters onto mode coefficients, decoded through the basis"""
    fitted = Fit_Standardized_Ridge(train.parameters, Project(basis, train.fields))
    return Reconstruct(basis, Apply_Standardized_Ridge(fitted, evaluated.parameters))


def Perovskite_Nearest_Neighbor_Predictions(
    train: PerovskiteAngleBlock, evaluated: PerovskiteAngleBlock
) -> NDArray[np.float64]:
    """the memorization floor: the field of the closest training run in lattice-parameter space"""
    nearest = Nearest_Training_Run(train.parameters, evaluated.parameters)
    return train.fields[nearest]


def Perovskite_Training_Mean_Predictions(
    train: PerovskiteAngleBlock, evaluated: PerovskiteAngleBlock
) -> NDArray[np.float64]:
    """the flat floor: every evaluated run predicted as the training block's own mean field, parameters ignored"""
    return np.tile(train.fields.mean(axis=0), (evaluated.fields.shape[0], 1))


def Perovskite_Renormalization_Scales(
    rebuilt: NDArray[np.float64], cell_volumes: NDArray[np.float64]
) -> NDArray[np.float64]:
    """the exact factor the card's renormalize_to_electron_count law takes on each evaluated run's field"""
    point_count = rebuilt.shape[1]
    return np.asarray(
        [
            float(
                Renormalization_Scale(
                    rebuilt[run], float(cell_volumes[run]) / point_count, np.asarray(PEROVSKITE_ELECTRON_COUNT)
                )
            )
            for run in range(rebuilt.shape[0])
        ],
        dtype=np.float64,
    )


def Perovskite_Conservation_Applied(
    rebuilt: NDArray[np.float64], cell_volumes: NDArray[np.float64]
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """every evaluated run's field renormalized exactly onto the known electron count, with the scale each took"""
    scales = Perovskite_Renormalization_Scales(rebuilt, cell_volumes)
    return rebuilt * scales[:, None], scales
