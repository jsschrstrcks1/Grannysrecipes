#!/bin/bash
# Soli Deo Gloria.
# memory-directives-inject — SessionStart hook: operator law loads itself.
# Injects the K1 DIRECTIVES section (protected + human-endorsed policy
# memories) into session context via memory_evidence.py's READ-ONLY listing —
# no recall() call, so nothing in the store is mutated by session startup.
#
# The evidence half of recall stays deliberate (the session recalls for its
# actual task topic, per the sophos skill); directives are the half that must
# never depend on someone remembering to ask.
#
# Fail-open: always exits 0; a broken store must never block session start.
# Kill-switch: MEMORY_DIRECTIVES_INJECT=0
set +e

[ "${MEMORY_DIRECTIVES_INJECT:-1}" = "0" ] && exit 0

PROJ="${CLAUDE_PROJECT_DIR:-$(pwd)}"
PARENT="$(dirname "$PROJ")"
EVIDENCE=""
for CAND in "$PROJ/orchestrator/memory_evidence.py" \
            "$PARENT/ken/orchestrator/memory_evidence.py"; do
    [ -f "$CAND" ] && EVIDENCE="$CAND" && break
done
[ -z "$EVIDENCE" ] && exit 0

OUT=$(timeout 20 python3 "$EVIDENCE" directives --limit 15 2>/tmp/memory-directives-inject.err)
[ -z "$OUT" ] && exit 0

echo "── cognitive memory: session-start directive injection (automated) ──"
echo "$OUT"
echo "── (evidence-tier recall for the task topic: python3 ken/orchestrator/memory_evidence.py recall \"<topic>\" — see skills/sophos) ──"
exit 0
