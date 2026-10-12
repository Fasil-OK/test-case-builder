---
name: test-case-builder
description: Write manual QC / QA test cases for a project by analyzing its repository - the PRD and docs first, unit tests as a reference for expected behaviour, source code where those leave gaps - and save them to docs/qa/TEST_CASES.md plus a CSV for Excel or a test-management tool. Every case gets an ID, title, priority, type, preconditions, test data, steps, expected result and source; PRD requirements not built yet and behaviour with no unit test are flagged in the title, and the document opens with a per-feature summary. Use this whenever the user asks for manual test cases, QC or QA test cases, a test case document or sheet, test scenarios for testers, a UAT or regression checklist, or says things like "write test cases for this project", "what should QC test", "prepare the test cases for the release" - even if they never say "manual". Not for writing automated test code (unit, integration or end-to-end tests).
---

# Test Case Builder

Write the manual test cases for a project so that a QC tester who has never seen the code
can run them step by step and decide pass or fail without asking anyone.

The skill takes one optional argument: a feature name or a path that narrows the scope.
Without it, cover the whole repository.

## What makes a case usable

Keep these in mind through every step; they decide what is worth writing down.

- **It goes through an interface a tester can reach** - a screen, an HTTP endpoint (curl or
  Postman), a CLI command. "Call `validateEmail()` with an empty string" is a unit test,
  not a QC case.
- **It checks one behaviour, and the expected result is observable.** "Works correctly" is
  not an expected result. "The response is 201 and the note appears in `GET /notes`" is.
- **It stands alone.** Testers run subsets, in any order, on a fresh environment. Whatever
  state a case needs goes in its preconditions, never in "run TC-X-003 first".
- **It gives literal values.** "Enter an invalid email" makes the tester invent data and
  makes two runs incomparable. "Enter `qa.user@` in Email" does not.

## Workflow

### 1. Survey the repo, in this order

1. **Docs** - a PRD or requirements document if the repo has one (look for `PRD*`,
   `requirements*`, `docs/prd/`, `specs/`), README, `docs/`, an OpenAPI file, user guides,
   the changelog, `.env.example` (names only). They say what the product is meant to do,
   in the words a tester will see on screen. A PRD is the strongest of these: read it
   first and cite the requirement in each case's Source. Keep a list of the PRD
   requirements you cannot find in the code: they still get cases, tagged
   `[Not developed]` (step 4).
2. **Tests** - unit, integration and end-to-end test files and their fixtures. Use them as
   a reference only. They are the most precise statement of expected behaviour in the
   repo: which inputs are valid, where the boundaries are, the exact error messages, the
   edge cases the developers worried about. Do not run them and do not turn each one into
   a case. A unit test checks a function; a QC case checks a behaviour through the
   product's interface, so several unit tests usually collapse into one case and tests of
   pure internals produce none. Tests are often incomplete or absent. That never removes
   a case: write it from the docs and the code, and tag it `[No unit test]` (step 4).
3. **Code, where docs and tests leave gaps** - entry points, routes and controllers, forms
   and validation rules, CLI definitions, permission checks, models and migrations (field
   lengths, uniqueness, required columns), config defaults.

Skip dependencies, build output and lockfiles. Do not open real `.env` files or other
secret stores.

While surveying, also note how the product is started and reached (manifest scripts,
README, Docker files); the Test environment section needs it.

### 2. Check there is something to test

- **No source code yet:** with a PRD, write the cases from it, all tagged
  `[Not developed]`. Without one, say so and stop: there is nothing to derive cases from.
- **Nothing a tester can drive** (a library with no UI, API or CLI): tell the user. Write
  cases only if they confirm testers will exercise it some other way, and ask how.
- **The repo already keeps manual test cases in another format or tool export:** do not
  convert or overwrite them. Ask whether to follow that format or create this one beside it.

### 3. List the features

Build the list of user-facing features in scope. For each, note its entry point, its
source files and a short area code for IDs (`AUTH`, `NOTES`, `EXPORT`). Show the user the
list in a few lines, then carry on without waiting.

### 4. Derive the cases

For each feature, walk these angles and write a case wherever the repo shows the behaviour:

- the main flow succeeding
- other valid ways through it (optional fields, alternative inputs)
- each validation rule being broken: required, format, length, uniqueness
- boundaries: minimum, maximum, just outside each, empty
- permissions: not signed in, wrong role, another user's data
- state: duplicates, an item that was deleted, the same action twice, data still there
  after a reload or restart
