"""the plotting library's single entry point, with a file-writing backend chosen first"""

from typing import Any

import matplotlib

# a file-writing backend, chosen before pyplot is imported so no display is needed
matplotlib.use("Agg")

from matplotlib import pyplot

# one untyped name for the whole foreign surface
PYPLOT: Any = pyplot
