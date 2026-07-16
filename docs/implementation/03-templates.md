---
id: impl-03-templates
title: The 20 abstract-property templates
status: draft
revision: 1
canonical-for:
  - template signatures
depends-on: []
referenced-by: []
research-sources: []
---
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
