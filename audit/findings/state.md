# Cohesion audit — the state and its representation

Subject: `journals/oracle/state/` — `unified-state`, `crystal-inputs`, `gamma-hat`,
`multiscale-state`, `born-oppenheimer-levels`.

Auditor: postdoc, state and representation. Read-only on `journals/` and `data/`; every
correction below is a proposal, not an applied change.

**Headline.** The state pages are internally tidy and physically load-bearing in ways
that have not been checked. The three worst defects are a **sign-and-dimension error in
the macro carrier-continuity residual** (S1) that would train an operator toward a
sign-flipped current; a **factor-5.5 error in the plane-wave count** that both memory
numbers on `gamma-hat` are derived from (S3); and the discovery that the corpus's own
**emergence axiom is void as argued** (S8–S11) — the load-bearing "constraint manifold"
rationale is contradicted by the macro tier the same refinement admitted, and the
"same scale" clause has no fixed referent.

On the inherited question the principal flagged — whether `multiscale-state`'s dangling
quotation of `unified-state` was substantively resolved or only textually removed — the
answer is **neither cleanly**: the two pages now agree on the *conclusion*, but both
inherited the *argument*, and the argument is unsound. See S8.

---

### Read this before using any earlier summary of this subject

**Five findings attributed to this subject in `audit/REGISTER.md` and in the principal's
brief are defects I planted myself**, in a scratch copy, to calibrate my own method. They
do not exist in `journals/`. They are struck in §2 as W1–W5, each against the primary text
that refutes it. `git status journals/ data/` is empty at this commit and a `diff` of the
plant copy against the corpus returns exactly my seven plants and nothing else.

The leak is confined to `REGISTER.md:79` and `:91`; no other postdoc's findings file
contains a plant signature. **`REGISTER.md`'s severity ranking row #8 is a planted defect
and must be struck**, as must the Einstein bullet in defect class 5 and the PBE-gap bullet
in class 6.

This has one compensating result, recorded in §5: the reader who found them **did not know
they were plants**, which makes this the audit's only genuinely *blind* calibration. It
returned **5 of 7**. The two misses are the finding of the calibration, and one of them —
a flat self-contradiction between two adjacent sentences, walked past by a method that caught
five value errors — is a gap in how this fleet reads, not only in how I read.

**On the gauge (the principal's item B), I cannot sign the finding as it reached me**, and
the reasons are in S24: the normative text is on someone else's page, the Gauss's-law
consequence does not follow, and the static field is not homeless. What survives is
narrower, is a genuine defect, and sits underneath the disagreement my two undergraduates
could not settle — because the object they were arguing about has two incompatible
definitions in the corpus.

---

### A statement about the audit's coverage, not only about my calibration

This belongs at the front because it bounds what every subject's clean verdict is worth,
mine included.

My method caught **five of five** defects that were wrong *values* or *cross-page
disagreements*, and **zero of one** defect that was a sentence contradicting its neighbor
in plain prose. The register's own calibration table shows the same shape in other subjects,
described in their own words: *"audits structure and sign, not magnitudes"*, *"misses prose
surrounding an equation"*, *"all three misses one class: prose using no ML vocabulary"*.

**The fleet reads for numbers that look wrong and for references that disagree. It does not
reliably read for sentences that disagree with themselves.**

That is defect class 1 in the register's taxonomy — a claim that resolves but is not true —
and it is precisely the class the corpus's existing checkers are structurally incapable of
seeing, because a sentence contradicting the next sentence still has valid links, a
resolving citation and a single owner. **Both the automated gates and the human-shaped sweep
are blind in the same direction.** Nothing in this audit has measured how much of that class
the corpus holds, and one plant is not a measurement — but the direction of the gap is
established, and it is the one direction where nothing else is looking.

**My estimate, stated as an estimate:** the corpus likely carries more undiscovered class-1
prose contradictions than any other defect class this audit has found. I hold that at medium
confidence. It rests on one miss in my own subject plus three converging calibration remarks
in others, and it is falsifiable cheaply — see the proposed second pass in §6, which needs a
different instrument rather than more of the same one.

---

### Severity ranking for this subject

Supplied so the register can be rebuilt without re-reading the file. Twenty-five findings;
the ten that carry weight, ranked by consequence rather than by confidence.

| # | finding | class | why it ranks here |
|---|---|---|---|
| 1 | **S1** · carrier continuity: missing `1/q`, sign-flipped, `p` row unexecutable | 4 + 2 | Trains the operator backwards. Frozen beats correct 4:1; the exact minimizer is reversed transport. Spurious term is **~5×10³ ×** the generation-recombination signal against both generation channels, **doping-independent and worse under mesh refinement** |
| 2 | **S16** · three-tier residual contract has no interface | 3 | Two of nineteen categories have no argument through which their state can arrive; no `∂_t x` reaches any `EOM/*`, and the corpus gives three incompatible accounts of where one comes from |
| 3 | **S8–S11** · emergence axiom void as argued | 1 | The load-bearing rationale for the whole stratification. Conclusion survives on a different, sound argument; the stated one is contradicted by both tiers the refinement admitted |
| 4 | **S2** · one `j` slot for three incompatible currents | 3 | Bipolar transport unscoreable. **A structural gap filed as a data gap** — buying every missing coefficient would not fix it |
| 5 | **S3** · `N_PW ≈ 1000` is **181** (exact) / 206 (smooth formula) | 4 | Both memory budgets rest on it, and it inverts the section's "feasibility boundary, not an optimization" thesis. Formula validated to 0.15% against exact enumeration and 0.08% against a real VASP run |
| 6 | **S24** · gauge derivation invalid; `A` slot defined twice | 4 + 2 | The partition is correct and the relayed consequences do not follow — but the derivation cannot work, and `A` is typed *external* while carrying an equation of motion and a term in the system energy |
| 7 | **S19** · slow tier carries the redundancy its own definition forbids | 1 | `charge_dist[D]` is a normalization of `conc[D,q]`. Third instance of the S8 pattern, in the tier defined by its absence |
| 8 | **S22** · slow tier's declared timescale excludes six of its own barriers | 4 | Stated floor completes in 1.1 s, ceiling in 10²⁵ years. Nothing owns ns→hours, where the corpus's own "severe" degradation path lives |
| 9 | **S5** · "three physically orthogonal inputs" is false | 4 | Diamond and c-BN — the corpus's own anchor pair — share a periodicity structure and differ in space group. The kernel cache is keyed on the assumption |
| 10 | **S20** · promotion story covers one of six slow fields | 3 | `s(t=0)` is required by every slow-tier trajectory and is specified for at most a subset of one field |

Below the line but real: **S4** (half-life pair impossible at the stated barrier, prefactor-independent),
**S7** (staleness "bound" is not a bound, not a radius, not evaluable), **S21** (level table
contradicts its own prose; optical row wrong for the MVP material), **S23** (closed universe
containing unbounded families), **S6/S14** (`Environment` membership unevidenced; the
structural/swept partition is ill-posed as a per-field bit), **S12**, **S13**, **S15**,
**S17**, **S18**, **S25**.

**Not in this ranking, and struck:** the five withdrawn plants, §2a.

---

## 1 · Findings

### S1 — The macro carrier-continuity equation is dimensionally wrong, sign-wrong, and its hole row is unexecutable

**Severity: high. Confidence: high (derivation below; independently re-derived by a
directed check).**

Three lines on `multiscale-state`, all in the macro tier.

`multiscale-state:403-405`, the stated balance equations:

```
(DD) ∂_t n + ∇·j = G − R,   j_n = q·μ_n·n·E + q·D_n·∇n
```

`multiscale-state:445-446`, the finite-volume right-hand sides that the `EOM/Continuum`
residual scores against:

```
| `n` | `(1/V_c)·[ −Σ_f j_f·A_f/q + (G − R)(c)·V_c ]` |
| `p` | the same, with the hole sign                    |
```

**(a) Dimensions.** `MacroState` is typed at `multiscale-state:342-346`: `n, p` in
`m⁻³`, `j` in `A·m⁻²`. Then `∂_t n` is `m⁻³s⁻¹` and `∇·j` is `A·m⁻³ = C·s⁻¹·m⁻³`. They
differ by one factor of charge. `(DD)` as written cannot be evaluated. The residual row
at `:445` *does* carry the `/q`, so the two statements of the same equation disagree with
each other as well.

The missing factor has a size: `1/q = 1/(1.602176634×10⁻¹⁹ C) = 6.2415×10¹⁸`. **The page
contradicts itself by eighteen orders of magnitude, forty lines apart.**

**(b) Sign.** Derive it. An electron carries charge `−q` with `q > 0`, so the particle
flux is `Φ_n = J_n/(−q)`. Particle conservation `∂_t n + ∇·Φ_n = G − R` gives

```
∂n/∂t = +(1/q)·∇·J_n + (G − R)          [electrons]
∂p/∂t = −(1/q)·∇·J_p + (G − R)          [holes]
```

This is the standard pair (Sze, *Physics of Semiconductor Devices*, 3rd ed., §2.4;
Selberherr, *Analysis and Simulation of Semiconductor Devices*, ch. 1).

Applying the divergence theorem with outward face normals, `Σ_f j_f·A_f = ∮j·dA ≈
(∇·j)V_c`, the `n` row at `:445` reads

```
∂_t n = −(1/q)·∇·j + (G − R)
```

which is the **hole** equation. The electron row carries the hole sign.

Note that `(DD)` at `:404` is wrong *without reference to any face convention at all* — it
is written as a PDE, where `∇·j` is unambiguous. `∂_t n + ∇·j = G − R` rearranges to
`∂_t n = −∇·j + (G − R)`, the hole structure, and the current it is closed with on the
same line — `j_n = q·μ_n·n·E + q·D_n·∇n` — is unambiguously the **electron** current. The
equation matches neither carrier.

**(b′) It is provably a defect, not a convention choice.** *(This argument reached me
through the principal; I verified it independently and it is correct. It is the part of
the finding that closes the escape route, so it belongs in the record with its origin
named.)*

The obvious defense of the `n` row is that `A_f` is an inward face normal. Test that
defense against the two rows that sit beside it in the same table:

| row | `:443-449` right-hand side | reduces correctly under |
|---|---|---|
| `T_L` | `(1/C_pρ_m)·[Σ_f κ_f(∇T_L)_f·A_f + Q V_c]/V_c` vs `(H)` `C_pρ_m ∂_t T_L − ∇·(κ∇T_L) = j·E` | **outward** |
| `φ` | `‖Σ_f ε_f(∇φ)_f·A_f + ρ V_c‖²` vs `(P)` `∇·(ε∇φ) = −ρ` | **outward** |
| `n` | `(1/V_c)[−Σ_f j_f·A_f/q + (G−R)V_c]` vs the electron equation | **inward** |

Under outward normals `Σ_f (·)_f·A_f → (∇·)(·)V_c`, so `T_L` gives
`∂_t T_L = (1/C_pρ_m)[∇·(κ∇T_L) + Q]` ✓ and `φ` gives `V_c²‖∇·(ε∇φ) + ρ‖²`, which
vanishes exactly on Poisson ✓. The same substitution turns the `n` row into
`∂_t n = −(1/q)∇·j + (G−R)` ✗. Flipping to inward normals repairs `n` and breaks the
other two.

**No single convention makes all three rows right.** The defense is unavailable, and the
`n` row is a defect on the face of the table rather than an unstated convention.

That is three independent confirmations: the PDE is dimensionally wrong, the PDE is
sign-wrong against its own closure, and the discretization is sign-wrong against its own
neighbors.

**(c) The `p` row is unexecutable.** "the same, with the hole sign" is an instruction to
take whatever sign the `n` row carries and apply the hole convention. But the `n` row
already carries the hole sign. Under one reading `p` is identical to `n` and one of them
is wrong; under the other, `p` flips to `+(1/q)∇·j`, which is the *electron* equation, and
the two rows are swapped. **There is no reading under which both rows are correct.** This
is a class-2 defect (a careful reader follows the instruction correctly and still gets the
wrong answer) sitting on top of a class-4 defect.

**(d) Consequence — the loss does not merely mis-score, it rewards the wrong answer.**
`EOM/Continuum[n,c] = ‖∂_t n − RHS_n‖²` is the training signal, with
`RHS_n = −(1/q)∇·J + (G−R)` while the truth is `∂_t n = +(1/q)∇·J + (G−R)`. Then:

| trajectory the operator predicts | residual it scores |
|---|---|
| **correct** physics | `‖(2/q)∇·J‖²` |
| **frozen**, `∂_t n = 0` | `‖(1/q)∇·J − (G−R)‖² → ‖(1/q)∇·J‖²` when transport dominates |
| `∂_t n = −(1/q)∇·J + (G−R)` — **reversed transport** | **exactly 0** |

So a frozen trajectory scores **four times better** than a correct one, and the loss's
exact minimizer is a trajectory whose transport runs backwards. The gradient is not
noisy — it points away from the physics.

**(e) The size of the spurious term, and a form that does not depend on the doping.**
*(An order-of-magnitude estimate reached me through the principal; the doping-independent
form below is mine, and it both corrects that estimate and makes the finding robust.)*

The ratio of the spurious transport term to the generation-recombination signal the
residual exists to teach is

```
|(1/q)∇·J| / |G − R|  ~  (n·v_sat/L) / (n/τ)  =  v_sat·τ / L
```

**The carrier density cancels.** The ratio is the recombination length over the cell
size — a pure geometry-and-materials number, independent of doping, injection level and
bias point. At the corpus's own operating point (`multiscale-state:456`, 1 MV/cm across
~10 nm cells) with diamond's `v_sat ≈ 10⁷ cm/s = 10⁵ m/s`, `L = 10 nm`:

| `τ` | `v_sat·τ/L` |
|---|---|
| 1 ps | 10 |
| 100 ps | 10³ |
| 1 ns | **10⁴** |

(This counts recombination alone; the control below adds the second generation channel and
brings the figure to ~5×10³.)

This matters more than the point estimate. Because the ratio is `v_sat·τ/L`, it is **large
for any mesh fine enough to resolve the device** — refining the mesh makes the defect
worse, linearly. There is no operating point inside the corpus's declared envelope at
which the spurious term is small, and the one knob that would shrink it is the one the
Péclet argument at `:456-458` requires to stay fine.

