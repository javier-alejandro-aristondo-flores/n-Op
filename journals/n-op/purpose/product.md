---
id: product
title: "The product"
owns:
  - product identity
  - evidence never verdicts
  - product consumers
  - product principles
  - score not solve
  - deployment shape
  - oracle-file contents
  - oracle-file rules
  - state input obligation
  - environment argument
  - static slot schema
  - refusal is absence
  - selection surfaces
  - import as compiler input
  - the two loops
  - design variable boundary
  - command-line verbs
anchors:
  identity: "Identity"
  evidence-not-verdict: "Evidence, never verdicts"
  consumers: "Consumers"
  principles: "Principles"
  score-not-solve: "Score, not solve"
  deployment-shape: "A compiler and its oracle-files"
  oracle-file-contents: "What an oracle-file contains"
  behavioral-rules: "Three rules about files"
  state-input: "State, per call"
  environment-input: "Environment, per call"
  call-contract: "The call"
  static-schema: "The static slot schema"
  refusal-is-absence: "Refusal is absence"
  selection: "Selection"
  import-is-a-compiler-input: "Import is a compiler input"
  two-loops: "The two loops"
  design-variable-boundary: "The design-variable boundary"
  cli: "The command line"
depends-on:
  - purpose-and-scope
  - library-landscape
  - architectural-principles
  - unified-state
  - crystal-inputs
  - pino-bridge
  - residual-definitions
  - representation-substrate
  - cert-obligations
  - applicability-classifiers
  - compose-time-pipeline
  - canonical-vocabularies
  - accuracy-ledger
open-questions: []
---
# The product

The behavioral contract of the finished program: what a user runs, hands in, and gets
back.

## Identity

