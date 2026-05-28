# `n-Op` Research Brief — Unified Architecture for a Physically-Informed Neural Operator over Crystals

## 0. Purpose of this document

This document is an idea dump. It is written for an independent researcher who has not been part of the design dialogue and who is being asked to read everything we have decided, considered, rejected, deferred, or left open — and then to formulate **one unified architecture** that takes the system from inputs to residuals end-to-end.

It does not push a single design. Where multiple named approaches exist, all are presented with both the case for and the critique against. Where a question is open, it is flagged open. Where something has been ruled out of scope, the boundary is stated explicitly.

Reading discipline: any named term is defined at first use. Comprehensiveness is the goal; brevity is not.

---

## 1. The problem

`n-Op` ("neural operator") is a project to train a **physically-informed neural operator (PINO)** that predicts the time evolution of the state of a crystalline material under operating conditions. The downstream target is the design of **durable high-performance ultra-wide-bandgap (UWBG) semiconductor chips for harsh environments** — chips that must function inside, for instance, a jet turbine: high temperature (>500 °C), thermal cycling, mechanical vibration, high field, high current density, possibly radiation.

The user-stated minimum viable demonstration (MVP) is to model **diamond** with three target capabilities:

1. Crystal structure prediction (and prediction of structures of diamond-compatible heterostructures).
2. Electron-cloud diffusion through the lattice.
3. Heat diffusion through the lattice.

The discipline imposed on the MVP is **"as much closed-form / computationally feasible expressions as possible"** and **"hyper domain-specific purpose-built tools."** The MVP is diamond-centric and the broader material scope includes anything that can form a semiconductor with diamond: c-BN, AlN, GaN, β-Ga₂O₃, AlGaN; refractory contact metals (W, Mo, Pt, Ti, Ni, Ta, TiN, WSi₂); substrates (SiC, Si, sapphire); gate dielectrics (Al₂O₃, HfO₂, AlN-as-dielectric).

The user has stated that **the comprehensiveness of the spec is the point**, even as implementation is diamond-first. That distinction — comprehensive spec, diamond-first build — runs through everything below.

---

## 2. The library landscape

`n-Op` is partitioned into three sibling libraries.

- **`/physics`** — a substrate-agnostic reference oracle library. It encodes the laws of the system: state structure, dynamics, observable definitions, residual definitions, and certification obligations. It does **not** hold time-varying state values, train neural networks, integrate trajectories, or wrap external DFT codes at runtime. This is the library this document is primarily about.
- **`/informed-operator`** — the PINO itself. It consumes `/physics` and learns the time-evolution operator. Out of scope for the current design pass.
- **`/interface`** — the user-facing surface. Out of scope for the current design pass.

The user is currently building the **lattice-math foundation** inside `/physics/library/lattice-math/`. Nothing else has been implemented.

`/physics` is a single library; engineering aspects (defects, dopants, surfaces, interfaces, operating-condition effects) live **inside** `/physics`, not in a separate `/engineering` library.

---

## 3. Inputs (the "descriptor" side)

Three physically orthogonal inputs feed `/physics`:

1. **`PeriodicityStructure`** — the Bravais lattice, space group, cell vectors `h`. The geometry of repetition.
2. **`SiteDecoration`** — which species sit at which Wyckoff positions; orbital basis on each site.
3. **`Environment`** — temperature, pressure, applied electric and magnetic fields, chemical potentials, charge carrier injection conditions.

These three together fully specify "what crystal, in what conditions." Earlier candidates `Reference` and `Property` were considered as top-level inputs and demoted: `Reference` belongs in the cert layer (Section 13), and `Property` is an output, not an input.

---

## 4. The unified state

The instantaneous state of the system is

```
x(t) = (h, R_I, P_I, Π_h, Z_I, γ̂, A)
```

where:

- `h` — cell vectors (3 × 3 real).
- `R_I` — ion positions (3N real).
- `P_I` — ion momenta (3N real).
- `Π_h` — cell momentum (3 × 3 real, Parrinello–Rahman).
- `Z_I` — species labels (N discrete, immutable).
- `γ̂` — the one-body electronic density matrix, possibly Pauli-spinor extended for magnetism; defined on `(r, r'; t)`.
- `A` — the external electromagnetic vector potential `A(r, t)`.

Other quantities a working physicist might list — phonon distributions `n_{q,s}`, carrier distributions `f_n(k, r)`, surface coverages `θ_i`, composition vectors — are **emergent**, not irreducible. They are coarse-grainings, semiclassical limits, or projections of `x(t)`.

