# Oracle Interface — Research Request (I0–I2)

> Research request, 2026-07-22. A spec, not an audit: it tracks current truth
> and is rewritten as units close (`conventions`). Its citations are swept by
> `journal/tools/check_data_agreement.py`, whose surface this document's landing
> extended to `journal/live/specs/` — see §8.

---

## 1 Goal

Close the input side of the oracle's interface to specification depth: what an
`Environment` *is*, what a state *looks like on the wire*, and what
"evaluate at these points" *means per slot*.

This is a sibling to `journal/live/specs/2026-07-21-oracle-code-spec-research-brief.md`,
not a replacement. That brief researches the oracle's interior — formulas,
pipeline stages, substrate, cert. Its G9 unit covers the outward seams
(`Validate` / `Import` / `dynamics`) as *contracts*. Neither reaches the shape
of the values those contracts carry.

## 2 Scope

**In:** the three units below, all oracle-facing.

**Deliberately out, and named so the absence is accounted for** rather than
read as covered:

- **I3 — the operator's input side.** The seam contract in
  `informed-operator/design/learnable-structure-requirements.md` specifies what
  `Learnable_Structure` *emits* and what conditions it, and never what it
  consumes. Crystal identity appears in no requirement.
- **I4 — time semantics at the seam.** R4 names a query time; `/physics` holds
  no trajectory.
- **I5 — supervision coverage per slot.** Which slots the supervised stage
  actually constrains.

Those are genuine open design, not consolidation, and they want their own
request once I0–I2 have fixed the vocabulary they would be written in.

## 3 Settled foundation — constraints, not research targets

Do not reopen these; specify against them.

- The compiler's input is the triple `PeriodicityStructure` / `SiteDecoration` /
  `Environment` (`crystal-inputs`). Its semantic model is CIF content plus an
  environment record (`product §3`).
- The per-call input is the 7-tuple `x = (h, R_I, P_I, Π_h, Z_I, γ̂, A)`
  (`unified-state`) plus `env`, `request` and `gradient` (`pino-bridge §1`).
- Slots are a closed `StateComponent` vocabulary addressed by dense ordinal, not
  by symbol (`representation-substrate §3`).
- `γ̂`'s encoding is a Stage-4 choice over `Basis × Form`; the diamond MVP is
  committed to `(Reciprocal, BlockDiag)` (`gamma-hat §1`, `gamma-budget`).
- A kernel is specialized to one identity tuple; the runtime `env` argument
  varies within a stamped validity box (`product §2`).
- `/physics` is scorer-only. Nothing accumulates; no slot has a history
  (`gamma-hat §2`).

## 4 Why this is upstream of R1.1

The 2026-07-21 brief names R1.1 — the diamond MVP formula set to code depth —
as its "do first." Every one of the registry's 132 substantive formulas carries

```
applicability : (Crystal, Environment) → Bool
```

(`named-formulas`), and applicability is required to be first-order decidable at
registration. `multiscale-state §12` makes **field presence** the firing
condition for the harsh-environment predicates. So decidability is a claim about
a record whose fields have never been enumerated.

R1.1 cannot be specified to code depth against an argument type that does not
exist. I0 is the unblocker; it is also the least interesting of the three, which
is worth saying plainly rather than dressing up.

## 5 The research program

### I0 — The `Environment` record

**Objective.** Produce the closed field schema, and assign every field to the
structural / swept partition.

**Why it is not already answered.** No page claims `Environment` in its
`canonical-for`. `crystal-inputs` carries a prose list with no types;
`multiscale-state §12` carries a five-row table covering only the
harsh-environment *additions*. Meanwhile the type appears in signatures across
canon — every registry row's `applicability`, the `ResidualGenerator`
applicability field (`residual-machinery §1`), several property templates
(`property-templates`), and `Validate` itself. Seam requirement R4 obliges the
operator to accept it as "named, typed conditioning channels."

**Produce, per field:** name · type · unit · cardinality (scalar, vector, or
function-valued) · structural-or-swept · required/optional · default · the
consumers that read it.

**Two things the schema must settle, not merely record:**

