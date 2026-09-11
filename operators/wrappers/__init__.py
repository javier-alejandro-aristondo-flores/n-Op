"""conservation, residual and conditioning behavior around inner operators, and the conformal calibrator"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray

from operators.framework import Array, Coefficients, Discretization, GridFunction, Operator, Quadrature_Weights
from operators.metrics import Median_Per_Unit
from operators.substrate import Mean_Over_Last_Axis, Sum_Over_Last_Axis

SYMMETRY_ORBIT = "symmetry_orbit"


def Channel_Means(values: Any) -> Any:
    """the mean of each channel on its own, shaped to broadcast back over the grid it came from"""
    flattened = values.reshape(values.shape[0], -1)
    grid_axes = (1,) * (len(values.shape) - 1)
    return Mean_Over_Last_Axis(flattened).reshape(values.shape[0], *grid_axes)


def Renormalization_Scale(values: Any, weight_each: float, target_integral: Any) -> Any:
    """the single factor that puts the quadrature integral of the values on the requested total"""
    integral = Sum_Over_Last_Axis(values.reshape(-1)) * weight_each
    return target_integral / integral


class Conserving(Operator[GridFunction, GridFunction]):
    """an inner operator's output projected onto its exact conservation law"""


    def __init__(
        self,
        inner: Operator[GridFunction, GridFunction],
        law: Literal["renormalize_to_electron_count", "zero_mean"],
    ) -> None:
        self.inner = inner
        self.law = law
        self.last_removed_mean: NDArray[np.float64] | None = None
        self.last_renormalization_scale: NDArray[np.float64] | None = None


    def Forward(self, produced_values: Any, weight_each: float, condition_vector: Any = None) -> Any:
        """the law imposed on values from whichever engine made them, with nothing coerced on the way"""
        if self.law == "zero_mean":
            # channel by channel, so no channel borrows another's offset
            return produced_values - Channel_Means(produced_values)
        if condition_vector is None:
            raise ValueError("renormalization needs the electron count as the condition")
        return produced_values * Renormalization_Scale(produced_values, weight_each, condition_vector[0])


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        produced = self.inner(input_function, output_discretization, condition)
        values = np.asarray(produced.values, dtype=np.float64)
        weights = Quadrature_Weights(produced)
        # a uniform grid gives every point the same weight, so one of them is the whole rule
        weight_each = float(weights[0])
        if self.law == "zero_mean":
            corrected = self.Forward(values, weight_each)
            self.last_removed_mean = np.asarray(float(values.mean()))
        else:
            if condition is None:
                raise ValueError("renormalization needs the electron count as the condition")
            condition_vector = np.asarray(condition.vector, dtype=np.float64)
            corrected = self.Forward(values, weight_each, condition_vector)
            self.last_renormalization_scale = np.asarray(
                float(Renormalization_Scale(values, weight_each, condition_vector[0]))
            )
        return GridFunction(
            np.asarray(corrected, dtype=np.float64), produced.channel_labels, produced.domain, produced.quadrature
        )


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = {f"inner.{name}": value for name, value in self.inner.Inspect().items()}
        if self.last_removed_mean is not None:
            state["last_removed_mean"] = self.last_removed_mean
        if self.last_renormalization_scale is not None:
            state["last_renormalization_scale"] = self.last_renormalization_scale
        return state


class Residual(Operator[GridFunction, GridFunction]):
    """the inner operator's output added back to its input"""


    def __init__(self, inner: Operator[GridFunction, GridFunction]) -> None:
        self.inner = inner


    def Forward(self, input_values: Any, produced_values: Any) -> Any:
        """the correction laid back onto the field it corrects, on whichever engine holds the two"""
        return input_values + produced_values


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        produced = self.inner(input_function, output_discretization, condition)
        summed = np.asarray(
            self.Forward(
                np.asarray(input_function.values, dtype=np.float64),
                np.asarray(produced.values, dtype=np.float64),
            ),
            dtype=np.float64,
        )
        return GridFunction(summed, input_function.channel_labels, produced.domain, produced.quadrature)


    def Inspect(self) -> dict[str, Array]:
        return {f"inner.{name}": value for name, value in self.inner.Inspect().items()}


