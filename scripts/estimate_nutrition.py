#!/usr/bin/env python3
"""
Nutrition Estimation Script for Granny Hudson's Recipe Archive

Estimates nutritional information based on ingredient lists and standard
nutritional values. Results are approximations suitable for home cooking.

Usage:
    python scripts/estimate_nutrition.py [--dry-run] [--recipe-id ID] [--force]

Options:
    --dry-run      Preview nutrition estimates without saving
    --recipe-id    Estimate for a specific recipe only
    --force        Re-estimate all recipes (even those with existing nutrition)
"""

import json
import re
import sys
from fractions import Fraction
from pathlib import Path

# =============================================================================
# Nutrition Database (per standard measure)
# Values are approximate and based on USDA data
# Format: {ingredient: {unit: {calories, fat_g, carbs_g, protein_g, sodium_mg, fiber_g, sugar_g}}}
# =============================================================================

NUTRITION_DB = {
    # PROTEINS
    'chicken breast': {'oz': {'cal': 46, 'fat': 1, 'carb': 0, 'protein': 9, 'sodium': 20, 'fiber': 0, 'sugar': 0}},
    'chicken': {'lb': {'cal': 800, 'fat': 48, 'carb': 0, 'protein': 88, 'sodium': 320, 'fiber': 0, 'sugar': 0}},
    'ground beef': {'lb': {'cal': 1152, 'fat': 88, 'carb': 0, 'protein': 80, 'sodium': 320, 'fiber': 0, 'sugar': 0}},
    'extra-lean ground beef': {'lb': {'cal': 800, 'fat': 48, 'carb': 0, 'protein': 88, 'sodium': 300, 'fiber': 0, 'sugar': 0}},
    'bacon': {'slice': {'cal': 43, 'fat': 3.3, 'carb': 0.1, 'protein': 3, 'sodium': 137, 'fiber': 0, 'sugar': 0}},
    'pork chops': {'oz': {'cal': 52, 'fat': 2.5, 'carb': 0, 'protein': 7, 'sodium': 18, 'fiber': 0, 'sugar': 0}},
    'pork loin': {'lb': {'cal': 800, 'fat': 32, 'carb': 0, 'protein': 120, 'sodium': 280, 'fiber': 0, 'sugar': 0}},
    'pork': {'lb': {'cal': 1000, 'fat': 64, 'carb': 0, 'protein': 100, 'sodium': 280, 'fiber': 0, 'sugar': 0}},
    'spareribs': {'lb': {'cal': 1200, 'fat': 96, 'carb': 0, 'protein': 80, 'sodium': 400, 'fiber': 0, 'sugar': 0}},
    'ham': {'oz': {'cal': 46, 'fat': 2.4, 'carb': 0.4, 'protein': 5.5, 'sodium': 365, 'fiber': 0, 'sugar': 0}},
    'shrimp': {'oz': {'cal': 30, 'fat': 0.5, 'carb': 0.3, 'protein': 6, 'sodium': 55, 'fiber': 0, 'sugar': 0}},
    'crabmeat': {'oz': {'cal': 25, 'fat': 0.4, 'carb': 0, 'protein': 5, 'sodium': 95, 'fiber': 0, 'sugar': 0}},
    'clams': {'oz': {'cal': 21, 'fat': 0.3, 'carb': 1, 'protein': 3.6, 'sodium': 32, 'fiber': 0, 'sugar': 0}},
    'fish': {'oz': {'cal': 35, 'fat': 0.8, 'carb': 0, 'protein': 7, 'sodium': 45, 'fiber': 0, 'sugar': 0}},
    'swordfish': {'oz': {'cal': 41, 'fat': 1.4, 'carb': 0, 'protein': 6.7, 'sodium': 30, 'fiber': 0, 'sugar': 0}},
    'red snapper': {'oz': {'cal': 28, 'fat': 0.4, 'carb': 0, 'protein': 5.8, 'sodium': 18, 'fiber': 0, 'sugar': 0}},
    'cod': {'oz': {'cal': 23, 'fat': 0.2, 'carb': 0, 'protein': 5, 'sodium': 18, 'fiber': 0, 'sugar': 0}},
    'turkey': {'lb': {'cal': 720, 'fat': 32, 'carb': 0, 'protein': 100, 'sodium': 280, 'fiber': 0, 'sugar': 0}},
    'lamb': {'lb': {'cal': 1100, 'fat': 80, 'carb': 0, 'protein': 88, 'sodium': 280, 'fiber': 0, 'sugar': 0}},
    'cornish hen': {'each': {'cal': 500, 'fat': 28, 'carb': 0, 'protein': 60, 'sodium': 200, 'fiber': 0, 'sugar': 0}},
    'corned beef': {'oz': {'cal': 71, 'fat': 5.4, 'carb': 0.4, 'protein': 5, 'sodium': 285, 'fiber': 0, 'sugar': 0}},
    'sausage': {'oz': {'cal': 82, 'fat': 7, 'carb': 0.4, 'protein': 4, 'sodium': 230, 'fiber': 0, 'sugar': 0}},
    'egg': {'large': {'cal': 72, 'fat': 5, 'carb': 0.4, 'protein': 6, 'sodium': 71, 'fiber': 0, 'sugar': 0}},
    'eggs': {'large': {'cal': 72, 'fat': 5, 'carb': 0.4, 'protein': 6, 'sodium': 71, 'fiber': 0, 'sugar': 0}},

    # DAIRY
    'butter': {'cup': {'cal': 1628, 'fat': 184, 'carb': 0, 'protein': 2, 'sodium': 1284, 'fiber': 0, 'sugar': 0},
               'tbsp': {'cal': 102, 'fat': 11.5, 'carb': 0, 'protein': 0.1, 'sodium': 80, 'fiber': 0, 'sugar': 0}},
    'margarine': {'cup': {'cal': 1628, 'fat': 184, 'carb': 0, 'protein': 2, 'sodium': 1284, 'fiber': 0, 'sugar': 0},
                  'tbsp': {'cal': 102, 'fat': 11.5, 'carb': 0, 'protein': 0.1, 'sodium': 80, 'fiber': 0, 'sugar': 0}},
    'milk': {'cup': {'cal': 149, 'fat': 8, 'carb': 12, 'protein': 8, 'sodium': 107, 'fiber': 0, 'sugar': 12}},
    'heavy cream': {'cup': {'cal': 821, 'fat': 88, 'carb': 7, 'protein': 5, 'sodium': 89, 'fiber': 0, 'sugar': 7}},
    'sour cream': {'cup': {'cal': 445, 'fat': 44, 'carb': 8, 'protein': 6, 'sodium': 123, 'fiber': 0, 'sugar': 5}},
    'cream cheese': {'oz': {'cal': 99, 'fat': 10, 'carb': 1, 'protein': 2, 'sodium': 84, 'fiber': 0, 'sugar': 1}},
    'cheddar cheese': {'cup': {'cal': 455, 'fat': 37, 'carb': 1.5, 'protein': 28, 'sodium': 700, 'fiber': 0, 'sugar': 0}},
    'mozzarella cheese': {'cup': {'cal': 316, 'fat': 20, 'carb': 4, 'protein': 28, 'sodium': 632, 'fiber': 0, 'sugar': 1}},
    'parmesan cheese': {'tbsp': {'cal': 22, 'fat': 1.4, 'carb': 0.2, 'protein': 2, 'sodium': 76, 'fiber': 0, 'sugar': 0}},
    'cheese': {'cup': {'cal': 400, 'fat': 32, 'carb': 2, 'protein': 24, 'sodium': 650, 'fiber': 0, 'sugar': 0}},
    'evaporated milk': {'cup': {'cal': 338, 'fat': 19, 'carb': 25, 'protein': 17, 'sodium': 266, 'fiber': 0, 'sugar': 25}},
    'sweetened condensed milk': {'cup': {'cal': 982, 'fat': 27, 'carb': 166, 'protein': 24, 'sodium': 389, 'fiber': 0, 'sugar': 166}},
    'cool whip': {'cup': {'cal': 200, 'fat': 14, 'carb': 18, 'protein': 1, 'sodium': 20, 'fiber': 0, 'sugar': 14}},
    'whipped topping': {'cup': {'cal': 200, 'fat': 14, 'carb': 18, 'protein': 1, 'sodium': 20, 'fiber': 0, 'sugar': 14}},
    'cottage cheese': {'cup': {'cal': 220, 'fat': 10, 'carb': 6, 'protein': 26, 'sodium': 820, 'fiber': 0, 'sugar': 6}},
    'yogurt': {'cup': {'cal': 150, 'fat': 8, 'carb': 12, 'protein': 8, 'sodium': 115, 'fiber': 0, 'sugar': 12}},

    # GRAINS & STARCHES
    'flour': {'cup': {'cal': 455, 'fat': 1.2, 'carb': 95, 'protein': 13, 'sodium': 3, 'fiber': 3, 'sugar': 0}},
    'all-purpose flour': {'cup': {'cal': 455, 'fat': 1.2, 'carb': 95, 'protein': 13, 'sodium': 3, 'fiber': 3, 'sugar': 0}},
    'bread flour': {'cup': {'cal': 455, 'fat': 1.5, 'carb': 95, 'protein': 15, 'sodium': 3, 'fiber': 3, 'sugar': 0}},
    'cake flour': {'cup': {'cal': 400, 'fat': 0.8, 'carb': 88, 'protein': 9, 'sodium': 3, 'fiber': 2, 'sugar': 0}},
    'oats': {'cup': {'cal': 307, 'fat': 5, 'carb': 55, 'protein': 11, 'sodium': 5, 'fiber': 8, 'sugar': 1}},
    'rice': {'cup': {'cal': 206, 'fat': 0.4, 'carb': 45, 'protein': 4, 'sodium': 2, 'fiber': 0.6, 'sugar': 0}},
    'pasta': {'oz': {'cal': 100, 'fat': 0.5, 'carb': 20, 'protein': 3.5, 'sodium': 1, 'fiber': 1, 'sugar': 0}},
    'linguine': {'oz': {'cal': 100, 'fat': 0.5, 'carb': 20, 'protein': 3.5, 'sodium': 1, 'fiber': 1, 'sugar': 0}},
    'noodles': {'cup': {'cal': 220, 'fat': 2, 'carb': 40, 'protein': 8, 'sodium': 10, 'fiber': 2, 'sugar': 0}},
    'bread crumbs': {'cup': {'cal': 427, 'fat': 6, 'carb': 78, 'protein': 14, 'sodium': 930, 'fiber': 3, 'sugar': 6}},
    'hamburger bun': {'each': {'cal': 120, 'fat': 2, 'carb': 21, 'protein': 4, 'sodium': 200, 'fiber': 1, 'sugar': 3}},
    'biscuit mix': {'cup': {'cal': 480, 'fat': 16, 'carb': 72, 'protein': 8, 'sodium': 1360, 'fiber': 2, 'sugar': 8}},
    'cornmeal': {'cup': {'cal': 442, 'fat': 4, 'carb': 94, 'protein': 10, 'sodium': 4, 'fiber': 9, 'sugar': 1}},
    'tortilla': {'each': {'cal': 90, 'fat': 2.5, 'carb': 15, 'protein': 2, 'sodium': 200, 'fiber': 1, 'sugar': 0}},
    'crescent rolls': {'each': {'cal': 100, 'fat': 5, 'carb': 11, 'protein': 2, 'sodium': 220, 'fiber': 0, 'sugar': 2}},
    'croissant': {'each': {'cal': 230, 'fat': 12, 'carb': 26, 'protein': 5, 'sodium': 310, 'fiber': 1, 'sugar': 6}},
    'puff pastry': {'sheet': {'cal': 900, 'fat': 60, 'carb': 72, 'protein': 12, 'sodium': 360, 'fiber': 2, 'sugar': 2}},
    'pie crust': {'each': {'cal': 650, 'fat': 40, 'carb': 64, 'protein': 8, 'sodium': 400, 'fiber': 2, 'sugar': 2}},
    'graham cracker crust': {'each': {'cal': 800, 'fat': 36, 'carb': 112, 'protein': 8, 'sodium': 600, 'fiber': 2, 'sugar': 40}},
    'tater tots': {'cup': {'cal': 200, 'fat': 10, 'carb': 24, 'protein': 2, 'sodium': 400, 'fiber': 2, 'sugar': 0}},
    'potato': {'medium': {'cal': 163, 'fat': 0.2, 'carb': 37, 'protein': 4, 'sodium': 13, 'fiber': 4, 'sugar': 2}},
    'potatoes': {'lb': {'cal': 350, 'fat': 0.4, 'carb': 80, 'protein': 9, 'sodium': 28, 'fiber': 9, 'sugar': 4}},
    'sweet potato': {'medium': {'cal': 103, 'fat': 0.1, 'carb': 24, 'protein': 2, 'sodium': 41, 'fiber': 4, 'sugar': 7}},

    # SUGARS & SWEETENERS
    'sugar': {'cup': {'cal': 774, 'fat': 0, 'carb': 200, 'protein': 0, 'sodium': 2, 'fiber': 0, 'sugar': 200},
              'tbsp': {'cal': 48, 'fat': 0, 'carb': 12.5, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 12.5},
              'tsp': {'cal': 16, 'fat': 0, 'carb': 4, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 4}},
    'granulated sugar': {'cup': {'cal': 774, 'fat': 0, 'carb': 200, 'protein': 0, 'sodium': 2, 'fiber': 0, 'sugar': 200},
                         'tbsp': {'cal': 48, 'fat': 0, 'carb': 12.5, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 12.5},
                         'tsp': {'cal': 16, 'fat': 0, 'carb': 4, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 4}},
    'brown sugar': {'cup': {'cal': 829, 'fat': 0, 'carb': 214, 'protein': 0, 'sodium': 57, 'fiber': 0, 'sugar': 212},
                    'tbsp': {'cal': 52, 'fat': 0, 'carb': 13.4, 'protein': 0, 'sodium': 4, 'fiber': 0, 'sugar': 13.3},
                    'tsp': {'cal': 17, 'fat': 0, 'carb': 4.5, 'protein': 0, 'sodium': 1, 'fiber': 0, 'sugar': 4.4}},
    'powdered sugar': {'cup': {'cal': 467, 'fat': 0, 'carb': 119, 'protein': 0, 'sodium': 1, 'fiber': 0, 'sugar': 117},
                       'tbsp': {'cal': 29, 'fat': 0, 'carb': 7.4, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 7.3}},
    'confectioners sugar': {'cup': {'cal': 467, 'fat': 0, 'carb': 119, 'protein': 0, 'sodium': 1, 'fiber': 0, 'sugar': 117},
                            'tbsp': {'cal': 29, 'fat': 0, 'carb': 7.4, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 7.3}},
    'honey': {'tbsp': {'cal': 64, 'fat': 0, 'carb': 17, 'protein': 0.1, 'sodium': 1, 'fiber': 0, 'sugar': 17},
              'cup': {'cal': 1031, 'fat': 0, 'carb': 279, 'protein': 1, 'sodium': 14, 'fiber': 0, 'sugar': 278}},
    'maple syrup': {'tbsp': {'cal': 52, 'fat': 0, 'carb': 13, 'protein': 0, 'sodium': 2, 'fiber': 0, 'sugar': 12},
                    'cup': {'cal': 840, 'fat': 0, 'carb': 216, 'protein': 0, 'sodium': 28, 'fiber': 0, 'sugar': 192}},
    'corn syrup': {'cup': {'cal': 925, 'fat': 0, 'carb': 251, 'protein': 0, 'sodium': 395, 'fiber': 0, 'sugar': 153},
                   'tbsp': {'cal': 58, 'fat': 0, 'carb': 16, 'protein': 0, 'sodium': 25, 'fiber': 0, 'sugar': 10}},
    'molasses': {'tbsp': {'cal': 58, 'fat': 0, 'carb': 15, 'protein': 0, 'sodium': 7, 'fiber': 0, 'sugar': 11}},

    # OILS & FATS
    'olive oil': {'tbsp': {'cal': 119, 'fat': 14, 'carb': 0, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0}},
    'vegetable oil': {'tbsp': {'cal': 120, 'fat': 14, 'carb': 0, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0}},
    'oil': {'tbsp': {'cal': 120, 'fat': 14, 'carb': 0, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0}},
    'shortening': {'cup': {'cal': 1845, 'fat': 205, 'carb': 0, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0}},
    'mayonnaise': {'tbsp': {'cal': 94, 'fat': 10, 'carb': 0.1, 'protein': 0.1, 'sodium': 88, 'fiber': 0, 'sugar': 0}},

    # VEGETABLES
    'onion': {'medium': {'cal': 44, 'fat': 0.1, 'carb': 10, 'protein': 1.2, 'sodium': 4, 'fiber': 2, 'sugar': 5}},
    'garlic': {'clove': {'cal': 4, 'fat': 0, 'carb': 1, 'protein': 0.2, 'sodium': 1, 'fiber': 0, 'sugar': 0}},
    'tomato': {'medium': {'cal': 22, 'fat': 0.2, 'carb': 5, 'protein': 1, 'sodium': 6, 'fiber': 1.5, 'sugar': 3}},
    'tomatoes': {'can': {'cal': 80, 'fat': 0.4, 'carb': 16, 'protein': 4, 'sodium': 600, 'fiber': 4, 'sugar': 10}},
    'diced tomatoes': {'can': {'cal': 80, 'fat': 0.4, 'carb': 16, 'protein': 4, 'sodium': 600, 'fiber': 4, 'sugar': 10}},
    'tomato sauce': {'cup': {'cal': 59, 'fat': 0.5, 'carb': 13, 'protein': 2.5, 'sodium': 1284, 'fiber': 3, 'sugar': 8}},
    'tomato paste': {'tbsp': {'cal': 13, 'fat': 0.1, 'carb': 3, 'protein': 0.7, 'sodium': 130, 'fiber': 0.7, 'sugar': 2}},
    'mushrooms': {'cup': {'cal': 15, 'fat': 0.2, 'carb': 2, 'protein': 2, 'sodium': 4, 'fiber': 0.7, 'sugar': 1}},
    'green pepper': {'medium': {'cal': 24, 'fat': 0.2, 'carb': 6, 'protein': 1, 'sodium': 4, 'fiber': 2, 'sugar': 3}},
    'bell pepper': {'medium': {'cal': 24, 'fat': 0.2, 'carb': 6, 'protein': 1, 'sodium': 4, 'fiber': 2, 'sugar': 3}},
    'celery': {'stalk': {'cal': 6, 'fat': 0.1, 'carb': 1, 'protein': 0.3, 'sodium': 32, 'fiber': 0.6, 'sugar': 0.5}},
    'carrot': {'medium': {'cal': 25, 'fat': 0.1, 'carb': 6, 'protein': 0.6, 'sodium': 42, 'fiber': 1.7, 'sugar': 3}},
    'broccoli': {'cup': {'cal': 31, 'fat': 0.3, 'carb': 6, 'protein': 2.5, 'sodium': 30, 'fiber': 2, 'sugar': 1.5}},
    'corn': {'cup': {'cal': 132, 'fat': 1.8, 'carb': 29, 'protein': 5, 'sodium': 23, 'fiber': 3.6, 'sugar': 5}},
    'green beans': {'cup': {'cal': 31, 'fat': 0.1, 'carb': 7, 'protein': 2, 'sodium': 6, 'fiber': 3, 'sugar': 1.5}},
    'peas': {'cup': {'cal': 117, 'fat': 0.6, 'carb': 21, 'protein': 8, 'sodium': 7, 'fiber': 7, 'sugar': 8}},
    'lettuce': {'cup': {'cal': 5, 'fat': 0.1, 'carb': 1, 'protein': 0.5, 'sodium': 5, 'fiber': 0.5, 'sugar': 0.5}},
    'spinach': {'cup': {'cal': 7, 'fat': 0.1, 'carb': 1, 'protein': 0.9, 'sodium': 24, 'fiber': 0.7, 'sugar': 0}},
    'cabbage': {'cup': {'cal': 17, 'fat': 0.1, 'carb': 4, 'protein': 1, 'sodium': 13, 'fiber': 1.8, 'sugar': 2}},
    'zucchini': {'medium': {'cal': 31, 'fat': 0.4, 'carb': 7, 'protein': 2, 'sodium': 16, 'fiber': 2, 'sugar': 5}},
    'avocado': {'each': {'cal': 322, 'fat': 29, 'carb': 17, 'protein': 4, 'sodium': 14, 'fiber': 13, 'sugar': 1}},
    'beets': {'cup': {'cal': 58, 'fat': 0.2, 'carb': 13, 'protein': 2, 'sodium': 106, 'fiber': 4, 'sugar': 9}},

    # FRUITS
    'banana': {'medium': {'cal': 105, 'fat': 0.4, 'carb': 27, 'protein': 1.3, 'sodium': 1, 'fiber': 3, 'sugar': 14}},
    'apple': {'medium': {'cal': 95, 'fat': 0.3, 'carb': 25, 'protein': 0.5, 'sodium': 2, 'fiber': 4, 'sugar': 19}},
    'lemon juice': {'tbsp': {'cal': 3, 'fat': 0, 'carb': 1, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0.4}},
    'lime juice': {'tbsp': {'cal': 4, 'fat': 0, 'carb': 1, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0.3}},
    'orange juice': {'cup': {'cal': 112, 'fat': 0.5, 'carb': 26, 'protein': 2, 'sodium': 2, 'fiber': 0.5, 'sugar': 21}},
    'pineapple': {'cup': {'cal': 82, 'fat': 0.2, 'carb': 22, 'protein': 0.9, 'sodium': 2, 'fiber': 2, 'sugar': 16}},
    'strawberries': {'cup': {'cal': 49, 'fat': 0.5, 'carb': 12, 'protein': 1, 'sodium': 1, 'fiber': 3, 'sugar': 7}},
    'blueberries': {'cup': {'cal': 84, 'fat': 0.5, 'carb': 21, 'protein': 1, 'sodium': 1, 'fiber': 4, 'sugar': 15}},
    'cranberries': {'cup': {'cal': 46, 'fat': 0.1, 'carb': 12, 'protein': 0.5, 'sodium': 2, 'fiber': 5, 'sugar': 4}},
    'raisins': {'cup': {'cal': 434, 'fat': 0.7, 'carb': 115, 'protein': 5, 'sodium': 17, 'fiber': 5, 'sugar': 86}},
    'coconut': {'cup': {'cal': 283, 'fat': 27, 'carb': 12, 'protein': 3, 'sodium': 16, 'fiber': 7, 'sugar': 5}},
    'peach': {'medium': {'cal': 59, 'fat': 0.4, 'carb': 14, 'protein': 1, 'sodium': 0, 'fiber': 2, 'sugar': 13}},
    'cherry': {'cup': {'cal': 87, 'fat': 0.3, 'carb': 22, 'protein': 1.5, 'sodium': 0, 'fiber': 3, 'sugar': 18}},
    'pumpkin': {'cup': {'cal': 83, 'fat': 0.3, 'carb': 20, 'protein': 3, 'sodium': 12, 'fiber': 3, 'sugar': 8}},

    # NUTS & SEEDS
    'walnuts': {'cup': {'cal': 765, 'fat': 76, 'carb': 16, 'protein': 18, 'sodium': 2, 'fiber': 8, 'sugar': 3}},
    'pecans': {'cup': {'cal': 753, 'fat': 78, 'carb': 15, 'protein': 10, 'sodium': 0, 'fiber': 10, 'sugar': 4}},
    'almonds': {'cup': {'cal': 828, 'fat': 72, 'carb': 28, 'protein': 30, 'sodium': 1, 'fiber': 16, 'sugar': 6}},
    'peanuts': {'cup': {'cal': 854, 'fat': 72, 'carb': 24, 'protein': 35, 'sodium': 26, 'fiber': 12, 'sugar': 6}},
    'peanut butter': {'tbsp': {'cal': 94, 'fat': 8, 'carb': 3, 'protein': 4, 'sodium': 73, 'fiber': 1, 'sugar': 1}},

    # CHOCOLATE & BAKING
    'chocolate chips': {'cup': {'cal': 805, 'fat': 50, 'carb': 92, 'protein': 7, 'sodium': 18, 'fiber': 8, 'sugar': 80}},
    'cocoa powder': {'tbsp': {'cal': 12, 'fat': 0.7, 'carb': 3, 'protein': 1, 'sodium': 1, 'fiber': 2, 'sugar': 0}},
    'chocolate': {'oz': {'cal': 155, 'fat': 9, 'carb': 17, 'protein': 1.4, 'sodium': 7, 'fiber': 2, 'sugar': 14}},
    'vanilla': {'tsp': {'cal': 12, 'fat': 0, 'carb': 0.5, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0.5}},
    'vanilla extract': {'tsp': {'cal': 12, 'fat': 0, 'carb': 0.5, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0.5}},
    'baking soda': {'tsp': {'cal': 0, 'fat': 0, 'carb': 0, 'protein': 0, 'sodium': 1260, 'fiber': 0, 'sugar': 0}},
    'baking powder': {'tsp': {'cal': 2, 'fat': 0, 'carb': 1, 'protein': 0, 'sodium': 488, 'fiber': 0, 'sugar': 0}},
    'yeast': {'packet': {'cal': 21, 'fat': 0.3, 'carb': 3, 'protein': 3, 'sodium': 4, 'fiber': 1, 'sugar': 0}},
    'gelatin': {'packet': {'cal': 23, 'fat': 0, 'carb': 0, 'protein': 6, 'sodium': 14, 'fiber': 0, 'sugar': 0}},
    'jello': {'package': {'cal': 80, 'fat': 0, 'carb': 19, 'protein': 2, 'sodium': 120, 'fiber': 0, 'sugar': 19}},
    'pudding mix': {'package': {'cal': 140, 'fat': 0, 'carb': 35, 'protein': 0, 'sodium': 340, 'fiber': 0, 'sugar': 28}},
    'cake mix': {'package': {'cal': 1600, 'fat': 32, 'carb': 312, 'protein': 16, 'sodium': 2800, 'fiber': 4, 'sugar': 168}},

    # CANNED GOODS
    'cream of mushroom soup': {'can': {'cal': 225, 'fat': 15, 'carb': 18, 'protein': 4, 'sodium': 2175, 'fiber': 1, 'sugar': 2}},
    'cream of chicken soup': {'can': {'cal': 225, 'fat': 15, 'carb': 18, 'protein': 5, 'sodium': 2175, 'fiber': 1, 'sugar': 2}},
    'chicken broth': {'cup': {'cal': 15, 'fat': 0.5, 'carb': 1, 'protein': 2, 'sodium': 860, 'fiber': 0, 'sugar': 0}},
    'beef broth': {'cup': {'cal': 17, 'fat': 0.5, 'carb': 0.1, 'protein': 3, 'sodium': 893, 'fiber': 0, 'sugar': 0}},
    'vegetable broth': {'cup': {'cal': 12, 'fat': 0.2, 'carb': 2, 'protein': 0.5, 'sodium': 940, 'fiber': 0, 'sugar': 1}},
    'beans': {'cup': {'cal': 225, 'fat': 1, 'carb': 40, 'protein': 15, 'sodium': 400, 'fiber': 12, 'sugar': 1}},
    'pie filling': {'can': {'cal': 840, 'fat': 0, 'carb': 210, 'protein': 0, 'sodium': 100, 'fiber': 4, 'sugar': 180}},
    'pineapple': {'can': {'cal': 280, 'fat': 0.4, 'carb': 68, 'protein': 2, 'sodium': 4, 'fiber': 4, 'sugar': 60}},

    # CONDIMENTS & SEASONINGS
    'salt': {'tsp': {'cal': 0, 'fat': 0, 'carb': 0, 'protein': 0, 'sodium': 2325, 'fiber': 0, 'sugar': 0}},
    'pepper': {'tsp': {'cal': 6, 'fat': 0.1, 'carb': 1.5, 'protein': 0.2, 'sodium': 1, 'fiber': 0.6, 'sugar': 0}},
    'ketchup': {'tbsp': {'cal': 19, 'fat': 0, 'carb': 5, 'protein': 0.2, 'sodium': 154, 'fiber': 0, 'sugar': 4}},
    'mustard': {'tsp': {'cal': 3, 'fat': 0.2, 'carb': 0.3, 'protein': 0.2, 'sodium': 57, 'fiber': 0, 'sugar': 0}},
    'soy sauce': {'tbsp': {'cal': 9, 'fat': 0, 'carb': 0.8, 'protein': 1.3, 'sodium': 879, 'fiber': 0, 'sugar': 0}},
    'worcestershire sauce': {'tbsp': {'cal': 13, 'fat': 0, 'carb': 3, 'protein': 0, 'sodium': 167, 'fiber': 0, 'sugar': 2}},
    'vinegar': {'tbsp': {'cal': 3, 'fat': 0, 'carb': 0, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0}},
    'hot sauce': {'tsp': {'cal': 1, 'fat': 0, 'carb': 0, 'protein': 0, 'sodium': 124, 'fiber': 0, 'sugar': 0}},
    'italian seasoning': {'tsp': {'cal': 3, 'fat': 0.1, 'carb': 0.6, 'protein': 0.1, 'sodium': 1, 'fiber': 0.3, 'sugar': 0}},
    'cinnamon': {'tsp': {'cal': 6, 'fat': 0, 'carb': 2, 'protein': 0.1, 'sodium': 0, 'fiber': 1, 'sugar': 0}},

    # BEVERAGES & ALCOHOL
    'wine': {'cup': {'cal': 200, 'fat': 0, 'carb': 5, 'protein': 0.2, 'sodium': 12, 'fiber': 0, 'sugar': 2}},
    'beer': {'cup': {'cal': 100, 'fat': 0, 'carb': 9, 'protein': 1, 'sodium': 10, 'fiber': 0, 'sugar': 0}},
    'coffee': {'cup': {'cal': 2, 'fat': 0, 'carb': 0, 'protein': 0.3, 'sodium': 5, 'fiber': 0, 'sugar': 0}},
    'apple cider': {'cup': {'cal': 120, 'fat': 0, 'carb': 28, 'protein': 0.3, 'sodium': 10, 'fiber': 0.5, 'sugar': 24}},
    'galliano liqueur': {'oz': {'cal': 103, 'fat': 0, 'carb': 11, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 11}},
    'sake': {'oz': {'cal': 39, 'fat': 0, 'carb': 1.5, 'protein': 0.1, 'sodium': 1, 'fiber': 0, 'sugar': 0}},
    'sherry': {'oz': {'cal': 45, 'fat': 0, 'carb': 2, 'protein': 0.1, 'sodium': 3, 'fiber': 0, 'sugar': 1}},
    'soda water': {'cup': {'cal': 0, 'fat': 0, 'carb': 0, 'protein': 0, 'sodium': 75, 'fiber': 0, 'sugar': 0}},

    # WATER (0 calories but included for completeness)
    'water': {'cup': {'cal': 0, 'fat': 0, 'carb': 0, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0}},
    'hot water': {'cup': {'cal': 0, 'fat': 0, 'carb': 0, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0}},
    'warm water': {'cup': {'cal': 0, 'fat': 0, 'carb': 0, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0}},

    # ADDITIONAL DAIRY
    'whipping cream': {'cup': {'cal': 821, 'fat': 88, 'carb': 7, 'protein': 5, 'sodium': 89, 'fiber': 0, 'sugar': 7}},
    'half-and-half': {'cup': {'cal': 315, 'fat': 28, 'carb': 10, 'protein': 7, 'sodium': 98, 'fiber': 0, 'sugar': 10},
                      'tbsp': {'cal': 20, 'fat': 1.7, 'carb': 0.6, 'protein': 0.4, 'sodium': 6, 'fiber': 0, 'sugar': 0.6}},
    'whipped cream': {'cup': {'cal': 400, 'fat': 43, 'carb': 3, 'protein': 2, 'sodium': 44, 'fiber': 0, 'sugar': 3}},

    # HERBS & SPICES (minimal calories, but tracked for completeness)
    'paprika': {'tsp': {'cal': 6, 'fat': 0.3, 'carb': 1.2, 'protein': 0.3, 'sodium': 2, 'fiber': 0.7, 'sugar': 0.3}},
    'cayenne': {'tsp': {'cal': 6, 'fat': 0.3, 'carb': 1, 'protein': 0.2, 'sodium': 1, 'fiber': 0.5, 'sugar': 0.2}},
    'basil': {'tsp': {'cal': 1, 'fat': 0, 'carb': 0.1, 'protein': 0.1, 'sodium': 0, 'fiber': 0.1, 'sugar': 0}},
    'dried basil': {'tsp': {'cal': 1, 'fat': 0, 'carb': 0.1, 'protein': 0.1, 'sodium': 0, 'fiber': 0.1, 'sugar': 0}},
    'dried basil leaves': {'tsp': {'cal': 1, 'fat': 0, 'carb': 0.1, 'protein': 0.1, 'sodium': 0, 'fiber': 0.1, 'sugar': 0}},
    'fresh basil': {'tbsp': {'cal': 1, 'fat': 0, 'carb': 0.1, 'protein': 0.1, 'sodium': 0, 'fiber': 0, 'sugar': 0}},
    'fresh basil leaves': {'tbsp': {'cal': 1, 'fat': 0, 'carb': 0.1, 'protein': 0.1, 'sodium': 0, 'fiber': 0, 'sugar': 0}},
    'parsley': {'tbsp': {'cal': 1, 'fat': 0, 'carb': 0.2, 'protein': 0.1, 'sodium': 2, 'fiber': 0.1, 'sugar': 0}},
    'chopped parsley': {'tbsp': {'cal': 1, 'fat': 0, 'carb': 0.2, 'protein': 0.1, 'sodium': 2, 'fiber': 0.1, 'sugar': 0}},
    'minced parsley': {'tbsp': {'cal': 1, 'fat': 0, 'carb': 0.2, 'protein': 0.1, 'sodium': 2, 'fiber': 0.1, 'sugar': 0}},
    'fresh parsley': {'tbsp': {'cal': 1, 'fat': 0, 'carb': 0.2, 'protein': 0.1, 'sodium': 2, 'fiber': 0.1, 'sugar': 0}},
    'cilantro': {'tbsp': {'cal': 1, 'fat': 0, 'carb': 0.1, 'protein': 0.1, 'sodium': 1, 'fiber': 0, 'sugar': 0}},
    'fresh cilantro': {'tbsp': {'cal': 1, 'fat': 0, 'carb': 0.1, 'protein': 0.1, 'sodium': 1, 'fiber': 0, 'sugar': 0}},
    'fresh cilantro leaves': {'tbsp': {'cal': 1, 'fat': 0, 'carb': 0.1, 'protein': 0.1, 'sodium': 1, 'fiber': 0, 'sugar': 0}},
    'rosemary': {'tsp': {'cal': 2, 'fat': 0.1, 'carb': 0.4, 'protein': 0, 'sodium': 1, 'fiber': 0.2, 'sugar': 0}},
    'dried rosemary': {'tsp': {'cal': 2, 'fat': 0.1, 'carb': 0.4, 'protein': 0, 'sodium': 1, 'fiber': 0.2, 'sugar': 0}},
    'thyme': {'tsp': {'cal': 3, 'fat': 0.1, 'carb': 0.6, 'protein': 0.1, 'sodium': 1, 'fiber': 0.3, 'sugar': 0}},
    'dried thyme': {'tsp': {'cal': 3, 'fat': 0.1, 'carb': 0.6, 'protein': 0.1, 'sodium': 1, 'fiber': 0.3, 'sugar': 0}},
    'sage': {'tsp': {'cal': 2, 'fat': 0.1, 'carb': 0.4, 'protein': 0.1, 'sodium': 0, 'fiber': 0.3, 'sugar': 0}},
    'dried sage': {'tsp': {'cal': 2, 'fat': 0.1, 'carb': 0.4, 'protein': 0.1, 'sodium': 0, 'fiber': 0.3, 'sugar': 0}},
    'dried sage leaves': {'tsp': {'cal': 2, 'fat': 0.1, 'carb': 0.4, 'protein': 0.1, 'sodium': 0, 'fiber': 0.3, 'sugar': 0}},
    'tarragon': {'tsp': {'cal': 2, 'fat': 0, 'carb': 0.4, 'protein': 0.2, 'sodium': 1, 'fiber': 0, 'sugar': 0}},
    'dried tarragon': {'tsp': {'cal': 2, 'fat': 0, 'carb': 0.4, 'protein': 0.2, 'sodium': 1, 'fiber': 0, 'sugar': 0}},
    'dried tarragon leaves': {'tsp': {'cal': 2, 'fat': 0, 'carb': 0.4, 'protein': 0.2, 'sodium': 1, 'fiber': 0, 'sugar': 0}},
    'oregano': {'tsp': {'cal': 3, 'fat': 0.1, 'carb': 0.7, 'protein': 0.1, 'sodium': 0, 'fiber': 0.4, 'sugar': 0}},
    'dried oregano': {'tsp': {'cal': 3, 'fat': 0.1, 'carb': 0.7, 'protein': 0.1, 'sodium': 0, 'fiber': 0.4, 'sugar': 0}},
    'dried oregano leaves': {'tsp': {'cal': 3, 'fat': 0.1, 'carb': 0.7, 'protein': 0.1, 'sodium': 0, 'fiber': 0.4, 'sugar': 0}},
    'chives': {'tbsp': {'cal': 1, 'fat': 0, 'carb': 0.1, 'protein': 0.1, 'sodium': 0, 'fiber': 0, 'sugar': 0}},
    'minced chives': {'tbsp': {'cal': 1, 'fat': 0, 'carb': 0.1, 'protein': 0.1, 'sodium': 0, 'fiber': 0, 'sugar': 0}},
    'bay leaf': {'each': {'cal': 2, 'fat': 0.1, 'carb': 0.5, 'protein': 0, 'sodium': 0, 'fiber': 0.2, 'sugar': 0}},
    'nutmeg': {'tsp': {'cal': 12, 'fat': 0.8, 'carb': 1.1, 'protein': 0.1, 'sodium': 0, 'fiber': 0.5, 'sugar': 0}},
    'ground nutmeg': {'tsp': {'cal': 12, 'fat': 0.8, 'carb': 1.1, 'protein': 0.1, 'sodium': 0, 'fiber': 0.5, 'sugar': 0}},
    'cumin': {'tsp': {'cal': 8, 'fat': 0.5, 'carb': 0.9, 'protein': 0.4, 'sodium': 4, 'fiber': 0.2, 'sugar': 0}},
    'ground cumin': {'tsp': {'cal': 8, 'fat': 0.5, 'carb': 0.9, 'protein': 0.4, 'sodium': 4, 'fiber': 0.2, 'sugar': 0}},
    'cardamom': {'tsp': {'cal': 6, 'fat': 0.1, 'carb': 1.4, 'protein': 0.2, 'sodium': 0, 'fiber': 0.6, 'sugar': 0}},
    'ground cardamom': {'tsp': {'cal': 6, 'fat': 0.1, 'carb': 1.4, 'protein': 0.2, 'sodium': 0, 'fiber': 0.6, 'sugar': 0}},
    'fennel seeds': {'tsp': {'cal': 7, 'fat': 0.3, 'carb': 1, 'protein': 0.3, 'sodium': 2, 'fiber': 0.8, 'sugar': 0}},
    'whole fennel seeds': {'tsp': {'cal': 7, 'fat': 0.3, 'carb': 1, 'protein': 0.3, 'sodium': 2, 'fiber': 0.8, 'sugar': 0}},
    'crushed fennel': {'tsp': {'cal': 7, 'fat': 0.3, 'carb': 1, 'protein': 0.3, 'sodium': 2, 'fiber': 0.8, 'sugar': 0}},

    # EXTRACTS
    'almond extract': {'tsp': {'cal': 10, 'fat': 0, 'carb': 0.3, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0.3}},
    'maple extract': {'tsp': {'cal': 10, 'fat': 0, 'carb': 0.3, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0.3}},
    'maple-flavored extract': {'tsp': {'cal': 10, 'fat': 0, 'carb': 0.3, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0.3}},
    'liquid smoke': {'tsp': {'cal': 0, 'fat': 0, 'carb': 0, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0}},
    'liquid smoke seasoning': {'tsp': {'cal': 0, 'fat': 0, 'carb': 0, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0}},

    # SWEETS & CANDIES
    'marshmallows': {'cup': {'cal': 159, 'fat': 0.1, 'carb': 41, 'protein': 1.4, 'sodium': 22, 'fiber': 0, 'sugar': 29}},
    'miniature marshmallows': {'cup': {'cal': 159, 'fat': 0.1, 'carb': 41, 'protein': 1.4, 'sodium': 22, 'fiber': 0, 'sugar': 29}},
    'maraschino cherries': {'each': {'cal': 8, 'fat': 0, 'carb': 2, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 2}},
    'bing cherries': {'cup': {'cal': 87, 'fat': 0.3, 'carb': 22, 'protein': 1.5, 'sodium': 0, 'fiber': 3, 'sugar': 18}},
    'maple candy': {'oz': {'cal': 100, 'fat': 0, 'carb': 25, 'protein': 0, 'sodium': 3, 'fiber': 0, 'sugar': 24}},

    # ADDITIONAL NUTS & SEEDS
    'nuts': {'cup': {'cal': 800, 'fat': 72, 'carb': 24, 'protein': 20, 'sodium': 5, 'fiber': 8, 'sugar': 4}},
    'chopped nuts': {'cup': {'cal': 800, 'fat': 72, 'carb': 24, 'protein': 20, 'sodium': 5, 'fiber': 8, 'sugar': 4}},
    'sesame seeds': {'tbsp': {'cal': 52, 'fat': 4.5, 'carb': 2, 'protein': 1.6, 'sodium': 1, 'fiber': 1, 'sugar': 0}},
    'sunflower seeds': {'cup': {'cal': 818, 'fat': 72, 'carb': 28, 'protein': 29, 'sodium': 4, 'fiber': 12, 'sugar': 3}},

    # JAMS, JELLIES & PRESERVES
    'jam': {'tbsp': {'cal': 56, 'fat': 0, 'carb': 14, 'protein': 0.1, 'sodium': 6, 'fiber': 0.2, 'sugar': 12}},
    'apricot jam': {'tbsp': {'cal': 56, 'fat': 0, 'carb': 14, 'protein': 0.1, 'sodium': 6, 'fiber': 0.2, 'sugar': 12}},
    'raspberry jam': {'tbsp': {'cal': 56, 'fat': 0, 'carb': 14, 'protein': 0.1, 'sodium': 6, 'fiber': 0.2, 'sugar': 12}},
    'jelly': {'tbsp': {'cal': 52, 'fat': 0, 'carb': 14, 'protein': 0, 'sodium': 6, 'fiber': 0, 'sugar': 10}},
    'red currant jelly': {'tbsp': {'cal': 52, 'fat': 0, 'carb': 14, 'protein': 0, 'sodium': 6, 'fiber': 0, 'sugar': 10}},

    # ADDITIONAL VEGETABLES
    'cucumber': {'medium': {'cal': 45, 'fat': 0.3, 'carb': 11, 'protein': 2, 'sodium': 6, 'fiber': 2, 'sugar': 5}},
    'small cucumber': {'each': {'cal': 20, 'fat': 0.1, 'carb': 5, 'protein': 1, 'sodium': 3, 'fiber': 1, 'sugar': 2}},
    'radishes': {'cup': {'cal': 19, 'fat': 0.1, 'carb': 4, 'protein': 0.8, 'sodium': 45, 'fiber': 2, 'sugar': 2}},
    'olives': {'cup': {'cal': 155, 'fat': 14, 'carb': 8, 'protein': 1, 'sodium': 1560, 'fiber': 3, 'sugar': 0}},
    'black olives': {'cup': {'cal': 155, 'fat': 14, 'carb': 8, 'protein': 1, 'sodium': 1560, 'fiber': 3, 'sugar': 0}},
    'sliced black olives': {'cup': {'cal': 155, 'fat': 14, 'carb': 8, 'protein': 1, 'sodium': 1560, 'fiber': 3, 'sugar': 0}},

    # ADDITIONAL FRUITS
    'raspberries': {'cup': {'cal': 64, 'fat': 0.8, 'carb': 15, 'protein': 1.5, 'sodium': 1, 'fiber': 8, 'sugar': 5}},
    'frozen raspberries': {'cup': {'cal': 64, 'fat': 0.8, 'carb': 15, 'protein': 1.5, 'sodium': 1, 'fiber': 8, 'sugar': 5}},
    'mandarin oranges': {'cup': {'cal': 72, 'fat': 0.2, 'carb': 18, 'protein': 1, 'sodium': 10, 'fiber': 2, 'sugar': 14}},
    'mandarin orange slices': {'cup': {'cal': 72, 'fat': 0.2, 'carb': 18, 'protein': 1, 'sodium': 10, 'fiber': 2, 'sugar': 14}},
    'orange rind': {'tbsp': {'cal': 6, 'fat': 0, 'carb': 2, 'protein': 0.1, 'sodium': 0, 'fiber': 0.6, 'sugar': 1}},
    'grated orange rind': {'tbsp': {'cal': 6, 'fat': 0, 'carb': 2, 'protein': 0.1, 'sodium': 0, 'fiber': 0.6, 'sugar': 1}},
    'lemon rind': {'tbsp': {'cal': 3, 'fat': 0, 'carb': 1, 'protein': 0.1, 'sodium': 0, 'fiber': 0.4, 'sugar': 0.4}},
    'grated lemon rind': {'tbsp': {'cal': 3, 'fat': 0, 'carb': 1, 'protein': 0.1, 'sodium': 0, 'fiber': 0.4, 'sugar': 0.4}},
    'lemonade concentrate': {'can': {'cal': 400, 'fat': 0, 'carb': 108, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 100}},
    'frozen lemonade concentrate': {'can': {'cal': 400, 'fat': 0, 'carb': 108, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 100}},

    # ADDITIONAL PROTEINS
    'sirloin': {'lb': {'cal': 880, 'fat': 48, 'carb': 0, 'protein': 104, 'sodium': 280, 'fiber': 0, 'sugar': 0}},
    'boneless sirloin': {'lb': {'cal': 880, 'fat': 48, 'carb': 0, 'protein': 104, 'sodium': 280, 'fiber': 0, 'sugar': 0}},
    'round steak': {'lb': {'cal': 720, 'fat': 24, 'carb': 0, 'protein': 120, 'sodium': 240, 'fiber': 0, 'sugar': 0}},
    'salami': {'oz': {'cal': 119, 'fat': 10, 'carb': 0.5, 'protein': 6, 'sodium': 529, 'fiber': 0, 'sugar': 0}},

    # BREADS & BAKED GOODS
    'english muffin': {'each': {'cal': 134, 'fat': 1, 'carb': 26, 'protein': 4, 'sodium': 264, 'fiber': 2, 'sugar': 2}},
    'angel food cake': {'slice': {'cal': 72, 'fat': 0.2, 'carb': 16, 'protein': 2, 'sodium': 210, 'fiber': 0, 'sugar': 12}},
    'crepe': {'each': {'cal': 90, 'fat': 4, 'carb': 11, 'protein': 3, 'sodium': 100, 'fiber': 0, 'sugar': 2}},
    'crepes': {'each': {'cal': 90, 'fat': 4, 'carb': 11, 'protein': 3, 'sodium': 100, 'fiber': 0, 'sugar': 2}},
    'croutons': {'cup': {'cal': 122, 'fat': 2, 'carb': 22, 'protein': 4, 'sodium': 209, 'fiber': 2, 'sugar': 1}},
    'ritz crackers': {'cup': {'cal': 310, 'fat': 16, 'carb': 38, 'protein': 4, 'sodium': 480, 'fiber': 1, 'sugar': 6}},

    # CONDIMENTS
    'catsup': {'tbsp': {'cal': 19, 'fat': 0, 'carb': 5, 'protein': 0.2, 'sodium': 154, 'fiber': 0, 'sugar': 4}},
    'horseradish': {'tbsp': {'cal': 7, 'fat': 0.1, 'carb': 2, 'protein': 0.2, 'sodium': 47, 'fiber': 0.5, 'sugar': 1}},

    # BOUILLON
    'bouillon cube': {'each': {'cal': 5, 'fat': 0.1, 'carb': 0.6, 'protein': 0.5, 'sodium': 900, 'fiber': 0, 'sugar': 0}},
    'beef bouillon cube': {'each': {'cal': 5, 'fat': 0.1, 'carb': 0.6, 'protein': 0.5, 'sodium': 900, 'fiber': 0, 'sugar': 0}},
    'chicken bouillon cube': {'each': {'cal': 5, 'fat': 0.1, 'carb': 0.6, 'protein': 0.5, 'sodium': 900, 'fiber': 0, 'sugar': 0}},

    # FOOD COLORING (essentially 0 nutrition)
    'food coloring': {'drop': {'cal': 0, 'fat': 0, 'carb': 0, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0}},
    'red food coloring': {'drop': {'cal': 0, 'fat': 0, 'carb': 0, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0}},
    'green food coloring': {'drop': {'cal': 0, 'fat': 0, 'carb': 0, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0}},

    # ADDITIONAL SPECIALTY ITEMS
    'cream of tartar': {'tsp': {'cal': 2, 'fat': 0, 'carb': 0.5, 'protein': 0, 'sodium': 2, 'fiber': 0, 'sugar': 0}},
    'frozen bread dough': {'loaf': {'cal': 1200, 'fat': 20, 'carb': 220, 'protein': 36, 'sodium': 2200, 'fiber': 8, 'sugar': 12}},
    'bread dough': {'loaf': {'cal': 1200, 'fat': 20, 'carb': 220, 'protein': 36, 'sodium': 2200, 'fiber': 8, 'sugar': 12}},
    'cognac': {'tbsp': {'cal': 33, 'fat': 0, 'carb': 0, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0},
               'oz': {'cal': 66, 'fat': 0, 'carb': 0, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0}},
    'barley': {'cup': {'cal': 651, 'fat': 2.3, 'carb': 135, 'protein': 23, 'sodium': 22, 'fiber': 32, 'sugar': 1}},
    'allspice': {'tsp': {'cal': 5, 'fat': 0.2, 'carb': 1.4, 'protein': 0.1, 'sodium': 1, 'fiber': 0.4, 'sugar': 0}},
    'whole allspice': {'tsp': {'cal': 5, 'fat': 0.2, 'carb': 1.4, 'protein': 0.1, 'sodium': 1, 'fiber': 0.4, 'sugar': 0}},
    'ground allspice': {'tsp': {'cal': 5, 'fat': 0.2, 'carb': 1.4, 'protein': 0.1, 'sodium': 1, 'fiber': 0.4, 'sugar': 0}},
    'prunes': {'cup': {'cal': 418, 'fat': 0.7, 'carb': 111, 'protein': 4, 'sodium': 4, 'fiber': 12, 'sugar': 66}},
    'cooked prunes': {'cup': {'cal': 265, 'fat': 0.5, 'carb': 70, 'protein': 2, 'sodium': 3, 'fiber': 8, 'sugar': 42}},
    'chili sauce': {'tbsp': {'cal': 20, 'fat': 0.1, 'carb': 5, 'protein': 0.3, 'sodium': 200, 'fiber': 0.2, 'sugar': 3},
                    'cup': {'cal': 320, 'fat': 1.6, 'carb': 80, 'protein': 4.8, 'sodium': 3200, 'fiber': 3.2, 'sugar': 48}},
    'pot roast': {'lb': {'cal': 880, 'fat': 52, 'carb': 0, 'protein': 100, 'sodium': 280, 'fiber': 0, 'sugar': 0}},
    'beef roast': {'lb': {'cal': 880, 'fat': 52, 'carb': 0, 'protein': 100, 'sodium': 280, 'fiber': 0, 'sugar': 0}},
    'round bone pot roast': {'lb': {'cal': 880, 'fat': 52, 'carb': 0, 'protein': 100, 'sodium': 280, 'fiber': 0, 'sugar': 0}},
    'beef round': {'lb': {'cal': 720, 'fat': 32, 'carb': 0, 'protein': 104, 'sodium': 260, 'fiber': 0, 'sugar': 0}},
    'stew meat': {'lb': {'cal': 880, 'fat': 52, 'carb': 0, 'protein': 100, 'sodium': 280, 'fiber': 0, 'sugar': 0}},
    'grated mozzarella': {'cup': {'cal': 316, 'fat': 20, 'carb': 4, 'protein': 28, 'sodium': 632, 'fiber': 0, 'sugar': 1}},
    'bread cubes': {'cup': {'cal': 130, 'fat': 2, 'carb': 24, 'protein': 4, 'sodium': 230, 'fiber': 1, 'sugar': 2}},
    'fresh bread cubes': {'cup': {'cal': 130, 'fat': 2, 'carb': 24, 'protein': 4, 'sodium': 230, 'fiber': 1, 'sugar': 2}},
    'patty shells': {'each': {'cal': 150, 'fat': 10, 'carb': 12, 'protein': 2, 'sodium': 120, 'fiber': 0, 'sugar': 0}},
    'frozen patty shells': {'each': {'cal': 150, 'fat': 10, 'carb': 12, 'protein': 2, 'sodium': 120, 'fiber': 0, 'sugar': 0}},
    'instant breakfast drink': {'packet': {'cal': 130, 'fat': 0.5, 'carb': 28, 'protein': 5, 'sodium': 220, 'fiber': 0, 'sugar': 24}},
    'orange drink': {'cup': {'cal': 120, 'fat': 0, 'carb': 30, 'protein': 0, 'sodium': 10, 'fiber': 0, 'sugar': 28}},
    'fruit': {'cup': {'cal': 80, 'fat': 0.3, 'carb': 20, 'protein': 1, 'sodium': 2, 'fiber': 3, 'sugar': 14}},
    'mixed fruit': {'cup': {'cal': 80, 'fat': 0.3, 'carb': 20, 'protein': 1, 'sodium': 2, 'fiber': 3, 'sugar': 14}},
    'assorted fruit': {'cup': {'cal': 80, 'fat': 0.3, 'carb': 20, 'protein': 1, 'sodium': 2, 'fiber': 3, 'sugar': 14}},

    # MORE SPECIALTY ITEMS
    'cloves': {'tsp': {'cal': 7, 'fat': 0.4, 'carb': 1.3, 'protein': 0.1, 'sodium': 5, 'fiber': 0.7, 'sugar': 0.5}},
    'ground cloves': {'tsp': {'cal': 7, 'fat': 0.4, 'carb': 1.3, 'protein': 0.1, 'sodium': 5, 'fiber': 0.7, 'sugar': 0.5}},
    'whole cloves': {'tsp': {'cal': 7, 'fat': 0.4, 'carb': 1.3, 'protein': 0.1, 'sodium': 5, 'fiber': 0.7, 'sugar': 0.5}},
    'pectin': {'packet': {'cal': 10, 'fat': 0, 'carb': 3, 'protein': 0, 'sodium': 5, 'fiber': 1, 'sugar': 0}},
    'liquid pectin': {'pouch': {'cal': 10, 'fat': 0, 'carb': 3, 'protein': 0, 'sodium': 5, 'fiber': 1, 'sugar': 0}},
    'paraffin': {'each': {'cal': 0, 'fat': 0, 'carb': 0, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0}},  # Not consumed
    'melted paraffin': {'each': {'cal': 0, 'fat': 0, 'carb': 0, 'protein': 0, 'sodium': 0, 'fiber': 0, 'sugar': 0}},
    'pickles': {'cup': {'cal': 17, 'fat': 0.2, 'carb': 3.7, 'protein': 0.4, 'sodium': 1208, 'fiber': 1, 'sugar': 2}},
    'dill pickles': {'each': {'cal': 12, 'fat': 0.1, 'carb': 2.7, 'protein': 0.3, 'sodium': 870, 'fiber': 0.8, 'sugar': 1}},
    'pickle': {'each': {'cal': 12, 'fat': 0.1, 'carb': 2.7, 'protein': 0.3, 'sodium': 870, 'fiber': 0.8, 'sugar': 1}},
    'coleslaw': {'cup': {'cal': 150, 'fat': 8, 'carb': 18, 'protein': 2, 'sodium': 260, 'fiber': 2, 'sugar': 10}},
    'pound cake': {'slice': {'cal': 220, 'fat': 10, 'carb': 28, 'protein': 3, 'sodium': 180, 'fiber': 0.5, 'sugar': 18}},
    'frozen pound cake': {'each': {'cal': 2640, 'fat': 120, 'carb': 336, 'protein': 36, 'sodium': 2160, 'fiber': 6, 'sugar': 216}},
    'frozen pound cakes': {'each': {'cal': 2640, 'fat': 120, 'carb': 336, 'protein': 36, 'sodium': 2160, 'fiber': 6, 'sugar': 216}},
    'cake decors': {'tbsp': {'cal': 70, 'fat': 0, 'carb': 18, 'protein': 0, 'sodium': 5, 'fiber': 0, 'sugar': 14}},
    'm&ms': {'cup': {'cal': 1024, 'fat': 44, 'carb': 148, 'protein': 10, 'sodium': 88, 'fiber': 4, 'sugar': 128}},
    'peanut m&ms': {'cup': {'cal': 1024, 'fat': 48, 'carb': 132, 'protein': 16, 'sodium': 80, 'fiber': 6, 'sugar': 108}},
}

