---
id: arch-03-inputs
title: Inputs
status: draft
revision: 1
canonical-for:
  - top-level inputs
depends-on: []
referenced-by: []
research-sources: []
---
# Inputs

Three physically orthogonal inputs fully specify "what crystal, in what
conditions":

1. **`PeriodicityStructure`** — the spatial skeleton: dimensionality
   `d ∈ {0,1,2,3}`, lattice vectors `{a_i}`, periodicity flags. The geometry of
   repetition (Bravais lattice, space group, cell vectors `h`).
2. **`SiteDecoration`** — the per-position content: which species sit at which
   Wyckoff positions; orbital basis; optional spin, charge state, occupancy, and
   a tag (`host` / `defect` / `adsorbate` / `substrate` / `impurity`). Defects,
   surfaces, adsorbates, magnetic configurations, charged systems, and alloys
   are **special cases of `SiteDecoration`**, not new top-level types.
3. **`Environment`** — external conditions: temperature, pressure (or volume),
   chemical potentials, applied electric/magnetic fields, applied stress,
   temperature gradient, carrier-injection conditions.

`Reference` (a bag of `(Crystal, Environment, weight)` baselines) and `Property`
(the requested observable) are **not** top-level inputs: `Reference` composes
from the three above and belongs to the cert layer; `Property` is an output
request, a parameter of `predict`/`residual`.

---
