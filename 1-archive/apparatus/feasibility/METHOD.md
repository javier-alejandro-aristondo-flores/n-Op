# Method — what carried across all four gates

Conventions shared by the four studies, and the method corrections each one earned. This
exists so a correction found in one gate is not buried inside that gate's verdict, where
the next campaign would have to already know to look for it.

## Shared conventions

| | |
|---|---|
| **Statistics** | k-point-weighted throughout |
| **Fitted constants** | weighted medians, which are L1-optimal for the reported MAE — the treatment most favorable to the rigid models, and therefore conservative for a kill test |
| **Density-of-states broadening** | σ = 0.3 eV. With a coarse k-mesh the raw spectrum is a comb of spikes, so a smaller σ measures the comb rather than the physics. Gates 2 and 3 quote it as the realistic figure; Gate 4 kept it for comparability |
| **Cross-validation** | grouped, never plain, wherever the samples are not independent |
| **Outputs** | on `/Pool` while a gate ran, asserted at the top of every script; `POTCAR` denied by assertion, never by omission from a keep-list |

## Corrections earned, and what each cost

**A checksum is not a rerun.** *(Gate 4, step 1.)* The dataset documents 24 shapes computed
three times and says the copies are bit-identical. Testing that on raw file hashes reported
the opposite — 72 of 144 EIGENVAL comparisons *differing*. Comparing the parsed numbers
instead gives a largest difference of exactly **0 eV**. The HSE `INCAR` sets
`System = <directory name>`, so the copies carry different name strings in line 5 and
identical physics in every other line. The documentation was right; the instrument was
wrong. **Compare content, not bytes, when the question is about content.**

**Character matching is ill-posed in a small single-element cell.** *(Gate 4, step 5.)*
Assigning PBE to HSE bands by lm-character overlap alone drove the fitted unoccupied
intercept to **−14.7 eV**: in a two-atom all-carbon cell every band is s/p-derived, so an
occupied and an unoccupied state can carry near-identical character vectors and a
pure-overlap assignment swaps them across the gap. Gate 2's cost — energy difference plus
λ = 2.0 eV × character mismatch — resolves it. Under that cost, plain index matching
changes the coefficients by at most **2.2 × 10⁻⁴**, so index order was adopted as
*validated*, not assumed.

**Grouped cross-validation, and why it is kept even when it changes nothing.** Gate 3 found
grouping by dopant set was doing real work — plain leave-one-out flattered every tier by up
to 0.028 eV, and Tier A would have looked meaningfully better than it was. Gate 4 grouped by
symmetry orbit and found it changed the answer by 0.1 meV. Both results are reported. The
second is not evidence the grouping was unnecessary; it is evidence that no model was
exploiting symmetry-image leakage, which is a fact about the models worth having.

**A measured noise floor, not an assumed one.** Gate 3 measured the permutation-importance
noise floor directly and found its own headline feature ranking was a 2σ draw — the
"strongest" descriptor was worth 0.0021 ± 0.0025 eV, with one of six draws negative. Gate 4
measured its floor from symmetry twins (213 orbits, 996 points) and got 0.011 meV on the
gap, six hundred times below the threshold the gate then used. In both cases the number
that mattered came from measuring the instrument rather than trusting it.

**A degeneracy check must test the symmetry it names.** *(Gate 4.)* Checking the Γ valence
triplet on all *shear-free* cells reported a 3064 meV "splitting". Shear-free is not cubic:
a cell stretched unequally along x, y and z splits the triplet through the tetragonal
deformation potential b. Restricted to genuinely **isotropic** strain, the splitting is
0.002 meV. A control that fires on correct physics is not a control.

**Tolerances must be ones the data can meet.** *(Gate 4.)* A 1e-12 isotropy test rejected 39
of 47 isotropic cells, because family 1's `POSCAR`s use an a₁-along-x frame whose residual
shear survives at 1e-11 — a trap the dataset itself documents.

## A note on filenames

Directory names were anglicized on the way in: `pbe_hse_eig` became
`gate-2-eigenvalue-correction`. The files *inside* were not touched. Each `VERDICT.md` ends
in a **Files** section listing its evidence by bare filename, so renaming the contents
would desynchronize every verdict from its own manifest. The verdicts are primary records
and moved byte-for-byte; the resulting snake_case inside a kebab-case repository is
deliberate.
