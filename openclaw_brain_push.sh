#!/usr/bin/env bash
set -euo pipefail

# Safe-by-default sync: local workspace -> OneDrive mirror
# Dry-run unless you pass --apply.

OD_DEFAULT="/mnt/c/Users/seanc/OneDrive/OpenClawWorkspace"
OD="${1:-$OD_DEFAULT}"
WS="$HOME/.openclaw/workspace"

APPLY=0
if [[ "${2:-}" == "--apply" ]] || [[ "${1:-}" == "--apply" ]]; then
  APPLY=1
  if [[ "${1:-}" == "--apply" ]]; then
    OD="$OD_DEFAULT"
  fi
fi

mkdir -p "$OD/memory"

STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="$OD/.sync_backups/push_$STAMP"
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
  if [[ -f "$WS/$f" ]]; then
    rsync "${RSYNC_ARGS[@]}" "$WS/$f" "$OD/$f"
  fi
done

if [[ -d "$WS/memory" ]]; then
  rsync "${RSYNC_ARGS[@]}" "$WS/memory/" "$OD/memory/" || true
fi

echo "PUSH complete ($([[ $APPLY -eq 1 ]] && echo APPLY || echo DRY-RUN))"
echo "  from: $WS"
echo "  to:   $OD"
echo "  backups (if overwrites): $BACKUP_DIR"