# 02 — How to read the files and derive quantities

> **Copy — the dataset itself lives at `/Pool/Diamond_Stretch_And_Skew_Sweep/`.** This is a
> research-stratum companion describing an external DFT dataset (diamond lattice-distortion
> sweeps, VASP 6.2.0, PBE + HSE06(α=0.27)); it is **not** part of the book's canon pages
> (`journal/pages/`, checked by `journal/tools/apparatus.py`), which stay canonical. `/Pool` is
> the source of truth for both these documents and the data; if they ever disagree, `/Pool`
> wins. The data is **not** in this repository and must not be — every run directory holds a
> VASP-licensed POTCAR and this remote is public. Cite this suite from a spec via
> `research-sources:`.


This document answers: **for each quantity the program needs, how do we get it out of this
dataset** — which files to read, what deterministic transformation to apply, and what
correction/caveat applies. Part A maps the needs to recipes; Part B gives the reading
mechanics the recipes rest on; Part C contains worked examples whose numbers were actually
computed from this data (marked ✔ VERIFIED) so any agent can re-run them as self-tests.

The exhaustive "everything else that could be milked" list is `03-what-is-derivable.md`.

Filenames below are the plain names used in this tree; `CHANGELOG.md` maps them to the
VASP-canonical names you will see in VASP's own documentation.

## Part A — the needs-map

n-Op consumes external data through ground-truth-bridge records (`arch-16-pino-bridge`
§16.2): `(value, σ, provenance, coverage-mask)` targets attached to observables, gated by
applicability. This dataset is a *computed* provenance class (DFT), distinct from the
experimental constants in the cert reference battery. It is a sweep over `h`, the cell-vector
state component (`arch-04-state`) — at fixed composition, fixed everything else.

| Need (bundle / artifact) | Quantity | Recipe | Status |
|---|---|---|---|
| B8 thermodynamics; EOS observables | E(V) cold curve, V₀, B₀, B₀′, P(V) | §C1: Birch–Murnaghan fit over family 1, per functional | ✔ VERIFIED |
| B7 mechanics; `elastic-tensors.csv` cross-check | C11, C12, C44 | §C2: energy-curvature fit **with a linear term**, or stress slopes | ✔ VERIFIED |
| B7 mechanics | C44 (relaxed AND clamped), Kleinman ζ | §C3: family 3 final vs first-ionic-step energies; relaxed-vs-input geometry | ✔ VERIFIED |
| B7 derived | B, G, E, ν (Voigt/Reuss/Hill), sound velocities, elastic Debye temperature θ_D | closed-form combinations of C11, C12, C44, density (§A1) | derivable |
| B1 electronic | indirect & direct gap at each strain | §C4: eigenvalues+occupations from vasprun, or the author's census CSVs | ✔ VERIFIED |
| B1 electronic | gap deformation potentials | gap(g) over families 1/2/3 + finite differences | derivable |
| B10 static-validity | Born-stability boundary, spinodal | stress/energy Hessians along families 2/3/6 rays | derivable |
| Cert / consistency residuals | σ_ij vs (1/V)∂E/∂ε; force→0 at convergence; **the symmetry null of §C5** | §A2 | ✔ VERIFIED |
| PINO `h`-slot training targets | E(h), σ(h) on **1,131 distinct** h-points × 2 levels | bulk extraction §B5 — **de-duplicate first, see §B6** | derivable |
| Dressing / functional-transfer pairs | E_HSE06(0.27) − E_PBE, gap_HSE − gap_PBE at identical geometry | every point has both levels; subtract | derivable |
| Trajectory force data | (positions, E, F, σ) per ionic step | §B4: PBE vasprun per-step blocks | ✔ VERIFIED |

**A1 — closed-form elastic combinations** (cubic crystal): B = (C11+2C12)/3;
G_V = (C11−C12+3C44)/5; G_R = 5(C11−C12)C44 / (4C44+3(C11−C12)); G = (G_V+G_R)/2 (Hill);
E = 9BG/(3B+G); ν = (3B−2G)/(6B+2G); v_L = √((B+4G/3)/ρ), v_T = √(G/ρ),
v_m = [ (2/v_T³ + 1/v_L³)/3 ]^(−1/3); θ_D = (ħ/k_B)·v_m·(6π²n)^(1/3) with n = atoms/volume.
Density from the cell: ρ = 2·m_C/V (m_C = 12.011 u).

