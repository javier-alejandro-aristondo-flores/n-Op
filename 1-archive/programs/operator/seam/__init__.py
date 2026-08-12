"""The seam section — what crosses the oracle-operator boundary.

Twins `journals/operator/seam/`. The one page there,
`learnable-structure-contract`, is the only corpus page in this repository that
governs a single file explicitly: `differentiation.py` quotes its `#seam-purity`
anchor verbatim, and the rule that plain arrays cross this boundary and nothing
else is what makes the quarantine checkable.

Re-exported here so the section directory is the import surface. Callers say
`from seam import fit`, not `from seam.differentiation import fit`, which keeps
the section rather than the file as the thing they depend on.
"""

from .differentiation import (  # noqa: F401
    DEVICE,
    OUT_DTYPE,
    TORCH_DTYPE,
    TrainingReport,
    fit,
    indirect_gap,
    parameter_count,
    predict_in_batches,
    seed_everything,
    weighted_absolute_error,
)
