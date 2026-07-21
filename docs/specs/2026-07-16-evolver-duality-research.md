# 2026-07-16 — Research memo: the scorer ↔ stepper duality ("evolver duality")

> **Deliverable of** `[timeline] §2026-07-16 (Wave 2 / evolver)` (independent
> deep-research commission, 2026-07-16). Per the commissioning note this memo **commits to
> nothing**: no atomic-tree edit, no `docs/product.md` edit, no vocabulary change may follow
> before joint review. Structure follows brief §4 exactly: §1 verdict, §2 the algebra, §3 the
> shape of a steppable lowering, §4 refusal cases, §5 integrator-interface proposal, §6 sources.
> Arch citations are by doc id; external claims are grounded in §6. Signature blocks below are
> behavioral contracts in the house idiom (`arch-16-pino-bridge`, `docs/product.md`), not code.

---

## 1. Survivability verdict

**Survives with restrictions.** The restrictions are structural, enumerable, compile-time
decidable, and — the strongest finding of this research — largely coincident with invariants
the architecture already enforces for other reasons. One form of the idea **dies**, and it is
worth recording which: the *strong* reading of "one IR, two interpreters," in which "scorer"
and "stepper" are two algebras over the same term functor, each assigning a local meaning to
every node. That reading is refuted by the formalism it invokes (§2.2). What survives is one
level down and is, on this substrate, unusually strong: a **shared-kernel factorization**.
Every equation-of-motion residual in the IR is already `compare(ẋ-input, RHS-subgraph)`; a
stepper is `advance(state, RHS-subgraph)` over the *same, content-addressed RHS sub-DAG*. One
compile front-end (Stages 1–3), one canonical extraction, two Stage-4 lowerings — the scorer
wraps the RHS in a comparison, the evolver wraps it in a hand-off to time integration. The
"shared state that can be reformed into either form" demanded by the original question is the
RHS forest plus the generator-structure tags, and the sharing is literal: both artifacts
reference the same node addresses under the substrate's identity discipline
(`arch-20-representations §20.4`).

The argument, compressed:

1. **The re-arrangement asked about exists and is thirty years mechanized.** Turning residual
   equation sets into integrable causal form is *causalization* in the acausal-modeling world:
   bipartite matching of equations to unknowns, strongly-connected-component sorting into
   block-lower-triangular (BLT) form, alias elimination, tearing, and structural index
   reduction (Pantelides; dummy derivatives; the Σ-method). These are the production passes of
   Dymola/OpenModelica and of ModelingToolkit's `structural_simplify` (§6 group A). Matching
   and sorting are low-polynomial; optimal tearing is NP-complete but is an optimization, not
   a feasibility, question. The brief's seed claim is verified.
2. **On this IR the machinery mostly *verifies* rather than *repairs*.** The acausal world
   needs heavy causalization because users write arbitrary implicit equations. Here the
   dynamical form is GENERIC (`arch-05-generic`): every EOM-family residual leaf is
   structurally `‖ẋᵢ − (L·δE/δxᵢ + M·δS/δxᵢ)‖²` with the rate estimate an *input* (the
   consumer-supplied trajectory finite-difference — score-not-solve,
   `arch-16-pino-bridge`, `arch-21-multiscale-state §21.4`) and the generator contraction an
   ordinary evaluable sub-DAG the scorer already executes. The matching is forced (each EOM
   leaf to its own ẋᵢ), the mass operator is the identity, and the differentiation index of
   the micro and slow tiers is zero. The genuinely acausal remainder is small and known by
   name: the macro tier's two algebraic rows (`φ`, `j` — `arch-21-multiscale-state §21.9`) and
   every fixed-point / nested-minimization node (§2.5, §2.6).
3. **The strong duality dies exactly where the theory predicts.** Interpreters in the
   initial-algebra / tagless-final sense are compositional: one denotation per op symbol,
   meaning assembled by folding (§6 group C). The scorer, the adjoint, and the cert traversals
   are such folds — which is *why* the pipeline already emits several programs from one graph.
   Causality assignment is not per-node: which equation determines which unknown is a global
   property of the equation-variable incidence structure (a maximum matching). So "stepper" is
   not an interpretation of the IR; it is a *transformation* of the IR (causalization) followed
   by an interpretation of the transformed graph, followed by a temporal unfold. The
   industrial compiler architecture (flatten → match → sort → index-reduce → tear → integrate)
   is the existence proof of this factorization.
4. **The restrictions are the exceptions to step 2**, and each lands on machinery the
   architecture already has: fixed-point nodes step only via per-step solve plans whose
   regularity condition (nonsingular fixed-point Jacobian) is *the same condition* Stage-4
   implicit-differentiation adjoint synthesis already gates on (`arch-07-pipeline §7.4`,
   `impl-07-residual-factory §7.5`); the macro tier steps as a semi-explicit index-1 system
   given the same nonsingularity its committed Scharfetter–Gummel finite-volume discretization
   already assumes; and the non-EOM residual categories never become dynamics at all — they
   re-enter as the *preservation obligations* of structure-preserving integration, keyed by
   the identical `ResidualKey`s the scorer emits (§2.8).
5. **Cost honesty.** A steppable lowering does not inherit the scorer's complexity class. "No
   solver-call hot paths" (`arch-20-representations §20.5`, `arch-18-open-decisions`) is a
   scorer invariant; a stepper for the BO-constrained micro tier pays a T3-class solve per
   step (the classical cost of Born–Oppenheimer dynamics), and the macro tier pays an implicit
   linear solve per step. The evolver is therefore the *trusted-slow sibling* of the fast
   learned evolution the product already delegates to its consumer — not a replacement for it.

Verification of the brief's four seed observations (brief §2 demanded verify-don't-assume):

