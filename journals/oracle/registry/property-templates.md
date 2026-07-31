---
id: property-templates
title: "Property templates"
owns:
  - template signatures
  - what each template produces
  - template collapse discipline
  - template overlap resolution
anchors:
  what-a-template-is: "What a template is"
  discipline: "The collapse discipline"
  what-each-produces: "What each template produces"
  signatures: "The typed signatures"
  overlap-resolution: "Overlap resolution"
depends-on:
  - computational-methods
  - named-formulas
  - typed-compositions
  - typeclass-alphabet
  - topology-atlas
  - cert-obligations
open-questions: []
---
# Property templates

## What a template is

A template is a parameterized chain of computational methods
([computational-methods]). A concrete observable is an instantiation of one —
the template with its argument tuple filled in. [typed-compositions] is the set
of instantiations.

## The collapse discipline

**Collapse *N observables with the same shape* into *one template with N argument
tuples*.**

The alternative — one entry per observable — makes the vocabulary grow with the
catalogue, and every compiler pass, typing rule and certification obligation
grows with it. A template that admits a new observable by taking a new argument
tuple admits it for free.

The discipline also decides what is *not* a template: a construction that would
need its own entry only because its arguments differ is a parameterization, and
belongs inside an existing template. The cases where that call has been made are
below.

## What each template produces

The observables each template instantiates. Signatures follow.

*General:*

| Template | Produces |
|---|---|
| `StateReadoutOf` | lattice parameters, bond lengths, charge density, magnetic moments |
| `AlgebraicOf` | any named-formula combination — formation energy, surface energy, hardness |
| `SecondDerivativeOf` | elastic constants, force constants, polar susceptibility |
| `SpectrumOf` | band structure, phonon dispersion |
| `SpectralAggregateOf` | density of states, phonon density of states, heat capacity, vibrational and electronic free energy |
| `ResponseOfTo` | dielectric function, frequency-dependent conductivity, exchange interactions |
| `PathStationaryOf` | migration barrier, reaction pathway |
| `KineticEvolutionOf` | electronic and thermal conductivity, ionic diffusivity |
| `ClassifyOf` | space group, Wyckoff orbit, crystal-structure class |
| `ComparisonOf` | defect characterization, surface-region comparison |
| `RadiativeEmissionOf` | photoluminescence |
| `MicrokineticSteadyStateOf` | catalytic activity, turnover frequency |

*Renormalization, configurational, symmetry:*

| Template | Produces |
|---|---|
| `SelfConsistentRenormalizationOf` | fixed-point dressing of a bare quantity — renormalized phonons, self-consistent self-energies, polaron dressing |
| `ConfigurationalFreeEnergyOf` | composition-dependent free energy |
| `SymmetryAdaptedHamiltonianOf` | the most general symmetry-allowed Bloch Hamiltonian for a composition |

*Domain interface, defect, thermodynamic:*

| Template | Produces |
|---|---|
| `InterfaceEquilibriumOf` | Schottky barrier, band offset, interface dipole |
| `SelfConsistentChargeBalanceOf` | charge-neutral Fermi level, defect populations, carrier densities |
| `HarmonicStiffnessHessianOf` | the mass-weighted dynamical matrix |
| `BiSlabGrandPotentialOf` | adhesion energy, interface formation energy, debonding force |
| `MassActionEquilibriumOf` | equilibrium composition of a reaction set |

## The typed signatures

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
        one fixed-point structure shared across self-consistent phonons, the GW
        self-energy, BSE iteration and polaron dressing; emits IterativeResult
        certification evidence

ConfigurationalFreeEnergyOf(parameterization: {ClusterExpansion(ECI),
                                               RedlichKister(L_ν, order),
                                               BraggWilliams},
                            composition: x, T: Temperature) → G_config
        the cluster expansion is a discrete zero-temperature lattice energy and
        Redlich–Kister is a continuous composition-dependent finite-temperature
        excess Gibbs energy — distinct parameterizations of one template, not
        instances of each other

SymmetryAdaptedHamiltonianOf(space-group: SpaceGroup,      -- 1..230 (+ magnetic)
                             wyckoff-orbits: {WyckoffOrbit},
                             orbital-basis: {Orbital},
                             neighbor-shells: Int) → ParameterizedBlochHamiltonian
        constructive: emits the most general symmetry-allowed H(k) as a
        parametric family indexed by the couplings symmetry allows — the
        substrate the symmetry-indicator classification reads

InterfaceEquilibriumOf(left: Crystal, right: Crystal, coupling: InterfaceCoupling,
                       env: Environment, method: BiSlabSolver) → BicrystalState
        charge transfer and band alignment together

SelfConsistentChargeBalanceOf(host: Crystal, defect-set: {DefectSpecies},
                              env: Environment, method: ChargeNeutralitySolver,
                              tol: Real) → (E_F: Scalar, {N_q}: Vector, {n,p}: Scalar²)
        closes the equilibrium-statistics ↔ non-equilibrium dependency cycle in
        a same-pass fixed point rather than by ordering the two

HarmonicStiffnessHessianOf(F: Functional, x₀: StatePoint,
                           displacement-basis: Basis, method: HessianMethod)
                           → Tensor[3N × 3N]
        symmetrization, acoustic-sum-rule enforcement and the Born-effective-charge
        correction are template-level concerns, not caller concerns

BiSlabGrandPotentialOf(slab-left: Crystal, slab-right: Crystal,
                       gap: Length, env: Environment) → Scalar

MassActionEquilibriumOf(species: {Species}, reactions: {Reaction},
                        env: Environment, method: NonlinearSolver) → CompositionVector
        an equilibrium readout — point-defect, gas-exchange and adsorbate
        equilibria — distinct from MicrokineticSteadyStateOf, which is a driven
        steady state
```

The argument types these signatures are written in are defined by no page
([computational-methods#argument-types]).

## Overlap resolution

Three constructions look like candidate templates and are not:

- **`ClusterExpansion` is a parameterization of `ConfigurationalFreeEnergyOf`**,
  not a separate template. It is one of three parameterizations of one free
  energy, and the three are distinct in form rather than in kind.
- **Bulk-boundary correspondence is a certification obligation, not a template.**
  It is obligation-7 ([cert-obligations]), a morphism over the discrete
  structures the topology atlas emits ([typeclass-alphabet#discrete-structure],
  [topology-atlas#entry]). A template produces an observable; this checks a
  relation between two, which is the certification layer's job.
- **`HarmonicStiffnessHessianOf` specializes `SecondDerivativeOf`** rather than
  duplicating it. The specialization exists because the symmetrization and
  sum-rule work belongs to every caller and would otherwise be repeated by each.
