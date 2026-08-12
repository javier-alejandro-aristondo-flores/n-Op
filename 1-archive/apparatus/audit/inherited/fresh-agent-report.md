# Fresh-agent acceptance test

Read-only pass over `journals/` + `generated/corpus.json`, using only `journals/practice/agent-contract.md`
as the entry contract. No git history, no `journal/`, no `physics/`, no `informed-operator/`,
no `restructure/`.

**Headline: the navigation works.** Four of five tasks resolved in one index query plus one
file. The defects I found are real but narrow, and all four sit in the same blind spot:
*things the checker cannot see because they are propositions, not links.*

---

## Files opened per task

Counting `generated/corpus.json` as one open; jq queries against it are not separate opens.

| Task | Index queries | Pages opened | Wrong guesses |
|---|---|---|---|
| 1 · seven state components | 1 | **1** (`unified-state`) | 0 |
| 2 · when the oracle attaches | 1 | **1** (`training-stages`) | 0 |
| 3 · where 5.7 goes | 1 | **3** (`reference-battery`, `accuracy-ledger`, `conventions`) | 0 |
| 4 · environment record fields | 1 | **1** (`crystal-inputs`) — and the index alone already answered it | 0 |
| 5 · dangling-reference sweep | — | whole corpus by script + 2 by hand (`glossary`, `formula-registry`) | — |

Nine of forty-five pages opened by hand across the whole exercise. The `topics` map answered
every "who owns this?" question on the first try, including one where the topic key was
literally the phrase in my question (`where the oracle attaches`).

---

## 1 · The seven components of the state

`journals/oracle/state/unified-state.md` — heading **"The seven slots"** (anchor `slots`).

```
x(t) = ( h,    cell vectors            ∈ GL⁺(3,ℝ)
         R_I,  ion positions           ∈ ℝ^{3N}
         P_I,  ion momenta             ∈ ℝ^{3N}
         Π_h,  cell momentum (Parrinello–Rahman) ∈ ℝ^{3×3}
         Z_I,  species labels (immutable), discrete
         γ̂,    one-body density matrix, 2×2 Pauli-spinor operator on (r,r';t)
         A )   external EM vector potential ∈ ℝ³ field A(r,t)
```

Carried in Weyl gauge `A₀ ≡ 0`, transverse `∇·A = 0`. Route: `topics["state seven-tuple"]
→ unified-state`, then `anchors.slots`. One hop.

## 2 · When the oracle attaches, and why that order

`journals/operator/training/training-stages.md` — **"The stage ordering"** (`stage-ordering`)
and **"Why this order"** (`why-this-order`).

It attaches at **stage 2 of 3**, the *informed epoch*: after supervised epochs on
density-functional-theory data, before inference. Stage 3 runs alone and calls no oracle.

The stated reason: **"The oracle refines. It does not search."** A residual is a *local*
signal — it says how far a supplied candidate sits from each law and which direction reduces
that. Over a large space there is nothing for such a signal to point toward. The supervised
stage buys the small space that makes it useful. Hence: "Running the informed epoch first
would not work, and running it forever would not help."

Two topic keys point here — `training stage ordering` and `where the oracle attaches` — both
owned by this page. No hunting.

## 3 · Where the static permittivity of diamond, 5.7, goes

**The corpus already knows this fact and is waiting for it.** It is carried as open question
`diamond-static-permittivity-unseeded`, which names the value, its uncertainty, its consumer,
and both admissible ways to close it. This was the single most impressive result of the test.

**Exact page and heading:**
`journals/oracle/accuracy/accuracy-ledger.md` → **"What the seeded values rest on"**
(anchor `seed-provenance`), in the table **"UNSEEDED — no source found"**, row
`dielectric-static`. Landing a source moves that row up into the **"Resolved to named
literature"** table on the same heading.

**The value itself does not go in a page.** `conventions.md` → "Data files and generated
files" is explicit: data files are *sources*, a page that states a value is *quoting* it, and
the citation of record is the `Source` column of
`physics/library/cert/reference-data/material-constants.csv`. `accuracy-ledger` repeats the
pointer twice. So: citation into the CSV, provenance status onto `seed-provenance`.

