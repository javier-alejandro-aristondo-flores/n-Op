# Crystal-Structure-Prediction & Heterostructure-Prediction Residuals for `/physics`

This is a methodology survey of crystal-structure-prediction and heterostructure residuals, grounded in the project architecture (GENERIC dynamics dx/dt = L·δE/δx + M·δS/δx, the 4-level Born–Oppenheimer hierarchy, and the closed method / template / formula registries), proposing where new residuals plug in.

> **Conventions.** Misfit convention: `(a_film − a_sub)/a_sub`, matching
> `defects-surfaces-interfaces.md` Part H. χ is termination-tagged (defects file Part E is
> canonical). Contact-table values (Pt barrier, carbide onsets) are survey-grade — pin
> provenance at the metals wave. History: `## Changelog` at the end of this file.

All "typed signatures" below use the convention `name : (input-types) -> output-type [cost-tier, differentiability]`, with cost tiers `T0` (closed-form, ~µs), `T1` (small linear algebra / sums, ~ms), `T2` (ML-potential single-point, ~10ms–1s), `T3` (DFT-single-point, minutes–hours), `T4` (full self-consistent loop, hours–days). Differentiability ratings: `D+` (smooth analytic), `D0` (piecewise smooth, subgradient OK), `D-` (combinatorial; needs surrogate / softening).

---

## Part A — CSP Methodology Survey (CS-grounded)

CSP is fundamentally **discrete-continuous combinatorial search under a black-box energy oracle**. Every method is a (search-strategy, scoring-function, convergence-criterion) triple over the same configuration space.

**Configuration space (canonical encoding).** A crystal candidate is `c = (lattice ∈ R^{3×3}, species ∈ Σ^N, frac_coords ∈ [0,1)^{N×3}, occupancies ∈ [0,1]^N, optional spin/charge labels)` modulo space-group symmetry and lattice equivalence. Symmetry quotient collapses the space by factors of 10²–10⁴ but introduces non-smooth equivalence classes.

**Scoring function (canonical).** Ground-truth `E(c)` is a DFT total energy → formation energy → hull-distance pipeline. Cheap surrogates substitute classical potentials, ML potentials, or bond-counting heuristics.

### A.1 Method-by-method

| Method | Search space | Search strategy | Scoring | Convergence | Cheap proxy | Faithful residual |
|---|---|---|---|---|---|---|
| **USPEX (evolutionary)** | Fixed composition or variable-composition; symmetry-constrained lattices | Genetic ops: heredity (slab cut + paste), mutation (lattice strain, atom swap), softmutation (along phonon eigenmode) | DFT relax → E_form; fitness = -ΔH_hull | Generations without improvement (plateau detection) | Bond-counting + Ewald electrostatic + soft-sphere overlap | DFT-PBE+D3 with k-point convergence; hull from Materials Project facet |
| **CALYPSO (PSO)** | Same as USPEX | Particle-swarm: velocity = inertia·v + c1·(p_best - x) + c2·(g_best - x) in symmetry-constrained subspace | DFT relax | Swarm diversity collapse | Buckingham/Lennard-Jones pair sum | Same as USPEX |
| **AIRSS (random)** | Restricted: cell volumes from species radii, "sensible" species-pair constraints | i.i.d. sampling of symmetry-seeded structures, local relax only | DFT relax → keep low-E basin reps | Coverage of low-E basins; usually fixed budget | Hard-sphere packing + EAM | DFT-PBE plus phonon screen |
| **Prototype substitution** | Discrete: { (prototype, species_assignment) : prototype ∈ ICSD } | Enumerate prototypes × species perms; rank by similarity heuristics | DFT relax of top-K | Top-K converged | Mendeleev-number similarity + size mismatch | DFT-PBE+D3 |
| **ML-potential-driven (GAP, NequIP, MACE)** | Same continuous lattice+coords; basin-hopping or MD-quench | MD at T → quench; or basin-hopping with MLIP gradients | MLIP energy + ensemble-variance uncertainty; DFT spot-check | MLIP-DFT energy gap < ε on held-out | MLIP single-point | DFT single-point + active-learning loop on high-uncertainty configs |
| **Generative (CDVAE, DiffCSP, FlowMM, MatterGen)** | Continuous latent z ∈ R^d; decoder → (lattice, types, coords) | Diffusion in coord+lattice+type space; flow-matching on Riemannian manifold (lattice ∈ GL(3)/symmetries) | Property-conditioned likelihood + classifier guidance | Sample acceptance rate; FID-like structural metric | Decoder forward pass | DFT relax of top samples; symmetry repair |

