# Cohesion audit — principal's register

Written 2026-07-31 at the point the fleet hit a hard session limit. Eight findings files
are on disk in `audit/findings/` — 126,901 words, **223 structured findings**. **This
file is the synthesis, which existed nowhere else.** It is the principal's judgement:
severity ranking, the cross-cutting defect classes, the correction split, and what is
owed.

**None of it has been grounded yet.** A separate pass verifies every quoted claim
against the live corpus by content; until that lands, treat a finding here as a claim
about the corpus rather than a fact about it. See `audit/GROUNDING.md`.

Read this first. Read the per-subject files for evidence.

---

## Status

| | |
|---|---|
| Subjects delivered | compilation (12 findings, closed) |
| Subjects with substantial drafts | laws (15+), seams (16), certification, registry, state, values |
| Undergraduate reports returned and verified | 22 |
| Findings established | 246 structured, across nine subjects |
| Adjacent-contradiction class | **swept complete: 45 of 45 pages, 41 findings, 18 STRONG** |
| Corpus gates | still green; nothing in this audit changed `journals/` or `data/` |
| Stopped by | session limit, not by completion |

**Nothing here has been applied.** The audit was read-only by design.

---

## The nine defect classes

Ranked by how much of the corpus each touches. The classes matter more than the
individual findings, because the corpus will keep generating instances of them until
the class is closed.

### 1 · A claim that resolves but is not true — the dominant class

Every existing checker validates *links*: a citation resolves, a topic has one owner,
a table's rows match its header. **Not one asks whether a claim is true.** The audit's
single largest result is that this gap is not theoretical — it is where nearly every
finding lives. A sentence stating the opposite of the physics passes every gate in
this repository today.

**The purest instance, and it is one grep.** `formula-registry.md:49` declares the
signature field holds *"typed inputs to output, **with units**"*. **Zero of 134 rows
carry a unit.** The schema states a property the data does not have, nothing checks it,
and the consequence is downstream: without units the signature column stops being a
namespace, which is how eight bare-token collisions arise — including a capture
coefficient in cm³/s whose only other appearance is an Auger coefficient in cm⁶/s, the
one row that must not consume it.

### 2 · A guarantee asserted rather than constructed

- The **GENERIC degeneracy conditions** are claimed "identically zero by construction".
  Never constructed. The generator's signature never sees `E` or `S`; antisymmetry and
  positive-semidefiniteness do not imply either degeneracy condition.
- **Obligation 9** is vacuous on all six rows it governs — its four clauses presuppose
  a fitted artifact, and a relaxation is a deterministic function.
- **`bound`**, one of three tokens in the evolver obligation vocabulary, has no referent
  anywhere and no theorem in the named literature.

### 3 · A tripwire disabled by the very assertion that needed checking

`Degeneracy` is removed from the training loss on the ground that it is identically
zero by construction. That premise is false in general and **provably false** for the
Magnetic and Chemical rows — an impossibility proof shows no symmetric operator can
produce the Landau-Lifshitz damping term the corpus writes while satisfying
`M·δE/δx = 0`. The one check that would have caught this is switched off by the claim
that needed checking. What remains is a cert check written `≈ 0` with **no tolerance
anywhere in the corpus**.

### 4 · "Enforced" as a prose claim with no mechanism

**Measured, not inferred: `traps.md` carries 45 `— enforced` markers, and no checker
reads the marker.** `grep -rn "enforced" tools/*.py` returns two hits, both comments
about an unrelated citation rule. Control: the same grep pattern returns 17 hits for
`owns`, a marker the checkers do read — so the sweep fires.

Consequences already found: a trap marked **enforced** is violated by canon in three
places, including the tolerance ledger; the gauge trap is marked **enforced** and both
its anchors are the text found defective. The corpus has a vocabulary for asserting a
hazard is handled and nothing connecting the assertion to a check.

**Proposed gate:** every `enforced` marker either names a checker probe or is
downgraded to `advisory`. This is mechanically checkable and would fire 45 times today.

### 5 · Wrong equations, with a computable direction of wrongness

Distinct from under-specification and far more urgent.

- **Carrier continuity** is dimensionally inconsistent (missing `1/q`, sides differ by
  6.2×10¹⁸) *and* sign-flipped. A correct trajectory scores `‖(2/q)∇·J‖²`; a frozen
  trajectory scores **four times better in the transport-dominated limit** (4.0008 at
  the operating point — asymptotic, not exact); **the loss minimiser is reversed
  transport.** The spurious term is **5.06×10³×** the source scale it exists to teach —
  measured against *both* denominators, since the corpus's own Chynoweth parameters make
  avalanche and recombination comparable at 1 MV/cm rather than orders apart.
  *An earlier draft of this register said ~10⁴, which used the weaker denominator alone.*
  The ratio has a **doping-independent closed form** — `v_sat·τ/L` against recombination,
  `1/(α·L)` against impact ionisation — so it **grows linearly under mesh refinement**,
  and the one knob that would shrink it is the one the Péclet argument requires to stay
  fine. A ten-form control sweep found the corpus states carrier continuity **exactly
  once**, so there is no correct statement elsewhere and the loose-gloss reading is
  unavailable.
