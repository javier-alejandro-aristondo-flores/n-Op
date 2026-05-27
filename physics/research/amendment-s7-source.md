I'll start by reading the existing IMPLEMENTATION-PLAN.md to understand its style and structure, then produce the amendment.
Now I have a clear picture of the existing plan's structure and discipline. I'll produce the amendment proposal.

---

# AMENDMENT PROPOSAL TO `IMPLEMENTATION-PLAN.md`

**Authoring stream:** S7 (synthesis)
**Inputs consumed:** S1 (UWBG observable catalog), S2 (CSP + heterostructure), S3 (defects/doping/surfaces/interfaces/high-T), S4 (non-equilibrium/high-field/hot-carrier), S5 (PINO residual loss methodology), S6 (deduplicated cheap-residual catalog).
**Scope anchor:** diamond-centric UWBG semiconductor stack (diamond + UWBG companions + refractory contacts + substrates + dielectrics) targeted at harsh-environment chips (jet-turbine-class operation, T_op up to ~900 K, fields up to multi-MV/cm, gradient ~ 10⁷ K/m).
**Insertion discipline:** the sections below are written to be pasted as **new top-level sections §19–§35** of `IMPLEMENTATION-PLAN.md`, OR — for §§2-13 of this amendment — applied as in-place edits to the existing numbered sections of the plan. Both forms are provided. No existing locked-in commitment is rescinded.

---

## Section 1 — Amendment summary (one-page overview)

This amendment retargets `/physics` for the user's PINO-training programme on UWBG-semiconductor harsh-environment chips, without disturbing the GENERIC core. The retargeting is **additive**: state vector unchanged, GENERIC bracket form unchanged, four-level BO hierarchy unchanged, no-symbolics-on-runtime-path unchanged, single-typed-seal discipline unchanged.

**What changes**

1. The **named-formula registry** grows from ~22 to **87 entries** (S6 deduplicated catalog).
2. The **observable-bundle list** grows from 8 → **11** (adds `defect-resolved`, `surface-resolved`, `interface-resolved`, `field-resolved`, `hot-carrier-resolved`, `degradation`, plus reconciliations).
3. The **abstract-template registry** grows from 12 → **18** (adds `InterfaceEquilibriumOf`, `SelfConsistentChargeBalanceOf`, `HarmonicStiffnessHessianOf`, `BiSlabGrandPotentialOf`, `MassActionEquilibriumOf`, `ClusterExpansionOf`).
4. The **residual-category list** grows from 5 → **7** (adds `structural-validity`, `thermodynamic-consistency`).
5. The **cert-obligation list** grows from 6 → **10** (adds `bulk-edge-correspondence`, `reference-battery-cert` formalized as separate obligation distinct from obligation-4 frozen fixtures, `surrogate-net-validity`, `adjoint-existence-at-registration`).
6. `Environment` gains **one optional field**: `temperature_gradient`.
7. `Response` interface gains **one optional parameter**: `causal?:Boolean`.
8. Two new **sub-methods** are registered: `field-line-integral` (under `path-search`) and `interface-tunneling` (under `linear-response`).
9. A new top-level architectural piece is added: the **`residual-generator` factory** (`generic/residual-generator.rkt` and registry under `residuals/registered/`). This is the load-bearing PINO-facing surface.
10. A new top-level architectural piece is added: the **`pino-bridge/` exports** — three typed surfaces (`Generate`, `Validate`, `Import`) consumed by `/informed-operator`.
11. The reference-cache substrate is unified under `shared/reference-cache.rkt` with namespaced sub-caches (`phases/`, `defects/`, `interfaces/`, `band-references/`).
12. A new **two-tier accuracy discipline** is encoded in every formula and residual record: `cost-tier ∈ {T0, T1, T2, T3}` and `diff-tag ∈ {D0, D1, D2, D3, D4}`. These tags drive sampling, scheduling, and the autodiff boundary.

**What stays the same**

- Unified state `x(t) = (h, R_I, P_I, Π_h, Z_I, γ̂, A)`. **No new DOFs.**
- GENERIC bracket form `dx/dt = L·δE/δx + M·δS/δx`.
- Four-level BO hierarchy (Level 1 ← Level 2 ← Level 3 ← Level 4).
- 12 method primitives.
- Three top-level inputs (`PeriodicityStructure`, `SiteDecoration`, `Environment`).
- Four cross-cutting interfaces (`Scalar`, `FieldOnGrid`, `Tensor`, `Response`).
- Cert as first-class sub-tree; loud failure with numeric witnesses; substrate-agnostic stance; long descriptive names; gate-style tests.

**What enters scope**

- Diamond + UWBG companion materials (β-Ga₂O₃, AlN, c-BN, AlGaN at high Al).
- Refractory contacts (W, Mo, TiN, TaN, NbN, Ir, Pt).
- High-T substrate / dielectric / passivation stacks.
- Defect populations, surface terminations, metal-semiconductor interfaces — **as `SiteDecoration` special cases**, not new top-level types.
- High-field, hot-carrier, self-heating, electromigration, degradation kinetics — **as Level-4 emergent distributions over the existing state**, not new state.

**What leaves scope (explicit; see Section 14)**

Strongly-correlated materials; flexoelectricity in centrosymmetric crystals; magneto-thermal coupling in heavy contacts; deep-defect non-Markovian dynamics beyond Marcus; polaron localization beyond Fröhlich; 4-phonon scattering; full NEGF tunneling; full SCPH/SSCHA; plasma-process surface damage; grain-boundary statistics; continuum creep; quantum-tunneling-corrected rates.

---

## Section 2 — State vector amendment (apply to existing §3.1)

**Edit instruction:** keep §3.1 verbatim. Append the following confirmation paragraph immediately after the `x(t)` listing.

> **UWBG-scope completeness confirmation (S7, derived from S4).** The 7-tuple `(h, R_I, P_I, Π_h, Z_I, γ̂, A)` is structurally sufficient for the full UWBG-chip / harsh-environment scope. All quantities required to describe operation under high field, hot-carrier injection, self-heating, defect drift, and metal-semiconductor interface physics are **emergent from the irreducible state**:
>
> | Quantity | Symbol | Derivation from irreducible state |
> |---|---|---|
> | Electron temperature | `T_e(r, t)` | Second moment of the carrier distribution `f_n(k,r,t)` obtained as the semiclassical limit of `γ̂` |
> | Current density | `j(r, t)` | First velocity moment of `f_n` (or `Tr[ĵ γ̂]` in the full quantum form) |
> | Internal E-field | `E_field(r, t)` | `−∂_t A − ∇φ` where `φ` is recovered from `γ̂` via Hartree (Poisson on `Tr[γ̂](r)`) and `A` is part of state |
> | Lattice temperature | `T_L(r, t)` | Local equipartition over `{P_I}` within a spatial window, or fitted Bose–Einstein over an emergent `n_{qs}(r,t)` |
> | Local dielectric | `ε(r, ω)` | Linear response of `γ̂` to a probe perturbation; reduces to a function of state at fixed `(R_I, h)` |
> | Defect populations | `N_D, N_A, N_t(E,r,t)` | Coarse-graining of `SiteDecoration` over spatial bins with `tag ∈ {'defect, 'impurity}`; their dynamics are master-equation evolutions on `R_I` configurations |
> | Surface coverages | `θ_i(t)` | Spatial restriction of `SiteDecoration` with `tag = 'adsorbate` |
> | Interface dipole | `Δφ_int` | Real-space integral of the planar-averaged Hartree potential built from `γ̂` |
> | Schottky barrier | `φ_B` | `Δ(ε_F, band edge)` evaluated on the relaxed bicrystal — a state readout |
>
> **No new DOFs are required.** Adding any of the above to the state vector would create a constraint manifold (the consistency conditions tying it back to `γ̂`/`R_I`/`A`) and reintroduce the precise integration pathology the GENERIC formulation is designed to avoid.

