<!-- GENERATED FILE — do not edit. Source files under docs/{architecture,implementation,mvp}/. Regenerate with `python docs/meta/assemble.py`. -->

# n-Op Implementation Plan

## Contents

- [Architectural principles](#impl-01-principles)
- [The 12 computational methods](#impl-02-methods)
- [The 20 abstract-property templates](#impl-03-templates)
- [The named-formula registry](#impl-04-formulas)
- [The 11 observable bundles](#impl-05-bundles)
- [Target observables as typed compositions](#impl-06-compositions)
- [Residual machinery](#impl-07-residual-factory)
- [Cert obligations — detail and axis mapping](#impl-08-cert-detail)
- [Cross-cutting design rules](#impl-09-cross-cutting)
- [Build sequence](#impl-10-build-sequence)
- [Verification](#impl-11-verification)


<a id="impl-01-principles"></a>

# Architectural principles

Carried throughout the build:

1. **Strict layered architecture, single typed seal.** Imports flow one way:
   `core ← shared ← state/canonicals/generic/methods ← observables ← cert ← api`.
   One typed module wraps everything; internal datatypes are opaque across the
   seal.
2. **Minimum primitives.** The 12-method computational vocabulary is the closed
   primitive set; everything else is composition.
3. **No symbolic computation on the runtime path.** Structured data appears only
   as expand-time/compose-time input or as inert certificate output.
4. **Typed everything.** Every method, template, and formula has an explicit
   typed signature; no string-encoded formulas; no implicit parameters.
5. **Composition over duplication.** Properties are typed compositions of the
   small method vocabulary; observables that share a shape share a template.
6. **Loud failure with numeric witnesses.** Every degeneracy raises at the typed
   boundary carrying the offending number (residual norm, condition number,
   offending order).
7. **Cert is first-class.** Schema + freeze fixture + tamper tripwire +
   high-precision oracle; roughly the weight of any one level.
8. **Substrate-agnostic.** `/physics` emits state + dynamics + residuals +
   readouts; the integrator, trainer, and PINO live downstream.

---


<a id="impl-02-methods"></a>

# The 12 computational methods

The closed primitive set. Each carries a typed signature and a sub-method
dispatch.

```
state-readout            StateReadout(x: State, extractor: Extractor) → Value
                         sub: pairwise-distance-PBC, atomic-sphere-integral,
                              position-diagonal-trace, cell-metric-extraction,
                              spectral-extremum, occupation-sum

algebraic-combination    AlgebraicCombination(inputs: {Value},
                                               formula: NamedFormula) → Value
                         (ALWAYS invokes a named registry formula — no inline math)

functional-differentiation
                         FunctionalDifferentiation(F: Functional, wrt: Coordinate,
                                                   at: StatePoint, order: ℕ = 1) → Tensor
                         sub: gradient (order 1), hessian (order 2), higher-order

variational-minimization VariationalMinimization(F: Functional, target: Coordinate,
                                                  fixed: Coordinate, method: Optimizer,
                                                  tol: Real) → StatePoint
                         sub: steepest-descent, conjugate-gradient, BFGS, FIRE,
                              Newton, SCF-mixing, Pulay-mixing

spectral-decomposition   SpectralDecomposition(Op: Operator, basis: Basis,
                                                k: Int = full, method: EigenSolver)
                                                → (Spectrum, Eigenvectors)
                         sub: full-diagonalization, Lanczos, Davidson,
                              inverse-iteration, shift-invert

spectral-aggregation     SpectralAggregation(spectrum: Spectrum, aggregator: Aggregator,
                                              weights: Field) → Field
                         sub: delta-sum (DOS), partition-Z (log-sum-exp),
                              thermal-average (Bose / Fermi / Maxwell-Boltzmann)

linear-response          LinearResponse(observable: Operator, perturbation: Operator,
                                         kernel: ResponseKernel, frequency: Real = 0)
                                         → Response
                         sub: Kubo, Linear-Response-DFT (Dyson), Greens-function,
                              Sternheimer, interface-tunneling †

path-search              PathSearch(F: Functional, initial: StatePoint, final: StatePoint,
                                     method: PathMethod, n_images: Int = 9, tol: Real)
                                     → MinimumEnergyPath
                         sub: NEB, climbing-image-NEB, dimer, string-method,
                              field-line-integral †

convex-optimization      ConvexOptimization(points: {StatePoint}, objective: ConvexObjective,
                                             method: ConvexSolver) → Solution
                         sub: convex-hull (lower envelope), common-tangent,
                              quadratic-program

kinetic-evolution        KineticEvolution(distribution: Distribution, collisions: CollisionKernel,
                                           gradient: AppliedGradient, method: KineticMethod,
                                           truncation: Int) → SteadyState
                         sub: BTE-RTA, BTE-full, master-equation, drift-diffusion,
                              mesh-interpolation†,
                              Cahn-Hilliard, Allen-Cahn

statistical-sampling     StatisticalSampling(distribution: Distribution, method: Sampler,
                                              n_samples: Int) → SampleSet
                         sub: Monte-Carlo, molecular-dynamics, kMC, importance-sampling

symmetry-projection      SymmetryProjection(target: Tensor, group: SymmetryGroup,
                                             projection_kind: ProjKind) → Tensor
                         sub: point-group-projection, space-group-projection,
                              time-reversal-symmetrize
```

† `interface-tunneling`, `field-line-integral`, and `mesh-interpolation` (the
compile-time band / e-ph interpolator under `kinetic-evolution`, `arch-09 §9.1`)
are the three registered sub-methods added for the UWBG scope. Sub-methods extend a method's dispatch
table without changing its typed signature; each requires a sub-method test and
a regression-freeze entry.

---


<a id="impl-03-templates"></a>

# The 20 abstract-property templates

Templates are parameterized method chains; concrete observables are
instantiations. See `arch-09-vocabularies §9.2` for the grouping and the
"produces" summary; signatures follow.

```
StateReadoutOf(x: State, extractor: Extractor) → Value

AlgebraicOf(inputs: {Value}, formula: NamedFormula) → Value

SecondDerivativeOf(F: Functional, x₀: StatePoint, coord: Coordinate,
                   metric: TensorNorm) → Tensor

SpectrumOf(Op: ParametricOperator, domain: ParametricDomain) → FieldOnGrid

SpectralAggregateOf(spectrum-from: Source, aggregator: Aggregator,
                    weights: Field) → FieldOnGrid

ResponseOfTo(observable: Operator, perturbation: Operator,
             kernel: ResponseKernel, frequency: Real) → Response

PathStationaryOf(F: Functional, initial: StatePoint, final: StatePoint,
                 method: PathMethod) → ReactionCoord

KineticEvolutionOf(distribution: Distribution, collisions: CollisionKernel,
                   gradient: AppliedGradient) → SteadyState

ClassifyOf(object: StateComponent, classifier: Classifier) → DiscreteLabel

ComparisonOf(target: StateComponent, reference: StateComponent,
             metric: ComparisonMetric) → Difference

RadiativeEmissionOf(excited_state: State, optical_coupling: Operator) → Field

MicrokineticSteadyStateOf(network: RateNetwork, initial: Coverage,
                          driving: Environment) → Coverage

SelfConsistentRenormalizationOf(bare: BareSubstrate,
                                method: {SCP-perturbative, SSCHA-stochastic, TDEP,
                                         GW-one-shot, GW-self-consistent,
                                         BSE-iterated, polaron-self-consistent},
                                T: Temperature,
                                convergence: ConvergenceCriterion) → DressedQuantity
        (fixed-point structure shared across SCPH/SSCHA, GW self-energy, BSE
         iteration, polaron; emits IterativeResult cert evidence — impl-07 §7.7)

ConfigurationalFreeEnergyOf(parameterization: {ClusterExpansion(ECI),
                                               RedlichKister(L_ν, order),
                                               BraggWilliams},
                            composition: x, T: Temperature) → G_config
        (cluster-expansion is discrete T=0 lattice energy; Redlich–Kister is
         continuous composition-dependent finite-T excess Gibbs — DISTINCT
         parameterizations of one template, not instances of each other)

SymmetryAdaptedHamiltonianOf(space-group: SpaceGroup,      -- 1..230 (+ magnetic)
                             wyckoff-orbits: {WyckoffOrbit},
                             orbital-basis: {Orbital},
                             neighbor-shells: Int) → ParameterizedBlochHamiltonian
        (constructive Stage-1 of the synthesis pipeline: emits the most general
         symmetry-allowed H(k) as a parametric family indexed by the free
         couplings symmetry allows; the substrate X_BS classification reads)

InterfaceEquilibriumOf(left: Crystal, right: Crystal, coupling: InterfaceCoupling,
                       env: Environment, method: BiSlabSolver) → BicrystalState
        (charge transfer + band alignment; consumed by Schottky-barrier,
         band-offset, interface-dipole observables)

SelfConsistentChargeBalanceOf(host: Crystal, defect-set: {DefectSpecies},
                              env: Environment, method: ChargeNeutralitySolver,
                              tol: Real) → (E_F: Scalar, {N_q}: Vector, {n,p}: Scalar²)
        (closes the L3 ↔ non-equilibrium dependency cycle via a same-pass fixed point)

HarmonicStiffnessHessianOf(F: Functional, x₀: StatePoint,
                           displacement-basis: Basis, method: HessianMethod)
                           → Tensor[3N × 3N]
        (specialization of SecondDerivativeOf for dynamical matrices;
         symmetrization, acoustic-sum-rule enforcement, and Born-effective-charge
         correction are template-level concerns)

BiSlabGrandPotentialOf(slab-left: Crystal, slab-right: Crystal,
                       gap: Length, env: Environment) → Scalar
        (adhesion energy, interface formation energy, debonding force)

MassActionEquilibriumOf(species: {Species}, reactions: {Reaction},
                        env: Environment, method: NonlinearSolver) → CompositionVector
        (equilibrium readout — point-defect / gas-exchange / adsorbate equilibria;
         distinct from MicrokineticSteadyStateOf, which is a driven steady state)
```

**Overlap resolution (recorded once):** `ClusterExpansion` is a *parameterization
of* `ConfigurationalFreeEnergyOf`, not a separate template. Bulk-boundary
correspondence is a cert obligation (§8 obligation-7), not a template.
`HarmonicStiffnessHessianOf` specializes `SecondDerivativeOf` rather than
duplicating it.

---


<a id="impl-04-formulas"></a>

# The named-formula registry

The canonical, machine-readable list is
`physics/library/formulas/registry-manifest.csv` — 132 substantive rows plus 2
markers for relations enforced architecturally and therefore not residualized
(force = −∇energy; equivariance). `formula-registry.md` is the narrative index.
Every algebraic combination invokes a named formula with typed inputs and an
explicit output type; no inline math.

Each formula record carries:

```
record FormulaRecord {
  name               : Symbol                  -- behavior-named (e.g. defect-formation-energy)
  signature          : (Inputs) → Output       -- typed, with units
  bundle             : {BundleId}              -- one or more of B1..B11, or the
                                               --   L1 primitive tag (linear-response
                                               --   primitives Z*/ε∞/χ∞/α_M, rows 91–94,
                                               --   feed multiple bundles)
  cost-tier          : T0 | T1 | T2 | T3
  diff-tag           : D0 | D1 | D2 | D3 | D4
  source             : provenance pointer (research file / literature DOI)
  depends-on         : {Symbol}                -- upstream formulas / primitives
  applicability      : (Crystal, Environment) → Bool
  adjoint-validated  : Passed | Failed(witness) | NotApplicable | Relaxed(rationale)
}
```

**Cost tiers:** T0 closed-form (≤10 µs) · T1 small linear algebra / 1D quadrature
(≤10 ms) · T2 Brillouin-zone / mesh integral (≤10 s) · T3 self-consistent loop or
PDE solve (≤10 min).

**Differentiability tags:** D0 no autodiff needed — a pure read, **or an integer /
categorical output with no useful derivative** (topology invariants, discrete CSP
metrics: "exception-set everywhere") · D1 analytic forward derivative · D2 adjoint
required (validated at registration) · D3 implicit-function adjoint via fixed-point
linearization, **or a finite-difference surrogate where there is no fixed point**
(stated in the formula's docs) · D4 autodiff relaxed via a differentiable surrogate
— surrogate-net bridge, **log-sum-exp soft-hull, or Gumbel-Softmax relaxation** —
approved at registration with an obligation-9 validity domain.

The corrected physics is canonical in the registry and in §6 below: optical
absorption uses `(2ω/c)·Im(√ε)`; the operator-spectrum-area sum rule carries the
`2/π` prefactor; the acoustic sum rule sums over all lattice translations
(`Σ_J Σ_R Φ_{IαJβ}(R) = 0`); the magnetic relaxation term is the
orientation-preserving form `S × (S × H_eff)`; the harmonic transition-rate
normalization consumes products-over-modes (scalars), not spectra.

**Applicability-decidability invariant.** Every `applicability` predicate is
first-order decidable in `(Crystal, Environment)` — finite case analysis on
typeclass tags (lattice type, site decoration, environment-field presence),
not on numeric thresholds or solver outputs. Non-decidable classifiers are
forbidden at registration; see the registry-build gate
(`impl-10-build-sequence` Phase 7).

---


<a id="impl-05-bundles"></a>

# The 11 observable bundles

The eleven physics-domain bundles `B1..B11` are listed in
`arch-09-vocabularies §9.4`. Representative contents:

- **B1 electronic-structure** — BandStructure, DOS, BandGap, ChargeDensity,
  effective-mass tensor, k-resolved DOS.
- **B2 phonon** — PhononDispersion, PhononDOS, group velocity, Grüneisen,
  self-consistent phonons.
- **B3 transport** — conductivity (BTE & Kubo), mobility (Matthiessen,
  Caughey–Thomas), Seebeck, Wiedemann–Franz κ_e, Hall mobility.
- **B4 defect-resolved** — DefectFormationEnergy, charge-transition levels,
  populations, SRH / Auger recombination, multiphonon capture, Huang–Rhys.
- **B5 surface-resolved** — SurfaceEnergy, surface grand potential, Wulff shape,
  termination stability window.
- **B6 interface-resolved** — Schottky barrier (Schottky–Mott + MIGS), band
  offset, interface dipole, adhesion, contact resistance, field emission;
  the polarization / 2DEG package (rows 113–119) and the gate-dielectric
  layer models (Poole–Frenkel row 129; pyroelectric n_s(T) row 128).
- **B7 mechanics** — elastic constants C_ij, bulk modulus, sound velocity,
  hardness, deformation potentials, piezoresistance.
- **B8 thermodynamics** — Gibbs free energy, phase-diagram convex hull,
  chemical-potential references, Clausius–Clapeyron.
- **B9 non-equilibrium-operating** — self-heating T_op, coupled EM–thermal PDE,
  hot-carrier temperature balance, impact ionization, avalanche, tunneling
  currents (Fowler–Nordheim, Richardson–Dushman, Padovani–Stratton), NEGF
  transmission.
- **B10 static-validity** — bond-valence sum, Pauling radius ratio, Born
  stability, generalized stacking-fault energy, structure uniqueness; the
  XRD structure-factor channel (row 132).
- **B11 degradation** — carbide growth, electromigration MTTF, Coffin–Manson
  fatigue; the slow-tier kinetics (rows 105–112: vacancy generation,
  H redistribution / desorption, platelet nucleation, vibration-driven
  dislocation multiplication, air oxidation, radiation displacement); the
  gate-dielectric lifetime pair (TDDB row 130, JMAK crystallization row 131).

(A file tree may additionally group observable *modules* by output data-shape;
the residual-driving grouping is the eleven physics-domain bundles.)

---


<a id="impl-06-compositions"></a>

# Target observables as typed compositions

Every property in `properties.md` written as a typed composition — the
validation that the closed vocabulary covers the target scope. Each invokes only
methods (§2), templates (§3), and named formulas (§4).

### Structural

```
LatticeParameters = StateReadoutOf(state.h, extractor = cell-metric-extraction)
BondLengths       = StateReadoutOf((state.R, state.h), extractor = pairwise-distance-PBC)
CrystalStructure  = ClassifyOf((state.R, state.h), classifier = space-group-detection)
Defects(energy)   = AlgebraicOf({E_defect = E_BO(crystal-with-defect),
                                 E_perfect = E_BO(reference),
                                 Δn, μ = env.chem-pots, q, E_F = env.Fermi-level},
                                formula = defect-formation-energy)
Defects(char.)    = ComparisonOf(state, reference-perfect, metric = atom-matching)
Surfaces(region)  = StateReadoutOf(state, extractor = extract-surface-region)
Surfaces(energy)  = AlgebraicOf({E_slab, E_bulk, n, A}, formula = slab-arithmetic)
```

### Electronic

```
BandStructure = SpectrumOf(Ĥ_KS[γ̂], domain = BZMesh(nx, ny, nz))
DOS           = SpectralAggregateOf(BandStructure, aggregator = delta-energy-bin,
                                    weights = uniform)
BandGap       = AlgebraicOf({BandStructure}, formula = conduction-min-minus-valence-max)
ChargeDensity = StateReadoutOf(γ̂, extractor = position-diagonal-trace)
```

### Optical

```
DielectricFunction = ResponseOfTo(observable = γ̂, perturbation = A-ext,
                                  kernel = current-current-correlator, frequency = ω-mesh)
Absorption(ω)      = AlgebraicOf({DielectricFunction}, formula = (2ω/c)·Im(√ε))
RefractiveIndex(ω) = AlgebraicOf({DielectricFunction}, formula = Re(√ε))
Photoluminescence  = RadiativeEmissionOf(excited_state = γ̂-pumped, optical_coupling = dipole-d)
```

### Mechanical

```
ElasticConstants = SecondDerivativeOf(F = E_BO, x₀ = equilibrium-state,
                                      coord = symmetric-strain-η,
                                      metric = Frobenius²-volume-normalized)
BulkModulus      = AlgebraicOf({ElasticConstants}, formula = voigt-reuss-hill.K)
StressStrain(lin)= AlgebraicOf({ElasticConstants, applied-ε},
                               formula = linear-elasticity-stress-strain)
Hardness(model)  = AlgebraicOf({K, G, …}, formula = {chen | teter | tian | mazhnik-oganov}-hardness)
```

### Thermal

```
PhononDispersion    = SpectrumOf(operator = HarmonicStiffnessHessianOf(E_BO, R₀, u),
                                 domain = BZMesh)
HeatCapacity(T)     = SpectralAggregateOf(PhononDispersion, aggregator = bose-einstein-cv(T),
                                          weights = uniform)
ThermalConductivity = KineticEvolutionOf(distribution = phonon-distribution(n_qν),
                                         collisions = three-phonon-anharmonic-Ψ,
                                         gradient = ∇T, method = BTE-RTA)
ThermalExpansion    = AlgebraicOf({ModeGrüneisen(T), HeatCapacity(T)}, formula = QHA-expansion)
```

### Magnetic

```
MagneticMoments      = StateReadoutOf(γ̂, extractor = atomic-sphere-spin-integral)
SpinDensity          = StateReadoutOf(γ̂, extractor = position-diagonal-spin-trace)
ExchangeInteractions = ResponseOfTo(observable = γ̂, perturbation = infinitesimal-spin-rotation,
                                    kernel = exchange-coupling-formula, frequency = 0)
```

### Transport

```
ConductivityViaBTE  = KineticEvolutionOf(distribution = carrier-f_n,
                                         collisions = e-phonon-scattering-g²,
                                         gradient = applied-E-field, method = BTE-RTA,
                                         truncation = first-order)
ConductivityViaKubo = ResponseOfTo(observable = current-operator-ĵ, perturbation = A,
                                   kernel = current-current-correlator, frequency = ω→0⁺)
Conductivity        = { ConductivityViaBTE, ConductivityViaKubo }
                      (both formulas evaluated; method-equivalence is enforced
                       by cert obligation-6 as an Algebraic/MethodEquivalence
                       residual — arch-11-residuals, arch-12-cert)
CarrierMobility     = AlgebraicOf({Conductivity, carrier-density}, formula = σ/(n·e))
IonicDiffusion      = let ν_min   = SpectrumOf(HarmonicStiffnessHessianOf(E_BO, init), normal-modes)
                          ν_saddle = SpectrumOf(HarmonicStiffnessHessianOf(E_BO, saddle),
                                                normal-modes-minus-unstable)
                          ν₀ = AlgebraicOf({StateReadoutOf(ν_min,    product-of-modes),
                                            StateReadoutOf(ν_saddle, product-of-modes)},
                                           formula = harmonic-transition-rate-normalization)
                          D₀ = AlgebraicOf({a, Z, ν₀}, formula = jump-diffusivity)
                          E_a = StateReadoutOf(PathStationaryOf(E_BO, init, fin),
                                               extractor = saddle-vs-min-difference)
                      in AlgebraicOf({D₀, E_a, T}, formula = arrhenius)
MigrationBarrier    = PathStationaryOf(F = E_BO, initial = site-i, final = site-j,
                                       method = climbing-image-NEB, n_images = 9, tol = 1e-3)
```

(The harmonic transition-rate normalization consumes the **product** of
normal-mode frequencies via the `product-of-modes` extractor, not the spectra.)

### Thermodynamic

```
TotalEnergy     = StateReadoutOf(E[x], extractor = identity)
FormationEnergy = AlgebraicOf({E_compound = E_BO(target),
                               E_refs = {E_BO(ref)}, n_i, μ_i = env.chem-pots},
                              formula = formation-energy-from-references)
PhaseStability  = ConvexOptimization(points = {(x_φ, F_φ)}, objective = lower-convex-envelope)
FreeEnergy(T)   = AlgebraicOf({E_BO,
                               F_vib = SpectralAggregateOf(PhononDispersion, bose-einstein-helmholtz(T)),
                               F_el  = SpectralAggregateOf(BandStructure, fermi-dirac-helmholtz(T))},
                              formula = F = E_BO + F_vib + F_el)
```

### Chemical / surface

```
AdsorptionEnergy = AlgebraicOf({E_BO(slab+ads), E_BO(slab), E_BO(molecule)},
                               formula = adsorption-energy-difference)
ReactionPathway  = PathStationaryOf(F = E_BO, initial = reactant, final = product,
                                    method = climbing-image-NEB)
CatalyticActivity= let RateNetwork = {(step, AlgebraicOf({ν₀ = harmonic-rate-prefactor,
                                                          E_a = PathStationaryOf(…).saddle,
                                                          T}, formula = htst-rate))}
                       θ = MicrokineticSteadyStateOf(network = RateNetwork,
                                                     initial = vacuum-coverage,
                                                     driving = env.chem-pots)
                   in AlgebraicOf({θ, RateNetwork, RC-step}, formula = turnover-frequency)
SurfaceEnergy    = AlgebraicOf({E_BO(slab), E_BO(bulk-per-formula-unit), n, A},
                               formula = slab-arithmetic)
```

All target observables resolve to typed compositions over the closed vocabulary.

---


<a id="impl-07-residual-factory"></a>


# Residual machinery

The PINO-facing factory that turns named formulas (`impl-04-formulas`)
into `ResidualLeaf` nodes (`arch-06-physics-graph §6.3`) in the
`PhysicsGraph`. Under the always-cheap reframe (`arch-07-pipeline`),
this is now part of Stage 1 (graph construction). The factory has
three responsibilities: generate the leaves with content-addressed keys,
gate registration on adjoint correctness, and provide the per-formula
metadata the runtime kernel uses for its outputs.

## 7.1 The `ResidualGenerator` record

```
record ResidualGenerator {
  name                 : Symbol
  observable           : ObservableRef
  bundle               : BundleId                 -- B1..B11 or the L1 primitive tag
                                                  --   (impl-04-formulas; facet, not identity)
  category             : CategoryTag              -- 19 named tags (arch-11-residuals §11.1)
  layer                : 1..7                     -- compose-time DAG layer (the 7-layer
                                                  --   compute DAG of residual-generator-catalog §2)
  cost-tier            : T0 | T1 | T2 | T3
  diff-tag             : D0 | D1 | D2 | D3 | D4
  dressing-tag         : bare | dressed(scheme: G0W0|SCP-perturbative|LO-TO-NA-correction
                                                |Born-charge|epsilon-infinity
                                                |electronic-susceptibility)   -- = the §7.7 OneShotCert schemes
                         -- provenance label only; not a loss-weighting axis
  characteristic-scale : σ                        -- declared accuracy scale of the observable
                                                  --   (a Quantity in its units), seeded from the
                                                  --   accuracy ledger (arch-11-residuals §11.7,
                                                  --   docs/accuracy-ledger.md); the error-model
                                                  --   input to Quantity.combineTol — never a
                                                  --   fitted weight
  axes                 : List<AxisLabel>          -- the dimensions this generator unfolds over
                                                     (k-point, frequency, atomic pair, shell, …)
  applicability        : (Crystal, Environment) → Bool
  input-contract       : {TypedSlot}
  output-contract      : TypedSlot
  forward              : Inputs → Output
  loss-projection      : Output → Map<ResidualKey, Scalar>
                         -- emits one entry per axis tuple; key is content-addressed (arch-11-residuals)
  weight-policy        : ConsumedBy(/informed-operator)
                         -- /physics declares the granularity; aggregation lives downstream
  sampling-policy      : UniformBatch | RAD(τ) | Importance | ValidationOnly
  dependencies         : {Symbol}                 -- same-pass fixed-point co-convergence
  adjoint-cert         : Passed | Failed(witness) | NotApplicable | Relaxed(rationale)
  registration-hash    : ContentAddress           -- cert-tripwire detection
}
```

## 7.2 Granularity (canonical reference: `arch-11-residuals`)

Each generator unfolds along its `axes` to emit *N* residual
contributions, one per axis tuple. Each contribution is a
`ResidualLeaf` node with a content-addressed `ResidualKey`:

```
ResidualKey = (producer : Producer, axes : Tuple<AxisLabel>)
Producer    = Formula(NamedFormula) | Method(NamedMethod)
```

The PINO holds `Map<ResidualKey, Weight>`; `/physics` emits
`Map<ResidualKey, Scalar>`. Category, bundle, and dressing-tag are
queryable facets via a parallel `Map<ResidualKey, ContributionFacets>`.
The `dressing` facet is a provenance label for cert and audit; bare and
dressed residuals on the same observable live as distinct
`FormulaApply`/`MethodInvoke` chains in the graph (`arch-09-vocabularies`),
not as weighted siblings.

## 7.3 Factory entry point

```
make-residual-generator(observable     : ObservableRef,
                        formula        : NamedFormula,
                        axes           : List<AxisLabel>,
                        sampling-policy: SamplingPolicy,
                        applicability  : (Crystal, Environment) → Bool)
                      → ResidualGenerator
```

Called once per formula at load time. The returned generator is
inserted into Stage 1 of the pipeline when its `applicability`
predicate holds for the current composition.

## 7.4 Generator subtypes

Three generator subtypes:

- **Standard residual** — derived from a named formula; participates in
  loss; D2 entries gated on adjoint existence.
- **Ground-truth-bridge** — anchors a generator to an `Import`-supplied
  target value with `(value, σ, provenance, coverage-mask)`
  (`arch-16-pino-bridge §16.2`); loss is the σ-scaled Huber against the
  target.
- **Cert-only** — no loss contribution; runs as part of cert evidence
  (`arch-12-cert`), not as part of training loss.

## 7.5 Registration-time adjoint gate (hard)

D2 entries run a vJp-vs-JvP check on `N ≈ 64` sampled points at
registration time; if the max relative error exceeds `τ_adj` (default
`1e-4`) the build fails loud. Forces an honest gradient or an explicit
downgrade to D3 / D4 with recorded rationale.

Under the always-cheap reframe, most D2 generators with a fixed-point
solve in their forward pass are wired to the **implicit-diff adjoint**
synthesized at Stage 4 (`arch-07-pipeline §7.4`); the gate verifies
that synthesized adjoint, not a hand-written backward.

## 7.6 Training-loop consumption

Executed by `/informed-operator`: enumerate the active residuals for
the current curriculum phase (Warmup → Refine → Polish), sample each
per its policy, evaluate forward + projection, and run same-pass
fixed-point iteration at the DAG layer barrier for the
L3↔non-equilibrium cycle. Aggregation across `ResidualKey`s lives
entirely in `/informed-operator`, not in this factory.

## 7.7 Dressing certificates

The `OneShotCert` and `IterativeResult` records (Layer 1.25 and Layer
1.75 per `arch-08-bo-levels`) survive as **schemas attached to dressed
`MethodInvoke` nodes**, no longer as a separate per-generator field:

```
record OneShotCert {
  scheme            : G0W0 | SCP-perturbative | LO-TO-NA-correction
                    | Born-charge | epsilon-infinity | electronic-susceptibility
  inputs-hash       : ContentAddress
  parameters        : Map<Symbol, Value>          -- k-mesh, cutoff, …
  output            : DressedQuantity
  closure-residual  : Map<ResidualKey, Scalar>    -- one entry per (axis tuple)
                                                  --   the cert verifies; granular
                                                  --   like every other residual
                                                  --   emission (arch-11-residuals)
  cost-tier         : T1 | T2
}

record IterationSnapshot {                        -- one element of trajectory
  iter              : Nat
  residual          : Map<ResidualKey, Scalar>    -- per-key closure residual
  energy            : Scalar                      -- functional value at this iter
  witness           : Optional<Witness>           -- non-null iff divergent
  params            : Map<Symbol, Value>          -- mixing factor, broadening, …
}

record IterativeResult {                          -- Layer 1.75 (V2-deferred)
  scheme            : scGW | SSCHA-stochastic | TDEP | BSE-iterated
                    | DMFT | polaron-self-consistent
  inputs-hash       : ContentAddress
  parameters        : Map<Symbol, Value>          -- mixing, broadening, max-iter
  trajectory        : List<IterationSnapshot>
  converged?        : Bool
  divergence-witness: Optional<Witness>           -- non-null iff not converged
  final             : DressedQuantity
  cost-tier         : T3
}
```

V1 ships Layer 1.25 wired and Layer 1.75 as type/cert scaffolding only,
with `not-implemented-in-V1` stubs that fail loud.

## 7.8 Cadence policy (cost-tier → training cadence)

`sampling-policy` (§7.1) chooses *which* samples; the **cadence policy** chooses
*how often* each generator is evaluated, binding the cost tier to the training loop
so the expensive tiers never run per sample:

| Tier | Cost | Cadence |
|---|---|---|
| T0 | ≤10 µs closed-form | **every SGD step** (per-sample, backprop-native) |
| T1 | ≤10 ms small-LA / 1-D quadrature | **RAD-subsampled** (per-batch stochastic importance) |
| T2 | ≤10 s BZ / mesh integral | **per-epoch cached** (offline reference cache per composition + `(T,P,q)` query) — e.g. `NEGF-transmission` (row 80: one linear solve per energy) |
| T3 | ≤10 min iterative / PDE | **on-demand / calibration-only**, with a cheap T0/T1 proxy during training — e.g. `reference-phase-energy-cache` (row 87) |

Only the T0/T1 core runs on the per-sample hot path (the µs–ms class of
`arch-07-pipeline §7.6`); T2 is on-request per-epoch; T3 is reference / calibration
side. This is the policy that makes the always-cheap claim honest about *runtime
cadence*, not just per-op cost.


<a id="impl-08-cert-detail"></a>

# Cert obligations — detail and axis mapping

The ten obligations are listed in `arch-12-cert`. Each maps onto a
Layer-0 axis, so its checker is a generic function over a typeclass:

| Obligation | Axis / mechanism |
|---|---|
| 1 symmetry equivariance | `Sampleable` × group action: a symmetry op on the domain equals the orbit-induced action on the codomain (under `approxEq`) |
| 2 physical bounds | `Quantity` ordering: value checked against each declared bound |
| 3 analytic limits | `HasAnalyticStructure`: evaluate the limit, check the witness predicate |
| 4 reference battery | content-side: read `cert/reference-data/*.csv`, compare under `approxEq` |
| 5 conservation | `Integrable`: `integrate(measure) = declared-invariant` to tolerance |
| 6 GENERIC degeneracy + named-formula consistency | `Sampleable` + `approxEq`: two formulas claiming one quantity agree on the shared domain (Algebraic/MethodEquivalence), plus the cert-only Degeneracy tripwire `‖L δS/δx‖² + ‖M δE/δx‖²` ≈ 0 per tier (generator-construction bug detector, `arch-05-generic` category, `arch-11-residuals`) |
| 7 boundary correspondence | `DiscreteStructure` morphism: observed boundary-band count matches `(X_BS_generator, orientation) → multiplicity` |
| 8 reference-battery-versioned | versioning discipline on obligation 4; per-entry provenance; trips at >3σ |
| 9 surrogate-net validity | for D4: declared input domain contains the query, surrogate uncertainty below tolerance, refresh up to date |
| 10 adjoint-existence at registration | the `impl-07-residual-factory §7.5` gate; enforced at registration, not prediction |

The certificate is an inert s-expression carrying scalar verdicts plus numeric
witnesses for failures; its schema is the cross-workstream contract, with a
freeze fixture, a tamper tripwire, and a high-precision oracle cross-check
(non-load-bearing).

---


<a id="impl-09-cross-cutting"></a>

# Cross-cutting design rules

These rules cut across formulas, methods, residuals, cert, and the
pino-bridge surface. They are not architectural decisions — those live in
`arch-*`. They are reusable patterns that show up in more than one place
in the implementation.

## 9.1 Method equivalence as a residual, not a path-selector

Several observables admit multiple formulas that should agree on their
shared domain (conductivity via BTE-RTA vs Kubo; thermal conductivity via
QHA+Callaway vs DFPT+3-phonon-BTE; effective mass from `k·p` vs DFT
band-curvature). The discipline under the always-cheap pipeline
(`arch-07-pipeline`) and the granularity rule (`arch-11-residuals`)
is:

- All applicable formulas for an observable are instantiated as
  `FormulaApply` nodes (`arch-06-physics-graph §6.2`); hash-consing
  collapses shared subgraphs.
- Equivalence is enforced via the `Algebraic/MethodEquivalence`
  residual category (`arch-11-residuals §11.1`), one `ResidualLeaf`
  per agreeing pair.
- Cert obligation 6 (`arch-12-cert`) consumes the
  `Algebraic/MethodEquivalence` leaf; if `|f₁ − f₂| > tolerance` it
  trips with both values as witnesses. The tolerance kind depends on the
  pair's sub-kind (`arch-11-residuals §11.1` cat-15): an **equivalence pair**
  (BTE-σ ≡ Kubo-σ, sharing an agreement theorem) trips on any disagreement,
  while a **consistency pair** (QHA+Callaway κ vs iterative-LBTE κ — *no* agreement
  theorem, only a bounded model gap) trips only on excess beyond the declared
  `τ_method`. Treating the Callaway-vs-BTE κ pair as an equivalence would wrongly
  score the legitimate model gap as a bug; it is a consistency pair.
- The `Observable` output role (`arch-06-physics-graph §6.3`)
  designates which compose-time-selected formula is the *exposed*
  value to downstream consumers; selection is by `ContributionFacets`
  precedence (declared dressing tier, then registration order). The
  unselected formulas still contribute their residual leaves.

The architecture never averages observables and never silently selects
between formulas at runtime; both are exposed in the graph and the
disagreement is a typed residual.

## 9.2 Same-type → shared interpretation; type-change → explicit stage

Elements that are *parallel interpretations of one signature* — the 19
`CategoryTag`s (`arch-11-residuals §11.1`), the dressing tiers within L1
(`arch-08-bo-levels §8.1`), the 10 cert obligations
(`arch-12-cert`), source/dressing tags on `ContributionFacets`,
applicability guards (`arch-13-applicability`) — share one interface
with multiple handlers.

Elements that *compose into a pipeline with a type change between
stages* — the γ̂ encoding pipeline (`arch-15-gamma-hat`), the 4 BO
levels (`arch-08-bo-levels`), the compose-time pipeline (stages 1–4 + the 2.5 sub-stage)
(`arch-07-pipeline`), the synthesis → property → PINO layering — stay
explicit multi-stage structures.

Rule of thumb: same type ⇒ one interface, many handlers; type changes
between stages ⇒ keep the stages.

## 9.3 Provenance tags are not weighting axes

`ContributionFacets` (`arch-11-residuals §11.2`) attaches `(category,
bundle, dressing)` to every `ResidualLeaf` as a sidecar — purely
queryable provenance, never part of `ResidualKey` identity and never
the basis for a per-residual loss weight. Loss weighting lives in
`/informed-operator`'s curriculum schedule (`arch-11-residuals §11.4.1`),
keyed by `CategoryTag` participation gates only. A facet field exists
to answer "which residuals belong to bundle B?", not "what is the
weight of residual r?".

## 9.4 Couplings are declared channels; terms are generated

Cross-regime physics is not a hand-rolled list. The library author
declares `CouplingChannel` records (`arch-19-coupling-structure`),
each specifying `{pieces, target, order, derivative, applicability}`.
The Stage-2.5 invariant synthesizer takes the crystal's symmetry
group and the active channels and *generates* the explicit
`InvariantTerm`s — symmetry-respecting tensors that become
`FormulaApply` nodes in the graph. Adding a new physical regime
(piezoelectricity, magnon-phonon coupling, …) is a channel
declaration, not a code edit. Channels register through the same
factory pattern as residual generators (`impl-07-residual-factory §7.3`):
content-addressed by parameter tuple, applicability validated as
first-order decidable.

---


<a id="impl-10-build-sequence"></a>

# Build sequence

Each phase produces a verifiable artifact. The implementation-language decision is
resolved (`arch-18-open-decisions`, Closed decisions;
`physics/research/implementation-language.md`): a **Haskell** compiler-host for
Stages 1–4 + the substrate, emitting a **Julia** Stage-5 runtime, with **GAP** and
**Lean 4** offline.

| Phase | Scope | Artifact |
|---|---|---|
| 0 | Repository scaffold: the directory tree, orientation docs, per-directory READMEs | Empty skeleton matching the architecture |
| 1 | **Tier-1 numeric substrate** (`core`): coefficient/derivative layout, autodiff engine, staged code generation, tensor algebra, mesh integration | `core` implemented + tested against analytic references |
| 2 | **Tier-2 physical primitives** (`shared`): pair-sum with PBC, electrostatics (Ewald), kinetic density, density-from-orbitals, Hellmann–Feynman forces, DFT stress | Physical-primitive library, tested at analytic limits |
| 3 | **Input concepts** (`inputs`): typed constructors + readers for PeriodicityStructure, SiteDecoration, Environment | Round-trip-preserving system descriptions |
| 4 | **Unified state** (`state`): the 7-tuple container; per-level components (L1–L4); enumerate/serialize/hash | State encoding complete |
| 5 | **Methods vocabulary** (`methods`): the 12 methods + sub-method dispatch | Computational vocabulary, tested per method |
| 6 | **Templates** (`abstract-properties`): the 20 templates as typed factories | Template machinery, tested with multiple argument tuples |
| 7 | **Formula registry** (`formulas`): the 132 formulas with typed signatures + citations; the manifest; **applicability-decidability gate** (every classifier first-order decidable on typeclass tags; non-decidable entries rejected — `impl-04-formulas`) | Closed registry; algebraic combinations no longer hand-waved |
| 8 | **GENERIC operators** (`generic`): L sub-brackets, M sub-brackets, assembly; **instantiate active `CouplingSpec` via Stage-2.5 invariant synthesis** (`arch-19-coupling-structure`) and attach generated `InvariantTerm`s to the `E_coupling`, `L_assembly`, `M_assembly` aggregators | Antisymmetry of L, PSD of M, Jacobi, degeneracy verified |
| 9 | **Canonicals** (`canonicals`): E[x] and S[x] assembled across levels | Dimensional + analytic-limit checks pass |
| 10 | **Observables** (`observables`): the target observables as compositions (§6), in 11 bundles | Library callable for any observable; reference-crystal checks |
| 11 | **Residuals + Cert** (`residuals`, `cert`): 19 named categories, ResidualGenerator factory, 10 obligations, schema/freeze/oracle | Self-certifying outputs; usable residual contract |
| 12 | **Dynamics + integration validation** (`dynamics`): assemble the unified RHS; validate on harmonic oscillator, two-level Rabi, ideal-gas relaxation | Unified dynamics callable; RHS handed to any integrator |
| 13 | **API seal + pino-bridge**: the single typed seal; `Validate` and `Import` (`arch-16-pino-bridge`); worked examples; end-to-end demo | Shippable; downstream libraries can build against it |

Recommended start order: substrate (Phases 1–7) before any concrete observable,
then GENERIC/canonicals/observables (Phases 8–10), then residuals/cert/dynamics
(Phases 11–12), then the seal (Phase 13).

---


<a id="impl-11-verification"></a>

# Verification

### 11.1 Internal consistency (static)

The spec is internally consistent when:

1. Every observable in §6 invokes only methods (§2), templates (§3), and
   registry formulas (§4) — no inline math, no ad-hoc combinators.
2. Every method/template/formula has a typed signature with no string-encoded
   parameters.
3. The directory tree (Phase 0) contains every concept named in this plan and in
   `architecture.md`.
4. The nine regime extractions (`arch-05-generic`) are realizable as the
   compositions in `impl-06-compositions`.
5. Every residual category (§7) is grounded in a GENERIC identity or a named
   formula.
6. Every cert obligation (§10) corresponds to a residual category or an algebraic
   identity, and maps to a Layer-0 axis.
7. The counts here match `arch-09-vocabularies` exactly (12 methods, 20 templates,
   132 formulas, 11 bundles, 19 residual categories, 10 cert obligations).

Once the Phase-0 skeleton exists, items 1–7 are checkable mechanically by walking
the tree and the registry manifest.

### 11.2 Runtime gates

Five sequential gates validate the built system:

1. **Registration sanity.** All 132 formulas instantiate as `ResidualGenerator`
   records without error; every D2 entry passes the registration-time adjoint
   gate (`impl-07-residual-factory §7.5`); every D4 entry carries an
   obligation-9 rationale; D0/D1 entries register without an adjoint (none
   needed).
2. **End-to-end worked example — Diamond–W Schottky at 500 °C.** Input: diamond
   bulk + W contact + Si substrate, `Environment(T = 773 K, field = 1 MV/cm)`.
   The DAG layers fire in order; the L3 ↔ non-equilibrium cycle (charge balance
   ↔ self-heating) closes via a same-pass fixed point in ≤ 5 iterations; roughly
   three dozen residuals fire and are accounted for in the cert manifest. Output:
   Schottky barrier, drift velocity, electron temperature, self-heating ΔT,
   predicted MTTF. The run completes within its declared cost budget and cert
   obligations 1, 2, 3, 5, 8 emit verdicts.
3. **Curriculum sanity (synthetic).** A three-phase training run on Si bulk
   (~5 observables, ~1k samples) completes without GradNorm divergence, without a
   Layer-3 ↔ non-equilibrium fixed-point failure, and without an adjoint-cert
   reset mid-training.
4. **Cross-regime cert obligations fire.** Obligation-6 (BTE-σ ≡ Kubo-σ on an
   equilibrium reference); obligation-9 (a D4 query outside its declared domain
   trips with a witness); obligation-10 (a synthetic D2 formula with a broken
   adjoint is refused at registration — loud, at build time); obligation-7
   (non-topological diamond emits NA with rationale; a contrived Z₂ system emits
   the predicted edge-state count).
5. **`/informed-operator` integration smoke test.** `Validate` with `gradient =
   Skip` populates label values for ~10 Si observables; `Validate` with
   `gradient = Compute` returns finite per-residual scalars and finite
   cotangents of the declared shape on a randomly-initialized state; `Import`
   accepts a synthetic VASP-formatted payload and returns `GroundTruthBridgeGenerator`s
   with coverage masks. All return within their typed contracts.
