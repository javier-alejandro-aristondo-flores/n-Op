---
id: forced-decisions
title: "Decisions this slice forces"
owns:
  - polyglot implementation shape
  - implementation role requirements
  - tight-binding warm start
  - one-shot-dressing substrate requirement
anchors:
  implementation-language: "The implementation language"
  tb-warm-start: "Tight binding as a warm start"
  substrate-data: "What the substrate level must expose"
depends-on:
  - capability-slices
  - compose-time-pipeline
  - representation-substrate
  - born-oppenheimer-levels
  - accuracy-ledger
  - reference-battery
  - residual-definitions
open-questions:
  - id: implementation-language-picks
    anchor: implementation-language
    summary: "Which language fills each of the four roles — compiler host, runtime host, group-theory engine, proof assistant. The four-role shape is closed; the picks are not. Haskell, Julia, the `GAP` computer-algebra system and Lean 4 are on record as candidates, together with the requirement each was chosen to satisfy; each role must be re-argued against its alternatives, against bring-your-own reverse-mode differentiation, an equality-saturation library, a typed intermediate representation and a code-generation path, before code is written."
---
# Decisions this slice forces

Three decisions the MVP slice forces that are not derivable from the capability
selection itself ([capability-slices]).

## The implementation language

The concrete needs are fixed by what the slice has to compute: reverse-mode automatic
differentiation through implicit-differentiation adjoints, for Boltzmann transport in
the relaxation-time approximation, for the self-consistent field, and for G₀W₀; a
staged symbolic intermediate representation with code generation at the lowering stage
([compose-time-pipeline#lowering-and-adjoint-synthesis]); irreducible-Brillouin-zone
tooling; and optional GPU execution for k-point meshes.

These are met by a **polyglot of domain-specific languages** filling four roles:

| Role | What it must satisfy | Runs |
|---|---|---|
| Compiler host | A type system strong enough to make the operator-indexed graph and its composition rules compile-time facts; equality saturation over the project's own node type; one derived canonical serializer, because identity *is* the hash ([representation-substrate#serialization]); adjoint synthesis as a typed pass over the project's own intermediate representation | compose time |
| Runtime host | Ingests generated source and compiles it natively, so the hot path crosses no foreign-function boundary; owns the optional GPU code generation; dense linear algebra for the apply loop | runtime |
| Group-theory engine | Generates and validates character tables and projectors for the finite groups the symmetry quotient needs; results are baked in | offline |
| Proof assistant | Machine-checked proofs of the injectivity and algebraic-law obligations, beside the implementation | offline |

**The four-role shape is the settled part; which language fills each role is open.**

Two structural facts make the split safe rather than merely convenient. First, the
boundary between *lowering* and *runtime kernel application* is a narrow, natural
language seam: the compiler emits a kernel, the runtime applies it, and no substrate
object ever serializes across — what crosses is the generated kernel once, then flat
arrays in and keyed arrays out. Second, the group-theory engine and the proof
assistant are **offline leaves**: they run at build and specification time, on no hot
path, so they add no interop risk. Only two of the four roles are live at all.

The selection constraints are part of the decision and outlast any particular pick:
core infrastructure is built **in-house**, so a framework that would own
differentiation is a liability rather than an asset; automatic differentiation and
implicit differentiation are already in hand, so built-in differentiation is no
advantage and driving adjoint synthesis from the project's own intermediate
representation is the requirement; polyglot is acceptable **provided the boundaries
are clean**; languages should be well-known within their domain and serve the problem;
and Rust is excluded by preference. Team familiarity is not a factor.

Every named candidate is a candidate to compare against, never a mandate. Compare
against the requirement column above.

## Tight binding as a warm start

A three-nearest-neighbor sp³d⁵ tight-binding model for carbon is used as a
**warm-start initializer** for the self-consistent-field inner loop.

**It is not a separately evaluated formula and not an independent residual.** It seeds
an iteration whose converged result is what gets scored; nothing in the residual map
comes from it. Treating it as a model in its own right would put an unscored
approximation into the evidence ([residual-definitions#categories]).

## What the substrate level must expose

The closed-form discipline needs the quantum-electronic-substrate level to expose more
than the one-body density matrix, because the one-shot dressings that sit on top of it
consume specific outputs:

- **G₀W₀** needs roughly 30 to 50 unoccupied bands together with their wavefunctions.
- **The quasi-harmonic approximation** needs volume-dependent phonons, from which the
  mode Grüneisen parameters follow.

These are the substrate-level outputs the MVP requires. Their exact form — band count,
wavefunction format, and the phonon output shape — is an open question on the page
that owns the levels ([born-oppenheimer-levels#dressing-tiers]).

The declared accuracy each headline output must meet is
[accuracy-ledger#design-grade], and the machine-readable anchor for every one of those
targets is [reference-battery#contents]. Neither is restated here; the decision this
page carries is that the anchors must exist before the certification obligations can
fire, not what their values are.
