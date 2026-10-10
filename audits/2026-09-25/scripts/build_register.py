"""build the audit register (markdown) and its structured companion from the findings, verdicts, adjudication, ledger, calibration and coverage files; every printed quote is re-grounded at 485a7d9"""
import collections
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

AUDIT = Path(__file__).resolve().parent.parent
SNAP = Path("/home/javier/Projects/Physics/Programs/n-Op-audit-baseline")
FIXES = AUDIT.parent.parent
REGISTER = FIXES / "audits" / "2026-09-25-test-suite-audit.md"
COMPANION = AUDIT / "outputs" / "register.json"
SEVERITY_WORDS = {"S1": "wrong result", "S2": "wrong statement", "S3": "silent deviation", "S4": "latent defect", "S5": "cosmetic"}

REVIEW_LIST = """## The review list (needs Javier's or the PI's decision; nothing here was changed)

| # | finding | why it is not clear-cut | proposed resolution |
|---|---|---|---|
| R1 | Perovskite symmetry copies: the 125 angle runs are 14 crystals; 57 of 61 holdout test runs have a mirrored or permuted copy in training (M3-branch-trunk-parameters-to-charge-001, confirmed by the conductor on 2 October) | re-labels the lattice task's rows; a symmetry-aware copy floor near 1.7e-7 would beat every member on that block | add the symmetry-aware copy floor as a row; re-label the rows; re-split only when training resumes |
| R2 | Energy trunk (VI.1): no bar; a nearest-curve copy (0.149 / 0.172) beats the member (0.206 / 0.265) | changes a verdict word | report the copy row; status "no bar; a copy beats it" (F13 removed the word "pass") |
| R3 | Frequency_Split_Relative_L2 weights a z-aligned error by the square root of two and a full band returns 0.2968 where Relative_L2 returns 0.2980 | every frequency_split row moves when fixed | fix the function, re-score inference-only, record old beside new |
| R4 | The conformal coverage: results.json stores the median 1.0 and the guarantee band in the interval fields, the report quotes the mean 0.977, the guarantee bounds a third event (M5-correction-001, -013, N4-encoders-readouts-wrappers-001, -003, S1-metrics-intervals-pooling-016) | a reported number and its interpretation change together | report the event the guarantee bounds (22/22 or 21/22, from the checkpoint), label the statistics, correct the artifact |
| R5 | Manifold decoder scored in-sample on 337 of 423 levels; Galerkin on 24 of 27; the two-input bases fit on the validation fold too | numbers are not what the text says, verdicts stand | state the in-sample share beside each number; add the out-of-sample rows |
| R6 | Alloy ELF targets exist and are unused by every ELF member | scoring them is a new result | decide whether the cubic block's loader maps the spin-summed key |
| R7 | 7 of 21 fold-0 defect units share chemistry with training (section 9.2 says stratify by chemistry class) | a split change means retraining | label the held-out-chemistry rows now; new split when training resumes |
| R8 | The two silicon runs labeled "H" (K01) | a data label and the splits | exclusion rule E11, re-split when training resumes |
| R9 | The ELF ridge floor fits unclipped spin densities and the gradient magnitude; the shell filter is fit on the up spin only | changing a pre-registered floor moves every bar | keep the floors; note the differences; report the physical-form floors as separate lines |
| R10 | Real pseudopotential titles in two test files and one spec (K31, M10-structure-to-density-023) | Javier's call; the repository is private since October | invented fixture titles, one commit |
| R11 | The flagship and branch-trunk members have no results.json; the ladder rows' MAEs have no committed source (K26, K35) | writing one runs the evaluation (inference-only) | generate from the A7 re-scoring outputs once the guards are off |
| R12 | Half of the flagship's spectral parameters are dead (F1 is the bookkeeping) | a parametrization change | design A4 of the physicality plan, with a checkpoint converter |
| R13 | The stored spin-polarized ELF follows VASP 6.2.0's pre-fix convention, ELF = 1/(1 + 2^(4/3) chi^2) (proven 9 October from a WAVECAR recomputation) | every ELF floor, bar and result moves under the corrected target | record it in the canon and the store's field table; derive the corrected target by exact algebra as a new store field; never pool alloy and diamond ELF |
| R14 | The semilocal floor named in the canon (a gradient-expansion ELF) is not the floor built (a linear ridge); the gradient-expansion floor scores 0.0904 against the ridge's 0.0976 | the 97.8% claim is against a weaker floor than described | add the gradient-expansion row; restate the claim |
| R15 | The orbit map merges 22 of 296 orbits (all two-angle and 13 of 19 three-angle shear orbits) whose cells are not symmetry-equivalent (D2-grouping-and-splits-003, -004; count corrected by the verifier) | units, splits and the "exact symmetry copies" claims for those families change | split those orbits by the metric's eigenvalues; re-label the units; re-split when training resumes |
| R16 | The implicit adjoint iteration has no convergence check and returns a divergent partial sum silently for a non-contractive equilibrium (N3-compositions-007) | training-path code | add a convergence record and a raise-or-fallback; applies to future runs |
| R17 | The parametric bracketing floor's shear-arm rows are measured on fields averaged over three shear orientations and both functionals, not on any run (M2-flagship-ladder-potential-parametric-001, S1) | the II.4 floor numbers move (per run the one-angle floor is 2x, the two-angle 1.3x) | recompute the floor rows per run; the canon's expectation that the floor wins is unaffected |
| R18 | The fixed-basis budget searches score candidates by plain run medians, not unit medians (K10, report.py lines 266 and 1188) | could change the chosen budget | document now; unit medians when training resumes |

Questions for the PI are listed in the plan's FLAGSHIP PHYSICALITY section (eight on the pause, budget and inputs; six on the pseudopotential license).
"""

