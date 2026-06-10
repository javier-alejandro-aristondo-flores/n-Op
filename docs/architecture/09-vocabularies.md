---
id: arch-09-vocabularies
title: Canonical vocabularies and counts
status: draft
revision: 1
canonical-for:
  - vocabulary counts
  - theory-context vocabularies
depends-on: []
referenced-by:
  - arch-06-physics-graph
  - arch-07-pipeline
  - arch-11-residuals
  - impl-09-cross-cutting
  - arch-19-coupling-structure
  - arch-20-representations
  - arch-21-multiscale-state
research-sources: []
---
# Canonical vocabularies and counts

Every other document references these numbers rather than restating them.

| Vocabulary | Count | Closed? |
|---|---|---|
| Top-level inputs | 3 | yes |
| State DOFs | 7-tuple | yes |
| BO hierarchy levels | 4 | yes |
| Dressing layers | 1 / 1.25 / 1.75 / 2 / 3 | yes |
| Computational methods | 12 (+2 sub-methods) | yes |
| Abstract-property templates | 20 | yes |
| Named formulas | 110 substantive (+2 rejected markers) | yes — see `formula-registry.md` |
| Observable bundles | 11 (B1–B11) | yes |
| Residual categories | 19 | yes |
| Cert obligations | 10 | yes |
| Layer-0 typeclasses | 4 | yes |
| Crystal symmetry group | first-class (space group × time-reversal × U(1) × SU(2)) | yes |
| State sub-DOF tags | `orbital, spin, sublattice, valley, strain, gauge, charge, none` | yes |
| Theory-context vocabularies | 10 (`XCFunctionalTag`, `PPType`, `PPSourceTag`, `ManyBodyLevel`, `GWScheme`, `DoubleCountingTag`, `ImpuritySolverTag`, `OrbitalBasisTag`, `RelativisticTreatment`, `SOCScheme`) — see §9.7 | yes (versioned) |

### 9.1 Twelve computational methods

Closed vocabulary; instances are programs in this vocabulary:

`state-readout`, `algebraic-combination`, `functional-differentiation`,
`variational-minimization`, `spectral-decomposition`, `spectral-aggregation`,
`linear-response`, `path-search`, `convex-optimization`, `kinetic-evolution`,
`statistical-sampling`, `symmetry-projection`.

Plus two registered sub-methods: `field-line-integral` (under `path-search`) and
`interface-tunneling` (under `linear-response`).

### 9.2 Twenty abstract-property templates

Parametric method-chain templates; concrete observables are instantiations. The
discipline: collapse "N observables with the same shape" into "1 template × N
argument tuples." Detailed signatures in `impl-03-templates`.

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

### 9.3 110 named formulas

Closed registry of typed, fully-parameterized algebraic formulas, named by
behavior (person-attribution names appear only as parenthetical literature
pointers). The canonical machine-readable list is
`physics/library/formulas/registry-manifest.csv` (110 substantive rows + 2
markers for relations that are enforced architecturally and therefore *not*
residualized: force = −∇energy, and equivariance). Rows 1–87 are grounded in the
domain research (`physics/research/`); rows 88–102 are the linear-response and
topology-atlas extensions; rows 105–112 are the slow-tier degradation / radiation
extensions (`arch-21-multiscale-state §21.13`). Each formula carries a typed signature, a cost tier
`T0..T3`, a differentiability tag `D0..D4`, and an applicability classifier
(§13). See `formula-registry.md` for the narrative index.

### 9.4 Eleven observable bundles

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

### 9.5 `CrystalSymmetryGroup` and `IrrepLabel`

The crystal symmetry group is a first-class entity assembled at Stage 1+2
from `PeriodicityStructure × SiteDecoration` (`arch-07-pipeline §7.2`):

```
CrystalSymmetryGroup = SpaceGroup
                     ⋊ TimeReversal             -- Z₂-graded antiunitary twist
                     ⋊ U(1)Gauge?               -- present where applicable
                     ⋊ SU(2)Spin?               -- present where applicable
```

It is the input to the Stage-2 IBZ block-diagonalization rewrite and to
the Stage-2.5 invariant generator (`arch-19-coupling-structure §19.3`).
Its identity is an `Address[GroupAtlas]` over the canonical serialization
of its finite presentation, factor descriptors, and action homomorphisms
(`arch-20-representations §20.4`). Derived outputs — character tables,
irrep decompositions, projectors, BZ stalks, Fourier caches — are
ordinary substrate fibers stored through Stage 2 / 2.5 sidecars
(`arch-20-representations §20.3`).

