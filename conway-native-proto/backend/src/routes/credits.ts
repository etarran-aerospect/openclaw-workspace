import { Router } from "express";
import { z } from "zod";
import { prisma } from "../db.js";

export const creditsRouter = Router();

/**
 * POST /api/validate-receipt
 * Prototype: accepts { email, platform, receipt, amountCents }
 * Adds ledger entry and returns balance.
 */
creditsRouter.post("/validate-receipt", async (req, res) => {
  const body = z.object({
    email: z.string().email(),
    platform: z.enum(["apple", "google"]),
    receipt: z.string().min(3),
    amountCents: z.number().int().positive()
  }).parse(req.body);

  const user = await prisma.user.upsert({
    where: { email: body.email },
    create: { email: body.email },
    update: {}
  });

  const last = await prisma.creditsLedger.findFirst({
    where: { userId: user.id },
    orderBy: { createdAt: "desc" }
  });

  const prevBal = last?.balanceAfterCents ?? 0;
  const newBal = prevBal + body.amountCents;

  await prisma.creditsLedger.create({
    data: {
      userId: user.id,
      type: "purchase",
      amountCents: body.amountCents,
      balanceAfterCents: newBal,
      metadata: { platform: body.platform, receipt: body.receipt }
    }
  });

  res.json({ userId: user.id, balanceCents: newBal });
});

/**
 * GET /api/credits/balance?userId=...
 */
creditsRouter.get("/credits/balance", async (req, res) => {
  const userId = z.string().uuid().parse(req.query.userId);
  const last = await prisma.creditsLedger.findFirst({
    where: { userId },
    orderBy: { createdAt: "desc" }
  });
  res.json({ balanceCents: last?.balanceAfterCents ?? 0 });
});
