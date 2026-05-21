# External Agent Memory Setup

Persistent AeroSpect agent memory lives outside this repo at:

- Windows: C:\AI
- WSL: ~/AI
- OpenClaw workspace symlink: ./AI

The `AI` symlink/folder is intentionally ignored by Git in this workspace. Do not track the symlink in the OpenClaw workspace repo.

The agent should load:

- ./AI/agents/aerospect-agent/startup-context.md

Memory should be backed up separately to a private GitHub repo, OneDrive, or manual zip backups.