**Control on the denominator.** A ratio is only as good as what sits underneath it, so I
checked whether the second generation channel — impact ionization, which is field-driven and
could plausibly dominate at 1 MV/cm — shrinks it. I used **the corpus's own Chynoweth
parameters**, `accuracy-ledger:286`: diamond `a = 1.93×10⁵ cm⁻¹`, `b = 7.59×10⁶ V/cm`,
`v_sat = 1.5×10⁷ cm/s` (Hiraiwa & Kawarada, *J. Appl. Phys.* **114**, 034506 (2013)).

```
α(10⁶ V/cm) = 97.56 cm⁻¹      G_avalanche = α·n·v_sat = 9.76×10²⁵ cm⁻³s⁻¹
                              R_SRH       = n/τ       = 1.00×10²⁶ cm⁻³s⁻¹  (τ = 1 ns)
                              avalanche / SRH = 0.98
```

**The two channels are comparable at this field**, not orders apart. That does not weaken
the finding, and the reason is worth stating because it is the same structural fact twice:
**the avalanche ratio also cancels the carrier density**, and for an independent reason —

```
transport / SRH        =  (n·v_sat/L) / (n/τ)        =  v_sat·τ / L   =  1.00×10⁴
transport / avalanche  =  (n·v_sat/L) / (α·n·v_sat)  =  1 / (α·L)     =  1.03×10⁴
```

One is the recombination length over the cell size; the other is the **ionization length**
over the cell size. Both are ~10⁴ at the corpus's operating point, arriving there by
different physics. Against **both channels together** the ratio is

```
transport / (SRH + avalanche) = 5.06×10³
```

**So the honest figure is ~5×10³, not 10⁴** — the relay's estimate was high by a factor of
two because it counted one denominator. Three to four orders of magnitude either way, and
the finding is unchanged; but the number in the record should be the one that survives both
channels. Sensitivity to the least-constrained input, the carrier lifetime:

| `τ` | transport / (SRH + avalanche) |
|---|---|
| 1 ps | 9.99 |
| 100 ps | 911 |
| 1 ns | 5.06×10³ |

Even at `τ = 1 ps` — an aggressively short lifetime for diamond — the spurious term is an
order of magnitude larger than the signal. **There is no lifetime at which the residual
teaches what it exists to teach.**

**Verification of the 4:1 claim.** The factor is asymptotic in `T/g`, not exact. Computed:
`T/g = 10` gives 4.94, `10²` gives 4.08, `10³` gives 4.008, `10⁴` gives 4.0008. At the
corpus's operating point `T/g ≈ 10⁴`, so **4:1 holds to four significant figures** — but the
claim is a limit and I am stating it as one.

**What would refute it.** A statement elsewhere in the corpus that `j` in `(DD)` denotes a
*particle* flux rather than a charge current density, or that `n` in `(DD)` denotes a
charge density. I searched: `multiscale-state:342-346` types `j` in `A·m⁻²` and `n` in
`m⁻³`, `:447` closes `j` against `q·μ_n·n·E + q·D_n·∇n` (a charge current), and `:445`
divides by `q`. All three fix the units as I have read them.

