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

### THIRD SYNTHESIS RETURNED — corrected architecture from mesh analyses

All 10 mesh-pair agents returned. **The linear 5-layer stack is the wrong shape.** Multiple agents converged on this independently. Eight corrections specified:

1. **Two paths, not one stack.** Read path: `B → D` directly. Write path: `B → A → Planner → C? → E → D`. Most γ̂ traffic (apply, density, trace, eigendecomp) skips A/C/E entirely.
2. **Name the Planner.** A 6th structural component on the A/B boundary that consumes workload profiles + A's structure and produces bundle specs for E. Previously implicit and unowned.
3. **Merge A and E at the type level.** E is structurally A with bundle-typed leaves. Keep E as documentation vocabulary; implement as A-with-bundle-leaves. The 5-layer reads as a 4-layer: `B → (A with bundle leaves) → C? → D`.
4. **C as side-channel, multi-target extraction.** Not a vertical layer. C produces a multi-target BundleSpec that populates E's slots directly (not single-extract-then-re-expand).
5. **ε-equality stratification.** Architectural rule: C operates on exact-equivalence rule subset only; A/E handle approximate rewrites with explicit ε tracking; D's witnesses carry runtime accuracy.
6. **Tensor-rank stratification.** Bundled mode for γ̂ (2-index); unbundled mode for BSE/BTE (4-index, |B|× storage prohibitive). E is not universal.
7. **Consistency witness promoted to B destructor.** `γ̂.consistency_witness : Witness` becomes part of B's interface. Single-slot implementations return trivial witness; bundle implementations return real bound.
8. **B owns self-consistency.** B's coalgebraic fixed point drives Ĥ[γ̂] iteration; each iteration produces a fresh γ̂ through a single-step write-path computation. A needs `Let`/`Fix` constructors for the within-iteration sharing.

Three persistent gaps that no single pair could resolve, declared as system-level concerns:

- **ε-equality has no clean home** — handled by the stratification rule above.
- **Self-consistency is unowned** — resolved by B owning the loop.
- **Cost-and-call-pattern planner had no home** — resolved by naming the Planner as 6th component.

---

## POST-DEPARTURE BRANCHES (logged for durability)

### Branch: real/reciprocal as candidate fifth framing

User asked whether real/reciprocal space separation might be the natural answer to the γ̂ hole.

**Outcome:** Not a new framing — already captured. **R2 (momentum-block-diagonal) IS the reciprocal-space encoding; R3 (sparse-in-localized-basis) IS the real-space encoding.** FFT is the consistency mechanism in an E-bundle `{R2, R3}`.

It solves cheap diagonal-operation dispatch but **does NOT solve the storage hole** — both forms are O(N²). The actual storage savings come from **rank exploitation** (R1, basis-independent).

**Architectural refinement surfaced:** R1/R2/R3 conflates two orthogonal axes. Cleaner factoring:

```
Encoding = (basis ∈ {Real, Reciprocal, Wannier, NaturalOrbital, ...},
            form  ∈ {Dense, Sparse, BlockDiag, LowRank, ...})
```

Then R1 = `(any, LowRank)`, R2 = `(Reciprocal, BlockDiag)`, R3 = `(Real, Sparse)`. Opens slots for `(Wannier, Sparse)` and `(NaturalOrbital, LowRank)`. **Recommended amendment to architecture.**

### Branch: physicist colleague stress-test (gaps surfaced)

A physicist collaborator joined and probed four advanced physics scenarios:

1. **AZ symmetry classes (Cartan tenfold-way)** — missing from registry. Fix: add `topology-classification` method, `TopologicalInvariantOf` template, formulas for Chern / Z₂-Pfaffian / winding number. **Surgical addition.**

2. **Frustrated Wigner / spin liquids / strong correlation** — γ̂ is mean-field-only by construction; this is **out of theoretical scope** of the current L1 substrate. Bringing in scope requires alternative L1 carrier (tensor-network state, selected-CI, DMFT/DMET embedding, neural quantum state). Framings A/B/C/D/E would wrap any of these, but R1/R2/R3 catalog is wrong. **Architectural admission, not a registry fix.**