**A2 — consistency channels** (cert-style). This dataset has **five**, three of which are new:
1. **Thermodynamic**: numerical dE/dε along any family ray must equal −V·σ-component (mind
   units, §B3, and the sign convention `01_…` §5).
2. **Relaxation validity**: final forces < 1 meV/Å (EDIFFG).
3. **Symmetry, within family 3**: the xy/xz/yz sweeps are equivalent by cubic symmetry;
   their spread is a numerical-noise estimate. **Valid at all γ** — a single simple shear has
   the same finite-strain tensor shape under permutation.
4. **Symmetry, within family 4** — NEW: cubic symmetry forbids a γ₁·γ₂ cross-term in the
   shear-shear energy. Fitting it must return zero (§C5). This is the dataset's only test
   against a *symmetry requirement* rather than against literature or against itself.
5. **Two-route V₀ agreement** — NEW: the energy-route V₀ (EOS minimum) and the stress-route
   V₀ (where mean stress crosses zero) must agree. Their gap is the Pulay bias (§C6).

**Not a consistency channel, despite appearances:** family 4's three plane pairs are *not*
symmetry-equivalent at finite γ (§B7), and the 24 shapes it shares with family 3 are
bit-identical recomputations (§B6). Neither carries noise information.

**Import-record provenance block** — every derived value entering n-Op must carry:
`{functional: PBE | HSE06(alpha=0.27, hfscreen=0.2), encut: 550 eV, kmesh: Γ-7×7×7
(172 irreducible, ISYM=0), potcar: PAW_PBE C 08Apr2002, code: VASP 6.2.0,
reference-state: a0=3.567 Å (experimental; NOT the functional equilibrium — see §B3),
relaxation: PBE ions relaxed / HSE static at PBE geometry}`.
The last two fields are the ones people forget and the ones that bite.

## Part B — reading mechanics

