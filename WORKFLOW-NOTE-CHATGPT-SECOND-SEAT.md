# Workflow Note — ChatGPT Second Seat + Claw

## Goal
Use ChatGPT seat #2 for structured first-pass output, then let Claw execute with minimal copy/paste.

## Source of Truth
- Drive folder: `AI-Handoffs`
- Link: https://drive.google.com/drive/folders/12i5sOnnKRZQO3SahByrIG4DZvmMTEnZH
- Key files:
  - `INBOX.md` (ChatGPT first pass)
  - `SPEC.md` (approved plan)
  - `DONE.md` (completion log)

## Fast Daily Flow
1. In ChatGPT seat #2, ask for output in INBOX format.
2. Paste result into `AI-Handoffs/INBOX.md`.
3. Tell Claw: **"Use latest INBOX, create SPEC, execute."**
4. Claw executes and updates `DONE.md`.

## Reusable Prompt for Seat #2
"Create a first-pass handoff in the required INBOX format for this task. Include explicit files/paths, acceptance criteria, risks, and open questions."

## READY_FOR_CLAW meaning
- [ ] Yes, execute now → Claw can proceed.
- [ ] Needs Ethan review first → wait for your approval.

## Guardrails
- Keep one active `request_id` at a time.
- Be explicit with filenames/paths/IDs.
- If uncertain, list assumptions.

## If things drift
- Reset by starting from `INBOX.md` template again.
- Keep Custom Instructions short and strict.
