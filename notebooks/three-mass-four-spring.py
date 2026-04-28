# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python 3
#     name: python3
# ---

# %% [markdown]
# # `compose-physics` — full surface tour and validation
#
# This notebook is both the **tour** of the rewrite and its **validation
# witness**. It exercises every layer of the tool against a 3-mass /
# 4-spring 1D chain:
#
# ```
#   wall - k - m - k - m - k - m - k - wall
#             x1      x2      x3
# ```
#
# The contract being checked, layer by layer:
#
# 1. The IR is a funcallable tree of primitives — every node is directly
#    evaluable from Lisp, and there is **no symbolic algebra** anywhere.
# 2. The vocabulary is a closed table of named forward/inverse function
#    pairs — no user-extensible plug-ins, no embedded foreign callables.
# 3. A problem is a slot map plus a list of single-state residual rows
#    plus a list of per-slot update rows. Updates default to identity.
# 4. The simplifier rewrites trees structurally; the solver inverts
#    residuals symbolically by linear rearrangement and `apply` inversion,
#    and **fails loudly** when the residual is not analytically tractable.
# 5. The canonicalizer + content-hash makes problem identity reproducible.
# 6. The emitter chunks the IR into one C file per group of rows,
#    individually addressable, behind a single dispatch translation unit.
# 7. The CLI registers a problem into a content-addressed directory,
#    builds the shared library, and writes a manifest.
# 8. The compiled `.so` exposes `compute_residual`, `compute_update`,
#    `get_n`, `get_k` — and nothing else.
#
# After the tour, four numerical invariants are verified:
#
# - eigenmode frequencies match the analytic spectrum,
# - `compute_residual` is identically zero along the trajectory,
# - the Lisp-evaluated update is **bit-identical** to the compiled C
#   update,
# - total energy is conserved within the symplectic-Euler band.

# %% [markdown]
# ## Setup
#
# Resolve paths. The project is now `n-Op/compose-physics/`; this
# notebook lives in `n-Op/notebooks/` as a sibling.

# %%
import os, sys, ctypes, subprocess, shutil, math, tempfile, textwrap, hashlib
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

NOTEBOOK_DIR = Path.cwd().resolve()
while NOTEBOOK_DIR.name != 'notebooks' and NOTEBOOK_DIR.parent != NOTEBOOK_DIR:
    NOTEBOOK_DIR = NOTEBOOK_DIR.parent
N_OP_ROOT = NOTEBOOK_DIR.parent
COMPOSE_PHYSICS_ROOT = N_OP_ROOT / 'compose-physics'
assert (COMPOSE_PHYSICS_ROOT / 'compose-physics.asd').is_file(), COMPOSE_PHYSICS_ROOT
sys.path.insert(0, str(COMPOSE_PHYSICS_ROOT))

PROBLEM_LISP = NOTEBOOK_DIR / 'three-mass-four-spring.lisp'
REGISTRY_ROOT = Path('/tmp/compose-physics-validation')

print('n-Op root          :', N_OP_ROOT)
print('compose-physics    :', COMPOSE_PHYSICS_ROOT)
print('problem source     :', PROBLEM_LISP)
print('registry root (tmp):', REGISTRY_ROOT)


# %% [markdown]
# ### `run_lisp` — drive SBCL from Python
#
# Most of the tour pokes at Lisp-side objects (the IR, the vocabulary,
# the simplifier, the solver, the canonicalizer). To avoid hand-rolled
# REPL transcripts, the helper below loads `compose-physics`, evaluates
# the requested form, and returns the captured stdout. The Lisp side
# does the printing — Python just displays it.

# %%
def run_lisp(form_text: str, *, also_load_problem: bool = False) -> str:
    # The library has load-time self-tests that share a /tmp directory keyed
    # by (get-universal-time); back-to-back SBCL invocations within the same
    # second collide. Sweep the slate before every call.
    subprocess.run('rm -rf /tmp/cp-index-self-check-*', shell=True, check=False)
    preamble = textwrap.dedent(f'''\
        (require :asdf)
        (push #p"{COMPOSE_PHYSICS_ROOT}/" asdf:*central-registry*)
        (let ((*standard-output* (make-broadcast-stream)))
          (asdf:load-system :compose-physics))
        (setf *read-default-float-format* (quote double-float))
    ''')
    if also_load_problem:
        preamble += f'(let ((*standard-output* (make-broadcast-stream))) (load #p"{PROBLEM_LISP}"))\n'
    with tempfile.NamedTemporaryFile('w', suffix='.lisp', delete=False) as handle:
        handle.write(preamble)
        handle.write(form_text)
        script_path = handle.name
    try:
        completed = subprocess.run(
            ['sbcl', '--non-interactive', '--load', script_path],
            capture_output=True, text=True)
    finally:
        os.unlink(script_path)
    if completed.returncode != 0:
        raise RuntimeError('SBCL failed:\n' + completed.stderr)
    return completed.stdout.rstrip()


