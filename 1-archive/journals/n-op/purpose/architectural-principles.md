---
id: architectural-principles
title: "Architectural principles"
owns:
  - one compile pipeline over one substrate
  - minimum primitives
  - runtime symbolic exclusion
  - typed signatures principle
  - composition over duplication
  - loud at compose time absent at runtime
  - certification is first-class
  - numerics-agnostic seam
anchors:
  one-pipeline: "One compile pipeline over one substrate"
  minimum-primitives: "Minimum primitives"
  no-runtime-symbolics: "No symbolic computation on the runtime path"
  typed-everything: "Typed everything"
  composition-over-duplication: "Composition over duplication"
  loud-then-absent: "Loud at compose time, absent at runtime"
  cert-first-class: "Certification is first-class"
  numerics-agnostic: "Numerics-agnostic at the seam, committed within"
depends-on:
  - compose-time-pipeline
  - representation-substrate
  - canonical-vocabularies
  - product
  - cert-obligations
open-questions: []
---
# Architectural principles

Eight principles, carried throughout the build.

## One compile pipeline over one substrate

Structure is the compose-time pipeline ([compose-time-pipeline]) operating over the
content-addressed representation substrate
([representation-substrate#identity-exact]). One pipeline, one substrate — not a
pipeline per capability and not a substrate per stage.

## Minimum primitives

The computational method vocabulary, together with its registered sub-methods, is the
**closed primitive set** ([canonical-vocabularies]). Everything else is composition. A
new capability is a new arrangement of existing primitives or it is a change to the
vocabulary; there is no third option.

## No symbolic computation on the runtime path

Structured data appears only as compose-time input or as inert certificate output. The
compiled kernel is a closed, straight-line numeric function: no symbolic work, no
solver invocations, no branching on structure.

## Typed everything

Every method, template and formula has an explicit typed signature. No string-encoded
formulas. No implicit parameters.

## Composition over duplication

Properties are typed compositions of the small method vocabulary; observables that
share a shape share a template.

## Loud at compose time, absent at runtime

A degeneracy the oracle cannot stand behind is caught at compose time and refused with
a numeric witness. It is never *raised* from the compiled kernel — what the oracle
cannot certify is simply not in the kernel, so its key is absent from every map
([product#refusal-is-absence]). At runtime, failure surfaces as a failed certificate
leaf carrying its witness, never as an exception.

## Certification is first-class

Schema, freeze fixture, tamper tripwire and high-precision oracle together carry
roughly the weight of any one level of the system
([cert-obligations#certificate-artifact]). Certification is not a reporting layer
bolted on at the end.

## Numerics-agnostic at the seam, committed within

The emitted oracle assumes nothing about its caller: pure function, flat arrays at the
boundary, no loop ownership. This is *not* substrate-agnosticism in general —
internally the oracle library is committed to the substrate of
[representation-substrate#contract].

It emits state readouts and residuals. The integrator, the trainer and the operator
all live downstream, and **the time-evolution verbs are unclaimed**: nothing in this
base promises a trajectory.
