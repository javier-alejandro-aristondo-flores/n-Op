# The operator library — strain → HSE06(0.27) electronic structure for diamond

A surrogate for an expensive calculation. Diamond's band structure responds strongly and
nonlinearly to strain; computing it with the screened hybrid functional HSE06 costs roughly
42× what the cheap PBE functional costs at this system size. This library learns the map
from a strain state — and, in the primary mode, the cheap PBE eigenvalue field — to the
HSE06(0.27) field, so band-gap-sensitive predictions can be made across a strain sweep
without paying for the hybrid.

Everything is measured against `HSE06(0.27)` — mixing parameter α = 0.27, not the more
common 0.25. Every external-facing claim carries that caveat.

## Three modes, one model family

| | input | output |
|---|---|---|
| **1 · correction** (primary) | PBE eigenvalue field + strain | the PBE→HSE06 residual field |
| **2 · direct** | strain alone | the HSE06 field, no PBE run at inference |
| **3 · pretrain** | strain alone | the PBE field — used only to warm-start Mode 2 |

Mode 1 predicts the **residual**, not the full spectrum. The correction is a ~1.2 eV object
carrying ~325 meV of structured variation; relearning a ~40 eV spectrum to recover it would
be strictly harder.

## Two roots, and a third that is not reachable

| | where | committed |
|---|---|---|
| results, figures | `results/`, `figures/` | yes — every number is checkable without the dataset |
| the frozen corpus | `feasibility/gate-4-strain-sweep/results/` | yes, and **read-only from here** |
| extracted VASP text | `/Pool` | never, and nothing here can reach it |

`locations.py` resolves all three and asserts the distinctions. Nothing in this library needs
the raw archives: Gate 4 detached from `/Pool` after its table was built, and this library
starts downstream of that. Every run directory in those archives carries a licensed
pseudopotential and this remote is public.

## What is reused rather than rewritten

Gate 4 owns the strain convention, the symmetry orbits, the frozen splits, the observable
definitions and the deformation-potential baseline. `locations.py` puts its `code/` on the
import path and this library imports them. A second definition here could drift from the one
the exams were pre-registered against, and the drift would be invisible.

**One exception, and it is a correction.** Gate 4's `orbit_labels` factorises on
`str(canonical_strain(row))`, and `np.round` preserves signed zero while `==` does not — so
156 orbits split on a difference that is not one, and the count comes out 658 where there
are 348. Its own `step1_noise` used the correct route and published 213 multi-member orbits
over 996 points; the two were never compared. `symmetry.py` applies the float normalization
the corpus already requires (`learnable-structure-contract#seam-purity`: negative zero maps
to positive zero) and reproduces 348. Both groupings are reported wherever it matters.

That correction is not cosmetic. Under proper grouping the gradient-boosted baseline loses
**34 meV** it had not earned, and Gate 4's claim that "no model was exploiting symmetry-image
leakage" does not hold for it. Five-parameter deformation-potential theory barely moves,
which is why Gate 4's verdict survives — and is in fact strengthened.

## The modules

| module | what it is |
|---|---|
| `locations.py` | the roots, and the import path that makes reuse work |
| `corpus.py` | the 1,131 distinct shapes, VBM-referenced, with orbits and the three frozen splits |
| `symmetry.py` | the 48 octahedral operations on strain and on the mesh; the corrected orbit labeller; a calibration battery |
| `observables.py` | O1–O4 and the density of states, from a field — predicted or true, by one procedure |
| `baselines.py` | B0–B4, and the Phase-1 reproduction gate |
| `differentiation.py` | the differentiation boundary: arrays in, arrays out, no tensor escapes |
| `models/branch_trunk.py` | Family A, the branch-and-trunk operator |
| `training.py` | orbit-grouped folds; early stopping on inner folds only |
| `evaluate.py` | the ladder, the band groups, the DOS, the two structured splits |

## Substrate

Reverse-mode differentiation is borrowed and quarantined in `differentiation.py`. Only plain
`numpy` arrays cross that file's boundary — no tensors, tapes or graphs — which keeps the
corpus's seam rule true from the first commit and makes replacing the substrate an edit to
one file.

The project's own numerics library, `numbers`, is a certifying generator of dual-number and
Taylor-jet libraries: **forward** mode, machine-checked in ACL2, lowered to straight-line
C++. That is the right instrument for an oracle's elementary functions and the wrong one for
training, where forward mode costs one pass per parameter. What is taken from it instead is
its verification culture — anti-theater, and a residual trust boundary named verbatim. The
error card is built that way.

## Checks that must fire

Each of these fails loudly if the machinery is wrong, and each has been watched fail:

```
python corpus.py         # 1,131 shapes, 348 orbits, the splits
python symmetry.py       # 213 multi-member orbits over 996 points, reproducing Gate 4's
                         # step 1 independently; twins agree after the group action
python observables.py    # extraction matches Gate 4's table to 1e-15 eV
python baselines.py      # B4 family holdout 69.7 meV and B1gap 47.5 meV, as published
python models/branch_trunk.py   # the model beats the stretch baseline it contains
```

The last one matters more than it looks. The branch–trunk model is given the PBE eigenvalue
at the point it is evaluating, so it can represent `ΔE = slope·E + intercept` per branch
exactly — the two-branch stretch of B1 and B2. The operator therefore **contains** the model
it must beat, and a failure to beat it is a training failure rather than an expressivity one.

## Known limits, stated rather than discovered later

- **Continuous-k output is experimental and unvalidated.** The trunk will return a number at
  any k; there is no off-mesh ground truth without new DFT, and none is in scope.
- **The indirect→direct crossover is mesh-limited.** 44 shapes are direct-gap at Γ on this
  mesh, but the true conduction minimum sits near 0.76 of Γ→X while the nearest mesh point is
  at 0.857. The crossover is real; its location is not converged.
- **Two families carry argmin hops** — uniaxial and biaxial, both inside
  `2-stretch-one-axis-or-two-axes` — where the conduction minimum jumps between mesh points
  and leaves 76–151 meV kinks. Gap metrics there partly measure the mesh.
- **Group averaging does not enforce the Γ degeneracy.** Under isotropic strain the input is
  invariant under all 48 operations and every operation fixes Γ, so the average collapses to
  the raw prediction. The ≤1 meV degeneracy check is an empirical acceptance test here, not a
  guarantee.
