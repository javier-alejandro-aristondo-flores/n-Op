"""the six physical channel labels this member reads, and the transform each one is prepared through"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

CHARGE_DENSITY = "charge_density"
MAGNETIZATION_DENSITY = "magnetization_density"
ELECTRON_LOCALIZATION_UP = "electron_localization_up"
ELECTRON_LOCALIZATION_DOWN = "electron_localization_down"
LOCAL_POTENTIAL_UP = "local_potential_up"
LOCAL_POTENTIAL_DOWN = "local_potential_down"

CHANNEL_VOCABULARY = (
    CHARGE_DENSITY,
    MAGNETIZATION_DENSITY,
    ELECTRON_LOCALIZATION_UP,
    ELECTRON_LOCALIZATION_DOWN,
    LOCAL_POTENTIAL_UP,
    LOCAL_POTENTIAL_DOWN,
)

# the three pairwise groups the canon's own dedicated competitors and the mask menu are both built from
DENSITY_GROUP = (CHARGE_DENSITY, MAGNETIZATION_DENSITY)
ELF_GROUP = (ELECTRON_LOCALIZATION_UP, ELECTRON_LOCALIZATION_DOWN)
POTENTIAL_GROUP = (LOCAL_POTENTIAL_UP, LOCAL_POTENTIAL_DOWN)

# the four channels stored at the fine native grid, truncated down before every use
FINE_GROUP_LABELS = (CHARGE_DENSITY, MAGNETIZATION_DENSITY, LOCAL_POTENTIAL_UP, LOCAL_POTENTIAL_DOWN)

FINE_SHAPE = (80, 80, 80)
COARSE_SHAPE = (40, 40, 40)

# a positive floor under a training-block statistic that would otherwise divide by zero
STATISTIC_FLOOR = 1e-12

FUNCTIONAL_LEVELS = ("gga_pbe", "hse06", "alloy_unpolarized", "other")

FUNCTIONAL_COVARIATE_WIDTH = len(FUNCTIONAL_LEVELS)


@dataclass(frozen=True, slots=True)
class ChannelStatistics:
    """the training block's own constants every raw channel is prepared and undone through"""

    reference_density: float
    magnetization_scale: float
    potential_scale: float


def Log_Compressed_Density(density: NDArray[np.float64], reference_density: float) -> NDArray[np.float64]:
    """the charge density mapped through the same dynamic-range compression the flagship applies to its own spin channels"""
    return np.log1p(np.maximum(density, 0.0) / reference_density)


def Inverted_Log_Compressed_Density(
    transformed: NDArray[np.float64], reference_density: float
) -> NDArray[np.float64]:
    """the physical charge density a log-compressed channel stands for"""
    return np.expm1(transformed) * reference_density


def Standardized_Magnetization(
    magnetization: NDArray[np.float64], magnetization_scale: float
) -> NDArray[np.float64]:
    """the magnetization density divided by the training block's own scale, no mean removed since the corpus already centers it near zero"""
    return magnetization / magnetization_scale


def Inverted_Standardized_Magnetization(
    transformed: NDArray[np.float64], magnetization_scale: float
) -> NDArray[np.float64]:
    """the physical magnetization density a standardized channel stands for"""
    return transformed * magnetization_scale


def Prepared_Potential(
    potential: NDArray[np.float64], run_mean: float, potential_scale: float
) -> NDArray[np.float64]:
    """one spin channel's own local potential, its run mean removed and the training block's own scale divided out"""
    return (potential - run_mean) / potential_scale


def Inverted_Prepared_Potential(
    transformed: NDArray[np.float64], run_mean: float, potential_scale: float
) -> NDArray[np.float64]:
    """the physical local potential a mean-removed, scaled channel stands for"""
    return transformed * potential_scale + run_mean


def Transform_Channel(
    label: str, raw_value: NDArray[np.float64], statistics: ChannelStatistics
) -> NDArray[np.float64]:
    """one named channel's raw physical values mapped into the space the network is trained in"""
    if label == CHARGE_DENSITY:
        return Log_Compressed_Density(raw_value, statistics.reference_density)
    if label == MAGNETIZATION_DENSITY:
        return Standardized_Magnetization(raw_value, statistics.magnetization_scale)
    if label in ELF_GROUP:
        return raw_value
    if label in POTENTIAL_GROUP:
        return Prepared_Potential(raw_value, float(raw_value.mean()), statistics.potential_scale)
    raise ValueError(f"{label} is not one of this member's six channels")


def Invert_Channel(
    label: str, transformed_value: NDArray[np.float64], statistics: ChannelStatistics
) -> NDArray[np.float64]:
    """the physical values a transformed channel stands for, a potential channel read back as zero-mean by construction"""
    if label == CHARGE_DENSITY:
        return Inverted_Log_Compressed_Density(transformed_value, statistics.reference_density)
    if label == MAGNETIZATION_DENSITY:
        return Inverted_Standardized_Magnetization(transformed_value, statistics.magnetization_scale)
    if label in ELF_GROUP:
        return transformed_value
    if label in POTENTIAL_GROUP:
        # the member-side conservation head already pins the reconstruction to zero mean before this runs
        return Inverted_Prepared_Potential(transformed_value, 0.0, statistics.potential_scale)
    raise ValueError(f"{label} is not one of this member's six channels")


def Functional_Label(run_path: str, campaign: str) -> str:
    """the one functional level a run's own path and campaign resolve to"""
    if campaign == "alloy_ensemble":
        return "alloy_unpolarized"
    lowered = run_path.lower()
    if "hse06" in lowered or "hse" in lowered:
        return "hse06"
    if "gga-pbe" in lowered or "gga_pbe" in lowered:
        return "gga_pbe"
    return "other"


def Functional_One_Hot(run_path: str, campaign: str) -> NDArray[np.float64]:
    """the functional covariate the variable encoding reads through its own condition slot"""
    label = Functional_Label(run_path, campaign)
    vector = np.zeros(FUNCTIONAL_COVARIATE_WIDTH, dtype=np.float64)
    vector[FUNCTIONAL_LEVELS.index(label)] = 1.0
    return vector
