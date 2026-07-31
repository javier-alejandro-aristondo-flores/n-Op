# Adjacent self-contradictions — the 27-page tail

**Quoting convention.** Every quote is byte-exact except that where the source hard-wraps
a sentence across lines, the newline is rendered as a single space. Nothing is elided,
paraphrased, or emphasised beyond what the source itself marks. All 63 quoted strings in
this report were mechanically confirmed present in the corpus under whitespace
normalisation before the report was written.

---

## 1. Calibration on practice/conventions.md

**Four found: one STRONG, two MEDIUM, one WEAK.** Stated as found, not rounded.

### C1 — `practice/conventions.md`, "Data files and generated files" · STRONG

> **first half** (line ~118): "Three kinds of file sit outside the journals, and each relates to prose differently."

> **second half** (line ~134): "**Neither kind has a page id**, so both are named by path rather than cited."

**Why they cannot both be true:** The section announces three kinds and then enumerates
exactly two — **Data files are sources.** and **Generated files are outputs.** — before
closing with "Neither kind" and "both", which are two-item words. The section heading
("Data files and generated files") and the frontmatter anchor (`artifacts: "Data files and
generated files"`) also name two. No third kind appears anywhere on the page.

**Which is correct:** Two. The enumeration, the heading, the anchor and the closing
two-item words all agree; "Three kinds" is the outlier.

**What would refute this finding:** A third `**Bold.**` file-kind paragraph in the section
that I failed to see.

### C2 — `practice/conventions.md`, "What a result has to show" · MEDIUM

> **first half** (line ~88): "**Green means the structure is sound. It does not mean the physics is right.**"

> **second half** (line ~93): "**Green does not mean a check ran.**" … "A checker that finds nothing and a checker that is not looking produce identical output."

**Why they cannot both be true:** The first asserts green ⇒ the structure is sound. The
second asserts that a checker which never ran produces the same green, so green does not
by itself license any conclusion about the structure. Five lines apart, both bolded, both
framed as what green means.

**Which is correct:** The second. The first is shorthand for a scope contrast (structure
versus physics) and overstates its own guarantee.

**What would refute this finding:** Reading the first sentence as scoping rather than
entailment — which is available, hence MEDIUM rather than STRONG.

### C3 — `practice/conventions.md`, "Calibrate before certifying" · MEDIUM

> **first half** (line ~106): "plant a known set of defects in a throwaway copy and confirm every one is found"

> **second half** (line ~108): "a pass that finds four of six planted defects is a four-of-six gate, and rounding it up is the same failure the calibration exists to prevent"

**Why they cannot both be true:** The first makes calibration a pass/fail procedure whose
success condition is finding *every* planted defect. The second treats a four-of-six
result as a legitimate, reportable calibration outcome — a graded measurement, not a
failed one. Two lines apart, in the same paragraph.

**Which is correct:** The second. It is the more specific and more argued claim; "confirm
every one is found" should read "confirm which are found".

**What would refute this finding:** Reading "confirm every one is found" as "check each
one individually" rather than "verify that all are found".

### C4 — `practice/conventions.md`, "Style" against the frontmatter · WEAK

> **first half** (line ~47): "**One subject per page.** A page may own several topics when they are facets of one machine"

> **second half** (line ~31): "This page is deliberately small. Four things are left over, and none of them is structural:"

**Why they cannot both be true:** The rule permits multiple owned topics only as facets of
one machine — "That is cohesion, not drift." This page's frontmatter `owns:` four topics,
and the page describes them as leftovers, which is the stated opposite of cohesion.

**Which is correct:** Underdetermined from the passage. Either the rule needs a
leftovers exemption or the page is the exception it forbids.

**What would refute this finding:** Treating "what is left over after agent-contract" as
itself one machine.

---

## 2. Coverage

All 26 listed pages read fully, plus the coupling-structure tail. Nothing skipped.

| Page | Coverage |
|---|---|
| `n-op/purpose/library-landscape.md` | read fully (80 lines) |
| `n-op/build/build-sequence.md` | read fully (113) |
| `n-op/build/build-verification.md` | read fully (208) |
| `n-op/build/capability-slices.md` | read fully (138) |
| `n-op/build/forced-decisions.md` | read fully (99) |
| `n-op/build/mvp-system.md` | read fully (65) |
| `oracle/registry/canonical-vocabularies.md` | read fully (110) |
| `oracle/registry/computational-methods.md` | read fully (160) |
| `oracle/registry/formula-registry.md` | read fully (121) |
| `oracle/registry/observable-bundles.md` | read fully (124) |
| `oracle/registry/properties.md` | read fully (173) |
| `oracle/registry/property-templates.md` | read fully (192) |
| `oracle/registry/topology-atlas.md` | read fully (78) |
| `oracle/registry/typeclass-alphabet.md` | read fully (148) |
| `oracle/registry/typed-compositions.md` | read fully (345) |
| `oracle/state/born-oppenheimer-levels.md` | read fully (116) |
| `oracle/state/crystal-inputs.md` | read fully (156) |
| `oracle/state/gamma-hat.md` | read fully (190) |
| `oracle/compilation/compose-time-pipeline.md` | read fully (399) |
| `oracle/compilation/representation-substrate.md` | read fully (379) |
| `oracle/accuracy/accuracy-ledger.md` | read fully (462) |
| `oracle/accuracy/reference-battery.md` | read fully (173) |
| `operator/loss/residual-loss-design.md` | read fully (479) |
| `operator/seam/learnable-structure-contract.md` | read fully (197) |
| `operator/training/training-stages.md` | read fully (143) |
| `interface/boundary.md` | read fully (67) |
| `oracle/laws/coupling-structure.md` | read partially, **lines 435–690** as instructed |

