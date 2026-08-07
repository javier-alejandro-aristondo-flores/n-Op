# Phase 1 gate — the disposition list

Eleven read-only surveyors over 165,274 words at `2af93d2`. Nothing has been
edited in the corpus; `journal/`, `physics/`, and `informed-operator/` are byte-for-byte
unchanged and both checkers still report clean.

## What Phase 1 produced

| | |
|---|---|
| Disposition rows | **1,525** — keep 413 · delete 489 · mine 407 · move 207 |
| Open questions | 121 → the emitted register (plan §5) |
| Log-worthy advancements | 128 → `log/timeline.md` (plan §7) |
| Contradictions | **89** — collected, not resolved. Auditor 2's starting corpus |
| Unparsed after repair | 9 (one `— (gap)` marker, eight blank spacer rows) |

Merged output is in `restructure/merged/`: `rows.md`, `open.md`, `log.md`,
`contradictions.md`, `notes.md`, `conflicts.md`. Regenerate with
`python restructure/merge.py`.

## What Phase 1 changed about the plan

Five things the plan got wrong or did not know. All are now corrected in it.

1. **The citation split is 47%, not ~40%.** 315 bracketed against 289 backticked,
   measured against the real 58-id set. Worst page: `computational-overview` at 4
   against 42 — **91% unchecked** — on a page that claims the checkers hold it to the
   same rules as any other.
2. **`§N` coordinates are unchecked into 57% of the corpus.**
   `check_book_structure.py:469` skips resolution when the target has no numbered
   headings, and 33 of 58 pages have none. A `§99` into any of them passes. Found by
   planted probe, not by reading. The plan's original rationale (ordinals "rot when a
   heading is inserted") was true but minor.
3. **A third homeless type: `Crystal`.** Zero definitions against eight
   `(Crystal, Environment)` signature uses across five pages — and that signature is
   on every registry row, every `CouplingChannel`, every `ResidualGenerator`.
4. **A new defect class: the dangling *quotation*.** `multiscale-state §1` quotes
   `unified-state` as classifying defect populations "emergent — coarse-grainings of
   `x(t)`" and argues at length against it. That string appears nowhere in
   `unified-state`; its only corpus-wide occurrence is inside the quotation of it.
5. **Delimiter-sensitive formats cannot carry physics.** Literal `|` in bra-kets
   (`⟨ψ_{m,k+q}|∂_{qν}V|ψ_{n,k}⟩`) and norms (`Σ_κ M_κ|e_κ|²`) split sixteen
   disposition rows into up to eleven columns — the third appearance of the same class
   after the corpus's own CSV arity bug and Phase 1's merge tooling. The new checker
   must validate **table arity per page**; nothing does today.

## Structural exposure the demolition creates

**Three surviving artifacts cite dying containers**, and two of them sit in
`registry-manifest.csv`, which **outranks canon pages** in the authority order:

| Artifact | Cites | Consequence |
|---|---|---|
| `registry-manifest.csv` row 48 (`MIGS-corrected-barrier`) | `deriv-defects §F.3` | provenance orphaned when ch. 11 dies |
| `registry-manifest.csv` row 50 (`interface-bond-counting`) | `deriv-generator-catalog §6` | same |
| `material-constants.csv:42` (β-Ga₂O₃ `E_d` = 25 eV) | "non-equilibrium stratum H.1" | **worse — see below** |

The `E_d` row is the sharp one. The CSV names the appendix as its source; the
appendix (`11.5:407`) states `Ga₂O₃ ~25 eV` as a bare parenthetical **with no
citation**; the row's provenance-type reads `literature-review` and no literature is
ever named. A value with no external provenance, laundered into canonical status.
Deleting ch. 11 removes even the appearance of a source. **Phase 2 must re-source it
or mark it unseeded — it cannot simply be carried.**

## Gate failures — CLEARED

- **38 serial open-question ids** (`OQ-1`, `Q-1`, `Q1`…) across `practice`, `program`,
  `appendix-b`, `appendix-c` — the serial-naming scheme the corpus retired on
  2026-07-22, reappearing in a fresh work product. All renamed to descriptive slugs.
- **20 shared targets** — checked pairwise. **Zero duplicates.** Every one carries
  genuinely different facts; the dominant pattern is an appendix derivation (the
  mathematics) landing on the same anchor as its registry entry (the composition),
  which is exactly the intended convergence.

## Convergent findings — 13

Gaps reached independently by more than one surveyor from different scopes.
Corroboration, not collision:

| found by | question |
|---|---|
| **4** | `environment-schema` · `adjoint-drift-monitoring` |
| 2 | `state-wire-schema` · `obligation-9-scope` · `g0w0-cost-scope-tag` · `implementation-language-picks` · `layer-175-minimum-spec` · `mesh-sigma-floor-undeclared` · `pde-mesh-adjoint-scheme` · `semiconductor-interface-predicate` · `surrogate-net-build-vs-adopt` · `unregistered-composition-formulas` · `response-causality-slot` |

**The serial ids were concealing two-thirds of this.** Before renaming, the detector
saw 4 convergent findings; after, 13. A serial id collides by construction, so a
genuine second sighting is indistinguishable from a numbering clash — which is a
second, independent argument for the descriptive-naming rule beyond readability.

## Gate decisions taken (2026-07-30)

| | |
|---|---|
| **D14** | `computational-overview` deleted; 25 originals routed to the pages that own what they cost; `corpus.json` emits a generated cost-and-complexity view |
| **D15** | `gamma-budget` merges into `gamma-hat` |
| **D16** | `properties` and `typed-compositions` stay separate; the coverage claim becomes machine-checked across them |
| **D17** | All four nomenclature defects renamed in the same pass; new names proposed before they land |

## Decisions that are yours

Three page-set changes and one vocabulary question. Every surveyor escalated rather
than guessing; none of these is dispositioned yet.

1. **`computational-overview` (6,475 words)** — delete outright, or keep with a real
   ownership claim? Its own charter (`4.4:38`) is to restate chapters 1–10. The
   surveyor's argument: a page whose charter is restatement cannot be made
   non-duplicating by editing it, and its vacuous `canonical-for` is not a coincidence —
   a page owning no topic distinct from its id is a page with nothing of its own.
2. **`gamma-budget` (246 words)** — merge into `gamma-hat`? One owned topic, one
   inbound reference, and `gamma-hat §5` already restates its two headline numbers
   without the derivation.
3. **`properties` (6.10) into `typed-compositions` (6.8)?** `6.8:39` says it writes
   "every property in `properties.md`" as a typed composition — the two are one
   artifact split in half, a checklist and its proof of coverage. Merging makes the
   coverage claim checkable. Against: nine paragraphs of reader-facing prose merged
   into dense typed pseudocode reads as two documents.
4. **The four nomenclature defects** — `D0 | DN | D1 | D2 | D3 | D4` where `DN` is not
   between `D0` and `D1`; `Layer-1.75`; a "4+1 stage" pipeline containing a "Stage 2.5"
   (its own table enumerates six); `GAP` overloaded three ways. Held at propose-only
   per plan §4, because renaming a technical vocabulary is a contents change.
