
import os
import time

from pathlib import Path
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)


# =====================================================
# 1. CONFIGURATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

LLM_MODEL = "gemini-3.5-flash-lite"


# =====================================================
# 2. GEMINI AI SERVICE
# =====================================================

class GeminiAIService:

    def __init__(self):

        print("\n[DEBUG 1] Constructor called")

        print("[DEBUG] Model:", LLM_MODEL)

        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not found in .env"
            )

        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            api_key=GEMINI_API_KEY,
            max_retries=1,
            timeout=30
        )

        print("[DEBUG] Gemini API Key loaded: Yes")
        print("[DEBUG] LLM initialized successfully")
        print("[DEBUG] LLM object type:", type(self.llm))


    # =================================================
    # 3. GENERATE AI RESPONSE
    # =================================================

    def generate_response(self, user_prompt: str):

        print("\n[DEBUG 2] generate_response() called")

        print("[DEBUG] self:", self)
        print("[DEBUG] User prompt:", user_prompt)

        # System instructions
        system_prompt = (
            "You are an expert Python and Generative AI tutor. "
            "Explain concepts in simple Roman Urdu. "
            "Provide practical examples with explanations."
        )

        # Create messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        print("\n[DEBUG 3] Messages created")

        print("[DEBUG] Messages type:", type(messages))
        print("[DEBUG] Total messages:", len(messages))

        for index, message in enumerate(messages, start=1):

            print(f"\n[DEBUG] Message {index}")

            print("Type:", type(message))
            print("Content:", message.content)

        # =============================================
        # 4. SEND REQUEST
        # =============================================

        print("\n[DEBUG 4] Sending request to Gemini...")

        start_time = time.perf_counter()

        response = self.llm.invoke(messages)

        elapsed_time = time.perf_counter() - start_time

        print("\n[DEBUG 5] Gemini response received")

        print("[DEBUG] Response type:", type(response))
        print("[DEBUG] Execution time:", round(elapsed_time, 2))

        # =============================================
        # 5. EXTRACT GENERATED TEXT
        # =============================================

        print("\n[DEBUG 6] Extracting AI response")

        generated_text = response.text

        print("[DEBUG] Generated text type:", type(generated_text))
        print("[DEBUG] Generated text length:", len(generated_text))

        # =============================================
        # 6. TOKEN USAGE
        # =============================================

        print("\n[DEBUG 7] Token usage")

        usage = response.usage_metadata or {}

        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)

        print("[DEBUG] Input tokens:", input_tokens)
        print("[DEBUG] Output tokens:", output_tokens)
        print("[DEBUG] Total tokens:", total_tokens)

        # =============================================
        # 7. RESPONSE METADATA
        # =============================================

        print("\n[DEBUG 8] Response metadata")

        print("[DEBUG] Response ID:", response.id)

        print(
            "[DEBUG] Response metadata:",
            response.response_metadata
        )

        return generated_text


# =====================================================
# 8. MAIN APPLICATION
# =====================================================

def main():

    print("\n======================================")
    print(" LESSON 07 - FIRST GEMINI AI APPLICATION")
    print("======================================")

    user_prompt = input(
        "\nEnter your question for AI: "
    ).strip()

    if not user_prompt:
        print("Prompt cannot be empty.")
        return

    try:

        print("\n[DEBUG] Creating GeminiAIService object...")

        ai_service = GeminiAIService()

        print("\n[DEBUG] Calling generate_response()")

        result = ai_service.generate_response(
            user_prompt
        )

        print("\n======================================")
        print("             AI RESPONSE")
        print("======================================\n")

        print(result)

        print("\n======================================")
        print("                 END")
        print("======================================")

    except Exception as error:

        print("\n[ERROR] Something went wrong!")

        print("[ERROR] Type:", type(error).__name__)
        print("[ERROR] Message:", str(error))


# =====================================================
# 9. ENTRY POINT
# =====================================================

if __name__ == "__main__":
    main()
