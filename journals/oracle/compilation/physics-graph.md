---
id: physics-graph
title: "The physics graph"
owns:
  - physics graph schema
  - graph node kinds and output roles
  - per-stage sidecars
  - graph realization of the closed vocabularies
  - arena and index graph representation
  - graph acyclicity guarantee
  - observable selection precedence
anchors:
  the-graph: "The one data structure"
  acyclic: "Acyclic, and why that word is load-bearing"
  representation: "The arena representation"
  node: "Anatomy of a node"
  node-kinds: "The three node kinds"
  output-role: "Output role"
  observable-selection: "Which formula the observable exposes"
  sidecars: "Per-stage sidecars"
  vocabulary-realization: "The graph is every other vocabulary"
  why-one-structure: "Why it is the data structure"
depends-on:
  - crystal-inputs
  - unified-state
  - generic-dynamics
  - compose-time-pipeline
  - representation-substrate
  - born-oppenheimer-levels
  - typeclass-alphabet
  - canonical-vocabularies
  - named-formulas
  - computational-methods
  - property-templates
  - observable-bundles
  - residual-definitions
  - cert-obligations
  - applicability-classifiers
  - topology-atlas
  - coupling-structure
  - gamma-hat
  - pino-bridge
  - forced-decisions
open-questions: []
---
# The physics graph

## The one data structure

