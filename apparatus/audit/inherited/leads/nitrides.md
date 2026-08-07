# Provenance leads — AlN and GaN

Groundwork for auditor 2. **These are leads, not verdicts.** Nothing here rules on whether
a seeded value is correct. Each entry names what the value could be checked against, states
how confident I am, and says what would settle it.

Scope: the AlN/GaN rows in `physics/library/cert/reference-data/*.csv` whose `Source` cell
names no author and no year.

Two rows resolve **without any literature acquisition** (`frohlich-alpha`, and the derivation
half of `bulk-modulus`). One row's stated absence appears to be **contradicted by a paper the
corpus already cites** (`thermal-conductivity`). One declared gap is **closable from an open
preprint** (`caughey-thomas-mu-n-set`).

---

## Summary table

| Row | Material | Lead status | Confidence |
|---|---|---|---|
| `frohlich-alpha` | AlN | **Resolves internally** — Davydov is already in the corpus with year + DOI | Very high |
| `bulk-modulus` | AlN | **Derivable internally** from McNeil C_ij already in the same CSV | High |
| `debye-temperature` | AlN | **Citation found in full** — Wang et al., Powder Diffr. 29(4) 352 (2014) | Very high |
| `thermal-conductivity` ×2 | AlN | **Absence claim looks false** — Slack 1987 measured to 1800 K | High (abstract-only) |
| `pyroelectric-coefficient` | GaN | **Source triple identified**; sign premise independently confirmed | High / medium-high |
| `mass-density` | GaN, AlN | Secondary-only, and does not reconcile with the crystallographic cell | High on arithmetic |
| `mobility-hole` | AlN | **Gap confirmed still real** | High |
| `caughey-thomas-mu-n-set` | AlN | **Gap is closable** — one named source is an open arXiv preprint | High |

---

## 1. `frohlich-alpha` AlN — 0.58 ± 0.1

**CSV:** `transport-coefficients.csv:19` · Source cell `derived from band/dielectric inputs
(Davydov omega_LO 110-114 meV)` · class `derived`

**Resolves internally. No search was needed and none should be done.**

`Davydov omega_LO 110-114 meV` is the enclosing round of two rows in the corpus's own
`phonon-frequencies.csv`:

- row 8 — AlN A₁(LO) **110.7 meV**, `Davydov et al. PRB 58 12899 (1998) 10.1103/PhysRevB.58.12899`
- row 9 — AlN E₁(LO) **113.6 meV**, `Davydov et al. 1998`

The rounding is documented in the corpus's own changelog
(`9.1-accuracy-ledger.md`): *"AlN ω_LO range re-rounded 111–114 → 110–114 meV to match the
canonical enclosing-round of the Davydov anchors A₁(LO) 110.7 / E₁(LO) 113.6."*

**Independent confirmation the citation is real and correctly transcribed.** Liu,
Fernández-Serra & Allen (PRB 93, 081205) cite it as their Ref. 23 with the full author list:
V. Y. Davydov, Y. E. Kitaev, I. N. Goncharuk, A. N. Smirnov, J. Graul, O. Semchinova,
D. Uffmann, M. B. Smirnov, A. P. Mirgorodsky, R. A. Evarestov, *Phys. Rev. B* **58**, 12899
(1998).

**Note for whoever writes the replacement Source cell:** α_F is *derived*, so a complete
provenance needs the other inputs too, and they are all already in the corpus —
ε₀(⊥) = 8.5 and ε_∞(⊥) = 4.77 (`material-constants.csv:18-19`) and m*_e(⊥) = 0.32 m₀
(`material-constants.csv:11`). Caveat: those dielectric rows are themselves *partly*
`Ioffe NSM` (they also cite Wagner & Bechstedt PRB 66 115202 (2002)), so resolving
`frohlich-alpha` inherits a weaker link one hop down.

**Confidence:** very high.
**What would settle it:** nothing external.

---

## 2. `bulk-modulus` AlN (wz) — 210 GPa ± 10

