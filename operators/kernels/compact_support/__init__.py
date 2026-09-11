"""small-support kernels as grid convolution or message passing"""

# pyright: reportUnusedImport=false

from operators.kernels.compact_support.continuous import (
    ContinuousDisplacementKernel,
    Radial_Profile_Features,
    Sending_Points,
)
from operators.kernels.compact_support.geometry import (
    Cell_Heights,
    Folded_Fractional_Gaps,
    Grid_Offsets,
    Image_Reach,
    Lattice_Images,
    Offset_Reach,
    Periodic_Radius_Graph,
    RadiusGraph,
    Vector_Lengths,
    Voxel_Indices,
)
from operators.kernels.compact_support.tabulated import Stencil_From_Weights, TabulatedStencilKernel
