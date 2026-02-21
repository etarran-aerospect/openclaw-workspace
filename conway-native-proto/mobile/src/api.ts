const API = "http://192.168.68.52:8787/api";

export async function login(email: string) {
  const r = await fetch(`${API}/login`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ email })
  });
  if (!r.ok) throw new Error(`login failed ${r.status}`);
  return r.json() as Promise<{ token: string; userId: string }>;
}

export async function validateReceipt(email: string, amountCents: number) {
  const r = await fetch(`${API}/validate-receipt`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ email, platform: "apple", receipt: "TEST_RECEIPT", amountCents })
  });
  if (!r.ok) throw new Error(`receipt failed ${r.status}`);
  return r.json() as Promise<{ userId: string; balanceCents: number }>;
}

export async function getBalance(userId: string) {
  const r = await fetch(`${API}/credits/balance?userId=${encodeURIComponent(userId)}`);
  if (!r.ok) throw new Error(`balance failed ${r.status}`);
  return r.json() as Promise<{ balanceCents: number }>;
}

export async function birthAgent(userId: string, templateId?: string) {
  const r = await fetch(`${API}/agents`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ userId, templateId, birthFeeCents: 200 })
  });
  const json = await r.json();
  if (!r.ok) throw new Error(json?.error ?? `birth failed ${r.status}`);
  return json as { birthTicket: string; balanceCents: number };
}

export async function registerAgent(birthTicket: string, walletAddress: string, sandboxId: string) {
  const r = await fetch(`${API}/agents/register`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ birthTicket, walletAddress, sandboxId })
  });
  const json = await r.json();
  if (!r.ok) throw new Error(json?.error ?? `register failed ${r.status}`);
  return json as { agent: any };
}

export async function listAgents(userId: string) {
  const r = await fetch(`${API}/users/${userId}/agents`);
  if (!r.ok) throw new Error(`list agents failed ${r.status}`);
  return r.json() as Promise<{ agents: any[] }>;
}

// Conway-backed endpoints
export async function listConwaySandboxes() {
  const r = await fetch(`${API}/mobile/conway/sandboxes`);
  const json = await r.json();
  if (!r.ok) throw new Error(json?.error ?? `conway list failed ${r.status}`);
  return json as { sandboxes: any[]; count: number };
}

export async function provisionConwaySandbox(name: string, tier: string = "micro") {
  const r = await fetch(`${API}/mobile/conway/sandboxes`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ name, tier }),
  });
  const json = await r.json();
  if (!r.ok) throw new Error(json?.error ?? `conway provision failed ${r.status}`);
  return json as { sandbox: any };
}

