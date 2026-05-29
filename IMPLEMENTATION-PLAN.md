# `/physics` — Comprehensive Implementation Plan

> **AMENDMENT STATUS (added during S1–S7 UWBG research integration).**
> This plan has been amended for the UWBG-semiconductor harsh-environment-chip scope. The amendment lives in two forms:
>
> 1. **Source document**: `physics/research/amendment-s7-source.md` (~9700 words, 17 sections) — the edit-ready amendment as produced by Stream S7.
> 2. **In-place edits**: §§19–§26 of THIS file are appended at the end (residual-generator factory, three pino-bridge exports, multi-source training discipline, out-of-scope declarations, outstanding decisions, verification, post-amendment migration, applicability classifiers). The amendment's prescribed in-place edits to existing §3.1, §5.3, §7, §8, §10, §11, §12, §13 are deferred until the implementation language is fixed and the build skeleton begins — see source document for the diff specification.
>
> **Headline count changes (per amendment):**
> - Named formulas: ~22 → 87 (manifest at `physics/library/formulas/registry-manifest.csv`)
> - Abstract templates: 12 → 18 (+InterfaceEquilibriumOf, +SelfConsistentChargeBalanceOf, +HarmonicStiffnessHessianOf, +BiSlabGrandPotentialOf, +MassActionEquilibriumOf, +ClusterExpansionOf)
> - Observable bundles: 8 → 11 (+defect-resolved, +surface-resolved, +interface-resolved, +field-resolved, +hot-carrier-resolved, +degradation)
> - Residual categories: 5 → 7 (+structural-validity, +thermodynamic-consistency)
> - Cert obligations: 6 → 10 (+bulk-edge-correspondence, +reference-battery-versioned, +surrogate-net-validity, +adjoint-existence-at-registration)
> - Methods: 12 (unchanged) + 2 new sub-methods (field-line-integral, interface-tunneling)
> - State vector: **UNCHANGED** — the 7-tuple `(h, R_I, P_I, Π_h, Z_I, γ̂, A)` is confirmed sufficient (S4 finding); non-equilibrium quantities are emergent
> - Environment: +`temperature_gradient`; Response interface: +`causal?:Boolean` param
>
> **Research provenance for the amendment** (all under `physics/research/`):
> - `uwbg-observable-catalog.md` (S1), `csp-heterostructure.md` (S2), `defects-surfaces-interfaces.md` (S3), `non-equilibrium-high-field.md` (S4), `residual-generator-catalog.md` (S6), `amendment-s7-source.md` (S7), `applicability-classifiers.md` (post-S7), plus `informed-operator/design/residual-loss-methodology.md` (S5)
>
> ---

> **Companion documents:** `research/group-A-ion-dynamics.md`,
> `research/group-B-electronic-magnetic-optical.md`,
> `research/group-C-transport-thermo-chemical.md`.
> Read those for the mathematical grounding. This plan synthesizes
> them into the architecture and execution sequence.

---

## 1. Project context

The repository at `~/Desktop/Physics/Programs/n-Op/` is the start of
**n-Op**, a project that builds a physically-informed neural
operator (PINO) for materials physics. The operator is meant to
learn **how the unified multiphysics state of a system evolves over
time**, inside a fixed crystal lattice.

n-Op is structured as three sibling top-level libraries:

```
n-Op/
├── physics/             ← this document is about THIS sibling
├── informed-operator/   ← the PINO; consumes /physics; learns state evolution
└── interface/           ← user-facing surface
```

`/physics` is the **reference oracle** the operator is trained
against. It encodes the entire multiphysics system as a unified
state, provides the dynamics (equations of motion) that evolve it,
produces the residuals that enforce physics on any candidate
evolution, and exposes the observable readouts derived from state.

The architectural style is lifted from the prior Racket library at
`~/Desktop/Physics/Library/physics/` — strict layered architecture
with a single typed seal, "minimum primitives, no extras without
justification," no-symbolics on the runtime path, cert as
first-class deliverable, loud failure with numeric witnesses, and
substrate-agnostic stance. See `physics-library-architecture.md`
for the full architectural summary of the prior library.

---

## 2. What `/physics` is, in one sentence

> A substrate-agnostic library that encodes the entire multiphysics
> system as a unified state, expresses its dynamics in the GENERIC
> two-bracket form, exposes physical-constraint residuals as PINO
> loss terms, and provides observable readouts as typed
> compositions of a small vocabulary of computational methods.

`/physics` does NOT train, hold learned weights, integrate
trajectories, wrap external DFT/MD codes at runtime, or know about
the neural operator's architecture. Those are all downstream
concerns owned by `/informed-operator`.

### Key invariants

1. **State first.** Every quantity is either part of the state
   (irreducible DOF) or computed from the state (derived).
2. **GENERIC dynamics.** `dx/dt = L · δE/δx + M · δS/δx` with
   `L` antisymmetric, `M ⪰ 0`, plus degeneracy conditions.
3. **No-symbolics on the runtime path.** Structured data only as
   expand-time macro input or as inert certificate output.
4. **Typed everything.** Every method, template, formula has an
   explicit typed signature. No string-encoded formulas. No
   implicit / optional / hand-waved parameters.
5. **Composition over duplication.** Properties are typed
   compositions of a small vocabulary of methods. Three
   "second-derivative" observables share one template.
6. **Loud failure with numeric witnesses.** Every degeneracy raises
   at the typed boundary with the offending number attached.
7. **Cert is first-class.** Schema + freeze fixture + tamper
   tripwire + bigfloat oracle. Roughly the size of any one level.

---

## 3. Mathematical foundation: GENERIC over unified state

### 3.1 Unified state vector

```
x(t) = ( h(t),                cell vectors                          ∈ GL⁺(3, ℝ)
        {R_I(t)}_{I=1..N},    ion positions                          ∈ ℝ^{3N}
        {P_I(t)}_{I=1..N},    ion momenta                            ∈ ℝ^{3N}
        Π_h(t),               cell momentum                          ∈ ℝ^{3×3}
        {Z_I}_{I=1..N},       species labels (immutable)             discrete
        γ̂(r, r'; t),          Pauli-spinor 1-body density matrix     2×2 spinor operator
        A(r, t)               external EM vector potential           ∈ ℝ^3 field
      )
```

These are the **irreducible DOFs**. Continuum displacement fields
`u(X, t)`, phonon distributions `n_{qs}(r, t)`, carrier
distributions `f_n(k, r, t)`, surface coverages `θ_i(t)`, and
composition vectors `x_i(t)` are **emergent** (coarse-grainings,
Bloch transforms, semiclassical limits of the irreducible state).

### 3.2 Canonical functionals

```
E[x] = E_kin(ions)                  Σ_I |P_I|²/(2M_I) + tr(Π_hᵀΠ_h)/(2W)
     + E_BO(R, h)                   min_γ̂ ⟨Ĥ_electronic⟩[γ̂; R, h]
     + E_KS[γ̂]                      kinetic + Hartree + xc functional on γ̂
     + E_EM[A]                      (1/8π) ∫ (|E|² + |B|²) dr
     + E_coupling                   electron-phonon, spin-orbit, magneto-elastic, optical-electronic

S[x] = S_vib[x]                     vibrational entropy from phonon spectrum
     + S_electronic[γ̂; T]           electronic entropy (Fermi-Dirac of γ̂ spectrum)
     + S_config[x]                  configurational entropy of coarse-grained DOFs
```

### 3.3 GENERIC operators

```
L (Poisson, antisymmetric):
  - symplectic on (R, P)           {f,g}_RP = Σ_I (∂_{R_I}f · ∂_{P_I}g − ∂_{P_I}f · ∂_{R_I}g)
  - symplectic on (h, Π_h)         {f,g}_hΠ = ∂_h f : ∂_Π g − ∂_Π f : ∂_h g
  - Liouville on γ̂                 (1/iℏ) [Ĥ_KS, ·]
  - Maxwell on A                   Hamilton form of EM field
  - semiclassical streaming        on emergent distributions

M (dissipative, symmetric PSD):
  - phonon-phonon scattering       three- and four-phonon collision kernels
  - electron-phonon scattering     Fermi-golden-rule from g_{nm,ν}(k,q)
  - Gilbert damping                α S × (S × H_eff) for magnetic dynamics
  - radiative damping              spontaneous-emission rate for optical
  - chemical rate matrix           symmetrized W_ij from detailed balance
```

### 3.4 Unified equation of motion

```
dx/dt = L · δE/δx + M · δS/δx
```

with the degeneracy conditions:

```
L · δS/δx = 0              reversible part doesn't change entropy
M · δE/δx = 0              dissipative part conserves energy
```

Static observables are **equilibrium readouts** — fixed points
where `dx/dt = 0`. Time-evolving observables are **trajectory
readouts** along the GENERIC flow. The same framework subsumes
both; static is the equilibrium limit.

### 3.5 The 9 regimes as extractions of GENERIC

| Regime | Extraction |
|--------|-----------|
| Structural | Critical points of `E` at `T = 0` (or `F` at `T > 0`); 1st derivatives |
| Mechanical | 2nd strain-derivatives of `F` at equilibrium |
| Thermal | Eigendecomposition of `∂²E_BO/∂u²` (phonons); BTE for phonon distribution (full GENERIC) |
| Electronic | SCF as gradient flow on `E_KS`; TDKS as Liouville on `γ̂` (pure L) |
| Magnetic | Pauli-spinor extension of `γ̂`; LLG = L (precession) + M (Gilbert) |
| Optical | Response of `γ̂` to `A(t)` via L; absorption via M (radiative damping) |
| Transport | BTE on emergent carrier distribution: L (streaming) + M (collisions) |
| Thermodynamic | min `F` at fixed `(T, V, N)`; convex hull of `{F_φ}` |
| Chemical | Master equation on configurations (M = rate matrix); NEB on `E_BO` |

See `research/synthesis.md` for the detailed derivation of each
extraction from the unified GENERIC structure.

---

## 4. Architectural principles

Inherited from the source library, retargeted for the GENERIC
framework:

| # | Principle | Application here |
|---|-----------|-----------------|
| 1 | Strict layered architecture, single typed seal | `core ← shared ← state/canonicals/generic/methods ← observables ← cert ← api`. One typed module wraps everything. |
| 2 | Minimum primitives, no extras | The 12-method computational vocabulary is the closed primitive set. Everything else is composition. |
| 3 | No-symbolics on runtime path | Structured data only as expand-time macro input (canonical trees) or inert cert output. State is flat numeric. |
| 4 | Cert as first-class sub-tree | Schema + freeze fixture + tamper tripwire + bigfloat oracle. Six obligations (see §13). |
| 5 | Loud failure carrying numeric witnesses | Every degeneracy raises with the offending number attached. |
| 6 | Compile-time staging via macros | `derive-residual`, `derive-update`, `derive-readout` macros lift trees into flat numeric code. |
| 7 | Substrate-agnostic stance | `/physics` only emits state + dynamics + residuals + readouts. The PINO, integrator, trainer all live downstream. |
| 8 | House style | Long descriptive names, header docstrings stating contract + exclusions, gate-style tests, tracker IDs in headers. |
| 9 | Dual VCS + bd workflow | `_darcs/` for project VCS, `.git/` for bd-tracker scaffolding. |

---

## 5. Top-level concepts (the three "what is" inputs)

`/physics` accepts three irreducible top-level input concepts. They
are physically orthogonal — each varies independently of the
others:

### 5.1 PeriodicityStructure

The spatial skeleton. A discrete subgroup of `R³` describing the
translations that leave the system invariant. Parameters:

- Dimensionality `d ∈ {0, 1, 2, 3}` (cluster / chain / slab / bulk)
- Lattice vectors `{a_i}` (when `d > 0`)
- Periodicity flags `(periodic_x, periodic_y, periodic_z)` for slab
  / nanowire variants

### 5.2 SiteDecoration

The per-position content. A function from positions in the
fundamental domain to an extensible **attribute record**. Each
site carries:

- `species` (one of a closed set of element symbols)
- `position` (fractional or Cartesian)
- optional `spin` (3-vector for noncollinear magnetic structures)
- optional `charge_state` (oxidation state)
- optional `occupancy` (probability ∈ [0, 1] for alloys / disorder)
- optional `tag` (`'host` / `'defect` / `'adsorbate` / `'substrate`
  / `'impurity`)

Defects, surfaces, adsorbates, magnetic configurations, charged
systems, and alloys are all SPECIAL CASES of `SiteDecoration` —
not new top-level types.

### 5.3 Environment

External conditions on the system. Universal across regimes:

- `temperature` (T)
- `pressure` (P) or equivalently `volume` (V)
- `chemical_potentials` (`{μ_i}` per species, for grand-canonical contexts)
- `applied_electric_field` (`E_ext(r, t)`, optional)
- `applied_magnetic_field` (`B_ext(r, t)`, optional)
- `applied_stress` (`σ_ext`, optional)

### 5.4 Demoted, one-layer-down

- **Reference** — a bag of `(Crystal, Environment, weight)` tuples
  used as baselines for energy-difference observables. Composes
  from the three top-level concepts; not a new concept.
- **Property** — the API-side request specifying which observable
  to predict. Parameter of `predict` and `residual` functions; not
  an input to the system description.

---

## 6. Born-Oppenheimer hierarchy: the 4 levels

The 9 regimes don't live as flat siblings. They organize into a
**4-level hierarchy** where each level mathematically coarse-grains
the previous. Dependency strictly upward: Level 4 → Level 3 →
Level 2 → Level 1.

### Level 1 — Quantum electronic substrate

- **Operates on:** `γ̂(r, r'; t)` (Pauli-spinor 1-body density
  matrix), `A(r, t)` (external EM)
- **For fixed:** nuclear positions `(R_I, h)` (fixed by Level 2)
- **Math:** Hohenberg–Kohn theorems; Kohn–Sham reduction;
  TDKS-Liouville; TDCSDFT (Vignale–Rasolt + spin); Runge–Gross
  theorem; van Leeuwen action on Keldysh contour
- **Regimes covered:** ELECTRONIC, OPTICAL, MAGNETIC
- **Irreducible state at this level:** `γ̂`, `A`
- **Canonical:** `E_KS[γ̂]`, `E_EM[A]`
- **Closure functional:** `v_xc(r)`, `B_xc(r)`, `f_xc(r, r', ω)`,
  BSE kernel `K`
- **Dynamics:** Liouville–von Neumann on `γ̂`; Maxwell on `A`

### Level 2 — Born-Oppenheimer surface

- **Operates on:** `(R_I, P_I, h, Π_h)` Parrinello–Rahman phase
  space + immutable `{Z_I}`
- **Uses from Level 1:** `E_BO(R, h) = min_γ̂ ⟨Ĥ⟩`,
  `F_I = -∂E_BO/∂R_I` (Hellmann–Feynman + Pulay),
  `σ = -∂E_BO/∂h` (DFT stress)
- **Math:** variational on `(R, h)`; derivatives of `E_BO`;
  strain expansion; Parrinello–Rahman extended Hamiltonian
- **Regimes covered:** STRUCTURAL, MECHANICAL
- **Irreducible state at this level:** `(R, P, h, Π_h, Z)`
- **Canonical:** `E_kin(P, Π_h) + E_BO(R, h)`
- **Dynamics:** Symplectic Hamilton's equations on the Parrinello–
  Rahman phase space

### Level 3 — Equilibrium statistics

- **Operates on:** spectral data from Level 1 (`{ε_n(k)}`) and
  Level 2 (`{ω_{qs}}`)
- **Uses from Levels 1 + 2:** Eigenspectra, derived from `Ĥ_KS`
  and `D(q)` respectively
- **Math:** partition functions `Z(T, V, N)`; free energies
  `F = -k_BT log Z`, `G = F + PV`, `Ω = F - μN`; QHA / SCP;
  Cahn–Hilliard / Allen–Cahn gradient flow; convex hull
- **Regimes covered:** THERMAL, THERMODYNAMIC
- **Irreducible state at this level:** aggregate intensives
  `(T, P, μ_i)`, composition `(x_i)`, phase amounts `(c_φ)`, plus
  spatial fields if phase-field is used
- **Canonical:** `F[x; T]`, `G[x; T, P]`, `Ω[x; T, μ]`
- **Entropy:** `S_vib`, `S_electronic`, `S_config`
- **Dynamics:** gradient flow `∂_t x = -M · δF/δx`

### Level 4 — Non-equilibrium kinetics

- **Operates on:** emergent distribution functions `f_n(r, k, t)`
  (carriers), `n_{qs}(r, t)` (phonons), coverages `θ_i(t)`,
  reaction coordinates `ξ(t)`
- **Uses from Levels 1–3:** All lower data; in particular spectral
  data (band structure, phonons) and free energies
- **Math:** Boltzmann transport equation; Kubo / Green–Kubo
  linear response; GENERIC two-bracket; master equation; Marcus
  theory; TST / hTST / Vineyard; NEB
- **Regimes covered:** TRANSPORT, CHEMICAL/SURFACE; PHONON
  TRANSPORT (part of thermal)
- **Irreducible state at this level:** emergent distributions and
  coordinates (above)
- **Canonical:** Lyapunov functional `H[f]` or relative entropy
  `D(P || P_eq)`
- **GENERIC L:** semiclassical streaming
- **GENERIC M:** collision integrals, rate matrices

### Note: regimes can span levels

**Thermal** spans Level 3 (Bose–Einstein on phonon spectrum) and
Level 4 (phonon BTE for thermal conductivity). The library is
organized by levels, not by regimes — a regime is a navigational
*view* across the levels that contribute to it.

---

## 7. The computational vocabulary (12 methods)

This is the **closed primitive set**. Every observable on the
slide decomposes into a chain of these methods. Each has a typed
signature.

```
methods/
├── state-readout                  StateReadout(x, extractor: Extractor) → Value
│                                  pairwise-distance-PBC, atomic-sphere-integral,
│                                  position-diagonal-trace, cell-metric-extraction,
│                                  spectral-extremum, occupation-sum
│
├── algebraic-combination          AlgebraicCombination({inputs}, formula: NamedFormula) → Value
│                                  (Always invokes a NAMED FORMULA from the registry —
│                                   no string formulas, no implicit math.)
│
├── functional-differentiation     FunctionalDifferentiation(F: Functional,
│                                                              w.r.t.: Coordinate,
│                                                              at: StatePoint,
│                                                              order: ℕ = 1) → Tensor
│                                  Sub-methods: gradient (order=1), hessian (order=2),
│                                  higher-order (order>2)
│
├── variational-minimization       VariationalMinimization(F: Functional,
│                                                            target: Coordinate,
│                                                            fixed: Coordinate,
│                                                            method: Optimizer,
│                                                            tol: real) → StatePoint
│                                  Sub-methods: steepest-descent, conjugate-gradient,
│                                  BFGS, FIRE, Newton, SCF-mixing, Pulay-mixing
│
├── spectral-decomposition         SpectralDecomposition(Op: Operator,
│                                                          basis: Basis,
│                                                          k: int = full,
│                                                          method: EigenSolver) → (Spectrum, Eigenvectors)
│                                  Sub-methods: full-diagonalization, Lanczos,
│                                  Davidson, inverse-iteration, shift-invert
│
├── spectral-aggregation           SpectralAggregation(spectrum: Spectrum,
│                                                       aggregator: Aggregator,
│                                                       weights: Field) → Field
│                                  Sub-methods: delta-sum (DOS), partition-Z (log-sum-exp),
│                                  thermal-average (Bose / Fermi / MB), occupation-sum
│
├── linear-response                LinearResponse(observable: Operator,
│                                                  perturbation: Operator,
│                                                  kernel: ResponseKernel,
│                                                  frequency: real = 0) → Response
│                                  Sub-methods: Kubo (correlator), Linear-Response-DFT (Dyson),
│                                  Greens-function (resolvent), Sternheimer
│
├── path-search                    PathSearch(F: Functional,
│                                              initial: StatePoint,
│                                              final: StatePoint,
│                                              method: PathMethod,
│                                              n_images: int = 9,
│                                              tol: real) → MinimumEnergyPath
│                                  Sub-methods: NEB, climbing-image-NEB, dimer,
│                                  string-method
│
├── convex-optimization            ConvexOptimization(points: Set[StatePoint],
│                                                      objective: ConvexObjective,
│                                                      method: ConvexSolver) → Solution
│                                  Sub-methods: convex-hull (lower envelope),
│                                  common-tangent, quadratic-program
│
├── kinetic-evolution              KineticEvolution(distribution: Distribution,
│                                                    collisions: CollisionKernel,
│                                                    gradient: AppliedGradient,
│                                                    method: KineticMethod,
│                                                    truncation: int) → SteadyState
│                                  Sub-methods: BTE-RTA, BTE-full, master-equation,
│                                  drift-diffusion, Cahn-Hilliard, Allen-Cahn
│
├── statistical-sampling           StatisticalSampling(distribution: Distribution,
│                                                       method: Sampler,
│                                                       n_samples: int) → SampleSet
│                                  Sub-methods: Monte-Carlo, molecular-dynamics, kMC,
│                                  importance-sampling
│
└── symmetry-projection            SymmetryProjection(target: Tensor,
                                                       group: SymmetryGroup,
                                                       projection_kind: ProjKind) → Tensor
                                   Sub-methods: point-group-projection,
                                   space-group-projection, time-reversal-symmetrize
```