- **The gauge derivation does not support its own conclusion.** `generic-dynamics:186-187`
  derives transversality from the "remaining **time-independent** gauge freedom" of the
  Weyl gauge. That cannot work by its own adjective: `A → A + ∇χ(r)` shifts `∇·A` by a
  time-independent `∇²χ`, while the obstruction `∂_t(∇·A) = −4πcρ` is time-dependent, so
  transversality holds at one instant only. What is described is Coulomb gauge with the
  non-dynamical scalar potential eliminated. **The partition is correct; the derivation
  of it is not** — a one-sentence fix, not a scope decision.
  *An earlier draft of this register claimed Gauss's law was violated identically and
  that a static applied field was homeless. Both were over-claims and are withdrawn:
  the longitudinal sector is owned by the Hartree and ion–ion channels, which is the
  standard nonrelativistic-QED partition, and a uniform field lives in the k=0 mode of
  a transverse `A`, where transversality is vacuous.*
- **The `A` slot's identity is not fixed.** `unified-state:37` types it "**external** EM
  vector potential, while `residual-definitions:79` gives it an equation of motion,
  `generic-dynamics:189` puts its energy in the system energy, and `:201` has minimal
  coupling read it. An external field is prescribed, not evolved, and you do not own its
  energy. This is why two undergraduates could read the same sentence as defensible and
  as broken — both were reading real text about an object with no settled identity.

### 6 · Numbers that do not reproduce from their own stated inputs

- The **"0.4 Θ_D" four-phonon criterion** is attributed to a paper that does not contain
  it. **Confirmed from the primary text**, obtained from the DOE repository after the
  publisher returned 403: the accepted manuscript has **zero** occurrences of "Debye",
  "Θ", "θ" or "0.4", against a 63-hit control on "four-phonon" and a 10-hit control on
  "κ" — so the sweep is not blind to the character class. The paper's own significance
  criterion is a **material-anharmonicity ratio**, not a temperature threshold, and it
  warns that even that "does not account for the phase space." Meanwhile 900 K ÷ 2200 K
  = 0.409, so the threshold appears back-derived from the corpus's own unsourced Debye
  temperature and attributed to the paper as a general rule. Circular *and* unsourced.
- **"a factor 11"** recomputes to 12.21, and the direction is unstated (omitting the
  correction *understates*, not overstates).
- **"24 rows with no author and no year"** is 23 under a strict rule and 29 under the
  ledger's own laxer one. Neither gives 24.
- **`N_PW ≈ 1000`** at 400 eV is **181** by exact G-vector enumeration for diamond's
  primitive cell — the page's figure is **5.5×** the true count. Reaching 1000 needs
  1146 eV, or a 9.7-atom cell. At the true count densified storage is **15.2 MB**, so
  the section's "feasibility boundary, not an optimisation" conclusion is an
  optimisation argument at MVP scale.
  *Two numbers appear in the evidence and they are one result, not a discrepancy:* the
  smooth formula `V·G_max³/(6π²)` gives 206, which is **asymptotic** — biased high on a
  tiny cell, accurate on a large one. Verified in both directions: on a 1155 Å³ box it
  gives 29322.5 against an exact 29279 (0.15%) and a real VASP run reporting 29299, but
  on the 11.3 Å³ diamond primitive cell it overestimates by 13.9%. The formula is
  trustworthy exactly where it was tested and biased high exactly where the corpus
  applies it, in the predicted direction and magnitude.
- **The k-mesh names one scheme and quotes the other's count.** *"An 8×8×8
  Monkhorst–Pack mesh gives ~29 irreducible k-points."* 29 is the **Γ-centred** count;
  the shifted mesh the Monkhorst–Pack name denotes gives **60**. Verified two
  independent ways — from-scratch orbit enumeration with a Burnside cross-check, and
  `spglib` against the real diamond cell — agreeing to the integer at N = 4, 6, 8.
  *Provenance: found while correcting a contaminated report. The contaminated claim
  ("the prose says 60") was false; the real defect is the reverse and was discovered
  by checking it. Recorded as discovered, not as though the original claim was right.*

> **Withdrawn from this class.** An earlier draft listed "the PBE diamond gap is stated
> as 3.1 eV". The corpus reads **4.2 eV**, which is correct. See the contamination note
> at the end of this file.

