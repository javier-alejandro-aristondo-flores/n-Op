# Class 1 — adjacent self-contradictions

One instrument, one class: **two claims, in one place, that cannot both be true.** No
arithmetic, no cross-page resolution, no literature, no registry. Everything below rests
on quoted primary text with locations, so a third party can see the incompatibility
without trusting the reader.

---

## 1. Calibration, unrounded

### 1a. The known instance — found by reading

`journals/oracle/laws/residual-definitions.md` was read cold, end to end, before anything
else. The method surfaced the known instance.

- **line 74:** "Seven per micro state-component degree of freedom
  ([unified-state#slots]), plus two cross-tier siblings"
- **lines 78–85** enumerate seven, ending: "7. `EOM/Z` — same form on atomic-number
  labels; non-trivial only under chemistry-active dynamics, otherwise structurally null."
- **line 255**, under *What becomes a separately-weightable contribution*: "The
  equation-of-motion violation per state component `i ∈ {h, R_I, P_I, Π_h, γ̂, A}`,
  optionally per spatial or momentum bin."

Six components. `Z` is dropped. **Confirmed by reading.**

One qualification on the word *adjacent*: this instance spans two sections of one page
(line 74/84 against line 255), not two sentences. The class as it actually occurs in this
corpus is **same-page, same-owned-concept**, and that is the scope I swept.

### 1b. Planted defects — 4 of 4

I asked the `blind-calibrator` teammate to plant an unknown number of contradictions in a
separate scratch copy. Its reply — the single word "planted" — **arrived after this report
was written**, and the blind control was then destroyed before it could be run (see
Appendix A). What follows is the weaker self-plant, reported as such.

To recover as much blindness as possible, a script chose and applied the edits; I did not
see the sites, counts, or diffs before reading. It planted **4** defects across an unknown
subset of 6 unread pages, by two transformations: bump a spelled-out count word, and flip
a `never` to `always`.

| # | Page | Planted defect | Found? |
|---|---|---|---|
| 1 | `oracle/registry/named-formulas.md` | "Optical absorption is `(2ω/c)·Im(√ε)` — the factor of **three** is part of the form." | yes |
| 2 | `oracle/seams/residual-machinery.md` | `characteristic-scale` comment: "the observable's **declared** accuracy scale … an error-model input, **always** a fitted weight" | yes |
| 3 | `oracle/state/multiscale-state.md` | "they create no algebraic constraint with the micro **eight**-tuple" (page says seven-tuple 4× elsewhere) | yes |
| 4 | `oracle/laws/coupling-structure.md` | "split into **three** channels — a short-range polynomial one and a long-range kernel one" | yes |

**4 of 4.** Two of the six pages (`unified-state.md`, `physics-graph.md`) carried no
plant, and I reported none from them — **no false positives on the planted class.**

**What this control is worth, honestly.** I knew plants existed and knew the two
transformation families, so this measures whether the shape survives my reading depth, not
whether I would notice it unprompted. It is a 4-of-4 gate on *sensitivity*, not on
*vigilance*. Defect 2 is the strongest evidence, because I caught it from the
contradiction inside a single line ("declared … always a fitted weight") rather than by
hunting for a flipped word.

---

## 2. Coverage — 18 of 45 pages

Full reads unless noted. Discursive pages first, per the brief.

- **`practice/` (4 of 4):** `traps.md`, `conventions.md`, `agent-contract.md`, `glossary.md`
- **`n-op/purpose/` (3 of 4):** `purpose-and-scope.md`, `product.md`,
  `architectural-principles.md` — *not read:* `library-landscape.md`
- **`oracle/laws/` (3 of 3):** `residual-definitions.md`, `generic-dynamics.md`,
  `coupling-structure.md` *(partial — lines 40–440 of 689)*
- **`oracle/certification/` (3 of 3):** `cert-obligations.md`, `out-of-scope.md`,
  `applicability-classifiers.md`
- **`oracle/state/` (2 of 5):** `unified-state.md`, `multiscale-state.md`
- **`oracle/compilation/` (1 of 3):** `physics-graph.md`
- **`oracle/registry/` (1 of 10):** `named-formulas.md`
- **`oracle/seams/` (1 of 2):** `residual-machinery.md`

**Not swept at all:** `n-op/build/*` (5 pages), most of `oracle/registry/*` (9),
`oracle/state/*` (3), `oracle/compilation/*` (2), `oracle/accuracy/*` (2),
`operator/*` (3), `interface/*` (1).

---

## 3. Findings — 18

Ordered by strength. Severity is my judgement of how hard the incompatibility is to talk
away.

---

### F1 — `oracle/certification/cert-obligations.md`, *The ten obligations*  · STRONG

> **line 61:** "The axis is the **second column**; it is not a separate mapping, and it is
> not restated anywhere else, because this list existed in three copies with three
> different second columns and a retag reached one of them."

> **line 65:** `| # | Obligation | Typeclass axis and check | Complexity |`
>
> **line 67:** `| 1 | symmetry equivariance | `Sampleable` × group action: … | `O(1)` per invariant |`

The typeclass axis is the **third** column. The second column is the obligation name. The
sentence asserting where the axis lives is two lines above the table that puts it
elsewhere, and the assertion is load-bearing — it is the argument for why the axis is not
duplicated anywhere else.

**Which is correct:** the table. The prose is a fossil from a version without the `#`
column — drop `#` and "second column" is right. Fix the prose.

---

### F2 — `oracle/laws/generic-dynamics.md`, *The Poisson and friction operators* vs *Generator structure is per tier*  · STRONG

> **line 92**, inside the `L` decomposition:
> `· Liouville–von Neumann on γ̂   (1/iℏ) [Ĥ_KS, ·]`

> **lines 140–142:** "**The `γ̂`-block of `L` is the Lie–Poisson bracket** — … giving
> `∂γ̂/∂t = −(i/ℏ)[Ĥ_KS, γ̂]` with `Ĥ_KS = δE/δγ̂`, written `[·, γ̂]` **not** the bare
> `[Ĥ_KS, ·]`."

The page writes the γ̂-block of `L` as `(1/iℏ) [Ĥ_KS, ·]` and then names that exact form
as the one it is *not*. Same page, same object, 50 lines apart.

**Which is correct:** the later passage, and it says why — the Lie–Poisson form satisfies
Jacobi by construction and delivers the degeneracy `L_γ̂·δS_el/δγ̂ = [δS_el/δγ̂, γ̂] = 0`,
which the bare fixed-operator form does not manifestly give. Line 92 is the summary block
where the fossil survived.

---

### F3 — `oracle/laws/coupling-structure.md`, *Composition*, one bullet  · STRONG

> **lines 88–89**, the `CouplingChannel` record:
> `kernel_extension : Optional<KernelExt>   -- the non-polynomial part;`
> `                                         --   present iff ¬polynomial_sufficient`

> **lines 151–152:** "The generator returns a `GeneratorOutput`, not a bare list, because
> **a channel's full coupling may be the polynomial basis *plus* a non-polynomial
> kernel**"

> **lines 270–273:** "When a channel carries a `kernel_extension`, its lowered kernel node
> adds into the same aggregator as its polynomial invariants: `full_coupling = Σ
> poly_invariants + kernel_extension(q, ω)`."

against, four lines later in the same bullet:

> **lines 274–276:** "A long-range mechanism is therefore split into **two channels** — a
> short-range polynomial one and a long-range kernel one — **rather than one channel that
> is partly polynomial and partly not**."

The record, the generator contract and the aggregator rule all commit to a single channel
carrying both parts. The bullet's own closing sentence says that arrangement never occurs.
Both cannot hold.

Reinforcing the first reading, the generator's well-formedness guards
(**lines 181–183**) exist *only* for a channel that is partly polynomial and partly not:
"`if ¬polynomial_sufficient(c) ∧ c.kernel_extension = None: error "partial coverage, no
kernel"`".

**Which is correct:** the machinery — three record fields and two guards outweigh one
sentence. But the Verdi–Giustino example in the same bullet supports the split reading, so
this is two live designs on one page, not a slip. It needs a decision, not a wording fix.

---

### F4 — `practice/conventions.md`, *Data files and generated files*  · STRONG

> **lines 120–121:** "**Data files are sources.** The registry manifest and the reference
> data under **[registry] and [reference-data]** hold the corpus's coefficients, formula
> rows, signatures and tags."

> **line 134:** "**Neither kind has a page id**, so both are **named by path rather than
> cited**."

The section cites the data files by id in its own second sentence, then asserts fourteen
lines later that they have no page id and are named by path rather than cited. The
practice on the page refutes the rule on the page.

**Which is correct:** line 121's usage. The passage demonstrates id-citation working;
line 134 denies a thing the same section does. (The owner page settles it the same way,
but that is a cross-page check and outside this pass.)

---

### F5 — `practice/conventions.md`, same section  · STRONG

> **line 118:** "**Three kinds of file** sit outside the journals, and each relates to
> prose differently."

The section then enumerates **two**, with bolded lead-ins — "**Data files are sources.**"
(line 120) and "**Generated files are outputs.**" (line 129) — and closes:

> **line 134:** "**Neither kind** has a page id, so **both** are named by path…"

"Neither" and "both" are two-item words. The heading is "Data files and generated files";
the frontmatter `owns` entry is "data and generated files". Everything says two except the
lead sentence, which says three.

**Which is correct:** genuinely underdetermined from the passage. Either "Three" is wrong,
or a third kind's paragraph was dropped and "Neither/both" is wrong. I lean to the second
— a third kind (the log) is plausible — but the passage alone cannot decide, and inventing
the missing paragraph would be the reconstruction hazard `traps.md` warns about.

---

### F6 — `practice/glossary.md`, *An index, not a second definition* vs *Tokens that need a qualifier*  · STRONG

> **lines 39–43:** "**No term is defined here.** **Every row below names a page**, and that
> page is where the term is specified. A glossary that carries its own one-line definition
> carries a second copy of something another page owns, and the two drift the moment either
> is edited… **A pointer cannot drift.**"

The page's second table carries one-line definitions and names no page:

> **line 177:** "| `graph` | **the physics graph, which is acyclic and whose topological
> order is its evaluation order** | … |"
>
> **line 182:** "| `kernel` | **the compiled artifact, which carries a file hash** | … |"
>
> **line 181:** "| `cell` | **the crystallographic unit cell** | … |"

Nine of the ten rows in that table cite no page at all (only the `GAP` row does). The
middle column is exactly "its own one-line definition" — the thing the page says it does
not carry, and the thing the "a pointer cannot drift" defence does not cover, because
these are not pointers.

**Which is correct:** the table has to exist — it is the overloaded-token register the
page `owns`. The absolute claim in the lead is what needs narrowing to the first table.

**Defence considered:** "below" could scope to the first table only, whose header is
literally "Specified in". But "**No term is defined here**" says *here*, not *in the table
below*, and the page knowingly hosts both artifacts.

---

### F7 — `oracle/laws/generic-dynamics.md`, *Generator structure is per tier*, one bullet  · STRONG

> **lines 146–153:** "**The `born-oppenheimer-surface` level is single-generator
> (Hamiltonian) at fixed entropy.** … at `born-oppenheimer-surface` the active generator is
> `E` alone (an **isothermal** single-generator contraction), and entropy production lives
> with the distribution and configurational variables."

The same bullet describes the same contraction as **at fixed entropy** (isentropic) and as
**isothermal**. Those are different constraints, and the page distinguishes them elsewhere
— the regimes table at **line 117** reads "Critical points of `E` at `T = 0` (or `F` at
`T > 0`)", i.e. `E`-driven and `F`-driven are the corpus's own isentropic/isothermal split.

**Which is correct:** "the active generator is `E` alone" is the operative clause, and it
means isentropic. "Isothermal" is the wrong word. Worth a physicist's confirmation, since
`S_vib(R,h)` being parametric in `(R,h)` complicates "fixed entropy" too.

---

### F8 — `oracle/seams/residual-machinery.md`, *The layered compute DAG*  · STRONG

> **lines 109–111:** "Layer 0 is the primitives, which have no dependencies; **each higher
> layer depends only on layers below it.** The index is **therefore a topological
> stratification**, and the runtime evaluates stratum by stratum."

> **line 113:** "**One cycle crosses the strata:** the operating-condition observables and
> the coupled-field balance are mutually dependent through the self-heating operating
> temperature."

Two lines apart. A topological stratification admits no cycle across strata; that is what
the word means. The universal claim and its counterexample sit in consecutive paragraphs,
and the "therefore" makes the first a conclusion the second refutes.

**Which is correct:** the cycle is real — the page goes on to say how it is closed. The
stratification sentence needs the exception in it.

**Note:** `physics-graph.md` resolves this cleanly for its own graph ("the recursion lives
*inside* one node and the edge set stays acyclic"). This page does not adopt that move; it
places the fixed-point iteration "at the layer barrier", i.e. between strata.

---

### F9 — `oracle/state/multiscale-state.md`, *The defect-population residual* vs *The unified three-tier residual contract*  · MEDIUM-HIGH

> **line 265:** `EOM/DefectPopulation[D,q,site] = …`
>
> **lines 278–280:** "**Axes** are `(DefectSpecies, ChargeState, SiteClass)`… There is one
> weightable `ResidualLeaf` **per species, charge and site**"

> **line 486:** "| Slow | defect concentrations | **(species, site)** | `EOM/DefectPopulation` | … |"

The summary table's Index column drops `ChargeState`, which the body states three times.
The same table's Macro row reads `(MeshCell, MacroField)`, matching line 467 exactly — so
the Index column *is* the axes, and the Slow row is short one.

**Which is correct:** the body. This is structurally the **same defect as the calibration
instance** — a summary enumeration silently dropping one member the body carries.

**Defence considered:** charge states are attached to species in the `DefectSpecies`
universe (line 124–128), so "(species, site)" could be shorthand. But the residual's own
index is `[D,q,site]`, and the key is built from the axes.

---

### F10 — `practice/agent-contract.md`, opening claim vs the schema block  · MEDIUM

> **lines 24–26:** "**The block at the end of this page is the schema the checker parses**
> — this document and the enforcement are the same artifact, **so they cannot disagree.**"

> **lines 158–160**, prose: "**History.** No changelogs, no strikethrough, no *"formerly"*,
> *"superseded"*, *"no longer"*, *"used to"*, *"retired"*, ***"closed on <date>"***."

> **lines 225–226**, the block: `history: [superseded, formerly, "no longer", "used to",
> retired, deprecated, legacy, "prior version", "earlier version", "struck through",
> "pre-book"]`

`"closed on <date>"` is forbidden by the prose and absent from the enforcement list. The
block also forbids five markers the prose never mentions. The document and the enforcement
do disagree, on the page that says they cannot.

**Which is correct:** the block is what runs, so the prose is currently unenforced. Either
add `"closed on <date>"` to the block or drop the "cannot disagree" claim — nothing derives
one list from the other, which is what makes the claim false as stated.

---

### F11 — `practice/agent-contract.md`, *Forbidden* vs the schema block  · MEDIUM

> **lines 158–160:** "**History.** No changelogs, no strikethrough, no *"formerly"*,
> *"superseded"*, *"no longer"*, *"used to"*, ***"retired"***… Pages state what is true, in
> the present tense, **and nothing about how they got that way**."
>
> **line 225:** `history: [… retired, …]`

> **line 237:** `retired-vocabularies:`

The page forbids the marker `retired` in prose *and* in its own machine-readable forbidden
list, then uses it as a block key twelve lines below that list. The block's content — a
map from old serials to current names — is also, by the page's own definition, "how they
got that way".

**Defence, and it is real:** the table has a present-tense function. `traps.md` requires
that "a label lifted from outside this corpus is translated, never copied", and this table
is the translator. Fenced blocks are also invisible to prose sweeps
(`conventions.md` line 55). So the substance is defensible; the *name* is the violation.
Rename to `inbound-vocabulary-translation` or similar and the contradiction disappears
without losing anything.

---

### F12 — `n-op/purpose/product.md`, *What an oracle-file contains* vs *The call*  · MEDIUM

> **lines 129–131:** "**The callable** — `Validate`, with **its gradient entry point**
> baked in at compile time. Consumers that never need gradients simply **never invoke that
> entry point**."

> **lines 179–182:** "**One entry point**, whose signature is [pino-bridge#validate]. It
> returns four things: … **an optional cotangent map populated only when gradients were
> requested**…"

Two API shapes. Either there is one entry point and gradients are a request flag on it, or
there is a separate gradient entry point that consumers invoke or don't. "One entry point"
and "never invoke that entry point" cannot both describe the same surface.

**Which is correct:** the single-entry-point/request-flag model. The page carries it twice
more — "populated only when gradients were **requested**" (line 181) and "**Call-time
subsetting.** The call's **request parameter**…" (line 215). Line 130 is the outlier.

---

### F13 — `oracle/laws/coupling-structure.md`, *The parameter axes*  · MEDIUM

> **lines 101–106:** "`SubDofTag` enumerates the internal labels a component carries: **γ̂
> carries `orbital`, `spin` and — where applicable — `sublattice` and `valley`; `h` carries
> `strain`; `A` carries `gauge`.** **Which `(component, sub-dof)` pairs are legal is not
> stated anywhere in this corpus**, and `make-coupling-channel` cannot validate a
> `StatePiece` without that table."

The clause immediately before states six legal pairs. The clause after says such pairs are
stated nowhere in the corpus. As written, the sentence refutes its own predecessor.

**Which is correct:** the substance is fine and the gap is genuinely open (it carries the
`sub-dof-pair-table` open question). This is a quantifier slip: what is missing is the
*complete* table — `R`, `P`, `Π_h`, `Z` are unassigned, and `charge` and `none` have no
owner. Narrow the claim and it is true.

---

### F14 — `practice/glossary.md`, *Tokens that need a qualifier*  · MEDIUM

> **line 171:** "**One sense is reserved.** Every other sense carries a qualifier, always."

> **line 183:** "| `source` | **nothing** — the token names two different fields on two
> records the same factory reads together | … |"
>
> **line 185:** "| `coverage-mask` | **nothing** — three unrelated masks multiply into one
> loss | … |"
>
> **line 186:** "| `GAP` | **nothing** — the missing-data marker is **`UNSEEDED`** | … |"

Three of the ten rows reserve no sense at all, under a column headed "Reserved sense" and a
rule that says one sense is reserved.

**Which is correct:** the table. The three-way outcome (reserve one / reserve none) is the
real policy; the rule sentence describes only the first. The consequence clause ("Every
other sense carries a qualifier") survives either way — it is the premise that is too
narrow.

---

### F15 — `oracle/laws/coupling-structure.md`, *Cert hooks*  · MEDIUM

> **line 295:** "- **Positivity — antisymmetry of `L`, positive-semidefiniteness of `M`.**"

> **lines 308–311:** "The cert-obligation indices are fixed in
> [cert-obligations#the-ten-obligations]: equivariance is obligation 1, **antisymmetry of
> `L` is obligation 5 (conservation)**, positive-semidefiniteness of `M` is obligation 2
> (positivity)."

The bullet is headed *Positivity* and contains antisymmetry of `L`, which the section's own
closing sentence assigns to obligation 5, **conservation**. A heading its own section
contradicts.

**Which is correct:** the closing sentence. The bullet merges two distinct obligations
under the label of one of them; the owner page keeps them in separate bullets.

---

### F16 — `oracle/compilation/physics-graph.md`, *The one data structure* vs *Why it is the data structure*  · MEDIUM

> **lines 59–62:** "Every other *thing* in the oracle … is a kind of node, a labelled
> subset of nodes, or **a per-stage sidecar indexed by node id**."

> **lines 111–113:** "Per-node decorations … live in per-stage sidecars **instead of on the
> node**"

> **lines 254–256:** "**Closure.** Every closed vocabulary is either a typing rule for a
> node kind, a labelled subset of nodes, or **an annotation field on a node**. Nothing in
> the oracle lives outside the graph."

The same trichotomy appears twice with different third members. The page then states
explicitly that those two members are *not* the same thing — sidecars live "instead of on
the node", are "**not part of a node's identity, not hash-consed, and do not survive their
last consumer**" (line 204).

**Which is correct:** line 61's version. Sidecars are the real third category, and the
Closure bullet's "annotation field on a node" contradicts the page's own insistence that
they are not on the node.

---

### F17 — `oracle/registry/named-formulas.md`, *What the registry is*  · MEDIUM-LOW

> **lines 56–59:** "**Counts over the manifest belong to the manifest.** This page states
> the rules a row obeys and names individual rows where a rule needs an example. **It does
> not tally them.** A tally written in prose beside the table it counts is a second copy
> with no mechanism holding it to the first."

> **line 61:** "**Two rows** are **architectural markers** rather than formulas…"

Two lines later, a count over the manifest. It is also restated in the band table at
**line 270**: "| 103–104 | the two architectural markers |" — a second copy of the second
copy, and precisely the failure the rule describes.

**Defence considered:** the rule permits "names individual rows where a rule needs an
example", and both markers are named individually. But "**Two** rows are architectural
markers" is a closed claim about manifest membership that no reader can check against the
page, which is what the rule exists to prevent.

---

### F18 — `oracle/laws/residual-definitions.md`, *The 19 residual categories*  · MEDIUM

> **line 68:** "Residuals fall into **19 residual categories**, **identified by name and
> never by ordinal**"

> **line 198:** "**Categories 16 and 17** stay disjoint because they consume type-distinct
> inputs — snapshot versus snapshot-plus-environment"

The page forbids identifying categories by ordinal and then does exactly that. Same section,
same page.

**Which is correct:** the rule, and the corpus argues for it at length elsewhere — ordinals
repoint silently when an entry is inserted. Fix: "`Static/Snapshot` and
`Static/Thermodynamic` stay disjoint because…". (The 1–17 numbering of the list itself is
presentational and can stay; the prose reference is what breaks.)

---

## 4. Verdict on the hypothesis

**The estimate looks low — substantially.**

Eighteen findings across eighteen pages read. Even discarding the ten I rated MEDIUM or
below, the eight STRONG findings alone come to **0.44 per page**, and those eight are
flat: a table's third column called the second, an operator written in the exact form the
page says it is not, a bullet whose machinery and whose conclusion describe opposite
designs, a section that cites data files by id and then says data files are not cited.

Extrapolating the full rate over the 27 unread pages would put the corpus somewhere near
**40 adjacent contradictions**, against ~140 defects that twelve agents found across *all*
classes. Extrapolating only the strong ones still puts it near 20. Either number makes this
the largest single class in the corpus, and the twelve-agent sweep surfaced almost none of
it.

**Three things sharpen the verdict rather than soften it.**

1. **The rate will not hold uniformly.** I read the most discursive pages first, as
   instructed. Registry and table-heavy pages (`oracle/registry/*`, 9 unread) have less
   prose to contradict itself, so the true corpus-wide count is likely below a linear
   extrapolation. The `practice/` and `laws/` sections are where this class concentrates —
   and those are the pages every other page depends on.

2. **The corpus's own authors catch some of these, which proves the class is real and
   confirms the checkers cannot see it.** Two adjacent self-contradictions are already
   written up in frontmatter `open-questions`: `cert-obligations.md`'s obligation 9 ("This
   page contradicts itself about it: the obligation reads `surrogate`, its tolerance-ledger
   row reads `relaxation validity`") and `residual-machinery.md`'s `adjoint-cert` having
   four cases where the page's own rule needs a fifth. Both were found by a human or agent
   reading, never by a gate. Every finding above has valid links, a resolving citation and a
   single owner — the structural checkers pass all eighteen.

3. **The blind spot is exactly where the calibration said it was.** F2 and F7 are prose
   surrounding an equation. F1, F9 and the calibration instance are prose against an
   adjacent table or enumeration. F3, F4 and F16 are a rule against its own machinery. Not
   one of the eighteen required arithmetic, a second file, or a citation check — which is
   why eleven passes that audit "structure and sign, not magnitudes" walked past them.

**One caution on my own instrument.** My positive control was self-planted; the blind
control I requested never arrived. A 4-of-4 self-plant measures sensitivity to a shape I
was already looking for. It does **not** establish that I would find a contradiction whose
shape I had not anticipated, and it establishes nothing about the 27 pages I did not read.
This is a discovery result, not a certification: it says the class is dense, not that I
found all of it.

---

## 5. Near-findings rejected, with reasons

A passage that reads awkwardly is not a contradiction. These were considered and dismissed.

| Page · passage | Why rejected |
|---|---|
| `residual-definitions` — "Facets are provenance, **not** weighting axes" vs "Weighting … keyed by category participation gates alone" | Holds: gates are per-**category**, weights are per-**residual**. The distinction is real and the page keeps it. |
| `residual-definitions` — "`CategoryTag` … carries semantic weight **nowhere else**" vs the curriculum gate keyed on `CategoryTag` | Arguable, but "nowhere else" reads as scoped to `ResidualKey` identity, which is the page's subject. |
| `residual-definitions` — contributions "**unbounded**", generators "**countable**" | Weak word choice, not incompatibility. Both can hold simultaneously; the contrast wanted is *finite*. |
| `residual-definitions` — dynamical stability in both `Positivity` (10) and `Static/Snapshot` (16) | Real overlap, but the page makes no global disjointness claim — only 16-against-17. |
| `traps` — "lands on the **right number** for the wrong material" vs "*Breaks:* the anchor" | Resolves: the room-temperature numbers collide, the **high-temperature** ones do not, and the anchor cited is high-temperature. |
| `traps` — `enforced` = "stated on the **page** named" vs one entry pointing at `tools/check_the_checker.py` | "Page" read loosely. Definitional stretch, not a contradiction. |
| `traps` — "**no checker** can separate the two by shape" vs "put it in backticks so a search … does not return the other" | Different levels: the token's own characters vs added context markers. |
| `purpose-and-scope` — "Three things hold under **either reading**", item 1 being "no time-evolution verb **today**" | "Today"/"now" hedge it. The item is about the current spec, not about how the question resolves. Close, but survives. |
| `purpose-and-scope` — "disciplined by it **at every step**" vs "why it cannot come first" | Reconcilable as per-step *within* the attached stage vs stage ordering. Settling it needs `training-stages` — cross-page. |
| `product` — "**The product is the oracle**" vs "The product has **two parts**" | The page does the reconciling itself at line 146: "'The oracle' as a general object is the *compiler*; each file is the oracle *for one instance*." |
| `generic-dynamics` — `E[x]` written as a `+`-joined sum vs "`E[x]` is **not a flat simultaneous sum**" | Disclosed. The page states the hazard and explains the level-conditional activation. Presentational, not contradictory. |
| `applicability-classifiers` — "**Illustrative.**" vs "this is **the collected vocabulary** those fields draw on" | Resolves across columns: illustrative in the *property* column, complete in the *predicate* column. |
| `cert-obligations` — "Cert is a **first-class** deliverable: [4 things]" vs three of them "are **non-load-bearing**" | Deliverable ≠ load-bearing for certifying a prediction. The page draws the distinction deliberately. |
| `cert-obligations` — "**Four compose-time refusals**" including one that "**trips obligation 9**" per query | The admissibility test ("only if external anchor data back its declared validity domain") is a compose-time field comparison; the query trip is additional. |
| `coupling-structure` — guard `if … c.target ∈ {Scalar, PSDSymmForm, AntisymmForm}` when the type admits exactly those three | Vacuous condition — dead code implying a fourth target once existed. Not two claims that cannot both be true. |
| `multiscale-state` — "the two directions have **different owners**" vs "The rate law in **both** directions is the slow tier's" | Muddy but survivable: owner of the *mechanism* differs, owner of the *rate law* does not. |
| `unified-state` — "**external** EM vector potential" vs "These seven are the **irreducible degrees of freedom**" | Genuine tension, but settling it needs `generic-dynamics`'s Maxwell block and `EOM/A` — cross-page, outside this pass. |
| `residual-machinery` — row 122 tagged `fixpoint-adjoint` while "there is no fixed point", against "A row that is not a converged fixed point **cannot** be retagged into `fixpoint-adjoint`" | **Declared**, with the `dormant-row-cert-encoding` open question attached. Known, not undiscovered. |
| `cert-obligations` — obligation 9 `surrogate` vs `relaxation validity` | **Declared** in frontmatter, in those words. Known. |

---

## 6. By-catch — outside this class, not counted

Surfaced by reading but **cross-page**, so out of scope by the brief. Recorded because the
class that owns them may not have swept these pairings. **Unverified** — each needs the
owning auditor to confirm.

- `product.md` line 202 / `architectural-principles.md` line 67 — refusal "is not in the
  compiled kernel… It is **never *raised***" — against `out-of-scope.md` line 123:
  "`predict` **raises** `out-of-scope` with a witness for any of the above."
- `out-of-scope.md` uses a verb `predict`; `product.md` line 252 says "**Three verbs**,
  minimal by principle" — `compile`, `inspect`, `validate`.
- `architectural-principles.md` lines 74–76 — schema, freeze fixture, tamper tripwire and
  high-precision oracle "**together carry roughly the weight of any one level of the
  system**" — against `cert-obligations.md` line 54: the same three "are checks *on* the
  schema, and are **non-load-bearing**".
- Jacobi verification is owned by neither page: `generic-dynamics.md` line 166 calls it "a
  **cert-side numerical check**"; `cert-obligations.md` line 108 says "**Jacobi status is
  [generic-dynamics]'s**" and lists no Jacobi obligation among the ten.
- `physics-graph.md` line 246 — `Import` produces "**certification-only** `ResidualLeaf`
  nodes" — against `product.md` lines 220–224, where `Import` slots are read by consumers
  and the design loop sinks gradients through them.
- `multiscale-state.md` line 337 cites `[residual-definitions#constraint-categories]` for
  the `Conservation` residual; `Conservation` is category 9, under
  `#structural-categories`. A resolving anchor pointing at the wrong content — the
  "dangling promise" `traps.md` line 140 names.
- `conventions.md` line 46 — "**American English** everywhere" — against `centralised`
  (`agent-contract` 163), `realised`/`generalising` (`residual-definitions` 58, 105),
  `homogenised` (`unified-state` 61), `Wannier-centre` (`out-of-scope` 86), and
  `aluminium` (`out-of-scope`, `applicability-classifiers`) against `aluminum` (`traps`).
  The last is a same-corpus split on one material's name.
- `product.md` line 100 names the principle "***agnostic by purity***";
  `architectural-principles.md` line 21 calls it "Numerics-agnostic at the seam, committed
  within". No page carries the first name.
- `cert-obligations.md` line 129 — "**[conventions] owns that namespace rule**".
  `conventions.md`'s `owns` lists page style, count phrasing, verdict discipline, and data
  and generated files. No namespace rule.
- `residual-machinery.md` line 67 — `layer : 0..6` uses the token `layer` unqualified for a
  compute-DAG stratum; `glossary.md` line 179 reserves `layer` for "the physical or
  epitaxial layer, which is real physics".

---

## 7. Boundary compliance

Read-only throughout. All planting and all mutated reads happened in a scratch copy under
`/tmp/claude-1000/…/scratchpad/`. Every quotation above was re-verified against the real
repository before being written down.

```
$ git status --porcelain journals/ data/
(no output)
```

---

## Appendix A — provenance of every quotation

Added after the findings were written, in answer to a direct question from the principal
about which corpus this report describes. **No finding, severity or verdict was changed.**

### A1. Which tree the findings come from

I read from two locations, and both are accounted for.

**Real tree — `/home/javier/Projects/Physics/Programs/n-Op/journals/` (12 pages):**
`residual-definitions`, `traps`, `conventions`, `agent-contract`, `glossary`,
`purpose-and-scope`, `product`, `architectural-principles`, `out-of-scope`,
`applicability-classifiers`, `cert-obligations`, `generic-dynamics`.

**My own scratch working copy — `…/scratchpad/self/journals/` (6 pages):**
`unified-state`, `physics-graph`, `residual-machinery`, `named-formulas`,
`multiscale-state`, `coupling-structure`. This copy was made by me with `cp -r` from the
real tree at the start of the run and then mutated only by my own 4-line plant script
(§1b). Findings drawn from it: **F3, F8, F9, F13, F15, F16, F17**.

### A2. The scratch copy differs from the real tree in exactly 4 lines

```
$ diff -r journals/ scratchpad/self/journals/
coupling-structure.md 274:  "two channels"      → "three channels"
named-formulas.md     317:  "factor of two"     → "factor of three"
residual-machinery.md  81:  "never a fitted"    → "always a fitted"
multiscale-state.md    87:  "seven-tuple"       → "eight-tuple"
```

Four differing line-pairs, no others. All four are my plants, all four were identified in
§1b, and none is used as a finding. **No finding rests on mutated text.**

### A3. Line numbers are not offset

Every plant was an in-line substitution. Line counts are byte-identical between the two
trees for all six pages (689/500/337/301/84/275). Line numbers cited in this report are
therefore valid against the real tree.

### A4. Every quoted half re-verified against the real tree

All 20 quotation pairs — both halves of every finding plus the calibration instance —
were re-checked by substring match against the real files with line wrapping normalised,
because several quotations span a line break.

**20 of 20 verified. 0 failures.**

### A5. The blind control, and how it was destroyed

`blind-calibrator` did plant, into `…/scratchpad/blind/journals/` — a directory I created
and **never read**. Its plants touch `mvp-system.md`, `product.md`,
`canonical-vocabularies.md` and `agent-contract.md`, and unlike mine they change line
counts, so that copy is not line-comparable with the real tree.

Answering A1–A2 required diffing my scratchpad against the real tree, which displayed the
blind plants. **The blind control is now burned and cannot be run.** That was the right
trade — establishing which corpus this report describes mattered more than preserving a
control — but it means the 4-of-4 in §1b remains the only calibration behind this report,
with the sensitivity-not-vigilance caveat stated there still fully in force.

Two of those blind plants sit in `product.md` and `agent-contract.md`, both of which I
read **from the real tree**. There is no path by which they could have reached a finding.
