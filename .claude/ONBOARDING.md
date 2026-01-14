# Claude Code Infrastructure — Onboarding

This repository has been enhanced with Claude Code infrastructure. Here's what's new:

---

## CLAUDE.md Overview

The main instruction file contains:

| Section | Purpose |
|---------|---------|
| **Project Mission** | Soli Deo Gloria — Reformed Baptist family project |
| **Recipe Schema** | Full JSON structure for recipes |
| **OCR Correction** | Character confusion tables, measurement checks |
| **Image Safeguards** | 2000px dimension limits, processing workflow |
| **Quality Checklist** | Verification steps for accuracy |
| **Non-Negotiables** | Rules that must never be broken |

---

## New `.claude/` Directory

```
.claude/
├── settings.json              # Hook configuration
├── skill-rules.json           # Skill auto-activation (3 skills)
├── ONBOARDING.md              # THIS FILE
├── MAINTENANCE.md             # Detailed maintenance workflows
├── CROSS_REPO_STANDARDS.md    # Cross-repo sync standards
├── mcp-servers.md             # MCP server integration docs
├── hooks/
│   ├── post-write-validate.sh # Runs after Edit/Write on recipes
│   └── image-safety-check.sh  # Runs before Read on images
└── skills/
    ├── recipe-transcription/
    │   └── SKILL.md           # OCR workflow guidance
    └── recipe-validation/
        └── SKILL.md           # Schema validation guidance
```

---

## Automatic Hooks

These run automatically based on `settings.json`:

| Hook | Trigger | What It Does |
|------|---------|--------------|
| `post-write-validate.sh` | Edit\|Write on recipe files | Runs validation, shows errors |
| `image-safety-check.sh` | Read on image files | Warns if image may exceed 2000px |

---

## Skills (Auto-Activate via `skill-rules.json`)

| Skill | Activates When | Loads |
|-------|----------------|-------|
| `recipe-transcription` | Reading images, keywords: transcribe, OCR, handwritten | `.claude/skills/recipe-transcription/SKILL.md` |
| `recipe-validation` | Editing recipes, keywords: validate, check, schema | `.claude/skills/recipe-validation/SKILL.md` |
| `image-safety` | Reading images in `granny/` | Rule-based warnings |

---

## Key Documentation Files

**Read in this order:**
1. `CLAUDE.md` — Main instructions (always read first)
2. `.claude/MAINTENANCE.md` — Detailed task workflows
3. `.claude/skills/*/SKILL.md` — Skill-specific guidance (auto-loaded)

**Reference as needed:**
- `.claude/CROSS_REPO_STANDARDS.md` — When syncing across family repos
- `.claude/mcp-servers.md` — When integrating MCP servers

---

## Quick Verification

```bash
# Check hooks are configured
cat .claude/settings.json | python -c "import json,sys; print('Hooks OK' if json.load(sys.stdin).get('hooks') else 'No hooks')"

# Check skills are defined
cat .claude/skill-rules.json | python -c "import json,sys; d=json.load(sys.stdin); print(f'{len(d[\"skills\"])} skills defined')"

# Verify skill files exist
ls .claude/skills/*/SKILL.md
```

---

## When Working on This Repo

1. **Read `CLAUDE.md`** — Contains all core rules and quick reference
2. **Let hooks run** — They provide automatic validation and warnings
3. **Check skill guidance** — When transcribing or validating, skills auto-load context
4. **Use maintenance workflows** — `.claude/MAINTENANCE.md` has step-by-step guides

---

## Quick Reference

### Priority Framework

| Priority | Principle |
|----------|-----------|
| 1 | **Accuracy-First** — Never guess or invent |
| 2 | **Preservation-First** — Handwritten images are sacred |
| 3 | **Fidelity-First** — Preserve Granny's exact wording |
| 4 | **Readability-First** — Family needs usable recipes |

### Non-Negotiables

- **NEVER** delete handwritten images
- **NEVER** invent ingredients, steps, or measurements
- **ALWAYS** use `[UNCLEAR]` for uncertain text
- **ALWAYS** validate after making changes
- Collection field must be `"granny"` for all recipes

### Common Commands

```bash
python scripts/image_safeguards.py status   # Before reading images
python scripts/validate-recipes.py           # After editing recipes
python scripts/process_images.py             # After adding images
python scripts/shard_recipes.py              # After modifying recipes
```

---

## Repository Structure

```
Grannysrecipes/
├── CLAUDE.md                    # Main AI instructions
├── granny/                      # Recipe collection folder
│   ├── *.jpeg                   # Original scanned images
│   ├── processed/               # AI-friendly resized images
│   ├── recipes_master.json      # All recipes (master)
│   ├── recipes-index.json       # Lightweight index for sharding
│   └── recipes-{category}.json  # Category shards
├── scripts/
│   ├── validate-recipes.py      # Recipe validation
│   ├── image_safeguards.py      # Image dimension checks
│   ├── process_images.py        # Image resizing
│   └── shard_recipes.py         # Generate category shards
└── .claude/                     # Claude Code configuration
```

---

*Last updated: 2026-01*
