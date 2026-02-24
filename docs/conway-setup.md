# Conway Setup (Shared, Secret-Safe)

This repo stores a repeatable setup for Conway MCP via `mcporter` without committing API keys.

## Prereqs

- Node/npm installed
- OpenClaw installed

## 1) Install CLIs

```bash
npm install -g conway-terminal mcporter
```

## 2) Set your Conway API key (local shell only)

```bash
export CONWAY_API_KEY="cnwy_k_..."
```

Do **not** commit this key to git.

## 3) Configure mcporter server

```bash
mcporter config add conway --command conway-terminal --env CONWAY_API_KEY="$CONWAY_API_KEY" --scope home
```

## 4) Verify tools are available

```bash
mcporter list conway --schema
```

## 5) Test connectivity

```bash
mcporter call conway.sandbox_list --output json
```

## Optional: one-command bootstrap

Use script in this repo:

```bash
scripts/setup-conway.sh
```

It requires `CONWAY_API_KEY` to be set in your shell.
