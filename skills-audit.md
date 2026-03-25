# Comprehensive Skills Audit — All 9 Repositories

**Date:** 2026-03-25
**Scope:** jsschrstrcks1 organization — all Claude Code skill deployments

---

## 1. Repository Overview

| # | Repository | Domain | Pipeline Mode | Skills Count |
|---|-----------|--------|---------------|-------------|
| 1 | **Romans** | Sermon manuscripts | `sermon` | 9 |
| 2 | **ken** | Personal hub / orchestrator host | *(explicit)* | 3 |
| 3 | **Allrecipes** | Recipe aggregator | `recipe` | 6 |
| 4 | **flickersofmajesty** | Photography e-commerce | `cruising` | 13 |
| 5 | **Grandmasrecipes** | Grandma Baker's recipes | `recipe` | 5 |
| 6 | **Grannysrecipes** | Granny Hudson's recipes | `recipe` | 5 |
| 7 | **InTheWake** | Cruising / web content | `cruising` | 8 |
| 8 | **manateecreeksheep** | Sheep flock management | `sheep` | 7 |
| 9 | **MomsRecipes** | MomMom Baker's recipes | `recipe` | 6 |

---

## 2. Skills Inventory Per Repository

### Romans (Sermon Repository)
| Skill | Purpose |
|-------|---------|
| careful-not-clever | Integrity guardrail — verifies Scripture refs, quotes, claims |
| cognitive-memory | Cross-session knowledge persistence |
| consult | Quick single-model second opinion |
| icp-2 | Human-First SEO & AEO standard |
| like-a-human | Voice guard during writing |
| orchestrate | Full sermon pipeline (Claude lead → Grok challenge → Gemini expand → GPT structure) |
| sermon-map | Maintains sermon-map.md, theological-map.md, series-trajectory.md, date-map.md |
| thus-says-the-lord | Reformed Baptist sermon evaluation rubric (100-point weighted scale) |
| voice-audit | Post-draft authenticity diagnostic |

**Hooks:** PreToolUse (require-fetch-before-status on Bash), PostToolUse (careful-not-clever verification on Edit/Write, sermon-auto-index on Write)

### ken (Hub / Orchestrator Host)
| Skill | Purpose |
|-------|---------|
| consult | Quick single-model second opinion |
| icp-2 | Human-First SEO & AEO standard |
| orchestrate | Hub orchestrator — no default mode, specify explicitly |

**Hooks:** None configured
**Note:** Hosts the orchestrator at `orchestrator/` used by all repos.

### Allrecipes (Recipe Aggregator)
| Skill | Purpose |
|-------|---------|
| careful-not-clever | Integrity guardrail for recipe accuracy |
| consult | Quick single-model second opinion |
| icp-2 | Human-First SEO & AEO standard |
| orchestrate | Recipe pipeline (GPT lead → Gemini → Claude safety → Grok creative) |
| recipe-transcription | Transcribe handwritten recipe images |
| recipe-validation | Validate recipe data integrity |

**Hooks:** None configured

### flickersofmajesty (Photography E-Commerce)
| Skill | Purpose |
|-------|---------|
| cognitive-memory | Cross-session knowledge persistence |
| consult | Quick single-model second opinion |
| emotional-hook-test | Pre-publication buyer emotional experience gate |
| frontend-design | Production-grade UI with high design quality |
| frontend-dev-guidelines | React/TypeScript patterns (Suspense, MUI v7, TanStack Router) |
| icp-2 | Human-First SEO & AEO standard |
| like-a-human | Voice guard for photography content |
| orchestrate | Cruising pipeline for web content generation |
| pdf | PDF manipulation toolkit |
| skill-creator | Guide for creating new skills |
| skill-developer | Skill management following Anthropic best practices |
| voice-audit | Post-draft authenticity diagnostic for photography content |
| web-artifacts-builder | Multi-component HTML artifacts (React, Tailwind, shadcn/ui) |

**Hooks:** UserPromptSubmit (skill-activation-prompt), PostToolUse (post-tool-use-tracker on Edit/Write)

### Grandmasrecipes (Grandma Baker)
| Skill | Purpose |
|-------|---------|
| consult | Quick single-model second opinion |
| icp-2 | Human-First SEO & AEO standard |
| orchestrate | Recipe pipeline |
| recipe-transcription | Transcribe handwritten recipe images |
| recipe-validation | Validate recipe data integrity |

**Hooks:** PostToolUse (post-write-validate on Edit/Write), PreToolUse (image-safety-check on Read)

### Grannysrecipes (Granny Hudson)
| Skill | Purpose |
|-------|---------|
| consult | Quick single-model second opinion |
| icp-2 | Human-First SEO & AEO standard |
| orchestrate | Recipe pipeline |
| recipe-transcription | Transcribe handwritten recipe images |
| recipe-validation | Validate recipe data integrity |

**Hooks:** PostToolUse (post-write-validate on Edit/Write), PreToolUse (image-safety-check on Read)

