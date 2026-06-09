# AUDIT PROMPT — `/physics` module of n-Op

You are a **senior computational-physics + scientific-computing auditor**. Your job is to perform a deep, adversarial-but-constructive audit of the **`/physics`** module of a project called **n-Op**. You have a large token budget; spend it on *verification and judgment*, not on rediscovering the project — this brief and the orientation document below front-load the context you need.

The person commissioning this audit is a **computer scientist, not a physicist**, and is *deliberately deferring physics-correctness judgment to you*. Do **not** defer back to them or hedge on physics. Bring rigorous domain expertise: name specific approximations, regimes of validity, error magnitudes, and missing terms. Where you are uncertain, say so precisely and state what would resolve it.

## 1. What `/physics` is (grounding)

`/physics` is a **pure oracle** for a physically-informed neural operator (PINO). It does *not* simulate or store state values; it (1) instantiates a crystalline system, (2) defines the laws governing the time-evolution of its state, and (3) **scores how badly a candidate state/trajectory violates those laws** — emitting a *granular vector of physics residuals with gradients*. The PINO (a separate module, `/informed-operator`) consumes those residuals as a training signal. The downstream purpose is **designing durable ultra-wide-bandgap (UWBG) semiconductor devices** (diamond first; also GaN, AlN, c-BN, β-Ga₂O₃, AlGaN) for harsh environments (>500 °C, high field, high current density, radiation).

Computationally, `/physics` is **a compiler that emits a numerical kernel**, organized around one content-addressed data substrate:
- **Dynamics** use the **GENERIC** form `dx/dt = L·δE/δx + M·δS/δx` (`E` energy functional, `S` entropy functional, `L` antisymmetric/reversible operator, `M` PSD/irreversible operator). All "regimes" of multiphysics (structural, mechanical, thermal, electronic, magnetic, optical, transport, thermodynamic, chemical) are recovered as **extractions** of this single equation.
- A **4+1 stage compose-time pipeline** turns a user request + 3 descriptors (`PeriodicityStructure`, `SiteDecoration`, `Environment`) into a compiled kernel: (1) symbolic lift, (2) symmetry quotient, (2.5) invariant synthesis, (3) algebraic simplification, (4) lowering+adjoint+codegen, (5) runtime apply. Stages 1–4 run once per problem; Stage 5 runs millions of times.
- A **representation substrate** (the "canonical structure"): every object is a *fiber* over five primitives (content-addressed `Address`, typed indexed `Universe`, `SparseSet`, `PersistentMap`, hash-consed `MerkleDAG`) with four op-signatures.
- The state is a **7-tuple** `x = (h, R_I, P_I, Π_h, Z_I, γ̂, A)`; the electronic object `γ̂` is the feasibility-critical data structure (encoded, never densified).

**Read `docs/computational-overview.md` FIRST** — it is a 538-line computational-lens reference (data structures, algorithms, complexity, data layouts, numerical behavior) written specifically to orient you efficiently, with every claim cited to an atomic doc. Its **§13** distinguishes what is *intended to be valid* (treat §§1–12 as claims to verify) from what is *intentionally open* (do not flag intentional deferrals as defects).

## 2. The core objective and the design philosophy (internalize these — the audit is judged against them)

**Objective:** a **general-purpose lattice-physics residual calculator** — given any crystalline material and operating environment, produce accurate, differentiable physics residuals across all relevant regimes.

**The two non-negotiable design commitments you are auditing against:**

1. **Utmost accuracy, *without* relying on expensive numerical methods.** The entire bet of this architecture is that physics residuals can be computed to design-grade accuracy using **elegant computational structures + algorithms** and **closed-form (or one-shot, non-iterative) expressions** wherever possible — pushing unavoidable cost to compile-time specialization (symmetry quotient, sparsity, low-rank/HODLR/TT compression, content-addressed caching, implicit-differentiation adjoints) so the runtime hot path stays cheap (`O(log n)`, no solver invoked from scratch). Accuracy is paramount because the output drives real device design; but accuracy is to be *earned through structure*, not brute force.
   - **This is the central tension you must scrutinize.** DFT, GW, the Boltzmann transport equation, phonon spectra, self-consistent field loops are *normally* expensive iterative numerics. Where does the spec genuinely achieve closed-form/one-shot accuracy, and where does it quietly depend on an iterative solver or a coarse surrogate? Is each such choice's accuracy adequate for UWBG device design? Where it is not, say so.

