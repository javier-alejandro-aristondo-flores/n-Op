# Disposition — oracle/compilation

Scope: `journal/pages/04-pipeline-and-compilation/` — `4.1-physics-graph.md`,
`4.2-compose-time-pipeline.md`, `4.3-representation-substrate.md`,
`4.4-computational-overview.md` (12,046 words total; 4.4 alone is 6,475).
Read at: 2af93d2

**Checker calibration performed** (§ "Notes for Phase 2" → *Calibration*). Five
defect classes central to this fragment were proved **uncheckable** by
`check_book_structure.py`. No claim below rests on a green run.

---

## Disposition rows

Targets use `journal/section/page#anchor`. Anchor slugs are proposals.

**Coverage.** All 54 heading-level blocks across the four pages appear in exactly
one row (4.1: 7, 4.2: 8, 4.3: 12, 4.4: 27). Split rows are added wherever a
block contains a fact whose target differs from the block's own; those cite a
line range rather than an anchor. Source anchors here are abbreviated
GitHub-style slugs of the *current* headings — they are locators, not proposals.

### 4.1-physics-graph.md → `oracle/compilation/physics-graph`

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 1 | `authority: canon`, `content-hash: f2084f41fb88` | `4.1-physics-graph.md:4-5` | delete | — | D3/§4 delete the `authority` tier and `content-hash`. Calibration proved the hash actively *masks* other defects (Notes → Calibration) |
| 2 | `canonical-for: PhysicsGraph schema / NodeKind, OutputRole, ResidualKey / per-stage sidecars` | `4.1-physics-graph.md:6-9` | keep | `oracle/compilation/physics-graph` frontmatter `owns:` | three topics, none identical to the id — this page is **not** vacuous; one of the good examples to pattern the other 18 on |
| 3 | The `PhysicsGraph` is the single data structure everything in `/physics` is a view of | `4.1-physics-graph.md#the-physicsgraph` (43-57) | keep | `oracle/compilation/physics-graph#the-graph` | sole statement; 14 pages list it in `referenced-by` |
| 4 | `Node` = 4 fields (`id`, `type`, `kind`, `role`); decorations live in sidecars, not on the node | `4.1-physics-graph.md#1-anatomy-of-a-node` | keep | `oracle/compilation/physics-graph#node` | sole normative statement of node anatomy |
| 5 | `NodeKind` is the substrate's primary closed-polymorphism mechanism; graph identity = closure of output `Address[GraphNode]` multiset | `4.1-physics-graph.md:81-88` | keep | `oracle/compilation/physics-graph#node` | restated at `4.3:143` and `4.3:311-316` — **duplicate pair**, keep here (topic owner), delete the 4.3 copy (row 47) |
| 6 | The three node kinds; `InputKind = StateSlot \| EnvScalar(EnvField)` | `4.1-physics-graph.md#2-the-three-node-kinds` | keep | `oracle/compilation/physics-graph#node-kinds` | sole statement |
| 7 | **`EnvField` is used and never defined** | `4.1-physics-graph.md:98` | move | `oracle/state/crystal-inputs#environment` | homeless — see Open questions `environment-record`. No page's `canonical-for` claims it; only other mentions are `11.8:269`, `11.8:580` (a page being deleted) |
| 8 | Symmetry projection / fixed-point solves / observables+residuals are **not** additional node kinds | `4.1-physics-graph.md:110-123` | keep | `oracle/compilation/physics-graph#node-kinds` | negative-space statement; sole source. High value — prevents re-proposal |
| 9 | `OutputRole = Internal \| Observable(BundleId) \| ResidualLeaf(ResidualKey)` and what each exposes | `4.1-physics-graph.md#3-output-role` | keep | `oracle/compilation/physics-graph#output-role` | sole statement |
| 10 | Per-stage sidecar list + `CompressionPlan` family; sidecars are not hash-consed and do not survive their last consumer | `4.1-physics-graph.md#4-per-stage-sidecars` | keep | `oracle/compilation/physics-graph#sidecars` | sole *definition*; restated verbatim at `4.4:296-307` (row 78) |
| 11 | Stage-visibility poset `1 < 2 < 2.5 < 3 < 4 < 5` | `4.1-physics-graph.md:145-147` | delete | — | duplication: stated three times (`4.1:146`, `4.3:304`, `4.4:298`). Keep the `4.3` statement (row 46), which owns the substrate's attachment discipline |
| 12 | "The graph *is* every other vocabulary" — 13-row realization table | `4.1-physics-graph.md#5-the-graph-is-every-other-vocabulary` | keep | `oracle/compilation/physics-graph#vocabulary-realization` | sole cross-map from every closed vocabulary to its graph realization. Load-bearing for the closure argument |
| 13 | BO level is "derivable from a node's transitive inputs; **not stored**" | `4.1-physics-graph.md:179` | keep | `oracle/compilation/physics-graph#vocabulary-realization` | restated `4.4:252`; this is the owning page (row 71 deletes the 4.4 copy) |
| 14 | Why it is *the* data structure — closure / composition / correctness / performance / substrate-agnosticism | `4.1-physics-graph.md#6-why-it-is-the-data-structure` | keep | `oracle/compilation/physics-graph#why-one-structure` | rationale, present-tense, no history markers |
| 15 | Closing analogy: graph : `/physics` :: relational schema : database | `4.1-physics-graph.md:208-211` | keep | `oracle/compilation/physics-graph#why-one-structure` | the single best one-line framing in the chapter |
| 16 | 44 backticked cross-refs, **0 bracketed** | `4.1-physics-graph.md` (whole) | move | one citation syntax `[id#anchor]` per §4 | 100% of this page's references are in the syntax calibration proved unchecked |

