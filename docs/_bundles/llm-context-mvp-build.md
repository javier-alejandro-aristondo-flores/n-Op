<!-- GENERATED FILE — do not edit. Source files under docs/{architecture,implementation,mvp}/. Regenerate with `python docs/meta/assemble.py`. -->

# n-Op Diamond MVP Build (LLM context bundle)

## Contents

- [The system](#mvp-01-system)
- [γ̂ budget at MVP scale](#mvp-02-gamma-budget)
- [The three capability slices](#mvp-03-capabilities)
- [Decisions this slice forces](#mvp-05-decisions-forced)
- [MVP build order](#mvp-06-build-order)
- [Residual machinery](#impl-07-residual-factory)
- [Build sequence](#impl-10-build-sequence)


<a id="mvp-01-system"></a>

# The system

**Diamond, primitive cell.** Space group Fd-3m (No. 227); 2 carbon atoms at the
8a Wyckoff site; sp³; lattice constant a = 3.567 Å. Eight valence electrons
(2s²2p² × 2) → **4 occupied bands**.

| Anchor | Value | Consequence for the MVP |
|---|---|---|
| Indirect gap | 5.47 eV (X-point) | PBE gives ~4.2 eV (−23%); **G₀W₀ or hybrid required** (registry row 6) |
| Max phonon energy | ~165 meV (~1332 cm⁻¹) | highest of any solid; phonon grid must resolve it |
| Debye temperature | ~2200 K | **QHA valid through ~800 °C** → SCPH (row 13) deferred |
| Thermal conductivity | ~2200 W·m⁻¹K⁻¹ (300 K; battery anchor, exp 2000–2500) | the headline Cap-3 target |
| Elastic constants | C₁₁≈1079, C₁₂≈124, C₄₄≈578 GPa | Cap-1 stability + sound velocity |
| Polarity | **non-polar (homopolar)** | Z\*=0 by symmetry → **no LO-TO, no Fröhlich** → registry rows 17, 21, 22 excluded by applicability |
| High-T failure | air-oxidation onset ~600–700 °C (the actual lifetime limiter); sp³→sp² graphitization only above ~1500 °C in vacuum | the diamond–graphite phase boundary is the Cap-1 thermodynamic check; oxidation is the slow-tier degradation channel (`arch-21`) |

**Units.** Atomic units internally; report eV, Å, W·m⁻¹K⁻¹, cm²V⁻¹s⁻¹.

---


<a id="mvp-02-gamma-budget"></a>

# γ̂ budget at MVP scale

The dense one-body density matrix is `O(N_r²)` and was flagged as a feasibility
risk. At MVP scale it is a non-issue, because γ̂ is **never densified**:

- **Encoding:** `(Reciprocal, BlockDiag)` — one block per k-point — with each block
  stored as **orbitals** (low-rank in the band index: `N_PW × N_b`), not as a
  dense `N_PW × N_PW` matrix.
- **Sizing (primitive cell, G₀W₀-capable basis):** PW cutoff ~400 eV ⇒ `N_PW ≈ 1000`;
  `N_b ≈ 40` (4 occupied + unoccupied manifold for G₀W₀); 8×8×8 Monkhorst–Pack ⇒
  **~29 irreducible k-points**. Orbital storage ≈ `N_PW × N_b × 16 B × N_k`
  ≈ 1000 × 40 × 16 × 29 ≈ **~18 MB**. (Densifying would cost `N_PW² × 16 × N_k`
  ≈ 460 MB per the same mesh — which is exactly why we never do it.)
- **Warm-start initializer:** tight-binding **3NN sp³d⁵** for carbon ⇒ a `~18 × 18` Hamiltonian
  per k — kilobytes. Used to seed the SCF inner loop (`mvp-05-decisions-forced`);
  not a separate residual path.
- **Beyond the MVP:** defect/interface supercells grow `N_PW` linearly; orbital
  storage stays ≈ linear in `N_atoms × N_b`. The dense-γ̂ concern returns only if
  a large supercell is densified — which the encoding forbids. A supercell memory
  budget is the first thing to revisit when leaving the primitive cell.

---


<a id="mvp-03-capabilities"></a>

# The three capability slices

Each capability is a strict selection from the closed vocabularies of
`arch-09-vocabularies` (methods, templates, formulas, bundles), the residual
categories of `arch-11-residuals`, and the cert obligations of `arch-12-cert`.
Formula numbers reference `physics/library/formulas/registry-manifest.csv`.

### Cap 1 — Crystal-structure prediction

*Construct a symmetry-allowed candidate, relax to the E_BO minimum, certify
stability; one heterostructure check (c-BN on diamond) via lattice matching.*

| Facet | MVP content |
|---|---|
| State used | `h`, `R_I`, `Z_I`; `γ̂` (T=0, for `E_BO`) |
| BO levels | L1 (`E_BO = min_γ̂ E`) → L2 (relaxation on (R, h)) |
| Methods | variational-minimization · functional-differentiation · algebraic-combination · symmetry-projection · spectral-decomposition · convex-optimization (hull check only) |
| Templates | `SymmetryAdaptedHamiltonianOf` · `SecondDerivativeOf` · `ClassifyOf` · `StateReadoutOf` · `AlgebraicOf` |
| Formulas | **57** born-stability-criteria · **60** elastic-constants-Cij · **61** bulk-modulus · **62** sound-velocity-isotropic · **85** structure-uniqueness-CSP · **30** defect-formation-energy-zhang-northrup · **44** surface-grand-potential-γ (B5) · **52** vegard-correction · **54** matthews-blakeslee-critical-thickness (c-BN/diamond hetero) · **67** phase-diagram-convex-hull · **124** tp-aware-hull (δ_meta metastability band — metastable diamond reads R_hull = 0) |
| Bundles | B10 static-validity · B7 mechanics · B4 defect (row 30) · B6 interface (rows 52/54; row 54 also B11) · (B5 surface for row 44) · B8 thermodynamics (rows 67/124, the diamond–graphite hull) |
| Residuals | static-validity (Born stability, dynamical stability, space-group equivariance) · structural EOM (`∇_R E_BO = 0`, stress matches) · thermodynamic-consistency (diamond–graphite hull, rows 67/124) |
| Cert | 1 symmetry · 2 bounds · 3 analytic limits · 5 conservation |
| Implementation | DFT `E_BO` + DFPT-stress `C_ij`; TB 3NN sp³d⁵ as SCF warm-start initializer (`mvp-05-decisions-forced`) |

### Cap 2 — Electron-cloud (carrier) diffusion

*Electronic-structure substrate + carrier transport through the lattice.*

| Facet | MVP content |
|---|---|
| State used | `γ̂`, `A`; emergent carrier distribution `f_n(k,r)` |
| BO levels | L1 (bands from `γ̂`) + L4 (carrier transport) |
| Methods | spectral-decomposition · linear-response · kinetic-evolution · state-readout |
| Templates | `SpectrumOf` · `ResponseOfTo` · `KineticEvolutionOf` · `StateReadoutOf` · `AlgebraicOf` |
| Formulas | **1** bandgap-direct · **2** bandgap-indirect · **3** effective-mass-tensor · **4** DOS-tetrahedron · **5** fermi-level-charge-neutral · **6** quasi-particle-shift-G0W0-surrogate · **14** drude-conductivity · **15** matthiessen-mobility · **16** caughey-thomas-mobility · **18** v-sat-intervalley · **19** hall-mobility-from-σ · **20** mobility-impurity-phonon · **24** wiedemann-franz-electronic-kappa |
| Excluded (non-polar) | **17** v-sat-POP-limit · **21** frohlich-coupling · **22** frohlich-scattering-rate — masked off by the `is-polar-material` applicability classifier (false for diamond) |
| Bundles | B1 electronic-structure · B3 transport |
| Residuals | EOM (Liouville on `γ̂`; carrier streaming) · conservation (charge continuity `∂ρ/∂t + ∇·j = 0`) · positivity (`ρ ≥ 0`, `f ∈ [0,1]`) · algebraic (Einstein `D = μ k_B T / q`) |
| Cert | 1 symmetry · 2 bounds · 5 conservation · 6 named-formula consistency (BTE-σ ≡ Kubo-σ) |
| Implementation | DFT+G₀W₀ bands + BTE-RTA; TB 3NN bands as SCF warm-start initializer |

### Cap 3 — Heat diffusion

*Phonon spectrum + phonon-mediated thermal transport through the lattice.*

| Facet | MVP content |
|---|---|
| State used | `R_I`, `P_I`; emergent phonon distribution `n_{qs}`, `T_L` |
| BO levels | L2 (`E_BO` Hessian → phonons) + L3 (Bose statistics) + L4 (phonon BTE) |
| Methods | spectral-decomposition · spectral-aggregation · kinetic-evolution |
| Templates | `HarmonicStiffnessHessianOf` · `SpectrumOf` · `SpectralAggregateOf` (heat capacity, aggregator = `bose-einstein-cv`) · `KineticEvolutionOf` |
| Formulas | **7** acoustic-sum-rule · **8** dynamical-matrix-hermiticity · **9** phonon-dispersion · **10** phonon-DOS · **11** phonon-group-velocity · **12** grueneisen-mode (QHA / thermal expansion) · **25** callaway-lattice-kappa · **121/122** high-T κ siblings of row 25 (4-phonon factor + dormant iterative-LBTE consistency pair) · **70** self-heating-T_op (B9; cheap closure) |
| Deferred | **13** SCPH (QHA suffices ≤800 °C) · **26** phonon-poiseuille-length · **27** second-sound-speed (low-T hydrodynamics, out of harsh-env scope) |
| Bundles | B2 phonon · B3 transport · (B9 self-heating for row 70) |
| Residuals | EOM (phonon streaming + collision; heat equation `∂_t T = ∇·(κ∇T)`) · conservation (energy) · positivity (`ω² ≥ 0`) · algebraic (acoustic sum rule `Σ_J Σ_R Φ(R) = 0`) |
| Cert | 2 bounds · 3 analytic limits (harmonic-crystal, Dulong–Petit) · 5 conservation |
| Implementation | DFPT phonons + 3-phonon BTE-RTA; QHA + Callaway κ available as a closed-form sibling formula whose method-equivalence with the DFPT/BTE path is asserted under cert obligation-6 |

---


<a id="mvp-05-decisions-forced"></a>

# Decisions this slice forces

- **Implementation language (H1) — resolved.** The concrete needs (reverse-mode
  AD through implicit-diff adjoints for BTE-RTA / SCF / G₀W₀, staged symbolic IR
  with Stage-4 codegen, IBZ tooling, optional GPU for k-point meshes) are met by a
  **polyglot of DSLs** (`arch-18-open-decisions`, Closed decisions;
  `physics/research/implementation-language.md`): a **Haskell** compiler-host for
  Stages 1–4 + the substrate, emitting a **Julia** Stage-5 runtime (which owns the
  optional GPU codegen), with **GAP** (group-theory tables) and **Lean 4** (spec
  proofs) offline.
- **TB-3NN-sp³d⁵ for carbon as warm-start initializer.** Used as a seed for
  the SCF inner loop only; not a separately-evaluated formula and not an
  independent residual.
- **Layer-1.25 substrate data (H7).** The closed-form discipline needs L1 to
  expose more than `γ̂`: G₀W₀ needs ~30–50 **unoccupied bands + wavefunctions**;
  QHA needs **volume-dependent (Grüneisen) phonons**. These are the L1 outputs
  the MVP requires — specify them when building `state/level-1`.
- **Reference-battery seed (H4).** `physics/library/cert/reference-data/` carries
  the full diamond battery (seeded 2026-07-08): lattice a, indirect gap,
  C₁₁/C₁₂/C₄₄ + bulk modulus + density, Debye T, max phonon energy,
  κ(300 K), **κ(773 K) ≈ 620 W/m·K** (the high-T 4-phonon anchor), κ(1100 K),
  cohesive energy, the diamond–graphite boundary point, ε_r, the Isberg ToF
  mobilities, v_sat/β, and the Chynoweth pair — every H8 target has a
  machine-readable anchor.
- **Design-grade accuracy targets (H8).** The MVP's headline outputs must meet
  declared accuracy: gap ±0.15 eV post-G₀W₀, C_ij ±5%, κ(300 K) ±20%, E_form
  ±0.2 eV, μ factor-2 (full per-observable ledger in `docs/accuracy-ledger.md`,
  wired via `arch-11-residuals §11.7`). Cert obligation 4 checks them at the
  battery anchors; the high-T anchors κ(773 K)/κ(1100 K) are **landed** (registry
  rows 121–122, the 4-phonon correction + iterative-LBTE sibling; curated κ(T)
  battery in `docs/accuracy-ledger.md`).

---


<a id="mvp-06-build-order"></a>

# MVP build order

A focused subset of the phases in `impl-10-build-sequence`:

1. `core` — autodiff, tensor algebra, mesh integration (k-mesh, tetrahedron).
2. `shared` — Ewald; the tight-binding (3NN sp³d⁵) carbon Hamiltonian builder.
3. `inputs` — the diamond `PeriodicityStructure` + `SiteDecoration` + `Environment`.
4. `state` — `γ̂` as k-blocked orbitals (§2); `(R, P, h)`.
5. methods (the 10) and formulas (the ~34, incl. the κ high-T siblings 121–122) of §3.
6. canonicals — `E_BO` (DFT, with TB 3NN sp³d⁵ as SCF warm-start) and the phonon Hessian.
7. the three capability residuals (Cap 1/2/3 rows above).
8. cert obligations 1–6 and 10 (the registration adjoint gate stays in the MVP,
   `mvp-04`) + the seeded diamond reference battery (`mvp-05` H4).
9. validate: relaxed lattice, gap (with G₀W₀), C_ij, phonon max, κ(300 K) against
   the battery.

Completing this slice yields a diamond-only `/physics` that can emit a granular
residual vector with cotangents, expose observable values, and certify them for
all three capabilities — the concrete substrate `/informed-operator` then trains
against.


<a id="impl-07-residual-factory"></a>


# Residual machinery

The PINO-facing factory that turns named formulas (`impl-04-formulas`)
into `ResidualLeaf` nodes (`arch-06-physics-graph §6.3`) in the
`PhysicsGraph`. Under the always-cheap reframe (`arch-07-pipeline`),
this is now part of Stage 1 (graph construction). The factory has
three responsibilities: generate the leaves with content-addressed keys,
gate registration on adjoint correctness, and provide the per-formula
metadata the runtime kernel uses for its outputs.

## 7.1 The `ResidualGenerator` record

```
record ResidualGenerator {
  name                 : Symbol
  observable           : ObservableRef
  bundle               : BundleId                 -- B1..B11 or the L1 primitive tag
                                                  --   (impl-04-formulas; facet, not identity)
  category             : CategoryTag              -- 19 named tags (arch-11-residuals §11.1)
  layer                : 1..7                     -- compose-time DAG layer (the 7-layer
                                                  --   compute DAG of residual-generator-catalog §2)
  cost-tier            : T0 | T1 | T2 | T3
  diff-tag             : D0 | D1 | D2 | D3 | D4
  dressing-tag         : bare | dressed(scheme: G0W0|SCP-perturbative|LO-TO-NA-correction
                                                |Born-charge|epsilon-infinity
                                                |electronic-susceptibility)   -- = the §7.7 OneShotCert schemes
                         -- provenance label only; not a loss-weighting axis
  characteristic-scale : σ                        -- declared accuracy scale of the observable
                                                  --   (a Quantity in its units), seeded from the
                                                  --   accuracy ledger (arch-11-residuals §11.7,
                                                  --   docs/accuracy-ledger.md); the error-model
                                                  --   input to Quantity.combineTol — never a
                                                  --   fitted weight
  axes                 : List<AxisLabel>          -- the dimensions this generator unfolds over
                                                     (k-point, frequency, atomic pair, shell, …)
  applicability        : (Crystal, Environment) → Bool
  input-contract       : {TypedSlot}
  output-contract      : TypedSlot
  forward              : Inputs → Output
  loss-projection      : Output → Map<ResidualKey, Scalar>
                         -- emits one entry per axis tuple; key is content-addressed (arch-11-residuals)
  weight-policy        : ConsumedBy(/informed-operator)
                         -- /physics declares the granularity; aggregation lives downstream
  sampling-policy      : UniformBatch | RAD(τ) | Importance | ValidationOnly
  dependencies         : {Symbol}                 -- same-pass fixed-point co-convergence
  adjoint-cert         : Passed | Failed(witness) | NotApplicable | Relaxed(rationale)
  registration-hash    : ContentAddress           -- cert-tripwire detection
}
```

## 7.2 Granularity (canonical reference: `arch-11-residuals`)

Each generator unfolds along its `axes` to emit *N* residual
contributions, one per axis tuple. Each contribution is a
`ResidualLeaf` node with a content-addressed `ResidualKey`:

```
ResidualKey = (producer : Producer, axes : Tuple<AxisLabel>)
Producer    = Formula(NamedFormula) | Method(NamedMethod)
```

The PINO holds `Map<ResidualKey, Weight>`; `/physics` emits
`Map<ResidualKey, Scalar>`. Category, bundle, and dressing-tag are
queryable facets via a parallel `Map<ResidualKey, ContributionFacets>`.
The `dressing` facet is a provenance label for cert and audit; bare and
dressed residuals on the same observable live as distinct
`FormulaApply`/`MethodInvoke` chains in the graph (`arch-09-vocabularies`),
not as weighted siblings.

## 7.3 Factory entry point

```
make-residual-generator(observable     : ObservableRef,
                        formula        : NamedFormula,
                        axes           : List<AxisLabel>,
                        sampling-policy: SamplingPolicy,
                        applicability  : (Crystal, Environment) → Bool)
                      → ResidualGenerator
```

Called once per formula at load time. The returned generator is
inserted into Stage 1 of the pipeline when its `applicability`
predicate holds for the current composition.

## 7.4 Generator subtypes

Three generator subtypes:

- **Standard residual** — derived from a named formula; participates in
  loss; D2 entries gated on adjoint existence.
- **Ground-truth-bridge** — anchors a generator to an `Import`-supplied
  target value with `(value, σ, provenance, coverage-mask)`
  (`arch-16-pino-bridge §16.2`); loss is the σ-scaled Huber against the
  target.
- **Cert-only** — no loss contribution; runs as part of cert evidence
  (`arch-12-cert`), not as part of training loss.

## 7.5 Registration-time adjoint gate (hard)

D2 entries run a vJp-vs-JvP check on `N ≈ 64` sampled points at
registration time; if the max relative error exceeds `τ_adj` (default
`1e-4`) the build fails loud. Forces an honest gradient or an explicit
downgrade to D3 / D4 with recorded rationale.

Under the always-cheap reframe, most D2 generators with a fixed-point
solve in their forward pass are wired to the **implicit-diff adjoint**
synthesized at Stage 4 (`arch-07-pipeline §7.4`); the gate verifies
that synthesized adjoint, not a hand-written backward.

## 7.6 Training-loop consumption

Executed by `/informed-operator`: enumerate the active residuals for
the current curriculum phase (Warmup → Refine → Polish), sample each
per its policy, evaluate forward + projection, and run same-pass
fixed-point iteration at the DAG layer barrier for the
L3↔non-equilibrium cycle. Aggregation across `ResidualKey`s lives
entirely in `/informed-operator`, not in this factory.

## 7.7 Dressing certificates

The `OneShotCert` and `IterativeResult` records (Layer 1.25 and Layer
1.75 per `arch-08-bo-levels`) survive as **schemas attached to dressed
`MethodInvoke` nodes**, no longer as a separate per-generator field:

```
record OneShotCert {
  scheme            : G0W0 | SCP-perturbative | LO-TO-NA-correction
                    | Born-charge | epsilon-infinity | electronic-susceptibility
  inputs-hash       : ContentAddress
  parameters        : Map<Symbol, Value>          -- k-mesh, cutoff, …
  output            : DressedQuantity
  closure-residual  : Map<ResidualKey, Scalar>    -- one entry per (axis tuple)
                                                  --   the cert verifies; granular
                                                  --   like every other residual
                                                  --   emission (arch-11-residuals)
  cost-tier         : T1 | T2
}

record IterationSnapshot {                        -- one element of trajectory
  iter              : Nat
  residual          : Map<ResidualKey, Scalar>    -- per-key closure residual
  energy            : Scalar                      -- functional value at this iter
  witness           : Optional<Witness>           -- non-null iff divergent
  params            : Map<Symbol, Value>          -- mixing factor, broadening, …
}

record IterativeResult {                          -- Layer 1.75 (V2-deferred)
  scheme            : scGW | SSCHA-stochastic | TDEP | BSE-iterated
                    | DMFT | polaron-self-consistent
  inputs-hash       : ContentAddress
  parameters        : Map<Symbol, Value>          -- mixing, broadening, max-iter
  trajectory        : List<IterationSnapshot>
  converged?        : Bool
  divergence-witness: Optional<Witness>           -- non-null iff not converged
  final             : DressedQuantity
  cost-tier         : T3
}
```

V1 ships Layer 1.25 wired and Layer 1.75 as type/cert scaffolding only,
with `not-implemented-in-V1` stubs that fail loud.

## 7.8 Cadence policy (cost-tier → training cadence)

`sampling-policy` (§7.1) chooses *which* samples; the **cadence policy** chooses
*how often* each generator is evaluated, binding the cost tier to the training loop
so the expensive tiers never run per sample:

| Tier | Cost | Cadence |
|---|---|---|
| T0 | ≤10 µs closed-form | **every SGD step** (per-sample, backprop-native) |
| T1 | ≤10 ms small-LA / 1-D quadrature | **RAD-subsampled** (per-batch stochastic importance) |
| T2 | ≤10 s BZ / mesh integral | **per-epoch cached** (offline reference cache per composition + `(T,P,q)` query) — e.g. `NEGF-transmission` (row 80: one linear solve per energy) |
| T3 | ≤10 min iterative / PDE | **on-demand / calibration-only**, with a cheap T0/T1 proxy during training — e.g. `reference-phase-energy-cache` (row 87) |

Only the T0/T1 core runs on the per-sample hot path (the µs–ms class of
`arch-07-pipeline §7.6`); T2 is on-request per-epoch; T3 is reference / calibration
side. This is the policy that makes the always-cheap claim honest about *runtime
cadence*, not just per-op cost.


<a id="impl-10-build-sequence"></a>

# Build sequence

Each phase produces a verifiable artifact. The implementation-language decision is
resolved (`arch-18-open-decisions`, Closed decisions;
`physics/research/implementation-language.md`): a **Haskell** compiler-host for
Stages 1–4 + the substrate, emitting a **Julia** Stage-5 runtime, with **GAP** and
**Lean 4** offline.

| Phase | Scope | Artifact |
|---|---|---|
| 0 | Repository scaffold: the directory tree, orientation docs, per-directory READMEs | Empty skeleton matching the architecture |
| 1 | **Tier-1 numeric substrate** (`core`): coefficient/derivative layout, autodiff engine, staged code generation, tensor algebra, mesh integration | `core` implemented + tested against analytic references |
| 2 | **Tier-2 physical primitives** (`shared`): pair-sum with PBC, electrostatics (Ewald), kinetic density, density-from-orbitals, Hellmann–Feynman forces, DFT stress | Physical-primitive library, tested at analytic limits |
| 3 | **Input concepts** (`inputs`): typed constructors + readers for PeriodicityStructure, SiteDecoration, Environment | Round-trip-preserving system descriptions |
| 4 | **Unified state** (`state`): the 7-tuple container; per-level components (L1–L4); enumerate/serialize/hash | State encoding complete |
| 5 | **Methods vocabulary** (`methods`): the 12 methods + sub-method dispatch | Computational vocabulary, tested per method |
| 6 | **Templates** (`abstract-properties`): the 20 templates as typed factories | Template machinery, tested with multiple argument tuples |
| 7 | **Formula registry** (`formulas`): the 132 formulas with typed signatures + citations; the manifest; **applicability-decidability gate** (every classifier first-order decidable on typeclass tags; non-decidable entries rejected — `impl-04-formulas`) | Closed registry; algebraic combinations no longer hand-waved |
| 8 | **GENERIC operators** (`generic`): L sub-brackets, M sub-brackets, assembly; **instantiate active `CouplingSpec` via Stage-2.5 invariant synthesis** (`arch-19-coupling-structure`) and attach generated `InvariantTerm`s to the `E_coupling`, `L_assembly`, `M_assembly` aggregators | Antisymmetry of L, PSD of M, Jacobi, degeneracy verified |
| 9 | **Canonicals** (`canonicals`): E[x] and S[x] assembled across levels | Dimensional + analytic-limit checks pass |
| 10 | **Observables** (`observables`): the target observables as compositions (§6), in 11 bundles | Library callable for any observable; reference-crystal checks |
| 11 | **Residuals + Cert** (`residuals`, `cert`): 19 named categories, ResidualGenerator factory, 10 obligations, schema/freeze/oracle | Self-certifying outputs; usable residual contract |
| 12 | **Dynamics + integration validation** (`dynamics`): assemble the unified RHS; validate on harmonic oscillator, two-level Rabi, ideal-gas relaxation | Unified dynamics callable; RHS handed to any integrator |
| 13 | **API seal + pino-bridge**: the single typed seal; `Validate` and `Import` (`arch-16-pino-bridge`); worked examples; end-to-end demo | Shippable; downstream libraries can build against it |

Recommended start order: substrate (Phases 1–7) before any concrete observable,
then GENERIC/canonicals/observables (Phases 8–10), then residuals/cert/dynamics
(Phases 11–12), then the seal (Phase 13).

---
