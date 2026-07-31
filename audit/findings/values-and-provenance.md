# Values and provenance — audit findings

Subject: every seeded number and what it rests on. `journals/oracle/accuracy/` (`accuracy-ledger`,
`reference-battery`), `data/reference-data/*.csv` (179 rows), `data/registry-manifest.csv`,
`data/diamond-strain-sweep/`.

Read-only pass. Nothing here was applied.

---

## The limitation this report is read under

**Read this before any finding.**

The cross-check that certified ledger-against-CSV agreement scored 6 of 6 on its own calibration
and then **refused the score**, on the ground that it had only ever compared corpus text against
corpus text and had never once checked a citation against primary literature. That refusal is the
single most important result the audit produced about itself, and it governs this file:

> **Establishing that the corpus agrees with itself is not establishing that the corpus is
> correct.** The great majority of the mechanical work below — encoding censuses, key-collision
> counts, arithmetic reproductions, cross-file agreement — measures internal consistency. A corpus
> can be perfectly self-consistent and uniformly wrong.

Where a finding in this file *does* rest on primary literature, it is marked **[primary]** and the
document and quotation are named. There are now four such checks, and one of them (F1) overturns a
top-ten severity item by reading the cited paper. Everything unmarked is internal evidence and
should be read as such.

Two further honesty adjustments, both of which cut against this file:

- **Several of the sharpest-sounding items are already declared open questions** on
  `accuracy-ledger.md:44–71`. A declared question is honest and is not a defect. Where a thread was
  declared, I say so and state what my contribution actually is — usually *closing* it, which is a
  contribution but not a finding against the corpus.
- **One of my own probes returned a clean zero because it was broken.** Caught by a control (§5).
  The draft number it was supposed to check turned out to be right, but the probe would have
  certified a false negative.

---

## Status

| | |
|---|---|
| Findings established | 17, of which 7 are new since the draft |
| Inherited contradictions triaged | 8 in my subject — 6 dead (source page deleted), 1 alive and extended (F4), 1 answered by being unanswerable (§2b) |
| Primary-literature checks completed | **3** — the FLR 2017 full text (F1, and the reference-list confirmations in F11), the Lee 2023 Crossref record (N7), the Olson 1993 citation via FLR's reference list. F10 rests on an internal proof plus one standard constant stated from knowledge, not fetched |
| Undergraduates in flight | 2 — Slack 1987 (AlN), Vurgaftman & Meyer 2003 (AlN effective mass) |
| Calibration | 6 of 8, unrounded — **plus two of my own certified-clean checks found to rest on methods that could not support them** (§5) |
| Corpus gates | untouched; nothing here changed `journals/` or `data/` |

Findings marked **[principal]** landed with the principal during the session-limited run and are
folded in here with attribution. Where I re-ran their arithmetic myself the result is stated in my
numbers, and **two of them do not reproduce as circulated** — see F5 and F9.

---

## 1 · Findings

Ordered by severity. Every finding states what would refute it.

---

### F1 — The `0.4 Θ_D` four-phonon criterion is attributed to a paper that never uses the word "Debye", and the paper's own second material refutes the generalisation by a factor of 2.3 **[primary]** **[principal: identified; this verification is mine]**

**Severity: high. Confidence: high — primary text, with a stated control.**

**The claim.** `data/registry-manifest.csv:122`, registry row 121:

> `121,kappa-4phonon-high-t-correction,"(κ_3ph, T, Θ_D) → κ",…,"S1 (Slack-like 4-phonon multiplicative factor, valid T≳0.4Θ_D; Feng-Lindsay-Ruan PRB 96 161201)",…`

The validity criterion `T ≳ 0.4 Θ_D` sits inside the same cell as, and is attributed to,
Feng, Lindsay & Ruan, *Phys. Rev. B* **96**, 161201(R) (2017). `accuracy-ledger.md:125` repeats it:
*"the four-phonon correction is needed above `≈0.4 Θ_D` … For diamond that threshold is about
880 K"*.

**The evidence.** I obtained the full accepted manuscript (OSTI 1427696, via Unpaywall from DOI
10.1103/PhysRevB.96.161201) and extracted its text — 5,230 words, all four figure captions, the
complete reference list.

**The word "Debye" does not occur anywhere in the paper.** Zero occurrences.

*Control for that negative:* the same extraction locates both of the paper's substantive claims
about diamond, verbatim, so the extraction is not the reason "Debye" is missing:

> "For diamond and Si the three-phonon predictions agree well with measured data at low
> temperature (<600 K for Si, <900 K for diamond), however, significant deviations from experiment
> occur at high temperatures. For example, at 1,000 K three-phonon scattering alone over-predicts
> κ of diamond and silicon by 31% and 26% as compared to experimental values, respectively."

What the paper actually states is a **per-material temperature**, not a Debye fraction. And it
states **two** of them — which is what kills the generalisation:

| material | FLR's stated threshold | Θ_D | implied fraction |
|---|---|---|---|
| diamond | 900 K | 2200 K (the corpus's seeded value) | **0.409** |
| silicon | 600 K | 645 K | **0.930** |

The corpus's `0.4` is diamond's number divided by the corpus's own Debye temperature — a value the
same ledger declares **UNSEEDED** (`accuracy-ledger.md:430`). It reproduces to three digits:
900 ÷ 2200 = 0.4091. Applied to the paper's other material the same rule predicts a silicon
threshold of 0.4 × 645 = **258 K**, against the paper's stated **600 K**.

*Robustness of the silicon leg:* 645 K is my own value, not the corpus's — silicon has no row in
the battery. The conclusion does not depend on which figure is used: across the standard range of
quoted silicon Debye temperatures (625, 636, 645, 692 K) the implied fraction is **0.87–0.96**, and
the predicted threshold under a 0.4 rule is 250–277 K against FLR's stated 600 K. There is no
silicon Debye temperature that reconciles the two materials under a single fraction; reconciling
them would require Θ_D(Si) ≈ 1470 K, which is more than twice any published value.

So the criterion is circular in one direction and false in the other: back-derived from an unsourced
number, then generalised into a universal rule the cited paper neither states nor supports.

**This resolves the 773 K contradiction constructively** (my draft V6, now retired as a separate
finding). Regime row 12 says the correction is *needed* above ≈0.4 Θ_D = 880 K; the MVP target row
(`accuracy-ledger.md:188`) says the 773 K target is met by that correction, *valid* ≳0.4 Θ_D. Both
readings failed. FLR's own 900 K settles it: **at 773 K the three-phonon path is adequate on the
cited paper's own testimony**, so the MVP row names the wrong path, and the four-phonon correction
belongs above 900 K.

**Proposed correction.** Replace `valid T≳0.4Θ_D` in registry row 121 and in regime row 12 with the
cited paper's own directly-stated per-material thresholds — ~900 K for diamond, ~600 K for silicon —
and change the 773 K MVP row to name the three-phonon path. This removes the dependence on the
UNSEEDED Debye temperature entirely, which is the reason to prefer it over re-deriving the fraction.

**What would refute it, and the strongest defence available.** Three things, in descending order of
plausibility:

1. **The cell's `Slack-like` qualifier.** The full cell reads *"S1 (Slack-like 4-phonon
   multiplicative factor, valid T≳0.4Θ_D; Feng-Lindsay-Ruan PRB 96 161201)"*. A reader could argue
   the functional *form* is Slack's and only the four-phonon *result* is FLR's, so the criterion is
   attributed to Slack rather than to FLR. **This does not rescue it.** The cell names exactly one
   citation, and no Slack work is named anywhere near it; more importantly, the criterion is still
   refuted by FLR's own two materials regardless of who is credited with it. If the intent is a
   Slack attribution, the cell must name the Slack paper and the criterion must still be corrected.
2. A Debye-fraction criterion in the FLR **supplemental material**, which I did not obtain — the
   main text references "Supplemental Fig. S1". This is **shaped gap G3**, and it bears only on the
   attribution, not on the falsification.
3. A different paper being the intended attribution entirely, which would make this a citation
   defect rather than a manufactured criterion.

---

### F2 — The `×N` uncertainty encoding carries two incompatible meanings, and the schema declares only one **[principal: 179-row sweep; independently re-run here]**

**Severity: high. Confidence: high (mechanical, re-runnable).**

**The claim.** `reference-battery#row-schema` declares three uncertainty encodings and instructs
that **"a consumer must dispatch on the format"**. For the multiplicative one:

> | a multiplicative factor, written `×N` | a log-scale band — the value is known to within a factor N, so `σ_ln = ln N` |

`traps.md:215` repeats the same single rule.

**The evidence.** My own sweep of all 179 rows:

| population | count | example | what `σ_ln = ln N` gives |
|---|---|---|---|
| **N < 1** | **34** (70.8% of multiplicative, **19.0% of the whole battery**) | `thermal-conductivity` diamond 773 K, `×0.4` | `ln 0.4 = −0.916` — **a negative σ** |
| **N ≥ 1** | 14 | `impact-ionization-an` GaN, `×3` | `ln 3 = +1.099` — works |

The N<1 values in use are {0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5}; the N≥1 values are {2.0, 2.5, 3.0}.
The 34 N<1 cells can only mean *"±N as a fraction of the value"* — a **linear relative** band. Read
as a log band, `×0.15` on the diamond 300 K conductivity anchor would be a factor of 6.7, against a
measured spread of 2000–2500 W/m·K (a factor of 1.25).

**Two conventions share one column and the format does not distinguish them.** A consumer doing
exactly what the page instructs applies the log rule to all 48 and gets a negative σ on 34.

**And the log reading is not benign where it does apply.** On the 14 N≥1 cells, `τ_battery = 3σ`
in log space trips at a factor `N³`:

| N | rows | trip threshold |
|---|---|---|
| ×2.0 | 2 (pyroelectric AlN, GaN) | factor **8** |
| ×2.5 | 2 (impact ionization, diamond) | factor **15.6** |
| ×3.0 | **10** (impact ionization: GaN ×4, β-Ga₂O₃ ×6) | factor **27** |

A factor-27 acceptance band on impact-ionization coefficients — a quantity whose literature the
ledger itself says spans "four orders" — is a gate that will accept essentially any computed value.

**Five encodings are in use where the schema declares three plus a dash.** Full census of all 179:

| encoding | rows | declared? |
|---|---|---|
| absolute | 118 | ✔ |
| multiplicative `×N` | 48 | ✔ (ambiguously — above) |
| dash | 6 | ✔ |
| `unbounded` | 3 | ✔ |
| **`sign only — magnitude not pinned`** | **2** | ✘ |
| **`range` / `range (theory only)`** | **2** | ✘ |

The two `sign only` rows (`crystal-field-splitting-delta-cr`, AlN and GaN) also carry a
**non-numerical Value** — `negative (Δ_cr < 0)` and `positive (Δ_cr > 0)` — against a schema that
says Value is *"the numerical value in canonical units"*. The two `range` rows likewise hold
intervals (`150-200 cm2/Vs`, `12–15.4 MV/cm`), and nothing states whether a range is a uniform
interval, a 1σ band, or a min/max over sources.

**Five properties use different encodings across their own rows** — so the ambiguity is not
partitioned by quantity:

| property | encodings mixed |
|---|---|
| `thermal-conductivity` | absolute **and** multiplicative |
| `breakdown-field-critical` | multiplicative **and** range |
| `mobility-electron-best-exp` | multiplicative **and** range |
| `impact-ionization-an` | multiplicative **and** unbounded |
| `impact-ionization-bn` | multiplicative **and** unbounded |