### A.2 Strengths and failure modes

- **USPEX/CALYPSO** — strength: global; failure: cost (10⁴ DFT relaxations); poor at high-Z or magnetic systems where DFT itself is unreliable.
- **AIRSS** — strength: embarrassingly parallel, no hyperparameter drama; failure: scales badly with N; misses entropy-stabilized phases.
- **Prototype substitution** — strength: nearly free, finds known-class winners; failure: cannot discover novel topologies.
- **MLIP-driven** — strength: 10³–10⁴× speedup; failure: extrapolation cliff outside training distribution; missing dispersion or magnetic order; chemistry-blindness for new species.
- **Generative** — strength: amortized sampling, conditional design; failure: symmetry violations, charge-imbalance hallucinations, mode collapse on common space groups (Fd-3m, P6₃mc dominate).

### A.3 The PINO connection

The PINO is itself a generative-property predictor: input (composition + crude structure descriptor) → output (electronic/elastic/thermal properties). The CSP loop is **outside** the PINO. But the PINO's residual loss is exactly what every CSP method also needs: a cheap differentiable validity oracle. The same residual library can:
1. Train the PINO (physics-loss term).
2. Filter generative samples before DFT (CDVAE/MatterGen post-filter).
3. Guide MLIP-driven basin hopping (acquisition function = predicted property + validity residuals).

This is the leverage point. Build the residual library **once** and reuse it in every CSP backend.

---

## Part B — Validity / Scoring Residuals

For each residual: cheap-compute form for the inner-compute path (label generation), faithful form for the physics-informed loss. All residuals normalized so `R = 0` ⇔ constraint satisfied; `R > 0` ⇔ violation.

### B.1 Catalog table

| Residual | Signature | Cheap (T0–T1) | Faithful | Tier | Diff |
|---|---|---|---|---|---|
| `R_HumeRothery` | `(species_pair, radii, EN, valence) -> R⁺` | `Σ_pairs max(0, |r_A-r_B|/r̄ - 0.15)² + λ_EN·(ΔEN)²` | Same; thresholds calibrated against alloy database | T0 | D+ |
| `R_Pauling` | `(coordination, charges, radii) -> R⁺` | 5 sub-residuals: radius-ratio bands, electrostatic valence, polyhedral sharing penalties | Bond-valence-sum with tabulated `b₀` | T0 | D+ |
| `R_ChargeBalance` | `(species, oxidation_states, multiplicities) -> R⁺` | `(Σ_i n_i · z_i)²` | Same | T0 | D+ |
| `R_Stoichiometry` | `(composition_target, composition_actual) -> R⁺` | `Σ_e (n_e^target - n_e^actual)²` | Same | T0 | D+ |
| `R_HullDistance_cheap` | `(composition, E_form_predicted, hull_facets) -> R⁺` | `max(0, E_form - E_hull(composition))²` with PINO-predicted E_form | Recompute hull from converged DFT of competing phases | T1 / T3 | D0 |
| `R_FormationEnergy` | `(structure, μ_elements) -> R⁺` | Bond-counting Σ ε_ij(d_ij) − Σ μ_i n_i (Tersoff-like) | DFT total E − Σ μ_i n_i | T1 / T3 | D+ / D+ |
| `R_DynamicStab` | `(structure) -> R⁺` | Sum of squared **soft-mode proxies**: spring-constant matrix from harmonic bond/angle model; min eigenvalue penalty `max(0, −λ_min)²` | Phonon DOS via finite-difference; `Σ_q max(0, −ω²(q))` | T1 / T3 | D0 |
| `R_BornStab` | `(C_ij elastic tensor) -> R⁺` | Cubic: `max(0, −(C₁₁−C₁₂))² + max(0, −(C₁₁+2C₁₂))² + max(0, −C₄₄)²`; analogous for hex/orth | C from DFT-DFPT or strain-stress fits | T0 (given C) / T3 (computing C) | D0 |
| `R_SymmetryConsistency` | `(coords, space_group) -> R⁺` | `Σ_g∈G ‖g·x − x‖²` averaged over generators g | Same; tolerance from spglib | T0 | D+ |
| `R_BondLengthSanity` | `(structure, covalent_radii) -> R⁺` | `Σ_ij max(0, (r_i+r_j)·0.7 − d_ij)² + max(0, d_ij − (r_i+r_j)·1.3)²` (overlap & dangling-bond penalty) | Same with refined radii from neutral-atom DFT | T0 | D+ |
| `R_CoordinationConsistency` | `(structure, expected_CN_table) -> R⁺` | `Σ_i (CN_i^actual − CN_i^expected)²`, CN via soft cutoff `Σ_j σ((r_cut − d_ij)/δ)` | Same with Voronoi tessellation | T0 / T1 | D+ / D0 |

