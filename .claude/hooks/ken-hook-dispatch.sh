#!/usr/bin/env bash
# ken-hook-dispatch.sh — run a hook that lives in the KEN repo (the personal hub /
# memory host), WITHOUT baking one machine's path to ken into this repo's settings.
#
# Why this exists (UL-173 class, spun off hls-dead-path-hooks-in-9-repos): this repo's
# .claude/settings.json registered ken's Slice 6 observation hook by the hard-coded
# absolute path /home/user/ken/.claude/hooks/observe-tool-use.sh. That path is correct
# on THIS container and DEAD on the operator's Mac and any other layout, so memory
# capture silently stops there — preventable loss of the continuity the hook exists to
# provide. (ken's hook already self-locates ken from BASH_SOURCE once reached; the only
# breakage is the absolute path that names where ken is.)
#
# This resolves ken by LAYOUT at run time — env override, then the sibling checkout
# relative to THIS repo, then documented hints — and execs the named ken hook from
# there. A .py target runs under python3; anything else under bash. stdin is passed
# through so the observation writer still sees the tool payload.
#
# FAIL LOUD, NOT FATAL — matches household-hook-dispatch.sh and ken's own observe hook:
# if ken cannot be found, say so on stderr, name the consequence (memory capture is
# NOT running), give the remedy, and exit 0. Observation must never break a tool call.
#
# Kill-switch (operator debugging only): KEN_HOOK_DISPATCH=0
# Soli Deo Gloria.
set -u
[ "${KEN_HOOK_DISPATCH:-1}" = "0" ] && exit 0

target="${1:-}"
[ -n "$target" ] || { echo "ken-hook-dispatch: no hook name given" >&2; exit 0; }
payload="$(cat 2>/dev/null || true)"

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
selfrepo="$(cd "${here}/../.." >/dev/null 2>&1 && pwd)"

# Candidates are LAYOUTS, never a specific machine. First that exists AND carries a
# ken marker (the memory orchestrator) AND the requested hook wins — an empty or
# unrelated dir named ken must not satisfy it.
ken=""
for cand in "${HOUSEHOLD_KEN_ROOT:-}" \
            "${selfrepo}/../ken" \
            "${HOME:-/nonexistent}/ken" \
            "/workspace/ken"; do
  [ -n "$cand" ] || continue
  if [ -d "$cand" ] && [ -f "$cand/orchestrator/hook_observe.py" ] && [ -f "$cand/.claude/hooks/$target" ]; then
    ken="$(cd "$cand" >/dev/null 2>&1 && pwd)"
    break
  fi
done

if [ -z "$ken" ]; then
  {
    echo "⚠ MEMORY CAPTURE NOT RUNNING — ken could not be resolved from $(basename "$selfrepo")."
    echo "   Consequence: the Slice 6 observation hook ($target) did NOT run. Tool-use in this"
    echo "   repo is NOT being observed into cognitive memory — a continuity gap, not a crash."
    echo "   Tried: \$HOUSEHOLD_KEN_ROOT, ${selfrepo}/../ken, \$HOME/ken, /workspace/ken"
    echo "   Remedy: set HOUSEHOLD_KEN_ROOT=<path to ken>, or clone ken beside this repo."
  } >&2
  exit 0
fi

hook="$ken/.claude/hooks/$target"
case "$target" in
  *.py) printf '%s' "$payload" | python3 "$hook" || true ;;
  *)    printf '%s' "$payload" | bash "$hook" || true ;;
esac
exit 0