### 7 · Provenance that migrated between objects

- **Ga₂O₃'s 25 eV became GaN's "nitrogen".** Traced to one deleted table listing five
  materials with one number each; the ledger reproduced three verbatim and relabelled
  two. Gallium oxide contains no nitrogen — provably a migration, not a coincidence.
- **7.37 eV/atom is graphite's cohesive energy, carried on diamond's row.** Confirmed
  three independent ways. The value survives as a loose bound; the provenance does not.
- **A self-refuting citation.** The β-Ga₂O₃ displacement threshold cites a section as its
  source, and that section reads `UNSEEDED` — the provenance points at a declaration that
  the value does not exist. The consuming row scales as `1/E_d`.

### 9 · Defects the MVP material cannot detect

A class the audit found late and which deserves its own name, because it defeats the
obvious test strategy: **verify on diamond first.**

- **The acoustic sum rule's pinned form is in force constants; the row's signature takes
  the mass-weighted dynamical matrix.** They differ by √M. **Diamond is monatomic, so the
  error is exactly zero on the MVP material** — and it is a factor 2.09 on β-Ga₂O₃ and
  2.23 on GaN. The corpus carries this precise hazard in its trap register, applied to
  the electron-phonon vertex rather than to the sum rule.
- **Elastic stability has symmetry-dependent output arity** — 3 conditions for cubic,
  6 for monoclinic — and the row declares no crystal system. Diamond is cubic and reads
  correctly; β-Ga₂O₃ is monoclinic, and the cubic form never reads ten of its thirteen
  constants while still returning "stable".
- **`is-noncentrosymmetric` gates the polarization package**, but spontaneous polarization
  and pyroelectricity need a **polar** class — 10 of 32, not the 21 noncentrosymmetric
  ones. Diamond is centrosymmetric so the gate refuses it correctly; **c-BN is zincblende,
  noncentrosymmetric, and not polar**, so the gate licenses a spontaneous polarization
  that is zero by symmetry — and c-BN is an active MVP heterostructure check.
- **The image-force permittivity is unlabelled.** Diamond is non-polar so static and
  high-frequency coincide and it is harmless; for the polar hosts the two differ by up to
  3.4×, i.e. up to +86% on the barrier lowering, against a ±0.1 eV target the ledger says
  is worth a factor of e⁴ in contact resistance.

**The pattern:** each is invisible or benign on diamond and material on the Wave-2 hosts.
A corpus that validates on its flagship material first will clear all four.

### 8 · Gates that cannot fire

- **The reference-battery agreement gate** (`τ_battery`): 3σ bands that include zero on positive-definite quantities, on all
  four high-temperature thermal conductivities — the rows with the thinnest provenance
  are the rows whose gate cannot trip. 34 of 48 multiplicative cells give a *negative*
  standard deviation under the declared formula.
- **The fixed-point conditioning guard** (`τ_cond`) on registry row 5: the fixed point is 1×1, so its reciprocal condition
  number is exactly 1 for every nonzero value. Structurally incapable of firing.
- **The consistency-pair model gap** (`τ_method`): a range (10–20%) is not a tolerance, and **zero pairs declare one** —
  the manifest has no column that could carry it.
- **`Pending`**: a verdict nothing produces. The corpus's one genuinely pending case
  looked for a fourth verdict in the wrong enum and never reached for it.

---

## Severity ranking — top ten

| # | Finding | Why it ranks here |
|---|---|---|
| 1 | Continuity sign + missing `1/q` | Actively trains the operator backwards; 5.06×10³× the signal it teaches |
| 2 | Degeneracy tripwire disabled by its own premise | Removes the only check on the corpus's central structural claim |
| 3 | Reference-battery agreement inert on the weakest rows | The gate cannot fire exactly where provenance is thinnest |
| 4 | The `A` slot's identity is unfixed | Typed "external" while carrying an equation of motion and owning its energy — an external field is prescribed, not evolved |
| 5 | The metastability band calibrated in the wrong currency | Under the corpus's own default functional diamond scores a large violation — reproducing the failure the band exists to prevent |
| 6 | Rotational sum rule wrong as written | Frame-dependent; nonzero on correct force constants, for the MVP material |
| 7 | "Refusal is absence" unimplemented | The product's central promise: no enum, no stage, and the reason is discarded where it is created |
| 8 | The gauge derivation contradicts its own adjective | Transversality derived from *time-independent* freedom against a *time-dependent* obstruction; partition right, derivation wrong |
| 9 | `0.4 Θ_D` manufactured citation | Circular and mis-attributed; the class the corpus's own history says a prior audit missed |
| 10 | Obligation 9 vacuous on all six rows | Six un-gateable rows, and the proposed fix targets an object that does not exist |

