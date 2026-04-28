# compose-physics

Compose closed-form physics problems into compiled C kernels.

`compose-physics` is a Common Lisp tool that takes a closed-form description
of a physical system — a set of residual expressions and a set of per-slot
update expressions — and emits a self-contained, compiled shared library
exposing two entry points: `compute_residual` and `compute_update`. It is
purpose-built to provide the residual term and state-update rule consumed
during the training of physics-informed neural operators (PINOs).

The Lisp side performs no numerical evaluation. It is an algebra and code
generator. All numerics live in the emitted C.

## What it produces

For every registered problem, `compose-physics` writes a content-addressed
directory containing:

- `manifest.sexp` — problem metadata, slot list, file inventory, toolchain
- `problem.sexp`, `residual.sexp`, `update.sexp` — canonical IR snapshots
- `residual_chunk_*.c`, `update_chunk_*.c` — chunked C kernels, one row
  per residual / one row per update slot, individually addressable
- `dispatch.c` — fans calls out to the chunked kernels
- `Makefile`, `lib<name>.so` — the built shared library
- A copy of (or reference to) the original `.lisp` source

Two callable entry points are exposed by the `.so`:

- `compute_residual(state, out)` — fills `out[k]` for each residual row
- `compute_update(state, out)` — fills `out[i]` for each slot update

A neural operator can address residual rows individually for per-row
weighting, take gradients through them, or use them as a validity measure.
The numerical form is the state-update rule used to roll the system
forward by one step.

## Design intent

- **No symbolics, ever.** The IR is a funcallable tree of primitives.
  Every node in the tree is directly evaluable from Lisp at any time.
  There is no symbolic algebra system, no rewriting backend that produces
  un-evaluable nodes.
- **One tree, two views.** The same expression tree is both manipulated
  (chunked, hashed, serialized) and evaluated. Manipulation and evaluation
  do not live on separate structures.
- **Residual single-state.** A residual reads exactly one state and
  reports a vector of row values; zero means satisfied.
- **Per-slot update.** Updates are written one slot at a time and default
  to identity for slots the user does not touch.
- **No problem composition.** Each problem stands alone. Composition is
  an outside-the-tool concern.
- **Closed problem set.** No user-extensible vocabulary, no plug-in
  primitives, no compiled foreign callables embedded in the tree.
- **No notebook-driven workflow.** The notebook in `notebooks/` is a
  validation harness, not the intended interface. The intended interface
  is the CLI.

## Repository layout

```
compose-physics/
├── algebra/                 closed-form IR, vocabulary, solver
│   ├── expression-trees.lisp
│   ├── problem.lisp
│   ├── vocabulary/
│   └── solve/
├── emission/                tree → chunked C kernels + dispatch + Makefile
├── persistence/             canonical sexp, content-hashing, registry writer
│   ├── sexp/
│   └── registry/
├── compose_physics/         Python CLI (argparse + rich)
│   └── cli/
├── notebooks/               three-mass / four-spring validation harness
├── compose-physics.asd
└── packages.lisp
```

## Requirements

- SBCL (tested on 2.6.x) with ASDF
- A C compiler in `PATH` (default: `cc`)
- `make`
- Python ≥ 3.13 with `rich` for the CLI

## Usage

Author a problem in Lisp (see `notebooks/three-mass-four-spring.lisp` for a
reference) and register it:

```sh
python -m compose_physics register path/to/problem.lisp \
    --registry-root /path/to/registry \
    --source-dest copy
```

This loads the problem in SBCL, canonicalizes and content-hashes it,
writes the registry directory, and runs `make` to produce
`lib<problem-name>.so`.

The manifest, the canonical sexp snapshots, and the `.so` are everything
a downstream consumer (a training loop, a simulation harness, a notebook)
needs. The interface to the emitted code is the consumer's choice;
`compose-physics` exposes only two C entry points and lets the caller
wrap them.

## Notes on the toolchain

The default C flags include `-ffast-math`. This is appropriate for
production but breaks bit-identity comparisons against the Lisp-side
funcall path because of FP reassociation. For any test that requires
Lisp-vs-C bit identity, register the problem with
`-O2 -fPIC -fno-fast-math -fno-associative-math`.

## Status

The project is the result of a total rewrite. It lives under
[`n-Op`](../) as a sibling to the neural-operator training code, and is
managed via `_darcs` from inside `compose-physics/`; only the outer
`n-Op` repo is tracked in git.
