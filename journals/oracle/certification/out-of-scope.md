---
id: out-of-scope
title: "Out of scope"
owns:
  - scope exclusions
  - out-of-scope refusal mechanism
anchors:
  exclusions: "What the oracle library does not model"
  refusal-mechanism: "How a refusal is raised"
depends-on:
  - accuracy-ledger
  - cert-obligations
  - coupling-structure
  - multiscale-state
  - purpose-and-scope
  - traps
open-questions: []
---
# Out of scope

## What the oracle library does not model

Stated and held. Each entry is a refusal the library makes on purpose, and several are
the enforcement site another page's hazard points at.

- **Strongly-correlated systems** — frustrated Wigner crystals, spin liquids, Mott
  physics. The one-body density matrix is mean-field by construction, and ultra-wide-gap
  materials are large-gap and far from Mott physics.
- **Flexoelectricity in centrosymmetric materials** — below the numerical-noise floor;
  order-of-magnitude only.
- **Magneto-thermal coupling in heavy contact metals** — formally present in the
  entropy, not modeled.
- **Deep-defect non-Markovian dynamics** — a Markov master-equation closure is assumed.
- **Polaron localization beyond Fröhlich.**
- **Full non-equilibrium Green's-function tunneling, full self-consistent phonon theory,
  and the live iterative linearized-Boltzmann and full four-phonon solves** — these are
  `iterative-dressing`, deferred to V2. What *does* ship in V1 on the `one-shot-dressing`
  path is the **closed-form high-temperature four-phonon correction**, a multiplicative
  conductivity factor valid at `T ≳ 0.4 Θ_D` (registry row 121), and the
  **iterative-Boltzmann conductivity sibling anchored to a published solution** (row 122,
  a dormant `MethodEquivalence` binding with no live solve). Where a cheap proxy is
  needed during training it is a registered relaxation carrying an obligation-9 validity
  domain — and **no such proxy ships in V1**, with the accuracy regime declared in
  [accuracy-ledger#observable-regimes].
- **Electron-phonon gap renormalization beyond the adiabatic one-shot** — the faithful
  Brillouin-zone sum over the spectral function, and the non-adiabatic treatment worth
  about 25% on polar zero-point renormalization, are `iterative-dressing` and deferred to
  V2. V1 ships the adiabatic one-shot dressing `ΔE_g = ZPR·coth(Θ/2T)` (registry row 120)
  with the per-material coefficients of [accuracy-ledger#ahc-zpr].
- **Hot-carrier breakdown above about 500 °C** — the high-field-by-high-temperature
  distribution-tail correction needs per-material Boltzmann or Monte-Carlo anchor data
  that **do not exist in the V1 corpus**. Until they do, the learned correction ships as
  identity and the corner is **cert-refused** ([coupling-structure],
  [cert-obligations#composition-refusals]) rather than claimed as a met target.
- **Plasmon-phonon coupling and Lyddane-Sachs-Teller breakdown at degenerate doping** —
  above roughly `10²⁰ cm⁻³`, which heavily boron-doped diamond contact layers reach, the
  static permittivity derived through that relation and Fröhlich screening both lose
  validity. V1 **applicability-gates** the derived-permittivity path and Fröhlich
  screening on `n < n_degenerate(host)`; outside the gate the quantity is masked, not
  silently extrapolated. The same gate carries the degenerate-Einstein refinement
  ([multiscale-state]).
- **III-nitride high-temperature thermal expansion** — quasi-harmonic validity is
  **per-material and does not follow a Debye-temperature-scaled rule** ([traps], which
  names this page as its enforcement site): diamond holds through about 800 °C, while
  gallium nitride and aluminum nitride both fail by about 500 °C, which is the design
  point. V1 has **no design-grade path**, only the per-material widened uncertainty in
  [accuracy-ledger#observable-regimes]. This propagates into the gap's temperature
  dependence through the strain path, into the shear modulus, and into the
  temperature-pressure hull for the flagship polar materials. V2 is a first-order
  self-consistent-phonon correction as a second `one-shot-dressing`.
- **Alloy-disorder mobility in aluminum-gallium-nitride beyond the closed-form Harrison
  term** — the `is-alloy`-gated row 127 ships in V1; a full configurationally-averaged
  disorder treatment is V2.
- **Measured avalanche and p-type transport in pure aluminum nitride, and
  measurement-grade high-temperature conductivity for it.** V1 **cert-refuses**
  measured-avalanche and p-type claims for this material and flags its high-temperature
  conductivity as theory-only. What is missing, and with what uncertainty, is
  [accuracy-ledger#residue]; the stance is here.
- **β-Ga₂O₃ hole transport — cert-refused, never seeded.** The valence bands are flat and
  holes self-trap as small polarons, so there is no band-like p-transport to model: a
  hole mobility, a hole impact-ionization coefficient, or a Caughey-Thomas hole quartet
  for this material would be an invented number rather than a missing one. The ~3.5 eV
  ultraviolet luminescence is free-electron to self-trapped-hole recombination and
  **not** a band-edge transition, and must not be read as one. **The refusal is the
  correct output.**
- **Absolute Berry-phase and Wannier-center polarization** — the path-integral evaluator
  for spontaneous polarization is deferred to V2. V1 uses the Born-charge composition
  path (registry rows 113–114, ±5%, [accuracy-ledger#polarization-coefficients]); the
  absolute modern-theory integral needs a Berry-phase sub-stage that is not in the closed
  twelve-method alphabet, analogous to the quasi-particle gap upgrade over the
  semi-local functional.
- **Plasma-process surface damage; grain-boundary statistics; continuum creep and
  dislocation climb; quantum-tunneling-corrected reaction rates** — classical
  transition-state theory is adequate at an operating temperature of 600 K and above.
- **Total-ionizing-dose radiation effects** — oxide trapped charge and interface-trap
  buildup in gate dielectrics under ionizing flux. Displacement damage (registry rows
  111–112) is in scope; total ionizing dose is predominantly amorphous-oxide physics and
  is deferred with the dielectric wave, coupling to the amorphous-film entry below.
- **Single-event effects and upsets** — transient upsets from single-particle strikes.
  These belong to a digital-circuit layer above the oracle library.
- **Hexagonal boron nitride as a host material** — it appears in research anchor sets
  only, and the layered-material machinery it needs is not in the V1 scope list
  ([purpose-and-scope]): direction-dependent moduli, which the bulk-modulus classifier
  already special-cases, a borderline-polar in-plane response, and a van-der-Waals
  interlayer channel. Decide it in only if a two-dimensional-substrate use case
  materializes.
- **Amorphous atomic-layer-deposited gate films** — the oracle library models the
  *crystalline* polymorphs, α-alumina, monoclinic hafnia and aluminum nitride as a
  dielectric. As-deposited amorphous films have no `PeriodicityStructure` and are out of
  scope as hosts. Their *crystallization* — the driver of the leakage spike above about
  700 °C — **is** in scope, as the slow-tier Johnson-Mehl-Avrami-Kolmogorov row 131, and
  the dielectric compact-model rows 129 and 130 apply to the film as a parameterized
  layer rather than as a resolved crystal.
- **General dopant redistribution** — row 106's drift-diffusion shape instantiates per
  species, and V1 carries hydrogen, the corpus's named silent killer. Other dopants are
  per-material wave instantiations of the same row, not new physics.
- **True renormalization-group flow; inverse design and minimal-model search**, which
  would live in the operator library as a prediction head rather than as an oracle
  primitive; **fragile topology.**

## How a refusal is raised

`predict` raises `out-of-scope` with a witness for any of the above. Cert obligation 3
flags suspect cases ([cert-obligations#the-ten-obligations]).

A refusal is not a failure of the library. Where the anchor data to check a claim do not
exist, the refusal *is* the honest output, and the alternative — a number carried because
something has to be returned — is the failure mode every entry above exists to prevent.
