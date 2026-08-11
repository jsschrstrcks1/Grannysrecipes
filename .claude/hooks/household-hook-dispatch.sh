#!/usr/bin/env bash
# household-hook-dispatch.sh — run a household hook that lives in open-claw-stuff,
# WITHOUT baking one machine's path to open-claw-stuff into this repo's settings.
#
# Why this exists: InTheWake's .claude/settings.json registered the HLS wiring —
# library-preflight-inject.sh (SessionStart + UserPromptSubmit) and
# library-preflight-guard.js (PreToolUse) — with the hardcoded prefix
# /Users/kenbaker/ocs-work/.claude/hooks/... That path is the operator's Mac and
# is DEAD in every container and on any machine whose open-claw-stuff checkout is
# elsewhere. So the HLS preflight never fired here: the catalog held 620
# InTheWake tasks and nothing in the repo made an agent use them. Same disease as
# UL-337/UL-173, one repo over.
#
# This resolves open-claw-stuff by LAYOUT at run time — env override, then the
# sibling checkout relative to THIS repo, then documented hints — and execs the
# named hook from there. A .js target runs under node; anything else under bash.
# stdin is passed through so guards/observers still see the tool payload.
#
# FAIL LOUD, NOT FATAL — household posture, and the injector precedent
# (sophos-inject.sh): if open-claw-stuff cannot be found, say so on stderr,
# name the consequence, give the remedy, and exit 0. The HLS preflight is an
# obligation-injector, not a safety gate; it must never be the thing that breaks
# a session. The real enforcement (dangerous-command guard) stays fail-closed
# in its own hook.
#
# Kill-switch (operator debugging only): HOUSEHOLD_HOOK_DISPATCH=0
# Soli Deo Gloria.
set -u
[ "${HOUSEHOLD_HOOK_DISPATCH:-1}" = "0" ] && exit 0

target="${1:-}"
[ -n "$target" ] || { echo "household-hook-dispatch: no hook name given" >&2; exit 0; }
payload="$(cat 2>/dev/null || true)"

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
selfrepo="$(cd "${here}/../.." >/dev/null 2>&1 && pwd)"

# Candidates are LAYOUTS, never a specific machine. First that exists AND carries
# a marker wins — an empty dir named open-claw-stuff must not satisfy it.
ocs=""
for cand in "${HOUSEHOLD_OCS_ROOT:-}" \
            "${selfrepo}/../open-claw-stuff" \
            "${HOME:-/nonexistent}/open-claw-stuff" \
            "/workspace/open-claw-stuff"; do
  [ -n "$cand" ] || continue
  if [ -d "$cand" ] && [ -e "$cand/.household-library" ] && [ -f "$cand/.claude/hooks/$target" ]; then
    ocs="$(cd "$cand" >/dev/null 2>&1 && pwd)"
    break
  fi
done

if [ -z "$ocs" ]; then
  {
    echo "⛔ HLS UNREACHABLE — open-claw-stuff could not be resolved from $(basename "$selfrepo")."
    echo "   Consequence: the HLS preflight/guard ($target) did NOT run. Work here is UNGOVERNED by"
    echo "   the library — you will not be told if a task is already checked out by another patron."
    echo "   Tried: \$HOUSEHOLD_OCS_ROOT, ${selfrepo}/../open-claw-stuff, \$HOME/open-claw-stuff, /workspace/open-claw-stuff"
    echo "   Remedy: set HOUSEHOLD_OCS_ROOT=<path to open-claw-stuff>, or clone it beside this repo."
  } >&2
  exit 0
fi

hook="$ocs/.claude/hooks/$target"
case "$target" in
  *.js) printf '%s' "$payload" | node "$hook" || true ;;
  *)    printf '%s' "$payload" | bash "$hook" || true ;;
esac
exit 0