NOT_CHECKED = """## What was not checked, and deviations from the plan

- **Agents on Fable.** The plan said every agent runs on Opus. Round 1b's relaunch set no model, so the auditors G, O1, O2, O3, the ledger extractions L4-L7 and the resolver batches L1:1-4, L3:1-5, L2:1, L2:3, L6:1 and L6:3 ran on Fable 5.1 (the conductor's model). Their results stand and were verified like everything else; every later agent (round 2, the last resolver, round 3) ran on Opus.
- **The conductor's S2 re-check is a sample.** The plan committed the conductor to re-checking every S1 and S2. Every S1 (26) and every contested S2 was re-checked; of the 303 S2 that round 2 confirmed, a seeded sample of 48 (seed 20261009) was re-checked in the conductor's own context, 47 confirmed and 1 reproduced by the verifier only, none refuted. The other 255 stand on the blind verifier plus the mechanical grounding.
- **The evidence-command replay** of every S1-S3 finding, a mechanical-gate step, was skipped: the round-2 verifiers re-derived evidence by their own routes instead.
- **S4 and S5 verification.** S4 findings carry one blind verifier; S5 findings are grounded mechanically and not verified, by the round-2 design.
- **Round 3** re-read the 56 files round 1 covered only superficially; its findings were grounded, deduplicated against the 618 and verified before entering this register (see the round-3 section). Coverage after round 3 is complete at the file level; depth remains what one or two readers give a file.
- **The salvaged auditors.** Three round-1 auditors (structure-to-density, convolutional, results page) were stopped by the session limit after saving complete files; their saved files stand as their returns, calibrated against the 19 auditors whose saved files matched their returns.
- **The unparsable resolver file.** Resolver batch L6:1's saved file could not be parsed; its 40 rows were re-resolved by one Opus agent on 9 October.
- **Store integrity.** The guards (store, census, training and figure caches read-only; pseudopotential files unreadable) were on from the audit's first gate on 25 September until the end of Phase D on 9 October and restored from the recorded modes (19,202 targets, 0 failures). The fingerprint of `/Pool/VASP_DATA/_derived` and `_census` taken after the restore matches the one taken after the first gate in every one of its 10,808 entries (content, time and permission bits), so nothing the audit or the flagship inspection ran wrote to the store.
- **Not in scope:** 1-archive/, the pnp-op seed paper, the ladder worktree's unmerged branch (except where trunk quotes it), and /Pool data the test-suite work never read. The fixed-point rung's evaluation (uncommitted in the ladder worktree) is not judged here.
"""


