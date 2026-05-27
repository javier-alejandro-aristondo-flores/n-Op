# Plan: `/physics` — research-grounded unified state-and-dynamics encoding

## Context

The repository `~/Desktop/Physics/Programs/n-Op/` is the start of
**n-Op**: a physically-informed neural operator (PINO) that learns
**how a multiphysics system evolves over time** inside a fixed
crystal. The system's state at any instant is the simultaneous
manifestation of all nine regimes from `properties.md`.

We are designing the **`/physics`** sibling of n-Op:

```
n-Op/
├── physics/             ← we are designing THIS
├── informed-operator/   ← the PINO; consumes /physics; learns state evolution
└── interface/           ← user-facing surface
```

Architectural style lifted from
`~/Desktop/Physics/Library/physics/`. Architecture is grounded in
deep mathematical research dispatched to three parallel agents (one
per group of three regimes); their full reports are staged in their
agent plan files at:
- `~/.claude/plans/please-read-the-slide-humble-sunrise-agent-aadb3b52151528703.md` (Group A: ion dynamics)
- `~/.claude/plans/please-read-the-slide-humble-sunrise-agent-afe4343cb8dc41820.md` (Group B: electronic / magnetic / optical)
- `~/.claude/plans/please-read-the-slide-humble-sunrise-agent-a93a9efd61c535537.md` (Group C: transport / thermodynamic / chemical)
On execution, write these to `n-Op/research/group-{A,B,C}-*.md`.

## Research re-organized: 4-level BO hierarchy (replacing A/B/C dispatching groups)

The dispatching groups (A=ions, B=electronic, C=non-equilibrium)
were artifacts of parallelization. The math suggests a natural
**four-level hierarchy** where each level coarse-grains the previous.

### Level 1 — Quantum electronic substrate
- Operates on `γ̂(r, r'; t)` (Pauli-spinor 1-body density matrix)
  for fixed nuclei (R, h)
- Regimes: ELECTRONIC, OPTICAL, MAGNETIC
- Math: KS / TDKS / TDCSDFT; HK theorem; variational on γ̂;
  Liouville–von Neumann; Runge–Gross
- Irreducible: `γ̂`, `A(r, t)` for EM coupling

### Level 2 — Born–Oppenheimer surface
- Operates on `E_BO(R, h)` derived from Level 1 (min over γ̂)
- Regimes: STRUCTURAL, MECHANICAL
- Math: variational on (R, h); derivatives of `E_BO`;
  Hellmann–Feynman; strain expansion; Parrinello–Rahman dynamics
- Irreducible: `(R_I, P_I, h, Π_h)` — ion phase space

### Level 3 — Equilibrium statistics on the BO surface
- Bose–Einstein, Fermi–Dirac, Maxwell–Boltzmann over Levels 1 + 2
- Regimes: THERMAL, THERMODYNAMIC
- Math: partition functions, free energies, QHA, SCP, convex hull,
  Lyapunov gradient flow
- Irreducible: spectral data + aggregate `T, P, μ, x_i, c_φ`

### Level 4 — Non-equilibrium kinetics
- Distributions over phase space; full GENERIC `L + M`
- Regimes: TRANSPORT, CHEMICAL/SURFACE
- Math: Boltzmann transport; Kubo / Green-Kubo; GENERIC; master
  equation; Marcus; TST; NEB
- Irreducible: emergent distributions `f_n`, `n_{qs}`, coverages
  `θ_i`, coordinates `ξ`

Each level uses lower levels as inputs but introduces its own
irreducible state. Dependency goes strictly upward.

### Two orthogonal axes that cross-cut the hierarchy

- **By GENERIC role**: pure-L (Level 1 TDKS, Level 2 MD),
  pure-M (Level 3 gradient flow, Level 4 master eq), full GENERIC
  (Level 4 BTE, magnetic LLG, optical with damping)
- **By derivation tier**: direct readout / 1-jet / 2-jet /
  spectral / spectral integrals / response / Kubo bilinears

### Research compilation organized around the hierarchy

```
research/
├── level-1-electronic-substrate.md     (electronic, optical, magnetic)
├── level-2-born-oppenheimer-surface.md (structural, mechanical)
├── level-3-equilibrium-statistics.md   (thermal, thermodynamic)
├── level-4-nonequilibrium-kinetics.md  (transport, chemical)
└── synthesis.md                         (GENERIC over unified state across levels)
```

(The previous A/B/C agent reports remain accessible in their plan
files; they will be re-cut and merged into the four level documents.)

## Level 2 — fleshed out (template for the layering pattern)

User requested validation of the layering on one concrete level
before committing to all four. Picked **Level 2 — BO surface**
(structural + mechanical regimes) because it's the most concrete
and most directly inherits the source library's machinery.

### Scope
- Operates on configuration-and-cell manifold `Q = {(R_I, h)}`
- Functional: `E_BO(R, h)` derived from Level 1 + kinetic energy
- Regimes: STRUCTURAL, MECHANICAL

### Level 2 irreducible state
```
(R_I, P_I, h, Π_h, {Z_I})    Parrinello-Rahman phase space
```
Dim: `6N + 18` reals + N discrete species labels. Constraint
`det h > 0`. `γ̂` is NOT Level-2 state; it's evaluated by calling
Level 1 at each `(R, h)`.

### Level 2 canonical contributions
```
E₂[x] = E_kin(P, Π_h) + E_BO(R, h)
S₂[x] = 0                            (no stats at this level)
```

### Level 2 GENERIC pieces
```
L₂ = Parrinello-Rahman Poisson bracket on (R, P, h, Π_h)
M₂ = 0                               (no dissipation at this level)
```

### Level 2 dynamics
```
dR/dt = P/M,  dP/dt = F = -∇_R E_BO        (Hellmann-Feynman via Level 1 call)
dh/dt = Π_h/W,  dΠ_h/dt = -Ω σ h^{-T}      (Level 1 stress)
```

### Level 2 residuals
EOM violation; force balance; torque balance; energy conservation;
stress symmetry (Cauchy); Born stability; space-group equivariance;
symplectic preservation.

### Level 2 observables (with destination bundle)

| Observable | Source | Bundle |
|------------|--------|--------|
| Lattice params | h | scalars |
| Bond lengths | (R, h) | scalars |
| Volume | det h | scalars |
| Forces | −∂E_BO/∂R | atom-indexed |
| Stress | −(1/Ω)∂E_BO/∂h | tensor-indexed |
| Elastic constants | (1/Ω)∂²E_BO/∂η² | tensor-indexed |
| Moduli K, G, E, ν | aggregates of C | scalars |
| Sound velocities | Christoffel(C) | scalars |
| Space group | symmetry analysis | scalars |
| Surface / adsorption / formation energies | slab arithmetic | scalars |

### Level 2 couplings

- **Down to Level 1**: every `E_BO`, `F_I`, `σ` evaluation calls L1
- **Up to Level 3**: provides Hessian Φ for D(q) → phonon stats
- **Up to Level 4**: provides BO surface for NEB; forces for MD

### Level 2 directory layout

```
library/level-2-bo-surface/
├── README.md
├── state/{ion-positions, ion-momenta, cell-vectors, cell-momentum, species-labels}
├── canonical/{kinetic-energy, born-oppenheimer-energy}
├── poisson-L/{symplectic-ions, symplectic-cell, combined}
├── readouts/{geometry/, forces, stress, elastic-constants, moduli, sound-velocities,
│            symmetry-analysis, surface-energy, adsorption-energy, formation-energy}
├── residuals/{force-balance, torque-balance, energy-conservation, stress-symmetry,
│              born-stability, space-group-equivariance, symplectic-preservation}
└── dynamics/parrinello-rahman-EOM
```

