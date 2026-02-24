#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${CONWAY_API_KEY:-}" ]]; then
  echo "ERROR: CONWAY_API_KEY is not set."
  echo "Run: export CONWAY_API_KEY='cnwy_k_...'"
  exit 1
fi

echo "Installing conway-terminal + mcporter..."
npm install -g conway-terminal mcporter

echo "Configuring mcporter server 'conway' (home scope)..."
mcporter config add conway --command conway-terminal --env CONWAY_API_KEY="$CONWAY_API_KEY" --scope home

echo "Verifying Conway tools..."
mcporter list conway --schema >/dev/null

echo "Testing sandbox list..."
mcporter call conway.sandbox_list --output json

echo "Done. Conway MCP is configured for this user."
