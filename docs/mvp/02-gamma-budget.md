---
id: mvp-02-gamma-budget
title: γ̂ budget at MVP scale
status: draft
revision: 1
canonical-for:
  - γ̂ MVP budget
depends-on: []
referenced-by: []
research-sources: []
---
# γ̂ budget at MVP scale

The dense one-body density matrix is `O(N_r²)` and was flagged as a feasibility
risk. At MVP scale it is a non-issue, because γ̂ is **never densified**:

- **Encoding:** `(Reciprocal, BlockDiag)` — one block per k-point — with each block
  stored as **orbitals** (low-rank in the band index: `N_PW × N_b`), not as a
  dense `N_PW × N_PW` matrix.
- **Sizing (primitive cell, G₀W₀-capable basis):** PW cutoff ~400 eV ⇒ `N_PW ≈ 1000`;
  `N_b ≈ 40` (4 occupied + unoccupied manifold for G₀W₀); 8×8×8 Monkhorst–Pack ⇒
  **~29 irreducible k-points**. Orbital storage ≈ `N_PW × N_b × 16 B × N_k`
  ≈ 1000 × 40 × 16 × 29 ≈ **~18 MB**. (Densifying would cost `N_PW² × 16 × N_k`
  ≈ 460 MB per the same mesh — which is exactly why we never do it.)
- **Warm-start initializer:** tight-binding **3NN sp³d⁵** for carbon ⇒ a `~18 × 18` Hamiltonian
  per k — kilobytes. Used to seed the SCF inner loop (`mvp-05-decisions-forced`);
  not a separate residual path.
- **Beyond the MVP:** defect/interface supercells grow `N_PW` linearly; orbital
  storage stays ≈ linear in `N_atoms × N_b`. The dense-γ̂ concern returns only if
  a large supercell is densified — which the encoding forbids. A supercell memory
  budget is the first thing to revisit when leaving the primitive cell.

---