Given the inputs ([crystal-inputs#top-level-inputs]), the unified state
([unified-state]), and the dynamics ([generic-dynamics#generic-form]), there is one
data structure that everything else in the oracle library is a view of:

> **The `PhysicsGraph`.**

A typed, hash-consed, content-addressed directed acyclic graph. It is what the
compose-time pipeline produces ([compose-time-pipeline]), what the runtime kernel
evaluates, what the certification obligations traverse
([cert-obligations#the-ten-obligations]), and what the operator library trains against. Every other *thing* in the oracle — formulas,
methods, templates, observables, residuals, bundles, applicability classifiers, the
topology atlas — is a kind of node, a labelled subset of nodes, or a per-stage sidecar
indexed by node id.

## Acyclic, and why that word is load-bearing

The physics graph is **directed and acyclic**, and its topological order **is** its
evaluation order. Nothing else in the compiler has to supply a schedule: the order in
which values become available is a property of the structure itself.

Self-consistency does not put a cycle in it. A converged fixed point is a
`MethodInvoke` node whose named method has fixed-point semantics, so the recursion
lives *inside* one node and the edge set stays acyclic. Every pass that closes over the
graph — hash-consing, cross-formula subexpression elimination, tape scheduling, codegen
— terminates for that reason.

**One token, two structures with opposite guarantees.** The dependency relation among
the pages of this corpus is *cyclic* by construction — two pages routinely explain each
other — and must never be closed over. That object is the **page index**, and it is
emitted rather than authored. `graph` unqualified inside this library means the physics
graph, and the physics graph is the acyclic one. A rule that holds for the page index
does not transfer here, and applying "the graph is cyclic by design" to anything on
this page inverts its central guarantee.

## The arena representation

Nodes live in a flat array and `NodeId` is an integer handle, not a pointer. That buys
compact storage, cache locality on traversal, trivial serialization, and a hash-cons
table keyed directly by address.

Edges are the `args` lists inside apply and invoke nodes. There is no separate edge
table and no edge carries an identity of its own; the graph is the multiset of its
output-root addresses closed under children-pointers.

## Anatomy of a node

```
Node =
  ( id   : ContentAddress    -- hash-cons identity; the typed family is
                             --   Address[GraphNode]
  , type : Layer0Type        -- the typeclass alphabet
  , kind : NodeKind
  , role : OutputRole
  )
```

Four fields. Two — `kind` and `role` — are named sum types whose names earn their keep;
one reuses the existing typeclass alphabet ([typeclass-alphabet#axes]); one is the
hash-cons
identity, whose exactness discipline is [representation-substrate#identity-exact].

Per-node decorations — applicability predicates, symmetry annotations, compression
plans, adjoint strategies, certification hooks, provenance tags — live in per-stage
sidecars instead of on the node, produced by one stage and visible to later stages
under the stage-visibility order ([representation-substrate#replaces]). None of them is
carried into the runtime kernel.

`NodeKind` is the substrate's **primary closed-polymorphism mechanism**: a closed
vocabulary that discriminates the typed payload sum
([representation-substrate#clusters]). Graph identity is the closure of the multiset of
output `Address[GraphNode]` values under children-pointers; the graph has no identifier
independent of its outputs.

## The three node kinds

```
NodeKind =
  | Input(InputKind)
  | FormulaApply(formula : NamedFormula, args : List<NodeId>)
  | MethodInvoke(method  : NamedMethod,  args : List<NodeId>)

InputKind = StateSlot(StateComponent) | EnvScalar(EnvField)
```

Every operation in the oracle is one of these three:

1. **`Input`** — a slot of the unified state ([unified-state#slots]) or an
   environmental scalar such as temperature, chemical potential or applied field
   ([crystal-inputs#environment]).
2. **`FormulaApply`** — application of one of the named formulas
   ([named-formulas#the-registry]) to typed argument nodes.
3. **`MethodInvoke`** — application of one of the computational methods
   ([computational-methods#the-alphabet]) to typed argument nodes.

Three constructs look as though they might be further node kinds, and are not:

- **Symmetry projection** is `MethodInvoke(symmetry-projection, …)` — one of the
  existing methods. The symmetry quotient
  ([compose-time-pipeline#symmetry-quotient]) inserts these as `MethodInvoke` nodes,
  not as a new species.
- **Fixed-point solves** — self-consistent field, relaxation-time transport, the
  steady-state Liouville problem — are `MethodInvoke` of the methods that carry
  fixed-point semantics. The fixed-point property is a fact about the named method,
  looked up when adjoints are synthesized
  ([compose-time-pipeline#lowering-and-adjoint-synthesis]).
- **Observables and residuals** are *roles*, not kinds. The same computation is
  `Internal` in one composition and an `Observable` in another.

## Output role

```
OutputRole =
  | Internal
  | Observable(bundle : BundleId)
  | ResidualLeaf(key : ResidualKey)
```

The role tells the runtime kernel which nodes are *exposed*. `Internal` nodes are
evaluated and never returned. `Observable` nodes feed the operator seam
([pino-bridge#surface])
and carry a bundle tag drawn from the observable-bundle universe
([observable-bundles#the-eleven]). `ResidualLeaf` nodes produce the entries of the
granularity-keyed residual vector defined in [residual-definitions#granularity].

### Which formula the observable exposes

When more than one formula computes the same observable, the `Observable` role
designates which compose-time-selected one is the **exposed** value to downstream
consumers. Selection is by precedence over the contribution facets
([residual-definitions#facets]): declared dressing tier first, then registration order.

**The unselected formulas still contribute their residual leaves.** Losing the
`Observable` role does not remove a node from the graph; it removes it from the
exposed output while its `ResidualLeaf` keys survive intact.

That is the whole of the discipline: **the graph never averages observables and never
silently selects between formulas at runtime.** Both are evaluated, both are exposed as
leaves, and the disagreement between them is a typed residual rather than a hidden
choice. A reader looking for where the blend happens will not find one, because there
is none.

The same shape governs dressed quantities. A bare and a dressed residual on the same
observable live as **distinct `FormulaApply` and `MethodInvoke` chains** in the graph —
**not as weighted siblings**. The dressing tag that distinguishes them is a provenance
label rather than a weighting axis ([born-oppenheimer-levels#dressing-tiers]), and the
graph structure is what makes that true: there is no node at which a weight between
them could be applied.

## Per-stage sidecars

Information that a stage decides *about* nodes or channels lives in maps keyed by a
typed sidecar key: `NodeId` for per-node decorations, `CouplingChannel` for the
invariant sidecar. Each map is produced by one stage and visible to any later stage
under the stage-visibility order ([representation-substrate#replaces]); the backing
store is a persistent map ([representation-substrate#clusters]). Sidecars are **not part
of a node's identity, not hash-consed, and do not survive their last consumer**.

```
SymbolicLiftSidecar.applicability      : Map<NodeId, Predicate>
SymbolicLiftSidecar.coupling-channels  : List<CouplingChannel>
SymmetrySidecar.symmetry               : Map<NodeId, IrrepBlock>
InvariantSidecar.invariants            : Map<CouplingChannel, GeneratorOutput>
LoweringSidecar.compression            : Map<NodeId, CompressionPlan>
LoweringSidecar.adjoint                : Map<FixedPointNodeId, AdjointSolver>
LoweringSidecar.materialization        : Map<TapeNodeId, Store | Recompute>

CompressionPlan =
  | Dense
  | Sparse(sparsity-pattern)
  | LowRank(rank)
  | HODLR(params)
  | TT(ranks)
  | …
```

The operator never sees these sidecars. The runtime kernel does not carry them either:
they are codegen inputs, consumed during lowering and erased. Which plan each
operator-typed node receives is decided by
[compose-time-pipeline#lowering-and-adjoint-synthesis].

## The graph is every other vocabulary

| Vocabulary item | Realized as |
|---|---|
| named formulas ([named-formulas#the-registry]) | typing rules for `FormulaApply` nodes |
| computational methods ([computational-methods#the-alphabet]) | typing rules for `MethodInvoke` nodes |
| property templates ([property-templates#what-a-template-is]) | graph-construction macros that emit subgraphs |
| observable bundles ([observable-bundles#the-eleven]) | the `bundle` payload of `Observable` roles |
| residual categories ([residual-definitions#categories]) | a facet on `ResidualLeaf`, in `ContributionFacets.category` |
| Born–Oppenheimer levels ([born-oppenheimer-levels#hierarchy]) | a label **derivable from a node's transitive inputs; not stored** |
| the typeclass alphabet ([typeclass-alphabet#axes]) | the `type` field on every node |
| applicability classifiers ([applicability-classifiers#the-predicate-contract]) | a symbolic-lift sidecar that *prunes* the graph; not retained |
| the topology atlas ([topology-atlas#entry]) | a precomputed table consumed by the symmetry quotient |
| certification obligations ([cert-obligations#the-ten-obligations]) | global traversals, indexed by `NodeKind` and `OutputRole` |
| the density-matrix encoding ([gamma-hat#encoding-vocabulary]) | a `CompressionPlan` for nodes whose `type` is the density-matrix typeclass |
| `Validate` ([pino-bridge#validate]) | the differentiated projection to `Observable` and `ResidualLeaf` outputs |
| `Import` ([pino-bridge#import]) | insertion of `Input` nodes pinned to external values, plus certification-only `ResidualLeaf` nodes |

The Born–Oppenheimer row is the one to read twice. A node's level is a **derived**
property, recomputed from the transitive input set; storing it would create a second
place for it to be wrong.

## Why it is the data structure

- **Closure.** Every closed vocabulary ([canonical-vocabularies#scope]) is either a typing
  rule for a node kind, a labelled subset of nodes, or an annotation field on a node.
  Nothing in the oracle lives outside the graph.
- **Composition.** Composing observables *is* composing subgraphs. Property templates
  ([property-templates#what-a-template-is]) are graph-construction macros, and coupling
  channels ([coupling-structure#channel-record]) lower into `FormulaApply` nodes on the
  assembly aggregators.
- **Correctness.** The certification layer ([cert-obligations#the-ten-obligations]) is a graph traversal;
  the granularity discipline ([residual-definitions#granularity]) is "leaves are
  addressable"; the
  symmetry discipline is a rewrite; the adjoint discipline is a per-node lowering
  strategy.
- **Performance.** The pipeline ([compose-time-pipeline]) is graph rewrites and
  lowering. Performance work has no other surface.
- **Substrate-agnosticism.** The graph is language-neutral typed pseudocode. Which host
  it lives in is the implementation-language question
  ([forced-decisions#implementation-language]); the concept
  is invariant under that choice.

> The `PhysicsGraph` is to the oracle what the relational schema is to a database:
> every other notion is a view, a query, or an annotation over it. Picking a language
> is picking a host for *this* graph.