A critical reframing established midway through the design: `x(t)` is a **type** that the PINO's predictions instantiate at each time step. `/physics` does not hold values of `x(t)`; it defines what `x(t)` is, what laws govern its evolution, and how to evaluate whether a candidate `x(t)` from the PINO satisfies those laws.

---

## 5. Dynamics (GENERIC)

The chosen framework for dynamics is **GENERIC** (General Equation for the Non-Equilibrium Reversible–Irreversible Coupling). It writes time evolution as

```
dx/dt = L · δE/δx + M · δS/δx
```

with the following structure:

- `E[x]` — total energy functional.
- `S[x]` — total entropy functional.
- `L` — Poisson operator: antisymmetric; reversible dynamics.
- `M` — friction operator: symmetric, positive semidefinite (PSD); irreversible dynamics.
- Degeneracy conditions: `L · δS/δx = 0` (reversible part conserves entropy) and `M · δE/δx = 0` (dissipative part conserves energy).

Each of the nine traditional regimes of multi-physics — structural, mechanical, thermal, electronic, magnetic, optical, transport, thermodynamic, chemical/surface — is recovered as an **extraction** of this single equation. Static observables are equilibrium readouts (fixed points of the GENERIC flow); time-evolving observables are trajectory readouts.

The PINO's primary loss term is the **EOM-violation residual** `‖dx/dt − (L δE/δx + M δS/δx)‖²`. Additional residual categories are listed in Section 12.

---

## 6. The 4-level Born–Oppenheimer hierarchy

Within `x(t)`, the components separate naturally into four levels whose dependencies flow strictly upward:

- **L1 — Quantum electronic substrate.** Operates on `γ̂(r, r'; t)` at fixed `(R, h)`. Regimes: electronic, optical, magnetic. Math: KS / TDKS / TDCSDFT, Hohenberg–Kohn, Runge–Gross, Liouville–von Neumann.
- **L2 — Born–Oppenheimer surface.** Operates on `E_BO(R, h) = min_γ̂ E[γ̂; R, h]`. Regimes: structural, mechanical. Math: Hellmann–Feynman, strain expansion, Parrinello–Rahman dynamics on `(R, P, h, Π_h)`.
- **L3 — Equilibrium statistics on the BO surface.** Bose–Einstein, Fermi–Dirac, Maxwell–Boltzmann distributions over L1 and L2 spectra. Regimes: thermal, thermodynamic. Math: partition functions, free energies, quasi-harmonic approximation, convex hull.
- **L4 — Non-equilibrium kinetics.** Distributions over phase space; full GENERIC `L + M`. Regimes: transport, chemical/surface. Math: Boltzmann transport, Kubo / Green–Kubo, master equation, Marcus theory, transition state theory, nudged elastic band.

Each level uses lower levels as inputs but introduces its own irreducible state. This hierarchy structures `state/`, `canonicals/`, `generic/`, and `dynamics/` inside `/physics/library/`; it does not by itself organize observables (see Section 7).

---

## 7. The three-layer architecture

A separate and complementary partition organizes the library by **what kind of work each piece does**.

- **Layer 1 — Synthesis pipeline.** Takes `(G, q, W, k)` — space group, momentum point, Wyckoff orbit, orbital basis — and produces a `CrystalSystem` via six stages: Lattice Construction → Fiber Construction → Symmetry-Constrained Hamiltonian Family → Topological Phase Selection → Assembly → Verification. This layer is well-specified and polynomial-time.
- **Layer 2 — Property machinery.** Twelve computational methods composed into eighteen abstract templates instantiated into eighty-seven named formulas, producing observables in eleven typed bundles. Detailed in Sections 8–11.
- **Layer 3 — PINO.** Consumes `/physics`'s definitions, predicts state trajectories, and is trained against residuals. Lives in `/informed-operator`.

The hierarchy (Section 6) and the three-layer architecture (this section) are orthogonal views of the same library. The hierarchy partitions *what state component lives where*; the three-layer view partitions *what computational role each piece plays*.

---

## 8. The closed registries (Layer 2 content)

The Layer 2 property machinery is built as a small number of closed registries that compose.

### 8.1 Twelve computational methods

Closed vocabulary; instances are programs in this vocabulary:

`state-readout`, `algebraic-combination`, `functional-differentiation`, `variational-minimization`, `spectral-decomposition`, `spectral-aggregation`, `linear-response`, `path-search`, `convex-optimization`, `kinetic-evolution`, `statistical-sampling`, `symmetry-projection`.

### 8.2 Eighteen abstract-property templates

Parametric method-chain templates. One template, many instances. Examples:

`SecondDerivativeOf(F, x₀, coord)` → ElasticConstants, ForceConstants, PolarSusceptibility.
`SpectralAggregateOf(Op, aggregator)` → DOS, PhononDOS, HeatCapacity.
`ResponseOfTo(component, perturbation)` → DielectricFunction, Conductivity(ω).
`PathStationaryOf(F, initial, final)` → MigrationBarrier, ReactionPathway.
`KineticEvolutionOf(dist, collision, grad)` → ElectronicConductivity, ThermalConductivity, IonicDiffusivity.
`AlgebraicOf({inputs}, formula)` → FormationEnergy, SurfaceEnergy.
`ClassifyOf(object, classifier)` → SpaceGroup, WyckoffOrbit.
`ComparisonOf(target, reference, metric)` → DefectComparison, SurfaceComparison.
`SpectrumOf(operator, parametric-domain)` → BandStructure, PhononDispersion.
`RadiativeEmissionOf(excited-state, optical-coupling)` → Photoluminescence.
`MicrokineticSteadyStateOf(rate-network)` → CatalyticActivity.
`StatisticalAggregateOf(distribution, weight)` → Cv(T), F(T).
Plus: `StateReadoutOf`, `BulkBoundaryCorrespondenceOf` (added to fill cert obligation-7), `SymmetryAdaptedHamiltonianOf` (added if topology is integrated; see Section 16).

### 8.3 Eighty-seven named formulas

Closed registry of typed, fully-parameterized algebraic formulas. Examples: `slab-arithmetic`, `arrhenius`, `vineyard-prefactor`, `kramers-kronig-hilbert`, `chen-hardness`, `voigt-reuss-hill-averages`, `christoffel-eigenvalue`, `bose-einstein-cv`, `fermi-dirac-helmholtz`, `defect-formation-energy`, `lorenz-wiedemann-franz`, `van-roosbroeck-shockley`, `htst-rate`, plus UWBG-specific additions (Fröhlich coupling, polar-optical-phonon scattering, Shockley–Read–Hall recombination, Chynoweth impact ionization, Zener tunneling, Caughey–Thomas mobility, Schottky–Mott + Bardeen correction, Fowler–Nordheim tunneling, Makov–Payne / Freysoldt / Kumagai–Oba charged-defect corrections, Redlich–Kister excess-free-energy basis, and others).

Each formula has a typed signature, a cost tier `T0..T3`, a differentiability tag `D0..D4`, and an applicability classifier (Section 14).

### 8.4 Eleven observable bundles

Organized by *data shape*, not by physical regime: `electronic-structure`, `phonon`, `transport`, `defect-resolved`, `surface-resolved`, `interface-resolved`, `mechanics`, `thermodynamics`, `non-equilibrium-operating`, `structural-validity`, `degradation`.

---

## 9. The central object — γ̂ — and its representation

The one-body density matrix `γ̂` is the most demanding object in the architecture: it is a single logical entity with multiple inequivalent encodings, different operations are cheap on different encodings, and it must support efficient time evolution. Five named **framings** were explored as standalone candidates and then synthesized.

### 9.1 The five framings

- **Framing A — typed term algebra with rewrite rules.** `γ̂` is a term in a grammar; encodings are productions; conversions are rewrites under equational laws; operations are visitors over the term; invariants are type-level tags; evolution is a fold.
- **Framing B — codata / coalgebraic.** `γ̂` is opaque; only destructors are exposed (apply, trace, density, ...); encodings are invisible to callers; invariants are destructor laws; evolution is an F-coalgebra.
- **Framing C — e-graph with cost-driven equality saturation.** `γ̂` is an e-class containing all known equivalent representations cross-linked; per-query extraction selects the cheapest representation.
- **Framing D — tensor network with cost-aware contraction.** `γ̂` is a node with node-type ∈ {Dense, Sparse, LowRank, BlockDiag}; operations are contractions; a cost-aware optimizer chooses the contraction order and the encoding of the output.
- **Framing E — multi-representation pullback with consistency invariant.** `γ̂` is a *bundle* of synchronized encodings (e.g. real-space + reciprocal-space) maintained together; the consistency invariant is part of the type or carried as a witness; categorically, a pullback of decoding morphisms.

### 9.2 The layered hybrid (current working design)

After ten pairwise mesh analyses (one per `{A,B,C,D,E} choose 2`), no single framing was judged sufficient alone. The synthesis is a **layered hybrid**:

- **Interface layer:** Framing B — codata destructors. What `/physics` exposes to callers.
- **Staging / expand layer:** Framing A — typed term algebra. Compile-time symbolic composition; rewrites stage per-encoding code at expansion time.
- **Planner (sixth component, named by mesh analysis):** consumes workload profiles + A's structure, produces bundle specs for E.
- **Optional optimization layer:** Framing C — e-graph for cross-cutting encoding selection at staging time. May be omitted in V1.
- **Runtime representation:** Framing E — pullback bundle of maintained encodings. Used for `γ̂` specifically; not used for objects of higher tensor rank (BSE four-index, BTE collision matrices) where the storage multiplier is prohibitive.
- **Runtime substrate:** Framing D — tensor network with cost-aware contraction.

The mesh-synthesis pass surfaced corrections to the original linear-stack reading: there is a **read path** (`B → D` direct, used by apply / trace / density / eigendecomposition — the bulk of γ̂ traffic) and a **write path** (`B → A → Planner → C? → E → D`, used by construction, self-consistent iteration, time stepping). Most γ̂ traffic skips A/C/E entirely. The "consistency witness" between maintained encodings becomes a first-class destructor on B. Self-consistency (when `Ĥ[γ̂]` depends on `γ̂` itself) is owned by B's coalgebraic fixed point.

### 9.3 Open architectural amendment — basis × form factoring

R1 (low-rank), R2 (momentum-block-diagonal), R3 (sparse-in-localized-basis) conflate two orthogonal axes. Cleaner factoring:

```
Encoding = (basis ∈ {Real, Reciprocal, Wannier, NaturalOrbital, ...},
            form  ∈ {Dense, Sparse, BlockDiag, LowRank, ...})
```

Recommended but not yet committed.

---

## 10. The synthesis pipeline (Layer 1, in detail)

Starting from `(G, q, W, k)`:

1. **Lattice construction.** Build the Bravais lattice and the symmetry-adapted basis from `G` and `W`.
2. **Fiber construction.** Construct the orbital fiber over each Wyckoff position from the orbital basis.
3. **Symmetry-constrained Hamiltonian family.** Solve the linear system imposed by `G` to enumerate the family of symmetry-compatible Bloch Hamiltonians.
4. **Topological phase selection.** Use symmetry indicators to filter or label members of the family by their topological class.
5. **Assembly.** Assemble the chosen Hamiltonian.
6. **Verification.** Run cert obligations against the assembled object.

This pipeline is polynomial-time and well-specified. It corresponds to the work of MagneticTB, Crystalline.jl, IrRep, and the Bilbao Crystallographic Server tables.

---

## 11. The "missing-formula" question and the patching analyses

A meta-audit identified several apparent gaps in the closed registries — LO/TO non-analytic correction, charged-defect corrections (Makov–Payne / Freysoldt / Kumagai–Oba), internal-strain coupling Λ, self-consistent / temperature-dependent phonons (SCP / SSCHA / TDEP), Redlich–Kister CALPHAD basis, Wegscheider cycle-basis reduction. Three named **paths** for closing these were considered.

- **Path γ (flat).** Add six formulas to the registry. Simplest; loses the chance to find a unifying pattern.
- **Path γ' (substrate-extension).** Most "missing formulas" are actually thin Layer 1 surfaces. Enrich Layer 1 — add a long-range Coulomb sub-stage with linear response producing `Z*`, `ε∞`, `χ^∞`; add an anharmonic-basis extension — and most "missing formulas" become derived properties exposed at the Stage-3 / Stage-5 handoff. Net change: one method, one template, plus Layer 1 extensions; not six independent formulas.
- **Path γ'' (intermediate).** Some collapse, some don't.

### 11.1 The γ' validator (Validator-1)

A research subagent was dispatched to validate γ'. It returned three substantive corrections:

- LO/TO is **not** automatic; the Pick–Cochran–Martin / Gonze–Lee analytic correction is a real formula entry, plus the q → 0 directional limit is a cert obligation. Net: +1 formula + 3 Layer 1 primitives.
- The three charged-defect schemes are **not** the same method with different coefficients. Freysoldt uses planar-averaged potentials with alignment; Kumagai–Oba uses atomic-site averaging; Makov–Payne is the original asymptotic series. They should be modeled as a strategy-pattern method `charged-defect-correction(scheme: {MP, FNV, KO}, …)` plus a separate Madelung Layer 1 primitive — **not** merged.
- Redlich–Kister is **not** an instance of `ClusterExpansion`. Cluster expansion is discrete T = 0 lattice energy; Redlich–Kister is continuous composition-dependent finite-T excess Gibbs energy. Connected only via thermodynamic integration. Should be registered as a separate formula.