| Seed claim | Status after research |
|---|---|
| Residuals are structurally `r = LHS(ẋ) − RHS`; causalization is a mechanized pass | **Verified, sharpened**: `LHS` is the identity on an *input* rate estimate for all micro and slow EOM rows; two macro rows carry no `∂_t` at all (algebraic constraints). Causalization is mechanized (§6.A), with named complexity: matching/BLT low-polynomial, tearing NP-complete, structural index analysis cheap but generic-values-only (§4.3). |
| Structured generators are tagged in the IR | **Verified, one caveat**: the reversible/dissipative split, per-tier degeneracy, and target shapes (`AntisymmForm`/`PSDSymmForm`) are IR-visible (`arch-05-generic`, `arch-19-coupling-structure`). Caveat: the Jacobi property of *generated* antisymmetric cross-blocks is only cert-checked numerically, which grades (not blocks) geometric-integrator dispatch (§2.6, §3.4). |
| The pipeline already performs exact rewrites and emits a second program (adjoint); a stepper is a third emission; sibling-artifact identity per `arch-20-representations §20.4` | **Verified**: Stage-3 equality saturation and Stage-4 adjoint synthesis confirmed (`arch-07-pipeline`); `docs/product.md` (landed 2026-07-16) fixes the artifact model — immutable, self-describing, hash-identified oracle-files — and deliberately leaves every time-evolution verb unclaimed pending this memo (its §9). |
| Tiered state ⇒ "steppable" means multi-rate steppable | **Verified, strengthened**: the `arch-21-multiscale-state` adiabatic contract (slow tier driven by time-averaged micro quantities; macro by homogenized coefficient closures) is precisely the heterogeneous-multiscale-method pattern, and the tier design's "no cross-tier constraint manifold" decision means no monolithic cross-tier DAE ever needs to be formed (§3.4). |

---

## 2. The algebra

### 2.1 Three layers, not one

The question asked for "some form of abstract algebra on trees." The research resolves it into
three distinct layers, each with existing, citable theory. Nothing new needs inventing; what
needs deciding is where each layer acts in the pipeline.

- **Term layer** — the op-signature. The IR is the free term structure over
  `S = Input | FormulaApply(132) | MethodInvoke(12)` (`arch-06-physics-graph`), hash-consed
  into a Merkle DAG. An *interpretation* is an S-algebra: one denotation per op, meaning
  assembled by fold (catamorphism; §6.C). The scorer (numeric denotation), the adjoint
  (per-op vJp denotation, composed in reverse), and the cert traversals (evidence-semilattice
  denotation) are all folds. This is the formal reason "several programs from one graph"
  already works.
- **System layer** — the equation–unknown incidence structure. Steppability is a property of
  the *set* of residual leaves against the *set* of state slots: existence of a perfect
  matching, BLT ordering of the induced dependency graph, and a differentiation-index witness
  (Pantelides / Σ-method). This is combinatorial graph algebra on a quotient of the IR, not
  term algebra; it is global by nature.
- **Temporal layer** — recursion direction. Scoring is a fold applied once per supplied
  sample. Stepping is an *unfold* (anamorphism): iterate a one-step map built from the RHS
  fold. The two recursion schemes share the RHS kernel; they differ only in the driver around
  it.

### 2.2 Why the strong form dies

Claim: there is no S-algebra `α_step` such that `fold(α_step)` is a stepper on every graph
where `fold(α_score)` is the scorer.

Argument: a stepper must assign, to each differential slot, the equation that produces its
rate, and to each algebraic unknown, the constraint that determines it. Exhibit two graphs
containing the *same* subterm where any correct assignment differs — e.g. a constraint
subgraph matched to unknown `u` in one composition and to unknown `v` in another (any torn
algebraic loop yields this). A fold gives the subterm one context-independent denotation;
causality is context-dependent. Hence no per-op denotation exists; the obstruction is exactly
the content of the acausal literature's matching pass. Tagless-final formalizes the boundary
cleanly: what varies per interpreter is the per-symbol meaning; whole-program re-arrangement
is outside the formalism's notion of interpretation (§6.C). The conclusion is not a
technicality — it dictates the *architecture* of the surviving design: the stepper cannot be
"another backend for the same nodes"; it must be **a Stage-4 sibling lowering that consumes a
system-layer analysis** (§3.1), exactly as the adjoint is a sibling lowering that consumes
fixed-point facts.

### 2.3 The factorization that survives

For every EOM-family category (9 of 19: the seven micro components plus
`EOM/DefectPopulation`, `EOM/Continuum` — `arch-11-residuals §11.1`,
`arch-21-multiscale-state §21.10`), the residual leaf has the shape

```
residual_i  =  ‖ ẋᵢ-input  ⊖  RHSᵢ(state, env, adiabatic-params) ‖²
```

where `RHSᵢ` is the contraction of the tier's tagged generators (`L·δE/δxᵢ + M·δS/δxᵢ`, or the
master-equation / finite-volume specializations). Define the **causal cut**: delete the
comparison node and the `ẋᵢ-input` leaf; re-root on `RHSᵢ`. Then:

- **scorer** = `compare(ẋ-inputs, fold(RHS-forest))` — the existing kernel;
- **evolver** = `fold(RHS-forest)` re-exported as a tangent map `(state, env, params) → ẋ`,
  handed to a time-integration driver (an unfold) that `/physics` does not own (§5).

Both artifacts share the RHS forest *by address*: the sub-DAG is content-addressed, and the
causal cut removes nodes without rewriting any node below it. Sharing survives compilation
because both lowerings consume the same Stage-3 output (§2.7). This is the precise, surviving
sense of "one structure, reformable into either form."

### 2.4 Re-formability conditions (the algebra the IR must satisfy)