### B.2 Worked example: diamond validity

For diamond (C, Fd-3m, a = 3.567 Å, 8 atoms/conventional cell):

- `R_ChargeBalance` = 0 (covalent, formal charges 0).
- `R_Pauling`: radius ratio inapplicable (single species). Reduces to coordination check: CN=4 for all → `R_CoordinationConsistency = 0`.
- `R_SymmetryConsistency`: Fd-3m generators are 48 ops; with frac_coords at (1/8, 1/8, 1/8) and (7/8, 7/8, 7/8) for the two-atom basis, residual is ~10⁻³⁰ (numerical floor).
- `R_BornStab` (cubic): with C₁₁=1080, C₁₂=125, C₄₄=576 GPa → all three conditions satisfied → R = 0.
- `R_DynamicStab` cheap form: harmonic spring constants from Tersoff parameters; no soft modes.
- `R_HullDistance`: diamond is metastable vs graphite by ~25 meV/atom at T=0 — this is the famous "diamond is not on the convex hull" gotcha. The residual must use a **temperature-and-pressure-aware hull**, not the T=0 hull. Cheap fix: add `ΔG = ΔE − T·ΔS_config − P·ΔV` term with tabulated S_config and ΔV.

The diamond gotcha generalizes: **for harsh-environment chips, the hull must be evaluated at operating conditions**, not standard. New residual:

| `R_HullDistance_TP` | `(c, T, P, μ_elements(T,P)) -> R⁺` | `max(0, ΔG_form(T,P) − ΔG_hull(T,P))²` | Quasi-harmonic free energy from MLIP-phonons | T1 / T2 | D0 |

### B.3 Why cheap dynamical-stability matters

Faithful phonons are T3 (DFPT or finite-difference, ~hours). The cheap proxy is the **second-derivative matrix of a harmonic bond-bend Hamiltonian**:

```
H_harm(u) = ½ Σ_ij k_r (|r_ij(u) − r⁰_ij|)² + ½ Σ_ijk k_θ (θ_ijk(u) − θ⁰_ijk)²
```

with `k_r`, `k_θ` from a tabulated bond-angle force field. The Hessian eigenvalues at u=0 give a 3N×3N stiffness; negative eigenvalues → soft modes. This is T1 (matrix diagonalization of a sparse 3N×3N) and `D+` because the Hessian is an analytic function of the structure. It gets the **sign** of stability right ~85% of the time on benchmark sets (vs full phonons), which is enough for label generation; full phonons stay in the faithful path.

---

## Part C — Heterostructure / Metal-Semiconductor Stack Prediction

### C.1 Standard pipeline

1. **Choose two phases** A (substrate / bulk) and B (overlayer).
2. **Surface enumeration** — for A, enumerate Miller indices {(hkl)} up to some max-index; for each, enumerate terminations (which atomic layer ends the slab).
3. **Lattice-matching search** — find (m, n) supercell pairs (m×m of A surface, n×n of B surface) such that strain `ε = (m·a_A − n·a_B) / (n·a_B)` is below threshold (typically 5%); allow rotations.
4. **Stacking enumeration** — for each (surface, supercell) pair, slide B over A on a 2D grid; relax.
5. **Score** — interface energy `γ_int = (E_slab − E_A^slab − E_B^slab) / A_int`.

### C.2 Heterostructure residual catalog