def show(label: str, body: str) -> None:
    bar = '─' * max(len(label), 8)
    print(f'┌{bar}─┐\n│ {label} │\n└{bar}─┘')
    print(body)
    print()


# %% [markdown]
# ## 1 — The IR is a funcallable tree of primitives
#
# Five node kinds: `term`, `sum`, `product`, `scale`, `apply`. Every
# instance is a `funcallable-instance`; calling it with a state vector
# evaluates the subtree and returns a `double-float`. There is no
# separate "evaluator" — the tree *is* the evaluator. This is the
# load-bearing invariant: there is no way to construct a node that
# isn't directly callable.

# %%
show('IR primitives — construct, inspect, funcall',
     run_lisp(r'''
        (in-package :compose-physics)
        (let* ((mass     (term 1.0d0 0 :name "m"))
               (velocity (term 1.0d0 1 :name "v"))
               (squared  (product velocity velocity))
               (scaled   (scale 0.5d0 (product mass squared)))
               (kinetic  (sum scaled (term 0.0d0 2 :name "_unused"))))
          (format t "term        --> ~A~%" mass)
          (format t "product     --> ~A~%" squared)
          (format t "scale       --> ~A~%" scaled)
          (format t "sum         --> ~A~%~%" kinetic)
          (let ((state (make-array 3 :element-type 'double-float
                                     :initial-contents '(2.0d0 3.0d0 0.0d0))))
            (format t "funcall (mass)              = ~F~%" (funcall mass     state))
            (format t "funcall (v*v)               = ~F~%" (funcall squared  state))
            (format t "funcall (0.5*m*v^2)         = ~F~%" (funcall scaled   state))
            (format t "funcall (kinetic energy)    = ~F~%" (funcall kinetic  state))))
     '''))


# %% [markdown]
# `apply` is the fifth node kind. It looks up a named entry in the
# vocabulary, calls its forward function on the child's value, and
# returns a `double-float`. The point: **the tree carries the name**;
# the numerical implementation is decoupled from the IR. That's how
# the C emitter can map the same node onto a `<math.h>` call, and how
# the solver can find the *inverse* of `:exp` later.

# %%
show('apply node — named vocabulary call, funcalled in Lisp',
     run_lisp(r'''
        (in-package :compose-physics)
        (let* ((x        (term 1.0d0 0 :name "x"))
               (exp-of-x (apply :exp x)))
          (format t "node           --> ~A~%" exp-of-x)
          (format t "vocabulary key --> ~A~%" (apply-name exp-of-x))
          (let ((state (make-array 1 :element-type 'double-float :initial-contents '(1.5d0))))
            (format t "funcall (exp(1.5)) = ~F   (cl:exp = ~F)~%"
                    (funcall exp-of-x state)
                    (cl:exp 1.5d0))))
     '''))


# %% [markdown]
# ## 2 — Vocabulary is a closed, named table
#
# `register-function` adds an entry; `lookup-function-record` reads it
# back. Each record carries: forward function, inverse key (or `nil`),
# and a C emission identifier. Inversions are *symbolic relationships*
# between named entries — there is no symbolic algebra, just a table.

# %%
show('standard vocabulary entries',
     run_lisp(r'''
        (in-package :compose-physics)
        (dolist (key (sort (copy-list (vocabulary-keys)) #'string<
                           :key (lambda (k) (string-downcase (symbol-name k)))))
          (let ((rec (lookup-function-record key)))
            (format t "  ~12A  c=~A   inverse=~A~%"
                    key
                    (function-record-emission-identifier rec)
                    (function-record-inverse-key rec))))
     '''))

# %%
show('forward + inverse round-trip on :exp / :log',
     run_lisp(r'''
        (in-package :compose-physics)
        (let* ((forward (lookup-forward-function :exp))
               (inverse (lookup-inverse-function :exp))
               (x       2.5d0))
          (format t "exp(2.5)         = ~F~%" (funcall forward x))
          (format t "log(exp(2.5))    = ~F~%" (funcall inverse (funcall forward x)))
          (format t "inverse key of :exp = ~A~%" (lookup-inverse-key :exp)))
     '''))


