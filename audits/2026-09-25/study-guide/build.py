"""assembles the study guide from its parts, draws its diagrams to scale, grounds every fact against its source, and refuses any page number no grounded fact supports"""

import base64
import html
import math
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGE = HERE / "page"
OUT = HERE / "operator-suite-study-guide.html"
BASE = Path("/home/javier/Projects/Physics/Programs/n-Op-audit-baseline")
AUDIT = Path("/home/javier/Projects/Physics/Programs/n-Op-streams/audit-fixes/audits/2026-09-25")
SOURCES = {
    "results": BASE / "operator-results.md",
    "suite": BASE / "test-suite.md",
    "pool": Path("/Pool/VASP_DATA/read-me-first.md"),
    "staged": BASE / "operators/training/staged.py",
    "spectra": BASE / "operators/data/spectra.py",
    "coda": BASE / "operators/codomain_attention/report.md",
    "dft": BASE / "operators/deep_dft/report.md",
    "cno": BASE / "operators/alias_free_convolutional/report.md",
    "cno_spec": BASE / "operators/alias_free_convolutional/IMPLEMENTATION.md",
    "manifold_spec": BASE / "operators/nonlinear_manifold_decoder/IMPLEMENTATION.md",
    "don": BASE / "operators/deep_operator_network/report.md",
    "commits": HERE / "commits.txt",
    "counts": HERE / "counts.txt",
    "comp": HERE / "computations.txt",
    "a2": AUDIT / "outputs/a2-integrity.json",
    "a7_manifold": AUDIT / "outputs/a7-manifold.log",
    "a7_correction": AUDIT / "outputs/a7-correction.log",
    "a7_explicit": AUDIT / "outputs/a7-ladder-explicit.log",
    "a7_tied": AUDIT / "outputs/a7-ladder-weight_tied.log",
    "a7_injected": AUDIT / "outputs/a7-ladder-weight_tied_injected.log",
    "a7_matched": AUDIT / "outputs/a7-ladder-explicit_matched.log",
    "manifests": AUDIT / "outputs/a10-manifests.tsv",
    "phase_a": AUDIT / "findings/phase-a.jsonl",
    "leads": AUDIT / "findings/known-leads-verified.jsonl",
    "recheck": AUDIT / "findings/integrator-recheck.jsonl",
    "ladder": Path("/home/javier/Projects/Physics/Programs/n-Op-streams/ladder/operators/factorized_fourier/report.md"),
    "plan": Path("/home/javier/.claude/plans/now-since-we-have-dreamy-panda.md"),
}

