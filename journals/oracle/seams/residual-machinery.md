---
id: residual-machinery
title: "Residual machinery"
owns:
  - ResidualGenerator record
  - residual factory
  - the layered compute DAG
  - generator subtypes
  - fidelity generators
  - registration-time adjoint gate
  - dressing certificates
anchors:
  factory: "The factory"
  generator-record: "The ResidualGenerator record"
  layer-dag: "The layered compute DAG"
  factory-entry: "Factory entry point"
  subtypes: "Generator subtypes"
  fidelity-generators: "Fidelity generators"
  registration-gate: "The registration-time adjoint gate"
  dressing-certs: "Dressing certificates"
depends-on:
  - accuracy-ledger
  - physics-graph
  - compose-time-pipeline
  - born-oppenheimer-levels
  - coupling-structure
  - residual-definitions
  - cert-obligations
  - pino-bridge
  - representation-substrate
  - named-formulas
  - crystal-inputs
  - traps
open-questions:
  - id: adjoint-drift-monitoring
    anchor: registration-gate
    summary: "The gate validates the formula's adjoint once, at registration. The composition's adjoint is synthesised later, per composition, over a graph the simplification stage has already rewritten, and nothing revalidates the second."
  - id: dormant-row-cert-encoding
    anchor: registration-gate
    summary: "A dormant row's gate is deferred rather than passed and must be recorded as such, but adjoint-cert has four cases and none of them is deferred."
---
# Residual machinery

## The factory

