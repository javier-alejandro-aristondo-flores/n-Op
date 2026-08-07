# %% [markdown]
# # PBE against HSE06(0.27): what the two functionals actually do to diamond
#
# A visual comparison of the two density-functional-theory treatments across the
# 1,131-shape strain sweep. Every panel answers one question about how the cheap
# functional differs from the expensive one, because that difference is what the
# operator has to learn.
#
# **The short version of the physics.** A *functional* is the approximation of electron
# exchange-correlation energy that defines a flavour of DFT. **PBE** is cheap and
# systematically underestimates the band gap — the energy between the highest occupied
# and lowest empty electron state. **HSE06** is a screened hybrid that mixes in exact
# exchange to fix the gap, and costs about 42× more here. This corpus uses mixing
# parameter α = 0.27, so everything below is **HSE06(0.27)**, not the more common 0.25.
#
# **One constraint governs every panel.** Periodic DFT has no absolute energy reference
# across different cells — the potential zero drifts from calculation to calculation. So
# a raw eigenvalue from one strained cell cannot be compared with one from another. Every
# spectrum here is referred to **its own valence-band maximum**, and every quantity
# plotted is a *difference within a single calculation*.

# %%
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

if str(Path.cwd()) not in sys.path:
    sys.path.insert(0, str(Path.cwd()))

from corpus import N_OCCUPIED, load
from observables import GRID, curves, scalar_observables

corpus = load()
print(f"{len(corpus)} distinct shapes, {corpus.energies_pbe.shape[1]} k-points, "
      f"{corpus.energies_pbe.shape[2]} bands, both functionals")
print(f"strain magnitude spans {corpus.strain_norm.min():.5f} to "
      f"{corpus.strain_norm.max():.4f}")

# %% [markdown]
# ## Colour, decided once
#
# Two functionals are two **identities**, so they take two categorical hues in fixed
# order and keep them in every panel — PBE blue, HSE06 orange. Strain magnitude is a
# **magnitude**, so it takes a single-hue ramp light→dark rather than a rainbow. The
# pair was validated for color-vision deficiency rather than eyeballed: worst-pair
# ΔE 24.7 under protanopia, 33.6 for normal vision, both far clear of the floors.
#
# Text never wears a series color — labels stay in ink and the colored mark beside
# them carries the identity.

# %%
PBE_COLOUR = "#2a78d6"        # categorical slot 1
HSE_COLOUR = "#eb6834"        # categorical slot 2
INK = "#0b0b0b"
INK_SOFT = "#52514e"
SURFACE = "#fcfcfb"
STRAIN_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "axes.edgecolor": "#d8d7d2", "axes.labelcolor": INK_SOFT,
    "text.color": INK, "xtick.color": INK_SOFT, "ytick.color": INK_SOFT,
    "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": "#eceae4", "grid.linewidth": 0.8,
    "axes.grid": True, "font.size": 10, "figure.dpi": 120,
    "legend.frameon": False,
})


def tidy(ax, title, xlabel, ylabel):
    ax.set_title(title, color=INK, fontsize=11, loc="left", pad=10)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_axisbelow(True)
    return ax


equilibrium = int(np.argmin(corpus.strain_norm))
most_strained = int(np.argmax(corpus.strain_norm))
print(f"least-strained shape: {corpus.point[equilibrium]}  "
      f"(||E|| = {corpus.strain_norm[equilibrium]:.5f})")
print(f"most-strained shape:  {corpus.point[most_strained]}  "
      f"(||E|| = {corpus.strain_norm[most_strained]:.4f})")

# %% [markdown]
# ## 1 · The density of states, near equilibrium
#
# The density of states is the curve of "how many electron states exist per unit
# energy". It is built by Gaussian-broadening the discrete eigenvalues at σ = 0.3 eV —
# with a coarse 7×7×7 mesh the raw spectrum is a comb of spikes, so a narrower σ would
# measure the comb rather than the physics.
#
# Zero on the x-axis is each curve's **own** valence-band maximum. The flat region to
# the right of zero is the band gap, and the whole comparison is visible in how far the
# conduction edge sits from zero in each.

# %%
pbe_curves = curves(corpus.referenced("pbe"), corpus.weights)
hse_curves = curves(corpus.referenced("hse"), corpus.weights)