**CSV:** `elastic-tensors.csv:13` · Source cell `Ioffe NSM` · class `experimental`

### What Ioffe actually says

The Ioffe NSM AlN mechanical-properties page does carry `Bs = 210 GPa` at 300 K, so the
value is faithfully transcribed. But the page attributes nothing per-value — it carries one
undifferentiated reference list (Slack 1973, Goldberg 2001, Nikolaev 1998, Drory 1996,
McNeil 1993, Wright 1997, Gerlich 1986, Thokala & Chaudhuri 1995, Sanjurjo 1983, and
others). **Secondary-compilation-only is the finding**: there is no way to tell from the
page which measurement 210 GPa came from.

### Strongest lead: it is derivable from data the corpus already owns

For a hexagonal crystal, B = [(C₁₁+C₁₂)C₃₃ − 2C₁₃²] / (C₁₁+C₁₂+2C₃₃−4C₁₃).

Feeding the McNeil–Grimsditch–French constants **already carried in the same CSV**
(`elastic-tensors.csv:7-11`, 410.5 / 148.5 / 98.9 / 388.5):

> **B = 210.13 GPa**

This is the identical pattern the diamond row already uses —
`(C₁₁+2C₁₂)/3 from McSkimin & Andreatch 1972` (`elastic-tensors.csv:20`). Adopting it makes
`bulk-modulus` AlN a `derived-experimental` row citing
**McNeil, Grimsditch & French, J. Am. Ceram. Soc. 76, 1132 (1993), 10.1111/j.1151-2916.1993.tb03730.x**,
which the corpus has already vetted.

### Independent primary candidates, if a direct measurement is wanted instead

| Source | Value | Note |
|---|---|---|
| Ueno, Onodera, Shimomura & Takemura, *Phys. Rev. B* **45**, 10123 (1992) | B₀ = 207.9 ± 6.2 GPa | High-pressure X-ray, diamond-anvil cell to 30 GPa; wurtzite→rocksalt at 22.9 GPa |
| Xia, Xia & Ruoff, *J. Appl. Phys.* **73**, 8198 (1993) | — | Energy-dispersive synchrotron XRD; rocksalt-phase focus |

Both sit inside the CSV's ±10 GPa.

### One thing I checked because it looks like a copy error and is not

AlN and GaN both carry **exactly 210 GPa**. That is not a duplication artifact: Polian's
GaN constants (390/145/106/398) give **B = 209.99 GPa** by the same formula, entirely
independently of the AlN numbers. The coincidence is physical.

**Confidence:** high for the internal derivation; medium for which primary Ioffe is
reporting.
**What would settle it:** nothing, if the corpus adopts the derived form. Otherwise, read
Ueno 1992.

---

## 3. `mass-density` GaN 6.15 and AlN 3.23 g/cm³ (± 0.02)

**CSV:** `elastic-tensors.csv:14-15` · Source cell `Ioffe NSM` · class `experimental`

Both values are faithfully transcribed from Ioffe. But Ioffe is secondary, and — this is
the part worth auditor 2's attention — **neither value reconciles with the crystallographic
cell printed on the same Ioffe page.**

### AlN: Ioffe lists two densities and the corpus took the one that does not close

Ioffe's AlN basic-parameters page states **both** `3.255 g/cm³` and `3.23 g/cm³`, plus
a = 3.112 Å, c = 4.982 Å, and 9.58×10²² atoms/cm³.

| Check | Result |
|---|---|
| ρ from Ioffe's own cell (Z=2, M = 40.988 g/mol) | **3.258 g/cm³** |
| atoms/cm³ from Ioffe's own cell | 9.574×10²² — matches Ioffe's stated 9.58×10²² |
| ρ from Wang et al. 2014 refined cell (a = 3.11139, c = 4.97843) | **3.262 g/cm³** |
| CSV value | **3.23** |

So Ioffe's cell, atom count, and 3.255 figure are mutually consistent, and **3.23 is the
outlier the corpus selected.** The gap (0.025–0.032) exceeds the CSV's own ±0.02.