The consumer-facing factory that turns named formulas
([named-formulas#the-registry]) into `ResidualLeaf` nodes
([physics-graph#node-kinds]) in the physics graph. Under the always-cheap
discipline ([compose-time-pipeline#always-cheap]) it is part of the
symbolic-lift stage ([compose-time-pipeline#symbolic-lift]).

It has three responsibilities: generate the leaves with content-addressed keys,
gate registration on adjoint correctness, and provide the per-formula metadata
the runtime kernel uses for its outputs.

## The ResidualGenerator record

```
record ResidualGenerator {
  name                 : Symbol
  observable           : ObservableRef
  bundle               : {BundleName}             -- one or more observable bundles;
                                                  --   named-formulas is canonical.
                                                  --   A SET, not a scalar: 40 of the 134
                                                  --   registry rows carry two bundles.
  category             : CategoryTag              -- the 19 residual categories
  layer                : 0..6                     -- stratum in the layered compute DAG
  cost-tier            : microseconds | milliseconds | seconds | minutes
                                                  -- named-formulas is canonical
  differentiability    : read | direct | adjoint | fixpoint-adjoint | relaxed | none
                                                  -- named-formulas is canonical
  dressing-tag         : bare | dressed(scheme: G0W0 | SCP-perturbative
                                                | LO-TO-NA-correction | Born-charge
                                                | epsilon-infinity
                                                | electronic-susceptibility)
                         -- the one-shot-dressing cert schemes below;
                         -- a provenance label only, never a loss-weighting axis
  characteristic-scale : Quantity                 -- the observable's declared accuracy
                                                  --   scale, a standard deviation in its
                                                  --   own units, seeded from the ledger;
                                                  --   an error-model input, never a
                                                  --   fitted weight
  axes                 : List<AxisLabel>          -- the dimensions this generator unfolds
                                                  --   over (k-point, frequency, atomic
                                                  --   pair, shell, …)
  applicability        : (Crystal, Environment) → Bool
  input-contract       : {TypedSlot}
  output-contract      : TypedSlot
  forward              : Inputs → Output
  loss-projection      : Output → Map<ResidualKey, Scalar>
                         -- one entry per axis tuple; the key is content-addressed
  weight-policy        : ConsumedBy(operator)
                         -- the oracle declares the granularity; aggregation is downstream
  sampling-policy      : UniformBatch | RAD(τ) | Importance | ValidationOnly
  dependencies         : {Symbol}                 -- same-pass fixed-point co-convergence
  adjoint-cert         : Passed | Failed(witness) | NotApplicable | Relaxed(rationale)
  registration-hash    : ContentAddress           -- cert-tripwire detection
}
```

`Crystal` and `Environment` are [crystal-inputs#crystal-type]. The key each
generator emits, and the facets carried alongside it, are
[residual-definitions#residualkey]; the accuracy scale it declares is
[residual-definitions#error-budget], seeded from [accuracy-ledger#composition].

## The layered compute DAG

`layer` is the generator's stratum in the compute DAG over the whole registry.
Layer 0 is the primitives, which have no dependencies; each higher layer depends
only on layers below it. The index is therefore a topological stratification,
and the runtime evaluates stratum by stratum.

One cycle crosses the strata: the operating-condition observables and the
coupled-field balance are mutually dependent through the self-heating operating
temperature. It is closed by a **same-pass fixed-point iteration at the layer
barrier**, not by nested optimisation — both sides are evaluated in the same
forward pass, and the truncation that the iteration cap introduces is estimated
rather than assumed away (see the fidelity generators below).

## Factory entry point

```
make-residual-generator(observable      : ObservableRef,
                        formula         : NamedFormula,
                        axes            : List<AxisLabel>,
                        sampling-policy : SamplingPolicy,
                        applicability   : (Crystal, Environment) → Bool)
                      → ResidualGenerator
```

Called once per formula at load time. The returned generator is inserted into
the symbolic-lift stage ([compose-time-pipeline#symbolic-lift]) when its
`applicability` predicate holds for the current composition. Coupling channels
register through this same pattern ([coupling-structure#registration]).

## Generator subtypes

- **Standard residual** — derived from a named formula; participates in the
  loss; `adjoint` entries are gated on adjoint existence.
- **Ground-truth-bridge** — anchors a generator to an `Import`-supplied target
  value with `(value, standard-deviation, provenance, axis-coverage)`
  ([pino-bridge#import]); the loss is the scale-normalised Huber against the
  target.
- **Cert-only** — no loss contribution; runs as part of cert evidence
  ([cert-obligations#the-ten-obligations]), not as part of training loss.

## Fidelity generators

Identity is exact in the representation substrate
([representation-substrate#identity-exact]), and any operation that can make the
computed object differ from its exact counterpart must estimate that difference.
This is where the estimate lives.

**Normative.** A generator whose lowering introduces representation error must
register a paired **fidelity generator** — a cert-only subtype carrying a
computable *a-posteriori* estimator of that error. Three lowerings trigger it
today:

| Lowering | Estimator | Cost |
|---|---|---|
| A `CompressionPlan` other than `Dense` ([compose-time-pipeline#lowering-and-adjoint-synthesis]) | the discarded spectrum, `‖A − A_k‖₂ = σ_{k+1}`, with the Frobenius tail for the root-sum-square form | already computed by the truncation |
| A truncated inner solve — a self-consistent field at its tolerance, the equilibrium-statistics ↔ non-equilibrium-kinetics cycle at its ≤5-iteration cap | the a-posteriori inexact-adjoint estimate `τ_trunc` ([cert-obligations#tolerance-ledger]): the implicit-function adjoint assumes the forward solve *converged*, and the error from stopping early is bounded by `‖J⁻¹‖·‖r_stop‖`, computable a-posteriori per Ehrhardt & Roberts, *IMA J. Appl. Math.* 89(1) 254–278 (2024) | the stopping residual is already computed |
| A rewrite admitted under a side condition at the simplification stage ([compose-time-pipeline#rewrite-admission]) | the rewrite's declared float discrepancy on the sampled points | shares the adjoint gate's sample set |

**An a-priori target is not a substitute for an a-posteriori estimate.** A
compression plan already carries an error *target* and picks its rank to meet
it. The target is what the plan intended; the estimate is what it achieved; only
the second is evidence. A declared intention that nothing measures is not a
measurement ([traps#target-is-not-measurement]).

The fidelity generator's output flows into `Quantity.combineTol`
([residual-definitions#error-budget]) alongside the other budget terms, and into
the cert as evidence. It **never** enters the training loss: a network must not
be able to reduce its loss by making the oracle's self-assessment optimistic.

## The registration-time adjoint gate

**Hard.** `adjoint` **and** `fixpoint-adjoint` entries run a
vector-Jacobian-versus-Jacobian-vector check on `N ≈ 64` sampled points at
registration time. If the maximum relative error exceeds `τ_adj`, default
`1e-4`, the build fails loud.

`fixpoint-adjoint` entries run a **second** check at the same points: the
reciprocal condition number of the fixed-point Jacobian must exceed `τ_cond`. An
ill-conditioned implicit-function adjoint returns a gradient that is large and
wrong rather than absent, and the first check cannot see it — both sides solve
against the same bad Jacobian and agree.

`fixpoint-adjoint` is a **refinement of `adjoint`**, not an alternative to it.
It names how the adjoint is synthesised — by the implicit-function theorem over
a converged fixed point — and it runs `adjoint`'s gate plus one more. It is
never an exemption from validating the adjoint. **The escape hatch is
`relaxed`**: it is the tag for a genuinely non-smooth row, and it forces either
an honest gradient or an explicit retag carrying a named relaxation and a
recorded rationale. A row that is not a converged fixed point cannot be retagged
into `fixpoint-adjoint`.

**A passing gate is not evidence of a correct tag.** The two products agree
trivially wherever the true gradient is zero, so a row whose output is
piecewise-constant — an argmin over a discrete set, a hard-cutoff count —
**passes this gate spuriously** and ships a certificate for a gradient that does
not exist. Registry rows 46 and 50 are that shape. Before trusting an `adjoint`
pass, check that the sampled points straddle a region where the output actually
varies.

**A dormant row cannot be gated, and must not read as though it were.** Registry
row 122 (`iterative-lbte-kappa`) is tagged `fixpoint-adjoint`, but its
`provenance` cell declares it dormant, anchored to a published iterative thermal
conductivity in V1 with the live solve deferred to V2. In V1 it returns an
anchored constant: there is no fixed point, so there is no fixed-point Jacobian
to condition, and both gates pass it trivially. That is the spurious pass one
level worse, because here the gradient is not merely locally zero but
structurally absent. The tag describes the V2 form. Until the live solve lands,
the row's gate is **deferred, not passed**, and a deferred gate must be recorded
as such in the cert rather than emitted as a pass. Any other row whose
`provenance` declares it dormant or anchored inherits this rule.

**The cert has no way to say "deferred".** `adjoint-cert` carries four cases —
`Passed`, `Failed(witness)`, `NotApplicable`, `Relaxed(rationale)` — and a
deferred gate is none of them. The rule above cannot be encoded in the record
this page defines.

Under the always-cheap discipline, most `adjoint` generators with a fixed-point
solve in their forward pass are wired to the **implicit-differentiation adjoint
synthesised at the lowering stage**
([compose-time-pipeline#lowering-and-adjoint-synthesis]); the gate verifies that
synthesised adjoint, not a hand-written backward.

**What the gate does not cover.** It runs once, at registration, against the
*formula's* adjoint. The *composition's* adjoint is synthesised later, per
composition, over a graph the simplification stage has already rewritten.
Nothing revalidates the second against the first. The rewrite-admission rule
([compose-time-pipeline#rewrite-admission]) makes a rewrite's *value* discrepancy
visible; it says nothing about whether the adjoint that ships is still the one
that was gated.

## Dressing certificates

The `OneShotCert` and `IterativeResult` records — one-shot-dressing and
iterative-dressing per [born-oppenheimer-levels#dressing-tiers] — are schemas
attached to dressed `MethodInvoke` nodes, not per-generator fields.

```
record OneShotCert {
  scheme            : G0W0 | SCP-perturbative | LO-TO-NA-correction
                    | Born-charge | epsilon-infinity | electronic-susceptibility
  inputs-hash       : ContentAddress
  parameters        : Map<Symbol, Value>          -- k-mesh, cutoff, …
  output            : DressedQuantity
  closure-residual  : Map<ResidualKey, Scalar>    -- one entry per axis tuple the cert
                                                  --   verifies; granular like every
                                                  --   other residual emission
  reference-state   : Address[StateSnapshot]      -- what "frozen at reference" is
                                                  --   frozen AT
  staleness-coeff   : Quantity                    -- ‖∂(dressing)/∂x‖, measured once at
                                                  --   reference-state, at compile time
  cost-tier         : milliseconds | seconds
}
```

The last two fields are the frozen dressing's **validity radius**, computable
rather than declared. A one-shot dressing does not respond to state excursions
and contributes no gradient ([born-oppenheimer-levels#dressing-tiers]), so the
term it drops is its state-dependence. To first order that term is `‖x −
reference-state‖ · staleness-coeff` — a compile-time coefficient measured once
where the dressing is already being computed, times a runtime norm. Their
product is the dressing-staleness entry of the error budget
([residual-definitions#error-budget]).

This is the fidelity rule applied to a dressing: a frozen approximation is still
an approximation, so it owes an estimator, and the estimator *is* the radius.
Nothing is refused for leaving the radius — the term simply grows, and the
consumer reads it.

```
record IterationSnapshot {                        -- one element of a trajectory
  iter              : Nat
  residual          : Map<ResidualKey, Scalar>    -- per-key closure residual
  energy            : Scalar                      -- functional value at this iteration
  witness           : Optional<Witness>           -- non-null iff divergent
  params            : Map<Symbol, Value>          -- mixing factor, broadening, …
}

record IterativeResult {                          -- iterative-dressing; V2-deferred
  scheme            : scGW | SSCHA-stochastic | TDEP | BSE-iterated
                    | DMFT | polaron-self-consistent
  inputs-hash       : ContentAddress
  parameters        : Map<Symbol, Value>          -- mixing, broadening, max-iter
  trajectory        : List<IterationSnapshot>
  converged?        : Bool
  divergence-witness: Optional<Witness>           -- non-null iff not converged
  final             : DressedQuantity
  cost-tier         : minutes
}
```

V1 ships one-shot-dressing wired, and iterative-dressing as type and cert
scaffolding only, with `not-implemented-in-V1` stubs that fail loud.
