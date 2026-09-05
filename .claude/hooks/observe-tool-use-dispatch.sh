#!/usr/bin/env bash
# observe-tool-use-dispatch.sh — reach the Slice 6 observation hook without
# baking one machine's layout into committed settings.
#
# It replaced a hard-coded `/home/user/ken/.claude/hooks/observe-tool-use.sh`,
# which resolves on a Linux container and NOT on the operator's Mac — while the
# same settings file carried `HOUSEHOLD_OCS_ROOT=/Users/kenbaker/atlas-serve`,
# which resolves on the Mac and not in the container. Two machine-absolute paths
# in one file, each dead on the other machine, both silently (UL-337/UL-173).
#
# FAIL LOUD, NOT FATAL — household posture, operator directive 2026-08-10.
# A missing observation hook must SAY so on stderr; it must never take a session
# down, because observation capture is not a safety gate. Contrast the
# dangerous-command guard, which is fail-CLOSED on purpose: loud is about whether
# it can be missed, fatal is about whether work proceeds. Always exits 0.
#
# Kill-switch (operator debugging only): OBSERVE_TOOL_USE=0
# Soli Deo Gloria.
set -u
[ "${OBSERVE_TOOL_USE:-1}" = "0" ] && exit 0

payload="$(cat 2>/dev/null || true)"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Resolution order, widest-to-narrowest. Every candidate is a LAYOUT, never a
# specific machine: an explicit env override, then the sibling-checkout layout
# relative to this hook, then a repo-local copy.
candidates=()
[ -n "${HOUSEHOLD_KEN_ROOT:-}" ] && candidates+=("$HOUSEHOLD_KEN_ROOT/.claude/hooks/observe-tool-use.sh")
candidates+=("$here/../../../ken/.claude/hooks/observe-tool-use.sh")
candidates+=("$here/observe-tool-use.sh")

for c in "${candidates[@]}"; do
  if [ -f "$c" ]; then
    if ! printf '%s' "$payload" | bash "$c"; then
      echo "⚠ observe-tool-use: observer failed at $c — this observation may be lost." >&2
    fi
    exit 0
  fi
done

# Nothing resolved. Say it plainly, name the consequence, give the remedy — a
# silent no-op here is exactly the defect this file exists to remove.
{
  echo "⚠ observe-tool-use: NOT FOUND — cognitive-memory observation capture is NOT running."
  echo "   Tried:"
  for c in "${candidates[@]}"; do echo "     $c"; done
  echo "   Consequence: this session's tool use is not being observed; memory continuity is degraded,"
  echo "   not broken — recall still works, but nothing new is captured automatically."
  echo "   Remedy: set HOUSEHOLD_KEN_ROOT=<path to the ken checkout>, or place ken beside this repo."
} >&2
exit 0