Stated as compile-time-checkable conditions **S1–S6**, per tier. These are the memo's answer
to "the properties the op-signature must satisfy, stated precisely."

- **S1 — explicit comparison form.** Every EOM-family `ResidualLeaf` over tier state slot
  `xᵢ` decomposes at its root as `norm²(ẋᵢ-input ⊖ tᵢ)` where the rate-estimate input occurs
  exactly once, at the cut, and `tᵢ` is rate-free. Generalization admitted by the theory: a
  left operator on the rate that is linear, constant over the trajectory, and nonsingular
  (then `RHS := LHS⁻¹·t`, one compile-time factorization). On the current spec the identity
  form holds for all micro and slow rows by construction (`arch-05-generic`,
  `arch-21-multiscale-state §21.4`).
- **S2 — squareness and matching.** Over the tier, the bipartite incidence of
  `{EOM leaves} ∪ {algebraic-constraint leaves}` versus
  `{differential slots} ∪ {algebraic unknowns}` admits a perfect matching in which each EOM
  leaf matches its own slot (forced by S1) and the algebraic block's matched Jacobian is
  structurally nonsingular — i.e. the tier is a semi-explicit system of differentiation index
  ≤ 1, witnessed by the Σ-method / Pantelides check. The incidence structure needed is a
  byproduct of Stage-3 sparsity inference (`arch-07-pipeline §7.3`); the check is cheap.
- **S3 — solvable interior.** Every node inside the RHS forest is forward-evaluable within
  the evolver's *declared* per-step cost class: T0–T2 unconditionally; any node whose method
  has fixed-point semantics (the Stage-4 lookup fact, `arch-06-physics-graph §6.2`) only via
  an attached per-step solve plan whose regularity condition — nonsingular fixed-point
  Jacobian — is identical to the condition Stage-4 adjoint synthesis already imposes
  (`arch-07-pipeline §7.4`). Differentiability tags do **not** gate the forward lowering
  (stepping needs no adjoint); they gate the evolver's optional tangent/sensitivity sibling.
- **S4 — generator-tag totality.** Every additive block of every `tᵢ` carries one tag from
  the closed generator set the IR already has — canonical-symplectic pair, Lie–Poisson
  density-matrix block, Maxwell block, generated `AntisymmForm` cross-block (with recorded
  Jacobi grade), PSD diagonal / PSD cross dissipative block, master-equation rate generator,
  parabolic finite-volume block (`arch-05-generic`, `arch-19-coupling-structure`,
  `arch-21-multiscale-state`). The tags select the integrator class and the preservation
  obligations (§3.4). An untagged block refuses (none exists in the current spec).
- **S5 — cut stability under rewriting.** Stage-3 equality saturation must not lose the causal
  cut. Two facts make this cheap. (i) Saturation only *adds* nodes to e-classes; the
  compare-form representative demanded by S1 cannot be destroyed by saturation, only by
  *extraction*. (ii) "Rate-free-ness" of a subterm is a finite semilattice fact, so "this
  e-class retains a representative of the form `ẋ ⊖ (rate-free term)`" is expressible as an
  e-class analysis in exactly the egg sense (§6.B), and extraction can be constrained to
  respect it. Additionally, the existing AD-safety bar on rewrites must be read as
  *trajectory-safety*: rewrites exact almost-everywhere but wrong on measure-zero sets (the
  `x/x → 1` family documented in the AD-correctness literature, §6.B) are tolerable for a
  pointwise scorer yet can matter for a flow that crosses or is attracted to the bad set. The
  Stage-3 discipline ("all exact and AD-safe," `arch-07-pipeline §7.3`) already excludes
  these; the evolver adds motivation, not new machinery.
- **S6 — single extraction, shared identity.** Both lowerings must consume **one** canonical
  Stage-3 extraction. Equality saturation deliberately forks identity inside the compile (an
  e-class holds many address-distinct equal terms); if the scorer and evolver extracted
  independently under different cost functions, the shared RHS would denote equal but
  address-distinct forests, silently breaking the sibling-artifact sharing and the kernel
  cache (`arch-07-pipeline §7.6`, `arch-20-representations §20.4`). Rule: one extraction per
  compile; two lowerings of the extracted graph; the evolver artifact's own identity is a new
  domain-separated address family over the same composition fingerprint.

### 2.5 What "index" looks like for this graph class

The differentiation index — the number of differentiations needed to expose an ODE — is the
classical measure of how far a system is from steppable (§6.A). Per tier:

- **Micro tier, dynamic reading (L1 clock):** index 0. All seven EOM rows are explicit; the
  admissibility conditions on the density-matrix slot (trace, spectral bounds —
  `arch-11-residuals §11.1` Positivity/Conservation) are *invariants of the flow*, not
  constraints coupled into it: the reversible block is an isospectral conjugation flow and
  the trace is conserved, so they are preservation obligations (§3.4), not index sources.
- **Micro tier, Born–Oppenheimer reading (L2 clock):** the nested minimization
  `E_BO = min over γ̂` (`arch-08-bo-levels`) makes the electronic slot a quasi-steady-state
  variable: the tier is a singularly perturbed system whose reduced form is a semi-explicit
  **index-1** DAE — differential slots `(R, P, h, Π_h)`, algebraic unknown `γ̂`, constraint
  "inner stationarity," regular exactly when the inner solve's Jacobian is nonsingular (the
  Stage-4 adjoint's own regularity condition; near-singularity = slow self-consistency is the
  shared failure mode). The two readings are two *different matchings of the same graph* —
  causalization is not unique here, and the non-uniqueness is physical (timescale
  separation). A steppable lowering must record which matching it took (§3.2); the
  architecture's adiabatic axiom (`arch-21-multiscale-state §21.0`) makes the reduced reading
  the default.
