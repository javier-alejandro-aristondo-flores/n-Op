# n-Op — Architecture

The conceptual specification for `n-Op`: what the system is, the state it
defines, the laws that govern it, and the closed vocabularies from which every
observable and residual is composed. This document is the **single source of
truth for the project's vocabularies and counts**; the implementation plan
(`implementation-plan.md`) gives detailed signatures and a build sequence and
refers back here for the model.

---

## 1. Purpose and scope

`n-Op` ("neural operator") trains a **physically-informed neural operator
(PINO)** that predicts the time evolution of the state of a crystalline material
under operating conditions. The downstream target is the design of **durable
high-performance ultra-wide-bandgap (UWBG) semiconductor chips for harsh
environments** — chips that must function inside, for instance, a jet turbine:
high temperature (>500 °C), thermal cycling, mechanical vibration, high field,
high current density, possibly radiation.

`/physics` does not represent the *state values* of a system; it is the way to
**instantiate a physical system** (a crystal) and define the laws through which
something else (the PINO) is evolved. It defines what a state *is*, what laws
govern its evolution, and how to evaluate whether a candidate state satisfies
those laws. Properties of the crystal may themselves have to be predicted, and
some perturbations alter what those properties do to the lattice — so the
properties are derived from state, never hard-coded.

**Minimum viable demonstration (MVP):** model **diamond**, with three target
capabilities:

1. Crystal-structure prediction (including diamond-compatible heterostructures).
2. Electron-cloud diffusion through the lattice.
3. Heat diffusion through the lattice.

The MVP discipline is **"as much closed-form / computationally feasible
expressions as possible"** and **purpose-built tools**. The MVP is
diamond-centric; the broader material scope includes anything that forms a
semiconductor with diamond: c-BN, AlN, GaN, β-Ga₂O₃, AlGaN; refractory contact
metals (W, Mo, Pt, Ti, Ni, Ta, TiN, WSi₂); substrates (SiC, Si, sapphire); gate
dielectrics (Al₂O₃, HfO₂, AlN-as-dielectric).

**The comprehensiveness of the spec is the point**, even though implementation
is diamond-first. That distinction — comprehensive spec, diamond-first build —
runs through everything below. The concrete diamond-first build target — the
minimal slice of this spec the three capabilities require — is carved out in
`mvp-slice.md`.

---

## 2. The library landscape

`n-Op` is partitioned into three sibling libraries.

- **`/physics`** — a substrate-agnostic reference oracle. It encodes the laws of
  the system: state structure, dynamics, observable definitions, residual
  definitions, and certification obligations. It does **not** hold time-varying
  state values, train neural networks, integrate trajectories, or wrap external
  DFT codes at runtime. This document is primarily about `/physics`.
- **`/informed-operator`** — the PINO itself. It consumes `/physics` and learns
  the time-evolution operator. Design notes live under
  `informed-operator/design/`.
- **`/interface`** — the user-facing surface. Out of scope for the current
  design pass.

Engineering aspects (defects, dopants, surfaces, interfaces, operating-condition
effects) live **inside** `/physics`, not in a separate library.

---

## 3. Inputs — the descriptor side

Three physically orthogonal inputs fully specify "what crystal, in what
conditions":

1. **`PeriodicityStructure`** — the spatial skeleton: dimensionality
   `d ∈ {0,1,2,3}`, lattice vectors `{a_i}`, periodicity flags. The geometry of
   repetition (Bravais lattice, space group, cell vectors `h`).
2. **`SiteDecoration`** — the per-position content: which species sit at which
   Wyckoff positions; orbital basis; optional spin, charge state, occupancy, and
   a tag (`host` / `defect` / `adsorbate` / `substrate` / `impurity`). Defects,
   surfaces, adsorbates, magnetic configurations, charged systems, and alloys
   are **special cases of `SiteDecoration`**, not new top-level types.
3. **`Environment`** — external conditions: temperature, pressure (or volume),
   chemical potentials, applied electric/magnetic fields, applied stress,
   temperature gradient, carrier-injection conditions.

`Reference` (a bag of `(Crystal, Environment, weight)` baselines) and `Property`
(the requested observable) are **not** top-level inputs: `Reference` composes
from the three above and belongs to the cert layer; `Property` is an output
request, a parameter of `predict`/`residual`.

---

## 4. The unified state

The instantaneous state is the 7-tuple

