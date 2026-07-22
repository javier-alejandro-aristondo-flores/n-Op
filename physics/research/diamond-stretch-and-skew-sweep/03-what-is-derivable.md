# 03 — What is derivable: the exhaustive list

> **Copy — the dataset itself lives at `/Pool/Diamond_Stretch_And_Skew_Sweep/`.** This is a
> research-stratum companion describing an external DFT dataset (diamond lattice-distortion
> sweeps, VASP 6.2.0, PBE + HSE06(α=0.27)); it is **not** part of the lint-enforced atomic tree
> (`docs/architecture/`, `docs/implementation/`, `docs/mvp/`), which stays canonical. `/Pool` is
> the source of truth for both these documents and the data; if they ever disagree, `/Pool`
> wins. The data is **not** in this repository and must not be — every run directory holds a
> VASP-licensed POTCAR and this remote is public. Cite this suite from a spec via
> `research-sources:`.


Everything that can be milked from this dataset, useful to the program or not, tiered by how
much modeling sits between the raw numbers and the result. Tier rule of thumb:
**T0–T2 are data; T3 is data requiring careful fitting; T4–T5 are science built on the data
with stated assumptions; T6 is meta. Extrapolation discipline is at the end.**

Throughout: "per level" = separately at PBE and HSE06(α=0.27); recipes referenced as `02_…` §.
Quantities verified from this data are marked ✔.

**Read `02_…` §B6 before fitting anything.** 1,179 rows are 1,131 distinct shapes.

## T0 — Direct reads (no transformation)

1. Total energy E and free energy F per run, per ionic step (✔ used everywhere).
2. Stress tensor σ_ij per run per step — **including all HSE06 runs** (✔).
3. Forces per atom per step (nonzero only in shear families 3/4/5) (✔).
4. Relaxed geometries: the internal coordinate under every sampled shear (✔).
5. Eigenvalue field ε_nk: 8 bands × 172 k-points per run per level (✔).
6. Occupations, Fermi-level bookkeeping value, DOS + integrated DOS arrays.
7. Orbital/site-projected band weights: s, p_x, p_y, p_z character of every state.
8. Charge density ρ(r) on 3D grids (+ PAW augmentation occupancies) per run per level.
9. Relaxation trajectories (positions/E/F/σ per step; 1–3 steps typical).
10. Calculation metadata: parameter echoes, k-point lists + weights, SCF iteration counts,
    wall-times, job scripts, rerun history.
11. **The author's own census** (`electronic-summary-{pbe,hse06}.csv` per family): volume,
    lattice parameters, total energy, band gap, VBM, CBM, Fermi level, convergence flag and
    electron count for every point at both levels — **no XML parsing required** (✔). This is
    the fastest path to any scalar target and covers all 1,179 points.

## T1 — Single-run derived (one file + arithmetic)

12. Indirect band gap; direct gap at Γ (and at any mesh k) (✔ 5.4383 eV / 7.045 eV at
    HSE06(0.27), near-reference point).
13. VBM/CBM locations on the mesh; CBM valley position along the Δ-line (1/7-mesh
    resolution) and its drift under strain.
14. Band-edge degeneracy structure: VBM triplet (Γ₂₅′) splitting magnitudes under any
    non-hydrostatic strain — read directly from the top-3 valence eigenvalues at Γ.
15. Bandwidths (valence-band width from eigenvalue extrema), band centroids.
16. DOS-derived features: gap edges, band-edge DOS slopes, van Hove peak positions.
17. sp³-hybridization measures: s/p weight ratios of VBM/CBM states.
18. Hydrostatic pressure of a run: P = −Tr(σ)/3 (kB → GPa ÷10) (✔).
19. Deviatoric stress tensor; resolved shear stresses on any plane.
20. Charge-density scalars: ρ at bond midpoint, ρ minima/maxima, bond-charge asymmetry under
    strain; interstitial vs bond-region charge partition.
21. Internal displacement vector u (relaxed − input geometry, shear runs) (✔ 0.0087 Å at
    γ=0.1, purely ∥ z).
22. Number-of-SCF-steps and relaxation-step counts (hardness indicators).
23. **Deformation-gradient invariants per run** (✔): det F (exactly 1.000000 for all 540
    shear points — a null-check in its own right), tr(E_GL), ‖E_GL‖, the rotation content of
    F. Cheap, and they expose the two frame traps of `02_…` §B2.

