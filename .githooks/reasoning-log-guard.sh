#!/bin/bash
# ============================================================================
# reasoning-log-guard.sh — the RUNTIME-INDEPENDENT half of the reasoning log.
#
# Injection hooks (.claude/hooks/reasoning-log-inject.sh) only reach agents
# whose harness runs Claude Code hooks. Grok, Codex, Hermes, a shell script, a
# human — none of them see that text. But every one of them lands work the same
# way: `git commit`. So the obligation is enforced HERE, where all runtimes
# converge.
#
# RULE: a substantive commit requires a REASONING-LOG.md entry dated today.
#
# Substantive = the commit stages something that is not itself bookkeeping.
# Exempt (never require an entry):
#   • commits that touch ONLY REASONING-LOG.md      (the log's own persistence)
#   • commits that touch ONLY .memory/ or .household-library/  (machine state)
#   • merge commits                                  (no new reasoning authored)
#   • commit message contains [no-reasoning]         (explicit, reviewable opt-out)
#   • REASONING_LOG_GUARD=0                          (operator debugging)
#
# Satisfied by EITHER: REASONING-LOG.md staged in this commit, OR an entry
# already dated today (one session's entry covers its several commits).
#
# Exit 0 = allowed. Exit 1 = blocked with instructions.
# Soli Deo Gloria
# ============================================================================
set -u

[ "${REASONING_LOG_GUARD:-1}" = "0" ] && exit 0

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo .)"
LOG="$REPO_ROOT/REASONING-LOG.md"
TODAY="$(date -u +%Y-%m-%d)"

# A merge in progress authors no new reasoning of its own.
[ -f "$REPO_ROOT/.git/MERGE_HEAD" ] && exit 0

# Explicit opt-out recorded in the commit message itself (reviewable in history).
for mf in "$REPO_ROOT/.git/COMMIT_EDITMSG" "$REPO_ROOT/.git/MERGE_MSG"; do
  [ -f "$mf" ] && grep -qiF '[no-reasoning]' "$mf" && exit 0
done

STAGED="$(git diff --cached --name-only 2>/dev/null)"
[ -z "$STAGED" ] && exit 0

# Is anything staged that is NOT pure bookkeeping?
SUBSTANTIVE=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  case "$f" in
    REASONING-LOG.md|.memory/*|.household-library/*) continue ;;
    *) SUBSTANTIVE=1; break ;;
  esac
done <<< "$STAGED"

[ "$SUBSTANTIVE" -eq 0 ] && exit 0

# Satisfied if the log is part of this commit.
echo "$STAGED" | grep -qxF 'REASONING-LOG.md' && exit 0

# Or if today's entry already exists (one entry covers a session's commits).
if [ -f "$LOG" ] && grep -qE "^## ${TODAY}" "$LOG" 2>/dev/null; then
  exit 0
fi

cat >&2 <<EOF
ERROR [reasoning-log]: this commit changes work but REASONING-LOG.md has no
entry dated ${TODAY}.

  Operator directive (2026-07-30): every runtime — Claude, Grok, Codex, Hermes,
  the household pipeline — records HOW it reached its conclusions and WHY it
  made the calls it made. The log is kept for the operator's own reading.

  Append to ${LOG#$REPO_ROOT/}, newest at the top:

    ## ${TODAY} — <short title>
    **Asked.**    What was requested, and how you read it.
    **Weighed.**  Options considered; what you ruled in/out and why.
    **Decided.**  The call you made, and the reasoning behind it.
    **Unsure.**   Anything uncertain, guessed at, or worth revisiting.

  Be honest: if you guessed, say so. Uncertainty stays on the page.

  Genuinely trivial change? Add [no-reasoning] to the commit message — an
  explicit, reviewable record of that judgment. Operator debugging override:
  REASONING_LOG_GUARD=0.
EOF
exit 1