**What else must be touched — the corpus told me all of this, I guessed none of it:**

1. `accuracy-ledger` frontmatter — delete the `diamond-static-permittivity-unseeded`
   open-question entry.
2. **"Per-observable accuracy regimes"**, regime row 31 (`schottky_barrier φ_B`) — ends
   "**and that permittivity is UNSEEDED**, `diamond-static-permittivity-unseeded`". That
   clause dies. The row is the value's only consumer: image-force lowering
   `Δφ=√(qE/4πε_sε₀)`, 0.16 eV at 10⁶ V/cm and 0.50 eV at 10⁷.
3. **"MVP design-grade targets"** — "five of those anchors are in the seeded-value provenance
   section below, **two of them UNSEEDED**" becomes one.
4. **A physics trap the corpus flags and I would otherwise have walked into.** If closing by
   derivation from the refractive index, the row states no frequency window and the
   derivation only works at one: **infrared gives 5.66, visible gives 5.84.** Landing "5.7"
   without naming the window is not a close.
5. `log/timeline.md` (repo root, exists) — per `agent-contract`, the date · finding ·
   evidence · attribution · what-it-superseded entry. Pages carry the resolution in present
   tense; the story that it was ever open goes only here.

**The one gap in task 3:** there is no page that owns *the open-question closure procedure*.
I assembled the five steps above from four pages. `conventions.md` owns "data and generated
files" and `agent-contract` owns "fact placement", but nothing owns "what you do when an
UNSEEDED row gets seeded". For a corpus with 51 open questions, that is the most-repeated
workflow in it and it is unwritten. See recommendation R4.

## 4 · The environment record's fields and units

**The corpus cannot fully tell me, it knows it cannot, and it says so twice.** The index
alone answered this — I opened `crystal-inputs` only to confirm.

`journals/oracle/state/crystal-inputs.md` → **"The environment record"** (`environment`)
names **13 fields**. **Five carry a declared type and unit:**

| Field | Type and unit |
|---|---|
| `radiation_flux` | `ParticleFlux` (cm⁻²s⁻¹) |
| `radiation_dose` | `Fluence` (cm⁻²) |
| `displacement_threshold` | `Energy` (eV), per host |
| `vibration_spectrum` | `PSD`, amplitude vs frequency, 100 Hz – 10 kHz |
| `p_O2` | `Pressure` (Pa) — a specialization of the pressure slot, not an independent field |

The other eight — `temperature`, `pressure`, `chemical_potentials`,
`applied_electric_field`, `applied_magnetic_field`, `applied_stress`,
`temperature_gradient`, `carrier_injection` — read **`UNSEEDED`** in the type column, with
the reason stated inline: recoverable as *names* from signatures and prose, but types and
units stated nowhere, "which is why they read `UNSEEDED` rather than carrying a plausible
guess."

**The gap is recorded from both sides**, which is what made it a one-hop answer:

- `environment-schema` on `crystal-inputs#environment` — field set not closed, no schema
  version, so adding a field silently changes which formulas apply to every existing
  composition.
- `environment-schema-at-the-seam` on `learnable-structure-contract#conditioning-inputs` —
  the seam obliges the operator to accept the record as typed channels, so the obligation
  "names a channel whose contents cannot be checked."

Two adjacent open questions matter for anyone landing this: `environment-structural-partition`
(only `temperature` is classified) and `crystal-type` (`Crystal` is used in every applicability
signature in the corpus and defined nowhere).

This is the best behavior I saw. A typed table with eight honest holes beats a complete table
with eight guesses, and the holes are individually addressable.

---

## 5 · Does the corpus reference anything that does not exist?

### How I looked