3. **Bulk-edge correspondence** — missing template + cert. Fix: add `BulkBoundaryCorrespondenceOf(invariant, slab)` template, add bulk-edge consistency cert obligation, 1-2 index-theorem formulas. **Surgical addition.**

4. **Symmetry-class transitions under energy / RG / effective Hamiltonians** — missing machinery. Fix: new RG layer between L1 and L2 that allows symmetry class of effective H to depend on energy scale. **Significant reframing** (makes scale-dependence first-class in the GENERIC bracket).

Plus: valley physics not first-class (no `ValleyResolved` bundle); typed perturbations carrying irrep labels would tighten selection rules; multi-photon/nonlinear response missing as a template.

---

## NEW GOAL CONTEXT — UWBG-semiconductor PINO

User clarified the ultimate goal driving /physics:

> Generate closed-form, cheap-ish residuals on lattice physics systems for training a neural operator via expanded loss `loss + λ₁·res₁ + λ₂·res₂ + ...`. The PINO predicts crystal structures, including diamond-metal semiconductor combos, in pursuit of durable high-performance ultra-wide bandgap (UWBG) semiconductors. Must include real electron diffusion math, temperature interactions, lattice shape, and many other interacting effects.

**Materials in scope (likely):** Ga₂O₃, AlN, BN, diamond, h-BN, possibly InN, ZnO at edge of UWBG. Diamond-metal heteroepitaxial stacks for thermal management + contact engineering.

**Applications:** high-power electronics, RF, deep UV, harsh-environment / radiation-hard electronics. Figures of merit: Baliga, Johnson, Keyes, breakdown field, mobility-bandgap product.

**Required predictions** (incomplete list, to be refined by Stream 1):
- Bandgap (corrected for quasi-particle effects)
- Dielectric constants (static + frequency-dependent)
- Carrier mobility (electrons + holes, T-dependent)
- Breakdown field
- Thermal conductivity (T-dependent)
- Defect formation energies (key dopants and traps, charged)
- Elastic moduli + hardness
- Schottky barrier heights at metal-semiconductor interfaces
- Crystal stability (phonon spectrum positive, hull distance)
- Doping efficiency (self-compensation, deep-level traps)

---

## GAP ANALYSIS — current architecture vs UWBG-PINO goal

### What's already covered well

- Lattice / crystal structure: L2 has E_BO, forces, stress, elastic constants
- Bulk electronic structure: L1 γ̂ + KS Hamiltonian + spectral observables
- Bulk transport (in principle): L4 BTE on emergent carrier distributions
- Bulk thermal: L3 + L4 phonon BTE
- Uncharged defect formation: L2 + `AlgebraicOf/slab-arithmetic`
- Phase stability: L3 `convex-optimization/hull`
- 5 residual categories cover most physics constraints structurally
- γ̂ representation hybrid (B/A-with-bundle-leaves/Planner/C?/E/D) addresses the storage hole

### What's flagged but unresolved (from prior audits)

- **LO/TO non-analytic correction** — Ga₂O₃ is polar; required for polar UWBG phonons
- **Charged-defect corrections** (Makov-Payne, Freysoldt, potential alignment) — required for any charged dopant or trap
- **Band-gap problem** — KS underestimates by 30–100%; need GW or scissor correction for **every** UWBG bandgap residual
- **SOC + DM** — relevant for diamond surface states, valley physics
- **SCP / SSCHA temperature-dependent phonons** — diamond at high operating T
- **RTA / MRTA / SERTA distinction** in transport sub-methods
- **Configurational entropy + Redlich-Kister CALPHAD** — required for dopant solubility, alloy phase diagrams

### What's MISSING for UWBG-PINO and not yet discussed

**Architectural concept missing — residual generation as first-class:**

The 5 residual categories are conceptual classifications, not a *machinery* for generating residuals from compositions. For PINO training, every observable composition `f(state) = composition_chain(...)` needs a corresponding residual generator `res_f(state, prediction) = (f(state) - prediction)² · weight`. This *residual-generator* is a structural concept currently absent from the architecture.

**Discipline missing — differentiability and cost-tiering:**

- Current formulas are typed signatures but NOT committed to auto-diff compatibility. Need to declare differentiability per formula.
- Residuals are not cost-classified. PINO training needs cheap residuals (sampled every step) and expensive ones (sampled rarely). Need a cost tier on each residual.

