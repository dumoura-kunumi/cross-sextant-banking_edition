"""
Idle State - Initial state that captures user input.

This state is the entry point for each user query. It:
1. Captures the user query from context.current_query
2. Adds it to the conversation history
3. Transitions to AnalysisState to begin the audit process
"""

from typing import Any
from src.states.base import AgentState


class IdleState(AgentState):
    """
    Initial state that waits for and processes user input.
    
    This state:
    1. Reads the user query from context.current_query (set by main.py)
    2. Adds the query to the conversation history
    3. Transitions to AnalysisState to begin the audit process
    
    Note: In a real event-driven system, this state might wait for events.
    Here, we assume the query is already set by the main loop.
    """
    
    def handle(self, context: Any) -> None:
        """
        Handles the idle state logic.
        
        Args:
            context: The ComplianceAgent context instance
        """
        query = context.current_query
        
        if not query or not query.strip():
            print(f"[{self.__class__.__name__}] No query provided. Waiting...")
            return
        
        print(f"[{self.__class__.__name__}] Received user query: {query[:100]}...")
        
        # Add user query to conversation history
        context.add_message(role="user", content=query)
        
        # Clear previous state data
        context.current_tool_call = None
        context.audit_result = None
        context.decision_data = None
        
        # Transition to AnalysisState
        # This begins the audit process:
        # Idle -> Analysis -> Audit -> FinalResponse -> Idle
        from src.states.analysis import AnalysisState
        context.transition_to(AnalysisState())
