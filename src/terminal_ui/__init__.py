"""Terminal UI module for Heroes III HotA AI Assistant"""

# Placeholder for terminal UI components
# Will be implemented by Terminal UI agent

from typing import Any


class TerminalDisplay:
    """Placeholder for terminal display class"""
    
    def __init__(self):
        pass
    
    def display_advice(self, game_state: Any, advice: str):
        """Display advice in terminal"""
        print(f"\n[Turn {game_state.turn}] AI Advice:")
        print(advice)
    
    def display_status(self, message: str, level: str = "info"):
        """Display status message"""
        print(f"[{level.upper()}] {message}")