### 4.2-compose-time-pipeline.md → `oracle/compilation/compose-time-pipeline`

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 17 | `authority`, `content-hash: 909aad6a17d6` | `4.2:4-5` | delete | — | D3/§4 |
| 18 | `canonical-for: 4+1 stage compose-time pipeline / always-cheap discipline / stage boundaries` | `4.2:6-9` | move | `oracle/compilation/compose-time-pipeline` frontmatter `owns:` | topic 1 carries the nomenclature defect (Contradictions row C1); topics 2–3 are sound. **Do not rename** — proposal only, per §4 |
| 19 | One residual surface, one stack, one fidelity; cost bounded by compose-time specialization | `4.2#the-compose-time-pipeline` (50-54) | keep | `oracle/compilation/compose-time-pipeline#always-cheap` | the always-cheap discipline's own statement; cited by `architectural-principles` p1 |
| 20 | Everything before Stage 5 runs once per `(PeriodicityStructure, SiteDecoration, Environment)` tuple | `4.2:56-60` | keep | `oracle/compilation/compose-time-pipeline#always-cheap` | sole statement of the recompile unit |
| 21 | Stage 1 — symbolic lift: inputs, template instantiation, applicability pruning, sidecar discarded | `4.2#1-stage-1-symbolic-lift` | keep | `oracle/compilation/compose-time-pipeline#stage-1` | sole normative statement |
| 22 | Stage 2 — symmetry quotient: block-diagonalization + IBZ orbit collapse, up to 48× in cubic | `4.2#2-stage-2-symmetry-quotient` | keep | `oracle/compilation/compose-time-pipeline#stage-2` | sole normative statement |
| 23 | Stage 2.5 — invariant synthesis: per-channel generator run, `GeneratorOutput` sidecar | `4.2#25-stage-25-invariant-synthesis` | keep | `oracle/compilation/compose-time-pipeline#stage-2-5` | sole statement of 2.5 *as a pipeline stage*; the generator itself is owned by `coupling-structure §3` |
| 24 | `InvariantTerm` is the constructive dual of an irrep-block decomposition — same machinery as §2, used to build rather than decompose | `4.2:114-116` | keep | `oracle/compilation/compose-time-pipeline#stage-2-5` | sole statement; explains why 2.5 is a sub-stage of 2 rather than a peer. **This is the argument that justifies the "2.5" name** — load-bearing for C1 |
| 25 | Stage 3 — the three rewrites (hash-consing, cross-formula CSE, tearing/alias elimination) | `4.2#3-stage-3-algebraic-simplification` | keep | `oracle/compilation/compose-time-pipeline#stage-3` | sole normative statement |
| 26 | Why only three; exactness is not a property of the rewrite *system* | `4.2:139-143` | keep | `oracle/compilation/compose-time-pipeline#rewrite-admission` | sole statement; the premise of the admission rule |
| 27 | **Rewrite-admission rule (normative), 3 conditions** | `4.2:145-154` | keep | `oracle/compilation/compose-time-pipeline#rewrite-admission` | the live guard that closed γ̂ question 1. Present-tense fact — keep per brief exception 1 |
| 28 | Equality saturation stays an **offline** rewrite oracle | `4.2:156-158` | keep | `oracle/compilation/compose-time-pipeline#rewrite-admission` | restated `gamma-hat:139-141`, `4.4:235`; this is the owning page |
| 29 | Herbie/egglog evidence: unsound rules, 289 benchmarks, 104 wins vs **135** losses, soundness affordable not free | `4.2:160-173` | keep | `oracle/compilation/compose-time-pipeline#rewrite-admission` | the external evidence the rule rests on. Keep the numbers; they are the reason condition 2 is written as it is |
| 30 | "(This corpus quoted the 104 without the 135 until 2026-07-22, which turned an even trade into a win.)" | `4.2:173` | delete | — | history of a corrected error → Log-worthy L1. The *corrected* claim survives in row 29 |
| 31 | The e-graph community arrived at the same exact-identity/ε-alongside separation independently | `4.2:175-178` | move | `oracle/compilation/representation-substrate#identity-exact` | belongs beside the separation it corroborates. **Carries a retired coordinate `§20.4.1`** — re-anchor to `#identity-exact` (Contradictions C2) |
| 32 | `[traps] §50` — rewrite exact almost-everywhere is tolerable for a scorer, not for a flow | `4.2:180-184` | keep | `oracle/compilation/compose-time-pipeline#rewrite-admission` | a live hazard (brief exception 2); consumer-side under the scorer-only decision |
| 33 | Stage 3 preserves granularity — sharing upstream nodes does not collapse `ResidualLeaf` keys | `4.2:186-189` | keep | `oracle/compilation/compose-time-pipeline#stage-3` | sole statement of the interaction between CSE and granularity |
| 34 | Stage 4 — compression-plan selection; **each plan carries a per-plan error target**, rank chosen to meet it | `4.2:195-204` | keep | `oracle/compilation/compose-time-pipeline#stage-4` | the error-target refinement is original here and feeds `Quantity.combineTol` |
| 35 | Stage 4 — implicit-differentiation adjoint; one extra linear *system*, **not `O(1)` work**; Blondel et al. 2022 | `4.2:205-213` | keep | `oracle/compilation/compose-time-pipeline#stage-4` | the qualification is precise here and **dropped** in `4.4:370-373` (Contradictions C5) |
| 36 | Stage 4 — adjoint-tape materialization schedule; `revolve` optimal on a chain, **NP-complete on a DAG** (Naumann 2009) | `4.2:214-223` | keep | `oracle/compilation/compose-time-pipeline#stage-4` | resolution of γ̂ question 2, stated on the owning page |
| 37 | This lowering **owes no fidelity generator** — it marks the boundary of the ε rule (value, not cost) | `4.2:223-229` | keep | `oracle/compilation/compose-time-pipeline#stage-4` | negative-space guard; sole statement |
| 38 | "(This was previously carried as an open data-structure problem … in `gamma-hat §4`. It was misfiled …)" | `4.2:230-233` | delete | — | history of a reclassification → Log-worthy L3. The disposition itself survives in row 36 |
| 39 | Stage 4 — codegen: one entry, four typed exits | `4.2:234-238` | keep | `oracle/compilation/compose-time-pipeline#stage-4` | sole statement |
| 40 | Stage 4 sidecars are codegen inputs, erased after codegen | `4.2:240-242` | delete | — | duplication of `4.1:167-168` (row 10), which owns sidecar lifecycle |
| 41 | Stage 5 — runtime kernel application; `evaluate` signature with 4 outputs | `4.2#5-stage-5-runtime-kernel-application` | keep | `oracle/compilation/compose-time-pipeline#stage-5` | the raw kernel primitive; `pino-bridge §1` wraps it |
| 42 | The PINO sees the graph only through `ResidualKey` hashes; loss aggregation lives in `/informed-operator` | `4.2:262-264` | keep | `oracle/compilation/compose-time-pipeline#stage-5` | module-boundary statement; restated `4.4:498`, `cross-cutting-rules §3` |
| 43 | Compose-time/runtime boundary table (6 rows: stage · runs · cost · output) | `4.2#6-the-compose-time--runtime-boundary` | keep | `oracle/compilation/compose-time-pipeline#boundary` | **enumerates six stages under a "4+1" label** — the defect's clearest instance (C1) |
| 44 | Composition fingerprint keys a kernel cache; scalar env params are runtime inputs, not recompile triggers | `4.2:277-281` | keep | `oracle/compilation/compose-time-pipeline#boundary` | sole statement; restated `4.4:589-591` (row 88). **Depends on an undefined structural/scalar split of `Environment`** — Open questions `environment-record` |
| 45 | **Runtime cost is three-class, not one** — per-sample core / on-request spectral / per-composition reference | `4.2:283-294` | keep | `oracle/compilation/compose-time-pipeline#boundary` | corrects the single "µs–ms" figure in the row above it; sole statement |