# %% [markdown]
# ## 3 — Problem authoring
#
# A problem is a slot map (ordered list of slot names → indices) plus a
# list of residual rows (`name`, `expression`) and a list of update rows
# (`slot-name`, `slot-index`, `expression`, `explicit-p`). Slots that
# the user does not provide an update for default to **identity**:
# `slot[t+1] = slot[t]`. There are no useless parameters; consumer-side
# wrappers handle convenience.
#
# The reference problem source:

# %%
print(PROBLEM_LISP.read_text())


# %% [markdown]
# Loading it from Lisp populates `cl-user::*problem*`. The next cell
# loads it and introspects the resulting `problem` object.

# %%
show('introspect the loaded *problem*',
     run_lisp(r'''
        (in-package :compose-physics)
        (let* ((p (symbol-value (find-symbol "*PROBLEM*" :common-lisp-user))))
          (format t "name              : ~A~%" (problem-name p))
          (format t "slot-count        : ~D~%" (problem-slot-count p))
          (format t "residual-count    : ~D~%" (problem-residual-count p))
          (format t "slot-names        : ~A~%" (coerce (problem-slot-names p) 'list))
          (format t "~%residual rows:~%")
          (loop for row across (problem-residual-rows p) do
                (format t "  ~A~%" (residual-row-name row)))
          (format t "~%update rows (explicit only):~%")
          (loop for row across (problem-update-rows p)
                when (update-row-explicit-p row) do
                (format t "  slot[~D]=~A := <expression-tree>~%"
                        (update-row-slot-index row)
                        (update-row-slot-name row)))
          (format t "~%update rows (implicit-identity):~%")
          (loop for row across (problem-update-rows p)
                unless (update-row-explicit-p row) do
                (format t "  slot[~D]=~A := identity~%"
                        (update-row-slot-index row)
                        (update-row-slot-name row))))
     ''', also_load_problem=True))


# %% [markdown]
# ## 4 — Simplification is structural, never symbolic
#
# `simplify-expression` flattens nested `sum`/`product` chains, folds
# numeric scale factors, and drops zero terms. It does **not** distribute,
# does not cancel, does not factor — those would require symbolic
# algebra. The simplifier is purely a tree-shape rewrite.

# %%
show('before / after simplify',
     run_lisp(r'''
        (in-package :compose-physics)
        (let* ((x (term 1.0d0 0 :name "x"))
               (y (term 1.0d0 1 :name "y"))
               (raw (sum (scale 1.0d0 x)
                         (scale 0.0d0 y)
                         (sum x y)
                         (scale 2.0d0 (scale 3.0d0 x)))))
          (format t "raw       :~%")
          (format t "  ~S~%" (canonicalize-expression raw))
          (format t "simplified:~%")
          (format t "  ~S~%" (canonicalize-expression (simplify-expression raw))))
     '''))


# %% [markdown]
# ## 5 — `solve-for` rearranges residuals analytically
#
# Given a residual `R(state) = 0` and a target slot `s`, `solve-for`
# returns an expression for `s` in terms of the other slots. The
# strategy is closed-form and discrete: it walks the tree, performs
# linear rearrangement around `+`/`-`/scalar-`*`, and inverts `apply`
# nodes by looking up the registered inverse. It is **not** a CAS: if
# the residual is non-linear in the target, or if no registered inverse
# exists, it raises a structured `solve-failure`.

# %%
show('solve-for — linear rearrangement (residual: m*a - k*x = 0, target a)',
     run_lisp(r'''
        (in-package :compose-physics)
        (let* ((x (term 1.0d0 0 :name "x"))
               (a (term 1.0d0 1 :name "a"))
               (m (term 1.0d0 2 :name "m"))
               (k (term 1.0d0 3 :name "k"))
               (residual (sum (product m a) (scale -1.0d0 (product k x))))
               (solved   (solve-for residual 1 "a" "newton")))
          (format t "residual : ~S~%" (canonicalize-expression residual))
          (format t "solved   : ~S~%" (canonicalize-expression solved))
          (format t "~%verify by funcall on a sample state:~%")
          (let ((state (make-array 4 :element-type 'double-float
                                     :initial-contents '(0.7d0 0.0d0 2.0d0 5.0d0))))
            (format t "  k*x/m = ~F~%" (funcall solved state))
            (format t "  hand  = ~F~%" (/ (* 5.0d0 0.7d0) 2.0d0))))
     '''))