| Residual | Signature | Cheap | Faithful | Tier | Diff |
|---|---|---|---|---|---|
| `R_LatticeMatch` | `(a_A, a_B, m, n, θ) -> R⁺` | `((m·a_A·cos θ − n·a_B) / (n·a_B))²` averaged over 2D | Anisotropic with full strain tensor ε_αβ; Vegard correction | T0 | D+ |
| `R_StrainEnergy` | `(ε_αβ, C_ijkl) -> R⁺` | `½ V · C_ijkl · ε_ij · ε_kl` (linear elasticity) | DFT relax of strained cell | T0 / T3 | D+ |
| `R_WorkFunctionAlign` | `(Φ_metal, χ_semi, Δ_dipole) -> R⁺` | Schottky-Mott: `Φ_B = Φ_metal − χ_semi`; residual = deviation from target | Slab DFT with explicit dipole correction | T0 / T3 | D+ |
| `R_InterfaceEnergy` | `(E_AB, E_A, E_B, A) -> R⁺` | Bond-counting: `Σ_broken ε_bond / A` | DFT slab arithmetic | T1 / T3 | D+ |
| `R_ChargeTransferSC` | `(ρ_A, ρ_B, ρ_AB) -> R⁺` | `(Δρ_predicted − Δρ_PINO)²` with simple capacitor model `ΔQ = C·(Φ_A − Φ_B)` | Bader-charge differences from converged DFT | T0 / T3 | D+ |
| `R_TerminationChemPot` | `(termination, μ_elements) -> R⁺` | Grand-potential `Ω = E − Σ μ_i n_i`; residual = max(0, Ω − Ω_min)² | Same with DFT-converged μ | T1 / T3 | D+ |
| `R_ThermalMismatch` | `(α_A(T), α_B(T), T_growth, T_op) -> R⁺` | `((α_A − α_B)·ΔT)² × stiffness` — penalizes delamination risk | QHA-derived α(T) | T0 / T2 | D+ |
| `R_CarbideFormation` | `(metal, μ_C, T) -> R⁺ × {C-forms, C-doesn't}` | `max(0, −ΔG_carbide(T))² · indicator(metal ∈ carbide-formers)` | Full thermo on M-C phase diagram | T0 / T3 | D0 (indicator) |

### C.3 Diamond-metal interface knowledge cheat-sheet

This is the **harsh-environment chip** core question. Diamond χ is termination-dependent and must always be termination-tagged: ≈ −1.3 eV (H-terminated (100)/(111), NEA) through +0.4…+0.7 eV (clean / OH) to +1.7/+2.6 eV (O ether/ketone, PEA) — canonical per-termination table in `defects-surfaces-interfaces.md` Part E. Diamond bandgap ≈ 5.47 eV.

| Metal | Φ (eV) | Diamond contact behavior | Carbide? | T_stable | Use case |
|---|---|---|---|---|---|
| W | 4.55 | Schottky on undoped, near-Ohmic on heavily B-doped; W₂C/WC growth measurable from ~600–700°C (kinetics: defects file F.5 — ~3 nm per 1000 h at 500°C) | Yes (WC, W₂C) | Excellent to 1000°C | Gate metal, refractory contact |
| Mo | 4.60 | Similar to W; Mo₂C growth measurable from ~500–700°C (defects file F.5) | Yes | Good to 900°C | Refractory contact |
| Pt | 5.65 | High Schottky barrier (~1.4–1.7 eV reported on H-term — pin provenance at the metals wave; ~2.0 eV on O-term); **no carbide** | No | Excellent to 1100°C | Schottky diode, gate |
| Au | 5.10 | Schottky; **no carbide, no reactivity**; poor adhesion → Ti adhesion layer needed | No | Limited by adhesion; up to ~600°C | Probe pad, top metal |
| Ti | 4.33 | Forms TiC at ~400°C — Ohmic contact after anneal; standard "Ti/Pt/Au" stack | Yes (TiC) | TiC stable to 1500°C, but interdiffusion | **Ohmic contact** |
| Ni | 5.15 | Reacts above ~700°C; forms Ni-C eutectic-ish; used for diamond etching | Partial (Ni-C solution) | Poor for chips | Avoid as contact |
| Al | 4.28 | Reactive, low Schottky; Al₄C₃ at high T | Yes (Al₄C₃, hygroscopic!) | Bad above 400°C | Avoid for harsh env |
| Ta | 4.25 | Forms TaC, very refractory | Yes (TaC) | Excellent to 1200°C | Diffusion barrier |
| TiN | 4.5 (conductive ceramic) | Diffusion barrier; no further carbide | Self-passivating | Excellent | Barrier layer |
| WSi₂ | ~4.6 | Silicide contact; needs SiC interlayer typically | Indirect | Good to 800°C | Specialized |

Residual implication: the PINO must learn **carbide-formation indicator** as a learned feature. A new categorical residual fits:

`R_InterfaceReactivity : (metal, semi, T) -> R⁺ × {stable, reactive, eutectic}` — cheap form is a lookup-table embedding plus `max(0, T − T_reactive)²`; faithful form is grand-potential phase diagram of M-C-X system.

### C.4 Diamond-on-substrate (epitaxy)

