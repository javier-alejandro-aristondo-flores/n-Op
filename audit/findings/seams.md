# The seams — oracle ↔ operator, in both directions

Subject: `journals/oracle/seams/pino-bridge`, `journals/oracle/seams/residual-machinery`,
`journals/operator/seam/learnable-structure-contract`,
`journals/operator/training/training-stages`, `journals/operator/loss/residual-loss-design`,
`journals/interface/boundary`.

Baseline at time of audit: `python tools/check_structure.py --check` → `structure OK · 45
pages, 273 owned topics, 51 open questions`; `python tools/check_the_checker.py` → `probes:
34 · caught 34 · missed 0`. **Not one finding below is visible to either checker**, which is
the premise of the audit rather than a complaint about the tools.

---

## 1 · Findings

Identifiers are stable; the sections below are in the order they were written, not in severity
order. This index is the reading order.

| | finding | class | severity |
|---|---|---|---|
| **S1** | `coverage-mask` retired in prose only — survives in the persisted schema, the content address, and the glossary's live-name table; and there is a **fourth** sense | contradiction + misinterpretable | high |
| **S2** | the axis-coverage flat index has no stated ordering, and feeds a content address that outlives it | missing information | high |
| **S3** | `Import` keys its leaf by "the named target's `ResidualKey`"; an observable does not determine one | contradiction | high |
| **S18** | operator side batched, oracle side has no batch concept, compilation unit finer than a batch element | missing information | high |
| **S4** | `ObservableRef` and `Cotangent` are specified nowhere | missing information | high |
| **S7** | `Polish` names two different 30% windows; the declared open question mis-states its own defect | contradiction + misinterpretable | high |
| **S9** | "structural projection" carries two incompatible cost claims and is defined neither time | false claim | med-high |
| **S6** | the oracle picks a loss function its own record field forbids and the operator declares open | contradiction | high |
| **S15** | the per-key error budget is computed, exported, and never used by the loss | missing information | med-high |
| **S16** | the evolver hand-off exports the representation-health problem and withholds the instrument | missing information | med-high |
| **S17** | the surrogate-relaxation worked example is one-signed; its sign carries nothing | false claim | med-high |
| **S8** | build gate 3: three phases where there are four, and cites the wrong side of the seam | contradiction | med-high |
| **S20** | "a row critical to the MVP silently leaves the differentiable path" is marked enforced; nothing enforces it | false claim | med-high |
| **S5** | `named-formulas` assigns evaluation frequency to the residual factory | contradiction | med-high |
| **S13** | a curriculum phase turns on a consistency pair one leg of which is dormant | missing information | medium |
| **S10** | determinism contracted in one direction only, and not on the side doing the arithmetic | missing information | medium |
| **S11** | key-set drift across recompiles is unowned | missing information | medium |
| **S12** | "discretisation invariance" asserted flatly; a fourth silent failure omitted from a list claiming completeness | false claim | medium |
| **S19** | the adjoint cost claim drops the compilation page's qualification and generalises across two tiers | false claim | low-med |
| **S14** | `Validate`'s fourth return value stated two ways | contradiction | low-med |

### S1 — The retired token `coverage-mask` survives in the persisted schema, in the content address, in the glossary's live-name table, and in a **fourth** sense the retirement never enumerated

**Severity: high. Confidence: high.**

`glossary.md:185` retires the token explicitly, and states the reason in the corpus's own
words:

> | `coverage-mask` | nothing — three unrelated masks multiply into one loss | `axis-coverage`
> for axis-tuple coverage, `applicability-mask` for per-sample applicability,
> `label-presence` for label presence per source |

`pino-bridge.md:99-108` restates the hazard and is emphatic:

> `AxisCoverage` declares **which axis tuples of the named target the imported datum actually
> constrains**. That is the only thing it means here. […] All three multiply into the same
> loss term, so one name shared across them yields a loss that is wrong and reports clean.

The rename is prose-deep. The token survives at six sites:

| site | form | what it means there |
|---|---|---|
| `cert-obligations.md:212` | `coverage-mask` | inside the **content address** of a reference-cache entry |
| `cert-obligations.md:217` | `coverage_mask BLOB` / `RoaringCoverageMask` | the persisted **column and type** |
| `cert-obligations.md:223` | `coverage_mask` | the key-construction tuple |
| `glossary.md:99` | `RoaringCoverageMask` | registered as a **live** name in "Where a name is specified", 86 lines above the entry that retires it |
| `multiscale-state.md:469` | `RoaringCoverageMask` | **a fourth sense** — see below |
| `product.md:220` | "coverage-masked" | axis-coverage; unambiguous in context but in the retired spelling |

Plus `data/diamond-strain-sweep/02-how-to-read-and-derive.md:27`, which is what an
implementer reads when wiring the actual training data.

Three consequences, in descending order of how quietly they fail.

**(a) The seam page names a column that does not exist.** `pino-bridge.md:126-128` says the
serialised bytes "are stored in the **axis-coverage column** of the reference cache's entry
table" and cites `[cert-obligations#reference-cache]`. That table has no `axis-coverage`
column; it has `coverage_mask`.

**(b) There is a fourth sense.** `multiscale-state.md:469`:

> a `RoaringCoverageMask` over `enumerate(product(MeshCell, MacroField))` selects the
> constrained subdomain.

That is subdomain selection over a device mesh crossed with macro fields — not axis-tuple
coverage of an imported datum, not per-sample applicability, not label presence. The
retirement note enumerates three senses; the corpus contains four. A split that is not
exhaustive is not a split.

**(c) The retirement prescribes a name nobody uses.** `glossary.md:185` prescribes
`applicability-mask`; `residual-loss-design.md:310` writes `sample-applicability-mask` and
its `owns:` list at `:14` writes `sample-applicability mask`.

**Why nothing caught it.** `coverage-mask` is absent from the `retired-vocabularies` block at
`agent-contract.md:230-256`, which is the list the vocabulary sweep enforces; and `glossary`
is exempt from that sweep by design ("disambiguates retired tokens from the external names
they shadow", printed by `check_structure.py`). The one page allowed to write the retired
token is the page that registered it as live.

**What would refute this.** A statement anywhere that `RoaringCoverageMask` and
`AxisCoverage` are deliberately two types with different domains — I looked and found none;
`AxisCoverage` and `RoaringAxisCoverage` occur **only** on `pino-bridge` (3 and 1 occurrences
respectively, corpus-wide), and `RoaringCoverageMask` occurs only on `glossary`,
`cert-obligations` and `multiscale-state`. The two vocabularies do not meet anywhere.

**Proposed correction.** Add `coverage-mask` to `agent-contract`'s `retired-vocabularies`;
rename the SQLite column and type on `cert-obligations`; delete the `RoaringCoverageMask` row
from the glossary's live-name table and add `AxisCoverage`; give `multiscale-state`'s fourth
sense its own name and add it to the retirement note; fix `pino-bridge`'s column name.

---

### S2 — The axis-coverage flat index has no stated ordering, and it is part of a content address that outlives the ordering it depends on

**Severity: high. Confidence: high.**

`pino-bridge.md:113-116`:

```
flat-index(axes) = enumerate(product(axes))   -- lexicographic over axis values
RoaringAxisCoverage = serialised Roaring bitmap of selected flat-index positions
```

A Roaring bitmap is a set of integers. Its meaning is entirely carried by the index those
integers point into. Three things are unstated, and each one is sufficient on its own to make
a stored mask decode to the wrong set of axis tuples with no error raised.

**(a) No total order on axis values.** `axes : List<AxisLabel>` where the labels are
"(k-point, frequency, atomic pair, shell, …)" (`residual-machinery.md:83-85`). "Lexicographic
over axis values" presupposes a total order on k-points, on atomic pairs, on shells. None is
stated anywhere. Two implementations that both correctly implement the instruction can
produce incompatible bitmaps, and each will validate.

This is not a hypothetical gap in a corpus that elsewhere takes canonicalisation seriously:
`representation-substrate.md:155-183` gives an eleven-rule canonical serialisation covering
records, sequences, sets, maps, sum types, group actions, optionals and floats. Rule 4 covers
the *outer* product (`Sequences … elements in declared order`), so the axis order is fixed.
The *inner* value sets are covered by rule 5 — "sorted by **address bytes** … so order cannot
leak into identity" — which is a different order from "lexicographic over axis values", and
which is explicitly designed to destroy the property `flat-index` requires. The corpus
therefore contains two candidate orderings for this construction and they disagree.

**(b) The index depends on the compose-time grid, and the grid is not in the content
address.** The axis grids are "instance-specific, symmetry-quotiented axis grids fixed at
compose time" (`learnable-structure-contract.md:105-108`, citing
`compose-time-pipeline#symmetry-quotient`). The cache key is
`ContentAddress over (observable, value, sigma, provenance, coverage-mask)`
(`cert-obligations.md:212, 223`) — the grid is absent. The cache is described as one of "the
**persistent** components of the oracle library" and is read concurrently "from the training
process and the cert evaluator" (`cert-obligations.md`, reference-cache section), so it
outlives any one composition, while the index its masks are written against does not.