Note the Wang 2014 cell is from **the corpus's own `debye-temperature` source** (§4 below) —
an internal cross-check that is currently unused.

### GaN: 6.15 is inconsistent with the accepted cell by ~1%

Ioffe's GaN basic page states a = 3.189 Å, c = 5.186 Å (300 K), density 6.15 g/cm³,
8.9×10²² atoms/cm³.

| Check | Result |
|---|---|
| ρ from Ioffe's own cell (Z=2, M = 83.730 g/mol) | **6.088 g/cm³** |
| atoms/cm³ from Ioffe's own cell | 8.758×10²² vs Ioffe's stated 8.9×10²² |
| c required to yield ρ = 6.15 at a = 3.189 | **5.134 Å** — not the accepted GaN c |
| CSV value | **6.15** |

6.15 g/cm³ is very widely quoted for GaN, so the corpus is in good company; but it does not
follow from the modern wurtzite cell, and the discrepancy is ~3× the stated uncertainty.

### Cleanest path, and the corpus already has a precedent for it

`mass-density` β-Ga₂O₃ (`elastic-tensors.csv:26`) is already handled as
`crystallographic from the Åhman cell (Z=4)`, class `derived-experimental`. The same
treatment applied here would give AlN 3.26 (Wang 2014 cell) and GaN 6.09, each citing a
named primary cell determination.

**Confidence:** high on the arithmetic and on Ioffe being secondary-only. I have *not*
established which cell determination the field currently considers definitive for GaN —
that is auditor 2's call, and it is the thing that decides between 6.09 and 6.15.
**What would settle it:** a decision on compilation-value vs crystallographic-value, then
one primary XRD cell reference per material.

---

## 4. `debye-temperature` AlN (wz) — 1000 K ± 80 — **citation found in full**

**CSV:** `phonon-frequencies.csv:11` · Source cell
`Wang–Zhao Powder Diffr. (971 K); DFT 950–1050 K`

**Full citation:**

> Wang, J.; Zhao, M.; Jin, S. F.; Li, D. D.; Yang, J. W.; Hu, W. J.; Wang, W. J.
> "Debye temperature of wurtzite AlN determined by X-ray powder diffraction."
> *Powder Diffraction* **29**(4), 352–355 (2014). DOI **10.1017/S0885715614000542**

Method: Rietveld refinement of room-temperature XRPD; Θ_D extracted from the refined
Debye–Waller factors (Al 0.442(12) Å², N 0.559(33) Å²) via the Debye approximation.
Refined cell a = 3.11139(1) Å, c = 4.97843(3) Å; N position z = 0.38459(33).

**Result: Θ_D = 971 K** — exactly the parenthetical in the CSV. `Wang–Zhao` is
first-two-authors shorthand and is accurate.

### One flag on the band, not the citation

Ioffe's AlN basic page — the source the corpus trusts for two other AlN rows — states
**Θ_D = 1150 K**, which falls outside the CSV's 1000 ± 80 K. The AlN Debye temperature has a
genuinely wide literature spread (971 K experimental, ~950–1050 K DFT, 1150 K Ioffe), and the
seeded uncertainty currently excludes one commonly cited value. Registered for auditor 2; I
am not ruling on whether ±80 is too tight.

**Confidence:** very high on the citation; the value, method, and parenthetical all match.
**What would settle it:** nothing for provenance. For the band, a decision on whether Ioffe's
1150 K deserves to be inside σ.

---

## 5. `thermal-conductivity` AlN (wz c-axis) ×2 — **the stated absence appears to be false**

**CSV:** `transport-coefficients.csv:25` (773 K, 140 W/mK, σ = ×0.3) and `:43`
(1100 K, 95 W/mK, σ = ×0.4)
**Source cells:** `3-ph BTE / Slack extrapolation (theory-only)` and
`3-ph BTE / Slack extrapolation (theory-only; no >500 K single-crystal measurement)`