- **Slow tier:** index 0, stiff. The generator is a master-equation rate structure with
  Arrhenius rates spanning many decades — the stiffness class of exponential/implicit
  integrators, not of index reduction.
- **Macro tier:** semi-explicit **index 1**. Differential slots `(T_L, n, p)`; algebraic rows:
  the elliptic potential constraint (matched to `φ`; regular iff the discretized operator
  with boundary conditions is nonsingular — the standard situation, and the same
  nonsingularity the committed finite-volume discretization assumes) and the flux-closure row
  (matched to `j`, which is *explicitly defined* by the closure — an alias in the Modelica
  sense, eliminable by the existing Stage-3 alias pass, leaving `φ` as the only genuine
  algebraic unknown). Index analysis of exactly this coupled drift-diffusion/potential class
  is established in the device-simulation literature (§6.A). Index > 1 does not arise
  structurally in any committed tier; the S2 witness is still mandated because *generated*
  cross-couplings could in principle create hidden constraints, and because structural
  analysis has known blind spots (§4.3).

### 2.6 Violators, named

Which existing vocabulary entries and graph constructions violate which condition (the brief's
coverage area 6):

| Vocabulary / construction | Condition touched | Consequence |
|---|---|---|
| `Import`-pinned inputs + cert-only `ResidualLeaf` (`arch-16-pino-bridge §16.2`) | none — outside the EOM family | Constants/parameters to the evolver; their reference-check slots never become dynamics. Absent from the steppable form by construction. |
| The 10 non-EOM residual categories (`arch-11-residuals §11.1`) | none — not equations of motion | Never candidates for causalization. `Conservation`/`Positivity`/`Degeneracy` re-enter as preservation obligations; `Algebraic/*`, `Static/*` at most as trajectory monitors (§2.8). |
| `variational-minimization` fixed-point modes (SCF; the L2 nested min), `kinetic-evolution` steady-state modes (BTE-RTA), and the equilibrium/steady-state templates (`SelfConsistentChargeBalanceOf`, `SelfConsistentRenormalizationOf`, `MassActionEquilibriumOf`, `InterfaceEquilibriumOf`, `MicrokineticSteadyStateOf`) | S3 | Steppable **only** with a per-step solve plan (quasi-steady-state / index-1 reading); per-step cost enters the T3 class. Refused when the plan's regularity condition fails — the same failure the adjoint gate already reports. |
| T3 rows generally (4 rows; e.g. the drift-diffusion hydrogen-redistribution row) | S3 | Same: solve-plan-or-absent. |
| D4 surrogate rows (soft convex-hull, Gumbel-Softmax class; 3 rows) | S3/S4 | **Refused inside any RHS**: a surrogate's forward relaxation bias would become model error *of the vector field*, compounding along trajectories; their exact counterparts are nonsmooth/discrete. Witness: the surrogate-validity cert (obligation 9) magnitude. |
| D0 rows (21; integer/categorical) | none for the forward | Evaluable inside an RHS; excluded only from the evolver's optional tangent sibling. The diff-tag axis is orthogonal to steppability — a finding worth recording, since the brief conjectured otherwise. |
| `path-search` method and template (NEB/dimer/string) | S1 | Boundary-value / saddle-search computations, not initial-value flows; no rate input exists. Refused as dynamics; they participate *parametrically* (their barrier outputs feed slow-tier Arrhenius rates). |
| `statistical-sampling` (MC, MD-sampling, kMC) | S1/S4 | The method's semantics is distributional. The V1 evolver class is deterministic ODE/DAE flow; jump-process stepping (kMC) would be a distinct artifact class. Note the slow tier already uses the *mean-field* master-equation ODE, which is steppable. |
| Macro `φ`/`j` algebraic rows (`arch-21-multiscale-state §21.9`) | S2 | Steppable via the index-1 witness; `j` alias-eliminated; `φ` needs one embedded elliptic solve per step (declared in the manifest). |
| `EOM/Z` (chemistry-inactive compositions) | S1 (degenerately) | Identically-zero generator: absent, with "null generator" as the recorded witness. |
| Generated `AntisymmForm` cross-blocks with cert-graded Jacobi status (`arch-05-generic`) | S4 (grade, not violation) | Dispatchable to a Poisson/symplectic integrator only when the Jacobi grade is exact-by-construction; otherwise the block's preservation grade is downgraded in the manifest (the splitting still conserves energy by antisymmetry; the backward-error interpretation weakens). |
| `mesh-interpolation` sub-method and other compile-time interpolators | none | Compile-time table constructions; inside an RHS they are table reads. Unaffected. |

### 2.7 The rewriting substrate (coverage area 3, resolved)

E-graphs remain the right Stage-3 substrate under a two-lowering regime, with two disciplines:

- **Protect the cut in extraction, not in saturation** (S5). Saturation is monotone — it never
  removes the compare-form representative; only extraction chooses representatives. The
  rate-free-ness analysis is a textbook e-class analysis (semilattice facts joined across
  merges, per the egg design, §6.B), and the extraction constraint is local to the residual
  roots. Cost: negligible against Stage 3's existing budget.
- **One extraction, two lowerings** (S6). Never re-saturate or re-extract per artifact.
  Saturation *inside* a compile may fork and re-canonicalize identities freely; the substrate's
  content-address discipline is preserved exactly because e-graph internals never cross the
  Stage-3 boundary (consistent with the V1 rule that e-graphs stay off the runtime path,
  `arch-15-gamma-hat §15.4`). The evolver artifact then shares the scorer's RHS addresses by
  construction, and the sibling relationship is a filesystem-level fact
  (`docs/product.md` identity model; `arch-20-representations §20.4` domain separation for the
  new artifact family).