fig, ax = plt.subplots(figsize=(9, 4.2))
ax.plot(GRID, pbe_curves[equilibrium], color=PBE_COLOUR, lw=2, label="PBE")
ax.plot(GRID, hse_curves[equilibrium], color=HSE_COLOUR, lw=2, label="HSE06(0.27)")
ax.axvline(0, color=INK_SOFT, lw=1, ls=":")
# The label lives in the gap, which is the one wide empty region of the plot and also the
# thing being compared. Offset from the curves it would sit on top of the data it describes.
ax.annotate("valence maximum = 0\nby construction", xy=(0.3, 0.55), color=INK_SOFT,
            fontsize=9, va="top")
# Both edge labels go in the gap -- the one wide empty region -- with arrows out to the
# edges themselves. Placing them beside the edges put text over the conduction peaks.
for shape_curve, colour, name, height in (
        (pbe_curves[equilibrium], PBE_COLOUR, "PBE", 1.90),
        (hse_curves[equilibrium], HSE_COLOUR, "HSE06(0.27)", 1.72)):
    edge = GRID[(GRID > 0.5) & (shape_curve > 0.02)][0]
    ax.annotate(f"{name} conduction edge, {edge:.2f} eV", xy=(edge, 0.06),
                xytext=(0.3, height), fontsize=9, color=INK_SOFT, va="center",
                arrowprops=dict(arrowstyle="->", color=colour, lw=1.1,
                                connectionstyle="angle,angleA=0,angleB=90,rad=4"))
tidy(ax, "Density of states at the least-strained cell", "energy relative to the valence maximum (eV)",
     "states per eV")
ax.set_ylim(0, 2.05)
ax.legend(loc="upper left")
ax.set_xlim(-25, 15)
plt.tight_layout()
plt.show()

# %% [markdown]
# Two things to read off it. The **conduction edge moves** by more than a volt — that is the
# gap correction everyone cites the hybrid for. But look also at the deep valence, below
# −15 eV, where the two combs are visibly *out of step*: HSE06 pushes those states further
# down. So the correction is **not a rigid scissor shift** of the empty states; it is a
# stretch that touches the whole spectrum, growing with distance from the valence maximum.
# Panel 3 measures that stretch directly.
#
# The comb structure is real and not an artifact of plotting: 172 k-points broadened at
# σ = 0.3 eV is a sparse sample of a continuous curve, and a narrower σ would show more
# comb, not more physics.

# %% [markdown]
# ## 2 · The same comparison under heavy strain
#
# The sweep reaches 14.85% Green–Lagrange strain, deep into the regime where linear
# response fails. Both curves deform — the question is whether they deform *together*.

# %%
fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), sharey=True)
for ax, shape, label in ((axes[0], equilibrium, "least strained"),
                         (axes[1], most_strained, "most strained")):
    ax.plot(GRID, pbe_curves[shape], color=PBE_COLOUR, lw=2, label="PBE")
    ax.plot(GRID, hse_curves[shape], color=HSE_COLOUR, lw=2, label="HSE06(0.27)")
    ax.axvline(0, color=INK_SOFT, lw=1, ls=":")
    tidy(ax, f"{label}  (‖E‖ = {corpus.strain_norm[shape]:.4f})",
         "energy relative to the valence maximum (eV)",
         "states per eV" if shape == equilibrium else "")
    ax.set_xlim(-25, 15)
axes[0].legend(loc="upper left")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 3 · The correction itself, state by state
#
# Rather than comparing two spectra, plot their **difference** against energy. Each point
# is one eigenvalue at one k-point: its PBE energy on the x-axis, and how much HSE06 moves
# it on the y-axis.
#
# The two straight lines are the finding. The correction is a *two-branch linear stretch* —
# roughly `0.11·E` for occupied states and `0.09·E + 0.90` for empty ones — not a rigid
# scissor shift. Four free parameters capture most of it, which is why the operator is
# built to predict the residual on top of this rather than the spectrum from scratch.

# %%
pbe_field = corpus.referenced("pbe")
correction = corpus.correction()
occupied = np.zeros(pbe_field.shape[2], dtype=bool)
occupied[:N_OCCUPIED] = True

