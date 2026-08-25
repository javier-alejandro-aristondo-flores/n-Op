# UWBG Neural-Operator Corpus: Literature Sweep, Transformation Catalog & Block Design

## TL;DR
- The single most valuable, genuinely-open direction is **ρ→ELF field-to-field learning on the 547 cross-material runs**: predicting the electron localization function *from the true self-consistent DFT density* has NEVER been published (only geometry→ELF and superposed-atomic-density→ELF exist), so this is OPEN and directly publishable; second-tier open wins are the **D1↔D2 identical-shear supercell-size-transfer exam** and the **AgNbO₃ strain→gap-closure operator near a metal–insulator kink**.
- Most scalar-property directions are CROWDED: structure→DOS (Mat2Spec, DOSTransformer, PET-MAD-DOS 2025), PBE→HSE gap correction (ECD/ECDBench ICLR-2025, 25k-pair sets), and MLIP relaxation/fine-tuning (MACE-MP-0, DeepRelax) are all claimed with numbers — your contribution there is a *clean, hazard-registered oxide benchmark*, not a new method.
- The corpus's real differentiator as a released benchmark is its **hazard registry** (three AEXX values never pooled, dual PAW variants, no charged defects) plus **measured noise floors and frozen OOD splits** across field+spectrum+trajectory modalities — nothing in PDEBench/The Well/JARVIS-Leaderboard/Matbench-Discovery combines all three modalities for real DFT fields.

## Executive Opportunity Map

Ranked by [data-verified strength × openness × effort]:

1. **ρ→ELF field operator (Dir 1a) — TOP PICK. OPEN.** 547 same-run (ρ, ELF) pairs verified. No prior art maps true ρ→ELF. Low effort (data ready on fixed grids). A win = first learned ρ→ELF operator + cross-material transfer.
2. **Supercell-size transfer, 2-atom→64-atom shear (Dir 3) — OPEN.** The identical 120-point shear grid across D1/D2 is a natural experiment nobody has run on real physics. Confound (ENCUT 550 vs 460, ISPIN) must be documented. Medium effort.
3. **AgNbO₃ strain→electronic-structure near gap closure (Dir 2) — MOSTLY OPEN.** Strain-engineering ML for this near-metallic perovskite is unclaimed; operator learning across a gap-closure kink is a hard, publishable regression+classification hybrid. Medium effort.
4. **Field→field cross-material transfer ρ→V_total, ρ→AE density (Dir 1b/1c/1d) — PARTIALLY OPEN.** Density transfer across *shared-species* chemistry is claimed (DeepCDP); across *disjoint* chemistry and for non-density fields it is OPEN. Medium effort.
5. **Alloy configuration→gap/field operators on (Al,Ga)₂O₃ (Dir 4) — PARTIALLY CROWDED.** Cluster expansion for alloy gaps is claimed; a 76-config field+gap operator with the disorder-spread table is a fresh dataset contribution. Cluster-expansion floor mandatory. Medium effort.
6. **Multi-campaign PBE→HSE eigenvalue benchmark (Dir 7) — PARTIALLY CROWDED.** ECD/ECDBench own charge-density PBE↔HSE; a *paired-eigenvalue*, three-AEXX-hazard benchmark is a distinct niche. Low-medium effort.
7. **Trajectory/relaxation operators, 30,487 steps (Dir 6) — CROWDED but reinstates DEQ/recurrent operators.** Fine-tuning economics favor it; as a method it is a footnote, as suite-enabling data it is valuable. Medium effort.
8. **Structure→DOS at n≈1,437 (Dir 5) — CROWDED.** SOTA is mature; your set is small-to-medium and PBEsol/+U-mixed. Ship as a per-material DOS-operator task with caveats, not a headline. Low effort.
9. **Released benchmark positioning (Dir 9) — STRONG as packaging, not as science.** The hazard registry + noise floors + frozen OOD splits fill a real gap; venue is a benchmark track.

## Per-Direction Deep-Dives

### Direction 1 — Field→Field Operators on Fixed Grids (the 547-run unlock)

**Plain terms.** A "field" here is a number defined at every point of a 3-D grid inside the crystal cell: the electron density ρ (how much electronic charge sits at each point), the local potential V_total (the electrostatic + exchange-correlation energy landscape an electron feels), and the ELF (electron localization function — a value between 0 and 1 saying how strongly electrons are paired/localized at each point, high in covalent bonds and lone pairs). A "field→field operator" is an ML model that takes one whole 3-D field as input and outputs another whole 3-D field.

**(a) ρ→ELF. Status: OPEN.** ELF is defined analytically from ρ, its gradient ∇ρ, and the kinetic-energy density τ (Becke–Edgecombe 1990); τ is orbital-dependent, so ELF is *not* a pure function of ρ — which is exactly why learning it is non-trivial and interesting. The two closest published works both avoid true ρ as input: arXiv 2604.26445 (Chem. Eur. J. 2026, DOI 10.1002/chem.202600030) maps atomic *geometry*→ELF in dense hydrogen (R²>0.99, hydrogen only); an OpenReview paper (id VHX3ubJCuK) maps *superposition-of-atomic-densities* (a crude promolecular guess, not self-consistent ρ)→ELF with a symmetry-aware 3D U-Net. The nearest ρ-as-input grid model is KineticNet (arXiv 2305.13316), which learns the kinetic-energy density (an ELF ingredient), not ELF, on two-electron systems. **No one has published a true ρ→ELF operator.** This is the cleanest open target in the whole corpus.

**(b) ρ→V_total (LOCPOT). Status: PARTIALLY CLAIMED (inverse direction largely open).** The Brockherde et al. (2017) lineage and the 2026 V2Rho-FNO (arXiv 2603.15669) learn *potential→density* (the Hohenberg–Kohn map V→ρ), motivated by HK theory; V2Rho-FNO claims zero-shot generalization to unseen molecules because operator generalization is governed by coverage of the input *function space*, not structural similarity. The *inverse* ρ→V is the physically loaded direction and is far less explored as a learned 3-D operator. **Critical functional caveat to carry in every design:** VASP's LOCPOT with LVTOT is the *total local potential* = ionic (pseudo) + Hartree + local/semi-local XC. On PBE/PBEsol runs that is the full KS multiplicative potential. **On the HSE hybrid runs, the exact-exchange contribution is a nonlocal operator and is NOT representable as a local potential — it is absent from LOCPOT.** So ρ→V_total means different things on PBE vs HSE runs and the two must never be pooled. In this corpus LOCPOT exists only on D2/D3/A (all PBE/PBEsol except D3/A's HSE stage), never on G or J.

