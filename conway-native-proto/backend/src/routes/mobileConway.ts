import { Router } from "express";
import { z } from "zod";
import { listSandboxes, provisionSandbox } from "../conwayClient.js";

export const mobileConwayRouter = Router();

/**
 * GET /api/mobile/conway/sandboxes
 * Lists Conway sandboxes for your account.
 */
mobileConwayRouter.get("/mobile/conway/sandboxes", async (_req, res) => {
  try {
    const data = await listSandboxes();
    res.json({
      sandboxes: data.sandboxes ?? [],
      count: data.count ?? (data.sandboxes?.length ?? 0),
    });
  } catch (e: any) {
    console.error("[mobile] listConwaySandboxes failed", e);
    res.status(500).json({ error: e.message ?? "conway_list_failed" });
  }
});

/**
 * POST /api/mobile/conway/sandboxes
 * Body: { name, tier? }
 * Provisions a new Conway sandbox.
 */
mobileConwayRouter.post("/mobile/conway/sandboxes", async (req, res) => {
  const body = z
    .object({
      name: z.string().min(3),
      tier: z.string().optional(),
    })
    .parse(req.body);

  try {
    const sandbox = await provisionSandbox(body);
    res.json({ sandbox });
  } catch (e: any) {
    console.error("[mobile] provisionConwaySandbox failed", e);
    res.status(500).json({ error: e.message ?? "conway_provision_failed" });
  }
});
