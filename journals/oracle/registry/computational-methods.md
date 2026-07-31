---
id: computational-methods
title: "Computational methods"
owns:
  - the twelve computational methods
  - method signatures
  - sub-method registration
  - method argument types
anchors:
  the-alphabet: "The alphabet"
  signatures: "The typed signatures"
  sub-methods: "Sub-methods"
  argument-types: "The argument types are not defined"
depends-on:
  - named-formulas
  - property-templates
  - typeclass-alphabet
  - compose-time-pipeline
  - build-verification
open-questions:
  - id: argument-type-alphabet-homeless
    anchor: argument-types
    summary: "The argument types the method and template signatures are written in — Extractor, Aggregator, ResponseKernel, Optimizer, EigenSolver and the rest — are defined by no page, so neither set of signatures can be typed as written."
---
# Computational methods

## The alphabet

Twelve computational methods, and the vocabulary is closed. Every program the
oracle runs is a composition in this alphabet:

`state-readout` · `algebraic-combination` · `functional-differentiation` ·
`variational-minimization` · `spectral-decomposition` · `spectral-aggregation` ·
`linear-response` · `path-search` · `convex-optimization` · `kinetic-evolution` ·
`statistical-sampling` · `symmetry-projection`

Closure is the property that makes the rest of the architecture possible. A
composition built from a closed alphabet can be typed, rewritten and
differentiated by a compiler that knows only the alphabet
([compose-time-pipeline]); an open one cannot, because the compiler would have to
handle a case it has never seen. Every extension pressure therefore lands on the
sub-method dispatch table, not on this list.

## The typed signatures

Each method carries a typed signature and a sub-method dispatch:

```
state-readout            StateReadout(x: State, extractor: Extractor) → Value
                         sub: pairwise-distance-PBC, atomic-sphere-integral,
                              position-diagonal-trace, cell-metric-extraction,
                              spectral-extremum, occupation-sum

algebraic-combination    AlgebraicCombination(inputs: {Value},
                                              formula: NamedFormula) → Value
                         always dispatches to a registry row — no inline math

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
                         sub: delta-sum (density of states), partition-Z
                              (log-sum-exp), thermal-average
                              (Bose / Fermi / Maxwell-Boltzmann)

linear-response          LinearResponse(observable: Operator, perturbation: Operator,
                                        kernel: ResponseKernel, frequency: Real = 0)
                                        → Response
                         sub: Kubo, linear-response-DFT (Dyson), Greens-function,
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
                              mesh-interpolation †, Cahn-Hilliard, Allen-Cahn

statistical-sampling     StatisticalSampling(distribution: Distribution, method: Sampler,
                                             n_samples: Int) → SampleSet
                         sub: Monte-Carlo, molecular-dynamics, kMC, importance-sampling

symmetry-projection      SymmetryProjection(target: Tensor, group: SymmetryGroup,
                                            projection_kind: ProjKind) → Tensor
                         sub: point-group-projection, space-group-projection,
                              time-reversal-symmetrize
```

The `algebraic-combination` constraint is the call-site half of the rule
[named-formulas#no-inline-math] states: the method takes a registry row as an
argument and has no other way to combine its inputs.

Return types such as `Response`, `Field` and `Tensor` are the typeclass aliases
of [typeclass-alphabet#aliases]; without them these signatures do not type.

Methods are the primitives; [property-templates] parameterizes chains of them,
and a concrete observable is an instantiation of a template.

## Sub-methods

Three sub-methods marked † above are registered for the wide-bandgap scope:
`interface-tunneling` under `linear-response`, `field-line-integral` under
`path-search`, and `mesh-interpolation` under `kinetic-evolution`.

**A sub-method extends a method's dispatch table without changing its typed
signature.** Registration requires two things: a sub-method test, and a
regression-freeze entry ([build-verification]). That is what keeps the alphabet
closed under pressure — a new numerical technique is a new dispatch entry, not a
new method.

`mesh-interpolation` is the compile-time band and electron-phonon interpolator.
It uses Fourier interpolation for gauge-free quantities — band energies and
velocities — and Wannier interpolation for gauge-sensitive ones, principally the
electron-phonon matrix elements, with dipole and quadrupole polar corrections
that are mandatory rather than optional. The runtime reads only the interpolated
grid, which is continuously differentiable, so gradients taken through it are
well defined.

Interpolation is a sub-method, not a thirteenth method. The distinction is not
bookkeeping: a thirteenth method would be a thirteenth case in every compiler
pass, a thirteenth arm in every typing rule, and a change to the closure claim
above.

## The argument types are not defined

The signatures on this page and on [property-templates] are written in argument
types — `Extractor`, `Aggregator`, `ResponseKernel`, `PathMethod`, `Optimizer`,
`EigenSolver`, `ConvexSolver`, `KineticMethod`, `Sampler`, `ProjKind`,
`Classifier`, `ComparisonMetric`, `TensorNorm`, `HessianMethod`,
`NonlinearSolver`, `BiSlabSolver`, `ChargeNeutralitySolver`,
`ConvergenceCriterion` — **that no page defines.** They appear only at use sites.

Neither the twelve signatures here nor the twenty on [property-templates] can be
typed as written until they are, and an implementation reading these signatures
has to invent them. Stated here rather than left to be discovered.
