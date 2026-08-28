"""atomic structure to charge density and magnetization, queried anywhere"""

from operators.framework import GridFunction, NeuralOperator, PointSet


class DeepDft(NeuralOperator[PointSet, PointSet, GridFunction | PointSet]):
    """atom embedding and message passing over atoms and probes"""


    def __init__(self) -> None:
        raise NotImplementedError