The brief said confirming the absence would be as valuable as finding a source. **I could
not confirm it. The absence claim looks wrong, and the counterexample is already cited in
the same CSV, one row up.**

### Slack et al. 1987 measured single-crystal AlN to 1800 K

> G. A. Slack, R. A. Tanzilli, R. O. Pohl, J. W. Vandersande,
> "The intrinsic thermal conductivity of AlN," *J. Phys. Chem. Solids* **48**(7), 641–647 (1987).
> ScienceDirect PII `0022369787901533`

Abstract (as retrieved, two independent searches returning the same wording):

> "The thermal conductivity of high purity **single crystals** of AlN has been measured **from
> 0.4 to 1800 K** … The maximum thermal conductivity is 23 W/cmK at 52 K, and at 300 K the
> value … for pure AlN is 3.19 W/cmK (80% of that of pure copper). **Above 500 K the value
> decreases as T⁻¹·²⁵.**"

**The corpus's own 300 K AlN row (`transport-coefficients.csv:24`) already cites
`Slack JPCS 48 641 (1987)`.** So the paper that is said not to exist is already in the file.

### Consistency arithmetic, offered as a lead only

Anchoring Slack's own 300 K value (3.19 W/cmK = 319 W/mK) and applying his stated T⁻¹·²⁵:

| T | Slack law | Seeded | Seeded σ band |
|---|---|---|---|
| 773 K | **98 W/mK** | 140 | ×0.3 → 98–182 — Slack lands exactly on the lower edge |
| 1100 K | **63 W/mK** | 95 | ×0.4 → 57–133 — Slack sits inside |

The two seeded points imply κ ∝ T⁻¹·¹⁰; Slack states T⁻¹·²⁵. The σ bands do cover the
discrepancy, which is to the corpus's credit — but the values were built by extrapolation
when a measurement was available.

### Other high-temperature anchors checked — none reaches 500 K

| Source | Range | Max T |
|---|---|---|
| Rounds et al., *Appl. Phys. Express* **11**, 071001 (2018), 10.7567/APEX.11.071001 (already cited at 300 K) | 30–325 K, 3ω | 325 K |
| Inyushkin et al., *J. Appl. Phys.* **127**, 205109 (2020) | 5–410 K, PVT single crystal, κ(300 K) up to 316 W/mK | 410 K |
| Xu et al., *J. Appl. Phys.* (2019), Stanford poplab | ~100–400 K | ~400 K |

So the "no >500 K single-crystal measurement" claim is correct about *everything modern* —
and wrong about the 1987 paper the row's own sibling cites.

**Confidence:** high that Slack 1987 is a >500 K single-crystal measurement. **Abstract-only
— I could not open the paywalled full text.** Two things are therefore unverified and matter:
whether the >500 K data are on the same single crystals as the low-T data (rather than
ceramic or extrapolated), and whether they are **c-axis resolved** (the CSV rows are
c-axis-specific).

**What would settle it:** read Slack 1987 in full. **This is the highest-value acquisition in
this batch** — it decides whether two `first-principles-bte` theory-only rows should become
experimental rows with a 1987 primary citation, and it is a single paywalled PDF.

---

## 6. `pyroelectric-coefficient` GaN (wz) — +4.5×10⁻⁶ C/m²K, σ = ×2 — SIGN GUARD

**CSV:** `polarization-piezoelectric.csv:14` · Source cell
`first-principles + heterostructure measurements (thin data); SIGN GUARD as AlN row` · class `dft`

### The Source cell's three-part description maps onto an identifiable triple

**First-principles:**
> Jian Liu, Maria V. Fernández-Serra, Philip B. Allen,
> "First-principles study of pyroelectricity in GaN and ZnO,"
> *Phys. Rev. B* **93**, 081205(R) (2016). DOI **10.1103/PhysRevB.93.081205** ·
> arXiv:1603.00657 — **open access, read in full**

Quasi-harmonic DFPT. Computes primary p_ε, secondary p₂, and total p_σ for GaN over
0–1000 K. Their Fig. 1 plots all three curves **positive**, on an axis spanning 0–6
(units 10⁻⁶ C/m²K), with total p in the 4–5 range near 300 K — consistent with the
seeded **+4.5**.

