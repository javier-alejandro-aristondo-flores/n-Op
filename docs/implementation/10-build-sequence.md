---
id: impl-10-build-sequence
title: Build sequence
status: draft
revision: 1
canonical-for:
  - build sequence
depends-on:
  - arch-19-coupling-structure
referenced-by: []
research-sources: []
---
# Build sequence

Each phase produces a verifiable artifact. The implementation-language decision is
resolved (`arch-18-open-decisions`, Closed decisions;
`physics/research/implementation-language.md`): a **Haskell** compiler-host for
Stages 1–4 + the substrate, emitting a **Julia** Stage-5 runtime, with **GAP** and
**Lean 4** offline.

| Phase | Scope | Artifact |
|---|---|---|
| 0 | Repository scaffold: the directory tree, orientation docs, per-directory READMEs | Empty skeleton matching the architecture |
| 1 | **Tier-1 numeric substrate** (`core`): coefficient/derivative layout, autodiff engine, staged code generation, tensor algebra, mesh integration | `core` implemented + tested against analytic references |
| 2 | **Tier-2 physical primitives** (`shared`): pair-sum with PBC, electrostatics (Ewald), kinetic density, density-from-orbitals, Hellmann–Feynman forces, DFT stress | Physical-primitive library, tested at analytic limits |
| 3 | **Input concepts** (`inputs`): typed constructors + readers for PeriodicityStructure, SiteDecoration, Environment | Round-trip-preserving system descriptions |
| 4 | **Unified state** (`state`): the 7-tuple container; per-level components (L1–L4); enumerate/serialize/hash | State encoding complete |
| 5 | **Methods vocabulary** (`methods`): the 12 methods + sub-method dispatch | Computational vocabulary, tested per method |
| 6 | **Templates** (`abstract-properties`): the 20 templates as typed factories | Template machinery, tested with multiple argument tuples |
| 7 | **Formula registry** (`formulas`): the 110 formulas with typed signatures + citations; the manifest; **applicability-decidability gate** (every classifier first-order decidable on typeclass tags; non-decidable entries rejected — `impl-04-formulas`) | Closed registry; algebraic combinations no longer hand-waved |
| 8 | **GENERIC operators** (`generic`): L sub-brackets, M sub-brackets, assembly; **instantiate active `CouplingSpec` via Stage-2.5 invariant synthesis** (`arch-19-coupling-structure`) and attach generated `InvariantTerm`s to the `E_coupling`, `L_assembly`, `M_assembly` aggregators | Antisymmetry of L, PSD of M, Jacobi, degeneracy verified |
| 9 | **Canonicals** (`canonicals`): E[x] and S[x] assembled across levels | Dimensional + analytic-limit checks pass |
| 10 | **Observables** (`observables`): the target observables as compositions (§6), in 11 bundles | Library callable for any observable; reference-crystal checks |
| 11 | **Residuals + Cert** (`residuals`, `cert`): 17 named categories, ResidualGenerator factory, 10 obligations, schema/freeze/oracle | Self-certifying outputs; usable residual contract |
| 12 | **Dynamics + integration validation** (`dynamics`): assemble the unified RHS; validate on harmonic oscillator, two-level Rabi, ideal-gas relaxation | Unified dynamics callable; RHS handed to any integrator |
| 13 | **API seal + pino-bridge**: the single typed seal; `Validate` and `Import` (`arch-16-pino-bridge`); worked examples; end-to-end demo | Shippable; downstream libraries can build against it |

Recommended start order: substrate (Phases 1–7) before any concrete observable,
then GENERIC/canonicals/observables (Phases 8–10), then residuals/cert/dynamics
(Phases 11–12), then the seal (Phase 13).

---