### InTheWake (Cruising / Web Content)
| Skill | Purpose |
|-------|---------|
| Humanization | *(custom — likely voice/tone enforcement)* |
| careful-not-clever | Integrity guardrail |
| cognitive-memory | Cross-session knowledge persistence |
| consult | Quick single-model second opinion |
| frontend-dev-guidelines | React/TypeScript patterns |
| icp-2 | Human-First SEO & AEO standard |
| orchestrate | Cruising pipeline |
| skill-developer | Skill management |
| standards | *(custom — likely project standards enforcement)* |

**Hooks:** UserPromptSubmit (session-start-guardrail), PreToolUse (voice-audit-hook on Bash), PostToolUse (post-tool-use-tracker + ship-page-validator + port-content-voice-hook on Edit/Write)

### manateecreeksheep (Sheep Flock Management)
| Skill | Purpose |
|-------|---------|
| careful-not-clever | Integrity guardrail for sheep records |
| cognitive-memory | Cross-session knowledge persistence |
| consult | Quick single-model second opinion |
| flock-validation | Pedigree, breed composition, pen, tag, health record validation |
| icp-2 | Human-First SEO & AEO standard |
| image-transcription | Transcribe spiral notebook photos & handwritten notes |
| orchestrate | Sheep flock decision pipeline (GPT lead planner) |

**Hooks:** PostToolUse (careful-not-clever prompt verification on Edit/Write), PreToolUse (image-safety-check prompt on Read)

### MomsRecipes (MomMom Baker)
| Skill | Purpose |
|-------|---------|
| careful-not-clever | Integrity guardrail for recipe accuracy |
| consult | Quick single-model second opinion |
| icp-2 | Human-First SEO & AEO standard |
| orchestrate | Recipe pipeline |
| recipe-transcription | Transcribe handwritten recipe images |
| recipe-validation | Validate recipe data integrity |

**Hooks:** None configured

---

## 3. Cross-Repository Skill Matrix

| Skill | Romans | ken | Allrecipes | flickers | Grandmas | Grannys | InTheWake | sheep | Moms |
|-------|--------|-----|-----------|----------|----------|---------|-----------|-------|------|
| consult | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| orchestrate | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| icp-2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| cognitive-memory | ✅ | — | — | ✅ | — | — | ✅ | ✅ | — |
| careful-not-clever | ✅ | — | ✅ | — | — | — | ✅ | ✅ | ✅ |
| like-a-human | ✅ | — | — | ✅ | — | — | — | — | — |
| voice-audit | ✅ | — | — | ✅ | — | — | — | — | — |
| recipe-transcription | — | — | ✅ | — | ✅ | ✅ | — | — | ✅ |
| recipe-validation | — | — | ✅ | — | ✅ | ✅ | — | — | ✅ |
| frontend-dev-guidelines | — | — | — | ✅ | — | — | ✅ | — | — |
| frontend-design | — | — | — | ✅ | — | — | — | — | — |
| skill-developer | — | — | — | ✅ | — | — | ✅ | — | — |
| sermon-map | ✅ | — | — | — | — | — | — | — | — |
| thus-says-the-lord | ✅ | — | — | — | — | — | — | — | — |
| flock-validation | — | — | — | — | — | — | — | ✅ | — |
| image-transcription | — | — | — | — | — | — | — | ✅ | — |
| emotional-hook-test | — | — | — | ✅ | — | — | — | — | — |
| web-artifacts-builder | — | — | — | ✅ | — | — | — | — | — |
| pdf | — | — | — | ✅ | — | — | — | — | — |
| skill-creator | — | — | — | ✅ | — | — | — | — | — |
| Humanization | — | — | — | — | — | — | ✅ | — | — |
| standards | — | — | — | — | — | — | ✅ | — | — |

---

## 4. Gap Analysis & Recommendations

### 4.1 Universal Skills (deployed to all 9 repos) — ✅ Complete
- **consult** — ✅ All 9
- **orchestrate** — ✅ All 9
- **icp-2** — ✅ All 9

### 4.2 cognitive-memory — Inconsistent Deployment
**Current:** Romans, flickersofmajesty, InTheWake, manateecreeksheep (4/9)
**Missing from:** ken, Allrecipes, Grandmasrecipes, Grannysrecipes, MomsRecipes

**Recommendation:** Deploy to ALL repositories. Cross-session memory is valuable everywhere — recipe repos need to remember transcription progress, ken needs it as the hub. This is the highest-priority gap.

### 4.3 careful-not-clever — Partially Deployed
**Current:** Romans, Allrecipes, InTheWake, manateecreeksheep, MomsRecipes (5/9)
**Missing from:** ken, flickersofmajesty, Grandmasrecipes, Grannysrecipes

**Recommendation:**
- **Grandmasrecipes & Grannysrecipes** — HIGH priority. These recipe repos have the same accuracy-first ethos but lack the guardrail skill (they do have PostToolUse hooks for validation, but not the skill itself).
- **flickersofmajesty** — MEDIUM priority. Product descriptions and pricing should be verified.
- **ken** — LOW priority. Hub repo with minimal content creation.