# Unit conversions to standard measures
UNIT_CONVERSIONS = {
    'tbsp': {'tsp': 3, 'cup': 0.0625},
    'tsp': {'tbsp': 0.333, 'cup': 0.0208},
    'cup': {'tbsp': 16, 'tsp': 48, 'oz': 8, 'ml': 240},
    'oz': {'cup': 0.125, 'lb': 0.0625, 'g': 28.35},
    'lb': {'oz': 16, 'g': 454, 'cup': 2},
    'quart': {'cup': 4, 'pint': 2},
    'pint': {'cup': 2, 'quart': 0.5},
    'gallon': {'quart': 4, 'cup': 16},
}


def parse_quantity(qty_str):
    """Parse quantity string to float, handling fractions."""
    if not qty_str:
        return 1.0

    qty_str = str(qty_str).strip()

    # Handle ranges (e.g., "1-2") - take average
    if '-' in qty_str and not qty_str.startswith('-'):
        parts = qty_str.split('-')
        try:
            return (parse_quantity(parts[0]) + parse_quantity(parts[1])) / 2
        except:
            pass

    # Handle mixed numbers (e.g., "1-1/2" or "1 1/2")
    qty_str = qty_str.replace('-', ' ')
    parts = qty_str.split()

    total = 0.0
    for part in parts:
        try:
            if '/' in part:
                total += float(Fraction(part))
            else:
                total += float(part)
        except:
            pass

    return total if total > 0 else 1.0