**Pages that produced nothing, and what was checked on each** (no free emptiness):

- **`library-landscape.md`** — three-library partition against the three sections and "There
  is no fourth library"; the three oracle exclusions against the CLI-placement and
  engineering sections; operator/interface remits against each other. All consistent.
- **`build-sequence.md`** — the frontmatter's "Five phases … are marked open" against the
  five `open` cells in the table (matches); "Two admission rules" against the two named
  (matches); the `in`/`open` definitions against the exit criterion's dependence on phase
  13 (consistent — the page reasons about exactly this); "two collapses" against the table
  order; recommended start order against table order.
- **`canonical-vocabularies.md`** — "the ten vocabularies" against the ten table rows
  (matches); "Each of the ten is a `Universe` instance" against the atomic-species section;
  "exactly four certification obligations" against the four named; the hybrid-functional
  normalisation rule against `ManyBodyLevel`'s member list (Hybrid correctly absent).
- **`observable-bundles.md`** — "the eleven bundles" against the eleven table rows; "twelve
  admissible values in all" against eleven names plus `linear-response-primitive`; "Four
  rows carry a behaviour name" against the four listed; rows 91–94 against "four rows
  carrying a value it does not recognise".
- **`topology-atlas.md`** — "All four are lookups or integer linear algebra" against the
  four cheap parts listed; the five-field atlas entry against "Every field is
  combinatorial"; the cheap/expensive split against "for every composition rather than for
  a chosen few"; "Topology is the map, not a feature" against the consumption argument.
- **`typeclass-alphabet.md`** — "three orthogonal axes plus a discrete bucket, captured as
  four typeclasses" against the four sections; "Four aliases" against the four named and
  "The other three … never expanded"; `combineTol` monotonicity against the two composition
  rules; `DiscreteStructure`'s exclusions against the orthogonality claim.
- **`gamma-hat.md`** — the 5×4 encoding product against the five first-class pairs;
  scorer-only against the read/write path asymmetry and the self-consistency paragraph;
  node-identity-exact against the rewrite-admission rule; the memory-budget encoding claim
  against "never densified" and the supercell paragraph.
- **`learnable-structure-contract.md`** — "five properties" against the five table rows;
  "Two offers" against the two listed; loop-agnosticism against every requirement section
  (none names a specific loop); seam purity against the conditioning-channel obligation;
  the six "does not ask about" bullets against "Why an operator". Its two declared gaps
  (unified-state wire schema, environment record) are honest gaps, not contradictions.
- **`training-stages.md`** — three stages against "It attaches for one stage" and "Nothing
  on the inference path calls the oracle"; "all three failures are silent" against the
  three bullets and "None of the three announces itself"; the Grover preconditions against
  the refutation; the two curriculum schedules against the declared open question.
- **`forced-decisions.md`** — "Three decisions" against the three sections; the four-role
  table against "Only two of the four roles are live at all" and the `Runs` column;
  "Neither is restated here" against the two anchors named; the substrate-output list
  against the open question on exact form.
- **`boundary.md`** — "declared stub" against the five owned items and the undesigned list;
  "Nothing in this list is visible through the seam" against the gradient-sink bullet;
  driver-versus-command-line against the CLI placement.

---

## 3. Findings

Ten STRONG, twelve MEDIUM, one WEAK. Ordered strongest first within severity.

### F1 — `oracle/accuracy/reference-battery.md`, "Invariant checks on a computed row" · STRONG

> **first half** (line ~110): "Each is a closed form that any correct calculation already satisfies, and each follows from a conservation law."

> **second half** (line ~117): "| `det(A) = V` | the lattice-matrix determinant equals the reported volume | arithmetic |"

**Why they cannot both be true:** The universal says each of the five checks follows from a
conservation law. The table's own third column is exactly the column that names the law,
and for this row it names "arithmetic", which is not a conservation law. The `spin parity`
row is a second instance — "you cannot pair every electron" is a counting argument.

**Which is correct:** The table. Three of the five follow from conservation laws; the
sentence should say so rather than claiming all five do.

**What would refute this finding:** A reading on which "arithmetic" names a conservation
law.

### F2 — `oracle/registry/properties.md`, "Category to bundle" · STRONG

> **first half** (line ~90): "Each category projects onto one or more observable bundles"

> **second half** (line ~102): "| Magnetic | none |"

**Why they cannot both be true:** The sentence introducing the table universally quantifies
over categories; the table it introduces contains a row with no bundle. The page's own
frontmatter settles it — "The magnetic category projects onto no observable bundle" — and
the paragraph after the table repeats it: "the category is in scope and has no bundle
behind it".

**Which is correct:** "none". The introducing sentence is the defect.

**What would refute this finding:** Nothing on this page; the page contradicts the sentence
three separate times.

### F3 — `n-op/build/build-verification.md`, "The strain hypersurface this gate runs against" · STRONG

> **first half** (line ~104): "Twenty-four shapes are each computed three times, and the three copies agree bit for bit, so de-duplication drops 48 surplus rows and loses nothing."

