# n-Op

A **physically-informed neural operator (PINO)** that predicts how the
multiphysics state of a crystalline material evolves in time, in service of
designing **durable ultra-wide-bandgap (UWBG) semiconductor chips for harsh
environments** (jet-turbine-class: high temperature, thermal cycling, high
field, high current density).

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

## Where to start

| Document | What it is |
|---|---|
| [`docs/architecture.md`](docs/architecture.md) | The conceptual specification and the **single source of truth for vocabularies and counts**. Start here. |
| [`docs/implementation-plan.md`](docs/implementation-plan.md) | Typed signatures, the target observables as compositions, the residual/cert machinery, and the phased build sequence. |
| [`docs/formula-registry.md`](docs/formula-registry.md) | Narrative index over the closed formula registry. |
| [`docs/properties.md`](docs/properties.md) | The nine categories of material property the operator targets. |
| `physics/library/formulas/registry-manifest.csv` | The canonical, machine-readable formula list (102 entries + 2 markers). |
| `physics/research/` | The mathematical grounding: per-regime derivations (`group-A/B/C`) and the UWBG domain catalogs. |
| `informed-operator/design/residual-loss-methodology.md` | The PINO multi-source training methodology. |

## Directory map

```
n-Op/
├── README.md
├── docs/                          the canonical specification set
│   ├── architecture.md
│   ├── implementation-plan.md
│   ├── formula-registry.md
│   └── properties.md
├── physics/
│   ├── library/                   the implementation scaffold (empty; awaiting language decision)
│   │   ├── formulas/registry-manifest.csv
│   │   └── cert/reference-data/    machine-readable cert reference battery
│   └── research/                   mathematical grounding + UWBG domain catalogs
├── informed-operator/
│   └── design/                     PINO residual-loss methodology
└── interface/                      placeholder
```

## The one open decision

The **implementation language is not yet chosen**, and it blocks the first
implementation phase. The hot numeric path, the autodiff requirement for
adjoint-bearing (D2) residuals, the compile-time staging of `γ̂` code, and the
crystallographic/topology tool ecosystem all bear on the choice. Everything in
`docs/` is written language-neutrally so the architecture is independent of this
decision. See `docs/architecture.md §17` for the full list of open decisions.

No code has been written yet. `physics/library/` is an empty scaffold whose
directory names match the architecture.
