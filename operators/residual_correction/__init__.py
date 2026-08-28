"""Cheap-functional charge density to accurate-functional charge density."""

from operators.framework import Array, Coefficients, Discretization, GridFunction, Operator


class ResidualCorrection(Operator[GridFunction, GridFunction]):
    """Wraps a backbone with residual, conditioning, and conservation behavior."""


    def __init__(self) -> None:
        raise NotImplementedError


    def __call__(
        self,
        input_function: GridFunction,
        output_discretization: Discretization,
        condition: Coefficients | None = None,
    ) -> GridFunction:
        raise NotImplementedError


    def Inspect(self) -> dict[str, Array]:
        raise NotImplementedError