**Control sweep — and its result changes the finding's weight.** I searched all of
`journals/` for ten forms of the equation: `continuity`, `G − R`, `G - R`, `∇·j`, `∇·J`,
`∂_t n`, `∂n/∂t`, `dn/dt`, `charge conservation`, `carrier conservation`. Total hits
across the entire corpus: **four lines, all on `multiscale-state`** — `:358` (total-current
continuity, which is S2's subject), `:404`, `:445`, and one navigational mention on
`capability-slices:79`. Six of the ten patterns return nothing at all.

**There is no competing statement, and there is also no correct one.** The corpus states
carrier continuity exactly once, and that statement is the defective one. This removes the
mildest reading — that `(DD)` is a loose gloss on a correct equation stated properly
elsewhere — and it means anything generated from the corpus has nothing to fall back on.

**Proposed correction.** Write the two continuity equations explicitly rather than by
reference to each other:

```
(DD_n)  ∂_t n − (1/q)·∇·j_n = G − R
(DD_p)  ∂_t p + (1/q)·∇·j_p = G − R
```

and give the `p` residual row its own right-hand side in full. Delete the phrase "the same,
with the hole sign" — it is the mechanism by which the error propagates.

---

### S2 — One `j` slot is used for three incompatible currents

**Severity: high. Confidence: high.**

`MacroState` (`multiscale-state:342-346`) carries exactly one current field,
`j : Field[DeviceMesh → ℝ³] [A·m⁻²]`. The same page then uses it three ways:

| Line | Use | What `j` must be |
|---|---|---|
| `:358` | "current continuity `∇·j + ∂ρ/∂t = 0` is a scorable balance" | the **total** current `j_n + j_p` |
| `:380` | gives `j_n` for electrons and `j_p` for holes as two separate formulas | **two** fields |
| `:447` | the `j` residual closes `‖j(c) − (q·μ_n·n·E + q·D_n·∇n)(c)‖²` | the **electron** current alone |

That `:358` requires the total current is not a matter of taste — it follows from summing
the two continuity equations with `ρ = q(p − n + N_D⁺ − N_A⁻)` (`:403`):
`∂_t(p − n) = −(1/q)∇·(j_p + j_n)`, hence `∂ρ/∂t = −∇·(j_n + j_p)`. The balance at `:358`
holds exactly for the sum and for nothing else.

So the macro state is **under-specified for bipolar transport**: it carries `p` as a state
field, a hole continuity row, and a hole drift-diffusion formula, but no hole current slot.
The page's own open question (`multiscale-state:51-52`) says "The **hole schema is
committed**; the coefficients are a per-composition data gap." The coefficients are indeed
a data gap. The *schema* is not committed — it is missing a field.

**This is a structural gap filed as a data gap, and the misfiling has a cost.** *(The
framing is the principal's; the evidence is mine, above.)* An open question that says
"the coefficients are a per-composition data gap" routes to acquisition — buy `μ_p`,
`D_p`, seed the ledger, close it. But there is **no hole current slot, no hole flux
expression and no hole closure**, so buying every missing coefficient would not make one
bipolar device scorable. The work is a schema change touching `MacroState`, the residual
table, and the `(MeshCell, MacroField)` axis cardinality at `:468` — and it is currently
invisible to whoever reads the open-questions list, because that list says the schema is
done. **Wrongly-classified gaps do not get worked on**; they get waited on.

**What would refute it.** A second current field in the macro schema, or a statement that
`j` is the total current and `j_n`, `j_p` are derived. Neither exists: `:447` and `:487`
both carry the five-field tuple with one `j`.

**Proposed correction.** `MacroState = (T_L, φ, n, p, j_n, j_p)`, with `:358`'s balance
written on `j_n + j_p`, and the `j` residual row split in two. Note this also changes the
`(MeshCell, MacroField)` axis cardinality at `:468`.

---

### S3 — `N_PW ≈ 1000` is 5.5× too large for the cell the page describes, and both memory numbers rest on it

**Severity: medium-high. Confidence: high (computation below is re-runnable).**

`gamma-hat:160-173`:

> A plane-wave cutoff near 400 eV gives `N_PW ≈ 1000`; the band count is `N_b ≈ 40`, four
> occupied plus the unoccupied manifold the quasi-particle correction needs; an 8×8×8
> Monkhorst–Pack mesh gives **~29 irreducible k-points**.

The number of plane waves below a cutoff is `N_PW = V_cell·G_max³/(6π²)` with
`G_max = √(2mE_cut)/ħ`. For the cell this page describes — and `mvp-system:33-34` fixes it:
"Diamond, primitive cell. Space group Fd-3m (No. 227); two carbon atoms at the 8a Wyckoff
site … **four occupied bands**" — `a = 3.567 Å`, so `V_prim = a³/4 = 11.35 Å³ = 76.6 bohr³`,
and at 400 eV `G_max = 5.42 bohr⁻¹`:

```
N_PW = 76.6 × 5.42³ / (6π²) = 206
```

**And the exact count is lower still: 181.** The formula above is an asymptotic — it is the
volume of a sphere in `G`-space divided by the reciprocal-cell volume, which is only exact
in the limit of many `G`-vectors. Diamond's primitive cell is small enough that the
discreteness of the reciprocal lattice matters. Enumerating the actual reciprocal lattice
vectors of the fcc primitive cell with `|G| ≤ G_max` at Γ gives

```
exact G-vector count = 181        (smooth formula overestimates by 13.9%)
```

*(This refinement reached me from the principal after I had filed 206; I re-derived it by
independent enumeration and it is correct. Both numbers belong in the record: 206 is what
the standard formula gives, 181 is what a code actually allocates.)*

**A control that shows the two numbers are consistent rather than competing.** The same
enumeration run on a large cell reproduces the asymptotic, which is why my VASP check
worked: for a cubic box of 1155 Å³ at 500 eV, the smooth formula gives 29322.5 and exact
enumeration gives 29279 — agreeing to **0.15%**, against VASP's reported 29299. So the
formula is trustworthy where it was tested and biased high where it is applied here, in the
direction and by roughly the magnitude expected. **The two results are one result.**

Not 1000, by either count — the page's figure is **5.5× the true one**. To reach
`N_PW ≈ 1000` at this cell volume you need `E_cut ≈ 1150 eV`; to reach it at 400 eV you need
a cell ~4.9× larger, i.e. ~10 atoms — which contradicts "four occupied bands" and
contradicts the k-point count (see below).

**The other two numbers in the same paragraph are right, which is what pins the cell.**
I recomputed both:

- **29 irreducible k-points for an 8×8×8 Γ-centered Monkhorst–Pack mesh on the fcc
  lattice: confirmed exactly** by explicit orbit counting under the 48 operations of `O_h`
  (4×4×4 → 8, 6×6×6 → 16, 8×8×8 → 29). This is the *fcc primitive* count; a simple-cubic
  8-atom cell would not give 29.
- **`N_b ≈ 40`, four occupied: confirmed.** Two carbon atoms give eight valence electrons
  give four occupied bands.
- **The `~18 × 18` tight-binding warm start (`gamma-hat:184-185`): confirmed.** `sp³d⁵` is
  9 orbitals per atom × 2 atoms = 18. (Spinless — with spin it would be 36×36. The page
  does not say which, and `γ̂` is elsewhere a Pauli spinor; minor, logged below.)

So every other quantity in the paragraph is consistent with the 2-atom primitive cell, and
`N_PW` alone is not.

**Consequence.** Both budget figures are derived from `N_PW = 1000` and both move:

| | page (`N_PW = 1000`) | smooth (206) | **exact (181)** |
|---|---|---|---|
| orbital storage `N_PW·N_b·16B·N_k` | 18.6 MB | 3.82 MB | **3.36 MB** |
| densified `N_PW²·16B·N_k` | 464 MB | 19.7 MB | **15.2 MB** |

The page's arithmetic is internally correct (`1000×40×16×29 = 18.6 MB`;
`1000²×16×29 = 464 MB` — both reproduce). Only the input is wrong.

**This matters beyond tidiness**, because the page's conclusion is a *feasibility* claim:
"**The slot choice is a feasibility boundary, not an optimization**" (`gamma-hat:176-177`).
At the corrected numbers the densified matrix is ~15 MB — trivially affordable — so at MVP
scale the encoding choice is an optimization after all, and the feasibility argument only
returns at supercell scale, which is exactly the budget the page declares missing
(`gamma-hat:187-190`). The correction does not change the *design*; it changes the stated
reason for it, and the stated reason is the page's thesis.

**What would refute it.** A different lattice constant, a stated non-primitive cell, a
convention counting plane waves on the charge-density grid, or a norm-conserving/hard-PAW
convention I have not accounted for. The cell is not in doubt: the paragraph heads itself
"**Sizing, primitive cell**" (`gamma-hat:159`) and says "four occupied", which is two carbon
atoms.

**Control — the formula validated against a real production VASP run.** *(This closes the
acquisition item this finding previously carried.)* A VASP `OUTCAR` exists at
`~/Downloads/OUTCAR`. It is not diamond — it is an H₂ dimer in a box — which makes it a
**better** control than a diamond run would be, because it tests the formula on a system
100× larger in volume, at a different cutoff, with a different element, where no
diamond-specific coincidence could rescue a wrong formula:

| | |
|---|---|
| cell volume | 1155.00 Å³ |
| `ENCUT` | 500 eV |
| VASP reports (`OUTCAR:450`) | `k-point 1 : ... plane waves: **29299**` |
| `N_PW = V·G_max³/(6π²)` predicts | **29322.5** |
| relative error | **0.0803 %** |

The formula I applied to diamond is confirmed to better than one part in a thousand against
the code the corpus's numbers would come from — which is what licenses applying it to
diamond. Combined with the exact enumeration above, the diamond primitive cell at 400 eV
holds **181** plane waves (206 by the asymptotic formula), and both figures are now
empirically anchored rather than textbook.

**A convention trap, checked and rejected as the origin.** The same `OUTCAR` also reports
`total plane-waves NPLWV = 201600` at line 248 — a field whose label reads like the
quantity we want but which is **the FFT grid**, `NGX·NGY·NGZ = 56·60·60 = 201600`, 6.88×
the true count. That is a real way to overcount `N_PW` from a VASP output by a large factor.
It does **not** explain `≈ 1000`: the corresponding grid for diamond primitive at 400 eV is
~23³ per axis, i.e. thousands, not 1000. **The origin of the figure remains unexplained**,
and I record the rejected hypothesis so the next reader does not re-run it.

**Proposed correction.** Either restate `N_PW ≈ 180` at 400 eV — the exact count, which is
what a code allocates — and rework both budget figures and the feasibility sentence, or state
the cutoff that actually gives 1000 (~1146 eV) and say why the MVP needs it.

---

### S4 — The nitrogen-aggregation half-life pair is impossible at the stated barrier, for any prefactor

**Severity: medium-high. Confidence: high (the argument is prefactor-independent).**

`multiscale-state:204-207`, formula `platelet-nucleation-allen-cahn` (registry row 107):

> `k_nuc·c_Ns² − k_dis·c_platelet`, `k_nuc = ν₀·exp(−E_nuc/kT)`, `E_nuc ≈ 3.5 eV`. The
> substitutional-nitrogen-to-A-center half-life is **years at 500 °C and hours at 1000 °C**.

The ratio of Arrhenius rates between two temperatures depends only on `E_a` — the
prefactor cancels:

```
k(1273 K)/k(773 K) = exp[ E_a/k_B · (1/773 − 1/1273) ] = 9.1 × 10⁸   at E_a = 3.5 eV
```

So if the half-life is 3 years (`9.5×10⁷ s`) at 500 °C, it is `0.10 s` at 1000 °C — not
hours. Conversely, for the stated pair (years → hours, a ratio of ~10⁴) to hold, the
barrier would have to be

```
E_a = ln(10⁴) / (1/k_BT₁ − 1/k_BT₂) = 1.54 eV
```

**No choice of `ν₀` reconciles the two statements with `E_nuc = 3.5 eV`.** With
`ν₀ = 10¹³ s⁻¹` the pair is 143 years and 5 seconds.

At least one of the three numbers — the barrier, the 500 °C half-life, the 1000 °C
half-life — is wrong, and the page gives no way to tell which. This feeds `EOM/DefectPopulation`
(`multiscale-state:265`) and the degradation bundle, so it is a scored quantity.

Separately, the formula is named for **platelet** nucleation but its rate law is the
substitutional-nitrogen → A-center reaction; whether platelets nucleate directly from
`N_s` or at a later aggregation stage is a literature question I have put to a directed
check that did not return before the session limit (gap **G1**, §3); the naming mismatch is visible from the page alone and does not wait on it.

**What would refute it.** A stated temperature-dependent prefactor (none appears; the page
fixes the Arrhenius form at `:171-172` as `rate = ν₀·exp(−E_a/kT)` for *all* nine slow
formulas), or a reading in which "years"/"hours" describe different reactions.

**Proposed correction.** Pin the barrier to a cited measurement and recompute both
half-lives from it, or drop the half-life pair.

---

### S5 — "Three physically orthogonal inputs" is false, and the corpus's own anchor pair is the counterexample

**Severity: medium-high. Confidence: high.**

`crystal-inputs:39`:

> Three **physically orthogonal** inputs fully specify what crystal, in what conditions

and `:49-51` puts the space group inside the first of them:

> `PeriodicityStructure` is the geometry of repetition: dimensionality `d ∈ {0,1,2,3}`,
> lattice vectors `{a_i}`, periodicity flags, **the Bravais lattice and space group**, and
> the cell vectors `h`.

**The space group is not a function of the periodicity structure.** It is a function of the
periodicity structure *and* the decoration. The cleanest counterexample is the corpus's own
anchor pair:

| | Bravais lattice | atom positions | space group |
|---|---|---|---|
| diamond | fcc | 2 atoms, `(0,0,0)`, `(¼,¼,¼)` | **Fd-3m** (#227) |
| cubic BN | fcc | 2 atoms, same positions | **F-43m** (#216) |

Identical skeleton, different space group, and the difference is *entirely* in the
decoration — two like species versus two unlike ones. Both are anchor materials
(`purpose-and-scope:205`), and `capability-slices:49,57` runs a **c-BN-on-diamond**
heterostructure check, so the corpus pairs these two materials directly.

The dependency also runs the other way: `SiteDecoration` is defined as "which species sit
at which **Wyckoff positions**" (`crystal-inputs:58`), and a Wyckoff label is meaningless
without a space group. Diamond's two atoms are one 8a orbit in Fd-3m; c-BN's are 4a and 4c
in F-43m. **The two "orthogonal" inputs are mutually defining.**

And the page refutes itself a third time at `:130-133`, in the `Environment` record:

> `applied_stress` and `applied_magnetic_field` are the hard cases in either direction,
> because both **can change the symmetry that the symmetry-quotient stage builds its
> structure on**

So the symmetry depends on all three inputs, and the page says so 90 lines after calling
them orthogonal.

**This is load-bearing, not cosmetic.** `compose-time-pipeline:117-118` feeds the symmetry
quotient stage "the topology-atlas entry for this composition's **space group**, Wyckoff
orbits and orbital basis", and `:377-378` keys the kernel cache on "a content hash of
periodicity, decoration, and the *structural* part of the environment" as three separate
parts. If the space group is recorded in the periodicity part but determined by all three,
two compositions can share a periodicity hash and not share a symmetry.

**A cross-subject corollary, reported and not chased** (registry's page, flagged to the
principal): `typed-compositions:113-114` derives it as

```
CrystalStructure = ClassifyOf((state.R, state.h), classifier = space-group-detection)
```

— from positions and cell only. That signature **cannot distinguish diamond from c-BN**,
because their positions and cells are the same and only `state.Z` differs. The species
labels are missing from the classifier's arguments.

**What would refute it.** A statement that `PeriodicityStructure.space_group` is a derived
cache rather than an input field, with an owner for the derivation. None exists; the two
accounts (stored on `crystal-inputs`, derived on `typed-compositions`) are simply
unreconciled.

**Proposed correction.** Move the space group out of `PeriodicityStructure` and make it a
derived property of `(PeriodicityStructure, SiteDecoration, Environment)` with a stated
owner; add `state.Z` to the `space-group-detection` signature; and replace "physically
orthogonal" with an accurate statement — the three inputs are *independently supplied*, not
independent.

---

### S6 — Eight of the thirteen `Environment` fields are used nowhere in the corpus, and the page says otherwise

**Severity: medium. Confidence: high (mechanical, re-runnable).**

`crystal-inputs:91-94`:

> Only the last five fields carry a declared type and unit anywhere in the corpus. The
> first eight are recoverable as *names* — **they are used in signatures and in prose
> across the corpus** — but their types and units are stated nowhere.

The second clause is false of the corpus as it now stands. Grepping all of `journals/`:

| field | occurrences outside its own table row |
|---|---|
| `applied_electric_field` | **0** |
| `applied_magnetic_field` | 0 (one, in the structural/swept paragraph of the same page) |
| `applied_stress` | 0 (same) |
| `temperature_gradient` | **0** |
| `carrier_injection` | **0** |

Also zero for the spaced-out prose forms ("applied electric field", "temperature
gradient", "carrier injection", "applied stress", "applied magnetic field").

So the stated justification for these fields' membership in the record — that the corpus
uses them — does not hold. Either the fields are vestigial (carried over from pre-restructure
pages), or their use sites were lost in the rewrite. The page's own framing makes this
matter: the record "is a **public interface** rather than an implementation detail"
(`:73-74`), and `:102-106` requires the field set to be **closed and versioned** because
"adding a field changes which formulas apply to every existing composition, silently".
A closed, versioned public interface whose membership has no evidence is the same hazard
in the other direction.

**What would refute it.** Use sites in a stratum I did not sweep. I searched `journals/`
only, which is the corpus under audit.

**Proposed correction.** Either cite the use site for each of the eight, or mark them
`PROVISIONAL` distinctly from `UNSEEDED` — the current single marker conflates "we know
this field exists but not its type" with "nothing in the corpus refers to this field".

---

### S7 — The dressing-staleness "bound" is not a bound, is not a radius, and cannot be evaluated

**Severity: medium-high. Confidence: high on (a)–(c).**

This is the resolution of inherited contradiction #2 (`contradictions.md:12`), which
registered `born-oppenheimer-levels` stating a gap that `open-decisions` recorded closed.
The restructure closed it by writing a bound onto the page. **The closure is unsound.**

`born-oppenheimer-levels:92-104`:

> **The staleness term has a bound, and the bound is the validity radius.** … To first
> order the dropped term is `‖Δx‖ · ‖∂(dressing)/∂x‖_ref`. The sensitivity coefficient is
> measured **once, at the reference state, at compile time** … and the runtime factor is a
> norm on the state. … **A composition that leaves the radius is refusable, because the
> radius is a number.**

**(a) A first-order Taylor term is not a bound.** The quantity written is the derivative
evaluated *at the reference state*, times a displacement. To bound the dropped remainder
you need either a supremum of the derivative over the segment (a Lipschitz constant) or a
second-derivative bound giving an `O(‖Δx‖²)` remainder. Neither is stated. The stated
quantity is an *estimate* that is accurate precisely where it is not needed (near the
reference) and unbounded in error where it is (far from it). For the case the page names —
the G₀W₀ shift versus strain — the sensitivity is not constant. A directed check on that
specific number did not return before the session limit (gap **G2**, §3); (a)–(c) below are
independent of it.

**(b) It cannot be a radius, by units.** A radius is a distance in state space. `‖Δx‖ ·
‖∂(dressing)/∂x‖` carries the units of the dressing — energy, for a quasi-particle shift.
Setting an energy equal to a radius is dimensionally impossible. What a radius would be is

```
Δx_max = τ_allowed / ‖∂(dressing)/∂x‖_ref
```

which requires an allowed tolerance `τ_allowed`, and **no tolerance is stated**. So "A
composition that leaves the radius is refusable, because the radius is a number" is
unsupported: what is a number is the staleness *term*; refusability would have to come from
the accuracy target, which lives in `accuracy-ledger` and is not referenced here.

**(c) `‖Δx‖` is not defined on this state.** The state is a heterogeneous product: a 3×3
matrix in `GL⁺(3,ℝ)`, `3N` positions, `3N` momenta, a 3×3 momentum, **discrete** labels, an
operator-valued `γ̂`, and a vector field `A` (`unified-state:27-38`). A norm on that product
requires a per-slot unit and a relative weighting, and `unified-state:74-80` states that
per-slot "dtype, **unit**, index order and memory layout are recorded nowhere". So the
product `‖Δx‖·‖∂(dressing)/∂x‖` has no numerical value as written. On the discrete slot
`Z_I` it has no value even in principle.

This is the same root cause as the laws postdoc's L5 (`audit/findings/laws.md:239-268`),
which found `δ_PSD = 1e-9 absolute` unusable for want of a unit convention on `M` and cited
this same `unified-state` gap. **Two independent findings in two subjects trace to one
missing declaration on my page.** I record that agreement rather than averaging it: the
wire-schema open question is currently framed as a *serialization* gap, and it is also a
*numerical* gap, blocking at least two error-model quantities.

**What would refute it.** A stated tolerance and a stated state metric. I searched
`born-oppenheimer-levels`, `residual-definitions#error-budget` (`:347-363`) and
`unified-state`; the error budget lists "dressing staleness" as a summand and states no
tolerance, metric or bound.

**Proposed correction.** Downgrade the claim from "bound" to "first-order estimator", state
the tolerance that converts it into a radius, and either give a per-slot metric on the state
or restrict `‖Δx‖` to the slots the dressing actually depends on (for G₀W₀-vs-strain, that
is `h` alone, which *does* have a natural norm).

---

### S8 — The emergence axiom's constraint-manifold rationale is void: the macro tier is itself a differential-algebraic system, by the page's own words

**Severity: medium-high. Confidence: high.**

This answers the principal's flagged question directly. The dangling quotation is gone and
the two pages now agree on the *conclusion*. Both kept the *argument*, and the argument does
not survive the tier the refinement admitted.

The argument, on both pages:

- `unified-state:55-57`: "Admitting a same-timescale coarse-graining would tie a
  **constraint manifold** back onto the irreducible degrees of freedom and reintroduce the
  **integration pathology** this formulation exists to avoid."
- `multiscale-state:86-90`: "Because the added tiers are independent by timescale or by
  scale, they create **no algebraic constraint** with the micro seven-tuple. … The
  constraint-manifold pathology that `[unified-state#emergence]` guards against arises only
  for quantities redundant on the *same* timescale and scale."

And the stated reason for keeping the carrier distribution out of the macro tier,
`multiscale-state:360-362`:

> **Kept emergent, never promoted:** the carrier distribution `f_n(k,r)` — promoting it
> double-counts its own moments and **produces a differential-algebraic system**

Now read what the macro tier actually contains, on the same page:

- `:353-354` — "`φ(r)` is **Poisson-constrained**, `∇·(ε∇φ) = −ρ`, and is carried so that
  the constraint is *scored* rather than satisfied for free."
- `:444` — φ's residual row: "**algebraic constraint** `‖Σ_f ε_f·(∇φ)_f·A_f + ρ(c)·V_c‖²`"
- `:447` — j's residual row: "**algebraic closure** `‖j(c) − (q·μ_n·n·E + q·D_n·∇n)(c)‖²`"
- `:466-467` — "The potential and the current density are **algebraic constraint** balances
  with **no time derivative**."

Two of the five macro fields are algebraically determined by the other three. That is a
differential-algebraic system, and the page says so approvingly. **So a DAE is
disqualifying when it would admit `f_n` and a design feature when it admits `φ` and `j`.**
Both cannot hold.

**Which is right?** The DAE clause is the unsound half, and score-not-solve is why. The
oracle never integrates — `multiscale-state:110-111`: "The oracle **scores** each tier's law
violation; the operator supplies each tier's trajectory." An algebraic residual is perfectly
scorable; there is no integrator to trip over an index-1 constraint. The "integration
pathology" is a pathology of a solver the oracle does not contain.

Note that the *conclusion* about `f_n` is still right, for the other reason the same sentence
gives: promoting `f_n` "**double-counts its own moments**" — a redundancy-and-consistency
argument, which is sound and sufficient. The corpus has a good reason and a bad one stapled
together, and the bad one is the one both state pages elevate to an axiom.

**What would refute it.** A statement that the macro algebraic rows are not constraints on
the state but merely scored diagnostics — but `:487` lists them in the tier's state and
`:466` calls them constraint balances. Or a statement that the oracle does integrate
somewhere; `gamma-hat:78-92` and `multiscale-state:110` both deny it emphatically.

**Proposed correction.** Delete the constraint-manifold / integration-pathology clause from
both `unified-state:55-57` and `multiscale-state:88-90`, and let the exclusion of `f_n` rest
on moment double-counting, which is true. This is a *simplification* of the corpus's
argument, not a weakening of its conclusion.

---

### S9 — The "same scale" clause has no fixed referent, so the axiom's verdict flips with an input

**Severity: medium. Confidence: high.**

`multiscale-state:67-69` states the axiom:

> A quantity `y` is **emergent** from a tier — excluded from that tier's state — **iff** it
> is recoverable from that tier's state by coarse-graining **on the same timescale and the
> same scale**.

"The same scale" requires the tier to *have* a scale. The micro tier's is given as **"unit
cell"** (`multiscale-state:96`). But the corpus plans to leave it: `gamma-hat:187` — "Defect
and interface **supercells** grow `N_PW` linearly"; `born-oppenheimer-levels:25` — "for
version-1 defect **supercells** it is hours".

In a defect supercell, the vacancy concentration **is** recoverable from the micro state on
the same scale and at the same instant: count the missing sites in `(R_I, Z_I)`, divide by
the cell volume. By the axiom's own words it is then emergent and must stay out. But it is
the first field of the slow-state schema (`multiscale-state:143`, `conc[D,q]`).

Likewise `H_content` (`:145`): hydrogen atoms are ions in the micro tier with positions and
species labels, and the corpus's own defect universe carries hydrogen-decorated defects
(`V_Ga–nH`, `V_O–H`, `:127-128`). In any cell that contains them, `H_content` is a count.

**So the axiom returns different verdicts on the same quantity depending on how large the
input cell is** — and the cell size is supplied by `PeriodicityStructure`, an input, not
fixed by the tier. The axiom is not well-defined until the micro tier's scale is pinned, and
it is not pinned. The slow tier's own scale is given as "**unit cell to mesh**"
(`multiscale-state:97`), which *overlaps* the micro tier's, so at the overlap only the
timescale clause separates them — and S10 shows that clause does not do the work.

**What would refute it.** A stated dilution or cell-size condition bounding when the tiers
are independent. I searched both pages; none exists.

**Proposed correction.** State the condition explicitly — something of the form "the micro
cell is small enough that the expected defect count within it is ≪ 1, so slow-tier
concentrations are not resolvable in it" — and state what happens when a defect supercell
violates it (which is the MVP's own plan).

---

### S10 — The slow tier is classified by timescale, but "frozen" is not "not recoverable"

**Severity: medium. Confidence: high.**

`multiscale-state:78-82` classifies the slow tier:

> **Slow / history-dependent** — a different *timescale*. … At the micro timescale these are
> *frozen*: they evolve over hours to years … A frozen-in population is distinguishable from
> an equilibrium one only if the frozen-in one is stored.

The axiom's test (`:67-69`) is **recoverability by coarse-graining**. A frozen quantity is
maximally recoverable — it is sitting in the state, unchanging. Being slow is not being
hidden.

The sentence that carries the actual argument — "distinguishable from an equilibrium one
only if stored" — is about *predicting* the population from an equilibrium law, which is a
different claim from *recovering* it from the state. The axiom is stated in terms of
recovery and justified in terms of prediction. They are not the same test, and the page
never says which one governs.

What actually separates the slow tier from the micro tier is **scale** (a unit cell cannot
represent 10¹⁵ cm⁻³) plus **history** (the current state does not determine the past
integrated flux). Both are good arguments. The timescale classification the page uses is
the one that does not work.

**What would refute it.** A reading of "coarse-graining on the same timescale" as
"time-averaging over the micro relaxation time", under which a frozen quantity is invariant
and therefore trivially recovered — which strengthens my point rather than weakening it.

**Proposed correction.** Reclassify the slow tier under *history-dependence* and *scale*,
and state the axiom's test as recoverability from the tier's state **and its accessible
history**, which is what the corpus means.

---

### S11 — "Couple only parametrically, therefore no constraint manifold" holds only under a condition never stated

**Severity: medium. Confidence: medium-high.**

`unified-state:62-63` and `multiscale-state:86-90` both carry the claim; the principal named
it as the load-bearing argument for the whole stratification. Verified:

- **Micro ← slow and macro** is genuinely parametric: the micro tier fast-equilibrates at
  fixed slow and macro state (`multiscale-state:100-103`), and the reverse coupling is
  adiabatic-parameter dependence (`:305-310`). Sound.
- **Slow ← micro** is stated as driving by *time-averaged* micro quantities (`:291-302`).
  Sound in form.
- **But the independence claim needs the tiers not to share degrees of freedom**, and S9
  shows they do share them whenever the micro cell is large enough to contain a defect. The
  claim is conditional on a dilution assumption that is stated nowhere and that the MVP's
  own defect-supercell plan violates.

**A separate, smaller defect in the same section.** `multiscale-state:291` heads the table
"Each slow rate is parameterized by **time-averaged micro quantities**", and the driving
vector at `:302` is

```
ds/dt = Φ_kinetic( s ; ⟨T_L⟩_τ, ⟨j⟩_τ, ⟨E⟩_τ, ⟨ρ_dis⟩_τ, dx_ox/dt, dx_carbide/dt ; Environment )
```

Three of those six are **not micro quantities**. `ρ_dis` (dislocation density), `x_ox`
(oxide front) and `x_carbide` (carbide thickness) are all *slow-state fields*, listed as
such at `:146-148`. So the "adiabatic driving contract" — the thing that certifies the
coupling is parametric — includes the slow tier driving itself. That is fine as dynamics
(`ds/dt = Φ(s;…)` is an ODE in `s`), but it is mis-labeled, and the table row at `:298`
("`G_V` feeding vacancy generation | dislocation density and dislocation velocity") files a
slow-slow coupling under a micro-slow heading.

**What would refute it.** A stated separation-of-scales condition. None found.

**Proposed correction.** State the dilution condition; and split the driving vector into its
micro-supplied part `(⟨T_L⟩, ⟨j⟩, ⟨E⟩)` and its intra-slow part `(ρ_dis, x_ox, x_carbide)`.

---

### S12 — `T_e ≥ T_L` is scored as a Positivity residual, but it is an identity in the sign of `j·E`, and `j·E < 0` is physical

**Severity: medium. Confidence: high on the structure; medium on the frequency of `j·E < 0`.**

`multiscale-state:368-377`:

> `T_e − T_L = (2/3)(j·E)·τ_E/(n·k_B)` at steady state … `T_e` is **never state**; it is
> reconstructed from `(n, j, T_L)` and the supplied `τ_E`. … The positivity bound
> `T_e ≥ T_L` is scored as a `Positivity` residual.

The steady-state closure is dimensionally correct — I checked: `[j·E] = W·m⁻³`, `[τ_E] = s`,
`[n k_B] = J·m⁻³·K⁻¹`, quotient in K. The transient form is consistent with it. Both match
the standard two-temperature energy balance.

Two problems follow from combining them with the residual.

**(a) The residual carries no information about the operator's prediction.** `T_e` is not
state; the operator never predicts it. The oracle reconstructs it *by that formula*. Then

```
T_e ≥ T_L  ⟺  (2/3)(j·E)τ_E/(n k_B) ≥ 0  ⟺  j·E ≥ 0     (τ_E, n > 0)
```

so the residual is an identity in the sign of `j·E`, a quantity computed from other state
components. It fires or does not fire on the *reconstruction*, never on a prediction. It is
a structurally null residual carrying the name of a physical constraint — the same shape the
corpus already recognizes for `Degeneracy` (`residual-definitions:109-112`, "identically zero
by construction, so it is a generator-construction-bug tripwire and never a training-loss
term") but without that classification.

**(b) When it does fire, it is wrong to fire.** `j·E < 0` is realizable: wherever the
diffusion current opposes the local field (the depletion region of a forward-biased
junction), and over any device delivering rather than dissipating power. In those regions
the closure *correctly* returns `T_e < T_L`, and the residual would penalize a correct
trajectory. Carrier cooling below the lattice is a known feature of hydrodynamic transport
models, not an unphysicality to be masked.

**What would refute it.** A statement that the Positivity residual is cert-only for this
entry (as `Degeneracy` is). `residual-definitions:119-120` lists `Positivity` as a scored
category with no such carve-out, and `:283` puts it in the Warmup band, i.e. on from
training fraction 0.

**Proposed correction.** Either drop `T_e ≥ T_L` (it is implied by the closure), or move it
to cert-only as a tripwire on `τ_E > 0` and `n > 0`, which is what it actually tests.

---

### S13 — The transport regime windows overlap

**Severity: low-medium. Confidence: high.**

`multiscale-state:374-376`:

> Ohmic below ≈10⁴ V/cm where `T_e ≈ T_L`; warm from 10⁴ to 10⁵; **hot from 10⁵ to 10⁶**,
> which needs the momentum closure's mobility collapse; **saturated above a few × 10⁵**,
> where `j ≈ q·n·v_sat`.

`[3×10⁵, 10⁶]` V/cm falls in both "hot" and "saturated". The page states at `:56-58` that
these windows "gate the per-sample applicability mask, so their width is load-bearing" and
declares their *width* an open question — but an overlap is not a width uncertainty, it is
two answers for one sample, and no precedence rule is given.

**Proposed correction.** Make the four windows a partition with explicit boundaries, or
state which wins in the overlap.

---

### S14 — The structural/swept partition is specified as a per-field global bit; soundness requires it to be per-composition

**Severity: medium. Confidence: medium-high.**

`crystal-inputs:109-110`: "**Every environment field is either structural or swept**, and
the partition is what makes kernel caching sound." `compose-time-pipeline:377-378` keys the
cache on "a content hash of periodicity, decoration, and the *structural* part of the
environment" — one hash function, so one partition.

But whether a field is structural is not a property of the field. `applied_stress` is
structural for the symmetry-quotient stage (it lowers the point group, as `crystal-inputs:131-133`
itself says) and swept for `vibration-induced-vacancy-generation`, which reads `σ_stress`
as a scalar magnitude in a power law (`multiscale-state:211`). A single global bit cannot
express both. The page notices the tension and files it as an undecided *value* — "the hard
cases **in either direction**" — rather than as an ill-posed question. **No filling of the
partition can be correct while it is a function of the field alone.**

The sound form is per-composition: a field is structural for a composition if any formula in
that composition's graph consumes it at compile time. The page states neither that rule nor
any other.

A supporting observation on the one entry the corpus does fix. `temperature` is declared
swept (`crystal-inputs:129`). But temperature carries a compile-time-relevant threshold: the
quasi-harmonic approximation "suffices to about 800 °C" (`capability-slices:94`), above which
row 13 (self-consistent phonons) is required and is deferred to version 2. A swept
temperature crossing 1073 K therefore leaves the validity envelope of the only wired
vibrational treatment. Whether the environment box (`crystal-inputs:119-122`) encodes that
threshold is not stated. This is the page's own "misfiling is silent" failure
(`crystal-inputs:124-127`) applied to the one field it considers settled.

**What would refute it.** A statement that the fingerprint is computed per-composition over
the fields that composition's graph consumes at compile time. `compose-time-pipeline:377-382`
says the opposite — it defers the partition to `crystal-inputs`, which states it per-field.

**Proposed correction.** Restate the partition as a per-(field, composition) predicate
derived from the graph, and keep the global table only as a default with a stated
over-approximation rule.

---

### S15 — Carbide-growth thicknesses cannot be reproduced from the stated barriers

**Severity: low-medium. Confidence: high on the arithmetic; the literature check on the
prefactor ratios did not return (gap **G3**, §3) and does not affect the finding.**

`multiscale-state:215-219`, `carbide-growth-parabolic` (row 81): "Barriers by contact metal:
Ti **1.4 eV** (≈600 nm per 1000 h at 500 °C, severe), Mo **2.1 eV** (≈15 nm), W **2.4 eV**
(≈3 nm), Pt none."

With `x = √(2k t)` and `k = k₀·exp(−E/kT)`, thickness scales as `√(exp(−E/kT))`. Anchoring
on Ti at 600 nm and holding `k₀` fixed:

| metal | `E` | thickness at shared `k₀` | page |
|---|---|---|---|
| Ti | 1.4 eV | 600 nm | 600 nm |
| Mo | 2.1 eV | **3.1 nm** | 15 nm |
| W | 2.4 eV | **0.33 nm** | 3 nm |

Reproducing the stated numbers requires `k₀(Mo)/k₀(Ti) ≈ 23` and `k₀(W)/k₀(Ti) ≈ 83`. That
is not impossible — prefactors do vary between carbide systems — but **no prefactor is
stated for any metal**, so the four numbers cannot be checked, reproduced, or recomputed at
another temperature by anyone reading the page. Since the row's output `x_carbide` is a
slow-state field feeding `G_interface` (`multiscale-state:186`), the numbers are used.

**Proposed correction.** State `k₀` per metal, or state the temperature and time at which
each thickness was evaluated together with the source.

---

### S16 — The three-tier residual contract has no interface: two of the nineteen categories cannot be evaluated, and no `∂_t x` reaches any of them

**Severity: high. Confidence: high.**

`multiscale-state:478-500` states the "unified three-tier residual contract": `EOM/DefectPopulation`
and `EOM/Continuum` are scored categories in "**One `ResidualKey = (producer, axes)` space**
[that] spans all tiers", weighted by the operator, and placed in the Refine curriculum band
(`:286-287`). The macro residual is explicitly "score-not-solve: the operator supplies the
macro-state trajectory on the mesh" (`:474-475`).

The scoring interface is `pino-bridge:48-59`, described at `:14` as "**The only surface**" and
at `:61` as "**A single entry point**":

```
Validate(state    : UnifiedState,           -- the seven-tuple of unified-state
         env      : Environment,
         request  : all | {ResidualKey} | {ObservableRef},
         gradient : Skip | Compute)
       → ( residuals, values, cograds, cert )
```

**(a) No tier but the micro tier can enter.** `state` is annotated in the signature itself as
"the seven-tuple of unified-state". There is no slow-state argument and no macro-state argument.
The slow and macro tiers appear in `pino-bridge` only through `dynamics(tier)` (`:132-148`) —
which is the **evolver** hand-off, a tangent map for a consumer that *integrates*, on the
explicitly unclaimed path (`pino-bridge` open question `evolver-lowering-spec`: "No time-evolution
product verb is claimed until it is"). So two of the nineteen `CategoryTag` members have no
argument through which their state could arrive.

**(b) No time derivative reaches any `EOM/*` residual, and the corpus gives three different
accounts of where one comes from.** Every equation-of-motion residual is `‖∂_t x − (L δE/δx +
M δS/δx)‖²`. `Validate` takes one state, no rate, and no trajectory. The three accounts:

| where | account |
|---|---|
| `gamma-hat:83-86` | the operator **supplies** the rate — "it *scores* a supplied `∂_t γ̂`"; "**Scoring a proposed rate is not taking a step**" |
| `multiscale-state:284-286` | the oracle **finite-differences** it — "the oracle scores the finite-difference slow-state rate against the formula right-hand side at each step" |
| `pino-bridge:51-54` | neither — one state, no rate argument |

A supplied rate needs an argument. A finite difference needs two states. The signature provides
neither. Two of the three accounts are on my pages, so this is not solely a seam problem.

**What would refute it.** A `UnifiedState` type that is a union across tiers, or an unstated
convention that `state` carries a rate. `glossary:101` resolves `UnifiedState` to
`pino-bridge#validate`, which resolves it to "the seven-tuple of unified-state" — the loop
closes on the micro tier with no rate.

**Proposed correction (my side).** `multiscale-state` should state what the three-tier contract
requires of the seam — a per-tier state argument and an explicit rate or trajectory argument —
rather than asserting a shared `ResidualKey` space and leaving the interface to be inferred.
`gamma-hat:83-86` and `multiscale-state:284-286` must agree on who differentiates. **Flagged to
the principal** as a cross-subject contradiction with `pino-bridge`.

---

### S17 — Macro conservation is stated to hold by construction and is also a scored training residual

**Severity: medium. Confidence: medium-high.**

`multiscale-state:336-338`:

> The mesh is **conservative** — the face flux out of a cell is the flux into its neighbor — so
> the `Conservation` residual **holds discretely**.

If the oracle computes each face flux once from the operator-supplied fields and applies it with
opposite signs to the two adjacent cells — which is what a conservative finite-volume scheme
means, and what Scharfetter–Gummel at `:453` does — then `Σ_cells Σ_f j_f A_f` telescopes to the
boundary **whatever the operator predicts**. Global conservation is then an identity, carrying no
gradient and no information about the prediction.

The page's own idiom makes the tension explicit. Twenty lines later, at `:353-354`:

> `φ(r)` is Poisson-constrained … and is carried **so that the constraint is *scored* rather than
> satisfied for free**.

So the page distinguishes "scored" from "satisfied for free", and places macro conservation in
the second category — while `Conservation` is a scored category (`residual-definitions:113`) in
the Warmup band, on from training fraction 0 (`residual-definitions:283`). The corpus already has
the right classification for this situation and applies it to `Degeneracy`
(`residual-definitions:109-112`: "identically zero by construction, so it is a
generator-construction-bug tripwire and **never a training-loss term**"). Macro `Conservation` has
the same structure and does not get the same treatment.

**Where I am uncertain.** A charitable reading is that the sentence means "the discretization is
not itself a source of conservation error", which is true and worth saying. That reading is
available but is not what the sentence says, and the distinction decides whether a Warmup-band
training term is live or null. I am reporting it as class 2 — misinterpretable with consequences
— rather than as a flat error.

**Proposed correction.** Say which is meant. If conservation holds by construction at the macro
tier, mark that tier's `Conservation` entry cert-only, as `Degeneracy` is. If it does not, say
what breaks it (a non-conservative boundary condition, an operator-supplied flux rather than an
oracle-computed one) and where the residual gets its signal.

---

### S18 — The slow tier is presented as a GENERIC specialization, but an irradiation source is not an entropy-gradient flow

**Severity: medium. Confidence: medium.**

`multiscale-state:265-271`:

```
EOM/DefectPopulation[D,q,site] = ‖ dc_D^q/dt|_predicted − ( G^q_total[D] − c_D^q·k_ann^q[D] ) ‖²
```

> This is the slow-tier specialization of `‖dx_i/dt − (L·δE/δx_i + M·δS/δx_i)‖²`. Generation and
> annihilation are both branches of the single dissipative master-equation generator: `M` is the
> rate matrix … The slow tier has **no reversible bracket**.

For this to be a *specialization* rather than a coincidence of shape, one needs
`G_total − c·k_ann = M·δS/δc` for a positive-semidefinite `M` satisfying GENERIC's degeneracy
condition `M·δE/δc = 0` — which `generic-dynamics:132-138` requires **per tier**.

That holds for a closed master equation obeying detailed balance. It does not hold for
`G_total = G_thermal + G_irradiation + G_interface` (`multiscale-state:185`). `G_irradiation` is
supplied by `frenkel-pair-yield` from the external `radiation_flux` and `radiation_dose`
(`crystal-inputs:85-86`), and `G_interface` is driven by oxide and carbide front velocities. Both
are **external drives**: they inject defects, and energy, from outside the tier. An externally
driven source is not `M·δS/δc` for any friction matrix, and `M·δE/δc = 0` — energy conservation
within the tier — fails for exactly those branches.

The page half-notices this: it says the reversible part is "none; **energy sits in the state
energies**" (`:486`). But `M·δE/δx = 0` is a condition on `M`, not a statement about where energy
is stored, and it is a condition the corpus scores as a residual category (`Degeneracy`,
`residual-definitions:109`).

**What would refute it.** A statement that the slow tier's GENERIC structure holds only for the
thermal branch, with the irradiation and interface branches entering as an external forcing term
outside the bracket — which is the standard treatment of a driven system and would be correct.
Nothing on either page says it.

**Proposed correction.** Write the slow-tier equation of motion as
`dc/dt = M·δS/δc + F_ext`, with `F_ext = G_irradiation + G_interface`, and state that the
degeneracy condition applies to `M` alone. This is a small change and it makes the claim true.

---

### S19 — The slow-state schema carries the redundancy its own tier is defined to exclude

**Severity: medium-high. Confidence: high.**

`multiscale-state:141-148` types the slow fiber:

| Field | Type and unit | Index |
|---|---|---|
| `conc[D,q]` | `Concentration` (cm⁻³), non-negative | `DefectSpecies × ChargeState` |
| `charge_dist[D]` | `Simplex` over charge states, summing to 1 | `DefectSpecies → Simplex` |

`conc[D,q]` is already resolved per charge state. Therefore

```
charge_dist[D][q] = conc[D,q] / Σ_q' conc[D,q']
```

identically. `charge_dist` is a normalization of `conc`, carrying no independent information —
an **algebraic constraint among the slow tier's own state fields**. The page calls it "its
dynamic refinement" (`:152`), but there is nothing left to refine once the charge index is
present.

This matters because it is the third instance of the pattern in S8, in the tier whose defining
property is supposed to be its absence:

| tier | redundant field | constraint |
|---|---|---|
| macro | `φ` | `∇·(ε∇φ) = −ρ` (`:353`, `:444`) |
| macro | `j` | `j = qμ_n nE + qD_n∇n` (`:447`) |
| **slow** | **`charge_dist[D]`** | **`= conc[D,·] / Σ conc[D,·]`** |

And `unified-state:55-57` states that admitting a redundant quantity "would tie a constraint
manifold back onto the irreducible degrees of freedom". The slow tier does it to itself. Taken
with S8, the axiom is violated in every tier that the refinement admitted, which is the strongest
form of the answer to "does the refinement license anything?" — it licensed both new tiers, and
both carry exactly what the axiom exists to forbid.

**What would refute it.** A reading in which `conc[D,q]` is a *total* concentration per species
with `q` a nuisance index, or in which `charge_dist` evolves under a law that `conc` does not.
The schema says `DefectSpecies × ChargeState` for one and `DefectSpecies → Simplex` for the
other; there is no such reading. `:278` confirms both indices are live: "**Axes** are
`(DefectSpecies, ChargeState, SiteClass)`".

**Proposed correction.** Drop `charge_dist[D]`, or drop the charge index on `conc` and carry
`(conc[D], charge_dist[D])` as the pair — either is consistent. Carrying both is not.

---

### S20 — "The slow fiber is the dynamic promotion of `SiteDecoration.occupancy`" is true of one of six fields, and only for vacancies

**Severity: medium. Confidence: high.**

The promotion story is stated on both of my pages — `crystal-inputs:66-67` ("Its dynamic
promotion — the slow-state fiber whose initial condition it becomes") and
`multiscale-state:153-164`:

> **The slow fiber is the dynamic promotion of `SiteDecoration.occupancy` … not a mutation of the
> species labels.** … Occupancy is the right physical quantity: a vacancy is occupancy going to
> zero. The static `SiteDecoration.occupancy` becomes the **initial condition** `s(t=0)`.

Check it against the schema it claims to initialize (`:141-148`):

| slow field | is it an occupancy of a site? |
|---|---|
| `conc[D,q]` | **only for vacancy species.** An interstitial (`C_i`, `Ga_i`, `B_i`, `N_i`, `Al_i`) is an *addition*, not a lowered occupancy. A complex (`NV`, `NVN`, `N3V`, `V_Ga–nH`, `V_O–H`, `V_Ga–Ga_i–V_Ga`) is neither. Most of the `DefectSpecies` universe at `:122-128` is not vacancies. |
| `charge_dist[D]` | no — `SiteDecoration` carries a scalar "charge state" (`crystal-inputs:59`), not a distribution |
| `H_content` | no |
| `oxide_front` | no |
| `carbide_thickness` | no |
| `dislocation_density` | no |

So the stated mechanism initializes at most a *subset of one* of six fields. **The initial
condition for the other five is specified nowhere**, and `s(t=0)` is a required input to every
slow-tier trajectory the operator predicts and the oracle scores
(`EOM/DefectPopulation`, `:265`).

There is also a type gap even in the case that works: `SiteDecoration.occupancy` is a per-site
fraction, `conc[D,q]` is a volumetric concentration in cm⁻³. The conversion
(`conc = (1 − occupancy)·N_site`) is stated nowhere, and `N_site` — the site density — appears
only inside `G_thermal` at `:185` with no definition.

**What would refute it.** A statement elsewhere of where `oxide_front(0)`, `carbide_thickness(0)`,
`H_content(0)` and `dislocation_density(0)` come from. I searched both pages and
`crystal-inputs#site-decoration`; the only initial-condition statement in the subject is the one
quoted.

**Proposed correction.** State the initial condition for each of the six fields. Four of them
(`oxide_front`, `carbide_thickness`, `dislocation_density`, `H_content`) are as-fabricated
properties, not decorations — they may need a new input, which collides with the "alphabet is
exactly three wide" closure rule at `crystal-inputs:45`. That collision is worth surfacing rather
than absorbing.

---

### S21 — The level table assigns each regime to one level; the prose three lines later says regimes span levels, and for the MVP material the table's assignment is wrong

**Severity: medium. Confidence: high.**

`born-oppenheimer-levels:37-42` gives a "Regimes" column that reads as a partition — each of the
nine regimes appears exactly once:

| level | regimes |
|---|---|
| `quantum-electronic-substrate` (operates on `γ̂` and `A` **at fixed positions and cell**) | electronic, **optical**, magnetic |
| `born-oppenheimer-surface` | structural, mechanical |
| `equilibrium-statistics` | **thermal**, thermodynamic |
| `non-equilibrium-kinetics` | transport, chemical and surface |

Then `:44-46`:

> A **regime** is a navigational *view* across the levels that contribute to it — **the thermal
> regime spans equilibrium-statistics and the phonon transport of non-equilibrium-kinetics**.

The prose contradicts the table it sits under, using the table's own example. And it
under-counts: `generic-dynamics:119` extracts the thermal regime as "Eigendecomposition of
`∂²E_BO/∂u²` (phonons); BTE for phonon distribution" — the Hessian of `E_BO` is a
`born-oppenheimer-surface` object, so the thermal regime spans **three** levels, not the one the
table gives or the two the prose gives.

**The optical row is worse, and it is wrong for the MVP material specifically.** The
`quantum-electronic-substrate` level is defined as operating "**at fixed positions and cell**".
Diamond is an **indirect**-gap semiconductor: its fundamental absorption edge is entirely
phonon-assisted, because the Γ→Δ transition needs a phonon to conserve crystal momentum. That is
how the gap the corpus quotes was measured in the first place — Clark, Dean & Harris, Proc. R.
Soc. Lond. A 277, 312 (1964) identify the edge from its phonon-assisted structure, and
`born-oppenheimer-levels:110-111` quotes that gap. So for diamond, the optical regime cannot be
computed at a level with the ions frozen; it requires the vibrational spectrum, which lives two
levels up.

**What would refute it.** A statement that the Regimes column is indicative rather than a
partition. The column has no such qualifier and the anchor `hierarchy` is the page's own
canonical statement of the levels.

**Proposed correction.** Make the Regimes column many-to-many, or delete it and keep only the
prose statement that a regime is a view. Then state where phonon-assisted optical absorption is
computed for an indirect-gap host, since diamond is the MVP.

*A related point in someone else's subject, flagged to the principal:* `generic-dynamics:122`
extracts the optical regime as "Response of `γ̂` to `A(t)` via `L`; **absorption via `M`
(radiative damping)**". For an indirect-gap material the absorption edge is set by phonon-assisted
processes, not by radiative damping. That is a physics claim on the laws page, not mine.

---

### S22 — The slow tier's declared timescale does not follow from its declared barrier range, and six of its own barriers fall outside that range

**Severity: medium. Confidence: high (re-runnable arithmetic).**

`multiscale-state:78-82` defines the slow tier:

> At the micro timescale these are *frozen*: **they evolve over hours to years, set by Arrhenius
> barriers of 2–7 eV**

Two independent problems.

**(a) The range does not produce the timescale.** With `rate = ν₀·exp(−E_a/kT)` — the form the
page fixes for every slow formula at `:171-172` — and `ν₀ = 10¹³ s⁻¹` at the page's own 500 °C
reference point:

| barrier | `1/rate` at 773 K |
|---|---|
| 2.0 eV (stated floor) | **1.1 s** |
| 2.5 eV | 33 min |
| 3.1 eV | 1 year |
| 3.5 eV | 207 years |
| 7.0 eV (stated ceiling) | **1.4 × 10²⁵ years** |

The band that actually gives "hours to years" at 500 °C is **2.5 – 3.5 eV**. The stated floor is
a second and the stated ceiling exceeds the age of the universe by fifteen orders of magnitude.

**(b) Six of the page's own barriers are below the stated floor.** From its own formula set:
`C_i` 1.6–1.7 eV (`:190`), `V_Ga` in GaN 1.9 eV (`:190`), `V_O` in β-Ga₂O₃ 1.9–2.4 eV (`:191`),
hydrogen diffusion `E_diff = 1.7 eV` (`:197`), carbide growth on Ti 1.4 eV (`:217`). At 1.4 eV the
process completes in **134 µs**.

That last one is not a curiosity: the page calls the Ti carbide channel "**severe**" — it is the
fastest degradation path in the set and the reason Ti is a bad contact metal — and it sits 8
orders of magnitude faster than the tier that owns it, in a band the tier's own definition
excludes.

**Consequence for the stratification.** The tier table at `:96-98` gives the micro tier fs–ns and
the slow tier hours–years. **Nothing owns ns to hours**, and the corpus's own slow formulas
operate there. The adiabatic-driving argument itself survives — 134 µs is still five orders
slower than nanosecond micro equilibration, so time-averaging is still justified — but the
*declared band* is wrong, and the sentence that justifies the band by a barrier range is wrong in
both directions.

This is the concrete form of S10: the tier is classified by a timescale that its own contents do
not have.

**What would refute it.** A per-formula prefactor much smaller than 10¹³ s⁻¹. The ratio argument
is prefactor-sensitive here (unlike S4), so this one is conditional on `ν₀ ≈ 10¹³ s⁻¹` — the
standard attempt frequency, and the only value consistent with the page's other statements. To
move a 1.4 eV barrier into the "hours" band you would need `ν₀ ≈ 10⁵ s⁻¹`, which is not a lattice
attempt frequency. **No prefactor is stated anywhere for any of the nine formulas** — which is
itself the class-3 defect underneath this one.

**Proposed correction.** State `ν₀` per formula. Correct the band to the barriers the tier
actually contains, or state the timescale as a *range* (µs–years) and say what makes the tier
coherent other than its speed — history-dependence, which is the true criterion (S10).

---

### S23 — The `DefectSpecies` universe is declared closed and densely ordinal, but two of its members are unbounded families and most cannot be typed by its own record

**Severity: medium. Confidence: high.**

`multiscale-state:118-120`:

> `DefectSpecies` is a closed `Universe[T]` … with `carrier_kind = Closed` and
> `ordinal_policy = DenseU32`.

and `:130-131` gives the element record:

> `{name, site : LatticeSite, charge_states : List[Int], spin}`

**(a) `site : LatticeSite` is singular; most members are not.** From the enumerator at `:122-128`:
`NV` (2 sites), `NVN` (3), `N3V` (4), `V2` (2), `V_B–O` (2), `V_Al–O` (2), `V_Ga–O_N` (2),
`V_Ga–Ga_i–V_Ga` (3), `V_O–H` (2), `V_Al–nC_N` (1+n), `V_Ga–nH` (1+n). Only the simple vacancies,
interstitials and antisites are single-site. A record with one `LatticeSite` field cannot type the
majority of its own universe.

**(b) Two members are parameterized families, so the universe is not enumerable as declared.**
`V_Ga–nH` (GaN) and `V_Al–nC_N` (AlN) carry a free integer `n` with **no stated bound**. A
`Universe` with `carrier_kind = Closed` and `ordinal_policy = DenseU32` requires a finite member
list with a dense ordinal assignment; a family indexed by an unbounded `n` has neither. (In the
literature `n` is bounded — `V_Ga` in GaN is a triple acceptor, so `V_Ga–nH` runs `n = 1,2,3`.
The bound exists; the corpus does not state it, which is the defect.)

**This propagates.** `conc[D,q]` is indexed `DefectSpecies × ChargeState` with that dense ordinal
(`:143`), and `EOM/DefectPopulation` emits "**one weightable `ResidualLeaf` per species, charge and
site**" with "**no preaggregation**" (`:278-281`). A residual leaf per site, for species whose
record carries one site and whose count is unbounded, is not constructible.

**What would refute it.** A `LatticeSite` type that is itself a set or tuple, or a stated bound on
`n`. `LatticeSite` is not defined anywhere I could find in `journals/`; searching for it returns
only this record.

**Proposed correction.** Type the site field as a multiset of `LatticeSite`, and enumerate the
hydrogen and carbon complexes explicitly at their physical bounds (`n = 1..3` for `V_Ga–nH`)
rather than as a family — which is what "closed" requires and what the `schema_version` extension
rule at `:131-133` is for.

---

### S24 — The gauge: the partition is correct, the derivation of it is invalid, and the `A` slot has two incompatible definitions

**Severity: medium (down from the high it carried on arrival). Confidence: high on the
mathematics, high on the slot contradiction.**

This finding arrived from the principal as "the gauge is over-determined … Gauss's law
violated identically … a static applied field has nowhere to live", and with a live
disagreement between two of my undergraduates. **I am not signing it as it arrived.**
Three of its parts do not survive primary text; a fourth, narrower part does; and
underneath the disagreement there is a contradiction neither undergraduate found.

**The primary text.** Two places, and they are not equals:

- `unified-state:40-42` — "The vector potential is carried in the Weyl gauge `A₀ ≡ 0`,
  transverse `∇·A = 0`; the electrostatic sector lives in the matter functionals. **The
  normative gauge-and-partition statement is [generic-dynamics].**"
- `generic-dynamics:185-187`, under a heading marked **Normative** — "The state's `A` is
  carried in the **Weyl gauge** `A₀ ≡ 0`, with the remaining **time-independent gauge
  freedom** fixed by transversality `∇·A = 0` — the Coulomb-gauge radiation field."

**Correction 1 — the normative statement is not on my page.** `unified-state:40` carries
no `Normative` marker and explicitly forwards to `generic-dynamics`. So does the `(1/8π)`
energy functional, at `generic-dynamics:71` and `:189`. The gauge finding's primary home
is **postdoc-laws'**, not mine. What is mine is the slot definition, and that is where the
new defect is.

**Correction 2 — Gauss's law is not violated, and `E_∥` is not missing.**
`generic-dynamics:189-195` states three times that the longitudinal/electrostatic sector
is owned by the matter functionals — the Hartree term inside `E_KS[γ̂]` and the ion–ion
electrostatic channel — and "appears nowhere in `E_EM`, so no electrostatic energy is
double-counted". That is the **standard nonrelativistic-QED partition**: transverse field
dynamical, Coulomb interaction instantaneous in the matter sector. It is correct, it is
the textbook construction, and a reader implementing the section as written gets the
electrostatics. "`E_∥ ≡ 0` while `ρ ≠ 0`" and "at 1 MV/cm the missing piece dominates"
over-claim, and I am striking them rather than passing them on.

**Correction 3 — a static applied field is not homeless.** Transversality in Fourier is
`k·A_k = 0`. **At `k = 0` this is vacuous**, so the uniform mode is entirely unconstrained
by `∇·A = 0`, and a uniform field is carried by `A(t) = −cEt` (Gaussian, matching the
`(1/8π)` convention the corpus writes; `A(t) = −Et` in SI) — which is spatially uniform and
therefore satisfies `A₀ ≡ 0` and `∇·A = 0` simultaneously and exactly. This is the standard velocity-gauge treatment of a uniform
field in a periodic system, and it is precisely why **Berry-phase electric enthalpy is not
required**: the Berry-phase machinery, with its mesh-dependent critical field, is needed
only for the *scalar-potential* route, where `−E·r` is non-periodic and the spectrum is
unbounded below. The corpus has two available routes and picks neither explicitly — that
is the real defect here, and it is class 3, not class 4.

**What survives, and it is a naming error with teeth.** `generic-dynamics:186-187` does
not merely assert both conditions; it *derives* the second from the first, via "the
remaining **time-independent** gauge freedom". **That derivation cannot work, and its own
adjective is the proof.** Residual gauge freedom in Weyl gauge is `A → A + ∇χ(r)` with `χ`
time-independent (any `∂_t χ` would reintroduce `A₀`). Such a shift changes `∇·A` by
`∇²χ(r)` — a *time-independent* amount. But the obstruction is time-dependent: from
`E = −(1/c)∂_t A` and `∇·E = 4πρ`,

```
∂_t(∇·A) = −4πcρ    ⟹    ∇·A(r,t) = ∇·A(r,0) − 4πc ∫₀ᵗ ρ(r,t′) dt′
```

A time-independent `∇²χ` can cancel that at **one instant only**. Weyl and Coulomb are
alternative, mutually exclusive gauge fixings: Weyl keeps `A₀ = 0` and lets `∇·A ≠ 0`
carry the electrostatics; Coulomb keeps `∇·A = 0` and lets `A₀ ≠ 0` carry it. What the
page actually describes — transverse `A`, electrostatics in the matter functionals — is
**Coulomb gauge with the non-dynamical scalar potential eliminated**, which is sound. It
is not Weyl gauge, and it is not reached by fixing Weyl and then spending residual
freedom. **The partition is correct; the sentence that justifies it is not.** The fix is
one sentence.

**Resolving my two undergraduates — and I am not averaging them.**

- The one who judged it **defensible** was right that the *partition* is standard and
  correct, and right that the "electrostatic sector lives in the matter functionals"
  clause is doing real work. It is. No Gauss's-law violation follows.
- The one who judged it **over-determined** was right that the *literal conjunction* is
  unachievable where charge is present, and right that the page's own
  "time-independent" clause is what proves it.
- **Neither had the whole answer, and the reason is that they were reading different
  objects into the same symbol** — which is the actual defect, below.

**The new finding, and it is mine: the `A` slot is defined twice, incompatibly.**

`unified-state:37` types the slot:

```
A )     external EM vector potential       ∈ ℝ³ field A(r,t)
```

**External.** But three other places treat the same slot as the system's own field:

| where | what it makes `A` |
|---|---|
| `residual-definitions:74-89` | `EOM/A` is item 2 of "**Seven per micro state-component degree of freedom**", carrying the aggregate form `‖dx_i/dt − (L δE/δx_i + M δS/δx_i)‖²` — an **evolved** field with a GENERIC equation of motion |
| `generic-dynamics:71`, `:189` | `E_EM[A]` is a summand of the **system energy** `E[x]` |
| `generic-dynamics:201` | the minimal-coupling channel reads it |

**An external field is prescribed, not evolved, and you do not own its energy.** If `A` is
external, `E_EM[A]` does not belong in `E[x]` and `EOM/A` should not exist. If `A` is the
system's own radiation field, "external" is the wrong label — and then the Weyl/Coulomb
conflict above is live, because the system's own charges are the `ρ` that obstructs
transversality.

This is why the two readings could both be defended from real text: **on the "external"
reading the gauge sentence is consistent** (no sources inside the cell, so no obstruction),
**and on the "own radiation field" reading it is not.** The corpus has not fixed which,
so the sentence has no determinate truth value. That is a class-2 defect (a competent
reader binds the symbol to the wrong object) sitting under a class-4 one.

**And the applied field has a place but no path.** `applied_electric_field` occurs
**exactly once in the entire corpus** — its own table row at `crystal-inputs:80`, marked
`UNSEEDED`. Zero consumers. The contrast is inside the same table: `radiation_flux` at
`:85` names its consumer ("read by the displacement and …"). So the corpus knows how to
state a consumer and does so one row away. Nothing states that a uniform applied field
enters through `A`'s `k = 0` mode, or through anything else. This is S6's mechanism
applied to the field the 1 MV/cm target depends on.

**What would refute this finding.** A statement that `A` is decomposed into an external
prescribed part and an internal dynamical part, with `E_EM` and `EOM/A` scoped to the
latter. I searched `unified-state`, `generic-dynamics`, `residual-definitions` and
`coupling-structure`; `A` is a single undecomposed slot in all four.

**Proposed correction.** (i) Fix the slot definition — decide whether `A` is external,
dynamical, or a declared sum of both, and make `E_EM` and `EOM/A` agree with the choice.
(ii) On `generic-dynamics`, replace the derivation with the construction it is actually
describing: "`A` is the transverse radiation field in Coulomb gauge, `∇·A = 0`; the
non-dynamical scalar potential is eliminated in favor of the instantaneous Coulomb
interaction, which the matter functionals own." Delete "Weyl" and delete the appeal to
residual freedom. (iii) State how a uniform applied field enters, and name the route.

**This trap is marked `enforced`, and nothing enforces it.** `traps.md:379-384` carries
"Gauge and electrostatic partition … *Breaks:* electrostatic energy double-counted, and the
vector-potential equation of motion becomes gauge-dependent. — **enforced**,
[unified-state#slots], [generic-dynamics#gauge-partition]". Both anchors are the text S24
finds defective. I checked whether any mechanism stands behind the marker:
`journals/practice/traps.md` carries **45** `— enforced` markers, and
`grep -rn "enforced" tools/*.py` returns **two hits, both comments about an unrelated
citation rule**. No checker reads the marker, and none probes this trap. This is the
principal's defect class 4 confirmed from my side, on the specific trap whose subject
matter I own: the assertion that the hazard is handled is the *only* thing standing between
the hazard and the corpus.

**Flagged to the principal as cross-subject**, both on `generic-dynamics` and therefore
postdoc-laws': (a) the gauge derivation above; (b) **the energy functional is in Gaussian
units** — `E_EM = (1/8π)∫(|E_⊥|²+|B|²)` at `:71` and `:189` — in a corpus that is SI
everywhere else (`accuracy-ledger:144` uses `√(qE/4πε_sε₀)`; `multiscale-state` uses
`A·m⁻²`, `V/cm`, `J·m⁻³`). This does not cancel in a ratio: converting to SI, the electric
term scales by `1/(4πε₀)` and the magnetic term by `μ₀/(4π)`, whose quotient is
`1/(ε₀μ₀) = c²`. Since `|E| = c|B|` in a radiation field, using the Gaussian expression on
SI-valued fields weights the electric term **`c² ≈ 9×10¹⁶` times too heavily** relative to
the magnetic one. No single overall constant repairs it.

---

### S25 — The k-point paragraph names one sampling scheme and quotes the other one's count

**Severity: low-medium. Confidence: high (orbit enumeration below is re-runnable).**

*(Provenance, stated because it is unusual: this finding exists only because a reader
audited my plant copy, where I had changed 29 to 60, and did correct physics on top of the
false number — establishing that **both** counts are real, for different meshes. The plant
is withdrawn as W3; this is the real defect underneath it. I verified both counts
independently before recording it.)*

`gamma-hat:162-163`:

> an **8×8×8 Monkhorst–Pack mesh** gives **~29 irreducible k-points**

The two halves belong to different schemes. By explicit orbit enumeration over the 48
operations of `O_h` (inversion included, so time reversal adds nothing), on the fcc
reciprocal lattice:

| mesh | Γ-centered (unshifted) | Monkhorst–Pack shifted |
|---|---|---|
| 4×4×4 | 8 | 10 |
| 6×6×6 | 16 | 28 |
| **8×8×8** | **29** | **60** |

The 4×4×4 row is the control: 8 and 10 are the published values for fcc and reproduce
exactly, so the enumerator is calibrated before it is trusted on 8×8×8.

**Verified three independent ways, and they agree to the integer at N = 4, 6 and 8:** my
from-scratch orbit enumeration above; a Burnside cross-check; and `spglib` run against the
real diamond cell. Three routes, one answer — this finding does not rest on any single
implementation.

**29 is the Γ-centered count. 60 is the Monkhorst–Pack count.** The original prescription
(Monkhorst & Pack, *Phys. Rev. B* **13**, 5188 (1976)) places points at
`u_r = (2r − q − 1)/2q`, which for even `q` is offset half a step from Γ — the shifted mesh.
The distinction is not pedantic in practice: VASP's `KPOINTS` file has separate `Gamma` and
`Monkhorst-Pack` modes, and entering `Monkhorst-Pack / 8 8 8` for diamond returns 60
irreducible points, not 29.

**Consequence.** `N_k` multiplies both memory budgets at `:165-172`. A reader who follows
the *name* gets 60 and doubles both figures; a reader who follows the *number* gets 29. With
S3's correction to `N_PW` the two errors partly offset, which is worth stating so nobody
treats the page's 18 MB as accidentally right:

| | `N_PW` | `N_k` | orbital storage |
|---|---|---|---|
| page as written | 1000 | 29 | 18.6 MB |
| corrected, Γ-centered | 181 | 29 | 3.4 MB |
| corrected, if MP-shifted is meant | 181 | 60 | 6.9 MB |

**On how this finding was arrived at, stated plainly because the route matters.** The
contaminated claim was that the page's prose says 60 and its computations use 29. **That
claim was false** — the page says 29 throughout, and no "60" occurs in it. The real defect is
the reverse of the reported one and was found by checking the report rather than by
accepting it. It is recorded here as *discovered while correcting a contaminated report*,
and it must not be folded into the register as though the original claim had been right.
The withdrawal (W3) and this finding are both true, and they are not the same statement.

**What would refute it.** A statement that "Monkhorst–Pack" is being used in the loose sense
of "any regular mesh". The page gives no such gloss, and it pairs the term with a specific
integer, which is exactly the context where the loose sense stops being safe.

**Proposed correction.** Say which mesh: either "an 8×8×8 **Γ-centered** mesh gives ~29
irreducible k-points" or "an 8×8×8 Monkhorst–Pack mesh gives ~60", and carry the matching
`N_k` through both budget lines. The first is the smaller change and is consistent with the
numbers already on the page.

---

## 2 · Findings that did not survive

### 2a · Withdrawn as contaminated — five defects that are mine, not the corpus's

These reached the principal, and two reached `audit/REGISTER.md`, as findings against this
subject. **They are calibration defects I planted in a scratch copy.** Each row below gives
the primary text that refutes it, so the withdrawal is checkable without trusting me.

| # | reported as | primary text in `journals/` | verdict |
|---|---|---|---|
| W1 | Einstein relation inverted in the normative statement, `D = μq/k_BT`, wrong by ~1500× | `multiscale-state:382` — "The Einstein relation is `D = μ·k_B·T/q`"; `:414` — "Einstein `D = μk_BT/q`, nondegenerate" | **both correct.** Plant P2. Struck from `REGISTER.md:79` and severity row #8 |
| W2 | PBE diamond gap stated 3.1 eV against ≈4.2 | `born-oppenheimer-levels:110` — "underestimates the diamond indirect gap by about 23% — roughly **4.2 eV** against a measured" | **correct.** Plant P1. Struck from `REGISTER.md:91` |
| W3 | k-point count says 60 in prose while computations use 29 | `gamma-hat:163` — "**~29 irreducible k-points**". `grep -rn "60" journals/` returns no such claim | **no contradiction exists.** Plant P6 |
| W4 | `temperature` swept in a table and structural in prose on the same page | `crystal-inputs:77` — "the one field the corpus fixes as **swept**"; `:129` — "`temperature` is **swept**" | **consistent.** Plant P5 |
| W5 | Scharfetter–Gummel Bernoulli guard declared unnecessary; 0/0 at `Δψ→0` | `multiscale-state:460-461` — "with one removable singularity at `Δψ → 0` **guarded by the series** `B(t) ≈ 1 − t/2`" | **the guard is present and correct.** Plant P4 |

**Method note.** All five were caught by the rule the principal issued mid-run — *a finding
rests on the primary text, never a summary of it*. I applied it to a summary from the
principal, which is the case the rule is least comfortable in and most needed for. Had I
taken the relay at face value, this file would have filed five fabricated findings against
a corpus whose own history includes a fabricated citation, and they would have looked like
wins: five mechanically checkable value errors, exactly the profile of a productive sweep.

**What was real in the relay:** `N_PW ≈ 1000` (my S3, independently verified), the carrier
continuity defect (my S1, independently verified, and the principal's convention proof
strengthened it), and the hole-schema misclassification (my S2, and the principal's framing
of it is better than mine and is now in the text).

**One real finding the contamination handed us.** Whoever read the k-point plant did
correct physics on top of it: 29 is the **Γ-centered** 8×8×8 count and 60 is the **shifted**
mesh. `gamma-hat:162` names "Monkhorst–Pack", whose prescription for even subdivisions is
the shifted mesh, while quoting the Γ-centered count — see S25.

### 2b · Investigated and rejected on the merits

| # | Investigated | Why it did not survive |
|---|---|---|
| N1 | **Scharfetter–Gummel is wrong.** | It is **correct**, and this is the strongest clean verdict in the subject. I derived it: assume `J_n` constant between nodes and `ψ` linear, use the integrating factor `e^{−ψ/V_T}`, integrate; the result is `J_n = (qD/h)[n_{i+1}B(Δ) − n_i B(−Δ)]` with `Δ = (ψ_{i+1}−ψ_i)/V_T`, which is `multiscale-state:453` term for term **including which node pairs with which Bernoulli argument** — the pairing is where transcriptions of this formula usually fail, and it is right here. `B(t) ≈ 1 − t/2` is the correct series for the removable singularity, and the guard is present at `:460-461`. A second check reached me through the principal and I am recording it because it is independent of mine and stronger: the closed form was **verified numerically against direct integration to 1.7×10⁻¹³**. Nothing to report — and the contrast with S1 is the point: the hard formula on this page is right and the easy one is not. |
| N2 | **The Péclet number is wrong.** | It is **right**: 1 MV/cm × 10 nm = 1 V, against `k_BT/q = 25.85 mV` at 300 K, gives `Pe = 38.7 ≈ 40`. I checked it again at the corpus's own 500 °C harsh-environment point, where `k_BT/q = 66.6 mV` and `Pe = 15`. The conclusion (central differencing unusable) survives at both, so the 300 K choice is not load-bearing. Not a finding. |
| N3 | **Drift-diffusion carrier sign convention is wrong.** | The claim at `multiscale-state:381` — "**only the diffusion term changes sign between carriers, never the drift term**" — is **correct** for `j_n = qμ_n nE + qD_n∇n`, `j_p = qμ_p pE − qD_p∇p` with `q > 0`. This is the standard textbook pair. Notable that the corpus got this right and the continuity sign wrong (S1). |
| N4 | **The degenerate Einstein relation is wrong.** | `D/μ = (k_BT/q)·F_{1/2}(η)/F_{−1/2}(η)` with `η = (E_F − E_C)/k_BT` (`multiscale-state:390-392`) is the standard generalized Einstein relation. Correct. The surrounding treatment (nondegenerate form in v1, discrepancy entered as a declared model-form error) is honest and well-shaped. |
| N5 | **The Poisson equation and the heat equation are wrong.** | Both correct. `∇·(ε∇φ) = −ρ` with `ρ = q(p − n + N_D⁺ − N_A⁻)`; `C_p ρ_m ∂_t T_L − ∇·(κ∇T_L) = j·E`. The finite-volume rows for `T_L` and `φ` also reduce correctly under the divergence theorem — I checked the `1/V_c` factors cancel as intended. Only the carrier rows are wrong (S1). |
| N6 | **The homogenization table has a wrong relation.** | Spot-checked eight rows: thermal diffusivity `κ/(C_pρ_m)`; `σ = qnμ₀`; Caughey–Thomas `μ(E) = μ₀[1+(μ₀E/v_sat)^β]^{−1/β}`; Chynoweth `a·exp(−b/E)`; multiplication factor `M = 1/(1−∫α dx)`; avalanche generation `α_n n v_n + α_p p v_p`; SRH lifetime `τ_n = 1/(σ_n v_th N_T)`; Robin interface condition `q_f = ΔT/TBR`. All standard and correctly written. |
| N7 | **The `frenkel-pair-yield` dimensional argument is wrong.** | It is **right and unusually careful**: `Φ [cm⁻²] × Σ_d [cm⁻¹] × N_d [1] = cm⁻³`, and the page explicitly says why the bare product without `Σ_d` would be a fluence rather than a density (`multiscale-state:246-249`). This is the corpus catching its own dimensional error, and it is worth saying so. |
| N8 | **The 8×8×8 → 29 irreducible k-point count is wrong.** | **Confirmed correct** by explicit orbit enumeration under `O_h`. See S3 — this is what pins the cell and therefore establishes that `N_PW` is the wrong number, not the cell. |
| N9 | **The hydrogen-diffusion range is wrong.** | `√(Dt)` with `D = 10⁻¹³ cm²/s` and `t = 1000 h` gives 6.0 µm, exactly as stated (`multiscale-state:198`). The implied `D₀ = 1.2×10⁻² cm²/s` at `E_diff = 1.7 eV` is physically ordinary. Internally consistent. |
| N10 | **`G_thermal` for diamond vacancies is not actually negligible at 773 K.** | `exp(−7.2/k_BT) = 1.2×10⁻⁴⁷` at 773 K. The page's conclusion — that the 500 °C generation budget is dominated by `G_interface` and `G_irradiation` — follows. Correct. |
| N11 | **`unified-state`'s wire-schema gap is an undeclared omission.** | It is **declared**, precisely and with its consequence named (`unified-state:74-84`). Per the brief, declared open questions are honest and out of scope. It reappears in S7 only because a *different* page relies on the missing content without noting the dependency. |
| N12 | **`Crystal` being undefined is a finding.** | Declared open (`crystal-inputs:31-33`, `:145-156`), with both candidate readings stated and the inference from call sites given. Honest. Not a finding. |
| N13 | **`EOM/Z` over an immutable slot.** | Real, but **already owned**: the laws postdoc's L6 (`audit/findings/laws.md:276+`) covers it with the same evidence. I add only that `unified-state:50` calls all seven slots "the irreducible **degrees of freedom**", which extends the contradiction onto my page — an immutable discrete label is not a degree of freedom. Reported as a note, not a separate finding. |
| N14 | **Group order "at most 192" (`compose-time-pipeline:362`) is wrong** — the largest crystallographic point group is `O_h` with 48. | Withdrawn: 192 = 96 (the `O_h` double group) × 2 (antiunitary time reversal), which is defensible for magnetic double groups, and `coupling-structure:231` does work with "Fd-3m + time reversal". Also not my page. |
| N15 | **`p_O2` listed as a 13th field while declared "not an independent field"** makes the count 13-or-12. | The page's internal counting is self-consistent (8 untyped + 5 typed = 13, and both sub-counts are stated correctly). The redundancy question is real and its check did not return (gap **G4**, §3); the *count* is not a defect either way. |
| N16 | **`sp³d⁵` warm start should be 36×36 with spin.** | The page says 18×18, which is right for a spinless model, and a warm-start initializer for an SCF inner loop is legitimately spinless. Logged as an ambiguity, not a defect, since `γ̂` is elsewhere a Pauli spinor and nothing states the initializer drops spin. |

---

## 3 · Shaped gaps

**No gap in this subject is blocked by an unreachable source.** Acquisition item A1 closed
without a purchase (§4); every other finding rests on primary corpus text plus arithmetic I
ran myself. So there is nothing here in the four-part paywall form.

There are, however, **four directed checks that were dispatched and never returned** — the
session hit its limit while they were running. That is a different kind of gap and I am
declaring it in the same shape, because the effect on a reader is identical: a finding whose
support is thinner than the surrounding text implies. All four are literature questions, all
four are reachable, and none of them blocks the finding it attaches to.

| check | what it would settle | the conclusion without it | branches | what depends on it |
|---|---|---|---|---|
| **G1** · does platelet nucleation proceed directly from substitutional N, or at a later aggregation stage? | whether `platelet-nucleation-allen-cahn` (`multiscale-state:204-207`) is named for the right reaction | the formula's **rate law** is the N_s → A-center reaction while its **name** is platelet nucleation; the mismatch is visible without the literature | if platelets do nucleate from N_s, the name is fine and only the half-life pair is wrong; if not, the row conflates two stages and needs splitting | **S4's naming remark only.** S4's core result — that no prefactor reconciles 3.5 eV with years-at-500 °C and hours-at-1000 °C — is prefactor-independent arithmetic and does not wait on this |
| **G2** · is the G₀W₀ quasi-particle shift's sensitivity to strain approximately constant over the validity radius? | whether the first-order staleness estimator is *numerically* adequate even though it is not a bound | it is not a bound regardless (S7a), and the units argument (S7b) and the undefined `‖Δx‖` (S7c) are independent of it | if the sensitivity is near-constant, S7 is a rigor defect with small practical consequence; if it varies strongly, the estimator also under-reports | **the severity of S7, not its validity.** S7(a)–(c) stand either way |
| **G3** · are carbide-growth prefactors for Ti/Mo/W in the ratios the stated thicknesses require (≈1 : 23 : 83)? | whether `carbide-growth-parabolic`'s four numbers are reproducible | the numbers **cannot be checked from the page**, because no prefactor is stated for any metal — which is the finding | if the literature ratios match, the values are right and only the *statement* is incomplete; if not, the values are wrong too | **S15's severity.** The "not reproducible from stated inputs" finding holds either way |
| **G4** · is `p_O2` genuinely derivable from `chemical_potentials`, or an independent field? | whether the `Environment` record has a redundant thirteenth field | the record's **count** is internally consistent (N15), so this is a redundancy question, not a counting one | if derivable, `p_O2` should be removed or marked derived; if independent, the "not an independent field" note at `crystal-inputs` is wrong | **nothing.** N15 already rejects the counting finding on other grounds |

**None of these four changes a finding's verdict; three change a severity and one changes a
remark.** I am stating that explicitly so the next reader does not treat the subject as
provisional. The findings in §1 do not rest on unreturned work.

---

## 4 · Acquisition requests

**A1 — CLOSED. No purchase required.** *(Retained rather than deleted, because the way it
closed is the point.)*

- **What it asked:** how many plane waves per k-point a production code actually reports,
  to check the corrected count (181 exact / 206 asymptotic) against `N_PW ≈ 1000`.
- **How it closed:** not with the diamond dataset it named. A VASP `OUTCAR` for an unrelated
  system — H₂ in a box, `~/Downloads/OUTCAR` — validates the closed-form count to **0.08%**
  (S3). Since the formula is not system-specific, a run on *any* system tests it, and a run
  on a *dissimilar* system tests it harder. **The blocked item was never the diamond data;
  it was the formula's trustworthiness, and that is separable.**
- **What it teaches about routing around a block:** the acquisition request as I first wrote
  it named the one artifact I could not reach and would have sat open indefinitely. Asking
  instead what the artifact was *for* made a file already on the machine sufficient.
- **Residual value in the diamond dataset:** none for S3. Memory records a 1,179-row diamond
  VASP strain sweep at `~/Downloads/test_files_for_diamond_recovered/`, not present at that
  path on this machine. It would still be useful for the accuracy subject's bridge feedstock,
  which is not mine.

**No open acquisition requests for this subject.** No finding in this file waits on a paper.

---

## 5 · Calibration

### Result: 5 of 7 — and it is the audit's only blind calibration

Seven defects were planted in a scratch copy of all five state pages
(`.../scratchpad/state-audit/calib/`). **The calibration then ran itself, by accident, and
that is what makes it worth more than the six self-designed ones in the register.**

A reader in the fleet audited the scratch copy believing it to be the corpus, found five of
the seven, and reported them upward as corpus defects. Two reached `REGISTER.md`. The
reader **did not know it was reading a plant copy** — no expectation of defects, no count
to hit, no knowledge that a score was being kept. The principal's register records that
"the blind-calibration arm never ran; every calibration above is self-designed." It ran.
This was it.

| plant | class | found? |
|---|---|---|
| P1 · PBE gap `4.2 → 3.1 eV` | 4 false value | **found** |
| P2 · Einstein relation inverted | 4 inverted formula | **found** |
| P3 · "Reference instantiations … are held here" | 1 contradiction, adjacent | **missed** |
| P4 · deleted the Bernoulli singularity guard | 3 missing info | **found** |
| P5 · `temperature` swept → structural | 1 contradiction, cross-page | **found** |
| P6 · `29 → 60` irreducible k-points | 4 false value | **found** |
| P7 · "Hellmann–Feynman forces (exact at any basis-set size)" | 4 false physics, no internal tell | **missed** |

**5 of 7. Reported as found, not rounded.**

**The detection was an accident of routing, and that is the part to worry about.** These
plants were caught only because they were handed back to the agent that wrote them. I
recognized the five instantly — not by auditing them, but by recognizing my own work. **Sent
to any other subject, nothing in this program as designed would have found them.** No agent
verifies a received finding against the file it names; no channel distinguishes a plant from
a finding, because a plant that could be distinguished would not be testing anything. The
structural cause outlives this incident: **plants and findings are indistinguishable by
construction, so when they travel the same channel to the same reader, contamination is the
default rather than a lapse.** Vigilance is not the fix; channel separation is — a
calibration result should report a score and a method verdict and never a defect list, and
any agent reporting a defect should name the file it verified against.

Two observations about *how* it found them, both from the reported text rather than from the
score:

- On P2 the reader noted "while two other statements on the same page are correct" — it
  located the internal inconsistency, not just the wrong formula. On P4 it added "which is
  the quasi-neutral bulk — the majority of mesh cells", which is correct physics and is not
  in the plant. On P6 it derived that 29 and 60 are both real counts for different meshes.
  **Where the method worked, it worked well and went beyond the plant.**

**The two misses are the result, and they are not symmetrical.**

**P7 missing is the designed outcome and confirms the method's stated boundary.** It was
built to require outside knowledge — Hellmann–Feynman forces are exact only for a complete
or nuclear-position-independent basis; a finite atom-centered basis leaves Pulay terms — and
to leave **no internal trace**. A method that reads for internal consistency cannot catch
it. That is a known, bounded limitation, and it matches the register's pattern: two other
subjects reported the same class of miss ("audits structure and sign, not magnitudes";
"misses prose surrounding an equation").

**P3 missing is the alarming one, and it should change how the fleet reads.** P3 was
designed as the *easy* plant: a flat self-contradiction between **two adjacent sentences**
on `unified-state:70` — "This library holds no values of `x(t)`. Reference instantiations of
`x(t)` for each anchored host are held here and reused across compositions." The second
sentence denies the first, immediately, in plain prose. No arithmetic, no outside knowledge,
no cross-page lookup. It was walked past by a reader that caught five numeric and cross-page
defects in the same sweep.

The inference I draw — and I hold it with medium confidence, since it rests on one miss —
is that **the fleet's reading is tuned to values and to cross-references, and is weakest on
plain prose asserting two incompatible things in one place.** That is not a marginal class.
It is defect class 1 in the register's own taxonomy ("a claim that resolves but is not
true"), and it is the class the corpus's checkers are structurally blind to, since a
sentence contradicting its neighbor still has valid links. **A gate that catches five of
five value errors and zero of one adjacent prose contradiction is not an 83% gate; it is
two gates, one of which is untested and one of which just failed its only trial.**

I would not certify any part of this subject clean against class-1 prose contradictions on
the strength of this calibration, and I have not — see §6.

The planted set, by class:

| id | page | class | defect | design intent |
|---|---|---|---|---|
| P1 | `born-oppenheimer-levels` | 4 false value | PBE diamond gap `4.2 → 3.1 eV`, leaving "about 23%" unchanged | catchable two ways: wrong DFT value, and internal arithmetic |
| P2 | `multiscale-state` | 4 inverted formula | Einstein relation `D = μk_BT/q → D = μq/(k_BT)` | catchable by dimensions alone — the easiest plant |
| P3 | `unified-state` | 1 contradiction | added "Reference instantiations of `x(t)` … are held here" two clauses after "This library holds no values of `x(t)`" | flat self-contradiction, adjacent |
| P4 | `multiscale-state` | 3 missing info | deleted the removable-singularity guard on `B(t) = t/(e^t−1)` at `Δψ → 0` | requires noticing an absence, not an error |
| P5 | `crystal-inputs` | 1 contradiction, cross-page | `temperature` flipped from swept to structural | contradicts `compose-time-pipeline:379-380`, which names a temperature sweep as *the* runtime-input example |
| P6 | `gamma-hat` | 4 false value | `29 → 60` irreducible k-points | catchable two ways: wrong fcc symmetry reduction, and inconsistent with the 29 used two lines below |
| P7 | `born-oppenheimer-levels` | 4 false physics, no internal tell | "Hellmann–Feynman forces **(exact at any basis-set size)**" | requires outside knowledge (Pulay forces); **no internal inconsistency to trip on** — the hard one |

P7 was designed as the honest test of the method, on the reasoning that every other plant
leaves a trace inside the document and P7 does not. **That reasoning was half wrong, and the
result exposed it.** P3 leaves the most conspicuous trace of all seven — a denial in the very
next sentence — and was missed anyway. Leaving a trace and being *found* are not the same
property, and my design conflated them: I graded the plants by how much evidence they leave,
not by whether the instrument reads that kind of evidence. The instrument reads values and
cross-references. P3 was neither, and I had no plant that tested prose-against-adjacent-prose
except the one I had classified as trivially easy.

**A calibration set can only measure the instrument along the axes its designer thought to
vary.** Mine varied class and difficulty; it did not vary *evidence type*, and evidence type
turned out to be the axis that mattered. That is a defect in my calibration design, and I am
recording it rather than the flattering reading — which would be that I planted a hard one
and a lucky one.

---

## 6 · Evidence transcript for what I am calling clean

See §2, which is the transcript: sixteen specific comparisons, each naming the check run and
its result.

**On delegation, and why nothing here rests on an undergraduate's word.** I dispatched two
directed checks in this session — one on the k-point and plane-wave counts, one on the
continuity convention proof and consequence arithmetic. **I then ran both myself**, in full,
rather than waiting on them: the orbit enumeration over `O_h` (with the 4×4×4 → 8/10 control
against published tables), the `N_PW` formula validated to 0.08% against a real VASP
`OUTCAR`, the three-row face-normal reduction, the loss geometry with its asymptotic check,
the two-channel scale ratio using the corpus's own Chynoweth parameters, and the ten-pattern
control sweep for competing continuity statements. Every number in S1, S3 and S25 is one I
computed, with the script preserved. Neither undergraduate had returned when this file was
finalized, and **no finding in it is waiting on one** — if they return with a disagreement it
is a check on me, not a gap in the evidence.

That is deliberate given how this session began. The five withdrawn findings in §2a reached
me from a trusted upstream with severity already attached, and every one dissolved on
contact with a `grep`. **I did not want the repair for that failure to be another layer of
delegation.**

The areas I am prepared to call clean on that basis are:

- **The macro-tier constitutive relations and homogenization map** — sixteen formulas
  checked term by term against standard references (N3–N7). Every one correct. The macro
  tier's *physics content* is in good shape; its *bookkeeping* (S1, S2) is not, and the
  contrast is sharp enough to be worth stating: someone who knew the physics wrote the
  formulas, and the continuity signs were written by transcription.
- **The finite-volume discretization machinery** — conservation form, face fluxes, the
  Scharfetter–Gummel exponential fitting and its singularity guard, the Péclet argument
  (N1, N2, N5). Correct and unusually well-motivated.
- **The `gamma-hat` sizing chain except `N_PW`** — cell, band count, k-point count,
  tight-binding dimension, and the arithmetic of both budget formulas (N8, and S3's table).

I am **not** calling clean: the emergence axiom and tier stratification (S8–S11), the
`Environment` record (S6, S14), the seven-tuple's slot statuses (S24 found one slot with
two definitions; I have not audited the other six for the same failure), the gauge
statement beyond S24's scope, or the mean-field boundary.

**A limit on all of the above, from §5.** My calibration passed 5 of 5 on value errors and
cross-page contradictions, and **0 of 1 on an adjacent prose self-contradiction**. Every
clean verdict in this section rests on comparisons of the first two kinds — formulas
against references, numbers against arithmetic, claims against their use sites. **None of
it is evidence about the third kind.** The areas above are clean *of value and reference
defects*; a sentence on any of those pages that contradicts its own neighbor in plain
prose would not have been caught by what I ran, and P3 is the demonstration. This is not a
hedge — it is the specific gate my calibration measured and failed, and it should be read
as narrowing every clean verdict above rather than as a caveat attached to none of them.

The cheapest repair is a targeted second pass reading only for adjacent self-contradiction,
with no arithmetic and no cross-referencing — a different instrument, not more of the same
one. I did not have the slots to run it.

---

## 7 · Log-worthy advancements

Reported, not written — `log/timeline.md` has a single writer.

0. **The audit's blind-calibration arm ran, and returned 5 of 7** (§5). It ran by accident,
   through a scratch copy that leaked into the evidence chain, and it is the only
   calibration in this audit not designed by the agent it scored. Two entries belong in the
   record: the score, and the **asymmetry of the misses** — five value-and-cross-reference
   defects caught, one adjacent prose self-contradiction walked past. The second is a
   method finding about the fleet, not about this subject, and it names the class the
   corpus's link-checkers are structurally blind to.

0b. **A method rule, paid for by a near-miss of my own:** *the primary-text rule binds
   hardest on evidence that arrives from inside the audit.* Five findings reached me from
   the principal with severity attached and two already in the register; all five were
   mine, planted, and refuted by one `grep` each. Summaries from a trusted upstream are
   exactly where the rule feels least necessary and is most load-bearing.

1. **The emergence axiom's stated rationale is void and its conclusion survives on a
   different, sound argument** (S8). This is a genuine simplification of the corpus's
   foundations, not a defect report: two pages can drop a clause and get stronger.
2. **Two independent audit subjects trace an unusable error-model quantity to one missing
   declaration** — the per-slot unit convention on `unified-state` (S7, and the laws
   postdoc's L5). The wire-schema open question should be reclassified from a serialization
   gap to a numerical one, because it currently blocks `δ_PSD` and the dressing-staleness
   term.
3. **The `N_PW` correction inverts the stated justification for the density-matrix encoding**
   (S3): at MVP scale the encoding is an optimization, and the feasibility argument that the
   page rests on returns only at supercell scale — which is the budget the page already
   declares missing. The design is unchanged; its rationale moves.

4. **The carrier-continuity defect has a doping-independent size** (S1e). Against
   recombination the ratio is `v_sat·τ/L`; against impact ionization it is `1/(α·L)`. Both
   cancel the carrier density, both are a *length over the cell size* — recombination length
   and ionization length respectively — and both land near 10⁴ at the corpus's operating
   point by independent physics. Against the two channels together the figure is **5.06×10³**
   (the estimate that reached me, 10⁴, counted one denominator). This converts the finding
   from a point estimate into a statement about the whole declared envelope: the ratio *grows*
   under mesh refinement, and at `τ = 1 ps` it is still 10. **No choice of bias, doping,
   injection level or lifetime makes the residual usable while the sign stands.**

5. **The gauge finding shrank on contact with primary text, and a different defect was
   underneath it** (S24). The over-determination is real as mathematics but the partition it
   was said to break is correct and standard; what is actually broken is the *derivation*
   ("time-independent gauge freedom" cannot fix a time-dependent obstruction) and, beneath
   that, the `A` slot's identity — typed **external** on `unified-state:37` while carrying
   an equation of motion and a term in the system energy. Worth logging as a shape: **two
   competent readers disagreeing about one sentence was the symptom, and an undefined object
   was the cause.** Averaging them would have buried it.
