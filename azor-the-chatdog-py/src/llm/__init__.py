"""
LLM Module Initialization
Provides factory function for creating LLM clients based on configuration.
"""

import os
from typing import Type
from .protocol import LLMClientProtocol
from .gemini_client import GeminiLLMClient
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from .openrouter_client import OpenRouterClient

# LlamaClient is intentionally NOT imported here — llama_cpp is an optional
# dependency that is only loaded when ENGINE=LLAMA_CPP.

_ENGINE_MAPPING: dict[str, Type[LLMClientProtocol]] = {
    'GEMINI': GeminiLLMClient,
    'OPENAI': OpenAIClient,
    'ANTHROPIC': AnthropicClient,
    'OPENROUTER': OpenRouterClient,
}


def create_llm_client_from_environment() -> LLMClientProtocol:
    """
    Factory function that creates the appropriate LLM client based on the ENGINE environment variable.

    LlamaClient is imported lazily so that llama-cpp-python is never loaded unless ENGINE=LLAMA_CPP.

    Returns:
        LLMClientProtocol: An initialized LLM client instance

    Raises:
        ValueError: If ENGINE is not set or not recognized
        ImportError: If ENGINE=LLAMA_CPP but llama-cpp-python is not installed
    """
    from cli import console

    engine = os.getenv('ENGINE')
    if not engine:
        raise ValueError("ENGINE environment variable is not set")

    engine = engine.upper()

    if engine == 'LLAMA_CPP':
        try:
            from .llama_client import LlamaClient
        except ImportError as e:
            raise ImportError(
                "ENGINE is set to LLAMA_CPP but llama-cpp-python is not installed. "
                "Install it with: pip install llama-cpp-python"
            ) from e
        console.print_info(LlamaClient.preparing_for_use_message())
        return LlamaClient.from_environment()

    if engine not in _ENGINE_MAPPING:
        valid_engines = ', '.join([*_ENGINE_MAPPING.keys(), 'LLAMA_CPP'])
        raise ValueError(f"ENGINE must be one of: {valid_engines}, got: {engine}")

    client_class = _ENGINE_MAPPING[engine]
    console.print_info(client_class.preparing_for_use_message())
    return client_class.from_environment()


# Export the protocol and factory function
__all__ = ['LLMClientProtocol', 'create_llm_client_from_environment']
