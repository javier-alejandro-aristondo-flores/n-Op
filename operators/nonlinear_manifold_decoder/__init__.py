"""Strain or lattice parameters to charge density field, decoded point by point."""

from operators.framework import NeuralOperator


class NonlinearManifoldDecoder(NeuralOperator):
    """Assembles a sensor encoder, dense layers, and a nonlinear decoder."""


    def __init__(self) -> None:
        raise NotImplementedError