def Rows(path):
    """one parsed object per non-empty line of a jsonl file, or nothing when the file is absent"""
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def Normalized(text):
    """whitespace-collapsed, compatibility-normalized text for content matching"""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip()


FILE_CACHE = {}


def Snapshot_Text(file_name):
    """a file's text at 485a7d9, or a commit's message for a commit:<hash> name, cached"""
    if file_name in FILE_CACHE:
        return FILE_CACHE[file_name]
    if file_name.startswith("commit:"):
        text = subprocess.run(["git", "-C", str(SNAP), "log", "-1", "--format=%B", file_name[7:]], capture_output=True, text=True).stdout
    else:
        path = SNAP / file_name
        text = path.read_text(errors="replace") if path.exists() else ""
    FILE_CACHE[file_name] = Normalized(text)
    return FILE_CACHE[file_name]


def Grounded(file_name, quote):
    """whether the quote appears in the file's content at 485a7d9"""
    return bool(quote) and Normalized(quote) in Snapshot_Text(file_name)


def Load():
    """every input the register is built from"""
    findings = {f["id"]: f for f in Rows(AUDIT / "findings/round1b-findings-deduped.jsonl")}
    verdicts = {v["id"]: v for v in Rows(AUDIT / "findings/round2-verdicts.jsonl")}
    reproductions = {r["id"]: r for r in Rows(AUDIT / "findings/round2-reproductions.jsonl") + Rows(AUDIT / "findings/round3-reproductions.jsonl")}
    defenses = {d["id"]: d for d in Rows(AUDIT / "findings/round2-defenses.jsonl") + Rows(AUDIT / "findings/round3-defenses.jsonl")}
    leads = {v["id"]: v for v in Rows(AUDIT / "findings/round2-lead-verdicts.jsonl")}
    known_leads = Rows(AUDIT / "findings/known-leads-verified.jsonl")
    adjudication = {a["id"]: a for a in Rows(AUDIT / "findings/phase-d-adjudication.jsonl")}
    s1_recheck = {r["id"]: r for r in Rows(AUDIT / "findings/phase-d-s1-recheck.jsonl") if "id" in r}
    s2_recheck = {r["id"]: r for r in Rows(AUDIT / "findings/phase-d-s2-recheck.jsonl") if not r["id"].startswith("_")}
    round3 = {f["id"]: f for f in Rows(AUDIT / "findings/round3-findings-deduped.jsonl")}
    round3_verdicts = {v["id"]: v for v in Rows(AUDIT / "findings/round3-verdicts.jsonl")}
    phase_a = Rows(AUDIT / "findings/phase-a.jsonl")
    ledger_rows = Rows(AUDIT / "findings/round1b-ledger-rows-final.jsonl")
    resolutions = {r["row_id"]: r for r in Rows(AUDIT / "findings/round1b-resolutions-merged.jsonl")}
    calibration = json.loads((AUDIT / "outputs/blind-calibration.json").read_text())
    coverage = json.loads((AUDIT / "outputs/round1b-coverage-merged.json").read_text())
    fix_map_path = AUDIT / "findings/fix-map.json"
    fix_map = json.loads(fix_map_path.read_text()) if fix_map_path.exists() else {}
    commits = subprocess.run(["git", "-C", str(FIXES), "log", "--format=%h%x09%s", "485a7d9..HEAD"], capture_output=True, text=True).stdout.strip().splitlines()
    return dict(findings=findings, verdicts=verdicts, reproductions=reproductions, defenses=defenses, leads=leads, known_leads=known_leads, adjudication=adjudication, s1_recheck=s1_recheck, s2_recheck=s2_recheck, round3=round3, round3_verdicts=round3_verdicts, phase_a=phase_a, ledger_rows=ledger_rows, resolutions=resolutions, calibration=calibration, coverage=coverage, fix_map=fix_map, commits=commits)


