# notes-api - Manual Test Cases

- **Generated:** 2026-10-12
- **Revision:** `f949f72` (clean)
- **Scope:** Whole repository

## Summary

| Feature | Cases | P1 | P2 | P3 | Not developed | No unit test |
|---|---|---|---|---|---|---|
| Health check | 1 | 1 | 0 | 0 | 0 | 0 |
| Login | 4 | 2 | 2 | 0 | 0 | 4 |
| Notes | 13 | 8 | 4 | 1 | 0 | 13 |
| **Total** | 18 | 11 | 6 | 1 | 0 | 17 |

## Test environment

- **Requirements:** Node 20 and a Postgres database (`README.md`).
- **Setup:** copy `.env.example` to `.env` and set `DATABASE_URL`, `JWT_SECRET` and `PORT` (default `3000`). Then run `npm install`, `npm run migrate`, `npm run dev`.
- **Base URL:** `http://localhost:3000`
- **Tools:** curl or Postman for the API; `psql` connected to the same database for TC-NOTES-007.
- **Accounts:** two users, **User A** `qa.user.a@example.com` and **User B** `qa.user.b@example.com`, both with password `Qa-Pass-123!`.
  TODO: how test users are created. The API has no registration endpoint and the repo has no seed script, so a row has to be inserted into `users` with a bcrypt hash of the password.
- **Token A / Token B:** the `token` value returned by `POST /auth/login` for User A / User B (steps in TC-AUTH-001). Send it as the header `Authorization: Bearer <token>`.

## Test cases

### Health check

#### TC-HEALTH-001: Health endpoint answers without a token

- **Priority:** P1
- **Type:** Functional
- **Source:** `src/server.js:9`, `test/health.test.js` ("GET /health returns ok")

**Steps**

1. Send `GET /health` with no `Authorization` header.

**Expected result**

1. The response status is `200` and the body is `{"ok":true}`.

### Login

#### TC-AUTH-001: [No unit test] Login with valid credentials returns a token

- **Priority:** P1
- **Type:** Functional
- **Source:** `src/routes/auth.js:8-16`

**Preconditions**

- User A exists.

**Test data**

- Body: `{"email": "qa.user.a@example.com", "password": "Qa-Pass-123!"}`

**Steps**

1. Send `POST /auth/login` with header `Content-Type: application/json` and the body above.
2. Send `GET /notes` with header `Authorization: Bearer <token from step 1>`.

**Expected result**

1. The response status is `200` and the body has a single field `token` holding a non-empty string.
2. The response status is `200`, which shows the token is accepted.

#### TC-AUTH-002: [No unit test] Login is rejected with a wrong password

- **Priority:** P1
- **Type:** Negative
- **Source:** `src/routes/auth.js:12-14`

**Preconditions**

- User A exists.

**Test data**

- Body: `{"email": "qa.user.a@example.com", "password": "Wrong-Pass-999"}`

**Steps**

1. Send `POST /auth/login` with the body above.

**Expected result**

1. The response status is `401` and the body is `{"error":"invalid credentials"}`. No `token` field is returned.

#### TC-AUTH-003: [No unit test] Login for an unregistered email gives the same error as a wrong password

- **Priority:** P2
- **Type:** Security
- **Source:** `src/routes/auth.js:12-14`

**Preconditions**

- No user exists with the email `qa.nobody@example.com`.

**Test data**

- Body: `{"email": "qa.nobody@example.com", "password": "Qa-Pass-123!"}`

**Steps**

1. Send `POST /auth/login` with the body above.

**Expected result**

1. The response status is `401` and the body is `{"error":"invalid credentials"}`, identical to TC-AUTH-002, so the response does not reveal whether the email is registered.

#### TC-AUTH-004: [No unit test] Login is rejected with empty email and password

- **Priority:** P2
- **Type:** Negative
- **Source:** `src/routes/auth.js:9-14`

**Test data**

- Body: `{"email": "", "password": ""}`

**Steps**

1. Send `POST /auth/login` with the body above.

