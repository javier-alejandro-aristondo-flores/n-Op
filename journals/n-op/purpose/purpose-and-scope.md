---
id: purpose-and-scope
title: "Purpose and scope"
owns:
  - program purpose
  - downstream device target
  - property-targeted crystal design goal
  - oracle library remit
  - oracle loop exclusion
  - verifying is cheaper than solving
  - computational hardness argument
  - valuation oracle versus decision oracle
  - minimum viable demonstration
  - MVP discipline
  - material scope
  - comprehensive spec diamond-first build
anchors:
  what-n-op-is: "What n-Op is"
  downstream-target: "The downstream target"
  oracle-remit: "What the oracle library does"
  no-loops: "What the oracle library is not"
  why-a-grader: "Verifying is cheaper than solving"
  hardness: "The hardness results the design rests on"
  valuation-oracle: "A valuation oracle, not a decision oracle"
  mvp: "The minimum viable demonstration"
  mvp-discipline: "The MVP discipline"
  material-scope: "Material scope"
  spec-and-build: "Comprehensive spec, diamond-first build"
depends-on:
  - product
  - architectural-principles
  - build-sequence
  - library-landscape
  - capability-slices
  - mvp-system
  - unified-state
  - generic-dynamics
  - residual-definitions
  - canonical-vocabularies
  - named-formulas
  - training-stages
  - pino-bridge
  - boundary
open-questions:
  - id: operator-capability-framing
    anchor: what-n-op-is
    summary: "What the operator is trained to produce is stated two incompatible ways in the material this base is built from — predicting the time evolution of the state, versus returning the state channels the caller did not supply given a crystal identity and the properties already known. The oracle side is unaffected; the operator side cannot be described until this is settled."
---
# Purpose and scope

## What n-Op is

n-Op pairs a **compiled oracle for crystalline matter** with a **neural operator
trained against it**. The oracle is handed a candidate state of a crystal under stated
operating conditions and returns a granular, itemized account of how far that
candidate is from satisfying each law it is supposed to satisfy — many independent
named checks, each a number, each traceable to a published formula. The operator is
the fast learner that produces the candidate states.

