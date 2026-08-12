# Literature verification — citations the corpus makes

The brief's class 4, *false claims*, and the class the corpus's own history says a prior
audit missed: a **fabricated** citation, a mis-citation, and a conductivity overprediction
all cleared the 2026-06-10 re-audit.

**Gated on grounding.** Every corpus claim checked here was first confirmed present in the
live tree. That ordering is what this program got wrong twice — the 727 K nickel and
3.56712 Å findings were competent literature work aimed at claims the corpus does not make.

---

## Result

| | |
|---|---|
| Distinct citations extracted from `journals/` + `data/` | **49** |
| Verifiable by exact method (APS, constructible DOI) | **15** |
| **Confirmed defects** | **1** — in 3 sites |
| Clean verdicts earned | 14 APS citations · 13 β-Ga₂O₃ elastic constants exact · FBA · Olson |
| Not checkable by this method | 34 (AIP article numbers — see limits) |

---

## Confirmed defect · Zoroddu is cited at the wrong volume, in three places

**Severity: medium · Confidence: certain · Mechanical**

The corpus cites **`Zoroddu PRB 63 045208 (2001)`**. `10.1103/PhysRevB.63.045208` does not
exist.

The paper is **`Phys. Rev. B 64, 045208 (2001)`** — Zoroddu, Bernardini, Ruggerone &
Fiorentini, *"First-principles prediction of structure, energetics, formation enthalpy,
elastic constants, polarization, and piezoelectric constants of AlN, GaN, and InN:
Comparison of local and gradient-corrected density-functional theory."* Positively
identified: full author list, year, page and subject all match. **The volume is off by
one.**

Three sites, all wrong the same way:

| site | text |
|---|---|
| `accuracy-ledger.md:313` | `Zoroddu PRB 63 (2001)` |
| `polarization-piezoelectric.csv:2` | `Zoroddu PRB 63 045208 (2001)` |
| `polarization-piezoelectric.csv:3` | `Zoroddu PRB 63 (2001)` |

It backs the **spontaneous-polarization zincblende-reference** rows for GaN and AlN, which
feed the polarization gate — the same package the register flags as licensed by
`is-noncentrosymmetric` when it needs a *polar* class.

**Correction:** `63` → `64` at all three sites. Purely mechanical; no physics decision.

---

## Clean verdict · the β-Ga₂O₃ elastic tensor, 13 of 13 exact

Earned, not assumed. `elastic-tensors.csv` carries 13 constants for β-Ga₂O₃ sourced
`RUS+LDI JAP 124 085102 (2018)`. That is **"Unusual elasticity of monoclinic β−Ga₂O₃"**,
J. Appl. Phys. **124**, 085102 (2018), which determined all 13 independent constants by
resonant ultrasound spectroscopy with laser-Doppler interferometry — hence `RUS+LDI`, which
is a **method pair, not an author**.

Every value and every uncertainty matches the primary source exactly:

`C11 242.8±2.9` · `C22 343.8±3.8` · `C33 347.4±2.5` · `C44 47.8±0.2` · `C55 88.6±0.5` ·
`C66 104.0±0.5` · `C12 128±0.1` · `C13 160±1.5` · `C23 70.9±2.1` · `C15 −1.62±0.05` ·
`C25 0.36±0.01` · `C35 0.97±0.03` · `C46 5.59±0.69` GPa.

**13 present in the paper, 13 in the corpus, 0 mismatches, 0 missing.**

**This corroborates a severity-ranked finding.** β-Ga₂O₃ genuinely has **13** independent
elastic constants. The register's claim that a cubic Born-stability form — 3 conditions —
would leave ten of them unread while still returning "stable" rests on a fact now confirmed
against primary literature.

---

## Controls

| control | expectation | result |
|---|---|---|
| `10.1103/PhysRevB.47.14850` (Olson, known real) | must resolve | **resolved** — title matches |
| `10.1103/PhysRevB.999.99999` (fabricated) | must not resolve | **not found** |
| Guo APL 106 111909 (known real, verified via arXiv:1412.7472) | tests the AIP path | **returns "unresolved"** |
| Klimm CRT 58 2200204 (known real, verified via DOI 10.1002/crat.202200204) | tests the AIP path | **returns "unresolved"** |

The last two are the important ones. **Two citations I had already verified as real by other
routes both come back "unresolved" from this method.** That is a positive demonstration that
an unresolved AIP citation is *uninformative* — it cannot support a defect claim. Without
those controls, 34 correct citations would have been reported as suspect.

---

## What this method cannot do — three limits, all measured

**1 · APS stopped issuing constructible DOIs.** Recent APS papers carry opaque DOIs such as
`10.1103/4rsc-ysk8`. `Lan-Ebert PRB 113 155302 (2026)` was reported NOT-FOUND on the first
run and **is correctly cited** — Crossref confirms Physical Review B, volume 113, article
155302, 2026, authors Lan … Ebert. A bibliographic fallback now covers this. **False
positive, caught before it was reported.**

**2 · Crossref's fuzzy search retrieves same-surname strangers.** A "coordinate mismatch"
verdict built on a single shared surname produced **12 false defects** in one run — "Guo"
retrieved a filled-skutterudite study, "Yan" retrieved electrospun nanofibers, "Zhang"
retrieved a terahertz topological insulator. The verdict was removed: **this method now
never claims a defect from a fuzzy match.**

**3 · AIP article numbers are not reliably queryable.** 34 citations to `JAP`, `APL`, `SST`,
`SSE`, `JPCM`, `CRT` and `APEX` cannot be confirmed or refuted this way, as the Guo and
Klimm controls prove. **They are unverified, not suspect**, and closing them needs
per-paper retrieval rather than a bulk sweep.

**And one parsing limit worth recording:** the extractor initially read `RUS+LDI` as an
author and `FBA` as an author. Both are corpus initialisms — a method pair and
Fiorentini-Bernardini-Ambacher respectively. Neither is a defect.

---

## Coverage statement

**15 of 49 citations were checked by a method with working controls. 1 is wrong.** The
remaining 34 are unverified, and the reason is an instrument limit rather than a judgment
about them. Reporting this as "citations verified" would be exactly the failure the
`target-is-not-measurement` trap describes.
