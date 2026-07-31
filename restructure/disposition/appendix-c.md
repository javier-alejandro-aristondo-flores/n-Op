# Disposition — appendix C (observable catalog · generator catalog · language study)

Scope: `journal/pages/11-appendix-derivations/11.7-deriv-observable-catalog.md` (7,537 w),
`journal/pages/11-appendix-derivations/11.8-deriv-generator-catalog.md` (6,824 w),
`journal/pages/11-appendix-derivations/11.9-deriv-language-study.md` (2,314 w). 16,675 words total.
Read at: 2af93d2

**Ground truth used for every re-resolution:** `physics/library/formulas/registry-manifest.csv`
(134 rows: 132 substantive + 2 architectural markers at rows **103–104**),
`journal/pages/09-reference-data-and-accuracy/9.1-accuracy-ledger.md`,
`physics/library/cert/reference-data/*.csv`. **No value in this fragment was seeded from an
appendix page.** Every row number and every `Diff` tag quoted below was re-resolved
mechanically against the manifest; the script diffed all 89 appendix rows against it.

---

## The three re-resolutions the brief asked for, done

These govern half the rows below, so they are stated once here rather than repeated.

**R-1 — `11.8` row numbers `#1`–`#87` DO align with the registry; `#88`/`#89` do NOT.**
The scope banner at `11.8:20-21` says row numbers are "snapshot-local, NOT current registry
numbers." That is **false for #1–#87 and dangerously true for #88–#89.** Diffing all 89 rows
by name: rows 1–87 match the registry one-to-one, with exactly five renames, each of which
`11.8` already annotates inline (`#31`, `#32`, `#33`, `#41`, `#74`). Rows **#88 and #89** in
`11.8` are the two architectural rejections (`F-equals-minus-grad-E`, `equivariance`); in the
current registry those live at **rows 103 and 104**, and rows 88/89 are two unrelated
substantive formulas (`long-range-coulomb-directional-limit-correction`,
`charged-supercell-extrapolation-isotropic-general`). The 87-row alignment is what makes this
lethal: a reader who spot-checks a few rows will find them correct and then trust 88/89.

**R-2 — the `Diff` column disagrees with the registry on 18 of the 87 rows, and `11.8`'s own
translation legend mispredicts 9 of them.** The §1.1 legend is not merely retired, it is
*wrong as a decoder*. Measured, appendix → registry:

| §1.1 legend's claim | rows where it holds | rows where it **fails** |
|---|---|---|
| `D0` → canon `D1` | 8 (`#31 #32 #33 #49 #52 #53 #56 #66`) | **`#54` → `D3`** |
| `D1` → canon `D1` unchanged | all others | **`#50` → `D4`** |
| `D2` → canon `D2` | most | **`#5 #13 #36` → `D3`** (all three are fixed points); **`#46` → `D4`** |
| `D3` → canon `D1` or `D2` | 1 (`#12` → `D1`) | **`#45 #67 #85` → `D4`** — legend never predicts `D4` |
| `D4` → canon `D4` | 1 (`#84`) | — |

Also one tier change: `#13 SCPH-self-consistent-phonons` is `T2` in the appendix, **`T3`** in
the registry. Bundle and Path columns agree on all 87 rows.

**Consequence: the `Diff`, `Tier` and `#` columns of `11.8` §1.2 carry no information the
registry lacks, and 19 cells of active misinformation.** The table is `delete`, not `mine`.

**R-3 — `11.7`'s "landed: registry row N" annotations are trustworthy.** All 32 landed-row
claims I checked resolve to the named formula (allowing for behaviour-renaming that
`retired-names.csv` maps: `fowler-nordheim` → `field-emission-current`, `richardson-dushman`
→ `thermionic-emission-current`, `padovani-stratton` → `thermionic-field-emission-current`,
`kane-zener` → `interband-tunneling-rate`). Unlike `11.8`'s `Diff` column, these can be carried.

---

## Disposition rows