def parse_serving_yield(yield_str, category=None, title=None):
    """Parse serving yield to get number of servings."""
    title_lower = (title or '').lower()
    category = category or ''

    # Handle missing yield based on category/title
    if not yield_str:
        # Dessert defaults
        if category == 'desserts':
            if any(word in title_lower for word in ['cake', 'cheesecake', 'pie', 'tart']):
                return 12  # Cakes/pies serve ~12
            if any(word in title_lower for word in ['cookie', 'brownie', 'bar', 'square']):
                return 24  # Cookie recipes make ~24 cookies (2 per serving = 12 servings)
            if any(word in title_lower for word in ['fudge', 'candy']):
                return 24  # Candy recipes
            return 8  # Generic dessert
        if category == 'mains':
            if 'casserole' in title_lower:
                return 6
            return 4
        if category == 'sides':
            return 6
        if category == 'breads':
            if 'loaf' in title_lower or 'bread' in title_lower:
                return 12  # Bread loaves
            return 8
        if category == 'appetizers':
            return 8
        if category == 'snacks':
            return 8
        return 4  # Default

    yield_str = str(yield_str).lower()

    # Extract numbers
    numbers = re.findall(r'(\d+(?:\.\d+)?)', yield_str)

    if not numbers:
        return 4

    # Check for cookies/pieces - assume 2 cookies per serving
    if any(word in yield_str for word in ['cookie', 'piece', 'bar', 'square', 'muffin', 'roll', 'croissant']):
        total_pieces = float(numbers[-1]) if 'dozen' not in yield_str else float(numbers[0]) * 12
        return max(1, int(total_pieces / 2))  # 2 pieces per serving

    # Check for "dozen"
    if 'dozen' in yield_str:
        return int(float(numbers[0]) * 12 / 2)  # 2 per serving

    # Handle ranges
    if len(numbers) >= 2 and '-' in yield_str:
        return int((float(numbers[0]) + float(numbers[1])) / 2)

    # Check for cups/pounds (e.g., "2 cups", "3 lbs")
    if any(word in yield_str for word in ['cup', 'pound', 'lb', 'quart']):
        return 8  # Assume 8 servings for bulk recipes

    # For loaves, assume 12 slices
    if 'loaf' in yield_str or 'loaves' in yield_str:
        return int(float(numbers[0])) * 12

    # Default to first number found
    return int(float(numbers[0]))


