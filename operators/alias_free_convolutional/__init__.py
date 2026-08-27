"""Charge density to electron localization field, by alias-free convolution."""

from operators.framework import GridFunction, NeuralOperator


class AliasFreeConvolutional(NeuralOperator[GridFunction, GridFunction, GridFunction]):
    """Assembles a pointwise lift and multi-scale layers in the alias-free mode."""


    def __init__(self) -> None:
        raise NotImplementedError
