"""one layer applied repeatedly, weight-tied to a fixed depth or iterated to its own equilibrium"""

from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray

from operators.framework import Array, Coefficients, Composition, GridFunction, Layer
from operators.substrate import Gaussian_Error_Linear_Unit, Solve_Linear_System

type FixedPointBackward = Literal["phantom", "jacobian_free", "implicit"]


def Sliced_Lifted(lifted: dict[str, Any], prefix: str) -> dict[str, Any]:
    """the slice of a shared lifted dict that belongs to one part, its own names restored"""
    return {name[len(prefix):]: value for name, value in lifted.items() if name.startswith(prefix)}


def Applied_Once(
    layer: Layer[GridFunction], kernel_lifted: dict[str, Any], local_linear_lifted: dict[str, Any], state: Any
) -> Any:
    """one activated pass of a layer over the current value, differentiable through whichever engine holds it"""
    spatial_shape = state.shape[1:]
    output_shape = (int(spatial_shape[0]), int(spatial_shape[1]), int(spatial_shape[2]))
    kernel_output = layer.kernel.Forward(kernel_lifted, state, output_shape)
    local_output = layer.local_linear.Forward(local_linear_lifted, state)
    summed = local_output + kernel_output
    if layer.activation == "alias_free":
        raise NotImplementedError("the alias-free activation is the convolutional entry's own build")
    activated = Gaussian_Error_Linear_Unit(summed)
    if layer.residual and activated.shape == state.shape:
        activated = activated + state
    return activated


def Single_Layer_Parameter_Values(layer: Layer[GridFunction]) -> dict[str, NDArray[np.float64]]:
    """one shared layer's kernel and local linear arrays, prefixed once and not per application"""
    collected: dict[str, NDArray[np.float64]] = {}
    for name, value in layer.kernel.parameter_values.items():
        collected[f"kernel.{name}"] = value
    for name, value in layer.local_linear.parameter_values.items():
        collected[f"local_linear.{name}"] = value
    return collected


def Single_Layer_Inspection(layer: Layer[GridFunction]) -> dict[str, Array]:
    """one shared layer's inspected kernel and local linear state, prefixed once and not per application"""
    state: dict[str, Array] = {}
    for name, value in layer.kernel.Inspect().items():
        state[f"kernel.{name}"] = value
    for name, value in layer.local_linear.Inspect().items():
        state[f"local_linear.{name}"] = value
    return state


class WeightTied(Composition[GridFunction]):
    """one layer applied a fixed number of times with the same weights, gradients accumulating across every use"""


    def __init__(self, layer: Layer[GridFunction], depth: int) -> None:
        self.layer = layer
        self.depth = depth
        self.last_application_norms: NDArray[np.float64] | None = None


    def Application_Outputs(self, lifted: dict[str, Any], input_values: Any) -> list[Any]:
        """the value after each application of the shared layer in turn, tape on throughout"""
        kernel_lifted = Sliced_Lifted(lifted, "kernel.")
        local_linear_lifted = Sliced_Lifted(lifted, "local_linear.")
        current = input_values
        outputs: list[Any] = []
        for _ in range(self.depth):
            current = Applied_Once(self.layer, kernel_lifted, local_linear_lifted, current)
            outputs.append(current)
        return outputs


    def Forward(self, lifted: dict[str, Any], input_values: Any) -> Any:
        """the value after the last application, differentiable through whichever engine lifted the shared dict"""
        outputs = self.Application_Outputs(lifted, input_values)
        return outputs[-1] if outputs else input_values


    def Parameter_Values(self) -> dict[str, NDArray[np.float64]]:
        """the one shared layer's kernel and local linear arrays, prefixed once and not per application"""
        return Single_Layer_Parameter_Values(self.layer)


    def Apply(self, input_function: GridFunction, condition: Coefficients | None = None) -> GridFunction:
        values = np.asarray(input_function.values, dtype=np.float64)
        outputs = self.Application_Outputs(self.Parameter_Values(), values)
        self.last_application_norms = np.asarray(
            [float(np.linalg.norm(np.asarray(output, dtype=np.float64))) for output in outputs], dtype=np.float64
        )
        produced = np.asarray(outputs[-1], dtype=np.float64) if outputs else values
        return GridFunction(produced, input_function.channel_labels, input_function.domain, input_function.quadrature)


    def Inspect(self) -> dict[str, Array]:
        state = Single_Layer_Inspection(self.layer)
        if self.last_application_norms is not None:
            state["last_application_norms"] = self.last_application_norms
        return state


@dataclass(frozen=True, slots=True)
class FixedPointSolve:
    """one converged solve's outcome, the equilibrium beside what the solver can say about reaching it"""

    equilibrium: Any
    iterations_taken: int
    final_residual: float
    cap_was_hit: bool
    residual_norm_history: list[float]


def Anderson_Mixing_Weights(
    residual_history: list[NDArray[np.float64]], regularization: float, condition_ceiling: float
) -> NDArray[np.float64] | None:
    """weights summing to one that best cancel the residual history in a least-squares sense, none past the ceiling"""
    flattened = [np.reshape(residual, -1) for residual in residual_history]
    anchor = flattened[-1]
    differences = np.stack([earlier - anchor for earlier in flattened[:-1]], axis=0)
    if float(np.linalg.cond(differences)) > condition_ceiling:
        return None
    gram = differences @ differences.T
    regularized_gram = gram + regularization * np.eye(gram.shape[0])
    right_hand_side = differences @ (-anchor)
    free_weights = Solve_Linear_System(regularized_gram, right_hand_side)
    return np.concatenate([free_weights, np.asarray([1.0 - float(np.sum(free_weights))])])


