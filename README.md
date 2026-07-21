# n-Op

n-Op trains a **physically-informed neural operator (PINO)** that predicts how
the multiphysics state of a crystalline material evolves in time, in service of
designing **durable ultra-wide-bandgap (UWBG) semiconductor chips for harsh
environments** (jet-turbine-class: >500 °C, thermal cycling, mechanical
vibration, high field, high current density, possibly radiation).

The minimum viable demonstration is **diamond**, with three capabilities:
crystal-structure prediction, electron-cloud diffusion, and heat diffusion. The
spec is comprehensive; the build is diamond-first.

**No code has been written yet.** This repository is specification and research.

## Start here

The specification is a **book**. Do not go spelunking through directories — the
apparatus exists so you do not have to.

| | |
|---|---|
| **[instructions.md](instructions.md)** | **Read this first.** How to go from the book to a working understanding, and how to get an edit back into the right page. |
| [contents.md](contents.md) | Chapters → pages, in reading order. *Generated.* |
| [index.md](index.md) | Every canonical topic → the single page that owns it. *Generated.* |
| [glossary.md](glossary.md) | One-line definitions for the load-bearing terms. |

Chapters are **by concern**, and chapters **2–6 are the contiguous `/physics`
oracle block** — for oracle-internal work that range is usually sufficient.

Pages are addressed by their `id` (`arch-07-pipeline`, `accuracy-ledger`), never
by filename or by the display tag. That is why the corpus could be restructured
wholesale without breaking a cross-reference.

## The three libraries

- **`physics/`** — the reference oracle. It encodes the laws: state structure,
  GENERIC dynamics, observable definitions, residual definitions, and
  certification obligations. It does **not** hold time-varying state values,
  train networks, integrate trajectories, or wrap external DFT codes at runtime.
  This is the current focus.
  *Numerics-agnostic at its seam* (flat arrays, no framework tensors) while
  internally committed to the representation substrate of `[arch-20-representations]`.
- **`informed-operator/`** — the PINO itself; consumes `physics/` and learns the
  time-evolution operator.
- **`interface/`** — where every driving loop lives (training, design search,
  active learning). Not yet designed.

## Architectural framing

`/physics` is a compiler that emits a numerical kernel, structured around two
load-bearing concepts:

- **The `PhysicsGraph`** (`[arch-06-physics-graph]`) — the canonical compose-time
  data structure. Three node kinds, typed dataflow edges, per-stage sidecars.
  Every observable, every residual, every certificate is a node.
- **The 4+1 stage compose-time pipeline** (`[arch-07-pipeline]`) — symbolic lift
  → symmetry quotient → invariant synthesis → algebraic simplification →
  lowering + adjoint synthesis → runtime kernel. Stages 1–4 run once per crystal
  identity; Stage 5 runs millions of times.

## Layout

```
n-Op/
├── contents.md · index.md · glossary.md · instructions.md   the apparatus
├── pages/                    the book — 47 canon pages
│   └── appendix/             derivations (authority: supporting)
├── tools/
│   ├── apparatus.py          regenerate the apparatus + check invariants
│   ├── build_book.py         the migration that produced pages/
│   └── lint.py · seams.py    older checkers, pending retarget
├── physics/
│   └── library/              code scaffold (no code yet)
│       ├── formulas/registry-manifest.csv    the canonical formula registry
│       └── cert/reference-data/              machine-readable cert battery
├── docs/                     live work products only (audits/specs still executing)
├── informed-operator/design/ PINO seam contract + loss methodology
└── interface/                placeholder
```

Run `python tools/apparatus.py` after editing any page: it restamps content
hashes and regenerates `contents.md` / `index.md`. `--check` verifies without
writing, and is the gate — it fails on a duplicate `canonical-for` topic, an
asymmetric dependency edge, an unresolvable `[id]` reference, or a stale hash.

## Open decisions

Tracked in `[arch-18-open-decisions]`. The load-bearing ones:

- **Implementation language — open.** A polyglot proposal (a typed functional
  compiler host with its own AD, a separate numeric runtime, offline computer
  algebra and proof assistants) is one candidate configuration under evaluation,
  not a commitment. Everything in the book stays language-neutral.
- Surrogate-net build vs adopt; the PDE-mesh adjoint scheme; the γ̂ open
  questions; the Layer-1.75 spec.
- The **differentiability tag scheme is being redesigned** — three incompatible
  definitions are currently in force and eleven smooth registry rows are
  mis-tagged in a way that would ship them without adjoints.

The integrator interface closed 2026-07-16: a per-tier tangent kernel plus a
steppable-form manifest, with the integrator staying consumer-side.

## Before changing anything physical

Read `[traps]` — the standing traps register. Sign, unit, and reference-frame
errors in this corpus have historically survived ordinary review and inverted
real physics.
