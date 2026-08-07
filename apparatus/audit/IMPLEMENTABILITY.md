# Pass A — can the oracle be built from this corpus?

**No. Not as it stands.**

Four auditors, eleven implementation units, no contact between them. **75 findings — 61
ABSENT, 14 UNDERSPECIFIED.** The question was never *"does a page discuss this"* but *"can an
implementer type it,"* and the answer at the core of the system is repeatedly no.

This is not a verdict on the corpus's quality. Auditor 1 found it well-formed; auditor 2
found it truthful; pass B found its physical coverage of its own target environment
**stronger** than a skeptical prior assumed. The corpus is an excellent *specification of
intent*. It is not yet a specification anyone can build from, and the gap is larger than its
own 51 declared open questions admit.

---

## Verification, before any finding is believed

| check | result |
|---|---|
| Quotations grounded by content against the live corpus | **121 of 122** |
| The one remainder | a regex in a control paragraph, not a quotation |
| `ground.py` controls (9 positive, 4 negative, incl. the en-dash and Unicode classes) | **13 of 13 pass — instrument trusted** |
| Fabricated quotations | **zero** |

**Two instrument bugs were found and fixed during this verification**, both of which would
have made the pass look fraudulent:

1. **Blockquotes used for two purposes.** Agents put their control searches inside `>` blocks,
   so the grader scored regexes and grep commands as failed quotations — 114 false ABSENT.
   **My brief's fault:** it specified blockquotes for evidence and never reserved them for
   verbatim corpus text.
2. **Markdown table-cell pipe escaping.** The corpus writes `\|` inside table cells so the
   table does not break. A quotation of table content can never match until that escape is
   normalized away. This falsely condemned a quotation that is present verbatim at
   `cert-obligations.md`.

Before the fixes: 27 of 65 quotations "absent" in one file. After: one, and it is a regex.
**The instrument was wrong, not the auditors** — the sixth and seventh time in this program,
and the reason nothing is believed until its controls fire.

---

## Four independent convergences

The auditors were forbidden to contact each other, held different unit assignments, and read
overlapping-but-different page sets. They independently landed on the same holes:

| Hole | Found by |
|---|---|
| `Layer0Type` — the type field on **every** graph node — is declared a closed universe with dense ordinals and never enumerated | **all three** of cert, state, compile |
| `ObservableRef` — the key type of two of the three public exports — is defined nowhere | cert, state |
| The closed-enum refusal mode is never enumerated | cert, state |
| The environment box has no type and no supplier | cert, state |

Convergence between non-communicating readers is the strongest evidence this method
produces. These four are not artifacts of one auditor's lens.

---

## What is actually missing, by theme

### 1 · There is no unit system

`R1` — **no unit system is declared anywhere in the corpus**, and the single pointer to one
resolves to a page that does not define it.

This is the deepest finding of the audit, because everything numeric rests on it: every
residual, every tolerance, every accuracy target, every imported datum's standard deviation.
Two independent routes reached it. Pass C found the macro drift-diffusion balance
dimensionally inconsistent — carrier density in `m⁻³` added to current divergence in
`A·m⁻³`, terms that differ by exactly one factor of charge. **That is not a typo; it is what
happens when no unit discipline exists to catch it.**

**Re-derived by hand, independently, with a firing control.** `SI units`, `atomic units`,
`Hartree atomic`, `unit convention`, `base units` and `all units` each return **zero files**.
The control fires — `eV` appears in 7 files and `meV/atom` in 3 — so unit vocabulary is
reachable by search and the absence is real. Meanwhile the registry *requires* what it never
defines:

> | `signature` | typed inputs to output, with units |

**And the corpus knows the hazard.** Its only use of the phrase is a trap warning:

> The 4π in the source term rides the unit system. *Breaks:* factor-4π errors across the
> electromagnetic sector. — advisory

The corpus identifies the unit system as load-bearing, names a specific factor-4π failure
mode across an entire physical sector, and **still never declares which system it uses.**
That is stronger than the finding as originally reported.

### 2 · The core types are names without definitions

