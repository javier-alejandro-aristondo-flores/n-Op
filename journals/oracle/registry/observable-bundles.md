---
id: observable-bundles
title: "Observable bundles"
owns:
  - the eleven observable bundles
  - bundle contents
  - linear-response primitives
anchors:
  the-eleven: "The eleven bundles"
  contents: "What each bundle holds"
  linear-response-primitives: "Rows that feed several bundles"
depends-on:
  - named-formulas
  - formula-registry
  - born-oppenheimer-levels
  - multiscale-state
  - residual-definitions
  - traps
open-questions: []
---
# Observable bundles

## The eleven bundles

Observables are grouped by physics domain. The grouping is what the residual
machinery aggregates over ([residual-definitions#facets]), so it is the
grouping that has to be canonical — a second grouping of the same observables
competes with it rather than complementing it.

| Bundle | Primary level |
|---|---|
| `electronic-structure` | quantum-electronic-substrate |
| `phonon` | born-oppenheimer-surface |
| `transport` | non-equilibrium-kinetics |
| `defect-resolved` | born-oppenheimer-surface, equilibrium-statistics, non-equilibrium-kinetics |
| `surface-resolved` | born-oppenheimer-surface |
| `interface-resolved` | born-oppenheimer-surface |
| `mechanics` | born-oppenheimer-surface |
| `thermodynamics` | equilibrium-statistics |
| `non-equilibrium-operating` | non-equilibrium-kinetics |
| `static-validity` | born-oppenheimer-surface |
| `degradation` | non-equilibrium-kinetics |

The levels are the Born–Oppenheimer hierarchy's
([born-oppenheimer-levels#hierarchy]).

**The `bundle` field of a formula record takes these eleven names or the value
`linear-response-primitive`** — twelve admissible values in all. Any consumer
validating that field reads the vocabulary from here, and reading the table alone
is how the four rows below come to look like defects
([formula-registry#harvest]).

A file tree may group observable code by output data shape — zone-resolved,
energy-resolved, real-space, tensor-indexed — and that grouping is a convenience
of the layout. The residual-driving grouping is the eleven above.

## What each bundle holds

Representative contents. The authoritative per-row assignment is the manifest's
`bundle` field.

- **`electronic-structure`** — band structure, density of states, band gap,
  charge density, the effective-mass tensor, wavevector-resolved density of
  states.
- **`phonon`** — phonon dispersion, phonon density of states, group velocity,
  Grüneisen parameters, self-consistent phonons.
- **`transport`** — conductivity by both the Boltzmann and Kubo routes, mobility
  (Matthiessen combination, Caughey–Thomas field dependence), Seebeck
  coefficient, Wiedemann–Franz electronic thermal conductivity, Hall mobility.
- **`defect-resolved`** — defect formation energy, charge-transition levels,
  populations, Shockley–Read–Hall and Auger recombination, multiphonon capture,
  Huang–Rhys factors.
- **`surface-resolved`** — surface energy, surface grand potential, Wulff shape,
  termination stability window.
- **`interface-resolved`** — Schottky barrier (registered as
  `barrier-from-workfunction-affinity`, plus the metal-induced-gap-states
  correction), band offset, interface dipole, adhesion, contact resistance, field
  emission; the polarization and two-dimensional-electron-gas package (rows
  113–115, 117–118); the gate-dielectric layer models (`poole-frenkel-current`,
  row 129, and the pyroelectric sheet-density drift, row 128).
- **`mechanics`** — elastic constants, bulk modulus, sound velocity, hardness,
  deformation potentials, piezoresistance.
- **`thermodynamics`** — Gibbs free energy, phase-diagram convex hull,
  chemical-potential references, the Clausius–Clapeyron slope.
- **`non-equilibrium-operating`** — self-heating operating temperature, the
  coupled electromagnetic–thermal solve, hot-carrier temperature balance, impact
  ionization, avalanche, tunnelling currents (Fowler–Nordheim,
  Richardson–Dushman, Padovani–Stratton), non-equilibrium Green's-function
  transmission.
- **`static-validity`** — bond-valence sum,
  `radius-ratio-coordination-class` (a.k.a. the Pauling radius ratio),
  `elastic-stability-criteria` (a.k.a. Born stability), generalized
  stacking-fault energy, structure uniqueness; the X-ray-diffraction
  structure-factor channel (row 132).
- **`degradation`** — carbide growth, electromigration mean time to failure,
  `plastic-strain-fatigue-life` (a.k.a. Coffin–Manson fatigue); the slow-tier
  kinetics of rows 105–112 — vacancy generation, hydrogen redistribution and
  desorption, platelet nucleation, vibration-driven dislocation multiplication,
  air oxidation, radiation displacement ([multiscale-state#slow-kinetics]); the
  gate-dielectric lifetime pair (`tddb-thermochemical-e-model`, row 130, and
  `dielectric-crystallization-jmak`, row 131).

Four rows carry a behaviour name where the literature carries a person's name,
and the person is kept in the row's provenance cell instead:
`barrier-from-workfunction-affinity`, `radius-ratio-coordination-class`,
`elastic-stability-criteria`, `plastic-strain-fatigue-life`. The behaviour name
is what a reader can bind to an object without knowing the literature; the
person's name is what a literature search needs, and the provenance cell is where
a literature search starts ([formula-registry#provenance]).

## Rows that feed several bundles

Rows 91–94 — the lattice Coulomb scalar, the operator position derivative (Born
effective charges), the high-frequency response tensor, and the electronic
linear-response tensor — carry `linear-response-primitive` rather than a bundle
name. They are primitives of the quantum-electronic substrate that feed several
bundles, so assigning them to one would be a false statement about which
residuals they drive.

`linear-response-primitive` is a value of the `bundle` field, not a level of the
Born–Oppenheimer hierarchy. The distinction matters because these four rows are
correct as they stand: a consumer that takes the bundle vocabulary from the
eleven-row table above, rather than from the field's full vocabulary, finds four
rows carrying a value it does not recognise and reports four correct rows as
defects ([traps#vocabulary-has-an-owner]).
