"""The differentiation boundary. Plain arrays cross it; nothing else does.

**Why this module exists at all.** `journals/n-op/build/forced-decisions.md` records that
core infrastructure is built in-house and that "a framework that would own differentiation
is a liability rather than an asset", with the implementation language still open. The
project's own numerics library, `numbers`, is a certifying generator of dual-number and
Taylor-jet libraries -- **forward** mode over six transcendental families, machine-checked
in ACL2. That is the right instrument for an oracle's elementary functions and the wrong
one for training: forward mode costs one pass per parameter, and these models carry tens of
thousands.

So reverse mode is borrowed, and quarantined here. Every public entry point takes and
returns `numpy` arrays; no tensor, tape or graph is reachable from outside this file. That
keeps the corpus's seam rule -- *"only flat numeric arrays cross the boundary -- no
framework tensors with attached tapes, no lazy graphs, no callbacks"*
(`learnable-structure-contract#seam-purity`) -- true from the first commit rather than as a
later cleanup, and it means replacing the substrate is an edit to one file.

**Precision.** The spec allows float32 at the network boundary and requires float64 for
canonicalization and metrics. Training runs in float32; everything that leaves does so as
float64, and every metric downstream is computed there.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

import numpy as np
import torch

TORCH_DTYPE = torch.float32
OUT_DTYPE = np.float64
DEVICE = torch.device("cpu")

__all__ = ["seed_everything", "parameter_count", "weighted_absolute_error", "fit",
           "predict_in_batches", "TrainingReport"]


def seed_everything(seed: int) -> None:
    """Fix every generator this module can reach. Reported in provenance."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)


def parameter_count(module: torch.nn.Module) -> int:
    return int(sum(p.numel() for p in module.parameters() if p.requires_grad))


def _as_tensor(array: np.ndarray) -> torch.Tensor:
    return torch.as_tensor(np.ascontiguousarray(array), dtype=TORCH_DTYPE, device=DEVICE)


def _as_array(tensor: torch.Tensor) -> np.ndarray:
    return tensor.detach().cpu().numpy().astype(OUT_DTYPE)


def weighted_absolute_error(prediction: torch.Tensor, target: torch.Tensor,
                            kweights: torch.Tensor) -> torch.Tensor:
    """k-weighted mean absolute error over a (batch, n_k, n_band) field.

    The 172 points are what survives folding a 7x7x7 mesh by time reversal, and they carry
    unequal multiplicities. Weighting by them is what makes this the Brillouin-zone average
    rather than an average over an arbitrary list.

    Absolute rather than squared, deliberately: the sorted-eigenvalue field has genuine
    kinks where bands cross, and the conduction minimum hops between mesh points on two
    families. Squared error would let those few points dominate the gradient.
    """
    per_state = (prediction - target).abs().mean(dim=-1)          # over bands
    return (per_state * kweights).sum(dim=-1).mean() / kweights.sum()


def indirect_gap(field: torch.Tensor, n_occupied: int = 4) -> torch.Tensor:
    """min over the mesh of the conduction bands, minus max of the valence bands.

    The same mesh-minimum procedure the ground-truth extraction uses, so a model scored on
    it is scored like for like. `amin`/`amax` are differentiable almost everywhere; the
    subgradient at a tie is what makes the argmin-hopping families a genuine kink rather
    than a discontinuity, which is one more reason the primary loss is L1.
    """
    valence = field[..., :n_occupied].amax(dim=-1).amax(dim=-1)
    conduction = field[..., n_occupied:].amin(dim=-1).amin(dim=-1)
    return conduction - valence


@dataclass
class TrainingReport:
    """What a fit did, for the provenance record and the error card."""

    parameters: int
    epochs_run: int
    best_epoch: int
    best_validation: float
    training_curve: list[float] = field(default_factory=list)
    validation_curve: list[float] = field(default_factory=list)


