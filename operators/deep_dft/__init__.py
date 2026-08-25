"""Atomic structure to charge density and magnetization fields, queried at any point."""

from operators.framework import NeuralOperator


class DeepDft(NeuralOperator):
    """Assembles an atom embedding and message-passing layers over atoms and probes."""


    def __init__(self) -> None:
        raise NotImplementedError
