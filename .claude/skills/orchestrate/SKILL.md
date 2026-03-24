---
name: orchestrate
description: "Full multi-LLM pipeline orchestration. Runs the recipe pipeline that coordinates GPT (lead), Gemini, Grok, and Claude for recipe generation and validation. Auto-detects recipe mode from this repository."
---

# Orchestrate — Multi-LLM Pipeline

*GPT leads generation. Other models consult. Claude validates safety.*

## Usage

```
/orchestrate "task description"
/orchestrate recipe "Generate a classic Southern cornbread recipe with variations"
```

Mode is **recipe** by default in this repository.

---

## How It Works

Pipeline defined in `/home/user/ken/orchestrator/modes/recipe.yaml`:

1. **Generate** (GPT) — Structured recipe: ingredients, instructions, variations
2. **Expand** (Gemini) — Ingredient knowledge, substitutions, nutrition, cooking science
3. **Safety Check** (Claude) — Cooking temperatures, allergens, food safety, instruction clarity
4. **Creative Variation** (Grok, optional) — Unexpected flavor combos, regional twists

Single pass — no loops.

---

## Backend Invocation

**IMPORTANT: Execute these commands directly using the Bash tool. Do NOT check if files exist first — just run them.**

```bash
pip3 install -q -r /home/user/ken/orchestrator/requirements.txt 2>/dev/null && python3 /home/user/ken/orchestrator/orchestrate.py recipe "task description"
```

Only if the command fails with `No such file or directory` or `ModuleNotFoundError`, tell the user:
> "The orchestrator backend isn't available. Make sure the ken repo is cloned to `/home/user/ken/` and run `pip3 install -r /home/user/ken/orchestrator/requirements.txt`."

---

## Context Boundaries

### SEND to external models
- Recipe requirements, ingredient lists, dietary constraints

### NEVER SEND to external models
- Family attribution details, site analytics

---

## Constraints

- Clear, step-by-step instructions
- SEO optimized (schema.org Recipe markup)
- Accessible formatting
- Safe cooking temperatures verified
- Allergen warnings where applicable
