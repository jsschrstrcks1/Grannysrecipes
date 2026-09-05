#!/bin/bash
# ============================================================================
# check-required-hooks.sh — guard against silent removal of Claude Code hooks
# from .claude/settings.json (including via merges — a merge is how these got
# dropped once, and merges don't go through the Write/Edit tools, so only a
# git pre-commit check that runs during merges can catch it).
#
# Removing a hook on purpose: delete its line from the PROTECTED list below in
# the SAME commit. That edit is the explicit, reviewable record of consent.
#
# Exit 0 = all present. Exit 1 = a protected hook is missing (block).
# Soli Deo Gloria
# ============================================================================
set -u
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo .)"
SETTINGS="$REPO_ROOT/.claude/settings.json"

# Protected hook commands / env flags (substring match — robust to path form
# and JSON reformatting). To retire one, delete its line here in the same commit
# that removes it from settings.json.
PROTECTED=(
  "bootstrap-guard.mjs"
  "bootstrap-stamp-hook.mjs"
  "dangerous-command-guard.mjs"
  "sophos-inject.sh"
  "image-safety-check.sh"
  "post-write-validate.sh"
  "prompt-injection-guard.js"
  "session-pulse-scan.sh"
)

if [ ! -f "$SETTINGS" ]; then
  echo "ERROR [required-hooks]: .claude/settings.json is missing entirely." >&2
  exit 1
fi

missing=()
for cmd in "${PROTECTED[@]}"; do
  grep -qF "$cmd" "$SETTINGS" || missing+=("$cmd")
done

if [ "${#missing[@]}" -gt 0 ]; then
  echo "ERROR [required-hooks]: .claude/settings.json is missing protected hook(s):" >&2
  for m in "${missing[@]}"; do echo "    - $m" >&2; done
  echo "" >&2
  echo "  These must not be dropped without operator consent. If a removal is" >&2
  echo "  intentional, delete the matching line(s) from the PROTECTED list in" >&2
  echo "  .githooks/check-required-hooks.sh in this SAME commit. Otherwise restore" >&2
  echo "  the hook(s) in .claude/settings.json." >&2
  exit 1
fi
exit 0
