"""Wrappers: conservation, residual, and conditioning behavior around inner operators."""

from typing import Literal

import numpy
from numpy.typing import NDArray

from operators.framework import Coefficients, Discretization, GridFunction, Operator
from operators.framework.domain import Array
from operators.framework.integral import Quadrature_Weights


class Conserving(Operator[GridFunction, GridFunction]):
    """Projects an inner operator's output onto its exact conservation law."""


    def __init__(
        self,
        inner: Operator[GridFunction, GridFunction],
        law: Literal["renormalize_to_electron_count", "zero_mean"],
    ) -> None:
        self.inner = inner
        self.law = law
        self.last_correction_scale: NDArray[numpy.float64] | None = None


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        produced = self.inner(input_function, output_discretization, condition)
        values = numpy.asarray(produced.values, dtype=numpy.float64)
        weights = Quadrature_Weights(produced)
        weight_each = float(weights[0])
        if self.law == "zero_mean":
            corrected = values - values.mean(axis=(1, 2, 3), keepdims=True)
            self.last_correction_scale = numpy.asarray([float(values.mean())])
        else:
            if condition is None:
                raise ValueError("renormalization needs the electron count as the condition")
            target_integral = float(numpy.asarray(condition.vector)[0])
            integral = float(values.sum() * weight_each)
            scale = target_integral / integral
            corrected = values * scale
            self.last_correction_scale = numpy.asarray([scale])
        return GridFunction(corrected, produced.channel_labels, produced.domain, produced.quadrature)


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = {f"inner.{name}": value for name, value in self.inner.Inspect().items()}
        if self.last_correction_scale is not None:
            state["last_correction_scale"] = self.last_correction_scale
        return state


class Residual(Operator[GridFunction, GridFunction]):
    """Adds the inner operator's output to its input, starting exactly at the identity."""


    def __init__(self, inner: Operator[GridFunction, GridFunction]) -> None:
        self.inner = inner


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        produced = self.inner(input_function, output_discretization, condition)
        summed = numpy.asarray(input_function.values, dtype=numpy.float64) + numpy.asarray(
            produced.values, dtype=numpy.float64
        )
        return GridFunction(summed, input_function.channel_labels, produced.domain, produced.quadrature)


    def Inspect(self) -> dict[str, Array]:
        return {f"inner.{name}": value for name, value in self.inner.Inspect().items()}


class Conditioned(Operator[GridFunction, GridFunction]):
    """Scales and shifts the inner operator's channels from the conditioning vector."""


    def __init__(self, inner: Operator[GridFunction, GridFunction], channels: int, condition_width: int, seed: int = 0) -> None:
        self.inner = inner
        generator = numpy.random.default_rng(seed)
        scale = 1.0 / numpy.sqrt(condition_width)
        self.parameter_values: dict[str, NDArray[numpy.float64]] = {
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
        condition_vector = numpy.asarray(condition.vector, dtype=numpy.float64)
        channel_scales = 1.0 + self.parameter_values["condition_scale_weights"] @ condition_vector
        channel_shifts = self.parameter_values["condition_shift_weights"] @ condition_vector
        values = numpy.asarray(produced.values, dtype=numpy.float64)
        modulated = values * channel_scales[:, None, None, None] + channel_shifts[:, None, None, None]
        return GridFunction(modulated, produced.channel_labels, produced.domain, produced.quadrature)


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = {f"inner.{name}": value for name, value in self.inner.Inspect().items()}
        state.update(self.parameter_values)
        return state


__all__ = [
    "Conserving",
    "Residual",
    "Conditioned",
]
