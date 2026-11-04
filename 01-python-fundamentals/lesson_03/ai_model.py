

class AIModel:

    def __init__(
        self,
        name: str,
        provider: str,
        supports_vision: bool,
        cost: float
    ):
        self.name = name
        self.provider = provider
        self.supports_vision = supports_vision

        if cost < 0:
            raise ValueError("Cost cannot be negative.")

        self._cost = cost

    @property
    def cost(self) -> float:
        return self._cost

    @cost.setter
    def cost(self, value: float):
        if value < 0:
            raise ValueError("Cost cannot be negative.")

        self._cost = value
        
    def get_details(self) -> dict:
        return {
            "name": self.name,
            "provider": self.provider,
            "supports_vision": self.supports_vision,
            "cost_per_1m_tokens": self.cost
        }

    def is_within_budget(self, max_budget: float) -> bool:
        return self.cost <= max_budget


# Inheritance example
class VisionAIModel(AIModel):

    def __init__(
        self,
        name: str,
        provider: str,
        cost: float
    ):
        super().__init__(
            name=name,
            provider=provider,
            supports_vision=True,
            cost=cost
        )

    def analyze_image(self) -> str:
        return f"{self.name} supports image analysis."
