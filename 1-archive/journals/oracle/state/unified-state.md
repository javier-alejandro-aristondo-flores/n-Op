---
id: unified-state
title: "The unified state"
owns:
  - state seven-tuple
  - state slot vocabulary
  - state as type not value
anchors:
  slots: "The seven slots"
  emergence: "What the state leaves out"
  type-not-value: "A type, not a value"
  wire-schema: "The wire schema"
depends-on:
  - generic-dynamics
  - born-oppenheimer-levels
  - representation-substrate
  - multiscale-state
open-questions:
  - id: state-wire-schema
    anchor: wire-schema
    summary: "Per-slot dtype, unit, index order and memory layout are unspecified, and the density matrix's array shape is a function of a compile-time compression choice."
---
# The unified state

## The seven slots

The instantaneous state is the seven-tuple

```
x(t) = ( h,      cell vectors                       ∈ GL⁺(3, ℝ)   (3×3 real)
         R_I,    ion positions                      ∈ ℝ^{3N}
         P_I,    ion momenta                        ∈ ℝ^{3N}
         Π_h,    cell momentum (Parrinello–Rahman)  ∈ ℝ^{3×3}
         Z_I,    species labels (immutable)         discrete
         γ̂,      one-body density matrix            2×2 Pauli-spinor operator
                 (Pauli-spinor for magnetism)       on (r, r'; t)
         A )     external EM vector potential       ∈ ℝ³ field A(r,t)
```

The vector potential is carried in the Weyl gauge `A₀ ≡ 0`, transverse `∇·A = 0`;
the electrostatic sector lives in the matter functionals. The normative
gauge-and-partition statement is [generic-dynamics].

The seven slot labels are a closed vocabulary, realized as a typed indexed universe
([representation-substrate]). Downstream code addresses a slot by that universe's
dense ordinal handle, never by raw symbol.

## What the state leaves out

These seven are the **irreducible degrees of freedom of the micro tier**.

Quantities recoverable from them by coarse-graining **on the micro timescale and
micro scale** — phonon distributions, the carrier distribution, surface coverages,
electron and lattice temperatures, micro-scale current density and internal fields —
are **emergent**, and stay out. Admitting a same-timescale coarse-graining would tie
a constraint manifold back onto the irreducible degrees of freedom and reintroduce
the integration pathology this formulation exists to avoid.

Quantities **not** recoverable on the micro timescale or scale are first-class state
in a tier of their own, not emergent: slow, history-dependent defect populations and
composition vectors, evolving over hours to years; and homogenized device-scale
fields on a device mesh. Both couple to the micro tier only parametrically — by
adiabatic driving or by homogenization — so neither introduces a constraint manifold.
[multiscale-state] owns the tiers and the emergence axiom they rest on;
[born-oppenheimer-levels] owns which level each belongs to.

## A type, not a value

`x(t)` is a **type**, which the operator's predictions instantiate at each step.
This library holds no values of `x(t)`. It defines what `x(t)` is, and how to test a
candidate against the laws.

## The wire schema

**Not yet specified.** The seven slots above are given as mathematical types. Their
*representations* are not: per-slot dtype, unit, index order and memory layout are
recorded nowhere, and the density matrix's array shape is not a property of the state
type at all — it is an output of a compile-time compression choice, so it varies with
plane-wave cutoff, band count and irreducible point count.

The operator seam requires emitted candidates to match "per-slot array shapes and
layouts, units, and the gauge conventions recorded there", pointing here. The gauge
conventions are above. The rest of that sentence is this gap, and it is stated rather
than left to be discovered by whoever tries to serialize a state.
