"""Convert a test-case Markdown file (format: references/template.md) to CSV.

Usage: python md_to_csv.py docs/qa/TEST_CASES.md

Writes TEST_CASES.csv beside the Markdown, fills the Markdown's "## Summary" section with
a per-feature count table, and prints that table. Status, Actual result and Remarks
already recorded in an existing CSV are kept, matched by case ID.
Exits 1 without writing when the Markdown breaks the format.
"""
import csv
import re
import sys
from collections import Counter
from pathlib import Path

HEADING = r"#### (TC-[A-Z0-9]+-\d{3}): (.+)"
INLINE = ["Priority", "Type", "Source"]
BLOCKS = ["Preconditions", "Test data", "Steps", "Expected result"]
TESTER = ["Status", "Actual result", "Remarks"]  # left blank for the tester
PRIORITIES = ["P1", "P2", "P3"]
TAGS = ["Not developed", "No unit test"]  # title prefixes: "[Not developed] Title"
COLUMNS = ["ID", "Title", "Feature", "Priority", "Type", *BLOCKS, "Source", *TESTER]
REQUIRED = ["Feature", "Priority", "Type", "Steps", "Expected result", "Source"]


def parse(text):
    cases, feature, case, block = [], "", None, None
    for line in text.splitlines():
        if m := re.match(HEADING, line):
            case = dict.fromkeys(COLUMNS, "") | {"ID": m[1], "Title": m[2].strip(), "Feature": feature}
            cases.append(case)
            block = None
        elif re.match(r"#{1,6} ", line):  # any other heading ends the current case
            if line.startswith("### "):
                feature = line[4:].strip()
            elif line.startswith("## "):
                feature = ""
            case = block = None
        elif case is None:
            continue
        elif m := re.match(rf"- \*\*({'|'.join(INLINE)}):\*\* (.+)", line):
            case[m[1]] = m[2].strip()
        elif m := re.match(rf"\*\*({'|'.join(BLOCKS)})\*\*\s*$", line):
            block = m[1]
        elif block and line.strip() and line.strip() != "---":
            case[block] += ("\n" if case[block] else "") + line.strip()
    return cases


def problems(cases, text):
    found = [f"malformed case heading: {h}" for h in re.findall(rf"^(?!{HEADING})#### .*", text, re.M)]
    if not cases:
        found.append("no cases found (expected headings like '#### TC-AUTH-001: Title')")
    if not re.search(r"^## Summary[ \t]*$", text, re.M):
        found.append("missing '## Summary' section (the per-feature table is written there)")
    for key in ("ID", "Title"):  # a repeated title is nearly always a case added twice
        found += [f"duplicate {key}: {v}" for v, n in Counter(c[key] for c in cases).items() if n > 1]
    for c in cases:
        found += [f"{c['ID']}: missing {f}" for f in REQUIRED if not c[f]]
        if c["Priority"] and c["Priority"] not in PRIORITIES:
            found.append(f"{c['ID']}: Priority must be P1, P2 or P3")
        if c["Title"].startswith("[") and not c["Title"].startswith(tuple(f"[{t}] " for t in TAGS)):
            found.append(f"{c['ID']}: unknown tag in title (use {' or '.join(f'[{t}]' for t in TAGS)})")
    return found


def summary(cases):
    def row(label, group):
        counts = [len(group)]
        counts += [sum(c["Priority"] == p for c in group) for p in PRIORITIES]
        counts += [sum(c["Title"].startswith(f"[{t}]") for c in group) for t in TAGS]
        return f"| {label} | " + " | ".join(map(str, counts)) + " |"

    head = ["Feature", "Cases", *PRIORITIES, *TAGS]
    features = dict.fromkeys(c["Feature"] for c in cases)  # document order
    return "\n".join([
        "| " + " | ".join(head) + " |",
        "|" + "---|" * len(head),
        *(row(f, [c for c in cases if c["Feature"] == f]) for f in features),
        row("**Total**", cases),
    ])


def cell(value):
    # Excel and Sheets run a cell that starts with = + - @ as a formula.
    value = re.sub(r"^[-*] ", "• ", value, flags=re.M)
    return "'" + value if value[:1] in ("=", "+", "-", "@") else value


def main(md_path):
    md = Path(md_path)
    text = md.read_text(encoding="utf-8")
    cases = parse(text)
    if found := problems(cases, text):
        sys.exit("Not written - fix the Markdown:\n" + "\n".join(found))

    out = md.with_suffix(".csv")
    old = {}
    if out.exists():
        with out.open(newline="", encoding="utf-8-sig") as f:
            old = {r.get("ID"): r for r in csv.DictReader(f)}
    ids = {c["ID"] for c in cases}
    lost = [i for i, r in old.items() if i not in ids and any(r.get(t) for t in TESTER)]
    if lost:
        sys.exit("Not written - these cases have results recorded in the CSV but are gone "
                 "from the Markdown: " + ", ".join(lost))

    table = summary(cases)
    filled = re.sub(r"(^## Summary[ \t]*\n).*?(?=^## |\Z)", lambda m: f"{m[1]}\n{table}\n\n",
                    text, count=1, flags=re.M | re.S)
    if filled != text:
        with md.open("w", encoding="utf-8", newline="\n") as f:
            f.write(filled)

    with out.open("w", newline="", encoding="utf-8-sig") as f:  # BOM so Excel reads UTF-8
        writer = csv.DictWriter(f, COLUMNS, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for c in cases:
            row = {k: cell(v) for k, v in c.items()}
            row |= {t: old.get(c["ID"], {}).get(t) or "" for t in TESTER}
            writer.writerow(row)

    print(f"{out}: {len(cases)} cases\n{table}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
