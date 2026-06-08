---
id: mvp-05-decisions-forced
title: Decisions this slice forces
status: draft
revision: 1
canonical-for:
  - MVP-forced decisions
depends-on: []
referenced-by: []
research-sources: []
---
# Decisions this slice forces

- **Implementation language (H1).** Now decidable against concrete needs:
  reverse-mode AD through implicit-diff adjoints (BTE-RTA, SCF, G₀W₀), staged
  symbolic IR with Stage-4 codegen, IBZ tooling, and GPU support for k-point
  meshes. Candidates per `arch-18-open-decisions §1`: Julia (Symbolics +
  ModelingToolkit + Enzyme), Python + JAX (jit + JAXopt), or a custom MLIR
  stack.
- **TB-3NN-sp³d⁵ for carbon as warm-start initializer.** Used as a seed for
  the SCF inner loop only; not a separately-evaluated formula and not an
  independent residual.
- **Layer-1.25 substrate data (H7).** The closed-form discipline needs L1 to
  expose more than `γ̂`: G₀W₀ needs ~30–50 **unoccupied bands + wavefunctions**;
  QHA needs **volume-dependent (Grüneisen) phonons**. These are the L1 outputs
  the MVP requires — specify them when building `state/level-1`.
- **Reference-battery seed (H4).** Seed `physics/library/cert/reference-data/`
  with the ~10 diamond rows the MVP validates against: lattice a, indirect gap,
  C₁₁/C₁₂/C₄₄, Debye T, κ(300 K), max phonon energy, cohesive/formation energy,
  and the diamond–graphite boundary point.

---
