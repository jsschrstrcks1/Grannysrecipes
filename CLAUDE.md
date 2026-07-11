# CLAUDE.md — Agent pointer (Grannysrecipes)

**Soli Deo Gloria.** Pointer only — household law is not duplicated here.

**Household SSOT:** `/Users/kenbaker/ocs-work`

## Read order (mandatory)

| # | Layer | Load |
|---|-------|------|
| 1 | **Soli Deo Gloria** | `/Users/kenbaker/ocs-work/skills/soli-deo-gloria/SKILL.md` |
| 2 | **Careful, not clever** | `/Users/kenbaker/ocs-work/skills/careful-not-clever/SKILL.md` |
| 3 | **Sophos OS** | `/Users/kenbaker/ocs-work/docs/SOPHOS-OPERATING-SYSTEM.md` |
| 4 | **Cognitive memory** | `ken/orchestrator/memory_ops.py`; `/Users/kenbaker/ocs-work/admin/recall-memory.mjs` |
| 5 | **Household rulebook** | `/Users/kenbaker/ocs-work/docs/HOUSEHOLD-AGENT-RULEBOOK.md` |
| 6 | **Household library** | `/Users/kenbaker/ocs-work/skills/household-library/SKILL.md` |

**Do not skip to §5–6 without §1–4.**

### User task gates (P0)

```bash
node /Users/kenbaker/ocs-work/admin/library.mjs preflight --query "<task>" --patron claude-code --merge --repo Grannysrecipes
```

## Layer 2 — This repo

| Resource | Path |
|----------|------|
| Archived full guide | `admin/REPO-AGENT-APPENDIX.md` |
| Task shelf | `admin/LIBRARY.md` |
| Open work | `admin/UNFINISHED_TASKS.md` or `admin/PENDING_TASKS.md` |

*Household catalog SSOT:* `/Users/kenbaker/ocs-work/.household-library/catalog.jsonl`
