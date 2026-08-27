"""Strain or lattice parameters to charge density field, decoded point by point."""

from operators.framework import Coefficients, GridFunction, NeuralOperator, PointSet


class NonlinearManifoldDecoder(NeuralOperator[Coefficients, Coefficients, GridFunction | PointSet]):
    """Assembles a sensor encoder, dense layers, and a nonlinear decoder."""


    def __init__(self) -> None:
        raise NotImplementedError
