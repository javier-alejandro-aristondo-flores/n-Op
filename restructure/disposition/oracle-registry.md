# Disposition — oracle/registry

Scope: all ten pages of `journal/pages/06-vocabularies-and-registry/` —
`6.1-canonical-vocabularies` · `6.2-typeclass-alphabet` · `6.3-topology-atlas` ·
`6.4-computational-methods` · `6.5-property-templates` · `6.6-named-formulas` ·
`6.7-observable-bundles` · `6.8-typed-compositions` · `6.9-formula-registry` ·
`6.10-properties`.
Consulted as reference, not dispositioned: `physics/library/formulas/registry-manifest.csv`,
`journal/tools/check_data_agreement.py`, `journal/tools/check_book_structure.py`,
`journal/contents.md`, `journal/index.md`, `journal/glossary.md`.

Read at: 2af93d2

---

## What I swept, and what the checkers actually catch

Both checkers report clean at `2af93d2`. Per the brief I planted seven defects of
the exact classes I make claims about, in a scratch copy at
`/tmp/.../scratchpad/registry-probe-*` (full tree copy, no `.git`, checkers
restamped between probes so `content-hash` staleness could not mask the result).
The copy has since been deleted.

| # | Planted defect | Structure | Data | Verdict |
|---|---|---|---|---|
| A | `6.9` says **133** substantive formulas (CSV + `6.1` say 132) | **FAILED** | clean | count drift vs CSV **is** caught |
| B | `6.9` cost-tier `T2` bound `≤10 s` → `≤100 s`, `6.6` untouched | OK | clean | **legend drift between two pages is NOT caught** |
| C | undeclared `formula = totally-made-up-thing` in `6.8` | OK | **FAILED** (`formula-arg`) | the declared-gap mechanism works as `6.8` claims |
| D | `6.2` `canonical-for` reduced to its own id | OK | clean | **vacuous ownership is NOT caught** (plan defect 4, confirmed in scope) |
| E | backticked `` `uwbg-observable-atlas` `` (nonexistent id) in `6.3` | OK | clean | **backticked refs are NOT checked** (plan defect 1, confirmed in scope) |
| F | bracketed `[uwbg-observable-atlas]` in `6.3` | **FAILED** | clean | bracketed refs are checked |
| G | `6.3` also claims topic `bundle signatures` | **FAILED** | clean | duplicate-topic invariant fires — on non-vacuous topics only |

Probe B is the load-bearing one for this chapter: the `T0–T3` legend is written
out twice, verbatim, and nothing holds the two copies together.

Citation-form census for the chapter: **24 bracketed** `[id]` refs (checked) and
**24 backticked** page-id refs (unchecked). Four pages — `6.3`, `6.4`, `6.5`,
`6.7` — carry **zero** bracketed refs, so *every* cross-reference they make is in
the unverified form.

---

## Disposition rows

Target notation: `oracle/registry/<page>#<anchor>`. Anchors are proposed slugs.

### 6.1-canonical-vocabularies

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 1 | `authority: canon`, `content-hash: 4edb…`, `referenced-by:` list | `6.1-canonical-vocabularies.md:1-41` | delete | — | D1/D6/§4: `authority` tier dies with ch. 11; `content-hash` replaced by git; `referenced-by` is regenerated |
| 2 | "Every other document references these numbers rather than restating them." | `6.1-canonical-vocabularies.md:44` | delete | — | **false as written** — see Contradiction 1. The *intent* survives as the `corpus.json` emission rule (plan §6); the sentence is an unenforced aspiration |
| 3 | Count table, 11 of 14 rows: top-level inputs 3 · state 7-tuple · BO levels 4 · dressing layers · methods 12(+3) · templates 20 · formulas 132(+2) · bundles 11 · residual categories 19 · cert obligations 10 · Layer-0 typeclasses 4 | `6.1-canonical-vocabularies.md:46-58` | delete | — | every one restates a count whose topic another page owns: `crystal-inputs` (`index.md:98`), `unified-state` (`:87`), `born-oppenheimer-levels` (`:43`), `computational-methods` (`:54`), `property-templates` (`:88`), the CSV, `observable-bundles` (`:18`), `residual-definitions` (`:92`), `cert-obligations` (`:89`), `typeclass-alphabet` (`:51`). Under plan §6 the count table is an **emitted** view over `corpus.json`, not a hand-maintained page |
| 4 | Count-table row `State sub-DOF tags` (`orbital, spin, sublattice, valley, strain, gauge, charge, none`) | `6.1-canonical-vocabularies.md:60` | delete | — | owned by `coupling-structure` — `glossary.md:62` names it as the canonical page and `3.3-coupling-structure.md:98` states the enumeration |
| 5 | Count-table row `Crystal symmetry group | first-class (space group × time-reversal × U(1) × SU(2))` | `6.1-canonical-vocabularies.md:59` | move | `oracle/compilation/representation-substrate#crystal-symmetry-group` | it is a one-line restatement of §5 on the same page; travels with row 12 |
| 6 | Count-table row `Theory-context vocabularies | 10 (…)` | `6.1-canonical-vocabularies.md:61` | keep | `oracle/registry/canonical-vocabularies#theory-context` | this is the one count the page genuinely owns (`index.md:95`); merge into §7's own table |
| 7 | §1 — the twelve method names as a closed list | `6.1-canonical-vocabularies.md:63-70` | move | `oracle/registry/computational-methods#the-alphabet` | `computational-methods` is canonical-for *method signatures* (`index.md:54`); the name list and the signatures are one fact split across two pages |
| 8 | §1 — the three registered sub-methods and the `mesh-interpolation` description (Fourier for gauge-free band energies/velocities, Wannier–EPW for gauge-sensitive e-ph matrix elements, mandatory dipole/quadrupole polar corrections, runtime reads the interpolated grid only, C1-clean) | `6.1-canonical-vocabularies.md:72-77` | move | `oracle/registry/computational-methods#sub-methods` | the interpolator's *content* exists only here; `6.4:83-87` carries only the † footnote naming the three. Sole statement of the Fourier/Wannier–EPW split |
| 9 | §1 — "the closed 12-method alphabet is preserved; interpolation is a sub-method, not a new top-level method" | `6.1-canonical-vocabularies.md:76-77` | move | `oracle/registry/computational-methods#sub-methods` | live closure rule, not history |
| 10 | §2 — the three template tables (general 12 · renormalization/configurational/symmetry 3 · domain-interface/defect/thermo 5) with the `Produces` column and per-template notes | `6.1-canonical-vocabularies.md:79-119` | move | `oracle/registry/property-templates#what-each-produces` | `property-templates` is canonical-for *template signatures*; the `Produces` mapping (what observables each template instantiates) exists **only** here and `6.5` explicitly defers to it (`6.5:18-19`). Splitting a template's signature from what it produces is the split that forces the reader to open two pages |
| 11 | §2 — the collapse discipline: "collapse *N observables with the same shape* into *1 template × N argument tuples*" | `6.1-canonical-vocabularies.md:81-83` | move | `oracle/registry/property-templates#discipline` | live design rule; sole statement |
| 12 | §2 — "Bulk-boundary correspondence is **not** a template; handled at the cert layer (obligation-7…)" | `6.1-canonical-vocabularies.md:120-122` | delete | — | verbatim duplicate of `6.5:106-107`, which states it as part of the overlap-resolution block. Keep the `6.5` copy |
| 13 | §3 — the row-band provenance narrative (rows 1–87 research-grounded, 88–102 linear-response/topology, 105–112 slow-tier, 113–118 polarization/2DEG, 120–127 accuracy package, 128–134 gap-audit) | `6.1-canonical-vocabularies.md:128-143` | delete | — | duplicated at greater length and detail by `6.9:42-80`, which names the individual rows. Two copies of one band map; keep the fuller one (row 62 below) |
| 14 | §3 — "Each formula carries a typed signature, a cost tier `T0..T3`, a differentiability tag from `D0 | DN | D1 | D2 | D3 | D4` … and an applicability classifier" | `6.1-canonical-vocabularies.md:143-147` | delete | — | third copy of the tag vocabulary; `named-formulas` owns it (`6.6:41-56`, `glossary.md:41`) and `6.9:104-106` already models the correct behaviour (link, do not repeat) |
| 15 | §3 — the parenthetical warning "(`DN` is not inside `D0..D4` — see [named-formulas])" | `6.1-canonical-vocabularies.md:145-146` | delete | — | **the nomenclature defect, occurrence 1 of 2.** The warning exists only because the vocabulary is misordered. Renaming (plan §4) removes the need for it; until then the warning belongs once, on the owning page. See Open question `dn-not-between-d0-and-d1` |
| 16 | §3 — "See `formula-registry.md` for the narrative index." | `6.1-canonical-vocabularies.md:147` | delete | — | `.md`-filename citation, matched by neither checker; and `formula-registry` dissolves (rows 59-66) |
| 17 | §4 — the `B1..B11` bundle table (ID · Bundle · Primary level) | `6.1-canonical-vocabularies.md:149-166` | move | `oracle/registry/observable-bundles#the-eleven` | **MACHINE-LOAD-BEARING.** `check_data_agreement.py:450-452` harvests the `\| Bn \|` codes from this exact file to validate the CSV `Bundle` column, and hard-errors if the table is not found (`:464-467`). Moving it requires updating `_VOCAB_PAGE`. Merging it into `observable-bundles`, which holds the per-bundle contents, gives one page one job |
| 18 | §4 — the L1-primitive parenthetical (rows 91–94: Z*, ε∞, χ∞, α_M carry `L1`, not a B-tag) | `6.1-canonical-vocabularies.md:167-170` | move | `oracle/registry/observable-bundles#l1-primitives` | live and load-bearing: `traps §70` records that harvesting the table without this note retagged four correct rows. The *schema* source is `6.6:44-47` (harvested at `check_data_agreement.py:456-457`); this is its prose statement |
| 19 | §4 — "(A file tree may additionally group observable *modules* by output data-shape … but the canonical, residual-driving grouping is the eleven physics-domain bundles above.)" | `6.1-canonical-vocabularies.md:170-172` | delete | — | near-verbatim duplicate of `6.7:49-50`. Keep the `6.7` copy |
| 20 | §5 — `CrystalSymmetryGroup = SpaceGroup ⋊ TimeReversal ⋊ U(1)Gauge? ⋊ SU(2)Spin?` and its assembly at Stage 1+2 from `PeriodicityStructure × SiteDecoration` | `6.1-canonical-vocabularies.md:174-184` | move | `oracle/compilation/representation-substrate#crystal-symmetry-group` | sole definition; its *identity* is an `Address[GroupAtlas]` and its derived outputs are substrate fibers, both substrate concerns. Alternative target flagged in Notes |
| 21 | §5 — the group's identity (`Address[GroupAtlas]` over the canonical serialization of finite presentation, factor descriptors, action homomorphisms) and derived-output storage (character tables, irreps, projectors, BZ stalks, Fourier caches as Stage-2/2.5 sidecars) | `6.1-canonical-vocabularies.md:188-193` | move | `oracle/compilation/representation-substrate#crystal-symmetry-group` | same fact-cluster; the citations already point into `representation-substrate §3, §4` |
| 22 | §5 — `IrrepLabel = (group : Address[GroupAtlas-context], local-name : Symbol)`, local-name unique only inside its group context, and its role as Stage-2 output / Stage-2.5 input discriminator | `6.1-canonical-vocabularies.md:194-205` | move | `oracle/compilation/representation-substrate#irrep-label` | sole definition; `4.3-representation-substrate.md:133` already lists `IrrepLabel` as a C1 vocabulary it governs |
| 23 | §6 — the allowed `(StateComponent, SubDofTag)` pairs table (`γ̂`, `A`, `R_I`, `P_I`, `h`, `Π_h`, `Z_I`) | `6.1-canonical-vocabularies.md:207-222` | move | `oracle/laws/coupling-structure#sub-dof-pairs` | `SubDofTag` is owned by `coupling-structure` (`glossary.md:62`), the constructors that enforce the table live there (`3.3:92-98`), and the page itself says so |
| 24 | §6 — "`StatePiece` constructors reject pairs not listed here at registration time" | `6.1-canonical-vocabularies.md:223-224` | move | `oracle/laws/coupling-structure#sub-dof-pairs` | a live registration guard; travels with the table it guards |
| 25 | §7 — the ten theory-context vocabularies table (`XCFunctionalTag` … `SOCScheme`) with member lists and notes | `6.1-canonical-vocabularies.md:240-251` | keep | `oracle/registry/canonical-vocabularies#theory-context` | sole statement; `3.3-coupling-structure.md:596` explicitly defers here ("The vocabularies backing these four fields (ten closed C1 vocabularies) are…"). The *record* stays in `coupling-structure §11`, the *vocabularies* here — a clean split |
| 26 | §7 — the newness argument (no existing vocabulary covers them; the `{SCP, SSCHA, TDEP, GW, BSE-iterated, polaron}` selector is a per-observable dressing method, a different axis from the composition-global theory frame) | `6.1-canonical-vocabularies.md:229-235` | keep | `oracle/registry/canonical-vocabularies#theory-context` | a live non-duplication rationale, not history: it is what stops the two axes being merged again |
| 27 | §7 — each is a `Universe[T]` with `carrier_kind = Closed` and dense `u32` ordinals; adding a member is a versioned `schema_version` bump, not an open-registry append, "because it changes the meaning of every recorded coefficient" | `6.1-canonical-vocabularies.md:235-238` | keep | `oracle/registry/canonical-vocabularies#theory-context` | live versioning rule with its reason attached |
| 28 | §7 — `AtomicSpecies` V1 membership `{C, B, N, Al, Ga, O, H}` and the justification (β-Ga₂O₃ host; O-bearing defects `O_N`, `V_Al–O`, `V_Ga–O_N`, `V_O–H`; slow-tier rows 106, 110 read H and row 109 reads O via `p_O2`) | `6.1-canonical-vocabularies.md:253-260` | keep | `oracle/registry/canonical-vocabularies#atomic-species` | sole statement; the "required by committed content, not future scope" framing is present-tense justification, not history |
| 29 | §7 — "Si and the contact-metal species enter with their waves (schema_version bump)" | `6.1-canonical-vocabularies.md:260-261` | keep | `oracle/registry/canonical-vocabularies#atomic-species` | forward-looking scope statement, not a remnant |
| 30 | §7 — the `HybridAsManyBody` normalization rule: a hybrid is always `XCFunctionalTag.Hybrid` + `ManyBodyLevel.KohnSham`, normalized by `make-theory-context` so the `Address[TheoryContext]` is canonical | `6.1-canonical-vocabularies.md:261-264` | keep | `oracle/registry/canonical-vocabularies#theory-context` | live canonicalization rule; **but** delete the "`* HybridAsManyBody` is reserved/deprecated for V1" framing (§9 scaffolding vocabulary) and the `*` marker in the table, restating it as "not a `ManyBodyLevel` member" |
| 31 | §7 — these vocabularies condition *interpretation and verification*, never *enumeration* of the symmetry-invariant basis; they touch exactly four cert obligations (reference-battery, named-formula-consistency, reference-versioning, surrogate-validity) "and none of the others" | `6.1-canonical-vocabularies.md:266-270` | keep | `oracle/registry/canonical-vocabularies#theory-context` | a live scoping guard with a closed answer; sole statement |

