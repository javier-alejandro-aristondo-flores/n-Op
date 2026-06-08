---
id: arch-02-libraries
title: Library landscape
status: draft
revision: 1
canonical-for:
  - library partitioning
depends-on: []
referenced-by: []
research-sources: []
---
# Library landscape

`n-Op` is partitioned into three sibling libraries.

- **`/physics`** — a substrate-agnostic reference oracle. It encodes the laws of
  the system: state structure, dynamics, observable definitions, residual
  definitions, and certification obligations. It does **not** hold time-varying
  state values, train neural networks, integrate trajectories, or wrap external
  DFT codes at runtime. This document is primarily about `/physics`.
- **`/informed-operator`** — the PINO itself. It consumes `/physics` and learns
  the time-evolution operator. Design notes live under
  `informed-operator/design/`.
- **`/interface`** — the user-facing surface. Out of scope for the current
  design pass.

Engineering aspects (defects, dopants, surfaces, interfaces, operating-condition
effects) live **inside** `/physics`, not in a separate library.

---
