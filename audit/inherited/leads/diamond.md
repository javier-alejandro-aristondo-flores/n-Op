# Provenance leads — diamond rows

Groundwork for a later adversarial audit. **These are leads, not verdicts.** Nothing here
rules on whether a CSV value is correct. Each entry says: what the row currently claims,
what literature it could be checked against, how well that literature matches, and how
confident I am that it is the right source.

Searched 2026-07-31. Where I found nothing, I say so.

---

## 0. First, the cheap check: do the internal pointers resolve?

Four rows point inward (`see accuracy-ledger.md`, `mvp-system`). I checked before searching.

**They do not resolve to citations. The accuracy-ledger points back at the CSVs.**

`9.1-accuracy-ledger.md:142-146` states, in its own words:

> Per-value citations are the `source` column of `physics/library/cert/reference-data/*.csv`,
> **which is canonical for them**

So `phonon-max-energy` and `debye-temperature` say "see accuracy-ledger" and the
accuracy-ledger says "see the CSV". That is a closed loop, not a hop. `mvp-system`
(`8.1-mvp-system.md:23-24`) carries the same two numbers — `~165 meV (~1332 cm⁻¹)`,
`~2200 K` — with no source either.

**The one exception is κ**, which does resolve, to a citation pair that is worth
examining closely. See §1.

| Row | Pointer | Resolves? |
|---|---|---|
| `phonon-max-energy` | accuracy-ledger | **No** — ledger disclaims and points back at CSV |
| `debye-temperature` | accuracy-ledger | **No** — same loop; Θ_D≈2200 K appears at `9.1:68` and `10.4-traps.md:278` uncited |
| `bandgap-indirect` | mvp-system | **No** — `8.1:23` states 5.47 eV with no source |
| `lattice-constant-a` | mvp-system | **No** — `8.1:17` states 3.567 Å with no source |
| `thermal-conductivity` ×2 | Pass C battery | **Yes, partly** — ledger `9.1:169` names two papers. See below. |

---

## 1. `thermal-conductivity`, diamond (type IIa) — the priority rows

### What the CSV says

| Row | T | Value | σ | Source cell | class |
|---|---|---|---|---|---|
| `transport-coefficients.csv:33` | 300 K | 2200 W/mK | ×0.15 | `exp 2000–2500; Feng–Lindsay–Ruan PRB 96 161201 (2017); Broido APL 91 231922 (2007)` | experimental |
| `transport-coefficients.csv:34` | 773 K | **620 W/mK** | ×0.4 | `Pass C battery anchor (interpolation ±40%; independent est. 600–700; 2026-06-10 re-audit)` | theory-interpolation |
| `transport-coefficients.csv:35` | 1100 K | **450 W/mK** | ×0.4 | `Pass C battery anchor (κ∝T^−1.2 consistency)` | theory-interpolation |

### Where the internal pointer lands

`9.1-accuracy-ledger.md:169` carries the κ(T) battery table:

> `| diamond | 2200 (exp 2000–2500) | 620 | 450 | Feng–Lindsay–Ruan PRB 96 161201 (2017); Broido APL 91 231922 (2007) |`

So the ledger attributes **all three** values, including 773 K and 1100 K, to that pair —
while the CSV declares the same two values `theory-interpolation`. The two canon artifacts
describe the same numbers differently. Whichever is right, one of them is not.

### Lead A — `Broido APL 91 231922 (2007)` appears to be about silicon and germanium, not diamond

**Full citation:** D. A. Broido, M. Malorny, G. Birner, N. Mingo, D. A. Stewart,
"Intrinsic lattice thermal conductivity of semiconductors from first principles",
*Appl. Phys. Lett.* **91**, 231922 (2007).

The published abstract states the method obtains "excellent agreement between calculated and
measured intrinsic lattice thermal conductivities of **silicon and germanium**." I found no
indication diamond is in it. It is also cited as ref [1] *inside* Feng–Lindsay–Ruan 2017 —
i.e. as the methods precedent, not as a diamond κ source.

**The diamond paper from that same group is a different one:** D. A. Ward, D. A. Broido,
D. A. Stewart, G. Deinzer, "Ab initio theory of the lattice thermal conductivity in
diamond", *Phys. Rev. B* **80**, 125203 (2009) — exact BTE solution, natural and
isotopically enriched diamond, "in very good agreement with experimental data".

