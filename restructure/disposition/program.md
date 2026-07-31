# Disposition — program (purpose + build)

Scope: `journal/pages/01-purpose-and-product/` (1.1–1.5) → `journals/program/purpose/`
and `journal/pages/08-mvp-and-build/` (8.1–8.7) → `journals/program/build/`. 12 pages, 8,198 words.
Read at: 2af93d2

**Probes run** (scratch copies, deleted after; corpus untouched). Baseline
`check_book_structure.py --check` green: `58 pages, 98 canonical topics, graph symmetric`.

| probe | planted | result |
|---|---|---|
| A | `8.6` `canonical-for:` set to exactly its own id `build-sequence` | **green** — no vacuous-ownership check exists, exact or otherwise |
| B | backticked citation ` `no-such-page-at-all` ` in `8.5` | **green** on the reference (only my edit's hash noise) |
| C (control for B) | same id bracketed `[another-ghost-id]` in `8.5` | **fires** — `reference [another-ghost-id] resolves to no page` |
| C2 | `8.7`'s "132 formulas" → "999 formulas" | **green** — outside the count-drift sweep |
| D | `1.5`'s "132 substantive named formulas" → "999" | **green** — outside the sweep |
| E (control) | "999 substantive formulas" planted in `8.3` | **fires** — `says 999 substantive formulas; registry CSV has 132` |

The count sweep (`check_book_structure.py:317`) matches only the adjacent phrase
`(\d+)\s+substantive formulas`. Both restatements of the formula count inside my scope
use variant phrasings and are unswept.

---

## Disposition rows

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 1 | `authority: canon` + `content-hash` frontmatter keys | all 12 scope pages, frontmatter | delete | — | D6/§4 delete both corpus-wide; `authority` has no second tier once ch. 11 dissolves |
| 2 | PINO "predicts the **time evolution** of the state of a crystalline material" | `1.1-purpose-and-scope.md:19-20` | keep | `program/purpose/purpose-and-scope#what-n-op-is` | **Contradiction C1 — do not resolve.** Framing must be settled before the sentence is rewritten |
| 3 | Downstream target: durable UWBG chips for harsh environments (jet turbine, >500 °C, cycling, vibration, field, current density, radiation) | `1.1:20-25` | keep | `program/purpose/purpose-and-scope#downstream-target` | sole full statement in canon; `1.5:37-39` and `10.3-audit-prompt:23` restate it |
| 4 | `/physics` does not represent state *values*; it instantiates a physical system and defines the laws | `1.1:27-31` | keep | `program/purpose/purpose-and-scope#what-physics-is` | sole statement of the instantiate-vs-store distinction |
| 5 | Properties are derived from state, **never hard-coded**; some perturbations alter what properties do to the lattice | `1.1:31-33` | move | `oracle/registry/properties#derived-not-hardcoded` | a rule about properties, stated on the purpose page; `6.10-properties` owns properties and is silent on it |
| 6 | MVP models **diamond** | `1.1:34-35` | keep | `program/purpose/purpose-and-scope#mvp` | scope fact the purpose page legitimately owns |
| 7 | "…with three target capabilities: 1. crystal-structure prediction 2. electron-cloud diffusion 3. heat diffusion" | `1.1:35-40` | delete | cite `[capability-slices]` | duplication; `8.2-capability-slices` owns "MVP capabilities" and states all three in full |
| 8 | MVP discipline: "as much closed-form / computationally feasible expressions as possible" + purpose-built tools | `1.1:42-44` | keep | `program/purpose/purpose-and-scope#mvp-discipline` | sole statement; nothing else names the discipline |
| 9 | Broader material scope: c-BN, AlN, GaN, β-Ga₂O₃, AlGaN; W, Mo, Pt, Ti, Ni, Ta, TiN, WSi₂; SiC, Si, sapphire; Al₂O₃, HfO₂, AlN-as-dielectric | `1.1:44-47` | keep | `program/purpose/purpose-and-scope#material-scope` | **Contradiction C5** — `11.5-deriv-high-field.md:26` gives a different anchor set, neither a subset of the other |
| 10 | Comprehensive spec, diamond-first build — the distinction that "runs through everything" | `1.1:49-53` | keep | `program/purpose/purpose-and-scope#comprehensive-spec-diamond-build` | sole statement of the program's central scoping stance |
| 11 | "**`[mvp-scope]` owns MVP scope** … The paragraph above is a summary of it, not a second definition of it; where the two differ, that page wins." | `1.1:54-56` | delete | — | a tie-breaker that exists only because the fact is stated twice. Row 7 removes the duplication; the rule then has nothing to arbitrate. Scaffolding of the "we might disagree later" kind D1 forbids |
| 12 | `/physics` is a pure oracle: owns no training control flow, no sample selection beyond per-generator `sampling-policy`, no loss-consuming loop | `1.1:59-62` | keep | `program/purpose/purpose-and-scope#what-physics-is-not` | owner; `1.2:228-229` and `1.3:22-24` restate |
| 13 | Active-learning loops (residual-adaptive sampling, query-by-committee, importance reweighting) live in `/interface`, not `/physics` and not `/informed-operator`; both expose the signals an external policy consumes | `1.1:62-68` | move | `interface/boundary#what-interface-owns` | the plan gives `interface/` exactly one page stating the boundary. This paragraph is its only seed content anywhere in canon |
| 14 | `canonical-for: [product]` — identical to id | `1.2-product.md:6-7` | delete | replace with ≥1 distinct topic | vacuous ownership, defect 4; probe A shows no checker fires |
| 15 | Header blockquote: "companion to the atomic spec"; "every claim cites its canonical `arch-xx` / `impl-xx` source"; "Fixed by discussion 2026-07-16" | `1.2:25-31` | delete | — | `arch-xx`/`impl-xx` are retired id formats (defect 2 class); "the atomic spec/tree" is a pre-book container name; dated fixing is history |
| 16 | The amendment-direction rule: "amend by editing this file against the atomic tree, never the reverse" | `1.2:31` | move | `practice/conventions#companion-page-amendment` | a live editorial convention buried in a scaffolding blockquote |
| 17 | Identity: the product is **the oracle** — the compiled scoring function ships, not a service/framework/the PINO | `1.2:37-41` | keep | `program/purpose/product#identity` | owner |
| 18 | Mission: "verify whether a crystal is valid" = produce slot-by-slot evidence; the oracle never renders a verdict | `1.2:43-46` | keep | `program/purpose/product#evidence-not-verdict` | sharpest statement in canon; make it the owner |
| 19 | Consumers: two classes, one surface (`/informed-operator` hot loop; people screening/reconciling) | `1.2:48-53` | keep | `program/purpose/product#consumers` | sole statement |
| 20 | Principle **YAGNI** — no machinery without a present need | `1.2:56-57` | keep | `program/purpose/product#principles` | sole statement |
| 21 | Principle **Evidence, never verdicts** | `1.2:57-59` | delete | cite row 18 | restates §1 Mission four lines above it, on the same page |
| 22 | Principle **Refusal is first-class** | `1.2:59-61` | keep | `program/purpose/product#principles` | owner of the product-side phrasing; `1.4:34-40` owns the mechanics |
| 23 | Principle **No natural language** — every artifact is machine data | `1.2:61-63` | keep | `program/purpose/product#principles` | sole statement |
| 24 | Principle **Agnostic by purity** — pure function, flat arrays, no loop ownership | `1.2:63-66` | delete | cite `[architectural-principles#numerics-agnostic]` | third statement of one fact: `1.3:18-19`, `1.4:44-49`, here |
| 25 | Same bullet's parenthetical citing `informed-operator/design/learnable-structure-requirements.md` | `1.2:65-66` | mine | `operator/seam/learnable-structure` | container deleted per §9; the mirror-commitment claim survives |
| 26 | **Score, not solve.** "The caller supplies complete candidate states; the oracle never fills in missing pieces" | `1.2:67-68` | keep | `program/purpose/product#score-not-solve` | **owner — this is the oracle/operator boundary.** Its citation `(purpose-and-scope)` is a **dangling promise**: `1.1` states no such thing (full read, no match for "score", "solve", "complete candidate", "fills in") |
| 27 | Deployment shape: compiler (seconds–minutes, once per identity) + oracle-file (µs–ms, millions of calls) | `1.2:70-81` | keep | `program/purpose/product#deployment-shape` | the *persisted-artifact* framing is unique to this page; the compose/runtime split itself duplicates `compose-time-pipeline` and `1.5:59-70` |
| 28 | What an oracle-file contains — callable, static slot schema, identity/content hash, certificate reference | `1.2:83-97` | keep | `program/purpose/product#oracle-file-contents` | sole statement; "file hash = kernel hash" appears only here |
| 29 | Behavioral rules: one file per crystal identity · environment-box validity · oracle-files are immutable | `1.2:99-113` | keep | `program/purpose/product#behavioral-rules` | sole statement of all three |
| 30 | Inputs (identity): "CIF content plus an environment record"; a CIF alone is a compile request, not a scoreable object | `1.2:117-122` | delete | cite `[crystal-inputs]` | stated a third time at `1.5:99-103`; `2.1-crystal-inputs` owns "top-level inputs" |
| 31 | State is a deliberate **superset** of any interchange format; the missing pieces are what the operator learns to supply | `1.2:124-128` | keep | `program/purpose/product#state-input` | keep once here; `1.5:104-108` restates it verbatim-in-substance |
| 32 | *Structural* well-formedness (shapes, finite values) is the caller's obligation; *physical* admissibility is scored, never presupposed | `1.2:129-130` | keep | `program/purpose/product#state-input` | sole statement of the obligation split; load-bearing for the seam |
| 33 | `Environment` (per call): the operating-condition record, varying within the file's stamped box | `1.2:132-133` | keep | `program/purpose/product#environment-input` | **homeless-fact instance.** The `Environment` record type is named here, at `8.6:37` phase 3, and in `compose-time-pipeline §1` signatures; no page's `canonical-for` claims it. Matches the brief's confirmed homeless fact |
| 34 | The `Validate(state, env, request, gradient) → residuals, values, cograds, kernel` signature block | `1.2:137-145` | delete | cite `[pino-bridge#call-contract]` | the page cites `pino-bridge §1` as its own source; the signature is `pino-bridge`'s. Keep a prose sentence naming the four returns |
| 35 | Keyed floats only; the residual value is **raw** — the oracle never normalizes, weights, sums, or judges across slots | `1.2:147-149` | delete | cite row 18 + `[residual-definitions]` | third statement on one page (§1 Mission, §1 Principles, §4) |
| 36 | The static schema carries per key: producing registry row, axis coordinates, closed-enum tags, error scale σ; **consumers compute `z = value/σ` themselves — a join against the schema, not a product output** | `1.2:151-156` | keep | `program/purpose/product#static-schema` | the "z is a join, not an output" rule appears only here and is a real boundary |
| 37 | Refusal is absence: an uncertifiable check is not in the kernel, so its key is not in any map; the reason is enum + numeric witness in the cert record | `1.2:158-161` | keep | `program/purpose/product#refusal-is-absence` | owner of the product-facing phrasing |
| 38 | Selection: compose-time scoping + call-time subsetting, both already in the architecture | `1.2:165-172` | keep | `program/purpose/product#selection` | sole statement |
| 39 | "*Recorded refinement (future `pino-bridge` edit, deliberately not made yet):* `request` should additionally accept the schema's closed-enum tags as selectors" | `1.2:173-176` | move | `oracle/seams/pino-bridge` `open-questions:` | a deferred-edit marker — the "we might change it later" shape D1 names. Either make the edit or carry it as an open question under D7; not as prose |
| 40 | `Import` pins `(named-target, value, σ, provenance, coverage-mask)` as a first-class check; two readings — reconciliation vs design | `1.2:180-190` | delete | cite `[pino-bridge#import]` | stated three times: here, `1.5:120-127`, and `pino-bridge §2` which both cite |
| 41 | "In the artifact model, `Import` is a compiler input" — new pins → new oracle-file → every result attributable | `1.2:192-195` | keep | `program/purpose/product#import-is-a-compiler-input` | unique to the product/artifact view |
| 42 | The two loops are mirror images: training sinks gradients into weights, design into the candidate; one oracle, one surface, two sinks | `1.2:197-200` | keep | `program/purpose/product#two-loops` | keep **here**; delete the duplicate at `1.5:129-132` |
| 43 | The design-variable boundary: continuous (cell, positions, composition fraction) directly optimizable; discrete (species, decoration, symmetry family) = enumerate-and-compile or external search | `1.2:202-208` | keep | `program/purpose/product#design-variable-boundary` | keep **here**; delete the duplicate at `1.5:132-137` |
| 44 | Static instantaneous-property design works today; **lifetime** design additionally requires a time-evolution capability this spec does not claim | `1.2:208-210` | keep | `program/purpose/product#design-variable-boundary` | related to C1; the claim itself is stable under either framing |
| 45 | The CLI: `compile` · `inspect` · `validate`; in-program loading is primary; nothing interactive, stateful, or daemonized | `1.2:214-224` | keep | `program/purpose/product#cli` | owner; `1.3:29-31` states only the *boundary* fact (the CLI ships inside `/physics`), which is distinct |
| 46 | What the product is not — 5 bullets (no state/evolution/training/loop; no aggregation or judgment; no runtime external simulation; no open-ended expressions; no natural language) | `1.2:226-235` | delete | cite rows 12, 18, 23 + `[canonical-vocabularies]` | every bullet restates a fact with an owner elsewhere on this page or on `1.1`/`1.3`. Collapse to a cite list |
| 47 | Open decision 1: time-evolution verbs unclaimed; scorer↔stepper duality **resolved "survives with restrictions"** — evolver is a flag-gated Stage-4 sibling sharing the scorer's RHS forests, integrator stays consumer-side | `1.2:242-251` | mine | `oracle/laws/generic-dynamics#evolver-duality` | cites `live/specs/2026-07-16-evolver-duality-research.md`, a container deleted per D13/§9. The **resolution** is a present-tense fact (brief exception 1). **Contradiction C2** with `1.5:211-216` |
| 48 | "§8 is preserved verbatim: the hand-off is tendencies, never trajectories" | `1.2:248-249` | delete | keep only the tendencies-not-trajectories clause | `§8` is a bare ordinal into a document being deleted; unresolvable after cutover |
| 49 | Open decision 2 (loading convention / ABI) and 3 (wire formats) | `1.2:252-257` | move | `oracle/seams/pino-bridge` `open-questions:` | D7/§5 — the owning page declares its own gaps |
| 50 | Open decision 4 (compile-cache management policy) | `1.2:258-260` | move | `oracle/compilation/representation-substrate` `open-questions:` | D7/§5; content addressing makes correctness free, only policy is open |
| 51 | The three-library partition `/physics` · `/informed-operator` · `/interface` | `1.3-library-landscape.md:16` | keep | **becomes `journals/oracle` · `operator` · `interface`** — and the page states it in prose | the partition *is* the top-level tree; the page survives because rows 53–56 are boundary facts a directory layout cannot encode. See Notes |
| 52 | `/physics` numerics-agnostic at its seam while internally committed to the representation substrate | `1.3:18-20` | delete | cite `[architectural-principles#numerics-agnostic]` | see row 24; three statements of one fact |
| 53 | `/physics` does **not** hold time-varying state values, train networks, integrate trajectories, or wrap external DFT codes at runtime | `1.3:22-24` | keep | `program/purpose/library-landscape#physics-boundary` | the runtime-DFT exclusion appears only here and at `1.2:231-232` |
| 54 | "This book is primarily about `/physics`." | `1.3:24` | delete | — | container self-reference, and false under D4: the corpus covers all three modules |
| 55 | `/informed-operator` is the PINO; consumes `/physics` and **learns the time-evolution operator**; seam contract + loss methodology live under `informed-operator/design/` | `1.3:25-27` | mine | `operator/seam` + `operator/loss` | the design directory is deleted per §9. **Contradiction C1** — this page states the time-evolution framing |
| 56 | `/interface` owns every driving loop — training, design search, active learning; not yet designed | `1.3:28-29` | keep | `program/purpose/library-landscape#interface` + seeds `interface/boundary` | pairs with row 13 |
| 57 | The oracle's own CLI ships **inside** `/physics`; `/interface` is the loops, not the command line | `1.3:29-31` | keep | `program/purpose/library-landscape#cli-lives-in-physics` | sole statement of this boundary; without it the tree implies the CLI is interface work |
| 58 | Engineering aspects (defects, dopants, surfaces, interfaces, operating-condition effects) live **inside** `/physics`, not a separate library | `1.3:33-34` | keep | `program/purpose/library-landscape#engineering-is-inside-physics` | sole statement; load-bearing against a fourth module appearing |
| 59 | `canonical-for: [architectural principles]` — the page's own id with the hyphen spelled as a space | `1.4:6-7` | delete | replace with ≥1 distinct topic | **vacuous ownership the plan's count of 18 misses.** Checker key is `" ".join(topic.lower().split())` (`check_book_structure.py:197`) — case- and whitespace-normalised, **not** hyphen-normalised. See Notes for the full list of 5 |
| 60 | P1 One compile pipeline over one substrate (4+1 stage pipeline over the content-addressed substrate) | `1.4:21-23` | keep | `program/purpose/architectural-principles#one-pipeline` | owner. "4+1 stage" containing a "Stage 2.5" is on the plan §4 rename list |
| 61 | "The earlier `core ← shared ← …` import chain is **retired**: it described a module layout that no longer exists." | `1.4:24-26` | delete | — | explicit history marker (§9, 105-line pattern). **Contradiction C4**: `8.5:19-20` and `8.6:35-36` still name build phases `core` and `shared` |
| 62 | P2 Minimum primitives — the 12-method vocabulary + 3 registered sub-methods is the closed primitive set | `1.4:27-29` | keep | `program/purpose/architectural-principles#minimum-primitives` | keep the *principle*; the counts duplicate `canonical-vocabularies` — cite, do not restate |
| 63 | P3 No symbolic computation on the runtime path | `1.4:30-31` | keep | `program/purpose/architectural-principles#no-runtime-symbolics` | owner |
| 64 | P4 Typed everything — explicit typed signatures, no string-encoded formulas, no implicit parameters | `1.4:32-33` | keep | `program/purpose/architectural-principles#typed-everything` | owner; `8.7:25-26` restates as a checkable item |
| 65 | P5 Composition over duplication | `1.4:34-35` | keep | `program/purpose/architectural-principles#composition-over-duplication` | owner |
| 66 | P6 Loud at compose time, absent at runtime; never *raised* from the kernel; runtime failure is a `Failed` cert leaf with a witness, never an exception | `1.4:36-40` | keep | `program/purpose/architectural-principles#loud-then-absent` | **owner of the refusal mechanics**; `1.2:59-61` and `1.2:158-161` are the product-facing restatements |
| 67 | P7 Cert is first-class — schema + freeze fixture + tamper tripwire + high-precision oracle | `1.4:41-42` | keep | `program/purpose/architectural-principles#cert-first-class` | sole statement of the four-part weighting |
| 68 | P8 Numerics-agnostic at the seam, committed within; emits readouts and residuals; integrator/trainer/PINO downstream; time-evolution verbs unclaimed | `1.4:43-49` | keep | `program/purpose/architectural-principles#numerics-agnostic` | **owner** — rows 24 and 52 collapse into this |
| 69 | `canonical-for: [rationale]` vacuous; `referenced-by: []`; `depends-on: [timeline]` alone while the prose cites 12 pages | `1.5-rationale.md:6-10` | delete | replace | vacuous ownership + **orphan page** (nothing in canon cites it; `contents.md:19` lists it, `10.3-audit-prompt:57` names it in a chapter map). The 12 uncited edges are all backticked → defect 1 |
| 70 | Header blockquote: "**Historical snapshot** — claims, counts, and status as of 2026-07-16"; "Presentation artifacts are dated and are never updated"; "the canon chapters (1–10) are canonical"; "cites its canonical `arch-xx` / `impl-xx` / audit source"; "This is a **presentation companion**" | `1.5:14-19` | delete | — | five distinct scaffolding markers in six lines: dated snapshot, staleness disclaimer, chapter-number authority, retired id formats, deleted-container role |
| 71 | "Purpose of this report." paragraph | `1.5:21-24` | delete | — | document-about-the-document; the page's purpose is its frontmatter under §4 |
| 72 | §1 The one-paragraph version | `1.5:30-41` | delete | cite rows 3, 17, 18 | every clause has an owner on `1.1` or `1.2`. **Exception, split out as row 73** |
| 73 | End goal is **property-targeted crystal design**: "you state the properties you need; the system searches for crystals simultaneously physically real and fit for purpose — and it can show its work" | `1.5:36-41` | move | `program/purpose/purpose-and-scope#downstream-target` | the design-direction goal; `1.1` states the *chip* target but never the properties-in-structures-out goal. Note `journal/live/specs/2026-07-21-oracle-code-spec-research-brief.md:11` calls this "a *direction*, not a mechanism" and says no proposer component is specified anywhere — flag for auditor 3 |
| 74 | §2 **Verifying is cheaper than solving** — direct simulation is prohibitively expensive, ML surrogates are untrustworthy exactly at extrapolation; the answer is a grader so cheap and complete the operator can be disciplined by it at every step; the learned half's known weakness is exactly what the oracle exposes | `1.5:43-55` | keep | `program/purpose/purpose-and-scope#why-a-grader` | **the single most load-bearing block on this page and it is stated nowhere else in canon.** The program's central justification. Cross-scope: `journal/live/presentations/2026-07-22-cs-framing-outline.md:102` develops it into a complexity-class argument and notes "None of that is in the corpus" |
| 75 | §3 `/physics` is a compiler paired with the pure functions it emits — compose time vs runtime | `1.5:59-70` | delete | cite `[computational-overview]`, `[compose-time-pipeline]` | third statement; see row 27 |
| 76 | §3 The grammar is closed — 132 substantive formulas (+2 markers), 12 methods (+3 sub-methods), 20 templates, 11 bundles, 19 residual categories, 10 obligations; enumerable / traceable / decidable | `1.5:73-82` | delete | cite `[canonical-vocabularies]` | duplicate counts, **and unswept**: probe D shows "132 substantive **named** formulas" evades the count-drift regex. Keep the enumerable/traceable/decidable triad → move to `program/purpose/purpose-and-scope#why-a-grader` |
| 77 | §3 Identity is content-addressed; same inputs → bit-identical kernel; reproducibility is structural, not policy | `1.5:83-87` | delete | cite `[representation-substrate]` | duplicate of `1.2:92-95` and the substrate page |
| 78 | §3 The output is evidence, never a verdict | `1.5:88-95` | delete | cite row 18 | fourth statement of one fact across `1.2` §1/§4/§8 and here |
| 79 | §4 The interfaces (in: identity/CIF+env · in: state superset · out: four things) | `1.5:97-112` | delete | cite rows 30, 31, 34 | wholesale duplicate of `1.2` §3–§4 |
| 80 | §5 One framework, two loops — `Import`, measured datum ≡ desired property, mirror-image loops, continuous/discrete design variables | `1.5:114-139` | delete | cite rows 40, 42, 43 | wholesale duplicate of `1.2` §6 |
| 81 | §6 **Is a neural operator the right learner?** — periodic domain is the native habitat of spectral operators; the state really is function channels; discretization invariance is a requirement not a luxury; supervision is native (pointwise residuals + synthesized gradients) | `1.5:141-156` | move | `operator/seam#why-a-neural-operator` | **unique and load-bearing.** The only argued justification in canon for the choice of learner |
| 82 | §6 Caveats: not everything is a field (sites are a point set, species discrete) ⇒ hybrid architecture; localized features strain global spectral bases; long-horizon rollout drift is the known failure mode | `1.5:157-165` | move | `operator/seam#known-failure-modes` | the only statement of the operator's failure modes in canon; directly relevant to auditor 3 |
| 83 | §6 The compiler's symmetry analysis produces the exact block structure an equivariant network needs — the oracle can *hand the operator its equivariance* | `1.5:162-165` | move | `operator/seam#equivariance-handoff` | a concrete unexploited seam capability, stated once |
| 84 | §6 `Learnable_Structure` — a kernel for compiling arbitrary learnable structures; mirror-image of the oracle's compiler; one grades, one learns | `1.5:167-171` | mine | `operator/seam/learnable-structure` | the workstream named in `informed-operator/design/learnable-structure-requirements.md`, a container deleted per §9 |
| 85 | §7 A certified specification base — 58 pages, **99 canonical topics**, dependency graph, closed vocabularies, tolerance ledger, 10 obligations with four refusal modes | `1.5:175-179` | delete | — | corpus self-description; regenerated into `index/corpus.json` per §6. **Contradiction C3: 99 vs the measured 98** (checker prints `98 canonical topics`; my scan of all 58 pages agrees) |
| 86 | §7 The 2026-07-16 reconciliation campaign: ~88 defects, calibration-gated auditors (5/5 planted contradictions), two rounds, evidence transcripts | `1.5:179-184` | delete | — | history. **Log-worthy #1** |
| 87 | §7 "The one waiver that campaign carried — a stale formula count in the CS-audience deck — was **discharged** when the deck was retired; **no waiver stands today**" | `1.5:184-187` | delete | — | closed-item story. The resolution ("no waiver stands") is the absence of a thing, not a fact needing a home. **Log-worthy #2** |
| 88 | §7 "A 2026-07-21 pass then re-audited the campaign's own bulk edits adversarially and corrected what they had broken" | `1.5:187-188` | delete | — | history. **Log-worthy #3** — and materially relevant: it is the pass that produced the D4 retag behind defect 6 |
| 89 | §7 "held there by two standing checkers covering twelve structural invariants and sixteen mechanical sweeps, plus a third tool that calibrates them — **58 probes** … plus a gate that refuses green if any check has no probe at all" | `1.5:188-192` | delete | — | tooling self-description; §8 rebuilds `check_the_checkers.py` against the new rule set, so every count here goes stale at cutover |
| 90 | §7 Seeded, σ-disciplined reference data; genuine gaps marked `GAP` and **refused by the certification layer rather than filled by guesswork** | `1.5:193-196` | move | `oracle/accuracy/reference-battery#gap-discipline` | the *rule* is live and load-bearing; the 2026-07-08 seeding date is history. `GAP` is overloaded three ways (`[traps] §59`) — plan §4 rename list |
| 91 | §7 Training feedstock: recovered **1,179-row** HSE06 gap-tuned strain hypersurface of diamond, **1,131 distinct** strain shapes after de-duplication, six lattice-distortion families to ±10%, with stress tensors, mapped onto the import interface | `1.5:197-204` | move | `oracle/accuracy/reference-battery#diamond-strain-hypersurface` | **live and load-bearing** — this is the MVP's ground-truth feedstock for mechanics, energetics, and gap-vs-strain, and `8.2:48-50` already depends on it for Cap-1's data-backed sensitivity test. No page in canon owns the dataset |
| 92 | §7 "the ~877 figure quoted earlier was the byte-salvage count, not the row count, and de-duplication must precede any fit" | `1.5:199-201` | delete | keep the de-dup rule only | correction-of-a-past-number is history; **"de-duplication must precede any fit" is a live methodological guard** → carry it to row 91's target. **Log-worthy #4** |
| 93 | §7 A concrete first build — three capabilities, ~34 formulas, 10 of 12 methods, obligations 1–6 and 10, written build order | `1.5:205-208` | delete | cite `[mvp-scope]`, `[build-order]` | duplicate of `8.3:17-33` |
| 94 | §8 The evolver question — "a live research question **we are commissioning as an independent deep-dive**. Until it resolves, time-evolution product verbs stay unclaimed" | `1.5:210-216` | delete | cite row 47 | **Contradiction C2** — `1.2:242-251` says the same research **resolved** ("survives with restrictions"). One page says commissioned, the other says resolved |
| 95 | §8 The wave program — β-Ga₂O₃ next, seeding spec "drafted and **frozen pending its adversarial audit**"; then c-BN/4H-SiC, contact metals and substrates, gate dielectrics | `1.5:217-220` | mine | `oracle/accuracy/reference-battery#wave-program` | cites `live/specs/2026-07-08-wave2-beta-ga2o3-seeding.md`, a deleted container. The **wave ordering** is live; the "frozen pending audit" status is **stale** — see Open question `beta-ga2o3-wave-status` |
| 96 | §8 Known unknowns kept visible — measured impact ionization for AlN, hole transport, hot-carrier tail anchors recorded as cert-refused domains | `1.5:221-224` | move | `oracle/certification/out-of-scope#known-data-gaps` | live refusals; `5.3-out-of-scope` owns "scope exclusions" and does not currently list them |
| 97 | §9 The close | `1.5:226-234` | delete | — | rhetorical summation; every claim restated from §3 and §7 |
| 98 | Diamond primitive cell: Fd-3m (No. 227), 2 C at 8a Wyckoff, sp³, a = 3.567 Å, 8 valence electrons → **4 occupied bands** | `8.1-mvp-system.md:16-18` | keep | `program/build/mvp-system#the-cell` | sole statement; the 4-occupied-bands consequence is load-bearing for Cap 2 |
| 99 | Anchor table **value column** — 5.47 eV, ~165 meV, ~2200 K, ~2200 W·m⁻¹K⁻¹, C₁₁≈1079 / C₁₂≈124 / C₄₄≈578 GPa | `8.1:20-28` | delete | cite `physics/library/cert/reference-data/*.csv` | verified duplication: every value matches `material-constants.csv:27-28`, `elastic-tensors.csv:17,19`, `phonon-frequencies.csv:16-17`, `transport-coefficients.csv:33`. **Circular provenance** — those CSV rows record their own provenance as "curated MVP anchor (mvp-system)" while this page states the numbers. Per the brief, values seed from the ledger and the CSVs, never the other way |
| 100 | Anchor table **consequence column** — CBM sits on Δ at ≈0.76 Γ→X, *not* at X, and the six-fold Δ valley degeneracy is what the effective-mass and transport rows consume; PBE −23% ⇒ G₀W₀/hybrid required; phonon grid must resolve 165 meV; Θ_D ~2200 K ⇒ QHA valid through ~800 °C ⇒ SCPH (row 13) deferred; non-polar ⇒ Z\*=0 ⇒ registry rows 17, 21, 22 excluded by applicability | `8.1:22-27` | keep | `program/build/mvp-system#mvp-consequences` | **the page's unique content.** Each consequence is a design decision derived from an anchor and stated nowhere else |
| 101 | High-T failure: air-oxidation onset ~600–700 °C is the actual lifetime limiter; graphitization only above ~1500 °C in vacuum; the diamond–graphite boundary is the Cap-1 thermodynamic check; oxidation is the slow-tier degradation channel | `8.1:28` | keep | `program/build/mvp-system#high-t-failure` | **load-bearing for `[traps] §43`**, which names `[mvp-system]` as its enforcement point (`10.4-traps.md:299-301`) |
| 102 | Units: atomic units internally; report eV, Å, W·m⁻¹K⁻¹, cm²V⁻¹s⁻¹ | `8.1:30` | move | `practice/conventions#units` | a corpus-wide convention stated on an MVP page; `10.1-conventions` owns conventions |
| 103 | Each capability is a strict selection from the closed vocabularies, residual categories, and cert obligations; formula numbers reference the registry manifest | `8.2-capability-slices.md:19-22` | keep | `program/build/capability-slices#selection-discipline` | the discipline statement; owner |
| 104 | Cap 1 table — state used, BO levels, 6 methods, 5 templates, 12 formulas (57/60/61/62/85/30/44/52/54/67/124), bundles, residuals, cert 1/2/3/5, implementation | `8.2:24-39` | keep | `program/build/capability-slices#cap-1` | sole statement of Cap-1's vocabulary selection |
| 105 | Cap 1 acceptance test — null (ground-truth diamond returns ≈0 within σ), sensitivity (the specific keys that fire name the violated law), data-backed sensitivity against the strain hypersurface | `8.2:41-50` | move | `program/build/build-verification#first-end-to-end-gate` | labelled "**first end-to-end gate**" yet it sits on the capability page while `build-verification` owns "verification gates" and does not mention it. Either move it or make 8.7 cite it — do not leave the gate set split across two pages |
| 106 | Cap 2 table — state, BO levels L1+L4, 4 methods, 5 templates, 13 formulas, bundles B1/B3, residuals, cert 1/2/5/6, implementation | `8.2:52-67` | keep | `program/build/capability-slices#cap-2` | sole statement |
| 107 | Cap 2 Excluded (non-polar): rows 17, 21, 22 masked off by the `is-polar-material` classifier (false for diamond) | `8.2:63` | keep | `program/build/capability-slices#cap-2` | restates row 100's polarity consequence. One owner needed — recommend the *rule* stays on `mvp-system`, the *masked row list* stays here |
| 108 | Cap 3 table — state, BO levels L2+L3+L4, 3 methods, 4 templates, formulas 7–12/25/121/122/70, deferred 13/26/27, bundles, residuals, cert 2/3/5 | `8.2:69-84` | keep | `program/build/capability-slices#cap-3` | sole statement |
| 109 | The QHA + Slack/Callaway κ is a **consistency pair, not an equivalence pair** — no agreement theorem, only a bounded model gap; obligation-6 trips on excess beyond `τ_method`, not on disagreement; calling it a method-equivalence would score a legitimate model gap as a bug | `8.2:84` | move | `oracle/seams/cross-cutting-rules#consistency-vs-equivalence-pairs` | a cross-cutting rule buried in a table cell on an MVP page; the cell itself cites `[cross-cutting-rules]` and `[traps] §29` |
| 110 | "In the MVP": ~34 formulas of 132 · 10 of 12 methods · 10 of 20 templates · bundles B1/B2/B3/B7/B10 primary with all 11 touched · six residual families · obligations 1–6 **and 10** · Layers 1 + 1.25 | `8.3-mvp-scope.md:17-34` | move | `program/build/capability-slices#mvp-totals` | **merge recommendation.** Every total is a summation over the three Cap tables in `8.2`. Two pages that must be edited together to stay correct are one page |
| 111 | "~34 named formulas (**the rows above**, incl. the κ high-T siblings 121–122 and the hull pair 67/124)" | `8.3:18-19` | delete | — | "the rows above" points at `8.2`'s tables — a pre-book pointer that broke when the monolith was split. Unresolvable as written; the merge in row 110 repairs it by construction |
| 112 | Obligation 10 (registration adjoint gate) **stays** in the MVP because D2 gradients must be validated when the PINO first trains; only 7–9 defer | `8.3:31-33`, `8.3:41-42` | keep | `program/build/capability-slices#mvp-totals` | stated twice on one page (In-MVP and Deferred both argue it) — collapse to one |
| 113 | "Deferred (the other ~⅔)": remaining ~100 formulas, defect zoo beyond row 30, surface chemistry, interface/Schottky, high-field/hot-carrier/breakdown, degradation, most of the topology atlas (rows 96–102) | `8.3:35-40` | move | `oracle/certification/out-of-scope#mvp-deferrals` | `5.3-out-of-scope` owns "scope exclusions" and already carries an overlapping deferral list |
| 114 | Deferred: "**Layer 1.75** (iterative dressing), SCPH/SSCHA, **the D4 surrogate nets**, the non-diamond materials, heterostructures beyond the single c-BN lattice-match" | `8.3:43-44` | move | `oracle/certification/out-of-scope#mvp-deferrals` | **stale vocabulary, second instance of defect 6.** The 2026-07-21 retag changed `D4` from *surrogate* to *relaxed*; "the D4 surrogate nets" names a set that no longer exists — the same failure the plan documents at `10.2-open-decisions` item 1, realized again here and not in the plan's inventory. `Layer-1.75` is on the plan §4 rename list |
| 115 | "The buildable unit is roughly one-third of the full vocabulary." | `8.3:46` | keep | `program/build/capability-slices#mvp-totals` | the one sentence on this page that is a judgment rather than a sum |
| 116 | **Implementation language (H1) — resolved.** Concrete needs met by a polyglot of DSLs: a compiler host for Stages 1–4 + the substrate that emits source for a separate runtime host (owning optional GPU codegen), plus an offline group-theory engine and an offline proof assistant. **The four-role shape is settled; the languages filling the roles are not** | `8.4-forced-decisions.md:21-29` | keep | `program/build/forced-decisions#implementation-language` | **owner — and this fact is stated four times.** Here, `8.6:24-30`, `10.2-open-decisions:83-90` (open item 6), `10.2-open-decisions:169-179`. Recommend this page owns it; the open picks become an `open-questions:` entry here (`implementation-language-picks`) |
| 117 | **TB-3NN-sp³d⁵ for carbon as warm-start initializer** — a seed for the SCF inner loop only; not a separately-evaluated formula and not an independent residual | `8.4:30-32` | keep | `program/build/forced-decisions#tb-warm-start` | owner. Restated three times: `8.2:39` (Cap 1), `8.2:67` (Cap 2), `8.5:24` (step 6). The "not a residual" qualifier appears **only here** and is the part that prevents a modelling error |
| 118 | **Layer-1.25 substrate data (H7)** — G₀W₀ needs ~30–50 unoccupied bands + wavefunctions; QHA needs volume-dependent (Grüneisen) phonons; these are the L1 outputs the MVP requires | `8.4:33-36` | keep | `program/build/forced-decisions#layer-125-substrate-data` | sole statement of the L1 output requirement |
| 119 | "— specify them when building `state/level-1`." | `8.4:36` | move | `oracle/state/born-oppenheimer-levels` `open-questions:` | a build-time TODO in prose; under D7 an unspecified requirement is an open question on the owning page |
| 120 | **Reference-battery seed (H4)** — the full diamond battery enumerated (lattice a, gap, C₁₁/C₁₂/C₄₄ + bulk modulus + density, Θ_D, max phonon energy, κ(300 K), **κ(773 K) ≈ 620 W/m·K**, κ(1100 K), cohesive energy, diamond–graphite boundary point, ε_r, Isberg ToF mobilities, v_sat/β, Chynoweth pair) | `8.4:37-43` | move | `oracle/accuracy/reference-battery#diamond-battery` | a battery inventory on an MVP page; `9.2-reference-battery` owns it and already cites back (`9.2:52` cites "`forced-decisions §H4`" — the dependency runs the wrong way). "seeded 2026-07-08" is history |
| 121 | **Design-grade accuracy targets (H8)** — gap ±0.15 eV post-G₀W₀, C_ij ±5%, κ(300 K) ±20%, E_form ±0.2 eV, μ factor-2; cert obligation 4 checks them at the battery anchors | `8.4:44-48` | delete | cite `[accuracy-ledger]` | the page says so itself: "full per-observable ledger in [accuracy-ledger]". Restating five tolerances beside their ledger is the drift class D7 exists to prevent |
| 122 | "the high-T anchors κ(773 K)/κ(1100 K) are **landed** (registry rows 121–122 …)" | `8.4:48-50` | delete | — | closed-item framing; the anchors are facts on the ledger and the registry, and the story of them landing is history |
| 123 | The `H1` / `H4` / `H7` / `H8` labels themselves | `8.4:21,33,37,44` | delete | renumber or drop | **a fourth identifier namespace, defined nowhere.** Only H1/H4/H7/H8 exist — H2/H3/H5/H6 appear nowhere in the corpus — yet they are cited across pages (`8.5:27` "`forced-decisions` H4"; `9.2:52` "`forced-decisions §H4`"). Worse, `H1` collides with a second series: `2.4-multiscale-state.md:198,434,436` uses `F-H1` for a formula from `deriv-high-field` Part H. Same overload class as `GAP` (`[traps] §59`) |
| 124 | "A focused subset of the phases in `build-sequence`" + the 9 MVP build steps (`core`, `shared`, `inputs`, `state`, methods+formulas, canonicals, capability residuals, cert+battery, validate) | `8.5-build-order.md:17-29` | move | `program/build/build-sequence#mvp-column` | **merge recommendation.** This page is a projection of `8.6`'s phase table filtered by `8.3`'s scope. Express it as an in-MVP column on the one phase table; the projection then cannot drift from its source, and the omission in C6 becomes impossible |
| 125 | Steps citing `(§2)`, `of §3`, `(Cap 1/2/3 rows above)` | `8.5:22,23,25` | delete | rewrite as `[page#anchor]` | three bare cross-page pointers into `8.2`/`8.1` that broke when the monolith was split; plan §4 removes bare ordinals |
| 126 | "Completing this slice yields a diamond-only `/physics` that can emit a granular residual vector with cotangents, expose observable values, and certify them for all three capabilities — the concrete substrate `/informed-operator` then trains against" | `8.5:31-34` | keep | `program/build/build-sequence#mvp-exit-criterion` | the MVP's exit criterion, stated only here. **Contradiction C6** — it requires phase 13 (`API seal + pino-bridge`), which the build order omits |
| 127 | `canonical-for: [build sequence]` — the page's own id with the hyphen spelled as a space | `8.6-build-sequence.md:6-7` | delete | replace with ≥1 distinct topic | second in-scope instance of the hyphen-variant vacuous claim; see row 59 and Notes |
| 128 | Intro restating the four-role polyglot language shape | `8.6:24-29` | delete | cite row 116 | duplicate of `8.4:21-29`, down to the same two citations |
| 129 | "The phases below are language-neutral: none of them depends on the pick, which is why the pick can stay open this long." | `8.6:29-30` | keep | `program/build/build-sequence#language-neutrality` | the justification for leaving `implementation-language-picks` open; stated here and paraphrased at `10.2-open-decisions:89-90` |
| 130 | The 14-phase build table (Phase 0 scaffold → Phase 13 API seal + pino-bridge), each with scope and verifiable artifact | `8.6:32-47` | keep | `program/build/build-sequence#phases` | **owner** — the full build plan for `/physics`; nothing else states it |
| 131 | Phase 7's **applicability-decidability gate** — every classifier first-order decidable on typeclass tags; non-decidable entries rejected | `8.6:41` | keep | `program/build/build-sequence#phases` | a hard admission rule stated in a table cell; cites `named-formulas` |
| 132 | Phase 8's Stage-2.5 invariant synthesis instantiating active `CouplingSpec` and attaching generated `InvariantTerm`s | `8.6:42` | keep | `program/build/build-sequence#phases` | cites `coupling-structure`; "Stage-2.5" inside a "4+1 stage" pipeline is on the plan §4 rename list |
| 133 | Recommended start order (1–7, then 8–10, then 11–12, then 13) | `8.6:49-51` | keep | `program/build/build-sequence#phases` | fold into the table as an ordering column rather than a second statement of the same sequence |
| 134 | §1 Internal consistency, items 1–7 — every observable invokes only registered methods/templates/formulas; typed signatures with no string-encoded parameters; the directory tree contains every named concept; nine regime extractions realizable as typed compositions; every residual category grounded; every cert obligation maps to a Layer-0 axis; counts match | `8.7-build-verification.md:19-36` | keep | `program/build/build-verification#static-consistency` | owner of the static gate set. **Every `§`-ordinal in it (`§2`, `§3`, `§4`, `§6`, `§7`, `§10`) points into the pre-book monolith and must be rewritten to `[page#anchor]`** |
| 135 | Item 3's requirement that the tree contain every concept named "in this plan and in `architecture.md`" | `8.7:27-28` | delete | repoint at the real owners | **`architecture.md` does not exist anywhere in the repo** (`find . -name architecture.md` → nothing). A live dangling reference in canon, invisible to the checker because it is backticked — probe B/C confirm the asymmetry. Same class as defect 2. "this plan" is a pre-book self-reference |
| 136 | Item 7's count restatement — 12 methods, 20 templates, 132 formulas, 11 bundles, 19 residual categories, 10 cert obligations | `8.7:35-36` | delete | cite `[canonical-vocabularies]` | **unswept duplication.** Probe C: corrupting "132 formulas" here to "999" leaves the checker green, because the count sweep requires the adjacent phrase "substantive formulas". Restating six guarded numbers in an unguarded phrasing is a drift generator |
| 137 | "Once the Phase-0 skeleton exists, items 1–7 are checkable mechanically by walking the tree and the registry manifest." | `8.7:38-39` | keep | `program/build/build-verification#static-consistency` | the mechanization claim; the point of the whole section |
| 138 | Gate 1 Registration sanity — all 132 formulas instantiate; every `D2` **and** `D3` passes the registration-time adjoint gate; `D3` additionally passes the fixed-point-Jacobian conditioning check; `D4` carries an obligation-9 rationale naming its relaxation; `D0`/`DN` register without an adjoint; `D1` without a gate | `8.7:45-51` | keep | `program/build/build-verification#gate-1-registration` | owner of the per-D-tag registration rules. **Cross-scope trap:** this is the live legend; `11.8-deriv-generator-catalog` uses a retired one in which `D3` and `D0` mean something else (plan §2). Anyone mining 11.8 into this must not seed the tags from there |
| 139 | Gate 1 **Fidelity pairing** — every generator whose lowering introduces representation error registers its paired fidelity generator; a missing pairing **fails the build**, not a warning | `8.7:51-58` | keep | `program/build/build-verification#gate-1-registration` | the enforcement statement for `residual-machinery §4.1`; cites `[traps] §64` and `§58` (a build that passes without checking looks like a build that checked) |
| 140 | The adjoint-tape materialization schedule is the one lowering **exempt** by construction — it changes cost, not value | `8.7:58-61` | keep | `program/build/build-verification#gate-1-registration` | the sole stated exemption; without it the pairing rule is over-broad |
| 141 | Gate 2 End-to-end worked example — Diamond–W Schottky at 500 °C, `Environment(T = 773 K, field = 1 MV/cm)`; L3 ↔ non-equilibrium cycle closes by same-pass fixed point in ≤ 5 iterations; ~three dozen residuals accounted for; obligations 1, 2, 3, 5, 8 emit verdicts | `8.7:62-69` | keep | `program/build/build-verification#gate-2-worked-example` | owner. Partially restated at `4.4-computational-overview.md:529` — cross-scope with the compilation surveyor |
| 142 | Gate 3 Curriculum sanity — "a **three-phase** training run on Si bulk (~5 observables, ~1k samples) completes without GradNorm divergence, without a Layer-3 ↔ non-equilibrium fixed-point failure, and without an adjoint-cert reset mid-training" | `8.7:70-73` | keep | `program/build/build-verification#gate-3-curriculum` | **Contradiction C7** — `7.2-residual-machinery.md:218` says three phases (Warmup → Refine → Polish); `11.8-deriv-generator-catalog.md:332` says four (Warmup \| Refine \| Calibrate \| Polish) and `11.8:447` schedules work at a "Refine→Calibrate" boundary. Also operator-side content on a `/physics` build page — cross-link `operator/training` |
| 143 | Gate 4 Cross-regime cert obligations fire — obligation-6 (BTE-σ ≡ Kubo-σ), obligation-9 (out-of-domain D4 trips with a witness), obligation-10 (broken adjoint refused at registration), obligation-7 (diamond emits NA with rationale; a contrived Z₂ system emits the predicted edge-state count) | `8.7:74-79` | keep | `program/build/build-verification#gate-4-obligations` | sole statement of the obligation-firing tests |
| 144 | Gate 5 `/informed-operator` integration smoke test — `Validate` with `gradient = Skip` populates labels for ~10 Si observables; with `Compute` returns finite scalars and cotangents of the declared shape on a randomly-initialized state; `Import` accepts a synthetic VASP-formatted payload and returns `GroundTruthBridgeGenerator`s with coverage masks | `8.7:80-86` | keep | `program/build/build-verification#gate-5-seam-smoke-test` | sole statement of the seam acceptance test; the only place a VASP-formatted `Import` payload is named as a build requirement |

---

## Open questions

| id | question | owning page | why it is open |
|---|---|---|---|
| `implementation-language-picks` | Which language fills each of the four polyglot roles (compiler host, runtime host, group-theory engine, proof assistant)? | `program/build/forced-decisions#implementation-language` | The four-role shape is settled; the picks are not. `deriv-language-study` records Haskell / Julia / GAP / Lean 4 as candidates and, more usefully, which requirement each was chosen to satisfy. Nothing in the build order depends on the pick (`8.6:29-30`), which is why it can stay open. Currently stated as open item 6 on `10.2-open-decisions`, which dissolves per §3 |
| `layer-125-l1-exposure` | What exactly must L1 expose at Layer 1.25 — the unoccupied-band count and wavefunction format for G₀W₀, and the volume-dependent Grüneisen phonon outputs for QHA? | `oracle/state/born-oppenheimer-levels` | `8.4:36` defers it in prose: "specify them when building `state/level-1`". The requirement is named; the specification does not exist |
| `validate-request-selectors` | Should `Validate`'s `request` parameter accept the static schema's closed-enum tags as selectors, so subsetting never requires enumerating keys? | `oracle/seams/pino-bridge` | Recorded at `1.2:173-176` as a "future edit, deliberately not made yet". Selector sugar over existing enums; no new machinery |
| `beta-ga2o3-wave-status` | Is the β-Ga₂O₃ wave still "frozen pending its adversarial audit"? | `oracle/accuracy/reference-battery#wave-program` | `1.5:217-220` states frozen-pending-audit as of 2026-07-16 and cites a `live/specs/` file being deleted. The status is a dated snapshot on a page that disclaims being updated; the successor page needs the current state, which I cannot establish from the corpus |
| `oracle-file-abi` | How is the loading convention / ABI for a non-native program calling an oracle-file resolved — native module, flat-array C-style ABI, or both? | `oracle/seams/pino-bridge` | `1.2:252-255`. The abstract contract (one self-describing file, flat arrays at the boundary) is fixed; the container is not |
| `oracle-file-wire-formats` | What are the wire formats for state files, residual/value maps, and the schema table on the CLI surface? | `oracle/seams/pino-bridge` | `1.2:256-257`. Constrained by canonical-serialization discipline; otherwise open |
| `compile-cache-policy` | What is the compile-cache management policy (eviction, sharing, provenance listing) that enumerate-and-compile design searches rely on? | `oracle/compilation/representation-substrate` | `1.2:258-260`. Content addressing makes correctness free; only policy is open |
| `environment-schema` | Which page owns the `Environment` record type? | `oracle/state/crystal-inputs` (proposed) | Named in signatures at `1.2:132-133`, `8.6:37`, and `compose-time-pipeline §1`; claimed by no `canonical-for`. Confirms the brief's homeless-fact finding from a second direction |
| `diamond-dataset-owner` | Does the diamond strain-hypersurface dataset (1,179 rows / 1,131 distinct) get a canonical owner, and is it reference data or training feedstock? | `oracle/accuracy/reference-battery` (proposed) | Stated only at `1.5:197-204`, on a page that disclaims being current, while `8.2:48-50` already depends on it for Cap-1's data-backed sensitivity test. A load-bearing dataset with no owner |

---

## Log-worthy advancements

| date | finding or decision | evidence | attribution | superseded |
|---|---|---|---|---|
| 2026-07-16 | Reconciliation campaign: the full specification base passed a staged sweep finding and fixing ~88 verified defects, followed by adversarial multi-agent certification. Auditors were calibration-gated (5/5 planted contradictions detected before their reports were trusted), ran two independent rounds (first by document family, then re-sliced by invariant class), and produced evidence transcripts rather than verdicts. | `1.5-rationale.md:179-184`; `10.5-timeline.md §2026-07-16 (reconciliation pass)` | multi-agent audit campaign | — |
| 2026-07-16 | The scorer↔stepper duality research resolved **"survives with restrictions"**: the evolver is a flag-gated Stage-4 sibling artifact ("evolver-file") sharing the scorer's content-addressed RHS forests, with the integrator staying consumer-side. Time-evolution product verbs remain unclaimed until that lowering is specified and built as its own named wave (slow tier first); when trajectories exist, the scorer audits them under the same slot keys. | `1.2-product.md:242-251`; `10.2-open-decisions.md:213-216,258-259` | evolver-duality deep-dive | supersedes the "commissioning an independent deep-dive" status still stated at `1.5-rationale.md:211-216` — see Contradiction C2 |
| 2026-06-25 | The single waiver carried by the reconciliation campaign — a stale formula count in the CS-audience deck — was discharged by retiring the deck. No waiver stands. | `1.5-rationale.md:184-187`; `10.5-timeline.md §2026-06-25 (CS-audience deck)` | reconciliation campaign follow-up | — |
| 2026-07-21 | An adversarial pass re-audited the reconciliation campaign's own bulk edits and corrected what those edits had broken. Recording this matters beyond the fix: it is the pass whose D4 retag (*surrogate* → *relaxed*) left two live references to a "D4 surrogate" set that no longer exists (`10.2-open-decisions` item 1, and `8.3-mvp-scope.md:43`). | `1.5-rationale.md:187-188`; `8.3-mvp-scope.md:43-44` | adversarial re-audit | supersedes the *surrogate* reading of the D4 tag |
| 2026-07-16 | Diamond strain-hypersurface feedstock characterised: 1,179 rows at hybrid level (HSE06, gap-tuned exact exchange), **1,131 distinct strain shapes after de-duplication**, six lattice-distortion families to ±10%, with stress tensors, mapped onto the oracle's import interface. Methodological guard established: **de-duplication must precede any fit.** | `1.5-rationale.md:197-204` | dataset salvage + health audit | supersedes the ~877 figure, which was a byte-salvage count and never a row count |
| 2026-07-08 | Diamond reference battery seeded with a machine-readable anchor for every declared accuracy target, including the high-T 4-phonon anchor κ(773 K) ≈ 620 W/m·K and κ(1100 K), landing as registry rows 121–122 (closed-form 4-phonon correction + dormant iterative-LBTE consistency sibling). | `8.4-forced-decisions.md:37-50`; `physics/library/cert/reference-data/transport-coefficients.csv` | battery seeding pass | — |
| 2026-07-21 | The identity/ε rule closed three of the four named verifier-soundness gaps. Recorded here because `8.7`'s registration gate depends on which gaps remain live. | `10.2-open-decisions.md:94-97` | 2026-07-21 pass | supersedes three of the four originally-named gaps |

---

## Contradictions — COLLECTED, NOT RESOLVED

| claim | source A | source B | nature of the conflict |
|---|---|---|---|
| **C1 — What the operator does.** Completion vs time-evolution. | `1.1-purpose-and-scope.md:19-20`: the PINO "predicts the **time evolution** of the state of a crystalline material". Also `1.3-library-landscape.md:25-26`: `/informed-operator` "learns the **time-evolution operator**" | Javier: the operator returns the channels **not supplied**, given a topology plus known properties — completion. Consistent with `1.2-product.md:124-128`: "the missing pieces are precisely what the neural operator **learns to supply**" and `1.5-rationale.md:104-108` | Two incompatible readings of the operator's job, both in canon, one of them twice. Auditor 2 owns it. **Pages in my scope that state or depend on the framing:** `1.1` (rows 2, 7), `1.3` (row 55), `1.2` (rows 31, 44, 47), `1.4` (row 68), `1.5` (rows 81, 82, 94), `8.7` (row 142, curriculum gate). The oracle side is not in tension — `1.2:67-68` score-not-solve holds under either reading |
| **C2 — Is the evolver research commissioned or resolved?** | `1.2-product.md:242-251`: the scorer↔stepper duality research "**resolved** *survives with restrictions*"; the evolver is a flag-gated Stage-4 sibling artifact | `1.5-rationale.md:211-216`: "a live research question we are **commissioning as an independent deep-dive**. Until it resolves, time-evolution product verbs stay unclaimed" | Same research question, two mutually exclusive states, both present-tense in canon. `10.2-open-decisions.md:213-216` sides with `1.2` ("verdict: survives with restrictions"), making `1.5` the stale source — but `1.5` carries no marker saying so beyond its blanket "as of 2026-07-16" header |
| **C3 — Canonical topic count.** | `1.5-rationale.md:176`: "**99** canonical topics each owned exactly once" | `check_book_structure.py --check` at 2af93d2 prints "58 pages, **98** canonical topics"; my independent parse of all 58 pages' `canonical-for` blocks also yields 98 | Off by one in a page that presents the number as an audited fact. Trivial to fix, non-trivial that a self-description in canon disagrees with the tool that certifies it and no check compares them |
| **C4 — Is the `core ← shared` module chain retired or is it the build plan?** | `1.4-architectural-principles.md:24-26`: "The earlier `core ← shared ← …` import chain is **retired**: it described a module layout that no longer exists" | `8.5-build-order.md:19-20` steps 1–2 are `core` and `shared`; `8.6-build-sequence.md:35-36` phases 1–2 are "(`core`)" and "(`shared`)" | One page declares a naming scheme dead; two others build against it. Either the retirement is wrong or three pages name modules that do not exist. Note the retirement sentence is itself scaffolding (row 61), so resolving C4 cannot be done by deleting it |
| **C5 — The material anchor set.** | `1.1-purpose-and-scope.md:44-47`: c-BN, AlN, GaN, β-Ga₂O₃, AlGaN; contact metals W, Mo, Pt, Ti, Ni, Ta, TiN, WSi₂; substrates SiC, Si, sapphire; dielectrics Al₂O₃, HfO₂, AlN-as-dielectric | `11.5-deriv-high-field.md:26`: diamond, c-BN, **h-BN**, AlN, GaN, β-Ga₂O₃, AlGaN; refractory metals W, Mo, **Re, Ir**, TiN, **TaN**; dielectrics **SiO₂**, Al₂O₃, HfO₂ | Neither set is a subset of the other: A adds Pt/Ti/Ni/Ta/WSi₂ and the substrate class; B adds h-BN/Re/Ir/TaN/SiO₂ and omits substrates entirely. `1.1` owns "purpose" and should own scope; the appendix is being mined, so the merged set must be decided rather than inherited |
| **C6 — The MVP build order omits phases the MVP requires.** | `8.5-build-order.md:17`: "A focused subset of the phases in `build-sequence`", listing 9 steps; closing at `8.5:31-34` claims the result is "the concrete substrate `/informed-operator` then trains against" | `8.6-build-sequence.md:32-47` has 14 phases. `8.5` omits phase 6 (templates), 8 (GENERIC operators), 10 (observables), 12 (dynamics), and 13 (API seal + `pino-bridge`) — yet `8.3-mvp-scope.md:21` puts "10 of the 20" templates in the MVP, `8.3:24-26` puts five bundles in as primaries, and the exit criterion needs `Validate`, which phase 13 delivers | A subset relation asserted but never checked, and false as written. `8.7:80-86` gate 5 exercises `Validate` and `Import`, so the verification gates assume a phase the build order never builds. The merge in row 124 makes this class of error unrepresentable |
| **C7 — How many curriculum phases are there?** | `8.7-build-verification.md:70`: "a **three-phase** training run"; `7.2-residual-machinery.md:218`: "the current curriculum phase (Warmup → Refine → Polish)" — three | `11.8-deriv-generator-catalog.md:332`: `curriculum-phase : Warmup \| Refine \| Calibrate \| Polish` — four; `11.8:447` schedules SCPH refresh at "S5's Refine→Calibrate" boundary, a boundary that does not exist in the three-phase reading | A gate in `8.7` asserts a phase count that one page confirms and another contradicts. `11.8` is an appendix under the retired-legend warning, so the four-phase reading may be the stale one — but `11.8:447` and `11.8:571` schedule real work at the extra boundary, so it cannot simply be dropped when 11.8 is mined |

---

## Notes for Phase 2

### The merge recommendation, stated plainly

Seven pages on "the MVP and how to build it" reduce to **five**, and five pages on
"what n-Op is" reduce to **five with one gutted**. What each page uniquely owns:

| page | what it uniquely owns | verdict |
|---|---|---|
| `mvp-system` | the **consequence** column — CBM on Δ not at X and the six-fold degeneracy that transport rows consume; PBE −23% ⇒ hybrid required; Θ_D ⇒ QHA valid to 800 °C ⇒ SCPH deferred; non-polar ⇒ rows 17/21/22 excluded; oxidation is the lifetime limiter | **survives.** Its value column does not (row 99) |
| `capability-slices` | the per-capability vocabulary selection — which methods, templates, formulas, bundles, residuals, obligations each capability draws | **survives; absorbs `mvp-scope`** |
| `mvp-scope` | nothing that is not a sum over `capability-slices`' three tables, except the one-third judgment and the deferral list | **merge into `capability-slices`**; deferrals → `out-of-scope` |
| `forced-decisions` | the polyglot four-role shape; the TB warm-start's "not a residual" qualifier; the L1 output requirement | **survives.** Its battery inventory → `reference-battery`, its tolerances → `accuracy-ledger` |
| `build-order` | the MVP exit criterion (one sentence). The 9 steps are a projection of `build-sequence` filtered by `mvp-scope` | **merge into `build-sequence` as an in-MVP column** |
| `build-sequence` | the 14-phase plan, the decidability gate, the Stage-2.5 attachment, language-neutrality | **survives; absorbs `build-order`** |
| `build-verification` | the static consistency set and the five runtime gates | **survives**, but every `§`-ordinal in §1 must be rewritten and `architecture.md` removed |

The merges are not tidying. `build-order`-as-a-projection is what produced C6: a subset
relation asserted in prose, never checked, and false. Expressed as a column on the source
table, C6 cannot recur. `mvp-scope`-as-a-summary is what produced the orphaned pointer "the
rows above" (row 111) and the stale "D4 surrogate nets" (row 114).

### `library-landscape`: both, and the page must survive

The three-module partition **is** the top-level tree (`journals/oracle` · `operator` ·
`interface`), so the partition itself becomes organization. But four facts on that page
cannot be encoded by a directory layout and are stated nowhere else:

- the oracle's CLI ships **inside** `/physics`; `/interface` is the loops, not the command line (row 57);
- engineering aspects (defects, dopants, surfaces, interfaces, operating-condition effects) live inside `/physics`, not a fourth library (row 58);
- `/physics` does not wrap external DFT codes **at runtime** (row 53);
- `/interface` owns every driving loop and is not yet designed (row 56).

Keep the page, demoted from "here is the partition" to "here are the module boundary
rules." Without it, a reader who sees three sibling directories has no statement of what
may not cross between them — and the CLI question in particular will be re-litigated,
because a directory named `interface/` reads like the natural home for a command line.

### `rationale`: the plan keeps the page; after de-duplication it is two sections

The plan's target lists `program/purpose/rationale`. My finding is that of its nine
sections, **§2 and §6 are the only content not owned elsewhere** — everything else is a
restatement of `product`, `purpose-and-scope`, `crystal-inputs`, `unified-state`,
`pino-bridge`, `canonical-vocabularies`, `representation-substrate`, or the timeline.
And the two survivors belong to different journals: §2 (verifying is cheaper than solving)
is `program/purpose`, §6 (why a neural operator, its caveats, the equivariance handoff)
is `operator/seam`.

So the honest options are: (a) `rationale` survives carrying §2 only, with §6 relocated;
or (b) `rationale` dissolves entirely, §2 → `purpose-and-scope#why-a-grader`, §6 →
`operator/seam`. I lean (b) — a page whose remaining content is one argument is a section,
not a page — but this is a structure decision above my scope, so I have dispositioned the
rows to their content targets and left the page question here. **Either way §2 and §6 must
be relocated before the page is touched.** §2 is the program's central justification and
§6 is the only argued defence of the choice of learner; both currently sit on a page that
is orphaned (`referenced-by: []`), self-labelled a historical snapshot, and therefore the
single most likely thing in the corpus to be deleted wholesale by someone reading its
header.

### Two defect findings that extend the plan's §2 inventory

**1. Vacuous ownership is 23 pages, not 18.** The plan counts pages whose `canonical-for`
topic string equals the id exactly. The checker's uniqueness key is
`" ".join(topic.lower().split())` (`check_book_structure.py:197`) — case- and
whitespace-normalised but **not hyphen-normalised** — so a page can own the spelling of its
own id with spaces and be invisible to both the plan's count and any string test. Five such
pages exist; two are in my scope:

| page | id | owns |
|---|---|---|
| `1.4-architectural-principles` | `architectural-principles` | `architectural principles` |
| `8.6-build-sequence` | `build-sequence` | `build sequence` |
| `6.3-topology-atlas` | `topology-atlas` | `topology atlas` |
| `7.3-cross-cutting-rules` | `cross-cutting-rules` | `cross-cutting rules` |
| `10.2-open-decisions` | `open-decisions` | `open decisions` |

The last three are outside my scope; the surveyors for registry, seams, and governance
should confirm rather than take this from me. **The consequence for Phase 2 is specific:**
plan §8 states the fix as "every page owns ≥1 topic distinct from its id." Implemented as a
string comparison, that rule passes all five of these pages unchanged. The check must
normalise hyphens, whitespace, and case before comparing — otherwise the fix ships with the
defect it was written to close. Probe A separately confirms there is no vacuous-ownership
check today at all: a page owning *exactly* its own id runs green.

**2. A fourth identifier namespace, undefined and collided.** `8.4-forced-decisions` labels
its bullets `H1`, `H4`, `H7`, `H8`. H2, H3, H5, and H6 appear nowhere in the corpus, so the
series is not merely undocumented — it is not a series. The labels are nonetheless cited
across pages: `8.5:27` ("`forced-decisions` H4") and `9.2-reference-battery.md:52`
("`forced-decisions §H4`"). And `H1` collides with an unrelated series: `2.4-multiscale-state`
uses `F-H1` at lines 198, 434, and 436 for a formula from `deriv-high-field` Part H. This is
the same overload class as `GAP` (`[traps] §59`) and belongs on the plan §4 rename list.
Deleting the labels requires fixing both external citations.

### Citation exposure in this scope

`1.2-product` cites 9 pages that are not in its `depends-on`; `1.5-rationale` cites 12.
Both pass the checker because those citations are backticked and `REF_RE` matches only
`[id]` (defect 1). These two pages alone account for **21 unverified dependency edges** —
about 60% of their combined citation load. The remaining ten pages in my scope are clean on
this axis, with two exceptions I checked and dismissed: `8.2` and `8.7` cite `[traps]`
without listing it in `depends-on`, which the checker tolerates because `traps` is in its
`NOT_IDS`-style exemption path rather than because the edge is real.

Under the one-syntax rule this becomes visible work rather than a latent hazard, but note
the ordering: **rewriting citations to `[id#anchor]` on `1.2` and `1.5` will surface 21 new
`depends-on` edges at once**, and several of them (`purpose-and-scope`, `library-landscape`)
create cycles with pages that already cite back. Decide the cycle policy before rewriting
these two, not after.

### Dangling promises found

- **`score-not-solve` → `purpose-and-scope`.** Cited from `1.2:68` and `1.5:50` as though
  `1.1` were the source. `1.1` contains no statement of it — I read the page in full and
  grepped for "score", "solve", "complete candidate", and "fills in". The real owner is
  `1.2:67-68` itself. This is the exact class the brief flags (R1 → `unified-state`): the
  page resolves, the claim is not there. **The oracle/operator boundary — the one thing the
  team lead named as correct and load-bearing — currently cites a page that does not state it.**
- **`architecture.md`** (`8.7:28`). The file does not exist anywhere in the repo. Invisible
  to the checker because it is backticked, per probes B and C.
- **Cross-page ordinals that broke at the split.** `8.3:18` "the rows above" (rows are on
  `8.2`); `8.5:22,23,25` "(§2)", "of §3", "Cap 1/2/3 rows above"; `8.7:23,24,31,33`
  "§2/§3/§4/§6/§7/§10"; `8.6:44` "(§6)"; `1.2:27,85,90,93,111,133,210,248`;
  `1.5:139,177`. None of these resolve within their own page. Each needs an explicit
  `[page#anchor]` target chosen by hand — this is the largest single mechanical task in my
  scope and it cannot be automated, because the ordinals refer to sections of a document
  that no longer exists.

### One cross-scope item I could not disposition

`10.2-open-decisions.md:169` reads "(the *picks* are open item **5** above)" while the item
in question is numbered **6** at line 83; item 5 is the semiconductor-interface applicability
predicate. The same page cites "the §20.4 injectivity and algebraic-law obligations" at line
176 — the book has eleven chapters. Both are in the governance surveyor's scope, not mine,
but both are load-bearing on my rows 116 and 129: the implementation-language fact I am
recommending `forced-decisions` own is currently cross-referenced through a broken ordinal.
Flagging so the two dispositions are reconciled rather than each assuming the other is right.

### Ordering hazards for the builder

1. **Row 105 before row 124.** The Cap-1 acceptance test is labelled the "first end-to-end
   gate" but lives on `capability-slices`, not `build-verification`. If `build-order` is
   merged into `build-sequence` first, the gate set is briefly split across three pages.
2. **Rows 81–84 before anything touches `1.5`.** The operator-side content (why a neural
   operator, the failure modes, the equivariance handoff, `Learnable_Structure`) must land in
   `operator/seam` before `rationale` is edited. `operator/seam` is being built from
   `informed-operator/design/`, which is also being deleted — so both sources of the
   operator seam disappear in the same phase.
3. **Row 99 before row 100.** The consequence column depends on the value column for its
   antecedents. Delete the values only once the consequences carry their own citations into
   `reference-data/*.csv`, or the derivations become unreadable.
4. **C1 touches nine rows across five of my twelve pages.** Whichever way auditor 2 resolves
   completion-vs-evolution, rows 2, 7, 31, 44, 47, 55, 68, 81, 82, 94, and 142 are all edited
   in that pass. Do not rewrite any of those sentences during the mechanical relocation —
   move them verbatim and let the resolution pass rewrite them once.