**B1 — where every primitive lives.** Preferred source: `everything-machine-readable.xml`
(VASP's `vasprun.xml`; complete, well-formed in every run).

| Primitive | vasprun.xml location | Cheap alternative |
|---|---|---|
| Final total energy E0 | last `<calculation>` → `<energy>` → `<i name="e_0_energy">` | last `E0=` of `energy-per-iteration-summary.txt` |
| Clamped-ion energy | first `<calculation>` | **first** `E0=` of the same file |
| Per-step energies | each `<calculation>` block | `N F= … E0= …` lines |
| Forces (per step) | `<varray name="forces">` | — |
| Stress (per step, kB) | `<varray name="stress">` (present in HSE06 runs too) | OUTCAR `in kB` line |
| Lattice + positions | `<structure>` blocks (`initialpos` … `finalpos`) | input / final geometry files |
| Eigenvalues + occupations | `<eigenvalues><array>` → `<r>E occ</r>` | `band-energies-per-kpoint.txt` |
| k-points + weights | `<varray name="kpointlist">`, `<varray name="weights">` | `irreducible-kpoint-list-with-weights.txt` |
| Orbital projections | `<projected>` | `orbital-character-per-band-per-kpoint.txt` |
| DOS / Fermi | `<dos>` → `<i name="efermi">` | `density-of-states-curve.txt` |
| Parameter echo (trust this) | `<parameters>` and `<incar>` | `calculation-settings.txt` (what was *asked*) |
| Charge density | not in vasprun | `charge-density-grid-full.txt` |
| Energy, gap, VBM/CBM, volume — **all points at once** | — | the per-family `electronic-summary-*.csv` (the author's own census) |

That last row is worth knowing: for scalar targets you often need no XML parsing at all.
The census CSVs cover every point at both levels and were produced by the original author's
own extractor.

**B2 — recovering the deformation from the files** (never trust names alone):
read the 3×3 lattice A from the input geometry file (apply the scale rule: positive s →
A×s; negative s → uniform rescale so |det| = |s|). With A_ref = the unstrained matrix of
`01_…` §1 in the same row convention, the deformation gradient is **F = A_ref⁻¹ · A_def**
(row-vector convention: new-row = old-row · F). Then engineering strains from F − I; the
rotation-free finite strain is the **Green–Lagrange tensor E_GL = (FᵀF − I)/2**.

Verified on all 1,179 points. Two traps:

- **Family 1's F carries a rotation that is not physics** (antisymmetric part up to 0.087)
  because its POSCARs use an a₁-along-x lattice frame. `FᵀF` is isotropic to 1×10⁻¹¹.
  Compare `E_GL` or `FᵀF` across families, never `F`.
- Families 3/4/5 are simple shears; F carries a genuine rotation. At |γ| = 0.1, E_GL picks
  up second-order normal components (γ²/2 = 0.005), so **fits beyond |γ| ≈ 0.02 must use
  E_GL** (or fit E vs γ directly along the sampled ray).

**B3 — the reference-state offset (the one mandatory correction).**
All deformations are relative to the *experimental* a₀ = 3.567 Å. The functionals' own
equilibria differ (✔ VERIFIED, §C1): PBE V₀ = 11.4133 Å³ (a₀ = 3.5740 Å) — the reference is
0.6% *below* PBE equilibrium; HSE06(0.27) V₀ = 11.1517 Å³ (a₀ = 3.5465 Å) — the reference is
1.7% *above* HSE equilibrium. So every run carries a hydrostatic stress offset. **Measured at
the reference volume itself (`cell-volume-11.35-cubic-angstroms`): +19.7 kB at PBE
(compressive), −86.3 kB at HSE06 (tensile, i.e. 8.6 GPa).**

Recipes must use one of:
(a) **stress differences** between strained points (offsets cancel in slopes),
(b) energy fits carrying an explicit **linear term** — see §C2, this is the cheapest fix and
    the one people skip,
(c) explicit re-referencing of strains to the functional's own V₀.

**The cost of skipping it is not academic**: §C2 measures a **15% error in C44** and a 60×
inflation of fit residual from omitting the linear term alone.

**B4 — trajectory reading.** Each PBE run's vasprun contains one `<calculation>` per ionic
step. Step 1 = **clamped-ion** result at the imposed strain (atoms at ideal positions); last
step = relaxed. Both are physics: clamped vs relaxed distinguishes bare elastic response
from internal-relaxation screening (§C3). Normal-strain families (1/2/6) keep atoms
symmetry-pinned — expect 1–2 steps and zero forces; force-bearing trajectories exist **only
in shear families 3/4/5**.

**B5 — bulk extraction pattern.** The parse-worthy content is ~1.3 MB/run (vasprun.xml +
OSZICAR + CONTCAR); the wavefunction and charge-density files are ~75% of the bytes and are
not needed for scalar targets. Recommended: stream each family tarball once,
`tar xzf <family>.tar.gz --wildcards '*/everything-machine-readable.xml' '*/energy-per-iteration-summary.txt' '*/final-relaxed-crystal-geometry.txt'`,
parse into one table keyed by `index-of-all-runs.tsv`, and content-address the raw files you
keep. For scalars only, the census CSVs (§B1) are faster still.

**B6 — DE-DUPLICATE FIRST.** The manifest has **1,179 rows but only 1,131 distinct shapes**.
24 single-skew shapes are each computed three times: once in `3-skew-one-plane`, and twice in
`4-skew-two-planes` (each shear plane belongs to two of the three plane-pairs, so its
zero-rows repeat it). All copies are **bit-identical** — same geometry, deterministic code,
same energy to the last digit.

Consequences:
- They are **not** independent samples and carry **zero** noise information.
- Any least-squares fit or training set built naively from the manifest gives those 24
  shapes **3× weight**.
- Filter on `duplicate_group` (non-empty = redundant) and keep one member per group.

They are still useful for one thing: because those copies span families with *different*
`PREC` spellings, they prove the `Accuratei` typo is inert (`01_…` §2).

**B7 — family 4's plane pairs are not interchangeable at finite γ.** It is tempting to treat
`xy_xz`, `xy_yz`, `xz_yz` as symmetry-equivalent (as family 3's xy/xz/yz genuinely are) and
use their spread as a noise estimate. **Do not.** They coincide only as γ→0. At γ = 0.1 their
Green–Lagrange tensors differ materially:

| pair | γ²/2 normal leakage | extra off-diagonal |
|---|---|---|
| `xy_xz` | all 0.010 into E_xx | — |
| `xy_yz` | split 0.005 / 0.005 into E_xx, E_yy | — |
| `xz_yz` | split 0.005 / 0.005 | E_xy = 0.005 |

The energies follow the algebra: internal relaxation at (0.1, 0.1) is 8.0 meV for `xy_xz`
versus 10.0 and 10.1 meV for the two that split their leakage. **That spread is physics —
finite-strain path-dependence — not noise.** Using it as σ_unc would corrupt every error bar
derived from family 4.

## Part C — worked, verified examples (re-runnable self-tests)

Every number below was recomputed from this tree during its authoring.

**C1 — EOS (family 1).** ✔ VERIFIED. Read final `E0` from both sub-runs of all 47
`cell-volume-*` dirs; fit 3rd-order Birch–Murnaghan per functional:

| Level | V₀ (Å³) | a₀ (Å) | B₀ (GPa) | B₀′ | max fit residual |
|---|---|---|---|---|---|
| PBE | 11.4133 | 3.5740 | 434.2 | 3.66 | 0.15 meV |
| HSE06(α=0.27) | 11.1517 | 3.5465 | 473.8 | 3.59 | 0.17 meV |

Literature checks: PBE diamond a₀ ≈ 3.572–3.574 Å, B₀ ≈ 432–435 GPa (match); experiment
a₀ = 3.567 Å, B₀ = 443 GPa. Sub-meV residuals over a ±10% volume range certify E(V) as
smooth and fit-grade. Pressure curve P(V) = −dE/dV from the BM3 form; the sampled range
spans ≈ −30 to ≈ +55 GPa.

**C2 — C11, C12, C44, and why the linear term is mandatory.** ✔ VERIFIED.
Fit U = E/V in Green–Lagrange Voigt coordinates over all unique points inside a small-strain
window. The cubic basis is
U = σ₀(e1+e2+e3) + ½C11(e1²+e2²+e3²) + C12(e1e2+e2e3+e3e1) + ½C44(e4²+e5²+e6²).
The **first term is not optional** — the reference is not the functional's equilibrium
(§B3), so a linear term genuinely exists. Measured effect (PBE):

| window | linear term | C11 | C12 | C44 | B | RMS |
|---|---|---|---|---|---|---|
| \|e\|≤0.021 | omitted | 1073.1 | 141.4 | 570.3 | 451.9 | 7.450 meV |
| \|e\|≤0.021 | **included** | 1077.4 | 140.4 | 574.7 | 452.7 | **1.045 meV** |
| \|e\|≤0.011 | omitted | 1057.0 | 133.9 | 554.9 | 441.6 | 2.817 meV |
| \|e\|≤0.011 | **included** | **1071.2** | **138.3** | **570.5** | 449.3 | **0.129 meV** |
| \|e\|≤0.006 | omitted | 1017.3 | 124.2 | **492.7** | 421.9 | 1.641 meV |
| \|e\|≤0.006 | **included** | 1078.5 | 139.9 | 590.7 | 452.8 | **0.027 meV** |

Omitting it costs **15% on C44** at the tightest window and inflates the residual 60×.
Recommended values (|e| ≤ 0.011, linear term included): **C11 = 1071, C12 = 138,
C44 = 570, C11−C12 = 933 GPa**. Experiment: 1079 / 124 / 578 / 955.

*Stress route cross-check*: at uniax ε = +0.005 (HSE06), σ_xx − σ_yy = **−49.04 kB** →
(C11−C12) ≈ 981 GPa raw, landing near 955 after the finite-strain correction.

*Independent cross-check between routes*: the elastic-route B = (C11+2C12)/3 = 449 GPa is
evaluated at the *experimental* reference, while the EOS-route B₀ = 434.2 GPa is at PBE's own
V₀. The reference sits 0.6% below PBE equilibrium ⇒ ΔP ≈ 2.6 GPa ⇒ ΔB ≈ B₀′·ΔP ≈ 9.5 GPa,
predicting ≈ 443.7. Two entirely independent routes — energy curvature and an EOS fit —
reconcile to ~1%. This is the strongest single validation in the dataset.

**C3 — C44, clamped C44⁰, Kleinman ζ (family 3).** ✔ VERIFIED.
Relaxed U(γ) = ½C44γ² from *final* energies; clamped U⁰(γ) = ½C44⁰γ² from *first-ionic-step*
energies (first `E0=` per run). Internal displacement: relaxed minus input geometry for atom
2 relative to atom 1, converted to Cartesian.

At γ_xy = 0.10 (PBE): sublattice shift is **purely ∥ z** (the symmetry-allowed channel for
xy shear), |u| = **0.0087 Å** → **ζ = 0.0976** (literature DFT ζ ≈ 0.10–0.13).
Relation: ζ = |u| / (a/4 · γ).

**ζ is essentially γ-independent**: 0.0974 at γ = 0.05 versus 0.0976 at γ = 0.10 — flat to
0.2% over a factor of two in γ. The internal-strain response is harmonic across the whole
sampled range.

**C4 — band gap (any run).** ✔ VERIFIED. From vasprun `<eigenvalues>`: VBM = max E over
states with occ > 0.5; CBM = min E over occ < 0.5; gap = CBM − VBM (indirect if arg-k
differs; also report the direct gap at fixed k). At uniax ε = +0.005, HSE06(0.27): indirect
gap = **5.4383 eV** (VBM at Γ, CBM at a Δ-line mesh point), direct Γ-gap = 7.045 eV;
experiment 5.47 / 7.3 eV. The census CSVs agree to their printed precision.

Caveats: (i) the CBM is mesh-sampled — the true Δ-minimum falls between mesh points, biasing
the gap high by up to ~0.05–0.1 eV; treat gap *changes* across strain as far more accurate
than absolute values; (ii) NBANDS = 8 → only 4 conduction bands; (iii) under shear, band
degeneracies split — track band *connectivity*, not just extrema.

**C5 — the cubic-symmetry null (family 4).** ✔ VERIFIED. **New; only 2-angle data can run
it.** Cubic symmetry forbids a γ₁·γ₂ cross-term in the shear-shear energy. Fit
U = c₀ + ½C44(γ₁²+γ₂²) + C_x·γ₁γ₂ + (quartics) to each plane pair. Result: C_x =
**−0.000 GPa** in all three pairs, while C44 comes out identically 565.8 GPa in all three.

This is the dataset's only check against a *symmetry requirement* rather than against
literature or against itself, and it is the single most informative test that a parser (or a
rename, or a rebuild) has not corrupted anything — it tests the physics, not the bytes.

**C6 — the Pulay bias, quantified (family 1).** ✔ VERIFIED. **New.** Two independent routes
to V₀ must agree if the basis is converged: the energy route (BM3 minimum) and the stress
route (where mean stress crosses zero). They do not, and the gap is the Pulay bias:

| Level | V₀ energy route | V₀ stress route | disagreement | equivalent pressure bias |
|---|---|---|---|---|
| PBE | 11.4133 Å³ | 11.4009 Å³ | +0.109% | +0.47 GPa (+4.7 kB) |
| HSE06(0.27) | 11.1517 Å³ | 11.1381 Å³ | +0.122% | +0.58 GPa (+5.8 kB) |

Both levels agree on the magnitude despite being very different functionals — that shared
value is the evidence it is a basis-set effect from the common ENCUT = 550 eV, not something
level-specific. **Practical rule: absolute stresses from this dataset carry ≈ +5 kB of Pulay
bias.** Slopes and differences are unaffected.

**C7 — assigning σ_unc to derived values.** Use the built-in redundancies, and only the real
ones:

- **family 3's xy/xz/yz spread** — genuinely symmetry-equivalent at all γ. Use this.
- **family-4 symmetry null (§C5)** — the deviation of C_x from zero is a direct noise floor.
- **BM3 fit residuals** (§C1) — for EOS quantities.
- **two-route V₀ agreement (§C6)** — for anything stress-derived.
- **NOT family 4's plane-pair spread** (§B7) — that is finite-strain physics.
- **NOT the 24 duplicated shapes** (§B6) — bit-identical, zero information.

The *physical* error (functional bias) is estimated by the PBE↔HSE06 spread and by anchoring
to experiment — record both separately in the import record.
