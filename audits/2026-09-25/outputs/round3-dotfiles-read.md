# Round 3, the two never-read files (read by the conductor, 2026-10-09)

The corrected coverage (outputs/round1b-coverage-merged.json) leaves exactly two owned files that no auditor read: `.gitattributes` and `.gitignore` (owner: G, gates and package). Both read in full at 485a7d9.

- `.gitattributes`: marks *.npz, *.npy, *.gz, *.png binary and records why the committed artifacts stay out of Git LFS. Its reasoning names "a public research artifact" and a `git log --oneline -- '*/results/*' | wc -l` check as the condition to revisit; at 485a7d9 the remote was public, so the sentence was true when written. No contradiction pair. Design note only: the committed figure suites (822 images) are regenerated per member, which is the churn the comment says would change the answer; nothing on disk contradicts the file.
- `.gitignore`: `.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`. Nothing to contradict.

Findings: none. Both files count as covered.
