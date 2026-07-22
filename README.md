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
| **[instructions.md](journal/instructions.md)** | **Read this first.** How to go from the book to a working understanding, and how to get an edit back into the right page. |
| [contents.md](journal/contents.md) | Chapters → pages, in reading order. *Generated.* |
| [index.md](journal/index.md) | Every canonical topic → the single page that owns it. *Generated.* |
| [glossary.md](journal/glossary.md) | One-line definitions for the load-bearing terms. |

Chapters are **by concern**, and chapters **2–6 are the contiguous `/physics`
oracle block** — for oracle-internal work that range is usually sufficient.

Pages are addressed by their `id` (`compose-time-pipeline`, `accuracy-ledger`), never
by filename or by the display tag. That is why the corpus could be restructured
wholesale without breaking a cross-reference.

## The three libraries

- **`physics/`** — the reference oracle. It encodes the laws: state structure,
  GENERIC dynamics, observable definitions, residual definitions, and
  certification obligations. It does **not** hold time-varying state values,
  train networks, integrate trajectories, or wrap external DFT codes at runtime.
  This is the current focus.
  *Numerics-agnostic at its seam* (flat arrays, no framework tensors) while
  internally committed to the representation substrate of `[representation-substrate]`.
- **`informed-operator/`** — the PINO itself; consumes `physics/` and learns the
  time-evolution operator.
- **`interface/`** — where every driving loop lives (training, design search,
  active learning). Not yet designed.

## Architectural framing

`/physics` is a compiler that emits a numerical kernel, structured around two
load-bearing concepts:

- **The `PhysicsGraph`** (`[physics-graph]`) — the canonical compose-time
  data structure. Three node kinds, typed dataflow edges, per-stage sidecars.
  Every observable, every residual, every certificate is a node.
- **The 4+1 stage compose-time pipeline** (`[compose-time-pipeline]`) — symbolic lift
  → symmetry quotient → invariant synthesis → algebraic simplification →
  lowering + adjoint synthesis → runtime kernel. Stages 1–4 run once per crystal
  identity; Stage 5 runs millions of times.

## Layout

```
n-Op/
├── journal/                  the specification, as a book
│   ├── contents.md · index.md · glossary.md · instructions.md    the apparatus
│   ├── pages/NN-chapter/     one folder per chapter; 58 pages, 49 canon
│   │   └── 11-appendix-derivations/   9 supporting derivations
│   ├── live/                 work products still executing
│   └── tools/                apparatus.py (regenerate + check) · seams.py (sweeps)
│                             · calibrate.py (plants defects; proves the other two look)
├── physics/
│   └── library/              code scaffold (no code yet)
│       ├── formulas/registry-manifest.csv    the canonical formula registry
│       └── cert/reference-data/              machine-readable cert battery
├── informed-operator/design/ PINO seam contract + loss methodology
└── interface/                placeholder
```

Run `python journal/tools/apparatus.py` after editing any page: it restamps content
hashes and regenerates `contents.md` / `index.md`. `--check` verifies without writing
and is the gate, alongside `python journal/tools/seams.py`. Between them they fail on
a duplicate `canonical-for` topic, an asymmetric or missing dependency edge, an
unresolvable `[id]`, a section coordinate or dated anchor that resolves to nothing, a
line-number citation, a registry count, per-tag tally or per-tier distribution that
disagrees with the CSV, a retired formula name left unresolved, a `D4` row with no
named relaxation, and a stale hash.

**Green is not evidence a check ran.** Both checkers have shipped holes that made them
skip whole classes of citation silently. Before citing a clean run, plant a defect of
the class you are claiming is absent and confirm the checker fails (`[traps]` §58).
`python journal/tools/calibrate.py` does exactly that — 50 probes into a temporary
copy — and additionally reports any check that *no* probe reaches, since a calibration
with holes in it is the same failure one level up.

## Open decisions

Tracked in `[open-decisions]`. The load-bearing ones:

- **Implementation language — open.** A polyglot proposal (a typed functional
  compiler host with its own AD, a separate numeric runtime, offline computer
  algebra and proof assistants) is one candidate configuration under evaluation,
  not a commitment. Everything in the book stays language-neutral.
- Surrogate-net build vs adopt; the PDE-mesh adjoint scheme; the Layer-1.75 spec.
  (The four γ̂ data-structure questions closed 2026-07-21 — identity stays exact
  and ε is estimated beside it; see `[gamma-hat]` §4.)
- **One** open verifier-soundness gap: no post-registration adjoint-drift
  monitoring — the registration gate validates the *formula's* adjoint, Stage 4
  synthesizes the *composition's* adjoint later over a rewritten graph, and
  nothing revalidates the second. Three others were named and closed on
  2026-07-21; all four stay listed in `[open-decisions]` with their
  resolutions, because an absent check reads exactly like a passing one and a
  silently closed one reads like it was never there.

The integrator interface closed 2026-07-16: a per-tier tangent kernel plus a
steppable-form manifest, with the integrator staying consumer-side.

## Before changing anything physical

Read `[traps]` — the standing traps register. Sign, unit, and reference-frame
errors in this corpus have historically survived ordinary review and inverted
real physics.