```
x(t) = ( h,      cell vectors                       ∈ GL⁺(3, ℝ)   (3×3 real)
         R_I,    ion positions                      ∈ ℝ^{3N}
         P_I,    ion momenta                        ∈ ℝ^{3N}
         Π_h,    cell momentum (Parrinello–Rahman)  ∈ ℝ^{3×3}
         Z_I,    species labels (immutable)         discrete
         γ̂,      one-body density matrix            2×2 Pauli-spinor operator
                 (Pauli-spinor for magnetism)       on (r, r'; t)
         A )     external EM vector potential        ∈ ℝ³ field A(r,t)
```

These are the **irreducible degrees of freedom**. Phonon distributions
`n_{q,s}`, carrier distributions `f_n(k,r)`, surface coverages `θ_i`, electron
and lattice temperatures, current density, internal fields, defect populations,
and composition vectors are all **emergent** — coarse-grainings, Bloch
transforms, or semiclassical limits of `x(t)`. Adding any of them to the state
would create a constraint manifold tying it back to the irreducible DOFs and
reintroduce the integration pathology the formulation avoids.

`x(t)` is a **type** that the PINO's predictions instantiate at each time step.
`/physics` does not hold values of `x(t)`; it defines what `x(t)` is and how to
test a candidate against the laws.

---

## 5. Dynamics — GENERIC

Time evolution uses the **GENERIC** form (General Equation for the
Non-Equilibrium Reversible–Irreversible Coupling):

```
dx/dt = L · δE/δx + M · δS/δx
```

- `E[x]` — total energy functional.
- `S[x]` — total entropy functional.
- `L` — Poisson operator: antisymmetric; reversible dynamics.
- `M` — friction operator: symmetric, positive semidefinite; irreversible
  dynamics.
- Degeneracy conditions: `L · δS/δx = 0` (reversible part conserves entropy) and
  `M · δE/δx = 0` (dissipative part conserves energy).

Each traditional regime of multiphysics is recovered as an **extraction** of
this single equation. Static observables are equilibrium readouts (fixed points
where `dx/dt = 0`); time-evolving observables are trajectory readouts. The
PINO's primary loss term is the **EOM-violation residual**
`‖dx/dt − (L δE/δx + M δS/δx)‖²`.

### Canonical functionals and operators

The two functionals decompose as:

```
E[x] = E_kin(ions)      Σ_I |P_I|²/2M_I + tr(Π_hᵀΠ_h)/2W
     + E_BO(R, h)       min_γ̂ ⟨Ĥ_electronic⟩[γ̂; R, h]
     + E_KS[γ̂]          kinetic + Hartree + exchange-correlation on γ̂
     + E_EM[A]          (1/8π) ∫ (|E|² + |B|²) dr
     + E_coupling       electron-phonon · spin-orbit · magneto-elastic · optical-electronic

S[x] = S_vib           vibrational entropy from the phonon spectrum
     + S_electronic     Fermi–Dirac entropy of the γ̂ spectrum
     + S_config         configurational entropy of coarse-grained DOFs
```

The two operators decompose as:

```
L (antisymmetric Poisson):
  · symplectic on (R, P)         canonical ion phase space
  · symplectic on (h, Π_h)       Parrinello–Rahman cell phase space
  · Liouville–von Neumann on γ̂   (1/iℏ) [Ĥ_KS, ·]
  · Maxwell on A                 Hamiltonian form of the EM field
  · semiclassical streaming      on emergent distributions

M (symmetric, positive semidefinite):
  · phonon–phonon scattering     three- and four-phonon collision kernels
  · electron–phonon scattering   Fermi-golden-rule from g_{nm,ν}(k,q)
  · spin relaxation              orientation-preserving form  S × (S × H_eff)
  · radiative damping            spontaneous-emission rate (optical)
  · chemical rate matrix         symmetrized W_ij from detailed balance
```

These pieces are assembled across the four levels of §6; each level contributes
the `E`, `S`, `L`, and `M` terms that act on its irreducible state.

### The nine regimes as extractions

| Regime | Extraction |
|--------|-----------|
| Structural | Critical points of `E` at `T = 0` (or `F` at `T > 0`); 1st derivatives |
| Mechanical | 2nd strain-derivatives of `F` at equilibrium |
| Thermal | Eigendecomposition of `∂²E_BO/∂u²` (phonons); BTE for phonon distribution |
| Electronic | SCF as gradient flow on `E_KS`; TDKS as Liouville on `γ̂` (pure `L`) |
| Magnetic | spin-doubled `γ̂`; spin EOM = `L` (precession) + `M` (orientation-preserving relaxation `S × (S × H_eff)`) |
| Optical | Response of `γ̂` to `A(t)` via `L`; absorption via `M` (radiative damping) |
| Transport | BTE on emergent carrier distribution: `L` (streaming) + `M` (collisions) |
| Thermodynamic | min `F` at fixed `(T, V, N)`; convex hull of `{F_φ}` |
| Chemical/surface | Master equation on configurations (`M` = rate matrix); minimum-energy-path search on `E_BO` |