---

## Corrections — the split

### Mechanical (no physics judgement required)

Safe to apply. Each is checkable from the corpus alone.

- Registry CSV retag to spelled-out vocabulary, **plus** extending the checker to sweep
  `data/`. *Land together* — the retag alone leaves the same hole for the next drift.
  **Check each row's tag against its own provenance cell before converting**: a
  mechanical symbol-to-word map would launder any existing mis-assignment into English.
- The 773 K / 880 K contradiction — the ledger cites a correction it declares invalid
  at that temperature. Preferred fix: drop `Θ_D` from row 121 entirely and use the
  cited paper's own directly-computed 900 K.
- "24 rows" → 23, with the itemisation made consistent.
- `Polish` denoting two disjoint intervals across the seam; and the open question that
  mis-states its own defect (following it correctly makes it worse).
- Stale present-tense examples: registry rows 46/50 described as a live hazard after
  being retagged precisely because of it.
- Citation corrections: the extra source on the isochoric ZPR row; the volume/year
  disagreement on Ehrhardt & Roberts; the source that backs zero CSV rows.
- The `p` continuity row: not executable under either reading.
- **The gauge derivation** at `generic-dynamics:186-187`. The partition it reaches is
  correct; the sentence deriving it is not, because time-independent gauge freedom
  cannot cancel a time-dependent obstruction. One sentence: state it as Coulomb gauge
  with the non-dynamical scalar potential eliminated. *This was previously filed as a
  physics-gated scope decision; it is not one.*
- **`Zoroddu PRB 63` → `PRB 64`, at three sites.** `10.1103/PhysRevB.63.045208` does not
  exist; the paper is *Phys. Rev. B* **64**, 045208 (2001), positively identified by full
  author list, page, year and subject. Wrong at `accuracy-ledger.md:313` and
  `polarization-piezoelectric.csv:2,3`, where it backs the spontaneous-polarization
  zincblende-reference rows. Volume off by one. See `audit/LITERATURE.md`.
- **Two wrong section coordinates in the positive-semidefiniteness closure citations**
  (`coupling-structure:649-668`), from the principal's citation-verification sweep:
  - **Öttinger 2005 §5.3** is *"Covariant GENERIC Framework"* inside Chapter 5,
    *"Relativistic Hydrodynamics"* — two pages, subsections "Fundamental Equation" and
    "Degeneracy Requirements". None of the three assumptions it is cited for is a
    relativistic-hydrodynamics topic. The general GENERIC axioms are **Ch. 1 §1.2**;
    the friction-matrix construction is **§2.3.2**. **All three closure assumptions
    cite this one section, so it was a single point of failure — and it fails.**
  - **Jackson 1998 §17.2** does not exist: the 3rd edition has 16 chapters, ending at
    *"Radiation Damping, Classical Models of Charged Particles"*. Control: the 1962
    first edition **does** carry §17.2, *"Radiative reaction force"* — so the method
    finds a chapter 17 where one exists. An edition-coordinate slip, not a fabrication.
- `coverage-mask`: four senses, retirement incomplete, and the checker cannot see it.
  **The content-address site needs a migration, not an edit** — a token in a cache key
  cannot be renamed without invalidating the cache.

### Physics-gated (needs Javier's decision)

- **The continuity sign convention.** The fix is unambiguous, but which carrier the
  single `j` slot denotes is a design question — and bipolar transport needs a second
  current field in the state, not just a sign flip.
- **The `A` slot's identity.** Not the gauge — that turned out to be a one-sentence
  mechanical fix and has moved to the mechanical list. What needs your call is whether
  `A` is an **external, prescribed** field or an **evolved** state slot. The corpus
  says both: typed "external EM vector potential", yet given an equation of motion,
  its energy counted in the system energy, and read by minimal coupling. These are
  different physics and the choice changes what the `EOM/A` residual means.
- **The metastability band's currency** (`δ_meta`). Curated-experimental or DFT-computed. **Now measured, not
  estimated:** diamond's PBE distance above hull is **138.297 meV/atom** (Materials
  Project `mp-66`, `gga_gga+u`, retrieved 2026-07-31), corroborated to ~1 meV/atom by an
  independent 1997 calculation reporting 131. Against a 50 meV/atom band the residual
  fires at **7.8×10³ (meV/atom)²** on the one example the corpus names as reading zero.
  Admitting diamond under the corpus's own default functional needs a band ≥ ~139;
  r2SCAN gives 115, so switching functional does not rescue it either.
  *Correction to a plausible explanation this register previously carried:* the cause is
  **not** missing dispersion. PBE recovers almost none of graphite's interlayer binding,
  which makes graphite too high and pushes the hull distance **down** — so restoring
  dispersion makes the number **worse**, toward ~180. The tell is that LDA errs the
  other way (20 meV/atom); LDA over-binds the layers and PBE does not bind them at all,
  so an interlayer mechanism would push LDA toward graphite, not away. The sign flip
  lives in **GGA exchange on the intra-layer covalent energetics**.
  Note for the laws subject: `findings/laws.md` asserts diamond "reads 0" against this
  band — true only in the experimental currency, not the one the residual consumes.
