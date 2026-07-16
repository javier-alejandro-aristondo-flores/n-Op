# n-Op

n-Op trains a **physically-informed neural operator (PINO)** that predicts how
the multiphysics state of a crystalline material evolves in time, in service of
designing **durable ultra-wide-bandgap (UWBG) semiconductor chips for harsh
environments** (jet-turbine-class: high temperature (>500 °C), thermal cycling,
mechanical vibration, high field, high current density, possibly radiation).

The minimum viable demonstration is **diamond**, with three capabilities:
crystal-structure prediction, electron-cloud diffusion, and heat diffusion. The
spec is comprehensive; the build is diamond-first.

## The three libraries

`n-Op` is partitioned into three sibling libraries:

- **`physics/`** — a substrate-agnostic reference oracle. It encodes the laws:
  state structure, GENERIC dynamics, observable definitions, residual
  definitions, and certification obligations. It does **not** hold time-varying
  state values, train networks, integrate trajectories, or wrap external DFT
  codes at runtime. This is the current focus.
- **`informed-operator/`** — the PINO itself; consumes `physics/` and learns the
  time-evolution operator.
- **`interface/`** — the user-facing surface (not yet designed).

## Architectural framing

`/physics` is structured around two load-bearing concepts:

- **The `PhysicsGraph`** (`docs/architecture/06-physics-graph.md`) — the
  canonical compose-time data structure. Three node kinds (`Input`,
  `FormulaApply`, `MethodInvoke`); typed dataflow edges; per-stage sidecars.
  Every observable, every residual, every certificate is a node.
- **The 4+1 stage compose-time pipeline** (`docs/architecture/07-pipeline.md`)
  — symbolic lift → symmetry quotient → invariant synthesis (Stage 2.5) →
  algebraic simplification → lowering + adjoint synthesis → runtime kernel. The earlier cheap/faithful split is
  retired; every kernel emerging from Stage 4 is fast by construction
  ("always-cheap" discipline).

## Where to start

The spec lives in an atomic-file tree under `docs/`. The three legacy
monoliths are regenerated from the tree by `docs/meta/assemble.py`.

| Path | What it is |
|---|---|
| `docs/architecture/` | The conceptual specification, one concept per file. Start at `01-purpose.md` and `06-physics-graph.md`. **Single source of truth for vocabularies and category/bundle counts** (the formula count is owned by the registry CSV below). |
| `docs/mvp/` | The diamond MVP projected onto the spec: γ̂ budget, three capabilities, decisions forced, build order. Start here for the build. |
| `docs/implementation/` | Typed signatures, observable compositions, residual/cert machinery, phased build sequence. |
| `docs/meta/conventions.md` | Atomic-file rules (frontmatter, anchors, lint discipline). |
| `docs/meta/glossary.md` | One-line definitions for the load-bearing terms. |
| `docs/meta/manifest.yaml` | Assembly order + named LLM-context bundles. |
| `docs/formula-registry.md` | Narrative index over the closed formula registry. |
| `docs/properties.md` | The nine property categories with bundle/formula-row mapping. |
| `physics/library/formulas/registry-manifest.csv` | The canonical, machine-readable formula list (132 entries + 2 markers). |
| `physics/research/` | Mathematical grounding: per-regime derivations and UWBG catalogs. |
| `informed-operator/design/residual-loss-methodology.md` | PINO multi-source training methodology. |

The regenerated monoliths (`docs/architecture.md`,
`docs/implementation-plan.md`, `docs/mvp-slice.md`) are convenience reads only;
edits go to the atomic files.

## Directory map

```
n-Op/
├── README.md
├── docs/
│   ├── architecture/              atomic spec files (21 sections)
│   ├── implementation/            atomic build-plan files (11 sections)
│   ├── mvp/                       atomic diamond-MVP files (6 sections)
│   ├── meta/                      manifest.yaml, conventions.md, glossary.md,
│   │                              assemble.py, lint.py, AUDIT_PROMPT.md
│   ├── audits/                    frozen audit records (never edited)
│   ├── specs/                     wave / pass design specs
│   ├── presentation/              decks (dated snapshots) + build tooling
│   ├── architecture.md            regenerated monolith
│   ├── implementation-plan.md     regenerated monolith
│   ├── mvp-slice.md               regenerated monolith
│   ├── formula-registry.md
│   └── properties.md
├── physics/
│   ├── library/                   code scaffold (no code yet) + the registry CSV and cert battery
│   │   ├── formulas/registry-manifest.csv
│   │   └── cert/reference-data/    machine-readable cert reference battery
│   └── research/                   mathematical grounding + UWBG domain catalogs
├── informed-operator/
│   └── design/                     PINO residual-loss methodology
└── interface/                      placeholder
```

## Open decisions

The **implementation language is decided** (arch-18, closed 2026-06): a
polyglot of domain-specific DSLs joined at the Stage-4→Stage-5 codegen seam —
**Haskell** hosts the Stage-1–4 symbolic compiler and the `arch-20` substrate,
**Julia** is the Stage-5 runtime (Stage 4 emits Julia source), with **GAP**
(offline group theory) and **Lean 4** (offline proofs) as sidecars. Everything
in `docs/` remains language-neutral. Five decisions remain open — surrogate-net
build vs adopt, the PDE-mesh adjoint scheme, the γ̂ §15.4 questions, the
Layer-1.75 V2 spec, and the integrator interface — see
`docs/architecture/18-open-decisions.md`.

No code has been written yet. `physics/library/` is a code-free scaffold whose
directory names match the architecture; its two populated corners are the
canonical formula registry (`formulas/registry-manifest.csv`) and the cert
reference battery (`cert/reference-data/`).