The per-regime derivations of each extraction from the unified structure are in
`implementation-plan.md` and grounded in `physics/research/group-{A,B,C}-*.md`.

---

## 6. The 4-level Born–Oppenheimer hierarchy

Within `x(t)`, components separate into four levels whose dependencies flow
strictly upward (Level 4 → 3 → 2 → 1):

- **L1 — Quantum electronic substrate.** Operates on `γ̂(r,r';t)` and `A(r,t)` at
  fixed `(R, h)`. Regimes: electronic, optical, magnetic. Math: Kohn–Sham /
  TDKS / TDCSDFT, Hohenberg–Kohn, Runge–Gross, Liouville–von Neumann.
- **L2 — Born–Oppenheimer surface.** Operates on `(R, P, h, Π_h)` with immutable
  `Z`. Uses `E_BO(R,h) = min_γ̂ E[γ̂; R, h]`, Hellmann–Feynman forces, DFT
  stress. Regimes: structural, mechanical. Math: variational on `(R,h)`, strain
  expansion, Parrinello–Rahman dynamics.
- **L3 — Equilibrium statistics on the BO surface.** Bose–Einstein,
  Fermi–Dirac, Maxwell–Boltzmann over L1/L2 spectra. Regimes: thermal,
  thermodynamic. Math: partition functions, free energies, quasi-harmonic
  approximation, convex hull.
- **L4 — Non-equilibrium kinetics.** Distributions over phase space; full
  GENERIC `L + M`. Regimes: transport, chemical/surface. Math: Boltzmann
  transport, Kubo / Green–Kubo, master equation, Marcus theory, transition-state
  theory, minimum-energy-path search.

Each level uses lower levels as inputs but introduces its own irreducible state.
A regime is a navigational *view* across the levels that contribute to it
(thermal spans L3 statistics and L4 phonon transport).

### Dressing layers (one-shot vs iterative)

Within L1, corrections that "dress" the bare substrate are organized into a
two-tier split:

```
Layer 1      Bare substrate.
Layer 1.25   One-shot closed-form dressing — pure functions, no iteration.
             V1 members: G₀W₀ quasi-particle energies; first-order
             self-consistent phonons (SCP); the linear-response sub-stage
             producing Z*, ε∞, χ∞; the LO/TO non-analytic correction;
             one-shot diagonalization; one-shot topological invariants.
             Cert vocabulary: OneShotCert = WellPosed | IllPosed.
Layer 1.75   Iterative fixed-point dressing — DEFERRED to V2 in code, SPECIFIED
             for forward compatibility. Members: self-consistent GW, full
             SCPH/SSCHA, DMFT, BSE iterative variants, self-consistent polaron.
             Cert vocabulary: IterativeResult = ConvergedAt | DivergedAt | Stale.
             Each member gets a bespoke combinator, NOT a shared primitive.
Layer 2      Property machinery (interface unchanged; dressed carriers are
             type-substitutable for bare).
Layer 3      PINO (lives in /informed-operator).
```

The diamond MVP runs entirely against Layer 1.25, preserving the closed-form
discipline. (Diamond needs only two dressings: G₀W₀ — Kohn–Sham underestimates
the diamond gap by ~30%, G₀W₀ corrects to ~5.5 eV vs measured 5.47 eV — and
first-order SCP, marginal at 773 K and growing above 1500 K.) Comprehensiveness
is preserved via the V1 specification of Layer 1.75 even though no V1 code
implements it.

---

## 7. The three-layer architecture (computational role)

Orthogonal to the hierarchy of §6, the library partitions by **what kind of work
each piece does**:

- **Layer 1 — Synthesis pipeline.** Takes `(G, q, W, k)` — space group, momentum
  point, Wyckoff orbit, orbital basis — and produces a `CrystalSystem` via six
  stages: Lattice Construction → Fiber Construction → Symmetry-Constrained
  Hamiltonian Family → Topological Phase Selection → Assembly → Verification.
  Polynomial-time and well-specified.
- **Layer 2 — Property machinery.** The closed registries (§8): methods,
  templates, formulas, and observable bundles.
- **Layer 3 — PINO.** Consumes `/physics`'s definitions, predicts state
  trajectories, trains against residuals. Lives in `/informed-operator`.

The BO hierarchy (§6) partitions *what state component lives where*; the
three-layer view partitions *what computational role each piece plays*. They are
orthogonal views of one library.

---

## 8. Canonical vocabularies and counts (single source of truth)

Every other document references these numbers rather than restating them.