These 12 methods cover every observable on the slide.

---

## 8. Abstract property templates (14)

> **γ' update (validator-1):** templates 12 → 14. Added at bottom:
> `SelfConsistentRenormalizationOf` (covers SCPH/SSCHA, GW self-energy, polaron, BSE-iterated; method selector picks variant), and `ConfigurationalFreeEnergyOf` (covers cluster-expansion AND Redlich-Kister composition-dependent excess Gibbs as separate parameterizations — they are NOT the same formula).

Templates are **parameterized method chains**. Concrete observables
are template instantiations. The discipline: collapse "N
observables with the same shape" into "1 template × N argument
tuples."

```
abstract-properties/
├── state-readout-of                  StateReadoutOf(x: State, extractor: Extractor) → Value
│
├── algebraic-of                      AlgebraicOf({inputs}, formula: NamedFormula) → Value
│
├── second-derivative-of              SecondDerivativeOf(F: Functional,
│                                                         x₀: StatePoint,
│                                                         coord: Coordinate,
│                                                         metric: TensorNorm) → Tensor
│
├── spectrum-of                       SpectrumOf(Op: ParametricOperator,
│                                                  domain: ParametricDomain) → FieldOnGrid
│
├── spectral-aggregate-of             SpectralAggregateOf(spectrum-from: Source,
│                                                          aggregator: Aggregator,
│                                                          weights: Field) → FieldOnGrid
│
├── response-of-to                    ResponseOfTo(observable: Operator,
│                                                    perturbation: Operator,
│                                                    kernel: ResponseKernel,
│                                                    frequency: real) → Response
│
├── path-stationary-of                PathStationaryOf(F: Functional,
│                                                       initial: StatePoint,
│                                                       final: StatePoint,
│                                                       method: PathMethod) → ReactionCoord
│
├── kinetic-evolution-of              KineticEvolutionOf(distribution: Distribution,
│                                                         collisions: CollisionKernel,
│                                                         gradient: AppliedGradient) → SteadyState
│
├── classify-of                       ClassifyOf(object: StateComponent,
│                                                  classifier: Classifier) → DiscreteLabel
│                                                  (space group, Wyckoff, crystal-structure class)
│
├── comparison-of                     ComparisonOf(target: StateComponent,
│                                                    reference: StateComponent,
│                                                    metric: ComparisonMetric) → Difference
│                                                    (defect characterization, surface region)
│
├── radiative-emission-of             RadiativeEmissionOf(excited_state: State,
│                                                          optical_coupling: Operator) → Field
│                                                          (PL spectra, photoemission)
│
├── microkinetic-steady-state-of      MicrokineticSteadyStateOf(network: RateNetwork,
│                                                                  initial: Coverage,
│                                                                  driving: Environment) → Coverage
│                                                                  (catalytic activity, TOF)
│
├── self-consistent-renormalization-of  SelfConsistentRenormalizationOf(
│                                          bare: BareSubstrate,
│                                          method: {SCP-perturbative, SSCHA-stochastic,
│                                                   TDEP, GW-one-shot, GW-self-consistent,
│                                                   BSE-iterated, polaron-self-consistent},
│                                          T: Temperature,
│                                          convergence: ConvergenceCriterion
│                                       ) → DressedQuantity
│                                       [γ' addition; fixed-point structure shared across
│                                        SCPH/SSCHA, GW self-energy, BSE iteration, polaron;
│                                        emits IterativeResult cert evidence — see §27]
│
└── configurational-free-energy-of    ConfigurationalFreeEnergyOf(
                                          parameterization: {ClusterExpansion(ECI),
                                                             RedlichKister(L_ν, order),
                                                             BraggWilliams},
                                          composition: x,
                                          T: Temperature
                                       ) → G_config
                                       [γ' addition; cluster-expansion (discrete T=0 lattice
                                        energy) and Redlich-Kister (continuous composition-
                                        dependent excess Gibbs) are DISTINCT parameterizations
                                        of this template, NOT instances of each other]
```

---

## 9. Named formulas registry (closed; canonical list in `registry-manifest.csv`)

> **γ' update (validator-1):** the brief listing below is illustrative; the canonical, machine-readable registry is `physics/library/formulas/registry-manifest.csv` (95 substantive rows + 2 architectural markers). γ' additions (rows 88–95): `lo-to-non-analytic-correction` (Gonze-Lee, requires Z\*/ε∞ from L1 linear-response sub-stage), `makov-payne-correction` (Madelung-based, separate from FNV/LZ — NOT merged), `kumagai-oba-correction` (atomic-site averaging), `madelung-constant` (L1 primitive), `born-effective-charge-tensor` (L1 primitive), `high-frequency-dielectric-tensor` (L1 primitive), `electronic-susceptibility-chi-infinity` (L1 primitive), `redlich-kister-excess-gibbs` (registered separate from cluster-expansion — see §8 template note). The strategy-pattern dispatcher `charged-defect-correction(scheme ∈ {MP, FNV, LZ, KumagaiOba})` lives in `methods/`, not `formulas/`.


Every algebraic combination invokes a NAMED FORMULA with typed
inputs and explicit output type. No string formulas, no embedded
math expressions. Each is independently citable to published
references and is independently verifiable by the cert sub-tree.

```
formulas/
├── slab-arithmetic                   (E_slab, E_bulk, n, A) → real
├── arrhenius                         (D₀, E_a, T) → real
├── einstein-mobility-diffusivity     (μ, T, q) → real
├── kramers-kronig-hilbert            (Im_ε: Field[ω]) → Field[ω]
├── chen-hardness                     (K, G) → real
├── teter-hardness                    (G) → real
├── tian-hardness                     (K, G) → real
├── mazhnik-oganov-hardness           (K, G, χ_electroneg) → real
├── voigt-reuss-hill-averages         (C_IJ) → (K, G)
├── christoffel-eigenvalue            (C, q̂, ρ) → sound-speed
├── vineyard-prefactor                (ν_min, ν_saddle) → real
├── jump-diffusivity                  (a, Z, ν₀) → D₀
├── bose-einstein-cv                  (ω, T) → real
├── bose-einstein-helmholtz           (ω, T) → real
├── fermi-dirac-helmholtz             (ε, μ, T) → real
├── fermi-dirac-occupation            (ε, μ, T) → real
├── formation-energy-from-references  ({E_compound, {E_refs}, {n_i}, {μ_i}}) → real
├── defect-formation-energy           (E_def, E_perfect, Δn, μ, q, E_F) → real
├── lorenz-wiedemann-franz            (σ, T) → κ_el
├── linear-elasticity-stress-strain   (C, ε) → σ
├── van-roosbroeck-shockley           (α(ω), T) → PL(ω)
├── htst-rate                         (ν₀, E_a, T) → rate
├── turnover-frequency                (θ_steady, network, RC-step) → real
└── current-density-from-distribution (δf, group-vel) → j-vector
```

This is the closed registry for the materials-physics scope on the
slide. New formulas added through a controlled cert-validated
process; the registry is a load-bearing contract.

---

## 10. Observable bundles (8 bundles, organized by data shape)

Per the user-chosen bundling axis: outputs are grouped by **where
they live in their typed domain**, not by physical regime. This
makes the cross-cutting numerical machinery (BZ integration,
real-space FFT, tensor contraction) live once per bundle and be
reused by every regime that produces into it.

```
observables/
├── bz-resolved/                      BandStructure, PhononDispersion,
│                                     KResolvedDOS, MagnonDispersion
│
├── energy-resolved/                  DOS, OpticalAbsorption, JointDOS,
│                                     ImChi(ω), ReChi(ω)
│
├── real-space/                       ChargeDensity, SpinDensity,
│                                     ElectrostaticPotential
│
├── atom-indexed/                     Forces, MagneticMoments, AtomicCharges,
│                                     DisplacementField
│
├── tensor-indexed/                   ElasticConstants, ConductivityTensor,
│                                     ThermalConductivityTensor,
│                                     ThermalExpansionTensor, Susceptibility
│
├── temperature-resolved/             HeatCapacity(T), FreeEnergy(T),
│                                     IonicDiffusivity(T)
│
├── reaction-coord/                   NEBProfile, MigrationPath
│
└── scalars/                          BandGap, TotalEnergy, FormationEnergy,
                                      SurfaceEnergy, AdsorptionEnergy,
                                      BulkModulus, Hardness, MigrationBarrier
```

Each output type in a bundle is named, physically meaningful, and
implements one or more cross-cutting interfaces.

---

## 11. Cross-cutting interfaces (4)

Define what *operations* an output supports. Closed, stable set:

```
interfaces/
├── scalar                  arithmetic on a number with units
├── field-on-grid           evaluate, tabulate, integrate, restrict, differentiate
├── tensor                  index, contract, change-of-basis, symmetrize
└── response                evaluate, Hilbert-transform, integrate, causality-check
```

These are orthogonal to bundles — an output's bundle determines
its shape; the interface determines what operations make sense on
that shape. Many outputs implement multiple interfaces
(`OpticalAbsorption` is `FieldOnGrid` over `EnergyAxis` AND
`Response` with causality structure).

---

## 12. Residual contract (PINO loss terms)

