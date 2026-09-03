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
#   - NEVER announces the chain is live unless it can actually run: git silently skips a
#     hook without the execute bit, so "present" is not "runnable" (UL-893)
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

# PRESENT IS NOT RUNNABLE (UL-893, measured 2026-08-12 while validating UL-347).
#
# The gate above asks whether the hook FILE exists. git asks something stricter: it
# silently SKIPS a hook that is not executable — no error, no exit code, no output. So a
# mode-644 pre-commit left this hook printing the full "are live from this commit on"
# banner while the staged dangerous-command scan did not run at all. That is the cardinal
# false-CALM, and on the one boundary the household has decided cannot fail: an agent
# reads "live" and proceeds believing a catastrophic command would be caught.
#
# Measured identically on the pre-UL-347 and post-UL-347 hook, so this is inherited, not
# a regression from that fix. The exec bit is lost in ordinary ways: `cp` without -p,
# unzip, `rsync` without -p, a generated or exported tree, or core.fileMode=false.
#
# Arming stays correct either way — core.hooksPath SHOULD point at .githooks — so the fix
# is not to refuse, it is to stop the ANNOUNCEMENT from outrunning the evidence. We check
# every hook git itself invokes, because the banner names four guards spread across more
# files than pre-commit alone; claiming all four are live while checking one is the same
# error one size smaller.
GIT_INVOKED_HOOKS="pre-commit pre-push commit-msg post-merge"
not_runnable=""
for _name in $GIT_INVOKED_HOOKS; do
  _f="$root/.githooks/$_name"
  if [ -f "$_f" ] && [ ! -x "$_f" ]; then
    not_runnable="${not_runnable:+$not_runnable }$_name"
  fi
done

current="$(git -C "$root" config --get core.hooksPath 2>/dev/null || true)"

if [ -n "$current" ]; then
  # Already set — by the CLI self-heal, by this hook in an earlier session, or by the operator.
  # Never touch it. An operator who points hooksPath somewhere else means it.
  #
  # But do not leave silently when the chain cannot run. This is the LARGER population —
  # a repo armed months ago whose hooks later lost the exec bit — and silence here is the
  # same false-CALM as a wrong banner, only quieter. Absence of a warning is not evidence
  # that the guards are live, so when we know they are not, we say so.
  if [ -n "$not_runnable" ]; then
    echo "[arm-hooks-path] WARNING: core.hooksPath is set, but these hooks are NOT executable" \
         "and git will SKIP them: $not_runnable" >&2
    echo "[arm-hooks-path] The git-side P0 guards are INERT despite being wired." \
         "Run: chmod +x $root/.githooks/*" >&2
  fi
  exit 0
fi

if git -C "$root" config core.hooksPath .githooks 2>/dev/null; then
  # Name the REPOSITORY that was armed, not the directory we were pointed at. When
  # those differ, the difference is the thing a reader most needs to see.
  echo "[arm-hooks-path] core.hooksPath was UNSET in $(basename "$root") → set to .githooks."
  if [ -n "$not_runnable" ]; then
    # Armed, but do NOT claim the chain is live — it demonstrably is not.
    echo "[arm-hooks-path] WARNING: these hooks are NOT executable and git will SKIP them:" \
         "$not_runnable" >&2
    echo "[arm-hooks-path] core.hooksPath is now set, but the git-side P0 guards are STILL INERT." \
         "Run: chmod +x $root/.githooks/*" >&2
  else
    echo "[arm-hooks-path] The git-side P0 guards (dangerous-command staged scan, reasoning-log," \
         "concept-ledger, required-hooks) were INERT until now and are live from this commit on."
  fi
else
  # Could not write config — report, do not block. `node admin/hooks-path-doctor.mjs --heal`
  # is the manual path, and --strict exits 2 for CI.
  echo "[arm-hooks-path] WARNING: core.hooksPath is unset and could not be set in $root." >&2
  echo "[arm-hooks-path] The git-side P0 guards are INERT. Run: node admin/hooks-path-doctor.mjs --heal" >&2
fi

exit 0
