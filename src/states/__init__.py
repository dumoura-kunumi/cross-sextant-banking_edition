"""
States package for the Compliance Agent State Machine.

This package contains all state implementations following the State Design Pattern:
- base: Abstract base class for all states
- idle: Initial state that captures user input
- analysis: Analyzes user intent and calls audit tool
- audit: Executes ISR semantic audit
- final_response: Generates final response to user
- error: Handles errors in the state machine
"""

from src.states.base import AgentState
from src.states.idle import IdleState
from src.states.analysis import AnalysisState
from src.states.audit import AuditState
from src.states.final_response import FinalResponseState
from src.states.error import ErrorState

__all__ = [
    "AgentState",
    "IdleState",
    "AnalysisState",
    "AuditState",
    "FinalResponseState",
    "ErrorState",
]