### Worked-example flow (compute ElasticConstants end-to-end)

Strain → relax R at fixed h(η) [Level-2 dynamics + Level-1 calls]
→ tabulate E_BO(η) → fit polynomial → extract C_IJ → symmetrize
→ project onto point group → emit as tensor-indexed observable +
Born-stability cert + residual contribution.

### Universal observable pattern (validated by Level 2)

```
USE  this level's state →
CALL lower levels for derived inputs →
APPLY this level's dynamics if needed →
PRODUCE result in shared observable bundle →
CONTRIBUTE residuals to PINO loss →
EMIT cert obligations
```

### What this validates about the layering
- Each level owns its irreducible state pieces
- Each level's canonical contributions are additive
- Each level's GENERIC pieces (L, M) are additive (M₂=0 is fine)
- Each level populates shared observable bundles (data-shape axis)
- Each level adds residual contributions to unified contract
- Cross-level calls are strictly downward (L4 → L3 → L2 → L1)

Pattern should generalize to Levels 1, 3, 4.

## Bigger reframe (user-stated): sort by computational method

> "I want the structure to be sorted by computational method of
> representation. So we can easily compose and/or [de]compose
> between properties into an abstract property. So to work towards
> a unified representation."

The PRIMARY organizing axis is now computational method, not BO
hierarchy. Hierarchy still organizes state / canonicals / dynamics;
methods organize how observables are computed.

### Computational vocabulary (~12 methods, closed set)

- state-readout
- algebraic-combination
- functional-differentiation (gradient, hessian, higher)
- variational-minimization (SD, CG, BFGS, FIRE, Newton, SCF)
- spectral-decomposition (full diag, Lanczos, Davidson)
- spectral-aggregation (DOS, partition function, thermal average,
  occupation sum)