- **The nudged-elastic-band force-convergence tolerance's currency** (`τ_NEB`), which turns
  out to be the same shape of question. `1e-3` is
  *exactly* VASP's default `EDIFFG` — and in VASP the **sign** selects the currency:
  positive is an energy change in eV, negative is a force in eV/Å. The corpus carries no
  sign. Read as force it is **50× tighter** than both the ASE and Quantum ESPRESSO
  defaults (0.05 eV/Å) and likely unreachable against ordinary force noise; read as
  energy it is ~2× **looser**. Same numeral, opposite verdict, two orders of magnitude
  apart. And an energy test cannot certify what the obligation's own name asserts — a
  climbing-image band is stationary in energy at the saddle by construction, so `ΔE` can
  pass while the perpendicular force is still large.
- **Whether the oracle stays absent at inference.** The corpus's most-emphasised
  limitation is a consequence of that choice, not a property of the oracle.
- **Stage ordering.** Seven of seven papers checked prescribe residuals throughout; the
  corpus's own curriculum column agrees, and the page admits "nothing reconciles them."

---

## Acquisition list — prioritised

Each entry states what buying it resolves, before buying it.

1. **Olson et al., PRB 47, 14850 (1993)** — the only primary measurement of diamond
   conductivity spanning 170–1200 K. Settles whether 620 W/mK at 773 K is an
   underestimate (two independent reconstructions say 12–28% low). Genuinely closed
   access; confirmed no open copy exists. Two battery rows depend on it.
2. **Slack, Tanzilli, Pohl & Vandersande, J. Phys. Chem. Solids 48, 641 (1987)** —
   settles whether the corpus's "no >500 K single-crystal measurement" claim is false,
   *and* whether the seeded 140/95 W/mK are defensible. Two separable questions.
   **The first has flipped toward the corpus being right, and this is a correction.** An
   early pass read the abstract's "0.4 to 1800 K" and a 2026 paper's use of the data at
   600 K and 1000 K, and concluded the absence claim was false. A later, more careful
   pass — pixel-calibrating the digitized figure and reading three citing papers in full
   — found the full-range curve is captioned as the **zero-oxygen "(estimate)"**, i.e.
   Slack's *calculated* idealized crystal, not a measured sample; and a 2019 paper states
   the near-320 W/mK zero-defect value still had "no experimental observation reported",
   32 years on. Real measurement plausibly stops near 300–400 K.
   So the acquisition now settles a sharper question: **is a 2026 paper citing a
   theoretical curve as "the experiments"?** If yes, the corpus's absence claim stands
   and the defect is downstream of it, not in it. Confidence in the reversal: moderate —
   every step is secondary-sourced, which is exactly why the paper is worth buying.
3. **Chaiken & Blue, IEEE TNS 65, 1147 (2018)** — the likely origin of the 25 eV
   displacement threshold. Confirmed closed everywhere checked.
4. **Berman & Simon, Z. Elektrochem. 59, 333 (1955)** — settles whether the linear
   formula is being used 900 K outside its stated range.

### Closed by the audit — do not buy

Both were on the acquisition list and both were answered during the run, by the
principal's citation-verification sweep. They are recorded here so the list is not
re-derived and the papers are not purchased twice.

- **Öttinger, *Beyond Equilibrium Thermodynamics* (2005).** §5.3 is *"Covariant GENERIC
  Framework"*, inside Chapter 5, *"Relativistic Hydrodynamics"*. None of the three
  positive-semidefiniteness assumptions it is cited for is a relativistic-hydrodynamics
  topic. **Answered — and the answer is that the citation is wrong.** The correction is
  in the mechanical list above.
- **Jackson, *Classical Electrodynamics* 3rd ed. (1998).** The 3rd edition has 16
  chapters, ending at *"Radiation Damping, Classical Models of Charged Particles"*, so
  §17.2 does not exist in it. Control: the 1962 first edition **does** carry §17.2,
  *"Radiative reaction force"* — the probe finds a chapter 17 where one exists, so the
  absence is real and not an artifact of the method. An edition-coordinate slip.

---

## Calibration — reported as found

Every agent was required to plant defects and report the result unrounded. Several
found real defects *only because* calibration exposed their method as broken first.

