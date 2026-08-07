"""The state, and its wire schema -- for the slots this slice uses.

`unified-state.md` gives the seven slots as mathematical types and then says outright:

    **Not yet specified.** The seven slots above are given as mathematical types. Their
    *representations* are not: per-slot dtype, unit, index order and memory layout are
    recorded nowhere

This module fixes the representation for the three slots a static snapshot needs. The
other four are deliberately absent rather than stubbed -- see the note at the bottom.

A `Frame` is *not* a state. The state is what a caller supplies; a frame is a state plus
the computed quantities a calculation reported alongside it (forces, stress, occupations).
The oracle cannot compute those -- that would be solving -- so they arrive as imported
data. Keeping the two types distinct is what stops `Validate` from quietly acquiring a
solver.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

# ---------------------------------------------------------------------------
# The wire schema, stated once, for the slots in scope.
# ---------------------------------------------------------------------------

WIRE_SCHEMA = {
    "cell": {
        "dtype": "float64",
        "shape": "(3, 3)",
        "unit": "angstrom",
        "index_order": "row i is lattice vector i; column j is Cartesian component j",
        "layout": "C-contiguous",
    },
    "positions": {
        "dtype": "float64",
        "shape": "(n_ions, 3)",
        "unit": "angstrom",
        "index_order": "row I is ion I; column j is Cartesian component j",
        "layout": "C-contiguous, Cartesian (not fractional)",
    },
    "species": {
        "dtype": "int32",
        "shape": "(n_ions,)",
        "unit": "atomic number Z",
        "index_order": "entry I is ion I, matching `positions` row order",
        "layout": "C-contiguous",
    },
}

#: Slots of the seven-tuple this slice does not carry, and why. Named rather than
#: silently omitted, because a reader must be able to tell "out of scope" from "forgotten".
SLOTS_NOT_CARRIED = {
    "ion_momenta": "static snapshot; no dynamics in this slice",
    "cell_momentum": "static snapshot; no dynamics in this slice",
    "density_matrix": "array shape is an output of a compile-time compression choice "
                      "that this slice does not make",
    "vector_potential": "the slot has no conjugate momentum, so its equation of motion "
                        "has no computable right-hand side (auditor 3, pass B); the state "
                        "type is to be reopened once for this and two other holes",
}


@dataclass(frozen=True)
class CrystalState:
    """The caller-supplied state. Cell, positions, species -- nothing derived.

    Structural well-formedness (shapes, finite values) is the caller's obligation and is
    checked here. *Physical* admissibility is scored, never presupposed, and is not
    checked here.
    """

    cell: np.ndarray       # (3, 3) float64, angstrom
    positions: np.ndarray  # (n, 3) float64, angstrom, Cartesian
    species: np.ndarray    # (n,) int32, atomic number

    def __post_init__(self) -> None:
        cell = np.asarray(self.cell, dtype=np.float64)
        pos = np.asarray(self.positions, dtype=np.float64)
        spec = np.asarray(self.species, dtype=np.int32)
        if cell.shape != (3, 3):
            raise ValueError(f"cell must be (3, 3), got {cell.shape}")
        if pos.ndim != 2 or pos.shape[1] != 3:
            raise ValueError(f"positions must be (n, 3), got {pos.shape}")
        if spec.shape != (pos.shape[0],):
            raise ValueError(
                f"species {spec.shape} does not match positions {pos.shape[0]} ions"
            )
        for name, arr in (("cell", cell), ("positions", pos)):
            if not np.all(np.isfinite(arr)):
                raise ValueError(f"{name} carries non-finite values")
        object.__setattr__(self, "cell", cell)
        object.__setattr__(self, "positions", pos)
        object.__setattr__(self, "species", spec)

    @property
    def n_ions(self) -> int:
        return int(self.positions.shape[0])

    @property
    def volume(self) -> float:
        """Cell volume from the lattice matrix, in angstrom^3.

        Note this is *computed*, and the `det(A) = V` invariant check compares it against
        the volume a calculation *reported*. The two must agree; that they are computed by
        different routes is the whole point of the check.
        """
        return float(abs(np.linalg.det(self.cell)))


@dataclass(frozen=True)
class Environment:
    """The per-call operating-condition record, varying within the file's stamped box."""

    temperature_k: float = 300.0
    pressure_gpa: float = 0.0


@dataclass
class Frame:
    """A state plus what a calculation reported about it.

    The derived channels are `None` when the producing run did not report them -- and
    `None` is load-bearing: it is what drives `RefusalMode.INPUT_CHANNEL_ABSENT` rather
    than a check silently scoring zero.
    """

    state: CrystalState
    #: forces on ions, (n, 3) eV/angstrom
    forces: np.ndarray | None = None
    #: stress tensor, (3, 3) GPa, continuum sign convention
    stress: np.ndarray | None = None
    #: band occupations per spin channel: list of (n_kpoints, n_bands)
    occupations: list[np.ndarray] | None = None
    #: k-point weights, (n_kpoints,), summing to 1
    kpoint_weights: np.ndarray | None = None
    #: electron count the run was set up with
    n_electrons: float | None = None
    #: net magnetic moment in bohr magnetons; None when the run was not spin-polarized
    magnetic_moment: float | None = None
    #: volume as *reported* by the producing calculation (not recomputed from the cell)
    reported_volume: float | None = None
    #: total energy of the cell, eV. Extensive -- it scales with cell size, so it is only
    #: ever compared between frames of the same cell content. Carried because the
    #: equilibrium volume has two independent routes, the minimum of E(V) and the zero of
    #: the mean stress, and their disagreement is a measurable basis-set diagnostic.
    total_energy: float | None = None
    #: free-form provenance, carried but never interpreted
    provenance: dict = field(default_factory=dict)