- linear-response (Kubo, LR-DFT, Green's function)
- path-search (NEB, dimer, TST)
- convex-optimization (convex hull, QP)
- kinetic-evolution (BTE, master, drift-diffusion, Cahn-Hilliard)
- statistical-sampling (MC, MD, kMC)
- symmetry-projection (point, space, time-reversal)

### Observables as method compositions

Every observable is a chain. Examples:

```
ElasticConstants    = symmetry-projection ∘ hessian-w.r.t.-η ∘ relax ∘ E_BO
BandStructure       = spectral-decomposition ∘ Ĥ_KS[γ̂]
DOS                 = spectral-aggregation/δ-sum ∘ BandStructure
BandGap             = state-readout/extremum ∘ DOS
FreeEnergy(T)       = spectral-aggregation/log-Z(T) ∘ phonon-eigenvalues
ConductivityTensor  = linear-response/Kubo ∘ velocity-op ∘ BandStructure
MigrationBarrier    = state-readout/extremum ∘ path-search/NEB ∘ E_BO
SurfaceEnergy       = algebraic-combination/slab-arithmetic ∘ E_BO
PhaseStability      = convex-optimization/hull ∘ {FreeEnergy_φ}
```

### Abstract properties as parametric method templates

```
SecondDerivativeOf(F, x₀, coord)            → ElasticConstants, ForceConstants, PolarSusceptibility
SpectralAggregateOf(Op, aggregator)          → DOS, PhononDOS, HeatCapacity, FreeEnergy
ResponseOfTo(component, perturbation)        → DielectricFunction, Conductivity(ω), Susceptibility
PathStationaryOf(F, initial, final)          → MigrationBarrier, ReactionPathway
KineticEvolutionOf(dist, collision, grad)    → ElectronicConductivity, ThermalConductivity, IonicDiffusivity
AlgebraicOf({inputs}, formula)               → FormationEnergy, SurfaceEnergy, AdsorptionEnergy
StatisticalAggregateOf(distribution, weight) → Cv(T), F(T), thermal averages
```

One template, many instances. Properties unify into the method
algebra.

### Architecture (methods/abstract-properties as primary axis)

```
library/
├── state/                 sub-organized by BO level (where DOFs live)
├── canonicals/            E, S; per-level contributions assembled into totals
├── generic/               L, M; per-level contributions assembled into totals
├── dynamics/              unified GENERIC EOM
│
├── methods/               ★ COMPUTATIONAL VOCABULARY ★
│   ├── state-readout
│   ├── algebraic-combination
│   ├── functional-differentiation
│   ├── variational-minimization
│   ├── spectral-decomposition
│   ├── spectral-aggregation
│   ├── linear-response
│   ├── path-search
│   ├── convex-optimization
│   ├── kinetic-evolution
│   ├── statistical-sampling
│   └── symmetry-projection
│
├── abstract-properties/   ★ PARAMETRIC METHOD-CHAIN TEMPLATES ★
│   ├── second-derivative-of
│   ├── spectral-aggregate-of
│   ├── response-of-to
│   ├── path-stationary-of
│   ├── kinetic-evolution-of
│   ├── algebraic-of
│   └── statistical-aggregate-of
│
├── observables/           concrete properties (bundled by data shape)
├── residuals/             method-aware loss terms
├── interfaces/, core/, shared/, cert/
```

### What this unifies

- Shared subcomputations are explicit in composition (DOS and
  BandGap share BandStructure)
- Three "second-derivative" observables collapse to ONE template +
  three argument tuples
- New observables = one-line additions instantiating a template
- Residuals can target "every observable using method X" instead
  of per-regime files
- The neural operator's outputs match the library's compositional
  structure

## Validation against the full slide (all 36 observables)

Walked every item in properties.md as a method composition. Results:

### Clean fits with original 7 templates (~25/36)

All of regime 2, 5, 6, 8; most of 3, 4, 7, 9; geometric items in 1.

### Stretched but workable (~7/36)

- 4.3 Nonlinear stress-strain — path-integration over strain-space
- 4.4 Hardness trends — empirical correlations via AlgebraicOf
- 7.2 Ionic diffusion (Arrhenius) — simple AlgebraicOf hides derivation
- 7.3 Conductivity has TWO valid compositions (BTE + Kubo)

### Vocabulary gaps → 5 new abstract templates

- **ClassifyOf(object, classifier)** — discrete labels (space group,
  Wyckoff, crystal-structure class) — used by 1.3
- **ComparisonOf(target, reference, metric)** — structural
  differences — used by 1.4 (defects), 1.5 (surfaces)
- **SpectrumOf(operator, parametric-domain)** — bands, phonons,
  magnons (parametric spectrum) — used by 2.1, 5.1, magnon
- **RadiativeEmissionOf(excited-state, optical-coupling)** —
  photoluminescence — used by 3.4
- **MicrokineticSteadyStateOf(rate-network)** — catalytic activity
  from rate network — used by 9.3

### Final abstract-property vocabulary (12 templates)

```
abstract-properties/
├── state-readout-of/             ★
├── algebraic-of/                  ★
├── second-derivative-of/         ★
├── spectrum-of/                  NEW
├── spectral-aggregate-of/         ★
├── response-of-to/                ★
├── path-stationary-of/            ★
├── kinetic-evolution-of/          ★
├── classify-of/                  NEW
├── comparison-of/                NEW
├── radiative-emission-of/        NEW
└── microkinetic-steady-state-of/ NEW
```

### What the validation showed

- ~70% fit cleanly; compositional discipline holds
- ~20% stretched but use existing methods
- ~10% needed new templates, all physically meaningful in own right
- 2 observables have multiple equivalent compositions (BTE/Kubo for
  conductivity; QHA/min-F for thermal expansion) — cert layer
  verifies equivalence on equilibrium states

## Concrete parameterization discipline (user-stated)

> "We need to be concrete with parameterizations, not so loose
> and stretched."

Every method, template, formula has a TYPED signature with explicit
parameters. No string formulas. No implicit / optional / hand-waved
arguments. Library refuses untyped instantiations.

### New `formulas/` folder

Named concrete algebraic formulas with typed inputs → output.
Closed registry (~20 for the materials-physics scope on the slide).
Each independently verifiable against published references via cert.

```
formulas/
├── slab-arithmetic                  (slab-E, bulk-E, n, A) → real
├── arrhenius                        (D₀, E_a, T) → real
├── einstein-mobility-diffusivity    (μ, T, q) → real
├── kramers-kronig-hilbert           (Im_ε: Field[ω → ℝ]) → Field[ω → ℝ]
├── chen-hardness                    (K, G) → real
├── teter-hardness                   (G) → real
├── tian-hardness                    (K, G) → real
├── mazhnik-oganov-hardness          (K, G, χ_electroneg) → real
├── voigt-reuss-hill-averages        (C_IJ) → (K, G)
├── christoffel-eigenvalue           (C, q̂, ρ) → sound-speed
├── vineyard-prefactor               (ν_min, ν_saddle) → real
├── jump-diffusivity                 (a, Z, ν₀) → D₀
├── bose-einstein-cv                 (ω, T) → real
├── bose-einstein-helmholtz          (ω, T) → real
├── fermi-dirac-helmholtz            (ε, μ, T) → real
├── formation-energy-from-references ({E_compound, {E_refs}, {n_i}, {μ_i}}) → real
├── lorenz-wiedemann-franz           (σ, T) → κ_el
├── linear-elasticity-stress-strain  (C, ε) → σ
├── van-roosbroeck-shockley          (α(ω), T) → PL(ω)
├── htst-rate                        (ν₀, E_a, T) → rate
├── defect-formation-energy          (E_defect, E_perfect, Δn, μ, q, E_F) → real
├── turnover-frequency               (θ_steady, network, RC-step) → real
└── current-density-from-distribution (δf, group-vel) → j-vector
```

### 7 stretched cases now concrete

All 7 cases that previously stretched now decompose into typed
chains ending in named formulas. Example chains shown above for:
- nonlinear stress-strain
- hardness (with model: enum)
- ionic diffusion (full Arrhenius chain via Vineyard)
- conductivity (BTE + Kubo, both fully typed + cert equivalence)
- catalytic activity (RateNetwork → microkinetic steady state → TOF)
- defect formation (Zhang–Northrup formula)
- surface energy (slab arithmetic)

All 36 observables now fit cleanly as typed, fully-parameterized
method compositions.

### Typed-signature pattern

Every method / template / formula:

```
Name(
    explicit-typed-parameters: with types and defaults
) → TypedOutput
```

No optional / implicit / string-encoded params. Library refuses
untyped instantiations at load time.

The PINO consumes the same typed instantiations — when it predicts
an observable, it knows exactly which parameterization produced
the training label, and the residual loss uses the same typed
parameters.

## The grand unification — GENERIC over a unified state

The three groups combine into ONE structure: GENERIC dynamics on a
unified system state.

### Unified state (irreducible DOFs)

```
x(t) = ( h(t),                 cell vectors                           [Group A]
        {R_I(t)},              ion positions                          [Group A]
        {P_I(t)},              ion momenta                            [Group A]
        Π_h(t),                cell momentum                          [Group A]
        {Z_I},                 species labels (immutable)             [Group A]
        γ̂(r, r'; t),           Pauli-spinor 1-body density matrix     [Group B]
        A(r, t)                external EM vector potential           [Group B]
      )
```

Continuum displacement fields, phonon distributions `n_{qs}`,
carrier distributions `f_n(k, r)`, surface coverages `θ_i`,
composition vectors `x_i` are EMERGENT (coarse-grainings,
projections, semiclassical limits) — not irreducible state.

### Canonical functionals

```
E[x] = E_kin(ions) + E_BO(R, h) + E_KS[γ̂] + E_EM[A] + E_coupling[γ̂, A, R]

S[x] = S_vib[x] + S_electronic[γ̂; T] + S_config[x]
```

### GENERIC operators

```
L (reversible, antisymmetric Poisson):
  - symplectic on (R, P)
  - Liouville-von Neumann on γ̂
  - Maxwell on A
  - semiclassical streaming on emergent distributions

M (dissipative, symmetric PSD):
  - phonon-phonon scattering
  - electron-phonon scattering
  - Gilbert damping on spins
  - radiative damping
  - chemical rate matrix
```

### Unified EOM

```
dx/dt = L · δE/δx + M · δS/δx
```

with degeneracy `L · δS/δx = 0` and `M · δE/δx = 0`.

### Each of the 9 regimes is an EXTRACTION

| Regime | Extraction of unified structure |
|--------|--------------------------------|
| Structural | critical points of E at T=0 (or F at T>0); 1st derivatives |
| Mechanical | 2nd strain-derivatives of F at equilibrium |
| Thermal | 2nd displacement-Hessian of E_BO (phonons); BTE for phonon distribution (L+M) |
| Electronic | SCF as gradient flow / TDKS as Liouville (L on γ̂) |
| Magnetic | Pauli-spinor extension of γ̂; LLG = L (precession) + M (Gilbert) |
| Optical | Response of γ̂ to A(t) via L; absorption via M |
| Transport | BTE on emergent carrier distribution: L (streaming) + M (collisions) |
| Thermodynamic | min F at fixed (T,V,N); convex hull of {F_φ} |
| Chemical | Master equation on configs (M = rate matrix); NEB on E_BO |

Static observables are EQUILIBRIUM READOUTS (fixed points of the
GENERIC flow). Time-evolving observables are TRAJECTORY READOUTS.
Same framework; static = equilibrium limit.

## Refined directory tree (research-grounded, hierarchy-aligned)

```
n-Op/
├── physics/
│   ├── README.md
│   ├── AGENTS.md, CLAUDE.md, _darcs/, .git/, .gitignore
│   ├── research/                        ← organized by BO hierarchy
│   │   ├── level-1-electronic-substrate.md
│   │   ├── level-2-born-oppenheimer-surface.md
│   │   ├── level-3-equilibrium-statistics.md
│   │   ├── level-4-nonequilibrium-kinetics.md
│   │   └── synthesis.md                 ← GENERIC across the hierarchy
│   │
│   ├── library/
│   │   ├── info.rkt
│   │   ├── main.rkt                     ← THE typed seal
│   │   ├── api.rkt
│   │   │
│   │   ├── inputs/                      ← time-independent
│   │   │   ├── periodicity-structure
│   │   │   ├── site-decoration
│   │   │   └── environment
│   │   │
│   │   ├── state/                       ← UNIFIED SYSTEM STATE
│   │   │   ├── system-state                 unified container
│   │   │   ├── irreducible-dofs             (h, R_I, P_I, Π_h, Z_I, γ̂, A)
│   │   │   ├── derived-fields               phonon dist, carrier dist, coverages — projections
│   │   │   └── enumeration                  iterate / serialize / hash
│   │   │
│   │   ├── canonicals/                  ← E[x] and S[x]
│   │   │   ├── energy-functional/
│   │   │   │   ├── kinetic-energy
│   │   │   │   ├── born-oppenheimer         E_BO(R, h)
│   │   │   │   ├── kohn-sham                E_KS[γ̂]
│   │   │   │   ├── electromagnetic          E_EM[A]
│   │   │   │   └── couplings/               electron-phonon, spin-orbit, optical-electronic, magneto-elastic
│   │   │   └── entropy-functional/
│   │   │       ├── vibrational              S_vib
│   │   │       ├── electronic               S_electronic
│   │   │       └── configurational          S_config
│   │   │
│   │   ├── generic/                     ← GENERIC OPERATORS L, M
│   │   │   ├── poisson-L/                   antisymmetric reversible bracket
│   │   │   │   ├── symplectic-ions
│   │   │   │   ├── liouville-density-matrix
│   │   │   │   ├── maxwell-em
│   │   │   │   └── streaming-emergent
│   │   │   └── dissipative-M/               symmetric PSD dissipative bracket
│   │   │       ├── phonon-collisions
│   │   │       ├── electron-phonon-scattering
│   │   │       ├── gilbert-damping
│   │   │       ├── radiative-damping
│   │   │       └── chemical-rates
│   │   │
│   │   ├── dynamics/                    ← unified GENERIC EOM
│   │   │   └── total-evolution              dx/dt = L δE/δx + M δS/δx
│   │   │
│   │   ├── residuals/                   ← PINO loss terms
│   │   │   ├── eom-violation                primary: ||dx/dt - (L δE/δx + M δS/δx)||²
│   │   │   ├── degeneracy                   ||L δS/δx||² + ||M δE/δx||²
│   │   │   ├── conservation                 conserved quantities preserved
│   │   │   ├── positivity                   M ⪰ 0, |S_i|=1, f∈[0,1], ρ≥0
│   │   │   ├── algebraic-identities         Maxwell, Einstein, detailed balance, KK, sum rules
│   │   │   └── total-residual               outer linear combination
│   │   │
│   │   ├── observables/                 ← readouts of state (bundled by data shape)
│   │   │   ├── bz-resolved/             BandStructure, PhononDispersion, KResolvedDOS, MagnonDispersion
│   │   │   ├── energy-resolved/         DOS, OpticalAbsorption, ImChi(ω), ReChi(ω)
│   │   │   ├── real-space/              ChargeDensity, SpinDensity, ElectrostaticPotential
│   │   │   ├── atom-indexed/            Forces, MagneticMoments, AtomicCharges, DisplacementField
│   │   │   ├── tensor-indexed/          ElasticConstants, ConductivityTensor, ThermalConductivityTensor
│   │   │   ├── temperature-resolved/    HeatCapacity(T), FreeEnergy(T), IonicDiffusivity(T)
│   │   │   ├── reaction-coord/          NEBProfile, MigrationPath
│   │   │   └── scalars/                 BandGap, TotalEnergy, FormationEnergy, SurfaceEnergy,
│   │   │                                AdsorptionEnergy, BulkModulus, Hardness, MigrationBarrier
│   │   │
│   │   ├── level-1-electronic/          ← γ̂ + closure + Liouville dynamics
│   │   │   ├── density-matrix
│   │   │   ├── ks-hamiltonian
│   │   │   ├── tdks-liouville
│   │   │   └── closures/                    v_xc, B_xc, f_xc, BSE-K
│   │   │
│   │   ├── level-2-bo-surface/          ← E_BO(R, h) + ion phase space
│   │   │   ├── born-oppenheimer-energy
│   │   │   ├── ion-phase-space
│   │   │   ├── symplectic-dynamics
│   │   │   └── strain-expansion
│   │   │
│   │   ├── level-3-statistics/          ← spectrum → partition function → F
│   │   │   ├── spectral-data                eigenvalues from Levels 1 + 2
│   │   │   ├── statistics                   Bose, Fermi, Maxwell–Boltzmann
│   │   │   ├── partition-functions
│   │   │   ├── free-energy
│   │   │   └── convex-hull
│   │   │
│   │   ├── level-4-kinetics/            ← distributions + GENERIC L + M
│   │   │   ├── emergent-distributions       carrier, phonon, coverage
│   │   │   ├── generic-L-streaming          per-regime streaming brackets
│   │   │   ├── generic-M-collision          per-regime collision brackets
│   │   │   ├── coupling-fluxes              transport / chemical fluxes
│   │   │   └── master-equation
│   │   │
│   │   ├── regimes/                     ← navigational extraction views
│   │   │   ├── electronic/                  → Level 1 readouts
│   │   │   ├── optical/                     → Level 1 (γ̂ response to A)
│   │   │   ├── magnetic/                    → Level 1 (Pauli-spinor γ̂)
│   │   │   ├── structural/                  → Level 2 (E critical points)
│   │   │   ├── mechanical/                  → Level 2 (2nd strain-derivatives)
│   │   │   ├── thermal/                     → Level 3 (Bose stats) + Level 4 (phonon BTE)
│   │   │   ├── thermodynamic/               → Level 3 (min F, convex hull)
│   │   │   ├── transport/                   → Level 4 (BTE on carriers)
│   │   │   └── chemical/                    → Level 4 (master eq + NEB)
│   │   │
│   │   ├── core/                        ← tier 1: math primitives
│   │   ├── shared/                      ← tier 2: physical primitives
│   │   ├── interfaces/                  ← cross-cutting (Scalar, FieldOnGrid, Tensor, Response)
│   │   ├── cert/                        ← obligations + degeneracy check
│   │   ├── examples.rkt
│   │   └── tests/
│   │
│   └── install/
│
├── informed-operator/
└── interface/
```

## What I will do (research-grounded execution)

1. Write the three research files from agent plan files to
   `physics/research/group-{A,B,C}-*.md`.
2. Write a `physics/research/synthesis.md` capturing the GENERIC
   unification.
3. Create the directory skeleton above.
4. Write `physics/README.md` framing the GENERIC structure as
   `/physics`'s organizing principle.
5. Write per-directory `README.md` for each non-leaf folder.
6. Write `canonicals/ENERGY.md` and `canonicals/ENTROPY.md`
   documenting the functional decomposition.
7. Write `generic/POISSON.md` and `generic/DISSIPATIVE.md`
   documenting the L and M operator decompositions.
8. Write `dynamics/TOTAL-EVOLUTION.md` documenting the unified EOM.
9. Write `residuals/CONTRACT.md` documenting the five residual
   categories and how they connect to GENERIC structure.
10. Write per-regime `extraction.md` in each `regimes/<r>/` showing
    what the regime extracts from the unified state.
11. Verify cross-references: every regime extraction points to
    actual canonical/operator pieces; every observable declares
    its state-component dependency; the slide maps to specific
    observables with nothing unaccounted for.

I will NOT commit to a language, write code, touch `/informed-
operator` or `/interface`, or run external physics codes.

## Open architectural questions (deferred)

1. Implementation language.
2. Internal layout of each state component (Pauli-spinor γ̂
   representation; ion phase space packing; EM gauge choice).
3. Macro grammar for the GENERIC pieces — `derive-L-component`,
   `derive-M-component`, `derive-E-piece`, `derive-S-piece`.
4. Integrator interface (lives downstream in `/informed-operator`).
5. Coupling grammar — how cross-regime terms in `E_coupling` and
   in `L`/`M` are declared.
6. Start order — substrate first or one canonical piece end-to-end.

## Audit step (active)

User requested: spawn 3 subagents (one per research group file) to
audit each for:

1. Inconsistencies / lack of detail
2. What can be expanded
3. **Deep computational approach** — numerically, algorithmically,
   how do you elegantly approach these problems?

Agents to write per-group audit reports to:
- `physics/research/group-A-audit.md`
- `physics/research/group-B-audit.md`
- `physics/research/group-C-audit.md`

After they return, I synthesize cross-group findings into the
implementation plan (Phases 5, 8, 9 most affected by computational-
approach recommendations).

## Audit reports (staged in agent plan files)

Each auditor produced a 5000–10000 word audit + computational-approach
report. Plan mode blocked writes to `research/`; the full reports
live at:

- Group A: `~/.claude/plans/please-read-the-slide-humble-sunrise-agent-a728e217733b6277d.md`
- Group B: `~/.claude/plans/please-read-the-slide-humble-sunrise-agent-a1557e553d7bc8461.md`
- Group C: `~/.claude/plans/please-read-the-slide-humble-sunrise-agent-a476c528e1980a4ee.md`

On execution, these get moved to:

- `physics/research/group-A-audit.md`
- `physics/research/group-B-audit.md`
- `physics/research/group-C-audit.md`

### Audit headlines

**Group A — Ion dynamics (~9600 words)**

Inconsistencies: LO/TO non-analytic correction completely missing
(polar materials need Born effective charges Z* and ε∞ from Level 1);
stress sign / Voigt / shear conventions silently differ across
sections (factor-2 errors in shear moduli); internal-strain coupling
Λ and clamped-vs-relaxed elastic-constants distinction missing.

Expansions: self-consistent / temperature-dependent phonons (SCP,
TDEP, SSCHA) — half of high-T physics is dynamically unstable at
the static structure where QHA fails outright; operationalized
ULICS + Le Page-Saxe elastic-constants pipeline (6 strain patterns
+ regression vs. 21 SCFs); sparse third-order Ψ via compressed-
sensing (without it Ψ is unstorable for N_c > 8).

Computational: one primitive `derivative-tower(E_BO, point, chart,
order) → tower` covers structural forces/stress + mechanical
C_IJ^cl,rel + thermal Φ/Ψ + Grüneisen; unified atomistic state
`(h, R, P, Π_h, h_0, R_0, F, η)` struct-of-arrays; Φ sparse-by-
cutoff, D(q) never stored, always Bloch-summed on demand;
tetrahedron-with-Blöchl for phonon DOS; FIRE2 + BFGS + RFO + MTK
extended Hamiltonian behind one `geometry-relax` signature.

**Group B — Electronic / magnetic / optical (~7300 words)**

Inconsistencies: band-gap problem unaddressed (KS underestimates by
30–100%; GW absent, BSE one line; every `BandGap` observable is
wrong without quasi-particle correction); closure functional
collapsed to one symbol `v_xc` (LDA / GGA / hybrid / +U / GW
differ by O(N³) to O(N⁴N_ω) cost and dramatically in accuracy —
cert needs to record which); SOC + Dzyaloshinskii–Moriya absent
from magnetic Hamiltonian (no skyrmions, no MCA, no anomalous-Hall
without them).

Expansions: full GW + BSE pipeline end-to-end (G₀W₀ quasi-particle
spectrum → Lanczos–Haydock BSE for absorption / excitons); SCF
mathematics (Pulay-DIIS + Kerker preconditioner; spin-aware
mixing; broken-symmetry guesses; RMM-DIIS direct minimization);
DFT+U with self-consistent linear-response U.

Computational: PAW + plane waves + Wannier90 as canonical Level-1
substrate (one `Hψ` primitive serves SCF, Sternheimer, RT-TDDFT,
GW); Sternheimer preconditioned-CG as THE primitive for every
perturbative response (optical, phonon, magnetic susceptibility,
Born charges); Lanczos–Haydock continued-fraction BSE for
absorption (O(N_iter × N_eh) not O(N_eh³)); semi-implicit Mentink
SIA/SIB for stochastic LLG (exact |S|=1, Stratonovich-consistent);
commutator-free 4th-order Magnus (CFM4) for RT-TDDFT and
Pauli-TDKS (4–8× larger dt than Crank–Nicolson, unitary).

**Group C — Transport / thermodynamic / chemical (~9000 words)**

Inconsistencies: RTA / MRTA / SERTA / full iterative BTE conflated
into one bullet (each is a different typed sub-method; collision
rate W never factored into |g|²·δ form, so BTE↔Kubo equivalence
unprovable from the notation); Onsager symmetry stated twice with
incompatible scope (B-flip case missing from the GENERIC version);
configurational entropy and Redlich–Kister CALPHAD parameterization
missing from the free-energy decomposition.

Expansions: stiffness handling + BKL + binary-tree event selection
for chemical kinetics (microkinetic ODE silently catastrophic with
explicit solvers; kMC text omits BKL rejection-free O(log N));
anharmonic/soft-mode SSCHA + Cahn–Hilliard–Cook (stochastic
noise-augmented); Berry-curvature semiclassics + Mott formula +
Wiedemann–Franz + Hall/Nernst as cross-regime cert battery.

Computational: symmetrized collision matrix + null-space deflation
as canonical BTE representation (Onsager + detailed balance +
conservation become structural properties of the data type);
tetrahedron method for all Fermi-window / DOS-weighted integrals
(both transport and thermodynamic; exact sum-rule preservation;
shared cross-regime cert); semi-implicit Fourier-spectral as
default Cahn–Hilliard / Allen–Cahn stepper (O(N log N) per step,
unconditionally stable); BKL binary-tree kMC + Wegscheider
cycle-basis reduction (makes detailed balance structural rather
than residual); single cross-regime cert obligation
`M-positive-on-physical-subspace` applied to BTE collision matrix,
CH/AC mobility tensor, symmetrized master-equation rate matrix.

### Cross-cutting themes (cross all 3 groups)

1. **One canonical primitive per group, lots of templates instantiating it.**
   Group A: derivative-tower(E_BO). Group B: Hψ primitive. Group C:
   symmetrized collision/rate matrix. The IMPLEMENTATION-PLAN's
   12-method vocabulary should be REFINED — these audits show
   each method has 3–4 typed sub-method variants worth distinguishing
   (e.g., spectral-decomposition / Davidson vs. LOBPCG vs. PPCG).

2. **Sparse-by-cutoff + on-demand reconstruction is universal.**
   Φ sparse in real-space; Ψ sparse in real-space; H sparse in
   Wannier basis; collision matrices sparse in mode-pair-conserving
   energy. Never store dense full-domain tensors. Reconstruct via
   Bloch/Wannier interpolation on demand.

3. **Tetrahedron method is cross-cutting.** Phonon DOS (A), BZ
   integrals in linear response (B), Fermi-window transport (C),
   spectral aggregates for free energy (A→C). One implementation,
   exact sum-rule preservation, multi-regime cert.

4. **Symmetry-adapted patterns dominate at scale.** Le Page-Saxe
   for elastic (6 strain patterns vs. 21 SCFs). Same pattern for
   Born charges (3 perturbations vs. 9). Same for piezoelectric.
   Same template: symmetry-adapted-perturbation-set.

5. **Cert obligations cluster into ~3 cross-regime invariants.**
   M ⪰ 0 (dissipative-matrix PSD): BTE + CH/AC + master-eq. Sum
   rules: acoustic (Group A) + f-sum + Friedel + Luttinger (Group
   B) + particle-number conservation in BTE collisions (Group C).
   Method equivalence: BTE-σ ≡ Kubo-σ (Group C), DFPT-Φ ≡ FD-Φ
   (Group A), QHA-α ≡ direct-min-α (Group A↔C).

### Implications for IMPLEMENTATION-PLAN.md

- Phase 1 (core/) needs `derivative-tower` primitive + tetrahedron
  integrator + Wannier-interpolation primitive
- Phase 5 (methods/) needs sub-method explosion: spectral-decomposition
  has Davidson/LOBPCG/PPCG/Lanczos/Sternheimer-CG variants
- Phase 7 (formulas/) needs Redlich-Kister, Marcus, BEP-with-cross-validation,
  Born-Huang LO/TO splitting, plus 6 cert formulas (cycle-basis
  detection, Wegscheider, symmetry-adapted strain projection,
  Le Page-Saxe regression, M-PSD check, tetrahedron weight)
- Phase 8 (generic/) needs:
  - L additions: non-analytic LO/TO term for polar phonons
  - M additions: stochastic LLG (Stratonovich), CH/AC mobility,
    Wegscheider-projected master rate
- Phase 9 (canonicals/) needs:
  - E additions: configurational entropy term, SOC + DM in magnetic,
    SCP/SSCHA temperature-dependent phonons
  - S additions: explicit configurational entropy (Bragg-Williams + CE)
- Phase 11 (cert/) gets the 3 cross-regime invariants above as
  explicit obligations

## CURRENT STATE OF UNDERSTANDING (durable log)

> Written deliberately for the case where conversation context is
> compressed away. Re-reading this should let me pick up where the
> design left off, without needing the back-and-forth dialogue.

### What is n-Op

A project at `~/Desktop/Physics/Programs/n-Op/`. The aim: a
physically-informed neural operator (PINO) that learns the
**time evolution** of unified multiphysics state inside crystals.
Three sibling top-level libraries:
- `/physics` — the substrate-agnostic reference oracle (we are
  designing this)
- `/informed-operator` — the PINO; downstream; not in scope
- `/interface` — user surface; not in scope

### What `/physics` IS

A library that:
1. Encodes the entire multiphysics system as a unified state x(t)
2. Expresses its dynamics in the GENERIC two-bracket form
3. Produces residuals usable as PINO loss terms
4. Exposes observable readouts derived from state
5. Does NOT train, hold weights, integrate trajectories, wrap
   external DFT/MD codes at runtime, or know about NN architecture

### Decided architecture (locked-in)

- **3 top-level inputs**: PeriodicityStructure + SiteDecoration +
  Environment. Physically orthogonal. Reference + Property demoted.
- **GENERIC dynamics**: dx/dt = L · δE/δx + M · δS/δx over
  unified state x = (h, R_I, P_I, Π_h, Z_I, γ̂, A).
  L antisymmetric, M ⪰ 0, plus degeneracy conditions.
- **4-level BO hierarchy**: L1 (γ̂) ← L2 (R, h) ← L3 (stats) ←
  L4 (kinetics). Strict downward dependency.
- **9 inherited principles** from source library: strict layering +
  typed seal, minimum primitives + composition, no-symbolics on
  runtime path, cert as first-class, loud failure with numeric
  witnesses, compile-time staging, substrate-agnostic stance, long-
  name + header-docstring house style, dual VCS (darcs + bd).
- **12 methods vocabulary**: state-readout, algebraic-combination,
  functional-differentiation, variational-minimization, spectral-
  decomposition, spectral-aggregation, linear-response, path-search,
  convex-optimization, kinetic-evolution, statistical-sampling,
  symmetry-projection.
- **12 abstract-property templates**: StateReadoutOf, AlgebraicOf,
  SecondDerivativeOf, SpectrumOf, SpectralAggregateOf, ResponseOfTo,
  PathStationaryOf, KineticEvolutionOf, ClassifyOf, ComparisonOf,
  RadiativeEmissionOf, MicrokineticSteadyStateOf.
- **24 named formulas registry**: slab-arithmetic, arrhenius,
  vineyard-prefactor, kramers-kronig-hilbert, chen-hardness, etc.
  Closed registry; controlled growth process.
- **8 observable bundles** by data shape: bz-resolved, energy-
  resolved, real-space, atom-indexed, tensor-indexed, temperature-
  resolved, reaction-coord, scalars. User's chosen axis.
- **4 cross-cutting interfaces**: Scalar, FieldOnGrid, Tensor,
  Response.
- **6 cert obligations**: symmetry, bounds, analytic-limits,
  reference-battery, conservation, degeneracy. Plus inert-sexpr
  schema + freeze fixture + tamper tripwire + bigfloat oracle.
- **5 residual categories**: EOM-violation (primary), degeneracy,
  conservation, positivity, algebraic-identities. Total residual =
  weighted linear combination.
- **All 36 observables on the slide** as typed one-line
  compositions in IMPLEMENTATION-PLAN §15.
- **11-phase implementation sequence** in IMPLEMENTATION-PLAN §16.

### Files on disk (concrete state)

```
~/Desktop/Physics/Programs/n-Op/
├── .git/, .gitignore                           (mostly empty)
├── properties.md                               (9-regime spec)
├── physics-library-architecture.md             (source-library summary)
├── IMPLEMENTATION-PLAN.md                      (1343 lines, 67 KB)
└── research/
    ├── group-A-ion-dynamics.md                 (719 lines)
    ├── group-B-electronic-magnetic-optical.md  (505 lines)
    └── group-C-transport-thermo-chemical.md    (688 lines)
```

No code written. No language chosen. No `physics/library/` directory.

### Audit reports (staged in agent plan files, not yet on disk)

- `~/.claude/plans/please-read-the-slide-humble-sunrise-agent-a728e217733b6277d.md` — Group A audit, ~9600 words
- `~/.claude/plans/please-read-the-slide-humble-sunrise-agent-a1557e553d7bc8461.md` — Group B audit, ~7300 words
- `~/.claude/plans/please-read-the-slide-humble-sunrise-agent-a476c528e1980a4ee.md` — Group C audit, ~9000 words

On plan-mode exit: move to `physics/research/group-{A,B,C}-audit.md`.

### Open threads (not yet decided)

From the audits — three follow-up threads:

1. **Data type as cert** (discussed in depth) — push invariants
   into the type system rather than runtime checks. Proposed
   taxonomy: always-structural / always-runtime / could-go-either-way.
   NOT YET DECIDED.

2. **Sub-method explosion** — 12-method vocabulary expands to
   ~40 sub-methods (Davidson / LOBPCG / PPCG for spectral; FIRE2
   / BFGS / RFO for minimization). Three resolutions on the table.
   NOT YET DISCUSSED.

3. **Closure-functional polymorphism** — v_xc is LDA/GGA/HSE/+U/GW,
   each with different cost/accuracy/cert. Library needs polymorphism.
   NOT YET DISCUSSED.

Other audit findings flagged but not addressed:
- Group A: LO/TO non-analytic correction missing; Voigt/shear
  convention inconsistencies; internal-strain coupling Λ absent
- Group B: band-gap problem (KS underestimates 30–100%); SOC + DM
  absent from magnetic Hamiltonian
- Group C: RTA/MRTA/SERTA conflated; Onsager B-flip case missing;
  Redlich–Kister CALPHAD parameterization absent

From IMPLEMENTATION-PLAN §17 (six deferred decisions):
1. Implementation language (Racket vs. Python/JAX/PyTorch) — gates Phase 1
2. Internal layout of state components — gates Phase 4
3. Macro grammar for derive-{residual, update, readout, eom} — gates Phase 5
4. Integrator interface — gates Phase 13
5. Coupling grammar — gates Phases 8 + 9
6. Start order — substrate first vs. one regime end-to-end

### User-stated preferences and discipline signals (durable)

These have been stated explicitly across the dialogue and should
constrain future moves:

- **"Related concepts grouped, not super-unified."** Don't fuse
  everything into one mega-type.
- **"Concrete with parameterizations, not loose and stretched."**
  Every method/template/formula has a typed signature; no string
  formulas; no implicit / optional / hand-waved arguments.
- **"Most canonical representation."** Prefer the most canonical
  form; derive when possible; fragment only when forced.
- **"One beautiful canonical form that can be expanded INTO either
  residual form, or numerical form."** Each regime has a canonical
  functional; residual and numerical derive via macros.
- **"Output should be the same shape no matter what is produced."**
  Universal output abstraction at the bundle level.
- **"Bundle by computational method of representation."** Drove
  the methods + abstract-templates architecture.
- **User has repeatedly pushed back on forced-choice questions
  when not ready to commit.** Prefers open dialogue. Don't force.
- **User asked for deep research, computational rigor, audits.**
  Has dispatched two rounds of subagents (per-group research, then
  per-group audit). Now a meta-audit of the documents.
- **Stay conceptual (CS / math / physics), NOT low-level /
  engineering / language.** "Language and engineering topics come
  much later." Do not raise implementation-language questions, code
  organization details, performance tuning, or build-system
  decisions until the conceptual architecture is fully settled.
- **Use CS vocabulary, not physics-academia jargon.** User is in
  the HiPE (High Performance Physics) lab at Texas State,
  subgroup 3. Terms like "Krylov basis", "Hermitian operator",
  "Bloch periodicity", "Wannier functions" do not communicate. The
  same ideas in CS terms — "iterative procedure that builds a
  tridiagonal projection of A via repeated A·v", "self-adjoint
  linear map", "discrete translational symmetry of an indexed
  function", "change of basis producing a sparse representation" —
  do communicate. **The CS abstraction is the load-bearing
  description; physics names are decoration.**

### What's happening right now

User asked me to (a) log my entire understanding (this section) and
(b) dispatch a subagent to meta-audit the four primary documents
(IMPLEMENTATION-PLAN.md + 3 research files) for:
- Internal consistency / discrepancies
- Things that don't hold up computationally / physically /
  mathematically
- Depth and clarity issues
- True-but-incomplete statements
- Not-feasible-to-run claims
- Badly mathematically stated claims

The meta-audit agent runs in BACKGROUND so the log gets written
immediately. When the agent returns, I synthesize its findings.

### Decision pending after meta-audit

Depends on what the meta-audit finds:
- Minor issues: continue with the three open threads + 6 deferred
  decisions
- Major issues: fix them first, re-validate, then continue

Eventual transition to landing: ExitPlanMode + write audits to
disk + pick language + start Phase 0. User has said they're not in
a hurry: "I am not asking to speed it up. I just want a point to
continue working today."

### META-AUDIT RETURNED (~10,400 words)

Full report at `~/.claude/plans/please-read-the-slide-humble-sunrise-agent-ae0e7f2d11fc12004.md`.
On plan-mode exit: move to `n-Op/META-AUDIT.md`.

**Verdict:** architecture *shape* sound (GENERIC + 4-level BO +
12×12×~22×36×6 coherent and matches slide). But:

- **Faithful?** NO — §15 compositions escape the §8/§9 closed
  vocabularies in ~9 places; the plan's own §18 self-verification
  fails.
- **Complete?** NO — cert tolerances, reference battery, k-mesh
  policies, xc choice, sparsity strategies absent; ~10 modules
  missing from §14 tree.
- **Feasible?** NO as written — dense γ̂, dense BSE, full-distribution
  BTE all need sparsity policies that aren't declared. γ̂ stored
  dense is O(N_r²) doubles = terabytes for any nontrivial cell.
- **Correct?** MOSTLY — ~20 factor-of-2 / missing-mass / wrong-
  prefactor errors; correctable via local edits.

**Top 5 showstoppers:**

1. γ̂(r,r';t) declared as irreducible state without basis /
   discretization choice (Plan §3.1). Need to commit to a basis
   (plane waves vs. NAO vs. real-space) before Phases 1–3 can
   touch it.
2. **Absorption formula has wrong factor of 2** (Plan §15 item 3):
   `α = (ω/c)·Im(√ε)` should be `α = (2ω/c)·Im(√ε)`. Group-B has
   it correct.
3. **§15 compositions use templates and formulas NOT in the closed
   registries.** `MapOver`, `MinimizationOf`, `match`-dispatch are
   not in §8 templates; ~9 inline string formulas violate §9
   registry rule. Plan's own self-verification fails.
4. **PhononDispersion composition omits mass-weighting and Bloch
   sum** (§15 item 5). `dynamical-matrix(SecondDerivativeOf(E_BO,
   R₀, u))` is wrong; should be `(M_I M_J)^{-1/2} Σ_R Φ(R) e^{-iq·R}`.
5. **`research/synthesis.md` referenced but does not exist** (Plan
   §3 and §14).

**Top 5 major:**

1. f-sum rule missing 2/π factor in §12; Group-B has it correct.
2. Acoustic sum rule misstated in §12 (`Σ_J Φ(0)=0` vs. correct
   `Σ_J Σ_R Φ(R)=0`).
3. "Gilbert damping" name swapped with Landau–Lifshitz form
   between §3.3 and Group-B §M.3.
4. Vineyard prefactor type mismatch §15 item 7 (`SpectrumOf`
   returns spectrum, formula expects scalars; conversion missing).
5. Charged-defect formation energies need Makov–Payne / Freysoldt
   corrections + potential alignment — neither in §9 signature.

The full report has: per-document section-by-section findings,
a 15-item cross-document discrepancy table, a feasibility analysis
(storage + complexity tables), a 35-line factor/sign error
inventory, an edge-case + missing-approximation inventory, and a
45-item prioritized remediation list (showstopper / major / minor).

### ACTIVE BRAINSTORM — Hole 1 (γ̂'s computational structure)

User invoked `/superpowers:brainstorming` with: "What computational
structure lends to this component in particular. What makes it
elegant." Clarified: "If we can use some form of generative code.
Genetic, tree-algebra, orthogonal algebraic data types. What
*lends* to the problem. Not necessarily what I want — what is the
natural representation."

**Proposal on the table:** typed term algebra with rewrite rules.

Argument: γ̂ has five distinctive features and ONE CS abstraction
covers all five.

1. One logical object, multiple equivalent encodings (R1 low-rank
   outer-product / R2 momentum-block-diagonal / R3 sparse-in-
   localized-basis) → γ̂ is a TERM in a grammar; encodings are
   PRODUCTIONS.
2. Operations cost different amounts in different encodings →
   operations are VISITORS over the term; cost is a property of
   the (visitor, production) pair.
3. Encodings convert via algebraic moves (basis change, contraction,
   blocking) → conversions are TERM REWRITES under equational laws.
4. Invariants hold regardless of encoding (self-adjoint, idempotent
   for closed-shell, trace = N) → invariants are TYPE-LEVEL TAGS
   orthogonal to the production axis. *This is the orthogonality
   the user named.*
5. γ̂ evolves in time → a time-step is a FOLD over the term that
   consumes state and emits a new term.

Grammar sketch:

```
γ̂ ::= OuterProductSum(vectors, scalars)        -- R1
    | BlockDiagonal(γ̂-per-momentum-block)       -- R2
    | SparseInBasis(triples, basis)             -- R3
    | BasisChange(basis, γ̂)                     -- conversion-as-construction
    | UnitaryEvolution(γ̂, U, dt)                -- time-step constructor
    | LinearCombination([(α, γ̂)])
    | Restriction(γ̂, subspace)
```

Falls out for free:
- "Opaque operator with action interface" — visitors apply / solve /
  eigendecompose against the term *as-is*; never demand reduction
  to a dense matrix. Directly addresses the meta-audit showstopper
  #1 (γ̂ declared without basis → dense → terabytes): the grammar
  ALLOWS a dense production (e.g. as a degenerate `SparseInBasis`)
  but never forces one.
- Composes with the source library's `formula-trees.rkt` +
  `staged-code-generation.rkt` pattern: the term grammar IS the
  formula tree; rewrites + visitors get staged into specialized
  code per production at expand time.

**Frontier — where the dialogue paused (user picks the angle):**

- Lock proposal: typed-term-algebra-with-rewrites is the natural fit.
- Reframe: try a different generative shape — e-graph with cost-
  driven equality saturation; free monad over a γ̂-algebra; algebraic
  effects; final-tagless encoding.
- Deepen on a piece: invariants-as-types axis (how tags compose with
  productions); the rewrite-law set (which moves are sound, which
  need cert); the staging story (how visitors specialize); concrete
  shape of a visitor (e.g. `apply Ĥ to γ̂`).
- Pivot: γ̂'s shape is settled enough — go to Hole 2 (BSE storage)
  or Hole 3 (BTE storage) and look for the analogous natural fit.

Context note: user had to power down the machine and returned fresh,
asking for a stock-take. This subsection IS the stock-take, written
so the brainstorm survives any future compression event.

### ACTIVE BRANCH — 4-agent framing-research dispatch on γ̂

After my head-to-head walk-through on γ̂' = U·γ̂·U† (which surfaced D
as low-friction, B as cleanest interface, A as combinatorially heavy,
C as overkill-for-one-op), user redirected:

> "Lets not do it pairwise. Lets do a single fully detailed structure.
> Then YOU do a 4 Choose 2 comparison between each. Then present me a
> report. ... Make a subagent for each, and make them detail it. Let
> them come to you for questions. You teach them. ... Focus on both
> computational expressability + speed/efficienty."

Protocol:
1. Dispatch ONE subagent per framing (A/B/C/D), each with detailed
   brief covering project context + γ̂ technical details + assigned
   framing + 10-section deliverable spec.
2. Subagents are READ-ONLY research; they may ask clarifying questions
   via SendMessage; I'm responsible for answers.
3. After all 4 return, I compute 6 pairwise comparisons (4 choose 2):
   A↔B, A↔C, A↔D, B↔C, B↔D, C↔D — focused on computational
   expressivity AND speed/efficiency.
4. Synthesize unified comparative report; present to user with verdict
   on natural fit + open next-move question.

DISPATCHED (parallel, foreground, named framing-A through framing-D,
model=opus). Awaiting their reports.

The 4 framings under study (locked vocabulary):
- A: typed term algebra with rewrite rules (γ̂ as term; encodings as
  productions; conversions as rewrites; operations as visitors;
  invariants as type-level tags; evolution as fold).
- B: codata / coalgebraic (γ̂ as opaque; only destructors; encodings
  invisible; invariants as destructor laws; evolution as F-coalgebra).
- C: e-graph with cost-driven equality saturation (γ̂ as e-class;
  all encodings stored cross-linked; per-query cost-driven extraction).
- D: tensor network with cost-aware contraction (γ̂ as node with
  node-type ∈ {Dense, Sparse, LowRank, BlockDiag}; operations as
  contractions; cost-aware contraction-order optimizer chooses
  encoding for output).

### FIRST SYNTHESIS RETURNED — layered hybrid recommendation

All 4 agents independently concluded their own framing was insufficient
alone. The convergent verdict: **no single framing fits γ̂**. The natural
fit is a layered hybrid:

- INTERFACE LAYER: B (codata destructors) — what /physics exposes
- STAGING/EXPAND LAYER: A (typed term algebra) — compile-time symbolic
  composition; rewrites stage per-encoding code at expand time
- OPTIONAL OPTIMIZATION: C (e-graph) at staging time for cross-cutting
  encoding selection
- RUNTIME SUBSTRATE: D (tensor networks) — concrete numerics with
  cost-aware contraction

This aligns with the project's existing principles (staging,
substrate-agnosticity, no-symbolics-at-runtime, cert-with-witnesses).

