---
id: library-landscape
title: "Library boundaries"
owns:
  - library boundary rules
  - oracle runtime exclusions
  - command-line placement
  - engineering scope placement
  - operator library remit
  - interface library remit
anchors:
  partition: "What this page is for"
  oracle-exclusions: "What may not enter the oracle library"
  operator: "The operator library"
  interface: "The interface library"
  cli-placement: "The command line ships inside the oracle library"
  engineering: "Engineering aspects are oracle-library work"
depends-on:
  - agent-contract
  - purpose-and-scope
  - architectural-principles
  - product
  - unified-state
  - representation-substrate
  - boundary
open-questions: []
---
# Library boundaries

## What this page is for

The three-library partition is the top level of this base's own tree
([agent-contract#shape]), so the partition needs no page to announce it. What a
directory layout cannot carry is the part that matters when a fact has to be filed:
**what may not cross between the libraries.** That is this page.

Without it, a reader who sees three sibling directories has no statement of the
boundaries, and the command-line question in particular gets re-argued every time —
because a directory named for the interface reads like the natural home for a command
line, and it is not.

## What may not enter the oracle library

- **No state values.** The oracle library defines the state type and holds no instance
  of it ([unified-state#type-not-value]).
- **No training, no integration.** It trains no neural network and integrates no
  trajectory. Every loop that would do either lives in the interface library
  ([purpose-and-scope#no-loops]).
- **No external simulation software at runtime.** External data enters only as values
  pinned at compile time ([product#import-is-a-compiler-input]). There is no path by
  which a compiled kernel shells out to a solver.

The oracle library is numerics-agnostic *at its seam* while internally committed to
the representation substrate ([representation-substrate#contract]); the principle that
states this once is [architectural-principles#numerics-agnostic].

## The operator library

The operator library is the neural operator itself. It **consumes** the oracle library
and is trained against it; the dependency never runs the other way. What it is trained
to produce is [purpose-and-scope#what-n-op-is], where the framing is an open question
— this page fixes only the direction of the dependency.

Its seam contract and its loss methodology are the operator library's own pages, not
this one's.

## The interface library

The interface library owns **every driving loop**: training, design search, active
learning. It is not yet designed. [boundary#ownership] states what belongs to it.

## The command line ships inside the oracle library

The oracle's own command line — the three verbs of [product#cli] — ships **inside the
oracle library**. The interface library is the loops, not the command line.

## Engineering aspects are oracle-library work

Defects, dopants, surfaces, interfaces and operating-condition effects live **inside**
the oracle library, not in a library of their own. There is no fourth library.
