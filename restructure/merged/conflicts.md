# Merge conflicts and gate checks

## Needs resolution before Phase 2

- target claimed by 2 fragments: `oracle/certification/cert-obligations#reference-cache`  <- oracle-cert-accuracy, oracle-compilation
- target claimed by 2 fragments: `oracle/certification/cert-obligations#tolerance-ledger`  <- oracle-cert-accuracy, practice
- target claimed by 2 fragments: `oracle/compilation/compose-time-pipeline#stage-2-5`  <- oracle-compilation, oracle-laws-seams
- target claimed by 2 fragments: `oracle/laws/generic-dynamics#evolver-duality`  <- program, strata
- target claimed by 2 fragments: `oracle/laws/generic-dynamics#nine-regimes`  <- appendix-a, oracle-laws-seams
- target claimed by 2 fragments: `oracle/laws/residual-definitions#balance-laws`  <- appendix-a, appendix-b
- target claimed by 2 fragments: `oracle/laws/residual-definitions#static-thermodynamic`  <- appendix-b, oracle-state
- target claimed by 2 fragments: `oracle/laws/residual-definitions#symmetries`  <- appendix-a, appendix-b
- target claimed by 2 fragments: `oracle/registry/typed-compositions#electronic`  <- appendix-a, oracle-registry
- target claimed by 2 fragments: `oracle/registry/typed-compositions#magnetic`  <- appendix-a, oracle-registry
- target claimed by 2 fragments: `oracle/registry/typed-compositions#mechanical`  <- appendix-a, oracle-registry
- target claimed by 2 fragments: `oracle/registry/typed-compositions#optical`  <- appendix-a, oracle-registry
- target claimed by 2 fragments: `oracle/registry/typed-compositions#structural`  <- appendix-a, oracle-registry
- target claimed by 2 fragments: `oracle/registry/typed-compositions#thermal`  <- appendix-a, oracle-registry
- target claimed by 2 fragments: `oracle/registry/typed-compositions#thermodynamic`  <- appendix-a, oracle-registry
- target claimed by 2 fragments: `oracle/registry/typed-compositions#transport`  <- appendix-a, oracle-registry
- target claimed by 2 fragments: `oracle/seams/residual-machinery#registration-gate`  <- appendix-c, oracle-laws-seams
- target claimed by 3 fragments: `oracle/state/crystal-inputs#environment`  <- appendix-b, oracle-compilation, oracle-state
- target claimed by 2 fragments: `practice/glossary`  <- appendix-a, strata
- target claimed by 2 fragments: `program/purpose/purpose-and-scope#material-scope`  <- appendix-c, program

## Convergent findings — the same gap found independently

Not conflicts. Two or more surveyors reached the same descriptive id from
different scopes, which corroborates the finding. Merge into one entry and
record every source.

- `adjoint-drift-monitoring` — found by oracle-compilation, oracle-laws-seams, practice, strata
- `environment-schema` — found by appendix-b, appendix-c, oracle-state, program, strata
- `g0w0-cost-scope-tag` — found by oracle-state, practice
- `implementation-language-picks` — found by practice, program
- `layer-175-minimum-spec` — found by practice, strata
- `mesh-sigma-floor-undeclared` — found by oracle-cert-accuracy, practice
- `obligation-9-scope` — found by oracle-cert-accuracy, strata
- `pde-mesh-adjoint-scheme` — found by oracle-compilation, practice
- `response-causality-slot` — found by appendix-b, appendix-c
- `semiconductor-interface-predicate` — found by oracle-cert-accuracy, practice
- `state-wire-schema` — found by oracle-state, strata
- `surrogate-net-build-vs-adopt` — found by oracle-compilation, practice
- `unregistered-composition-formulas` — found by oracle-registry, practice

## Shared targets — verify, do not assume

Two fragments routing content to one anchor is correct when they carry
*different* facts, and a duplication when they carry the same one. Each needs
an eyeball before the page is written.

- `oracle/certification/cert-obligations#reference-cache` <- oracle-cert-accuracy, oracle-compilation
- `oracle/certification/cert-obligations#tolerance-ledger` <- oracle-cert-accuracy, practice
- `oracle/compilation/compose-time-pipeline#stage-2-5` <- oracle-compilation, oracle-laws-seams
- `oracle/laws/generic-dynamics#evolver-duality` <- program, strata
- `oracle/laws/generic-dynamics#nine-regimes` <- appendix-a, oracle-laws-seams
- `oracle/laws/residual-definitions#balance-laws` <- appendix-a, appendix-b
- `oracle/laws/residual-definitions#static-thermodynamic` <- appendix-b, oracle-state
- `oracle/laws/residual-definitions#symmetries` <- appendix-a, appendix-b
- `oracle/registry/typed-compositions#electronic` <- appendix-a, oracle-registry
- `oracle/registry/typed-compositions#magnetic` <- appendix-a, oracle-registry
- `oracle/registry/typed-compositions#mechanical` <- appendix-a, oracle-registry
- `oracle/registry/typed-compositions#optical` <- appendix-a, oracle-registry
- `oracle/registry/typed-compositions#structural` <- appendix-a, oracle-registry
- `oracle/registry/typed-compositions#thermal` <- appendix-a, oracle-registry
- `oracle/registry/typed-compositions#thermodynamic` <- appendix-a, oracle-registry
- `oracle/registry/typed-compositions#transport` <- appendix-a, oracle-registry
- `oracle/seams/residual-machinery#registration-gate` <- appendix-c, oracle-laws-seams
- `oracle/state/crystal-inputs#environment` <- appendix-b, oracle-compilation, oracle-state
- `practice/glossary` <- appendix-a, strata
- `program/purpose/purpose-and-scope#material-scope` <- appendix-c, program
