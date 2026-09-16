"""atomic structure to charge density, by a plane-wave branch plus a gaussian branch"""

from operators.framework import GridFunction, NeuralOperator, PointSet


class GaussianPlaneWave(NeuralOperator[PointSet, PointSet, GridFunction | PointSet]):
    """a spectral branch over a fixed probe lattice and a gaussian-orbital branch per atom, summed at any query point"""


    def __init__(self) -> None:
        raise NotImplementedError
