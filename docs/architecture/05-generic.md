---
id: arch-05-generic
title: Dynamics — GENERIC
status: draft
revision: 1
canonical-for:
  - GENERIC equation
  - nine regimes as extractions
depends-on: []
referenced-by:
  - arch-06-physics-graph
  - arch-08-bo-levels
  - arch-19-coupling-structure
  - arch-20-representations
  - arch-21-multiscale-state
research-sources: []
---
# Dynamics — GENERIC

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
- Degeneracy conditions: `L · δS/δx = 0` (reversible part conserves entropy) and
  `M · δE/δx = 0` (dissipative part conserves energy).

Each traditional regime of multiphysics is recovered as an **extraction** of
this single equation. Static observables are equilibrium readouts (fixed points
where `dx/dt = 0`); time-evolving observables are trajectory readouts. The
structural residual that grounds every other is the **EOM-violation residual**
`‖dx/dt − (L δE/δx + M δS/δx)‖²`. Every other residual category in
`arch-11-residuals` is either a refinement of it (per state component, per
axis) or an algebraic identity the dynamics must satisfy. `/physics` emits the
full granular residual vector; aggregation into a scalar training objective
lives in `/informed-operator`.

### Canonical functionals and operators

The two functionals decompose as:

```
E[x] = E_kin(ions)      Σ_I |P_I|²/2M_I + tr(Π_hᵀΠ_h)/2W
     + E_BO(R, h)       min_γ̂ ⟨Ĥ_electronic⟩[γ̂; R, h]
     + E_KS[γ̂]          kinetic + Hartree + exchange-correlation on γ̂
     + E_EM[A]          (1/8π) ∫ (|E_⊥|² + |B|²) dr   — transverse sector only;
                        the longitudinal/electrostatic energy lives in the
                        matter functionals (normative gauge paragraph below)
     + E_coupling       Σ_{c ∈ CouplingSpec, v ∈ realize(c) | v.target = Scalar} v
                        — channels declared per arch-19-coupling-structure;
                          MVP set: electron-phonon, minimal coupling,
                          ion-ion electrostatic.

S[x] = S_vib           vibrational entropy from the phonon spectrum
     + S_electronic     Fermi–Dirac entropy of the γ̂ spectrum
     + S_config         configurational entropy of coarse-grained DOFs
```

The two operators decompose as:

```
L (antisymmetric Poisson):
  · symplectic on (R, P)         canonical ion phase space
  · symplectic on (h, Π_h)       Parrinello–Rahman cell phase space
  · Liouville–von Neumann on γ̂   (1/iℏ) [Ĥ_KS, ·]
  · Maxwell on A                 Hamiltonian form of the EM field
  · semiclassical streaming      on emergent distributions
  · cross-blocks                 Σ_c Σ_{v ∈ realize(c) | v.target = AntisymmForm} v
                                 (arch-19-coupling-structure)

M (symmetric, positive semidefinite):
  · diagonal kernels             per-component dissipation (intra-block)
  · cross-kernels                Σ_c Σ_{v ∈ realize(c) | v.target = PSDSymmForm} v
                                 (arch-19-coupling-structure;
                                  MVP set: phonon-phonon and electron-phonon
                                  scattering kernels)
```

These pieces are assembled across the four levels of `arch-08-bo-levels`; each level contributes
the `E`, `S`, `L`, and `M` terms that act on its irreducible state.

### The nine regimes as extractions

| Regime | Extraction |
|--------|-----------|
| Structural | Critical points of `E` at `T = 0` (or `F` at `T > 0`); 1st derivatives |
| Mechanical | 2nd strain-derivatives of `F` at equilibrium |
| Thermal | Eigendecomposition of `∂²E_BO/∂u²` (phonons); BTE for phonon distribution |
| Electronic | SCF as gradient flow on `E_KS`; TDKS as Liouville on `γ̂` (pure `L`) |
| Magnetic | spin-doubled `γ̂`; spin EOM = `L` (precession) + `M` (orientation-preserving relaxation `S × (S × H_eff)`) |
| Optical | Response of `γ̂` to `A(t)` via `L`; absorption via `M` (radiative damping) |
| Transport | BTE on emergent carrier distribution: `L` (streaming) + `M` (collisions) |
| Thermodynamic | min `F` at fixed `(T, V, N)`; convex hull of `{F_φ}` |
| Chemical/surface | Master equation on configurations (`M` = rate matrix); minimum-energy-path search on `E_BO` |

The per-regime derivations of each extraction from the unified structure are in
the `docs/implementation/` tree (especially `impl-06-compositions`) and grounded
in `physics/research/group-{A,B,C}-*.md`.

