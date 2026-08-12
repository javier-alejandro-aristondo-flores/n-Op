---
id: generic-dynamics
title: "Dynamics — the GENERIC form"
owns:
  - the two-generator equation of motion
  - regimes as extractions
  - energy and entropy functionals
  - Poisson and friction operator blocks
  - per-tier generator structure
  - gauge fixing and the electrostatic partition
anchors:
  generic-form: "The two-generator form"
  extraction-principle: "Every regime is an extraction"
  functionals: "The energy and entropy functionals"
  operators: "The Poisson and friction operators"
  nine-regimes: "The nine regimes as extractions"
  per-tier-generators: "Generator structure is per tier"
  jacobi-status: "Jacobi status per Poisson block"
  level-conditional-activation: "Energy activation is level-conditional"
  gauge-partition: "Gauge fixing and the electrostatic partition"
depends-on:
  - unified-state
  - born-oppenheimer-levels
  - multiscale-state
  - residual-definitions
  - coupling-structure
  - typed-compositions
  - build-sequence
open-questions: []
---
# Dynamics — the GENERIC form

## The two-generator form

Time evolution uses the **GENERIC** form (General Equation for the
Non-Equilibrium Reversible–Irreversible Coupling):

```
dx/dt = L · δE/δx + M · δS/δx
```

- `E[x]` — total energy functional.
- `S[x]` — total entropy functional.
- `L` — Poisson operator: antisymmetric; reversible dynamics.
- `M` — friction operator: symmetric, positive semidefinite; irreversible
  dynamics.
- Degeneracy conditions: `L · δS/δx = 0` (the reversible part conserves entropy)
  and `M · δE/δx = 0` (the dissipative part conserves energy).

