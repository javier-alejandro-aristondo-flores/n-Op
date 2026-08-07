---
id: capability-slices
title: "The three capability slices"
owns:
  - capability selection discipline
  - crystal-structure prediction slice
  - carrier diffusion slice
  - heat diffusion slice
  - MVP vocabulary totals
  - MVP buildable fraction
anchors:
  selection-discipline: "Selection discipline"
  structure-prediction: "Crystal-structure prediction"
  carrier-diffusion: "Electron-cloud diffusion"
  heat-diffusion: "Heat diffusion"
  totals: "What the three slices add up to"
depends-on:
  - mvp-system
  - forced-decisions
  - build-verification
  - born-oppenheimer-levels
  - unified-state
  - canonical-vocabularies
  - named-formulas
  - residual-definitions
  - cert-obligations
  - generic-dynamics
  - applicability-classifiers
  - out-of-scope
open-questions: []
---
# The three capability slices

## Selection discipline

Each capability is a **strict selection** from the closed vocabularies — methods,
templates, formulas, bundles ([canonical-vocabularies]) — from the residual categories
of [residual-definitions#categories], and from the certification obligations of
[cert-obligations#the-ten-obligations]. Formula numbers reference the registry
manifest ([named-formulas#the-registry]).

Nothing in a capability is described in its own terms. A capability is the *set of
rows it selects*, which is what makes the totals at the end of this page a sum rather
than a second definition.

## Crystal-structure prediction

*Construct a symmetry-allowed candidate, relax it to the Born–Oppenheimer minimum, and
certify stability; one heterostructure check — c-BN on diamond — by lattice matching.*

| Facet | Content |
|---|---|
| State slots | cell vectors, ion positions, species labels; the one-body density matrix at zero temperature, for the Born–Oppenheimer energy ([unified-state#slots]) |
| Levels | quantum-electronic-substrate (the Born–Oppenheimer energy as a minimization over the density matrix) then born-oppenheimer-surface (relaxation on positions and cell) ([born-oppenheimer-levels#hierarchy]) |
| Methods | variational-minimization · functional-differentiation · algebraic-combination · symmetry-projection · spectral-decomposition · convex-optimization (hull check only) |
| Templates | `SymmetryAdaptedHamiltonianOf` · `SecondDerivativeOf` · `ClassifyOf` · `StateReadoutOf` · `AlgebraicOf` |
| Formulas | 57 elastic-stability-criteria · 60 elastic-constants · 61 bulk-modulus · 62 sound-velocity-isotropic · 85 structure-uniqueness · 30 defect-formation-energy · 44 surface-grand-potential · 52 alloy-lattice-interpolation · 54 critical-thickness-force-balance (c-BN on diamond) · 67 phase-diagram-convex-hull · 124 temperature-pressure-aware hull, whose metastability band reads zero for metastable diamond |
| Bundles | static-validity · mechanics · defect-resolved (row 30) · surface-resolved (row 44) · interface-resolved (rows 52 and 54, with row 54 also degradation) · thermodynamics (rows 67 and 124, the diamond–graphite hull) |
| Residuals | static validity (Born stability, dynamical stability, space-group equivariance) · structural equation of motion (the energy gradient on positions vanishes; stress matches) · thermodynamic consistency (the diamond–graphite hull) |
| Certification | 1 symmetry · 2 bounds · 3 analytic limits · 5 conservation |
| Implementation | density-functional Born–Oppenheimer energy with perturbation-theory stress for the elastic constants; tight binding as a warm start ([forced-decisions#tb-warm-start]) |

The acceptance test for this slice is the build's **first end-to-end gate** and is
stated with the other gates, at [build-verification#first-end-to-end-gate].

## Electron-cloud diffusion

*Electronic-structure substrate plus carrier transport through the lattice.*

| Facet | Content |
|---|---|
| State slots | the one-body density matrix and the external vector potential, with the carrier distribution emergent ([unified-state#emergence]) |
| Levels | quantum-electronic-substrate (bands from the density matrix) and non-equilibrium-kinetics (carrier transport) |
| Methods | spectral-decomposition · linear-response · kinetic-evolution · state-readout |
| Templates | `SpectrumOf` · `ResponseOfTo` · `KineticEvolutionOf` · `StateReadoutOf` · `AlgebraicOf` |
| Formulas | 1 bandgap-direct · 2 bandgap-indirect · 3 effective-mass-tensor · 4 density-of-states-tetrahedron · 5 fermi-level-charge-neutral · 6 quasi-particle-shift · 14 drude-conductivity · 15 matthiessen-mobility · 16 field-dependent-mobility · 18 saturation-velocity-intervalley · 19 hall-mobility-from-conductivity · 20 mobility-impurity-phonon · 24 electronic-thermal-conductivity |
| Excluded, non-polar | 17 saturation-velocity polar-optical limit · 21 polar-coupling-constant · 22 polar-optical-scattering-rate — masked off by the is-polar-material classifier, which is false for diamond ([applicability-classifiers#polar-predicate-split]). The physics that makes it false is [mvp-system#consequences] |
| Bundles | electronic-structure · transport |
| Residuals | equation of motion (Liouville on the density matrix; carrier streaming) · conservation (charge continuity) · positivity (density non-negative, occupations in the unit interval) · algebraic identities (the Einstein relation) |
| Certification | 1 symmetry · 2 bounds · 5 conservation · 6 named-formula consistency, Boltzmann conductivity against Kubo conductivity |
| Implementation | density-functional bands corrected by G₀W₀, with Boltzmann transport in the relaxation-time approximation; tight-binding bands as a warm start |

## Heat diffusion

*Phonon spectrum plus phonon-mediated thermal transport through the lattice.*

| Facet | Content |
|---|---|
| State slots | ion positions and ion momenta, with the phonon distribution and lattice temperature emergent |
| Levels | born-oppenheimer-surface (the energy Hessian giving phonons), equilibrium-statistics (Bose occupation), non-equilibrium-kinetics (phonon transport) |
| Methods | spectral-decomposition · spectral-aggregation · kinetic-evolution |
| Templates | `HarmonicStiffnessHessianOf` · `SpectrumOf` · `SpectralAggregateOf` (heat capacity, aggregating Bose–Einstein occupations) · `KineticEvolutionOf` |
| Formulas | 7 acoustic-sum-rule · 8 dynamical-matrix-hermiticity · 9 phonon-dispersion · 10 phonon-density-of-states · 11 phonon-group-velocity · 12 mode Grüneisen parameter, for the quasi-harmonic approximation and thermal expansion · 25 single-mode relaxation-time lattice conductivity · 121 and 122, its high-temperature siblings — a four-phonon correction and a dormant iterative-transport consistency partner · 70 self-heating operating temperature |
| Deferred | 13 self-consistent phonon theory, since the quasi-harmonic approximation suffices to about 800 °C · 26 phonon-poiseuille-length · 27 second-sound-speed, both low-temperature hydrodynamics and outside the harsh-environment target |
| Bundles | phonon · transport · non-equilibrium-operating (row 70) |
| Residuals | equation of motion (phonon streaming and collision; the heat equation) · conservation (energy) · positivity (squared frequencies non-negative) · algebraic identities (the acoustic sum rule) |
| Certification | 2 bounds · 3 analytic limits (harmonic crystal, Dulong–Petit) · 5 conservation |
| Implementation | perturbation-theory phonons with three-phonon relaxation-time transport. The closed-form quasi-harmonic plus Slack–Callaway conductivity sits alongside it as a **consistency pair, not an equivalence pair** — the rule and its enforcement are [residual-definitions#pair-kinds] |

## What the three slices add up to

Every figure below is a sum over the three tables above. It is stated here rather than
on a page of its own because a summary that can be edited independently of its source
will eventually disagree with it.

**In the MVP.**

- About **34 named formulas** — the rows selected above, including the
  high-temperature conductivity siblings 121 and 122 and the hull pair 67 and 124.
- All computational methods except `path-search` and `statistical-sampling`, with
  `convex-optimization` reaching only the hull check: chemical and Monte-Carlo
  machinery is not on the diamond path.
- **Ten distinct templates** — about half the template vocabulary.
- Bundles electronic-structure, phonon, transport, mechanics and static-validity as
  **primaries**; defect-resolved, surface-resolved, interface-resolved,
  thermodynamics, non-equilibrium-operating and degradation touched per row. Every
  bundle is touched; five are primaries.
- Residual families exercised: micro equation-of-motion violation, conservation,
  positivity, algebraic identities, static snapshot, static thermodynamic. Degeneracy
  is certification-only ([generic-dynamics#operators],
  [residual-definitions#categories]); the slow-tier and macro equation-of-motion
  siblings defer with their tiers.
- **Certification obligations 1–6 and 10.** The registration adjoint gate — obligation
  10 — stays in the MVP because adjoint-tagged gradients must be validated when the
  operator first trains. Only the battery and topology obligations 7, 8 and 9 defer.
- The substrate and one-shot-dressing layers are wired: G₀W₀, the quasi-harmonic
  approximation, and density-functional perturbation theory.

**Deferred.** The complement — the remaining formulas, the defect zoo beyond row 30,
surface chemistry, interface and Schottky physics, high-field and hot-carrier and
breakdown, degradation, most of the topology atlas, iterative dressing,
self-consistent phonon theory, the non-diamond materials, and heterostructures beyond
the single c-BN lattice match — is [out-of-scope#exclusions]. Deferrals are stated
once, where scope exclusions are owned.

**The buildable unit is roughly one-third of the full vocabulary.** That is the one
judgment on this page rather than a sum, and it is what makes the MVP a demonstration
rather than a subset chosen for convenience.