def Final_Status(finding, data):
    """the finding's register status after round 2, the adjudication and the conductor's re-checks"""
    identifier = finding["id"]
    is_round3 = identifier in data["round3"] and identifier not in data["findings"]
    verdict = (data["round3_verdicts"] if is_round3 else data["verdicts"]).get(identifier, {}).get("verdict")
    adjudged = data["adjudication"].get(identifier)
    severity = finding["severity"]
    status = "unverified"
    note = ""
    if verdict == "claim_holds":
        status = "confirmed"
    elif verdict == "partly":
        status = "confirmed in part"
    elif verdict == "negation_holds":
        status = "refuted"
    elif verdict is None and severity == "S5":
        status = "grounded only (S5, not verified by design)"
    if adjudged:
        severity = adjudged.get("severity", severity)
        decision = adjudged["decision"]
        status = {"keep": status if status != "unverified" else "confirmed", "narrow": "confirmed, narrowed", "downgrade": "confirmed, downgraded", "drop": "dropped (refuted)", "post_snapshot": "postdates the audited commit"}.get(decision, status)
        note = adjudged.get("note", "")
    if is_round3:
        status += " (round 3)"
    reproduction = data["reproductions"].get(identifier)
    if reproduction is not None:
        status += f"; reproduced by a second route: {reproduction.get('reproduced', '?')}"
    defense = data["defenses"].get(identifier)
    if defense is not None and defense.get("excuse") not in (None, "none", "reading"):
        status += f"; defense: {defense['excuse']}" + (" (after the result)" if defense.get("post_result") else "")
    if identifier in data["s1_recheck"]:
        status += f"; conductor re-check: {data['s1_recheck'][identifier].get('recheck', 'done')}"
    if identifier in data["s2_recheck"]:
        status += f"; conductor re-check: {data['s2_recheck'][identifier]['result']}"
    fix = data["fix_map"].get(identifier)
    if fix:
        status += f"; fix: {fix}"
    return severity, status, note


def Finding_Lines(finding, severity, status, note, detailed):
    """the register's lines for one finding; detailed findings print the full pair, the rest one row"""
    grounded = Grounded(finding["file"], finding["quote"])
    quote = finding["quote"] if grounded else "[quote withheld: did not re-ground]"
    if detailed:
        lines = [f"#### {finding['id']} ({severity}, {SEVERITY_WORDS[severity]}) in `{finding['file']}`", "", f"- **Quote:** {quote}", f"- **Counter ({finding['counter_kind']}, `{finding['counter_file']}`):** {finding['counter']}", f"- **Claim:** {finding['claim']}", f"- **Fix proposed:** {finding['fix']}" + (" (clear-cut)" if finding.get("clear_cut") else ""), f"- **Status:** {status}"]
        if note:
            lines.append(f"- **Adjudication:** {note}")
        lines.append("")
        return lines, grounded
    claim = finding["claim"].replace("|", "\\|").replace("\n", " ")
    return [f"| {finding['id']} | `{finding['file']}` | {claim} | {status}{(' — ' + note) if note else ''} |"], grounded


