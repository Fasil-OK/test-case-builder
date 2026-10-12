# notes-api

Backend for the Notes mobile app. Small on purpose.

## Getting going

You need Node 20 and a Postgres you can point at. Copy `.env.example` to `.env`, fill it in,
then `npm install`, `npm run migrate`, `npm run dev`.

For the staging database ask Priya - credentials are not in any vault yet.

## Things that bit us

- Deleting a note only sets `deleted_at`. The nightly export job (lives in the ops repo, not
  here) depends on those rows still existing. Do not add a hard delete.
- The mobile app relies on `/notes` returning newest first. Changing the order breaks the client.
