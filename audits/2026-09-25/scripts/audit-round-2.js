export const meta = {
  name: 'audit-round-2',
  description: 'Blind verification of the audit findings: verifiers on every S1-S4 finding, reproducers and defenders on the serious tiers, the known leads, and a coverage critic; every agent on Opus',
  phases: [
    { title: 'Verify', detail: 'blind verifiers, reproducers and defenders over stripped packets' },
    { title: 'Known leads', detail: 'the integrator\'s own leads verified the same way' },
    { title: 'Critic', detail: 'coverage and unresolved ledger rows read from the transcripts' },
  ],
}

const SNAP = '/home/javier/Projects/Physics/Programs/n-Op-audit-baseline'
const SCRATCH = '/home/javier/Projects/Physics/Programs/n-Op-audit-scratch'
const PACKETS = `${SCRATCH}/_packets/round2`

const COMMON = `## Where things are (all read-only)
- The audited snapshot of the repository: ${SNAP}, a git worktree at commit 485a7d9, write-protected. Read repository files only there. History: git -C ${SNAP} log 485a7d9 -- <file>; git -C ${SNAP} show <hash>:<file>; git -C ${SNAP} log --format='%h %aI %s%n%b' 485a7d9 -- <file>. Use only history reachable from 485a7d9 (never --all, never other branches).
- Python, from the snapshot root: cd ${SNAP} && CUDA_VISIBLE_DEVICES= .venv/bin/python -c '...'. The package imports as operators.
- The data: /Pool/VASP_DATA. Read /Pool/VASP_DATA/read-me-first.md first when you touch data; the census (/Pool/VASP_DATA/_census/runs.jsonl and ANSWERS.md) answers most questions about runs. The derived store: /Pool/VASP_DATA/_derived/<campaign>/<id>.npz with a .json sidecar. Training artifacts: /Pool/VASP_DATA/_derived/_training/<member>/ (checkpoints, <run>_manifest.json, <run>_curves.npz). Figure caches: /Pool/VASP_DATA/_derived/_figures/<member>/. All of it is write-protected. Pseudopotential files (POTCAR) are unreadable by design: never open one, and exclude them from every recursive search (grep -r --exclude='POTCAR*').
- Your packet: one JSON file under ${PACKETS}, named in your task. It is the only file there you read.
- Your scratch folder, the only place you may write: ${SCRATCH}/<your label>/ (create it).

## Rules
- Off-limits, do not read, list or search: ~/.claude/, anything under /tmp/claude-*, /home/javier/Projects/Physics/Programs/n-Op-streams/, the live checkout /home/javier/Projects/Physics/Programs/n-Op/, other agents' scratch folders, other packet files, and the web.
- Never run a report generator (python -m operators.<...>.report), a report's Main(), a training driver, Train, Staged_Training, any Write_* function, or any checkpoint loader (Load_Trained_Member, Read_Checkpoint, Latest_Stage_Checkpoint and the like). Reading a manifest or a curves file with json or numpy is fine.
- Tests: single test files only, one at a time: cd ${SNAP} && CUDA_VISIBLE_DEVICES= timeout 300 .venv/bin/python -m pytest -p no:cacheprovider -q operators/tests/<file>. Never the whole suite.
- Keep each command under about two minutes and two gigabytes of memory. If a check needs more, do not run it: say exactly what would decide the item.
- Never write a pseudopotential title (the strings OUTCAR echoes on its TITEL lines) into your output, and nothing from /Pool beyond metric values and run paths.
- Save your final answer as JSON to your scratch folder before returning it (verifiers: verdicts.json; reproducers: reproductions.json; defenders: defenses.json; the critic: critique.json): an interruption loses everything unsaved, and a saved file counts as your return.`

