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

---

## What the lead sweep returned

Three agents, one per material family. Full detail in `restructure/leads/`. Every claim
below was re-verified against the CSVs before being written here.

**Not every finding is a missing citation.** Four classes came back, and two were not
what this pass was looking for.

### A. Resolves internally — no search was needed

| Row | Resolves via |
|---|---|
| `frohlich-alpha` AlN | its own inputs are two rows of `phonon-frequencies.csv`, both citing Davydov with year and DOI |
| `bulk-modulus` AlN | derivable from the elastic constants already in the same CSV |
| `mass-density` β-Ga₂O₃ | the Åhman citation sits in the audit file, unpropagated |
| `caughey-thomas-mu-n-set` β-Ga₂O₃ | the audit's gap register carries the substantiating sentence |

Four of the twenty-four never needed literature. They needed the corpus to look at itself.

### B. Resolved to named primary literature

`mobility-electron-best-exp` β-Ga₂O₃ → four named papers, three matching exactly ·
`debye-temperature` AlN → full citation recovered · `lattice-constant-a`,
`phonon-max-energy`, `mass-density` diamond → primary sources with exact matches.

### C. A declared absence that contradicts a citation in the same file

`transport-coefficients.csv` row 43 states AlN conductivity is theory-only with
**"no >500 K single-crystal measurement"**. Row 24 of the same file cites
**Slack, J. Phys. Chem. Solids 48, 641 (1987)** for the 300 K value — and that paper
reports measurements to far above 500 K.

This is the opposite failure from an unsourced value: **a refusal to seed, on grounds
the corpus's own citation contradicts.** An unnecessary refusal costs coverage
silently, and unlike a wrong value nothing will ever fire on it.

`caughey-thomas-mu-n-set` AlN may be the same shape — the lead found one named source
that is an open preprint.

### D. The diamond conductivity rows — four separate problems

The two rows this pass was aimed at (`transport-coefficients.csv` 773 K = 620 W/mK,
1100 K = 450 W/mK, both `Pass C battery anchor`).

1. **The ledger and the CSV describe the same numbers differently.** The accuracy
   ledger attributes all three temperatures to *Feng–Lindsay–Ruan (2017); Broido
   (2007)*. The CSV declares two of them `theory-interpolation`. Both are canon; the
   ledger outranks nothing here — they simply disagree about what kind of number this
   is. **Structural, and mine.**
2. **A citation appears to name the wrong material.** `Broido, Appl. Phys. Lett. 91,
   231922 (2007)` is, by its published abstract, about **silicon and germanium**. The
   diamond paper from that group is a different one (Ward et al., Phys. Rev. B 80,
   125203, 2009). The corpus records the 2026-06-10 re-audit as having missed *a
   mis-citation*; this is a candidate for it, or for a second one on the same quantity.
3. **The overprediction is probably named in the corpus's own cited paper.**
   Feng–Lindsay–Ruan states that three-phonon scattering alone **overpredicts diamond
   conductivity by 31% at 1000 K**, and that including four-phonon scattering reduces
   the prediction by 30% at 1000 K. The corpus records that re-audit as having missed
   *a κ overprediction*. The two are very likely the same thing.
4. **A numerical confusion trap, and it belongs in the traps register.** That paper's
   widely-quoted "2200 → 1400 W/mK at room temperature" figures are for **boron
   arsenide, not diamond** — and they collide numerically with diamond's own ~2200
   W/mK, one paragraph away. Anyone re-deriving the diamond anchor from this paper can
   land on the right number for the wrong material and see nothing wrong.

**The single highest-value acquisition:** Olson et al., *Phys. Rev. B* **47**,
14850 (1993) — the only primary measurement spanning 170–1200 K, which both
high-temperature rows depend on, and which could not be retrieved.

### E. Where "no source found" is the honest answer

`dielectric-static` diamond and `debye-temperature` diamond. Neither is a minor row:
the first feeds image-force lowering, the second sets the four-phonon validity window
that the 773 K conductivity row depends on. The Debye temperature additionally carries
±50 K against a literature spread of 1860–2230 K by method — **a stated uncertainty
narrower than the disagreement between methods.**

### F. One value whose trail points at the wrong material

`cohesive-energy` diamond, 7.37 eV/atom ± 0.05. The lead traces the standard tabulated
7.374 to **graphite**; diamond's figure is 7.346. Both sit inside the stated band, so
the *value* is defensible either way — but the *provenance* may be another material's
number. Registered, not adjudicated.

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
