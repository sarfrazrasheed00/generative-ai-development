
from ai_model import AIModel


class ModelSelector:

    def __init__(self, models: list[AIModel]):
        self.models = models

    def filter_models(
        self,
        vision_required: bool,
        max_budget: float
    ) -> list[AIModel]:

        return [
            model
            for model in self.models
            if (
                (not vision_required or model.supports_vision)
                and model.is_within_budget(max_budget)
            )
        ]

    def sort_by_cost(
        self,
        models: list[AIModel]
    ) -> list[AIModel]:

        return sorted(
            models,
            key=lambda model: model.cost
        )

    def recommend_model(
        self,
        vision_required: bool,
        max_budget: float
    ) -> AIModel | None:

        filtered = self.filter_models(
            vision_required,
            max_budget
        )

        sorted_models = self.sort_by_cost(filtered)

        if not sorted_models:
            return None

        return sorted_models[0]
