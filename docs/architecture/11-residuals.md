---
id: arch-11-residuals
title: Residuals
status: draft
revision: 1
canonical-for:
  - residual granularity discipline
  - ResidualKey / ContributionFacets schema
  - the seventeen residual categories
depends-on:
  - arch-06-physics-graph
  - arch-07-pipeline
  - arch-09-vocabularies
  - arch-10-typeclasses
referenced-by:
  - arch-16-pino-bridge
  - impl-07-residual-factory
  - impl-09-cross-cutting
  - arch-19-coupling-structure
  - arch-20-representations
research-sources:
  - physics/research/residual-generator-catalog.md
---

# Residuals

Residuals are the physics-informed loss terms `/informed-operator`
trains against. In the `PhysicsGraph` (`arch-06-physics-graph`) they
are realized as nodes with `OutputRole = ResidualLeaf(key)`. The
emission discipline is **granular**: every independent component is
its own scalar with its own content-addressed key, and `/physics`
never preaggregates.

## 11.1 The seventeen categories (a taxonomy facet)

Residuals fall into seventeen categories, identified by symbolic
tags rather than ordinals. The categories are a *facet* on each
contribution, not a granularity floor or a unit of weighting.

**EOM-violation (per state component) — 7 categories.** One per
DOF of the unified state (`arch-04-state`):

  1. `EOM/γ̂` — `‖∂γ̂/∂t − …‖²` on the density-matrix DOF.
  2. `EOM/A` — same form on the EM gauge potential.
  3. `EOM/R` — same form on ion positions.
  4. `EOM/P` — same form on ion momenta.
  5. `EOM/h` — same form on the cell metric.
  6. `EOM/Π_h` — same form on the cell-metric conjugate.
  7. `EOM/Z` — same form on atomic-number labels (only non-trivial
     under chemistry-active dynamics; otherwise structurally null).

  Aggregate form: `‖dx_i/dt − (L δE/δx_i + M δS/δx_i)‖²` for each
  state-component `x_i`. The axis structure of each EOM residual
  (the set of axis tuples emitted per `arch-11-residuals §11.2`) is
  the union of axes contributed by `(a)` the diagonal kinematic /
  symplectic operators and `(b)` the `InvariantTerm`s of every active
  `CouplingChannel` whose `pieces` include component `x_i`
  (`arch-19-coupling-structure`). Each generated invariant adds its
  own axis tuple; there is no per-coupling residual category.

**Structural axes of GENERIC — 3 categories.**

  8. `Degeneracy` — `‖L δS/δx‖² + ‖M δE/δx‖²`.
  9. `Conservation` — energy, particle-number / charge, momentum /
     crystal-momentum, spin.
 10. `Positivity` — `M ⪰ 0`, `f ∈ [0,1]`, `ρ ≥ 0`, `ω² ≥ 0`,
     `σ ⪰ 0`, `|S_i| = 1`.

**Algebraic identities — 5 categories** (the former umbrella, now
split by analytic kind):

 11. `Algebraic/Kramers-Kronig` — causality dispersion identities on
     response functions.
 12. `Algebraic/SumRules` — f-sum `(2/π)∫ω·Im ε dω = ω_p²`; acoustic
     sum `Σ_J Σ_R Φ_{IαJβ}(R) = 0`; oscillator strengths.
 13. `Algebraic/BalanceLaws` — detailed balance; Einstein relation
     between mobility and diffusion.
 14. `Algebraic/Symmetries` — Onsager reciprocity; Maxwell relations;
     space-group equivariance of response tensors.
 15. `Algebraic/MethodEquivalence` — different formulas claiming the
     same observable agree on their shared domain (BTE-σ ≡ Kubo-σ in
     linear response, etc.).

**Constraint violations (by input-domain type) — 2 categories.**
Disjoint by the *type* of input the constraint reads:

 16. `Static/Snapshot` — depends only on the geometric + electronic
     snapshot, no environment field. Valence-bond-sum charge balance;
     Born stability; dynamical stability; space-group equivariance of
     the snapshot.
 17. `Static/Thermodynamic` — depends on snapshot + environment
     (temperature, chemical potentials, partial pressures).
     Hull-distance, formation-energy-from-references, solubility,
     mass-action, carbide-formation.

Categories 16 and 17 stay disjoint because they consume
type-distinct inputs (snapshot vs snapshot+environment), and the
PINO curriculum schedules them differently for that reason.

The `CategoryTag` enum is the closed set of 17 symbols above. It
appears in `ContributionFacets.category` and nowhere else carries
semantic weight.

## 11.2 The atomic unit: residual contribution

