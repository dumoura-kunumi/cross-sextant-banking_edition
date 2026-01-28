"""
Error State - Handles errors in the state machine.

This state is used when unrecoverable errors occur.
It can log the error and either transition back to Idle or terminate.
"""

from typing import Any
from src.states.base import AgentState


class ErrorState(AgentState):
    """
    Error state for handling unrecoverable errors.
    
    This state:
    1. Logs the error
    2. Optionally adds an error message to history
    3. Transitions back to IdleState to allow recovery
    """
    
    def __init__(self, error_message: str = "An error occurred"):
        """
        Initializes the error state with an error message.
        
        Args:
            error_message: Description of the error
        """
        self.error_message = error_message
    
    def handle(self, context: Any) -> None:
        """
        Handles the error state logic.
        
        Args:
            context: The ComplianceAgent context instance
        """
        print(f"[{self.__class__.__name__}] ERROR: {self.error_message}")
        
        # Optionally add error message to history
        # context.add_message(
        #     role="assistant",
        #     content=f"I encountered an error: {self.error_message}. Please try again."
        # )
        
        # Transition back to IdleState to allow recovery
        from src.states.idle import IdleState
        context.transition_to(IdleState())
