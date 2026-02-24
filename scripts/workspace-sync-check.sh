#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${1:-$HOME/.openclaw/workspace}"
cd "$REPO_DIR"

echo "== sync-check: $(pwd) =="

BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "branch: $BRANCH"

# Refresh remote refs
if git remote get-url origin >/dev/null 2>&1; then
  git fetch origin --quiet || true
fi

LOCAL=$(git rev-parse HEAD)
UPSTREAM=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || true)

if [[ -n "$UPSTREAM" ]]; then
  REMOTE=$(git rev-parse "$UPSTREAM")
  BASE=$(git merge-base HEAD "$UPSTREAM")

  if [[ "$LOCAL" == "$REMOTE" ]]; then
    AHEAD_BEHIND="up-to-date"
  elif [[ "$LOCAL" == "$BASE" ]]; then
    AHEAD_BEHIND="behind"
  elif [[ "$REMOTE" == "$BASE" ]]; then
    AHEAD_BEHIND="ahead"
  else
    AHEAD_BEHIND="diverged"
  fi

  echo "upstream: $UPSTREAM"
  echo "sync: $AHEAD_BEHIND"
else
  echo "upstream: (none)"
  echo "sync: unknown"
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "working-tree: dirty"
  git status -sb
else
  echo "working-tree: clean"
fi
