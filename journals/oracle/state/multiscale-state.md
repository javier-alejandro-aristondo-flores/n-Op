---
id: multiscale-state
title: "Multiscale state — the slow and macro tiers"
owns:
  - three-tier state stratification
  - the refined emergence axiom
  - defect-species universe
  - slow configurational state schema
  - slow-kinetic formula set
  - adiabatic driving contract
  - device-mesh universe
  - macro continuum-field state schema
  - moment closures for electron temperature and current density
  - the micro-to-macro homogenisation map
  - the defect-population and continuum residual categories
  - the unified three-tier residual contract
anchors:
  emergence-axiom: "The refined emergence axiom"
  three-tiers: "The three tiers"
  defect-species: "The defect-species universe"
  slow-state-schema: "The slow-state schema"
  slow-kinetics: "Slow-kinetic formulas"
  eom-defect-population: "The defect-population residual"
  adiabatic-driving: "The adiabatic driving contract"
  device-mesh: "The device mesh"
  macro-state-schema: "The macro field set"
  moment-closures: "Moment closures"
  homogenisation-map: "The homogenisation map"
  eom-continuum: "The continuum residual"
  residual-contract: "The unified three-tier residual contract"
depends-on:
  - unified-state
  - crystal-inputs
  - born-oppenheimer-levels
  - generic-dynamics
  - representation-substrate
  - canonical-vocabularies
  - computational-methods
  - property-templates
  - residual-definitions
  - pino-bridge
  - compose-time-pipeline
  - coupling-structure
  - formula-registry
  - out-of-scope
open-questions:
  - id: mesh-adjoint-scheme
    anchor: device-mesh
    summary: "Discrete- versus continuous-adjoint of the finite-volume operator, for differentiating the continuum residual. The mesh format is committed; the adjoint binding is not, and it inherits the compile-time-to-runtime automatic-differentiation seam."
  - id: hole-transport-anchors
    anchor: moment-closures
    summary: "Hole mobility, hole impact-ionisation coefficient and hole saturation velocity are anchored for few hosts. The hole schema is committed; the coefficients are a per-composition data gap, and every bipolar macro composition is unanchored until it closes."
  - id: niel-displacement-coefficients
    anchor: slow-kinetics
    summary: "The recombination efficiency as a function of lattice temperature, and the NIEL-derived displacement cross-section per host, particle type and energy. No closed form exists in the corpus — only the coupling structure and a curated provenance-ledger slot. Frenkel-pair yield cannot be evaluated without them. A data-acquisition task, not an invention task."
  - id: regime-threshold-windows
    anchor: moment-closures
    summary: "The per-host field windows that switch the transport regime are order-of-magnitude only. They gate the per-sample applicability mask, so their width is load-bearing."
  - id: displacement-threshold-provenance
    anchor: slow-kinetics
    summary: "The per-host displacement thresholds feeding the NRT displacement count have no provenance outside the derivation chapter. The β-Ga₂O₃ value is UNSEEDED; diamond, GaN and AlN carry numbers whose only source is that chapter."
---
# Multiscale state — the slow and macro tiers

## The refined emergence axiom

A quantity `y` is **emergent** from a tier — excluded from that tier's state — **iff** it is
recoverable from that tier's state by coarse-graining **on the same timescale and the same
scale**.