---

## Section 3 — Environment amendment (apply to existing §5.3)

**Edit instruction:** §5.3 currently lists six fields. Append one:

```
- temperature_gradient   ∇T(r, t)   optional, FieldOnGrid[ℝ³]
                                     (default: zero;
                                      required for thermo-electric, Seebeck,
                                      thermal-EMG, self-heating closure when
                                      external substrate clamp is anisotropic)
```

Confirm the other six fields are unchanged and cover all remaining harsh-environment inputs:

| Field | Covers |
|---|---|
| `temperature` | bath / substrate temperature; T_amb up to 900 K for jet-turbine scope |
| `pressure` | hydrostatic baseline; default 1 atm |
| `chemical_potentials` | open-system dopant baths; oxygen partial pressure for surface chemistry |
| `applied_electric_field` | DC/AC bias; field strengths up to ~10 MV/cm |
| `applied_magnetic_field` | retained as optional; default zero (out of scope for current target) |
| `applied_stress` | thermomechanical stress from CTE mismatch; mechanical clamps |

---

## Section 4 — Interfaces amendment (apply to existing §11)

**Edit instruction:** §11 currently lists four interfaces. Replace the `response` line with:

```
└── response       evaluate, Hilbert-transform, integrate, causality-check,
                   causal?: Boolean   (default: #true; set #false to disable
                                       KK enforcement on responses known to
                                       be acausal — e.g., truncated cumulant
                                       expansions used as warmup approximants)
```

`Scalar`, `FieldOnGrid`, `Tensor` interfaces are unchanged. The `causal?` flag is consumed by `residuals/algebraic-identities/kramers-kronig.rkt`: when `causal? = #false`, the KK residual is registered with weight zero and emits a cert tripwire if a downstream consumer queries it as if causal.

---

## Section 5 — Method-vocabulary amendment (apply to existing §7)

**Method count: 12 (unchanged).** No new method primitives.

**Two new sub-methods registered** under existing primitives:

```
linear-response/
  …existing: Kubo, Linear-Response-DFT, Greens-function, Sternheimer…
  ├── interface-tunneling             InterfaceTunneling(barrier-profile: FieldOnGrid[ℝ],
                                                          E_F_left, E_F_right: Scalar,
                                                          model: TunnelModel) → Response
                                       (covers Padovani-Stratton thermionic-field-emission
                                        and Fowler-Nordheim regimes; explicit out-of-scope
                                        for full NEGF — see §14)

path-search/
  …existing: NEB, climbing-image-NEB, dimer, string-method…
  ├── field-line-integral             FieldLineIntegral(field: FieldOnGrid[ℝ³],
                                                          start: Point, end: Point,
                                                          integrator: LineIntegrator) → Scalar
                                       (covers ∫E·dl drift-trajectory potentials, work
                                        integrals along carrier paths, electromigration
                                        force integrals)
```

**Registration discipline.** Sub-methods are added by extending the dispatch table inside `methods/linear-response.rkt` and `methods/path-search.rkt`. Adding a sub-method does not change the method's typed signature, does not require a new file at the methods/ level, and must be accompanied by:
1. a sub-method test in `tests/method-tests/`,
2. a one-line entry in the method's header docstring,
3. a regression-freeze entry pinning sample outputs.

---

## Section 6 — Template-vocabulary amendment (apply to existing §8)

**Template count: 12 → 18.** Six new templates, each with explicit typed signature.

```
abstract-properties/
  …existing 12 templates unchanged…
  │
  ├── interface-equilibrium-of          InterfaceEquilibriumOf(
  │                                       left: Crystal,
  │                                       right: Crystal,
  │                                       coupling: InterfaceCoupling,
  │                                       env: Environment,
  │                                       method: BiSlabSolver) → BicrystalState
  │                                     [S3 origin; consumed by Schottky-barrier,
  │                                      band-offset, interface-dipole observables]
  │
  ├── self-consistent-charge-balance-of SelfConsistentChargeBalanceOf(
  │                                       host: Crystal,
  │                                       defect-set: Set[DefectSpecies],
  │                                       env: Environment,
  │                                       method: ChargeNeutralitySolver,
  │                                       tol: real) → (E_F: Scalar,
  │                                                     {N_q^(d)}: Vector,
  │                                                     {n,p}: Scalar²)
  │                                     [S3 origin; closes the Layer-3 ↔ Layer-5
  │                                      dependency cycle via same-pass fixed point]
  │
  ├── harmonic-stiffness-hessian-of     HarmonicStiffnessHessianOf(
  │                                       F: Functional,
  │                                       x₀: StatePoint,
  │                                       displacement-basis: Basis,
  │                                       method: HessianMethod) → Tensor[ℝ^{3N×3N}]
  │                                     [S2 origin; specialization of
  │                                      second-derivative-of to phonon dynamical
  │                                      matrices and dynamical-stiffness questions —
  │                                      kept separate from generic SecondDerivativeOf
  │                                      because the symmetrization, acoustic-sum-rule
  │                                      enforcement, and Born-effective-charge correction
  │                                      are template-level concerns]
  │
  ├── bi-slab-grand-potential-of        BiSlabGrandPotentialOf(
  │                                       slab-left: Crystal,
  │                                       slab-right: Crystal,
  │                                       gap: Length,
  │                                       env: Environment) → Scalar
  │                                     [S2 origin; underlies adhesion energy,
  │                                      interface formation energy, debonding force]
  │
  ├── mass-action-equilibrium-of        MassActionEquilibriumOf(
  │                                       species: Set[Species],
  │                                       reactions: Set[Reaction],
  │                                       env: Environment,
  │                                       method: NonlinearSolver) → CompositionVector
  │                                     [S2 origin; covers point-defect equilibria,
  │                                      gas-phase exchange equilibria, surface-
  │                                      adatom equilibria. Distinct from
  │                                      MicrokineticSteadyStateOf in that mass-action
  │                                      is an equilibrium readout, microkinetic is a
  │                                      driven steady state]
  │
  └── cluster-expansion-of              ClusterExpansionOf(
                                          host: Crystal,
                                          basis-clusters: Set[Cluster],
                                          training-energies: Map[Configuration, Scalar],
                                          method: CERegression) → ClusterFunctional
                                        [S2 origin; consumed by alloy phase diagram,
                                         segregation energetics, configurational
                                         entropy at finite T]
```

**S2/S3 overlap resolution.** Both S2 and S3 proposed `InterfaceEquilibriumOf`. S3's version subsumes S2's (S3 explicitly handles charge transfer + band alignment; S2 handles only mechanical coherency). Adopt S3's signature. S2's coherency check is reduced to a residual entry under `structural-validity` (see Section 9).

---

## Section 7 — Formula-registry amendment (apply to existing §9)

**Formula count: ~22 → 87.** The full 87-entry registry is the canonical S6 deduplicated catalog (consumed verbatim by this amendment as the master list). The registry table below lists every entry with: `name`, `signature`, `source-stream`, `cost-tier`, `diff-tag`, `layer`. Bundle membership and dependency edges are tracked in `formulas/registry-manifest.scm` (introduced in Phase 7+).

**Tag legend.**