def fit(module: torch.nn.Module, inputs: dict[str, np.ndarray], target: np.ndarray,
        kweights: np.ndarray, *, train_index: np.ndarray, validation_index: np.ndarray,
        epochs: int = 400, batch_size: int = 64, learning_rate: float = 3e-3,
        weight_decay: float = 1e-5, patience: int = 40, seed: int = 0,
        verbose: bool = False, gap_weight: float = 0.0,
        base_field: np.ndarray | None = None) -> TrainingReport:
    """Adam with weight decay and early stopping on a held-out fold.

    Both regularizers are required by the spec at this sample count, and the stopping
    signal is an *inner* validation fold -- never the frozen exams.

    **`gap_weight` is an auxiliary derived-observable term, and it is off by default.**
    The spec permits one (§6.2) provided every weight is logged and its inclusion is
    justified by inner-fold improvement rather than by test behavior. It is *not* the
    prohibited thing: §6.4 forbids up-weighting the gap *region of the energy window*
    inside the per-eigenvalue loss, on the sound argument that doing so optimizes the
    quantity the exams measure. A term on the derived observable is a different mechanism
    and is explicitly allowed.

    It exists because the gap is two extremal states out of 1,376, so a field-averaged
    loss barely weights them -- which is why the per-shape stretch fitted *on the answer*
    still leaves 127 meV of gap error while a single scalar constant leaves 47.5.
    """
    seed_everything(seed)
    tensors = {name: _as_tensor(value) for name, value in inputs.items()}
    target_tensor = _as_tensor(target)
    weight_tensor = _as_tensor(kweights)
    base_tensor = None if base_field is None else _as_tensor(base_field)
    if gap_weight and base_tensor is None:
        raise ValueError("a gap term needs the PBE field it is added to")

    def total_loss(prediction: torch.Tensor, rows: np.ndarray) -> torch.Tensor:
        loss = weighted_absolute_error(prediction, target_tensor[rows], weight_tensor)
        if gap_weight:
            predicted_gap = indirect_gap(base_tensor[rows] + prediction)
            true_gap = indirect_gap(base_tensor[rows] + target_tensor[rows])
            loss = loss + gap_weight * (predicted_gap - true_gap).abs().mean()
        return loss

    optimiser = torch.optim.Adam(module.parameters(), lr=learning_rate,
                                 weight_decay=weight_decay)
    # An L1 loss has constant gradient magnitude, so a step size that is right early is
    # too large near a minimum and the loss orbits it instead of settling. Cosine decay
    # to a hundredth of the initial rate; without it the training curve oscillates by
    # more than the residual being chased.
    schedule = torch.optim.lr_scheduler.CosineAnnealingLR(optimiser, T_max=epochs,
                                                          eta_min=learning_rate / 100)
    generator = np.random.default_rng(seed)

    best_state = {k: v.detach().clone() for k, v in module.state_dict().items()}
    report = TrainingReport(parameters=parameter_count(module), epochs_run=0,
                            best_epoch=-1, best_validation=float("inf"))

    for epoch in range(epochs):
        module.train()
        order = generator.permutation(len(train_index))
        total, batches = 0.0, 0
        for start in range(0, len(order), batch_size):
            rows = train_index[order[start:start + batch_size]]
            optimiser.zero_grad(set_to_none=True)
            prediction = module(**{k: v[rows] for k, v in tensors.items()})
            loss = total_loss(prediction, rows)
            loss.backward()
            optimiser.step()
            total += float(loss.detach())
            batches += 1
        schedule.step()

        module.eval()
        with torch.no_grad():
            prediction = module(**{k: v[validation_index] for k, v in tensors.items()})
            validation = float(total_loss(prediction, validation_index))

        report.epochs_run = epoch + 1
        report.training_curve.append(total / max(batches, 1))
        report.validation_curve.append(validation)

        if validation < report.best_validation - 1e-9:
            report.best_validation = validation
            report.best_epoch = epoch
            best_state = {k: v.detach().clone() for k, v in module.state_dict().items()}
        elif epoch - report.best_epoch >= patience:
            break

        if verbose and epoch % 25 == 0:
            print(f"    epoch {epoch:4d}  train {total / max(batches, 1):.5f}  "
                  f"validation {validation:.5f}", flush=True)

    module.load_state_dict(best_state)
    return report


def predict_in_batches(module: torch.nn.Module, inputs: dict[str, np.ndarray],
                       batch_size: int = 128) -> np.ndarray:
    """Forward pass, arrays in and arrays out, with no graph retained."""
    module.eval()
    count = len(next(iter(inputs.values())))
    pieces = []
    with torch.no_grad():
        for start in range(0, count, batch_size):
            stop = min(start + batch_size, count)
            batch = {name: _as_tensor(value[start:stop])
                     for name, value in inputs.items()}
            pieces.append(_as_array(module(**batch)))
    return np.concatenate(pieces, axis=0)
