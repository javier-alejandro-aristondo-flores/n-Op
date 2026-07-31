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
nothing. It is not: `cert-obligations.md:127-128` **explicitly declares** that `τ_n`, `τ_p`,
`τ_PO`, `τ_E`, `τ_hop`, `τ_iv` and `τ_alloy` are *physical times, not tolerances*, and that
"a `τ_x` is a tolerance only if it appears in the table below." 17 ledger rows + 7 declared
physical times + the `τ_x` placeholder = 25. **All accounted for. Zero undefined tolerance
symbols.**

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
