# Nothing-was-lost — what was actually checked

The structural checker cannot answer this question. It verifies that every citation
resolves; it cannot verify that a fact still exists. These are the checks that can,
what each one can and cannot establish, and what they found.

---

## 1. Do preservation targets resolve? — weak, and honestly so

Every disposition row marked `keep`, `move` or `mine` names a target. 1,027 rows.

| | |
|---|---|
| target is a real page | 817 (79%) |
| target is not a page — the registry CSV, the log, a frontmatter register | 89 (9%) |
| target resolves to nothing | 121 (11%) |

**This check is weaker than it looks and should not be quoted as a loss rate.** Most
of the 121 are targets written at *section* granularity by a Phase 1 surveyor — the
page exists, the surveyor just wrote `operator/loss` rather than
`operator/loss/residual-loss-design`. A further 11 route deliberately outside the
corpus, and 6 point at a page that merged by decision.

More importantly, the anchors in those targets were **proposed before any page
existed**. Builders chose their own. A mismatch measures the gap between a proposal
and a decision, not a lost fact.

---

## 2. Do distinctive facts survive? — sampled, and it found real losses

Twenty distinctive technical facts, chosen because they survive rewriting: named
equations, specific numbers, named methods. Eighteen present. **Two absent, both
real, both routed.**

- **The low-rank integrator family and its literature.** `gamma-hat` states that the
  drift problem is "exported, not dissolved" — and never says exported *to what*. The
  named family and its papers were gone from the whole tree. This matters beyond a
  missing reference: the manifest's obligation vocabulary
  (`conserve | bound | monotone`) is *precisely* the vocabulary that literature states
  its guarantees in, which is what lets a consumer match an integrator to the
  obligations term for term. And the load-bearing property — error bounds independent
  of small singular values — is the one thing no standard integrator has, and the
  reason a low-rank density matrix is safe to step at all. Without it the export is a
  hand-wave. **The disposition predicted this exact failure in writing.**
- **The diamond dataset's counts and its de-duplication warning.** The acceptance test
  cites the dataset; no page carries its size. It is 1,179 rows but only **1,131
  distinct shapes**, and the check double-counts 48 of them unless de-duplicated
  first. A silently wrong acceptance test is worse than a missing one, because it
  passes. A third figure (~877) circulates and is a byte-salvage count from a
  truncated download, not a dataset size.

---

## 3. Do literature citations survive? — systematic, low-noise

Author-plus-year is distinctive and survives rewriting, unlike prose, which is
deliberately reworded. Harvested from old canon and from the new corpus.

76 citations in old canon · 70 in the new corpus · 44 present in old and absent in new.

**That 44 is almost entirely an artifact and one real finding:**

- **~20 are scaffolding**, caught because the pattern matches `Closed 2026-07-21`,
  `Superseded 2026-…`, `Corrected 2026-…`. Those are history phrasings, deleted on
  purpose. Their absence is the restructure succeeding.
- **~15 are reference-data citations that live in the CSVs**, which survive the
  restructure untouched and **outrank the ledger** in the authority order. The old
  ledger restated them; the new one does not. A citation restated beside an
  authoritative CSV is a drift generator — dropping the restatement applies the
  anti-duplication principle rather than violating it. Verified individually for
  Taniyasu, Ponce and Maeda: each is present in `transport-coefficients.csv`.
- **3 are the integrator papers** from §2 above — the one real loss this check found
  independently, which is what gives the method its credibility.

Two results that the disposition explicitly warned could be lost in a move **were
checked and survived**: the optimal-checkpointing result on a chain, and the
NP-completeness of the general graph case. Both are on the pipeline page with full
citations.

---

## What none of these checks can do

They cannot tell you a fact is *stated correctly* — only that it is present. A
sentence that survives the move with its sign inverted passes every check here.

That is deliberate: it is auditor 2's question, and the 89-row contradiction register
is its starting point. **The one thing to carry forward is that all three losses found
across all three checks came from pages that were correctly deleted or merged.** A
page can be the right thing to remove and still be the only home of something, and no
structural check will ever tell you that.