**Confidence: high** that APL 91 231922 is Si/Ge. **Medium** that Ward 2009 is the paper
that was meant. **What would settle it:** open APL 91 231922 and confirm diamond is absent;
then check whether Ward 2009's numbers are the ones in the battery.

Worth noting against the PROVENANCE.md flag: the 2026-06-10 re-audit is recorded as having
missed *a mis-citation*. This is a candidate for a second one on the same quantity.

### Lead B — what Feng–Lindsay–Ruan 2017 actually says about diamond

**Full citation:** T. Feng, L. Lindsay, X. Ruan, "Four-phonon scattering significantly
reduces intrinsic thermal conductivity of solids", *Phys. Rev. B* **96**, 161201(R) (2017).
DOI 10.1103/PhysRevB.96.161201. Open copy read in full:
`https://engineering.purdue.edu/NANOENERGY/publications/Feng_PRB_2017_Four_Phonon.pdf`

What it states about diamond, quoted:

- "For diamond and Si the three-phonon predictions agree well with measured data at low
  temperature (<600 K for Si, **<900 K for diamond**), however, significant deviations from
  experiment occur at high temperatures."
- "at 1000 K, three-phonon scattering alone **overpredicts κ of diamond** … by 31% … as
  compared to experimental values."
- Abstract: "For silicon and diamond, the predicted thermal conductivity is **reduced by 30%
  at 1000 K** after including four-phonon scattering."
- Fig. 4 plots natural diamond κ over **200–1200 K**, dashed κ₃ vs solid κ₃₊₄, against
  measured symbols.

**Caution for whoever audits this:** the well-known numbers **2241 → 1417 W/mK at room
temperature** in this paper are **BAs, not diamond**. The abstract's "reduces the predicted
thermal conductivity from 2200 to 1400 W/m K at room temperature" is also BAs. Two BAs
numbers (2200-ish room-temperature κ) sit one paragraph from the diamond discussion and
collide numerically with diamond's own ~2200. That is a live confusion trap.

The paper gives **no diamond κ number in text** — its diamond values live only in Fig. 4.

**What would settle it:** digitize Fig. 4, or get the Supplemental Material.

### Lead C — the primary measurement papers for diamond κ above 300 K

These are the measurement papers the parent asked for. Ordered by how directly they cover
773 K and 1100 K.

**C1 — the one that spans the whole range.**
J. R. Olson, R. O. Pohl, J. W. Vandersande, A. Zoltan, T. R. Anthony, W. F. Banholzer,
"Thermal conductivity of diamond **between 170 and 1200 K** and the isotope effect",
*Phys. Rev. B* **47**, 14850–14856 (1993). DOI 10.1103/PhysRevB.47.14850.
Natural and synthetic single-crystal diamond; Debye and Callaway analysis. Also reprinted as
a chapter in Springer, DOI 10.1007/978-3-642-84888-9_12.

This is **the** primary source for diamond κ at 773 K and 1100 K. It is cited as ref [28]
inside Feng 2017 and is the blue-circle dataset in that paper's Fig. 4.
**Confidence: high** that this is the right source. Paywalled — I could not extract its
numeric table. **What would settle it: this paper's Table/figure data. Getting it is the
single highest-value acquisition on this list.**

**C2 — independent high-T measurement, type IIa specifically, with numbers I could read.**
J. W. Vandersande, "High temperature thermal and electric conductivities of diamond and
diamond films", *Proc. SPIE* **2428**, 610 (1995) — reported via OSTI record 552238:

> natural type IIa diamond (purest form): "room temperature thermal conductivity of
> **24–25 W/cm-K** which drops to **4–5 W/cm-K at 1000 °C**"

i.e. **2400–2500 W/mK at 300 K → 400–500 W/mK at 1273 K.**

Companion: J. Vandersande, C. Vining, A. Zoltan, "Thermal Conductivity of Natural Type IIa
Diamond", *NASA Tech Briefs* **16**(12), Dec 1992, report NPO-18609 — flash diffusivity on an
8.04 × 8.84 × 2.35 mm natural white type-IIa specimen, **500–1250 K**. NTRS record
19920000747 carries the method and range but not the numbers.

**Confidence: high** that these are genuine type-IIa high-T measurements in the right range.
**Medium** on the numbers, since 24–25 / 4–5 W/cm-K are rounded to one digit in a
secondary record. **What would settle it:** the SPIE paper or the full Tech Brief.

