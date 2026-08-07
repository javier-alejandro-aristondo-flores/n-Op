"""Where this library reads from and writes to, and how it reaches Gate 4's code.

**Three roots, and they must not be confused.**

* `RESULTS` and `FIGURES` are inside the repository and are committed. Every number this
  library publishes is checkable from them without the dataset.
* `GATE4` is Gate 4's committed output — `spectra.npz`, `observables.csv`,
  `step1_copies.csv`. This library reads it and never writes to it. It is the frozen
  corpus, and freezing means read-only in the strong sense: a script that wrote there
  could silently change the exams.
* The extracted VASP cache is **not reachable from here at all**. Nothing in this library
  needs it: Gate 4 detached from `/Pool` after `build_table.py`, and this library starts
  downstream of that. If a future step needs raw run content it must go through Gate 4's
  `paths.require_cache`, which prints how to make one.

The import-path insertion below is the whole reuse mechanism, and it is deliberate. Gate 4
owns the strain convention, the symmetry orbits, the frozen splits, the observable
definitions and the deformation-potential baseline. Reimplementing any of them here would
create a second definition that could drift from the one the exams were pre-registered
against. Gate 4 set the precedent by reusing `physics.formulas.elastic.green_lagrange_voigt`
rather than rewriting strain; this follows it.

Gate 4's modules do `from paths import RESULTS`. This module is therefore **not** called
`paths` — if it were, it would shadow theirs and they would import the wrong roots.
"""

from __future__ import annotations

import sys
from pathlib import Path

#: Repository root. This file sits one level below it.
REPO = Path(__file__).resolve().parents[1]

LIBRARY = Path(__file__).resolve().parent
RESULTS = LIBRARY / "results"
FIGURES = LIBRARY / "figures"

#: Gate 4's committed evidence. Read-only.
GATE4 = REPO / "feasibility" / "gate-4-strain-sweep"
GATE4_CODE = GATE4 / "code"
GATE4_RESULTS = GATE4 / "results"

# Gate 4's `code/` goes on the path so `import step3_ladder` resolves there, and so its
# own `from paths import RESULTS` finds *its* roots rather than this module's.
for path in (str(REPO), str(GATE4_CODE)):
    if path not in sys.path:
        sys.path.insert(0, path)

assert RESULTS.is_relative_to(REPO), "results are committed and must be inside the repo"
assert GATE4_RESULTS.is_dir(), (
    f"Gate 4's results are not at {GATE4_RESULTS}. This library is built entirely on "
    "them; there is nothing to do without them."
)


def ensure_results() -> Path:
    """The output directory, created on first use."""
    RESULTS.mkdir(parents=True, exist_ok=True)
    return RESULTS


def ensure_figures() -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    return FIGURES
