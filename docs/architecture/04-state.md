---
id: arch-04-state
title: The unified state
status: draft
revision: 1
canonical-for:
  - state 7-tuple
depends-on: []
referenced-by:
  - arch-06-physics-graph
  - arch-08-bo-levels
  - arch-15-gamma-hat
  - arch-19-coupling-structure
  - arch-20-representations
research-sources: []
---
# The unified state

The instantaneous state is the 7-tuple

```
x(t) = ( h,      cell vectors                       ∈ GL⁺(3, ℝ)   (3×3 real)
         R_I,    ion positions                      ∈ ℝ^{3N}
         P_I,    ion momenta                        ∈ ℝ^{3N}
         Π_h,    cell momentum (Parrinello–Rahman)  ∈ ℝ^{3×3}
         Z_I,    species labels (immutable)         discrete
         γ̂,      one-body density matrix            2×2 Pauli-spinor operator
                 (Pauli-spinor for magnetism)       on (r, r'; t)
         A )     external EM vector potential        ∈ ℝ³ field A(r,t)
```

These are the **irreducible degrees of freedom**. Phonon distributions
`n_{q,s}`, carrier distributions `f_n(k,r)`, surface coverages `θ_i`, electron
and lattice temperatures, current density, internal fields, defect populations,
and composition vectors are all **emergent** — coarse-grainings, Bloch
transforms, or semiclassical limits of `x(t)`. Adding any of them to the state
would create a constraint manifold tying it back to the irreducible DOFs and
reintroduce the integration pathology the formulation avoids.

`x(t)` is a **type** that the PINO's predictions instantiate at each time step.
`/physics` does not hold values of `x(t)`; it defines what `x(t)` is and how to
test a candidate against the laws.

---
