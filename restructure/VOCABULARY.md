# The vocabulary register — Phase 1.5

Every corpus-invented name, its senses, and what it becomes under D18 (*spell
everything out*). Nothing here is applied; this is the map that goes to Javier for
sign-off before any page is written.

---

## 1. `S1`–`S5` — RECOVERED

The registry's `Source` column carries this on all 132 rows. **Canon defines it
nowhere.** The only gloss was `11.8-deriv-generator-catalog:20`, a page banner-marked
as a retired snapshot whose *other* legend (the `Diff` column) is known-wrong — so it
could not be trusted.

Recovered instead from two independent paths that agree:

- **From usage.** Source cells for four rows read `defects G.1/G.2/G.3/G.7` and two
  read `non-eq H.1/H.2`. `11.4-deriv-defects` runs sections A–I and
  `11.5-deriv-high-field` runs A–J, so these are within-page section references.
  → `S3` = defects, `S4` = non-equilibrium.
- **From git history.** Commit `dfad72b` *"S1-S7 research integration"* migrated
  *"7 current-session UWBG research streams"*, and `IMPLEMENTATION-PLAN.md:20` at that
  commit names each one.

The two agree exactly on S3 and S4, which is what licenses trusting history for the
rest.

| Tag | Original research stream | Lives now as | Rows |
|---|---|---|---|
| `S1` | `uwbg-observable-catalog.md` | `11.7-deriv-observable-catalog` | 38 |
| `S2` | `csp-heterostructure.md` | `11.6-deriv-csp` | 33 |
| `S3` | `defects-surfaces-interfaces.md` | `11.4-deriv-defects` | 29 |
| `S4` | `non-equilibrium-high-field.md` | `11.5-deriv-high-field` | 28 |
| `S5` | `residual-loss-methodology.md` | `informed-operator/design/` (still live) | 3 |
| `S6` | `residual-generator-catalog.md` | `11.8-deriv-generator-catalog` | — |
| `S7` | `amendment-s7-source.md` | deleted; folded into the spec | — |

The registry uses only `S1`–`S5` because **`S6` is the reconciliation of the other
five** and `S7` was an architecture amendment, not a formula source.

> Worth recording: `11.8`'s banner calls it *"a Historical S1–S5 reconciliation
> snapshot"*. It **is** S6 — the reconciliation — and never says so. A document that
> does not know its own name is the same defect class as a page with a vacuous
> ownership claim.

### Proposed spelling

| Was | Becomes |
|---|---|
| `S1` | `observable-catalog` |
| `S2` | `crystal-structure-prediction` |
| `S3` | `defects-and-interfaces` |
| `S4` | `non-equilibrium-high-field` |
| `S5` | `residual-loss-methodology` |
| `extension` | *(unchanged — already English)* |
| `topology atlas` | `topology-atlas` *(hyphenated for consistency)* |

Combinations spell out too: `S1+S3` → `observable-catalog + defects-and-interfaces`.

**The column already proves this works.** Two of its seven values — `extension` and
`topology atlas` — are English today and sit beside the serials without trouble. The
serials are the anomaly, not the words.

**Consequence for the checker.** `check_data_agreement.py` vocabulary-checks the
`Bundle`, `Tier`, `Diff` and `Path` columns and **skips `Source`** — which is how an
undefined vocabulary survived on 132 rows. Once the values are named, `Source` joins
the column-vocabulary check.

---

## 2. The remaining tag families

Recovery status per family. Names are proposed only where the meaning is established.

