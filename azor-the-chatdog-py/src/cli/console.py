"""
Console output utilities for the chatbot.
Centralizes colorama usage for consistent terminal output.
"""
import sys
from colorama import init, Fore, Style
from files.config import LOG_DIR

init(autoreset=True)


def print_error(message: str):
    """Print an error message in red color.
    
    Args:
        message: The error message to display
    """
    print(Fore.RED + message + Style.RESET_ALL)


def print_assistant(message: str):
    """Print an assistant message in cyan color.
    
    Args:
        message: The assistant message to display
    """
    print(Fore.CYAN + message + Style.RESET_ALL)


def print_user(message: str):
    """Print a user message in blue color.
    
    Args:
        message: The user message to display
    """
    print(Fore.BLUE + message + Style.RESET_ALL)


def print_info(message: str):
    """Print an informational message in yellow color.
    
    Args:
        message: The informational message to display
    """
    print(message)

def print_help(message: str):
    """Print an informational message in yellow color.
    
    Args:
        message: The informational message to display
    """
    print(Fore.YELLOW + message + Style.RESET_ALL)


def display_help(session_id: str):
    """Displays a short help message."""
    print_info(f"Current session (ID): {session_id}")
    print_info(f"Session files are saved continuously in: {LOG_DIR}")
    print_help("Available commands (slash commands):")
    print_help("  /switch <ID>      - Switch to an existing session.")
    print_help("  /help             - Show this help.")
    print_help("  /exit, /quit      - End the chat.")
    print_help("\n  /session list     - List saved sessions.")
    print_help("  /session display  - Show full session history.")
    print_help("  /session pop      - Remove the last user/assistant message pair.")
    print_help("  /session clear    - Clear the current session history.")
    print_help("  /session new      - Start a new session.")


def display_final_instructions(session_id: str):
    """Displays instructions for continuing the session."""
    print_info("\n--- Resuming a session ---")
    print_info(f"To continue this session (ID: {session_id}) later, run:")
    print(Fore.WHITE + Style.BRIGHT + f"\n    python {sys.argv[0]} --session-id={session_id}\n" + Style.RESET_ALL)
    print("--------------------------------------\n")

