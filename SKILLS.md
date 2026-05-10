# Skills — Grannysrecipes

> The private one. Skills here operate under stricter context boundaries than the public recipe repos: memorial content never leaves the local machine.

This document is the human-facing index of all Claude Code skills configured in this repository. The agent-facing pointer lives in [`CLAUDE.md`](CLAUDE.md). Skills follow the agent-skills-spec format and live under `.claude/skills/`.

**Total skills configured: 18.** 16 are the standard household kit; 2 are recipe-domain specific.

---

## Quick reference

| Skill | Activation | Default | Domain |
|---|---|---|---|
| [`recipe-transcription`](#recipe-transcription) | automatic on image+recipe context | on | Recipe ingestion |
| [`recipe-validation`](#recipe-validation) | automatic before commit | on | Recipe integrity |
| Standard household kit (16 skills) | mixed | on | See [section below](#standard-household-kit) |

---

## How invocation works

Claude Code skills can fire three ways:

**1. Automatic activation** via YAML `keywords:` and surrounding context.

**2. Explicit invocation:**

```
"Use the recipe-transcription skill to extract this card from Granny."
/skill recipe-transcription
```

**3. Implicit invocation by task shape** — image reads of recipe sources, recipe JSON edits, completion claims, web fetches, etc.

**Disabling for a session:** "For this session, do not apply X."

---

## Privacy posture (load-bearing)

This repo is a **private family archive**. Three controls are non-negotiable and enforced by `.githooks/pre-commit`:

1. `robots.txt` blocks all crawlers.
2. Every HTML file ships `<meta name="robots" content="noindex, nofollow">`.
3. No `sitemap.xml`.

**Two-tier privacy for AI consultation** — this is the rule that diverges from sister recipe repos:

- **Recipe content** **may** be shared with external AI models for transcription help.
- **Memorial content** (people's names, photos, stories under `Memorial/`) **must not** be sent to external models. Process locally only.

When working with skills that call out to GPT/Gemini/Grok, ensure no `Memorial/` paths are in the context. The orchestrator's `consult` and `orchestrate` skills are constrained accordingly.

---

## Recipe-domain skills

### `recipe-transcription`

**Path:** `.claude/skills/recipe-transcription/SKILL.md`

Extracts structured recipe data from images. Optimized for messy handwriting and partial text — this collection skews handwritten more than the other recipe repos.

**Activation:** automatic when image-source-of-recipe context is detected, or explicit.

**Non-negotiables enforced by this skill (Granny-specific tightenings):**

- Never invent ingredients, steps, temperatures, times, or yields
- Mark unreadable text `[UNCLEAR]`; provide 2–3 `[GUESS]` candidates with confidence levels
- Preserve original intent; normalize only spelling and formatting
- Keep family names and attributions verbatim (e.g., "Aunt Linda's Pound Cake")
- Never discard an `image_refs` reference — even merged duplicates keep all refs
- Always read from `granny/processed/`, never raw oversized images
- **Every recipe must carry `"collection": "granny"`**

**Example prompts that should trigger:**

| Prompt | Expected behavior |
|---|---|
| "Transcribe `granny/processed/granny-12.jpeg`" | Reads processed copy, marks `[UNCLEAR]` for ambiguous handwriting, provides `[GUESS]` candidates |
| "Add Aunt Velma's pecan pie" | Preserves attribution; sets `"collection": "granny"` |
| "Process the new card scans" | Refuses raw read of oversized images; calls `process_images.py` first |

### `recipe-validation`

**Path:** `.claude/skills/recipe-validation/SKILL.md`

Validates `granny/recipes_master.json` against the schema. Plus: validates the privacy posture as part of completion (`scripts/check-noindex.sh`).

**Activation:** automatic before commit; also explicit.

**Validation rules enforced:**

- Required fields: `id`, `collection`, `title`, `attribution`, `source_note`, `category`, `ingredients[]`, `instructions[]`, `confidence`
- `"collection": "granny"` on every recipe (mandatory)
- Slug uniqueness
- `image_refs` retention (don't discard on merge)
- `confidence.overall` set; `flags` populated when `low`
- **Privacy check:** `robots.txt` blocks all, no `sitemap.xml`, every HTML has `noindex`

**Manual invocation:**

```
python scripts/validate-recipes.py
bash scripts/check-noindex.sh
```

The pre-commit hook re-runs these. **If they fail, fix the underlying file rather than bypassing the hook.**

---

## Standard household kit

Common to every sister repo. Canonical versions live in `ken/.claude/skills/`.

| Skill | Activation | One-line |
|---|---|---|
| `brainstorming` | automatic on creative work | Pre-implementation creative exploration. |
| `cognitive-memory` | automatic on session start | Cross-session knowledge persistence. Memory scope: `/Grannysrecipes`. |
| `executing-plans` | explicit | Use when executing a written plan in a separate session. |
| `finishing-a-development-branch` | explicit | Decide merge / PR / cleanup. |
| `prompt-optimizer` | automatic on prompt-improvement requests | Optimizes raw prompts. Advisory only. |
| `receiving-code-review` | explicit | Use when receiving review feedback. |
| `requesting-code-review` | explicit | Use when completing tasks before merging. |
| `safety-guard` | automatic on destructive ops | Prevents destructive operations. |
| `security-review` | automatic on auth/secrets/payment | Security checklist + patterns. |
| `security-scan` | explicit | Scans `.claude/` config. |
| `session-checkpoint` | automatic + explicit | Atomic commits, checkpoint summaries, rate-limit recovery. |
| `subagent-driven-development` | explicit | Implementation plans with independent tasks. |
| `systematic-debugging` | automatic on bug/test-failure | Use before proposing fixes. |
| `using-git-worktrees` | explicit | Isolate feature work. |
| `verification-before-completion` | automatic on completion claims | Refuses "complete/fixed/passing" without observed output. |
| `writing-plans` | explicit | Use when you have a spec for a multi-step task. |

---

## Multi-LLM orchestrator

This repo defaults to **`recipe` mode** in the orchestrator hosted in [ken](https://github.com/jsschrstrcks1/ken). Lead model: GPT.

| Slash command | Usage |
|---|---|
| `/consult` | `/consult gpt structure "review this Aunt Linda's pound cake transcription"` |
| `/orchestrate recipe "<task>"` | Full pipeline: transcribe → validate → integrate |

**Strict context boundary:** recipe content may go to consultants; **memorial content must not.**

First-time setup per session:

```bash
pip3 install -q -r /home/user/ken/orchestrator/requirements.txt
```

---

## See also

- [`CLAUDE.md`](CLAUDE.md) — agent context
- [`README.md`](README.md) — public-facing overview (still anti-indexed)
- [`.claude/standards/`](.claude/standards/) — OCR, IMAGE_WORKFLOW, FRAGMENT_HANDLING, RECIPE_SCHEMA, CONVERSIONS, NUTRITION_QUESTIONS, DUPLICATE_HANDLING, BLOAT_MANAGEMENT
- [`.githooks/pre-commit`](.githooks/) — enforces noindex / no-sitemap
- `ken` — hosts the orchestrator; canonical versions of the standard household kit
