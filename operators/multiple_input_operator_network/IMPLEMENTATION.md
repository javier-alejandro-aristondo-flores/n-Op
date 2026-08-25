# multiple_input_operator_network — (charge density, local potential) → electron localization field

**Operator.** MIONet — Jin, Meng, Lu, *SIAM Journal on Scientific Computing* 44(6), A3490 (2022).
Suite entry: `test-suite.md` §3, II.2.

## What it assembles

Two sensor encoders, one per labeled input field, combined multiplicatively in the latent space,
read out through the shared trunk.

## Why it is shaped this way

It rides the Deep Operator Network's stack entirely and exists as its own package for one reason:
it is its own literature name with its own question — does the potential carry information about
electron localization that the density does not?

Channel labels do the work here. The operator must know which input field is which, which is why
`GridFunction` carries names rather than bare channel indices.

## Floors and kill thresholds

One gate, and it is decisive: if adding the potential improves on density-alone by five percent
or less, the potential adds nothing and the task is dropped.

## Implementation specification

To be written.
