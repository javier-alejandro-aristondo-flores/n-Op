"""Cheap-functional (PBE) charge density → accurate-functional (HSE) charge density.

The residual correction operator with conformal intervals — the best local-first science in
the suite: 1,339 byte-verified same-geometry pairs whose whole tensor set fits in the
resident card's memory. Δ-learning framing: Ramakrishnan, Dral, Rupp, von Lilienfeld — JCTC
11, 2087 (2015); multifidelity operator form: Howard, Perego, Karniadakis, Stinis — J.
Comput. Phys. 493, 112462 (2023); transfer protocol: Subramanian et al., NeurIPS 2023;
intervals: Romano, Patterson, Candès — NeurIPS 2019. test-suite.md §5, entries IV.1 + IV.3.

Not an architecture: an assembly of wrappers over a backbone. Residual (zero-initialized —
training starts exactly at the measured identity floor of 1.11–1.19% relative error),
Conditioned (campaign / exact-exchange fraction), Conserving (the correction integrates to
zero exactly — both fidelities share the electron count), and the ConformalCalibrator at the
symmetry-orbit level. Backbone: the Deep Operator Network's projection form first (wave 1),
the factorized Fourier operator later (wave 2) — a configuration switch, which is the point
of the framework.
"""

from operators.framework import Operator


class ResidualCorrection(Operator):
    """The wrapper assembly. Backbone and settings fixed in the implementation phase."""

    def __init__(self) -> None:
        raise NotImplementedError("implementation phase — see IMPLEMENTATION.md")

    def __call__(self, v, out, condition=None):
        raise NotImplementedError("implementation phase — see IMPLEMENTATION.md")