### 6.2-typeclass-alphabet

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 32 | `authority`, `content-hash`, `referenced-by` | `6.2-typeclass-alphabet.md:1-16` | delete | — | D6/§4 |
| 33 | The framing: every observable output is typed by three orthogonal axes plus a discrete bucket, as four typeclasses | `6.2-typeclass-alphabet.md:19-20` | keep | `oracle/registry/typeclass-alphabet#axes` | sole statement; `4.1-physics-graph.md:180` cites it for the `type` field on every node |
| 34 | "Presented here as language-neutral typed pseudocode; the implementation language is undecided — see [open-decisions]" | `6.2-typeclass-alphabet.md:20-22` | move | page `open-questions:` frontmatter of `oracle/registry/typeclass-alphabet` | D7/§5: `10.2-open-decisions` dissolves into per-page frontmatter. `depends-on: open-decisions` (`:8-9`) must be retargeted with it — it is this page's only declared dependency |
| 35 | `Quantity` (Value axis): `unitsOf`, `approxEq(tol)`, `rescale`, `combineTol`; combineTol associative/commutative/monotone with per-instance max-absolute or root-sum-square | `6.2-typeclass-alphabet.md:23-28` | keep | `oracle/registry/typeclass-alphabet#quantity` | sole statement; cited by `3.2-residual-definitions.md:299` and `5.1-cert-obligations.md:131` for the σ error model |
| 36 | `Sampleable` (Shape axis) and its à-la-carte capabilities `Integrable` / `Differentiable` / `Restrictable`, with the `exceptionSet` (phase transitions, band crossings, charge-transition levels) and the `chart` tag | `6.2-typeclass-alphabet.md:29-37` | keep | `oracle/registry/typeclass-alphabet#sampleable` | sole statement; the exception-set list is cited from `10.3-audit-prompt.md:116` |
| 37 | `HasAnalyticStructure` (Constraint axis): witnesses `(Local | Global)`-tagged, `certifyAnalytic` returns witnesses or a typed failure | `6.2-typeclass-alphabet.md:38-42` | keep | `oracle/registry/typeclass-alphabet#analytic-structure` | sole statement |
| 38 | `DiscreteStructure` (Combinatorial axis): `identity`, `compose`, `isoEq`; not `Quantity`, not `Sampleable`; topology-atlas outputs live here | `6.2-typeclass-alphabet.md:43-46` | keep | `oracle/registry/typeclass-alphabet#discrete-structure` | sole statement; `6.3:40` and `5.4-cert-obligations-detail.md:28` both depend on it |
| 39 | The alias definitions — `Response = Sampleable + Integrable + Differentiable + HasAnalyticStructure(KramersKronig)` over a frequency domain, etc. | `6.2-typeclass-alphabet.md:48-51` | keep | `oracle/registry/typeclass-alphabet#aliases` | **live, not history**: `Response`, `FieldOnGrid`, `Tensor` and `Scalar` appear as return types throughout `6.4` and `6.5` signatures (`6.4:49-54`, `6.5:29-36`). Without the aliases those signatures do not type |
| 40 | The framing "The **old names** … **survive only as** aliases" | `6.2-typeclass-alphabet.md:48-49` | delete | — | §9 history marker; restate present-tense as "Four aliases name common parameterizations" |
| 41 | "Cert obligations (§12) map onto these axes mechanically." | `6.2-typeclass-alphabet.md:51` | move | `oracle/registry/typeclass-alphabet#axes`, retargeted to `[cert-obligations-detail]` | the claim is live, the coordinate is rotted: bare `§12` names no page, and the axis-mapping table it promises is `5.4-cert-obligations-detail` (whose title is literally "detail and **axis mapping**"). Dangling-promise class |

