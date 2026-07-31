# Disposition — oracle/state

Scope: `journal/pages/02-inputs-and-state/` — `2.1-crystal-inputs.md`,
`2.2-unified-state.md`, `2.3-gamma-hat.md`, `2.4-multiscale-state.md`,
`2.5-born-oppenheimer-levels.md`, `2.6-gamma-budget.md` (964 lines, 7,073 words).
Read at: 2af93d2

Target journal/section for all six: `oracle/state/`. Page ids unchanged.

## Disposition rows

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 1 | `authority: canon` + `content-hash:` keys | all six pages, frontmatter (`2.1:4-5`, `2.2:4-5`, `2.3:4-5`, `2.4:4-5`, `2.5:4-5`, `2.6:4-5`) | delete | — | D1/§4: `authority` tier dies with ch. 11; `content-hash` is a restamped identifier git already answers |
| 2 | `referenced-by` lists | all six, frontmatter | delete | — | §4: stays generated, never hand-written; regenerated into `corpus.json` |
| 3 | "Three physically orthogonal inputs fully specify *what crystal, in what conditions*" | `2.1-crystal-inputs.md:18-19` | keep | `oracle/state/crystal-inputs#top-level-inputs` | sole statement of the input triple; cited by `compose-time-pipeline §1`, `product`, `build-order`, `build-sequence` |
| 4 | `PeriodicityStructure` — `d ∈ {0,1,2,3}`, lattice vectors `{a_i}`, periodicity flags, Bravais/space group, cell vectors `h` | `2.1:21-23` | keep | `oracle/state/crystal-inputs#periodicity-structure` | only definition in the corpus |
| 5 | `SiteDecoration` — species at Wyckoff positions, orbital basis, optional spin/charge/occupancy, tag `host\|defect\|adsorbate\|substrate\|impurity` | `2.1:24-28` | keep | `oracle/state/crystal-inputs#site-decoration` | only definition; `multiscale-state §3.2` depends on `SiteDecoration.occupancy` by name |
| 6 | "Defects, surfaces, adsorbates, magnetic configurations, charged systems and alloys are special cases of `SiteDecoration`, not new top-level types" | `2.1:26-28` | keep | `oracle/state/crystal-inputs#site-decoration` | load-bearing closure rule — it is what keeps the input alphabet at three |
| 7 | `Environment` — untyped prose list: temperature, pressure/volume, chemical potentials, applied E/B fields, applied stress, temperature gradient, carrier-injection | `2.1:29-31` | keep | `oracle/state/crystal-inputs#environment` | **homeless fact, confirmed.** No `canonical-for` anywhere names `Environment` (swept all 58 pages' `canonical-for`; only `crystal-inputs: top-level inputs` is even adjacent). See row 8 and Notes §A |
| 8 | The five harsh-environment `Environment` fields, **typed**: `radiation_flux`/`ParticleFlux`, `radiation_dose Φ_dose`/`Fluence`, `displacement_threshold E_d`/`Energy`, `vibration_spectrum`/`PSD`, `p_O2`/`Pressure` | `2.4-multiscale-state.md:427-442` (§12, "Required `Environment` field additions") | move | `oracle/state/crystal-inputs#environment` | a delta table ("*Required additions*") is scaffolding by shape — a diff against another page. Its five rows are the only *typed* `Environment` rows in the corpus; they merge into row 7's table |
| 9 | Same five fields restated untyped inside `crystal-inputs` prose with a cross-cite to `multiscale-state §12` | `2.1:31-34` | delete | — | duplication: collapses into rows 7+8 once the typed table lands on the owning page. The cross-cite disappears with it |
| 10 | "Presence of these fields fires the §4 applicability predicates (first-order decidable on field presence)" | `2.4:440-442` | move | `oracle/state/crystal-inputs#environment` | present-tense rule about `Environment`, not about the slow tier. Makes *absent ≠ zero* load-bearing — see Notes §A |
| 11 | `Reference` = bag of `(Crystal, Environment, weight)` baselines; composes from the three inputs; belongs to the cert layer | `2.1:36-38` | keep | `oracle/state/crystal-inputs#not-inputs` | only statement; `Crystal` is used here as a type name and defined nowhere — Notes §A |
| 12 | `Property` is an output request, a parameter of the oracle-file's `Validate` call | `2.1:38-39` | keep | `oracle/state/crystal-inputs#not-inputs` | agrees with `pino-bridge §1`'s `request` parameter |
| 13 | "(`predict` / `residual` were the pre-oracle-file verb names and no longer exist.)" | `2.1:40` | delete | — | scaffolding: retired names, "no longer exist". D1 verbatim. Not log-worthy — a rename, not an advancement |
| 14 | The 7-tuple `x(t) = (h, R_I, P_I, Π_h, Z_I, γ̂, A)` with per-slot mathematical types | `2.2-unified-state.md:29-40` | keep | `oracle/state/unified-state#slot-set` | the corpus's most-cited single block; 12 pages list `unified-state` in `depends-on` |
| 15 | `A` carried in Weyl gauge `A₀ ≡ 0`, transverse `∇·A = 0`; electrostatic sector in the matter functionals | `2.2:42-44` | keep | `oracle/state/unified-state#slot-set` | but the page **defers** the normative statement to `generic-dynamics` (`3.1-generic-dynamics.md:169-182`), where it actually lives. Retarget the pointer; do not duplicate the paragraph. `traps §25` names both pages as enforcers |
| 16 | Per-slot **array shapes and layouts, units, index order, dtype**, and `γ̂`'s shape as a function of its `CompressionPlan` | **absent** — promised at `2.2#slot-set` by `informed-operator/design/learnable-structure-requirements.md:27-31` (R1) | — (gap) | `oracle/state/unified-state#wire-schema` | **Dangling promise, confirmed by probe.** `2.2:29-40` gives mathematical types (`ℝ^{3N}`, `GL⁺(3,ℝ)`), never array layout; **zero units appear anywhere on the page**; `Z_I` is only "discrete"; `γ̂` has no array shape at all. Probe D3 (Notes §D) shows no checker can see this. Open question `I1` |
| 17 | The 7-tuple are the irreducible DOFs of the micro tier; quantities recoverable by coarse-graining **on the micro timescale and scale** are emergent and stay out — adding one would create a constraint manifold | `2.2:46-53` | keep | `oracle/state/unified-state#emergence` | already the *refined* axiom; the resolution has landed on this page |
| 18 | Quantities not recoverable on the micro timescale/scale are first-class state in their own tier: slow defect populations + composition vectors (hours–years), homogenized device-scale fields; they couple only parametrically, so introduce no constraint manifold | `2.2:55-62` | keep | `oracle/state/unified-state#emergence` | the micro-side half of the three-tier stratification; `multiscale-state` owns the tiers themselves |
| 19 | "(This is also the reconciliation of the **earlier** 'distributions are emergent' wording with `born-oppenheimer-levels`: L4 introduces its own irreducible state … the full distribution itself stays emergent by moment closure.)" | `2.2:64-67` | delete | — | scaffolding: "the earlier wording" is history of the page correcting itself. The substantive clause is already stated present-tense at `born-oppenheimer-levels:62-71`, which owns L4 — deleting loses nothing. Log-worthy row 2 |
| 20 | `x(t)` is a **type** the PINO instantiates per time step; `/physics` holds no values of `x(t)` — it defines what `x(t)` is and how to test a candidate | `2.2:69-71` | keep | `oracle/state/unified-state#type-not-value` | score-not-solve, stated at the state level. Load-bearing for the seam |
| 21 | The seven slot labels are the closed C1 vocabulary `StateComponent`, a `Universe[StateComponent]`; downstream addresses slots by dense ordinal handle, not raw symbol | `2.2:73-76` | keep | `oracle/state/unified-state#slot-set` | R1 depends on this exact rule (`learnable-structure-requirements.md:30-31`) |
| 22 | Title + framing: "γ̂ … the most demanding object in the state vector: one logical entity, multiple inequivalent encodings, different operations cheap on different encodings" | `2.3-gamma-hat.md:26-34` | keep | `oracle/state/gamma-hat` (preamble) | the page's reason to exist |
| 23 | "This file documents … **how the four questions once listed as open data-structure problems resolved** (§4)" | `2.3:38-40` | delete | — | scaffolding: the page advertising its own history. Rows 32-36 keep the resolutions |
| 24 | `Basis ∈ {Real, Reciprocal, Wannier, NaturalOrbital, SymmetryAdapted}` × `Form ∈ {Dense, Sparse, BlockDiag, LowRank}` | `2.3:41-48` (§1) | keep | `oracle/state/gamma-hat#encoding-vocabulary` | sole statement; `canonical-for: γ̂ encoding vocabulary` |
| 25 | The five first-class V1 `(Basis, Form)` pairs and what each is for | `2.3:50-58` | keep | `oracle/state/gamma-hat#encoding-vocabulary` | sole statement |
| 26 | Stage 4 selects one slot per density-matrix node from `(PeriodicityStructure, SiteDecoration)`; transcoders convert on demand | `2.3:60-63` | keep | `oracle/state/gamma-hat#encoding-vocabulary` | this is the `CompressionPlan` topic the page owns |
| 27 | **`/physics` is scorer-only: `γ̂` never evolves inside the oracle.** States arrive complete, are scored, discarded; no trajectory, no `γ̂` with a history | `2.3:67-70` (§2) | keep | `oracle/state/gamma-hat#scorer-only` | cited as the decision by `compose-time-pipeline:183`, `computational-overview:222,226`, `open-decisions:228`. Highest-traffic anchor on the page |
| 28 | "This is not new — `[library-landscape]` and the README already say … **This section used to list time-stepping as a `γ̂` write path, which contradicted them; canon wins** and the write path is construction and self-consistency only." | `2.3:70-73` | delete | — | scaffolding: "used to list … canon wins" is the story of a contradiction closing. The surviving fact ("the write path is construction and self-consistency only") is already in row 30's diagram. Log-worthy row 3 |
| 29 | An EOM-violation residual over `γ̂` scores a supplied `∂_t γ̂` against `L·δE/δx + M·δS/δx` — scoring a proposed rate is not taking a step | `2.3:75-78` | keep | `oracle/state/gamma-hat#scorer-only` | the non-obvious corollary; without it §2 reads as forbidding the `EOM/γ̂` residual |
| 30 | Read path (dominant: apply `Ĥ`, extract density, trace, eigendecomposition) vs write path (construction + self-consistent step) and the two pipelines | `2.3:80-94` | keep | `oracle/state/gamma-hat#read-write-paths` | but see Contradictions/Notes §C — `computational-overview:222-227` restates it with cost detail this page lacks; one page must own it |
| 31 | "**Where trajectory ownership went.**" `/physics` emits a per-tier tangent map + steppable-form manifest (a pure function, not an integrator); the consumer that integrates owns `γ̂` representation health; drift is **exported, not dissolved** | `2.3:96-101` | keep | `oracle/seams/pino-bridge#steppable-form-manifest` (the export) + a one-line consequence at `oracle/state/gamma-hat#scorer-only` | the fact is live and load-bearing; the heading "Where … went" is scaffolding — rename. The manifest is a seam export, not a state fact |
| 32 | Self-consistency is *structured* by the coalgebraic fixed-point form but *solved* by the Stage-4 implicit-diff adjoint; convergence iteration happens above the substrate | `2.3:103-106` | keep | `oracle/state/gamma-hat#read-write-paths` | γ̂-specific; the general Stage-4 rule is `compose-time-pipeline §4` |
| 33 | §3 table — five strategies (codata interface, typed term algebra, e-graph, pullback bundle, tensor network) realized as Stage-4 internals, not architectural peers | `2.3:108-121` | keep | `oracle/state/gamma-hat#stage4-internals` | sole statement; "pullback bundle = multi-slot V2" is the only place the V1/V2 slot cardinality is fixed |
| 34 | §4 heading "The four questions, and where each went" + "This section listed four 'genuinely open CS problems'. They were one problem … seen from four sides … **None is still open here.**" | `2.3:123-131` | delete | — | pure scaffolding — the frame around the resolutions, per exception 1 of the brief. Rows 35-38 carry the resolutions forward. Log-worthy row 4. **Retarget hazard:** 8 external citations point at `gamma-hat §4` — Notes §B |
| 35 | Node identity is **exact**, never bisimulation-up-to-ε: `≈_ε` is not transitive, so it yields no quotient, no canonical representative, nothing to hash. A rewrite is admitted when exact over ℝ *and* its float side conditions are discharged by an e-class analysis carrying interval and not-equals facts. E-graphs stay offline | `2.3:133-141` | keep | `oracle/state/gamma-hat#identity-is-exact` | present-tense guard (brief exception 1). The *general* rule is canonical at `representation-substrate §4.1/§20.4.2` and the rewrite-admission rule at `compose-time-pipeline §3` — cite, do not restate |
| 36 | Materialization policy is a **cost** question with no error term: the rematerialization-vs-storage trade-off; `revolve` (Griewank & Walther, *ACM TOMS* 26(1) 19–45, 2000) optimal for a chain, **NP-complete** on a general DAG (Naumann, *J. Discrete Algorithms* 7(4) 402–410, 2009) | `2.3:143-150` | move | `oracle/compilation/compose-time-pipeline#stage4-adjoint-tape` | the page says so itself: "It belongs to Stage-4 codegen as a schedule over the adjoint tape … **not to this page**". The two literature results are the substance and must not be lost in the move |
| 37 | Long-trajectory drift is not `/physics`'s problem (nothing accumulates in a scorer); the robust DLRA integrators — projector-splitting (Lubich & Oseledets, *BIT* 54, 2014), BUG (Ceruti & Lubich, *BIT* 62(1) 23–44, 2022) — have error bounds **independent of small singular values** (Kieri/Lubich/Walach, *SIAM J. Numer. Anal.* 54, 2016); rank-adaptive BUG (Ceruti/Kusch/Lubich, *BIT* 62, 2022) preserves norm, energy, and monotone gradient decrease — mapping term-for-term onto trace, `L`, and `M` of `generic-dynamics` | `2.3:152-168` | move | `oracle/seams/pino-bridge#steppable-form-manifest` | this is the hand-off content for the consumer that integrates — it belongs with the manifest that declares the hand-off, not on the state page. The `(norm, energy, gradient-decrease) ↔ (trace, L, M)` mapping is the load-bearing claim |
| 38 | Rank-dependent applicability of `(NaturalOrbital, LowRank)` is a **compile-time predicate** decided at Stage 4 from `(PeriodicityStructure, SiteDecoration)`, not a runtime check; four-index objects (BSE, BTE collision matrices) go to TT compression | `2.3:170-177` | keep | `oracle/state/gamma-hat#encoding-vocabulary` | it is a slot-selection rule — same subject as §1, and belongs beside the other slot choices |
| 39 | §5 Diamond MVP: `(Reciprocal, BlockDiag)`, k-blocks as orbitals, ~18 MB, densifying ~460 MB "which is exactly why the encoding forbids it" | `2.3:179-184` | delete | — | verbatim duplication of `gamma-budget:18-25`, which carries the derivation this does not. Replace with a citation to `oracle/state/gamma-budget`. **Unsure-flag:** if Phase 2 folds `gamma-budget` into `gamma-hat` (Notes §E) this becomes the merge site instead |
| 40 | §1 "The emergence-axiom **correction**": "`unified-state` lists defect populations and distributions among quantities that are *emergent — coarse-grainings of `x(t)`* … That classification is **too strong**: it **contradicts** `[born-oppenheimer-levels]` (L4) … and it forbids exactly the physics the project exists to predict" | `2.4-multiscale-state.md:57-64` | delete | — | scaffolding **and factually stale**: the quoted string "emergent — coarse-grainings of `x(t)`" appears nowhere in `unified-state` today (grep: its only occurrence corpus-wide is this quotation of it). Both cited pages already carry the resolution — rows 17-18, 47. See Contradictions 1 |
| 41 | **Refined emergence axiom.** `y` is emergent from a tier **iff** recoverable from that tier's state by coarse-graining on the **same timescale and same scale**. `n_{q,s}`, `f_n(k,r)`, electron/lattice temperatures are emergent at the micro timescale | `2.4:66-70` | keep | `oracle/state/multiscale-state#emergence-axiom` | `canonical-for` topic; the definition the whole stratification rests on. Must survive row 40's deletion intact |
| 42 | Two non-recoverable classes: **slow/history-dependent** (different timescale — defect concentrations, charge-state distributions, H content, oxidation/carbide fronts; frozen at micro timescale, Arrhenius barriers 2–7 eV, carry integrated thermal/irradiation history) and **homogenized/device-scale** (different scale — `T_L, φ, n, p, j` on a device mesh, not derivable from one unit cell) | `2.4:71-81` | keep | `oracle/state/multiscale-state#emergence-axiom` | sole statement of the two-axis split |
| 43 | Because the tiers are independent by timescale **or** by scale they create **no algebraic constraint** with the micro 7-tuple; they couple only parametrically. The full distribution is never promoted | `2.4:83-87` | keep | `oracle/state/multiscale-state#emergence-axiom` | this is the argument that the added tiers do not reintroduce the pathology `unified-state` guards against |
| 44 | "The micro axiom holds verbatim; this document adds the two tiers and **reconciles** `unified-state` ⊥ `born-oppenheimer-levels`." | `2.4:87-88` | delete | — | scaffolding: a document describing its own editorial act. Nothing in it is a fact about the physics or the types |
| 45 | §2 three-tier table — Micro / Slow / Macro × (members, equilibration timescale & scale, index geometry, dynamics) | `2.4:90-97` | keep | `oracle/state/multiscale-state#three-tiers` | `canonical-for: three-tier state stratification`; the page's spine |
| 46 | Slow and macro are **adiabatic parameters** of micro: micro fast-equilibrates at fixed slow/macro under `Environment`; slow/macro drift under time-averaged `⟨micro⟩_τ` or homogenized coefficients | `2.4:98-101` | keep | `oracle/state/multiscale-state#three-tiers` | the coupling contract in one sentence |
| 47 | The slow tier is a configurational layer above L4; the macro tier is **L4's spatial fluid-limit reduction** lifted from one cell to a device mesh — the "irreducible state" `born-oppenheimer-levels` attributes to L4 | `2.4:101-105` | keep | `oracle/state/multiscale-state#three-tiers` | present-tense identification, not a reconciliation narrative. `born-oppenheimer-levels:62-71` states the same thing from the other side — acceptable as a two-way structural fact, but see Notes §C |
| 48 | `/physics` scores each tier's law-violation, the PINO supplies each tier's trajectory (score-not-solve preserved at every scale); **no new computational method** — slow reuses `kinetic-evolution`, macro reuses the device-PDE residual pattern (row 71) | `2.4:105-108` | keep | `oracle/state/multiscale-state#three-tiers` | the closed-alphabet invariant, asserted at the tier level |
| 49 | §3.1 `DefectSpecies` closed C1 `Universe[T]` (`carrier_kind = Closed`, `ordinal_policy = DenseU32`) + the five-host member table with charge states | `2.4:112-127` | keep | `oracle/state/multiscale-state#defect-species` | sole statement; cited as `multiscale-state §3.1` from 2 sites |
| 50 | `DefectSpecies` element record `{name, site : LatticeSite, charge_states, spin}`; adding a member is a versioned `schema_version` bump | `2.4:128-131` | keep | `oracle/state/multiscale-state#defect-species` | the extension rule; parallels `canonical-vocabularies §7` |
| 51 | §3.2 slow-state fiber as cluster **C3** `PersistentMap[TypedKey, V]` (HAMT-32, stage-visible), **not** part of `ResidualKey` identity + the six-field schema table (`conc[D,q]`, `charge_dist[D]`, `H_content`, `oxide_front`, `carbide_thickness`, `dislocation_density`) with types, units, indices | `2.4:133-147` | keep | `oracle/state/multiscale-state#slow-state-schema` | `canonical-for: slow / configurational state schema`. **This is the only fully typed-and-united state schema in my scope** — the shape `unified-state` is missing (row 16) |
| 52 | The slow fiber is a new C3 fiber that is the **dynamic promotion of `SiteDecoration.occupancy`**, not a mutation of `Z_I`; `Z_I` stays immutable; static `occupancy` becomes the initial condition `s(t=0)`; tier hygiene ties no constraint manifold. Drives B11 with defect-resolved sub-outputs in B4 | `2.4:150-158` | keep | `oracle/state/multiscale-state#slow-state-schema` | a *decision*, stated present-tense. Ties directly to row 5's `SiteDecoration` |
| 53 | §4 nine slow-kinetic formulas F-G1…F-H2 with governing equations, barrier values, T/D tags, instantiation forms and bundle assignments | `2.4:161-211` | keep | `oracle/state/multiscale-state#slow-kinetics` | cited as `multiscale-state §4`. Values must be re-seeded from `registry-manifest.csv` rows 105–112, never from the `deriv-*` sources cited inline (brief trap) |
| 54 | The `[deriv-defects]` / `[deriv-high-field]` / `[deriv-observable-catalog]` Part-and-section citations threaded through §4 (≈30 of them) | `2.4:161-211` passim | delete | — | ch. 11 ceases to exist (D3); these citations cannot survive it. The *content* they point at is already inlined here — this page is where those derivations land |
| 55 | "Eight of the nine processes are **new** `FormulaRecord`s (rows 105–112); **F-F5 is the existing row 81, re-tagged** so its output `x_carbide` is a slow-state field" | `2.4:161-162`, `2.4:187-188` | delete framing / keep fact | `oracle/state/multiscale-state#slow-kinetics` | "new"/"re-tagged"/"not re-added" is authoring history. The surviving fact: *`x_carbide` (row 81) is a slow-state field.* Registry row numbers stay |
| 56 | "an earlier '~1 mm' was 170× high" (F-G2 H-diffusion range, correct value √(Dt) ≈ 6 µm in 1000 h) | `2.4:179` | delete framing / keep value | `oracle/state/multiscale-state#slow-kinetics` | the parenthetical is the story of a correction; **6 µm** is the fact. Log-worthy row 5 |
| 57 | Two research-flags inside §4: #46 "OUTSIDE registry unless reaction-rate template present" — satisfied by `kinetic-evolution`; and F-H2's `η_recomb(T_L)`/`σ_d` have **no closed form in the corpus** | `2.4:192-194`, `2.4:208-211` | keep | `oracle/state/multiscale-state#slow-kinetics` + `open-questions:` frontmatter | the second is a live gap, not a remnant → open question `msq-niel-coefficients`. The first is a *resolved* flag → keep one clause, drop "Research-flagged" |
| 58 | §5 `EOM/DefectPopulation` residual: the formula, its derivation as the slow-tier specialization of `‖dx_i/dt − (LδE/δx + MδS/δx)‖²`, axes `(DefectSpecies, ChargeState, SiteClass)`, one `ResidualLeaf` per `(species, charge, site)`, no preaggregation, `ResidualKey`/facets, curriculum band **Refine** `[0.10, 0.60)` | `2.4:215-235` | keep | `oracle/state/multiscale-state#eom-defect-population` | `canonical-for`; most-cited section of the page (4 external `§5` citations) |
| 59 | "This is `[deriv-csp]` Part E.1 `R_ThermalCycleStability`'s population-drift residual **promoted to first-class**." | `2.4:234-235` | delete | — | provenance of a promotion, and it cites a dying container. The residual's definition (row 58) is complete without it |
| 60 | §6 adiabatic driving contract: the five-row `⟨micro⟩_τ` table, the `d s/dt = Φ_kinetic(…)` signature, and the reverse (slow→micro) parametric dependence via `SelfConsistentChargeBalanceOf` + SRH `τ_n = 1/(σ_n v_th N_T)` | `2.4:237-256` | keep | `oracle/state/multiscale-state#adiabatic-driving` | `canonical-for: adiabatic micro→slow driving contract`; the only statement of the bidirectional contract |
| 61 | §7.1 `DeviceMesh : Universe[MeshCell]` C7 closed universe (`DenseU32`, `Roaring\|Bitset`), `MeshCell` carrying `(centroid, volume, face-list)`, fields as C3 fibers, `MerkleDAG diff = O(changed frontier)` | `2.4:262-269` | keep | `oracle/state/multiscale-state#device-mesh` | `canonical-for: device-mesh Universe` |
| 62 | Finite-volume discretization in integral conservation form; the mesh is **conservative** so the `Conservation` residual holds discretely | `2.4:271-274` | keep | `oracle/state/multiscale-state#device-mesh` | the guarantee that makes cat. 9 checkable on the macro tier |
| 63 | "**Relation to the `[open-decisions]` PDE-mesh item (open item 2).** The macro tier **subsumes and narrows** the deferred item: the mesh *format* is now committed … what remains open is only the *mesh-adjoint scheme*" | `2.4:276-280` | delete framing / move gap | `open-questions:` on `oracle/state/multiscale-state` | D7: the register is emitted from the page. The committed part is rows 61-62; the open part is open question `mesh-adjoint-scheme` (duplicated at §15.1 — row 76) |
| 64 | §7.2 `MacroState = (T_L, φ, n, p, j)` with types **and units** (`[K]`, `[V]`, `[m⁻³]`, `[A·m⁻²]`) on `DeviceMesh` | `2.4:282-287` | keep | `oracle/state/multiscale-state#macro-state-schema` | `canonical-for: macro continuum-field state schema`; cited as `§7.2` from `unified-state:60`. The second united schema in scope (cf. row 16) |
| 65 | Per-field justifications: `T_L` spatial coarse-graining of micro `S_vib`; `φ` Poisson-constrained so the constraint is *scored* not free; `n,p` are **0th moments** of `f_n` (densities, not the distribution); `j` via closed-form 1st-moment closure so current-continuity is a scorable balance | `2.4:289-296` | keep | `oracle/state/multiscale-state#macro-state-schema` | each is a promotion decision with a stated reason; deleting the reasons re-opens the question |
| 66 | **Kept emergent (never promoted):** `f_n(k,r)` (promotion double-counts its moments → DAE), `T_e(r)`, `E(r) = −∇φ`, all transport coefficients. "`(T_L,φ,n,p,j)` are a new **scale**, not a new **distribution**" | `2.4:298-301` | keep | `oracle/state/multiscale-state#macro-state-schema` | the exclusion list is as load-bearing as the inclusion list — it is what keeps the DAE out |
| 67 | §8.1 two-temperature energy balance (steady + transient), `τ_E` per-composition, `T_e` **never state**, the four field-regime windows (Ohmic ≲10⁴ V/cm → saturated ≳ few×10⁵), positivity bound `T_e ≥ T_L` scored as a `Positivity` residual | `2.4:305-314` | keep | `oracle/state/multiscale-state#moment-closures` | `canonical-for: moment-closure (emergent T_e, j)`; the regime windows are cited by `applicability-classifiers:115` |
| 68 | "`tau-energy-POP-acoustic` (row 73) carries both channels in one row … **they were proposed as separate `tau-energy-pop` / `tau-energy-acoustic` formulas**" | `2.4:309-311` | delete | — | scaffolding carrying **two retired names**. `retired-names.csv:56-57` retires both to `tau-energy-POP-acoustic` on 2026-07-21; this sentence is their only live use in my scope. Verification §3 requires zero |
| 69 | §8.2 drift-diffusion momentum closure: `j_n`/`j_p` with "**only the diffusion term changes sign** between carriers, never the drift term", Einstein `D = μk_BT/q`, Caughey–Thomas `μ(E)`, saturated collapse `j ≈ qnv_sat`, coefficients micro-supplied, faithful tier verifies vs BTE-`j(E)` | `2.4:317-322` | keep | `oracle/state/multiscale-state#moment-closures` | the sign rule is a trap-grade statement; keep it emphatic |
| 70 | **Degenerate-statistics caveat (declared model-form error):** p⁺ B-doped diamond at 10²⁰–10²¹ cm⁻³ needs `D/μ = (k_BT/q)·F_{1/2}(η)/F_{−1/2}(η)`; V1 carries the nondegenerate form with the discrepancy entered as a declared model-form-error term in `combineTol` on any composition crossing `n_degenerate(host)`; same gate carries the plasmon–phonon/LST exclusion | `2.4:324-332` | keep | `oracle/state/multiscale-state#moment-closures` | `traps §42` enforces it against this page. A live declared-error budget, not a remnant |
| 71 | §9 the three macro balance PDEs (P)/(DD)/(H) + the eight-row homogenization map HM-1…HM-8 (micro output → relation → macro coefficient → equation) | `2.4:334-355` | keep | `oracle/state/multiscale-state#homogenization-map` | `canonical-for: the micro→macro homogenization map`; the actual micro/macro bridge |
| 72 | **Supply contract** — per-composition, error-tagged (cheap closed-form + faithful BTE tied by `Algebraic/MethodEquivalence`, the `dressing` facet), cached (content-addressed, `O(log₃₂ n)`, never a re-solve), compile/runtime split (Stage 1–4 fix the form, Stage 5 evaluates) | `2.4:357-362` | keep | `oracle/state/multiscale-state#homogenization-map` | the "no solver-call hot paths" invariant applied to coefficients |
| 73 | §10 `EOM/Continuum` residual: the general form, the five-row per-field `RHS_field` table, axes `(MeshCell, MacroField)`, `RoaringCoverageMask`, "macro instance of the EOM-violation family, not a new top-level category", score-not-solve restated for the mesh | `2.4:364-378`, `2.4:394-400` | keep | `oracle/state/multiscale-state#eom-continuum` | `canonical-for`; 3 external `§10` citations |
| 74 | **Scharfetter–Gummel is required, not optional:** the exponentially-fitted face flux with `B(t)=t/(e^t−1)`; at UWBG operating point cell Péclet `Pe ≈ 40`, where central differencing makes **the residual operator itself wrong**; removable singularity guarded by `B(t)≈1−t/2`; only the convection-dominated carrier flux needs it | `2.4:380-392` | keep | `oracle/state/multiscale-state#eom-continuum` | `traps §31` enforces it against this page. Highest-consequence single paragraph in my scope |
| 75 | §11 unified three-tier residual contract: the tier × (`x`, index, EOM category, `L`, `M`) table; one residual shape instantiated three ways; macro `L` quasi-static; one `ResidualKey` space across tiers; `CategoryTag` **closed set grows 17 → 19**; `/physics` never pre-sums across tiers | `2.4:404-425` | keep | `oracle/state/multiscale-state#three-tier-residual-contract` | `canonical-for`. The "17 → 19" phrasing is a delta — restate as "the closed set has 19 members, including `EOM/DefectPopulation` and `EOM/Continuum`" |
| 76 | "Resolving `[deriv-transport]` §4.3 ('three distinct state schemas + a *common* residual contract') **into concrete types**" | `2.4:404-405` | delete | — | provenance sentence citing a dying container. The concrete types (row 75) stand alone |
| 77 | §12 heading "**Required** `Environment` field additions" + the driving-tier framing sentence | `2.4:427-430` | delete | — | the delta framing; the five typed rows move to `crystal-inputs` (row 8) |
| 78 | "`p_O2` is a specialization of the existing partial-pressure slot; `μ_env` chemical potentials already present" | `2.4:440-441` | move | `oracle/state/crystal-inputs#environment` | a fact about `Environment`'s own structure — that `p_O2` is not an independent field but a specialization. Must not be lost in the merge |
| 79 | §13 three `Static/Thermodynamic` residuals R-T1 (Gibbs adsorption `‖dγ/dμ + Γ‖²`), R-T2 (charge–Fermi Maxwell `‖dE_form/dE_F − q‖²`), R-T3 (Clausius–Clapeyron analog), with T/D tags; curriculum **Polish** `[0.60, 0.90)` | `2.4:444-455` | move | `oracle/laws/residual-definitions#static-thermodynamic` | these are residual definitions, not state. `residual-definitions §1` item 17 owns the category; a state page defining residuals is the duplication the restructure exists to remove. **Unsure-flag:** they tie `charge_dist[D]`/`[H]`/`x_ox` (slow state) to registry rows 30/44 — if Phase 2 keeps residual definitions beside the state they constrain, this stays. Flagging rather than guessing |
| 80 | §14 "**New** registry rows 105–112" — the eight ids, plus "Rows 103–104 are the two architectural markers; F-F5 = `carbide-growth-parabolic` is the existing row 81, **not re-added**" | `2.4:458-466` | delete | — | duplication + scaffolding. `registry-manifest.csv` is the sole source (the page says so); "new"/"not re-added" is authoring history. Row 53 already binds each formula to its row number |
| 81 | "(the canonical, sole source for row content — **an embedded copy here drifted and was removed by the 2026-07 reconciliation**)" | `2.4:459-461` | delete | — | scaffolding: the story of a defect being fixed. Log-worthy row 6 — the *lesson* (an embedded copy of a CSV drifts) belongs in the log |
| 82 | §15 five open sub-decisions: (1) mesh-adjoint scheme, (2) mesh generation/refinement — structured-tensor for V1, adaptive deferred to V2, (3) hole-transport coefficient anchors, (4) bidirectional slow↔macro coupling, (5) `η_recomb(T_L)`, `σ_d`, regime thresholds — curated `ProvenanceLedger` coefficients, flagged as data-acquisition not invention | `2.4:468-487` | move | `open-questions:` frontmatter on `oracle/state/multiscale-state` (items 1, 3, 5) + body (items 2, 4) | D7. **Items 2 and 4 are not open** — 2 is a committed V1 decision with a V2 deferral, 4 is a stated contract; they are body facts miscategorized as gaps. Items 1/3/5 are genuine open questions |
| 83 | "The corpus was genuinely insufficient on five bounded points; each is a tracked sub-decision, **not a silent gap**" | `2.4:468-470` | delete | — | self-defense about the page's own honesty. The emitted register makes the claim structurally |
| 84 | §16 "Landing edits to existing docs" — the entire section, listing edits already applied to `unified-state`, `generic-dynamics`, `born-oppenheimer-levels`, `residual-definitions`, `crystal-inputs`, `canonical-vocabularies`, `open-decisions`, the registry | `2.4:489-496` | delete | — | pure scaffolding: a completed to-do list of edits to other pages, including "(contradiction removed)". Every item is either already applied (verified: rows 17-18, 47) or superseded by this disposition table |
| 85 | The 7-tuple partitions into four levels with dependencies flowing strictly upward (L4→3→2→1); the hierarchy partitions the **state-component space**, complementary to `PhysicsGraph` which partitions the *computation* | `2.5-born-oppenheimer-levels.md:34-38` | keep | `oracle/state/born-oppenheimer-levels#hierarchy` | `canonical-for: 4-level BO hierarchy`; the complementarity claim prevents a standing confusion |
| 86 | L1–L4 definitions: operands, regimes, and mathematical apparatus per level | `2.5:40-55` | keep | `oracle/state/born-oppenheimer-levels#hierarchy` | sole statement; `capability-slices` and `cross-cutting-rules` depend on it |
| 87 | Each level uses lower levels as inputs but introduces its own irreducible state; a **regime** is a navigational *view* across contributing levels | `2.5:57-60` | keep | `oracle/state/born-oppenheimer-levels#hierarchy` | defines "regime", used corpus-wide |
| 88 | **L4's own irreducible state is the macro continuum tier** — `T_L, φ, n, p, j` on a device mesh, full distribution kept emergent by moment closure; slow defect populations form a first-class slow tier; micro 7-tuple is the L1/L2 tier | `2.5:62-69` | keep | `oracle/state/born-oppenheimer-levels#l4-irreducible-state` | present-tense and correct; the resolution **has** landed here |
| 89 | "…**this resolves the apparent tension** with `unified-state`'s emergence wording (see `unified-state` and `multiscale-state §1`)" | `2.5:69-71` | delete | — | scaffolding: names a tension that no longer exists on either page, and its `multiscale-state §1` pointer lands on the section row 40 deletes. Row 88 survives without it |
| 90 | BO level is **derivable** from a node's transitive inputs — not a stored field on `Node`; Stage 1 ordering follows the level discipline | `2.5:73-77` | keep | `oracle/state/born-oppenheimer-levels#hierarchy` | the anti-denormalization rule; `physics-graph §5` agrees |
| 91 | §1 dressing tiers are **V1-vs-V2 implementation scope, not a runtime hierarchy**; dressing is a Stage-4 codegen choice; the `dressing` tag is a provenance label, **not a loss-weighting axis** | `2.5:79-86` | keep | `oracle/state/born-oppenheimer-levels#dressing-tiers` | `canonical-for: dressing tiers`; the "not a loss-weighting axis" clause is load-bearing for `/informed-operator` |
| 92 | The Layer 1 / 1.25 / 1.75 / 2 / 3 table with per-layer members and cert types (`OneShotCert`, `IterativeResult`) | `2.5:87-119` | keep | `oracle/state/born-oppenheimer-levels#dressing-tiers` | sole statement. **`Layer-1.75` is one of the four nomenclature defects (plan §4)** — propose a rename to Javier, do not rename unilaterally |
| 93 | **Frozen at reference (normative):** a Layer-1.25 dressing is computed once per composition at the reference state and is thereafter constant; contributes no gradient; gap-vs-strain enters only through row 63's deformation potential; cost is a **dressing-staleness** term in the error model | `2.5:96-104` | keep | `oracle/state/born-oppenheimer-levels#dressing-tiers` | normative and present-tense; the deliberate trade is stated with its price |
| 94 | "What is **NOT yet declared** is the **validity radius** … Until it is, the staleness term has no bound, and a composition cannot be refused for leaving the radius because no radius is stated. Tracked in `[open-decisions]`." | `2.5:104-109` | delete | — | **stale gap: `open-decisions:113-121` closed it on 2026-07-21** — the estimator `‖Δx‖·‖∂(dressing)/∂x‖_ref` *is* the radius, measured once at the reference state, entering `combineTol`. See Contradictions 2. Replace with the resolution (row 95), not with nothing |
| 95 | The resolution to fold in: dressing-staleness bound = `‖Δx‖ · ‖∂(dressing)/∂x‖_ref`, sensitivity coefficient measured once at compile time, `OneShotCert` gains the coefficient field, product enters `combineTol` | `journal/pages/10-process-and-governance/10.2-open-decisions.md:113-121` (outside my scope) | move | `oracle/state/born-oppenheimer-levels#dressing-tiers` | brief exception 1: a closed item's resolution is a present-tense fact and belongs on the page that owns the topic. Flagged for the `open-decisions` surveyor as a cross-scope handoff |
| 96 | Still-open residue of that item: **G₀W₀ cost is not scope-tagged by cell size** — T2 (≤10 s) plausible at MVP scale, hours for V1 defect supercells, so the tier table is violated silently rather than refused | `10.2-open-decisions.md:122-125` (outside my scope) | move | `open-questions:` on `oracle/state/born-oppenheimer-levels` | genuinely open, and it is about Layer-1.25's cost tier — this page owns the tier. Open question `g0w0-cost-scope-tag` |
| 97 | Diamond MVP runs entirely against Layer 1.25, preserving the closed-form discipline; needs one dressing wired | `2.5:121-123` | keep | `oracle/state/born-oppenheimer-levels#dressing-tiers` | MVP scope commitment |
| 98 | **G₀W₀:** PBE underestimates the diamond indirect gap by ~23% (~4.2 eV vs measured 5.47 eV); G₀W₀ corrects to ~5.5 eV | `2.5:124-126` | keep | `oracle/state/born-oppenheimer-levels#dressing-tiers` | **value-checked:** agrees with `physics/library/cert/reference-data/material-constants.csv:28` (`bandgap-indirect, diamond, 300 K, 5.47 eV ± 0.01`, whose own note reads "PBE −23% ⇒ G₀W₀/hybrid path (registry row 6)"). Re-seed from the CSV, not from this page |
| 99 | **First-order SCP is judged and not wired:** marginal at 773 K, growing above 1500 K; MVP covers vibrational T-dependence with QHA (registry row 12, "QHA suffices ≤800 °C"); full SCPH (row 13) defers with Layer 1.75 | `2.5:126-130` | keep | `oracle/state/born-oppenheimer-levels#dressing-tiers` | a live scope decision with its reason; `capability-slices` carries the QHA window |
| 100 | Dense `γ̂` is `O(N_r²)` and "**was flagged as** a feasibility risk"; at MVP scale a non-issue because γ̂ is never densified | `2.6-gamma-budget.md:15-16` | keep fact / delete framing | `oracle/state/gamma-budget#budget` | "was flagged as" is history; "γ̂ is never densified" is the live rule and the page's thesis |
| 101 | Encoding: `(Reciprocal, BlockDiag)`, one block per k-point, each stored as orbitals `N_PW × N_b`, not dense `N_PW × N_PW` | `2.6:18-20` | keep | `oracle/state/gamma-budget#budget` | consistent with `gamma-hat §1` row 24; this page carries the sizing consequence |
| 102 | Sizing derivation: PW cutoff ~400 eV ⇒ `N_PW ≈ 1000`; `N_b ≈ 40`; 8×8×8 MP ⇒ ~29 irreducible k-points; `N_PW × N_b × 16 B × N_k` ≈ **~18 MB**; densified `N_PW² × 16 × N_k` ≈ **460 MB** | `2.6:21-25` | keep | `oracle/state/gamma-budget#budget` | `canonical-for: γ̂ MVP budget`; the only place the arithmetic is shown. `gamma-hat §5` (row 39) quotes the two numbers without it |
| 103 | Warm-start initializer: tight-binding 3NN sp³d⁵ for carbon ⇒ ~18×18 Hamiltonian per k, kilobytes; seeds the SCF inner loop; **not a separate residual path** | `2.6:26-28` | keep | `oracle/state/gamma-budget#budget` | the "not a separate residual path" clause prevents a wrong reading; `forced-decisions` is the dependency |
| 104 | Beyond MVP: defect/interface supercells grow `N_PW` linearly, orbital storage stays ≈ linear in `N_atoms × N_b`; the dense-γ̂ concern returns only if a large supercell is densified — which the encoding forbids. **"A supercell memory budget is the first thing to revisit when leaving the primitive cell."** | `2.6:29-32` | keep | `oracle/state/gamma-budget#beyond-mvp` | the final sentence is an unowned forward obligation — candidate open question `supercell-memory-budget`, see Notes §E |

## Open questions

| id | question | owning page | why it is open |
|---|---|---|---|
| `state-wire-schema` | Per-slot wire schema for the 7-tuple: dtype, unit, index order, memory layout, and `γ̂`'s array shape as a function of its `CompressionPlan` | `oracle/state/unified-state` | R1 (`learnable-structure-requirements.md:27-31`) obliges the operator to emit "per-slot array shapes and layouts, units, and the gauge conventions recorded there" — none of it is recorded there. The seam's mandatory structural check has no specification to check against. (= salvage `I1`) |
| `environment-schema` | The closed `Environment` field set, each field's type and unit, and the **structural / swept** partition | `oracle/state/crystal-inputs` | `Environment-structural` keys the kernel cache (`compose-time-pipeline:278`, `computational-overview:590`) and no page says which fields are structural. A structural field misfiled as swept silently reuses a kernel outside its envelope. (= salvage `I0`) |
| `crystal-type` | Is `Crystal` the pair `(PeriodicityStructure, SiteDecoration)` or the full triple with `Environment`? | `oracle/state/crystal-inputs` | `(Crystal, Environment) → Bool` is the applicability signature on every registry row, `CouplingChannel`, `ResidualGenerator`, and property template. `Crystal` is defined nowhere (grep: zero definitions, ≥7 signature uses). The pairing with `Environment` implies the pair, but nothing states it |
| `mesh-adjoint-scheme` | Discrete- vs continuous-adjoint of the finite-volume operator, for differentiating `EOM/Continuum` | `oracle/state/multiscale-state` | stated twice on the page (`2.4:276-280`, `2.4:473-475`); inherits the Stage-4→Stage-5 AD seam. Live residue of `open-decisions` item 2 |
| `hole-transport-anchors` | `μ_p, α_p, v_sat,p` anchors per host — the `p` schema is committed, the coefficients are not | `oracle/state/multiscale-state` | `2.4:478-479`. A per-composition data gap; every bipolar macro composition is unanchored until it closes |
| `msq-niel-coefficients` | `η_recomb(T_L)` and the NIEL displacement cross-section `σ_d(host, particle, energy)` | `oracle/state/multiscale-state` | `2.4:208-211`, `2.4:483-487`: **no closed form exists in the corpus** — only the coupling structure and a curated `ProvenanceLedger` slot. F-H2 cannot be evaluated without them. A data-acquisition task, explicitly not to be invented |
| `regime-threshold-windows` | Per-material regime-switch field windows are order-of-magnitude only | `oracle/state/multiscale-state` | `2.4:485-487`; the §8.1 windows (`10⁴/10⁵/few×10⁵ V/cm`) gate `applicability-classifiers`' per-sample mask, so their width is load-bearing |
| `g0w0-cost-scope-tag` | G₀W₀ cost is not scope-tagged by cell size: T2 (≤10 s) at MVP scale, hours for V1 defect supercells | `oracle/state/born-oppenheimer-levels` | `open-decisions:122-125`. The tier table is violated silently rather than refused. A cost claim, so the ε rule does not reach it. **Cross-scope:** the text lives on `10.2-open-decisions`, the topic belongs here |
| `supercell-memory-budget` | The γ̂ memory budget when leaving the primitive cell | `oracle/state/gamma-budget` | `2.6:31-32` says it "is the first thing to revisit"; nothing tracks it, so it is an obligation with no owner |

## Log-worthy advancements

| date | finding or decision | evidence | attribution | superseded |
|---|---|---|---|---|
| 2026-07 (reconciliation) | **The refined emergence axiom.** A quantity is emergent from a tier iff recoverable by coarse-graining *on the same timescale and the same scale*. This admitted the slow and macro tiers as first-class state without reintroducing the constraint-manifold pathology, and made aging and device-scale operation representable at all | `multiscale-state §1` (`2.4:66-88`); landed at `unified-state:46-62` | corpus reconciliation | the unqualified "distributions and defect populations are emergent" rule of `unified-state` |
| 2026-07 | **`unified-state` ⊥ `born-oppenheimer-levels` resolved:** L4's "own irreducible state" is made concrete as the macro continuum-field tier, with the full distribution kept emergent by moment closure | `born-oppenheimer-levels:62-71`; `multiscale-state:101-105` | corpus reconciliation | the stated contradiction between the two pages |
| 2026-07-21 | **`/physics` is scorer-only for `γ̂`.** Resolved a standing contradiction: `library-landscape` and the README denied trajectories while `gamma-hat §2` listed time-stepping as a `γ̂` write path. Canon won; the write path is construction and self-consistency only. Consequence: drift is **exported** to the integrating consumer via the steppable-form manifest, not dissolved | `gamma-hat:67-73`; `10.5-timeline.md:257-260` | 2026-07-21 oracle-file decision | `gamma-hat §2`'s time-stepping write path |
| 2026-07-21 | **The four γ̂ data-structure questions were one problem, and it closed.** Exact content-addressed identity meeting approximate numerics, seen from four sides. Resolution: **identity stays exact; ε is estimated beside it.** `≈_ε` is not transitive ⇒ no quotient, no canonical representative, nothing to hash — so identity cannot be bisimulation-up-to-ε. Dispositions: ε-equality → the rewrite-admission rule; materialization → a Stage-4 adjoint-tape schedule (a cost question with no error term); drift → exported to the consumer; rank-applicability → a Stage-4 compile-time predicate | `gamma-hat §4` (`2.3:123-177`); `representation-substrate §4.1`/`§20.4.2`; `open-decisions:58-70` | 2026-07-21 | `open-decisions` item 3; the "genuinely open CS problems" framing in `computational-overview` |
| 2026-07 | **H redistribution range corrected 170×.** Diamond interstitial H at 500 °C: `√(Dt) ≈ 6 µm` in 1000 h, not the earlier ~1 mm. Changes whether H redistribution is a device-scale or a near-surface phenomenon | `multiscale-state:177-180` (F-G2, `E_diff = 1.7 eV`, `D(500 °C) ≈ 1e−13 cm²/s`) | corpus reconciliation | the ~1 mm estimate |
| 2026-07 | **An embedded copy of registry rows drifted from the CSV and was removed**, establishing `physics/library/formulas/registry-manifest.csv` as the sole source for row content | `multiscale-state:458-461` | 2026-07 reconciliation | the embedded row table in `multiscale-state §14` |
| 2026-07 | **Frenkel-pair yield was dimensionally invalid** without the macroscopic displacement cross-section `Σ_d = N_atom·σ_d` (cm⁻¹): the bare `N_d·(1−η)·Φ_dose` is a fluence (cm⁻²), not a concentration | `multiscale-state:201-211`; `traps §7` | corpus reconciliation | the pre-`Σ_d` F-H2 expression |
| 2026-07 | **Scharfetter–Gummel is mandatory for the macro carrier flux.** At the UWBG operating point (1 MV/cm, ~10 nm cells) the cell Péclet number is ≈40, where central differencing makes the *residual operator itself* wrong — the operator would be scored against a discretization artifact | `multiscale-state:380-392`; `traps §31` | corpus reconciliation | naive/central finite-volume differencing for `j_f` |
| 2026-07-21 | **The dressing-staleness bound exists:** a frozen Layer-1.25 dressing owes an estimator like any other approximation, and the estimator *is* the validity radius — `‖Δx‖·‖∂(dressing)/∂x‖_ref`, sensitivity measured once at the reference state | `open-decisions:113-121` | 2026-07-21 | verifier-soundness gap 3 ("no declared validity radius"), **still stated as open at `born-oppenheimer-levels:104-109`** |
| 2026-07-21 | **`tau-energy-pop` and `tau-energy-acoustic` merged into `tau-energy-POP-acoustic` (row 73)** — one row carrying both the polar-optical and acoustic channels | `retired-names.csv:56-57`; `multiscale-state:309-311` | 2026-07-21 retag | the two separate proposed formulas |

## Contradictions — COLLECTED, NOT RESOLVED

| claim | source A | source B | nature of the conflict |
|---|---|---|---|
| What `unified-state` says about emergence | `multiscale-state:59-60`: "`unified-state` lists *defect populations* and *distributions* among quantities that are '**emergent — coarse-grainings of `x(t)`**' and therefore forbidden from the state" | `unified-state:46-62`: emergence is qualified "on the micro timescale and scale", and defect populations are explicitly named "**first-class state in their own tier, not emergent**" | A **dangling quotation**: the quoted string appears nowhere in `unified-state` — its only occurrence corpus-wide is inside this quotation of it. `multiscale-state §1` argues against a version of `unified-state` that no longer exists. Same defect *class* as R1 (a citation that resolves to a page which does not contain what the citation claims), in a new form — a quoted string rather than a promised table |
| Whether the Layer-1.25 validity radius is declared | `born-oppenheimer-levels:104-109`: "What is **NOT yet declared** is the validity radius … Until it is, the staleness term **has no bound**, and a composition cannot be refused for leaving the radius because no radius is stated. Tracked in `[open-decisions]`" | `open-decisions:113-121`: "~~No declared validity radius for frozen Layer-1.25 dressings.~~ **Closed 2026-07-21** — … the estimator *is* the radius … `OneShotCert` gains the coefficient field, and the product enters `combineTol` as the dressing-staleness term that already exists but **had no number in it**" | **Second realized instance of the register/page drift class (plan §2 defect 6).** The page states a gap the register says is closed, and cites that register as tracking it. Exactly what D7 makes unrepresentable. Note both sources agree the term exists in `combineTol`; they disagree only on whether it has a bound |
| Whether the four γ̂ questions were ever "the only open CS problems" | `journal/live/specs/2026-07-21-oracle-code-spec-research-brief.md:125`: the entry "quoted canon as calling these 'the only open CS problems in the design'" | `computational-overview §13` "explicitly disclaimed it" (per the same line) — the spec file records canon saying the opposite *at the time* | A self-reported mis-citation of canon inside an unswept stratum (`journal/live/specs/` has never been swept — salvage README). Registered because it is evidence that `gamma-hat §4`'s status was reported inconsistently across strata, not because the resolution is in doubt |
| Where the gauge conventions are recorded | `learnable-structure-requirements.md:27-31` (R1): emitted candidates must match "the gauge conventions **recorded there**" — pointing at `unified-state` | `unified-state:42-44` carries a parenthetical and explicitly defers: "normative gauge/partition paragraph in `generic-dynamics`"; the normative text is at `generic-dynamics:169-182` | Not a physics conflict — a **pointer conflict**. The seam requirement names the wrong owner. Registered so the builder retargets R1 rather than duplicating the paragraph onto `unified-state` |

## Notes for Phase 2

### A. The `Environment` record — what a complete schema needs, and who should own it

**Confirmed homeless.** I swept the `canonical-for` block of all 58 pages: no page names
`Environment`, and the only adjacent topic in the corpus is `crystal-inputs: top-level
inputs`. Meanwhile `Environment` appears in signatures on at least 13 pages —
`coupling-structure:82`, `named-formulas:54,176`, `applicability-classifiers:31,117,124`,
`residual-machinery:83,124`, `property-templates:51,79,84,96,100`, `pino-bridge:40`,
`residual-definitions:235`, `compose-time-pipeline:247,255,278`,
`computational-overview:52,334,473,590`, `cert-obligations:63`, `product:102,107,132`,
`build-order:21`, `build-sequence:37`, `glossary:35`, `traps:241` — and as a column header
in all five `physics/library/cert/reference-data/*.csv` files.

**Owner: `oracle/state/crystal-inputs`, anchor `#environment`.** It already owns "top-level
inputs" and already carries the (untyped) list; `multiscale-state §12` is shaped as a delta
("*Required* additions") and a delta table cannot survive D1. Add to `owns`:
`Environment record schema` and `structural/swept Environment partition`.

**A complete schema needs four things the corpus does not have anywhere:**

1. **Types and units per field.** Only the five harsh-env fields are typed
   (`multiscale-state:432-438`). The base fields are bare prose nouns. The field *names*
   are recoverable — `temperature`, `applied_electric_field`, `applied_stress`,
   `temperature_gradient` from `deriv-high-field:592`, `μ_env` from `multiscale-state:440`,
   plus pressure-or-volume, carrier-injection, applied magnetic field from
   `crystal-inputs:29-31` — but their types and units are not stated anywhere, and
   `deriv-high-field:592` is an appendix page (mine, do not seed values from it).
2. **The structural / swept partition, per field.** `Environment-structural` is used at
   `compose-time-pipeline:278` and `computational-overview:590` to key the kernel cache
   and is **defined nowhere** (grep: two uses, zero definitions). Swept scalars are
   re-evaluated per training sample (`applicability-classifiers:116-124`, `traps §33`);
   structural ones trigger recompile (`product:107`). Misfiling one silently reuses a
   kernel outside its envelope — this is why the partition is load-bearing, not cosmetic.
   Note `applied_stress` and `applied_magnetic_field` are the interesting cases: both can
   change the symmetry the Stage-2 quotient is built on.
3. **Absent ≠ zero.** `multiscale-state:440-442` makes *presence of a field* fire an
   applicability predicate ("first-order decidable on field presence"). So the schema must
   admit an unset state distinct from a zero value, and the set must be **closed and
   versioned** (a `schema_version` bump, as `DefectSpecies` has at `multiscale-state:129-131`)
   — otherwise adding a field silently changes which formulas apply to every existing
   composition.
4. **The `Environment` box.** `product:107` and `applicability-classifiers:124` stamp each
   emitted kernel with the scalar ranges its Stage-2.5 structure is valid on. The box is a
   per-swept-field range set — it cannot be specified until (2) says which fields are swept.

**`Crystal` is a third homeless type** and I found it while doing this. `(Crystal,
Environment) → Bool` is *the* applicability signature — every registry row, every
`CouplingChannel`, every `ResidualGenerator`, five property templates, and the glossary
entry use it — and `Crystal` is defined nowhere in the corpus. `crystal-inputs:36-38` uses
it in `(Crystal, Environment, weight)` without introducing it. It is almost certainly
`(PeriodicityStructure, SiteDecoration)`, but "almost certainly" is what the restructure
exists to eliminate. Same owner, same anchor.

### B. Retargeting hazard: `gamma-hat §4` has eight inbound citations

Row 34 deletes the framing of §4 and rows 35-38 scatter its four resolutions across three
pages. Eight external citations point at `gamma-hat §4` and **most cite it for the story,
not the content**: `README.md:105-106`, `open-decisions:58-70` (a struck-through item),
`computational-overview:229-232` and `:615-618`, `compose-time-pipeline:231-233`,
`10.5-timeline.md:212`, and two in `journal/live/specs/`. Each needs a decision, and three
of the sites are themselves scaffolding that other surveyors will delete. Do the
`gamma-hat` rewrite **after** the `computational-overview` and `open-decisions` fragments
land, or the retargets will be written twice.

`computational-overview:615-618` argues explicitly for keeping the closed item visible:
*"an entry that silently disappears from it reads as though it was never a problem."* D1
and D2 overrule that — the log is where it stays visible — but the builder should expect
the same argument to recur wherever a closed item is deleted, and answer it the same way.

### C. Three declared duplications to collapse, and one that is fine

- `computational-overview:222-227` restates `gamma-hat §2`'s read/write asymmetry **with
  cost detail `gamma-hat` lacks** (`matmat` against `N_PW × N_b` factors; costs set by
  `N_b`, not `N_PW²`). Do not delete either blindly — merge the cost detail into
  `oracle/state/gamma-hat#read-write-paths` and leave a citation behind.
- `computational-overview:229-240` restates the four γ̂ resolutions and labels itself
  "Summarised here; `gamma-hat §4` is canonical". Collapse to a citation.
- `gamma-hat §5` (row 39) restates `gamma-budget`'s two numbers without its derivation.
- **Fine as-is:** `unified-state:55-62` and `multiscale-state §1-2` state the tier split
  from the micro and multi-tier sides respectively. That is one fact viewed from two
  levels, not duplication — but only *after* row 40 removes `multiscale-state §1`'s
  argument-against-a-stale-quotation framing.

### D. What I checked mechanically, and what the checkers cannot see

Both checkers report clean on `2af93d2` and on a scratch copy of the tree. Per the brief I
planted defects rather than trusting that. Probes were run in
`scratchpad/probe/` (full copy of `journal/`, `physics/`, `informed-operator/`,
`README.md`), each planted in `2.2-unified-state.md`, restamped, then `--check`ed:

| probe | planted | result |
|---|---|---|
| A | `` `multiscale-state §99` `` — §-ordinal to a nonexistent section | **caught** |
| B | `` `uwbg-observable-catalog` `` — backticked ref to a nonexistent page | **not caught** |
| C | `[uwbg-observable-catalog]` — bracketed ref to a nonexistent page (control) | **caught** |
| D1 | `` `gamma-budget §1` `` — §-ordinal into a page that has **no numbered sections** | **not caught** |
| D2 | `` `gamma-budget §77` `` — same, absurd ordinal | **not caught** |
| D3 | "Per-slot memory layouts … are tabulated in `` `multiscale-state §12` ``" — section exists, claim absent | **not caught** |
| E | both a bracketed and a §-ordinal bogus ref planted in `informed-operator/design/` | **not caught** — the file is not walked at all |

Two consequences beyond what the plan records:

1. **The plan's §4 rationale for deleting `§N` ordinals is half right.** Ordinals do *not*
   "rot silently" in general — probe A shows the resolver fires
   (`check_book_structure.py:466-471`). But `:468-469` reads
   `if pid not in coords or not coords[pid]: continue`, with the comment *"unknown target
   or a page with no numbered headings"*. **33 of 58 pages have no `## <digit>` headings**,
   so every `§N` citation into them is skipped. Three of those are mine —
   `crystal-inputs`, `unified-state`, `gamma-budget`. `:470` also accepts `§8.2` whenever
   `§8` exists, so subsection precision is unchecked. Declared anchors fix all of this;
   the point is that the current guarantee is narrower than either the plan or a green run
   suggests.
2. **Probe D3 is the dangling-promise class**, and it confirms the salvage README's finding
   from the other direction: the defect survives even when the cited section *exists*. No
   syntactic check can catch it. If Phase 2 wants mechanical coverage, the only lever I see
   is requiring a citation to name the **topic** it is fetching (`[unified-state#wire-schema
   → per-slot units]`) and checking the topic against the target's `owns` — turning a
   content claim into a graph claim. That is a design proposal, not a finding.

I did **not** verify that `check_data_agreement.py` sweeps my six pages for value
disagreement; I confirmed only that it reports clean. Treat value-agreement in my scope as
**not checked**. The one value I did check by hand is row 98's diamond gap, against
`material-constants.csv:28`, and it agrees.

### E. Two structural observations I am flagging rather than acting on

- **`gamma-budget` is a merge candidate.** 246 words, one owned topic (`γ̂ MVP budget`),
  one `depends-on` (`forced-decisions`), and exactly **one** referencing page — `gamma-hat`,
  which restates its two headline numbers. Folding it into
  `oracle/state/gamma-hat#mvp-budget` would remove a page, remove a duplication, and cost
  nothing. I did not disposition it that way because the plan's §3 names `gamma-budget` as
  a surviving page in `oracle/state/`, and page-set changes are Javier's call at the
  Phase 1 gate. Rows 100-104 assume it survives; if it merges, they all retarget to one
  anchor.
- **No page in my scope is vacuously owned.** All six declare `canonical-for` topics
  distinct from their ids, and none appears in the plan's list of 18. `gamma-budget` is the
  closest call (`γ̂ MVP budget` vs id `gamma-budget`) — distinct by the letter of the rule,
  but it is one topic that restates the page title, so under the new `owns` requirement it
  should gain a second topic (the never-densify rule of row 100 is the obvious candidate)
  or merge per the point above.

### F. Ordering hazards for the builder

1. **`multiscale-state` must be rewritten before `unified-state` and
   `born-oppenheimer-levels` are finalized.** Rows 40, 44, 84 delete the reconciliation
   narrative; rows 19 and 89 delete the answering paragraphs on the other two pages. All
   three deletions are only safe together — done singly, each looks like it is removing the
   sole statement of the tier split.
2. **Row 8 (the `Environment` table move) crosses page boundaries in the opposite direction
   from the citation.** `crystal-inputs` currently *cites* `multiscale-state §12`;
   afterwards `multiscale-state` will need to cite `crystal-inputs#environment` from §4's
   applicability predicates. Do not leave both citing each other.
3. **Row 95 imports a resolution from `10.2-open-decisions`, which is outside my scope and
   is being dissolved into per-page frontmatter (plan §3).** If the `open-decisions`
   surveyor routes that resolution elsewhere, rows 94-96 conflict. Coordinate before
   writing `born-oppenheimer-levels`.
4. **Rows 36-37 move literature citations out of `gamma-hat` into `compose-time-pipeline`
   and `pino-bridge`.** Six papers with full bibliographic detail (Griewank & Walther;
   Naumann; Lubich & Oseledets; Ceruti & Lubich; Kieri/Lubich/Walach; Ceruti/Kusch/Lubich).
   They are the substance of those two bullets. If a move drops them, the surviving text
   asserts "the literature has an answer" without naming it.
5. **Row 53 (§4's nine formulas) and row 71 (§9's homogenization map) carry ~40 numeric
   values** — barriers, cross-sections, diffusivities, thresholds. Every one traces to a
   `deriv-*` page that is being deleted (row 54). Re-seed from
   `registry-manifest.csv` rows 105–112 and `9.1-accuracy-ledger` per the brief's trap, and
   expect that some values exist *only* in the appendix. Where that happens it is a
   Contradiction row for auditor 2 or an acquisition task — not a value to copy forward
   from an appendix page.

### G. What I could not disposition confidently

- **Row 79** (`multiscale-state §13`, the three thermodynamic-identity residuals). They are
  residual *definitions* sitting on a state page, so structurally they belong with
  `residual-definitions`. But all three are consistency conditions **on slow-tier state
  fields** (`charge_dist[D]`, `[H]`, `x_ox`), and splitting them from the schema they
  constrain may be the worse outcome. I routed them to `oracle/laws/residual-definitions`
  and am flagging it; whoever holds the `oracle/laws` fragment should decide, since they
  can see whether §13's siblings (items 1–17 of `residual-definitions §1`) are staying put.
- **Row 31/37** (the steppable-form manifest and the DLRA literature). I routed both to
  `oracle/seams/pino-bridge`. They could equally belong to `oracle/operator/seam`, which is
  being mined fresh from `informed-operator/design/` and does not exist yet. Whoever builds
  that page should re-check.
- **Row 39** depends on the `gamma-budget` merge question in Notes §E.