# %%
show('solve-for — apply inversion (residual: exp(x) - y = 0, target x)',
     run_lisp(r'''
        (in-package :compose-physics)
        (let* ((x (term 1.0d0 0 :name "x"))
               (y (term 1.0d0 1 :name "y"))
               (residual (sum (apply :exp x) (scale -1.0d0 y)))
               (solved   (solve-for residual 0 "x" "exp-eq")))
          (format t "residual : ~S~%" (canonicalize-expression residual))
          (format t "solved   : ~S~%" (canonicalize-expression solved))
          (let ((state (make-array 2 :element-type 'double-float
                                     :initial-contents '(0.0d0 7.389056099d0))))
            (format t "  log(7.389...) = ~F   (~A)~%"
                    (funcall solved state) "should be ~2.0")))
     '''))

# %%
show('solve-for — failure path is loud and structured',
     run_lisp(r'''
        (in-package :compose-physics)
        (let* ((x (term 1.0d0 0 :name "x"))
               (residual (product x x)))
          (handler-case (solve-for residual 0 "x" "x-squared")
            (solve-failure (err)
              (format t "caught ~A~%" (type-of err))
              (format t "  reason : ~A~%" (solve-failure-reason err))
              (format t "  target : ~A~%" (solve-failure-target-slot-name err)))))
     '''))


# %% [markdown]
# ## 6 — Canonical sexp + content hash
#
# Two problems with the same algebraic content must produce the same
# canonical sexp and the same content hash, regardless of how the user
# typed them. A trivially perturbed problem must produce a different
# hash.

# %%
show('canonical sexp of the loaded *problem* (head)',
     run_lisp(r'''
        (in-package :compose-physics)
        (let* ((p (symbol-value (find-symbol "*PROBLEM*" :common-lisp-user)))
               (text (canonical-sexp-string (canonicalize-problem p))))
          (format t "length : ~D characters~%" (length text))
          (format t "first 600:~%~A~%~%..." (subseq text 0 (min 600 (length text))))
          (format t "~%content-hash : ~A~%" (problem-content-hash p)))
     ''', also_load_problem=True))

# %% [markdown]
# Determinism check: rebuild the same problem from a **different
# textual ordering** of the residual sums and confirm the hash is
# identical. Then perturb one literal coefficient and confirm the hash
# changes.

# %%
show('hash determinism + perturbation sensitivity',
     run_lisp(r'''
        (in-package :compose-physics)
        (flet ((build (coefficient)
                 (with-state (x v a m k dt time)
                   (let* ((rhs (scale -1.0d0 (product k x)))
                          (residual-a (sum (product m a) rhs))
                          (a-next (product (apply :reciprocal m) (product k x)))
                          (v-next (sum v (product a dt)))
                          (x-next (sum x (product (sum v (scale coefficient (product a dt))) dt)))
                          (time-next (sum time dt)))
                     (make-problem
                       :name "linear-toy"
                       :slot-names (list "x" "v" "a" "m" "k" "dt" "time")
                       :residual-specs (list (cons "newton" residual-a))
                       :update-specs   (list (cons "v" v-next)
                                             (cons "x" x-next)
                                             (cons "a" a-next)
                                             (cons "time" time-next)))))))
          (let ((h1 (problem-content-hash (build 1.0d0)))
                (h2 (problem-content-hash (build 1.0d0)))
                (h3 (problem-content-hash (build 1.0000001d0))))
            (format t "build #1 hash : ~A~%" h1)
            (format t "build #2 hash : ~A   (same input, must match)~%" h2)
            (format t "perturbed     : ~A   (different)~%" h3)
            (format t "~%match #1==#2 : ~A~%" (string= h1 h2))
            (format t "differ #1!=#3: ~A~%" (not (string= h1 h3)))))
     '''))


# %% [markdown]
# ## 7 — Serialize / deserialize round-trip
#
# The canonical sexp form is the on-disk wire format. Round-tripping
# through it must produce a problem whose canonical sexp is identical
# (and therefore whose content hash is identical) to the original.