### 6.3-topology-atlas

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 42 | `authority`, `content-hash`, `referenced-by` | `6.3-topology-atlas.md:1-12` | delete | — | D6/§4 |
| 43 | `canonical-for: topology atlas` against `id: topology-atlas` | `6.3-topology-atlas.md:6-7` | move | new owned topics on `oracle/registry/topology-atlas` | **near-vacuous ownership**: the topic differs from the id by one hyphen, so the duplicate-topic invariant is effectively inert here even though the plan's count of 18 does not include it. Needs ≥1 genuinely distinct topic (suggest `symmetry-indicator group X_BS`, `compose-time topology classification`) |
| 44 | `depends-on: []` | `6.3-topology-atlas.md:8` | move | declared deps on `oracle/registry/typeclass-alphabet`, `oracle/certification/cert-obligations` | the body depends on both (`:40`) and declares neither — a missing graph edge that survives only because the citations are bare ordinals rather than ids |
| 45 | "The architecture treats a *material* as a composition `(Lattice + SiteDecoration + Laws) → Material` whose properties are derived, never hardcoded" | `6.3-topology-atlas.md:15-17` | move | `oracle/compilation/compose-time-pipeline` (or `program/purpose/architectural-principles`) | this is the composition axiom, not a topology fact; it is restated here as preamble. Flagged as low-confidence in Notes |
| 46 | `TopologyAtlasEntry = (space-group 1..230 (+magnetic), AZ-class, X_BS, EBRs, compatibility)` | `6.3-topology-atlas.md:20-27` | keep | `oracle/registry/topology-atlas#entry` | sole record definition; `glossary.md:36` points here |
| 47 | `X_BS` computed in polynomial time via Smith Normal Form on the integer matrix of orbit-induced representations | `6.3-topology-atlas.md:29-30` | keep | `oracle/registry/topology-atlas#x-bs` | `4.4-computational-overview.md:458` restates the SNF/complexity claim; that copy is another surveyor's, but this is the owning statement |
| 48 | 117 of 230 space groups have non-trivial `X_BS` under time-reversal in the spin-doubled setting; max `|X_BS| = 72` | `6.3-topology-atlas.md:30-32` | keep | `oracle/registry/topology-atlas#x-bs` | sole statement of both numbers anywhere in the corpus |
| 49 | The always-on / opt-in split: cheap parts (`X_BS` class, orbit-representation decomposition, compatibility check, boundary-mode multiplicity via indicator lookup) always-on at compose-time; expensive global integrals (Wilson loops, Chern, Z₂ via Pfaffian) opt-in per observable | `6.3-topology-atlas.md:32-36` | keep | `oracle/registry/topology-atlas#cost-split` | sole statement; consumed by `4.2-compose-time-pipeline.md:82` |
| 50 | "The atlas gives the PINO a navigational signal: `X_BS` tells the model which compositions are topologically equivalent, so gradients in one inform the other. Topology is the map, not a feature." | `6.3-topology-atlas.md:37-39` | keep | `oracle/registry/topology-atlas#pino-signal` | sole statement of *why* the atlas exists; the only operator-facing claim on the page |
| 51 | "Atlas outputs are `DiscreteStructure` instances (§10), and cert obligation-7 is literally a morphism over them." | `6.3-topology-atlas.md:39-40` | move | `oracle/registry/topology-atlas#entry`, retargeted to `[typeclass-alphabet#discrete-structure]` and `[cert-obligations]` | claim is live and confirmed at `5.4-cert-obligations-detail.md:28`; the bare `§10` resolves to nothing. Dangling-promise class |

### 6.4-computational-methods

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 52 | `authority`, `content-hash`, `referenced-by: []` | `6.4-computational-methods.md:1-11` | delete | — | D6/§4. Note the empty `referenced-by`: outside a heading in `4.4-computational-overview.md:389`, **nothing in the corpus cites this page** — the content it holds is reached via `6.1 §1` instead. Merging rows 7–9 here fixes that |
| 53 | "The closed primitive set. Each carries a typed signature and a sub-method dispatch." | `6.4-computational-methods.md:14-15` | keep | `oracle/registry/computational-methods#the-alphabet` | sole statement |
| 54 | The twelve typed signatures with their sub-method dispatch tables (`state-readout` … `symmetry-projection`) | `6.4-computational-methods.md:17-81` | keep | `oracle/registry/computational-methods#signatures` | sole statement; canonical-for *method signatures* (`index.md:54`) |
| 55 | "(ALWAYS invokes a named registry formula — no inline math)" on `algebraic-combination` | `6.4-computational-methods.md:25` | keep | `oracle/registry/computational-methods#signatures` | restates the rule `6.6:36-37` owns, but here it is a signature-site constraint; keep both, cross-link |
| 56 | † footnote: the three registered sub-methods added for UWBG scope; "sub-methods extend a method's dispatch table without changing its typed signature; each requires a sub-method test and a regression-freeze entry" | `6.4-computational-methods.md:83-87` | keep | `oracle/registry/computational-methods#sub-methods` | the extension rule and its two gates are stated only here |

### 6.5-property-templates

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 57 | `authority`, `content-hash`, `referenced-by` | `6.5-property-templates.md:1-14` | delete | — | D6/§4 |
| 58 | "Templates are parameterized method chains; concrete observables are instantiations." | `6.5-property-templates.md:16-17` | keep | `oracle/registry/property-templates#what-a-template-is` | sole statement |
| 59 | "See `canonical-vocabularies §2` for the grouping and the 'produces' summary; signatures follow." | `6.5-property-templates.md:18-19` | delete | — | the split it points across is closed by rows 10–11 (the `Produces` tables land on this page). A pointer to content now on the same page |
| 60 | The twenty template signatures with their inline annotations — fixed-point structure shared across SCPH/SSCHA/GW/BSE/polaron emitting `IterativeResult`; CE-vs-Redlich–Kister distinctness; `SymmetryAdaptedHamiltonianOf` as constructive Stage-1; `SelfConsistentChargeBalanceOf` closing the L3↔non-equilibrium cycle; `HarmonicStiffnessHessianOf` as a specialization; `MassActionEquilibriumOf` as equilibrium-not-driven | `6.5-property-templates.md:21-103` | keep | `oracle/registry/property-templates#signatures` | sole statement; canonical-for *template signatures* (`index.md:88`) |
| 61 | "Overlap resolution": `ClusterExpansion` is a parameterization of `ConfigurationalFreeEnergyOf`, not a separate template · bulk-boundary correspondence is a cert obligation (§8 obligation-7), not a template · `HarmonicStiffnessHessianOf` specializes `SecondDerivativeOf` | `6.5-property-templates.md:105-109` | keep | `oracle/registry/property-templates#overlap-resolution` | live anti-duplication rules for the template vocabulary. Two edits: delete the "(recorded once)" framing (§9 marker), and retarget the bare `§8 obligation-7` to `[cert-obligations]` — it names no page and conflicts with three other bare ordinals for the same target (Contradiction 4) |