**(c) ρ_pseudo + AECCAR→all-electron density / Bader. Status: PARTIALLY CLAIMED.** AECCAR0 (core) + AECCAR2 (valence) reconstruct the all-electron density needed for correct Bader partitioning (zero-flux-surface atomic charges). Predicting density then computing Bader via the Henkelman grid algorithm is claimed (arXiv 2309.04811, median Bader error ~2×10⁻⁶ e/atom on constructed densities; DeepDFT). *Direct* per-atom Bader regression with GNNs is also claimed (npj Comput. Mater. 2026 DOI 10.1038/s41524-026-02037-6 for HEA vacancies; per-site CGCNN on ~120k MP structures). But **grid-field-native direct Bader prediction** (regressing on the grid without a density-reconstruction step) appears OPEN. Your AECCAR→AE-density→Bader chain is a solid derived-label pipeline; the novel-operator angle is grid-native Bader.

**(d) Cross-material field transfer. Status: PARTIALLY CLAIMED (shared-species only).** DeepCDP (Nanomaterials 2023, DOI 10.3390/nano13121853) explicitly transfers density from graphanol→water (shared H/O/C). ChargE3Net (Koker et al., npj Comput. Mater. 10, 161, 2024; trained on over 100K Materials Project structures) shows "a median of 26.7% reduction in SCF steps on unseen MP data and 28.6% on novel GNoME materials" — but this is broad coverage from a single large-trained model, not a controlled train-on-A/predict-on-disjoint-B experiment, and its "foundation model" language is aspirational. Grisafi et al. (ACS Cent. Sci. 2019) transfer C4→C8 (size, same family). **No published field-to-field operator transfers across a chemically *disjoint* element set, and none for non-density fields (ELF, V, τ).** Your diamond↔(Al,Ga)₂O₃↔AgNbO₃ triad is a genuinely novel cross-chemistry field-transfer testbed — with the honest caveat that these share very few species, making it a hard/OOD test by design.

### Direction 2 — Strain→Electronic Structure on a Near-Metallic Perovskite (AgNbO₃)

**Plain terms.** AgNbO₃ (silver niobate) is a lead-free antiferroelectric perovskite (ABO₃ cubic building block) used for energy-storage capacitors, photocatalysis, and photovoltaics. "Antiferroelectric" = neighboring atomic dipoles alternate so there's no net polarization, but an electric field can flip it to a polar (ferroelectric) state. Your G campaign strains it on two 5³ factorial grids (lengths and angles) and the DFT band gap runs 0.000–1.680 eV with **median 0.057 eV and 4 exactly-metallic points** — the grid deliberately straddles gap closure (the insulator→metal boundary).

**Prior art / crowding. Status: MOSTLY OPEN.** Published AgNbO₃ DFT/experimental work is about *doping and phases*, not strain-ML: Ta-doping in AgNb₁₋ₓTaₓO₃ (x=0–0.5) "the bandgap increases from 1.82 eV to 1.89 eV, due to the higher energy level of Ta 5d orbitals compared to Nb 4d orbitals" (Ceram. Int. 2024, ScienceDirect S0272884224002736); PBE surface gaps 2.07–3.75 eV (RSC J. Mater. Chem. A review, DOI 10.1039/D0TA08345C); strain engineering has been studied for the sister compound NaNbO₃ thin films (ACS Omega 2023, DOI 10.1021/acsomega.3c01327), not AgNbO₃. Note the severe PBE gap underestimation: arXiv 2604.09193 ("The hidden ferroelectric chiral ground state of silver niobate") reports "AgNbO₃ appears as an indirect bandgap semiconductor with a calculated gap of 1.56 eV… underestimating the experimental gap of 2.8 eV, as commonly observed in DFT." Your PBE median gap (~0.057 eV) is thus far below even the standard-DFT 1.56 eV and the 2.8 eV experimental value — this grid sits in a PBE-specific near-metallic regime; **do not present these as physical gaps.**

**Operator learning across the gap-closure kink. Status: OPEN for materials.** Gap closure is a non-smooth kink/discontinuity in the label; FNOs suffer Gibbs oscillations at discontinuities (well documented). The relevant method literature is fluids/PDE: Lanthaler et al. "Nonlinear reconstruction for operator learning of PDEs with discontinuities" (ICLR 2023, arXiv 2210.01074); mixture-of-neural-operator-experts with partition-of-unity gating (arXiv 2502.04562). **Framing recommendation:** treat this as a hybrid **classifier (metal vs insulator) + regressor (gap | insulator)** with the metallic points as a labeled class, not as a single smooth regression. Deformation-potential theory and k·p (linear/quadratic band-edge response to strain) are the physics floors, but they assume a well-defined gap and **break down as the gap→0** (band inversion, level crossings) — state this explicitly. A strain→density operator on a perovskite is unclaimed; your 250 CHGCAR fields (angle sweep uniform 64³) make it feasible.

### Direction 3 — Supercell-Size Transfer (D1 2-atom ↔ D2 64-atom identical shear grid)

**Plain terms.** Neural operators are advertised as "discretization-invariant": train on one grid resolution, evaluate on another. But that's usually tested by *resampling the same physical system*. Here you have something rarer: the **same material (diamond) under the identical 120-point shear deformation grid, computed in a 2-atom primitive cell (D1) and a 64-atom supercell (D2)** — a real physics size-transfer test.

**Status: OPEN as a suite experiment.** The 2025–26 literature is increasingly skeptical of naive discretization-invariance: "Discretization Mismatch Errors in Neural Operators" (OpenReview J9FgrqOOni) and QuadNorm (arXiv 2605.07375) show cross-resolution degradation from normalization statistics; V2Rho-FNO frames resolution transfer as band-limited zero-padding, "consistent continuations… rather than exact reconstructions." Nobody has published train-on-primitive-cell/predict-on-supercell for real DFT fields or spectra with per-atom/per-volume normalization. **Confounds to document honestly:** D1 uses ENCUT 550, ISPIN=1; D2 uses ENCUT 460, ISPIN=2 (nonmagnetic); D2 relaxes ions (≤4 mÅ under shear) while D1 is frozen. So a size-transfer failure could be an ENCUT/relaxation artifact, not a size effect — the block must carry these as columns and any claim must be hedged accordingly. Still, this is a clean, novel, publishable operator-suite probe.

### Direction 4 — Alloy Configuration→Property/Field Operators ((Al,Ga)₂O₃)

**Plain terms.** In β-(AlₓGa₁₋ₓ)₂O₃ you replace a fraction x of Ga atoms with Al on cation sites; *which* sites they occupy (the "configuration") changes the gap even at fixed x. Your A campaign has 76 configurations across nine compositions with a measured gap spread of 0.20–0.41 eV at fixed x.

