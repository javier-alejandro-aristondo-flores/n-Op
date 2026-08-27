"""Charge density and local potential to electron localization field."""

from operators.framework import Coefficients, GridFunction, NeuralOperator, PointSet


class MultipleInputOperatorNetwork(NeuralOperator[GridFunction, Coefficients, GridFunction | PointSet]):
    """Assembles two sensor encoders, a low-rank product, and a shared trunk."""


    def __init__(self) -> None:
        raise NotImplementedError