AD-safety interacts once more: the adjoint of the *evolver* (sensitivities of trajectories)
is **not** the scorer's adjoint — trajectory sensitivities require forward/adjoint
sensitivity analysis threaded through the integrator (a consumer concern under §5), while the
scorer's cotangents remain per-sample. No rewrite-soundness condition beyond exactness is
added by the evolver itself (§2.4 S5).

### 2.8 The duality's second half: what the stepper must *preserve* is what the scorer *checks*

The clean surprise of the fit analysis: the 10 non-EOM categories do not disappear from the
evolver story — they become its obligations, under the *same keys*.

- `Conservation` slots ↔ first integrals the integrator must conserve (exactly where the
  splitting conserves them; by discrete-gradient or projection steps elsewhere; §3.4).
- `Positivity` slots ↔ bounds the integrator must maintain (isospectral stepping preserves the
  density-matrix spectral bounds exactly; concentrations and occupations need
  positivity-preserving schemes or projection; the closure bound `T_e ≥ T_L` is inherited from
  the closure form).
- `Degeneracy` (cert-only, identically zero by construction, `arch-05-generic`) ↔ the
  *license* for reversible–irreversible splitting: because `L·δS = 0` and `M·δE = 0` per tier,
  the L-subflow conserves both generators' Lyapunov structure and the M-subflow conserves
  energy while producing entropy — each subflow inherits the full GENERIC structure, which is
  precisely the property the GENERIC-integrator literature builds on (§6.D).
- `Algebraic/*`, `Static/*` ↔ trajectory monitors at most (properties of solutions and
  materials, not of the flow).

Behavioral consequence: the scorer is the evolver's *auditor*. Scoring an evolver-produced
trajectory with the existing oracle-file measures exactly the drift the integrator failed to
prevent, slot by slot, with no new machinery. The duality is thus two-sided: shared RHS
downward (§2.3), shared obligation keys upward. This is the strongest architectural argument
that the two artifacts belong to one compile.

One contract note: `CategoryTag` facets are deliberately non-semantic for the training
consumer (`arch-11-residuals §11.2`). The evolver lowering must *read* the category facet at
compile time (to partition EOM vs obligation vs monitor). Facets are compile-visible sidecar
data, so this is legal today; it should be recorded as a facet-consumer when the lowering is
specified.

---

## 3. The shape of a steppable lowering (behavioral; a possible spec addition)

### 3.1 Placement: a Stage-4 sibling emission, not a second pipeline

Stages 1–3 are shared verbatim — S6 *requires* it, and everything the lowering consumes
(pruned graph, symmetry sidecar, invariant sidecar, sparsity/incidence, category facets,
fixed-point facts) already exists at Stage 4. Stage 4 gains one concurrent decision cluster
beside compression-plan selection, adjoint synthesis, and codegen (`arch-07-pipeline §7.4`):

- **causalization audit** — check S1–S4 per tier over the extracted graph; compute the
  matching, the alias eliminations, the index witness, and the per-block generator tags;
- **evolver codegen** — emit the tangent kernel(s) and the manifest below; record refusals.

Runs only when requested (a compile flag): compositions that never ask for an evolver pay
nothing.

### 3.2 Artifacts

One **evolver-file** per composition, the sibling of the oracle-file, mirroring the product's
four-part artifact anatomy (`docs/product.md`):

1. **The callable(s)** — per steppable tier: a pure tangent map
   `(state_tier, env, adiabatic-params) → tangent_tier`, plus separately addressable
   generator sub-entries — the energy and entropy functionals, their derivative maps, and the
   `L·`/`M·` contraction blocks. The sub-entries matter: degeneracy-respecting and
   discrete-gradient integrators consume the *generators*, not just their assembled
   contraction (§3.4); all six are existing interior nodes, so exposing them is
   role-promotion, not new computation. Optionally a tangent-linearization entry (for
   implicit stepping) — reusing the same per-op derivative machinery as the scorer's adjoint.
2. **The steppable-form manifest** (the static schema of this artifact): per tier — coverage
   (which state slots re-formed), the chosen matching (e.g. the L2 reading: dynamic vs
   quasi-steady electronic slot), the index witness, per-block generator tags with
   preservation grades, the obligation map (`ResidualKey → conserve | bound | monotone`),
   embedded solve plans with their regularity conditions and per-step cost class, the cadence
   contract (tier clock; which time-averaged micro quantities and homogenized coefficient
   closures it reads — the `arch-21-multiscale-state §21.5/§21.8` contracts, reified), and
   the **refusal ledger** (§4).
3. **Identity** — content hash in a new domain-separated address family
   (`arch-20-representations §20.4`), stamped with the same composition fingerprint and
   registry/spec versions as its scorer sibling; immutable, like every artifact.
4. **Certificate reference** — hash-pinned evidence for the new obligation this artifact
   introduces (below).

### 3.3 Contracts and invariants

- **Scorer–evolver exactness.** For every steppable EOM key:
  `residual(state, env, ẋ) = ‖ẋ − tangent(state, env, params)‖²` up to serializer/float
  normalization — testable mechanically by evaluating both siblings on sampled states,
  exactly the differential-golden-test pattern already guarding the Stage-4→Stage-5 seam
  (`arch-18-open-decisions`). This is the new cert obligation: **the evolver never introduces
  a second truth**; it re-exposes the scorer's RHS.
- **Score-not-solve is preserved where it lives.** The product still never fills in state,
  never owns a loop, never evolves anything (`docs/product.md` §8; `arch-01-purpose`). The
  tangent map is a per-call pure readout — "the instantaneous lawful tendency at the supplied
  state" — not a trajectory. Integration is the consumer's (§5).
