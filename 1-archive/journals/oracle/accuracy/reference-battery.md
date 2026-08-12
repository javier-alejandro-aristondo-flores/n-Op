---
id: reference-battery
title: "The reference battery"
owns:
  - reference-row schema
  - uncertainty encodings
  - reference-data contents
  - battery seeding waves
  - reference archive format
  - reference-calculation invariant checks
anchors:
  purpose: "Purpose"
  contents: "What the reference data holds"
  row-schema: "The row schema"
  invariant-checks: "Invariant checks on a computed row"
  why-csv: "Why CSV"
  wave-programme: "The remaining waves"
  boundaries: "What this is not"
depends-on:
  - cert-obligations
  - accuracy-ledger
  - crystal-inputs
  - coupling-structure
  - traps
open-questions: []
---
# The reference battery

## Purpose

[reference-data] holds the **machine-readable reference data** that
cert obligation 8 reads ([cert-obligations#the-ten-obligations]). It is the canonical
source of truth for one question — *what does the literature say about this quantity?* —
and it is what the oracle's predictions and computed values are checked against.

Its `Source` column is **canonical for per-value citations**. Where a `Source` cell names
no literature, [accuracy-ledger#seed-provenance] states what the row actually rests on.

## What the reference data holds

Five files, 179 rows. One file per sub-area, each row typed, with explicit provenance,
canonical units and an uncertainty band.

| File | Rows | Holds |
|---|---|---|
| `material-constants.csv` | 43 | band gaps direct, indirect and effective; Varshni parameters; effective masses; static and optical permittivities; gap deformation potentials; zero-point renormalizations; lattice constant; cohesive and formation energies; absorption onsets; crystal-field splitting; displacement threshold |
| `elastic-tensors.csv` | 38 | elastic constants; bulk moduli; mass densities; the monoclinic cell parameters and angle; the alloy interpolation rule |
| `phonon-frequencies.csv` | 18 | transverse and longitudinal optical mode energies; Debye temperatures; mode Grüneisen parameters; maximum phonon energy; the dominant Fröhlich mode |
| `polarization-piezoelectric.csv` | 14 | spontaneous polarization; Born charges; piezoelectric constants, proper and improper; sheet density; pyroelectric coefficients; the alloy bowing row |
| `transport-coefficients.csv` | 66 | mobilities and their Caughey-Thomas parameter sets; saturation and peak velocities; Fröhlich coupling; alloy disorder potential; thermal conductivities; critical breakdown fields; impact-ionization coefficients |

**Three sub-areas have no file yet**: interface properties — Schottky barriers, work
functions and carbide-formation energies per metal-semiconductor pair; defect formation
energies per host, species and charge state; and elemental chemical potentials at
standard conditions. Nothing reads them, and no row anywhere points into them.

The same directory carries the **cert reference cache**, whose schema, keying and write
discipline are [cert-obligations#reference-cache]. The files above are the canonical
archive; the cache is what obligations 4 and 8 read at check time. **How a row travels
from one to the other is stated nowhere** — that is the open question `csv-to-sqlite-path`
on [cert-obligations].

## The row schema

Every row carries ten fields.

- **Property** — the canonical name from the formula registry.
- **Material** — the formula, with space group or polytype where that is ambiguous.
- **Environment** — the conditions the value was measured or computed under, as a
  serialization of the record [crystal-inputs#environment] owns. It is also the third
  component of the obligation-8 lookup key, so a cell naming something that record cannot
  hold is a row no lookup will ever match.
- **Value** — the numerical value in canonical units.
- **Uncertainty** — the one-sigma band, instrumental or computational. See below.
- **Source** — a DOI, paper title and page reference; or a computational provenance,
  meaning functional, k-mesh and cutoff.
- **Source class** — `experimental`, `dft-pbe`, `dft-hse`, `gw`, `dft-d3` and so on.
- **Version** — the semantic version of this row, incremented on correction.
- **Added** — the date the row first entered.
- **Modified** — the date the row last changed.

**Three uncertainty encodings appear, and a consumer must dispatch on the format.**

| Encoding | Meaning |
|---|---|
| an absolute value in the Value's units, e.g. `7 W/mK` | a one-sigma band on a linear scale |
| a multiplicative factor, written `×N` | a log-scale band — the value is known to within a factor N, so `σ_ln = ln N` |
| `unbounded` | no constraining uncertainty exists; treat as missing |

A bare `—` means the uncertainty is **not yet assigned**, which is a different state from
`unbounded`. Such a row cannot back a `ProvenanceLedger` coefficient until an assignment
pass values it: [coupling-structure] requires a complete `(value, σ, source, cost-class)`
tuple, and [cert-obligations#composition-refusals] refuses any composition carrying an
unprovenanced coefficient.

Remaining `—` cells are exactly the declared `UNSEEDED` rows, the gated alloy-bowing row,
the alloy interpolation rule — a rule rather than a value, and exempt by construction —
and the gallium-nitride breakdown-field slope, whose normalized form is itself declared
`UNSEEDED`.

**Population is incremental and reviewable: every row must be defensible against a
literature citation before it is committed.** Where a row is not,
[accuracy-ledger#seed-provenance] names it rather than letting it pass as seeded.

## Invariant checks on a computed row

A row sourced from literature is defensible against its citation. **A row whose `Source`
is a computational provenance has no citation to be defensible against** — and these
checks are what defensibility means for it. Each is a closed form that any correct
calculation already satisfies, and each follows from a conservation law.

| Written | Read as | Holds because |
|---|---|---|
| `Σ_I f_I = 0` | forces summed over ions vanish | translational invariance |
| `σ_ij = σ_ji` | the stress tensor is symmetric | conservation of angular momentum |
| `Σ_nk w_k f_nk = NELECT` | occupations, weighted over bands and k-points, sum to the electron count | electrons are conserved |
| `det(A) = V` | the lattice-matrix determinant equals the reported volume | arithmetic |
| spin parity | an odd electron count forces an odd integer magnetization | you cannot pair every electron |

Closed form, one pass per frame, and **no anchor is required** — the calculation is
checked against itself rather than against a curated value.

**They catch parser bugs and run failures together, and both are otherwise invisible**:
the run exits cleanly and the numbers look reasonable. That is what earns them their
place. A value comparison cannot see either failure, because a mis-parsed run produces
plausible numbers that no tolerance will catch — the number is not far from the anchor,
it is a different quantity.

These are not cert obligations, and the distinction is the object rather than the law.
Obligations 1, 2 and 5 check symmetry, positivity and conservation on an **emitted
composition** ([cert-obligations#coupling-derived-checks]); these check an **ingested
calculation** before its numbers ever become a row. Same conservation laws, opposite
ends of the pipeline.

## Why CSV

CSV is the lowest-common-denominator format that survives the open
implementation-language decision. Once that language is fixed, the cert layer may
re-serialize to something more typed — a columnar format, or language-native records —
but **the canonical archive stays CSV, for human auditability.** A reference battery a
person cannot read with no tooling is a reference battery nobody checks.

One consequence is load-bearing and easy to lose: physics notation contains literal `|`,
in bra-kets, norms and determinants. In a delimiter-separated format an unescaped one
splits the row and shifts every cell to its right, and by-name checks keep passing
because the cells they read are non-empty and merely hold the wrong values. That defect
shipped for a month in this data. [traps] carries it as a hazard.

## The remaining waves

Seeding proceeds in waves, and two conditions gate one of them.

- **The second-anchor wave** — cubic boron nitride and 4H silicon carbide, together with
  the three files that do not exist yet.
- **The metals-and-substrates wave** — a *reduced schema*: Fermi level, work function,
  electrical and thermal conductivity against temperature, thermal expansion, and
  electromigration and carbide parameters. Two conditions must be met before it starts.
  **Nickel's Curie point at 627 K sits inside the operating window** and must be decided
  before any metal is seeded. And the **contact-value provenance must be pinned first**:
  Schottky barriers and carbide onsets are contested, so the rule for them is to record
  the range and never pick a point ([traps]).
- **The dielectrics wave** — folding in the dielectric-aging coefficients and the stance
  on total ionizing dose and amorphous films.

## What this is not

- **Not a training dataset.** Training data belongs to the operator library.
- **Not a simulation-result cache.** Computed sweeps live in [strain-sweep], under
  different versioning semantics. A hypersurface generated to exercise an acceptance
  check is not a battery entry however many rows it carries — the battery is curated
  anchors, keyed for lookup, one row per quantity.
- **Not authoritative beyond what its sources support.** It inherits the uncertainties of
  its primary sources, and it inherits their absences too.
