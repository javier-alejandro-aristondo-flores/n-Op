"""CodomainAttentionKernel: attention where the tokens are channels, not grid points.

Queries, keys, and values are produced per channel by spectral kernels whose weights are
shared across channels (the sharing is what makes the channel count variable — token counts
run five to eight across this corpus under the spin-block law). Attention scores are L²
inner products of token functions, taken with the representation's quadrature; the attention
map is at most eight by eight and costs a rounding error next to the spectral convolutions.
"""
