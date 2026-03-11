# OpenClaw recovery checklist

Use this when the assistant suddenly loses local file/shell access or seems much less capable than before.

## Primary symptom
- Assistant can chat, but cannot read/write local files, run shell commands, or create folders.

## Most likely cause
`~/.openclaw/openclaw.json` was changed to a restricted tool profile.

Expected setting:

```json
"tools": {
  "profile": "full"
}
```

Restricted setting that caused problems on 2026-03-10:

```json
"tools": {
  "profile": "messaging"
}
```

## Quick checks
Run:

```bash
openclaw status
openclaw gateway status
```

If channels and gateway are healthy but the assistant still cannot access local files/tools, inspect config:

```bash
cat ~/.openclaw/openclaw.json
```

## Valid tool profiles
As confirmed by OpenClaw 2026.3.8:

- `minimal`
- `coding`
- `messaging`
- `full`

Use `full` for normal desktop assistant behavior with local tool access.

## Fix procedure
1. Back up config:

```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak
```

2. Edit config:

```bash
nano ~/.openclaw/openclaw.json
```

3. Set:

```json
"tools": {
  "profile": "full"
}
```

4. Restart gateway:

```bash
openclaw gateway restart
```

5. Start a fresh chat/session and test with something simple:

```text
read SOUL.md
```

or

```text
create a test folder in the workspace
```

## Notes
- This is not mainly a workspace GitHub sync issue.
- `~/.openclaw/openclaw.json` lives outside the workspace repo.
- The issue on 2026-03-10 was most likely caused by onboarding/config reset changing `tools.profile` to `messaging`.

## Optional hardening
After updates, onboarding, or config changes, verify:

```bash
openclaw status
cat ~/.openclaw/openclaw.json
```

Check specifically for:
- `tools.profile: full`
- expected channels connected
- expected auth still present (Telegram, WhatsApp, gog/Google Drive)
