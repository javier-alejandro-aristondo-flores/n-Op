"""one layer applied repeatedly, weight-tied to a fixed depth or iterated to its own equilibrium"""

from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray

from operators.compositions.activation import (
    POINTWISE_ACTIVATIONS,
    Activated,
    Activation_Table,
    ActivationTable,
)
from operators.framework import Array, Coefficients, Composition, GridFunction, Layer
from operators.substrate import (
    CustomGradient,
    Detached,
    Host_Array,
    Sum_Over_Last_Axis,
    Solve_Linear_System,
    Vector_Jacobian_Product,
)

type FixedPointBackward = Literal["phantom", "jacobian_free", "implicit"]


def Sliced_Lifted(lifted: dict[str, Any], prefix: str) -> dict[str, Any]:
    """the slice of a shared lifted dict that belongs to one part, its own names restored"""
    return {name[len(prefix):]: value for name, value in lifted.items() if name.startswith(prefix)}


def Applied_Once(
    layer: Layer[GridFunction],
    kernel_lifted: dict[str, Any],
    local_linear_lifted: dict[str, Any],
    state: Any,
    injection: Any | None = None,
    activations: ActivationTable = POINTWISE_ACTIVATIONS,
) -> Any:
    """one activated pass of a layer over the current value, differentiable through whichever engine holds it"""
    spatial_shape = state.shape[1:]
    output_shape = (int(spatial_shape[0]), int(spatial_shape[1]), int(spatial_shape[2]))
    kernel_output = layer.kernel.Forward(kernel_lifted, state, output_shape)
    local_output = layer.local_linear.Forward(local_linear_lifted, state)
    summed = local_output + kernel_output
    # the input injected before the activation is what makes an iterated map's fixed point depend on the input
    if injection is not None:
        summed = summed + injection
    activated = Activated(activations, layer.activation, summed)
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


    def __init__(
        self,
        layer: Layer[GridFunction],
        depth: int,
        input_injection: bool = False,
        activations: ActivationTable | None = None,
    ) -> None:
        self.layer = layer
        self.depth = depth
        self.activations = Activation_Table(activations)
        # with the injection on, this is exactly the fixed point's own iteration unrolled a fixed number of times
        self.input_injection = input_injection
        self.last_application_norms: NDArray[np.float64] | None = None


    def Application_Outputs(self, lifted: dict[str, Any], input_values: Any) -> list[Any]:
        """the value after each application of the shared layer in turn, tape on throughout"""
        kernel_lifted = Sliced_Lifted(lifted, "kernel.")
        local_linear_lifted = Sliced_Lifted(lifted, "local_linear.")
        injection = input_values if self.input_injection else None
        current = input_values
        outputs: list[Any] = []
        for _ in range(self.depth):
            current = Applied_Once(
                self.layer, kernel_lifted, local_linear_lifted, current, injection, self.activations
            )
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
    # every residual is relative to the iterate's own norm, so a tolerance means the same thing on any grid
    final_residual: float
    cap_was_hit: bool
    residual_norm_history: list[float]


def Host_Inner_Product(first: Any, second: Any) -> float:
    """the inner product of two fields taken on whichever engine holds them, and only the scalar brought to the host"""
    product = (first * second).reshape(-1)
    return float(Host_Array(Sum_Over_Last_Axis(product)))


def Anderson_Gram(residual_history: list[Any]) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """the residual differences' gram matrix and right-hand side, small host arrays built from engine inner products"""
    anchor = residual_history[-1]
    differences = [earlier - anchor for earlier in residual_history[:-1]]
    count = len(differences)
    gram = np.zeros((count, count))
    for row_position in range(count):
        for column_position in range(row_position + 1):
            entry = Host_Inner_Product(differences[row_position], differences[column_position])
            gram[row_position, column_position] = entry
            gram[column_position, row_position] = entry
    right_hand_side = np.asarray([-Host_Inner_Product(difference, anchor) for difference in differences])
    return gram, right_hand_side