### Generator structure is per-tier (degeneracy / Jacobi normalization)

The two-generator form and its degeneracy conditions `L·δS/δx = 0`, `M·δE/δx = 0`
hold **per tier / per BO level with the generators active at that tier**, not as a
single global bracket over all variables simultaneously. This is what reconciles
the written functionals with the degeneracy conditions and the `impl-10` Phase-8
"degeneracy verified" artifact. (The tiers are defined in
`arch-21-multiscale-state`; the standard GENERIC mechanical-vs-thermal split.)

- **The `γ̂`-block of `L` is the Lie–Poisson bracket** — `{A,B}(γ̂) = Tr( γ̂ ·
  [δA/δγ̂, δB/δγ̂] )`, giving `∂γ̂/∂t = −(i/ℏ)[Ĥ_KS, γ̂]` with `Ĥ_KS = δE/δγ̂`,
  written `[·, γ̂]` **not** the bare `[Ĥ_KS, ·]`. The Lie–Poisson form satisfies the
  **Jacobi identity by construction** and **degeneracy**: the Fermi–Dirac
  electronic entropy is a spectral functional of `γ̂`, so `δS_el/δγ̂` commutes with
  `γ̂` and `L_γ̂·δS_el/δγ̂ = [δS_el/δγ̂, γ̂] = 0`.
- **L2 (the mechanical surface) is single-generator (Hamiltonian) at fixed
  entropy.** The symplectic and Parrinello–Rahman blocks generate the `E_BO`-flow;
  `S_vib(R,h)` is a slow / parametric functional whose `(R,h)`-dependence drives the
  dissipative dynamics of the slow and macro tiers, not the L2 bracket. The apparent
  `L·δS_vib/δR ≠ 0` is therefore not a degeneracy violation: at L2 the active
  generator is `E` alone (an isothermal single-generator contraction); entropy
  production lives with the distribution / configurational variables.

**Jacobi status per `L`-block.** Canonical blocks (symplectic `(R,P)`, `(h,Π_h)`;
Lie–Poisson `γ̂`; Maxwell `A`) satisfy Jacobi **exactly**. Generated `AntisymmForm`
cross-blocks (`arch-19-coupling-structure`) conserve energy by antisymmetry but do
**not** automatically satisfy Jacobi (an additional condition); V1 restricts them to
the semidirect-product / Lie–Poisson class (Jacobi by construction) or flags them.
`impl-10` Phase-8 "Jacobi verified" is exact for canonical blocks and a cert-side
numerical check for generated cross-blocks — not a global symbolic proof.

**`Degeneracy` is cert-only, not a training residual.** Under the per-tier generator
structure the `Degeneracy` category (`arch-11-residuals §11.1`) is **identically zero
by construction**; it is a cert obligation — a generator-construction-bug tripwire —
not a PINO loss term (removed from the `arch-11 §11.4.1` training gate).

**`E`-functional activation is level-conditional.** `E[x]` is not a flat simultaneous
sum: at L1 the active electronic energy is `E_KS[γ̂; R₀, h₀]` — **parametric in the
frozen geometry** (it carries `∫ v_ext(R)·n + V_II(R,h)` even though `γ̂` is the
active variable); at L2, `E_BO(R,h) = min_γ̂ E_KS[γ̂; R,h]` *replaces* `E_KS` with `γ̂`
resolved (no double-count). The e-ph coupling channel contributes the linear-order
cross-term for the `L`/`M` blocks and the beyond-reference part of `E_coupling`, not
the full electron–ion energy.

**Gauge fixing and the electrostatic partition (normative).** The state's `A`
(`arch-04-state`) is carried in the **Weyl gauge** `A₀ ≡ 0` with the residual
time-independent gauge freedom fixed by transversality `∇·A = 0` — i.e. the
Coulomb-gauge radiation field. Under this split, `E_EM[A] = (1/8π)∫(|E_⊥|² + |B|²)`
counts the **transverse (radiation) sector only**; the **longitudinal /
electrostatic sector is owned by the matter functionals** — the Hartree term inside
`E_KS[γ̂]` and the ion–ion electrostatic channel — and appears nowhere in `E_EM`, so
no electrostatic energy is double-counted between the field and matter terms. This
is the standard nonrelativistic-QED partition (transverse field dynamical; Coulomb
interaction instantaneous in the matter sector). Consequences: the `EOM/A` residual
(`arch-11-residuals §11.1`) is evaluated on the transverse `A` in this gauge and is
therefore gauge-unambiguous; the minimal-coupling channel (`arch-19`) reads the
transverse `A`; gauge invariance of observables remains architectural (the
equivariance marker, registry row 104). (2026-07 gap-audit A2.)

---
