# Test case document format

`scripts/md_to_csv.py` reads this format, so keep the heading levels and the bold labels
exactly as shown. Everything else (wording, how many cases, which optional blocks) is yours.

## Skeleton

```markdown
# <Project name> - Manual Test Cases

- **Generated:** <YYYY-MM-DD>
- **Revision:** `<short commit sha>` (<clean | uncommitted changes>), or "not a git repository"
- **Scope:** <Whole repository | the feature or path that was asked for>

## Summary

<leave empty: scripts/md_to_csv.py writes the per-feature table here>

## Test environment

What a tester needs before the first case: how to start or reach the product, the tools
(browser, curl, Postman), the accounts and roles to create. Commands come from the repo's
manifests and docs. Where the repo does not say, write `TODO: <what is missing>`.

## Test cases

### <Feature name>

#### TC-<AREA>-001: <Title>

- **Priority:** P1
- **Type:** Functional
- **Source:** `docs/PRD.md` (requirement id or section), `path/to/file.ext:line`

**Preconditions**

- <state the product must be in before step 1>

**Test data**

- <literal values the steps use>

**Steps**

1. <one action>
2. <one action>

**Expected result**

1. <what the tester observes>

## Not covered

- <area or angle left out, and why: no interface, needs production data, out of scope>

## Needs confirmation

- <question, with the conflicting or missing sources>
```

## Rules for a case

- **Heading:** `#### TC-<AREA>-<NNN>: <Title>`. AREA is uppercase letters or digits, NNN is
  three digits starting at `001` within each area.
- **Title:** the behaviour and the condition, readable on its own in a list of 200.
  "Login is rejected with a wrong password", not "Login test 2".
- **Tag:** `[Not developed]` or `[No unit test]` directly after the colon, spelled exactly
  so because the summary counts them:
  `#### TC-AUTH-005: [Not developed] Password reset link expires after 30 minutes`.
- **Priority, Type, Source** are required. Source points at what the expected result was
  taken from, so a reviewer can check it.
- **Preconditions** and **Test data** are optional; leave the block out when there is
  nothing to say.
- **Preconditions** name a state a second tester can reach and check: which account and
  role, which record. "The user is logged in" does not say as whom. Include whatever makes
  the case repeatable (`No user exists with the email qa.new@example.com`), because the
  same case is run again every cycle.
- **Steps:** numbered, one action each, imperative, with the literal value to type or send.
  Start with the action (`Click`, `Enter`, `Send`), not `Verify` or `Check`: checking
  belongs in the expected result. Name buttons, fields and messages exactly as the product
  shows them, taken from templates, translation files or tests.
- **Expected result:** what the tester sees - text on screen, status code and body, a file
  that appears, a row in a list. Number the items to match the steps when a result belongs
  to a particular step.
- Put commands and values inline in backticks. No fenced code blocks, tables or `---`
  lines inside a case: they do not survive into a spreadsheet cell.
- Empty `Not covered` or `Needs confirmation` sections get a single `- None.` line, so the
  reader knows they were considered.

## Example

```markdown
### Notes

#### TC-NOTES-003: Creating a note without a title is rejected

- **Priority:** P2
- **Type:** Negative
- **Source:** `src/routes/notes.js:31`, `test/notes.test.js` ("rejects empty title")

**Preconditions**

- The API is running at `http://localhost:3000`.
- A user `qa.user@example.com` is registered and you have their access token.

**Test data**

- Body: `{"title": "", "body": "Test body 1"}`

**Steps**

1. Send `POST /notes` with the access token in the `Authorization: Bearer` header and the body above.
2. Send `GET /notes` with the same token.

**Expected result**

1. The response status is `400` and the body is `{"error": "title is required"}`.
2. The list does not contain a note with body `Test body 1`.
```

## CSV columns

`ID, Title, Feature, Priority, Type, Preconditions, Test data, Steps, Expected result,
Source, Status, Actual result, Remarks`

Feature is the `###` heading the case sits under. The last three are left empty for the
tester. The file is UTF-8 with a byte-order mark and every field quoted, so Excel opens it
with multi-line cells intact.
