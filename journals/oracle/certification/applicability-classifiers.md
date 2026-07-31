---
id: applicability-classifiers
title: "Applicability classifiers"
owns:
  - applicability predicate contract
  - polar predicate split
  - swept-environment validity windows
  - applicability predicate storage
  - always-true applicability stubs
anchors:
  the-predicate-contract: "The predicate contract"
  polar-predicate-split: "The two polar predicates"
  trap-density-gates: "What gates trap density and subthreshold swing"
  example-predicates: "Standard predicates"
  v1-commitment: "The V1 commitment"
  swept-environment-windows: "Swept-environment validity windows"
  predicate-storage: "How a predicate is stored"
depends-on:
  - cert-obligations
  - typeclass-alphabet
  - coupling-structure
  - representation-substrate
  - multiscale-state
  - pino-bridge
  - traps
open-questions:
  - id: semiconductor-interface-predicate
    anchor: trap-density-gates
    summary: "Interface trap density needs a semiconductor-interface applicability predicate, and the classifier vocabulary carries none broad enough. `has-metal-semiconductor-interface` is too narrow, because traps sit at semiconductor-dielectric interfaces as well. Until one is defined, the trap-density row carries an always-true stub. Naming the gap rather than inventing a classifier is the deliberate choice here: a dangling pointer is safer than a plausible reconstruction."
  - id: soft-applicability-classifiers
    anchor: v1-commitment
    summary: "Applicability is Boolean in V1. Two extensions are deferred and unscoped: soft classifiers valued in [0,1], and the composition rule for classifiers under perturbation — what a composed predicate should return when one input crystal is a perturbation of another that the predicate accepts."
---
# Applicability classifiers

## The predicate contract

Every property, observable and residual carries a typed predicate

```
applicability : (Crystal, Environment) → Bool
```

The physics-informed loss masks out non-applicable properties per sample, so the model
is neither falsely supervised — predicting a band gap for a metal — nor penalized for a
quantity that is undefined rather than zero.

**This is what makes the architecture compositional across crystal types.** One
interface accepts diamond, gallium nitride, aluminium nitride, cubic boron nitride and
refractory metals, and each property's classifier decides whether it is a meaningful
question for that crystal.

`CouplingChannel.applicability` ([coupling-structure]) uses the same contract: a
first-order decidable function on typeclass tags. A channel whose predicate returns false
is skipped at invariant synthesis and contributes no invariants to the composition.

## The two polar predicates

"Polar" conflates two independent crystal properties, and the registry gates on each
separately.

- **`is-polar-material`** — nonzero Born effective charges, equivalently a
  longitudinal-transverse optical splitting. Gates the **Fröhlich and polar-optical
  phonon paths**: the long-range static electron-phonon channels, the
  polar-optical-limited saturation velocity, and the relative permittivity derived
  through the Lyddane-Sachs-Teller relation. It is a property of the *bonds*, not of the
  point group.
- **`is-noncentrosymmetric`** — the piezoelectric crystal classes, those with no
  inversion centre. Gates the **polarization package**: spontaneous polarization,
  piezoelectric tensors, the two-dimensional-electron-gas sheet density, and
  pyroelectricity.

The two coincide on the corpus's anchor materials — diamond, where both are false, and
wurtzite III-nitrides, where both are true — and **split on β-Ga₂O₃**, which is
centrosymmetric in `C2/m`, so it has no spontaneous polarization, no piezoelectricity and
no pyroelectricity, and is at the same time strongly polar-phonon, with a multi-mode
Fröhlich interaction that is its dominant mobility limiter.

Each wrong gating fails in its own direction. Gating the polarization package on the
Fröhlich-sense predicate would wrongly *activate* spontaneous polarization for β-Ga₂O₃;
gating Fröhlich on the piezoelectric-sense predicate would wrongly *deactivate* that
material's dominant scattering channel.

## What gates trap density and subthreshold swing

Two registry rows sit numerically inside the polarization band and are not polarization
physics. `interface-trap-density` (row 116) computes `D_it(E)` from dangling-bond
density, trap cross-section and strain mismatch; `subthreshold-swing-Dit` (row 119)
computes the metal-oxide-semiconductor subthreshold swing from `D_it`, the oxide
capacitance and the depletion capacitance. Neither depends on inversion-symmetry
breaking, so **neither is gated on `is-noncentrosymmetric`** — that gate would refuse
trap density and subthreshold swing for every centrosymmetric host, diamond and β-Ga₂O₃
among them, and it would be circular, because row 115 consumes `D_it` and so trap
density would exist only where the polarization-induced electron gas already did.

- **Row 119** is gated on `is-dielectric-layer`, the same predicate the gate-dielectric
  rows carry. Subthreshold swing needs an oxide capacitance, and without a dielectric
  there is no `C_ox`.
