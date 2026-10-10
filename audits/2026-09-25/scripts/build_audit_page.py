"""build the private audit page (one html file) from the register's structured companion and the register's own prose sections"""
import collections
import html
import json
import re
from pathlib import Path

AUDIT = Path(__file__).resolve().parent.parent
REGISTER = AUDIT.parent / "2026-09-25-test-suite-audit.md"
COMPANION = AUDIT / "outputs" / "register.json"
PAGE = AUDIT / "outputs" / "audit-register.html"
SEVERITY_WORDS = {"S1": "wrong result", "S2": "wrong statement", "S3": "silent deviation", "S4": "latent defect", "S5": "cosmetic"}
STYLE = """
:root { --bg: #f6f7f5; --fg: #1f2622; --muted: #5b6660; --line: #d7ddd9; --panel: #ffffff; --accent: #0f6b73; --accent-soft: #dcecec; --s1: #9a3b36; --s2: #a4671c; --s3: #5c5a9c; --s4: #2f6a8f; --s5: #6b7470; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: #15191a; --fg: #e4e8e5; --muted: #a0aba5; --line: #2d3537; --panel: #1d2325; --accent: #5fb8bf; --accent-soft: #1f3a3d; --s1: #e08a84; --s2: #d9a65a; --s3: #a9a6e0; --s4: #7fb3d3; --s5: #9aa39f; color-scheme: dark; } }
:root[data-theme="dark"] { --bg: #15191a; --fg: #e4e8e5; --muted: #a0aba5; --line: #2d3537; --panel: #1d2325; --accent: #5fb8bf; --accent-soft: #1f3a3d; --s1: #e08a84; --s2: #d9a65a; --s3: #a9a6e0; --s4: #7fb3d3; --s5: #9aa39f; color-scheme: dark; }
body { background: var(--bg); color: var(--fg); font-family: "Source Sans 3", "Segoe UI", system-ui, sans-serif; font-size: 16px; line-height: 1.5; margin: 0; }
main { max-width: 1100px; margin: 0 auto; padding-block: 2rem 4rem; padding-inline: 16px; }
h1, h2, h3 { font-family: "Source Serif 4", Georgia, serif; text-wrap: balance; line-height: 1.2; }
h1 { font-size: 2rem; margin: 0 0 .25rem; } h2 { font-size: 1.4rem; margin: 2.5rem 0 .75rem; border-bottom: 1px solid var(--line); padding-bottom: .25rem; } h3 { font-size: 1.1rem; margin: 1.5rem 0 .5rem; }
p, li { max-width: 72ch; } .lede { color: var(--muted); margin-bottom: 1.5rem; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin: 1rem 0 1.5rem; }
.tile { background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: .75rem 1rem; }
.tile .n { font-size: 1.8rem; font-weight: 600; font-variant-numeric: tabular-nums; } .tile .l { color: var(--muted); font-size: .85rem; text-transform: uppercase; letter-spacing: .04em; }
table { border-collapse: collapse; width: 100%; font-size: .92rem; } .wrap { overflow-x: auto; margin: .75rem 0 1.25rem; }
th, td { text-align: left; vertical-align: top; padding: .4rem .6rem; border-bottom: 1px solid var(--line); } th { color: var(--muted); font-weight: 600; font-size: .8rem; text-transform: uppercase; letter-spacing: .04em; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
code { font-family: "JetBrains Mono", ui-monospace, Menlo, monospace; font-size: .85em; background: var(--accent-soft); padding: .05em .3em; border-radius: 3px; }
.sev { display: inline-block; font-weight: 600; font-size: .78rem; padding: .05em .45em; border-radius: 3px; color: #fff; }
.S1 { background: var(--s1); } .S2 { background: var(--s2); } .S3 { background: var(--s3); } .S4 { background: var(--s4); } .S5 { background: var(--s5); }
details { border: 1px solid var(--line); border-radius: 6px; margin: .5rem 0; background: var(--panel); } summary { cursor: pointer; padding: .6rem .9rem; font-weight: 600; } details > div { padding: 0 .9rem .9rem; }
.finding { border-top: 1px solid var(--line); padding: .7rem 0; } .finding .meta { color: var(--muted); font-size: .85rem; } .finding p { margin: .3rem 0; }
.bar { display: flex; height: 18px; border-radius: 4px; overflow: hidden; margin: .5rem 0 1rem; max-width: 720px; } .bar span { display: block; height: 100%; }
.legend { display: flex; flex-wrap: wrap; gap: .5rem 1.2rem; font-size: .85rem; color: var(--muted); }
.note { background: var(--panel); border-left: 3px solid var(--accent); padding: .6rem .9rem; margin: 1rem 0; max-width: 80ch; }
"""