FACTS = [
    ("results", "the branch–trunk member measured a seed spread of 14–35% of the median"),
    ("results", "ridge floor (parameters → mode coefficients); kill: beat by 25% | 0.00414 | 0.00411"),
    ("results", "nearest-neighbor field copy; kill: beat by 2× | 0.00896 | 0.00896"),
    ("results", "rank-32 projection ceiling | 0.000017 | 0.000017"),
    ("results", "| principal_component | 0.000821 | 0.001092 |"),
    ("results", "| proper_orthogonal | 0.000819 | 0.001122 |"),
    ("results", "canonical, scored on the same 40³ block | 0.001896 | 0.002413"),
    ("results", "canonical, all 124 test runs across nine grid shapes (copy floor 0.0094) | 0.002339 | 0.002766"),
    ("results", "put their paired difference at 0.5% and 1.8% against within-configuration spreads of 14–35%"),
    ("results", "88 held-out test runs over 22 orbits per functional"),
    ("results", "32,000 steps, one seed"),
    ("results", "| training-mean floor | 0.392 | 0.757 |"),
    ("results", "| ridge floor | 0.368 | 0.518 |"),
    ("results", "0.206 (44% better than the ridge) | 0.265 (49%)"),
    ("results", "| ablation, band edges weighted 5× | 0.208 | 0.193 |"),
    ("results", "248 test runs over 30 orbits"),
    ("results", "window −28 to +8 eV from the valence-band maximum"),
    ("results", "467 of 601 bins are nearly strain-invariant valence states"),
    ("results", "every truth crosses its threshold at +0.020 eV with zero spread"),
    ("results", "| fold 0 (interpolation) | 0.0423 | 0.0853 | 0.0183 pass/pass | 0.0189 pass/pass | 0.0235 pass/pass |"),
    ("results", "| factor-0.8 holdout (extrapolation) | 0.0755 | 0.0877 | 0.0937 | 0.1264 | 0.0434 |"),
    ("results", "| factor-1.2 holdout (extrapolation) | 0.0766 | 0.0877 | 0.0584 | 0.0606 | 0.0499 |"),
    ("results", "per-spin log-compressed densities plus six lattice Gram-matrix channels on the fine 80³ grid → truncation to 40³"),
    ("results", "(19 modes per axis; the canon's \"20³\" is one more than a 40-point axis can hold) at width 64, 11.55M parameters"),
    ("results", "Trained on folds 2–4 (196 runs), early-stopped on fold 1 (65 runs, 24 units), judged on fold 0 (76 runs, 29 units)"),
    ("results", "the canon's kill anchor | 0.0976 |"),
    ("results", "| per-shell linear filter (a one-layer linear Fourier operator) | 0.0830 |"),
    ("results", "| training-mean template (added) | 0.0160 |"),
    ("results", "(added, the memorization null) | 0.0062 | 0.0082 | 0.0014 |"),
    ("results", "| pooled, 29 units | 0.00217 | 1.05% | 0.9998 |"),
    ("results", "| defect set | 0.00233 | 1.35% | 0.9995 |"),
    ("results", "| strains | 0.00070 | 0.26% | 0.99999 |"),
    ("results", "| canon kill: half the semilocal ridge | ≤ 0.0488 | pass, 97.8% better than the ridge |"),
    ("results", "| canon pattern rule: 20% better than the ridge | ≤ 0.0781 | pass |"),
    ("results", "| added: beat the nearest-run copy | < 0.0062 | pass, 65% better |"),
    ("results", "| added stretch: half the template | ≤ 0.0080 | pass |"),
    ("results", "Hartree + semilocal exchange-correlation ridge 47.96% — the canon's anchor, so the bar is 23.98%"),
    ("results", "| explicit, twelve layers | 11.55M | 24,404 | 3.94 h | 3.6 GB | 8.0e-5 | 0.00217 | all pass |"),
    ("results", "| 0.96M | 23,804 | 2.69 h | 3.2 GB | 1.2e-4 | 0.00297 |"),
    ("results", "| 0.96M | 35,505 (full budget, still improving) | 0.52 h | 0.7 GB | 3.9e-4 | 0.01004 | canon levels pass; fails the copy and the stretch |"),
    ("results", "| 0.96M | 28,504 | resumed across two power losses | 3.5 GB | 1.0e-4 | 0.00271 |"),
    ("results", "injecting the input at every application buys another 9%"),
    ("results", "a four-million-entry iterate meant parts per million"),
    ("results", "width 128, four heads, four layers, 374,145 parameters"),
    ("results", "(32³ tokens, 64³ queries, the six factors as constant channels)"),
    ("results", "| fold 0 of the angle stratum, 25 runs | nearest-angle copy, the floor | 0.0853 (bar ≤ 0.0426) |"),
    ("results", "| | the training-mean field (context) | 0.1755 |"),
    ("results", "| | the member | 0.1780 — killed |"),
    ("results", "| 27 interior levels of the angle arm | linear-in-angle interpolation, the floor | 0.0264 (bar ≤ 0.0132) |"),
    ("results", "| | the member | 0.1191 — killed |"),
    ("results", "52,283 steps in its two hours at 0.138 s per step, 1.5 GB on the card"),
    ("results", "(outputs for two different structures 27% apart at initialization, 4e-8 apart after training"),
    ("results", "the top 5% of voxels carry 77% of it"),
    ("results", "245,632 parameters"),
    ("results", "(224,896 parameters)"),
    ("results", "33,650 steps each, about half an hour each at 0.11 s per step, 0.8 GB"),
    ("results", "| semilocal ridge (the pattern-rule floor) | 0.097618 |"),
    ("results", "| training-mean template | 0.015957 |"),
    ("results", "| nearest-run copy | 0.006164 |"),
    ("results", "| density-alone twin | 0.014553 |"),
    ("results", "| two-branch member | 0.016454 |"),
    ("results", "passed (83.1% better, 20% required)"),
    ("results", "against its own twin at 5% better: killed — it is 13.1% worse"),
    ("results", "48 times the density's scale"),
    ("results", "272,001 parameters; about 10,200 steps in seven minutes on the card"),
    ("results", "| 423 interior levels of the strain arms (leave one level out) | bracketing linear interpolation, the floor | 0.000911 | bar: a third better, ≤ 0.000607 |"),
    ("results", "Gaussian radial basis on the six strain components, the second floor | 0.000991 | bar ≤ 0.000661 |"),
    ("results", "| | ridge to the strain tensor (context) | 0.004225 |"),
    ("results", "| | nearest-run copy (context) | 0.019876 |"),
    ("results", "| | the member | 0.002452 | killed: 2.7× worse than interpolation |"),
    ("results", "| committed holdout split, 22 units |"),
    ("results", "| every grid shape, 30 units | the member | 0.002795 |"),
    ("results", "inflation 1.32× against a bar of 1.3×"),
    ("results", "pooled 0.091%"),
    ("results", "i.e. 0.064% relative L2"),
    ("results", "moments within 5% with the right sign on 90% of magnetic runs"),
    ("results", "24,865 parameters; 20,000 steps"),
    ("results", "| identity (return the cheap density) | 0.011131 | the floor |"),
    ("results", "| global affine | 0.010466 |"),
    ("results", "| ridge from the strain components | 0.000049 |"),
    ("results", "| ridge from the cheap density's coefficients | 0.000005 |"),
    ("results", "| rank-32 representation ceiling | 0.000002 |"),
    ("results", "| the member | 0.002079 | 81.3% better; canon kill ≤ 0.005565 passed"),
    ("results", "406 times better than the trained member"),
    ("results", "Level 0.90, exchangeable unit the symmetry orbit, calibrated on 23 validation orbits and applied to the 22 test orbits of the correction member: coverage 0.977 against a guaranteed interval of 0.900 to 0.942"),
    ("results", "| 822 committed |"),
    ("results", "rank-32 proper-orthogonal coefficients"),
    ("results", "the twelve-layer stack is still a quarter better"),
    ("suite", "costs 10–100× more"),
    ("suite", "AEXX 0.27 (diamond strain atlas), 0.25 (defect set + one pristine reference), 0.325 (alloy ensemble"),
    ("suite", "2,680 runs = 1,340 points × 2"),
    ("suite", "exactly half per axis, corpus-wide (80³→40³"),
    ("suite", "547 = 182 + 169 + 196"),
    ("suite", "full-field on 169"),
    ("suite", "64-atom pristine diamond strains"),
    ("suite", "20-atom monoclinic"),
    ("suite", "AgNbO₃ 5-atom cell"),
    ("suite", "angle sweep uniform 64³"),
    ("suite", "~40³ grids"),
    ("suite", "(120 identical g-values)"),
    ("suite", "All 48 diamond-group operations"),
    ("suite", "2-atom diamond under 1–6-axis strain"),
    ("pool", "5,085 VASP (DFT) calculation runs"),
    ("staged", "DEFAULT_STAGE_FRACTIONS = (0.3, 0.3, 0.4)"),
    ("staged", "DEFAULT_PEAK_LEARNING_RATE = 1e-3"),
    ("staged", "DEFAULT_PROBE_STEPS = 200"),
    ("staged", "DEFAULT_VALIDATION_INTERVAL = 100"),
    ("staged", "DEFAULT_FINAL_STAGE_PATIENCE = 15"),
    ("staged", "chosen_peak_rate = peak_learning_rate * 0.3"),
    ("spectra", "\"strain_atlas\": 0.175,"),
    ("coda", "the card's 5.61 GB ceiling"),
    ("coda", "parameters: 3,838,762"),
    ("coda", "2.2917 seconds per step, 2.2072 GB peak accelerator memory"),
    ("coda", "fold 0 (evaluation): 76 runs"),
    ("coda", "fold 1 (validation): 65 runs"),
    ("coda", "folds 2-4 (pretrain): 196 runs"),
    ("coda", "alloy transfer set (zero-shot only): 182 runs"),
    ("coda", "absolute bar 0.004340"),
    ("coda", "absolute bar 0.002713"),
    ("dft", "42 runs across 21 units"),
    ("dft", "18 of the 42 fold-zero runs carry an element absent from every training fold"),
    ("dft", "superposed_atomic_density_floor_all_42 normalized_mean_absolute_error 21 42 0.154149"),
    ("dft", "superposed_atomic_density_floor_held_out_18 normalized_mean_absolute_error 9 18 0.161438"),
    ("dft", "reduced_salted_floor_all_42 normalized_mean_absolute_error 21 42 0.111713"),
    ("dft", "nearest_structure_copy_context_all_42 normalized_mean_absolute_error 21 42 0.067496"),
    ("dft", "pooled bar 0.015415"),
    ("dft", "bar 0.037238"),
    ("dft", "25 magnetic fold-zero runs"),
    ("dft", "Parameter count: 523,970"),
    ("dft", "cutoff 4.0 angstrom"),
    ("cno", "261 runs across folds one through four train the floors, 76 runs in fold zero"),
    ("cno", "semilocal_ridge_floor mean_absolute_error 29 152 0.097618"),
    ("cno", "per_shell_linear_filter mean_absolute_error 29 152 0.083022"),
    ("cno", "training_mean_trivial_floor mean_absolute_error 29 152 0.015957"),
    ("cno", "nearest_run_copy_floor mean_absolute_error 29 152 0.006164"),
    ("cno", "The 21 axis-stretched grid-shift probe cells"),
    ("cno_spec", "72, 80, 84 all reach at least 18, 20, 21"),
    ("manifold_spec", "into a 128-wide latent"),
    ("don", "Train 608 runs, validation 83, test 88 over 22 orbits"),
    ("don", "Trained point-sampled on 928 runs across every grid shape"),
    ("don", "runs -28.0 to 8.0 eV from the valence-band maximum over 601 points at 0.06 eV"),
    ("don", "Train 1856 runs, validation 256, test 248 over 30 orbits"),
    ("commits", "floor(7200 / 0.137711) = 52283"),
    ("commits", "-169.2%/-147.4% against the required 33.3% improvement"),
    ("commits", "(0.451 s/step) while the member's, run second in a fresh process against an already-warm cache, measured 0.107 s/step"),
    ("commits", "an 18x blowup in the high-frequency band on every split"),
    ("comp", "low band, error along x 0.030861, along z 0.021822, ratio 1.4142"),
    ("comp", "whole field as the low band 0.296828, plain relative L2 0.298005"),
    ("comp", "supplement pair (alpha 0.8 against alpha 1.2): as stored 3.02e-01, best over 48 transforms 6.31e-07"),
    ("comp", "swap pair (alpha 0.8 beta 0.9 against alpha 0.9 beta 0.8): as stored 1.11e-01, best over 48 transforms 3.38e-07"),
    ("comp", "control, different crystals (alpha 0.8 against alpha 0.9): as stored 8.21e-02, best over 48 transforms 8.21e-02"),
    ("comp", "angle-stratum runs 125, distinct crystals 14"),
    ("comp", "fold-0 angle runs 25, with a same-crystal run in folds 1-4: 25, distinct fold-0 crystals 10"),
    ("comp", "holdout_factor_0p8: angle runs held out 61, whose crystal also sits among runs not held out 57"),
    ("comp", "median 1.7e-07, worst 6.9e-07 over 25 runs"),
    ("comp", "control, ridge floor: whole window 0.368, band edges 0.518"),
    ("comp", "nearest-neighbor curve copy: whole window 0.149, band edges 0.171, 30 units, 1856 training runs"),
    ("counts", "strain_atlas_holdout: 296 orbits; train 236 orbits (2112 runs), validation 30 orbits (288 runs), test 30 orbits (280 runs)"),
    ("counts", "paired_fields_fivefold: 207 units, 540 runs, five folds"),
    ("counts", "perovskite_folds: 249 units, one run each; angle 125, length 124"),
    ("counts", "twin_shear_map: 20 shear orbits"),
    ("counts", "store strain_atlas: 2680 archives"),
    ("counts", "store supercell_strains: 200 archives"),
    ("counts", "store defect_set: 196 archives"),
    ("counts", "store perovskite_grid: 250 archives"),
    ("counts", "store alloy_ensemble: 182 archives"),
    ("counts", "store relaxation_pool: 1576 archives"),
    ("counts", "audit round 1: 19 auditors returned 552 findings: S1 22, S2 300, S3 73, S4 87, S5 70"),
    ("counts", "91 findings; total awaiting verification 643"),
    ("a2", "\"E1\": 6,"),
    ("a2", "\"E6\": 73,"),
    ("a2", "\"E8\": 128,"),
    ("a7_manifold", "levels holding no training run: member 0.002381 vs floor 0.000626 on 86 levels, improvement -280.2%"),
    ("a7_manifold", "without the shear arms: member 0.002384 vs floor 0.001057 on 357 levels, improvement -125.4%"),
    ("a7_correction", "blocks: train 608, validation 83, test 88 entries"),
    ("a7_explicit", "explicit: MAE 0.002170 (reported 0.00217)"),
    ("a7_tied", "weight_tied: MAE 0.002966 (reported 0.002966)"),
    ("a7_injected", "weight_tied_injected: MAE 0.002706 (reported 0.002706)"),
    ("a7_matched", "explicit_matched: MAE 0.010043 (reported 0.01004)"),
    ("manifests", "elf_fold0_explicit_35505_stage1 10652 10652 0 False 8400 8.022756274309965e-05"),
    ("manifests", "elf_fold0_explicit_35505_stage2 14201 3100 0 True 1600 8.080974191197281e-05"),
    ("manifests", "canonical_cheap_stage0 6000 6000 0 False 3000 0.00011329452014858058 20260828 0.003"),
    ("manifests", "canonical_cheap_stage1 6000 6000 0 False 5000 6.44957332648725e-05 20260829 0.001"),
    ("manifests", "canonical_cheap_stage2 8000 3700 0 True 2700 2.4646595405405e-05 20260830 0.0003"),
    ("manifests", "energy_trunk_primary_stage0 800 800 0 False 800 0.22474651038646698 20260911 0.002"),
    ("manifests", "energy_trunk_primary_stage1 1200 1200 0 False 1160 0.18020161986351013 20260912 0.0007"),
    ("manifests", "energy_trunk_primary_stage2 5000 5000 0 False 5000 0.14154598116874695 20260913 0.0002"),
    ("phase_a", "it ran 33,170 training steps (plus a 200-step probe) in about 78 minutes"),
    ("phase_a", "Both runs trained 22,090 steps, not 33,650"),
    ("phase_a", "scores the member in-sample on 24 of 27 levels"),
    ("leads", "82 of 196 defect-set runs"),
    ("leads", "exactly two disagree"),
    ("recheck", "median 1.0"),
    ("ladder", "fold 0 (kill block): convergence rate 100.00%, mean iterations 11.0"),
    ("ladder", "MAE 0.015242"),
    ("ladder", "best validation score 0.000791"),
    ("plan", "26 auditors plus the ledger"),
    ("plan", "2.56× *worse*"),
    ("plan", "Charge integrals match electron counts within 2.7e-7"),
    ("plan", "Raw files match the store to 3–6e-8"),
    ("plan", "moves the ridge floor from 0.251% to"),
    ("plan", "0.414%"),
    ("plan", "both tied rungs beat the matched one-layer comparator 3.4–3.7×"),
    ("plan", "26,332 steps in ~5.5 h"),
    ("plan", "stage 0 at 2,800 of 2,828"),
    ("plan", "(best validation 0.2638 at step 1,000"),
    ("plan", "the weight-tied rung 2.0% worse"),
    ("plan", "in-sample on 337 of 423 arm levels"),
    ("plan", "66 of 423 manifold levels"),
]

