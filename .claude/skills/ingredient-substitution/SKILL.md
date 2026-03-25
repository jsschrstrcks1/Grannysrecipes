---
name: ingredient-substitution
description: "Knows common ingredient substitutions and validates they don't break recipes. Handles dairy-free, gluten-free, egg-free, sugar-free, and altitude adjustments."
version: 1.0.0
---

# Ingredient Substitution — Granny Hudson's Kitchen

> Adapt the recipe. Preserve the dish.

## Purpose

Suggests safe ingredient substitutions for dietary restrictions, allergies, or ingredient availability — while validating that the substitution won't break the recipe's chemistry or character.

## When to Fire

- On `/sub` command
- When discussing dietary restrictions, allergies, or ingredient availability
- When a recipe contains an ingredient someone can't eat
- When suggesting alternatives for [UNCLEAR] ingredients

## Common Substitutions

### Dairy-Free
| Original | Substitute | Notes |
|----------|-----------|-------|
| Butter | Coconut oil (baking), olive oil (savory) | 1:1 ratio. Coconut oil changes flavor in delicate recipes. |
| Milk | Oat milk (baking), almond milk (drinking) | Oat milk is thickest, best for baking. |
| Heavy cream | Full-fat coconut cream | Refrigerate can, use solid part only. |
| Sour cream | Coconut cream + lemon juice | Works in baking, not as a topping. |
| Cream cheese | Cashew cream cheese | Texture differs. Works in dips, not cheesecake. |

### Gluten-Free
| Original | Substitute | Notes |
|----------|-----------|-------|
| All-purpose flour | 1:1 GF blend (Bob's Red Mill) | Add 1/4 tsp xanthan gum per cup if blend doesn't include it. |
| Breadcrumbs | Crushed GF crackers or almond flour | Almond flour browns faster — reduce temp 25°F. |
| Soy sauce | Tamari or coconut aminos | Tamari is closest in flavor. |

### Egg-Free
| Original | Substitute | Notes |
|----------|-----------|-------|
| 1 egg (binding) | 1 tbsp ground flaxseed + 3 tbsp water | Let sit 5 min to gel. Works in muffins, pancakes. |
| 1 egg (leavening) | 1/4 cup applesauce + 1/2 tsp baking powder | Adds moisture and slight sweetness. |
| 1 egg (richness) | 3 tbsp aquafaba (chickpea water) | Whips like egg whites. Best for meringues. |

### Sugar-Free / Diabetic
| Original | Substitute | Notes |
|----------|-----------|-------|
| White sugar | Erythritol or monk fruit (baking) | 70% as sweet — adjust to taste. |
| Brown sugar | Erythritol + molasses (1 tbsp/cup) | Mimics moisture and flavor. |
| Honey | Sugar-free maple syrup | Won't caramelize the same way. |

### Altitude Adjustments (3,500+ ft)
- Reduce sugar by 1 tbsp per cup
- Increase liquid by 2-4 tbsp per cup
- Increase oven temp by 15-25°F
- Reduce baking powder by 1/8 tsp per tsp

## Validation Rules

Before suggesting a substitution, check:

1. **Is this a baking recipe?** Baking chemistry is fragile. Substitutions must maintain moisture, structure, and leavening balance.
2. **Is the ingredient structural?** Flour, eggs, and fat are structural. Substituting them changes the recipe fundamentally. Flag this.
3. **Does the substitution change flavor significantly?** Coconut oil in a savory dish is noticeable. Note it.
4. **Is this a family recipe with emotional weight?** Don't suggest changing Granny Hudson's signature recipe — offer a variation instead.

## Integration

- **recipe-validation** — validate substituted recipes still pass
- **nutrition-estimator** — recalculate nutrition after substitution
- **careful-not-clever** — never guess a substitution ratio. Use verified data.

---

*Soli Deo Gloria* — Adapt with care. Every recipe matters to someone.
