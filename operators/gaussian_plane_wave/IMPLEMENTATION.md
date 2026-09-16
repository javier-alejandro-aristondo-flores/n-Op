# gaussian_plane_wave — atomic structure → charge density field

**Operator.** GPWNO — Kim & Ahn, ICML 2024. Suite entry: `test-suite.md` §4, III.3, provisional.

## What it assembles

Atoms embedded by element and pseudopotential title → a plane-wave branch (messages from atoms
onto a fixed probe lattice in fractional coordinates, factorized spectral layers over that lattice,
an analytic plane-wave readout at any query point) plus a gaussian branch (fixed-exponent gaussians
times real spherical harmonics per atom, images summed by cell heights under a smooth envelope,
coefficients from the structure anchor's own message-passing stack) → the sum, renormalized to the
electron count.

## Why it is shaped this way

**A global basis and a local basis, split by what each carries.** The probe lattice's plane waves
carry the smooth part; the gaussians carry the cores, where the pseudo-density is signed and no
positivity clamp is applied.

**The fixed-frame variant first.** This corpus never rotates a cell, so an invariant stack plus a
perceptron emits the gaussian coefficients directly; the equivariant head is the expensive class
and is not this build.

## Floors and kill thresholds

Beat the superposed-atomic-density floor by five times or reject. The kill benchmark is the
structure anchor at matched budget, same campaign, split, query sampling and conventions: within
its error the entry stands; up to a quarter worse it stays only with three times faster inference
or an extrapolation win; worse than that it is redundant and retires. The canon's expectation,
recorded in advance: the redundant band or worse.

## Implementation specification

To be written.