```
residuals/
├── eom-violation/                    ‖dx/dt − (L δE/δx + M δS/δx)‖²
│                                     PRIMARY residual; trains the PINO on the physics
│
├── degeneracy/                       ‖L δS/δx‖² + ‖M δE/δx‖²
│                                     enforces GENERIC structure
│
├── conservation/                     conserved-quantity violations
│   ├── energy
│   ├── particle-number / charge
│   ├── momentum / crystal-momentum
│   └── spin / total angular momentum
│
├── positivity/                       physical-bound violations
│   ├── M-positive-semidefinite       ‖max(0, -λ(M))‖²
│   ├── distribution-bounds           Σ max(0, -f)² + max(0, f-1)² (fermions)
│   ├── density-non-negative          ‖max(0, -ρ)‖² (charge, spin, DOS)
│   ├── frequency-real                ‖max(0, -ω²)‖² (phonons, optical modes)
│   ├── conductivity-non-negative     ‖max(0, -λ(σ))‖²
│   └── spin-magnitude                ‖|S_i| - 1‖² (atomistic spins)
│
├── algebraic-identities/             named-formula consistency
│   ├── kramers-kronig                Re ε and Im ε satisfy KK Hilbert transform
│   ├── f-sum                         ∫ ω Im ε(ω) dω = ω_p²
│   ├── acoustic-sum                  Σ_J Φ_{IαJβ}(0) = 0
│   ├── detailed-balance              W_ij P_j^eq = W_ji P_i^eq
│   ├── einstein-relation             D = μ k_B T / q
│   ├── onsager-symmetry              L_αβ(B) = L_βα(-B)
│   ├── maxwell-relations             (∂S/∂V)_T = (∂P/∂T)_V (and cyclic)
│   └── method-equivalence            BTE-σ ≡ Kubo-σ in linear response limit
│
└── total-residual                    outer linear combination with regime-aware weights
```

The **total residual** is the weighted sum of the above. Weights
are exposed as parameters; the cert layer verifies that all
weights ≥ 0 and that the linear combination is dimensionally
consistent.

---

## 13. Cert sub-tree (6 obligations)

```
cert/
├── certificate                       schema, emitter, inert-sexpr guard (lifted)
├── certificate-text-renderer         deterministic layout (lifted)
├── regression-freeze                 frozen reference + tamper tripwire (lifted)
├── high-precision-crosscheck         bigfloat oracle, non-load-bearing (lifted)
│
├── obligation-1-symmetry             crystallographic group respected
├── obligation-2-bounds               physical positivity (gaps ≥ 0, ω real, σ ≥ 0, ρ ≥ 0)
├── obligation-3-analytic-limits      harmonic-crystal phonons, free-electron bands,
│                                     Dulong-Petit, ideal-gas
├── obligation-4-reference-battery    frozen DFT / MD / experimental values
│                                     on a held-out crystal battery
├── obligation-5-conservation         DOS integrates to electron count;
│                                     Cv consistent with phonon DOS;
│                                     Maxwell relations hold
└── obligation-6-degeneracy           GENERIC-specific: L δS = 0, M δE = 0,
                                      and named-formula consistency across
                                      equivalent compositions (BTE ≡ Kubo, etc.)
```

The certificate emitted for any prediction is an inert s-expression
carrying scalar verdicts for each obligation, plus the numeric
witnesses for any failures. Same discipline as the source library:
schema is the cross-workstream contract.

---

## 14. Complete directory tree

