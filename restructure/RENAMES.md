# The four nomenclature renames — proposal (D17)

All four are one defect: **a serial or overloaded token doing a job a descriptive
name should do.** It is the same defect the corpus already fixed once for page ids
on 2026-07-22, left unfixed in four other vocabularies.

Nothing here is applied. These are proposals for sign-off.

---

## 1. The differentiability vocabulary

**Now:** `D0 | DN | D1 | D2 | D3 | D4` — 134 registry rows, 122 backticked prose uses.

Three things are wrong with it, and they compound:

- **`DN` sits inside a numeric series it is not part of.** Canon has to carry the
  written warning *"`DN` is not inside `D0–D4`"* (`10.3-audit-prompt:116`). A
  vocabulary that needs a footnote to be read correctly has the wrong names.
- **`D3` is a *refinement of* `D2`, not a successor to it** — `named-formulas:92`
  says so explicitly, and that every `D3` row runs `D2`'s gate *plus one more*. The
  numbering implies a sequence that contradicts the semantics.
- **The tags collide with physics.** `conventions:347`: `` `D1` `` is a
  differentiability tag, `D1` unbacked is a wurtzite deformation potential. The
  backtick rule exists *only* to hold this collision apart.

| Now | Rows | Proposed | Means |
|---|---|---|---|
| `D0` | 1 | **`read`** | a stored or passed-through value; identity adjoint |
| `D1` | 91 | **`direct`** | analytic closed form or autodiff-native; gradient available directly |
| `D2` | 23 | **`adjoint`** | adjoint required, gated vJp-vs-JvP at registration |
| `D3` | 5 | **`fixpoint-adjoint`** | implicit-function adjoint over a converged fixed point — visibly a refinement of `adjoint`, which is what it is |
| `D4` | 6 | **`relaxed`** | genuinely non-smooth, ships a named relaxation |
| `DN` | 6 | **`none`** | no useful derivative; integer, categorical, boolean, set-valued; not relaxable in place |

Three defects die at once: `fixpoint-adjoint` reads as refining `adjoint`, `none`
reads as outside the others, and the backtick rule becomes unnecessary because no
word collides with a deformation potential.

**This also retires the `D4` surrogate/relaxed drift permanently.** That defect
survived a retag because `D4` is an opaque token — it can silently mean two things.
`relaxed` cannot.

---

## 2. The dressing layers

**Now:** Layer 1 · 1.25 · **1.75** · 2 · 3 — 46 mentions. A serial scheme that ran out
of room and began subdividing; `1.75` is where it became unreadable.

| Now | Proposed | Means |
|---|---|---|
| Layer 1 | **`substrate`** | bare substrate |
| Layer 1.25 | **`one-shot-dressing`** | closed-form dressing, pure functions, no iteration |
| Layer 1.75 | **`iterative-dressing`** | iterative fixed-point dressing; deferred to V2 |
| Layer 2 | **`property-machinery`** | the rest of the PhysicsGraph |
| Layer 3 | *(not a layer)* | the PINO. It lives in `/informed-operator` and is a **library**, not a layer of `/physics` |

Note the parallel this exposes: `one-shot` vs `iterative` is the *same distinction* as
`direct` vs `fixpoint-adjoint` above. Under numbers that was invisible.

Layer 3's demotion matters — under the three-library corpus, calling the PINO a "layer
of the oracle" is a category error the numbering concealed.

---

## 3. The pipeline stage count

**Now:** "the **4+1** stage compose-time pipeline" — a canonical topic name whose own
table (`4.2:268-275`) enumerates **six** rows: 1, 2, **2.5**, 3, 4, 5. 9 uses of "4+1",
180 ordinal stage references.

**Proposed: drop the count from the name and stop numbering the stages.** The topic
becomes `compose-time pipeline`. The stages already have real names:

> symbolic lift → symmetry quotient → invariant synthesis → algebraic simplification
> → lowering & adjoint synthesis → runtime kernel application

