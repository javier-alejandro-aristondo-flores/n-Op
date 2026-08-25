"""Encoders — concrete Operators that carry the input into channel space.

Intended contents (implementation phase):
  - PointwiseLift — widen channels point by point (the grid operators' entrance)
  - SensorEncoder — a whole input read into a finite vector (the branch of the
    branch–trunk family; parameters enter here too)
  - BasisProjectionEncoder — project onto a data-derived basis (proper-orthogonal /
    principal-component variants)
  - AtomEmbedding — species and positions onto point features, keyed by (element,
    pseudopotential title): twelve elements ship with two pseudopotential variants across
    campaigns, and the embedding must not conflate them
  - VariableEncoding — per-field learned encodings for variable channel sets (the
    codomain-attention operator's entrance)

No abstract class here: an encoder is just an Operator.
"""