### 4.3-representation-substrate.md → `oracle/compilation/representation-substrate`

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 46 | `authority`, `content-hash: 2e06544bce5b` | `4.3:4-5` | delete | — | D3/§4 |
| 47 | `canonical-for` — 7 distinct topics | `4.3:6-13` | keep | `oracle/compilation/representation-substrate` frontmatter `owns:` | the richest non-vacuous ownership claim in the chapter; pattern to copy |
| 48 | Substrate is **a contract, not a single dynamic container** | `4.3#representation-substrate` (48-57) | keep | `oracle/compilation/representation-substrate#contract` | sole statement; prevents the "one container" misreading |
| 49 | Five substrate primitives with full type definitions | `4.3#1-substrate-primitives` | keep | `oracle/compilation/representation-substrate#primitives` | sole *definition*; `4.4:82-92` restates as a cost table (row 62) |
| 50 | `Address[D]` is domain-separated; SHA-256, truncation only in log output | `4.3:101-105` | keep | `oracle/compilation/representation-substrate#primitives` | sole statement |
| 51 | Four op-signatures (`PredicateOps`, `SymbolicTensorOps`, `EvidenceOps`, `GroupOps`) | `4.3#2-the-parametric-op-signature-family` | keep | `oracle/compilation/representation-substrate#op-signatures` | sole definition. Prose says "Four … (a fourth, `GroupOps`, is added below). Three cover …" — awkward but not a defect |
| 52 | Per-cluster representation table (C1–C7 + 4 named fibers) | `4.3#3-per-cluster-representation-table` | keep | `oracle/compilation/representation-substrate#clusters` | sole statement of cluster→backend mapping |
| 53 | The `InvariantTerm`/`FormulaApply` symbolic-form row is **a separate fiber, not C4** | `4.4:143` → target `4.3#clusters` | move | `oracle/compilation/representation-substrate#clusters` | 4.3's table lists this row **unlabelled**, between C4 and the next; only `4.4:143` says explicitly it is not C4. Original to 4.4 — the one place the ambiguity is resolved |
| 54 | Canonical serialization rule — 11 numbered rules | `4.3#4-canonical-serialization-rule` | keep | `oracle/compilation/representation-substrate#serialization` | sole definition; `4.4:99-110` restates all 11 (row 63) |
| 55 | **§4.1 Identity is exact; ε rides alongside** — normative, with the non-transitivity argument | `4.3#41-identity-is-exact-ε-rides-alongside` | keep | `oracle/compilation/representation-substrate#identity-exact` | the keystone. Cited by `gamma-hat:128`, `4.4:231`, `10.2:62`, `live/specs`. **Every one of those citations uses the retired `§20.4.2` form** (C2) |
| 56 | Four consequences if the quotient is lost (no representative / dedup dies / `O(1)` equality dies / union-find dies) | `4.3:205-215` | keep | `oracle/compilation/representation-substrate#identity-exact` | the proof body; sole statement |
| 57 | **Rejected alternatives** — quantized addressing, ball/interval addressing — "recorded so they are not re-proposed" | `4.3:221-230` | keep | `oracle/compilation/representation-substrate#identity-exact` | **Not scaffolding.** Rejected-alternative records are forward-looking guards, not history of the corpus. Also → Log-worthy L4 |
| 58 | **§4.2 Estimate, don't decide** — any operation that can differ from exact emits an a-posteriori estimate | `4.3#42-the-consequence-estimate-dont-decide` | keep | `oracle/compilation/representation-substrate#estimate-dont-decide` | the ε obligation; registration duty lives at `residual-machinery §4.1` |
| 59 | "The gate gets **weaker**, not stronger" — from "must be exact" to "must estimate its own error" | `4.3:253-256` | keep | `oracle/compilation/representation-substrate#estimate-dont-decide` | present-tense statement of the rule's scope. The phrase "The prior rule was…" is a comparison, not a changelog — keep, but rewrite to drop "prior" |
| 60 | Every estimator so far is a byproduct of work already done (truncated SVD gives `σ_{k+1}`; inner solve gives its residual) | `4.3:257-261` | keep | `oracle/compilation/representation-substrate#estimate-dont-decide` | the affordability argument; sole statement |
| 61 | Hot-path commitments + 13-row complexity table + `SparseSet` backend ladder | `4.3#5-hot-path-commitments` | keep | `oracle/compilation/representation-substrate#hot-paths` | sole definition; `4.4:158-167` restates the table (row 64) and `4.4:119-123` the ladder (row 65) |
| 62 | What the substrate replaces (4 items) | `4.3#6-what-the-substrate-replaces` | keep | `oracle/compilation/representation-substrate#replaces` | keep items 1–3; item 4 (`PhysicsGraph` identity, `4.3:311-316`) duplicates `4.1:85-88` → delete that bullet, cross-reference instead (row 5) |
| 63 | What the substrate does **not** replace (3 items) | `4.3#7-what-the-substrate-does-not-replace` | keep | `oracle/compilation/representation-substrate#not-replaced` | negative-space; sole statement. High value |
| 64 | §8 Relationship to existing files — 11 bullets restating what each other page owns | `4.3#8-relationship-to-existing-files` | delete | — | **duplication engine in miniature.** Every bullet restates the other page's own claim; the header sentence ("each retains its canonical authority over its own concept") admits it. Replaced by the emitted topic→page map in `index/corpus.json` (§6) |
| 65 | §8's one non-restating claim: `IrrepLabel` identity is `(Address[GroupAtlas-context], local-irrep-name)` | `4.3:347-348` | move | `oracle/registry/canonical-vocabularies#irrep-label` | this is a *definition*, not a pointer, and it is the only one in §8. Would be lost if §8 is deleted wholesale |
| 66 | §9 Versioning discipline — `schema_version` bump, old addresses stay valid, migration is an explicit morphism; ROBDD atom-order versioning | `4.3#9-versioning-discipline` | keep | `oracle/compilation/representation-substrate#versioning` | forward-looking discipline, not history. Sole statement |

### 4.4-computational-overview.md → dissolved

