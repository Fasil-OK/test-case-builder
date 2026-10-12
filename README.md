<p align="center">
  <img src="assets/logo.svg" width="112" alt="test-case-builder logo">
</p>

<h1 align="center">test-case-builder</h1>

<p align="center">
  <strong>An agent skill that reads your repo and writes the manual test cases QC needs,<br>and flags what it could not verify instead of making it up.</strong>
</p>

<p align="center">
  <a href="https://github.com/Fasil-OK/test-case-builder/stargazers"><img src="https://img.shields.io/github/stars/Fasil-OK/test-case-builder?style=flat" alt="GitHub stars"></a>
  <a href="https://github.com/Fasil-OK/test-case-builder/actions/workflows/tests.yml"><img src="https://github.com/Fasil-OK/test-case-builder/actions/workflows/tests.yml/badge.svg" alt="tests"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT license"></a>
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/Agent%20Skills-compatible-4F46E5" alt="Agent Skills compatible"></a>
</p>

<p align="center">
  <a href="#install">Install</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#what-you-get">What you get</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#tags">Tags</a> ·
  <a href="#example">Example</a> ·
  <a href="#tested">Tested</a>
</p>

---

## Why

Ask a coding agent for "test cases" and you usually get one of two things: automated test
code, or a list of scenarios like "verify that login works" that no tester can actually
run. Hand the job to QC instead and their first week goes to asking developers what the
product is supposed to do.

`test-case-builder` makes the agent read what the repo already knows and write cases a
tester who has never seen the code can run step by step. It has one rule: **an expected
result is written only when the repo has evidence for it.**

- **Reads in order of authority.** The PRD and docs first, unit tests as a reference for exact behaviour, source code where those leave gaps.
- **Written for testers.** Every case goes through a screen, an endpoint or a command, with literal test data and a result you can observe.
- **Says what is not built.** A PRD requirement with no code behind it still gets a case, titled `[Not developed]`.
- **Says what nothing else checks.** Behaviour with no automated test is titled `[No unit test]`.
- **Two files that cannot disagree.** Markdown for review, CSV for Excel or a test-management tool. A script generates the second from the first.

## Install