- `cost-tier`: `T0` (closed-form, ≤ 10 µs), `T1` (small linear algebra / 1D quadrature, ≤ 10 ms), `T2` (Brillouin-zone / mesh integral, ≤ 10 s), `T3` (self-consistent loop or PDE solve, ≤ 10 min).
- `diff-tag`: `D0` (no autodiff required — pure observable read), `D1` (analytic forward derivative known), `D2` (registered with adjoint validation gate — backward mode required for PINO loss), `D3` (implicit-function adjoint via fixed-point linearization), `D4` (autodiff explicitly relaxed — surrogate-net bridge or finite-difference fallback approved at registration time).
- `layer`: 1-7 per S6's seven-layer DAG.

**Existing 24 entries retained verbatim** (slab-arithmetic, arrhenius, einstein-mobility-diffusivity, kramers-kronig-hilbert, chen-hardness, teter-hardness, tian-hardness, mazhnik-oganov-hardness, voigt-reuss-hill-averages, christoffel-eigenvalue, vineyard-prefactor, jump-diffusivity, bose-einstein-cv, bose-einstein-helmholtz, fermi-dirac-helmholtz, fermi-dirac-occupation, formation-energy-from-references, defect-formation-energy, lorenz-wiedemann-franz, linear-elasticity-stress-strain, van-roosbroeck-shockley, htst-rate, turnover-frequency, current-density-from-distribution). All retag to `(cost-tier, diff-tag, layer)` per S6's catalog.

**63 additional entries from S1-S6.** Grouped by source-stream contribution:

*From S1 (UWBG observable hubs) — 8 entries:*
```
band-edge-effective-mass            (E(k), k₀) → m*                          T1 D1 L2
deformation-potential-acoustic      (∂E_c/∂ε, C_ij) → Ξ                      T1 D2 L2
deformation-potential-optical       (∂E_c/∂u_qν) → D_o                       T2 D2 L2
luttinger-kohn-parameters           (E_v(k near Γ)) → (γ₁, γ₂, γ₃)           T2 D1 L2
dielectric-permittivity-static      (ε(ω→0)) → ε_s                           T2 D2 L3
phonon-frequency-LO-TO              (ε_∞, ε_s, ω_TO) → ω_LO                  T0 D1 L3
band-offset-AB                      (φ_A, φ_B, IP_A, IP_B) → ΔE_v            T1 D2 L4
work-function-from-slab             (V_vac, E_F) → φ                         T1 D2 L4
```

*From S2 (CSP + heterostructure) — 15 entries:*
```
coherent-strain-energy              (a_film, a_sub, C_ij) → E_strain         T0 D1 L1
critical-thickness-matthews-blakeslee (b, ν, β, a_sub) → h_c                  T0 D1 L1
adhesion-work-from-bi-slab          (E_AB, E_A, E_B, A) → W_ad               T1 D2 L4
image-charge-correction-defect      (q, ε_r, L) → ΔE_image                   T0 D1 L3
makov-payne-correction              (q, ε_r, L, α_M) → ΔE_MP                 T0 D1 L3
freysoldt-correction                (q, ε_r, V_avg_profile) → ΔE_FS          T1 D2 L3
murnaghan-eos                       (V, K, K', V₀) → P                       T0 D1 L2
birch-murnaghan-eos                 (V, K, K', V₀) → E                       T0 D1 L2
qha-thermal-expansion               (γ_qν, Cv_qν, K) → α(T)                  T2 D2 L3
gruneisen-mode                      (ω_qν(V)) → γ_qν                         T1 D2 L3
acoustic-sum-rule-correction        (Φ_IαJβ) → Φ_corrected                   T1 D1 L3
born-effective-charge               (∂P/∂u_Iα at E=0) → Z*_Iα                T2 D2 L3
piezoelectric-tensor                (∂P/∂ε at E=0) → e_iα                    T2 D2 L3
elastic-compliance-from-stiffness   (C_IJ) → S_IJ                            T0 D1 L2
debye-temperature-from-velocities   (v_l, v_t, n) → θ_D                      T0 D1 L3
```

*From S3 (defects/doping/surfaces/interfaces/high-T) — 17 entries:*
```
charge-neutrality-residual          ({N_q^(d)}, n, p, N_A^−, N_D^+) → 0       T1 D3 L3
mott-schottky-built-in-potential    (φ_B, N_D, ε_s, T) → V_bi                T0 D1 L4
depletion-width                     (V_bi, N_D, ε_s, V_bias) → W             T0 D1 L4
schottky-barrier-from-bicrystal     (E_F^M, ε_c^S, Δφ_int) → φ_B             T1 D2 L4
fermi-level-self-consistent         ({N_q^(d)(E_F)}, N_c, N_v, T) → E_F     T1 D3 L3
ionization-energy-arrhenius-fit     ({σ_T}) → (E_a, σ_0)                     T0 D1 L4
shockley-read-hall-rate             (n, p, n_t, p_t, τ_n, τ_p) → R_SRH        T0 D1 L4
auger-recombination-rate            (n, p, C_n, C_p) → R_Aug                  T0 D1 L4
radiative-recombination-rate        (n, p, B_rad) → R_rad                    T0 D1 L4
fowler-nordheim-current             (E_field, φ_B, m*) → J_FN                T0 D1 L4
thermionic-emission                 (T, φ_B, A*) → J_TE                      T0 D1 L4
padovani-stratton-tfe               (T, φ_B, N_D, E_field) → J_TFE           T1 D2 L4
surface-grand-potential-perAtom     (E_slab, {μ_i}, {n_i}, A) → γ_surf       T1 D2 L4
adsorbate-equilibrium-coverage      (μ_i, K_eq(T)) → θ_i                     T0 D1 L4
hydrogen-diffusion-effective-D      (D_H, c_traps, E_trap, T) → D_eff       T1 D2 L4
defect-cluster-binding              (E_cluster, Σ E_isolated) → E_bind       T0 D1 L4
oxidation-rate-deal-grove           (T, p_O2, A, B) → x_ox(t)                T0 D1 L4
```

*From S4 (non-equilibrium/high-field/hot-carrier) — 18 entries:*
```
drift-velocity-from-mobility        (μ(E), E) → v_d                          T0 D1 L5
saturation-velocity-caughey-thomas  (μ_0, E, v_sat, β) → v(E)                T0 D1 L5
impact-ionization-coefficient       (E, a_imp, b_imp) → α_imp                T0 D1 L5
chynoweth-ionization                (E, α_∞, E_crit) → α_imp                  T0 D1 L5
keldysh-multiphoton-ionization      (E, ℏω, E_gap) → W_K                     T1 D2 L5
energy-balance-hot-carrier          (j·E, τ_E, T_e, T_L) → ∂_t T_e            T1 D3 L6
electron-temperature-implicit       (j, σ(T_e), ∇T_e, τ_E) → T_e(r)          T2 D3 L6
heat-equation-self-heating          (j·E, κ_L, c_p, T_L, ∇T_L) → ∂_t T_L      T2 D3 L6
peltier-coefficient                 (S, T) → Π_Pelt                          T0 D1 L4
seebeck-coefficient-mott            (σ(E), E_F, T) → S                       T1 D2 L4
nernst-coefficient                  (S, B, σ, n) → N_Nernst                  T1 D2 L4
hall-coefficient                    (n, p, μ_n, μ_p) → R_H                   T0 D1 L4
electromigration-blech              (j, Z*, ρ, σ) → ∇μ_drift                 T0 D1 L5
black-equation-em-lifetime          (j, A_em, n_em, E_a, T) → t_fail         T0 D1 L6
joule-heating-density               (j, E) → q_J                              T0 D1 L5
hot-carrier-injection-luckyelectron (E_field, λ_e, φ_B) → P_inj              T1 D2 L5
poole-frenkel-emission              (E, φ_t, ε_r, T) → J_PF                  T0 D1 L5
trap-assisted-tunneling-rate        (E_t, E_field, N_t, τ_c) → R_TAT          T1 D2 L5
```

