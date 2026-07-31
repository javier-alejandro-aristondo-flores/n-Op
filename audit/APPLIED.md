# Corrections applied — auditor 2

Every edit below is mechanical, was verified against a primary source or the corpus's own
declaration, and required no physics judgement. **Physics-gated items are untouched** and
remain Javier's: the vector-potential slot's identity, the metastability band's currency,
the continuity sign convention and whether the state needs a second current field, the
nudged-elastic-band force-convergence tolerance's currency, whether the oracle stays absent
at inference, and stage ordering.

Landed as one commit on `audit2-mechanical-corrections`, so reverting is one command.

---

## 1 · `Zoroddu PRB 63` → `PRB 64` — 3 sites

**Finding:** `audit/LITERATURE.md`. **Evidence:** `10.1103/PhysRevB.63.045208` does not
resolve. The paper is *Phys. Rev. B* **64**, 045208 (2001) — Zoroddu, Bernardini,
Ruggerone & Fiorentini, *"First-principles prediction of structure, energetics, formation
enthalpy, elastic constants, polarization, and piezoelectric constants of AlN, GaN, and
InN."* Positively identified on full author list, page, year and subject; volume off by one.

| site | before | after |
|---|---|---|
| `journals/oracle/accuracy/accuracy-ledger.md:313` | `Zoroddu PRB 63 (2001)` | `Zoroddu PRB 64 (2001)` |
| `data/reference-data/polarization-piezoelectric.csv:2` | `Zoroddu PRB 63 045208 (2001)` | `Zoroddu PRB 64 045208 (2001)` |
| `data/reference-data/polarization-piezoelectric.csv:3` | `Zoroddu PRB 63 (2001)` | `Zoroddu PRB 64 (2001)` |

Controls: a known-real DOI resolved and a fabricated DOI did not, in the same run.

## 2 · Retired marker `GAP` → `UNSEEDED` — 8 cells

**Finding:** `audit/COMPLETENESS.md` finding 2. **Evidence:** `agent-contract.md:255`
declares `missing-data-marker: {GAP: UNSEEDED}`, and `UNSEEDED` is already the live marker
across 8 pages (16 uses in the accuracy ledger alone). All 8 stragglers were in
`data/reference-data/transport-coefficients.csv`, which the checker does not sweep.

Scope was restricted to **uppercase standalone `GAP`**. Deliberately *not* changed:

- `agent-contract.md:255` — the retirement declaration itself.
- `glossary.md:186`, `traps.md:673` — entries that exist to warn about the token.
- `forced-decisions.md:24` — the **GAP computer-algebra system**, a proper noun.
- The lowercase `gap` **Source class** on several rows — that is a separate, undeclared
  vocabulary (`COMPLETENESS.md` finding 4) and is not resolved by this retirement.

### One thing the blind substitution broke, and it is the warning made concrete

`breakdown-field-slope-kBR` read *"normalized K-1 is a GAP"*. Mechanical replacement
produced **"is a UNSEEDED"** — ungrammatical, because `GAP` was being used as a *noun*
there and `UNSEEDED` is a *marker*. Corrected by hand to *"normalized K-1 is UNSEEDED"*.

This is exactly the hazard the register attaches to the larger registry retag: **a blind
symbol-to-word map launders meaning.** It is the reason that retag must be done cell by
cell against each row's own provenance, and not with `sed`.

---

## Verification

| check | result |
|---|---|
| `python tools/check_structure.py --check` | **exit 0** |
| `python tools/check_the_checker.py` | **34 probes · 34 caught · 0 missed · 0 stale · 29 error sites · 0 unreached** |
| Diff scope | 4 files, 12 insertions, 12 deletions |
| Full diff reviewed before commit | yes — and it is what caught the grammar defect above |

`generated/corpus.json` regenerated, as required after any page edit; the stale-index gate
fired correctly on the first attempt and was the reason to regenerate rather than a defect.

---

## Held, not applied

- **The registry retag** (508 retired tag cells). The register's condition stands: it lands
  **with** the checker extension that sweeps `data/`, or not at all — the retag alone leaves
  the same hole open for the next drift. And per the incident above, cell by cell.
- **`Source class` vocabulary** — 22 values, 19 undeclared, closing with "and so on".
  Needs a decision on the controlled set before anything is rewritten.
- **The four undeclared uncertainty encodings** — a schema decision, not a data edit.
- **Everything resting on an unverified literature claim** — 34 of 49 citations are
  unverified because the method could not reach AIP article numbers, not because they are
  suspect.
