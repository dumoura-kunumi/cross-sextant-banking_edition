from abc import ABC, abstractmethod

class AgentState(ABC):
    """
    Abstract base class for all agent states.
    """
    
    @abstractmethod
    def handle(self, context) -> None:
        """
        Handle the logic for the current state and transition to the next state.
        
        Args:
            context: The ComplianceAgent context instance.
        """
        pass