const VERIFY = batch => `You are a blind verifier in an audit of a research repository (a Python package, operators/, of neural operators trained on VASP calculations; a test plan, test-suite.md, specified each member before its code; reports and a results page summarize results). You receive packets: a file, a verbatim quote from it at commit 485a7d9, a claim that the quote is wrong in some stated way, and the claim's negation. You know nothing else: not who made the claim, not their evidence, not how serious they thought it was. For each packet, derive your own evidence from the snapshot, the data and the artifacts, and decide.

${COMMON}

## Your packet
${PACKETS}/${batch}.json. Read it, confirm each quote is in its file at 485a7d9 (search the content, never a line number), then investigate each claim on its own.

## For each item return
- id;
- verdict: claim_holds (the quote is wrong as the claim says), negation_holds (the quote is right and the claim is mistaken), partly (the claim is right in part: say which part), or undetermined (what would decide it, within the limits);
- severity, your own, blind: S1 a wrong number, verdict or data label; S2 a statement that misdescribes code, data or results; S3 a silent deviation from a pre-code document; S4 a latent defect that has not yet produced a wrong number; S5 cosmetic; none if the negation holds;
- evidence: verbatim quotes with their files, or read-only commands with their output; the pointer in the packet is only a hint;
- evidence_commands: the commands that reproduce your evidence.
Your label (for the scratch folder): verify-${batch}`

const REPRODUCE = batch => `You are a reproducer in an audit of a research repository (a Python package, operators/, of neural operators trained on VASP calculations). You receive packets: a file, a verbatim quote at commit 485a7d9, and a claim that a number, verdict or data label in it is wrong. Your job is to reach the quantity each claim is about by a route different from reading the file that states it: from the raw data, the stored arrays, the training manifests, the split files, the floor code, or an independent small computation; and to report what you found, whether or not it agrees with the claim.

${COMMON}

## Your packet
${PACKETS}/${batch}.json.

## For each item return
- id;
- route: what independent source or computation you used;
- value_found: the number, label or fact your route gives;
- reproduced: yes if your route agrees with the claim, no if it agrees with the quoted text, unreachable if your route could not reach it (say why);
- evidence and evidence_commands as verbatim quotes and read-only commands.
Your label (for the scratch folder): reproduce-${batch}`

const DEFEND = batch => `You are the defender in an audit of a research repository (a Python package, operators/, of neural operators trained on VASP calculations; a test plan, test-suite.md, specified each member before its code; each member has IMPLEMENTATION.md, report.md and often results.json; operator-results.md is the results page). You receive packets: a file, a verbatim quote at commit 485a7d9, and a claim that it is wrong or deviates from what was written before the code. Your job is to search for anything that would excuse each item: a reader-facing document that records the change and its reason (test-suite.md as it is now, the member's IMPLEMENTATION.md, its report.md, operator-results.md), or failing that a commit message or a code comment that records it, or a reading under which the quote and the claim are both right.

${COMMON}

## Your packet
${PACKETS}/${batch}.json.

## For each item return
- id;
- excuse: recorded (a reader-facing document states the change and its reason: quote it, with its file), commit_or_comment_only (only a commit message or a code comment records it: quote it), reading (both are right under a reading you state), or none (you searched and found nothing: say what you searched);
- quote, file: the excusing text and where it lives, or empty;
- post_result: true if the recording was written after the affected result existed (compare the commit that wrote the recording with the commit or artifact that produced the result), else false;
- assessment: one sentence on whether the excuse actually covers the claim.
Your label (for the scratch folder): defend-${batch}`

const CRITIC = `You are the coverage critic of an audit of a research repository. You never see the findings. You read ${PACKETS}/coverage.json, which records for every auditor which of its owned files it opened whole, in part, only through a shell command, or never, measured from the auditors' transcripts, and ${PACKETS}/ledger-unresolved.json, which lists the pre-code commitment rows that no resolver classified. Decide what a further round must cover: list every owned file that no auditor read whole or in part, every auditor whose coverage looks thin against its file list, and every unresolved ledger row, grouped into at most twelve round-3 assignments, each a short brief naming the files or rows and what to check. Say plainly if nothing more is needed.

${COMMON}

Return: assignments (array of {name, files, rows, brief}), files_never_read (array of paths), auditors_thin (array of names with one reason each), verdict (one sentence). Your label (for the scratch folder): critic`