```
n-Op/
├── physics/
│   ├── README.md                            top-level architecture doc
│   ├── AGENTS.md, CLAUDE.md                 agent / contributor workflow
│   ├── .gitignore, _darcs/, .git/           dual VCS + bd scaffolding
│   ├── IMPLEMENTATION-PLAN.md               THIS DOCUMENT
│   ├── properties.md                        the 9-regime scope (existing)
│   ├── physics-library-architecture.md      source-library reference (existing)
│   ├── demo.ipynb                           end-to-end tour (later)
│   │
│   ├── research/                            mathematical research (companion files)
│   │   ├── group-A-ion-dynamics.md          structural, mechanical, thermal
│   │   ├── group-B-electronic-magnetic-optical.md
│   │   ├── group-C-transport-thermo-chemical.md
│   │   └── synthesis.md                     GENERIC + level hierarchy + composition algebra
│   │
│   ├── library/
│   │   ├── info.rkt                         package manifest + raco test wiring
│   │   ├── main.rkt                         THE typed seal (single typed module)
│   │   ├── api.rkt                          typed boundary contents
│   │   ├── examples.rkt                     worked-example runners
│   │   │
│   │   ├── inputs/                          time-independent system definition
│   │   │   ├── periodicity-structure.rkt
│   │   │   ├── site-decoration.rkt
│   │   │   └── environment.rkt
│   │   │
│   │   ├── state/                           unified system state x(t)
│   │   │   ├── system-state.rkt             unified container
│   │   │   ├── enumeration.rkt              iterate / serialize / hash full state
│   │   │   ├── level-1-electronic/          γ̂, A
│   │   │   │   ├── density-matrix.rkt
│   │   │   │   ├── pauli-spinor.rkt
│   │   │   │   └── em-vector-potential.rkt
│   │   │   ├── level-2-bo/                  (R, P, h, Π_h, Z)
│   │   │   │   ├── ion-positions.rkt
│   │   │   │   ├── ion-momenta.rkt
│   │   │   │   ├── cell-vectors.rkt
│   │   │   │   ├── cell-momentum.rkt
│   │   │   │   └── species-labels.rkt
│   │   │   ├── level-3-statistical/         aggregate intensives
│   │   │   │   ├── temperature.rkt
│   │   │   │   ├── pressure.rkt
│   │   │   │   ├── chemical-potentials.rkt
│   │   │   │   └── composition.rkt
│   │   │   └── level-4-kinetic/             emergent distributions
│   │   │       ├── carrier-distribution.rkt
│   │   │       ├── phonon-distribution.rkt
│   │   │       ├── coverages.rkt
│   │   │       └── reaction-coordinates.rkt
│   │   │
│   │   ├── canonicals/                      E[x], S[x] assembled across levels
│   │   │   ├── energy-functional/
│   │   │   │   ├── kinetic-energy.rkt
│   │   │   │   ├── born-oppenheimer.rkt     E_BO(R, h)
│   │   │   │   ├── kohn-sham.rkt            E_KS[γ̂]
│   │   │   │   ├── electromagnetic.rkt      E_EM[A]
│   │   │   │   ├── couplings/
│   │   │   │   │   ├── electron-phonon.rkt
│   │   │   │   │   ├── spin-orbit.rkt
│   │   │   │   │   ├── optical-electronic.rkt
│   │   │   │   │   └── magneto-elastic.rkt
│   │   │   │   └── total-energy.rkt         assembly: E[x] = Σ contributions
│   │   │   └── entropy-functional/
│   │   │       ├── vibrational.rkt          S_vib
│   │   │       ├── electronic.rkt           S_electronic (Fermi-Dirac)
│   │   │       ├── configurational.rkt      S_config
│   │   │       └── total-entropy.rkt        assembly: S[x] = Σ contributions
│   │   │
│   │   ├── generic/                         L, M operators
│   │   │   ├── poisson-L/
│   │   │   │   ├── symplectic-ions.rkt
│   │   │   │   ├── symplectic-cell.rkt
│   │   │   │   ├── liouville-density-matrix.rkt
│   │   │   │   ├── maxwell-em.rkt
│   │   │   │   ├── streaming-carriers.rkt
│   │   │   │   ├── streaming-phonons.rkt
│   │   │   │   └── total-L.rkt              assembly: L[x] = Σ contributions
│   │   │   └── dissipative-M/
│   │   │       ├── phonon-collisions.rkt    three-phonon + four-phonon
│   │   │       ├── electron-phonon-scattering.rkt
│   │   │       ├── gilbert-damping.rkt
│   │   │       ├── radiative-damping.rkt
│   │   │       ├── chemical-rates.rkt       master-equation symmetrized
│   │   │       └── total-M.rkt              assembly: M[x] = Σ contributions
│   │   │
│   │   ├── dynamics/                        unified GENERIC EOM
│   │   │   └── total-evolution.rkt          dx/dt = L δE/δx + M δS/δx
│   │   │
│   │   ├── methods/                         ★ COMPUTATIONAL VOCABULARY (12) ★
│   │   │   ├── state-readout.rkt
│   │   │   ├── algebraic-combination.rkt    (always invokes a NamedFormula)
│   │   │   ├── functional-differentiation.rkt
│   │   │   ├── variational-minimization.rkt
│   │   │   ├── spectral-decomposition.rkt
│   │   │   ├── spectral-aggregation.rkt
│   │   │   ├── linear-response.rkt
│   │   │   ├── path-search.rkt
│   │   │   ├── convex-optimization.rkt
│   │   │   ├── kinetic-evolution.rkt
│   │   │   ├── statistical-sampling.rkt
│   │   │   └── symmetry-projection.rkt
│   │   │
│   │   ├── abstract-properties/             ★ PARAMETRIC TEMPLATES (12) ★
│   │   │   ├── state-readout-of.rkt
│   │   │   ├── algebraic-of.rkt
│   │   │   ├── second-derivative-of.rkt
│   │   │   ├── spectrum-of.rkt
│   │   │   ├── spectral-aggregate-of.rkt
│   │   │   ├── response-of-to.rkt
│   │   │   ├── path-stationary-of.rkt
│   │   │   ├── kinetic-evolution-of.rkt
│   │   │   ├── classify-of.rkt
│   │   │   ├── comparison-of.rkt
│   │   │   ├── radiative-emission-of.rkt
│   │   │   └── microkinetic-steady-state-of.rkt
│   │   │
│   │   ├── formulas/                        ★ NAMED FORMULAS (closed, ~22) ★
│   │   │   ├── slab-arithmetic.rkt
│   │   │   ├── arrhenius.rkt
│   │   │   ├── einstein-mobility-diffusivity.rkt
│   │   │   ├── kramers-kronig-hilbert.rkt
│   │   │   ├── chen-hardness.rkt
│   │   │   ├── teter-hardness.rkt
│   │   │   ├── tian-hardness.rkt
│   │   │   ├── mazhnik-oganov-hardness.rkt
│   │   │   ├── voigt-reuss-hill-averages.rkt
│   │   │   ├── christoffel-eigenvalue.rkt
│   │   │   ├── vineyard-prefactor.rkt
│   │   │   ├── jump-diffusivity.rkt
│   │   │   ├── bose-einstein-cv.rkt
│   │   │   ├── bose-einstein-helmholtz.rkt
│   │   │   ├── fermi-dirac-helmholtz.rkt
│   │   │   ├── fermi-dirac-occupation.rkt
│   │   │   ├── formation-energy-from-references.rkt
│   │   │   ├── defect-formation-energy.rkt
│   │   │   ├── lorenz-wiedemann-franz.rkt
│   │   │   ├── linear-elasticity-stress-strain.rkt
│   │   │   ├── van-roosbroeck-shockley.rkt
│   │   │   ├── htst-rate.rkt
│   │   │   ├── turnover-frequency.rkt
│   │   │   └── current-density-from-distribution.rkt
│   │   │
│   │   ├── observables/                     concrete properties (bundled by data shape)
│   │   │   ├── bz-resolved/
│   │   │   │   ├── band-structure.rkt
│   │   │   │   ├── phonon-dispersion.rkt
│   │   │   │   ├── k-resolved-dos.rkt
│   │   │   │   └── magnon-dispersion.rkt
│   │   │   ├── energy-resolved/
│   │   │   │   ├── dos.rkt
│   │   │   │   ├── optical-absorption.rkt
│   │   │   │   ├── joint-dos.rkt
│   │   │   │   └── susceptibility-omega.rkt
│   │   │   ├── real-space/
│   │   │   │   ├── charge-density.rkt
│   │   │   │   ├── spin-density.rkt
│   │   │   │   └── electrostatic-potential.rkt
│   │   │   ├── atom-indexed/
│   │   │   │   ├── forces.rkt
│   │   │   │   ├── magnetic-moments.rkt
│   │   │   │   ├── atomic-charges.rkt
│   │   │   │   └── displacement-field.rkt
│   │   │   ├── tensor-indexed/
│   │   │   │   ├── elastic-constants.rkt
│   │   │   │   ├── conductivity-tensor.rkt
│   │   │   │   ├── thermal-conductivity-tensor.rkt
│   │   │   │   ├── thermal-expansion-tensor.rkt
│   │   │   │   └── susceptibility-tensor.rkt
│   │   │   ├── temperature-resolved/
│   │   │   │   ├── heat-capacity-T.rkt
│   │   │   │   ├── free-energy-T.rkt
│   │   │   │   └── ionic-diffusivity-T.rkt
│   │   │   ├── reaction-coord/
│   │   │   │   ├── neb-profile.rkt
│   │   │   │   └── migration-path.rkt
│   │   │   └── scalars/
│   │   │       ├── band-gap.rkt
│   │   │       ├── total-energy.rkt
│   │   │       ├── formation-energy.rkt
│   │   │       ├── surface-energy.rkt
│   │   │       ├── adsorption-energy.rkt
│   │   │       ├── bulk-modulus.rkt
│   │   │       ├── hardness.rkt
│   │   │       └── migration-barrier.rkt
│   │   │
│   │   ├── regimes/                         navigational extraction views
│   │   │   ├── electronic/                  → Level 1 + observables it produces
│   │   │   ├── optical/                     → Level 1 (γ̂ response to A)
│   │   │   ├── magnetic/                    → Level 1 (Pauli-spinor γ̂)
│   │   │   ├── structural/                  → Level 2 (E_BO critical points)
│   │   │   ├── mechanical/                  → Level 2 (2nd strain-derivatives)
│   │   │   ├── thermal/                     → Level 3 (Bose stats) + Level 4 (phonon BTE)
│   │   │   ├── thermodynamic/               → Level 3 (min F, convex hull)
│   │   │   ├── transport/                   → Level 4 (BTE on carriers)
│   │   │   └── chemical/                    → Level 4 (master eq + NEB)
│   │   │
│   │   ├── interfaces/                      cross-cutting operation interfaces
│   │   │   ├── scalar.rkt
│   │   │   ├── field-on-grid.rkt
│   │   │   ├── tensor.rkt
│   │   │   └── response.rkt
│   │   │
│   │   ├── residuals/
│   │   │   ├── eom-violation.rkt            primary
│   │   │   ├── degeneracy.rkt
│   │   │   ├── conservation/
│   │   │   │   ├── energy.rkt
│   │   │   │   ├── particle-number.rkt
│   │   │   │   ├── momentum.rkt
│   │   │   │   └── spin.rkt
│   │   │   ├── positivity/
│   │   │   │   ├── M-PSD.rkt
│   │   │   │   ├── distribution-bounds.rkt
│   │   │   │   ├── density-non-negative.rkt
│   │   │   │   ├── frequency-real.rkt
│   │   │   │   ├── conductivity-non-negative.rkt
│   │   │   │   └── spin-magnitude.rkt
│   │   │   ├── algebraic-identities/
│   │   │   │   ├── kramers-kronig.rkt
│   │   │   │   ├── f-sum.rkt
│   │   │   │   ├── acoustic-sum.rkt
│   │   │   │   ├── detailed-balance.rkt
│   │   │   │   ├── einstein-relation.rkt
│   │   │   │   ├── onsager-symmetry.rkt
│   │   │   │   ├── maxwell-relations.rkt
│   │   │   │   └── method-equivalence.rkt
│   │   │   └── total-residual.rkt
│   │   │
│   │   ├── core/                            TIER 1: math primitives, regime-agnostic
│   │   │   ├── coefficient-recurrences.rkt  (lifted from source library)
│   │   │   ├── derivative-layout.rkt        (lifted)
│   │   │   ├── basis-algebra.rkt
│   │   │   ├── mesh-integration.rkt
│   │   │   ├── tensor-algebra.rkt
│   │   │   ├── autodiff-engine.rkt
│   │   │   └── staged-code-generation.rkt   (lifted)
│   │   │
│   │   ├── shared/                          TIER 2: physical primitives, regime-shared
│   │   │   ├── pair-sum.rkt                 sum over atom pairs with PBC
│   │   │   ├── electrostatic.rkt            Ewald, etc.
│   │   │   ├── kinetic-density.rkt          T_s[ρ] for KS
│   │   │   ├── density-from-orbitals.rkt    ρ = Σ f|ψ|²
│   │   │   ├── force-from-functional.rkt    Hellmann-Feynman + Pulay
│   │   │   └── stress-from-functional.rkt   DFT stress tensor
│   │   │
│   │   ├── cert/                            FIRST-CLASS sub-tree
│   │   │   ├── certificate.rkt              schema, emitter, inert-sexpr guard
│   │   │   ├── certificate-text-renderer.rkt
│   │   │   ├── regression-freeze.rkt
│   │   │   ├── high-precision-crosscheck.rkt
│   │   │   ├── obligation-1-symmetry.rkt
│   │   │   ├── obligation-2-bounds.rkt
│   │   │   ├── obligation-3-analytic-limits.rkt
│   │   │   ├── obligation-4-reference-battery.rkt
│   │   │   ├── obligation-5-conservation.rkt
│   │   │   └── obligation-6-degeneracy.rkt
│   │   │
│   │   └── tests/                           gate-style rackunit-equivalent suites
│   │       ├── oracle-test                  reference == staged equivalence
│   │       ├── stage-test                   macro-expansion correctness
│   │       ├── method-tests/                one per method
│   │       ├── template-tests/              one per abstract template
│   │       ├── formula-tests/               one per named formula
│   │       ├── observable-tests/            one per concrete observable
│   │       ├── residual-tests/              each residual category
│   │       ├── cert-tests/                  each obligation
│   │       └── integration-stress-test.rkt
│   │
│   └── install/                             downstream pipeline placeholder
│       └── README.md
│
├── informed-operator/                       NOT designing now
└── interface/                               NOT designing now
```

---

## 15. All 36 observables as typed compositions

Every item on `properties.md` written as a one-line typed
composition. This is the validation that the architecture covers
the slide.

### 1. Structural

```
LatticeParameters       = StateReadoutOf(state.h, extractor=cell-metric-extraction)
BondLengths             = StateReadoutOf((state.R, state.h), extractor=pairwise-distance-PBC)
CrystalStructure        = ClassifyOf((state.R, state.h), classifier=space-group-detection)
Defects (energetics)    = AlgebraicOf(
                              {E_defect = canonical.E_BO(crystal-with-defect),
                               E_perfect = canonical.E_BO(reference),
                               Δn, μ = env.chem-pots, q, E_F = env.Fermi-level},
                              formula = formulas/defect-formation-energy)
Defects (characterize)  = ComparisonOf(state, reference-perfect, metric=atom-matching)
Surfaces (region)       = StateReadoutOf(state, extractor=extract-surface-region)
Surfaces (energy)       = AlgebraicOf({E_slab, E_bulk, n, A},
                              formula = formulas/slab-arithmetic)
```

### 2. Electronic

```
BandStructure   = SpectrumOf(canonical.Ĥ_KS[γ̂],
                              domain=BZMesh(nx, ny, nz))
DOS             = SpectralAggregateOf(BandStructure,
                              aggregator=delta-energy-bin,
                              weights=uniform)
BandGap         = AlgebraicOf({BandStructure},
                              formula=ε_c_min − ε_v_max)
                              (or as StateReadoutOf(BandStructure, spectral-extremum))
ChargeDensity   = StateReadoutOf(γ̂, extractor=position-diagonal-trace)
```

### 3. Optical

```
DielectricFunction = ResponseOfTo(observable=γ̂,
                                    perturbation=A-ext,
                                    kernel=current-current-correlator,
                                    frequency=ω-mesh)
Absorption(ω)      = AlgebraicOf({DielectricFunction},
                                   formula=(ω/c)·Im(√ε))
RefractiveIndex(ω) = AlgebraicOf({DielectricFunction},
                                   formula=Re(√ε))
PhotoluminescenceTrend = RadiativeEmissionOf(excited_state=γ̂-pumped,
                                               optical_coupling=dipole-d)
```

### 4. Mechanical

