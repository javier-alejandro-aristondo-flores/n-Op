---
id: impl-04-formulas
title: The named-formula registry
status: draft
revision: 1
canonical-for:
  - formula registry signatures
depends-on: []
referenced-by:
  - impl-07-residual-factory
research-sources: []
---
# The named-formula registry

The canonical, machine-readable list is
`physics/library/formulas/registry-manifest.csv` — 132 substantive rows plus 2
markers for relations enforced architecturally and therefore not residualized
(force = −∇energy; equivariance). `formula-registry.md` is the narrative index.
Every algebraic combination invokes a named formula with typed inputs and an
explicit output type; no inline math.

Each formula record carries:

```
record FormulaRecord {
  name               : Symbol                  -- behavior-named (e.g. defect-formation-energy)
  signature          : (Inputs) → Output       -- typed, with units
  bundle             : {BundleId}              -- one or more of B1..B11, or the
                                               --   L1 primitive tag (linear-response
                                               --   primitives Z*/ε∞/χ∞/α_M, rows 91–94,
                                               --   feed multiple bundles)
  cost-tier          : T0 | T1 | T2 | T3
  diff-tag           : D0 | D1 | D2 | D3 | D4
  source             : provenance pointer (research file / literature DOI)
  depends-on         : {Symbol}                -- upstream formulas / primitives
  applicability      : (Crystal, Environment) → Bool
  adjoint-validated  : Passed | Failed(witness) | NotApplicable | Relaxed(rationale)
}
```

**Cost tiers:** T0 closed-form (≤10 µs) · T1 small linear algebra / 1D quadrature
(≤10 ms) · T2 Brillouin-zone / mesh integral (≤10 s) · T3 self-consistent loop or
PDE solve (≤10 min).

**Differentiability tags:** D0 no autodiff needed — a pure read, **or an integer /
categorical output with no useful derivative** (topology invariants, discrete CSP
metrics: "exception-set everywhere") · D1 analytic forward derivative · D2 adjoint
required (validated at registration) · D3 implicit-function adjoint via fixed-point
linearization, **or a finite-difference surrogate where there is no fixed point**
(stated in the formula's docs) · D4 autodiff relaxed via a differentiable surrogate
— surrogate-net bridge, **log-sum-exp soft-hull, or Gumbel-Softmax relaxation** —
approved at registration with an obligation-9 validity domain.

The corrected physics is canonical in the registry and in §6 below: optical
absorption uses `(2ω/c)·Im(√ε)`; the operator-spectrum-area sum rule carries the
`2/π` prefactor; the acoustic sum rule sums over all lattice translations
(`Σ_J Σ_R Φ_{IαJβ}(R) = 0`); the magnetic relaxation term is the
orientation-preserving form `S × (S × H_eff)`; the harmonic transition-rate
normalization consumes products-over-modes (scalars), not spectra.

**Applicability-decidability invariant.** Every `applicability` predicate is
first-order decidable in `(Crystal, Environment)` — finite case analysis on
typeclass tags (lattice type, site decoration, environment-field presence),
not on numeric thresholds or solver outputs. Non-decidable classifiers are
forbidden at registration; see the registry-build gate
(`impl-10-build-sequence` Phase 7).

---
