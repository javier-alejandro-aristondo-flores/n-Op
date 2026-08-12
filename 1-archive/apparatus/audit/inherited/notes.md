# Merged — notes

Fragments: 11/11

### from `oracle-state`

### A. The `Environment` record — what a complete schema needs, and who should own it

**Confirmed homeless.** I swept the `canonical-for` block of all 58 pages: no page names
`Environment`, and the only adjacent topic in the corpus is `crystal-inputs: top-level
inputs`. Meanwhile `Environment` appears in signatures on at least 13 pages —
`coupling-structure:82`, `named-formulas:54,176`, `applicability-classifiers:31,117,124`,
`residual-machinery:83,124`, `property-templates:51,79,84,96,100`, `pino-bridge:40`,
`residual-definitions:235`, `compose-time-pipeline:247,255,278`,
`computational-overview:52,334,473,590`, `cert-obligations:63`, `product:102,107,132`,
`build-order:21`, `build-sequence:37`, `glossary:35`, `traps:241` — and as a column header
in all five `physics/library/cert/reference-data/*.csv` files.

**Owner: `oracle/state/crystal-inputs`, anchor `#environment`.** It already owns "top-level
inputs" and already carries the (untyped) list; `multiscale-state §12` is shaped as a delta
("*Required* additions") and a delta table cannot survive D1. Add to `owns`:
`Environment record schema` and `structural/swept Environment partition`.

**A complete schema needs four things the corpus does not have anywhere:**

1. **Types and units per field.** Only the five harsh-env fields are typed
   (`multiscale-state:432-438`). The base fields are bare prose nouns. The field *names*
   are recoverable — `temperature`, `applied_electric_field`, `applied_stress`,
   `temperature_gradient` from `deriv-high-field:592`, `μ_env` from `multiscale-state:440`,
   plus pressure-or-volume, carrier-injection, applied magnetic field from
   `crystal-inputs:29-31` — but their types and units are not stated anywhere, and
   `deriv-high-field:592` is an appendix page (mine, do not seed values from it).
2. **The structural / swept partition, per field.** `Environment-structural` is used at
   `compose-time-pipeline:278` and `computational-overview:590` to key the kernel cache
   and is **defined nowhere** (grep: two uses, zero definitions). Swept scalars are
   re-evaluated per training sample (`applicability-classifiers:116-124`, `traps §33`);
   structural ones trigger recompile (`product:107`). Misfiling one silently reuses a
   kernel outside its envelope — this is why the partition is load-bearing, not cosmetic.
   Note `applied_stress` and `applied_magnetic_field` are the interesting cases: both can
   change the symmetry the Stage-2 quotient is built on.
3. **Absent ≠ zero.** `multiscale-state:440-442` makes *presence of a field* fire an
   applicability predicate ("first-order decidable on field presence"). So the schema must
   admit an unset state distinct from a zero value, and the set must be **closed and
   versioned** (a `schema_version` bump, as `DefectSpecies` has at `multiscale-state:129-131`)
   — otherwise adding a field silently changes which formulas apply to every existing
   composition.
4. **The `Environment` box.** `product:107` and `applicability-classifiers:124` stamp each
   emitted kernel with the scalar ranges its Stage-2.5 structure is valid on. The box is a
   per-swept-field range set — it cannot be specified until (2) says which fields are swept.

**`Crystal` is a third homeless type** and I found it while doing this. `(Crystal,
Environment) → Bool` is *the* applicability signature — every registry row, every
`CouplingChannel`, every `ResidualGenerator`, five property templates, and the glossary
entry use it — and `Crystal` is defined nowhere in the corpus. `crystal-inputs:36-38` uses
it in `(Crystal, Environment, weight)` without introducing it. It is almost certainly
`(PeriodicityStructure, SiteDecoration)`, but "almost certainly" is what the restructure
exists to eliminate. Same owner, same anchor.

### B. Retargeting hazard: `gamma-hat §4` has eight inbound citations

Row 34 deletes the framing of §4 and rows 35-38 scatter its four resolutions across three
pages. Eight external citations point at `gamma-hat §4` and **most cite it for the story,
not the content**: `README.md:105-106`, `open-decisions:58-70` (a struck-through item),
`computational-overview:229-232` and `:615-618`, `compose-time-pipeline:231-233`,
`10.5-timeline.md:212`, and two in `journal/live/specs/`. Each needs a decision, and three
of the sites are themselves scaffolding that other surveyors will delete. Do the
`gamma-hat` rewrite **after** the `computational-overview` and `open-decisions` fragments
land, or the retargets will be written twice.

`computational-overview:615-618` argues explicitly for keeping the closed item visible:
*"an entry that silently disappears from it reads as though it was never a problem."* D1
and D2 overrule that — the log is where it stays visible — but the builder should expect
the same argument to recur wherever a closed item is deleted, and answer it the same way.

### C. Three declared duplications to collapse, and one that is fine

- `computational-overview:222-227` restates `gamma-hat §2`'s read/write asymmetry **with
  cost detail `gamma-hat` lacks** (`matmat` against `N_PW × N_b` factors; costs set by
  `N_b`, not `N_PW²`). Do not delete either blindly — merge the cost detail into
  `oracle/state/gamma-hat#read-write-paths` and leave a citation behind.
- `computational-overview:229-240` restates the four γ̂ resolutions and labels itself
  "Summarized here; `gamma-hat §4` is canonical". Collapse to a citation.
- `gamma-hat §5` (row 39) restates `gamma-budget`'s two numbers without its derivation.
- **Fine as-is:** `unified-state:55-62` and `multiscale-state §1-2` state the tier split
  from the micro and multi-tier sides respectively. That is one fact viewed from two
  levels, not duplication — but only *after* row 40 removes `multiscale-state §1`'s
  argument-against-a-stale-quotation framing.

### D. What I checked mechanically, and what the checkers cannot see

Both checkers report clean on `2af93d2` and on a scratch copy of the tree. Per the brief I
planted defects rather than trusting that. Probes were run in
`scratchpad/probe/` (full copy of `journal/`, `physics/`, `informed-operator/`,
`README.md`), each planted in `2.2-unified-state.md`, restamped, then `--check`ed:

| probe | planted | result |
|---|---|---|
| A | `` `multiscale-state §99` `` — §-ordinal to a nonexistent section | **caught** |
| B | `` `uwbg-observable-catalog` `` — backticked ref to a nonexistent page | **not caught** |
| C | `[uwbg-observable-catalog]` — bracketed ref to a nonexistent page (control) | **caught** |
| D1 | `` `gamma-budget §1` `` — §-ordinal into a page that has **no numbered sections** | **not caught** |
| D2 | `` `gamma-budget §77` `` — same, absurd ordinal | **not caught** |
| D3 | "Per-slot memory layouts … are tabulated in `` `multiscale-state §12` ``" — section exists, claim absent | **not caught** |
| E | both a bracketed and a §-ordinal bogus ref planted in `informed-operator/design/` | **not caught** — the file is not walked at all |

Two consequences beyond what the plan records:

1. **The plan's §4 rationale for deleting `§N` ordinals is half right.** Ordinals do *not*
   "rot silently" in general — probe A shows the resolver fires
   (`check_book_structure.py:466-471`). But `:468-469` reads
   `if pid not in coords or not coords[pid]: continue`, with the comment *"unknown target
   or a page with no numbered headings"*. **33 of 58 pages have no `## <digit>` headings**,
   so every `§N` citation into them is skipped. Three of those are mine —
   `crystal-inputs`, `unified-state`, `gamma-budget`. `:470` also accepts `§8.2` whenever
   `§8` exists, so subsection precision is unchecked. Declared anchors fix all of this;
   the point is that the current guarantee is narrower than either the plan or a green run
   suggests.
2. **Probe D3 is the dangling-promise class**, and it confirms the salvage README's finding
   from the other direction: the defect survives even when the cited section *exists*. No
   syntactic check can catch it. If Phase 2 wants mechanical coverage, the only lever I see
   is requiring a citation to name the **topic** it is fetching (`[unified-state#wire-schema
   → per-slot units]`) and checking the topic against the target's `owns` — turning a
   content claim into a graph claim. That is a design proposal, not a finding.

I did **not** verify that `check_data_agreement.py` sweeps my six pages for value
disagreement; I confirmed only that it reports clean. Treat value-agreement in my scope as
**not checked**. The one value I did check by hand is row 98's diamond gap, against
`material-constants.csv:28`, and it agrees.

### E. Two structural observations I am flagging rather than acting on

- **`gamma-budget` is a merge candidate.** 246 words, one owned topic (`γ̂ MVP budget`),
  one `depends-on` (`forced-decisions`), and exactly **one** referencing page — `gamma-hat`,
  which restates its two headline numbers. Folding it into
  `oracle/state/gamma-hat#mvp-budget` would remove a page, remove a duplication, and cost
  nothing. I did not disposition it that way because the plan's §3 names `gamma-budget` as
  a surviving page in `oracle/state/`, and page-set changes are Javier's call at the
  Phase 1 gate. Rows 100-104 assume it survives; if it merges, they all retarget to one
  anchor.
- **No page in my scope is vacuously owned.** All six declare `canonical-for` topics
  distinct from their ids, and none appears in the plan's list of 18. `gamma-budget` is the
  closest call (`γ̂ MVP budget` vs id `gamma-budget`) — distinct by the letter of the rule,
  but it is one topic that restates the page title, so under the new `owns` requirement it
  should gain a second topic (the never-densify rule of row 100 is the obvious candidate)
  or merge per the point above.

### F. Ordering hazards for the builder

1. **`multiscale-state` must be rewritten before `unified-state` and
   `born-oppenheimer-levels` are finalized.** Rows 40, 44, 84 delete the reconciliation
   narrative; rows 19 and 89 delete the answering paragraphs on the other two pages. All
   three deletions are only safe together — done singly, each looks like it is removing the
   sole statement of the tier split.
2. **Row 8 (the `Environment` table move) crosses page boundaries in the opposite direction
   from the citation.** `crystal-inputs` currently *cites* `multiscale-state §12`;
   afterwards `multiscale-state` will need to cite `crystal-inputs#environment` from §4's
   applicability predicates. Do not leave both citing each other.
3. **Row 95 imports a resolution from `10.2-open-decisions`, which is outside my scope and
   is being dissolved into per-page frontmatter (plan §3).** If the `open-decisions`
   surveyor routes that resolution elsewhere, rows 94-96 conflict. Coordinate before
   writing `born-oppenheimer-levels`.
4. **Rows 36-37 move literature citations out of `gamma-hat` into `compose-time-pipeline`
   and `pino-bridge`.** Six papers with full bibliographic detail (Griewank & Walther;
   Naumann; Lubich & Oseledets; Ceruti & Lubich; Kieri/Lubich/Walach; Ceruti/Kusch/Lubich).
   They are the substance of those two bullets. If a move drops them, the surviving text
   asserts "the literature has an answer" without naming it.
5. **Row 53 (§4's nine formulas) and row 71 (§9's homogenization map) carry ~40 numeric
   values** — barriers, cross-sections, diffusivities, thresholds. Every one traces to a
   `deriv-*` page that is being deleted (row 54). Re-seed from
   `registry-manifest.csv` rows 105–112 and `9.1-accuracy-ledger` per the brief's trap, and
   expect that some values exist *only* in the appendix. Where that happens it is a
   Contradiction row for auditor 2 or an acquisition task — not a value to copy forward
   from an appendix page.

### G. What I could not disposition confidently

