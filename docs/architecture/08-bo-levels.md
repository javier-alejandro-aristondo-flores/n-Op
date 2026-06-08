---
id: arch-08-bo-levels
title: The 4-level Born–Oppenheimer hierarchy
status: draft
revision: 1
canonical-for:
  - 4-level BO hierarchy
  - dressing tiers (V1 vs V2 scope)
depends-on:
  - arch-04-state
  - arch-05-generic
  - arch-06-physics-graph
referenced-by:
  - impl-07-residual-factory
  - impl-09-cross-cutting
research-sources:
  - physics/research/group-A-ion-dynamics.md
  - physics/research/group-B-electronic-magnetic-optical.md
  - physics/research/group-C-transport-thermo-chemical.md
---

# The 4-level Born–Oppenheimer hierarchy

The 7-tuple state (`arch-04-state`) partitions into four levels whose
dependencies flow strictly upward (Level 4 → 3 → 2 → 1). The hierarchy
is a partition of the **state-component space**, complementary to
(not competing with) the `PhysicsGraph` (`arch-06-physics-graph`),
which partitions the *computation*.

- **L1 — Quantum electronic substrate.** Operates on `γ̂(r,r';t)` and
  `A(r,t)` at fixed `(R, h)`. Regimes: electronic, optical, magnetic.
  Math: Kohn–Sham / TDKS / TDCSDFT, Hohenberg–Kohn, Runge–Gross,
  Liouville–von Neumann.
- **L2 — Born–Oppenheimer surface.** Operates on `(R, P, h, Π_h)` with
  immutable `Z`. Uses `E_BO(R, h) = min_γ̂ E[γ̂; R, h]`, Hellmann–Feynman
  forces, DFT stress. Regimes: structural, mechanical. Math: variational
  on `(R, h)`, strain expansion, Parrinello–Rahman dynamics.
- **L3 — Equilibrium statistics on the BO surface.** Bose–Einstein,
  Fermi–Dirac, Maxwell–Boltzmann over L1/L2 spectra. Regimes: thermal,
  thermodynamic. Math: partition functions, free energies,
  quasi-harmonic approximation, convex hull.
- **L4 — Non-equilibrium kinetics.** Distributions over phase space;
  full GENERIC `L + M`. Regimes: transport, chemical/surface. Math:
  Boltzmann transport, Kubo / Green–Kubo, master equation, Marcus
  theory, transition-state theory, minimum-energy-path search.

Each level uses lower levels as inputs but introduces its own
irreducible state. A regime is a navigational *view* across the levels
that contribute to it (thermal spans L3 statistics and L4 phonon
transport).

In the `PhysicsGraph`, BO level is **derivable** from the transitive
inputs of a node — it is not a stored field on `Node`
(`arch-06-physics-graph §6.5`). Stage 1 ordering follows the level
discipline: L1 nodes are constructed first; L2/L3/L4 nodes depend on
their L1/L2/L3 ancestors.

## 8.1 Dressing tiers (V1 vs V2 scope)

Within L1, corrections that "dress" the bare substrate are organized
into deferred-implementation tiers. **These are V1-vs-V2 implementation
scope, not a runtime hierarchy.** Dressing is a Stage-4 codegen choice
for specific `MethodInvoke` nodes; the `dressing` tag on
`ContributionFacets` is a provenance label, not a loss-weighting axis.

```
Layer 1      Bare substrate.
Layer 1.25   One-shot closed-form dressing — pure functions, no iteration.
             V1 members: G₀W₀ quasi-particle energies; first-order
             self-consistent phonons (SCP); the linear-response
             sub-stage producing Z*, ε∞, χ∞; the LO/TO non-analytic
             correction; one-shot diagonalization; one-shot topological
             invariants.
             Cert: OneShotCert (impl-07-residual-factory §7.7).
Layer 1.75   Iterative fixed-point dressing — DEFERRED to V2 in code,
             SPECIFIED for forward compatibility. Members: self-
             consistent GW, full SCPH/SSCHA, DMFT, BSE iterative
             variants, self-consistent polaron.
             Cert: IterativeResult (impl-07-residual-factory §7.7).
             Each member gets a bespoke Stage-4 lowering, NOT a shared
             primitive.
Layer 2      Property machinery — the rest of the PhysicsGraph.
Layer 3      PINO — lives in /informed-operator.
```

The diamond MVP runs entirely against Layer 1.25, preserving the
closed-form discipline. Diamond needs only two dressings:

- **G₀W₀** — Kohn–Sham underestimates the diamond gap by ~30%; G₀W₀
  corrects to ~5.5 eV vs measured 5.47 eV.
- **First-order SCP** — marginal at 773 K, growing above 1500 K.

Comprehensiveness is preserved via the V1 specification of Layer 1.75
even though no V1 code implements it.