```
ElasticConstants = SecondDerivativeOf(F=canonical.E_BO,
                                        x₀=equilibrium-state,
                                        coord=symmetric-strain-η,
                                        metric=Frobenius²-volume-normalized)
BulkModulus      = AlgebraicOf({ElasticConstants},
                                formula=formulas/voigt-reuss-hill-averages.K)
StressStrain(linear)    = AlgebraicOf({ElasticConstants, applied-ε},
                                        formula=formulas/linear-elasticity-stress-strain)
StressStrain(nonlinear) = MapOver(strain-sequence, η ↦
                                    let relaxed = VariationalMinimization(E_BO,
                                                                            target=R,
                                                                            fixed=h(η),
                                                                            method=BFGS,
                                                                            tol=1e-4)
                                        σ(η) = FunctionalDifferentiation(E_BO,
                                                                          w.r.t.=h,
                                                                          at=relaxed)
                                                                          · h(η)ᵀ / Ω
                                    in (η, σ(η)))
Hardness(model)         = match model:
                            Chen          → AlgebraicOf({K, G},
                                              formula=formulas/chen-hardness)
                            Teter         → AlgebraicOf({G},
                                              formula=formulas/teter-hardness)
                            Tian          → AlgebraicOf({K, G},
                                              formula=formulas/tian-hardness)
                            Mazhnik-Oganov → AlgebraicOf({K, G, χ},
                                              formula=formulas/mazhnik-oganov-hardness)
```

### 5. Thermal

```
PhononDispersion = SpectrumOf(operator=dynamical-matrix(
                                             SecondDerivativeOf(E_BO, R₀, u)),
                                domain=BZMesh)
HeatCapacity(T)  = SpectralAggregateOf(PhononDispersion,
                                         aggregator=formulas/bose-einstein-cv(T),
                                         weights=uniform)
ThermalConductivity = KineticEvolutionOf(distribution=phonon-distribution(n_qν),
                                           collisions=three-phonon-anharmonic-Ψ,
                                           gradient=∇T,
                                           method=BTE-RTA)
ThermalExpansion = AlgebraicOf({ModeGrüneisen(T), HeatCapacity(T)},
                                 formula=QHA-expansion)
                   (or as MinimizationOf(F(T, h), h, method=BFGS))
```

### 6. Magnetic

```
MagneticMoments      = StateReadoutOf(γ̂, extractor=atomic-sphere-spin-integral)
SpinDensity          = StateReadoutOf(γ̂, extractor=position-diagonal-spin-trace)
ExchangeInteractions = ResponseOfTo(observable=γ̂,
                                      perturbation=infinitesimal-spin-rotation,
                                      kernel=Liechtenstein-formula,
                                      frequency=0)
```

### 7. Transport

```
ConductivityViaBTE  = KineticEvolutionOf(distribution=carrier-f_n,
                                           collisions=e-phonon-scattering-g²,
                                           gradient=applied-E-field,
                                           method=BTE-RTA,
                                           truncation=first-order)
ConductivityViaKubo = ResponseOfTo(observable=current-operator-ĵ,
                                     perturbation=A-vector-potential,
                                     kernel=current-current-correlator,
                                     frequency=ω→0+)
Conductivity        = match method-flag: BTE → ConductivityViaBTE; Kubo → ConductivityViaKubo
                      (cert obligation 6 verifies equivalence)
CarrierMobility     = AlgebraicOf({Conductivity, carrier-density},
                                    formula=μ=σ/(n·e))
IonicDiffusion(species) = let ν₀ = AlgebraicOf(
                                       {ν_min=SpectrumOf(SecondDerivativeOf(E_BO,initial,u),
                                                          normal-modes),
                                        ν_saddle=SpectrumOf(SecondDerivativeOf(E_BO,saddle,u),
                                                              normal-modes-minus-unstable)},
                                       formula=formulas/vineyard-prefactor)
                              D₀ = AlgebraicOf({a=jump-distance, Z=coord, ν₀},
                                       formula=formulas/jump-diffusivity)
                              E_a = StateReadoutOf(PathStationaryOf(E_BO, init, fin),
                                       extractor=saddle-vs-min-difference)
                          in AlgebraicOf({D₀, E_a, T}, formula=formulas/arrhenius)
MigrationBarrier = PathStationaryOf(F=canonical.E_BO,
                                      initial=species-at-site-i,
                                      final=species-at-site-j,
                                      method=NEB-climbing-image,
                                      n_images=9,
                                      tol=1e-3)
```

### 8. Thermodynamic

```
TotalEnergy     = StateReadoutOf(canonical.E[x], extractor=identity)
FormationEnergy = AlgebraicOf(
                      {E_compound = canonical.E_BO(target),
                       E_refs = {canonical.E_BO(ref) for ref in references},
                       n_i, μ_i = env.chemical-potentials},
                      formula = formulas/formation-energy-from-references)
PhaseStability  = ConvexOptimization(
                      points = {(x_φ, F_φ) for φ in candidate-phases},
                      objective = lower-convex-envelope)
FreeEnergy(T)   = AlgebraicOf(
                      {E_BO = canonical.E_BO,
                       F_vib = SpectralAggregateOf(PhononDispersion,
                                                    formulas/bose-einstein-helmholtz(T)),
                       F_el = SpectralAggregateOf(BandStructure,
                                                   formulas/fermi-dirac-helmholtz(T))},
                      formula = F = E_BO + F_vib + F_el)
```

### 9. Chemical / surface

```
AdsorptionEnergy   = AlgebraicOf(
                         {E_slab_ads = canonical.E_BO(slab + adsorbate),
                          E_slab = canonical.E_BO(slab),
                          E_mol = canonical.E_BO(isolated-molecule)},
                         formula = E_slab_ads − E_slab − E_mol)
ReactionPathway    = PathStationaryOf(F=canonical.E_BO,
                                        initial=reactant,
                                        final=product,
                                        method=NEB-climbing-image)
CatalyticActivity  = let RateNetwork = {(step,
                                           AlgebraicOf({
                                             ν₀=formulas/vineyard-prefactor(...),
                                             E_a=PathStationaryOf(...).saddle-energy,
                                             T},
                                             formula=formulas/htst-rate))
                                          for step in elementary-steps}
                         θ_steady = MicrokineticSteadyStateOf(
                                         network=RateNetwork,
                                         initial=vacuum-coverage,
                                         driving=conditions.chem-potentials,
                                         method=newton-on-ODE-fixed-point)
                     in AlgebraicOf({θ_steady, RateNetwork, RC-step},
                                     formula = formulas/turnover-frequency)
SurfaceEnergy      = AlgebraicOf(
                         {E_slab = canonical.E_BO(slab),
                          E_bulk = canonical.E_BO(bulk-per-formula-unit),
                          n = atoms-in-slab / atoms-in-bulk-formula-unit,
                          A = slab-surface-area},
                         formula = formulas/slab-arithmetic)
```

All 36 observables fit cleanly as typed compositions.

---

## 16. Implementation phases

Eleven sequential phases, each producing a verifiable artifact.

### Phase 0 — Repository scaffold

1. Initialize `_darcs/` as project VCS; keep `.git/` as bd-tracker scaffold (per `physics-library-architecture.md` lift).
2. Create `physics/` directory and the full directory tree per §14.
3. Place README.md / AGENTS.md / CLAUDE.md at the root.
4. Place per-directory README.md at every non-leaf folder.

**Artifact:** complete empty skeleton + orientation docs. `find physics/ -type d` matches §14.

### Phase 1 — Tier-1 substrate (`core/`)

5. Define numeric primitives lifted from source library:
   `coefficient-recurrences.rkt`, `derivative-layout.rkt`,
   `staged-code-generation.rkt`.
6. Implement new primitives:
   `basis-algebra.rkt`, `mesh-integration.rkt`,
   `tensor-algebra.rkt`, `autodiff-engine.rkt`.
7. Tests: `tests/core-test.rkt` validating ring axioms,
   layout consistency, autodiff against analytic reference.

**Artifact:** all of `core/` implemented and tested. Tier-1 substrate complete.

### Phase 2 — Tier-2 physical primitives (`shared/`)

8. `pair-sum.rkt`, `electrostatic.rkt` (Ewald), `kinetic-density.rkt`,
   `density-from-orbitals.rkt`, `force-from-functional.rkt`,
   `stress-from-functional.rkt`.
9. Each module: header docstring stating contract + exclusions;
   call interface declared; test against analytic limit.

**Artifact:** physical primitive library complete; ready for canonicals to assemble.

### Phase 3 — Input concepts (`inputs/`)

10. `PeriodicityStructure`, `SiteDecoration`, `Environment` typed
    constructors; serializers; readers from CIF / POSCAR-like
    formats; tests for round-trip preservation.

**Artifact:** the three top-level input types complete; system descriptions can be expressed.

### Phase 4 — Unified state (`state/`)

11. `system-state.rkt`: the unified container; enumerable, hashable.
12. Per-level state component modules (Levels 1–4).
13. `enumeration.rkt`: iterate / serialize / hash whole state.
14. Tests: round-trip enumeration, hash collision check on minor
    perturbations, lifecycle (allocate / mutate / freeze).

**Artifact:** unified state encoding complete.

### Phase 5 — Methods vocabulary (`methods/`)

15. Implement each of the 12 methods with typed signatures.
16. Each method has its own sub-method dispatch (e.g.
    `spectral-decomposition` has full-diag / Lanczos / Davidson
    sub-methods).
17. Tests per method against analytic test problems.

**Artifact:** computational vocabulary complete.

### Phase 6 — Abstract templates (`abstract-properties/`)

18. Implement each of the 12 templates. Each template is a typed
    factory that produces an Observable from typed arguments.
19. Tests: instantiate one template with several argument tuples
    and verify outputs match a hand-computed reference.

**Artifact:** parametric template machinery complete.

### Phase 7 — Named formulas registry (`formulas/`)

20. Implement each of the ~22 formulas with typed signature +
    reference citation in header.
21. Tests: each formula evaluated on a known test case from its
    cited reference paper.

**Artifact:** closed formula registry complete; algebraic combinations are no longer hand-waved.

### Phase 8 — GENERIC operators (`generic/`)

22. Implement `L` sub-brackets (symplectic ions/cell, Liouville on
    γ̂, Maxwell, semiclassical streaming). Assembly module
    `total-L.rkt`.
