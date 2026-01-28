"""
Base abstrata para todos os estados do Sextant FSM.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from src.utils.logger import setup_logger


class SextantState(ABC):
    """Base para todos os estados do Sextant Banking Edition"""
    
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Optional["SextantState"]:
        """
        Executa o estado e retorna próximo estado (ou None se terminal).
        
        Args:
            context: Contexto compartilhado entre estados
            
        Returns:
            Próximo estado ou None se terminal
        """
        pass
    
    def _log_transition(self, proximo_estado: str, dados: Optional[Dict] = None):
        """Log estruturado de transição"""
        self.logger.info(
            f"Transitioning to {proximo_estado}",
            extra={"extra_data": dados or {}}
        )
    
    def _log_error(self, error: Exception, context: Optional[Dict] = None):
        """Log estruturado de erro"""
        self.logger.error(
            f"Error in {self.__class__.__name__}: {error}",
            exc_info=True,
            extra={"extra_data": context or {}}
        )