**Expected result**

1. The response status is `401` and the body is `{"error":"invalid credentials"}`.

### Notes

#### TC-NOTES-001: [No unit test] Create a note with a title and a body

- **Priority:** P1
- **Type:** Functional
- **Source:** `src/routes/notes.js:14-21`

**Preconditions**

- You have Token A.

**Test data**

- Body: `{"title": "Test Note 1", "body": "Test body 1"}`

**Steps**

1. Send `POST /notes` with Token A and the body above.
2. Send `GET /notes` with Token A.

**Expected result**

1. The response status is `201`. The body has `id`, `title` = `Test Note 1`, `body` = `Test body 1` and `created_at`.
2. The list contains a note with the `id` from step 1.

#### TC-NOTES-002: [No unit test] Create a note with a title only

- **Priority:** P2
- **Type:** Functional
- **Source:** `src/routes/notes.js:15-21`, `migrations/002_create_notes.sql:5`

**Preconditions**

- You have Token A.

**Test data**

- Body: `{"title": "Test Note 2"}`

**Steps**

1. Send `POST /notes` with Token A and the body above.

**Expected result**

1. The response status is `201`, `title` is `Test Note 2` and `body` is an empty string `""`.

#### TC-NOTES-003: [No unit test] Creating a note without a title is rejected

- **Priority:** P2
- **Type:** Negative
- **Source:** `src/routes/notes.js:16`

**Preconditions**

- You have Token A.

**Test data**

- Body 1: `{"body": "Test body 3"}`
- Body 2: `{"title": "", "body": "Test body 3"}`

**Steps**

1. Send `POST /notes` with Token A and Body 1.
2. Send `POST /notes` with Token A and Body 2.
3. Send `GET /notes` with Token A.

**Expected result**

1. The response status is `400` and the body is `{"error":"title is required"}`.
2. The response status is `400` and the body is `{"error":"title is required"}`.
3. The list contains no note with body `Test body 3`.

#### TC-NOTES-004: [No unit test] Notes are listed newest first

- **Priority:** P1
- **Type:** Functional
- **Source:** `src/routes/notes.js:6-11`, `README.md` (Things that bit us)

**Preconditions**

- You have Token A.

**Test data**

- First body: `{"title": "Order Check Old"}`
- Second body: `{"title": "Order Check New"}`

**Steps**

1. Send `POST /notes` with Token A and the first body.
2. Wait two seconds, then send `POST /notes` with Token A and the second body.
3. Send `GET /notes` with Token A.

**Expected result**

1. The response status is `201`.
2. The response status is `201`.
3. The response status is `200` and the body is a JSON array. `Order Check New` appears before `Order Check Old`, and every item has exactly the fields `id`, `title`, `body` and `created_at`.

#### TC-NOTES-005: [No unit test] A user does not see another user's notes

- **Priority:** P1
- **Type:** Security
- **Source:** `src/routes/notes.js:8-9`

**Preconditions**

- You have Token A and Token B.

**Test data**

- Body: `{"title": "Private Note A"}`

**Steps**

1. Send `POST /notes` with Token A and the body above.
2. Send `GET /notes` with Token B.

**Expected result**

1. The response status is `201`.
2. The response status is `200` and the list contains no note titled `Private Note A`.

#### TC-NOTES-006: [No unit test] Deleting a note removes it from the list

- **Priority:** P1
- **Type:** Functional
- **Source:** `src/routes/notes.js:25-30`, `src/routes/notes.js:8`

**Preconditions**

- You have Token A.
- User A has a note titled `Delete Me 1`; note its `id`.

**Steps**

1. Send `DELETE /notes/<id>` with Token A.
2. Send `GET /notes` with Token A.

**Expected result**

1. The response status is `204` and the body is empty.
2. The list contains no note with that `id`.

#### TC-NOTES-007: [No unit test] A deleted note stays in the database with a deletion time

- **Priority:** P1
- **Type:** Integration
- **Source:** `README.md` (Things that bit us), `src/routes/notes.js:24-28`

