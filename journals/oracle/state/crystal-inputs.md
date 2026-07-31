---
id: crystal-inputs
title: "Crystal inputs"
owns:
  - top-level inputs
  - periodicity structure
  - site decoration
  - Environment record schema
  - structural and swept Environment partition
anchors:
  top-level-inputs: "The three inputs"
  periodicity-structure: "The periodicity structure"
  site-decoration: "The site decoration"
  environment: "The environment record"
  structural-swept: "Structural fields and swept fields"
  not-inputs: "What is not an input"
  crystal-type: "The Crystal type"
depends-on:
  - unified-state
  - multiscale-state
  - applicability-classifiers
  - compose-time-pipeline
  - product
open-questions:
  - id: environment-schema
    anchor: environment
    summary: "The environment record's field set is not closed and only its five harsh-environment fields carry a declared type and unit. The rest are prose nouns, and the record has no schema version, so adding a field silently changes which formulas apply to every existing composition."
  - id: environment-structural-partition
    anchor: structural-swept
    summary: "Which environment fields are structural and which are swept is stated for temperature alone. The structural subset keys the kernel cache, so a structural field misfiled as swept silently reuses a kernel outside its envelope."
  - id: crystal-type
    anchor: crystal-type
    summary: "The applicability signature on every registry row, every coupling channel, every residual generator and every property template is a function of a Crystal and an Environment. Crystal is defined nowhere. The pairing with Environment implies it is the periodicity structure and site decoration together, but nothing states it."
---
# Crystal inputs

## The three inputs

Three physically orthogonal inputs fully specify **what crystal, in what conditions**:

1. `PeriodicityStructure` — the spatial skeleton.
2. `SiteDecoration` — the per-position content.
3. `Environment` — the external conditions.

The alphabet is exactly three wide, and the closure rules below are what keep it that wide.

## The periodicity structure

`PeriodicityStructure` is the geometry of repetition: dimensionality `d ∈ {0,1,2,3}`, lattice
vectors `{a_i}`, periodicity flags, the Bravais lattice and space group, and the cell vectors
`h`.

The cell vectors are also the first slot of the micro state ([unified-state#slots]): the input
supplies the reference cell, and the state carries it as a degree of freedom.

## The site decoration

`SiteDecoration` is the per-position content: which species sit at which Wyckoff positions; the
orbital basis; optional spin, charge state and occupancy; and a tag drawn from `host`, `defect`,
`adsorbate`, `substrate`, `impurity`.

**Defects, surfaces, adsorbates, magnetic configurations, charged systems and alloys are special
cases of `SiteDecoration`, not new top-level types.** This is the closure rule that keeps the
input alphabet at three. A new physical situation is a new decoration, never a fourth input.

`SiteDecoration.occupancy` is static here. Its dynamic promotion — the slow-state fiber whose
initial condition it becomes — belongs to [multiscale-state#slow-state-schema].

## The environment record

`Environment` is the external-conditions record. It is a parameter of every applicability
predicate, of the compiled kernel's validity stamp, and of the oracle-file's evaluation call, so
its field set is a public interface rather than an implementation detail.

| Field | Type and unit | Notes |
|---|---|---|
| `temperature` | `UNSEEDED` | the one field the corpus fixes as swept |
| `pressure` | `UNSEEDED` | carried as pressure or as volume |
| `chemical_potentials` | `UNSEEDED` | per element; the hydrogen and oxygen potentials are functions of temperature and pressure |
| `applied_electric_field` | `UNSEEDED` | vector |
| `applied_magnetic_field` | `UNSEEDED` | vector |
| `applied_stress` | `UNSEEDED` | tensor |
| `temperature_gradient` | `UNSEEDED` | vector |
| `carrier_injection` | `UNSEEDED` | injection conditions |
| `radiation_flux` | `ParticleFlux` (cm⁻²s⁻¹) | read by the displacement and Frenkel-pair formulas |
| `radiation_dose` | `Fluence` (cm⁻²) | read by the Frenkel-pair yield |
| `displacement_threshold` | `Energy` (eV), per host | read by the displacement count |
| `vibration_spectrum` | `PSD`, amplitude against frequency over 100 Hz – 10 kHz | read by vibration-induced vacancy generation |
| `p_O2` | `Pressure` (Pa) | a specialisation of the pressure slot, not an independent field |

Only the last five fields carry a declared type and unit anywhere in the corpus. The first eight
are recoverable as *names* — they are used in signatures and in prose across the corpus — but
their types and units are stated nowhere, which is why they read `UNSEEDED` rather than
carrying a plausible guess.

**An absent field and a field present at zero are distinguishable.** Presence of a field is what
fires an applicability predicate — the predicates are first-order decidable on field presence
alone — so the schema must admit an unset state that is not a zero value. A composition with no
`radiation_flux` field is a composition the irradiation formulas do not apply to; a composition
with `radiation_flux = 0` is one they apply to and evaluate to zero. Those are different
compositions and they must not compile to the same kernel.

**The field set must therefore be closed and versioned.** Adding a field changes which formulas
apply to every existing composition, silently, because every applicability predicate reads
presence. The extension rule is a `schema_version` bump, as for the defect-species universe
([multiscale-state#defect-species]).

## Structural fields and swept fields

Every environment field is either **structural** or **swept**, and the partition is what makes
kernel caching sound.

- A **structural** field participates in the composition fingerprint that keys the kernel cache
  ([compose-time-pipeline#boundary]). Changing it triggers a recompile.
- A **swept** field is passed as a runtime input and is not baked into the kernel. What follows
  for a validity window over such a field — per-sample re-evaluation, and which windows that
  covers — is [applicability-classifiers#swept-environment-windows].

Each emitted kernel is stamped with its **environment box** — the per-swept-field range set on
which its invariant-synthesis structure is valid. A sample whose swept scalar leaves the box is
masked out, or trips the relevant certification obligation, rather than being scored against a
kernel that does not cover it ([product#environment-input]).

**Misfiling is silent and it is the reason this partition is load-bearing.** A structural field
recorded as swept is passed at runtime into a kernel whose compile-time structure never accounted
for it, so the kernel is reused outside its envelope and nothing fires. The failure has no
symptom at the seam; it shows up only as a wrong number.

`temperature` is swept: the corpus fixes it as a runtime-swept scalar. The rest of the partition
is unstated. `applied_stress` and
`applied_magnetic_field` are the hard cases in either direction, because both can change the
symmetry that the symmetry-quotient stage builds its structure on, which is a compile-time
property rather than a runtime one.

## What is not an input

`Reference` and `Property` are **not** top-level inputs.

`Reference` is a bag of `(Crystal, Environment, weight)` baselines. It composes from the three
inputs above and belongs to the certification layer.

`Property` is an output request — a parameter of the oracle-file's `Validate` call
([product#call-contract]) — not a description of the system being asked about.

## The Crystal type

`(Crystal, Environment) → Bool` is the applicability signature carried by every registry row,
every coupling channel, every residual generator and every property template. It is also the
shape of the `Reference` baseline above.

**`Crystal` is not defined.** It is used across the corpus and introduced nowhere. Two readings
fit every use site: `Crystal` is the pair `(PeriodicityStructure, SiteDecoration)`, or it is the
full triple including `Environment`. The pairing with a separate `Environment` argument at every
call site favours the first, since the second would make the signature redundant in its own
second argument — but that is an inference from call sites, not a statement, and the type stays
open until one is written down here.