`x` is the seven-tuple of [unified-state#slots].

## Every regime is an extraction

Each traditional regime of multiphysics is recovered as an **extraction** of this
single equation. Static observables are equilibrium readouts (fixed points where
`dx/dt = 0`); time-evolving observables are trajectory readouts. The structural
residual that grounds every other is the **equation-of-motion violation residual**
`‖dx/dt − (L δE/δx + M δS/δx)‖²`. Every other residual category in
[residual-definitions#categories] is either a refinement of it (per state
component, per axis) or an algebraic identity the dynamics must satisfy; the
emission discipline for all of them is [residual-definitions#granularity].

## The energy and entropy functionals

The two functionals decompose as:

```
E[x] = E_kin(ions)      Σ_I |P_I|²/2M_I + tr(Π_hᵀΠ_h)/2W
     + E_BO(R, h)       min_γ̂ ⟨Ĥ_electronic⟩[γ̂; R, h]
     + E_KS[γ̂]          kinetic + Hartree + exchange-correlation on γ̂
     + E_EM[A]          (1/8π) ∫ (|E_⊥|² + |B|²) dr   — transverse sector only;
                        the longitudinal/electrostatic energy lives in the
                        matter functionals (see the gauge partition below)
     + E_coupling       Σ_{c ∈ CouplingSpec, v ∈ realize(c) | v.target = Scalar} v
                        — channels declared per coupling-structure;
                          MVP set: electron-phonon, minimal coupling,
                          ion-ion electrostatic.

S[x] = S_vib           vibrational entropy from the phonon spectrum
     + S_electronic     Fermi–Dirac entropy of the γ̂ spectrum
     + S_config         configurational entropy of coarse-grained DOFs
```

## The Poisson and friction operators

The two operators decompose as:

```
L (antisymmetric Poisson):
  · symplectic on (R, P)         canonical ion phase space
  · symplectic on (h, Π_h)       Parrinello–Rahman cell phase space
  · Liouville–von Neumann on γ̂   (1/iℏ) [Ĥ_KS, ·]
  · Maxwell on A                 Hamiltonian form of the EM field
  · semiclassical streaming      on emergent distributions
  · cross-blocks                 Σ_c Σ_{v ∈ realize(c) | v.target = AntisymmForm} v
                                 (coupling-structure)

M (symmetric, positive semidefinite):
  · diagonal kernels             per-component dissipation (intra-block)
  · cross-kernels                Σ_c Σ_{v ∈ realize(c) | v.target = PSDSymmForm} v
                                 (coupling-structure;
                                  MVP set: phonon-phonon and electron-phonon
                                  scattering kernels)
```

The cross-blocks and cross-kernels are generated from declared channels, not
enumerated: [coupling-structure#coverage-policy].

These pieces are assembled across the four levels of
[born-oppenheimer-levels#hierarchy]; each level contributes the `E`, `S`, `L` and
`M` terms that act on its irreducible state.

## The nine regimes as extractions

| Regime | Extraction |
|--------|-----------|
| Structural | Critical points of `E` at `T = 0` (or `F` at `T > 0`); 1st derivatives |
| Mechanical | 2nd strain-derivatives of `F` at equilibrium |
| Thermal | Eigendecomposition of `∂²E_BO/∂u²` (phonons); BTE for phonon distribution |
| Electronic | SCF as gradient flow on `E_KS`; TDKS as Liouville on `γ̂` (pure `L`) |
| Magnetic | spin-doubled `γ̂`; spin equation of motion = `L` (precession) + `M` (orientation-preserving relaxation `S × (S × H_eff)`) |
| Optical | Response of `γ̂` to `A(t)` via `L`; absorption via `M` (radiative damping) |
| Transport | BTE on emergent carrier distribution: `L` (streaming) + `M` (collisions) |
| Thermodynamic | min `F` at fixed `(T, V, N)`; convex hull of `{F_φ}` |
| Chemical/surface | Master equation on configurations (`M` = rate matrix); minimum-energy-path search on `E_BO` |

The per-regime derivation of each extraction from the unified structure is
[typed-compositions].

## Generator structure is per tier

The two-generator form and its degeneracy conditions `L·δS/δx = 0`,
`M·δE/δx = 0` hold **per tier / per level, with the generators active at that
tier** — not as a single global bracket over all variables simultaneously. This
is what reconciles the written functionals with the degeneracy conditions and
with the "degeneracy verified" artifact of [build-sequence#phases]. The tiers are
[multiscale-state#three-tiers]; the split is the standard GENERIC
mechanical-versus-thermal one.

- **The `γ̂`-block of `L` is the Lie–Poisson bracket** — `{A,B}(γ̂) = Tr( γ̂ ·
  [δA/δγ̂, δB/δγ̂] )`, giving `∂γ̂/∂t = −(i/ℏ)[Ĥ_KS, γ̂]` with `Ĥ_KS = δE/δγ̂`,
  written `[·, γ̂]` **not** the bare `[Ĥ_KS, ·]`. The Lie–Poisson form satisfies
  the **Jacobi identity by construction** and **degeneracy**: the Fermi–Dirac
  electronic entropy is a spectral functional of `γ̂`, so `δS_el/δγ̂` commutes
  with `γ̂` and `L_γ̂·δS_el/δγ̂ = [δS_el/δγ̂, γ̂] = 0`.
- **The `born-oppenheimer-surface` level is single-generator (Hamiltonian) at
  fixed entropy.** The symplectic and Parrinello–Rahman blocks generate the
  `E_BO`-flow; `S_vib(R,h)` is a slow / parametric functional whose
  `(R,h)`-dependence drives the dissipative dynamics of the slow and macro
  tiers, not that level's bracket. The apparent `L·δS_vib/δR ≠ 0` is therefore
  not a degeneracy violation: at `born-oppenheimer-surface` the active generator
  is `E` alone (an isothermal single-generator contraction), and entropy
  production lives with the distribution and configurational variables.

The consequence for the `Degeneracy` residual category is stated at
[residual-definitions#categories].

## Jacobi status per Poisson block

Canonical blocks (symplectic `(R,P)`, `(h,Π_h)`; Lie–Poisson `γ̂`; Maxwell `A`)
satisfy Jacobi **exactly**. Generated `AntisymmForm` cross-blocks
([coupling-structure#target-shapes]) conserve energy by antisymmetry but do
**not** automatically satisfy Jacobi — that is an additional condition. V1
restricts them to the semidirect-product / Lie–Poisson class, where Jacobi
holds by construction, or flags them. The "Jacobi verified" artifact of
[build-sequence#phases] is exact for canonical blocks and a cert-side numerical
check for generated cross-blocks; it is not a global symbolic proof.

## Energy activation is level-conditional

`E[x]` is not a flat simultaneous sum.

At `quantum-electronic-substrate` the active electronic energy is
`E_KS[γ̂; R₀, h₀]` — **parametric in the frozen geometry**, carrying
`∫ v_ext(R)·n + V_II(R,h)` even though `γ̂` is the active variable.

At `born-oppenheimer-surface`, `E_BO(R,h) = min_γ̂ E_KS[γ̂; R,h]` *replaces*
`E_KS` with `γ̂` resolved, so there is no double count. The electron-phonon
coupling channel contributes the linear-order cross-term for the `L` and `M`
blocks and the beyond-reference part of `E_coupling` — not the full
electron–ion energy.

## Gauge fixing and the electrostatic partition

**Normative.** The state's `A` ([unified-state#slots]) is carried in the **Weyl
gauge** `A₀ ≡ 0`, with the remaining time-independent gauge freedom fixed by
transversality `∇·A = 0` — the Coulomb-gauge radiation field.

Under this split, `E_EM[A] = (1/8π)∫(|E_⊥|² + |B|²)` counts the **transverse
(radiation) sector only**. The **longitudinal / electrostatic sector is owned by
the matter functionals** — the Hartree term inside `E_KS[γ̂]` and the ion–ion
electrostatic channel — and appears nowhere in `E_EM`, so no electrostatic
energy is double-counted between the field and the matter terms. This is the
standard nonrelativistic-QED partition: transverse field dynamical, Coulomb
interaction instantaneous in the matter sector.

Three consequences:

- The `EOM/A` residual ([residual-definitions#eom-categories]) is evaluated on
  the transverse `A` in this gauge, and is therefore gauge-unambiguous.
- The minimal-coupling channel ([coupling-structure#target-shapes]) reads the
  transverse `A`.
- Gauge invariance of observables remains architectural — it is carried by the
  equivariance marker, registry row 104, not by a residual.