- **Row 79** (`multiscale-state §13`, the three thermodynamic-identity residuals). They are
  residual *definitions* sitting on a state page, so structurally they belong with
  `residual-definitions`. But all three are consistency conditions **on slow-tier state
  fields** (`charge_dist[D]`, `[H]`, `x_ox`), and splitting them from the schema they
  constrain may be the worse outcome. I routed them to `oracle/laws/residual-definitions`
  and am flagging it; whoever holds the `oracle/laws` fragment should decide, since they
  can see whether §13's siblings (items 1–17 of `residual-definitions §1`) are staying put.
- **Row 31/37** (the steppable-form manifest and the DLRA literature). I routed both to
  `oracle/seams/pino-bridge`. They could equally belong to `oracle/operator/seam`, which is
  being mined fresh from `informed-operator/design/` and does not exist yet. Whoever builds
  that page should re-check.
- **Row 39** depends on the `gamma-budget` merge question in Notes §E.

---

### from `oracle-laws-seams`

**The stage-ordering / curriculum boundary, stated once so the builder does not have to re-derive it.**
Three facts, three owners:

- **Epoch sequence** — supervised VASP epochs → one informed epoch → oracle-free inference, plus the
  *why* (a residual is a local signal; the oracle refines, it does not search) and the four
  consequences. → `operator/training/stage-ordering`. Mined from
  `informed-operator/design/training-stages.md` (whole file) and `2026-07-22-prep.md:286-296`.
  These are the **only** two statements of it and neither is in canon.
- **Category participation gate** — which `CategoryTag`s are live at which fraction. →
  `oracle/laws/residual-definitions#curriculum-gate`. Stays where it is. It is keyed on the
  oracle's own closed vocabulary and states a property of the residual surface.
- **Source-weight schedule** — `w_cheap / w_vasp / w_exp / λ_residual` over training. →
  `operator/loss/`. Mined from `residual-loss-methodology.md:171-205`.

The test that separates them: *if the operator switched to a different data source, which fact
changes?* The gate does not; the stage ordering and the weight schedule both do.

**Two of these three currently collide on the same numbers.** The category gate and the
source-weight schedule both use `0.10 / 0.60 / 0.90` and both name their middle phases
"Refine". They are different schedules on different axes. Whoever writes the two pages should
make the distinction explicit at both ends, or a later reader will merge them.

**Ordering hazard — `cross-cutting-rules` must not be deleted before row 114 is moved.**
The `Observable`-role selection precedence ("declared dressing tier, then registration order")
exists in exactly one sentence in the corpus, on the page I am recommending be dissolved.
`physics-graph` defines the role and states no precedence. Delete-then-move loses it.

**Ordering hazard — `residual-machinery §2` before `residual-definitions §2`.**
Row 47 deletes a duplicated block but three lines at its tail are unique (row 48). Deleting the
section wholesale loses the bare-vs-dressed-chains rule.

**Ordering hazard — ch. 11 and the `layer : 0..6` field.** Row 94's citation is already broken;
the 7-layer compute DAG it means to cite lives in `11.8-deriv-generator-catalog §2`, which is
being mined. If ch. 11 is dissolved before the DAG gets a home, the field's semantics go with it.
`11.8` also carries the **retired differentiability legend** the plan warns about — the same page,
so mining it needs the warning applied and the `curriculum-phase` enum treated as suspect
(contradiction row 2).

**On `pino-bridge` versus `learnable-structure-requirements` — the duplication is real but
smaller than it looks, and the split should survive.** I checked all ten requirements. R1–R8 and
O1–O2 are *demands on the operator*; `pino-bridge` states *what the oracle exports*. Those are the
two halves of one contract and they belong on opposite sides of the module boundary:
`oracle/seams/pino-bridge` and `operator/seam/learnable-structure`. What is genuinely duplicated
is the *oracle-side setup* each requirement restates before making its demand:

| | duplicated statement | canonical owner |
|---|---|---|
| intro | "the only surface a downstream consumer sees is the pino-bridge" | `pino-bridge#surface` (row 84) |
| intro | the two-loop symmetry (training sinks cotangents into weights, design into the candidate) | stated **three** times: `1.5-rationale.md:129`, `1.2-product.md:197-199`, LSR:20-23. One owner; two citations. |
| R1 | admissibility is scored, never presupposed | `residual-definitions#structural-categories` |
| R2 | symmetry-quotiented axis grids fixed at compose time | `compose-time-pipeline#stage-2` |
| R3 | the oracle returns per-key cotangents | `pino-bridge#validate` |
| R5 | float normalization (canonical quiet-NaN, `−0.0 → +0.0`) | `representation-substrate#addressing` |
| R8 | loop logic lives in `/interface` | `program/purpose/purpose-and-scope` |
| O1 | the Stage-2 sidecar carries per-instance symmetry structure | `compose-time-pipeline#stage-2` |
| O2 | tiers evolve at heterogeneous rates | `oracle/state/multiscale-state` |

Each should become a citation, leaving the requirement itself. **None of them currently
*disagrees* with its canonical source** — I checked each — so this is redundancy, not drift. The
one exception is R1, which cites `unified-state` for content that page does not contain
(open question `state-array-layout`), and R1's finite-float64 demand, which has no oracle-side
counterpart at all.

**LSR carries the find/replace damage (plan defect 8) at lines 4–5** — ``the atomic tree
(`the canon chapters*`, `the canon chapters*`)`` — so its own provenance sentence is unreadable
and the two documents it names cannot be recovered from the text. `git log -S` on that file is
the only route. Mining it does not require them, but the log entry attributing the contract does.
I checked whether the same damage hit my scope: `generic-dynamics:122` also reads "the canon
chapters", but `git show 2f1d22f^` proves it was already there before the rename (only
`impl-06-compositions` → `typed-compositions` changed), so it is pre-book chapter-numbering prose,
**not** find/replace damage. Disposition unchanged (row 10) but the classification differs.

**Nomenclature defects present in this scope, per §4 — propose to Javier, do not act.**
`DN` outside `D0–D4` (`7.2:70`) · `Layer-1.75` (`7.2:227,272,285`) · `Stage 2.5` inside a
"4+1 stage" pipeline (`3.3:224,243`; `7.3:76,99`). All are load-bearing tokens appearing in typed
enums, not just prose, so renaming them is a code-shaped change even though no code exists yet.

**Values in this scope are unverified and unverifiable by the current tooling.** Calibration
(header table) shows `check_data_agreement.py` reads none of them despite sweeping
`journal/pages/`. I hand-checked the three that have a canonical source and they agree: AHC ZPR
amplitudes against ledger row 15, the `Δα` freezing rule against ledger row 49, and registry rows
25/63/72/75/80/87/92/104/120/121/122/124/125/126 against `registry-manifest.csv` (all resolve,
all names match). The rest — the diamond metastability band (+25 meV/atom, σ 5 meV/atom), the
440 GB dielectric-matrix figure, `|G| ≤ 192`, `dim(T) ≤ ~250`, ~12M ops, `τ_adj = 1e-4`,
`N ≈ 64` — have **no canonical source in the corpus to check against.** I did verify the 440 GB
figure is arithmetically self-consistent with its own stated dimensions (12³ × 64 × 500² ×
complex128 ≈ 442 GB). Everything else in that list is stated once and checked by nothing. That is
a statement about coverage, not a claim that any of them is wrong — auditor 2's call.

**Blocks I could not disposition confidently.** Row 69 (`CouplingSpec` schema-version bump): I
marked it `mine` per the tie-break rule, but the live fact is thin once its "previously/now"
motivation is stripped, and I could not determine whether the version bump is still *doing*
anything in a corpus with no legacy addresses to collide with. Row 92 (the `bundle`-field comment)
has the same shape. Both are cases where the scaffolding *is* the explanation, and removing it
leaves a rule with no visible reason. Flagging rather than guessing.

**What I swept and dismissed.** All §-coordinate citations in the six files were machine-checked
against every page's numbered and dated headings: two do not resolve or are not checkable —
`residual-generator-catalog §2` (row 94) and `accuracy-ledger §1/§15/§49`. The latter is a
**notation collision, not a broken pointer**: those are ledger *row* numbers written in
section-coordinate syntax, and `accuracy-ledger` has zero numbered headings, so
`check_citations` skips them by the `pid not in coords or not coords[pid]` guard. Content-wise
all three land (verified against ledger rows 1, 15, 49). Under the new `[id#anchor]` scheme they
must be re-expressed as row references. I also verified `timeline §2026-06-10 (Wave 1)` and
`traps §58` *are* checked — by the dated-anchor path and the dedicated trap-number handler
respectively — so neither is a finding despite both targets having no numbered headings.

---

### from `oracle-compilation`

### Calibration — what the checkers actually catch

Per the brief I did not trust a green run. I copied the corpus to a scratch tree,
confirmed both checkers green, then planted one defect at a time in
`4.1-physics-graph.md`.

**First attempt produced three false positives, and the reason matters.** Every
planted defect initially "fired" — but the failure message was always
`stale content-hash (… -> …); regenerate`, never the citation error. The
`content-hash` stamp trips on *any* byte change and masks the check under test.
Re-running with hashes restamped between probes gives the true picture:

| planted defect | result |
|---|---|
| backticked citation → nonexistent page id | **MISSED** |
| backticked citation → real page absent from `depends-on` | **MISSED** |
| backticked **retired** page id (`arch-11-residuals`) | **MISSED** |
| section citation → nonexistent section (`§99.7`) | **MISSED** |
| retired serial coordinate (`§20.4.2`) | **MISSED** |
| bracketed citation → nonexistent page id | FIRED |
| bracketed citation → real page absent from `depends-on` | FIRED |

Three consequences for Phase 2:

1. **`content-hash` is a calibration hazard, not just maintenance cost.** Any
   probe that edits a page trips the hash check first. A calibration harness that
   does not restamp between probes will report the checker as catching defects it
   does not catch. This is a plausible mechanism for the false "one defect per
   check" claim in the plan's standing warning, and it is an independent argument
   for §4's deletion of the stamp.
2. **Chapter 4 is almost entirely unchecked.** 190 of 198 cross-references are
   backticked. `4.1-physics-graph` has **44 backticked and 0 bracketed** — none of
   its references is verified by anything.
3. **`check_the_checkers.py` reports `58/58 fired, 0 missed, 0 stale` and
   `coverage: every data-agreement check (19) fired under some probe`.** That is
   true and not reassuring: the probe set is derived from the checks that exist,
   so the five classes above are not "uncovered", they are invisible. When the
   harness is rebuilt (§8), the probe set must be derived from the *defect space*
   — including anchor resolution and citation syntax — not from the check list.

### The `§20.x` census — every retired-coordinate citation

`§20.x` is the retired serial coordinate for `representation-substrate`
(`10.1:153`, `journal/instructions.md:51`). Full corpus census, so Phase 2 can
re-anchor in one pass — **note that the correct target differs between them**:

| location | as written | resolves to |
|---|---|---|
| `4.2:177` | `§20.4.1` | `representation-substrate#identity-exact` |
| `4.4:231` | `` `§4.1`/`§20.4.2` `` | both `#identity-exact` **and** `#estimate-dont-decide` |
| `2.3-gamma-hat.md:128` | `` `§4.1`/`§20.4.2` `` | both |
| `2.3-gamma-hat.md:136` | `§20.4.1` | `#identity-exact` |
| `10.2-open-decisions.md:62` | `§4.1/§20.4.2` | both |
| `10.2-open-decisions.md:114` | `§20.4.2` | `#estimate-dont-decide` |
| `10.2-open-decisions.md:178, 187, 201` | `§20.4` | `#serialization` |
| `11.9-deriv-language-study.md:68, 86` | `§20.4` | `#serialization` |
| `live/presentations/2026-07-22-cs-framing-outline.md:360` | `§20.5` | `#hot-paths` |
| `live/specs/2026-07-21-oracle-code-spec-research-brief.md:97, 125` | `§4.1`/`§20.4.2` | both |

