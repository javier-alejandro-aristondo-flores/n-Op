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
questions (deferred): soft `[0,1]` classifiers, classifier composition under
perturbation, and current-vs-initial-state evaluation for trajectory training.

`CouplingChannel.applicability` (`arch-19-coupling-structure §19.2`) uses
the same predicate contract: a first-order decidable function on typeclass
tags. A channel whose `applicability` returns `false` is skipped at Stage 2.5
and contributes no invariants to the composition.

---
