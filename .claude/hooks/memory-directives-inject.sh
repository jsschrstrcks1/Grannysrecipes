#!/bin/bash
# Soli Deo Gloria.
# memory-directives-inject — SessionStart hook: operator law loads itself.
# Injects the K1 DIRECTIVES section (protected + externally authorized policy
# memories) into session context via memory_evidence.py's READ-ONLY listing —
# no recall() call, so nothing in the store is mutated by session startup.
#
# The evidence half of recall stays deliberate (the session recalls for its
# actual task topic, per the sophos skill); directives are the half that must
# never depend on someone remembering to ask.
#
# Fail-open: always exits 0; a broken store must never block session start.
# Kill-switch: MEMORY_DIRECTIVES_INJECT=0
#
# @gate name=memory-directives-inject plane=harness event=SessionStart doc=docs/HOUSEHOLD-LOUD-BOOTSTRAP-REQUIREMENT.md
# @gate-code runtime-missing: node and/or python3 is not on PATH; directive injection cannot run and (for node) every node guard is inert; no directive list is printed over that | remedy: put node and python3 on PATH and start a new session
# @gate-code evidence-script-missing: memory_evidence.py was not found at any candidate path, so operator law is NOT loaded this session (this used to be exit 0 with empty output, indistinguishable from "disabled"; lane E probe 7, 2026-10-11) | remedy: set HOUSEHOLD_OCS_ROOT to an open-claw-stuff checkout, or place open-claw-stuff beside this repo
# @gate-code directive-rule-older: no open-claw-stuff copy of memory_evidence.py was found and ken's older copy chose the directives, so personal or unendorsed records may be shown as law (UL-1482) | remedy: set HOUSEHOLD_OCS_ROOT to an open-claw-stuff checkout, or place open-claw-stuff beside this repo
# @gate-exit 0: always (informational; UNAVAILABLE is a line, never a blocked session)
set +e

[ "${MEMORY_DIRECTIVES_INJECT:-1}" = "0" ] && exit 0

# RUNTIME PRESENT? (plan item 3.7; lane E probe 10.) Checked in bash, first, because bash is the one
# interpreter guaranteed to be here. One loud line, exit 0, and NO directive list over a dead plane.
_missing=""
command -v node    >/dev/null 2>&1 || _missing="node"
command -v python3 >/dev/null 2>&1 || _missing="${_missing:+$_missing and }python3"
if [ -n "$_missing" ]; then
    echo "[memory-directives-inject] UNAVAILABLE code=runtime-missing: $_missing not on PATH; operator directives are NOT loaded this session and every node guard is inert; see docs/HOUSEHOLD-LOUD-BOOTSTRAP-REQUIREMENT.md"
    exit 0
fi

PROJ="${CLAUDE_PROJECT_DIR:-$(pwd)}"
PARENT="$(dirname "$PROJ")"
HOME_DIR="${HOME:-}"
_hookdir="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
_selfroot="$(cd "${_hookdir}/../.." >/dev/null 2>&1 && pwd)"
EVIDENCE=""
FALLBACK=""
# Resolution order (UL-1482, 2026-11-09). open-claw-stuff's admin/memory_evidence.py carries the household
# directive rule: personal records refused, quarantined and refuted ones refused, an endorsement and an
# operator-directive tag required. ken's orchestrator/memory_evidence.py is an older copy whose rule
# has none of that. This list used to try ken's copy second, so a session started in ken loaded operator
# law through the older rule. Which hook ran must not change what counts as law, so every place an
# open-claw-stuff checkout can sit is tried first, and ken's copy is a fallback that says so.
#   1 in-repo admin (this IS open-claw-stuff), 2 operator override $HOUSEHOLD_OCS_ROOT, 3 a child of a
#   multi-root project dir, 4 a sibling checkout, 5 ~/open-claw-stuff, 6 ~/ocs-work, 7 the repo this
#   hook shipped from; only then 8-10 ken's copy (in-repo, sibling, ~/ken).
CANDS="$PROJ/admin/memory_evidence.py
${HOUSEHOLD_OCS_ROOT:-/nonexistent}/admin/memory_evidence.py
$PROJ/open-claw-stuff/admin/memory_evidence.py
$PARENT/open-claw-stuff/admin/memory_evidence.py
$HOME_DIR/open-claw-stuff/admin/memory_evidence.py
$HOME_DIR/ocs-work/admin/memory_evidence.py
${_selfroot:-/nonexistent}/admin/memory_evidence.py"
KEN_CANDS="$PROJ/orchestrator/memory_evidence.py
$PARENT/ken/orchestrator/memory_evidence.py
$HOME_DIR/ken/orchestrator/memory_evidence.py"
while IFS= read -r CAND; do
    [ -n "$CAND" ] && [ -f "$CAND" ] && EVIDENCE="$CAND" && break
