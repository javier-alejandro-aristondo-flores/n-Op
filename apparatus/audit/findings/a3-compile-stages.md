# A3 — the five compile stages: build-sheet audit

Units 4, 5 and 6: symbolic lift, symmetry quotient, invariant synthesis, algebraic
simplification, lowering and codegen. Read at `HEAD = 476aad7`.

**Quotation convention.** Every blockquote is copied out of the live file and then
whitespace-normalized — hard line wraps joined with a single space — and markdown
emphasis markers (`**`, `*`) stripped. Nothing else is altered: backticks, em-dashes,
en-dashes, `×`, `≤`, `⟺`, `¬`, `∧`, `χ`, `ρ`, `Σ` and every other Unicode character are
as they appear on disk. This is the same normalization the brief's own example
blockquote uses.

**Counts.** ABSENT 14 · UNDERSPECIFIED 6 · DETERMINED ≈22 (listed in Coverage, not
reported individually).

---

## Unit 4 — stage 1 (symbolic lift) and stage 2 (symmetry quotient)

### C1 — the predicates that drive the entire pruning stage have no per-row data source, in `applicability-classifiers.md` and `formula-registry.md`

**Verdict:** ABSENT

**The obligation.** Stage 1's whole output — the pruned graph — is produced by
evaluating one predicate per node:

> Sidecar produced. `SymbolicLiftSidecar.applicability : Map<NodeId, Predicate>`. Each node's applicability predicate is a reduced ordered binary decision diagram, so evaluation costs one decision path. Any subgraph whose applicability is false for this crystal-and-environment pair is deleted.

and the classifier page makes carrying the predicate normative and per-row:

> Every registry entry gets an explicit `applicability` field. Always-true stubs are acceptable for V1.0 and are refined incrementally — an explicit stub is a claim a reader can find and a checker can count, which an absent field is not.

**What is missing.** The registry manifest is the declared home of per-row values:

> The manifest is the machine-readable table of named formulas: one row per formula, at [registry]. It is canonical for every per-row

and its column list does not include the field:

> One column per field of the formula record ([named-formulas#formula-record]):

The nine columns it then names are row number, `name`, `signature`, `bundle`,
`cost-tier`, `differentiability`, `anchor-class`, `provenance`, `depends-on`. The live
table matches: `head -1 data/registry-manifest.csv` returns nine fields —
`#,Name,Signature,Bundle,Tier,Diff,Path,Source,Depends on` — over 134 data rows, with no
applicability column. `grep -c "is-polar-material\|is-noncentrosymmetric"` over that file
returns 1: row 128 mentions two predicate names inside the free text of its `Source`
cell. So an implementer building stage 1 has 134 formulas and zero predicates to compile
into decision diagrams, and the "checker can count" claim has nothing to count. This is
the input to the stage, not a refinement of it.

**Control.** Searched `grep -rn "applicability" journals/oracle/registry/formula-registry.md`
→ 2 hits, both pointers to the classifier page (`depends-on` and the
field-vocabulary table), none establishing a column. Control that fires: the same page's
field list does carry `differentiability`, and `grep -o "D1\|D2\|D3" data/registry-manifest.csv`
finds that column populated per row — so the manifest does carry the coded per-row fields
it declares, and the absence of this one is not a search artifact.

---

### C2 — no applicability predicate is given a decision procedure, and the flagship one contradicts the decidability rule, in `applicability-classifiers.md`

**Verdict:** UNDERSPECIFIED

**The obligation.** The predicate must be decidable from tags alone:

> Every `applicability` predicate is first-order decidable in `(Crystal, Environment)`: finite case analysis on typeclass tags — lattice type, site decoration, presence of an environment field — and never on numeric thresholds or solver outputs.

**What is missing.** The classifier page's table of standard predicates is explicitly
"Illustrative" and gives, per row, a name and a prose gloss — never a rule over tags. For
the predicate the corpus leans hardest on, the gloss is a computed physical quantity and
the page says so:

> longitudinal-transverse optical splitting. Gates the Fröhlich and polar-optical phonon paths: the long-range static electron-phonon channels, the polar-optical-limited saturation velocity, and the relative permittivity derived through the Lyddane-Sachs-Teller relation. It is a property of the bonds, not of the point group.

Nonzero Born effective charges are a solver output; the page also rules out the one
tag-level surrogate an implementer would reach for, the point group. No rule is supplied
in its place, for this predicate or any other. Two implementers gate β-Ga₂O₃'s dominant
scattering channel differently and both can cite the page. The atom vocabulary the rule
is supposed to range over is also not located: the classifier page sends the reader to
`[typeclass-alphabet]` for it, and that page carries four typeclasses and four aliases —
no tag universe at all.

**Control.** Searched `grep -rni "typeclass tag\|typeclass-tag" journals/` → 7 hits, all
asserting decidability *over* tags, none enumerating the tags. Control that fires:
`grep -rn "Members" journals/oracle/registry/canonical-vocabularies.md` → the ten theory
vocabularies are enumerated member by member, so the corpus does enumerate closed
vocabularies where it has them.

---

### C3 — the decision diagram's variable order is made load-bearing for identity and never fixed, in `applicability-classifiers.md`

**Verdict:** UNDERSPECIFIED

**The obligation.** Reduction and canonicity of an ROBDD are properties of a *fixed*
order, and the page makes the order part of a version:

> An applicability predicate is a `MerkleDAG[PredicateOps, Atom]` root in the substrate's sense ([representation-substrate]): a reduced ordered Boolean DAG over typed parameterized atoms drawn from the typeclass-tag vocabularies ([typeclass-alphabet]). The atom order is part of the predicate-vocabulary version. Adding a new atom creates a new order id and forces explicit re-canonicalization of stored predicate roots, rather than silent reinterpretation of the roots already stored.

**What is missing.** The order itself, and the rule that produces it. Nothing states the
initial order, an ordering heuristic, or a canonical sort key over atoms. Because a
predicate's `Address` is the hash of its canonical root, two implementations that pick
different orders produce different addresses for the *same* predicate, and the
re-canonicalization machinery above has no fixed point to canonicalize toward.

**Control.** Searched `grep -rni "variable order\|variable ordering" journals/` → 0 hits;
`grep -rn "atom order" journals/` → 3 hits, all about versioning the order, none stating
one. Control that fires: the canonical serialization rule does fix orders elsewhere in
exactly this style — "named fields sorted lexicographically by field name", "sorted by
address bytes" — so the corpus states canonical orders where it has them.

---

### C4 — `CrystalSymmetryGroup` is consumed by both stages and constructed nowhere, in `coupling-structure.md`

**Verdict:** ABSENT

**The obligation.** Stage 2 rewrites against the space-group action and stage 3 takes the
group as its first argument:

> Standard representation theory. Given the crystal's symmetry group ([canonical-vocabularies#scope] lifts `CrystalSymmetryGroup` to a first-class typeclass entity, built at compose time from `PeriodicityStructure × SiteDecoration`) and a channel specification, this routine returns the finite basis of `target`-shaped symmetry-invariant terms at the requested `order` and `derivative`.

**What is missing.** The construction. That parenthetical is the only statement in the
corpus about where the group comes from, and it delegates to
`[canonical-vocabularies#scope]`, whose text is "What these vocabularies do not decide" —
a section about which certification obligations the theory vocabularies touch. It says
nothing about building a group. The glossary names `[coupling-structure]` as the owner of
the type; `coupling-structure` redirects to the anchor above. So nothing in the corpus
gives: the symmetry-detection algorithm from lattice vectors and site positions, the
position/angle tolerance that detection runs at, the group's concrete representation
(generator set, element list, coset table), the double-cover construction the theory
context is said to trigger, time-reversal augmentation, or the magnetic-group case that
`space-group : 1..230 (+ magnetic)` implies.

**Control.** Searched `grep -rn "CrystalSymmetryGroup" journals/` → 8 hits: two in the
generator's signature and cache key, three in `representation-substrate` declaring it
"sui generis" with derived caches, one glossary pointer, one theory-context remark, one
the delegation quoted above. Every one consumes it; none builds it. Searched
`grep -rni "space-group determination\|symmetry detection\|spglib\|Bilbao" journals/` → 0.
Control that fires: `grep -rn "make-theory-context\|make-coupling-channel" journals/`
finds smart constructors whose validation duties are spelled out — the corpus does
specify constructors where it has them.

---

### C5 — the Brillouin-zone mesh that the wedge collapse rewrites over is not an input and has no source, in `compose-time-pipeline.md`

**Verdict:** ABSENT

**The obligation.** One of stage 2's two rewrites is defined over a sampling of the zone:

> Irreducible-wedge orbit collapse. Nodes ranging over the full Brillouin zone are rewritten to range over the irreducible wedge with integer orbit weights. In cubic systems this is up to 48× fewer sample points.

**What is missing.** The mesh. `PeriodicityStructure` is "the geometry of repetition:
dimensionality `d ∈ {0,1,2,3}`, lattice vectors `{a_i}`, periodicity flags, the Bravais
lattice and space group, and the cell vectors `h`" — no mesh. `SiteDecoration` and
`Environment` carry none either, so the mesh is not a field of any of the three compile
inputs, and no stage is said to choose one. The one place a composition writes it down
leaves it as free parameters nobody binds:

> BandStructure = SpectrumOf(Ĥ_KS[γ̂], domain = BZMesh(nx, ny, nz))

Also absent: the wedge-construction procedure (which of the 230 groups' asymmetric units,
under which convention), and how the integer orbit weights are computed and attached —
the "48×" is a fact about cubic multiplicity, not a procedure. Every k-indexed residual
axis and every operator dimension at stage 5 inherits this.

**Control.** Searched `grep -rn "nx" journals/` → 1 hit, the unbound parameter above;
`grep -rn "BZMesh" journals/` → 2 hits, that line and one bare use as a domain type;
`grep -rni "Monkhorst" journals/` → 1 hit, `gamma-hat`'s MVP *sizing* prose ("an 8×8×8
Monkhorst–Pack mesh gives ~29 irreducible k-points"), which is a memory-budget
illustration, not an input binding. Control that fires: `grep -rn "PeriodicityStructure"
journals/` → 10 hits including its full field list, so the search reaches the input
records and the mesh is genuinely not among their fields. **Not** the declared open
question `mesh-uncertainty-floor-undeclared`: that one asks for a numeric
*mesh-uncertainty floor* for transport observables and presupposes a mesh exists; this is
the absence of any mesh-valued input at all.

---

### C6 — operator block-diagonalization has no irrep interface, no basis convention, and no commutation test, in `compose-time-pipeline.md`

**Verdict:** UNDERSPECIFIED

**The obligation.**

> Operator block-diagonalization. Every operator that commutes with the space-group action is rewritten into its irreducible-representation decomposition. Schur's lemma collapses a dense `MethodInvoke(eigendecomposition, …)` node into per-irrep blocks, turning one cubic-in-dimension dense eigensolve into a sum of much smaller ones.

**What is missing.** Three things an implementer must type. (i) The test. "Every operator
that commutes with the space-group action" is a predicate over a symbolic node at compile
time — before any numerics, since the stage is "purely symbolic — no numerics run here" —
and no rule is given for deciding it from a `MethodInvoke`'s method and arguments.
(ii) The interface to the tables. `forced-decisions` does designate an offline
group-theory engine that "Generates and validates character tables and projectors for the
finite groups the symmetry quotient needs; results are baked in", so the *source* is
designated — but not the form the baked-in result takes, what it is keyed on, or which
irrep-basis convention it fixes (real versus complex irreps, phase convention, ordering
within a degenerate block). Since the rewritten node is hash-consed and addressed by
exact bytes, two admissible conventions give two addresses for one physics. (iii) The
sidecar's value type: `SymmetrySidecar.symmetry : Map<NodeId, IrrepBlock>` and `IrrepBlock`
is declared nowhere.

**Control.** Searched `grep -rn "IrrepBlock" journals/` → 2 hits, the sidecar declaration
in `compose-time-pipeline.md` and its restatement in `physics-graph.md`; both are use
sites. `grep -rn "IrrepLabel" journals/` → 2 hits, a glossary pointer and a listing among
`Universe` instances with dense ordinals — no members. Control that fires:
`grep -rn "CompressionPlan" journals/` → 8 hits *including* the variant list in
`physics-graph.md`, so a sidecar value type declared in this corpus does normally get its
constructors written down.

---

### C7 — three of the five topology-atlas fields have no computation and no data source, in `topology-atlas.md`

**Verdict:** ABSENT

**The obligation.** The atlas is claimed to run for every composition, at compile time:

> At compose time the atlas computes, for each composition:

and the entry it computes carries `space-group`, `AZ-class`, `X_BS`, `EBRs` and
`compatibility`. The cheap tier is claimed unconditional:

> The cheap parts run at compose time for every composition: the symmetry-indicator class, the orbit-representation decomposition, the compatibility check, and boundary-mode multiplicity by indicator lookup. All four are lookups or integer linear algebra over the entry above.

**What is missing.** The lookups have no table and the linear algebra has no matrix.
`EBRs` and `compatibility` are each named once, in the record, and never derived,
sourced, versioned, or given a format — yet obligation 7's cost model
(`Elementary-band-representation table lookup plus multiplicity enumeration`) assumes a
table on disk. `AZ-class` is likewise named once and never determined; nothing says how
the ten-element label is read off a composition. And the one field with a stated method
still lacks its input:

> `X_BS` is computed in polynomial time, by Smith Normal Form on the integer matrix of orbit-induced representations.

The construction of that integer matrix — from which orbits, in which irrep basis, with
which row/column convention — is not given, so the Smith Normal Form has no argument.

**Control.** Searched `grep -rn "EBR" journals/` (case-sensitive) → 1 hit, the record
field. Case-insensitive search returns 98 and is an instrument bug: `-i "EBR"` matches
the substring in "algebra". `grep -rn "compatibility relation" journals/` → 1 hit;
`grep -rn "AZ-class" journals/` → 1 hit; `grep -rni "Bilbao\|crystallographic server\|topological quantum chemistry" journals/ data/` → 0. Control that fires:
`grep -rn "Smith Normal Form" journals/` → 2 hits, so the search reaches this page's
vocabulary; and `data/reference-data/*.csv` rows all carry `Source` and `Version` columns
while `PseudoDojo v0.4.1` is version-pinned in prose — the corpus does pin external tables
where it depends on them.

---

## Unit 5 — stage 3 (invariant synthesis) and stage 4 (algebraic simplification)

### C8 — no state component has a declared transformation law, so the character that decides emptiness cannot be formed, in `coupling-structure.md`

**Verdict:** ABSENT

**The obligation.** The generator's cost model and its emptiness test are both stated in
terms of the representation carried by the channel's tensor product `T`:

> Emptiness of `poly` is decided by the character inner product `⟨χ_T, χ_trivial⟩_G = (1/|G|) Σ_g χ_T(g)` — a single trace per group element, never forming `ρ(g)` explicitly.

and the projector that runs when the basis is non-empty is

> the full Reynolds projection `P = (1/|G|) Σ_g ρ(g)`, run only when the basis is non-empty, is `O(|G|·dim(T)²) ≤ ~12M` operations.

**What is missing.** `T` is the ordered tensor product of the channel's `pieces`, each a
`(StateComponent, SubDofTag)` pair. Nothing in the corpus states how any state component
transforms under a crystal symmetry operation — not the cell vectors `h`, not ion
positions `R`, not momenta `P`, not the vector potential `A`, not the density matrix `γ̂`,
and not any sub-degree-of-freedom label. Without a representation per component there is
no `ρ(g)`, no `χ_T(g)`, no trace to take, and no way to check the asserted `dim(T) ≤ ~250`.
This is upstream of the declared open question `sub-dof-pair-table`: that one asks which
`(component, sub-dof)` pairs are *legal*; this is the absence of a transformation law for
even the legal ones. Also missing: how `derivative : Ultralocal | Gradient(Nat)` enters
`T` — a gradient depth adds vector factors under the point group, and the rule that turns
`Gradient(n)` into representation factors is not stated.

**Control.** Searched `grep -rn "transforms as\|transforms under\|transformation law\|acts on" journals/`
→ 0 hits. Control that fires: `grep -rn "Reynolds" journals/` → 5 hits and
`grep -rni "irrep" journals/` → 17 hits, so the corpus's representation-theory vocabulary
is reachable by this style of search; the transformation laws are simply not in it.

---

### C9 — the projector's image is never turned into a basis, and identity depends on which basis is chosen, in `coupling-structure.md`

**Verdict:** UNDERSPECIFIED

**The obligation.** The generator's one substantive line is a call whose result is a list
of symbolic tensor expressions:

> else: poly = trivial_irrep_projector(G, c.pieces, c.target, c.order, c.derivative)

and each element carries a symbolic form and a content address, with the whole output
addressed and cached:

> The result is cached on `Address[CrystalSymmetryGroup] × Address[CouplingChannel]` ([representation-substrate#serialization]), so

**What is missing.** The step from a projector to a basis. `P` is a linear idempotent;
its image is a subspace, and extracting a *list* of basis vectors requires a stated
choice — orthogonalization scheme, pivot order, normalization, and the ordering of the
returned list. Nothing states one. Since `Address` equality is exact over canonical bytes
by construction, two implementations that pick different (individually correct) bases
produce different `generator-hash` and `output_hash` values for identical physics, and the
cache-collapse claim rests on a canonicalization the corpus never fixes. Missing with it:
the map from a numeric projector to `symbolic-form : SymbolicTensor` — the generator's
declared output is a symbolic tensor DAG, and no rule converts projector columns into one
— and `IrrepCoefficientTable`, the type of `InvariantTerm.irrep-coefficients`, which is
named once and defined nowhere. The `AntisymmForm` / `PSDSymmForm` target projections are
stated as obligations ("`AntisymmForm` invariants are projected onto the antisymmetric
component", "onto the positive-semidefinite cone") without the projection formula or
whether they are applied before or after the Reynolds average.

**Control.** Searched `grep -rn "IrrepCoefficientTable" journals/` → 1 hit, the field
declaration itself. Searched `grep -rni "orthogonalis\|orthogonaliz\|Gram-Schmidt\|row echelon\|canonical basis" journals/` → 0 hits. Control that fires:
`grep -rn "canonical serialization rule\|canonicalized" journals/` → the substrate spells
out an eleven-clause canonicalization for bytes, so the corpus does specify
canonicalization where it has decided one; for the invariant basis it has not.

---

### C10 — equality saturation is named without a rule set, a termination rule, or any extraction procedure, in `compose-time-pipeline.md`

**Verdict:** ABSENT

**The obligation.** The stage's mechanism is committed:

> Action. Three rewrites, all exact and adjoint-safe, implemented as equality saturation over an e-graph — union-find over equivalence classes plus e-matching:

**What is missing.** All three of the things that make an equality-saturation pass a
program. (i) The rewrite rules: the three bullets are *effects* — hash-consing,
cross-formula subexpression elimination, tearing and alias elimination — and the first two
are congruence closure rather than rules at all; no e-matching pattern, left-hand side or
right-hand side is written anywhere. (ii) The termination rule: no iteration cap, node
cap, or saturation criterion. (iii) **Extraction** — the procedure that picks one term out
of the saturated e-graph, and the cost function it minimizes. Extraction is what decides
which program is emitted, and it is not mentioned anywhere in the corpus. The declared
open question `algebraic-simplification-performance` is a *budget* statement — "no bound
on saturation time or e-graph size is committed anywhere" — and the page's own line, "This
is the algorithmically hardest pass to build, and its cost is the one open-ended figure in
the compose-time budget", is also about cost. Extraction is not a cost question: without
it there is no output, however long you let the saturation run.

**Control.** Searched `grep -rni "extraction" journals/` → 13 hits, every one either a
GENERIC regime extraction in `generic-dynamics`/`build-verification` or `pino-bridge`'s
"one extraction, two lowerings" about the tangent map; none is an e-graph term extraction.
Searched `grep -rni "rewrite rule" journals/` → 0; `grep -rni "cost function" journals/` →
0. Control that fires: `grep -rn "e-matching" journals/` → 1 hit and
`grep -rni "e-class" journals/` → 7 hits, so e-graph vocabulary is present in the corpus
and reachable by this search style.

---

### C11 — admission condition 2 requires an e-class analysis over tensor-algebra operations that is never defined, in `compose-time-pipeline.md`

**Verdict:** ABSENT

**The obligation.** Condition 2 of the rewrite-admission rule is normative and names the
mechanism:

> 2. every condition under which it fails in floating point is expressed as a side condition discharged by an e-class analysis — an interval fact, a not-equals fact — and not as a caveat in prose; and

**What is missing.** The analysis. An e-class analysis is a semilattice with a per-operator
transfer function and a join, and none of the three is given: no domain (interval of what
— each tensor entry, a norm, a spectral bound?), no join rule, no transfer function for
any operator. The op signature this DAG actually uses is not scalar arithmetic; it is
`SymbolicTensorOps`, "a colored operad ... generated by the target shapes of
[coupling-structure#target-shapes] — scalar, antisymmetric form, positive-semidefinite
symmetric form — plus tensor product, contraction, derivative, group action, projection
and binding". Interval and not-equals analyses over contraction, derivative and group
action are not standard objects, and the corpus imports the result wholesale from a
scalar-float rewriting setting without stating the lifting. Condition 3's obligation
inherits the hole: the fidelity generator owes "the rewrite's declared float discrepancy
on the sampled points", and nothing says how a *rewrite* — a graph transformation with no
domain of its own — gets sampled.

**Control.** Searched `grep -rni "interval" journals/` → 11 hits: three restatements of
the same architectural claim in `compose-time-pipeline`, two in `representation-substrate`
(one of them the rejected "ball or interval addressing" alternative), one in `gamma-hat`,
one in `traps`, and four unrelated physics uses ("unit interval", "across the interval").
No hit defines a lattice, a join or a transfer function. Control that fires:
`grep -rn "combineTol" journals/` → the corpus does specify a composition law for its other
analysis-like quantity, including associativity, commutativity and monotonicity.

---

### C12 — tearing, alias elimination and sparsity inference are names with no algorithm, and stage 5 consumes their output, in `compose-time-pipeline.md`

**Verdict:** ABSENT

**The obligation.** The third rewrite is asserted, and its output is a declared input to
the next stage:

> Tearing and alias elimination. Algebraic dependencies are resolved at compose time, and sparsity patterns are inferred for the next stage.

Stage 5's plan table then consumes it: `known or inferred sparsity pattern, from the
preceding stage's inference` selects `Sparse(pattern)`.

**What is missing.** What an "algebraic dependency" is in a graph whose edges are already
explicit argument lists; what is torn and how tear variables are selected; what relation
"alias" names and how two nodes are found to be aliases; the sparsity-inference algorithm
and what it runs over, given that the stage is purely symbolic and no numerics have run;
and the representation of `sparsity-pattern`, which is the payload of the `Sparse` plan
constructor and is declared nowhere. An implementer cannot produce the object stage 5
pattern-matches on.

**Control.** Searched `grep -rni "tearing\|alias" journals/` → 3 hits, all restatements of
the bullet above (`compose-time-pipeline` and the pass list in `physics-graph`), none
algorithmic. Searched `grep -rn "sparsity-pattern\|sparsity pattern" journals/` → 4 hits,
all naming it as a plan payload or as this stage's output. Control that fires:
`grep -rn "Roaring" journals/` → the corpus does specify a concrete wire format for its
other sparse structure, down to "serialized Roaring bitmap" and a lexicographic flat index.

---

### C13 — `kernel_tag_matches_range` is a guard with no mapping, and one declared channel has no admissible tag, in `coupling-structure.md`

**Verdict:** ABSENT

**The obligation.** The generator's third integrity guard rejects a channel on a
tag-to-range mismatch:

> if ¬polynomial_sufficient(c) ∧ ¬kernel_tag_matches_range(c): error "kernel tag ≠ mechanism_range"

and `make-coupling-channel` enforces the same pairing at registration:

> with the well-formedness invariant enforced by `make-coupling-channel`: `polynomial_sufficient(c) ⟺ (c.kernel_extension = None)`, and a non-sufficient channel's `kernel_extension.tag` must match its `mechanism_range`.

**What is missing.** The map. `KernelExt.tag` ranges over four values —
`FroehlichLongRange | ScreenedCoulombRPA | GWQuasiparticleSelfEnergy | TDDFTXCKernel` —
and `MechanismRange` over `ShortRange | LongRangeStatic(pole_order) | LongRangeDynamical`.
No page states which tags match which ranges, so the predicate cannot be written. The
coverage table makes the consequence concrete rather than hypothetical: it declares
`electron-phonon (piezoelectric acoustic, long-range)` as `LongRangeStatic(1)` with
`polynomial_sufficient` false, so that channel *must* carry a `kernel_extension` — and no
tag in the four-member vocabulary names it.

> The piezoelectric-acoustic channel is `LongRangeStatic(1)` with a `1/q` pole: the second long-range electron-phonon mechanism the wurtzite III-nitride members carry, alongside Fröhlich's `1/q²`. It is gated on `is-noncentrosymmetric` ([applicability-classifiers#polar-predicate-split]) — piezoelectric scattering needs a piezoelectric class — and is inert for diamond.

Under any reading of the missing map, `make-coupling-channel` refuses a channel the
coverage policy declares live for the III-nitride members.

**Control.** Searched `grep -rn "kernel_tag_matches_range" journals/` → 1 hit, the guard
line itself. Searched `grep -rni "piezoelectric" journals/oracle/laws/coupling-structure.md`
→ hits in the coverage-policy paragraph and the channel table, none in the `KernelExt`
record. Control that fires: the sibling derived predicate *is* given in full —
`polynomial_sufficient(c)` is written as a four-arm match over `MechanismRange` — so this
page does write out its total functions where it has decided them.

---

## Unit 6 — stage 5: lowering, compression, adjoint synthesis, codegen

### C14 — the per-plan error target has no value and no selection rule, in `compose-time-pipeline.md`

**Verdict:** ABSENT

**The obligation.**

> Each compression plan carries a per-plan error target — the truncation tolerance for the low-rank, hierarchical and tensor-train ranks — and the rank is chosen to meet that target, not by structure alone. The target enters the per-residual error budget through `Quantity.combineTol` ([residual-definitions#error-budget]).

**What is missing.** The target's value, and the procedure that sets it. The tolerance
ledger registers the name and then defers: `δ_plan` is described as the
"per-compression-plan truncation error target ([compose-time-pipeline]); the sum over
active plans is the compression term in `combineTol`", and its Default column reads "per
plan, declared at plan selection" — declared by whom, from what, is nowhere. Nor is the
rank-search itself: given a target, no page says how the rank is raised or lowered to meet
it, or what happens when no rank within the memory budget does.

**Control.** Searched `grep -rn "error target" journals/` → 5 hits: the obligation above,
the ledger row, an `accuracy-ledger` restatement, and two `traps` entries warning that a
declared target is not a measurement. None values it. Control that fires: every other row
of the same ledger table carries a number — `δ_sym` `1e-6`, `δ_PSD` `1e-9`, `τ_adj`
`1e-4`, `τ_cond` `1e-8`, `τ_interp` `1e-10` — so the table's Default column is populated
where a value has been decided.

---

### C15 — the compression-plan decision procedure has no thresholds, no precedence, and no way to identify the nodes it applies to, in `compose-time-pipeline.md`

**Verdict:** UNDERSPECIFIED

**The obligation.** The stage assigns a plan per node from a five-row table whose
left-hand column is the structure found: `small or dense operator` → `Dense`;
`numerical rank far below the dimension, estimated by rank-revealing QR or a
randomized-SVD range-finder here` → `LowRank(rank)`; `hierarchically low-rank off-diagonal
blocks` → `HODLR(params)`; `high-dimensional tensor operator, such as a collision
operator` → `TT(ranks)`, `cores built once by sequential tensor-train cross`.

**What is missing.** Every threshold: how small is "small", how far below is "far below",
what makes off-diagonal blocks "hierarchically" low-rank, what dimension counts as
"high-dimensional". The row precedence when a node matches several. The `params` of
`HODLR` — no leaf size, no admissibility condition, no tree. The rank vector of `TT` and
the stopping rule of the cross approximation. And, upstream of all of it, the selector:

> Compression-plan selection. Each operator-typed node is assigned a `CompressionPlan` ([physics-graph#sidecars]). The decision procedure, per node:

`operator-typed` is used twice in the corpus and defined neither time. A node's `type` is
a `Layer0Type` drawn from the typeclass alphabet, and that alphabet's members are
`Quantity`, `Sampleable`, `HasAnalyticStructure`, `DiscreteStructure` plus the aliases
`Scalar`, `Tensor`, `FieldOnGrid`, `Response` — none of which is `Operator`. The predicate
that decides which nodes enter this stage at all cannot be evaluated.

**Control.** Searched `grep -rn "operator-typed" journals/` → 2 hits, both use sites.
Searched `grep -rn "Layer0Type" journals/` → 2 hits, a field comment and a listing among
`Universe` instances — no member list. Control that fires:
`grep -rn "density-matrix-typed" journals/` → `gamma-hat` does name a node class this way
*and* gives its encoding product `Basis × Form` with both member lists, so the corpus does
enumerate node-type vocabularies where it has them.

---

### C16 — slot applicability is delegated in a circle and no slot predicate is ever stated, in `compose-time-pipeline.md` and `gamma-hat.md`

**Verdict:** ABSENT

**The obligation.** The pipeline makes slot applicability a compile-time predicate and
points elsewhere for its content:

> Whether a plan applies at all is decided here too, and by the same mechanism. Slot applicability is a compile-time predicate over `(PeriodicityStructure, SiteDecoration)`, evaluated at this stage alongside every other lowering choice. It is never a runtime check — that would be structural branching on the hot path, and its cost is what made the question look hard. Which predicate governs a given encoding slot is the encoding vocabulary's ([gamma-hat#encoding-vocabulary]).

**What is missing.** The encoding vocabulary does not carry them; it points back:

> Lowering selects one slot per density-matrix-typed node from the `(PeriodicityStructure, SiteDecoration)` pair ([crystal-inputs#top-level-inputs]). Transcoders convert on demand for operations whose runtime cost is lower in a different encoding. Rank governs one of these slots, and it is decided once. Whether `(NaturalOrbital, LowRank)` applies is one of the compile-time slot predicates ([compose-time-pipeline#lowering-and-adjoint-synthesis]); what this one tests is the substrate's rank.

That is the entire content: one of the five slots is said to test the substrate's rank, as
quoted above, with no threshold and no rank estimator named for a compile-time test that
must run before any numerics. The other four first-class pairs — `(Reciprocal, BlockDiag)`, `(Real,
Sparse)`, `(Wannier, Sparse)`, `(SymmetryAdapted, BlockDiag)` — get a "For" gloss
("periodic substrates", "defects, surfaces, amorphous regions") and no predicate at all.
The transcoders are named and their triggering rule ("operations whose runtime cost is
lower in a different encoding") has no cost model behind it.

**Control.** Searched `grep -rn "slot predicate" journals/` → 1 hit, the `gamma-hat` line
above. Searched `grep -rni "slot applicability" journals/` → 1 hit, the pipeline paragraph
above. The two point at each other and neither states a predicate. Control that fires:
`grep -rn "is-noncentrosymmetric" journals/` → the corpus does name predicates and their
gated targets where it has decided them.

---

### C17 — the adjoint-tape schedule is an unnamed heuristic with no bound and no tape, in `compose-time-pipeline.md`

**Verdict:** ABSENT

**The obligation.**

> Adjoint-tape materialization schedule. Reverse mode needs forward values, and each one is either stored or recomputed. Choosing per node is the classic rematerialization-versus-storage trade-off, and it is decided here, at compile time, from the graph's shape — never by a runtime heuristic, which would be structural branching on the hot path. On a chain the optimal schedule is known in closed form (`revolve`; Griewank & Walther, ACM TOMS 26(1) 19–45, 2000). On a general directed acyclic graph the problem is NP-complete (Naumann, J. Discrete Algorithms 7(4) 402–410, 2009 — a separate result from `revolve`). The plan is therefore a bounded heuristic over the tape, with its choice recorded.

**What is missing.** The heuristic. The paragraph establishes that one is needed and names
neither it nor its family. "Bounded" is not given a bound: no memory budget, no slot
count, no cost model that the store-versus-recompute choice is scored against — and
`revolve` is parameterized precisely by a checkpoint count that nothing here supplies.
"With its choice recorded" has no record format. The object being scheduled is also
undeclared: the sidecar is `LoweringSidecar.materialization : Map<TapeNodeId, Store |
Recompute>` and neither the tape nor `TapeNodeId` is defined anywhere — the physics graph
has `NodeId`, and no rule maps graph nodes to tape nodes.

**Control.** Searched `grep -rni "rematerial\|tape\|revolve\|checkpoint" journals/` → 10
hits: the paragraph above, the two sidecar declarations, the `build-verification`
exemption note, the pipeline `owns:` entry, and three unrelated operator-library uses
("framework tensors with attached tapes", "how checkpoints are stored"). None names a
heuristic or a bound. Control that fires: the same stage's *other* undecided-looking
choice is decided in full — `τ_L3L4` fixes the same-pass fixed point at "at most 5
iterations" — so the corpus does commit numeric caps where it has chosen them.

---

### C18 — the composition's adjoint has no synthesis rule, no solver, and no nesting composition, in `compose-time-pipeline.md`

**Verdict:** ABSENT

**The obligation.**

> Adjoint synthesis. For every `MethodInvoke` whose named method has fixed-point semantics, the implicit-differentiation adjoint is synthesized. Gradient cost becomes one extra linear system, independent of the forward iteration count

and the two-level case is made mandatory:

> Nesting constrains the order. A force evaluation on the Born–Oppenheimer surface contains a converged quantum-electronic-substrate inner solve ([born-oppenheimer-levels#hierarchy]), so the adjoint has to thread the implicit-differentiation chain through both levels, not only the outer one.

**What is missing.** Four typed things. (i) The trigger set: which of the twelve
computational methods carry fixed-point semantics is never listed. `physics-graph` says
"The fixed-point property is a fact about the named method, looked up when adjoints are
synthesized" — no page carries the lookup. (ii) The synthesis itself: the linear system
`(I − ∂F/∂x)ᵀ λ = ...` is nowhere written, so which Jacobian transpose, assembled or
matrix-free, is a choice. (iii) The solver and its tolerance: the sidecar value type is
`LoweringSidecar.adjoint : Map<FixedPointNodeId, AdjointSolver>`, and `AdjointSolver`
appears exactly once in the corpus — in that declaration — with no variants and no
stopping rule. `τ_cond` and `τ_trunc` govern the *registration* gate and the truncation
estimate, not this solve. (iv) The nesting composition: no rule for chaining an inner
adjoint into an outer one, no ordering, no statement of what the inner solve's converged
state contributes to the outer Jacobian.

**Control.** Searched `grep -rn "AdjointSolver" journals/` → 1 hit; `grep -rn "fixed-point semantics" journals/` → 3 hits, all asserting the property exists and is looked up, none
listing which methods have it. Control that fires:
`grep -rn "differentiability" journals/` → the corpus does carry a six-value
differentiability vocabulary per *formula row*, with `named-formulas` declared canonical —
so the per-method fact is missing, not merely hard to find.

---

### C19 — two of the four typed exits have undeclared element types, in `compose-time-pipeline.md`

**Verdict:** ABSENT

**The obligation.**

> Codegen. The whole graph is lowered to a compiled kernel with one entry point — the `Input` slots — and four typed exits: a residual map keyed by `ResidualKey`, a gradient map on the same keys, an observable map, and the certification evidence produced by the obligation traversals ([cert-obligations#the-ten-obligations]).

**What is missing.** The element types. The gradient exit is
`Map<ResidualKey, Cotangent>` and `Cotangent` is declared nowhere — three uses
(`compose-time-pipeline`, `pino-bridge`, `residual-definitions`), all as a map value, no
definition, no shape, no dtype, no index order, and no statement of what it is a cotangent
*of* (the state seven-tuple? a slot? a flattened vector?). `CertEvidence`, the fourth
exit, is likewise named at every use site and never given a payload. This is not covered
by the declared open question `three-aliases-never-expanded`, which names exactly
`Scalar`, `Tensor` and `FieldOnGrid`. The entry point inherits the same gap from the state
side: `unified-state` states in-page that the wire schema — "per-slot dtype, unit, index
order and memory layout" — is not specified, so the one entry point has no layout either.

**Control.** Searched `grep -rn "Cotangent" journals/` → 3 hits, all map-value use sites;
`grep -rn "CertEvidence" journals/` → use sites only. Control that fires:
`grep -rn "Response is" journals/oracle/registry/typeclass-alphabet.md` → the fourth alias
*is* expanded ("`Response` is `Sampleable + Integrable + Differentiable +
HasAnalyticStructure(KramersKronig)` over a frequency domain"), so the corpus does expand
its exit types where it has decided them.

---

### C20 — the registration gate's sample set is undefined, and the rewrite fidelity generator is defined in terms of it, in `residual-machinery.md`

**Verdict:** UNDERSPECIFIED

**The obligation.**

> Hard. `adjoint` and `fixpoint-adjoint` entries run a vector-Jacobian-versus-Jacobian-vector check on `N ≈ 64` sampled points at registration time. If the maximum relative error exceeds `τ_adj`, default `1e-4`, the build fails loud.

**What is missing.** Where the 64 points come from. No distribution, no domain, no seed,
no reproducibility rule — and the gate is a build-failing check, so two implementations
disagree about whether the build passes. The page itself shows the choice is
load-bearing: it warns that a piecewise-constant row "passes this gate spuriously" and
instructs the reader to "check that the sampled points straddle a region where the output
actually varies", which is a property *of the sample set* that nothing constructs. The
rewrite-admission fidelity generator then inherits the gap by reference — its estimator is
"the rewrite's declared float discrepancy on the sampled points", cost "shares the adjoint
gate's sample set" — and a rewrite is a graph transformation with no formula domain to
sample.

**Control.** Searched `grep -rni "sampled point\|sample set" journals/` → 6 hits, all
consuming the notion; `grep -rni "sampling distribution" journals/` → 0. Control that
fires: `grep -rn "sampling-policy" journals/` → the corpus does specify a sampling
vocabulary elsewhere (`UniformBatch | RAD(τ) | Importance | ValidationOnly`) for the
training path — so it names sampling policies where it has decided them.

---

## Coverage

Read fully:

- `journals/oracle/compilation/compose-time-pipeline.md`
- `journals/oracle/compilation/physics-graph.md`
- `journals/oracle/compilation/representation-substrate.md`
- `journals/oracle/registry/topology-atlas.md`
- `journals/oracle/registry/property-templates.md`
- `journals/oracle/registry/computational-methods.md`
- `journals/oracle/registry/canonical-vocabularies.md`
- `journals/oracle/registry/typeclass-alphabet.md`
- `journals/oracle/certification/applicability-classifiers.md`
- `journals/oracle/laws/coupling-structure.md`
- `journals/oracle/state/gamma-hat.md`
- `journals/oracle/state/crystal-inputs.md`
- `journals/oracle/seams/residual-machinery.md`
- `journals/oracle/seams/pino-bridge.md`
- `journals/n-op/build/forced-decisions.md`

Read partially (targeted sections plus full-corpus grep):

- `journals/n-op/purpose/product.md` — deployment shape, oracle-file contents, call, CLI
- `journals/oracle/certification/cert-obligations.md` — tolerance ledger, obligations 7 and 10, refusals
- `journals/oracle/state/born-oppenheimer-levels.md` — hierarchy, dressing tiers
- `journals/oracle/state/unified-state.md` — slots, wire schema
- `journals/oracle/registry/named-formulas.md` — formula record, diff tags, applicability decidability, row bands
- `journals/oracle/registry/formula-registry.md` — manifest fields, provenance vocabulary
- `journals/oracle/registry/typed-compositions.md` — electronic block, frontmatter
- `journals/oracle/accuracy/accuracy-ledger.md` — compression/budget region, mesh convergence row
- `journals/n-op/build/build-verification.md` — gate 1, fidelity pairing, tape exemption
- `journals/practice/glossary.md` — ownership table
- `data/registry-manifest.csv` — header and column population
- `generated/corpus.json` — open-question index only

Not read: `journals/operator/**`, `journals/interface/**`, `journals/n-op/build/{build-sequence,capability-slices,mvp-system}.md`,
`journals/n-op/purpose/{purpose-and-scope,library-landscape,architectural-principles}.md`,
`journals/oracle/laws/{generic-dynamics,residual-definitions}.md`,
`journals/oracle/state/multiscale-state.md`, `journals/oracle/registry/{properties,observable-bundles}.md`,
`journals/oracle/accuracy/reference-battery.md`, `journals/oracle/certification/out-of-scope.md`,
`journals/practice/{traps,conventions,agent-contract}.md`, `data/**` beyond the manifest header.
All of these were reached by full-corpus grep for every term this audit turned on, so
absence claims cover them; only their prose was not read end to end.

**DETERMINED, counted not reported (≈22).** Stage list and the compose/runtime split with
each stage's side; symbolic-lift construction order (Born–Oppenheimer level order,
substrate first); the sidecar schema — names, key types, producing stage, stage-visibility
order, erasure at last consumer; the `Node` schema, three node kinds and three output
roles; the arena representation and the no-edge-table rule; `Address` computation and the
eleven-clause canonical serialization rule; the `polynomial_sufficient` derivation as a
total four-arm match on `MechanismRange`; the three well-formedness guards in
`generate-invariants` with their exact error conditions; the spinor-parity pre-prune's
condition and result; the generator's cache key and the exclusion of `theory_context` from
it; the record field lists for `CouplingChannel`, `StatePiece`, `InvariantTerm`,
`GeneratorOutput`, `KernelExt`, `GaugeRule`, `CoverageBound`, `CouplingSpec`,
`TheoryContext`, `ResidualGenerator`, `OneShotCert`, `IterationSnapshot`,
`IterativeResult`; the rewrite-admission rule as an admission *policy* (its three
conditions, and the offline-oracle boundary); invariant composition — direct sum per
target, kernel extension as one more summand, monotone order truncation, no
channel-correlation primitive; the MVP `CoverageBound` `(4, Gradient(1))` and
prune-before-character ordering; the 15-row channel template table with per-row
`mechanism_range` and `polynomial_sufficient`; the PSD closure argument, its three
assumptions with references, the runtime guard `λ_min ≥ −δ_PSD` on the assembled
per-mechanism super-block, and the dormant semidefinite fallback; the `CompressionPlan`
variant list; the fidelity-generator pairing obligation and the tape schedule's principled
exemption from it; the runtime `evaluate` signature and its four exit keys; the recompile
trigger (composition fingerprint over structural environment fields); the hot-path
asymptotics table with constant factors; the MVP density-matrix encoding and its 18 MB
versus 460 MB budget.

## Near-findings rejected

- **The argument types in the template and method signatures** (`Extractor`, `Aggregator`,
  `ResponseKernel`, …). Real and blocking for stage 1's template expansion, but declared:
  open question `argument-type-alphabet-homeless`. Note in passing that the declared list
  is narrower than the actual set — `Operator`, `Basis`, `Functional`, `StatePoint`,
  `Distribution`, `CollisionKernel` are used the same way and are not in it — but the
  class is self-reported, so I did not raise it.
- **`Scalar`, `Tensor`, `FieldOnGrid` never expanded.** Declared:
  `three-aliases-never-expanded`. `Cotangent` and `CertEvidence` are *not* in that list,
  which is why C19 stands.
- **The state wire schema** (per-slot dtype, unit, index order, layout). Blocks the codegen
  entry point, but `unified-state` states it in-page and it is the declared open question
  `state-wire-schema`. Cited inside C19 as context, not raised as a finding.
- **`Crystal` undefined.** Every applicability predicate is typed on it. Declared:
  `crystal-type`.
- **Which `(StateComponent, SubDofTag)` pairs are legal.** Declared: `sub-dof-pair-table`.
  C8 is the different and prior question — no component has a transformation law even
  where the pair is legal.
- **The equality-saturation cost bound.** Declared:
  `algebraic-simplification-performance`. C10 reports the rule set, termination and
  extraction, which that question does not touch.
- **The implementation language / codegen host.** Declared: `implementation-language-picks`,
  which explicitly includes "a typed intermediate representation and a code-generation
  path". I therefore did not report the codegen *target*; C19 reports the exit types,
  which are language-independent.
- **No numeric mesh-uncertainty floor.** Declared: `mesh-uncertainty-floor-undeclared`.
  C5 is the absence of a mesh *input*, which that question presupposes.
- **The symmetry quotient's stated input reads "the topology-atlas entry for this
  composition's space group, Wyckoff orbits and orbital basis" while the atlas record
  carries none of the last two as fields.** Rejected as a finding: the sentence reads
  naturally as "the entry *for* (space group, Wyckoff orbits, orbital basis)", i.e. the
  entry's key, and those three are recoverable from `PeriodicityStructure` and
  `SiteDecoration`. Ambiguous, not absent.
- **`Import`'s pinned `Input` nodes are inserted at symbolic lift but the stage's Inputs
  paragraph does not list the targets file.** A composition-request completeness question;
  `product#import-is-a-compiler-input` covers the intent. Too thin to raise.
- **`SymbolicLiftSidecar.coupling-channels` is declared as an input to stage 3 but stage 1's
  own "Sidecar produced" paragraph names only `.applicability`.** The channel list's
  producer is stated in `coupling-structure`'s worked example ("Symbolic lift records the
  channel in the stage sidecar"), so it is recoverable. Rejected as by-catch-grade.
- **`MerkleDAG` node-store growth, hash-cons table sizing, and arena capacity.** Genuinely
  unspecified, but they are implementation sizing rather than build-sheet content — an
  implementer types them without inventing physics or design.

## By-catch

- `compose-time-pipeline` calls `kernel_extension` "the nullspace sense of the word, not
  the compiled artifact" (twice, including in the runtime `kernel` disambiguation), but
  `coupling-structure` defines it as an integral kernel `K(q,ω)` — "a section of a `BZ × ℝ_ω`
  fiber bundle valued in a bounded-rank tensor". Neither the nullspace nor the artifact.
- `coupling-structure` sends the reader to `[canonical-vocabularies#scope]` for the lifting
  of `CrystalSymmetryGroup`; that anchor's text is about which certification obligations
  the theory vocabularies touch and never mentions the group. Dangling in content, not in
  form.
- `applicability-classifiers` requires predicates to be decidable "never on numeric
  thresholds or solver outputs", while `is-polar-material` is defined by nonzero Born
  effective charges — a registry-computed quantity. Same tension underlies
  `is-insulator-or-semiconductor` (a gap threshold) and `is-superconductor`.
- The `KernelExt.tag` vocabulary has no member for the piezoelectric-acoustic channel that
  the coverage-policy table declares `LongRangeStatic(1)` and `polynomial_sufficient` false.
- `topology-atlas` frontmatter declares `open-questions: []` while three of its five record
  fields have no derivation and no data source (C7).
- `data/registry-manifest.csv` carries nine columns; `formula-registry` says "One column
  per field of the formula record" and the record in `named-formulas` has more fields than
  that — `applicability`, `axes`, `input-contract`, `output-contract`,
  `characteristic-scale` among them.
- `forced-decisions` assigns character tables and projectors to an offline group-theory
  engine whose "results are baked in", which is the only statement in the corpus about
  where irrep data comes from; it is on a build page rather than on either compilation page
  that consumes it.
