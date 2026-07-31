# Completeness of what is stated

Not *"is a topic missing"* — that is auditor 3. This asks: **is what the corpus already
states fully stated?** A formula with no validity range, a value with no uncertainty
convention, a tag that resolves to nothing.

**The reframing that made this sweep possible.** The corpus is **structurally complete
everywhere**: the registry manifest is 134 rows at full 9-column arity with zero blank
cells, and the five reference-data files are 179 rows with zero blank cells. Nothing is
empty. So structural sweeps find nothing and prove nothing — **every real completeness
defect here is semantic: a cell that is filled but does not carry what its column
promises.**

Each sweep below ships with controls. Counts are published with the rule that produced
them.

---

## What this sweep killed first — two of its own premises

Recorded before the findings, because the plan that authorised this work asserted both as
measured defects and **both are wrong**. The corpus is correct on each.

**The 24-vs-17 tolerance gap does not exist.** 25 tolerance-shaped symbols appear across
`journals/`, against a 17-row tolerance ledger. That looked like eight residuals governed by
nothing. It is not: `cert-obligations.md:127-128` **explicitly declares** that seven of them
are *physical times, not tolerances* — the carrier lifetimes, the polar-optical and
intervalley scattering times, the hopping and alloy-scattering times — and that a token in
that family "is a tolerance only if it appears in the table below." 17 ledger rows + 7
declared physical times + the generic placeholder = 25. **All accounted for. Zero undefined
tolerance names.**

**But the disambiguation is itself the defect**, and it is recorded as finding 6 below: that
paragraph has to exist only because the tolerances are named with symbols instead of English,
which is what the corpus's own vocabulary rule forbids.

**The uncertainty column does have a declared convention.**
`reference-battery.md:82-99` declares it precisely: an absolute value in the Value's units
is a one-sigma linear band; `×N` is a log-scale band with `σ_ln = ln N`; `unbounded` means
no constraining uncertainty exists; and a bare `—` means *not yet assigned*, explicitly a
different state from `unbounded`. The 78 distinct value *shapes* I first measured collapse
to four declared encodings.

**And its enumeration holds.** `reference-battery.md:96-99` claims the remaining `—` cells
are *exactly* the declared `UNSEEDED` rows, the gated alloy-bowing row, the alloy
interpolation rule, and the gallium-nitride breakdown-field slope. Measured: **6 `—` rows,
all six mapping to those four categories.** Clean verdict, earned.

---

## Finding 1 · The canonical data artifact is written entirely in the retired vocabulary

**Severity: high · Confidence: certain · Mechanical**

The corpus's central rule — *everything invented here is spelled out in English; `direct`
and `adjoint` are names, `D1` and `D2` are not* — is machine-checked across `journals/` and
**was never applied to `data/`.**

`agent-contract.md` declares 42 retired tokens. In the registry manifest's four dedicated
tag columns:

| column | retired vocabulary | cells |
|---|---|--:|
| `Bundle` | `bundle` (`B1`…`B11`, `L1`) | 132 / 134 |
| `Tier` | `cost-tier` (`T0`…`T3`) | 132 / 134 |
| `Diff` | `differentiability` (`D1`…`D4`, `DN`) | 132 / 134 |
| `Source` | `research-stream` (`S1`…`S5`) | 112 / 134 |

**508 of 536 tag cells carry a retired token.** The 28 that do not are 6 `—` cells and 22
`Source` cells carrying prose.

This is not a cosmetic drift. `data/registry-manifest.csv` is cited by id as `[registry]`
and is canon. The checker sweeps `journals/` and **not** `data/`, so the one rule the corpus
describes as "the namespace this corpus lacks" is unenforced precisely where the machine
reads.

**The correction is the one the register already names, and it must land as a pair:** retag
*plus* extend the checker to sweep `data/`. The retag alone leaves the same hole open for
the next drift. **Check each row's tag against its own provenance cell before converting** —
a blind symbol-to-word map would launder any existing mis-assignment into English and make
it unfindable.

## Finding 2 · The retired `GAP` marker is live on 8 reference-data cells

**Severity: medium · Confidence: certain · Mechanical**

`agent-contract.md` retires `GAP` in favour of `UNSEEDED`. Eight cells in
`transport-coefficients.csv` still carry it:

| property | column |
|---|---|
| `caughey-thomas-mu-n-set` (AlN) | **Value** |
| `caughey-thomas-mu-n-set` (β-Ga₂O₃) | **Value** |
| `mobility-hole` (AlN) | **Value** |
| `impact-ionization-hole` | **Value** |
| `breakdown-field-slope-kBR` | Source |
| `breakdown-field-critical` | Source |
| `impact-ionization-an` | Source |
| `impact-ionization-bn` | Source |

Four sit in the **`Value`** column — a cell whose column promises "the numerical value in
canonical units" and which instead holds a marker plus prose, e.g.
`GAP — paywalled (Farahmand 2001 Tbl II / Wang 2025 Tbl SIII)`. That is honest about the
absence and it is still a typed cell holding an untyped thing.

