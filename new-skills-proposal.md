# New Skills Proposal & Redeployment Plan

**Date:** 2026-03-25
**Scope:** All 9 repositories — jsschrstrcks1 organization

---

## Part A: New Skills to Build

### 1. `seo-schema-audit` — For: InTheWake, flickersofmajesty, recipe repos

**Problem:** These sites use structured data (JSON-LD, Open Graph, schema.org) but have no automated validation skill. InTheWake has 388 port pages, 298 ship profiles, 472 dining pages — schema errors at that scale compound silently. flickersofmajesty uses Product schema. Recipe repos need Recipe schema.

**What it does:**
- Validates JSON-LD against schema.org specs (Product, Recipe, Article, FAQPage, LocalBusiness)
- Checks Open Graph and Twitter Card completeness
- Validates `ai:summary`, `ai:target-audience` meta tags (ICP-2 compliance)
- Detects stale `last-reviewed` dates (>90 days)
- Verifies canonical URLs match actual file paths
- Reports missing or malformed schema per page

**Trigger:** Fires on Edit/Write of any `.html` file containing `application/ld+json`

**Deploy to:** InTheWake, flickersofmajesty, Allrecipes, Grandmasrecipes, Grannysrecipes, MomsRecipes

---

### 2. `link-integrity` — For: InTheWake, flickersofmajesty

**Problem:** InTheWake has 64+ HTML files with heavy cross-linking (port→ship→restaurant→cruise-line). flickersofmajesty links products to categories. Broken internal links are invisible until a visitor hits them.

**What it does:**
- Scans modified HTML files for internal `href` and `src` references
- Verifies target files exist in the repo
- Checks anchor references (`#section-id`) resolve to actual IDs
- Validates image paths exist (especially after file renames)
- Reports orphaned pages (exist but nothing links to them)

**Trigger:** PostToolUse on Edit/Write of `.html` files

**Deploy to:** InTheWake, flickersofmajesty (the two sites with significant cross-linking)

---

### 3. `ebook-builder` — For: Grandmasrecipes, MomsRecipes, Grannysrecipes

**Problem:** All three recipe repos have `ebook/` directories with `book.html` and `print.css`. Currently ebook generation is manual. A skill that knows the ebook structure, recipe data format, and print CSS constraints would make regeneration reliable.

**What it does:**
- Generates/regenerates `book.html` from `data/recipes.json` (or equivalent)
- Enforces print-friendly layout (page breaks, margins, image sizing)
- Maintains table of contents with recipe categories
- Validates all recipe references in the ebook match actual recipe data
- Handles collection-specific branding (Grandma Baker vs. Granny Hudson vs. MomMom Baker)

**Trigger:** `/ebook` command or when recipe data changes significantly

**Deploy to:** Grandmasrecipes, Grannysrecipes, MomsRecipes

---

### 4. `breeding-advisor` — For: manateecreeksheep

**Problem:** The repo has a sophisticated `breeding_projector.py` (heterosis, inbreeding coefficients, parasite resistance) but no skill that helps Claude interpret results, recommend pairings, or explain tradeoffs in plain language.

**What it does:**
- Wraps `breeding_projector.py` output with plain-language interpretation
- Recommends top 3 sire×dam pairings based on goals (parasite resistance, heat tolerance, wool quality, temperament)
- Flags inbreeding risks with explanations a farmer can act on
- Compares projected offspring against current flock needs
- Tracks breeding decisions across sessions via cognitive-memory integration

**Trigger:** `/breed` command or when discussing sire/dam pairings

**Deploy to:** manateecreeksheep only

---

### 5. `sermon-cross-reference` — For: Romans

**Problem:** With 465 sermon manuscripts, cross-referencing is a major task. The sermon-map tracks structure, but there's no skill for finding thematic connections, repeated illustrations, or theological threads across the entire corpus.

