"""LowRankKernel and DenseKernel: the universal pairing and the finite one.

  - LowRankKernel — κ(x, y) = Σ_j φ_j(x) · ψ_j(y): the input side is inner products of ψ_j
    against the representation's quadrature (this is where measure-as-data pays), the output
    side evaluates φ_j anywhere. Works against every measure; the branch–trunk family and the
    softmax-free attention of the Galerkin lineage are both this kernel.
  - DenseKernel — κ over a finite index set: a dense layer on Coefficients is a kernel
    integral against the counting measure, which is why the branch–trunk processors need no
    special case.
"""
