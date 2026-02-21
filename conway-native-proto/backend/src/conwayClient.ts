import fetch from "node-fetch";

const CONWAY_API_BASE = process.env.CONWAY_API_BASE ?? "https://api.conway.tech";
const CONWAY_API_KEY = process.env.CONWAY_API_KEY;

if (!CONWAY_API_KEY) {
  console.warn("[Conway] CONWAY_API_KEY not set – Conway routes will fail");
}

async function conwayFetch(path: string, init: RequestInit = {}) {
  if (!CONWAY_API_KEY) {
    throw new Error("CONWAY_API_KEY not configured");
  }

  const url = `${CONWAY_API_BASE}${path}`;
  const headers = {
    ...(init.headers || {}),
    Authorization: `Bearer ${CONWAY_API_KEY}`,
    "content-type": "application/json",
  } as Record<string, string>;

  const res = await fetch(url, { ...init, headers });
  const text = await res.text();
  let json: any = null;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    /* ignore non-JSON */
  }
  if (!res.ok) {
    console.error("[Conway] error", res.status, text);
    throw new Error(json?.error ?? `Conway ${res.status}`);
  }
  return json;
}

export async function listSandboxes() {
  const data = await conwayFetch("/v1/sandboxes");
  return data; // { sandboxes, count, source }
}

export interface ProvisionSandboxInput {
  name: string;
  tier?: string; // e.g. "micro"
}

export async function provisionSandbox(input: ProvisionSandboxInput) {
  const body = JSON.stringify({
    name: input.name,
    tier: input.tier ?? "micro",
  });
  const data = await conwayFetch("/v1/sandboxes", {
    method: "POST",
    body,
  });
  return data; // sandbox object
}
