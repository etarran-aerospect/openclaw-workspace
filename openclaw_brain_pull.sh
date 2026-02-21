#!/usr/bin/env bash
set -euo pipefail

# Safe-by-default sync: OneDrive -> local workspace
# Dry-run unless you pass --apply.

OD_DEFAULT="/mnt/c/Users/seanc/OneDrive/OpenClawWorkspace"
OD="${1:-$OD_DEFAULT}"
WS="$HOME/.openclaw/workspace"

APPLY=0
if [[ "${2:-}" == "--apply" ]] || [[ "${1:-}" == "--apply" ]]; then
  APPLY=1
  # if user passed --apply as $1, shift OD back to default
  if [[ "${1:-}" == "--apply" ]]; then
    OD="$OD_DEFAULT"
  fi
fi

if [[ ! -d "$OD" ]]; then
  echo "ERROR: OneDrive mirror not found: $OD" >&2
  exit 1
fi

mkdir -p "$WS/memory"

STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="$WS/.sync_backups/pull_$STAMP"
mkdir -p "$BACKUP_DIR"

RSYNC_ARGS=(
  -avh
  --checksum
  --itemize-changes
  --no-perms --no-owner --no-group
  --backup --backup-dir "$BACKUP_DIR"
)

if [[ $APPLY -eq 0 ]]; then
  RSYNC_ARGS+=(--dry-run)
fi

FILES=(SOUL.md USER.md MEMORY.md TOOLS.md HEARTBEAT.md AGENTS.md IDENTITY.md)
for f in "${FILES[@]}"; do
  if [[ -f "$OD/$f" ]]; then
    rsync "${RSYNC_ARGS[@]}" "$OD/$f" "$WS/$f"
  fi
done

if [[ -d "$OD/memory" ]]; then
  rsync "${RSYNC_ARGS[@]}" "$OD/memory/" "$WS/memory/" || true
fi

echo "PULL complete ($([[ $APPLY -eq 1 ]] && echo APPLY || echo DRY-RUN))"
echo "  from: $OD"
echo "  to:   $WS"
echo "  backups (if overwrites): $BACKUP_DIR"