Two further retired coordinates of the same family, outside my scope but found
while sweeping: `4.4:614` and `10.3:114` cite `` `γ̂` §15.4 `` (retired serial for
`gamma-hat`), and `2.4-multiscale-state.md:280` cites a bare `§16`.

### The 4.4 recommendation — and where it conflicts with the plan

Plan §3 lists `computational-overview` as a surviving page under
`oracle/compilation/`. A claim-by-claim disposition **empties it**: 27 of ~40
blocks restate a page that already owns the topic, and each of the 11 originals
has a better owner (`computational-methods`, `unified-state`, `physics-graph`,
`compose-time-pipeline`, `cert-obligations`, `topology-atlas`,
`property-templates`, `gamma-budget`, `born-oppenheimer-levels`).

**My recommendation: delete the page and route the originals.** The reasoning is
the plan's own. A page whose charter is to restate ten chapters (`4.4:38`) cannot
be made non-duplicating by editing it — the duplication is the charter. Its
vacuous `canonical-for` is not a coincidence: a page that owns no topic distinct
from its id is precisely a page with nothing of its own, and the checker cannot
see the duplication because the duplicate-topic invariant never fires on it. Its
§11 math-to-location map is the one thing that genuinely wants to be
cross-cutting, and §6 already says that job belongs to emitted `corpus.json`.

**This is Javier's call, not mine** — it changes the agreed target structure. If
he keeps the page, it must be given a real `owns:` list (I suggest: *per-method
complexity and numerical stability*, *cross-cutting cost model*), and rows 108,
114, 117 should stay on it rather than move. Rows 87, 99, 100 should move
regardless: they are the ones other pages already depend on.

### Ordering hazards

- **Row 87 is the one that must not be missed.** `4.4:186-192` is the only
  per-slot layout table in the corpus, and seam requirement R1 points at
  `unified-state` for exactly that content. Deleting 4.4 before the table is
  moved converts a documented dangling promise into a permanent loss. Same shape,
  lower stakes, for rows 99 (arena/index DAG — `10.3:106` depends on it) and 53
  (the not-C4 disambiguation).
- **Rows 108 and 117 relocate into pages that are currently very thin.**
  `computational-methods` is 309 words; row 108 is roughly 1,200. The receiving
  page's structure will need to be designed, not appended to.
- **Do not seed any value in this fragment from `11.8` or `11.9`.** I took no
  values from appendix pages; the γ̂ budget numbers in rows 90–91 are checked
  against `gamma-budget` (`2.6:16-33`), not against an appendix.
- **`4.3 §8` (row 64) must be deleted only after `corpus.json` emits the
  topic→page map**, since §8 is the corpus's current human-readable version of
  that map. Delete it earlier and navigation regresses between phases.

### What I could not disposition confidently

- **Row 120 (§11 math-to-location map).** I marked it `mine` to `index/corpus.json`
  because §6 says navigation is emitted, but `corpus.json`'s specified schema
  (page/topic/anchor/edges/open-questions/formula-registry) has **no field for
  "branch of mathematics"**. Either the schema grows a field or this map needs a
  home as prose. Flagged rather than guessed.
- **Row 70 (the computational-lens blockquote).** I routed the lens to
  `practice/conventions`, but no surveyor owns "reading conventions" explicitly
  and `practice/conventions` may already be full. Low stakes; one paragraph.
- **Whether `4.2:114-116` settles C1.** It is the strongest argument that "2.5"
  is principled rather than sloppy, and it may mean the right fix is to keep the
  fractional stage and rename the *count* ("5+1"), not the stage. I did not
  decide; §4 says propose only.
- **`4.3 §2`'s "Four op signatures … (a fourth, `GroupOps`, is added below). Three
  cover …"** reads as though it was edited from three to four in place. It is
  correct as written, just awkward, so I did not log it as a contradiction — but
  a Phase-2 rewrite should smooth it.

---

### from `oracle-cert-accuracy`

**The 5.1 / 5.4 split is not real. Merge 5.4 into 5.1 and delete the page.** The
brief asked me to determine this, so here is the full basis:

- 5.4 is 293 words. Its closing paragraph (`5.4:33-36`) restates 5.1's opening
  (`5.1:45-48`) — and each copy carries a clause the other lacks, which is
  duplication drift already in progress, not a summary/detail relationship.