**The oracle side of that division is settled and is stated crisply.** The oracle
receives a *complete* candidate state together with the crystal identity its kernel
was compiled for, and grades it. It never fills in a missing piece, owns no loop, and
proposes nothing ([product#score-not-solve]). The operator is the half that supplies
what the caller does not have; the state type is deliberately a superset of any
interchange format, and the pieces no database carries are the operator's to produce
([product#state-input]).

**The operator side is not settled, and this page does not settle it.** Two readings
are present in the material this base is built from, and they are different claims:

- the operator **predicts the time evolution** of the state of a crystalline material
  under operating conditions; or
- the operator **completes** a state — given a crystal identity and the properties
  already known, it returns the channels that were not supplied.

The open question on this page carries the choice. Three things hold under either
reading and can be relied on now: n-Op claims **no time-evolution verb** today
([architectural-principles#numerics-agnostic]); the oracle grades whatever it is
handed and is indifferent to how the candidate was produced; and the MVP's capability
is fixed independently, as a selection from closed vocabularies rather than as a verb
([capability-slices#selection-discipline]). Two of the three MVP capabilities are
named for transport processes, so whether their output is a trajectory or a completed
channel set is the same open question, asked about a concrete slice.

## The downstream target

The downstream target is the design of **durable high-performance ultra-wide-bandgap
semiconductor chips for harsh environments** — chips that must function inside, for
instance, a jet turbine: temperatures above 500 °C, thermal cycling, mechanical
vibration, high field, high current density, possibly radiation.

Stated as a direction rather than a mechanism: **properties in, structures out.** You
state the properties you need, and the system searches for crystals that are
simultaneously physically real and fit for purpose — and can show its work for every
candidate it accepts or rejects. The mechanism that makes a measured datum and a
desired property the same object is [product#import-is-a-compiler-input]; the two
loops that consume it are [product#two-loops]. **No component that proposes candidates
is specified in this base.** The direction is a direction.

## What the oracle library does

The oracle library does not represent the *state values* of a system. It is the way to
**instantiate a physical system** — a crystal — and to define the laws that a
candidate is held to. It defines what a state is ([unified-state#slots]), what laws
govern it ([generic-dynamics#generic-form]), and how to evaluate whether a candidate
state satisfies those laws ([residual-definitions#categories]). Where the edges of
that library run — what may not enter it, and what the other two libraries own — is
[library-landscape].

## What the oracle library is not

The oracle library is a **pure oracle**. It owns no training control flow, no sample
selection beyond the per-generator sampling policy, and no loop that consumes loss
values to decide what to evaluate next.

Active-learning policies belong to the interface library, in neither the oracle nor
the operator; both the oracle and the operator expose the signals such a policy
consumes — granular residuals, gradients, certification evidence. [boundary#ownership]
states what the interface library owns.

## Verifying is cheaper than solving

Direct simulation of these materials at device-relevant conditions is prohibitively
expensive, and machine-learned surrogates are fast but untrustworthy precisely where
it matters — extrapolation into the harsh corners this program targets. The answer is
an old one from computer science: **checking a proposed solution is far cheaper than
producing one.**

n-Op does not build a faster solver. It builds a *grader* cheap enough and complete
enough that the learned half can be disciplined by it at every step
([product#score-not-solve], [pino-bridge#surface]). The grader never solves for
anything; its only job is to measure disagreement with the laws. That division of
labor is what makes the learned half safe to use: its known weakness — drift under
long rollouts, and extrapolation — is exactly the thing the grader exposes, cheaply,
at every step.

Three properties follow from the grammar being closed ([canonical-vocabularies]) and
are the reason a grader can be trusted at all:

- **Enumerable.** A compiled oracle can list every check it contains.
- **Traceable.** Every emitted number leads back to a numbered, literature-cited
  registry row ([named-formulas#the-registry]).
- **Decidable.** A request compiles or is rejected. Nothing fails ambiguously at
  runtime.

## The hardness results the design rests on

The section above states the trade informally. Its formal backing is two complexity
results, and they are the reason there is a grader in the architecture at all rather
than a better solver.

- **Finding the ground state is NP-hard.** Barahona (1982) established that finding
  the ground state of a three-dimensional Ising spin glass is NP-hard. NP is the class
  of problems whose solutions are *verifiable* in polynomial time; NP-hard means at
  least as hard as everything in it.
- **Quantum hardware does not rescue it.** Kitaev established that the k-local
  Hamiltonian problem is QMA-complete. Quantum Merlin–Arthur is the quantum analog
  of NP — a quantum verifier checking a quantum witness — so the hardness survives the
  change of machine rather than dissolving with it.

The consequence is the architecture. The search side is intractable and the check side
is not, so the system is built around the check: the oracle scores and never solves,
and score-not-solve is a principle rather than a preference
([product#score-not-solve]).

**One citation carries a qualification that must travel with it.** Baker–Gill–Solovay
(1975) exhibits oracles `A` and `B` with `P^A = NP^A` and `P^B ≠ NP^B`, so no proof
technique that *relativizes* — that survives handing both sides an oracle — can settle
P versus NP. It is cited here as a limit on the oracle **technique**, not as a claim
about this system. Detached from that qualification it reads as something far stronger
than was ever argued.

The loop this produces is not a search. Its honest analog is counterexample-guided
inductive synthesis, with a gradient in place of the counterexample. Where in training
the oracle attaches, and why it cannot come first, is
[training-stages#why-this-order].

## A valuation oracle, not a decision oracle

A textbook oracle returns one bit: yes or no. **This one returns a keyed vector of
real-valued residuals together with cotangents** — the gradient information for the
backward pass ([product#call-contract]).

The difference is load-bearing, and it is why the complexity framing above does not
make this a decision procedure. **One bit gives a learner no direction; a residual
with a gradient does.** A yes-or-no verifier could certify a candidate and still teach
nothing about how to produce a better one. The design needs the direction, so the
oracle is a valuation oracle — and the shape of what it returns follows from that
requirement rather than from convenience.

## The minimum viable demonstration

The minimum viable demonstration models **diamond**. Its three capability slices, and
the exact vocabulary each draws, are [capability-slices]. The physical system they are
built around — the cell, the anchors, and what each anchor forces — is [mvp-system].

## The MVP discipline

**As much closed-form and computationally feasible expression as possible**, and
**purpose-built tools**.

## Material scope

The MVP is diamond-centric. The broader material scope is anything that forms a
semiconductor with diamond: c-BN, AlN, GaN, β-Ga₂O₃, AlGaN; refractory contact metals
(W, Mo, Pt, Ti, Ni, Ta, TiN, WSi₂); substrates (SiC, Si, sapphire); gate dielectrics
(Al₂O₃, HfO₂, and AlN as a dielectric).

## Comprehensive spec, diamond-first build

**The comprehensiveness of the specification is the point**, even though
implementation is diamond-first. That distinction — comprehensive spec, diamond-first
build — runs through everything here. The in-versus-deferred boundary, formula by
formula, is [capability-slices#totals]; the phase-by-phase construction, and which
phases the diamond-first build reaches, is [build-sequence].