*From S6 honest-gap surrogates and Layer-7 closures — 5 entries:*
```
huang-rhys-factor-effective         (Δq², ω_eff) → S_HR                      T1 D4 L7
multiphonon-capture-effective       (S_HR, ℏω_eff, T, ΔE) → C_n_eff          T1 D4 L7
four-phonon-correction-learned      (3ph-baseline, T, anharm-features) → Δκ T1 D4 L7
scph-renormalization-periodic       (ω_harm, ⟨u²⟩, T) → ω_renorm             T2 D4 L7
negf-tunneling-surrogate            (barrier-profile, E_F_lr, T) → J_tun     T2 D4 L7
```

**Each formula record stored under `formulas/registered/<name>.rkt`** with header:

```racket
;; Name: defect-formation-energy
;; Signature: (E_def E_perfect Δn μ q E_F) → Scalar[eV]
;; Source-stream: existing (lifted) | S1 | S2 | S3 | S4 | S6
;; Cost-tier: T0 | T1 | T2 | T3
;; Diff-tag: D0 | D1 | D2 | D3 | D4
;; Layer: 1..7
;; Cited reference: <DOI / paper>
;; Adjoint-validated: #t | #f | not-applicable | relaxed-with-rationale
;; Bundle membership: {B1, B4, ...}
;; Same-pass dependencies: {<formula-names that must co-converge>}
```

The full 87-entry registry-manifest is delivered as a CSV/scm artifact by Phase 7+ — this amendment commits to S6's catalog as the source of truth.

---

## Section 8 — Observable-bundle amendment (apply to existing §10)

**Bundle count: 8 → 11.** The existing 8 bundles are retained; three new bundles are added, and the contents of two existing bundles are extended.

**New bundles (S6 reconciliation):**

```
observables/
  …existing 8 bundles unchanged…
  │
  ├── defect-resolved/                  data shape: per-defect-species map keyed
  │                                     by (host-crystal, defect-tag, charge-state)
  │                                     with scalar / spectral / response payloads
  │                                     Examples:
  │                                       DefectFormationEnergy(d, q, μ, E_F)
  │                                       DefectLevels(d, q)
  │                                       CaptureCrossSection(d, T)
  │                                       SRHLifetime(d, q)
  │
  ├── interface-resolved/               data shape: per-bicrystal map keyed by
  │                                     (left-crystal, right-crystal, termination-pair)
  │                                     with scalar / spectral / response payloads
  │                                     Examples:
  │                                       SchottkyBarrier(M, S, term)
  │                                       BandOffset(A, B)
  │                                       InterfaceDipole(M, S)
  │                                       AdhesionWork(A, B)
  │                                       SpecificContactResistance(M, S, T)
  │
  ├── surface-resolved/                 data shape: per-surface-facet map keyed by
  │                                     (crystal, Miller-indices, termination)
  │                                     with scalar / coverage / spectral payloads
  │                                     Examples:
  │                                       SurfaceEnergy(facet, term, μ)
  │                                       SurfaceReconstructionTrend(facet)
  │                                       AdsorptionIsotherm(facet, species, T)
  │                                       SurfaceDipole(facet, term)
  │
  ├── field-resolved/                   data shape: function over (E-field-magnitude,
  │                                     direction) for transport / breakdown observables
  │                                     Examples:
  │                                       DriftVelocity(E)
  │                                       ImpactIonizationCoefficient(E)
  │                                       FieldEmissionCurrent(E, φ_B)
  │                                       BreakdownField (scalar, extracted)
  │
  ├── hot-carrier-resolved/             data shape: function over (T_e or carrier-energy)
  │                                     with rate / population / spectral payloads
  │                                     Examples:
  │                                       HotCarrierTemperature(j, geometry)
  │                                       HotCarrierInjectionProbability(T_e, φ_B)
  │                                       AvalancheMultiplicationFactor(E, geometry)
  │                                       EnergyRelaxationTime(T_e)
  │
  └── degradation/                      data shape: time-to-failure or rate-vs-stressor
                                        scalars and arrays
                                        Examples:
                                          ElectromigrationMTTF(j, T)
                                          OxidationKineticsCurve(T, p_O2)
                                          DopantDiffusionProfile(T, t)
                                          DielectricBreakdownVoltageTrend(T, t, field)
```

**Extended existing bundles:**

- `temperature-resolved/` extended with `IntrinsicCarrierConcentration(T)`, `MobilityVsT(T)`, `ThermalConductivityVsT(T)`.
- `scalars/` extended with `WorkFunction`, `IonizationEnergy`, `ElectronAffinity`, `BreakdownField`, `SaturationVelocity`, `DebyeTemperature`, `IntrinsicCarrierConcentration_300K`.

**The 11-bundle reconciled list (B1-B11 in S6 nomenclature).**

| S6 ID | Bundle dir | Primary regime contributors |
|---|---|---|
| B1 | `bz-resolved/` + `energy-resolved/` (S6 groups these as electronic-structure functional group) | Level 1 (electronic) |
| B2 | `bz-resolved/` (phonon part) + parts of `tensor-indexed/` | Level 2 (phonon) |
| B3 | `tensor-indexed/` (transport tensors) + `field-resolved/` | Level 4 (transport) |
| B4 | `defect-resolved/` (new) | Levels 2+3+4 (defects) |
| B5 | `surface-resolved/` (new) | Level 2 (surface) |
| B6 | `interface-resolved/` (new) | Level 2 (interface) |
| B7 | `tensor-indexed/` (elastic part) + `atom-indexed/` (forces, displacements) | Level 2 (mechanics) |
| B8 | `scalars/` + `temperature-resolved/` (thermo readouts) | Level 3 (thermodynamics) |
| B9 | `field-resolved/` + `hot-carrier-resolved/` (new) | Level 4 (non-eq operating) |
| B10 | `scalars/` (structural-validity validators) | Level 2 (structural validity) |
| B11 | `degradation/` (new) | Level 4 (degradation) |

The dual labeling (file-system bundle = data-shape sibling; S6 ID = physics-functional grouping) is by design: the **file tree is organized by data shape** (preserving the existing principle from §10) while the **catalog manifest is organized by physics** (so the PINO training loop and cert sub-tree can iterate functionally-coherent groups). The mapping is one-to-many in both directions and lives in `observables/bundle-manifest.scm`.

---

## Section 9 — Residual-category amendment (apply to existing §12)

**Residual-category count: 5 → 7.** Add two new top-level categories.

```
residuals/
  …existing 5 categories unchanged…
  │
  ├── structural-validity/              constraints on geometric / topological
  │                                     validity that are NOT covered by EOM-violation
  │                                     because they constrain admissible inputs, not
  │                                     trajectory evolution.
  │   ├── lattice-coherency             ‖a_film − a_substrate(1+ε_misfit)‖²
  │                                     enforces Matthews-Blakeslee critical-thickness
  │                                     compliance for coherent epitaxy
  │   ├── interface-stoichiometry       ‖Σ_i n_i^(left) − Σ_i n_i^(right)‖²
  │                                     at non-polar interfaces (polar interfaces
  │                                     register expected dipole instead)
  │   ├── slab-thickness-convergence    ‖E_slab(L) − E_slab(L+ΔL)‖² < tol
  │                                     surface energy must be converged in slab thickness
  │   ├── defect-supercell-isolation    ‖E_def(L) − E_def_extrap(∞)‖²
  │                                     enforces image-charge-corrected convergence
  │   └── space-group-consistency       symmetry of relaxed state == declared space group
  │                                     (or symmetry-breaking flag set)
  │
  └── thermodynamic-consistency/        constraints from second-law and equilibrium
                                        relations that are NOT degeneracy conditions
                                        (those stay in degeneracy/) and NOT pure
                                        algebraic identities (those stay in
                                        algebraic-identities/).
      ├── convex-hull-membership        ‖max(0, F_phase − F_hull(x_phase))‖²
                                        a predicted phase must lie on or above
                                        the predicted convex hull
      ├── chemical-potential-bounds     ‖max(0, μ_i − μ_i^ref(elemental))‖²
                                        μ-values must not exceed elemental references
                                        (else the elemental phase precipitates)
      ├── detailed-balance-fluxes       Σ_i (R_i^forward − R_i^backward)² at equilibrium
                                        net flux must vanish at thermal equilibrium
                                        (distinct from rate-symmetry detailed-balance
                                        which lives under algebraic-identities/)
      ├── carrier-charge-balance        ‖p − n + Σ_d q_d N_d^q‖²
                                        global charge neutrality on the device scale
      └── gibbs-phase-rule-consistency  declared (#phases, #components, #constraints)
                                        satisfies Gibbs' inequality
```

