# Grounding pass — do the audit's quotations exist in the corpus?

**Result: no fabricated findings were detected.** All 189 findings were tested; every one
whose evidence this instrument could read resolves to real corpus text, and the eight
that appeared not to were hand-checked and are instrument artifacts, not fabrications.

This pass exists because the audit's own failures all had one shape. Five planted
defects reached the register. Two literature checks were dispatched against claims the
corpus does not make — nickel's Curie point read as 727 K when `reference-battery.md`
says **627 K**, and `3.56712 Å` attributed to Hom/Kiszenick/Post when
`accuracy-ledger.md` says **3.566986 Å** and already flags the loose uncertainty. In
every case the evidence was checkable in one command and the command was not run.

**The ordering rule this establishes: grounding gates literature dispatch.** Nothing is
checked against a paper until the corpus claim it rests on is confirmed to exist. The two
false positives above were competent literature work aimed at a premise nobody grounded.

---

## Method

For every quotation in `audit/findings/*.md`: normalise, then search the live tree for
the literal string.

**By content, never by coordinate.** No `file.md:NN` reference is trusted — a deletion in
a modified copy offsets every line after it, and that is precisely how one real defect
(the `Adiabatic-Hedin-Coulomb` / `Allen–Heine–Cardona` eponym clash) was once wrongly
dismissed as a plant. The coordinate is recorded; the *string* is the test.

Normalisation collapses only what legitimately differs between a quotation and its
source: markdown emphasis the auditor added, line wrapping, non-breaking spaces, the
several dash codepoints that render alike, and trailing punctuation the auditor supplied.
**Unicode is otherwise preserved** — the en-dash class is exactly where a naive sweep goes
blind.

| verdict | meaning |
|---|---|
| **GROUNDED** | the string is in the file the finding names |
| **MOVED / UNATTRIBUTED** | the string is in the corpus; the finding named a different file, or named none |
| **untestable** | the quotation cannot match verbatim, or the finding quotes nothing |

---

## Calibration — reported as found

**13 controls, 13 pass.** Nine positive strings hand-verified present today, four negative
strings known absent.

| | control | result |
|---|---|---|
| POS | `The axis is the second column` | found |
| POS | `external EM vector potential` | found |
| POS | `typed inputs to output, with units` | found |
| POS | `remaining time-independent gauge freedom` | found |
| POS | `Adiabatic-Hedin-Coulomb` | found |
| POS | `Neither kind has a page id` | found |
| POS | `Nickel's Curie point at 627 K` | found |
| POS | `Allen–Heine–Cardona` — **en-dash class** | found |
| POS | `δ_meta` — **Unicode class** | found |
| NEG | `zzqx wobbling flange of the metriplectic hamster` | absent |
| NEG | `the PBE diamond gap is stated as 3.1 eV` — struck fabrication | absent |
| NEG | `Nickel's Curie point at 727 K` — today's false positive | absent |
| NEG | `3.56712` — today's false positive | absent |

The two Unicode controls matter more than the rest: a pass that reports absence while
being blind to a character class reports absence *everywhere* that class appears.

### The instrument was wrong five times before it was right

Recorded because the first four runs each produced a confident, wrong number, and because
a calibration that only reports its final score hides the thing worth knowing.

| run | reported | the bug |
|---|---|---|
| 1 | 77 of 113 absent | Blockquotes separated by prose were **concatenated** into strings existing nowhere |
| 2 | 65 "MOVED" | 36 of them named no file at all — an *attribution gap* reported as a *relocation* |
| 3 | 131 findings with "no evidence" | 127 of those quote inline or in table cells; the pass read blockquotes only |
| 4 | 417 absent | A 14-item random sample was **14/14 artifact** — elisions, mid-sentence fragments, blockquote-marker bleed, and the auditors' own defect-class names |
| 5 | 58 untestable | The filter rejected any quotation **opening with a quote mark** — silently discarding the primary evidence of several STRONG findings |