**Heterostructure / thin-film measurements** (their Refs. 9 and 10):
> K. Matocha, V. Tilak, G. Dunne, *Appl. Phys. Lett.* **90**, 123511 (2007), 10.1063/1.2716309
>
> A. D. Bykhovski, V. V. Kaminski, M. S. Shur, Q. C. Chen, M. A. Khan,
> "Pyroelectricity in gallium nitride thin films," *Appl. Phys. Lett.* **69**, 3254–3256 (1996)

**"(thin data)" is corroborated by the first-principles paper itself:** *"For GaN,
disagreement in the experimentally measured pyroelectric coefficients is reported, possibly
due to the piezoelectric contribution from the strain introduced by the substrates."*

### SIGN CONVENTIONS — the part the brief asked for

**a) The corpus's premise is independently confirmed.** The seeded III-N P_sp being negative
in the zinc-blende reference frame is not a corpus idiosyncrasy:

> Benbedra, Meskine, Boukortt, Hayn, Abbassa, Abbes,
> "The trigonal structure as a reference to access the spontaneous polarization of wurtzite
> crystals," arXiv:2210.17343 — **open access, read in full**

Their Table 2 (C/m²):

| Material | P_sp, trigonal ref (this work) | P_sp, ZB ref (literature) |
|---|---|---|
| AlN | −0.087 | **−0.090** |
| GaN | −0.035 | **−0.034** |

The ZB-reference column is attributed to Bernardini, Fiorentini & Vanderbilt. Their text:
*"The spontaneous polarization has a negative sign and is nonzero only along the c-axis,
which corresponds to the [0001̄] direction."*

**b) A robustness result for the guard.** The sign does **not** flip between the zinc-blende
and trigonal reference structures (−0.090 vs −0.087; −0.034 vs −0.035). The guard's hazard
is therefore *not* ZB-vs-trigonal choice of reference — it is the **unsigned positive-magnitude
convention**, which is a different and more slippery thing.

**c) The hazard is real and documented.** The classic experimental GaN sources report a
pyroelectric **voltage** coefficient in V/m·K, **as an unsigned magnitude, with no sign
convention stated anywhere**:

- Bykhovski et al., APL 69, 3254 (1996): ~10⁴ V/m·K
- Gaska, Shur & Bykhovski, "Pyroelectric and Piezoelectric Properties of GaN-Based Materials,"
  *MRS Internet J. Nitride Semicond. Res.* **4**(S1), 57–68 (1999),
  DOI 10.1557/S1092578300002246 — open access: *"can reach 7×10⁵ V/m-K."*
  I checked this paper specifically for a sign convention and it defines none.

A value lifted from these carries neither a sign nor a frame. That is precisely what the
corpus's guard protects against, and it is worth recording that the guard's stated failure
mode is observable in the actual source literature rather than hypothetical.

**d) Third-party cross-check of the same pairing.** "Mechanisms of pyroelectricity in three-
and two-dimensional materials" (arXiv:1803.04580) reports ZnO P_s = **−0.035 C/m²** in its
Table 1 while plotting p **positive** in its Fig. 1 — the same P_s-negative / p-positive
pairing the corpus uses.

**Confidence:** high on the citation triple and on the negative-P_sp premise. **Medium-high**
that Liu et al. is the specific first-principles source behind +4.5 — the paper publishes no
numeric table of p, so I read ~4–5 at 300 K off Fig. 1.
**What would settle it:** digitize Fig. 1 of Liu et al. at 300 K, or confirm whether a numeric
total-p appears in the published (non-arXiv) version.

### Adjacent finding — the AlN row this row inherits from has a wrong DOI

Not my assigned row, but the GaN Source cell says `SIGN GUARD as AlN row`, so it inherits
from it. `polarization-piezoelectric.csv:13` reads:

> `Yan et al. APL 90 212102 (2007) 10.1063/1.2742589`

