"""Kernels of separable form: dense index maps and feature inner products."""

from collections.abc import Callable
from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.framework import (
    Coefficients,
    Discretization,
    GridFunction,
    Kernel,
    PointSet,
    PointSpec,
    Representation,
)
from operators.framework.domain import Array
from operators.framework.integral import Output_Points, Quadrature_Weights, Source_Points_And_Values


class DenseKernel(Kernel[Coefficients, Coefficients]):
    """A learned matrix over finite index sets, integrating by plain contraction."""

    supported_representations = (Coefficients,)


    def __init__(self, output_count: int, input_count: int, seed: int = 0) -> None:
        generator = np.random.default_rng(seed)
        scale = 1.0 / np.sqrt(input_count)
        self.parameter_values: dict[str, NDArray[np.float64]] = {
            "weights": generator.normal(0.0, scale, size=(output_count, input_count))
        }
        self.last_output_vector: NDArray[np.float64] | None = None


    def Forward(self, lifted: dict[str, Any], input_vector: Any) -> Any:
        return lifted["weights"] @ input_vector


    def Integrate(
        self,
        input_function: Coefficients,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> Coefficients:
        vector = np.asarray(input_function.vector, dtype=np.float64)
        produced = np.asarray(self.Forward(self.parameter_values, vector), dtype=np.float64)
        self.last_output_vector = produced
        return Coefficients(vector=produced, domain=input_function.domain)


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = dict(self.parameter_values)
        if self.last_output_vector is not None:
            state["last_output_vector"] = self.last_output_vector
        return state


class LowRankKernel(Kernel[Representation, Coefficients]):
    """A feature-product kernel: output features against a learned core against input features."""

    supported_representations = (GridFunction, PointSet, Coefficients)


    def __init__(
        self,
        feature_map: Callable[[NDArray[np.float64]], NDArray[np.float64]],
        feature_count: int,
        seed: int = 0,
    ) -> None:
        self.feature_map = feature_map
        generator = np.random.default_rng(seed)
        self.parameter_values: dict[str, NDArray[np.float64]] = {
            "core": generator.normal(0.0, 1.0 / feature_count, size=(feature_count, feature_count))
        }
        self.last_kernel_values: NDArray[np.float64] | None = None


    def Kernel_Matrix(self, targets: NDArray[np.float64], sources: NDArray[np.float64]) -> NDArray[np.float64]:
        target_features = self.feature_map(targets)
        source_features = self.feature_map(sources)
        return target_features @ self.parameter_values["core"] @ source_features.T


    def Integrate(
        self,
        input_function: Representation,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> Coefficients:
        sources, values = Source_Points_And_Values(input_function)
        weights = Quadrature_Weights(input_function)
        targets = Output_Points(output_discretization)
        kernel_values = self.Kernel_Matrix(targets, sources)
        self.last_kernel_values = kernel_values
        integrated = kernel_values @ (values * weights[:, None])
        return Coefficients(vector=integrated.reshape(-1), domain=input_function.domain)


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = dict(self.parameter_values)
        if self.last_kernel_values is not None:
            state["last_kernel_values"] = self.last_kernel_values
        return state


def Point_Spec_Over_Indices(index_count: int) -> PointSpec:
    """Names the output discretization of a finite index set."""
    return PointSpec(np.arange(index_count, dtype=np.float64).reshape(-1, 1))
