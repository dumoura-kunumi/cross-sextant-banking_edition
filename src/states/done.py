"""
Estado terminal: Auditoria concluída.
"""
from src.core.state import SextantState


class DoneState(SextantState):
    """Estado terminal - auditoria concluída"""
    
    async def execute(self, context):
        self.logger.info("Audit completed successfully!")
        self.logger.info(f"Report available at: {context.get('report_path', 'N/A')}")
        return None  # Estado terminal