**Every one of those five was found by sampling the output, not by reading the code.** The
first four runs would each have supported a confident public claim that the audit was
substantially fabricated. It is not.

---

## Results

189 findings. Shaped gaps, near-findings, acquisition requests and appendices are
excluded — grading an open question or an already-rejected candidate as a finding
manufactures failures the auditors never claimed.

| | count | |
|---|--:|---|
| **a — grounded in corpus text** | **75** | quotation resolves in the corpus; may land |
| **b — rests on a literature claim** | **48** | corpus side grounded; source side unverified → Step 2 |
| **u — evidence in an untestable form** | **58** | tables, backticked signatures, counts — not fabrications, *unreadable by this instrument* |
| **artifact-only, hand-checked** | **8** | appeared absent; all eight resolved |

261 quotations tested: **124 grounded**, 104 moved or unattributed, 33 untestable.

### The eight that appeared absent — every one dispositioned by hand

| finding | why it read ABSENT | disposition |
|---|---|---|
| `F10` compilation | quote elided with `…`; the phrase searched was the auditor's own proposed resolution in scare quotes | real — grounds at `crystal-inputs.md:132` |
| `F11` compilation | auditor interpolation `generalis[es]` cannot match verbatim | real — grounds at `residual-definitions.md:105` |
| `F36` registry | the string is the *register's* defect-class name, not a corpus quote | not a corpus claim |
| `S19` state | evidence is a markdown **table**; extracted string was the auditor's own question | real — grounds at `multiscale-state.md:143-144` |
| `S20` seams | fragment containing a shell command | artifact |
| `S21` seams | quotation is from a **paper**, correctly absent from the corpus | literature → Step 2 |
| `S22` seams | same paper quotation | literature → Step 2 |
| `F15` values | auditor's arithmetic paraphrase; corpus says `1,179 rows, of which 1,131 are distinct shapes` | real — grounds at `build-verification.md:104` |

**Zero fabrications.**

---

## What this pass cannot see — a coverage statement, not a clean bill

**58 findings present evidence in a form this instrument cannot read**, and they are not
evenly spread:

| subject | untestable / total |
|---|---|
| `registry.md` | **25 / 36** |
| `certification.md` | 10 / 37 |
| `state.md` | 7 / 25 |
| `values-and-provenance.md` | 5 / 17 |
| `seams.md` | 4 / 22 |
| `class1-adjacent-contradictions.md` | 3 / 18 |
| `compilation.md` | 3 / 13 |
| `laws.md` | 1 / 21 |

The concentration is structural, not suspicious: registry findings are about CSV rows,
signatures and counts, which are asserted with backticks and tables rather than quoted
prose. **They are the largest claim surface in the corpus and the least covered by this
check** — the same subject the register already records as worst-served by slot
allocation. A second instrument is needed there, and it is a different instrument, not
more of this one.

**The honest limit:** this pass proves the audit's quotations are real. It does **not**
prove the inferences drawn from them are correct. A verbatim quotation can still support
a wrong conclusion — which is exactly what happened with the gauge finding, where the
quoted text was real and the consequence claimed from it was over-stated twice.

---

## Consequence for landing

- **Grade (a), 75 findings** — corpus side verified. Eligible for the mechanical
  correction batch, subject to being mechanical.
- **Grade (b), 48 findings** — hold. Corpus side is grounded, so these are now *safe to
  dispatch* to literature verification. That is Step 2, and this pass is its gate.
- **Grade (u), 58 findings** — do not land on this evidence. Not quarantined as false;
  untested. They need the registry-shaped instrument.
- **Physics-gated items land never** — the `A` slot's identity, `δ_meta`'s currency, the
  continuity sign convention and whether the state needs a second current field, and
  whether the oracle stays absent at inference remain Javier's decisions.

Corpus unmodified throughout: `git status --porcelain journals/ data/ log/ generated/`
returns empty, and both gates stay green.

---

## Verification of this pass

Ten grade-(a) findings drawn at random (seed 31) and re-checked with an
independently-written matcher against the file the pass named: **10 / 10 agreement**.