Wrote an independent checker from the `agent-contract` schema block alone
(`scratchpad/check.py`, ~230 lines) — I did not read or run `tools/check_structure.py`, so
this is a second opinion rather than a re-run. It parses all 45 pages, and checks: frontmatter
schema and forbidden keys, `id`-equals-stem, `owns` non-empty / excludes-own-id /
unique-across-corpus, anchors-resolve-to-real-headings, every `[page]` and `[page#anchor]`
citation resolves, cited-id-in-`depends-on`, `depends-on` resolves, forbidden history markers,
retired serial vocabularies, table arity with escaped pipes, section-ordinal / line-number /
bare-path citations, referenced filesystem paths, orphan pages, and full cross-check of
`generated/corpus.json` against the pages it claims to summarize.

**Calibration, per `conventions.md` "Calibrate before certifying":**

```
citations parsed          : 788      anchors declared : 424
  of which anchored       : 617      headings found   : 478
owns topics               : 272      depends-on edges : 435
open questions            : 51       tables scanned   : 72
pages with 0 anchors parsed : []     (i.e. the parser did not silently no-op)
negative control (2 planted fakes): ['[no-such-page]', '[unified-state#no-such-anchor]'] — both caught
```

### What I found

**FINDING 1 — Seven dangling pointers in the glossary. The only real defect class.**

`journals/practice/glossary.md` → "Where a name is specified" promises: *"Every row below
names a page, and that page is where the term is specified."* For seven of fifty backticked
rows, **the name does not appear on the page named.** Two severities:

*Names that exist nowhere in the corpus except the glossary row itself:*

| Name | Glossary says | Reality |
|---|---|---|
| `StateTier` | `multiscale-state` | appears in no page. Glossary only. |
| `EvidenceDAG` | `representation-substrate` | appears in no page. That page has the topic "evidence attestation DAG" and the type `EvidenceOps`, but no `EvidenceDAG`. |

*Names that exist, but on a different page than the glossary says:*

| Name | Glossary says | Actually in |
|---|---|---|
| `ResidualVector` | `residual-definitions` | `compose-time-pipeline` |
| `CertEvidence` | `cert-obligations` | `compose-time-pipeline`, `pino-bridge` |
| `RoaringCoverageMask` | `pino-bridge` | `cert-obligations`, `multiscale-state` |
| `CrystalSymmetryGroup` | `canonical-vocabularies` | `representation-substrate`, `coupling-structure` |
| `IrrepLabel` | `canonical-vocabularies` | `representation-substrate` |

**Why the checker cannot catch this, and why that generalizes.** Every one of these rows
contains a *valid* citation — `[multiscale-state]` resolves, is in `depends-on`, and passes
every rule in the schema block. The rule set validates **the pointer**. The glossary's claim
is a **proposition about the target's contents**, and nothing checks propositions. This is the
structural blind spot, and the glossary is the worst place to have it: it exists precisely
because — in its own words — "the topic map does not answer here." The one index built for
name lookup is the one index nothing verifies.

Cheap fix: for any glossary row whose left cell is a single backticked token, assert the token
appears in the cited page's body. That is a five-line check and it catches all seven.

**FINDING 2 — A path that does not exist, on the page that owns it.**

`journals/oracle/registry/formula-registry.md:32` — "one row per formula, at
`data/registry-manifest.csv`". **No such path.** The file is at
`physics/library/formulas/registry-manifest.csv`, which is what both
`accuracy-ledger.md:85` and `conventions.md:120` say.

The owner page has the wrong path and two non-owner pages have the right one. This is the
"never state a fact in two pages" rule failing in the direction the rule was written to
prevent — and it is invisible to the checker because `conventions.md` deliberately puts paths
in backticks *to keep them out of the citation sweep*. Nothing then checks them. A path in
backticks is currently write-only.

Also absent, but legitimately so — a planned artifact, not a defect:
`physics/library/cert/reference-data/cache.sqlite` (its population path is the declared open
question `csv-to-sqlite-path`).

**FINDING 3 — Six `depends-on` edges that are never cited.**

