---
name: session-checkpoint
description: "Enforces atomic commits, checkpoint summaries, rate-limit recovery, and safe resume patterns. Writes session state to cognitive-memory so interrupted sessions can restart cleanly."
version: 1.0.0
---

# Session Checkpoint

*Soli Deo Gloria — we work carefully, in small steps, offering each commit as honest labor.*

## Why This Skill Exists

Claude Code makes multiple API calls per step. Large files + multi-file edits can exhaust per-minute token budgets. When a rate limit fires mid-session, work-in-progress can be lost. This skill prevents that.

## Session Startup Protocol

### 1. Identify the single target file
Do not load all files simultaneously. Load only what the task requires.

### 2. Write a session intent to memory

```bash
python3 /home/user/ken/orchestrator/memory_ops.py encode recipes insight \
  "Session intent: [task description]. Target: [files]. Expected: [outcome]." \
  --tags session,intent,checkpoint
```

### 3. Recall prior session state

```bash
python3 /home/user/ken/orchestrator/memory_ops.py recall "session checkpoint" --domain recipes --limit 5
```

## Checkpoint Protocol (During Work)

After every logical unit of work, encode to memory:

```bash
python3 /home/user/ken/orchestrator/memory_ops.py encode recipes insight \
  "Checkpoint [N]: Edited [file]. Changed [what]. Still needs [remaining]. Risks: [any]." \
  --tags session,checkpoint
```

### When to checkpoint:
- After completing a function or block edit
- Before switching to a second file
- Before any find-and-replace touching multiple locations
- Before modifying critical data structures

## Rate Limit Recovery

When you see `Rate limit reached` or HTTP 429:

1. **Stop.** Do not retry immediately.
2. **Encode recovery state to memory:**

```bash
python3 /home/user/ken/orchestrator/memory_ops.py encode recipes decision \
  "RATE LIMIT RECOVERY: Interrupted at [step]. File: [name]. Last clean: [state]. Next step: [action]. Do NOT: [incomplete work]." \
  --tags session,recovery,rate-limit --protected
```

3. **Wait 60 seconds** for per-minute limits to reset.
4. **On resume**, recall the recovery memory first:

```bash
python3 /home/user/ken/orchestrator/memory_ops.py recall "rate limit recovery" --domain recipes --limit 3
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

1. Encode final checkpoint to memory (protected)
2. List deferred issues in a separate memory
3. Confirm all touched files are consistent

