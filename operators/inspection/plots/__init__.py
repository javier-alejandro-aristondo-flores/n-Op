"""the one place the plotting library may be imported, composed into the figure surface"""

# pyright: reportUnusedImport=false

from operators.inspection.plots.renderers import (
    Centred_On_Zero,
    Render_Bars,
    Render_Curves,
    Render_Field_Sheet,
    Render_Field_Slices,
    Render_Matrix,
    Render_Scalars,
    Render_Spectrum,
)
from operators.inspection.plots.results import (
    Render_Error_Spread,
    Render_Floor_Comparison,
    Render_Prediction_Against_Truth,
)
from operators.inspection.plots.suite import RenderedSuite, Render_Inspection_Suite