`test-case-builder` is a plain [Agent Skill](https://agentskills.io): a folder with a
`SKILL.md`. It works in any [agent that supports the format](https://agentskills.io/clients),
including Claude Code, Codex, Cursor, Gemini CLI and GitHub Copilot.

**Any agent**, with the [skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add Fasil-OK/test-case-builder
```

**Claude Code**, as a plugin:

```
/plugin marketplace add Fasil-OK/test-case-builder
/plugin install test-case-builder@test-case-builder
```

**Manual:** copy the [`skills/test-case-builder`](skills/test-case-builder) folder into your
agent's skills directory, for example `~/.claude/skills/`.

The CSV step needs Python 3.9 or newer, with no packages to install.

## Usage

Run it on the whole repo:

```
/test-case-builder
```

Or narrow it to a feature or a path:

```
/test-case-builder checkout
```

Or just ask:

> write the QC test cases for this project
>
> prepare manual test cases for the login module from the PRD
>
> what should QC test before this release?

Installed as a Claude Code plugin, the command is `/test-case-builder:test-case-builder`.

## What you get

Two files in `docs/qa/` (or the folder your repo already uses for QA material):

| File | For |
|---|---|
| `TEST_CASES.md` | Reading and review. Opens with a summary, then the cases grouped by feature |
| `TEST_CASES.csv` | Excel, Google Sheets or a test-management tool. One row per case, with empty Status, Actual result and Remarks columns for the tester |

The document opens with a summary the script counts for you:

| Feature | Cases | P1 | P2 | P3 | Not developed | No unit test |
|---|---|---|---|---|---|---|
| Health check | 1 | 1 | 0 | 0 | 0 | 0 |
| Login | 4 | 2 | 2 | 0 | 0 | 4 |
| Notes | 13 | 8 | 4 | 1 | 0 | 13 |
| **Total** | 18 | 11 | 6 | 1 | 0 | 17 |

And every case looks like this:

```markdown
#### TC-NOTES-009: [No unit test] A user cannot delete another user's note

- **Priority:** P1
- **Type:** Security
- **Source:** `src/routes/notes.js:27-30`

**Preconditions**

- You have Token A and Token B.
- User A has a note titled `Keep Me A`; note its `id`.

**Steps**

1. Send `DELETE /notes/<id>` with Token B.
2. Send `GET /notes` with Token A.

**Expected result**

1. The response status is `404` and the body is empty.
2. The list still contains the note `Keep Me A`.
```

The document ends with two sections that are often the most useful part: **Not covered**
(what was left out, and why) and **Needs confirmation** (where the docs and the code
disagree, or the repo does not say what should happen).

## How it works

1. **Survey the repo**, in this order:

   | Source | Used for |
   |---|---|
   | PRD, requirements, README, `docs/`, OpenAPI | What the product is meant to do, in the words a tester will see |
   | Unit, integration and end-to-end tests | Reference only: valid inputs, boundaries, exact error messages. They are not run and not copied one to one |
   | Source code | The gaps: routes, validation rules, permission checks, field limits, config defaults |

2. **List the features** and give each a short area code for IDs (`AUTH`, `NOTES`).
3. **Derive the cases.** Main flow, alternate flows, each validation rule, boundaries, permissions, state, failure handling, status workflows, and rules that combine conditions.
4. **Check coverage.** Every feature and every PRD requirement has a case, or a line under Not covered saying why not.
5. **Write the Markdown, generate the CSV.** The script validates the format, fills in the summary table and writes the CSV.
6. **Report** the two paths, the summary and the open questions.

## Tags

A tag at the start of a title shows in every list, filter and export:

| Tag | Meaning |
|---|---|
| `[Not developed]` | The PRD requires it and the code does not have it yet. The case is written from the PRD alone, ready for when the feature lands |
| `[No unit test]` | The behaviour is in the code and no automated test exercises it. Manual testing is the only check it gets |

When you run the skill again, a tag is dropped once the feature is built or a test covers
it. The case keeps its ID.

### Rules it follows

- **No guessed expected results.** A tester files a bug whenever the product disagrees with the case, so a guess becomes a false bug report. What cannot be established goes under Needs confirmation.
- **Docs and code disagree? It reports, it does not choose.** Which one is right is a product decision.
- **IDs are permanent.** Bug reports refer to them for years. Cases are never renumbered and IDs are never reused.
- **Tester results survive a re-run.** Status, Actual result and Remarks are carried over from the existing CSV by case ID, and the script refuses to drop a case that has results recorded.
- **No padding.** Inputs the code treats the same way get one representative case, not five.
- **Fake test data only.** `qa.user@example.com`, never a real name, key or value from your environment files.
- **Hands off the code.** It changes the two test-case files and nothing else. It does not start the app or run the test suite.
- **Spreadsheet safe.** Cells that Excel or Sheets would run as a formula are neutralised.

## Example

[`examples/notes-api`](examples/notes-api) is a small Express API with login and notes
endpoints, one unit test and no PRD. The skill's output for it is in
[`docs/qa/TEST_CASES.md`](examples/notes-api/docs/qa/TEST_CASES.md) and
[`TEST_CASES.csv`](examples/notes-api/docs/qa/TEST_CASES.csv): 18 cases across three
features, 17 of them tagged `[No unit test]` because the one test only covers `/health`.

It also raised five questions nobody had written down, among them:

- `DELETE /notes/abc` passes a non-numeric id straight to a numeric database column, and the app has no error handler. What should the response be?
- A title made only of spaces passes validation and is saved. Intended?
- The API has no registration endpoint and no seed script, so how are test users created?

## Tested

- **The CSV script** has a self-check, [`tests/test_md_to_csv.py`](tests/test_md_to_csv.py), that runs on every push: parsing, the summary table, carrying tester results over, and each case where it must refuse to write.
- **The skill itself** has been run once, by its author, on the example above. There is no with-and-without benchmark yet, and the `[Not developed]` path has not been run against a real PRD.

Treat it as a first release. If it writes a case your repo has no evidence for, that is a
bug worth reporting.

## Repository layout

```
skills/test-case-builder/
├── SKILL.md                  workflow and rules
├── references/
│   └── template.md           document layout and case format
└── scripts/
    └── md_to_csv.py          validates the Markdown, fills the summary, writes the CSV
examples/notes-api/           a sample app and the test cases written for it
tests/test_md_to_csv.py       self-check for the script
```

## Contributing

Issues and pull requests are welcome. The most useful report is a case with an expected
result the repo had no evidence for, or a behaviour that should have had a case and did
not. Include the case and the file it should have come from.

## License

[MIT](LICENSE)
