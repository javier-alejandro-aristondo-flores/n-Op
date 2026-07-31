---
id: typed-compositions
title: "Target observables as typed compositions"
owns:
  - per-observable compositions
  - property coverage claim
  - unregistered composition formulas
anchors:
  purpose: "What this page proves"
  coverage: "Property to composition"
  structural: "Structural"
  electronic: "Electronic"
  optical: "Optical"
  mechanical: "Mechanical"
  thermal: "Thermal"
  magnetic: "Magnetic"
  transport: "Transport"
  thermodynamic: "Thermodynamic"
  chemical-surface: "Chemical and surface"
  declared-gap: "The declared gap"
depends-on:
  - properties
  - computational-methods
  - property-templates
  - named-formulas
  - cert-obligations
  - residual-definitions
  - accuracy-ledger
  - traps
open-questions:
  - id: unregistered-composition-formulas
    anchor: declared-gap
    summary: "Eighteen formula names invoked by the compositions on this page are not rows in the manifest, so the closed-vocabulary claim does not hold in full. Nine are transcription plus tag assignment; nine need literature before a row would be defensible."
  - id: undeclared-non-formula-slots
    anchor: declared-gap
    summary: "Two names are invoked in slots that are not formula arguments and are neither manifest rows nor part of the declared gap: exchange-coupling-formula as a response kernel, and harmonic-rate-prefactor as a rate prefactor. Whether they belong to the declared gap or to a kernel vocabulary no page owns is unsettled."
  - id: cij-averaging-scheme
    anchor: mechanical
    summary: "Which averaging scheme the bulk modulus takes over the elastic constants — Voigt, Reuss or Hill — is an open pick."
---
# Target observables as typed compositions

## What this page proves