> **second half** (line ~113): "- The three copies of a shape are geometrically identical and **textually different**."

**Why they cannot both be true:** "Agree bit for bit" means byte-identical rows. The second
passage says they are textually different and gives the mechanism — "One row leaves the
untouched skew columns blank; the others write an explicit `0.000` into one of them." Both
cannot hold, and the difference is load-bearing: it is the entire reason "Sorting the
geometry columns for unique rows therefore returns all 1,179".

**Which is correct:** "Textually different". It carries the specific evidence and the whole
de-duplication argument depends on it; "agree bit for bit" should say the physical values
agree.

**What would refute this finding:** Reading "bit for bit" as scoped to the numeric columns
only — but the passage that follows is explicit that a numeric column also differs in
representation.

### F4 — `oracle/accuracy/reference-battery.md`, "The row schema" into "Invariant checks" · STRONG

> **first half** (line ~101): "**Population is incremental and reviewable: every row must be defensible against a literature citation before it is committed.**"

> **second half** (line ~107): "**A row whose `Source` is a computational provenance has no citation to be defensible against**"

**Why they cannot both be true:** If no row may be committed without being defensible
against a literature citation, then no committed row can lack a citation. Six lines later
the page describes a committed class of rows that has none, and devotes a whole section to
what defensibility means for them instead. The schema confirms the class exists: "**Source**
— a DOI, paper title and page reference; or a computational provenance".

**Which is correct:** The second. The universal should read "defensible against a literature
citation or against the invariant checks below".

**What would refute this finding:** Reading "a literature citation" as a stand-in for "a
defensibility argument of any kind" — but the next section explicitly contrasts the two.

### F5 — `oracle/registry/property-templates.md`, "Overlap resolution" · STRONG

> **first half** (line ~178): "Three constructions look like candidate templates and are not:"

> **second half** (line ~82): "| `HarmonicStiffnessHessianOf` | the mass-weighted dynamical matrix |"

**Why they cannot both be true:** The third construction in that list is
`HarmonicStiffnessHessianOf` — "**`HarmonicStiffnessHessianOf` specializes
`SecondDerivativeOf`** rather than duplicating it." But it *is* a template on this page: it
has a row in the "What each template produces" table and a full entry in the typed-signature
block. The other two entries in the overlap list (`ClusterExpansion`, bulk-boundary
correspondence) correctly appear in neither.

**Which is correct:** It is a template. The overlap-resolution list's framing sentence is
wrong for its third item — that item resolves a *duplication* question, not a
*templatehood* question.

**What would refute this finding:** A reading of "look like candidate templates and are not"
that admits things which are templates.

### F6 — `oracle/compilation/compose-time-pipeline.md`, "Symbolic lift" into "Invariant synthesis" · STRONG

> **first half** (line ~113): "After this stage every remaining node is meaningful for this composition, and the sidecar is discarded."

> **second half** (line ~146): "**Inputs.** The `SymbolicLiftSidecar.coupling-channels : List<CouplingChannel>` declared by the composition"

**Why they cannot both be true:** Symbolic lift discards its sidecar at stage exit; invariant
synthesis, two stages later, takes a field of that same sidecar as an input. Either the
sidecar survives — and "the sidecar is discarded" is false — or the "Sidecar produced" entry
for symbolic lift is incomplete and `.coupling-channels` belongs to something else. The
page's own convention elsewhere is explicit about survival ("`SymmetrySidecar.symmetry` …
consumed during lowering") and about erasure ("all three are erased once codegen completes"),
so the reader has no third reading available.

**Which is correct:** Underdetermined from the passage. The sidecar must survive for the
pipeline to work, so "discarded" is the likelier defect — but which field is discarded and
which persists is not recoverable from this page.

**What would refute this finding:** A statement that `SymbolicLiftSidecar` has per-field
lifetimes and only `.applicability` is discarded.

### F7 — `oracle/laws/coupling-structure.md`, "Mechanism range" into "Extension types" · STRONG

> **first half** (line ~573): "| electron-phonon (piezoelectric acoustic, long-range) | `LongRangeStatic(1)` | **false** |"

> **second half** (line ~605): "tag            : FroehlichLongRange | ScreenedCoulombRPA | GWQuasiparticleSelfEnergy | TDDFTXCKernel"

**Why they cannot both be true:** The well-formedness invariant on the page is
"`polynomial_sufficient(c) ⟺ (c.kernel_extension = None)`, and a non-sufficient channel's
`kernel_extension.tag` must match its `mechanism_range`." The piezoelectric-acoustic channel
is non-sufficient, so it must carry a `KernelExt` whose tag matches its mechanism — and the
tag vocabulary, stated on the page to have "All four variants", contains no piezoelectric
variant. The channel is unrepresentable under the page's own schema.

**Which is correct:** Underdetermined. Either the tag vocabulary is short a fifth variant, or
the piezoelectric-acoustic row's `polynomial_sufficient` value is wrong — but the derived
projection `LongRangeStatic(_) => false` forces the value, so the vocabulary is the likelier
gap.

**What would refute this finding:** A rule permitting `FroehlichLongRange` to tag any
`LongRangeStatic` pole order — which the page's own "tag a channel by its general mechanism"
instruction argues against, since it names the two as distinct mechanisms.