- **Cost classes are declared, not inherited.** The scorer's `O(log n)`-hot-path/no-solver
  invariants are *scorer* invariants. The evolver manifest declares per-step cost per tier:
  slow tier T0–T1 per step (cheap — its RHS rows are closed forms); macro tier one implicit
  finite-volume solve per step; micro tier either stiff-explicit at femtosecond scale (pure
  L1 reading) or a T3-class solve per step (Born–Oppenheimer reading — the classical cost,
  §6.E). No claim of training-loop compatibility is made or implied.
- **Erasure discipline unchanged.** Sidecars are consumed at Stage 4 and erased; the manifest
  is compile *output* (like the kernel), not a retained sidecar.
- **Immutability / attribution.** New registry version, new pins, new identity ⇒ new sibling
  pair; the two files cross-reference by fingerprint, so "which oracle audits this evolver"
  is a filesystem fact.

### 3.4 What integration consumes from the tags, and what it must preserve (coverage area 5)

Behavioral findings from the structure-preserving-integration literature (§6.D–E), stated as
manifest requirements rather than method choices:

- **The reversible/irreversible split is the master structure.** GENERIC integrators split
  the flow into the L-generated and M-generated subflows; the per-tier degeneracy conditions
  are exactly what make each subflow inherit both structures (energy conserved; entropy
  non-decreasing), so composition (e.g. Strang) preserves both to the splitting order. The
  subtlety documented in that literature — naive splitting satisfies the degeneracy
  conditions only approximately, repaired by constructing the dissipative step against a
  modified energy — is the reason the manifest must expose `δE`/`δS` and the `L·`/`M·` blocks
  separately (§3.2 item 1), not only their sum.
- **Per-block dispatch is compilable from existing tags**: canonical-symplectic pairs →
  symplectic stepping; the density-matrix Lie–Poisson block → unitary/isospectral stepping
  (preserving the spectral admissibility bounds and the trace *exactly*, i.e. several
  Positivity/Conservation obligations for free); PSD dissipative blocks → gradient-flow /
  discrete-gradient stepping with guaranteed entropy monotonicity; master-equation generators
  → exponential or implicit stiff stepping with positivity preservation; macro parabolic
  blocks → implicit finite-volume steps on the committed Scharfetter–Gummel fluxes.
- **Exactness where cheap, projection where not.** Discrete-gradient methods make energy
  conservation / entropy production exact per step; linear invariants (trace, charge) are
  conserved by the split flows; remaining invariants get projection steps whose *targets are
  the existing Conservation/Positivity keys* (§2.8).
- **Multi-rate is tier-structured, not monolithic.** The tier design already commits the
  coupling pattern: slow reads time-averaged micro quantities (the
  heterogeneous-multiscale-method estimator pattern), macro reads per-cell homogenized
  closures, micro reads slow/macro as adiabatic parameters. So the evolver never forms one
  cross-tier system — it emits one steppable form per tier plus the coupling contract, and
  the multirate order theory (MRI-GARK class) applies when a consumer steps two tiers
  numerically at once. This preserves the `arch-21-multiscale-state` no-cross-tier-DAE
  design decision at the dynamics level.

### 3.5 Scope recommendation (V-ordering, not a commitment)

The value-to-cost ordering is unambiguous from the research: **slow tier first** (its RHS rows
are T0/T1 closed forms; stiffness is handled by standard implicit/exponential steppers; it is
the product's lifetime/degradation story — the capability `docs/product.md` §6 explicitly
could not claim), **macro tier second** (index-1, committed discretization, one embedded
solve per step), **micro tier last and restricted** (Born–Oppenheimer reading = solve-per-step
cost; pure-L1 reading = femtosecond stiffness; both honest but expensive; the learned operator
remains the product's fast-evolution answer).

---

## 4. Refusal cases

### 4.1 The principled rule

> A subgraph re-forms into the steppable lowering **iff** it lies in the image of the EOM
> factorization with witnesses — S1 (comparison form) and S4 (tagged generators) locally, S2
> (matching + index ≤ 1) at its tier, S3 (solve plans with regular Jacobians) for its
> interior. Everything else is **absent** from the evolver artifact, and the absence is
> accounted for: a closed-enum refusal mode plus a numeric or structural witness in the
> manifest's refusal ledger — no prose, no runtime error, no partial dynamics.

This is the product's existing refusal semantics (`docs/product.md` §4 "refusal is absence";
`arch-12-cert`) applied to a second artifact: refusal modes are enum codes; witnesses are
machine data (the deficient matching's unmatched rows, the offending node address, the
singular-Jacobian sample, the surrogate-bias magnitude).

### 4.2 Refusal classes (closed enumeration, from §2.6)

1. **`not-dynamics`** — cert-only `Import` bridges; the 10 non-EOM categories; pure readouts.
   Absent by construction; not recorded as failures (they are not candidates). The
   obligation/monitor re-entry of Conservation/Positivity/Degeneracy is recorded on the
   *steppable* side (§2.8), not in the refusal ledger.
2. **`no-rate-form`** — leaves failing S1: boundary-value producers (`path-search`),
   distributional producers (`statistical-sampling`), identically-null generators (`EOM/Z`
   when chemistry-inactive). Witness: producer id + the missing-rate-input fact.
3. **`unmatched-or-high-index`** — tier fails S2: matching deficiency or index witness > 1.
   Whole-tier refusal (a partial tier would be a lie), witness: the deficient rows and the
   Σ/Pantelides certificate. Not expected for any committed tier (§2.5); the gate exists for
   generated couplings and future tiers.
4. **`solve-plan-unavailable`** — fixed-point interior node with no regular plan (singular or
   near-singular fixed-point Jacobian at sampled states — the adjoint gate's failure mode,
   shared). Witness: the sampled conditioning number, τ-thresholded like the existing
   registration gates (`impl-07-residual-factory §7.5` pattern).
5. **`surrogate-in-rhs`** — D4 rows inside a would-be RHS. Witness: the obligation-9
   validation error magnitude.
