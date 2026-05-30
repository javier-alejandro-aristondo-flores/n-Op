# `reference-data/` — Machine-Readable Cert Reference Battery

## Purpose

This directory holds the **machine-readable reference data** that cert obligation-8 (`reference-battery-versioned`) reads from. It is the canonical source-of-truth for "what does the literature say about this quantity?" — used to validate that `/physics`'s predictions, computed values, and reference outputs agree with established theory and experiment.

## Contents (populated incrementally)

Each sub-area below holds typed records with explicit provenance (DOI / source URL), units, and uncertainty bands. Format is one CSV (or JSON) per sub-area; the cert layer reads them at obligation-check time.

```
reference-data/
├── README.md                          (this file)
├── defect-formation-energies.csv      (per host × defect species × charge state)
├── material-constants.csv             (lattice constants, gaps, dielectrics per material)
├── interface-properties.csv           (Schottky barriers, work functions, carbide-formation E_a per metal-semiconductor pair)
├── elastic-tensors.csv                (C_ij components for each anchor material)
├── phonon-frequencies.csv             (key LO/TO modes, Debye temperatures)
├── transport-coefficients.csv         (mobilities, breakdown fields, thermal conductivities at reference T)
└── chemical-potentials.csv            (μ_elemental references at standard conditions)
```

## Schema discipline

Every row carries:

- **Property** — canonical name from the formula registry
- **Material** — IUPAC formula plus space group / polytype where ambiguous
- **Environment** — temperature, pressure, applied field as applicable
- **Value** — numerical value in canonical units
- **Uncertainty (σ)** — one-sigma uncertainty band (instrumental or computational)
- **Source** — DOI, paper title, page reference; OR computational provenance (DFT functional + k-mesh + cutoff)
- **Source class** — `experimental` / `dft-pbe` / `dft-hse` / `gw` / `dft-d3` / etc.
- **Version** — semantic version of this row (incremented on correction)
- **Added** — date row first entered
- **Modified** — date row last changed

## How cert obligation-8 uses this

For each prediction (or each `/physics`-computed value) that matches an observable in the reference battery:

1. Look up the matching row by (Property, Material, Environment).
2. Compute the residual: `|predicted - reference| / σ_reference`.
3. If residual > tolerance (default 3σ), trip the cert with the numerical witness.
4. Emit cert evidence carrying the reference row's provenance.

## Why CSV (V1)

CSV is the lowest-common-denominator format that survives language-decision uncertainty. Once the implementation language is fixed, the cert layer may re-serialize to a more typed format (Arrow, Parquet, or language-native records) — but the canonical archive stays CSV for human-auditability.

## Initial population sources

The seed dataset will be assembled from:

- The diamond–metal interface table (work functions, Schottky barriers, carbide formation E_a)
- Material-constant anchors (bandgaps, dielectrics, elastic moduli for diamond, c-BN, AlN, GaN, β-Ga₂O₃)
- The defect-formation-energy table (B in diamond, P in diamond, V_C, NV center, V_Ga in GaN, V_O in β-Ga₂O₃)
- High-field anchors (breakdown fields, saturation velocities, Caughey-Thomas exponents per material)

Population is **incremental and reviewable** — every row should be defensible against a literature citation before commit.

## What this is NOT

- Not a training dataset (training data lives elsewhere, possibly in `informed-operator/data/`)
- Not a simulation result cache (simulation results live in their own area with different versioning semantics)
- Not authoritative beyond what its sources support (it inherits the uncertainties of its primary sources, period)