class FixedPoint(Composition[GridFunction]):
    """one layer applied until its own output stops changing, differentiated through the equilibrium it reaches"""


    def __init__(
        self,
        layer: Layer[GridFunction],
        backward: FixedPointBackward = "phantom",
        phantom_depth: int = 1,
        damping: float = 0.5,
        history_depth: int = 5,
        regularization: float = 1e-4,
        condition_ceiling: float = 1e8,
        tolerance: float = 1e-3,
        iteration_cap: int = 32,
    ) -> None:
        self.layer = layer
        self.backward: FixedPointBackward = backward
        self.phantom_depth = phantom_depth
        self.damping = damping
        self.history_depth = history_depth
        self.regularization = regularization
        self.condition_ceiling = condition_ceiling
        self.tolerance = tolerance
        self.iteration_cap = iteration_cap
        self.last_solve: FixedPointSolve | None = None


    def Solved(
        self, kernel_lifted: dict[str, Any], local_linear_lifted: dict[str, Any], input_values: Any
    ) -> FixedPointSolve:
        """damped picard toward the shared layer's fixed point, anderson-accelerated once two residuals exist"""
        state = input_values
        residual_history: list[NDArray[np.float64]] = []
        applied_history: list[NDArray[np.float64]] = []
        residual_norm_history: list[float] = []
        for iteration_index in range(self.iteration_cap):
            applied = Applied_Once(self.layer, kernel_lifted, local_linear_lifted, state)
            applied_values = np.asarray(applied, dtype=np.float64)
            state_values = np.asarray(state, dtype=np.float64)
            residual = applied_values - state_values
            residual_norm = float(np.linalg.norm(residual))
            residual_norm_history.append(residual_norm)
            if residual_norm < self.tolerance:
                return FixedPointSolve(applied, iteration_index + 1, residual_norm, False, residual_norm_history)
            residual_history.append(residual)
            applied_history.append(applied_values)
            if len(residual_history) > self.history_depth:
                residual_history.pop(0)
                applied_history.pop(0)
            weights = (
                Anderson_Mixing_Weights(residual_history, self.regularization, self.condition_ceiling)
                if len(residual_history) >= 2
                else None
            )
            if weights is not None:
                state = sum(weight * applied_value for weight, applied_value in zip(weights, applied_history))
            else:
                if len(residual_history) >= 2:
                    # a residual history whose differences are nearly parallel is discarded rather than mixed
                    del residual_history[:-1]
                    del applied_history[:-1]
                state = self.damping * applied + (1.0 - self.damping) * state
        return FixedPointSolve(state, self.iteration_cap, residual_norm_history[-1], True, residual_norm_history)


    def Resolved(self, lifted: dict[str, Any], input_values: Any) -> tuple[Any, FixedPointSolve]:
        """the backward rule's state beside the solve that reached it, computed once for forward and apply alike"""
        if self.backward == "implicit":
            # the adjoint needs a vector-jacobian-product primitive that substrate does not expose yet
            raise NotImplementedError("the implicit backward rule is not available yet, ask the fixed-point stream")
        kernel_lifted = Sliced_Lifted(lifted, "kernel.")
        local_linear_lifted = Sliced_Lifted(lifted, "local_linear.")
        solved = self.Solved(kernel_lifted, local_linear_lifted, input_values)
        depth = 1 if self.backward == "jacobian_free" else self.phantom_depth
        # once the substrate exposes a detach primitive, that call belongs here before the reentry loop
        state = solved.equilibrium
        for _ in range(depth):
            state = Applied_Once(self.layer, kernel_lifted, local_linear_lifted, state)
        return state, solved


    def Forward(self, lifted: dict[str, Any], input_values: Any) -> Any:
        """the state at or just past the fixed point, shaped by whichever backward rule was asked for"""
        return self.Resolved(lifted, input_values)[0]


    def Parameter_Values(self) -> dict[str, NDArray[np.float64]]:
        """the one shared layer's kernel and local linear arrays, prefixed once and not per application"""
        return Single_Layer_Parameter_Values(self.layer)


    def Apply(self, input_function: GridFunction, condition: Coefficients | None = None) -> GridFunction:
        values = np.asarray(input_function.values, dtype=np.float64)
        produced, solved = self.Resolved(self.Parameter_Values(), values)
        self.last_solve = solved
        return GridFunction(
            np.asarray(produced, dtype=np.float64),
            input_function.channel_labels,
            input_function.domain,
            input_function.quadrature,
        )


    def Inspect(self) -> dict[str, Array]:
        state = Single_Layer_Inspection(self.layer)
        if self.last_solve is not None:
            state["last_iterations_taken"] = np.asarray(self.last_solve.iterations_taken)
            state["last_final_residual"] = np.asarray(self.last_solve.final_residual)
            state["last_cap_was_hit"] = np.asarray(self.last_solve.cap_was_hit)
            state["last_residual_norm_history"] = np.asarray(self.last_solve.residual_norm_history, dtype=np.float64)
        return state
