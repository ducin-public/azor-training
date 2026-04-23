"""
Anthropic LLM Client Implementation
Encapsulates all Anthropic Claude interactions.
"""

import os
import sys
from typing import Optional, List, Any, Dict
from anthropic import Anthropic
from dotenv import load_dotenv
from cli import console
from .anthropic_validation import AnthropicConfig


class AnthropicResponse:
    """
    Response object that provides a .text attribute containing the response text.
    """

    def __init__(self, text: str):
        self.text = text


class AnthropicChatSession:
    """
    Wrapper class that provides a chat session interface compatible with Gemini's interface.
    Manages conversation history and provides send_message() and get_history() methods.
    """

    def __init__(self, anthropic_client: Anthropic, model_name: str, system_instruction: str, history: Optional[List[Dict]] = None):
        """
        Initialize the Anthropic chat session.

        Args:
            anthropic_client: Initialized Anthropic client instance
            model_name: Model to use (e.g., 'claude-3-5-haiku-latest')
            system_instruction: System prompt for the assistant
            history: Previous conversation history in universal format
        """
        self.anthropic_client = anthropic_client
        self.model_name = model_name
        self.system_instruction = system_instruction
        self._history = history or []

    def send_message(self, text: str) -> Any:
        """
        Sends a message to the Anthropic model and returns a response object.

        Args:
            text: User's message

        Returns:
            Response object with .text attribute containing the response
        """
        # Add user message to history
        user_message = {"role": "user", "parts": [{"text": text}]}
        self._history.append(user_message)

        # Convert universal format to Anthropic format
        anthropic_messages = self._convert_to_anthropic_format()

        try:
            # Generate response using Anthropic
            message = self.anthropic_client.messages.create(
                model=self.model_name,
                max_tokens=512,
                system=self.system_instruction,
                messages=anthropic_messages
            )

            response_text = message.content[0].text.strip()

            # Add assistant response to history
            assistant_message = {"role": "model", "parts": [{"text": response_text}]}
            self._history.append(assistant_message)

            # Return response object compatible with Gemini interface
            return AnthropicResponse(response_text)

        except Exception as e:
            console.print_error(f"Error while generating Anthropic response: {e}")
            # Return error response
            error_text = "Sorry, an error occurred while generating a response."
            assistant_message = {"role": "model", "parts": [{"text": error_text}]}
            self._history.append(assistant_message)
            return AnthropicResponse(error_text)

    def get_history(self) -> List[Dict]:
        """Returns the current conversation history in universal format."""
        return self._history

    def _convert_to_anthropic_format(self) -> List[Dict[str, str]]:
        """
        Converts universal history format to Anthropic message format.

        Returns:
            List of messages in Anthropic format: [{"role": "user|assistant", "content": "..."}]
        """
        anthropic_messages = []

        # Convert conversation history (system is passed separately in Anthropic)
        for message in self._history:
            role = message["role"]
            text = message["parts"][0]["text"] if message["parts"] else ""

            # Map universal roles to Anthropic roles
            if role == "user":
                anthropic_role = "user"
            elif role == "model":
                anthropic_role = "assistant"
            else:
                # Default to user for unknown roles
                anthropic_role = "user"

            anthropic_messages.append({
                "role": anthropic_role,
                "content": text
            })

        return anthropic_messages


class AnthropicClient:
    """
    Encapsulates all Anthropic Claude interactions.
    Provides a clean interface for chat sessions, token counting, and configuration.
    """

    def __init__(self, model_name: str, api_key: str):
        """
        Initialize the Anthropic client with explicit parameters.

        Args:
            model_name: Model to use (e.g., 'claude-3-5-haiku-latest')
            api_key: Anthropic API key

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
        Returns a message indicating that Anthropic client is being prepared.

        Returns:
            Formatted preparation message string
        """
        return "🤖 Preparing Anthropic client..."

    @classmethod
    def from_environment(cls) -> 'AnthropicClient':
        """
        Factory method that creates an AnthropicClient instance from environment variables.

        Returns:
            AnthropicClient instance initialized with environment variables

        Raises:
            ValueError: If required environment variables are not set
        """
        load_dotenv()

        # Walidacja z Pydantic
        config = AnthropicConfig(
            model_name=os.getenv('ANTHROPIC_MODEL_NAME') or os.getenv('MODEL_NAME', 'claude-3-5-haiku-latest'),
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY', '')
        )

        return cls(model_name=config.model_name, api_key=config.anthropic_api_key)

    def _initialize_client(self) -> Anthropic:
        """
        Initializes the Anthropic client.

        Returns:
            Initialized Anthropic client

        Raises:
            SystemExit: If client initialization fails
        """
        try:
            return Anthropic(api_key=self.api_key)
        except Exception as e:
            console.print_error(f"Error initializing Anthropic client: {e}")
            sys.exit(1)

    def create_chat_session(self,
                          system_instruction: str,
                          history: Optional[List[Dict]] = None,
                          thinking_budget: int = 0) -> AnthropicChatSession:
        """
        Creates a new chat session with the specified configuration.

        Args:
            system_instruction: System role/prompt for the assistant
            history: Previous conversation history (optional, in universal dict format)
            thinking_budget: Thinking budget for the model (ignored for Anthropic, compatibility parameter)

        Returns:
            AnthropicChatSession with universal dictionary-based interface
        """
        if not self._client:
            raise RuntimeError("LLM client not initialized")

        return AnthropicChatSession(
            anthropic_client=self._client,
            model_name=self.model_name,
            system_instruction=system_instruction,
            history=history or []
        )

    def count_history_tokens(self, history: List[Dict]) -> int:
        """
        Counts tokens for the given conversation history.
        Note: This is an approximation using rough estimation.
        Anthropic's SDK provides count_tokens() for more accurate counting.

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
            # For more accurate counting, use Anthropic's count_tokens method
            return len(full_text) // 4

        except Exception as e:
            console.print_error(f"Error while counting tokens: {e}")
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

        return f"✅ Anthropic client ready (Model: {self.model_name}, Key: {masked_key})"

    @property
    def client(self):
        """
        Provides access to the underlying Anthropic client for backwards compatibility.
        This property should be used sparingly and eventually removed.
        """
        return self._client
