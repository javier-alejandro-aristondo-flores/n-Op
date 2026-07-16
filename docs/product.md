# n-Op — Product Behavior (`/physics` as a deliverable)

> The **behavioral contract of the finished program**: what a user runs, hands in, and
> gets back — deliberately silent on languages, frameworks, and wire formats (those are
> recorded open decisions, §9). A hand-written companion to the atomic spec, like
> `docs/computational-overview.md` and `docs/accuracy-ledger.md` — **not** part of the
> lint-enforced atomic tree; every claim cites its canonical `arch-xx` / `impl-xx` source
> so it can be verified rather than re-derived. Fixed by discussion 2026-07-16; amend by
> editing this file against the atomic tree, never the reverse.

---

## 1. Identity

The product is **the oracle**. `/physics` compiles a description of a crystal into a fast,
pure scoring function; that function — not a service, not a framework, not the neural
operator — is what ships. The PINO (`/informed-operator`) is the product's most important
*consumer*, not the product (`arch-02-libraries`); every loop that drives either of them
lives outside both, in `/interface` (`arch-01-purpose`).

**Mission, stated precisely.** "Verify whether a crystal is valid" means: *produce the
slot-by-slot evidence from which validity is judged*. The oracle measures disagreement
with the laws at full granularity and hands over the itemized result; it never renders a
verdict. Judgment belongs to the consumer looking at the evidence.

**Consumers.** Two classes, one surface (`arch-16-pino-bridge`):

- `/informed-operator` — the hot-loop consumer: millions of calls, gradients on.
- People like us — computer scientists screening candidates or reconciling them against
  measured data, from a shell or their own programs.

**Principles** (named, so future additions can be tested against them):

- **YAGNI.** No machinery without a present need; a flag beats a framework.
- **Evidence, never verdicts.** No aggregation, thresholding, or judgment anywhere in the
  product (`arch-11-residuals`).
- **Refusal is first-class.** What the oracle cannot stand behind is absent, and the
  absence is accounted for — never papered over (`arch-12-cert`).
- **No natural language.** Every artifact is machine data: keyed numbers, enum codes,
  numeric witnesses, hashes.
- **Agnostic by purity.** The emitted oracle assumes nothing about its caller: pure
  function, flat arrays at the boundary, no loop ownership
  (`informed-operator/design/learnable-structure-requirements.md` mirrors the same
  commitments from the consumer side).
- **Score, not solve.** The caller supplies complete candidate states; the oracle never
  fills in missing pieces (`arch-01-purpose`).

## 2. Deployment shape: a compiler and its oracle-files

The product has two parts, matching the architecture's two phases (`arch-07-pipeline`,
`docs/computational-overview.md`):

- **The compiler** — a CLI. Run once per crystal identity: identity in, **one
  self-describing artifact file out** ("oracle-file"). Compose time is seconds–minutes;
  it is where all symbolic work, pruning, structure exploitation, and derivative
  synthesis are spent.
- **The oracle-file** — the emitted kernel, persisted. Loaded by any program and called
  like a function, microseconds–milliseconds per call, millions of times. This file is
  the thing consumers actually hold.

**What an oracle-file contains** (one file on disk; four things inside):

1. **The callable** — `Validate` (§4), with its gradient entry point baked in at compile
   time (`arch-16-pino-bridge §16.1`). Consumers that never need gradients simply never
   invoke that entry point.
2. **The static slot schema** — the complete table of every check the kernel contains:
   slot key → producing registry row, axis coordinates, closed-enum tags, error scale σ
   (§4). This makes the file self-describing: a consumer can enumerate its contents with
   no other resource.
3. **Its identity** — the content hash of the compiled kernel (`arch-20-representations
   §20.4`), the identity descriptors it was compiled from, and the registry/spec versions
   it was compiled against. **File hash = kernel hash**: attribution, caching, and
   "which oracle produced this result?" are filesystem-level facts.
4. **Its certificate reference** — a hash-pinned pointer to the certification evidence
   for this kernel (`arch-12-cert`), so trust travels with the file.