A **residual contribution** is the smallest scalar (or scalar-valued
field-norm) the loss aggregator can multiply by an independent weight.
Every contribution is a `ResidualLeaf` node carrying a content-addressed
key:

```
ResidualKey = (producer : Producer, axes : Tuple<AxisLabel>)
Producer    = Formula(NamedFormula) | Method(NamedMethod)

ContributionFacets =                         -- sidecar; not part of identity
  ( category : CategoryTag                   -- one of 17 symbolic tags (§11.1)
  , bundle   : BundleId                      -- B1..B11
  , dressing : bare | dressed(scheme)        -- provenance label
  )
```

Two evaluations with identical inputs produce the identical key. The
PINO holds `Map<ResidualKey, Weight>` independent of `/physics`'s
internals; weights persist across compose-time recompiles. Facets are
exposed via a parallel `Map<ResidualKey, ContributionFacets>` that the
PINO consults for category- or bundle-level aggregation.

`ResidualKey` is a typed `ContentAddress` instance in the substrate's
sense (`arch-20-representations §20.3` row for cluster C5);
`CategoryTag`, `BundleId`, and `AxisLabel` are `Universe[T]` instances
(cluster C1); `ContributionFacets` is the value type of a typed sidecar
fiber and never participates in `ResidualKey` identity (cluster C3).

## 11.3 Examples of what becomes a separately-weightable contribution

Not "the algebraic-identities category" but each of:

- One Kramers–Kronig identity on one component of `ε(ω)` at one
  frequency band.
- The acoustic sum rule per Cartesian pair `(α, β)` and per shell `R`.
- The conservation residual for one charge species in one slab
  subdomain.
- The Born stability eigenvalue penalty per failing eigenmode of `C_ij`.
- The EOM violation per state-component
  `i ∈ {h, R_I, P_I, Π_h, γ̂, A}`, optionally per spatial / momentum bin.

Not "EOM violation"; not "Born stability"; not "conservation."

## 11.4 Output type

The runtime kernel emits a vector, not a scalar:

```
evaluate : (State, Environment) → ( residuals : Map<ResidualKey, Scalar>
                                  , gradient  : Map<ResidualKey, Cotangent>
                                  , …  )
```

Aggregation (per-category sums, GradNorm balancing, residual-adaptive
sampling, per-bundle weight schedules, curriculum gating) lives in
`/informed-operator`, not in `/physics`. `/physics` is an oracle that
reports per-component values; the consumer chooses how to reduce them.

### 11.4.1 Curriculum gating defaults

`/physics` specifies the **default** curriculum schedule that
`/informed-operator` uses to gate which residual categories
(`CategoryTag`, §11.1) participate at each training fraction.
`/informed-operator` may override.

```
fraction ∈ [0, 1] of total training budget
[0.00, 0.10)  Warmup    — Conservation + Positivity only
[0.10, 0.60)  Refine    — add all EOM/* + all Algebraic/* except MethodEquivalence
[0.60, 0.90)  Polish    — add Algebraic/MethodEquivalence + Static/Snapshot + Static/Thermodynamic + Degeneracy
[0.90, 1.00]  Cooldown  — no new categories; weights frozen for final evaluation
```

Rationale: Warmup keeps the network on hard physical constraints
before the EOM surface (which dominates the loss landscape) turns on;
Refine carries the bulk of dynamics learning; Polish tightens the
cross-formula equivalence and thermodynamic-consistency residuals once
the dynamical residuals are quiet; Cooldown freezes the schedule for
deterministic final-cert evaluation.

The schedule is a normative default, not a contract: `/informed-operator`
declares its own `Map<CategoryTag, GateSchedule>` if it overrides any
fraction or category.

## 11.5 Granularity composes with hash-consing

Two contributions sharing 99% of their DAG ancestry — for example, all
Kramers–Kronig identities sharing the dielectric-function computation
— is the common case. Stage 3 (`arch-07-pipeline §7.3`) hash-consing
already gives the upstream sharing for free. The granularity directive
adds only that the *leaves* of the DAG — the per-contribution scalars
— are individually addressable. The single compose-time pipeline
produces a kernel that emits the full `Map<ResidualKey, Scalar>` in
one forward pass with no extra cost over emitting a single aggregated
scalar; reverse-mode produces the per-key gradient by structural
projection of the same pullback.

## 11.6 Closure (vocabulary count)

Residual contributions are **unbounded** (they unfold along the
generator's `axes`), but residual *generators* (`impl-07-residual-factory
§7.1`) remain countable: one per `(formula, applicability cell)` plus
the cert-only and ground-truth-bridge subtypes. The closed-vocabulary
discipline (`arch-09-vocabularies`) holds at the generator level.
