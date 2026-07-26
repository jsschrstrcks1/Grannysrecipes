#!/bin/bash
# Soli Deo Gloria.
# memory-autopersist — Stop hook: encoded memories must never die with an
# ephemeral container. If the cognitive store (.memory/) has uncommitted
# changes at session stop, commit them (ONLY .memory paths — nothing else is
# swept up) and push the current branch.
#
# Fail-open contract: ALWAYS exits 0 — a broken push must never block session
# teardown. Failures are loud: logged to /tmp/memory-autopersist.err and
# echoed so the transcript shows them.
#
# Kill-switch: MEMORY_AUTOPERSIST=0
set +e

[ "${MEMORY_AUTOPERSIST:-1}" = "0" ] && exit 0

# Resolve the store repo: this repo if it carries .memory/, else the sibling
# open-claw-stuff (the canonical location memory_ops resolves to).
PROJ="${CLAUDE_PROJECT_DIR:-$(pwd)}"
if [ -d "$PROJ/.memory" ]; then
    STORE="$PROJ"
else
    STORE="$(dirname "$PROJ")/open-claw-stuff"
fi
[ -d "$STORE/.memory" ] || exit 0

cd "$STORE" || exit 0

# Only .memory paths — never sweep unrelated working-tree changes, and add
# ONLY the specific detected files (never lock/tmp sidecars, even if a repo
# lacks the .gitignore rule for them).
CHANGES=$(git status --porcelain -- .memory/ 2>/dev/null | grep -v '\.lock$' | grep -v '\.tmp$')
[ -z "$CHANGES" ] && exit 0

N=$(echo "$CHANGES" | wc -l | tr -d ' ')
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)

echo "$CHANGES" | sed 's/^...//' | while IFS= read -r F; do
    [ -n "$F" ] && git add -- "$F" 2>>/tmp/memory-autopersist.err
done
git commit -m "chore(memory): autopersist ${N} store change(s) at session stop

Automated by .claude/hooks/memory-autopersist.sh — cognitive memory is
git-persisted; an encoded memory left uncommitted dies with an
ephemeral container. Only .memory/ paths are included.

Soli Deo Gloria." >>/tmp/memory-autopersist.err 2>&1

if git push origin "$BRANCH" >>/tmp/memory-autopersist.err 2>&1; then
    echo "[memory-autopersist] committed+pushed ${N} memory change(s) on ${BRANCH}"
else
    echo "[memory-autopersist] WARNING: committed ${N} memory change(s) on ${BRANCH} but PUSH FAILED — see /tmp/memory-autopersist.err; memories are safe in the local commit only"
fi
exit 0