const VERDICT_SCHEMA = { type: 'object', properties: { verdicts: { type: 'array', items: { type: 'object', properties: {
  id: { type: 'string' }, verdict: { type: 'string', enum: ['claim_holds', 'negation_holds', 'partly', 'undetermined'] },
  severity: { type: 'string', enum: ['S1', 'S2', 'S3', 'S4', 'S5', 'none'] }, evidence: { type: 'string' },
  evidence_commands: { type: 'array', items: { type: 'string' } } }, required: ['id', 'verdict', 'severity', 'evidence', 'evidence_commands'] } } }, required: ['verdicts'] }
const REPRODUCTION_SCHEMA = { type: 'object', properties: { reproductions: { type: 'array', items: { type: 'object', properties: {
  id: { type: 'string' }, route: { type: 'string' }, value_found: { type: 'string' }, reproduced: { type: 'string', enum: ['yes', 'no', 'unreachable'] },
  evidence: { type: 'string' }, evidence_commands: { type: 'array', items: { type: 'string' } } }, required: ['id', 'route', 'value_found', 'reproduced', 'evidence', 'evidence_commands'] } } }, required: ['reproductions'] }
const DEFENSE_SCHEMA = { type: 'object', properties: { defenses: { type: 'array', items: { type: 'object', properties: {
  id: { type: 'string' }, excuse: { type: 'string', enum: ['recorded', 'commit_or_comment_only', 'reading', 'none'] }, quote: { type: 'string' }, file: { type: 'string' },
  post_result: { type: 'boolean' }, assessment: { type: 'string' } }, required: ['id', 'excuse', 'quote', 'file', 'post_result', 'assessment'] } } }, required: ['defenses'] }
const CRITIQUE_SCHEMA = { type: 'object', properties: {
  assignments: { type: 'array', items: { type: 'object', properties: { name: { type: 'string' }, files: { type: 'array', items: { type: 'string' } }, rows: { type: 'array', items: { type: 'string' } }, brief: { type: 'string' } }, required: ['name', 'files', 'rows', 'brief'] } },
  files_never_read: { type: 'array', items: { type: 'string' } }, auditors_thin: { type: 'array', items: { type: 'string' } }, verdict: { type: 'string' } }, required: ['assignments', 'files_never_read', 'auditors_thin', 'verdict'] }

const OPUS = 'opus'
const batches = args.batches
const leadBatches = args.lead_batches

phase('Verify')
const verified = await pipeline(batches,
  batch => agent(VERIFY(batch.id), { label: `verify:${batch.id}`, phase: 'Verify', schema: VERDICT_SCHEMA, model: OPUS })
    .then(result => ({ batch: batch.id, tier: batch.tier, verdicts: result ? result.verdicts : null })),
  (verified, batch) => {
    const extra = []
    if (batch.tier === 'full') extra.push(agent(REPRODUCE(batch.id), { label: `reproduce:${batch.id}`, phase: 'Verify', schema: REPRODUCTION_SCHEMA, model: OPUS }).then(r => ({ reproductions: r ? r.reproductions : null })))
    if (batch.tier === 'full' || batch.tier === 'defended') extra.push(agent(DEFEND(batch.id), { label: `defend:${batch.id}`, phase: 'Verify', schema: DEFENSE_SCHEMA, model: OPUS }).then(r => ({ defenses: r ? r.defenses : null })))
    return Promise.all(extra).then(results => Object.assign({}, verified, ...results))
  })

phase('Known leads')
const leads = await parallel(leadBatches.map(batch => () =>
  agent(VERIFY(batch.id), { label: `lead:${batch.id}`, phase: 'Known leads', schema: VERDICT_SCHEMA, model: OPUS })
    .then(result => ({ batch: batch.id, verdicts: result ? result.verdicts : null }))))

phase('Critic')
const critique = await agent(CRITIC, { label: 'critic', phase: 'Critic', schema: CRITIQUE_SCHEMA, model: OPUS })

const counted = verified.filter(Boolean)
log(`verified batches: ${counted.length} of ${batches.length}; verdicts: ${counted.reduce((n, v) => n + (v.verdicts ? v.verdicts.length : 0), 0)}; lead batches: ${leads.filter(Boolean).length} of ${leadBatches.length}; critic: ${critique ? critique.verdict : 'none'}`)
return { verified, leads, critique }
