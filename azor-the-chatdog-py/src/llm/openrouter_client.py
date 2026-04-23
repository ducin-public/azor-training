"""
OpenRouter LLM Client Implementation

OpenRouter exposes an OpenAI-compatible API, so we reuse the openai SDK
and point it at https://openrouter.ai/api/v1.
"""

import os
import sys
from typing import Optional, List, Any, Dict
from openai import OpenAI
from dotenv import load_dotenv
from cli import console
from .openrouter_validation import OpenRouterConfig

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterResponse:
    """Response object with a .text attribute containing the response text."""

    def __init__(self, text: str):
        self.text = text


class OpenRouterChatSession:
    """
    Chat session wrapper for OpenRouter.
    Manages conversation history and maps the universal format to the OpenAI-compatible API.
    """

    def __init__(
        self,
        openrouter_client: OpenAI,
        model_name: str,
        system_instruction: str,
        history: Optional[List[Dict]] = None,
    ):
        self.openrouter_client = openrouter_client
        self.model_name = model_name
        self.system_instruction = system_instruction
        self._history = history or []

    def send_message(self, text: str) -> Any:
        """
        Sends a message to the OpenRouter model and returns a response object.

        Args:
            text: User's message

        Returns:
            OpenRouterResponse with .text attribute
        """
        self._history.append({"role": "user", "parts": [{"text": text}]})

        openai_messages = self._convert_to_openai_format()

        try:
            completion = self.openrouter_client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                max_tokens=4096,
            )

            response_text = completion.choices[0].message.content.strip()

            self._history.append({"role": "model", "parts": [{"text": response_text}]})

            return OpenRouterResponse(response_text)

        except Exception as e:
            console.print_error(f"Error while generating OpenRouter response: {e}")
            error_text = "Sorry, an error occurred while generating a response."
            self._history.append({"role": "model", "parts": [{"text": error_text}]})
            return OpenRouterResponse(error_text)

    def get_history(self) -> List[Dict]:
        """Returns the current conversation history in universal format."""
        return self._history

    def _convert_to_openai_format(self) -> List[Dict[str, str]]:
        """Converts universal history format to OpenAI message format."""
        openai_messages = []

        if self.system_instruction:
            openai_messages.append({"role": "system", "content": self.system_instruction})

        for message in self._history:
            role = message["role"]
            text = message["parts"][0]["text"] if message["parts"] else ""
            openai_role = "assistant" if role == "model" else "user"
            openai_messages.append({"role": openai_role, "content": text})

        return openai_messages


class OpenRouterClient:
    """
    OpenRouter LLM Client.
    Provides the same interface as other LLM clients in this codebase.
    """

    def __init__(self, model_name: str, api_key: str):
        if not api_key:
            raise ValueError("API key cannot be empty or None")

        self.model_name = model_name
        self.api_key = api_key
        self._client = self._initialize_client()

    @staticmethod
    def preparing_for_use_message() -> str:
        return "🤖 Preparing OpenRouter client..."

    @classmethod
    def from_environment(cls) -> 'OpenRouterClient':
        load_dotenv()

        config = OpenRouterConfig(
            model_name=os.getenv('OPENROUTER_MODEL_NAME') or os.getenv('MODEL_NAME', 'qwen/qwen3.5-9b'),
            openrouter_api_key=os.getenv('OPENROUTER_API_KEY', ''),
        )

        return cls(model_name=config.model_name, api_key=config.openrouter_api_key)

    def _initialize_client(self) -> OpenAI:
        try:
            return OpenAI(api_key=self.api_key, base_url=OPENROUTER_BASE_URL)
        except Exception as e:
            console.print_error(f"Error initializing OpenRouter client: {e}")
            sys.exit(1)

    def create_chat_session(
        self,
        system_instruction: str,
        history: Optional[List[Dict]] = None,
        thinking_budget: int = 0,
    ) -> OpenRouterChatSession:
        if not self._client:
            raise RuntimeError("LLM client not initialized")

        return OpenRouterChatSession(
            openrouter_client=self._client,
            model_name=self.model_name,
            system_instruction=system_instruction,
            history=history or [],
        )

    def count_history_tokens(self, history: List[Dict]) -> int:
        if not history:
            return 0

        try:
            text_parts = []
            for message in history:
                if "parts" in message and message["parts"]:
                    text_parts.append(message["parts"][0]["text"])
            return len(" ".join(text_parts)) // 4
        except Exception as e:
            console.print_error(f"Error while counting tokens: {e}")
            return 0

    def get_model_name(self) -> str:
        return self.model_name

    def is_available(self) -> bool:
        return self._client is not None and bool(self.api_key)

    def ready_for_use_message(self) -> str:
        if len(self.api_key) <= 8:
            masked_key = "****"
        else:
            masked_key = f"{self.api_key[:8]}...{self.api_key[-4:]}"

        return f"✅ OpenRouter client ready (Model: {self.model_name}, Key: {masked_key})"

    @property
    def client(self):
        return self._client