**Behavioral consequences, stated as rules:**

- **One file per crystal identity.** A kernel is specialized to one
  `(PeriodicityStructure, SiteDecoration, Environment)` tuple (`arch-07-pipeline §7.1`).
  "The oracle" as the general object is the *compiler*; each file is the oracle *for one
  instance*. Searches over discrete identity space produce many files — cheap under
  content-addressed caching, but the mental model is "a directory of kernels," never
  "one universal file."
- **Environment-box validity.** The compile-time environment fixes the *envelope* — which
  checks exist — and stamps the file with its validity box (`arch-13-applicability`);
  the runtime `env` argument varies *within* that box. Outside the box: recompile. The
  stamp makes out-of-box use mechanically detectable.
- **Oracle-files are immutable.** New pinned targets (§6), a new registry version, or a
  new identity each produce a **new file** with a new hash. Nothing is ever edited in
  place; every result stays permanently attributable.

## 3. Inputs

**Identity (to the compiler, once).** The crystal's discrete description: what repeats,
how it is decorated, the operating conditions (`arch-03-inputs`). Its semantic model is
**CIF content plus an environment record** — the crystallographic interchange content
every materials database and simulation code already produces, extended with the
operating-condition fields no crystallographic format carries. (A CIF alone is not a
scoreable object; it is a compile request.)

**State (to the oracle-file, per call).** The full state object as `arch-04-state`
defines it — geometry, sites and momenta, species, the electronic degrees of freedom,
fields. This is deliberately a **superset** of any standard interchange format: the
missing pieces are precisely what the neural operator learns to supply (score-not-solve).
The state type is the product's own; no external standard exists for it and none should.
*Structural* well-formedness (shapes, finite values) is the caller's obligation;
*physical* admissibility is scored, never presupposed (`arch-11-residuals`).

**Environment (per call).** The operating-condition record, varying within the file's
stamped box (§2).

## 4. The call contract

One entry point (`arch-16-pino-bridge §16.1`):

```
Validate(state, env, request, gradient) →
    residuals : Map<SlotKey, Float>     -- raw law-violation scores
    values    : Map<Name, Value>        -- requested derived quantities (numbers/arrays)
    cograds   : optional gradient map   -- only when gradient = Compute
    kernel    : content hash            -- the producing oracle-file's identity
```

**Keyed floats only.** A slot key is a structured value — (producing rule × axis point),
renderable as a hierarchical path (`arch-11-residuals`). The residual value is **raw**:
the oracle never normalizes, weights, sums, or judges across slots.

**The static schema carries everything that does not vary per call:** for each key, the
producing registry row, the axis coordinates, closed-enum tags (category / bundle /
dressing — `impl-07-residual-factory`, for subset selection and grouping only), and the
error scale σ (`arch-11-residuals §11.7`). Consumers who want cross-slot comparability
compute `z = value / σ` themselves — a join against the schema, not a product output.

**Refusal is absence.** A check the oracle cannot stand behind for this instance —
inapplicable, outside the certified envelope, or cert-refused — is not in the compiled
kernel, so its key is simply not in any map. The *reason* is machine data in the
certification record: a closed-enum refusal mode plus numeric witnesses
(`arch-12-cert`). No prose, anywhere.

## 5. Selection

Two flag layers, both already in the architecture — no new machinery:

- **Compose-time scoping.** The compile request names the observable bundles and residual
  categories wanted (`arch-07-pipeline §7.1`, vocabularies of `arch-09-vocabularies`);
  everything unrequested or inapplicable is pruned and never becomes code.
- **Call-time subsetting.** `Validate`'s `request` parameter evaluates the full kernel, a
  set of slot keys, or a set of named quantities (`arch-16-pino-bridge §16.1`).

*Recorded refinement (future `arch-16-pino-bridge` edit, deliberately not made yet):*
`request` should additionally accept the schema's closed-enum tags as selectors
("everything in this family"), so subsetting never requires the caller to enumerate keys.
Selector sugar over the existing enums; nothing more.