| Family | Status | Notes |
|---|---|---|
| `D0`–`D4`, `DN` | **named** (D17) | `read · direct · adjoint · fixpoint-adjoint · relaxed · none` |
| Layer `1`–`3` | **named** (D17) | `substrate · one-shot-dressing · iterative-dressing · property-machinery`; Layer 3 is the operator **library**, never a layer |
| `S1`–`S5` | **named** (§1 above) | recovered from two agreeing paths |
| `T0`–`T3` | needs naming | meanings are stated in `6.9-formula-registry:102-104`; **but three incompatible legends exist** — registry, generator-catalog, and `informed-operator`, the last unbannered. Reconcile before naming. |
| `B1`–`B11` | needs naming | bundle names already exist in prose at `6.1-canonical-vocabularies:153-165`; this is transcription, not recovery |
| `C1`–`C7` | needs naming | cluster names exist at `4.3-representation-substrate:133-139` |
| `L1`–`L4` | needs naming | BO level names exist at `2.5-born-oppenheimer-levels:40-55`. **Note the `L1` trap:** it is simultaneously a BO level and a registry `Bundle` value — the collision that corrupted four rows (`traps §70`) |
| `P0`–`P2`, `P1`/`P4` | **dies** | audit priorities and a retired coupling family — scaffolding under D1. **`P3` at `3.3-coupling-structure:579` is already dangling** and must be resolved or deleted, not carried |
| gap-audit `A#`–`E#` | **dies** | audit findings are history under D1. But they are **embedded in registry `Source` cells** (`extension (2026-07 gap-audit B1; …)`), so removal touches the canonical CSV, not just the timeline |

---

## 3. Overloaded words — proposed resolutions

Ranked by blast radius. Each needs one sense; the others get a different word.

| Token | Senses | Proposed |
|---|---|---|
| **`coverage-mask`** | axis-tuple coverage · per-sample applicability · label-presence-per-source | **three names.** They multiply into one loss; conflating them is wrong-and-green. Suggest `axis-coverage` · `applicability-mask` · `label-presence`. Two of the three live in files being rewritten anyway |
| **`graph`** | `PhysicsGraph` (DAG; topological order **is** evaluation order) · the page graph (**cyclic**; must never be closed over) | keep `PhysicsGraph` qualified always; the page graph becomes the **page index**, since under the new structure it is emitted, not authored |
| **`source`** | `FormulaRecord.source` (a provenance citation) · `ResidualGenerator.source` (closed enum `Model \| DFT-Battery \| …`) | `provenance` for the citation; `compared-against` for the enum. Two records the factory reads together must not share a field name |
| **`tier`** | StateTier · cost tier · dressing tier · build tier | `tier` reserved for **StateTier** (micro/slow/macro). Cost tiers get their spelled-out names; dressing tiers already renamed; build `Tier-1/2` → `stage` of the build order |
| **`layer`** | dressing Layer · Layer-0 typeclasses · `layer : 0..6` DAG field · physical/epitaxial layer | `layer` reserved for the **physical** sense (it is real physics). The DAG field becomes `depth`; dressing layers already renamed; Layer-0 typeclasses → `typeclass-alphabet` needs no number |
| **`slot`** | state slot · residual output slot · encoding slot | `slot` reserved for **state slot**. Others: `residual-key` (already exists) and `encoding-choice` |
| **`cell`** | unit cell · mesh cell · CSV table cell · applicability cell | `cell` reserved for the **crystallographic** sense. `mesh-cell` always qualified (the type is already `MeshCell`); table cells are `field` in CSV context |
| **`path`** | `Path` CSV column (anchor class) · hot path · read/write path · `path-search` method · k-path · file path | the CSV column is renamed — it is **denied at five sites and documented at zero**, which is the corpus telling us the name is wrong. Suggest `anchor-class`, which is what all five denials call it |
| **`kernel`** | compiled artifact · physics operator (`CollisionKernel`, `ResponseKernel`) · `KernelExt` | `kernel` reserved for the **compiled artifact** (it carries the file hash). Physics kernels stay qualified, as they already are |

Lower blast radius, same treatment: `channel` · `field` · `stage` · `phase` ·
`basis`/`Wannier` · `frame` · `target` · `class` · `bundle` · `axis` · `wave` ·
`seam` · `gate` · `block`/`Form`.

**Checked and rejected as false positives:** `universe`, `key`, `witness`, `identity`,
`node`, `record`, `map`, `view`, `plan`, `mask`, `policy`, `version`, `budget`.

---

## 4. One incidental finding

`10.3-audit-prompt:96` cites `` `uwbg-observable-catalog` ``, recorded in the plan as
"an id that does not exist." It is more specific than that: **it was a real file** —
`physics/research/uwbg-observable-catalog.md`, research stream S1 — deleted when the
research stratum was folded into `pages/11-`. So it is a stale *filename*, not an
invention. Still a dangling reference, and it still resolves to nothing; but the origin
is now known, which matters because the same class may affect other citations that
predate the fold.