### `11.7-deriv-observable-catalog` — 7,537 words

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 1 | Frontmatter: `authority: supporting`, `content-hash: ac38543a00a9`, `canonical-for: [deriv-observable-catalog]` | `11.7:1-18` | delete | — | D1/D6 kill `authority` + `content-hash`; `canonical-for` names only the page's own id — one of the 18 vacuous claims (plan §2 defect 4). Owns nothing. |
| 2 | Conventions banner: Part C's 8 groups are the "pre-canon **data-shape** view"; canonical grouping is the 11 physics-domain bundles | `11.7:21-24` | delete | — | Duplicate. `canonical-vocabularies §4` + `observable-bundles` own the 11 bundles; the data-shape caveat is already stated at `6.7-observable-bundles.md:49` and `6.1-canonical-vocabularies.md:170`. |
| 3 | Part A — 24 materials × "physically distinctive (what makes the surrogate hard)" | `11.7#part-a` | mine | `oracle/certification/applicability-classifiers#material-scope` | Sole statement of *why each material is hard for a surrogate*. Not in `crystal-inputs`, not in `out-of-scope`. This is the material-coverage claim the applicability predicates are written against. |
| 4 | Part A — per-material high-T failure modes (≥500 °C): diamond air-oxidation 600–700 °C as the lifetime limiter vs graphitization >1500 °C; H-desorption 700–900 °C; Al melts 660 °C; Al₂O₃ crystallizes >700 °C; Au needs a barrier >400 °C | `11.7#part-a` (col. 5) | mine | `oracle/certification/out-of-scope#operating-ceilings` | Split from row 3: these are operating-envelope bounds, not scope. The diamond one is already `[traps] §43`; the other ~20 are stated nowhere else. |
| 5 | Part A — per-material role in the diamond-anchored chip (channel / spreader / buffer / ohmic / barrier / substrate) | `11.7#part-a` (col. 4) | mine | `program/purpose/purpose-and-scope#material-scope` | Split from row 3. States what the corpus is *for*, materially. Currently homeless. |
| 6 | **Part B — the 16 figures of merit: definition formula + required-observable list for each** | `11.7#part-b` | **mine** | `oracle/accuracy/accuracy-ledger#figures-of-merit` | **Highest-value block in this page.** `accuracy-ledger:110` asserts "the **16 FoMs** … are algebraic compositions of the above" and names only three; it gives no formula and no observable list. `computational-overview:605` and `audit-prompt:120` cite "(+16 FoM)" as a known formalization gap. **Part B is the only enumeration in the corpus** — and it has 15 rows, not 16 (Contradiction C-1). Grep for `BFOM\|JFOM\|KFOM\|Baliga\|Keyes` outside ch. 11 returns only prose mentions, no definitions. |
| 7 | Part C preamble — the 8 data-shape codes (`BZ EN RS AT TN TR RC SC`) | `11.7:85` | delete | — | Self-labelled "pre-canon"; superseded by the 11 bundles. The *existence* of a data-shape axis is already noted at `observable-bundles:49`. |
| 8 | Part C preamble — the closed method/template/named-formula vocabulary as of first draft (12 methods × 12 templates × 25 formulas) | `11.7:87` | delete | — | Superseded counts. `canonical-vocabularies §3` is canonical and current (12 methods + 3 sub-methods, 20 templates, 132 formulas). Note the page's own body admits "the braced list below has 25 members; '24' was the figure this preamble carried". |
| 9 | **Part C — the 52 catalog observables: per-observable `governing equation`** | `11.7#part-c` groups 1–8 | **mine** | **`oracle/registry/observable-catalog#governing-equations` (NEW PAGE — see Notes)** | Sole home. `physics/research/` holds only the two diamond VASP datasets — **no catalogs** — so the spec brief's claim that "the math today lives in `physics/research/`" is false. The ledger carries tolerance only. 52 equations die with this page. |
| 10 | **Part C — per-observable `faithful residual` expression** (`r_gap = …`, `r_ph = ‖D(q)e − ω²e‖²`, …) | `11.7#part-c` | **mine** | **`oracle/registry/observable-catalog#faithful-residuals`** | Split from row 9 — different target likely. These are the explicit residual forms the generator factory instantiates. `residual-definitions` owns the 19 *categories*; it does not carry 52 expressions. Sole statement. |
| 11 | **Part C — per-observable `cheap-path` (a)/(b) alternatives** (~104 named approximations: TB-3NN-sp³d⁵, Wannier interpolation, Slack, Cahill, Chynoweth, Okuto-Crowell, Anderson, Tersoff midgap, Padovani-Stratton, Griffith, Debye-Grüneisen …) | `11.7#part-c` | **mine** | **`oracle/registry/observable-catalog#cheap-paths`** | Sole statement of the *two-option* cheap path per observable. The ledger's "Cheap vs faithful" column compresses this to one clause and drops option (b) entirely. |
| 12 | Part C — per-observable `native composition` (method ∘ template, e.g. "hybrid-DFT ∘ eigenproblem on KS-Hamiltonian; or GW ∘ Dyson") | `11.7#part-c` | mine | `oracle/registry/typed-compositions#per-observable-compositions` | 52 worked instances of the composition grammar `typed-compositions` defines abstractly. Not duplicated there. |
| 13 | Part C — per-observable `accuracy regime` | `11.7#part-c` | delete | — | **Superseded by `9.1-accuracy-ledger` rows 1–52**, which is canonical and explicitly says it *restored* this column from here (`9.1:36`). Two rows already diverge (see C-2). Do not carry. |
| 14 | Part C — per-observable `high-T notes` | `11.7#part-c` | mine | `oracle/accuracy/accuracy-ledger` (merge into existing rows 1–52) | Partly present in the ledger, partly not. Same observable numbering (#1–52) makes the merge mechanical. Unsure — flagged as merge-not-copy. |
| 15 | Part C — per-observable `couples to` lists | `11.7#part-c` | delete | — | Duplicate of Part D's coupling matrix at finer granularity; Part D is the machine-readable form. Keep one. |
| 16 | Part C — the two `(material, T)`-style **signatures** on each observable | `11.7#part-c` col. 2 | mine | `oracle/registry/observable-catalog#signatures` | The observable's typed arity. The registry's `Signature` column is keyed to the 132 *formulas*, not the 52 observables — different axis (see Notes). |
| 17 | **Part D — the 22 × 21 coupling matrix (row observable needed to compute column observable)** | `11.7#part-d` | **mine** | `oracle/laws/coupling-structure#observable-coupling-matrix` | Sole machine-readable statement of the observable dependency graph. `coupling-structure` owns coupling but carries no such matrix. |
| 18 | Part D — centrality ranking: the 7 most-depended-upon observables (gap, bands, ω_λ(q), E_f, E_F, **T_op as meta-observable**, φ_B) | `11.7#part-d` | mine | `oracle/laws/coupling-structure#centrality` | Present-tense design-priority fact ("these seven get the most careful faithful-residual formulations"). T_op's meta-observable status is load-bearing for the layer ordering (`11.8` §2.2). |
| 19 | Part E — 12 named accuracy-failure modes of standard DFT/BTE, with magnitude + mitigation | `11.7#part-e` | mine | `oracle/accuracy/accuracy-ledger#failure-modes` | Present-tense method limits (KS gap underestimation 30–100%; charged-defect alignment 0.3–1 eV; BTE-RTA hot-tail; MIGS-vs-Schottky-Mott 0.3–1 eV; 3-ph vs 4-ph 10–20%; SOC 10–30 meV). Not duplicated in the ledger, which is per-observable, not per-method. |
| 20 | Part E — the QHA-breakdown row's per-material framing (diamond 0.49 Θ_D holds, GaN 1.29 Θ_D fails, AlN 0.77 Θ_D fails — "no single fraction fits") | `11.7#part-e` | delete | — | Already canonical at `[traps] §40` and `accuracy-ledger` #14, both cited by this row. The row's own "the Θ_D/2 justification this row used to give is the one that register explicitly retired" is scaffolding. |
| 21 | Part F — 12 honest limits of scope (strong correlation, flexoelectricity, magneto-thermal, non-Markovian deep defects, polaron localization, excitonic transport, radiation cascades, plasma damage, GB statistics, creep, tunneling-corrected rates, plasmon-phonon) | `11.7#part-f` | mine | `oracle/certification/out-of-scope#declared-limits` | Present-tense scope declaration. `out-of-scope` carries strong correlation (`5.3:26`); the other 11 need checking against it — several look absent. |
| 22 | "Summary of registry gaps flagged for architecture amendment" — 10 bullets, each with its landing disposition | `11.7#summary-of-registry-gaps` | delete | — | Scaffolding: self-described as "Kept as the **scoping record**". Every bullet has landed (verified: rows 40–41, 105–110, 113–119, 121, 13, 44/46, 70–71, 76–80, 115, 116, 128). |
| 23 | …except the three items still **genuinely outside** the registry: `#18`/`#49` full-band MC and the hot-carrier EDF tail; `#41` device-scale resonant modes; full radiation-cascade dynamics | `11.7:279` | mine | `oracle/certification/out-of-scope#registry-gaps` | Exception 1 of the brief: a closed item's *resolution* is present-tense. These three are **not** closed — they are live gaps. `accuracy-ledger` #49 carries the EDF-tail refusal; `#41` and cascade dynamics need a home. |
| 24 | Closing line: "52 catalog observables across the 8 data-shape groups" | `11.7:283` | delete | — | Count preserved in `glossary.md:76` ("Catalog observables") and `accuracy-ledger:49-53`, both of which survive. |
| 25 | `## Changelog` — 5 dated entries (2026-07-21 ×2, 2026-07-16 ×2, 2026-07-07) incl. superseded κ values ("±10%/±20%", "2000 → ~600 W/mK at 800 K") and the row-20 breakdown sign error | `11.7:287-326` | delete | → log | D1/D2. Two entries are log-worthy advancements (L-3, L-4 below); the superseded values are exactly the trap the brief warns about and must not travel. |

### `11.8-deriv-generator-catalog` — 6,824 words

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 26 | Frontmatter: `authority: supporting`, `content-hash: d633cb54697d`, vacuous `canonical-for: [deriv-generator-catalog]` | `11.8:1-17` | delete | — | As row 1. Owns nothing. |
| 27 | Scope banner — "Historical S1–S5 reconciliation **snapshot** (87 entries)", the retired-legend warning, the `retired-names.csv` pointer | `11.8:20-30` | delete | — | Pure scaffolding, and **partly false** (R-1: rows 1–87 do align). Its live content — that `D3`/`D0` meant the opposite — is already `[traps] §53`, which survives. |
| 28 | §Preface — "Diamond is the anchor substrate. Where streams disagree, this document binds the resolution." | `11.8:34-36` | delete | — | Stream-arbitration framing; the streams (S1–S5) do not survive D3. Diamond-as-anchor is canonical in `mvp-scope`. |
| 29 | §1.1 Bundles B1–B11 with contents | `11.8:44-55` | delete | — | Duplicate. `canonical-vocabularies §4` (`6.1:151-165`) + `observable-bundles` own them. **Note B10 is named `structural-validity` here, `static-validity` in canon** — see C-3. |
| 30 | §1.1 Cost tiers T0–T3 **as scheduling cadence** (per-step / per-batch / per-epoch / on-demand) | `11.8:58-61` | mine | `operator/training#residual-cadence` | Not a duplicate: `named-formulas:59-61` defines T0–T3 by **wall-clock cost** (≤10 µs / ≤10 ms / ≤10 s / ≤10 min). The cadence reading is a distinct, operator-side fact and is stated nowhere else. See C-2. |
| 31 | §1.1 the retired S5 five-tier differentiability legend + its translation table | `11.8:63-74` | delete | — | Retired vocabulary, **and wrong as a decoder** (R-2: mispredicts 9 of the 18 changed rows). `named-formulas` §"Differentiability tags" is canonical; `[traps] §53` carries the hazard. Carrying this forward is strictly worse than dropping it. |
| 32 | §1.1 `Path`: `cheap` = per-step loss, `faithful` = compared against battery | `11.8:76` | delete | — | Superseded and **contradicted**: `formula-registry:94` states `Path` is an **anchor class, not a runtime path selector** ("every formula is on the single residual surface under the always-cheap pipeline"). The appendix's reading is the pre-reframe one. |
| 33 | §1.2 the 89-row catalog table — `#`, `Name`, `Bundle`, `Tier`, `Diff`, `Path`, `Source`, `Depends on` | `11.8:80-170` | delete | — | **Superseded in full by `physics/library/formulas/registry-manifest.csv`**, which carries the identical column schema plus 45 more rows and current tags. Verified mechanically: 87/87 name match, 19 cells of stale `Diff`/`Tier`, and the `#88`/`#89` collision (R-1, R-2). The `Signature` column is the one thing the registry also has. Nothing unique survives. |
| 34 | §1.2 the `Source` column's S1–S5 stream provenance | `11.8:80-170` | delete | — | Stream bookkeeping; D3 dissolves the two-tier/stream system. The registry's own `Source` column carries current provenance (literature DOIs / research pointers). |
| 35 | §1.2 footer — "87 + 2 = 89 rows; ~13% dedup compression from ~100 raw proposals"; the 5 named unifications | `11.8:172` | delete | → log | Superseded count (132 substantive now). The dedup *decision* is log-worthy (L-6); the arithmetic is not. |
| 36 | §2.1 Centrality hubs — the seven hubs and the T_op ASCII fan-out | `11.8:178-194` | delete | — | Duplicate of `11.7` Part D centrality ranking (row 18), which is the better-sourced statement (derived from the full coupling matrix). Keep one. |
| 37 | **§2.2 The layered compute DAG — Layers 0–6, with per-layer membership** | `11.8:196-246` | **mine** | `oracle/seams/residual-machinery#layer-dag` | **The single most load-bearing block in my scope.** `7.2-residual-machinery.md:67-68` declares the canon field `layer : 0..6` and defines it *only* by citing "the 7-layer compute DAG of **residual-generator-catalog §2**" — **an id that does not exist** (the page is `deriv-generator-catalog`). Dangling promise + dead id in one. If ch. 11 dies unmined, a canon field loses its definition entirely. |
| 38 | §2.2 the ordering constraint — **"T_op must be predicted/converged before Layer-3 residuals fire"**; RAD sampling and GradNorm must respect it | `11.8:216-218` | mine | `operator/training#layer-ordering` | Split from row 37: this is a *training-loop* obligation, not a graph fact. `11.8` §7.4 restates it as a hard requirement and §6.3 shows the failure it prevents (loss computes c_def at RT while predicting 500 °C performance). Stated nowhere in canon. |
| 39 | §2.3 Cycle resolution — Layer 3 ↔ Layer 5 (T_op → σ,κ → T_op) closed by fixed-point iteration **in the same forward pass, no nested optimization**; E_F ↔ c_def is a genuine nested fixed point needing an implicit-layer/DEQ node | `11.8:248-252` | mine | `oracle/laws/coupling-structure#self-consistency-cycles` | Present-tense structural fact. The registry confirms the consequence independently: rows 5, 36 and 13 are all `D3` (implicit-function adjoint) — which is *why* the legend mistranslation at R-2 matters. |
| 40 | §3.1 `ResidualGenerator` record definition | `11.8:281-299` | delete | — | **Superseded by `residual-machinery §1`** (`7.2:51-96`), which is richer and current: adds `applicability`, `category`, `axes`, `dressing-tag`, `characteristic-scale`, `registration-hash`; fixes `bundle` to a set; uses the canonical `D0\|DN\|D1\|D2\|D3\|D4`. The appendix's version predates the `applicability` slot (its own banner says so). |
| 41 | §3.1 the three legend-conditioned slots: `backward?` iff `D2`, `relaxation?` iff `D4`, **`fd-step?` iff `D3`** | `11.8:293-295` | delete | — | **Actively wrong under canon and must not be carried.** Canon `D3` = converged fixed point needing an implicit-function adjoint (`named-formulas`); an `fd-step` slot on a `D3` row is the exact error `[traps] §53` names. `residual-machinery` correctly has no such slot. |
| 42 | §3.1 `InputContract` / `OutputContract` records — `state-slots`, **`env-slots : subset of Environment record`**, `cache-handles`, `coverage-mask`; shape/units/expected-range/symmetry | `11.8:267-279` | mine | `oracle/registry/named-formulas#contracts` | `residual-machinery` has `input-contract : {TypedSlot}` / `output-contract : TypedSlot` with no expansion. This is the only place the contracts are unpacked — and the only place in the corpus that gestures at `Environment`'s contents. See `environment-schema`. |
| 43 | §3.2 `make-residual-generator` factory signature | `11.8:304-311` | delete | — | Superseded by `residual-machinery §3` (`7.2:117-126`), whose signature is current (`observable, formula, axes, sampling-policy, applicability`). |
| 44 | §3.2 factory *behaviour* — the 8-step instantiation procedure, incl. **"error at registration, not at training time"** for a missing `D2` adjoint | `11.8:313-322` | mine | `oracle/seams/residual-machinery#factory-behaviour` | The 8 steps are stated nowhere in canon; `residual-machinery §3` gives only the entry point. Step 4's registration-time-gate rule is restated as a decision at §4.5 and is live (`adjoint-cert` field exists). Steps keyed to the retired legend (`D3`→fd-step) must be dropped on the way — see row 41. |
| 45 | §3.3 `PinoTrainStep` record + the `step()` procedure (layer-grouped ordering, coverage-mask skip, σ-scaling, `maybe-update-state` for self-consistent nodes) | `11.8:326-354` | mine | `operator/training#train-step` | Operator-side; `/physics` canon deliberately stops at `weight-policy : ConsumedBy(/informed-operator)` (`7.2:89-90`). This is the only written form of the consuming loop. |
| 46 | §3.3 `curriculum-phase : Warmup \| Refine \| Calibrate \| Polish` | `11.8:332` | mine | `operator/training#curriculum` | The four-phase curriculum vocabulary. Referenced by §5 dispositions (Gumbel-Softmax τ annealed "to 0.1 by Polish") and §6.4. Homeless in canon. |
| 47 | §3.4 tier → sampling-policy map (T0→UniformBatch, T1→RAD-Adaptive, T2→PerEpoch, T3→OnDemand) and when each is evaluated | `11.8:358-363` | mine | `operator/training#sampling-policy` | `residual-machinery` declares the *enum* (`UniformBatch \| RAD(τ) \| Importance \| ValidationOnly`) but not which tier gets which. §7.12 restates it as a rule. Note the enums differ — see Notes. |
| 48 | §3.4 diff-tag → backward-path table | `11.8:365-371` | delete | — | Retired legend (the table's own header says so). `named-formulas` owns the current per-tag adjoint story. |
| 49 | §3.5 Multi-source loss — 4 source families (Model-internal/cheap, DFT-Battery, MLIP, Experiment), GradNorm outer rebalance every K steps, NTK-init inner weights frozen after warmup, Huber for experimental with per-observable σ | `11.8:373-383` | mine | `operator/loss#multi-source-balancing` | The loss-design fact. `accuracy-ledger:291` and `residual-definitions §7` own `characteristic-scale : σ` as an error-model input and explicitly say it is "**never a fitted weight**" — so the weighting scheme itself has no `/physics` owner and belongs operator-side. |
| 50 | §3.6 the three `/physics` exports realized via the factory — `Generate`, `Validate`, `Import` | `11.8:385-390` | mine | `oracle/seams/pino-bridge#exports` | `pino-bridge §2` owns `Import` (ground-truth-bridge). `Generate`/`Validate` as named exports need confirming against `pino-bridge`; the *triple* is stated only here. Unsure — flagged. |
| 51 | §4.1 Cost-tier reconciliation: keep T0–T3, reject S2's T0–T4; MLIP-ness belongs in the `source` tag, not the cost tier | `11.8:395-399` | delete | → log | Decision landed — canon is T0–T3 everywhere (`named-formulas:48`). Resolution is present-tense and already canonical; the S2-vs-rest story is scaffolding. Log as L-6. |
| 52 | §4.2 `coupled-em-thermal-pde-residual` is a sub-residual under `eom-violation`, not a new top-level category; PDE-ness is captured by `T1` + `D2` | `11.8:401-405` | mine | `oracle/laws/residual-definitions#category-assignment` | Present-tense taxonomy rule with a live rationale ("PDE-vs-algebraic crosscuts every bundle and breaks the bundle-as-cohesive-domain abstraction"). `residual-definitions` owns the 19 categories; this assignment rule is not stated there. |
| 53 | §4.3 `ReferenceCache` unification — one type, one lifecycle, one invalidation policy, two namespaced sub-caches (`ref-cache.phases`, `ref-cache.defects`) | `11.8:407-413` | mine | `oracle/accuracy/reference-battery#reference-cache` | Present-tense design decision. Registry rows 66 and 87 both exist and both reference it. No canon page defines the cache type. |
| 54 | §4.4 Bundle count = 11, with the S1–S4 dedup map (band-alignment→B6, defect-population-spectrum→B4, field-resolved+hot-carrier→B9, new B11) | `11.8:415-429` | delete | → log | Resolution is canonical (`canonical-vocabularies §4`). The dedup *map* is stream history. The rationale sentence — "bundles are physical-domain cohesion units for the unified state vector, not residual-category bins" — is worth checking against `observable-bundles`; if absent there, promote it (see Notes). |
| 55 | §4.5 The `AdjointFn` slot **must** be filled at registration for `D2`; the factory errors at registration, not training | `11.8:431-433` | mine | `oracle/seams/residual-machinery#registration-gate` | Live guard. `residual-machinery` has `adjoint-cert : Passed\|Failed(witness)\|NotApplicable\|Relaxed(rationale)` but does not state the fail-at-registration rule. Overlaps row 44 step 4 — merge on landing. |
| 56 | §5 Honest-gaps table — 10 hard residuals with a recommended disposition each (surrogate-net for #40/#41; faithful-only on-demand for #80 with #77/#79 as cheap proxies; periodic-refresh for #13; Gumbel-Softmax for #84; log-sum-exp soft-min for #67; SOAP-descriptor surrogate for #85) | `11.8:437-452` | mine | `oracle/certification/out-of-scope#hard-residual-dispositions` | Present-tense engineering dispositions with rationale. **Re-key required**: the "Current tag" column is in the retired legend (e.g. `#45` "T1/D3" is now `D4`; `#67` "T1/D3" is now `D4`; `#85` "T1/D3" is now `D4`). Carry the disposition prose, drop the tag column. |
| 57 | §5 the 4-phonon row's "(superseded)" entry recording that rows 121–122 landed | `11.8:445` | delete | → log | Closed-item story. The resolution (`kappa-4phonon-high-t-correction` row 121, `iterative-lbte-kappa` row 122, valid `T ≳ 0.4·Θ_D`) is already canonical in `accuracy-ledger` #12/#13 and the registry. |
| 58 | §5 Strategic gap — surrogate-net-bridge must be a **first-class architecture component**, complementing (not replacing) the MLIP bridge; required for #6/#13/#40/#41 | `11.8:454` | mine | `program/build/mvp-system#surrogate-bridge` | Live architectural requirement. Note the row's own parenthetical retracts the "~5% of the catalog" figure as computed off the wrong set — carry the requirement, not the number. |
| 59 | §6 Worked example — Diamond–W Schottky contact at 500 °C: scenario setup, 37-step firing sequence across Layers 0–6, cost accounting (24×T0, 9×T1, 2×T2, 0×T3) | `11.8:458-538` | mine | `program/build/build-verification#integration-test` | §7.13 proposes exactly this as "the canonical integration test for S7's amendment". `build-verification:45` already checks "all 132 formulas instantiate as `ResidualGenerator`" — this is the end-to-end complement. **Carry with the §6.2 corrections applied** (they are in-place already per the 2026-07-07 gap audit). |
| 60 | §6.2 step 9 — the MIGS-corrected barrier "**does not reproduce**": Cowley-Sze gives ~3.5–3.7 eV for every termination-tagged χ, not the ~4.5 eV stated. "Flagged unpinned; do not quote the 4.5 until the inputs are pinned" | `11.8:493` | mine | `oracle/registry/formula-registry` (row 48 `Source`) — **already there** | Not a new fact: `registry-manifest.csv` row 48's `Source` cell carries the identical UNPINNED flag naming `deriv-generator-catalog §6`. **The CSV cell will dangle at cutover** — see Notes, ordering hazard 3. Open question `migs-worked-example-inputs`. |
| 61 | §6.3 "Key physics demonstration": at 773 K the B-acceptor activation rises ~10³× vs RT; the catalog catches it because #35 fires *at* the T_op predicted by #70+#71 | `11.8:538` | mine | `program/build/build-verification#integration-test` | The assertion the integration test exists to make. Merge with row 59. |
| 62 | §6.4 Four failure modes the catalog catches (MIGS disagreement >0.3 eV; E_F non-convergence → drop sample; avalanche M>10 → out-of-envelope mask; carbide growth >100 nm → mission fail; T_op mismatch → Warmup-only) | `11.8:540-546` | mine | `oracle/certification/cert-obligations-detail#runtime-refusals` | Present-tense refusal/masking rules. `applicability-classifiers` owns coverage masks; these five concrete trips are stated only here. |
| 63 | §7 items 1–13 — summary recommendations to "S7" | `11.8:552-578` | delete | — | Restatements of §1–§6 addressed to a stream that no longer exists, plus superseded item 1 ("adopt the 87-entry catalog as the canonical registry" — it is 132). Every live element is carried by rows 37–62 above. |
| 64 | **§7 item 14 — "The `Environment` record needs a `temperature_gradient` field" — adopt directly** | `11.8:580` | mine | `oracle/state/unified-state#environment` | **Never adopted.** `grep -rn "temperature_gradient"` outside ch. 11 returns nothing. And `Environment` itself is the brief's confirmed homeless fact — used in signatures at 12+ canon sites (`named-formulas:54`, `residual-machinery:83`, `residual-definitions:235`, `applicability-classifiers:31`, `property-templates:51,79`, `product:102`, `computational-overview:52,334,473`, `cert-obligations:63`) and **defined by no page**. Open question `environment-schema`. |
| 65 | §7 item 15 — the response-interface needs a `causal? : Boolean` slot for non-causal nonlinear responses | `11.8:582` | mine | `oracle/registry/property-templates#response-interface` | Also never adopted; `grep` finds only `Algebraic/Kramers-Kronig` (`residual-definitions:134`) and causality witnesses (`typeclass-alphabet:39`), not the slot. Open question `response-causality-slot`. |
| 66 | §7 item 16 — v1's documented frontier = S1's 12 limits + §5's 4 architecture-level gaps | `11.8:584` | delete | — | Duplicate: the 12 limits are `11.7` Part F (row 21); the 4 gaps are §5 (row 56). Both dispositioned. |
| 67 | Closing flourish — "The catalog is now executable. The factory is now typed…" | `11.8:586` | delete | — | Rhetoric addressed to a retired stream. |
| 68 | `## Changelog` — 2026-07-16 strata rewrite, 2026-07-07 gap audit | `11.8:590-601` | delete | → log | D1/D2. The 2026-07-07 entry is log-worthy (L-3). |

### `11.9-deriv-language-study` — 2,314 words

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 69 | Frontmatter + title "(`open-decisions`, **open item 5**)" | `11.9:1-19` | delete | — | As row 1 — **and the ordinal is wrong**: the language item is **6**; item 5 is the semiconductor-interface applicability predicate (`10.2:73`). See C-5. D6 kills bare `§`-ordinal citations anyway. |
| 70 | Status banner — "partially superseded"; what closed in 2026-06 was the *shape*; the picks did not close | `11.9:21-28` | delete | → log | Scaffolding. The live content is fully carried by `open-decisions` item 6 (`10.2:83-91`) and the Closed-decisions entry (`10.2:169-212`), both of which survive. Log as L-2. |
| 71 | Study provenance — 4 web-verified Round-1 axes, 1 adversarial audit, Round-2 pass; "survey current to 2024–2026" | `11.9:30-34` | delete | → log | Method provenance, not a fact. Belongs in the log entry (L-1) as attribution — this is a compliance-relevant "who/what produced it". |
| 72 | **The five durable requirements: (1) build in-house, minimize large-framework dependence — a framework that *owns* differentiation is a liability; (2) AD + implicit-diff already in hand, so built-in AD is no advantage — driving Stage-4 adjoint synthesis from our own IR is the requirement; (3) polyglot acceptable iff boundaries are clean; (4) well-known but domain-specific languages; (5) not Rust, and team familiarity is not a factor** | `11.9:36-53` | **mine** | `program/purpose/architectural-principles#implementation-requirements` | **The durable part, per `open-decisions` item 6 itself**: "the requirement each candidate was chosen to satisfy is the durable part." Stated in full nowhere else — `open-decisions` paraphrases requirements per-candidate but never lists the five constraints. Language-neutral. Reads as requirements, not as a mandate. |
| 73 | The structural insight: `/physics` is *a compiler over a content-addressed typed substrate that emits a fast runtime kernel* — two genuinely different workloads — and the Stage-4→Stage-5 boundary is a narrow, natural language seam | `11.9:55-59` | mine | `oracle/compilation/compose-time-pipeline#codegen-seam` | The argument the whole polyglot shape rests on. `open-decisions` states the *conclusion* (four roles) but not this derivation. `computational-overview:59,582` and `forced-decisions:23-28` state the seam; none states why it is a *language* seam. |
| 74 | The four-role polyglot table (Stages 1–4 compiler / Stage 2–2.5 group theory / Stage 5 runtime / proofs) with **"only two *live* languages; GAP and Lean are offline leaves on no hot path, so they add zero interop risk"** | `11.9:61-72` | delete | — | Duplicate. `open-decisions` Closed-decisions (`10.2:169-179`) carries all four roles in language-neutral form, and `forced-decisions:23-28` restates them. The offline-leaf argument is the one element not obviously duplicated — promote that clause only if absent (see Notes). |
| 75 | §Compiler-host = Haskell (ratified) — GADTs/`DataKinds` for the operad, `hegg` for Stage 3, `GHC.Generics` for the §20.4 serializer, a-la-carte typeclasses, ROBDD | `11.9:74-93` | delete | — | **Candidate advocacy, and the header word "ratified" is now false.** `open-decisions` item 6 requires every mention of a language to read as a candidate, "never a mandate". The per-candidate requirement summaries already live at `10.2:184-205`. Javier has reopened the picks. |
| 76 | §Compiler-host — the OCaml runner-up analysis and the fallback-host designation | `11.9:95-101` | delete | — | Same. `10.2:189` already records "(OCaml is the documented fallback host.)" |
| 77 | §Runtime = Julia — emitted source, JIT once per composition, zero FFI/ABI crossing per sample; rejected C-ABI/FFI and shared LLVM/MLIR | `11.9:103-113` | delete | — | Same — and duplicated at `10.2:190-194`, which correctly abstracts it to "a host with fast JIT of generated numeric source and a workable GPU story — not Julia specifically." |
| 78 | **What crosses the seam is narrow: the generated kernel (once) + a flat `Float64` state array in / residual + gradient + observable + cert arrays out. No substrate object ever serializes across** | `11.9:115-118` | **mine** | `oracle/compilation/compose-time-pipeline#codegen-seam` | Language-neutral and load-bearing — it is *the safety argument for the split*, and it pins the seam's data contract. `computational-overview:582` says the compiler "emits runtime-host source"; it does not state what crosses. |
| 79 | **§The condition that makes polyglot a net win — build a Stage-4→Stage-5 differential golden test up front (emitted kernel vs tree-walking interpreter of the same IR, random states, agreement to tolerance); emit a typed `Expr`, not raw strings; compile in a setup phase, run the hot loop in a later world age. Without it, collapse to a single host.** | `11.9:120-129` | **mine** | `oracle/certification/cert-obligations#tau-interp` | **Load-bearing for a live canon tolerance.** `cert-obligations:152` defines `τ_interp` = "Stage-4→Stage-5 differential golden test: two evaluators of the same IR must agree (`[deriv-language-study]`)" at `1e-10` relative — and cites *this page* as its source. The obligation exists in canon; its rationale and construction do not. |
| 80 | **§Per-stage hardware split — CPU-dominant compiler; GPU is a Stage-5-only optional accelerator chosen *per-composition* by Stage-4 codegen, not a global setting** (6-row table, Stages 1–5) | `11.9:131-143` | **mine** | `oracle/compilation/computational-overview#hardware-split` | Language-neutral. `10.2:206-208` compresses this to two sentences inside a *language* decision, which is the wrong owner — the split is a property of the pipeline. The per-stage table is unique. |
| 81 | §Why GPU is not central — Stage 2 yields small irrep blocks (`O_h` `d_λ ∈ {1,2,3}`; double cover under SOC adds spinor irreps to `d_λ = 4`) plus ragged sparsity = the classic GPU anti-pattern; GPU wins only at large k-mesh / `(Real/Wannier, Sparse)` defect supercells **and** when the PINO keeps batches device-resident | `11.9:145-156` | mine | `oracle/compilation/computational-overview#hardware-split` | The quantitative justification. `computational-overview:342` independently notes small blocks are "a poor fit for wide-SIMD/GPU batching unless many blocks are batched" — consistent, but far thinner. Ties to the `O(log n)` / no-solver-on-the-hot-path commitment (`representation-substrate §5`). |
| 82 | Round-1 scored matrix (6 candidates × 5 axes) and Round-2 compiler-host bake-off (3 hosts × 4 axes) | `11.9:158-180` | delete | — | Candidate advocacy with numeric scores — the most mandate-like content on the page. Javier has reopened the picks; `live/specs/2026-07-21-...brief.md` R0.1 explicitly requires re-deriving a comparison matrix and "**re-examine, rather than inherit, any prior exclusion**". Carrying scores would prejudge it. |
| 83 | §Excluded — **Python + JAX disqualified: JAX's tracing/`jit` model *owns* differentiation (`custom_vjp` can't pair forward-mode, can't take array `nondiff_argnums`, won't serialize a staged program), so with AD in hand its one advantage is moot and obstructive** | `11.9:186-190` | mine | `program/purpose/architectural-principles#implementation-requirements` | Keep as a **worked application of requirement (1)/(2)**, not as a verdict. `10.2:211-212` already carries the one-line version. This is the sharpest evidence for the AD-ownership requirement and the brief's R0.1 names it as a constraint to test against. Merge into row 72. |
| 84 | §Excluded — Rust (single-language winner, excluded by preference); Julia-as-compiler-host (2.5/5, ModelingToolkit.jl anti-pattern); custom MLIR (≈34–50+ pm, eventual optional Stage-4 GPU backend); single-host collapse fallback | `11.9:182-200` | delete | — | Candidate advocacy. The two durable clauses are already canonical: Rust-excluded-by-preference and the Julia-only/Haskell-only fallback at `10.2:209-211`. The MLIR-as-later-optional-GPU-backend note is thin and language-specific. |
| 85 | **§Honest liabilities — the codegen seam is the riskiest point: it is exactly where the compiler host's type system stops, so a bad template = silently wrong physics (adjoint signs, index conventions)** | `11.9:202-206` | **mine** | `practice/traps` (new entry) | **A live hazard, not a remnant** — brief exception 2. Language-neutral: it holds for any emit-source split. `[traps]` has no entry for it. Its mitigation is row 79's golden test, giving the trap a named enforcement. |
| 86 | §Liabilities — two-language build tax; Haskell iteration velocity at the `DataKinds` frontier; **the operad's compile-time soundness does not survive a host swap (drops to smart-constructor checks)** | `11.9:208-217` | delete | — | Candidate-specific. The third clause is a real structural observation but is stated only about Haskell→OCaml/Julia and would read as advocacy for a reopened pick. Unsure — flagged in Notes. |
| 87 | §Build-cost — live system ≈26–34 person-months; most likely blow-up is Stage-3 sparsity inference + the `SymbolicTensorOps` operad typechecker, not the commodity wiring | `11.9:219-225` | mine | `program/build/build-order#cost-risk` | The *risk localisation* is durable and language-neutral: the open-ended pieces are Stage-3 sparsity inference and the operad typechecker. The person-month figure is conditioned on the retired picks — carry the risk, drop the number. |
| 88 | §Sources — "Per-axis dossiers under `/tmp/impl-lang-research/` (`a1`–`a4`, `b1`–`b2`)" plus ~20 external references | `11.9:227-237` | delete | — | **The internal dossiers are gone** — `/tmp` paths from a 2026-06 session; unrecoverable and uncitable. The external list is candidate-specific and superseded by R0.1's mandate to re-verify. Note the dead-provenance fact in the log entry (L-1). |
| 89 | `## Changelog` — 2026-07-16, 2026-07-21 (partial reopen), 2026-06 (decision closed, "commit ec52314-era") | `11.9:241-251` | delete | → log | D1/D2. Both the 2026-06 closure and the 2026-07-21 partial reopen are log-worthy (L-1, L-2). |

---

## Open questions

| id | question | owning page | why it is open |
|---|---|---|---|
| `migs-worked-example-inputs` | `MIGS-corrected-barrier` (registry row 48): the §6 worked example's inputs (`S≈0.85`, `φ_CNL≈4.0`) evaluate to ~3.5–3.7 eV under every termination-tagged χ, not the ~4.5 eV the example states. What pins them? | `oracle/registry/formula-registry` (row 48) | Flagged UNPINNED in **both** `11.8:493` and the `registry-manifest.csv` row-48 `Source` cell. The value must not be quoted until pinned. The CSV's pointer to `deriv-generator-catalog §6` dies at cutover. |
| `environment-schema` | What are the fields of the `Environment` record? | `oracle/state/unified-state` | The brief's confirmed homeless fact, and my scope holds both the only gesture at its contents (`11.8:269` `env-slots : subset of Environment record`) and an unadopted amendment (`11.8:580`, add `temperature_gradient`). Used in 12+ canon signatures, defined in none. |
| `response-causality-slot` | Does the response interface need a `causal? : Boolean` slot for non-causal nonlinear responses? | `oracle/registry/property-templates` | Proposed at `11.8:582` as "adopt directly"; never adopted. No trace outside ch. 11. |
| `observable-catalog-owner` | Which page owns the 52 catalog observables and their math? | *(none — target-tree gap)* | The target structure in the plan has no such page. The ledger owns their tolerances (a different fact), the registry owns 132 formulas (a different axis). See Notes. |
| `fom-count-16-or-15` | Are the 16 FoMs 16, or 15? | `oracle/accuracy/accuracy-ledger` | The count is asserted in three canon pages; the only enumeration (`11.7` Part B) has 15 rows. See C-1. |
| `out-of-scope-limits-coverage` | Do `11.7` Part F's 12 out-of-scope limits all appear in `out-of-scope`? | `oracle/certification/out-of-scope` | Only strong correlation confirmed present (`5.3:26`). The other 11 were not individually swept — **not checked**. |
| `sampling-policy-enum-owner` | `residual-machinery`'s `sampling-policy` enum is `UniformBatch \| RAD(τ) \| Importance \| ValidationOnly`; `11.8` §3.1 has `UniformBatch \| RADAdaptive \| PerEpoch \| OnDemand`. Which is current, and where did `PerEpoch`/`OnDemand` go? | `oracle/seams/residual-machinery` | The tier→policy map (row 47) is stated in the appendix's enum. Translating it needs this answered. |

---

## Log-worthy advancements

| date | finding or decision | evidence | attribution | superseded |
|---|---|---|---|---|
| L-1 · 2026-06 | **Implementation-language decision closed on the *shape*: a four-role polyglot of domain-specific DSLs joined at the Stage-4→Stage-5 codegen seam** (compiler host owning Stages 1–4 + substrate, emitting source for a separate runtime host; offline group-theory engine; offline proof assistant). Leading candidates recorded as Haskell / Julia / GAP / Lean 4. | `11.9#recommendation`; `10.2-open-decisions` Closed decisions; commit "ec52314-era" per `11.9:248` | `deriv-language-study`: 4 web-verified Round-1 axes (compute/hardware, substrate type-system fit, compiler/staging fit, in-house dependency + build cost), 1 adversarial audit, 1 Round-2 pass. **Per-axis dossiers were under `/tmp/impl-lang-research/` and no longer exist** — the study's internal provenance is unrecoverable. | The prior framing "which numerical ecosystem" (Julia vs Python+JAX vs custom-MLIR) |
| L-2 · 2026-07-21 | **The language *picks* were reopened; only the four-role shape stayed closed.** Every mention of a language in the corpus is a candidate to compare against, never a mandate; the requirement each candidate was chosen to satisfy is the durable part. | `11.9:244-247`; `10.2-open-decisions` item 6 (`10.2:83-91`) | Javier | the 2026-06 pick set as a commitment |
| L-3 · 2026-07-07 | **Gap audit: the Diamond–W worked example carried five compounding physics errors in one artifact** — Fröhlich/POP-limited `v_sat` fired on non-polar diamond in violation of its own `is-polar-material` classifier; the ~4.5 eV *n*-type barrier fed into leakage for a *p*-type contact (~3.5 eV wrong); image-force lowering 0.06 eV (a √10 field error; correct 0.16 eV at 10⁶ V/cm); κ_L(773 K) ≈ 800 against a battery value of 620; χ untagged by termination. | `11.8:596-601`; corrections in place at `11.8#6.2`; generalized as `[traps] §44` | 2026-07-07 gap audit | the pre-audit §6 example |
| L-4 · 2026-07-21 | **A live physics sign error was found in a file named as a source for downstream formula research**: `breakdown_field E_b` was recorded as dropping ~20% from 300 K to 800 K; **E_b RISES with T** (`κ_BR>0`, +5×10⁻⁴/K diamond, +7×10⁻⁴/K 4H-SiC). UWBG breakdown *hardens* with T. | `11.7:295-301`; `accuracy-ledger` #20; registry row 123 `breakdown-field-temperature-slope`; Hiraiwa–Kawarada JAP 114 034506 (2013) | 2026-07-21 corpus reconciliation | the conflation of breakdown with the mobility/velocity collapse |
| L-5 · 2026-07-21 | **κ(T) accuracy regime re-anchored**: the observable catalog read "±10% diamond, ±20% III-N" with a 2000 W/mK 300 K anchor while `accuracy-ledger` cited *that file* as its source — so the disagreement pointed the wrong way. Ledger per-temperature bands are canonical. | `11.7:289-294`; `accuracy-ledger` #13 | 2026-07-21 P1 repair | ±10%/±20% and "drops from 2000 to ~600 W/mK at 800 K" |
| L-6 · 2026-06 | **Cross-stream reconciliation of the residual catalog**: cost tiers fixed at T0–T3 (S2's T0–T4 rejected — MLIP-ness belongs in the `source` tag, not the cost tier); observable bundles fixed at 11 (B1–B11), with B11 `degradation` newly introduced for time-integrated lifetime residuals; `ReferenceCache` unified from two proposals into one type with two namespaces; ~13% dedup compression from ~100 raw proposals to 87 entries. | `11.8` §4.1, §4.3, §4.4; landed in `canonical-vocabularies §4`, `named-formulas:48` | S6 reconciliation pass | S2's T0–T4; the S2/S3 bundle proliferation; separate ref-phase-cache and defect-reference-battery |
| L-7 · **2026-07-30** | **The appendix generator catalog's `Diff` column disagrees with the current registry on 18 of its 87 carried-over rows, and the appendix's own §1.1 translation legend mispredicts 9 of them** — including all three fixed-point rows (`fermi-level-charge-neutral`, `SCPH-self-consistent-phonons`, `self-consistent-charge-balance`), which the legend maps to `D2` but which are canonically `D3`. **Separately, appendix rows `#88`/`#89` (the two architectural rejections) are registry rows 103–104; registry rows 88/89 are unrelated substantive formulas.** Rows `#1`–`#87` *do* align, which is what makes the two exceptions dangerous. | This survey; mechanical diff of all 89 rows against `physics/library/formulas/registry-manifest.csv` @ 2af93d2. Detail in R-1/R-2 above. | Phase-1 structure survey (appendix C) | the scope banner's blanket claim that all row numbers are snapshot-local |
| L-8 · **2026-07-30** | **A canon field's definition is reachable only through a dead id.** `residual-machinery` declares `layer : 0..6` and defines it solely by citing "the 7-layer compute DAG of `residual-generator-catalog §2`" — **no page has that id** (it is `deriv-generator-catalog`). The reference is unbracketed, so `REF_RE` never sees it; verified by planting `totally-nonexistent-page-xyz` in that exact position and getting a clean `--check`. | `7.2-residual-machinery.md:67-68`; probe described under Notes | Phase-1 structure survey (appendix C) | — |

---

## Contradictions — COLLECTED, NOT RESOLVED

| claim | source A | source B | nature of the conflict |
|---|---|---|---|
| C-1 · How many figures of merit are there? | "the **16 FoMs**" — `9.1-accuracy-ledger.md:110`; "the 52-observable (**+16 FoM**) catalog" — `4.4-computational-overview.md:605`; "the 52 (**+16 FoM**) observable catalog" — `10.3-audit-prompt.md:120` | `11.7#part-b` enumerates **15** rows | The count is asserted in three canon pages; the only enumeration anywhere has 15 entries. *(Possible reconciliation, not adjudicated: row 5 is "HMFOM / HCAFOM", which may name two distinct published FoMs in one row.)* |
| C-2 · What do the cost tiers T0–T3 mean? | **Wall-clock cost**: "T0 closed-form (≤10 µs) · T1 small linear algebra / 1D quadrature (≤10 ms) · T2 Brillouin-zone / mesh integral (≤10 s) · T3 self-consistent loop or PDE solve (≤10 min)" — `6.6-named-formulas.md:59-61` | **Scheduling cadence**: "T0 = per-step … T1 = per-batch … T2 = per-epoch (MLIP-bridge or surrogate-mediated) … T3 = on-demand (faithful DFT/MD/NEGF call, rare)" — `11.8:58-61` | Two different definitions of the same four tokens. They mostly co-vary, but they are not the same claim, and `SCPH-self-consistent-phonons` is where they part: `T2` (per-epoch surrogate refresh) in the appendix, **`T3`** (self-consistent loop) in the registry. |
| C-3 · What is bundle B10 called? | `static-validity` — `6.1-canonical-vocabularies.md:164`; `observable-bundles` ("B10 static-validity") | `structural-validity` — `11.8:54` | Bundle name divergence. Canon is self-consistent; the appendix is the outlier. Low stakes, but the appendix's bundle list is otherwise presented as authoritative. |
| C-4 · Is `Path` a runtime selector or an anchor class? | "**Anchor class**, `cheap` or `faithful` — what the row's value is trusted against, ***not* a runtime path selector** (every formula is on the single residual surface under the always-cheap pipeline)" — `6.9-formula-registry.md:94` | "`cheap` = goes into per-step loss; `faithful` = compared against DFT/experiment battery" — `11.8:76`; and §3.3's `step()` branches on it | The appendix reads `Path` as a live dispatch axis and builds a training loop on that reading. Canon says it is a provenance/anchor label. This affects how §3.3 (row 45) may be carried. |
| C-5 · Which `open-decisions` item is the language decision? | Item **6** — `10.2-open-decisions.md:83`. Item 5 is "A semiconductor-interface applicability predicate" (`10.2:73`) | "open item **5**" — `11.9` title/`id` line (`11.9:3`, `11.9:19`) **and** `10.2-open-decisions.md:169` ("the *picks* are open item 5 above") | A stale ordinal in two places, one of them **inside the owning canon page itself**. It resolves to a real item that is a different decision entirely — a dangling promise that no checker can see. |
| C-6 · Do the appendix row numbers match the registry? | "Row numbers `#N` are snapshot-local, **NOT** current registry numbers" — `11.8:20-21` | Mechanical diff: rows **1–87 match one-to-one by name**; only `#88`/`#89` diverge (→ registry 103/104) | The warning is over-broad in a way that is itself hazardous: a reader who verifies it and finds it false may then trust the whole table, including 88/89 — where the collision is real and silent. |

---

## Notes for Phase 2

**1. The biggest single issue in my scope is a gap in the target tree, not in the corpus.**
The target structure has **no page that owns the 52 catalog observables**. The ledger owns
their *tolerances* on the same `#1–52` keys; the registry owns 132 *formulas* on a different
axis (observable ↔ registry row is **not** 1:1 — one observable can be served by several
formulas, and 45 registry rows serve no Part-C observable at all). Yet Part C is the sole home
of 52 governing equations, 52 faithful-residual expressions, ~104 named cheap-path
alternatives, and 52 typed signatures — roughly **3,000 words of irreplaceable mathematics**,
and the single largest concentration of unique content in my three pages.

I have targeted rows 9, 10, 11, 16 at a proposed new page **`oracle/registry/observable-catalog`**.
This is an addition to the structure Javier must approve at the Phase-1 gate; I did not have
authority to invent it silently, and folding it into `accuracy-ledger` would put governing
equations on a page whose stated job is tolerances. **Flagging rather than deciding.**
The alternative worth putting to him: extend `data/registry-manifest.csv` with
`equation` / `residual` / `cheap-path` columns and let the 52 observables live as a keyed view
over it — which is what `live/specs/2026-07-21-oracle-code-spec-research-brief.md` R1.0 already
proposes ("a per-row skeleton — equation / method / residual / tolerance / provenance slots").
Note R1.0 states this math "lives in `physics/research/` catalogs"; **that is false** —
`physics/research/` contains only the two diamond VASP datasets. It lives here and nowhere else.

**2. Ordering hazards — three, all of which lose data if run in the wrong order.**

- **`retired-names.csv` must outlive the mining of `11.8` §1.2 and `11.7` Part C.** The plan
  (§9) deletes it. But `11.7`'s vocabulary list and `11.8`'s table are keyed to *literature*
  names (`fowler-nordheim`, `richardson-dushman`, `padovani-stratton`, `kane-zener`,
  `makov-payne-correction`, `freysoldt-correction`, `lany-zunger-correction`,
  `Schottky-Mott-alignment`), and only that CSV maps them to the behaviour-named registry rows.
  Delete it first and the mined prose becomes unresolvable. Worse: `makov-payne-correction`
  maps **ambiguously** — "`-isotropic-cubic` (row 31) **or** `-isotropic-general` (row 89) — the
  old name was ambiguous across both" — so that one needs a human decision, not a lookup.
- **`registry-manifest.csv` row 48's `Source` cell cites `deriv-generator-catalog §6`.** A data
  file citing a page that is about to be deleted. Nothing checks CSV→page citations, so this
  will dangle silently. Re-point it when row 60 lands.
- **`residual-machinery:68` must be repaired *before* `11.8` is deleted**, not after — it is
  currently the only pointer from canon to the layer DAG's definition, and it is already broken
  (L-8). If the DAG is not mined first, the `layer : 0..6` field becomes undefined in the new tree.

**3. Checker calibration — what I actually verified, and what I did not.**
Per the brief, I did not trust the green run. In a scratch copy under the session scratchpad
(the corpus was never touched; `git diff --stat journal/pages/` is empty):

- **Probe A** — replaced `residual-generator-catalog §2` with `totally-nonexistent-page-xyz §2`
  at `7.2-residual-machinery.md:68`, restamped the content-hash, re-ran
  `check_book_structure.py --check` → **`book structure OK`, 58 pages, 0 problems.** The
  bare/backticked dangling-id class is completely invisible. This is why the real defect survived.
- **Probe B (control)** — inserted `[totally-fake-page]` as prose on the same page →
  **`FAILED: reference [totally-fake-page] resolves to no page`.** So the checker is live and
  the blindness is specific to the unbracketed syntax, exactly as plan §2 defect 1 predicts.
- **Not checked:** whether `check_data_agreement.py` compares the appendix `Diff`/`Tier` columns
  against `registry-manifest.csv`. It reports clean while 19 such cells disagree (R-2), which
  strongly suggests it does not — but I did not plant a probe to confirm, so I am not claiming it.
- **Not checked:** `out-of-scope-limits-coverage`, whether all 12 of Part F's limits appear in `out-of-scope`.

**4. Rows I could not disposition with confidence.**

- **Row 14** (Part C high-T notes) — these overlap the ledger's rows 1–52 partially and
  unevenly. I marked `mine` per the brief's tie-break rule, but the real instruction to Phase 2
  is *merge per-observable, do not bulk-copy*; a bulk copy will duplicate ~20 clauses the ledger
  already carries better.
- **Row 50** (`Generate`/`Validate`/`Import` as the three `/physics` exports) — `pino-bridge §2`
  clearly owns `Import`; I did not confirm whether it names the other two. If it does, this is a
  `delete`.
- **Row 54's rationale clause** ("bundles are physical-domain cohesion units for the unified
  state vector, not residual-category bins") — I dispositioned the block `delete`, but that one
  sentence is a good statement of *why* the bundle axis exists. Check `observable-bundles`; if
  it is absent there, promote the clause rather than losing it.
- **Row 86** (the operad's compile-time soundness does not survive a host swap) — a real
  structural observation, but it is stated only in terms of Haskell→OCaml/Julia and would read
  as advocacy for a pick that is now reopened. `delete` under the no-mandate rule; someone
  should confirm that is the right call rather than rewriting it host-neutrally.

**5. What the three pages are, in one line each, for the builder.**
`11.7` is a **content-rich page in a dead container** — most of its unique value is live
mathematics and it is the most expensive of the three to lose. `11.8` is **half dead weight,
half load-bearing** — its 89-row table is fully superseded by a CSV that is better in every
column, while §2.2 and §3.3–§3.5 hold facts canon actively depends on and does not state.
`11.9` is **mostly advocacy for a decision that has since reopened** — its durable residue is
about five paragraphs: the requirement list, the seam data contract, the golden test, the
hardware split, and one trap.

**6. Vacuous ownership confirmed on all three pages.** `deriv-observable-catalog`,
`deriv-generator-catalog` and `deriv-language-study` each declare `canonical-for` naming only
their own id (`11.7:6-7`, `11.8:6-7`, `11.9:6-7`) — three of the eighteen. None of the three is
inside the duplicate-topic invariant, which is precisely how `11.8` could carry a full parallel
copy of the formula registry for months without any checker noticing the duplication.