# %%
show('serialize → deserialize → re-canonicalize equality',
     run_lisp(r'''
        (in-package :compose-physics)
        (let* ((p (symbol-value (find-symbol "*PROBLEM*" :common-lisp-user)))
               (text-original (canonical-sexp-string (canonicalize-problem p)))
               (round-trip    (deserialize-problem-from-string text-original))
               (text-round    (canonical-sexp-string (canonicalize-problem round-trip))))
          (format t "original  hash : ~A~%" (content-hash-string text-original))
          (format t "roundtrip hash : ~A~%" (content-hash-string text-round))
          (format t "byte-identical : ~A~%" (string= text-original text-round)))
     ''', also_load_problem=True))


# %% [markdown]
# ## 8 — Register the problem via the CLI
#
# This is the canonical user-facing path. The CLI:
#
# 1. starts SBCL,
# 2. loads the problem,
# 3. canonicalizes + content-hashes it,
# 4. writes the registry directory,
# 5. emits the chunked C, dispatch, Makefile, manifest,
# 6. runs `make` to produce `lib<name>.so`.
#
# We use `-fno-fast-math` here because we're going to compare the
# compiled output bit-by-bit to the Lisp `funcall` path further down.

# %%
if REGISTRY_ROOT.exists():
    shutil.rmtree(REGISTRY_ROOT)
REGISTRY_ROOT.mkdir(parents=True)

completed = subprocess.run(
    [sys.executable, '-m', 'compose_physics', 'register',
     str(PROBLEM_LISP),
     '--registry-root', str(REGISTRY_ROOT),
     '--source-dest', 'copy',
     '--c-flags', '-O2 -fPIC -fno-fast-math -fno-associative-math'],
    cwd=COMPOSE_PHYSICS_ROOT, capture_output=True, text=True)
print(completed.stdout)
if completed.returncode != 0:
    print('STDERR:', completed.stderr)
    raise RuntimeError('registration failed')

# %%
problem_dirs = [p for p in REGISTRY_ROOT.iterdir() if p.is_dir()]
assert len(problem_dirs) == 1, problem_dirs
problem_dir = problem_dirs[0]
library_pathname = problem_dir / 'libthree-mass-four-spring.so'
assert library_pathname.is_file(), library_pathname

print('problem directory :', problem_dir)
print('library           :', library_pathname.name)


# %% [markdown]
# ## 9 — Emitted artifacts
#
# Inspect what the registry actually wrote.

# %%
print('directory contents:')
for entry in sorted(problem_dir.iterdir()):
    print(f'  {entry.name:30s}  {entry.stat().st_size:>8d} bytes')

# %%
print((problem_dir / 'manifest.sexp').read_text())

# %% [markdown]
# **Chunked residual kernel** — one C row per residual:

# %%
chunk_path = next(problem_dir.glob('residual_chunk_*.c'))
print(chunk_path.name)
print('─' * 60)
print(chunk_path.read_text())

# %% [markdown]
# **Chunked update kernel** — one C row per explicit update slot
# (identity-update slots produce a `state[i]` passthrough):

# %%
chunk_path = next(problem_dir.glob('update_chunk_*.c'))
print(chunk_path.name)
print('─' * 60)
print(chunk_path.read_text())

# %% [markdown]
# **Dispatch translation unit** — fans calls out to chunked rows:

# %%
print((problem_dir / 'dispatch.c').read_text())

# %% [markdown]
# **Makefile** — toolchain, no implicit anything:

# %%
print((problem_dir / 'Makefile').read_text())


# %% [markdown]
# ## 10 — Bind the C ABI through ctypes
#
# The `.so` exposes exactly four C entry points: `get_n` (slot count),
# `get_k` (residual count), `compute_residual(state, out)`,
# `compute_update(state, out)`. Nothing else.

# %%
library = ctypes.CDLL(str(library_pathname))

library.get_n.restype = ctypes.c_int
library.get_k.restype = ctypes.c_int
library.get_n.argtypes = []
library.get_k.argtypes = []

DOUBLE_POINTER = ctypes.POINTER(ctypes.c_double)
library.compute_residual.restype = None
library.compute_residual.argtypes = [DOUBLE_POINTER, DOUBLE_POINTER]
library.compute_update.restype = None
library.compute_update.argtypes = [DOUBLE_POINTER, DOUBLE_POINTER]

SLOT_COUNT = library.get_n()
RESIDUAL_COUNT = library.get_k()
assert SLOT_COUNT == 13, SLOT_COUNT
assert RESIDUAL_COUNT == 3, RESIDUAL_COUNT

