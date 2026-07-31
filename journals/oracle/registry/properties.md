---
id: properties
title: "Target properties"
owns:
  - target property scope
  - property catalogue
  - property category to bundle map
  - scope versus inventory precedence
anchors:
  scope-vs-inventory: "Scope, not inventory"
  catalogue: "The catalogue"
  bundle-map: "Category to bundle"
  categories: "The nine categories"
depends-on:
  - typed-compositions
  - observable-bundles
  - formula-registry
open-questions:
  - id: magnetic-has-no-bundle
    anchor: bundle-map
    summary: "The magnetic category projects onto no observable bundle: the one-body density matrix is mean-field and the wide-bandgap scope did not force a dedicated bundle, so magnetic properties are in scope with no residual grouping behind them."
---
# Target properties

## Scope, not inventory

This page lists the materials properties n-Op is *targeted at*. The nine
categories define the **target scope** — the buckets any quantity a user might
ask for should fall into — and not the implemented scope.

**They are not a claim that all nine can be computed today.** The manifest is
canonical for what exists ([formula-registry]), and [typed-compositions] carries
the declared gap of composition formulas that are invoked but unregistered.
Several entries below are targets rather than rows.

**Read this page as scope and the registry as inventory. Where they disagree, the
registry wins.** A scope list is a statement of intent and can be edited by
deciding something; an inventory is a statement of fact about an artifact, and
editing it requires changing the artifact. Any other precedence rule lets a page
claim a capability into existence.

## The catalogue

One row per targeted property. [typed-compositions#coverage] carries the typed
composition that realises each of them, and that pairing — one row here, one
composition there — is what makes the coverage claim checkable rather than
asserted.

| Category | Property |
|---|---|
| Structural | Lattice parameters |
| Structural | Bond lengths |
| Structural | Crystal structure |
| Structural | Defects |
| Structural | Surfaces |
| Electronic | Band structure |
| Electronic | Density of states |
| Electronic | Band gap |
| Electronic | Charge density |
| Optical | Absorption |
| Optical | Dielectric function |
| Optical | Refractive index |
| Optical | Photoluminescence |
| Mechanical | Elastic constants |
| Mechanical | Bulk modulus |
| Mechanical | Stress–strain response |
| Mechanical | Hardness |
| Thermal | Phonons |
| Thermal | Heat capacity |
| Thermal | Thermal conductivity |
| Thermal | Thermal expansion |
| Magnetic | Magnetic moment |
| Magnetic | Spin density |
| Magnetic | Exchange interactions |
| Transport | Carrier mobility |
| Transport | Ionic diffusion |
| Transport | Conductivity |
| Transport | Migration barriers |
| Thermodynamic | Total energy |
| Thermodynamic | Formation energy |
| Thermodynamic | Phase stability |
| Thermodynamic | Free energy |
| Chemical and surface | Adsorption energy |
| Chemical and surface | Reaction pathways |
| Chemical and surface | Catalytic activity |
| Chemical and surface | Surface energy |

## Category to bundle

Each category projects onto one or more observable bundles
([observable-bundles#the-eleven]). **The authoritative per-formula assignment is
the manifest's `bundle` field**; the table below is a category-level overview and
does not re-define bundle membership or bundle semantics.

| Category | Observable bundles |
|---|---|
| Structural | `static-validity`, `defect-resolved`, `surface-resolved` |
| Electronic | `electronic-structure` |
| Optical | `electronic-structure` — the linear-response and dielectric rows |
| Mechanical | `mechanics` |
| Thermal | `phonon`, `thermodynamics` |
| Magnetic | none |
| Transport | `transport`, `non-equilibrium-operating` |
| Thermodynamic | `thermodynamics` |
| Chemical and surface | `surface-resolved`, `interface-resolved`, `degradation` |

The magnetic row is the clearest instance of the precedence rule above: the
category is in scope and has no bundle behind it, because the one-body density
matrix is treated at mean-field level and the wide-bandgap scope did not force a
dedicated grouping. Stated rather than papered over — a category with no bundle
generates no residuals, and a reader who assumed otherwise would be assuming the
model is trained on something it is not.

## The nine categories

### Structural

The geometric description of a material: the spatial arrangement of atoms and the
resulting unit cell, surfaces and imperfections. Every other property is built on
top of an accurate structure, so errors here propagate everywhere downstream.

### Electronic

How electrons populate the available energy levels and distribute themselves
through the crystal. These quantities decide whether a material is a metal,
semiconductor or insulator, and they feed almost every other category — optical,
magnetic, transport and chemical behaviour all trace back here.

### Optical

How the material responds to light: which photon energies it absorbs, how its
refractive index changes with frequency, and how excited electrons release energy
when they relax. These govern colour, transparency, and any photonic or
optoelectronic application.

### Mechanical

How the material deforms and resists deformation under applied force. These
tensors and scalars describe stiffness, compressibility, and the yielding and
hardness behaviour that determine whether a material survives a given mechanical
environment.

### Thermal

How the lattice's vibrational modes store and transport heat. These set the heat
capacity, the rate at which a material conducts thermal energy, and how it
expands with temperature — all critical for thermal management and
high-temperature operation.

### Magnetic

The configuration and interaction of electron spins. These determine whether a
material is ferromagnetic, antiferromagnetic or paramagnetic, and they control
phenomena from data storage to spintronics.

### Transport

How charge carriers and ions move through the material under external fields or
concentration gradients. These govern electrical conductivity, ionic conduction,
and the activation energies for atomic migration.

### Thermodynamic

The energetic landscape that decides which phases are stable, which are
metastable, and which spontaneously transform. Total and formation energies,
together with free energies, drive phase-diagram construction and any prediction
of synthesizability.

### Chemical and surface

How atoms and molecules bind to a surface and how they rearrange along reaction
pathways. These underlie catalysis, corrosion, and almost every interfacial
process where the material interacts chemically with its environment.