**(c) The integrity story rests on the key covering what matters.** `cert-obligations.md`
states "a tampered payload changes the key and trips the obligation-8 freeze comparison". The
key does not cover the index without which the mask is meaningless, so a mask that has
silently reindexed is byte-identical to a correct one.

**What would refute this.** A stated canonical order for k-points / pairs / shells, or a grid
fingerprint in the cache key, or a statement that a cache entry is invalidated on recompile. I
swept `journals/` for `lexicograph|canonical order|index order|ordering|sorted|total order`;
the only hits bearing on this are `representation-substrate.md:164-178` (which gives the
conflicting rule) and `unified-state.md:76`, which declares per-slot index order unspecified —
a *different* gap, honestly declared, and not this one.

**Proposed correction.** State the total order per `AxisLabel` type on the page that owns
axis labels, and put the compose-time grid fingerprint in the cache key. Until then this is a
correctness hazard on the one export whose whole job is to say which points a datum
constrains.

---

### S3 — `Import` keys its leaf by "the named target's `ResidualKey`", and an observable does not determine a `ResidualKey`

**Severity: high. Confidence: high.**

`pino-bridge.md:90-93` — Import "inserts a pinned `Input` node carrying `(value,
standard-deviation)` and a **cert-only** `ResidualLeaf` node keyed by **the named target's
`ResidualKey`**".

`residual-definitions.md:216-217` defines the key:

```
ResidualKey = (producer : Producer, axes : Tuple<AxisLabel>)
Producer    = Formula(NamedFormula) | Method(NamedMethod)
```

A `ResidualKey` belongs to a *producer*, not to an observable. `Import`'s signature
(`pino-bridge.md:77-82`) takes `named-target : ObservableRef` and **no formula and no
method**, so a `GroundTruthBridgeGenerator` has neither `Producer` case available. Two
distinct defects follow:

**(a) The phrase presupposes a function that does not exist.** "The named target's
`ResidualKey`" reads as though an `ObservableRef` determines a key. It cannot, whenever an
observable has more than one producing formula — and the corpus guarantees that case exists,
because `Algebraic/MethodEquivalence` is an entire residual category defined as "different
formulas claiming the same observable agree on their shared domain"
(`residual-definitions.md:154-155`). Concretely: registry rows 25
(`single-mode-rta-lattice-kappa`), 121 (`kappa-4phonon-high-t-correction`) and 122
(`iterative-lbte-kappa`) all output lattice thermal conductivity, and
`residual-definitions.md:173-175` binds 121 and 122 to 25 as a consistency pair. Importing a
measured diamond κ is ambiguous three ways.

The accuracy ledger settles that this is live rather than hypothetical.
`accuracy-ledger.md:126`, observable 13 `thermal_conductivity κ(T)`, states that "the anchor is
the iterative solution near 2200, **not** the relaxation-time value near 1800" — one
`ObservableRef`, disambiguated in prose *by naming which producing row is meant*, which is
precisely the information `Import`'s signature has no field for. (That the ledger's chosen
anchor, row 122, is dormant in V1 per `residual-machinery.md:209-219` is a separate matter
belonging to the accuracy subject; reported to the principal.)

**(b) A bridge leaf has no distinct key even when the observable has one producer.** If the
bridge leaf takes the producing formula's key, it *collides* with the physics leaf for the
same formula and axis tuple — and `residual-definitions.md:226` guarantees collision:
"Two evaluations with identical inputs produce the identical key." The operator holds
`Map<ResidualKey, Weight>` (`residual-definitions.md:227-228`). One weight would then govern
both a law residual and a data comparison. That is the "wrong and green" failure the seam
pages are written to prevent.

**What would refute this.** A third `Producer` case, or a statement that an `ObservableRef`
resolves to a canonical producing formula. `Producer` has exactly two cases corpus-wide, and
`ObservableRef` is not specified anywhere at all (see S4).

**Proposed correction.** Add a `Bridge(ObservableRef, Provenance)` case to `Producer`, or key
bridge leaves in a separate map. Either way `residual-definitions` and `pino-bridge` have to
agree, and today they do not.

---

### S4 — `ObservableRef` and `Cotangent` — the two type names that carry the seam's two channels — are specified nowhere

**Severity: high. Confidence: high.**

The glossary states its own rule (`glossary.md:63-66`): "If a name is missing from both, no
page claims it. **That is a finding**, not a lookup failure."

I harvested every CamelCase identifier appearing inside fenced code blocks on the six seam
pages and checked each against the glossary's "Where a name is specified" table and against
`generated/corpus.json`'s topic map. Setting aside inline-defined enum constructors
(`UniformBatch`, `ValidationOnly`, `Passed`, `NotApplicable`, `ConsumedBy`, `Skip`, `Compute`,
…) and names cross-referenced in adjacent prose (`Crystal` and `Environment` →
`crystal-inputs`, `residual-machinery.md:101`; `Quantity` → `typeclass-alphabet#quantity`),
two load-bearing types are genuinely unowned:

**`ObservableRef`** — 7 occurrences corpus-wide, all uses, zero definitions
(`pino-bridge.md:53, 56, 77`; `residual-machinery.md:61, 123`; `compose-time-pipeline.md:337`;
`cert-obligations.md:213`). It is: one of the three legal values of `Validate`'s `request`
parameter; the key of the `values` map, i.e. the *entire observable output channel of the
seam*; the sole identifier of an `Import` target; a field of the generator record; and a
serialised column in the persisted reference cache. No page says what one is, whether it names
a registry row, a bundle member or a ledger observable, or how a consumer obtains a valid one.
S3 is a direct consequence of this gap.

**`Cotangent`** — 3 occurrences, all uses, zero definitions (`pino-bridge.md:57`;
`compose-time-pipeline.md:336`; `residual-definitions.md:267`). `learnable-structure-contract.md:120`
does fix its *shape* — "a cotangent structured like the emitted state" — which is enough to
implement against, so this is the weaker half of the finding. What is missing is the type
entry, not the semantics.

Also unindexed but lower stakes: `TypedSlot` (2 uses, no definition), `AxisCoverage` /
`RoaringAxisCoverage` (see S1), `DressedQuantity`, `StateSnapshot`, `BundleName`,
`SamplingPolicy`, `NamedFormula`.

