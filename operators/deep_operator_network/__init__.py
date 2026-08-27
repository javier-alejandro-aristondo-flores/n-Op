"""Strain or lattice parameters to charge density field, by branch and trunk."""

from operators.framework import Coefficients, GridFunction, NeuralOperator, PointSet


class DeepOperatorNetwork(NeuralOperator[Coefficients | GridFunction, Coefficients, GridFunction | PointSet]):
    """Assembles a sensor encoder, dense layers, and a basis-expansion readout."""


    def __init__(self) -> None:
        raise NotImplementedError