### 6.6-named-formulas

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 62 | `authority`, `content-hash`, `referenced-by` | `6.6-named-formulas.md:1-28` | delete | — | D6/§4 |
| 63 | The CSV is canonical and machine-readable; 132 substantive + 2 architectural markers (force = −∇energy; equivariance) not residualized; `formula-registry.md` is the narrative index | `6.6-named-formulas.md:31-34` | keep | `oracle/registry/named-formulas#the-registry` | keep the CSV-is-canonical pointer and the two-marker rule; **delete the `formula-registry.md` pointer** (that page dissolves, rows 68-76) and let the counts come from the emitted index rather than prose |
| 64 | "Every algebraic combination invokes a named formula with typed inputs and an explicit output type; no inline math." | `6.6-named-formulas.md:35-37` | keep | `oracle/registry/named-formulas#no-inline-math` | the rule the whole registry exists to enforce; sole normative statement |
| 65 | `record FormulaRecord { name, signature, bundle, cost-tier, diff-tag, path, source, depends-on, applicability, adjoint-validated }` | `6.6-named-formulas.md:38-57` | keep | `oracle/registry/named-formulas#formula-record` | **MACHINE-LOAD-BEARING.** `check_data_agreement.py:456-457` harvests the extra `L1` bundle value from the phrase "`L1` primitive tag" in this file. Moving or rewording the `bundle` comment breaks the Bundle check silently (`traps §70`) |
| 66 | **Cost tiers** — `T0` closed-form (≤10 µs) · `T1` small LA / 1D quadrature (≤10 ms) · `T2` BZ/mesh integral (≤10 s) · `T3` self-consistent loop or PDE (≤10 min) | `6.6-named-formulas.md:59-61` | keep | `oracle/registry/named-formulas#cost-tiers` | **sole owner** per `glossary.md:41`. Four other copies exist and none is guarded: `6.9:100-102` (verbatim, → delete row 73), `4.4-computational-overview.md:435` (+distribution counts), `7.2-residual-machinery.md:296-297` (partial, with sampling cadence — a different fact), `informed-operator/design/residual-loss-methodology.md:328`. Probe B proves drift between any two is undetected |
| 67 | The differentiability tags' purpose statement — "The tag answers exactly one question: *how does a consumer obtain a gradient through this row?*" | `6.6-named-formulas.md:63-65` | keep | `oracle/registry/named-formulas#diff-tags` | the invariant that makes the vocabulary decidable; sole statement |
| 68 | `D0` — pure read, adjoint is the identity, registers without a synthesized adjoint; exactly one row qualifies (`reference-phase-energy-cache`, keyed on a phase id alone); a row taking continuous arguments is not a pure read | `6.6-named-formulas.md:66-72` | keep | `oracle/registry/named-formulas#diff-tags` | sole definition. Verified against the CSV: `Diff=D0` occurs exactly once |
| 69 | `DN` — no useful derivative; integer/categorical/boolean/set-valued; not relaxable in place; "**the strongest claim in this vocabulary**… so it is the tag most likely to be wrong"; the two pre-assignment checks | `6.6-named-formulas.md:73-78` | keep | `oracle/registry/named-formulas#diff-tags` | sole definition plus a live assignment discipline |
| 70 | `D1` smooth, no registration gate · `D2` adjoint required, vJp-vs-JvP agreement within `τ_adj`, the gate checks the *synthesized* adjoint not a hand-written backward | `6.6-named-formulas.md:79-84` | keep | `oracle/registry/named-formulas#diff-tags` | sole definition |
| 71 | `D3` — implicit-function adjoint; gradient is one linear solve against the transposed fixed-point Jacobian, independent of forward iteration count; **the iteration-count independence is the test** (if adjoint cost scales with forward steps the row is `D2`) | `6.6-named-formulas.md:85-90` | keep | `oracle/registry/named-formulas#diff-tags` | sole statement of the discriminating test |
| 72 | `D3` is a **refinement** of `D2`, not an alternative: every `D3` row runs the `D2` gate **and** a fixed-point-Jacobian conditioning check refusing registration below `τ_cond`; with the rows it bites named (`fermi-level-charge-neutral`, `self-consistent-charge-balance`, `SCPH-self-consistent-phonons`) and why (∂F/∂E_F flattest in a wide-gap intrinsic semiconductor; soft modes) | `6.6-named-formulas.md:92-104` | keep | `oracle/registry/named-formulas#diff-tags` | **This is a closed gap's resolution stated as present-tense fact — exactly brief exception 1.** `10.2-open-decisions.md:133-135` still narrates it as "closed on 2026-07-21"; that narration deletes, this survives. Restated in summary at `6.9:113-116` → delete that copy |
| 73 | `D4` — relaxed; genuinely non-smooth (argmin, hull, sort, discrete metric); ships a declared smooth relaxation whose bias is model-form error entering `combineTol`, approved with an obligation-9 validity domain; **the relaxation is named in the row's `source` cell** and a `D4` row without one fails the registry-build gate | `6.6-named-formulas.md:105-109` | keep | `oracle/registry/named-formulas#diff-tags` | sole statement; the `source`-cell rule is machine-checked (`check_data_agreement.py` class (g)) |
| 74 | **Mixed-output rule** — the diff-tag describes the continuous component; a discrete label never drags a row to `DN`; where the continuous→discrete map is itself load-bearing (threshold, min-over-set) that non-smoothness makes the row `D4` and the relaxation covers exactly that step | `6.6-named-formulas.md:111-121` | keep | `oracle/registry/named-formulas#mixed-outputs` | live tagging rule; sole statement |
| 75 | The three mixed-output rows named (`radius-ratio-coordination-class`, `elastic-stability-criteria`, `structure-uniqueness-CSP`) with their output shapes | `6.6-named-formulas.md:112-114` | keep | `oracle/registry/named-formulas#mixed-outputs` | verified present in the CSV |
| 76 | "…which is how these three rows **previously read** `D1`, `D1` and `DX`" | `6.6-named-formulas.md:117-119` | delete | — | §9 history marker. Log-worthy row 3 |
| 77 | "**`DN` splits the old `D0`**, which conflated…" — the retag narrative: eleven smooth analytic rows sat at `D0` and registered with no adjoint since `build-verification` exempts `D0`; among them the alloy-lattice interpolation `product` promises is directly optimizable; those eleven **are now** `D1` | `6.6-named-formulas.md:123-130` | delete | — | §9 history. **Two live facts must be extracted before it goes:** (i) `build-verification` exempts `D0` from adjoint synthesis — a live rule → move to `oracle/registry/named-formulas#diff-tags`; (ii) the alloy-lattice-interpolation row is on the differentiable path → already implied by its `D1` tag in the CSV. Log-worthy row 2 |
| 78 | The `chemical-potential-ref-table` story: survived the first pass because "ref-cache lookup" reads like a pure read; it takes `T` and `P`, so `D0` zeroed `∂μ_i/∂T` and left row 69's Maxwell cross-derivative residual vacuously satisfied | `6.6-named-formulas.md:130-135` | keep | `oracle/registry/named-formulas#diff-tags` | **the story is history but the test is live**: "an implementation detail (a cache) mistaken for a mathematical one (an identity adjoint)" is the operative `D0`-misuse rule that row 68 forward-references ("see the note on `D0` misuse below"). Rewrite present-tense as a rule; the "survived the first pass" framing deletes |
| 79 | "The tag is spelled `DN`, not `DX`" — `DX` collides with the DX center in AlGaN/AlN; diff tags are written in backticks in prose; the wurtzite deformation potentials `D1`–`D5` in `[accuracy-ledger]` are the other live collision | `6.6-named-formulas.md:137-143` | keep | `oracle/registry/named-formulas#diff-tags` **and** `practice/traps` | a live search hazard and a live typographic convention, not a remnant (brief exception 2). Both collisions still exist in the corpus today |
| 80 | "The corrected physics is canonical in the registry **and in §6 below**: optical absorption uses `(2ω/c)·Im(√ε)`; the operator-spectrum-area sum rule carries the `2/π` prefactor; the acoustic sum rule sums over all lattice translations (`Σ_J Σ_R Φ_{IαJβ}(R) = 0`); the magnetic relaxation term is `S × (S × H_eff)`; the harmonic transition-rate normalization consumes products-over-modes, not spectra" | `6.6-named-formulas.md:145-150` | keep | `oracle/registry/named-formulas#corrected-forms` | the five forms are live canonical statements. **But "§6 below" does not exist — this page has no §6 and no numbered sections at all.** Dangling promise; delete the pointer. Also delete "The corrected physics" framing → state the five forms directly |
| 81 | **`path` — the anchor class.** `cheap` (117 rows) vs `faithful` (15); **not** a runtime path selector; what a row's value is *anchored against* — own closed form vs a reference-grade DFT/DFPT/NEGF/MC evaluation or measured battery entry | `6.6-named-formulas.md:152-160` | keep | `oracle/registry/named-formulas#anchor-class` | sole owner. Counts verified against the CSV: `Path` = 117 cheap / 15 faithful / 2 `—` |
| 82 | A **consistency pair** is a `cheap` row and a `faithful` row computing the same observable with no agreement theorem, only a bounded model gap; QHA+Slack/Callaway κ vs iterative-LBTE κ is the canonical example; treating it as an equivalence pair scores the legitimate gap as a bug | `6.6-named-formulas.md:161-167` | keep | `oracle/registry/named-formulas#anchor-class` | the definition tying `path` to obligation-6. `7.3-cross-cutting-rules.md:51-54` defines consistency pairs but **never in terms of `cheap`/`faithful`** — see Notes |
| 83 | "The `Cheap vs faithful` column of `[accuracy-ledger]` is the per-observable statement of the same distinction." | `6.6-named-formulas.md:166-167` | keep | `oracle/registry/named-formulas#anchor-class` | citation verified to land on the claim: `9.1-accuracy-ledger.md:55` has that exact column header |
| 84 | "The field was **briefly declared retired**… It did — but the anchor-class meaning is what the corpus actually uses the column for, in four live places… Retiring a field that four pages depend on is how a load-bearing distinction becomes folklore." | `6.6-named-formulas.md:169-173` | delete | — | §9 history marker (`retired`). Log-worthy row 4. The generalizable lesson ("a field four pages depend on") belongs in `practice/traps`, not on this page. The "four live places" count is unverifiable — see Notes |
| 85 | **Applicability-decidability invariant** — every `applicability` predicate is first-order decidable in `(Crystal, Environment)`: finite case analysis on typeclass tags, not numeric thresholds or solver outputs; non-decidable classifiers forbidden at registration | `6.6-named-formulas.md:175-180` | keep | `oracle/registry/named-formulas#applicability-decidability` | sole statement of the invariant; the gate it names is `build-sequence` Phase 7 (`8.6:41`, verified) |

### 6.7-observable-bundles

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 86 | `authority`, `content-hash`, `referenced-by: []` | `6.7-observable-bundles.md:1-11` | delete | — | D6/§4. **`referenced-by` is empty and it is accurate: no page anywhere in the corpus cites `observable-bundles`.** A true orphan, reachable only through `6.1 §4`. Row 17 merges the table here and gives it inbound edges |
| 87 | "The eleven physics-domain bundles `B1..B11` are listed in `canonical-vocabularies §4`. Representative contents:" | `6.7-observable-bundles.md:14-15` | delete | — | the pointer closes once row 17 lands the table on this page |
| 88 | The eleven bundles' representative contents (B1 electronic-structure … B11 degradation), including the registered-name aliases (`barrier-from-workfunction-affinity`, `radius-ratio-coordination-class` a.k.a. Pauling radius ratio, `elastic-stability-criteria` a.k.a. Born stability, `plastic-strain-fatigue-life` a.k.a. Coffin–Manson) and the row-band pointers (113–115/117–118 polarization-2DEG; 128–131 gate-dielectric; 105–112 slow-tier; 132 XRD) | `6.7-observable-bundles.md:17-47` | keep | `oracle/registry/observable-bundles#contents` | sole statement; canonical-for *bundle signatures* (`index.md:18`). All named rows verified present in the CSV. The behavior-name↔person-name aliases exist nowhere else and are the only defense against the person-attribution names re-entering |
| 89 | "(A file tree may additionally group observable *modules* by output data-shape; the residual-driving grouping is the eleven physics-domain bundles.)" | `6.7-observable-bundles.md:49-50` | keep | `oracle/registry/observable-bundles#contents` | keep this copy; delete the `6.1:170-172` duplicate (row 19) |

