# Provenance leads — β-Ga₂O₃

Groundwork for auditor 2. **These are leads, not verdicts.** No value below is ruled
correct or incorrect; where a match looks bad it is described, not adjudicated.

Four rows in `physics/library/cert/reference-data/*.csv` whose `Source` cell names no
author and no year. Two resolve to named primary literature with high confidence, one
resolves internally but with a caveat that changes its wording, and the priority row —
`displacement-threshold-Ed` — turns out to have a real literature behind it whose
**shape is not a scalar**.

---

## 1. `displacement-threshold-Ed` — the priority row

`material-constants.csv:42` · β-Ga₂O₃ (C2/m) · **25 eV ± 5** · provenance-type
`literature-review` · Source `literature (carried from non-equilibrium stratum H.1;
multiscale-state §4)`

### The headline finding: the literature's shape is a five-site table plus a directional map

β-Ga₂O₃ has two inequivalent Ga sites and three inequivalent O sites, and the modern
literature reports E_d **per site**, with a strong additional dependence on recoil
direction. A single scalar is a modeling choice, not a measurement. The corpus's
`~25 eV` corresponds to no per-site value in the current literature.

The internal audit (`journal/live/audits/2026-07-16-wave2-beta-ga2o3-audit.md`) **does
not mention this row at all** — not in the number verdicts, not in the GAP register, not
in the acquisition items. It was never audited. The `literature-review` provenance-type
is unsupported by any internal document.

### Candidate A — the directional map (most complete source)

