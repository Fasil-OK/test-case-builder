import { Router } from "express";
import { query } from "../db.js";

export const notesRouter = Router();

notesRouter.get("/", async (req, res) => {
  const { rows } = await query(
    "SELECT id, title, body, created_at FROM notes WHERE user_id = $1 AND deleted_at IS NULL ORDER BY created_at DESC",
    [req.user.id]
  );
  res.json(rows);
});

notesRouter.post("/", async (req, res) => {
  const { title, body } = req.body ?? {};
  if (!title) return res.status(400).json({ error: "title is required" });
  const { rows } = await query(
    "INSERT INTO notes (user_id, title, body) VALUES ($1, $2, $3) RETURNING id, title, body, created_at",
    [req.user.id, title, body ?? ""]
  );
  res.status(201).json(rows[0]);
});

// Soft delete: rows are kept for the nightly export, never removed.
notesRouter.delete("/:id", async (req, res) => {
  const { rowCount } = await query(
    "UPDATE notes SET deleted_at = now() WHERE id = $1 AND user_id = $2 AND deleted_at IS NULL",
    [req.params.id, req.user.id]
  );
  res.status(rowCount ? 204 : 404).end();
});
