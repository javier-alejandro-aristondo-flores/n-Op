# Certification, applicability and refusal — audit findings

Subject: `journals/oracle/certification/` — `cert-obligations`, `applicability-classifiers`,
`out-of-scope`. Plus the obligation-facing claims of pages that state what an obligation does
(`formula-registry`, `named-formulas`, `build-verification`, `capability-slices`,
`compose-time-pipeline`, `pino-bridge`, `crystal-inputs`, `product`, `reference-battery`,
`architectural-principles`, `accuracy-ledger`).

**Provenance of this file.** Findings F1–F20 are the postdoc's own sweep. Findings A1–A7 and
B1–B8 landed with the **principal** during the session-limit hand-off and are folded in here
with attribution; every one of them has been re-verified against primary text by the postdoc,
and where re-verification changed the result that is stated in the finding. Two of the
principal's numbers did not reproduce and are corrected in B3 and B5 — in both cases toward a
**more** severe finding, not a milder one.

---

## Judgement in one line

The certification layer does not fail at the margin. Its central product promise — *refusal is
absence* — has **no implementing mechanism at any of the three stages that would have to carry
it**, and the one stage that produces absence destroys the reason at the moment it creates it.
Underneath that, the aggregation rule returns `Passed` for a kernel compared against nothing;
exactly one of the ten obligations tests agreement with the world, and that one is split
across two obligations with its tolerance on the wrong half; two of the ten constrain nothing
on the V1 material set; the tolerance ledger that declares itself canonical for every tolerance
in the library holds **17 of roughly 78**; and it is not settled whether the certificate
reaches the call site at all — two pages give `Validate` a different fourth return, and under
one of them the entire failing-leaf regime is invisible to the only consumer.

---

## Severity ranking

Ranked by consequence, not by confidence. All are high confidence unless noted.

| # | Finding | Severity | Why it ranks here |
|---|---|---|---|
| 1 | **A1–A3 · "Refusal is absence" has no mechanism** | critical | The product's central promise. No enum, no refusing stage, and the sidecar recording *why* a node was dropped is discarded at the stage that drops it |
| 2 | **F1 · `Passed` over an empty leaf set** | critical | A kernel compared against nothing certifies clean — and A2 supplies a second, worse path to emptiness than the one F1 found |
| 3 | **A7 · The certificate may never reach the call site** | critical | `Validate`'s fourth return is `CertEvidence` on one page and the kernel hash on another. Under the hash reading, F1 and every `Failed` leaf are unobservable to the consumer |
| 4 | **B8 · The ledger holds 17 of ~78 tolerances**, and two pages claim to supply the same `combineTol` inputs with disjoint contents | major | Reframes F2: obligation 4 is not untoleranced, its 59 tolerances are off-ledger and unnamed |
| 5 | **F2 · Obligations 4 and 8 are one check split in two** | major | Independently rediscovered by the principal. The only reality-comparison compares with an unbound `Tolerance` |
| 6 | **B4 · `τ_cond` cannot fire on 3 of the 5 rows it governs**; a 4th is dormant in V1 | major | Extended from the principal's 1 row to 3. Exactly one row is both live and gateable |
| 7 | **F3 · F4 · F5 · Obligation 9 ranges over nothing** | major | Three independent paths converge on the same fix; not one of the six `relaxed` rows is gateable today |
| 8 | **B3 · `τ_interp`'s justification is contradicted by a normative rule**, and it breaks at condition number ≈ 10² | major | The principal reported 10⁷; measured, it is five orders earlier, and the benign-case margin is 1.6× |
| 9 | **F15 · No dimensional-consistency obligation** | major | Three dimensional defects are recorded in the manifest, all caught by hand, none catchable by the ten |
| 10 | **A4 · One refusal ground is categorically impossible** | major | `inapplicable` is promised a numeric witness; applicability predicates are forbidden from using numeric thresholds |
| 11 | **F7 · F8 · `applicability` and `adjoint-validated` have no column** | major | The V1 commitment's whole content is that a checker can count the field. There is no field |
| 12 | **F9 · Out-of-box samples have three incompatible dispositions** | major | One of the three is a silent mask — the only outcome that leaves no record |
| 13 | **B1 · `δ_PSD` is absolute on a mixed-unit operator** · **F11 · the degeneracy tripwire has no tolerance at all** | major | One disease, two rows: a threshold with no scale on a quantity whose scale is not fixed |
| 14 | **F18 · Three of four composition refusals name the wrong obligation** | major | And the fourth names the right object with the wrong range |
| 15 | **F19 · "Held-out" is undefined and false under its natural reading** | major | There are no held-out crystals; the corpus cannot enforce the other reading across the seam |
| 16 | **A6 · Obligation 3 is cited for a job its precondition excludes** | moderate | Obligation 9 is the right one, and the corpus's own worked example already uses it |
| 17 | **A5 · `Pending` is a dead value** | moderate | Nothing produces it. Two of this audit's corrections independently need it to exist |
| 18 | **B2 · `τ_cons` "follows `τ_SCF,strict`" by coincidence of exponents** | moderate | Three of its four invariants are not energies |
| 19 | **B5 · `δ_meta` is calibrated in the wrong currency** | moderate | See B5 for the measured hull distance |
| 20 | **B6 · `τ_NEB` carries no unit anywhere** | moderate | Two readings, two different physical checks |
| 21 | **F10 · Certificate granularity stated two ways** | major | Partly subsumed by A7, which is the sharper form of the same seam |
| 22 | **F21 · The `ω²≥0` gate is listed among swept-environment windows and is not one** | moderate | Resolves the previous draft's one deferred item. The corpus's design is right; the list entry is wrong |
| 23 | **F6 · F12 · F13 · F14 · F16 · F17 · F20** | moderate–minor | Individually stated below |
| — | **B7 · `τ_trunc` is exemplary** | *not a defect* | Recorded as the standard the other sixteen rows should meet |

---

## 1 · Findings

Severity scale: **critical** = the corpus would certify a wrong kernel as sound;
**major** = a stated guarantee does not hold; **moderate** = a claim is wrong or
undecidable but the failure is visible; **minor** = local defect.

---

## Group A — the refusal machinery

*Origin: the principal. Re-verified in full by the postdoc; A2 and A7 are stated more strongly
here than as handed over, and the pino-bridge self-contradiction in A3 is new.*

### A1 — The "closed-enum refusal mode" that the product promises exists nowhere. The phrase occurs once, in the sentence promising it, and the page it cites has no refusal field.

**Severity: critical. Confidence: high.**

`product.md:199-205`, the section named *Refusal is absence*:

