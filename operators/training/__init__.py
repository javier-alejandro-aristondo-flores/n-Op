"""split-aware loading, the fields it holds resident, the batches drawn from them and the training loop"""

# pyright: reportUnusedImport=false

from operators.training.cache import (
    Build_Field_Cache,
    CachedField,
    Cached_Field_Statistics,
    FieldCache,
    Functional_Field_Cache,
    Global_Statistics,
    Parameter_Spreads,
    Shape_Groups,
)
from operators.training.hardware import DeviceChoice, Resolved_Device_Name, Training_Engine
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
from operators.training.loop import (
    ForwardLoss,
    Read_Checkpoint,
    Train,
    TrainingHook,
    TrainingProgress,
    TrainingResult,
    Unit_Mean_Score,
    Unit_Scores,
    Write_Checkpoint,
)
from operators.training.staged import (
    DEFAULT_FINAL_STAGE_PATIENCE,
    DEFAULT_PEAK_LEARNING_RATE,
    DEFAULT_PROBE_STEPS,
    DEFAULT_STAGE_FRACTIONS,
    DEFAULT_VALIDATION_INTERVAL,
    Sane_Loss_Curve,
    Staged_Step_Counts,
    Staged_Training,
)
from operators.training.sampling import (
    Batch_Of_Fields,
    BatchArray,
    BatchSource,
    CoordinateFeaturizedBatches,
    Evenly_Spaced_Flat_Indices,
    FixedBatches,
    PointSampledBatches,
    TrainingBatch,
)
