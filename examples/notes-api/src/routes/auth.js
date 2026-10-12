import { Router } from "express";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import { query } from "../db.js";

export const authRouter = Router();

authRouter.post("/login", async (req, res) => {
  const { email, password } = req.body ?? {};
  const { rows } = await query("SELECT id, password_hash FROM users WHERE email = $1", [email]);
  const user = rows[0];
  if (!user || !(await bcrypt.compare(password ?? "", user.password_hash))) {
    return res.status(401).json({ error: "invalid credentials" });
  }
  // HACK: tokens cannot be revoked; there is no server-side session or deny list yet
  res.json({ token: jwt.sign({ id: user.id }, process.env.JWT_SECRET, { expiresIn: "7d" }) });
});