`ObservableRef`, `Layer0Type`, `AxisLabel`, `EvidenceOps`, `InputKind`, `EnvField`,
`Witness`, `CrystalSymmetryGroup`, `canonical_node_bytes`. Each is load-bearing; none is
defined. Without `canonical_node_bytes` a `NodeId` cannot be computed, and without `NodeId`
the content-addressed graph — the substrate the whole design rests on — cannot exist.

`X18` adds that **dense ordinals are assigned by no stated rule, so no address is
reproducible.** Content-addressing that is not reproducible is not content-addressing.

### 3 · The registry is titles, not bodies

`R3` — the manifest names **132 formulas and gives a writable body for 19. Seventy-two rows
carry neither an expression nor a citation** that would let one be recovered.

The stratified sample is the only proper rate in this pass, and it was chosen deliberately to
span every axis the manifest codes — differentiability, cost tier, bundle, provenance, anchor
class — loading both extremes:

> | verdict | count | rows |
> |---|---|---|
> | DETERMINED | 3 | 74, 103, 124 |

**Three of twenty rows are implementable.** The corpus's own principle is that every emitted
number leads back to a numbered, literature-cited registry row. For most rows, the row is
where the trail ends.

### 4 · "Refusal is absence" — the corpus's headline principle — has no mechanism

`X9`, `X10`, `S10`. The principle is stated forcefully and repeatedly: what the oracle cannot
stand behind is simply not in the kernel, and the reason is machine data, never prose. But
**nothing connects a failed obligation to a missing check.** No compile stage mentions
refusal. The closed enum of refusal modes is never enumerated.

And the corpus's one admission that a refusal enum is unwritten is **scoped to the evolver
hand-off** — a narrow confession attached to a system-wide dependency. That scope mismatch was
found independently by the cert auditor, unprompted.

### 5 · The compiler stages are named, not specified

`C10` — equality saturation with **no rule set, no termination rule, and no extraction
procedure**. `C14`, `C15` — the compression-plan decision has no thresholds, no precedence,
and its per-plan error target has no value and no selection rule. `C17` — the adjoint-tape
schedule is an unnamed heuristic with no bound and no tape. `C4` — `CrystalSymmetryGroup` is
consumed by two stages and constructed nowhere.

The corpus is precise about *why* each stage exists and what it buys. It does not say what
any of them does.

### 6 · Certification binds on a field that does not exist

`X1`, `X2` — each obligation is declared a generic function over one typeclass axis, and **no
record carries a typeclass axis field.** Four of the ten obligations name no axis at all. So
for most obligations the governed set is not machine-determinable — which is auditor 2's
finding 7, arrived at independently and sharpened from "the relation is absent" to "and here
are precisely which four obligations have no binding at all."

`X5` — `Pending` is a verdict nothing produces. `X8` — the `applicability` field the predicate
contract requires exists on no manifest schema.

### 7 · The deliverable has no format

`X13` — the oracle-file, the thing consumers actually hold, **has no on-disk format**.
`X16` — the three command-line verbs have no arguments, no input format, no output encoding
and no failure behavior. `X14` — *"file hash equals kernel hash"* names three hashes and
reconciles none of them.

---

## The honest caveat: this is a census, not a rate

**I primed for absence.** The brief said *"ABSENT is what this audit exists to find"* and
*"DETERMINED items need no report beyond a count."* So 61 absences is a **census of specific
things an implementer cannot type — not a percentage of the corpus.**

Where a denominator was reported it is: ≈22 determined against 20 findings in the compile
stages; 9 determined against 20 findings in state and identity. Only the registry sample is a
true rate, and it is **3 of 20**.

Do not read this pass as *"85% of the corpus is missing."* Read it as *"here are 75 named,
grounded, individually-checkable holes, and the load-bearing ones are at the center rather
than the edges."*

## Coverage not reached

- The registry was **sampled, not swept** — 20 of 134 rows, stratified and declared.
- Pass B's angle 3, testing whether the seven slots really are the irreducible degrees of
  freedom, was **not run**.
- `DETERMINED` items were counted, not enumerated, so this pass cannot state what *is* buildable.
