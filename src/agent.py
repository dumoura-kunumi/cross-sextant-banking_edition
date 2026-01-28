"""
Compliance Agent - Context class for the State Design Pattern.

This class maintains the agent's state, history, and tools.
It acts as the Context in the State Design Pattern, delegating
behavior to the current state.
"""

from typing import List, Dict, Any, Optional
from openai import OpenAI
from src.tools.isr_auditor import SemanticISRAuditorTool
from src.states.base import AgentState


class ComplianceAgent:
    """
    Context class for the Compliance Agent State Machine.
    
    Maintains:
    - Message history for LLM interactions
    - OpenAI client instance
    - ISR Auditor Tool instance
    - Current state (Idle, Analysis, Audit, FinalResponse, Error)
    - Shared data between states (current_query, tool_call data, etc.)
    
    The agent follows this flow:
    IdleState -> AnalysisState -> AuditState -> FinalResponseState -> IdleState
    """
    
    def __init__(self, client: OpenAI, initial_state: AgentState):
        """
        Initializes the Compliance Agent.
        
        Args:
            client: OpenAI client instance
            initial_state: Initial state for the agent (typically IdleState)
        """
        self.client = client
        self.history: List[Dict[str, Any]] = []
        self.tool = SemanticISRAuditorTool(client)
        self._state = initial_state
        
        # Shared data between states
        self.current_query: Optional[str] = None
        self.current_tool_call: Optional[Any] = None
        self.decision_data: Optional[Dict[str, Any]] = None
        self.audit_result: Optional[Dict[str, Any]] = None

    def transition_to(self, state: AgentState) -> None:
        """
        Transition to a new state.
        
        This is the core method of the State Pattern - it allows states
        to change the context's behavior by changing its state.
        
        Args:
            state: The new state to transition to
        """
        previous_state = type(self._state).__name__
        new_state = type(state).__name__
        print(f"[State Transition] {previous_state} -> {new_state}")
        self._state = state

    def run(self) -> None:
        """
        Executes the current state's logic.
        
        This method delegates to the current state's handle() method.
        The state is responsible for:
        1. Performing its logic
        2. Transitioning to the next state via transition_to()
        
        Note: This should be called in a loop in main.py until the agent
        returns to IdleState or reaches a terminal state.
        """
        self._state.handle(self)

    def add_message(
        self,
        role: str,
        content: Optional[str] = None,
        tool_calls: Optional[List] = None,
        tool_call_id: Optional[str] = None,
        name: Optional[str] = None
    ) -> None:
        """
        Helper method to add messages to the conversation history.
        
        Args:
            role: Message role ("system", "user", "assistant", "tool")
            content: Message content (text)
            tool_calls: List of tool calls (for assistant messages)
            tool_call_id: Tool call ID (for tool messages)
            name: Tool name (for tool messages)
        """
        message: Dict[str, Any] = {"role": role}
        
        if content is not None:
            message["content"] = content
        if tool_calls:
            message["tool_calls"] = tool_calls
        if tool_call_id:
            message["tool_call_id"] = tool_call_id
        if name:
            message["name"] = name
            
        self.history.append(message)
    
    def get_current_state_name(self) -> str:
        """
        Returns the name of the current state (for debugging/logging).
        
        Returns:
            Name of the current state class
        """
        return type(self._state).__name__