"""any subset of the corpus fields to the fields left out"""

from operators.framework import GridFunction, NeuralOperator


class CodomainAttention(NeuralOperator[GridFunction, GridFunction, GridFunction]):
    """variable channel encodings with attention over channel tokens"""


    def __init__(self) -> None:
        raise NotImplementedError