done <<EOF
$CANDS
EOF
if [ -z "$EVIDENCE" ]; then
    while IFS= read -r CAND; do
        [ -n "$CAND" ] && [ -f "$CAND" ] && EVIDENCE="$CAND" && FALLBACK=1 && break
    done <<EOF
$KEN_CANDS
EOF
fi
if [ -z "$EVIDENCE" ]; then
    # "not found" used to be exit 0 with nothing printed, the same output as MEMORY_DIRECTIVES_INJECT=0.
    # Operator law silently absent is the false-CALM this household keeps paying for; name it.
    echo "[memory-directives-inject] UNAVAILABLE code=evidence-script-missing: memory_evidence.py not found (tried: $(printf '%s\n%s' "$CANDS" "$KEN_CANDS" | tr '\n' ' ')); operator directives are NOT loaded this session. Remedy: set HOUSEHOLD_OCS_ROOT to an open-claw-stuff checkout, or place open-claw-stuff beside this repo."
    exit 0
fi
if [ -n "$FALLBACK" ]; then
    # Loud, and still exit 0: an older rule is better than no law, but the session must know which rule it got.
    echo "[memory-directives-inject] FALLBACK code=directive-rule-older: no open-claw-stuff checkout found, so operator law below was chosen by ken's older copy ($EVIDENCE), which does not refuse personal records or require an endorsement and directive tag. Remedy: set HOUSEHOLD_OCS_ROOT to an open-claw-stuff checkout, or place open-claw-stuff beside this repo."
fi

# Where python3's stderr goes. This was the fixed path /tmp/memory-directives-inject.err. On a shared
# machine, once another user or job owned that file, the redirect failed before python3 ever ran, so every
# session there read "injection FAILED" and lost operator law. Measured 2026-11-09 on the macOS CI runner,
# where two jobs share /tmp (open-claw-stuff #4708). A per-run file under $TMPDIR cannot be held by anyone
# else; /dev/null is the last resort, and a failure still says so, with no detail file.
ERRF=$(mktemp "${TMPDIR:-/tmp}/memory-directives-inject.XXXXXX" 2>/dev/null) || ERRF=/dev/null

# macOS often lacks GNU timeout; prefer timeout/gtimeout when present, else bare run.
if command -v timeout >/dev/null 2>&1; then
    OUT=$(timeout 20 python3 "$EVIDENCE" directives --limit 15 2>"$ERRF")
    RC=$?
elif command -v gtimeout >/dev/null 2>&1; then
    OUT=$(gtimeout 20 python3 "$EVIDENCE" directives --limit 15 2>"$ERRF")
    RC=$?
else
    OUT=$(python3 "$EVIDENCE" directives --limit 15 2>"$ERRF")
    RC=$?
fi

# Fail-open still means exit 0 (a broken store must never block session start), but a crash here
# used to be indistinguishable from "the store has no directives today": OUT was empty either way,
# and stderr went to a /tmp file nobody reads. That silently drops operator law from the session
# with no trace in context. Say so instead; still exit 0.
if [ "$RC" != "0" ]; then
    echo "── cognitive memory: directive injection FAILED (exit $RC) — operator law may be MISSING this session, not merely empty. Detail: $ERRF ──"
    exit 0
fi
[ -z "$OUT" ] && exit 0

echo "── cognitive memory: session-start directive injection (automated) ──"
echo "$OUT"
echo "── (evidence-tier recall: python3 \"$EVIDENCE\" recall \"<topic>\" — see skills/sophos) ──"
exit 0
