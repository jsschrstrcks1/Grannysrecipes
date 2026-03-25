---
name: cognitive-memory
description: "Cross-repository cognitive memory system with semantic search. Persists knowledge across sessions using TF-IDF recall, memory versioning, knowledge graph edges, and confidence decay. Memory is cognition, not storage."
trigger:
  - keyword: [memory, remember, recall, forget, "what do we know", "last session", "previous session", "what was", "do you remember"]
  - intent: ["recalling past context", "storing new knowledge", "resolving contradictions", "session continuity"]
  - event: session_start
priority: high
version: 3.0.0
---

# Cognitive Memory System v3

> Memory as stewardship: what we remember shapes how we serve.

## What's New in v2

- **Semantic search**: TF-IDF + cosine similarity replaces keyword matching. "deworming resistance" finds "FAMACHA scoring" and "parasite resistance" even without shared words.
- **Memory versioning**: `update` creates a new version, preserves the original with `supersedes` chain.
- **Knowledge graph**: `link` creates bidirectional edges between related memories.
- **Duplicate detection**: `consolidate` flags memories with >80% similarity.
- **Recency boost**: Recent memories score higher. Old unrecalled memories decay.

## Overview

This skill provides persistent cognitive memory across Claude Code sessions. It is NOT a database — it is a reasoning layer that encodes selectively, consolidates contradictions, recalls semantically, and forgets intentionally.

**Memory store:** `~/.memory/DOMAIN/`
**Operations script:** `/home/user/ken/orchestrator/memory_ops.py`

## Session Start Protocol

At the beginning of every session, recall relevant memories:

```bash
python3 /home/user/ken/orchestrator/memory_ops.py recall "" --domain recipes --limit 10
python3 /home/user/ken/orchestrator/memory_ops.py tree --domain recipes
```

Present a brief summary to the user:
- Recent changes and current state
- Open questions or low-confidence memories
- Any contradictions flagged but not yet resolved

## Seven Cognitive Operations

### 1. REMEMBER — Encode new knowledge

```bash
python3 /home/user/ken/orchestrator/memory_ops.py encode recipes <type> "content" \
  --tags tag1,tag2 --related id1,id2
```

**Types:** insight, decision, pattern, fact, preference

**Importance → confidence mapping:**
- 0.9: Critical decisions, corrections, structural changes
- 0.7: Important observations, verified facts
- 0.5: General notes, routine work
- 0.3: Temporary states, minor observations

### 2. RECALL — Semantic search

```bash
python3 /home/user/ken/orchestrator/memory_ops.py recall "natural language query" --domain recipes --limit 10
```

Recall now uses TF-IDF semantic matching. You don't need exact keywords — conceptually related memories surface automatically. Each result includes a `_score` field.

**Trust but verify:** If a recalled memory has low confidence or a low score, say so. Don't present uncertain memories as facts.

### 3. UPDATE — Version a memory

```bash
python3 /home/user/ken/orchestrator/memory_ops.py update <id> "corrected content" --domain recipes
```

Creates a new version. The old memory is preserved with reduced confidence and a `superseded_by` pointer. Use this when facts change — don't forget and re-encode, update.

### 4. LINK — Connect related memories

```bash
python3 /home/user/ken/orchestrator/memory_ops.py link <id_a> <id_b>
```

Creates a bidirectional edge. Use when you discover two memories are related — a breeding decision connects to a flock validation insight, a recipe correction connects to a transcription note.

### 5. CONSOLIDATE — Maintain memory health

```bash
python3 /home/user/ken/orchestrator/memory_ops.py consolidate --domain recipes
```

Decays unrecalled memories, removes dead ones, and reports potential duplicates (>80% similarity). Run periodically or at session end.

### 6. TREE — See what we know

```bash
python3 /home/user/ken/orchestrator/memory_ops.py tree --domain recipes
```

Shows memory count, types, edge connections, and version chains per domain.

### 7. FORGET — Intentional removal

```bash
python3 /home/user/ken/orchestrator/memory_ops.py forget <id> --domain recipes
```

## What Memory Is NOT

- Memory does NOT replace primary data files in this repository
- Memory does NOT override primary sources
- Memory does NOT store raw data — it stores *conclusions about* data
- Memory does NOT act autonomously — you decide when to remember and recall

## Soli Deo Gloria

Careful, not clever. What we remember matters. What we forget matters too.


## Domain-Specific: Family Recipe Archive