DERIVED = [
    ("a right angle in degrees", 90.0),
    ("0.8 × 90°", 0.8 * 90),
    ("1.2 × 90°", 1.2 * 90),
    ("improvement 1 − 0.0183 ÷ 0.0423, in percent", (1 - 0.0183 / 0.0423) * 100),
    ("a stage fraction of 0.3, in percent", 30.0),
    ("a stage fraction of 0.4, in percent", 40.0),
    ("the peak rate ÷ 3", 1e-3 / 3),
    ("the peak rate ÷ 9", 1e-3 / 9),
    ("the copy's band-edge score, the unrounded value printed on 2 October", 0.1715),
]

QUIZ_DISTRACTORS = {"43.3", "131", "50"}
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"


def Normalized(text: str) -> str:
    """markdown emphasis and code ticks removed, dashes unified, whitespace collapsed"""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("**", "").replace("`", "")
    text = re.sub(r"[‐‑‒–—−]", "-", text)
    return " ".join(text.split())


NUMBER = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?(?:e[-+]?\d+)?(?![\w])")


def Number_Tokens(text: str) -> list[str]:
    """every number written in a text, commas kept for display"""
    tokens = []
    for match in NUMBER.finditer(text):
        token = match.group(0).rstrip(",")
        after = text[match.end():match.end() + 12]
        if re.match(rf"\s*({MONTHS})", after):
            continue
        tokens.append(token)
    return tokens