- failure handling: not found, a dependency that is unavailable
- status workflows (draft, submitted, approved ...): each allowed move, and the forbidden
  ones a user could attempt
- rules that combine conditions (role, plan, status): one case per distinct outcome, not
  one per combination

Skip the angles that do not apply, and do not pad. Every case costs tester time on every
test cycle, so a case that no realistic defect would fail is a loss. Inputs the code
treats the same way need one representative, not a case each: five malformed emails that
hit the same check are one case.

**Check coverage before writing.** Go back over the feature list and, when there is a
PRD, its requirements. Each one has at least one case, or a line under Not covered saying
why not. A requirement that silently has no case reads as "tested" to everyone downstream.

**Priority**

| | Use for |
|---|---|
| **P1** | The product is unusable or unsafe if this fails: core flows, sign-in, data loss, security, money |
| **P2** | Common alternate flows, validation, error handling |
| **P3** | Rare edge cases, cosmetic details |

**Type** - one of `Functional`, `Negative`, `Boundary`, `Security`, `UI`, `Integration`.

**Tags** - put a tag at the start of the title when it applies, so it shows in every
list, filter and export:

| Tag | When |
|---|---|
| `[Not developed]` | The PRD requires the behaviour and the code does not have it. Write the case from the PRD alone, so it is ready when the feature lands. Take the steps only as far as the PRD goes: do not invent screen names, endpoints or messages it does not give |
| `[No unit test]` | The behaviour is in the code and no automated test in the repo exercises it. Manual testing is the only check it gets, which matters when choosing what to run |

A case carries at most one tag; `[Not developed]` already implies there is no test.

### 5. Write the files

Write the Markdown file following [references/template.md](references/template.md). Put
it at `docs/qa/TEST_CASES.md`, or in the folder the repo already uses for QA material.

Then generate the CSV from it:

```sh
python <this skill's folder>/scripts/md_to_csv.py docs/qa/TEST_CASES.md
```

The script writes `TEST_CASES.csv` beside the Markdown, with empty Status, Actual result
and Remarks columns for the tester. It also fills the `## Summary` section at the top of
the Markdown with a table of cases per feature (total, per priority, per tag) and prints
that table; leave the section empty and let the script count, so the numbers cannot
disagree with the cases. It refuses to write when a
case breaks the format; fix what it lists and run it again. Do not write the CSV by hand:
generating it is what keeps the two files identical. Only if Python is not available,
write it by hand with the columns listed in the template and say so in the report.

### 6. Report

Give the paths of both files, the summary table from the script's output, and everything
listed under Not covered and Needs confirmation.

## Rules, and why they exist

**Write only what you verified.** Every expected result, and every screen, field,
endpoint and message a step names, comes from a doc, a test or the code, and the case's
Source says which. A tester files a bug whenever the product
disagrees with the case, so a guessed expected result turns into false bug reports and
then into testers who stop trusting the document. When you cannot establish what should
happen, put the question under Needs confirmation instead of writing a case around a guess.

**When docs and code disagree, report it; do not choose.** List it under Needs
confirmation with both versions and their sources. Which one is right is a product
decision, and it is often the most useful thing this pass finds.

**Change nothing but the two test-case files.** No code fixes, no new automated tests,
and do not start the app or run the test suite. If something looks broken, say so in the
report.

**Use obviously fake test data** (`qa.user@example.com`, `Test Note 1`). Never copy real
names, emails, keys or values from the repo's data or environment files into a case.

**IDs are permanent.** Bug reports and test runs refer to cases by ID for years. Never
renumber, and never reuse the ID of a removed case.

## Running it again

When `TEST_CASES.md` already exists, read it first and update it in place:

- keep every existing case and its ID
- add cases for new behaviour, using the next free number in that area
- correct the steps or expected result of cases whose behaviour changed, and list each
  one in the report with the reason
- for cases whose behaviour no longer exists, do not delete them on your own: list them in
  the report and remove them when the user agrees
- refresh the tags, keeping the ID: drop `[Not developed]` once the code is there and
  rewrite the steps against the real interface; drop `[No unit test]` once a test covers
  the behaviour

Then run the script again. It carries each tester's Status, Actual result and Remarks over
from the existing CSV by case ID, and refuses to drop a case that has results recorded.