6. **`structure-grade-degraded`** — not a refusal but a grade: generated `AntisymmForm`
   blocks whose Jacobi status is numerical-only; recorded per block so a consumer knows which
   preservation claims are exact and which are cert-graded (§2.6).
7. **`out-of-class`** — stochastic/jump dynamics (kMC) and any future non-deterministic-flow
   request: a different artifact class, deliberately unclaimed by this lowering (mirrors the
   product's deliberate-non-claim discipline).

Complexity honesty: every check above is polynomial (matching, SCC/BLT, Σ-certificate,
sampled numerical gates); the one NP-hard neighbor — optimal tearing — is an *efficiency*
optimization inside solve plans, where a heuristic tearing is admissible and its quality only
moves per-step constants, never feasibility (§6.A).

### 4.3 The structural–numerical gap (a known failure mode, gated)

Structural index analysis is generic-values analysis: it can pass while the actual Jacobian is
singular at the operating point (and, rarely, misjudge the index — the documented
success-check failures and their conversion repairs, §6.A). Mechanized practice (ModelingToolkit
docs, §6.A) hits exactly this as "singular mass/Newton matrices." Consequence for the spec
sketch: the S2/S3 witnesses must be **paired with sampled numerical spot-checks** at
registration/compile time — the same philosophy as the existing adjoint consistency gate — and
failures refuse loudly (classes 3/4 above), never degrade silently.

---

## 5. Proposed resolution of the integrator-interface open decision

`arch-18-open-decisions` item 5 asks for "the exact signature `dynamics` exposes to
`/informed-operator` for handing off the assembled GENERIC right-hand side." Conditional on
the §1 verdict, the research supports resolving it as follows.

**Proposal.** `dynamics` is the **evolver-file hand-off**, per tier — the causalized tangent
kernel plus the steppable-form manifest — and *not* an integrator:

```
dynamics(tier) →
    tangent      : (state_tier, env, adiabatic-params) → tangent_tier
    generators   : { E, S, δE/δx, δS/δx, L·(·), M·(·) }      -- addressable sub-entries
    constraints  : algebraic subsystem + solve plans + index witness
    structure    : per-block generator tags + preservation grades
    obligations  : Map<ResidualKey, conserve | bound | monotone>
    cadence      : tier clock + coupling contract (averaging / homogenization / adiabatic reads)
    cost         : declared per-step class + embedded-solve declarations
    identity     : sibling fingerprint + certificate reference
```

`/physics` guarantees: exactness against the scorer sibling (§3.3), tag totality, index
witnesses, declared costs, refusal accounting. The consumer — `/informed-operator`, a
classical-integration harness in `/interface`, or a person's program — owns step-size control,
scheme choice, and the loop. This keeps every `docs/product.md` §1/§8 principle intact
(score-not-solve; no loop ownership; evidence-never-verdicts extends to "tendencies, never
trajectories") while making the hand-off *sufficient for structure preservation*, which an
opaque RHS closure is not: the research is unambiguous that degeneracy-respecting,
entropy-monotone, bound-preserving integration must consume the generators, the split, and
the obligations — precisely the fields above (§3.4, §6.D).

**Rejected alternatives.** (a) *Opaque RHS closure only*: discards the structure tags and
obligations; a consumer integrator can then silently violate the invariants the scorer will
later flag — the one outcome the product's evidence discipline exists to prevent. (b)
*`/physics` ships the integrator / a rollout verb*: contradicts `docs/product.md` §8 ("never
evolves anything, owns no loop") and would import step-size policy — a judgment — into a
product that renders none. If the product ever claims time-evolution *verbs* (its §9 item 1),
they belong in `/interface` as compositions over this hand-off, with the scorer auditing the
produced trajectories (§2.8). (c) *Defer entirely*: the interface is the one committed
consumer of this research (`docs/product.md` §9 names it), and the manifest fields above are
exactly what §2–§4 showed to be necessary and compile-time available; deferral would buy no
information.

**Non-commitment.** Per the commissioning note, this section is a proposal for joint review;
no arch edit accompanies this memo.

---

## 6. Sources

Primary papers and canonical tool documentation only; grouped by coverage area. Repo documents
cited throughout by id (`arch-xx`, `impl-xx`, `docs/product.md`, `docs/computational-overview.md`).

**A. Acausal model compilation, causalization, and DAE structural analysis**

- C. C. Pantelides, "The consistent initialization of differential-algebraic systems,"
  *SIAM J. Sci. Stat. Comput.* 9(2):213–231, 1988. (Graph-based detection of hidden
  constraints; the structural index-reduction pass named in the brief.)
- S. E. Mattsson, G. Söderlind, "Index reduction in differential-algebraic equations using
  dummy derivatives," *SIAM J. Sci. Comput.* 14(3):677–692, 1993. (Differentiate-and-replace
  repair producing an at-most-index-1, non-overdetermined system; the standard production
  pass.)
- J. D. Pryce, "A simple structural analysis method for DAEs," *BIT Numerical Mathematics*
  41(2):364–394, 2001. (The Σ-method: signature-matrix assignment problem; the cheap
  compile-time index witness proposed in §2.4 S2.)
- G. Tan, N. S. Nedialkov, J. D. Pryce, "Conversion methods for improving structural analysis
  of differential-algebraic equation systems," *BIT Numerical Mathematics* 57:845–865, 2017.
  (Documented failure cases of structural analysis and their repairs; grounds §4.3.)
- H. Elmqvist, M. Otter, "Methods for tearing systems of equations in object-oriented
  modeling," *Proc. European Simulation Multiconference (ESM'94)*, 1994. (Tearing as used in
  Dymola-class compilers.)
- A. Baharev, A. Neumaier, H. Schichl, "Failure modes of tearing and a novel robust approach,"
  *Proc. 12th Int. Modelica Conference*, 2017; and R. M. Karp, "Reducibility among
  combinatorial problems," 1972 (minimum feedback set NP-completeness, the reduction behind
  minimum-tearing hardness). (Grounds §4.2's complexity honesty.)
- A. Benveniste et al., "The mathematical foundations of physical systems modeling languages,"
  arXiv:2008.05166. (Synthesis of matching/BLT/index machinery as compiler passes.)
- Y. Ma, S. Gowda, R. Anantharaman, C. Laughman, V. Shah, C. Rackauckas, "ModelingToolkit: a
  composable graph transformation system for equation-based modeling," arXiv:2103.05244, 2021;
  and ModelingToolkit.jl documentation, "Automated index reduction of DAEs" (SciML docs,
  accessed 2026-07-16 — names the Pantelides pass; documents the singular-Jacobian failure
  mode of un-reduced stepping). (The closest living one-front-end/many-lowerings system.)
- M. Bodestedt, C. Tischendorf, "PDAE models of integrated circuits and index analysis,"
  *Math. Comput. Model. Dyn. Syst.* 13(1):1–17, 2007. (Index analysis of coupled
  drift-diffusion/potential systems; precedent for §2.5's macro-tier claim.)

**B. Rewriting substrates**

- M. Willsey, C. Nandi, Y. R. Wang, O. Flatt, Z. Tatlock, P. Panchekha, "egg: fast and
  extensible equality saturation," *Proc. ACM Program. Lang.* 5(POPL):23, 2021. (E-class
  analyses — the mechanism behind §2.4 S5's cut-preservation constraint; rebuilding;
  extraction.)
- W. Lee, H. Yu, X. Rival, H. Yang, "On correctness of automatic differentiation for
  non-differentiable functions," *NeurIPS* 2020. (The measure-zero pathology class behind the
  trajectory-safety reading of AD-safe rewrites, §2.4 S5.)

