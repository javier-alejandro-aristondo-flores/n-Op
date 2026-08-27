"""Atomic structure to charge density and magnetization fields, queried at any point."""

from operators.framework import GridFunction, NeuralOperator, PointSet


class DeepDft(NeuralOperator[PointSet, PointSet, GridFunction | PointSet]):
    """Assembles an atom embedding and message-passing layers over atoms and probes."""


    def __init__(self) -> None:
        raise NotImplementedError