## T2 — Grid-derived, linear-response regime (|ε|, |γ| ≲ 0.02 windows)

24. **Full cubic elastic tensor**: C11, C12, C44 — three independent constants = the complete
    linear elasticity of diamond, per level, by both energy-curvature and stress-slope routes
    (redundant cross-check). ✔ **C11 = 1071, C12 = 138, C44 = 570, C11−C12 = 933 GPa** (PBE,
    |e| ≤ 0.011, linear term included, RMS 0.129 meV). **The linear term is mandatory**; see
    `02_…` §C2 — omitting it costs 15% on C44.
25. **Clamped-ion C44⁰** (first-ionic-step energies) and the **Kleinman internal-strain
    parameter ζ** (✔ ζ = 0.0976) — the internal-relaxation decomposition of shear response.
    ✔ ζ is γ-independent to 0.2% over γ = 0.05→0.10, so the harmonic value is well defined.
26. **Zone-center optical phonon frequency ω_TO(Γ)**: from clamped-ion force vs relaxed
    displacement in shear runs, k = F/u_rel, ω = √(k/μ) with μ = m_C/2. ≈ 1307 cm⁻¹ (PBE lit.
    ≈ 1290–1300; experiment 1332). Extrapolate γ→0 over the 40-point sweep for the harmonic
    value; γ-dependence gives the mode's strain coupling (phonon deformation potential of the
    Raman mode).
