"""
Máquina de estados principal do Sextant Banking Edition.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from src.core.state import SextantState
from src.states.load_artifacts import LoadArtifactsState
from src.utils.logger import setup_logger


class SextantFSM:
    """Máquina de estados para Sextant Banking Edition"""
    
    def __init__(self):
        self.context: Dict[str, Any] = {}
        self.current_state: Optional[SextantState] = LoadArtifactsState()
        self.logger = setup_logger("SextantFSM")
        self.history: list = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    async def run(self):
        """Executa a máquina de estados até terminal"""
        self.start_time = datetime.now()
        self.logger.info("Starting Sextant FSM execution")
        
        while self.current_state:
            try:
                state_name = self.current_state.__class__.__name__
                self.logger.info(f"Entering state: {state_name}")
                
                self.history.append({
                    "state": state_name,
                    "timestamp": datetime.now().isoformat(),
                    "context_keys": list(self.context.keys())
                })
                
                # Executa estado atual
                proximo_estado = await self.current_state.execute(self.context)
                self.current_state = proximo_estado
                
                if proximo_estado is None:
                    self.logger.info("FSM reached terminal state")
                
            except Exception as e:
                self.logger.error(
                    f"Error in {self.current_state.__class__.__name__}: {e}",
                    exc_info=True
                )
                self.current_state = None  # Termina com erro
        
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds() if self.start_time else 0
        self.logger.info(f"FSM execution completed in {duration:.2f} seconds")
    
    def get_state_history(self) -> list:
        """Retorna histórico de estados"""
        return self.history
    
    def get_execution_time(self) -> Optional[float]:
        """Retorna tempo de execução em segundos"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