**What it does:**
- Finds all sermons that reference a given passage, doctrine, or illustration
- Detects repeated illustrations across sermons (beyond sermon-map's DEDUP)
- Maps theological argument chains ("where else did we establish X?")
- Suggests callback opportunities to previous sermons in a series
- Generates "preaching history" reports for any Bible book or doctrine

**Trigger:** `/xref <term>` command or when drafting a sermon that references previous teaching

**Deploy to:** Romans only

---

### 6. `port-content-builder` — For: InTheWake

**Problem:** 388 port pages need consistent structure, accurate data, and the site's voice. Currently InTheWake has standards files and voice hooks, but no skill that knows the port page template, POI schema, and content requirements.

**What it does:**
- Generates port pages from the `poi-index.schema.json` and `port-map.schema.json` data
- Enforces `SHIP_PAGE_STANDARD.md` structure for ship pages
- Auto-populates sections: Getting There, Getting Around, Must-See, Dining, Shopping, Beach/Excursion
- Validates against schema definitions before writing
- Integrates with voice hooks to maintain the site's tone

**Trigger:** When creating or editing port/ship HTML pages

**Deploy to:** InTheWake only

---

### 7. `nutrition-estimator` — For: Grandmasrecipes, Grannysrecipes, MomsRecipes, Allrecipes

**Problem:** `estimate_nutrition.py` exists in Grandmasrecipes but the skill layer is missing. Claude needs to know when/how to run it, how to interpret results, and how to handle edge cases (unclear measurements, regional ingredients).

**What it does:**
- Wraps `estimate_nutrition.py` with skill-level guidance
- Knows which recipes lack nutrition estimates and prioritizes them
- Handles unclear measurements (`[UNCLEAR]` tagged) by using conservative estimates
- Cross-validates estimates against similar recipes in the same collection
- Formats nutrition facts for ebook and web display
- Flags recipes with unusually high sodium/sugar for diabetic-converter compatibility

**Trigger:** After recipe transcription or when nutrition data is requested

**Deploy to:** Grandmasrecipes, Grannysrecipes, MomsRecipes, Allrecipes

---

### 8. `accessibility-audit` — For: InTheWake, flickersofmajesty

**Problem:** InTheWake explicitly targets WCAG 2.1 AA compliance and has an `accessibility.html` page and `disability-at-sea.html`. flickersofmajesty sells to a broad audience. Neither has an automated accessibility skill.

**What it does:**
- Checks `alt` text on all images (meaningful, not decorative-only)
- Validates color contrast ratios in CSS
- Checks heading hierarchy (no skipped levels)
- Validates ARIA labels on interactive elements (calculators, quizzes)
- Checks keyboard navigation paths for tools
- Verifies form labels and error states
- Reports WCAG 2.1 AA violations with fix suggestions

**Trigger:** PostToolUse on Edit/Write of `.html` or `.css` files

**Deploy to:** InTheWake, flickersofmajesty

---

### 9. `collection-sync` — For: Allrecipes (aggregator)

**Problem:** Allrecipes is the aggregator for Grandmasrecipes, Grannysrecipes, and MomsRecipes. Currently the `aggregate_collections.py` script exists but there's no skill ensuring the aggregator stays in sync with the individual collections.

**What it does:**
- Detects when individual recipe repos have been updated
- Identifies new/modified/deleted recipes that need aggregation
- Validates cross-collection search indexes are current
- Checks for duplicate recipes across collections (same dish, different grandma)
- Maintains a sync status report showing last-synced state per collection

**Trigger:** Session start or `/sync` command

**Deploy to:** Allrecipes only

---

### 10. `content-freshness` — For: InTheWake, flickersofmajesty

**Problem:** InTheWake has cruise content that becomes stale (ship itineraries change, restaurants close, ports update policies). flickersofmajesty product availability changes. No skill tracks content age or flags staleness.

**What it does:**
- Scans `last-reviewed` meta tags across all pages
- Flags pages not reviewed in >90 days (configurable)
- Prioritizes by traffic-sensitivity (port pages > ship pages > general articles)
- For InTheWake: checks if cruise line data is current season
- For flickersofmajesty: checks if product listings have current pricing
- Generates freshness report sorted by staleness

**Trigger:** `/freshness` command or session start check

**Deploy to:** InTheWake, flickersofmajesty

---

## Part B: Redeployment of Existing Skills

### Priority 0 — Critical Gaps

| Skill | Deploy To | Rationale |
|-------|----------|-----------|
| **cognitive-memory** | ken, Allrecipes, Grandmasrecipes, Grannysrecipes, MomsRecipes | Cross-session memory is foundational. 5 repos lack it. |
| **Post-write validation hooks** | MomsRecipes, Allrecipes | Recipe repos without any hooks — should match Grandmasrecipes/Grannysrecipes pattern |
| **Image-safety-check hooks** | MomsRecipes, Allrecipes | Prevent reading unprocessed originals when processed versions exist |

### Priority 1 — Consistency Gaps

| Skill | Deploy To | Rationale |
|-------|----------|-----------|
| **careful-not-clever** | Grandmasrecipes, Grannysrecipes | Accuracy-first repos without the integrity guardrail skill |
| **like-a-human** | InTheWake | Has Humanization but may not match the standard like-a-human provides |
| **voice-audit** | InTheWake | Has voice-audit-hook but not the full diagnostic skill |

### Priority 2 — Organizational Improvements

| Skill | Action | Rationale |
|-------|--------|-----------|
| **skill-developer** | Copy to ken | Hub should be the home for skill development |
| **skill-creator** | Move from flickersofmajesty to ken | Meta-skill belongs in the hub, not a domain repo |
| **cognitive-memory** | Already global in `~/.claude/skills/` | Verify repo-level copies aren't diverging from global version |

---

## Part C: Combined Priority Roadmap

| Priority | Action | Type | Repos |
|----------|--------|------|-------|
| **P0** | Deploy cognitive-memory to 5 missing repos | Redeploy | ken, Allrecipes, Grandmasrecipes, Grannysrecipes, MomsRecipes |
| **P0** | Add validation hooks to MomsRecipes & Allrecipes | Redeploy | MomsRecipes, Allrecipes |
| **P1** | Build `seo-schema-audit` | **NEW** | InTheWake, flickersofmajesty, 4 recipe repos |
| **P1** | Build `link-integrity` | **NEW** | InTheWake, flickersofmajesty |
| **P1** | Deploy careful-not-clever to Grandmasrecipes, Grannysrecipes | Redeploy | Grandmasrecipes, Grannysrecipes |
| **P2** | Build `ebook-builder` | **NEW** | Grandmasrecipes, Grannysrecipes, MomsRecipes |
| **P2** | Build `nutrition-estimator` | **NEW** | All 4 recipe repos |
| **P2** | Build `breeding-advisor` | **NEW** | manateecreeksheep |
| **P2** | Build `accessibility-audit` | **NEW** | InTheWake, flickersofmajesty |
| **P2** | Build `port-content-builder` | **NEW** | InTheWake |
| **P3** | Build `sermon-cross-reference` | **NEW** | Romans |
| **P3** | Build `collection-sync` | **NEW** | Allrecipes |
| **P3** | Build `content-freshness` | **NEW** | InTheWake, flickersofmajesty |
| **P3** | Move skill-creator/skill-developer to ken | Redeploy | ken, flickersofmajesty |

---

## Summary

- **10 new skills proposed** based on actual repo content, tooling, and gaps
- **8 redeployment actions** to standardize existing skills across repos
- Total: **18 action items** across all 9 repositories

*All new skills follow the existing SKILL.md format with YAML frontmatter, clear trigger conditions, and defined relationships to existing skills.*