1. **The structural / swept partition.** `compose-time-pipeline §6` keys the
   kernel cache on `(Periodicity, Decoration, Environment-structural)` and calls
   scalar environment parameters runtime inputs. Which field falls on which side
   has never been assigned. It is not cosmetic: a structural field misfiled as
   swept silently reuses a kernel outside its envelope, and a swept field
   misfiled as structural forces a recompile per temperature point and destroys
   the sweep the validity-window machinery exists to serve
   (`applicability-classifiers`).
2. **Optionality is semantic.** Because presence fires predicates
   (`multiscale-state §12`), "optional" is part of the type, not a convenience.
   An absent field and a field present at zero must be distinguishable.

**Note for whoever takes this.** `vibration_spectrum` is a power spectral
density over 100 Hz–10 kHz — the only function-valued member of an otherwise
scalar record. Record it as such; what it means as a conditioning channel is
I3's problem, not this unit's.

**Done when** a schema table exists, one page owns it via `canonical-for`, every
field traces to at least one named consumer, and every `Environment`-typed
signature in canon type-checks against it.

**Deps:** none. *Consolidation, not research.*

### I1 — The state wire schema

**Objective.** A per-slot serialization contract for the 7-tuple.

**Why it is not already answered.** `unified-state` records *mathematical*
types — `h ∈ GL⁺(3,ℝ)`, `R_I ∈ ℝ^{3N}`. `computational-overview §3.1` records
containers and memory layout. Neither records dtype, unit, or index order.
Seam requirement R1 obliges emitted candidates to match "per-slot array shapes
and layouts, units, and the gauge conventions recorded there," pointing at
`unified-state` — a forward reference to a table that was never written.

This is not only an I/O concern. R5 requires bitwise-deterministic emission so
content-addressed caching holds, applying the float normalization of
`representation-substrate §4`. The wire form is therefore load-bearing for
identity.

**The hard case is slot 6.** `γ̂`'s shape is not a property of the state type at
all — it is an output of the Stage-4 `CompressionPlan` (`gamma-hat §1`). For the
MVP slot this is `N_k` blocks of `N_PW × N_b` complex doubles, never the dense
`N_PW × N_PW` form (`computational-overview §3.2`). So slot 6's wire shape is
parameterized by compile-time choices: plane-wave cutoff, band count,
irreducible k-count.

**Produce:** per slot — dtype · unit · index order · gauge or sign convention;
for `γ̂`, shape as a function of the `CompressionPlan` slot; and an explicit
statement of which of these the *state type* fixes versus which the *compiled
kernel* fixes. Repoint R1 at whatever ends up owning the table.

**Done when** an engineer can round-trip a candidate state with no further
design decision, and the float-normalization rule is stated at the boundary
rather than inferred from the substrate page.

**Deps:** none. *Mostly consolidation; the `γ̂` parameterization is the one part
that is not.*

### I2 — The query domain per channel

**Objective.** Define what a query coordinate is for each slot under seam
requirement R2, and state the scope of the discretization-invariance claim.

**Why it is not already answered.** R2 is the seam's most load-bearing
requirement: given per-channel lists of query coordinates, return that channel's
values at exactly those points — emission on a fixed internal mesh with
caller-side interpolation does not satisfy it. That is well-posed for slots
carried as fields over a domain: `A` on its grid, the macro fields on the
`DeviceMesh` of `multiscale-state §7.1`. It is not obviously well-posed for
`R_I` and `P_I`, which are a point set indexed by atom rather than a field. And
it is genuinely unresolved for `γ̂`: the query domain is plausibly the k-point,
but each block's interior is `N_PW × N_b` in a plane-wave basis fixed at compose
time. A basis index is not a coordinate anything can be queried at.

**The tension to resolve, stated concretely.** `rationale` claims one operator
must transfer across meshes and supercell sizes. If slot 6's emission width is
set by the compiling kernel's cutoff, one trained operator cannot serve two
oracle-files at different cutoffs. Three ways out, and the unit must pick one:

- the cutoff joins the operator's identity, and therefore its R7 content hash;
- slot 6 gains a basis-independent emission form, with the projection onto the
  kernel's basis owned by the seam;
- the transfer claim narrows to the slots where it actually holds, and says so.

**Produce:** a per-slot table — query domain · coordinate type · what
"evaluate at points" means there; the `γ̂` resolution; and the
discretization-invariance claim restated with its scope attached.

