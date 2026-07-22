# /physics Oracle — Code-Specification Research Brief

*2026-07-21 · standalone research brief (lives under `journal/live/`, outside the book's `pages/`) · to be executed as a fan-out of independent research agents*

---

## 1. Goal

**Terminal deliverable.** Executing the research program defined in this brief produces **one document that fully *specifies*, but does not *implement*, the code of the `/physics` oracle.** "Fully specifies" means: every module, data structure, algorithm, numerical method, type signature, contract, and tolerance is pinned to the point that implementation is a mechanical act — a competent engineer could type it out with no further research and no open design questions.

**What the oracle is (why the spec matters).** The oracle is a compiler: it takes a material identity and emits an immutable, content-addressed *oracle-file* — a pure function that **scores** a complete candidate state against the laws of physics (keyed law-violation residuals + requested observables + optional cotangents + a certificate), and never solves, completes, or judges. It is the **physics-informed residual-loss term** — and the certifier — for training the neural operator (`/informed-operator`): the oracle scores an emitted candidate state and returns keyed residuals plus their cotangents, which enter that operator's training loss. This brief specifies the **oracle**; the operator and the driving loops are separate systems and are out of scope here (§2). The longer-range aim the corpus states — property-targeted crystal design — is a *direction*, not a mechanism assumed here: inverse design is explicitly out of scope for `/physics` (`arch-17-out-of-scope`), and no separate "proposer" component is specified anywhere in the corpus.

**How this brief is used.** The research program (§4) is decomposed into independent, individually-dispatchable **research units (R#)**. Each names its objective, its internal sources, the external research it requires (academic literature or engineering/tooling references, each consulted once), and a concrete definition-of-done. Units are sized so that one agent can close one unit and return a self-contained specification fragment; the fragments assemble into the terminal code spec (§5). Correctness-critical units carry an adversarial-verification step.

**Design status this brief builds on.** The architecture is committed and deep, but there is **zero implementation code** and `physics/library/` is an empty scaffold (only `cert/reference-data/*.csv` and `formulas/registry-manifest.csv` hold content). So the research targets are precisely the items the canon still marks open, deferred, or specified only at design (not code) depth. This brief is that map, made actionable.

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
- The **neural operator** (`/informed-operator`) and the driving loops (`/interface`) — their *internals*. Only their seams to the oracle are in scope.
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
- **Numerics-agnostic at the seam, committed within.** The emitted oracle assumes nothing about its caller — pure function, flat arrays at the boundary, no loop ownership. This is *not* substrate-agnosticism in general: internally `/physics` is committed to the representation substrate of `[arch-20-representations]` (`[impl-01-principles]` principle 8). The spec must keep these two facts separate — the boundary is portable, the interior is not.
- **Evidence, never verdicts.** Keyed floats only — raw per-slot residuals; no normalization, weighting, summation, or judgment anywhere in the product.
- **Refusal is absence — with two distinct regimes.** A check the oracle cannot stand behind is simply not present in the compiled kernel; its key is absent from every map. The regimes must not be conflated (`[impl-01-principles]` principle 6): a degeneracy is caught **at compose time** and refused there *with a numeric witness*; it is never raised from the compiled kernel. **At runtime** there are no exceptions at all — failure surfaces as a `Failed` cert leaf carrying its witness. Consequence for the spec: the compile-time refusal path and the runtime `Failed`-leaf path are separate surfaces with separate enumerations.
- **Trust travels with the file.** Each oracle-file carries a hash-pinned certificate reference.

### 3.3 The tractability spine (governs how targets and observables are organized)
Two facts keep the observable/target space finite and cross-coupling free of combinatorial blow-up, and the spec must preserve both:
- **Closed vocabulary.** A fixed grammar — 3 inputs, a 7-tuple state, 132 named formulas, 11 observable bundles, 19 residual categories, 10 cert obligations, 4 typeclasses. The channel space is enumerable, not open-ended.
- **Generative-functional collapse.** The physics is one metriplectic law, `dx/dt = L·δE/δx + M·δS/δx` — two scalar functionals (energy E, entropy S) and two operators (reversible L, dissipative M) on one state. Every property, every parameter-axis dependence, and every cross-coupling (thermoelastic, piezoresistive, thermoelectric, piezoelectric …) is a derivative/projection of E and S — not an independently enumerated object. Consequence for the spec: expose only the **primitive** axes (temperature, frequency, field, strain, direction); axis *combinations* are cross-derivatives and must fall out for free, never be enumerated.

### 3.4 The oracle-contract requirements (forward-compatibility for target-pinning)
The contract must guarantee all six, so the neural operator can be trained and certified against the oracle — and targets pinned against it — without the contract being reopened later:
1. **Granular, keyed, per-channel residuals + observables — never aggregated.** (Enables per-channel loss terms.)
2. **Axis-keyed slots** (`ResidualKey = (producer, axis-tuple)`) with axis coordinates in the static schema. (Makes functional/curve targets representable as sets of per-axis-point slots.)
3. **Every *targetable* observable is on the differentiable path** (baked adjoint → cotangents), carries a σ, and is pinnable as a target — not a forward-only readout. In the current differentiability vocabulary (`D0 | DN | D1 | D2 | D3 | D4`, owned by `impl-04-formulas`) this means **targetable ⇒ `D1`/`D2`/`D3`**; `DN` rows (no useful derivative — integer, categorical, boolean, set-valued) cannot be differentiable targets at all, and `D4` rows (relaxed: argmin / hull / sort / discrete) are targetable only through their declared relaxation.
4. **The primitive targetable axes are exposed** (temperature, frequency, field, strain, direction); combinations are automatic (§3.3).
5. **The scorer/evolver split is kept clean** so time-dependent targets can later attach via the evolver sibling; nothing is baked that forecloses it.
6. **One shared namespace** across state channels ↔ observable keys ↔ residual keys, so the operator and the oracle compose.

### 3.5 The diamond MVP acceptance test (the first end-to-end validation target)
The MVP code spec must be validated by this test (also recorded in [mvp-03-capabilities], Cap 1):
- **Null:** grade a ground-truth, relaxed pure-diamond state → every residual slot ≈ 0 within σ (the oracle certifies truth as lawful).
- **Sensitivity:** perturb the state (displace an atom, distort the cell off the energy minimum, wrong lattice constant) → non-zero residual, **and the specific keys that fire name the violated law** (`∇_R E_BO = 0` for a bad relaxation, space-group equivariance for a broken symmetry, Born stability for an over-stretch).
- **Data-backed sensitivity:** perturb *along* the existing diamond strain-hypersurface dataset (1,179 DFT points, PBE/HSE) and confirm the residual tracks the DFT energy rise off the minimum — a quantitative curve-match, not just a sign check. **De-duplicate first:** the manifest's 1,179 rows are only 1,131 distinct shapes. (Note: the "~877" figure that appears in older narrative is the byte-salvage count from a truncated download, not the dataset size.)

### 3.6 Settled architecture decisions (do not reopen)
Recorded as closed in `arch-18`: multiscale state + device scale-bridge; the integrator (`dynamics`) hand-off interface (tangent-kernel + steppable-form manifest, integrator stays consumer-side); reference-cache backend; coverage-mask format; curriculum schedule; active-learning placement in `/interface`; applicability decidability; coupling-channel structure and coverage policy; the representation substrate; PhysicsGraph identity; no solver-call hot paths. *(The language decision, though marked closed in canon, is treated as open here per §2 — see R0.1.)*

---

## 4. The research program

Format per unit: **objective** → *specifies* / **internal** sources / **external** research (A = academic/theory, E = engineering/tooling) / **done** / *deps* / *verify* (adversarial where correctness-critical). Units are grouped; groups are roughly independent; suggested sequencing is in §6.

### G0 — Toolchain and language (OPEN)

- **R0.1 — Host-toolchain comparison.** Objective: evaluate candidate language/toolchain configurations for each layer of the system against the design's hard constraints, and recommend one *without* foreclosing it. Constraints to test against: bring-your-own reverse-mode AD (a host whose tracer *owns* differentiation conflicts with adjoint synthesis); availability/quality of an e-graph / equality-saturation library; a typed IR expressive enough for the op-indexed DAG and the typeclass layer; a codegen path to a fast numeric runtime with optional GPU; content-addressed data structures. Candidate configurations to include (as candidates, not defaults): the canon's polyglot proposal (a functional/typed compiler host with its own AD + a separate numeric runtime + offline computer-algebra + offline proof assistant); single-language options; other typed-functional hosts. Re-examine, rather than inherit, any prior exclusion. **Internal:** `[deriv-language-study]`; `arch-18` closed-decision text (as the argument to critique, not accept); `arch-20` (substrate demands); `arch-07 §7.4` (AD seam). **External (A/E):** AD ecosystems per candidate; e-graph libraries (egg / egglog / hegg and equivalents); typed-IR/GADT ergonomics; codegen and GPU stories; computer-algebra and proof-assistant interop. **Done:** a comparison matrix (layer × candidate × constraint) plus a recommended configuration with written rationale and an explicit "reopen if" list. *Verify:* adversarial — attack the recommended configuration on the AD-ownership and e-graph constraints. *Note:* until R0.1 lands, all other units specify language-agnostically (§2).

### G1 — Formula specification (the largest theory body)

- **R1.0 — Registry realignment.** Objective: reconcile the scattered research catalogs to the *current* 132 registry rows and emit a per-row skeleton (equation / method / residual / tolerance / provenance slots). The math today lives in `physics/research/` catalogs keyed to snapshot-local numbers, explicitly stale against the registry. **Internal:** `physics/library/formulas/registry-manifest.csv`; `[deriv-observable-catalog]` (Part C: governing equation + method + residual + tolerance — the richest math-bearing table); `[deriv-generator-catalog]`; `[deriv-csp]`; record schema `impl-04-formulas`. **Done:** every registry row has a stub keyed to its current `#`, with the four slots present (possibly empty), ready for R1.1+. *Deps: none (do first in G1).*
- **R1.1 — Diamond MVP formula set (do first).** Objective: fully specify the Cap-1 formulas to code depth: `E_BO` (the variational principle **plus** the reference-solve protocol it delegates to — functional, pseudopotentials, k-mesh, convergence), elastic constants `C_ij` (finite-strain protocol: strain magnitudes, symmetrization, acoustic-sum-rule handling; or DFPT), `elastic-stability-criteria` (row 57 — all crystal-class branches, not only cubic; the "Born" criteria, de-eponymised), `structure-uniqueness-CSP` (row 85 — the descriptor and its hyperparameters: radial/angular cutoffs, basis, kernel; **retagged `DX` → `D4` on 2026-07-21**, so its declared relaxation — softmin over the comparison set plus a sigmoid on `(d − d_min)` — is part of the spec, and the widths are hyperparameters to pin alongside the descriptor. It is *not* validation-only), plus bulk modulus, sound velocity, `phase-diagram-convex-hull` (row 67, tagged `D4` — specify its relaxation), indirect gap, phonon-max, κ(300 K). Each: governing equation + numerical method + residual form + tolerance + provenance. **Internal:** `mvp-03-capabilities` Cap 1; `arch-08-bo-levels §L2`; `arch-19 §19`; the R1.0 skeleton. **External (A, some E):** DFT stress–strain and DFPT elastic-constant protocols; descriptor-distance (e.g. SOAP-type) papers for hyperparameters; convex-hull construction; the reference-solve delegate (wrap which established DFT code, or reimplement — an E decision with reproducibility pinning). **Done:** each MVP formula is code-spec complete and validated against the diamond dataset. *Verify:* adversarial + numerical check vs the diamond dataset (1,179 points → de-duplicate to 1,131 distinct shapes first). *Deps: R1.0.*
- **R1.2…R1.k — Remaining formulas by bundle (staged after MVP).** Objective: same treatment for the other ~120 formulas, batched by observable bundle (electronic, phonon, transport, mechanics, thermodynamics, defect/surface/interface, non-equilibrium, degradation). One unit per bundle (or per coherent sub-cluster). **Done:** per-row code-spec completeness, bundle by bundle. *Deps: R1.0; R1.1 as the pattern exemplar.*
- **R1.x — Reference-solve integration.** Objective: decide and pin, for each "native composition" that delegates to an external solve (DFT / DFPT / GW / BTE), whether to wrap an established solver or reimplement, and pin exact reproducibility (code+version, functional, pseudopotentials, meshes, tolerances). **External (E):** established DFT/DFPT/GW/BTE packages and their reproducibility knobs. **Done:** a solver-integration + reproducibility spec per native-composition class. *Deps: R1.1 (shares E_BO/DFPT choices).*

### G2 — Pipeline stage algorithms

- **R2.1 — Stage 1 (symbolic lift + applicability prune).** Objective: specify graph construction from the three inputs and applicability pruning via the versioned decision-diagram predicate layer. **Internal:** `arch-07 §7.1`; `arch-13-applicability`; `arch-20 §20.2` (`PredicateOps`). **External (E):** ROBDD libraries. **Done:** construction + prune algorithm at code depth.
- **R2.2 — Stage 2 (symmetry quotient).** Objective: specify operator block-diagonalization into per-irrep blocks (Schur), IBZ orbit collapse, offline character-table generation, and the group product table. **Internal:** `arch-07 §7.2`; `arch-09 §9.5`; `arch-14-topology` (incl. Smith Normal Form for the symmetry-indicator group); `arch-20 §20.5` (Schreier–Sims). **External (A/E):** computational group theory; irrep/isotypic decomposition; Smith Normal Form; character-table tooling. **Done:** the quotient algorithm at code depth. *Verify:* adversarial (correctness of block-diagonalization on a nontrivial group).
- **R2.3 — Stage 2.5 (invariant synthesis).** Objective: expand the one unspecified primitive in the existing pseudocode — the trivial-irrep projector's basis construction/orthogonalization — to code depth. **Internal:** `arch-19 §19.3` (pseudocode, complexity bounds, Reynolds projection, character inner product). **External (A):** invariant-theory projector construction. **Done:** the projector primitive specified; the stage is then complete. *Deps: R2.2.*
- **R2.4 — Stage 3 (algebraic simplification).** *(The "genuinely open problem" this entry carried was closed 2026-07-21; scope reduced accordingly.)* Objective: specify hash-consing, cross-formula CSE, tearing/alias elimination, and equality-saturation to code depth. The ε-equality item is **no longer open**: identity stays exact and ε is estimated beside it (`arch-20-representations §20.4.1`/`§20.4.2`), and a rewrite is admitted iff it is exact over ℝ with its float side conditions discharged by an e-class interval / not-equals analysis and a fidelity generator registered (`arch-07 §7.3`). Equality saturation stays offline for that stated reason rather than as a hedge. **Internal:** `arch-07 §7.3`; `arch-20 §20.4.1`; `arch-18` (offline-rewrite constraint). **External (A):** equality saturation / e-graphs (egg / egglog literature — Zhang et al., PLDI 2023 is the soundness mechanism the rule adopts). **Done:** hash-consing/CSE/tearing at code depth, and the admission rule's side-condition analysis specified concretely enough to implement. *Verify:* adversarial — the admission rule is load-bearing and was twice mis-called open.
- **R2.5 — Stage 4 (lowering + compression + codegen).** Objective: specify compression-plan selection (Dense / Sparse / LowRank / HODLR / TT — choosing rank to meet a per-plan error target), the numeric kernels (randomized SVD / Davidson / Lanczos / TT-cross), the codegen seam to the runtime, and the Stage-4→Stage-5 differential golden test. **Internal:** `arch-07 §7.4`; `arch-18` (codegen seam). **External (A/E):** randomized numerical linear algebra; hierarchical (HODLR) matrices; tensor-train decomposition; golden-test methodology. **Done:** selection policy + kernels + codegen seam at code depth. *Deps: R5 (adjoint synthesis shares this stage).*

### G3 — Representation substrate → code (nearest to ready)

- **R3.1 — Primitives + serialization.** Objective: bind the five substrate primitives (Address / Universe / SparseSet / PersistentMap / MerkleDAG), the four op-signatures, the per-cluster backends, and the eleven-clause canonical serialization (incl. float NaN/−0.0 normalization) to the chosen host, porting concrete libraries. **Internal:** `arch-20` (already typed-pseudocode + asymptotics + thresholds). **External (E):** Roaring bitmaps; HAMT/persistent maps; content-addressing (domain-separated hashing); the host's type-level encoding of the op-indexed DAG. **Done:** an implementation-ready data-structures spec. *Deps: R0.1 (host).*
- **R3.2 — Serialization-injectivity verification.** Objective: specify a check (optionally machine-proved) that the canonical pre-hash encoding is injective. **Internal:** `arch-20 §20.4`; `arch-18` (proof-assistant candidate). **External (A):** proof-assistant encoding. **Done:** an injectivity-verification spec. *(Verification, not open research.)*

### G4 — Cert layer completion (schema ready; checker bodies partial)

- **R4.1 — Machinery.** Objective: specify the reference-data cache (the SQL schema is given), the s-expression evidence renderer, the Merkle-DAG semilattice-meet aggregation with early-exit, the freeze fixture, and the tamper tripwire. **Internal:** `arch-12` (schema, tolerance ledger, aggregation) + `impl-08-cert-detail`. **External (E):** embedded SQL/WAL; content-addressed caching. **Done:** cert machinery at code depth. *Deps: R3.1.*
- **R4.2 — Checker bodies.** Objective: fill the named-but-untabulated checkers: obligation-3 analytic-limit witness predicates per observable; obligation-7 bulk-boundary `(k_generator, orientation) → multiplicity` table; obligation-6 degeneracy-tripwire tolerances. **Internal:** `arch-12 §12.0.x`; `impl-08`. **External (A + reference-data):** analytic-limit closed forms; topological bulk-boundary multiplicities. **Also resolve — obligation-9 scope defect:** obligation 9 is stated as "surrogate-net validity (for `D4` surrogate formulas)", but after the differentiability retag `D4` means *relaxed* (argmin / hull / sort / discrete). Its checker body — declared input domain, surrogate uncertainty below tolerance, refresh up to date, dev set — describes a **learned net**, which a soft-hull or Gumbel-Softmax relaxation is not; meanwhile the actual learned surrogate (`quasi-particle-shift-G0W0-surrogate`) is `D2` and falls outside the obligation. Decide whether obligation 9 rebinds to the true surrogate rows, splits into surrogate-validity + relaxation-validity, or is rescoped some other way. **Done:** each obligation's checker specified, and obligation 9's scope re-pinned. *Overlaps R6.2 (analytic witnesses); feeds R7.1.*

### G5 — AD / adjoint (principle set; engine + synthesis absent)

- **R5.1 — Reverse-mode AD engine.** Objective: specify the project's own reverse-mode AD over the typed IR — source-transform vs define-by-run, reverse-pass generation, checkpointing — such that it, not a host tracer, owns differentiation. **Internal:** `arch-18` (own-AD decision); `arch-11 §residuals` (reverse-mode per-key gradient). **External (A/E):** reverse-mode AD design; AD over typed functional IRs. **Done:** an AD-engine spec. *Deps: R0.1.*
- **R5.2 — Implicit-differentiation adjoint synthesis.** Objective: specify how, for each fixed-point method class (SCF, GW, BSE, charge-balance), the implicit-function-theorem adjoint is synthesized from the graph — assembling `dF/dx`, choosing the linear solver/preconditioner, delivering the gradient as one extra linear solve — and how the registration gate validates it (vector-Jacobian vs Jacobian-vector agreement on ~64 points, τ_adj = 1e-4, on the *synthesized* adjoint). **Internal:** `arch-07 §7.4`; `impl-07 §7.5` (the gate). **External (A):** implicit differentiation / adjoint methods for fixed points. **Done:** per-method-class adjoint-synthesis spec + gate. *Verify:* adversarial + the registration gate itself. *Deps: R5.1.*
- **R5.3 — PDE-mesh adjoint (open decision).** Objective: decide and specify discrete- vs continuous-adjoint of the finite-volume operator for the macro continuum tier, reusing the Stage-4→Stage-5 AD seam. **Internal:** `arch-18` (open item 2). **External (A):** PDE-constrained optimization / discrete-vs-continuous adjoint. **Done:** a chosen scheme + spec. *Deps: R5.1.*

### G6 — Typeclasses, methods, templates → code (signature-complete; bodies absent)

- **R6.1 — Encode the interface layer.** Objective: bind the 4 typeclasses, 12 methods, and 20 templates to typed interfaces in the chosen host; wire a units library; pin the `combineTol` semantics (max-abs vs root-sum-square, per instance). **Internal:** `arch-10-typeclasses`; `impl-02-methods`; `impl-03-templates`. **External (E):** typeclass/type-system encoding; a units library. **Done:** the interface layer at code depth. *Deps: R0.1.*
- **R6.2 — Analytic-structure witnesses.** Objective: specify the `certifyAnalytic` witness predicates (Kramers–Kronig, Onsager, sum-rules). **Internal:** `arch-10`. **External (A):** the analytic-structure relations. **Done:** witness predicates specified. *Overlaps R4.2.*

### G7 — Open architecture decisions (arch-18)

- **R7.1 — Surrogate-net build vs adopt — SCOPE MUST BE RE-ESTABLISHED FIRST.** Objective: decide whether a learned-surrogate path ships at all and, if so, build vs adopt. **Blocking sub-task:** the differentiability retag repurposed `D4` from *surrogate* to *relaxed* (argmin / hull / sort / discrete), so `arch-18` item 1's phrase "the D4 surrogate formulas" no longer denotes what it denoted when written. Today's `D4` rows are `wulff-shape`, `termination-stability-window`, `interface-bond-counting`, `phase-diagram-convex-hull`, `cluster-expansion-energy` and `structure-uniqueness-CSP` — relaxations, not learned nets — while the one actual learned surrogate, `quasi-particle-shift-G0W0-surrogate`, now sits at `D2`. Re-establish which rows the decision governs *before* deciding it, and reconcile with obligation 9 (see the scope defect noted in R4.2). **Internal:** `arch-18` item 1; `impl-04-formulas` (the current `D0 | DN | D1 | D2 | D3 | D4` vocabulary); `arch-12` obligation 9. **External (A/E):** surrogate modeling. **Done:** a scope statement, then a decision + (if shipping) a spec; else an explicit non-ship with refusal path preserved.
- **R7.2 — PDE-mesh adjoint.** *(= R5.3.)*
- **~~R7.3 — The γ̂ open CS problems.~~ Closed 2026-07-21; no research task remains.** The four density-matrix data-structure problems — ε-equality error tracking; materialization policy; long-trajectory drift / rank-refresh; rank-dependent applicability of the low-rank slot — were one problem seen four ways, and resolve under `arch-20-representations §20.4.1`/`§20.4.2` plus the scorer-only decision. Dispositions: ε-equality → the rewrite-admission rule (R2.4); materialization → the Stage-4 adjoint-tape schedule, a scheduling question with no error term; drift → exported to the integrating consumer via the steppable-form manifest, since a scorer accumulates nothing; rank applicability → a Stage-4 compile-time predicate. **Internal:** `arch-15-gamma-hat §15.4` (canonical); `arch-18` item 3 (struck through). *(This entry also quoted canon as calling these "the only open CS problems in the design"; canon said the opposite even then — `computational-overview` §13 explicitly disclaimed it.)*
- **R7.4 — Layer-1.75 minimum spec.** Objective: specify the minimum sufficient for a later contributor to implement self-consistent GW / DMFT (V1 ships only type/cert scaffolding + loud not-implemented stubs). **Internal:** `arch-18` item 4; `impl-07 §7.7` (stubs). **External (A):** self-consistent GW / DMFT interfaces. **Done:** the minimum-spec boundary drawn.

### G8 — Product surface: ABI, wire formats, cache policy

- **R8.1 — Loading convention / ABI.** Objective: decide and specify native-module vs flat-array C-style ABI vs both, for how consumers load and call an oracle-file. **Internal:** `[product] §9`. **External (E):** FFI/ABI design. **Done:** the loading contract.
- **R8.2 — Wire formats.** Objective: specify serialization of state files, residual/value maps, and the CLI schema table. **Internal:** `[product] §9`; `arch-20 §20.4` (canonical serialization to reuse). **External (E):** serialization formats. **Done:** wire-format specs.
- **R8.3 — Compile-cache management.** Objective: specify eviction / sharing / provenance policy (content addressing already makes correctness free; only policy is open). **Internal:** `[product] §9`; `arch-07 §7.6` (fingerprint keying). **Done:** a cache-policy spec.

### G9 — Consumer seams

- **R9.1 — The Validate / Import / dynamics contracts.** Objective: specify the three outward seams to code depth, provably honoring the six oracle-contract requirements (§3.4) — including that every targetable observable is differentiable and axis-keyed, and that the dynamics hand-off leaves the evolver sibling reachable. **Internal:** `arch-16-pino-bridge`; `[product] §4, §6`; §3.4 of this brief. **Done:** the seam contracts specified, with a checklist mapping each to reqs. 1–6. *Deps: R5 (differentiability), R1.0 (axis metadata).*

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

Page ids below are the book's stable identifiers (`journal/pages/**`); they survived the chapter reorganisation, as did each page's internal `§` numbering, so both forms of citation resolve.

**Internal canon (the book):** `arch-01-purpose`, `arch-03-inputs`, `arch-04-state`, `arch-05-generic`, `arch-06-physics-graph`, `arch-07-pipeline`, `arch-08-bo-levels`, `arch-09-vocabularies`, `arch-10-typeclasses`, `arch-11-residuals`, `arch-12-cert`, `arch-13-applicability`, `arch-14-topology`, `arch-15-gamma-hat`, `arch-16-pino-bridge`, `arch-17-out-of-scope`, `arch-18-open-decisions`, `arch-19-coupling-structure` (invariant synthesis), `arch-20-representations`, `arch-21-multiscale-state`; `impl-02-methods`, `impl-03-templates`, `impl-04-formulas`, `impl-07-residual-factory`, `impl-08-cert-detail`; `mvp-03-capabilities`.
**Internal (narrative, overview, appendix derivations):** `[product]`; `[computational-overview]`; `[formula-registry]`; `[reference-battery]`; `[traps]`; `[deriv-language-study]`, `[deriv-observable-catalog]`, `[deriv-generator-catalog]`, `[deriv-csp]`.
**Internal (data, outside the book):** `physics/library/formulas/registry-manifest.csv`; `physics/library/cert/reference-data/*.csv`; `physics/research/diamond-stretch-and-skew-sweep/` (the strain-hypersurface dataset — note it is currently **untracked** in git).
**External research themes (each consulted as needed, once):** computational group theory & irrep decomposition; Smith Normal Form; invariant-theory projectors; equality saturation / e-graphs and error-tracked rewriting; randomized numerical linear algebra, HODLR, tensor-train; reverse-mode AD design; implicit-differentiation / adjoint methods for fixed points; PDE discrete-vs-continuous adjoint; descriptor-distance methods and their hyperparameters; DFT/DFPT/GW/BTE reference-solve protocols and reproducibility; low-rank / natural-orbital density-matrix representations; embedded SQL/content-addressed caching; ABI/FFI and serialization; language/AD/e-graph/codegen ecosystems per candidate toolchain.

---

*This brief specifies research, not implementation. Its completion yields the code specification; the code specification, in turn, is what gets implemented. Language and toolchain remain open (R0.1) until that unit closes.*

---

## Changelog

- **2026-07-21 (P1 registry repair):** the differentiability tag `DX` was renamed
  `DN` (it collided with the DX center) and eight rows were retagged. Two of them
  are cited in this brief: `structure-uniqueness-CSP` (row 85) moved `DX → D4`, so
  R1.1 must now specify its relaxation and is no longer validation-only; and the
  `D4` set named in R7.1 grew from three rows to six. Row 74 was renamed
  `field-activated-ionization-rate → impact-ionization-coefficient` and row 41
  `vibronic-coupling-factor → lattice-relaxation-phonon-quanta`;
  `physics/library/formulas/retired-names.csv` carries the full map. This file is a
  spec still executing, not a frozen record — see `[conventions]` on why
  `journal/live/specs/` tracks current truth while `journal/live/audits/` does not.
