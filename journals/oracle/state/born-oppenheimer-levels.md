---
id: born-oppenheimer-levels
title: "The four Born–Oppenheimer levels"
owns:
  - four-level Born-Oppenheimer hierarchy
  - regime as a view across levels
  - dressing tiers
  - dressing-staleness bound
anchors:
  hierarchy: "The four levels"
  kinetics-irreducible-state: "The irreducible state of the non-equilibrium-kinetics level"
  dressing-tiers: "Dressing tiers"
depends-on:
  - unified-state
  - multiscale-state
  - physics-graph
  - compose-time-pipeline
  - residual-definitions
  - residual-machinery
  - capability-slices
  - formula-registry
open-questions:
  - id: g0w0-cost-scope-tag
    anchor: dressing-tiers
    summary: "The G₀W₀ quasi-particle correction's evaluation cost is not scope-tagged by cell size. A seconds-tier budget of ten seconds or less is plausible at MVP scale; for version-1 defect supercells it is hours. The cost tier is therefore violated silently rather than refused. This is a cost claim, so the error-estimate rule does not reach it."
---
# The four Born–Oppenheimer levels

## The four levels

The micro seven-tuple ([unified-state#slots]) partitions into four levels. Each level takes the
levels beneath it as input and nothing flows the other way.

The hierarchy is a partition of the **state-component space**. It is complementary to, not
competing with, the physics graph ([physics-graph#the-graph]), which partitions the **computation**.

| Level | Operates on | Regimes | Mathematics |
|---|---|---|---|
| `quantum-electronic-substrate` | `γ̂(r,r';t)` and `A(r,t)` at fixed positions and cell | electronic, optical, magnetic | Kohn–Sham and time-dependent Kohn–Sham, time-dependent current-spin-density functional theory, Hohenberg–Kohn, Runge–Gross, Liouville–von Neumann |
| `born-oppenheimer-surface` | `(R, P, h, Π_h)` with immutable species labels | structural, mechanical | variational treatment of positions and cell, `E_BO(R,h) = min_γ̂ E[γ̂; R,h]`, Hellmann–Feynman forces, density-functional stress, strain expansion, Parrinello–Rahman dynamics |
| `equilibrium-statistics` | Bose–Einstein, Fermi–Dirac and Maxwell–Boltzmann occupations over the spectra of the two levels below | thermal, thermodynamic | partition functions, free energies, quasi-harmonic approximation, convex hull |
| `non-equilibrium-kinetics` | distributions over phase space; the full reversible-plus-dissipative generator pair | transport, chemical and surface | Boltzmann transport, Kubo and Green–Kubo, master equation, Marcus theory, transition-state theory, minimum-energy-path search |

Each level uses lower levels as inputs but **introduces its own irreducible state**. A **regime**
is a navigational *view* across the levels that contribute to it — the thermal regime spans
equilibrium-statistics and the phonon transport of non-equilibrium-kinetics.

A node's level is **derivable** from its transitive inputs. It is not a stored field on `Node` ([physics-graph#node]).
Symbolic-lift ordering follows the level discipline: quantum-electronic-substrate nodes are
constructed first, and each higher level's nodes depend on their lower-level ancestors
([compose-time-pipeline#symbolic-lift]).

## The irreducible state of the non-equilibrium-kinetics level

The kinetics level introduces distributions over phase space, which are not recoverable from a
single micro seven-tuple. That irreducible state is concrete, and it is two tiers rather than one
([multiscale-state#three-tiers]):

- the **macro continuum-field tier** — homogenised lattice temperature, potential, carrier
  densities and current density on a device mesh, with the full distribution kept emergent by
  moment closure ([multiscale-state#macro-state-schema]);
- the **slow, configurational tier** — history-dependent defect populations on an hours-to-years
  timescale ([multiscale-state#slow-state-schema]).

The micro seven-tuple is the tier of the two lowest levels.

## Dressing tiers

Within `quantum-electronic-substrate`, corrections that dress the bare substrate are organised
into implementation tiers. **These are version-1-versus-version-2 implementation scope, not a
runtime hierarchy.** Dressing is a lowering choice for specific `MethodInvoke` nodes, and the
`dressing` tag on `ContributionFacets` is a **provenance label, not a loss-weighting axis**. That
is a structural fact rather than a convention — the graph is what makes it true
([physics-graph#observable-selection]).

| Tier | Contents | Certificate |
|---|---|---|
| `substrate` | the bare substrate | — |
| `one-shot-dressing` | closed-form dressing, pure functions, no iteration: G₀W₀ quasi-particle energies; first-order self-consistent phonons; the linear-response sub-stage producing Born effective charges, high-frequency permittivity and susceptibility; the longitudinal-to-transverse-optical non-analytic correction; one-shot diagonalisation; one-shot topological invariants | `OneShotCert` ([residual-machinery#dressing-certs]) |
| `iterative-dressing` | iterative fixed-point dressing: self-consistent GW; full self-consistent phonons (SCPH) and the stochastic self-consistent harmonic approximation (SSCHA); temperature-dependent effective potentials (TDEP); dynamical mean-field theory (DMFT); iterative Bethe–Salpeter variants; the self-consistent polaron. Deferred to version 2 in code and specified for forward compatibility; each member gets a bespoke lowering rather than a shared primitive | `IterativeResult` ([residual-machinery#dressing-certs]) |
| `property-machinery` | the rest of the physics graph | — |

The operator is a **library**, not a dressing tier. It lives outside this hierarchy entirely.

**Frozen at reference (normative).** A one-shot dressing is computed **once per composition, at
the reference state, and is thereafter constant.** It does not respond to the operator's state
excursions and it contributes no gradient — gap-versus-strain, for instance, enters only through
the separate deformation potential of registry row 63 ([formula-registry#manifest]), never through the
frozen quasi-particle shift. This is a deliberate trade: it is what makes the tier closed-form,
and its price is a **dressing-staleness** term in the error model ([residual-definitions#error-budget]).

**The staleness term has a bound, and the bound is the validity radius.** A frozen dressing is an
approximation, so it owes an estimator like any other approximation, and that estimator *is* the
radius. To first order the dropped term is

```
‖Δx‖ · ‖∂(dressing)/∂x‖_ref
```

The sensitivity coefficient is measured **once, at the reference state, at compile time** — the
dressing is already computed there, so the measurement is nearly free — and the runtime factor is
a norm on the state. `OneShotCert` carries the coefficient field, and the product enters
`combineTol` as the dressing-staleness term ([residual-definitions#error-budget]). A composition that leaves
the radius is refusable, because the radius is a number.

**The diamond MVP runs entirely against `one-shot-dressing`**, preserving the closed-form
discipline, and it needs exactly one dressing wired:

- **The G₀W₀ quasi-particle correction (registry row 6).** Kohn–Sham with the PBE functional
  underestimates the diamond indirect gap by about 23% — roughly 4.2 eV against a measured
  5.47 ± 0.01 eV at 300 K — and G₀W₀ brings it to about 5.5 eV.
- **First-order self-consistent phonons are judged and not wired.** The correction is marginal at
  773 K and grows above 1500 K. The MVP covers vibrational temperature dependence with the
  quasi-harmonic approximation instead (registry row 12, which suffices to 800 °C
  ([capability-slices])), and the full self-consistent treatment (registry row 13) defers with
  `iterative-dressing`.