def Anderson_Mixing_Weights_From_Gram(
    gram: NDArray[np.float64], right_hand_side: NDArray[np.float64], regularization: float, condition_ceiling: float
) -> NDArray[np.float64] | None:
    """weights summing to one that best cancel the residual history in a least-squares sense, none past the ceiling"""
    # the differences' own condition number is the square root of their gram matrix's
    if float(np.sqrt(np.linalg.cond(gram))) > condition_ceiling:
        return None
    regularized_gram = gram + regularization * np.eye(gram.shape[0])
    free_weights = Solve_Linear_System(regularized_gram, right_hand_side)
    return np.concatenate([free_weights, np.asarray([1.0 - float(np.sum(free_weights))])])


def Anderson_Mixing_Weights(
    residual_history: list[Any], regularization: float, condition_ceiling: float
) -> NDArray[np.float64] | None:
    """the mixing weights straight from a residual history, on whichever engine holds it"""
    gram, right_hand_side = Anderson_Gram(residual_history)
    return Anderson_Mixing_Weights_From_Gram(gram, right_hand_side, regularization, condition_ceiling)


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
        activations: ActivationTable | None = None,
    ) -> None:
        self.layer = layer
        self.activations = Activation_Table(activations)
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
        # every iterate is detached the moment it is made, so the whole solve stays off whichever tape lifted it
        state = Detached(input_values)
        # the input enters every iteration, so the equilibrium is a function of it and not of the starting point alone
        injection = state
        residual_history: list[Any] = []
        applied_history: list[Any] = []
        residual_norm_history: list[float] = []
        for iteration_index in range(self.iteration_cap):
            applied = Detached(
                Applied_Once(self.layer, kernel_lifted, local_linear_lifted, state, injection, self.activations)
            )
            # the residuals stay on their engine, and only the scalars the host decides on come across
            residual_values = applied - state
            residual_norm = float(np.sqrt(Host_Inner_Product(residual_values, residual_values)))
            iterate_norm = float(np.sqrt(Host_Inner_Product(applied, applied)))
            # relative to the iterate, so the tolerance does not tighten with the number of entries
            residual_norm = residual_norm / max(iterate_norm, 1e-12)
            residual_norm_history.append(residual_norm)
            if residual_norm < self.tolerance:
                return FixedPointSolve(applied, iteration_index + 1, residual_norm, False, residual_norm_history)
            residual_history.append(residual_values)
            applied_history.append(applied)
            if len(residual_history) > self.history_depth:
                residual_history.pop(0)
                applied_history.pop(0)
            weights = (
                Anderson_Mixing_Weights(residual_history, self.regularization, self.condition_ceiling)
                if len(residual_history) >= 2
                else None
            )
            if weights is not None:
                # the coefficients are host floats, so mixing never forces the field arrays off their own engine
                state = sum(
                    float(weight) * applied_value for weight, applied_value in zip(weights, applied_history)
                )
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
            return self.Implicit_Resolved(lifted, input_values)
        kernel_lifted = Sliced_Lifted(lifted, "kernel.")
        local_linear_lifted = Sliced_Lifted(lifted, "local_linear.")
        solved = self.Solved(kernel_lifted, local_linear_lifted, input_values)
        depth = 1 if self.backward == "jacobian_free" else self.phantom_depth
        # detached again here, at the equilibrium itself, even though solved already leaves nothing tape-connected
        state = Detached(solved.equilibrium)
        for _ in range(depth):
            state = Applied_Once(
                self.layer, kernel_lifted, local_linear_lifted, state, input_values, self.activations
            )
        return state, solved


    def Implicit_Resolved(self, lifted: dict[str, Any], input_values: Any) -> tuple[Any, FixedPointSolve]:
        """the equilibrium reached by the declared adjoint rather than any reentry, rung three's exact backward"""
        parameter_names = sorted(lifted)
        solve_holder: list[FixedPointSolve] = []

        def Split(arguments: tuple[Any, ...]) -> tuple[dict[str, Any], dict[str, Any]]:
            """the flat positional arguments read back as the two named dicts applied once expects"""
            by_name = dict(zip(parameter_names, arguments))
            return Sliced_Lifted(by_name, "kernel."), Sliced_Lifted(by_name, "local_linear.")

        def Implicit_Forward(arguments: tuple[Any, ...]) -> Any:
            """the equilibrium alone, the solve itself never asked to carry a declared gradient"""
            kernel_lifted, local_linear_lifted = Split(arguments)
            solved = self.Solved(kernel_lifted, local_linear_lifted, arguments[-1])
            solve_holder.append(solved)
            return solved.equilibrium

        def Implicit_Backward(cotangent: Any, output: Any, saved_arguments: tuple[Any, ...]) -> tuple[Any, ...]:
            """the cotangent solved through i minus j transpose, then pulled back onto every saved argument"""
            kernel_lifted, local_linear_lifted = Split(saved_arguments)
            saved_injection = saved_arguments[-1]

            def Applied_At_The_Equilibrium(state: Any) -> Any:
                """applied once at the fixed state, differentiable only through the state itself"""
                return Applied_Once(
                    self.layer, kernel_lifted, local_linear_lifted, state, saved_injection, self.activations
                )

            adjoint = cotangent
            for _ in range(self.iteration_cap):
                updated = Vector_Jacobian_Product(Applied_At_The_Equilibrium, output, adjoint) + cotangent
                adjoint_step = Detached(updated - adjoint)
                change = float(np.sqrt(Host_Inner_Product(adjoint_step, adjoint_step)))
                adjoint_norm = float(np.sqrt(Host_Inner_Product(Detached(updated), Detached(updated))))
                adjoint = updated
                if change / max(adjoint_norm, 1e-12) < self.tolerance:
                    break

            gradients: list[Any] = []
            for varying_position in range(len(parameter_names)):

                def Applied_Varying_One_Parameter(
                    parameter_value: Any, varying_position: int = varying_position
                ) -> Any:
                    """applied once at the fixed equilibrium, with every parameter but this one held fixed too"""
                    varied_arguments = tuple(
                        parameter_value if position == varying_position else saved_arguments[position]
                        for position in range(len(saved_arguments))
                    )
                    varied_kernel_lifted, varied_local_linear_lifted = Split(varied_arguments)
                    return Applied_Once(
                        self.layer,
                        varied_kernel_lifted,
                        varied_local_linear_lifted,
                        output,
                        saved_injection,
                        self.activations,
                    )

                gradients.append(
                    Vector_Jacobian_Product(Applied_Varying_One_Parameter, saved_arguments[varying_position], adjoint)
                )

            def Applied_Varying_The_Injection(injection: Any) -> Any:
                """applied once at the fixed equilibrium with every parameter held, so only the input moves"""
                return Applied_Once(
                    self.layer, kernel_lifted, local_linear_lifted, output, injection, self.activations
                )

            # the input is the last saved argument, and its gradient is what lets the parts upstream train
            gradients.append(Vector_Jacobian_Product(Applied_Varying_The_Injection, saved_injection, adjoint))
            return tuple(gradients)

        rule = CustomGradient(forward=Implicit_Forward, backward=Implicit_Backward)
        equilibrium = rule.Apply(*(lifted[name] for name in parameter_names), input_values)
        return equilibrium, solve_holder[0]


    def Forward(self, lifted: dict[str, Any], input_values: Any) -> Any:
        """the state at or just past the fixed point, shaped by whichever backward rule was asked for"""
        produced, solved = self.Resolved(lifted, input_values)
        # the solve's counts and residuals are host numbers on either engine, and the health floor is read during training
        self.last_solve = solved
        return produced


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
