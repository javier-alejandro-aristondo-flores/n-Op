"""kernels of separable form, dense index maps and feature inner products"""

from collections.abc import Callable
from typing import Any

import numpy as np
from numpy.typing import NDArray

from operators.framework import (
    Array,
    Coefficients,
    Discretization,
    GridFunction,
    Kernel,
    Output_Points,
    PointSet,
    PointSpec,
    Quadrature_Weights,
    Representation,
    Source_Points_And_Values,
)
from operators.substrate import Engine


class DenseKernel(Kernel[Coefficients, Coefficients]):
    """a learned matrix over finite index sets, integrated by plain contraction"""

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
    """output features against a learned core against input features"""

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
        """the dense pairwise kernel this low-rank form is never forced to integrate through"""
        target_features = self.feature_map(targets)
        source_features = self.feature_map(sources)
        return target_features @ self.parameter_values["core"] @ source_features.T


    def Forward(self, lifted: dict[str, Any], target_features: Any, source_features: Any, weighted_values: Any) -> Any:
        """branch coefficients, the fixed feature matrices contracted against the learned core between them"""
        kernel_values = target_features @ lifted["core"] @ source_features.T
        return kernel_values @ weighted_values


    def Lifted_Constants(
        self, engine: Engine, input_function: Representation, output_discretization: Discretization
    ) -> tuple[Any, Any, Any]:
        """this query's feature matrices and quadrature-weighted source values, as engine constants"""
        sources, values = Source_Points_And_Values(input_function)
        weights = Quadrature_Weights(input_function)
        targets = Output_Points(output_discretization)
        weighted_values = np.asarray(values, dtype=np.float64) * weights[:, None]
        return (
            engine.Lift_Constant(np.asarray(self.feature_map(targets), dtype=np.float64)),
            engine.Lift_Constant(np.asarray(self.feature_map(sources), dtype=np.float64)),
            engine.Lift_Constant(weighted_values),
        )


    def Integrate(
        self,
        input_function: Representation,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> Coefficients:
        sources, values = Source_Points_And_Values(input_function)
        weights = Quadrature_Weights(input_function)
        targets = Output_Points(output_discretization)
        self.last_kernel_values = self.Kernel_Matrix(targets, sources)
        target_features = np.asarray(self.feature_map(targets), dtype=np.float64)
        source_features = np.asarray(self.feature_map(sources), dtype=np.float64)
        # the quadrature is paid here, exactly as the dense reference pays it
        weighted_values = np.asarray(values, dtype=np.float64) * weights[:, None]
        produced = np.asarray(
            self.Forward(self.parameter_values, target_features, source_features, weighted_values),
            dtype=np.float64,
        )
        return Coefficients(vector=produced.reshape(-1), domain=input_function.domain)


    def Inspect(self) -> dict[str, Array]:
        state: dict[str, Array] = dict(self.parameter_values)
        if self.last_kernel_values is not None:
            state["last_kernel_values"] = self.last_kernel_values
        return state


def Point_Spec_Over_Indices(index_count: int) -> PointSpec:
    """the output discretization of a finite index set"""
    return PointSpec(np.arange(index_count, dtype=np.float64).reshape(-1, 1))