def find_ingredient_match(item_name):
    """Find best matching ingredient in database."""
    item_lower = item_name.lower()

    # Direct match
    if item_lower in NUTRITION_DB:
        return item_lower

    # Check for partial matches
    for db_item in NUTRITION_DB:
        if db_item in item_lower or item_lower in db_item:
            return db_item

    # Check for common variations
    variations = {
        'butter or margarine': 'butter',
        'vegetable oil': 'oil',
        'cooking oil': 'oil',
        'canola oil': 'oil',
        'large eggs': 'eggs',
        'large egg': 'egg',
        'white sugar': 'sugar',
        'ground beef': 'ground beef',
        'lean ground beef': 'extra-lean ground beef',
        'chicken breast halves': 'chicken breast',
        'boneless chicken': 'chicken breast',
        'frozen mixed vegetables': 'peas',  # Approximate
        'mixed vegetables': 'peas',
        'green onion': 'onion',
        'yellow onion': 'onion',
        'red onion': 'onion',
    }

    for var, match in variations.items():
        if var in item_lower:
            return match

    return None


def estimate_nutrition(recipe):
    """Estimate nutrition for a recipe."""
    ingredients = recipe.get('ingredients', [])
    yield_str = recipe.get('servings_yield', '')
    category = recipe.get('category', '')
    title = recipe.get('title', '')

    servings = parse_serving_yield(yield_str, category, title)

    totals = {
        'calories': 0,
        'fat_g': 0,
        'carbs_g': 0,
        'protein_g': 0,
        'sodium_mg': 0,
        'fiber_g': 0,
        'sugar_g': 0
    }

    missing_ingredients = []
    assumptions = []

    for ing in ingredients:
        item = ing.get('item', '')
        qty = parse_quantity(ing.get('quantity', '1'))
        unit = ing.get('unit', '').lower().strip()

        # Find matching ingredient
        match = find_ingredient_match(item)

        if not match or match not in NUTRITION_DB:
            missing_ingredients.append(item)
            continue

        db_entry = NUTRITION_DB[match]

        # Find unit match or convert
        if unit in db_entry:
            nutrition = db_entry[unit]
        elif unit in ['', 'each', 'medium', 'large', 'small']:
            # Try common defaults
            for default_unit in ['each', 'medium', 'cup', 'oz']:
                if default_unit in db_entry:
                    nutrition = db_entry[default_unit]
                    break
            else:
                nutrition = list(db_entry.values())[0]
        else:
            # Try to find any matching unit
            nutrition = list(db_entry.values())[0]
            assumptions.append(f"{item}: used default unit")

        # Add to totals
        totals['calories'] += nutrition.get('cal', 0) * qty
        totals['fat_g'] += nutrition.get('fat', 0) * qty
        totals['carbs_g'] += nutrition.get('carb', 0) * qty
        totals['protein_g'] += nutrition.get('protein', 0) * qty
        totals['sodium_mg'] += nutrition.get('sodium', 0) * qty
        totals['fiber_g'] += nutrition.get('fiber', 0) * qty
        totals['sugar_g'] += nutrition.get('sugar', 0) * qty

    # Calculate per serving
    per_serving = {
        'calories': round(totals['calories'] / servings),
        'fat_g': round(totals['fat_g'] / servings, 1),
        'carbs_g': round(totals['carbs_g'] / servings, 1),
        'protein_g': round(totals['protein_g'] / servings, 1),
        'sodium_mg': round(totals['sodium_mg'] / servings),
        'fiber_g': round(totals['fiber_g'] / servings, 1),
        'sugar_g': round(totals['sugar_g'] / servings, 1)
    }

    # Determine status
    if len(missing_ingredients) == 0:
        status = 'complete'
    elif len(missing_ingredients) <= len(ingredients) * 0.3:
        status = 'partial'
    else:
        status = 'insufficient_data'

    return {
        'status': status,
        'servings_used': servings,
        'per_serving': per_serving,
        'missing_inputs': missing_ingredients if missing_ingredients else [],
        'assumptions': assumptions if assumptions else []
    }


