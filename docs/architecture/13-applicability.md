---
id: arch-13-applicability
title: Applicability classifiers
status: draft
revision: 1
canonical-for:
  - applicability discipline
depends-on: []
referenced-by:
  - arch-07-pipeline
  - arch-19-coupling-structure
  - arch-20-representations
research-sources: []
---
# Applicability classifiers

Every property, observable, and residual carries a typed predicate
`applicability : (Crystal, Environment) → Bool`. The PINO loss masks out
non-applicable properties per-sample, so the model is neither falsely supervised
(e.g. predicting a band gap for a metal) nor penalized for an undefined quantity.
This is what makes the architecture **compositional across crystal types**: the
same interface accepts diamond, GaN, AlN, c-BN, refractory metals — each
property's classifier decides whether it is a meaningful question for that
crystal (band gap iff insulator/semiconductor; Schottky barrier iff
metal-semiconductor interface; polar-optical scattering iff polar — false for
diamond; carbide-formation iff the interface includes a carbide former — false
for Pt/diamond, true for Ti/diamond).

V1 commitment: every registry entry gets an explicit `applicability` field;
always-true stubs are acceptable for V1.0 and refined incrementally. Open
questions (deferred): soft `[0,1]` classifiers, and classifier composition under
perturbation.

**Swept-Environment validity windows (committed, V1).** A predicate or formula
*validity window* that depends on a **runtime-swept** `Environment` scalar — temperature
(QHA window, the regime windows of `arch-21-multiscale-state §21.7.1`, the `ω²≥0`
claimed-stable gate, the Chynoweth field domain, the 4-phonon `T ≳ 0.4 Θ_D` window) — is
**re-evaluated per training sample** in the PINO loss mask, *not* once against the
composition's nominal `(Crystal, Environment)`. The per-sample mask path already exists
(`arch-16-pino-bridge`); compose-time `Stage-2.5` structure decisions are frozen, but the
*mask* over them is a runtime read of the swept scalar. To make this checkable, each emitted
kernel is **tagged with the `Environment` box** (the scalar ranges) on which its Stage-2.5
structure is valid; a sample whose swept scalar leaves that box is masked out (and, for a
cert query, trips the relevant obligation) rather than silently scored against a stale kernel.
This is the resolution of the former "current-vs-initial-state evaluation for trajectory
training" question.

`CouplingChannel.applicability` (`arch-19-coupling-structure §19.2`) uses
the same predicate contract: a first-order decidable function on typeclass
tags. A channel whose `applicability` returns `false` is skipped at Stage 2.5
and contributes no invariants to the composition.

The storage shape for an applicability predicate is a
`MerkleDAG[PredicateOps, C1Atom]` root in the substrate's sense
(`arch-20-representations §20.2`, §20.3 row for the applicability
cluster): a reduced ordered Boolean DAG over typed parameterized atoms
drawn from the C1 typeclass-tag vocabularies (`arch-10-typeclasses`).
The atom order is part of the predicate-vocabulary version
(`arch-20 §20.9`); adding a new atom creates a new order id and forces
explicit re-canonicalization of stored predicate roots rather than
silent reinterpretation. Cert obligation checkers (`arch-12-cert`) are
**not** ROBDDs over typeclass-tag atoms — they are typed registered
morphisms from GENERIC artifacts to evidence, registered through the
C2 generator-registry machinery (`arch-20 §20.7`). The split is
preserved.

---
