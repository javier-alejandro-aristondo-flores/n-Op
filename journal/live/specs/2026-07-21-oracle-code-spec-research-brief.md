# /physics Oracle — Code-Specification Research Brief

*2026-07-21 · standalone research brief (outside the atomic tree) · to be executed as a fan-out of independent research agents*

---

## 1. Goal

**Terminal deliverable.** Executing the research program defined in this brief produces **one document that fully *specifies*, but does not *implement*, the code of the `/physics` oracle.** "Fully specifies" means: every module, data structure, algorithm, numerical method, type signature, contract, and tolerance is pinned to the point that implementation is a mechanical act — a competent engineer could type it out with no further research and no open design questions.

**What the oracle is (why the spec matters).** The oracle is a compiler: it takes a material identity and emits an immutable, content-addressed *oracle-file* — a pure function that **scores** a complete candidate state against the laws of physics (keyed law-violation residuals + requested observables + optional cotangents + a certificate), and never solves, completes, or judges. It is the physics-informed loss term and the certifier for the program's end goal — **property-targeted crystal design** (desired properties in, structure out, produced by a learned proposer that the oracle disciplines). This brief specifies the **oracle**; the learned proposer and the driving loops are separate systems and are out of scope here (§2).

**How this brief is used.** The research program (§4) is decomposed into independent, individually-dispatchable **research units (R#)**. Each names its objective, its internal sources, the external research it requires (academic literature or engineering/tooling references, each consulted once), and a concrete definition-of-done. Units are sized so that one agent can close one unit and return a self-contained specification fragment; the fragments assemble into the terminal code spec (§5). Correctness-critical units carry an adversarial-verification step.

**Design status this brief builds on.** The architecture is committed and deep, but there is **zero implementation code** and `physics/library/` is an empty scaffold (only `cert/reference-data/` holds content). So the research targets are precisely the items the canon still marks open, deferred, or specified only at design (not code) depth. This brief is that map, made actionable.

---

## 2. Scope

**In scope — the oracle and its outward seams:**
- The **compile pipeline**, Stages 1–4 (symbolic lift + applicability pruning; symmetry quotient; invariant synthesis; algebraic simplification; lowering + adjoint synthesis + codegen).
- The **oracle-file runtime**, Stage 5 (the emitted kernel: `Validate`, gradients, observables, cert reference).
- The **certification layer** (the ten obligations, evidence aggregation, the reference-data cache).
- The **representation substrate** (the storage/identity primitives everything is expressed in).
- The project's **automatic differentiation** and implicit-differentiation adjoint synthesis.
- The **consumer seams only**: the `Validate` / `Import` / dynamics-hand-off contracts, specified to honor the oracle-contract requirements in §3.4.

**Out of scope (do not chase):**
- The learned proposer (`/informed-operator`) and the driving loops (`/interface`) — their *internals*. Only their seams to the oracle are in scope.
- The **evolver / time-evolution lowering** — it is a decided-in-principle but deferred sibling and lands as its own named wave; this brief specifies only that the oracle contract does not foreclose it (§3.4, req. 5).
- The **V2 physics upgrades and out-of-scope phenomena** enumerated in `arch-17-out-of-scope` (e.g. live NEGF / SCPH / 4-phonon BTE / non-adiabatic AHC / absolute Berry-phase polarization / strongly-correlated `γ̂`). The spec must preserve their refusal paths, not implement them.

**Language / toolchain — treated as OPEN.** This brief makes **no prescriptive language commitment.** Any programming language, library, or toolchain named anywhere below is a *candidate to investigate and compare*, never a mandate. Toolchain selection is itself a research unit (**R0.1**). Consequently, every downstream specification unit must be written **language-agnostically** — at the level of algorithm, typed interface, and data contract — with at most a thin, clearly-labelled per-candidate binding note. The code spec must not hard-depend on an unchosen language.

---

## 3. Settled foundation (constraints the spec must honor — not research targets)

These are fixed inputs. Research units must respect them; they are not to be reopened (except language, §2).

### 3.1 Runtime model
Compile-once, call-many. The CLI compiles a `(PeriodicityStructure, SiteDecoration, Environment)` identity into one immutable, hash-identified, self-describing oracle-file (seconds–minutes, all symbolic work here); consumers load it and call it as a pure function (µs–ms, millions of times). One file per identity; new pins / new registry version / new identity → new file, new hash. Immutable, never edited in place.

### 3.2 Behavioral invariants
- **Score, not solve.** The caller supplies complete candidate states; the oracle never fills in missing pieces, owns no loop, evolves nothing.
- **Evidence, never verdicts.** Keyed floats only — raw per-slot residuals; no normalization, weighting, summation, or judgment anywhere in the product.
- **Refusal is absence.** A check the oracle cannot stand behind is simply not present in the compiled kernel; its key is absent from every map.
- **Trust travels with the file.** Each oracle-file carries a hash-pinned certificate reference.

### 3.3 The tractability spine (governs how targets and observables are organized)
Two facts keep the observable/target space finite and cross-coupling free of combinatorial blow-up, and the spec must preserve both:
- **Closed vocabulary.** A fixed grammar — 3 inputs, a 7-tuple state, 132 named formulas, 11 observable bundles, 19 residual categories, 10 cert obligations, 4 typeclasses. The channel space is enumerable, not open-ended.
- **Generative-functional collapse.** The physics is one metriplectic law, `dx/dt = L·δE/δx + M·δS/δx` — two scalar functionals (energy E, entropy S) and two operators (reversible L, dissipative M) on one state. Every property, every parameter-axis dependence, and every cross-coupling (thermoelastic, piezoresistive, thermoelectric, piezoelectric …) is a derivative/projection of E and S — not an independently enumerated object. Consequence for the spec: expose only the **primitive** axes (temperature, frequency, field, strain, direction); axis *combinations* are cross-derivatives and must fall out for free, never be enumerated.

### 3.4 The oracle-contract requirements (forward-compatibility with inverse design)
The contract must guarantee all six, so a learned proposer can be trained/certified against the oracle without the contract being reopened later:
1. **Granular, keyed, per-channel residuals + observables — never aggregated.** (Enables per-channel loss terms.)
2. **Axis-keyed slots** (`ResidualKey = (producer, axis-tuple)`) with axis coordinates in the static schema. (Makes functional/curve targets representable as sets of per-axis-point slots.)
3. **Every *targetable* observable is on the differentiable path** (baked adjoint → cotangents), carries a σ, and is pinnable as a target — not a forward-only readout.
4. **The primitive targetable axes are exposed** (temperature, frequency, field, strain, direction); combinations are automatic (§3.3).
5. **The scorer/evolver split is kept clean** so time-dependent targets can later attach via the evolver sibling; nothing is baked that forecloses it.
6. **One shared namespace** across state channels ↔ observable keys ↔ residual keys, so proposer and oracle compose.

### 3.5 The diamond MVP acceptance test (the first end-to-end validation target)
The MVP code spec must be validated by this test (also recorded in [mvp-03-capabilities], Cap 1):
- **Null:** grade a ground-truth, relaxed pure-diamond state → every residual slot ≈ 0 within σ (the oracle certifies truth as lawful).
- **Sensitivity:** perturb the state (displace an atom, distort the cell off the energy minimum, wrong lattice constant) → non-zero residual, **and the specific keys that fire name the violated law** (`∇_R E_BO = 0` for a bad relaxation, space-group equivariance for a broken symmetry, Born stability for an over-stretch).
- **Data-backed sensitivity:** perturb *along* the existing diamond strain-hypersurface dataset (~1,179 DFT points, PBE/HSE) and confirm the residual tracks the DFT energy rise off the minimum — a quantitative curve-match, not just a sign check.

### 3.6 Settled architecture decisions (do not reopen)
Recorded as closed in `arch-18`: multiscale state + device scale-bridge; the integrator (`dynamics`) hand-off interface (tangent-kernel + steppable-form manifest, integrator stays consumer-side); reference-cache backend; coverage-mask format; curriculum schedule; active-learning placement in `/interface`; applicability decidability; coupling-channel structure and coverage policy; the representation substrate; PhysicsGraph identity; no solver-call hot paths. *(The language decision, though marked closed in canon, is treated as open here per §2 — see R0.1.)*

---

## 4. The research program

Format per unit: **objective** → *specifies* / **internal** sources / **external** research (A = academic/theory, E = engineering/tooling) / **done** / *deps* / *verify* (adversarial where correctness-critical). Units are grouped; groups are roughly independent; suggested sequencing is in §6.

### G0 — Toolchain and language (OPEN)

- **R0.1 — Host-toolchain comparison.** Objective: evaluate candidate language/toolchain configurations for each layer of the system against the design's hard constraints, and recommend one *without* foreclosing it. Constraints to test against: bring-your-own reverse-mode AD (a host whose tracer *owns* differentiation conflicts with adjoint synthesis); availability/quality of an e-graph / equality-saturation library; a typed IR expressive enough for the op-indexed DAG and the typeclass layer; a codegen path to a fast numeric runtime with optional GPU; content-addressed data structures. Candidate configurations to include (as candidates, not defaults): the canon's polyglot proposal (a functional/typed compiler host with its own AD + a separate numeric runtime + offline computer-algebra + offline proof assistant); single-language options; other typed-functional hosts. Re-examine, rather than inherit, any prior exclusion. **Internal:** `[deriv-language-study]`; `arch-18` closed-decision text (as the argument to critique, not accept); `arch-20` (substrate demands); `arch-07 §7.4` (AD seam). **External (A/E):** AD ecosystems per candidate; e-graph libraries (egg / egglog / hegg and equivalents); typed-IR/GADT ergonomics; codegen and GPU stories; computer-algebra and proof-assistant interop. **Done:** a comparison matrix (layer × candidate × constraint) plus a recommended configuration with written rationale and an explicit "reopen if" list. *Verify:* adversarial — attack the recommended configuration on the AD-ownership and e-graph constraints. *Note:* until R0.1 lands, all other units specify language-agnostically (§2).

### G1 — Formula specification (the largest theory body)

- **R1.0 — Registry realignment.** Objective: reconcile the scattered research catalogs to the *current* 132 registry rows and emit a per-row skeleton (equation / method / residual / tolerance / provenance slots). The math today lives in `physics/research/` catalogs keyed to snapshot-local numbers, explicitly stale against the registry. **Internal:** `physics/library/formulas/registry-manifest.csv`; `[deriv-observable-catalog]` (Part C: governing equation + method + residual + tolerance — the richest math-bearing table); `[deriv-generator-catalog]`; `[deriv-csp]`; record schema `impl-04-formulas`. **Done:** every registry row has a stub keyed to its current `#`, with the four slots present (possibly empty), ready for R1.1+. *Deps: none (do first in G1).*
- **R1.1 — Diamond MVP formula set (do first).** Objective: fully specify the Cap-1 formulas to code depth: `E_BO` (the variational principle **plus** the reference-solve protocol it delegates to — functional, pseudopotentials, k-mesh, convergence), elastic constants `C_ij` (finite-strain protocol: strain magnitudes, symmetrization, acoustic-sum-rule handling; or DFPT), Born-stability (all crystal-class branches, not only cubic), structure-uniqueness (the descriptor and its hyperparameters — radial/angular cutoffs, basis, kernel), plus bulk modulus, sound velocity, diamond–graphite convex hull, indirect gap, phonon-max, κ(300 K). Each: governing equation + numerical method + residual form + tolerance + provenance. **Internal:** `mvp-03-capabilities` Cap 1; `arch-08-bo-levels §L2`; `arch-19 §19`; the R1.0 skeleton. **External (A, some E):** DFT stress–strain and DFPT elastic-constant protocols; descriptor-distance (e.g. SOAP-type) papers for hyperparameters; convex-hull construction; the reference-solve delegate (wrap which established DFT code, or reimplement — an E decision with reproducibility pinning). **Done:** each MVP formula is code-spec complete and validated against the diamond dataset. *Verify:* adversarial + numerical check vs the ~1,179-point diamond dataset. *Deps: R1.0.*
- **R1.2…R1.k — Remaining formulas by bundle (staged after MVP).** Objective: same treatment for the other ~120 formulas, batched by observable bundle (electronic, phonon, transport, mechanics, thermodynamics, defect/surface/interface, non-equilibrium, degradation). One unit per bundle (or per coherent sub-cluster). **Done:** per-row code-spec completeness, bundle by bundle. *Deps: R1.0; R1.1 as the pattern exemplar.*
- **R1.x — Reference-solve integration.** Objective: decide and pin, for each "native composition" that delegates to an external solve (DFT / DFPT / GW / BTE), whether to wrap an established solver or reimplement, and pin exact reproducibility (code+version, functional, pseudopotentials, meshes, tolerances). **External (E):** established DFT/DFPT/GW/BTE packages and their reproducibility knobs. **Done:** a solver-integration + reproducibility spec per native-composition class. *Deps: R1.1 (shares E_BO/DFPT choices).*

### G2 — Pipeline stage algorithms

- **R2.1 — Stage 1 (symbolic lift + applicability prune).** Objective: specify graph construction from the three inputs and applicability pruning via the versioned decision-diagram predicate layer. **Internal:** `arch-07 §7.1`; `arch-13-applicability`; `arch-20 §20.2` (`PredicateOps`). **External (E):** ROBDD libraries. **Done:** construction + prune algorithm at code depth.
- **R2.2 — Stage 2 (symmetry quotient).** Objective: specify operator block-diagonalization into per-irrep blocks (Schur), IBZ orbit collapse, offline character-table generation, and the group product table. **Internal:** `arch-07 §7.2`; `arch-09 §9.5`; `arch-14-topology` (incl. Smith Normal Form for the symmetry-indicator group); `arch-20 §20.5` (Schreier–Sims). **External (A/E):** computational group theory; irrep/isotypic decomposition; Smith Normal Form; character-table tooling. **Done:** the quotient algorithm at code depth. *Verify:* adversarial (correctness of block-diagonalization on a nontrivial group).
- **R2.3 — Stage 2.5 (invariant synthesis).** Objective: expand the one unspecified primitive in the existing pseudocode — the trivial-irrep projector's basis construction/orthogonalization — to code depth. **Internal:** `arch-19 §19.3` (pseudocode, complexity bounds, Reynolds projection, character inner product). **External (A):** invariant-theory projector construction. **Done:** the projector primitive specified; the stage is then complete. *Deps: R2.2.*
- **R2.4 — Stage 3 (algebraic simplification) — CONTAINS A GENUINELY OPEN PROBLEM.** Objective: specify hash-consing, cross-formula CSE, tearing/alias elimination, and equality-saturation; **and resolve or bound** the flagged-unsolved item — error tracking for ε-equality e-graphs (the reason equality saturation is an *offline-only* tool in V1; no runtime rewrite engine is permitted). **Internal:** `arch-07 §7.3`; `arch-15-gamma-hat §15.4` (the open-problem statement); `arch-18` (offline-rewrite constraint). **External (A):** equality saturation / e-graphs (egg / egglog literature); rewriting under approximate/interval equality; error propagation in CSE. **Done:** hash-consing/CSE/tearing at code depth; a written verdict on ε-equality error tracking — either a method, or a proof it stays offline with the V1 boundary drawn. *Verify:* adversarial — treat the ε-equality result skeptically; this is a known-hard item.
- **R2.5 — Stage 4 (lowering + compression + codegen).** Objective: specify compression-plan selection (Dense / Sparse / LowRank / HODLR / TT — choosing rank to meet a per-plan error target), the numeric kernels (randomized SVD / Davidson / Lanczos / TT-cross), the codegen seam to the runtime, and the Stage-4→Stage-5 differential golden test. **Internal:** `arch-07 §7.4`; `arch-18` (codegen seam). **External (A/E):** randomized numerical linear algebra; hierarchical (HODLR) matrices; tensor-train decomposition; golden-test methodology. **Done:** selection policy + kernels + codegen seam at code depth. *Deps: R5 (adjoint synthesis shares this stage).*

### G3 — Representation substrate → code (nearest to ready)

- **R3.1 — Primitives + serialization.** Objective: bind the five substrate primitives (Address / Universe / SparseSet / PersistentMap / MerkleDAG), the four op-signatures, the per-cluster backends, and the eleven-clause canonical serialization (incl. float NaN/−0.0 normalization) to the chosen host, porting concrete libraries. **Internal:** `arch-20` (already typed-pseudocode + asymptotics + thresholds). **External (E):** Roaring bitmaps; HAMT/persistent maps; content-addressing (domain-separated hashing); the host's type-level encoding of the op-indexed DAG. **Done:** an implementation-ready data-structures spec. *Deps: R0.1 (host).*
- **R3.2 — Serialization-injectivity verification.** Objective: specify a check (optionally machine-proved) that the canonical pre-hash encoding is injective. **Internal:** `arch-20 §20.4`; `arch-18` (proof-assistant candidate). **External (A):** proof-assistant encoding. **Done:** an injectivity-verification spec. *(Verification, not open research.)*

### G4 — Cert layer completion (schema ready; checker bodies partial)

- **R4.1 — Machinery.** Objective: specify the reference-data cache (the SQL schema is given), the s-expression evidence renderer, the Merkle-DAG semilattice-meet aggregation with early-exit, the freeze fixture, and the tamper tripwire. **Internal:** `arch-12` (schema, tolerance ledger, aggregation) + `impl-08-cert-detail`. **External (E):** embedded SQL/WAL; content-addressed caching. **Done:** cert machinery at code depth. *Deps: R3.1.*
- **R4.2 — Checker bodies.** Objective: fill the named-but-untabulated checkers: obligation-3 analytic-limit witness predicates per observable; obligation-7 bulk-boundary `(k_generator, orientation) → multiplicity` table; obligation-6 degeneracy-tripwire tolerances. **Internal:** `arch-12 §12.0.x`; `impl-08`. **External (A + reference-data):** analytic-limit closed forms; topological bulk-boundary multiplicities. **Done:** each obligation's checker specified. *Overlaps R6.2 (analytic witnesses).*

### G5 — AD / adjoint (principle set; engine + synthesis absent)

- **R5.1 — Reverse-mode AD engine.** Objective: specify the project's own reverse-mode AD over the typed IR — source-transform vs define-by-run, reverse-pass generation, checkpointing — such that it, not a host tracer, owns differentiation. **Internal:** `arch-18` (own-AD decision); `arch-11 §residuals` (reverse-mode per-key gradient). **External (A/E):** reverse-mode AD design; AD over typed functional IRs. **Done:** an AD-engine spec. *Deps: R0.1.*
- **R5.2 — Implicit-differentiation adjoint synthesis.** Objective: specify how, for each fixed-point method class (SCF, GW, BSE, charge-balance), the implicit-function-theorem adjoint is synthesized from the graph — assembling `dF/dx`, choosing the linear solver/preconditioner, delivering the gradient as one extra linear solve — and how the registration gate validates it (vector-Jacobian vs Jacobian-vector agreement on ~64 points, τ_adj = 1e-4, on the *synthesized* adjoint). **Internal:** `arch-07 §7.4`; `impl-07 §7.5` (the gate). **External (A):** implicit differentiation / adjoint methods for fixed points. **Done:** per-method-class adjoint-synthesis spec + gate. *Verify:* adversarial + the registration gate itself. *Deps: R5.1.*
- **R5.3 — PDE-mesh adjoint (open decision).** Objective: decide and specify discrete- vs continuous-adjoint of the finite-volume operator for the macro continuum tier, reusing the Stage-4→Stage-5 AD seam. **Internal:** `arch-18` (open item 2). **External (A):** PDE-constrained optimization / discrete-vs-continuous adjoint. **Done:** a chosen scheme + spec. *Deps: R5.1.*

### G6 — Typeclasses, methods, templates → code (signature-complete; bodies absent)

- **R6.1 — Encode the interface layer.** Objective: bind the 4 typeclasses, 12 methods, and 20 templates to typed interfaces in the chosen host; wire a units library; pin the `combineTol` semantics (max-abs vs root-sum-square, per instance). **Internal:** `arch-10-typeclasses`; `impl-02-methods`; `impl-03-templates`. **External (E):** typeclass/type-system encoding; a units library. **Done:** the interface layer at code depth. *Deps: R0.1.*
- **R6.2 — Analytic-structure witnesses.** Objective: specify the `certifyAnalytic` witness predicates (Kramers–Kronig, Onsager, sum-rules). **Internal:** `arch-10`. **External (A):** the analytic-structure relations. **Done:** witness predicates specified. *Overlaps R4.2.*

### G7 — Open architecture decisions (arch-18)

- **R7.1 — Surrogate-net build vs adopt.** Objective: decide whether the D4 surrogate path ships at all and, if so, build vs adopt. **Internal:** `arch-18` item 1. **External (A/E):** surrogate modeling. **Done:** a decision + (if shipping) a spec; else an explicit non-ship with refusal path preserved.
- **R7.2 — PDE-mesh adjoint.** *(= R5.3.)*
- **R7.3 — The γ̂ open CS problems.** Objective: resolve the four density-matrix data-structure problems — ε-equality error tracking; materialization policy; long-trajectory drift / rank-refresh; rank-dependent applicability of the low-rank slot. Canon calls these "the only open CS problems in the design." **Internal:** `arch-15-gamma-hat §15.4`; `arch-18` item 3. **External (A):** low-rank / natural-orbital representations; numerical stability of long-trajectory low-rank updates. **Done:** a spec (or a bounded deferral) for each. *Verify:* adversarial (shares the ε-equality item with R2.4).
- **R7.4 — Layer-1.75 minimum spec.** Objective: specify the minimum sufficient for a later contributor to implement self-consistent GW / DMFT (V1 ships only type/cert scaffolding + loud not-implemented stubs). **Internal:** `arch-18` item 4; `impl-07 §7.7` (stubs). **External (A):** self-consistent GW / DMFT interfaces. **Done:** the minimum-spec boundary drawn.

### G8 — Product surface: ABI, wire formats, cache policy

- **R8.1 — Loading convention / ABI.** Objective: decide and specify native-module vs flat-array C-style ABI vs both, for how consumers load and call an oracle-file. **Internal:** `product.md §9`. **External (E):** FFI/ABI design. **Done:** the loading contract.
- **R8.2 — Wire formats.** Objective: specify serialization of state files, residual/value maps, and the CLI schema table. **Internal:** `product.md §9`; `arch-20 §20.4` (canonical serialization to reuse). **External (E):** serialization formats. **Done:** wire-format specs.
- **R8.3 — Compile-cache management.** Objective: specify eviction / sharing / provenance policy (content addressing already makes correctness free; only policy is open). **Internal:** `product.md §9`; `arch-07 §7.6` (fingerprint keying). **Done:** a cache-policy spec.

### G9 — Consumer seams

- **R9.1 — The Validate / Import / dynamics contracts.** Objective: specify the three outward seams to code depth, provably honoring the six oracle-contract requirements (§3.4) — including that every targetable observable is differentiable and axis-keyed, and that the dynamics hand-off leaves the evolver sibling reachable. **Internal:** `arch-16-pino-bridge`; `product.md §4, §6`; §3.4 of this brief. **Done:** the seam contracts specified, with a checklist mapping each to reqs. 1–6. *Deps: R5 (differentiability), R1.0 (axis metadata).*

### G10 — Formalization gaps

- **R10.1 — Machine-readable catalogs.** Objective: bring the observable catalog (52 observables + 16 figures-of-merit), the crystal-structure-validity residual catalog, and the remaining non-equilibrium bundle to full machine-readability, aligned to registry rows. **Internal:** [computational-overview] (the formalization-gap list); the research catalogs. **Done:** registry-aligned machine-readable catalogs. *Deps: R1.0.*

---

## 5. Terminal deliverable — structure of the code specification

The assembled research produces a single code-specification document (or a tight set), organized as:
1. **Toolchain & layering** — the chosen configuration (R0.1) and the per-layer language bindings.
2. **Representation substrate** — data structures, ops, serialization (R3).
3. **Type/interface layer** — typeclasses, methods, templates (R6).
4. **Formula specifications** — per registry row: equation, method, residual, tolerance, provenance, adjoint (R1).
5. **Pipeline** — per-stage algorithms, Stages 1–4 (R2), with the AD/adjoint synthesis (R5) at Stage 4.
6. **Runtime** — the oracle-file: `Validate`, gradients, observables, cert reference; the ABI and wire formats (R8).
7. **Cert layer** — obligations, aggregation, cache, checkers (R4).
8. **Consumer seams** — Validate / Import / dynamics contracts against §3.4 (R9).
9. **Open-item register** — the residual open decisions (R7) with their drawn boundaries or chosen resolutions.
10. **Validation plan** — the diamond MVP acceptance test (§3.5) as the first end-to-end gate, plus the per-stage golden/registration gates.

Each section is "code-spec complete" when an engineer can implement it with no further research and no open design question.

---

## 6. Execution model and sequencing

**Fan-out.** One agent per research unit (or per bundle sub-cluster in G1). Each agent reads the named internal canon plus its external sources (each consulted once) and returns a self-contained specification fragment in the §5 structure. Correctness-critical units (R0.1, R2.2, R2.4, R5.2, R7.3) return through an adversarial-verification pass before acceptance.

**Suggested order (dependencies, not a strict serialization):**
1. **First:** R0.1 (toolchain) and R1.0 (registry realignment) — they unblock nearly everything. R3.1 (substrate) can start in parallel once R0.1 lands.
2. **MVP slice:** R1.1 + R5.1/R5.2 (adjoint for the MVP formulas) + R2.2/R2.3 (symmetry) + R4.1 + R9.1 → enough to specify the code behind the diamond Cap-1 and satisfy §3.5.
3. **Hard/open items, in parallel:** R2.4 (ε-equality e-graph), R7.3 (γ̂), R5.3 (PDE adjoint) — flagged genuinely-open; may return "bounded deferral" rather than a full method.
4. **Breadth:** R1.2…R1.k by bundle, R2.5, R6, R8, R4.2, R10 — scale-out once the MVP spine is specified.
5. **Last:** assemble §5 and re-verify against §3.

**Staging principle.** Specify the **diamond MVP subset first** and validate it against §3.5 before scaling to all 132 formulas and 11 bundles — the MVP is the correctness anchor for everything after.

---

## 7. Source index

**Internal canon (atomic tree):** `arch-01-purpose`, `arch-03-inputs`, `arch-04-state`, `arch-05-generic`, `arch-06-physics-graph`, `arch-07-pipeline`, `arch-08-bo-levels`, `arch-09-vocabularies`, `arch-10-typeclasses`, `arch-11-residuals`, `arch-12-cert`, `arch-13-applicability`, `arch-14-topology`, `arch-15-gamma-hat`, `arch-16-pino-bridge`, `arch-17-out-of-scope`, `arch-18-open-decisions`, `arch-19` (invariant synthesis), `arch-20-representations`, `arch-21-multiscale-state`; `impl-02-methods`, `impl-03-templates`, `impl-04-formulas`, `impl-07-residual-factory`, `impl-08-cert-detail`; `mvp-03-capabilities`.
**Internal (standalone / research strata):** [product]; [computational-overview]; `[deriv-language-study]`, [deriv-observable-catalog], [deriv-generator-catalog], [deriv-csp]; `physics/library/formulas/registry-manifest.csv`; `physics/library/cert/reference-data/*.csv`; the diamond strain-hypersurface dataset.
**External research themes (each consulted as needed, once):** computational group theory & irrep decomposition; Smith Normal Form; invariant-theory projectors; equality saturation / e-graphs and error-tracked rewriting; randomized numerical linear algebra, HODLR, tensor-train; reverse-mode AD design; implicit-differentiation / adjoint methods for fixed points; PDE discrete-vs-continuous adjoint; descriptor-distance methods and their hyperparameters; DFT/DFPT/GW/BTE reference-solve protocols and reproducibility; low-rank / natural-orbital density-matrix representations; embedded SQL/content-addressed caching; ABI/FFI and serialization; language/AD/e-graph/codegen ecosystems per candidate toolchain.

---

*This brief specifies research, not implementation. Its completion yields the code specification; the code specification, in turn, is what gets implemented. Language and toolchain remain open (R0.1) until that unit closes.*