def main():
    dry_run = '--dry-run' in sys.argv
    force = '--force' in sys.argv
    target_id = None

    for i, arg in enumerate(sys.argv):
        if arg == '--recipe-id' and i + 1 < len(sys.argv):
            target_id = sys.argv[i + 1]

    # Load recipes
    recipes_path = Path('granny/recipes_master.json')
    with open(recipes_path, 'r') as f:
        data = json.load(f)

    recipes = data['recipes']
    updated_count = 0

    for recipe in recipes:
        # Skip if already has nutrition (unless targeting specific recipe or forcing)
        if recipe.get('nutrition') and not target_id and not force:
            continue

        # Skip if not matching target
        if target_id and recipe['id'] != target_id:
            continue

        nutrition = estimate_nutrition(recipe)

        if dry_run:
            print(f"\n=== {recipe['title']} ===")
            print(f"Servings: {nutrition['servings_used']}")
            print(f"Status: {nutrition['status']}")
            print(f"Per serving: {nutrition['per_serving']['calories']} cal, "
                  f"{nutrition['per_serving']['fat_g']}g fat, "
                  f"{nutrition['per_serving']['carbs_g']}g carbs, "
                  f"{nutrition['per_serving']['protein_g']}g protein")
            if nutrition['missing_inputs']:
                print(f"Missing: {', '.join(nutrition['missing_inputs'][:5])}")
        else:
            recipe['nutrition'] = nutrition
            updated_count += 1

    if not dry_run:
        with open(recipes_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Updated {updated_count} recipes with nutrition estimates")
        print("Run 'python scripts/shard_recipes.py' to regenerate shards")
    else:
        print(f"\n[DRY RUN] Would update {len([r for r in recipes if not r.get('nutrition')])} recipes")


if __name__ == '__main__':
    main()
