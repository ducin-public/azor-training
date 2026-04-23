from typing import List, Dict
from cli import console

def display_full_session(history: List[Dict], session_id: str, assistant_name: str):
    """
    Displays the full session history.
    
    Args:
        history: List of dicts: {"role": "user|model", "parts": [{"text": "..."}]}
        session_id: Session ID
        assistant_name: Assistant name to display
    """
    if not history:
        console.print_info("Session history is empty.")
        return

    console.print_info(f"\n--- FULL SESSION HISTORY ({session_id}, {len(history)} message(s)) ---")
    
    for i, content in enumerate(history):
        # Handle universal dictionary format
        role = content.get('role', '')
        display_role = "YOU" if role == "user" else assistant_name
        
        # Extract text from parts
        text = ""
        if 'parts' in content and content['parts']:
            text = content['parts'][0].get('text', '')
        
        # Display with appropriate function
        if role == "user":
            console.print_user(f"\n[{i+1}] {display_role}:")
            console.print_user(f"{text}")
        else:
            console.print_assistant(f"\n[{i+1}] {display_role}:")
            console.print_assistant(f"{text}")
            
    console.print_info("--------------------------------------------------------")