**Why nothing caught it, and why the checker actively blesses the S1 defect.**
`tools/check_structure.py:231-249`, `check_name_index`, validates in **one direction only**:
for each row already in the glossary, it asserts that the cited page uses the token. It never
asks the converse — for each type name used in a signature, is it indexed? Its own docstring
names the gap it does not close ("the rules validate pointers, and a name index is a set of
claims"), and this is a *different* gap: the set of claims is not required to be complete.
A consequence worth stating plainly: `glossary.md:99` maps `RoaringCoverageMask` to
`[cert-obligations#reference-cache]`, and `cert-obligations.md:217` does use that token — so
the checker **passes** the row, confirming the retired name of S1 as correctly indexed.

**What would refute this.** A definition site I missed. The greps are single-token and
exhaustive over `journals/`; I have listed every occurrence of each.

---

### S20 — The hazard "a row critical to the MVP silently leaves the differentiable path" is marked enforced, and nothing enforces it

**Severity: medium-high. Confidence: high.**

`traps.md:645-652`, on the `none` differentiability tag:

> `none` asserts that no relaxation **exists**, not merely that none has been written. It is
> therefore the label most often wrong. […] *Breaks:* **a row critical to the minimum viable
> product silently leaves the differentiable path.** — enforced, `[named-formulas#diff-tags]`

Three things have to hold for "enforced" to be true, and none does:

1. **`named-formulas#diff-tags` is a definition, not a check.** It says what the six values
   mean and warns that `none` is "the strongest claim in the vocabulary". A definition cannot
   fire.
2. **No tool reads the registry.** `data/registry-manifest.csv` is called "canonical and
   machine-readable" at `named-formulas.md:44-46`, and `grep -rn "registry-manifest\|csv"
   tools/*.py` returns two hits: a regex that matches `.csv` in a line-number citation, and a
   probe *string* in `check_the_checker.py`. `check_structure.py`'s six checks
   (`check_frontmatter`, `check_topics`, `check_citations`, `check_name_index`, `check_tables`,
   `check_vocabulary`) all operate on `journals/*.md`. The `Diff` column is never read by
   anything.
3. **There is no machine-readable notion of "critical to the MVP" to check against.** The MVP
   capability set is prose across `mvp-system` and `capability-slices`; nothing joins it to
   registry rows.

So the one hazard in the corpus that states my brief's question — is a targetable quantity
actually on the differentiable path — is recorded as handled and is not. This is the
"prior clearance is not evidence" pattern in a new place: not a stale audit verdict, but a
stale *enforcement* claim.

**What would refute this.** A checker I have not found. `tools/` contains exactly two Python
files; I read the check list of both.

**Scope note.** The trap register belongs to the practice subject and the registry to the
registry subject; what makes this mine is that the unenforced property is the seam's
targetability contract. Reported to the principal as well.

---

### S5 — `named-formulas` assigns evaluation *frequency* to the residual factory, contradicting its own next clause and citing a responsibility list that does not contain it

**Severity: medium-high. Confidence: high.**

The corpus draws a clean distinction and then breaks it in one sentence. The distinction, at
`residual-loss-design.md:242`: "Cadence says how often. Sampling says **which points**." And at
`:216-221`:

> Cadence is **how often** a residual is evaluated during training. It is a property of the
> training loop, not of the formula. **The oracle owns no loop, so it owns no cadence.**

The break, at `named-formulas.md`, closing paragraph of `#cost-tiers`:

> The cost value is what **the residual factory reads when it decides how often to sample a
> generator** ([residual-machinery#factory]); the decision itself, and the cadence vocabulary
> it is expressed in, belong to the operator.

Two defects in that one sentence:

1. **It contradicts itself across its own semicolon.** The factory decides how often; the
   decision belongs to the operator. Both cannot hold.
2. **Its citation does not carry the claim.** `residual-machinery.md:52-54` enumerates the
   factory's responsibilities exhaustively — "It has three responsibilities: generate the leaves
   with content-addressed keys, gate registration on adjoint correctness, and provide the
   per-formula metadata the runtime kernel uses for its outputs." Deciding evaluation frequency
   is not among them. This is the "dangling promise" shape: the anchor resolves, the page is
   real, the claim is not there.

**What I checked and did not find, so that the finding stays the right size.** I first read the
oracle's `sampling-policy` field (`residual-machinery.md:94` — `UniformBatch | RAD(τ) |
Importance | ValidationOnly`) as a second instance of the same overreach. It is not.
`boundary.md:53-55` gives the loops library "**Active learning.** Residual-adaptive sampling
**beyond a formula's declared policy**", which accepts that a formula declares a sampling
policy; and under the corpus's own sampler/cadence split, *which points* is legitimately the
oracle's while *how often* is not. The field is consistent with both pages. The finding is
`named-formulas`'s sentence alone.

**What would refute this.** A reading on which "how often to sample" means "which points". The
surrounding paragraph is entirely about per-step and per-epoch rates and about "a `minutes` row
sampled as though its cost value were a cadence […] sampled at the wrong rate", so the sentence
means frequency.

**Proposed correction.** Delete the first clause and let the second stand.

---

### S6 — The oracle specifies a loss function for a residual subtype, which its own record field forbids and which the operator page declares open

**Severity: high. Confidence: high.**

Three statements, and they cannot all stand.

1. `compose-time-pipeline.md:353` — "**Loss aggregation lives in the operator library, not
   here**". `residual-machinery.md:92` — `weight-policy : ConsumedBy(operator)`, commented
   "the oracle declares the granularity; aggregation is downstream".
2. `residual-machinery.md:139-145`, the ground-truth-bridge subtype — "**the loss is a Huber
   scaled by the standard deviation** that `Import` call supplied for that datum." That is a
   loss function and its scale, chosen on an oracle page.
3. `residual-loss-design.md:368-375` — "**Which standard deviation scales it is not fixed, and
   this page does not pre-empt it.** The seam supplies two, and does not conflate them […]
   Both are reachable across the seam; only the per-datum one varies per measurement."

So the operator page carries an open question (`residual-loss-design.md:54-56`,
`experimental-sigma-source`) about a choice the oracle page has already made, in the direction
the operator page describes as one of two live options — and the oracle page was not entitled
to make it.

**What would refute this.** That the two Huber terms are different objects — the oracle's
bridge residual and the operator's experimental data term. If so, nothing says it, and the
`compared-against` enum (`residual-loss-design.md:272-275`) makes an experiment battery a
per-generator comparison target, which points the other way. This is the question I put to the
gradient-path undergraduate; see §2 for the disposition.

---

### S7 — `Polish` names two different 30% windows of training

**Severity: high. Confidence: high.**

Two schedules, four phases each, three shared interior breakpoints, and **the third and fourth
phase names are rotated by one against each other**:

| | Schedule A — residual-category gate, `residual-definitions.md:283-288` | Schedule B — source-weight curriculum, `residual-loss-design.md:329-332` |
|---|---|---|
| `[0.00, 0.10)` | Warmup | Warm-up |
| `[0.10, 0.60)` | Refine | Refine |
| `[0.60, 0.90)` | **Polish** | Calibrate |
| `[0.90, 1.00]` | Cooldown | **Polish** |

`training-stages.md:116-118` addresses the pair and stops one step short:

> They share their endpoints, which is the reason to say plainly that they are addressed
> separately here.

Sharing endpoints is the harmless half. Sharing a *phase name* for two different intervals is
the harmful half, and no page says it. A reader who is told "raise the residual weight in
Polish" cannot determine whether that means `[0.60, 0.90)` or `[0.90, 1.00]`, and the two
readings differ by 30% of the training run and by which schedule's knob is being turned.

**The declared open question mis-describes its own defect.** `residual-definitions.md:49-51`:

> "Consumers of this gate name three phases where it names four, and a further vocabulary
> substitutes **Calibrate for Cooldown**. The phase set is not agreed across the seam."

Calibrate is at position 3 and Cooldown at position 4. The substitutions are Calibrate-for-
**Polish** and Polish-for-**Cooldown**. A maintainer who resolves the question exactly as
written — renaming Cooldown to Calibrate — produces `Warmup/Refine/Polish/Calibrate` against
`Warm-up/Refine/Calibrate/Polish`, in which **both** contested names now appear in both
schedules at swapped positions. Following the instruction correctly makes the corpus worse.
This is the corpus's own named hazard class, realised inside a declared open question.

Separately, "Consumers of this gate name three phases where it names four" no longer describes
the corpus: `residual-loss-design` names four. The only surviving three-phase claim is S8.

**What would refute this.** A disambiguating use of `Polish` somewhere. I swept `journals/`,
`README.md`, `data/` and `tools/` for all six phase names: 20 hits, of which the only use
outside the two defining tables and their own prose is `multiscale-state.md:286` — "Curriculum
band: **Refine**, `[0.10, 0.60)`" — which disambiguates by carrying the interval, and is
therefore clean. So the collision is currently latent rather than realised. It is a hazard
armed and not yet fired.

**Proposed correction.** Rename one of the two `Polish` phases. `residual-loss-design`'s
fourth phase is described as "all four balanced by GradNorm | final equilibrium" and
`residual-definitions`'s fourth as "weights frozen for final evaluation" — these are different
enough that neither name is forced.

---

### S8 — The build gate that reaches across the seam asserts three phases, cites the wrong side of the seam, and cannot be satisfied as written

**Severity: medium-high. Confidence: high.**

`build-verification.md:170-179`, Gate 3 — curriculum sanity:

> A synthetic **three-phase** training run on bulk silicon […] This gate is the one place a
> build check reaches across the seam into training. The curriculum phases and their gating
> fractions are **owned on the operator side** ([residual-definitions#curriculum-gate]); what
> this gate asserts is only that a run of that shape completes.

Three defects in one paragraph:

1. **Three phases.** Both schedules have four (S7). No three-phase schedule exists in the
   current corpus. A gate asserting that "a run of that shape" completes names a shape nothing
   defines.
2. **Wrong side of the seam.** The sentence says the phases are owned on the *operator* side
   and cites `residual-definitions`, which is an **oracle** page
   (`journals/oracle/laws/`) and which states at `:277-279` that "**The oracle** specifies the
   default schedule". The operator-side schedule is `residual-loss-design#curriculum`. The one
   gate whose stated purpose is to reach across the seam points at the wrong side of it.
3. Consequently the gate exercises whichever schedule the implementer guesses.

This is the pre-restructure contradiction `program`/C7 in the inherited register ("How many
curriculum phases are there?"), surviving the restructure in a new location. The old sites
(`8.7:70`, `7.2:218`, `11.8:332`) are gone; `build-verification.md:172` is new.

**What would refute this.** A three-phase schedule I have not found. `grep -rn
"three-phase\|three phase"` over `journals/` returns exactly two hits: this gate and the
frontmatter summary quoted in S7.

---

### S9 — "Structural projection" carries two incompatible cost claims, and the granular-cotangent export rests on it

**Severity: medium-high. Confidence: medium-high.**

The phrase appears exactly twice corpus-wide, is defined neither time, and states a different
cost each time.

`residual-definitions.md:326-330`:

> One compose-time pipeline therefore produces a kernel that emits the full
> `Map<ResidualKey, Scalar>` in a single forward pass at no extra cost over emitting one
> aggregated scalar; reverse mode produces the per-key gradient by structural projection of
> **the same pullback**.

`compose-time-pipeline.md:342-344`:

> the optional adjoint pass is reverse mode by structural projection, **linear in the residual
> vector's size**.

One pullback, or a number of pullbacks linear in the key count. These are not the same claim,
and the second is the correct one for reverse-mode automatic differentiation over a
vector-valued output: recovering the full Jacobian costs one reverse sweep per output row.

The first claim is not merely imprecise, it is contradicted by its own page two paragraphs
earlier. `residual-definitions.md:319-321` establishes the condition under which the
projection is impossible:

> Two contributions sharing 99% of their DAG ancestry — for example, all Kramers–Kronig
> identities sharing one dielectric-function computation — is the common case.

Shared *upstream* ancestry is exactly the case in which per-key adjoints superpose in the
shared subgraph and cannot be separated after the fact; separating them requires carrying `k`
adjoint values through the shared region, which is `k` sweeps' worth of work.

**Why this is a seam finding rather than a laws finding.** The whole granularity contract
exports `cograds : Optional<Map<ResidualKey, Cotangent>>` (`pino-bridge.md:57`) — one
state-shaped cotangent per key, i.e. the materialised Jacobian — and
`learnable-structure-contract.md:118-126` then has the *loop* linearly combine them into one
state-shaped cotangent before handing it to the operator. The seam is arranged so the operator
pays one vector–Jacobian product and the oracle pays `k` reverse sweeps, and the corpus states
in one of its two cost sentences that the oracle side is free. The cheap alternative — the loop
hands the oracle its weight vector and the oracle returns `Σ_k λ_k ∂r_k/∂x` in one sweep — is
foreclosed by `weight-policy : ConsumedBy(operator)` (`residual-machinery.md:92`), and no page
records that trade.

**What would refute this.** A statement that the residual family is *block-separable* over its
axes — that residual at axis point `q` depends on state components at `q` alone. Under
block-diagonality one seeded reverse sweep does recover all blocks, and the "structural
projection" claim would be correct *for that family*. `gamma-hat` does describe a
block-diagonal reciprocal-space encoding, so this may be true of some residual families. It is
not true of the example `residual-definitions` itself gives (Kramers–Kronig identities sharing
one dielectric function), and the claim is stated unconditionally. **This finding is that the
claim is unconditional, not that it is always false.**

**Proposed correction.** State the cost as linear in the key count, and state the
block-separability condition under which it collapses. If the `k`-sweep cost is unacceptable,
the design question — whether the oracle should accept a weight map — needs asking, and
`weight-policy` is where it was foreclosed without being asked.

---

### S10 — The seam contracts bitwise determinism in one direction only, and the undertaking side is the one doing the floating-point work

**Severity: medium. Confidence: high.**

`learnable-structure-contract.md:141-146`:

> Inference-mode emission is deterministic, bitwise, for fixed inputs and fixed identity, so
> content-addressed caching holds.

Corpus-wide, `grep -rn "determinis\|bitwise\|reproducib" journals/` returns five hits: this
one, an anchor line for it, a "deterministic text renderer" for the cert
(`cert-obligations.md:42`), and `residual-definitions.md:295` on freezing a schedule. **No page
contracts the oracle's determinism.**

Several things depend on it: the attribution pair `(oracle kernel hash × operator hash)`
(`learnable-structure-contract.md:154-159`); the reference cache's content-addressed key over
`(observable, value, sigma, provenance, coverage-mask)` (`cert-obligations.md:212`); and
`product.md`'s claim that "attribution, caching, and 'which oracle produced this result?' are
filesystem-level facts". Meanwhile the oracle's numerics include a fixed-point iteration capped
at five iterations, SVD truncation, Brillouin-zone integration and `RAD(τ)` sampling — none of
which is bitwise-reproducible across thread counts or BLAS versions without an explicit
undertaking.

The operator is held to a standard the oracle is not held to, on a seam where the oracle does
the numerically heavy half.

**What would refute this.** A determinism undertaking on an oracle page. There is none.

---

### S11 — Key-set drift across recompiles is unowned

**Severity: medium. Confidence: medium-high.**

`residual-definitions.md:226-229`: "The operator holds `Map<ResidualKey, Weight>` […] and those
weights persist across compose-time recompiles."

`product.md` ("Refusal is absence"): "A check the oracle cannot stand behind for this instance
— inapplicable, outside the certified envelope, or refused by certification — is not in the
compiled kernel, so its key is simply not in any map."

Put together: a recompile can silently remove keys the operator still holds weights for. The
loss then loses a term and nothing signals it. The instrument to detect this exists — the
static slot schema, which `product.md` says lets "a consumer enumerate its contents with no
other resource" — but no page obliges anyone to use it.
`learnable-structure-contract` is by its own statement "the complete list of demands"
(`:48-51`) and contains no reconciliation requirement; `boundary.md`, where a driver
obligation would live, is a declared stub.

**What would refute this.** A reconciliation obligation on any of the three pages. I read all
three in full.

---

### S12 — "Discretisation invariance" is stated as a property neural operators have; the operator-learning literature says otherwise, and `training-stages` omits it from the failure list that claims to be complete

**Severity: medium. Confidence: medium-high.**

`learnable-structure-contract.md:60`, the second row of the five-property "why an operator"
table:

> **Discretisation invariance** | supercell size and reciprocal-space mesh density vary across
> the problem. A mesh-bound model is retrained per mesh; **one set of weights carries across
> meshes**

Bartolucci, de Bézenac, Raonić, Molinaro, Mishra & Alaifari, *Representation Equivalent Neural
Operators: a Framework for Alias-free Operator Learning* (arXiv:2305.19913; NeurIPS 2023)
introduces "operator aliasing, which measures inconsistency between neural operators and their
discrete representations", and reports that "aliasing introduces errors when handling
different discretisations and grids and loss of crucial continuous structures" — i.e. that
standard neural operators, Fourier neural operators included, are *not* discretisation-invariant
as implemented. (Verified from the paper's abstract; I could not run further searches, see §3.)

The *contract* built on this row is fine — `#evaluate-at-points` contracts point-evaluation,
which branch-trunk operators satisfy exactly. The defect is in the justification and, more
consequentially, in the omission:

`training-stages.md:120-138` lists three shortfalls of the trained operator and characterises
the list as complete and as the page's honest half — "all three failures are **silent**". Mesh
sensitivity from aliasing is a fourth failure of exactly that character: a plausible number
comes back on a mesh the model was not trained at, with nothing marking it. It bears directly
on the seam's self-described "single most load-bearing requirement", which is evaluation at
points off the training grid.

**What would refute this.** A statement elsewhere that the discretisation-invariance claim is
approximate, or a demonstration that the specific architecture family chosen is alias-free
(Raonić et al.'s convolutional neural operators are a candidate). Architecture is explicitly
unconstrained by the seam (`learnable-structure-contract.md:68-72`), so no such demonstration
is available.

---

### S13 — A curriculum phase turns on a consistency pair one leg of which is dormant and barred from the gradient

**Severity: medium. Confidence: medium-high.** *Partly cross-subject — registry and laws.*

`residual-loss-design.md:414-417` states that the `on-demand` tier is "**never in the training
gradient** — it runs as a periodic validation hook". `agent-contract.md:240-241` gives the code
mapping: `cost-tier {T3: minutes}` and `cadence-tier {T3: on-demand}`.

`residual-definitions.md:173-175` binds registry rows 121
(`kappa-4phonon-high-t-correction`) and 122 (`iterative-lbte-kappa`) to row 25 as a
**consistency pair** under `Algebraic/MethodEquivalence`, which the curriculum turns on at
`[0.60, 0.90)`. Row 122 is `T3` — hence `on-demand`, hence never in the training gradient —
**and** dormant, by `residual-machinery.md:209-219`: "In V1 it returns an anchored constant:
there is no fixed point".

So one leg of a two-leg consistency pair cannot fire in V1 and could not enter the gradient if
it did. The failure presents as a residual that is permanently zero, which is indistinguishable
from a satisfied law. The 121↔25 leg is `T1`/`D1` and is fine, which is what makes this quiet
rather than obvious: the category does light up, at half strength, with nothing recording that.

**Two near-findings in this area that did not survive.** I flagged row 87
(`reference-phase-energy-cache`, `D0`/`read` yet `T3`/minutes) as an inconsistent tag pair;
`named-formulas.md#cost-tiers` anticipates it exactly — "costs `minutes` to evaluate and is
`read` for differentiability […] Cost and differentiability are independent axes" — and is
right. Killed. I also expected `Positivity`'s `ω² ≥ 0`, which the curriculum turns on in
*Warmup*, to depend on the `T3` row 13 `SCPH-self-consistent-phonons`; it does not — row 9
`phonon-dispersion` is `T1`/`D2` and produces `ω_λ(q)`, with SCPH a higher-fidelity
renormalisation on top. Killed.

---

### S15 — The oracle computes a per-key uncertainty for every residual, hands it over, and tells the consumer to use it; the loss design has no channel for it

**Severity: medium-high. Confidence: high.**

The oracle's side is fully built. `residual-definitions.md:341-363` composes a per-`ResidualKey`
error budget through `Quantity.combineTol`, summing the input standard deviation, model-form
error, compression truncation, dressing staleness and coefficient-provenance standard
deviation. `product.md` ("The static slot schema") exports it per key — "for each key: the
producing registry row, the axis coordinates, the closed-enum tags […] and **the error scale —
a standard deviation**" — and states the intended use explicitly:

> Consumers who want cross-slot comparability compute the standardised score `z = value / σ`
> **themselves** — that is a join against the schema, not a product output.

The operator's side never joins. `residual-loss-design.md#balancing` and `#defaults` set the
per-residual weights `λ_i(t)` entirely from GradNorm across the four source families and
neural-tangent-kernel-initialised fixed weights within the residual family. Neither `σ`, nor
`combineTol`, nor `characteristic-scale`, nor any normalisation by a declared scale appears
anywhere in the loss design.

This matters on the page's own terms. `residual-loss-design.md:155` states the failure mode:
"Fixed weights fail once term scales differ by more than two orders of magnitude." The residual
surface here spans a dimensionless `‖Tr γ̂ − N_e‖²`, a mesh-scale `‖∂_t field − RHS‖²` in SI
units, and thermal-conductivity residuals of order 10³ W/m·K. The per-key σ is precisely the
object that makes those commensurable, and it is the object the design does not use.

And the four-source table at `residual-loss-design.md:265` records the noise of physics
residuals as "**none, or known**". By the oracle's own construction it is never none — every
key carries a non-zero budget — and the "known" branch is known only to the oracle, because
nothing downstream reads it.

**What would refute this.** A rule forbidding the join. Two candidates, and neither forbids it:
`residual-definitions.md:241` says *facets* are "never the basis for a per-residual loss
weight", which is about `(category, bundle, dressing)` and not about σ; and
`residual-machinery.md:80-82` says `characteristic-scale` is "an error-model input, **never a
fitted weight**" — a declared σ used as `1/σ` normalisation is not a *fitted* weight, so the
rule permits exactly the use that is missing. The channel is open and unused.

**Proposed correction.** Either normalise residual terms by the exported per-key σ before
balancing, and say so; or state why the design deliberately declines to, given that the oracle
computes the quantity specifically to be consumed this way.

---

### S18 — The operator side of the seam is batched, the oracle side has no batch concept, and its unit of compilation is finer than a batch element

**Severity: high. Confidence: high.**

The operator is contracted to be batched. `learnable-structure-contract.md:148-151`:

> ## Batch axis
> Emission and cotangent intake carry a leading batch dimension. Batch elements are
> independent: no cross-batch coupling is observable at the seam.

The oracle has no batch concept anywhere. `Validate(state : UnifiedState, …)` takes one state
(`pino-bridge.md:51`); the compiled kernel's inputs are "**A dense state vector** […] and an
environment" (`compose-time-pipeline.md`, runtime kernel application); the stage table at
`compose-time-pipeline.md:366` runs kernel application "**per state sample** […]
microseconds–milliseconds, millions of times"; the command line is "oracle-file plus **a state
file**" (`product.md`, "The command line"). A corpus-wide sweep for `batch` returns twelve
hits, of which the only ones on the oracle side are the *name* of a sampler enum value and a
passing mention of the operator's mask.

And the oracle's unit of compilation is finer than one batch element.
`product.md` ("Three rules about files"): "**One file per crystal identity.** A kernel is
specialised to one periodicity structure, site decoration and environment."

Now the third mask forces the question. `applicability-classifiers.md` (predicate contract):

> The physics-informed loss masks out non-applicable properties **per sample**, so the model is
> neither falsely supervised — predicting a band gap for a metal — nor penalized for a quantity
> that is undefined rather than zero. […] One interface accepts diamond, gallium nitride,
> aluminium nitride, cubic boron nitride and refractory metals.

A band gap and a metal in the same batch means the batch spans crystal identities. This is a
dichotomy and both branches are defects:

**If a batch spans identities** — which the passage above asserts — then one gradient step
requires up to `B` invocations of `B` distinct compiled oracle-files, and no page says so. The
per-step cost of the informed epoch is then `B ×` a kernel evaluation plus `B ×` the
per-key reverse sweeps of S9, against a seam whose cost discussion
(`residual-loss-design.md#cadence`) is entirely about *which formulas* are evaluated and never
about how many kernels. `learnable-structure-contract.md:154-159` also breaks: a residual map
is to be "permanently attributable to the pair *(oracle kernel hash × operator hash)*", and a
batch has no single oracle kernel hash.

**If a batch does not span identities**, then within one oracle-file the applicability
predicate is constant across the batch — because the inapplicable checks were already pruned at
compose time and their keys are simply absent (`product.md`, "Refusal is absence"). A constant
is not a mask. Sense (3) of the three-way split then collapses into the compile-time prune, and
`residual-loss-design.md:314-318`'s "all three multiply into the same loss term" is a product
with two live factors and one identity.

So either the seam has an undeclared `B`-fold cost and a broken attribution rule, or one of the
three carefully separated masks is not an independent object. The corpus does not say which,
and `boundary.md:49` — which assigns "**Batching policy.** Which samples, in what batches, in
what order" to the loops library — is a declared stub, so the question has a named recipient
and no answer.

**What would refute this.** A batched entry point on the oracle side, or a statement that one
oracle-file covers several crystal identities. Neither exists: `product.md` is explicit that
"'The oracle' as a general object is the *compiler*; each file is the oracle *for one
instance*", and that searches over discrete identity space "produce many files […] the mental
model is 'a directory of kernels'".

**Proposed correction.** State on `learnable-structure-contract` or `boundary` how a batched
emission meets a per-identity, unbatched oracle — and, if a batch spans identities, say what
the attribution rule becomes.

---

### S17 — The worked example for the strongest relaxation technique is wrong, and wrong on the MVP material

**Severity: medium-high. Confidence: high.**

`residual-loss-design.md:204-209`, the third of three techniques for moving a `none`-tier
quantity into `relaxed`:

> - **Surrogate continuous residual** — replace the discrete predicate with a signed continuous
>   quantity **whose sign carries the discrete fact**. "Is the band gap direct?" becomes the
>   indirect-minus-direct gap difference.
>
> The third is the strongest where it applies, because it removes the discreteness rather than
> smoothing it: the discrete fact becomes **the sign of a differentiable scalar**, and the
> residual stays exact.

The general technique is sound. The example does not instantiate it, because the quantity it
names is one-signed.

The indirect gap minimises `E_c(k_c) − E_v(k_v)` over **all** pairs `(k_v, k_c)`; the direct gap
minimises the same expression over the **diagonal** pairs `k_v = k_c`. The diagonal is a subset
of all pairs, so

```
E_g^indirect  ≤  E_g^direct        for every band structure, always
```

with equality exactly when the fundamental gap is direct. So `indirect − direct` is `≤ 0`
everywhere. Its **sign** carries no information; its **vanishing** carries the fact. An
implementer who follows the instruction as written and builds
`sign(E_g^indirect − E_g^direct)` gets a classifier that answers "indirect" for every material
in the registry, including direct-gap ones, where the quantity is exactly zero and `sign(0)` is
a convention.

The correct relaxation is the same quantity read as a one-sided residual — `directness` is
`E_g^direct − E_g^indirect` vanishing, scored as a hinge or a magnitude — which is
differentiable, exact, and available: registry rows 1 `bandgap-direct` and 2 `bandgap-indirect`
are both `T0`/`D1`.

**Why it matters beyond the wording.** Diamond is the MVP material and is an indirect-gap
semiconductor; B1 electronic-structure is an MVP capability; and `traps.md:269-273` already
warns that "Diamond's direct-gap zero-point renormalization is a different valley from the
indirect […] the load-bearing indirect gap". This is the one example the page gives of the
technique it calls strongest, on the material the build is first for.

**What would refute this.** A definition of the direct gap on which it can fall below the
indirect gap. There is none — the minimisation domains are nested by construction. Or a reading
on which "signed" means "one-signed"; but the page's own gloss, "the discrete fact becomes the
sign of a differentiable scalar", forecloses it.

**Proposed correction.** Replace "whose sign carries the discrete fact" with "whose vanishing
carries the discrete fact" and keep the example, or keep the wording and replace the example
with a genuinely two-sided one — hull distance against a metastability band
(`residual-definitions.md:186-191`) is one already in the corpus.

---

### S16 — The evolver hand-off exports the representation-health problem and withholds the instrument the oracle already built for it

**Severity: medium-high. Confidence: high.**

`pino-bridge.md:162-170` sets the standard the page is to be judged by:

> a consumer that integrates a tier inherits the representation-health problem along with the
> tangent map. The manifest therefore declares the encoding each block was compiled against,
> and the conditions under which that encoding stops being a fair approximation: the
> `CompressionPlan` slot, its rank, and its truncation target.
> **Exporting the problem is legitimate; exporting it silently is not.**

A rank and a truncation target are properties of the *compiled plan*. The condition under which
the approximation stops being fair is a property of the *trajectory* — it is whether the
discarded spectrum has grown as the state moved. The manifest declares the first and calls it
the second.

The oracle owns the correct instrument and does not hand it over.
`residual-machinery.md:150-166` is normative: "A generator whose lowering introduces
representation error must register a paired **fidelity generator** — a cert-only subtype
carrying a computable *a-posteriori* estimator of that error", and its first row is exactly this
case — a non-`Dense` `CompressionPlan`, estimator "the discarded spectrum, `‖A − A_k‖₂ =
σ_{k+1}`", cost "already computed by the truncation". `residual-machinery.md:168-172` then
draws precisely the distinction the manifest gets wrong:

> **An a-priori target is not a substitute for an a-posteriori estimate.** A compression plan
> already carries an error *target* and picks its rank to meet it. The target is what the plan
> intended; the estimate is what it achieved; only the second is evidence.

The manifest exports the plan's rank and its **truncation target** — the a-priori quantity that
same page says is not evidence — and not the a-posteriori estimate.

The routing confirms it. The fidelity generator's output "flows into `Quantity.combineTol` […]
and into the cert as evidence" (`residual-machinery.md:174-176`); cert evidence is a return of
`Validate` (`pino-bridge.md:58`). `dynamics(tier)` returns a manifest whose only cert-facing
field is "sibling fingerprint **and the certificate reference**" (`pino-bridge.md:152`) — a
pointer to a compile-time attestation, which cannot carry a per-step value. So a consumer that
scores gets the running estimate and a consumer that integrates — the only one who needs it —
gets a hash.

**Four further undeclared misses**, from building the consumer's requirement list before
re-reading the field list:

| a consumer needs | manifest field |
|---|---|
| a stiffness indicator or spectral-radius bound, to choose explicit against implicit | none — "per-step cost" is declared, per-step *stability limit* is not. The three tiers span femtoseconds to seconds (`multiscale-state#three-tiers`), so this is not a marginal omission |
| a local-error estimator for step-size control | none |
| whether the tangent map is autonomous — its signature `(state_tier, env, adiabatic-params) → tangent_tier` carries no time argument, while `env` is a per-call argument that varies within its stamped box (`product.md`, "Environment-box validity") | none states whether `env` and `adiabatic-params` may vary along a trajectory or must be frozen |
| the time unit of the emitted tangent | none, and `unified-state.md:76` declares per-slot units unspecified — so the derivative's units are undetermined at the point of use |
| consistent initial conditions for the algebraic subsystem | the `index-≤1 witness` (`pino-bridge.md:146`) bounds the index, which is what makes a solve tractable; index-1 systems still require consistent initialisation, and nothing says who computes it |

**Separating this from the declared gap.** `pino-bridge.md:34-37` honestly declares that "the
manifest record, the refusal enum, and the scorer-versus-evolver exactness obligation" are
unwritten. That covers the *record's schema*. It does not cover the claim at `:162-170`, which
is stated as settled and is wrong about what it has declared; nor the five misses above, which
are absences inside a list the page presents as complete.

**What would refute this.** A statement that the fidelity generator's per-evaluation output is
reachable from a `dynamics(tier)` consumer. `residual-machinery.md:174-177` routes it to
`combineTol` and the cert and nowhere else, and adds that it "**never** enters the training
loss" — an exclusion aimed at the operator, which leaves the integrator unaddressed rather than
served.

---

### S21 — The evolver obligation vocabulary does not match the named integrator's theorems term for term; one of its three tokens has no referent at all

**Severity: high. Confidence: high.** *Primary-source verification performed by the principal's
agent, which read Ceruti, Kusch & Lubich (arXiv:2104.05247v1) end to end, the
Einkemmer–Kormann–Kusch–McClarren–Qiu review, and Ceruti's dissertation. I am reporting the
result, not the reading; the theorem numbers below are that agent's and are checkable against
the preprint.*

`pino-bridge.md:172-195` makes a term-for-term claim and stakes the hand-off on it:

> `conserve | bound | monotone` is not an arbitrary vocabulary. It is the vocabulary the robust
> dynamical-low-rank literature states its guarantees in, so a consumer can match an integrator
> to the obligations **term for term**. […] Up to a declared truncation tolerance it preserves:
> the norm, where the equation does — `conserve`, for instance `Tr γ̂`; the energy, for
> Hamiltonian systems — `conserve`, the `L` block; monotone decrease of the functional in
> gradient flows — `monotone`, the `M` block.

**What checks out, and it is the hard part.** All four citations are correct in every stated
field — authors, title, journal, volume, page range, year. And the page names the *right*
integrator: every result below rests on a lemma the paper twice says does **not** hold for the
fixed-rank sibling. Had `pino-bridge` named the unconventional fixed-rank integrator instead,
all three claims would be false rather than qualified. This is recorded because a clean verdict
is earned and shown, and this one is.

**(a) `Tr γ̂` is not the norm the theorem conserves.** Theorem 3.1 conserves the **Frobenius**
norm `‖γ̂‖_F = (Tr γ̂²)^½` — the purity. `Tr γ̂` is the electron count. These are independent
functionals: truncation controls the ℓ² tail, while trace loss is the ℓ¹ tail and is bounded
only by `√(2r − r₁)·ϑ`. Verified numerically by that agent: at `ϑ = 1e-3` the Frobenius norm
moved by `1e-7` while the trace lost `1.16e-3` — **larger than the truncation tolerance
itself**.

This lands directly on the oracle's own residual set. `residual-definitions.md:115-118` makes
`‖Tr γ̂ − N_e‖²` a `Conservation` residual — "a candidate state must carry the right electron
count" — so the example `pino-bridge` chose to illustrate `conserve` is precisely the quantity
the cited theorem does not protect.

**(b) Energy conservation is real, and is canonical-only.** Theorem 3.4 gives it — no later
structure-preserving variant is needed, which is worth stating because that was my prior
expectation and it was wrong. But it assumes canonical Hamiltonian form `Q̇ = ∇_P H`, and the
paper states outright that one should not apply dynamical low-rank approximation directly to
those equations. The `L` block is **mixed**: `(R, P)` and `(h, Π_h)` are canonical; Liouville–von
Neumann on γ̂ and Maxwell on `A` are not. The Schrödinger route (Theorem 3.3) fails twice for
γ̂ — `Ĥ_KS[γ̂]` is nonlinear in γ̂, and the conserved quadratic form is identically zero by
cyclicity for the von Neumann map. The review, co-authored by one of the named authors, says
preservation in the non-canonical case is "presently not clear if this is possible."

**(c) "Monotone decrease" is not monotone.** Theorem 3.2 reads
`f(Y₁) ≤ f(Y₀) − α²h + βϑ`. So `f` may **increase** wherever `βϑ > α²h` — near a stationary
point, which is exactly where a gradient flow converges and exactly where a residual is being
driven. Two further conditions go undeclared: the theorem assumes a **Euclidean** gradient flow
while the `M` block is a *metric* gradient flow, which no paper in this family covers; and the
guarantee requires the inner S-step to be solved exactly, by implicit Euler, or by a
discrete-gradient method — an explicit Runge–Kutta S-step voids it. A consumer told to match
"term for term" is given no way to know that last condition exists.

**(d) `bound` has no referent — this is the sharpest of the four.** The token occurs twice
corpus-wide: the obligation-map declaration at `pino-bridge.md:149` and the sentence claiming
the vocabulary is the literature's at `:174-176`. The CKL preprint has **zero** occurrences of
"positiv". The review calls positivity preservation for low-rank methods "challenging" and
"difficult" and treats it as unresolved, because the orthogonal basis functions must take
negative values; where it is achieved at all it is a bolt-on outside this family.

So `pino-bridge.md:174-176` — "It is the vocabulary the robust dynamical-low-rank literature
states its guarantees in" — is **false for one of its three tokens**. And the bite is maximal
rather than incidental: `residual-definitions.md:137-139` rests the oracle's soundness *as a
verifier of the state itself* on exactly the admissibility bounds `bound` would have to carry —
"A candidate γ̂ outside these bounds can zero every equation-of-motion residual while being
unphysical."

**Proposed correction.** Replace `Tr γ̂` with the Frobenius norm as the `conserve` example and
say what happens to the trace; scope the energy claim to the canonical sub-blocks and say the
γ̂ and `A` blocks are uncovered; restate `monotone` with its `βϑ` slack, its Euclidean
assumption and its S-step condition; and either find a family member that preserves positivity
or withdraw `bound` and say plainly that admissibility is not preserved under integration.

---

### S22 — Every one of those theorems assumes the whole right-hand side has its structure, and the GENERIC right-hand side has neither

**Severity: high. Confidence: high.** *Same verification source as S21.*

Each theorem in S21 is stated for a system whose **entire** right-hand side is of one kind: a
canonical Hamiltonian system, or a gradient flow. The equation the oracle actually hands over
is `dx/dt = L δE/δx + M δS/δx` (`residual-definitions.md:87-88`, citing
`generic-dynamics#generic-form`), which is neither — it is a sum of one of each.

`pino-bridge.md:187-188` asserts the bridge: "The blocks are [generic-dynamics#operators], so
the three guarantees map term-for-term onto the structure the residuals are written against."
The mapping holds **per block, per hypothesis class, and never simultaneously**. A consumer who
integrates the coupled system — which is the only thing `dynamics(tier)` is for — is outside
every theorem's hypotheses even where each block individually satisfies one.

This is not the declared open question at `pino-bridge.md:34-37`, which covers the manifest
record, the refusal enum and the scorer-versus-evolver exactness obligation. The composition
gap is presented as settled, in the sentence that does the load-bearing work.

**What would refute this.** A structure-preserving low-rank result for GENERIC or
metriplectic systems as a whole. The review's statement that non-canonical preservation is
"presently not clear if this is possible" points the other way.

---

### S19 — The adjoint cost claim drops the qualification the compilation page was careful to add, and then generalises it across two tiers

**Severity: low-medium. Confidence: high.** *Re-instantiation of inherited `oracle-compilation` C5 on a seam page.*

`compose-time-pipeline.md:271-278` is careful:

> Gradient cost becomes one extra linear *system*, independent of the forward iteration count —
> **not constant work**, since that system is itself solved iteratively, but independent of how
> long the forward solve ran (Blondel et al., *Efficient and Modular Implicit Differentiation*,
> NeurIPS 35, 2022, 5230–5242 […])

`residual-loss-design.md:176-179` drops it: "the implicit-function form then costs **one linear
solve** independent of iteration count". That much is defensible on its own. What is not is the
conclusion drawn at `:188-190`:

> an adjoint-tier residual costs roughly **one extra forward-equivalent** per gradient, which is
> what keeps it off the per-step path.

"One adjoint solve ≈ one forward solve" is the standard rule of thumb for the discrete adjoint
on a *non*-fixed-point problem (Giles & Pierce 2000), and the paragraph applies it to both
tiers immediately after distinguishing them. For the `fixpoint-adjoint` tier the adjoint linear
system is solved iteratively with its own iteration count and its own conditioning — which is
precisely why `residual-machinery.md:186-190` requires a *second* gate on the reciprocal
condition number of the fixed-point Jacobian. A badly conditioned system is exactly the case
where "one forward-equivalent" is wrong, and the corpus already knows that case exists.

The inherited register recorded this as C5 between `4.2` and `4.4`; `4.4` is gone and the
imprecision has reappeared on `residual-loss-design`.

**Proposed correction.** Carry `compose-time-pipeline`'s qualification, and scope the
forward-equivalent estimate to the `adjoint` tier.

---

### S14 — `Validate`'s fourth return value is stated two ways; the registered contradiction is still live

**Severity: low-medium. Confidence: high.** *Triage of inherited `oracle-laws-seams` row 4.*

`pino-bridge.md:58` — `cert : CertEvidence`. `compose-time-pipeline.md:338` — `CertEvidence :
CertEvidence`. `product.md:182` — the call "returns four things: […] and **the content hash of
the producing kernel**."

Two of three say cert evidence; `product` says the kernel hash. The pre-restructure form of
this contradiction is registered and unresolved; it survives with `product` as the outlier.
It matters mildly because `learnable-structure-contract.md:154-159` requires residual maps to
be attributable to `(oracle kernel hash × operator hash)` and, under the `pino-bridge` reading,
the call returns neither half of that pair — the oracle side has to be obtained from the
oracle-file's hash instead.

`CertEvidence` is also indexed by `glossary.md:85` to
`[compose-time-pipeline#runtime-kernel-application]`, which uses the name in a signature and
never says what it contains.

---

## 2 · Findings that did not survive

*This section is completed once the undergraduate returns are in; the entries below are ones I
killed myself.*

- **Row 87 `reference-phase-energy-cache`, `D0` with `T3`.** Looked like an inconsistent tag
  pair. `named-formulas.md#cost-tiers` addresses it directly and correctly. Killed. (Recorded
  under S13.)
- **"Attributable to the pair `(oracle kernel hash × operator hash)`" is incomplete because the
  input state is not in the pair.** Read as "the producing pair can be identified", which is
  the natural reading, the sentence is true. Killed.
- **The two-loop symmetry does no work.** `learnable-structure-contract#loop-agnostic` grounds
  loop-agnosticism in a symmetry between the training and design loops, and the design loop
  optimises the candidate directly against `cograds` (`product#design-variable-boundary`) and
  need never exercise the seam's vector–Jacobian obligation at all. So the symmetry is thinner
  than claimed — but the *conclusion* (the contract names no loop) is independently true and
  the requirements list is unaffected. Rhetorical weakness, not a defect. Killed.
- **The gauge-convention pointer.** Inherited `oracle-state` row 4 records that the seam
  requirement points at `unified-state` for gauge conventions which `unified-state` defers to
  `generic-dynamics`. Post-restructure, `unified-state.md:78-84` carries the gauge conventions
  and explicitly names the remainder of that sentence as its declared wire-schema gap.
  **Resolved by the restructure.** Killed.
- **The `T0`–`T3` cost/cadence collision** (inherited `appendix-c` C-2). `agent-contract.md:230-256`
  now lists both mappings under `retired-vocabularies` and states plainly that they are "two
  vocabularies, not one"; `residual-loss-design.md:222-224` and `named-formulas.md#cost-tiers`
  both restate the separation. **Resolved by the restructure.** Killed.
- **The operator's job — completion versus time evolution** (inherited `program` C1). Now a
  declared open question at `purpose-and-scope.md:44-47`, with both readings stated and three
  invariants named that hold under either. Honest, therefore not a finding. One residue:
  `learnable-structure-contract.md:63` asserts the *completion* reading as settled ("what is
  learned is the map from topology and partial properties to the rest of the state"). Minor;
  reported to the principal rather than raised here.
- **The Grover argument lists a mechanism as a precondition.** `training-stages.md:70-73`:
  "Grover needs superposition over the search space, a *marking* oracle, and amplitude
  amplification […] none of the three preconditions holds." Amplitude amplification is what
  Grover *does* given the first two, not a precondition on the problem; and the stated reason —
  "Training has gradients and does local descent" — supports the final clause ("no unstructured
  search to accelerate") rather than the three. The conclusion is correct and the paragraph is
  doing rhetorical work the page openly admits to ("the question deserves an answer because it
  is the first one the word *oracle* provokes"). Not a defect. Killed.
- **The counterexample-guided-inductive-synthesis analogy discards the property that makes
  CEGIS interesting.** `training-stages.md:63-67` offers CEGIS "with a gradient in place of the
  counterexample". A CEGIS counterexample eliminates at least the current candidate, which is
  what gives the loop its termination argument; a gradient eliminates nothing and gives local
  descent. But the page offers the analogy explicitly as a *naming* claim — "That names what the
  oracle contributes better than 'physics-informed loss' does" — not as a convergence claim, and
  `residual-loss-design.md:398-400` states plainly that "**Convergence here is empirical.**" No
  contradiction. Killed.
- **`channel` is overloaded.** Used for operator output channels
  (`learnable-structure-contract.md:108`), environment conditioning channels (`:131`), compile
  flags (`product.md:254`), coupling channels, and scattering channels. Real, and the same
  defect class as S1 — but `coverage-mask` was retired for multiplying three masks into one
  loss, whereas the `channel` senses do not compose into a shared quantity, so nothing fails
  silently. Reported as a readability item, not a finding.

---

## 3 · Shaped gaps

### G1 — Web search was exhausted mid-audit

**What it would settle.** Whether the three preservation guarantees `pino-bridge.md:178-186`
attributes to the rank-adaptive basis-update-and-Galerkin integrator (norm, energy for
Hamiltonian systems, monotone functional decrease for gradient flows) are proved for *that*
integrator in Ceruti, Kusch & Lubich, *BIT* 62 (2022), or only for a different member of the
dynamical-low-rank family; and whether any published guarantee in that family is stated as a
*bound*, which is the one token of the three-token obligation vocabulary
(`conserve | bound | monotone`, `pino-bridge.md:149`) that the page's own list of guarantees
maps nothing to.

**The conclusion without it.** The session's 200-call web-search budget was consumed before I
could verify these. My dedicated undergraduate was launched before the budget was exhausted
and may have completed the verification; if its return is present in §1 this gap closes. If
not: on my own knowledge, the *unconventional* and *rank-adaptive* BUG integrators are proved
robust to small singular values, and energy conservation is the property I would most expect
to belong to a later structure-preserving variant rather than to the 2022 rank-adaptive paper —
but I will not assert that without the text.

**The branches.** If the three guarantees are all proved for the named integrator, S-BUG
below does not arise and only the unmapped `bound` token stands. If energy conservation
belongs to a different integrator, then `pino-bridge` names a family that cannot honour the
`conserve`/`L`-block obligation it exports, and a consumer matching "term for term" as
instructed would choose wrongly. If no guarantee in the family is stated as a bound, the
obligation vocabulary has a third token with no referent and the "term for term" claim is
false as written.

**What depends on it.** Nothing in S1–S14. This gap is isolated to the evolver hand-off.

---

## 4 · Acquisition requests

To be completed from undergraduate returns. Standing request regardless: raise
`CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`, or run the literature checks in a fresh session —
the constraint is a session budget, not a paywall, and no paper has yet been found to be
unreachable.

---

## 5 · Calibration

Method: six defects planted in a scratch copy of the corpus at
`.../scratchpad/calib`, one or two per defect class, then a fresh agent given the same subject
and the same four-class instruction, with no knowledge of the plants.

| # | class | plant |
|---|---|---|
| P1 | contradiction, cross-page | `learnable-structure-contract` made to say the oracle returns a single **pre-summed** cotangent, against `pino-bridge`'s per-key `cograds` and `residual-definitions`'s "never preaggregates" |
| P2 | contradiction, within-page | `residual-loss-design` cadence table: `seconds` → `per-batch`, against the prose rule and the tier mapping |
| P3 | misinterpretable | `pino-bridge` flat-index changed from "lexicographic over axis **values**" to "over axis **labels**" — a construction a careful reader implements correctly and gets a different index |
| P4 | missing information | the adjoint gate's `τ_adj` default `1e-4` and its `N ≈ 64` sample count deleted, leaving a threshold named and unvalued |
| P5 | false claim, mathematics | the dynamical-low-rank robustness theorem re-attributed from "independent of small singular values" to "independent of the stiffness of the underlying equation" |
| P6 | false claim, numeric | one curriculum endpoint moved, `0.60` → `0.65`, so the table disagrees with the knob list on the same page |

**Result: pending.** The calibration agent is running; this section reports as found, including
a partial result, per the brief.

---

## 6 · Evidence transcript

Nothing in this subject is being certified clean, so this section records the sweeps that
produced the negatives above rather than a clearance.

- **Phase-name sweep.** `grep -rniE "\b(warm-?up|refine|polish|calibrate|cooldown)\b"` over
  `journals/`, `README.md`, `data/`, `tools/` → 20 hits. All accounted for in S7. Exactly one
  use outside the two defining tables and their own prose (`multiscale-state.md:286`), and it
  is clean because it carries its interval.
- **Retired-token sweep.** `grep -rn "coverage-mask\|coverage_mask\|CoverageMask"` over
  `journals/`, `data/`, `tools/`, `generated/` → 7 hits, all enumerated in S1.
- **Seam type-name sweep.** Every CamelCase identifier inside fenced code blocks on the six
  seam pages (35 distinct), checked against the glossary's "Where a name is specified" table
  and `generated/corpus.json`. 11 indexed, 24 not; of the 24, 11 are inline-defined enum
  constructors and 4 are cross-referenced in adjacent prose. The residue is S4.
- **Ordering-convention sweep.** `grep -rn
  "lexicograph\|canonical order\|index order\|ordering\|sorted\|total order"` over `journals/`
  → 19 hits. Two bear on the flat index and they conflict (S2); one is the declared
  wire-schema gap at `unified-state.md:76`; the rest are unrelated.
- **Determinism sweep.** `grep -rn "determinis\|bitwise\|reproducib"` over `journals/` → 5
  hits, all enumerated in S10.
- **Cost/cadence sweep.** All five `T3` rows read from `data/registry-manifest.csv` and traced
  to the residual categories that consume them (S13). All six `D4` and six `DN` rows read and
  checked against `named-formulas`'s definitions of `relaxed` and `none` — the topology-atlas
  `DN` rows (96–100, 102) are integer-valued invariants and correctly tagged; the `D4` rows
  each carry a named relaxation in the `Source` cell and are correctly tagged.
- **Checker baseline.** Run before and after; `structure OK · 45 pages, 273 owned topics, 51
  open questions` and `probes: 34 · caught 34 · missed 0` both times. Nothing I did changed
  either result, and nothing I found is visible to either.

---

## 7 · Log-worthy advancements

Reported, not written — `log/timeline.md` has a single writer.

1. The `coverage-mask` split declared complete by the restructure is **not** complete: the
   token survives in the persisted cache schema and in the content address, the glossary
   registers the retired type as live, and a fourth sense exists that the retirement never
   enumerated (S1).
2. The axis-coverage flat index is an identity-bearing construction with no stated ordering,
   in a corpus that canonicalises every other identity-bearing serialisation (S2).
3. `Import` cannot key its leaf under the `ResidualKey` schema the seam exports (S3).
4. `Polish` denotes two different 30% windows, and the declared open question that covers the
   phase-name disagreement mis-describes it in a way that makes following the instruction
   harmful (S7).
5. Build gate 3 asserts a three-phase training run that no schedule defines, and cites the
   oracle's page for a schedule it says the operator owns (S8).

---

## 8 · Triage of the inherited contradiction register

Six were registered on the seam pages. Disposition:

| registered | status |
|---|---|
| `oracle-laws-seams` — curriculum fraction denominator | **Persists, declared.** `residual-definitions.md:304-313` now states the gap honestly and traces its downstream consequence. Not a finding; the *phase-name* half of it is S7. |
| `oracle-laws-seams` — curriculum phase names and count | **Persists, and the declaration is wrong.** S7. |
| `oracle-laws-seams` — `Validate` output types | **Persists.** S14. |
| `oracle-laws-seams` — T2 residual cadence | **Resolved.** The competing per-epoch/30%-gate policies are gone; `residual-loss-design.md:226-237` now gives one cost→cadence default with an explicit override rule. |
| `oracle-laws-seams` — where the seam contract is canonical (circular deference) | **Resolved.** `unified-state.md:74-84` now carries the gauge conventions and declares the remainder as its own gap rather than deferring in a circle. |
| `oracle-state` — where gauge conventions are recorded | **Resolved.** Same repair. |

Two further registered items touching this subject: `appendix-c` C-2 (cost vs cadence tiers)
**resolved** at `agent-contract.md:230-256`; `program` C1 (what the operator does) **converted
into a declared open question** at `purpose-and-scope.md:44-47`.