**Semiconductor-specific formulas not in registry:**

- Fröhlich electron-phonon coupling (polar materials — Ga₂O₃, AlN)
- Polar-optical-phonon-limited mobility
- Shockley-Read-Hall recombination rate (deep-level traps)
- Impact ionization coefficient (Chynoweth law) — breakdown
- Zener tunneling rate — breakdown
- Deformation potential coupling (acoustic e-ph)
- Density-of-states effective mass (anisotropic)
- Hall factor (statistical correction to Hall mobility)
- Schottky-Mott barrier height + Bardeen MIGS correction
- Fowler-Nordheim tunneling current
- Caughey-Thomas field-dependent mobility (drift saturation)
- SRH-multiphonon-emission formulas
- Defect-cluster formation energies

**State vector additions probably needed:**

- Hot-electron temperature T_e (distinct from lattice T_L) for high-field regime
- Local chemical potentials μ_i as state-aspect (for doping/growth conditions)
- Surface/interface termination flags (for heterostructure prediction)

**Observable bundles probably needed:**

- Interface-resolved (band alignment across a junction; charge transfer)
- Field-strength-resolved (mobility vs E-field; breakdown field profile)
- Hot-carrier-distribution-resolved (T_e vs T_L)

**Residual categories probably needed (additions to current 5):**

- Reference-battery residuals (predicted matches a known experimental/computed datapoint)
- Convergence residuals (variational gradient = 0 at predicted state)
- Structural-validity residuals (Born stability, dynamical stability, formability)
- Hull-distance residuals (predicted phase stability)

**Crystal-structure-prediction-specific machinery:**

- Formability heuristics (Hume-Rothery, electronegativity, ionic-radius ratio)
- Prototype-matching (does predicted structure match a known prototype with substitutions)
- Hull-distance computation against a reference database

**Interface / heterostructure machinery:**

- Slab + slab → heterostructure composition
- Work-function alignment
- Lattice-matching residuals (epitaxial strain)
- Charge-transfer self-consistency

**Hot-carrier / non-equilibrium electronic machinery:**

- Drift-diffusion-Poisson coupling
- Electron-temperature equation
- Coupled electrical-thermal solver residuals

**PINO integration interface (not specified):**

- What's the typed boundary between /physics-computed reference values and /informed-operator-predicted values?
- What's the autodiff / gradient interface across that boundary?
- How are residuals batched / sampled / weighted during training?

---

## RESEARCH SESSION PLAN

### Why this session

The user's actual deliverable is **a trained PINO that predicts UWBG semiconductor properties**, supported by **cheap closed-form residuals from /physics**. The current architecture is a strong backbone but has substantial gaps against this deliverable (above). Closing those gaps requires domain-physics knowledge (UWBG specifics), methodology knowledge (PINO loss design), and architectural knowledge (where additions slot in). A parallel research session is the cheapest way to compile this in one pass.

### Three-phase structure

**Phase 1 — five parallel domain surveys (dispatched simultaneously).** Each is independent; outputs are standalone reports.

**Phase 2 — closed-form catalog (dispatched after Phase 1).** Single agent consuming Phase 1 outputs.

**Phase 3 — architecture gap synthesis + PINO integration design (dispatched after Phase 2).** Single agent consuming all prior outputs; produces the concrete amendment proposal.

### Phase 1 streams — brief outlines (full prompts at dispatch time)

**Stream S1 — UWBG semiconductor scope and observable catalog.**
Materials: Ga₂O₃, AlN, BN, diamond, h-BN. Applications and figures of merit. What does a PINO need to predict for each material to support the user's high-performance / durability goals? Catalog observables with their governing equations and required accuracy. Highlight where standard DFT/BTE accuracy is insufficient.

**Stream S2 — Crystal-structure-prediction methodology.**
Survey CSP approaches (USPEX, CALYPSO, AIRSS, prototype-based, ML-potential-driven). For each: what's the scoring/validity criterion, how is it expressed as a residual or loss? Special attention to heterostructure / diamond-metal stacks. Hull distance, formability, dynamical stability, mechanical stability as residuals.

