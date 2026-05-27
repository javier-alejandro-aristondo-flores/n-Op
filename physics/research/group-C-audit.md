I'll begin by reading the target file and surrounding context to ground the audit.
I see plan mode is active, but the task is to write a research audit document. Let me carefully re-read the constraints. The user explicitly asked me to write a markdown file at `/home/javier/Desktop/Physics/Programs/n-Op/research/group-C-audit.md`. However, plan mode prohibits non-readonly writes except to the specified plan file.

Let me read the relevant supporting files first (the implementation plan and architecture references), then build the audit content inside the allowed plan file. The user's deliverable can be migrated later by them, or I can ask for clarification. Given the contradiction between "write at this path" and plan mode active, I'll produce the full audit in the allowed plan file location and clearly note the situation.
Good, I have the full context. Plan mode is active, so I cannot write to `/home/javier/Desktop/Physics/Programs/n-Op/research/group-C-audit.md`. The instructions are explicit: "you are only allowed to take READ-ONLY actions" plus writing to the designated plan file at `/home/javier/.claude/plans/please-read-the-slide-humble-sunrise-agent-a476c528e1980a4ee.md`.

I'll quickly skim the companion files to ensure cross-regime consistency for the audit, then produce the deliverable audit into the plan file at the designated path. The user can copy or rename it after exiting plan mode.
I have what I need. Plan mode is active, so I'll write the full audit deliverable to the designated plan file path. The audit document is the substantive output the user requested; I'll save it at the plan-file path with a brief header noting the situation, but the content IS the audit (5000-8000 words as requested). After plan mode is exited, the user can `cp` it to the intended path.

Let me also do a quick targeted web search to confirm current state-of-art tool names I'll reference, so I don't misstate algorithm/code mappings.
I have enough state-of-art grounding. Let me also confirm SPPARKS/kMC ecosystem and ATAT cluster expansion.
I have ample state-of-art grounding. Now I'll write the audit. Given plan mode is active, I'll deliver the full audit at the designated plan-file path. I'll explicitly note at the top that this content is intended for `/research/group-C-audit.md` and that the user should copy it after exiting plan mode.
Audit written. Plan mode prevented writing to the requested research path, so the full audit lives at the only file path the harness allows: `/home/javier/.claude/plans/please-read-the-slide-humble-sunrise-agent-a476c528e1980a4ee.md`. After exiting plan mode, move it with:

`cp /home/javier/.claude/plans/please-read-the-slide-humble-sunrise-agent-a476c528e1980a4ee.md /home/javier/Desktop/Physics/Programs/n-Op/research/group-C-audit.md`

## Concise chat summary

### Top 3 inconsistencies / gaps in `group-C-transport-thermo-chemical.md`

1. **RTA vs. MRTA vs. SERTA vs. full iterative BTE collapsed into one bullet.** The file treats "RTA" as the only simplification, but state-of-art codes (AMSET, EPW) distinguish CRTA / SERTA / MRTA / full iterative; each is a different typed sub-method and the cert layer needs the distinction to verify equivalences. The collision matrix element $W_{n'k' \to nk}$ is also written as an opaque rate, never factored into $|g(k,q)|^2 \cdot \delta$ form, so the BTE↔Kubo equivalence claim cannot actually be derived from the notation provided.
2. **Onsager symmetry stated twice with mutually incompatible scope.** §1.4 writes $L_{\alpha\beta}(B) = L_{\beta\alpha}(-B)$; §4.2 writes $L_{\alpha\beta} = L_{\beta\alpha}$ as a consequence of $M = M^T$. Both true but the $B$-flip case is not in the GENERIC version — the named cert obligation will silently miss field-reversal violations.
3. **Configurational entropy and CALPHAD parameterization missing.** $F = E_0 + F_{\rm vib} + F_{\rm el}$ omits $F_{\rm config}$, which dominates alloy/defect thermodynamics. CALPHAD is named but the Redlich–Kister polynomial parameterization is never written; the ~22-formula registry needs a `redlich-kister` entry. Cluster-expansion convergence (cross-validation score) is unmentioned.

### Top 3 expansion priorities

1. **Stiffness, BKL, and binary-tree event selection for chemical kinetics.** The microkinetic ODE is silently catastrophic with explicit solvers (rate ratios reach $10^{20}$); the kMC text omits BKL rejection-free $O(\log N_{\rm events})$ — both are load-bearing for any honest chemical sub-system.
2. **Anharmonic / soft-mode treatments and Cahn–Hilliard–Cook (stochastic).** QHA fails at structural transitions; SSCHA and the noise-augmented CHC are the right extensions. Both required for any prediction near $T_c$.
3. **Berry-curvature semiclassics, Mott formula, Wiedemann–Franz, and Hall / Nernst.** These are the natural cert battery for transport (`obligation-3-analytic-limits`) and the bridge to the magnetic regime; currently mentioned only in passing or not at all.

### Top 5 computational-approach recommendations

1. **Symmetrized collision matrix + null-space deflation** as the canonical BTE representation. Makes Onsager symmetry, detailed balance, and the conservation null-mode structural properties of the data type, so the cert verifies them once per object, not per call.
2. **Tetrahedron method for all Fermi-window / DOS-weighted integrals** (both transport and thermodynamic). Exact sum-rule preservation; uniform numerical signature across regimes; strong cross-regime conservation cert.
3. **Semi-implicit Fourier-spectral as default Cahn–Hilliard / Allen–Cahn stepper.** $O(N \log N)$ per step, unconditionally stable with a stabilization parameter; FFT diagonalizes the stiff bi-Laplacian. PRISMS-PF (matrix-free FEM) is the documented fall-back for non-periodic geometry.
4. **BKL binary-tree kMC + Wegscheider cycle-basis reduction of rate constants** (project away dependent rates at network-construction time). Makes detailed balance structural rather than residual, and removes the dominant degenerate-parameter pathology.
5. **A single cross-regime cert obligation `M-positive-on-physical-subspace`** applied to the BTE collision matrix, the CH/AC mobility tensor, and the symmetrized master-equation rate matrix. One typed primitive, three load-bearing checks — the cleanest cross-regime cert in the audit.

Sources used to verify state-of-art:
- [AMSET / Nature Comms 2021](https://www.nature.com/articles/s41467-021-22440-5)
- [Quality of CRTA/SERTA/MRTA approximations](https://arxiv.org/pdf/2202.12605)
- [ShengBTE](https://www.shengbte.org/)
- [almaBTE](https://www.sciencedirect.com/science/article/abs/pii/S0010465517302059)
- [PRISMS-PF](https://www.nature.com/articles/s41524-020-0298-5)
- [GPU FS phase-field](https://arxiv.org/pdf/2306.04322)
- [MKMCXX](https://www.mkmcxx.nl/)
- [CatMAP](https://catmap.readthedocs.io/en/latest/tutorials/creating_a_microkinetic_model.html)
- [SPPARKS](https://spparks.github.io/features.html)
- [Zacros](https://royalsocietypublishing.org/rsta/article/381/2250/20220235/112404)
- [ATAT + SQS](https://arxiv.org/pdf/0906.1608)