23. Implement `M` sub-brackets (phonon collisions, e-ph
    scattering, Gilbert, radiative, chemical rates). Assembly
    `total-M.rkt`.
24. Tests: `L^T = -L` (antisymmetry), `M ⪰ 0` (PSD), Jacobi
    identity for `L`, degeneracy conditions.

**Artifact:** GENERIC operators complete; can express any dynamics consistent with §3.

### Phase 9 — Canonicals (`canonicals/`)

25. Implement `E[x]` pieces: kinetic, BO, KS, EM, couplings, total.
26. Implement `S[x]` pieces: vibrational, electronic,
    configurational, total.
27. Tests: dimensional consistency; analytic-limit checks (free
    electron, harmonic crystal, ideal gas).

**Artifact:** canonical functionals complete; equilibria and dynamics can be set up.

### Phase 10 — Concrete observables (`observables/`)

28. Implement each of the 36 concrete observables as a one-line
    composition per §15.
29. Tests: each observable evaluated on a reference crystal
    (silicon, MgO, Fe, etc.) and checked against known values.

**Artifact:** the slide is implemented; the library can be called for any observable.

### Phase 11 — Residuals + Cert (`residuals/`, `cert/`)

30. Implement residual categories (EOM-violation, degeneracy,
    conservation, positivity, algebraic-identities, total).
31. Implement cert obligations (symmetry, bounds, analytic-limits,
    reference-battery, conservation, degeneracy).
32. Implement certificate schema, emitter, freeze fixture, tamper
    tripwire, bigfloat oracle.
33. Tests: cert run on a battery of frozen reference crystals;
    deliberate tampered case must trip tripwire; oracle agreement
    within tolerance.

**Artifact:** the library can certify its own outputs; PINO has a usable residual contract.

### Phase 12 — Dynamics + integration validation

34. Implement `dynamics/total-evolution.rkt`: assembles `L`, `M`,
    `δE/δx`, `δS/δx` into the unified RHS.
35. Validate against known dynamics: harmonic-oscillator phase
    space, two-level system Rabi oscillation, ideal-gas Boltzmann
    relaxation.

**Artifact:** unified dynamics callable; can hand RHS to any integrator.

### Phase 13 — API seal and examples

36. `main.rkt` / `api.rkt`: the single typed seal. All public
    types and functions cross through `require/typed` (or
    language-equivalent) with `#:opaque` on internal datatypes.
37. `examples.rkt`: end-to-end worked example runners (e.g.
    "compute elastic constants of silicon").
38. `demo.ipynb`: end-to-end notebook tour for outside readers.

**Artifact:** the library is shippable; downstream consumers
(`/informed-operator`, `/interface`) can begin building against
it.

---

## 17. Deferred decisions

The following are *deliberately* deferred from this plan. They
should be addressed in their own focused design discussions before
the corresponding phase.

1. **Implementation language.** Racket (matches source library
   exactly; native macro staging) vs. ML-stack (Python / JAX /
   PyTorch — better tensor + autograd ergonomics). Affects how
   `methods/` and `abstract-properties/` are implemented but not
   the architecture above. **Blocks Phase 1.**
2. **Internal layout of each state component.** Pauli-spinor `γ̂`
   representation (real basis vs. spinor pair); ion phase-space
   packing (interleaved vs. struct-of-arrays); EM gauge choice.
   **Blocks Phase 4.**
3. **Macro grammar.** `derive-residual`, `derive-update`,
   `derive-readout` signatures and their derivation-spec
   vocabularies. **Blocks Phase 5.**
4. **Integrator interface.** Exact signature `/physics/dynamics/`
   exposes to `/informed-operator`. **Blocks Phase 13.**
5. **Coupling grammar.** How cross-regime terms in `E_coupling`
   and in `L`/`M` are declared and composed. **Blocks Phase 8 + 9.**
6. **Start order.** One regime end-to-end (Structural, simplest)
   or shared substrate first (Phases 1–7 before any concrete
   observable). My recommendation: **shared substrate first**
   — the source library's discipline. **Determines Phase
   ordering.**

---

## 18. Verification of this plan

The plan is internally consistent when:

1. Every observable in §15 invokes only methods listed in §7,
   templates in §8, and formulas in §9.
2. Every method/template/formula has a typed signature with no
   string-encoded parameters.
3. The directory tree in §14 contains every concept named in §3–§13.
4. The 9 regimes' extractions in §3.5 are realizable as the
   observable compositions in §15.
5. Every residual category in §12 is grounded in a GENERIC
   identity or a named formula from §9.
6. Every cert obligation in §13 corresponds to a residual category
   or an algebraic identity.

The verification can be carried out mechanically once the
skeleton is in place (Phase 0): walk the file tree and confirm
cross-references.

---

## 19. ResidualGenerator factory

**(Source: `physics/research/amendment-s7-source.md` §11; surfaced by S5, typed by S6.)**

The missing architectural piece prior to the amendment. `/physics` had residual *categories* but no *machinery* for generating a residual from an arbitrary observable composition. The factory closes that gap.

```
record ResidualGenerator {
  name              : Symbol
  observable        : ObservableRef
  bundle            : BundleId               -- one of B1-B11
  layer             : 1..7                   -- DAG layer; see dependency ordering
  cost-tier         : T0 | T1 | T2 | T3      -- per-step / per-batch / per-epoch / on-demand
  diff-tag          : D0 | D1 | D2 | D3 | D4 -- closed-form / autodiff / adjoint / FD / relaxed
  source-tag        : cheap-generate | faithful-residual | ground-truth-bridge | cert-only
  dressing-tag      : bare | dressed(scheme: SCP|SSCHA|GW|BSE|polaron, cert: OneShotCert|IterativeResult, T: Temperature)
                      -- γ' addition: residuals from bare-KS and G₀W₀-dressed paths disagree by
                         ~30% on diamond and CANNOT be averaged; multi-source training discipline
                         (§21) requires explicit dressing-tag exposure so the loop can per-tag
                         the loss instead of mixing. See §27 for OneShotCert/IterativeResult.
  applicability     : (Crystal, Env) → Bool  -- per-sample masking (see §26)
  input-contract    : List<TypedSlot>
  output-contract   : TypedSlot
  forward           : Inputs → Output
  backward          : Inputs × Output × Cotangent → Cotangent  -- required iff D2
  loss              : Output → Scalar
  weight-policy     : GradNormGroup | NTKInit | Fixed | CurriculumStaged
  sampling-policy   : UniformBatch | RAD(τ) | Importance | ValidationOnly
  dependencies      : Set<Symbol>            -- same-pass fixed-point co-convergence
  adjoint-cert      : Passed | Failed(witness) | NotApplicable | Relaxed(rationale)
  registration-time : Timestamp
  registration-hash : Sha256                 -- for cert-tripwire detection
}
```

**Factory:**
```
make-residual-generator(observable, path, distance, weight-policy, sampling-policy, source-tag, applicability)
  → ResidualGenerator
```

**Registration-time adjoint validation gate (hard).** D2 entries run vJp vs JvP check on N=64 sample points; max relative error > τ_adj fails the build. Forces honest gradient implementations or explicit downgrade to D3/D4 with rationale.

Full type definitions, training-loop consumption pattern, and tag-driven scheduling in `amendment-s7-source.md` §11. The 87-entry registry manifest is at `physics/library/formulas/registry-manifest.csv`.


## 20. PINO integration: three exports

**(Source: `amendment-s7-source.md` §12; aligns with the `prompt.md`-clarified scope of `/physics`.)**

`/physics` exposes exactly three typed surfaces to `/informed-operator`:

| Export | Direction | Autodiff? | Purpose |
|---|---|---|---|
| **Generate** | `/physics → /informed-operator` | NO (pre-compute) | Approximate training labels via cheap-compute path |
| **Validate** | `/informed-operator → /physics` | YES (backprop) | Compare predictions to faithful-residual path; emit per-residual loss + gradients + cert evidence |
| **Import** | external → `/physics` | NO | Ingest VASP ground-truth + experimental data as `TargetEntry`s with `(value, σ, provenance, coverage-mask)` |

Sealed at `pino-bridge/api.rkt` (or language equivalent). Full signatures + handshake protocol in `amendment-s7-source.md` §12.


## 21. Multi-source training discipline

**(Source: S5 methodology, formalized in `amendment-s7-source.md` §13.)**

The PINO trains on FOUR supervisory sources simultaneously: (a) cheap-generated labels, (b) VASP ground-truth, (c) experimental measurements, (d) `/physics` residuals.

**Four-phase curriculum** (defaults — knobs in `amendment-s7-source.md` §21.7):

| Phase | Fraction | Active |
|---|---|---|
| Warmup | 0.00 – 0.10 | cheap-generate targets + D0/D1 faithful-residual; no T2/T3 |
| Refine | 0.10 – 0.60 | full D1/D2 faithful; GradNorm-balanced T0/T1; experimental targets enter |
| Calibrate | 0.60 – 0.90 | + D3 implicit-function residuals; L3↔L5 same-pass fixed-point activated; T2 on RAD-sampled minibatches |
| Polish | 0.90 – 1.00 | + D4 surrogate-net residuals; T3 validation triggers periodic; obligation-9 cert per epoch |

**Outer balancing:** GradNorm across `{cheap-generate-targets, faithful-residual, ground-truth-bridge}` (3-task or 4-task depending on coverage).

**Inner balancing (within faithful-residual):** NTK-initialized fixed weights, frozen after init.

**Experimental terms:** Huber loss with per-observable σ from `TargetEntry`; transition at 1.345σ.

**Sampling:** T0 uniform always-on; T1 RAD-adaptive; T2 curriculum-gated; T3 validation-only never-in-gradient.

**Coverage-mask discipline:** every `TargetEntry` carries a per-observable bitmask; loss respects mask per-sample. The applicability classifier (§26) extends this per-property.


## 22. Out-of-scope declarations

**(Source: S1's 12 limits + S6's 5 honest gaps; full table in `amendment-s7-source.md` §14.)**

Excluded explicitly so the architecture is honest about what it does NOT cover:

