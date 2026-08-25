"""Neural operators over the n-Op DFT corpus, as one integral-transform framework.

Every named operator in this package is an assembly of parts from ``operators.framework``:
an encoder, zero or more kernel-integral layers under a composition scheme, a readout, and
optional wrappers. The framework's four abstract classes — Operator, Representation, Kernel,
Composition — are the whole vocabulary; see ``operators/README.md`` for the anatomy and
``test-suite.md`` at the repository root for what each operator is for, its data, its floors,
and its kill thresholds.
"""
