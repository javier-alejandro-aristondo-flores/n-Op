# A3 — certification, the exported surface, and the representation substrate

Build-sheet pass over units 9, 10 and 11. For each thing an implementer must produce:
the exact type of every input and output; the algorithm rather than its name; every
numeric constant and its origin; and the error or refusal path. Findings are things an
implementer could not type. DETERMINED items are counted at the end and not reported.

Frontmatter `open-questions:` blocks were read **last**, after all findings below were
written, and are used only to mark what the corpus already admits.

---

## Unit 9 — certification

### X1 — the obligation traversal binds on a typeclass axis that no record carries, in `cert-obligations.md`

**Verdict:** ABSENT

**The obligation.** The page makes the axis the whole dispatch mechanism:

> Each obligation is a **generic function over one typeclass axis** ([typeclass-alphabet]),
> which is what lets one checker serve every formula that presents that axis rather than
> one checker per formula. The axis is the second column; it is not a separate mapping, and
> it is not restated anywhere else, because this list existed in three copies with three
> different second columns and a retag reached one of them.

[typeclass-alphabet] states the same dependency from its own side:

> mechanically ([cert-obligations#the-ten-obligations]) — an obligation is a
> claim about one axis, so the axis decides which obligations even apply.

**What is missing.** Nothing anywhere records, per formula or per node, *which axes it
presents*. `FormulaRecord` ([named-formulas#formula-record]) has ten fields — `name`,
`signature`, `bundle`, `cost-tier`, `differentiability`, `anchor-class`, `provenance`,
`depends-on`, `applicability`, `adjoint-validated` — and none of them is a typeclass. The
manifest's field list ([formula-registry#fields]) has nine and none of them is a
typeclass. `data/registry-manifest.csv` has nine columns — `#`, `Name`, ``Signature
`(in) → out` ``, `Bundle`, `Tier`, `Diff`, `Path`, `Source`, `Depends on`. `ResidualGenerator`
([residual-machinery#generator-record]) has eighteen fields and none of them is a
typeclass. The one place a typeclass is carried is the graph node's `type : Layer0Type`,
whose membership is itself never given (X20).

So an implementer asking "over what does obligation 1 run?" has no field to read. The
answer is available only by a human reading the signature column of each of 134 rows and
deciding whether the output is a function on a domain. Two competent implementers would
bind different sets — and the page's own history says the second column has already been
mis-edited once.

**Control.** Searched `grep -rniE "typeclass (tag|field|axis).*(column|field|manifest|row)|presents.*typeclass|carries.*typeclass" journals/` → 0 hits. Searched `grep -rc "Sampleable" journals/` → hits in exactly two files, `typeclass-alphabet.md` (5) and `cert-obligations.md` (2), none of them a record field. Control that fires: the same style of search for a field that *is* per-row, `grep -rn "the manifest's \`cost-tier\` field" journals/` → 1 hit, so the search reaches statements of the form "the per-row value is looked up in field X" where they exist.

---

### X2 — four of the ten obligations name no typeclass axis at all, in `cert-obligations.md`

**Verdict:** ABSENT

**The obligation.** The table's second column is declared to be the axis and the axis is
declared to determine the traversal set (quoted in X1). The column reads, for four rows:

> | 4 | reference battery | content-side: look a row up by `(Property, Material, Environment)` in the frozen reference data on a held-out crystal battery ([reference-battery]) and compare under `approxEq` | `O(log n)` B-tree |

> | 8 | reference-battery versioning | versioning discipline on obligation 4: per-entry provenance travels with the verdict, the row's schema version is compared by the reader, and the cert trips at `τ_battery` with the numerical witness | `O(log n)` + `O(1)` |

> | 10 | adjoint existence at registration | the registration-time adjoint gate ([residual-machinery]), enforced at registration and never at prediction: a DAG walk asserting every upstream node has a registered adjoint. It covers **both** `adjoint` and `fixpoint-adjoint`, because the second refines the first rather than replacing it and runs its gate plus a conditioning check ([named-formulas#diff-tags]) — gating only `adjoint` would exempt the stronger tier from the test the weaker one must pass | `O(#nodes)`, memoized |

**What is missing.** "content-side", "versioning discipline on obligation 4", "the
registration-time adjoint gate" and obligation 9's checker body are not typeclass axes.
Obligation 10 alone is recoverable — it reads `differentiability ∈ {adjoint,
fixpoint-adjoint}`, which is a real manifest column. For 4 and 8 the corpus never says
which formulas have a battery row to be checked against: `anchor-class` is the closest
candidate and the page explicitly denies it is a runtime selector
([named-formulas#anchor-class]: "This is **not** a runtime path selector"). For 9 the
scope is declared open — but see the scope note below.

The corpus admits obligation 9's scope only:

> - id: surrogate-validity-scope

That declaration is about *which tag* obligation 9 ranges over. It says nothing about
obligations 4 and 8, which have no candidate tag at all.

**Control.** Searched `grep -rn "Sampleable\|HasAnalyticStructure\|DiscreteStructure\|Integrable" journals/oracle/certification/cert-obligations.md` → hits on rows 1, 2, 3, 5, 6, 7 only; rows 4, 8, 9, 10 return nothing. Control that fires: the same search finds `Quantity` on row 2 and `DiscreteStructure` on row 7, so the search does reach the axis names where they were written.

---

### X3 — the stage each obligation runs at is stated for one of ten, in `cert-obligations.md`

**Verdict:** ABSENT

**The obligation.** The corpus places the cert in three mutually exclusive places. Per
prediction:

> The certificate emitted for any prediction is an **inert s-expression** carrying scalar
> verdicts plus numeric witnesses for the failures.

At codegen ([compose-time-pipeline#lowering-and-adjoint-synthesis]):

> **Codegen.** The whole graph is lowered to a compiled kernel with one entry point — the
> `Input` slots — and four typed exits: a residual map keyed by `ResidualKey`, a gradient
> map on the same keys, an observable map, and the certification evidence produced by the
> obligation traversals ([cert-obligations#the-ten-obligations]).

And explicitly *not* per sample ([representation-substrate#hot-paths]):

> The two super-logarithmic rows below — symmetry projector, evidence aggregation — are compile-time, cached, or
> certification-side, and are not per-sample.

**What is missing.** Exactly one obligation carries a stage — obligation 10, "enforced at
registration and never at prediction". For the other nine an implementer must decide
whether the checker runs at registration, at symbolic lift, at codegen, or inside
`evaluate`, and the three statements above support three different answers. The choice is
not cosmetic: obligation 4 is a database read, obligation 6 evaluates a degeneracy
tripwire per tier, and obligation 1 samples the emitted form — putting any of them inside
`evaluate` violates the hot-path commitment, and putting them at codegen means
`CertEvidence` in the runtime output tuple is a constant the kernel carries rather than a
per-call result. Nothing says which.

**Control.** Searched `grep -rniE "at (registration|compose time|compile time|prediction|check time|runtime)" journals/oracle/certification/` → the only obligation-scoped hit is obligation 10's "enforced at registration and never at prediction". Control that fires: the same search over `journals/oracle/seams/residual-machinery.md` returns "It runs once, at registration, against the" and "measured once at" — so the phrasing class is present in the corpus and the search reaches it.

---

### X4 — obligation 4's lookup key has no columns and no index in the store it reads, in `cert-obligations.md`

**Verdict:** ABSENT

**The obligation.** The traversal is specified as a keyed lookup at a stated complexity:

> | 4 | reference battery | content-side: look a row up by `(Property, Material, Environment)` in the frozen reference data on a held-out crystal battery ([reference-battery]) and compare under `approxEq` | `O(log n)` B-tree |

and the store it reads is given a complete DDL:

> ```
> table entries (
>   key             TEXT  PRIMARY KEY,   -- ContentAddress over (observable, value, sigma, provenance, coverage-mask)
>   observable      TEXT  NOT NULL,      -- ObservableRef serialization
>   value           BLOB  NOT NULL,      -- typed payload (scalar, tensor, curve)
>   sigma           REAL  NOT NULL,
>   provenance      TEXT  NOT NULL,      -- JSON: { source, doi?, fetched-at, version }
>   coverage_mask   BLOB  NOT NULL,      -- RoaringCoverageMask serialization
>   schema_version  INT   NOT NULL
> )
> ```

**What is missing.** The lookup cannot be written against that table. There is no
`material` column and no `environment` column, so two of the three key components have
nowhere to be read from. The only indexed column is `key`, and `key` is a content address
**over the value itself** — so keying by it presupposes knowing the answer the lookup is
for. The remaining candidate, `observable`, is an unindexed `TEXT` column, which makes the
stated `O(log n)` B-tree bound wrong by a linear factor even if `ObservableRef` turned out
to encode material and environment — and `ObservableRef` is defined nowhere (X11).

The corpus admits one adjacent gap and it is a different one:

> - id: csv-to-sqlite-path

That declaration covers *how a CSV row becomes a cache row*. It does not cover the fact
that the destination table has no columns for the key the obligation looks up on.

**Control.** Searched the DDL block for its key components: `sed -n '210,220p' journals/oracle/certification/cert-obligations.md | grep -ci "material\|environment"` → 0. Control that fires: the same search for `observable` on the same block → 2 hits, so the search does read the DDL's column names.

---

### X5 — `Pending` is a verdict nothing produces, in `cert-obligations.md`

**Verdict:** ABSENT

**The obligation.** The aggregation rule is a three-valued semilattice:

> - `Failed` if any obligation leaf is `Failed`,
> - `Pending` if any leaf is `Pending` and none is `Failed`,
> - `Passed` otherwise.

**What is missing.** No obligation is anywhere said to return `Pending`, and no rule says
under what condition a leaf takes that value. Every one of the ten obligations is
described as a comparison against a tolerance, which is two-valued. An implementer writing
the ten checkers has no case that emits the middle element, at which point the meet is
Boolean and the third value is dead. If `Pending` is meant to carry the deferred-gate case
that [residual-machinery#registration-gate] says has nowhere to go — "**The cert has no
way to say "deferred".**" — nothing says so; that page reaches for a fourth value on a
*different* record (`adjoint-cert`) and does not connect it to this one.

**Control.** Searched `grep -rn "Pending" journals/` → exactly 1 hit in the whole corpus, the aggregation bullet quoted above. Control that fires: the same search for the sibling values, `grep -rn "\`Passed\`\|Failed(witness)" journals/` → 4 hits across `cert-obligations.md`, `residual-machinery.md` and `named-formulas.md`, including a record that actually declares them as field values — so the search reaches verdict vocabularies that are produced somewhere.

---

### X6 — the certificate artifact is two incompatible objects and neither has a byte-level form, in `cert-obligations.md`

**Verdict:** ABSENT

**The obligation.** The page owns "certificate artifact" and states it twice, differently.
As a serialized term:

> The certificate emitted for any prediction is an **inert s-expression** carrying scalar
> verdicts plus numeric witnesses for the failures. It executes nothing and decides
> nothing; reading it is the whole of consuming it.

As a hash:

> `Failed` absorbs, which is what licenses early exit. The attestation DAG's root
> `Address` is the cert artifact the operator library consumes.

And the file that consumers hold carries a third thing ([product#oracle-file-contents]):

> 4. **Its certificate reference** — a hash-pinned pointer to the certification evidence

**What is missing.** No grammar for the s-expression: no atom set, no node names, no
ordering, no encoding of the "scalar verdicts", no encoding of the "numeric witnesses", no
statement of whether it is the serialization of the attestation DAG or an independent
rendering. The page announces machinery over it — "a schema, a deterministic text
renderer, a freeze fixture with a tamper tripwire, and a high-precision oracle
cross-check" — and specifies none of the four. A deterministic renderer with no stated
term order is not implementable, and a freeze fixture with no byte form has nothing to
freeze.

**Control.** Searched `grep -rn "s-expression\|sexp\|S-expression" journals/` → 1 hit, the sentence quoted above; the token appears nowhere else in the corpus. Control that fires: the corpus does specify serialization at byte level where it chooses to — `grep -rn "big-endian" journals/` → 2 hits in `representation-substrate.md` giving `Nat`/`Int`/`Float` layouts, and the SQLite DDL above is given column by column. So the search style reaches byte-level format statements where they exist.

---

### X7 — four tolerance-ledger rows carry no value and name no record that holds one, in `cert-obligations.md`

**Verdict:** UNDERSPECIFIED

**The obligation.** The ledger is declared canonical for every tolerance:

> Canonical names and default values for every tolerance and error bound in the oracle
> library. These are the inputs `Quantity.combineTol` ([typeclass-alphabet]) composes into
> the per-observable error budget ([residual-definitions]).

Four of its seventeen rows resolve the Default column to a deferral:

> | `τ_method` | `Algebraic/MethodEquivalence` **consistency-pair** model-gap envelope (obligation 6) | 10–20%, declared per formula pair |

> | `δ_surrogate` | obligation-9 validity margin, measured on a held-out development set. **What it ranges over is `surrogate-validity-scope`**: this row reads *relaxation* validity and the obligation reads *surrogate* validity | per formula |

> | `δ_plan` | per-compression-plan truncation error target ([compose-time-pipeline]); the sum over active plans is the compression term in `combineTol` | per plan, declared at plan selection |

**What is missing.** "declared per formula pair", "per formula" and "declared at plan
selection" name no field on any record. `FormulaRecord` has no tolerance field.
`ResidualGenerator` has `characteristic-scale`, which [residual-machinery#generator-record]
calls "an error-model input, never a" fitted weight — an accuracy scale, not a tolerance.
`CompressionPlan` is a sum of `Dense | Sparse(sparsity-pattern) | LowRank(rank) |
HODLR(params) | TT(ranks) | …` with no error-target member. So three of the four terms
`combineTol` is supposed to compose have no storage location, and `combineTol` cannot be
called. `τ_method`'s "10–20%" additionally gives a range where the column promises a value.

**Control.** Searched `grep -rhoE '\`(τ|δ|ε|σ)_[A-Za-z0-9,]+\`' journals/ | sort -u` → 26 distinct symbols; all 17 ledger names are present, and every non-ledger symbol (`τ_E`, `τ_PO`, `τ_p`, `τ_n`, `τ_iv`, `τ_hop`, `τ_alloy`, `σ_d`, `ε_static`, `τ_x`) is one the page itself declares a physical time or a physics symbol. So the ledger *is* exhaustive over tolerance names — that half of the unit's question is DETERMINED, and this finding is about the Default column only. Control that fires: the same search finds `1e-6`, `1e-9`, `1e-8 Ha`, `50 meV/atom` and `3σ` in the same column, so the search reaches rows that do carry values.

---

### X8 — the `applicability` field the predicate contract requires exists on no manifest schema, in `applicability-classifiers.md`

**Verdict:** ABSENT

**The obligation.** The V1 commitment is stated as a countable, checkable property:

> **Every registry entry gets an explicit `applicability` field.** Always-true stubs are
> acceptable for V1.0 and are refined incrementally — an explicit stub is a claim a reader
> can find and a checker can count, which an absent field is not.

Obligation 2 reads it at check time ([cert-obligations#the-ten-obligations]):

> `Quantity` ordering: the value is checked against each declared bound. Applicability evaluation plus a scalar range test

**What is missing.** The manifest's field list ([formula-registry#fields]) has nine rows
and `applicability` is not one of them; the same page's vocabulary table names
`applicability` as a coded field with a defining page, so the two tables on one page
disagree about whether the column exists. `data/registry-manifest.csv` has nine columns
and none is applicability. So "a checker can count" has nothing to count, and the stub
that [applicability-classifiers#trap-density-gates] says row 116 "runs on" is not
recorded anywhere a program can read.

Storage *is* specified for the predicate object itself — a `MerkleDAG[PredicateOps, Atom]`
root — so the gap is precisely the binding from row to root. Nothing states which column,
sidecar or side table holds it.

**Control.** Searched `grep -rn "applicability" journals/oracle/registry/formula-registry.md` → 2 hits: the `depends-on` entry and the vocabulary-table row. Neither is in the field list. Searched `head -1 data/registry-manifest.csv` → `#,Name,Signature \`(in) → out\`,Bundle,Tier,Diff,Path,Source,Depends on`. Control that fires: the same two searches for `differentiability` find it *both* in the field list and as the CSV's `Diff` column — so the search reaches fields that are genuinely present in both places.

---

### X9 — "refusal is absence" has no mechanism: nothing connects a failed obligation to a missing check, in `product.md`

**Verdict:** ABSENT

**The obligation.** This is the corpus's headline guarantee about what it does when it
cannot proceed:

> A check the oracle cannot stand behind for this instance — inapplicable, outside the
> certified envelope, or refused by certification — is not in the compiled kernel, so
> its key is simply not in any map.

**What is missing.** Three causes are named and only the first has a mechanism.

*Inapplicable* is implemented: [compose-time-pipeline#symbolic-lift] states "Any subgraph
whose applicability is false for this crystal-and-environment pair is **deleted**."

*Outside the certified envelope* — "certified envelope" appears once in the corpus, here,
and is defined nowhere. It is not the environment box, which is a different object with a
different name on a different page (X15).

*Refused by certification* has no mechanism at all. The five compose-time stages are
symbolic lift, symmetry quotient, invariant synthesis, algebraic simplification, lowering
and adjoint synthesis; the only deletion in any of them is the applicability deletion
above. Certification obligations are described as traversals over the finished graph
([physics-graph#vocabulary-realization]: "global traversals, indexed by `NodeKind` and
`OutputRole`"), and the four composition-validity refusals are "emitted as obligation
leaves"; nothing anywhere removes a node because a leaf came back `Failed`, and nothing
states at which stage such a removal would happen or what re-runs after it. Since a
`Failed` leaf is also what the aggregation rule turns into a composition-level `Failed`
verdict, the two readings — the whole composition fails, versus the offending check
silently disappears from the kernel — are both live and lead to completely different
compilers.

Traced end to end, as asked: **who decides** — unstated for two of three causes;
**at which stage** — unstated (X3); **writing what** — a refusal mode that is never
enumerated (X10); **into which record** — the certification record, which has two
incompatible descriptions (X6); **read by whom** — unstated. Every link but the first is
missing.

**Control.** Searched `grep -rniE "prune|pruned|pruning" journals/` → 10 hits, every one of them either the applicability prune, the compile-request prune, or the invariant generator's character pre-prune; none is cert-driven. Searched `grep -rniE "not in the compiled kernel|removed from the kernel|never becomes code" journals/` → 2 hits, both in `product.md`, both asserting the outcome. Control that fires: `grep -rn "is \*\*deleted\*\*" journals/` → 1 hit in `compose-time-pipeline.md`, so a search of this shape does find the corpus's one real deletion mechanism where it exists.

---

### X10 — the closed-enum refusal mode is never enumerated, and the declaration that admits a missing refusal enum covers only the evolver, in `product.md`

**Verdict:** ABSENT

**The obligation.** The page makes machine-readability of the reason a named principle —
"**No natural language.** Every artifact is machine data: keyed numbers, enum codes,
numeric witnesses, hashes." — and then discharges it here:

> The *reason* is machine data in the certification record: a closed-enum refusal mode
> plus numeric witnesses
> ([cert-obligations#certificate-artifact]). No prose, anywhere.

**What is missing.** The enum's members. `cert-obligations#certificate-artifact`, the
page this sentence points at, does not contain the word refusal at all; the four
composition-validity refusals are a *different* anchor on that page and are named in
prose bullets rather than as enum members, and they cover only compose-time coefficient
and tag mismatches — not inapplicability, not out-of-envelope, not out-of-scope. The
witnesses are described per bullet ("the offending coefficient or row pair", "the
`(slope coefficient, thermal-expansion instance, observable)` triple", "the tag pair")
and their types are never given.

**On the scope of the corpus's own admission.** One open question mentions a refusal enum:

> - id: evolver-lowering-spec
>     anchor: steppable-form-manifest
>     summary: "The full lowering specification — the manifest record, the refusal enum, and the scorer-versus-evolver exactness obligation — is not written. No time-evolution product verb is claimed until it is."

Its anchor is `steppable-form-manifest` and its consequence is "No time-evolution product
verb is claimed until it is" — so it declares the refusal enum unwritten **for
`dynamics(tier)`**, a hand-off the corpus explicitly does not ship. It does not cover the
refusal mode of the scoring path, which `product.md` relies on for the shipped product and
states as settled. The wide dependency is attached to the narrow admission: a reader
skimming open questions will see "the refusal enum" already confessed and mark this known.
It is not.

**Control.** Searched `grep -rnE "Refusal(Mode|Kind|Reason)|refusal-(mode|kind|reason)|RefusedBecause" journals/` → 0 hits. Searched `grep -rn "closed enum\|closed-enum" journals/` → 3 hits, none enumerating refusal values. Searched `grep -rni "refusal" journals/` → 32 hits, all prose. Control that fires: the same style of search for enumerated closed vocabularies finds plenty — `grep -rnE "NodeKind =|OutputRole =|Producer *=|InputKind =|CompressionPlan =" journals/` → 6 hits with members written out, and `canonical-vocabularies.md` gives ten closed vocabularies member by member. So the search reaches enumerated vocabularies where the corpus wrote them.

---

## Unit 10 — the exported surface and the artifact

### X11 — `ObservableRef`, the key type of two of the three exports, is defined nowhere, in `pino-bridge.md`

**Verdict:** ABSENT

**The obligation.** It is a parameter and a return key on the only surface consumers see:

> ```
> Validate(state    : UnifiedState,           -- the seven-tuple of unified-state
>          env      : Environment,
>          request  : all | {ResidualKey} | {ObservableRef},
>          gradient : Skip | Compute)
>        → ( residuals : Map<ResidualKey, Scalar>
>          , values    : Map<ObservableRef, Value>              -- bundled observable outputs
>          , cograds   : Optional<Map<ResidualKey, Cotangent>>  -- the kernel's gradient map
>          , cert      : CertEvidence )
> ```

and the first argument of the second export:

> ```
> Import(named-target  : ObservableRef,
>        value         : Value,
>        standard-deviation : Scalar,
>        provenance    : Provenance,
>        axis-coverage : AxisCoverage)
>      → GroundTruthBridgeGenerator
> ```

**What is missing.** `ObservableRef` has no definition, no record, no page. It is also the
`observable` column of the reference cache ("ObservableRef serialization") and the key of
`ObservableMap` in the runtime kernel's output tuple, so it is simultaneously a wire type,
a database column, and a selection argument — and an implementer cannot write any of the
three. Whether it names a registry row, a bundle member, a `(row, axis-tuple)` pair, or
a catalog property is undecidable from use sites: `Import`'s "named-target" and
`request`'s "a subset of observables" pull in different directions.

The glossary states the consequence of its own absence explicitly — "If a name is missing
from both, no page claims it. That is a finding, not a lookup failure" — and
`ObservableRef` is missing from both. The same is true of `Value`, `Cotangent`,
`Provenance` and `TypedSlot`, all of which appear only as bare type names in signatures.

**Control.** Searched `grep -c "ObservableRef" journals/practice/glossary.md` → 0, and `python3` over `generated/corpus.json` for a topic containing `ObservableRef` → 0 of 273 topics. Control that fires: the identical pair of searches for the sibling key type, `ResidualKey`, → 1 glossary row pointing at `[residual-definitions#residualkey]`, where the type is actually written out as `ResidualKey = (producer : Producer, axes : Tuple<AxisLabel>)`; and a topic `residual granularity discipline` exists. So both instruments reach a surface type that *is* claimed and defined.

---

### X12 — the fourth return of `Validate` is two different objects on two pages, and its type is a name with no definition, in `pino-bridge.md` and `product.md`

**Verdict:** UNDERSPECIFIED

**The obligation.** The signature says the fourth return is certification evidence:

>          , cert      : CertEvidence )

The product page, describing the same single entry point, says it is a hash:

> One entry point, whose signature is [pino-bridge#validate]. It returns four things:
> the raw residual map keyed by slot, the values map holding requested derived
> quantities, an optional cotangent map populated only when gradients were requested,
> and the content hash of the producing kernel.

**What is missing.** An implementer cannot type the return. The two readings are not
reconcilable by inspection: `cert-obligations` says the artifact the consumer holds is the
attestation DAG's root `Address`, which is a cert hash and not a kernel hash, while
`product` names the kernel hash specifically. And `CertEvidence` itself is undefined — the
glossary points it at `[compose-time-pipeline#runtime-kernel-application]`, where the only
occurrence is the tuple field `CertEvidence : CertEvidence`, a name standing for itself.

**Control.** Searched `grep -rn "CertEvidence" journals/` → 3 hits: the glossary pointer, the `pino-bridge` signature, and the `compose-time-pipeline` tuple line. None is a definition. Control that fires: the same search for `ResidualGenerator` → hits including a full `record ResidualGenerator { … }` block, so the search reaches type definitions where the corpus wrote them.

---

### X13 — the oracle-file has no on-disk format, in `product.md`

**Verdict:** ABSENT

**The obligation.** The file is the product:

> - **The oracle-file** — the emitted kernel, persisted. Loaded by any program and
>   called like a function, microseconds to milliseconds per call, millions of times.
>   This file is the thing consumers actually hold.

> One file on disk, four things inside.

**What is missing.** Everything below "four things". No container, no magic bytes, no
header, no section table, no encoding for the callable (native shared object? bytecode?
serialized IR?), no encoding for the static slot schema, no ordering, no versioning of the
file format itself as distinct from the registry and specification versions it records.
"Loaded by any program and called like a function" is an interoperability claim that
cannot be met without a stated ABI, and "self-describing" is a property of a format, not a
property that can be asserted in the absence of one.

The corpus's own gap markers do not reach here. `state-wire-schema` covers the state
object's per-slot dtype and layout, not the artifact; `implementation-language-picks`
covers which language hosts the compiler, and a file format is exactly the thing that must
be fixed *independently* of that choice if "loaded by any program" is to mean anything.

**Control.** Searched `grep -rniE "\b(magic bytes|magic number|file header|section table|container format|CBOR|protobuf|flatbuffers?|msgpack|\.so\b|shared object|dynamic library)\b" journals/` → 0 hits. Control that fires: the same search style over format vocabulary the corpus *does* use returns plenty — `grep -rn "16-byte" journals/` → 1 hit specifying the domain separator's width, `grep -rn "big-endian" journals/` → 2 hits specifying scalar layout, and the reference cache is given a full SQL DDL. So the corpus states on-disk formats where it has decided them, and the search reaches those statements.

---

### X14 — "file hash equals kernel hash" names three hashes and reconciles none of them, in `product.md`

**Verdict:** UNDERSPECIFIED

**The obligation.** It is asserted as a filesystem-level guarantee:

> **File hash equals kernel hash**, so attribution, caching, and "which oracle
>    produced this result?" are filesystem-level facts.

**What is missing.** The file's third content is "the content hash of the compiled kernel",
so the kernel hash is *inside* the bytes whose hash is claimed to equal it. Taken as a hash
over file bytes the statement is unsatisfiable; taken as a naming convention (the file is
*named* by the kernel hash) it is satisfiable but different, and nothing says which is
meant or which byte range is covered. Separately, `compose-time-pipeline#boundary` defines
a third identity — "A composition fingerprint — a content hash of periodicity, decoration,
and the *structural* part of the environment — keys a kernel cache" — and no page states
whether the composition fingerprint and the kernel hash are the same value. An implementer
must choose, and the choice determines whether two structurally identical compositions
compiled against different registry versions collide in the cache.

**Control.** Searched `grep -rniE "file hash|kernel hash|composition fingerprint|sibling fingerprint" journals/` → 7 hits across 5 files, none of them relating the three. Control that fires: the corpus does state hash-construction rules precisely elsewhere — `grep -rn "Address\[D\] = Hash" journals/` → 1 hit giving the three inputs to every address — so a statement of this shape would have been found if written.

---

### X15 — the environment-box stamp has no type and its out-of-box behavior is an unresolved disjunction, in `crystal-inputs.md`

**Verdict:** ABSENT

**The obligation.** It is what makes out-of-box use "mechanically detectable"
([product#behavioral-rules]) and what
[applicability-classifiers#swept-environment-windows] says makes per-sample masking
checkable "rather than merely intended":

> Each emitted kernel is stamped with its **environment box** — the per-swept-field range set on
> which its invariant-synthesis structure is valid. A sample whose swept scalar leaves the box is
> masked out, or trips the relevant certification obligation, rather than being scored against a
> kernel that does not cover it ([product#environment-input]).

**What is missing.** Three things, in the sentence that owns the object.

*The type.* "range set" is not a type. Closed or half-open intervals, unions, per-field or
joint, what a field absent from the box means, and where the box lives in the artifact are
all unstated. Since the box is stamped on the kernel and the kernel's file format does not
exist (X13), it has no location either.

*The behavior.* "masked out, **or** trips the relevant certification obligation" is a
disjunction with no decision rule. These are opposite outcomes — one silently drops a
sample from a training batch, the other emits a `Failed` leaf — and an implementer must
pick one.

*The obligation.* "the relevant certification obligation" names none of the ten. None of
the ten mentions the environment box.

**On scope.** `crystal-inputs` declares two adjacent open questions —
`environment-schema` (the record's field set and types) and
`environment-structural-partition` (which fields are structural versus swept). Neither
mentions the box. The box is downstream of both and independent of them: even with the
partition settled and every field typed, none of the three gaps above closes.

**Control.** Searched `grep -rniE "certified envelope|environment box|validity box|range set" journals/` → 5 hits, being the sentence above, the two pages pointing at it, and `product.md`'s "certified envelope" and "validity box". No hit gives a type or a decision rule. Control that fires: the same search style for a stamp the corpus *does* type — `grep -rn "coverage_mask   BLOB" journals/` → 1 hit giving column, type and serialization for the axis-coverage stamp. So a per-field typed stamp is something this corpus writes when it has decided one.

---

### X16 — the three command-line verbs have no arguments, no output encoding, no input format, and no failure path, in `product.md`

**Verdict:** ABSENT

**The obligation.** The command line is one of the two consumption paths and is owned by
this page:

> - `compile` — identity, plus environment, plus channel flags, plus an optional targets
>   file, produces one oracle-file.
> - `inspect` — oracle-file produces its static schema and identity, enumerated.
> - `validate` — oracle-file plus a state file, plus environment and request flags,
>   produces the keyed-float maps, serialized.

**What is missing.**

*Arguments.* No flag names anywhere in the corpus. "identity" is three descriptors with no
stated file form; "channel flags" and "request flags" name no vocabulary — `request` on
the exported call is `all | {ResidualKey} | {ObservableRef}`, and how a set of content
addresses is written on a command line is not addressed.

*Input format.* "a state file" and "a targets file" have no format. `Import` is declared a
compiler input — "a targets file handed to the compiler" — so the targets file is the wire
form of the `Import` signature, and it has no encoding.

*Output encoding.* "produces the keyed-float maps, serialized" and "enumerated" name no
format. Keys are content addresses; whether they render as hex, base64 or names is
unstated.

*Failure path.* No exit codes, no stderr contract, no statement of what the command line
does when the state file is malformed, when the environment leaves the box, or when the
cert refuses. This is the same refusal chain as X9, now with a second unwritten end.

**Control.** Searched `grep -rnE '^\s*[-*]?\s*\`?--[a-z]' journals/` → 0 hits; the string `--` introducing a flag appears nowhere in the corpus. Searched `grep -rniE "exit code|exit status|stderr|stdout|non-zero" journals/` → 1 hit, "returns a non-zero residual", which is about a residual value and not a process status. Control that fires: `grep -rn '\`compile\`\|\`inspect\`\|\`validate\`' journals/` → the three verbs are found by name, so the search reaches the command line where it is written; it is the arguments that are not there.

---

### X17 — the out-of-scope refusal is raised by a call the bridge does not export, in `out-of-scope.md`

**Verdict:** ABSENT

**The obligation.** The page owns the "out-of-scope refusal mechanism" and states it in
one sentence:

> `predict` raises `out-of-scope` with a witness for any of the above. Cert obligation 3
> flags suspect cases ([cert-obligations#the-ten-obligations]).

**What is missing.** `predict` is not on the exported surface. [pino-bridge#not-exported]:

> `Predict`, `Certify` and `EnumerateObservables` remain available as the oracle's
> internal interface for non-operator consumers — the loops library, debugging
> tools, the cert-only batch validator. They are not part of the pino-bridge
> contract.

So the single stated mechanism for roughly twenty-five scope exclusions — including the
ones the page marks emphatically, "**cert-refused**" for aluminium-nitride avalanche
claims and β-Ga₂O₃ hole transport, "**The refusal is the correct output.**" — fires on a
call that the operator library and every pino-bridge consumer never make. What `Validate`
does in the same situation is unstated; `product.md`'s answer is absence from the kernel,
which is a different mechanism with no chain behind it (X9). Neither the signature of
`predict` nor the type of `out-of-scope` nor the type of its witness is given anywhere.

Obligation 3's role compounds it: obligation 3 is the analytic-limits checker
(`HasAnalyticStructure`, "compare to the closed form at `|predicted − exact|/σ < 3`"), and
nothing in it flags scope. "flags suspect cases" is a claim about a checker whose stated
body cannot do it.

**Control.** Searched `grep -rn "predict\b" journals/oracle/certification/out-of-scope.md` → 1 hit, the sentence quoted. Searched `grep -rnE "\bPredict\b|\bCertify\b|EnumerateObservables" journals/` → hits only in `pino-bridge.md`'s not-exported paragraph. Control that fires: the same search for `Validate` → hits in `pino-bridge.md`, `product.md`, `physics-graph.md` and `boundary.md`, i.e. an exported verb is visible across the corpus in the way a load-bearing entry point is; `predict` is not.

---

## Unit 11 — the representation substrate and the typeclass alphabet

### X18 — dense ordinals are assigned by no stated rule, so no `Address` is reproducible, in `representation-substrate.md`

**Verdict:** ABSENT

**The obligation.** Ordinals enter identity through the serialization rule:

> 7. **Sum types** — discriminator drawn from the vocabulary indexing the sum, serialized
>    as a 32-bit ordinal followed by a length-prefixed payload.

and downstream records store them rather than names
([canonical-vocabularies#versioning]):

> Each of the ten is a `Universe` instance with a closed carrier and dense
> unsigned ordinals ([representation-substrate#primitives]). A downstream record
> stores the ordinal, not the name.

**What is missing.** How a member gets its ordinal. Declaration order in the page table?
Lexicographic over member names? An explicit assignment table? Nothing says, and no
vocabulary in the corpus carries an ordinal column. This is not a cosmetic choice: the
serializer's injectivity is called "the single highest-consequence invariant in the
system", and every `Address` — hence every cache key, every `ResidualKey` the operator
holds weights against, every dedup, the cert root — is a function of these ordinals. Two
competent implementers produce disjoint address spaces over identical corpora, and neither
is detectably wrong.

The versioning discipline sharpens the gap rather than filling it: "Under dense ordinals a
new member either shifts existing ordinals or occupies a slot that older records may have
meant differently" describes exactly the hazard that a stated assignment rule would
manage, and then manages it with a version bump instead of a rule.

**Control.** Searched `grep -rn "ordinal" journals/` → 13 hits: the policy type `DenseU32 | DenseU64 | None`, the "doubles as a dense array index" note, the serialization rule, the version-bump rule, and page-numbering usages in `agent-contract.md`. None states an assignment. Control that fires: the same search style for the adjacent decision the corpus *did* make — `grep -rn "The choice is a property of the" journals/` → 1 hit, "**The choice is a property of the universe, fixed at registration — not of an individual sparse set.**", the backend-selection rule, which is stated with its threshold ladder in full. So the corpus does pin registration-time choices where it made them.

---

### X19 — the domain separators, the domain list, and the initial schema versions are all absent, in `representation-substrate.md`

**Verdict:** ABSENT

**The obligation.** Every address in the system is a function of all three:

> Address[D] = Hash(domain_separator(D), schema_version(D), canonical_node_bytes)

> 1. **Domain separator first** — a fixed 16-byte tag for the domain, so identical bytes
>    in different domains cannot collide.
> 2. **Schema version next** — an unsigned 32-bit value declared in the universe
>    descriptor, bumped on incompatible changes.

**What is missing.** The width of the separator is given and its values are not. `DomainId`
is used as a field type in `PersistentMap` and `MerkleDAG` and is never enumerated, so the
set of domains that must have separators is itself unknown — addresses are taken over at
least `Universe`, `Set[U]`, `Map[K,V]`, `DAG[S,L]`, `GraphNode`, `GraphAtlas`,
`InvariantTerm`, `GeneratorOutput` and `StateSnapshot`, gathered from scattered use sites
rather than from a list. No initial `schema_version` is stated for any universe or domain,
so "bumped on incompatible changes" has no baseline.

An implementer can write the hash function and cannot compute a single address with it.
Combined with X18 this makes the substrate's identity layer — the thing the page calls
"one canonical serialization rule, not per-cluster conventions" — unimplementable to a
common value, even though the rule itself is written out in eleven numbered clauses and is
otherwise the most completely specified thing in the corpus.

**Control.** Searched `grep -rn "domain_separator\|domain separator\|DomainId\|domain-separat" journals/` → 8 hits: the address formula, the rule clause, two field declarations, and four assertions that some address is domain-separated. No tag value, no domain list. Control that fires: the same page states the neighboring constants concretely — `grep -rn "SHA-256, 256 bits" journals/` → 1 hit, "The digest is SHA-256, 256 bits wide, truncated nowhere in storage", and clause 11 gives the float normalization exactly. So the search reaches constants on this page where they were written.

---

### X20 — `Layer0Type`, the type field on every graph node, is never enumerated, in `physics-graph.md` and `representation-substrate.md`

**Verdict:** ABSENT

**The obligation.** It is one of the node's four fields:

>   , type : Layer0Type        -- the typeclass alphabet

it is declared a closed universe with dense ordinals:

> | **vocabularies** — `StateComponent`, `SubDofTag`, `IrrepLabel`, `OutputRole`, `NodeKind`, `InputKind`, `CategoryTag`, `AxisLabel`, `BundleId`, `Layer0Type` | `Universe[T]` instances with dense ordinals | closed universes get `DenseU32`; open universes get `DenseU64` with an append-only registry |

and it is the realization of the typeclass alphabet in the graph
([physics-graph#vocabulary-realization]):

> | the typeclass alphabet ([typeclass-alphabet#axes]) | the `type` field on every node |

**What is missing.** Its members. `Layer0Type` appears exactly twice in the corpus, in the
two lines quoted above, and nothing says what a value of it looks like.
[typeclass-alphabet] describes four *typeclasses* plus three à-la-carte capabilities plus
four aliases — a constraint system a type may satisfy, not a set of types — so it cannot be
read off as the carrier. Three of the four aliases are declared never expanded
(`three-aliases-never-expanded`), which covers `Scalar`, `Tensor` and `FieldOnGrid` as
*return types in signatures*; it does not say that the node's type universe has no
membership, which is a different and larger hole. Since obligation dispatch is by axis
(X1) and this is the only field in the corpus that carries an axis, the two gaps close
each other's escape route.

`IrrepLabel` is in the same position: named once in the cluster table, pointed at from the
glossary, and enumerated nowhere.

**Control.** Searched `grep -rn "Layer0Type\|IrrepLabel" journals/` → 3 hits total: the node field, the cluster row, and the glossary pointer for `IrrepLabel`. Control that fires: the same search for the neighboring members of that same cluster list — `grep -rn "NodeKind =\|OutputRole =" journals/` → both enumerated in full in `physics-graph.md`, and `AtomicSpecies`'s membership is given outright in `canonical-vocabularies.md` as `{C, B, N, Al, Ga, O, H}`. So the search reaches enumerated universes in the same table where the corpus wrote them.

---

### X21 — `EvidenceOps` has four named ops and no attributes or arities, so the cert DAG cannot be built, in `representation-substrate.md`

**Verdict:** ABSENT

**The obligation.** The op signature is a required parameter of the primitive:

> Node[S, L] = Leaf(L) | Op(op : S.Op, attrs : S.Attrs[op], children : S.Arities[op])

and the evidence instance is named:

> - **`EvidenceOps`** — attestation, aggregation by semilattice meet, reference linkage,
>   trajectory chunk. Used by [cert-obligations#evidence-aggregation].

**What is missing.** `S.Op`, `S.Attrs[op]` and `S.Arities[op]` are given for none of the
four ops, and `EvidencePayload` — the leaf type — is named twice and defined nowhere. An
implementer cannot construct a node, cannot canonicalize one, and therefore cannot compute
the root `Address` that `cert-obligations` says *is* the artifact the operator library
consumes. The same absence applies to `PredicateOps` and `GroupOps`; `SymbolicTensorOps`
is the only one whose generators are listed, and even there the attribute records are not.

This is the load-bearing half of X6: the s-expression has no grammar and the DAG has no
node schema, so the certificate has no byte-level form under either of its two
descriptions.

**Control.** Searched `grep -rn "Attrs\|Arities" journals/` → 1 hit, the `Node[S, L]` line quoted above. Control that fires: the same search for the sibling parameter that *is* elaborated — `grep -rn "colored operad" journals/` → 1 hit introducing `SymbolicTensorOps`'s generator list in full ("scalar, antisymmetric form, positive-semidefinite symmetric form — plus tensor product, contraction, derivative, group action, projection and binding"). So the corpus does elaborate an op signature where it chose to.

---

### X22 — `Witness` names three different objects under one type, and is not in the overloaded-token register, in `typeclass-alphabet.md`

**Verdict:** UNDERSPECIFIED

**The obligation.** One definition exists:

> Witness = (Local | Global, law)

**What is missing.** That type does not fit its other two uses.
[residual-machinery#dressing-certs] declares `witness : Optional<Witness>` with the comment
"non-null iff divergent" and `divergence-witness: Optional<Witness>` — a numerical
divergence record, not a `(Local | Global, law)` pair. `cert-obligations` speaks throughout
of "numeric witnesses", and its four composition refusals carry witnesses that are a
coefficient, a triple, and a tag pair — none of which is a law. `adjoint-cert` carries
`Failed(witness)` with a fourth shape again. An implementer typing `Optional<Witness>` from
the one definition available produces a field that cannot hold what the pages say goes in
it.

The corpus has a register for exactly this hazard — [glossary#overloaded] lists ten tokens
that name two things and assigns each a qualifier — and `witness` is not among them.

**Control.** Searched `grep -rnE "\bWitness\b" journals/` → 6 hits across four files, one definition and five uses in incompatible positions. Control that fires: the same search for a token that *is* registered — `grep -rn "coverage-mask" journals/practice/glossary.md` → 1 hit, the register row splitting it three ways into `axis-coverage`, `applicability-mask` and `label-presence`. So the register exists, is populated, and reaches tokens of this shape.

---

## Coverage

**Read fully**

- `journals/oracle/certification/cert-obligations.md`
- `journals/oracle/certification/applicability-classifiers.md`
- `journals/oracle/certification/out-of-scope.md`
- `journals/oracle/seams/pino-bridge.md`
- `journals/oracle/seams/residual-machinery.md`
- `journals/n-op/purpose/product.md`
- `journals/interface/boundary.md`
- `journals/oracle/compilation/representation-substrate.md`
- `journals/oracle/compilation/physics-graph.md`
- `journals/oracle/registry/typeclass-alphabet.md`
- `journals/oracle/registry/canonical-vocabularies.md`
- `journals/oracle/registry/typed-compositions.md`
- `journals/oracle/registry/formula-registry.md`
- `journals/oracle/registry/named-formulas.md`
- `journals/oracle/accuracy/reference-battery.md`
- `journals/oracle/state/crystal-inputs.md`
- `journals/practice/glossary.md`
- `data/registry-manifest.csv` (parsed; header and tag distributions)

**Read partially**

- `journals/oracle/compilation/compose-time-pipeline.md` — lines 1–130 and 300–400 read fully (always-cheap, partial evaluation, symbolic lift, symmetry quotient opening, lowering/codegen, runtime kernel application, the boundary table). Invariant synthesis, algebraic simplification and the rewrite-admission rule read only through grep.
- `journals/oracle/laws/residual-definitions.md` — lines 180–309 read fully (`CategoryTag`, `ResidualKey`, `ContributionFacets`, output type, curriculum gate). The seventeen category definitions above line 180 read only through grep.
- `journals/oracle/laws/coupling-structure.md` — grep only, for `StateComponent`, `ProvenanceLedger`, target shapes, provenance contract.
- `journals/oracle/state/unified-state.md`, `multiscale-state.md`, `gamma-hat.md` — frontmatter and grep only.
- `journals/practice/traps.md`, `agent-contract.md`, `conventions.md` — grep only.
- `generated/corpus.json` — structure and topic map read; used as a control instrument for X11.

**Not read**

- `journals/oracle/accuracy/accuracy-ledger.md`
- `journals/oracle/registry/computational-methods.md`, `property-templates.md`, `properties.md`, `observable-bundles.md`, `topology-atlas.md`
- `journals/oracle/laws/generic-dynamics.md`, `residual-definitions.md` lines 1–179
- `journals/oracle/state/born-oppenheimer-levels.md`
- `journals/n-op/build/*` (five pages), `journals/n-op/purpose/purpose-and-scope.md`, `library-landscape.md`, `architectural-principles.md`
- `journals/operator/**` (three pages) — out of unit, frontmatter read only
- `data/diamond-*/`, `data/reference-data/*.csv`, `tools/`

All open-questions frontmatter across all 45 pages was extracted and read (51 declared,
51 found).

## Near-findings rejected

- **The tolerance ledger is incomplete.** Rejected. Enumerated every `τ_`/`δ_`/`ε_`/`σ_` symbol in the corpus (26 distinct) and every one absent from the ledger is a physical time or physics symbol the page itself excludes by name. The ledger is exhaustive over tolerance *names*; only four Default cells are empty, which is X7.
- **The `Environment` record cannot be typed.** Rejected as a finding of mine — declared twice, by `environment-schema` on `crystal-inputs` and `environment-schema-at-the-seam` on `learnable-structure-contract`, and the `UNSEEDED` markers are explicit in the table. Only the *box* over it is undeclared (X15).
- **`Crystal` is undefined**, which breaks every `applicability` signature including the predicate contract I audit. Rejected: declared as `crystal-type`.
- **Obligation 9 names a tag whose meaning does not match its checker.** Rejected: declared as `surrogate-validity-scope`, and the page flags the contradiction inline.
- **The `AxisCoverage` flat index is not reproducible** — `flat-index(axes) = enumerate(product(axes))` needs a total order on each axis's values and an ordinal for `AxisLabel`. Rejected as a separate finding because it is a consequence of X18 (no ordinal rule) rather than an independent gap; noted here because it is the highest-consequence instance, the mask being part of a cache content address.
- **Applicability predicates are stored but not bound to rows.** Folded into X8 rather than reported twice; the storage side (`MerkleDAG[PredicateOps, Atom]`, versioned atom order) is DETERMINED and only the row→root binding is missing.
- **`Import` is not differentiated through but inserts graph nodes** — I looked for a stated mechanism that keeps a pinned `Input` out of the adjoint. `physics-graph` says `Import` inserts "certification-only `ResidualLeaf` nodes", which is a mechanism. Not a gap.
- **The three exports are two, since `dynamics` is unbuilt.** Rejected: `evolver-lowering-spec` declares the whole lowering unwritten and withholds the product verb. Its *scope leak* is X10, which is a different claim.
- **`combineTol` has no stated composition law.** Rejected: `typeclass-alphabet` gives associativity, commutativity, monotonicity and the two admissible instances (maximum-absolute or root-sum-square). Per-instance choice is a declared design freedom, not a gap.
- **`SparseSet` backend selection is unspecified.** Rejected: the threshold ladder is given with concrete numbers (`n ≤ 8`, dense `n ≤ 256`, sparse-over-large, persistent) and fixed at registration.

## By-catch

- `product.md` and `pino-bridge.md` disagree about the fourth return of the single exported call (kernel hash versus `CertEvidence`); recorded as X12 because it blocks typing, but the disagreement itself is a contradiction and belongs to that sweep.
- `formula-registry.md`'s own two tables disagree about whether `applicability` is a manifest field; the field list omits it and the vocabulary table includes it.
- `formula-registry.md` declares a seven-member closed provenance vocabulary (`observable-catalog`, `crystal-structure-prediction`, …); `data/registry-manifest.csv`'s `Source` column holds `S1`–`S5` codes instead, so the "closed vocabulary, so the provenance field is checkable" claim cannot be checked against the table as it stands.
- `formula-registry.md`'s field list names `anchor-class`; the CSV column is `Path`, whose reserved-sense row in `glossary.md` says "the registry column that classified anchors is `anchor-class`, which is what every denial of the old name already called it" — the rename landed in the glossary and not in the data file.
- `named-formulas.md` gives `FormulaRecord` ten fields; `formula-registry.md` gives the manifest nine; the CSV has nine, and the two missing ones (`applicability`, `adjoint-validated`) are the two that certification reads.
- `residual-machinery.md` states "40 of the 134 registry rows carry two bundles" — the CSV parses to 134 data rows, so that count is live and correct as of this reading.
