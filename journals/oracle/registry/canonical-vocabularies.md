---
id: canonical-vocabularies
title: "Theory-context vocabularies"
owns:
  - theory-context vocabularies
  - atomic species universe
  - closed-vocabulary versioning
anchors:
  theory-context: "The ten vocabularies"
  versioning: "Adding a member is a version bump"
  atomic-species: "Atomic species"
  scope: "What these vocabularies do not decide"
depends-on:
  - coupling-structure
  - representation-substrate
  - property-templates
  - formula-registry
  - cert-obligations
  - multiscale-state
  - purpose-and-scope
  - agent-contract
open-questions: []
---
# Theory-context vocabularies

## The ten vocabularies

A `TheoryContext` is the global theory frame a coupling specification is
interpreted in — the answer to *"computed at what level of theory?"* for a
whole composition at once. [coupling-structure#theory-context-placement] owns
the record and its four axes; this page owns the ten closed vocabularies those
axes are built from.

They are a genuinely separate axis, not a restatement of one the corpus already
has. The nearest neighbour is the dressing-method selector inside
`SelfConsistentRenormalizationOf` ([property-templates#signatures]), which
chooses self-consistent phonons, GW, an iterated Bethe–Salpeter solve or a
polaron treatment — but that is a *per-observable* choice about how one quantity
is dressed, while a theory context is *composition-global* and fixes the frame
every observable in the composition is read in. Merging the two axes makes it
impossible to record that two observables were dressed differently within one
frame, which is the normal case.

| Vocabulary | Members | Notes |
|---|---|---|
| `XCFunctionalTag` | `LDA(·) \| GGA(·) \| MetaGGA(·) \| Hybrid(flavour, exx_fraction, screening_omega?)` | exchange–correlation functional; a hybrid carries its exact-exchange fraction in the payload |
| `PPType` | `NormConserving \| Ultrasoft \| PAW` | pseudopotential construction kind |
| `PPSourceTag` | `PseudoDojo(version) \| SSSP(version, accuracy) \| GBRV(version) \| VASP_PAW(set) \| Custom(DOI?)` | the table version string is an open key, content-pinned by an optional file digest |
| `ManyBodyLevel` | `KohnSham \| KohnShamPlusU(HubbardParams) \| GW(GWScheme) \| DMFT(DMFTParams)` | the discriminator is closed; the Hubbard and dynamical-mean-field arms carry sub-records |
| `GWScheme` | `G0W0 \| GW0 \| scGW \| QSGW` | |
| `DoubleCountingTag` | `FLL \| AMF \| Dudarev` | double counting for Hubbard corrections and dynamical mean field |
| `ImpuritySolverTag` | `CTQMC \| ED \| NRG \| IPT` | impurity solver for dynamical mean field |
| `OrbitalBasisTag` | `Wannier \| PAW \| Lowdin` | the projection basis for Hubbard corrections; also closes the gauge-choice ambiguity for downfolded channels |
| `RelativisticTreatment` | `NonRelativistic \| ScalarRelativistic \| FullRelativistic(SOCScheme)` | |
| `SOCScheme` | `DiracPAW \| TwoComponentZORA \| SecondVariational \| PerturbativeSOC` | spin–orbit coupling scheme |

**A hybrid functional is always recorded as `XCFunctionalTag.Hybrid` together
with `ManyBodyLevel.KohnSham`.** "Hybrid" is not a member of `ManyBodyLevel`:
recording the same physical choice on two axes would make two different records
denote one calculation, and the address a theory context hashes to would stop
being canonical. `make-theory-context` normalizes this on construction
([coupling-structure#couplingspec]).

## Adding a member is a version bump

Each of the ten is a `Universe` instance with a closed carrier and dense
unsigned ordinals ([representation-substrate#primitives]). A downstream record
stores the ordinal, not the name.

**Adding a member is a versioned schema bump, not an open-registry append** —
because it changes the meaning of every coefficient already recorded against that
universe. Under dense ordinals a new member either shifts existing ordinals or
occupies a slot that older records may have meant differently; either way the
stored coefficients silently re-bind. A version bump is what makes the re-binding
visible.

## Atomic species

`AtomicSpecies` is the ordinary closed vocabulary of the elements, and it is the
key universe of the pseudopotential set. Its membership is
`{C, B, N, Al, Ga, O, H}`.

Oxygen and hydrogen are there because committed content requires them, not
because of anticipated scope: β-Ga₂O₃ is a host material
([purpose-and-scope#material-scope]) and a defect host
([multiscale-state#defect-species]); the oxygen-bearing defects `O_N`,
`V_Al–O`, `V_Ga–O_N` and `V_O–H` decorate the nitride and oxide hosts; and the
seeded slow-tier rows read hydrogen (rows 106 and 110) and oxygen through the
oxygen partial pressure (row 109).

Silicon and the contact-metal species enter with their material waves, under the
version bump above.

## What these vocabularies do not decide

They condition the **interpretation and verification** of coefficients. They
never condition the **enumeration** of the symmetry-invariant basis: which
invariants exist is a property of the crystal symmetry group, and a change of
functional cannot add or remove one.

That boundary is why they touch exactly four certification obligations —
reference battery, named-formula consistency, reference versioning, and
surrogate validity — and none of the others
([cert-obligations#the-ten-obligations]). Every obligation they touch is one
about whether a number may be compared to another number; none is about what
the composition contains.

Counts over the registry are the manifest's ([formula-registry#counts]); the
per-page ownership of any other vocabulary in this corpus is answered by the
emitted topic map rather than restated here ([agent-contract#placement]).
