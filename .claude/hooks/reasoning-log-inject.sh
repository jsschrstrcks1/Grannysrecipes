#!/bin/bash
# Soli Deo Gloria.
# reasoning-log-inject — SessionStart hook: the reasoning-log obligation loads
# itself, every session, regardless of which model is running.
#
# Operator directive (Ken, 2026-07-30): the reasoning log must fire EVERY time
# and be MODEL-INDEPENDENT. A skill only loads when something invokes it, and a
# model swap mid-session (/model) re-rolls the runtime — so the obligation
# cannot live in a skill or in one model's good intentions. It lives here: the
# harness executes this hook at session start and injects the text below into
# context, whichever model is driving.
#
# HONEST LIMIT — read this before trusting it: this hook GUARANTEES that the
# obligation is present in context. It CANNOT guarantee the reasoning entry is
# actually written; only the agent can do that. The mechanical half is the
# injection (here) and the persistence (reasoning-log-persist.sh). The writing
# half is compliance. Do not let the presence of a hook be mistaken for proof
# that the log is current — read the log.
#
# Fail-open: always exits 0; a missing log must never block session start.
# Kill-switch: REASONING_LOG_INJECT=0
set +e

[ "${REASONING_LOG_INJECT:-1}" = "0" ] && exit 0

PROJ="${CLAUDE_PROJECT_DIR:-$(pwd)}"
LOG="$PROJ/REASONING-LOG.md"

echo "── reasoning log: session-start obligation injection (automated) ──"

if [ -f "$LOG" ]; then
    # Dated entries only — the file's prose sections are also '## ' headers.
    ENTRIES=$(grep -cE '^## [0-9]{4}-[0-9]{2}-[0-9]{2}' "$LOG" 2>/dev/null || echo 0)
    LAST=$(grep -m1 -E '^## [0-9]{4}-[0-9]{2}-[0-9]{2}' "$LOG" 2>/dev/null | sed 's/^## //')
    echo "Log: REASONING-LOG.md (${ENTRIES} entr(ies); most recent: ${LAST:-none})"
else
    echo "Log: REASONING-LOG.md does NOT yet exist in this repo — create it on the"
    echo "first substantive request, using the format below."
fi

cat <<'DIRECTIVE'

STANDING OBLIGATION — applies to every model, every session, no invocation needed:

  For each substantive request from the operator, append an entry to
  REASONING-LOG.md in this repo explaining HOW you reached your conclusion and
  WHY you made the calls you made. Newest entry at the TOP, under the header.

  Format (four parts, kept so the log stays skimmable):
    ## YYYY-MM-DD — <short title>
    **Asked.**    What was requested, and how you read it.
    **Weighed.**  Options and considerations; what you ruled in/out and why.
    **Decided.**  The call you made, and the reasoning behind it.
    **Unsure.**   Anything uncertain, guessed at, or worth revisiting.

  Substantive = anything with real reasoning behind it. Trivial one-liners are
  skipped deliberately, to keep the log signal rather than noise.

  This is a faithful RECONSTRUCTION of reasoning, not a raw token stream, and
  it must be honest: if you guessed, write that you guessed; if you were
  uncertain, leave the uncertainty on the page. A polished log that hides the
  doubt is the clever shortcut this household forbids. Integrity is doxology.

  Entries are committed+pushed automatically at session stop by
  .claude/hooks/reasoning-log-persist.sh — nothing dies with the container.
DIRECTIVE

echo "── (Soli Deo Gloria) ──"
exit 0