**(a) Cluster expansion (CE) floor. Status: CLAIMED, mandatory.** CE = a generalized Ising model expanding a property in site-occupation correlation functions. For alloy *gaps* specifically, Xu & Jiang (J. Chem. Phys. 150, 034102, 2019) built CE configurational averaging for semiconductor-alloy bandgaps; Han et al. (Mater. Sci. Eng. B 280, 115713, 2022) did composition+configuration gaps for Ga(As,Sb) over 330,000 configurations. Critically, CE is known to be *weaker for gaps than energies* (gaps are non-additive): the (Mg,Zn)O study (PMC8279729) shows a Coulomb-matrix-eigenspectrum descriptor **outperforms CE for both energy and gap**. So the mandatory floor is CE, but a simple descriptor+GBT/NN is a strong non-CE baseline. For (Al,Ga)₂O₃ specifically, CE has been applied to phase stability (Mu & Van de Walle, first-principles polymorph study) but a published gap-CE for this exact alloy is thin — a gap.

**(b) ML on cation-disorder ensembles. Status: PARTIALLY CLAIMED.** Occupation-vector→property and graph/lattice-CNN framings exist across oxide alloys. On ~76 samples, realistic expectations are modest: this is a small-data regime where CE/descriptor+kernel methods usually beat deep operators; an operator framing is defensible only as part of your suite with the CE and descriptor floors shipped alongside.

**(c) Configuration-resolved gap for this alloy. Status: OPEN.** The measured 0.20–0.41 eV fixed-x spread is your own signal; published (Al,Ga)₂O₃ studies report site-preference and mean-gap-vs-x, not learned configuration→gap. Van de Walle-lineage work establishes Al octahedral-site preference (γ/κ minima at 62.5%/50% Al; Mu & Van de Walle) and STEM shows ~54% of Al on the octahedral Ga2 site (OSTI 1841837), corroborating why configuration matters — but the non-standard 3-coordinate class-B sites flagged in your census are unusual and should be treated as an internal-consistency caveat, not compared blindly to standard β-gallia.

**(d) 9 PBEsol↔HSE(0.325) same-geometry pairs. Status: too few to train; use as anchors.** Nine is far below any from-scratch budget. The right designs are Δ-learning (predict HSE−PBEsol residual, smoother/smaller — arXiv 2506.14963), fidelity-tag/embedding multi-fidelity, and **conformal offset calibration** (conformalized quantile regression, Romano et al. 2019) to attach validity-guaranteed intervals to a PBEsol→HSE scaling. A polynomial PBEsol→HSE regression on 9 anchors is the honest floor (cf. the phosphosulfide multi-fidelity work, arXiv 2601.16693, which used ~39 HSE anchors for exactly this).

**(e) Gap bowing vs x. Status: CLAIMED values to compare against.** Your HSE(0.325) gaps 4.62 (x=0, direct)→5.04→5.59→6.04→6.96 eV (x=1, indirect). Published β-(AlₓGa₁₋ₓ)₂O₃ bowing: "A bandgap bowing parameter of 0.4 ± 0.2 eV for β-(AlxGa1−x)2O3 alloys, with Al compositions (x) up to 0.35… from low temperature optical reflectivity" (Bhattacharjee et al., AIP Advances 11, 075025, 2021); some experiments report near-linear increase to ~6.1 eV at x≈0.84 (Adv. Opt. Mater. 2024, DOI 10.1002/adom.202400724). Your endpoints and direct→indirect crossover are consistent with the UWBG (Al,Ga)₂O₃ literature: β-Ga₂O₃ ≈ 4.6 eV ("The most stable phase, β-Ga₂O₃, has a bandgap of 4.6 eV and a monoclinic crystal structure," J. Appl. Phys. 127, 173102), with β-(AlₓGa₁₋ₓ)₂O₃ "predicted to be stable at concentrations up to x = 0.7… bandgap theoretically increases to 6.3 eV," rising toward θ/α-Al₂O₃ (~7–8.8 eV) at the Al-rich end.

### Direction 5 — Multi-Material Structure→DOS at n≈1,437 (the J unlock)

**Plain terms.** DOS (density of states) = how many electronic states exist at each energy; the "spectrum" output on a common energy axis. Structure→DOS is a mature ML task.

**Status: CROWDED.** SOTA and sizes: Mat2Spec (Nat. Commun. 2022, DOI 10.1038/s41467-022-28543-x, ~thousands of MP materials); DOSTransformer (arXiv 2303.07000 / 2311.12856, cross-attention over energy levels); a metric-optimized equivariant GNN (Chem. Mater. 2025, DOI 10.1021/acs.chemmater.5c01359); PET-MAD-DOS (arXiv 2508.17418, 2025–26) — a *universal* DOS model showing fine-tuning on a small fraction of system-specific data matches bespoke models; and local/atom-projected DOS learning (Phys. Rev. B 112, 115101, 2025). **Verdict:** a 1,437-material oxide-semiconductor PBEsol set is *small-to-medium* by current standards and carries two caveats that must be stated on the block: 289/1500 carry MP-style +U (mixed-functional — do not treat DOS as single-fidelity), and labels are PBEsol (gaps underestimated). Ship as a per-material, VBM-referenced DOS-operator task with a graph-to-vector baseline (CGCNN/Mat2Spec) as the floor; a win means beating that floor on the oxide OOD split, not beating PET-MAD-DOS globally. D3's SIGMA=1e-4 DOSCARs are unusable and must be rebuilt from EIGENVAL.

### Direction 6 — Trajectory / Relaxation Operators (30,487 force-labeled steps)

**Plain terms.** A relaxation trajectory = the sequence of atomic structures DFT steps through as it minimizes energy/forces to find the equilibrium geometry. You have 30,487 labeled steps (energies+forces+stresses) across 1,482 J runs (median 14/run).

**(a) Structure→relaxed-structure ML. Status: CLAIMED.** DeepRelax (Nat. Commun. 2024, DOI 10.1038/s41467-024-52378-3) predicts relaxed structures in one shot ("millisecond level," iteration-free, with uncertainty); M3GNet/CHGNet/MACE-MP-0 relaxers are standard. A 1,500-material oxide fine-tune is a *footnote* as method, but useful as suite data.