User then pulled at a 5th candidate via the question "Would something
like a pull-back type thing work? a dual-memory thing? Is that codata?"

### ACTIVE BRANCH — 5th framing dispatched (Framing E)

User opted to add E as a proper 5th framing rather than fold it into
the hybrid. Dispatched single framing-E subagent. After it returns:
- Compute 4 new pairwise comparisons (A↔E, B↔E, C↔E, D↔E)
- Re-synthesize unified report with E included
- Present updated findings

Framing E: multi-representation pullback with consistency invariant.
γ̂ as a TUPLE/BUNDLE of synchronized encodings (e.g. R1+R3 maintained
together), with a consistency invariant baked into the type or
maintained as a witness. Sits BETWEEN A (single representation) and
C (all equivalent forms via saturation). Categorical foundation:
pullback of decoding morphisms. Related to lens/optic structures
(profunctor optics give bidirectional bundled views). Storage cost
is multiplied by bundle cardinality; benefit is zero conversion cost
between maintained forms.

### SECOND SYNTHESIS RETURNED — 5-layer hybrid with E

After E's report came back, the hybrid was refined into a 5-layer
structure:
- INTERFACE: B (codata)
- STAGING: A (term algebra)
- OPTIONAL OPTIMIZATION: C (e-graph) — saturation-time
- RUNTIME REPRESENTATION: E (pullback bundle)
- RUNTIME SUBSTRATE: D (tensor network)

E earns its place specifically for γ̂ (read-heavy workload); the
hybrid drops E for BSE/BTE (storage prohibitive at higher rank).

### ACTIVE BRANCH — 10 mesh-analysis subagents on framing pairs

User feedback: "I believe this is it, the good set of tools. But I
am not convinced of the unity of the actual hybrid we have made.
So lets consider that and what its missing."

Protocol: dispatch ONE subagent per framing PAIR (5 choose 2 = 10
pairs). Each studies how its two framings MESH — boundary, control
direction, natural joint representation, impedance mismatches — and
critiques the 5-layer hybrid's placement of them. The 10 pairs:
A-B, A-C, A-D, A-E, B-C, B-D, B-E, C-D, C-E, D-E.

Each agent answers 5 questions: (1) How do X and Y mesh? (2) Can one
control or inform the other? (3) What's the natural joint representation?
(4) Where are the impedance mismatches? (5) Does the proposed 5-layer
hybrid put X and Y in the right relationship?

After all 10 return, synthesize a unified mesh architecture that
addresses unity concerns. Present revised hybrid.

DISPATCHED (parallel, foreground, named pair-AB through pair-DE,
model=opus). Awaiting reports.
