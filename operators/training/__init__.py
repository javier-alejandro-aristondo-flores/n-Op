"""split-aware loading and the engine-facet training loop"""

# pyright: reportUnusedImport=false

from operators.training.loader import (
    AUXILIARY_PROBE_ROLE,
    Aligned_Energy_Grid,
    Field_From_Archive,
    FieldPrecision,
    Lattice_Factors_Of,
    Paired_Field_Examples,
    Parameter_Field_Examples,
    ParameterExample,
    Per_Channel_Statistics,
    STATE_DENSITY_POINT_COUNT,
    STATE_DENSITY_WINDOW_BY_CAMPAIGN,
    State_Density_Examples,
    StateDensityExample,
    Strain_Assignments_By_Run,
    Strain_Assignments_Of_Pool,
    Strain_Charge_Pairs,
    TrainingExample,
)
from operators.training.loop import Train, TrainingResult