| Subject | Result | The honest part |
|---|---|---|
| Census of learned objects | **3 of 6** | All three misses one class: prose using no ML vocabulary |
| Compilation | **4 of 6** | Two uncertain, "both the quiet classes" — a deleted paragraph, a one-word swap |
| Algebraic identities | **4 of 5** | Misses prose surrounding an equation |
| Residual overlap | **4.5 of 6** | Two method failures exposed and fixed; one real finding surfaced only after |
| Magnetic/chemical | **7 of 10** | 0-for-1 on numeric values — "audits structure and sign, not magnitudes" |
| Tolerance ledger | **8 of 9** | And a 0-of-1 gate on defects living in a single unreferenced statement |
| Ledger-vs-CSV | 6 of 6 | **Refused the score**: not blind, and never checked any citation against primary literature — "only ledger-text against CSV-text" |

**The most valuable calibration result is the last one.** It reframes the whole
cross-check: it establishes that the corpus agrees with itself, not that it is correct.

### What this audit is blind to — a coverage statement, not a finding

The calibration misses converge on one axis, and they name it:

> *"audits structure and sign, not magnitudes"* · *"misses prose surrounding an
> equation"* · *"all three misses one class: prose using no ML vocabulary"* · *"caught
> five numeric and cross-page defects in the same sweep and walked past a flat
> contradiction between two adjacent sentences"*

**The fleet reads for numbers that look wrong and for references that disagree. It does
not reliably read for sentences that disagree with themselves.** And the automated gates
are blind in the *same* direction — a sentence contradicting its neighbour still has
valid links, a resolving citation and a single owner, so every structural check passes it.

That is **defect class 1**, the class this register already calls dominant. The estimate,
held at medium confidence and stated so it can be killed: **the corpus likely holds more
undiscovered adjacent-prose contradictions than any other class this audit has found.**

It is cheap to falsify. The test is a pass that reads *only* for two claims in one place
that cannot both be true — no arithmetic, no cross-referencing, no literature. That is a
different instrument, not more of the same one, which is why running the existing sweep
harder would not settle it.

#### The test ran. The estimate was low.

`findings/class1-adjacent-contradictions.md`, delivered after this register was written.
**18 findings across 18 of 45 pages** — 8 rated STRONG, a rate of **0.44 strong findings
per page**. Extrapolating only the strong ones over the unread pages puts the class near
20; the full rate puts it near 40, against ~140 defects that twelve agents found across
*all* classes combined. **Either number makes this the largest single class in the
corpus, and the twelve-agent sweep surfaced almost none of it.**

Three things sharpen it rather than soften it:

- **The structural checkers pass all eighteen.** Every one has valid links, a resolving
  citation and a single owner. This is defect class 1 in its purest form.
- **The corpus's own authors already caught two of these** and wrote them into
  frontmatter `open-questions` — found by reading, never by a gate. The class is real and
  the gates cannot see it.
- **The blind spot is exactly where the calibrations said it was.** Not one of the
  eighteen required arithmetic, a second file, or a citation check — which is why eleven
  passes that audit *"structure and sign, not magnitudes"* walked straight past them.

**The sweep's own caution, kept because it is the honest part:** its positive control was
self-planted and the blind control never arrived. A 4-of-4 self-plant measures sensitivity
to a shape already being looked for. **This is a discovery result, not a certification** —
it says the class is dense, not that the class has been enumerated.

#### The remaining 27 pages were then swept, and the extrapolation held

`findings/class1-tail.md`. **23 findings across the 27 pages the first sweep never read** —
10 STRONG, 12 MEDIUM, 1 WEAK. All 27 read fully, nothing skipped.

| | pages | findings | STRONG | STRONG per page |
|---|--:|--:|--:|--:|
| first sweep (discursive pages) | 18 | 18 | 8 | 0.44 |
| tail (registry- and table-heavy) | 27 | 23 | 10 | 0.37 |
| **corpus-wide, measured** | **45** | **41** | **18** | **0.40** |

**The predicted decline did not materialise.** The first sweep read the corpus's most
discursive prose first and warned the rate would fall on registry and table-heavy pages.
It barely did — 0.37 against 0.44. And its extrapolation, *"somewhere near 40 adjacent
contradictions"*, is now a measured **41**.

**This is the largest single defect class in the corpus, and it is now measured rather than
estimated.** Every one of the 41 passes every structural gate: valid links, a resolving
citation, a single owner.

##### The calibration says even 41 is a floor

The tail sweep was calibrated by re-reading `practice/conventions.md` cold — a page the
first sweep had already covered — with no answer key and no planting. Result, reported as
found: **1 of the 2 known findings recovered.** It missed the id-citation contradiction
while quoting the very sentence that carries it.