2. **Largest possible canonical structure, then specialize down.** The design wants *one* maximally-general representation/abstraction that can express the physics, with concrete cases obtained by *specialization* (fibers, typeclass instances, generated terms) rather than by bespoke per-case code. GENERIC (one equation → nine regimes), the substrate (one Merkle/universe contract → all objects), and the coupling generator (symmetry-generated invariant terms → all cross-regime couplings) are the three expressions of this principle. Judge whether the canonical structure is *as large and as clean as it should be*, whether specialization is *principled*, and whether anything is ad-hoc that should be canonical (or over-generalized where a specialization would be clearer).

## 3. Directory map & research-file guide (what to read, in what order)

Repository root: `/home/javier/Projects/Physics/Programs/n-Op`. Everything is **specification + research; there is zero implementation code yet** (greenfield). Treat the docs as the artifact under audit.

```
docs/
  computational-overview.md        ← READ FIRST (computational-lens reference, 538 ln)
  architecture.md / implementation-plan.md / mvp-slice.md / formula-registry.md / properties.md
                                     ← GENERATED monoliths/bundles (assembled from the atomic files
                                       below); read a monolith only if you prefer one big file.
  _bundles/                        ← generated LLM-context bundles (full-spec, arch-only, mvp-build)
  meta/                            ← tooling: lint.py, assemble.py, carve.py, manifest.yaml,
                                       conventions.md, glossary.md  (read glossary.md for vocabulary)

  architecture/   (the canonical spec — 20 atomic files; READ THESE for depth)
    01-purpose          02-libraries        03-inputs           04-state
    05-generic (GENERIC dynamics)           06-physics-graph (the IR)
    07-pipeline (4+1 stages)                08-bo-levels (L1–L4 layering)
    09-vocabularies (12 methods / 20 templates / 102 formulas / CrystalSymmetryGroup)
    10-typeclasses (4 capability typeclasses)     11-residuals (17 categories)
    12-cert (10 obligations)                13-applicability (predicates)
    14-topology (symmetry/topology atlas)   15-gamma-hat (the γ̂ data structure + open problems)
    16-pino-bridge (the output boundary)    17-out-of-scope
    18-open-decisions (5 open, incl. resolved impl-language)
    19-coupling-structure (the coupling generator — 580 ln, the keystone of cross-regime physics)
    20-representations (the substrate — the "canonical structure", 283 ln)

  implementation/ (how it gets built — 11 atomic files)
    01-principles  02-methods  03-templates  04-formulas  05-bundles  06-compositions
    07-residual-factory  08-cert-detail  09-cross-cutting  10-build-sequence  11-verification

  mvp/ (the diamond-first slice — 6 atomic files)
    01-system  02-gamma-budget  03-capabilities  04-in-mvp-vs-deferred  05-decisions-forced  06-build-order

physics/research/   (the PRIMARY-SOURCE physics research the spec was synthesized from)
  group-A-ion-dynamics.md            (719 ln) — structural/mechanical/vibrational/ionic regime physics
  group-C-transport-thermo-chemical.md (688) — transport, thermal, thermodynamic, chemical/surface physics
  defects-surfaces-interfaces.md     (620) — per-host defect inventories, surface & interface physics
  non-equilibrium-high-field.md      (558) — impact ionization, avalanche, hot carriers, self-heating, leakage
  residual-generator-catalog.md      (551) — the catalog of residual generators
  group-B-electronic-magnetic-optical.md (505) — electronic-structure, magnetic, optical regime physics
  csp-heterostructure.md             (302) — crystal-structure-prediction validity & heterostructure residuals
  uwbg-observable-catalog.md         (260) — the ~80 target observables the PINO must predict
  applicability-classifiers.md        (72) — per-property applicability predicates
  implementation-language.md         (210) — (the resolved language decision; context only, not physics)

physics/library/    ← EMPTY SCAFFOLD (directory tree of .gitkeep placeholders) + one populated file:
  formulas/registry-manifest.csv     ← the 102 named formulas, indexed (signatures, bundles, cost/diff tiers)
informed-operator/, interface/       ← sibling modules; mostly empty. /physics must stay decoupled from them.
```

**Recommended reading order (token-efficient):** `docs/computational-overview.md` → `glossary.md` → the architecture atomic files in this priority: 05, 20, 07, 06, 09, 19, 11, 04, 15, 08, 12, 10, 13, 14, 16, then 01/03/17/18 → the `physics/research/*` group files (these are the physics ground truth — compare them against what landed in the spec) → `implementation/*` and `mvp/*` for the build/accuracy commitments → `physics/library/formulas/registry-manifest.csv` for the formula inventory.

## 4. THE AUDIT

Perform the audit in three ordered parts. **Part 1 (physics) gates the rest** — if the physics is incomplete or wrong, the structures are moot.