| Vocabulary | Count | Closed? |
|---|---|---|
| Top-level inputs | 3 | yes |
| State DOFs | 7-tuple | yes |
| BO hierarchy levels | 4 | yes |
| Dressing layers | 1 / 1.25 / 1.75 / 2 / 3 | yes |
| Computational methods | 12 (+2 sub-methods) | yes |
| Abstract-property templates | 20 | yes |
| Named formulas | 102 substantive (+2 rejected markers) | yes — see `formula-registry.md` |
| Observable bundles | 11 (B1–B11) | yes |
| Residual categories | 7 | yes |
| Cert obligations | 10 | yes |
| Layer-0 typeclasses | 4 | yes |

### 8.1 Twelve computational methods

Closed vocabulary; instances are programs in this vocabulary:

`state-readout`, `algebraic-combination`, `functional-differentiation`,
`variational-minimization`, `spectral-decomposition`, `spectral-aggregation`,
`linear-response`, `path-search`, `convex-optimization`, `kinetic-evolution`,
`statistical-sampling`, `symmetry-projection`.

Plus two registered sub-methods: `field-line-integral` (under `path-search`) and
`interface-tunneling` (under `linear-response`).

### 8.2 Twenty abstract-property templates

Parametric method-chain templates; concrete observables are instantiations. The
discipline: collapse "N observables with the same shape" into "1 template × N
argument tuples." Detailed signatures in `implementation-plan.md §8`.

*General (12):*

| Template | Produces |
|---|---|
| `StateReadoutOf` | lattice parameters, bond lengths, charge density, magnetic moments |
| `AlgebraicOf` | any named-formula combination (formation energy, surface energy, hardness, …) |
| `SecondDerivativeOf` | elastic constants, force constants, polar susceptibility |
| `SpectrumOf` | band structure, phonon dispersion |
| `SpectralAggregateOf` | DOS, phonon DOS, heat capacity, vibrational/electronic free energy |
| `ResponseOfTo` | dielectric function, conductivity(ω), exchange interactions |
| `PathStationaryOf` | migration barrier, reaction pathway |
| `KineticEvolutionOf` | electronic/thermal conductivity, ionic diffusivity |
| `ClassifyOf` | space group, Wyckoff orbit, crystal-structure class |
| `ComparisonOf` | defect characterization, surface-region comparison |
| `RadiativeEmissionOf` | photoluminescence |
| `MicrokineticSteadyStateOf` | catalytic activity, turnover frequency (driven steady state) |

*Renormalization / configurational / symmetry (3):*

| Template | Produces / notes |
|---|---|
| `SelfConsistentRenormalizationOf` | fixed-point dressing; method selector ∈ {SCP, SSCHA, GW, BSE-iterated, polaron}; emits `IterativeResult` |
| `ConfigurationalFreeEnergyOf` | composition-dependent free energy; parameterizations {ClusterExpansion (discrete, T=0), Redlich–Kister (continuous, finite-T excess Gibbs), Bragg–Williams} — **distinct, not instances of each other** |
| `SymmetryAdaptedHamiltonianOf` | constructive emission of the most general symmetry-allowed `H(k)` from (space group, Wyckoff orbits, orbital basis, neighbor shells); the substrate every composed material is classified against (§14) |

*Domain interface / defect / thermo (5):*

| Template | Produces / notes |
|---|---|
| `InterfaceEquilibriumOf` | bicrystal equilibrium with charge transfer + band alignment (Schottky barrier, band offset, interface dipole) |
| `SelfConsistentChargeBalanceOf` | charge-neutral Fermi level + defect populations; closes the L3↔non-equilibrium dependency cycle via a same-pass fixed point |
| `HarmonicStiffnessHessianOf` | mass-weighted dynamical matrix with acoustic-sum-rule enforcement and Born-effective-charge correction (a specialization of `SecondDerivativeOf` whose symmetrization is a template-level concern) |
| `BiSlabGrandPotentialOf` | grand potential of a two-slab system (adhesion, interface formation energy, debonding) |
| `MassActionEquilibriumOf` | equilibrium composition of a reaction set (point-defect / gas-exchange / adsorbate equilibria) — an equilibrium readout, distinct from `MicrokineticSteadyStateOf`'s driven steady state |

Bulk-boundary correspondence is **not** a template; it is handled at the cert
layer (obligation-7, a `DiscreteStructure` morphism over the topology atlas,
§14).

### 8.3 102 named formulas