`compose-time-pipeline → canonical-vocabularies`, `glossary → conventions`,
`observable-bundles → named-formulas`, `property-templates → named-formulas`,
`representation-substrate → typeclass-alphabet`, `residual-loss-design → boundary`.

The contract checks that every citation is in `depends-on`; it does not check the converse.
These six edges are emitted into `referenced_by` in `corpus.json`, so the reverse-edge index
overstates coupling by six. Minor, but `referenced_by` is exactly what someone uses to judge
blast radius before an edit.

**FINDING 4 — `generated/corpus.json` has no staleness marker, and it went stale under me.**

Top-level keys are `open_questions`, `pages`, `topics`. No timestamp, no version, no content
hash. Mid-session the index silently fell behind the pages: `pino-bridge` gained four owned
topics — `the evolver hand-off`, `residual obligation map`, `encoding validity domain`,
`steppable-form manifest fields` — plus one open question and four `depends-on` edges, none of
which were in the index I had been told to use as my primary entry point.

The proximate cause here is benign (other builders are writing; corpus.json regenerated 06:53,
`pino-bridge.md` edited 06:55). **The structural problem is not.** A reader whose first move is
`topics["the evolver hand-off"]` gets "no page owns this", and `glossary.md` instructs them to
read that as *a finding*: "If a name is missing from both, no page claims it. That is a
finding, not a lookup failure." A stale index therefore does not fail loudly — it manufactures
false findings, with the corpus's own blessing. Emitting a `generated_at` timestamp, or a hash
of the page set, would let a reader tell.

**FINDING 5 — 25 type names used on two or more pages, absent from the glossary.**

Not undefined — each is specified on some page — but not reachable by name lookup. Highest
traffic: `ProvenanceLedger` (4 pages, and it is the record the whole coefficient-provenance
contract turns on), `MethodInvoke` (4), `StateComponent` (5), `AntisymmForm` (3),
`DiscreteStructure` (3), `PeriodicityStructure`, `SiteDecoration`, `PSDSymmForm`,
`ResponseKernel`, and the `…Of` property-template family (`SpectrumOf`, `AlgebraicOf`,
`ClassifyOf`, `KineticEvolutionOf`, `SymmetryAdaptedHamiltonianOf`, and seven more).

Note `StateComponent`: the glossary has a row "state component → `[unified-state]`", but
`unified-state` contains the string `StateComponent` zero times; the type is used in
`physics-graph`, `representation-substrate`, `multiscale-state` and `coupling-structure`. The
prose noun and the type name have been conflated.

### What I tried to break and could not

I want to be explicit about this, because a clean verdict is only worth the attempts behind it.

- **Zero dangling citations.** 788 citations, 617 of them anchored, across 45 pages —
  every `[page]` resolves, every `[page#anchor]` resolves to a *declared* anchor, and every
  declared anchor matches an actual heading string. Not one failure. The negative control
  confirms the check fires. Against the previous corpus's reported "33 of 58 pages contained
  ordinals that silently failed to resolve", this is the rebuild's clearest win.
- **`owns` uniqueness.** 272 topics, zero collisions, zero pages owning their own id, zero
  empty `owns`. The anti-duplication mechanism is actually holding.
- **Table arity.** 72 tables, zero row/header mismatches. The escaped-pipe discipline is real,
  including in tables full of `\|`-bearing notation.
- **Frontmatter.** Zero missing required keys, zero forbidden keys, zero `id`/filename
  mismatches, zero unquoted titles across 45 pages.