**C. One-IR-many-interpreters formalisms**

- E. Meijer, M. Fokkinga, R. Paterson, "Functional programming with bananas, lenses,
  envelopes and barbed wire," *FPCA* 1991. (Catamorphisms/anamorphisms; the fold/unfold
  factorization of §2.1/§2.3.)
- J. Carette, O. Kiselyov, C.-c. Shan, "Finally tagless, partially evaluated: tagless staged
  interpreters for simpler typed languages," *J. Funct. Program.* 19(5):509–543, 2009; O.
  Kiselyov, "Typed tagless final interpreters" (lecture notes). (Interpreters as per-symbol
  algebras; the formal boundary used in §2.2.)

**D. GENERIC / metriplectic structure-preserving integration**

- M. Grmela, H. C. Öttinger, "Dynamics and thermodynamics of complex fluids. I/II," *Phys.
  Rev. E* 56:6620–6632 and 6633–6655, 1997. (The two-generator form and the degeneracy
  conditions the IR's tags encode.)
- H. C. Öttinger, "GENERIC integrators: structure preserving time integration for
  thermodynamic systems," *J. Non-Equilib. Thermodyn.* 43(2):89–100, 2018
  (doi:10.1515/jnet-2017-0034). (What an integrator must consume/preserve from the
  two-generator structure.)
- X. Shang, H. C. Öttinger, "Structure-preserving integrators for dissipative systems based
  on reversible–irreversible splitting," *Proc. R. Soc. A* 476:20190446, 2020. (Splitting;
  the modified-energy/modified-friction repair of approximate degeneracy — the reason §3.2
  exposes generators separately.)
- R. I. McLachlan, G. R. W. Quispel, N. Robidoux, "Geometric integration using discrete
  gradients," *Phil. Trans. R. Soc. A* 357(1754):1021–1045, 1999. (Exact discrete energy
  conservation / Lyapunov-monotone dissipative integration; §3.4.)
- E. Hairer, C. Lubich, G. Wanner, *Geometric Numerical Integration*, 2nd ed., Springer,
  2006. (Symplectic methods, splitting, projection onto invariants — the projection-step
  obligations of §3.4.)
- S. Blanes, F. Casas, J. A. Oteo, J. Ros, "The Magnus expansion and some of its
  applications," *Phys. Rep.* 470(5–6):151–238, 2009. (Unitary/isospectral integration of the
  Lie–Poisson block; exact preservation of spectral admissibility bounds, §3.4.)

**E. Multirate, multiscale, stiffness, and the micro-tier cost classes**

- A. Sandu, "A class of multirate infinitesimal GARK methods," *SIAM J. Numer. Anal.*
  57(4):2300–2327, 2019 (doi:10.1137/18M1205492); M. Günther, A. Sandu, "Multirate
  generalized additive Runge–Kutta methods," *Numer. Math.* 133:497–524, 2016. (Order theory
  for coupled fast/slow stepping; §3.4.)
- W. E, B. Engquist, "The heterogeneous multiscale methods," *Commun. Math. Sci.*
  1(1):87–132, 2003. (Macro-solver-with-micro-estimator; the pattern the
  `arch-21-multiscale-state` adiabatic contract instantiates.)
- M. Hochbruck, A. Ostermann, "Exponential integrators," *Acta Numerica* 19:209–286, 2010.
  (The stiffness class of the slow tier's Arrhenius rate structure.)
- R. Car, M. Parrinello, "Unified approach for molecular dynamics and density-functional
  theory," *Phys. Rev. Lett.* 55:2471, 1985. (The fictitious-dynamics alternative to
  per-step inner solves — cited in §2.5/§2.6 as a *generator rewrite*, i.e. a different
  dynamical system, hence outside a lowering's scope; its existence delimits what "lowering"
  may honestly claim.)