**Verdict: dissolve the page.** Of ~40 claim-blocks, 27 restate a page that
already owns the topic, 11 are original, and 2 are self-referential scaffolding.
The 11 originals have identifiable topic owners elsewhere. See Notes for Phase 2
→ *The 4.4 recommendation*, which conflicts with plan §3 and needs Javier's call.

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 67 | `title: `/physics` — Computational Architecture Reference` — **unquoted backtick, invalid YAML** | `4.4:3` | delete | — | `yaml.safe_load` raises `ScannerError`; verified against all four scope pages, this is the only failure. §4 requires quoted titles |
| 68 | `authority`, `content-hash: 4823d9f76406` | `4.4:4-5` | delete | — | D3/§4 |
| 69 | `canonical-for: - computational-overview` — **vacuous** | `4.4:6-7` | delete | — | owns only its own id; the duplicate-topic invariant cannot fire on it. This page is a 6,475-word restatement engine sitting *outside* the anti-duplication machinery — the two facts are causally linked |
| 70 | Header blockquote: computational lens, physics meaning suppressed, depth target | `4.4:33-41` | mine | `practice/conventions#computational-lens` | the *lens* is a reusable reading convention worth keeping; the page-scoped framing is not |
| 71 | "This is a hand-written companion to the canon chapters (1–10)" | `4.4:38` | delete | — | **the duplication charter.** A page whose stated job is to restate ten chapters is a duplication engine by construction |
| 72 | "Every claim cites its canonical `arch-xx` / `impl-xx` source" | `4.4:39` | delete | — | retired id formats (plan §2 defect 7 class) **and** false of the page: zero of its 99 citations use either format. Same defect as `10.3-audit-prompt:96` |
| 73 | `/physics` is a compiler emitting a numerical kernel; compose-time vs runtime split | `4.4#1-what-kind-of-program-this-is` | delete | — | restates `4.2:50-60` + `architectural-principles` p1 |
| 74 | Compose-time is "branchy, allocation-heavy, pointer-chasing; latency- and correctness-bound, not throughput-bound" | `4.4:53-54` | move | `oracle/compilation/compose-time-pipeline#boundary` | **original** — no other page characterizes the compiler's own performance profile. One sentence, worth relocating |
| 75 | Four-role polyglot split settled; languages open; compiler emits runtime-host source, JIT once, flat arrays only | `4.4:61-66` | delete | — | restates `open-decisions` + `deriv-language-study`. The decision belongs in `program/build` per the language surveyor's scope |
| 76 | Central design lever: expensive structure discovery once at compile time | `4.4:68-72` | delete | — | restates `4.2:50-54` (the always-cheap discipline) |
| 77 | §2 heading + intro ("every load-bearing object is a *fiber* over five primitives; the storage and identity contract for the whole system") and the §2.1 primitives cost table | `4.4#2-the-memory-model` (75-92), `4.4#21-primitives` | delete | — | restates `4.3:48-53` and `4.3#1` |
| 78 | Cost annotations original to §2.1: "≈ two SIMD loads"; "ordinal doubles as a dense array index" | `4.4:84-85` | move | `oracle/compilation/representation-substrate#hot-paths` | **original** constant-factor detail absent from `4.3 §5` |
| 79 | §2.2 the 11 serialization rules, restated | `4.4#22-content-addressing-and-the-canonical-serializer` | delete | — | restates `4.3#4` rule for rule |
| 80 | "The serializer's *injectivity* is the single highest-consequence invariant in the system" | `4.4:96-98` | delete | — | also at `4.3:226-227` and `11.9:86`; `4.3` owns it |
| 81 | Numerical note: float normalization is what makes content-addressing safe for computed values; length-prefixing prevents concatenation ambiguity | `4.4:112-115` | move | `oracle/compilation/representation-substrate#serialization` | **original** — states *why* rules 10/11 exist. `4.3:170-181` gives the rules without the rationale |
| 82 | §2.3 `SparseSet` backend ladder | `4.4#23-backend-selection-decision-procedures` | delete | — | restates `4.3:286-294` |
| 83 | HAMT depth bound `≤ ⌈log₃₂ \|keys\|⌉` (≤ ~6 for ≤ 10⁹ keys); insert path-copies one root-to-leaf path | `4.4:125` | move | `oracle/compilation/representation-substrate#hot-paths` | **original** — `4.3` gives `O(log₃₂ n)` without the concrete depth bound |
| 84 | §2.4 op-signatures + per-cluster table | `4.4#24-op-signatures-and-the-per-cluster-storage-table` | delete | — | restates `4.3#2`–`#3`. Exception: the not-C4 row → row 53 |
| 85 | §2.5 hot-path complexity table | `4.4#25-hot-path-complexity-commitments` | delete | — | restates `4.3#5` |
| 86 | §3 three-tier state (micro/slow/macro), moment closure, homogenization | `4.4#3-the-data-operated-on--state-and-γ̂` (173-182) | delete | — | restates `multiscale-state` |
| 87 | **§3.1 the 7-tuple table — container, layout, byte counts per slot** | `4.4#31-the-7-tuple` | move | `oracle/state/unified-state#slot-layouts` | **This is the table the brief says was never written.** Seam requirement R1 cites `unified-state` for "per-slot array shapes and layouts"; `unified-state` has no such table and `4.4:186-192` is the only place one exists. Deleting 4.4 wholesale would realize the dangling promise permanently |
| 88 | Slots are a closed `StateComponent` universe; downstream code indexes by dense ordinal, not symbol | `4.4:194-195` | move | `oracle/state/unified-state#slot-layouts` | **original** — the "not by symbol" access rule is stated nowhere else |
| 89 | §3.2 γ̂ 5×4 encoding grid + slot-selection decision procedure | `4.4:199-209` | delete | — | restates `gamma-hat §1` (`2.3:41-63`), including the five first-class pairs |
| 90 | γ̂ MVP budget: `N_PW≈1000`, `N_b≈40`, `N_k≈29`, ≈18 MB vs ≈460 MB dense, TB warm start, supercell scaling | `4.4:211-220` | delete | — | restates `gamma-budget` (`2.6:16-33`) number for number |
| 91 | "k-blocks are mutually independent → embarrassingly parallel and independently addressable"; read costs set by `N_b`, not `N_PW²` | `4.4:216-217`, `4.4:225` | move | `oracle/state/gamma-budget#parallelism` | **original** — the parallelism consequence of the block encoding appears nowhere else |
| 92 | γ̂ read/write asymmetry | `4.4:222-227` | delete | — | restates `gamma-hat §2` (`2.3:65-106`) |
| 93 | §3.2 the four γ̂ questions, "resolved not open", with dispositions | `4.4:229-247` | delete | — | restates `gamma-hat §4` (`2.3:123-177`), which the passage itself names canonical. See Open questions note on resolution siting |
| 94 | §3.3 L1–L4 dependency order; level derived from transitive inputs, not stored | `4.4:249-254` | delete | — | restates `born-oppenheimer-levels` + `4.1:179` |
| 95 | §3.3 the "Operations (computational)" column — per-level algorithm classes | `4.4:256-260` | move | `oracle/state/born-oppenheimer-levels#computational-operations` | **original** — maps each BO level to its numerical-kernel class; no other page does |
| 96 | Order-of-operations: an L2 force evaluation contains a converged L1 inner solve; the adjoint must thread implicit-diff through both | `4.4:262-265` | move | `oracle/compilation/compose-time-pipeline#stage-4` | **original** and load-bearing for adjoint synthesis — the nesting constraint is stated nowhere else |
| 97 | §3.4 dressing tiers Layer 1 / 1.25 / 1.75; MVP runs entirely at 1.25; 1.75 V2-deferred | `4.4#34-dressing-tiers` | delete | — | restates `born-oppenheimer-levels §1`. Carries the `Layer-1.75` nomenclature defect (§4) — propose only |
| 98 | §4 `PhysicsGraph` node/kind/role definitions and sidecar list | `4.4#4-the-ir--the-physicsgraph` (282-304) | delete | — | restates `4.1#1`–`#4` |
| 99 | **Arena / index DAG** — nodes in a flat array, `NodeId` = integer handle not pointer; gives cache locality, trivial serialization, natural hash-cons table | `4.4:277-280` | move | `oracle/compilation/physics-graph#representation` | **original and sole statement.** `10.3-audit-prompt:106` asks whether "the arena/index DAG" is the right choice — an auditor question pointing at a structure only this page defines. Delete 4.4 without moving this and the audit prompt dangles |
| 100 | **`CompressionPlan` Stage-4 selection procedure** — the five choose-by rules (small/dense → Dense; inferred sparsity → Sparse; `r ≪ n` → LowRank; hierarchical off-diagonal → HODLR; high-dim tensor → TT) | `4.4:306-312` | move | `oracle/compilation/compose-time-pipeline#stage-4` | **original.** `4.2:195-204` names the plans and the error target but gives **no selection criteria**; `4.1:158-165` gives only the type. This is the actual decision procedure |
| 101 | §5 pipeline summary table (in→out, algorithm class, cost) | `4.4#5-the-core-algorithm--the-41-pipeline` (321-328) | delete | — | restates `4.2#6`. **Second instance of the "4+1" label over six enumerated stages** (C1) |
| 102 | The "Algorithm class" column — macro expansion+BDD / finite-group rep theory / Reynolds / e-graph / numerical-LA planning | `4.4:323-328` | move | `oracle/compilation/compose-time-pipeline#boundary` | **original** — names the mathematical class of each stage; `4.2#6` gives cost and output only |
| 103 | §5 Stage 1 / Stage 2 / Stage 2.5 / Stage 3 narrative restatements | `4.4:330-364` | delete | — | restates `4.2#1`–`#3` and `coupling-structure §3` (verified: pre-prune, emptiness test, `\|G\|≤192`, `dim(T)≤250`, ≤12M ops all at `3.3:172-194`) |
| 104 | Schur numerical note: cubic blocks are *small* (`d_λ ∈ {1,2,3}`, 4 under SOC) → favors cache-resident dense solve per block, **poor fit for wide-SIMD/GPU unless batched** | `4.4:340-342` | move | `oracle/compilation/compose-time-pipeline#stage-2` | **original** — the only hardware-mapping consequence stated anywhere in the corpus |
| 105 | §5 Stage 4 restatement: compression selection, implicit-diff adjoint, τ_adj gate, codegen | `4.4:366-381` | delete | — | restates `4.2#4` + `residual-machinery §5`. Drops `4.2`'s "not `O(1)` work" qualification (C5) |
| 106 | Conditioning of the adjoint solve is set by the fixed-point map's Jacobian; near-singular Jacobians (slow self-consistency) are **the failure mode** | `4.4:372-373` | move | `oracle/compilation/compose-time-pipeline#stage-4` | **original** — names the failure mode; `4.2` and `residual-machinery §5` give the `τ_cond` guard without saying what it guards against |
| 107 | §5 Stage 5 restatement | `4.4:383-385` | delete | — | restates `4.2#5` |
| 108 | **§6.1 the 12-method table — kernel, complexity, selection criteria, numerical stability** | `4.4#61-the-12-methods--numerical-kernels` | move | `oracle/registry/computational-methods#kernels` | **original, and the largest single block of unowned engineering content in my scope.** `computational-methods` is 309 words and owns only "method signatures"; it carries no complexity, no solver-selection rule, no stability note. Verified absent corpus-wide: `reorthogonalization`, `robust orientation predicates`, `Scharfetter–Gummel` (only in `multiscale-state`), broadening-η regularization, symplectic-for-MD, cell-lists vs `O(N²)`, near-degeneracy block solvers |
| 109 | §6.2 the 10 representative template signatures | `4.4#62-the-20-templates--graph-construction-macros` | delete | — | restates `property-templates` (verified: `6.5:16-40` carries typed signatures) |
| 110 | The "Composes" column (template → method) and the `HarmonicStiffnessHessianOf` annotation "+ symmetrization + acoustic-sum-rule enforcement" | `4.4:414-425` | move | `oracle/registry/property-templates#composition` | **original** — the template→method map and the ASR-stabilization note are not in `property-templates` |
| 111 | §6.3 formula distribution by cost-tier and diff-tag | `4.4#63-the-132-formulas--distribution` | delete | — | restates `canonical-vocabularies §3` / `named-formulas`. Carries the `D0\|DN\|D1..D4` ordering defect (§4) — propose only |
| 112 | §6.4 the dynamics computationally (`L` antisymmetric, `M` PSD, EOM-violation residual) | `4.4#64-the-dynamics-computationally` | delete | — | restates `generic-dynamics` + `residual-definitions` |
| 113 | §7 symmetry & topology structures table | `4.4#7-symmetry--topology-data-structures` | delete | — | restates `canonical-vocabularies §5` + `topology-atlas` |
| 114 | §7 cost column (Schreier–Sims storage `O(\|G\|·d)`; character table `O(\|G\|·#irreps)`; SNF `O(m·n·log max)`; coset-tree lookup `O(log #orbits)`) and "computed offline in GAP, baked in as content-addressed tables" | `4.4:453-462` | move | `oracle/registry/topology-atlas#costs` | **original** — `topology-atlas` states SNF is polynomial but gives no storage/lookup costs and no offline-bake statement |
| 115 | §8 `Validate` signature, `ResidualKey`, granularity, gradients, `Import`, `RoaringCoverageMask` | `4.4#8-outputs-and-the-consumer-boundary` | delete | — | restates `pino-bridge §1`–`§2.1` + `residual-definitions §4` |
| 116 | §9 ten cert obligations table | `4.4#9-verification--cert` | delete | — | restates `cert-obligations` |
| 117 | §9 the **per-obligation complexity column** | `4.4:509-520` | move | `oracle/certification/cert-obligations#costs` | **original** — `cert-obligations:110` gives one blanket "`O(1)`–`O(block)` per invariant" line; the per-obligation costs exist only here |
| 118 | §9 `SqliteReferenceCache` operational detail: write-once, deletes disallowed, WAL mode, `n ≈ 10–10⁴` | `4.4:522-527` | move | `oracle/certification/cert-obligations#reference-cache` | **original** operational spec beyond `cert-obligations §2` |
| 119 | §10 coupling-structure summary | `4.4#10-coupling-structure` | delete | — | restates `coupling-structure §1`, `§3`, `§10`, `§11` |
| 120 | §11 the math-to-location map (14 rows: branch of math → where it enters) | `4.4#11-the-math-to-location-map` | mine | `index/corpus.json` (emitted) — see Notes | **original**, and genuinely useful, but it is a *navigation index in prose* — exactly what §6 says must be emitted rather than hand-written. Hand-maintaining it is how it rots |
| 121 | §12 the `core ← shared ← …` import chain is **retired**; "must not be cited to architectural-principles" | `4.4:576-581` | delete | — | scaffolding about scaffolding. The same retirement is already stated at `architectural-principles:24` — which itself needs the history marker stripped (that page is another surveyor's scope) |
| 122 | What survives of the build discipline: freeze a layer's typed interfaces, then implement upper-layer leaves independently | `4.4:580-581` | move | `program/build/build-sequence#discipline` | the one present-tense fact inside row 121 |
| 123 | §12 polyglot seam + **differential golden test (emitted kernel vs tree-walking interpreter of the same IR)** | `4.4:582-588` | move | `program/build/build-verification#golden-test` | the seam restates `open-decisions`, but the golden test is **original** and is a concrete verification obligation |
| 124 | §12 composition fingerprint / kernel cache | `4.4:589-591` | delete | — | restates `4.2:277-281` (row 44) |
| 125 | §13 "internally coherent (58 pages, both checkers clean)" and "was deep-audited" | `4.4:597-599` | delete | — | a page certifying the corpus by page-count and a green run. Calibration (Notes) shows the green run does not license the claim. Self-referential |
| 126 | §13 formalization gaps: 52-observable (+16 FoM) catalog, crystal-structure-validity residual catalog, rest of `B9` | `4.4:604-613` | move | Open questions → owning pages | genuinely open enumeration work; see Open questions `observable-catalog`, `b9-bundle`, `csp-residual-catalog` |
| 127 | §13 the landed/deferred parenthetical (rows 113–119, 120–127, sub-method, V2 deferrals, "remediated through P2") | `4.4:606-613` | delete | — | history of what landed when → Log-worthy L6. The V2 deferral *list* survives as open questions (row 126) |
| 128 | §13 "The data-structure layer — no longer open … Kept here rather than deleted because an entry that silently disappears reads as though it was never a problem" | `4.4:614-618` | delete | — | **the corpus explicitly arguing for retaining scaffolding.** D1/D2 answer it: the entry goes to `log/timeline.md`, which is exactly the "does not silently disappear" mechanism the passage is reaching for |
| 129 | §13 **no post-registration adjoint-drift monitoring** — registration validates the formula's adjoint; Stage 4 synthesizes the composition's adjoint over a rewritten graph; nothing revalidates | `4.4:619-623` | move | Open questions → `oracle/compilation/compose-time-pipeline#stage-4` | live open question; currently stated only here and at `10.2:99-105`, neither of which is the owning page. This is plan §5's worked example, confirmed real |
| 130 | §13 deferred engineering decisions: surrogate-net build-vs-adopt, PDE-mesh adjoint scheme, Layer-1.75 onramp, language pick | `4.4:624-629` | move | Open questions → owning pages | four live open items |
| 131 | "(The integrator-interface signature closed 2026-07-16 …)" | `4.4:627-629` | delete | — | closure framing → Log-worthy L5; the *resolution* (per-tier tangent + steppable-form manifest, integrator consumer-side) is a present-tense fact that currently has **no owning page** — Open questions `steppable-form-manifest` |
| 132 | §13 closing: treat §§1–12 as claims that *should be valid*, §13 as *intentionally open* | `4.4:631-632` | delete | — | a page declaring its own claims merely "should be" valid is the companion problem restated. Under D7 open items live on owning pages, so the distinction has no carrier |

---

## Open questions

| id | question | owning page | why it is open |
|---|---|---|---|
| `adjoint-drift-monitoring` | Stage 4 synthesizes the composition's adjoint over a graph Stage 3 already rewrote; the registration gate validated only the formula's adjoint. What revalidates the second? | `oracle/compilation/compose-time-pipeline#stage-4` | Explicitly open at `10.2:99-105` ("Still open — and the ε rule does not close it"). Stated on no pipeline page today |
| `environment-record` | What are the fields of `Environment`, and which are **structural** (recompile triggers) vs **scalar** (runtime inputs)? | `oracle/state/crystal-inputs#environment` | The kernel-cache fingerprint at `4.2:277-281` keys on "`Environment`-structural"; `applicability-classifiers:124` tags kernels with "the `Environment` box". Neither the record nor the split is defined anywhere. `EnvField` (`4.1:98`) is likewise undefined. Homeless |
| `steppable-form-manifest` | What is the schema of the steppable-form manifest and the per-tier tangent map? | `oracle/seams/pino-bridge` *(or a new `interface/` page)* | Cited as a closed decision by `gamma-hat:97`, `4.4:242`, `4.4:628`, `traps`, `timeline` — but no page's `canonical-for` claims it. Only a full schema exists, in `journal/live/specs/2026-07-16-evolver-duality-research.md:353`, which is slated for deletion. **Homeless resolution of a closed question** |
| `pde-mesh-adjoint-scheme` | Which adjoint scheme for the PDE mesh? (the mesh *format* is committed in `multiscale-state`) | `oracle/state/multiscale-state` | `4.4:624-626`; deferred just-in-time |
| `surrogate-net-build-vs-adopt` | Build or adopt the surrogate net for `D4` formulas? | `oracle/registry/named-formulas` | `4.4:624`. **Note the D4 retag collision** — Contradictions C6 |
| `layer-175-onramp` | The GW / DMFT onramp for iterative fixed-point dressings | `oracle/state/born-oppenheimer-levels#dressing-tiers` | `4.4:626`; V2-deferred, V1 ships loud `not-implemented` stubs |
| `implementation-language` | Which languages fill the four settled roles? | `program/build/forced-decisions` | `4.4:61-66`, `4.2:204-206`. The four-role split is settled; the fill is not |
| `observable-catalog` | The 52-observable (+16 FoM) catalog is researched but not machine-readable | `oracle/registry/observable-bundles` | `4.4:605-606`; enumeration task |
| `b9-bundle` | The rest of the `B9` bundle is not formalized | `oracle/registry/observable-bundles` | `4.4:606` |
| `csp-residual-catalog` | The crystal-structure-validity residual catalog is not machine-readable | `oracle/laws/residual-definitions` | `4.4:605-606` |
| `stage3-performance` | Equality saturation at Stage 3 is "the hardest pass to build" and its performance is open-ended | `oracle/compilation/compose-time-pipeline#stage-3` | `4.4:363-364`. Not listed in `10.2-open-decisions` — an open item with no register entry today |

---

## Log-worthy advancements

| date | finding or decision | evidence | attribution | superseded |
|---|---|---|---|---|
| 2026-07-21 | **Identity stays exact; ε rides alongside.** `≈_ε` is not transitive, so it induces a covering by maximal cliques rather than a quotient — no canonical representative, nothing to hash. Content addressing therefore cannot absorb tolerance | `4.3:186-219` → `oracle/compilation/representation-substrate#identity-exact` | corpus (keystone resolution of the γ̂ cluster) | the framing of ε-equality as an open CS problem |
| 2026-07-21 | **Rewrite-admission rule.** A Stage-3 rewrite is admissible iff exact over ℝ, its float side conditions are discharged by an e-class interval/not-equals analysis, and it registers a fidelity generator | `4.2:145-158` → `oracle/compilation/compose-time-pipeline#rewrite-admission` | corpus, adopting Zhang et al. (PLDI 2023, `egglog`) | "exactness-only" as the admission gate |
| 2026-07-22 | **Correction to the egglog evidence.** The sound rule set won on accuracy in 104 of 289 benchmarks *against 135 where the unsound set still won*. The corpus had quoted 104 without 135, turning an even trade into a win | `4.2:160-173` | corpus self-correction | the one-sided 104-only citation |
| 2026-07-21 | **Materialization policy reclassified** from an accuracy problem to a Stage-4 scheduling problem: forcing vs deferring changes cost, not value, so no error term exists and no fidelity generator is owed | `4.2:214-233`, `gamma-hat:143-150` | corpus | "materialization policy … no principled default" as an open γ̂ data-structure problem |
| 2026-07-21 | **Attribution correction:** DAG-rematerialization NP-completeness is Naumann (*J. Discrete Algorithms* 7(4) 402–410, 2009), a separate result from `revolve` (Griewank & Walther, *ACM TOMS* 26(1) 19–45, 2000). Previously folded into the `revolve` parenthetical as though one source gave both | `4.2:220-222`, `gamma-hat:148-149` | corpus self-correction | the merged citation |
| 2026-07-21 | **Rejected addressing alternatives recorded:** quantized addressing (buys ε-dedup at the cost of injectivity, plus a grid artifact at every cell boundary) and ball/interval addressing (relocates non-transitivity into ball overlap, doubles every payload) | `4.3:221-230` | corpus | — (recorded to prevent re-proposal) |
| 2026-07-16 | **Integrator interface closed:** `/physics` emits a per-tier tangent map and a steppable-form manifest — a pure function, not an integrator. Long-trajectory drift is *exported* to the integrating consumer, not dissolved | `4.4:627-629`, `gamma-hat:96-101` | corpus | long-trajectory drift as an internal γ̂ open problem |
| 2026-07-21 | **Runtime cost is three-class, not one:** per-sample core (µs–ms), on-request spectral (0.1–10 s, per-epoch cached), per-composition reference (seconds–minutes, calibration-only) | `4.2:283-294` | corpus | the single "µs–ms" runtime figure |
| 2026-07-21 | **Rank-dependent applicability of the low-rank γ̂ slot is a compile-time predicate** on `(PeriodicityStructure, SiteDecoration)` decided at Stage 4 — the runtime cost that was the original objection no longer exists | `gamma-hat:170-177` | corpus | the runtime-check framing |
| 2026-07-22 | **Compression plans carry per-plan error targets;** ranks are chosen to meet the target, not by structure alone, and the target enters the per-residual budget via `Quantity.combineTol` | `4.2:200-204` | corpus | rank selection by structure alone |
| *(undated)* | **Adjoint-tape materialization owes no fidelity generator** — recomputing and reading a stored value give the same value. Marks the boundary of the ε rule: it is about value, not cost | `4.2:223-229` | corpus | — |

*Included with a note per the brief's under-logging guidance:* the last row is
undated in the corpus; the timeline surveyor may be able to date it.

---

## Contradictions — COLLECTED, NOT RESOLVED

| claim | source A | source B | nature of the conflict |
|---|---|---|---|
| **C1** — How many compose-time stages are there? | `4.2:6` `canonical-for: 4+1 stage compose-time pipeline`; `architectural-principles:21`; `4.4:316` | `4.2:56` "runs in **five** stages plus the Stage-2.5 sub-stage"; `4.2:268-275` table enumerates **six** rows (1, 2, 2.5, 3, 4, 5); `10.3:27` also enumerates six under the "4+1" label | The canonical topic name states a count the page's own table contradicts. `4.2:114-116` gives the substantive defence — 2.5 is the constructive dual of stage 2, hence a sub-stage — but the name never absorbed it. **Nomenclature; propose, do not rename** (§4) |
| **C2** — Which section of `representation-substrate` resolves ε-equality? | `4.2:177` and `gamma-hat:136` cite `§20.4.1` for the exact-identity separation, which maps to today's `§4.1` | `gamma-hat:127-128`, `4.4:231`, `10.2:62`, `10.2:114`, `live/specs:97,125` all cite the pair `` `§4.1`/`§20.4.2` `` | `§20.x` is the **retired serial-derived coordinate** for `arch-20-representations` (`10.1:153`, `instructions.md:51`). Under the old numbering `§20.4.1 ↔ §4.1` and `§20.4.2 ↔ §4.2`, so the pair `§4.1`/`§20.4.2` names **two different sections as though they were one section under two numberings**. Half-migrated: someone renumbered `.1` and left `.2`. Full census in Notes |
| **C3** — Is `computational-overview` held to the same rules as canon? | `4.4:38` "the checkers hold it to the same citation rules as any other page" | Calibration: 95 of its 99 citations are backticked and therefore unchecked; its frontmatter does not parse as YAML; its `canonical-for` is vacuous | The page asserts a level of enforcement that does not exist for it |
| **C4** — Does `4.4` cite `arch-xx`/`impl-xx` sources? | `4.4:39` "Every claim cites its canonical `arch-xx` / `impl-xx` source" | Zero occurrences of either format in the page | Stale self-description; same retired-id class as `10.3:96` |
| **C5** — Is the implicit-diff adjoint `O(1)`? | `4.2:207-210` "one extra linear *system*, independent of forward iteration count — **not `O(1)` work**, since that system is itself solved iteratively" | `4.4:370-372` "**one linear solve** … independent of the forward iteration count" | The companion drops the qualification the canonical page was careful to add. Precision loss, arguably a false claim → auditor 2 |
| **C6** — Does `D4` mean *surrogate* or *relaxed*? | `4.4:436` "`D4` relaxed, e.g. log-sum-exp soft-hull / Gumbel-Softmax"; `cert-obligations:147` "`D4` relaxation validity" | `4.4:519` "surrogate-net validity (**D4 only**)"; `4.4:624` "surrogate-net build-vs-adopt"; `cert-obligations:65` "for D4 **surrogate** formulas"; `cert-obligations:178` "surrogate validity" | **New instances of plan §2 defect 6**, which was documented only at `10.2` item 1. The 2026-07-21 retag reached the tag table but not the cert obligations or the deferred-decisions list. `cert-obligations` contradicts itself internally (`:65` vs `:147`). Flagged to the certification surveyor |
| **C7** — Is the `InvariantTerm`/`FormulaApply` symbolic-form fiber part of C4? | `4.3:139-140` lists it as the row immediately after C4, unlabelled | `4.4:143` "a separate fiber, **not C4**" | Only the companion disambiguates. If 4.4 is deleted wholesale the ambiguity returns (row 53) |
| **C8** — Are the four `γ̂` questions closed? | `gamma-hat:123-130`, `4.4:229`, `live/specs:125` — closed | `10.3-audit-prompt:114` still instructs the auditor to examine "the `γ̂` §15.4 ε-equality **open problem**" | The audit prompt was not updated at closure, and cites a retired `§15.4` coordinate besides. `10.3` is another surveyor's scope; flagged |

---

## Notes for Phase 2

### Calibration — what the checkers actually catch

Per the brief I did not trust a green run. I copied the corpus to a scratch tree,
confirmed both checkers green, then planted one defect at a time in
`4.1-physics-graph.md`.

**First attempt produced three false positives, and the reason matters.** Every
planted defect initially "fired" — but the failure message was always
`stale content-hash (… -> …); regenerate`, never the citation error. The
`content-hash` stamp trips on *any* byte change and masks the check under test.
Re-running with hashes restamped between probes gives the true picture:

| planted defect | result |
|---|---|
| backticked citation → nonexistent page id | **MISSED** |
| backticked citation → real page absent from `depends-on` | **MISSED** |
| backticked **retired** page id (`arch-11-residuals`) | **MISSED** |
| section citation → nonexistent section (`§99.7`) | **MISSED** |
| retired serial coordinate (`§20.4.2`) | **MISSED** |
| bracketed citation → nonexistent page id | FIRED |
| bracketed citation → real page absent from `depends-on` | FIRED |

Three consequences for Phase 2:

1. **`content-hash` is a calibration hazard, not just maintenance cost.** Any
   probe that edits a page trips the hash check first. A calibration harness that
   does not restamp between probes will report the checker as catching defects it
   does not catch. This is a plausible mechanism for the false "one defect per
   check" claim in the plan's standing warning, and it is an independent argument
   for §4's deletion of the stamp.
2. **Chapter 4 is almost entirely unchecked.** 190 of 198 cross-references are
   backticked. `4.1-physics-graph` has **44 backticked and 0 bracketed** — none of
   its references is verified by anything.
3. **`check_the_checkers.py` reports `58/58 fired, 0 missed, 0 stale` and
   `coverage: every data-agreement check (19) fired under some probe`.** That is
   true and not reassuring: the probe set is derived from the checks that exist,
   so the five classes above are not "uncovered", they are invisible. When the
   harness is rebuilt (§8), the probe set must be derived from the *defect space*
   — including anchor resolution and citation syntax — not from the check list.

### The `§20.x` census — every retired-coordinate citation

`§20.x` is the retired serial coordinate for `representation-substrate`
(`10.1:153`, `journal/instructions.md:51`). Full corpus census, so Phase 2 can
re-anchor in one pass — **note that the correct target differs between them**:

| location | as written | resolves to |
|---|---|---|
| `4.2:177` | `§20.4.1` | `representation-substrate#identity-exact` |
| `4.4:231` | `` `§4.1`/`§20.4.2` `` | both `#identity-exact` **and** `#estimate-dont-decide` |
| `2.3-gamma-hat.md:128` | `` `§4.1`/`§20.4.2` `` | both |
| `2.3-gamma-hat.md:136` | `§20.4.1` | `#identity-exact` |
| `10.2-open-decisions.md:62` | `§4.1/§20.4.2` | both |
| `10.2-open-decisions.md:114` | `§20.4.2` | `#estimate-dont-decide` |
| `10.2-open-decisions.md:178, 187, 201` | `§20.4` | `#serialization` |
| `11.9-deriv-language-study.md:68, 86` | `§20.4` | `#serialization` |
| `live/presentations/2026-07-22-cs-framing-outline.md:360` | `§20.5` | `#hot-paths` |
| `live/specs/2026-07-21-oracle-code-spec-research-brief.md:97, 125` | `§4.1`/`§20.4.2` | both |

Two further retired coordinates of the same family, outside my scope but found
while sweeping: `4.4:614` and `10.3:114` cite `` `γ̂` §15.4 `` (retired serial for
`gamma-hat`), and `2.4-multiscale-state.md:280` cites a bare `§16`.

### The 4.4 recommendation — and where it conflicts with the plan

Plan §3 lists `computational-overview` as a surviving page under
`oracle/compilation/`. A claim-by-claim disposition **empties it**: 27 of ~40
blocks restate a page that already owns the topic, and each of the 11 originals
has a better owner (`computational-methods`, `unified-state`, `physics-graph`,
`compose-time-pipeline`, `cert-obligations`, `topology-atlas`,
`property-templates`, `gamma-budget`, `born-oppenheimer-levels`).

**My recommendation: delete the page and route the originals.** The reasoning is
the plan's own. A page whose charter is to restate ten chapters (`4.4:38`) cannot
be made non-duplicating by editing it — the duplication is the charter. Its
vacuous `canonical-for` is not a coincidence: a page that owns no topic distinct
from its id is precisely a page with nothing of its own, and the checker cannot
see the duplication because the duplicate-topic invariant never fires on it. Its
§11 math-to-location map is the one thing that genuinely wants to be
cross-cutting, and §6 already says that job belongs to emitted `corpus.json`.

**This is Javier's call, not mine** — it changes the agreed target structure. If
he keeps the page, it must be given a real `owns:` list (I suggest: *per-method
complexity and numerical stability*, *cross-cutting cost model*), and rows 108,
114, 117 should stay on it rather than move. Rows 87, 99, 100 should move
regardless: they are the ones other pages already depend on.

### Ordering hazards

- **Row 87 is the one that must not be missed.** `4.4:186-192` is the only
  per-slot layout table in the corpus, and seam requirement R1 points at
  `unified-state` for exactly that content. Deleting 4.4 before the table is
  moved converts a documented dangling promise into a permanent loss. Same shape,
  lower stakes, for rows 99 (arena/index DAG — `10.3:106` depends on it) and 53
  (the not-C4 disambiguation).
- **Rows 108 and 117 relocate into pages that are currently very thin.**
  `computational-methods` is 309 words; row 108 is roughly 1,200. The receiving
  page's structure will need to be designed, not appended to.
- **Do not seed any value in this fragment from `11.8` or `11.9`.** I took no
  values from appendix pages; the γ̂ budget numbers in rows 90–91 are checked
  against `gamma-budget` (`2.6:16-33`), not against an appendix.
- **`4.3 §8` (row 64) must be deleted only after `corpus.json` emits the
  topic→page map**, since §8 is the corpus's current human-readable version of
  that map. Delete it earlier and navigation regresses between phases.

### What I could not disposition confidently

- **Row 120 (§11 math-to-location map).** I marked it `mine` to `index/corpus.json`
  because §6 says navigation is emitted, but `corpus.json`'s specified schema
  (page/topic/anchor/edges/open-questions/formula-registry) has **no field for
  "branch of mathematics"**. Either the schema grows a field or this map needs a
  home as prose. Flagged rather than guessed.
- **Row 70 (the computational-lens blockquote).** I routed the lens to
  `practice/conventions`, but no surveyor owns "reading conventions" explicitly
  and `practice/conventions` may already be full. Low stakes; one paragraph.
- **Whether `4.2:114-116` settles C1.** It is the strongest argument that "2.5"
  is principled rather than sloppy, and it may mean the right fix is to keep the
  fractional stage and rename the *count* ("5+1"), not the stage. I did not
  decide; §4 says propose only.
- **`4.3 §2`'s "Four op signatures … (a fourth, `GroupOps`, is added below). Three
  cover …"** reads as though it was edited from three to four in place. It is
  correct as written, just awkward, so I did not log it as a contradiction — but
  a Phase-2 rewrite should smooth it.