def Value(token: str) -> float:
    """a printed number as a float"""
    return float(token.replace(",", ""))


def Printed_Match(token: str, grounded: list[float]) -> bool:
    """a printed number agrees with some grounded value at the precision it is printed to"""
    number = Value(token)
    plain = token.replace(",", "")
    if "e" in plain:
        mantissa = plain.split("e")[0]
        digits = len(mantissa.replace(".", "").lstrip("0"))
        return any(value > 0 and float(f"{value:.{max(digits, 1) - 1}e}") == number for value in grounded)
    if "." in plain:
        decimals = len(plain.split(".")[1])
        return any(abs(round(value, decimals) - number) < 10 ** (-decimals - 3) for value in grounded)
    return any(abs(value - number) < 1e-9 for value in grounded)


def Ground() -> list[float]:
    """every fact's quote found in its source; returns the numbers the verified quotes carry"""
    texts: dict[str, str] = {}
    failures = []
    grounded: list[float] = []
    for key, quote in FACTS:
        if key not in texts:
            texts[key] = Normalized(SOURCES[key].read_text(encoding="utf-8", errors="replace"))
        needle = Normalized(quote)
        if needle not in texts[key]:
            failures.append((key, quote))
            continue
        grounded.extend(Value(token) for token in Number_Tokens(needle))
    grounded.extend(value for _, value in DERIVED)
    if failures:
        print(f"GROUNDING FAILED for {len(failures)} of {len(FACTS)} facts:")
        for key, quote in failures:
            print(f"  [{key}] {quote}")
        sys.exit(1)
    print(f"grounding: {len(FACTS)} of {len(FACTS)} quotes found verbatim in their sources; {len(grounded)} grounded numbers")
    return grounded


