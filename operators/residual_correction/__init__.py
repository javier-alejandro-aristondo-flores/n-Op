"""Cheap-functional charge density to accurate-functional charge density."""

from operators.framework import Operator


class ResidualCorrection(Operator):
    """Wraps a backbone with residual, conditioning, and conservation behavior."""


    def __init__(self) -> None:
        raise NotImplementedError


    def __call__(self, input_function, output_discretization, condition=None):
        raise NotImplementedError
