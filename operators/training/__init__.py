"""Split-aware loading and the engine-facet training loop."""

from operators.training.loader import (
    Field_From_Archive,
    Paired_Field_Examples,
    Per_Channel_Statistics,
    Strain_Charge_Pairs,
    TrainingExample,
)
from operators.training.loop import Train, TrainingResult

__all__ = [
    "Field_From_Archive",
    "Paired_Field_Examples",
    "Per_Channel_Statistics",
    "Strain_Charge_Pairs",
    "TrainingExample",
    "Train",
    "TrainingResult",
]