| Substrate | Misfit (a_dia − a_sub)/a_sub | Defect density typical | Notes |
|---|---|---|---|
| Ir(100) | −7% | 10⁶–10⁷ cm⁻² (best heteroepitaxy) | Bias-enhanced nucleation; current SOTA for single-crystal heteroepi-diamond |
| Pt(111) | −9% | 10⁸ cm⁻² | Carbide-free; good template |
| 3C-SiC(100) | −18% (but C-template) | Polycrystalline → nanocrystalline | C atoms readily; large misfit |
| Si(100) | −34% (huge) | Polycrystalline only | Carbide buffer SiC forms; high TD density |
| Sapphire (Al₂O₃) | large (basal-plane registry-dependent) | Polycrystalline | Common substrate, MPCVD |

Residual: `R_HeteroEpiNucleation : (substrate, diamond_orientation, P_CH₄/H₂, T_growth) -> R⁺` — cheap form is `R_LatticeMatch · exp(−E_nuc(substrate)/kT)`; faithful form is wall-time first-principles nucleation barrier calculation (rarely done; usually empirical).

---

## Part D — Doping-Pattern Prediction

Dopant placement is the **L4 kinetics** problem in the BO hierarchy: which dopant configurations are accessible at growth conditions and stable at operating conditions.

### D.1 Doping residual catalog

| Residual | Signature | Cheap | Faithful | Tier | Diff |
|---|---|---|---|---|---|
| `R_DopantSitePref` | `(dopant, host, candidate_site) -> R⁺` | `(E_site − E_site_min) / kT` from tabulated site preferences | DFT supercell at each site | T0 / T3 | D+ |
| `R_SolubilityLimit` | `(dopant, host, μ_dopant, T) -> R⁺` | `max(0, [X] − [X]_eq(μ,T))² ` where `[X]_eq ∝ exp(−E_form/kT)` | DFT formation energy in dilute limit + Boltzmann | T0 / T3 | D+ |
| `R_SelfCompensation` | `(donor_conc, acceptor_conc, gap) -> R⁺` | `min(n_D, n_A)²` — counts forced pairs | Configurational with defect-defect binding from DFT | T0 / T3 | D+ |
| `R_Clustering` | `(dopant_positions, T, J_pair) -> R⁺` | Cluster-expansion: `Σ_ij J_ij · σ_i σ_j` against MC equilibrium distribution | DFT cluster expansion fit | T1 / T3 | D+ |
| `R_DopantChargeBalance` | `(n_D⁺, n_A⁻, n_e, n_h) -> R⁺` | `(n_D⁺ − n_A⁻ − n_e + n_h)²` | Same + SRH stats | T0 | D+ |
| `R_ActivationEnergy` | `(dopant_level_predicted, target_E_a) -> R⁺` | `(E_a^pred − E_a^target)²` against tabulated levels | DFT defect-level + image-charge correction | T0 / T3 | D+ |

### D.2 Worked example: boron-doped diamond (B:C)

B is the workhorse p-type dopant for diamond, substitutional on C site, E_a = 0.37 eV (acceptor level). Above ~5×10²⁰ cm⁻³ → metallic / superconducting; below → activated conductor.

Residuals:
- `R_DopantSitePref`: substitutional B vs interstitial B vs split-interstitial; cheap proxy via covalent-radius match (r_B ≈ r_C → substitutional wins by ~3 eV); R = 0 for substitutional.
- `R_SolubilityLimit`: ~10²¹ cm⁻³ during HPHT growth, lower for CVD; cheap form gives `[B]_eq = N_C · exp(−E_f/kT)` with E_f ≈ 0.4 eV at C-rich conditions.
- `R_SelfCompensation`: B-H complexes (H always present in CVD); passivate B. New residual `R_HydrogenPassivation` may be warranted as a sub-residual.
- `R_ActivationEnergy`: target 0.37 eV; PINO-predicted level must hit this within ~30 meV.

N-type doping of diamond is unsolved at production scale. Candidates: P (E_a = 0.6 eV, hard to incorporate substitutionally), N (deep donor 1.7 eV, useless for conduction), Li (interstitial, unstable). The residual library needs to **express the failure**, not hide it. `R_SolubilityLimit` for P in diamond is huge (P:C unfavorable by ~10 eV/atom under standard conditions) — the residual catches this.

---

## Part E — Defect-Pattern Prediction (Harsh-Environment Durability)

Operating temperature in a jet turbine: 500–1000°C. Native defect populations and ordering at these T are first-order property determinants.

### E.1 Defect residual catalog

