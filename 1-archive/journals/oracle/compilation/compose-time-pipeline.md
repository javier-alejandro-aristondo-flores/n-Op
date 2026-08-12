---
id: compose-time-pipeline
title: "The compose-time pipeline"
owns:
  - compose-time pipeline stages
  - always-cheap discipline
  - the pipeline as partial evaluation
  - stage boundaries
  - rewrite admission rule
  - compression plan selection
  - adjoint synthesis and tape scheduling
  - runtime cost classes
anchors:
  always-cheap: "The always-cheap discipline"
  partial-evaluation: "The pipeline is partial evaluation"
  symbolic-lift: "Symbolic lift"
  symmetry-quotient: "Symmetry quotient"
  invariant-synthesis: "Invariant synthesis"
  algebraic-simplification: "Algebraic simplification"
  rewrite-admission: "The rewrite-admission rule"
  lowering-and-adjoint-synthesis: "Lowering and adjoint synthesis"
  runtime-kernel-application: "Runtime kernel application"
  boundary: "The compose-time and runtime boundary"
depends-on:
  - crystal-inputs
  - unified-state
  - physics-graph
  - representation-substrate
  - generic-dynamics
  - born-oppenheimer-levels
  - named-formulas
  - computational-methods
  - property-templates
  - observable-bundles
  - residual-definitions
  - residual-machinery
  - cert-obligations
  - applicability-classifiers
  - topology-atlas
  - coupling-structure
  - gamma-hat
  - pino-bridge
  - traps
open-questions:
  - id: algebraic-simplification-performance
    anchor: algebraic-simplification
    summary: "Equality saturation is the hardest pass to build and its cost is open-ended; no bound on saturation time or e-graph size is committed anywhere."
---
# The compose-time pipeline

## The always-cheap discipline

The oracle exposes **one residual surface, evaluated through one stack, at one
fidelity**. Runtime cost is bounded by compose-time specialization, symmetry
quotienting, compression, and structural sharing — every kernel emerging from the
stages below is fast by construction.

Everything except the runtime stage executes **once per
`(PeriodicityStructure, SiteDecoration, Environment)` tuple**, producing a compiled
kernel. The runtime stage applies that kernel to dense state vectors millions of times
per training run.