Closed registry of typed, fully-parameterized algebraic formulas, named by
behavior (person-attribution names appear only as parenthetical literature
pointers). The canonical machine-readable list is
`physics/library/formulas/registry-manifest.csv` (102 substantive rows + 2
markers for relations that are enforced architecturally and therefore *not*
residualized: force = −∇energy, and equivariance). Rows 1–87 are grounded in the
domain research (`physics/research/`); rows 88–102 are the linear-response and
topology-atlas extensions. Each formula carries a typed signature, a cost tier
`T0..T3`, a differentiability tag `D0..D4`, and an applicability classifier
(§13). See `formula-registry.md` for the narrative index.

### 8.4 Eleven observable bundles

Organized by physics domain (the `B1..B11` labels used in the registry):

| ID | Bundle | Primary level |
|---|---|---|
| B1 | electronic-structure | L1 |
| B2 | phonon | L2 |
| B3 | transport | L4 |
| B4 | defect-resolved | L2/L3/L4 |
| B5 | surface-resolved | L2 |
| B6 | interface-resolved | L2 |
| B7 | mechanics | L2 |
| B8 | thermodynamics | L3 |
| B9 | non-equilibrium-operating | L4 |
| B10 | static-validity | L2 |
| B11 | degradation | L4 |

(A file tree may additionally group observable *modules* by output data-shape —
BZ-resolved, energy-resolved, real-space, tensor-indexed, etc. — but the
canonical, residual-driving grouping is the eleven physics-domain bundles above.)

---

## 9. The central object — γ̂ — and its representation

The one-body density matrix `γ̂` is the most demanding object: a single logical
entity with multiple inequivalent encodings, where different operations are cheap
on different encodings, and which must support efficient time evolution. Five
representation strategies were explored and synthesized into a layered hybrid.

### 9.1 The strategies

- **Codata / coalgebraic (interface):** `γ̂` is opaque; only destructors are
  exposed (apply, trace, density, eigendecomposition, …). What `/physics`
  exposes to callers.
- **Typed term algebra (staging):** `γ̂` as a term in a grammar; conversions are
  rewrites under equational laws; used for compile-time symbolic composition.
- **E-graph with equality saturation (optional optimization):** cross-cutting
  encoding selection at staging time. May be omitted in V1.
- **Pullback bundle of synchronized encodings (runtime representation):** used
  for `γ̂` specifically; **single-slot in V1** (one canonical encoding per
  material, chosen at compose-time), generalizable to multi-slot in V2.
- **Tensor network with cost-aware contraction (runtime substrate):** the
  numeric layer where contractions actually run.

### 9.2 Read path vs write path

The hybrid is **not** a linear stack through which every operation passes. There
are two paths:

```
READ PATH (dominates trajectory evolution):
    interface ──destructor──▶ tensor-network substrate
    (apply Ĥ, density, trace, eigendecomposition — lazy materialization;
     no term staging, no bundle sync)

WRITE PATH (construction, self-consistent step, time-stepping):
    interface ▶ term-algebra ▶ planner ▶ (e-graph?) ▶ (encoding) ▶ substrate
```

Most `γ̂` traffic takes the short read path; a naive linear implementation would
pay term-staging cost on every read (~5× overhead). The consistency witness
between encodings is a first-class destructor on the interface. Self-consistency
(when `Ĥ[γ̂]` depends on `γ̂`) is *structured* by the coalgebraic fixed-point form
but is **not solved by it** — the convergence work still happens via explicit
iteration above the substrate.

### 9.3 Encoding vocabulary: basis × form

An encoding factors into two orthogonal axes:

```
Basis ∈ { Real, Reciprocal, Wannier, NaturalOrbital, SymmetryAdapted }
Form  ∈ { Dense, Sparse, BlockDiag, LowRank }
```

First-class V1 pairs: `(Reciprocal, BlockDiag)` for periodic substrates;
`(Real, Sparse)` for defects/surfaces/amorphous regions; `(Wannier, Sparse)` for
interface layers and dangling bonds; `(NaturalOrbital, LowRank)` for low-rank
substrates; `(SymmetryAdapted, BlockDiag)` for the output of
`SymmetryAdaptedHamiltonianOf`. A deterministic selection function
`canonical_encoding(lattice, decoration, environment) → (Basis, Form)` picks one
slot per material at compose-time; transcoders convert on demand.

### 9.4 Open questions (not yet resolved)

The hybrid's *shape* is settled; the following are genuinely open and should be
decided before or during the first `γ̂` implementation:

- **The planner is an unnamed component.** Encoding-choice policy lives neither
  in the interface nor in the term algebra; it is the "planner" that consumes
  the term structure plus the pending call pattern. Its interface is not yet
  specified.
- **Approximate vs exact equality (ε-equivalence).** If the interface contract
  is bisimulation-up-to-ε, the e-graph layer needs error-tracking; this is
  unsolved and is the main reason the e-graph layer is "optional" rather than
  load-bearing.