## 6. Reconciliation and design: one mechanism

`Import` pins an external value into the graph as a first-class check —
`(named-target, value, σ, provenance, coverage-mask)` → a pinned reference node and its
slots, coverage-masked to exactly the axis points the datum constrains
(`arch-16-pino-bridge §16.2`). Two readings of the same object:

- **Reconciliation (measurements).** Pin measured data; the slots read "disagrees with
  reality by this much." This is how a user asks *"is this candidate consistent with what
  I measured?"* — the answer arrives as ordinary slots in the residual map.
- **Design (aspirations).** Pin desired property values; the identical slots read "misses
  the spec by this much." Law-consistency slots and target slots sit side by side in one
  differentiable objective.

**In the artifact model, `Import` is a compiler input** (a targets file handed to
`compile`), because pinning inserts graph nodes at compose time
(`arch-16-pino-bridge §16.2`). New pins → new oracle-file. That is a feature: every
reconciliation or design result is attributable to a specific, hash-named artifact.

**The two loops are mirror images.** Training proposes states and sinks the oracle's
gradients into the *operator's weights*; design proposes candidates and sinks the same
gradients into the *candidate itself*. One oracle, one call surface, two gradient sinks —
both loops live in `/interface`, never in the product (`arch-01-purpose`).

**The design-variable boundary, stated honestly.** Within one oracle-file, the
*continuous* variables — cell, positions, composition fraction where the registry treats
it as an axis — are directly optimizable through the baked gradients. The *discrete*
variables — species, decoration, symmetry family — are the compiler's specialization
axis: searching them means enumerate-and-compile (many files, cached by content) or an
external proposer. Static, instantaneous-property design works on today's contract;
**lifetime design** ("properties after N hours at conditions") additionally requires a
time-evolution capability, which this spec deliberately does not claim (§9).

## 7. The CLI

Three verbs, minimal by principle:

- `compile` — identity (+ environment, + channel flags, + optional targets file) → one
  oracle-file.
- `inspect` — oracle-file → its static schema and identity, enumerated (the internal
  `EnumerateObservables` made visible; `arch-16-pino-bridge §16.3`).
- `validate` — oracle-file + state file (+ env, + request flags) → the keyed-float maps,
  serialized. A convenience wrapper for shell use around the same callable.

In-program loading of the oracle-file is the **primary** consumption path; the CLI is the
same function with file handles. Nothing interactive, nothing stateful, no daemon.

## 8. What the product is not

- It holds no state values, never evolves anything, never trains, and owns no loop
  (`arch-01-purpose`, `arch-02-libraries`).
- It never aggregates or judges: no verdict bit, no score rollup, no thresholds.
- It never calls external simulation software at runtime; external data enters only as
  pinned `Import` values at compile time.
- It accepts no open-ended expressions: the grammar is the closed vocabularies of
  `arch-09-vocabularies`, and requests either compile or are rejected at compose time.
- It emits no natural language.

## 9. Open decisions and unclaimed capabilities

Recorded here in the manner of `arch-18-open-decisions`; none blocks the v1 verbs
(screening, reconciliation):

1. **Time-evolution verbs (rollout; endpoint/lifetime queries) — deliberately
   unclaimed.** Pending the independent scorer↔stepper duality research
   (`docs/specs/2026-07-16-evolver-duality-research-brief.md`). Nothing in this document
   depends on its outcome.
2. **Loading convention / ABI.** How a non-native program loads and calls an oracle-file
   (native module vs. a flat-array C-style ABI vs. both). The abstract contract — one
   self-describing file, flat arrays at the boundary — is fixed; the container is not.
3. **Wire formats.** Serialization of state files, residual/value maps, and the schema
   table for the CLI surface. Constrained by the canonical-serialization discipline of
   `arch-20-representations §20.4`; otherwise open.
4. **Compile-cache management.** Policy for the kernel store that enumerate-and-compile
   design searches rely on (eviction, sharing, provenance listing). Content addressing
   makes correctness free; only policy is open.