class Conditioned(Operator[GridFunction, GridFunction]):
    """the inner operator's channels scaled and shifted from the conditioning vector"""


    def __init__(
        self, inner: Operator[GridFunction, GridFunction], channels: int, condition_width: int, seed: int = 0
    ) -> None:
        self.inner = inner
        generator = np.random.default_rng(seed)
        scale = 1.0 / np.sqrt(condition_width)
        self.parameter_values: dict[str, NDArray[np.float64]] = {
            "condition_scale_weights": generator.normal(0.0, scale, size=(channels, condition_width)),
            "condition_shift_weights": generator.normal(0.0, scale, size=(channels, condition_width)),
        }


    def Forward(self, lifted: dict[str, Any], produced_values: Any, condition_vector: Any) -> Any:
        """the channels modulated by weights the caller has lifted, so an engine can differentiate them"""
        # one plus the learned scale, so untrained weights leave the channels alone
        channel_scales = 1.0 + lifted["condition_scale_weights"] @ condition_vector
        channel_shifts = lifted["condition_shift_weights"] @ condition_vector
        grid_axes = (1,) * (len(produced_values.shape) - 1)
        scaled = produced_values * channel_scales.reshape(channel_scales.shape[0], *grid_axes)
        return scaled + channel_shifts.reshape(channel_shifts.shape[0], *grid_axes)


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        produced = self.inner(input_function, output_discretization, condition)
        if condition is None:
            return produced
        modulated = np.asarray(
            self.Forward(
                self.parameter_values,
                np.asarray(produced.values, dtype=np.float64),
                np.asarray(condition.vector, dtype=np.float64),
            ),
            dtype=np.float64,
        )
        return GridFunction(modulated, produced.channel_labels, produced.domain, produced.quadrature)


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = {f"inner.{name}": value for name, value in self.inner.Inspect().items()}
        state.update(self.parameter_values)
        return state


@dataclass(frozen=True, slots=True)
class ConformalInterval:
    """a two-quantile prediction after the calibrated offset has widened it"""

    lower: NDArray[np.float64]
    upper: NDArray[np.float64]


def Nonconformity_Scores(
    lower: NDArray[np.float64], upper: NDArray[np.float64], truth: NDArray[np.float64]
) -> NDArray[np.float64]:
    """one score per run: the largest amount the interval misses the truth by anywhere in it"""
    missed_low = np.asarray(lower, dtype=np.float64) - np.asarray(truth, dtype=np.float64)
    missed_high = np.asarray(truth, dtype=np.float64) - np.asarray(upper, dtype=np.float64)
    worst = np.maximum(missed_low, missed_high)
    return np.asarray(worst.reshape(worst.shape[0], -1).max(axis=1), dtype=np.float64)


def Conformal_Offset(unit_scores: NDArray[np.float64], level: float) -> float:
    """the score at the rank a finite calibration set needs for the level to hold"""
    unit_count = int(unit_scores.shape[0])
    rank = int(np.ceil((unit_count + 1) * level))
    if rank > unit_count:
        raise ValueError(f"{unit_count} units cannot carry a {level:.2f} claim, which needs at least {rank}")
    return float(np.sort(unit_scores)[rank - 1])


def Coverage_Guarantee(unit_count: int, level: float) -> tuple[float, float]:
    """the band the marginal coverage is guaranteed to land in, at this many units"""
    return level, level + 1.0 / (unit_count + 1)


def Coverage_Deviation(unit_count: int, level: float) -> float:
    """the spread of realized coverage across calibration sets of this size"""
    return float(np.sqrt(level * (1.0 - level) / unit_count))


class ConformalCalibrator:
    """split-conformal offsets for a two-quantile head, calibrated over exchangeable units"""


    def __init__(self, level: float = 0.90, unit: str = SYMMETRY_ORBIT) -> None:
        self.level = level
        self.unit = unit
        self.offset: float | None = None
        self.unit_scores = np.zeros(0, dtype=np.float64)


    def Calibrate(
        self,
        lower: NDArray[np.float64],
        upper: NDArray[np.float64],
        truth: NDArray[np.float64],
        unit_keys: Sequence[str],
    ) -> float:
        """the offset the held-out units require, remembered and returned"""
        self.unit_scores = Median_Per_Unit(Nonconformity_Scores(lower, upper, truth), unit_keys)
        self.offset = Conformal_Offset(self.unit_scores, self.level)
        return self.offset


    def __call__(self, lower: NDArray[np.float64], upper: NDArray[np.float64]) -> ConformalInterval:
        """the two quantiles widened by the calibrated offset"""
        if self.offset is None:
            raise ValueError("the calibrator has no offset until it has seen a calibration set")
        return ConformalInterval(
            np.asarray(lower, dtype=np.float64) - self.offset, np.asarray(upper, dtype=np.float64) + self.offset
        )


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = {
            "requested_level": np.asarray(self.level),
            "exchangeable_unit": np.asarray(self.unit),
        }
        if self.offset is None:
            return state
        unit_count = int(self.unit_scores.shape[0])
        guarantee_low, guarantee_high = Coverage_Guarantee(unit_count, self.level)
        state["calibration_unit_scores"] = self.unit_scores
        state["calibration_unit_count"] = np.asarray(unit_count)
        state["conformal_offset"] = np.asarray(self.offset)
        state["coverage_guarantee_low"] = np.asarray(guarantee_low)
        state["coverage_guarantee_high"] = np.asarray(guarantee_high)
        state["coverage_deviation"] = np.asarray(Coverage_Deviation(unit_count, self.level))
        return state
