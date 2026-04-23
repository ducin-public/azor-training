"""
Azor Assistant Configuration
Contains Azor-specific factory function.
"""

from .assistent import Assistant

def create_azor_assistant() -> Assistant:
    """
    Creates and returns an Azor assistant instance with default configuration.
    
    Returns:
        Assistant: Configured Azor assistant instance
    """
    # Assistant name displayed in the chat
    assistant_name = "AZOR"
    
    # System role/prompt for the assistant
    system_role = "You are a helpful assistant. Your name is Azor and you are a dog of great capabilities. You are the best friend of Reks, but you happily reach out to people. Your task is to help the user solve problems, answer questions, and provide information in a polite and understandable way."
    
    return Assistant(
        system_prompt=system_role,
        name=assistant_name
    )
