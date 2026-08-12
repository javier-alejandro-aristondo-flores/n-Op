---
id: mvp-system
title: "The MVP system"
owns:
  - diamond primitive cell
  - MVP anchor consequences
  - diamond high-temperature failure mode
anchors:
  the-cell: "The cell"
  consequences: "What each anchor forces"
  high-t-failure: "High-temperature failure"
depends-on:
  - purpose-and-scope
  - capability-slices
  - reference-battery
  - accuracy-ledger
  - named-formulas
  - multiscale-state
  - applicability-classifiers
  - conventions
open-questions: []
---
# The MVP system

Diamond is the MVP material ([purpose-and-scope#mvp]). This page states the cell, and
what each measured anchor **forces** on the build. The anchor values themselves are
seeded reference data and live in [reference-battery#contents]; the tolerances they
must be met to are [accuracy-ledger#mvp-targets]. Nothing here restates a number that
those two own.

## The cell

Diamond, primitive cell. Space group Fd-3m (No. 227); two carbon atoms at the 8a
Wyckoff site; sp³ bonding. Eight valence electrons (2s²2p², twice) give **four
occupied bands** — the count the electronic-structure slice is sized against.

The lattice constant, the indirect gap, the maximum phonon energy, the Debye
temperature, the thermal conductivity and the elastic constants are the diamond
battery anchors ([reference-battery#contents]).

## What each anchor forces

| Anchor | What it forces on the MVP |
|---|---|
| Indirect gap | The conduction-band minimum sits on Δ at about 0.76 of the way from Γ to X — **not** at X. The six-fold Δ valley degeneracy is what the effective-mass and transport rows consume. A semi-local functional underestimates the gap by about 23%, so **G₀W₀ or a hybrid functional is required** (registry row 6). |
| Maximum phonon energy | The highest of any solid; the phonon grid must resolve it. |
| Debye temperature | The quasi-harmonic approximation stays valid through about 800 °C, so self-consistent phonon theory (registry row 13) defers out of the MVP. |
| Thermal conductivity | The headline target of the heat-diffusion slice. |
| Elastic constants | Feed the structure slice's stability criteria and the isotropic sound velocity. |
| Polarity | Diamond is **non-polar (homopolar)**, so the Born effective charge vanishes by symmetry: no LO–TO splitting and no Fröhlich coupling. The polar transport rows are excluded by applicability rather than deferred by choice ([applicability-classifiers#polar-predicate-split]); which rows those are is [capability-slices#carrier-diffusion]. |

Each row is a design decision derived from a measurement, not a restatement of one.
Read with [named-formulas#row-bands] for what a registry row number denotes.

## High-temperature failure

**Air-oxidation onset at about 600–700 °C is diamond's actual lifetime limiter.**
Graphitization — sp³ collapsing to sp² — sets in only above about 1500 °C in vacuum,
so it is not the operating constraint the harsh-environment target runs into first.

Two consequences: the diamond–graphite phase boundary is the structure slice's
thermodynamic check ([capability-slices#structure-prediction]), and oxidation is the
slow-tier degradation channel ([multiscale-state#slow-kinetics]).

Units — internal and reported — follow the corpus convention ([conventions]).
