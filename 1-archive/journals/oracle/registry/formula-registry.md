---
id: formula-registry
title: "The registry manifest"
owns:
  - manifest field schema
  - research-stream provenance vocabulary
  - column-vocabulary harvest rule
  - registry count discipline
anchors:
  manifest: "What the manifest is"
  fields: "The fields"
  provenance: "The provenance vocabulary"
  harvest: "Where a field's vocabulary lives"
  counts: "Counts belong to the table"
depends-on:
  - named-formulas
  - observable-bundles
  - topology-atlas
  - applicability-classifiers
  - agent-contract
  - traps
open-questions:
  - id: research-stream-documents-absent
    anchor: provenance
    summary: "Four of the five research streams the provenance vocabulary names have no page in this corpus, so a provenance value on rows 1–87 identifies a stream but cannot be followed to the document that grounds the row."
---
# The registry manifest

## What the manifest is

The manifest is the machine-readable table of named formulas: one row per
formula, at [registry]. It is canonical for every per-row
value. [named-formulas] states what a row *means* — the record, the tag
vocabularies, the registration rules — and this page states what the table
*looks like*.

The row number is a **stable identifier**. It orders nothing and is never reused;
contiguous bands of it were added as packages, and [named-formulas#row-bands]
maps the bands to their physics.

## The fields

One column per field of the formula record ([named-formulas#formula-record]):

| Field | Holds |
|---|---|
| row number | stable identifier |
| `name` | behavior-named identifier; a person's name appears only in `provenance` |
| `signature` | typed inputs to output, with units |
| `bundle` | one or more observable bundles, or `linear-response-primitive` |
| `cost-tier` | what one evaluation costs |
| `differentiability` | how a consumer obtains a gradient through the row |
| `anchor-class` | what the row's value is trusted against |
| `provenance` | where the row came from, and what it is called in the literature |
| `depends-on` | upstream formulas and primitives |

## The provenance vocabulary

Every row carries a provenance value. Seven are admissible:

| Value | The row came from |
|---|---|
| `observable-catalog` | the observable catalog |
| `crystal-structure-prediction` | structure prediction and heterostructure work |
| `defects-and-interfaces` | defects, surfaces and interfaces |
| `non-equilibrium-high-field` | non-equilibrium and high-field transport |
| `residual-loss-methodology` | the residual and loss methodology |
| `extension` | completing a vocabulary the streams left partial, rather than mined from a stream |
| `topology-atlas` | derived from the topology atlas ([topology-atlas]) |

The first five are **research streams** — the bodies of work the base catalog
was mined from. A row grounded in more than one is written as a sum, for example
`observable-catalog + defects-and-interfaces`.

A value may carry a parenthetical, and it carries exactly three kinds of thing:
the literature attribution the row is known by (`a.k.a. …`, which is where a
literature search starts and is why a person's name never enters the row's own
name); the declared smooth relaxation, for a `relaxed` row, which the
registration gate requires; and a gating or conditioning note explaining why the
row's differentiability value is what it is.

This is a closed vocabulary, so the provenance field is checkable in the same way
the other coded fields are. It has to be: it is the field that decides whether a
row is defensible, and an unchecked provenance field is how a row with no source
looks exactly like a row with one.

## Where a field's vocabulary lives

Each coded field draws on a closed vocabulary, and **each vocabulary is defined
on exactly one page**:

| Field | Vocabulary defined by |
|---|---|
| `bundle` | [observable-bundles#the-eleven] |
| `cost-tier` | [named-formulas#cost-tiers] |
| `differentiability` | [named-formulas#diff-tags] |
| `anchor-class` | [named-formulas#anchor-class] |
| `provenance` | this page |
| `applicability` | [applicability-classifiers#the-predicate-contract] |

**Every consumer harvests the vocabulary from its defining page. No consumer
restates it.** This binds tools as hard as it binds pages: a checker that
hard-codes the admissible values validates the column against its own copy, and
goes on reporting clean after the definition changes underneath it. A harvest
that fails to find its source must be a loud failure, not a silent empty set —
an empty vocabulary accepts everything ([traps#vocabulary-has-an-owner]).

The same rule is what stops a second legend from appearing. A vocabulary written
out twice has no mechanism holding the copies together, and the copies diverge in
the direction of whoever edited last ([agent-contract#placement]).

## Counts belong to the table

**The manifest is canonical for every count over it**: how many rows carry a
given bundle, cost, differentiability value or anchor class; how many rows there
are at all. No page restates one.

A page states rules and names individual rows where a rule needs an example. A
tally written into a sentence beside the table it counts is a second copy of the
table's contents in a form nothing can check, and it goes stale on the next row
added — which is a normal, expected event, not an exceptional one.