**Stream S3 — Defect, doping, surface, interface physics.**
For UWBG semiconductors: native defects, dopants, charged-defect corrections (Makov-Payne, Freysoldt), self-compensation, DX centers, deep-level traps. Surface reconstructions, work functions, dangling-bond states. Schottky-Mott + Bardeen + MIGS for metal-semiconductor contacts. SRH multiphonon recombination. Output: typed formula list + residual definitions.

**Stream S4 — Non-equilibrium / high-field / hot-carrier physics.**
Breakdown physics (impact ionization, avalanche, Zener tunneling). Polar-optical-phonon (Fröhlich) scattering. Drift-saturation models. Hot-electron temperature equation. Self-heating (coupled electrical-thermal). Radiation hardness / defect cascade physics. Output: typed formula list + residual definitions for high-field regime.

**Stream S5 — PINO residual loss design (literature + methodology).**
Survey how PINNs / FNOs / DeepONets / materials neural operators use physics-informed residuals. Loss balancing (NTK-based, GradNorm, adaptive). Differentiability disciplines (closed-form vs autodiff vs adjoint). Cost-tiering and residual sampling strategies. Specifically for materials/condensed-matter PINOs: what's known to work. Output: residual design discipline + sampling strategy recommendation.

### Phase 2 stream — closed-form catalog

**Stream S6 — Cheap residual catalog.**
Consumes S1-S5. For each observable identified in S1-S4 that's expensive to compute natively, propose a closed-form or semi-analytic approximation suitable as a PINO training residual. For each:
- Native form (full theory, expensive)
- Closed-form approximation (cheap, semi-analytical)
- Cost tier (per-step / per-100-step / per-epoch)
- Differentiability rating (closed-form derivative, autodiff-friendly, finite-difference-required)
- Accuracy regime (when does the approximation hold)
- Connection to a /physics composition (so the residual reuses library machinery)

Output: cost-tiered residual library, ready to insert into /physics `residuals/` directory.

### Phase 3 stream — architecture gap analysis + PINO integration design

**Stream S7 — UWBG amendment to architecture.**
Consumes all prior streams. Produces a concrete amendment proposal to IMPLEMENTATION-PLAN.md covering:

- **State vector additions** (T_e, μ_i, surface terminations, ...) with rationale
- **Canonical functional additions** (E_coupling pieces, S terms)
- **GENERIC operator additions** (L, M contributions)
- **Method additions** (any new primitives)
- **Template additions** (any new abstract templates)
- **Formula registry additions** (with typed signatures)
- **Observable bundle additions** (interface-resolved, field-resolved, hot-carrier-resolved)
- **Residual category additions** (reference-battery, convergence, structural-validity, hull-distance)
- **Cert obligation additions** (cross-regime identities for the new physics)
- **PINO integration interface** — typed boundary between /physics reference and /informed-operator predictions; autodiff/gradient interface; residual batching/sampling/weighting

Output: amendment-ready document plus open-question list for user decisions.

### Logistics

- All agents: `general-purpose` subagent type, `opus` model, foreground parallel dispatch within each phase
- Length expectation per stream: 3000-6000 words
- Read-only research; return findings in final message
- CS-only vocabulary discipline preserved
- Agents may ask clarifying questions via SendMessage; conductor (me) is responsible for answers

### Verification

The session is successful if Stream S7's amendment proposal:

1. Lists every new formula / template / method needed for UWBG-PINO training, with typed signatures
2. Specifies the residual-generation machinery (the missing structural concept) with concrete syntax
3. Identifies the PINO-library integration interface concretely (types + autodiff boundary)
4. Is honest about what remains out of scope (e.g., strongly-correlated systems, true RG flow)
5. Lists deferred decisions explicitly for user input

Secondary verification: the catalog from S6 should cover every observable in S1 with a defined closed-form residual.

---

## OUTSTANDING DECISIONS — RESOLVED BY USER

