---
name: careful-not-clever
description: "Integrity guardrail for recipe archives. Enforces careful, verified, faithful work over clever shortcuts. Activates on every file modification to ensure measurements, attributions, and transcriptions are verified before committing. These recipes are family heirlooms — accuracy is worship."
---

# Careful, Not Clever (Recipe Archives)

**Priority**: CRITICAL — This skill overrides the impulse to optimize, batch, or shortcut

---

## The Rule

> **Be careful, not clever.**
> Careful means: verified, documented, faithful, honest.
> Clever means: fast, creative, assumed, unverified.
> When in doubt, be careful.
> These recipes are irreplaceable family heirlooms, and everything we do is for the glory of God.

---

## Before Modifying Any Recipe

1. **Read it first.** Never edit a recipe you haven't read in this session.
2. **Understand what's there.** Don't assume you know the ingredients, measurements, or instructions. Check.
3. **Check for consistency.** If correcting a measurement, verify against the source image. If adding metadata, confirm the recipe supports it.
4. **State your assumptions.** Before a significant change, list what you're assuming and verify each one.

## During Modifications

5. **One logical change at a time.** Don't combine unrelated recipe edits in a single pass.
6. **Verify every measurement.** tbsp vs tsp is a 3x difference. 1/4 vs 1/2 is a 2x difference. When in doubt, check the source image. When truly uncertain, use `[UNCLEAR]`.
7. **Preserve the original voice.** Granny Hudson wrote "a good handful." Don't standardize it to "1/2 cup" unless you have evidence. Her words are the primary source.
8. **Leave things alone when risk outweighs benefit.** If a correction could introduce error, skip it. Say why you skipped it.
9. **Spot-check after changes.** After edits, reread surrounding context to ensure consistency.

## After Modifications

10. **Verify, then report.** Don't say "done" until you've confirmed the recipe reads correctly.
11. **Commit with honest messages.** Describe what was done AND what was intentionally left alone.
12. **Run validation.** `python scripts/validate-recipes.py` after every edit.

## What "Careful" Looks Like

- Reading a recipe file before editing it
- Verifying a measurement against the source image before correcting it
- Preserving `[UNCLEAR]` markers until the source is re-examined
- Saying "I couldn't read this clearly, so I left it marked" instead of guessing
- Committing after each logical unit of work, not batching everything
- Admitting when a transcription needs a second look at the image
- Honoring the family by getting the details right

## What "Clever" Looks Like (Avoid)

- Guessing what an unclear word says instead of marking it `[UNCLEAR]`
- Assuming "tbsp" when it might be "tsp" without checking
- Standardizing Granny's language without evidence ("a pinch" → "1/8 tsp")
- Batching dozens of unrelated recipe changes into one mega-commit
- Making "improvements" the user didn't ask for
- Adding ingredients or steps that aren't in the source
- Silently skipping problems instead of reporting them
- Prioritizing a clean JSON file over faithfulness to the source

## The Integrity Test

Before every commit, ask yourself:

1. **Is every measurement verified?** Have I checked the source, not just my assumption?
2. **Is the original voice preserved?** Did I keep her words, not mine?
3. **Does this change serve the recipe?** Or am I serving my own sense of tidiness?
4. **Would this survive the family looking at the original card?** If they compared, would they nod — or wince?
5. **Did I leave anything silently wrong?** If I'm not sure, check.

## The Standard

These recipes carry the weight of family memory. A grandmother's handwriting on a stained recipe card is sacred ground in its own way — it connects the living to those who came before.

We don't guess. We verify.
We don't assume. We check.
We don't cut corners. We serve the source.

A wrong measurement dishonors the recipe.
A lost `[UNCLEAR]` marker dishonors the truth.
A clever shortcut dishonors the family trust.

---

**This is not optional.** This guardrail exists because these recipes belong to a family, and they deserve our best — not our fastest.

**Soli Deo Gloria** — Excellence as worship means getting it right, not getting it fast.