An **`IrrepLabel`** names one irreducible representation of a
`CrystalSymmetryGroup`. Identity is the pair

```
IrrepLabel = (group : Address[GroupAtlas-context], local-name : Symbol)
```

— the local name (`Γ₁`, `X₃⁺`, …) is unique only inside its group
context. `IrrepLabel`s are the output discriminators of Stage-2
block-diagonalization and the input discriminators selecting which
trivial-irrep basis the Stage-2.5 generator projects onto.

### 9.6 Allowed `(StateComponent, SubDofTag)` pairs

`SubDofTag` is the closed vocabulary of internal-DOF labels
(`arch-19-coupling-structure`). Not every state component carries every
sub-DOF; the allowed pairs are:

| Component | Allowed `SubDofTag`s |
|---|---|
| `γ̂` | `orbital`, `spin`, `sublattice` *(when applicable)*, `valley` *(when applicable)* |
| `A`  | `gauge` |
| `R_I` | `none` |
| `P_I` | `none` |
| `h`  | `strain` |
| `Π_h` | `strain` |
| `Z_I` | `charge` |

`StatePiece` constructors (`arch-19-coupling-structure §19.2`) reject
pairs not listed here at registration time.

### 9.7 Theory-context vocabularies

The four axes of `TheoryContext` (`arch-19-coupling-structure §19.11`) —
the global theory frame a `CouplingSpec` is interpreted in — are built
from ten closed C1 vocabularies. They are genuinely new (no existing
arch-09 vocabulary covers them; the closest neighbour, the
`{SCP, SSCHA, GW, BSE-iterated, polaron}` selector inside the §9.2
`SelfConsistentRenormalizationOf` template, is a *per-observable dressing
method*, a different axis from the composition-global theory frame). Each
is a `Universe[T]` instance with `carrier_kind = Closed` and dense `u32`
ordinals (`arch-20-representations §20.1, §20.3`); adding a member is a
versioned `schema_version` bump (`arch-20 §20.9`), not an open-registry
append, because it changes the meaning of every recorded coefficient.

| Vocabulary | Members (MVP) | Notes |
|---|---|---|
| `XCFunctionalTag` | `LDA(·) \| GGA(·) \| MetaGGA(·) \| Hybrid(flavour, exx_fraction, screening_omega?)` | exchange-correlation functional; hybrid carries float exact-exchange fraction in payload |
| `PPType` | `NormConserving \| Ultrasoft \| PAW` | pseudopotential construction kind |
| `PPSourceTag` | `PseudoDojo(version) \| SSSP(version, accuracy) \| GBRV(version) \| VASP_PAW(set) \| Custom(DOI?)` | the table version string is an open key, content-pinned by an optional `Address[PPFile]` digest |
| `ManyBodyLevel` | `KohnSham \| KohnShamPlusU(HubbardParams) \| GW(GWScheme) \| DMFT(DMFTParams) \| HybridAsManyBody(·)*` | discriminator closed; `+U`/DMFT carry sub-records with `PersistentMap` fields |
| `GWScheme` | `G0W0 \| GW0 \| scGW \| QSGW` | |
| `DoubleCountingTag` | `FLL \| AMF \| Dudarev` | DFT+U / DMFT double-counting |
| `ImpuritySolverTag` | `CTQMC \| ED \| NRG \| IPT` | DMFT impurity solver |
| `OrbitalBasisTag` | `Wannier \| PAW \| Lowdin` | the +U projection basis (also closes the gauge-choice ambiguity for downfolded channels) |
| `RelativisticTreatment` | `NonRelativistic \| ScalarRelativistic \| FullRelativistic(SOCScheme)` | |
| `SOCScheme` | `DiracPAW \| TwoComponentZORA \| SecondVariational \| PerturbativeSOC` | |

`AtomicSpecies` (the key universe of `pseudopotential_set`) is the
ordinary closed vocabulary of the elements; for the MVP it is `{C, B, N,
Al, Ga}`. `* HybridAsManyBody` is reserved/deprecated for V1 — a hybrid
is always recorded as `XCFunctionalTag.Hybrid` with `ManyBodyLevel.KohnSham`,
normalized by `make-theory-context` (`arch-19 §19.8`) so the
`Address[TheoryContext]` is canonical.

These vocabularies condition the *interpretation and verification* of
coefficients, never the *enumeration* of the symmetry-invariant basis;
accordingly they touch the reference-battery, named-formula-consistency,
reference-versioning, and surrogate-validity cert obligations
(`arch-12-cert`), and none of the others.

---
