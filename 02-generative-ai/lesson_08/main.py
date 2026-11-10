
import os
import time

from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage


# ===============================================
# 1. CONFIGURATION
# ===============================================

BASE_DIR = Path(__file__).resolve().parent

# Reuse Lesson 07 environment file
ENV_PATH = BASE_DIR.parent / "lesson_07" / ".env"

load_dotenv(ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

LLM_MODEL = "gemini-3.5-flash-lite"


# ===============================================
# 2. PYDANTIC OUTPUT SCHEMA
# ===============================================

class ContentResponse(BaseModel):

    title: str = Field(
        description="Professional marketing title"
    )

    description: str = Field(
        description="Marketing description of the product"
    )

    benefits: list[str] = Field(
        description="Exactly 3 benefits of the product",
        min_length=3,
        max_length=3
    )

    keywords: list[str] = Field(
        description="Exactly 5 relevant SEO keywords",
        min_length=5,
        max_length=5
    )

    call_to_action: str = Field(
        description="Short marketing call to action"
    )

    tone: Literal[
        "professional",
        "friendly",
        "luxury"
    ] = Field(
        description="Selected marketing tone"
    )


# ===============================================
# 3. INPUT SCHEMA
# ===============================================

class ContentRequest(BaseModel):

    product_name: str = Field(min_length=3)

    target_audience: str = Field(min_length=3)

    tone: Literal[
        "professional",
        "friendly",
        "luxury"
    ] = "professional"

    language: str = Field(min_length=2)


# ===============================================
# 4. GEMINI CONTENT GENERATOR
# ===============================================

class AIContentGenerator:

    def __init__(self, llm):

        print("\n[DEBUG 1] Constructor called")

        self.llm = llm

        print("[DEBUG] LLM injected successfully")
        print("[DEBUG] LLM type:", type(self.llm))

        # Configure structured output once
        self.structured_llm = (
            self.llm.with_structured_output(
                ContentResponse,
                method="json_schema",
                include_raw=True
            )
        )

        print("[DEBUG] Structured LLM created")
        print("[DEBUG] Output schema: ContentResponse")


    # ===========================================
    # 5. PROMPT GENERATION
    # ===========================================

    def build_messages(
        self,
        request: ContentRequest
    ):

        print("\n[DEBUG 2] Building prompts")

        system_prompt = """
You are an expert marketing content writer.

Follow these instructions:
- Write original, clear and engaging content.
- Match the requested audience and tone.
- Use the requested language.
- Include exactly 3 benefits.
- Include exactly 5 SEO keywords.
- Keep the description concise.
- Do not invent product specifications,
  certifications, prices, or guarantees.
- The output tone field must match
  the requested tone.
"""

        user_prompt = f"""
Generate marketing content for this product.

Product: {request.product_name}
Target Audience: {request.target_audience}
Tone: {request.tone}
Language: {request.language}

Create a professional product title,
description, benefits, SEO keywords,
and call to action.
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        print("[DEBUG] Message count:", len(messages))

        for index, message in enumerate(messages, 1):
            print(f"\n[DEBUG] Message {index}")
            print("[DEBUG] Role:", message.type)
            print("[DEBUG] Content:", message.content)

        return messages


    # ===========================================
    # 6. GENERATE STRUCTURED RESPONSE
    # ===========================================

    def generate(
        self,
        request: ContentRequest
    ) -> ContentResponse:

        print("\n[DEBUG 3] generate() called")

        print("[DEBUG] Request object:", request)
        print("[DEBUG] Request type:", type(request))

        messages = self.build_messages(request)

        print("\n[DEBUG 4] Sending request to Gemini")

        start = time.perf_counter()

        result = self.structured_llm.invoke(messages)

        elapsed = time.perf_counter() - start

        print("\n[DEBUG 5] API response received")
        print("[DEBUG] Execution time:", round(elapsed, 2))

        print("[DEBUG] Result type:", type(result))
        print("[DEBUG] Result keys:", list(result.keys()))

        # =======================================
        # 7. RAW RESPONSE
        # =======================================

        raw = result["raw"]

        print("\n[DEBUG 6] RAW RESPONSE")

        print("[DEBUG] Raw type:", type(raw))
        print("[DEBUG] Raw content:", raw.content)
        print("[DEBUG] Response ID:", raw.id)

        print(
            "[DEBUG] Token usage:",
            raw.usage_metadata
        )

        # =======================================
        # 8. PARSED OUTPUT
        # =======================================

        parsed = result["parsed"]

        parsing_error = result["parsing_error"]

        print("\n[DEBUG 7] PARSED RESPONSE")

        print("[DEBUG] Parsed type:", type(parsed))
        print("[DEBUG] Parsing error:", parsing_error)

        if parsing_error is not None:
            raise ValueError(
                f"Parsing failed: {parsing_error}"
            )

        if parsed is None:
            raise ValueError(
                "Gemini returned no structured data"
            )

        print("[DEBUG] Title:", parsed.title)
        print("[DEBUG] Benefits:", parsed.benefits)
        print("[DEBUG] Keywords:", parsed.keywords)

        # =======================================
        # 9. BUSINESS RULE VALIDATION
        # =======================================

        if parsed.tone != request.tone:
            raise ValueError(
                "Generated tone does not match request"
            )

        print("\n[DEBUG 8] Validation successful")

        return parsed


# ===============================================
# 10. MAIN APPLICATION
# ===============================================

def main():

    print("\n====================================")
    print("LESSON 08 - AI CONTENT GENERATOR")
    print("====================================")

    if not GEMINI_API_KEY:
        print("[ERROR] GEMINI_API_KEY is missing")
        return

    try:

        product_name = input(
            "\nProduct name: "
        ).strip()

        target_audience = input(
            "Target audience: "
        ).strip()

        tone = input(
            "Tone (professional/friendly/luxury): "
        ).strip().lower()

        language = input(
            "Language (English/Roman Urdu): "
        ).strip()

        if not tone:
            tone = "professional"

        if not language:
            language = "English"

        # =======================================
        # 11. VALIDATE USER INPUT
        # =======================================

        print("\n[DEBUG] Validating user input")

        request = ContentRequest(
            product_name=product_name,
            target_audience=target_audience,
            tone=tone,
            language=language
        )

        print("[DEBUG] Input validation passed")
        print("[DEBUG] Request:", request.model_dump())

        # =======================================
        # 12. INITIALIZE GEMINI LLM
        # =======================================

        llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            api_key=GEMINI_API_KEY,
            max_retries=1,
            timeout=60
        )

        print("\n[DEBUG] Gemini LLM initialized")

        generator = AIContentGenerator(llm)

        # =======================================
        # 13. GENERATE CONTENT
        # =======================================

        content = generator.generate(request)

        # =======================================
        # 14. JSON OUTPUT
        # =======================================

        json_output = content.model_dump_json(
            indent=4
        )

        print("\n========== FINAL JSON ==========")

        print(json_output)

        # =======================================
        # 15. SAVE JSON FILE
        # =======================================

        output_path = BASE_DIR / "content_output.json"

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(json_output)

        print("\n[DEBUG] JSON file saved:")
        print(output_path)

    except ValidationError as error:

        print("\n[VALIDATION ERROR]")

        for issue in error.errors():
            print(issue["loc"], issue["msg"])

    except Exception as error:

        print("\n[ERROR]", type(error).__name__)
        print("[ERROR MESSAGE]", str(error))


# ===============================================
# 16. ENTRY POINT
# ===============================================

if __name__ == "__main__":
    main()