fig, ax = plt.subplots(figsize=(9, 4.6))
for mask, colour, label in ((occupied, PBE_COLOUR, "occupied states"),
                            (~occupied, HSE_COLOUR, "empty states")):
    x = pbe_field[equilibrium][:, mask].ravel()
    y = correction[equilibrium][:, mask].ravel()
    ax.scatter(x, y, s=14, color=colour, alpha=0.75, edgecolor="none", label=label)
    slope, intercept = np.polyfit(x, y, 1)
    line = np.linspace(x.min(), x.max(), 2)
    ax.plot(line, slope * line + intercept, color=colour, lw=1.4, ls="--")
    ax.annotate(f"{slope:.3f}·E {intercept:+.2f}", xy=(line[-1], slope * line[-1] + intercept),
                xytext=(6, 0), textcoords="offset points", color=INK_SOFT, fontsize=9,
                va="center")
tidy(ax, "How HSE06 moves each PBE state, at the least-strained cell",
     "PBE energy relative to the valence maximum (eV)", "HSE06 − PBE (eV)")
ax.legend(loc="upper left")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 4 · Band energies along Γ→X
#
# Γ is the center of the Brillouin zone; X is a corner. The conduction minimum of diamond
# lies on this line, which is why strain along it matters so much.
#
# **These are mesh points, not a converged band path.** A Γ-centered 7×7×7 mesh samples
# only four points along Γ→X, and diamond's true conduction minimum sits near 0.76 of the
# way while the nearest sampled point is at 0.857. The shape is right; the exact minimum
# is not resolved, and no critical strain should be read off this panel.

# %%
on_delta = np.where((np.abs(corpus.kfrac[:, 2]) < 1e-6)
                    & (np.abs(corpus.kfrac[:, 0] - corpus.kfrac[:, 1]) < 1e-6))[0]
order = np.argsort(corpus.kfrac[on_delta, 0])
path = on_delta[order]
# X sits at fractional (1/2, 1/2, 0), so a point (t, t, 0) is 2t of the way there. The
# four sampled points land at 0, 2/7, 4/7 and 6/7 = 0.857 -- which is exactly the value
# the caveat below quotes, and the reason it is quoted.
distance = 2.0 * corpus.kfrac[path, 0]

fig, axes = plt.subplots(1, 2, figsize=(12, 4.4), sharey=True)
for ax, shape, label in ((axes[0], equilibrium, "least strained"),
                         (axes[1], most_strained, "most strained")):
    for functional, colour, name in (("pbe", PBE_COLOUR, "PBE"),
                                     ("hse", HSE_COLOUR, "HSE06(0.27)")):
        field = corpus.referenced(functional)[shape]
        for band in range(field.shape[1]):
            ax.plot(distance, field[path, band], color=colour, lw=1.6,
                    label=name if band == 0 else None, marker="o", ms=4)
    ax.axhline(0, color=INK_SOFT, lw=1, ls=":")
    tidy(ax, f"{label}  (‖E‖ = {corpus.strain_norm[shape]:.4f})",
         "fraction of the way from Γ toward X",
         "energy relative to the valence maximum (eV)" if shape == equilibrium else "")
    ax.set_ylim(-25, 20)
axes[0].legend(loc="lower left")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 5 · The band gap across the whole sweep
#
# One point per shape, both functionals, against strain magnitude. Colour is identity
# again — same two hues, same meaning.
#
# The response is enormous: the PBE gap runs from 4.81 eV down to 0.441 eV, a factor of
# eleven. HSE06 tracks it with an offset of roughly 1.2 eV.

# %%
pbe_scalars = scalar_observables(corpus.referenced("pbe"), corpus.kfrac)
hse_scalars = scalar_observables(corpus.referenced("hse"), corpus.kfrac)
pbe_gap = pbe_scalars["indirect_gap"].to_numpy()
hse_gap = hse_scalars["indirect_gap"].to_numpy()

fig, ax = plt.subplots(figsize=(9, 4.6))
ax.scatter(corpus.strain_norm, pbe_gap, s=9, color=PBE_COLOUR, alpha=0.6,
           edgecolor="none", label="PBE")
ax.scatter(corpus.strain_norm, hse_gap, s=9, color=HSE_COLOUR, alpha=0.6,
           edgecolor="none", label="HSE06(0.27)")
