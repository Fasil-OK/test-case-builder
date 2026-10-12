import express from "express";
import { authRouter } from "./routes/auth.js";
import { notesRouter } from "./routes/notes.js";
import { requireAuth } from "./middleware/requireAuth.js";

export const app = express();
app.use(express.json({ limit: "100kb" }));

app.get("/health", (_req, res) => res.json({ ok: true }));
app.use("/auth", authRouter);
app.use("/notes", requireAuth, notesRouter);

if (process.env.NODE_ENV !== "test") {
  const port = process.env.PORT || 3000;
  app.listen(port, () => console.log(`notes-api listening on ${port}`));
}
