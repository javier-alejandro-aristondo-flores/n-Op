# Research log

This is the compliance record for n-Op. It is the **only** place in this repository
where research history is kept. Every page in `journals/` states what is true in the
present tense and says nothing about how it got that way; if an advancement is not
here, it is not recorded anywhere.

This file is not a page. It has no frontmatter and declares no anchors.

## Schema

Every entry carries five fields:

| field | meaning |
|---|---|
| **date** | when the finding was made or the decision taken — not when it landed, where the two differ and both are known |
| **finding or decision** | the advancement itself |
| **Evidence** | where an auditor can check it |
| **Attribution** | who or what produced it |
| **Supersedes** | the claim, value or rule it replaced |

## How to read the markers

- **`MISSING:`** — the field cannot be supplied from any surviving source. The reason
  follows. These are not defects to be tidied away: an entry with a declared gap is
  auditable, an entry with an invented attribution is not. Nothing here has been
  guessed.
- **`EVIDENCE-DIES:`** — the entry's evidence is, or includes, a page that does not
  survive this restructure (`journal/` singular, and the chapter-11 appendix
  derivations). The finding is recorded; the artifact that recorded it will not exist.
  Where the *content* was carried into a surviving page, that page is named too.
- **`PINNED:`** — the source record carried no date, or a partial one, and the date
  shown was recovered from git history. The commit is named so the pin can be checked.
  A pin is a claim about evidence, not an estimate.

Undated entries come first, each carrying whatever bound is known. After them the
record runs forward in time, oldest first, so it can be read as it happened. Four
entries carry a month but no day; each sits at the end of its month, and its heading
says `day MISSING` so it is not mistaken for a precise date.

**Counts, so that they can be checked rather than trusted:** 141 entries · 5 complete on
all five fields · 133 missing an attribution · 14 missing a day or a date · 1 missing
what it superseded · 37 whose evidence dies at cutover · 11 whose date was pinned from
git.

Citations are `[page-id]` or `[page-id#anchor]` and resolve against `journals/`.
Registry rows cite `data/registry-manifest.csv`; seeded coefficients cite
`data/reference-data/`. Literature is cited in full.

---

# Undated

Four entries whose date is not recoverable at all, and six more that carry only an
upper bound. Ordering within this section is by subject, not by time. Five further entries
that reached Phase 1 undated were pinned from git history and appear in the dated run
below, each marked `PINNED`.

### undated · The coupled electrical–thermal residual was filed inside the equation-of-motion category rather than beside it

The coupled electrical–thermal partial-differential-equation residual was placed
inside the equation-of-motion violation category rather than made a sixth top-level
category, on the reasoning that equation-of-motion violation is measured over the
unified state's evolution while the coupled check is measured over the *emergent*
field tuple (electrostatic potential, carrier density, current, temperature). This is
the reasoning that produced the two cross-tier equation-of-motion siblings in the
nineteen-category taxonomy.

