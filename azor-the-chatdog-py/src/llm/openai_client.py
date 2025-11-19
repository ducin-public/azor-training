"""
OpenAI LLM Client Implementation
Encapsulates all OpenAI interactions.
"""

import os
import sys
from typing import Optional, List, Any, Dict
from openai import OpenAI
from dotenv import load_dotenv
from cli import console
from .openai_validation import OpenAIConfig


class OpenAIResponse:
    """
    Response object that provides a .text attribute containing the response text.
    """

    def __init__(self, text: str):
        self.text = text


class OpenAIChatSession:
    """
    Wrapper class that provides a chat session interface compatible with Gemini's interface.
    Manages conversation history and provides send_message() and get_history() methods.
    """

    def __init__(self, openai_client: OpenAI, model_name: str, system_instruction: str, history: Optional[List[Dict]] = None):
        """
        Initialize the OpenAI chat session.

        Args:
            openai_client: Initialized OpenAI client instance
            model_name: Model to use (e.g., 'gpt-4-turbo')
            system_instruction: System prompt for the assistant
            history: Previous conversation history in universal format
        """
        self.openai_client = openai_client
        self.model_name = model_name
        self.system_instruction = system_instruction
        self._history = history or []

    def send_message(self, text: str) -> Any:
        """
        Sends a message to the OpenAI model and returns a response object.

        Args:
            text: User's message

        Returns:
            Response object with .text attribute containing the response
        """
        # Add user message to history
        user_message = {"role": "user", "parts": [{"text": text}]}
        self._history.append(user_message)

        # Convert universal format to OpenAI format
        openai_messages = self._convert_to_openai_format()

        try:
            # Generate response using OpenAI
            completion = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                max_tokens=512
            )

            response_text = completion.choices[0].message.content.strip()

            # Add assistant response to history
            assistant_message = {"role": "model", "parts": [{"text": response_text}]}
            self._history.append(assistant_message)

            # Return response object compatible with Gemini interface
            return OpenAIResponse(response_text)

        except Exception as e:
            console.print_error(f"Błąd podczas generowania odpowiedzi OpenAI: {e}")
            # Return error response
            error_text = "Przepraszam, wystąpił błąd podczas generowania odpowiedzi."
            assistant_message = {"role": "model", "parts": [{"text": error_text}]}
            self._history.append(assistant_message)
            return OpenAIResponse(error_text)

    def get_history(self) -> List[Dict]:
        """Returns the current conversation history in universal format."""
        return self._history

    def _convert_to_openai_format(self) -> List[Dict[str, str]]:
        """
        Converts universal history format to OpenAI message format.

        Returns:
            List of messages in OpenAI format: [{"role": "user|assistant|system", "content": "..."}]
        """
        openai_messages = []

        # Add system instruction first
        if self.system_instruction:
            openai_messages.append({
                "role": "system",
                "content": self.system_instruction
            })

        # Convert conversation history
        for message in self._history:
            role = message["role"]
            text = message["parts"][0]["text"] if message["parts"] else ""

            # Map universal roles to OpenAI roles
            if role == "user":
                openai_role = "user"
            elif role == "model":
                openai_role = "assistant"
            else:
                openai_role = role

            openai_messages.append({
                "role": openai_role,
                "content": text
            })

        return openai_messages


class OpenAIClient:
    """
    Encapsulates all OpenAI interactions.
    Provides a clean interface for chat sessions, token counting, and configuration.
    """

    def __init__(self, model_name: str, api_key: str):
        """
        Initialize the OpenAI client with explicit parameters.

        Args:
            model_name: Model to use (e.g., 'gpt-4-turbo')
            api_key: OpenAI API key

        Raises:
            ValueError: If api_key is empty or None
        """
        if not api_key:
            raise ValueError("API key cannot be empty or None")

        self.model_name = model_name
        self.api_key = api_key

        # Initialize the client during construction
        self._client = self._initialize_client()

    @staticmethod
    def preparing_for_use_message() -> str:
        """
        Returns a message indicating that OpenAI client is being prepared.

        Returns:
            Formatted preparation message string
        """
        return "🤖 Przygotowywanie klienta OpenAI..."

    @classmethod
    def from_environment(cls) -> 'OpenAIClient':
        """
        Factory method that creates an OpenAIClient instance from environment variables.

        Returns:
            OpenAIClient instance initialized with environment variables

        Raises:
            ValueError: If required environment variables are not set
        """
        load_dotenv()

        # Walidacja z Pydantic
        config = OpenAIConfig(
            model_name=os.getenv('OPENAI_MODEL_NAME') or os.getenv('MODEL_NAME', 'gpt-4-turbo'),
            openai_api_key=os.getenv('OPENAI_API_KEY', '')
        )

        return cls(model_name=config.model_name, api_key=config.openai_api_key)

    def _initialize_client(self) -> OpenAI:
        """
        Initializes the OpenAI client.

        Returns:
            Initialized OpenAI client

        Raises:
            SystemExit: If client initialization fails
        """
        try:
            return OpenAI(api_key=self.api_key)
        except Exception as e:
            console.print_error(f"Błąd inicjalizacji klienta OpenAI: {e}")
            sys.exit(1)

    def create_chat_session(self,
                          system_instruction: str,
                          history: Optional[List[Dict]] = None,
                          thinking_budget: int = 0) -> OpenAIChatSession:
        """
        Creates a new chat session with the specified configuration.

        Args:
            system_instruction: System role/prompt for the assistant
            history: Previous conversation history (optional, in universal dict format)
            thinking_budget: Thinking budget for the model (ignored for OpenAI, compatibility parameter)

        Returns:
            OpenAIChatSession with universal dictionary-based interface
        """
        if not self._client:
            raise RuntimeError("LLM client not initialized")

        return OpenAIChatSession(
            openai_client=self._client,
            model_name=self.model_name,
            system_instruction=system_instruction,
            history=history or []
        )

    def count_history_tokens(self, history: List[Dict]) -> int:
        """
        Counts tokens for the given conversation history.
        Note: This is an approximation using rough estimation.
        OpenAI's tiktoken library could be used for more accurate counting.

        Args:
            history: Conversation history in universal dict format

        Returns:
            Estimated token count
        """
        if not history:
            return 0

        try:
            # Build text from history
            text_parts = []
            for message in history:
                if "parts" in message and message["parts"]:
                    text_parts.append(message["parts"][0]["text"])

            full_text = " ".join(text_parts)

            # Rough estimation: ~4 characters per token on average
            # For more accurate counting, use tiktoken library
            return len(full_text) // 4

        except Exception as e:
            console.print_error(f"Błąd podczas liczenia tokenów: {e}")
            return 0

    def get_model_name(self) -> str:
        """Returns the currently configured model name."""
        return self.model_name

    def is_available(self) -> bool:
        """
        Checks if the LLM service is available and properly configured.

        Returns:
            True if client is properly initialized and has API key
        """
        return self._client is not None and bool(self.api_key)

    def ready_for_use_message(self) -> str:
        """
        Returns a ready-to-use message with model info and masked API key.

        Returns:
            Formatted message string for display
        """
        # Mask API key - show first 4 and last 4 characters
        if len(self.api_key) <= 8:
            masked_key = "****"
        else:
            masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}"

        return f"✅ Klient OpenAI gotowy do użycia (Model: {self.model_name}, Key: {masked_key})"

    @property
    def client(self):
        """
        Provides access to the underlying OpenAI client for backwards compatibility.
        This property should be used sparingly and eventually removed.
        """
        return self._client
