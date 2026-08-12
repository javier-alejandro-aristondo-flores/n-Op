"""Put the repository root on `sys.path` so `programs.oracle...` resolves.

Without this, `import programs.oracle.registry.elastic` succeeds only when the
interpreter happens to have the repository root on the path -- which is true for
`python -m pytest` from the root and false for a bare `pytest`. The contract was
never written down, so the invocation form silently decided whether the suite ran.

The root goes on the path, never `programs/` itself. `programs/operator/` would
otherwise place a directory named `operator` on the path, and `operator` is a
path-resolved standard-library module rather than a frozen one, so it would be
shadowed -- including for `pandas`, which imports it from `frame.py` and
`series.py`. Importing through the `programs` package keeps every name unambiguous.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