**Per S6 explicit decision:** the `coupled-em-thermal-pde-residual` (Joule heating + heat equation + drift-diffusion-Poisson + Maxwell) is registered as a **sub-residual under `eom-violation/`** (specifically `eom-violation/coupled-multi-physics-pde.rkt`), NOT as a new top-level category. Rationale: it is a Level-4 manifestation of the GENERIC EOM applied to emergent fields, not a categorically new constraint.

**No overlap with existing 5 categories:**

| New category | Distinguished from existing | Rationale |
|---|---|---|
| `structural-validity` | not `positivity` | constrains input admissibility, not bounds on outputs |
| `structural-validity` | not `conservation` | no conserved quantity; rather geometric soundness |
| `thermodynamic-consistency` | not `degeneracy` | concerns thermodynamic state, not GENERIC operator structure |
| `thermodynamic-consistency` | not `algebraic-identities` | concerns inequalities and finite-data fixed-points, not closed-form formula equivalences |

---

## Section 10 — Cert-obligations amendment (apply to existing §13)

**Cert-obligation count: 6 → 10.** Add four new obligations, none redundant with the existing six.

```
cert/
  …existing 6 obligations unchanged…
  │
  ├── obligation-7-bulk-edge-correspondence
  │                                     Where applicable (topological insulators,
  │                                     polar surfaces with bound charges), bulk
  │                                     invariants must predict surface/edge state
  │                                     counts (S1-flagged: "physicist gap" vs
  │                                     "mathematician gap"). Verdict is per-system
  │                                     conditional — non-topological systems mark
  │                                     this obligation NA with rationale.
  │
  ├── obligation-8-reference-battery-versioned
  │                                     Formalizes the held-out battery of S3+S5:
  │                                     a SHA-pinned set of (Crystal, Environment,
  │                                     {observable: value, σ}) tuples assembled
  │                                     from VASP ground truth + curated
  │                                     experimental data. Distinct from
  │                                     obligation-4 (which is a frozen-fixture
  │                                     regression tripwire); obligation-8 is the
  │                                     ground-truth diff. Requires per-entry
  │                                     provenance (source, version, uncertainty).
  │
  ├── obligation-9-surrogate-net-validity
  │                                     For every D4 (autodiff-relaxed, surrogate-
  │                                     net-bridged) formula entry, a validity cert
  │                                     must accompany the prediction: (a) input
  │                                     domain of the surrogate is declared and
  │                                     queried point lies within it; (b) surrogate
  │                                     uncertainty is below a per-formula
  │                                     tolerance; (c) periodic refresh against
  │                                     the underlying physics is up-to-date per
  │                                     declared schedule. Failure of any subclause
  │                                     trips the tripwire with witness.
  │
  └── obligation-10-adjoint-existence-at-registration
                                        ENFORCED AT REGISTRATION TIME, not at
                                        prediction time (hard gate per S6). For
                                        every D2 formula record, the
                                        make-residual-generator factory invokes a
                                        numerical-adjoint check (vJp ≈ JvP up to
                                        tolerance on a sampled input). A formula
                                        that fails this check cannot be registered
                                        with diff-tag D2 — must be downgraded to
                                        D3 (implicit) or D4 (relaxed with explicit
                                        rationale recorded in the obligation log).
```

---

## Section 11 — Residual-generator factory (NEW SECTION — insert as §19)

This is the **new load-bearing architectural piece** demanded by S5 and elaborated in S6. It lives at `library/generic/residual-generator.rkt` and `library/residuals/registered/`.

### 19.1 The `ResidualGenerator` record

```racket
(struct ResidualGenerator
  ([name           : Symbol]                       ;; unique key into registry
   [observable     : ObservableRef]                ;; which observable this is the residual for
   [bundle         : BundleId]                     ;; B1-B11
   [layer          : (U 1 2 3 4 5 6 7)]            ;; S6 DAG layer
   [cost-tier      : (U 'T0 'T1 'T2 'T3)]
   [diff-tag       : (U 'D0 'D1 'D2 'D3 'D4)]
   [source-tag     : (U 'cheap-generate            ;; tier-A: produces approximate labels
                        'faithful-residual         ;; tier-B: physically-accurate loss term
                        'ground-truth-bridge       ;; consumes external (VASP / expt)
                        'cert-only)]               ;; used only by cert sub-tree
   [input-contract : (Listof TypedSlot)]           ;; what state slices + env fields needed
   [output-contract: TypedSlot]                    ;; what shape comes out
   [forward        : (-> Inputs Output)]           ;; the residual computation
   [backward       : (U (-> Inputs Output Cotangent Cotangent)
                        #f)]                       ;; vJp; #f when D0/D4
   [loss           : (-> Output Scalar)]           ;; how this residual contributes to total loss
   [weight-policy  : WeightPolicy]                 ;; GradNorm | fixed-init | curriculum-staged
   [sampling-policy: SamplingPolicy]               ;; uniform | RAD | importance | validation-only
   [dependencies   : (Setof Symbol)]               ;; other ResidualGenerator names that must
                                                   ;; fire in same pass (Layer-3↔5 closure)
   [adjoint-cert   : AdjointCertVerdict]           ;; set at registration time
   [registration-time : Timestamp]
   [registration-hash : Sha256])                  ;; for cert-tripwire detection
  #:transparent)
```

Supporting types:

```racket
(define-type TypedSlot (List Symbol TypeExpr Unit))
(define-type WeightPolicy
  (U 'gradnorm-outer
     (List 'fixed-init Real)
     (List 'curriculum-staged Phase Phase Phase Phase)))
(define-type SamplingPolicy
  (U 'uniform-mesh
     (List 'rad Real)                              ;; residual-adaptive sampling, with τ
     (List 'importance (-> StatePoint Real))
     'validation-only))
(define-type AdjointCertVerdict
  (U 'passed
     (List 'failed Real)                           ;; with witness: max(|vJp − JvP|)
     'not-applicable
     (List 'relaxed Rationale)))
```

### 19.2 The factory function