- **Row 116** needs a *semiconductor-interface* predicate that the classifier vocabulary
  does not carry. It runs on an always-true stub, which the V1 commitment permits, and
  the missing predicate is the open question `semiconductor-interface-predicate` rather
  than a classifier written to fill the hole. Naming a gap instead of reconstructing one
  is [traps]'s rule.

## Standard predicates

Illustrative. Every registry entry carries its own field; this is the collected
vocabulary those fields draw on.

| Property | Applicability predicate | Notes |
|---|---|---|
| Band gap | `is-insulator-or-semiconductor(Crystal)` | Metals have no gap; the quantity is undefined, not zero |
| Magnetic moment per site | `has-magnetic-order(Crystal)` | Non-magnetic systems have zero or fluctuating moments, not an observable |
| Schottky barrier height | `has-metal-semiconductor-interface(Crystal)` | Meaningful only for heterostructures with an adjacent metal and semiconductor |
| Defect formation energy for species X | `defect-species-meaningful(X, Crystal)` | A boron substitutional in copper is not the defect it is in diamond |
| Superconducting `T_c` | `is-superconductor(Crystal)` | A finite predicted `T_c` for most materials is wrong, not noisy |
| Polar-optical (Fröhlich) scattering | `is-polar-material(Crystal)` | Nonzero Born charges and optical-mode splitting — a bond property, not a point group. False for diamond; **true for centrosymmetric β-Ga₂O₃**, where it is the dominant mobility limiter |
| Polarization package — spontaneous polarization, `e_ij`, sheet density, pyroelectricity | `is-noncentrosymmetric(Crystal)` | Piezoelectric classes, no inversion centre. True for wurtzite III-nitrides; **false for β-Ga₂O₃ (`C2/m`) and diamond**. Independent of `is-polar-material` |
| Interface trap density `D_it` (row 116) | *(interface predicate — not in the vocabulary)* | Dangling bonds plus strain mismatch. **Not** point-group gated; applies to diamond and β-Ga₂O₃. Always-true stub |
| Subthreshold swing (row 119) | `is-dielectric-layer(Crystal)` | Needs a gate-oxide capacitance, not an inversion-symmetry property |
| Carbide formation rate at an interface | `interface-includes-carbide-former(Crystal)` | Platinum on diamond never forms a carbide; titanium on diamond does |
| Bulk modulus (scalar) | `is-three-dimensional-solid(Crystal)` | Layered materials have direction-dependent moduli; the scalar is ill-defined |
| Carrier mobility | `is-conductor-or-semiconductor(Crystal)` | Wide-gap insulators at low temperature have effectively zero free carriers |
| Thermal expansion (isotropic scalar) | `has-cubic-or-isotropic-symmetry(Crystal)` | Anisotropic crystals need the tensor form; the scalar is wrong |

## The V1 commitment

**Every registry entry gets an explicit `applicability` field.** Always-true stubs are
acceptable for V1.0 and are refined incrementally — an explicit stub is a claim a reader
can find and a checker can count, which an absent field is not.

## Swept-environment validity windows

A predicate or formula *validity window* that depends on a **runtime-swept**
`Environment` scalar — temperature, through the quasi-harmonic window, the regime
windows of [multiscale-state], the `ω² ≥ 0` claimed-stable gate, the impact-ionization
field domain, and the four-phonon window at `T ≳ 0.4 Θ_D` — is **re-evaluated per
training sample** in the loss mask, and not once against the composition's nominal
`(Crystal, Environment)`.

The per-sample mask path already exists ([pino-bridge]). Compose-time structure decisions
are frozen at invariant synthesis, but the *mask* over them is a runtime read of the
swept scalar.

To make that checkable, **each emitted kernel is tagged with the `Environment` box** —
the scalar ranges on which its compose-time structure is valid. A sample whose swept
scalar leaves that box is masked out, and for a cert query trips the relevant obligation,
rather than being silently scored against a stale kernel.

## How a predicate is stored

An applicability predicate is a `MerkleDAG[PredicateOps, Atom]` root in the substrate's
sense ([representation-substrate]): a reduced ordered Boolean DAG over typed
parameterized atoms drawn from the typeclass-tag vocabularies ([typeclass-alphabet]).

The atom order is part of the predicate-vocabulary version. Adding a new atom creates a
new order id and forces explicit re-canonicalization of stored predicate roots, rather
than silent reinterpretation of the roots already stored.

**Cert obligation checkers are not Boolean DAGs over typeclass-tag atoms.** They are
typed registered morphisms from GENERIC artifacts to evidence, registered through the
generator-registry machinery ([representation-substrate]), and
[cert-obligations#the-ten-obligations] is their list. The two mechanisms both take
typeclass tags as input and are otherwise unrelated; keeping the split explicit is what
stops a predicate from being mistaken for an obligation.