The first run of that re-check reported 7/10. All three disagreements were bugs in
the *re-check* — it failed to strip a leading quotation mark that the main pass
strips. Recorded because a 7/10 would have been reported as a finding about the
grounding pass when it was a finding about the checker checking it, and that is the
same error class this whole document exists to catch.

Gates after the pass: `check_structure --check` exit 0; `check_the_checker`
34 probes, 34 caught, 0 missed, 0 stale, 29 error sites, 0 unreached.
`git status --porcelain journals/ data/ log/ generated/` empty.

---

## Appendix — per-finding record

| subject | id | quotes | grounded | moved/unattr | untestable | grade |
|---|---|--:|--:|--:|--:|---|
| certification | `A1` | 2 | 2 | 0 | 0 | **a** grounded |
| certification | `A2` | 1 | 1 | 0 | 0 | **a** grounded |
| certification | `A3` | 1 | 1 | 0 | 0 | **a** grounded |
| certification | `A4` | 0 | 0 | 0 | 0 | **u** untestable form |
| certification | `A5` | 0 | 0 | 0 | 0 | **u** untestable form |
| certification | `A6` | 4 | 4 | 0 | 0 | **a** grounded |
| certification | `A7` | 3 | 3 | 0 | 0 | **b** literature |
| certification | `B0` | 1 | 1 | 0 | 0 | **a** grounded |
| certification | `B1` | 1 | 1 | 0 | 0 | **a** grounded |
| certification | `B2` | 1 | 1 | 0 | 0 | **a** grounded |
| certification | `B3` | 3 | 0 | 1 | 2 | **b** literature (2 untestable) |
| certification | `B4` | 3 | 1 | 2 | 0 | **b** literature |
| certification | `B5` | 0 | 0 | 0 | 0 | **u** untestable form |
| certification | `B6` | 0 | 0 | 0 | 0 | **u** untestable form |
| certification | `B7` | 1 | 1 | 0 | 0 | **b** literature |
| certification | `B8` | 3 | 3 | 0 | 0 | **a** grounded |
| certification | `F1` | 3 | 3 | 0 | 0 | **b** literature |
| certification | `F10` | 4 | 4 | 0 | 0 | **b** literature |
| certification | `F11` | 1 | 1 | 0 | 0 | **a** grounded |
| certification | `F12` | 5 | 1 | 4 | 0 | **b** literature |
| certification | `F13` | 0 | 0 | 0 | 0 | **u** untestable form |
| certification | `F14` | 1 | 1 | 0 | 0 | **b** literature |
| certification | `F15` | 1 | 1 | 0 | 0 | **b** literature |
| certification | `F16` | 1 | 1 | 0 | 0 | **b** literature |
| certification | `F17` | 0 | 0 | 0 | 0 | **u** untestable form |
| certification | `F18` | 2 | 2 | 0 | 0 | **a** grounded |
| certification | `F19` | 4 | 4 | 0 | 0 | **b** literature |
| certification | `F2` | 3 | 2 | 0 | 1 | **b** literature (1 untestable) |
| certification | `F20` | 0 | 0 | 0 | 0 | **u** untestable form |
| certification | `F21` | 3 | 3 | 0 | 0 | **a** grounded |
| certification | `F3` | 4 | 0 | 1 | 3 | **b** literature (3 untestable) |
| certification | `F4` | 0 | 0 | 0 | 0 | **u** untestable form |
| certification | `F5` | 0 | 0 | 0 | 0 | **u** untestable form |
| certification | `F6` | 1 | 1 | 0 | 0 | **a** grounded |
| certification | `F7` | 4 | 4 | 0 | 0 | **b** literature |
| certification | `F8` | 0 | 0 | 0 | 0 | **u** untestable form |
| certification | `F9` | 3 | 3 | 0 | 0 | **a** grounded |
| class1-adjacent-contradictions | `F1` | 1 | 1 | 0 | 0 | **a** grounded |
| class1-adjacent-contradictions | `F10` | 2 | 2 | 0 | 0 | **a** grounded |
| class1-adjacent-contradictions | `F11` | 1 | 1 | 0 | 0 | **a** grounded |
| class1-adjacent-contradictions | `F12` | 1 | 1 | 0 | 0 | **b** literature |
| class1-adjacent-contradictions | `F13` | 1 | 1 | 0 | 0 | **a** grounded |
| class1-adjacent-contradictions | `F14` | 2 | 2 | 0 | 0 | **a** grounded |
| class1-adjacent-contradictions | `F15` | 1 | 1 | 0 | 0 | **a** grounded |
| class1-adjacent-contradictions | `F16` | 1 | 1 | 0 | 0 | **a** grounded |
| class1-adjacent-contradictions | `F17` | 1 | 1 | 0 | 0 | **a** grounded |
| class1-adjacent-contradictions | `F18` | 3 | 2 | 0 | 1 | **a** grounded (1 untestable) |
| class1-adjacent-contradictions | `F2` | 0 | 0 | 0 | 0 | **u** untestable form |
| class1-adjacent-contradictions | `F3` | 4 | 4 | 0 | 0 | **a** grounded |
| class1-adjacent-contradictions | `F4` | 2 | 2 | 0 | 0 | **b** literature |
| class1-adjacent-contradictions | `F5` | 2 | 1 | 0 | 1 | **a** grounded (1 untestable) |
| class1-adjacent-contradictions | `F6` | 0 | 0 | 0 | 0 | **u** untestable form |
| class1-adjacent-contradictions | `F7` | 1 | 1 | 0 | 0 | **a** grounded |
| class1-adjacent-contradictions | `F8` | 2 | 2 | 0 | 0 | **a** grounded |
| class1-adjacent-contradictions | `F9` | 0 | 0 | 0 | 0 | **u** untestable form |
| compilation | `F1` | 3 | 3 | 0 | 0 | **a** grounded |
| compilation | `F10` | 1 | 0 | 0 | 1 | **a** artifact-only — hand-checked |
| compilation | `F11` | 1 | 0 | 0 | 1 | **a** artifact-only — hand-checked |
| compilation | `F12` | 0 | 0 | 0 | 0 | **u** untestable form |
| compilation | `F2` | 2 | 2 | 0 | 0 | **a** grounded |
| compilation | `F3` | 2 | 1 | 0 | 1 | **a** grounded (1 untestable) |
| compilation | `F4` | 1 | 1 | 0 | 0 | **a** grounded |
| compilation | `F5` | 0 | 0 | 0 | 0 | **u** untestable form |
| compilation | `F6` | 1 | 1 | 0 | 0 | **a** grounded |
| compilation | `F6` | 2 | 2 | 0 | 0 | **a** grounded |
| compilation | `F7` | 0 | 0 | 0 | 0 | **u** untestable form |
| compilation | `F8` | 2 | 2 | 0 | 0 | **a** grounded |
| compilation | `F9` | 1 | 1 | 0 | 0 | **a** grounded |
| laws | `L1` | 6 | 0 | 3 | 3 | **a** grounded (3 untestable) |
| laws | `L10` | 1 | 0 | 1 | 0 | **a** grounded |
| laws | `L11` | 1 | 0 | 1 | 0 | **a** grounded |
| laws | `L12` | 1 | 0 | 1 | 0 | **b** literature |
| laws | `L13` | 1 | 0 | 1 | 0 | **a** grounded |
| laws | `L14` | 1 | 0 | 1 | 0 | **a** grounded |
| laws | `L15` | 1 | 0 | 1 | 0 | **b** literature |
| laws | `L16` | 3 | 0 | 3 | 0 | **b** literature |
| laws | `L17` | 6 | 0 | 6 | 0 | **b** literature |
| laws | `L18` | 3 | 0 | 2 | 1 | **a** grounded (1 untestable) |
| laws | `L19` | 1 | 0 | 1 | 0 | **a** grounded |
| laws | `L2` | 4 | 0 | 4 | 0 | **a** grounded |
| laws | `L20` | 2 | 0 | 2 | 0 | **a** grounded |
| laws | `L21` | 4 | 0 | 4 | 0 | **a** grounded |
| laws | `L3` | 1 | 0 | 1 | 0 | **a** grounded |
| laws | `L4` | 5 | 0 | 5 | 0 | **a** grounded |
| laws | `L5` | 0 | 0 | 0 | 0 | **u** untestable form |
| laws | `L6` | 5 | 0 | 5 | 0 | **a** grounded |
| laws | `L7` | 2 | 0 | 1 | 1 | **a** grounded (1 untestable) |
| laws | `L8` | 2 | 0 | 2 | 0 | **a** grounded |
| laws | `L9` | 2 | 0 | 2 | 0 | **a** grounded |
| registry | `F1` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F10` | 1 | 0 | 1 | 0 | **b** literature |
| registry | `F11` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F12` | 1 | 0 | 1 | 0 | **b** literature |
| registry | `F13` | 1 | 0 | 1 | 0 | **a** grounded |
| registry | `F14` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F15` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F16` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F17` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F18` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F19` | 1 | 0 | 1 | 0 | **b** literature |
| registry | `F2` | 1 | 0 | 1 | 0 | **b** literature |
| registry | `F20` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F21` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F22` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F23` | 2 | 1 | 1 | 0 | **b** literature |
| registry | `F24` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F25` | 1 | 0 | 1 | 0 | **b** literature |
| registry | `F26` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F27` | 1 | 1 | 0 | 0 | **b** literature |
| registry | `F28` | 1 | 0 | 1 | 0 | **b** literature |
| registry | `F29` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F3` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F30` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F31` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F32` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F33` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F34` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F35` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F36` | 1 | 0 | 0 | 1 | **a** artifact-only — hand-checked |
| registry | `F4` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F5` | 2 | 0 | 2 | 0 | **a** grounded |
| registry | `F6` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F7` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F8` | 0 | 0 | 0 | 0 | **u** untestable form |
| registry | `F9` | 0 | 0 | 0 | 0 | **u** untestable form |
| seams | `S1` | 1 | 1 | 0 | 0 | **a** grounded |
| seams | `S10` | 2 | 1 | 0 | 1 | **a** grounded (1 untestable) |
| seams | `S11` | 0 | 0 | 0 | 0 | **u** untestable form |
| seams | `S12` | 2 | 2 | 0 | 0 | **b** literature |
| seams | `S13` | 0 | 0 | 0 | 0 | **u** untestable form |
| seams | `S14` | 0 | 0 | 0 | 0 | **u** untestable form |
| seams | `S15` | 2 | 1 | 1 | 0 | **a** grounded |
| seams | `S16` | 4 | 4 | 0 | 0 | **b** literature |
| seams | `S17` | 2 | 2 | 0 | 0 | **b** literature |
| seams | `S18` | 1 | 1 | 0 | 0 | **a** grounded |
| seams | `S19` | 2 | 1 | 0 | 1 | **a** grounded (1 untestable) |
| seams | `S2` | 2 | 2 | 0 | 0 | **a** grounded |
| seams | `S20` | 1 | 0 | 0 | 1 | **a** artifact-only — hand-checked |
| seams | `S21` | 1 | 0 | 0 | 1 | **a** artifact-only — hand-checked |
| seams | `S22` | 1 | 0 | 0 | 1 | **a** artifact-only — hand-checked |
| seams | `S3` | 1 | 1 | 0 | 0 | **b** literature |
| seams | `S4` | 1 | 1 | 0 | 0 | **b** literature |
| seams | `S5` | 3 | 2 | 1 | 0 | **a** grounded |
| seams | `S6` | 1 | 1 | 0 | 0 | **a** grounded |
| seams | `S7` | 5 | 5 | 0 | 0 | **a** grounded |
| seams | `S8` | 0 | 0 | 0 | 0 | **u** untestable form |
| seams | `S9` | 2 | 2 | 0 | 0 | **b** literature |
| state | `S1` | 0 | 0 | 0 | 0 | **u** untestable form |
| state | `S10` | 2 | 0 | 1 | 1 | **a** grounded (1 untestable) |
| state | `S11` | 1 | 0 | 1 | 0 | **a** grounded |
| state | `S12` | 0 | 0 | 0 | 0 | **u** untestable form |
| state | `S13` | 1 | 0 | 1 | 0 | **a** grounded |
| state | `S14` | 0 | 0 | 0 | 0 | **u** untestable form |
| state | `S15` | 0 | 0 | 0 | 0 | **u** untestable form |
| state | `S16` | 4 | 0 | 4 | 0 | **b** literature |
| state | `S17` | 1 | 0 | 1 | 0 | **a** grounded |
| state | `S18` | 0 | 0 | 0 | 0 | **u** untestable form |
| state | `S19` | 1 | 0 | 0 | 1 | **a** artifact-only — hand-checked |
| state | `S2` | 2 | 0 | 2 | 0 | **a** grounded |
| state | `S20` | 0 | 0 | 0 | 0 | **u** untestable form |
| state | `S21` | 1 | 0 | 1 | 0 | **b** literature |
| state | `S22` | 1 | 0 | 1 | 0 | **a** grounded |
| state | `S23` | 0 | 0 | 0 | 0 | **u** untestable form |
| state | `S24` | 3 | 0 | 2 | 1 | **a** grounded (1 untestable) |
| state | `S25` | 2 | 0 | 1 | 1 | **b** literature (1 untestable) |
| state | `S3` | 2 | 0 | 2 | 0 | **a** grounded |
| state | `S4` | 1 | 0 | 1 | 0 | **a** grounded |
| state | `S5` | 3 | 0 | 3 | 0 | **b** literature |
| state | `S6` | 2 | 0 | 1 | 1 | **b** literature (1 untestable) |
| state | `S7` | 1 | 0 | 1 | 0 | **a** grounded |
| state | `S8` | 3 | 0 | 3 | 0 | **a** grounded |
| state | `S9` | 2 | 0 | 1 | 1 | **a** grounded (1 untestable) |
| values-and-provenance | `F1` | 2 | 1 | 0 | 1 | **b** literature (1 untestable) |
| values-and-provenance | `F10` | 1 | 1 | 0 | 0 | **b** literature |
| values-and-provenance | `F11` | 3 | 2 | 0 | 1 | **b** literature (1 untestable) |
| values-and-provenance | `F12` | 0 | 0 | 0 | 0 | **u** untestable form |
| values-and-provenance | `F13` | 1 | 1 | 0 | 0 | **b** literature |
| values-and-provenance | `F14` | 0 | 0 | 0 | 0 | **u** untestable form |
| values-and-provenance | `F15` | 1 | 0 | 0 | 1 | **a** artifact-only — hand-checked |
| values-and-provenance | `F16` | 3 | 1 | 1 | 1 | **a** grounded (1 untestable) |
| values-and-provenance | `F17` | 2 | 0 | 2 | 0 | **a** grounded |
| values-and-provenance | `F2` | 4 | 1 | 2 | 1 | **b** literature (1 untestable) |
| values-and-provenance | `F3` | 0 | 0 | 0 | 0 | **u** untestable form |
| values-and-provenance | `F4` | 1 | 1 | 0 | 0 | **b** literature |
| values-and-provenance | `F5` | 2 | 1 | 1 | 0 | **b** literature |
| values-and-provenance | `F6` | 2 | 0 | 2 | 0 | **b** literature |
| values-and-provenance | `F7` | 2 | 0 | 2 | 0 | **b** literature |
| values-and-provenance | `F8` | 0 | 0 | 0 | 0 | **u** untestable form |
| values-and-provenance | `F9` | 0 | 0 | 0 | 0 | **u** untestable form |