SLOT_NAMES = ['x1','x2','x3','v1','v2','v3','a1','a2','a3','m','k','dt','time']
SLOT_INDEX = {name: index for index, name in enumerate(SLOT_NAMES)}
print('slot-count    :', SLOT_COUNT)
print('residual-count:', RESIDUAL_COUNT)
print('slots         :', SLOT_NAMES)


# %%
def buffer_of(state_dict):
    buffer = np.zeros(SLOT_COUNT, dtype=np.float64)
    for name, value in state_dict.items():
        buffer[SLOT_INDEX[name]] = value
    return buffer

def compute_residual(state):
    out = np.zeros(RESIDUAL_COUNT, dtype=np.float64)
    library.compute_residual(
        state.ctypes.data_as(DOUBLE_POINTER),
        out.ctypes.data_as(DOUBLE_POINTER))
    return out

def compute_update(state):
    out = np.zeros(SLOT_COUNT, dtype=np.float64)
    library.compute_update(
        state.ctypes.data_as(DOUBLE_POINTER),
        out.ctypes.data_as(DOUBLE_POINTER))
    return out


# %% [markdown]
# ## 11 — Eigenmode analysis
#
# Stiffness `K = k * [[2,-1,0],[-1,2,-1],[0,-1,2]]`, mass `M = m * I`.
# Continuous eigenfrequencies:
#
# $$\omega_j^2 = \frac{2k}{m} \left(1 - \cos\frac{j\pi}{4}\right), \quad j=1,2,3.$$

# %%
MASS = 1.0
STIFFNESS = 4.0
DT = 1.0e-3

K_matrix = STIFFNESS * np.array([[2,-1,0],[-1,2,-1],[0,-1,2]], float)

analytic_omega = np.sqrt(np.array([
    (2 * STIFFNESS / MASS) * (1 - math.cos(j * math.pi / 4))
    for j in (1, 2, 3)]))
eigvals, eigvecs = np.linalg.eigh(K_matrix / MASS)
numerical_omega = np.sqrt(eigvals)

print('analytic  omega:', analytic_omega)
print('numerical omega:', numerical_omega)
assert np.allclose(np.sort(analytic_omega), np.sort(numerical_omega))

MODE_SHAPES = eigvecs


# %% [markdown]
# ## 12 — Step each eigenmode and recover the frequency via FFT

# %%
def initial_state_for_mode(mode_index, amplitude=1e-3):
    shape = MODE_SHAPES[:, mode_index]
    positions = amplitude * shape
    accelerations = -(K_matrix @ positions) / MASS
    return buffer_of({
        'x1': positions[0], 'x2': positions[1], 'x3': positions[2],
        'v1': 0.0, 'v2': 0.0, 'v3': 0.0,
        'a1': accelerations[0], 'a2': accelerations[1], 'a3': accelerations[2],
        'm': MASS, 'k': STIFFNESS, 'dt': DT, 'time': 0.0,
    })

STEP_COUNT = 65536

def integrate(state):
    history = np.empty((STEP_COUNT, SLOT_COUNT), dtype=np.float64)
    current = state.copy()
    for step in range(STEP_COUNT):
        history[step] = current
        current = compute_update(current)
    return history

def dominant_frequency(signal, dt):
    detrended = signal - signal.mean()
    spectrum = np.abs(np.fft.rfft(detrended))
    freqs = np.fft.rfftfreq(len(detrended), d=dt)
    peak_index = int(np.argmax(spectrum[1:])) + 1
    if 0 < peak_index < len(spectrum) - 1:
        left, center, right = spectrum[peak_index - 1: peak_index + 2]
        denominator = (left - 2 * center + right)
        offset = 0.5 * (left - right) / denominator if denominator != 0 else 0.0
    else:
        offset = 0.0
    bin_width = freqs[1] - freqs[0]
    return freqs[peak_index] + offset * bin_width

histories = []
recovered_omega = np.zeros(3)
for mode_index in range(3):
    history = integrate(initial_state_for_mode(mode_index))
    histories.append(history)
    f_hz = dominant_frequency(history[:, SLOT_INDEX['x1']], DT)
    recovered_omega[mode_index] = 2 * math.pi * f_hz

for mode_index in range(3):
    expected = analytic_omega[mode_index]
    found    = recovered_omega[mode_index]
    print(f'mode {mode_index}: analytic={expected:.6f} '
          f'recovered={found:.6f} '
          f'rel_err={abs(found-expected)/expected:.2e}')
    assert abs(found - expected) / expected < 5e-3