1. **Material scope: DIAMOND-CENTRIC, broad.** Diamond is the anchor material; include anything that can conceptually form a semiconductor with diamond. In practice this is:
   - **Diamond and diamond derivatives**: pristine diamond, doped diamond (N, B, P, Si, etc.), diamane, lonsdaleite
   - **UWBG companions**: c-BN, h-BN, AlN, GaN, Ga₂O₃, β-Ga₂O₃, AlGaN, AlN/GaN superlattices
   - **Contact metals**: W, Mo, Pt, Au, Ti, Ni, Al, Ta, TiN, WSi₂ (refractory metals dominate for thermal stability)
   - **Heteroepitaxial substrates**: SiC (especially 4H-SiC), Si (for diamond CVD), sapphire (for nitrides)
   - **Gate dielectrics**: Al₂O₃, HfO₂, AlN-as-dielectric, possibly SiO₂
   - **Interfaces between any of the above**

2. **Application: chips for harsh environments (e.g., inside a jet turbine).** This means:
   - **High-T operation** (≥500°C, possibly higher)
   - **Vibration / mechanical stress tolerance**
   - **High power density** (high E-field, high current density)
   - **Long-duration reliability under thermal cycling**
   - **Possibly radiation tolerance** (turbine ≠ rad, but harsh-env extends here naturally)
   - **Implications**: priorities are thermal stability of defects, breakdown field at elevated T, contact reliability under thermal cycling, electromigration under high current, defect kinetics under operating conditions

