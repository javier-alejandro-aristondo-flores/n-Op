"""Where this campaign reads from and writes to.

**Two roots, and they must not be the same place.** The distinction is the whole reason
this module exists rather than a constant in each script:

* `RESULTS` and `FIGURES` are inside the repository and are committed. Every number in
  `VERDICT.md` is checkable from them without the dataset, which is the point.
* `CACHE` is 1.6 GB of VASP text extracted from the archives. It must **never** enter the
  repository — every run directory it mirrors carries a licensed pseudopotential, and this
  remote is public. It is regenerable by `extract_sweep.py` in about two minutes.

While this campaign ran, both were one directory on `/Pool` and each script asserted
`OUT.startswith("/Pool/")`. That assertion was right then and is wrong now: the results
belong in the repository and the cache must stay out of it, so the single assertion
becomes two opposing ones.

The environment override follows the convention `tests/test_ingest_pool.py` already sets
for the same dataset: a name, a default outside the repository, and a clear skip when the
data is absent rather than a stack trace fifty lines later.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

#: Repository root. `code/` -> gate -> `feasibility/` -> root.
REPO = Path(__file__).resolve().parents[3]

GATE = Path(__file__).resolve().parents[1]
RESULTS = GATE / "results"
FIGURES = GATE / "figures"

#: The run manifest, committed. Read from the repository rather than from the dataset, so
#: the noise-floor step needs no /Pool at all.
RUN_MANIFEST = REPO / "data" / "diamond-strain-sweep" / "index-of-all-runs.tsv"

# So `physics.formulas.elastic` imports whether or not this is run from the repository
# root. It replaces a hardcoded absolute path to one developer's home directory.
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

#: Extracted VASP text. Deliberately outside the repository; override with NOP_SWEEP_CACHE.
DEFAULT_CACHE = Path("/Pool/strain_gate4/cache")
CACHE = Path(os.environ.get("NOP_SWEEP_CACHE", DEFAULT_CACHE))

assert RESULTS.is_relative_to(REPO), "results are committed and must be inside the repo"
assert not CACHE.is_relative_to(REPO), (
    f"the extracted cache is at {CACHE}, inside the repository. It carries licensed "
    "pseudopotentials and this remote is public. Set NOP_SWEEP_CACHE elsewhere."
)


def require_cache() -> Path:
    """The cache directory, or a clean exit saying how to make one.

    Only `extract_sweep.py` and `build_table.py` need it. Everything downstream reads the
    committed tables in `RESULTS`, so the pipeline detaches from the dataset after the
    table is built — which is what makes the verdict checkable on a machine that has never
    seen `/Pool`.
    """
    if not CACHE.is_dir():
        sys.exit(
            f"no extracted sweep cache at {CACHE}.\n"
            "Build one with code/extract_sweep.py, or point NOP_SWEEP_CACHE at an "
            "existing one. The archives live on /Pool and are never committed."
        )
    return CACHE