### What to Encode
- **Transcription corrections**: When a measurement was misread and corrected, what the original said
- **Recipe relationships**: "This is the same as Grandma's cornbread but with buttermilk instead of sweet milk"
- **Unclear resolutions**: When an [UNCLEAR] marker was resolved — what it turned out to be
- **Processing decisions**: Why certain images needed reprocessing, OCR quirks discovered
- **Collection patterns**: Recurring ingredient substitutions, regional terminology, family conventions
- **Validation insights**: Common validation failures and their root causes

### Encoding Patterns

```bash
# After resolving an unclear transcription
python3 /home/user/ken/orchestrator/memory_ops.py encode recipes fact \
  "Recipe 042 (dump cake): [UNCLEAR] on line 3 was '1 can cherry pie filling' — confirmed from second photo IMG_453" \
  --tags recipe-042,unclear-resolved,dump-cake

# After discovering a pattern
python3 /home/user/ken/orchestrator/memory_ops.py encode recipes pattern \
  "Grandma uses 'oleo' for margarine throughout. Don't standardize it — that's her word." \
  --tags vocabulary,oleo,margarine,voice

# Link related recipes across collections
python3 /home/user/ken/orchestrator/memory_ops.py link <grandma_cornbread_id> <granny_cornbread_id>
```

### What NOT to Encode
- Full recipe JSON (that's in recipes.json)
- Image file paths (that's in the data directory)
- Nutrition estimates (that's in the nutrition estimator output)
- Things validate-recipes.py already checks

### Careful-Not-Clever Integration
Before encoding any recipe memory, verify against the source image. If you resolved an [UNCLEAR], note which image confirmed it.


## v3 Upgrades (Research-Driven)

### Protected Memories
Foundational knowledge that should NEVER decay, regardless of recall frequency.

```bash
# Encode as protected from the start
python3 /home/user/ken/orchestrator/memory_ops.py encode recipes fact "content" --protected

# Protect an existing memory
python3 /home/user/ken/orchestrator/memory_ops.py protect <id> --domain recipes
```

**When to protect:**
- Vocabulary conventions ("oleo means margarine")
- Core identity facts ("Kelsier is the gold standard sire")
- Architectural decisions that downstream work assumes
- Definitions that other memories reference implicitly

**Auto-protection:** Memories with 3+ graph edges are automatically protected during consolidation — if many things reference it, it is foundational by definition.

### Cross-Domain Recall
Recall now searches ALL domains by default. Each result includes `_domain` so you know where it came from. This enables cross-pollination — a breeding pattern in sheep might inform resource organization in recipes.

```bash
# Search everywhere (default)
python3 /home/user/ken/orchestrator/memory_ops.py recall "optimization strategy"

# Restrict to one domain when you know what you want
python3 /home/user/ken/orchestrator/memory_ops.py recall "optimization strategy" --domain recipes
```

### Graph Centrality Scoring
Well-connected memories score higher in recall. A memory linked to 5 other memories ranks above an isolated memory with the same text similarity. This rewards knowledge that has been woven into the graph.

**Score formula:** `similarity * confidence * (0.70 + 0.15*recency + 0.15*centrality)`

### Graph Traversal
Explore the knowledge graph from any memory:

```bash
# Direct neighbors
python3 /home/user/ken/orchestrator/memory_ops.py neighbors <id> --depth 1

# Neighbors of neighbors
python3 /home/user/ken/orchestrator/memory_ops.py neighbors <id> --depth 2
```

### Tiered Storage (Active + Archive)
Old, low-confidence, unprotected memories are automatically archived during consolidation (>180 days, <0.3 confidence). Archived memories:
- Are preserved in `~/.memory/_archive/`
- Are excluded from default recall (use `--include-archive` to search them)
- Can be promoted back: `python3 memory_ops.py promote <id>`
- Maintain graph edges for integrity

```bash
# Manually archive
python3 /home/user/ken/orchestrator/memory_ops.py archive <id> --domain recipes

# Search including archive
python3 /home/user/ken/orchestrator/memory_ops.py recall "old topic" --include-archive

# Bring something back
python3 /home/user/ken/orchestrator/memory_ops.py promote <id>
```

### Enhanced Consolidation
Consolidate is now smarter:
1. **Decay** — only unrecalled, unprotected, >7-day-old memories (protected are immune)
2. **Auto-protect** — memories with 3+ edges get protected automatically
3. **Auto-merge** — memories with >85% similarity are merged (tags combined, lower one archived)
4. **Auto-archive** — old (>180d), low-confidence (<0.3), unprotected memories move to archive
5. **Near-duplicate flagging** — 70-85% similarity reported for manual review