**He, H., Zhao, J., Byggmästar, J., He, R., Nordlund, K., He, C., & Djurabekova, F.
(2024). "Threshold displacement energy map of Frenkel pair generation in β-Ga₂O₃ from
machine-learning-driven molecular dynamics simulations." *Acta Materialia* **276**,
120087.** DOI [10.1016/j.actamat.2024.120087](https://doi.org/10.1016/j.actamat.2024.120087).
Open access (CC BY-NC-ND). **Read in full** (open copy:
`https://www.mv.helsinki.fi/home/knordlun/pub/He24.pdf`).

Method: >5,000 MD simulations with the tabGAP machine-learned interatomic potential,
10,240-atom cell, ~5,500 recoil directions, >1,000 per PKA type. E_d averaged over solid
angle by their Eq. 1.

| Site | Coordination | Mean E_d | Median E_d |
|---|---|---|---|
| Ga1 | tetrahedral | **22.91 eV** | 22 eV |
| Ga2 | octahedral | **20.04 eV** | 18 eV |
| O1 | 3-fold | **17.44 eV** | 15 eV |
| O2 | 3-fold | **17.38 eV** | 15 eV |
| O3 | 4-fold | **17.07 eV** | 14 eV |

Directional spread, which is the part a scalar destroys:

- **Minimum E_d for every PKA type is ~7–8 eV** (§4, verbatim: "the minimum E_d values
  for each PKA type are very low, approximately ranging from 7 to 8 eV").
- **Maximum exceeds 60 eV** for O1 and O3; reaches 43 eV for O2. Values above 40 eV are
  statistically rare.
- Ga1 recoils with polar angle θ near 90° are hardest — "most of them exceeding 30 eV"
  and some >60 eV; Ga1 is least likely to be displaced nearly parallel to the (010) plane.
- The paper states plainly: *"the TDE value is strongly crystal direction-dependent,
  hence, sufficient sampling of random displacement directions is required for more
  accurate value of TDE."*
- It estimates that **more than 5 × 90 × 360 directions** are needed for a standard TDE
  map of β-Ga₂O₃.

**Monoclinic trap the paper flags explicitly** and that the corpus's never-average rule
should inherit: *"the direction of [100] is not perpendicular to the (100) plane, which
can potentially lead to misleading interpretations."*

### Candidate B — the AIMD scalar pair

**Tuttle, B. R., Karom, N. J., O'Hara, A., Schrimpf, R. D., & Pantelides, S. T. (2023).
"Atomic-displacement threshold energies and defect generation in irradiated β-Ga₂O₃: A
first-principles investigation." *Journal of Applied Physics* **133**(1), 015703.**
DOI [10.1063/5.0124285](https://doi.org/10.1063/5.0124285).

- **Ga: 28 ± 1 eV · O: 14 ± 1 eV** (DFT-based AIMD).
- He et al. compare against these directly and attribute the difference to their own
  larger cell (10,240 atoms) and to treating Ga 3d as valence rather than fixed-core.
  Both studies agree on the ordering: Ga E_d > O E_d.
- These are the values that circulate as **SRIM practice** for Ga₂O₃ (28 eV Ga /
  14 eV O), typically paired with density 5.88 g/cm³.

### Candidate C — the likely actual origin of "25 eV"

**Chaiken, M. F., & Blue, T. E. (2018). "An Estimation of the Neutron Displacement
Damage Cross Section for Ga₂O₃." *IEEE Transactions on Nuclear Science* **65**,
1147–1152.**

This is the strongest candidate for where a bare parenthetical `Ga₂O₃ ~25 eV` in a
radiation-damage context would have come from. It is cited downstream specifically as
*"Chaiken and Blue studied the neutron radiation effects of β-Ga₂O₃, and the threshold
displacement energy (E_d) of Ga atoms was determined to be 25 eV"* — note **of Ga
atoms**, not of the material. Coupled neutronics + PKA transport simulation.

**Unresolved and important:** whether Chaiken & Blue *derived* 25 eV or *assumed* it from
an earlier source. The full text is behind IEEE (both the published version and the
accepted manuscript bot-blocked, 403/418). If they assumed it, the chain continues and
the corpus's provenance problem is inherited rather than solved.

### Match to the CSV value

| Reading of "25 eV ± 5" | Assessment |
|---|---|
| Ga sublattice only | ±5 spans 20–30 eV, which covers Ga1 22.9, Ga2 20.0, and Tuttle's Ga 28. Defensible. |
| Material-wide scalar | Sits above all three O sites (17.0–17.4) by more than the O values plus the band's lower edge; the O sublattice is the softer one and therefore the one that governs damage onset. |
| A minimum | Contradicted — minima are ~7–8 eV. |
| An average | Contradicted by He et al.'s own solid-angle averages, none of which is 25. |

The row carries no site tag and no direction tag, while every other β-Ga₂O₃ row seeded in
the Wave-2 pass was direction-tagged per the never-average rule. **This row is the
exception to a rule the corpus applied everywhere else in the same material.**

### Consequence for the NRT formula the corpus uses

`N_d = 0.8·T_dam/(2·E_d)` (`11.5-deriv-high-field.md:407`, restated at
`2.4-multiscale-state.md:199`) takes one scalar E_d. For a five-site material with
per-site averages 17–23 eV and directional minima of 7–8 eV, the scalar is a modeling
decision. Which site (or which average over sites) belongs in the denominator is a
question the corpus has never posed. Registering it here because deleting chapter 11
deletes the only place the formula and the number appear together.

### Confidence and what would settle it

- **He et al. 2024 exists and says what is quoted above: certain** (read in full).
- **Tuttle et al. 2023 values: high** (publisher abstract + He et al.'s citation of them).
- **Chaiken & Blue is the origin of the corpus's 25: moderate.** Plausible and
  well-matched to the context, but not demonstrated.
- **25 eV as a defensible present-day scalar for the material: low.** No post-2022 study
  reproduces it as a material value.

**What would settle it:** (a) read Chaiken & Blue's full text and see whether 25 eV is
derived or assumed; (b) decide whether the corpus wants a per-site table (He et al.) or a
single NRT-input scalar, and if the latter, state the averaging convention explicitly
rather than carrying a bare number.

### Further reading found but not chased

- Tuttle-adjacent: "A first-principles study of low-energy radiation responses of
  β-Ga₂O₃", *J. Appl. Phys.* **136**(6), 065901 (2024).
- "Orientation-dependent surface radiation damage in β-Ga₂O₃ explored by atomistic
  simulations", *Acta Materialia* (2025).
- "Ultrahigh stability of oxygen sublattice in β-Ga₂O₃" (2024) — bears directly on the
  γ/β polymorphic radiation-tolerance story.
- "Radiation effects in β-Ga₂O₃-based devices: From atomic-scale damage to radiation
  hardening strategies", *J. Appl. Phys.* **140**(4), 040701 (2026) — a recent review;
  likely the fastest route to a settled community value if one exists.

---

## 2. `mass-density` — resolves cleanly

`elastic-tensors.csv:26` · **5.96 g/cm³ ± 0.02** · `derived-experimental` · Source
`crystallographic from the Åhman cell (Z=4)`

**Åhman, J., Svensson, G., & Albertsson, J. (1996). "A Reinvestigation of β-Gallium
Oxide." *Acta Crystallographica Section C* **52**, 1336–1338.**
DOI [10.1107/S0108270195016404](https://doi.org/10.1107/S0108270195016404).

Cell: monoclinic C2/m, a = 12.214 Å, b = 3.0371 Å, c = 5.7981 Å, β = 103.83°,
V = 208.85 Å³, Z = 4 → **ρ = 5.961 g/cm³**.

- **Match: exact.** 5.961 → 5.96 as seeded.
- **Confidence: high.** Standard structure determination for the material; supersedes
  Geller, *J. Chem. Phys.* **33**, 676 (1960).
- **This was already resolved internally and never propagated.** The Wave-2 audit's
  §2 "Pins landed" states: *"Åhman, Svensson & Albertsson, Acta Cryst. C52 1336 (1996)
  (lattice; ρ 5.96 derived)"*. The citation existed on 2026-07-16 and simply never
  reached the CSV cell. **It is lost when that audit file is deleted.**
- **What would settle it:** nothing. Fill the cell in.

**One discrepancy an auditor will meet:** radiation-damage papers running SRIM on Ga₂O₃
commonly use **5.88 g/cm³**. Not a contradiction of Åhman — a different (probably
measured, possibly polycrystalline) figure. Worth knowing before it looks like one.

---

## 3. `mobility-electron-best-exp` — all three compilation entries trace to primaries

`transport-coefficients.csv:53` · **150–200 cm²/Vs** at 300 K · `experimental` · Source
`bulk CZ 152 / MOCVD 176-~200 / 2DEG 180 (Wave-2 audit compilation)`

The audit **does not resolve this internally** — its §2 restates the same compilation
(*"best measured μ 150–200 (bulk CZ 152 / MOCVD 176–~200 / 2DEG 180)"*) without naming a
single primary source. Found externally:

| Entry | Primary source | Value given | Match | Confidence |
|---|---|---|---|---|
| **2DEG 180** | Zhang, Y., Neal, A., Xia, Z., Joishi, C., Zheng, Y., Bajaj, S., Brenner, M., Mou, S., Dorsey, D., Chabak, K., Jessen, G., Hwang, J., Heremans, J., & Rajan, S. — "High mobility two-dimensional electron gas in modulation-doped β-(Al_xGa₁₋ₓ)₂O₃/Ga₂O₃ heterostructures", *Appl. Phys. Lett.* **112**, 173502 (2018); arXiv:1802.04426 | Verbatim: *"The room temperature mobility was measured to be 162 cm²/Vs and 180 cm²/Vs for sample A and B, respectively."* Peak 2790 cm²/Vs at 50 K (sample B); sheet density 2.05–2.25×10¹² cm⁻² | **exact** | **high** — read in full |
| **MOCVD 176** | Zhang, Y., Alema, F., Mauze, A., Koksaldi, O. S., Miller, R., Osinsky, A., & Speck, J. S. — "MOCVD grown epitaxial β-Ga₂O₃ thin film with an electron mobility of 176 cm²/V s at room temperature", *APL Materials* **7**, 022506 (2019) | 176 cm²/V·s at RT; 3481 cm²/V·s at 54 K; net background 7.4×10¹⁵ cm⁻³; UID film | **exact** (the number is in the title) | **high** |
| **MOCVD ~200** | Peterson, C., Bhattacharyya, A., Chanchaiworawit, K., Kahler, R., Roy, S., Liu, Y., Rebollo, S., Kallistova, A., Mates, T. E., & Krishnamoorthy, S. — "200 cm²/Vs electron mobility and controlled low 10¹⁵ cm⁻³ Si doping in (010) β-Ga₂O₃ epitaxial drift layers", *Appl. Phys. Lett.* **125**(18), 182103 (2024) | up to 200 cm²/Vs RT Hall, 4.5 µm Si-doped film, n in 10¹⁵ cm⁻³ range | **exact** | **high** |
| **bulk CZ 152** | Galazka, Z., et al. — "Czochralski-grown bulk β-Ga₂O₃ single crystals doped with mono-, di-, tri-, and tetravalent ions", *J. Cryst. Growth* **529**, 125297 (2020), DOI 10.1016/j.jcrysgro.2019.125297 | undoped CZ crystals: Hall mobility **80–152 cm²/V·s** | 152 is the **top of a range**, not a headline record | **moderate** — the number matches but the attribution is inferred; 152 also circulates as the quoted bulk benchmark in Peterson et al. 2024 |

**Not named by the compilation but sitting inside its range:** Feng, Z., Bhuiyan,
A. F. M. A. U., Karim, M. R., & Zhao, H. — "MOCVD homoepitaxy of Si-doped (010) β-Ga₂O₃
thin films with superior transport properties", *Appl. Phys. Lett.* **114**, 250601
(2019): **184 cm²/V·s** at RT (n = 2.5×10¹⁶ cm⁻³), 4984 cm²/V·s at 45 K. Read in full.
The `176–~200` bracket silently contains this without citing it.

### Two flags for auditor 2 (not verdicts)

1. **The row mixes three different physical systems** under one `experimental` tag: a
   bulk melt-grown crystal, an epitaxial thin film, and a **modulation-doped 2DEG**. A
   2DEG channel mobility is a heterostructure property, not a bulk material constant —
   the whole point of modulation doping is that it beats bulk by spatially separating
   carriers from donors. Whether it belongs in a bulk-material row is a scoping question
   the compilation never poses.
2. **The upper end is at the theoretical ceiling.** Peterson et al. state 200 cm²/Vs
   *"reaching the predicted theoretical maximum room temperature phonon scattering-limited
   mobility"*, consistent with the corpus's own polar-optical-phonon-limited μ < 200
   statement. A "best experimental" band whose top coincides with the phonon limit is
   physically sensible but leaves no headroom — relevant if the band is used as a σ-trip
   window.

**What would settle the one soft entry:** read the reference Peterson et al. 2024 cite
for "152", which is the cleanest arbiter of which Galazka paper the number belongs to.

---

## 4. `caughey-thomas-mu-n-set` — resolves internally, but the wording needs narrowing

`transport-coefficients.csv:65` · value `GAP — no consensus published fit; derive from
μ(N_D) or acquire` · provenance-type `gap` · Source `Wave-2 audit confirmed genuine`

**This one does resolve internally.** The audit's §3 GAP register carries it explicitly:
*"Genuine and carried: C–T electron quartet (no consensus published fit — derive from
μ(N_D) or acquire)"*. The Source cell is an accurate pointer. When the audit file is
deleted, that sentence is the thing to lift out.

### But: published C–T-form parameter sets for β-Ga₂O₃ do exist

The claim *"no **consensus** published fit"* survives. The claim *"no published fit"*
would not. Found:

- **Jang, C.-H., Atmaca, G., & Cha, H.-Y. (2022). "Normally-off β-Ga₂O₃ MOSFET with an
  epitaxial drift layer." *Micromachines* **13**(8), 1185.**
  DOI [10.3390/mi13081185](https://doi.org/10.3390/mi13081185). Table 1, explicit
  Caughey–Thomas form: **μ_min = 20 cm²/Vs, μ_max = 155 cm²/Vs, N_ref = 1.0×10¹⁸ cm⁻³,
  α = β = γ = 0, δ = 0.8, T_L = 300 K.** The authors state these were determined from
  Ga₂O₃ experimental data (their refs 28–29), not adopted from another material.
- **Ong, E. K. J., Nguyen, L. M. L., Eng, M., Zhang, Y., & Wong, H. Y. — "Ga₂O₃ TCAD
  Mobility Parameter Calibration using Simulation Augmented Machine Learning with
  Physics-Informed Neural Network", arXiv:2504.02283.** Read in full. Uses the **Philips
  Unified (PhuMob)** model, *not* Caughey–Thomas — a different functional form, so it
  does not fill a C–T quartet. Extracted from 66 fabricated Ga₂O₃ SBDs: μ_max 123
  (expert manual) / 187 (AE-PINN) / 225 (AE-NN); μ_min 80 / 60 / 75; log N_ref 17.3–17.5;
  α 0.9–2.8; θ 1.8–2.6.
- **"TCAD Simulation Models, Parameters, and Methodologies for β-Ga₂O₃ Power Devices",
  *ECS J. Solid State Sci. Technol.* (2023),
  DOI [10.1149/2162-8777/accfbe](https://doi.org/10.1149/2162-8777/accfbe)** — a review
  that likely compiles these. **Not read** (403 on both IOP and the SJSU ScholarWorks
  copy). This is the single highest-value unread document for this row.

### Assessment

- **Match to the CSV:** the gap declaration is **consistent** with what the literature
  shows — the two available parameterizations disagree substantially (μ_max 155 vs
  ~187–225) and use different functional forms, so there is genuinely no consensus set.
- **Confidence that the gap is genuine as *worded*: moderate-to-high.**
- **Confidence that "no published fit exists" would be safe to say: low** — it would be
  refuted by Jang et al. alone.
- **What would settle it:** read the ECS TCAD review. If it endorses a C–T quartet, the
  row moves from `gap` to a citable value; if it reports the spread, the gap is confirmed
  with a citation attached — which is strictly better than a gap asserted on internal
  authority.

Note also that μ_max = 155 cm²/Vs (Jang et al.) sits **below** the `150–200` band in row
3 above, and the PhuMob μ_max ≈ 187–225 straddles its top. Device-extraction mobilities
and best-material Hall mobilities are not the same quantity; flagged so the two rows are
not read as a contradiction.

---

## Summary for auditor 2

| Row | Status | Action implied |
|---|---|---|
| `displacement-threshold-Ed` | **Real literature exists; it is a five-site table with a 7–60+ eV directional range, not a scalar.** The corpus's 25 eV matches no modern per-site value and was never audited. Likely origin (Chaiken & Blue 2018) identified but unverified. | Decide table-vs-scalar; if scalar, state the convention. `UNSEEDED` remains defensible. |
| `mass-density` | **Resolved.** Åhman 1996, ρ = 5.961 → 5.96 exact. Citation existed internally since 2026-07-16 and never reached the cell. | Fill in the citation. |
| `mobility-electron-best-exp` | **Resolved to four named primaries**, three exact, one (CZ 152) moderate. Row mixes bulk / thin-film / 2DEG systems. | Cite all four; consider whether the 2DEG belongs. |
| `caughey-thomas-mu-n-set` | **Resolves internally**, and the literature supports "no *consensus* fit" — but published C–T sets do exist, so the wording must stay precise. | Lift the audit sentence out; read the ECS review before final wording. |

**Sources**

- [He et al., Acta Materialia 276, 120087 (2024)](https://doi.org/10.1016/j.actamat.2024.120087) · [open copy](https://www.mv.helsinki.fi/home/knordlun/pub/He24.pdf)
- [Tuttle et al., J. Appl. Phys. 133, 015703 (2023)](https://doi.org/10.1063/5.0124285)
- [Chaiken & Blue, IEEE Trans. Nucl. Sci. 65, 1147 (2018)](https://ieeexplore.ieee.org/document/8340879/)
- [Åhman, Svensson & Albertsson, Acta Cryst. C52, 1336 (1996)](https://doi.org/10.1107/S0108270195016404)
- [Zhang et al., Appl. Phys. Lett. 112, 173502 (2018)](https://arxiv.org/abs/1802.04426)
- [Zhang et al., APL Materials 7, 022506 (2019)](https://pubs.aip.org/aip/apm/article/7/2/022506/1064091/MOCVD-grown-epitaxial-Ga2O3-thin-film-with-an)
- [Peterson et al., Appl. Phys. Lett. 125, 182103 (2024)](https://pubs.aip.org/aip/apl/article/125/18/182103/3318415/)
- [Feng et al., Appl. Phys. Lett. 114, 250601 (2019)](https://par.nsf.gov/servlets/purl/10105817)
- [Galazka et al., J. Cryst. Growth 529, 125297 (2020)](https://doi.org/10.1016/j.jcrysgro.2019.125297)
- [Jang, Atmaca & Cha, Micromachines 13, 1185 (2022)](https://doi.org/10.3390/mi13081185)
- [Ong et al., arXiv:2504.02283](https://arxiv.org/pdf/2504.02283)
- [TCAD models review, ECS J. Solid State Sci. Technol. (2023)](https://doi.org/10.1149/2162-8777/accfbe)