### 6.8-typed-compositions

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 90 | `authority`, `content-hash`, `referenced-by` | `6.8-typed-compositions.md:1-12,32-37` | delete | — | D6/§4 |
| 91 | `unregistered-formulas:` frontmatter — the eighteen declared names | `6.8-typed-compositions.md:13-31` | keep | `oracle/registry/typed-compositions` frontmatter | **machine-read and probe-verified (probe C).** `check_data_agreement.py:110-147` fails an undeclared `formula =` argument and `:242` fails a stale declaration. This is the corpus's one working example of a gap declared in a way a checker can hold. Preserve the key under the new fixed frontmatter schema (plan §4 specifies a *fixed key set* — this key must be in it, or the mechanism dies at cutover) |
| 92 | "Every property in `properties.md` written as a typed composition — the validation that the closed vocabulary covers the target scope. Each invokes methods (§2), templates (§3), and named formulas (§4) — **except for the declared gap below**." | `6.8-typed-compositions.md:39-43` | move | `oracle/registry/typed-compositions#purpose` | the purpose statement is live; the three bare ordinals `(§2)(§3)(§4)` are pre-book coordinates naming no page and must become `[computational-methods]`, `[property-templates]`, `[named-formulas]`. The `properties.md` filename citation becomes `[properties]` — or dissolves if rows 106-110 merge the two pages |
| 93 | Structural compositions (LatticeParameters, BondLengths, CrystalStructure, Defects energy + characterization, Surfaces region + energy) | `6.8-typed-compositions.md:45-58` | keep | `oracle/registry/typed-compositions#structural` | sole statement |
| 94 | Electronic compositions (BandStructure, DOS, BandGap, ChargeDensity) | `6.8-typed-compositions.md:60-68` | keep | `oracle/registry/typed-compositions#electronic` | sole statement |
| 95 | Optical compositions (DielectricFunction, Absorption, RefractiveIndex, Photoluminescence) | `6.8-typed-compositions.md:70-78` | keep | `oracle/registry/typed-compositions#optical` | sole statement |
| 96 | Mechanical compositions (ElasticConstants, BulkModulus, StressStrain, Hardness) | `6.8-typed-compositions.md:80-92` | keep | `oracle/registry/typed-compositions#mechanical` | sole statement |
| 97 | The Voigt/Reuss/Hill averaging note — "an open pick; see the C_ij weak-link note in `[accuracy-ledger]`" | `6.8-typed-compositions.md:87-88` | move | `open-questions:` frontmatter of `oracle/registry/typed-compositions` | D7/§5: an open item stated inline. Citation verified to resolve to a page; whether it lands on a C_ij weak-link note is `accuracy` surveyor's call |
| 98 | Thermal compositions (PhononDispersion, HeatCapacity, ThermalConductivity, ThermalExpansion) | `6.8-typed-compositions.md:94-105` | keep | `oracle/registry/typed-compositions#thermal` | sole statement |
| 99 | Magnetic compositions (MagneticMoments, SpinDensity, ExchangeInteractions) | `6.8-typed-compositions.md:107-114` | keep | `oracle/registry/typed-compositions#magnetic` | sole statement. Flag: `kernel = exchange-coupling-formula` names nothing in the registry and is not in `unregistered-formulas` — see Open question `undeclared-non-formula-slots` |
| 100 | Transport compositions (ConductivityViaBTE, ConductivityViaKubo, Conductivity as a both-evaluated pair, CarrierMobility, IonicDiffusion, MigrationBarrier) | `6.8-typed-compositions.md:116-142` | keep | `oracle/registry/typed-compositions#transport` | sole statement; the `Conductivity` pair is the worked instance of obligation-6 method-equivalence |
| 101 | "(The harmonic transition-rate normalization consumes the **product** of normal-mode frequencies via the `product-of-modes` extractor, not the spectra.)" | `6.8-typed-compositions.md:144-145` | keep | `oracle/registry/typed-compositions#transport` | live correctness note; restates one of the five corrected forms in row 80 — cross-link rather than duplicate |
| 102 | Thermodynamic compositions (TotalEnergy, FormationEnergy, PhaseStability, FreeEnergy) | `6.8-typed-compositions.md:147-159` | keep | `oracle/registry/typed-compositions#thermodynamic` | sole statement |
| 103 | Chemical/surface compositions (AdsorptionEnergy, ReactionPathway, CatalyticActivity, SurfaceEnergy) | `6.8-typed-compositions.md:161-177` | keep | `oracle/registry/typed-compositions#chemical-surface` | sole statement. Flag: `ν₀ = harmonic-rate-prefactor` at `:168` names the same quantity the same page calls `harmonic-transition-rate-normalization` at `:135` — Contradiction 5 |
| 104 | "All target observables resolve to typed compositions over the closed vocabulary, **except the declared gap below**." | `6.8-typed-compositions.md:179-180` | keep | `oracle/registry/typed-compositions#purpose` | the honest form of the closed-vocabulary claim |
| 105 | **Declared gap** — eighteen invoked names are not registry rows, so the closed-vocabulary claim does not hold in full; the frontmatter is machine-read; a *declared* gap is reported separately from an *undeclared* one | `6.8-typed-compositions.md:182-188` | keep | `oracle/registry/typed-compositions#declared-gap` | verified by probe C. This block is the reason the page is trustworthy |
| 106 | The refusal rationale — "a registry row must be defensible against a literature citation, and registering these on thin provenance would put unsourced rows into the artifact whose entire discipline is that unsourced values are refused (`[traps]` §19)" | `6.8-typed-compositions.md:190-194` | keep | `oracle/registry/typed-compositions#declared-gap` | live policy; citation verified — `10.4-traps.md:162` is §19 "Unprovenanced coefficient ⇒ refuse the composition" |
| 107 | "The gap is tracked in `[open-decisions]`." | `6.8-typed-compositions.md:193-194` | move | `open-questions:` frontmatter of `oracle/registry/typed-compositions` | D7/§5. `10.2-open-decisions.md:137-154` restates this entire block; that copy deletes and this page becomes the single home. **This is the register/page drift class the plan's defect 6 describes, one page away from realizing** |
| 108 | Tranche 1 — **definition already fixed** (9 names): `refractive-index-from-dielectric`, `absorption-from-dielectric`, `mobility-from-conductivity`, `linear-elasticity-stress-strain` (Hooke), `slab-arithmetic`, `arrhenius`, `adsorption-energy-difference`, `helmholtz-free-energy-decomposition`, `QHA-expansion` (whose tensor form `[traps]` §9 pins, including the compliance-not-stiffness trap) | `6.8-typed-compositions.md:198-206` | keep | `oracle/registry/typed-compositions#declared-gap` | sole statement of the split; `10.4-traps.md:101` is §9 and does pin the compliance form |
| 109 | Tranche 2 — **needs sourcing** (9 names): the four hardness models, `harmonic-transition-rate-normalization`, `jump-diffusivity` (geometric prefactor convention is the trap), `htst-rate`, `turnover-frequency`, `formation-energy-from-references` | `6.8-typed-compositions.md:208-212` | keep | `oracle/registry/typed-compositions#declared-gap` | sole statement; this is the research-shaped half of the gap |
| 110 | "Four invocations above **used to carry** inline mathematics… They **now** carry the declared names instead" | `6.8-typed-compositions.md:214-217` | delete | — | §9 history marker. Log-worthy row 6 |
| 111 | The four declared-name→expression table: `absorption-from-dielectric` = `(2ω/c)·Im(√ε)` · `refractive-index-from-dielectric` = `Re(√ε)` · `mobility-from-conductivity` = `σ/(n·e)` · `helmholtz-free-energy-decomposition` = `E_BO + F_vib + F_el` | `6.8-typed-compositions.md:219-226` | keep | `oracle/registry/typed-compositions#declared-gap` | **load-bearing**: these four expressions are what makes registering those rows transcription rather than research. Deleting them converts four transcription tasks into four research tasks |

### 6.9-formula-registry

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 112 | `authority`, `content-hash`, `referenced-by` | `6.9-formula-registry.md:1-21` | delete | — | D6/§4 |
| 113 | `canonical-for: [formula-registry]` — identical to `id: formula-registry` | `6.9-formula-registry.md:6-7` | delete | — | **vacuous ownership** (plan defect 4, one of the named 18). Probe D confirms nothing fires. The page owns no topic that another page could collide with, so it sits outside the anti-duplication machinery entirely — which is how it accumulated the duplication below |
| 114 | `[`../physics/library/formulas/registry-manifest.csv`](../physics/library/formulas/registry-manifest.csv)` | `6.9-formula-registry.md:26` | delete | — | **the link is broken.** From `journal/pages/06-vocabularies-and-registry/`, `../physics/...` resolves to `journal/pages/physics/...`, which does not exist (verified). Neither checker looks at relative markdown links |
| 115 | "What the registry is" — every algebraic combination invokes a named formula, no inline math, no string-encoded expressions; each formula is a typing rule for a `FormulaApply` node in the `PhysicsGraph`; the registry bounds Stage-1 graph construction; each is independently citable and verifiable; new formulas enter only through a controlled cert-validated process; "a contract, not a convenience" | `6.9-formula-registry.md:29-38` | delete | — | every clause is stated elsewhere: no-inline-math at `6.6:35-37`; `FormulaApply` typing rule at `4.1-physics-graph.md:174`; the Stage-1 bound at `4.1:174-176`; the controlled-entry gate at `8.6-build-sequence.md:41`. Nothing here is unique |
| 116 | "Counts" — the full row-band → physics-package map, naming the individual rows in bands 120–127 and 128–134 (`ahc-gap-renormalization`, `kappa-4phonon-high-t-correction`, `iterative-lbte-kappa`, `breakdown-field-temperature-slope`, `tp-aware-hull`, `detailed-balance-cycle-residual`, `rotational-sum-rule`, `alloy-disorder-scattering`, `pyroelectric-coefficient`, `poole-frenkel-current`, `tddb-thermochemical-e-model`, `dielectric-crystallization-jmak`, `xrd-structure-factor`, `raman-activity`, `radiative-recombination-rate`) with the gating predicates | `6.9-formula-registry.md:42-61` | move | `oracle/registry/named-formulas#row-bands` | the **only** full band map; `6.1:128-143` is a shorter copy of the same fact (row 13 deletes it). All 15 named rows verified present in the CSV. Keeping it on `named-formulas` puts the band map next to the record schema it describes |
| 117 | The `is-noncentrosymmetric` gating note — "the piezo-class predicate of the applicability-classifiers two-predicate split, not the Fröhlich `is-polar-material` gate" | `6.9-formula-registry.md:45-47` | move | `oracle/registry/named-formulas#row-bands` | a live disambiguation between two predicates that look interchangeable; sole statement in this chapter |
| 118 | "2 architectural markers (rows 103–104)… force = −∇energy (an autodiff identity) and equivariance (a structural constraint). They appear in the manifest so the decision is recorded, not so they generate loss." | `6.9-formula-registry.md:62-66` | move | `oracle/registry/named-formulas#the-registry` | the *reason* the two markers are in the CSV exists only here; `6.6:32-34` names them without saying why they are recorded |
| 119 | "Rows 1–87 grounded in `physics/research/`" and "Rows 88–102 are the linear-response and topology-atlas extensions" with their contents enumerated | `6.9-formula-registry.md:67-80` | move | `oracle/registry/named-formulas#row-bands` | same band map; travels with row 116. **Note the path `physics/research/` — `10.3-audit-prompt.md` was flagged in the plan for citing this directory for physics that moved. Verify the directory still exists before re-stating the provenance** |
| 120 | "Columns" — the eight-column CSV legend (`#`, `Name`, `Signature`, `Bundle`, `Tier`, `Diff`, `Path`, `Source`, `Depends on`) with per-column meanings | `6.9-formula-registry.md:82-96` | delete | — | restates the CSV's own header row plus semantics each of which is owned elsewhere: `Bundle`→`6.1 §4`/`6.6`; `Tier`→`6.6`; `Diff`→`6.6` (this row says so itself); `Path`→`6.6` (says so itself). Under plan §6 the column legend belongs to `data/` and the emitted `corpus.json`, not to a prose page |
| 121 | The `Source` column note — "'extension' / 'topology atlas' — the latter for rows 88–102 **and 128–134** (the 2026-07 gap-audit rows, which the Counts section below has always described correctly; only this legend lagged)" | `6.9-formula-registry.md:95` | delete | — | the surviving *fact* (rows 128–134 carry `Source = topology atlas`) belongs in the CSV, which already carries it. "the Counts section below has always described correctly; only this legend lagged" is §9 history about a fixed drift. Log-worthy row 7 |
| 122 | "Tag legend" **cost tiers** — `T0` ≤10 µs · `T1` ≤10 ms · `T2` ≤10 s · `T3` ≤10 min | `6.9-formula-registry.md:100-102` | delete | — | **verbatim second copy of `6.6:59-61`, unguarded — probe B proves drift between them is invisible to both checkers.** The page is duplicating in one paragraph exactly what it forbids in the next |
| 123 | "Tag legend" **differentiability** — "see `[named-formulas]`, which is canonical… Restating it here is what let five incompatible legends coexist; this page now links rather than repeats." | `6.9-formula-registry.md:104-106` | delete | — | a pure pointer plus §9 history about five dead legends. The *behaviour* it models is right and should become the corpus-wide default; the *sentence* is scaffolding. Log-worthy row 5 |
| 124 | "How a formula becomes a residual" — the factory reads each record and produces a `ResidualGenerator`; cost tier sets sampling cadence; diff tag sets gradient-bearing and triggers the `D2`/`D3` registration gate; applicability masks per training sample; each generator unfolds along `axes` to emit a content-addressed `Map<ResidualKey, Scalar>`; weighting and aggregation belong to `/informed-operator` | `6.9-formula-registry.md:108-119` | delete | — | a summary of `7.2-residual-machinery.md:40-50, 55-95` and `:296-297`, which own the factory, the record and the cadence table. The `D3`-refines-`D2` parenthetical duplicates row 72 |

