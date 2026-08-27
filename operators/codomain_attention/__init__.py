"""Any subset of the corpus fields to the fields left out."""

from operators.framework import GridFunction, NeuralOperator


class CodomainAttention(NeuralOperator[GridFunction, GridFunction, GridFunction]):
    """Assembles variable channel encodings and attention over channel tokens."""


    def __init__(self) -> None:
        raise NotImplementedError