**C3 — 300 K anchor, high precision, modern.**
A. V. Inyushkin, A. N. Taldenkov, V. G. Ralchenko, A. P. Bolshakov, A. V. Koliadin,
A. N. Katrusha, "Thermal conductivity of high purity synthetic single crystal diamonds",
*Phys. Rev. B* **97**, 144305 (2018). **6–410 K only** — up to 24 W/cm·K (2400 W/mK) at room
temperature; 285 W/cm·K at the ~63 K maximum, highest ever for natural-isotope diamond.
Does **not** reach 773 K. Relevant to row 33, not rows 34/35.

**C4 — 300 K, the classic isotope pair.**
L. Wei, P. K. Kuo, R. L. Thomas, T. R. Anthony, W. F. Banholzer, "Thermal conductivity of
isotopically modified single crystal diamond", *Phys. Rev. Lett.* **70**, 3764 (1993).
Also D. G. Onn, A. Witek, Y. Z. Qiu, T. R. Anthony, W. F. Banholzer, *Phys. Rev. Lett.*
**68**, 2806 (1992). 300 K region.

**C5 — the exponent, measured, in a lower window.**
A. Sukhadolau, E. Ivakin, V. Ralchenko, A. Khomich, A. Vlasov, A. Popovich, "Thermal
conductivity of CVD diamond at elevated temperatures", *Diamond Relat. Mater.* **14**(3),
589–593 (2005). Measured **293–460 K**, fitted κ ∝ T⁻ⁿ with **n = 0.17–1.02**, varying with
diamond quality. CVD, not single-crystal type IIa — but it is the only *measured* exponent
I found in an overlapping window, and it does not reach 1.2.

**C6 — older type IIa high-T.**
R. Berman, P. R. W. Hudson, M. Martinez, *J. Phys. C* **8**, L430 (1975) — cited as ref [29]
of Feng 2017's diamond comparison set. Also G. A. Slack, *J. Phys. Chem. Solids* **34**,
321 (1973). Not retrieved.

### The spread I actually found

| Source | 300 K | 773 K | 1100 K | 1273 K |
|---|---|---|---|---|
| CSV / ledger | 2200 (exp 2000–2500) | 620 | 450 | — |
| Vandersande SPIE 1995 (type IIa, measured) | 2400–2500 | — | — | 400–500 |
| Inyushkin PRB 2018 (measured) | 2400 | — | — | — |
| Feng 2017 (κ₃₊₄, calc) | Fig. 4 only | Fig. 4 only | Fig. 4 only | — |
| Olson PRB 1993 (measured, 170–1200 K) | **not retrieved — the gap** | | | |
| GaN-on-diamond device models (engineering) | often 1200–2200, κ ∝ (300/T)¹·⁰ | | | |

So: **at 300 K the measured spread is ~2000–2500 and the CSV's 2200 sits inside it. Above
300 K I could not find a primary number to compare 620 and 450 against.** The one measured
high-T anchor I did find (Vandersande, 400–500 W/mK at 1273 K) is *above* what the CSV's
own trend extrapolates to at that temperature, but that is one rounded secondary quote and
is not a basis for any conclusion.

### Lead D — an internal arithmetic check anyone can run without literature

The 1100 K row's stated justification is `κ∝T^−1.2 consistency`. The three CSV values do not
sit on a T^−1.2 line, and are not self-consistent with each other under any single exponent:

| Interval | exponent implied by the CSV's own numbers |
|---|---|
| 300 → 773 K | **T^−1.34** |
| 773 → 1100 K | **T^−0.91** |
| 300 → 1100 K | T^−1.22 |

And applying the stated law to the stated anchor: 620 × (1100/773)^−1.2 = **406**, not 450.
From 2200 at 300 K: T^−1.2 gives **707 at 773 K** and **463 at 1100 K**.

Two things follow, both worth registering as leads and neither a verdict:

1. The endpoints (300 and 1100 K) are consistent with T^−1.2 to about 3%; the **middle
   point is not on that line**. Whatever produced 620 was not the stated law.
2. The implied exponent **decreases** with temperature (1.34 → 0.91). Four-phonon scattering
   makes the high-T falloff *steeper*, not shallower — the corpus's own ledger row 121 is
   the 4-phonon correction, valid `T ≳ 0.4 Θ_D`. So the shape runs against the physics the
   ledger says it embodies.