## Finding 3 · Four uncertainty cells use encodings the schema does not declare

**Severity: medium · Confidence: certain · Mechanical**

`reference-battery.md:82` states: *"**Three** uncertainty encodings appear, and a consumer
must dispatch on the format."* Four rows carry a fourth and fifth:

| encoding found | rows | declared? |
|---|--:|---|
| absolute with units | 118 | yes |
| `×N` multiplicative | 48 | yes |
| `—` unassigned | 6 | yes |
| `unbounded` | 3 | yes |
| **`sign only — magnitude not pinned`** | **2** | **no** |
| **`range`** | **1** | **no** |
| **`range (theory only)`** | **1** | **no** |

A consumer written against the declared set — which is what the sentence instructs — falls
through on four rows. The fix is a schema decision, not a data edit: either the three
encodings become five, or those four rows convert to a declared form.

## Finding 4 · `Source class` is an open vocabulary in a corpus whose rule is controlled vocabulary

**Severity: medium-high · Confidence: certain**

`reference-battery.md:77` declares it as:
`experimental`, `dft-pbe`, `dft-hse`, `gw`, `dft-d3` **and so on**.

- The data uses **22 distinct classes**.
- **19 of them the declaration never names**, including the singletons `dft`, `derived`,
  `mixed`, `theory-pop`, `literature-review`, `analytic-fit`, `dft-vff`.
- **Two classes the declaration explicitly names are used by zero rows**: `dft-pbe` and
  `dft-d3`.

*"And so on"* means no value can ever be wrong, so nothing can check it. The collisions this
produces are real: `dft` against `dft-lda` against `dft-hse`; `derived` against
`derived-experimental`; `first-principles` against `first-principles-bte`. `mixed` names
nothing at all.

This field is **load-bearing for provenance**, which is why it matters more than its size
suggests: the register's live question about a GaN row labelled `experimental` while being
an extrapolation past its source's measured range is only answerable if this vocabulary
means something.

## Finding 5 · Two manifest rows carry an undeclared `—` in `Tier` and `Diff`

**Severity: low · Confidence: certain · Mechanical**

Rows **103** (`F-equals-minus-grad-E`) and **104** (`equivariance`) carry `—` in both `Tier`
and `Diff`. Both are identities rather than evaluated formulas, so "no cost tier, no
differentiability" is plausibly correct — but `—` is declared for the *reference-data*
`Uncertainty` column and **nowhere for these two**. A reader cannot tell "not applicable"
from "not yet assigned", and those are the two states `reference-battery.md:90` goes out of
its way to separate elsewhere.

## Finding 6 · Every one of the 17 tolerance names is a symbol, which the corpus's own central rule forbids

**Severity: high · Confidence: certain**

This is defect class 1 in its purest form: a rule that resolves and is not enforced.

`agent-contract.md` states the rule and states why it exists:

> **no corpus-invented name may be a serial or a symbol.**
>
> Everything the corpus invents is spelled out in English. Standard deviation is the name;
> `σ` is not. `direct` and `adjoint` are names; `D1` and `D2` are not. […] Corpus tags and
> physics symbols were drawn from one alphabet, and **two checkers were written for that and
> then deleted because no rule could separate them. Spelling the corpus half out separates
> them by construction.**

`cert-obligations.md:122` then opens its tolerance table: *"**Canonical names** and default
values for every tolerance and error bound in the oracle library."* **All 17 of those
canonical names are Greek symbols.** They are corpus inventions, not physics: nothing outside
this corpus calls a metastability band `δ_meta` or a nudged-elastic-band force tolerance
`τ_NEB`.

**The collision the rule predicts has already happened, and was patched with prose.**
Immediately above the table, `cert-obligations.md:125-128`:

> `ε` is reserved for permittivity in the physics formulas. **`τ` is not a reserved tolerance
> prefix** — `τ_n`, `τ_p`, `τ_PO`, `τ_E`, `τ_hop`, `τ_iv` and `τ_alloy` are physical times,
> and a `τ_x` is a tolerance only if it appears in the table below.

That paragraph is the finding. It exists **only** because the names are symbols, and the
contract says explicitly that this remedy was already tried and abandoned — a disambiguation
rule is what the two deleted checkers were. English names make the paragraph unnecessary by
construction, which is the contract's entire argument.

**Why nothing fires.** `check_structure.py`'s vocabulary sweep matches tokens against the
**retired-vocabularies list**. It has no rule for *"is this invented name a symbol?"* — that
is a semantic judgement, not a list lookup. So all 17 pass green, exactly as the signature
column's unit promise passes with zero of 134 rows carrying a unit.

**Scale:** 57 occurrences across 6 pages.

**Proposed names**, each derived from the row's own stated meaning in the ledger:

| corpus token | English name |
|---|---|
| `δ_sym` | `symmetry-projection-residual` |
| `δ_PSD` | `negative-eigenvalue-guard` |
| `τ_SCF,strict` | `self-consistent-field-convergence-strict` |
| `τ_SCF,train` | `self-consistent-field-convergence-training` |
| `τ_L3L4` | `equilibrium-to-nonequilibrium-fixed-point` |
| `τ_equiv` | `equivalence-pair-agreement` |
| `τ_method` | `consistency-pair-model-gap` |
| `δ_meta` | `metastability-band` |
| `τ_adj` | `adjoint-registration-gate` |
| `τ_cond` | `fixed-point-conditioning-guard` |
| `τ_trunc` | `truncated-solve-gradient-error` |
| `δ_surrogate` | `surrogate-validity-margin` |
| `τ_battery` | `reference-battery-agreement` |
| `δ_plan` | `compression-plan-truncation-target` |
| `τ_NEB` | `nudged-elastic-band-force-convergence` |
| `τ_cons` | `conservation-residual` |
| `τ_interp` | `lowering-runtime-agreement` |

**Held, not applied.** 57 sites across the certification chapter is the largest single edit
this audit would make, and the `GAP` → `UNSEEDED` incident already demonstrated what a blind
substitution does to prose. It lands cell by cell, and **the disambiguation paragraph is
deleted in the same commit** — leaving it is what would make the rename cosmetic.

**Two residual-category names carry the same defect**: `EOM/γ̂` and `EOM/Π_h`. The other seven
(`EOM/R`, `EOM/P`, `EOM/h`, `EOM/A`, `EOM/Z`, `EOM/Continuum`, `EOM/DefectPopulation`) name
either standard physics symbols or English words, and are not part of this finding.

## Finding 7 · The obligation-to-formula governance relation is not representable from the data

**Severity: high · Confidence: certain**

**Obligations bind by typeclass axis, not by name.** `cert-obligations.md:60` says so
explicitly — one checker "serve[s] every formula that presents that axis" rather than naming
each. The ten obligations bind to `Sampleable` (1, 6), `Quantity` (2), `HasAnalyticStructure`
(3), `Integrable` (5), `DiscreteStructure` (7), a content-side lookup (4, 8), a surrogate
input-domain test (9), and the registration adjoint gate (10).

**No formula row declares which typeclass axes it presents.** The manifest's nine columns are
`# · Name · Signature · Bundle · Tier · Diff · Path · Source · Depends on`. Measured across
all 134 rows:

| axis | occurrences in the manifest |
|---|--:|
| `Sampleable` · `Quantity` · `Integrable` · `HasAnalyticStructure` · `DiscreteStructure` · `Differentiable` · `Response` · `Restrictable` · `FieldOnGrid` | **0 each** |

Controls: `bandgap` returns 2, a fabricated token returns 0 — the sweep fires. The axis names
appear on exactly **one** page in the corpus, `typeclass-alphabet.md`, which is where they are
*defined*; they are attached to no formula anywhere.

**The consequence.** For 9 of the 10 obligations you cannot determine, from the corpus, which
formulas they govern. The single exception is obligation 10, reachable through the `Diff`
column, which encodes differentiability. **The governance relation is not underspecified — it
is absent**, and no check can be written against a relation that no artifact records.

This is the structural cause beneath two findings the register already carries separately:
obligation 9 "names a set of formulas that does not exist", and the manifest "has no
`applicability` column". Both are instances of the same missing edge.

**What it is not.** This does *not* say the obligations are wrong or that formulas go
unchecked in practice. It says the scope of each obligation is not machine-determinable, so
the claim "obligation N covers the right rows" is currently unfalsifiable — which is the same
shape as every other finding in defect class 1.

**A correction is a schema decision, not an edit**: either the manifest gains a typeclass-axis
column, or each obligation states its scope as a predicate over columns that do exist
(`Bundle`, `Tier`, `Diff`). It is Javier's call which, and it is recorded rather than proposed
because the two options have different downstream costs.

---

## Controls

Every sweep above was run with both, per `audit/METHOD.md` rule 3.

| control | expectation | result |
|---|---|---|
| `zzqx…` nonsense string over all of `data/` | must not fire | **not found** |
| `diamond` over all of `data/` | must fire | **12 files** |
| retired-token regex vs. `C2/m` space group | must be *rejected* as a false positive | rejected by hand — `C2` matched the β-Ga₂O₃ space group, not the cluster tag |
| retired-token regex vs. tag columns | must fire on known tags | 508 cells |

**One artifact caught and excluded before it became a finding.** A naive sweep reported
*"35 of 42 retired tokens are still live in `data/`"*. Two were false positives — `C2`
matching the space group `C2/m`, and `B8` matching the prose string
`2026-07 gap-audit B8 resolution` in a Source cell. Restricting the claim to **dedicated tag
columns**, where a token cannot be anything but a tag, is what makes Finding 1 safe to act
on. The looser number was never true.

---

## Scope

This document covers completeness of *what is stated*. It does **not** ask whether the
corpus covers what it should — no sweep here looks for an absent topic. That is auditor 3,
and its two recorded traps still stand: the oracle grades a complete state via residuals
while the operator returns the channels *not* supplied, and completeness of the oracle is
not completeness of n-Op.

Corpus unmodified: `git status --porcelain journals/ data/ log/ generated/` empty; both
gates green.