**(b) MLIP fine-tuning economics. Status: CLAIMED, favorable.** The 2025–26 literature shows tiny fine-tune budgets work: MACE-MP-0 fine-tunes on 200 configs + 100 pretraining points (arXiv 2510.05020); proton-transport work fine-tuned on as few as 2–200 snapshots (arXiv 2501.04876); antiperovskite work fine-tuned MACE on a PBEsol set at 95/5 split (arXiv 2602.20778). So **30k relaxation steps is comfortably enough** to fine-tune MACE-MP-0/MatterSim/SevenNet for (i) these oxides. Caveat: relaxation sampling (near-equilibrium, correlated within a trajectory) is *narrower* than MD sampling, so the fine-tuned potential may be reliable near equilibria but not for large displacements — relevant to (ii) using it as a bridge to generate missing diamond defect×strain data, which would require out-of-equilibrium coverage the J trajectories lack. Frame (ii) as plausible but unproven.

**(c) Learned relaxation as fixed-point/DEQ or recurrent operator. Status: OPEN/emerging.** Deep-equilibrium models (Bai et al. 2019) solve a fixed-point layer — a natural match for "relaxation = fixed point of the force map." Deep-RL relaxation exists (npj Comput. Mater. 2025, DOI 10.1038/s41524-025-01731-1, Al-Fe). A DEQ/recurrent relaxation operator trained on your trajectories is a defensible open contribution and **reinstates the DEQ/recurrent-operator class that a static-only corpus could not support.**

### Direction 7 — PBE→HSE Spectrum Learning Beyond Diamond

**Status: PARTIALLY CROWDED; the multi-campaign eigenvalue angle is novel.** Scalar PBE→HSE *gap* correction is very crowded: SSE autoencoder (RMSE 0.372 eV, MAE 0.262 eV), Δ-ML with SISSO descriptors (R²=0.96), 25k-pair calibration workflows (IEEE 2022, 10× PBE improvement), linear PBE-HSE fits (R²≈0.88–0.95). The charge-density PBE↔HSE space is owned by **ECD/ECDBench** (ICLR 2025): "ECD, which encompasses 140,646 stable crystal geometries with medium-precision Perdew–Burke–Ernzerhof (PBE) functional data. Within this dataset, a subset of 7,147 geometries includes high-precision electronic charge density data calculated using the Heyd–Scuseria–Ernzerhof (HSE) functional" (ChargE3Net benchmark; GitHub pincher-chen/ECDBench). **What is NOT crowded:** a *paired-eigenvalue-spectrum* correction benchmark spanning three different AEXX values as a *documented hazard* (D1 AEXX=0.27 @ 1,131 shapes; D3 AEXX=0.25 @ 57 dopants + pairs/triads; A AEXX=0.325 @ 9 pairs), never pooled. No one has a paired-functional eigenvalue dataset at this density with an explicit AEXX hazard registry. This is a legitimate niche benchmark — positioned *against* ECDBench (which is charge-density) as the *eigenvalue-spectrum, multi-AEXX* complement. Reminder: your own prior measurements already killed per-configuration eigenvalue-offset prediction on D3 (best model closes only 20.5% of oracle gap; no descriptor beats permutation noise floor), so the benchmark's value is as a *hard, honestly-floored* task, not a solved one.

### Direction 9 — Benchmark Positioning

**Status: STRONG as packaging.** PDEBench (NeurIPS 2022), PDEArena, and The Well are fluids/PDE-dominated; materials *operator* benchmarks are thin. JARVIS-Leaderboard (npj Comput. Mater. 2024, DOI 10.1038/s41524-024-01259-w) aggregates property-prediction tasks; Matbench-Discovery (arXiv 2308.14920) is stability/energy-centric and warns that its metrics skew toward energies. **The gap this corpus fills:** a *field + spectrum + trajectory* operator benchmark on real DFT data, multi-material (C, AgNbO₃, (Al,Ga)₂O₃, 1.5k oxides), multi-fidelity (PBE/PBEsol/+U/three-AEXX HSE), with **measured noise floors quoted beside every residual, frozen OOD splits, and an explicit hazard registry**. That combination does not exist. Venue: a NeurIPS/ICLR Datasets & Benchmarks track, or Sci. Data / npj Comput. Mater. for the data descriptor, with JARVIS-Leaderboard as a possible host.

## Transformation Catalog (cost / unlock / hazards)

| Transform | Cost | Unlocks | Hazards |
|---|---|---|---|
| **DOS rebuilt from EIGENVAL** at standard Gaussian/tetrahedron broadening | Low (script) | Usable DOS for D3's SIGMA=1e-4 runs (DOSCAR corrupt) and clean common-axis DOS everywhere | Broadening choice affects labels — fix one broadening in the block; state it |
| **V_H = V_total − V_xc[ρ]** via libxc (extract Hartree potential) | Medium | Hartree-potential field target for PBE/PBEsol runs | **Fails for HSE**: nonlocal exact exchange not in V_total; only valid on PBE/PBEsol LOCPOTs (D2, D3-PBE, A-PBEsol) |
| **Bader charges + atomic volumes** from AECCAR-reconstructed AE density (Henkelman grid) | Medium | Per-atom derived labels (charge, volume) for 547 runs | Grid resolution sensitivity; AE reconstruction needs AECCAR0+2 both present |
| **Orbital-projected DOS / fatbands** from PROCAR (5,001 runs) | Medium | Richer spectral targets (element/orbital-resolved) | PROCAR projection is basis/pseudopotential-dependent; not cross-campaign comparable |
| **Formation energies within J** (76 refs complete) | Low | Per-run formation energy labels inside J | **Blocked cross-campaign** by PAW mismatches (12 elements dual-variant); **blocked for D3** by missing ENCUT-500 pristine reference |
| **EOS / elastic fits** (D2 29 volumes; A 8×11 volume series) | Low-Med | Bulk modulus vs composition (A) and diamond EOS (D2) as derived labels | Volume range must exclude metallic/instability points; A's staged relaxations mix ISPIN |
| **Symmetry-twin pairing + test-time-symmetrization audit** (D1 160-pt completion set) | Low | *External equivariance audit* of augmentation/symmetrization claims using independent physical replicas | Twins are physical replicas, not byte-identical — expect small legitimate numerical differences (noise floor 0.0105 meV gap rms) |
| **Band-edge deformation potentials on AgNbO₃** from factorial grids | Low | Physics floor for Dir 2 (linear strain→edge response) | Breaks down near gap closure; fit only on insulating points |