class TextCollector(HTMLParser):
    """visible text of a page, minus scripts, styles, dates and anything marked data-nofact"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.stack: list[bool] = []
        self.chunks: list[str] = []
        self.voids = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr",
                      "circle", "line", "rect", "path", "polygon", "polyline", "stop", "use"}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        names = {name for name, _ in attrs}
        skipping = tag in ("script", "style", "time") or "data-nofact" in names
        if tag in self.voids:
            return
        self.stack.append(skipping)
        if skipping:
            self.skip_depth += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        return

    def handle_endtag(self, tag: str) -> None:
        if tag in self.voids or not self.stack:
            return
        if self.stack.pop():
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.skip_depth == 0:
            self.chunks.append(data)


def Check_Expand(match: re.Match[str]) -> str:
    """one compact check block written out in full"""
    part = match.group(1)
    body = match.group(2)
    question = re.search(r"<q>(.*?)</q>", body, re.S).group(1).strip()
    answer = re.search(r"<a>(.*?)</a>", body, re.S).group(1).strip()
    source = re.search(r"<src>(.*?)</src>", body, re.S).group(1).strip()
    return (f'<div class="check" data-part="{part}">\n'
            f'<p class="check-label" data-nofact>Check</p>\n'
            f'<p class="q">{question}</p>\n'
            f'<textarea aria-label="Your answer" placeholder="Your answer (optional)" rows="2"></textarea>\n'
            f'<div class="row"><button type="button" class="reveal" aria-expanded="false">Show answer</button></div>\n'
            f'<div class="answer" hidden>\n<p>{answer}</p>\n<p class="src" data-nofact>Source: {source}</p>\n'
            f'<div class="row" role="group" aria-label="How well did you know it?"><span class="rate-label">How well did you know it?</span>'
            f'<button type="button" data-rate="2" aria-pressed="false">Knew it</button>'
            f'<button type="button" data-rate="1" aria-pressed="false">Partly</button>'
            f'<button type="button" data-rate="0" aria-pressed="false">Didn\'t know</button></div>\n'
            f'</div>\n</div>')


def Pipeline_Svg() -> str:
    """the eight stages from a run to a verdict"""
    stages = [("VASP run", "files on /Pool"), ("Census row", "one per run"), ("Store archive", "fields ÷ volume"),
              ("Split file", "units into folds"), ("Floors and bars", "before training"), ("Training", "staged, saved"),
              ("Scoring", "unit medians"), ("Verdict", "pass or kill")]
    width, box, gap, top, height = 1000, 106, 18, 22, 66
    left = (width - (len(stages) * box + (len(stages) - 1) * gap)) / 2
    parts = [f'<svg viewBox="0 0 {width} 112" role="img" aria-label="Eight stages from a VASP run to a verdict: run, census row, store archive, split file, floors and bars fixed before training, training, scoring by unit medians, verdict.">',
             '<defs><marker id="arrow-pipe" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="s-muted"/></marker></defs>']
    for number, (title, sub) in enumerate(stages):
        x = left + number * (box + gap)
        fill = "s-soft" if title == "Floors and bars" else "s-sheet"
        stroke = "k-accent" if title in ("Floors and bars", "Verdict") else "k-rule"
        parts.append(f'<rect x="{x:.1f}" y="{top}" width="{box}" height="{height}" rx="5" class="{fill} {stroke}" stroke-width="1.5"/>')
        parts.append(f'<text x="{x + box / 2:.1f}" y="{top + 29}" text-anchor="middle" font-size="13" font-weight="600" class="s-ink">{html.escape(title)}</text>')
        parts.append(f'<text x="{x + box / 2:.1f}" y="{top + 48}" text-anchor="middle" font-size="11.5" class="s-muted">{html.escape(sub)}</text>')
        if number < len(stages) - 1:
            parts.append(f'<line x1="{x + box + 2:.1f}" y1="{top + height / 2}" x2="{x + box + gap - 3:.1f}" y2="{top + height / 2}" class="k-muted" stroke-width="1.5" marker-end="url(#arrow-pipe)"/>')
    parts.append(f'<text x="{left:.1f}" y="106" font-size="11" class="s-muted">the shaded stage is fixed before any training step runs</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def Folds_Svg() -> str:
    """fold roles on the cubic block, for the model and for the floors"""
    columns, label_width, cell, gap, top = 5, 120, 112, 8, 34
    parts = ['<svg viewBox="0 0 740 196" role="img" aria-label="Fold roles: the model trains on folds 2 to 4, stops by fold 1 and is judged on fold 0; the floors fit on folds 1 to 4 and are judged on fold 0.">']
    for fold in range(columns):
        x = label_width + fold * (cell + gap)
        parts.append(f'<text x="{x + cell / 2}" y="22" text-anchor="middle" font-size="12.5" font-weight="600" class="s-ink">fold {fold}</text>')
    rows = [("the model", ["judged", "decides when to stop", "trains", "trains", "trains"]),
            ("the floors", ["judged", "fitted", "fitted", "fitted", "fitted"])]
    for row_number, (label, roles) in enumerate(rows):
        y = top + row_number * 52
        parts.append(f'<text x="0" y="{y + 26}" font-size="12.5" class="s-muted">{label}</text>')
        for fold, role in enumerate(roles):
            x = label_width + fold * (cell + gap)
            fill = "s-sheet" if role == "judged" else ("s-hold" if role.startswith("decides") else "s-soft")
            stroke = "k-accent" if role == "judged" else "k-rule"
            weight = "600" if role == "judged" else "400"
            parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="40" rx="4" class="{fill} {stroke}" stroke-width="{2 if role == "judged" else 1}"/>')
            parts.append(f'<text x="{x + cell / 2}" y="{y + 25}" text-anchor="middle" font-size="11.5" font-weight="{weight}" class="s-ink">{role}</text>')
    counts_y = top + 2 * 52 + 22
    parts.append(f'<text x="{label_width + cell / 2}" y="{counts_y}" text-anchor="middle" font-size="11.5" class="s-muted">76 runs · 29 units</text>')
    parts.append(f'<text x="{label_width + (cell + gap) + cell / 2}" y="{counts_y}" text-anchor="middle" font-size="11.5" class="s-muted">65 runs · 24 units</text>')
    span_left = label_width + 2 * (cell + gap)
    span_right = label_width + 4 * (cell + gap) + cell
    parts.append(f'<line x1="{span_left}" y1="{counts_y - 14}" x2="{span_right}" y2="{counts_y - 14}" class="k-rule" stroke-width="1"/>')
    parts.append(f'<text x="{(span_left + span_right) / 2}" y="{counts_y}" text-anchor="middle" font-size="11.5" class="s-muted">196 runs</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def Cells_Svg() -> str:
    """one two-dimensional lattice outlined by a 72-degree cell and by its edge-reversed 108-degree twin"""
    spacing = 64.0
    angle = math.radians(72)
    first = (spacing, 0.0)
    second = (spacing * math.cos(angle), -spacing * math.sin(angle))
    origin = (96.0, 214.0)
    points = []
    for column in range(-2, 9):
        for row in range(-1, 4):
            x = origin[0] + column * first[0] + row * second[0]
            y = origin[1] + column * first[1] + row * second[1]
            if 20 <= x <= 620 and 20 <= y <= 240:
                points.append((x, y))
    parts = ['<svg viewBox="0 0 640 262" role="img" aria-label="The same lattice of points outlined by two cells: one with a 72 degree angle, and the same cell with its second edge reversed, which has a 108 degree angle.">']
    for x, y in points:
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" class="s-muted"/>')

    def Cell(corner: tuple[float, float], along: tuple[float, float], across: tuple[float, float], css: str, dash: str) -> None:
        corners = [corner, (corner[0] + along[0], corner[1] + along[1]),
                   (corner[0] + along[0] + across[0], corner[1] + along[1] + across[1]), (corner[0] + across[0], corner[1] + across[1])]
        path = " ".join(f"{x:.1f},{y:.1f}" for x, y in corners)
        parts.append(f'<polygon points="{path}" class="s-none {css}" stroke-width="2.4"{dash}/>')

    acute_corner = (origin[0] + 1 * first[0], origin[1])
    Cell(acute_corner, first, second, "k-accent", "")
    obtuse_corner = (origin[0] + 5 * first[0] + 2 * second[0], origin[1] + 2 * second[1])
    reversed_second = (-second[0], -second[1])
    Cell(obtuse_corner, first, reversed_second, "k-ink", ' stroke-dasharray="6 4"')
    radius = 20.0
    arc_end = (acute_corner[0] + radius * math.cos(angle), acute_corner[1] - radius * math.sin(angle))
    parts.append(f'<path d="M{acute_corner[0] + radius:.1f},{acute_corner[1]:.1f} A{radius},{radius} 0 0 0 {arc_end[0]:.1f},{arc_end[1]:.1f}" class="s-none k-accent" stroke-width="1.6"/>')
    parts.append(f'<text x="{acute_corner[0] + 24:.1f}" y="{acute_corner[1] - 8:.1f}" font-size="13" font-weight="600" class="s-accent">72°</text>')
    obtuse_angle = math.radians(-108)
    arc_end = (obtuse_corner[0] + radius * math.cos(obtuse_angle), obtuse_corner[1] - radius * math.sin(obtuse_angle))
    parts.append(f'<path d="M{obtuse_corner[0] + radius:.1f},{obtuse_corner[1]:.1f} A{radius},{radius} 0 0 1 {arc_end[0]:.1f},{arc_end[1]:.1f}" class="s-none k-ink" stroke-width="1.6"/>')
    parts.append(f'<text x="{obtuse_corner[0] + 18:.1f}" y="{obtuse_corner[1] + 26:.1f}" font-size="13" font-weight="600" class="s-ink">108°</text>')
    parts.append('<text x="16" y="254" font-size="12" class="s-muted">solid: a cell with a 72° angle · dashed: the same lattice, second edge reversed, a 108° cell</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def Schedule_Svg() -> str:
    """the probe and three stages, widths by share of the budget, heights by learning rate on a log scale"""
    left, right, base = 64.0, 720.0, 200.0
    probe_width = 44.0
    span = right - left - probe_width
    rates = [1e-3, 1e-3 / 3, 1e-3 / 9]
    shares = [0.3, 0.3, 0.4]

    def Height(rate: float) -> float:
        return 60.0 + (math.log10(1e-3) - math.log10(rate)) * 100.0

    parts = ['<svg viewBox="0 0 760 246" role="img" aria-label="The staged schedule: a probe of up to 200 steps, then stages at the peak rate, a third of it and a ninth of it over 30, 30 and 40 percent of the budget; only the last stage stops early, and the function returns the last stage\'s best.">']
    parts.append(f'<line x1="{left}" y1="{base}" x2="{right + 8}" y2="{base}" class="k-muted" stroke-width="1.2"/>')
    parts.append(f'<text x="{right + 8}" y="{base + 18}" text-anchor="end" font-size="11.5" class="s-muted">steps →</text>')
    parts.append(f'<text x="{left - 8}" y="{Height(1e-3) + 4}" text-anchor="end" font-size="11" class="s-muted">1e-3</text>')
    parts.append(f'<text x="{left - 8}" y="{Height(1e-3 / 3) + 4}" text-anchor="end" font-size="11" class="s-muted">3.3e-4</text>')
    parts.append(f'<text x="{left - 8}" y="{Height(1e-3 / 9) + 4}" text-anchor="end" font-size="11" class="s-muted">1.1e-4</text>')
    parts.append(f'<rect x="{left}" y="{Height(1e-3)}" width="{probe_width - 4}" height="{base - Height(1e-3)}" class="s-hold k-rule" stroke-width="1"/>')
    parts.append(f'<text x="{left + (probe_width - 4) / 2}" y="{Height(1e-3) - 8}" text-anchor="middle" font-size="11" class="s-ink">probe</text>')
    x = left + probe_width
    labels = ["stage 0 · 30%", "stage 1 · 30%", "stage 2 · 40%"]
    for number, (rate, share) in enumerate(zip(rates, shares)):
        width = span * share
        top = Height(rate)
        parts.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{width - 4:.1f}" height="{base - top:.1f}" class="s-soft k-accent" stroke-width="1.2"/>')
        parts.append(f'<text x="{x + (width - 4) / 2:.1f}" y="{top - 8:.1f}" text-anchor="middle" font-size="12" font-weight="600" class="s-ink">{labels[number]}</text>')
        if number == 2:
            parts.append(f'<text x="{x + (width - 4) / 2:.1f}" y="{base - 14:.1f}" text-anchor="middle" font-size="11" class="s-ink">stops after 15 passes without gain</text>')
            parts.append(f'<text x="{x + width - 6:.1f}" y="{base + 34:.1f}" text-anchor="end" font-size="11.5" font-weight="600" class="s-accent">returns this stage\'s best only</text>')
        x += width
    parts.append(f'<text x="{left}" y="{base + 34}" font-size="11" class="s-muted">up to 200 steps; rerun at 0.3 × the rate if the loss blows up</text>')
    parts.append(f'<text x="8" y="16" font-size="11" class="s-muted">learning rate, log scale</text>')
    parts.append("</svg>")
    return "\n".join(parts)


ROWS = [
    ("Flagship, explicit stack", 0.00217, 0.0976, 0.0062),
    ("Ladder: weight-tied, injected", 0.00271, 0.0976, 0.0062),
    ("Ladder: one explicit layer", 0.01004, 0.0976, 0.0062),
    ("Branch–trunk, strain", 0.000821, 0.00414, 0.00414),
    ("Branch–trunk, perovskite", 0.0183, 0.0423, 1.7e-7),
    ("Energy trunk", 0.206, 0.368, 0.149),
    ("Two-input network", 0.016454, 0.097618, 0.006164),
    ("Manifold decoder", 0.002452, 0.000911, 0.000911),
    ("Galerkin transformer", 0.1780, 0.0853, 1.7e-7),
    ("Correction network", 0.002079, 0.011131, None),
]


def Power_Label(ratio: float) -> str:
    """a ratio rounded to the nearest power of ten, written with a superscript exponent"""
    superscripts = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
    return "10" + str(round(math.log10(ratio))).translate(superscripts)


def Scoreboard_Svg() -> str:
    """a dumbbell per model: its error over the plan's floor (open) and over the strongest simple method (filled), log scale"""
    plot_left, plot_right, top, row_height = 250.0, 880.0, 54.0, 30.0
    lowest, highest = -2.0, 3.0

    def X(ratio: float) -> float:
        return plot_left + (math.log10(ratio) - lowest) / (highest - lowest) * (plot_right - plot_left)

    height = top + len(ROWS) * row_height + 24
    parts = [f'<svg viewBox="0 0 960 {height:.0f}" role="img" aria-label="For each judged model, its error divided by the plan\'s floor (open circle) and by the strongest simple method known now (filled circle), on a log scale where values left of 1 mean the model wins. The table below lists every number.">']
    parts.append('<g data-nofact>')
    for exponent in range(int(lowest), int(highest) + 1):
        x = X(10.0 ** exponent)
        label = {-2: "0.01", -1: "0.1", 0: "1", 1: "10", 2: "100", 3: "1000"}[exponent]
        parts.append(f'<line x1="{x:.1f}" y1="{top - 14}" x2="{x:.1f}" y2="{height - 22}" class="k-rule" stroke-width="{1.6 if exponent == 0 else 1}"/>')
        parts.append(f'<text x="{x:.1f}" y="{top - 20}" text-anchor="middle" font-size="11" class="s-muted">{label}×</text>')
    parts.append(f'<text x="{X(1.0) - 8:.1f}" y="{height - 6}" text-anchor="end" font-size="11" class="s-muted">← the model is better</text>')
    parts.append(f'<text x="{X(1.0) + 8:.1f}" y="{height - 6}" font-size="11" class="s-muted">the floor is better →</text>')
    parts.append('</g>')
    parts.append(f'<circle cx="{plot_left + 6}" cy="12" r="5" class="s-sheet k-muted" stroke-width="1.8"/><text x="{plot_left + 16}" y="16" font-size="11.5" class="s-ink">against the plan\'s floor</text>')
    parts.append(f'<circle cx="{plot_left + 200}" cy="12" r="5" class="s-accent"/><text x="{plot_left + 210}" y="16" font-size="11.5" class="s-ink">against the strongest simple method known now</text>')
    for number, (name, member, plan_floor, strongest) in enumerate(ROWS):
        y = top + number * row_height + row_height / 2
        parts.append(f'<text x="0" y="{y + 4:.1f}" font-size="12" class="s-ink">{html.escape(name)}</text>')
        plan_ratio = member / plan_floor
        strong_ratio = 406.0 if strongest is None else member / strongest
        plan_x = X(plan_ratio)
        off_scale = strong_ratio > 10.0 ** highest
        strong_x = plot_right + 18 if off_scale else X(strong_ratio)
        parts.append(f'<line x1="{plan_x:.1f}" y1="{y:.1f}" x2="{strong_x:.1f}" y2="{y:.1f}" class="k-muted" stroke-width="1.4"/>')
        parts.append(f'<circle cx="{plan_x:.1f}" cy="{y:.1f}" r="5.5" class="s-sheet k-muted" stroke-width="1.8"><title data-nofact>{html.escape(name)}: {plan_ratio:.2g} times the plan\'s floor</title></circle>')
        if off_scale:
            parts.append(f'<polygon points="{strong_x - 6:.1f},{y - 6:.1f} {strong_x + 6:.1f},{y:.1f} {strong_x - 6:.1f},{y + 6:.1f}" class="s-accent"><title data-nofact>{html.escape(name)}: about {Power_Label(strong_ratio)} times a symmetry-aware copy</title></polygon>')
        else:
            parts.append(f'<circle cx="{strong_x:.1f}" cy="{y:.1f}" r="5.5" class="s-accent"><title data-nofact>{html.escape(name)}: {strong_ratio:.2g} times the strongest simple method</title></circle>')
        label = f"≈{Power_Label(strong_ratio)}×" if off_scale else (f"{strong_ratio:.2g}×" if strong_ratio < 100 else f"{strong_ratio:.0f}×")
        parts.append(f'<text x="{strong_x + 12:.1f}" y="{y + 4:.1f}" font-size="11" class="s-muted" data-nofact>{html.escape(label)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def Image(name: str, alt: str) -> str:
    """a committed repository figure embedded as a data URI"""
    path = BASE / "operators/factorized_fourier/figures/fold_0/explicit" / f"{name}.png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f'<img src="data:image/png;base64,{encoded}" alt="{html.escape(alt)}" loading="lazy" width="1660" height="504">'


def Assemble() -> str:
    """the parts in order, checks expanded, drawings and images in place"""
    order = ["00-head.html", "10-header.html", "21-part1.html", "22-part2.html", "23-part3.html", "24-part4.html",
             "25-part5.html", "26-part6.html", "27-part7.html", "28-part8.html", "29-quiz-map.html", "90-script.html"]
    text = "\n".join((PAGE / name).read_text(encoding="utf-8") for name in order)
    text = re.sub(r'<check part="(\d)">(.*?)</check>', Check_Expand, text, flags=re.S)
    replacements = {
        "<!--PIPELINE-->": Pipeline_Svg(), "<!--FOLDS-->": Folds_Svg(), "<!--CELLS-->": Cells_Svg(),
        "<!--SCHEDULE-->": Schedule_Svg(), "<!--SCOREBOARD-->": Scoreboard_Svg(),
        "<!--IMG:flagship_best-->": Image("prediction_best", "The flagship's best fold-0 run: truth, prediction and their difference for one slice of the spin-up localization field; the prediction matches the truth closely."),
        "<!--IMG:flagship_worst-->": Image("prediction_worst", "The flagship's worst fold-0 run: the truth shows a bright localization feature at a dopant site in the center, which the prediction misses."),
    }
    for marker, content in replacements.items():
        if marker not in text:
            sys.exit(f"missing marker {marker}")
        text = text.replace(marker, content)
    leftover = re.findall(r"<!--[A-Z:_a-z]+-->|<check |</check>", text)
    if leftover:
        sys.exit(f"unexpanded markers: {leftover}")
    return text


def Check_Numbers(page: str, grounded: list[float]) -> None:
    """every number a reader sees must agree with a grounded fact at its printed precision"""
    collector = TextCollector()
    collector.feed(page)
    visible = Normalized(" ".join(collector.chunks))
    script = re.search(r"var QUIZ = \[(.*?)\];", page, re.S).group(1)
    quiz_text = Normalized(re.sub(r'"(part|q|options|answer|why)":?', " ", script))
    unsourced = []
    for origin, text in (("page", visible), ("quiz", quiz_text)):
        for token in Number_Tokens(text):
            plain = token.replace(",", "")
            if "." not in plain and "e" not in plain and Value(token) <= 10:
                continue
            if Value(token) == 2026:
                continue
            if origin == "quiz" and plain in QUIZ_DISTRACTORS:
                continue
            if not Printed_Match(token, grounded):
                unsourced.append((origin, token))
    if unsourced:
        print(f"UNSOURCED NUMBERS: {len(unsourced)}")
        for origin, token in unsourced:
            position = (visible if origin == "page" else quiz_text).find(token)
            context = (visible if origin == "page" else quiz_text)[max(0, position - 60):position + 40]
            print(f"  [{origin}] {token}  …{context}…")
        sys.exit(1)
    print(f"numbers: every number on the page and in the quiz agrees with a grounded fact")


def Calibrate(grounded: list[float]) -> None:
    """the checker must flag a planted wrong number and a planted wrong quote, and pass an en dash and a superscript"""
    if Printed_Match("0.00218", grounded):
        sys.exit("calibration failed: a planted wrong number was accepted")
    if not Printed_Match("0.00217", grounded) or not Printed_Match("8.1e-5", grounded):
        sys.exit("calibration failed: a true number was refused")
    text = Normalized(SOURCES["results"].read_text(encoding="utf-8"))
    if Normalized("ridge floor (parameters → mode coefficients); kill: beat by 30%") in text:
        sys.exit("calibration failed: a planted wrong quote was found")
    if Normalized("14–35%") not in text or Normalized("40³ block") not in text:
        sys.exit("calibration failed: an en dash or a superscript did not match")
    print("calibration: a planted wrong number and a planted wrong quote were refused; an en dash and a superscript matched")


def Check_Egress(page: str) -> None:
    """no pseudopotential header text and no oversized embedded payload"""
    for pattern in ("TITEL", "PAW_PBE", "PAW_GGA", "US ", "VRHFIN", "LEXCH"):
        if pattern in page and pattern != "US ":
            sys.exit(f"egress: found {pattern}")
    images = re.findall(r"data:image/png;base64,([A-Za-z0-9+/=]+)", page)
    print(f"egress: no pseudopotential text; {len(images)} embedded figures, page {len(page.encode('utf-8')) / 1024:.0f} KB")


if __name__ == "__main__":
    grounded = Ground()
    Calibrate(grounded)
    page = Assemble()
    Check_Numbers(page, grounded)
    Check_Egress(page)
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT}")