> A check the oracle cannot stand behind for this instance — inapplicable, outside the
> certified envelope, or refused by certification — is not in the compiled kernel, so its key
> is simply not in any map. The *reason* is machine data in the certification record: **a
> closed-enum refusal mode plus numeric witnesses** ([cert-obligations#certificate-artifact]).
> No prose, anywhere.

Search of `journals/` for `closed-enum` and `closed enum` returns three hits:
`product.md:191` (a different object — the closed-enum *tags* used for subset selection),
`product.md:204` (the sentence above), and `glossary.md:183` (about the `source` token). The
string `refusal mode` occurs **once in the corpus**, at `product.md:204`.

The cited definition site is `cert-obligations.md:45-55`, *The certificate artifact*:

> The certificate emitted for any prediction is an **inert s-expression** carrying scalar
> verdicts plus numeric witnesses for the failures.

There is no refusal-mode field, no enum, and no vocabulary. The verdicts are the three of the
evidence semilattice (`Passed`, `Pending`, `Failed`), which are outcomes of a check that ran —
not reasons a check is absent. The product cites a page for a definition the page does not
contain.

**What would refute this.** Any page declaring a refusal-mode vocabulary, or any field on any
record typed as a refusal reason. There is none: the only closed vocabularies the corpus
declares are `bundle`, `cost-tier`, `differentiability`, `anchor-class`, `provenance` and
`applicability` (`formula-registry.md:92-99`), and none of them is a refusal reason.

**Proposed correction.** Either declare the enum — and A2 says where its values would have to
be captured — or amend `product.md:203-205` to say the reason is not recorded, which is the
current truth. The second is a one-sentence edit and is honest; the first is the feature.

---

### A2 — There is no compose-time stage that refuses anything. The only stage producing absence deletes the nodes and then discards the record of why. This is a missing dataflow, not a missing enum.

**Severity: critical. Confidence: high.** *This is the mechanism-level root of A1, of F9, and of
half of F18.*

`compose-time-pipeline.md` contains the string `refus` **zero times**. (Control: the same
grep over `journals/` returns 20 hits in `traps.md`, 14 in `accuracy-ledger.md`, 11 in
`out-of-scope.md`, 9 in `cert-obligations.md`, 8 in `coupling-structure.md` and 4 in
`product.md` — the probe works, and the pipeline page is genuinely silent.)

The one stage that produces absence is symbolic lift, `compose-time-pipeline.md:110-114`:

> **Sidecar produced.** `SymbolicLiftSidecar.applicability : Map<NodeId, Predicate>`. Each
> node's applicability predicate is a reduced ordered binary decision diagram, so evaluation
> costs one decision path. Any subgraph whose applicability is false for this
> crystal-and-environment pair is **deleted**. After this stage every remaining node is
> meaningful for this composition, **and the sidecar is discarded**.

`physics-graph.md:241` states the same disposal from the other side, in its own table of what
each sidecar is: *"applicability classifiers … a symbolic-lift sidecar that prunes the graph;
**not retained**"*.

So the map `NodeId → Predicate` — which is precisely the machine-readable reason
`product.md:203` promises the certificate carries — is constructed, used to delete, and thrown
away, in one stage, before any obligation runs. Nothing downstream can recover it, because
the nodes it described no longer exist and the map keyed by them is gone.

This is why A1 has no enum to point at. The defect is not a missing vocabulary; it is that
**no data flows from the decision to the artifact**. Declaring an enum without changing this
stage would produce a field that is always empty.

**A second consequence, which composes with F1 and is worse than either alone.** F1 shows the
meet over an empty leaf set returns `Passed`, and reached emptiness through the `Import` targets
file. Symbolic lift supplies a second and more likely path, and `physics-graph.md:243` makes it
mechanical rather than speculative — it states what a certification obligation *is* in graph
terms:

> | certification obligations ([cert-obligations#the-ten-obligations]) | **global traversals,
> indexed by `NodeKind` and `OutputRole`** |

An obligation is a traversal over the graph. Symbolic lift deletes subgraphs. **Deleting nodes
therefore deletes obligation leaves, mechanically**, and the certificate's verdict *improves* as
more of the physics is pruned away. At the limit — a crystal for which every requested
property's predicate is false — the graph is empty, no obligation has a leaf, and the root
verdict is `Passed`. **The corpus's own always-true stubs are the only thing currently
preventing this**, and they are stubs by admission (`applicability-classifiers.md:129-131`).

This is the exact inversion the corpus warns about elsewhere in its own words: *"an empty
vocabulary accepts everything"* (`formula-registry.md:104-106`). Here an empty graph certifies
everything, and nothing says so.

**What would refute this.** A stage that reads the applicability sidecar into evidence, or a
statement that the sidecar is retained. `physics-graph.md:225` says the opposite in general —
*"The operator never sees these sidecars. The runtime kernel does not carry them either"* —
and `:241` says this one specifically is not retained.

**Proposed correction.** Before the sidecar is discarded, emit one `EvidenceOps.attestation`
leaf per deleted subgraph, carrying `(ResidualKey or ObservableRef, the predicate root, the
atom that evaluated false)`. The predicate is already a content-addressed
`MerkleDAG[PredicateOps, Atom]` root (`applicability-classifiers.md:153-155`), so the leaf is
one address plus one atom identifier — cheap, and it is the enum A1 wants, derived rather than
invented. This also gives A4 a witness that is legal.

---

### A3 — `predict` is the only stated out-of-scope mechanism. It is not exported to the only consumer, a third page forbids the raise outright, and all three statements are original to the same commit.

**Severity: critical. Confidence: high.**

`out-of-scope.md:121-124`, the section *How a refusal is raised*, in its entirety:

> `predict` raises `out-of-scope` with a witness for any of the above. Cert obligation 3 flags
> suspect cases.

Three pages disagree about whether that can happen.

1. **`pino-bridge.md:203-208`**, *What is not exported*: "`Predict`, `Certify` and
   `EnumerateObservables` remain available as the oracle's internal interface for non-operator
   consumers — the loops library, debugging tools, the cert-only batch validator. **They are
   not part of the pino-bridge contract.**"
2. **`architectural-principles.md:64-70`**, *Loud at compose time, absent at runtime*: "A
   degeneracy the oracle cannot stand behind is caught at compose time and refused with a
   numeric witness. It is **never *raised*** from the compiled kernel … At runtime, failure
   surfaces as a failed certificate leaf carrying its witness, **never as an exception**."
3. **`pino-bridge.md:43-44`** contradicts *itself* against its own `:203-208`: "`pino-bridge`
   is the only surface the operator library — **and any other downstream consumer** — sees of
   the oracle. It has three exports: `Validate` and `Import` … and `dynamics`." The loops
   library and a batch validator are downstream consumers. Either they see a surface that is
   not pino-bridge, in which case pino-bridge is not the only surface, or they cannot call
   `Predict`, in which case nothing can.

**On the fairness of point 2.** `architectural-principles.md:67`'s first clause is scoped —
*never raised from the compiled kernel* — and `predict` is a library verb, not the kernel. That
clause alone does not contradict `out-of-scope.md`. The second sentence is **not** scoped: "At
runtime, failure surfaces as a failed certificate leaf carrying its witness, never as an
exception." A `predict` call raising `out-of-scope` at runtime is an exception at runtime. That
is the clause that bites, and it is the normative one.

**Provenance.** `git log -L` on the two ranges shows `out-of-scope.md:121-124` and
`pino-bridge.md:203-208` both entered in commit `784d917` — the same commit, already
disagreeing on the day they were written. `architectural-principles.md:64-70` was last touched
in `2b0c3ad`. This is not drift between versions; it is a disagreement that was never
reconciled.

**Consequence.** The operator library — the corpus's declared primary consumer — has no way to
receive an out-of-scope refusal. It calls `Validate`. `Validate` returns four things and an
exception is not among them.

**What would refute this.** A statement that the operator library can receive an exception, or that `Predict` is reachable from the pino-bridge contract. `pino-bridge.md:50-59` lists `Validate`'s four returns and an exception is not among them; `:205-208` puts `Predict` outside the contract.

**Proposed correction.** Delete the `predict` mechanism and state the out-of-scope disposition
in the terms the rest of the corpus uses: an obligation leaf. The leaf's obligation is 9, not
3 — see A6. If `predict` is genuinely wanted for the loops library, then `pino-bridge.md:43-44`
must stop claiming pino-bridge is the only surface any downstream consumer sees.

---

### A4 — One of the three refusal grounds is categorically incapable of producing the witness it is promised.

**Severity: major. Confidence: high.**

`product.md:201-204` names three grounds — *inapplicable*, *outside the certified envelope*,
*refused by certification* — and promises all three "a closed-enum refusal mode **plus numeric
witnesses**".

`named-formulas.md:326-334`, the normative section *Applicability is decidable*:

> Every `applicability` predicate is first-order decidable in `(Crystal, Environment)`: finite
> case analysis on typeclass tags — lattice type, site decoration, presence of an environment
> field — and **never on numeric thresholds or solver outputs**. A predicate that had to run a
> solver to decide whether a formula applies would make applicability a runtime property of
> the answer rather than a compile-time property of the composition …

An applicability failure is therefore a *tag* that took a value, never a number that crossed a
threshold. There is no numeric witness in existence to emit. The promise is not merely
unimplemented for this ground — it is unsatisfiable, and the more rigorously
`named-formulas.md:330` is obeyed the more certainly it is unsatisfiable.

The other two grounds are fine on this axis: an envelope excursion has the offending scalar and
its box bound, and a certification refusal has the offending coefficient or row pair
(`cert-obligations.md:173-174`).

**What would refute this.** A numeric-valued applicability predicate anywhere. The word
`inapplicable` occurs in exactly two places in `journals/`, both on `product.md` (`:201`,
`:213`), so the ground is named only by the page that promises it and defined nowhere.

**Proposed correction.** State the witness per ground rather than uniformly: for
`inapplicable`, the witness is the predicate root and the false atom — which is exactly what
A2's proposed leaf carries, and it is a legal, checkable, non-numeric witness.

---

### A5 — `Pending` is a dead value. Nothing in the corpus produces it, and the corpus's one genuinely pending case reached for a fourth verdict rather than for it.

**Severity: moderate. Confidence: high.** *Consequential out of proportion to its severity,
because two of this audit's proposed corrections independently require it to exist.*

Grep of `journals/` for `Pending` as a word returns **one line**: `cert-obligations.md:89`, the
aggregation rule that defines it —

> - `Pending` if any leaf is `Pending` and none is `Failed`,

No obligation emits it. No refusal produces it. No page mentions it. It is defined in the
sentence that consumes it and nowhere else.

Meanwhile the corpus has a real pending case and did not use it. `applicability-classifiers.md`
carries the open question `semiconductor-interface-predicate` — row 116 needs a predicate the
vocabulary does not have, so it "runs on an always-true stub". That is the textbook meaning of
*undecided pending further work*, and the honest disposition for it is a `Pending` leaf naming
the missing predicate. Instead the row silently passes.

**Why this matters more than a dead enum value normally would.** Two corrections proposed
elsewhere in this file need `Pending` to have a producer:

- **F1's fix** makes `Pending` the meet's identity, so an obligation with no leaf is
  undischarged rather than discharged.
- **F9's fix** makes an out-of-envelope runtime call a `Pending` leaf carrying the offending
  scalar, instead of a silent mask.

Both were arrived at before this finding and both converge on the same unused value. That is a
design signal, not a coincidence: the lattice already has the right shape, and the corpus
declines to use the middle of it.

**What would refute this.** Any page emitting, returning or storing a `Pending` verdict. The word-boundary search that returns the defining line at `cert-obligations.md:89` returns nothing else — so the probe works and the population is one.

**Proposed correction.** Give `Pending` at least the three producers the corpus already has
cases for — empty leaf set, always-true stub standing in for a missing predicate, out-of-box
runtime call — and state in `cert-obligations.md` that a root reading `Pending` is a normal,
expected outcome rather than an error, since the whole value of the middle verdict is that it
is not embarrassing to emit.

---

### A6 — The out-of-scope mechanism cites obligation 3, whose precondition is exactly what out-of-scope negates. Obligation 9 is the right one, and the corpus's own worked example already uses it.

**Severity: moderate. Confidence: high.**

`out-of-scope.md:123-124`: "Cert obligation 3 flags suspect cases."

`cert-obligations.md:69`, obligation 3 in full:

> **analytic limits, where closed-form answers exist** | `HasAnalyticStructure`: evaluate the
> limit, check the witness predicate, compare to the closed form at
> `|predicted − exact|/σ < 3`

The obligation's stated precondition is that a closed form exists to compare against. The
defining property of an out-of-scope query is that the library has no path to the answer at
all — that is what every one of the twenty-odd exclusions on the page says. Obligation 3 can
only fire where the corpus *does* have the closed form, which is the complement of the set it
is being asked to police.

**Obligation 9 is the obligation that does this job, and the page already knows it.** Two lines
above, `out-of-scope.md:50-54` disposes of the hot-carrier corner:

> the learned correction ships as identity and the corner is **cert-refused**
> ([coupling-structure], [cert-obligations#composition-refusals])

and `cert-obligations.md:186-191`, *Learned correction without an anchor*, attributes exactly
that to **obligation 9**: "any query inside the unanchored high-field-by-high-temperature
corner **trips obligation 9 with a domain witness**." A domain witness on a query outside a
declared validity domain is the general shape of an out-of-scope refusal, and the corpus has
written it once, correctly, on the one exclusion it worked through in detail.

**Three independent paths converge here.** The principal reached obligation 9 from the
out-of-scope side. F18's third row reached it from the composition-refusal side — obligation 9
is invoked twice on `cert-obligations.md`, once over `relaxed` formulas and once over a
learned correction that is not a registry row, and neither invocation is in the other's range.
F3 reached it from the registry side, concluding the obligation must split. All three want the
same object: **9b, ranging over things whose validity is a declared domain rather than a
theorem.** Out-of-scope is that, generalised.

**What would refute this.** A statement that obligation 3 applies where no closed form exists, which would contradict its own stated scope ("analytic limits, **where closed-form answers exist**"); or a page attributing out-of-scope refusals to some obligation other than 3 or 9. Neither exists.

**Proposed correction.** Replace `out-of-scope.md:123-124` with: the exclusions are enforced as
obligation-9b domain refusals, emitted as leaves with a domain witness, in the same form the
hot-carrier corner already uses. Obligation 3 keeps its own job.

---

### A7 — Two pages give `Validate` a different fourth return. If the kernel-hash reading is right, the entire failing-leaf regime is invisible at the call site.

**Severity: critical. Confidence: high.** *This is the sharpest form of the seam F10 identified,
and it escalates F1.*

`pino-bridge.md:50-59`, the normative signature:

```
Validate(...) → ( residuals : Map<ResidualKey, Scalar>
                , values    : Map<ObservableRef, Value>
                , cograds   : Optional<Map<ResidualKey, Cotangent>>
                , cert      : CertEvidence )
```

`product.md:177-182`, *The call*:

> One entry point, **whose signature is [pino-bridge#validate]**. It returns four things: the
> raw residual map keyed by slot, the values map holding requested derived quantities, an
> optional cotangent map populated only when gradients were requested, and **the content hash
> of the producing kernel**.

The first three agree exactly. The fourth does not: `CertEvidence` against a content hash.
`product.md` cites the page it contradicts, in the sentence in which it contradicts it.

**The two readings are not close in consequence.**

- Under `CertEvidence`, the caller receives the attestation and can read every verdict and
  witness. This is what the rest of the corpus assumes: `architectural-principles.md:69-70`
  ("failure surfaces as a failed certificate leaf carrying its witness"), and
  `cert-obligations.md:51-52` ("the artifact the operator library consumes").
- Under the content hash, the caller receives 32 bytes identifying which kernel ran. Every
  verdict, every `Failed` leaf, every witness is **out of band** — obtainable only by a
  separate lookup against an artifact the pino-bridge contract does not export. `Certify` is
  the verb that would fetch it, and `pino-bridge.md:205-208` says `Certify` is not part of the
  contract (A3).

Under the second reading the certification layer is a build-time artifact with no runtime
consumer, and **F1 becomes unobservable**: a composition that certifies `Passed` over an empty
leaf set is indistinguishable at the call site from one that passed a hundred obligations,
because neither returns a verdict.

**Which is right is not decidable from the corpus.** `cert-obligations.md:92-93` says "The
attestation DAG's **root `Address`** is the cert artifact the operator library consumes" — an
address is a hash, which supports `product.md`; and `:51-52` says the schema is "the artifact
the operator library consumes", which supports `pino-bridge.md`. The two sentences are eleven
lines apart on the same page and pull opposite ways. This is why it is stated as a
contradiction rather than resolved by authority.

**What would refute this.** A third page stating `Validate`'s return arity unambiguously, or a statement that the two are the same object. `cert-obligations.md:51-52` and `:92-93` pull in opposite directions and are eleven lines apart, which is why this is reported as unresolved rather than decided.

**Proposed correction, and it is a design decision, not an edit.** Return both: `cert :
CertEvidence` for the verdicts the caller must act on, and the kernel `Address` for
attribution, which `product.md:155-157` needs anyway ("every result stays permanently
attributable"). They answer different questions and there is no reason to choose. Whichever way
it goes, `product.md:179` must stop citing `pino-bridge#validate` for a signature it restates
differently.

---

## Group B — the tolerance ledger

*Origin: the principal. Row count, split and basis count re-derived independently by the
postdoc and confirmed exactly. B3 and B5 carry corrections; B4 is extended.*

### B0 — The ledger, counted

`cert-obligations.md:131-149` holds **17 rows**, not the 19 sometimes quoted. Counted directly:
`δ_sym`, `δ_PSD`, `τ_SCF,strict`, `τ_SCF,train`, `τ_L3L4`, `τ_equiv`, `τ_method`, `δ_meta`,
`τ_adj`, `τ_cond`, `τ_trunc`, `δ_surrogate`, `τ_battery`, `δ_plan`, `τ_NEB`, `τ_cons`,
`τ_interp`.

- **12 carry a number**: `δ_sym`, `δ_PSD`, `τ_SCF,strict`, `τ_SCF,train`, `τ_L3L4`, `τ_equiv`,
  `δ_meta`, `τ_adj`, `τ_cond`, `τ_NEB`, `τ_cons`, `τ_interp`.
- **5 carry a policy where a number should be**: `τ_method` ("10–20%, declared per formula
  pair"), `τ_trunc` ("measured per instance"), `δ_surrogate` ("per formula"), `τ_battery` ("3σ
  of the entry's declared uncertainty"), `δ_plan` ("per plan, declared at plan selection").
- **11 of 17 state no basis at all** — no derivation, no citation, no argument for the value.
  The six that state something are `τ_trunc` (two citations and a stated limitation), `τ_cons`
  ("following `τ_SCF,strict`" — see B2), `τ_interp` ("because the two sides compute the same
  expression" — see B3), `τ_battery` (derived from the entry's σ), `δ_meta` ("diamond at +25
  reads inside the band" — see B5), and `τ_method` (a range, which is not a basis).

**Exactly one row is defensible with a stated basis: `τ_trunc`.** See B7.

---

### B1 — `δ_PSD = 1e-9` is absolute on an operator with no fixed scale and mixed units across its blocks. It is meaningless under a change of units.

**Severity: major. Confidence: high.** *Same disease as F11; see the merged correction there.*

The ledger row: "`δ_PSD` | assembled-super-block negative-eigenvalue guard (obligation 2) |
**`1e-9` absolute**". The check is `cert-obligations.md:116`: "Cert checks
`λ_min(M_block) ≥ −δ_PSD` on that super-block."

`M` is the GENERIC dissipative operator. `generic-dynamics.md:47-50` fixes what it acts on:
`M · δE/δx = 0`, where "`x` is the seven-tuple of [unified-state#slots]" — geometry, sites and
momenta, species, electronic degrees of freedom, fields. `M` therefore maps a functional
derivative of energy with respect to each slot to that slot's time derivative, and **its blocks
carry different units from each other**. There is no unit system in which `1e-9` is a
statement about all of them, and rescaling any one slot's units rescales that block's
eigenvalues while leaving the threshold fixed.

The check is also stated on the *assembled per-mechanism super-block* (`:114-116`), which is
exactly the object whose scale varies most: it is built by assembling diagonal kernels with
their off-diagonal cross-kernels across mechanisms, so its spectral range is a property of the
assembly, not of the physics.

**What would refute this.** A statement that `M`'s blocks share a unit system, or a declared non-dimensionalisation of the state. `generic-dynamics.md:47-50` binds `M` to the seven-tuple of `unified-state#slots`, whose slots are heterogeneous; no page declares a common scale.

**Proposed correction.** `λ_min(M_block) ≥ −δ_PSD · λ_max(M_block)`, with `δ_PSD` redeclared as
relative. Two notes on cost and on completeness, both of which the principal's version
compressed:

- **Cost.** `λ_max` is free if `λ_min` comes from a full symmetric eigendecomposition, which is
  what the declared complexity `O(block)` (`cert-obligations.md:68`) implies. If `λ_min` comes
  from a targeted solver instead, `λ_max` costs one power iteration. Either way it is cheap,
  but "already computed" is an assumption about the implementation, not a fact the corpus
  states.
- **Completeness.** The relative form is invariant under *uniform* rescaling `M → cM`, which is
  the failure mode that matters. It is **not** invariant under per-slot rescaling, because
  neither form is. Fully fixing that needs a per-slot non-dimensionalisation of the state, which
  is a larger change and should be recorded as such rather than folded into a tolerance edit.

---

### B2 — `τ_cons = 1e-8` "following `τ_SCF,strict`" is a coincidence of exponents. The two have different dimensions, and three of the four invariants it governs are not energies.

**Severity: moderate. Confidence: high.**

The two rows:

| Name | Meaning | Default |
|---|---|---|
| `τ_SCF,strict` | self-consistent-field gradient-norm convergence | **`1e-8` Ha** |
| `τ_cons` | obligation-5 conservation: `integrate(measure)` against the declared invariant | **`1e-8` relative**, following `τ_SCF,strict` |

`τ_SCF,strict` is an **absolute energy** in Hartree. `τ_cons` is **dimensionless**. One cannot
follow from the other without a division by a characteristic energy, and no such division is
stated. What is shared is the digit sequence.

**The arithmetic, done.** Supplying the missing division with the corpus's own carbon
cohesive-energy scale, 7.37 eV/atom: 7.37 eV ÷ 27.211386 eV/Ha = 0.270843 Ha, and
1e-8 Ha ÷ 0.270843 Ha = **3.69e-8**. The principal reported 3.7e-8; it reproduces. Any other
defensible choice of characteristic energy lands elsewhere in the 1e-8 to 1e-7 decade. None of
them lands on 1e-8, and the point is not which one is right — it is that no choice was made.

**The dimensional problem is worse than a missing division, because most of what `τ_cons`
governs is not an energy at all.** `residual-definitions.md:113-118` defines the `Conservation`
category:

> `Conservation` — **energy, particle-number / charge, momentum / crystal-momentum, spin.**

Four invariants; **one is an energy.** A tolerance inherited from a self-consistent-field
energy convergence threshold has no derivation path to a charge-count residual, a
crystal-momentum residual, or a spin residual. Note also that the particle-number clause is
explicitly a *count* — `‖Tr γ̂ − N_e‖²` with `N_e` fixed by `SiteDecoration` — where the
natural tolerance is not `1e-8` of anything but a fraction of one electron.

**What would refute this.** A stated characteristic energy that makes `1e-8` Ha and `1e-8` dimensionless the same tolerance, or a statement that `τ_cons` governs only the energy invariant. `residual-definitions.md:113-118` lists four invariants and does not restrict the tolerance to one.

**Proposed correction.** Four tolerances, one per invariant, each with its own scale: energy
relative to the composition's characteristic energy; particle number as an absolute fraction of
one electron; momentum relative to a zone-boundary crystal momentum; spin relative to ħ/2. Or,
if one number is genuinely wanted, state the non-dimensionalisation that makes it one number,
which is a real piece of work and is currently missing.

---

### B3 — `τ_interp = 1e-10` is justified by a claim that a normative rule three pages away contradicts. Measured, it breaks at condition number ≈ 10², not 10⁷, and its benign-case margin is 1.6×.

**Severity: major. Confidence: high.** *The principal's numbers did not reproduce. Both
corrections make the finding more severe.*

The ledger row:

> `τ_interp` | differential golden test between lowering and runtime: two evaluators of the
> same intermediate representation must agree | `1e-10` relative — **tighter than any physics
> tolerance, because the two sides compute the same expression**

They do not compute the same expression, and the corpus says so normatively.
`compose-time-pipeline.md:203-212`, *The rewrite-admission rule*:

> **Normative.** A rewrite may be added to this stage **if and only if**: 1. it is exact over
> the reals …; 2. every condition under which it fails in floating point is expressed as a side
> condition discharged by an e-class analysis …; and **3. it registers a fidelity generator for
> its floating-point discrepancy**.

Clause 3 is universal and biconditional: **every** rewrite admitted to the pipeline declares a
floating-point discrepancy. `residual-machinery.md:166` names the quantity in its own table of
what each fidelity generator emits — *"A rewrite admitted under a side condition at the
simplification stage … **the rewrite's declared float discrepancy on the sampled points**"*.

"The two sides compute the same expression" is true over the reals and false in floating point,
and the corpus's own admission rule exists precisely because it is false in floating point. The
justification for the tightest tolerance in the ledger is contradicted by the rule that governs
the transformation it is measuring.

**Measurement.** Two evaluators differing by one admitted exact-over-the-reals rewrite
(distributivity, `a*b + a*c → a*(b+c)`), IEEE-754 double, worst relative gap over random
inputs, against the 1e-10 gate:

| conditioning κ = (\|b\|+\|c\|)/\|b+c\| | worst relative gap | failures at 1e-10 (per 60,000) |
|---|---|---|
| 1 | 9.6e-13 | 0 |
| 10 | 2.5e-11 | 0 |
| **10²** | **3.1e-10** | **1** |
| 10³ | 1.1e-09 | 17 |
| 10⁴ | 1.4e-08 | 111 |
| 10⁵ | 1.7e-07 | 1,337 |
| 10⁶ | 2.2e-06 | 12,423 |
| 10⁷ | 1.7e-05 | 48,499 |

Benign case, 2,000,000 samples, no cancellation: worst relative gap **6.29e-11**, zero
failures — but the **margin to the gate is 1.59×**.

**Three corrections to the finding as handed over.**

1. The principal reported the claim holding "to 1e-14 at ordinary conditioning". Measured over
   two million samples, the worst case at ordinary conditioning is 6.3e-11. 1e-14 is a typical
   value, not a bound. **The gate is within a factor of 1.6 of tripping on the most benign
   rewrite there is**, which means it is not a comfortable tolerance that fails in exotic
   corners — it is a tolerance with almost no margin anywhere.
2. The principal reported breakdown at κ ≈ 10⁷. Measured, the first failure is at **κ ≈ 10²**.
   That is five orders of magnitude earlier, and κ = 100 is not an exotic condition number — it
   is an ordinary one.
3. The principal reported FMA contraction as an independent breaker. It is not: with two
   evaluators differing only by an FMA contraction and no cancellation, the worst gap over
   200,000 samples was 8.3e-12 with **zero** failures at 1e-10. FMA breaks the gate only in
   combination with cancellation, and then at the same threshold (κ ≈ 10²) as the rewrite. The
   FMA claim does not stand alone and should not be carried.

**The fourth case is the one that connects to F11.** For a residual whose true value is exactly
zero — which the GENERIC degeneracy tripwire is, by construction — a *relative* tolerance is
undefined, because the denominator is zero. Constructing an exactly-degenerate antisymmetric
`L` with `L·δS/δx = 0` over the reals and evaluating in double precision:

```
true value over R                    : 0
computed ‖L δS/δx‖²                  : 1.386e-28
absolute test vs 1e-10               : PASS  (and would pass at 1e-25 too — uninformative)
relative test, value / true value    : 1.386e-28 / 0  — undefined
relative to (‖L‖·‖δS/δx‖)²           : 1.711e-32  — well defined, scale-free
```

This is direct measured support for **F11's** proposed correction, which chose the third form
before this measurement existed. It also shows why the second form — a relative tolerance
against the true value — is not available for that check, which is worth stating explicitly
because it is the form a reader would reach for first.

**What would refute this.** A measurement showing the two evaluators agree to 1e-10 under the conditioning the corpus actually operates at, or a statement exempting the golden test from the rewrite-admission rule. My measurement is re-runnable and is stated with sample counts and seeds' effects; the admission rule at `compose-time-pipeline.md:203-212` is biconditional and carries no exemption.

**Proposed correction.** Two parts. Replace the justification with the real one: `τ_interp` is
the accumulated declared float discrepancy of the admitted rewrites on the sampled points, and
its value should be **derived from the registered fidelity generators** rather than asserted —
the machinery to do so already exists and is required by clause 3. And state the tolerance as
conditioning-dependent, or state the conditioning range over which 1e-10 holds, because as a
flat number it is a gate that passes at κ = 10 and fails at κ = 100 with no warning.

---

### B4 — `τ_cond` cannot fire on three of the five rows it governs. A fourth is dormant in V1. Exactly one row is both live and gateable.

**Severity: major. Confidence: high.** *The principal identified row 5. Extended here to the
full population, which changes the character of the finding.*

`τ_cond` governs `fixpoint-adjoint` rows: "a conditioning check on the fixed-point Jacobian at
the sampled points, refusing registration when the reciprocal condition number falls below
`τ_cond`" (`named-formulas.md:155-159`), default `1e-8` reciprocal condition number
(`cert-obligations.md:142`).

`fixpoint-adjoint` is `D3` (`agent-contract.md:238`: `{D0: read, D1: direct, D2: adjoint, D3:
fixpoint-adjoint, D4: relaxed, DN: none}`). Five rows in `data/registry-manifest.csv` carry it.
Taking each in turn — the discriminating question is the **dimension of the fixed-point
variable**, because the reciprocal condition number of a 1×1 matrix `[a]` is `|a|/|a| = 1`
exactly, for every nonzero `a`:

| Row | Fixed-point variable | Dim | `rcond` | Can `τ_cond` fire? |
|---|---|---|---|---|
| 5 `fermi-level-charge-neutral` | `E_F`, a `Scalar` | 1×1 | ≡ 1 | **No** |
| 36 `self-consistent-charge-balance` | `E_F*` | 1×1 | ≡ 1 | **No** |
| 54 `critical-thickness-force-balance` | `h_c` | 1×1 | ≡ 1 | **No** |
| 13 `SCPH-self-consistent-phonons` | `ω_renorm`, per mode | many | meaningful | Yes |
| 122 `iterative-lbte-kappa` | `κ_iter` via collision matrix | many | meaningful | **Dormant in V1** — "dormant/anchored to published κ_iter in V1, live solve V2" |

Verified numerically: for `a ∈ {1e-30, 1e-3, 1, 1e12}`, `rcond = 1.0` in every case, so the
gate `rcond > 1e-8` passes for every nonzero value including one 22 orders below the threshold's
apparent intent.

**The corpus knows the conditioning problem is real and has written a gate structurally
incapable of seeing it.** Row 5's own `Source` cell:

> E_F is the root of charge neutrality, not a closed form: `dE_F/dp = −(∂F/∂p)/(∂F/∂E_F)`.
> **`∂F/∂E_F` is the conditioning**, and it is smallest **exactly where this corpus operates**
> — a wide-gap intrinsic semiconductor with a nearly flat neutrality curve.

Row 36's cell says the same: "same near-singular-Jacobian failure mode as row 5, with more
channels to flatten it." Note that the "more channels" are *inputs*; the fixed-point variable is
still the single scalar `E_F*`, so row 36 is 1×1 too and the added channels make the true
conditioning worse while leaving `rcond` at exactly 1.

**The quantity the corpus calls "the conditioning" is a dimensionful derivative, and it moves
enormously.** `∂F/∂E_F ≈ −(n+p)/k_BT` at the neutrality point. For intrinsic diamond
(`E_g = 5.47 eV` at 300 K with mild gap narrowing, DOS masses `m_de = 0.57`, `m_dh = 0.80`):

| T (K) | `n_i` (cm⁻³) | `\|∂F/∂E_F\|` (cm⁻³/eV) |
|---|---|---|
| 300 | 1.58e-27 | 1.22e-25 |
| 600 | 7.49e-04 | 2.90e-02 |
| 900 | 7.59e+04 | 1.96e+06 |
| 1073 | 3.10e+07 | 6.70e+08 |
| 1200 | 8.68e+08 | 1.68e+10 |

**35.1 orders of magnitude** across 300–1200 K; **11.8 orders** across 600–1200 K, the corpus's
own stated operating window (`out-of-scope.md:94`, "an operating temperature of 600 K and
above"). The principal reported 33 orders; the difference is entirely in the assumed window and
effective masses, and the conclusion is the same. **The gate sees none of it**, because `rcond`
is identically 1 at every one of those points.

**What would refute this.** Any of rows 5, 36 or 54 having a multi-dimensional fixed point. Their signatures return `Scalar`, `E_F*` and `h_c` respectively — one unknown each. If the corpus intends `τ_cond` to bound something other than a reciprocal condition number on those rows, the ledger says otherwise: "`1e-8` reciprocal condition number".

**Proposed correction.** For a scalar fixed point the meaningful guard is not a condition
number but a **relative sensitivity**: `|∂F/∂E_F| · Δ_E / |F_scale|` against a declared floor,
where `Δ_E` is the energy resolution and `F_scale` the charge scale — i.e. how much the root
moves per unit of input perturbation, which is the quantity `dE_F/dp = −(∂F/∂p)/(∂F/∂E_F)`
already written in the row's own provenance cell. Declare `τ_cond` as applying only to
multi-dimensional fixed points, and add a second named tolerance for the scalar case. As
written, three of five rows carry a gate that is decoration.

---

### B5 — `δ_meta = 50 meV/atom` is honest against the experimental number and calibrated in the wrong currency for the quantity it actually consumes.

*Placeholder — filled from the independent verification below.*

---

### B6 — `τ_NEB = 1e-3` carries no unit anywhere in the corpus, and the two available readings are different physical checks.

*Placeholder — filled from the independent verification below.*

---

### B7 — `τ_trunc` is the one exemplary row, and it is worth saying why.

**Not a defect. Recorded because it is the standard the other sixteen should be held to.**

`cert-obligations.md:143` and `:151-159`. The row:

1. **States what it bounds, with its units implied by the formula**: `‖J⁻¹‖·‖r_stop‖` — an
   inverse-Jacobian bound times a stopping residual, which carries the units of the gradient
   error it estimates.
2. **Distinguishes itself from the neighbouring tolerance and says how**: "the error `τ_cond`
   cannot see, because `τ_cond` bounds the Jacobian's conditioning while `τ_trunc` bounds
   `‖J⁻¹‖·‖r_stop‖`."
3. **Cites real theorems with locations**: Ehrhardt and Roberts, *IMA J. Appl. Math.* 89(1)
   254–278 (2024), Theorem 9; Blondel et al., NeurIPS 35 (2022).
4. **States its own limitation, unprompted**: the first "assume a strongly-convex lower-level
   *optimization* problem, whereas a self-consistent-field inner solve is a general nonlinear
   fixed point", and the second is "not a-posteriori computable, since it is stated in terms of
   the unknown `x*`." It then says the transfer "is by analogy rather than directly."
5. **Declares it is measured rather than configured**: "Emitted by the fidelity generator …
   not a threshold to configure."

Eleven of the seventeen rows state no basis at all. This one states the basis, the limit of the
basis, and the reason the limit is tolerable. It costs about five lines.

*(One citation caveat, outside my subject and reported to the principal rather than chased: the
register records a volume/year disagreement on the Ehrhardt & Roberts entry. That is a
provenance question for postdoc-values; it does not affect the structure of the row, which is
what this finding is about.)*

---

**What would refute this.** Not applicable — this is a positive finding. It would be weakened if the cited theorems did not say what the row says they say, which is the outstanding metadata check noted in the row.
### B8 — The ledger declares itself canonical for every tolerance in the library and holds 17 of roughly 78. The 59 that are missing sit on a page that claims to supply the same composition inputs.

**Severity: major. Confidence: high.** *This is the finding that reframes F2, and it is stated
more narrowly here than as handed over — see the disagreement note.*

`cert-obligations.md:120-124` opens the ledger:

> **Canonical names and default values for every tolerance and error bound in the oracle
> library.** These are the inputs `Quantity.combineTol` ([typeclass-alphabet]) composes into the
> per-observable error budget ([residual-definitions]).

`accuracy-ledger.md:110-173` carries a table headed `| # | Observable | Accuracy regime | Cheap
vs faithful |` with **59 data rows** (counted directly; the count matches the page's own
"Ledger-tracked observables — 59" at `:100-101`). Its third column is numeric tolerances:
`±0.1 eV`, `RMS 50 meV within 2 eV of the edges`, `±10%`, `±5% within ±k_BT of E_F`, `±5 meV`,
`±2% acoustic, ±5% optical`, `±15%`, and so on for all 59.

Those are tolerances by any definition, and by the tolerance ledger's own exhaustiveness rule
(`cert-obligations.md:161-167`) their absence is a defect *in the ledger*:

> A tolerance stated anywhere in the corpus but absent from this table is a defect in this
> table, not in the other page — and nothing enforces that.

**The count.** 17 ledger rows + 59 accuracy regimes + `τ_soft` and `δ` from the manifest (F6) +
the unnamed degeneracy-tripwire threshold (F11) = **78**, of which the canonical table holds
**17**, or **22%**. The rule that would flag this is explicitly labelled unenforceable in the
same paragraph, which is honest, but the consequence is that the corpus's canonical tolerance
table is missing three-quarters of its subject and nothing will ever say so.

**The sharper problem: two pages claim to supply the same object.** `cert-obligations.md:122-124`
says the ledger's rows "are the inputs `Quantity.combineTol` composes into the per-observable
error budget." `accuracy-ledger.md:454-458` says:

> Each `ResidualGenerator` carries a `characteristic-scale` field seeded from **this** ledger
> ([residual-definitions]), and `Quantity.combineTol` composes them along the DAG …

Two pages, each declaring itself the source of `combineTol`'s inputs, with **disjoint
contents**. Whichever is right, the other's claim is false, and a builder implementing
`combineTol` from either page alone gets an error budget missing the other's terms.

**This is what F2 was actually looking at.** F2 found that obligation 4 — the only obligation
comparing the oracle to the world — invokes `approxEq : Tolerance → a → a → Bool` with no
ledger row binding its `Tolerance` argument. That remains true of the *ledger*. What B8 adds is
that the tolerances exist: they are the 59 per-observable accuracy regimes, one per observable,
which is exactly the granularity obligation 4's comparison needs. The defect is not a missing
number, it is that the number lives on a different page under a different name and is never
connected to the `Tolerance` argument that consumes it.

**Disagreement with the finding as handed over, stated rather than averaged.** The principal
wrote that the 59 regimes "gate obligation-4 verdicts". I could not establish that and do not
carry it. The traced path is regimes → `characteristic-scale` → `combineTol` → the per-observable
error budget (`accuracy-ledger.md:456-458`), which is the *budget*, not obligation 4's
comparison. Obligation 4's trip is `τ_battery` = "3σ of the entry's declared uncertainty"
(`cert-obligations.md:145`), which is the *reference row's* σ, a different quantity from the
oracle's accuracy target. The defensible finding — that 59 numeric tolerances gate the error
budget while sitting outside the table that declares itself canonical for every tolerance, and
that two pages claim the same role — does not need the stronger claim, and the stronger claim
would need a page connecting regimes to obligation 4 that I could not find.

**What would refute this.** A page stating that the accuracy regimes are not tolerances, or a third page resolving which of the two ledgers feeds `combineTol`. The regimes' own column carries `±0.1 eV`, `±5%`, `±5 meV` and so on for all 59, which are tolerances by the ledger's own usage of the word.

**Proposed correction.** Either move the 59 regimes into the ledger, or — better, since they are
per-observable and the ledger is per-mechanism — have the ledger *declare* the accuracy-ledger
table as a second tolerance namespace with a named prefix, state which of the two feeds
`combineTol` and which feeds obligation 4, and bind obligation 4's `approxEq` tolerance
explicitly to the observable's regime. The last of those is a one-line fix to obligation 4's
row and closes F2's untoleranced comparison.

---

## Group F — the postdoc's own sweep

### F1 — The certificate's `Passed` is vacuous over an empty leaf set. A kernel compared against nothing certifies clean.

**Severity: critical. Confidence: high.**

`cert-obligations.md:85-90` defines aggregation:

> Aggregation across obligations is the **semilattice meet** of `EvidenceOps`, so a
> composition's overall verdict is
> - `Failed` if any obligation leaf is `Failed`,
> - `Pending` if any leaf is `Pending` and none is `Failed`,
> - `Passed` otherwise.

With zero leaves, no leaf is `Failed` and no leaf is `Pending`, so the root is `Passed`.
That is the correct meet on a three-element chain and it is the wrong verdict.

**Two independent paths reach the empty leaf set**, and only the first was in the original
draft.

*Path 1 — no pinned targets.* Obligation 4's comparison is realised through `Import`
(`pino-bridge.md:95-97`): "Its residual-leaf outputs serve the reference-battery obligation."
`Import` is a **compiler input** (`product.md:226-229`): "a targets file handed to the
compiler, not a runtime argument." And `product.md:201-203` states that a check the oracle
cannot stand behind "is not in the compiled kernel, so its key is simply not in any map." So
the set of reality-comparisons in a kernel is chosen by whoever writes the targets file,
**nothing requires it to be non-empty**, and a kernel compiled with no pinned targets emits a
certificate whose root verdict is `Passed`.

*Path 2 — aggressive pruning.* From **A2**: symbolic lift deletes every subgraph whose
applicability predicate is false, and `physics-graph.md:243` defines a certification obligation
as a *global traversal* of the graph. Fewer nodes therefore means fewer obligation leaves as a
mechanical consequence, so the certificate's verdict *improves monotonically as more physics is
deleted*, and a composition whose predicates all evaluate false has no leaves at all. This path
needs no adversarial targets file — it is the ordinary operation of the pipeline on a material
the predicates exclude.

The corpus knows this failure mode and states it twice, in two other places:

- `formula-registry.md:104-106` — "A harvest that fails to find its source must be a loud
  failure, not a silent empty set — **an empty vocabulary accepts everything**."
- `traps.md`, *A checker that finds nothing may not be looking* — "Both ran green the whole
  time."

It is not stated for the evidence semilattice, which is the one place where emptiness produces
a `Passed` verdict on a prediction.

**What would refute this.** A statement anywhere that a composition's certificate requires a
minimum leaf population, or that the meet over an empty obligation set is `Pending` rather
than `Passed`. I searched for `vacuous`, `non-empty`, `nonempty`, `empty set`, `no leaves`,
`at least one obligation` across `journals/` — the hits are `agent-contract.md:171`,
`agent-contract.md:188`, `named-formulas.md:123`, `formula-registry.md:105`,
`reference-battery.md:146`, `coupling-structure.md:202,208,487`, `traps.md:412`. None is
about the evidence semilattice.

**Proposed correction.** Two parts, both small.
1. Make the meet's identity `Pending`, not `Passed`: an obligation with no leaf is
   undischarged, not discharged. `Pending` already exists in the lattice and already means
   "not decided" — and per **A5** it currently has no producer at all, so this costs nothing
   and gives a dead value its first use.
2. Add a **coverage obligation** stating the minimum leaf population a composition must carry
   before its root may read `Passed`: at least one reference comparison per emitted observable
   that has a battery row available, and an explicit `Pending` with a witness naming the
   observable where none exists. Absence of anchor data is already the corpus's honest answer
   elsewhere (`out-of-scope.md:126-128`); this makes it the certificate's answer too. **F13**
   notes the quantity this obligation needs is already computed, stored and content-addressed.

---

### F2 — Obligations 4 and 8 are one check split in two. Obligation 4 compares with no tolerance; obligation 8 holds the tolerance and the trip. There are nine obligations, not ten.

**Severity: major. Confidence: high.** *Independently rediscovered by the principal; see B8 for
where obligation 4's tolerances actually live.*

`cert-obligations.md:70` (obligation 4):

> content-side: look a row up by `(Property, Material, Environment)` in the frozen reference
> data on a held-out crystal battery ([reference-battery]) and compare under `approxEq` |
> `O(log n)` B-tree

`cert-obligations.md:74` (obligation 8):

> versioning discipline on obligation 4: per-entry provenance travels with the verdict, the
> row's schema version is compared by the reader, and the cert trips at `τ_battery` with the
> numerical witness | `O(log n)` + `O(1)`

Three things follow.

1. **Obligation 4's comparison has no tolerance.** `approxEq` is typed
   `approxEq : Tolerance → a → a → Bool` (`typeclass-alphabet.md:58`). It takes a `Tolerance`
   argument. The tolerance ledger contains no row assigned to obligation 4. `τ_battery` is
   assigned to obligation 8: "reference-battery agreement before the cert trips (obligation 8,
   [reference-battery])" (`:145`). So the only obligation that compares the kernel to the world
   performs that comparison with an unbound tolerance parameter. **B8 identifies the 59
   per-observable accuracy regimes as the tolerances that should bind it.**
2. **The verdict lives in obligation 8.** "the cert trips at `τ_battery`" is the pass/fail on
   value agreement. Obligation 4 performs a lookup and an untoleranced comparison and cannot
   produce a verdict.
3. **The corpus's own pages behave as if there is one check, not two.**
   - `reference-battery.md:31-32`: "[reference-data] holds the machine-readable reference data
     that **cert obligation 8** reads" — singular, obligation 8.
   - `reference-battery.md:70-71`: the Environment cell "is also the third component of the
     **obligation-8 lookup key**" — the lookup is attributed to 8, which obligation 4 claims.
   - `build-verification.md:167-168`, Gate 2: "certification obligations 1, 2, 3, 5 **and 8**
     emit verdicts." Obligation 4 does not appear. A versioning discipline *on* obligation 4
     cannot emit a verdict when obligation 4 did not run.
   - `capability-slices.md:60,80,97`: the three MVP capability slices list certification
     obligations `1 · 2 · 3 · 5`, `1 · 2 · 5 · 6`, and `2 · 3 · 5`. **Obligation 4 appears in
     none of them, and neither does obligation 8.**

This was registered as a contradiction about *which* obligation carries the 3σ trip
(`audit/inherited/contradictions.md`, `oracle-cert-accuracy` fragment). It survives the
rewrite, and the resolution is stronger than the registration: it is not a mis-attribution
between two obligations, it is one obligation written twice with the halves separated. The
count of ten is inflated by one.

**What would refute this.** A statement that obligation 4 has its own tolerance distinct from
`τ_battery`, or that obligation 4 emits a verdict independent of obligation 8's trip. I found
neither.

**Proposed correction.** Merge into one obligation — "reference agreement, versioned" —
carrying the lookup, `τ_battery`, the provenance travel and the schema-version comparison, and
renumber. Bind the `approxEq` tolerance to the observable's accuracy regime per B8. If the
split is wanted, obligation 4 needs its own named tolerance in the ledger and obligation 8 must
be stated as a check on *metadata* only, with no value comparison in it.

---

### F3 — Obligation 9, as written, ranges over nothing; the checker body describes a different object from the tag; and the corpus's own acceptance gate already implements the correct reading.

**Severity: major. Confidence: high.** This is the registered open question
`surrogate-validity-scope`. The brief asked me to work out what the obligation should be
rather than confirm it, so the confirmation is compressed and the design is the finding.

**The confirmation, briefly.** `cert-obligations.md:75` states obligation 9 as "surrogate
validity" with body "declared input domain contains the query · surrogate uncertainty below
`δ_surrogate` · refresh current, measured on a held-out development set". `named-formulas.md`
defines `relaxed` as "genuinely non-smooth: argmin, convex hull, sort, discrete metric",
shipping a declared smooth relaxation. The six rows carrying it in
`data/registry-manifest.csv` — 45 `wulff-shape`, 46 `termination-stability-window`, 50
`interface-bond-counting`, 67 `phase-diagram-convex-hull`, 84 `cluster-expansion-energy`, 85
`structure-uniqueness-CSP` — are all relaxations (`Diff = D4`). The one learned surrogate, row 6
`quasi-particle-shift-G0W0-surrogate`, carries `adjoint` (`D2`).

**Three further pieces of evidence the open question does not record**, and they decide the
answer:

- `build-verification.md:188-189`, Gate 4: "**Obligation 9** — a `relaxed` query outside its
  declared domain trips with a witness." The corpus's own acceptance gate tests the
  *relaxation* reading, and tests only the domain clause.
- `build-verification.md:138-140`: "Every `relaxed` entry carries a rationale **naming its
  relaxation**, under **the obligation that governs relaxations**" — the relaxation reading
  again, and a fourth phrasing of obligation 9's subject.
- The tolerance-ledger row (`cert-obligations.md:144`) reads "relaxation validity".

So the corpus states obligation 9's subject four times and gets "relaxation" three times. The
odd one out is the obligation row itself, whose *body* was written for a learned net. The body
is not wrong — it is correct for an object that is not in the obligation's range.

**What the obligation should be: split it, and note that the second half cannot select on the
differentiability axis at all.**

**9a — relaxation validity**, ranging over `relaxed`. Three clauses, all computable from what
a `relaxed` row has:

1. *Parameterised declaration.* The provenance cell names a relaxation **and its numeric
   parameter** — the log-sum-exp temperature, the sigmoid width, the softmin `τ_soft`. A
   family name without a parameter fails, because the bias depends on the parameter and no
   bound can be formed without it. (See F5: not one of the six passes this today.)
2. *Bias bound below the declared allowance.* For the log-sum-exp family the bound is
   elementary and exact: for `LSE_τ(x₁…x_n) = τ ln Σᵢ exp(xᵢ/τ)`,
   `max x ≤ LSE_τ ≤ max x + τ ln n`, so `0 ≤ LSE_τ − max x ≤ τ ln n` uniformly, and the
   witness is the triple `(τ, n, τ ln n)`. Rows 45, 46, 67 and the softmin half of 85 are all
   in this family. Row 50's soft cutoff needs the width `δ` and the local neighbour density
   near `r_cut`. Row 84's mean-field/Gumbel-Softmax relaxation of a discrete cluster expansion
   admits **no** uniform bound of this kind, and that row must therefore declare a *measured*
   envelope instead of a derived one — naming that difference is the point of the clause, not
   an inconvenience.
3. *Budget entry.* The bound is actually contributed to `combineTol`. `named-formulas.md`
   asserts the bias "enter[s] the tolerance composition of [typeclass-alphabet#quantity]";
   nothing checks that it did. The witness is the term's value in the composed tolerance. This
   is `traps#target-is-not-measurement` applied to relaxation bias: "an intention that nothing
   measures is not a measurement."

The present body's *domain* clause survives here, but derived rather than declared: for a
relaxation, the valid domain **is** the region where clause 2's bound sits below allowance.
That is what Gate 4 already tests.

Tolerance: rename the ledger's `δ_surrogate` row to `δ_relax` — its text already reads
"relaxation validity" — and add the relaxation parameters to the ledger (F6).

**9b — surrogate validity**, ranging over learned objects. The present checker body is
*correct as written* for this object: declared input domain contains the query; predictive
uncertainty below `δ_surrogate`; refresh current; measured on a held-out development set.
All four clauses are meaningful for row 6.

**But 9b cannot select on the differentiability tag, and this is the structural point the open
question misses.** The differentiability field answers exactly one question — "how does a
consumer obtain a gradient through this row?" (`formula-registry.md:52`). Row 6 is `adjoint`
because you obtain its gradient by adjoint. That is the *correct* tag. No value of that field
can mean "this row's value comes from a fitted model", because that is a fact about provenance,
not about differentiation. Rebinding obligation 9 to any differentiability value therefore
cannot fix it; it would only move the mismatch.

What 9b needs is a selector on an axis that exists for the purpose — and **half of one already
exists.** `coupling-structure.md:337-341` declares
`cost-class ∈ {curated, per-material-DFPT, fit}` on every `ProvenanceLedger` coefficient,
"declar[ing] its acquisition pipeline". `fit` is exactly the marker 9b needs, and it already
covers the high-field tail correction. What it does not cover is a *registry row* whose value
comes from a fitted model, because `cost-class` lives on coefficients, not on rows — so row 6
is still unselectable.

The correction is therefore in two parts: range 9b over every `ProvenanceLedger` entry with
`cost-class = fit`, **and** add the same distinction to the manifest — either as a value in
the closed provenance vocabulary `formula-registry.md:59-85` owns (`learned`, alongside
`extension` and the five research streams) or as a `cost-class` column mirroring the coupling
ledger's. Either makes the population countable, which today it is not.

**Note on 9b's V1 population.** Row 6 is the only live subject. The high-field
distribution-tail correction ships as identity and its corner is refused
(`out-of-scope.md:50-54`), so it has no live values to validate — but that is a V1 accident,
not a structural exemption, and 9b must cover it the moment anchors arrive. **A6** adds a
third population to 9b: the out-of-scope exclusions themselves, which are domain refusals of
exactly this shape.

---

**What would refute this.** A page defining a set of learned formulas that `relaxed` selects, or a statement that the six `relaxed` rows are surrogates. All six are relaxations by their own provenance cells, and the one learned surrogate carries `adjoint`.
### F4 — Relaxation bias does not propagate. Obligation 9 selects the row that contains the relaxation, never the rows that consume it.

**Severity: major. Confidence: high.** This is a defect in the obligation's *quantifier*, and
it survives any of the rebindings the open question proposes.

The chain is concrete and it is in the MVP. From `data/registry-manifest.csv`:

- Row 50 `interface-bond-counting`, `Diff = D4` (`relaxed`), signature
  `(slab_pair, cutoff) → bond-vec`.
- Row 116 `interface-trap-density`, `Diff = D1` (`direct`), `Depends on:
  interface-bond-counting (row 50), strain`.
- Row 119 `subthreshold-swing-Dit`, `Diff = D1` (`direct`), `Depends on:
  interface-trap-density (116), C_ox`.
- Row 115 `2DEG-sheet-density`, `Diff = D2`, also consumes row 116.

`direct` means "smooth, and the gradient is available directly … **No registration gate**"
(`named-formulas.md`). So rows 116 and 119 carry no gate, and obligation 9 — which selects on
`relaxed` — never sees them. Yet their values inherit row 50's relaxation bias in full.

`combineTol` is monotone and composes tolerances upward, so the *tolerance* would propagate —
**if** the bias were ever placed in it. That placement is precisely what nothing checks
(F3, clause 3). The result is that the relaxation's model-form error is invisible at exactly
the rows a consumer reads: `D_it` and the subthreshold swing.

**What would refute this.** A statement that a `direct` row consuming a `relaxed` row inherits
the relaxed row's obligation, or a rule that a transitive consumer of a `relaxed` row is
itself tagged. I found neither; `named-formulas.md`'s mixed-output rule addresses a different
case (a row returning both a real and a discrete component).

**Proposed correction.** Obligation 9a ranges over the **transitive consumers** of any
`relaxed` row, not over `relaxed` rows alone. The check on a consumer is clause 3 only — that
the upstream bound appears in its composed tolerance — which is cheap and is a DAG walk of
exactly the shape obligation 10 already performs.

---

### F5 — Not one of the six `relaxed` rows declares a numeric relaxation parameter. The build gate that requires the relaxation to be "named" is satisfiable by a declaration that cannot be gated.

**Severity: major. Confidence: high.**

`named-formulas.md` (the `relaxed` bullet): "**The relaxation is named in the row's provenance
cell**; a `relaxed` row without one is un-gateable and fails the registry-build gate
([traps#unnamed-relaxation])." `build-verification.md:138-140` enforces the naming.

Verbatim from `data/registry-manifest.csv`, `Source` column:

| Row | Declared relaxation | Parameter |
|---|---|---|
| 45 `wulff-shape` | `S1 (soft-hull log-sum-exp)` | none — family only |
| 67 `phase-diagram-convex-hull` | `S1 (soft-min hull log-sum-exp)` | none — family only |
| 84 `cluster-expansion-energy` | `continuous site occupations x_i∈[−1,1] (mean-field / Gumbel-Softmax), bias declared under obligation-9` | none — family only, and it defers the bias to the obligation that covers nothing |
| 46 `termination-stability-window` | `softmin over γ(term) at temperature τ_soft` | symbol `τ_soft`, no value |
| 50 `interface-bond-counting` | `soft-cutoff coordination Σ_j σ((r_cut−d_ij)/δ) with declared width δ` | symbol `δ`, no value |
| 85 `structure-uniqueness-CSP` | `softmin over the set plus a sigmoid on (d−d_min) with declared width` | no symbol, no value |

The bias of every one of these depends on the parameter — `τ ln n` for the log-sum-exp family,
the neighbour density within `δ` of `r_cut` for the soft cutoff. A declaration naming the
family alone fixes no bound. So the gate as written passes six rows of which none is gateable,
which is the same shape as `traps#checker-not-looking`: the gate runs green and is not looking
at the thing that matters.

Row 84 is the worst of the six: it declares its bias "under obligation-9", and obligation 9 is
the obligation that ranges over nothing.

**What would refute this.** Any of the six rows carrying a numeric relaxation parameter. Verified against the manifest's `Source` column verbatim, row by row; the table in this finding is the complete population.

**Proposed correction.** The gate requires a *parameterised* declaration — family plus numeric
value, or family plus a named ledger symbol that has a value in the tolerance ledger. This is
clause 1 of the proposed 9a.

---

### F6 — Two relaxation parameters live in the manifest and in no tolerance ledger, and the ledger's namespace rule has no category for either.

**Severity: moderate. Confidence: high.**

`τ_soft` (row 46) and `δ` (row 50) appear in `data/registry-manifest.csv` and in no row of the
tolerance ledger at `cert-obligations.md:131-149`. By the ledger's own rule at `:161-167` —
"A tolerance stated anywhere in the corpus but absent from this table is a defect in this
table" — that is two defects in the ledger. **B8** shows they are two of at least sixty-one.

There is a second, sharper problem. The ledger states a namespace rule at `:126-129`:

> **`τ` is not a reserved tolerance prefix** — `τ_n`, `τ_p`, `τ_PO`, `τ_E`, `τ_hop`, `τ_iv`
> and `τ_alloy` are physical times, and a `τ_x` is a tolerance only if it appears in the table
> below.

The rule is stated as a complete dichotomy: a `τ_x` is a tolerance if it is in the table and a
physical time otherwise. `τ_soft` is a **softmin temperature** — a relaxation hyperparameter.
It is not in the table, and it is not a physical time. The rule as written misclassifies it,
and a reader following the rule correctly concludes that `τ_soft` is a physical time, which is
the exact failure mode the rule exists to prevent.

**What would refute this.** A ledger row for `τ_soft` or the row-50 cutoff width, or a third namespace category in the rule at `cert-obligations.md:126-129`. Neither exists.

**Proposed correction.** Add `τ_soft` and `δ_cutoff` (or per-row parameter names) to the
ledger with per-row values, and amend the namespace rule to three categories: tolerance in
this table, declared relaxation parameter in the manifest, physical time otherwise.

---

### F7 — The registry manifest has no `applicability` column. The V1 commitment that every entry carries an explicit field a checker can count is false of all 134 rows.

**Severity: major. Confidence: high.**

`applicability-classifiers.md:129-131`:

> **Every registry entry gets an explicit `applicability` field.** Always-true stubs are
> acceptable for V1.0 and are refined incrementally — an explicit stub is a claim a reader can
> find and a checker can count, which an absent field is not.

`data/registry-manifest.csv` has nine columns: `#`, `Name`, `Signature (in) → out`, `Bundle`,
`Tier`, `Diff`, `Path`, `Source`, `Depends on`. There is no `applicability` column, for any of
the 134 rows. Gates appear only as prose inside `Source` cells, on five rows (127, 128, 129,
130, 131). A reader cannot find the stub and no checker can count it — which is precisely what
the commitment says an absent field means.

The same page's storage section (`:151-159`) specifies a rich representation for a predicate —
"a `MerkleDAG[PredicateOps, Atom]` root … a reduced ordered Boolean DAG over typed
parameterized atoms" — with an atom order that is "part of the predicate-vocabulary version".
There is no column to hold the root.

**This compounds with a self-contradiction in `formula-registry.md`.** That page states at
`:43` "One column per field of the formula record ([named-formulas#formula-record])" and then
lists nine. The record at `named-formulas.md:71-85` has **ten** fields. The two omitted are
`applicability` and `adjoint-validated` (F8). And `formula-registry.md:92-99` then lists
`applicability` in its "Where a field's vocabulary lives" table as a coded field of the
manifest — so the page names `applicability` as a manifest field in one section and omits it
from its own field list in another.

**Consequence for row 116**, the case the applicability page is built around. It "runs on an
always-true stub, which the V1 commitment permits" (`applicability-classifiers.md:100-104`).
There is no field in which that stub is recorded. The open question
`semiconductor-interface-predicate` is honest and is not the finding; the finding is that its
declared mitigation — an explicit, findable, countable stub — does not exist in the artifact.
**A5** adds that the honest disposition for such a stub is a `Pending` leaf, which also does
not exist.

**What would refute this.** An `applicability` column in `data/registry-manifest.csv`. Counted directly: 134 rows, nine columns, none named `applicability`.

**Proposed correction.** Add the `applicability` column to the manifest, populated with the
predicate root or the literal `always-true` for a stub, and correct `formula-registry.md`'s
field list to ten. A count of always-true stubs then becomes a one-line query, which is what
the V1 commitment promises. Note that **A2**'s proposed evidence leaf needs this column too —
it emits the predicate root, which has nowhere to be stored today.

---

### F8 — `adjoint-validated` has no column either. Obligation 10's verdict has nowhere to live.

**Severity: moderate. Confidence: high.**

Obligation 10 is "the registration-time adjoint gate … enforced at registration and never at
prediction" (`cert-obligations.md:76`). Its verdict is a declared field of the formula record:
`adjoint-validated : Passed | Failed(witness) | NotApplicable | Relaxed(rationale)`
(`named-formulas.md:83`). The manifest has no such column.

So the one obligation that runs at build time, and whose whole purpose is to refuse a
registration "loud, at build time" (`build-verification.md:190-191`), leaves no persistent
trace in the canonical machine-readable artifact. Whether the gate ran for a given row is not
recoverable from the corpus's own data.

Two of the enum's four values also appear nowhere in the cert semilattice: `NotApplicable` and
`Relaxed(rationale)` — see F14.

---

**What would refute this.** An `adjoint-validated` column in the manifest, or a statement that obligation 10's verdict is stored elsewhere. Neither exists; the same nine-column check covers both.
### F9 — An out-of-environment-box sample has three incompatible dispositions, stated on three pages, one of which is neither refusal regime.

**Severity: major. Confidence: high.** *A2 supplies the mechanism-level reason this could not
have been consistent: there is no stage that refuses, so each page invented its own answer.*

| Page | What happens when a swept scalar leaves the box |
|---|---|
| `product.md:150-154` | "Outside the box: **recompile**. The stamp makes out-of-box use mechanically detectable." |
| `crystal-inputs.md:119-122` | "A sample whose swept scalar leaves the box is **masked out, or trips the relevant certification obligation**, rather than being scored against a kernel that does not cover it" |
| `applicability-classifiers.md:133-140` | the window is "**re-evaluated per training sample** in the loss mask" — masked |

Three behaviours with three different consequences. **Recompile** produces a new kernel with a
new hash and a new certificate. **Mask** produces silence — the sample contributes nothing, no
verdict, no witness. **Trip an obligation** produces a `Failed` leaf. Only the third is a
refusal in either of the corpus's two regimes; the first creates a new artifact and the second
creates nothing at all.

`crystal-inputs.md` states the disjunction — "masked out, **or** trips" — with no rule for
which. That is an undetermined disjunction at the exact seam the two-regime scheme is supposed
to cover, and it is the one place a sample can be silently dropped.

Note also that `product.md`'s "mechanically detectable" is a claim about **detection**, not
about **disposition**. Detecting an out-of-box call and deciding what to do about it are
different, and the corpus supplies the first and three answers to the second.

**A second-order problem that makes this worse.** The box's content is undefined for every
field but one. `crystal-inputs.md:129-133`: "`temperature` is swept: the corpus fixes it as a
runtime-swept scalar. **The rest of the partition is unstated.** `applied_stress` and
`applied_magnetic_field` are the hard cases in either direction, because both can change the
symmetry that the symmetry-quotient stage builds its structure on."

But `applicability-classifiers.md:135-140` lists five swept windows, and one of them is "the
impact-ionization **field** domain" — a window over `applied_electric_field`. **That field is
named in neither list**: it is not the one settled field, and it is not among the two the page
flags as hard. Its structural-versus-swept status is simply absent. If it is structural, the
impact-ionization domain is not a swept window at all and belongs at compile time, and the
per-sample mask the applicability page specifies for it is testing a field that was baked into
the kernel. The page cannot know which, because the partition it depends on does not exist.

This is exactly the failure `crystal-inputs.md:124-127` names two lines earlier: "**Misfiling is
silent** … the kernel is reused outside its envelope and nothing fires. The failure has no
symptom at the seam; it shows up only as a wrong number." The page states the hazard and then
leaves the field its own dependent needs unfiled.

`applicability-classifiers.md:146-149` is honest about the dependency — "without a recorded
range set there is nothing for a per-sample mask to test the swept scalar against, and the
re-evaluation would silently pass every sample" — and then cites `crystal-inputs` for the
range set. `crystal-inputs` does not have it. The honesty is real; the mechanism is not.

**What would refute this.** A rule selecting between mask, recompile and trip. `crystal-inputs.md:119-122` states the disjunction and supplies no rule, and no other page does either.

**Proposed correction.** Pick one disposition and state it as a rule with a condition:
recompile when the caller is a compiler client and the box miss is on a structural field;
`Pending` leaf with the offending scalar as witness when the caller is a runtime client (per
**A5**, this would be `Pending`'s second producer); and never a silent mask, because a silent
mask is the one outcome that produces no record. Then state the structural/swept status of
every field in the environment record, or state that a field of unknown status is treated as
structural (the conservative direction — it forces a recompile rather than reusing a kernel
outside its envelope, which is the failure `crystal-inputs.md:124-127` calls silent and
load-bearing).

---

### F10 — The certificate's granularity is stated two ways: one per composition, and one per call.

**Severity: major. Confidence: high.** *Partly subsumed by **A7**, which is the sharper form of
the same seam. Retained because A7 settles what is returned and this settles what the returned
thing is.*

`cert-obligations.md:80-82`: "The evidence produced by the ten obligations is one
`MerkleDAG[EvidenceOps, EvidencePayload]` **per composition**".

`compose-time-pipeline.md:314-318`: "The whole graph is lowered to a compiled kernel with one
entry point … and four typed exits: a residual map …, a gradient map …, an observable map, and
**the certification evidence produced by the obligation traversals**." A kernel exit is
produced per call.

`pino-bridge.md:55-58`: `Validate` returns `( residuals, values, cograds, cert : CertEvidence )`
— per call.

And `cert-obligations.md:46-49` opens with "The certificate emitted for **any prediction**" —
per prediction.

These are different objects with different lifetimes, and the difference is load-bearing in
three ways.

1. **Some obligations cannot be leaves of a per-call DAG.** Obligation 10 runs at registration,
   before any composition exists. The four composition-validity refusals
   (`cert-obligations.md:169-201`) are decided "by tag and field comparison on the active
   `CouplingSpec` and `ProvenanceLedger`" — compose-time. None of these depends on the call, so
   attaching them as leaves of a per-call certificate re-emits a fixed verdict on every call,
   and detaching them leaves them with no certificate to live in.
2. **The freeze fixture and the content address assume a stable artifact.**
   `cert-obligations.md:42-44` names "a freeze fixture with a tamper tripwire", and `:92-93`
   makes "The attestation DAG's root `Address`" the cert artifact the operator consumes. If the
   DAG is per call, the address changes per call and a freeze fixture over it is not a fixture.
3. **The strength of the claim changes.** If the certificate is per composition and computed at
   compose time, then "a prediction is certified by the ten obligations"
   (`cert-obligations.md:54-55`) means *the composition that produced this prediction was
   certified* — a materially weaker statement, since a composition covers every query in its
   environment box and the obligations evaluated none of them.

**A related unspecified point.** `cert-obligations.md:92` says "`Failed` absorbs, which is what
licenses early exit." Early exit means the remaining obligations are not evaluated, so the leaf
set — and therefore the DAG, and therefore the root `Address` — depends on evaluation order,
which no page specifies. Whether early exit is observable in the artifact is not stated, and it
must be, because the artifact is content-addressed and frozen. **This also interacts with F1**:
early exit produces a smaller leaf set, and a smaller leaf set is the condition under which the
meet's identity becomes visible.

---

**What would refute this.** A statement fixing the certificate's lifetime, or a rule making the per-call and per-composition objects the same. Four statements exist and they do not agree; A7 shows the disagreement reaches the signature itself.
### F11 — The GENERIC degeneracy tripwire is written `≈ 0` and has no tolerance anywhere in the corpus.

**Severity: major. Confidence: high.** *Upgraded from moderate: **B1** shows this is not an
isolated omission but one of two instances of the same disease, and **B3**'s measurement
settles which form the fix must take.*

`cert-obligations.md:72`, obligation 6: "plus the cert-only degeneracy tripwire
`‖L δS/δx‖² + ‖M δE/δx‖² ≈ 0` per tier".

The tolerance ledger's two obligation-6 rows are `τ_equiv` ("`Algebraic/MethodEquivalence`
**equivalence-pair** agreement") and `τ_method` ("**consistency-pair** model-gap envelope").
Both are about formula-pair agreement. Neither bounds the degeneracy tripwire, and no other
ledger row names it.

`residual-definitions.md:109-112` explains why it needs one: "under the per-tier generator
structure it is **identically zero by construction**, so it is a generator-construction-bug
tripwire". Identically zero by construction is exactly the case where a floating-point
evaluation needs a stated threshold — the check has no physics scale of its own, so "`≈ 0`" is
undecidable without one, and the quantity is a squared norm whose magnitude depends on the
units `L`, `M`, `E` and `S` are assembled in.

By the ledger's own exhaustiveness rule (`:161-167`) this is a defect in the ledger. It is
worse than the two in F6, because there the symbol exists and the ledger lacks it; here no
symbol exists at all.

**What would refute this.** A tolerance anywhere in the corpus bounding the degeneracy tripwire. Neither obligation-6 ledger row does, and no symbol for it exists — this is the stronger form of absence, since there is no name to search for.

**Proposed correction, now with a measured basis.** Name it `δ_degen` and state it as
**relative to `(‖L‖·‖δS/δx‖ + ‖M‖·‖δE/δx‖)²`**. B3's fourth experiment measured all three
candidate forms on an exactly-degenerate construction:

- absolute: passes at 1e-28, and would pass at 1e-25 — uninformative at any threshold a human
  would pick;
- relative to the true value: **undefined**, since the true value is zero;
- relative to the norm product: 1.7e-32, well-defined and scale-free.

Only the third is available, which is worth stating in the correction because the second is
what a reader reaches for first and it does not exist for this check.

---

### F12 — Obligation 8 certifies that provenance is *recorded*, not that it is *independent*. Two battery rows declare an experimental source class while citing an internal corpus page.

**Severity: moderate. Confidence: high.**

Obligation 8's clause is "per-entry provenance travels with the verdict"
(`cert-obligations.md:74`). Travelling is not checking. Nothing in obligation 4 or 8 requires
a reference row's `Source` to be external to the corpus, and nothing checks the `Source class`
column against the `Source` cell.

In `data/reference-data/` (179 rows across five CSVs, counted), **8 rows carry a `Source` that
names only an internal corpus artifact, with no external citation.** Of those, **four declare
`Source class = experimental`** — a class that asserts a measurement while pointing at a page:

| File | Observable | Material | `Source` | `Source class` |
|---|---|---|---|---|
| `material-constants.csv` | `lattice-constant-a` | diamond | "curated MVP anchor (mvp-system; standard XRD value)" | `experimental` |
| `material-constants.csv` | `bandgap-indirect` | diamond | "curated MVP anchor (mvp-system); PBE −23% ⇒ G₀W₀/hybrid path" | `experimental` |
| `phonon-frequencies.csv` | `phonon-max-energy` | diamond | "curated MVP anchor (see accuracy-ledger.md)" | `experimental` |
| `phonon-frequencies.csv` | `debye-temperature` | diamond | "curated MVP anchor (see accuracy-ledger.md)" | `experimental` |

The other four are internally sourced but declare a class that at least admits it —
`theory-interpolation` on the two `thermal-conductivity, diamond (type IIa)` rows ("Pass C
battery anchor"), and `experimental-review` on `saturation-velocity, diamond (holes)` and
`caughey-thomas-beta, diamond`.

*(The previous draft of this finding said "10 of 179 … two are unambiguous". Both numbers were
wrong in the safe direction: the keyword probe caught two rows — `polarization-bowing-b` citing
Fiorentini-Bernardini and `breakdown-field-critical` citing Maeda — that do carry real external
citations and are not instances. Strictly counted it is 8 internally-sourced rows, of which 4
rather than 2 declare `experimental`.)*

`reference-battery.md:75-76` requires the `Source` field to be "a DOI, paper title and page
reference; or a computational provenance, meaning functional, k-mesh and cutoff." **None of the
eight is either.** A row declaring `experimental` while pointing at an internal page passes
obligation 8, because its provenance travelled.

Note the second row in the table above is self-defeating in a way the others are not:
`bandgap-indirect` for diamond declares `Source class = experimental` and its own `Source` cell
then discusses the PBE error and the quasi-particle path — i.e. it describes a *computed*
quantity while claiming a measured class, in the same cell.

This matters beyond the two rows because `debye-temperature` is load-bearing for my subject:
the four-phonon validity window `T ≳ 0.4 Θ_D` (`out-of-scope.md:37-40`, registry row 121) reads
Θ_D, and if Θ_D's provenance is an internal pointer then the window's position is set by the
corpus rather than by measurement. *(The principal's register independently establishes that
the `0.4 Θ_D` criterion is back-derived from that same unsourced Θ_D and mis-attributed to a
paper containing no Debye criterion. The two findings are the same circle seen from two sides:
the value has no external provenance, and the rule that uses it was derived from it.)*

**Boundary note.** Whether any individual value is *right* is postdoc-values' and the diamond
lead's — particularly the two `thermal-conductivity, diamond (type IIa)` rows, which the
principal's register already has under acquisition. I report only the obligation-facing defect:
obligation 8 cannot see this class of problem at all, because recording provenance and checking
it are different operations and only the first is specified.

**What would refute this.** A clause in obligation 4 or 8 checking `Source class` against the `Source` cell, or a requirement that a battery row's source be external. `cert-obligations.md:74` says provenance *travels*; nothing says it is *checked*.

**Proposed correction.** Obligation 8 gains a clause: the `Source class` is consistent with the
`Source` cell, and a row whose `Source` names a corpus artifact is `internal` — a source class
the vocabulary does not currently have. An internal-sourced row should not be able to discharge
a reference comparison at all.

---

### F13 — The reference cache stores a coverage mask that no obligation reads.

**Severity: moderate. Confidence: high.**

The `SqliteReferenceCache` schema (`cert-obligations.md:210-220`) carries
`coverage_mask BLOB NOT NULL -- RoaringCoverageMask serialization`, and it is part of the
content address (`:222-225`).

Obligation 4 is a lookup plus `approxEq`. Obligation 8 checks provenance travel, schema version
and the `τ_battery` trip. Neither reads `coverage_mask`. I searched `journals/` for
`coverage_mask`, `coverage-mask`, `CoverageMask` and `axis-coverage`: the only occurrences
inside the certification subject are the schema line and the key-construction line, both in
`cert-obligations.md`.

This is a missed opportunity rather than a wrong claim, and it is the missed opportunity that
would fix F1. `AxisCoverage` "declares **which axis tuples of the named target the imported
datum actually constrains**" (`pino-bridge.md:101-102`). That is exactly the quantity a
coverage obligation needs: it is already computed, already stored, already content-addressed,
and no obligation asks it whether the emitted kernel's environment box is covered by anything
at all.

---

**What would refute this.** An obligation reading `coverage_mask`. Obligations 4 and 8 are quoted in full at `:70` and `:74`; neither does, and no other obligation touches the reference cache.
### F14 — `NotApplicable` is emitted by the corpus's own acceptance gate and is not in the cert semilattice.

**Severity: moderate. Confidence: high.**

The semilattice has exactly three values (`cert-obligations.md:87-90`). Two further verdicts
are specified elsewhere and reach the certificate:

- `NotApplicable` — in the `adjoint-validated` / `adjoint-cert` enum
  (`named-formulas.md:83`, `residual-machinery.md:96,222`), and emitted by an obligation in
  `build-verification.md:192-194`, Gate 4: "**Obligation 7** — non-topological diamond emits
  '**not applicable**' with a rationale".
- `Relaxed(rationale)` — same enum, same two sites.

The meet is defined on three values. What it does with a `NotApplicable` leaf is not stated.
The two candidate readings have opposite consequences: if `NotApplicable` is the meet's identity
it is absorbed and vanishes, and if it is below `Passed` it drags the root down. The corpus's
own gate emits it, so this is not a hypothetical. *(Note the contrast with **A5**: the corpus
has a fourth verdict nothing accommodates and a third verdict nothing produces, at the same
time.)*

**This also confirms obligation 7 is vacuous on the V1 material set.** Gate 4's positive test
for obligation 7 is "a **contrived** time-reversal-invariant test system". The anchor
materials — diamond (`Fd-3m`), wurtzite GaN and AlN (`P6₃mc`), β-Ga₂O₃ (`C2/m`), c-BN
(`F-43m`) — are trivial insulators, so obligation 7 returns `NotApplicable` for every
composition the corpus will actually compile. Together with obligation 9 (F3), **two of ten
obligations constrain nothing on the V1 material set.**

**A separate problem with obligation 7's cost.** Its complexity is stated as
`O(1) + O(#Wyckoff)` (`cert-obligations.md:73`) and its check is "the slab **must carry**
boundary states with the multiplicities a lookup table gives". Enumerating the boundary states
a slab actually carries requires a slab electronic-structure calculation — the corpus has slab
compositions (`property-templates.md:163` `BiSlabGrandPotentialOf`, `typed-compositions.md:292`
`SurfaceEnergy`), so the object exists, but its cost is nowhere near `O(#Wyckoff)`. Either the
obligation compares the lookup table against itself, which is tautological, or the complexity
column is wrong by many orders. The text does not say which.

---

**What would refute this.** A statement placing `NotApplicable` in the evidence lattice, or a rule for how the meet treats it. The lattice is stated as exactly three values at `:87-90`, and Gate 4 emits a fourth.
### F15 — No obligation checks dimensional consistency, and the manifest records three dimensional defects that were caught by hand.

**Severity: major. Confidence: high.** This is the most direct answer to "what could be wrong
with an emitted kernel that passes all ten".

`Quantity` declares `unitsOf : a → Units` (`typeclass-alphabet.md:57`). I searched `journals/`
for `unitsOf`, `dimensional consistency`, `unit check`, `units are checked`, `dimensional
analysis`: **one hit, the declaration itself.** No obligation, no registration gate and no
checker exercises it. Obligation 2 is "`Quantity` **ordering**: the value is checked against
each declared bound" — a range test, which is a different operation.

That the gap is real and not theoretical is recorded in the manifest, which carries three
signature corrections that are dimensional repairs:

- Row 68 `phase-boundary-slope`: "`ΔH/ΔV` alone has units of pressure, not pressure per kelvin,
  so the earlier `(ΔH, ΔV)` signature was dimensionally incomplete."
- Row 72 `hot-carrier-temperature-balance`: "without the carrier density the declared output
  cannot be formed — `(j·E)·τ_E` is J·m⁻³ and only division by `n·k_B` yields a temperature."
- Row 74 `impact-ionization-coefficient`: "α is ionizing collisions per unit length travelled —
  cm⁻¹, not a rate in s⁻¹."

Three dimensional errors, all found by human review, none of which any of the ten obligations
would have caught. Obligation 6 would catch a units error only where a *second* formula claims
the same quantity and is itself right; obligation 4 only where a battery row exists; obligation
3 only "where closed-form answers exist".

**B2 and B6 are two more instances of the same gap at the tolerance level rather than the
formula level** — a dimensionless tolerance derived from a Hartree one, and a force tolerance
with no unit at all. A dimensional obligation over formulas would not have caught either,
because tolerances are not formulas; that is worth noting, because it means the gap has two
halves and the cheap fix closes only one.

**What would refute this.** Any obligation or gate exercising `unitsOf`. The search returns one hit, the declaration.

**Control on that negative.** The same grep applied to the sibling method on the same typeclass, `approxEq`, returns **four** hits: the declaration at `typeclass-alphabet.md:58` and its uses in obligations **1, 4 and 6** (`cert-obligations.md:67,70,72`). So the probe finds uses when uses exist, and `unitsOf`'s single hit is a fact about the corpus rather than about my search. *(Obligation 3 does not appear in that list — it compares with an explicit `|predicted − exact|/σ < 3` rather than through `approxEq`. Noted because an earlier phrasing of this control claimed obligation 3 among the users, and it is not.)*

**Proposed correction.** A dimensional-consistency obligation, or a registration-time gate in
the same position as obligation 10's DAG walk: every `algebraic-combination` node's output
units, derived from its inputs, equal the declared output units of the registry row it
dispatches to. This is `O(#nodes)`, needs no physics, and would have caught all three recorded
defects. It is the cheapest missing check in the set. Separately, every ledger row should carry
a units column — which would have caught B2 and B6 by inspection.

The same argument applies to **sign conventions**, which `traps.md:161` carries as a whole
hazard section: a sign error survives obligations 1, 2 and 5 unless it happens to break
equivariance, a declared bound, or the antisymmetry of `L`. The corpus's own example —
"**`E_b` rises with temperature** … the falling quantity it is easily confused with is
mobility" (`accuracy-ledger.md:133`) — is a sign error in registry row 123 that no obligation
would detect.

---

### F16 — The degenerate-doping exclusion motivates its gate with a material for which the gated physics does not exist.

**Severity: moderate. Confidence: high.**

`out-of-scope.md:55-61`:

> **Plasmon-phonon coupling and Lyddane-Sachs-Teller breakdown at degenerate doping** — above
> roughly `10²⁰ cm⁻³`, which heavily boron-doped diamond contact layers reach, the static
> permittivity derived through that relation and Fröhlich screening both lose validity. V1
> **applicability-gates** the derived-permittivity path and Fröhlich screening on
> `n < n_degenerate(host)`.

Diamond is non-polar. `mvp-system.md:50` states it in full — "Diamond is **non-polar
(homopolar)**, so the Born effective charge vanishes by symmetry: no LO–TO splitting and no
Fröhlich coupling" — and `applicability-classifiers.md` states the same fact twice in its own
terms, at `:74-75` ("diamond, where both are false") and `:118` (`is-polar-material` is "False
for diamond"). The Lyddane–Sachs–Teller relation is a statement
about LO–TO splitting; with no splitting there is nothing to derive a static permittivity
through, and there is no Fröhlich screening to lose validity.

So the bullet offers diamond as the case that motivates a gate on two paths that are already
inactive for diamond — both are gated off by `is-polar-material`. A competent reader binds the
clause "which heavily boron-doped diamond contact layers reach" to the LST breakdown and
concludes diamond's permittivity path is at risk. It is not; it does not exist.

This is a **misinterpretable section** rather than a false statement — read narrowly, the
clause only asserts that the density is reachable in practice. But the corpus's own
polar-predicate split exists precisely to stop readers conflating the two senses of "polar",
and this sentence invites the conflation on the page that enforces the split's consequences.

**What would refute this.** Diamond having a Fröhlich channel or an LO-TO splitting. `mvp-system.md:50` states it has neither, by symmetry.

**Proposed correction.** Move the density-reachability observation to a separate clause, and
name a polar host for the motivating case — β-Ga₂O₃, which is where the physics actually bites
and where the multi-mode Fröhlich interaction is the dominant mobility limiter.

---

### F17 — The flexoelectricity exclusion's two clauses contradict each other, and the noise floor they rest on is stated nowhere.

**Severity: minor. Confidence: high.**

`out-of-scope.md:29-30`: "**Flexoelectricity in centrosymmetric materials** — below the
numerical-noise floor; order-of-magnitude only."

If a quantity is below the numerical-noise floor, no order of magnitude for it can be given —
that is what being below the noise floor means. The two clauses state incompatible epistemic
positions, and the exclusion's justification is whichever one the reader picks.

Separately, "the numerical-noise floor" is a definite description of a quantity the corpus
never states. I found no numerical-noise floor anywhere in `journals/` — which is one more
instance of B8's pattern: a threshold the corpus reasons from and never declares.

**What would refute this.** A stated numerical-noise floor anywhere in the corpus, which would at least make the second clause checkable. There is none.

**Proposed correction.** Pick one: either state the estimated magnitude and the threshold it
falls below, or state that it is unresolvable and drop the order-of-magnitude claim.

---

### F18 — Three of the four composition-validity refusals name an obligation whose checker body does not perform the check, and the fourth names an obligation whose declared range excludes it.

**Severity: major. Confidence: high.**

`cert-obligations.md:169-175` opens the section: "Four compose-time refusals are decided **by
tag and field comparison** on the active `CouplingSpec` and `ProvenanceLedger`, and are emitted
as obligation leaves". A tag-and-field comparison is a distinct operation from any of the ten
checker bodies. The attributions do not survive contact with them.

| Refusal | Attributed to | What that obligation's body actually does | Verdict |
|---|---|---|---|
| Unprovenanced coefficient | "obligations 4 and 9" | 4 is "look a row up … and compare under `approxEq`"; 9 ranges over `relaxed` | Wrong twice. Provenance is **obligation 8**'s clause — "per-entry provenance travels with the verdict". Obligation 4 is a value lookup and cannot see a missing ledger entry; obligation 9 ranges over the empty set (F3) |
| Gap-slope double count | "obligation 6" | "two formulas claiming one quantity agree on the shared domain … plus the … degeneracy tripwire" | Wrong. Detecting that a `total`-tagged slope and a thermal-expansion path are co-active is a tag comparison on the `CouplingSpec`, not an agreement test between two formulas |
| Learned correction without an anchor | "obligation 9" | 9 ranges over formulas tagged `relaxed` | **The object is right and the range is wrong.** The high-field distribution-tail correction is "outside the registry" (`accuracy-ledger.md:162`), so it carries no differentiability tag at all and `relaxed` cannot select it |
| Polarization-convention pairing | "obligation 6" | as above | Wrong, same reason as the gap-slope row: a `polarization-reference` tag-pair comparison is not a formula-agreement test |

`coupling-structure.md` — the page that owns all four rules — never names a number. It says
"**A cert obligation** refuses…" three times (`:344`, `:363`, `:396`), indefinite each time.
So the numbers exist only here, and three of four are wrong.

**The third row is the most important line in this finding**, and it settles F3 from a
direction the open question does not consider. Obligation 9 is invoked **twice on this one
page** — once in the obligations table over `relaxed` formulas, and once here over a learned
correction that is not a registry row. Neither invocation is in the other's range. The corpus
is already using obligation 9 as a surrogate-validity obligation in the place where it has an
actual surrogate to validate; what it lacks is a selector that reaches that object, which is
exactly what F3's 9b supplies. **A6 reaches the same conclusion from the out-of-scope side.**

**A5 supplies a further defect in this section that the table above does not capture.**
`cert-obligations.md:173-174` says of all four: "Each is a `Failed` verdict with a witness."
A `Failed` leaf is a check that ran and did not pass — **present and failing**. That is
precisely what `product.md`'s *refusal is absence* says cannot happen: a refused check "is not
in the compiled kernel, so its key is simply not in any map." The four compose-time refusals
are the corpus's only worked examples of refusal, and all four are implemented as the opposite
of the doctrine they are meant to instantiate. See **A1–A3**.

**What would refute this.** A statement that obligation 4 checks provenance, or that obligation
6's range includes tag comparisons on the `CouplingSpec`. Obligation 6's body is quoted in full
at `:72` and does not; obligation 4's at `:70` and does not.

**Proposed correction.** Re-attribute: unprovenanced coefficient → obligation 8; gap-slope
double count and polarization-convention pairing → a new composition-consistency obligation, or
explicitly no obligation, since a compose-time tag comparison is not the same kind of object as
a numerical check and forcing it into the ten is what produced the mis-numbering; learned
correction without an anchor → obligation 9b once 9 is split. And reconcile the `Failed`-leaf
disposition with *refusal is absence*, which is a doctrine decision, not an edit.

---

### F19 — "Held-out" appears three times in the obligation set and is defined nowhere. Neither held-out set has a stated referent, and neither can be enforced by the oracle library.

**Severity: major. Confidence: high.**

The word carries the whole weight of the corpus's trust claim and has no definition. I searched
`journals/` for `held-out`, `heldout`, `held out`, `development set`, `leave-one-out` and
`generaliz`. Every load-bearing hit is in my three pages:

- `cert-obligations.md:70`, obligation 4 — "in the frozen reference data on a **held-out
  crystal battery**"
- `cert-obligations.md:75`, obligation 9 — "measured on a **held-out development set**",
  complexity "forward pass over the development set"
- `cert-obligations.md:144`, `δ_surrogate` — "measured on a **held-out development set**"

The one well-formed use in the corpus is elsewhere and is not mine: `accuracy-ledger.md:115`
has "a **Wannierization quality gate** on held-out k-points", where the referent is explicit —
k-points not used in the interpolation fit.

**Obligation 4's phrase is ambiguous between two readings with very different strengths.**

(a) *Held-out crystals* — materials absent from training. Under this reading obligation 4 is
evidence of **generalization**.
(b) *Held-out values* — the same materials, values withheld from the training loss. Under this
reading obligation 4 is evidence of **fit**.

Reading (a) is what the phrase naturally suggests and it is **false of the artifact**:
`data/reference-data/` covers 11 material labels — AlGaN, AlGaN/GaN, AlN (wz, wz c-axis),
GaN (wz, wz a-axis), diamond, diamond (holes), diamond (type IIa), β-Ga₂O₃ (C2/m) — which are
exactly the anchor materials of `purpose-and-scope.md`. There are no held-out crystals.

Reading (b) is what `reference-battery.md:167` supports — "**Not a training dataset.** Training
data belongs to the operator library." But that is a statement about the battery's *role*, not
a mechanism, and it points at the problem: **training data belongs to a different library, so
the oracle cannot enforce that its battery was withheld from it.** The literature values in
`transport-coefficients.csv` are the same published numbers an operator-side training set would
draw on. Nothing in this corpus prevents the overlap, and nothing checks for it.

Obligation 9's "held-out development set" is worse, because under the tag it names there is no
set at all: a relaxation is a deterministic function of the same inputs, with no training set
and no development set to hold anything out of. The complexity column — "forward pass over the
development set" — costs an object that does not exist. This is a second, independent
demonstration that the body was written for a learned net (F3).

**What would refute this.** A page defining either set, or stating the mechanism by which the
battery is withheld from operator-side training. I found neither. The seam pages
(`pino-bridge.md`, `learnable-structure-contract.md`) specify what crosses the seam; neither
states a data-partition discipline across it.

**Proposed correction.** Three parts.
1. Replace "held-out crystal battery" with what it actually is — "the curated reference
   battery" — and drop the implication of generalization the corpus cannot support.
2. If a genuine held-out-crystal check is wanted, it is buildable and cheap: the second-anchor
   wave (`reference-battery.md:153-154`) adds cubic boron nitride and 4H silicon carbide, and
   holding *those* out of every fit would give obligation 4 a real generalization arm. That is
   a design recommendation, not a defect report.
3. Define obligation 9b's development set explicitly as part of the split in F3 — for row 6 it
   is the set of quasi-particle calculations withheld from the surrogate's fit, and that set
   has to exist and be named before 9b can be checked.

---

### F20 — The polar-predicate split names β-Ga₂O₃ as the case where the two predicates diverge. Both in-scope gate dielectrics diverge the same way, and they are the materials where the gated path matters most.

**Severity: moderate. Confidence: high.**

`applicability-classifiers.md:74-78`:

> The two coincide on the corpus's anchor materials — diamond, where both are false, and
> wurtzite III-nitrides, where both are true — and **split on β-Ga₂O₃**, which is
> centrosymmetric in `C2/m` …

`traps.md:389-390` restates it the same way: "They coincide on diamond and on wurtzite nitrides
and **split on gallium oxide** — centrosymmetric, yet Fröhlich-dominated."

`purpose-and-scope.md:206-207` puts three gate dielectrics in scope — "gate dielectrics
(Al₂O₃, HfO₂, and AlN as a dielectric)" — and sapphire, which is α-Al₂O₃, among the substrates.
`out-of-scope.md:107-109` confirms the crystalline polymorphs are modelled: "α-alumina,
monoclinic hafnia and aluminium nitride as a dielectric".

Two of those three split exactly as β-Ga₂O₃ does — centrosymmetric and strongly polar:

| Material | Space group | Inversion centre | `is-noncentrosymmetric` | Polar in the Born-charge sense | `is-polar-material` |
|---|---|---|---|---|---|
| α-Al₂O₃ (corundum, sapphire) | `R-3c` (167), point group `-3m` | yes | **false** | strong IR-active `A₂ᵤ`/`Eᵤ` modes; ε_static ≈ 9–11 against ε_∞ ≈ 3.1, i.e. large LO–TO splitting | **true** |
| monoclinic HfO₂ | `P2₁/c` (14), point group `2/m` | yes | **false** | large Born charges; ε_static ≈ 16–25 against ε_∞ ≈ 4–5 | **true** |
| AlN as a dielectric | `P6₃mc` | no | true | yes | true — coincides, as the passage says |

So three in-scope materials split, not one. And the two the passage omits are the ones where
the gated quantity is the whole point: `is-polar-material` gates "the relative permittivity
derived through the Lyddane-Sachs-Teller relation" (`applicability-classifiers.md:66-67`), which
is the corpus's stated method for observable 23, `dielectric_constant_static ε_r`
(`accuracy-ledger.md:136`). A gate dielectric's static permittivity is its defining property.

**This is not a false claim about the physics** — the predicates as defined return the right
answer for both oxides, because polarity is a bond property and the definition says so. It is a
documentation gap in the direction that matters, and the risk it creates is the one the corpus's
own trap register worries about: a builder who reads "split on β-Ga₂O₃" twice, in the two places
the corpus states the rule, may implement the split as a β-Ga₂O₃ special case rather than as a
general consequence of the two definitions. Both statements of the rule invite that reading, and
neither mentions the dielectrics.

**What would refute this.** Either oxide being non-polar or noncentrosymmetric. `R-3c` and
`P2₁/c` both contain an inversion centre — corundum's lack of piezoelectricity follows from it —
and both oxides have ε_static substantially above ε_∞, which by the Lyddane–Sachs–Teller
relation `ε_static/ε_∞ = Π(ω_LO/ω_TO)²` requires LO–TO splitting, hence nonzero Born charges.

**Proposed correction.** Extend the sentence to name all three splitting materials, and state
the split as a consequence of the definitions rather than as a list: *the two predicates diverge
for every centrosymmetric material with heteropolar bonds, which in this corpus is β-Ga₂O₃,
α-Al₂O₃ and monoclinic HfO₂.* One clause, and it converts an enumeration a reader can
under-generalise into a rule they cannot.

**Positive note, since this section is otherwise the best-reasoned passage in my subject.** The
β-Ga₂O₃ analysis is correct in every particular, including the direction of each failure mode,
and the corpus's handling of diamond's permittivity is quietly right for the same reason: with
`is-polar-material` false, diamond has no LO–TO splitting, so `ε_static = ε_∞ = 5.7` and the
Lyddane–Sachs–Teller path is correctly gated off. That is why the diamond static permittivity
must be seeded from the long-wavelength refractive index — which is what
`accuracy-ledger.md:52`'s open question already proposes. The gate and the open question have
the same cause, and neither page says so. *(Flagged to the principal — the value is
postdoc-values', the gate is mine.)*

---

### F21 — The `ω² ≥ 0` gate is decidable, and its listing among swept-environment windows is wrong. *(Resolved from the previous draft's deferred item.)*

**Severity: moderate. Confidence: high.**

The previous draft deferred this to an undergraduate that was lost to the session limit. It is
resolvable from primary text and is resolved here.

**The corpus's design is correct.** `named-formulas.md:326-334` forbids applicability predicates
from deciding "on numeric thresholds **or solver outputs**". A predicate reading `ω²` computed
by a phonon solve would be a solver-output predicate and is forbidden. The corpus avoids this
correctly: `residual-definitions.md:121-123` and `traps.md:394-397` both gate on the *claim* —
"`ω² ≥ 0` is **applicability-gated** to phases **claimed** dynamically stable" — which is a tag,
decidable by case analysis. That is the right design and both pages state it right.

**The defect is one list membership.** `applicability-classifiers.md:135-140` places "the
`ω² ≥ 0` claimed-stable gate" among *validity windows that depend on a runtime-swept
`Environment` scalar* and are "re-evaluated per training sample". A stability *claim* is not a
swept scalar and needs no per-sample re-evaluation against a range set. Two branches, both
defective:

- If the gate is tag-based, as the two owning pages say, it does not belong in that list, and
  its presence there tells a builder to implement a per-sample numeric re-evaluation that has
  nothing to read.
- If the gate is genuinely temperature-windowed — defensible physics, since a phase can be
  dynamically unstable harmonically and stabilised anharmonically at high `T` — then the
  *claim* needs a temperature range, and no page provides one. That is the same missing range
  set as **F9**'s second-order problem.

**What would refute this.** A declared temperature range for the dynamical-stability claim, which would make the swept-window listing correct; or removal of the entry from that list, which would make the tag-based reading complete. Neither exists today, so both branches stay open.

**Proposed correction.** Remove it from the swept-window list and state the gate as tag-based,
which is what the two owning pages say. If the temperature-windowed reading is wanted instead,
it needs a declared stability range per phase, which is a new field and should be recorded as
an open question rather than implied by a list entry.

---

## 2 · Findings that did not survive

**Obligation 7's lookup table is missing.** I suspected the elementary-band-representation table
obligation 7 depends on was promised and absent. It is not: `topology-atlas.md:28-33` declares
`EBRs` as a field of every `TopologyAtlasEntry`, and registry row 102
`boundary-mode-multiplicity-from-classification` is the "indicator-factor → boundary-state
lookup". The table exists. The obligation's *cost claim* is still wrong (F14) but the dependency
resolves.

**Obligation 7 is unimplementable for want of slabs.** Rejected: `property-templates.md:163`
declares `BiSlabGrandPotentialOf(slab-left: Crystal, slab-right: Crystal, …)` and
`typed-compositions.md:292` declares `SurfaceEnergy` over a slab. Slabs are first-class.

**Obligation 4 is circular because the battery both fits the formulas and checks them.** I
tested this on the Caughey-Thomas case, the most likely instance:
`data/reference-data/transport-coefficients.csv` carries both the fit parameters
(`caughey-thomas-mu-n-max/-min/-Nref/-alpha`, GaN, Farahmand et al. IEEE TED 48 535 (2001), a
Monte-Carlo fit) and a mobility value for the same material and temperature
(`mobility-electron-fp-ceiling`, GaN 300 K, Ponce, Jena & Giustino PRB 100 085204 (2019),
first-principles BTE). **Different sources**, so this instance is not circular. The general risk
stands and belongs to whoever owns the battery, but I could not make the charge stick on the
case most likely to carry it, so I am not reporting it as a finding.

**The evidence semilattice is not a semilattice.** Rejected. `Failed < Pending < Passed` is a
three-element chain, the meet is the minimum, and `Failed` absorbs under it. The stated
aggregation rule is exactly the meet. The defect is the identity element (F1), not the algebra.

**`is-polar-material` is wrong for β-Ga₂O₃.** Rejected. The page's claim — centrosymmetric in
`C2/m`, no spontaneous polarization, no piezoelectricity, no pyroelectricity, and at the same
time strongly polar-phonon with a multi-mode Fröhlich interaction as its dominant mobility
limiter — is correct, and the split it motivates is the right one. `C2/m` contains an inversion
centre; polarity in the Born-charge sense is a property of the bonds. This is the best-reasoned
passage in my subject.

**FMA contraction independently breaks `τ_interp`.** *Rejected — this was a claim in the
material handed over, and it does not reproduce.* Two evaluators differing only by an FMA
contraction, 200,000 well-conditioned samples: worst relative gap 8.3e-12, **zero** failures at
1e-10. FMA breaks the gate only in combination with cancellation, and then at the same
conditioning threshold as the rewrite itself, so it adds nothing as a separate mechanism. B3
carries the corrected version.

**The 59 accuracy regimes gate obligation-4 verdicts.** *Rejected as stated — see B8.* The
traced path is regimes → `characteristic-scale` → `combineTol` → error budget. Obligation 4's
trip is `τ_battery`, derived from the reference row's own σ, which is a different quantity. The
weaker claim — 59 numeric tolerances outside the canonical tolerance table, and two pages
claiming to supply the same `combineTol` inputs — is what I carry.

**`τ_cond` is defective only on registry row 5.** *Rejected as understated.* Three of the five
`fixpoint-adjoint` rows have a scalar fixed point and are structurally incapable of tripping the
gate, and a fourth is dormant in V1. B4 carries the extended version.

---

## 3 · Shaped gaps

**None of my findings is blocked on a source, and I want to be precise about why that is not a
free pass.** Every finding above rests on text inside this repository or on arithmetic I ran.
The two literature-dependent threads that touch my subject are owned elsewhere:

- The `0.4 Θ_D` four-phonon threshold against Feng, Lindsay & Ruan PRB 96 161201 — the
  principal's register establishes it is back-derived and mis-attributed. My F12 shows the Θ_D
  it was derived from has internal provenance. The two halves together close the question
  without needing the paper, though the paper would settle whether *any* Debye-scaled criterion
  is defensible.
- The ~25% non-adiabatic zero-point-renormalization figure (`out-of-scope.md:45-49`) — a value
  question, postdoc-values'.

Neither is a gap in the four-part sense, because neither blocks a finding of mine.

---

## 4 · Acquisition requests

**None from this subject.** My findings are internal-consistency findings and arithmetic; no
purchase changes any of them. I note for the principal's list that the Ehrhardt & Roberts entry
(B7) has a recorded volume/year disagreement, and that verifying it is a metadata lookup rather
than an acquisition.

---

## 5 · Calibration result

*Filled below from the blind arm — reported as found, unrounded, including partial.*

---

## 6 · Evidence transcript

**What I am calling clean, and what I am not.** I am not certifying any part of this subject
clean. The subject is dense with defects and the honest summary is that I found more than I
could rank. This transcript therefore records the comparisons I ran — including the ones that
came back clean, which is where a sweep is shown to be real — rather than supporting a clean
verdict.

### Comparisons run, by class

**Contradictions — cross-page claim pairs checked.**

| Pair | Result |
|---|---|
| `Validate`'s return arity and contents: `pino-bridge.md:50-59` vs `product.md:177-182` | **Contradiction** (A7). First three returns agree exactly; fourth differs |
| Out-of-scope raise: `out-of-scope.md:123` vs `pino-bridge.md:203-208` vs `architectural-principles.md:64-70` | **Three-way contradiction** (A3). Confirmed same-commit origin via `git log -L` |
| pino-bridge internal: `:43-44` ("only surface … any other downstream consumer") vs `:203-208` ("remain available … for non-operator consumers") | **Self-contradiction** (A3) |
| `combineTol`'s input source: `cert-obligations.md:122-124` vs `accuracy-ledger.md:454-458` | **Contradiction** (B8). Both claim it; contents disjoint |
| Refusal disposition: `product.md:150-154` vs `crystal-inputs.md:119-122` vs `applicability-classifiers.md:133-140` | **Three-way contradiction** (F9) |
| Refusal shape: `product.md:199-205` ("not in any map") vs `cert-obligations.md:173-174` ("Each is a `Failed` verdict") | **Contradiction** (F18 closing note) |
| Certificate granularity: `cert-obligations.md:80-82` vs `:46-49` vs `compose-time-pipeline.md:314-318` vs `pino-bridge.md:55-58` | **Contradiction** (F10) |
| Obligation 9's subject, four statements: `cert-obligations.md:75` vs `:144` vs `build-verification.md:138-140` vs `:184-190` | **3–1 split** (F3) |
| Obligation attribution in composition refusals: `cert-obligations.md:176-201` against each obligation's own body at `:67-76` | **3 of 4 wrong** (F18) |
| Formula-record field count: `formula-registry.md:43` ("one column per field") vs `named-formulas.md:71-85` (ten fields) vs the manifest (nine columns) | **Contradiction** (F7) |
| `formula-registry.md:43` field list vs `:92-99` vocabulary table | **Self-contradiction**: `applicability` in one, absent from the other (F7) |
| Obligation-4/8 ownership: `cert-obligations.md:70,74` vs `reference-battery.md:31-32,70-71` vs `build-verification.md:167-168` vs `capability-slices.md:60,80,97` | **Contradiction** (F2) |
| `ω²≥0` gate's nature: `residual-definitions.md:121-123` + `traps.md:394-397` vs `applicability-classifiers.md:135-140` | **Contradiction** (F21) |
| Polar-predicate statement: `applicability-classifiers.md:74-78` vs `traps.md:389-390` | **Consistent with each other**, both incomplete against `purpose-and-scope.md:206-207` (F20) |
| Slab machinery: `cert-obligations.md:73` vs `property-templates.md:163` + `typed-compositions.md:292` | **Clean** — slabs are first-class; the dependency resolves |
| EBR table: `cert-obligations.md:73` vs `topology-atlas.md:28-33` + manifest row 102 | **Clean** — the table exists |
| Evidence meet vs the three-element chain | **Clean** — the stated rule is exactly the meet; the defect is its identity, not its algebra |

**Missing crucial information — searched for, with the probe stated.**

| Probe | Result |
|---|---|
| `closed-enum`, `closed enum`, `refusal mode` across `journals/` | 3 + 1 hits; the promised enum **does not exist** (A1) |
| `refus` per file across `journals/` | `compose-time-pipeline.md` = **0**. Control: 20 in `traps.md`, 14 in `accuracy-ledger.md`, 11/9/8/4 elsewhere — the probe works (A2) |
| `\bPending\b` across `journals/` | **1 line**, the rule defining it (A5) |
| `inapplicable` across `journals/` | **2 hits**, both on the page that promises it (A4) |
| `numeric threshold`, `case analysis` | 1 hit each, both `named-formulas.md:329-331` — the normative decidability rule (A4, F21) |
| `unitsOf`, `dimensional consistency`, `unit check`, `dimensional analysis` | **1 hit**, the declaration itself (F15) |
| `held-out`, `heldout`, `held out`, `development set`, `leave-one-out`, `generaliz` | Every load-bearing hit is on my own pages; one well-formed use elsewhere (F19) |
| `coverage_mask`, `coverage-mask`, `CoverageMask`, `axis-coverage` | Two hits inside the subject, both schema lines; **no obligation reads it** (F13) |
| `vacuous`, `non-empty`, `nonempty`, `empty set`, `no leaves`, `at least one obligation` | 9 hits, **none about the evidence semilattice** (F1) |
| `sidecar` across `journals/` | 30 hits; `compose-time-pipeline.md:114` and `physics-graph.md:241` both say the applicability sidecar is destroyed (A2) |
| `exception`, `never raised` | `architectural-principles.md:67-70` is the only normative statement, and it forbids the mechanism `out-of-scope.md:123` specifies (A3) |
| numerical-noise floor | **Absent** — a definite description of a quantity never stated (F17) |
| tolerance symbols in prose vs ledger rows | `τ_soft`, `δ` (manifest), the degeneracy tripwire's threshold, and 59 accuracy regimes are all absent (F6, F11, B8) |

**Arithmetic and computation done, not taken on report.**

| Computation | Result |
|---|---|
| Tolerance-ledger row count, and the number/policy/basis split | 17 rows; 12 numeric, 5 policy; 11 with no basis. Reproduces the principal's split exactly (B0) |
| `τ_cons` "following `τ_SCF,strict`": 7.37 eV ÷ 27.211386 eV/Ha = 0.270843 Ha; 1e-8 ÷ 0.270843 | **3.69e-8**, reproducing the principal's 3.7e-8 (B2) |
| `Conservation` invariants, counted from `residual-definitions.md:113-118` | 4 invariants; **1 is an energy** (B2) |
| `rcond` of a 1×1 matrix `[a]` for `a ∈ {1e-30, 1e-3, 1, 1e12}` | **1.0** in every case; gate `> 1e-8` passes always (B4) |
| `fixpoint-adjoint` population and each row's fixed-point dimension | 5 rows; **3 scalar**, 1 dormant, 1 live-and-gateable (B4) |
| `∂F/∂E_F ≈ −(n+p)/k_BT` for intrinsic diamond, 300–1200 K | **35.1 orders**; 11.8 orders over the stated 600 K+ window (B4) |
| `τ_interp` breakdown scan, distributivity rewrite, IEEE-754 double, 60,000 samples per point | First failure at **κ ≈ 10²**, not 10⁷ (B3) |
| `τ_interp` benign case, 2,000,000 samples | Worst 6.29e-11; **margin 1.59×**, not the reported 1e-14 (B3) |
| FMA contraction alone, 200,000 samples | Worst 8.3e-12, **zero** failures — the claim does not reproduce (B3, §2) |
| Zero-true-value residual, three tolerance forms | Absolute uninformative; relative-to-true **undefined**; relative-to-norm 1.7e-32 (F11, B3) |
| Accuracy-regime table row count, `accuracy-ledger.md:110-173` | **59**, matching the page's own stated count at `:100-101` (B8) |
| Total tolerances in corpus vs ledger rows | 17 of ~78 = **22%** (B8) |
| Manifest column count and `applicability` / `adjoint-validated` presence | 9 columns; **neither present**, across all rows (F7, F8) |
| `reference-data/` material labels, counted | 11 labels, all anchor materials; **no held-out crystals** (F19) |
| `reference-data/` rows with an internal-only `Source`, and their declared `Source class` | 179 rows; **8 internal-only, 4 of them declaring `experimental`**. Corrects the previous draft's 10/2 (F12) |
| Caughey-Thomas circularity test, source-by-source | **Different sources** — charge does not stick (§2) |
| `D`-code mapping verified against `agent-contract.md:238` before relying on it | `D0:read, D1:direct, D2:adjoint, D3:fixpoint-adjoint, D4:relaxed, DN:none` |

**Controls run on negatives.** Every "X does not appear" above was paired with a probe that
finds something, so an empty result is a fact about the corpus rather than about my grep. The
two that mattered most: the `refus` count is reported per-file with the non-zero files listed,
so `compose-time-pipeline.md`'s zero is visibly a zero among positives; and the `Pending` search
used the same word-boundary pattern that returns the defining line, so its single hit is the
whole population rather than a pattern failure.

### Near-findings considered and dismissed

Beyond the seven in §2, these were examined and not written up:

- **`τ_SCF,train` (1e-4 Ha) is 10⁴ looser than `τ_SCF,strict`.** Considered as a defect; it is
  not. The row states the split's purpose ("on the runtime and training path, looser") and a
  looser convergence on the training path is ordinary practice. No basis is stated for either
  number, which is counted once in B0's 11-of-17 rather than reported twice.
- **`δ_sym = 1e-6 relative` is loose for a projection residual.** Considered; not a finding. It
  is relative, so it is at least dimensionally coherent — which is more than `δ_PSD` manages —
  and 1e-6 on a sampled projection is defensible. It has no stated basis, which B0 counts.
- **Obligation 1's "trivial-irrep projector" duplicates the coupling-derived check at
  `:102-105`.** Examined; the second is explicitly the specialised form of the first for
  generator-produced nodes, and the page says so. Not a defect.
- **`τ_L3L4`'s "at most 5 iterations" is a policy smuggled into a tolerance row.** True, and
  minor; it is a real observation about ledger hygiene but does not change any behaviour, and
  B0's policy count already captures the pattern.
- **The SQLite cache's write-once discipline conflicts with tombstoning.** Read carefully;
  `:231-233` is coherent — an update writes a new row and the obsolete one is tombstoned through
  `provenance.version`, with no in-place mutation. Not a contradiction.
- **`schema_version` is both "part of every `Address`" and "never part of the key".** Looked
  like a contradiction; it is not. `:226-230` distinguishes the *type-level* schema version,
  which enters the address, from the *per-row column*, which is compared by the reader. The
  distinction is stated. Clean, and one of the more careful passages in the subject.
- **Obligation 10 "never at prediction" contradicts the certificate being per-prediction.**
  Folded into F10 rather than reported separately — it is one of the three ways the granularity
  ambiguity bites, not an independent finding.
- **`out-of-scope.md`'s β-Ga₂O₃ hole-transport exclusion overstates the physics.** Checked: flat
  valence bands, small-polaron self-trapping, and the ~3.5 eV luminescence being
  free-electron-to-self-trapped-hole rather than band-edge are all correct as stated. The
  passage is right, and "the refusal is the correct output" is the right conclusion. Not a
  finding — recorded because it is the strongest paragraph on that page.

---

## 7 · Log-worthy advancements

Reported to the principal, not written to `log/timeline.md`.

1. **"Refusal is absence" has no implementing dataflow.** The applicability sidecar — the map
   `NodeId → Predicate` that *is* the machine-readable reason the product promises — is
   constructed, used to delete nodes, and discarded, in one compile stage, before any obligation
   runs (A2). Every other refusal defect in this subject is downstream of that one fact. The fix
   is to emit an evidence leaf before the discard, and it is small.
2. **The evidence semilattice's identity is `Passed`, so a certificate over an empty leaf set
   certifies clean** (F1), and pruning supplies a second path to emptiness in which the verdict
   *improves* as more physics is deleted (A2). One-value fix, with `Pending` — a verdict nothing
   currently produces (A5) — as the identity.
3. **The corpus's canonical tolerance table holds 17 of roughly 78 tolerances**, and two pages
   each declare themselves the source of `combineTol`'s inputs with disjoint contents (B8). This
   is the reason obligation 4 looked untoleranced (F2): its tolerances exist, on another page,
   under another name.
4. **Obligation 9's open question resolves to a split plus a new selector axis**, and three
   independent routes reach it — the registry side (F3), the composition-refusal side (F18) and
   the out-of-scope side (A6). The second half cannot select on the differentiability tag at all,
   because that field answers a question about gradients and "learned" is a fact about
   provenance.
5. **A conditioning gate that is structurally incapable of firing on three of the five rows it
   governs** (B4), on rows whose own provenance cells say the conditioning problem is real and
   is worst exactly where the corpus operates.
6. **The obligation set has no dimensional-consistency check**, and the manifest records three
   dimensional defects found by hand that it would have caught (F15) — plus two more at the
   tolerance level (B2, B6) that a formula-level check would still miss.