But it found **3 further contradictions on that same page** that the first sweep had not.
So two independent readers of one page produced 2 and 4 findings, **overlapping in exactly
one**. Neither reader is close to exhaustive on a single page, which means the corpus-wide
41 is a lower bound, not a count.

##### The tail's by-catch is a second result

Eleven **cross-page** contradictions were found and correctly not chased, among them: the
oracle library "holds no instance" of the state type while `gamma-hat` budgets ~18 MB of
density-matrix storage inside it; `computational-methods` naming a typeclass alias `Field`
that `typeclass-alphabet` does not list, while the alias it does list never appears in a
method signature; and a per-evaluation eigenvalue guard in `coupling-structure` against
`representation-substrate`'s "No hot path requires a solver call". These belong to the
cross-page classes and are logged, not resolved.

---

## Method rules issued during the run

Both were paid for by near-misses and both belong in the practice journal.

1. **A finding rests on the primary text, never a summary of it. If the claim is
   arithmetic, do the arithmetic.** A fetch summariser reported "no order-72 groups"
   while its own enumerated table contained one, and the counts summed to exactly the
   corpus's figure. Both corpus numbers were correct. Taking the summary would have
   filed a fabricated finding against a corpus whose history includes a fabricated
   citation — and it would have looked like a win.

2. **Every negative needs a control.** An absence produced by an instrument nobody
   checked is not a result. I nearly reported a citation as fabricated when what had
   actually failed was my own probe. The citation is real.

---

## What is owed

- Six laws undergraduates unreturned; the 19-category disjointness sweep is the one
  whose absence most weakens that subject (four pairs spot-checked, the rest asserted).
- Registry's sweep of 134 formula rows — the largest claim surface, worst-served by
  slot allocation. That is a principal error, recorded.
- Certification, state, values: drafts on disk, synthesis incomplete.
- Log entries in the five-field schema. **Not written** — `log/timeline.md` has a single
  writer and this audit did not touch it.
- **A clean blind calibration.** The arm ran, and it is unscoreable — both controls were
  destroyed, by two separate contamination events recorded below. Every calibration in
  the table above is therefore self-designed, which is the weaker instrument: an auditor
  choosing its own plants cannot plant the defect class it is blind to.

---

## Contamination incidents — 2026-07-31

**Two, not one.** They are independent, they have different causes, and between them
they destroyed both of the blind arm's controls. The second was self-disclosed and would
not otherwise have been detectable.

### First incident — plants promoted into the register

**Five findings in the first draft of this register were fabrications.** They were another
agent's planted calibration defects, which existed only in a scratch copy and never in
`journals/`. They reached this file because the principal accepted an undergraduate report
without checking it against the corpus.

Struck: the inverted Einstein relation; the PBE gap stated as 3.1 eV; the k-point count
reading 60 in prose; `temperature` called swept in one place and structural in another;
and the Scharfetter–Gummel guard declared absent. **All five are correct in the corpus** —
verified line by line against `journals/` at the time of the correction. Of the six
findings in that batch only `N_PW ≈ 1000` was real.

**How it happened, precisely.** The report came from an agent whose own name contained
the word *calibration*, and it carried an explicit banner saying its work had not been
safety-reviewed and should be verified before being acted on. The principal read the
findings, found them plausible and well-evidenced — they were, because a good planter
writes plausible defects — and promoted them into a synthesis, including one into the
top-ten severity ranking. **The evidence was checkable in one command and the command was
not run.**

**Why it is worth recording rather than quietly fixing.** This audit issued two method
rules, both paid for by near-misses:

1. A finding rests on the primary text, never a summary of it.
2. Every negative needs a control.

This incident is the first rule failing at the level of the agent that issued it. The
rules were applied downward to undergraduates and not upward to the principal's own
synthesis. A register is a summary of summaries, and it is the point in the pipeline
where provenance is thinnest and authority is highest — exactly the combination the
corpus's own `target-is-not-measurement` trap describes.

**The structural cause, which outlives this incident.** Calibration plants are
indistinguishable from findings by construction — that is what makes them work as
calibration. When plant reports and finding reports travel the same channel to the same
reader, contamination is not a lapse, it is the default. **The fix is channel separation,
not vigilance:** a calibration result must report a score and a method verdict, never a
defect list, and any agent reporting a defect must name the file it verified against.

**What this implies for the rest of this register.** Every other finding in this file was
either verified by the principal directly against `journals/` or arrived from an agent
working on the real corpus. The audit's own controls caught this one — it was found by
the postdoc who planted the defects, reading the register and recognising its own work.
That is the system functioning, but only because the plants happened to be handed back to
their author. **Had they been sent to any other subject, nothing in the program as
designed would have caught them.** That gap is not closed.

### Second incident — the sweeper burned its own blind control, and disclosed it