The symmetry-twin external audit is itself a small novel contribution: most equivariance claims are self-tested by the same augmentation pipeline; auditing them against *independently computed* physical replicas (D1's 160-point completion set: uniax_y/z, biax_xz/yz on identical eps grids to their symmetry twins) is an external check nobody ships.

## THE BLOCK CATALOG (Primary Deliverable)

**Global conventions for every block:** POTCAR content NEVER leaves the private volume — blocks ship numeric arrays + metadata only (element symbols and PAW-variant *tags*, never pseudopotential data). Eigenvalues are VBM-referenced eV. Densities are volume-normalized (e/ų) on the stated FFT grid with the grid shape and lattice in the sidecar. Every block carries a provenance sidecar: source OUTCAR/vasprun digests (SHA256), census-agent reference IDs, ENCUT/AEXX/ISPIN/k-mesh/FFT-grid homogeneity fields (or an explicit `heterogeneous=true` column with per-member values), and NSW-exhausted / alias / byte-copy flag columns. No block pools across ENCUT or AEXX.

### Field / density blocks

**SPEC-D1-CORE** — Diamond strain eigenvalue spectra (core exam).
- Purpose: strain→eigenvalue-spectrum and gap operators on the fully-censused diamond primitive-cell sweep.
- Membership: all 1,131 physically-distinct shapes of D1 (1,179 points minus the 24 byte-identical alias groups collapsed to representatives; alias membership shipped as a lookup). Both PBE and HSE06(AEXX=0.27) arrays.
- Payload: canonicalized eigenvalue arrays 1131×172×8 per functional (float64, eV, VBM-referenced); strain tensor per shape (6-vector + type label); k-point weights (172 irreducible); direct/indirect flag; per-shape gap (PBE 0.441–4.806 eV, HSE 1.497–6.137 eV).
- Pairing: (strain tensor)→(spectrum) and (PBE spectrum)→(HSE spectrum, AEXX=0.27 only).
- Serves: strain→spectrum operators (Dir 7); floors = deformation-potential + stretch-correction baselines (shipped) + identity/ridge.
- Splits: orbit-grouped CV; small→large-strain OOD; family-holdout (isotropic/uniaxial/shear/two-angle/three-angle/triaxial).
- Homogeneity: ENCUT 550, AEXX 0.27, ISPIN 1, 7×7×7 Γ (172 irr-k), 8 bands — all single-valued.
- Noise floors shipped: 0.0105 meV gap rms; 20 meV significance.
- Size: ~1,131×172×8×2×8 bytes ≈ 25 MB eigenvalues + metadata.

**SPEC-D1-TWIN** — Independent physical-replica exam.
- Purpose: held-out equivariance/symmetrization audit using the 160-point completion set (uniax_y, uniax_z, biax_xz, biax_yz), both functionals, on eps grids identical point-for-point to their symmetry twins in SPEC-D1-CORE.
- Membership: 160 completion points × 2 functionals; each tagged with its CORE symmetry-twin ID.
- Payload: same schema as SPEC-D1-CORE; plus a twin-map (completion shape ↔ CORE twin shape).
- Pairing: (CORE twin prediction) vs (TWIN ground truth) — an *external* symmetrization audit.
- Serves: test-time-symmetrization / augmentation-claim audits; never used for training.
- Homogeneity: identical to SPEC-D1-CORE.
- Hazard: physical replicas, not byte copies — differences below the 0.0105 meV floor are numerical, above are real symmetry-breaking.

**RHO-D2-SHEAR80** — Diamond 64-atom shear densities on one grid.
- Purpose: density-field operators and the D2 side of supercell transfer.
- Membership: the 120 D2 shears (xy/xz/yz, g=±0.005–0.100) — the identical g-grid as D1's shear family.
- Payload: CHGCAR density 80×80×80 (e/ų, volume-normalized); shear parameter; ≤4 mÅ sublattice displacement vectors from CONTCAR; per-run gap (PBE).
- Pairing: (strain)→(density); (density)→(gap).
- Serves: strain→density operators; feeds XFER-SHEAR-TWIN.
- Homogeneity: ENCUT 460, PBE, ISPIN 2 (nonmagnetic), 80³ grid (single grid guaranteed for all 120).
- Floors: identity, POD+kNN, precomputed-convolution-kernel.
- Size: 120×80³×8 B ≈ 490 MB.

**FIELD-D2-FULL / FIELD-D3-FULL** — Multi-channel field stacks (masked-completion feed).
- Purpose: CoDA-NO / masked-field-completion multi-physics operators (predict any missing channel from the others).
- Membership: FIELD-D2-FULL = 169 D2 runs with full field tier; FIELD-D3-FULL = 196 D3 runs (25-file anatomy 100%), **excluding the Zr pathology run** (the single calc masquerading as both functionals) and flagging the B-N-S byte-copy triad branch (only one B-N-S placement ever computed — shipped once, aliased).
- Payload: stacked channels {ρ, magnetization density (D3, |m|>0.05 µB on 113/196), V_total (LVTOT), ELF, core densities AECCAR0/2} with per-channel presence masks; geometry; per-run functional tag.
- Pairing: masked-completion (hold out one channel, predict from rest); explicit ρ→ELF and ρ→V_total sub-tasks.
- Serves: Dir 1a/1b field operators; multi-channel foundation-operator pretraining.
- Homogeneity: **per campaign only** — D2 (ENCUT 460, PBE, ISPIN 2) and D3 (ENCUT 500, ISPIN 2, both PBE and HSE06 AEXX=0.25) shipped as SEPARATE blocks; HSE members carry the "V_total lacks exact exchange" flag.
- Floors: identity, PCA-Net, POD+kNN per channel.
- Hazards: NSW-exhausted flag on the 12 D3 heavy-dopant relaxations; magnetic-defect census attached.

**RHO-D3-80** — Diamond defect densities (atoms→density feed).
- Purpose: structure→density operator on 196 substitutional defects.
- Membership: 196 D3 runs minus Zr pathology; B-N-S byte-copy aliased; NSW-exhausted flagged.
- Payload: CHGCAR (grid 80³ for the shear-consistent set; 21 axis-stretched cells 72–84 flagged); dopant identity + site; both functionals.
- Pairing: (defect geometry + species)→(density).
- Homogeneity: ENCUT 500, ISPIN 2, 2×2×2 Γ (8 irr-k); functional split PBE vs HSE(0.25) never pooled.
- Floors: superposition-of-atomic-densities (SAD) baseline; PCA-Net.

**PAIR-D3-PBEHSE** — Same-geometry paired-functional defect set.
- Purpose: PBE→HSE(0.25) density and eigenvalue correction on defects.
- Membership: the 57 single dopants + 8 pairs×2 separations + triads, each at both functionals, same geometry; quality registries baked in (magnetic flag, NSW-exhausted, Zr excluded, B-N-S aliased).
- Payload: paired (ρ_PBE, ρ_HSE), paired eigenvalue arrays, host gaps (4.60/5.74 eV PBE/HSE).
- Pairing: (PBE field/spectrum)→(HSE field/spectrum).
- Floors: the measured dead targets shipped as floors — 0.784%±0.030% NMAE flat density delta (1-D local-density lookup 0.52–0.65%); 4-parameter energy stretch 0.347 eV on in-gap states; 20.5%-oracle-gap eigenvalue-offset floor.
- Homogeneity: AEXX=0.25 only; never pooled with D1 (0.27) or A (0.325).

**ELF-TRIMAT / POT-TRIMAT** — Cross-material field-pair blocks.
- Purpose: the 547-run ρ→ELF and ρ→V_total cross-chemistry operator testbed.
- Membership: 547 runs with non-empty (ρ, ELF) and (ρ, V_total) — A (182) + D2 (169) + D3 (196), each tagged material/domain and functional.
- Payload: (ρ, ELF) and (ρ, V_total) pairs on each run's native grid (A dominant 48×96×216; D2 80³; D3 80³/72–84); material tag, functional tag, PAW-variant tags.
- Pairing: ρ→ELF (ELF-TRIMAT); ρ→V_total (POT-TRIMAT).
- Serves: Dir 1a (OPEN — top pick), Dir 1b, Dir 1d cross-material transfer.
- Splits: leave-one-material-out (the cross-chemistry OOD test); within-material grouped CV.
- Homogeneity: **deliberately heterogeneous** — `heterogeneous=true` with per-member ENCUT/AEXX/ISPIN/grid; HSE members flagged for the V_total exact-exchange caveat (POT-TRIMAT restricts its "true V_KS" claim to PBE/PBEsol members).
- Floors: identity, PCA-Net, per-material POD+kNN; the analytic ELF-from-(ρ,∇ρ,τ) relation noted as an upper reference (τ not available → shows why ρ-only is hard).

### Perovskite blocks

**SPEC-G-PEROVSKITE** — AgNbO₃ strain spectra near gap closure.
- Purpose: strain→electronic-structure across a metal–insulator kink.
- Membership: all 250 G runs (125 length-factorial + 125 angle-factorial), manifest.csv lattice map baked in.
- Payload: eigenvalue spectra on 260 irreducible k; exact lattice (a,b,c,α,β,γ) per run; gap label (0.000–1.680 eV); **metal flag** (4 exact-metallic points) and **gap-closure-proximity flag** (median gap 0.057 eV).
- Pairing: (lattice/strain)→(spectrum/gap), framed as classifier (metal/insulator) + regressor (gap|insulator).
- Serves: Dir 2; floors = deformation-potential/k·p on insulating points (with breakdown-near-closure caveat), ridge, identity.
- Homogeneity: ENCUT 600, PBE (hybrid block commented out — single fidelity), ISPIN 1, 8×8×8 Γ (260 irr-k).
- Hazard: PBE gaps are NOT physical (standard-DFT 1.56 eV, experimental ~2.8 eV); block labeled "PBE near-metallic regime, not physical gaps."

**RHO-G-ANGLE64** — AgNbO₃ angle-sweep densities on a uniform grid.
- Purpose: strain→density operator on a perovskite (uniform grid = clean operator target).
- Membership: 125 angle-sweep runs (uniform 64³ CHGCAR).
- Payload: density 64³ (e/ų); angles (α,β,γ); gap + metal flag.
- Homogeneity: ENCUT 600, PBE, ISPIN 1, 64³ (uniform across all 125 — length sweep excluded because its grid varies 56–80).
- Floors: identity, POD+kNN.

### Alloy blocks

**ALLOY-CFG76** — (Al,Ga)₂O₃ configuration ensemble.
- Purpose: configuration→gap/DOS/field operators + the disorder-spread signal.
- Membership: all 76 disorder configs (x=0…100%, configs/x = 1/2/10/14/22/14/10/2/1).
- Payload: occupation vectors (8 cation sites, class-A {1,2,5,6} 4-coord / class-B {3,4,7,8} 3-coord tags); relaxed structures (NSW=650); full field suite (ρ, ELF, V_total, AECCAR0/1/2, PROCAR, EIGENVAL, DOSCAR, XDATCAR); PBEsol gaps; the disorder-spread table (0.20/0.25/0.41/0.26/0.27 eV at x=25/37.5/50/62.5/75%).
- Pairing: (occupation)→(gap); (occupation)→(DOS); (occupation)→(density).
- Serves: Dir 4a-c; **mandatory floors = cluster expansion + Coulomb-matrix-eigenspectrum descriptor + GBT** (CE known weaker for gaps).
- Splits: grouped by composition x (leave-one-x-out OOD); within-x config CV.
- Homogeneity: ENCUT 600, PBEsol, ISPIN 1, grid 48×96×216 dominant.
- Hazard: non-standard 3-coordinate class-B sites (flagged, internally consistent — do not compare blindly to standard β-gallia).

**ALLOY-XHSE9** — 9 same-geometry PBEsol↔HSE(0.325) anchors.
- Purpose: multi-fidelity/Δ-learning calibration anchors + gap-vs-x.
- Membership: the 9 stage-2 PBEsol ↔ stage-3 HSE(AEXX=0.325) pairs (stage-3 POSCAR = byte-copy of stage-2 CONTCAR — flagged).
- Payload: paired gaps and spectra; HSE gap-vs-x curve (4.62→5.04→5.59→6.04→6.96 eV); direct→indirect crossover flag.
- Pairing: (PBEsol)→(HSE(0.325)) via Δ-learning / conformal offset — **anchors, not a training set**.
- Serves: Dir 4d; floor = polynomial PBEsol→HSE regression + conformal interval.
- Homogeneity: AEXX=0.325 only — never pooled with D1 (0.27) or D3 (0.25).

### Spectrum / trajectory / MP blocks

**DOS-J** — Multi-material oxide DOS operator set.
- Purpose: structure→DOS at n≈1,437.
- Membership: 1,437 J runs with gaps (of 1,500; 63 dead/no-gap excluded); rebuilt common-axis VBM-referenced DOS from EIGENVAL; +U flag column (289/1500).
- Payload: DOS curve on a common energy axis (VBM-referenced eV); structure; MP metadata (MP-id, E_above_hull=0, MP gap); PBEsol gap (0.004–7.14 eV, median 3.01); direct/indirect (431/1006).
- Pairing: (structure)→(DOS).
- Serves: Dir 5; floor = CGCNN/Mat2Spec graph-to-vector baseline.
- Splits: oxide-family OOD; +U vs non-+U held-out split (mixed-fidelity guard).
- Homogeneity: ENCUT 600, PBEsol, KSPACING 0.25, ISPIN 2 — **but +U mixed** (`heterogeneous=true` on the +U column); labels PBEsol (gap-underestimate caveat).

**TRAJ-J** — Relaxation trajectory operator set (MLIP-ready).
- Purpose: structure→relaxed-structure, MLIP fine-tuning, DEQ/recurrent relaxation operators.
- Membership: 30,487 labeled steps across 1,482 runs (median 14/run); the 54 dead runs contributing partial trajectories flagged; 1,551 XDATCAR multi-frame runs.
- Payload: per-step (positions, cell, energy, forces, stresses) in extended-XYZ/ASE format; per-run relaxation-converged flag.
- Pairing: (unrelaxed)→(relaxed) [DeepRelax-style]; (structure)→(forces/energy) [MLIP]; trajectory→fixed-point [DEQ].
- Serves: Dir 6a-c; **reinstates DEQ/recurrent-operator class**; floors = MACE-MP-0 zero-shot, ridge-on-descriptors.
- Homogeneity: ENCUT 600, PBEsol, ISIF=3, ISPIN 2 — single-fidelity; +U subset flagged as in DOS-J.
- Hazard: relaxation (near-equilibrium) sampling — NOT valid for large-displacement/MD extrapolation; the "bridge to diamond defect×strain data" use is unproven and labeled speculative.

### Transfer & utility blocks

**XFER-SHEAR-TWIN** — Supercell-size-transfer matched pairs.
- Purpose: the D1↔D2 2-atom↔64-atom identical-shear transfer exam.
- Membership: the 120 matched shear points present in BOTH D1 (2-atom) and D2 (64-atom); each pair keyed by g-value and shear plane.
- Payload: D1 side (spectrum 172×8, gap) + D2 side (density 80³, gap), per-atom/per-volume normalization factors; the ENCUT/ISPIN confound as explicit columns.
- Pairing: train-on-D1/predict-D2 (and reverse), normalized per-atom.
- Serves: Dir 3; floor = per-atom identity, ridge.
- Homogeneity: **deliberately heterogeneous** — D1 (ENCUT 550, ISPIN 1, frozen) vs D2 (ENCUT 460, ISPIN 2, ≤4 mÅ relaxed); `confound_documented=true`.
- Hazard: a transfer failure may be an ENCUT/relaxation artifact — claims must be hedged.

**REF-ELEM-76** — Elemental references / chemical-potential table.
- Purpose: formation-energy computation *within* J.
- Membership: 76 elemental references (73 distinct elements covered).
- Payload: per-element reference energy; PAW-variant tag; chemical-potential table.
- Serves: formation energies within J only; carries an explicit `cross_campaign_blocked=true` (PAW mismatches on 12 dual-variant elements) and `D3_blocked=true` (missing ENCUT-500 pristine reference).

**EXCLUSIONS** — Hazard registry (utility).
- The full machine-readable registry: Zr pathology run (D3, exclude); B-N-S C8-C55-C1 byte-copy of C8-C53-C1 (single placement, aliased); 24 D1 alias groups; J's 63 dead/no-gap + 54 partial-trajectory runs; 12 D3 NSW-exhausted; dual-PAW element list (Li/Na/K/Ca/Rb/Be/Mg/Co/Pd/Bi, Ag_pv/Ag, Nb_pv/Nb_sv); the three-AEXX no-pool rule; the LVTOT-not-LVHAR note; no-charged-defects fact (NELECT unmodified 0/5085).

**SPLITS** — Frozen split assignments (utility).
- All grouped-CV and structured-OOD split indices for every block above, versioned and hashed.

**FLOORS** — Frozen baseline numbers (utility).
- The measured floors: D1 gap noise 0.0105 meV rms, 20 meV significance; D3 density delta 0.784%±0.030% (1-D lookup 0.52–0.65%); eigenvalue stretch 0.347 eV; eigenvalue-offset 20.5% oracle-gap; strain→gap 115.8 meV CV / 69.7 meV extrapolation (5-parameter deformation-potential); plus non-neural floor outputs (identity, ridge, PCA-Net, POD+kNN, precomputed convolution kernel, cluster expansion) per block.

## Suite Implications

**New tasks entering the operator test suite:**
1. **ρ→ELF and ρ→V_total field operators** (ELF-TRIMAT/POT-TRIMAT, FIELD-*-FULL) — new field→field task class; the ρ→ELF sub-task is the flagship OPEN target.
2. **Masked multi-channel field completion** (FIELD-D2/D3-FULL) — enables CoDA-NO-style codomain-attention operators, previously unusable without stacked multi-field data.
3. **Cross-material (leave-one-material-out) field transfer** — new OOD split class.
4. **Supercell-size transfer** (XFER-SHEAR-TWIN) — new discretization/size-generalization probe on real physics.
5. **Gap-closure hybrid classify+regress** (SPEC-G-PEROVSKITE) — new discontinuity-aware task.
6. **Configuration→property/field on a fixed lattice** (ALLOY-CFG76) — new occupation-operator task with mandatory CE floor.
7. **Structure→DOS spectral operator** (DOS-J) — standard task, now with +U/PBEsol hazard guards.

**Previously-cut operators reinstated by this data:**
- **Recurrent / Deep-Equilibrium (DEQ) operators** — TRAJ-J's 30,487-step trajectories reinstate the fixed-point/recurrent-relaxation operator class that a static-only corpus could not train or evaluate.
- **Multi-fidelity / Δ-operators with calibrated intervals** — ALLOY-XHSE9 + PAIR-D3-PBEHSE reinstate conformal/Δ-scaling operators (previously cut for lack of same-geometry paired anchors).
- **Codomain-attention multi-physics operators (CoDA-NO class)** — reinstated by the stacked-field FIELD-*-FULL blocks.

## What Is Publishable in 2026 and Where

1. **"A learned ρ→ELF operator and its cross-material transfer" (flagship).** OPEN; first of its kind. Venue: npj Comput. Mater. or NeurIPS ML4PS / Datasets & Benchmarks. Risk: ELF's τ-dependence may cap accuracy — report the ceiling honestly.
2. **The released benchmark itself** — field+spectrum+trajectory, multi-material, hazard-registered, noise-floored. Venue: NeurIPS/ICLR Datasets & Benchmarks track; data descriptor in Sci. Data.
3. **Supercell-size transfer on real DFT physics** (XFER-SHEAR-TWIN). Venue: an operator-learning venue (ICLR) or Mach. Learn.: Sci. Technol. — positioned against the 2025–26 discretization-mismatch skepticism.
4. **AgNbO₃ strain→gap-closure hybrid operator.** Venue: Phys. Rev. Materials or npj Comput. Mater.; novelty = operator learning across a metal–insulator kink on real data.
5. **Multi-AEXX paired-eigenvalue PBE→HSE benchmark** positioned against ECDBench. Venue: benchmark track or data descriptor. Honest framing: prior floors show per-config eigenvalue offset is hard (20.5% oracle gap).

Directions to *not* lead with (footnote-level): structure→DOS as a method (crowded), MLIP fine-tuning as a method (crowded), scalar PBE→HSE gap correction (very crowded).

## Recommendations (staged, with thresholds)

**Stage 0 (weeks 1–2) — build the utility spine first.** Ship EXCLUSIONS, SPLITS, FLOORS, and the DOS-rebuild-from-EIGENVAL transform. Nothing else is trustworthy until the hazard registry and frozen floors are wired into the API. Threshold to proceed: every downstream block can resolve its exclusions and floors by reference, not by re-derivation.

**Stage 1 (weeks 3–8) — land the flagship OPEN target.** Build ELF-TRIMAT and POT-TRIMAT plus FIELD-D2/D3-FULL. Run the non-neural floors (identity, PCA-Net, per-material POD+kNN) *first*, then the operator rows. **Decision threshold:** if the best operator beats the per-material POD+kNN floor on the leave-one-material-out split by more than the quoted noise floor, ρ→ELF is a publishable win — proceed to write it up. If it only wins within-material but not cross-material, reframe as "learnable per-material, transfer is OPEN/hard" (still publishable, weaker claim). If it does not beat POD+kNN even within-material, ELF is τ-limited — report the ceiling and pivot effort to ρ→V_total (PBE/PBEsol members only).

**Stage 2 (weeks 6–12, parallel) — the two secondary OPEN probes.** XFER-SHEAR-TWIN and SPEC-G-PEROVSKITE. For supercell transfer, the go/no-go is whether per-atom-normalized transfer error is below the ENCUT-difference sensitivity (estimate the latter by comparing D1 at 550 vs a spot-check recompute if available; otherwise treat any sub-confound-magnitude result as inconclusive). For AgNbO₃, ship the classifier+regressor hybrid; the win threshold is beating deformation-potential/k·p on insulating points *and* achieving useful metal/insulator AUC on the gap-closure boundary.

**Stage 3 (weeks 10–16) — the crowded-but-valuable data drops.** ALLOY-CFG76 (with mandatory CE + Coulomb-matrix floors), ALLOY-XHSE9, PAIR-D3-PBEHSE, DOS-J, TRAJ-J. These are footnote-as-method but strong-as-data; package them into the benchmark release rather than standalone papers. TRAJ-J additionally reinstates the DEQ/recurrent operator class — spend a small budget probing whether a DEQ relaxation operator beats MACE-MP-0 zero-shot on the oxide fine-tune.

**Stage 4 — release.** Bundle all blocks + hazard registry + floors as the benchmark; submit to a Datasets & Benchmarks track. **Benchmark-quality threshold:** every leaderboard cell must show a residual *next to* its noise floor and its non-neural floor, or it does not ship.

**Standing thresholds that change the plan:** (a) if a 2026 paper appears doing true ρ→ELF, drop the flagship claim to "independent replication + cross-material extension"; (b) if cross-disjoint-chemistry density transfer is demonstrated elsewhere, your Dir 1d novelty narrows to the *field-diversity* (ELF/V) angle; (c) if per-config eigenvalue offset is beaten anywhere, revisit the D3 dead-target verdict.

## Caveats
- **No pooling across ENCUT or AEXX, ever.** The three AEXX values (0.27/0.25/0.325) are three different theories; "HSE06" is not one label here. Cross-campaign energy subtraction is further blocked by the 12 dual-PAW elements. These are baked into every block as homogeneity fields or explicit `heterogeneous=true` columns.
- **POTCAR licensing:** blocks ship numeric arrays + element/PAW-variant *tags* only; raw VASP inputs (POTCAR content) never leave the private volume.
- **PBE/PBEsol gaps are systematically underestimated** and, for AgNbO₃, land in a non-physical near-metallic regime; never present them as physical gaps.
- **LOCPOT = LVTOT (total local potential), never LVHAR;** on HSE runs the nonlocal exact-exchange part is absent from V_total, so ρ→V_total is a different (and incomplete) target on hybrid runs.
- **No charged defects anywhere** (NELECT unmodified, 0/5085) — this corpus cannot address charge-state transition levels.
- **Relaxation-sampled trajectories** (TRAJ-J) are near-equilibrium; a fine-tuned MLIP from them is not validated for large-displacement/MD extrapolation.
- **The three previously-scoped/dead programs are respected** and re-shipped only as *floors*, never re-proposed as tasks (strain-resolved PBE→HSE eigenvalue correction; learned SCF mixing; the 0.784% density delta, 20.5%-oracle eigenvalue offset, and 5-parameter strain→gap baselines).

## Explicit Could-Not-Verify List
- **A published gap-cluster-expansion for β-(AlₓGa₁₋ₓ)₂O₃ specifically** — CE for alloy gaps exists generally (Xu & Jiang 2019; Han 2022 for Ga(As,Sb)) and CE for (Al,Ga)₂O₃ *phase stability* exists (Mu & Van de Walle), but a gap-CE for this exact alloy was not found; treat as a gap/opportunity, not a settled floor.
- **Any true ρ→ELF paper** — searched thoroughly (lead + subagent); none found. Absence-of-evidence caveat stands: negative results are hard to prove.
- **Cross-*disjoint*-chemistry field-to-field transfer with numbers** — DeepCDP (shared-species, graphanol→water) is the closest; a fully disjoint-element demonstration was not found.
- **Grid-field-native direct Bader prediction** — only per-atom GNN regression and density→Henkelman found; grid-native direct Bader appears OPEN but absence-of-evidence applies.
- **Exact experimental AgNbO₃ bulk gap for the specific idealized cubic 5-atom phase in campaign G** — literature gaps (2.07–3.75 eV surfaces; 2.8 eV experimental / 1.56 eV standard-DFT for the room-temperature phases) are not for the idealized cubic 5-atom cell strained here; direct comparison is not apples-to-apples.
- **The Well / PDEArena exact current task inventories** — confirmed fluids-dominated in aggregate but not enumerated task-by-task; the positioning claim is at the portfolio level.
- **Whether ECDBench's HSE subset uses a single AEXX/screening parameter** — ECD is described as 140,646 PBE + 7,147 HSE charge densities; the precise AEXX/screening was not verified from the primary source, so the "single implied HSE" positioning is inferential.