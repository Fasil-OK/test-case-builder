"""Self-check for skills/test-case-builder/scripts/md_to_csv.py. Run: python test_md_to_csv.py"""
import csv
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "skills/test-case-builder/scripts/md_to_csv.py"
MD = """# Demo - Manual Test Cases

## Summary

stale text the script replaces

## Test cases

### Password reset

#### TC-RESET-001: [Not developed] Reset link expires after 30 minutes

- **Priority:** P2
- **Type:** Functional
- **Source:** `docs/PRD.md` (FR-12)

**Steps**

1. Request a password reset

**Expected result**

1. The link stops working after 30 minutes

### Login

#### TC-AUTH-001: Login succeeds with valid credentials

- **Priority:** P1
- **Type:** Functional
- **Source:** `src/auth.js:10`

**Preconditions**

- A user exists

**Steps**

1. Open /login
2. Submit the form

**Expected result**

- The dashboard opens

## Not covered

- None.
"""


def run(md):
    return subprocess.run([sys.executable, str(SCRIPT), str(md)], capture_output=True, text=True)


def rows(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


with tempfile.TemporaryDirectory() as d:
    md, out = Path(d, "TEST_CASES.md"), Path(d, "TEST_CASES.csv")
    md.write_text(MD, encoding="utf-8")
    assert run(md).returncode == 0
    _, r = rows(out)
    assert (r["ID"], r["Feature"], r["Priority"]) == ("TC-AUTH-001", "Login", "P1")

    # the summary table is written into the Markdown, and a second run changes nothing
    filled = md.read_text(encoding="utf-8")
    assert "stale text" not in filled and filled.count("#### TC-") == 2
    assert "| Password reset | 1 | 0 | 1 | 0 | 1 | 0 |" in filled
    assert "| **Total** | 2 | 1 | 1 | 0 | 1 | 0 |" in filled
    assert run(md).returncode == 0 and md.read_text(encoding="utf-8") == filled
    assert r["Steps"] == "1. Open /login\n2. Submit the form"
    assert r["Preconditions"] == "• A user exists"  # a leading "-" is a formula to Excel
    assert r["Expected result"] == "• The dashboard opens"  # "Not covered" did not leak in

    # tester results survive a regeneration
    r["Status"] = "Pass"
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, r.keys())
        writer.writeheader()
        writer.writerow(r)
    assert run(md).returncode == 0 and rows(out)[1]["Status"] == "Pass"

    # ...and dropping a case that has results is refused, leaving the CSV alone
    md.write_text(MD.replace("TC-AUTH-001", "TC-AUTH-002"), encoding="utf-8")
    assert run(md).returncode == 1 and rows(out)[1]["ID"] == "TC-AUTH-001"

    # broken format is rejected
    for broken in (
        MD.replace("\n**Expected result**\n\n- The", "\n**Expected**\n\n- The"),
        MD.replace("TC-AUTH-001", "TC-auth-1"),
        MD.replace("## Summary", "## Overview"),
        MD.replace("[Not developed]", "[Not Developed]"),
        MD.replace("Login succeeds with valid credentials", "[Not developed] Reset link expires after 30 minutes"),
    ):
        md.write_text(broken, encoding="utf-8")
        assert run(md).returncode == 1

print("ok")