- **Registry row ordinals — I expected this to be the kill shot and it was pre-empted.** The
  corpus cites "registry row 120" and similar 42 times, into an external CSV. That is
  structurally the `§4.1` failure the contract bans. But `formula-registry.md:37` states the
  row number is "a **stable identifier**. It orders nothing and is never reused", and
  `traps.md:152` applies the identical reasoning to trap numbers ("a numbered register
  renumbers whenever an entry is inserted"). The distinction between a *position* and an *id*
  was drawn deliberately. I was wrong.
- **`log/timeline.md` — I assumed it was missing and it is not.** `agent-contract` cites it as
  the sole home of history; it is absent from `journals/` and I had it written down as a
  dangling reference. It exists at repo root. My error, from assuming the contract's paths
  were journal-relative.
- **Forbidden history markers.** Every hit (18) is inside `agent-contract`, which quotes them
  as its own schema. Same for the sole `~~`, `## Changelog`, `§4.1` and `file.md:42` hits —
  all are the contract quoting what it forbids. No page carries a changelog, a strikethrough,
  or a "formerly".
- **Retired serial vocabularies.** Seven hits, all legitimate: `traps.md` and `glossary.md`
  documenting the collisions (`D1`–`D5` as *wurtzite deformation potentials*, `GAP` as three
  unrelated external objects), plus `C2/m` — a real space group, not a retired cluster tag.
  The spell-it-out rule is holding.

---

## Where I had to hunt

Four places, in descending order of cost. None cost more than two hops.

1. **`generated/corpus.json` is not under `journals/`.** The brief said the corpus "lives at
   `journals/`" with "a machine-readable index at `generated/corpus.json`", and I looked for
   `journals/generated/corpus.json`. It is at repo root. Thirty seconds, but it was my very
   first action and nothing in `agent-contract` states the path either — the contract
   references `generated/corpus.json` five times without ever saying it is repo-relative.

2. **`agent-contract`'s "shape of the base" points a new reader straight at the directories
   they must not read.** The diagram is:

   ```
   n-Op
   ├── physics/            the oracle library
   ├── informed-operator/  the operator library
   └── interface/          the loops library
   ```

   Those are code/library directories; the *journals* are `oracle/`, `operator/`,
   `interface/`. The `libraries:` map in the schema block does state the correspondence
   (`oracle: physics`), but it is 160 lines below the diagram. Had I not been told to avoid
   them, my second action would have been `ls physics/` — and in this tree that is the
   previous corpus. **Recommendation R1:** put the journal-name → library-name mapping in the
   diagram itself.

3. **Task 3's "what else to touch" required assembling four pages.** No single page owns the
   close-an-open-question workflow. The pieces are all there and all correct — they are just
   not collected, and I only found the `log/timeline.md` step because I had read
   `agent-contract` end to end for a different reason.

4. **Deciding between `reference-battery` and `accuracy-ledger` for task 3.** The topics map
   gave me both (`reference-row schema` / `reference-data contents` vs `seeded-value
   provenance status`), and I could not tell from the topic names alone which held the
   *diamond permittivity provenance*. I opened both. In fairness the answer was that I needed
   both — they own different halves — but the topic names did not signal that.

## What I expected to exist and did not find

- **A staleness marker on `generated/corpus.json`.** I reached for `generated_at` the moment I
  saw drift and there is no such field. See Finding 4.
- **A page owning the open-question lifecycle.** With 51 open questions carried in frontmatter
  and a whole vocabulary (`UNSEEDED`) built around unresolved provenance, I expected
  `practice/` to own "how a question closes". `conventions.md` owns page style, count phrasing,
  verdict discipline and data files; `agent-contract` owns placement. Neither owns closure.
- **A reverse index by *name* that is checked.** The glossary is that index, and it is the one
  thing in the corpus with no verification behind it (Finding 1).
- **Anything telling me the field types in task 4.** Correctly absent, correctly *declared*
  absent — the best possible version of not finding something.
- **A README or entry page in `journals/`.** There is no `journals/index.md` or equivalent; the
  entry point is `practice/agent-contract.md`, which I only knew from the brief. A reader
  who lands in the directory cold has five sibling directories and no marked front door.
  Minor, since the contract is genuinely the right front door once you know.

## If I had to add a fact tomorrow, would I know where to put it?

**Yes, with high confidence, for any fact that has a name.** The procedure in
`agent-contract` → "Where a fact goes" is four steps, and step 2 — *find the owner in
`generated/corpus.json`, the `topics` map answers in one hop* — worked on every single
lookup I attempted today, five for five, including one where I did not know the corpus's
term for the thing I wanted. 272 topics with zero ownership collisions means the map is
not just present but sound. That is the load-bearing claim of the whole rebuild and it
holds.

**Concretely confident about:**

- Adding a *value* — it goes in the CSV under `physics/library/`, never in a page;
  `conventions.md` → "Data files and generated files" is unambiguous, and
  `accuracy-ledger` re-points at it twice.
- Adding a *topic nobody owns* — step 4 covers it: pick the page that should own it, add to
  `owns`. The uniqueness invariant means I will be told immediately if I am wrong.
- Adding a *citation* — one syntax, both halves checked, and the reverse edges are emitted
  rather than authored so I cannot corrupt them.
- Knowing what NOT to write — the "Forbidden" section is short and absolute, and the
  present-tense rule removes the hardest judgment call (whether to narrate a change).

**Where my confidence drops:**

1. **Closing something, as opposed to adding something.** Adding a fact is documented; retiring
   an `UNSEEDED` marker touches a value, a provenance table, a consuming regime row, a count,
   a frontmatter block and the log, and nothing enumerates that. I got it right for the
   permittivity only because the open-question summary happened to name its own consumer
   ("regime row 31"). That is excellent authoring, not a mechanism — the next open question
   need not be so generous.

2. **Adding a *name* rather than a *topic*.** Topics go in `owns` and are checked. Names go in
   the glossary and are not. Finding 1 shows what happens: seven rows drifted with nothing
   firing. If I added `FooRecord` to `coupling-structure` tomorrow, I would know to add a
   glossary row, and I would have no way of learning if I pointed it at the wrong page.

3. **Anything involving a filesystem path.** Finding 2 — paths are deliberately backticked to
   escape the citation sweep, which means nothing validates them at all. I would be guessing
   whether `data/…` or `physics/library/…` is current, and today the *owner* page has it
   wrong.

### Recommendations, in the order I would do them

- **R1.** Glossary row check: left cell is one backticked token ⇒ that token must appear in
  the cited page. Five lines, catches all seven of Finding 1, and closes the corpus's only
  unverified index.
- **R2.** Backticked-path check: any `` `a/b/c` `` that looks like a repo path must exist, or
  be listed as a declared future artifact. Catches Finding 2. Needs a small allowlist for
  `EOM/A`, `Algebraic/MethodEquivalence`, `C2/m`, `dE_g/dT` — formula categories, space groups
  and derivatives that are not paths (these were my checker's main false-positive class).
- **R3.** Emit `generated_at` plus a hash of the page set into `corpus.json`, and have the
  checker refuse a stale index. Finding 4 — currently a stale index produces *false* findings,
  because `glossary.md` tells readers to interpret a miss as a finding.
- **R4.** Give `practice/` a page owning the open-question lifecycle: what closing one touches,
  in what order, and that the log entry is mandatory. The most-repeated workflow in a corpus
  carrying 51 open questions is the one that is unwritten.
- **R5.** Warn on `depends-on` entries never cited in the body (Finding 3), and add the
  journal→library mapping to the contract's own diagram (hunt 2).

---

### Verdict

I tried to break this corpus on ordinals, on anchors, on duplicate ownership, on table arity,
on history leakage and on retired vocabularies, and it held on all six — 788 citations without
a single dangling reference is not a result I expected to write. Twice I was confident I had
found a defect (`registry row 120` as a rotting ordinal, `log/timeline.md` as a missing file)
and both times the corpus was right and I was wrong.

The defects that remain share one shape: **the checker validates links, and every one of these
is a claim.** The glossary claiming a name lives on a page, a page claiming a file lives at a
path, an index claiming to be current. Three of my five recommendations are the same
recommendation — check the proposition, not just the pointer.

For the stated goal: a reader who has never seen this corpus answered five substantive
questions by opening nine of forty-five files, made zero wrong guesses on the four factual
tasks, and was handed the answer to task 3 by the corpus itself before asking. The rebuild
works for someone who did not do it.