```racket
(: make-residual-generator
   (-> #:observable ObservableRef
       #:path PathOfMethodsAndFormulas
       #:distance DistanceMetric
       #:weight-policy WeightPolicy
       #:sampling-policy SamplingPolicy
       #:source-tag SourceTag
       ResidualGenerator))

(define (make-residual-generator
          #:observable observable
          #:path path
          #:distance distance
          #:weight-policy weight-policy
          #:sampling-policy sampling-policy
          #:source-tag source-tag)
  ;; 1. Resolve typed signatures by composing along `path` — error if not type-consistent.
  ;; 2. Determine bundle, layer, cost-tier, diff-tag from path metadata.
  ;; 3. Synthesize forward closure by composing methods + formulas along path.
  ;; 4. If diff-tag in {D1, D2, D3}: synthesize backward closure.
  ;;    If diff-tag = D2: RUN THE ADJOINT VALIDATION GATE NOW.
  ;;      - Sample N points in the registered input domain.
  ;;      - Compute vJp via the synthesized backward.
  ;;      - Compute JvP via forward-mode autodiff on a numerical perturbation.
  ;;      - Compare; if max relative error > τ_adj, raise:
  ;;        (registration-failed 'adjoint-validation
  ;;                              #:witness max-error
  ;;                              #:offered-downgrade '(D3 D4))
  ;;    If diff-tag = D4: require explicit rationale string; record under
  ;;      obligation-9 (surrogate-net-validity) with the relaxation reason.
  ;; 5. Synthesize loss closure from distance metric.
  ;; 6. Resolve same-pass dependencies (Layer-3↔5 fixed-point cycle).
  ;; 7. Compute registration hash; emit registry entry.
  ...)
```

### 19.3 Registration discipline

Every entry in the 87-formula catalog is registered exactly once via this factory call, at library load time. The registry — `residuals/registered/` — is build-time-generated from the manifest `formulas/registry-manifest.scm`. Adding a new residual is a three-step diff:
1. Add the manifest entry.
2. Add the formula module under `formulas/registered/`.
3. Re-run the registration build; the adjoint gate fires automatically.

If a D2 entry fails the gate, the build fails loud — no PINO can train against a silently-broken backward.

### 19.4 Training-loop consumption pattern

`/informed-operator` consumes the registry via:

```racket
(: enumerate-active-residuals (-> CurriculumPhase (Listof ResidualGenerator)))
(: layer-grouped (-> (Listof ResidualGenerator) (Listof (Listof ResidualGenerator))))

;; Per training step:
(for ([layer-batch (layer-grouped (enumerate-active-residuals phase))])
  (for ([rg layer-batch])
    (define sample-points (sample (ResidualGenerator-sampling-policy rg)))
    (define forward-out (apply-forward rg sample-points))
    (define loss-contrib (apply-loss rg forward-out))
    (accumulate-into-total-loss rg loss-contrib))
  ;; Layer barrier: same-pass fixed-point iteration runs here for L3↔L5 cycle.
  (close-fixed-point-if-needed layer-batch))
```

### 19.5 How tags drive scheduling

- `cost-tier` determines per-step sampling budget — T0 always evaluated, T1 evaluated per minibatch, T2 evaluated per outer step, T3 evaluated only as validation triggers per the curriculum.
- `diff-tag` determines whether the residual contributes to gradient-bearing loss (D1-D3) or to gradient-free validation (D0, D4 unless surrogate provides backward).
- `layer` determines execution order — a Layer-N residual cannot fire until all its declared Layer-M (M < N) dependencies have closed in the same pass.
- `source-tag` partitions the registry into the three /pino-bridge exports (Section 12).

---

## Section 12 — PINO integration: three exports (NEW SECTION — insert as §20)

The `/physics` library exposes exactly three typed surfaces to `/informed-operator`. Each surface is a single typed function with explicit contract, autodiff boundary, and data-format handshake.

### 20.1 `Generate` — cheap-compute label production

```racket
(: Generate
   (-> #:inputs   (List PeriodicityStructure SiteDecoration Environment)
       #:request  (Listof ObservableRef)
       #:tier     (U 'cheap-only 'cheap-with-fallback)
       (HashTable ObservableRef GeneratedLabel)))

(define-struct GeneratedLabel
  ([value         : ObservableValue]
   [cost-tier     : (U 'T0 'T1 'T2)]                ;; T3 never emitted by Generate
   [provenance    : (Listof ResidualGeneratorRef)]  ;; which generators produced this
   [uncertainty   : Real]                            ;; estimated; from surrogate net or
                                                     ;; from formula-level error bound
   [cache-hit?    : Boolean]))                       ;; reference-cache lookup status
```

- **Contract:** produces approximate labels suitable for training but not for validation. The cheap-tier path uses cached reference-battery entries where available; otherwise composes T0-T2 formulas in source-tag `cheap-generate`.
- **Autodiff boundary:** Generate is **NOT differentiated through** by the PINO. It is a pre-compute step; outputs flow into the training set as fixed targets.
- **Data-format handshake:** outputs use the same `ObservableValue` algebra as `Validate` and `Import`, so the training loop can mix sources transparently.

### 20.2 `Validate` — faithful-residual path

```racket
(: Validate
   (-> #:state           UnifiedState
       #:env             Environment
       #:phase           CurriculumPhase
       #:request         (U 'all (Listof ResidualGeneratorRef))
       (List #:total-loss     Scalar
             #:per-residual   (HashTable ResidualGeneratorRef Scalar)
             #:gradients      (U Cotangent #f)
             #:cert-evidence  CertEvidence)))
```

- **Contract:** evaluates registered residuals with `source-tag ∈ {'faithful-residual, 'cert-only}` on a predicted state. Returns total loss, per-residual breakdown, gradients (when requested), and accumulated cert evidence.
- **Autodiff boundary:** Validate **IS differentiated through**. The PINO trains its weights `θ` by backpropagating through Validate's gradient output. The factory-synthesized `backward` closures are the load-bearing pieces here.
- **Data-format handshake:** `UnifiedState` is the exact 7-tuple from §3.1; `CertEvidence` is the inert-sexpr cert format from §13.

### 20.3 `Import` — external ground-truth ingestion

```racket
(: Import
   (-> #:source        (U 'vasp 'experimental 'curated-battery)
       #:provenance    Provenance
       #:payload       ExternalPayload
       (List #:training-targets (HashTable ObservableRef TargetEntry)
             #:cert-evidence    CertEvidence)))

(define-struct TargetEntry
  ([value        : ObservableValue]
   [uncertainty  : Real]                              ;; σ for Huber loss
   [provenance   : Provenance]
   [coverage     : CoverageMask]))                    ;; which residuals this target
                                                     ;; participates in
```

- **Contract:** accepts external data; validates against schema; emits training targets with per-observable uncertainty `σ` (Huber loss in S5) and a coverage mask (which residuals the target participates in).
- **Autodiff boundary:** Import is **NOT differentiated through**. Targets flow into the training set as fixed values.
- **Data-format handshake:** `ExternalPayload` recognizes VASP `OUTCAR/vasprun.xml`, experimental CSV/JSON with declared schema, and the project's own curated battery format (SHA-pinned).

### 20.4 Sealing

Exactly these three functions are exported from `pino-bridge/api.rkt`. Nothing else from the library is visible to `/informed-operator`. All other public functions (`Predict`, `Certify`, `EnumerateObservables`) remain available via `library/api.rkt` for non-PINO consumers.

---

## Section 13 — Multi-source training discipline (NEW SECTION — insert as §21)

Per S5 + S6. This section gives `/informed-operator` the contract it must satisfy when consuming `/physics`. It is documented here because the schedule knobs constrain the residual-generator weight-policies registered in `/physics`.

### 21.1 Four-phase curriculum