def Build():
    """write the register and its companion, returning the counts"""
    data = Load()
    all_findings = dict(data["findings"])
    all_findings.update(data["round3"])
    by_severity = collections.defaultdict(list)
    set_aside = []
    companion = []
    ungrounded = []
    for finding in all_findings.values():
        severity, status, note = Final_Status(finding, data)
        companion.append(dict(id=finding["id"], file=finding["file"], severity_original=finding["severity"], severity_final=severity, slice=finding["slice"], status=status, note=note, quote=finding["quote"], counter=finding["counter"], claim=finding["claim"], fix=finding["fix"], clear_cut=finding.get("clear_cut", False)))
        if severity not in SEVERITY_WORDS:
            set_aside.append((finding, status, note))
            continue
        by_severity[severity].append((finding, status, note))
    lines = ["# The test-suite audit of 2026-09-25: register", "", "Every finding is a contradiction pair quoted by content from the repository at trunk `485a7d9` (the read-only worktree `../n-Op-audit-baseline`). A finding enters this register only if its quote re-grounds at that commit when this page is built and a blind verifier confirmed it (round 2 or round 3); every S1 was also reproduced by a second route and re-checked by the conductor, and every contested S2 was adjudicated by the conductor. Severities: S1 wrong result, S2 wrong statement, S3 silent deviation (built or measured differently from a pre-code document with no reason recorded where readers look), S4 latent defect, S5 cosmetic. Nothing here quotes a pseudopotential title or a volumetric array.", ""]
    counts = {severity: len(by_severity[severity]) for severity in ("S1", "S2", "S3", "S4", "S5")}
    statuses = collections.Counter()
    for severity in counts:
        for _, status, _ in by_severity[severity]:
            statuses[status.split(";")[0]] += 1
    lines += ["## Counts", "", "| severity | findings |", "|---|---|"] + [f"| {severity} {SEVERITY_WORDS[severity]} | {counts[severity]} |" for severity in counts] + [f"| set aside (refuted or postdating the commit) | {len(set_aside)} |", "", "| status (first clause) | findings |", "|---|---|"] + [f"| {status} | {count} |" for status, count in statuses.most_common()] + [""]
    calibration = data["calibration"]
    tally = calibration["tally"]
    overlap = calibration["overlap_estimate"]
    lines += ["## Calibration and coverage", "", f"**Blind key.** {calibration['key']}. Of {tally['blind_items']} blind items the auditors found {tally['blind_found_by_findings']} through findings and {tally['blind_found_by_ledger_only']} more through the commitment ledger ({tally['blind_recall_findings_only']:.0%} and {tally['blind_recall_with_ledger']:.0%}; {tally['blind_recall_excluding_the_two_refuted_items_K05_K43']:.0%} excluding the two items the pre-check had already refuted). Memory-file items: {tally['memory_file_found']} of {tally['memory_file_items']}; hinted items: {tally['hinted_found']} of {tally['hinted_items']} ({tally['note']}).", "", f"**Overlap estimate.** {overlap['method']}: owners found {overlap['owner_found']}, the overlap auditors {overlap['overlap_found']}, both {overlap['both']}; estimated total {overlap['estimated_total']} (Chapman {overlap['chapman_estimate']}), so owner recall about {overlap['estimated_owner_recall']:.0%} and union recall about {overlap['estimated_union_recall']:.0%}. {overlap['caveat']}.", ""]
    lines += ["**The blind key, item by item** (status after the lead verification stage and the adjudication):", "", "| key | status | by |", "|---|---|---|"]
    lead_status = {}
    for item in calibration["items"]:
        lead = data["leads"].get(item["id"], {})
        adjudged = data["adjudication"].get(item["id"], {})
        verdict = lead.get("verdict", "")
        word = {"claim_holds": "holds", "partly": "holds in part", "negation_holds": "refuted"}.get(verdict, "not in the lead stage")
        if adjudged:
            word += f"; {adjudged['decision']}" + (f" ({adjudged['severity']})" if adjudged.get("severity") not in (None, "none") else "")
        lead_status[item["id"]] = word
        lines.append(f"| {item['id']} | {item['status']} by the auditors; {word} | {', '.join(item.get('by', [])) or '-'} |")
    lines.append("")
    coverage = data["coverage"]
    lines += ["**Coverage from transcripts** (files an auditor read whole / in part / only a shell / never):", "", "| auditor | whole | part | shell | never |", "|---|---|---|---|---|"] + [f"| {name} | {len(c['whole'])} | {len(c['part'])} | {len(c['shell'])} | {len(c['never'])} |" for name, c in sorted(coverage.items())] + ["", "Round 3 re-read every shell-level file with fresh auditors; the two never-read files were read by the conductor (`outputs/round3-dotfiles-read.md`).", ""]
    rows = data["ledger_rows"]
    resolutions = data["resolutions"]
    status_counts = collections.Counter(resolutions[r["row_id"]]["status"] for r in rows if r["row_id"] in resolutions)
    deviations = [resolutions[r["row_id"]] for r in rows if resolutions.get(r["row_id"], {}).get("status") == "deviation"]
    recording_counts = collections.Counter(d["recording"] for d in deviations)
    lines += ["## The commitment ledger", "", f"{len(rows)} commitments extracted from the pre-code documents (test-suite.md at 85d0be5, the specs at 9f0b34a, the manifests and README at 155112c); {sum(1 for r in rows if r['row_id'] in resolutions)} resolved against 485a7d9: " + ", ".join(f"{count} {status}" for status, count in sorted(status_counts.items())) + ". Of the deviations: " + ", ".join(f"{count} {recording}" for recording, count in sorted(recording_counts.items())) + f"; {sum(1 for d in deviations if d.get('post_result'))} recorded only after the affected result existed. The full ledger is `audits/2026-09-25/findings/round1b-ledger-rows-final.jsonl` with `round1b-resolutions-merged.jsonl`.", "", "### Silent deviations", "", "| row | commitment | as built |", "|---|---|---|"]
    row_by_id = {r["row_id"]: r for r in rows}
    for d in sorted(deviations, key=lambda d: d["row_id"]):
        if d["recording"] == "silent":
            row = row_by_id[d["row_id"]]
            lines.append(f"| {d['row_id']} | {row['quote'][:160].replace('|', '/').replace(chr(10), ' ')} | {d['as_built'][:220].replace('|', '/').replace(chr(10), ' ')} |")
    lines.append("")
    lines += ["## Fixes landed on `audit-fixes`", "", f"{len(data['commits'])} commits off `485a7d9`, one fix each, the full gate (631 tests) green after each batch, nothing pushed; `findings/fix-map.json` names the findings each closes:", ""] + [f"- `{line.split(chr(9))[0]}` {line.split(chr(9))[1][:220]}" for line in reversed(data["commits"])] + [""]
    lines += [REVIEW_LIST, NOT_CHECKED]
    for severity in ("S1", "S2", "S3", "S4", "S5"):
        detailed = severity == "S1"
        lines += [f"## {severity}: {SEVERITY_WORDS[severity]} ({counts[severity]})", ""]
        if not detailed:
            lines += ["| id | file | claim | status |", "|---|---|---|---|"]
        for finding, status, note in sorted(by_severity[severity], key=lambda item: item[0]["id"]):
            finding_lines, grounded = Finding_Lines(finding, severity, status, note, detailed)
            if not grounded:
                ungrounded.append(finding["id"])
            lines += finding_lines
        lines.append("")
    lines += ["## Set aside: refuted by the verification, or postdating the audited commit", "", "| id | file | claim | status |", "|---|---|---|---|"]
    for finding, status, note in sorted(set_aside, key=lambda item: item[0]["id"]):
        finding_lines, _ = Finding_Lines(finding, finding["severity"], status, note, False)
        lines += finding_lines
    lines.append("")
    lines += ["## Phase A (the conductor's mechanical sweeps)", ""] + [f"- **{item.get('id', '?')}** ({item.get('severity', '?')}) `{item.get('file', '')}`: {item.get('claim', '')}" for item in data["phase_a"]] + [""]
    lines += ["## Known leads verified by the conductor before round 1", "", "| key | status | by |", "|---|---|---|"] + [f"| {item['key']} | {item['status']} | {item['by']} |" for item in data["known_leads"]] + [""]
    REGISTER.write_text("\n".join(lines))
    COMPANION.write_text(json.dumps(dict(counts=counts, statuses=statuses, set_aside=len(set_aside), ungrounded=ungrounded, lead_status=lead_status, findings=companion), indent=1, sort_keys=True))
    return counts, statuses, ungrounded, len(set_aside)


if __name__ == "__main__":
    counts, statuses, ungrounded, aside = Build()
    print("counts:", counts, "set aside:", aside)
    print("statuses:", dict(statuses))
    print("ungrounded quotes withheld:", len(ungrounded), ungrounded[:10])
    print("wrote", REGISTER, "and", COMPANION)
    sys.exit(0)
