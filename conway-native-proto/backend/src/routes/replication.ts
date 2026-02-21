import { Router } from "express";
import { z } from "zod";
import { prisma } from "../db.js";

export const replicationRouter = Router();

// Agent requests permit
replicationRouter.post("/replication/request", async (req, res) => {
  const body = z.object({
    parentAgentId: z.string().uuid(),
    proposedSeedCents: z.number().int().positive(),
    metrics: z.record(z.any()).optional()
  }).parse(req.body);

  // v0 enforcement: cap seed + cap children/week placeholder
  const MAX_SEED = 1000; // $10 seed cap prototype
  const maxSeed = Math.min(body.proposedSeedCents, MAX_SEED);

  const permit = await prisma.replicationPermit.create({
    data: {
      parentAgentId: body.parentAgentId,
      maxSeedCents: maxSeed,
      expiresAt: new Date(Date.now() + 10 * 60 * 1000) // 10 min
    }
  });

  res.json({ permitId: permit.id, maxSeedCents: permit.maxSeedCents, expiresAt: permit.expiresAt.toISOString() });
});

// Complete replication (register child + lineage)
replicationRouter.post("/replication/complete", async (req, res) => {
  const body = z.object({
    permitId: z.string().uuid(),
    childWallet: z.string().min(10),
    sandboxId: z.string().min(2),
    genesisHash: z.string().min(8)
  }).parse(req.body);

  const permit = await prisma.replicationPermit.findUnique({ where: { id: body.permitId } });
  if (!permit) return res.status(404).json({ error: "permit_not_found" });
  if (permit.used) return res.status(409).json({ error: "permit_used" });
  if (permit.expiresAt.getTime() < Date.now()) return res.status(410).json({ error: "permit_expired" });

  const parent = await prisma.agent.findUnique({ where: { id: permit.parentAgentId } });
  if (!parent) return res.status(404).json({ error: "parent_not_found" });

  const child = await prisma.agent.create({
    data: {
      userId: parent.userId,
      walletAddress: body.childWallet,
      sandboxId: body.sandboxId,
      status: "running",
      parentAgentId: parent.id,
      ruleHash: parent.ruleHash
    }
  });

  const lineage = await prisma.lineageRecord.create({
    data: {
      parentAgentId: parent.id,
      childAgentId: child.id,
      permitId: permit.id,
      genesisHash: body.genesisHash
    }
  });

  await prisma.replicationPermit.update({
    where: { id: permit.id },
    data: { used: true }
  });

  res.json({ child, lineage });
});