**Done when** no slot's reading of R2 is ambiguous, and the transfer claim
carries a stated scope rather than a bare assertion.

**Deps:** I1. *Genuine design research — the only one of the three.*

## 6 Terminal deliverable

Three fragments of the code specification, in the structure the 2026-07-21 brief
already defines for it:

| Unit | Feeds |
|---|---|
| I0 | §5 item 3 (type/interface layer); unblocks R1.1 |
| I1 | §5 item 6 (runtime, wire formats); constrains R8.2 |
| I2 | §5 item 8 (consumer seams); constrains R9.1 |

Each is complete when an engineer can implement against it with no further
research and no open design question — the same bar the parent brief sets.

## 7 Sequencing

I0 and I1 are independent and can run concurrently. I2 needs I1's slot table
before it can say what a coordinate indexes.

I0 and I1 are consolidation passes over material canon already holds in
scattered form; they are in a research request because the scatter is what made
them invisible, not because the answers are unknown. I2 is the only unit that
can come back with "we do not know yet." If it does, a bounded deferral with a
stated scope is an acceptable result — an unscoped transfer claim is not.

## 8 Conventions this document is held to

`check_data_agreement.py` now sweeps `journal/live/specs/`. It did not when this
document was drafted: its surface comment exempted all of `journal/live/` as
"frozen work product," which lifted the `live/audits/` rationale one directory
up and contradicted `conventions` — specs are explicitly *not* frozen. Research
specs are where agents write, so that was the exemption that cost the most.
Extending the surface cost two findings across the three specs then present.

What the sweep does **not** cover, and is therefore held by discipline:

- `check_book_structure.py` still walks only `journal/pages/`, so `[id]`
  resolution and the no-line-number rule are not enforced here. Cite by `id`,
  inline as `[physics-graph]` or with a bare-ordinal section coordinate as
  `compose-time-pipeline §4`. Pages carrying no numbered headings —
  `crystal-inputs`, `unified-state`, `gamma-budget` — are cited bare. Never by
  display tag, never by file path for a page, **never by line number**.
- Files with no `id` — `journal/live/`, `journal/tools/`, the CSVs under
  `physics/library/`, `informed-operator/design/` — are cited by path.
- Retired **ids** have a map and no checker.
  `physics/library/formulas/retired-ids.csv` records the 2026-07-22 renaming of
  the `arch-NN` / `impl-NN` serials; nothing reads it, so an old id will not be
  caught for you. Retired formula *names* are swept; ids are not.
- A bare `§` self-reference is deliberately unchecked — `Öttinger 2005 §5.3` is
  shaped identically to a corpus coordinate, so the check was built, measured
  against the corpus, and removed rather than left to cry wolf.
- The six whole-vocabulary count phrasings are checked strictly. Phrase any
  subset or delta so it cannot collide.
- American English. ATX headings. Bare code fences for pseudo-syntax.

## 9 Source index

**Canon, by id:** `crystal-inputs` · `unified-state` · `gamma-hat` ·
`gamma-budget` · `multiscale-state` · `pino-bridge` · `residual-machinery` ·
`compose-time-pipeline` · `representation-substrate` · `applicability-classifiers` ·
`named-formulas` · `property-templates` · `capability-slices` · `product` ·
`rationale` · `computational-overview` · `open-decisions` · `conventions`.

**Outside the book, by path:**
`informed-operator/design/learnable-structure-requirements.md` (seam
requirements R1–R8, O1–O2) ·
`journal/live/specs/2026-07-21-oracle-code-spec-research-brief.md` (the parent
brief) · `physics/library/formulas/registry-manifest.csv`.

**External themes:** array/tensor interchange and wire formats; units and
dimensional-analysis type systems; IEEE-754 canonicalization for content
addressing; discretization-invariant operator learning and its
basis-dependence limits.

## Changelog

- **2026-07-22.** Written. Scope fixed at I0–I2 (oracle-facing) with I3–I5
  named and deferred. Drafted outside the book pending the research-standards
  revision, then landed once it settled — and landing it extended
  `check_data_agreement.py`'s surface to `journal/live/specs/`, which had been
  exempt on a misreading of `conventions` (§8).
