---
id: residual-definitions
title: "Residuals"
owns:
  - residual granularity discipline
  - the 19 residual categories
  - ResidualKey and ContributionFacets schema
  - equivalence pairs and consistency pairs
  - curriculum category gate
  - per-residual error composition
anchors:
  granularity: "Granularity"
  categories: "The 19 residual categories"
  eom-categories: "Equation-of-motion violation — 9 categories"
  structural-categories: "Structural axes of GENERIC — 3 categories"
  algebraic-categories: "Algebraic identities — 5 categories"
  pair-kinds: "Equivalence pairs and consistency pairs"
  constraint-categories: "Constraint violations — 2 categories"
  categorytag: "The category vocabulary"
  residualkey: "The atomic unit — a residual contribution"
  facets: "Facets are provenance, not weighting axes"
  granularity-examples: "What becomes a separately-weightable contribution"
  output-type: "Output type"
  curriculum-gate: "The curriculum category gate"
  hash-consing: "Granularity composes with hash-consing"
  closure: "Closure of the generator vocabulary"
  error-budget: "Per-residual error composition"
depends-on:
  - accuracy-ledger
  - unified-state
  - generic-dynamics
  - physics-graph
  - compose-time-pipeline
  - canonical-vocabularies
  - typeclass-alphabet
  - cert-obligations
  - gamma-hat
  - coupling-structure
  - representation-substrate
  - multiscale-state
  - residual-machinery
  - crystal-inputs
  - stage-ordering
open-questions:
  - id: curriculum-denominator
    anchor: curriculum-gate
    summary: "The gate is indexed on a training fraction, and what that fraction is a fraction of — the whole training run, or the single stage in which the oracle is attached — is not stated. The two readings place Warmup and Cooldown in different places."
  - id: curriculum-phase-names
    anchor: curriculum-gate
    summary: "Consumers of this gate name three phases where it names four, and a further vocabulary substitutes Calibrate for Cooldown. The phase set is not agreed across the seam."
---
# Residuals

## Granularity

Residuals are the physics-informed loss terms the operator library trains
against. In the physics graph ([physics-graph]) they are realised as nodes with
`OutputRole = ResidualLeaf(key)`.

The emission discipline is **granular**: every independent component is its own
scalar with its own content-addressed key, and the oracle never preaggregates.
Aggregation into a scalar training objective is the operator's business, not
this library's.

## The 19 residual categories

Residuals fall into **19 residual categories**, identified by name and never by
ordinal: 9 equation-of-motion violation + 3 GENERIC-structural + 5
algebraic-identity + 2 constraint-violation. The categories are a *facet* on
each contribution — not a granularity floor, and not a unit of weighting.

### Equation-of-motion violation — 9 categories

