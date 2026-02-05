import sys

# ANSI colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

def ask_user(question: str, default: bool = True) -> bool:
    """
    Prompts the user with a yes/no question.
    
    Args:
        question: The question to ask.
        default: True for [Y/n] (default yes), False for [y/N] (default no).
    
    Returns:
        True if user confirmed, False otherwise.
    """
    choices = " [Y/n]: " if default else " [y/N]: "
    
    while True:
        # Use print with flush=True to ensure prompt is visible
        print(f"{Colors.YELLOW}❓ {question}{choices}{Colors.ENDC}", end='', flush=True)
        choice = input().lower()
        if not choice: # User just pressed Enter
            return default
        if choice in ['y', 'yes']:
            return True
        if choice in ['n', 'no']:
            return False