### 6.10-properties

| # | Fact or block | Current location | Disposition | Target | Evidence |
|---|---|---|---|---|---|
| 125 | `authority`, `content-hash`, `referenced-by` | `6.10-properties.md:1-14` | delete | — | D6/§4. `referenced-by` names only `deriv-high-field` — **a chapter-11 page.** When ch. 11 dies this page's in-degree is zero |
| 126 | `canonical-for: [properties]` — identical to `id: properties` | `6.10-properties.md:6-7` | delete | — | **vacuous ownership** (plan defect 4, one of the named 18); probe D confirms it is unenforceable |
| 127 | "the nine categories define the **target scope**, not the implemented scope: the buckets any quantity a user might ask for should fall into" | `6.10-properties.md:17-21` | keep | `oracle/registry/properties#scope-vs-inventory` | the page's actual job, and it is not stated anywhere else |
| 128 | "**They are not a claim that the registry can compute all nine today.** … Read this page as scope, and the registry as inventory; **where they disagree, the registry wins.**" | `6.10-properties.md:22-29` | keep | `oracle/registry/properties#scope-vs-inventory` | a live precedence rule between two artifacts — exactly the kind of rule the restructure exists to make findable. Sole statement |
| 129 | Category 6 (Magnetic) has no dedicated bundle "because `γ̂` is mean-field and the UWBG scope did not force one" | `6.10-properties.md:25-27` | keep | `oracle/registry/properties#scope-vs-inventory` | a stated, reasoned coverage hole — the clearest instance of the rule in row 128. Candidate for `open-questions` instead; flagged in Notes |
| 130 | "Property → bundle map" preamble — the authoritative per-formula bundle assignment is the CSV `Bundle` column; the table is category→bundle overview only and does not re-define bundle semantics | `6.10-properties.md:31-37` | keep | `oracle/registry/properties#bundle-map` | an explicit, correct non-duplication disclaimer. Rare in this chapter and worth preserving as a pattern |
| 131 | The nine-row category→bundle table | `6.10-properties.md:39-49` | keep | `oracle/registry/properties#bundle-map` | sole statement of the category→bundle projection |
| 132 | "(The earlier `B1..B11` labels in this file were a stale pre-canon scheme — e.g. `B11`='topology atlas' — superseded by the `canonical-vocabularies §4` canon, where `B11`=degradation.)" | `6.10-properties.md:51-53` | delete | — | §9 history marker (`stale`, `pre-canon`, `superseded`). Log-worthy row 8 |
| 133 | The nine category sections — one paragraph of physical motivation each, plus the item list (Structural 5 · Electronic 4 · Optical 4 · Mechanical 4 · Thermal 4 · Magnetic 3 · Transport 4 · Thermodynamic 4 · Chemical/surface 4) | `6.10-properties.md:55-164` | keep | `oracle/registry/properties#categories` | **load-bearing input to `typed-compositions`**: `6.8:39` claims to write "every property in `properties.md`" as a composition, so this list is the checklist that claim is against. The motivation paragraphs exist nowhere else. See rows 141-143 for the merge proposal |
| 134 | The bare ordinal in "(defined in [canonical-vocabularies] §4\`)" — note the stray backtick | `6.10-properties.md:34` | move | `oracle/registry/properties#bundle-map` with an anchored citation | malformed citation: mixed bracketed-id and bare-ordinal forms plus an unbalanced backtick. Renders wrong today |

---

## Open questions

| id | question | owning page | why it is open |
|---|---|---|---|
| `unregistered-composition-formulas` | Eighteen formula names invoked by `typed-compositions` are not registry rows, so its closed-vocabulary claim does not hold in full. Nine are definitional (transcription + tag assignment); nine need literature (four hardness models, `harmonic-transition-rate-normalization`, `jump-diffusivity`, `htst-rate`, `turnover-frequency`, `formation-energy-from-references`). Which register, and in what order? | `oracle/registry/typed-compositions#declared-gap` | Declared and machine-enforced but unresolved. Currently double-homed: the page's frontmatter *and* `10.2-open-decisions.md:137-154` narrate it, and `10.2` dissolves. Verified: all 18 absent from the CSV; all 18 invoked at `formula =` sites in the page body |
| `undeclared-non-formula-slots` | Two names are invoked in non-`formula =` slots and are neither registry rows nor declared: `exchange-coupling-formula` (`kernel =`, `6.8:113`) and `harmonic-rate-prefactor` (`ν₀ =`, `6.8:168`). Are they in scope for the declared gap, or a separate vocabulary (`ResponseKernel` members) that no page owns? | `oracle/registry/typed-compositions#declared-gap` | The `unregistered-formulas` mechanism only sweeps `formula =` arguments (`check_data_agreement.py:99-107`), so the closed-vocabulary claim has a second hole the declared gap does not cover. `harmonic-rate-prefactor` also names the same ν₀ the same page computes via `harmonic-transition-rate-normalization` |
| `dn-not-between-d0-and-d1` | The `D0 | DN | D1 | D2 | D3 | D4` vocabulary is misordered — `DN` is not between `D0` and `D1`, and canon carries a written warning about it in two places. Propose a replacement ordering. **Propose only; do not rename** (plan §4). | `oracle/registry/named-formulas#diff-tags` | The vocabulary is stated in **11 places** and explained in exactly one. Full inventory below |
| `impl-language-undecided` | The typeclass alphabet is presented as language-neutral pseudocode because the implementation language is undecided. | `oracle/registry/typeclass-alphabet` | Inherited from `10.2-open-decisions`, which dissolves; `6.2` is the only chapter-6 page that depends on it (`6.2:8-9`) |
| `cij-averaging-scheme` | Which averaging scheme (Voigt / Reuss / Hill) `BulkModulus = AlgebraicOf({ElasticConstants}, formula = bulk-modulus)` uses is an open pick. | `oracle/registry/typed-compositions#mechanical` | Stated inline as "an open pick" at `6.8:87-88` and nowhere registered as an open item |
| `argument-type-alphabet-homeless` | The argument types used throughout the method and template signatures — `Extractor`, `Aggregator`, `ResponseKernel`, `PathMethod`, `Optimizer`, `EigenSolver`, `ConvexSolver`, `KineticMethod`, `Sampler`, `ProjKind`, `Classifier`, `ComparisonMetric`, `TensorNorm`, `HessianMethod`, `NonlinearSolver`, `BiSlabSolver`, `ChargeNeutralitySolver`, `ConvergenceCriterion` — are **defined by no page and carry no glossary entry**. Which page owns them? | unassigned — candidate `oracle/registry/computational-methods#argument-types` | Homeless-fact class. Swept `journal/pages/` + `glossary.md`: zero glossary entries, and each appears in only 1–3 files, all of them *uses*. The 12 method signatures and 20 template signatures cannot be typed without them |
| `environment-record-homeless` | `Environment` appears in seven signatures in this chapter alone (`6.5:51,79,84,96,100`; `6.6:54,176`) and 23 files corpus-wide; **no page's `canonical-for` claims it** and it has no glossary entry. | unassigned — the brief names it already | Confirms the brief's second homeless fact from inside this chapter. `Crystal`, its partner in `applicability : (Crystal, Environment) → Bool`, does have a glossary entry; `Environment` does not |
| `does-formula-registry-survive` | `formula-registry` (6.9) and `properties` (6.10) both hold vacuous `canonical-for` and both lose almost all inbound edges when ch. 11 is deleted. Do they survive as pages, or dissolve into `named-formulas` + `typed-compositions` + the emitted index? | `oracle/registry/` (structural) | `6.9`'s inbound edges are `deriv-csp`, `deriv-generator-catalog`, `deriv-high-field` (all ch. 11) and `properties`. `6.10`'s sole inbound edge is `deriv-high-field` (ch. 11). Post-deletion the pair is a disconnected island. My rows dissolve 6.9 and merge 6.10; **Javier should confirm** |
| `cost-tier-legend-unguarded` | The `T0–T3` legend is written out in full in at least four places and no checker holds any two together (probe B). Where does it live, and how is the single copy enforced? | `oracle/registry/named-formulas#cost-tiers` | `check_data_agreement.py:460-462` hardcodes `{'T0','T1','T2','T3'}` and `{'D0'…'DN'}` as a *fifth* copy, directly under a comment saying vocabularies are "HARVESTED, never restated here" (`:436-437`) |

### Every place the `D0 | DN | D1 | D2 | D3 | D4` vocabulary is stated or explained