**Preconditions**

- You have Token A and `psql` access to the database.
- User A has a note titled `Delete Me 2`; note its `id`.

**Steps**

1. Send `DELETE /notes/<id>` with Token A.
2. In `psql`, run `SELECT id, title, deleted_at FROM notes WHERE id = <id>;`

**Expected result**

1. The response status is `204`.
2. One row is returned. `title` is `Delete Me 2` and `deleted_at` holds the time of step 1, not NULL.

#### TC-NOTES-008: [No unit test] Deleting the same note a second time returns 404

- **Priority:** P2
- **Type:** Negative
- **Source:** `src/routes/notes.js:27-30`

**Preconditions**

- You have Token A.
- User A has a note titled `Delete Me 3`; note its `id`.

**Steps**

1. Send `DELETE /notes/<id>` with Token A.
2. Send the same request again.

**Expected result**

1. The response status is `204`.
2. The response status is `404` and the body is empty.

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

#### TC-NOTES-010: [No unit test] Deleting a note that does not exist returns 404

- **Priority:** P2
- **Type:** Negative
- **Source:** `src/routes/notes.js:27-30`

**Preconditions**

- You have Token A.
- No note has the id `999999999`.

**Steps**

1. Send `DELETE /notes/999999999` with Token A.

**Expected result**

1. The response status is `404` and the body is empty.

#### TC-NOTES-011: [No unit test] Notes endpoints reject a request with no token

- **Priority:** P1
- **Type:** Security
- **Source:** `src/server.js:11`, `src/middleware/requireAuth.js:3-10`

**Test data**

- Body: `{"title": "No Token Note"}`

**Steps**

1. Send `GET /notes` with no `Authorization` header.
2. Send `POST /notes` with no `Authorization` header and the body above.
3. Send `DELETE /notes/1` with no `Authorization` header.

**Expected result**

1. The response status is `401` and the body is `{"error":"unauthorized"}`.
2. The response status is `401` and the body is `{"error":"unauthorized"}`.
3. The response status is `401` and the body is `{"error":"unauthorized"}`.

#### TC-NOTES-012: [No unit test] Notes endpoints reject an invalid token

- **Priority:** P1
- **Type:** Security
- **Source:** `src/middleware/requireAuth.js:4-9`

**Test data**

- Header: `Authorization: Bearer not.a.valid.token`

**Steps**

1. Send `GET /notes` with the header above.

**Expected result**

1. The response status is `401` and the body is `{"error":"unauthorized"}`.

#### TC-NOTES-013: [No unit test] A request body over 100 kB is refused

- **Priority:** P3
- **Type:** Boundary
- **Source:** `src/server.js:7`

**Preconditions**

- You have Token A.

**Test data**

- A JSON body `{"title": "Big Note", "body": "<110,000 letters a>"}`

**Steps**

1. Send `POST /notes` with Token A and the body above.
2. Send `GET /notes` with Token A.

**Expected result**

1. The response status is `413`.
2. The list contains no note titled `Big Note`.

## Not covered

- Token expiry after 7 days (`src/routes/auth.js:16`): needs a 7-day wait or control of the server clock.
- Logout or token revocation: not implemented (`src/routes/auth.js:15`).
- The nightly export job that reads deleted notes: it lives in another repository (`README.md`).
- The migration script and Docker image: operational, no tester-facing behaviour.

## Needs confirmation

- `DELETE /notes/abc` (a non-numeric id): the id goes straight into a query on a BIGINT column (`src/routes/notes.js:26-28`) and the app has no error handler. What should the response be? Read from the code only, not run: the request may never get an answer.
- The same applies to any database failure in `/auth/login` and `/notes`: no error response is defined.
- A title of only spaces (`{"title": "   "}`) passes the check at `src/routes/notes.js:16` and is saved. Intended?
- There is no limit on title length other than the 100 kB body limit. Intended?
- Login with the `email` or `password` field missing altogether (`{}`): the code compares against an undefined email. Expected to be `401`, to be confirmed.
