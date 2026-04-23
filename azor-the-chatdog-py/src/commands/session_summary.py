from typing import List, Dict
from cli import console

def display_history_summary(history: List[Dict], assistant_name: str):
    """
    Shows a short history summary: omitted count and the last 2 messages.
    
    Args:
        history: List of dicts: {"role": "user|model", "parts": [{"text": "..."}]}
        assistant_name: Assistant name to display
    """
    total_count = len(history)
    
    if total_count == 0:
        return

    # Summary header
    if total_count > 2:
        console.print_info(f"\n--- Session resumed ---")
        omitted_count = total_count - 2
        console.print_info(f"({omitted_count} earlier message(s) omitted)")
    else:
        console.print_info(f"\n--- Session ---")

    # Display last 2 messages
    last_two = history[-2:]
    
    for content in last_two:
        # Handle universal dictionary format
        role = content.get('role', '')
        display_role = "YOU" if role == "user" else assistant_name
        
        # Extract text from parts
        text = ""
        if 'parts' in content and content['parts']:
            text = content['parts'][0].get('text', '')
        
        if role == "user":
            console.print_user(f"  {display_role}: {text[:80]}...")
        elif role == "model":
            console.print_assistant(f"  {display_role}: {text[:80]}...")
            
    console.print_info(f"----------------------------")

