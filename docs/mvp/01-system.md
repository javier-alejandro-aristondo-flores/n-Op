---
id: mvp-01-system
title: The system
status: draft
revision: 1
canonical-for:
  - diamond MVP system
depends-on: []
referenced-by: []
research-sources: []
---
# The system

**Diamond, primitive cell.** Space group Fd-3m (No. 227); 2 carbon atoms at the
8a Wyckoff site; sp³; lattice constant a = 3.567 Å. Eight valence electrons
(2s²2p² × 2) → **4 occupied bands**.

| Anchor | Value | Consequence for the MVP |
|---|---|---|
| Indirect gap | 5.47 eV (X-point) | PBE gives ~4.2 eV (−23%); **G₀W₀ or hybrid required** (registry row 6) |
| Max phonon energy | ~165 meV (~1332 cm⁻¹) | highest of any solid; phonon grid must resolve it |
| Debye temperature | ~2200 K | **QHA valid through ~800 °C** → SCPH (row 13) deferred |
| Thermal conductivity | ~2000 W·m⁻¹K⁻¹ | the headline Cap-3 target |
| Elastic constants | C₁₁≈1079, C₁₂≈124, C₄₄≈578 GPa | Cap-1 stability + sound velocity |
| Polarity | **non-polar (homopolar)** | Z\*=0 by symmetry → **no LO-TO, no Fröhlich** → registry rows 17, 21, 22 excluded by applicability |
| High-T failure | sp³→sp² (graphitization) above ~700 °C in vacuum | the diamond–graphite phase boundary is the Cap-1 thermodynamic check |

**Units.** Atomic units internally; report eV, Å, W·m⁻¹K⁻¹, cm²V⁻¹s⁻¹.

---
