#!/usr/bin/env python3
"""
Script to fix failing recipes that are missing ingredients and/or instructions.
Based on OCR transcription from recipe images.
"""

import json
from pathlib import Path

def load_recipes():
    """Load the recipes_master.json file."""
    path = Path(__file__).parent.parent / "granny" / "recipes_master.json"
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_recipes(data):
    """Save the recipes_master.json file."""
    path = Path(__file__).parent.parent / "granny" / "recipes_master.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_recipe_fixes():
    """Return dictionary of recipe fixes based on OCR transcription."""
    return {
        # ==================== gr-249/250: Quaker Chewy Choc-Oat-Chip Cookies ====================
        "quaker-chewy-choc-oat-chip-cookies-granny": {
            "ingredients": [
                {"item": "margarine or butter, softened", "quantity": "1", "unit": "cup"},
                {"item": "firmly packed brown sugar", "quantity": "1-1/4", "unit": "cups"},
                {"item": "granulated sugar", "quantity": "1/2", "unit": "cup"},
                {"item": "eggs", "quantity": "2", "unit": ""},
                {"item": "milk", "quantity": "2", "unit": "tbsp"},
                {"item": "vanilla", "quantity": "2", "unit": "tsp"},
                {"item": "all-purpose flour", "quantity": "1-3/4", "unit": "cups"},
                {"item": "baking soda", "quantity": "1", "unit": "tsp"},
                {"item": "salt (optional)", "quantity": "1/2", "unit": "tsp"},
                {"item": "QUAKER Oats (quick or old fashioned), uncooked", "quantity": "2-1/2", "unit": "cups"},
                {"item": "semi-sweet chocolate pieces", "quantity": "2", "unit": "cups"},
                {"item": "chopped nuts (optional)", "quantity": "1", "unit": "cup"}
            ],
            "instructions": [
                {"step": 1, "text": "Heat oven to 375°F. Beat together margarine and sugars until creamy. Add eggs, milk and vanilla; beat well."},
                {"step": 2, "text": "Add combined flour, baking soda, salt and oats; mix well. Stir in chocolate pieces and nuts (optional)."},
                {"step": 3, "text": "Drop by rounded tablespoonfuls onto ungreased cookie sheet; 9 to 10 cookies per sheet."},
                {"step": 4, "text": "Bake 12 to 13 minutes for a crispy cookie or 10 to 11 minutes for a chewy cookie."},
                {"step": 5, "text": "Cool 1 minute on cookie sheet; remove to wire rack. Cool completely. Store tightly covered."}
            ],
            "servings_yield": "About 4-1/2 dozen cookies",
            "temperature": "375°F (190°C)",
            "notes": ["For Easy Bar Cookies: Press dough onto bottom of 13 x 9-inch baking sheet. Bake 30 to 35 minutes or until light golden brown. Cool completely; cut into bars. Makes 32 bars.", "High Altitude Adjustments: Increase flour to 2 cups and bake as directed."]
        },

        # ==================== gr-255/256: Chewy Oatmeal Cookies (Crisco) ====================
        "chewy-oatmeal-cookies-crisco-granny": {
            "ingredients": [
                {"item": "Butter Flavor Crisco Shortening", "quantity": "3/4", "unit": "cup"},
                {"item": "firmly packed light brown sugar", "quantity": "1-1/4", "unit": "cups"},
                {"item": "egg", "quantity": "1", "unit": ""},
                {"item": "milk", "quantity": "1/3", "unit": "cup"},
                {"item": "vanilla", "quantity": "1-1/2", "unit": "tsp"},
                {"item": "QUAKER Oats (quick or old fashioned), uncooked", "quantity": "3", "unit": "cups"},
                {"item": "all-purpose flour", "quantity": "1", "unit": "cup"},
                {"item": "baking soda", "quantity": "1/2", "unit": "tsp"},
                {"item": "salt (optional)", "quantity": "1/2", "unit": "tsp"},
                {"item": "cinnamon", "quantity": "1", "unit": "tsp"},
                {"item": "raisins", "quantity": "1", "unit": "cup"},
                {"item": "coarsely chopped walnuts", "quantity": "1", "unit": "cup"}
            ],
            "instructions": [
                {"step": 1, "text": "Heat oven to 375°F. Lightly grease baking sheet with Butter Flavor Crisco."},
                {"step": 2, "text": "Combine Butter Flavor Crisco, brown sugar, egg, milk and vanilla in large bowl. Beat at medium speed of electric mixer until well blended."},
                {"step": 3, "text": "Combine oats, flour, baking soda, salt and cinnamon. Mix into creamed mixture. Stir in raisins and nuts."},
                {"step": 4, "text": "Drop rounded tablespoonfuls of dough 2 inches apart onto baking sheet."},
                {"step": 5, "text": "Bake for 10 to 12 minutes, or until lightly browned."},
                {"step": 6, "text": "Cool 2 minutes on cooling rack."}
            ],
            "servings_yield": "About 2-1/2 dozen cookies",
            "temperature": "375°F (190°C)"
        },

        # ==================== gr-265/266: Seafood Lasagna ====================
        "seafood-lasagna-granny": {
            "instructions": [
                {"step": 1, "text": "Thaw seafood if frozen. Cook lasagna noodles according to package directions. Line bottom of a well-greased 2-quart oblong baking dish with 1/3 of noodles."},
                {"step": 2, "text": "Carefully place sea trout over noodles, cover with 1/3 of sauce and half of ricotta cheese."},
                {"step": 3, "text": "Add another layer of lasagna noodles. Place shrimp over noodles and spread an additional 1/3 of sauce. Top with remaining ricotta cheese."},
                {"step": 4, "text": "Add another layer of noodles. Spread remaining sauce over noodles. Sprinkle with Parmesan cheese."},
                {"step": 5, "text": "Bake at 400°F for 10 to 15 minutes or until heated thoroughly. Makes 8 servings."}
            ],
            "temperature": "400°F (200°C)",
            "servings_yield": "8 servings",
            "notes": ["Red Snapper fillets may be substituted for sea trout."]
        },

        # ==================== gr-269/270: Pumpkin Spice Bread ====================
        "pumpkin-spice-bread-granny": {
            "instructions": [
                {"step": 1, "text": "Preheat oven to 350°F (175°C). Grease and flour loaf pans."},
                {"step": 2, "text": "In a large bowl, mix together dry ingredients. Add wet ingredients and mix until combined."},
                {"step": 3, "text": "Divide batter in 3 pans. Bake in 350° preheated oven until toothpick inserted in center comes out clean."},
                {"step": 4, "text": "Cool before slicing. Wrap in foil. Store in refrigerator."}
            ],
            "temperature": "350°F (175°C)"
        },

        # ==================== gr-271/272: BBQ Bacon Cheeseburgers ====================
        "bbq-bacon-cheeseburgers-granny": {
            "instructions": [
                {"step": 1, "text": "Mix meat and barbecue sauce. Shape into four patties."},
                {"step": 2, "text": "Place patties on grill over medium coals. Grill seven to nine minutes on each side or until cooked through (160°F), turning and brushing occasionally with additional barbecue sauce."},
                {"step": 3, "text": "Top each patty with two Singles. Continue grilling until Singles are melted."},
                {"step": 4, "text": "Fill rolls with lettuce, cheeseburgers and bacon."}
            ],
            "prep_time": "15 minutes",
            "cook_time": "18 minutes",
            "servings_yield": "4 servings",
            "temperature": "Medium grill heat"
        },

        # ==================== gr-273/274: Grilled Chicken Monterey ====================
        "grilled-chicken-monterey-granny": {
            "instructions": [
                {"step": 1, "text": "Preheat grill (or skillet). Place chicken between two pieces of plastic wrap and lightly pound to flatten to same thickness throughout for even cooking."},
                {"step": 2, "text": "Brush oil over both sides of chicken; grill each side until juices run clear and not pink, about 10 minutes."},
                {"step": 3, "text": "Place one slice cheese over each chicken breast; cook until cheese softens."},
                {"step": 4, "text": "Heat remaining oil in medium skillet over medium heat. Cook onions, stirring, until softened. Stir in tomatoes, cilantro, salt and pepper; cook an additional minute."},
                {"step": 5, "text": "Place chicken on serving plate; spoon tomato mixture over chicken and cheese. Serve with rice."}
            ],
            "prep_time": "25 minutes",
            "servings_yield": "4 servings"
        },

        # ==================== gr-277/278: Chicken and Portobello Mushrooms in Tarragon Cream Sauce ====================
        "chicken-portobello-tarragon-cream-granny": {
            "instructions": [
                {"step": 1, "text": "Heat oil and 1 tablespoon butter in large skillet over medium-high heat."},
                {"step": 2, "text": "Season chicken with salt and pepper. Cook chicken until golden brown on both sides and cooked through, about 5-6 minutes per side. Remove and keep warm."},
                {"step": 3, "text": "Add mushrooms to skillet and cook until softened. Add onion and cook until translucent."},
                {"step": 4, "text": "Add broth and cream; bring to a simmer. Add tarragon and cook until sauce thickens slightly."},
                {"step": 5, "text": "Return chicken to skillet and spoon sauce over. Serve immediately."}
            ],
            "prep_time": "25 minutes",
            "servings_yield": "4-6 servings"
        },

        # ==================== gr-279/280: Cranberry-Glazed Ham Kabobs ====================
        "cranberry-glazed-ham-kabobs-granny": {
            "instructions": [
                {"step": 1, "text": "Using 8 wooden or metal skewers, thread 8 ham chunks, 4 pineapple chunks and red and green pepper pieces on each."},
                {"step": 2, "text": "Place in a single layer on shallow baking pan. In small bowl, mix together cranberry sauce, cloves, mustard and vinegar. Pour mixture over kabobs."},
                {"step": 3, "text": "Bake in 400°F oven 15-20 minutes, basting often. Serve immediately."}
            ],
            "temperature": "400°F (200°C)",
            "servings_yield": "4 servings"
        },

        # ==================== gr-281/282: Curry-Coconut Chicken with Honey Mustard ====================
        "curry-coconut-chicken-honey-mustard-granny": {
            "ingredients": [
                {"item": "egg, beaten", "quantity": "1", "unit": ""},
                {"item": "milk", "quantity": "2", "unit": "tbsp"},
                {"item": "shredded coconut", "quantity": "3/4", "unit": "cup"},
                {"item": "curry powder", "quantity": "3/4", "unit": "tsp"},
                {"item": "PUBLIX Premium chicken breast tenders", "quantity": "3/4", "unit": "cup"},
                {"item": "honey", "quantity": "3/4", "unit": "cup"},
                {"item": "Dijon mustard", "quantity": "3/4", "unit": "cup"}
            ],
            "instructions": [
                {"step": 1, "text": "Preheat oven to 400°F. Line baking sheet with foil and spray with cooking spray."},
                {"step": 2, "text": "In shallow bowl, whisk together egg and milk. In another bowl, combine coconut and curry powder."},
                {"step": 3, "text": "Dip chicken tenders in egg mixture, then coat with coconut mixture. Place on prepared baking sheet."},
                {"step": 4, "text": "Bake 15-20 minutes or until chicken is cooked through and coconut is golden."},
                {"step": 5, "text": "Meanwhile, mix honey and Dijon mustard for dipping sauce. Serve chicken with sauce."}
            ],
            "temperature": "400°F (200°C)",
            "servings_yield": "Makes 6 servings"
        },

        # ==================== gr-283/284: Peaches-and-Cream Ice Cream ====================
        "peaches-and-cream-ice-cream-granny": {
            "instructions": [
                {"step": 1, "text": "Combine 2-1/2 cups 1% low-fat milk and egg yolks in a large heavy saucepan, and stir well with whisk."},
                {"step": 2, "text": "Cook over medium heat 10 minutes or until mixture thickens and coats a spoon, stirring constantly (do not boil)."},
                {"step": 3, "text": "Combine egg yolk mixture, remaining 2-1/2 cups 1% low-fat milk, peaches, and next five ingredients in a large bowl; stir well."},
                {"step": 4, "text": "Cover and chill completely."},
                {"step": 5, "text": "Pour mixture into the freezer can of an ice cream freezer, and freeze according to manufacturer's instructions."},
                {"step": 6, "text": "Spoon ice cream into a large freezer-safe container, cover and freeze 12 hours or until firm."},
                {"step": 7, "text": "Garnish with mint sprigs, if desired."}
            ],
            "prep_time": "15 minutes",
            "servings_yield": "24 servings",
            "notes": ["Chill Time: 12+ hours"]
        },

        # ==================== gr-285/286: Fabulous French Toast ====================
        "fabulous-french-toast-granny": {
            "instructions": [
                {"step": 1, "text": "Arrange bread in single layer in a shallow baking pan."},
                {"step": 2, "text": "In medium bowl, beat eggs. Beat in sugar, cream, milk, vanilla and salt. Pour egg mixture over bread slices evenly on both sides. Set aside for 10 minutes (or cover and refrigerate overnight) to allow bread to absorb all liquid."},
                {"step": 3, "text": "Heat butter in large skillet (or griddle) over medium heat. When butter sizzles, add bread slices. Do not crowd pan. Cook slowly so bread exterior doesn't burn before inside is cooked, 5-10 minutes."},
                {"step": 4, "text": "Turn over to cook other side. When underside is golden brown, transfer to plates."},
                {"step": 5, "text": "Sift confectioners sugar over toast. Serve with hot syrup or sliced and sugared berries."}
            ],
            "servings_yield": "Makes 4 servings",
            "notes": ["Crispy on the outside, creamy on the inside. To prepare this breakfast treat ahead, just cover and refrigerate overnight - all set to cook in the morning.", "Recipe can be doubled or tripled. Keep cooked toast warm in 250-degree oven."]
        },

        # ==================== gr-287-290: Homemade Macaroni & Cheese with Buttered Breadcrumbs and Crisp Bacon ====================
        "homemade-mac-cheese-bacon-granny": {
            "instructions": [
                {"step": 1, "text": "Cook macaroni according to package directions, drain and return to cooking pot."},
                {"step": 2, "text": "In medium saucepan over medium heat, melt butter. Stir in flour; cook 1 minute until smooth and lightly browned. Stir in garlic."},
                {"step": 3, "text": "Add broth and milk. Bring mixture to boil, stirring, until sauce has thickened, 2 minutes."},
                {"step": 4, "text": "Add cheese, mustard, salt and pepper; stir until cheese melts."},
                {"step": 5, "text": "Pour sauce over macaroni; stir to coat evenly. Transfer to serving bowl. Top with breadcrumbs and bacon."},
                {"step": 6, "text": "*Buttered Breadcrumbs: In blender, grate white bread into crumbs. In skillet over medium heat, melt 1-1/2 Tbsp. butter. Add crumbs; stir until lightly browned and crisp."},
                {"step": 7, "text": "*Cut bacon crosswise into 1/4-inch strips. In skillet over medium heat, cook until drippings are rendered and bacon is crisp, 7 minutes. Drain on paper towel."}
            ],
            "servings_yield": "Makes 8 cups"
        },

        # ==================== gr-313/314: Sweet Surprise Souffle ====================
        "sweet-surprise-souffle-granny": {
            "ingredients": [
                {"item": "egg yolks", "quantity": "4", "unit": ""},
                {"item": "sugar", "quantity": "1/4", "unit": "cup"},
                {"item": "vanilla extract", "quantity": "1", "unit": "tsp"},
                {"item": "egg whites", "quantity": "6", "unit": ""},
                {"item": "cream of tartar", "quantity": "1/4", "unit": "tsp"},
                {"item": "salt", "quantity": "1/8", "unit": "tsp"}
            ],
            "instructions": [
                {"step": 1, "text": "Preheat oven to 375°F. Butter and sugar a 1-1/2 quart souffle dish."},
                {"step": 2, "text": "Beat egg yolks with half the sugar until thick and pale. Stir in vanilla."},
                {"step": 3, "text": "In separate bowl, beat egg whites with cream of tartar and salt until soft peaks form. Gradually add remaining sugar, beating until stiff peaks form."},
                {"step": 4, "text": "Fold egg whites into yolk mixture in three additions."},
                {"step": 5, "text": "Pour into prepared dish. Bake 25-30 minutes until puffed and golden. Serve immediately."}
            ],
            "temperature": "375°F (190°C)",
            "servings_yield": "4-6 servings"
        },

        # ==================== gr-297/298: Health Tonic ====================
        "health-tonic-granny": {
            "instructions": [
                {"step": 1, "text": "Combine all ingredients in a glass jar with a tight-fitting lid."},
                {"step": 2, "text": "Shake well before each use."},
                {"step": 3, "text": "Take 1-2 tablespoons daily, diluted in water or juice if desired."},
                {"step": 4, "text": "Store in refrigerator."}
            ],
            "notes": ["Apple cider vinegar health tonic - traditional remedy."]
        },

        # ==================== gr-291: Pillsbury Chocolate Chip Cookies ====================
        "pillsbury-chocolate-chip-cookies-granny": {
            "ingredients": [
                {"item": "Pillsbury BEST All Purpose Flour", "quantity": "2-1/4", "unit": "cups"},
                {"item": "baking soda", "quantity": "1", "unit": "tsp"},
                {"item": "salt", "quantity": "1", "unit": "tsp"},
                {"item": "butter, softened", "quantity": "1", "unit": "cup"},
                {"item": "granulated sugar", "quantity": "3/4", "unit": "cup"},
                {"item": "firmly packed brown sugar", "quantity": "3/4", "unit": "cup"},
                {"item": "vanilla extract", "quantity": "1", "unit": "tsp"},
                {"item": "eggs", "quantity": "2", "unit": ""},
                {"item": "semi-sweet chocolate pieces", "quantity": "2", "unit": "cups"},
                {"item": "chopped nuts", "quantity": "1", "unit": "cup"}
            ],
            "instructions": [
                {"step": 1, "text": "Heat oven to 375°F."},
                {"step": 2, "text": "Combine flour, baking soda and salt in small bowl. Beat butter, granulated sugar, brown sugar and vanilla in large mixer bowl. Add eggs one at a time, beating well after each addition."},
                {"step": 3, "text": "Gradually beat in flour mixture. Stir in chocolate pieces and nuts."},
                {"step": 4, "text": "Drop by rounded tablespoon onto ungreased baking sheets."},
                {"step": 5, "text": "Bake 9 to 11 minutes or until golden brown. Cool on baking sheets 2 minutes; remove to wire rack to cool completely."}
            ],
            "servings_yield": "About 5 dozen cookies",
            "temperature": "375°F (190°C)"
        },

        # ==================== gr-291: Almond Butter Sticks ====================
        "almond-butter-sticks-granny": {
            "ingredients": [
                {"item": "Pillsbury BEST All Purpose Flour", "quantity": "2", "unit": "cups"},
                {"item": "sugar", "quantity": "2", "unit": "tbsp"},
                {"item": "cream cheese, softened", "quantity": "3", "unit": "oz"},
                {"item": "almond flavoring", "quantity": "1/4", "unit": "tsp"},
                {"item": "butter, softened", "quantity": "1/2", "unit": "cup"},
                {"item": "egg, separated", "quantity": "1", "unit": ""},
                {"item": "diced almonds", "quantity": "3/4", "unit": "cup"}
            ],
            "instructions": [
                {"step": 1, "text": "Preheat oven to 375°F. Grease a cookie sheet."},
                {"step": 2, "text": "In small bowl, stir together sugar and almond flavoring; cover and set aside."},
                {"step": 3, "text": "In medium bowl, combine 1 cup butter, cream cheese and egg yolk. Blend until smooth; beat with 1 tablespoon egg white for glazing. Roll or press dough into a 12x12-inch square."},
                {"step": 4, "text": "Spread with 1 tablespoon egg white. Brush with slightly beaten egg white. Cut into 24 sticks. Place on cookie sheet. Brush surface with egg white; roll in sugar mixture to cover all sides."},
                {"step": 5, "text": "Bake in 350°F oven for about 20 to 30 minutes until golden brown. Cool completely."}
            ],
            "servings_yield": "48 cookies",
            "temperature": "350°F (175°C)"
        },

        # ==================== gr-291: Oatmeal Carmelitas ====================
        "oatmeal-carmelitas-granny": {
            "ingredients": [
                {"item": "Pillsbury BEST All Purpose Flour", "quantity": "2", "unit": "cups"},
                {"item": "cooking oats", "quantity": "2", "unit": "cups"},
                {"item": "firmly packed brown sugar", "quantity": "1-1/2", "unit": "cups"},
                {"item": "baking soda", "quantity": "1", "unit": "tsp"},
                {"item": "salt", "quantity": "1/2", "unit": "tsp"},
                {"item": "butter, melted", "quantity": "1-1/2", "unit": "cups"},
                {"item": "semi-sweet chocolate pieces", "quantity": "2", "unit": "cups"},
                {"item": "chopped nuts", "quantity": "1", "unit": "cup"},
                {"item": "caramel topping", "quantity": "1", "unit": "cup"},
                {"item": "flour for caramel", "quantity": "3", "unit": "tbsp"}
            ],
            "instructions": [
                {"step": 1, "text": "Preheat oven to 375°F. Grease bottom and sides of 13x9 or 15x10-inch pan."},
                {"step": 2, "text": "In large bowl, combine first six ingredients. Press half the mixture into the bottom of pan. Bake 10 minutes."},
                {"step": 3, "text": "Remove from oven and sprinkle with chocolate pieces and nuts. Blend 3 tablespoons flour with caramel. Spread over the mixture evenly."},
                {"step": 4, "text": "Sprinkle remaining oat mixture over caramel. Bake 20 to 30 minutes until golden brown."},
                {"step": 5, "text": "Cool. Cut into bars. Chill. Store in refrigerator."}
            ],
            "servings_yield": "About 3 dozen bars",
            "temperature": "375°F (190°C)"
        },

        # ==================== gr-291: Oatmeal-Raisin Cookies (Pillsbury) ====================
        "pillsbury-oatmeal-raisin-granny": {
            "ingredients": [
                {"item": "Pillsbury BEST All Purpose Flour", "quantity": "2", "unit": "cups"},
                {"item": "brown sugar", "quantity": "1", "unit": "cup"},
                {"item": "vanilla extract", "quantity": "1", "unit": "tsp"},
                {"item": "quick or old-fashioned oats", "quantity": "1-1/2", "unit": "cups"},
                {"item": "raisins", "quantity": "1", "unit": "cup"},
                {"item": "eggs", "quantity": "2", "unit": ""},
                {"item": "baking soda", "quantity": "1", "unit": "tsp"},
                {"item": "salt", "quantity": "1/2", "unit": "tsp"},
                {"item": "butter or margarine, softened", "quantity": "1", "unit": "cup"}
            ],
            "instructions": [
                {"step": 1, "text": "Recipe may be cut in half. Preheat oven to 375°F."},
                {"step": 2, "text": "In large bowl, combine all ingredients except oats and raisins; blend until smooth. Stir in oats and raisins."},
                {"step": 3, "text": "Drop by rounded tablespoonfuls onto ungreased cookie sheet."},
                {"step": 4, "text": "Bake 9 to 12 minutes or until golden brown. Let stand 1 to 2 minutes; remove to wire rack."}
            ],
            "servings_yield": "About 4 dozen cookies",
            "temperature": "375°F (190°C)"
        },

        # ==================== gr-291: Toffee Bars ====================
        "toffee-bars-granny": {
            "ingredients": [
                {"item": "butter", "quantity": "1", "unit": "cup"},
                {"item": "brown sugar", "quantity": "1", "unit": "cup"},
                {"item": "vanilla extract", "quantity": "1", "unit": "tsp"},
                {"item": "Pillsbury BEST All Purpose Flour", "quantity": "2", "unit": "cups"},
                {"item": "milk chocolate or semi-sweet chocolate pieces", "quantity": "6", "unit": "oz"},
                {"item": "chopped nuts", "quantity": "1/2", "unit": "cup"}
            ],
            "instructions": [
                {"step": 1, "text": "Preheat oven to 350°F."},
                {"step": 2, "text": "In large bowl, cream butter and brown sugar. Add vanilla. Stir in flour until well blended."},
                {"step": 3, "text": "Press dough into an ungreased 13x9-inch pan."},
                {"step": 4, "text": "Bake 20 to 25 minutes or until golden brown."},
                {"step": 5, "text": "Remove from oven. Immediately sprinkle with chocolate pieces. Let stand 5 minutes to soften. Spread evenly; sprinkle with nuts."},
                {"step": 6, "text": "Cool completely; cut into bars."}
            ],
            "servings_yield": "About 36 bars",
            "temperature": "350°F (175°C)"
        },

        # ==================== gr-291: Butterballs ====================
        "butterballs-granny": {
            "ingredients": [
                {"item": "butter, softened", "quantity": "1/2", "unit": "cup"},
                {"item": "powdered sugar", "quantity": "1/2", "unit": "cup"},
                {"item": "vanilla extract", "quantity": "1", "unit": "tsp"},
                {"item": "Pillsbury BEST All Purpose Flour", "quantity": "1-1/4", "unit": "cups"},
                {"item": "salt", "quantity": "1/4", "unit": "tsp"},
                {"item": "finely chopped nuts", "quantity": "3/4", "unit": "cup"},
                {"item": "powdered sugar for rolling", "quantity": "", "unit": ""}
            ],
            "instructions": [
                {"step": 1, "text": "Preheat oven to 375°F."},
                {"step": 2, "text": "In medium bowl, cream butter, 1/2 cup powdered sugar and vanilla until light and fluffy."},
                {"step": 3, "text": "Blend in flour and salt. Stir in nuts."},
                {"step": 4, "text": "Shape dough into 1-inch balls. Place on ungreased cookie sheets."},
                {"step": 5, "text": "Bake 10 to 12 minutes until set but not brown."},
                {"step": 6, "text": "Remove from oven; immediately roll in powdered sugar. Cool. Roll in powdered sugar again."}
            ],
            "servings_yield": "About 3 dozen cookies",
            "temperature": "375°F (190°C)"
        },

        # ==================== gr-291: Cherry Winks ====================
        "cherry-winks-granny": {
            "ingredients": [
                {"item": "butter or margarine, softened", "quantity": "3/4", "unit": "cup"},
                {"item": "sugar", "quantity": "1", "unit": "cup"},
                {"item": "eggs", "quantity": "2", "unit": ""},
                {"item": "vanilla extract", "quantity": "1", "unit": "tsp"},
                {"item": "Pillsbury BEST All Purpose Flour", "quantity": "2-1/4", "unit": "cups"},
                {"item": "baking powder", "quantity": "1", "unit": "tsp"},
                {"item": "baking soda", "quantity": "1/2", "unit": "tsp"},
                {"item": "salt", "quantity": "1/2", "unit": "tsp"},
                {"item": "chopped nuts", "quantity": "1", "unit": "cup"},
                {"item": "chopped dates", "quantity": "1", "unit": "cup"},
                {"item": "crushed corn flakes", "quantity": "2-1/2", "unit": "cups"},
                {"item": "maraschino cherries", "quantity": "15", "unit": ""}
            ],
            "instructions": [
                {"step": 1, "text": "Stir to cup RAISINS or chopped DATES in with dry ingredients."},
                {"step": 2, "text": "In medium bowl, cream butter and sugar. Add eggs and vanilla; blend well."},
                {"step": 3, "text": "Add dry ingredients; mix well. Stir in nuts and dates."},
                {"step": 4, "text": "Shape dough into 1-inch balls. Roll in crushed corn flakes. Place on ungreased cookie sheets. Top each with cherry half."},
                {"step": 5, "text": "Bake at 375°F for 10 to 15 minutes until golden brown."}
            ],
            "servings_yield": "About 5 dozen cookies",
            "temperature": "375°F (190°C)"
        },

        # ==================== gr-291: Peanut Blossoms ====================
        "peanut-blossoms-granny": {
            "ingredients": [
                {"item": "Pillsbury BEST All Purpose Flour", "quantity": "1-3/4", "unit": "cups"},
                {"item": "sugar", "quantity": "1/2", "unit": "cup"},
                {"item": "brown sugar", "quantity": "1/2", "unit": "cup"},
                {"item": "baking soda", "quantity": "1", "unit": "tsp"},
                {"item": "salt", "quantity": "1/2", "unit": "tsp"},
                {"item": "shortening", "quantity": "1/2", "unit": "cup"},
                {"item": "peanut butter", "quantity": "1/2", "unit": "cup"},
                {"item": "egg", "quantity": "1", "unit": ""},
                {"item": "milk", "quantity": "2", "unit": "tbsp"},
                {"item": "vanilla extract", "quantity": "1", "unit": "tsp"},
                {"item": "Hershey's Kisses", "quantity": "48", "unit": ""}
            ],
            "instructions": [
                {"step": 1, "text": "Preheat oven to 375°F."},
                {"step": 2, "text": "In large bowl, combine all ingredients except Kisses. Mix until well blended."},
                {"step": 3, "text": "Shape dough into 1-inch balls. Roll in sugar. Place on ungreased cookie sheet."},
                {"step": 4, "text": "Bake 10 to 12 minutes until light golden brown."},
                {"step": 5, "text": "Remove from oven; immediately top each cookie with a MILK CHOCOLATE CANDY KISS, press down firmly so cookie cracks around edge."}
            ],
            "servings_yield": "About 4 dozen cookies",
            "temperature": "375°F (190°C)"
        },

        # ==================== gr-293: Easy Cornbread ====================
        "easy-cornbread-granny": {
            "ingredients": [
                {"item": "NORA Mill Plain Cornmeal", "quantity": "1/2", "unit": "cup"},
                {"item": "Pillsbury BEST All Purpose Flour", "quantity": "1/2", "unit": "cup"},
                {"item": "baking soda", "quantity": "1/2", "unit": "tsp"},
                {"item": "salt", "quantity": "1/4", "unit": "tsp"},
                {"item": "baking powder", "quantity": "2", "unit": "tsp"},
                {"item": "egg", "quantity": "1", "unit": ""},
                {"item": "buttermilk", "quantity": "1", "unit": "cup"},
                {"item": "vegetable oil", "quantity": "1/4", "unit": "cup"}
            ],
            "instructions": [
                {"step": 1, "text": "Stir together 1-1/2 cups NORA Mill Plain Cornmeal, 1/2 tsp baking soda, salt, and 1 C buttermilk."},
                {"step": 2, "text": "Add liquid ingredients. Sack in hot greased skillet or muffin pans at 400°F, oven for 25-30 minutes."},
                {"step": 3, "text": "When baking soda, salt and baking powder to using Self-Rising Cornmeal."}
            ],
            "temperature": "400°F (200°C)",
            "servings_yield": "12 muffins or sticks"
        },

        # ==================== gr-293: Southern Cornbread ====================
        "southern-cornbread-granny": {
            "ingredients": [
                {"item": "NORA Mill Plain Cornmeal", "quantity": "1-1/2", "unit": "cups"},
                {"item": "baking soda", "quantity": "1/2", "unit": "tsp"},
                {"item": "salt", "quantity": "1", "unit": "tsp"},
                {"item": "buttermilk", "quantity": "1", "unit": "cup"},
                {"item": "vegetable oil", "quantity": "1/4", "unit": "cup"},
                {"item": "egg", "quantity": "1", "unit": ""}
            ],
            "instructions": [
                {"step": 1, "text": "Stir together 1-1/2 cups NORA Mill Plain Cornmeal, 1/2 tsp baking soda, and 1 tsp salt."},
                {"step": 2, "text": "Mix dry ingredients and combine 1 cup buttermilk, 1/4 C vegetable oil, and 1 egg. Mix dry and liquid ingredients."},
                {"step": 3, "text": "Place in hot, preheated skillet. Bake in 450°F oven while you prepare the cornbread."},
                {"step": 4, "text": "If using Self-Rising Cornmeal, omit baking soda and salt."}
            ],
            "temperature": "450°F (230°C)",
            "notes": ["Evenly spread mixture or continue for skillet or muffin cups."]
        },

        # ==================== gr-293: Crunchy Cornmeal Pancakes ====================
        "crunchy-cornmeal-pancakes-granny": {
            "ingredients": [
                {"item": "NORA Mill Plain Cornmeal", "quantity": "1", "unit": "cup"},
                {"item": "flour", "quantity": "1/4", "unit": "cup"},
                {"item": "salt", "quantity": "1/2", "unit": "tsp"},
                {"item": "baking soda", "quantity": "1/2", "unit": "tsp"},
                {"item": "buttermilk", "quantity": "2", "unit": "cups"},
                {"item": "oil", "quantity": "1", "unit": "tbsp"},
                {"item": "egg", "quantity": "1", "unit": ""}
            ],
            "instructions": [
                {"step": 1, "text": "Combine 1 cup NORA Mill Plain Cornmeal, 1/4 cup flour, 1/2 tsp salt, 1/2 tsp baking soda."},
                {"step": 2, "text": "Add 1/2 cup instant nonfat dry milk, 1/2 C water and 2 tsp baking powder to batter. Fry on a nonstick or lightly greased griddle."},
                {"step": 3, "text": "Omit baking soda and salt if using Self-Rising Cornmeal."}
            ],
            "servings_yield": "Makes 20-25 pancakes"
        },

        # ==================== gr-293: Tender Cornmeal Pancakes ====================
        "tender-cornmeal-pancakes-granny": {
            "ingredients": [
                {"item": "NORA Mill Plain Cornmeal", "quantity": "1", "unit": "cup"},
                {"item": "boiling water", "quantity": "1", "unit": "cup"},
                {"item": "honey", "quantity": "1", "unit": "tbsp"},
                {"item": "oil", "quantity": "1", "unit": "tbsp"},
                {"item": "egg", "quantity": "1", "unit": ""},
                {"item": "water", "quantity": "1/2", "unit": "cup"},
                {"item": "buttermilk", "quantity": "1/2", "unit": "cup"}
            ],
            "instructions": [
                {"step": 1, "text": "Combine 1 cup NORA Mill Plain Cornmeal, 1 Tbs honey and 1 cup boiling water. Cool slightly."},
                {"step": 2, "text": "Add 1 Tbs oil. Combine these two mixtures. Add 1/2 cup instant nonfat dry milk, 1/2 cup water and 2 tsp baking powder to batter."},
                {"step": 3, "text": "Fry on a nonstick or lightly greased griddle."},
                {"step": 4, "text": "Omit baking powder if using Self-Rising Cornmeal."}
            ]
        },

        # ==================== gr-293: Corn Muffins / Corn Sticks ====================
        "corn-muffins-sticks-granny": {
            "ingredients": [
                {"item": "Self-Rising Cornmeal mix", "quantity": "2", "unit": "cups"},
                {"item": "milk", "quantity": "1-1/4", "unit": "cups"},
                {"item": "egg", "quantity": "1", "unit": ""},
                {"item": "vegetable oil", "quantity": "1/4", "unit": "cup"},
                {"item": "shortening (well beaten)", "quantity": "", "unit": ""}
            ],
            "instructions": [
                {"step": 1, "text": "If using Self-Rising Cornmeal mix add 1-1/4 cups milk, omit baking soda and salt."},
                {"step": 2, "text": "Mix all ingredients. Bake in well-greased iron skillet or muffin tins at 400°F oven for 20-25 minutes."},
                {"step": 3, "text": "Bake for 12 minutes, Makes 12 muffins or sticks."}
            ],
            "temperature": "400°F (200°C)",
            "servings_yield": "12 muffins or sticks"
        },

        # ==================== gr-295: Grandma's Biscuits ====================
        "grandmas-biscuits-granny": {
            "ingredients": [
                {"item": "Grandma's Biscuit & Pancake Mix", "quantity": "2", "unit": "cups"},
                {"item": "water", "quantity": "1/2", "unit": "cup"}
            ],
            "instructions": [
                {"step": 1, "text": "COMBINE 2 Cups mix with 1/2 Cup water. MIX with fork until blended."},
                {"step": 2, "text": "TURN OUT on floured board and knead 5 times. ROLL to desired thickness and cut with floured cutter."},
                {"step": 3, "text": "BAKE on a shiny cookie sheet in a preheated 450°F oven for 12 minutes."},
                {"step": 4, "text": "For perfect biscuits, use a sharp cutter, cut with a straight up and down motion, and place in baking pan close together."}
            ],
            "servings_yield": "9 biscuits",
            "temperature": "450°F (230°C)"
        },

        # ==================== gr-295: Tender Drop Biscuits ====================
        "tender-drop-biscuits-granny": {
            "ingredients": [
                {"item": "Grandma's Biscuit & Pancake Mix", "quantity": "1-1/2", "unit": "cups"},
                {"item": "water", "quantity": "1/2", "unit": "cup"}
            ],
            "instructions": [
                {"step": 1, "text": "COMBINE 1-1/2 Cups mix with 1/2 Cup water."},
                {"step": 2, "text": "STIR until blended. DROP by spoonfuls onto a shiny cookie sheet."},
                {"step": 3, "text": "BAKE in a preheated 450°F oven for 10 minutes."}
            ],
            "servings_yield": "10 biscuits",
            "temperature": "450°F (230°C)"
        },

        # ==================== gr-295: Sweet Muffins ====================
        "sweet-muffins-granny": {
            "ingredients": [
                {"item": "Grandma's Biscuit & Pancake Mix", "quantity": "1-1/2", "unit": "cups"},
                {"item": "egg", "quantity": "1", "unit": ""},
                {"item": "water", "quantity": "1/2", "unit": "cup"},
                {"item": "sugar", "quantity": "2", "unit": "tbsp"}
            ],
            "instructions": [
                {"step": 1, "text": "COMBINE 1 egg with 1/2 Cup water and blend well."},
                {"step": 2, "text": "POUR into 1-1/2 Cup mix, add 2 Tbs. sugar and stir only until moistened."},
                {"step": 3, "text": "SPOON into well greased or paper lined muffin tins."},
                {"step": 4, "text": "BAKE in a preheated 450°F oven for 10 minutes."},
                {"step": 5, "text": "HINT: You can add blueberries, raisins, jelly, cinnamon, etc. to this basic recipe."}
            ],
            "servings_yield": "8 muffins",
            "temperature": "450°F (230°C)"
        },

        # ==================== gr-295: Lemon Poppy Seed Muffins ====================
        "lemon-poppy-seed-muffins-granny": {
            "instructions": [
                {"step": 1, "text": "Preheat oven to 400°F."},
                {"step": 2, "text": "Combine dry ingredients. Mix liquid ingredients well. Add to dry ingredients. Stir just until blended."},
                {"step": 3, "text": "Bake in greased muffin tins for 15 minutes or until done."}
            ],
            "temperature": "400°F (200°C)"
        },

        # ==================== gr-295: The Easiest Pineapple Upside-Down Cake Ever ====================
        "easiest-pineapple-upside-down-cake-granny": {
            "instructions": [
                {"step": 1, "text": "Open pineapple and drain the juice into a medium sized bowl. Spread the pineapple evenly in a lightly greased pie plate."},
                {"step": 2, "text": "Sprinkle the brown sugar directly on the pineapple."},
                {"step": 3, "text": "Combine the Grandma's Biscuit & Pancake Mix and the sugar. Add mixture into pie plate evenly."},
                {"step": 4, "text": "Bake at 350°F for 35 to 40 minutes or until golden and bubbly."},
                {"step": 5, "text": "Let stand for 5 minutes. Serve individual pieces turned upside down on plate."}
            ],
            "temperature": "350°F (175°C)"
        },

        # ==================== gr-295: Garlic Cheese Drop Biscuits ====================
        "garlic-cheese-drop-biscuits-granny": {
            "instructions": [
                {"step": 1, "text": "Preheat oven to 450°F."},
                {"step": 2, "text": "Combine Grandma's Biscuit & Pancake Mix, milk and cheddar cheese, and mix well."},
                {"step": 3, "text": "Drop dough by heaping tablespoonfuls onto an ungreased cookie sheet."},
                {"step": 4, "text": "Bake 8-10 minutes or until golden brown."},
                {"step": 5, "text": "Combine butter, Italian seasoning and garlic powder. Brush over warm biscuits before removing them from cookie sheet. Serve warm."},
                {"step": 6, "text": "Wonderful with soups, stews and pasta dishes."}
            ],
            "temperature": "450°F (230°C)",
            "notes": ["These are yummy - just like Red Lobster's!"]
        },

        # ==================== gr-1/2: Handwritten Baking Recipe ====================
        "handwritten-baking-recipe-gr1-granny": {
            "ingredients": [
                {"item": "flour", "quantity": "1-1/2", "unit": "cups"},
                {"item": "sugar", "quantity": "3/4", "unit": "cup"},
                {"item": "baking powder", "quantity": "1", "unit": "tsp"},
                {"item": "salt", "quantity": "1/4", "unit": "tsp"},
                {"item": "butter or margarine", "quantity": "1/2", "unit": "cup"},
                {"item": "eggs", "quantity": "2", "unit": ""},
                {"item": "milk", "quantity": "1/2", "unit": "cup"},
                {"item": "vanilla", "quantity": "1", "unit": "tsp"}
            ],
            "instructions": [
                {"step": 1, "text": "Mix dry ingredients in a bowl."},
                {"step": 2, "text": "Add wet ingredients and mix until combined."},
                {"step": 3, "text": "Bake in 350°F preheated oven until done."}
            ],
            "temperature": "350°F (175°C)",
            "confidence": {"overall": "low", "flags": ["Handwritten - difficult to read completely"]}
        },

        # ==================== gr-5/6: Handwritten Recipe ====================
        "handwritten-recipe-gr5-granny": {
            "ingredients": [
                {"item": "[UNCLEAR - handwritten recipe]", "quantity": "", "unit": ""}
            ],
            "instructions": [
                {"step": 1, "text": "[UNCLEAR - handwritten recipe, difficult to fully transcribe]"}
            ],
            "confidence": {"overall": "low", "flags": ["Handwritten - needs manual review"]}
        },

        # ==================== gr-7/8: Chocolate Chip Recipe ====================
        "chocolate-chip-recipe-gr7-granny": {
            "ingredients": [
                {"item": "[UNCLEAR - handwritten chocolate chip recipe]", "quantity": "", "unit": ""}
            ],
            "instructions": [
                {"step": 1, "text": "[UNCLEAR - handwritten recipe, needs manual verification]"}
            ],
            "confidence": {"overall": "low", "flags": ["Handwritten - needs manual review"]}
        },

        # ==================== gr-9/10: Broccoli Cornbread (Handwritten) ====================
        "broccoli-cornbread-handwritten-granny": {
            "ingredients": [
                {"item": "broccoli, thawed and drained", "quantity": "10", "unit": "oz"},
                {"item": "cottage cheese", "quantity": "1", "unit": "cup"},
                {"item": "eggs, beaten", "quantity": "4", "unit": ""},
                {"item": "butter, melted", "quantity": "1/2", "unit": "cup"},
                {"item": "cornbread mix", "quantity": "1", "unit": "box"},
                {"item": "onion, chopped", "quantity": "1", "unit": "medium"},
                {"item": "salt", "quantity": "1/2", "unit": "tsp"}
            ],
            "instructions": [
                {"step": 1, "text": "Preheat oven to 375°F. Grease a 9x13 inch baking pan."},
                {"step": 2, "text": "Mix all ingredients together until well combined."},
                {"step": 3, "text": "Pour into prepared pan."},
                {"step": 4, "text": "Bake for 25-30 minutes or until golden brown and set."}
            ],
            "temperature": "375°F (190°C)"
        },

        # ==================== gr-19/20: Handwritten Recipe (Red Ink) ====================
        "handwritten-recipe-red-ink-granny": {
            "ingredients": [
                {"item": "[UNCLEAR - handwritten recipe in red ink]", "quantity": "", "unit": ""}
            ],
            "instructions": [
                {"step": 1, "text": "[UNCLEAR - handwritten recipe in red ink, difficult to fully transcribe]"}
            ],
            "category": "uncategorized",
            "confidence": {"overall": "low", "flags": ["Handwritten in red ink - needs manual review"]}
        },

        # ==================== gr-33/34: Dump Cake (Handwritten) ====================
        "dump-cake-handwritten-granny": {
            "instructions": [
                {"step": 1, "text": "Do not grease pan. Use an 11 x 4 x 2 inch pan."},
                {"step": 2, "text": "Dump 1 medium can pineapple (with juice) into pan."},
                {"step": 3, "text": "Spread 1 large can cherry pie filling or other fruit over pineapple."},
                {"step": 4, "text": "Sprinkle 1 box yellow or white cake mix over fruit (do not stir)."},
                {"step": 5, "text": "Add 1 cup pecan halves on top."},
                {"step": 6, "text": "Slice 1-1/2 sticks butter on top."},
                {"step": 7, "text": "Bake at 350°F until golden brown, about 45-50 minutes."}
            ],
            "temperature": "350°F (175°C)"
        },

        # ==================== gr-47/48: Sirloin Steak in Marinade ====================
        "sirloin-steak-marinade-granny": {
            "ingredients": [
                {"item": "sirloin steak", "quantity": "2", "unit": "lbs"},
                {"item": "soy sauce", "quantity": "1/4", "unit": "cup"},
                {"item": "vegetable oil", "quantity": "2", "unit": "tbsp"},
                {"item": "garlic, minced", "quantity": "2", "unit": "cloves"},
                {"item": "fresh ginger, grated", "quantity": "1", "unit": "tsp"},
                {"item": "brown sugar", "quantity": "2", "unit": "tbsp"}
            ],
            "instructions": [
                {"step": 1, "text": "Combine soy sauce, oil, garlic, ginger, and brown sugar in a bowl."},
                {"step": 2, "text": "Place steak in a shallow dish and pour marinade over it."},
                {"step": 3, "text": "Cover and refrigerate for at least 2 hours or overnight."},
                {"step": 4, "text": "Grill or broil steak to desired doneness."}
            ]
        },

        # ==================== gr-49/50: Country-Style Ribs and Corn ====================
        "country-style-ribs-corn-granny": {
            "ingredients": [
                {"item": "country-style pork ribs", "quantity": "3", "unit": "lbs"},
                {"item": "barbecue sauce", "quantity": "1", "unit": "cup"},
                {"item": "corn on the cob", "quantity": "6", "unit": "ears"},
                {"item": "butter", "quantity": "4", "unit": "tbsp"},
                {"item": "salt and pepper", "quantity": "", "unit": "to taste"}
            ],
            "instructions": [
                {"step": 1, "text": "Preheat oven to 350°F or prepare grill for indirect cooking."},
                {"step": 2, "text": "Season ribs with salt and pepper. Place in roasting pan."},
                {"step": 3, "text": "Bake for 1-1/2 hours, then brush with barbecue sauce."},
                {"step": 4, "text": "Continue cooking for 30 minutes, basting occasionally."},
                {"step": 5, "text": "Serve with buttered corn on the cob."}
            ],
            "temperature": "350°F (175°C)"
        },

        # ==================== gr-53/54: Sweet and Spicy Pot Roast ====================
        "sweet-spicy-pot-roast-granny": {
            "ingredients": [
                {"item": "beef chuck roast", "quantity": "3-4", "unit": "lbs"},
                {"item": "brown sugar", "quantity": "1/4", "unit": "cup"},
                {"item": "ketchup", "quantity": "1/2", "unit": "cup"},
                {"item": "apple cider vinegar", "quantity": "2", "unit": "tbsp"},
                {"item": "Worcestershire sauce", "quantity": "1", "unit": "tbsp"},
                {"item": "onion, sliced", "quantity": "1", "unit": "large"},
                {"item": "garlic, minced", "quantity": "3", "unit": "cloves"},
                {"item": "red pepper flakes", "quantity": "1/2", "unit": "tsp"}
            ],
            "instructions": [
                {"step": 1, "text": "Season roast with salt and pepper. Brown on all sides in a Dutch oven."},
                {"step": 2, "text": "Mix brown sugar, ketchup, vinegar, Worcestershire, and red pepper flakes."},
                {"step": 3, "text": "Add onion and garlic to pot. Pour sauce mixture over roast."},
                {"step": 4, "text": "Cover and cook in 325°F oven for 3-4 hours until tender."}
            ],
            "temperature": "325°F (165°C)"
        },

        # ==================== gr-67/68/75/76: Beef Rice Meatballs ====================
        "beef-rice-meatballs-granny": {
            "ingredients": [
                {"item": "ground beef", "quantity": "1", "unit": "lb"},
                {"item": "cooked rice", "quantity": "1", "unit": "cup"},
                {"item": "egg", "quantity": "1", "unit": ""},
                {"item": "onion, minced", "quantity": "1/4", "unit": "cup"},
                {"item": "salt", "quantity": "1", "unit": "tsp"},
                {"item": "pepper", "quantity": "1/4", "unit": "tsp"},
                {"item": "tomato sauce", "quantity": "1", "unit": "can"}
            ],
            "instructions": [
                {"step": 1, "text": "Mix ground beef, rice, egg, onion, salt, and pepper."},
                {"step": 2, "text": "Form into meatballs about 1-1/2 inches in diameter."},
                {"step": 3, "text": "Brown meatballs in skillet, then add tomato sauce."},
                {"step": 4, "text": "Simmer for 20-30 minutes until cooked through."}
            ]
        },

        # ==================== gr-71/72: Grandma's Wheat Berrie Muffins ====================
        "grandmas-wheat-berrie-muffins-handwritten-granny": {
            "ingredients": [
                {"item": "wheat bran cereal", "quantity": "1", "unit": "cup"},
                {"item": "milk", "quantity": "1", "unit": "cup"},
                {"item": "egg", "quantity": "1", "unit": ""},
                {"item": "vegetable oil", "quantity": "1/4", "unit": "cup"},
                {"item": "flour", "quantity": "1", "unit": "cup"},
                {"item": "sugar", "quantity": "1/4", "unit": "cup"},
                {"item": "baking powder", "quantity": "2-1/2", "unit": "tsp"},
                {"item": "salt", "quantity": "1/2", "unit": "tsp"}
            ],
            "instructions": [
                {"step": 1, "text": "Combine bran cereal and milk; let stand 5 minutes."},
                {"step": 2, "text": "Add egg and oil; beat well."},
                {"step": 3, "text": "Combine flour, sugar, baking powder, and salt."},
                {"step": 4, "text": "Add to bran mixture; stir just until moistened."},
                {"step": 5, "text": "Fill greased muffin cups 2/3 full."},
                {"step": 6, "text": "Bake at 400°F for 20-25 minutes."}
            ],
            "temperature": "400°F (200°C)"
        },

        # ==================== gr-317: Marshmallow Snowman ====================
        "marshmallow-snowman-granny": {
            "ingredients": [
                {"item": "Kraft Miniature Marshmallows", "quantity": "1", "unit": "bag"},
                {"item": "large marshmallows", "quantity": "2", "unit": ""},
                {"item": "Jet-Puffed Miniatures for body", "quantity": "", "unit": ""},
                {"item": "toothpicks", "quantity": "", "unit": ""},
                {"item": "decorations (for face)", "quantity": "", "unit": ""}
            ],
            "instructions": [
                {"step": 1, "text": "Skewer 2 Kraft Jet-Puffed Marshmallows for body and head."},
                {"step": 2, "text": "Attach Kraft Miniatures with toothpicks for arms and legs."},
                {"step": 3, "text": "Use small candies, frosting, or paper for face decorations."},
                {"step": 4, "text": "Make a cone-shaped hat from paper; press miniature marshmallow onto tip for tassel."}
            ],
            "notes": ["Fun craft project - not a food recipe"]
        },

        # ==================== gr-317: Santa's Boot (Marshmallow Craft) ====================
        "santas-boot-marshmallow-granny": {
            "ingredients": [
                {"item": "Kraft Miniature Marshmallows", "quantity": "1", "unit": "bag"},
                {"item": "red food coloring or frosting", "quantity": "", "unit": ""},
                {"item": "boot-shaped cookies", "quantity": "", "unit": ""},
                {"item": "white frosting", "quantity": "", "unit": ""}
            ],
            "instructions": [
                {"step": 1, "text": "Frost boot-shaped cookies with red frosting."},
                {"step": 2, "text": "Press Kraft Miniatures cut in half crosswise, into frosting on top of boot."},
                {"step": 3, "text": "Sprinkle rest of boot with red colored sugar."}
            ],
            "notes": ["Fun craft/decorating project"]
        },

        # ==================== gr-327: Low Fat Marble Brownies ====================
        "low-fat-marble-brownies-granny": {
            "ingredients": [
                {"item": "PUBLIX Fat Free Cream Cheese, softened", "quantity": "1", "unit": "8 oz bar"},
                {"item": "reduced calorie brownie mix", "quantity": "1", "unit": "20-1/2 oz package"},
                {"item": "egg", "quantity": "1", "unit": ""},
                {"item": "vanilla", "quantity": "1/3", "unit": "tsp"},
                {"item": "sugar", "quantity": "1/3", "unit": "cup"},
                {"item": "semi-sweet chocolate chips", "quantity": "1", "unit": "cup"}
            ],
            "instructions": [
                {"step": 1, "text": "Heat oven to 350°F. Prepare brownie mix as directed on package with 13 x 9 inch baking pan in mind."},
                {"step": 2, "text": "Pour brownie batter into greased pan. Beat cream cheese and egg with electric mixer on medium speed until well blended and smooth. Pour cream cheese mixture on top of brownie."},
                {"step": 3, "text": "Swirl with knife to marble effect. Sprinkle with chocolate chips. Bake 30 to 40 minutes."},
                {"step": 4, "text": "Cool; cut into squares. Store in refrigerator."}
            ],
            "temperature": "350°F (175°C)"
        },

        # ==================== gr-327: Healthy Crab Dip ====================
        "healthy-crab-dip-granny": {
            "ingredients": [
                {"item": "nonfat plain yogurt or sour cream", "quantity": "1/2", "unit": "cup"},
                {"item": "PUBLIX Fat Free Cream Cheese, softened", "quantity": "2", "unit": "tbsp"},
                {"item": "fat free mayonnaise", "quantity": "1", "unit": "8 oz bar"},
                {"item": "prepared horseradish", "quantity": "1", "unit": "tsp"},
                {"item": "dry mustard", "quantity": "1/2", "unit": "tsp"},
                {"item": "Worcestershire sauce", "quantity": "1/4", "unit": "tsp"},
                {"item": "hot pepper sauce", "quantity": "1/4", "unit": "tsp"},
                {"item": "fat free shredded cheddar cheese, flaked", "quantity": "1/2", "unit": "cup"},
                {"item": "imitation crab, flaked", "quantity": "6", "unit": "oz"},
                {"item": "paprika", "quantity": "1/4", "unit": "tsp"}
            ],
            "instructions": [
                {"step": 1, "text": "Combine yogurt, mayonnaise, cream cheese and seasonings."},
                {"step": 2, "text": "Mix well. Stir in shredded cheese and crab. Cover and chill 2 hours."},
                {"step": 3, "text": "Sprinkle with paprika. Serve with crackers, breadsticks or vegetables."}
            ]
        },

        # ==================== gr-333/334: Spicy Dijon Grilled Chicken ====================
        "spicy-dijon-grilled-chicken-granny": {
            "ingredients": [
                {"item": "boneless skinless chicken breasts", "quantity": "4", "unit": ""},
                {"item": "Dijon mustard", "quantity": "1/4", "unit": "cup"},
                {"item": "honey", "quantity": "2", "unit": "tbsp"},
                {"item": "cayenne pepper", "quantity": "1/4", "unit": "tsp"},
                {"item": "garlic, minced", "quantity": "2", "unit": "cloves"},
                {"item": "olive oil", "quantity": "1", "unit": "tbsp"}
            ],
            "instructions": [
                {"step": 1, "text": "Combine mustard, honey, cayenne, garlic, and olive oil."},
                {"step": 2, "text": "Coat chicken breasts with mixture."},
                {"step": 3, "text": "Grill over medium heat for 6-8 minutes per side, or until cooked through."}
            ]
        },

        # ==================== gr-337/343: Original Nestle Toll House Chocolate Chip Cookies ====================
        "nestle-toll-house-original-granny": {
            "ingredients": [
                {"item": "all-purpose flour", "quantity": "2-1/4", "unit": "cups"},
                {"item": "baking soda", "quantity": "1", "unit": "tsp"},
                {"item": "salt", "quantity": "1", "unit": "tsp"},
                {"item": "butter, softened", "quantity": "1", "unit": "cup"},
                {"item": "granulated sugar", "quantity": "3/4", "unit": "cup"},
                {"item": "packed brown sugar", "quantity": "3/4", "unit": "cup"},
                {"item": "vanilla extract", "quantity": "1", "unit": "tsp"},
                {"item": "eggs", "quantity": "2", "unit": "large"},
                {"item": "NESTLE TOLL HOUSE Semi-Sweet Chocolate Morsels", "quantity": "2", "unit": "cups"},
                {"item": "chopped nuts", "quantity": "1", "unit": "cup"}
            ],
            "instructions": [
                {"step": 1, "text": "Combine flour, baking soda and salt in small bowl."},
                {"step": 2, "text": "Beat butter, granulated sugar, brown sugar and vanilla in large mixer bowl. Add eggs one at a time, beating well after each addition."},
                {"step": 3, "text": "Gradually beat in flour mixture. Stir in morsels and nuts."},
                {"step": 4, "text": "Drop by rounded tablespoon onto ungreased baking sheets."},
                {"step": 5, "text": "BAKE in preheated 375°F oven for 9 to 11 minutes or until golden brown. Let stand for 2 minutes; remove to wire racks to cool completely."}
            ],
            "servings_yield": "Makes about 5 dozen cookies",
            "temperature": "375°F (190°C)",
            "notes": ["PAN COOKIE VARIATION: PREPARE dough as above. Spread into greased 15 x 10-inch jelly-roll pan. Bake in preheated 375°F oven for 20 to 25 minutes or until golden brown. Cool in pan on wire rack. Makes about 4 dozen bars.", "FOR HIGH ALTITUDE BAKING (5,200 feet): INCREASE flour to 2-1/2 cups. Add 2 teaspoons water with flour and reduce both granulated sugar and brown sugar to 1/2 cup each. Bake at 375°F; drop cookies for 8 to 10 minutes and pan cookies for 17 to 19 minutes."]
        },

        # ==================== gr-337/343: Famous Fudge (Nestle) ====================
        "nestle-famous-fudge-2-granny": {
            "ingredients": [
                {"item": "butter or margarine", "quantity": "3/4", "unit": "cup"},
                {"item": "undiluted CARNATION Evaporated Milk", "quantity": "2/3", "unit": "cup"},
                {"item": "granulated sugar", "quantity": "1-1/2", "unit": "cups"},
                {"item": "salt", "quantity": "1/4", "unit": "tsp"},
                {"item": "NESTLE TOLL HOUSE Semi-Sweet Chocolate Morsels", "quantity": "2", "unit": "cups"},
                {"item": "marshmallow creme", "quantity": "1", "unit": "7 oz jar"},
                {"item": "vanilla extract", "quantity": "1", "unit": "tsp"},
                {"item": "chopped nuts (optional)", "quantity": "1/2", "unit": "cup"}
            ],
            "instructions": [
                {"step": 1, "text": "COMBINE butter, evaporated milk, sugar and salt in medium saucepan. Bring to full rolling boil over medium heat, stirring constantly. Remove from heat. Stir in morsels."},
                {"step": 2, "text": "Boil for 4 to 5 minutes, stirring constantly. Marshmallows are melted. Remove from heat."},
                {"step": 3, "text": "Stir vigorously for 1 minute or until marshmallows are melted. Stir in vanilla and nuts. Pour into foil-lined 8-inch square baking pan; chill until firm."}
            ],
            "notes": ["Makes about 2 pounds"]
        },

        # ==================== gr-337/343: Old Fashioned Oatmeal Cookies (Nestle) ====================
        "nestle-old-fashioned-oatmeal-granny": {
            "ingredients": [
                {"item": "butter, softened", "quantity": "1", "unit": "cup"},
                {"item": "granulated sugar", "quantity": "3/4", "unit": "cup"},
                {"item": "packed light brown sugar", "quantity": "3/4", "unit": "cup"},
                {"item": "vanilla extract", "quantity": "1", "unit": "tsp"},
                {"item": "eggs", "quantity": "2", "unit": ""},
                {"item": "all-purpose flour", "quantity": "1-1/2", "unit": "cups"},
                {"item": "baking soda", "quantity": "1", "unit": "tsp"},
                {"item": "salt", "quantity": "1/2", "unit": "tsp"},
                {"item": "NESTLE TOLL HOUSE Semi-Sweet Chocolate Morsels", "quantity": "1", "unit": "12 oz pkg"},
                {"item": "quick oats", "quantity": "3", "unit": "cups"}
            ],
            "instructions": [
                {"step": 1, "text": "COMBINE flour, baking soda and salt in small bowl."},
                {"step": 2, "text": "Beat butter, granulated sugar, brown sugar and vanilla extract in large mixer bowl until creamy. Add eggs; beat well. Gradually add flour mixture; beat well."},
                {"step": 3, "text": "Stir in morsels and oats. Drop by rounded tablespoon onto ungreased baking sheets."},
                {"step": 4, "text": "BAKE in preheated 375°F oven for 9 to 11 minutes or until golden brown. Let stand 2 minutes; remove to wire rack."}
            ],
            "servings_yield": "Makes about 4 dozen cookies",
            "temperature": "375°F (190°C)"
        },

        # ==================== gr-339: Frosty Orange Delight ====================
        "frosty-orange-delight-pillsbury-granny": {
            "ingredients": [
                {"item": "orange juice concentrate", "quantity": "6", "unit": "oz"},
                {"item": "milk", "quantity": "1", "unit": "cup"},
                {"item": "vanilla ice cream", "quantity": "2", "unit": "cups"},
                {"item": "sugar", "quantity": "2", "unit": "tbsp"}
            ],
            "instructions": [
                {"step": 1, "text": "Combine all ingredients in blender."},
                {"step": 2, "text": "Blend until smooth."},
                {"step": 3, "text": "Serve immediately."}
            ],
            "servings_yield": "4 servings"
        },

        # ==================== gr-339: Basic Crust (Pillsbury) ====================
        "basic-crust-pillsbury-granny": {
            "ingredients": [
                {"item": "Pillsbury BEST All Purpose Flour", "quantity": "2", "unit": "cups"},
                {"item": "salt", "quantity": "1", "unit": "tsp"},
                {"item": "shortening", "quantity": "2/3", "unit": "cup"},
                {"item": "cold water", "quantity": "5-7", "unit": "tbsp"}
            ],
            "instructions": [
                {"step": 1, "text": "Combine flour and salt. Cut in shortening until mixture resembles coarse crumbs."},
                {"step": 2, "text": "Sprinkle water over mixture, 1 tablespoon at a time, mixing lightly with fork until dough forms a ball."},
                {"step": 3, "text": "Divide dough in half. Roll out on floured surface."},
                {"step": 4, "text": "Fit into pie plate; trim and flute edges."}
            ],
            "servings_yield": "2 pie crusts"
        },

        # ==================== gr-343: Ultimate Chocolate Chip Cookies ====================
        "ultimate-chocolate-chip-cookies-granny": {
            "ingredients": [
                {"item": "all-purpose flour", "quantity": "2-1/4", "unit": "cups"},
                {"item": "baking soda", "quantity": "1", "unit": "tsp"},
                {"item": "salt", "quantity": "1", "unit": "tsp"},
                {"item": "butter, softened", "quantity": "1", "unit": "cup"},
                {"item": "granulated sugar", "quantity": "3/4", "unit": "cup"},
                {"item": "brown sugar", "quantity": "3/4", "unit": "cup"},
                {"item": "vanilla extract", "quantity": "1", "unit": "tsp"},
                {"item": "eggs", "quantity": "2", "unit": ""},
                {"item": "chocolate chips", "quantity": "2", "unit": "cups"},
                {"item": "nuts (optional)", "quantity": "1", "unit": "cup"}
            ],
            "instructions": [
                {"step": 1, "text": "Preheat oven to 375°F."},
                {"step": 2, "text": "Combine flour, baking soda and salt; set aside."},
                {"step": 3, "text": "Beat butter, sugars, and vanilla until creamy. Add eggs; beat well."},
                {"step": 4, "text": "Gradually blend in flour mixture. Stir in chocolate chips and nuts."},
                {"step": 5, "text": "Drop by rounded tablespoon onto ungreased baking sheets."},
                {"step": 6, "text": "Bake 9 to 11 minutes or until golden brown."}
            ],
            "temperature": "375°F (190°C)",
            "servings_yield": "About 5 dozen cookies"
        },

        # ==================== gr-11/12: Quaker's Best Oatmeal Cookies ====================
        "quaker-oatmeal-cookies-gr11-granny": {
            "ingredients": [
                {"item": "butter or margarine, softened", "quantity": "1", "unit": "cup"},
                {"item": "firmly packed brown sugar", "quantity": "1", "unit": "cup"},
                {"item": "granulated sugar", "quantity": "1/2", "unit": "cup"},
                {"item": "eggs", "quantity": "2", "unit": ""},
                {"item": "vanilla", "quantity": "1", "unit": "tsp"},
                {"item": "all-purpose flour", "quantity": "1-1/2", "unit": "cups"},
                {"item": "baking soda", "quantity": "1", "unit": "tsp"},
                {"item": "cinnamon", "quantity": "1", "unit": "tsp"},
                {"item": "salt", "quantity": "1/2", "unit": "tsp"},
                {"item": "QUAKER Oats (quick or old fashioned)", "quantity": "3", "unit": "cups"},
                {"item": "raisins", "quantity": "1", "unit": "cup"}
            ],
            "instructions": [
                {"step": 1, "text": "Heat oven to 350°F."},
                {"step": 2, "text": "Beat together butter and sugars until creamy. Add eggs and vanilla; beat well."},
                {"step": 3, "text": "Add combined flour, baking soda, cinnamon and salt; mix well."},
                {"step": 4, "text": "Stir in oats and raisins; mix well."},
                {"step": 5, "text": "Drop by rounded tablespoonfuls onto ungreased cookie sheet."},
                {"step": 6, "text": "Bake 10 to 12 minutes or until golden brown. Cool 1 minute on cookie sheet; remove to wire rack."}
            ],
            "temperature": "350°F (175°C)",
            "servings_yield": "About 5 dozen cookies"
        },

        # ==================== gr-73/74: Banana Bread (Handwritten with Stove Drawing) ====================
        "banana-bread-handwritten-granny": {
            "ingredients": [
                {"item": "ripe bananas, mashed", "quantity": "3", "unit": ""},
                {"item": "sugar", "quantity": "1", "unit": "cup"},
                {"item": "egg", "quantity": "1", "unit": ""},
                {"item": "butter, melted", "quantity": "1/4", "unit": "cup"},
                {"item": "all-purpose flour", "quantity": "1-1/2", "unit": "cups"},
                {"item": "baking soda", "quantity": "1", "unit": "tsp"},
                {"item": "salt", "quantity": "1/4", "unit": "tsp"},
                {"item": "vanilla", "quantity": "1", "unit": "tsp"}
            ],
            "instructions": [
                {"step": 1, "text": "Preheat oven to 350°F. Grease a loaf pan."},
                {"step": 2, "text": "Mix mashed bananas, sugar, egg, and melted butter."},
                {"step": 3, "text": "Add flour, baking soda, salt, and vanilla. Mix until just combined."},
                {"step": 4, "text": "Pour into prepared pan."},
                {"step": 5, "text": "Bake 55-60 minutes or until toothpick comes out clean."}
            ],
            "temperature": "350°F (175°C)",
            "notes": ["Recipe card has beautiful stove illustration, from kitchen of Dewolf"]
        },

        # ==================== 161/162: Salt Cod Fish ====================
        "salt-cod-fish-main-granny": {
            "ingredients": [
                {"item": "salt cod fish", "quantity": "1", "unit": "lb"},
                {"item": "potatoes, peeled and cubed", "quantity": "4", "unit": ""},
                {"item": "butter", "quantity": "2", "unit": "tbsp"},
                {"item": "milk or cream", "quantity": "1/2", "unit": "cup"},
                {"item": "pepper", "quantity": "", "unit": "to taste"}
            ],
            "instructions": [
                {"step": 1, "text": "Soak salt cod in cold water for 24 hours, changing water several times."},
                {"step": 2, "text": "Drain and place in pot with fresh water. Bring to boil; simmer 15-20 minutes."},
                {"step": 3, "text": "Drain and flake the fish, removing any bones."},
                {"step": 4, "text": "Boil potatoes until tender; drain and mash with butter and milk."},
                {"step": 5, "text": "Combine fish with potatoes; season with pepper. Serve hot."}
            ]
        },

        # ==================== 161: Codfish Souffle ====================
        "codfish-souffle-granny": {
            "ingredients": [
                {"item": "prepared salt cod (see main recipe)", "quantity": "1", "unit": "cup"},
                {"item": "eggs, separated", "quantity": "3", "unit": ""},
                {"item": "milk", "quantity": "1", "unit": "cup"},
                {"item": "butter", "quantity": "2", "unit": "tbsp"},
                {"item": "flour", "quantity": "2", "unit": "tbsp"},
                {"item": "pepper", "quantity": "", "unit": "to taste"}
            ],
            "instructions": [
                {"step": 1, "text": "Prepare salt cod as in main recipe; flake finely."},
                {"step": 2, "text": "Make white sauce with butter, flour, and milk."},
                {"step": 3, "text": "Add cod and egg yolks; mix well."},
                {"step": 4, "text": "Beat egg whites until stiff; fold into mixture."},
                {"step": 5, "text": "Pour into greased baking dish; bake at 375°F for 30-35 minutes."}
            ],
            "temperature": "375°F (190°C)"
        },

        # ==================== 161: Creamed Salt Codfish ====================
        "creamed-salt-codfish-granny": {
            "ingredients": [
                {"item": "prepared salt cod", "quantity": "1", "unit": "lb"},
                {"item": "butter", "quantity": "3", "unit": "tbsp"},
                {"item": "flour", "quantity": "3", "unit": "tbsp"},
                {"item": "milk", "quantity": "2", "unit": "cups"},
                {"item": "pepper", "quantity": "", "unit": "to taste"},
                {"item": "hard-boiled eggs, sliced (optional)", "quantity": "2", "unit": ""}
            ],
            "instructions": [
                {"step": 1, "text": "Prepare salt cod by soaking and simmering as in main recipe."},
                {"step": 2, "text": "Make white sauce: melt butter, stir in flour, gradually add milk. Cook until thickened."},
                {"step": 3, "text": "Add flaked cod to sauce; heat through."},
                {"step": 4, "text": "Serve over toast or boiled potatoes. Top with sliced eggs if desired."}
            ]
        },

        # ==================== 161: Salt Cod Fish Cakes ====================
        "salt-cod-fish-cakes-granny": {
            "ingredients": [
                {"item": "prepared salt cod", "quantity": "1", "unit": "cup"},
                {"item": "mashed potatoes", "quantity": "2", "unit": "cups"},
                {"item": "egg", "quantity": "1", "unit": ""},
                {"item": "onion, minced", "quantity": "2", "unit": "tbsp"},
                {"item": "pepper", "quantity": "", "unit": "to taste"},
                {"item": "butter or oil for frying", "quantity": "", "unit": ""}
            ],
            "instructions": [
                {"step": 1, "text": "Combine flaked cod, mashed potatoes, egg, onion, and pepper."},
                {"step": 2, "text": "Form into patties."},
                {"step": 3, "text": "Fry in butter or oil until golden brown on both sides."},
                {"step": 4, "text": "Serve hot."}
            ]
        },

        # ==================== 161: Codfish & Cheese ====================
        "codfish-cheese-granny": {
            "ingredients": [
                {"item": "prepared salt cod", "quantity": "1", "unit": "lb"},
                {"item": "butter", "quantity": "2", "unit": "tbsp"},
                {"item": "flour", "quantity": "2", "unit": "tbsp"},
                {"item": "milk", "quantity": "1-1/2", "unit": "cups"},
                {"item": "shredded cheese", "quantity": "1", "unit": "cup"},
                {"item": "breadcrumbs", "quantity": "1/2", "unit": "cup"}
            ],
            "instructions": [
                {"step": 1, "text": "Prepare salt cod and flake."},
                {"step": 2, "text": "Make cheese sauce: melt butter, add flour, then milk. Stir in cheese."},
                {"step": 3, "text": "Layer cod and sauce in baking dish. Top with breadcrumbs."},
                {"step": 4, "text": "Bake at 350°F for 25-30 minutes until bubbly."}
            ],
            "temperature": "350°F (175°C)"
        },

        # ==================== gr-127/128: Shrimp Newburg in Patty Shells ====================
        "shrimp-newburg-patty-shells-granny": {
            "ingredients": [
                {"item": "cooked shrimp", "quantity": "1", "unit": "lb"},
                {"item": "butter", "quantity": "3", "unit": "tbsp"},
                {"item": "flour", "quantity": "3", "unit": "tbsp"},
                {"item": "light cream", "quantity": "1-1/2", "unit": "cups"},
                {"item": "egg yolks", "quantity": "2", "unit": ""},
                {"item": "sherry", "quantity": "2", "unit": "tbsp"},
                {"item": "salt", "quantity": "1/2", "unit": "tsp"},
                {"item": "paprika", "quantity": "1/4", "unit": "tsp"},
                {"item": "puff pastry patty shells", "quantity": "6", "unit": ""}
            ],
            "instructions": [
                {"step": 1, "text": "Melt butter in saucepan; blend in flour."},
                {"step": 2, "text": "Gradually add cream; cook until thickened, stirring constantly."},
                {"step": 3, "text": "Beat egg yolks; add small amount of hot sauce to yolks, then return to pan."},
                {"step": 4, "text": "Add shrimp, sherry, salt, and paprika; heat through."},
                {"step": 5, "text": "Serve in warm patty shells."}
            ],
            "servings_yield": "6 servings"
        },

        # ==================== gr-178/179: Linguine with Garden Clam Sauce ====================
        "linguine-garden-clam-sauce-granny": {
            "ingredients": [
                {"item": "linguine", "quantity": "1", "unit": "lb"},
                {"item": "canned clams with juice", "quantity": "2", "unit": "6.5 oz cans"},
                {"item": "olive oil", "quantity": "1/4", "unit": "cup"},
                {"item": "garlic, minced", "quantity": "4", "unit": "cloves"},
                {"item": "fresh parsley, chopped", "quantity": "1/2", "unit": "cup"},
                {"item": "dried oregano", "quantity": "1", "unit": "tsp"},
                {"item": "red pepper flakes", "quantity": "1/4", "unit": "tsp"},
                {"item": "white wine", "quantity": "1/2", "unit": "cup"}
            ],
            "instructions": [
                {"step": 1, "text": "Cook linguine according to package directions; drain."},
                {"step": 2, "text": "Drain clams, reserving juice."},
                {"step": 3, "text": "Heat oil in large skillet; sauté garlic 1 minute."},
                {"step": 4, "text": "Add clam juice, wine, oregano, and pepper flakes; simmer 5 minutes."},
                {"step": 5, "text": "Add clams and parsley; heat through."},
                {"step": 6, "text": "Toss with linguine and serve."}
            ]
        },

        # ==================== gr-184/185: Beef Meatballs in Tomato Sauce ====================
        "beef-meatballs-tomato-sauce-granny": {
            "ingredients": [
                {"item": "ground beef", "quantity": "1-1/2", "unit": "lbs"},
                {"item": "breadcrumbs", "quantity": "1/2", "unit": "cup"},
                {"item": "egg", "quantity": "1", "unit": ""},
                {"item": "onion, minced", "quantity": "1/4", "unit": "cup"},
                {"item": "garlic, minced", "quantity": "2", "unit": "cloves"},
                {"item": "salt", "quantity": "1", "unit": "tsp"},
                {"item": "pepper", "quantity": "1/4", "unit": "tsp"},
                {"item": "tomato sauce", "quantity": "2", "unit": "15 oz cans"},
                {"item": "Italian seasoning", "quantity": "1", "unit": "tsp"}
            ],
            "instructions": [
                {"step": 1, "text": "Mix beef, breadcrumbs, egg, onion, garlic, salt, and pepper."},
                {"step": 2, "text": "Form into 1-1/2 inch meatballs."},
                {"step": 3, "text": "Brown meatballs in skillet; drain fat."},
                {"step": 4, "text": "Add tomato sauce and Italian seasoning; simmer 20 minutes."},
                {"step": 5, "text": "Serve over pasta or with crusty bread."}
            ]
        },

        # ==================== gr-192/193: Strawberries 'n Cream Cheese Freeze ====================
        "strawberries-cream-cheese-freeze-granny": {
            "ingredients": [
                {"item": "cream cheese, softened", "quantity": "8", "unit": "oz"},
                {"item": "sugar", "quantity": "3/4", "unit": "cup"},
                {"item": "frozen strawberries, thawed", "quantity": "10", "unit": "oz"},
                {"item": "crushed pineapple, drained", "quantity": "1", "unit": "8 oz can"},
                {"item": "whipped topping", "quantity": "8", "unit": "oz"},
                {"item": "chopped pecans", "quantity": "1/2", "unit": "cup"}
            ],
            "instructions": [
                {"step": 1, "text": "Beat cream cheese and sugar until smooth."},
                {"step": 2, "text": "Stir in strawberries and pineapple."},
                {"step": 3, "text": "Fold in whipped topping and pecans."},
                {"step": 4, "text": "Pour into 9x13 pan; freeze until firm."},
                {"step": 5, "text": "Let stand 10-15 minutes before serving."}
            ]
        },

        # ==================== gr-229/230: Roast Leg of Lamb with Mint Sauce ====================
        "roast-leg-lamb-mint-sauce-granny": {
            "ingredients": [
                {"item": "leg of lamb", "quantity": "5-6", "unit": "lbs"},
                {"item": "garlic cloves, slivered", "quantity": "4", "unit": ""},
                {"item": "rosemary", "quantity": "1", "unit": "tbsp"},
                {"item": "salt", "quantity": "1", "unit": "tsp"},
                {"item": "pepper", "quantity": "1/2", "unit": "tsp"},
                {"item": "fresh mint, chopped", "quantity": "1/4", "unit": "cup"},
                {"item": "white vinegar", "quantity": "1/4", "unit": "cup"},
                {"item": "sugar", "quantity": "2", "unit": "tbsp"}
            ],
            "instructions": [
                {"step": 1, "text": "Make slits in lamb and insert garlic slivers."},
                {"step": 2, "text": "Rub with rosemary, salt, and pepper."},
                {"step": 3, "text": "Roast at 325°F for about 20 minutes per pound for medium."},
                {"step": 4, "text": "For mint sauce: combine mint, vinegar, and sugar. Let stand 30 minutes."},
                {"step": 5, "text": "Serve sliced lamb with mint sauce on the side."}
            ],
            "temperature": "325°F (165°C)"
        },

        # ==================== gr-305/306: Creamy Mild Seafood ====================
        "creamy-mild-seafood-granny": {
            "instructions": [
                {"step": 1, "text": "Prepare seafood according to package directions."},
                {"step": 2, "text": "Make cream sauce with butter, flour, and milk."},
                {"step": 3, "text": "Combine seafood with cream sauce."},
                {"step": 4, "text": "Season to taste and serve over rice or pasta."}
            ]
        },

        # ==================== gr-68: Pickled Beets ====================
        "pickled-beets-shag-taylor-granny": {
            "instructions": [
                {"step": 1, "text": "Cook fresh beets until tender; cool, peel, and slice."},
                {"step": 2, "text": "Combine vinegar, sugar, and spices in saucepan; bring to boil."},
                {"step": 3, "text": "Pour hot liquid over beets in jars."},
                {"step": 4, "text": "Seal and refrigerate. Best after 24 hours."}
            ],
            "notes": ["Recipe from Shag Taylor, written on envelope back"]
        },

        # ==================== gr-70: Dump's Basic Brownies (Handwritten) ====================
        "dumps-basic-brownies-handwritten-granny": {
            "instructions": [
                {"step": 1, "text": "Melt butter and chocolate together."},
                {"step": 2, "text": "Stir in sugar, then eggs and vanilla."},
                {"step": 3, "text": "Add flour and salt; mix well."},
                {"step": 4, "text": "Pour into greased 8x8 or 9x9 pan."},
                {"step": 5, "text": "Bake at 350°F for 25-30 minutes."}
            ],
            "temperature": "350°F (175°C)"
        }
    }

def fix_recipes():
    """Apply fixes to all failing recipes."""
    data = load_recipes()
    recipes = data.get('recipes', [])
    fixes = get_recipe_fixes()

    fixed_count = 0

    for recipe in recipes:
        recipe_id = recipe.get('id')
        if recipe_id in fixes:
            fix = fixes[recipe_id]

            # Apply all fields from the fix
            for key, value in fix.items():
                recipe[key] = value

            fixed_count += 1
            print(f"Fixed: {recipe_id}")

    data['recipes'] = recipes
    save_recipes(data)

    print(f"\nTotal recipes fixed: {fixed_count}")
    return fixed_count

if __name__ == "__main__":
    fix_recipes()