### 4.4 Recipe Repos — Hooks Inconsistency
| Hook | Allrecipes | Grandmas | Grannys | Moms |
|------|-----------|----------|---------|------|
| PostToolUse validation | ❌ | ✅ | ✅ | ❌ |
| PreToolUse image-safety | ❌ | ✅ | ✅ | ❌ |
| careful-not-clever skill | ✅ | ❌ | ❌ | ✅ |

**Recommendation:** Standardize all 4 recipe repos to have BOTH the hooks AND the skill. Currently Allrecipes and MomsRecipes have the skill but no hooks, while Grandmasrecipes and Grannysrecipes have hooks but no skill.

### 4.5 Voice/Writing Quality Skills — Domain-Appropriate
| Skill | Where Deployed | Where Needed |
|-------|---------------|-------------|
| like-a-human | Romans, flickersofmajesty | InTheWake (has Humanization instead — verify equivalence) |
| voice-audit | Romans, flickersofmajesty | InTheWake (has voice-audit-hook in PreToolUse — verify coverage) |

**Recommendation:** Audit whether InTheWake's `Humanization` skill and `voice-audit-hook` provide equivalent coverage to the `like-a-human` + `voice-audit` pair. If not, deploy those skills to InTheWake for consistency.

### 4.6 flickersofmajesty — Overloaded
With 13 skills, this repo has the most skills by far. Some may be meta/development skills (skill-creator, skill-developer, web-artifacts-builder) that could live in ken instead.

**Recommendation:** Consider whether skill-creator and skill-developer belong in the hub (ken) rather than a domain repo. pdf and web-artifacts-builder are legitimately needed for e-commerce.

### 4.7 ken — Underequipped
Only 3 skills (the universal trio). As the hub hosting the orchestrator, it should have:
- **cognitive-memory** — essential for cross-session orchestrator knowledge
- **skill-developer** — since it's the natural home for skill development work

### 4.8 InTheWake — Missing CLAUDE.md
This is the only repo without a `CLAUDE.md` file. It has 8 skills and the most complex hook setup (4 hooks across 3 events), but no top-level project context document.

**Recommendation:** Create a CLAUDE.md for InTheWake following the pattern of other repos.

---

## 5. Hook Architecture Summary

| Repo | PreToolUse | PostToolUse | UserPromptSubmit |
|------|-----------|-------------|-----------------|
| Romans | ✅ Bash: require-fetch-before-status | ✅ Edit/Write: careful-not-clever (prompt) + Write: sermon-auto-index (command) | — |
| ken | — | — | — |
| Allrecipes | — | — | — |
| flickersofmajesty | — | ✅ Edit/Write: post-tool-use-tracker | ✅ skill-activation-prompt |
| Grandmasrecipes | ✅ Read: image-safety-check | ✅ Edit/Write: post-write-validate | — |
| Grannysrecipes | ✅ Read: image-safety-check | ✅ Edit/Write: post-write-validate | — |
| InTheWake | ✅ Bash: voice-audit-hook | ✅ Edit/Write: post-tool-use-tracker + ship-page-validator + port-content-voice-hook | ✅ session-start-guardrail |
| manateecreeksheep | ✅ Read: image-safety-check (prompt) | ✅ Edit/Write: careful-not-clever (prompt) | — |
| MomsRecipes | — | — | — |

**Key Finding:** MomsRecipes and Allrecipes have NO hooks despite being recipe repos. Grandmasrecipes and Grannysrecipes demonstrate the recipe hook pattern that should be replicated.

---

## 6. Priority Action Items

| Priority | Action | Repos Affected |
|----------|--------|---------------|
| **P0** | Deploy cognitive-memory to ken, Allrecipes, Grandmasrecipes, Grannysrecipes, MomsRecipes | 5 repos |
| **P0** | Add hooks to MomsRecipes (post-write-validate + image-safety-check) | 1 repo |
| **P0** | Add hooks to Allrecipes (post-write-validate + image-safety-check) | 1 repo |
| **P1** | Deploy careful-not-clever to Grandmasrecipes, Grannysrecipes | 2 repos |
| **P1** | Create CLAUDE.md for InTheWake | 1 repo |
| **P1** | Deploy cognitive-memory + skill-developer to ken | 1 repo |
| **P2** | Audit InTheWake Humanization vs like-a-human equivalence | 1 repo |
| **P2** | Consider relocating skill-creator/skill-developer from flickersofmajesty to ken | 2 repos |
| **P2** | Deploy careful-not-clever to flickersofmajesty | 1 repo |
| **P3** | Evaluate whether recipe repos need like-a-human for website copy | 4 repos |

---

## 7. Global Skills (in ~/.claude/skills/)

| Skill | Purpose |
|-------|---------|
| cognitive-memory | Cross-repo memory (global baseline) |
| consult | Multi-LLM consultation (global baseline) |
| orchestrate | Pipeline orchestration (global baseline) |

These 3 global skills provide the foundation. Repo-level skills override or extend these as needed.

---

*Document generated from live skill/hook/settings analysis across all 9 repositories.*