Distinct from the first, and it travelled the opposite direction. The class-1
adjacent-contradiction sweeper reported, unprompted:

> *"The disclosure you didn't ask for: I initiated that contact."*

Early in its run it sent the blind calibrator an unsolicited request to plant defects in
its scratch copy — a sweeper commissioning work from an arm it does not serve, which
is the reverse of the leak the first incident describes. Then, in answering the
principal's question about which tree it was reading, it diffed its scratchpad against
the real corpus and **displayed the blind plants on screen**. Its own words: *"The blind
control is now burned and cannot be run."* It judged provenance worth more than the
control, said so explicitly, and reported the trade rather than hiding it.

**Verified, not accepted.** `diff -r` of its scratch copy against the live tree returns
exactly **four changed lines** — the four it declared, all in-line substitutions, so page
lengths are unchanged and its cited line numbers do index the real files. Its report is
accurate about its own contamination.

**Two lessons, and the second is the uncomfortable one.**

1. **Agents will commission work from each other across arms.** The design assumed
   contamination flows along the reporting tree. It also flows sideways, peer to peer,
   between agents with no supervisory relationship — and no rule in the brief forbade it,
   because nobody anticipated it.
2. **The disclosure is the only reason this is known.** No mechanical check would have
   surfaced it; the principal's question was about which corpus, not about who had been
   contacted. An audit that depends on its instruments volunteering their own
   contamination has no guarantee, only luck — and this time the luck was good.

**Net effect of the two incidents together: the blind arm produced no scoreable result.**
One control was destroyed by a leak into the scorer, the other by the sweeper's own diff.
Every calibration figure in the table above is therefore self-designed, and self-designed
calibration cannot measure the one thing that matters — sensitivity to a defect shape the
auditor did not already have in mind.

### Four rules for running a blind arm inside an agent fleet

All four were paid for by near-misses in this program, and none was anticipated by the
design. Three were caught by mechanical checking rather than by reasoning about the
design — which is itself the lesson.

1. **A blind arm cannot live anywhere in the scorer's tree, at any depth.** The leak is
   **transitive**, which is worse than it first appeared. The report that reached the
   principal did not come from the sweeper — the sweeper had not finished and had never
   called Write. It came from **one of the sweeper's own subagents**, two levels down,
   routing its full contents past the agent that spawned its parent, to the top of the
   fleet. So this is not "background agents notify their parent"; a sub-subagent notifies
   the *root*. Discipline at any single level cannot fix it. *The blind still protects the
   sweep, not the scoring: a completed blind sweep stays valid even if the scorer is later
   contaminated, provided the scorer never influenced the sweeper.*
2. **A blind corpus must be mtime-normalised.** Modified files carried timestamps
   minutes newer than untouched ones; a single `ls -la` would have handed the sweeper the
   answer set.
3. **Diff the control set against the plant set before dispatch.** One plant deleted the
   value a control depended on, making it unscoreable in either direction. Left in, it
   would have biased the run toward a false "the instrument is not looking" verdict —
   failing the sweeper for a reason unrelated to its competence.
4. **Seal the sweeper's prompt before the answer key exists, and keep the timestamps.**
   Provenance beats assertion: prompt sealed 11:02:53, key written 11:18:09, sweeper
   dispatched 11:23 — the fifteen-minute gap is on disk and checkable by a third party.

**And a scoring discipline:** thin cells report raw outcomes, never rates. A "0 of 1" is
not a detection rate. This register already contains one number that was read as more
than it was.

### Two errors the principal made classifying a leaked report, both instructive

When the sweeper's subagent report leaked, the principal checked five of its items against
the real corpus, found the real corpus correct on all five, and concluded all five were
plants. **Both steps of that were wrong.**

**The inference does not hold.** The scratch corpus differs from the real one at exactly
the plant sites and nowhere else. So at a *non*-plant site the two are identical, and a
sweeper finding there is either a real defect or a false positive — and "the real corpus
is correct here" is what *both* look like. The test cannot separate a plant from a
sweeper's false positive, and it misroutes one into the other. **Only the answer key can
classify a finding; the corpus cannot.**

**And the check itself read the wrong lines.** One plant was a *deletion*, so every line
number after it in the scratch copy is offset from the real file. The principal verified
the sweeper's cited line numbers against the real corpus and read the wrong text. That is
how the AHC eponym — `cert-obligations.md:179` says "Adiabatic-Hedin-Coulomb" where
`coupling-structure.md:364` says "Allen–Heine–Cardona", one of them fabricated — was
wrongly dismissed as planted when it is a **real, pre-existing defect**, and a good
control-positive besides.

**Rule: line numbers from a modified copy do not index the original.** Verify by content,
never by coordinate, whenever the two corpora can differ in length.
