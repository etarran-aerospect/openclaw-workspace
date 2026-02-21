import { Router } from "express";
import { z } from "zod";
import { prisma } from "../db.js";

export const eventsRouter = Router();

// Agent events ingest
eventsRouter.post("/agent-events", async (req, res) => {
  const body = z.object({
    agentId: z.string().uuid(),
    type: z.string().min(1),
    payload: z.any()
  }).parse(req.body);

  // Update lastSeen & store event
  await prisma.agent.update({
    where: { id: body.agentId },
    data: { lastSeen: new Date() }
  }).catch(() => { /* ignore */ });

  const ev = await prisma.agentEvent.create({
    data: { agentId: body.agentId, type: body.type, payload: body.payload ?? {} }
  });

  // v0: push stub (log). Later: APNs/FCM fanout based on user tokens.
  console.log("[PUSH_STUB]", body.agentId, body.type);

  res.json({ ok: true, eventId: ev.id });
});
