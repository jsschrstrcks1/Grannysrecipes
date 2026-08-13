#!/bin/bash
# arm-hooks-path.sh — SessionStart: bring the git-side P0 guards up before any work happens.
#
# WHY THIS EXISTS (UL-226/227). `git clone` never sets core.hooksPath and never populates
# .git/hooks from the repo — deliberately, because running repo-provided hooks on clone would be a
# security hole. So a fresh checkout has the .githooks chain WIRED IN THE REPO and DEAD IN GIT.
#
# That is not a theory. Measured 2026-08-09 in an isolated clone: the chain prints a
# `concept-ledger-check` line on every run, and a commit with core.hooksPath unset produced none
# while the identical commit armed produced one. The pre-commit guards — dangerous-command staged
# scan, reasoning-log guard, concept-ledger check, required-hooks — simply did not execute.
#
# `admin/library.mjs` already self-heals this, but ONLY when a library command runs. Anyone who
# clones and starts editing never triggers it, and that is exactly the population the original
# finding was about. This hook closes that gap for every agent session, which is the population
# that actually works in these repos.
#
# DISCIPLINE, mirroring the CLI self-heal it complements:
#   - arms ONLY when core.hooksPath is unset — an operator's explicit choice is never overridden
#   - arms ONLY when .githooks/pre-commit actually exists in this repo
#   - LOUD when it acts; silent when there is nothing to do, so it adds no noise to a healthy repo
#   - fail-OPEN: a missing git, a non-repo directory, or any error must never block a session.
#     A session that cannot start is a worse outcome than a session whose guards need one CLI call,
#     and the CLI self-heal and `hooks-path-doctor` both remain as backstops.
#
# Kill-switch for operator debugging: HOOKS_PATH_ARM=0
# Soli Deo Gloria.

set -u

[ "${HOOKS_PATH_ARM:-1}" = "0" ] && exit 0

repo="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Fail-open on anything unexpected: no git, not a repo, no .githooks — say nothing, block nothing.
command -v git >/dev/null 2>&1 || exit 0

# RESOLVE THE REPOSITORY FIRST, and act only on it (UL-347, measured 2026-08-11).
#
# The earlier version tested `$repo/.githooks/pre-commit` but wrote with
# `git -C "$repo" config`, which does not write to `$repo` — it writes to whichever
# repository `$repo` BELONGS to. When `$repo` is not a repository root those are two
# different repositories, and the hook armed the wrong one while printing the banner
# below. Measured: a plain directory carrying `.githooks/pre-commit` under a home
# directory that is itself a git repo set `core.hooksPath` in the HOME repo, where no
# `.githooks` exists, and announced that the guards were live. The tree holding the
# hooks was never armed. Worse than the wrong message: a non-existent hooksPath
# DISABLES hooks rather than falling back to `.git/hooks/`, so an ancestor repo using
# default hooks would have been silently disarmed.
#
# A check and its corresponding action must name the same resolved subject. One
# --show-toplevel does that, and it also fixes an under-arm: pointing the session at a
# SUBDIRECTORY of a real repo used to do nothing, and now correctly arms the repo.
root="$(git -C "$repo" rev-parse --show-toplevel 2>/dev/null || true)"
[ -n "$root" ] || exit 0            # not a repo, or bare (no worktree to guard)
[ -f "$root/.githooks/pre-commit" ] || exit 0

current="$(git -C "$root" config --get core.hooksPath 2>/dev/null || true)"

if [ -n "$current" ]; then
  # Already set — by the CLI self-heal, by this hook in an earlier session, or by the operator.
  # Never touch it. An operator who points hooksPath somewhere else means it.
  exit 0
fi

if git -C "$root" config core.hooksPath .githooks 2>/dev/null; then
  # Name the REPOSITORY that was armed, not the directory we were pointed at. When
  # those differ, the difference is the thing a reader most needs to see.
  echo "[arm-hooks-path] core.hooksPath was UNSET in $(basename "$root") → set to .githooks."
  echo "[arm-hooks-path] The git-side P0 guards (dangerous-command staged scan, reasoning-log," \
       "concept-ledger, required-hooks) were INERT until now and are live from this commit on."
else
  # Could not write config — report, do not block. `node admin/hooks-path-doctor.mjs --heal`
  # is the manual path, and --strict exits 2 for CI.
  echo "[arm-hooks-path] WARNING: core.hooksPath is unset and could not be set in $root." >&2
  echo "[arm-hooks-path] The git-side P0 guards are INERT. Run: node admin/hooks-path-doctor.mjs --heal" >&2
fi

exit 0
