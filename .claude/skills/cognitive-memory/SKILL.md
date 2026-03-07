---
name: cognitive-memory
description: Cross-repository cognitive memory system. Persists knowledge across sessions using encode, consolidate, recall, extract, and forget operations. Memory is cognition, not storage.
trigger:
  - keyword: [memory, remember, recall, forget, "what do we know", "last session", "previous session", "what was", "do you remember"]
  - intent: ["recalling past context", "storing new knowledge", "resolving contradictions", "session continuity"]
  - event: session_start
priority: high
---

# Cognitive Memory System

> Memory as stewardship: what we remember shapes how we serve.

## Overview

This skill provides persistent cognitive memory across Claude Code sessions. It is NOT a database — it is a reasoning layer that encodes selectively, consolidates contradictions, recalls adaptively, and forgets intentionally.

**Memory store:** `/home/user/.memory/memory.json`
**Configuration:** `/home/user/.memory/memory-config.json`
**Operations script:** `/home/user/.memory/memory_ops.py`
**Archive:** `/home/user/.memory/archive/`

## Session Start Protocol

At the beginning of every session, recall relevant memories for this repository:

```bash
python3 /home/user/.memory/memory_ops.py recall "" --scope /grannysrecipes --limit 10
python3 /home/user/.memory/memory_ops.py tree /grannysrecipes
```

Present a brief summary to the user:
- Recent changes and current state
- Open questions or low-confidence memories
- Any contradictions flagged but not yet resolved

## Five Cognitive Operations

### 1. REMEMBER — When you learn something new

```bash
python3 /home/user/.memory/memory_ops.py remember "FACT" \
  --scope /grannysrecipes/DOMAIN \
  --categories CAT1 CAT2 \
  --importance 0.0-1.0 \
  --confidence high|medium|low \
  --source-type session|user|notebook|document \
  --source-ref "SOURCE"
```

**Importance guidelines:**
- 0.9: Critical decisions, corrections, structural changes
- 0.7: Important observations, verified facts
- 0.5: General notes, routine work
- 0.3: Temporary states, minor observations

### 2. RECALL — When you need past context

```bash
python3 /home/user/.memory/memory_ops.py recall "QUERY" --scope /grannysrecipes
```

**Trust but verify:** If recall confidence is "low", say so. Don't present uncertain memories as facts.

### 3. EXTRACT — After processing large content

Decompose large outputs into atomic facts. Each fact gets its own REMEMBER call with appropriate scope, importance, and confidence.

### 4. TREE — To see what we know

```bash
python3 /home/user/.memory/memory_ops.py tree /grannysrecipes
```

### 5. FORGET — To keep memory useful

```bash
python3 /home/user/.memory/memory_ops.py forget --scope /grannysrecipes --older-than 90 --dry-run
python3 /home/user/.memory/memory_ops.py forget --scope /grannysrecipes --older-than 90
```

## What Memory Is NOT

- Memory does NOT replace primary data files in this repository
- Memory does NOT override primary sources
- Memory does NOT store raw data — it stores *conclusions about* data
- Memory does NOT act autonomously — you decide when to remember and recall

## Soli Deo Gloria

Careful, not clever. What we remember matters. What we forget matters too.
