
import json


# ---------------------------------------
# 1. AI Models Dataset
# ---------------------------------------

ai_models = [
    {
        "name": "GPT",
        "provider": "OpenAI",
        "supports_vision": True,
        "cost_per_1m_tokens": 5.00
    },
    {
        "name": "Gemini",
        "provider": "Google",
        "supports_vision": True,
        "cost_per_1m_tokens": 2.00
    },
    {
        "name": "Claude",
        "provider": "Anthropic",
        "supports_vision": True,
        "cost_per_1m_tokens": 3.00
    },
    {
        "name": "Llama",
        "provider": "Meta",
        "supports_vision": False,
        "cost_per_1m_tokens": 0.50
    }
]


# ---------------------------------------
# 2. Filter Models
# ---------------------------------------

def filter_models(
    models: list[dict],
    vision_required: bool,
    max_budget: float
) -> list[dict]:

    return [
        model
        for model in models
        if (
            (not vision_required or model["supports_vision"])
            and model["cost_per_1m_tokens"] <= max_budget
        )
    ]


# ---------------------------------------
# 3. Sort Models By Cost
# ---------------------------------------

def sort_by_cost(models: list[dict]) -> list[dict]:

    return sorted(
        models,
        key=lambda model: model["cost_per_1m_tokens"]
    )


# ---------------------------------------
# 4. Recommend Best Model
# ---------------------------------------

def recommend_model(
    models: list[dict],
    vision_required: bool,
    max_budget: float
) -> dict | None:

    filtered_models = filter_models(
        models,
        vision_required,
        max_budget
    )

    sorted_models = sort_by_cost(filtered_models)

    if not sorted_models:
        return None

    return sorted_models[0]


# ---------------------------------------
# 5. Main Application
# ---------------------------------------

def main():

    print("\n=== AI MODEL SELECTOR ===")

    # Ask user for vision requirement
    while True:
        vision_input = input(
            "\nDo you need vision support? (yes/no): "
        ).strip().lower()

        if vision_input in ["yes", "no"]:
            break

        print("Invalid input. Please enter yes or no.")

    vision_required = vision_input == "yes"

    # Ask user for maximum budget
    while True:
        try:
            max_budget = float(
                input("Enter maximum budget per 1M tokens ($): ")
            )

            if not 0 <= max_budget < float("inf"):
                print("Please enter a finite, non-negative budget.")
                continue

            break

        except ValueError:
            print("Invalid budget. Please enter a number.")

    # Filter models
    matching_models = filter_models(
        ai_models,
        vision_required,
        max_budget
    )

    # Sort matching models
    matching_models = sort_by_cost(matching_models)

    # Display number of matching models
    print("\nTotal matching models:", len(matching_models))

    if not matching_models:
        print("No AI models match your requirements.")
        return

    # Display all matching models
    print("\nAvailable Models:")

    for index, model in enumerate(matching_models, start=1):
        print(
            f"{index}. {model['name']} "
            f"({model['provider']}) - "
            f"${model['cost_per_1m_tokens']:.2f}"
        )

    # Recommend cheapest matching model
    recommended = recommend_model(
        ai_models,
        vision_required,
        max_budget
    )

    print("\nRecommended Model:")

    print(
        json.dumps(
            recommended,
            indent=4
        )
    )


# ---------------------------------------
# 6. Entry Point
# ---------------------------------------

if __name__ == "__main__":
    main()