Validator-1 also surfaced a deeper architectural proposal — **Layer 1.5: a renormalization layer** between Layer 1 (bare substrate) and Layer 2 (property machinery). The claim: SCPH / SSCHA, GW self-energy, BSE kernel, DMFT, and polaron renormalization all share a fixed-point structure `x = F(x; T, params)` with a convergence criterion. One method primitive would serve all five. Layer 2 receives "dressed" Layer 1 output. One uniform cert: "renormalization converged or explicitly declared divergent." Additionally, a topological-invariant Layer 1 primitive (Fu–Kane / Wilson loop / symmetry-indicators) was proposed to convert cert obligation-7 (bulk-edge correspondence) from a stub to a derived assertion.

### 11.2 The Layer-1.5 validator (Validator-2)

A second subagent was dispatched specifically to evaluate Layer 1.5 against the diamond MVP and the closed-form discipline. Verdict: **reject Layer 1.5 as proposed; accept "Alternative D" — a two-tier split**. Critique points:

- The "one fixed-point primitive serves all five" claim is false at the level of useful code reuse. Components share only a 12-line loop skeleton. Carriers, mixing schemes, convergence norms, and divergence witnesses are incompatible: SCPH operates on a real-symmetric dynamical matrix with Broyden mixing and imaginary-eigenvalue divergence witness; scGW operates on complex frequency-dependent self-energies with spectral DIIS and Kramers–Kronig / sum-rule witnesses; DMFT operates on local self-energy plus hybridization, needs metallic-and-insulating seed bracketing near the Mott transition, and its divergence witness is non-causal Σ. BSE is one-shot in standard practice and does not belong in a fixed-point family. The polaron has a closed-form Feynman variational treatment; self-consistent Migdal is iterative but applies in strong-coupling regimes diamond does not enter.
- The diamond MVP needs only 2 of 5 components: G₀W₀ (essential — Kohn–Sham underestimates the diamond gap by ~30 %; G₀W₀ corrects to 5.5 eV vs measured 5.47 eV) and first-order SCP (marginal at 773 K, growing at 1500 K+). The other three are non-diamond scope.
- Closed-form alternatives exist for the diamond-relevant subset: SCPH → first-order SCP; GW → G₀W₀; BSE → one-shot diagonalization; polaron → Feynman variational.
- The topological-invariant primitive is one-shot closed-form (Wilson loop / Fu–Kane) and does not belong in a *renormalization* layer.
- Layer 1 spec changes are real: G₀W₀ needs unoccupied manifolds + wavefunction representations; SCP needs anharmonic quartics; (V2) DMFT needs Wannier projections. Validator-1's "Layer 1 unaffected" framing was wrong.

### 11.3 Alternative D

```
Layer 1     Bare substrate (current Layer 1, with the substrate extensions above)
Layer 1.25  One-shot closed-form dressing — pure functions, no iteration
              G₀W₀, first-order SCP, BSE-one-shot, Feynman variational polaron,
              topological-invariant primitive (Wilson loop / Fu–Kane / symmetry indicators)
              cert vocabulary: OneShotCert = WellPosed | IllPosed
Layer 1.75  Iterative fixed-point dressing — DEFERRED to V2 in code, SPECIFIED in V1 docs
              full SCPH iteration, scGW, DMFT, BSE iterative variants, self-consistent Migdal
              cert vocabulary: IterativeResult = ConvergedAt | DivergedAt | Stale
              each component gets a bespoke combinator (NOT a shared primitive)
Layer 2     Property machinery (unchanged interface; dressed carriers type-substitutable for bare)
Layer 3     PINO
```

Diamond MVP runs entirely against Layer 1.25, preserving the closed-form discipline. Comprehensiveness is preserved via the V1 spec for Layer 1.75 even though no V1 code implements it.

A separate **registry-modified-γ'** drops out:

- LO/TO: +1 formula + 3 Layer 1 primitives.
- Charged-defect: strategy-pattern method + separate Madelung primitive (NOT merged).
- Redlich–Kister: separate formula (NOT a ClusterExpansion instance).
- SCP / SSCHA: parameterized template `SelfConsistentRenormalizationOf{scheme}` with V1 implementing only `SCP-first-order`.
- Templates 18 → 20; formulas net stable around 87–89; plus the topological-invariant primitive in Layer 1.25.

---

## 12. Residual categories and the residual-generator factory

Residuals are the physics-informed loss terms the PINO trains against. There are **seven** categories:

1. **EOM-violation** (primary): `‖dx/dt − (L δE/δx + M δS/δx)‖²`.
2. **Degeneracy:** `‖L δS/δx‖² + ‖M δE/δx‖²`.
3. **Conservation:** conserved quantities preserved.
4. **Positivity:** `M ⪰ 0`, `|S_i| = 1`, `f ∈ [0, 1]`, `ρ ≥ 0`.
5. **Algebraic identities:** Maxwell, Einstein, detailed balance, Kramers–Kronig, sum rules.
6. **Structural-validity:** Born stability, dynamical stability, formability heuristics.
7. **Thermodynamic-consistency:** hull-distance, chemical-potential consistency.

The architecture is **not** just five categories listed; it is a **residual-generator factory**. Every formula in the closed registry registers itself with the factory at load time with: typed signature, cost tier `T0..T3`, differentiability tag `D0..D4`, applicability classifier, source-tag (e.g. `{bare | dressed(scheme, cert, T)}`), and an adjoint declaration. The factory generates a `ResidualGenerator` record per formula. The PINO training loop reads these records and dispatches per-sample.

A registration-time **adjoint-existence gate** rejects formulas with `D ≤ 1` if no adjoint handler is provided.

---

## 13. Cert — ten obligations

Cert is first-class. Ten obligations:

1. Symmetry equivariance.
2. Bounds (physical constraints).
3. Analytic limits (limits where closed-form answers exist).
4. Reference-battery — machine-readable reference data (Section 13.1).
5. Conservation laws.
6. GENERIC degeneracy.
7. Bulk-edge correspondence (substantive content depends on topological-invariant primitive; see Sections 11.2 and 16).
8. Reference-battery-versioned (versioning discipline on obligation 4).
9. Surrogate-net validity (for `D4` surrogate formulas).
10. Adjoint-existence at registration (for residual generation).

### 13.1 The reference battery

A machine-readable archive at `physics/library/cert/reference-data/` holding typed records with provenance (DOI / source), units, uncertainty bands, semantic version, and source class (`experimental | dft-pbe | dft-hse | gw | dft-d3 | …`). CSV in V1 for language-agnostic auditability. Cert obligation-8 reads it, looks up matching rows by `(Property, Material, Environment)`, computes residual `|predicted − reference| / σ_reference`, and trips at > 3σ with a numerical witness carrying the row's provenance.

---

## 14. Applicability classifiers

Every property, observable, and residual carries an **applicability classifier** — a typed predicate `applicability : (Crystal, Environment) → Bool`. The PINO loss masks out non-applicable properties per-sample.

Examples: band gap is applicable iff `is-insulator-or-semiconductor(Crystal)`; Schottky barrier iff `has-metal-semiconductor-interface(Crystal)`; superconducting `T_c` iff `is-superconductor(Crystal)`; carbide-formation rate at interface iff `interface-includes-carbide-former(Crystal)` (Pt/diamond does not; Ti/diamond does).

This is what makes the architecture compositional across crystal types. The same `/physics` interface accepts diamond, GaN, AlN, c-BN, refractory contact metals — each property's classifier handles whether it is a meaningful question for the specific crystal in question.

Open: classifier composition under perturbation (phase transition closing a gap → does the classifier evaluate against the current or initial state?), soft classifiers `(Crystal, Env) → [0, 1]`, composite predicates.

---

## 15. Two-tier accuracy and multi-source training

### 15.1 Two-tier accuracy

Per the user's explicit clarification: `/physics` must support **two levels of fidelity per observable**:

- **Cheap-compute path.** For generating approximate training labels at scale. Accuracy ~20 % acceptable. Used in initial training epochs to reduce the PINO's search space.
- **Faithful-residual path.** For physics-informed loss. Must be physically faithful — when the PINO predicts a wrong state, the residual must reflect the wrongness accurately. Used throughout training.

These are **not** the same code path. They are independently designed.

### 15.2 Multi-source training

The PINO trains on four sources simultaneously: (a) cheap data generated by the cheap-compute path; (b) VASP ground-truth from external high-fidelity DFT; (c) experimental measurements; (d) physics residuals from the faithful-residual path.

Methodology (from research stream S5): four-phase curriculum (warmup 0–10 %, refine 10–60 %, calibrate 60–90 %, polish 90–100 %); GradNorm outer balancing + NTK-initialized inner per-formula weights; Huber loss with per-observable σ for experimental data; RAD (residual-adaptive distribution) sampling for `T1` residuals; coverage masks driven by applicability classifiers.

A non-trivial discipline issue: bare-KS and G₀W₀ band-structure residuals disagree by ~30 % on diamond. They **cannot be averaged**. The residual-generator's source-tag `{bare | dressed(scheme, cert, T)}` exposes which is which, and the curriculum must specify per-phase bare-vs-dressed weighting.

### 15.3 Three pino-bridge exports

`/physics/library/pino-bridge/` exposes three named interfaces:

- **Generate** — `/physics` → `/informed-operator` training labels. Cheap-compute path.
- **Validate** — `/informed-operator` predictions → `/physics` → residuals. Faithful-residual path.
- **Import** — external VASP outputs and experimental measurements → `/physics` as cert evidence and extra labels.

---

## 16. The topology integration question (open thread)

A separate research document on crystalline topological classification (the X_BS / Topological Quantum Chemistry framework — Po, Vishwanath, Watanabe; Bradlyn et al.) was reviewed and identified as **directly load-bearing** for several pieces that are vague or flagged-as-gap in the architecture above.

Specifically: (G, q) → finite abelian group X_BS = {BS}/{AI} via Smith Normal Form; 117 of 230 space groups have non-trivial X_BS spinful + TRS; max |X_BS| = 72 at SG 175 and 191. Algorithmic in polynomial time. Resolves the "AZ symmetry classes (Cartan tenfold-way)" gap. The Khalaf–Po–Vishwanath–Watanabe results give per-indicator-factor → surface-state-count rules, converting cert obligation-7 (bulk-edge correspondence) from a stub to a derived assertion. Tool ecosystem (Crystalline.jl, MagneticTB, IrRep, Z2Pack, WannierTools, Bilbao tables) creates concrete language-decision pressure: Julia or Python clearly viable; Mathematica only viable as a partial-precompute supplement.

