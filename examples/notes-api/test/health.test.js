import test from "node:test";
import assert from "node:assert/strict";

process.env.NODE_ENV = "test";
const { app } = await import("../src/server.js");

test("GET /health returns ok", async () => {
  const server = app.listen(0);
  const res = await fetch(`http://localhost:${server.address().port}/health`);
  assert.deepEqual(await res.json(), { ok: true });
  server.close();
});
