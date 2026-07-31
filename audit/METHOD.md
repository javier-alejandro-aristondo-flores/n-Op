# Audit method — what this program learned by getting it wrong

Read this before running any audit against this corpus. Every rule below was paid for by a
specific error in the 2026-07-31 cohesion audit, and each names the error so you can judge
whether it applies to what you are doing.

The single sentence: **the evidence layer held; the layer that summarised it did not.**
Findings resting on primary text and arithmetic were substantially correct. Every error —
without exception — was introduced by a relay, a summary, or an uncalibrated instrument.

---

## 1 · Ground before you dispatch

**Confirm the corpus makes a claim before sending anyone to check that claim against a
source.** Grounding is a *gate* on literature work, not a parallel track.

Two literature checks returned confident, well-evidenced findings against claims the corpus
does not make: nickel's Curie point "stated as 727 K" when `reference-battery.md` says
**627 K**, which is correct; and `3.56712 Å` attributed to Hom/Kiszenick/Post when
`accuracy-ledger.md` says **3.566986 Å** and already flags the loose uncertainty. Neither
agent was wrong about physics. Both were aimed at a premise nobody had verified existed.

The check is one command. Run it first.

## 2 · Verify by content, never by coordinate

Search for the quoted **string**. Never navigate to a cited `file.md:NN` and read what is
there.

A plant that *deleted* a line offset every subsequent line in a scratch copy. Cited line
numbers were then read against the real corpus, returning the wrong text — and a **real**
defect (`cert-obligations.md` writing "Adiabatic-Hedin-Coulomb" where
`coupling-structure.md` correctly writes "Allen–Heine–Cardona") was dismissed as a plant.

Normalise away only what legitimately differs between a quotation and its source: markdown
emphasis, line wrapping, non-breaking spaces, the several dash codepoints, trailing
punctuation the quoter added. **Collapse newlines on both sides** — the corpus wraps where a
quotation does not.

## 3 · Every negative needs a control

An absence produced by an instrument nobody checked is not a result.

A control is a pattern *demonstrated* to produce a hit. It must include the Unicode and
en-dash character class (`–`, `δ`, `τ`, `⟨u²⟩`), because a sweep blind to a character class
reports absence **everywhere that class appears** — which looks exactly like a finding.

## 4 · The instrument is wrong until calibrated, and sampling is what finds it

When a mechanical check produces a number, the first hypothesis is that the *instrument* is
broken, not the corpus.

The grounding script was wrong five consecutive times:

| reported | the actual bug |
|---|---|
| 77 of 113 absent | blockquotes separated by prose concatenated into strings existing nowhere |
| 65 "moved" | 36 named no file at all — an attribution gap reported as a relocation |
| 131 findings "no evidence" | 127 quote inline or in table cells; the pass read blockquotes only |
| 417 absent | a 14-item random sample was **14/14 instrument artifact** |
| 58 untestable | the filter rejected any quotation *opening with a quote mark* |

**Four of those five runs would have supported a confident claim that the audit was
substantially fabricated. The true count of fabrications was zero.** Every bug was found by
sampling the output; none by rereading the code.

This applies recursively. A hand re-verification of ten findings first read 7/10, and all
three disagreements were bugs in the re-checker.

## 5 · Report raw outcomes, never rates, in thin cells

A "0 of 1" is not a detection rate. A four-of-six gate is a four-of-six gate and rounding it
up is precisely the failure calibration exists to prevent. Publish every disputed count
**with the rule that produced it** — "24 rows with no author and no year" has been 23, 24,
28 and 29 depending on who counted, and none of those was dishonest.

## 6 · Isolation is architectural, not behavioural

A calibration arm **cannot live anywhere in the scorer's tree, at any depth.**

Contamination travelled two different directions in one run. A sub-subagent two levels down
routed its full contents past its own parent to the fleet root. Separately — and this was
self-disclosed, not detected — a sweeper *peer-to-peer* commissioned plants from a
calibration arm it did not serve, then burned the blind control by diffing its scratchpad
against the real tree to answer a provenance question. Between them both controls were
destroyed and the blind arm produced no scoreable result.

Discipline at any single level cannot fix a transitive leak. **The fix is channel
separation:** a calibration result reports a score and a method verdict, *never* a defect
list; any agent reporting a defect must name the file it verified against.

Additional requirements if you run a blind arm: mtime-normalise the corpus (a single
`ls -la` hands over the answer set); diff the control set against the plant set before
dispatch (one plant deleted the value a control depended on); seal the sweeper's prompt
before the answer key exists and keep the timestamps.

## 7 · Prefer the mechanism to the fleet

Mechanical checks outperformed agent judgment at every step of this program — provided the
mechanism is itself calibrated per rule 4. More agents add unverified claims to a pile that
already has a measurable error rate.

Where verification must happen, **do it in your own context.** Removing the relay is the
fix; more vigilance at each hop is not.

## 8 · A prior clearance is not evidence, and neither is authority

Re-verify values, never verdicts. Something marked verified is not verified: a recorded
2026-06-10 re-audit passed thermal conductivity as sound and missed a conductivity
overprediction, a mis-citation, and a fabricated citation.

Resolving a contradiction by naming which page outranks the other resolves nothing — it
looks up a convention. Go to the physics or to the literature.

## 9 · Nothing blocks; a blocker becomes a shaped gap

Never return "could not access". Route around first — author's copy, preprint, a later paper
quoting the number, a review that tabulates it, the same measurement by someone else, the
quantity derived from adjacent ones in hand.

If it genuinely cannot be reached, declare a gap with four parts: **what it would settle**
(a question with a determinate answer) · **the conclusion without it** · **the branches**
(what changes if X, if Y) · **what depends on it**. The fourth part keeps the gap isolated
rather than contagious. A gap that says "we could not check this" forces the research to be
redone; a shaped gap is closed by a lookup.

**Never substitute a guess for a blocked source.** A plausible number where a citation
belongs is worse than an absence, because nothing will ever fire on it.

---

## What "complete" means here, and what it does not

The corpus is **structurally complete**: 134 registry rows at full arity, 179 reference-data
rows, zero blank cells anywhere. So structural sweeps find nothing and prove nothing.

Every real completeness defect in this corpus is **semantic** — a cell that is filled but
does not carry what its column promises. The archetype is one grep: the schema declares the
signature field holds *"typed inputs to output, with units"*, and **zero of 134 rows carry a
unit**. The cell is not empty. It is not complete either.

Distinguish this from *coverage* completeness — whether a needed topic is absent — which is
a different audit with different instruments.