**And one material switches encoding between its own temperatures.** AlN `thermal-conductivity`:
300 K carries `7 W/mK` (absolute), 773 K carries `×0.3`, 1100 K carries `×0.4`. Three rows, one
property, one material, two encodings.

**The sharpest edge.** `traps.md:213–219` registers this exact hazard, in a section whose own title
asserts the count:

> ### Three uncertainty encodings, and one that is unassigned
>
> Absolute standard deviation, multiplicative `×N` (log-standard-deviation `ln N`), and
> `unbounded`. A row whose uncertainty cell is unassigned **cannot** back a provenance ledger
> coefficient. *Breaks:* consumers dispatch on the wrong uncertainty format, or a certification run
> refuses exactly the compositions a seeding wave existed to enable. — **enforced**,
> [reference-battery#row-schema]

Three things are wrong at once. The heading says **three** where **five** are in use. The
parenthetical `(log-standard-deviation ln N)` is the rule that is undefined on 34 of the 48 cells.
And the hazard is marked **enforced**, pointing at `reference-battery#row-schema` as the enforcing
authority — **the page whose rule produces the hazard**. There is no probe behind the marker; this
is the "enforced as a prose claim with no mechanism" class, instantiated on my subject's own column.

**What would refute it.** A statement anywhere that `×N` for `N < 1` means a linear relative band,
or that `sign only` and `range` are admitted. I searched `journals/` for `×N`, `multiplicative`,
`σ_ln`, `log-scale band`, `factor N`, `sign only`, `range`; the only hits on the encoding state the
log rule alone.

**Proposed correction.** Split the encodings into unambiguous markers — `±15%` for the linear
relative band, `×2.5` reserved for the log band — and declare `range` and `sign-only` with stated
semantics, or convert those four rows.

---

### F3 — Seven rows have a 3σ acceptance band that includes zero on a positive-definite quantity, and four of them are every high-temperature thermal conductivity in the corpus **[principal: confirmed]**

**Severity: high. Confidence: high (arithmetic on the shipped data).**

Under the linear reading forced by F2, `τ_battery = 3σ` produces:

| row | value | σ | 3σ as % of value | lower bound |
|---|---|---|---|---|
| `thermal-conductivity` diamond 773 K | 620 W/mK | ×0.4 | 120% | **−124** |
| `thermal-conductivity` diamond 1100 K | 450 W/mK | ×0.4 | 120% | **−90** |
| `thermal-conductivity` AlN 1100 K | 95 W/mK | ×0.4 | 120% | **−19** |
| `thermal-conductivity` GaN 1100 K | 37 W/mK | ×0.4 | 120% | **−7.4** |
| `caughey-thomas-mu-p-min` GaN | 10 cm²/Vs | ×0.5 | 150% | **−5** |
| `caughey-thomas-mu-n-Nref` GaN | 1e17 cm⁻³ | ×0.5 | 150% | **−5e16** |
| `caughey-thomas-mu-p-Nref` GaN | 2.5e17 cm⁻³ | ×0.5 | 150% | **−1.25e17** |

All seven are positive-definite. **No computed value can trip the lower side of these gates.**

The pattern is not random: **the four conductivity rows are exactly the corpus's high-temperature
conductivity rows** — the ones whose provenance is weakest. The two diamond rows carry an internal
audit pointer where a source belongs; the AlN rows carry a method. **The rows that most need
checking are the rows whose gate cannot fire.**

Even the 300 K diamond anchor, at `×0.15`, admits [1210, 3190] W/m·K — a 2.6× span on a quantity
whose measured spread is 2000–2500.

**What would refute it.** A statement that `τ_battery` is one-sided, clipped at zero, or compared in
log space for these rows. `cert-obligations.md:145` states `3σ` flatly.

**Proposed correction.** Tighten these σ to what the evidence supports, or state the band as
asymmetric/log so it is falsifiable on both sides. A gate that cannot fail low is not a gate.

---

### F4 — Gallium oxide's displacement threshold became gallium nitride's "nitrogen", and the row is simultaneously seeded and declared unseeded **[principal: identified; migration re-traced here from corpus history]**

**Severity: high. Confidence: high on the migration (documentary); high on the three-way state disagreement (mechanical).**

**Part one — the migration.**

`accuracy-ledger.md:155`, regime row 42:

> | 42 | displacement_threshold E_d | ±5 eV | tabulated: about 37 eV for carbon, about **20 eV on the gallium sublattice**, about **25 eV for nitrogen** |

The source table is recoverable from the corpus's own history. `log/timeline.md:1596` quotes the
now-deleted table from `11.5-deriv-high-field.md` in full:

> "against silicon's ≈21 eV, diamond (37–50 eV) is about 2× better, aluminium nitride (~35) and
> gallium oxide (~25) are better, and **gallium nitride (~20 eV) is at or below silicon**"

Five materials, one number each: Si 21, diamond 37–50, AlN 35, **β-Ga₂O₃ 25**, **GaN 20**.

`journals/oracle/state/multiscale-state.md:235` reproduces four of them faithfully as a per-host
table — Diamond ~37–50, GaN ~20, AlN ~35, β-Ga₂O₃ `UNSEEDED`.

The ledger's regime row 42 does not. It takes the same five-material list and relabels two entries
from *materials* to *sublattices*:

| source table | ledger row 42 | what changed |
|---|---|---|
| diamond 37–50 eV | "about 37 eV for **carbon**" | material → its only element; harmless |
| **GaN** ~20 eV | "about 20 eV on the **gallium sublattice**" | whole-compound value relabelled as one sublattice |
| **β-Ga₂O₃** ~25 eV | "about 25 eV for **nitrogen**" | **gallium oxide's value relabelled onto an element gallium oxide does not contain** |

**Gallium oxide is Ga₂O₃. It contains no nitrogen.** That is what makes this provably a migration
rather than a coincidence: no measurement of "nitrogen in gallium oxide" exists to be quoted,
because the object does not exist.

And the 25 is not idle. `material-constants.csv:42` is the corpus's **only** seeded displacement
threshold, and it is β-Ga₂O₃ at exactly `25 eV ± 5 eV`. The number that the ledger relabels
"nitrogen" and the number the battery seeds for gallium oxide are the same number.

**Part two — the row is in three states at once.**

| location | state |
|---|---|
| `data/reference-data/material-constants.csv:42` | **seeded**: `25 eV`, σ `5 eV`, Source class `literature-review` |
| `journals/oracle/state/multiscale-state.md:235` | **`UNSEEDED`** |
| `log/timeline.md:2148` | *"It is unseeded, and an open question"* — dated 2026-07-31 |

The CSV outranks canon pages for values. So the retirement was recorded and never applied: the
canonical carrier still seeds the value the log says was withdrawn, still under a
`literature-review` class that `accuracy-ledger.md:422` says corresponds to *"an appendix that
states the value as a bare parenthetical with no citation"*.

**Part three — the scalar is the wrong type of object.** The ledger already records this
(`accuracy-ledger.md:422`, citing He et al., *Acta Mater.* **276** 120087 (2024)): the literature
reports this quantity **per site** — two inequivalent gallium and three inequivalent oxygen — with
strong recoil-direction dependence. Per the inherited gallium-oxide lead the site means span
**17.0–22.9 eV**. **25 ± 5 matches no site mean, no average and no extremum**; its band [20, 30]
brushes the top of the site range and covers nothing else.

**What would refute it.** A source predating the deleted table that independently reports 25 eV for
nitrogen in some nitride, which the ledger could have been quoting instead. The arithmetic
coincidence with the seeded gallium-oxide row, and the fact that all five materials in the ledger's
list are the deleted table's five, make that very unlikely.

**Proposed correction.** Three separable actions: (a) fix regime row 42's labels to name materials,
not sublattices — or delete the tabulation, since it duplicates `multiscale-state`'s table, which
is correct; (b) apply the declared retirement to `material-constants.csv:42`, making it `UNSEEDED`;
(c) if a value is wanted, seed it per site as the literature reports it, which the consuming formula
(`nrt-displacements`, registry row 111, `N_d = 0.8·T_dam/(2·E_d)`) can take.

---

### F5 — The "24 unsourced rows" figure is correct only under a rule stated nowhere in the corpus, and the rule printed beside it gives 22

**Severity: moderate. Confidence: high (mechanical, fully enumerated). Corrects both my own draft and the circulated figures.**

`accuracy-ledger.md:378`: **"24 of them carry a `Source` cell that names no author and no year."**
`accuracy-ledger.md:214` restates the same rule.

**My draft certified this as ✓ matching. The principal's sweep reported 23 strictly and 29 laxly.
Neither is what I get, and the reason turns out to be more interesting than the count.**

30 of 179 rows have a Source cell containing no publication-plausible year (internal ISO audit dates
such as `2026-06-10` stripped; I checked for false positives from physical numbers like `1800 K`
and found none). Of those 30, **six carry an arXiv identifier** and **eight name a human surname**,
with overlap. So the count depends entirely on what "names no author" means:

| rule | count |
|---|---|
| any surname at all disqualifies | **22** |
| all but method eponyms ("Slack extrapolation") | **24** |
| full author citations + object eponyms (Åhman cell, Berman–Simon) | 25 |
| only full author citations (Łopuszyński & Majewski, Mora-Ramos, Wang–Zhao) | 27 |
| nothing disqualifies — every no-year row | 30 |
| **`audit/inherited/PROVENANCE.md`'s rule: "no author-year *and* no DOI/arXiv identifier"** | **24** ✓ |

**24 is exactly right — under the rule stated in `audit/inherited/PROVENANCE.md`, which is an audit
working note and not part of the corpus.** The rule printed in the ledger beside the number drops
the identifier clause, and under it the answer is 22.

The two sets are not merely different sizes; they differ in membership. The ledger's printed rule
excludes six rows that name authors (`elastic-tensors:26` Åhman, `material-constants:31`
Berman–Simon, `phonon-frequencies:11` **"Wang–Zhao Powder Diffr. (971 K)"** — a full author
citation with a journal — `transport:19` Davydov, `transport:25` and `:43` Slack), and admits four
the identifier rule excludes (`phonon-frequencies:12–15`, the Grüneisen rows, `arXiv 2211.03960`).
24 − 6 + 4 = 22.

So the itemised section under the count is enumerating a set the stated rule does not define.

**What would refute it.** A statement of the identifier clause somewhere in `journals/`. I did not
find one; the clause appears only in the inherited audit note.

**Proposed correction.** Print the rule that produces the number: *"no author-year and no DOI or
arXiv identifier"*. This is a one-line edit and it makes the count checkable.

---

### F6 — The obligation-8 lookup key's first component is drawn from no vocabulary, and the same physical quantity is spelled differently per material

**Severity: high. Confidence: high (mechanical).**

`reference-battery#row-schema` states: **"Property — the canonical name from the formula registry."**

99 distinct `Property` values appear across the five files. **Four** of them appear as a `Name` in
`data/registry-manifest.csv` (`bandgap-direct`, `bandgap-indirect`, `bulk-modulus`,
`pyroelectric-coefficient`). The registry's names are formula names
(`single-mode-rta-lattice-kappa`), so the literal rule was probably never the intent — **but no
other canonical property vocabulary exists.** `registry/properties.md` is explicitly *"scope, not
inventory"*; `registry/canonical-vocabularies.md` covers theory-context axes, not observable names.

The consequence is visible in the data:

| quantity | diamond | GaN / AlN | β-Ga₂O₃ |
|---|---|---|---|
| static permittivity | `dielectric-static` | `dielectric-static-perp`, `-para` | `epsilon-static` |
| high-frequency permittivity | — | `dielectric-optical-perp` | `epsilon-infinity` |
| zero-point renormalization | `ahc-zpr-isochoric` | `ahc-zpr-isochoric` | `ahc-zpr-gap-isochoric` |
| lattice constant | `lattice-constant-a` (`material-constants.csv`) | — | `lattice-a` (`elastic-tensors.csv`) |

A lookup for `dielectric-static` returns diamond only. **Nothing in the corpus states this
mapping**, and the lattice constant additionally moves file between materials.

The reference-battery page warns about precisely this failure mode — for the *third* key component:
*"a cell naming something that record cannot hold is a row no lookup will ever match."* The same
hazard on the *first* component is unstated and present.

**The same defect on a second column.** `Source class` is drawn from no closed vocabulary either:
the schema names five classes "and so on"; **22 distinct values** appear, including `mixed`,
`derived`, `gap` and `literature-review`.

**What would refute it.** A canonical observable vocabulary I did not find, or a documented
per-material alias table. I checked `registry/properties.md`, `registry/canonical-vocabularies.md`,
`registry/observable-bundles.md` and the manifest.

**Proposed correction.** Publish one closed property vocabulary and key every row to it, carrying
anisotropy as an explicit component index rather than a name variant (see F7).

---

### F7 — Crystallographic direction is carried in the Environment column, in four notations, one of which the corpus's own frame guard forbids

**Severity: high. Confidence: high on the structure; the *labelling correctness* is a shaped gap (G2).**

`reference-battery#row-schema` states Environment is *"a serialization of the record
[crystal-inputs#environment] owns"*. That record's fields are temperature, pressure, chemical
potentials, applied electric/magnetic field, applied stress, temperature gradient, carrier
injection, radiation flux/dose, displacement threshold, vibration spectrum, `p_O2`. **It has no
field for crystallographic direction.**

Censused across all 179 rows:

| what the Environment cell holds | rows | can the record hold it? |
|---|---|---|
| a temperature alone | 90 | ✔ |
| temperature and pressure | 1 | ✔ |
| **absent** — a bare `—` | 46 | mostly defensible: fit parameters and 0 K constants are genuinely condition-independent |
| **a crystallographic direction** (`[010]`, `⊥(100)`, `[E∥c*]`) | **19** | ✘ no such field |
| **`high field`**, with or without a direction | **14** | ✘ `applied_electric_field` is a vector; this names no magnitude |
| a note about the *value* (`(near-isotropic)`, `(per-axis 3.5-3.7)`) | 2 | ✘ |
| a boundary condition on a derivative (`(total, fixed stress)`) | 2 | ✘ |
| a carrier or scattering restriction (`n<1e18`, `phonon-limited`) | 2 | ✘ |
| a field magnitude with no direction (`~150 kV/cm`) | 1 | ✘ |
| a temperature **range** (`300-500 K`) | 1 | ✘ the field is a point |
| a **difference** of two environments (`700 K vs 0 K`) | 1 | ✘ not an environment |

**42 of 179 rows — 23.5% — carry an Environment cell holding something the declared record has no
field for.** By the page's own rule, each is "a row no lookup will ever match."

The 19 direction rows are sharpest, because there the direction is the *only* thing distinguishing
rows with materially different values. Six anisotropic β-Ga₂O₃ quantities use **four different
notations** for one material: `[010]`/`[100]`/`[001]`, `⊥(100)`/`⊥(010)`/`⊥(001)`, `[a]`/`[b]`/`[c*]`,
`[E∥a]`/`[E∥b]`/`[E∥c*]`.

**Strip the direction qualifier and six (Property, Material, Environment) triples each collapse
onto multiple rows with materially different values** — 17 rows in total:

| collapsed key | values | spread |
|---|---|---|
| `impact-ionization-an` / β-Ga₂O₃ / high field | 7.9e5, 2.16e6, 7.06e5 cm⁻¹ | **3.06×** |
| `thermal-conductivity` / β-Ga₂O₃ / 300 K | 27.0, 10.9, 14 W/mK | **2.48×** |
| `breakdown-field-critical` / β-Ga₂O₃ / 300 K | 10.2, 4.8, 7.6 MV/cm | **2.12×** |
| `impact-ionization-bn` / β-Ga₂O₃ / high field | 2.92e7, 1.77e7, 2.10e7 V/cm | 1.65× |
| `epsilon-static` / β-Ga₂O₃ / 300 K | 10.2, 10.87, 12.4 | 1.22× |
| `absorption-onset` / β-Ga₂O₃ / 300 K | 4.55, 4.80 eV | 1.05× |

*(This count was re-derived with a controlled stripper after an earlier probe of mine silently
returned zero — see §5. The number in my draft was right; the probe that confirmed it was not.)*

**The corpus forbids one of these notations, in the same subject.** The accuracy-ledger's monoclinic
frame guard:

> His **plane-normal** measurements `λ₍₁₀₀₎` and `λ₍₀₀₁₎` lie along `a*` and `c*` and must
> **never** be relabelled `[100]` and `[001]`.

`transport-coefficients.csv:47–48` records `300 K [100]` = 10.9 and `300 K [001]` = 14 W/m·K — the
bare-bracket form the guard forbids — while `material-constants.csv:37–39` uses the plane-normal
form `⊥(100)`, `⊥(001)` for the same crystal.

**Proposed correction.** Move direction out of Environment into an explicit component index on the
Property (or a new column), and fix one notation.

---

### F8 — The MVP "formation energy" target is declared path-met against anchors for a different physical quantity

**Severity: high. Confidence: high (internal, decisive).**

`accuracy-ledger#mvp-targets` defines *path-met* as *"the closed-form path exists in the registry
**and** its diamond reference anchors are seeded in the machine-readable battery, so cert
obligations 4 and 8 can actually check the target"*, then states:

> | formation energy at 300 K | **±0.2 eV** | path-met — registry rows 30 and the finite-size correction 31–33; battery cohesive-energy and graphite-boundary anchors |

**The path is defect machinery. The anchors are bulk allotrope thermodynamics.**

- Registry row 30 is `defect-formation-energy`; rows 31–33 are
  `charged-supercell-extrapolation-{isotropic-cubic, planar-aligned, image-charge}` — corrections
  that exist only for charged point defects. (All four verified against `data/registry-manifest.csv`.)
- The named anchors are `cohesive-energy` diamond (7.37 eV/atom, 0 K) and
  `formation-energy-vs-graphite` (+25 meV/atom, 300 K) — bulk phase energetics.
- **The tolerance settles which quantity is meant**: ±0.2 eV matches regime row 25,
  `defect_formation_energy E_f | ±0.2 eV | finite-size charge correction mandatory`. On a bulk
  formation energy of +25 meV/atom, ±0.2 eV would be **eight times the quantity itself**.

**And there is no anchor for the actual quantity.** No CSV contains any `defect*` Property — the
99-value census confirms it. `reference-battery#contents` says so itself: *"Three sub-areas have no
file yet: … defect formation energies per host, species and charge state … Nothing reads them."*
Obligation 8 keys on (Property, Material, Environment), so **no lookup can match and the target
cannot be checked** — which is exactly what `path-met` asserts it can be.

**What would refute it.** A reading in which the row means the bulk diamond–graphite formation
energy. That fails on the tolerance and on the registry rows: the bulk quantity's registry row is
124, `tp-aware-hull`, which the CSV's own Source cell cites.

**Proposed correction.** Downgrade the row from `path-met`, or split it into a defect target that is
not path-met pending the defect file and a bulk target anchored to the two rows named, pointing at
registry row 124.

*Related, and separate:* `data/diamond-defect-corpus/index-of-all-runs.tsv` holds 199 defect runs
with `E_final_eV`, `defect_order`, `n_substituted`, `species` and `nelect` — the feedstock such an
anchor would be built from. **Nothing in `journals/` references it.**

---

### F9 — The corpus's high-temperature κ interpolation reproduces β-Ga₂O₃ and does not reproduce diamond; and the AlN rows follow a different exponent from the one their own source cell names

**Severity: high. Confidence: high (arithmetic, re-runnable). Corrects the circulated AlN figures.**

**Part one — diamond against its control.** The method as the corpus states it: take the measured
300 K value and scale as `T^−m`.

*β-Ga₂O₃ [010]* — ledger: *"the 300 K tensor scaled by its own `T^−m` with `m ≈ 1.0–1.2`, at about
±20%"*. Implied exponents from the seeded rows 46, 49, 50 (27.0 → 9 → 6):

| interval | implied m |
|---|---|
| 300 → 773 K | **1.161** |
| 773 → 1100 K | **1.149** |
| 300 → 1100 K | **1.158** |

**Three points on one power law to within 1%.** The derivation is real and it reproduces.

*Diamond* — CSV row 35's stated justification is literally `κ∝T^−1.2 consistency`. Rows 33–35
(2200 → 620 → 450):

| interval | implied m | stated law from 2200 at m=1.2 | seeded | off by |
|---|---|---|---|---|
| 300 → 773 K | **1.338** | 706.6 | **620** | **−12.3%** |
| 773 → 1100 K | **0.908** | — | — | — |
| 300 → 1100 K | 1.221 | 462.7 | **450** | −2.7% |

Applying the stated law to the stated anchor: `620 × (1100/773)^−1.2` = **406**, not 450.

**Two things follow, and the second is the physics.**

1. The endpoints are consistent with `T^−1.2` and the middle point is not. Whatever produced 620 was
   not the stated law; the Source cell's "independent est. 600–700" has no named origin.
2. **The implied exponent falls with temperature — 1.34 → 0.91 — and it must rise.** Four-phonon
   scattering steepens the high-temperature falloff, which is what registry row 121 implements and
   what F1 confirms from FLR's primary text. β-Ga₂O₃'s exponent is flat (1.16 → 1.15, no four-phonon
   regime claimed). **Diamond's runs against the physics the corpus says is at work on exactly these
   rows.**

A single power law is in any case the wrong functional form for diamond across 300–1100 K —
Umklapp, four-phonon and isotope terms have different temperature dependences.

**Part two — AlN, and a correction to the circulated numbers.** The AlN 773 K and 1100 K rows carry
Source `3-ph BTE / Slack extrapolation (theory-only)`. From the seeded 300 K anchor of **339 W/mK**:

| T | seeded | `339·(300/T)^1.0` | `339·(300/T)^1.25` | implied m |
|---|---|---|---|---|
| 773 K | **140** | 131.6 | 103.8 | **0.934** |
| 1100 K | **95** | 92.5 | 66.8 | **0.979** |
| 773 → 1100 K | — | — | — | **1.099** |

**The seeded AlN values track a plain `1/T`, not `T^−1.25`.** All three implied exponents lie in
0.93–1.10.

**The figures circulated for this finding — 98 and 63 W/mK — do not come from the corpus's seeded
anchor.** They reproduce exactly from a **320 W/mK** anchor (320 × (300/773)^1.25 = 98.0;
320 × (300/1100)^1.25 = 63.1), not from the seeded 339. The direction and the conclusion survive;
the numbers should be **103.8 and 66.8** if the corpus's own 300 K row is the anchor. Which anchor
is right depends on Slack's own 300 K value — an undergraduate is in flight on it.

*Also noted, not landed:* the β-Ga₂O₃ 773/1100 rows state they were derived from **Klimm's 24.26**,
not from the seeded 300 K value of 27.0. Both anchors give exponents inside the stated 1.0–1.2 band,
so this is a coherence note rather than a defect: rows 46 and 49–50 are not on a common anchor, and
the row says so.

**What would refute part one.** A measured diamond κ(773 K) near 620 W/m·K — then the value is right
and only its justification is wrong. That is the Olson acquisition (§4).

---

### F10 — 7.37 eV/atom is graphite's cohesive energy, carried on diamond's row — and the corpus's own two rows prove it **[internal proof + one standard constant]** **[principal: confirmed three ways; this proof is mine]**

**Severity: moderate — the value survives as a loose bound; the provenance cell does not.**
**Confidence: high. This CLOSES a declared open question rather than reporting a new defect.**

`accuracy-ledger.md:62–64` declares `diamond-cohesive-energy-allotrope` and concludes the value is
*"defensible either way"*. It is not — the corpus contains both numbers needed to decide, and it
noticed the coincidence without closing the loop:

> "24–28 meV/atom is the same size as the diamond-graphite formation-energy row it has to be
> consistent with"

**The proof, from the corpus's own two rows plus one thermochemical constant.**

- `material-constants.csv:30` — `cohesive-energy`, diamond, 0 K: **7.37 eV/atom** ± 0.05
- `material-constants.csv:31` — `formation-energy-vs-graphite`, diamond: **+25 meV/atom** ± 5
  (diamond lies *above* graphite; the sign is not in dispute — graphite is the stable allotrope at
  ambient pressure)

These two rows must be consistent. So:

| reading | what it forces | against literature |
|---|---|---|
| 7.37 is **diamond's** | graphite = 7.37 + 0.025 = **7.395** | **24 meV/atom off** |
| 7.37 is **graphite's** | diamond = 7.37 − 0.025 = **7.345** | **1 meV/atom off** |

The independent anchor: the NIST-JANAF/ATcT carbon atomization enthalpy at 0 K is 711.19 kJ/mol
*relative to graphite*, since graphite is carbon's standard reference state. Divided by
96.48534 kJ·mol⁻¹·eV⁻¹ that is **7.3710 eV/atom for graphite** — computed with no reference to the
corpus. Diamond then follows at 7.371 − 0.025 = **7.346**, which is the figure the corpus itself
quotes for diamond.

*Honesty about the anchor:* 711.19 kJ/mol is a standard thermochemical constant that I did **not**
fetch from JANAF this session — it is stated from knowledge, and it should be checked against the
table before this is applied. **The proof does not depend on its precise value.** The decisive step
is internal: the corpus's two rows differ by 25 meV/atom, and any correct pair of allotrope cohesive
energies must place graphite *above* diamond by that amount. The external constant only tells us
which of the two seeded numbers, 7.37 or 7.395, is the tabulated one — and 7.37 being a tabulated
figure is not in dispute, since the row cites a standard table for it.

**The two seeded rows are mutually consistent only under the reading that 7.37 is graphite's.**

This also explains the mechanism: Kittel's Table 1 carries one bare **"C"** row under the
standard-reference-state convention — the same convention that puts white tin in the Sn row — and
that row is graphite's. `accuracy-ledger.md:411` traces the corpus's value to "Brewer, LBL-3720,
through the standard textbook table", which is exactly that route.

**What would refute it.** A tabulation giving diamond 7.37 and graphite 7.395 at 0 K. The
thermochemistry forbids it: the two allotropes differ by ~25 meV/atom and graphite is the lower-energy
one, so any table with graphite *above* diamond has the allotropes inverted.

**Proposed correction.** The value stays — it is within σ of diamond's true 7.346 — but the Source
cell must name the allotrope, and the `Source class` of `experimental` should become
`experimental (graphite reference state, standard tabulation)`. The open question can be closed with
the derivation above. **Do not** treat 7.37 and +25 meV/atom as two independent diamond anchors in
the MVP formation-energy row (F8): under this reading they are the same measurement twice.

---

### F11 — The diamond 300 K conductivity anchor's two named measurements appear in no CSV row, and the canonical Source cell names no measurement at all

**Severity: moderate-high. Confidence: high (mechanical).**

`accuracy-ledger.md:243`, the thermal-conductivity battery, gives diamond's provenance as:

> 300 K: measured — **Inyushkin PRB 97 144305 (2018)** gives 2400 to 410 K; **Vandersande Proc.
> SPIE 2428 610 (1995)** gives 2400–2500 for type IIa

`transport-coefficients.csv:33`, which is canonical for Source cells, gives:

> `exp 2000–2500; Feng–Lindsay–Ruan PRB 96 161201 (2017); Broido APL 91 231922 (2007)`

**Neither Inyushkin nor Vandersande appears in any of the 179 CSV Source cells.** I checked all
five files for both surnames: zero hits each.

So for a row classed `experimental`, the canonical Source cell names: an unattributed experimental
range ("exp 2000–2500"), a four-phonon **calculation** (FLR 2017 — confirmed calculational from its
primary text in F1), and Broido APL 91 231922 (2007), which the corpus's own declared open question
`diamond-thermal-conductivity-citation-material` says appears to be about silicon and germanium.
**The ledger's two actual measurements are the two that did not make it into the canonical column.**

*Confirmed en route:* FLR's reference [1] is `D. A. Broido, M. Malorny, G. Birner, N. Mingo, and
D. A. Stewart, Applied Physics Letters 91, 231922 (2007), DOI 10.1063/1.2822891` — the citation
resolves and matches the CSV exactly, so the open question is about the paper's *content*, not a
broken reference. FLR's diamond experimental data (Fig. 4b) come from its refs [23] Wei 1993,
[24] Onn 1992 and [25] **Olson, Pohl, Vandersande, Zoltan, Anthony & Banholzer, PRB 47, 14850
(1993)** — confirming both that the acquisition target in §4 is real and that its author list as
recorded is exactly right.

**Three further ledger-named sources back zero CSV rows**, found by the same sweep:

| source | where named | CSV rows backed |
|---|---|---|
| **Özbek & Baliga, IEEE EDL 32 1361 (2011)** | high-field coefficients table, GaN | **0** |
| Inyushkin PRB 97 144305 (2018) | thermal-conductivity battery, diamond | **0** |
| Vandersande Proc. SPIE 2428 610 (1995) | thermal-conductivity battery, diamond | **0** |
| Dagli, Mengle & Kioupakis arXiv 1910.05440 (2019) | carrier-transport table, alloy dip | **0** |

*(Control: "Poncé" also returned zero, but only because the CSVs spell it "Ponce" without the
accent — 3 rows. That is an encoding artifact, not a finding, and it is the reason this sweep needed
checking by eye rather than by count.)*

**Proposed correction.** Add Inyushkin and Vandersande to `transport-coefficients.csv:33` and
attribute "exp 2000–2500" to them; resolve the Broido question separately.

---

### F12 — Five ledger tables carry numbers that no reference-data row can check **[principal: identified; each verified here against the 99-property census]**

**Severity: moderate. Confidence: high (mechanical).**

The reference battery exists so that obligations 4 and 8 can check ledger values. These five ledger
tables have no counterpart in any of the 179 rows — the numbers are prose only, and nothing can ever
fire on them:

| ledger table | numbers stranded | nearest CSV property | why it does not cover them |
|---|---|---|---|
| wurtzite deformation potentials, five components (`accuracy-ledger.md:304`) | **10** (GaN −5.33/−8.84/5.80/−3.09/−2.82; AlN −4.31/−12.11/9.12/−3.79/−3.23) | `deformation-potential-gap-aV` ×2 | a different quantity (the gap deformation potential a_V, from Rinke). Their source, Yan APL **95** 121111 (2009), backs zero CSV rows — the one "Yan" hit in the CSVs is Yan APL **90** 212102 (2007), a different paper on the pyroelectric row |
| piezoelectric `d₃₃/d₃₁/d₁₅` (`:320`) | **6** (GaN 2.7/−1.4/1.8; AlN 5.4/−2.1/2.9 pm/V) | `piezoelectric-e31-*`, `-e33-full` | e-coefficients are a different tensor from d-coefficients |
| alloy conductivity dip (`:374`) | **3** (minimum at x≈0.6–0.71; −46.5%; −75.8%) | `alloy-disorder-potential` ×1 | that row is Pant's disorder potential, not the dip |
| breakdown-field temperature coefficients, diamond and 4H-SiC (`:287`) | **2** (+5e−4 /K; +7e−4 /K) | `breakdown-field-slope-kBR` ×1 | seeded for **GaN only** |
| Caughey-Thomas β for the nitrides (`:287`) | **2** (GaN β=2; AlN β~2) | `caughey-thomas-beta` ×1 | seeded for **diamond only** (β=1) |

**23 numbers in canon that no gate can reach.**

**What would refute it.** A sixth CSV file, or a property I mis-mapped. The 99-property census is in
§6 and is re-runnable.

**Proposed correction.** Either seed these into the battery, or mark them explicitly as
un-checkable prose so the gap is visible rather than implied.

---

### F13 — Uncertainties as a class: three self-contained defects, no literature required

**Severity: moderate. Confidence: high — each row contradicts its own contents.**

**F13a — A σ that does not cover the spread the same cell reports.** `phonon-frequencies.csv:18`,
`debye-temperature` β-Ga₂O₃: Value 738 K, Uncertainty 150 K (1σ band **[588, 888]**), Source
*"Guo APL 106 111909 (2015) calorimetric Debye fit; **literature spread 420–870** (FP 872, He et al.
2006); Mengle–Kioupakis 2019 concur"*.

**The stated spread runs to 420 K. The stated 1σ band stops at 588 K.** The lower 168 K of the
disagreement the cell reports lies outside the uncertainty the cell declares. The cell attributes
its upper end and leaves the 420 unattributed — so either values were deliberately excluded, and
the exclusion belongs in the cell, or the σ is too tight by its own evidence. Consequence is on the
**error budget, not the gate**: at 3σ the band covers the spread, but the schema declares
Uncertainty to be the **one-sigma** band and it is the 1σ value that `Quantity.combineTol` composes.

**F13b — The Debye rows widen σ to bracket the disagreement they name; the one row that names no
disagreement and no source has the tightest σ by a factor of three.**

| material | value | σ | σ/value | what the Source cell names |
|---|---|---|---|---|
| GaN | 600 K | 40 K | 6.7% | Slack estimate; Zheng 2019 cites **636** — 0.9σ away |
| AlN | 1000 K | 80 K | 8.0% | Wang–Zhao measured **971**; DFT 950–1050 — σ brackets both |
| β-Ga₂O₃ | 738 K | 150 K | 20.3% | spread **420–870** — σ does *not* bracket it (F13a) |
| **diamond** | **2200 K** | **50 K** | **2.3%** | *"curated MVP anchor"* — **no source, no disagreement named** |

Two of the sourced rows also seed a number that is not the measurement they cite: GaN seeds 600
while citing 636; AlN seeds a round 1000 while its measurement is 971. Both inside σ, so neither is
wrong — but both are curators' round numbers and the cells do not say so.

*On diamond:* see N1 — 2200 ± 50 is defensible for the **T → 0** Debye temperature. The defect is
that the row declares **no method and no temperature** and is consumed in a high-temperature
criterion.

**F13c — An uncertainty transplanted from a different material's row, and load-bearing as a gate.**
`transport-coefficients.csv:66`, `mobility-electron-best-exp` GaN, 1265 cm²/Vs, `×0.15`, class
`experimental`. Its Source cell says in full that the value was quoted as a **comparison** against
Poncé's 1034 first-principles ceiling, not as an independently cited measurement, and that
**"Sigma carried from the sibling AlN best-exp row pending its own pin"**.

1. **The row is classed `experimental` and cites no measurement.** The only paper named is
   first-principles. The sibling AlN row (`transport:13`, 426 cm²/Vs) *does* carry a real
   measurement — Taniyasu, Kasu & Makimoto, APL 89, 182112 (2006).
2. **The σ is not an uncertainty on this value.** Under `τ_battery = 3σ` that placeholder sets this
   row's acceptance gate at ±45%.

A placeholder σ is the cleanest instance of the class: a number in the uncertainty column that
measures nothing about the value beside it, which the gate consumes as though it did. **The honesty
of the cell is what makes it findable — and nothing downstream reads prose.**

---

### F14 — A registry formula's declared input is seeded nowhere, and the columns that could recover it carry no validity temperature

**Severity: moderate. Confidence: high on what survives; I killed the stronger version myself.**

`data/registry-manifest.csv` row 120, `ahc-gap-renormalization`, declares
`(ZPR, Θ, T, ε) → ΔE_g(T)` with `ΔE_g = ZPR·coth(Θ/2T)`.

**Θ is an explicit input.** The ledger's curated table for row 120 seeds, per material, the
isochoric ZPR, the lattice term, the total, `dE_g/dT e-ph`, the `slope-kind` tag and the source. It
does not seed Θ. Neither does any of the five CSVs. I grepped `journals/` and `data/` for `coth`,
Einstein temperature, effective phonon temperature: **five prose mentions of the formula, no value
for Θ anywhere.** The ledger describes the seeded quantity as *"the `coth` **amplitude**"* — exactly
right, and exactly the point.

**Θ is in principle recoverable** from the two seeded columns, since at high temperature
`coth(Θ/2T) → 2T/Θ` and `dE_g/dT → 2·ZPR/Θ`. But the ledger never states **at what temperature its
`dE_g/dT` is quoted**, and the answer moves with it:

| material | ZPR (meV) | dE_g/dT (meV/K) | Θ, high-T asymptote | k_BΘ | Θ if read at 600 K | k_BΘ | highest seeded phonon energy |
|---|---|---|---|---|---|---|---|
| GaN | −189 | −0.45 | 840 K | 72.4 meV | 741 K | 63.8 meV | 92.1 meV |
| AlN | −399 | −0.55 | 1451 K | **125.0 meV** | 1103 K | 95.1 meV | **113.6 meV** |
| diamond | −345 | −0.45 | 1533 K | 132.1 meV | 1143 K | 98.5 meV | 165.0 meV |
| β-Ga₂O₃ | −200 | −0.90 | 444 K | 38.3 meV | 426 K | 36.7 meV | — |

**The stronger finding I tried to land and could not.** On the asymptotic reading, AlN's implied
effective phonon energy is 125.0 meV — above AlN's own seeded maximum of 113.6 meV
(`phonon-frequencies.csv:9`, Davydov 1998). An effective single-oscillator energy is a weighted
average over the spectrum and cannot exceed its maximum, so that reading would be unphysical. **But
on the 600 K reading it is 95.1 meV and perfectly physical.** The corpus does not say which reading
is meant, so I cannot call AlN's pair inconsistent — and I am not going to.

**What survives** is the missing parameter and the missing validity temperature: a formula whose
fourth argument has no seeded value, and a slope column with no stated temperature, in a table whose
whole purpose is to be the curated seed for that formula.

**Proposed correction.** Seed Θ per material as its own row. Deriving it from a slope discards the
information about how good the single-oscillator fit is.

---

### F15 — The strain dataset's triple-counted shapes are not a diffuse over-weighting; they are exclusively the anharmonic shear tail

**Severity: moderate. Confidence: high (arithmetic on the shipped file, re-runnable).**

The corpus states the consequence generically — `build-verification.md:106`: *"Left in, those 24
shapes carry triple weight in any fit."*

**The 24 shapes are not a random 2% of the data.** Parsing
`data/diamond-strain-sweep/index-of-all-runs.tsv`:

- All 24 are **pure single-plane shears** — zero stretch on every axis, exactly one non-zero skew.
- All 24 sit at **|γ| ∈ {0.025, 0.050, 0.075, 0.100}**.
- **Not one is inside the corpus's own linear-response window.** `04-…:100–103` states *"Family 4's
  finest step (0.025) sits **outside** the |γ| ≤ 0.02 linear-response window … Use family 3 for
  C44."* The smallest duplicated |γ| is 0.025.

In the pure single-plane-shear sector (120 distinct shapes, 168 rows):

| | distinct shapes | rows as shipped |
|---|---|---|
| \|γ\| ≤ 0.02 — linear-response core | 24 | 24 |
| \|γ\| > 0.02 — anharmonic tail | 96 | 144 |
| **anharmonic : linear ratio** | **4.0** | **6.0** |

**Naive fitting inflates the anharmonic tail against the linear core by 1.5×, in the family the
corpus designates for C₄₄.** A reader told "24 of 1131 shapes at triple weight" concludes the effect
is ~2% and diffuse. It is a 50% reweighting concentrated on one elastic constant — compounding a
bias the same page already quantifies, that fitting without the reference-offset linear term
*"biases **C44 by 15%**"*.

**Proposed correction.** State the consequence directionally rather than as a row count.

---

### F16 — The de-duplication guidance has a second failure mode, in the opposite direction and undocumented, that silently destroys the equation-of-state family

**Severity: moderate-high. Confidence: high (arithmetic on the shipped file, re-runnable). New — found while re-verifying my own transcript, which was wrong about this.**

`build-verification.md:109–123` gives the de-duplication instruction:

> **De-duplicate before any fit, and de-duplicate on the manifest's own `duplicate_group`
> column.** Naming the column is not pedantry — **it is the only method that works**, and the
> obvious alternative fails *silently* … Sorting the geometry columns for unique rows therefore
> returns all 1,179 and reports the data clean. A careful person doing the sensible thing gets the
> wrong answer and no warning. **The `duplicate_group` column is the key; the coordinates are not.**

**Both halves of "it is the only method that works" are false, and the second failure is worse than
the one documented.**

The manifest has **seven** geometry columns, not six: `target_cell_volume_in_cubic_angstroms` plus
the three fractional stretches and three skews. What the key includes decides the answer:

| de-duplication key | distinct rows | verdict |
|---|---|---|
| raw *text* of the geometry columns | **1179** | the documented trap — finds nothing ✓ as described |
| raw text of geometry + shape-change kind | **1179** | ✓ as described |
| `duplicate_group` | **1131** | ✓ correct |
| **numeric, volume + six strain components** | **1131** | ✓ **also correct — so it is not "the only method that works"** |
| **numeric, the six strain components alone** | **1085** | ✘ **wrong by 46, and undocumented** |

**Why the six-component key fails, in the manifest's own words.** The preamble of
`index-of-all-runs.tsv` states the column semantics:

> ```
> target_cell_volume_in_cubic_angstroms  only for scale-all-axes-uniformly; blank elsewhere
> fractional_stretch_along_[xyz]_axis    fractional length change. blank = axis not stretched.
> ```

So the volume column is the **sole geometric descriptor of one of the nine families**, and it is
blank for the other eight. The entire `scale-all-axes-uniformly` family — **47 runs**, target volumes
10.05 to 12.35 Å³ in steps of 0.05 — therefore carries **all six strain components exactly zero**.
Those runs are hydrostatic: they are distinguished *only* by the volume column. Key on the strain
tensor and all 47 collapse to one, losing 46. The arithmetic closes exactly:
1179 − 46 − 48 = **1085**.

**This is the opposite error from the documented one, and it is the more damaging.** The documented
trap under-reports: it leaves 48 surplus rows in, and the page quantifies the cost as triple weight
on 24 shapes (F15). This one over-reports: it deletes 46 rows that are not duplicates at all — and
they are precisely the **equation-of-state family**, the runs from which the bulk modulus and the
`E(V)` curve are derived. A fit built on the collapsed set has no volume sweep left.

**And the page's own wording points the reader at it.** "The coordinates are not [the key]" is what a
reader takes away; for a strain sweep, "the coordinates" naturally means the strain tensor. A reader
who accepts the warning, abandons textual sorting, and switches to a numeric key on the strain
components has done exactly what the page asked and has silently destroyed the hydrostatic family.
`read-me-first.md:43` does list the volume sweep as `V = 10.05…12.35 Å³, step 0.05, 47` — so the
information exists, one file away, and nothing connects it to the de-duplication instruction.

**What would refute it.** A statement that the volume column is part of "the geometry columns" for
de-duplication purposes. `build-verification.md` names no columns; `02-how-to-read-and-derive.md:158`
gives only the `duplicate_group` recipe.

**Proposed correction.** Two edits. Replace "it is the only method that works" with the true claim —
*de-duplicate on `duplicate_group`, or on all seven geometry columns parsed numerically; the volume
column is one of them*. And state the second failure explicitly: *keying on the six strain
components alone collapses the 47-run uniform-scaling family to a single row, because that family
is hydrostatic and carries zero strain.*

---

### F17 — Minor: four small defects that do not move a physical conclusion

| # | claim | location | what I get |
|---|---|---|---|
| F17a **[principal: confirmed]** | *"mis-states the intrinsic carrier density by a factor 11 at 800 K"* | `accuracy-ledger` regime row 15 | `exp(345 meV / 2k_B·800 K)` = **12.2096**, not 11. (11 corresponds to 331 meV, or to 835 K at 345 meV.) **And the direction is unstated**: since the ZPR is negative the renormalized gap is smaller, so omitting the correction **understates** n_i by 12.21×, it does not overstate it |
| F17b | *"The same directory carries the **cert reference cache**"* | `reference-battery#contents` | `data/reference-data/` contains the five CSVs and nothing else. Stated in the present tense as a filesystem fact |
| F17c | `bulk-modulus` diamond, 442 ± **4** GPa, derived as `(C₁₁+2C₁₂)/3` | `elastic-tensors.csv:20` | ±4 GPa is the **independent-error** propagation of ±5 on C₁₁ and C₁₂ (3.73). Both come from one measurement, one sample, one method (McSkimin & Andreatch 1972), so the errors are correlated; conservative propagation gives **5.0 GPa**. The σ is not wrong — it assumes an independence the measurement does not have |
| F17d | `mass-density` diamond, 3.515 ± **0.001** g/cm³, Source `standard` | `elastic-tensors.csv:21` | Reproduced exactly by `8M/(N_A a³)` with **natural-abundance** M = 12.011 (3.5157). Pure ¹²C gives 3.5125 — a difference of **0.0032, three times the stated σ**. The row is implicitly natural-abundance and does not say so, in a corpus whose diamond conductivity anchors are isotope-sensitive |

---

## 2 · Findings that did not survive

**This is where the sweep is shown to be real.**

### N1 — *"the elastic route gives Θ_D ≈ 1860 K"* — refuted by computation, and the real defect is a different one **[my correction; adopted by the principal]**

`audit/inherited/leads/diamond.md` §6 and the declared `diamond-debye-temperature-unseeded` question
both rest on a literature spread of **1860 K (elastic constants) to 2230 K (low-temperature specific
heat)**. That attribution is the load-bearing half of the claim that ±50 K is narrower than the
disagreement between methods.

**I computed the elastic Debye temperature from the corpus's own seeded constants** — C₁₁ = 1079,
C₁₂ = 124, C₄₄ = 578 GPa (McSkimin & Andreatch 1972), ρ = 3.515 g/cm³, M = 12.011 — via
Voigt–Reuss–Hill and the Anderson mean-sound-velocity formula:

| average | v_L (m/s) | v_T (m/s) | v_m (m/s) | Θ_D |
|---|---|---|---|---|
| Voigt | 18162 | 12369 | 13484 | **2250.7 K** |
| Reuss | 18113 | 12315 | 13428 | **2241.4 K** |
| Hill | 18137 | 12342 | 13456 | **2246.1 K** |

To land on 1860 K the mean sound velocity would have to be 17.2% below what the corpus's own elastic
constants give.

**This is the physically expected result.** At T → 0 only long-wavelength acoustic phonons are
excited, and those are what the elastic constants describe — so the elastic and low-temperature
calorimetric Debye temperatures must agree. They do, at ~2240 K, and the calorimetric cluster is
2219 ± 20. **The seeded 2200 ± 50 K is well supported as a T → 0 Debye temperature.**

**What this does not rescue.** The row states **no method and no temperature** — its Environment cell
is a bare `—` — and it is consumed in a criterion about *high-temperature* behaviour, where the
T → 0 value is the wrong one. So the defect is real but it is **not** the one registered: it is a
missing method/temperature qualifier and a category mismatch at the consumer, not an over-tight σ.

*Precision, so this is not read as more than it is:* **all four** `debye-temperature` rows carry a
bare `—` Environment cell, not just diamond's. What is specific to diamond is the consumer — it is
the only one of the four feeding a high-temperature validity criterion — and the Source cell, which
alone among the four names neither a measurement nor a disagreement (F13b).

**And F1 supersedes the consumer entirely**: the recommended fix is to drop Θ_D from the four-phonon
criterion and use FLR's own 900 K, which removes the dependence on this row.

### N2 — *"the coordinates are not the key"* — filed as a near-finding in the draft; **it did not survive as a near-finding either, and became F16**

This entry is retained to record how the reasoning moved, because the movement is the point.

The draft's position was: numeric de-duplication *does* work, so "the coordinates are not the key" is
over-general, but it errs in the safe direction — it pushes readers onto a method that always works —
so it should not be landed.

**That position rested on a numeric key I had not fully specified, and it was wrong.** The manifest
has seven geometry columns, not six. On the full seven-column key numeric de-duplication gives 1131
and the draft's claim holds. On the six *strain* columns — the natural reading of "the coordinates"
for a strain sweep, and the one the page's own warning steers a reader toward — it gives **1085**,
silently deleting the entire 47-run hydrostatic family.

So the sentence does not err in the safe direction. It errs in the direction of the worse failure,
and the failure is undocumented. It is now **F16**, at moderate-high severity.

**The generalisable lesson**, which is why this entry stays: I dismissed the item on a judgement
about *direction of error* without having enumerated the ways a reader could instantiate the method I
was comparing against. "Numeric de-duplication works" was true of one key and false of another, and
I had checked only the one that made the corpus look wrong in a harmless way.

### N3 — `phonon-max-energy`'s wrong-consumer finding lost its consumer in the restructure

`leads/diamond.md` §7 establishes that the diamond `phonon-max-energy` row is named for the
dispersion maximum but seeded with the **zone-centre** Raman value (165.21 meV), while diamond's LO
branch overbends ~1.5 meV above Γ — so the true maximum is ~166.7 meV, three times the row's σ above
its value. The ledger reproduces this itself, so the corpus already knows.

The lead's *consequence* was that a deleted chapter fed `ω_phonon = 165 meV` into
`v-sat-intervalley`. **That consumer no longer exists.** Registry row 18 has signature
`(Δ_valley, m*_valleys) → v_sat` — no phonon energy at all. I grepped `journals/` and `data/` for
`phonon-max-energy` and `165 meV`: the only hits are the ledger's own note.

So the naming defect is real and documented, but it has **no downstream consequence** — which
changes its severity from "a formula is being fed the wrong quantity" to "a row's name does not
describe its value".

### N4 — the registry manifest's `Depends on` column does not resolve, and that is not a defect

209 dependency tokens in `data/registry-manifest.csv` match no `Name` in the manifest. I expected a
dangling-reference finding. They are **physical input symbols** — `bands`, `μ`, `n`, `ω_LO`, `m*`,
`T`, `E` — not formula references. The column legitimately carries both "the output of another
registry row" and "a primitive input".

What is true, and belongs to whoever owns the registry: **the column cannot be mechanically resolved
into a dependency graph**, because the two vocabularies are not distinguished and no symbol table
for the primitive inputs exists. Reported, not chased.

The manifest is structurally clean: 134 rows numbered 1..134, no gaps or duplicates, no duplicate
`Name`; the only rows lacking Bundle/Tier/Diff/Path are 103 and 104, both explicitly architectural.

### N5 — the formation-energy reading ambiguity does not propagate to the hull verdict

The inherited lead establishes that `formation-energy-vs-graphite` = +25 ± 5 meV/atom matches none of
its three defensible readings (ΔH 19.6, ΔG 30.1, Berman–Simon P·ΔV 29.8) within σ.

**But the downstream consequence is nil.** The row's Source cell justifies it as *"consistent with
tp-aware-hull (registry row 124) reading R=0 inside δ_meta"*, and `cert-obligations.md` sets
`δ_meta = 50 meV/atom`. All candidate readings — 19.6, 25, 28, 29.8, 30.1 — sit inside 50. **The
choice of thermodynamic potential does not change the hull verdict.** Any severity here is on
provenance grounds alone.

*Note the interaction with F10:* the 0 K diamond–graphite difference implied by the thermochemistry
is 25.1 meV/atom, which is the seeded value exactly. So the row is defensible as a **0 K** quantity
while being labelled 300 K — which is a fourth reading nobody enumerated, and the one that makes the
number land.

### N6 — `Arabov arXiv 2603.29484` is real **[principal: checked]**

Registered here so it is not re-investigated. The citation was checked and resolves. It is **not** a
finding, and it must not be carried as one in a corpus whose history includes a fabricated citation.

### N7 — the "citation bleed" on the isochoric ZPR row does not survive as stated **[correcting a principal item]**

The claim as circulated: one source cited for an *isochoric* renormalization is "an empirical
total-shift measurement". I checked the citation against Crossref.

`material-constants.csv:40` cites **Lee et al., APL Materials 11, 011106 (2023)** for
`ahc-zpr-gap-isochoric` at −0.19 ± 0.05 eV. The record resolves exactly: DOI 10.1063/5.0131453,
APL Materials, volume 11, issue 1, **article number 011106**, January 2023, Channyung Lee, Nathan D.
Rock, Ariful Islam, Michael A. Scarpulla, Elif Ertekin — *"Electron–phonon effects and
temperature-dependence of the electronic structure of monoclinic β-Ga₂O₃"*. Its abstract states it
evaluates *"band edge shifts from lattice thermal expansion and phonon-induced lattice vibrations"*
across 0–900 K, computationally **and** experimentally.

So the paper **explicitly decomposes** expansion from phonon renormalization, which means an
isochoric component is well-defined in it and citing it for one is not prima facie wrong. The
citation is real, correctly paginated, and about the right quantity. **I am not landing this.**

What remains open is narrower and is a shaped gap (G4): whether Lee's −0.19 eV is the isochoric
component or the total. The adjacent row 41 (`bandgap-shift-total-700K`, −0.45 eV) already carries
an explicit "NOT isochoric-only; do not compose" guard, so the corpus is alert to the distinction on
the neighbouring row.

---

## 2b · Triage of the inherited contradictions in my subject

The brief requires triaging `audit/inherited/contradictions.md` before using it, because the corpus
was rewritten since it was collected. **Eight of the 89 fall in my subject. Six are dead, one is
alive and folded in, one is answered by being unanswerable.**

`journals/.../11.5-deriv-high-field.md` no longer exists — I confirmed it is absent from the tree.
Every contradiction with that page on one side has lost that side.

| # | subject | verdict |
|---|---|---|
| **C8** GaN κ(300 K): 130 vs the CSV's 240 | dead — source page deleted. The CSV's 240 stands with a first-principles source and a measured comparison |
| **C9** diamond κ(T) monotonicity | **dead as a contradiction, alive as evidence** — folded into G1 below |
| **C10** β-Ga₂O₃ κ as scalar vs tensor | dead as stated; the *live* form is F7 — the tensor is seeded per direction, but the direction lives in a column that cannot hold it |
| **C12** β-Ga₂O₃ displacement threshold, circular provenance | **alive and extended** — this is F4, which adds the migration and the three-way seeded/UNSEEDED/retired disagreement |
| **C13** GaN deformation potentials: `Ξ_c − Ξ_v ≈ −11` vs `a_V = −7.6` | **answered by being unanswerable, and that is the finding.** The contradictions file addresses this to auditor 2 by name. One side is deleted. The surviving side — the ledger's five-component wurtzite table — is **prose-only with no CSV counterpart (F12)**, so nothing consumes it and no gate can check it. The convention question (whether `a_V` and a `Ξ_c − Ξ_v` difference are the same object) cannot arise until those numbers are seeded, and needs Yan APL 95 121111 (2009) if they ever are. **Recorded as a precondition on F12's correction: do not seed the five-component set without settling the convention first.** |
| C7, C11, C14 | not my subject — fatigue formulas, residual kinds, state-vector verdicts. Reported to the principal, not chased |

Two further entries touch the battery's *structure* rather than its values — a README the directory
does not contain, and an eight-file listing against five files on disk. Both are structure, which is
auditor 1's finished subject; the per-file counts in the **current** `reference-battery` page match
disk exactly (§6). The only residue in my subject is F17b, the "cert reference cache" claim.

---

## 3 · Shaped gaps

### G1 — the diamond κ measurement at 773 K and 1100 K

| part | content |
|---|---|
| **what it would settle** | What is the measured thermal conductivity of natural type IIa single-crystal diamond at 773 K and at 1100 K? |
| **the conclusion without it** | **620 W/m·K at 773 K is not what the corpus's own stated method produces.** `κ ∝ T^−1.2` from the 2200 anchor gives **707** at 773 K and **463** at 1100 K. The 1100 K row reproduces to 2.7%; the 773 K row is 12.3% low and sits on no single power law with the other two (F9). The same method on β-Ga₂O₃ produces three points on one exponent to 1%, so the method is not the problem. FLR's Fig. 4b plots measured diamond κ across this range from Olson 1993, Onn 1992 and Wei 1993 — the data exist and are standard. **Two further estimates bracket the CSV in opposite directions**, which is why this cannot be settled by argument: Vandersande, *Proc. SPIE* **2428**, 610 (1995) via OSTI 552238 gives 400–500 W/m·K at 1273 K, *above* the CSV's extrapolation there (~395); while the now-deleted high-field page recorded κ(900 K) ≈ 400 and κ(1200 K) ≈ 280, which is 22% and 31% *below* the CSV's two rows when evaluated on the CSV's grid (483 and 312). Notably that deleted curve follows `T^−1.24`, i.e. it obeys the canonical `T^−1.2` law the CSV's own rows do not. Its numbers are weak evidence — the page was deleted for being unsourced — but its *shape* is the shape the corpus claims. |
| **the branches** | **≈620 at 773 K:** the value stands, only its justification string is wrong; F9 shrinks to a provenance fix. **≈700 at 773 K:** the row is wrong by 12% and the stated law was right; the row moves and `theory-interpolation` becomes correct. **Materially lower than 620:** both high-temperature rows move, and F3 becomes the explanation for why nobody noticed — the gate on those rows cannot fail low. |
| **what depends on it** | F9 part one in full. The severity, though not the existence, of F3 on rows 34–35. The open questions `diamond-thermal-conductivity-provenance` and the ledger/CSV source disagreement (F11). **Not** F1 — the four-phonon threshold is now settled from FLR's primary text and holds whatever Olson says. |

### G2 — whether Guo 2015 measured crystallographic directions or plane normals

| part | content |
|---|---|
| **what it would settle** | Are the β-Ga₂O₃ conductivity values labelled `[100]` and `[001]` measurements along those crystallographic directions, or along the plane normals `a*` and `c*` (13.83° away)? |
| **the conclusion without it** | Undetermined. The corpus uses the bare-bracket notation its own frame guard forbids for exactly this quantity, and the plane-normal notation for the permittivity rows of the same crystal. The structural defect (F7) stands regardless. |
| **the branches** | **True directions:** the labels are right and F7 reduces to a notation and key-placement defect. **Plane normals:** the values are attached to the wrong directions in a material with 2.5× anisotropy, and this is the relabel the corpus explicitly forbids — a false-claim finding on two seeded rows. |
| **what depends on it** | The *labelling* half of F7 only. The structural half — 42 of 179 Environment cells — is independent. |

### G3 — the FLR supplemental material

| part | content |
|---|---|
| **what it would settle** | Does the supplemental material of Feng, Lindsay & Ruan, PRB 96 161201(R) (2017) state a Debye-fraction validity criterion for the four-phonon correction? |
| **the conclusion without it** | **No such criterion exists in the main text** — zero occurrences of "Debye" across 5,230 extracted words, controlled by locating both of the paper's substantive diamond claims verbatim. The paper states per-material temperatures instead (900 K diamond, 600 K silicon), and those two numbers correspond to Debye fractions of 0.41 and 0.93 — so a universal 0.4 rule is refuted by the paper's own data whatever the supplemental says. |
| **the branches** | **If the supplemental states a 0.4 Θ_D criterion:** the attribution is correct and F1 reduces to "the criterion is contradicted by the paper's own silicon result", which is still a defect but a smaller one. **If it does not:** F1 stands in full and the criterion is manufactured. |
| **what depends on it** | The *attribution* half of F1. The *falsification* half — 0.4 × 645 = 258 K against FLR's stated 600 K for silicon — is independent and stands either way. |

### G4 — what Lee 2023's −0.19 eV denotes

| part | content |
|---|---|
| **what it would settle** | Is the −0.19 ± 0.05 eV that `material-constants.csv:40` attributes to Lee et al. the **isochoric** (clamped-cell) zero-point renormalization, or a total shift including thermal expansion? |
| **the conclusion without it** | The citation is real and correctly paginated (N7), and the paper explicitly decomposes expansion from phonon renormalization, so an isochoric component is well-defined in it. No defect is established. |
| **the branches** | **Isochoric:** no finding; the row is correct. **Total:** the row double-counts against the strain path, which is exactly the hazard the `slope-kind` tag and row 41's "do not compose" guard exist to prevent — a composition-refusal defect on a row that passes the guard. |
| **what depends on it** | Nothing else in this file. Isolated. |

---

## 4 · Acquisition requests

### 1 · Olson, Pohl, Vandersande, Zoltan, Anthony & Banholzer, PRB 47, 14850 (1993)

"Thermal conductivity of diamond between 170 and 1200 K and the isotope effect."
DOI 10.1103/PhysRevB.47.14850. **Author list and citation confirmed** as FLR's reference [25].

| part | content |
|---|---|
| **what it would settle** | Measured κ of natural type IIa single-crystal diamond at 773 K and 1100 K. |
| **the conclusion without it** | 620 and 450 W/m·K are **unverified**. The CSV's three values are not self-consistent under any single power law (implied exponents 1.34, 0.91, 1.22), and the stated law applied to the stated anchor gives 406, not 450. |
| **the branches** | See G1. |
| **how many findings wait on it** | F9 part one; the severity of F3 on two rows; two declared open questions. |

### 2 · Slack, Tanzilli, Pohl & Vandersande, J. Phys. Chem. Solids 48, 641 (1987)

| part | content |
|---|---|
| **what it would settle** | Two separable things: (a) does the paper report single-crystal AlN κ above 500 K, which would falsify the absence claim on `transport-coefficients.csv:43`; (b) what exponent does it state for the high-temperature falloff, which decides whether the seeded 140/95 are defensible. |
| **the conclusion without it** | (a) **The absence claim is already internally contradicted**: the same file's 300 K row (`transport:24`) cites this exact paper. That contradiction needs no acquisition and is a declared open question (`aln-high-temperature-conductivity-absence`). (b) The seeded values track `T^−1` (implied exponents 0.93, 0.98, 1.10), not the `T^−1.25` a Slack extrapolation would imply. |
| **the branches** | If Slack measured to ~1800 K, the absence claim is simply false and the rows should cite the measurement. If the stated exponent is 1.25, the seeded 140/95 are too high — from the seeded 339 anchor, `T^−1.25` gives **103.8** and **66.8**. |
| **how many findings wait on it** | F9 part two. An undergraduate is in flight. |

### 3 · Vurgaftman & Meyer, J. Appl. Phys. 94, 3675 (2003), the AlN effective-mass table

| part | content |
|---|---|
| **what it would settle** | What experimental spread the paper reports for AlN electron effective mass, and whether its recommendation is experimental or theoretical. |
| **the conclusion without it** | `material-constants.csv:11–12` seed 0.32 and 0.33 m₀ at ±0.03, class **`experimental-review`**, citing this paper. ±0.03 on 0.32 is ±9.4%. If the paper's experimental data span 0.29–0.45 as reported to me, the half-width is ±0.08 on a midpoint of 0.37 — ±22%, so the seeded band is **2.3× tighter**, not sevenfold; I could not reproduce the sevenfold figure and do not carry it. |
| **the branches** | If the recommendation is a theory-convergence figure, the `experimental-review` class is wrong and the σ is tightened in the dangerous direction. If experimental values genuinely cluster near 0.32, the rows are fine. |
| **how many findings wait on it** | One potential finding, not yet landed. An undergraduate is in flight. |

### 4 · Feng, Lindsay & Ruan, PRB 96 161201(R) (2017), **supplemental material only**

Cheapest item on this list; the main text is already read and is open access via OSTI 1427696.
Settles G3. Note that F1's falsification half does not wait on it.

---

## 5 · Calibration result — as found

**6 of 8 planted defects caught, and one of the six only as an uncaught exception.**

I wrote my strain-dataset method as a standalone checker, confirmed it reports **zero** findings on
the clean file, then planted eight defects in scratch copies and re-ran it.

| # | planted defect | caught? |
|---|---|---|
| D1 | one row deleted | ✔ row count and both distinct-counts |
| D2 | one member's `duplicate_group` marker blanked | ✔ group size 2, and geometry/group disagreement |
| D3 | one triplicate perturbed geometrically | ✔ geometry/group disagreement |
| D4 | `recovery_status` set to `partial` on one row | ✔ |
| D5 | a geometry cell corrupted to non-numeric | ✔ **but as an uncaught `ValueError`, not a reported finding** |
| D6 | a duplicated shape's γ moved inside the linear-response window | ✔ |
| D7 | `source_archive_file` pointed at the wrong archive | ✘ **missed** |
| D8 | `kind_of_shape_change` mislabelled | ✘ **missed** |

**What the misses mean.** My method is a geometry-and-duplicate-structure checker. It never reads
the provenance columns and never cross-checks the family label against the geometry. **Anything I
certify clean about the strain data is certified on counts, geometry and duplicate structure only.**

I then closed both misses by writing the checks they exposed and running them on the real data (§6).
Both pass. **That does not upgrade the calibration** — it measured the method as it stood when I used
it, and it was a six-of-eight gate.

### A ninth result, found after the fact: one of my probes was broken and returned a clean zero

Re-running my own draft's key-collision claim, my collision probe reported **0 collisions** — a clean
result that would have retracted a finding. The probe stripped bracket *characters* (`[`, `]`) rather
than bracketed *content*, so `300 K [010]` became `300 K 010]` and never collided with anything.
With a controlled stripper — whose output on all 19 direction rows I printed and checked before
trusting the count — the answer is **6 collisions covering 17 rows**, which is what the draft said.

**The draft number was right and the probe that "confirmed" it was not.** This is the second instance
in this audit of the rule that every negative needs a control, and it is the reason F7's count is
shown with its stripper output in §6 rather than as a bare number.

### A tenth result: re-verifying a line I had already certified produced a new finding

Re-running the strain dataset's distinct-shape count, my own transcript line —
*"1131 by `duplicate_group`, 1131 by numeric geometry ✓ the two agree"* — **failed to reproduce**,
returning 1085. The line had never said which columns "numeric geometry" meant. Chasing the 46-row
gap produced **F16**, the audit's only finding in the class the brief names as this corpus's
signature form: an instruction a careful reader follows correctly and still gets the wrong answer.

**This is the strongest argument in this file for re-verifying clean verdicts rather than trusting
them.** A transcript line marked ✓ concealed both an under-specified method and an undocumented
data hazard, and only re-running it — not re-reading it — exposed either. The brief's rule is
*re-verify values, never verdicts*; this is that rule applied to my own verdicts, and it paid.

**Revised calibration statement.** I re-ran every line of my own §6 transcript this session.
**Three of them did not survive re-running as stated:**

| transcript line | what was wrong | outcome |
|---|---|---|
| key-collision count | the stripper removed bracket *characters*, not bracketed *content*, so it returned a false zero | number was right; probe was not |
| distinct shapes "1131 by numeric geometry" | never said which columns; on the six strain columns it is 1085 | **became F16** |
| "all 24 registry row numbers resolve" | the manifest has no gaps in 1..134, so resolution is near-vacuous; the count was also wrong | claim narrowed to the six rows actually verified |

**Three of the checks I certified clean were produced by methods that could not have supported the
certification.** Two had the right answer underneath; one concealed a finding. The gate on my own
transcript is therefore materially weaker than the six-of-eight above suggests, and I am reporting
that rather than resolving it in my favour. Every §6 line now states the method precisely enough to
be re-run and disagreed with.

### What was not calibrated

I did **not** calibrate the reference-data findings (F2–F8, F10–F13, F15) by planting defects,
because none is a search over many rows for an anomaly — each is a single stated claim compared
against a single computable fact, shown inline and re-runnable. The systematic row-sweep that *does*
need calibration is the uncertainty-encoding census, and it is now backed by the full 179-row
enumeration in §6 rather than by sampling.

**No arm of my calibration was blind.** Every defect above was planted by me, in a file whose
structure I already knew. A blind arm remains owed.

---

## 6 · Evidence transcript — what I am calling clean, and what I actually compared

**No free emptiness.** Each line is a check that passed, with the comparison made.

### Strain dataset (`data/diamond-strain-sweep/`)

| check | result |
|---|---|
| row count | 1179 data rows ✓ matches the header and `build-verification.md:104` |
| distinct shapes | 1131 by `duplicate_group`; 1131 by numeric geometry **on all seven geometry columns**; **1085** on the six strain columns alone ✗ — the first two agree, the third does not, and the discrepancy is F16. **My draft certified this line without stating which columns the numeric key used**, which is exactly the ambiguity the finding is about |
| duplicate structure | 24 groups, **all** of size 3, 72 rows ✓ matches the header |
| textual-dedup trap | raw-text geometry dedup returns 1179 ✓ the documented trap is real |
| the volume family | `scale-all-axes-uniformly` is 47 rows, all six strain components exactly zero, 47 distinct target volumes 10.05–12.35 Å³ ✓ matches `read-me-first.md:43`; it is the reason the six-column key fails |
| `recovery_status` | `complete` for all 1179 ✓ |
| family labels vs geometry | all 9 `kind_of_shape_change` labels agree with the geometry. The only apparent anomaly — 48 rows in `skew-two-planes` that are geometrically single-plane — is exactly the 48 surplus duplicate rows, as documented ✓ |
| archive vs family | each of the 6 archives contains exactly its own families ✓ |
| strain range | max \|stretch\| = 0.10, max \|skew\| = 0.10 ✓ consistent with "six families to ±10%" |
| reference volume | `a₀³/4` = 11.3462 Å³ ✓ matches the header's 11.345 |
| `C₁₁−C₁₂` cross-check | 1079 − 124 = 955 ✓ against the page's "933 vs 955 expt" |
| run count | 2358 = 1179 × 2 ✓ |

### Reference data (`data/reference-data/*.csv`)

| check | result |
|---|---|
| per-file row counts | elastic-tensors 38, material-constants 43, phonon-frequencies 18, polarization-piezoelectric 14, transport-coefficients 66 = **179** ✓ every count matches `reference-battery#contents` |
| CSV structural integrity | all five files have a 10-field header; **all 179 rows parse to exactly 10 fields**; no required cell is empty ✓ **0 defects** |
| uncertainty-encoding census | all 179 classified: 118 absolute, 48 multiplicative, 6 dash, 3 unbounded, 2 sign-only, 2 range. Of the 48 multiplicative, **34 have N<1** and 14 have N≥1 ✓ enumerated, not sampled (F2) |
| encoding consistency per property | 5 properties mix encodings; 1 (Property, Material) pair mixes them across its own temperatures ✓ (F2) |
| exact lookup-key collisions | **0** — no two rows share (Property, Material, Environment) exactly ✓ |
| collisions after stripping direction | **6 keys, 17 rows** — with the stripper's output on all 19 direction cells printed and checked first, after an uncontrolled version of the same probe returned a false zero (§5) |
| Environment census | all 179 classified against the declared environment record's field list; **42 hold something the record has no field for** ✓ (F7) |
| unsourced-row count | 30 rows have no publication year; the "24" reproduces exactly under the identifier rule and gives 22 under the printed rule, with all 8 borderline rows enumerated ✓ (F5) |
| version discipline | Versions are `1` (134 rows) and `2` (45 rows). **0** rows are modified-after-added while still at version 1, and **0** are at version >1 without having been modified ✓ fully consistent |
| dash-cell enumeration | The page claims the remaining `—` uncertainty cells are "exactly" four named things. There are **6**, and they are exactly those ✓ **the enumeration is accurate** |
| the literal-`\|` hazard | 16 markdown tables checked for ragged delimiter counts; the one apparent raggedness at `accuracy-ledger.md:170` is `\|F_hkl\|²`, **both pipes correctly escaped** ✓ |
| registry-row references | **This line was inflated in the draft and is corrected here.** The manifest is rows 1..134 with **no gaps and no duplicates** ✓, and every registry row number cited by `accuracy-ledger` is ≤ 134 ✓ — so "the reference resolves" is nearly vacuous as a check, and I should not have reported it as 24 confirmations. The part with teeth is that each cited row **names what the ledger says it names**, which I verified by hand for the rows I rely on: 30 (`defect-formation-energy`) and 31–33 (charged-supercell corrections) in F8; 120 (`ahc-gap-renormalization`) in F14; 121 (`kappa-4phonon-high-t-correction`) in F1; 124 (`tp-aware-hull`) in N5. Those six are confirmed. The remainder are not individually confirmed and are no longer claimed |
| ledger sources vs CSV backing | every surname named in the ledger checked against all 179 Source cells; **4 back zero rows** (F11), and one apparent fifth ("Poncé") is an accent artifact ✓ |
| image-force lowering | `Δφ = √(qE/4πε_sε₀)` at ε_s = 5.7 gives **0.1589 eV** at 10⁶ V/cm and **0.5026 eV** at 10⁷ ✓ both reproduce the ledger's 0.16 and 0.50 |
| β-Ga₂O₃ mass density | `4·M/(N_A·V)` with the Åhman cell gives **5.9618 g/cm³** ✓ reproduces the seeded 5.96 |
| diamond mass density | `8M/(N_A a³)` with M = 12.011 gives **3.5157** ✓ reproduces 3.515; pure ¹²C gives 3.5125, 3× the stated σ away (F17d) |
| diamond bulk modulus | `(C₁₁+2C₁₂)/3` = **442.33** ✓ reproduces 442; the σ is F17c |
| carbon atomization | 711.19 kJ/mol ÷ 96.48534 = **7.3710 eV/atom for graphite**; the corpus's two rows are mutually consistent only under that reading ✓ (F10) |
| β-Ga₂O₃ elastic tensor | 13 independent constants present ✓ exactly the right count for monoclinic 2/m; all 13 cite `JAP 124 085102 (2018)` with a frame declared |
| alloy-bowing sign guard | the ledger's `−b_P` form with `b_P` negative and the CSV's `+b·x(1−x)` with b positive are algebraically equivalent ✓ the guard is internally correct |
| pyroelectric sign guard | P_sp is negative in the zincblende reference frame and its magnitude falls with temperature, so `dP_sp/dT > 0` ✓ the seeded `+3.0e-6` and `+4.5e-6` are consistent with the stated convention |

### Primary literature actually read

| source | how obtained | what it settled |
|---|---|---|
| Feng, Lindsay & Ruan, PRB 96 161201(R) (2017) | OSTI 1427696 via Unpaywall; full text extracted, 5,230 words | F1 in full. Zero "Debye"; both diamond claims verbatim; reference list confirming Broido 2007 and Olson 1993 |
| Lee et al., APL Materials 11 011106 (2023) | Crossref DOI 10.1063/5.0131453 | N7 — citation real, article number correct, quantity appropriate |
| Olson et al., PRB 47 14850 (1993) | via FLR reference [25] | acquisition target confirmed real, full author list verified |
| Broido et al., APL 91 231922 (2007) | via FLR reference [1] | citation resolves and matches the CSV; the open question is about content, not a broken reference |

**Not clean, and not certified:** the *values* in every row above except the derived ones (the two
mass densities, the bulk modulus, the graphite cohesive energy), which I re-derived. Two literature
investigations are in flight and I am certifying no further seeded value against the literature
until they return.

---

## 7 · Log-worthy advancements

Reported, not written — `log/timeline.md` has a single writer.

1. **The `0.4 Θ_D` four-phonon criterion is manufactured.** The cited paper never uses the word
   "Debye"; it states per-material temperatures, and its own silicon number implies 0.93 Θ_D against
   diamond's 0.41. The corpus's 0.4 is 900 ÷ 2200 using a Debye temperature the same page declares
   UNSEEDED. **First primary-text refutation in this audit.**
2. The Uncertainty column carries **five** encodings where the schema declares three plus a dash, and
   the declared `×N` rule is undefined on **34 of the 48** cells that use it. It sets `τ_battery`.
   On the 14 cells where the log rule does work, ten trip only at a factor of **27**.
3. Seven battery rows have unfalsifiable lower acceptance bands, including **all four**
   high-temperature thermal conductivities — the rows with the thinnest provenance.
4. **Gallium oxide's 25 eV displacement threshold is tabulated in canon as "25 eV for nitrogen".**
   Traced to a deleted five-material table via `log/timeline.md:1596`. Gallium oxide contains no
   nitrogen. The same row is simultaneously seeded in the CSV, marked `UNSEEDED` in
   `multiscale-state`, and declared retired in the log.
5. **7.37 eV/atom is graphite's, proved from the corpus's own two rows**: 7.37 − 25 meV/atom = 7.345,
   which is diamond's literature value to 1 meV/atom, while the alternative reading misses graphite
   by 24. Closes a declared open question.
6. The "24 unsourced rows" figure is correct only under a rule that appears nowhere in the corpus;
   the rule printed beside it gives 22, and the two sets differ in membership by ten rows.
7. **42 of 179** Environment cells hold content the declared environment record has no field for;
   stripping direction collapses six lookup keys onto 17 rows with spreads up to 3.06×.
8. **Five ledger tables — 23 numbers — have no reference-data counterpart at all.** Deformation
   potentials, piezoelectric d-coefficients, the alloy conductivity dip, the diamond and 4H-SiC
   breakdown temperature coefficients, and the nitride Caughey-Thomas exponent.
9. The diamond 300 K conductivity anchor's two *measured* sources appear in no CSV row; the canonical
   Source cell names a calculation, an unattributed range, and a paper suspected of being about
   silicon and germanium.
10. The corpus's high-temperature κ interpolation reproduces β-Ga₂O₃'s three points on one exponent
    to 1% and fails diamond's 773 K row by 12.3%; diamond's implied exponent **falls** (1.34 → 0.91)
    where four-phonon physics requires it to rise. AlN's rows track `T^−1`, not the `T^−1.25` their
    own "Slack extrapolation" source cell implies.
11. Registry row 120's declared input Θ is seeded nowhere, and the columns that could recover it
    carry no validity temperature.
12. The elastic Debye temperature of diamond, computed from the corpus's own elastic constants, is
    **2246 K** — the inherited "1860 K elastic route" does not survive, and 2200 ± 50 K is defensible
    for the T → 0 quantity. The real defect is that the row declares no method and no temperature.
13. The strain dataset's 24 triplicated shapes are entirely the anharmonic shear tail — every one
    outside the corpus's own linear-response window; naive fitting reweights that tail 1.5× against
    the linear core, biasing C₄₄.
14. **The de-duplication instruction has a second, undocumented failure mode that deletes the
    equation-of-state family.** `duplicate_group` is not "the only method that works" — a numeric key
    on all seven geometry columns also gives 1131 — and a numeric key on the six *strain* columns
    gives 1085, collapsing the 47-run hydrostatic family to one because those runs carry zero strain
    and differ only in target volume. The page's own "the coordinates are not the key" steers a
    reader toward exactly that key. This is the corpus's signature defect form, found in a place the
    corpus had already written a warning about.
15. **Method, three times paid for:** a probe of mine returned a clean zero because it was broken;
    the circulated AlN figures (98/63) rest on a 320 W/mK anchor the corpus does not seed; and
    re-running a line I had already certified ✓ produced finding 14. Every negative needs a control;
    every arithmetic claim needs re-running from the corpus's own inputs; and **a clean verdict of
    one's own is a verdict, not a value — the brief's rule applies to the auditor too.**
