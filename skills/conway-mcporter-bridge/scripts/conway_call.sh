#!/usr/bin/env bash
# conway_call.sh — safe-ish wrapper around `conway-mcp call`.
#
# Usage:
#   conway_call.sh <tool_name> [--output json] [key=value ...]
#
# Examples:
#   conway_call.sh credits_balance --output json
#   conway_call.sh sandbox_exec --output json sandbox_id=... command='echo hi'

set -euo pipefail

if [[ ${1:-} == "" || ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  sed -n '1,120p' "$0"
  exit 0
fi

tool="$1"
shift

# Ensure ~/.local/bin is in PATH for non-interactive shells.
export PATH="$HOME/.local/bin:$PATH"

exec conway-mcp call "$tool" "$@"