**The anchor scheme dissolves this for free.** `compose-time-pipeline §2.5` becomes
`[compose-time-pipeline#invariant-synthesis]`. There is no stage number left to be
wrong about, no "2.5" to explain, and no count in a topic name to contradict a table.
The compose-time/runtime split — the distinction "4+1" was reaching for — is stated
where it belongs: in the table's own *Runs* column, which already says it.

---

## 4. `GAP`

**Now:** three meanings (`traps §59`), and the trap is **advisory only** — nothing
enforces it.

| Sense | Where | Disposition |
|---|---|---|
| **missing-data marker** — a value genuinely unavailable, cert-refused rather than guessed | 10 CSV cells (`GAP — paywalled …`) plus provenance-types `gap` / `genuine gap`, and `reference-battery` | **Rename → `UNSEEDED`** |
| **GAP the computer-algebra system** | `open-decisions`, the language study | keep — external proper noun; always write in full as *"the GAP computer-algebra system"* |
| **Gaussian Approximation Potential** | `deriv-csp` Part A | keep — external proper noun; always write in full |

`UNSEEDED` is proposed because *seed* is already the corpus's own verb for this
(`accuracy-ledger` uses it 12 times: "seed from the ledger", "do not seed until…"), so
the marker names the state it actually denotes — the row exists, the value is not
seeded. It cannot collide with anything.

**And it becomes checkable.** Today a sweep for missing data collects a language
candidate and an ML potential; `traps §59` can only advise. With a token that means
one thing, the checker can enforce it — one more advisory rule converted into a
machine-checked one.

---

## 5. `module` — found while writing this document

Added after Javier asked what "module" meant in §2. It meant *"one of the three
top-level libraries"* — and **the corpus's word for that is `library`, not `module`.**
`library-landscape` owns the topic as `library partitioning`; canon uses *library* 77
times against *module* 13. Using `module` for it would have added a **fourth** sense to
an already three-way-overloaded word, i.e. exactly the `GAP` defect, committed fresh
while documenting the `GAP` defect.

| Sense | Where | Disposition |
|---|---|---|
| **a library** — `/physics`, `/informed-operator`, `/interface` | `audit-prompt:3,15` | **forbidden.** The word is `library`. `audit-prompt` leaves the corpus anyway |
| **a native code module** — the loading convention, vs a flat-array C ABI | `product:253` | **keep** — an external FFI term meaning exactly this. Always written *"native module"*, never bare |
| **an observable module** — a file-tree grouping by output data-shape | `observable-bundles:49`, `canonical-vocabularies:170` | **rename.** `bundle` is already the canonical unit (11 observable bundles); a second word for a grouping of the same things buys nothing. Proposed: say *grouping*, or drop the sentence |
| *(historical)* "module layout that no longer exists" | `architectural-principles:25` | **delete** — scaffolding |

Two of the four senses die with containers already being removed. What is left is one
external term that must always carry its qualifier, and one redundant coinage.

**The general rule this establishes**, and the one the agent contract should carry:
*when the corpus already owns a word for something, no synonym is admissible.* That is
enforceable — a vocabulary sweep against the owned-term list — and it would have caught
this before it reached a document.

---

## Cost

All five land in the same pass that rewrites the pages, so there is no second
migration. Reach:

| Rename | Mechanical | Judgement |
|---|---|---|
| D-tags | 134 CSV rows + 122 prose uses | none — the map is 1:1 |
| Layers | 46 mentions | Layer 3's demotion to "a library, not a layer" |
| `module` | 13 uses, 3 senses | which of senses 1–2 survive (§5) |
| Pipeline | 9 + 180 ordinal refs | none — anchors replace ordinals corpus-wide anyway |
| `GAP` | 10 CSV cells + 2 provenance-type values | none |

The pipeline row is nearly free: those 180 ordinal references are being converted to
anchors regardless.