1. Strongly-correlated systems (frustrated Wigner, Mott insulators, heavy-fermion) — DFT-KS closure inadequate
2. Flexoelectricity in centrosymmetric materials — below numerical-noise floor; order-of-magnitude only
3. Magneto-thermal coupling in heavy contact metals (W, Ir, Pt) — formally in S, not modeled
4. Deep-defect non-Markovian dynamics — Markov master-equation closure assumed
5. Polaron localization beyond Fröhlich — large-polaron self-consistent treatment not modeled
6. 4-phonon scattering — replaced by `four-phonon-correction-learned` (D4 surrogate)
7. Full NEGF tunneling — replaced by `negf-tunneling-surrogate` (D4); proxies Padovani-Stratton + Fowler-Nordheim
8. Full SCPH / SSCHA — `scph-renormalization-periodic` (D4), periodic refresh between curriculum phases
9. Plasma-process surface damage — out of substrate-agnostic remit
10. Grain-boundary statistics — single-crystal or explicit bicrystal input required
11. Continuum creep / dislocation climb — out of GENERIC elastic regime
12. Quantum-tunneling-corrected reaction rates — classical Eyring TST adequate at T_op ≥ 600 K

Predict raises `out-of-scope` with witness for any of these; cert obligation-3 (analytic limits) flags suspect.


## 23. Outstanding decisions for user

**(Source: `amendment-s7-source.md` §15. Ordered by urgency.)**

1. **Implementation language (BLOCKS Phase 1).** Default recommendation: Python + JAX (autodiff + GPU + NTK/GradNorm ecosystem). Julia (Owl, Zygote, Enzyme) is a viable alternative. Racket retains the source library's macro discipline but lacks autodiff support for D2 entries.
2. **ReferenceCache backend (BLOCKS Phase 2 + 7).** Default: SQLite + SHA-pinned content-addressed schema.
3. **Surrogate-net infrastructure: build vs adopt (BLOCKS Polish phase).** Needed for 5 D4 entries.
4. **PDE-mesh format + adjoint library (BLOCKS Calibrate phase).** FEniCS+dolfin-adjoint / Firedrake+pyadjoint / JAX-FEM / custom finite-volume in JAX.
5. **Coverage-mask format (BLOCKS Phase 10/11 + Import).** Default: sparse representation from V1 to avoid rewrite.
6. **Curriculum schedule defaults** (0.10, 0.60, 0.90) — confirmable.
7. **Active-learning loop integration timing** — default: lives in `/interface`, not `/physics`.


## 24. Verification plan

**(Source: `amendment-s7-source.md` §16. Five sequential gates.)**

1. **Registration sanity:** 87 ResidualGenerator records instantiate without registration-time error. D2 entries pass adjoint validation gate. D4 entries carry obligation-9 rationale.
2. **Worked-example end-to-end:** Diamond-W-Schottky-500°C scenario (S6 §6) — 37 residual firings across 7 DAG layers, L3↔L5 cycle closes via same-pass fixed point in ≤5 iterations. Total ≤T2 budget.
3. **Curriculum sanity on synthetic problem:** 4-phase run on Si-bulk with ~5 observables, 1k samples — no GradNorm divergence, no Layer-3↔5 fixed-point failures, no adjoint-cert resets mid-training.
4. **Cross-regime cert obligations fire correctly:** obligations 6, 9, 10 all observable, including deliberate negative-test cases (D4 query outside domain trips obligation-9; synthetic D2-adjoint-failure formula refuses registration).
5. **`/informed-operator` integration smoke test:** Generate populates 10 Si observables; Validate produces finite loss + finite gradients of declared shape; Import accepts synthetic VASP-formatted payload with TargetEntry records.


## 25. Post-amendment migration plan

**(Source: `amendment-s7-source.md` §17. EXECUTED. See git log for the commit.)**

Status: this amendment landed in commit `<commit-hash>` titled "S1-S7 research integration; UWBG retargeting amendment; applicability-classifier addition". All 22 user-listed migration targets migrated; conductor working memory (`~/.claude/plans/resilient-stirring-horizon.md`) retains the topology-integration addendum pending separate research session (task #9 INTEGRATION NEEDED).


## 26. Applicability classifiers

**(Source: post-S7 user addition; full stub at `physics/research/applicability-classifiers.md`.)**

Every property, observable, and residual in the closed registries carries a typed predicate:

```
applicability : (Crystal, Environment) → Bool
```

PINO loss machinery masks per-sample: properties that don't apply (e.g., predicting band gap for a metal; predicting Schottky barrier for a homogeneous bulk crystal) don't contribute to gradient updates. This is what makes the architecture *compositional across crystal types*.

Examples:
- Band gap: `is-insulator-or-semiconductor(Crystal)`
- Magnetic moment per site: `has-magnetic-order(Crystal)`
- Schottky barrier: `has-metal-semiconductor-interface(Crystal)`
- Defect formation energy for species X: `defect-species-meaningful(X, Crystal)`
- Superconducting Tc: `is-superconductor(Crystal)`
- Polar-optical phonon scattering: `is-polar-material(Crystal)` (false for diamond)
- Carbide formation rate at interface: `interface-includes-carbide-former(Crystal)` (false for Pt/diamond)

The `ResidualGenerator` record (§19) carries an `applicability` slot wired into the factory at registration time.

**V1 commitment:** every formula registry entry, every observable bundle entry, every applicable cert obligation gets an explicit `applicability` field. Stub predicates (always-true) are acceptable for V1.0; refinement is incremental.

Open design questions on soft vs hard classifiers, classifier composition, and trajectory-aware evaluation in `physics/research/applicability-classifiers.md`.


---

End of amendment. Original plan §1–§18 stands. §19–§26 supersede or extend per amendment status banner at top of file.


## 27. Alternative D — Layer 1.25 / Layer 1.75 split (canonical)

**(Source: validator-1 + validator-2 mesh discussion; locked in this revision as the canonical architectural decision on renormalization placement.)**

The originally proposed "Layer 1.5 renormalization layer" (one undifferentiated layer absorbing SCPH, SSCHA, GW, BSE, DMFT, polaron) was rejected. Validator-2's critique stands: BSE is not iterated in the same sense as SCPH; polaron is mostly closed-form; the "all share fixed-point structure" framing was an over-elegant rationalization. Instead:

### Layer 1.25 — One-shot dressing (V1 scope)

Single-pass corrections applied to a bare Layer 1 substrate to produce a *dressed* quantity used by Layer 2 downstream. No iteration. Each entry produces an explicit `OneShotCert` carrying provenance.

```
record OneShotCert {
  scheme              : G0W0 | SCP-perturbative | LO-TO-NA-correction
                      | Born-charge-DFPT | epsilon-infinity-DFPT
  inputs-hash         : Sha256                  -- bare-substrate inputs frozen
  parameters          : Map<Symbol, Value>      -- e.g. k-mesh, cutoff
  output              : DressedQuantity
  one-shot-residual   : Scalar                  -- single-pass closure check
  cost-tier           : T1 | T2
  emitted-at          : Timestamp
}
```

**Layer 1.25 V1 members:** G₀W₀ quasi-particle energies, perturbative SCP (lowest-order), DFPT linear-response sub-stage (produces Z\*, ε∞, χ^∞ — the L1 primitives at registry rows 92–94), LO/TO non-analytic correction (uses Z\* and ε∞).

### Layer 1.75 — Iterative dressing (V2 scope, specified for forward compatibility)

Genuinely self-consistent fixed-point procedures. Specified but **deferred to V2**; the cert vocabulary below is reserved so that a V2 contributor can implement scGW or DMFT without re-litigating the architecture.

```
record IterativeResult {
  scheme              : scGW | SSCHA-stochastic | TDEP | BSE-iterated
                      | DMFT | polaron-self-consistent
  inputs-hash         : Sha256
  parameters          : Map<Symbol, Value>      -- mixing, broadening, max-iter
  trajectory          : List<IterationSnapshot> -- per-iteration residual, energy
  converged?          : true | false
  divergence-witness  : Optional<Witness>       -- non-null iff converged? = false
  final               : DressedQuantity
  cost-tier           : T3
  emitted-at          : Timestamp
}
```

**Layer 1.75 V2-deferred members:** self-consistent GW (scGW), full SCPH / SSCHA stochastic, DMFT, BSE iterative variants, self-consistent Migdal polaron.

**Discipline:** V1 ships with Layer 1.25 wired; Layer 1.75 ships as type/cert scaffolding only with `not-implemented-in-V1` stubs that fail loudly. The architecture is forward-compatible without paying V2 cost in V1.

### Integration with §19 ResidualGenerator

The `dressing-tag` slot on `ResidualGenerator` (added in §19) carries either `bare`, `dressed(scheme, OneShotCert, T)`, or `dressed(scheme, IterativeResult, T)`. The training loop (§21) per-tags loss contributions; bare and G₀W₀-dressed residuals on the same observable are tracked as **separate residuals**, never averaged.

### Path γ' validation summary

What validator-1 got right (now canonical):
- Wegscheider cycle-basis reduction is a *technique* within `KineticEvolutionOf`, not a new formula entry
- SCP/SSCHA belong under a template (`SelfConsistentRenormalizationOf`) with method selector, not as 3 separate formulas
- The pattern "audit-flagged 'missing formula' often resolves to a thinly-specified Layer 1 sub-stage exposing a derived primitive" generalizes

What validator-1 got wrong (corrected here):
- LO/TO is a real Layer 2 formula entry (row 88), not "automatic from a richer L1" — the q→0 directional limit is a load-bearing cert obligation
- MP / FNV / LZ / Kumagai-Oba are physically distinct correction methods; the strategy-pattern dispatcher lives in `methods/`, formulas stay separate
- Redlich-Kister is NOT a cluster-expansion instance; both live as separate parameterizations of `ConfigurationalFreeEnergyOf`
- Layer 1 primitives Z\*, ε∞, χ^∞ are registered (rows 92–94) rather than left implicit

### Out-of-scope confirmation (extends §22)

- True self-consistent GW, full SSCHA, DMFT, BSE iterative variants: V2, scaffolded only in V1
- Strong correlation (Mott, frustrated Wigner, spin liquids): out of scope per §22; the L1 substrate remains mean-field
- The 30% bare-vs-dressed disagreement on diamond is *expected* and is what motivates `dressing-tag`; it is not a bug to be averaged away