Requested inventory. **Explained once. Stated eleven times.**

| Location | Form |
|---|---|
| `journal/pages/06-vocabularies-and-registry/6.6-named-formulas.md:63-121` | **the sole explanation** — per-tag definitions, the mixed-output rule, the `D0`-misuse test, the `DN`-vs-`DX` spelling rule |
| `journal/pages/06-vocabularies-and-registry/6.6-named-formulas.md:49` | `record FormulaRecord` field, bare list |
| `journal/pages/06-vocabularies-and-registry/6.1-canonical-vocabularies.md:145` | bare list **+ the "`DN` is not inside `D0..D4`" warning** |
| `journal/pages/06-vocabularies-and-registry/6.9-formula-registry.md:105` | bare list, with an explicit link-don't-repeat note |
| `journal/pages/07-consumers-and-seams/7.2-residual-machinery.md:70` | `record ResidualGenerator` field, bare list, annotated "named-formulas is canonical" |
| `journal/pages/10-process-and-governance/10.3-audit-prompt.md:116` | bare list **+ the "`DN` is not inside `D0–D4`" warning** (occurrence 2 of 2) |
| `journal/pages/11-appendix-derivations/11.6-deriv-csp.md:27` | quoted inside a **collision note** — that survey's own `D+`/`D0`/`D-` legend, where `D0` means the opposite |
| `journal/pages/11-appendix-derivations/11.8-deriv-generator-catalog.md:27` | quoted inside the **retired-legend banner** |
| `journal/live/specs/2026-07-21-oracle-code-spec-research-brief.md:61` | bare list + the targetable⇒`D1`/`D2`/`D3` rule |
| `journal/live/specs/2026-07-21-oracle-code-spec-research-brief.md:123` | bare list, inside the `D4`-retag scope note |
| `informed-operator/design/residual-loss-methodology.md:119` | bare list, inside a **superseded-legend banner** |
| `informed-operator/design/residual-loss-methodology.md:421` | written `D0–D4` — **omits `DN` entirely**, which is the defect biting |
| `journal/tools/check_data_agreement.py:461` | hardcoded Python set `{'D0','D1','D2','D3','D4','DN'}` — a twelfth copy, in code |

Related live collisions the vocabulary must not reintroduce, per `6.6:137-143`: `DX` (the DX center in AlGaN/AlN, `deriv-defects` Part B) and `D1`–`D5` (wurtzite deformation potentials in `accuracy-ledger`).

### `T0–T3` and the `D`-tags: is each owned by exactly one page?

Asked specifically; answered specifically.

**`T0–T3` — one owner, four unguarded copies.** `glossary.md:41` names `named-formulas` as canonical. The legend is written out in full at `6.6:59-61` (owner), `6.9:100-102` (verbatim duplicate), `4.4-computational-overview.md:435` (duplicate + the 76/40/11/5 distribution, which I verified against the CSV and which reconciles), and `informed-operator/design/residual-loss-methodology.md:328`. `7.2-residual-machinery.md:296-297` restates `T0`/`T1` but attaches sampling cadence — that is a *different* fact and should keep its own home. `11.6-deriv-csp.md:27` runs a **different `T0`–`T4` scale one tier deeper**, flagged in place. Probe B: no checker holds any two together.

**`D`-tags — one owner, eleven restatements.** Table above.

---

## Log-worthy advancements

| date | finding or decision | evidence | attribution | superseded |
|---|---|---|---|---|
| 2026-07-21 | **`DN` split out of `D0`.** The old `D0` conflated "a pure read whose adjoint is the identity" with "an integer output with no derivative" — opposite answers to the question the tag exists to answer. Eleven smooth analytic rows sat at `D0` and therefore registered with **no adjoint at all**, because `build-verification` exempts `D0`; among them the alloy-lattice interpolation that `product` promises is directly optimizable through baked gradients. Those eleven are now `D1`. | `6.6-named-formulas.md:123-130`; `10.2-open-decisions.md`; CSV now shows exactly one `D0` row | corpus retag pass | the single-`D0` legend |
| 2026-07-21 | **The twelfth `D0` row.** `chemical-potential-ref-table` survived the first retag because "ref-cache lookup" reads like a pure read. It takes `T` and `P`, so tagging it `D0` zeroed `∂μ_i/∂T` and left row 69's Maxwell cross-derivative residual **vacuously satisfied**. Generalized rule: an implementation detail (a cache) is not a mathematical one (an identity adjoint). | `6.6-named-formulas.md:130-135` | second-pass audit | the first retag pass's coverage claim |
| undated (before 2026-07-22) | **Mixed-output rule adopted.** A row returning a real quantity *and* a discrete label is tagged by its continuous component; a discrete label never drags a row to `DN`. Without it the same construction was tagged three ways — `radius-ratio-coordination-class`, `elastic-stability-criteria` and `structure-uniqueness-CSP` read `D1`, `D1` and `DX`. | `6.6-named-formulas.md:111-121` | corpus retag pass | the `D1`/`D1`/`DX` tagging of those three rows |
| 2026-07-21 | **`D3` established as a refinement of `D2`, not an alternative**, and the `τ_cond` conditioning gate added. Every `D3` row runs the `D2` registration gate **plus** a fixed-point-Jacobian conditioning check. Without it the tag would be strictly weaker than `D2`, which is backwards: the ill-conditioned fixed point is the one failure mode canon names for it, and the gradient it produces is *large and wrong* rather than absent. Bites `fermi-level-charge-neutral`, `self-consistent-charge-balance` (∂F/∂E_F flattest exactly in a wide-gap intrinsic semiconductor) and `SCPH-self-consistent-phonons` (soft modes). | `6.6-named-formulas.md:92-104`; `10.2-open-decisions.md:133-135` | gap-closure pass | the unbounded-conditioning open item |
| undated (before 2026-07-22) | **The `path` field un-retired as an anchor class.** It was declared retired on the grounds that the always-cheap reframe collapsed the two runtime paths. It did — but the column's live meaning is *what a row's value is anchored against*, and that is the axis obligation-6 consistency pairs run along. Retiring a field several pages depend on is how a load-bearing distinction becomes folklore. | `6.6-named-formulas.md:152-173`; CSV `Path` = 117 cheap / 15 faithful | corpus audit | the retirement of the `path` field |
| undated (before 2026-07-22) | **`DX` renamed `DN`.** `DX` collided with the DX center — the deep-donor configuration this corpus discusses in AlGaN and AlN — so searching for the tag returned the physics and searching for the physics returned the tag. Diff tags are written in backticks in prose for the same reason; the wurtzite deformation potentials `D1`–`D5` are the other live collision. | `6.6-named-formulas.md:137-143` | nomenclature audit | the `DX` spelling |
| undated (before 2026-07-22) | **Four inline-math invocations replaced by declared names**, closing a violation of the no-inline-math rule inside the page validating the closed vocabulary. The expressions are recorded alongside the names — `(2ω/c)·Im(√ε)`, `Re(√ε)`, `σ/(n·e)`, `E_BO + F_vib + F_el` — which is what makes registering those four rows transcription rather than research. | `6.8-typed-compositions.md:214-226` | corpus audit | inline mathematics in `formula =` slots |
| undated (before 2026-07-22) | **Five corrected physical forms made canonical**: optical absorption `(2ω/c)·Im(√ε)`; the operator-spectrum-area sum rule carries the `2/π` prefactor; the acoustic sum rule sums over all lattice translations (`Σ_J Σ_R Φ_{IαJβ}(R) = 0`); the magnetic relaxation term is the orientation-preserving `S × (S × H_eff)`; the harmonic transition-rate normalization consumes products-over-modes, not spectra. | `6.6-named-formulas.md:145-150`; `6.8-typed-compositions.md:144-145` | physics reconciliation | the pre-correction forms of all five |
| undated (before 2026-07-22) | **`B1..B11` bundle labels re-canonicalized.** `properties` carried a pre-canon scheme in which `B11` meant "topology atlas"; canon now has `B11` = degradation. | `6.10-properties.md:51-53` | canon consolidation | the pre-canon `B*` scheme in `properties` |
| undated (before 2026-07-22) | **`mesh-interpolation` registered as a sub-method, preserving the closed 12-method alphabet.** The compile-time band/e-ph interpolator — Fourier for gauge-free band energies and velocities, Wannier–EPW for gauge-sensitive e-ph matrix elements, with mandatory dipole/quadrupole polar corrections; runtime reads the interpolated grid only, C1-clean. Interpolation is a sub-method, not a new top-level method. | `6.1-canonical-vocabularies.md:72-77`; `6.4-computational-methods.md:83-87` | UWBG scope extension | a proposed thirteenth method |
| 2026-07 | **The `Source`-legend lag closed.** Rows 128–134 (the 2026-07 gap-audit package) carry `Source = topology atlas`; the Counts prose always described them correctly and only the column legend lagged. | `6.9-formula-registry.md:95` | gap-audit pass | the pre-fix `Source` legend |
| undated (before 2026-07-22) | **Five incompatible differentiability legends collapsed to one**, and `formula-registry` switched from restating the vocabulary to linking it. The restatement is named as the cause of the five-legend divergence. | `6.9-formula-registry.md:104-106` | legend reconciliation | four superseded diff legends |
| 2026-07-22 | **Bundle vocabulary harvested from the field schema, not the nearby enumeration.** A first version of the `Bundle` column check harvested only the `6.1 §4` table, reported rows 91–94 (`Z*`, `ε∞`, `χ∞`, `α_M`, the `L1` primitives) as defects, and the "fix" retagged four correct rows to `B1` before either canon page was read. Both pages say `L1` is deliberate. | `check_data_agreement.py:436-457`; `10.4-traps.md` §70; commit `287d2eb` | checker calibration | the table-only harvest and the four incorrect `B1` retags |

---

## Contradictions — COLLECTED, NOT RESOLVED

