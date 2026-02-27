# How to use AI-Handoffs (Ethan + Claw)

Purpose: minimize copy/paste and keep handoffs robust between ChatGPT seat + Claw instances.

## Folder contents
- `INBOX.md` → first-pass output from ChatGPT
- `SPEC.md` → approved plan before execution
- `DONE.md` → completion log after execution

## Workflow (fast)
1. In ChatGPT, generate output using the template in `INBOX.md`.
2. Paste/update `INBOX.md` with that output.
3. If execution is approved, copy essentials into `SPEC.md` and mark status `approved`.
4. Tell Claw: "Use latest SPEC from AI-Handoffs and execute."
5. After completion, Claw appends summary/results to `DONE.md`.

## Rules that make this robust
- One active `request_id` at a time.
- Always include acceptance criteria.
- Keep file/link paths explicit.
- If blocked, set `status: blocked` in `SPEC.md` with reason.

## Recommended command phrases to me
- "Pull latest INBOX from AI-Handoffs and structure it into SPEC."
- "Execute approved SPEC request_id=<id>."
- "Append completion entry to DONE for request_id=<id>."

## Minimal-copy mode
- You only paste once into `INBOX.md`.
- Everything else happens from shared docs + Claw execution.

## Maintenance
- Weekly: archive old entries from `DONE.md` into dated files if it gets long.
- Keep templates stable so both Claws behave consistently.
