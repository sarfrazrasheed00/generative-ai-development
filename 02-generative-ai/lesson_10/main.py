
import os
import time

from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)


# =====================================================
# 1. CONFIGURATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

ENV_PATH = BASE_DIR.parent / "lesson_07" / ".env"

load_dotenv(ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

LLM_MODEL = "gemini-3.5-flash-lite"

MAX_HISTORY_TURNS = 5


# =====================================================
# 2. GEMINI CHAT SERVICE
# =====================================================

class GeminiChatService:

    def __init__(self, llm):

        print("\n[DEBUG 1] Constructor called")

        # Reuse existing LLM client
        self.llm = llm

        # System message remains at the beginning
        self.system_message = SystemMessage(
            content=(
                "You are a helpful Generative AI tutor. "
                "Explain concepts in simple Roman Urdu. "
                "Provide Python examples when useful. "
                "Use previous conversation messages "
                "to understand follow-up questions."
            )
        )

        # Store completed user/AI conversation turns
        self.history = []

        print("[DEBUG] LLM object:", type(self.llm))
        print("[DEBUG] History initialized:", self.history)
        print("[DEBUG] Max history turns:", MAX_HISTORY_TURNS)


    # =================================================
    # 3. DISPLAY CURRENT HISTORY
    # =================================================

    def show_history(self):

        print("\n========== CHAT HISTORY ==========")

        if not self.history:
            print("[DEBUG] No conversation history")
            return

        print("[DEBUG] Messages stored:", len(self.history))
        print("[DEBUG] Completed turns:", len(self.history) // 2)

        for index, message in enumerate(self.history, 1):

            print(f"\nMessage {index}")
            print("Role:", message.type)
            print("Content:", message.content)

        print("\n==================================")


    # =================================================
    # 4. BUILD API MESSAGES
    # =================================================

    def build_messages(self, user_prompt: str):

        print("\n[DEBUG 2] Building messages")

        # Include system message
        messages = [self.system_message]

        # Include previous conversation history
        messages.extend(self.history)

        # Add current user prompt
        messages.append(
            HumanMessage(content=user_prompt)
        )

        print("[DEBUG] API message count:", len(messages))

        for index, message in enumerate(messages, 1):

            print(f"\n[DEBUG] API Message {index}")
            print("[DEBUG] Role:", message.type)
            print("[DEBUG] Content:", message.content)

        return messages


    # =================================================
    # 5. MANAGE HISTORY SIZE
    # =================================================

    def trim_history(self):

        print("\n[DEBUG 3] Checking history size")

        max_messages = MAX_HISTORY_TURNS * 2

        print("[DEBUG] Current messages:", len(self.history))
        print("[DEBUG] Maximum messages:", max_messages)

        if len(self.history) > max_messages:

            removed_count = (
                len(self.history) - max_messages
            )

            print(
                "[DEBUG] Removing oldest messages:",
                removed_count
            )

            # Keep the latest completed turns
            self.history = self.history[-max_messages:]

        print("[DEBUG] History after trim:", len(self.history))


    # =================================================
    # 6. SEND CHAT MESSAGE
    # =================================================

    def chat(self, user_prompt: str) -> str:

        print("\n[DEBUG 4] chat() called")
        print("[DEBUG] User prompt:", user_prompt)

        # Prepare full conversation messages
        messages = self.build_messages(user_prompt)

        print("\n[DEBUG 5] Sending request to Gemini")

        start_time = time.perf_counter()

        response = self.llm.invoke(messages)

        elapsed = time.perf_counter() - start_time

        print("\n[DEBUG 6] Gemini response received")
        print("[DEBUG] Response type:", type(response))
        print("[DEBUG] Execution time:", round(elapsed, 2))

        # Extract generated text
        generated_text = response.text

        print("[DEBUG] Generated text type:", type(generated_text))
        print("[DEBUG] Generated text length:", len(generated_text))

        if not generated_text.strip():
            raise ValueError("Gemini returned an empty response")

        # =============================================
        # 7. TOKEN USAGE
        # =============================================

        usage = response.usage_metadata or {}

        print("\n[DEBUG 7] Token usage")
        print("[DEBUG] Input tokens:", usage.get("input_tokens"))
        print("[DEBUG] Output tokens:", usage.get("output_tokens"))
        print("[DEBUG] Total tokens:", usage.get("total_tokens"))

        # =============================================
        # 8. SAVE COMPLETED CONVERSATION TURN
        # =============================================

        print("\n[DEBUG 8] Saving conversation history")

        self.history.append(
            HumanMessage(content=user_prompt)
        )

        self.history.append(
            AIMessage(content=generated_text)
        )

        print("[DEBUG] History messages:", len(self.history))
        print("[DEBUG] Completed turns:", len(self.history) // 2)

        # Trim older conversation turns
        self.trim_history()

        return generated_text


    # =================================================
    # 9. CLEAR HISTORY
    # =================================================

    def clear_history(self):

        self.history.clear()

        print("\n[DEBUG] Conversation history cleared")


# =====================================================
# 10. MAIN APPLICATION
# =====================================================

def main():

    print("\n===================================")
    print(" LESSON 10 - GEMINI MEMORY CHATBOT")
    print("===================================")

    if not GEMINI_API_KEY:
        print("[ERROR] GEMINI_API_KEY missing")
        return

    # Initialize LLM once
    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        api_key=GEMINI_API_KEY,
        max_retries=1,
        timeout=60
    )

    # Dependency injection
    chatbot = GeminiChatService(llm)

    print("\nAvailable commands:")
    print("show  - Display conversation history")
    print("clear - Reset conversation")
    print("exit  - Close chatbot")

    # Continuous conversation loop
    while True:

        user_prompt = input(
            "\nYou: "
        ).strip()

        command = user_prompt.lower()

        if command == "exit":
            print("\nChatbot closed")
            break

        if command == "show":
            chatbot.show_history()
            continue

        if command == "clear":
            chatbot.clear_history()
            continue

        if not user_prompt:
            print("[ERROR] Message cannot be empty")
            continue

        try:

            # Actual Gemini API call
            response = chatbot.chat(user_prompt)

            print("\n========== GEMINI RESPONSE ==========")
            print(response)
            print("=====================================")

        except Exception as error:

            print("\n[ERROR TYPE]", type(error).__name__)
            print("[ERROR MESSAGE]", str(error))


# =====================================================
# 11. ENTRY POINT
# =====================================================

if __name__ == "__main__":
    main()
