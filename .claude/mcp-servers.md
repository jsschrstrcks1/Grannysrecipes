# MCP Servers for Granny Hudson's Recipe Archive

Model Context Protocol (MCP) servers can enhance recipe management with nutritional analysis, ingredient verification, and more.

---

## Recommended MCP Servers

### 1. Kitchen MCP Server

**Purpose:** Ingredient queries, nutritional information, recipe recommendations

**Use Cases:**
- Look up nutrition for specific ingredients
- Find ingredient substitutions
- Verify ingredient compatibility

**Tool Pattern:** `mcp__kitchen__<tool>`

---

### 2. OpenNutrition MCP Server

**Purpose:** Comprehensive nutritional database (300,000+ food items)

**Features:**
- USDA food database access
- International food databases
- Offline capability after initial setup

**Priority:** HIGH — Best for offline use, no API key required

**Tool Pattern:** `mcp__opennutrition__<tool>`

---

### 3. Spoonacular MCP Server

**Purpose:** Recipe search, nutrition analysis, substitutions

**Features:**
- Search similar recipes
- Detailed nutrition analysis
- Ingredient substitution finder

**Note:** Requires API key

**Tool Pattern:** `mcp__spoonacular__<tool>`

---

### 4. MealDB MCP Server

**Purpose:** Recipe cross-reference via TheMealDB

**Features:**
- Search recipes by name
- Category browsing
- No API key for basic use

**Tool Pattern:** `mcp__mealdb__<tool>`

---

## Integration Patterns

### Ingredient Substitution Lookup

```
User: "The recipe calls for buttermilk but I don't have any"

Workflow:
1. Query mcp__kitchen__substitution or mcp__spoonacular__substitute
2. Suggest: "1 cup milk + 1 tbsp lemon juice"
3. Add note to recipe if user confirms
```

### Nutrition Enhancement

```
User: "Add nutrition info to this recipe"

Workflow:
1. Parse ingredients from recipe
2. Query mcp__opennutrition__lookup for each ingredient
3. Calculate per-serving totals
4. Add to recipe.nutrition field
```

### Recipe Verification

```
User: "Does this ingredient list make sense?"

Workflow:
1. Search mcp__mealdb__search for similar recipes
2. Compare ingredient ratios
3. Flag any unusual amounts
```

---

## Configuration Example

```json
{
  "mcpServers": {
    "opennutrition": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-opennutrition"]
    },
    "kitchen": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-kitchen"]
    }
  }
}
```

---

## Priority Ranking

| Server | Priority | Reason |
|--------|----------|--------|
| OpenNutrition | HIGH | Offline, no API key, comprehensive |
| Kitchen | MEDIUM | General purpose, good for substitutions |
| MealDB | LOW | Recipe cross-reference only |
| Spoonacular | LOW | Requires API key |

---

## Future Considerations

- **Mealie MCP** — If migrating to self-hosted recipe system
- **OpenFoodFacts MCP** — For branded product information

---

## Usage Notes

1. MCP servers are optional enhancements
2. Core functionality works without any MCP servers
3. Install based on specific needs (nutrition, substitutions, etc.)
4. Always verify MCP suggestions against original recipes

---

*Last updated: 2026-01*