The lever is the same at every stage: expensive structure discovery — symmetry
reduction, sparsity pattern, compression plan, adjoint factorization — happens once, at
compose time, so the runtime only *applies* precomputed structured operators. That is
what lets every runtime hot path stay logarithmic or better and call no solver
([representation-substrate#hot-paths]).

## The pipeline is partial evaluation

That lever has a name, and the name carries a result.

**The first Futamura projection:** specializing an interpreter to a fixed program
yields a compiled program (Futamura, *Partial Evaluation of Computation Process — An
Approach to a Compiler-Compiler*, Systems·Computers·Controls 2(5), 1971, 45–50).

This library is that construction. The general physics evaluator is the interpreter;
the `(PeriodicityStructure, SiteDecoration, Environment)` tuple
([crystal-inputs#top-level-inputs]) is the fixed program; the compiled kernel is the
specialized residue. **Compile in seconds, call in microseconds** is therefore the
expected shape of a partial evaluator, not an optimization anyone had to hope would
work.

Two things follow that are otherwise easy to mistake for taste.

- **The compose-time and runtime split is the specialization boundary**, not a
  convenience. Everything symbolic happens on the side where the fixed program is
  known; everything numeric happens on the side where only the varying input remains.
  That is why the boundary falls exactly where it does — the compose-time and runtime
  boundary below states which stage sits on which side — and why a decision cannot be
  moved across it without changing what is being specialized.
- **A runtime structural branch is a specialization failure.** If the kernel still has
  to ask a question whose answer was fixed at compose time, the specializer left work
  undone. That is the reason structural branching on the hot path is barred rather than
  merely discouraged, and it is why every predicate this library evaluates is settled
  before codegen.

## Symbolic lift

**Inputs.** The request — which observable bundles ([observable-bundles#the-eleven]) and
which residual categories ([residual-definitions#categories]) the composition must cover — plus the
three descriptors ([crystal-inputs#top-level-inputs]) and the applicability classifiers
([applicability-classifiers#the-predicate-contract]).

**Action.** Construct the initial graph ([physics-graph]): each requested property
template ([property-templates#what-a-template-is]) is instantiated as a subgraph of `Input`,
`FormulaApply` and `MethodInvoke` nodes, in Born–Oppenheimer level order
([born-oppenheimer-levels#hierarchy]).

**Sidecar produced.** `SymbolicLiftSidecar.applicability : Map<NodeId, Predicate>`.
Each node's applicability predicate is a reduced ordered binary decision diagram, so
evaluation costs one decision path. Any subgraph whose applicability is false for this
crystal-and-environment pair is **deleted**. After this stage every remaining node is
meaningful for this composition, and the sidecar is discarded.

## Symmetry quotient

**Inputs.** The pruned graph; the topology-atlas entry for this composition's space
group, Wyckoff orbits and orbital basis ([topology-atlas#entry]).

**Action.** Two rewrites, both purely symbolic — no numerics run here. Both exist to
reduce the work the runtime stage will do.

- **Operator block-diagonalization.** Every operator that commutes with the
  space-group action is rewritten into its irreducible-representation decomposition.
  Schur's lemma collapses a dense `MethodInvoke(eigendecomposition, …)` node into
  per-irrep blocks, turning one cubic-in-dimension dense eigensolve into a sum of much
  smaller ones.
- **Irreducible-wedge orbit collapse.** Nodes ranging over the full Brillouin zone are
  rewritten to range over the irreducible wedge with integer orbit weights. In cubic
  systems this is up to **48× fewer** sample points.

`MethodInvoke(symmetry-projection, …)` nodes are inserted at the boundaries.

**Hardware consequence.** The blocks are *small* — cubic point groups give irrep
dimensions in `{1, 2, 3}`, up to 4 under spin–orbit coupling. That favors a
cache-resident dense solve per block and is a **poor fit for wide-SIMD or GPU
execution unless many blocks are batched together**. It is the one place where the
symmetry reduction and the target hardware pull in opposite directions.

**Sidecar produced.** `SymmetrySidecar.symmetry : Map<NodeId, IrrepBlock>`, consumed
during lowering when operator representations are chosen.

## Invariant synthesis

**Inputs.** The `SymbolicLiftSidecar.coupling-channels : List<CouplingChannel>`
declared by the composition ([coupling-structure#channel-record]); the crystal symmetry
group
constructed by the two preceding stages.

**Action.** For each channel whose applicability holds, run the invariant generator
([coupling-structure#invariant-generator]) and return the finite basis of target-shaped
symmetry-invariant terms at the channel's order and derivative depth.

Each `InvariantTerm` is the **constructive dual of an irrep-block decomposition**: the
same machinery as the symmetry quotient, applied to *build* invariants rather than to
*decompose* operators. That duality is why this stage sits where it does — it is not a
peer of the stages around it but the constructive face of the one before it, and its
outputs feed the one after it.

**Sidecar produced.** `InvariantSidecar.invariants : Map<CouplingChannel,
GeneratorOutput>` — the full generator contract of
[coupling-structure#generator-contract]: the polynomial basis, the
polynomial-sufficiency echo, and any `kernel_extension`
([coupling-structure#kernel-ext] — the nullspace sense of the word, not the compiled
artifact). Consumed by algebraic simplification,
which lowers the invariants into `FormulaApply` nodes on the energy functional
([generic-dynamics#functionals]) and the operator-assembly aggregators
([generic-dynamics#operators]).

## Algebraic simplification

**Action.** Three rewrites, all exact and adjoint-safe, implemented as equality
saturation over an e-graph — union-find over equivalence classes plus e-matching:

- **Hash-consing.** Pure subexpressions appearing in several residuals — a band
  structure, a charge density, a force field, a dynamical matrix — collapse to a single
  node referenced by every consumer.
- **Cross-formula subexpression elimination.** The named formulas
  ([named-formulas#the-registry]) often share intermediate quantities; these are pulled
  out.
- **Tearing and alias elimination.** Algebraic dependencies are resolved at compose
  time, and sparsity patterns are inferred for the next stage.

**Granularity survives.** Every `ResidualLeaf` keeps its content-addressed
`ResidualKey` ([residual-definitions#residualkey]); sharing an upstream node does not
collapse the
leaves that consume it. Sharing is an implementation fact about evaluation, not a claim
about which residuals are distinct.

**Sidecar produced.** None. The graph itself is the output.

This is the algorithmically hardest pass to build, and its cost is the one open-ended
figure in the compose-time budget.

## The rewrite-admission rule

**Why only three rewrites.** "Exact and adjoint-safe" holds for those three because
none of them changes a value or a derivative. It is **not** a property of the rewrite
*system*: past these three, exactness needs a side-condition discipline — positivity
guards, branch-cut guards — that none of the three carries.

**Normative.** A rewrite may be added to this stage if and only if:

1. it is **exact over the reals** — the rewrite is a real-algebra identity, so the
   e-graph's equality relation stays exact and
   [representation-substrate#identity-exact] is untouched;
2. every condition under which it fails in floating point is expressed as a **side
   condition discharged by an e-class analysis** — an interval fact, a not-equals fact
   — and not as a caveat in prose; and
3. it registers a **fidelity generator** for its floating-point discrepancy
   ([residual-machinery#fidelity-generators]).

Equality saturation stays an **offline** rewrite oracle. Its internals never cross this
stage's boundary; only the chosen rewrite does, and that rewrite is admitted under the
rule above.

**This is shipped state of the art, not a hope.** Herbie (Panchekha et al., PLDI 2015)
is the reference tool for floating-point accuracy rewriting. Its rule set was
known-unsound for years, causing repeated bugs — and the load-bearing fact, which is
Zhang et al.'s finding about Herbie rather than a claim in Herbie's own paper, is that
*merely deleting the unsound rules made the tool useless on a large part of its own
benchmark suite*. **Exactness-only is not a viable gate.** Zhang et al. (PLDI 2023,
`egglog`) made those rules sound by exactly the mechanism in condition 2: an interval
analysis carried as an e-class analysis, composed with a not-equals analysis,
discharging the side conditions rule by rule. On 289 benchmarks the sound version was
*faster* — unsound candidates had been slowing the search — and found a more accurate
program in **104** cases, against **135** where the unsound rule set still won on
accuracy. Soundness here is *affordable*, not free: no cost in time, a roughly even
trade in accuracy, and a search that cannot lie.

Note what that architecture does and does not do. The equality relation remains exact
over the reals, and the interval facts ride **alongside** it in an analysis — the
separation stated at [representation-substrate#identity-exact], which records that this
is where two communities reached it independently.

**A sharper form waits downstream.** [traps#trajectory-safety] records the case an
evolving consumer faces, where a rewrite that is exact almost everywhere but wrong on a
measure-zero set is tolerable for a pointwise scorer and not for a flow attracted to the
bad set. The oracle scores rather than integrates ([gamma-hat#scorer-only]), so that
case is consumer-side: the hazard is exported to whoever integrates, along with the rest
of the integration contract, rather than dissolved here.

## Lowering and adjoint synthesis

**Action.** Four concurrent decisions.

**Compression-plan selection.** Each operator-typed node is assigned a
`CompressionPlan` ([physics-graph#sidecars]). The decision procedure, per node:

| Structure found | Plan |
|---|---|
| small or dense operator | `Dense` |
| known or inferred sparsity pattern, from the preceding stage's inference | `Sparse(pattern)` |
| numerical rank far below the dimension, estimated by rank-revealing QR or a randomized-SVD range-finder here | `LowRank(rank)` |
| hierarchically low-rank off-diagonal blocks | `HODLR(params)` |
| high-dimensional tensor operator, such as a collision operator | `TT(ranks)`, cores built once by sequential tensor-train cross |

**Each compression plan carries a per-plan error target** — the truncation tolerance
for the low-rank, hierarchical and tensor-train ranks — and the rank is chosen to *meet
that target*, not by structure alone. The target enters the per-residual error budget
through `Quantity.combineTol` ([residual-definitions#error-budget]).

**Whether a plan applies at all is decided here too, and by the same mechanism.** Slot
applicability is a **compile-time predicate over `(PeriodicityStructure,
SiteDecoration)`**, evaluated at this stage alongside every other lowering choice. It is
never a runtime check — that would be structural branching on the hot path, and its cost
is what made the question look hard. Which predicate governs a given encoding slot is
the encoding vocabulary's ([gamma-hat#encoding-vocabulary]).

**Adjoint synthesis.** For every `MethodInvoke` whose named method has fixed-point
semantics, the **implicit-differentiation adjoint** is synthesized. Gradient cost
becomes one extra linear *system*, independent of the forward iteration count — **not
constant work**, since that system is itself solved iteratively, but independent of how
long the forward solve ran (Blondel et al., *Efficient and Modular Implicit
Differentiation*, NeurIPS 35, 2022, 5230–5242; the contrast is with unrolling, whose
memory scales linearly in iteration count). This is what makes residuals with
fixed-point semantics tractable as gradients.

The conditioning of that linear solve is set by the fixed-point map's Jacobian.
**Near-singular Jacobians — slow self-consistency — are the failure mode**, and they
are what the registration-time adjoint gate ([residual-machinery#registration-gate])
exists to catch.

**What the gate sees is a formula's own adjoint, validated once at registration. What
this stage synthesizes is the *composition's* adjoint, per composition, over a graph
that algebraic simplification has already rewritten.** The two are different objects,
and the exposure that creates is the gate's to carry
([residual-machinery#registration-gate]).

Nesting constrains the order. A force evaluation on the Born–Oppenheimer surface
*contains* a converged quantum-electronic-substrate inner solve
([born-oppenheimer-levels#hierarchy]), so the adjoint has to thread the
implicit-differentiation
chain through **both** levels, not only the outer one.

**Adjoint-tape materialization schedule.** Reverse mode needs forward values, and each
one is either **stored** or **recomputed**. Choosing per node is the classic
rematerialization-versus-storage trade-off, and it is decided here, at compile time,
from the graph's shape — never by a runtime heuristic, which would be structural
branching on the hot path. On a chain the optimal schedule is known in closed form
(`revolve`; Griewank & Walther, *ACM TOMS* 26(1) 19–45, 2000). On a general directed
acyclic graph the problem is **NP-complete** (Naumann, *J. Discrete Algorithms* 7(4)
402–410, 2009 — a separate result from `revolve`). The plan is therefore a bounded
heuristic over the tape, with its choice recorded.

**This lowering owes no fidelity generator**
([residual-machinery#fidelity-generators]). Recomputing a
value and reading a stored one give the *same* value, so the schedule trades memory
against time and introduces no discrepancy to estimate. That is worth stating because
it marks the boundary of the error-estimate obligation
([representation-substrate#estimate-dont-decide]): the obligation is about *value*, not
*cost*, and this is the lowering that shows the difference.

**Codegen.** The whole graph is lowered to a compiled kernel with one entry point — the
`Input` slots — and four typed exits: a residual map keyed by `ResidualKey`, a gradient
map on the same keys, an observable map, and the certification evidence produced by the
obligation traversals ([cert-obligations#the-ten-obligations]).

**Sidecars produced.** `LoweringSidecar.compression`, `.adjoint`, `.materialization`.
All three are codegen inputs and all three are erased once codegen completes
([physics-graph#sidecars]).

## Runtime kernel application

**Inputs.** A dense state vector ([unified-state#slots]) and an environment
([crystal-inputs#environment]).

**Action.** Apply the compiled kernel. No symbols. No interpretation. No path
selection.

**Outputs.**

```
evaluate : (State, Environment) → ( ResidualVector  : Map<ResidualKey, Scalar>
                                  , Gradient        : Map<ResidualKey, Cotangent>
                                  , ObservableMap   : Map<ObservableRef, Value>
                                  , CertEvidence    : CertEvidence )
```

The numeric work inside is the computational methods
([computational-methods#the-alphabet]); the
forward cost is graph evaluation, and the optional adjoint pass is reverse mode by
structural projection, linear in the residual vector's size.

**`kernel` here means the compiled artifact** — the thing this stage applies, the thing
the composition fingerprint keys, the thing that carries a file hash. Physics operators
whose names contain the word (`CollisionKernel`, `ResponseKernel`) and the nullspace
sense (`kernel_extension`) are always written with their qualifier and are never what
`kernel` alone denotes here.

The operator library sees the graph only through `ResidualKey` content hashes and never
touches a node directly ([pino-bridge#surface]). **Loss aggregation lives in the operator
library, not here**: this stage emits the granular vector, and the operator chooses how
to reduce it.

## The compose-time and runtime boundary

| Stage | In → out | Runs | Algorithm class | Cost |
|---|---|---|---|---|
| symbolic lift | request + descriptors → pruned graph | once per composition | macro expansion + binary decision diagrams | seconds |
| symmetry quotient | graph → block-structured graph | once per composition | finite-group representation theory | seconds; group sums linear in group order, order at most 192 |
| invariant synthesis | coupling declarations → tensor-algebra DAGs | once per composition | Reynolds projection over a finite group | seconds; at most 12 M operations, cached |
| algebraic simplification | graph → shared, sparse graph | once per composition | term rewriting over an e-graph | open-ended; the hardest pass |
| lowering and adjoint synthesis | graph → compiled kernel | once per composition | numerical-linear-algebra planning + implicit-differentiation + codegen | seconds–minutes |
| runtime kernel application | (state, environment) → numbers | **per state sample** | the computational methods ([computational-methods#the-alphabet]) | microseconds–milliseconds, millions of times |

The **Runs** column is the split. Five stages run once per composition; one runs per
sample. Nothing else about the stage list carries that distinction, and no count in a
name is asked to.

The two sides have opposite performance characters. Compose time is branchy,
allocation-heavy and pointer-chasing — **latency- and correctness-bound, not
throughput-bound**. Runtime is a straight-line numeric function with no symbols, no
structural branching, and no solver invoked from scratch.

**What triggers a recompile.** A composition fingerprint — a content hash of
periodicity, decoration, and the *structural* part of the environment — keys a kernel
cache. Scalar environment parameters that vary during training, such as a temperature
sweep, are passed as runtime inputs and are not baked into the kernel. Only structural
changes trigger a recompile. Which environment fields are structural and which are
swept is [crystal-inputs#structural-swept]'s to state.

**Runtime cost is three-class, not one.** The microseconds-to-milliseconds figure in
the table above is only the per-sample core.

| Class | What | Cost | Recomputed |
|---|---|---|---|
| per-sample core | equation-of-motion residual evaluation | microseconds–milliseconds | every call |
| on-request spectral | zone-resolved observables, full PDE residuals | 0.1–10 s | on request, then cached per composition |
| per-composition reference | property and reference solves | seconds–minutes | once per composition |

The **Recomputed** column is a cost fact: how often this library must do the work
again. How often a consumer *asks* is a loop policy and is not the oracle's to state
([named-formulas#cost-tiers] holds the two apart).

The seconds-to-minutes compile figure covers the five symbolic stages. The
per-composition *reference* solves that property observables require sit in the third
class and are scheduled off the per-sample hot path.