| Residual | Signature | Cheap | Faithful | Tier | Diff |
|---|---|---|---|---|---|
| `R_NativeDefectPop(T)` | `(host, T, μ) -> R⁺` per defect type | `[V]_eq = N · exp(−E_f^V/kT)`; residual = `(log[V]_predicted − log[V]_eq)²` | DFT defect formation energies with finite-T corrections | T0 / T3 | D+ |
| `R_DefectClustering` | `(defect_positions, J_pair, T) -> R⁺` | MC under cluster-expansion; KL divergence from equilibrium | DFT-fit cluster expansion + KMC | T1 / T3 | D+ |
| `R_VacancyOrdering` | `(V_pattern, ordering_potential) -> R⁺` | Ising-like on sublattice: `Σ J·σ_i σ_j` against target ordering | DFT supercell sweep | T1 / T3 | D+ |
| `R_AntisiteOrder` | `(A_on_B, B_on_A, μ, T) -> R⁺` | `Σ exp(−E_swap/kT)` vs predicted populations | DFT + special quasirandom structures (SQS) | T1 / T3 | D+ |
| `R_StackingFault` | `(γ_SF, stacking_seq) -> R⁺` | γ-surface from harmonic model; residual = `Σ γ_SF · area_SF` | DFT generalized stacking fault energy surface | T1 / T3 | D+ |
| `R_TwinBoundary` | `(Σ-value, γ_TB) -> R⁺` | Tabulated γ_TB for common Σ (Σ3 in diamond ≈ tens of mJ/m², effectively 0 — explains CVD twins) | DFT slab | T0 / T3 | D+ |
| `R_ThermalCycleStability` | `(defect_state₀, defect_state_after_cycles, ΔT) -> R⁺` | Defect-population drift `‖Δn_d‖²` under KMC | KMC with DFT migration barriers | T1 / T3 | D+ |
| `R_NV-center-conc` (diamond-specific) | `(N_conc, V_conc, T_anneal) -> R⁺` | Mass-action: `[NV] ∝ [N]·[V]·exp(−E_b/kT)` | DFT defect-complex binding energy | T0 / T3 | D+ |

### E.2 Diamond-specific defect notes

- **Vacancy V**: E_f ≈ 7 eV in pristine diamond → [V] at 1000°C ≈ 10⁻²⁵ atomic fraction, basically zero. But irradiation creates them.
- **Divacancy V₂**: binding ~4 eV; relevant for radiation damage.
- **NV center**: substitutional N + adjacent V; binding ~3 eV; concentration set by mass action.
- **Σ3 twin boundary**: γ_TB ≈ tens of mJ/m² (coherent twin — essentially free relative to other GBs) — explains the dense twinning in CVD polycrystalline diamond. Residual must allow near-zero penalty.
- **Stacking faults (intrinsic)**: γ_ISF ≈ 280 mJ/m² in diamond — modest, so SFs are common in heteroepitaxial growth.

Harsh-environment residual: `R_ThermalCycleStability` is the **durability** residual. At jet-turbine duty cycle (cold start to 1000°C, repeated), defect populations equilibrate to T_op but **freeze** during cooldown. The residual must distinguish equilibrium populations (from `R_NativeDefectPop(T_op)`) from frozen-in populations after cycling.

---

## Part F — Bridge to `/physics` Architecture

### F.1 Reuse map: existing → new

The state `x(t) = (h, R_I, P_I, Π_h, Z_I, γ̂, A)` already carries enough handles. Mapping:

| New residual class | Uses existing state component | Reuses which method/template |
|---|---|---|
| Validity residuals (Part B) | `R_I` (positions), `A` (lattice via gauge field if encoded as cell vectors), `h` (composition labels via species channels) | L2 BO surface evaluator; symmetry-projection template; formation-energy formula |
| Heterostructure residuals (Part C) | Two-region partitioning of `R_I` into substrate / overlayer; `γ̂` for electronic alignment | L1 electronic evaluator (for Φ, χ); L2 BO surface (for γ_int); strain template needs to be added |
| Doping residuals (Part D) | `R_I` with species-channel mutation; `γ̂` for activation energies; `Z_I` for charge balance | L3 stats (chemical-potential equilibration); L4 kinetics (solubility-limit via Boltzmann) |
| Defect residuals (Part E) | `R_I` with vacancy/interstitial labels; `Π_h` for thermal driving | L4 kinetics (population evolution under thermal cycling) directly maps here |

### F.2 New methods / templates / formulas needed

**New methods (architecture-level):**
1. `structure-validity-method` — closes the loop "is this a candidate even allowed?" before any energy evaluation. Bundles B residuals.
2. `interface-stacking-method` — bi-material slab generator + lattice-matcher. Bundles C residuals.
3. `defect-population-method` — equilibrium and KMC defect populations at finite T. Bundles D + E.