Phonon occupations `n_{q,s}`, the carrier distribution `f_n(k,r)`, and the electron and lattice
temperatures are emergent at the micro timescale: they fast-equilibrate to a function of the
micro seven-tuple ([unified-state#slots]) within the micro relaxation time.

Two classes of quantity are **not** so recoverable, and are therefore first-class state in a
tier of their own:

- **Slow / history-dependent** — a different *timescale*. Defect-population concentrations,
  charge-state distributions, hydrogen content, oxidation and carbide fronts. At the micro
  timescale these are *frozen*: they evolve over hours to years, set by Arrhenius barriers of
  2–7 eV, and they carry the integrated thermal and irradiation history. A frozen-in population
  is distinguishable from an equilibrium one only if the frozen-in one is stored.
- **Homogenised / device-scale** — a different *scale*. The continuum fields `T_L(r)`, `φ(r)`,
  `n(r)`, `p(r)`, `j(r)` on a device mesh, which are not derivable from a single unit cell.

Because the added tiers are independent **by timescale or by scale**, they create **no algebraic
constraint** with the micro seven-tuple. They evolve on their own clean flow and couple only
parametrically — by adiabatic driving or by homogenisation. The constraint-manifold pathology
that [unified-state#emergence] guards against arises only for quantities redundant on the *same*
timescale and scale, and those stay emergent: the full distribution is never promoted.

## The three tiers

| Tier | Members | Equilibration timescale and scale | Index geometry | Dynamics |
|---|---|---|---|---|
| **Micro** | the seven-tuple ([unified-state#slots]) | fs–ns, unit cell | continuous Brillouin zone × cell | full reversible-plus-dissipative brackets |
| **Slow / configurational** | defect concentrations and charge distributions, hydrogen content, oxide front, carbide thickness, dislocation density | hours–years, unit cell to mesh | discrete species × sites | ordinary differential / master equation |
| **Macro / continuum** | `T_L(r)`, `φ(r)`, `n(r)`, `p(r)`, `j(r)` on a device mesh | device scale | fields on real-space cells | parabolic and constraint partial differential equations |

The slow and macro tiers are **adiabatic parameters** of the micro tier. The micro seven-tuple
fast-equilibrates at fixed slow and macro state under the environment record
([crystal-inputs#environment]); the slow and macro state then drift under *time-averaged* micro
quantities or under *homogenised coefficients* that the micro tier supplies.

In the level hierarchy ([born-oppenheimer-levels#hierarchy]) the slow tier is a configurational
layer above `non-equilibrium-kinetics`, and the macro tier is that level's spatial fluid-limit
reduction — the drift-diffusion and Poisson system as the Boltzmann-transport fluid limit —
lifted from one cell to a device mesh. That is the irreducible state
[born-oppenheimer-levels#kinetics-irreducible-state] attributes to the kinetics level.

The oracle **scores** each tier's law violation; the operator supplies each tier's trajectory
([pino-bridge#validate]). Score-not-solve is preserved at every scale, and **no new computational method
is introduced**: the slow tier reuses `kinetic-evolution` ([computational-methods#the-alphabet]), the macro
tier reuses the coupled electromagnetic-thermal residual pattern of registry row 71.

## The defect-species universe

`DefectSpecies` is a closed `Universe[T]` in the substrate's **vocabularies** cluster
([representation-substrate#clusters]), with `carrier_kind = Closed` and `ordinal_policy = DenseU32`. Its
enumerator is the per-host native defect inventory:

| Host | `DefectSpecies` members | Charge states |
|---|---|---|
| Diamond | `V_C` (GR1), `C_i` (split-⟨100⟩), `V2`, `N_s`, `NV`, `NVN` (H3), `N3V`, `N2A`, `platelet` | `V_C` in `{+, 0, −}`; `NV` in `{+, 0, −}` |
| Cubic BN | `V_B`, `V_N`, `B_i`, `N_i`, `B_N`, `N_B`, `V_B–O` | `V_N` donor-like |
| AlN | `V_Al`, `V_N`, `O_N`, `Al_i`, `V_Al–O`, `V_Al–nC_N` | `V_Al` in `{0, −, 2−, 3−}`; `V_N` in `{0, +}` |
| GaN | `V_Ga`, `V_N`, `N_i`, `Ga_i`, `V_Ga–O_N`, `V_Ga–nH` | `V_Ga` in `{0, −, 2−, 3−}`; `V_N` in `{0, +}` |
| β-Ga₂O₃ | `V_O(I/II/III)`, `V_Ga(1/2)`, `Ga_i`, `V_Ga–Ga_i–V_Ga`, `V_O–H`, `V_Ga–nH` | `V_O` deep |

The element type carries the record `{name, site : LatticeSite, charge_states : List[Int],
spin}`. Adding a member is a versioned `schema_version` bump
([representation-substrate#versioning]), exactly as for the theory-context vocabularies
([canonical-vocabularies#versioning]).

## The slow-state schema

The slow state `s` is a typed fiber in the substrate's **sidecars** cluster —
`PersistentMap[TypedKey, V]`, hash-array-mapped trie with branching 32, stage-visible
([representation-substrate#clusters]) — and is **not** part of `ResidualKey` identity:

| Field | Type and unit | Index |
|---|---|---|
| `conc[D,q]` | `Concentration` (cm⁻³), non-negative | `DefectSpecies × ChargeState` |
| `charge_dist[D]` | `Simplex` over charge states, summing to 1 | `DefectSpecies → Simplex` |
| `H_content` | `Concentration` (cm⁻³), non-negative | scalar per region |
| `oxide_front` | `Length` (nm), non-negative | scalar per facet |
| `carbide_thickness` | `Length` (nm), non-negative | `MetalContact` |
| `dislocation_density` | `Length⁻²` (cm⁻²), non-negative | scalar per region |

`ChargeState` reuses the `SubDofTag = charge` already admitted on the species labels
([coupling-structure#channel-record]); `charge_dist[D]` is its dynamic refinement.

**The slow fiber is the dynamic promotion of `SiteDecoration.occupancy`
([crystal-inputs#site-decoration]), not a mutation of the species labels.** Three things follow,
and they are the reason the promotion is safe:

1. The species labels stay immutable ([unified-state#slots]) — atomic-number identity does not
   change as a vacancy forms.
2. Occupancy is the right physical quantity: a vacancy is occupancy going to zero. The static
   `SiteDecoration.occupancy` becomes the **initial condition** `s(t=0)` — the as-synthesised or
   frozen-in population.
3. As a separate adiabatic-parameter fiber on a different timescale, it ties **no** constraint
   manifold back to the micro tier. That is the condition the emergence axiom protects, met
   directly rather than by exclusion.

The slow fiber drives the **degradation** bundle's residuals, with defect-resolved sub-outputs in
the **defect-resolved** bundle.

## Slow-kinetic formulas

Nine registered formulas advance the slow state. All Arrhenius rates use
`rate = ν₀·exp(−E_a/kT)`. Each names the **instantiation form** of the `kinetic-evolution`
method it uses — master-equation, drift-diffusion, Allen–Cahn. Those are solver shapes of the
one method, **not** registered sub-methods: the closed alphabet's three registered sub-methods
are unchanged ([computational-methods#sub-methods]), and no new method or sub-method is introduced here.
Row content is read from the registry manifest, which is its sole source ([formula-registry#manifest]).

Each entry below carries its **evaluation cost**, its **differentiability**, its instantiation
form, and its bundles. The harsh-environment fields these formulas read are fields of the
environment record ([crystal-inputs#environment]).

- **`vacancy-generation-arrhenius`** (row 105) — `(c_V^q, T, μ, j, x_ox', ρ_dis, k_ann) →
  dc_V/dt` in cm⁻³s⁻¹.
  `dc_V/dt = G_total − c_V·k_ann`, with `G_total = G_thermal + G_irradiation + G_interface`;
  `G_thermal = ν₀·exp(−E_form^V/kT)·N_site`;
  `G_interface = ξ_int·(dx_ox/dt + dx_carbide/dt)·N_site,int`;
  `G_irradiation` supplied by `frenkel-pair-yield`; `k_ann = ν₀·exp(−E_migr^V/kT)`.
  For diamond `V_C`, `E_form ≈ 7.2 eV` (HSE06), so `G_thermal(773 K)` is negligible — **the
  500 °C generation budget is dominated by `G_interface` and `G_irradiation`.** Annihilation
  barriers: `V_C^0` 2.3 eV, `V_C^−` 2.8 eV, `C_i` 1.6–1.7 eV, `V_N` in GaN 2.6 eV, `V_Ga` in GaN
  1.9 eV, `V_O` in β-Ga₂O₃ 1.9–2.4 eV, `V_Al` in AlN 3.4 eV.
  microseconds · direct · master-equation · degradation, defect-resolved.

- **`hydrogen-redistribution-drift-diffusion`** (row 106) — `(c_H(r), T, E, μ_drift) →
  ∂c_H/∂t`.
  `∂c/∂t = ∇·(D(T)∇c) − ∇·(μ_drift·c·E)`, `D(T) = D₀·exp(−E_diff/kT)`. For interstitial
  hydrogen in diamond `E_diff = 1.7 eV` and `D(500 °C) ≈ 1e−13 cm²/s`, giving a redistribution
  range `√(Dt) ≈ 6 µm` in 1000 h — a near-surface phenomenon, not a device-scale one.
  minutes · adjoint · drift-diffusion · degradation, surface-resolved.
  The differentiability is `adjoint` and not `fixpoint-adjoint`: the output is a rate field from
  a transport operator, not a converged fixed point, so its adjoint is a backward-in-time
  vector-Jacobian product whose cost scales with the step count.

- **`platelet-nucleation-allen-cahn`** (row 107) — `(c_platelet, c_Ns, T) → dc_platelet/dt`.
  `k_nuc·c_Ns² − k_dis·c_platelet`, `k_nuc = ν₀·exp(−E_nuc/kT)`, `E_nuc ≈ 3.5 eV`. The
  substitutional-nitrogen-to-A-centre half-life is years at 500 °C and hours at 1000 °C.
  milliseconds · adjoint · Allen–Cahn · degradation, defect-resolved.

- **`vibration-induced-vacancy-generation`** (row 108) — `(ρ_dis, σ_stress, f_vib, v_dis, b) →
  (dρ_dis/dt, G_V)`.
  `dρ_dis/dt = κ_vib·(σ_stress/σ_yield)^m·f_vib` with `m ≈ 4–6`; `G_V = ξ·ρ_dis·v_dis·b`.
  milliseconds · direct · master-equation · degradation. `G_V` feeds the vacancy-generation
  source term.

- **`carbide-growth-parabolic`** (row 81) — `x_carbide = √(2·k_carb(T)·t)`,
  `k_carb = k₀·exp(−E_carb/kT)`, with the master-equation front advance `dx/dt = k_carb/x`. Its
  output `x_carbide` is a slow-state field. Barriers by contact metal: Ti 1.4 eV (≈600 nm per
  1000 h at 500 °C, severe), Mo 2.1 eV (≈15 nm), W 2.4 eV (≈3 nm), Pt none.
  microseconds · direct · master-equation · degradation, interface-resolved.

- **`air-oxidation-rate-eyring`** (row 109) — `(T, p_O2, ΔG‡, ν) → dx_ox/dt`.
  `r_ox = ν·exp(−ΔG‡/kT)` in Eyring form; the cheap tier is Arrhenius. Diamond onset is above
  600 °C and is **the lifetime limiter**; accuracy factor ≈3. The reaction-rate template this
  formula needs is supplied by `kinetic-evolution`.
  microseconds · direct · master-equation · degradation, surface-resolved.

- **`hydrogen-desorption-rate-eyring`** (row 110) — `(T, E_des, ν) → r_H`.
  `r_H = ν·exp(−E_des/kT)`, `E_des ≈ 3.8 eV` for the hydrogen-carbon bond. Drives the
  irreversible electron-affinity shift from negative to positive; desorbs at 700–900 °C;
  accuracy factor ≈2.
  microseconds · direct · master-equation · degradation, surface-resolved.

- **`nrt-displacements`** (row 111) — `(T_dam, E_d) → N_d`, `N_d = 0.8·T_dam/(2·E_d)`.
  microseconds · direct · algebraic-combination (the method, not the template) · degradation,
  defect-resolved. Feeds `frenkel-pair-yield`. Per-host displacement thresholds:

  | Host | Displacement threshold `E_d` |
  |---|---|
  | Diamond | ~37–50 eV |
  | GaN | ~20 eV |
  | AlN | ~35 eV |
  | β-Ga₂O₃ | `UNSEEDED` |

- **`frenkel-pair-yield`** (row 112) — `(N_d, Σ_d, Φ_dose, η_recomb) → DefectDensity`.
  `c_V,irr = Φ_dose·Σ_d·N_d·(1 − η_recomb)` in cm⁻³, where the **macroscopic displacement
  cross-section** `Σ_d = N_atom·σ_d` in cm⁻¹ supplies the missing inverse length: the product of
  `N_d` (displacements per primary knock-on atom, dimensionless), `Σ_d` (cm⁻¹) and the fluence
  `Φ_dose` (cm⁻²) is a concentration. Without `Σ_d` the bare `N_d·(1 − η_recomb)·Φ_dose` is a
  fluence, not a density. `σ_d` is the per-host, per-particle-type, per-energy NIEL-derived
  displacement cross-section — one curated provenance-ledger coefficient
  ([coupling-structure#provenance-contract]).
  microseconds · direct · master-equation · degradation, defect-resolved. This is the
  `G_irradiation` term of `vacancy-generation-arrhenius`.

Full cascade dynamics is out of scope. The recombination efficiency `η_recomb(T_L)` and the
displacement cross-section `σ_d` have **no closed form in the corpus**: only the coupling
structure and the curated-coefficient slot are specified.

## The defect-population residual

The slow tier earns an equation-of-motion violation category, `EOM/DefectPopulation` — the
slow-tier sibling of the seven micro categories ([residual-definitions#eom-categories]):

```
EOM/DefectPopulation[D,q,site] = ‖ dc_D^q/dt|_predicted − ( G^q_total[D] − c_D^q·k_ann^q[D] ) ‖²
```

This is the slow-tier specialisation of `‖dx_i/dt − (L·δE/δx_i + M·δS/δx_i)‖²`. Generation and
annihilation are both branches of the single dissipative master-equation generator: `M` is the
rate matrix, from the chemical and surface extraction of [generic-dynamics#operators]. The slow tier has
no reversible bracket.

Each slow field substitutes its own right-hand side from the formula set above — hydrogen
content takes the hydrogen redistribution rate, the oxide front takes the air-oxidation rate,
carbide thickness takes the parabolic growth rate, dislocation density takes the
vibration-induced generation rate.

**Axes** are `(DefectSpecies, ChargeState, SiteClass)`, plus a spatial bin for the field-valued
hydrogen content and oxide front. There is one weightable `ResidualLeaf` per species, charge and
site ([residual-definitions#granularity]) and **no preaggregation**. `ResidualKey` is
`(Method(kinetic-evolution), axes)`; the facets are the defect-population category, the
degradation bundle, and `bare`.

The operator predicts the aging trajectory; the oracle scores the finite-difference slow-state
rate against the formula right-hand side at each step, so a consistent aging curve drives the
residual toward zero. Curriculum band: **Refine**, `[0.10, 0.60)`, with the other
equation-of-motion residuals.

## The adiabatic driving contract

Each slow rate is parameterised by **time-averaged** micro quantities:

| Slow rate | Driven by the time-averaged micro quantity |
|---|---|
| `G_irradiation` | carrier and ion flux |
| every Arrhenius rate | lattice temperature, in each `exp(−E_a/kT)`; self-heating comes from the micro tier |
| `G_interface` | oxidation and carbide front velocities |
| `G_V` feeding vacancy generation | dislocation density and dislocation velocity |
| hydrogen drift | internal electric field |

```
ds/dt = Φ_kinetic( s ; ⟨T_L⟩_τ, ⟨j⟩_τ, ⟨E⟩_τ, ⟨ρ_dis⟩_τ, dx_ox/dt, dx_carbide/dt ; Environment )
```

The reverse coupling — slow to micro — is the adiabatic-parameter dependence. The micro
charge-state formation energy at the current Fermi level, the trap density `N_T` taken from the
defect concentrations, the electron affinity, and the gap and mobility all read the *current*
slow state as a fixed parameter. That is the `SelfConsistentChargeBalanceOf` closure
([property-templates#what-each-produces]) consuming the slow defect list, with Shockley–Read–Hall lifetime
`τ_n = 1/(σ_n·v_th·N_T)`.

The coupling is bidirectional and the two directions have different owners: the homogenisation
map reads slow defect density into the macro recombination term (macro from slow), while the
back-reaction — carrier-driven defect generation, the irradiation source term — is macro into
slow. The rate law in both directions is the slow tier's.

## The device mesh

`DeviceMesh : Universe[MeshCell]` is a closed universe over real-space cells in the substrate's
**sparse-masks** cluster ([representation-substrate#clusters]), with `carrier_kind = Closed`,
`ordinal_policy = DenseU32`, `enumerator = enumerate(product(mesh-axes))` ([pino-bridge#axis-coverage]) and
`backend_policy` of Roaring bitmap or bitset. Each `MeshCell` carries a centroid `r_c`, a volume
`V_c`, and a face list. Macro fields are fibers over it — `PersistentMap[MeshCell, FieldValue]`
in the sidecars cluster — so snapshots differing in one subdomain share unchanged cells by
address, and a Merkle-directed-acyclic-graph diff costs the changed frontier only.

Mesh generation and refinement are committed as **structured-tensor** for version 1, the
`enumerate(product(axes))` form above. Adaptive hot-spot refinement defers to version 2.

**Discretisation is finite-volume.** Each balance equation is read in integral conservation form

```
∂_t ∫_c φ dV + Σ_f Flux_f·A_f = ∫_c Source dV
```

with face fluxes built from the homogenised coefficients. The mesh is **conservative** — the
face flux out of a cell is the flux into its neighbour — so the `Conservation` residual
([residual-definitions#constraint-categories]) holds discretely.

## The macro field set

```
MacroState = ( T_L : Field[DeviceMesh → ℝ₊]   [K],
               φ   : Field[DeviceMesh → ℝ]    [V],
               n,p : Field[DeviceMesh → ℝ₊]   [m⁻³],
               j   : Field[DeviceMesh → ℝ³]   [A·m⁻²] )
```

Each field is carried for a stated reason, and the reason is what keeps the set closed:

- `T_L(r)` is the spatial coarse-graining of the micro vibrational entropy per-cell value onto
  the device profile.
- `φ(r)` is **Poisson-constrained**, `∇·(ε∇φ) = −ρ`, and is carried so that the constraint is
  *scored* rather than satisfied for free.
- `n(r)` and `p(r)` are the **zeroth moments** of the carrier distribution over a device cell —
  densities, not the distribution.
- `j(r)` comes from a **closed-form first-moment closure**, and is carried so that current
  continuity `∇·j + ∂ρ/∂t = 0` is a scorable balance.

**Kept emergent, never promoted:** the carrier distribution `f_n(k,r)` — promoting it
double-counts its own moments and produces a differential-algebraic system; the electron
temperature `T_e(r)`, which is a second moment with a closed form; the electric field
`E(r) = −∇φ`, which is quasi-static; and every transport coefficient. The load-bearing
distinction is that `(T_L, φ, n, p, j)` are a new **scale**, not a new **distribution**.

## Moment closures

**Energy closure — the electron temperature.** The two-temperature energy balance is
`T_e − T_L = (2/3)(j·E)·τ_E/(n·k_B)` at steady state and
`(3/2)·n·k_B·∂_t T_e = j·E − (3/2)·n·k_B·(T_e − T_L)/τ_E` in transient form. The energy
relaxation time `τ_E` is per-composition: `tau-energy-POP-acoustic` (row 73) carries both
channels in one row — the polar-optical branch on `(α_F, ℏω_LO, T_L)` and the acoustic branch on
`(v_s, ρ, Ξ, T_L)`. `T_e` is **never state**; it is reconstructed from `(n, j, T_L)` and the
supplied `τ_E`. Validity windows by field strength: Ohmic below ≈10⁴ V/cm where `T_e ≈ T_L`;
warm from 10⁴ to 10⁵; hot from 10⁵ to 10⁶, which needs the momentum closure's mobility collapse;
saturated above a few × 10⁵, where `j ≈ q·n·v_sat`. The positivity bound `T_e ≥ T_L` is scored
as a `Positivity` residual.

**Momentum closure — the current density.** Drift-diffusion gives
`j_n = q·μ_n(E,T)·n·E + q·D_n·∇n` for electrons and `j_p = q·μ_p·p·E − q·D_p·∇p` for holes:
**only the diffusion term changes sign between carriers, never the drift term.** The Einstein
relation is `D = μ·k_B·T/q`; the field-dependent mobility is Caughey–Thomas
`μ(E) = μ₀·[1 + (μ₀·E/v_sat)^β]^(−1/β)`; the saturated regime collapses to `j ≈ q·n·v_sat`. No
distribution is required. The low-field mobility, saturation velocity and the exponent are
micro-supplied. The faithful tier verifies against the Boltzmann-transport current as an
`Algebraic/MethodEquivalence` residual.

**Degenerate-statistics caveat — a declared model-form error.** The Einstein relation above is
the **nondegenerate** form. Boron-doped p⁺ diamond contact layers, and degenerate n⁺ III-nitride
layers, run at 10²⁰–10²¹ cm⁻³, where Fermi–Dirac statistics make the generalised relation
`D/μ = (k_B·T/q)·F_{1/2}(η)/F_{−1/2}(η)` with `η = (E_F − E_C)/k_B·T` the correct one. Version 1
carries the nondegenerate form, and the discrepancy is entered as a **declared model-form-error
term** in the `combineTol` budget ([residual-definitions#error-budget]) on any composition whose carrier
density crosses the host's degeneracy threshold. The generalised variant is a gated refinement
sharing the same closed form, so it introduces no new method. The same threshold gate carries the
plasmon-phonon and Lyddane–Sachs–Teller exclusion ([out-of-scope#exclusions]).

## The homogenisation map

The three macro balance equations are

```
(P)  ∇·(ε∇φ) = −ρ,   ρ = q(p − n + N_D⁺ − N_A⁻)
(DD) ∂_t n + ∇·j = G − R,   j_n = q·μ_n·n·E + q·D_n·∇n
(H)  C_p·ρ_m·∂_t T_L − ∇·(κ(T)∇T_L) = j·E
```

Each row below maps a **micro per-composition output** to a **macro coefficient or term** by an
explicit relation evaluated at the local cell state:

| Micro output | Homogenisation relation | Macro coefficient or term | Equation |
|---|---|---|---|
| lattice thermal conductivity (rows 25 and 121) | `D_thermal(r) = κ(T_L(r))/(C_p·ρ_m)`; face flux `q_f = −κ(T_L,f)·(∇T_L)_f` | heat diffusion | (H) |
| conductivity and low-field mobility (`mobility-impurity-phonon`) | `σ(r) = q·n·μ₀(T_L(r), N_D)`; drift `μ(E,T) = μ₀[1 + (μ₀\|E\|/v_sat)^β]^(−1/β)` at `E(r) = −∇φ`; face flux by Scharfetter–Gummel; Einstein `D = μk_BT/q`, nondegenerate | drift and diffusion terms | (DD) |
| saturation velocity | saturated regime `j_drift = q·n·v_sat`, decoupling current from field | saturated drift | (DD) |
| impact-ionisation coefficient (Chynoweth `a·exp(−b/E)`) | `G_av(r) = α_n(\|E\|)·n·v_n + α_p(\|E\|)·p·v_p` at the local field; breakdown `M = 1/(1 − ∫α dx)` (row 75) | avalanche source | (DD) |
| Shockley–Read–Hall and generation-recombination rates | `S_carrier = G_av + G_opt − R_SRH(n, p; defect density(r))`, where `R_SRH` reads the **slow tier's** per-cell defect density | generation minus recombination | (DD) |
| Joule heating | `Q(r) = j(r)·E(r) = −j·∇φ`, the energy-conserving dissipative cross-coupling | heat source | (H) |
| temperature-dependent permittivity | `ε(r) = ε(material, T_L(r))` | Poisson operator | (P) |
| thermal boundary resistance | interface faces take the Robin condition `q_f = (T_L⁺ − T_L⁻)/TBR` | interface boundary condition | (H) |

**Supply contract.** Coefficients are *per-composition* — closed-form evaluables of the local
`(T_L, E, n, p)`, applied per cell. They are *error-tagged*: a cheap closed form and a faithful
Boltzmann-transport form, tied by an `Algebraic/MethodEquivalence` residual, with the tag carried
on the `dressing` facet. They are *cached* by content address, at `O(log₃₂ n)` lookup, and never
re-solved — this is what honours the no-solver-call-in-hot-paths rule. And they are split across
compile and runtime ([compose-time-pipeline#boundary]): the compile-time stages fix the coefficient
*form*, hash-consed into the kernel, and the runtime kernel evaluates the cached closed form at
the operator-supplied per-cell fields.

## The continuum residual

Generalising registry row 71, for each macro field and cell:

```
EOM/Continuum[field, c] = ‖ ∂_t field(c) − RHS_field({fields(c')}_{c' ∈ stencil(c)}; homogenised coeffs) ‖²
```

with `RHS_field` the finite-volume discretisation:

| Field | Right-hand side per cell `c` |
|---|---|
| `T_L` | `(1/C_p·ρ_m)·[ Σ_f κ(T_L,f)·(∇T_L)_f·A_f + Q(c)·V_c ] / V_c` |
| `φ` | algebraic constraint `‖Σ_f ε_f·(∇φ)_f·A_f + ρ(c)·V_c‖²` |
| `n` | `(1/V_c)·[ −Σ_f j_f·A_f/q + (G − R)(c)·V_c ]` |
| `p` | the same, with the hole sign |
| `j` | algebraic closure `‖j(c) − (q·μ_n·n·E + q·D_n·∇n)(c)‖²` |

**The drift-diffusion face flux must use Scharfetter–Gummel, not central differencing.** The
inter-cell carrier flux in the density rows is

```
j_f = (qD/Δx)·[ n_{c⁺}·B(Δψ) − n_{c⁻}·B(−Δψ) ],   Δψ = q(φ_{c⁺} − φ_{c⁻})/k_BT,   B(t) = t/(e^t − 1)
```

with `B` the Bernoulli function. At the ultra-wide-bandgap operating point the cell Péclet
number `Pe = qEΔx/k_BT ≈ 40` — 1 MV/cm across a ~10 nm cell against 25 mV of thermal voltage —
and there a centrally differenced flux makes **the residual operator itself wrong at the
operating point**. The operator would then be scored against a discretisation artifact rather
than against the physics. Scharfetter–Gummel is closed-form and differentiable, with one
removable singularity at `Δψ → 0` guarded by the series `B(t) ≈ 1 − t/2`, so it preserves
continuous differentiability and the no-runtime-solver rule. The interface heat flux and the
Poisson and current constraints are unaffected: only the convection-dominated carrier flux needs
the exponential fitting.

The potential and the current density are **algebraic constraint** balances with no time
derivative. Axes are `(MeshCell, MacroField)`; the per-cell-per-field scalar is the atomic
contribution, with the spatial bin being the mesh cell ([residual-definitions#granularity]); a
`RoaringCoverageMask` over `enumerate(product(MeshCell, MacroField))` selects the constrained
subdomain.

`EOM/Continuum` is the **macro instance of the equation-of-motion violation family**, not a new
top-level category — `MacroField` plays the role `StateComponent` plays in the micro tier — and
registry row 71 is one coupled instance of it. Scoring is score-not-solve: the operator supplies
the macro-state trajectory on the mesh ([pino-bridge#validate]), and the oracle evaluates the per-cell
residual and cotangent. It never solves the partial differential equation.

## The unified three-tier residual contract

The three schemas are **not unifiable into one tensor** — they carry three distinct
discretisations — which is why the state is stratified rather than flattened:

| Tier | State | Index | Category | Reversible part | Dissipative part |
|---|---|---|---|---|---|
| Micro | seven components | Brillouin zone × cell | the seven micro `EOM/*` categories | streaming and force | collision |
| Slow | defect concentrations | (species, site) | `EOM/DefectPopulation` | none; energy sits in the state energies | master-equation generator |
| Macro | `(T_L, φ, n, p, j)` | (MeshCell, MacroField) | `EOM/Continuum` | quasi-static, the potential and current constraints | parabolic diffusion and sources |

All three share **one residual shape**, `‖∂_t x − (L·δE/δx + M·δS/δx)‖²`
([residual-definitions#eom-categories]), instantiated three ways, plus the common conservation, positivity and
algebraic-identity residuals. The macro reversible operator is quasi-static — there is no
reversible bracket between continuum fields — so its equation of motion is dominantly the
dissipative branch, which is exactly the pure-dissipative fluid limit and is consistent with the
macro tier being the spatial reduction of the kinetics level.

One `ResidualKey = (producer, axes)` space spans all tiers, over tier-typed axis universes. The
closed `CategoryTag` set has **19 members**, including `EOM/DefectPopulation` and
`EOM/Continuum`. The operator holds one `Map<ResidualKey, Weight>` and aggregates per
`CategoryTag` and per state-tier facet; **the oracle never pre-sums across tiers**
([residual-definitions#categorytag]).
