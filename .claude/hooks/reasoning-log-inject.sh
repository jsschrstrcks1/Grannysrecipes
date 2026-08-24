#!/bin/bash
# Soli Deo Gloria.
# reasoning-log-inject — the reasoning-log obligation loads itself, every
# session AND every prompt, regardless of which model or runtime is driving.
#
# Operator directive (Ken, 2026-07-30, strengthened same day): the reasoning
# log must fire EVERY time, be MODEL-INDEPENDENT, and capture reasoning from
# ANY agent — Claude, Grok, Codex, Hermes, the household pipeline.
#
# Why a hook and not a skill: a skill loads only when something invokes it, and
# `/model` re-rolls the runtime mid-session. The harness runs this hook itself.
#
# TWO MODES (argv[1], default "session"):
#   session — SessionStart: full obligation + log status. Once per session.
#   prompt  — UserPromptSubmit: ONE terse line. Fires on EVERY request so the
#             obligation cannot drift out of attention in a long session, but
#             stays cheap enough to repeat every turn.
#
# HONEST LIMIT — read before trusting it: this hook GUARANTEES the obligation
# is present in context. It CANNOT guarantee an entry is written; only the
# agent can do that. The mechanical halves are injection (here), persistence
# (reasoning-log-persist.sh), the commit-time guard (.githooks/
# reasoning-log-guard.sh — which DOES block, and covers every runtime that
# commits), and pipeline capture (atlas/server/reasoning-log-capture.mjs —
# which needs no compliance at all). Do not mistake a hook for proof the log
# is current: read the log.
#
# Fail-open: always exits 0. Kill-switch: REASONING_LOG_INJECT=0
set +e

[ "${REASONING_LOG_INJECT:-1}" = "0" ] && exit 0

MODE="${1:-session}"
PROJ="${CLAUDE_PROJECT_DIR:-$(pwd)}"
LOG="$PROJ/REASONING-LOG.md"
TODAY="$(date -u +%Y-%m-%d)"

# SCOPE (2026-08-11). The log obligation is PER-REPO: it belongs to the repo
# being worked on, enforced by that repo's own pre-commit guard. Registered at
# USER level (admin/install-prompt-inject.mjs) this hook fires in EVERY project,
# and un-scoped it told unrelated repos to create a household artifact —
# measured live on the operator's Mac, where driving it with CLAUDE_PROJECT_DIR
# set to ken-recipes-site and code/ printed "create it for this request" on
# every prompt. A standing instruction to seed household files into someone
# else's repo is a widening, not a reminder.
#
# NOT fixed by self-locating from $BASH_SOURCE the way sophos-inject.sh is.
# There the question is "where did Layer 0 ship from" (one answer, the hook's
# own repo); here it is "whose log is this" (the project's). Self-location would
# make this nag about open-claw-stuff's log while you work somewhere else —
# a different wrong answer, not a fix.
#
# INVARIANT (tested): the marker set is a SUPERSET of the commit guard's
# coverage. Wherever .githooks/reasoning-log-guard.sh exists, this hook ALWAYS
# speaks — so it can never fall silent in a repo where a commit would be
# BLOCKED for a missing entry. That is the property that makes gating safe.
#
# HONEST LIMIT — the gate tracks "does the log obligation BIND here", which is
# NOT the same question as "is this a household repo". Measured instance:
# ~/Project-Sophos is a household repo (the doctrine root) and is silenced,
# because it carries no guard, no log, no .household-library, and keeps its
# sophos skill at .claude/skills/ rather than skills/. That is correct for its
# state today — nothing there would block a commit for a missing entry — and it
# self-corrects the moment the guard is installed. But it IS a gap: do not read
# this gate as an inventory of household repos.
# Override with REASONING_LOG_INJECT_ALL_REPOS=1 to restore un-scoped behaviour.
in_scope() {
    [ -f "$PROJ/.githooks/reasoning-log-guard.sh" ] && return 0  # the guard BLOCKS here
    [ -f "$LOG" ]                                   && return 0  # already participating
    [ -d "$PROJ/.household-library" ]               && return 0  # household checkout
    [ -f "$PROJ/skills/sophos/SKILL.md" ]           && return 0  # household skills tree
    return 1
}
if [ "${REASONING_LOG_INJECT_ALL_REPOS:-0}" != "1" ] && ! in_scope; then
    exit 0
fi