- **Evidence** — outcome at [residual-definitions#eom-categories]. EVIDENCE-DIES: the
  reasoning is stated only at `11.5-deriv-high-field:265-281`.
- **Attribution** — the non-equilibrium high-field derivation stream.
- **Supersedes** — the proposal for a top-level coupled-partial-differential-equation
  residual category.

### undated, before 2026-07 · The nineteen-category residual taxonomy descends from the group-C derivation

The group-C derivation proposes exactly four clusters — equations of motion,
conservation, positivity and inequality, algebraic identities — which is the structure
[residual-definitions] now implements as 9 + 3 + 5 + 2.

- **Evidence** — [residual-definitions#categories]; [multiscale-state] cites the same
  section for the shared residual shape. EVIDENCE-DIES: the four-cluster proposal
  itself is at `11.3:665-684` and does not survive.
- **Attribution** — the group-C (transport) derivation stream.
- **Supersedes** — the informal four-cluster grouping.

### undated, before 2026-07 · The three-tier stratified state contract descends from the group-C derivation

Three distinct state schemas sharing a *common* residual contract, resolved into
concrete types.

- **Evidence** — [multiscale-state#three-tier-residual-contract]. EVIDENCE-DIES: the
  originating argument is at `11.3:601-630`.
- **Attribution** — the group-C derivation stream.
- **Supersedes** — the informal kinematic-geometry argument.

### undated · The ±5% polarization-difference result holds by accidental cancellation, not by generic reference-cancellation

The Dreyer ±5%-on-polarization-difference result was established to hold by an
**accidental cancellation** between the spurious zincblende-reference term and the
proper/improper piezoelectric-constant error — large, opposite in sign, nearly
cancelling — and **not** by generic reference-cancellation. Two consequences follow
and are both live: the self-consistent-pairing certificate, and the refusal for
high-indium indium-gallium-nitride on gallium nitride.

- **Evidence** — [accuracy-ledger#polarization-bowing];
  [cert-obligations#composition-refusals]. Literature: Dreyer et al., *Phys. Rev. X*
  **6**, 021038 (2016), §V.D–E.
- **Attribution** — corpus physics audit. MISSING: no pass, agent or person is named
  on the record.
- **Supersedes** — the "generic reference cancellation" reading.

### undated · Exhaustiveness of the tolerance ledger is not machine-checkable, and the failed attempt is recorded rather than retried

`τ` is not a reserved tolerance prefix — 48 correct uses across six pages are physical
times — and narrowing by value shape does not separate a 1e-12 s relaxation time from
a 1e-12 tolerance. Verdict: this is a review rule, and it is labelled as one.

- **Evidence** — [cert-obligations#tolerance-ledger]; [traps#practice].
- **Attribution** — corpus tooling work. MISSING: no agent or person named.
- **Supersedes** — the claim that a symbol prefix denotes a tolerance throughout.

### undated · Adjoint-tape materialization owes no fidelity generator

Recomputing a value and reading a stored one give the same value. This marks the
boundary of the estimate-don't-decide rule: it is about value, not cost.

- **Evidence** — [compose-time-pipeline#stage4-adjoint-tape].
- **Attribution** — corpus. MISSING: no pass named.
- **Supersedes** — nothing.

### undated, before 2026-07-22 · Five corrected physical forms made canonical

Optical absorption as `(2ω/c)·Im(√ε)`; the operator-spectrum-area sum rule carrying
its `2/π` prefactor; the acoustic sum rule summing over all lattice translations; the
magnetic relaxation term as the orientation-preserving `S × (S × H_eff)`; and the
harmonic transition-rate normalization consuming products over modes rather than
spectra.

- **Evidence** — [named-formulas#corrected-forms]; [typed-compositions#optical].
- **Attribution** — physics reconciliation. MISSING: no pass named. Git traces the
  acoustic sum rule's text to `bf26426` (2026-05-29) and earlier, so at least part of
  this predates the corpus's dated record.
- **Supersedes** — the pre-correction form of each of the five.

### undated, before 2026-07-22 · Four inline-math invocations replaced by declared names

This closed a violation of the no-inline-mathematics rule *inside the page that
validates the closed vocabulary*. The expressions are recorded beside the names, which
is what makes registering those four rows transcription rather than research.

- **Evidence** — [typed-compositions#per-observable-compositions];
  [named-formulas#no-inline-math].
- **Attribution** — corpus audit. MISSING: no pass named.
- **Supersedes** — inline mathematics in `formula =` slots.

### undated, before 2026-07-22 · The observable-bundle labels re-canonicalized

The properties page carried a pre-canon scheme in which the eleventh bundle meant
"topology atlas"; canon has it as degradation.

- **Evidence** — [properties#bundle-map]; [observable-bundles#the-eleven].
- **Attribution** — canon consolidation. MISSING: no pass named.
- **Supersedes** — the pre-canon bundle scheme in the properties page.

### undated, before 2026-07-22 · Mesh interpolation registered as a sub-method, preserving the closed twelve-method alphabet

The compile-time band and electron-phonon interpolator — Fourier for gauge-free band
energies and velocities, Wannier interpolation for gauge-sensitive electron-phonon
matrix elements, with mandatory dipole and quadrupole polar corrections; runtime reads
the interpolated grid only, and is first-derivative-clean. Interpolation is a
sub-method, not a new top-level method.

- **Evidence** — [computational-methods#sub-methods]; [canonical-vocabularies].
- **Attribution** — the ultra-wide-bandgap scope extension. MISSING: no pass named.
- **Supersedes** — a proposed thirteenth top-level method.

---

# 2026-05

### 2026-05-27 · Seven research streams integrated, and the registry's provenance vocabulary originates here

Seven concurrent ultra-wide-bandgap research streams were folded into the
specification, together with the ultra-wide-bandgap retargeting amendment and the
applicability-classifier addition. The registry's `Source` column takes its values from
these streams. **Canon never defined that vocabulary anywhere** — a defect that
survived on 132 rows until 2026-07-31.

- **Evidence** — commit `dfad72b`, and `IMPLEMENTATION-PLAN.md:20` at that commit,
  which names each stream; `data/registry-manifest.csv` `Source` column.
- **Attribution** — MISSING: no agent, model or person recorded. Javier is the sole
  human author of the repository.
- **Supersedes** — nothing.

### 2026-05-29 · The specification consolidated into one language-neutral corpus

The documentation set was consolidated into a single coherent specification with no
implementation language assumed. Language-neutrality has been a standing constraint
since; the implementation-language question was subsequently opened, closed on shape,
and reopened on picks (see 2026-06-08 and 2026-07-21).

- **Evidence** — commits `bf26426`, `affd5c2`.
- **Attribution** — MISSING.
- **Supersedes** — the pre-consolidation multi-document tree.

---

# 2026-06

### 2026-06-08 · The implementation-language decision closed on its *shape*: a four-role polyglot

A four-role polyglot of domain-specific languages joined at the codegen seam: a
compiler host owning the compose-time stages and the substrate, emitting source for a
separate runtime host; an offline group-theory engine; an offline proof assistant.
Leading candidates recorded as Haskell, Julia, the GAP computer-algebra system, and
Lean 4.

- **Evidence** — commit `ec52314` ("Close arch-18 §1: implementation-language
  decision"); [forced-decisions#language-roles]. EVIDENCE-DIES: the study itself is
  `11.9-deriv-language-study`. Worse — the study's own per-axis dossiers were written
  under `/tmp/impl-lang-research/` and **no longer exist**, so its internal provenance
  is unrecoverable regardless of what this restructure deletes.
- **Attribution** — a language study: four web-verified first-round axes (compute and
  hardware, substrate type-system fit, compiler and staging fit, in-house dependency
  and build cost), one adversarial audit, one second-round pass. MISSING: no agent,
  model or version named for any of them.
- **Supersedes** — the prior framing of the question as "which numerical ecosystem"
  (Julia vs Python-plus-JAX vs a custom MLIR stack).

### 2026-06-08 · The piezoelectric-acoustic electron-phonon channel added, closing the coupling coverage policy

The second long-range electron-phonon mechanism the wurtzite III-nitride members
carry — a static long-range channel with a `1/q` pole — gated on the
non-centrosymmetry predicate.

- **Evidence** — [coupling-structure#mechanism-range-table]; commit `b65d856`
  ("Coupling-channel coverage policy"). PINNED: the source record carried
  "2026-07-2x"; the text is present in `docs/architecture/19-coupling-structure.md` at
  `b65d856`, 2026-06-08.
- **Attribution** — the coupling coverage-policy wave. MISSING: no agent named.
- **Supersedes** — the fourteen-row template table, which had no piezoelectric-acoustic
  entry.

### 2026-06-08 · The coupling specification promoted from a bare set to a record, with a schema-version bump

From a bare sparse set of coupling-registry entries to a `{channels, theory_context}`
record, with a schema version bumped so that old bare-set addresses cannot collide with
new record addresses. This makes the theory frame part of content-addressed identity
automatically.

- **Evidence** — [coupling-structure#couplingspec]; commit `b65d856`. PINNED: the
  source record carried 2026-07-21; `theory_context` is present in
  `docs/architecture/19-coupling-structure.md` at `b65d856`, 2026-06-08. The later date
  is when the text reached the book, not when the decision was taken.
- **Attribution** — the coupling coverage-policy wave. MISSING: no agent named.
- **Supersedes** — the bare-set coupling specification.

### 2026-06 (day MISSING) · Cross-stream reconciliation of the residual catalog

Cost tiers fixed at four levels (a proposed five-level scheme was rejected: whether a
formula is a machine-learned interatomic potential belongs in its provenance tag, not
its cost tier); observable bundles fixed at eleven, with degradation newly introduced
for time-integrated lifetime residuals; the reference cache unified from two proposals
into one type with two namespaces; roughly 13% deduplication compression, from about
100 raw proposals to 87 entries.

- **Evidence** — landed at [canonical-vocabularies]; [named-formulas#the-registry].
  EVIDENCE-DIES: the reconciliation's own record is `11.8-deriv-generator-catalog`
  §4.1, §4.3, §4.4.
- **Attribution** — the sixth research stream, whose job was reconciling the other
  five. MISSING: no agent named; and the artifact does not identify itself as that
  stream — it is banner-marked as a "historical snapshot" of the streams it
  reconciles.
- **Supersedes** — the five-level cost-tier proposal; the bundle proliferation of two
  earlier streams; the separate reference-phase cache and defect reference battery.

### 2026-06-09 · Founding physics audit

Deep adversarial audit of the whole specification: every atomic file and research
stratum read, the formula registry classified, four skeptic passes run against the
audit's own findings. Three structural gaps found and since closed — the degradation
pipeline, the micro-to-device bridge, and polarization. Also produced the composed
error budget (called out as the highest-leverage single fix), the coefficient
provenance contract and its refusal, the per-tier generator structure for the
dissipative-bracket formalism, and the rule that the documentation-canon discipline
should be mechanized as a check.

- **Evidence** — [multiscale-state], [accuracy-ledger], [coupling-structure],
  [cert-obligations], [generic-dynamics], [conventions]; commits `bbc215f`, `8b3fba9`,
  `68b61cd`.
- **Attribution** — MISSING: "a deep adversarial audit" and "four skeptic passes". No
  person, model or tool version is named anywhere on the record. This gap is shared by
  every audit entry through 2026-07-22.
- **Supersedes** — nothing; this is the first audit of record.

### 2026-06-10 · Re-audit addendum

Fix-verification of the founding audit's remediation, plus a pre-landing physics audit
of the accuracy design. All priority-zero items and all three structural gaps confirmed
resolved; ten further findings, all landed — the Frenkel-pair dimensional defect,
mandatory Scharfetter–Gummel flux discretization, the machine-checkable slope-kind tag,
the learned-correction training contract, the degenerate-Einstein and plasmon-phonon
gates, and the image-force reconciliation.

- **Evidence** — [multiscale-state], [coupling-structure], [cert-obligations],
  [out-of-scope], [accuracy-ledger]; the naming-is-addressing rule at [conventions];
  commits `e826668`, `0078157`.
- **Attribution** — MISSING.
- **Supersedes** — parts of the founding audit's remediation. Its own clearance of
  three Wave-1 items was itself overturned the same day (see the sixteen corrections
  below).

### 2026-06-10 · Frenkel-pair yield was dimensionally invalid

Without the macroscopic displacement cross-section (atoms per volume times the
displacement cross-section, in inverse centimetres), the bare product of defects per
displacement, surviving fraction and dose fluence is a **fluence** in inverse square
centimetres — not a concentration. The expression could not have been right in any
units.

- **Evidence** — [multiscale-state#eom-defect-population]; [traps#units].
- **Attribution** — the re-audit addendum. MISSING: no agent named. The finding is
  dated from the re-audit's own record, which names the Frenkel-pair dimensional defect
  among its ten findings; the source log entry carried only "2026-07", which is when it
  landed in the state page.
- **Supersedes** — the pre-cross-section defect-generation expression.

### 2026-06-10 · Scharfetter–Gummel discretization made mandatory for the macro carrier flux

At the ultra-wide-bandgap operating point — 1 MV/cm across roughly 10 nm cells — the
cell Péclet number is about 40. There, central differencing makes the *residual
operator itself* wrong, so the operator would be scored against a discretization
artifact rather than against physics.

- **Evidence** — [multiscale-state#eom-continuum]; [traps#practice].
- **Attribution** — the re-audit addendum. MISSING: no agent named. Dated as above; the
  source log entry carried "2026-07", the landing date.
- **Supersedes** — naive and central finite-volume differencing for the carrier flux.

### 2026-06-10 · The learned-correction freezing rule

A learned correction trained on the same residual it modifies can co-adapt to zero that
residual and destroy the very obligation domain it exists to protect. Therefore: fit
only against external anchors, frozen with respect to the operator's training loss; and
with no version-one anchors available, ship it as the identity and keep the
high-field-high-temperature corner certificate-refused.

- **Evidence** — [coupling-structure#provenance-contract];
  [accuracy-ledger#high-field-coefficients]; `data/registry-manifest.csv` row 49.
- **Attribution** — the re-audit addendum, which names the learned-correction training
  contract among its ten findings; carried forward by the high-field wave. MISSING: no
  agent named.
- **Supersedes** — the unconstrained learned-coefficient path.

### 2026-06-10 · Wave 1 — III-nitride seeding and its adversarial audit: sixteen corrections

Two inventory passes, six primary-literature deep dives, and two adversarial auditors
mandated to *refute* the seeding. It produced the polarization-convention pairing rule
and the accidental-cancellation finding — the two rules the whole III-nitride
polarization package rests on — and sixteen numeric and citation corrections. One of
the sixteen caught a **fabricated citation in previously-cleared material**, which
became the rule that a clearance is not evidence.

The sixteen, kept in full because they are cited across the corpus as live provenance
markers and thirteen sites still reach for them:

| # | Correction |
|---|---|
| 1 | Zero-point renormalization amplitudes re-tagged from total to isochoric, and the values with them |
| 2 | The ±5% polarization-difference justification re-grounded on the accidental cancellation |
| 3 | The proper-piezoelectric-constant self-consistent-pairing certificate |
| 4 | The high-indium indium-gallium-nitride guard |
| 5 | Gallium-nitride high-temperature conductivity 100/70 → carry the measured 60 / 35–40 |
| 6 | Aluminium-nitride high-temperature conductivity → theory-only |
| 7 | Gallium-nitride ionization-coefficient citation "Maeda, *Appl. Phys. Lett.* 112 (2018)" → **Özbek & Baliga, *IEEE Electron Device Lett.* 32, 1361 (2011)** |
| 8 | Aluminium-nitride conductivity citation Lindsay *PRL* 109 → Rounds/Slack, *Appl. Phys. Express* 11 (2018) and Slack, *J. Phys. Chem. Solids* 48, 641 (1987) |
| 9 | Aluminium-nitride longitudinal-optical phonon energy 100 → ~111–114 meV (later re-rounded to 110–114 against the Davydov anchors) |
| 10 | Aluminium-nitride Debye temperature 1150 → ~1000 K |
| 11 | Gallium-nitride saturation velocity 2.5e7 → saturation 1.4e7 with peak 2.85e7 cm/s |
| 12 | Fröhlich coupling: gallium nitride 0.49 → ~0.40, aluminium nitride 0.65 → ~0.58 |
| 13 | Aluminium-nitride electron mobility 300 → 871 (perpendicular) / 619 (parallel) first-principles, 426 best experimental; the 300 was doped and defective material |
| 14 | Gallium-nitride ionization-coefficient uncertainty ×1.5 → at least ×3, reseeded from Cao |
| 15 | Diamond image-force lowering → 0.16 eV at 1e6 V/cm; the older 0.06 eV was a √10 field error |
| 16 | The re-audit addendum earlier that day had over-cleared corrections 5, 7 and 8 as "sound" — recorded, and the origin of the clearance-is-not-evidence rule |

Genuine gaps were flagged and never invented: the aluminium-nitride electron
Caughey–Thomas parameter quartet (paywalled); aluminium-nitride hole mobility (deep
magnesium); aluminium-nitride *measured* avalanche ionization coefficient (only
Monte-Carlo, electron-only, so the measured value stays certificate-refused);
aluminium-nitride hole ionization; a normalized breakdown-field temperature
coefficient for gallium and aluminium nitride (only device-level data exists — the
positive sign is confirmed); the perpendicular Born effective charge; the sign of one
piezoelectric constant (literature-split); aluminium-gallium-nitride piezoelectric
constants, composition-dependent saturation velocity, and holes; the aluminium-nitride
pressure derivative of the bulk modulus and its per-axis sound velocities.

- **Evidence** — [cert-obligations#ingest-battery], [coupling-structure],
  [accuracy-ledger#iii-n-electronic], [traps#frames], [traps#practice]; the seeded
  reference CSVs under `data/reference-data/`; commit `d6f4883`.
- **Attribution** — two inventory passes, six primary-literature deep dives, two
  adversarial auditors on a refute mandate. MISSING: none of them is named.
- **Supersedes** — correction 16 explicitly supersedes the re-audit addendum's
  clearance of corrections 5, 7 and 8, taken the same day.

### 2026-06-10 · Zero-point-renormalization amplitudes re-tagged isochoric, and the slope-kind guard introduced

The Engel/Miglio anharmonic-Hamiltonian-correction values are clamped-lattice
electron-phonon only — that is, isochoric — and had been carried under a `total` tag.
A `total` slope already folds in the lattice-expansion shift of roughly 30–40% that a
separate registry row carries in its own right, so the mis-tag was "the worst of both":
it both double-counted and made the certificate refuse co-activation with the
thermal-expansion path. The tag was made a machine-checkable double-count guard.

- **Evidence** — [coupling-structure#slope-kind-guard];
  [accuracy-ledger#ahc-zpr]; [cert-obligations#coupling-derived-checks];
  `data/registry-manifest.csv` row 63.
- **Attribution** — the Wave-1 III-nitride audit and Pass C. MISSING: no agent named.
- **Supersedes** — the `total` tag on isochoric magnitudes.

### 2026-06-10 · Pass C — per-material accuracy design

Four web-grounded deep dives folded into one adversarial audit; closed the founding
audit's second-priority tranche. Produced the anharmonic gap renormalization, the
four-phonon high-temperature correction, the breakdown-field temperature slope — which
corrected a **sign error** — the temperature-and-pressure-aware convex hull with its
metastability band, and the Wannierization quality gate.

- **Evidence** — [accuracy-ledger] and `data/registry-manifest.csv`; commits `54d34ab`,
  `ccd9441`.
- **Attribution** — MISSING.
- **Supersedes** — the claim that the breakdown field drops ~20% from 300 K to 800 K.
  EVIDENCE-DIES: the pass's full primary-source citations were never written to a page.
  The corpus records only that they are "in git history", which for a compliance record
  means they are not cited at all.

### 2026-06-25 · The computer-science-audience deck published, and retired the same year

A presentation framing the oracle as scoring rather than solving. It carried a stale
formula count under a standing waiver and published a boolean validity predicate that
canon forbids. Retiring the deck discharged the only waiver the reconciliation campaign
carried; no waiver now stands.

- **Evidence** — [product#evidence-not-verdict]; [rationale#score-not-solve]; commits
  `e862d12`, `fd79927`, `df89dc9`, `3a5e92b`.
- **Attribution** — MISSING.
- **Supersedes** — the deck itself, and its published boolean validity predicate, which
  the evidence-never-verdicts rule supersedes.

---

# 2026-07

### 2026-07-07 · Gap audit

A post-remediation sweep in three parallel inventory passes. Verifier-soundness holes
closed: density-matrix admissibility must be *scored* rather than assumed; the gauge
and electrostatic partition; and the two-predicate polar split, which is the rule that
keeps β-gallium-oxide coherent. Seven registry rows added. The forward wave programme —
waves three through five, the reduced metals schema, and the decision about a Curie
point falling inside the operating window — was promoted to the reference battery.

The audit's own section index is kept here because pages and eight data-file rows still
cite this audit by letter and number, and the tags have nothing else to resolve
against:

| | |
|---|---|
| **A** | Verifier-soundness holes — states the oracle could wrongly accept. **A1** density-matrix admissibility never scored · **A2** vector-potential gauge and the electrostatic double-count · **A3** the two "polar" predicates conflated |
| **B** | Missing or incorrect physics for the named scope. **B1** pyroelectricity absent · **B2** gate-dielectric degradation package empty · **B3** aluminium-gallium-nitride nonlinear polarization interpolation unstated · **B4** experimental structure channels unmapped · **B5** radiation modelled as displacement only · **B6** dangling radiative branch and hydrogen-only redistribution · **B7** research-file physics errors · **B8** un-reconciled numeric contradictions across research files |
| **C** | Consistency faults, mechanical. **C1**–**C12**: stale README and audit-prompt counts, the atomic-species set for the minimum viable product, scope reconciliation, the "17 named tags" slip (19 is canon), uncertainty-column holes against the refusal rule, mixed uncertainty conventions, the count check, and empty research-source frontmatter (deferred) |
| **D** | Data gaps — the per-material research programme. **D0** diamond battery missing · **D1** wave two = β-gallium-oxide · **D2** wave three = cubic boron nitride and 4H silicon carbide · **D3** no wave covered contact metals, substrates beyond silicon carbide, or dielectrics · **D4** standing acquisitions |
| **E** | Standing open registers — confirmed complete |

- **Evidence** — [traps#verifier-soundness]; [reference-battery#wave-program];
  `data/registry-manifest.csv` (seven Source cells) and
  `data/reference-data/transport-coefficients.csv` (one); commits `6c8e2e3`, `2d38c39`,
  `577f083`, `e9e176e`.
- **Attribution** — "three parallel inventory passes". MISSING: none named.
- **Supersedes** — MISSING: the record does not state what the audit's findings
  displaced, beyond the individual items logged below.

### 2026-07-07 · Density-matrix admissibility gates added to the positivity category

Ensemble N-representability — the density matrix Hermitian, with eigenvalues between
zero and one — expressed as per-wavevector-block spectral bounds, plus
applicability-gated zero-temperature idempotency. Without these a candidate density
matrix outside the bounds can zero every equation-of-motion residual while being
unphysical, so the oracle would be sound as a verifier of the *dynamics* but not of the
*state*.

- **Evidence** — [residual-definitions#positivity].
- **Attribution** — the gap audit, item A1. MISSING: no agent named.
- **Supersedes** — extends the pre-audit positivity category rather than replacing it.

### 2026-07-07 · Gauge fixing and the electrostatic partition made normative

The vector potential is carried in the Weyl gauge with transversality; the
electromagnetic energy counts the transverse sector only; the longitudinal
electrostatic sector is owned by the matter functionals. The vector-potential
equation-of-motion residual becomes gauge-unambiguous, and no electrostatic energy is
double-counted between field and matter terms.

- **Evidence** — [generic-dynamics#gauge-partition]; [unified-state#slots].
- **Attribution** — the gap audit, item A2. MISSING: no agent named.
- **Supersedes** — the prior electromagnetic-energy statement, which did not partition.

### 2026-07-07 · The status legend for minimum-viable-product targets split

"Path-met" means the closed-form path exists **and** its diamond anchors are seeded so
the accuracy obligations can check the target. It explicitly does **not** mean a
certificate run has passed. The former bare "met" read as target-met.

- **Evidence** — [accuracy-ledger#mvp-targets].
- **Attribution** — the gap audit, item D0. MISSING: no agent named. The source record
  carried only "2026-07"; the date is taken from the audit it names.
- **Supersedes** — the bare "met" status.

### 2026-07-07 · Gap audit B7 opened the group A/B/C derivations to physics review, and found four independent errors

This pass is the origin of the six corrections that follow.

- **Evidence** — EVIDENCE-DIES: recorded only at `11.1:742-747`, `11.2:527-533` and
  `11.3:711-714`, all of which are deleted. The corrections themselves survive in the
  pages named below; the *record that they were corrections* survives only here.
- **Attribution** — the gap audit, item B7. MISSING: no agent named.
- **Supersedes** — nothing directly; it is the parent of the six entries below.

### 2026-07-07 · Thermal-expansion formula corrected — a compliance/stiffness inversion

Was written with the inverse of the compliance where the compliance belongs, with the
tensorial Grüneisen parameter undefined and the reciprocal volume missing. Now: the
thermal-expansion tensor equals one over the volume, times the compliance (the inverse
of the stiffness), contracted with the sum over modes of the strain-Grüneisen tensor
times the mode heat capacity — the strain-Grüneisen tensor being the object whose
volumetric trace is the scalar Grüneisen parameter.

- **Evidence** — corrected form carried into [typed-compositions#mechanical] and
  [typed-compositions#thermal]. EVIDENCE-DIES: `11.1:502` and `11.1:743-746`.
- **Attribution** — gap audit B7. MISSING: no agent named.
- **Supersedes** — the inverted-compliance form.

### 2026-07-07 · Electron-phonon vertex mass convention made multi-species-correct

The bare one-over-root-two-mass-times-frequency prefactor is single-species shorthand.
Multi-species cells carry a per-atom mass through the mass-weighted eigenvector
normalization.

- **Evidence** — [coupling-structure#electron-phonon]. EVIDENCE-DIES: `11.1:514-522`,
  `11.2:148-152`.
- **Attribution** — gap audit B7. MISSING: no agent named.
- **Supersedes** — the unannotated single-mass vertex.

### 2026-07-07 · Non-collinear spin density-functional theory re-attributed

The construction was labelled "Vignale–Rasolt"; that is *current* density-functional
theory. The correct attribution is von Barth–Hedin and Kübler. Vignale–Rasolt is
retained, correctly, for the orbital-current functional in the relativistic synthesis.

- **Evidence** — EVIDENCE-DIES: `11.2:188`, `11.2:527-530`. This correction is a
  citation-hygiene finding about a page being deleted; unless the group-B derivation is
  mined into a surviving page, nothing but this entry will record it.
- **Attribution** — gap audit B7. MISSING: no agent named.
- **Supersedes** — the "Vignale–Rasolt" label on non-collinear spin density-functional
  theory.

### 2026-07-07 · The Maxwell source term's 4π restored

In Gaussian units, the semiconductor-Bloch/Maxwell coupling carries a factor of 4π on
the polarization source term. It was absent.

- **Evidence** — [traps#units]. EVIDENCE-DIES: `11.2:330-332`, `11.2:531-532`.
- **Attribution** — gap audit B7. MISSING: no agent named.
- **Supersedes** — the 4π-less source term.

### 2026-07-07 · Spin-orbit double-count removed

The relativistic Hamiltonian carried an explicit spin-orbit term *on top of* the Dirac
operator. Spin-orbit coupling emerges in the non-relativistic reduction and must not be
added by hand.

- **Evidence** — EVIDENCE-DIES: `11.2:466-467`, `11.2:530-531`. Same exposure as the
  re-attribution above.
- **Attribution** — gap audit B7. MISSING: no agent named.
- **Supersedes** — the Dirac-plus-explicit-spin-orbit Hamiltonian.

### 2026-07-07 · H-theorem direction corrected

The Lyapunov table said negative entropy is "non-decreasing"; the H-theorem gives
entropy production non-negative, so negative entropy is **non-increasing**. The error
contradicted the same file's own earlier section.

- **Evidence** — [generic-dynamics#entropy-functional]. EVIDENCE-DIES: `11.3:546`,
  `11.3:711-714`.
- **Attribution** — gap audit B7. MISSING: no agent named.
- **Supersedes** — the "non-decreasing" direction.

### 2026-07-07 · Gap audit B7 corrections to the defects derivation

The charge-balance exact form and the phosphorus-in-diamond activation example were
about 100× and 3× wrong; the misfit convention was normalized to the substrate lattice
constant; the diamond thermal-expansion anchor was corrected to about 3e-6 per kelvin
at 773 K; and the Freysoldt correction symbol was renamed to stop colliding with the
Fermi level.

- **Evidence** — [traps#practice]. EVIDENCE-DIES: `11.4-deriv-defects.md:672-677`.
- **Attribution** — the gap audit. MISSING: no agent named.
- **Supersedes** — the pre-audit values for each.

### 2026-07-07 · Gap audit B8 corrections to the crystal-structure-prediction derivation

Misfit denominators normalized to the substrate — diamond-on-silicon read **+52%**
under the old film-referenced denominator and reads −34% correctly; platinum on
hydrogen-terminated diamond and the tungsten/molybdenum carbide onsets harmonized to
ranges; and the Σ3 twin-boundary energy corrected from "≈0" to "tens of millijoules per
square metre, effectively 0".

- **Evidence** — EVIDENCE-DIES: `11.6-deriv-csp.md:359-364`.
- **Attribution** — the gap audit. MISSING: no agent named.
- **Supersedes** — the film-referenced misfit denominator; the near-zero twin-boundary
  energy.

### 2026-07-07 · The diamond-tungsten worked example carried five compounding physics errors in one artifact

A Fröhlich/polar-optical-phonon-limited saturation velocity fired on **non-polar
diamond**, in violation of the example's own polarity classifier; a roughly 4.5 eV
*n*-type barrier was fed into leakage for a *p*-type contact (about 3.5 eV wrong);
image-force lowering was 0.06 eV, a √10 field error against the correct 0.16 eV at
1e6 V/cm; lattice thermal conductivity at 773 K read about 800 against a battery value
of 620; and the electron affinity was untagged by surface termination.

- **Evidence** — generalized and live as [traps#practice]. EVIDENCE-DIES: the example
  and its corrections are at `11.8:596-601`.
- **Attribution** — the gap audit. MISSING: no agent named.
- **Supersedes** — the pre-audit worked example.

### 2026-07 (day MISSING) · The registry's provenance-legend lag closed

Rows 128–134 — the gap-audit package — carry a topology-atlas provenance. The counts
prose had always described them correctly; only the column legend lagged.

- **Evidence** — [formula-registry]; `data/registry-manifest.csv` rows 128–134.
- **Attribution** — the gap-audit pass. MISSING: no agent named; no day recorded.
- **Supersedes** — the pre-fix provenance legend.

### 2026-07-08 · The diamond reference battery seeded

A machine-readable anchor for every declared accuracy target, including the
high-temperature four-phonon anchor — thermal conductivity about 620 W/m·K at 773 K,
and the 1100 K value — landing as two registry rows: a closed-form four-phonon
correction and a dormant iterative linearized-Boltzmann consistency sibling.

- **Evidence** — [reference-battery#diamond-battery];
  `data/reference-data/transport-coefficients.csv`; `data/registry-manifest.csv` rows
  121–122; commit `e9e176e`.
- **Attribution** — a battery-seeding pass. MISSING: no agent named.
- **Supersedes** — nothing; this is the first battery.

### 2026-07-16 · Reconciliation pass and certification

A full-base scrub: 21 commits, 88 verified findings fixed, a calibration gate, and two
certifier rounds. Auditors were calibration-gated — five of five planted contradictions
detected before any report was trusted — ran two independent rounds (first by document
family, then re-sliced by invariant class), and produced evidence transcripts rather
than verdicts.

It produced the **authority order** and the **frozen-directories rule** — the two rules
that adjudicated every subsequent conflict — plus the certification protocol:
calibration gate, evidence transcripts, and a log of dismissed near-findings. All three
existed *only* in the campaign report and were promoted to canon before the report was
collapsed.

- **Evidence** — [rationale]; commits `72bebe8` through `774cfd0`.
- **Attribution** — a multi-agent audit campaign; "two certifier rounds". MISSING: no
  agent, model or version named.
- **Supersedes** — the pre-reconciliation base. **And is itself superseded**: the
  authority order and the frozen-directories rule are both replaced by this
  restructure's ownership model, in which a topic has exactly one owning page and
  nothing is frozen by directory.

### 2026-07-16 · The scorer-to-stepper strong duality is refuted; a shared-kernel factorization survives

No step algebra exists such that folding it steps every graph that folding the scoring
algebra scores — causality assignment is a global matching property, not a per-node
denotation. What survives is weaker and real: the stepper is a sibling lowering at the
code-generation stage, consuming a system-layer analysis. The evolver is a flag-gated
sibling artifact sharing the scorer's content-addressed right-hand-side forests, with
the integrator staying consumer-side. Time-evolution product verbs remain unclaimed
until that lowering is specified and built as its own named wave, slow tier first.

- **Evidence** — [product#deployment-shape];
  [compose-time-pipeline#evolver-lowering]; [generic-dynamics#evolver-duality];
  commits `402cab1`, `9eff050`, `7910de4`. EVIDENCE-DIES: the research memo itself is
  `journal/live/specs/2026-07-16-evolver-duality-research.md`.
- **Attribution** — an independent deep-research commission. MISSING: no agent, model
  or version named.
- **Supersedes** — the "one intermediate representation, two interpreters" strong
  reading. Also supersedes the corpus's own status record, which still described this
  work as being commissioned after it had returned.

### 2026-07-16 · The integrator interface closed

The physics library emits a per-tier tangent map and a steppable-form manifest — a pure
function, not an integrator. Long-trajectory drift is *exported* to the integrating
consumer rather than dissolved. Three alternatives were rejected with reasons: an
opaque right-hand-side closure discards the structure tags; shipping an integrator
imports step-size judgment the library has no basis for; and deferring the decision
buys no information.

- **Evidence** — [pino-bridge#steppable-form-manifest]; [gamma-hat#read-write-paths];
  commit `7910de4`.
- **Attribution** — the same commission, adopted. MISSING: no agent named.
- **Supersedes** — long-trajectory drift as an internal open problem of the density
  matrix; and the previously-open integrator-interface decision.

### 2026-07-16 · The scorer is the evolver's auditor

The ten non-equation-of-motion residual categories become the integrator's preservation
obligations under the *same* residual keys. Scoring an evolver-produced trajectory
measures exactly the drift the integrator failed to prevent, with no new machinery.

- **Evidence** — [residual-definitions#preservation-obligations].
  EVIDENCE-DIES: the memo section is in `journal/live/specs/`.
- **Attribution** — the same commission. MISSING: no agent named.
- **Supersedes** — nothing.

### 2026-07-16 · Wave 2 — the β-gallium-oxide package cleared and seeded

Two independent adversarial auditors: one on conventions returning clear-with-pins, one
on numbers returning block, then fixed. Nine value and provenance corrections applied,
including the critical-field misattribution — the anisotropic triple 10.2 / 4.8 / 7.6
MV/cm replaces a scalar "≈8" that **appears nowhere in the cited paper** — and the
starred-axis direction labels. The bowing rider remains gated pending a pin-read.

- **Evidence** — [accuracy-ledger#monoclinic-frames]; [traps#frames];
  `data/reference-data/`; commit `b489656`. EVIDENCE-DIES: the audit record is
  `journal/live/audits/2026-07-16-wave2-beta-ga2o3-audit.md`.
- **Attribution** — two web-verifying auditors on the Wave-1 refute mandate,
  adjudicated. MISSING: no agent, model or version named.
- **Supersedes** — the 2026-07-08 drafted values.

### 2026-07-16 · The polar predicate split into two independent predicates

Being polar — Born charges, longitudinal-optical/transverse-optical splitting, which
gates Fröhlich and polar-optical-phonon coupling — is not the same as being
non-centrosymmetric, which gates the piezoelectric classes. They coincide on diamond
(both false) and on the wurtzite III-nitrides (both true), which is why the conflation
was invisible for so long; they split on β-gallium-oxide, which is centrosymmetric in
its C2/m structure yet whose dominant mobility limiter is a multi-mode Fröhlich
interaction.

- **Evidence** — [applicability-classifiers#polar-predicate-split];
  [applicability-classifiers#is-polar-material].
- **Attribution** — the gap audit (item A3) and the Wave-2 seeding specification.
  MISSING: no agent named.
- **Supersedes** — the single "polar" predicate.

### 2026-07-16 · A fourth β-gallium-oxide axis frame identified in the reference data

The resonant-ultrasound and laser-diffraction elastic frame sets its first axis along
the real *a*, which is 13.83° from the reciprocal *a\**, so its first elastic constant
is **not** along the crystal-physical first axis. Four frames, one material.

- **Evidence** — [accuracy-ledger#monoclinic-frames]; [traps#frames];
  `data/reference-data/elastic-constants.csv`.
- **Attribution** — the Wave-2 adversarial audit. MISSING: no agent named.
- **Supersedes** — the three-frame guard.

### 2026-07-16 · Pyroelectric coefficients seeded with a sign correction

The coefficient is **positive** in the seeded zincblende-reference frame — aluminium
nitride +3.0e-6, gallium nitride +4.5e-6 C/m²K, uncertainty a factor of two — because
the spontaneous polarization is negative in that frame and its magnitude falls with
temperature. Raw literature quotes the coefficient as negative under the opposite
convention. The drift is 20–30% of the sheet-charge product over a 750 K temperature
swing, which is larger than the ±5% polarization budget at the operating point.

- **Evidence** — [accuracy-ledger#polarization-coefficients];
  `data/reference-data/polarization.csv`.
- **Attribution** — the Wave-2 adversarial audit. MISSING: no agent named.
- **Supersedes** — the unsigned, unflipped literature values.

### 2026-07-16 · The gate texts were read, and one refuted the audit's own premise

The erratum corrects only copper-platinum-ordered indium-alloy *piezoelectric*
polarization; the spontaneous-polarization bowing is untouched. "Ebert et al." resolved
to Lan et al., *Phys. Rev. B* **113**, 155302 (2026) — off-axis holography, open
access, indium-gallium-nitride only — which **experimentally refutes the
zincblende-reference bowing curvature** and validates the local-Hamiltonian frame. That
upgrades the ledger's certificate refusal from theoretical to experimental. The ±5%
aluminium-gallium-nitride anchor is untouched. Recorded because it *narrows* where the
accidental cancellation may be relied on.

- **Evidence** — [accuracy-ledger#polarization-bowing]; `data/registry-manifest.csv`
  row 35. Literature: Lan et al., *Phys. Rev. B* 113, 155302 (2026); commit `c7b6325`.
- **Attribution** — a user-acquired erratum plus an open-access re-check. Javier
  acquired the erratum. MISSING: the agent that performed the re-check is not named.
- **Supersedes** — the audit's own premise that bowing curvature is reference-invariant.

### 2026-07-16 · Two "paywalls" were bot-blocks, not paywalls

Both the elastic-tensor paper and the holography paper are open access; the auditors'
403 responses were bot-blocking. Re-checking closed the second gate the same day and
produced the derived high-temperature conductivity anchors along the *b* axis.

- **Evidence** — commits `85e2865`, `c7b6325`; `data/reference-data/`. EVIDENCE-DIES:
  the audit record is in `journal/live/audits/`.
- **Attribution** — a post-audit re-check. MISSING: no agent named.
- **Supersedes** — a declared data gap and a gate, both of which were spurious.

### 2026-07-16 · The diamond dataset is whole; the missing family was never lost

Two truncated transfers had concluded that a strain family existed and had been lost.
The archive order is 1, 3, 2, 6, 5, **4** — so every truncated copy stopped before
reaching family 4. A direct single-file download of 10,698,913,488 bytes passes an
end-to-end integrity check. The salvage inference was right; only its conclusion was
wrong.

- **Evidence** — `data/diamond-strain-sweep/read-me-first.md#provenance`.
- **Attribution** — dataset recovery. MISSING: no agent named.
- **Supersedes** — the 877-point byte-salvage count and its "family 4 lost" conclusion.

### 2026-07-16 · The diamond strain hypersurface characterised as operator feedstock

1,179 rows at hybrid level (screened-exchange functional with gap-tuned exact
exchange), **1,131 distinct strain shapes after de-duplication**, six lattice-distortion
families to ±10%, with stress tensors, mapped onto the oracle's import interface. A
methodological guard was established with it: **de-duplication must precede any fit.**

- **Evidence** — [rationale]; `data/diamond-strain-sweep/read-me-first.md`;
  `data/diamond-strain-sweep/index-of-all-runs.tsv`.
- **Attribution** — a dataset salvage and health audit. MISSING: no agent named.
- **Supersedes** — the ~877 figure, which was a byte-salvage count and never a row
  count.

### 2026-07-16 · Wave-1 III-nitride anchors rewritten in place with the audited values

Gallium-nitride saturation velocity 2.5e7 → 1.4e7 cm/s (the old number was the *peak*
velocity); aluminium-nitride longitudinal-optical phonon energy 100 → 110–114 meV;
Fröhlich coupling gallium nitride 0.49 → 0.40 and aluminium nitride 0.65 → 0.58;
aluminium-nitride electron mobility ~300 (doped) → 871 perpendicular / 619 parallel
first-principles, 426 best experimental; diamond image-force lowering 0.18 → 0.16 eV at
1e6 V/cm — **and a separate in-repo 0.06 eV traced to a √10 field-scaling error**.
Impact-ionization anchors reconciled to Cao 2018, Bulutay, and Ghosh–Singisetti in a
second pass.

- **Evidence** — [accuracy-ledger#iii-n-electronic];
  [accuracy-ledger#high-field-coefficients]; `data/reference-data/`. EVIDENCE-DIES: the
  in-place rewrite is recorded at `11.5-deriv-high-field.md:607-627`.
- **Attribution** — the 2026-06-10 Wave-1 audit; landed 2026-07-16. MISSING: no agent
  named.
- **Supersedes** — the pre-Wave-1 III-nitride anchor set.

### 2026-07-16 · Two tables of diamond-metal contact stability had drifted because one restated the other

Resolved by declaring the defects derivation the owner of the stability temperatures.
Recorded because the mechanism — restatement instead of citation — is the general
failure this restructure exists to prevent, and because **the declared deference was
never actually applied**: the dependent table kept its own column.

- **Evidence** — [accuracy-ledger#diamond-metal-contacts]. EVIDENCE-DIES:
  `11.6-deriv-csp.md:143-146`, and the owner it defers to is also a chapter-11 page.
- **Attribution** — the strata rewrite. MISSING: no agent named.
- **Supersedes** — the independent stability-temperature column in the
  crystal-structure-prediction derivation.

### 2026-07-16 · Legacy global regime numbers replaced by regime names

The reconciliation pass converted three status banners into changelogs and replaced a
derivation's legacy global "regime N" coordinates with regime names — they matched
neither the file's own local numbering nor the canonical table.

- **Evidence** — [generic-dynamics#nine-regimes]. EVIDENCE-DIES: `11.1:740-741`,
  `11.2:526`, `11.3:708-710`; and the changelogs those banners became are themselves
  forbidden under this restructure and are deleted.
- **Attribution** — the reconciliation pass. MISSING: no agent named.
- **Supersedes** — the global regime-number coordinates.

### 2026-07-21 · Corpus reconciliation into a book

Three systematic passes — a contradiction sweep, an authority map, and a
process-artifact audit — over about 26,300 lines. 29 contradictions found, six of high
severity. Four live defects fixed where canon contradicted the seeded data, including
two sign errors that would have inverted physics for anyone seeding from the ledger.
The corpus was restructured into a book: 58 pages across 11 chapters, addressed by page
identifier, with generated apparatus replacing roughly 10,500 lines of duplication.

- **Evidence** — commits `89840c2`, `9c45ccb`, `e12fabd`, `f43cbb8`, `e0e3b44`.
- **Attribution** — "three systematic passes". MISSING: no agent named.
- **Supersedes** — the pre-book monolith tree. **Superseded in turn** by this
  restructure, which replaces chapter numbering with journals and sections, and page
  identifiers with filenames.

### 2026-07-21 · Exact identity, measured error — one rule closing six open faces

The collision: identity is exact — an address is the hash of canonical bytes, with
floats normalised so that numerically equal values share an address — while every
object also carries a tolerance that composes. Approximate equality is a **tolerance**
relation and is not transitive, so it induces a covering by maximal cliques rather than
a partition. No partition means no canonical representative, nothing to hash, and
hash-consing, Merkle deduplication and constant-time address equality all die with it.
The substrate needs a quotient; the mathematics offers only a covering.

The resolution is one rule: *identity is exact, always; the tolerance never enters the
address. Any operation that can make the computed object differ from its exact
counterpart emits a computable a-posteriori estimate of that difference, as certificate
evidence.* Approximate equality is then never used as an identity relation, so its
non-transitivity never has to be repaired. Nothing branches at runtime; nothing is
refused for being approximate — it is *scored*, and the consumer decides. The gate gets
**weaker**: "must be exact" becomes "must be able to estimate its own error". No new
residual category, because these are certificate-only generators, so the
nineteen-category enumeration is untouched and the training loss is unpolluted.

- **Evidence** — [representation-substrate#identity-exact];
  [representation-substrate#estimate-dont-decide]; [gamma-hat#identity-is-exact];
  [traps#practice]; commits `c0e345f`, `e6b1946`. Literature: Lubich & Oseledets (2014);
  Kieri, Lubich & Walach (2016); Ceruti, Kusch & Lubich, *BIT* 62 (2022); Zhang et al.,
  PLDI (2023); Blondel et al., NeurIPS (2022).
- **Attribution** — MISSING: recorded as a corpus pass with no agent named.
- **Supersedes** — the framing of tolerance-equality as an open computer-science
  problem.

### 2026-07-21 · The four density-matrix data-structure questions were one problem, and it closed

Exact content-addressed identity meeting approximate numerics, seen from four sides.
Dispositions: tolerance-equality became the rewrite-admission rule; materialization
became an adjoint-tape schedule at the code-generation stage — a cost question with no
error term; drift is exported to the consumer; and rank-applicability became a
compile-time predicate.

Three of the six faces were not open at all. Robust dynamical-low-rank integrators —
projector-splitting, robustness to small singular values, and the rank-adaptive
basis-update-Galerkin family — preserve trace, Hamiltonian energy, and gradient-flow
monotonicity up to a declared tolerance, matching the corpus's own conserve/bound/
monotone obligation map term for term. Inexact implicit differentiation has *computable
a-posteriori* error estimates. Materialization was misfiled: it changes cost, not value.

- **Evidence** — [gamma-hat#resolutions]; [representation-substrate#identity-exact];
  the emitted open-question register.
- **Attribution** — a registry and substrate repair pass. MISSING: no agent named.
- **Supersedes** — the open-decision item that carried the four questions; the
  "genuinely open computer-science problems" framing. It also corrects a claim that
  canon had called these the *only* open computer-science problems, which the
  computational overview disclaimed in the same paragraph — a claim that was
  **twice** mis-called open.

### 2026-07-21 · The physics library is confirmed scorer-only for the density matrix

The density matrix never evolves in the oracle; the write path is construction and
self-consistency only. This resolved a standing contradiction in which the library
landscape and the README denied trajectories while the density-matrix page listed
time-stepping as a write path. Canon won. The consequence is that drift is **exported**
to the integrating consumer through the steppable-form manifest, not dissolved.

- **Evidence** — [gamma-hat#scorer-only]; [gamma-hat#read-write-paths];
  [pino-bridge#steppable-form-manifest].
- **Attribution** — the oracle-file decision of that date. MISSING: no agent named.
- **Supersedes** — the time-stepping write path on the density-matrix page.

### 2026-07-21 · The identity rule closed three of the four named verifier-soundness gaps

Recorded because the registration gate's strength depends on which gaps remain live.
The survivors are stated sharply rather than deleted.

- **Evidence** — the emitted open-question register; [build-verification#gate-1-registration].
- **Attribution** — the same pass. MISSING: no agent named.
- **Supersedes** — three of the four originally-named verifier-soundness gaps.

### 2026-07-21 · The dressing-staleness bound exists, and it is the validity radius

A frozen one-shot dressing owes an estimator like any other approximation, and that
estimator *is* the validity radius: the state displacement norm times the sensitivity
of the dressing to the state, measured once at the reference state.

- **Evidence** — [residual-machinery#dressing-certs];
  [born-oppenheimer-levels#dressing-tiers].
- **Attribution** — the estimate-don't-decide wave. MISSING: no agent named.
- **Supersedes** — the third verifier-soundness gap, "no declared validity radius".
  **Note for the auditor:** at the time this was surveyed, the levels page still stated
  that gap as open. Whether the new page states the resolution is the builder's
  responsibility; this entry records that the resolution exists.

### 2026-07-21 · The frozen-dressing validity radius became computable

A staleness coefficient — the norm of the dressing's sensitivity to the state —
measured once at the reference state at compile time, times a runtime state norm, is
the dressing-staleness term that the tolerance-composition function listed but had no
number for.

- **Evidence** — [residual-machinery#dressing-certs].
- **Attribution** — the estimate-don't-decide wave. MISSING: no agent named.
- **Supersedes** — the unquantified dressing-staleness term.

### 2026-07-21 · The rewrite-admission rule

A rewrite at the algebraic-simplification stage is admissible if and only if it is exact
over the reals, its floating-point side conditions are discharged by an equivalence-class
interval and not-equals analysis, and it registers a fidelity generator. Equality
saturation stays offline for a stated reason rather than as a hedge.

What settled it: rewriting under floating-point semantics is solved by side conditions
discharged by an equivalence-class analysis. Herbie's rules were known-unsound for
years, and deleting them *made the tool useless on a large part of its own benchmark
suite* — exactness-only is not a viable gate. The `egglog` work made them sound with an
interval analysis composed with a not-equals analysis, and the sound version was faster
overall. Its equality stays exact over the reals with the interval facts riding
alongside — the same separation this corpus arrived at independently.

- **Evidence** — [compose-time-pipeline#rewrite-admission]. Literature: Zhang et al.,
  PLDI (2023).
- **Attribution** — the corpus, adopting Zhang et al. MISSING: no agent named.
- **Supersedes** — "exactness-only" as the admission gate; and the "genuinely open
  problem" framing this rule was twice mis-filed under.

### 2026-07-21 · Materialization policy reclassified from accuracy to scheduling

Forcing versus deferring changes cost, not value, so no error term exists and no
fidelity generator is owed. It is a schedule at the code-generation stage —
checkpointing, in the `revolve` sense.

- **Evidence** — [compose-time-pipeline#stage4-adjoint-tape]; [gamma-hat#stage4-internals].
- **Attribution** — corpus. MISSING: no agent named.
- **Supersedes** — "materialization policy has no principled default" as an open
  data-structure problem.

### 2026-07-21 · Attribution correction: the rematerialization complexity result is Naumann, not `revolve`

NP-completeness of rematerialization on a directed acyclic graph is Naumann, *J.
Discrete Algorithms* **7**(4), 402–410 (2009) — a separate result from `revolve`
(Griewank & Walther, *ACM TOMS* **26**(1), 19–45, 2000). The corpus had folded it into
the `revolve` parenthetical as though one source gave both.

- **Evidence** — [compose-time-pipeline#stage4-adjoint-tape]; [gamma-hat#stage4-internals].
- **Attribution** — corpus self-correction. MISSING: no agent named.
- **Supersedes** — the merged citation.

### 2026-07-21 · Rejected addressing alternatives recorded so they are not re-proposed

Quantized addressing buys tolerance-deduplication at the cost of injectivity, plus a
grid artifact at every cell boundary. Ball or interval addressing relocates
non-transitivity into ball overlap and doubles every payload.

- **Evidence** — [representation-substrate#identity-exact].
- **Attribution** — corpus. MISSING: no agent named.
- **Supersedes** — nothing; recorded to prevent re-proposal.

### 2026-07-21 · Runtime cost is three-class, not one

Per-sample core work at microseconds to milliseconds; on-request spectral work at 0.1
to 10 seconds, cached per epoch; per-composition reference work at seconds to minutes,
calibration-only.

- **Evidence** — [named-formulas#cost-tiers]; [gamma-budget#budget].
- **Attribution** — corpus. MISSING: no agent named.
- **Supersedes** — the single "microseconds to milliseconds" runtime figure.

### 2026-07-21 · Rank-dependent applicability of the low-rank density-matrix slot is a compile-time predicate

Decided at the code-generation stage on the periodicity structure and site decoration.
The runtime cost that was the original objection no longer exists.

- **Evidence** — [gamma-hat#encoding-vocabulary];
  [compose-time-pipeline#stage-4].
- **Attribution** — corpus. MISSING: no agent named.
- **Supersedes** — the runtime-check framing.

### 2026-07-21 · Hardening the book against its own restructure

The restructure above was six bulk transformations — 56 pages moved, 11 process
artifacts collapsed, 25 formulas renamed, 19 rows retagged, about 97 graph edges
derived, about 40 path citations rewritten — and none had been verified. Six adversarial
skeptics were pointed at the transformations rather than at the physics, one per
transformation, briefed to find damage rather than confirm success. They found about
forty defects, all in the seam between what a transformation intended and what it did.

Both checkers were part of the defect. The structure checker validated only bracketed
identifiers matching four prefixes, leaving most of the corpus's identifiers unchecked;
its dated-anchor pattern skipped every dated timeline citation; and it never validated
the parenthetical that disambiguates the three entries sharing 2026-06-10. The data
checker captured formula arguments with an ASCII-only character class. The dependency-edge
criterion was documented as derivable and derived by nobody — deriving it found 33
missing edges, 325 to 358. And the file an agent reads first was checked by nothing and
was three restructures stale.

Three seeded values survived only in git history and were re-seeded into the reference
CSVs; three verifier-soundness gaps were named rather than left absent, because an
absent check reads exactly like a passing one.

- **Evidence** — [traps#practice]; [named-formulas]; [residual-machinery];
  [agent-contract#frontmatter]; commits `227e15a`, `29351de`, `b231e47`, `748967c`.
- **Attribution** — six adversarial skeptics, one per transformation; 66 skeptics on
  refutation. MISSING: none named.
- **Supersedes** — the assumption that a bulk transformation lands what it intends.

### 2026-07-21 · A pure-read differentiability tag split out of the no-derivative tag

The old single tag conflated "a pure read whose adjoint is the identity" with "an
integer output with no derivative" — opposite answers to the question the tag exists to
answer. **Eleven smooth analytic rows sat on it and therefore registered with no adjoint
at all**, because the build-verification gate exempts pure reads. Among them was the
alloy-lattice interpolation that the product page promises is directly optimizable
through baked gradients. Those eleven became direct-differentiable.

- **Evidence** — [named-formulas#diff-tags]; `data/registry-manifest.csv`, which now
  carries exactly one pure-read row; commit `00177b2`.
- **Attribution** — a registry retag pass. MISSING: no agent named.
- **Supersedes** — the single-tag legend.

### 2026-07-21 · The twelfth pure-read row, which the first retag missed

A chemical-potential reference table survived the first retag because "reference-cache
lookup" reads like a pure read. It takes temperature and pressure, so tagging it as a
pure read zeroed the chemical potential's temperature derivative and left a Maxwell
cross-derivative residual **vacuously satisfied**. The general rule: an implementation
detail (a cache) is not a mathematical one (an identity adjoint).

- **Evidence** — [named-formulas#diff-tags]; `data/registry-manifest.csv` row 69.
- **Attribution** — a second-pass audit. MISSING: no agent named.
- **Supersedes** — the first retag pass's coverage claim.

### 2026-07-21 · The fixed-point adjoint tag established as a *refinement* of the adjoint tag, with a conditioning gate

Every fixed-point row now runs the adjoint registration gate **plus** a
fixed-point-Jacobian conditioning check. Without that the tag would be strictly weaker
than the tag it refines, which is backwards: the ill-conditioned fixed point is the one
failure mode canon names for it, and the gradient it produces is *large and wrong*
rather than absent — a failure the adjoint gate structurally cannot see, because both
of its sides solve against the same bad Jacobian. It bites the charge-neutral Fermi
level (the derivative of the neutrality function with respect to the Fermi level is
flattest exactly in a wide-gap intrinsic semiconductor), the self-consistent charge
balance, and self-consistent phonons with soft modes.

- **Evidence** — [named-formulas#diff-tags]; `data/registry-manifest.csv` rows 5, 13,
  36; commits `4c1fb93`, `227e15a`.
- **Attribution** — a gap-closure pass. MISSING: no agent named.
- **Supersedes** — the unbounded-conditioning open item; and the reading in which the
  fixed-point tag was an *alternative* to the adjoint tag rather than a refinement of
  it.

### 2026-07-21 · Two rows shipped adjoint certificates for gradients that do not exist

Registry rows 46 and 50 have piecewise-constant outputs, so they pass the
vector-Jacobian versus Jacobian-vector consistency gate spuriously — on a zero gradient.
This established that a passing registration gate is not evidence of a correct adjoint
tag.

- **Evidence** — [residual-machinery#registration-gate]; [traps#practice];
  `data/registry-manifest.csv` rows 46, 50. PINNED: the source record carried
  "2026-07-2x"; commit `227e15a`, 2026-07-21.
- **Attribution** — corpus self-audit. MISSING: no agent named.
- **Supersedes** — the assumption that the registration gate is sufficient.

### 2026-07-21 · The differentiability tag that collided with a physical defect renamed

The tag spelled `DX` collided with the DX centre — the deep-donor configuration this
corpus analyses in aluminium-gallium-nitride and aluminium nitride — so searching for
the tag returned the physics and searching for the physics returned the tag. Eight rows
were retagged in the same pass; the crystal-structure-uniqueness row moved off the
renamed tag onto the relaxed tag, so it is no longer validation-only and its relaxation
is now part of the specification. The relaxed set grew from three rows to six. Two
further rows were renamed.

- **Evidence** — [named-formulas#diff-tags]; [traps#practice]; commits `00177b2`,
  `227e15a`.
- **Attribution** — the registry repair pass. MISSING: no agent named.
- **Supersedes** — the colliding tag spelling; and "surrogate" as the reading of the
  relaxed tag. **Superseded in turn** by this restructure, which replaces the whole
  serial family with English names (see 2026-07-31).

### 2026-07-21 · Five incompatible differentiability legends collapsed to one

The formula registry switched from restating the differentiability vocabulary to
linking it. The restatement is named as the cause of the five-legend divergence — the
same restatement-instead-of-citation mechanism this restructure is built to prevent.

- **Evidence** — [formula-registry]; [named-formulas#diff-tags]. PINNED: the source
  record carried only "before 2026-07-22"; commit `00177b2` ("Redesign the
  differentiability vocabulary; retag 19 rows", 2026-07-21) and `227e15a` are where the
  collapse lands.
- **Attribution** — legend reconciliation. MISSING: no agent or person named.
- **Supersedes** — the four divergent differentiability legends.

### 2026-07-21 · The mixed-output rule adopted

A row returning a real quantity *and* a discrete label is tagged by its continuous
component; a discrete label never drags a row to no-derivative. Without the rule the
same construction was tagged three different ways across three rows.

- **Evidence** — [named-formulas#mixed-outputs]. PINNED: the source record carried
  "before 2026-07-22"; commit `227e15a`, 2026-07-21.
- **Attribution** — the registry retag pass. MISSING: no agent named.
- **Supersedes** — the inconsistent tagging of the coordination-class, elastic-stability
  and structure-uniqueness rows.

### 2026-07-21 · The anchor-class field un-retired

It had been declared retired on the grounds that the always-cheap reframe collapsed the
two runtime paths. It did — but the column's live meaning is *what a row's value is
anchored against*, and that is the axis the consistency-pair obligation runs along.
Retiring a field several pages depend on is how a load-bearing distinction becomes
folklore.

- **Evidence** — [named-formulas#anchor-class]; `data/registry-manifest.csv`, 117 cheap
  against 15 faithful. PINNED: commit `49abc65` ("Un-retire `path`: it is declared dead
  in one place and load-bearing in four"), 2026-07-21.
- **Attribution** — corpus audit. MISSING: no agent named.
- **Supersedes** — the retirement of the field.

### 2026-07-21 · A restated enumeration drifted against its canonical ledger

The tolerance list restated on the residual-definitions page named ten symbols against a
ledger of sixteen. Recorded because it is the empirical basis for the one-home rule this
restructure is built on, and because it is the only *measured* instance of that drift in
the corpus.

- **Evidence** — [residual-definitions#error-budget]; ledger at
  [cert-obligations#tolerance-ledger]. PINNED: the source record carried "2026-07-2x";
  commit `68cc6fe`, 2026-07-21.
- **Attribution** — corpus self-audit. MISSING: no agent named.
- **Supersedes** — the ten-symbol restatement.

### 2026-07-21 · The tolerance-symbol check rebuilt to harvest its list from the ledger it checks

It had nine hard-coded symbols against a ledger of seventeen — a check reporting clean
on 53% coverage, with the shortfall recorded in a source comment and acted on by
nothing.

- **Evidence** — [cert-obligations#tolerance-ledger]; the data-agreement checker.
- **Attribution** — corpus tooling work. MISSING: no agent named; the source record
  dated this "approximately" 2026-07-21.
- **Supersedes** — the hard-coded nine-symbol list. **Note:** the stale description of
  the old behaviour survived on the obligations page after the rebuild, which is the
  restatement failure again.

### 2026-07-21 · A parser bug made the data checker report clean while pages invoked unregistered formulas

It scanned only backtick-quoted formula names, so `formula = <name>` arguments were
invisible. Widening the scan surfaced **17 findings immediately**.

- **Evidence** — commit `9b83b97` ("Consolidate the checkers onto the book; close the
  formula-arg blind spot"). PINNED: the source record carried "pre-2026-07-22".
- **Attribution** — self-reported. MISSING: no agent named.
- **Supersedes** — the narrower scan, and every clean run taken on its strength.

### 2026-07-21 · Two proposed energy-relaxation formulas merged into one row carrying both channels

The polar-optical and acoustic energy-relaxation channels became a single registry row.

- **Evidence** — [multiscale-state#slow-kinetics]; `data/registry-manifest.csv` row 73.
- **Attribution** — the retag pass. MISSING: no agent named.
- **Supersedes** — the two separate proposed formulas.

### 2026-07-21 · An embedded copy of registry rows had drifted from the CSV, and was removed

This established the registry manifest as the sole source for row content.

- **Evidence** — [multiscale-state]; `data/registry-manifest.csv`.
- **Attribution** — the reconciliation. MISSING: no agent named.
- **Supersedes** — the embedded row table in the state page.

### 2026-07-21 · Hydrogen redistribution range corrected 170-fold

Diamond interstitial hydrogen at 500 °C diffuses about **6 µm** in 1000 hours, not the
~1 mm previously carried. This changes whether hydrogen redistribution is a device-scale
or a near-surface phenomenon — which is to say, it changes which tier of the model owns
it.

- **Evidence** — [multiscale-state#slow-kinetics]; the diffusion barrier 1.7 eV and
  diffusivity ~1e-13 cm²/s at 500 °C. PINNED: commit `61e5c91` ("Three physics findings
  from the fleet, each verified by arithmetic before landing"), 2026-07-21; the source
  record carried only "2026-07".
- **Attribution** — the corpus reconciliation fleet. MISSING: no agent named.
- **Supersedes** — the ~1 mm estimate.

### 2026-07 (day MISSING, on or before 2026-07-21) · The emergence axiom refined

A quantity is emergent from a tier if and only if it is recoverable by coarse-graining
*on the same timescale and the same length scale*. The qualification admitted the slow
and macro tiers as first-class state without reintroducing the constraint-manifold
pathology, and made aging and device-scale operation representable at all.

- **Evidence** — [multiscale-state#emergence-axiom]; [unified-state#emergence].
- **Attribution** — the corpus reconciliation. MISSING: no agent named, and no day
  recorded. Git traces the text only to the book migration (`9c45ccb`, 2026-07-21), so
  2026-07-21 is an upper bound, not a pin.
- **Supersedes** — the unqualified rule that distributions and defect populations are
  emergent.

### 2026-07 (day MISSING, on or before 2026-07-21) · A contradiction between the state page and the level hierarchy resolved

The fourth Born-Oppenheimer level's claim to "its own irreducible state" is made
concrete as the macro continuum-field tier, with the full distribution kept emergent by
moment closure.

- **Evidence** — [born-oppenheimer-levels#l4-irreducible-state];
  [multiscale-state#macro-tier].
- **Attribution** — the corpus reconciliation. MISSING: no agent named; no day recorded.
- **Supersedes** — the stated contradiction between the two pages.

### 2026-07-21 · Serial page identifiers and eponymous formula names replaced by descriptive ones

38 page identifiers carrying chapter-and-number serials were renamed to descriptive
phrases. About 25 registry formulas were renamed by behaviour rather than by person —
for example, a vibronic coupling factor became the lattice-relaxation phonon quanta, and
a field-activated ionization rate became the impact-ionization coefficient. The token
`GAP` was found to mean three different things.

- **Evidence** — [traps#practice]; [conventions#naming]; commits `2f1d22f`, `be77d5b`.
  EVIDENCE-DIES: the old-to-new maps were kept in `retired-ids.csv` and
  `retired-names.csv`, both of which this restructure deletes. Before they go, the
  literature-name-to-behaviour-name mapping they carry is the *only* bridge from the
  published names (Fowler-Nordheim, Richardson-Dushman, Padovani-Stratton, Kane-Zener,
  Makov-Payne, Freysoldt, Lany-Zunger, Schottky-Mott) to the registry rows. One of them,
  the Makov-Payne correction, maps **ambiguously** onto two rows and needs a human
  decision rather than a lookup.
- **Attribution** — MISSING.
- **Supersedes** — the three-numbers-per-page identifier scheme. **Superseded in turn**
  by this restructure's rule that the filename is the identifier.

### 2026-07-21 · The implementation-language decision was reopened

Canon recorded it closed and prescribed four languages. It was not closed. The decision
is split at its real seam: the four-role polyglot *shape* stays closed, the *picks* are
open, and every language mention in the corpus is now a candidate carrying the
requirement it was chosen to satisfy — never a mandate. The requirement is the durable
part.

- **Evidence** — [forced-decisions#implementation-language];
  [forced-decisions#language-roles]; the emitted open-question register; commit
  `a0ff5be`.
- **Attribution** — Javier.
- **Supersedes** — the record that the decision was closed with four languages
  prescribed.

### 2026-07-21 · The certification result recorded honestly as four of six, not six of six

Six auditors were run over disjoint invariant classes — counts; signs, units and frames;
citations; completeness claims; topic ownership; and registry tags — each first
calibrated against a defect planted in a scratch copy that both checkers passed clean.
**Four of six found their exact plant. Two found a *different real defect* in the same
class and reported it as the plant.** That is a four-of-six gate and it is recorded as
one: their eye for the class is demonstrably real, but their live results are not
exhaustive. Both of the "wrong" finds were genuine — a glossary claim that a check
existed when none did, and a trap marked enforced at a page that did not state its rule.

They raised 54 findings. 66 skeptics tried to refute each one; **35 survived, 19 were
killed.** The survivors included a hole current written for the electron field, an
inverted Cowley-Sze pinning parameter, a stress sign contradicting both the stress
theorem and the page's own flow equation, two registry rows that could not form their
declared outputs from their declared inputs, and — repeatedly — values restated away
from their owners and drifted, including two that standing traps exist specifically to
forbid. About a third were residue from the same pass's own earlier edits, unswept.

Every checker was calibrated against a planted defect of its own class before any clean
run was believed: 15 probes, 15 fired, and two of the new checks missed on the first
attempt and were fixed before the result was accepted. That discipline caught a wrong
count in the pass's own commit message.

- **Evidence** — [agent-contract]; [traps#practice]; commits `d5a4974`,
  `68cc6fe`, `e95521c`.
- **Attribution** — six calibrated auditors and 66 refutation skeptics. MISSING: none
  named.
- **Supersedes** — nothing; it is a correction to how a result would otherwise have been
  reported.

### 2026-07-21 · A live physics sign error in a file named as a source for downstream research

The breakdown field was recorded as dropping ~20% from 300 K to 800 K. **It rises with
temperature** — the normalized temperature coefficient is positive, about +5e-4 per
kelvin for diamond and +7e-4 per kelvin for 4H silicon carbide. Ultra-wide-bandgap
breakdown *hardens* with temperature. The error came from conflating breakdown with the
mobility and velocity collapse, which does fall.

- **Evidence** — [accuracy-ledger#high-field-coefficients];
  `data/registry-manifest.csv` row 123. Literature: Hiraiwa & Kawarada, *J. Appl. Phys.*
  **114**, 034506 (2013). EVIDENCE-DIES: the erroneous file is `11.7`.
- **Attribution** — the 2026-07-21 corpus reconciliation. MISSING: no agent named.
- **Supersedes** — the ~20% drop, and the Pass C claim it descends from.

### 2026-07-21 · The thermal-conductivity accuracy regime re-anchored on the ledger

The observable catalog read ±10% for diamond and ±20% for the III-nitrides against a
2200 W/mK room-temperature anchor, while the accuracy ledger cited *that file* as its
source — so the disagreement pointed the wrong way. The ledger's per-temperature bands
are canonical.

- **Evidence** — [accuracy-ledger#kappa-battery]. EVIDENCE-DIES: `11.7:289-294`.
- **Attribution** — the 2026-07-21 repair pass. MISSING: no agent named.
- **Supersedes** — the ±10%/±20% bands and the claim that conductivity "drops from 2000
  to ~600 W/mK at 800 K".

### 2026-07-21 · A justification was fabricated; the conclusion it justified survived

A claim that a current-density-from-distribution formula was "already in registry" was
false — no such row existed or had existed. The emergent-moment conclusion survived;
only its justification was fabricated.

- **Evidence** — EVIDENCE-DIES: `11.5-deriv-high-field.md:556,603-605`.
- **Attribution** — the 2026-07-21 corpus reconciliation. MISSING: no agent named.
- **Supersedes** — the "already in registry" justification.

### 2026-07-22 · Re-audit of the calibration itself: the calibration did not do what canon said it did

Canon stated that the checker-checker "plants one defect per check", and "29 of 29
fired" was cited corpus-wide as the warrant for believing a green run. **Four of the
data checker's fourteen finding classes had no probe at all** — formula names,
tolerances, the glossary, and reference-data sources — and **nine structure-checker
checks likewise**, including duplicate identifiers, a missing required field, and a page
filed under the wrong chapter. Every one of those thirteen checks *worked*: all thirteen
new probes fired on the first attempt. The defect was never in the checkers; it was in
what the calibration established.

The repair is not the thirteen probes. Coverage is now **derived from the checker's own
source** and asserted at the end of every run, so a check nothing reaches fails the
calibration instead of passing silently. Verified by planting an unreachable check and
confirming the gate reports it.

- **Evidence** — [traps#practice]; [agent-contract]; commits `6b0c0e9`,
  `6cdf07c`, `86bb538`, `8571828`.
- **Attribution** — a re-audit briefed to treat every prior claim as unverified.
  MISSING: no agent named.
- **Supersedes** — the "one defect per check" claim and the 29-of-29 warrant; and the
  trap that stated the rule one level too low.

### 2026-07-22 · A distribution that adds up has not been checked

The cost-tier split was stated as 75/40/13/4 against an actual 76/40/11/5 — wrong in
three of four entries, and summing to 132 either way, so every check of the total
passed. The tally on the next line was correct precisely because a checker compared it
to the CSV.

- **Evidence** — [traps#practice]; commit `6b0c0e9`. EVIDENCE-DIES: the erroneous page
  is `4.4-computational-overview`, which this restructure deletes outright.
- **Attribution** — the re-audit. MISSING: no agent named.
- **Supersedes** — the 75/40/13/4 split.

### 2026-07-22 · A row of reference data had silently shifted its columns

An unquoted comma in a source cell split a transport-coefficients row into twelve fields
against a ten-column header. The "Added" column held the string `experimental` and the
"Modified" column held `1`. **Both checkers passed it**, because the cells they read by
name were still non-empty — they merely held the wrong values. That file outranks canon
for seeded coefficients. Table arity and date sanity are now checked.

- **Evidence** — [traps#practice]; [agent-contract#forbidden];
  `data/reference-data/transport-coefficients.csv`; commit `6cdf07c`.
- **Attribution** — the re-audit. MISSING: no agent named.
- **Supersedes** — the shifted row, and every clean run that passed over it. This is the
  origin of the escaped-pipe rule now in the agent contract.

### 2026-07-22 · Correction to the rewriting-soundness evidence

The sound rule set won on accuracy in 104 of 289 benchmarks — *against 135 where the
unsound set still won*. The corpus had quoted 104 without 135, which turned an even
accuracy trade into a win. The omitted half was the source's very next sentence.

- **Evidence** — [compose-time-pipeline#rewrite-admission]. Literature: Zhang et al.,
  PLDI (2023).
- **Attribution** — corpus self-correction. MISSING: no agent named.
- **Supersedes** — the one-sided 104-only citation.

### 2026-07-22 · A point-group gate was refusing trap density and subthreshold swing for every centrosymmetric host, including the minimum-viable-product system

Two registry rows — interface trap density and the trap-density-dependent subthreshold
swing — were removed from the non-centrosymmetry-gated polarization band. Neither
depends on inversion-symmetry breaking. The gate had been refusing them for **every
centrosymmetric host, diamond included**, and was circular, since a third row in the
same band consumes the trap density. The subthreshold-swing row was rebound to a
dielectric-layer predicate; the trap-density row was left on an always-true stub pending
a named predicate.

- **Evidence** — [applicability-classifiers#row-116-and-119]; the emitted open-question
  register; `data/registry-manifest.csv` rows 113–119; commit `edee529`.
- **Attribution** — the corpus gap-audit of that date. MISSING: no agent named.
- **Supersedes** — the whole-band gating of rows 113–119.

### 2026-07-22 · A checker harvested the wrong vocabulary and its "fix" corrupted four correct rows

A first version of the bundle-column check harvested only the nearby enumeration table,
reported four rows as defects, and the "fix" retagged them before either canon page was
read. **Both pages say the tag on those rows is deliberate** — they are
linear-response primitives feeding several bundles, not members of any one bundle. The
check was rebuilt to harvest from the field schema instead.

- **Evidence** — [traps#practice]; `data/registry-manifest.csv` rows 91–94; commits
  `74189be`, `287d2eb` ("Restore rows 91-94: L1 was never a defect, and my 'fix'
  corrupted them").
- **Attribution** — checker calibration; the corrupting fix and its reversal were the
  same author. MISSING: no agent named.
- **Supersedes** — the table-only harvest and the four incorrect retags.

### 2026-07-22 · A record type narrowed a set to a scalar at registration

The residual generator's bundle field was declared singular while **40 of the 134
registry rows carry two bundles**, so every dual-bundle row was silently narrowed when
it registered.

- **Evidence** — [residual-machinery#generator-record]; `data/registry-manifest.csv`.
  PINNED: the source record carried "2026-07-2x"; commit `5d096f0` ("Fleet round 2: …
  and a record type that narrowed a set to a scalar"), 2026-07-22.
- **Attribution** — corpus self-audit. MISSING: no agent named.
- **Supersedes** — the singular bundle field.

### 2026-07-22 · A dormant row's fixed-point gate is deferred, not passed

A dormant or anchored row has no fixed point, so there is no Jacobian to condition and
both gates pass trivially. This is the spurious-pass failure one level worse than the
piecewise-constant case, because the gradient is structurally absent rather than locally
zero. Generalized: any row whose provenance declares it dormant or anchored inherits the
rule.

- **Evidence** — [residual-machinery#registration-gate]; `data/registry-manifest.csv`
  row 122. PINNED: commit `5d096f0`, 2026-07-22.
- **Attribution** — corpus self-audit. MISSING: no agent named.
- **Supersedes** — the unqualified fixed-point reading of that row.

### 2026-07-22 · Compression plans carry per-plan error targets

Ranks are chosen to meet a stated target, not by structure alone, and the target enters
the per-residual budget through the tolerance-composition function.

- **Evidence** — [compose-time-pipeline#stage-4]; [cert-obligations#tolerance-ledger].
- **Attribution** — corpus. MISSING: no agent named.
- **Supersedes** — rank selection by structure alone.

### 2026-07-22 · A migration-barrier table whose criterion was wrong while its values were right

The header read "one year" as the onset criterion, which reproduces **none** of the
table's seven onset temperatures. All seven invert to a log-attempt-frequency-times-time
of about 30.6 — a hop time of order a second. Under the stated one-year criterion, 773 K
would sit well above the carbon-vacancy onset and the "on the verge of mobility at
500 °C" reading would be false.

- **Evidence** — EVIDENCE-DIES: `11.4-deriv-defects.md:91-98`. The corrected criterion
  must travel with the table when it is mined, or the values become unusable.
- **Attribution** — the 2026-07-22 adversarial re-audit. MISSING: no agent named.
- **Supersedes** — the one-year header criterion.

### 2026-07-22 · Two files stated two different closed forms for one registry row's saturation velocity

The bare square-root form evaluates to 4.0e7 cm/s for gallium nitride against the ~2e7
quoted beside it — a factor-of-two disagreement between a formula and its own worked
value. The Shockley form gives ~2.6e7 and is the surviving one.

- **Evidence** — `data/registry-manifest.csv`. EVIDENCE-DIES: `11.5-deriv-high-field.md:77`.
- **Attribution** — the 2026-07-22 adversarial re-audit. MISSING: no agent named.
- **Supersedes** — the bare square-root saturation-velocity form.

### 2026-07-22 · A worked example evaluated the exponent it had just retired, one line after declaring the new one

The diamond Caughey-Thomas example declared an exponent of one and then evaluated the
exponent-two form on the next line: the retag reached the prose and not the arithmetic
under it.

- **Evidence** — `data/reference-data/transport-coefficients.csv`, whose
  Caughey-Thomas exponent row **names this page as the superseded source**.
  EVIDENCE-DIES: `11.5-deriv-high-field.md:87-94`; the CSV's pointer to it dangles at
  cutover.
- **Attribution** — the 2026-07-22 adversarial re-audit. MISSING: no agent named.
- **Supersedes** — the exponent-two value for diamond.

### 2026-07-22 · Two errors partly cancelled into a plausible answer

In the gallium-nitride high-electron-mobility-transistor hot-carrier example, a
hundred-fold Joule-density fix was applied to the producing line and not to the
consuming one, and a *sheet* carrier density was used as if it were volumetric. Net
effect: a believable 386 K temperature rise against an actual ≈1930 K. The qualitative
conclusion — carriers hot enough to ionize below the breakdown field — was strengthened,
not weakened.

- **Evidence** — EVIDENCE-DIES: `11.5-deriv-high-field.md:320-332`.
- **Attribution** — the 2026-07-22 adversarial re-audit. MISSING: no agent named.
- **Supersedes** — the 386 K figure.

### 2026-07-22 · A project premise was refuted by its own numbers

The claim that ultra-wide-bandgap radiation tolerance is "uniformly one to two orders of
magnitude" better than silicon is contradicted three paragraphs above it by the same
page's own displacement-threshold table: against silicon's ≈21 eV, diamond (37–50 eV) is
about 2× better, aluminium nitride (~35) and gallium oxide (~25) are better, and
**gallium nitride (~20 eV) is at or below silicon**. Both halves of the claim — the
ratio and the word "uniformly" — were wrong.

- **Evidence** — [out-of-scope#material-limits]. EVIDENCE-DIES:
  `11.5-deriv-high-field.md:417`.
- **Attribution** — the 2026-07-22 adversarial re-audit. MISSING: no agent named.
- **Supersedes** — the "uniformly 1–2 orders of magnitude better" premise.

### 2026-07-22 · A checker-surface hole cost real findings

The data checker exempted the whole live working tree on a comment reading "frozen work
product" — lifting the rationale for frozen *audit* records one directory up, and
contradicting canon, which says specifications are explicitly *not* frozen. Extending
the surface to the specifications directory cost two findings across the three
specifications then present.

- **Evidence** — `restructure/salvage/2026-07-22-oracle-interface-research-request.md`;
  `restructure/salvage/README.md`.
- **Attribution** — an oracle-interface research request, recovered from an unmerged
  worktree. MISSING: no agent named.
- **Supersedes** — the blanket live-tree exemption.

### 2026-07-22 · Score-not-solve is a complexity-theoretic requirement, not a design preference

Verification is only cheap given a *complete* witness. A partial witness forces the
checker to solve for the rest, which returns it to the hard class. This is why the
oracle demands the full state including the electronic degrees of freedom — and
therefore why the operator must carry them.

- **Evidence** — [rationale#score-not-solve]; [product#score-not-solve].
  EVIDENCE-DIES: the argument is written out only in
  `journal/live/presentations/2026-07-22-cs-framing-outline.md`.
- **Attribution** — talk preparation, flagged by its own author as **brought in, not
  found in canon**, and offered as a candidate canon addition. MISSING: no agent named.
- **Supersedes** — nothing. Canon asserted score-not-solve without deriving it; this
  derives it.

### 2026-07-30 · Phase 1 — the whole corpus surveyed before a line of it was touched

Eleven read-only surveyors over 165,274 words. Nothing in the corpus was edited: the old
tree stayed byte-for-byte unchanged and both checkers still reported clean throughout.
The pass produced 1,525 disposition rows (413 keep, 489 delete, 407 mine, 207 move), 121
open questions, 128 log-worthy advancements — this file's raw material — and **89
contradictions, collected and deliberately not resolved**, which become the next
auditor's starting corpus. Nine rows failed to parse after repair: one gap marker and
eight blank spacers.

- **Evidence** — `restructure/GATE.md`; `restructure/merged/` (`rows.md`, `open.md`,
  `log.md`, `contradictions.md`, `notes.md`, `conflicts.md`), regenerable with
  `restructure/merge.py`; commit `d77ce27`.
- **Attribution** — eleven surveyor agents, one per corpus fragment, briefed read-only.
  MISSING: no model or version recorded for any of them. Javier directed the pass.
- **Supersedes** — nothing; it is the first full survey.

### 2026-07-30 · Citation enforcement provably stops at the book

One dangling reference was planted in the book pages, in the operator design tree, and
in the live specifications directory in a single run. **It fired only in the book.**
Separately, one retired formula name planted in the operator design tree and in the
specifications fired only in the former.

- **Evidence** — the structure and data checkers; `restructure/merged/notes.md`.
- **Attribution** — the Phase 1 structure survey. MISSING: no model or version recorded.
- **Supersedes** — the assumption that a green checker run covers the non-book strata.

### 2026-07-30 · The content hash does not cover frontmatter

Mutating a title into invalid YAML on a valid page left both the hash and every check
green. Frontmatter was entirely unguarded — and one chapter-11 page fails to parse as
YAML *today* while the structure checker reports the book OK.

- **Evidence** — planted probe, recorded in `restructure/merged/notes.md`.
- **Attribution** — the Phase 1 survey. MISSING: no model or version recorded.
- **Supersedes** — the belief that the content hash guarded the whole file. The
  disposition is to delete the content hash rather than extend it: the new contract
  validates frontmatter structurally and carries no hash at all.

### 2026-07-30 · The data checker does not compare page numerics to the reference CSVs

On a scratch copy: a numeric value in a chapter-11 table contradicting the reference
data — diamond room-temperature conductivity set to 9999 — produces **"data agreement
clean"**. A prose citation to a section that does not exist produces no finding. A
backticked reference to a nonexistent identifier produces no finding; the same reference
in brackets **does** fire. The checker is *alive* on those pages — a planted retired
formula name fired two finding classes — it simply never compares page numerics to the
canonical data.

- **Evidence** — planted probes on a scratch copy at commit `2af93d2`; recorded in
  `restructure/merged/notes.md`.
- **Attribution** — the Phase 1 survey. MISSING: no model or version recorded.
- **Supersedes** — the implicit assumption that a clean data-agreement run covers
  appendix values.

### 2026-07-30 · A canon field's definition is reachable only through a dead identifier

The residual machinery declares a layer field over a seven-layer compute graph and
defines it *solely* by citing a page identifier that **no page has**. The reference is
unbracketed, so the citation checker never sees it; verified by planting an obviously
nonexistent identifier in that exact position and getting a clean run. A bare
identifier followed by a section ordinal is silently skipped, so the corpus carries a
dangling reference in canon that no checker can see.

- **Evidence** — [residual-machinery#layer-dag]; planted probe recorded in
  `restructure/merged/notes.md`.
- **Attribution** — the Phase 1 survey. MISSING: no model or version recorded.
- **Supersedes** — the belief that section-coordinate citations are validated. **Order
  hazard, recorded because it is still live:** the definition must be mined into a
  surviving page *before* the chapter-11 tree is deleted, or the field becomes
  undefined in the new corpus.

### 2026-07-30 · Two grounding claims point at a research path that does not exist

The dynamics page grounds its nine-regime extraction table in a set of research files
that are not in the repository; the formula registry makes the same claim for registry
rows 1–87. The referents are in fact the chapter-11 derivations. Path citations are
checked by nothing.

- **Evidence** — [generic-dynamics#nine-regimes]; [formula-registry]; a filesystem
  search for the named path returns nothing.
- **Attribution** — the Phase 1 survey (two surveyors independently). MISSING: no model
  or version recorded.
- **Supersedes** — the belief that those grounding claims resolved. If the new pages
  repoint at real anchors, the ghost dies; if they are copied forward, the restructure
  inherits it with a new path.

### 2026-07-30 · The residual-category count is unchecked on its own owning page

The count check matches only a numeric-plus-noun pattern; the owning page states its
count in words and in bold digits. Corrupting the count **on the owning page** passes
clean; corrupting it on any citing page fires. The check was inverted with respect to
where it mattered.

- **Evidence** — the structure checker's count rule; calibration probe recorded in
  `restructure/merged/notes.md`.
- **Attribution** — the Phase 1 survey. MISSING: no model or version recorded.
- **Supersedes** — the belief that the nineteen-category count was checked.

### 2026-07-30 · A third live retired-identifier site, and it is inside canon

The cross-cutting rules page directs readers to a retired identifier prefix for
architectural decisions. The plan had located two such sites, both in an untracked file;
this one is in the book.

- **Evidence** — [cross-cutting-rules]. EVIDENCE-DIES: the retired-identifier map is
  `retired-ids.csv`, which this restructure deletes.
- **Attribution** — the Phase 1 survey. MISSING: no model or version recorded.
- **Supersedes** — the plan's count of two live sites.

### 2026-07-30 · The appendix generator catalog disagrees with the live registry on 18 of 87 carried rows

And the appendix's own translation legend mispredicts nine of them — including all three
fixed-point rows, which the legend maps to the plain adjoint tag but which are
canonically fixed-point-adjoint. Separately, the appendix's two architectural-rejection
rows are registry rows 103–104, while registry rows 88 and 89 are unrelated substantive
formulas. **Rows 1–87 do align, which is exactly what makes the two exceptions
dangerous.**

- **Evidence** — a mechanical diff of all 89 rows against `data/registry-manifest.csv`
  at commit `2af93d2`. EVIDENCE-DIES: the appendix is `11.8-deriv-generator-catalog`.
- **Attribution** — the Phase 1 survey. MISSING: no model or version recorded.
- **Supersedes** — the appendix's blanket claim that all its row numbers are
  snapshot-local.

### 2026-07-30 · Serial identifiers were concealing two-thirds of the convergent findings

Before the survey's own serial open-question identifiers were renamed to descriptive
slugs, the convergence detector saw 4 findings reached independently by more than one
surveyor. After renaming, it saw **13**. A serial identifier collides by construction,
so a genuine second sighting is indistinguishable from a numbering clash. This is a
second, independent argument for descriptive naming, beyond readability — and it was
measured, not asserted.

- **Evidence** — `restructure/GATE.md`.
- **Attribution** — the Phase 1 gate. MISSING: no model or version recorded.
- **Supersedes** — the count of 4 convergent findings. It also supersedes the survey's
  own work product: 38 serial open-question identifiers had reappeared in a fresh
  artifact, reproducing the very scheme the corpus retired on 2026-07-22.

### 2026-07-30 · Twenty shared disposition targets checked pairwise: zero duplicates

Every one carries genuinely different facts. The dominant pattern is an appendix
derivation (the mathematics) landing on the same anchor as its registry entry (the
composition), which is the intended convergence rather than a collision.

- **Evidence** — `restructure/GATE.md`.
- **Attribution** — the Phase 1 gate. MISSING: no model or version recorded.
- **Supersedes** — the assumption that shared targets implied duplication.

### 2026-07-30 · The section-ordinal citation coordinate is unchecked into 57% of the corpus

The checker skips resolution when the target page has no numbered headings, and 33 of 58
pages have none. A citation to a section number far beyond any that exists passes into
any of them. Found by a planted probe, not by reading. The original argument against
ordinals — that they rot when a heading is inserted above them — was true but minor
compared to this.

- **Evidence** — `restructure/GATE.md`; the structure checker's citation resolver.
- **Attribution** — the Phase 1 survey. MISSING: no model or version recorded.
- **Supersedes** — the stated rationale for removing section ordinals, which understated
  the problem. The disposition is declared anchors, which cannot silently fail to
  resolve.

### 2026-07-30 · The citation split is 47% unchecked, not about 40%

315 bracketed citations against 289 backticked, measured against the real 58-identifier
set. The worst page carries 4 checked against 42 unchecked — **91% unchecked** — on a
page that claims the checkers hold it to the same rules as any other.

- **Evidence** — `restructure/GATE.md`.
- **Attribution** — the Phase 1 survey. MISSING: no model or version recorded.
- **Supersedes** — the estimate of about 40%.

### 2026-07-30 · A third homeless type: the crystal

Zero definitions against eight uses of a crystal-and-environment signature across five
pages — and that signature is on every registry row, every coupling channel, and every
residual generator.

- **Evidence** — `restructure/GATE.md`; `data/registry-manifest.csv`.
- **Attribution** — the Phase 1 survey. MISSING: no model or version recorded.
- **Supersedes** — the previous inventory of two homeless types.

### 2026-07-30 · A new defect class: the dangling quotation

The state page quotes the unified-state page as classifying defect populations as
"emergent — coarse-grainings of the state", and argues at length against it. **That
string appears nowhere in the page it quotes.** Its only occurrence anywhere in the
corpus is inside the quotation of it. A citation checker cannot see this class at all,
because the citation resolves; it is the quoted content that does not exist.

- **Evidence** — `restructure/GATE.md`; corpus-wide string search.
- **Attribution** — the Phase 1 survey. MISSING: no model or version recorded.
- **Supersedes** — nothing; this class was not previously known.

### 2026-07-30 · Delimiter-sensitive formats cannot carry physics — the third instance of one class

Literal vertical bars in bra-kets and norms split sixteen disposition rows into as many
as eleven columns against a six-column header. This is the same failure as the corpus's
own reference-data arity bug and as the Phase 1 merge tooling's. Three independent
appearances of one class is a property of the format, not of the authors.

- **Evidence** — `restructure/GATE.md`; `restructure/merged/conflicts.md`;
  [agent-contract#forbidden], which now requires escaping and checks table arity per
  page.
- **Attribution** — the Phase 1 survey. MISSING: no model or version recorded.
- **Supersedes** — the assumption that the earlier CSV arity bug was an isolated defect.

### 2026-07-30 · Structural gate decisions

Four decisions taken at the Phase 1 gate. The restatement page — whose own charter was
to restate the rest of the corpus — is deleted outright, with its 25 original facts
routed to the pages that own what they cost, and a generated cost-and-complexity view
emitted in its place; a page whose charter is restatement cannot be made
non-duplicating by editing it. The density-matrix budget page merges into the
density-matrix page. The properties page and the typed-compositions page stay separate,
with the coverage claim between them becoming machine-checked. And all four nomenclature
defects are renamed in one pass, with the new names proposed before they land.

- **Evidence** — `restructure/GATE.md`; `restructure/RENAMES.md`.
- **Attribution** — Javier, on surveyor escalations. Every surveyor escalated rather
  than guessing.
- **Supersedes** — the restatement page and the separate budget page; the four serial or
  overloaded vocabularies named below.

### 2026-07-31 · The vocabulary recovery — nine tag families named, and one recovered from git because canon defined it nowhere

Every corpus-invented serial vocabulary was mapped to English names. **Not one required
invention**: every family already had English names written beside the serial, so the
serials were decoration over names that were already there, and the only thing they
contributed was collision potential.

The exception is the registry's provenance vocabulary, which appears on all 132 rows and
which **canon defines nowhere**. Its only gloss sat on a page banner-marked as a retired
snapshot whose *other* legend is known-wrong, so it could not be trusted. It was
recovered instead from two independent paths that agree: from usage — source cells
naming within-page sections of the defects and non-equilibrium derivations — and from
git history, where a 2026-05-27 commit migrating "7 current-session research streams"
names each one. The two agree exactly on the two streams usage can determine, which is
what licenses trusting history for the rest. The registry uses only five of the seven
because the sixth *is* the reconciliation of the other five and the seventh was an
architecture amendment, not a formula source.

The families and their names:

| family | becomes |
|---|---|
| research provenance | observable-catalog · crystal-structure-prediction · defects-and-interfaces · non-equilibrium-high-field · residual-loss-methodology |
| differentiability | read · direct · adjoint · fixpoint-adjoint · relaxed · none |
| evaluation cost | microseconds · milliseconds · seconds · minutes |
| training cadence | per-step · per-batch · per-epoch · on-demand |
| observable bundles | electronic-structure · phonon · transport · defect-resolved · surface-resolved · interface-resolved · mechanics · thermodynamics · non-equilibrium-operating · static-validity · degradation · linear-response-primitive |
| substrate clusters | vocabularies · registered-generators · sidecars · evidence · content-addressing · selected-subsets · sparse-masks |
| Born-Oppenheimer levels | quantum-electronic-substrate · born-oppenheimer-surface · equilibrium-statistics · non-equilibrium-kinetics |
| dressing layers | substrate · one-shot-dressing · iterative-dressing · property-machinery |
| missing-data marker | UNSEEDED |

Three consequences worth recording separately. **Cost and cadence were two vocabularies
sharing one alphabet**, and they had already mis-bound: an iterative residual is
`minutes` by cost and `per-epoch` by cadence, which under serials read as two different
numbers on the same scale. They belong to different libraries — the oracle owns no
training loop. **The twelfth bundle value was never a bundle**: four rows carried a
Born-Oppenheimer level in the bundle column because they are level-one primitives
feeding several bundles, and that is the exact collision that corrupted those four rows
on 2026-07-22. Named as `linear-response-primitive`, the collision stops being
representable. And **the provenance column joins the vocabulary check**: the data
checker had been checking four registry columns and skipping this one, which is how an
undefined vocabulary survived on 132 rows.

The dressing "Layer 3" is deleted rather than renamed. It is the neural operator, which
lives in its own library — calling it a layer of the oracle is a category error the
numbering concealed.

- **Evidence** — `restructure/VOCABULARY.md`; `restructure/RENAMES.md`;
  [agent-contract#vocabulary] and the retired-vocabularies block in its schema;
  `data/registry-manifest.csv`; commits `dfad72b` (2026-05-27, the origin) and `6d83b6a`
  (the recovery).
- **Attribution** — a vocabulary recovery pass; Javier signed off the names before any
  page was written. MISSING: no model or version recorded for the pass.
- **Supersedes** — every serial vocabulary listed above, and the corpus's dependence on
  a footnote warning that one tag was not inside the numeric series it appeared to
  belong to.

### 2026-07-31 · Eponyms are kept; serials and symbols are not

The rename targets tokens that are contentless or ambiguous, not standard technical
vocabulary. A Born-Oppenheimer surface names one thing unambiguously and keeps its name;
spelling out a Greek letter as "standard deviation" removes a symbol from a namespace it
should never have shared with the physics. The test is whether a reader could bind the
name to the wrong object — not whether a person's name appears in it. Where a name does
shadow a second quantity, the person moves into the source cell as an alias, which is
where a literature search starts anyway.

- **Evidence** — [agent-contract#vocabulary]; `restructure/VOCABULARY.md`.
- **Attribution** — the vocabulary pass, applying the corpus's own pre-existing eponym
  rule. MISSING: no model recorded.
- **Supersedes** — the reading in which removing serials would also have removed
  eponyms.

### 2026-07-31 · Overloaded words separated, with the blast radius measured

Nine tokens carried two to six meanings each. The heaviest: a coverage mask meaning
three different things that **multiply into one loss**, so conflating them is wrong and
green; "graph" meaning both the acyclic physics graph, whose topological order *is* its
evaluation order, and the page graph, which is **cyclic and must never be closed over**;
and "source" meaning both a provenance citation and a closed enumeration, on two records
the factory reads together. Thirteen further candidates were checked and rejected as
false positives.

- **Evidence** — `restructure/VOCABULARY.md`; [agent-contract#vocabulary], whose
  owned-terms block is the enforced list.
- **Attribution** — the vocabulary pass. MISSING: no model recorded.
- **Supersedes** — the single-token readings of each.

### 2026-07-31 · The structure: three libraries, journals of sections of pages, and the filename is the identifier

The specification is a set of journals; a journal is one cohesive corpus on one topic,
made of sections, made of pages; a page is one file and its filename is its identifier.
Journal and section are read off the path and never restated in frontmatter, because a
field that restates the path can disagree with it. Headings are addressed by declared
anchor, and there are no section ordinals. Ownership is the anti-duplication mechanism:
a topic appears in exactly one page's `owns` across the whole corpus, and no page may
own only its own name — **31% of the previous corpus failed that, which is why the
invariant could never fire there.**

- **Evidence** — [agent-contract#shape]; [agent-contract#frontmatter];
  [agent-contract#frontmatter]; [agent-contract#citing].
- **Attribution** — Javier, on the Phase 1 disposition.
- **Supersedes** — the eleven-chapter book with serial page identifiers, display tags
  and content hashes; the authority order and frozen-directories rule of 2026-07-16,
  which the ownership model replaces; and the hand-maintained reverse-edge and
  open-question registers, which are now emitted.

### 2026-07-31 · The enforcement was built before a single page was written

The agent contract and the checker are the same artifact: the machine-readable block at
the end of the contract is what the checker parses, so the document and the enforcement
cannot disagree. Changing a rule means changing that block. A partial mode was added so
that builders writing into a deliberately cyclic page graph are not blocked by citations
into pages nobody has written yet; the strict form is the conductor's final gate. The
checker also asserts its own coverage, so a check nothing reaches fails instead of
passing silently.

- **Evidence** — [agent-contract#schema]; commits `dbd0c2a` ("Build the enforcement
  before writing a single page") and `85da768` ("Give the checker a partial mode, and
  catch it losing sight of itself").
- **Attribution** — Javier, directing the restructure.
- **Supersedes** — the practice of writing the corpus first and mechanizing the rules
  afterwards, which produced the 2026-07-22 calibration finding.

### 2026-07-31 · The provenance sweep: what the seeded numbers actually rest on

179 rows across the five reference-data CSVs. **24 carry no author-year and no
persistent identifier.** These are the corpus's canonical seeded values, and they
outrank canon pages in the authority order. Not all 24 are defects; they fall into four
classes.

**Five are working as designed** — declared gaps and derived quantities: the
aluminium-nitride hole mobility is an explicit refusal, its Caughey-Thomas parameter set
a declared acquisition task, its Fröhlich coupling derived from inputs it cites, the
β-gallium-oxide mass density crystallographic, its Caughey-Thomas set confirmed a
genuine gap by the Wave-2 audit. This is the unseeded mechanism doing its job before it
had a name.

**Four are textbook constants** — diamond mass density, static dielectric constant,
cohesive energy and lattice constant. Defensible, but a corpus facing a government audit
should name the reference rather than say "standard": a value with no named source is
indistinguishable from one nobody checked.

**Nine are internal pointers** — the source cell points at another part of this corpus
rather than at literature. Each needs one hop to a real citation. This is the class the
sweep exists for.

**Five state a method where a source belongs.** A method is not a provenance:
"three-phonon transport extrapolation" says how the number was made, not what it can be
checked against.

The rule this establishes: **a value carried forward because it has always been there is
exactly the failure the 2026-06-10 clearance made.** A row whose provenance does not
resolve is not wrong — it is *unknown*, and the corpus has a word for that.

- **Evidence** — `restructure/PROVENANCE.md`; `data/reference-data/`; commit `2e4e551`
  ("Ask what the seeded numbers rest on, and find four different answers").
- **Attribution** — a provenance sweep, with three lead agents (one per material family)
  whose reports are in `restructure/leads/`. Every claim was re-verified against the
  CSVs before being written to the register. MISSING: no model or version recorded.
- **Supersedes** — the assumption that the reference CSVs were fully sourced because
  they were canonical.

### 2026-07-31 · Four rows never needed literature — they needed the corpus to look at itself

The aluminium-nitride Fröhlich coupling derives from two rows of the same corpus's
phonon-frequency file, both citing Davydov with year and identifier. The
aluminium-nitride bulk modulus is derivable from elastic constants already in the same
CSV. The β-gallium-oxide mass density's crystallographic citation sits in the audit file,
unpropagated. The β-gallium-oxide Caughey-Thomas gap has its substantiating sentence in
the audit's own gap register.

- **Evidence** — `restructure/leads/nitrides.md`;
  `restructure/leads/gallium-oxide.md`; `data/reference-data/phonon-frequencies.csv`;
  `data/reference-data/elastic-constants.csv`.
- **Attribution** — the material-family lead agents. MISSING: no model recorded.
- **Supersedes** — the classification of these four as needing external acquisition.

### 2026-07-31 · Rows resolved to named primary literature

The aluminium-nitride Debye temperature recovered in full: Wang, Zhao, Jin, Li, Yang, Hu
& Wang, "Debye temperature of wurtzite AlN determined by X-ray powder diffraction",
*Powder Diffraction* **29**(4), 352–355 (2014), DOI 10.1017/S0885715614000542 — Rietveld
refinement of room-temperature powder diffraction, yielding 971 K, exactly the
parenthetical the CSV carried. The β-gallium-oxide best experimental electron mobility
traces to four named papers, three matching exactly. Diamond's lattice constant resolves
to Hom, Kiszenick & Post, *J. Appl. Cryst.* **8**, 457 (1975) at 3.566986 Å, from which
the mass density follows exactly; the maximum phonon energy to Solin & Ramdas, *Phys.
Rev. B* **1**, 1687 (1970) for the zone-centre value and Kulda et al., *Phys. Rev. B*
**66**, 241202 (2002) for the true maximum; the indirect gap to the Clark-Dean-Harris
lineage, *Proc. R. Soc. A* **277**, 312 (1964); the graphite-referenced formation energy
to Berman & Simon, *Z. Elektrochem.* **59**, 333 (1955).

- **Evidence** — `restructure/leads/nitrides.md`, `restructure/leads/diamond.md`,
  `restructure/leads/gallium-oxide.md`; `data/reference-data/`.
- **Attribution** — the three material-family lead agents. MISSING: no model recorded.
- **Supersedes** — the author-only and unattributed source cells for each row.

### 2026-07-31 · A declared absence contradicted by a citation in the same file

One transport-coefficients row states that aluminium-nitride conductivity is theory-only
with **"no measurement above 500 K on single crystals"**. Another row of the same file
cites **Slack, *J. Phys. Chem. Solids* 48, 641 (1987)** for the room-temperature value —
and that paper reports measurements to far above 500 K.

This is the opposite failure from an unsourced value: **a refusal to seed, on grounds the
corpus's own citation contradicts.** An unnecessary refusal costs coverage silently, and
unlike a wrong value nothing will ever fire on it. The aluminium-nitride Caughey-Thomas
parameter set may be the same shape — the lead found a named source that is an open
preprint, so a gap the corpus has carried as paywalled since 2026-06-10 appears closable.

- **Evidence** — `restructure/leads/nitrides.md`;
  `data/reference-data/transport-coefficients.csv` rows 24 and 43.
- **Attribution** — the nitrides lead agent. MISSING: no model recorded.
- **Supersedes** — the declared absence, and the certificate refusal resting on it.
  **Not adjudicated here** — the refusal is not lifted by this entry, only contradicted.

### 2026-07-31 · The diamond conductivity rows carry four separate problems

The two high-temperature rows (620 W/mK at 773 K, 450 W/mK at 1100 K) both cite an audit
as their provenance.

1. **The ledger and the CSV describe the same numbers differently.** The ledger
   attributes all three temperatures to named theory papers; the CSV declares two of them
   theory-interpolation. Both are canon; they simply disagree about what *kind* of number
   this is.
2. **A citation appears to name the wrong material.** Broido, *Appl. Phys. Lett.* **91**,
   231922 (2007) is, by its published abstract, about **silicon and germanium**. The
   diamond paper from that group is Ward et al., *Phys. Rev. B* **80**, 125203 (2009).
   The corpus records the 2026-06-10 re-audit as having missed *a mis-citation*; this is
   a candidate for it, or for a second one on the same quantity.
3. **The overprediction is probably named in the corpus's own cited paper.**
   Feng, Lindsay & Ruan state that three-phonon scattering alone overpredicts diamond
   conductivity by 31% at 1000 K, and that including four-phonon scattering reduces the
   prediction by 30% there. The corpus records that re-audit as having missed *a
   conductivity overprediction*. The two are very likely the same thing.
4. **A numerical confusion trap.** That paper's widely-quoted "2200 → 1400 W/mK at room
   temperature" figures are for **boron arsenide, not diamond** — and they collide
   numerically with diamond's own ~2200 W/mK one paragraph away. Anyone re-deriving the
   diamond anchor from this paper can land on the right number for the wrong material and
   see nothing wrong.

Underneath all four: **the provenance is an audit the corpus itself records as having
missed a conductivity overprediction, a mis-citation, and a fabricated citation on that
exact quantity.** That is not a provenance chain, it is a loop. The corpus's own rule
applies — re-verify values, never verdicts; a later value-level correction supersedes an
earlier clearance, and inheriting false confidence is the failure mode the rule exists to
prevent.

The single highest-value acquisition is Olson et al., *Phys. Rev. B* **47**, 14850
(1993) — the only primary measurement spanning 170–1200 K, on which both
high-temperature rows depend, and which could not be retrieved.

- **Evidence** — `restructure/leads/diamond.md`; `restructure/PROVENANCE.md`;
  `data/reference-data/transport-coefficients.csv`; [accuracy-ledger#kappa-battery].
- **Attribution** — the diamond lead agent; re-verified against the CSVs. MISSING: no
  model recorded.
- **Supersedes** — the 2026-06-10 clearance of these rows, as a *warrant*. The values
  themselves are not adjudicated here.

### 2026-07-31 · Two diamond rows where "no source found" is the honest answer

The static dielectric constant and the Debye temperature. Neither is a minor row: the
first feeds image-force lowering, the second sets the four-phonon validity window that
the 773 K conductivity row depends on. The Debye temperature additionally carries ±50 K
against a literature spread of 1860–2230 K by method — **a stated uncertainty narrower
than the disagreement between methods.**

- **Evidence** — `restructure/leads/diamond.md`; `data/reference-data/`.
- **Attribution** — the diamond lead agent. MISSING: no model recorded.
- **Supersedes** — the "standard value" and unreferenced-database provenances. Both
  become unseeded and open questions rather than values carried because they have always
  been there.

### 2026-07-31 · One value whose provenance trail points at a different material

Diamond's cohesive energy, 7.37 eV/atom ± 0.05. The standard tabulated 7.374 traces to
**graphite**; diamond's figure is 7.346. Both sit inside the stated band, so the *value*
is defensible either way — but the *provenance* may be another material's number.

- **Evidence** — `restructure/leads/diamond.md`; `data/reference-data/`.
- **Attribution** — the diamond lead agent. Registered, not adjudicated. MISSING: no
  model recorded.
- **Supersedes** — the unattributed source cell.

### 2026-07-31 · The β-gallium-oxide displacement threshold becomes unseeded

The CSV names an appendix as its source; the appendix states the value as a bare
parenthetical **with no citation**; the row's provenance type reads "literature-review"
and no literature is ever named. A value with no external provenance, laundered into
canonical status. Deleting the appendix removes even the appearance of a source.

The lead sweep found the literature's actual shape is a five-site table plus a
directional map, not a scalar — so the row is not merely unsourced, it is the wrong
*type* of object for what the literature reports, which has consequences for the
displacement-damage formula that consumes it.

- **Evidence** — `restructure/leads/gallium-oxide.md`; `restructure/PROVENANCE.md`;
  `data/reference-data/material-constants.csv`. EVIDENCE-DIES: the named source is
  `11.5-deriv-high-field`.
- **Attribution** — the gallium-oxide lead agent. MISSING: no model recorded.
- **Supersedes** — the value's canonical status. It is unseeded, and an open question.

### 2026-07-31 · Two nitride mass densities do not reconcile with the accepted crystallographic cell

The aluminium-nitride figure was taken from a database that lists two densities, and the
corpus took the one that does not close against the cell. The gallium-nitride figure is
inconsistent with the accepted cell by about 1%. Both are secondary-source-only. The
corpus already has a precedent for the clean path: derive the density from the
crystallographic cell and the atomic masses, and cite the cell.

- **Evidence** — `restructure/leads/nitrides.md`;
  `data/reference-data/material-constants.csv`.
- **Attribution** — the nitrides lead agent. MISSING: no model recorded.
- **Supersedes** — the database-sourced densities as canonical values.

### 2026-07-31 · The audits stratum holds citations the reference data still lacks

Citations that would resolve several unsourced reference rows were already inside the
corpus — sitting in audit records and never propagated to the CSVs that need them. The
gap was distribution, not acquisition.

- **Evidence** — commit `8c6ea95` ("The audits stratum holds citations the reference
  data still lacks"); `restructure/PROVENANCE.md`.
- **Attribution** — the provenance sweep. MISSING: no model recorded.
- **Supersedes** — the assumption that an unsourced CSV row implied the source was not
  in the repository.

### 2026-07-31 · Cutover: what the deletion of the old trees costs this record

The chapter-11 appendix derivations and the whole `journal/` tree are deleted. Their
*content* is mined into the new corpus where a disposition row says it survives; their
*record of having been corrected* is not, because pages in the new corpus carry no
history at all. **Thirty-seven** entries in this log have evidence that lives, wholly or
partly, only in those trees; each is marked `EVIDENCE-DIES` above.

A further exposure is not marked, because it is not yet decided: **twenty-nine** entries
cite `restructure/` — the survey output, the provenance register, the lead reports and
the gate record. Whether that directory survives cutover has not been stated anywhere.
If it does not, those twenty-nine lose their evidence too, and the whole Phase 1 and
provenance record becomes unsupported. **This log's own evidence base therefore depends
on a decision nobody has taken.**

Four of those are worse than the others, because the dying page is cited from an
artifact that **outranks canon**: two registry rows cite chapter-11 sections as the
justification for their signatures, one reference-data row names a chapter-11 page as
its source, and the retired-name maps are the only bridge from published literature
names to the corpus's behaviour-based formula names. Nothing checks a citation from a
data file into a page, so these will dangle silently rather than fail.

- **Evidence** — `restructure/GATE.md`; `restructure/merged/notes.md`;
  `data/registry-manifest.csv` rows 48 and 50;
  `data/reference-data/material-constants.csv`.
- **Attribution** — the Phase 1 survey, which found the exposure; Javier, who took the
  deletion decision.
- **Supersedes** — nothing. Recorded so that an auditor tracing a value into a page that
  no longer exists finds out from this log why, rather than concluding the value was
  never sourced.


