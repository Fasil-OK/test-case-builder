import { readdir, readFile } from "node:fs/promises";
import { pool } from "../src/db.js";

// TODO: track applied migrations in a table; for now every file must be idempotent
for (const file of (await readdir("migrations")).sort()) {
  await pool.query(await readFile(`migrations/${file}`, "utf8"));
  console.log(`applied ${file}`);
}
await pool.end();