**DOI `10.1063/1.2742589` resolves to a different article** — "Surface acoustic wave device
on AlGaN/GaN," *APL* **90**, 213506 (2007). Verified by following the DOI.

The correct DOI for APL **90**, 212102 (2007) is **10.1063/1.2741600**:

> W. S. Yan, R. Zhang, X. Q. Xiu, Z. L. Xie, P. Han, R. L. Jiang, S. L. Gu, Y. Shi, Y. D. Zheng,
> "Temperature dependence of the pyroelectric coefficient and the spontaneous polarization of AlN,"
> *Appl. Phys. Lett.* **90**, 212102 (2007). DOI 10.1063/1.2741600

Author list, volume, and page in the CSV are right; only the DOI is wrong.

**Second flag on the same row, for auditor 2:** that paper's abstract describes a **Debye-model
calculation** over 0–1000 K, not an epilayer measurement. The CSV describes it as
`epilayer/Debye` and classes the row `experimental`. Whether the class survives is a
value-level question I am not ruling on, but it should be looked at.

---

## 7. `mobility-hole` AlN (wz) — declared gap — **still real**

**CSV:** `transport-coefficients.csv:14` · `GAP — deep Mg acceptor; holes < 1e10 cm-3` ·
Source cell `genuine gap` · class `gap`

**The gap is confirmed.** Nothing published gives an intrinsic AlN hole mobility. The corpus
is refusing to guess and should keep refusing.

**What has appeared since**, and why it does not close the gap: a 2025 study of Mg-doped
p-type AlN thin films grown by magnetron sputtering with Mg–Al alloy targets
(*Micromachines* **16**(9), 1035; open access, PMC12471319) reports Hall mobilities of
**0.105–0.181 cm²/V·s** at 0.01–0.5 at.% Mg. These are impurity-band / hopping values in
sputtered polycrystalline film, not band-transport hole mobility in single-crystal AlN. If
anything they reinforce the corpus's stated premise — the deep Mg acceptor and negligible
free-hole density are exactly what the paper works around.

**One internal consistency link worth recording.** The literature attributes AlN's anomalous
hole transport to the **valence split-off (crystal-field, CH-like) band** being the topmost
valence band. That is precisely what the corpus's own
`crystal-field-splitting-delta-cr` AlN row already records
(`material-constants.csv:43`, Rinke et al. PRB 77 075202 (2008), Δ_cr < 0, with the explicit
note that the absent AlN A-band hole-mass row is a refusal rather than an oversight). The
hole-mobility gap and that row are the same physics, currently unlinked.

**Confidence:** high.
**What would settle it:** nothing to acquire. Keep as `UNSEEDED` / gap.

---

## 8. `caughey-thomas-mu-n-set` AlN (wz) — declared gap — **closable now**

**CSV:** `transport-coefficients.csv:8` ·
`GAP — paywalled (Farahmand 2001 Tbl II / Wang 2025 Tbl SIII)` ·
Source cell `one targeted follow-up` · class `gap`

**The gap's stated cause is only half true. One of the two named sources is not paywalled.**

> Amanda Wang, Nick Pant, Woncheol Lee, Jie-Cheng Chen, Feliciano Giustino, Emmanouil Kioupakis,
> "Electron mobility in AlN from first principles," **arXiv:2506.09240** (2025)
> — open access, read in full including supplement

Its **Table SIII** is titled *"Fitted parameters for the ionized impurity concentration
dependence of the total drift and Hall mobility, based on the Caughey-Thomas model"* and
gives the full quartet, direction-resolved, for two ionization conditions:

| Row (as printed) | μ_min | μ_max | α | N_crit (cm⁻³) |
|---|---|---|---|---|
| drift, total ionization | 51.20 | 879.76 | 0.68 | 3.82×10¹⁷ |
| drift, total ionization | 65.85 | 631.00 | 0.65 | 6.66×10¹⁷ |
| drift, partial ionization | 0.38 | 875.50 | 0.89 | 2.44×10¹⁷ |
| drift, partial ionization | 0.79 | 621.29 | 0.91 | 4.21×10¹⁷ |
| Hall, total ionization | 61.65 | 974.29 | 0.70 | 3.75×10¹⁷ |
| Hall, total ionization | 61.95 | 663.55 | 0.71 | 9.33×10¹⁷ |
| Hall, partial ionization | 0.58 | 963.57 | 0.88 | 2.85×10¹⁷ |
| Hall, partial ionization | 1.39 | 672.90 | 0.91 | 5.04×10¹⁷ |

(mobilities in cm²/V·s; their Eq. 2 is the standard Caughey–Thomas form.)

### Three caveats, all of which matter more than the numbers

**a) Extraction caveat — I have deliberately not assigned directions above.** My text
extraction of Table SIII's ∥c / ⊥c row labels appears to contradict the paper's main text,
which states plainly:

> *"room-temperature mobilities to be 871 cm²/V·s and 619 cm²/V·s along the in-plane and
> out-of-plane directions, respectively"*

That matches the corpus's ledger entry `871(⊥) / 619(∥)` exactly, so **the corpus's existing
anisotropy assignment is corroborated and is not in question.** The Table SIII labels need to
be re-read in a rendered PDF before any quartet is bound to an axis. I raise this as an
extraction limitation of mine, not as a defect in the corpus.

**b) Class mismatch — this is a seeding decision, not a provenance one.** These are
*first-principles* fits. The corpus's **GaN** Caughey–Thomas row uses the empirical
Monte-Carlo set of Farahmand et al. Seeding AlN from Wang 2025 while GaN stays on Farahmand
2001 would make the AlN/GaN pair non-comparable in class. Flagging so the decision is taken
knowingly.

**c) Farahmand really is paywalled.** Full citation for the acquisition list:
> M. Farahmand, C. Garetto, E. Bellotti, K. F. Brennan, et al.,
> "Monte Carlo simulation of electron transport in the III-nitride wurtzite phase materials
> system: binaries and ternaries," *IEEE Trans. Electron Devices* **48**(3), 535–542 (2001).
> DOI **10.1109/16.906448**

**Confidence:** high that Table SIII exists, is open access, and contains the quartet.
Medium on the direction labels — see (a).
**What would settle it:** open arXiv:2506.09240 in a PDF viewer and confirm the ∥/⊥ labels
on Table SIII. That is a two-minute check and it is the only thing standing between this
"gap" and a seeded row.

---

## What I could not do

- **Slack 1987 full text** is paywalled. Everything in §5 rests on the abstract. The two
  unresolved questions (same crystals above 500 K? c-axis resolved?) can only be answered
  from the PDF, and they decide the disposition of both AlN κ rows.
- **Liu et al. 2016 publish no numeric table** of the GaN pyroelectric coefficient; +4.5 is
  consistent with their Fig. 1 but I read it off a plot.
- **Matocha et al. APL 90, 123511 (2007)** is paywalled; I confirmed the citation and its role
  as one of the two GaN experimental anchors but not its numeric value or sign convention.
- **Which primary measurement Ioffe reports** for AlN B and for either density remains
  unknown, and on the evidence of the page's undifferentiated reference list, may be
  unknowable from Ioffe alone.

## Sources