**The product is the oracle.** The oracle library compiles a description of a crystal
into a fast, pure scoring function; that function — not a service, not a framework,
not the neural operator — is what ships. The operator library is the product's most
important *consumer*, not the product ([library-landscape#operator]), and every loop
that drives either of them lives outside both ([purpose-and-scope#no-loops]).

## Evidence, never verdicts

"Verify whether a crystal is valid" means, precisely: **produce the slot-by-slot
evidence from which validity is judged.** The oracle measures disagreement with the
laws at full granularity and hands over the itemised result. It never renders a
verdict — no verdict bit, no score rollup, no thresholds, no aggregation across slots.
Judgment belongs to the consumer looking at the evidence. For a scientific instrument
this is the honest contract: it measures; it does not editorialise.

## Consumers

Two classes, one surface ([pino-bridge#surface]):

- **The operator library** — the hot-loop consumer: millions of calls, gradients on.
- **People** — computer scientists screening candidates or reconciling them against
  measured data, from a shell or from their own programs.

## Principles

Named, so that later additions can be tested against them.

- **YAGNI.** No machinery without a present need; a flag beats a framework.
- **Refusal is first-class.** What the oracle cannot stand behind is absent, and the
  absence is accounted for — never papered over
  ([cert-obligations#the-ten-obligations]).
- **No natural language.** Every artifact is machine data: keyed numbers, enum codes,
  numeric witnesses, hashes.

Three further principles are boundaries rather than preferences, so each is stated
where it is enforced rather than repeated here: *evidence, never verdicts* and *score,
not solve* have their own statements on this page, and *agnostic by purity* is
[architectural-principles#numerics-agnostic].

## Score, not solve

**The caller supplies complete candidate states; the oracle never fills in missing
pieces.** This is the oracle-operator boundary, and it is the reason the two halves
can be reasoned about separately. The complementary half — that the missing pieces are
exactly what the operator supplies — is [purpose-and-scope#what-n-op-is], where the
description of the operator's job is an open question. Nothing on this page depends on
how that question resolves.

## A compiler and its oracle-files

The product has two parts, matching the two phases of the architecture
([compose-time-pipeline#boundary]):

- **The compiler** — a command-line program. Run once per crystal identity: identity
  in, **one self-describing artifact file out** (an "oracle-file"). Compose time is
  seconds to minutes, and it is where all symbolic work, pruning, structure
  exploitation and derivative synthesis are spent.
- **The oracle-file** — the emitted kernel, persisted. Loaded by any program and
  called like a function, microseconds to milliseconds per call, millions of times.
  This file is the thing consumers actually hold.

## What an oracle-file contains

One file on disk, four things inside.

1. **The callable** — `Validate`, with its gradient entry point baked in at compile
   time ([pino-bridge#validate]). Consumers that never need gradients simply never
   invoke that entry point.
2. **The static slot schema** — the complete table of every check the kernel contains.
3. **Its identity** — the content hash of the compiled kernel
   ([representation-substrate#identity-exact]), the identity descriptors it was
   compiled from, and the registry and specification versions it was compiled against.
   **File hash equals kernel hash**, so attribution, caching, and "which oracle
   produced this result?" are filesystem-level facts.
4. **Its certificate reference** — a hash-pinned pointer to the certification evidence
   for this kernel ([cert-obligations#certificate-artifact]), so trust travels with
   the file.

## Three rules about files

- **One file per crystal identity.** A kernel is specialised to one periodicity
  structure, site decoration and environment ([crystal-inputs#top-level-inputs]). "The
  oracle" as a general object is the *compiler*; each file is the oracle *for one
  instance*. Searches over discrete identity space produce many files — cheap under
  content-addressed caching, but the mental model is "a directory of kernels", never
  "one universal file".
- **Environment-box validity.** The compile-time environment fixes the *envelope* —
  which checks exist — and stamps the file with its validity box
  ([applicability-classifiers#swept-environment-windows]); the runtime environment
  argument varies *within* that box. Outside the box: recompile. The stamp makes
  out-of-box use mechanically detectable.
- **Oracle-files are immutable.** New pinned targets, a new registry version, or a new
  identity each produce a **new file** with a new hash. Nothing is edited in place, so
  every result stays permanently attributable.

## State, per call

The full state object as [unified-state#slots] defines it: geometry, sites and
momenta, species, the electronic degrees of freedom, fields. This is deliberately a
**superset** of any standard interchange format — the missing pieces are precisely
what the operator learns to supply. The state type is the product's own; no external
standard exists for it and none should.

*Structural* well-formedness — shapes, finite values — is the caller's obligation.
*Physical* admissibility is scored, never presupposed
([residual-definitions#categories]).

## Environment, per call

The operating-condition record, varying within the file's stamped box. The record type
itself is [crystal-inputs#environment]; what this page fixes is that it is a per-call
argument and that its excursions are bounded by the compile-time stamp.

## The call

One entry point, whose signature is [pino-bridge#validate]. It returns four things:
the raw residual map keyed by slot, the values map holding requested derived
quantities, an optional cotangent map populated only when gradients were requested,
and the content hash of the producing kernel.

Slot keys are structured values and residual values are **raw**: the oracle never
normalises, weights, sums, or judges across slots
([residual-definitions#granularity]).

## The static slot schema

Everything that does not vary per call. For each key: the producing registry row, the
axis coordinates, the closed-enum tags used for subset selection and grouping, and the
error scale — a standard deviation ([residual-definitions#error-budget]).

This makes an oracle-file self-describing: a consumer can enumerate its contents with
no other resource. It also fixes a boundary. Consumers who want cross-slot
comparability compute the standardised score `z = value / σ` **themselves** — that is
a join against the schema, not a product output.

## Refusal is absence

A check the oracle cannot stand behind for this instance — inapplicable, outside the
certified envelope, or refused by certification — is not in the compiled kernel, so
its key is simply not in any map. The *reason* is machine data in the certification
record: a closed-enum refusal mode plus numeric witnesses
([cert-obligations#certificate-artifact]). No prose, anywhere.

## Selection

Two flag layers, both already in the architecture — no new machinery.

- **Compose-time scoping.** The compile request names the observable bundles and
  residual categories wanted ([compose-time-pipeline#boundary],
  [canonical-vocabularies]); everything unrequested or inapplicable is pruned and
  never becomes code.
- **Call-time subsetting.** The call's request parameter evaluates the full kernel, a
  set of slot keys, or a set of named quantities ([pino-bridge#validate]).

## Import is a compiler input

`Import` pins an external value into the graph as a first-class check, coverage-masked
to exactly the axis points the datum constrains ([pino-bridge#import]). One object,
two readings: pin a **measurement** and the slots read "disagrees with reality by this
much"; pin an **aspiration** and the identical slots read "misses the specification by
this much". The oracle cannot tell the difference and does not need to.

Because pinning inserts graph nodes at compose time, `Import` is a **compiler input**
— a targets file handed to the compiler, not a runtime argument. New pins produce a
new oracle-file. That is a feature: every reconciliation or design result is
attributable to a specific, hash-named artifact.

## The two loops

**Training** proposes states and sinks the oracle's gradients into the *operator's
weights*. **Design** proposes candidates and sinks the same gradients into the
*candidate itself*. One oracle, one call surface, two gradient sinks. Both loops live
in the interface library, never in the product ([purpose-and-scope#no-loops]).

## The design-variable boundary

Within one oracle-file the **continuous** variables — cell, positions, and composition
fraction where the registry treats it as an axis — are directly optimisable through
the baked gradients. The **discrete** variables — species, decoration, symmetry family
— are the compiler's specialisation axis: searching them means enumerate-and-compile
(many files, cached by content) or an external search over that discrete space.

Static, instantaneous-property design works on today's contract. **Lifetime design** —
"properties after N hours at these conditions" — additionally requires a
time-evolution capability that this specification does not claim.

## The command line

Three verbs, minimal by principle.

- `compile` — identity, plus environment, plus channel flags, plus an optional targets
  file, produces one oracle-file.
- `inspect` — oracle-file produces its static schema and identity, enumerated.
- `validate` — oracle-file plus a state file, plus environment and request flags,
  produces the keyed-float maps, serialised.

In-program loading of the oracle-file is the **primary** consumption path; the command
line is the same function with file handles. Nothing interactive, nothing stateful, no
daemon. Which library the command line ships inside is
[library-landscape#cli-placement].

The accuracy each headline output must meet is [accuracy-ledger#design-grade]; this
page fixes the shape of the answer, not its tolerance.