**New templates:**
1. `harmonic-stiffness-hessian-template` — cheap dynamical-stability proxy. Reusable for any structure.
2. `bi-slab-grand-potential-template` — termination scoring under μ. Reusable across all heterointerfaces.
3. `mass-action-equilibrium-template` — closed-form solver for defect/dopant complex populations given binding energies.
4. `cluster-expansion-template` — generic discrete Ising/Potts on lattice for clustering and ordering residuals.

**New formulas (named):**
- `bond-valence-sum`, `Pauling-radius-ratio`, `Hume-Rothery-mismatch`, `Born-stability-cubic`, `Born-stability-hexagonal`, `Born-stability-orthorhombic`, `lattice-strain-energy`, `Schottky-Mott-alignment`, `interface-bond-counting`, `Vegard-correction`, `defect-Boltzmann-population`, `cluster-expansion-energy`, `generalized-stacking-fault`, `twin-boundary-energy`, `mass-action-complex`.

That brings the count from 24 → roughly 39 named formulas. Plausible scope.

### F.3 New observable bundles

The existing observable bundles likely cover scalars, vector fields, etc. New bundles needed:

1. **`structural-validity`** — vector of validity residuals per candidate; output of `structure-validity-method`. Used as the gating filter for any CSP backend.
2. **`band-alignment`** — at interfaces, (Φ_metal, χ_semi, Φ_B^n, Φ_B^p, dipole) tuple per interface. Used for Schottky/Ohmic prediction.
3. **`defect-population-spectrum`** — concentration per defect type as a function of (T, μ), with covariance for clustered species. Used for durability scoring.
4. **`interface-stack`** — paired-region observables (substrate region quantities, overlayer region quantities, interface-localized quantities). The PINO needs to predict these jointly with shared latent.

### F.4 New residual category

The current 5 categories (EOM-violation, degeneracy, conservation, positivity, algebraic-identities) are dynamical-physics residuals — they constrain trajectories of x(t). They don't naturally express **discrete-structure validity** ("does this candidate satisfy Hume-Rothery?") or **equilibrium-population consistency** ("does [V] = exp(-E_f/kT)?").

Proposed two new categories:

6. **`structural-validity`** — Pauling, Hume-Rothery, charge balance, stoichiometry, symmetry consistency, bond-length sanity, coordination consistency, Born stability, cheap-phonon stability. All are **algebraic constraints on the static structure** rather than on dynamics. They are mostly `D+`, cheap, and fit the PINO loss directly.

7. **`thermodynamic-consistency`** — hull-distance (T,P), formation-energy, solubility limits, mass-action defect populations, interface grand-potential terminations, carbide-formation indicators. These are **equilibrium statements** at given (T, μ, P); cheap form uses tabulated reference energies, faithful form recomputes the relevant phase-diagram facets.

This brings the category count from 5 → 7.

### F.5 Two-tier path summary

- **Inner-compute (cheap) path** for residual library: every T0/T1 entry above. Total cost per candidate: ~1–10 ms wall-clock CPU, all `D+` or `D0`. Yields ~50 scalar residuals per candidate structure. Use as **physics-loss term** every PINO training step.
- **Faithful path**: T3/T4 entries; run **selectively** on uncertainty-weighted samples (active learning loop). Yields ground-truth residuals for the small validation set used to anchor the cheap path. Feeds back as correction-target for the cheap residuals (e.g., learned multiplier on `R_HullDistance_cheap` that pulls it toward the DFT value).

### F.6 Concrete integration sketch (diamond-W contact, end-to-end)

Pipeline that the augmented `/physics` would support for a single candidate diamond/W heterostructure at T_op = 800°C:

1. **Structural validity** (`structural-validity` bundle, 12 scalars): `R_Pauling=0, R_ChargeBalance=0, R_SymmetryConsistency=0, R_BondLengthSanity=0, R_BornStab_diamond=0, R_BornStab_W=0, ...` — all `T0`, ~100 µs total.
2. **Interface stack** (`interface-stack` bundle): `R_LatticeMatch(diamond(100)·4×4 vs W(110)·3×5) = 0.018, R_StrainEnergy = 0.45 eV/interface-cell, R_InterfaceEnergy_cheap = 3.2 J/m²` — `T1`, ~10 ms.
3. **Band alignment** (`band-alignment` bundle): `Φ_B^n = Φ_W − χ_diamond = 4.55 − 0.7 = 3.85 eV` (Schottky-Mott cheap path); PINO refines.
4. **Thermodynamic consistency** (`thermodynamic-consistency` bundle): `R_CarbideFormation(W, μ_C, 1073K) = max(0, −ΔG_WC(1073)) = 0` (WC forms, indicator triggers) → flag carbide interlayer needed; `R_HullDistance_TP(WC, 1073, 1 atm) = 0`.
5. **Defect population** (`defect-population-spectrum`): native vacancy in diamond at 1073 K ≈ 10⁻³⁰ (zero); W vacancies present; interface dislocations from `R_LatticeMatch · t_overlayer` estimate.
6. **Durability score**: `R_ThermalCycleStability` under 1000 cycles 300K↔1073K — KMC cheap form gives population drift; faithful path optional.

