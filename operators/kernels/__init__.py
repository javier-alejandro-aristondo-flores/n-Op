"""Concrete kernels: the five fused parametrization × measure pairings.

    spectral            SpectralKernel — translation-invariant, multiply in Fourier space
    compact_support     CompactSupportKernel — convolution on grids ≡ message passing on points
    low_rank            LowRankKernel and DenseKernel — the universal and the finite
    codomain_attention  CodomainAttentionKernel — attention where tokens are channels

Every kernel here must match ``framework.integral.dense_reference_integral`` on small
problems before it is trusted at size.
"""
