"""The in-house Adam optimizer over named parameter and gradient dictionaries."""

from dataclasses import dataclass

import numpy
from numpy.typing import NDArray

from operators.substrate.engine import ParameterSet


@dataclass(slots=True)
class AdamState:
    """Running first and second gradient moments with the step count."""

    first_moments: dict[str, NDArray[numpy.float64]]
    second_moments: dict[str, NDArray[numpy.float64]]
    step_count: int


def Fresh_Adam_State(parameters: ParameterSet) -> AdamState:
    """Returns zeroed moments matching the parameter shapes."""
    return AdamState(
        first_moments={name: numpy.zeros_like(value) for name, value in parameters.values.items()},
        second_moments={name: numpy.zeros_like(value) for name, value in parameters.values.items()},
        step_count=0,
    )


def Adam_Step(
    parameters: ParameterSet,
    gradients: dict[str, NDArray[numpy.float64]],
    state: AdamState,
    learning_rate: float = 1e-3,
    first_decay: float = 0.9,
    second_decay: float = 0.999,
    stabilizer: float = 1e-8,
) -> ParameterSet:
    """Applies one Adam update, mutating the state and returning the new parameters."""
    state.step_count += 1
    updated: dict[str, NDArray[numpy.float64]] = {}
    for name, value in parameters.values.items():
        gradient = gradients[name]
        state.first_moments[name] = first_decay * state.first_moments[name] + (1.0 - first_decay) * gradient
        state.second_moments[name] = second_decay * state.second_moments[name] + (1.0 - second_decay) * gradient**2
        corrected_first = state.first_moments[name] / (1.0 - first_decay**state.step_count)
        corrected_second = state.second_moments[name] / (1.0 - second_decay**state.step_count)
        updated[name] = value - learning_rate * corrected_first / (numpy.sqrt(corrected_second) + stabilizer)
    return ParameterSet(values=updated)
