# A3 — state, identity, graph

Build-sheet audit of Units 1–3: the state and environment types, crystal identity and
the kernel cache, and the physics graph. Each finding asks what an implementer must
type and reports what the corpus does not let them type.

Counts: **20 findings, all ABSENT.** Items reaching DETERMINED are counted in Coverage
and not reported individually.

---

## Unit 1 — the state and environment types

### S1 — the slow tier and the macro tier have no path into the oracle, in `pino-bridge.md`

**Verdict:** ABSENT

**The obligation.** The corpus makes the oracle responsible for scoring all three
tiers. `multiscale-state.md`:

> The oracle **scores** each tier's law violation; the operator supplies each tier's trajectory

and it puts two of the nineteen closed residual categories on the non-micro tiers:

> One `ResidualKey = (producer, axes)` space spans all tiers, over tier-typed axis universes. The

`residual-definitions.md` confirms both are live members of the closed `CategoryTag`
set, not aspirations:

>   - `EOM/DefectPopulation` — slow-tier defect-population kinetics,

**What is missing.** The only entry point takes two arguments, and neither is a slow
or macro state. `pino-bridge.md`:

> Validate(state    : UnifiedState,           -- the seven-tuple of unified-state
>          env      : Environment,

`UnifiedState` is the micro seven-tuple; `multiscale-state.md` is explicit that the
slow and macro tiers are *not* recoverable from it and are first-class state of their
own. So an implementer writing the runtime kernel has no expression for the value
`EOM/DefectPopulation[D,q,site]` reads: `c_D^q` arrives through no argument. The slow
fiber is placed in the substrate's *sidecar* cluster —

> The slow state `s` is a typed fiber in the substrate's **sidecars** cluster —

— and sidecars are compile-time objects that `physics-graph.md` says are none of them
"carried into the runtime kernel." Nothing states whether the slow state is a third call
argument, a fourth `Input` node kind, an environment field, or a compile-time constant.
Same for `MacroState`, which is given a full typed schema and no delivery mechanism.

**Control.** Searched `grep -rn "MacroState" journals/` → 2 hits: the definition in
`multiscale-state.md` and a glossary pointer. Searched
`grep -rEn "slow state|slow-state|slow fiber" journals/` → 13 hits, distributed
`multiscale-state.md` 9, `crystal-inputs.md` 2, `born-oppenheimer-levels.md` 1,
`glossary.md` 1 — every hit inside a state-definition page, none at a call site or node
constructor. Control that fires:
`grep -rn "env      : Environment" journals/` → 1 hit, so the search style does reach
call-signature text, and `grep -rn "Environment" journals/` reaches argument-position
vocabulary broadly.

---

### S2 — nine of the nineteen residual categories score a state rate the caller has no way to supply, in `unified-state.md`

**Verdict:** ABSENT

**The obligation.** The structural residual that grounds every other one is written
against a time derivative. `residual-definitions.md`:

> Aggregate form: `‖dx_i/dt − (L δE/δx_i + M δS/δx_i)‖²` for each state component

`gamma-hat.md` is explicit that the rate is an *input*, supplied by the caller, and
that supplying it is what keeps the oracle a scorer:

> consistent with this and is not an exception: it *scores* a supplied `∂_t γ̂` against the

**What is missing.** None of the seven slots is a rate, and no argument of `Validate`
carries one. The seven-tuple is `(h, R_I, P_I, Π_h, Z_I, γ̂, A)` — `P_I` and `Π_h` are
*momenta*, conjugate variables, not `dR/dt` and `dh/dt` in the sense the residual needs,
and there is no conjugate at all for `γ̂`, `A` or `Z`. So an implementer emitting an
`EOM/γ̂` leaf cannot name the operand on the left of the minus sign. Three readings each
imply different code and different call contracts — the rate is an eighth slot; the rate
is a second state passed for finite differencing (`multiscale-state.md` says "the oracle
scores the finite-difference slow-state rate against the formula right-hand side at each
step", which implies two states per call); or the rate is a per-call auxiliary map keyed
by state component. The corpus states none of them, and the finite-difference sentence
is the only hint, appearing once and for the slow tier only.

**Control.** Searched `grep -rn "state derivative\|rate input\|xdot\|supplied rate\|predicted rate"
journals/` → 0 hits. Searched `grep -rn "∂_t γ̂" journals/` → fires (1 hit,
`gamma-hat.md`), so the search reaches time-derivative vocabulary; searched
`grep -rn "dx_i/dt" journals/` → fires, so it reaches the residual's own notation. The
absence is of a *slot or argument*, not of the notation.

---

### S3 — the vector-potential slot gets no discretization and no compression plan, in `unified-state.md`

**Verdict:** ABSENT

**The obligation.** Two of the seven slots are functions on continuous domains. The
state declares one of them as a field:

> The vector potential is carried in the Weyl gauge `A₀ ≡ 0`, transverse `∇·A = 0`;

and the seam requires the operator to emit it. The corpus solves this problem once, for
the other field-valued slot: `gamma-hat.md` gives the density matrix an entire encoding
product,

> Basis ∈ { Real, Reciprocal, Wannier, NaturalOrbital, SymmetryAdapted }
> Form  ∈ { Dense, Sparse, BlockDiag, LowRank }

a first-class-pair table, a selection stage, and a byte budget.

**What is missing.** `A` gets no encoding vocabulary, no basis, no grid, and no owner
page. It is also the only slot whose declared type carries a time argument while the
state is instantaneous, so an implementer cannot tell whether the slot holds one
`ℝ³` field or a history. The lowering stage assigns plans by node type —

> **Compression-plan selection.** Each operator-typed node is assigned a

— and `A` enters the graph as `Input(StateSlot(...))`, not as an operator-typed node, so
no stage reaches it. This is *adjacent to* the confessed `state-wire-schema` question but
is not it: that question asks for dtype, unit, index order and memory layout, all of
which presuppose an array. What is missing here is prior — which discretization family
`A` is an array *of*, and which stage decides.

**Control.** Searched `grep -rn "vector potential" journals/` → 4 hits: the slot
declaration and gauge statement in `unified-state.md`, one operator-library line naming
it as a discretization problem, one capability-slice mention. None is a representation.
Control that fires: `grep -rn "density matrix" journals/` returns dozens of hits
including an encoding table and a byte budget, so the search style finds slot
representations where they exist.

---

### S4 — a node's Born–Oppenheimer level is declared derivable and the derivation is never given, in `born-oppenheimer-levels.md`

**Verdict:** ABSENT

**The obligation.** The level is load-bearing for graph construction order, and the page
deliberately refuses to store it:

> A node's level is **derivable** from its transitive inputs. It is not a stored field on `Node` ([physics-graph#node]).
> Symbolic-lift ordering follows the level discipline: quantum-electronic-substrate nodes are

`physics-graph.md` repeats the commitment and tells the reader it is the important row:

> The Born–Oppenheimer row is the one to read twice. A node's level is a **derived**

**What is missing.** The function. An implementer must write `level : NodeId → Level`
and the corpus supplies neither its base case nor its inductive step. Base case: no page
assigns a level to `Input(StateSlot(h))`, `Input(StateSlot(Z))` or
`Input(EnvScalar(temperature))`. Inductive step: no page says whether a node's level is
the maximum over its inputs, a property of the invoked method, or a property of the
formula row — and the three disagree. The page's own hierarchy makes maximum-over-inputs
wrong: it states that each level "introduces its own irreducible state", so an
`equilibrium-statistics` node built entirely from `born-oppenheimer-surface` spectra has
inputs whose maximum is one level below its own. Two competent implementers write
different functions, and the graph is built in a different order under each.

**Control.** Searched `grep -rn "derivable" journals/` → 5 hits; searched
`grep -rn "transitive inputs" journals/` → 2 hits, both the declarations quoted above.
Searched for the rule itself: `grep -rn "level of a node\|maximum over\|max over its inputs\|level is the"
journals/` → 0 hits. Control that fires: `grep -rn "topological order" journals/` returns
the graph's evaluation-order rule, so the search style does find ordering rules where the
corpus writes them.

---

### S5 — the predicate that picks a density-matrix encoding is delegated in a circle, in `gamma-hat.md`

**Verdict:** ABSENT

**The obligation.** Lowering must choose one encoding per density-matrix node, and
`compose-time-pipeline.md` names the deciding mechanism and points elsewhere for its
content:

> **Whether a plan applies at all is decided here too, and by the same mechanism.** Slot
> applicability is a **compile-time predicate over `(PeriodicityStructure,
> SiteDecoration)`**, evaluated at this stage alongside every other lowering choice. It is

> is what made the question look hard. Which predicate governs a given encoding slot is
> the encoding vocabulary's ([gamma-hat#encoding-vocabulary]).

**What is missing.** The pointed-to section supplies one predicate and four pieces of
prose. It says of the rank slot:

> **Rank governs one of these slots, and it is decided once.** Whether `(NaturalOrbital, LowRank)`

— a testable condition. For the other four first-class pairs the "For" column reads
"periodic substrates — the diamond MVP default", "defects, surfaces, amorphous regions",
"interface layers and dangling bonds", "the output of `SymmetryAdaptedHamiltonianOf`".
None of those is a predicate over `(PeriodicityStructure, SiteDecoration)`. An
implementer given a `SiteDecoration` tagged `defect` on a periodic host — the ordinary
case for this project's own defect supercells — cannot decide between `(Reciprocal,
BlockDiag)` and `(Real, Sparse)`, and the two produce different kernels, different memory
profiles and different truncation error. The delegation closes without ever landing on a
decidable condition.

**Control.** Searched `grep -rn "encoding slot" journals/` → 1 hit, the delegating sentence
in `compose-time-pipeline.md`; `grep -rn "compile-time predicate" journals/` → 1 hit, the
same passage. The pointed-to section contains neither string. (Instrument note: an earlier
regex `slot predicate|slot applicability` returned 1 rather than 2 because the corpus wraps
"Slot / applicability" across a line break — line-oriented search under-counts any phrase
that spans a wrap, so both controls here are single-line strings.) Control that fires:
`grep -rn "is-polar-material" journals/` returns a named, defined, gate-bearing predicate,
so the corpus does write applicability predicates where it has them, and the search reaches
that vocabulary.

---

### S6 — transcoders are named once and specified nowhere, in `gamma-hat.md`

**Verdict:** ABSENT

**The obligation.** The encoding product has twenty cells and the page requires
conversion between them:

> convert on demand for operations whose runtime cost is lower in a different encoding.

**What is missing.** Everything an implementer would type. Which of the twenty encodings
convert to which — the page does not say the relation is total, and several conversions
(`Reciprocal → Wannier`, `NaturalOrbital → Real`) are substantial numerical algorithms in
their own right rather than reshapes. What algorithm each uses. What error each
introduces, which matters because `representation-substrate.md` obliges any operation
that can make a computed object differ from its exact counterpart to emit an estimate,
and a transcode plainly can. And when they run: "on demand" reads as runtime, which
collides with the barred runtime structural branch, while the always-cheap discipline
would put them at lowering. The word appears once in the corpus.

**Control.** Searched `grep -rn "Transcoder\|transcoder\|transcode" journals/` → 1 hit,
the sentence quoted. Control that fires: `grep -rn "hash-consing" journals/` returns
multiple hits across pages including an algorithm and a stage assignment, so the search
style finds compile-stage machinery that the corpus does specify.

---

### S7 — `mesh-axes` is the whole of the device mesh's generation specification, in `multiscale-state.md`

**Verdict:** ABSENT

**The obligation.** The macro tier's entire index geometry is a universe over mesh cells,
and every macro field is a fiber over it:

> `ordinal_policy = DenseU32`, `enumerator = enumerate(product(mesh-axes))` ([pino-bridge#axis-coverage]) and

> Mesh generation and refinement are committed as **structured-tensor** for version 1, the

**What is missing.** `mesh-axes` occurs exactly once in the corpus. An implementer
allocating a mesh needs the axis count, the extent of each axis, the cell spacing, and
where those come from — the `PeriodicityStructure`, the `Environment`, the compile
request, or a mesh file. None is stated. The page then specifies a great deal that rests
on the mesh existing: a finite-volume discretization, per-cell centroid, volume and face
list, Scharfetter–Gummel face fluxes and a per-cell Péclet estimate quoting "a ~10 nm
cell". That figure is the only quantitative handle on cell size anywhere, and it appears
inside a worked example rather than as a mesh parameter. The claim "structured-tensor" and
the form `enumerate(product(axes))` fix the mesh's *shape* and leave its *size* and
*origin* unwritten.

**Control.** Searched `grep -rn "mesh-axes" journals/` → 1 hit, quoted above. Searched
`grep -rn "cell spacing\|mesh size\|number of cells\|mesh resolution" journals/` → 0 hits.
Control that fires: `grep -rn "Monkhorst" journals/` returns a fully parameterized
reciprocal-space mesh — "an 8×8×8 Monkhorst–Pack mesh gives" — so the corpus does write
mesh parameters where it has them, and this search style finds them.

---

### S8 — the environment box has no type and no supplier, in `crystal-inputs.md`

**Verdict:** ABSENT

**The obligation.** The box is the mechanism that makes swept-environment validity
checkable rather than intended. `crystal-inputs.md`:

> Each emitted kernel is stamped with its **environment box** — the per-swept-field range set on
> which its invariant-synthesis structure is valid. A sample whose swept scalar leaves the box is
> masked out, or trips the relevant certification obligation, rather than being scored against a

`applicability-classifiers.md` makes the whole per-sample window discipline rest on it:

> What makes that checkable rather than merely intended is the environment box stamped on

**What is missing.** Three things, none of them the confessed structural-versus-swept
partition. First, the type: "range set" is not a type — one closed interval per swept
field, a union of intervals, a box in the product space, and a convex hull are all "range
sets" and they admit different samples. Second, the supplier: the compile stage's declared
inputs are

> **Inputs.** The request — which observable bundles ([observable-bundles#the-eleven]) and

plus the three descriptors and the classifiers. No sweep range is among them, and the
`Environment` record carries per-call *values*, not ranges — so nothing in the compile
request tells the compiler what box to stamp. Third, the disjunction: "masked out, **or**
trips the relevant certification obligation" leaves an implementer to choose the branch,
and the two have opposite consequences for a training run (a dropped sample versus a
failed build).

**Control.** Searched `grep -rn "environment box" journals/` → 3 hits: the definition, the
`applicability-classifiers.md` dependency, and a `traps.md` entry, none carrying a type or a
source. Searched `grep -rn "range set" journals/` → 2 hits: the definition itself, and
`applicability-classifiers.md` stating it needs one ("without a recorded range set"). Both
demand the object; neither types it. Control that fires: `grep -rn "validity window" journals/` returns worked, numeric windows
elsewhere in the corpus ("Ohmic below ≈10⁴ V/cm"), so the search style reaches
validity-domain vocabulary that the corpus does populate.

---

### S9 — the per-sample mask has no representation in the call's return type, in `applicability-classifiers.md`

**Verdict:** ABSENT

**The obligation.** The page requires swept-environment windows to be re-evaluated per
training sample and asserts the plumbing already exists:

> The per-sample mask path already exists ([pino-bridge]). Compose-time structure decisions

**What is missing.** The cited page's return type has four members and none of them is a
mask:

>        → ( residuals : Map<ResidualKey, Scalar>
>          , values    : Map<ObservableRef, Value>              -- bundled observable outputs
>          , cograds   : Optional<Map<ResidualKey, Cotangent>>  -- the kernel's gradient map
>          , cert      : CertEvidence )

`product.md`'s "refusal is absence" rule does not cover this case: it makes a refused check
absent *from the compiled kernel*, decided once at compile time, whereas a masked sample is
a check that exists in the kernel and is invalid for this call. An implementer therefore
cannot express the outcome. The three candidate encodings — omit the key from the map, emit
a sentinel value, or record it in `CertEvidence` — are behaviorally different for the
consumer, and the fourth member's own type is undefined (`CertEvidence` occurs three times
in the corpus, every one a use), so the third candidate cannot even be checked.

**Control.** Searched `grep -n "mask" journals/oracle/seams/pino-bridge.md` — the page cited
as already carrying the mask path → **1 hit**, and it is a disclaimer: "It is not a per-sample
applicability mask over a training batch, and it is not a". The single occurrence of the word
on the cited page denies being the thing cited for. Searched `grep -rn "CertEvidence"
journals/` → 3 hits, all use sites.
Control that fires: `grep -rn "RoaringCoverageMask" journals/` returns a named, serialized,
byte-level mask format, so the corpus does specify mask representations where it has them.

---

### S10 — the closed refusal-mode enum is required by contract and enumerated nowhere, in `product.md`

**Verdict:** ABSENT

**The obligation.** The product page makes refusal machine-readable and forbids prose:

> A check the oracle cannot stand behind for this instance — inapplicable, outside the

> record: a closed-enum refusal mode plus numeric witnesses

and states as a principle that "Refusal is first-class" and that "Every artifact is machine
data: keyed numbers, enum codes," and "numeric witnesses, hashes."

**What is missing.** The enum. It has no name, no members, no ordinals, and no owning page —
which also puts it outside the versioning discipline that `representation-substrate.md`
applies to "Every universe and every domain". The nearest thing the corpus carries is four
*composition-level* refusals in `cert-obligations.md` ("Unprovenanced coefficient", "Gap-slope
double count", "Learned correction without an anchor", "Polarization-convention pairing"),
each of which kills a whole composition rather than accounting for one absent key, and none of
which covers the two other causes `product.md` names — inapplicable, and outside the certified
envelope. An implementer writing the certification record has to invent the code space, and
the codes are the consumer's only channel for why a key is missing.

**Control.** Searched `grep -rn "RefusalMode" journals/` → 0 hits;
`grep -rn "refusal mode" journals/` → 1 hit, the obligation quoted. Control that fires:
`grep -rn "adjoint-cert" journals/` returns a closed four-member enum written out in full
(`Passed | Failed(witness) | NotApplicable | Relaxed(rationale)`), so the corpus does
enumerate closed status vocabularies where it has them and this search style finds them.

---

## Unit 2 — crystal identity, the composition fingerprint, and the kernel cache

### S11 — the composition fingerprint omits the request, the coupling spec and the theory context, in `compose-time-pipeline.md`

**Verdict:** ABSENT

**The obligation.** The fingerprint decides when a cached kernel may be reused — it is the
corpus's whole answer to what makes two compile requests the same request:

> **What triggers a recompile.** A composition fingerprint — a content hash of
> periodicity, decoration, and the *structural* part of the environment — keys a kernel

**What is missing.** At least four things that provably change the emitted kernel are
outside that hash, and this is not the confessed structural-versus-swept partition, which
concerns only the third member.

*The request.* The first stage's inputs begin with it —

> **Inputs.** The request — which observable bundles ([observable-bundles#the-eleven]) and

— and `product.md` says of it, "everything unrequested or inapplicable is pruned and never
becomes code". Two requests for the same crystal with different bundles therefore produce
different kernels under one fingerprint.

*The coupling spec and theory context.* `coupling-structure.md` states that the theory
frame conditions the numbers baked into the kernel:

> has already selected the symmetry group and conditioned the coefficient values,

and that the spec is a compile input:

> encoding of the same channel set. The spec travels alongside the composition

So a PBE request and an HSE06 request for diamond hash identically and the cache serves
whichever compiled first. The corpus elsewhere calls a reuse of exactly this kind — a
kernel applied outside the envelope its structure was built for — a failure whose
"symptom at the seam" is, by that page's own account, none.

*The registry and specification versions.* `product.md` puts them inside the artifact's
identity, "the registry and specification versions it was compiled against", and says "a
new registry version" produces a new file. Neither is in the fingerprint.

*Import pins.* `product.md`: "Because pinning inserts graph nodes at compose time, `Import`
is a **compiler input** — a targets file handed to the compiler". Those nodes are in the
graph and not in the key.

**Control.** Searched `grep -rn "fingerprint" journals/` → 6 hits; the only two that state
membership are the two quoted, and neither names request, spec, theory context or version.
Control that fires: `grep -rn "cache key" journals/` → 5 hits, one of which is a fully
specified key with an explicit exclusion —

> operations. The result is cached on `Address[CrystalSymmetryGroup] ×

> context: the polynomial basis is symmetry-determined and theory-independent.

— so the corpus does write cache-key membership, with reasoning about what is deliberately
left out, and this search reaches that vocabulary.

---

### S12 — nothing canonicalizes the float-valued identity descriptors before an exact hash, in `crystal-inputs.md`

**Verdict:** ABSENT

**The obligation.** The identity descriptor carries continuous data:

> `PeriodicityStructure` is the geometry of repetition: dimensionality `d ∈ {0,1,2,3}`, lattice
> vectors `{a_i}`, periodicity flags, the Bravais lattice and space group, and the cell vectors

and the substrate forbids any tolerance on identity:

> **Normative.** `Address` equality is **exact**. No tolerance, no quantization, no

**What is missing.** A canonicalization step between them. The serialization rule's only
float treatment is rule 11, which normalizes not-a-number and negative zero and nothing
else. Under exact hashing, three ordinary situations produce distinct fingerprints for one
crystal: a permuted or sign-flipped choice of lattice vectors; a rotated setting of the same
cell; and a value differing in the last bit because it came from a different DFT code's
output. Each compiles a second kernel and, worse, breaks the "One file per crystal identity."
rule the product rests on. The corpus has the vocabulary for the fix — Wyckoff positions,
Bravais lattice and space group are all in the same descriptor, and a canonical cell
reduction is the standard remedy — but no page requires one, and no page says whether the
lattice vectors or only the discrete labels enter the hash. The `make-theory-context` smart
constructor shows the corpus is alert to exactly this hazard for a *discrete* field — it
normalizes the hybrid-functional double representation "so two byte-distinct encodings of
the same physics can never produce two" addresses. There is no counterpart for the
continuous fields.

**Control.** Searched `grep -rn "Niggli" journals/` → 0 hits;
`grep -rn "reduced cell" journals/` → 0 hits; `grep -rn "standard setting" journals/` → 0
hits. Control that fires: `grep -rn "Wyckoff" journals/` → 6 hits and
`grep -rn "space group" journals/` → 4 hits, so the search reaches crystallographic-setting
vocabulary in this corpus; the absent term is the reduction, not the subject matter. Second
control: `grep -rn "canonical serialization" journals/` → 5 hits, so the serialization
discipline is reachable and simply does not cover this.

---

### S13 — the kernel cache has no store, no invalidation and no eviction, in `compose-time-pipeline.md`

**Verdict:** ABSENT

**The obligation.** The always-cheap discipline depends on the cache: compile once, call
millions of times, and `product.md` builds a workflow on top of it — "Searches over discrete
identity space produce many files — cheap under content-addressed caching, but the mental
model is 'a directory of kernels'".

**What is missing.** Everything except the key's three named members. Where the cache lives
(process memory, a directory of oracle-files, a database). What an entry contains besides
the kernel. Whether a hit is validated against anything before use. What invalidates an
entry when the formula registry, the tolerance ledger or a `schema_version` changes — the
substrate's versioning discipline covers `Address` reinterpretation but says nothing about
cached compiled artifacts. Whether entries are ever evicted, and under what bound. An
implementer can write the key (modulo S11 and S12) and cannot write the cache.

**Control.** Searched `grep -rn "evict\|invalidat" journals/` → 0 hits. Searched
`grep -rn "kernel cache" journals/` → 2 hits, both the sentences already quoted. Control that
fires: the corpus specifies its *other* cache down to the column, in `cert-obligations.md`:

>   key             TEXT  PRIMARY KEY,   -- ContentAddress over (observable, value, sigma, provenance, coverage-mask)

with a write discipline, a schema-version rule and a justification for the storage engine. So
the corpus knows how to specify a cache; the kernel cache is not one of the ones it specified.

---

## Unit 3 — the physics graph

`physics-graph.md` and `representation-substrate.md` both carry `open-questions: []`. Every
finding below is against a page that reports itself complete.

### S14 — `canonical_node_bytes` for a graph node is undefined, so `NodeId` cannot be computed, in `physics-graph.md`

**Verdict:** ABSENT

**The obligation.** The graph's whole identity discipline rests on hash-consing every node,
and the node's first field is that hash:

>   ( id   : ContentAddress    -- hash-cons identity; the typed family is

The substrate gives the recipe in terms of one undefined term:

> Address[D] = Hash(domain_separator(D), schema_version(D), canonical_node_bytes)

**What is missing.** Which of `Node`'s four fields go into `canonical_node_bytes`, and the
answer is not free — the two plausible choices break different guarantees. Include `role`,
and hash-consing fails at its stated job: `physics-graph.md` says "Pure subexpressions
appearing in several residuals — a band structure, a charge density, a force field, a
dynamical matrix — collapse to a single node referenced by every consumer", but two consumers
that need the same band structure under different roles would get two addresses and no
sharing. Exclude `role`, and two nodes that must be distinguished collide, since the page
also says "The same computation is `Internal` in one composition and an `Observable` in
another" and `OutputRole` is a three-way sum, so one node cannot be an `Observable` and a
`ResidualLeaf` at once. The related question of whether `type` participates is equally
unanswered. `canonical_node_bytes` occurs exactly once in the corpus, at the definition
above, and is never expanded for any domain.

**Control.** Searched `grep -rn "canonical_node_bytes" journals/` → 1 hit, quoted. Searched
`grep -rn "node bytes\|which fields\|participates in identity" journals/` → 0 hits for a
field list. Control that fires: `grep -rn "never participates in `ResidualKey` identity"
journals/` fires in `residual-definitions.md`, and the serialization rule's record clause
("named fields sorted lexicographically by field name") fires — so the corpus does state
identity membership where it decided it, and this search reaches that vocabulary.

---

### S15 — `Layer0Type` is declared a closed universe with dense ordinals and has no members, in `physics-graph.md`

**Verdict:** ABSENT

**The obligation.** Every node in the graph carries one:

>   , type : Layer0Type        -- the typeclass alphabet

and `representation-substrate.md` puts it in the vocabularies cluster, which fixes its
storage and its extension rule:

> `CategoryTag`, `AxisLabel`, `BundleId`, `Layer0Type` | `Universe[T]` instances with dense ordinals

**What is missing.** The carrier. `Layer0Type` occurs exactly twice in the corpus — the two
lines above — and no page enumerates it. The comment points at the typeclass alphabet, but
that page defines four *typeclasses* (`Quantity`, `Sampleable`, `HasAnalyticStructure`,
`DiscreteStructure`) and four aliases, which is not a closed set of dense-ordinal members: a
node's type is a parameterized value (`gamma-hat.md` speaks of "nodes whose `type` is the
density-matrix typeclass", and no such member exists in the alphabet), and three of the four
aliases are confessed unexpanded. An implementer cannot allocate the universe, cannot assign
ordinals, cannot serialize a node under rule 7 — which demands "a 32-bit ordinal" drawn from
"the vocabulary indexing the sum" — and therefore cannot compute any node address.

**Control.** Searched `grep -rn "Layer0Type" journals/` → 2 hits, both quoted. Control that
fires: `grep -rn "CategoryTag" journals/` — the neighboring member of the same cluster row —
returns its enumeration, "The `CategoryTag` enum is the closed set of these **19 residual
categories**", so members of that cluster *are* enumerated elsewhere and this search style
finds them.

---

### S16 — `ObservableRef` keys three public surfaces and no page defines it, in `physics-graph.md`

**Verdict:** ABSENT

**The obligation.** It is the key of the values map the consumer reads, the argument of
`Import`, a field of every residual generator, and a stored column of the reference cache:

>   observable           : ObservableRef

**What is missing.** Its definition, and any route from the graph to it. The role that is
supposed to expose an observable carries a bundle tag only:

>   | Observable(bundle : BundleId)

and `observable-bundles` has eleven members, so the role cannot distinguish the many
observables sharing a bundle. An implementer building the runtime kernel's third exit
therefore cannot derive the map's key from the node that produces the value. Nor is
`ObservableRef` in the vocabularies cluster, so it has no ordinal policy, no schema version
and no extension rule, while the reference cache stores it as text — "ObservableRef
serialization" — under a canonicalization the corpus never states.

**Control.** Searched `grep -rn "ObservableRef" journals/` → 7 hits, every one a use site
(two signatures in `pino-bridge.md`, one output type in `compose-time-pipeline.md`, two in
`residual-machinery.md`, one column comment in `cert-obligations.md`, and the request
parameter). None is a definition. Control that fires: `grep -rn "ResidualKey =" journals/`
returns the definition of the sibling key, so definitions of key types are reachable by this
search style; `ObservableRef` has none.

---

### S17 — `ResidualKey` has no field for the axis point it is required to distinguish, in `residual-definitions.md`

**Verdict:** ABSENT

**The obligation.** The granularity discipline is the oracle's central promise, and it is
per-axis-point:

> - The acoustic sum rule per Cartesian pair `(α, β)` and per shell `R`.

and the generator must emit one entry per point:

>   loss-projection      : Output → Map<ResidualKey, Scalar>
>                          -- one entry per axis tuple; the key is content-addressed

**What is missing.** A place in the key to put the point. The key is

> ResidualKey = (producer : Producer, axes : Tuple<AxisLabel>)

and `AxisLabel` is the type of an axis *name*, not an axis *value* — the generator's own
field confirms it, with its comment naming dimensions rather than points:

>   axes                 : List<AxisLabel>          -- the dimensions this generator unfolds
>                                                   --   over (k-point, frequency, atomic
>                                                   --   pair, shell, …)

So the acoustic sum
rule's leaf for `(α=x, β=y, R=shell 3)` and its leaf for `(α=z, β=z, R=shell 1)` have the same
producer and the same axis-label tuple, hence the same key, and the map that must hold both
holds one. An implementer must either widen the key with a value tuple the corpus does not
define or abandon the granularity promise. The `AxisLabel` universe is separately
un-enumerable: its only characterization ends in an ellipsis, while its cluster row demands
dense ordinals.

**Control.** Searched `grep -rn "axis tuple" journals/` → 7 hits, all requiring per-tuple
emission, none giving the key a value field. Searched
`grep -rn "AxisValue\|axis value" journals/` → 1 hit, and it is `pino-bridge.md`'s
`flat-index` comment "lexicographic over axis values" — describing a Roaring bitmap index for
`AxisCoverage`, a different object, and one that lives outside `ResidualKey`. Control that
fires: `grep -rn "ResidualKey" journals/` returns many hits including its definition and its
identity discipline, so the search reaches this type's specification thoroughly; the value
field is not in it.

---

### S18 — `InputKind` has no constructor for the two non-micro tiers, and `EnvField` is undefined, in `physics-graph.md`

**Verdict:** ABSENT

**The obligation.** Every leaf of the graph is one of exactly two things:

> InputKind = StateSlot(StateComponent) | EnvScalar(EnvField)

and `coupling-structure.md` fixes the first constructor's payload to the micro tier:
"`StateComponent` is the seven-slot alphabet".

**What is missing.** Two constructors and one type. The slow tier's `conc[D,q]` and the macro
tier's `T_L(r)` are inputs to the two cross-tier residual categories, are not state slots, and
are not environment scalars — `multiscale-state.md` says outright that "`MacroField` plays the
role `StateComponent` plays in the micro tier", which names a second universe that the sum has
no arm for. This is the graph-side face of S1 and a distinct artifact: even given a call
argument, an implementer could not construct the leaf node that reads it. Separately,
`EnvScalar`'s payload type `EnvField` occurs exactly once in the corpus — in the line above —
and the environment record it would index is confessed not closed, so the second arm has no
enumerable payload either.

**Control.** Searched `grep -rn "InputKind" journals/` → 4 hits: the constructor in
`Node`, the definition line, a glossary pointer, and the vocabularies cluster row. Searched
`grep -rn "EnvField" journals/` → 1 hit. Control that fires: `grep -rn "NodeKind =" journals/`
returns the sibling sum written out with all three arms and a paragraph defending its
closure ("Three constructs look as though they might be further node kinds, and are not"), so
the corpus does argue for the closure of its node vocabularies where it has thought it
through, and this search finds that reasoning. No such passage exists for `InputKind`.

---

### S19 — observable-selection precedence names two orders and defines neither, in `physics-graph.md`

**Verdict:** ABSENT

**The obligation.** When several formulas compute one observable, exactly one is exposed, and
the page states the rule in one line:

> ([residual-definitions#facets]): declared dressing tier first, then registration order.

**What is missing.** Both orders, and the tie-break. The dressing tiers are a four-member list
in `born-oppenheimer-levels.md` (`substrate`, `one-shot-dressing`, `iterative-dressing`,
`property-machinery`) presented as implementation scope, and no page says which end of it
wins — plausibly the most-dressed value should be exposed, but the same page insists the
dressing tag is "a **provenance label, not a loss-weighting axis**", which argues the other
way. "Registration order" appears exactly once in the corpus, at the line quoted: it is not
defined as registry row number, load order, or address order, and the three differ. Nor does
the corpus say what happens when two candidates tie on both. This is not a cosmetic gap: the
page is emphatic that "the graph never averages observables and never silently selects between
formulas at runtime", so the compose-time selection is the *only* place the choice is made,
and its rule is unwritten.

**Control.** Searched `grep -rn "registration order" journals/` → 1 hit, quoted. Searched
`grep -rn "precedence" journals/` → the same passage and no ordering definition. Control that
fires: `grep -rn "stage-visibility order" journals/` returns an ordering that the corpus
writes out in full — "symbolic lift, symmetry quotient, invariant synthesis, algebraic
simplification, lowering and adjoint synthesis, runtime kernel application" — so the corpus
does spell out its orders where it has fixed them, and this search style finds them.

---

### S20 — `CompressionPlan` is an open sum that must serialize as a closed ordinal, and its selection carries no numbers, in `physics-graph.md`

**Verdict:** ABSENT

**The obligation.** The plan is a sidecar value, so it is stored in a `PersistentMap` and
canonicalized under rule 7, which requires "discriminator drawn from the vocabulary indexing
the sum, serialized as a 32-bit ordinal". The sum is written as:

> CompressionPlan =
>   | Dense
>   | Sparse(sparsity-pattern)
>   | LowRank(rank)
>   | HODLR(params)
>   | TT(ranks)
>   | …

**What is missing.** Three separate things.

*Closure.* The trailing `| …` makes the member list open, which cannot be reconciled with the
dense-ordinal serialization the substrate requires. An implementer must decide whether the sum
is closed at five, and the answer determines whether the ordinal is stable across versions.

*Payloads.* `sparsity-pattern`, `params` and `ranks` are named and never typed;
`sparsity-pattern` occurs once in the corpus. `pino-bridge.md` then exports these to the
consumer, declaring "the `CompressionPlan` slot, its rank, and its" truncation target in the
steppable-form manifest — so they cross a public seam untyped.

*Numbers.* The selection table's conditions are qualitative: "small or dense operator" and

> | numerical rank far below the dimension, estimated by rank-revealing QR or a randomized-SVD range-finder here | `LowRank(rank)` |

which leaves both the threshold and the estimator to the implementer, and the two estimators
return different ranks on the same matrix. The error target that is supposed to pin the rank
is circular: `compose-time-pipeline.md` says

> **Each compression plan carries a per-plan error target** — the truncation tolerance

while the tolerance ledger, which declares itself canonical for "every tolerance and error
bound in the oracle library", records the value as `per plan, declared at plan selection`.
Plan selection defers to the plan; the plan defers to plan selection; no number exists.

**Control.** Searched `grep -rn "δ_plan" journals/` → 1 hit, the ledger row that defers.
Searched `grep -rn "sparsity-pattern" journals/` → 1 hit, the definition line. Searched
`grep -rn "far below" journals/` → 1 hit, the table row. Control that fires:
`grep -rn "τ_adj" journals/` returns a tolerance with a stated default (`1e-4` relative) and a
stated enforcement point, so the ledger does carry valued tolerances and this search reaches
them; `δ_plan` is the row that carries none.

---

## Coverage

**Read fully**

- `journals/oracle/state/unified-state.md`
- `journals/oracle/state/crystal-inputs.md`
- `journals/oracle/state/gamma-hat.md`
- `journals/oracle/state/multiscale-state.md`
- `journals/oracle/state/born-oppenheimer-levels.md`
- `journals/oracle/compilation/physics-graph.md`
- `journals/oracle/compilation/compose-time-pipeline.md`
- `journals/oracle/compilation/representation-substrate.md`
- `journals/oracle/laws/residual-definitions.md`
- `journals/oracle/laws/generic-dynamics.md`
- `journals/oracle/seams/pino-bridge.md`
- `journals/oracle/seams/residual-machinery.md`
- `journals/oracle/certification/applicability-classifiers.md`
- `journals/oracle/registry/typeclass-alphabet.md`
- `journals/oracle/registry/canonical-vocabularies.md`
- `journals/oracle/registry/computational-methods.md`
- `journals/n-op/purpose/product.md`

**Read partially** (targeted sections, named)

- `journals/oracle/certification/cert-obligations.md` — certificate artifact, the ten
  obligations, tolerance ledger, composition-validity refusals, reference cache.
- `journals/oracle/laws/coupling-structure.md` — channel record, `CouplingSpec`,
  `TheoryContext` placement, MVP default theory context, invariant-generator cache key.
- `journals/practice/traps.md` — anchor list in full; `units`, `lattice-transpose`,
  `swept-environment-windows`, `face-flux-discretization` sections.
- `journals/operator/seam/learnable-structure-contract.md` — the seam's state-emission
  obligation only (out of unit; read to confirm what it demands of `unified-state`).
- `journals/practice/conventions.md` — section headings only.

**Not read**

- `journals/oracle/registry/named-formulas.md`, `formula-registry.md`, `properties.md`,
  `property-templates.md`, `observable-bundles.md`, `topology-atlas.md`,
  `typed-compositions.md`
- `journals/oracle/accuracy/*`, `journals/oracle/certification/out-of-scope.md`
- `journals/n-op/build/*`, `journals/n-op/purpose/{purpose-and-scope,library-landscape,architectural-principles}.md`
- `journals/operator/*` (except the one section above), `journals/interface/boundary.md`
- `journals/practice/{agent-contract,glossary}.md` — glossary consulted by grep only, not read
- Prior audit outputs in `audit/findings/` — deliberately not read, to keep this pass
  independent of the contradiction and structure sweeps.

**Items reaching DETERMINED, not reported above** (counted, 9): the canonical serialization
rule's eleven clauses; the substrate primitive records and their backend-selection ladder;
the hot-path asymptotic table; the sidecar lifetime and stage-visibility order; the slow-state
schema's six fields with types, units and index geometry; the `MacroState` field list with
units; the density-matrix MVP byte budget and its arithmetic; the `OneShotCert` /
`IterativeResult` / `ResidualGenerator` record schemas; the three node kinds' constructor
shapes.

## Near-findings rejected

- **The state's atom count `N`.** `R_I ∈ ℝ^{3N}` never says where `N` comes from. Rejected:
  it is derivable from `SiteDecoration`, and the general shape question is the confessed
  `state-wire-schema` open question.
- **Per-slot units mix Gaussian and SI.** `E_EM[A] = (1/8π)∫(…)` is Gaussian while
  `MacroState` is SI and the slow tier is cm⁻³. Rejected: per-slot units are exactly what
  `state-wire-schema` confesses.
- **Acyclicity of the graph is asserted, not enforced.** Rejected: content-addressed
  hash-consing makes a cycle unconstructible, since a node's address depends on its children's
  addresses. The guarantee is structural and an implementer gets it for free.
- **Sidecar lifetimes are vague.** Rejected: they are not. Each sidecar's producing stage and
  consuming stage are stated, and the erasure point at codegen is explicit.
- **`Crystal` is undefined.** Rejected as a finding: confessed at `crystal-inputs.md`'s
  `crystal-type` open question. Noted here because it propagates into every signature I
  examined, including `ResidualGenerator.applicability`.
- **The `Environment` record's eight `UNSEEDED` types.** Rejected: confessed at
  `environment-schema`.
- **Method and template argument types are undefined.** Rejected: confessed at
  `computational-methods.md`'s `argument-type-alphabet-homeless`, and the three unexpanded
  aliases at `typeclass-alphabet.md`'s `three-aliases-never-expanded`.
- **Equality saturation has no cost bound.** Rejected: confessed at
  `algebraic-simplification-performance`.
- **The tape materialization schedule is "a bounded heuristic".** Rejected as
  UNDERSPECIFIED-but-adequate: the corpus states the problem is NP-complete on a general DAG,
  names the closed-form chain case, and requires the choice to be recorded. An implementer can
  pick a heuristic and ship; two implementers differ only in performance, not in emitted
  values, and the page correctly notes this lowering owes no fidelity generator.
- **`CertEvidence` has no schema.** Rejected as a standalone finding in this unit: it is the
  certification workstream's, and a separate sweep covers that page. It appears inside S9 only
  because it is the last candidate home for the per-sample mask.
- **Serialization format of the state file and the output maps for the `validate` verb.**
  Rejected: subsumed by `state-wire-schema` on the input side, and the output side is a thin
  wrapper over `Map<ResidualKey, Scalar>`, whose gap is already S17.

## By-catch

- `Validate`'s fourth return is `cert : CertEvidence` in `pino-bridge.md`, but `product.md`
  ends its list of the call's four returns with "and the content hash of the producing kernel."
  Two different fourth members.
- `BundleId` in `physics-graph.md`'s `OutputRole` versus `BundleName` in
  `residual-definitions.md`'s `ContributionFacets` and `residual-machinery.md`'s generator
  record. The vocabularies cluster lists only `BundleId`.
- `compose-time-pipeline.md` says the compile stages run "once per
  `(PeriodicityStructure, SiteDecoration, Environment)` tuple" — the whole environment — while
  the same page's recompile rule keys on "the *structural* part of the environment".
- `physics-graph.md` lists `Import` as inserting "certification-only `ResidualLeaf` nodes",
  which under `OutputRole`'s three-way sum means those nodes cannot also be `Observable`, yet
  `Import`'s target is an `ObservableRef`.
- `residual-definitions.md` numbers the equation-of-motion categories 1–7 and then says the
  category count is 9 including the two cross-tier siblings; the enumerated list stops at 7 and
  the siblings are described in prose below it, so a reader counting the numbered items gets 17.
- `multiscale-state.md`'s Péclet worked example is the only place in the corpus with a device
  cell size (~10 nm); it functions as a de facto mesh parameter while being presented as an
  illustration.
