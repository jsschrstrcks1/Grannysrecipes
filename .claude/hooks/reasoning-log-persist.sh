#!/bin/bash
# Soli Deo Gloria.
# reasoning-log-persist — Stop hook: a reasoning entry must never die with an
# ephemeral container. If REASONING-LOG.md has uncommitted changes at session
# stop, commit it (ONLY that path — nothing else is swept up) and push.
#
# Deliberately mirrors memory-autopersist.sh: same fail-open contract, same
# narrow add-only-what-was-detected discipline. The reasoning log is the
# human-readable half of continuity, as cognitive memory is the machine half;
# both must survive the container, and neither may sweep up unrelated work.
#
# The commit message carries [no-reasoning] on purpose: this commit contains
# ONLY the log, so requiring the log-guard to pass on it would be circular
# (the guard already exempts log-only commits; the tag is belt and suspenders
# for repos where the guard is installed but the exemption list drifts).
#
# Fail-open contract: ALWAYS exits 0 — a broken push must never block session
# teardown. Failures are loud: logged to /tmp/reasoning-log-persist.err and
# echoed so the transcript shows them.
#
# Kill-switch: REASONING_LOG_PERSIST=0
set +e

[ "${REASONING_LOG_PERSIST:-1}" = "0" ] && exit 0

PROJ="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$PROJ" || exit 0
[ -f "REASONING-LOG.md" ] || exit 0

# Only the reasoning log — never sweep unrelated working-tree changes.
CHANGES=$(git status --porcelain -- REASONING-LOG.md 2>/dev/null)
[ -z "$CHANGES" ] && exit 0

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)

git add -- REASONING-LOG.md 2>>/tmp/reasoning-log-persist.err
git commit -m "docs(reasoning): persist reasoning-log entr(ies) at session stop [no-reasoning]

Automated by .claude/hooks/reasoning-log-persist.sh — the reasoning log is
git-persisted; an entry left uncommitted dies with an ephemeral container.
Only REASONING-LOG.md is included.

Soli Deo Gloria." >>/tmp/reasoning-log-persist.err 2>&1

if git push origin "$BRANCH" >>/tmp/reasoning-log-persist.err 2>&1; then
    echo "[reasoning-log-persist] committed+pushed REASONING-LOG.md on ${BRANCH}"
else
    echo "[reasoning-log-persist] WARNING: committed REASONING-LOG.md on ${BRANCH} but PUSH FAILED — see /tmp/reasoning-log-persist.err; the entry is safe in the local commit only"
fi
exit 0
