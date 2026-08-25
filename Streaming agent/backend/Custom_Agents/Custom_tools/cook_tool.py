from agents import(
    function_tool,
)

@function_tool
def get_recipe(dish: str):
    """
    Return a simple recipe for the given dish name.
    """
    recipes = {
        "pasta": {
            "name": "Simple Garlic Pasta",
            "ingredients": ["pasta", "garlic", "olive oil", "salt", "pepper"],
            "steps": [
                "Boil pasta until al dente.",
                "Sauté chopped garlic in olive oil.",
                "Mix pasta with garlic oil, add salt and pepper, and serve."
            ]
        },
        "omelette": {
            "name": "Basic Omelette",
            "ingredients": ["eggs", "salt", "pepper", "butter"],
            "steps": [
                "Beat eggs with salt and pepper.",
                "Heat butter in a pan.",
                "Pour eggs, cook gently, fold, and serve."
            ]
        }
    }

    dish_lower = dish.lower()
    if dish_lower not in recipes:
        return {
            "error": "Recipe not found",
            "available_recipes": list(recipes.keys())
        }

    return recipes[dish_lower]