### Part 1 — The physics: is it complete and correct for the objective?

Consider the physics *first*, on its own terms, for the goal of a general-purpose lattice-physics residual calculator targeting UWBG device design.
- **Completeness:** Does the spec capture all the physics needed? Walk the nine regimes (`arch-05`), the target observables (`uwbg-observable-catalog`), the residual categories (`arch-11`), and the coupling channels (`arch-19`). Is there enough information to actually compute each residual? What physics is **missing, under-specified, or hand-waved** — terms, regimes, couplings, boundary conditions, environmental dependencies (temperature, field, strain, radiation)?
- **Correctness:** Are the formulations, approximations, and named formulas physically correct and used within their regimes of validity? Flag any approximation that is wrong, mis-applied, or whose error is too large for design-grade accuracy at UWBG operating conditions (high T, high field).
- **The GENERIC bet:** Is `dx/dt = L·δE/δx + M·δS/δx` genuinely expressive enough to represent *all* the target physics as extractions? Identify any phenomenon that resists this form (far-from-equilibrium transport, strong correlation, non-Markovian memory, stochastic/rare-event kinetics) and assess how/whether the spec handles it.
- **The accuracy-vs-cost frontier:** This is central. For each major quantity, judge whether the spec's closed-form / one-shot / surrogate approach reaches design-grade accuracy *without* an expensive iterative method — and where it cannot, whether the fallback (e.g., the Layer-1.25 one-shot dressings like G₀W₀, or the D4 surrogate formulas, or the symmetry-reduced eigensolves) is accurate enough, and whether its cost is genuinely amortized at compile-time. Be specific about error magnitudes.
- **Material generality:** The spec is diamond-first but claims comprehensiveness. Does the physics actually generalize to the other UWBG materials and their distinctive phenomena (polar/piezoelectric materials, alloy disorder, defect chemistry, heterointerfaces, polarization fields) without missing physics?

### Part 2 — The data structures and programs: efficient, elegant, general?

Now consider the computational structures that will implement the physics (the substrate `arch-20`, the IR `arch-06`, the pipeline `arch-07`, the coupling generator `arch-19`, the methods/templates `arch-09`, the residual machinery `impl-07`).
- **The canonical-structure / specialize-down principle:** Is the canonical structure *as large and general as it should be*? Does it genuinely subsume the physics, with concrete cases obtained by clean specialization (fibers, typeclass instances, generated invariant terms), or are there ad-hoc structures that escape it / sui-generis exceptions that are larger than they should be? Could more be folded into the canonical structure, or is anything over-generalized at the cost of clarity or efficiency? Is the specialization mechanism principled and uniform?
- **Efficiency:** Are the data structures and algorithms efficient for their access patterns? Scrutinize the `O(log n)` / no-solver-on-the-hot-path commitments — are they actually achievable given the physics (eigensolves, sparse solves, fixed points), or are there hidden runtime costs? Are the data layouts (e.g., the `γ̂` k-blocked/low-rank encoding, the arena/index DAG, the compression-plan choices) the right ones?
- **Elegance & generality:** Are the abstractions (the GENERIC assembly, the SymbolicTensorOps operad, the Reynolds-projection coupling generator, the content-addressed Merkle substrate, the four typeclasses) clean, composable, and general — or are they leaky, redundant, or forced? Does the symbolic-IR → compiled-kernel design lose accuracy in lowering?
- **Coverage of the canonical structure:** Does the `SymbolicTensorOps` operad actually express every formula and coupling? Does the substrate genuinely represent every load-bearing object, and are the two sui-generis exceptions (`CrystalSymmetryGroup`, `PhysicsGraph`) the right and only ones? Does the coupling generator (symmetry-projected invariants + the typed long-range `KernelExt`) generate *all* needed cross-regime couplings, or are there couplings symmetry-projection cannot produce?

### Part 3 — Additional directions (use your own judgment too)

Beyond Parts 1–2, investigate whatever you judge important. To seed that, here are the questions the commissioner most wants answered — pursue these and add your own:

1. **An end-to-end accuracy / error model.** Compression (LowRank/HODLR/TT truncation), surrogate (D4) formulas, one-shot dressings (Layer 1.25), symmetry reduction (exact?), and the `γ̂` approximate-equality question all introduce error. Is there a *composed* error budget from inputs to emitted residual? Are truncation tolerances principled? Is error *tracked* anywhere, or silently dropped? (See the `γ̂` §15.4 ε-equality open problem and whether it generalizes to a systemic gap.)
2. **The closed-form discipline's true boundary.** Classify the 12 methods and the 102 formulas by *genuine* computational character: which are truly closed-form, which hide an eigensolve / SCF loop / Boltzmann solve / PDE timestepper. Where is an iterative numerical method *unavoidable*, and is the "expensive at compile-time, cheap at runtime" amortization real for it (e.g., does an SCF inner loop or a BTE solve actually collapse to a precomputed structured apply at Stage 5, or does it recur per state sample)?
3. **Differentiability completeness.** Every residual must be differentiable for the PINO. Assess coverage across the differentiability tiers (D0–D4), the exception sets (band crossings, phase transitions, level crossings), and the implicit-differentiation adjoints for fixed-point methods. Are the synthesized adjoints accurate (the spec gates them at `τ_adj = 1e-4`)? Where does differentiability break or degrade, and does that matter for training?
4. **Residual sufficiency for *learning*.** Do the 17 categories + the formula/coupling set give the PINO *enough* constraints — all relevant conservation laws, sum rules, symmetry/equivariance conditions, analytic-structure (Kramers–Kronig) constraints, detailed-balance/Onsager relations — to learn correct dynamics, not just locally-consistent ones? What residuals are missing?
5. **GENERIC structural guarantees.** Are the structural conditions actually enforceable by construction: `L` antisymmetric, `M` PSD, and the degeneracy conditions `L·δS/δx = 0`, `M·δE/δx = 0`? Does the symmetry-generated coupling machinery *preserve* these (the spec routes `AntisymmForm`/`PSDSymmForm` targets and claims PSD-by-construction) — verify, don't assume.
6. **Numerical stability of the elegant structures.** Content-addressing depends on canonical float normalization, yet physics is continuous and approximate — does ε-tolerance vs exact content-addressed identity create cache incoherence, instability, or silent staleness? Are the stabilization techniques (log-sum-exp, broadening η near resonances, acoustic-sum-rule enforcement, IBZ orbit weights, PSD/antisymmetric projection) sufficient and correctly placed?
7. **The formalization gaps (already known) — judge their *physics* severity.** A prior pass found four researched-but-not-yet-formalized registries: the ~80 observable catalog, the per-host defect inventory, the crystal-structure-validity residuals, and the detailed non-equilibrium (B9) bundle. These are enumeration gaps — but assess whether any of them hides a *physics* incompleteness (a missing observable, defect channel, or constraint that the design target actually requires), not merely a transcription debt.
8. **Anything else your expertise flags** — missing physics, an inelegant or non-general structure, an accuracy risk, a regime not covered, an approximation outside its validity, a better canonical abstraction. Bring it.

## 5. Ground rules

- **Verify against the documents; cite `arch-xx §y` / `impl-xx` / `physics/research/<file>` for every finding.** Do not trust the orientation doc blindly — it is itself part of what you check.
- **Compare the `physics/research/*` ground truth against what landed in the committed spec.** Surfacing physics that was researched but lost, weakened, or contradicted in synthesis is high-value.
- **Distinguish three verdicts per finding:** (a) *defect* — wrong/missing/incomplete and must be fixed; (b) *risk* — a judgment call or accuracy concern worth surfacing; (c) *intentionally open* — already flagged as deferred (don't count these as defects, but do confirm the open-list is complete).
- **Respect the philosophy:** when you criticize a closed-form approximation, weigh it against the alternative cost — the bar is "design-grade accuracy at acceptable cost," not "matches a converged ab-initio calculation." When you criticize a structure, weigh elegance/generality against efficiency. Recommend; don't just condemn.
- **Stay in scope:** audit `/physics`. The PINO/trainer (`/informed-operator`) and the active-learning loop (`/interface`) are out of scope except at the residual/observable boundary.

## 6. Deliverable

Produce a structured audit report:
1. **Executive verdict** — is `/physics` physically complete and computationally sound for a general-purpose, accurate, closed-form lattice residual calculator? One paragraph, then a confidence statement.
2. **Part 1 — Physics findings** — completeness, correctness, the accuracy-vs-cost frontier, GENERIC expressiveness, material generality. Ranked by severity, each with citation + verdict (defect/risk/open) + recommendation.
3. **Part 2 — Structure/program findings** — the canonical-structure/specialize-down judgment, efficiency, elegance, generality, coverage. Same format.
4. **Part 3 — Additional findings** — the seeded questions + your own.
5. **The accuracy/error-model assessment** (question 1) as its own section — it is the linchpin of the whole design bet.
6. **Prioritized recommendations** — what to fix or research next, ordered by impact on (a) accuracy, (b) generality, (c) the closed-form/cheap discipline.

Be concrete, quantitative where possible, and decisive. This audit gates whether the design is ready to build.
