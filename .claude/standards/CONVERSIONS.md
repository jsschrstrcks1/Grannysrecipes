# Measurement Conversions — Granny's Archive

## Rules

1. **Always preserve original units** — never replace what was written.
2. Provide metric conversions as a **separate, optional view**.
3. Label conversions clearly: "Converted (approx.)".
4. **Never convert `[UNCLEAR]` amounts** — only confirmed values.
5. Include both °F and °C for all oven temperatures.

## US → Metric Standard Table

| US Measure | Metric | Notes |
|---|---|---|
| 1 cup all-purpose flour | 120 g | Spooned & leveled |
| 1 cup bread flour | 130 g | |
| 1 cup cake flour | 115 g | |
| 1 cup granulated sugar | 200 g | |
| 1 cup brown sugar (packed) | 220 g | |
| 1 cup powdered sugar | 120 g | Sifted |
| 1 cup butter | 227 g (2 sticks) | |
| 1 tbsp butter | 14 g | |
| 1 cup milk / water / liquid | 240 ml | |
| 1 cup sour cream / yogurt | 240 g | |
| 1 cup honey / syrup | 340 g | |
| 1 oz | 28 g | |
| 1 lb | 454 g | |

## Temperature Conversions

| °F | °C | Description |
|---|---|---|
| 250 | 120 | Very low |
| 300 | 150 | Low |
| 325 | 165 | Low-moderate |
| 350 | 175 | Moderate |
| 375 | 190 | Moderate-high |
| 400 | 200 | Hot |
| 425 | 220 | Hot |
| 450 | 230 | Very hot |
| 475 | 245 | Very hot |
| 500 | 260 | Extremely hot |

## Conversion JSON Structure

```json
"conversions": {
  "has_conversions": true,
  "conversion_assumptions": [
    "All-purpose flour: 1 cup = 120g (spooned & leveled)"
  ],
  "ingredients_metric": [
    {"item": "flour", "quantity": "330", "unit": "g", "prep_note": "sifted"}
  ],
  "temperature_c": "190°C"
}
```
