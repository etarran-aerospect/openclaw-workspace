import { Router } from "express";
import { z } from "zod";
import crypto from "crypto";
import { prisma } from "../db.js";
import { signUserToken } from "../auth.js";
import jwt from "jsonwebtoken";

export const agentsRouter = Router();
const JWT_SECRET = process.env.JWT_SECRET ?? "dev-secret";

// 1) Simple login (prototype): POST /api/login {email} -> token + userId
agentsRouter.post("/login", async (req, res) => {
  const body = z.object({ email: z.string().email() }).parse(req.body);
  const user = await prisma.user.upsert({
    where: { email: body.email },
    create: { email: body.email },
    update: {}
  });
  const token = signUserToken(user.id);
  res.json({ token, userId: user.id });
});

// 2) Birth: POST /api/agents { userId, templateId?, ruleConfig? } -> birthTicket
agentsRouter.post("/agents", async (req, res) => {
  const body = z.object({
    userId: z.string().uuid(),
    templateId: z.string().optional(),
    ruleConfig: z.any().optional(),
    birthFeeCents: z.number().int().positive().default(200) // e.g., $2 birth fee
  }).parse(req.body);

  // Deduct birth fee from ledger
  const last = await prisma.creditsLedger.findFirst({
    where: { userId: body.userId },
    orderBy: { createdAt: "desc" }
  });
  const prev = last?.balanceAfterCents ?? 0;
  if (prev < body.birthFeeCents) return res.status(402).json({ error: "insufficient_credits" });

  const newBal = prev - body.birthFeeCents;
  await prisma.creditsLedger.create({
    data: {
      userId: body.userId,
      type: "birth",
      amountCents: -body.birthFeeCents,
      balanceAfterCents: newBal,
      metadata: { templateId: body.templateId ?? null }
    }
  });

  // Create "pending agent" container record? For v0, we issue a birth ticket only.
  const ticketPayload = {
    sub: body.userId,
    templateId: body.templateId ?? null,
    ruleHash: body.ruleConfig ? crypto.createHash("sha256").update(JSON.stringify(body.ruleConfig)).digest("hex") : null
  };
  const birthTicket = jwt.sign(ticketPayload, JWT_SECRET, { expiresIn: "10m" });

  res.json({ birthTicket, balanceCents: newBal });
});

// 3) Register agent: POST /api/agents/register { birthTicket, walletAddress, sandboxId, name? }
agentsRouter.post("/agents/register", async (req, res) => {
  const body = z.object({
    birthTicket: z.string().min(10),
    walletAddress: z.string().min(10),
    sandboxId: z.string().min(2).optional(),
    templateId: z.string().optional(),
    name: z.string().optional() // not stored yet; add later if you want
  }).parse(req.body);

  let payload: any;
  try {
    payload = jwt.verify(body.birthTicket, JWT_SECRET);
  } catch {
    return res.status(401).json({ error: "invalid_birth_ticket" });
  }

  const userId = payload.sub as string;

  const agent = await prisma.agent.create({
    data: {
      userId,
      walletAddress: body.walletAddress,
      sandboxId: body.sandboxId ?? null,
      status: "running",
      templateId: payload.templateId ?? body.templateId ?? null,
      ruleHash: payload.ruleHash ?? null
    }
  });

  // Persist rule config if ticket carried hash? (v0 stores only hash; expand later)
  res.json({ agent });
});

// 4) List agents: GET /api/users/:userId/agents
agentsRouter.get("/users/:userId/agents", async (req, res) => {
  const userId = z.string().uuid().parse(req.params.userId);
  const agents = await prisma.agent.findMany({
    where: { userId },
    orderBy: { createdAt: "desc" }
  });
  res.json({ agents });
});