Every property in the catalogue ([properties#catalogue]) written as a typed
composition. That is the validation that the closed vocabulary covers the target
scope: if a targeted property cannot be written as a composition of methods
([computational-methods]), templates ([property-templates]) and named formulas
([named-formulas]), the vocabulary is short something, and the gap is visible
here rather than discovered during implementation.

The coverage table below is the claim in checkable form. It pairs each catalogue
property with the composition identifiers that realise it, and every identifier
it names is defined in a block on this page.

**All target observables resolve to typed compositions over the closed
vocabulary, except the declared gap below** — eighteen invoked formula names that
are not manifest rows. The claim is stated with its exception rather than
without.

## Property to composition

| Property | Realised by |
|---|---|
| Lattice parameters | `LatticeParameters` |
| Bond lengths | `BondLengths` |
| Crystal structure | `CrystalStructure` |
| Defects | `DefectFormationEnergy`, `DefectCharacterization` |
| Surfaces | `SurfaceRegion`, `SurfaceEnergy` |
| Band structure | `BandStructure` |
| Density of states | `DOS` |
| Band gap | `BandGap` |
| Charge density | `ChargeDensity` |
| Absorption | `Absorption` |
| Dielectric function | `DielectricFunction` |
| Refractive index | `RefractiveIndex` |
| Photoluminescence | `Photoluminescence` |
| Elastic constants | `ElasticConstants` |
| Bulk modulus | `BulkModulus` |
| Stress–strain response | `StressStrainLinear` |
| Hardness | `Hardness` |
| Phonons | `PhononDispersion` |
| Heat capacity | `HeatCapacity` |
| Thermal conductivity | `ThermalConductivity` |
| Thermal expansion | `ThermalExpansion` |
| Magnetic moment | `MagneticMoments` |
| Spin density | `SpinDensity` |
| Exchange interactions | `ExchangeInteractions` |
| Carrier mobility | `CarrierMobility` |
| Ionic diffusion | `IonicDiffusion` |
| Conductivity | `Conductivity` |
| Migration barriers | `MigrationBarrier` |
| Total energy | `TotalEnergy` |
| Formation energy | `FormationEnergy` |
| Phase stability | `PhaseStability` |
| Free energy | `FreeEnergy` |
| Adsorption energy | `AdsorptionEnergy` |
| Reaction pathways | `ReactionPathway` |
| Catalytic activity | `CatalyticActivity` |
| Surface energy | `SurfaceEnergy` |

`SurfaceEnergy` realises two catalogue properties and is defined once, in the
chemical and surface section.

## Structural

```
LatticeParameters     = StateReadoutOf(state.h, extractor = cell-metric-extraction)

BondLengths           = StateReadoutOf((state.R, state.h),
                                       extractor = pairwise-distance-PBC)

CrystalStructure      = ClassifyOf((state.R, state.h),
                                   classifier = space-group-detection)

DefectFormationEnergy = AlgebraicOf({E_defect = E_BO(crystal-with-defect),
                                     E_perfect = E_BO(reference),
                                     Δn, μ = env.chem-pots, q, E_F = env.Fermi-level},
                                    formula = defect-formation-energy)

DefectCharacterization = ComparisonOf(state, reference-perfect,
                                      metric = atom-matching)

SurfaceRegion         = StateReadoutOf(state, extractor = extract-surface-region)
```

## Electronic

```
BandStructure = SpectrumOf(Ĥ_KS[γ̂], domain = BZMesh(nx, ny, nz))

DOS           = SpectralAggregateOf(BandStructure, aggregator = delta-energy-bin,
                                    weights = uniform)

BandGap       = AlgebraicOf({BandStructure}, formula = bandgap-indirect)

ChargeDensity = StateReadoutOf(γ̂, extractor = position-diagonal-trace)
```

## Optical

```
DielectricFunction = ResponseOfTo(observable = γ̂, perturbation = A-ext,
                                  kernel = current-current-correlator,
                                  frequency = ω-mesh)

Absorption(ω)      = AlgebraicOf({DielectricFunction},
                                 formula = absorption-from-dielectric)

RefractiveIndex(ω) = AlgebraicOf({DielectricFunction},
                                 formula = refractive-index-from-dielectric)

Photoluminescence  = RadiativeEmissionOf(excited_state = γ̂-pumped,
                                         optical_coupling = dipole-d)
```

## Mechanical

```
ElasticConstants   = SecondDerivativeOf(F = E_BO, x₀ = equilibrium-state,
                                        coord = symmetric-strain-η,
                                        metric = Frobenius²-volume-normalized)

BulkModulus        = AlgebraicOf({ElasticConstants}, formula = bulk-modulus)

StressStrainLinear = AlgebraicOf({ElasticConstants, applied-ε},
                                 formula = linear-elasticity-stress-strain)

Hardness(model)    = AlgebraicOf({K, G, …},
                                 formula = {chen | teter | tian | mazhnik-oganov}-hardness)
```

Which averaging scheme `BulkModulus` takes over the elastic constants — Voigt,
Reuss or Hill — is an open pick; [accuracy-ledger#elastic-coefficients] carries
the accuracy note on the elastic constants it depends on.

## Thermal

```
PhononDispersion    = SpectrumOf(operator = HarmonicStiffnessHessianOf(E_BO, R₀, u),
                                 domain = BZMesh)

HeatCapacity(T)     = SpectralAggregateOf(PhononDispersion,
                                          aggregator = bose-einstein-cv(T),
                                          weights = uniform)

ThermalConductivity = KineticEvolutionOf(distribution = phonon-distribution(n_qν),
                                         collisions = three-phonon-anharmonic-Ψ,
                                         gradient = ∇T, method = BTE-RTA)

ThermalExpansion    = AlgebraicOf({ModeGrüneisen(T), HeatCapacity(T)},
                                  formula = QHA-expansion)
```

## Magnetic

```
MagneticMoments      = StateReadoutOf(γ̂, extractor = atomic-sphere-spin-integral)

SpinDensity          = StateReadoutOf(γ̂, extractor = position-diagonal-spin-trace)

ExchangeInteractions = ResponseOfTo(observable = γ̂,
                                    perturbation = infinitesimal-spin-rotation,
                                    kernel = exchange-coupling-formula, frequency = 0)
```

`exchange-coupling-formula` names nothing in the manifest and sits in a kernel
slot rather than a formula slot, so the declared-gap mechanism below does not
cover it.

## Transport

```
ConductivityViaBTE  = KineticEvolutionOf(distribution = carrier-f_n,
                                         collisions = e-phonon-scattering-g²,
                                         gradient = applied-E-field, method = BTE-RTA,
                                         truncation = first-order)

ConductivityViaKubo = ResponseOfTo(observable = current-operator-ĵ, perturbation = A,
                                   kernel = current-current-correlator,
                                   frequency = ω→0⁺)

Conductivity        = { ConductivityViaBTE, ConductivityViaKubo }

CarrierMobility     = AlgebraicOf({Conductivity, carrier-density},
                                  formula = mobility-from-conductivity)

IonicDiffusion      = let ν_min    = SpectrumOf(HarmonicStiffnessHessianOf(E_BO, init),
                                                normal-modes)
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
                                       method = climbing-image-NEB, n_images = 9,
                                       tol = 1e-3)
```

`Conductivity` evaluates both members. Their agreement is not assumed: it is
enforced as a method-equivalence residual under obligation-6
([residual-definitions#pair-kinds], [cert-obligations#the-ten-obligations]).
This is the worked instance of that obligation — two methods, one observable,
one residual scoring the difference.

The harmonic transition-rate normalization consumes the **product** of normal-mode
frequencies through the `product-of-modes` extractor, not the spectra
([named-formulas#corrected-forms]).

## Thermodynamic

```
TotalEnergy     = StateReadoutOf(E[x], extractor = identity)

FormationEnergy = AlgebraicOf({E_compound = E_BO(target),
                               E_refs = {E_BO(ref)}, n_i, μ_i = env.chem-pots},
                              formula = formation-energy-from-references)

PhaseStability  = ConvexOptimization(points = {(x_φ, F_φ)},
                                     objective = lower-convex-envelope)

FreeEnergy(T)   = AlgebraicOf({E_BO,
                               F_vib = SpectralAggregateOf(PhononDispersion,
                                                           bose-einstein-helmholtz(T)),
                               F_el  = SpectralAggregateOf(BandStructure,
                                                           fermi-dirac-helmholtz(T))},
                              formula = helmholtz-free-energy-decomposition)
```

## Chemical and surface

```
AdsorptionEnergy = AlgebraicOf({E_BO(slab+ads), E_BO(slab), E_BO(molecule)},
                               formula = adsorption-energy-difference)

ReactionPathway  = PathStationaryOf(F = E_BO, initial = reactant, final = product,
                                    method = climbing-image-NEB)

CatalyticActivity = let RateNetwork = {(step, AlgebraicOf({ν₀ = harmonic-rate-prefactor,
                                                           E_a = PathStationaryOf(…).saddle,
                                                           T}, formula = htst-rate))}
                        θ = MicrokineticSteadyStateOf(network = RateNetwork,
                                                      initial = vacuum-coverage,
                                                      driving = env.chem-pots)
                    in AlgebraicOf({θ, RateNetwork, RC-step}, formula = turnover-frequency)

SurfaceEnergy    = AlgebraicOf({E_BO(slab), E_BO(bulk-per-formula-unit), n, A},
                               formula = slab-arithmetic)
```

`harmonic-rate-prefactor` names the same quantity the transport section computes
through `harmonic-transition-rate-normalization`, under a second name and in a
slot the declared-gap mechanism does not sweep.

## The declared gap

Eighteen formula names invoked above are **not rows in the manifest**, so this
page's closed-vocabulary claim does not hold in full. They are listed here, in
one table, so that a check over the compositions above can separate a *declared*
gap from an *undeclared* one — a new unregistered name still fails loudly.

| Formula name | Registering it is | Form |
|---|---|---|
| `refractive-index-from-dielectric` | transcription | `n(ω) = Re(√ε)` |
| `absorption-from-dielectric` | transcription | `α(ω) = (2ω/c)·Im(√ε)` |
| `mobility-from-conductivity` | transcription | `μ = σ/(n·e)` |
| `helmholtz-free-energy-decomposition` | transcription | `F = E_BO + F_vib + F_el` |
| `linear-elasticity-stress-strain` | transcription | Hooke's law |
| `slab-arithmetic` | transcription | determined by its inputs |
| `arrhenius` | transcription | determined by its inputs |
| `adsorption-energy-difference` | transcription | determined by its inputs |
| `QHA-expansion` | transcription | tensor form pinned by [traps#thermal-expansion-form] |
| `chen-hardness` | research | needs literature |
| `teter-hardness` | research | needs literature |
| `tian-hardness` | research | needs literature |
| `mazhnik-oganov-hardness` | research | needs literature |
| `harmonic-transition-rate-normalization` | research | needs literature |
| `jump-diffusivity` | research | the geometric prefactor convention is the trap |
| `htst-rate` | research | needs literature |
| `turnover-frequency` | research | needs literature |
| `formation-energy-from-references` | research | needs literature |

**They are deliberately not registered.** A manifest row must be defensible
against a literature citation, and registering these on thin provenance would
put unsourced rows into the artifact whose entire discipline is that unsourced
values are refused ([traps#unprovenanced-coefficient]). A declared gap is
honest; an unsourced row is not.

The two kinds need different work. **Transcription** means the expression is
written above, or the name plus its inputs determine it, or this corpus already
pins the form — registering one is transcription plus tag assignment. The four
expressions in the table are recorded precisely because that is what makes
those rows transcription rather than research: deleting them would convert four
bookkeeping tasks into four literature searches. `QHA-expansion` is the case
where the pinned form matters most, because [traps#thermal-expansion-form] pins
the *tensor* form including the compliance-not-stiffness trap that makes the
naive version dimensionally wrong.

**Research** means a modelling choice with literature behind it, and the choice
has to be made and cited before a row exists.
