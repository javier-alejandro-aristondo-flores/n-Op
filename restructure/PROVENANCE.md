# Provenance register — D19

What each seeded value actually rests on. Produced while scoping D19; the scope turned
out to be smaller than expected in one direction and larger in another.

---

## The `[Wave-1 A#]` markers — smaller than expected

**10 occurrences, in 2 files, both chapter-11 pages already slated for mining**
(`11.5-deriv-high-field`, `11.7-deriv-observable-catalog`). None are in the
reference-data CSVs.

So D19's stated scope is handled by the mining pass: as each page is mined, a marker
either resolves to a real citation that travels with the fact, or the fact does not
survive. No separate sweep is needed.

---

## The reference data — larger than expected

179 rows across the five reference-data CSVs. **24 carry no author-year and no
DOI/arXiv identifier.** These are the corpus's canonical seeded values; the CSVs
outrank canon pages in the authority order.

Not all 24 are defects. Classified:

### A. Working as designed — 5 rows

Declared gaps and derived quantities. **The corpus is behaving correctly here**; these
are the `UNSEEDED` mechanism doing its job before it had a name.

| Row | Source cell |
|---|---|
| `mobility-hole` AlN | `genuine gap` — an explicit refusal |
| `caughey-thomas-mu-n-set` AlN | `one targeted follow-up` — a declared acquisition task |
| `frohlich-alpha` AlN | derived from band/dielectric inputs, and it cites those inputs |
| `mass-density` β-Ga₂O₃ | crystallographic, derived from the Åhman cell |
| `caughey-thomas-mu-n-set` β-Ga₂O₃ | `Wave-2 audit confirmed genuine` |

### B. Standard values — 4 rows

`mass-density` diamond · `dielectric-static` diamond · `cohesive-energy` diamond ·
`lattice-constant-a` diamond. Textbook constants. Defensible, but a corpus facing a
government audit should name the reference rather than say "standard": a value with no
named source is indistinguishable from one nobody checked.

### C. Internal pointers — 9 rows

The Source cell points at another part of this corpus rather than at literature. Each
needs one hop to a real citation. **This is the class D19 exists for.**

| Row | Points at |
|---|---|
| `bandgap-indirect` diamond, `phonon-max-energy` diamond, `debye-temperature` diamond | `curated MVP anchor` → `mvp-system` / `accuracy-ledger` |
| `formation-energy-vs-graphite` diamond | Berman–Simon boundary point (eponym, no year) |
| `thermal-conductivity` diamond ×2 | `Pass C battery anchor` |
| `mobility-electron-best-exp` β-Ga₂O₃ | `Wave-2 audit compilation` |
| `bulk-modulus` / `mass-density` AlN, GaN | `Ioffe NSM` — a real database, but named without a locator |

### D. Method stated where a source belongs — 5 rows

| Row | Source cell |
|---|---|
| `thermal-conductivity` AlN ×2 | `3-ph BTE / Slack extrapolation (theory-only; no >500 K single-crystal measurement)` |
| `pyroelectric-coefficient` GaN | `first-principles + heterostructure measurements (thin data)` |
| `debye-temperature` AlN | `Wang–Zhao Powder Diffr.` (author, no year) |
| `displacement-threshold-Ed` β-Ga₂O₃ | `literature (carried from non-equilibrium stratum H.1)` |

A method is not a provenance. "3-ph BTE extrapolation" says how the number was made,
not what it can be checked against — and both AlN rows say plainly that no measurement
above 500 K exists, which is the honest part.

**`displacement-threshold-Ed` is the sharpest case and was already known.** The CSV
names an appendix; the appendix (`11.5:407`) states `Ga₂O₃ ~25 eV` as a bare
parenthetical with no citation; the provenance-type reads `literature-review` and no
literature is ever named. Chapter 11's deletion removes even the appearance of a
source. It becomes `UNSEEDED`.

---

## One finding that is not about provenance structure

Two `thermal-conductivity` diamond rows cite `Pass C battery anchor (… 2026-06-10
re-audit)`. **That is the audit the corpus itself records as having missed a κ
overprediction, a mis-citation, and a fabricated citation** (`audit-prompt §5`). A value
whose provenance is an audit known to have failed on that exact quantity is not a
provenance chain — it is a loop.

Whether the *value* is right is auditor 2's question, not this one's. Registered here
so it is not lost, and flagged because the corpus's own rule says it: *"Re-verify
values, never verdicts — a later value-level correction supersedes an earlier
clearance, and inheriting false confidence is the failure mode this rule exists to
prevent."*

---

## Disposition for Phase 2

| Class | Action |
|---|---|
| A — declared gaps | keep; convert the marker to `UNSEEDED`, which is what it already means |
| B — standard values | name the reference. Cheap, and it removes "trust me" from the canonical data |
| C — internal pointers | resolve one hop to the literature the pointer stands for. If the hop lands on nothing, the row is `UNSEEDED` |
| D — method-as-source | either find the source or mark `UNSEEDED`. Do not carry a method in a provenance field |

**The rule, which is the whole point of D19:** a value carried forward because it has
always been there is exactly the failure the 2026-06-10 clearance made. A row whose
provenance does not resolve is not wrong — it is *unknown*, and the corpus has a word
for that.