**Confidence: high** (it is arithmetic on the corpus's own numbers). **What would settle it:**
whatever produced 620 — the "independent est. 600–700" the source cell mentions has no
named origin anywhere I could find.

### Lead E — the Θ_D coupling, which changes whether 773 K is even in the 4-phonon window

The 4-phonon correction is declared valid `T ≳ 0.4 Θ_D`. `9.1:68` computes that as
"diamond ≈880 K", i.e. from Θ_D = 2200 K. **If Θ_D is instead 1860 K (see §6), the threshold
is 744 K and the 773 K point falls inside the window; at 2200 K it falls outside.** The
Debye-temperature row and the κ(773 K) row are not independent. Registering the coupling
here so auditor 2 does not treat them separately.

---

## 2. `bandgap-indirect`, diamond — 5.47 eV ± 0.01, 300 K

**Internal pointer:** dead (§0).

**Candidate source, classic:** C. D. Clark, P. J. Dean, P. V. Harris, "Intrinsic edge
absorption in diamond", *Proc. R. Soc. Lond. A* **277**, 312 (1964). This is the paper the
5.47/5.5 eV textbook value traces to — temperature-dependent absorption-edge spectra.
**Confidence: high** that this is the origin of the number.

**Candidate source, modern, and it disagrees at the σ the CSV claims:**
"Bandgap evolution of diamond", *Diamond Relat. Mater.* **132**, 109638 (2022) (Xi'an
Jiaotong Univ.). Re-measured the phonon-assisted intrinsic absorption edge of
electronic-grade single-crystal diamond over **10–620 K** and reports the indirect gap as
**5.480 ± 0.004 eV near 0 K**, explicitly framed as a re-evaluation of "the specific value
and temperature dependence".

The CSV's 5.47 is a 300 K value and 5.480 is a ~0 K value, so these need not conflict — but
the CSV's σ is ±0.01 eV, and the difference between the two figures is 0.010 eV. Whether
they agree depends entirely on the 300 K→0 K shift, which is exactly what the 2022 paper
re-measured. **Confidence: high** that both papers exist and say this. **Low** on whether
they agree. **What would settle it:** the 300 K number from each paper, side by side.

---

## 3. `cohesive-energy`, diamond — 7.37 eV/atom ± 0.05, 0 K

Source cell: `standard experimental atomization anchor`.

**This is the most interesting of the "standard value" rows, because 7.37 may be graphite.**

**Primary trail:** the tabulated experimental cohesive energies of carbon come from
**L. Brewer, Lawrence Berkeley Laboratory Report LBL-3720 (unpublished)** — the source
Kittel's *Introduction to Solid State Physics* cohesive-energy table credits ("The data were
supplied by Prof. Leo Brewer", confirmed in the 8th-edition text). Kittel's table lists
C(diamond) at 7.37 eV/atom / 711 kJ/mol, which is very likely where the CSV's number comes
from.

**But the same Brewer source, as quoted in a paper that used it as its experimental
benchmark, splits the two allotropes:**

H. Shin, S. Kang, J. Koo, H. Lee, J. Kim, Y. Kwon, "Cohesion energetics of carbon
allotropes: Quantum Monte Carlo study", *J. Chem. Phys.* **140**, 114702 (2014);
arXiv:1401.0105. Table I, "Exp." column, citing Brewer LBL-3720:

| | Exp. cohesive energy |
|---|---|
| **Graphite** | **7.374 eV/atom** |
| **Diamond** | **7.346 eV/atom** |

Difference **28 meV/atom** — and the paper's own DMC result for the graphite−diamond
difference is ~27 meV/atom, "basically identical to the experimentally-reported value".

So `7.37` matches **graphite** (7.374) to 3 decimal places and diamond (7.346) only to
within 24 meV. **Confidence: high** on the Shin table values as quoted. **Medium** on the
claim that Kittel labels 7.37 as diamond — I confirmed the Brewer attribution in Kittel's
text but the table itself is a graphic in the PDF I read and I did not read the cell.

**Why this matters beyond one row:** 24–28 meV/atom is the same size as the
`formation-energy-vs-graphite` row (+25 meV/atom) it has to be consistent with, and it is
half the row's own stated σ (±0.05 eV/atom = 50 meV), so the σ hides the discrepancy.

**What would settle it:** Kittel Table 3 of Ch. 3, cell for C(diamond); or Brewer LBL-3720
directly.

---

## 4. `formation-energy-vs-graphite`, diamond — +25 meV/atom ± 5, 300 K / 1 atm

Source cell: `Berman–Simon boundary point`.

**The eponym resolves cleanly:** R. Berman, F. Simon, "On the Graphite–Diamond Equilibrium",
*Z. Elektrochem.* **59**, 333 (1955); companion note "The Graphite–Diamond Equilibrium",
*Nature* **176**, 834 (1955). The Berman–Simon line is **P (atm) = 7000 + 27·T (K)**, stated
by the authors as valid **above 1200 K** and accurate to ~5%.
**Confidence: high** on the citation.

**But the Berman–Simon line is a pressure, not an energy**, and 300 K is 900 K below its
stated validity floor. Calling +25 meV/atom "a Berman–Simon boundary point" is a category
step that needs to be shown, not asserted. It is *derivable* — here is the arithmetic:

- Berman–Simon extrapolated to 300 K: P = 7000 + 27(300) = **15,100 atm = 1.53 GPa**
- ΔV(graphite→diamond) ≈ 1.88 cm³/mol
- P·ΔV = 2.88 kJ/mol = **29.8 meV/atom**

which lands on the standard thermochemical value, not on 25:

| Quantity, 298 K, 1 atm | value | meV/atom |
|---|---|---|
| ΔfG°(diamond) − ΔfG°(graphite) | 2.900 kJ/mol | **30.1** |
| ΔfH°(diamond) − ΔfH°(graphite) | 1.895 kJ/mol | **19.6** |
| Berman–Simon via P·ΔV | 2.88 kJ/mol | **29.8** |
| Brewer cohesive-energy difference (§3) | — | **28** |
| **CSV row** | — | **25 ± 5** |

**The CSV's 25 sits almost exactly midway between ΔH (19.6) and ΔG (30.1)**, and its ±5
does not reach either. The row's name — "formation energy" — does not say which one it is,
and the three defensible readings (ΔH, ΔG, 0 K ΔE-with-ZPE) differ by more than the σ.

**Confidence: high** on the tabulated thermochemistry (these are standard NIST-JANAF/CRC
values). **Low** on which one the row means. **What would settle it:** a statement of which
thermodynamic potential the row is, plus a check of whether `registry row 124`'s
`tp-aware-hull` R=0 reading depends on the choice.

---

## 5. `lattice-constant-a`, diamond — 3.567 Å ± 0.001, 300 K, and `mass-density` — 3.515 g/cm³ ± 0.001

Source cells: `curated MVP anchor (mvp-system; standard XRD value)` and `standard`.

**Named source for the lattice constant, high confidence:**
T. Hom, W. Kiszenick, B. Post, "Accurate lattice constants from multiple reflection
measurements. II. Lattice constants of germanium, silicon, and diamond", *J. Appl. Cryst.*
**8**, 457 (1975). Reported **a = 3.566986 Å** at 25 °C, relative uncertainty 2.6 × 10⁻⁶.
This is the standard XRD reference for diamond's lattice constant and is used as such by
other work (it is ref [40] of the Shin QMC paper, cited exactly for the diamond bond length).
**Confidence: high.** The CSV's 3.567 ± 0.001 is Hom rounded, with a σ ~400× looser than the
measurement's.

**Corroborating database:** Ioffe NSM Archive, Diamond → Basic Parameters
(`https://www.ioffe.ru/SVA/NSM/Semicond/Diamond/basic.html`) lists lattice constant 3.567 Å,
density 3.515 g/cm³, dielectric constant 5.7. The page names no primary references — same
"named without a locator" problem PROVENANCE.md §C already flags for the AlN/GaN Ioffe rows.

**`mass-density` is not an independent measurement — it is derivable from the row above:**

  ρ = 8 M / (N_A a³) = 8 × 12.011 / (6.02214076×10²³ × (3.5670×10⁻⁸ cm)³) = **3.5157 g/cm³**

matching the CSV's 3.515 to its stated σ. **Confidence: high.** This is the same situation
PROVENANCE.md §A already accepts for β-Ga₂O₃'s density ("crystallographic, derived from the
Åhman cell") — so the honest fix may be reclassifying diamond's density from class B to
class A, citing Hom 1975 + the standard atomic weight rather than naming a κ-style source.
(Note the atomic weight matters at the stated precision: natural-abundance M = 12.011 gives
3.5157; pure ¹²C gives 3.5125.)

---

## 6. `debye-temperature`, diamond — 2200 K ± 50

**Internal pointer:** dead (§0). Θ_D ≈ 2200 K appears uncited at `9.1:68`, `8.1:24`,
`10.4-traps.md:278`, `11.7:32`.

**No single source found — and the literature spread is far wider than ±50 K.** What I found:

| Value | Method | Where |
|---|---|---|
| **1860 K** | from measured elastic constants | Ioffe NSM Archive, Diamond → Basic Parameters |
| **1880 ± 10 K** | extrapolation of high-T heat-capacity data | secondary sources |
| **~1850 K** | textbook (Solid State Physics, Rohlf/other) | secondary |
| **2230 K** | Kittel-style low-T specific-heat Debye table | standard textbook problems |
| **1800–2200 K** | stated range | secondary compilations |
| **2200 ± 50 K** | — | **the CSV** |

Θ_D for diamond is **method-dependent by ~20%**, and the CSV's ±50 K (2.3%) is far tighter
than the spread between the two standard determinations. The corpus's own
`physics/research/diamond-stretch-and-skew-sweep/03-what-is-derivable.md:84` calls
2200 K the "**elastic** Debye temperature" expectation — but Ioffe attributes 1860 K to the
elastic route, so even the method label is contested.

**Confidence: high** that the spread is real and large. **Low** that any single source is
"the" one — this may be a row where the honest answer is a named method plus a wider σ, or
`UNSEEDED`. **What would settle it:** decide which Θ_D the corpus needs (elastic /
low-T calorimetric / high-T limit), because they are different numbers, then cite that one.
**This row is coupled to κ(773 K) — see §1 Lead E.** It is not a low-stakes row.

---

## 7. `phonon-max-energy`, diamond — 165 meV ± 0.5, 300 K

**Internal pointer:** dead (§0). `8.1:23` writes `~165 meV (~1332 cm⁻¹)`.

**The 1332 cm⁻¹ identification is solid.** The Γ-point triply-degenerate Raman mode of
diamond is 1332.5 cm⁻¹; 1332.5 × 0.1239842 = **165.21 meV**, matching the CSV to well
within σ. Standard citation: S. A. Solin, A. K. Ramdas, "Raman spectrum of diamond",
*Phys. Rev. B* **1**, 1687–1698 (1970) — its polarization study is what established the
1332 cm⁻¹ line as the zone-centre optical phonon of Γ₂₅⁺ (F_2g) symmetry.
**Confidence: high** on the number and the mode.

**But the row is named `phonon-max-energy`, and Γ is not the maximum of diamond's
dispersion.** Diamond's LO branch **overbends** — it rises above the Γ frequency away from
zone centre. Measured:

- J. Kulda, B. Dorner, B. Roessli, H. Sterner, R. Bauer, Th. May, K. Karch, P. Pavone,
  D. Strauch, "A neutron-scattering study of the overbending of the [100] LO phonon mode in
  diamond", *Solid State Commun.* **99**, 799 (1996) — first clear evidence of a maximum
  above the Γ-point frequency.
- J. Kulda, H. Kainzmaier, D. Strauch, B. Dorner, M. Lorenzen, M. Krisch, "Overbending of
  the longitudinal optical phonon branch in diamond as evidenced by inelastic neutron and
  x-ray scattering", *Phys. Rev. B* **66**, 241202(R) (2002) — overbending measured along all
  three principal directions: **1.5 meV (Δ, i.e. Γ–X), 0.5 meV (Λ), 0.2 meV (Σ)**.

So the true maximum phonon energy is ≈ 165.2 + 1.5 = **166.7 meV** — **3× the row's stated
σ of 0.5 meV above the row's value.**

Whether that matters depends on what consumes the row. `8.1:23`'s consequence column says
"phonon grid must resolve it", and `11.8:511` feeds ω_phonon = 165 meV into
`v-sat-intervalley`. A grid ceiling and an intervalley emission energy are arguably
different quantities from the Raman line.

**Confidence: high** on both the Kulda measurements and the arithmetic.
**What would settle it:** state whether the row means the Γ Raman mode or the dispersion
maximum, then cite Solin–Ramdas 1970 or Kulda 2002 accordingly. Also usable:
"Critical-point phonon frequencies of diamond", *Phys. Rev. B* **45**, 12854 (1992), which
tabulates the critical-point frequencies as a set.

---

## 8. `dielectric-static`, diamond — 5.7 ± 0.05, 300 K

Source cell: `standard value (feeds image-force lowering; Fröhlich inert — non-polar)`.

**No primary measurement paper found.** Every trail led to compilations, not to a
measurement.

- **Ioffe NSM Archive**, Diamond → Basic Parameters: "Dielectric constant (10²–10⁴ Hz): 5.7",
  with no reference named. **Confidence: medium** that this is where "standard" comes from
  (the corpus already uses Ioffe NSM as a source string for AlN/GaN); **low** as a
  provenance, since Ioffe names nobody.
- Measured CVD diamond values cluster nearby but not on it: **5.57** with loss tangent 0.007
  in one wide-frequency CVD-diamond study; ~5.7 quoted at 1 MHz elsewhere. Vendor data
  (Element Six, Sumitomo) quote 5.7.

The frequency window matters and the row does not state one. Since diamond is non-polar
there is no LO–TO splitting, so ε_static should equal ε_∞ = n² — an independent and cheap
cross-check the corpus could run instead of citing anybody. It works, but only at the right
wavelength: n ≈ 2.38 in the long-wavelength IR gives **n² = 5.66**, agreeing with 5.7 to
within the row's σ; n = 2.4175 at 589 nm gives 5.84, which does not. Note `9.1:87` consumes
ε_s = 5.7 in the image-force lowering formula, so the row is load-bearing.

**Confidence: low** on any specific source. **This is a genuine "no primary source found"
result.** **What would settle it:** either a named measurement (a Landolt–Börnstein or CRC
entry with its own citation would do), or a decision to derive it from the optical
refractive index and cite that instead.

---

## Summary table

| Row | Best candidate source | Match | Confidence |
|---|---|---|---|
| `thermal-conductivity` 773 K | Olson PRB 47 14850 (1993) — **not retrieved** | unknown | high that it's the right source, none on the value |
| `thermal-conductivity` 1100 K | same; + Vandersande SPIE 2428 610 (1995) | Vandersande gives 400–500 @ 1273 K | medium |
| `thermal-conductivity` 300 K | Feng PRB 96 161201 (2017) + Ward PRB 80 125203 (2009) | 2200 inside measured 2000–2500 | high on 300 K; **`Broido APL 91 231922` looks like Si/Ge** |
| `bandgap-indirect` | Clark–Dean–Harris Proc. R. Soc. A 277 312 (1964) | 5.47 is that lineage | high (source), low (vs 2022's 5.480) |
| `cohesive-energy` | Brewer LBL-3720 via Kittel | **7.374 = graphite; diamond = 7.346** | high on the split, medium on the trail |
| `formation-energy-vs-graphite` | Berman & Simon Z. Elektrochem. 59 333 (1955) | line is P–T; 25 sits between ΔH 19.6 and ΔG 30.1 | high (citation), low (which potential) |
| `lattice-constant-a` | Hom–Kiszenick–Post J. Appl. Cryst. 8 457 (1975) | 3.566986 Å | high |
| `mass-density` | derived from Hom + M=12.011 → 3.5157 | exact | high |
| `debye-temperature` | **none** — spread 1860–2230 K by method | ±50 K far too tight | low |
| `phonon-max-energy` | Solin–Ramdas PRB 1 1687 (1970) for Γ; Kulda PRB 66 241202 (2002) for the true max | Γ = 165.2 ✓; max ≈ 166.7 | high |
| `dielectric-static` | **none found** — Ioffe NSM, unreferenced | 5.7 | low |

**Two rows where "no source found" is the honest result: `dielectric-static` and
`debye-temperature`.** Neither is a small row — ε_s feeds image-force lowering, Θ_D sets the
4-phonon validity window that the κ(773 K) row depends on.

**The single highest-value acquisition on this list is Olson et al., PRB 47, 14850 (1993).**
It is the only primary measurement spanning 170–1200 K, both high-temperature κ rows depend
on it, and I could not get its numbers.