# %% [markdown]
# ## 13 — `compute_residual` is identically zero along the trajectory
#
# Since the update rule is the analytic solution to the residual at
# each step, the residual evaluated on the *output* state must remain
# at machine zero.

# %%
MAX_RESIDUAL = 0.0
for history in histories:
    for step in range(0, STEP_COUNT, 64):
        r = compute_residual(history[step])
        MAX_RESIDUAL = max(MAX_RESIDUAL, float(np.abs(r).max()))
print('max |residual| over all sampled states:', MAX_RESIDUAL)
assert MAX_RESIDUAL < 1e-10


# %% [markdown]
# ## 14 — Lisp-vs-C bit identity on a sample of states
#
# The funcallable Lisp tree and the compiled C kernel must produce
# the **same bit pattern** for both `compute_residual` and
# `compute_update`. This is the strongest check that the emitter
# preserves the IR semantics — and the reason `-fno-fast-math` matters.

# %%
def lisp_evaluate_problem(states):
    nstates = len(states)
    with tempfile.TemporaryDirectory(prefix='compose-physics-eval-') as tmp:
        tmp_path = Path(tmp)
        input_path  = tmp_path / 'input.txt'
        output_path = tmp_path / 'output.txt'
        with input_path.open('w') as handle:
            for state in states:
                handle.write(' '.join(repr(float(value)) for value in state))
                handle.write('\n')
        script = tmp_path / 'eval.lisp'
        script.write_text(textwrap.dedent(f'''\
          (require :asdf)
          (push #p"{COMPOSE_PHYSICS_ROOT}/" asdf:*central-registry*)
          (asdf:load-system :compose-physics)
          (load #p"{PROBLEM_LISP}")
          (setf *read-default-float-format* (quote double-float))
          (let* ((problem (symbol-value (find-symbol "*PROBLEM*" :common-lisp-user)))
                 (slot-count   (compose-physics:problem-slot-count problem))
                 (residual-rows (compose-physics:problem-residual-rows problem))
                 (update-rows   (compose-physics:problem-update-rows  problem))
                 (residual-count (length residual-rows)))
            (with-open-file (in #p"{input_path}" :direction :input)
              (with-open-file (out #p"{output_path}" :direction :output
                                                     :if-exists :supersede
                                                     :if-does-not-exist :create)
                (loop
                  for line = (read-line in nil nil)
                  while line do
                  (let ((buffer (make-array slot-count :element-type (quote double-float)))
                        (token-stream (make-string-input-stream line)))
                    (loop for i below slot-count do
                          (setf (aref buffer i) (coerce (read token-stream) (quote double-float))))
                    (let ((residual-out (make-array residual-count :element-type (quote double-float)))
                          (update-out (make-array slot-count :element-type (quote double-float))))
                      (loop for row across residual-rows for index from 0 do
                            (setf (aref residual-out index)
                                  (funcall (compose-physics:residual-row-expression row) buffer)))
                      (loop for row across update-rows for index from 0 do
                            (setf (aref update-out (compose-physics:update-row-slot-index row))
                                  (funcall (compose-physics:update-row-expression row) buffer)))
                      (loop for v across residual-out do
                            (format out "~,17,,,,,'eE " v))
                      (loop for v across update-out do
                            (format out "~,17,,,,,'eE " v))
                      (terpri out)))))))
        '''))
        completed = subprocess.run(['sbcl','--non-interactive','--load',str(script)],
                                   capture_output=True, text=True)
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr)
        residual_out = np.zeros((nstates, RESIDUAL_COUNT), dtype=np.float64)
        update_out   = np.zeros((nstates, SLOT_COUNT),     dtype=np.float64)
        with output_path.open() as handle:
            for row_index, line in enumerate(handle):
                values = [float(token) for token in line.split()]
                residual_out[row_index] = values[:RESIDUAL_COUNT]
                update_out[row_index]   = values[RESIDUAL_COUNT:RESIDUAL_COUNT + SLOT_COUNT]
        return residual_out, update_out

rng = np.random.default_rng(0xC0FFEE)
sample_states = []
for _ in range(8):
    sample_states.append(buffer_of({
        'x1': rng.normal(), 'x2': rng.normal(), 'x3': rng.normal(),
        'v1': rng.normal(), 'v2': rng.normal(), 'v3': rng.normal(),
        'a1': rng.normal(), 'a2': rng.normal(), 'a3': rng.normal(),
        'm': 1.0 + abs(rng.normal()),
        'k': 1.0 + abs(rng.normal()),
        'dt': 1e-3, 'time': rng.normal(),
    }))
