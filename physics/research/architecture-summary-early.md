I'll explore the Racket library structure and synthesize an architectural summary. Let me start by reading the top-level documentation and orientation files.
Excellent overview. Now let me read the AGENTS.md, CLAUDE.md, and explore the directory structure.
Now let me explore each subdirectory.
Let me read representative files from each module to understand patterns.
Now let me sample a few representative files from each subdirectory.
Let me sample a test file and the staged code generation file's strategy, then check the .gitignore.
Let me check naming conventions and check for any further patterns by sampling a few more.
Confirmed: exactly one typed module (the api boundary). Let me check the tests directory and verify a few more files.
Now I have enough to write the architectural summary. Let me also briefly check what's in the .claude directory.
Output directory exists. Let me also peek at one more file to confirm test patterns and then write the summary.
Now I have a clear picture. Let me write the architectural summary.
Wrote `/home/javier/Desktop/Physics/Programs/n-Op/physics-library-architecture.md` (425 lines, ~20 KB).

It covers Top-Level Layout, Module Architecture (with the strict `core ← kernel ← cert` import order I confirmed by grepping the relative requires, plus the typed `physics/api.rkt` seal), Conventions and Style (single `typed/racket/base` module out of 42; long descriptive names; header-docstring discipline; uniform `flvector` representation; loud-failure error model), Build / Install / Test Story (the deliberate `info.rkt` scoping; the placeholder `install/` and `interface/` stages), Design Philosophy (the layered/seal pattern, two primitives, no-symbolics rule, expand-time staging, verified-provenance certificate sub-tree), and Cross-Cutting Concerns (no logging, no FFI, near-zero external deps, macros confined to compile-time, `bd`-based issue workflow).

I kept it strictly architectural: no mention of what physics the library computes, what equations are solved, or what any module is "used for" at the domain level; modules under `library/physics/` and the worked examples are referenced only as structural slots, and `demo.ipynb` is mentioned only as existing at the repo root.
