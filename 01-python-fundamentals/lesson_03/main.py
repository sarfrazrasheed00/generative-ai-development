
import json
import math

from ai_model import AIModel, VisionAIModel
from model_selector import ModelSelector


# Dummy dataset for learning
# These prices are not real API prices.

models = [
    VisionAIModel("GPT", "OpenAI", 5.00),
    VisionAIModel("Gemini", "Google", 2.00),
    VisionAIModel("Claude", "Anthropic", 3.00),
    AIModel("Llama", "Meta", False, 0.50)
]


def get_vision_requirement() -> bool:

    while True:
        user_input = input(
            "Do you need vision support? (yes/no): "
        ).strip().lower()

        if user_input == "yes":
            return True

        if user_input == "no":
            return False

        print("Please enter yes or no.")


def get_budget() -> float:

    while True:
        try:
            budget = float(
                input("Enter maximum budget ($): ")
            )

            if not math.isfinite(budget) or budget < 0:
                print("Enter a valid non-negative budget.")
                continue

            return budget

        except ValueError:
            print("Invalid number. Try again.")


def main():

    print("\n=== OOP AI MODEL SELECTOR ===\n")

    vision_required = get_vision_requirement()
    max_budget = get_budget()

    selector = ModelSelector(models)

    matching_models = selector.filter_models(
        vision_required,
        max_budget
    )

    matching_models = selector.sort_by_cost(
        matching_models
    )

    print(f"\nMatching models: {len(matching_models)}")

    if not matching_models:
        print("No suitable AI model found.")
        return

    print("\nAvailable Models:")

    for index, model in enumerate(matching_models, start=1):
        print(
            f"{index}. {model.name} "
            f"({model.provider}) - "
            f"${model.cost:.2f}"
        )

    recommended = selector.recommend_model(
        vision_required,
        max_budget
    )

    print("\nRecommended Model:")

    print(
        json.dumps(
            recommended.get_details(),
            indent=4
        )
    )

    if isinstance(recommended, VisionAIModel):
        print("\n" + recommended.analyze_image())


if __name__ == "__main__":
    main()
