"""charge density to electron localization, by alias-free convolution"""

from operators.framework import GridFunction, NeuralOperator


class AliasFreeConvolutional(NeuralOperator[GridFunction, GridFunction, GridFunction]):
    """pointwise lift and multi-scale layers in the alias-free mode"""


    def __init__(self) -> None:
        raise NotImplementedError
