# OPENCLAW RECOVERY

If the Control UI gets weird, the agent disappears, or you see workspace/session errors like `deactivated_workspace`, do this in order.

## 30-second recovery

1. **Hard refresh the Control UI**
2. Make sure the model is set to:
   - `openai-codex/gpt-5.4`
3. In a shell, run:

```bash
openclaw status
openclaw gateway restart
```

4. Reopen or refresh the Control UI again
5. Send a simple ping like:
   - `helo`
   - `u there?`

## Model note

For this agent, the stable model path is:
- `openai-codex/gpt-5.4`

Avoid switching this agent to:
- `openai/gpt-4o-mini`

Reason: on this install, `openai-codex/...` and `openai/...` are different provider/auth paths. The `openai/...` path can trigger auth mismatch or stale session behavior unless intentionally reconfigured.

## What a healthy status looks like

Run:

```bash
openclaw status
```

You want to see roughly:
- gateway reachable
- gateway service running
- main agent active

## If restart didn’t fix it

Run:

```bash
openclaw logs --plain --local-time --limit 200
```

Things to look for:
- provider/auth errors
- repeated model switch warnings
- gateway reload/restart messages

## Rule of thumb

- **Good:** `openai-codex/gpt-5.4`
- **Suspicious:** `openai/...`

## File location

This file lives in the workspace root so it syncs with the repo and is easy to find from either machine.