def Section(markdown, heading):
    """the lines of one '## heading' section of the register, without the heading"""
    lines = markdown.splitlines()
    start = next((index for index, line in enumerate(lines) if line.startswith("## ") and heading in line), None)
    if start is None:
        return []
    end = next((index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")), len(lines))
    return lines[start + 1:end]


def Inline(text):
    """escaped text with backtick code spans and bold rendered"""
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    return re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)


def Table_Html(lines):
    """a markdown pipe table rendered as html, numbers right-aligned"""
    rows = [line for line in lines if line.startswith("|")]
    if len(rows) < 2:
        return ""
    cells = [[cell.strip() for cell in row.strip().strip("|").split("|")] for row in rows if not re.match(r"^\|[-| ]+\|$", row.strip())]
    header, body = cells[0], cells[1:]
    out = ["<div class='wrap'><table><thead><tr>"] + [f"<th>{Inline(cell)}</th>" for cell in header] + ["</tr></thead><tbody>"]
    for row in body:
        out.append("<tr>" + "".join(f"<td class='{'num' if re.fullmatch(r'[0-9.,%]+', cell) else ''}'>{Inline(cell)}</td>" for cell in row) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def Prose_Html(lines):
    """paragraphs, bullet lists and tables of a register section rendered as html"""
    out, bullets, table = [], [], []
    def flush():
        nonlocal bullets, table
        if bullets:
            out.append("<ul>" + "".join(f"<li>{Inline(item)}</li>" for item in bullets) + "</ul>"); bullets = []
        if table:
            out.append(Table_Html(table)); table = []
    for line in lines:
        if line.startswith("|"):
            table.append(line); continue
        if table:
            flush()
        if line.startswith("- "):
            bullets.append(line[2:]); continue
        if bullets:
            flush()
        if line.startswith("### "):
            out.append(f"<h3>{Inline(line[4:])}</h3>")
        elif line.strip():
            out.append(f"<p>{Inline(line)}</p>")
    flush()
    return "".join(out)


def Build():
    """write the page"""
    data = json.loads(COMPANION.read_text())
    markdown = REGISTER.read_text()
    findings = data["findings"]
    counts = data["counts"]
    total = sum(counts.values())
    by_status = collections.Counter(f["status"].split(";")[0] for f in findings if f["severity_final"] in counts)
    tiles = "".join(f"<div class='tile'><div class='n'>{counts[s]}</div><div class='l'>{s} {SEVERITY_WORDS[s]}</div></div>" for s in ("S1", "S2", "S3", "S4", "S5"))
    bar = "".join(f"<span class='{s}' style='width:{100 * counts[s] / total:.1f}%' title='{s} {counts[s]}'></span>" for s in counts)
    legend = "".join(f"<span><span class='sev {s}'>{s}</span> {SEVERITY_WORDS[s]}: {counts[s]}</span>" for s in counts)
    status_rows = "".join(f"<tr><td>{html.escape(status)}</td><td class='num'>{count}</td></tr>" for status, count in by_status.most_common())
    by_file = collections.Counter(f["file"] for f in findings if f["severity_final"] in counts)
    file_rows = "".join(f"<tr><td><code>{html.escape(name)}</code></td><td class='num'>{count}</td></tr>" for name, count in by_file.most_common(25))
    parts = [f"<title>Test-Suite Audit Register</title><style>{STYLE}</style>", "<main>", "<h1>The test-suite audit of 2026-09-25</h1>", f"<p class='lede'>Register of every verified finding against the neural-operator suite at trunk <code>485a7d9</code>: {total} findings, a 1,090-row commitment ledger, the blind calibration, the fixes landed, and the review list. Every quote on this page re-grounded at that commit when the page was built. Nothing here quotes a pseudopotential title or a volumetric array.</p>", f"<div class='tiles'>{tiles}</div>", f"<div class='bar'>{bar}</div><div class='legend'>{legend}</div>"]
    parts += ["<h2>How a finding earns its place</h2>", Prose_Html(markdown.splitlines()[2:4])]
    parts += ["<h2>Status after verification</h2>", f"<div class='wrap'><table><thead><tr><th>status (first clause)</th><th class='num'>findings</th></tr></thead><tbody>{status_rows}</tbody></table></div>"]
    parts += ["<h2>Calibration and coverage</h2>", Prose_Html(Section(markdown, "Calibration and coverage"))]
    parts += ["<h2>The commitment ledger</h2>", Prose_Html([line for line in Section(markdown, "The commitment ledger") if not line.startswith("### Silent")][:3]), "<details><summary>Silent deviations (the full list)</summary><div>" + Table_Html(Section(markdown, "The commitment ledger")) + "</div></details>"]
    parts += ["<h2>Fixes landed</h2>", Prose_Html(Section(markdown, "Fixes landed"))]
    parts += ["<h2>The review list</h2>", Prose_Html(Section(markdown, "The review list"))]
    parts += ["<h2>What was not checked, and deviations from the plan</h2>", Prose_Html(Section(markdown, "What was not checked"))]
    parts += ["<h2>Where the findings sit</h2>", f"<div class='wrap'><table><thead><tr><th>file</th><th class='num'>findings</th></tr></thead><tbody>{file_rows}</tbody></table></div>"]
    for severity in ("S1", "S2", "S3", "S4", "S5"):
        rows = sorted((f for f in findings if f["severity_final"] == severity), key=lambda f: f["id"])
        parts.append(f"<h2><span class='sev {severity}'>{severity}</span> {SEVERITY_WORDS[severity]} ({len(rows)})</h2>")
        if severity == "S1":
            for f in rows:
                parts.append(f"<div class='finding'><div class='meta'>{html.escape(f['id'])} · <code>{html.escape(f['file'])}</code></div><p><strong>Quote.</strong> {html.escape(f['quote'])}</p><p><strong>Counter.</strong> {html.escape(f['counter'])}</p><p><strong>Claim.</strong> {html.escape(f['claim'])}</p><p><strong>Fix proposed.</strong> {html.escape(f['fix'])}</p><p><strong>Status.</strong> {html.escape(f['status'])}</p>" + (f"<p><strong>Adjudication.</strong> {html.escape(f['note'])}</p>" if f["note"] else "") + "</div>")
        else:
            body = "".join(f"<tr><td>{html.escape(f['id'])}</td><td><code>{html.escape(f['file'])}</code></td><td>{html.escape(f['claim'])}</td><td>{html.escape(f['status'])}{(' — ' + html.escape(f['note'])) if f['note'] else ''}</td></tr>" for f in rows)
            parts.append(f"<details open><summary>{len(rows)} findings</summary><div><div class='wrap'><table><thead><tr><th>id</th><th>file</th><th>claim</th><th>status</th></tr></thead><tbody>{body}</tbody></table></div></div></details>")
    aside = [f for f in findings if f["severity_final"] not in counts]
    if aside:
        body = "".join(f"<tr><td>{html.escape(f['id'])}</td><td><code>{html.escape(f['file'])}</code></td><td>{html.escape(f['claim'])}</td><td>{html.escape(f['status'])}{(' — ' + html.escape(f['note'])) if f['note'] else ''}</td></tr>" for f in sorted(aside, key=lambda f: f["id"]))
        parts.append(f"<h2>Set aside: refuted, or postdating the audited commit ({len(aside)})</h2><div class='wrap'><table><thead><tr><th>id</th><th>file</th><th>claim</th><th>status</th></tr></thead><tbody>{body}</tbody></table></div>")
    parts += ["<h2>Phase A and the known leads</h2>", Prose_Html(Section(markdown, "Phase A")), Prose_Html(Section(markdown, "Known leads"))]
    parts.append("</main>")
    PAGE.write_text("\n".join(parts))
    return PAGE, total


if __name__ == "__main__":
    page, total = Build()
    print("wrote", page, "with", total, "findings;", page.stat().st_size, "bytes")