sample_array = np.stack(sample_states)
lisp_residual, lisp_update = lisp_evaluate_problem(sample_array)
c_residual = np.stack([compute_residual(s) for s in sample_array])
c_update   = np.stack([compute_update(s)   for s in sample_array])

residual_match = np.array_equal(lisp_residual.view(np.uint64), c_residual.view(np.uint64))
update_match   = np.array_equal(lisp_update.view(np.uint64),   c_update.view(np.uint64))
print('residual bit-identity:', residual_match)
print('update   bit-identity:', update_match)
if not residual_match:
    print('residual max |diff|:', np.abs(lisp_residual - c_residual).max())
if not update_match:
    print('update   max |diff|:', np.abs(lisp_update   - c_update).max())
assert residual_match and update_match


# %% [markdown]
# ## 15 — Energy bound under symplectic Euler
#
# The system is conservative; the integrator is symplectic Euler.
# Total energy must oscillate around the true value with bounded
# amplitude — never drift secularly.

# %%
def total_energy(state):
    positions  = state[[SLOT_INDEX[k] for k in ('x1','x2','x3')]]
    velocities = state[[SLOT_INDEX[k] for k in ('v1','v2','v3')]]
    kinetic    = 0.5 * MASS * float(velocities @ velocities)
    potential  = 0.5 * float(positions @ K_matrix @ positions)
    return kinetic + potential

general_initial = buffer_of({
    'x1': 1.0e-3, 'x2': -2.0e-3, 'x3': 1.5e-3,
    'v1': 0.0, 'v2': 0.0, 'v3': 0.0,
    'a1': 0.0, 'a2': 0.0, 'a3': 0.0,
    'm': MASS, 'k': STIFFNESS, 'dt': DT, 'time': 0.0,
})
positions0 = general_initial[[SLOT_INDEX[k] for k in ('x1','x2','x3')]]
accelerations0 = -(K_matrix @ positions0) / MASS
for value, name in zip(accelerations0, ('a1','a2','a3')):
    general_initial[SLOT_INDEX[name]] = value

general_history = integrate(general_initial)
energies = np.array([total_energy(general_history[step]) for step in range(0, STEP_COUNT, 16)])
energy_drift = (energies.max() - energies.min()) / energies.mean()
print('relative energy oscillation:', energy_drift)
assert energy_drift < 5e-3


# %% [markdown]
# ## 16 — Trajectory plots

# %%
times = np.arange(STEP_COUNT) * DT
fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
for axis, slot_group, title in zip(
        axes,
        (('x1','x2','x3'), ('v1','v2','v3'), ('a1','a2','a3')),
        ('positions', 'velocities', 'accelerations')):
    for name in slot_group:
        axis.plot(times, general_history[:, SLOT_INDEX[name]], label=name)
    axis.set_ylabel(title); axis.legend(loc='upper right'); axis.grid(True)
axes[-1].set_xlabel('time')
plt.tight_layout(); plt.show()

# %%
kinetic_history = 0.5 * MASS * (
    general_history[:, SLOT_INDEX['v1']]**2
    + general_history[:, SLOT_INDEX['v2']]**2
    + general_history[:, SLOT_INDEX['v3']]**2)
potential_history = np.array([
    0.5 * general_history[step, [SLOT_INDEX[k] for k in ('x1','x2','x3')]]
        @ K_matrix
        @ general_history[step, [SLOT_INDEX[k] for k in ('x1','x2','x3')]]
    for step in range(STEP_COUNT)])
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(times, kinetic_history, label='kinetic')
ax.plot(times, potential_history, label='potential')
ax.plot(times, kinetic_history + potential_history, label='total')
ax.set_xlabel('time'); ax.set_ylabel('energy'); ax.legend(); ax.grid(True)
plt.tight_layout(); plt.show()


# %% [markdown]
# ---
#
# **End of tour.** Every layer of `compose-physics` was exercised:
# IR primitives, vocabulary, problem authoring + introspection,
# simplifier, solver (linear, apply-inversion, structured failure),
# canonicalizer, content-hash, serialize/deserialize, CLI registration,
# emitted C inspection, ctypes binding, and four numerical invariants
# verified against the compiled `.so`.