27. Derived elastic scalars (from #24, closed forms in `02_…` §A1): bulk modulus B
    (cross-check vs EOS B₀ ✔ — they reconcile to ~1% via B₀′·ΔP, `02_…` §C2), shear moduli
    G_V/G_R/G_Hill, Young's modulus E, Poisson ν, Zener anisotropy A = 2C44/(C11−C12),
    Cauchy pressure C12−C44, directional Young's-modulus surface E(n̂), linear
    compressibilities.
28. Sound velocities v_L, v_T (any propagation direction via the Christoffel tensor from
    #24), v_m, and the **elastic Debye temperature θ_D** (~2200 K expected for diamond).
29. Pugh ratio G/B, Poisson-based ductility indicators, Chen–Niu Vickers-hardness estimate
    H_V = 2(k²G)^0.585 − 3 (model formulas, data-grade inputs).
30. **Gap deformation potentials**: hydrostatic a_gap = dE_gap/dlnV (family 1 gap(V) + P(V) →
    also dE_gap/dP, lit. ≈ +6 meV/GPa — a sharp cross-check); uniaxial gap response (family
    2); shear gap response (families 3/4/5). Bir–Pikus valence parameters b and d from
    VBM-splitting slopes — gap-referenced only (see NOT-derivable D4).
31. Effective-mass *estimates* by finite differences between neighboring mesh k-points
    (coarse: Δk = 1/7 of a reciprocal vector; usable for trends vs strain, not precision).
32. Density response to strain ∂ρ(r)/∂ε_ab: finite-difference fields between neighboring runs
    (function-space derivatives; natural neural-operator targets).
33. Piezo-optic-adjacent: strain dependence of the direct gap at Γ.
34. **Numerical-noise floor** of the whole pipeline — but only from the *real* redundancies
    (`02_…` §C7): family 3's xy/xz/yz spread, the family-4 symmetry null (#35), BM3 residuals,
    and two-route V₀ agreement (#36). **Not** family 4's plane-pair spread; **not** the 24
    duplicated shapes.
35. **The cubic-symmetry null** (family 4) ✔ — cubic symmetry forbids a γ₁γ₂ cross-term in
    the shear-shear energy; it fits to **−0.000 GPa** in all three plane pairs while C44 comes
    out identically 565.8 GPa in each. This is the dataset's **only** validation against a
    symmetry *requirement* rather than against literature or against itself, and it is
    impossible without 2-angle data.
36. **The Pulay stress bias, quantified** ✔ — energy-route V₀ minus stress-route V₀ gives
    **+0.109% (PBE) / +0.122% (HSE06)**, i.e. **≈ +5 kB** of bias on absolute stress at both
    levels. The agreement across two very different functionals is the evidence it is a
    basis-set effect of the shared ENCUT = 550 eV. Slopes and differences are unaffected.

## T3 — Anharmonic / finite-strain (the full sampled range, careful fitting)

37. **EOS**: Birch–Murnaghan (or Vinet/Rose) E(V), V₀, B₀, B₀′ per level (✔ table in
    `02_…` §C1); cold-curve pressure P(V) from −30 to +55 GPa; enthalpy H(P) = E + PV;
    Gibbs-at-0K.
38. **Third-order elastic constants.** The cubic set is C111, C112, C123, C144, C155, C456.
    Status, measured:
    - **C111, C112** — derivable from families 2/6, but fitting-protocol sensitive: they
      require the wide strain range (where truncation error bites) and diverge if the window
      is tightened (C111 ran −11k → −172k GPa as the window shrank from ±0.10 to ±0.011).
      Use a mid-window (±0.04–0.06) and quote the protocol.
    - **C123** — family-6 mixed-sign points. Weakly determined (±23%).
    - **C456** ✔ — **needs all three shears simultaneously nonzero, so family 5 alone
      supplies it.** Stable at ≈ **−1135 GPa** across every fit window tried (lit. ≈ −823).
      This is the family-5 payoff, and it now rests on 192 points instead of the 118 the
      truncated salvage had.
    - **C144, C155** — see #39. Do not trust the naive fit.
39. **The C144/C155 subtlety — read this before repeating an old claim.** Earlier
    documentation stated these are underivable "because every sampled point is either
    pure-normal or pure-shear." That reasoning is **wrong in finite-strain terms**: a simple
    shear at γ carries a Green–Lagrange *normal* component of γ²/2 (measured: up to 0.005 in
    family 3, 0.010 in family 4, 0.008 in family 5), so the shear families **do** sample
    mixed normal+shear. The full 10-parameter cubic fit over all 1,131 shapes is
    **rank-10 — formally complete, C144 and C155 included.**
    **But the conclusion survives anyway.** The leakage lies on a constrained path
    (e1 = γ²/2, tied to e6 = γ), nearly degenerate with pure quartic shear terms. The fitted
    values are worthless: C144 swings −2709 → −369 → +6982 → −10890 GPa as the window
    changes, against a literature ≈ −674, with ±22% formal error. **Verdict: not data-grade.
    A dedicated mixed normal+shear campaign is still the fix** (`04_…` §2.1). The correct
    statement is "weakly and unusably determined via finite-strain leakage", not
    "underivable".
40. **Fourth-order shear constants** — C4455-type cross terms (∂⁴E/∂ε₄²∂ε₅²). ≈ −360 GPa from
    a Green–Lagrange-basis fit over the shear sector. **Requires 2-angle data to separate
    from C456**, since family 5 always has all three shears on. Family 4 provides the
    C456-free slice. Also C4444-type (≈ −47 GPa) from the axes.
41. **Finite-strain path-dependence, as a first-class observable** — NEW, and only family 4
    can show it. The three plane pairs are symmetry-equivalent only as γ→0; at γ = 0.1 they
    differ measurably (internal relaxation 8.0 meV for `xy_xz` versus 10.0 / 10.1 meV for the
    two whose γ²/2 leakage splits across two normal components). That 2 meV splitting is a
    clean, isolated measurement of a genuine fourth-order effect. See `02_…` §B7 — and do not
    mistake it for noise.
42. Pressure derivatives of elastic constants dC_ij/dP (from strain-dependent local
    curvatures along family-1/6 volume changes — limited but extractable for C11, C12
    combinations).
43. **Ideal-strength lower bounds**: σ_xx(ε) along uniax to ±10% (still rising at range edge
    → lower bound on <100> ideal tensile strength); same for shear. With family 4 this extends
    to **biaxial-shear ideal strength** — the (γ₁,γ₂) energy landscape to |γ| = 0.1 on all
    three coordinate planes, which the old data could not map. True maxima lie beyond the
    sampled range — extrapolation class E3.
44. **Born-stability margins**: eigenvalues of the strain-dependent stiffness along all
    sampled rays; distance-to-instability maps (diamond stays stable everywhere in range —
    the margin itself is the datum).
45. Strain-dependence of ζ and of ω_TO(Γ) (mode Grüneisen parameter of the Raman mode). ✔ ζ
    is flat in γ; the volume-dependence needs the T5 route.
46. **Landau-type energy-surface expansions**: full 6-D polynomial/spline fit of E(E_GL) over
    the union of sampled manifolds — the master interpolator every other T3 item is a
    projection of. **The shear sector is now genuinely well-posed**: axes (family 3) ⊂
    coordinate planes (family 4) ⊂ interior (family 5), 492 distinct points. The normal sector
    has no equivalent 2-D layer, so the surface is better constrained in shear than in
    stretch — an asymmetry worth carrying into any surrogate's error model.
47. Anharmonic gap response: quadratic and higher terms of gap(strain); strain-dependent
    band-splitting nonlinearity.
48. **Scissor-validity test**: is gap_HSE − gap_PBE constant across the whole strain space?
    Tests whether a scissor correction on cheap PBE is transferable — directly relevant to
    the program's bare/dressed design. Now testable over 1,131 shapes including the whole
    shear sector.

## T4 — Model-mediated extrapolations (stated assumptions, still defensible)

49. **Debye–Grüneisen thermal model** from E(V) alone (Moruzzi–Janak–Schwarz): θ_D(V) ∝
    √(B(V)V^(1/3)) → Grüneisen γ_D = −dlnθ_D/dlnV → F(V,T) = E(V) + F_Debye(θ_D(V),T) →
    **thermal expansion α(T), c_v(T), B(T), thermal EOS, Mie–Grüneisen thermal pressure** —
    all approximate (Debye spectrum assumption; diamond's real phonon spectrum is not
    Debye-like, expect ~10–30% errors, trend-grade only).
50. Temperature-dependent elastic moduli via the quasi-static approximation.
51. Melting/instability *bounds* via Lindemann-type criteria on θ_D (order-of-magnitude).
52. EOS extrapolation outside the sampled window using the BM3/Vinet form (safe to ~2× the
    sampled compression, degrading gracefully; label ranges).
53. **Functional-transfer / Δ models**: train Δ = HSE06(0.27) − PBE on **1,131 paired
    shapes** (energies, stresses, gaps) → apply to new cheap PBE points of *similar*
    deformations; the residual statistics of the pairing are themselves a derivable (an
    uncertainty model for the dressing). De-duplicate first (`02_…` §B6).
54. Surrogate models of E(h), σ(h), gap(h) over the sampled manifolds (Gaussian process /
    neural operator); active-learning acquisition maps — where is the model most uncertain →
    where to run VASP next. **The un-sampled mixed stretch+skew sector will light up**, and
    it should: that is the real gap (#39, `04_…` §2.1).
55. Hardness/brittleness engineering estimates (from #27/#29 + model formulas);
    pressure-hardening trends of moduli.

## T5 — Derivable with additional compute (restart artifacts make it cheap)

The wavefunction, charge-density and relaxed-geometry files are *launchpads*: each enables a
VASP restart that was not run but is now one job away, at every one of 1,179 points.

**Prerequisite: rename back first.** VASP requires its canonical filenames
(`WAVECAR`, `CHGCAR`, `POSCAR`, …). `CHANGELOG.md` is the exact inverse map; applying it is a
scripted pass, not a research problem. Nothing below is lost by the plain-language renaming —
it is deferred by one command.

56. Dielectric function / optical absorption (LOPTICS from converged WAVECAR); refractive
    index vs strain (piezo-optics).
57. Full phonon dispersions and thermal properties via finite displacements (phonopy) at any
    sampled geometry → true QHA thermodynamics replacing tier-T4 approximations.
58. GW / BSE on top of stored wavefunctions (quasiparticle gaps, excitons vs strain).
59. Raman intensity of the 1332 cm⁻¹ mode vs strain (derivative of #56 wrt #26's mode).
60. Elastic constants by DFPT (validation of #24), Born charges (identically zero in diamond
    by symmetry — itself a null-check), piezoelectricity (zero — null-check).
61. Bader/QTAIM topological analysis of the stored charge densities (bond critical points,
    ellipticity vs shear) — needs only a charge-analysis tool, no VASP.
62. **The 12 absent family-4 points and the 24 absent family-5 combinations** (`04_…` §1) —
    each is one PBE + one HSE06 job from the stored inputs. ~72 calculations closes both
    holes; the geometries are trivially constructible from the existing POSCARs.

## T6 — Meta-derivables (about the calculations, not the crystal)

63. Cost model: PBE vs HSE06 wall-time ratio, scaling vs strain (SCF hardness), queue data —
    calibrates future campaign budgets.
64. Convergence-behavior map: SCF iterations vs deformation magnitude (where DFT gets hard);
    relaxation step counts (internal-relaxation onset).
65. Reproducibility forensics: rerun directories (double slurm logs) and their energy
    agreement.
66. **Determinism proof** ✔ — the 24 triplicated shapes (`02_…` §B6) are bit-identical across
    families that spell `PREC` differently (`Accuratei` vs `Accurate`). This simultaneously
    proves VASP's determinism on identical input *and* that the typo is inert. A rare case
    where redundant compute bought a real fact.
67. Reusable inputs: the k-set, the relaxed geometry library, the whole file tree as a
    regression fixture for any VASP-parser the program builds.
68. **A validation battery for the program itself**: every ✔ number in `02_…` Part C is a
    self-test an agent can re-derive to prove its parser + recipes are correct before touching
    anything downstream. The sharpest is the symmetry null (#35) — it tests physics, not
    bytes. (This is the "training an agent to use the data" payload.)

## NOT derivable from this dataset (do not pretend otherwise)

- **D1. Phonon dispersions / DOS / κ / heat capacity** beyond the Γ-TO mode of #26 and the
  T4 Debye surrogate — no supercell displacements, no DFPT output, no FORCE_SETS.
- **D2. Anything defect-, surface-, or interface-resolved** — single perfect bulk cell.
  (The stray 64-atom supercell in `converged_without_stress.zip` is *not* part of this
  dataset and uses incompatible settings — see `04_…` §4.)
- **D3. Transport** (mobility, conductivity), non-equilibrium, high-field, degradation.
- **D4. Absolute band-edge positions / absolute deformation potentials** — no core-level or
  electrostatic-potential reference was saved (LVTOT off); only *gap-referenced* quantities
  are meaningful across strain.
- **D5. C144, C155 at data grade** — formally rank-complete but numerically unusable; see #39.
  The honest statement is "weakly and unusably determined", not "underivable".
- **D6. k-point / ENCUT convergence errors** — single mesh, single cutoff; internal data
  cannot bound them (assign from external convergence studies). Note the Pulay bias of #36 is
  a *measurement* of one consequence, not a bound on the error itself.
- **D7. Finite-temperature anything** at data-grade (T4 gives model-grade only).
- **D8. Polarization / piezo / pyro / 2DEG channels** — identically zero in diamond by
  symmetry (vacuous, not missing; the null values ARE usable as symmetry checks).
- **D9. — RETIRED.** This entry previously read "Family-4 (2-angle shears) and the lost 40% of
  family 5 — truncation casualties." **Both are present.** Family 4 is 228 points; family 5 is
  complete at 192. Nothing in this dataset is a truncation casualty. See `read-me-first.md`.

## Extrapolation discipline (how far each claim may travel)

- **E1 Interpolation** inside the convex hull of sampled deformations, same level: safe;
  certify with leave-one-out residuals on the redundant points. Note the hull is now
  substantially larger in the shear sector (axes + planes + interior) than in the normal
  sector (axes + interior, no 2-D layer).
- **E2 Model-mediated** (BM-form beyond range, Debye–Grüneisen T > 0, Christoffel directions
  not sampled): allowed with the model named in provenance and an error class attached
  (trend-grade).
- **E3 Trend extrapolation beyond the hull** (ideal strength maxima, gap closure under extreme
  shear, stability loss): speculative — publishable only as bounds ("σ_ideal > X", "gap
  remains open for |γ| ≤ 0.1").
- **E4 Cross-material transfer** (diamond → other carbons/UWBG): not supported by this
  dataset alone; requires the program's own multi-material machinery.
- **E5 The mixed stretch+skew sector**: *no* extrapolation class applies. It is unsampled
  except along the degenerate γ²/2 leakage path (#39), and any surrogate will be least
  trustworthy exactly there while looking confident, because the leakage gives the fit
  formal rank. Treat model predictions in that sector as unvalidated, not as E1.