- **Materialization policy.** When to force vs defer materialization on the read
  path is a workload-dependent hyperparameter with no principled default yet.
- **Long-trajectory drift and rank growth.** Encodings degrade over many steps
  (low-rank densifies, sparsity fills in); a refresh/rebalance policy is
  undefined.
- **Rank-dependent applicability.** The pullback-bundle's value rests on cheap
  consistency checks, which become prohibitive for higher-rank objects
  (four-index BSE, BTE collision matrices); those objects are kept out of the
  bundle and stay on the substrate directly.

---

## 10. The Layer-0 typeclass alphabet

Every observable output is typed by three orthogonal axes plus a discrete
bucket, captured as four typeclasses. (Presented here as language-neutral typed
pseudocode; the implementation language is undecided — see §17.)

- **`Quantity` (Value axis).** Units, equality-with-tolerance, behavior under
  change of units/basis. Every numeric output is a `Quantity`. Carries
  `unitsOf`, `approxEq(tol)`, `rescale`, and `combineTol` (how tolerances
  compose under arithmetic — e.g. `κ = κ_el + κ_ph`; associative, commutative,
  monotone; per-instance choice of max-absolute or root-sum-square).
- **`Sampleable` (Shape axis).** Whether the output is a function on a domain,
  with `evaluate : f → Domain → Codomain` total on its claimed domain. Optional
  à-la-carte capabilities:
  - `Integrable` — `integrate(measure)`; linear, change-of-variables.
  - `Differentiable` — `derivative : f → Domain → Maybe Tangent`, total on
    `Domain \ exceptionSet` (phase transitions, band crossings,
    charge-transition levels live in the exception set); carries a `chart` tag so
    derivatives only compare across instances with matching charts.
  - `Restrictable` — `restrict(subdomain)`.
- **`HasAnalyticStructure` (Constraint axis).** Global analytic laws as
  witnesses — causality/Kramers–Kronig, hermiticity, convexity, Onsager
  involution, sum rules. A `Witness` is a list of `(Local | Global)`-tagged
  witnesses (one output can carry several simultaneously); `certifyAnalytic`
  returns the witnesses or a typed failure.
- **`DiscreteStructure` (Combinatorial axis).** Integer invariants,
  classification groups, holonomy spectra, polyhedra, convex hulls — objects in a
  discrete category with `identity`, `compose`, and `isoEq`. Not `Quantity` (no
  units), not `Sampleable` (no domain). The topology-atlas outputs live here.

The old names `Scalar / FieldOnGrid / Tensor / Response` survive only as
aliases over common parameterizations (`Response = Sampleable + Integrable +
Differentiable + HasAnalyticStructure(KramersKronig)` over a frequency domain,
etc.). Cert obligations (§12) map onto these axes mechanically.

---

## 11. Residuals and the residual-generator factory

Residuals are the physics-informed loss terms the PINO trains against. **Seven
categories:**

1. **EOM-violation** (primary): `‖dx/dt − (L δE/δx + M δS/δx)‖²`.
2. **Degeneracy:** `‖L δS/δx‖² + ‖M δE/δx‖²`.
3. **Conservation:** energy, particle-number/charge, momentum/crystal-momentum,
   spin.
4. **Positivity:** `M ⪰ 0`, `f ∈ [0,1]`, `ρ ≥ 0`, `ω² ≥ 0`, `σ ⪰ 0`, `|S_i| = 1`.
5. **Algebraic identities:** Kramers–Kronig; f-sum `(2/π)∫ω·Im ε dω = ω_p²`;
   acoustic sum `Σ_J Σ_R Φ_{IαJβ}(R) = 0`; detailed balance; Einstein relation;
   Onsager symmetry; Maxwell relations; method-equivalence (BTE-σ ≡ Kubo-σ in
   linear response).
6. **Static-validity** (snapshot only, no environment): valence-bond-sum charge
   balance, Born stability, dynamical stability, space-group equivariance.
7. **Thermodynamic-consistency** (snapshot + environment): hull-distance,
   formation-energy-from-references, solubility, mass-action, carbide-formation.

Categories 6 and 7 are disjoint by input domain (static-validity takes the
snapshot alone; thermodynamic-consistency adds environment). The total residual
is a weighted sum; the cert layer verifies all weights ≥ 0 and dimensional
consistency.