3. **Accuracy regime: two-tier.**
   - **Inner compute** (the library's ground-truth-generation path): does NOT need to be perfect. Used in initial training epochs to reduce search space.
   - **Residual accuracy**: critical. Residuals are physics-informed loss terms that constrain the PINO throughout all of training, and must be physically faithful — when the PINO predicts a wrong γ̂, the residual must reflect that wrongness accurately.
   - **Architectural implication**: /physics needs TWO LEVELS of fidelity per observable: a cheap-compute path (for fast generation of approximate labels), and a faithful-residual path (for accurate physics constraints). These are NOT the same code path. This is a major architectural distinction not previously called out.

4. **Strong correlation: OUT OF SCOPE confirmed.** Frustrated Wigner / spin liquids / Mott physics excluded from L1 substrate. (Reasonable for UWBG: large bandgap = far from Mott regime; correlation effects in deep-level traps are still bounded.)

5. **Training scheme: MULTI-SOURCE.** The PINO trains on FOUR sources simultaneously:
   - **(a) Cheap generated data** — from /physics's inner-compute path (fast approximations)
   - **(b) VASP ground-truth** — external high-fidelity DFT simulations
   - **(c) Experimental data** — real measurements
   - **(d) Residual training** — physics-informed loss from /physics's faithful-residual path

   **Architectural implication**: /physics has THREE export interfaces, not one:
   - **Generate**: produce approximate training labels (cheap, batched)
   - **Validate**: check predicted state against physics (the residual interface)
   - **Import**: accept external ground-truth (VASP files) and experimental measurements as cert evidence / training labels

---

## REVISIONS TO RESEARCH PLAN (based on user's answers)

### Material-scope revision (impacts S1, S2, S3)
- Anchor everything on **diamond**; treat other materials as "potential semiconductor partners with diamond" rather than as standalone scope
- **Specifically include metal-semiconductor interfaces** as a major subtopic (not just bulk semiconductor properties)
- Diamond derivatives (diamane, lonsdaleite) are first-class targets, not nice-to-have

### Application-scope revision (impacts S1, S3, S4)
- **High-T operation (≥500°C)** is a hard requirement → priorities shift toward:
  - Defect kinetics at high T (Stream S3 expand)
  - Thermal conductivity at high T (Stream S1 expand)
  - Breakdown field at elevated T (Stream S4 expand)
  - Contact reliability under thermal cycling (Stream S3 expand)
  - Electromigration under high current density (Stream S3 + S4)
- **Vibration / mechanical stress**: include fatigue residuals, defect generation under cyclic stress (Stream S3)
- **Long-duration reliability**: degradation-rate residuals, ageing physics (new subtopic in S3)

### Accuracy-regime revision (impacts S6 most, also S7 architecture)
- **Critical architectural distinction surfaces**: cheap-compute path vs faithful-residual path are SEPARATE
- S6 must produce TWO catalogs per observable:
  - **Cheap-compute formula** (for generating approximate training labels) — fast, autodiff-friendly, accuracy ~20% OK
  - **Faithful-residual formula** (for physics-informed loss) — accuracy-tight, may be more expensive, must be differentiable through the prediction
- S7 must reflect this in the architecture: residuals are NOT just inverses of compute paths; they are independently designed for fidelity

### Training-scheme revision (major impact on S5 and S7)
- S5 brief must explicitly address multi-source training:
  - How to balance physics-residual loss against label-supervised loss (with labels from VASP and experiment)
  - How to handle data hierarchy (cheap-generated < VASP < experimental in fidelity)
  - How to weight residuals against multi-source labels
  - Curriculum learning patterns (use cheap data first, refine with VASP, validate with experiment, regularize with residuals throughout)
- S7 must specify THREE interfaces, not one:
  - **Generate interface**: /physics → /informed-operator training labels (cheap-compute path)
  - **Validate interface**: /informed-operator predictions → /physics → residuals (faithful-residual path)
  - **Import interface**: external VASP outputs + experimental measurements → /physics as cert evidence / extra labels

### Out-of-scope confirmation
- Strong correlation excluded; defect deep-level traps treated semi-empirically (not full multi-reference)
- This simplification stated explicitly in the amendment for documentation

---

## POST-SCOPING CLEANUP (user-stated goal)

After this research session completes, the user wants to consolidate:

> "I want to get to a point where we can clean up all the docs weve been making, and concatenate them in this directory. Then I want to continue."

Concretely this means migrating from the plan-mode staging area to the project directory. The cleanup will need to:

1. **Move plan-staged content from `~/.claude/plans/` to `~/Desktop/Physics/Programs/n-Op/`**:
   - This plan file (resilient-stirring-horizon.md) → `n-Op/PROJECT-LOG.md` or `n-Op/design/scoping-log.md`
   - The prior plan file (please-read-the-slide-humble-sunrise.md) → archive or merge
   - The agent plan files for original 3-group research → `n-Op/research/group-{A,B,C}-*.md` (already noted in prior plan)
   - The audit reports → `n-Op/research/group-{A,B,C}-audit.md` (already noted)
   - The meta-audit → `n-Op/META-AUDIT.md`
   - The 4 framing reports (γ̂ brainstorm) → `n-Op/research/gamma-framing-{A,B,C,D,E}.md`
   - The 10 mesh-pair reports → `n-Op/research/gamma-mesh-{AB,AC,AD,...,DE}.md`
   - The 7 UWBG research streams (from this session) → `n-Op/research/uwbg-stream-{1..7}.md`

2. **Synthesize a coherent IMPLEMENTATION-PLAN.md amendment** rolling in:
   - The mesh-synthesis 8 corrections
   - The basis × form encoding factoring
   - The physicist's gap analysis (4 categories, in or out of scope)
   - The UWBG amendment from this research session
   - The two-tier accuracy distinction (cheap-compute vs faithful-residual)
   - The three-interface integration design (generate / validate / import)

3. **Update IMPLEMENTATION-PLAN.md** in place rather than appending — this is the consolidation user wants.

4. **The plan files in `~/.claude/plans/`** can then be considered archived; the project directory becomes the canonical home.

**This cleanup is OUT OF THE PLAN-MODE STEP** — it happens after the research session returns and synthesis is complete, with user approval. I'll surface it as a discrete subsequent step when we get there. The current plan-mode step is JUST the research session dispatch + synthesis.

---

## FINAL CONSOLIDATION — post-S7, post-prompt.md clarification

After all 7 streams returned and S7 produced the edit-ready amendment (~9700 words, 17 sections), user pointed me to `prompt.md` for clarification on `/physics`'s actual scope. Read it; asked clarifying questions; received decisive answers.

### Confirmed decisions from user

1. **PINO mode: Framing A — trajectory / state evolution.**
   - The PINO truly evolves state through the crystal.
   - GENERIC dynamics (dx/dt = L·δE/δx + M·δS/δx) remains the central organizing principle.
   - EOM-violation residual is primary.
   - 4-level BO hierarchy as state-evolution structure stands.
   - **S7 amendment is approximately CORRECT in shape, not overscoped.**

2. **/engineering is INTERNAL to /physics — not a sibling library.**
   - Defects, dopants, surfaces, interfaces, operating-condition effects all stay inside /physics.
   - The existing 11-bundle structure (with defect-resolved, surface-resolved, interface-resolved bundles in /physics) was right.
   - No library split.

3. **`prompt.md` reframe correctly interpreted:**
   - /physics provides the LAWS governing evolution (constitutive relations, GENERIC structure, residuals).
   - /physics does NOT hold the time-varying state values themselves — the PINO produces those as predictions.
   - The "unified state x(t)" is a TYPE that PINO predictions instantiate at each time step.
   - /physics's machinery evaluates whether predictions satisfy the constitutive laws via residuals.
   - This is exactly what the residual-generator factory + three exports (Generate / Validate / Import) capture.

### New architectural addition — applicability classifiers (NOT in S7)

User asked: "Do each of these properties apply to any lattice?" — answer: no. Properties have applicability domains.

Every property / observable / residual in the registry carries an applicability classifier:
```
applicability : (Crystal, Environment) → Bool
```

Examples:
- Band gap: applicable iff `is-insulator-or-semiconductor(Crystal)`
- Magnetic moment: applicable iff `has-magnetic-order(Crystal)`
- Schottky barrier: applicable iff `has-metal-semiconductor-interface(Crystal)`
- Defect formation energy for species X: applicable iff `defect-species-meaningful(X, Crystal)`
- Superconducting Tc: applicable iff `is-superconductor(Crystal)`

Coverage-mask discipline (from S5) extends to use these classifiers automatically. The PINO loss masks out non-applicable properties per training sample. **This is what makes the architecture compositional across crystal types** — same /physics interface for diamond, GaN, AlN, c-BN; each property's classifier handles whether it's meaningful for the specific crystal in question.

### Final architectural picture (consolidated)

```
n-Op/
├── physics/                ← single library; encompasses BOTH pristine crystals AND engineering aspects
│   ├── library/
│   │   ├── lattice-math/                ← user is actively working on this
│   │   ├── inputs/                      ← PeriodicityStructure + SiteDecoration + Environment
│   │   ├── state/                       ← UNIFIED STATE TYPE (data structure; PINO instantiates)
│   │   ├── canonicals/                  ← E[x], S[x] decompositions
│   │   ├── generic/                     ← L, M operators (define the laws)
│   │   ├── dynamics/                    ← total-evolution definition (dx/dt = L·δE/δx + M·δS/δx)
│   │   ├── methods/                     ← 12 computational primitives
│   │   ├── abstract-properties/         ← 18 templates
│   │   ├── formulas/                    ← 87 named formulas (S6 catalog)
│   │   ├── observables/                 ← 11 bundles (B1-B11)
│   │   ├── applicability/               ← NEW: per-property domain classifiers
│   │   ├── residuals/                   ← 7 categories + residual-generator factory
│   │   ├── cert/                        ← 10 cert obligations
│   │   ├── pino-bridge/                 ← Generate / Validate / Import exports
│   │   └── interfaces/                  ← Scalar, FieldOnGrid, Tensor, Response (causal?:Bool)
│   │
│   └── research/                        ← migrated from staging area; see migration list below
│
├── informed-operator/                   ← the PINO; consumes /physics; trains state evolution
│   └── design/                          ← S5 methodology lives here
│
└── interface/                           ← user surface (unchanged)
```

### Concrete file-migration list (executes immediately after ExitPlanMode)

| Staging source | Destination | Action |
|---|---|---|
| ~/.claude/plans/resilient-stirring-horizon.md (this file) | n-Op/physics/research/scoping-log.md | Move (canonical history) |
| ~/.claude/plans/please-read-the-slide-humble-sunrise.md | n-Op/physics/research/scoping-history-prior.md | Move (archive) |
| Original 3-group research agent outputs | n-Op/physics/research/group-{A,B,C}-research.md | Move |
| 3-group audit reports | n-Op/physics/research/group-{A,B,C}-audit.md | Move |
| Meta-audit | n-Op/META-AUDIT.md | Move |
| 4 γ̂-framing reports (A/B/C/D) | n-Op/physics/research/gamma-framing-{A,B,C,D}.md | Move |
| γ̂-framing E report | n-Op/physics/research/gamma-framing-E.md | Move |
| 10 γ̂-mesh-pair reports | n-Op/physics/research/gamma-mesh-{AB,AC,AD,AE,BC,BD,BE,CD,CE,DE}.md | Move |
| Stream S1 — UWBG observable catalog | n-Op/physics/research/uwbg-observable-catalog.md | Move |
| Stream S2 — CSP + heterostructure | n-Op/physics/research/csp-heterostructure.md | Move |
| Stream S3 — Defects/doping/surfaces/interfaces/high-T | n-Op/physics/research/defects-surfaces-interfaces.md | Move |
| Stream S4 — Non-equilibrium/high-field/hot-carrier | n-Op/physics/research/non-equilibrium-high-field.md | Move |
| Stream S5 — PINO residual methodology | n-Op/informed-operator/design/residual-loss-methodology.md | Move (belongs in /informed-operator, not /physics) |
| Stream S6 — Deduplicated cheap-residual catalog + factory spec | n-Op/physics/research/residual-generator-catalog.md | Move |
| Stream S7 — Architecture amendment | n-Op/physics/research/amendment-s7-source.md AND apply edits to n-Op/IMPLEMENTATION-PLAN.md | Move + apply |
| (NEW) Applicability classifier addition | n-Op/physics/research/applicability-classifiers.md | Create (new doc explaining the addition) |

Most agent outputs live in ~/.claude/projects/*/tasks/*.output JSONL transcripts. The user-visible final report is what each agent returned as its final message — those are the canonical content to extract and write as plain markdown to the destinations above.

### Post-migration steps (in order)

1. Apply S7's edits to n-Op/IMPLEMENTATION-PLAN.md:
   - In-place edits to existing §3.1, §5.3, §7, §8, §10, §11, §12, §13
   - Append new §19–§25 (residual-generator factory, three pino-bridge exports, multi-source training, out-of-scope, outstanding decisions, verification, post-amendment migration)
   - Add applicability classifiers as a sub-section under §10 (observable bundles) or as new §26

2. Extract S6's 87-formula catalog into a machine-readable manifest at n-Op/physics/library/formulas/registry-manifest.{scm|csv|yaml} (format depends on outstanding-decision #1: implementation language).

3. Create n-Op/physics/library/cert/reference-data/ and populate with S1-S4 tabular content (defect formation energies, diamond-metal interface table, material constant anchors) so cert obligation-8 (reference-battery-versioned) has machine-readable source-of-truth.

4. Single git commit titled "S1-S7 research integration; UWBG retargeting amendment; lattice-math foundation start" recording the move.

5. Resolve outstanding decisions in separate focused commits before starting Phase 1:
   - Implementation language (highest urgency; blocks Phase 1)
   - ReferenceCache backend (default SQLite + SHA-pinned schema)
   - Surrogate-net infrastructure build-vs-adopt
   - PDE-mesh format + adjoint library
   - Coverage-mask format (default sparse from the start)
   - Curriculum schedule confirmation (defaults 0.10, 0.60, 0.90)
   - Active-learning loop integration (default: lives in /interface, not /physics)

### Immediate user-facing next step

User is actively working on **lattice math generation**. After this consolidation lands, the natural concrete first piece of `/physics` to build is:
- `physics/library/lattice-math/` — Bravais lattices, space groups, basis vectors, reciprocal-space machinery
- `physics/library/inputs/periodicity-structure.{rkt|py|ml}` — the typed wrapper consumed by everything else

This is the foundation everything else hangs off. Building it correctly unblocks the rest of /physics.

### Verification of consolidation completion

The consolidation is complete when:
1. All 22 staging artifacts listed in the migration table have been moved/extracted to their destinations.
2. n-Op/IMPLEMENTATION-PLAN.md has the S7 amendment applied in place.
3. The applicability-classifier addition has been documented under the appropriate plan section.
4. A single commit captures the migration.
5. n-Op/physics/research/ contains the full provenance (every stream's final report).
6. n-Op/informed-operator/design/ contains the PINO methodology (S5).
7. The staging-area plan files in ~/.claude/plans/ can be considered archived.

### Outstanding (do NOT resolve in this plan-mode step)

- Implementation language decision (requires user input; S7 default-recommends Python+JAX)
- The 6 other outstanding decisions in S7 §15
- Whether to proceed immediately to lattice-math generation or to address an outstanding decision first

---

End of plan. Ready for ExitPlanMode → execute the file migration + amendment application.

---