- Its opening two lines are connective tissue ("The ten obligations are listed in
  `cert-obligations`").
- Its **only** unique content is the ten-row axis-mapping table.
- 5.1 already promises that table and fails to deliver it: `5.1:69` says "Each
  obligation maps onto a Layer-0 axis (§10)" — a bare ordinal that resolves to
  nothing on any page, and which does not name 5.4.
- **No prose anywhere in the corpus cites `cert-obligations-detail`.** I checked
  every inbound reference: `5.1:26`, `3.1:23`, `3.2:31`, `7.2:27` are all
  generated `referenced-by` entries (zero of the four lists it in `depends-on`,
  zero mention it in body text), plus `contents.md`, `index.md`, and
  `retired-ids.csv`. The only real consumers are in `journal/live/specs/`, a
  container D13 deletes.
- Its `canonical-for` is `cert obligation detail` — a topic whose only content is
  "the detail of the topic the other page owns."

A page reachable only by browsing, whose unique content answers a broken
cross-reference on its parent, is the split being a filing accident. **This
contradicts the plan's §3 target list, which names both `cert-obligations` and
`cert-obligations-detail` under `oracle/certification/`.** Flagging rather than
acting: if the merge is accepted, that line of §3 needs updating; the merged page
is ~2,100 words, well within range.

**Proposed `owns:` topics, to fix the two vacuous claims in my scope.** Both need
≥1 topic distinct from the id:
- `accuracy-ledger` → `per-observable accuracy regime`, `design-grade`,
  `curated coefficient seed`, `MVP design-grade targets`
- `reference-battery` → `reference-row schema`, `sigma encodings`,
  `battery seeding waves`

The other four pages' `canonical-for` values are already non-vacuous
(`ten cert obligations` + `reference-cache backend`, `applicability discipline`,
`scope exclusions`) and only need widening to cover topics they in fact own —
`cert-obligations` owns the tolerance ledger and the composition refusals, and
names neither.

**Ordering hazards for the builder.**

1. `check_data_agreement.py:179-183` locates the tolerance table by regexing for a
   heading matching `^## [\d.]+ Tolerance ledger$` in
   `journal/pages/05-certification-and-applicability/5.1-cert-obligations.md` —
   both the path and the heading text are hard-coded. Renaming the heading or
   moving the page empties `TOL_SYMBOLS`. There is a guard (line 184) that emits a
   finding when the list comes back empty; it is the only thing standing between
   the move and 17 silently unchecked tolerances. **Update the checker in the same
   commit that moves the page.**
2. `check_book_structure.py:366-376` finds the ledger by `id == "accuracy-ledger"`
   and parses rows with `^\| (\d+) \|`. Merging the gap-audit table (rows 53–59)
   into the main table is safe — the check already spans the whole body — but the
   `| N |` row-start format must survive the rewrite.
3. `9.1` is `depends-on: deriv-observable-catalog`, and its opening sentence and
   its count-disambiguation both define themselves by reference to it. So does
   `glossary.md:76` ("Catalog observables"). Chapter 11 deletion breaks three
   references to one dying page. The number 52 has to be restated as a fact, not
   as a property of a container.
4. `5.3` is `depends-on: deriv-high-field` and cites `[deriv-high-field] H.3` for
   the SEE/SEU disposition (`5.3:99-101`). That anchor exists today
   (`11.5:413 ### H.3 SEU rate (digital)`). The disposition is already "registered
   here", so the citation can simply drop.
5. `5.1` cites `[deriv-language-study]` for the `τ_interp` differential golden test
   (`5.1:152`). Whoever mines 11.9 must land that test's definition somewhere the
   tolerance ledger can point at.

**Checker calibration — what I actually verified, and what I did not.** Per the
brief I planted each defect in a scratch copy at
`…/scratchpad/cal` (a full copy of `journal/ physics/ informed-operator/`;
`corpus_root.refuse_if_scratch_copy` only refuses `.claude/worktrees`, so it ran).
Content-hashes were restamped before each `--check` so a stale hash could not mask
the result.

| planted defect | structure checker | data checker |
|---|---|---|
| `[no-such-page-at-all]` in 5.1 (control) | **FAILS** — "resolves to no page" | clean |
| `` `no-such-page-at-all` `` in 5.1 | **passes clean** | clean |
| `` `residual-machinery §9999` `` | **FAILS** — "§9999 does not resolve in `residual-machinery`" | clean |
| bare `(§9999)`, no page named | **passes clean** | clean |
| ledger κ(diamond, 300 K) 2200 → 9999 | **passes clean** | **passes clean** |
| vacuous `canonical-for` on 5.1 | **passes clean** (topic count 98→97, unremarked) | — |
| invalid YAML frontmatter | **passes clean** — 9.2 is live proof, no plant needed | clean |

Consequences for reading my scope: the backticked citation form is the one these
pages use almost exclusively (`coupling-structure §8`, `cert-obligations §1.3`,
`residual-machinery §5`, …), so their page-qualified ordinals *are* checked — that
class is genuinely clean here. What is not checked, and where I therefore looked by
hand: bare ordinals (found one, `5.1:69`), page-value-vs-CSV agreement (found the
duplication set in rows 42–45), and vacuous ownership (found two).

**Considered and dismissed.** I checked whether `9.1`'s "59 ledger-tracked
observables" headline had drifted from its table — it has not, and it is
machine-enforced. I checked whether `3.2:308-315`'s restatement of the seven MVP
targets was an uncontrolled duplication — it is not: it names `[accuracy-ledger]`
as canonical and carries its own warning that restating an enumeration is what let
one drift before. That is the model for every "cite, don't restate" row above. I
checked all `§`-ordinals in the six pages against their targets' headings;
apart from row 9 and the `§N`-means-a-row cases in row 33, they resolve. I did not
audit `journal/live/specs/2026-07-21-oracle-code-spec-research-brief.md` beyond the
obligation-9 passage — it is another surveyor's container, but it is worth someone
sweeping it before deletion, because it already contains at least one open question
canon does not.

**One thing I could not disposition confidently.** `5.3:122-123` says
"cert obligation-**3** flags suspect cases" for out-of-scope queries. Obligation 3
is analytic limits; obligation 9's domain check and the §1.3 refusals look like the
mechanisms that would actually fire. I left it as `keep` because deciding is a
contents question (auditor 2), but if it is a typo for obligation 9 it interacts
directly with `obligation-9-scope` above and should be resolved with it.

---

### from `oracle-registry`

**This chapter's real shape.** Ten pages describe one vocabulary and a CSV that is
canonical for much of the same content. The duplication is not evenly spread — it
concentrates in two places, and both have the same root cause:

- **`6.9-formula-registry` is the redundant page.** Of its five sections, "What the
  registry is" duplicates `6.6` + `4.1`, "Columns" restates the CSV header, the
  cost-tier legend duplicates `6.6` verbatim, the differentiability legend is a bare
  pointer, and "How a formula becomes a residual" summarizes `7.2`. Exactly one
  block is unique: the row-band → physics-package map. Rows 116-119 move that to
  `named-formulas`; the rest deletes. Under plan §6 the page's stated job — "the
  human-readable index over the CSV" — is what `index/corpus.json` plus the
  generated `contents.md` are for.

- **`6.1-canonical-vocabularies` is *not* redundant, despite looking index-shaped.**
  Only its header count table is index-like, and that table is the emitted view under
  plan §6. Its seven numbered sections carry substantive content that exists nowhere
  else: the `mesh-interpolation` interpolator description, the templates' `Produces`
  mapping, `CrystalSymmetryGroup` and `IrrepLabel`, the `(StateComponent, SubDofTag)`
  pair table, and the ten theory-context vocabularies. My rows scatter six of the
  seven sections to their owning pages and leave §7 — the one topic `index.md`
  agrees it owns. If Phase 2 prefers to keep `canonical-vocabularies` as a page,
  §7 alone is enough to justify it; if not, §7 merges into `coupling-structure`
  beside the `TheoryContext` record.

**Hard ordering hazard — the checker reads two of these pages.**
`check_data_agreement.py` harvests live vocabulary from the corpus at import time:

- `:450-452` reads the `| Bn |` table out of `6.1-canonical-vocabularies.md` by path,
  and `:464-467` raises a finding if the table is not found.
- `:456-457` reads the phrase `` `L1` primitive tag`` out of `6.6-named-formulas.md`
  by regex.

Row 17 moves that table to `observable-bundles` and row 65 keeps the `FormulaRecord`
comment intact. **Both edits must land in the same commit as the checker rewrite, or
the Bundle column silently goes unchecked** — the `if not _BUNDLES` guard prints a
finding, but only if someone reads it. `traps §70` records the last time this class
of mistake retagged four correct rows.

**Two pages are already orphans; two more become orphans when ch. 11 dies.**

| page | inbound edges today | after ch. 11 |
|---|---|---|
| `observable-bundles` (6.7) | **none** | none |
| `computational-methods` (6.4) | one heading in `4.4` | one |
| `formula-registry` (6.9) | `deriv-csp`, `deriv-generator-catalog`, `deriv-high-field`, `properties` | `properties` only |
| `properties` (6.10) | `deriv-high-field` | **none** |

`6.7` and `6.4` are orphaned because `6.1` holds the content that would cite them —
rows 7-9 and 17-18 fix that by merging. `6.9` and `6.10` are orphaned because their
only real readers were appendix pages. That, plus their vacuous `canonical-for`, is
why I dissolve `6.9` and propose merging `6.10`.

**Merge proposal I could not settle: `properties` into `typed-compositions`.**
`6.8:39` says it writes "every property in `properties.md`" as a typed composition,
so the two pages are one artifact split in half: `6.10` is the checklist, `6.8` is
the proof it is covered. Merging would make the coverage claim checkable — a
composition per listed property, with the gaps visible. Against merging: `6.10`'s
nine motivation paragraphs are reader-facing scope prose and `6.8` is dense typed
pseudocode; the merged page reads as two documents. I have dispositioned both to
survive as separate pages under `oracle/registry/`; **the merge is Javier's call**
and is the only structural decision in this chapter I did not make.

**Low-confidence rows, named.**
- Row 45 (`6.3:15-17`, the "(Lattice + SiteDecoration + Laws) → Material" composition
  axiom) — I sent it to `compose-time-pipeline`, but it may belong to
  `architectural-principles`. It is a preamble on a topology page either way.
- Rows 20-22 (`CrystalSymmetryGroup`, `IrrepLabel`) — I sent them to
  `representation-substrate` because their identity is an `Address[GroupAtlas]` and
  their derived outputs are substrate fibers. `compose-time-pipeline` is defensible:
  the group is *assembled* at Stage 1+2. Either target keeps them together; splitting
  them would be the wrong outcome.
- Row 129 (Magnetic has no dedicated bundle) — I kept it as a body fact. It is
  arguably an `open-questions` entry, since it is a stated coverage hole with a
  reason rather than a decision.

**The `path` field's history is worth preserving as a trap, not as prose.** Row 84
deletes the "briefly declared retired" paragraph, and the log entry captures the
event. But the *lesson* — a field several pages depend on was retired on a
reasonable-sounding argument, and un-retiring it required reconstructing why four
places used it — is a live hazard about how this corpus fails, and belongs in
`practice/traps` alongside §70. Flagging so it is not lost between the log and the
delete.

**Where I could not disposition confidently, and why.**
- The `Source`-column values in the CSV (`extension`, `topology atlas`, research-file
  pointers) are described by `6.9:95` and owned by the CSV. I dispositioned the
  prose; the CSV's own `Source` discipline is the manifest surveyor's.
- `6.9:69-70` cites `physics/research/` as the grounding for rows 1–87. The plan
  flags `10.3-audit-prompt` for citing that directory for physics that moved to
  `pages/11-`. I did not verify whether `physics/research/` still holds the rows-1–87
  grounding; if it does not, row 119's provenance claim is a dangling promise and
  the *actual* provenance may only exist inside chapter 11 — which would make it
  urgent, since ch. 11 is being deleted. **Worth one check before Phase 2 starts.**
- I did not disposition `registry-manifest.csv` (another surveyor owns it), but I
  verified against it throughout. Everything reconciled: 134 rows = 132 + 2 markers;
  `Path` 117/15/2; `Tier` 76/40/11/5 matching `4.4:435`; exactly one `D0` row
  matching `6.6:70`; all 18 declared-unregistered names absent; all 20 registry names
  I spot-checked from `6.6`/`6.7`/`6.8` present. **I found no count in this chapter
  that disagrees with the CSV.**

---

### from `program`

### The merge recommendation, stated plainly

Seven pages on "the MVP and how to build it" reduce to **five**, and five pages on
"what n-Op is" reduce to **five with one gutted**. What each page uniquely owns:

| page | what it uniquely owns | verdict |
|---|---|---|
| `mvp-system` | the **consequence** column — CBM on Δ not at X and the six-fold degeneracy that transport rows consume; PBE −23% ⇒ hybrid required; Θ_D ⇒ QHA valid to 800 °C ⇒ SCPH deferred; non-polar ⇒ rows 17/21/22 excluded; oxidation is the lifetime limiter | **survives.** Its value column does not (row 99) |
| `capability-slices` | the per-capability vocabulary selection — which methods, templates, formulas, bundles, residuals, obligations each capability draws | **survives; absorbs `mvp-scope`** |
| `mvp-scope` | nothing that is not a sum over `capability-slices`' three tables, except the one-third judgment and the deferral list | **merge into `capability-slices`**; deferrals → `out-of-scope` |
| `forced-decisions` | the polyglot four-role shape; the TB warm-start's "not a residual" qualifier; the L1 output requirement | **survives.** Its battery inventory → `reference-battery`, its tolerances → `accuracy-ledger` |
| `build-order` | the MVP exit criterion (one sentence). The 9 steps are a projection of `build-sequence` filtered by `mvp-scope` | **merge into `build-sequence` as an in-MVP column** |
| `build-sequence` | the 14-phase plan, the decidability gate, the Stage-2.5 attachment, language-neutrality | **survives; absorbs `build-order`** |
| `build-verification` | the static consistency set and the five runtime gates | **survives**, but every `§`-ordinal in §1 must be rewritten and `architecture.md` removed |

The merges are not tidying. `build-order`-as-a-projection is what produced C6: a subset
relation asserted in prose, never checked, and false. Expressed as a column on the source
table, C6 cannot recur. `mvp-scope`-as-a-summary is what produced the orphaned pointer "the
rows above" (row 111) and the stale "D4 surrogate nets" (row 114).

### `library-landscape`: both, and the page must survive

The three-module partition **is** the top-level tree (`journals/oracle` · `operator` ·
`interface`), so the partition itself becomes organization. But four facts on that page
cannot be encoded by a directory layout and are stated nowhere else:

- the oracle's CLI ships **inside** `/physics`; `/interface` is the loops, not the command line (row 57);
- engineering aspects (defects, dopants, surfaces, interfaces, operating-condition effects) live inside `/physics`, not a fourth library (row 58);
- `/physics` does not wrap external DFT codes **at runtime** (row 53);
- `/interface` owns every driving loop and is not yet designed (row 56).

Keep the page, demoted from "here is the partition" to "here are the module boundary
rules." Without it, a reader who sees three sibling directories has no statement of what
may not cross between them — and the CLI question in particular will be re-litigated,
because a directory named `interface/` reads like the natural home for a command line.

### `rationale`: the plan keeps the page; after de-duplication it is two sections

The plan's target lists `program/purpose/rationale`. My finding is that of its nine
sections, **§2 and §6 are the only content not owned elsewhere** — everything else is a
restatement of `product`, `purpose-and-scope`, `crystal-inputs`, `unified-state`,
`pino-bridge`, `canonical-vocabularies`, `representation-substrate`, or the timeline.
And the two survivors belong to different journals: §2 (verifying is cheaper than solving)
is `program/purpose`, §6 (why a neural operator, its caveats, the equivariance handoff)
is `operator/seam`.

So the honest options are: (a) `rationale` survives carrying §2 only, with §6 relocated;
or (b) `rationale` dissolves entirely, §2 → `purpose-and-scope#why-a-grader`, §6 →
`operator/seam`. I lean (b) — a page whose remaining content is one argument is a section,
not a page — but this is a structure decision above my scope, so I have dispositioned the
rows to their content targets and left the page question here. **Either way §2 and §6 must
be relocated before the page is touched.** §2 is the program's central justification and
§6 is the only argued defense of the choice of learner; both currently sit on a page that
is orphaned (`referenced-by: []`), self-labeled a historical snapshot, and therefore the
single most likely thing in the corpus to be deleted wholesale by someone reading its
header.

### Two defect findings that extend the plan's §2 inventory

**1. Vacuous ownership is 23 pages, not 18.** The plan counts pages whose `canonical-for`
topic string equals the id exactly. The checker's uniqueness key is
`" ".join(topic.lower().split())` (`check_book_structure.py:197`) — case- and
whitespace-normalized but **not hyphen-normalized** — so a page can own the spelling of its
own id with spaces and be invisible to both the plan's count and any string test. Five such
pages exist; two are in my scope:

| page | id | owns |
|---|---|---|
| `1.4-architectural-principles` | `architectural-principles` | `architectural principles` |
| `8.6-build-sequence` | `build-sequence` | `build sequence` |
| `6.3-topology-atlas` | `topology-atlas` | `topology atlas` |
| `7.3-cross-cutting-rules` | `cross-cutting-rules` | `cross-cutting rules` |
| `10.2-open-decisions` | `open-decisions` | `open decisions` |

The last three are outside my scope; the surveyors for registry, seams, and governance
should confirm rather than take this from me. **The consequence for Phase 2 is specific:**
plan §8 states the fix as "every page owns ≥1 topic distinct from its id." Implemented as a
string comparison, that rule passes all five of these pages unchanged. The check must
normalize hyphens, whitespace, and case before comparing — otherwise the fix ships with the
defect it was written to close. Probe A separately confirms there is no vacuous-ownership
check today at all: a page owning *exactly* its own id runs green.

**2. A fourth identifier namespace, undefined and collided.** `8.4-forced-decisions` labels
its bullets `H1`, `H4`, `H7`, `H8`. H2, H3, H5, and H6 appear nowhere in the corpus, so the
series is not merely undocumented — it is not a series. The labels are nonetheless cited
across pages: `8.5:27` ("`forced-decisions` H4") and `9.2-reference-battery.md:52`
("`forced-decisions §H4`"). And `H1` collides with an unrelated series: `2.4-multiscale-state`
uses `F-H1` at lines 198, 434, and 436 for a formula from `deriv-high-field` Part H. This is
the same overload class as `GAP` (`[traps] §59`) and belongs on the plan §4 rename list.
Deleting the labels requires fixing both external citations.

### Citation exposure in this scope

`1.2-product` cites 9 pages that are not in its `depends-on`; `1.5-rationale` cites 12.
Both pass the checker because those citations are backticked and `REF_RE` matches only
`[id]` (defect 1). These two pages alone account for **21 unverified dependency edges** —
about 60% of their combined citation load. The remaining ten pages in my scope are clean on
this axis, with two exceptions I checked and dismissed: `8.2` and `8.7` cite `[traps]`
without listing it in `depends-on`, which the checker tolerates because `traps` is in its
`NOT_IDS`-style exemption path rather than because the edge is real.

Under the one-syntax rule this becomes visible work rather than a latent hazard, but note
the ordering: **rewriting citations to `[id#anchor]` on `1.2` and `1.5` will surface 21 new
`depends-on` edges at once**, and several of them (`purpose-and-scope`, `library-landscape`)
create cycles with pages that already cite back. Decide the cycle policy before rewriting
these two, not after.

### Dangling promises found

- **`score-not-solve` → `purpose-and-scope`.** Cited from `1.2:68` and `1.5:50` as though
  `1.1` were the source. `1.1` contains no statement of it — I read the page in full and
  grepped for "score", "solve", "complete candidate", and "fills in". The real owner is
  `1.2:67-68` itself. This is the exact class the brief flags (R1 → `unified-state`): the
  page resolves, the claim is not there. **The oracle/operator boundary — the one thing the
  team lead named as correct and load-bearing — currently cites a page that does not state it.**
- **`architecture.md`** (`8.7:28`). The file does not exist anywhere in the repo. Invisible
  to the checker because it is backticked, per probes B and C.
- **Cross-page ordinals that broke at the split.** `8.3:18` "the rows above" (rows are on
  `8.2`); `8.5:22,23,25` "(§2)", "of §3", "Cap 1/2/3 rows above"; `8.7:23,24,31,33`
  "§2/§3/§4/§6/§7/§10"; `8.6:44` "(§6)"; `1.2:27,85,90,93,111,133,210,248`;
  `1.5:139,177`. None of these resolve within their own page. Each needs an explicit
  `[page#anchor]` target chosen by hand — this is the largest single mechanical task in my
  scope and it cannot be automated, because the ordinals refer to sections of a document
  that no longer exists.

### One cross-scope item I could not disposition

`10.2-open-decisions.md:169` reads "(the *picks* are open item **5** above)" while the item
in question is numbered **6** at line 83; item 5 is the semiconductor-interface applicability
predicate. The same page cites "the §20.4 injectivity and algebraic-law obligations" at line
176 — the book has eleven chapters. Both are in the governance surveyor's scope, not mine,
but both are load-bearing on my rows 116 and 129: the implementation-language fact I am
recommending `forced-decisions` own is currently cross-referenced through a broken ordinal.
Flagging so the two dispositions are reconciled rather than each assuming the other is right.

### Ordering hazards for the builder

1. **Row 105 before row 124.** The Cap-1 acceptance test is labeled the "first end-to-end
   gate" but lives on `capability-slices`, not `build-verification`. If `build-order` is
   merged into `build-sequence` first, the gate set is briefly split across three pages.
2. **Rows 81–84 before anything touches `1.5`.** The operator-side content (why a neural
   operator, the failure modes, the equivariance handoff, `Learnable_Structure`) must land in
   `operator/seam` before `rationale` is edited. `operator/seam` is being built from
   `informed-operator/design/`, which is also being deleted — so both sources of the
   operator seam disappear in the same phase.
3. **Row 99 before row 100.** The consequence column depends on the value column for its
   antecedents. Delete the values only once the consequences carry their own citations into
   `reference-data/*.csv`, or the derivations become unreadable.
4. **C1 touches nine rows across five of my twelve pages.** Whichever way auditor 2 resolves
   completion-vs-evolution, rows 2, 7, 31, 44, 47, 55, 68, 81, 82, 94, and 142 are all edited
   in that pass. Do not rewrite any of those sentences during the mechanical relocation —
   move them verbatim and let the resolution pass rewrite them once.

---

### from `practice`

**The timeline's five-field schema fails on attribution, corpus-wide.** All twelve
entries name their actors only as roles — "four skeptic passes", "two adversarial
auditors", "six auditors", "66 skeptics", "three systematic passes". Not one names a
person, a model, or a tool version. Under a contract audit, "who or what produced this
finding" is unanswerable from the page for the entire record. Entry L4 additionally
disclaims its own evidence link ("the full primary-source citations are in git
history"), and eight entries state no supersession. **This is the single item in my
scope that Phase 2 cannot fix by rewriting** — the information is either in git commit
metadata or it is gone. Recommend: reconstruct attribution from `git log` authorship
and commit messages *before* the old tree goes read-only, and put the reconstruction
in front of Javier as a table, not as prose.

**Two index tables inside the timeline are live resolvers, not history.** The Wave-1
A1–A16 correction table and the gap-audit A–E section index are cited by 13 and by 17
lines respectively (4 and 9 distinct files) — and critically, **8 of the gap-audit
citations are inside data files that survive the restructure**: seven rows of
`physics/library/formulas/registry-manifest.csv`
and one row of `transport-coefficients.csv` carry `gap-audit <letter><number>` in their
provenance cells. The timeline records that these tags were orphaned once already by a
mechanical citation rewrite and had to be restored. Deleting either table orphans
provenance in the registry itself. If the log is reorganized, **grep the CSVs before
touching those two tables.**

**The block I could not confidently home: the integrator interface (disposition rows
76–79).** `10.2-open-decisions`'s "Closed decisions" carries a ~55-line present-tense
contract — the per-tier evolver hand-off, its ten manifest fields, the encoding
validity domain, and the `conserve | bound | monotone` obligation map with its
literature anchors. It is not an open decision, it is a specification, and the target
tree has no page for it. Candidates: `oracle/laws/generic-dynamics` (it is the tangent
map of the GENERIC form), `oracle/seams/` (it is a consumer-facing export like
`pino-bridge`), or a new `oracle/seams/evolver-handoff`. I lean to the third —
`pino-bridge` and `residual-machinery` are already siblings there and this is the same
kind of object. **Ask Javier; do not guess.** Related: this block is the only statement
of why `/physics` may hand off a tangent map without claiming time-evolution, which is
the exact question the plan defers to auditor 2 (§12). Losing it would make that
question harder, not easier.

**The glossary is the fix for defect 4, not a separate problem.** 73 of its 75 terms
are not a `canonical-for` topic of any page; the 98 canonical topics and the 75
glossary terms are near-disjoint vocabularies over the same corpus. Meanwhile 18 pages
own only a restatement of their own id. These are the same defect seen from two sides:
the type vocabulary (`ContentAddress`, `Universe`, `SparseSet`, `CompressionPlan`,
`CouplingChannel`, `TheoryContext`, `OneShotCert`, `Stage 1`–`Stage 5`, …) is what
those 18 pages actually own, and it is currently declared in a hand-maintained table
that no checker compares against them. **Feeding the glossary's terms into `owns:`
fixes both at once and makes the emitted glossary a byproduct.** Do this before
writing `corpus.json`'s schema, because it roughly doubles the topic count and every
`owns:` entry needs an anchor to point at.

**Traps that lose their mechanism, in order of risk.** Trap 57 (rename forwarding) is
the only one whose mechanism is deleted outright — `retired-names.csv` is its entire
content. I marked it `delete` and I was not sure; the hazard survives the mechanism
and `rename-forwarding-mechanism` asks whether anything replaces it. Trap 46 (never seed from an appendix)
loses its *object*: rewrite it positively rather than deleting it, or the surviving
half ("seed from the ledger and the CSVs") disappears with the half that became
vacuous. Trap 53 must be kept **even though it names a retired legend** — it is the
translation key for chapter 11's `Diff` cells, and mining ch. 11 without it is how
rows 12 and 106 were mis-registered the first time. Traps 45, 58 (pointing at
`audit-prompt`), 59 (pointing at `open-decisions` and `deriv-csp`) and 44 (pointing at
two deleted appendix pages) need their pointers re-aimed, not their content changed.

**Ordering hazard: the traps register must be rewritten *after* the pages it cites,
not before.** Every `enforced, [page]` claim is an assertion about another page's
contents, and one of them is already false (Contradictions row 6, trap 29). The
`enforced`/`advisory` distinction is only worth keeping if every pointer is
re-verified against the target's *text*, not merely against its existence — which is
exactly the dangling-promise class the brief flags. Budget a pass that greps each
trap's distinctive phrase in its cited target. I spot-checked twelve; one failed.

**`10.1-conventions` after the authority order is removed.** What survives is smaller
than the page suggests and is worth stating plainly so Phase 2 does not over-preserve
it: the eponym-renaming test, the canonical count phrasings, the style rules
(American English, one subject per page, the keystone exception, ATX, fenced-code
tagging, no decorated separators), and the length target. Everything else in the page
is either a rule about how an *agent* works — which belongs in `practice/agent-contract`
— or scaffolding. Concretely: `practice/conventions` becomes a short writing-style page
and `practice/agent-contract` inherits the substance. The 18 history-marker lines are
almost entirely in the frontmatter-field and checker sections, and every one of them is
a tombstone for something already deleted.

**`instructions.md` and `10.1-conventions` state the same rules twice**, in five
places I found: the twelve structure checks (`conventions:261-284` ≡
`instructions:140-155`), the three-deleted-checks paragraph, "green does not mean a
check ran" plus `check_the_checkers.py` (also stated at traps 58 and 66 — four copies),
the cyclic-graph rule, and the arity rationale (also in the timeline — three copies).
The merge into `practice/agent-contract` is mostly a deduplication, and each pair
should be diffed rather than concatenated: `instructions:165` and `traps:503` already
disagree on a count that `conventions` does not state at all.

**What I swept and dismissed.** Trap numbering: verified directly (not via the
checker) that traps run 1–70 contiguously with no duplicate or skip — 70 headings, min
1, max 70. Glossary pointers: all 75 resolve to a real page id; the failure is that
they do not resolve to a *topic owner*, which is a different claim than the one the
header makes. Changelog blocks: **zero** in my nine files — the ten corpus-wide are
elsewhere. Strikethroughs: **all five in the corpus are in `10.2-open-decisions`**
(lines 58, 60, 108, 113, 126), and all five are closed-item history. `contents.md` and
`index.md`: I found no hand-edited content in either beyond their two header rules
(disposition rows 160, 162) — the generator's output matches, so their whole content
disposition is "emit from `corpus.json`".

**Not checked, stated as such.** I did not plant defects to calibrate either checker
against my scope, so I make no claim that any defect class is *absent* from these nine
files. Every finding above is a positive observation with a locator. In particular I
did not verify that the `enforced` pointers of the 58 traps I did not spot-check land
on their rules, and I did not verify that the resolutions of the three closed
verifier-soundness gaps (disposition rows 65, 66, 68) are actually stated at the pages
this fragment names as their homes — those three targets are assertions to check, not
facts I confirmed.

---

### from `appendix-a`

**1. The inbound-citation problem is asymmetric across my three pages, and 11.3 is the dangerous one.**

- `11.1` and `11.2` are cited from canon **only through frontmatter** (`born-oppenheimer-levels`'s `depends-on`). I read `2.5-born-oppenheimer-levels.md` end to end: it never cites either page in prose. Dropping them costs two `depends-on` edges.
- `11.3` is cited **seven times in canon prose**, all from `multiscale-state`: lines 104, 292, 294, 319, 336, 406, 417, 419 — with **section ordinals** (`§1.1`, `§1.2`, `§1.5`, `§4.2`, `§4.3`, `§4.5`). Every one must be rewritten, and three of them (C6, C13, C20 — the BTE, the `φ`-is-constrained fact, the transport observables) point at content `multiscale-state` **does not restate**. If 11.3 is deleted before those are mined into `multiscale-state`, canon loses the definition of the equation its macro tier is built on. **Order matters: mine C6/C13/C20 into `multiscale-state` first, rewrite the citations, then delete.**

**2. Two dangling promises point *into* my scope, and both name a path that does not exist.**
`generic-dynamics:123` grounds the nine-regime extraction table in `physics/research/group-{A,B,C}-*.md`; `formula-registry:70` grounds registry rows 1–87 in `physics/research/` generally. `physics/research/` contains 7 files, all diamond dataset. The actual referents are `11.1`/`11.2`/`11.3` (group A/B/C) and `11.4`–`11.8`. Probe 1 confirms the checker cannot see this. Phase 2 must repoint both to real anchors or the restructure inherits the same ghost with a new path.

**3. The plan's §2 defect 5 is wrong about *why* `11.1` fails to parse.** It attributes all three YAML failures to "unquoted backtick in `title:`". True for `4.4-computational-overview.md` and `9.2-reference-battery.md`. **`11.1`'s cause is an unquoted colon** — `title: Group A — Ion Dynamics: Structural, Mechanical, Thermal` — `yaml.safe_load` raises "mapping values are not allowed here" at line 2 col 30. A checker written to grep for backticks in titles would pass `11.1`. Quoting all titles fixes all three; a backtick-specific rule fixes two.

**4. Frontmatter is outside the content-hash (probe 6), so frontmatter corruption is completely unguarded today.** Worth carrying into the new checker's design: hash the whole file or validate frontmatter structurally, but do not leave the gap.

**5. A third citation syntax exists and nothing checks it.** Beyond `[id]` (checked) and `` `id` `` (unchecked, plan defect 1), there are bare `` `filename.md` `` references. `11.2:505` cites `` `properties.md` ``; 19 more across `10.1-conventions`, `10.3-audit-prompt`, `10.5-timeline`, `8.7-build-verification`, `6.8-typed-compositions`, `6.6-named-formulas`, `6.1-canonical-vocabularies`. `8.7-build-verification.md:28` cites `` `architecture.md` `` — **there is no `architecture.md` in the tree.** Not my scope to disposition, but it is the same defect class and the sweep found it.

**6. Intra-scope duplication — mine each of these exactly once.** These three pages restate each other, sometimes with an explicit cross-reference and sometimes not:

| fact | copies | mine from |
|---|---|---|
| e-ph vertex + multi-species mass convention | `11.1:514-522` (§3.6) · `11.2:148-152` (§E.6, defers to group A explicitly) | 11.1 (A52) |
| "transport IS the optical regime in dynamical-response form" (`σ_DC = lim_{ω→0} Re σ(ω)`) | `11.2:394-396` (§O.6) · `11.3:661-663` (§4.4) | 11.3 (C57) |
| QHA vibrational free energy `F_vib` | `11.1:406-413` (§3.1) · `11.3:245-253` (§2.1) | 11.1 (A41) |
| slab surface energy `γ_s = (E_slab − nE_bulk)/(2A)` | `11.1:147` (§1.5) · `11.3:495` (§3.5) | 11.1 (A18) |
| band group velocity `v = ħ⁻¹∇_kε` | `11.2:153-154` (§E.6) · `11.3:61` (§1.1) | 11.3 (C7) |
| the long-wavelength elastic↔phonon identity | `11.1:328-333` · `11.1:511-513` · `11.1:696-697` | 11.1 §2.6 (A35) |

**7. The `Environment`-class homeless-fact pattern recurs three more times in my scope** — a symbol carrying a canon residual, with no canon definition:

| symbol | canon uses it at | defined only at |
|---|---|---|
| `S_i` (atomistic spin unit vector) | `residual-definitions:114` — `\|S_i\| = 1` is a Positivity residual | `11.2:190-197` (§M.1) |
| `Φ_{IαJβ}` (force-constant matrix) | registry rows 7, 126; `residual-definitions:137-139` | `11.1:361-375` (§3.1) |
| `η` (Green–Lagrange strain) | `typed-compositions:84` — `coord = symmetric-strain-η`; registry row 60 | `11.1:185-198` (§2.1) |
| `γ̂`'s defining decomposition (`ρ = tr_σγ̂`, `m = tr_σ[σγ̂]`) | `residual-definitions:120-129` — Hermiticity, `0 ⪯ γ̂ ⪯ 1`, idempotency | `11.2:28-40`, `:96-98` |

Registry rows 7 and 8 already **admit** the pattern in their own `Depends on` column: "D(q) from the DFPT reference solve (**unregistered input**)". Canon knows these inputs are undefined and says so in a CSV cell.

**8. The `numerical methods` sections (`§x.7`, seven blocks across three pages) are the one class I could not disposition confidently.** They mix three kinds of content: (a) genuine spec facts — basis↔sparsity structure (B16, C15, C23), symplecticity (A45), ASR-by-symmetrization (A55), the DFPT-vs-finite-difference two-path structure (A37); (b) method primitives already in `computational-methods`'s closed set of 12; (c) bare external tool names (ShengBTE, BoltzTraP2, EPW, AMSET, Octopus, Yambo, Vampire, Spirit, Quickhull, Phono3py, ALAMODE, AlmaBTE). I split (a) out into its own rows and marked all of (c) `mine` → `computational-methods#reference-implementations` **per the brief's tie-break rule, while unsure**. Canon does name codes sparsely — `almaBTE` at `accuracy-ledger:170`, `EPW` at `canonical-vocabularies:75`, `VASP` at `pino-bridge:73` and `build-verification:84` — always attached to a specific number or interface, never as an inventory. If Javier wants no tooling inventory in the corpus, delete the (c) rows: A21, A26 (partial), A37, A55, B26, B38, C23, C34, C47. **That is a scope call, not a structure call, and I did not make it.**

**9. What I swept and dismissed.**
- **Superseded values behind changelogs** (the brief's top-risk trap): **absent from Group A/B/C**. Zero numeric physical values in 12,194 words — verified by unit-pattern grep across all three files (one hit, a formula). All three changelogs record *formula* corrections, not value supersessions. I seeded nothing from these pages; the three value-shaped Contradiction rows above (C2, C3) came from comparing the appendix's *methods* to `9.1-accuracy-ledger` and the registry CSV, in that direction.
- **The retired `D3`/`D0` differentiability legend** (`11.8`): does not appear in my scope. Zero `D0`–`D4` tags in any of the three files.
- **Strikethroughs, `superseded`, `retired`, `formerly`, `no longer`**: zero occurrences outside the three changelog blocks. The only history-flavored phrase in live prose is "three historical symbols" at `11.1:15`, which is A3 — a live notation hazard, not a remnant.
- **Vacuous ownership**: confirmed for all three pages (`canonical-for` names only the page's own id). Probe 5 proves the duplicate-topic invariant *works* — so this is not a broken check, it is three pages standing outside a working check. Nothing in my scope has ever been tested for duplicate ownership, which is why rows A9, A14, A17, A31, A46, A47, A48, B7, B12, B33, B34, C12, C50, C54, C55, C58, C59 (17 `delete`-for-duplication rows) had to be found by reading rather than by running anything.

---

### from `appendix-b`

### A. Every citation that must be repointed — the complete inventory

These are mechanical rewires. Grouped by the page that must be edited, not by my page.
All line numbers are at `2af93d2`. Counts confirm the brief's figures (5 and 6 outside-ch.11
`depends-on` edges, 4 and 2 prose-citing pages).

**`depends-on` frontmatter edges into my three pages (outside ch. 11):**

| Editing page | Line | Lists | Also inside ch. 11 |
|---|---|---|---|
| `10.5-timeline.md` | 27, 28, 31 | `deriv-csp`, `deriv-defects`, `deriv-high-field` | — |
| `6.6-named-formulas.md` | 11, 20 | `deriv-defects`, `deriv-csp` | — |
| `2.4-multiscale-state.md` | 32, 33, 34 | `deriv-csp`, `deriv-defects`, `deriv-high-field` | — |
| `10.1-conventions.md` | 13 | `deriv-defects` | — |
| `10.4-traps.md` | 24, 25, 34 | `deriv-csp`, `deriv-defects`, `deriv-csp` | — |
| `6.10-properties.md` | 13 | `deriv-high-field` | — |
| `6.1-canonical-vocabularies.md` | 28 | `deriv-high-field` | — |
| `5.3-out-of-scope.md` | 15 | `deriv-high-field` | — |
| `6.9-formula-registry.md` | 17, 19 | `deriv-csp`, `deriv-high-field` | — |
| — | — | — | `11.3:12`, `11.4:12`, `11.7:12,16`, `11.8:9`, `11.6:9` all die with their pages |

**Prose citations, page by page.** These are the ones that must land on a *claim*, not just a page:

- `2.4-multiscale-state.md` — **28 prose citations**, by far the heaviest load. Lines
  76, 78, 118, 129, 139, 140, 141, 143, 144, 162, 169, 174, 178, 182, 185, 189, 198, 201,
  208, 234, 243, 244, 245, 246, 247, 256, 290, 307, 312, 314, 320, 336, 446.
  Most repoint to a claim canon *already restates* (rows 9, 14, 16, 53, 57, 61, 66, 116,
  120, 123, 128, 136, 137 above) — those citations can simply be **dropped**, not repointed,
  because the fact is present in the citing page. **Five are dangling promises** and need a
  real target: `:256` (D.1/D.4 — canon states `τ_n` only, not `n_1`/`p_1` or the σ regimes),
  `:78` and `:234` (`[deriv-csp]` E.1/E.2 — canon uses `R_ThermalCycleStability` by name
  without a definition existing anywhere else), `:308` (row 73 `τ_E` "carries both channels"
  without stating either), `:330` (`μ₀(T,N_D)` declared micro-supplied with no formula).
- `10.1-conventions.md:221` — cites `[deriv-defects] Part G.2` as the *example* of the
  cite-by-id convention. Repoint to any surviving page, or rewrite the example.
- `10.4-traps.md:304` (trap 44) and `:426` (trap 59) — both cite my pages as *evidence for a
  trap*. Trap 44's citation is historical ("the 2026-07-07 gap audit found, in
  `[deriv-defects]` B.3/B.4…") and per D1/D2 should move to `log/timeline.md` with the
  trap keeping only the present-tense hazard.
- `6.6-named-formulas.md:139` — cites `[deriv-defects] Part B`.
- `5.3-out-of-scope.md:101` — "`[deriv-high-field]` H.3 disposition, now registered here."
  Self-resolving: drop the citation, keep the registration.
- `11.6-deriv-csp.md:23,141,143,150,363` — five citations into `11.4`; both pages die.

**Non-page citations — these are the ones a page-level checker cannot see:**

- `physics/library/formulas/registry-manifest.csv:49` (row 48) — *"the Cowley-Sze form
  **deriv-defects §F.3** states normatively."* **A registry row's justification cites a page
  being deleted.** Row 48's signature was changed on the strength of this. Must repoint.
- `physics/library/formulas/registry-manifest.csv:51` (row 50) — *"the form already used in
  **deriv-csp**"*, naming the soft-cutoff relaxation. Row 50 is `D4`, and
  `6.6-named-formulas.md:105-109` requires a `D4` row's relaxation to be named in its source
  cell or the registry-build gate fails. So this is load-bearing, not decorative.
- `registry-manifest.csv` rows **105, 106, 107, 108** — Source cells `S3 (defects G.1)`,
  `(defects G.2)`, `(defects G.3)`, `(defects G.7)`.
- `registry-manifest.csv` rows **111, 112** — `S4 (non-eq H.1)`, `(non-eq H.2)`.
- `physics/library/formulas/retired-names.csv:38` — `lattice-strain-energy,(never registered
  — **see deriv-csp F.2**),2026-07-21`. Both this CSV and that page are deleted by §9;
  no action beyond confirming the routing fact (rows 54 and 60) survives.
- `physics/library/cert/reference-data/material-constants.csv:42` — the β-Ga₂O₃ `E_d`
  source cell reads *"carried from **non-equilibrium stratum H.1**"*. See Contradiction C12.
- `journal/live/specs/2026-07-21-oracle-code-spec-research-brief.md:87,182` — cites
  `[deriv-csp]`. That stratum is deleted by D13; no repoint needed.
- `journal/contents.md:144-149` and `journal/index.md:31,32,35` — regenerated (§6).

### B. Where the mass actually goes — a warning about `multiscale-state`

Of the ~120 substantive blocks in my scope, **the largest single receiver is
`oracle/state/multiscale-state`**, and it is already the page that duplicates my pages most
heavily. Roughly 25 of my `delete` rows are "already stated there." If Phase 2 lands every
`mine` row targeted at it as well, that page absorbs the defect inventory, the recombination
machinery, the surface coupling, the charge-balance closure and the slow-tier onsets on top
of what it already carries.

**Recommendation:** treat `multiscale-state` as at risk of becoming the new chapter 11 —
a catch-all whose `owns:` list is a topic dump. Consider splitting the recombination /
trapping content (rows 35–39) and the surface-coupling content (rows 24, 42, 60, 84) into
their own pages under `oracle/state/` before landing. I did not have the authority to
propose page names; flagging the load rather than deciding it.

### C. Row 85 `structure-uniqueness-CSP` — the brief's premise does not hold

My brief states that `11.6-deriv-csp` "is the derivation behind `structure-uniqueness-CSP`
(registry row 85)" and asks whether the appendix reflects the 2026-07-21 `DX → D4` retag or
still states the pre-retag reading. **Neither.** I checked directly and report it plainly:

1. `11.6-deriv-csp.md` **never names `structure-uniqueness-CSP`.** Verified by grep across
   the whole file for the row name, and for `uniqueness`, `descriptor`, `softmin`,
   `duplicate`, `de-dup`, `B10` — the sole hit is the word "descriptor" at `:60`, in an
   unrelated sentence about PINO inputs.
2. Its B.1 validity catalog has twelve residuals and **none of them is a uniqueness or
   duplicate-detection residual.** Its F.2 "Proposed as → Landed as" table has thirteen rows
   and row 85 is not among them.
3. Row 85's declared relaxation — *"softmin over the set plus a sigmoid on `(d − d_min)`
   with declared width"* — is stated in exactly two places in the repo:
   `registry-manifest.csv:86` (the Source cell) and
   `journal/live/specs/2026-07-21-oracle-code-spec-research-brief.md:88,196`. The second is
   in `journal/live/`, which D13 deletes and which the plan records has **never been swept**
   by `check_data_agreement.py`.
4. The only chapter-11 appearance of row 85 anywhere is `11.8-deriv-generator-catalog.md:166`,
   a bare catalog line carrying the **stale `D3` tag** (Contradiction C17) — and 11.8 is the
   page using the retired legend, so even that line does not mean what it appears to.

**So: row 85 is a homeless fact, and it is an MVP Cap-1 row** (`8.2-capability-slices.md:35`).
Its descriptor choice, radial/angular cutoffs, basis, kernel, uniqueness threshold and
relaxation widths are all spec-level and are owned by no page. After `journal/live/` is
deleted, the CSV Source cell is the sole surviving statement. Registered as Open question `csp-descriptor-derivation`.

One thing 11.6 *does* get right and should be credited: its differentiability legend at `:27`
is a **words-only** three-way split (`smooth` / `piecewise` / `combinatorial`) that explicitly
de-collides itself from the registry vocabulary and names the **current** post-retag spelling
`D0 | DN | D1 | D2 | D3 | D4`. **`11.6` does not carry the retired D-legend.** Whatever the
hazard is in `11.8`, it is not replicated here — but its `T0`–`T4` **cost**-tier scale *is* a
live collision (one tier deeper than the registry's `T0`–`T3`, row 167), and every tier value
in its four residual catalogs is in the local scheme. Phase 2 must translate, not copy.

### D. Checker calibration — what I verified by planting, at `2af93d2`

Per the brief's standing rule. Scratch copy of `journal/`, `physics/`, `informed-operator/`;
baseline both checkers clean; one defect at a time; scratch destroyed after.

| Probe | Planted | `check_book_structure.py` | `check_data_agreement.py` |
|---|---|---|---|
| 1 | `[deriv-defects] Part **ZZ**` (page exists, section does not) in `11.6:141` | stale-hash only — **defect not detected** | clean — **not detected** |
| 2 | diamond κ(300) `2200 → 9999` in `11.5:237`, contradicting `transport-coefficients.csv` | stale-hash only — **not detected** | **clean — not detected** |
| 3 | ` `no-such-page-xyz` ` (backticked) appended to `11.4` | stale-hash only — **not detected** | clean — not detected |
| 4 | `[no-such-page-xyz]` (bracketed) appended to `11.4` | **FIRES** — "resolves to no page" | — |
| 5 | ` `Schottky-Mott-alignment` ` (retired name) appended to `11.5` | — | **FIRES** — 2 finding classes (`retired-name`, `retired-eponym`) |

Probe 5 matters: it establishes the data checker **is** alive on chapter 11 — it is not
exempted the way `journal/live/` is (`check_data_agreement.py:69-74` includes
`journal/pages/**` and excludes `journal/live/`). It simply **does not compare numeric values
in page tables against `reference-data/*.csv` at all.** That is why Contradictions C5, C6,
C8, C9, C10 have survived in a corpus that reports clean, and it is why the 2026-06-10
re-audit clearance recorded at `10.3-audit-prompt.md:130` could be inherited without
anything objecting.

Probes 1 and 3 confirm plan §2 defect 1 and the dangling-promise class in my scope
specifically. Note the content-hash check masks nothing — probe 4 reported two problems, so
probes 1–3 genuinely produced only the hash complaint.

**Consequence for Phase 2 verification:** disposition rows carrying values (rows 20, 22, 26,
39, 40, 45, 51, 54, 55, 65, 69, 73, 74, 94, 100, 104, 108, 118, 125, 131, 142, 176, 183, 186,
190, 194, 210) **cannot be validated by running the checkers after landing.** They need either
a new numeric-agreement check or a manual pass against the CSVs. Plan §11 item 7 ("nothing was
lost… checked mechanically against the table") will report success on a page whose numbers
are wrong.

### E. Blocks I could not disposition confidently

- **Row 13 / `fermi-level-charge-balance-closure` (charge-balance closure).** I am confident it is homeless; I am not confident
  `multiscale-state` is the right owner rather than `oracle/laws/coupling-structure`. It is a
  fixed-point solve, not a state schema. Named, not guessed.
- **Row 121 (the `coupled-pde` category decision).** I dispositioned it `delete` on the
  reading that the "cross-tier macro sibling" in the nineteen-category taxonomy *is* this
  residual. I could not confirm that identification from the text of
  `3.2-residual-definitions.md` alone — `:63-65` says two of the nine EOM categories are the
  slow and macro siblings "added with `multiscale-state`", which is strongly suggestive but
  not explicit. If it is wrong, row 121 is a `mine`, not a `delete`. **Flagging because a
  wrong `delete` is the expensive error.**
- **Rows 94, 104, 157 (c-BN and h-BN).** These materials appear in every anchor table in
  `11.5` and in **no** reference-data CSV. I dispositioned them `mine` to the ledger, but
  whether c-BN/h-BN are in scope at all is a question I am not authorized to answer — the
  ledger's own residue list (`9.1-accuracy-ledger.md:269-275`) does not mention them either
  way. If they are out of scope, these rows become `delete`; if in scope, the corpus has an
  unacknowledged coverage hole on two of its seven named materials.
- **Row 100's `μ₀(800 K) ≈ 2000 × (300/800)^2.5`.** The exponent 2.5 sits inside the CSV's
  declared `T^(−1.5..−2.8)` band, so it is not a contradiction — but the base value 2000 is
  (C5). I carried the *conclusion* (devices run saturated) and not the arithmetic. If auditor
  2 resolves C5 toward 4500, the conclusion strengthens rather than breaks: higher `μ₀` means
  earlier saturation.
- **Contradiction C13 (GaN `Ξ_c`/`Ξ_v` vs `a_V`).** I could not establish whether the two
  sources use the same sign and reference conventions. I logged it rather than dismissing it
  because the ledger's neighboring entries carry two explicit **SIGN GUARD** blocks
  (`9.1-accuracy-ledger.md:229-247`) on exactly this failure mode for polarization bowing and
  pyroelectric coefficients, which suggests the corpus has been bitten by convention
  mismatches before.

### F. Two things worth doing at landing that are not disposition rows

1. **Three of my `mine` targets are new traps.** Rows 29 (`E_corr^FNV` vs `E_F` symbol
   collision), 143 (deformation-potential sign convention), 167 (`T0`–`T4` vs `T0`–`T3` tier
   collision). Also worth considering: row 126's sheet-vs-volumetric carrier-density hazard,
   which produced L5. The traps register survives and is numbered contiguously (70 entries);
   these would be 71–74.
2. **The training-staging cluster.** Rows 34, 81, 156, 179, 204, 211, 212 are seven
   independent statements, across all three of my pages, of the same unowned thing: which
   tier generates labels, which corrects them, which validates, at what cost ratio, and at
   what accuracy a cheap proxy is good enough. This is the plan's confirmed homeless fact
   (§2, training stage ordering) arriving from a completely different direction than
   `informed-operator/design/training-stages.md`. **They should be landed together, once**,
   and cross-checked against that file rather than merged blindly — the memory record
   (`n-op-training-staging`) says VASP epochs narrow the space first and oracle residuals
   guide only the last epoch, which is a *different* staging claim from the
   cheap/mid/faithful ladder in `11.4` C.6. Whether those are two views of one pipeline or
   two competing pipelines is a contents question I am not authorized to settle.

---

### from `appendix-c`

**1. The biggest single issue in my scope is a gap in the target tree, not in the corpus.**
The target structure has **no page that owns the 52 catalog observables**. The ledger owns
their *tolerances* on the same `#1–52` keys; the registry owns 132 *formulas* on a different
axis (observable ↔ registry row is **not** 1:1 — one observable can be served by several
formulas, and 45 registry rows serve no Part-C observable at all). Yet Part C is the sole home
of 52 governing equations, 52 faithful-residual expressions, ~104 named cheap-path
alternatives, and 52 typed signatures — roughly **3,000 words of irreplaceable mathematics**,
and the single largest concentration of unique content in my three pages.

I have targeted rows 9, 10, 11, 16 at a proposed new page **`oracle/registry/observable-catalog`**.
This is an addition to the structure Javier must approve at the Phase-1 gate; I did not have
authority to invent it silently, and folding it into `accuracy-ledger` would put governing
equations on a page whose stated job is tolerances. **Flagging rather than deciding.**
The alternative worth putting to him: extend `data/registry-manifest.csv` with
`equation` / `residual` / `cheap-path` columns and let the 52 observables live as a keyed view
over it — which is what `live/specs/2026-07-21-oracle-code-spec-research-brief.md` R1.0 already
proposes ("a per-row skeleton — equation / method / residual / tolerance / provenance slots").
Note R1.0 states this math "lives in `physics/research/` catalogs"; **that is false** —
`physics/research/` contains only the two diamond VASP datasets. It lives here and nowhere else.

**2. Ordering hazards — three, all of which lose data if run in the wrong order.**

- **`retired-names.csv` must outlive the mining of `11.8` §1.2 and `11.7` Part C.** The plan
  (§9) deletes it. But `11.7`'s vocabulary list and `11.8`'s table are keyed to *literature*
  names (`fowler-nordheim`, `richardson-dushman`, `padovani-stratton`, `kane-zener`,
  `makov-payne-correction`, `freysoldt-correction`, `lany-zunger-correction`,
  `Schottky-Mott-alignment`), and only that CSV maps them to the behavior-named registry rows.
  Delete it first and the mined prose becomes unresolvable. Worse: `makov-payne-correction`
  maps **ambiguously** — "`-isotropic-cubic` (row 31) **or** `-isotropic-general` (row 89) — the
  old name was ambiguous across both" — so that one needs a human decision, not a lookup.
- **`registry-manifest.csv` row 48's `Source` cell cites `deriv-generator-catalog §6`.** A data
  file citing a page that is about to be deleted. Nothing checks CSV→page citations, so this
  will dangle silently. Re-point it when row 60 lands.
- **`residual-machinery:68` must be repaired *before* `11.8` is deleted**, not after — it is
  currently the only pointer from canon to the layer DAG's definition, and it is already broken
  (L-8). If the DAG is not mined first, the `layer : 0..6` field becomes undefined in the new tree.

**3. Checker calibration — what I actually verified, and what I did not.**
Per the brief, I did not trust the green run. In a scratch copy under the session scratchpad
(the corpus was never touched; `git diff --stat journal/pages/` is empty):

- **Probe A** — replaced `residual-generator-catalog §2` with `totally-nonexistent-page-xyz §2`
  at `7.2-residual-machinery.md:68`, restamped the content-hash, re-ran
  `check_book_structure.py --check` → **`book structure OK`, 58 pages, 0 problems.** The
  bare/backticked dangling-id class is completely invisible. This is why the real defect survived.
- **Probe B (control)** — inserted `[totally-fake-page]` as prose on the same page →
  **`FAILED: reference [totally-fake-page] resolves to no page`.** So the checker is live and
  the blindness is specific to the unbracketed syntax, exactly as plan §2 defect 1 predicts.
- **Not checked:** whether `check_data_agreement.py` compares the appendix `Diff`/`Tier` columns
  against `registry-manifest.csv`. It reports clean while 19 such cells disagree (R-2), which
  strongly suggests it does not — but I did not plant a probe to confirm, so I am not claiming it.
- **Not checked:** `out-of-scope-limits-coverage`, whether all 12 of Part F's limits appear in `out-of-scope`.

**4. Rows I could not disposition with confidence.**

- **Row 14** (Part C high-T notes) — these overlap the ledger's rows 1–52 partially and
  unevenly. I marked `mine` per the brief's tie-break rule, but the real instruction to Phase 2
  is *merge per-observable, do not bulk-copy*; a bulk copy will duplicate ~20 clauses the ledger
  already carries better.
- **Row 50** (`Generate`/`Validate`/`Import` as the three `/physics` exports) — `pino-bridge §2`
  clearly owns `Import`; I did not confirm whether it names the other two. If it does, this is a
  `delete`.
- **Row 54's rationale clause** ("bundles are physical-domain cohesion units for the unified
  state vector, not residual-category bins") — I dispositioned the block `delete`, but that one
  sentence is a good statement of *why* the bundle axis exists. Check `observable-bundles`; if
  it is absent there, promote the clause rather than losing it.
- **Row 86** (the operad's compile-time soundness does not survive a host swap) — a real
  structural observation, but it is stated only in terms of Haskell→OCaml/Julia and would read
  as advocacy for a pick that is now reopened. `delete` under the no-mandate rule; someone
  should confirm that is the right call rather than rewriting it host-neutrally.

**5. What the three pages are, in one line each, for the builder.**
`11.7` is a **content-rich page in a dead container** — most of its unique value is live
mathematics and it is the most expensive of the three to lose. `11.8` is **half dead weight,
half load-bearing** — its 89-row table is fully superseded by a CSV that is better in every
column, while §2.2 and §3.3–§3.5 hold facts canon actively depends on and does not state.
`11.9` is **mostly advocacy for a decision that has since reopened** — its durable residue is
about five paragraphs: the requirement list, the seam data contract, the golden test, the
hardware split, and one trap.

**6. Vacuous ownership confirmed on all three pages.** `deriv-observable-catalog`,
`deriv-generator-catalog` and `deriv-language-study` each declare `canonical-for` naming only
their own id (`11.7:6-7`, `11.8:6-7`, `11.9:6-7`) — three of the eighteen. None of the three is
inside the duplicate-topic invariant, which is precisely how `11.8` could carry a full parallel
copy of the formula registry for months without any checker noticing the duplication.

---

### from `strata`

**Ordering hazard — consume `retired-ids.csv` before deleting it.** It is deleted under D1/§9,
and it is simultaneously the only resolver for live retired ids in this scope: rows 16
(`arch-11-residuals`, `arch-18-open-decisions` in `training-stages.md`), 40
(`impl-07-residual-factory` → `residual-machinery`, which is the whole reason Part G is a
delete), and 78 (`arch-xx`/`impl-xx` named as the evolver memo's citation convention). Resolve
every one against the CSV, rewrite the citations, *then* delete. Same for `retired-names.csv`
and the `DX → DN` rename. If the deletion lands first, rows 16 and 40 become unresolvable and
the dispositions above cannot be executed.

**The `§11.4.1` coordinate needs two fixes, not one.** `training-stages.md` cites
`arch-11-residuals §11.4.1`. The id retired to `residual-definitions`, *and* the section
renumbered — the gating fractions are at `§4.1` ("Curriculum gating defaults",
`3.2-residual-definitions.md:245`). Mapping the id alone produces
`residual-definitions §11.4.1`, which resolves to nothing. Under the plan's anchor discipline
this becomes `[residual-definitions#curriculum-gating]`.

**Grep hazard — three tokens on plan §11's kill-list are load-bearing in this scope.**
Verification step 3 demands zero corpus-wide hits for `content-hash`, `retired`, and
`superseded`. But seam **R7** (row 11) legitimately requires that every `Learnable_Structure`
instance expose "one stable content hash" — that is an *operator instance* hash, unrelated to
the deleted page-frontmatter stamp. A blanket grep-and-delete kills a seam requirement. Rows
52, 100, 114, 115 and 116 are similarly at risk from a naive sweep for `not`/`never`-shaped
warning prose. Do the sweep by reading, not by regex.

**`residual-loss-methodology.md` Part G must be diffed, not assumed.** I marked it `delete`
because `impl-07-residual-factory` landed as `residual-machinery`. I did **not** verify that
`residual-machinery` carries everything Part G proposes — the `residual-sample-policy` record
and the `pino-training-step` sketch in particular. Diff the two before deleting; if
`residual-machinery` lacks the sampling-policy type, that part is a `mine`, not a `delete`.
This is the one row in this fragment where a wrong `delete` would lose a typed interface.

**Part C's methods must be re-keyed on the way in.** Rows 29 and 30 (Gumbel-Softmax /
straight-through / surrogate-continuous; discrete adjoint / DFPT / RTA) are keyed to this
file's own D-numbering, in which `D4` means non-differentiable and `D2` means adjoint-required.
Canon's `DN` is the non-differentiable tier and canon's `D4` is *relaxed*. Moving these blocks
without re-keying reproduces the `11.8` legend trap in a new location.

**Three things exist in exactly one place and will be easy to lose.** The invariant battery
(row 145), the strain transpose trap (row 146), and the H₂ coverage analysis (row 142) are all
in `prep.md`, an **untracked** file inside a container being deleted. None is cited by anything
that would notice their absence. The stage ordering (rows 17, 150) has two homes and both are
untracked. If Phase 2 works from `git ls-files`, all four vanish silently.

**`journal/tools/` is four files, not three, and `corpus_root.py` is the one to carry
forward.** It is not a checker; it is the guard that makes a checker's green result
*addressable* (`commit · path`) and refuses to run inside `.claude/worktrees`. Plan §"Phase 2"
requires that two trees both claiming to be the corpus be structurally impossible — this file
is the existing half of that. Rebuild the three checkers; **port this one**.

**Preserve the negative checker knowledge.** `check_data_agreement.py`'s "WHAT THIS TOOL
DELIBERATELY DOES NOT CHECK" section records three checks that were built, measured against the
corpus, and removed for cause (tolerance-ledger exhaustiveness fired 48× on correct prose; bare
`§` self-references are shaped identically to `Öttinger 2005 §5.3`; legend scoping cannot
distinguish `D0`-as-charge-state from `D0`-as-diff-tag). A rebuild that does not inherit this
will rebuild the noise and teach the reader to skim — `[traps] §69`. The same applies to
`check_the_checkers.py`'s `GUARD_PROBES` interlock, which keeps the published probe count equal
to the calibrated one.

**Rows I could not disposition confidently, named.**

- **`figures/STYLE.md` (row 173).** Every artifact it governs is deleted by decision, so by the
  letter it is dead scaffolding; but it is a coherent, reusable design vocabulary with no
  dependence on the specific figures. I chose `mine` per the brief's tie-break and flag it as
  the single most likely wrong `mine` in this fragment. One question to Javier settles it: will
  any figure ever be redrawn?
- **`physics/research/diamond-defect-corpus/index-of-all-runs.tsv` (row 123).** A run manifest
  with no companion prose, no provenance, no licensing note, and no citation from anywhere in
  my scope. It may be live MVP feedstock or it may be a stray. I moved it rather than delete it
  because a wrong delete on a dataset manifest is unrecoverable, but it needs an owner.
- **`residual-loss-methodology.md` Part D vs the registry `Tier` column (row 32).** Possible
  duplication that I could not settle without reading the registry's Tier semantics against
  Part D's cadence semantics. If they agree, Part D's table is a delete and only the sampling
  strategies survive.
- **The two curriculum schedules (Contradictions row 6).** I could not determine whether these
  are one schedule described twice or two schedules sharing endpoints. It matters for siting:
  one target if the former, two if the latter.

**A dangling file reference inside the research suite.** `read-me-first.md` lists `CHANGELOG.md`
in "The suite" table and again in warning 5 ("`CHANGELOG.md` is the exact inverse map… restoring
[VASP filenames] is a prerequisite for any restart"). No such file is in
`physics/research/diamond-stretch-and-skew-sweep/`. Either it lives only on `/Pool` — in which
case say so, as the header does for the data itself — or the rename map is lost, in which case
the archives cannot be restored to VASP-canonical filenames and the dataset is unusable for any
restart. Worth resolving before the dataset is relied on for the MVP acceptance test.

**One stale pointer aimed *into* this scope from canon.** Plan §2 defect 2 records that
`10.3-audit-prompt.md` directs readers to `physics/research/*` for physics that moved to
`pages/11-` long ago. Since `physics/research/` moves to `data/` under my rows 111–123 and
`pages/11-` is being dissolved, that pointer needs rewriting to whichever page ends up owning
the derivation — not to `data/`, which will hold only the dataset and its reading guide.

**What I swept and dismissed.** I read every markdown file in scope end to end rather than
sampling. Blocks I considered and deliberately did *not* raise as findings: the evolver memo's
`[product]`/`[computational-overview]` bracketed-id citations (they resolve; they are simply
unchecked, which is already recorded as defect 1); the seeding spec's `[verified]` /
`[audit-pin]` tag convention (a drafting device, fully resolved by the audit, no live referent);
`STYLE.md`'s SVG-level guidance on `<path>` vs `<line>` (asset-specific, dies with the assets
even under row 173's `mine`); and the talk script's slide-to-figure mapping (indexes deleted
files). I did **not** verify that any value in `physics/library/cert/reference-data/*.csv`
agrees with `9.1-accuracy-ledger` — that is a data-agreement question and the checker covers
that surface; per the brief I stayed on structure.

