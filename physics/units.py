"""The unit system.

Auditor 3 found that no unit system is declared anywhere in the 45-page specification --
six separate names for one returned zero files each -- while the registry *requires* every
signature to carry units ("typed inputs to output, with units"). The corpus even warns
itself that "the 4 pi in the source term rides the unit system" and names factor-4-pi
errors across the electromagnetic sector as the failure mode, without ever saying which
system is in use.

This module closes that. It **transcribes** the convention already in use and verified in
`data/diamond-strain-sweep/02-how-to-read-and-derive.md` (which handles VASP's kB correctly:
"-86.3 kB at HSE06 (tensile, i.e. 8.6 GPa)"). It does not invent a new one.

**Deliberately not a dimensional type system.** No unit-carrying scalars, no quantity
algebra, no checked signatures. That is a compiler project in a new costume, and the
registry's demand for unit-bearing signatures is exactly the pull toward it. What is wanted
is a declared convention and explicit converters at the boundary where foreign units enter.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Canonical units. Everything inside the oracle is in these and only these.
# ---------------------------------------------------------------------------

CANONICAL = {
    "energy": "eV",
    "length": "angstrom",
    "volume": "angstrom^3",
    "force": "eV/angstrom",
    "stress": "GPa",
    "elastic_constant": "GPa",
    "pressure": "GPa",
    "magnetic_moment": "bohr_magneton",
    "temperature": "K",
    "energy_per_atom": "eV/atom",
}

# ---------------------------------------------------------------------------
# Foreign units, and the one conversion that actually bites.
#
# VASP reports stress in kB (kilobar). 1 kB = 0.1 GPa. Getting this wrong is a
# factor-10 error in every elastic constant, and it is silent -- the numbers stay
# plausible. The verified analysis this transcribes states it as
# "-86.3 kB at HSE06 (tensile, i.e. 8.6 GPa)", which is this factor.
# ---------------------------------------------------------------------------

KBAR_TO_GPA = 0.1
GPA_TO_KBAR = 10.0

# meV/atom is the currency of the hull and metastability rows.
EV_TO_MEV = 1000.0
MEV_TO_EV = 1.0e-3


def stress_kbar_to_gpa(value):
    """VASP stress (kB) -> canonical stress (GPa).

    Applies to scalars and to numpy arrays of any shape, including the 3x3 tensor.
    """
    return value * KBAR_TO_GPA


def stress_gpa_to_kbar(value):
    """Canonical stress (GPa) -> VASP stress (kB). For writing VASP-facing artifacts."""
    return value * GPA_TO_KBAR


# ---------------------------------------------------------------------------
# Sign conventions, which are as load-bearing as the magnitudes.
# ---------------------------------------------------------------------------

#: VASP reports stress with the opposite sign to the continuum-mechanics convention:
#: a *positive* VASP stress means the cell wants to shrink (compressive). Flip when
#: pairing VASP stress against an elastic-constant fit written in the continuum
#: convention. Kept as an explicit named constant rather than a bare minus sign at
#: the call site, because a bare minus sign is invisible in review.
VASP_STRESS_SIGN = -1.0


def describe() -> str:
    """One-line-per-quantity statement of the convention, for the oracle-file schema."""
    lines = ["canonical units:"]
    lines += [f"  {k:20s} {v}" for k, v in CANONICAL.items()]
    lines.append(f"  {'stress (VASP in)':20s} kB, converted by x{KBAR_TO_GPA}")
    lines.append(f"  {'stress sign (VASP)':20s} x{VASP_STRESS_SIGN} to continuum convention")
    return "\n".join(lines)
