#!/bin/bash
# session-pulse-scan.sh — SessionStart hook
#
# Scans for an abandoned previous session pulse and prints a recovery
# summary to stdout. If no stale pulse is found, exits silently.
#
# Wired via .claude/settings.json: SessionStart event, no matcher.
# Non-blocking: any failure exits 0 so a broken hook never wedges a session.

set -u

CHECKPOINT="/home/user/ken/orchestrator/checkpoint.py"

if [ ! -f "$CHECKPOINT" ]; then
    exit 0
fi

OUT=$(python3 "$CHECKPOINT" scan 2>/dev/null) || exit 0

# Suppress the "no stale" case; surface anything else.
case "$OUT" in
    *'"stale": false'*) exit 0 ;;
    "") exit 0 ;;
esac

echo "── Stale session detected ──────────────────────────────────────"
echo "$OUT"
echo "────────────────────────────────────────────────────────────────"
exit 0
