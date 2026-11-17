
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
# 2. CHATBOT SERVICE
# =====================================================

class GeminiStreamingChatbot:

    def __init__(self, llm):

        print("\n[DEBUG 1] Initializing chatbot")

        self.llm = llm

        self.system_message = SystemMessage(
            content=(
                "You are a helpful Generative AI tutor. "
                "Explain concepts in simple Roman Urdu. "
                "Use previous messages for context."
            )
        )

        self.history = []

        print("[DEBUG] History:", self.history)
        print("[DEBUG] LLM:", type(self.llm))


    # =================================================
    # 3. BUILD MESSAGES
    # =================================================

    def build_messages(self, user_prompt: str):

        messages = [self.system_message]

        messages.extend(self.history)

        messages.append(
            HumanMessage(content=user_prompt)
        )

        print("\n[DEBUG 2] Building messages")
        print("[DEBUG] Message count:", len(messages))

        for index, message in enumerate(messages, 1):
            print(
                f"[DEBUG] {index}. {message.type}: "
                f"{message.content}"
            )

        return messages


    # =================================================
    # 4. STREAM RESPONSE
    # =================================================

    def chat(self, user_prompt: str) -> str:

        print("\n[DEBUG 3] Streaming started")

        messages = self.build_messages(user_prompt)

        full_response = ""

        chunk_count = 0

        first_chunk_time = None

        start_time = time.perf_counter()

        print("\nGemini: ", end="", flush=True)

        # Actual streaming API request
        for chunk in self.llm.stream(messages):

            chunk_count += 1

            # Extract current text chunk
            text = chunk.text

            # Track time to first text
            if text and first_chunk_time is None:
                first_chunk_time = (
                    time.perf_counter() - start_time
                )

            # Display chunk immediately
            print(text, end="", flush=True)

            # Accumulate full response
            full_response += text

        print("\n")

        elapsed = time.perf_counter() - start_time

        print("[DEBUG 4] Streaming completed")
        print("[DEBUG] Total chunks:", chunk_count)

        if first_chunk_time is not None:
            print(
                "[DEBUG] Time to first text:",
                round(first_chunk_time, 2),
                "seconds"
            )

        print(
            "[DEBUG] Total execution time:",
            round(elapsed, 2),
            "seconds"
        )

        print(
            "[DEBUG] Response length:",
            len(full_response)
        )

        # Reject empty output
        if not full_response.strip():
            raise ValueError(
                "Gemini returned an empty response"
            )

        # =============================================
        # 5. SAVE CONVERSATION HISTORY
        # =============================================

        self.history.append(
            HumanMessage(content=user_prompt)
        )

        self.history.append(
            AIMessage(content=full_response)
        )

        print("\n[DEBUG 5] Conversation saved")
        print("[DEBUG] Stored messages:", len(self.history))

        self.trim_history()

        return full_response


    # =================================================
    # 6. TRIM HISTORY
    # =================================================

    def trim_history(self):

        max_messages = MAX_HISTORY_TURNS * 2

        if len(self.history) > max_messages:

            self.history = self.history[-max_messages:]

            print("[DEBUG] Old messages removed")

        print(
            "[DEBUG] History after trim:",
            len(self.history)
        )


    # =================================================
    # 7. SHOW HISTORY
    # =================================================

    def show_history(self):

        print("\n========== HISTORY ==========")

        if not self.history:
            print("No conversation history")
            return

        for index, message in enumerate(self.history, 1):

            print(f"\n{index}. Role: {message.type}")
            print("Content:", message.content)

        print("=============================")


    # =================================================
    # 8. CLEAR HISTORY
    # =================================================

    def clear_history(self):

        self.history.clear()

        print("[DEBUG] Conversation cleared")


# =====================================================
# 9. MAIN APPLICATION
# =====================================================

def main():

    print("\n===================================")
    print(" LESSON 11 - GEMINI STREAMING CHAT")
    print("===================================")

    if not GEMINI_API_KEY:
        print("[ERROR] Gemini API key missing")
        return

    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        api_key=GEMINI_API_KEY,
        max_retries=1,
        timeout=60
    )

    chatbot = GeminiStreamingChatbot(llm)

    print("\nCommands: show | clear | exit")

    while True:

        user_prompt = input("\nYou: ").strip()

        command = user_prompt.lower()

        if command == "exit":
            print("Chatbot closed")
            break

        if command == "show":
            chatbot.show_history()
            continue

        if command == "clear":
            chatbot.clear_history()
            continue

        if not user_prompt:
            print("[ERROR] Empty input")
            continue

        try:

            chatbot.chat(user_prompt)

        except Exception as error:

            print("\n[ERROR TYPE]", type(error).__name__)
            print("[ERROR MESSAGE]", str(error))


# =====================================================
# 10. ENTRY POINT
# =====================================================

if __name__ == "__main__":
    main()