**The residual-generator factory** is the load-bearing PINO-facing machinery.
Every formula registers itself at load time, and the factory generates a
`ResidualGenerator` record per formula carrying: typed signature, bundle, DAG
layer, cost tier, differentiability tag, source tag
(`cheap-generate | faithful-residual | ground-truth-bridge | cert-only`),
dressing tag (`bare | dressed(scheme, cert, T)`), optional canonical encoding,
optional bias-correction, applicability classifier, forward/backward/loss
closures, weight policy, sampling policy, dependencies, and an adjoint-cert
verdict. A **registration-time adjoint-existence gate** rejects D2 formulas with
no validated adjoint (vJp vs JvP within tolerance on sampled points). Detailed
record definition in `implementation-plan.md §19`.

---

## 12. Cert — ten obligations

Cert is a first-class deliverable: schema, deterministic text renderer, freeze
fixture + tamper tripwire, and a high-precision oracle cross-check. The
certificate emitted for any prediction is an inert s-expression carrying scalar
verdicts plus numeric witnesses for failures.

1. Symmetry equivariance.
2. Bounds (physical positivity).
3. Analytic limits (where closed-form answers exist).
4. Reference battery (frozen reference data on a held-out crystal battery).
5. Conservation laws.
6. GENERIC degeneracy + named-formula consistency across equivalent
   compositions.
7. Bulk-boundary correspondence (a `DiscreteStructure` morphism: for a bulk
   classified as `X_BS = k`, the slab must carry boundary states with
   multiplicities given by a lookup table indexed on
   `(k_generator, boundary_orientation)`).
