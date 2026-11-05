
import json

from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    ConfigDict,
    field_validator
)


# ---------------------------------------
# 1. AI Request Schema
# ---------------------------------------

class AIRequest(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
        strict=True
    )

    prompt: str = Field(
        min_length=10,
        max_length=2000
    )

    model: Literal[
        "gpt",
        "gemini",
        "claude"
    ]

    temperature: float = Field(
        ge=0,
        le=2
    )

    max_tokens: int = Field(
        ge=1,
        le=4096
    )

    # Custom prompt validation
    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Prompt cannot be empty."
            )

        if len(value) < 10:
            raise ValueError(
                "Prompt must contain at least 10 characters."
            )

        return value


# ---------------------------------------
# 2. Sample User Requests
# ---------------------------------------

valid_request = {
    "prompt": "Explain Generative AI with examples",
    "model": "gpt",
    "temperature": 0.7,
    "max_tokens": 1000
}


invalid_request = {
    "prompt": "Hi",
    "model": "unknown",
    "temperature": 3.5,
    "max_tokens": -100
}


# ---------------------------------------
# 3. Request Processing Function
# ---------------------------------------

def process_request(data: dict):

    try:

        validated = AIRequest.model_validate(data)

        print("\nValidation Successful!")

        print("\nValidated Data:")

        print(
            validated.model_dump_json(indent=4)
        )

        return validated

    except ValidationError as error:

        print("\nValidation Failed!")

        for issue in error.errors():

            field = ".".join(
                str(part) for part in issue["loc"]
            )

            print(
                f"Field: {field} | "
                f"Error: {issue['msg']}"
            )

        return None


# ---------------------------------------
# 4. Main Application
# ---------------------------------------

def main():

    print("=== AI REQUEST VALIDATOR ===")

    print("\n--- Testing Valid Request ---")
    process_request(valid_request)

    print("\n--- Testing Invalid Request ---")
    process_request(invalid_request)


if __name__ == "__main__":
    main()