### F8 — `oracle/registry/formula-registry.md`, "The fields" into "Where a field's vocabulary lives" · STRONG

> **first half** (line ~43): "One column per field of the formula record"

> **second half** (line ~99): "| `applicability` | [applicability-classifiers#the-predicate-contract] |"

**Why they cannot both be true:** The section titled "The fields" enumerates nine fields as
the manifest's complete column set, one per field of the record. `applicability` is not among
them. Fifty lines later it appears as a row of the coded-field vocabulary table, under the
sentence "Each coded field draws on a closed vocabulary, and **each vocabulary is defined on
exactly one page**". A field cannot be a coded field of the record and absent from the
record's field list.

**Which is correct:** `applicability` is a real field — [crystal-inputs#crystal-type] treats
the applicability signature as "carried by every registry row". "The fields" table is missing
a row.

**What would refute this finding:** `applicability` being carried inside the `signature`
field rather than as its own column, which the fields table's description of `signature`
("typed inputs to output, with units") does not support.

### F9 — `oracle/compilation/compose-time-pipeline.md`, "The compose-time and runtime boundary" · STRONG

> **first half** (line ~364): "| algebraic simplification | graph → shared, sparse graph | once per composition | term rewriting over an e-graph | open-ended; the hardest pass |"

> **second half** (line ~397): "The seconds-to-minutes compile figure covers the five symbolic stages."

**Why they cannot both be true:** The table's Cost column gives four of the five symbolic
stages a bounded figure and gives algebraic simplification "open-ended". The closing sentence
then asserts a seconds-to-minutes figure covering all five. The page states the open-endedness
twice more — "its cost is the one open-ended figure in the compose-time budget", and the
frontmatter's "no bound on saturation time or e-graph size is committed anywhere".

**Which is correct:** The table. Compile cost is unbounded until the e-graph pass is bounded.

**What would refute this finding:** A reading of "covers" as "covers the four bounded ones" —
which the word "five" forecloses.

### F10 — `oracle/registry/typed-compositions.md`, "What this page proves" against "Magnetic" · STRONG

> **first half** (line ~56): "**All target observables resolve to typed compositions over the closed vocabulary, except the declared gap below** — eighteen invoked formula names that are not manifest rows."

> **second half** (line ~207): "`exchange-coupling-formula` names nothing in the manifest and sits in a kernel slot rather than a formula slot, so the declared-gap mechanism below does not cover it."

**Why they cannot both be true:** The headline claim names exactly one exception — the
eighteen-row declared gap — and stresses that "The claim is stated with its exception rather
than without." Two further names fall outside the closed vocabulary and outside that
exception: `exchange-coupling-formula` and, at line ~296, `harmonic-rate-prefactor`, "in a
slot the declared-gap mechanism does not sweep". The page's own frontmatter records them as a
separate open question.

**Which is correct:** The exceptions are real; the headline claim understates them by two.
A tighter instance of the same defect sits nine lines apart at lines ~296 and ~305, where
"a new unregistered name still fails loudly" stands directly beside a documented unregistered
name that does not fail at all.

**What would refute this finding:** Reading "target observables resolve to typed
compositions" as a claim about formula slots only, which the surrounding prose does not
qualify it to.

### F11 — `n-op/build/mvp-system.md`, "What each anchor forces" · MEDIUM

> **first half** (line ~37): "The lattice constant, the indirect gap, the maximum phonon energy, the Debye temperature, the thermal conductivity and the elastic constants are the diamond battery anchors"

> **second half** (line ~50): "| Polarity | Diamond is **non-polar (homopolar)**, so the Born effective charge vanishes by symmetry"

**Why they cannot both be true:** The prose enumerates the anchors as six named quantities.
The table that follows is headed "| Anchor | What it forces on the MVP |" under a section
promising "what each measured anchor **forces** on the build" — and its six rows include
Polarity, which is not on the list, and omit the lattice constant, which is. Polarity is also
not a *measured* anchor by the row's own account ("vanishes by symmetry"), against "Each row
is a design decision derived from a measurement".

**Which is correct:** Underdetermined. Either the anchor list is short Polarity and the
lattice constant forces nothing worth a row, or the table has an extra row and a missing one.

**What would refute this finding:** Reading the table as "anchors and other forcing facts",
which the column header "Anchor" and the section title "what each anchor forces" do not
license.

### F12 — `n-op/build/capability-slices.md`, "What the three slices add up to" · MEDIUM

> **first half** (line ~102): "Every figure below is a sum over the three tables above."

> **second half** (line ~136): "**The buildable unit is roughly one-third of the full vocabulary.** That is the one judgment on this page rather than a sum"

**Why they cannot both be true:** The section opens by asserting that every figure below it is
a sum over the three slice tables, and closes with a figure that is explicitly declared not a
sum. The bullet on certification obligations is a second instance: "The registration adjoint
gate — obligation 10 — stays in the MVP because adjoint-tagged gradients must be validated
when the operator first trains" is a design argument, not a summation, and obligation 10
appears in none of the three tables' Certification cells.

**Which is correct:** The opening sentence is too broad. It should scope to the bulleted
totals, and even there obligation 10 is an exception.

**What would refute this finding:** Reading "below" as scoping only to the bulleted list under
"**In the MVP.**" — available, hence MEDIUM.

### F13 — `oracle/accuracy/reference-battery.md`, "The row schema" · MEDIUM

> **first half** (line ~82): "**Three uncertainty encodings appear, and a consumer must dispatch on the format.**"

> **second half** (line ~90): "A bare `—` means the uncertainty is **not yet assigned**, which is a different state from `unbounded`."

**Why they cannot both be true:** A consumer dispatching on the Uncertainty column's format
meets four, not three: an absolute value, a `×N` factor, `unbounded`, and a bare `—`. The page
insists `—` is a distinct state from `unbounded`, and `unbounded` is counted as one of the
three — so the fourth cannot be excluded on the grounds that it encodes an absence.

**Which is correct:** Four states. The count and the table exclude a format the very next
paragraph requires a consumer to handle.

**What would refute this finding:** Treating "encoding" as strictly "encoding of a value",
which would also exclude `unbounded` and leave two.

### F14 — `oracle/compilation/representation-substrate.md`, "Hot-path commitments" · MEDIUM

> **first half** (line ~290): "The two super-logarithmic rows below — symmetry projector, evidence aggregation — are compile-time, cached, or certification-side, and are not per-sample."

> **second half** (line ~300): "| `SparseSet` membership (tuple, n ≤ 8) | `O(n)` | linear scan, no indirection |"

**Why they cannot both be true:** `O(n)` is super-logarithmic, and this row is neither the
symmetry projector nor evidence aggregation. `MerkleDAG` diff (`O(changed frontier)`) is a
third candidate. The count-word "two" is load-bearing here: it is what lets the page assert
"No **runtime per-sample** hot path is worse than logarithmic" while the table below contains
a linear row.

**Which is correct:** Underdetermined. Either the tuple backend's bound should be written
`O(1)` because `n ≤ 8` bounds it, or the count is wrong.

**What would refute this finding:** Reading `O(n)` under a fixed `n ≤ 8` as constant — in
which case the table should not write it as `O(n)`.

### F15 — `oracle/state/born-oppenheimer-levels.md`, "The four levels" into "The irreducible state" · MEDIUM

> **first half** (line ~31): "The micro seven-tuple ([unified-state#slots]) partitions into four levels."

> **second half** (line ~65): "The micro seven-tuple is the tier of the two lowest levels."

**Why they cannot both be true:** A partition into four levels gives each of the four a share
of the seven-tuple. The second sentence confines the whole seven-tuple to the lowest two, and
the intervening paragraph says why: the kinetics level's state is "not recoverable from a
single micro seven-tuple" and lives in two other tiers. The level table agrees — the two
upper rows operate on occupations and phase-space distributions, neither of which is a slot.

**Which is correct:** The second. The four levels partition the state-component space, of
which the seven-tuple is only the micro part.

**What would refute this finding:** Reading "partitions into four levels" as permitting empty
parts, which the following sentence ("Each level … **introduces its own irreducible state**")
argues against.

### F16 — `operator/loss/residual-loss-design.md`, "The assembled loss" into "The label-presence mask" · MEDIUM

> **first half** (line ~315): "**All three multiply into the same loss term**, which is exactly why they need three names."

> **second half** (line ~289): "m_o       label-presence for observable o on this sample, 1 or 0"

**Why they cannot both be true:** The assembled loss is written out in full with its legend,
and exactly one mask appears in it — `m_o`, on the three data terms. The residual term
`Σ_i λ_i(t) · residual_i(ŷ ; state)` carries no mask at all, though the
`sample-applicability-mask` is defined precisely as "whether a given generator applies to that
sample". The claim that all three multiply into the same term is not realised by the formula
the page prints.

**Which is correct:** All three are needed — the argument for it is specific and correct
("Conflate any two and the loss is wrong and green"). The written loss is incomplete.

**What would refute this finding:** Reading the loss block as schematic, with the index sets
`O_cheap` and so on absorbing applicability and coverage.

### F17 — `operator/loss/residual-loss-design.md`, "Residuals with no useful derivative" · MEDIUM

> **first half** (line ~196): "Three techniques move such a quantity into the `relaxed` tier, which is the tier that ships a *named* relaxation:"

> **second half** (line ~208): "the discrete fact becomes the sign of a differentiable scalar, and the residual stays exact"

**Why they cannot both be true:** The third technique is described as removing the
discreteness "rather than smoothing it", leaving the residual exact. An exact residual has
relaxed nothing, so it has no named relaxation to ship — yet the framing sentence places all
three techniques in the tier defined by shipping one.

**Which is correct:** The surrogate continuous residual does not belong in `relaxed`. The
page's own consequence elsewhere sharpens this: "Every `relaxed` entry carries a rationale
**naming its relaxation**".

**What would refute this finding:** Treating the substitution of a signed continuous quantity
for a boolean predicate as itself the named relaxation.

### F18 — `oracle/compilation/compose-time-pipeline.md`, "The compose-time and runtime boundary" · MEDIUM

> **first half** (line ~374): "Runtime is a straight-line numeric function with no symbols, no structural branching, and no solver invoked from scratch."

> **second half** (line ~391): "| per-composition reference | property and reference solves | seconds–minutes | once per composition |"

**Why they cannot both be true:** Seventeen lines after the unqualified claim, the page opens
"**Runtime cost is three-class, not one**" and gives one of the three runtime classes as
property and reference *solves* costing seconds to minutes. A straight-line numeric function
does not take minutes and does not solve.

**Which is correct:** The three-class table. The earlier sentence describes only the
per-sample core; it should say so, as the neighbouring claim does ("every runtime hot path").

**What would refute this finding:** Reading "no solver invoked from scratch" as permitting
warm-started solves, which the page does not state.

### F19 — `oracle/registry/computational-methods.md`, "Sub-methods" · MEDIUM

> **first half** (line ~130): "**A sub-method extends a method's dispatch table without changing its typed signature.**"

> **second half** (line ~136): "`mesh-interpolation` is the compile-time band and electron-phonon interpolator."

**Why they cannot both be true:** `mesh-interpolation` is registered under
`kinetic-evolution`, whose typed signature on this page is `KineticEvolution(distribution:
Distribution, collisions: CollisionKernel, gradient: AppliedGradient, method: KineticMethod,
truncation: Int) → SteadyState`. If a sub-method cannot change that signature, then
`mesh-interpolation` maps a distribution to a steady state — which a band and
electron-phonon interpolator producing "the interpolated grid" at compile time does not do.
It also does not fit "Every program the oracle runs is a composition in this alphabet",
since it runs before the program does.

**Which is correct:** The description of what `mesh-interpolation` does. Its placement under
`kinetic-evolution` is what does not fit — the other six sub-methods in that list (BTE-RTA,
BTE-full, master-equation, drift-diffusion, Cahn-Hilliard, Allen-Cahn) are all genuine
kinetic-evolution schemes.

**What would refute this finding:** A reading on which `KineticMethod` admits values that
change the return type.

### F20 — `n-op/build/capability-slices.md`, "Heat diffusion" against the totals · MEDIUM

> **first half** (line ~94): "| Deferred | 13 self-consistent phonon theory, since the quasi-harmonic approximation suffices to about 800 °C"

> **second half** (line ~133): "Deferrals are stated once, where scope exclusions are owned."

**Why they cannot both be true:** The rule says deferrals are stated once and elsewhere — on
[out-of-scope#exclusions]. This page states them twice: the heat slice's table has a
"Deferred" facet naming three rows with their reasons, and the totals paragraph names
"self-consistent phonon theory" among the deferred complement. Same page, same item, two
statements, under a sentence claiming one statement elsewhere.

**Which is correct:** Underdetermined. Either the table's Deferred facet is a legitimate
per-slice restatement and the rule needs qualifying, or the facet should not carry reasons.

**What would refute this finding:** Reading "stated once" as applying to the reason and not
the fact of deferral — but the table's cell carries both.

### F21 — `oracle/registry/formula-registry.md`, "The fields" against "Where a field's vocabulary lives" · MEDIUM

> **first half** (line ~101): "**Every consumer harvests the vocabulary from its defining page. No consumer restates it.**"

> **second half** (line ~50): "| `bundle` | one or more observable bundles, or `linear-response-primitive` |"

**Why they cannot both be true:** The page names [observable-bundles#the-eleven] as the
defining page for the `bundle` field's vocabulary and forbids any consumer from restating it.
Its own fields table then hard-codes one admissible value of that field. This is the exact
failure the rule warns about in the next sentence — "a checker that hard-codes the admissible
values validates the column against its own copy".

**Which is correct:** The rule. The fields table should describe the `bundle` column without
naming a member of its vocabulary.

**What would refute this finding:** Treating `linear-response-primitive` as a
not-a-bundle sentinel owned here rather than a bundle-field value — but
[observable-bundles] counts it as one of "twelve admissible values in all".

### F22 — `oracle/laws/coupling-structure.md`, "Coverage policy" · MEDIUM

> **first half** (line ~501): "The MVP global cap is `(max_order = 4, max_derivative = Gradient(1))`."

> **second half** (line ~504): "Every other mechanism class fits inside `(2, Gradient(1))`, with a few reaching `order = 3`."

**Why they cannot both be true:** The second sentence asserts a universal and falsifies it in
its own trailing clause: a mechanism class reaching `order = 3` does not fit inside
`(2, Gradient(1))`. These are the per-mechanism caps that prune tuples before the character
test, so the numbers are operative, not descriptive.

**Which is correct:** Underdetermined. Either the per-mechanism cap is 3 with anharmonicity
at 4, or it is 2 with named exceptions — the sentence supports neither cleanly.

**What would refute this finding:** Reading "fits inside" as "typically fits inside", which
a cap parameter cannot mean.

### F23 — `oracle/state/crystal-inputs.md`, "What is not an input" into "The Crystal type" · WEAK

> **first half** (line ~139): "`Reference` is a bag of `(Crystal, Environment, weight)` baselines."

> **second half** (line ~149): "It is also the shape of the `Reference` baseline above."

**Why they cannot both be true:** "It" is `(Crystal, Environment) → Bool`, whose argument
shape is a pair. The `Reference` baseline is a triple. Ten lines apart, and the page is
elsewhere exacting about argument shapes — it argues from a redundant second argument to
settle what `Crystal` means.

**Which is correct:** The triple. "The shape of the `Reference` baseline" is loose for "the
system-identifying part of it".

**What would refute this finding:** Reading "shape" as the keying part rather than the whole
tuple — which is why this is WEAK.

---

## 4. Near-findings rejected

- **`computational-methods.md`**, "Each method carries a typed signature and a sub-method
  dispatch" against `algebraic-combination`, which has no `sub:` list. Rejected: "always
  dispatches to a registry row" occupies the dispatch slot, so it does carry one.
- **`computational-methods.md`**, "without them these signatures do not type" against
  "Neither the twelve signatures here nor the twenty on [property-templates] can be typed as
  written". Rejected: the first states a necessary condition, not a sufficient one.
- **`build-verification.md`**, the adjoint-tape exemption ("Without that exemption the pairing
  rule would be over-broad") against the pairing rule's own trigger ("Every generator whose
  lowering introduces representation error"). Rejected: rhetorical over-claim — the rule as
  written already excludes it, so the exemption is redundant rather than contradictory.
- **`property-templates.md`**, "the three are distinct in form rather than in kind" against
  the signature note that the cluster expansion is a discrete zero-temperature lattice energy
  and Redlich–Kister a continuous finite-temperature excess Gibbs energy. Rejected as
  borderline: discrete-versus-continuous is arguably a difference in form.
- **`typeclass-alphabet.md`**, "Every numeric output is a `Quantity`" against
  `DiscreteStructure`'s "Not a `Quantity` — there are no units" for integer invariants.
  Rejected: the page's own framing treats integer invariants as labels, not numbers.
- **`typeclass-alphabet.md`**, `derivative : f → Domain → Maybe Tangent` described as "total on
  the domain *minus* an `exceptionSet`". Rejected: `Maybe` makes it total on the whole domain
  and the prose is a gloss on when it yields a value.
- **`typed-compositions.md`**, "**They are deliberately not registered.** … registering these
  on thin provenance would put unsourced rows into the artifact" against "registering one is
  transcription plus tag assignment" for the nine transcription rows. Rejected: reconcilable
  — a transcription row still owes a citation for its convention.
- **`representation-substrate.md`**, "Hashing is the only payload-linear operation anywhere on
  the identity path" against the sorting steps in serialization rules 3, 5 and 6. Rejected:
  checking it means reasoning about complexity, which is out of scope here.
- **`representation-substrate.md`**, "The serializer's **injectivity** is the single
  highest-consequence invariant" against rule 11's collapse of negative zero and distinct NaN
  patterns. Rejected: the page treats those as numerically equal values, not distinct ones.
- **`representation-substrate.md`**, the `n ≤ 8` / `n ≤ 256` backend ladder against "The choice
  is a property of the universe, fixed at registration — not of an individual sparse set".
  Rejected: `n` reads as universe cardinality throughout ("over a small closed universe",
  "over a large universe").
- **`compose-time-pipeline.md`**, "Equality saturation stays an **offline** rewrite oracle"
  against algebraic simplification running "once per composition" in the compose-time budget.
  Rejected on this page: "offline" is undefined here and reads as "not on the runtime path".
  (Noted in by-catch, since the corpus defines "offline" as distinct from compose time
  elsewhere.)
- **`gamma-hat.md`**, "States arrive complete, are scored, and are discarded" against the write
  path being "construction and the self-consistent step". Rejected: "construction" reads as
  building the internal encoding of an arrived state.
- **`crystal-inputs.md`**, `pressure` typed `UNSEEDED` against `p_O2` typed `Pressure` (Pa) and
  described as "a specialisation of the pressure slot". Rejected: the pressure slot's note
  ("carried as pressure or as volume") genuinely leaves its type open.
- **`crystal-inputs.md`**, "the predicates are first-order decidable on field presence alone"
  against every predicate taking a `Crystal` argument. Rejected as reconcilable: "alone" reads
  as scoped to the environment half of the decision.
- **`crystal-inputs.md`**, "Every environment field is either **structural** or **swept**"
  against "The rest of the partition is unstated". Rejected: that is a declared gap, not a
  contradiction.
- **`accuracy-ledger.md`**, the frontmatter's "before any transport regime below factor two can
  be claimed" against regime rows 16–22 claiming ±10–30%. Rejected: row 2 supplies the escape
  ("interpolation is the only path off factor two") and the sub-method exists.
- **`accuracy-ledger.md`**, "it is not the citation of record" against six curated-coefficient
  tables each carrying a `source` column. Rejected: declining canonicity is not the same as
  declining to carry copies.
- **`accuracy-ledger.md`**, row 13's "relaxation-time three-phonon **underestimates** diamond by
  30–50% near 300 K" against "three-phonon scattering alone **overpredicts** diamond
  conductivity by 31% at 1000 K". Rejected: different methods at different temperatures; both
  can hold.
- **`coupling-structure.md`**, "the theory choice has already selected the symmetry group and
  conditioned the coefficient values … `theory_context` is therefore solely metadata".
  Rejected: "solely metadata" is scoped to the runtime kernel by the preceding clause.
- **`coupling-structure.md`**, "positive-semidefiniteness is **structurally guaranteed by
  physics** … not a runtime search" against the per-evaluation guard `λ_min(M_block) ≥ −δ_PSD`.
  Rejected: the assumption blocks declare "tight at the operator level / loose at the
  coefficient level" on the same page.
- **`residual-loss-design.md`**, "fixed weights inside the residual family … without exploding
  the parameter count" against Defaults offering "Optional per-point self-adaptive weights".
  Rejected: "optional" carries it, though it strains "Each is the recommendation of a section
  above".
- **`observable-bundles.md`**, "the four rows below" (rows 91–94) against "Four rows carry a
  behaviour name" (a different four). Rejected: two disjoint sets of four; both can be true.
  A genuine reader hazard, not a contradiction.
- **`learnable-structure-contract.md`**, "Only flat numeric arrays cross the boundary" against
  accepting the environment record. Rejected: marshalling as per-channel flat arrays is
  available.
- **`training-stages.md`**, "none of the three preconditions holds" where the third listed item
  (amplitude amplification) is a technique rather than a precondition. Rejected: wording, not
  a contradiction.

---

## 5. By-catch

Not this defect class, not investigated.

- **Cross-page.** `born-oppenheimer-levels` says the MVP "needs exactly one dressing wired";
  `capability-slices` says "The substrate and one-shot-dressing layers are wired: G₀W₀, the
  quasi-harmonic approximation, and density-functional perturbation theory."
- **Cross-page.** `coupling-structure`'s MVP default theory context is `KohnSham` plain DFT
  with the gap handled "not by upgrading the default"; `mvp-system` says "**G₀W₀ or a hybrid
  functional is required**" and `born-oppenheimer-levels` wires G₀W₀ into the MVP.
- **Cross-page.** `library-landscape` says the oracle library "holds no instance" of the state
  type; `gamma-hat` budgets ~18 MB of density-matrix storage inside it.
- **Cross-page.** `computational-methods` names the typeclass return aliases as "`Response`,
  `Field` and `Tensor`"; `typeclass-alphabet` lists the four aliases as "`Scalar`, `Tensor`,
  `FieldOnGrid`, `Response`" — `Field` is used but is not an alias, `FieldOnGrid` is an alias
  but does not appear in the method signatures.
- **Cross-page.** `forced-decisions` uses "offline" as a `Runs` value distinct from "compose
  time"; `compose-time-pipeline` calls equality saturation "offline" while running it once per
  composition inside the compose-time budget.
- **Cross-page.** `compose-time-pipeline` bars runtime structural branching; `crystal-inputs`
  has a sample "masked out, or trips the relevant certification obligation" when its swept
  scalar leaves the kernel's environment box.
- **Cross-page.** `build-sequence` names its phase-8 admission rule "**Fidelity of the
  assembled operators**"; `build-verification` and `residual-machinery` use "fidelity" for
  representation-error pairing, a different concept.
- **Cross-page.** `crystal-inputs` says applicability predicates are "first-order decidable on
  field presence alone"; `build-sequence` requires them "first-order decidable on typeclass
  tags".
- **Cross-page.** `coupling-structure`'s per-evaluation PSD guard `λ_min(M_block) ≥ −δ_PSD` is
  an eigenvalue computation, against `representation-substrate`'s "No hot path requires a
  solver call".
- **Cross-page.** `training-stages` says the informed epoch consumes keyed residuals "never a
  sum"; `learnable-structure-contract` has the external loop "linearly combines them into
  **one** state-shaped cotangent".
- **Count that looks wrong.** `accuracy-ledger`, "five of those anchors are in the
  seeded-value provenance section below, two of them UNSEEDED" — the provenance section names
  closer to ten diamond anchors.
- **Count that looks wrong.** `accuracy-ledger`, "Four rows carry a *method* in the `Source`
  cell" against a table whose four entries cover six reference rows (two of them span 773 and
  1100 K).
- **Arithmetic that looks wrong.** `accuracy-ledger`, κ at 773 K is "path-met — the four-phonon
  correction, registry row 121, valid `≳0.4 Θ_D`" while regime row 12 puts that threshold "at
  about 880 K on the seeded Debye temperature". Left here rather than in findings because
  checking it is a numeric comparison, and the page's `diamond-debye-temperature-unseeded`
  open question already records the underlying issue.
- **Arithmetic that looks wrong.** `accuracy-ledger`, regime row 53 targets "±30% on p" for the
  pyroelectric slope while the seeded values carry "×2".
- **Arithmetic that looks wrong.** `gamma-hat`, "orbital storage stays roughly linear in
  `N_atoms × N_b`" where both factors grow with supercell size.
- **Missing information.** `typed-compositions`, `formation-energy-from-references` is
  classified "research | needs literature" while the structurally identical
  `adsorption-energy-difference` is "transcription | determined by its inputs".
- **Missing information.** `capability-slices` claims "All computational methods except
  `path-search` and `statistical-sampling`", implying a twelve-method vocabulary; the three
  slice tables between them name ten.
- **Formatting.** `property-templates`, "Overlap resolution" — the three bullets are merged
  into one list item (` - ` mid-line at lines ~183 and ~188), so the second and third
  constructions do not render as separate bullets.

---

## 6. Boundary compliance

`git status --porcelain journals/ data/` — **empty output.** The corpus is byte-identical to
how I found it.

- No scratch copy was made. No `cp -r`, no diff of the corpus against anything.
- The only file written under the repository is this report,
  `/home/javier/Projects/Physics/Programs/n-Op/audit/findings/class1-tail.md`. One
  quote-verification script was written to `$CLAUDE_JOB_DIR/tmp`, outside the repository, and
  reads `journals/` only.
- No other file under `audit/` was read or written. In particular
  `audit/findings/class1-adjacent-contradictions.md` was not opened, and no search was run for
  hints about `practice/conventions.md` before the calibration pass.
- No agent was contacted, no subagent spawned, no message sent.