# SUPERSET, not a replacement. A sibling landed the block below on main the same
# day, answering the same fault a different way: the gate above stays SILENT where
# the obligation does not bind, and this NAMES the directory when it does. Neither
# subsumes the other — silence is right for someone else's repo, naming is right
# for a household repo whose log genuinely is missing. Ordered gate-first so the
# git subprocess below runs only when the hook is going to speak.
#
# NAME THE DIRECTORY WE LOOKED IN (added 2026-08-11, measured). The log is per-repo,
# so PROJ is the right place to look — but when PROJ is not a repo at all, "does not
# exist yet, create it" is a true statement about a directory the agent should never
# write to. Observed live: with PROJ=$HOME this hook told every turn to create a log,
# while the repo's real one sat a directory away with hundreds of entries.
#
# Deliberately NOT resolving a different root here. A fallback to some other clone's
# log would be worse: an agent working in a household repo that legitimately has no
# log yet would be pointed at a DIFFERENT repo's file. There is no correct per-repo
# answer when PROJ is not a repo — so the fix is to make the ambiguity visible rather
# than to guess. Naming the path costs nothing and makes the fault self-diagnosing.
if git -C "$PROJ" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    WHERE="$PROJ"
else
    WHERE="$PROJ (NOT a git repository — if that is not the repo you are working in, the log you want is elsewhere and this is the wrong place to create one)"
fi

# Dated entries only — the file's own prose sections are also '## ' headers.
entry_count() { grep -cE '^## [0-9]{4}-[0-9]{2}-[0-9]{2}' "$LOG" 2>/dev/null || echo 0; }
has_today()   { grep -qE "^## ${TODAY}" "$LOG" 2>/dev/null; }

if [ "$MODE" = "prompt" ]; then
    # Per-request: one line, and it names the current state so an unwritten log
    # is visible on every single turn rather than once at session start.
    if [ ! -f "$LOG" ]; then
        echo "[reasoning log] REASONING-LOG.md does not exist yet in ${WHERE} — create it for this request (Asked/Weighed/Decided/Unsure). Standing operator directive; applies to every runtime."
    elif has_today; then
        echo "[reasoning log] REASONING-LOG.md has an entry for ${TODAY}. Append another for this request if it carries real reasoning (Asked/Weighed/Decided/Unsure)."
    else
        echo "[reasoning log] REASONING-LOG.md has NO entry for ${TODAY} ($(entry_count) total). Write one for this request before you finish (Asked/Weighed/Decided/Unsure)."
    fi
    exit 0
fi

echo "── reasoning log: session-start obligation injection (automated) ──"

if [ -f "$LOG" ]; then
    LAST=$(grep -m1 -E '^## [0-9]{4}-[0-9]{2}-[0-9]{2}' "$LOG" 2>/dev/null | sed 's/^## //')
    echo "Log: REASONING-LOG.md ($(entry_count) entr(ies); most recent: ${LAST:-none})"
    has_today || echo "NOTE: no entry yet for ${TODAY}."
else
    echo "Log: REASONING-LOG.md does NOT yet exist in ${WHERE} — create it on the"
    echo "first substantive request, using the format below."
fi

cat <<'DIRECTIVE'

STANDING OBLIGATION — every runtime (Claude, Grok, Codex, Hermes, the Sophos/
HELM pipeline), every session, no invocation needed:

  For each substantive request, append an entry to REASONING-LOG.md in this
  repo explaining HOW you reached your conclusion and WHY you made the calls
  you made. Newest entry at the TOP, under the header.

  Format (four parts, kept so the log stays skimmable):
    ## YYYY-MM-DD — <short title>
    **Asked.**    What was requested, and how you read it.
    **Weighed.**  Options and considerations; what you ruled in/out and why.
    **Decided.**  The call you made, and the reasoning behind it.
    **Unsure.**   Anything uncertain, guessed at, or worth revisiting.

  Optionally close with `_Runtime: <name>_` so a reader can tell which agent
  wrote the entry. The pipeline stamps this automatically.

  Substantive = anything with real reasoning behind it. Trivial one-liners are
  skipped deliberately, to keep the log signal rather than noise.

  This is a faithful RECONSTRUCTION of reasoning, not a raw token stream, and
  it must be honest: if you guessed, write that you guessed; if you were
  uncertain, leave the uncertainty on the page. A polished log that hides the
  doubt is the clever shortcut this household forbids. Integrity is doxology.

  ENFORCED, not merely requested: .githooks/reasoning-log-guard.sh BLOCKS a
  substantive commit when the log has no entry for today — from ANY runtime,
  including ones that never read this text. Entries are committed+pushed at
  session stop by .claude/hooks/reasoning-log-persist.sh.
DIRECTIVE

echo "── (Soli Deo Gloria) ──"
exit 0