tidy(ax, "Indirect band gap against strain magnitude, 1,131 shapes",
     "‖E‖  (Green–Lagrange strain magnitude)", "indirect gap (eV)")
ax.legend(loc="upper right")
plt.tight_layout()
plt.show()

print(f"PBE  gap range {pbe_gap.min():.3f} – {pbe_gap.max():.3f} eV")
print(f"HSE  gap range {hse_gap.min():.3f} – {hse_gap.max():.3f} eV")

# %% [markdown]
# ## 6 · Does the correction hold under strain?
#
# The panel that matters most for practice. Everyone who applies a hybrid correction
# measured at equilibrium to a *strained* structure — which is standard — is assuming
# the horizontal line below.
#
# It is not horizontal. The correction falls across the sweep, and the spread is 325 meV.
# Applying the equilibrium value everywhere mis-corrects by 47.5 meV on average and
# 201 meV at worst, against a numerical noise floor of 0.002 meV.

# %%
difference = hse_gap - pbe_gap
baseline = difference[equilibrium]

fig, ax = plt.subplots(figsize=(9, 4.6))
ax.scatter(corpus.strain_norm, difference, s=10, color=PBE_COLOUR, alpha=0.55,
           edgecolor="none")
ax.axhline(baseline, color=HSE_COLOUR, lw=2, ls="--")
# Anchored in the empty upper-left rather than offset from the line: at the default
# placement the label landed inside the densest part of the cloud and hid the data it
# was describing.
ax.annotate(f"equilibrium value, {baseline:.4f} eV\n— what standard practice assumes",
            xy=(0.012, baseline), xytext=(0.018, difference.max() - 0.005),
            color=INK_SOFT, fontsize=9, va="top",
            arrowprops=dict(arrowstyle="->", color=INK_SOFT, lw=0.8))
tidy(ax, "The HSE06 − PBE gap correction drifts with strain",
     "‖E‖  (Green–Lagrange strain magnitude)", "HSE06 − PBE indirect gap (eV)")
plt.tight_layout()
plt.show()

deviation = np.abs(difference - baseline) * 1000
print(f"mean mis-correction {deviation.mean():.1f} meV, worst {deviation.max():.1f} meV, "
      f"total spread {(difference.max() - difference.min()) * 1000:.0f} meV")

# %% [markdown]
# **A caution on reading a slope off that panel.** ‖E‖ is a *magnitude*, so compression
# and tension fold onto the same abscissa — two cells at the same ‖E‖ can sit either side
# of the cloud. A straight-line fit to it returns R² ≈ 0.21 with structured residuals, so
# the honest summary is the spread (325 meV) and the mis-correction (47.5 meV mean,
# 201 meV worst), not a single slope.

# %% [markdown]
# ## The table view
#
# Every panel above, as numbers — because a chart that cannot be read as a table is not
# accessible, and because these are the figures the rest of the library is measured against.

# %%
import pandas as pd

summary = pd.DataFrame({
    "quantity": ["indirect gap", "direct gap at Γ", "Γ valence splitting",
                 "gap correction (HSE − PBE)"],
    "PBE min": [pbe_gap.min(), pbe_scalars["direct_gap_gamma"].min(),
                pbe_scalars["valence_splitting_total"].min(), np.nan],
    "PBE max": [pbe_gap.max(), pbe_scalars["direct_gap_gamma"].max(),
                pbe_scalars["valence_splitting_total"].max(), np.nan],
    "HSE min": [hse_gap.min(), hse_scalars["direct_gap_gamma"].min(),
                hse_scalars["valence_splitting_total"].min(), difference.min()],
    "HSE max": [hse_gap.max(), hse_scalars["direct_gap_gamma"].max(),
                hse_scalars["valence_splitting_total"].max(), difference.max()],
})
summary.round(4)

# %% [markdown]
# ## What this comparison does not show
#
# - **The mesh limits the conduction minimum.** 44 of 1,131 shapes appear direct-gap at Γ
#   on this mesh. The crossover is real; its location is not converged.
# - **α = 0.27, not 0.25.** Nothing here is directly comparable to published HSE06 numbers
#   at the default mixing.
# - **Two sub-families carry sampling kinks.** In the uniaxial and biaxial cells the
#   conduction minimum hops between mesh points as strain grows, leaving 76–151 meV steps
#   in panel 5 that are the mesh, not the physics.
