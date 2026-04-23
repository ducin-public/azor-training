"""
LLM Client Protocol Definitions
Defines the interface contracts that all LLM clients must implement.
"""

from typing import Protocol, Optional, List, Dict, Any


class ChatSessionProtocol(Protocol):
    """
    Protocol defining the interface for chat sessions.
    All chat session wrappers must implement these methods.
    """

    def send_message(self, text: str) -> Any:
        """
        Sends a message and returns a response object with .text attribute.

        Args:
            text: User's message

        Returns:
            Response object with .text attribute containing the response
        """
        ...

    def get_history(self) -> List[Dict]:
        """
        Returns the current conversation history in universal format.

        Returns:
            List of dictionaries with format: {"role": "user|model", "parts": [{"text": "..."}]}
        """
        ...


class LLMClientProtocol(Protocol):
    """
    Protocol defining the interface for LLM clients.
    All LLM client implementations must implement these methods.
    """

    @staticmethod
    def preparing_for_use_message() -> str:
        """
        Returns a message indicating that the client is being prepared.

        Returns:
            Formatted preparation message string
        """
        ...

    @classmethod
    def from_environment(cls) -> 'LLMClientProtocol':
        """
        Factory method that creates a client instance from environment variables.

        Returns:
            Client instance initialized with environment variables
        """
        ...

    def create_chat_session(
        self,
        system_instruction: str,
        history: Optional[List[Dict]] = None,
        thinking_budget: int = 0
    ) -> ChatSessionProtocol:
        """
        Creates a new chat session with the specified configuration.

        Args:
            system_instruction: System role/prompt for the assistant
            history: Previous conversation history (optional, in universal dict format)
            thinking_budget: Thinking budget for the model

        Returns:
            Chat session object conforming to ChatSessionProtocol
        """
        ...

    def count_history_tokens(self, history: List[Dict]) -> int:
        """
        Counts tokens for the given conversation history.

        Args:
            history: Conversation history in universal dict format

        Returns:
            Total token count
        """
        ...

    def get_model_name(self) -> str:
        """
        Returns the currently configured model name.

        Returns:
            Model name string
        """
        ...

    def is_available(self) -> bool:
        """
        Checks if the LLM service is available and properly configured.

        Returns:
            True if client is properly initialized
        """
        ...

    def ready_for_use_message(self) -> str:
        """
        Returns a ready-to-use message with model info.

        Returns:
            Formatted message string for display
        """
        ...