| claim | source A | source B | nature of the conflict |
|---|---|---|---|
| Whether other documents restate the canonical counts | `6.1-canonical-vocabularies.md:44` — "Every other document references these numbers rather than restating them." | `1.5-rationale.md:75-77` (132 substantive, 12 methods +3 sub-methods, 20 templates, 11 bundles, 19 categories, 10 obligations) · `8.7-build-verification.md:35-36` · `4.4-computational-overview.md:432-435` · `4.1-physics-graph.md:174-183` · `journal/live/presentations/2026-07-22-prep.md:324-325` | The page's own governing rule is false of the corpus in both directions: at least five documents restate the numbers, and `6.1` itself restates eleven counts other pages own. Nothing enforces the rule |
| Whether a legend may be restated on `formula-registry` | `6.9-formula-registry.md:104-106` — "Restating it here is what let five incompatible legends coexist; this page now links rather than repeats." | `6.9-formula-registry.md:100-102` — the full `T0`/`T1`/`T2`/`T3` legend with all four timing bounds, verbatim from `6.6:59-61`, two lines earlier | The page states the anti-restatement rule for one tag column while violating it for another, in the same section. Probe B confirms the duplicate is unguarded |
| Whether coded-column vocabularies are harvested or restated in the checker | `check_data_agreement.py:436-437` — "The vocabularies are HARVESTED, never restated here — a second copy is the thing this tool exists to catch." | `check_data_agreement.py:460-462` — `('Tier', {'T0','T1','T2','T3'})`, `('Diff', {'D0','D1','D2','D3','D4','DN'})`, `('Path', {'cheap','faithful'})` hardcoded | Only `Bundle` is harvested. Three of four coded columns are exactly the second copy the comment forbids. If `6.6`'s legend changes, the checker keeps validating against the old vocabulary silently |
| Where cert obligation-7 / the cert obligations live | `6.5-property-templates.md:107` — "a cert obligation (§8 obligation-7)" | `6.2-typeclass-alphabet.md:51` — "Cert obligations (§12)" · `6.1-canonical-vocabularies.md:121-122` — "obligation-7 … §14" · `6.3-topology-atlas.md:40` — "`DiscreteStructure` instances (§10)" | Four bare ordinals in one chapter for two targets, all mutually inconsistent and none resolving to a page. Pre-book coordinates that rotted silently; `check_data_agreement.py:39-41` documents that bare-`§` resolution was deliberately removed from the checker |
| The name of the ν₀ harmonic prefactor | `6.8-typed-compositions.md:133-135` — `ν₀ = AlgebraicOf({…}, formula = harmonic-transition-rate-normalization)` | `6.8-typed-compositions.md:168` — `ν₀ = harmonic-rate-prefactor` | The same quantity carries two names on one page. Only the first is in `unregistered-formulas`; the second is invisible to the seam sweep because it is not in a `formula =` slot |
| Whether the named-formula vocabulary is closed | `6.1-canonical-vocabularies.md:54` — "Named formulas | 132 substantive (+2 architectural markers) | **yes**" (Closed? column) · `:128` — "Closed registry of typed, fully-parameterized algebraic formulas" | `6.8-typed-compositions.md:182-188` — eighteen invoked names are not registry rows, "so this page's closed-vocabulary claim does not yet hold in full" | `6.1` asserts closure without qualification; `6.8` declares the gap. Both are canon. Verified: all 18 absent from the CSV |
| How many live places use the `path` anchor class | `6.6-named-formulas.md:169-173` — "the anchor-class meaning is what the corpus actually uses the column for, **in four live places**… Retiring a field that **four pages** depend on…" | Sweep of `journal/pages/` for `cheap`/`faithful`: outside `6.6` and ch. 11 the pages are `6.9`, `9.1-accuracy-ledger`, `2.4-multiscale-state` — three. `7.3-cross-cutting-rules.md:51-54` defines the consistency pair but never uses `cheap`/`faithful`, and `5.1-cert-obligations.md:141-142` names the pair tolerances without the axis | An uncited count in prose that no page owns and no checker can verify. Which four were meant is not recoverable from the text |
| Which artifact wins a scope-vs-inventory disagreement | `6.10-properties.md:29` — "where they disagree, **the registry wins**" | `6.1-canonical-vocabularies.md:44` — the counts page is where numbers live and others reference it | Two different precedence rules for the same class of conflict, stated on two pages, neither citing the other. Mild, but the restructure has to pick one |

---

## Notes for Phase 2

**This chapter's real shape.** Ten pages describe one vocabulary and a CSV that is
canonical for much of the same content. The duplication is not evenly spread — it
concentrates in two places, and both have the same root cause:

- **`6.9-formula-registry` is the redundant page.** Of its five sections, "What the
  registry is" duplicates `6.6` + `4.1`, "Columns" restates the CSV header, the
  cost-tier legend duplicates `6.6` verbatim, the differentiability legend is a bare
  pointer, and "How a formula becomes a residual" summarizes `7.2`. Exactly one
  block is unique: the row-band → physics-package map. Rows 116-119 move that to
  `named-formulas`; the rest deletes. Under plan §6 the page's stated job — "the
  human-readable index over the CSV" — is what `index/corpus.json` plus the
  generated `contents.md` are for.

- **`6.1-canonical-vocabularies` is *not* redundant, despite looking index-shaped.**
  Only its header count table is index-like, and that table is the emitted view under
  plan §6. Its seven numbered sections carry substantive content that exists nowhere
  else: the `mesh-interpolation` interpolator description, the templates' `Produces`
  mapping, `CrystalSymmetryGroup` and `IrrepLabel`, the `(StateComponent, SubDofTag)`
  pair table, and the ten theory-context vocabularies. My rows scatter six of the
  seven sections to their owning pages and leave §7 — the one topic `index.md`
  agrees it owns. If Phase 2 prefers to keep `canonical-vocabularies` as a page,
  §7 alone is enough to justify it; if not, §7 merges into `coupling-structure`
  beside the `TheoryContext` record.

**Hard ordering hazard — the checker reads two of these pages.**
`check_data_agreement.py` harvests live vocabulary from the corpus at import time:

- `:450-452` reads the `| Bn |` table out of `6.1-canonical-vocabularies.md` by path,
  and `:464-467` raises a finding if the table is not found.
- `:456-457` reads the phrase `` `L1` primitive tag`` out of `6.6-named-formulas.md`
  by regex.

Row 17 moves that table to `observable-bundles` and row 65 keeps the `FormulaRecord`
comment intact. **Both edits must land in the same commit as the checker rewrite, or
the Bundle column silently goes unchecked** — the `if not _BUNDLES` guard prints a
finding, but only if someone reads it. `traps §70` records the last time this class
of mistake retagged four correct rows.

**Two pages are already orphans; two more become orphans when ch. 11 dies.**

| page | inbound edges today | after ch. 11 |
|---|---|---|
| `observable-bundles` (6.7) | **none** | none |
| `computational-methods` (6.4) | one heading in `4.4` | one |
| `formula-registry` (6.9) | `deriv-csp`, `deriv-generator-catalog`, `deriv-high-field`, `properties` | `properties` only |
| `properties` (6.10) | `deriv-high-field` | **none** |

`6.7` and `6.4` are orphaned because `6.1` holds the content that would cite them —
rows 7-9 and 17-18 fix that by merging. `6.9` and `6.10` are orphaned because their
only real readers were appendix pages. That, plus their vacuous `canonical-for`, is
why I dissolve `6.9` and propose merging `6.10`.

**Merge proposal I could not settle: `properties` into `typed-compositions`.**
`6.8:39` says it writes "every property in `properties.md`" as a typed composition,
so the two pages are one artifact split in half: `6.10` is the checklist, `6.8` is
the proof it is covered. Merging would make the coverage claim checkable — a
composition per listed property, with the gaps visible. Against merging: `6.10`'s
nine motivation paragraphs are reader-facing scope prose and `6.8` is dense typed
pseudocode; the merged page reads as two documents. I have dispositioned both to
survive as separate pages under `oracle/registry/`; **the merge is Javier's call**
and is the only structural decision in this chapter I did not make.

**Low-confidence rows, named.**
- Row 45 (`6.3:15-17`, the "(Lattice + SiteDecoration + Laws) → Material" composition
  axiom) — I sent it to `compose-time-pipeline`, but it may belong to
  `architectural-principles`. It is a preamble on a topology page either way.
- Rows 20-22 (`CrystalSymmetryGroup`, `IrrepLabel`) — I sent them to
  `representation-substrate` because their identity is an `Address[GroupAtlas]` and
  their derived outputs are substrate fibers. `compose-time-pipeline` is defensible:
  the group is *assembled* at Stage 1+2. Either target keeps them together; splitting
  them would be the wrong outcome.
- Row 129 (Magnetic has no dedicated bundle) — I kept it as a body fact. It is
  arguably an `open-questions` entry, since it is a stated coverage hole with a
  reason rather than a decision.

**The `path` field's history is worth preserving as a trap, not as prose.** Row 84
deletes the "briefly declared retired" paragraph, and the log entry captures the
event. But the *lesson* — a field several pages depend on was retired on a
reasonable-sounding argument, and un-retiring it required reconstructing why four
places used it — is a live hazard about how this corpus fails, and belongs in
`practice/traps` alongside §70. Flagging so it is not lost between the log and the
delete.

**Where I could not disposition confidently, and why.**
- The `Source`-column values in the CSV (`extension`, `topology atlas`, research-file
  pointers) are described by `6.9:95` and owned by the CSV. I dispositioned the
  prose; the CSV's own `Source` discipline is the manifest surveyor's.
- `6.9:69-70` cites `physics/research/` as the grounding for rows 1–87. The plan
  flags `10.3-audit-prompt` for citing that directory for physics that moved to
  `pages/11-`. I did not verify whether `physics/research/` still holds the rows-1–87
  grounding; if it does not, row 119's provenance claim is a dangling promise and
  the *actual* provenance may only exist inside chapter 11 — which would make it
  urgent, since ch. 11 is being deleted. **Worth one check before Phase 2 starts.**
- I did not disposition `registry-manifest.csv` (another surveyor owns it), but I
  verified against it throughout. Everything reconciled: 134 rows = 132 + 2 markers;
  `Path` 117/15/2; `Tier` 76/40/11/5 matching `4.4:435`; exactly one `D0` row
  matching `6.6:70`; all 18 declared-unregistered names absent; all 20 registry names
  I spot-checked from `6.6`/`6.7`/`6.8` present. **I found no count in this chapter
  that disagrees with the CSV.**