- [Ioffe NSM — AlN mechanical properties](https://www.ioffe.ru/SVA/NSM/Semicond/AlN/mechanic.html)
- [Ioffe NSM — AlN basic parameters](https://www.ioffe.ru/SVA/NSM/Semicond/AlN/basic.html)
- [Ioffe NSM — GaN mechanical properties](https://www.ioffe.ru/SVA/NSM/Semicond/GaN/mechanic.html)
- [Ioffe NSM — GaN basic parameters](https://www.ioffe.ru/SVA/NSM/Semicond/GaN/basic.html)
- [Wang et al., Debye temperature of wurtzite AlN, Powder Diffr. 29(4) 352 (2014)](https://www.cambridge.org/core/journals/powder-diffraction/article/abs/debye-temperature-of-wurtzite-aln-determined-by-xray-powder-diffraction/B84909E9DB9987867A3BA18A6BDA281D)
- [Slack, Tanzilli, Pohl & Vandersande, The intrinsic thermal conductivity of AlN, JPCS 48 641 (1987)](https://www.sciencedirect.com/science/article/abs/pii/0022369787901533)
- [Rounds et al., Thermal conductivity of single-crystalline AlN, APEX 11 071001 (2018)](https://iopscience.iop.org/article/10.7567/APEX.11.071001)
- [Inyushkin et al., On the thermal conductivity of single crystal AlN, JAP 127 205109 (2020)](https://pubs.aip.org/aip/jap/article/127/20/205109/157307/On-the-thermal-conductivity-of-single-crystal-AlN)
- [Xu et al., Thermal conductivity of crystalline AlN, JAP (2019)](https://poplab.stanford.edu/pdfs/Xu-AlNthermalCondDefectsSizeEffects-jap19.pdf)
- [Liu, Fernández-Serra & Allen, First-principles study of pyroelectricity in GaN and ZnO, arXiv:1603.00657 / PRB 93 081205 (2016)](https://arxiv.org/abs/1603.00657)
- [Benbedra et al., The trigonal structure as a reference to access the spontaneous polarization of wurtzite crystals, arXiv:2210.17343](https://arxiv.org/pdf/2210.17343)
- [Mechanisms of pyroelectricity in three- and two-dimensional materials, arXiv:1803.04580](https://arxiv.org/pdf/1803.04580)
- [Bykhovski et al., Pyroelectricity in gallium nitride thin films, APL 69 3254 (1996)](https://pubs.aip.org/aip/apl/article/69/21/3254/66761/Pyroelectricity-in-gallium-nitride-thin-films)
- [Gaska, Shur & Bykhovski, Pyroelectric and Piezoelectric Properties of GaN-Based Materials, MRS Internet J. Nitride Semicond. Res. 4(S1) 57 (1999)](https://www.cambridge.org/core/journals/materials-research-society-internet-journal-of-nitride-semiconductor-research/article/pyroelectric-and-piezoelectric-properties-of-ganbased-materials/747820208A9E0728E8505BEFF53B3B05/core-reader)
- [Yan et al., Temperature dependence of the pyroelectric coefficient and the spontaneous polarization of AlN, APL 90 212102 (2007)](https://pubs.aip.org/aip/apl/article-abstract/90/21/212102/333605/Temperature-dependence-of-the-pyroelectric)
- [DOI 10.1063/1.2742589 resolves to: Surface acoustic wave device on AlGaN/GaN, APL 90 213506 (2007)](https://pubs.aip.org/apl/article/90/21/213506/333118/Surface-acoustic-wave-device-on-AlGaN-GaN)
- [Wang, Pant, Lee, Chen, Giustino & Kioupakis, Electron mobility in AlN from first principles, arXiv:2506.09240 (2025)](https://arxiv.org/abs/2506.09240)
- [Farahmand et al., Monte Carlo simulation of electron transport in the III-nitride wurtzite phase materials system, IEEE TED 48(3) 535 (2001)](https://www.semanticscholar.org/paper/Monte-Carlo-simulation-of-electron-transport-in-the-Farahmand-Garetto/adfebc8db1fb77c0e3a7cab416b664d36e89d6af)
- [Mg-Doped P-Type AlN Thin Film Prepared by Magnetron Sputtering, Micromachines 16(9) 1035 (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12471319/)
- [Ueno et al., X-ray observation of the structural phase transition of aluminum nitride under high pressure, PRB 45 10123 (1992)](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.45.10123)
- [Xia, Xia & Ruoff, Pressure-induced rocksalt phase of aluminum nitride, JAP 73 8198 (1993)](https://pubs.aip.org/aip/jap/article-abstract/73/12/8198/384604/Pressure-induced-rocksalt-phase-of-aluminum)