```
Phase           Fraction      Active residual source-tags             Notes
─────────────────────────────────────────────────────────────────────────
Warmup          0.00 - 0.10   cheap-generate (targets) +              Operator learns
                              D0/D1 faithful-residual                 functional form;
                                                                      no heavy autodiff;
                                                                      no T2/T3 residuals.

Refine          0.10 - 0.60   D1/D2 faithful-residual full;           Bulk of training;
                              T0/T1 weights GradNorm-balanced;        Layer 1-5 active.
                              experimental targets enter via Import.

Calibrate       0.60 - 0.90   Add D3 (implicit-function) residuals;   Layer 6 closures;
                              activate same-pass L3↔L5 cycle;         coupled PDE residual.
                              T2 residuals enter on RAD-sampled
                              minibatches.

Polish          0.90 - 1.00   Add D4 surrogate-net residuals;         Degradation/long-time
                              T3 validation triggers fire             observables stabilized.
                              periodically (not every step);
                              obligation-9 cert checks per epoch.
```

The fractions `(0.10, 0.60, 0.90)` are **defaults** and exposed as knobs. They are user-confirmation-required (see Section 15).

### 21.2 Outer / inner weight balance

- **Outer (per source-tag):** GradNorm across `{cheap-generate-targets, faithful-residual, ground-truth-bridge}`. One learnable weight per source-tag, updated on the gradient-norm-balance objective with the standard α=1.5 default.
- **Inner (per residual within faithful-residual):** **NTK-initialization fixed** weights. Compute NTK eigenvalues at initialization, assign weights inversely proportional to the leading NTK eigenvalue per residual, **freeze**. This is S5's MLIP-derived lesson: architectural choices (here NTK weighting) outperform learned soft balancing in the inner loop.

### 21.3 Coverage-mask discipline

Every `TargetEntry` from `Import` carries a `CoverageMask` declaring which observables the target was actually measured for. The multi-source loss respects the mask: a target observed for `BandGap` only does not contribute to the `BandStructure` residual. This avoids the standard PINO failure mode of optimizing against silently-zero ground-truth slots.

### 21.4 Huber on experimental terms

Experimental targets enter via Huber loss with per-observable `σ` from the `TargetEntry`. The Huber transition point is set at `1.345 σ` (95% efficiency under Gaussian; standard). Targets from `vasp` source use squared-error loss (no outliers expected from systematic ground truth).

### 21.5 RAD sampling for T1 entries

Residual-Adaptive Density sampling: at each Refine/Calibrate step, every T1 entry's last residual values are used to construct a per-input-domain probability density, and minibatch sampling is biased toward high-residual regions. The bias coefficient `τ` is registered per generator at `sampling-policy = (rad τ)`; default `τ = 1.0` (linear bias).

### 21.6 T3 validation-only

T3 entries (self-consistent, expensive) are NEVER used as gradient-bearing training signals. They fire as **validation triggers** at end of each curriculum phase and as periodic checks in Polish; their verdicts feed cert evidence, not gradients.

### 21.7 Defaults exposed as user knobs

| Knob | Default | Range | Section |
|---|---|---|---|
| Phase fractions | (0.10, 0.60, 0.90) | three monotone in [0,1] | 21.1 |
| GradNorm α | 1.5 | (0, 3] | 21.2 |
| NTK-init refresh | once at init | once / every-N-epochs | 21.2 |
| Huber transition | 1.345 σ | (0.5, 3.0] σ | 21.4 |
| RAD τ | 1.0 | [0, 2] | 21.5 |
| T3 validation cadence | once per phase + every 10% of Polish | per-phase configurable | 21.6 |
| Adjoint validation tolerance τ_adj | 1e-4 | (1e-6, 1e-2] | §19.2 |

---

## Section 14 — Out-of-scope declarations (NEW SECTION — insert as §22)

Per S1's 12 limits plus S6's 5 honest gaps. Each entry below states **what is excluded**, **why**, and **how the library behaves when asked anyway**.

| # | Topic | Exclusion rationale | Library behavior |
|---|---|---|---|
| 1 | Strongly-correlated systems (frustrated Wigner crystals, Mott insulators, heavy-fermion) | DFT-based Kohn-Sham closure inadequate; would require DMFT or beyond | Predict raises `out-of-scope` with witness; cert obligation-3 (analytic limits) flags band-structure as suspect |
| 2 | Flexoelectricity in centrosymmetric materials | Higher-gradient response below current numerical-noise floor for diamond/c-BN; order-of-magnitude tracking only | Reported as order-of-magnitude with explicit uncertainty band, no PINO loss term |
| 3 | Magneto-thermal coupling in heavy contact metals (W, Ir, Pt) | Spin-phonon entropy production negligible at relevant temperatures, but coupling formally enters S; not modeled | Treated as zero in M; cert obligation-5 (conservation) does not check spin entropy production for these species |
| 4 | Deep-defect non-Markovian dynamics | Markov master-equation closure assumed; non-Markovian memory kernels out of scope | Predict valid only for trap depths shallow enough that Marcus / SRH apply |
| 5 | Polaron localization beyond Fröhlich | Small-polaron self-trapping treated only via Fröhlich coupling; large-polaron self-consistent treatment not modeled | Cert obligation-3 flags transport in materials where polaron-radius < few unit cells |
| 6 | 4-phonon scattering | T2/T3 cost prohibitive at training cadence | Replaced by `four-phonon-correction-learned` (D4, surrogate net); obligation-9 monitors |
| 7 | Full NEGF tunneling | Computational cost; out of scope for residual-generator factory | Replaced by `negf-tunneling-surrogate` (D4); also Padovani-Stratton + Fowler-Nordheim entered as T0/T1 proxies |
| 8 | Full SCPH / SSCHA | Self-consistent phonon renormalization too expensive per step | `scph-renormalization-periodic` (D4); periodic refresh between curriculum phases |
| 9 | Plasma-process surface damage | Process-specific; outside library's substrate-agnostic remit | Predict returns nominal pristine values; user injects process effects via Import |
| 10 | Grain-boundary statistics | Polycrystalline aggregation requires statistical sampling outside `/physics` scope | Predict requires single-crystal or explicit bicrystal input |
| 11 | Continuum creep / dislocation climb | Out of GENERIC formulation's elastic regime | Reported via `degradation/` bundle as empirical fit only; no L/M operator entries |
| 12 | Quantum-tunneling-corrected reaction rates | Classical Eyring TST adequate at jet-turbine T (T_op ≥ 600 K well above tunneling crossover for relevant barriers) | Vineyard / hTST classical; obligation-3 flags below 200 K |

---

## Section 15 — Outstanding decisions for user (NEW SECTION — insert as §23)

Choice points this amendment cannot resolve. Each blocks a specific phase; ordered by urgency.

1. **Implementation language (BLOCKS Phase 1, immediate).** Original plan deferred. With the residual-generator factory and three pino-bridge exports added, the choice now has stronger constraints:
   - **Racket + Typed Racket**: matches source library exactly; macro staging is excellent for the factory; but autodiff library ecosystem is thin — would require building D2 backward synthesis from scratch.
   - **Python + JAX**: best autodiff + GPU; `jit` covers staged-code-generation pattern; but loses Racket's macro discipline and module-seal style.
   - **OCaml + Owl**: typed seal natively; reasonable autodiff; but smaller community.
   - **Recommendation pending user input.** Default to Python + JAX given S5's NTK + GradNorm machinery is well-supported there; revisit only if Racket macro discipline is non-negotiable.

2. **Cache backend for `ReferenceCache` (BLOCKS Phase 2 + Phase 7).** Options:
   - SQLite with content-addressed schema (simple, single-file, portable).
   - DuckDB (better analytic queries, columnar).
   - Sled / LMDB embedded KV (fastest read).
   - File-tree of pickled / JSON blobs (simplest, debuggable, slowest).
   - Versioning policy: SHA-pin every input tuple → output tuple; immutable add-only.
   - **Recommendation pending user input.** Default SQLite + SHA-pinned schema.