Seven per micro state-component degree of freedom ([unified-state#slots]), plus
two cross-tier siblings ([multiscale-state]):

  1. `EOM/γ̂` — `‖∂γ̂/∂t − …‖²` on the density-matrix degree of freedom.
  2. `EOM/A` — same form on the EM gauge potential.
  3. `EOM/R` — same form on ion positions.
  4. `EOM/P` — same form on ion momenta.
  5. `EOM/h` — same form on the cell metric.
  6. `EOM/Π_h` — same form on the cell-metric conjugate.
  7. `EOM/Z` — same form on atomic-number labels; non-trivial only under
     chemistry-active dynamics, otherwise structurally null.

Aggregate form: `‖dx_i/dt − (L δE/δx_i + M δS/δx_i)‖²` for each state component
`x_i` ([generic-dynamics#generic-form]).

**Axis structure.** The set of axis tuples an equation-of-motion residual emits
is the union of the axes contributed by (a) the diagonal kinematic and
symplectic operators and (b) the `InvariantTerm`s of every active
`CouplingChannel` whose `pieces` include component `x_i`
([coupling-structure#invariant-generator]). Each generated invariant adds its
own axis tuple. There is no per-coupling residual category.

The two **cross-tier** siblings share the same
`‖∂_t x − (L δE/δx + M δS/δx)‖²` shape with `x` ranging over a non-micro tier
([multiscale-state]):

  - `EOM/DefectPopulation` — slow-tier defect-population kinetics,
    `‖d[D]^q/dt − (G − [D]^q·k_ann)‖²`.
  - `EOM/Continuum` — macro-tier continuum-field balance,
    `‖∂_t field − RHS(fields; homogenized coeffs)‖²`, generalising the
    device-scale partial-differential-equation residual.

### Structural axes of GENERIC — 3 categories

  8. `Degeneracy` — `‖L δS/δx‖² + ‖M δE/δx‖²`. **Cert-only**: under the
     per-tier generator structure ([generic-dynamics#per-tier-generators]) it is
     identically zero by construction, so it is a generator-construction-bug
     tripwire and never a training-loss term.
  9. `Conservation` — energy, particle-number / charge, momentum /
     crystal-momentum, spin. Particle number includes the **static γ̂-trace
     admissibility** `‖Tr γ̂ − N_e‖²`, with `N_e` fixed by `SiteDecoration`,
     checked per snapshot: a candidate state must carry the right electron
     count, not merely conserve whatever count it has along a trajectory.
     Structural on the state; no formula row of its own.
 10. `Positivity` — `M ⪰ 0`, `f ∈ [0,1]`, `ρ ≥ 0`, `ω² ≥ 0`, `σ ⪰ 0`,
     `|S_i| = 1`.
     - `ω² ≥ 0` is **applicability-gated** to phases claimed dynamically
       stable, so it does not penalise the legitimate saddle and transition
       configurations a trajectory must traverse.
     - The electron-temperature bound `T_e ≥ T_L` reads registry row 72
       (`hot-carrier-temperature-balance`), and the avalanche
       breakdown-integral guard `max(0, ∫α dx − 1)²` reads registry row 75
       (`avalanche-multiplication`). Both read existing rows; neither adds one.
     - **γ̂ admissibility** — ensemble N-representability, the state-level
       analogue of `f ∈ [0,1]`: `γ̂† = γ̂` and `0 ⪯ γ̂ ⪯ 1`, evaluated as
       per-block spectral bounds on the block-diagonal reciprocal-space
       encoding ([gamma-hat]). The extreme eigenvalues of each block are cheap
       to extract, which is what makes the bound affordable per evaluation. The
       zero-temperature idempotency `‖γ̂² − γ̂‖²` is applicability-gated to
       claimed-zero-temperature states exactly as `ω² ≥ 0` is gated to
       claimed-stable phases.

A candidate γ̂ outside these bounds can zero every equation-of-motion residual
while being unphysical. These admissibility gates are what make the oracle sound
as a **verifier of the state itself**, not only of its dynamics.

### Algebraic identities — 5 categories

 11. `Algebraic/Kramers-Kronig` — causality dispersion identities on response
     functions.
 12. `Algebraic/SumRules` — f-sum `(2/π)∫ω·Im ε dω = ω_p²`; acoustic sum
     `Σ_J Σ_R Φ_{IαJβ}(R) = 0`; the **rotational** sum rule
     `(Σ_J [Φ R_γ − Φ R_β])²` (Born–Huang / Gazis–Wallis, registry row 126);
     oscillator strengths.
 13. `Algebraic/BalanceLaws` — detailed balance; the Einstein relation between
     mobility and diffusion; the **Wegscheider reaction-cycle** closure
     `(Σ_r σ_r ln K_r)²` (registry row 125).
 14. `Algebraic/Symmetries` — Onsager reciprocity; Maxwell relations;
     space-group equivariance of response tensors.
 15. `Algebraic/MethodEquivalence` — different formulas claiming the same
     observable agree on their shared domain.

### Equivalence pairs and consistency pairs

`Algebraic/MethodEquivalence` carries two sub-kinds. They are an annotation on
the pair, not two tags:

- An **equivalence pair** binds two formulas that share an *agreement theorem*,
  and trips on any disagreement beyond `τ_equiv`, the numerical-agreement grade
  ([cert-obligations]). Conductivity by Boltzmann transport versus by Kubo is
  one.
- A **consistency pair** binds a cheap model to a microscopic reference with
  **no** agreement theorem — Callaway/Slack thermal conductivity against
  iterative Boltzmann transport, cheap-Chynoweth ionisation against
  Boltzmann/Monte-Carlo — and trips only on *excess beyond a declared model-gap
  tolerance* `τ_method` ([cert-obligations]). A legitimate model gap is
  therefore not scored as a bug.

The thermal-conductivity siblings — registry rows 121
(`kappa-4phonon-high-t-correction`) and 122 (`iterative-lbte-kappa`) — bind to
registry row 25 as a **consistency pair**.

### Constraint violations — 2 categories

Disjoint by the *type* of input the constraint reads:

 16. `Static/Snapshot` — depends only on the geometric and electronic snapshot,
     with no environment field: valence-bond-sum charge balance,
     `elastic-stability-criteria`, dynamical stability, space-group
     equivariance of the snapshot.
 17. `Static/Thermodynamic` — depends on snapshot plus environment
     (temperature, chemical potentials, partial pressures). Hull distance,
     including the **temperature- and pressure-aware metastability** form
     `max(0, ΔG_form(T,P) − ΔG_hull(T,P) − δ_meta)²`, whose band lets diamond
     read `R = 0` at its Berman–Simon boundary point of +25 meV/atom at 300 K
     and 1 atm, standard deviation 5 meV/atom (registry row 124,
     `tp-aware-hull`). Also formation-energy-from-references, solubility,
     mass-action and carbide formation; and the three slow-tier
     thermodynamic-consistency identities — Gibbs adsorption `dγ/dμ = −Γ`,
     charge–Fermi Maxwell `dE_form/dE_F = q`, and the Clausius–Clapeyron
     analogue `d ln[D]/d(1/T)` against `S_form` ([multiscale-state]).

Categories 16 and 17 stay disjoint because they consume type-distinct inputs —
snapshot versus snapshot-plus-environment — and the curriculum schedules them
differently for that reason.

### The category vocabulary

The `CategoryTag` enum is the closed set of these **19 residual categories**:
the 17 above plus the two cross-tier equation-of-motion siblings
`EOM/DefectPopulation` and `EOM/Continuum`. It appears in
`ContributionFacets.category` and carries semantic weight nowhere else.

## The atomic unit — a residual contribution

A **residual contribution** is the smallest scalar — or scalar-valued field norm
— that the loss aggregator can multiply by an independent weight. Every
contribution is a `ResidualLeaf` node carrying a content-addressed key:

```
ResidualKey = (producer : Producer, axes : Tuple<AxisLabel>)
Producer    = Formula(NamedFormula) | Method(NamedMethod)

ContributionFacets =                         -- sidecar; not part of identity
  ( category : CategoryTag                   -- one of the 19 categories
  , bundle   : BundleName                    -- the observable bundle
  , dressing : bare | dressed(scheme)        -- provenance label
  )
```

Two evaluations with identical inputs produce the identical key. The operator
holds `Map<ResidualKey, Weight>` independent of this library's internals, and
those weights persist across compose-time recompiles. Facets are exposed through
a parallel `Map<ResidualKey, ContributionFacets>` that the consumer reads for
category- or bundle-level aggregation.

In the representation substrate ([representation-substrate]), `ResidualKey` is a
typed `ContentAddress` instance; `CategoryTag`, `BundleName` and `AxisLabel` are
typed indexed universes; `ContributionFacets` is the value type of a typed
sidecar fiber and never participates in `ResidualKey` identity.

## Facets are provenance, not weighting axes

`ContributionFacets` attaches `(category, bundle, dressing)` to every
`ResidualLeaf` as a sidecar. It is queryable provenance: never part of
`ResidualKey` identity, and never the basis for a per-residual loss weight.
Weighting lives in the operator's curriculum, keyed by category participation
gates alone. A facet field exists to answer *"which residuals belong to the
transport bundle?"* — not *"what is the weight of residual r?"*

## What becomes a separately-weightable contribution

Not "the algebraic-identities category", but each of:

- One Kramers–Kronig identity on one component of `ε(ω)` at one frequency band.
- The acoustic sum rule per Cartesian pair `(α, β)` and per shell `R`.
- The conservation residual for one charge species in one slab subdomain.
- One failing eigenmode of `C_ij` under `elastic-stability-criteria`.
- The equation-of-motion violation per state component
  `i ∈ {h, R_I, P_I, Π_h, γ̂, A}`, optionally per spatial or momentum bin.

The negatives are what make the discipline operational. Not "equation-of-motion
violation" as one number; not `elastic-stability-criteria` as one number; not
"conservation" as one number.

## Output type

The runtime kernel emits a vector, not a scalar:

```
evaluate : (State, Environment) → ( residuals : Map<ResidualKey, Scalar>
                                  , gradient  : Map<ResidualKey, Cotangent>
                                  , …  )
```

`Environment` is [crystal-inputs]. Aggregation — per-category sums, GradNorm
balancing, residual-adaptive sampling, per-bundle weight schedules, curriculum
gating — lives in the operator library. This library is an oracle that reports
per-component values; the consumer chooses how to reduce them.

## The curriculum category gate

The oracle specifies the **default** schedule gating which residual categories
participate at each training fraction. The operator may override it.

```
fraction ∈ [0, 1] of the training run this gate is indexed on
[0.00, 0.10)  Warmup    — Conservation + Positivity only
[0.10, 0.60)  Refine    — add all EOM/* + all Algebraic/* except MethodEquivalence
[0.60, 0.90)  Polish    — add Algebraic/MethodEquivalence + Static/Snapshot
                          + Static/Thermodynamic
                          (Degeneracy is cert-only and is never a training residual)
[0.90, 1.00]  Cooldown  — no new categories; weights frozen for final evaluation
```

Rationale: Warmup keeps the network on hard physical constraints before the
equation-of-motion surface, which dominates the loss landscape, turns on; Refine
carries the bulk of dynamics learning; Polish tightens the cross-formula
equivalence and thermodynamic-consistency residuals once the dynamical residuals
are quiet; Cooldown freezes the schedule for deterministic final-cert
evaluation.

The gate is keyed on `CategoryTag`, this library's own closed vocabulary, and it
answers one question: *when is this residual meaningful?* It says nothing about
which epoch runs against which data source. The oracle is attached for one
training stage only, and the sequence of stages is [stage-ordering].

**The denominator is unsettled.** Because the oracle is absent from the stages
either side of the one it attaches to, a schedule indexed on the whole training
run and a schedule indexed on that single stage place Warmup and Cooldown in
different places. Both readings are coherent; the corpus does not say which is
meant.

The schedule is a normative default, not a contract: the operator declares its
own `Map<CategoryTag, GateSchedule>` if it overrides any fraction or category.

## Granularity composes with hash-consing

Two contributions sharing 99% of their DAG ancestry — for example, all
Kramers–Kronig identities sharing one dielectric-function computation — is the
common case. The compose-time pipeline's hash-consing stage
([compose-time-pipeline]) already gives that upstream sharing for free. The
granularity directive adds only that the *leaves* of the DAG, the
per-contribution scalars, are individually addressable.

One compose-time pipeline therefore produces a kernel that emits the full
`Map<ResidualKey, Scalar>` in a single forward pass at no extra cost over
emitting one aggregated scalar; reverse mode produces the per-key gradient by
structural projection of the same pullback.

## Closure of the generator vocabulary

Residual contributions are **unbounded** — they unfold along a generator's
`axes`. Residual *generators* ([residual-machinery#generator-record]) remain
**countable**: one per `(formula, applicability cell)`, plus the cert-only and
ground-truth-bridge subtypes. The closed-vocabulary discipline
([canonical-vocabularies]) holds at the generator level, which is what
reconciles it with unbounded emission.

## Per-residual error composition

Every residual generator carries a `characteristic-scale` — the target accuracy
of its observable, a standard deviation seeded from the per-observable accuracy
ledger ([accuracy-ledger]).

It is a **declared scale, not a fitted weight**. It is the error-model input
that `Quantity.combineTol` ([typeclass-alphabet]) composes along the DAG, per
instance by max-abs or by root-sum-square, into a per-`ResidualKey` error
budget. That budget sums:

- the input standard deviation;
- **model-form error** — relaxation-time and three-phonon approximations,
  compact models, the quasi-harmonic approximation;
- **compression truncation** at the lowering stage, against its per-plan error
  target ([compose-time-pipeline]);
- **dressing staleness** for a frozen one-shot dressing
  ([residual-machinery#dressing-certs]);
- **coefficient-provenance** standard deviation
  ([coupling-structure#provenance-contract]).

So *"is this closed-form choice accurate enough?"* is answerable by the system,
not only by external judgment.

The headline design-grade accuracy targets and the full ledger are
[accuracy-ledger]; the reference battery checks them at the MVP anchors
([cert-obligations]). Every numeric tolerance named across this library is
valued once, in the tolerance ledger ([cert-obligations]), which is canonical
for that list.