If integrated: adds `SymmetryAdaptedHamiltonianOf` as a 19th (or 20th if Alternative D's `SelfConsistentRenormalizationOf` is also added) template; adds a topological-invariant Layer 1 / Layer 1.25 primitive; substantively closes cert obligation-7; folds `topology-resolved` into the existing `electronic-structure` bundle (rather than adding a 12th bundle).

**Status:** flagged as a separate research session. **Not yet integrated** into the architecture above. The Layer 1.25 placement of the topological-invariant primitive (per Alternative D) may already do most of the work; whether a deeper integration session is needed remains open.

A flagged but un-pursued cross-pollination opportunity: the document explicitly notes the absence of work framing topological-material synthesis through dependent type theory / HoTT. A type-theoretic framing — `(G, q, d, target-X_BS)` as a type, Hamiltonian as proof of inhabitation — is a possible novel contribution. Not in V1 scope.

---

## 17. A candidate isomorphism — free algebra of typed effects

A recent reframing (still under discussion) observes that several apparently independent organizing principles in the architecture may all be the same structure wearing different hats:

- The layered hybrid for `γ̂` (B / A / Planner / C? / E / D).
- The two-tier accuracy discipline (cheap vs faithful).
- The three pino-bridge exports (Generate / Validate / Import).
- The Layer 1.25 / Layer 1.75 split (closed-form vs iterative dressing).
- The cert obligations as registration-time gates.
- The 5-layer stack (1 / 1.25 / 1.75 / 2 / 3).
- The read-path / write-path distinction discovered in the mesh analysis.

Candidate isomorphism: each is an instance of a **free algebra of typed effects with multiple handler stacks**. Effect signatures (e.g. `OneShotDress(scheme, sys) → DressedSystem`, `ComputeObservable(template, args, sys) → Observable`) are declared once; multiple handlers interpret the same effect (cheap handler, faithful handler, import handler, oracle handler). The 5-layer stack becomes an organizational view of effect signatures, not a structural commitment about runtime. "Layer 1.75 specified but deferred" becomes "effect signature defined, no handler registered for V1." Source-tag on residuals becomes the handler-stack identifier. Cert obligations become handler-registration laws. Applicability classifiers become dispatch guards.

Status: **proposal, not adopted.** Reasonable on its face; needs at least one independent reading to judge whether it is a real structural observation or a renaming. If real, the patching pass simplifies considerably (one section on "effect signatures + handler discipline" instead of separate Layer 1.25 and Layer 1.75 sections); if not, the multi-layer view stands.

---

## 18. Out-of-scope declarations

Stated and held:

- **Strongly correlated electron systems** (frustrated Wigner crystals, spin liquids, Mott physics) are out of scope for the V1 L1 substrate. `γ̂` is mean-field-by-construction. Bringing strong correlation in-scope would require an alternative L1 carrier (tensor-network state, selected-CI, DMFT/DMET embedding, or neural quantum state). Justification: UWBG materials are large-gap and far from Mott physics; correlation in deep-level traps is bounded and handled semi-empirically.
- **True renormalization-group flow** (symmetry-class transitions under energy scale) is out of scope. Could be added as a new layer if needed.
- **Inverse design / minimal-model search** (Stage 4 of the topology pipeline) is documented as an open problem; if topology is integrated, it lives in `/informed-operator` as a PINO head, not as a `/physics` primitive.
- **Fragile topology** is a real scope limit if topology is integrated; under standard X_BS the gap is documented and the case is excluded.
- **Engineering / process / device modeling** (CVD growth simulation, lithography, packaging) is downstream of all three libraries and out of scope.

---

## 19. Outstanding decisions

These are flagged for the user to make; none have been resolved.

1. **Implementation language.** Top candidates: Python + JAX (large ML ecosystem, autodiff-first), Julia (Crystalline.jl, Zygote / Enzyme.jl, scientific-computing-first), Racket (closest to the source library style; weakest ML ecosystem). The topology tool ecosystem favors Julia or Python.
2. **ReferenceCache backend.** Default candidate: SQLite with SHA-pinned schema.
3. **Surrogate-net build vs adopt.** For `D4` surrogate formulas.
4. **PDE-mesh format + adjoint library.** For `KineticEvolutionOf` instances that need explicit mesh.
5. **Coverage-mask format.** Sparse from the start, or dense + compression?
6. **Curriculum schedule confirmation.** Defaults 0.10, 0.60, 0.90; per-source weights TBD.
7. **Active-learning loop placement.** Default candidate: lives in `/interface`, not `/physics`.

---

## 20. Open questions for the independent researcher

These are the load-bearing questions on which a unified architecture proposal would substantially depend.

1. **Is the free-algebra-of-effects view (Section 17) a real structural observation, or is it a rename?** A negative finding is informative — it would strengthen the case for keeping the multi-layer view explicit.
2. **Does the topology integration (Section 16) need its own deep research session, or does Alternative D's placement of the topological-invariant primitive in Layer 1.25 substantively close it?**
3. **In the layered γ̂ hybrid, is the basis × form factoring (Section 9.3) the right axis decomposition, or is there a cleaner one?** Specifically, should `(NaturalOrbital, LowRank)` and `(Wannier, Sparse)` be first-class encodings in V1?
4. **The two-tier accuracy discipline introduces two implementations per observable. Under what discipline are they kept in sync?** A naive answer is "the faithful path is the oracle that the cheap path is tested against." Are there sharper alternatives?
5. **Are seven residual categories the right count, or should some be merged / split?** In particular: thermodynamic-consistency vs structural-validity overlap on hull-distance.
6. **For Layer 1.75 (iterative dressing, V2 code, V1 spec): what is the minimum spec content that lets a V2 contributor implement scGW or DMFT without re-litigating the architecture?**
7. **What does the cert layer do when two equivalent compositions of the same observable disagree?** (E.g., Kubo σ vs BTE σ. The current answer is "trip a cert with both witnesses"; is that adequate?)
8. **Are there observables in the eleven bundles whose applicability classifier is not first-order-decidable from the descriptor inputs?** If so, those need either deferred classifiers or a stricter input vocabulary.

---

## 21. Repository layout (as it stands today)

```
n-Op/
├── IMPLEMENTATION-PLAN.md           (canonical, with §§19–26 amendment)
├── META-AUDIT.md
├── RESEARCH-BRIEF.md                (this file)
├── physics/
│   ├── library/
│   │   ├── lattice-math/            (user is actively building this)
│   │   ├── inputs/                  (PeriodicityStructure, SiteDecoration, Environment)
│   │   ├── state/                   (unified state type)
│   │   ├── canonicals/              (E[x], S[x])
│   │   ├── generic/                 (L, M)
│   │   ├── dynamics/                (total-evolution definition)
│   │   ├── methods/                 (12 computational primitives)
│   │   ├── abstract-properties/     (18 templates, to grow to 19–20)
│   │   ├── formulas/                (87 named formulas; registry-manifest.csv)
│   │   ├── observables/             (11 bundles)
│   │   ├── applicability/           (per-property classifiers)
│   │   ├── residuals/               (7 categories + factory)
│   │   ├── cert/                    (10 obligations + reference-data/)
│   │   ├── pino-bridge/             (Generate, Validate, Import)
│   │   └── interfaces/              (Scalar, FieldOnGrid, Tensor, Response)
│   └── research/                    (25 migrated research documents covering
│                                     S1–S7 streams, γ̂ framings A–E, mesh-pair
│                                     analyses AB–DE, group audits, applicability,
│                                     scoping log)
├── informed-operator/
│   └── design/                      (S5 residual-loss methodology)
└── interface/
```

No code has been written. No implementation language has been chosen. The `physics/research/` directory contains the full provenance of every design decision summarized above; this brief is a high-level synthesis, not a substitute.

---

End of brief.
