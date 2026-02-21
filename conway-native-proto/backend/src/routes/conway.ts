import { Router } from "express";

export const conwayRouter = Router();

// GET /api/conway/sandboxes
conwayRouter.get("/conway/sandboxes", async (_req, res) => {
  const apiKey = process.env.CONWAY_API_KEY;
  if (!apiKey) {
    console.warn("[Conway] CONWAY_API_KEY not set");
    return res.status(500).json({ error: "conway_not_configured" });
  }

  const r = await fetch("https://api.conway.tech/v1/sandboxes", {
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
  });

  const json = await r.json();
  if (!r.ok) {
    console.error("[Conway] list failed", r.status, json);
    return res.status(r.status).json({ error: "conway_error", details: json });
  }

  const sandboxes = (json as any).sandboxes ?? (json as any[]);

  const mapped = sandboxes.map((s: any) => ({
    id: s.id ?? s.sandbox_id ?? s.name ?? "unknown",
    name: s.name ?? s.id ?? "Sandbox",
    status: s.status ?? "unknown",
    tier: s.tier ?? s.plan ?? "unknown",
    createdAt: s.created_at ?? s.createdAt ?? new Date().toISOString(),
    terminalUrl: s.terminal_url ?? s.terminalUrl ?? s.url ?? null,
  }));

  res.json({ sandboxes: mapped });
});

// POST /api/conway/sandboxes -> create a new sandbox
conwayRouter.post("/conway/sandboxes", async (_req, res) => {
  const apiKey = process.env.CONWAY_API_KEY;
  if (!apiKey) {
    console.warn("[Conway] CONWAY_API_KEY not set");
    return res.status(500).json({ error: "conway_not_configured" });
  }

  const r = await fetch("https://api.conway.tech/v1/sandboxes", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}), // adjust payload if/when needed
  });

  const json = await r.json();
  if (!r.ok) {
    console.error("[Conway] birth failed", r.status, json);
    return res.status(r.status).json({ error: "conway_error", details: json });
  }

  const s: any = json;

  const mapped = {
    id: s.id ?? s.sandbox_id ?? s.name ?? "unknown",
    name: s.name ?? s.id ?? "Sandbox",
    status: s.status ?? "unknown",
    tier: s.tier ?? s.plan ?? "unknown",
    createdAt: s.created_at ?? s.createdAt ?? new Date().toISOString(),
    terminalUrl: s.terminal_url ?? s.terminalUrl ?? s.url ?? null,
  };

  res.json(mapped);
});