Total cheap-path cost: ~50 ms. This is the inner-compute residual vector consumed by the PINO loss. The PINO can then **invert** the problem: given target (Φ_B, durability, etc.), generate candidate (composition, orientation, termination) that minimizes residual sum + matches property targets.

---

## Cross-cutting observations

1. **Symmetry as a first-class citizen.** Every residual that touches `R_I` should respect the space-group action; otherwise it leaks gauge dependence into the loss. The `gauge field A` in the state already provides the apparatus; the new templates should plug into it.

2. **Discrete-continuous boundary.** Validity residuals over space-group choice (D-) need surrogate softening — common trick is Gumbel-softmax over space-group probabilities, with the residual evaluated as expectation. This keeps the PINO end-to-end differentiable.

3. **Reference-phase database is a dependency.** Cheap hull-distance, formation-energy, and chemical-potential residuals all require tabulated reference phases (elemental + competing binaries/ternaries). The architecture needs a **`reference-phase-cache`** primitive — not a residual itself but a substrate that the formulas read from. For diamond-centric scope, the cache needs ~50 phases (C, W, Mo, Pt, Au, Ti, Ni, Al, Ta, plus binaries WC, Mo₂C, TiC, TaC, Al₄C₃, plus oxides/nitrides for dielectrics).

4. **Interface terminations explode combinatorially.** For diamond(111)/W(110) alone, terminations × stacking offsets × rotational alignments ≈ 10²–10³ candidates. The PINO is the natural amortizer: train it to **rank** terminations cheaply, run faithful DFT only on top-K.

5. **The two-tier discipline maps cleanly onto cost tiers.** Cheap path = T0+T1, faithful = T3+T4, T2 (MLIP) sits in between and is the natural **bridge** for active learning. Recommend adding T2 (MLIP single-point) as a third tier for the residuals that benefit most: `R_FormationEnergy`, `R_DynamicStab`, `R_InterfaceEnergy`. MACE-MP-0 or similar foundation MLIPs cover most of the diamond + UWBG + transition-metal chemistry in scope, out of the box.

6. **What this stream did NOT cover** (flagging for other streams / Phase 2):
   - Quantum-tunneling residuals at metal-semiconductor barriers (likely the defects/interfaces or electronic-transport area).
   - High-frequency / RF response residuals (likely transport stream).
   - Radiation-damage cascade modeling (mentioned briefly in E; deserves its own deep dive).
   - Surface-chemistry residuals during CVD growth (μ_H, μ_CH₄ dependent — relevant for n-type doping investigation).

---

**Summary recommendation to the conductor.** The minimum viable expansion of `/physics` for UWBG-chip CSP support is: **+3 methods, +4 templates, +15 named formulas, +4 observable bundles, +2 residual categories**, plus a `reference-phase-cache` primitive. All net additions preserve the GENERIC dx/dt structure (validity/thermo residuals are static constraints on the state x, not modifications to L or M). Cheap-compute paths for all proposed residuals stay in T0/T1 and are end-to-end differentiable, suitable for direct inclusion in the PINO physics loss. Diamond-metal interface chemistry (Part C.3 table) is the most domain-specific content and should be encoded as a learned-feature table inside the PINO with `R_InterfaceReactivity` as the supervising residual.

---

## Changelog

- **2026-07-16 (strata rewrite):** status banner converted to this changelog; the header note
  retains only the still-load-bearing conventions (misfit denominator, termination-tagged χ,
  survey-grade contact values). No value changes.
- **2026-07-07 (gap-audit B8):** corrections applied in place, per
  `docs/audits/2026-07-07-gap-audit.md` B8 — misfit denominators normalized to `/a_sub`
  (diamond-on-Si read 52% under the old `/a_film` denominator, now −34% under `/a_sub`);
  Pt/H-diamond φ_B and the W/Mo carbide onsets harmonized to ranges consistent with
  `defects-surfaces-interfaces.md` F.4/F.5; Σ3 twin-boundary γ_TB corrected from "≈0" to
  "tens of mJ/m², effectively 0".