3. **Surrogate-net infrastructure: build vs adopt (BLOCKS Polish phase of training).** The five D4 entries (Huang-Rhys, multiphonon-capture, 4-phonon, SCPH, NEGF-tunneling) need surrogate nets. Build in-house (full control, more work) or adopt MACE/Allegro/SchNet (faster bootstrap, less control). **Pending user input.**

4. **PDE-mesh format and adjoint library choice (BLOCKS Calibrate phase).** The coupled-em-thermal-PDE residual requires a PDE solver with adjoint. Options: FEniCS + dolfin-adjoint, Firedrake + pyadjoint, JAX-FEM, write custom finite-volume in JAX. **Pending user input.**

5. **Coverage-mask format (BLOCKS Phase 10/11 + Import design).** Per-sample dense bitmask (simple, small N_obs ≤ 100) vs sparse representation (necessary at N_obs ≥ 1000). With the 11-bundle structure currently sitting around N_obs ~ 200 entries, dense bitmask is marginally feasible. **Recommendation pending user input.** Default sparse from the start to avoid rewrite.

6. **Curriculum schedule (0.10, 0.60, 0.90) (DEFAULT BUT CONFIRMABLE).** These came from S5's standard PINO curriculum literature. User may wish to extend Polish (e.g. 0.80, not 0.90) if degradation observables prove hard.

7. **Active-learning loop integration timing (BLOCKS Phase 13+).** Does `/physics` support an active-learning loop where the PINO requests Import expand its battery? If yes, requires a 4th pino-bridge export `RequestGroundTruth`. **Pending user input. Default: no, active learning is `/interface`'s concern.**

---

## Section 16 — Verification plan (NEW SECTION — insert as §24)

How to know this amendment lands correctly. Five sequential gates.

**Gate 1 — Registration sanity.** The 87-entry catalog instantiates as registered `ResidualGenerator` records at library load time without error.
- All D2 entries pass the adjoint-validation gate (`max(|vJp − JvP|) < τ_adj` on N=64 sample points).
- All D4 entries carry an explicit rationale string and an obligation-9 entry.
- All D0/D1 entries register with `backward = #f` and a typed witness that no adjoint is needed.
- **Pass criterion:** `library-load-cert.scm` emits 87 `'passed` verdicts (or explicit acceptable downgrades).

**Gate 2 — Worked-example end-to-end.** The S6 §6 Diamond-W-Schottky-500°C worked example executes:
- Input: diamond bulk + W contact + Si-substrate / Environment(T=773 K, applied_field=1 MV/cm).
- Layers 1-7 fire in order; Layer 3↔5 cycle closes via same-pass fixed point in ≤ 5 iterations.
- 37 residual firings traced and accounted for in the cert manifest.
- Output: Schottky barrier, drift velocity, electron temperature, self-heating ΔT, predicted MTTF.
- **Pass criterion:** end-to-end run completes in declared T2 budget; cert obligations 1, 2, 3, 5, 8 emit verdicts; total residual finite and below sentinel threshold.

**Gate 3 — Curriculum sanity on synthetic problem.** A four-phase training run on a small-scale synthetic problem (Si bulk, ~5 observables, 1k samples) runs to completion without:
- GradNorm divergence (any weight exceeding 10× initial).
- Layer-3↔5 fixed point failing to converge in any minibatch.
- Adjoint-cert reset (no D2 entry should fail mid-training; failure means a sampled state escaped the registered input domain — a separate cert tripwire).
- **Pass criterion:** loss curves monotone within each phase; phase transitions cause expected loss bumps that recover within 100 steps.

**Gate 4 — Cross-regime cert obligations fire correctly.**
- Existing obligation-6 (BTE-σ ≡ Kubo-σ on equilibrium): unchanged behavior on Si@300K reference state.
- New obligation-9 (surrogate-net validity): deliberately query a D4 entry outside its declared input domain; obligation must trip with witness.
- New obligation-10 (adjoint-existence-at-registration): attempt to register a synthetic D2 formula known to fail adjoint; the registration must fail loud at build time, not silently.
- New obligation-7 (bulk-edge correspondence): on non-topological diamond, must emit NA with rationale; on a contrived synthetic Z₂ topological system, must emit the predicted edge-state count.

**Gate 5 — `/informed-operator` integration smoke test.** A minimal `/informed-operator` consumer:
- Calls `Generate` to populate training targets for 10 Si observables.
- Calls `Validate` on a randomly-initialized state and obtains finite loss + finite gradients of declared shape.
- Calls `Import` on a synthetic VASP-formatted payload and obtains TargetEntry records with declared coverage masks.
- All three exports return within type-checked contracts.

**All five gates passing constitutes amendment-landed verdict.**

---

## Section 17 — Post-amendment migration plan (NEW SECTION — insert as §25)

Once this amendment lands, the user wants to fold the staging-area research outputs (S1-S7) into the project structure. Recommended consolidation order and destinations:

### 25.1 File migrations

| Staging artifact | n-Op destination | Notes |
|---|---|---|
| S1 UWBG observable catalog | `physics/research/uwbg-observable-catalog.md` | New companion file alongside group-A/B/C |
| S2 CSP + heterostructure | `physics/research/csp-heterostructure.md` | New companion |
| S3 defects/doping/surfaces/interfaces | `physics/research/defects-surfaces-interfaces.md` | New companion |
| S4 non-equilibrium / high-field | `physics/research/non-equilibrium-high-field.md` | New companion |
| S5 PINO residual methodology | `informed-operator/design/residual-loss-methodology.md` | Belongs in `/informed-operator`, not `/physics` |
| S6 deduplicated cheap-residual catalog | `physics/research/residual-generator-catalog.md` + `physics/library/formulas/registry-manifest.scm` (machine-readable extract) | Companion AND build artifact |
| S7 this amendment | Apply as edits to `IMPLEMENTATION-PLAN.md`; archive original draft as `physics/research/amendment-s7-original.md` for traceability | |

### 25.2 Agent outputs as research vs cert references

- Stream outputs that are **methodological** (S5, parts of S6) become `research/` companions to `IMPLEMENTATION-PLAN.md`.
- Stream outputs that are **catalogs of facts** (S1, S2, S3, S4 tables; S6 87-entry list) become both research companions AND **cert reference data** in `physics/library/cert/reference-data/` (so obligation-8 has machine-readable source-of-truth).

### 25.3 Recommended consolidation order

1. Apply Sections 2-10 of this amendment as in-place edits to `IMPLEMENTATION-PLAN.md`.
2. Append Sections 11-17 as new sections §19-§25.
3. Create `physics/research/` companion files per 25.1.
4. Extract S6's catalog into `formulas/registry-manifest.scm`.
5. Create `physics/library/cert/reference-data/` and populate with S1-S4 tabular data.
6. Make a single commit titled "S1-S7 research integration; UWBG retargeting amendment" recording the move.
7. Resolve Section 15 outstanding decisions in separate, focused commits before starting Phase 1.

---

## End of amendment proposal

**Summary of deliverable.** This document specifies, in edit-ready form:
- 4 in-place edits to existing sections (§3.1, §5.3, §7, §8, §10, §11, §12, §13).
- 7 new sections (§19-§25) covering the residual-generator factory, the three pino-bridge exports, multi-source training discipline, out-of-scope declarations, outstanding user decisions, verification gates, and post-amendment migration.
- The unified state vector is **unchanged**.
- The GENERIC bracket form is **unchanged**.
- The four-level BO hierarchy is **unchanged**.
- The 12-method computational vocabulary is **unchanged**.
- The PINO-facing surface is **explicitly bounded** to three typed exports.
- The 87-entry formula catalog from S6 is adopted as the canonical registry.
- Every architectural addition is grounded in a specific stream's finding.

**Word count: ~9700.**

Ready to land.