8. Reference-battery-versioned (versioning discipline on obligation 4; reads
   `physics/library/cert/reference-data/`, looks up rows by
   `(Property, Material, Environment)`, trips at `|predicted − reference|/σ > 3`
   with the row's provenance).
9. Surrogate-net validity (for D4 surrogate formulas).
10. Adjoint-existence at registration (the gate of §11).

Each obligation maps onto a Layer-0 axis (§10), making the cert checkers generic
functions over the typeclasses.

---

## 13. Applicability classifiers

Every property, observable, and residual carries a typed predicate
`applicability : (Crystal, Environment) → Bool`. The PINO loss masks out
non-applicable properties per-sample, so the model is neither falsely supervised
(e.g. predicting a band gap for a metal) nor penalized for an undefined quantity.
This is what makes the architecture **compositional across crystal types**: the
same interface accepts diamond, GaN, AlN, c-BN, refractory metals — each
property's classifier decides whether it is a meaningful question for that
crystal (band gap iff insulator/semiconductor; Schottky barrier iff
metal-semiconductor interface; polar-optical scattering iff polar — false for
diamond; carbide-formation iff the interface includes a carbide former — false
for Pt/diamond, true for Ti/diamond).

V1 commitment: every registry entry gets an explicit `applicability` field;
always-true stubs are acceptable for V1.0 and refined incrementally. Open
questions (deferred): soft `[0,1]` classifiers, classifier composition under
perturbation, and current-vs-initial-state evaluation for trajectory training.

---

## 14. Topology as a navigational atlas

The architecture treats a *material* as a composition
`(Lattice + SiteDecoration + Laws) → Material` whose properties are derived,
never hardcoded. The **topology atlas** makes that derivation navigable. At
compose-time it computes, for each composition:

```
TopologyAtlasEntry =
  ( space-group   : 1..230 (+ magnetic)
  , AZ-class      : ten-element symmetry-class label
  , X_BS          : finite abelian symmetry-indicator group
  , EBRs          : elementary band representations
  , compatibility : compatibility-relation matrix )
```

`X_BS` is computed in polynomial time via Smith Normal Form on the integer
matrix of orbit-induced representations. (117 of 230 space groups have
non-trivial `X_BS` under time-reversal in the spin-doubled setting; max
`|X_BS| = 72`.) Cheap parts — `X_BS` class, orbit-representation decomposition,
compatibility check, boundary-mode multiplicity via the indicator lookup — are
always-on at compose-time. Expensive global integrals over the dual-space grid
(Wilson loops, Chern integrals, Z₂ via Pfaffian) are opt-in per observable.

The atlas gives the PINO a navigational signal: `X_BS` tells the model which
compositions are topologically equivalent, so gradients in one inform the other.
Topology is the map, not a feature. Atlas outputs are `DiscreteStructure`
instances (§10), and cert obligation-7 is literally a morphism over them.

---

## 15. Two-tier accuracy and multi-source training

**Two-tier accuracy.** `/physics` supports two fidelities per observable:

- **Cheap-compute path** — approximate training labels at scale (~20% accuracy
  acceptable), to reduce the PINO's search space in early epochs.
- **Faithful-residual path** — physically faithful loss; when the PINO predicts
  a wrong state, the residual must reflect the wrongness accurately.

These are independently designed code paths. Their accuracies need not match;
the cheap path's bias against the faithful path is measured on a held-out battery
during the Calibrate phase and corrected by a single optional affine
bias-correction applied at the Polish phase.

**Multi-source training.** The PINO trains on four sources simultaneously: (a)
cheap-generated labels, (b) external VASP ground truth, (c) experimental
measurements, (d) faithful physics residuals. Methodology (detailed in
`informed-operator/design/residual-loss-methodology.md`): four-phase curriculum
(warmup 0–10%, refine 10–60%, calibrate 60–90%, polish 90–100%); GradNorm outer
balancing across source families + NTK-initialized fixed inner weights; Huber
loss with per-observable σ on experimental data; residual-adaptive sampling for
T1 residuals; coverage masks driven by applicability classifiers.

Bare-Kohn–Sham and G₀W₀ residuals disagree by ~30% on diamond and **cannot be
averaged**; the residual-generator's `dressing-tag` exposes which is which so the
loop per-tags the loss.

**Three pino-bridge exports** (the only surfaces `/informed-operator` sees):

- **Generate** — `/physics → /informed-operator` cheap-compute training labels
  (not differentiated through).
- **Validate** — `/informed-operator → /physics` predictions → faithful-residual
  loss + gradients + cert evidence (differentiated through).
- **Import** — external VASP + experimental data → `/physics` as cert evidence
  and labeled targets with `(value, σ, provenance, coverage-mask)` (not
  differentiated through).

Detailed export signatures in `implementation-plan.md §20`.

---

## 16. Out of scope (explicit)

Stated and held, so the architecture is honest about what it does not cover:

- Strongly-correlated systems (frustrated Wigner crystals, spin liquids, Mott
  physics) — `γ̂` is mean-field by construction; UWBG materials are large-gap and
  far from Mott physics.
- Flexoelectricity in centrosymmetric materials — below the numerical-noise
  floor; order-of-magnitude only.
- Magneto-thermal coupling in heavy contact metals — formally in `S`, not
  modeled.
- Deep-defect non-Markovian dynamics — Markov master-equation closure assumed.
- Polaron localization beyond Fröhlich.
- 4-phonon scattering, full NEGF tunneling, full SCPH/SSCHA — replaced by D4
  surrogates or Layer-1.75 V2 scaffolding.
- Plasma-process surface damage; grain-boundary statistics; continuum creep /
  dislocation climb; quantum-tunneling-corrected reaction rates (classical
  Eyring TST adequate at T_op ≥ 600 K).
- True renormalization-group flow; inverse design / minimal-model search (would
  live in `/informed-operator` as a PINO head, not a `/physics` primitive);
  fragile topology.

`predict` raises `out-of-scope` with a witness for any of these; cert
obligation-3 flags suspect cases.

---

## 17. Open decisions

The architecture above is committed. These remain to be decided.

1. **Implementation language — the single blocking decision.** No language is
   chosen. The hot numeric path, the autodiff requirement for D2 residuals, the
   compile-time staging of `γ̂` code, and the topology-tool ecosystem all bear on
   the choice. (A language with first-class autodiff and a strong ML/GPU
   ecosystem is the natural default given the D2-adjoint and NTK/GradNorm needs.)
   This blocks the first implementation phase.
2. ReferenceCache backend (default candidate: SQLite with SHA-pinned schema).
3. Surrogate-net build vs adopt, for the D4 surrogate formulas.
4. PDE-mesh format + adjoint library, for `KineticEvolutionOf` instances needing
   an explicit mesh.
5. Coverage-mask format (sparse from the start, or dense + compression).
6. Curriculum schedule confirmation (defaults 0.10 / 0.60 / 0.90).
7. Active-learning loop placement (default: `/interface`, not `/physics`).
8. The `γ̂` open questions of §9.4 (planner interface, ε-equality, materialization
   and refresh policy, rank-dependent encoding handling).
9. Layer-1.75 minimum spec sufficient for a V2 contributor to implement
   self-consistent GW / DMFT.
10. Whether any observable's applicability classifier is not first-order
    decidable (checked observable-by-observable during registry build-out).
11. The integrator interface — the exact signature `dynamics` exposes to
    `/informed-operator` for handing off the assembled GENERIC right-hand side.
12. The coupling grammar — how cross-regime terms in `E_coupling` and in `L`/`M`
    (§5) are declared and composed.

---

The detailed registries, typed observable compositions, and the phased build
sequence are in `implementation-plan.md`. The mathematical grounding for every
regime is in `physics/research/`. The closed formula list is
`physics/library/formulas/registry-manifest.csv`, indexed by
`formula-registry.md`.
