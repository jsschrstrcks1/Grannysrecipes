---
name: session-checkpoint
description: "Enforces atomic commits, checkpoint summaries, rate-limit recovery, and safe resume patterns. Writes session pulses + cognitive memory so interrupted sessions can restart cleanly."
version: 2.0.0
---

# Session Checkpoint

*Soli Deo Gloria — we work carefully, in small steps, offering each commit as honest labor.*

## Why This Skill Exists

Claude Code makes many API calls per step. Large edits can exhaust per-minute token budgets, and a rate-limit kill in the middle of a multi-file change loses uncommitted work silently. This skill prevents that with two complementary mechanisms:

1. **Cognitive memory checkpoints** — narrative state for the next session.
2. **Session pulse** — a JSON heartbeat at `<repo>/.claude/state/session-pulse.json` that captures, on every beat, the list of git-uncommitted files. If a session dies before writing a HANDOFF, the next session can scan for stale pulses and see exactly what work was in flight.

The pulse module is `orchestrator/checkpoint.py`. It is pure stdlib, repo-scoped, and has no daemon — the session itself updates the pulse.

## Session Startup Protocol

### 1. Scan for an abandoned previous session

```bash
python3 /home/user/ken/orchestrator/checkpoint.py scan
```

If output is `{"ok": true, "stale": false}` you're clean. If a stale pulse is found you'll get a recovery summary listing the abandoned session's last action, last beat time, and the files that were uncommitted when it died — start work there. The stale pulse is automatically archived to `.claude/state/stale-sessions/`.

### 2. Open a new pulse

```bash
SID=$(python3 /home/user/ken/orchestrator/checkpoint.py new-id)
python3 /home/user/ken/orchestrator/checkpoint.py beat \
  --session "$SID" --action "starting <task>" --context "<short summary>"
```

Keep `$SID` for the rest of the session. Every later beat must use the same id so `beat_count` increments instead of resetting.

### 3. Identify the single target file

Do not load all files simultaneously. Load only what the task requires.

### 4. Write a session intent to cognitive memory

```bash
python3 /home/user/ken/orchestrator/memory_ops.py encode ken insight \
  "Session intent: [task]. Target: [files]. Expected: [outcome]." \
  --tags session,intent,checkpoint
```

### 5. Recall prior session state

```bash
python3 /home/user/ken/orchestrator/memory_ops.py recall "session checkpoint" --domain grannysrecipes --limit 5
```

## Checkpoint Protocol (During Work)

After every logical unit of work do **both**:

**A. Beat the pulse** — refreshes the at-risk-files snapshot.

```bash
python3 /home/user/ken/orchestrator/checkpoint.py beat \
  --session "$SID" --action "edited foo.py: added retry logic"
```

**B. Encode to cognitive memory** — narrative for resume.

```bash
python3 /home/user/ken/orchestrator/memory_ops.py encode ken insight \
  "Checkpoint [N]: Edited [file]. Changed [what]. Still needs [remaining]. Risks: [any]." \
  --tags session,checkpoint
```

### When to checkpoint

- After completing a function or block edit
- Before switching to a second file
- Before any find-and-replace touching multiple locations
- Before modifying critical data structures

## Rate Limit Recovery

When you see `Rate limit reached` or HTTP 429:

1. **Stop.** Do not retry immediately.
2. **Beat one final time** with the recovery state in `--action`:

   ```bash
   python3 /home/user/ken/orchestrator/checkpoint.py beat --session "$SID" \
     --action "RATE LIMIT: paused at <step> in <file>; resume with <next>"
   ```

3. **Encode recovery memory:**

   ```bash
   python3 /home/user/ken/orchestrator/memory_ops.py encode ken decision \
     "RATE LIMIT RECOVERY: Interrupted at [step]. File: [name]. Last clean: [state]. Next step: [action]. Do NOT: [incomplete work]." \
     --tags session,recovery,rate-limit --protected
   ```

4. **Wait 60 seconds** for per-minute limits to reset.
5. **On resume**, run `checkpoint.py scan` first, then recall the recovery memory:

   ```bash
   python3 /home/user/ken/orchestrator/memory_ops.py recall "rate limit recovery" --domain grannysrecipes --limit 3
   ```

## Atomic Commit Rules

- **Single file** per commit
- **Passing state** — file must be valid at commit time
- **Described** — commit message matches checkpoint summary
- **Never commit** half-edited functions or inconsistent state

## Token Conservation

1. Read a file once per session — store what you need in checkpoints
2. Edit precisely — targeted str_replace, not full-file rewrites
3. Don't verify by re-reading — reason about the change
4. One concern per session — log discovered issues for next session
5. Keep responses short — the context window is shared with skills

## End of Session

1. Write/update `HANDOFF.md` if work is incomplete (per the format in CLAUDE.md).
2. Encode the final checkpoint to cognitive memory (use `--protected` if it's foundational).
3. **Mark the pulse complete** so the next session doesn't flag it as abandoned:

   ```bash
   python3 /home/user/ken/orchestrator/checkpoint.py complete --session "$SID"
   ```

4. Confirm all touched files are consistent.

## Pulse File Reference

Path: `<repo>/.claude/state/session-pulse.json` (per-repo, atomic single-writer).

```json
{
  "session_id": "sess-20260428T015432Z-ac3592",
  "started_at": "2026-04-28T01:54:32+00:00",
  "last_beat":  "2026-04-28T01:54:41+00:00",
  "beat_count": 2,
  "status":     "active",        // "active" | "complete"
  "last_action": "edited foo.py",
  "context":     "refactoring retry logic",
  "files_in_play": ["foo.py"],   // optional, set explicitly via --files
  "at_risk":     ["foo.py", "bar.py"]  // git-uncommitted, recomputed each beat
}
```

Stale threshold: 30 minutes since `last_beat` with `status != "complete"`.
Stale archive: `<repo>/.claude/state/stale-sessions/<utc-timestamp>-<session-id>.json`.

## CLI Reference

| Command | Purpose |
|---|---|
| `checkpoint.py new-id` | Generate a fresh session id. |
| `checkpoint.py beat --session ID --action TEXT [--context TEXT] [--files A B]` | Record a heartbeat; refreshes at-risk file list. |
| `checkpoint.py status [--json]` | Show current pulse + at-risk files. |
| `checkpoint.py scan [--stale-minutes N] [--json]` | If pulse is stale-and-not-complete, archive it and print recovery summary. |
| `checkpoint.py recover [--json]` | Print recovery summary for the latest pulse. |
| `checkpoint.py complete [--session ID]` | Mark current pulse complete (graceful end). |
