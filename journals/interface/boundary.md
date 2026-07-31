---
id: boundary
title: "What the loops library owns"
owns:
  - driver responsibilities
  - gradient sink selection
anchors:
  what-it-is: "What the loops library is"
  ownership: "What it owns"
  stub: "What is not designed"
depends-on:
  - library-landscape
  - purpose-and-scope
  - learnable-structure-contract
  - training-stages
  - residual-loss-design
  - pino-bridge
open-questions:
  - id: loops-library-undesigned
    anchor: stub
    summary: "The loops library has a charter and no design: no driver interface, no schedule representation, no active-learning policy type, and no statement of what a driver persists between runs."
---
# What the loops library owns

This page is a **declared stub**. The charter below is settled; nothing beneath it is
designed. It exists so that the obligations the other two libraries push outward have a
named recipient instead of an implied one.

## What the loops library is

[library-landscape#interface] states the remit. This page states what falls under it.

The unit is a **driver**: the thing that runs. The other two libraries are built to be
driven, and each says so from its own side. The oracle scores what it is handed and
consumes nothing ([purpose-and-scope#no-loops]). The operator emits, and accepts
cotangents, as plain calls, and owns no loop
([learnable-structure-contract#loop-drivability]). Both expose signals — granular
residuals, gradients, certification evidence — for a policy that neither of them runs.
That policy is a driver, and drivers live here.

A command line is not a driver, which is why the oracle's own ships with the oracle
([library-landscape#cli-placement]).

## What it owns

- **Interleaving.** Calling emission, calling the oracle's validation entry
  ([pino-bridge#validate]), and deciding the order and rate of both.
- **Batching policy.** Which samples, in what batches, in what order.
- **Schedules.** Walking the stage ordering ([training-stages#stage-ordering]),
  advancing the curricula, and carrying the weights the loss policy declares
  ([residual-loss-design#defaults]).
- **Active learning.** Residual-adaptive sampling beyond a formula's declared policy,
  query by committee, importance reweighting against running loss statistics. This
  lives here and in neither of the other two.
- **The gradient sink.** Training pushes the oracle's cotangents into weights; design
  search pushes them into the candidate. The seam does not distinguish the two
  ([learnable-structure-contract#loop-agnostic]), so the choice is the driver's.

Nothing in this list is visible through the seam. That is the point of the seam.

## What is not designed

There is no driver interface, no representation for a schedule, no type for an
active-learning policy, and no statement of what a driver persists between runs. The
charter above constrains those decisions; it does not make them.
