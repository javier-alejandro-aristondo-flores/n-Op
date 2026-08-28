"""conservation, residual and conditioning behavior around inner operators"""

from typing import Literal

import numpy as np
from numpy.typing import NDArray

from operators.framework import Array, Coefficients, Discretization, GridFunction, Operator, Quadrature_Weights


class Conserving(Operator[GridFunction, GridFunction]):
    """an inner operator's output projected onto its exact conservation law"""


    def __init__(
        self,
        inner: Operator[GridFunction, GridFunction],
        law: Literal["renormalize_to_electron_count", "zero_mean"],
    ) -> None:
        self.inner = inner
        self.law = law
        self.last_correction_scale: NDArray[np.float64] | None = None


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
            # channel by channel, so no channel borrows another's offset
            corrected = values - values.mean(axis=(1, 2, 3), keepdims=True)
            self.last_correction_scale = np.asarray([float(values.mean())])
        else:
            if condition is None:
                raise ValueError("renormalization needs the electron count as the condition")
            # one scale puts the integrated density back on the electron count
            target_integral = float(np.asarray(condition.vector)[0])
            integral = float(values.sum() * weight_each)
            scale = target_integral / integral
            corrected = values * scale
            self.last_correction_scale = np.asarray([scale])
        return GridFunction(corrected, produced.channel_labels, produced.domain, produced.quadrature)


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = {f"inner.{name}": value for name, value in self.inner.Inspect().items()}
        if self.last_correction_scale is not None:
            state["last_correction_scale"] = self.last_correction_scale
        return state


class Residual(Operator[GridFunction, GridFunction]):
    """the inner operator's output added back to its input"""


    def __init__(self, inner: Operator[GridFunction, GridFunction]) -> None:
        self.inner = inner


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        produced = self.inner(input_function, output_discretization, condition)
        summed = np.asarray(input_function.values, dtype=np.float64) + np.asarray(
            produced.values, dtype=np.float64
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


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        produced = self.inner(input_function, output_discretization, condition)
        if condition is None:
            return produced
        condition_vector = np.asarray(condition.vector, dtype=np.float64)
        # one plus the learned scale, so untrained weights leave the channels alone
        channel_scales = 1.0 + self.parameter_values["condition_scale_weights"] @ condition_vector
        channel_shifts = self.parameter_values["condition_shift_weights"] @ condition_vector
        values = np.asarray(produced.values, dtype=np.float64)
        modulated = values * channel_scales[:, None, None, None] + channel_shifts[:, None, None, None]
        return GridFunction(modulated, produced.channel_labels, produced.domain, produced.quadrature)


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = {f"inner.{name}": value for name, value in self.inner.Inspect().items()}
        state.update(self.parameter_values)
        return state
