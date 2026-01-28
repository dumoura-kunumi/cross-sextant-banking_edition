"""
Estado: Calcula métricas globais.
"""
from src.core.state import SextantState
from src.services.metrics_calculator import MetricsCalculator
from src.states.generate_report import GenerateReportState


class CalculateMetricsState(SextantState):
    """Calcula métricas globais da auditoria"""
    
    async def execute(self, context):
        try:
            self.logger.info("Calculating global metrics...")
            
            resultados = context.get("resultados", [])
            
            if not resultados:
                self.logger.warning("No results to calculate metrics")
                context["metricas"] = None
            else:
                calculator = MetricsCalculator()
                metricas = calculator.calcular(resultados)
                metricas_por_categoria = calculator.calcular_por_categoria(resultados)
                
                context["metricas"] = metricas
                context["metricas_por_categoria"] = metricas_por_categoria
                
                self.logger.info(
                    f"Metrics calculated: "
                    f"Taxa Acerto: {metricas.taxa_acerto:.2%}, "
                    f"ISR Médio: {metricas.isr_medio:.3f}, "
                    f"Taxa Acessibilidade: {metricas.taxa_acessibilidade:.2%}"
                )
                
                if metricas.flesch_kincaid_medio:
                    self.logger.info(
                        f"Flesch-Kincaid Médio: {metricas.flesch_kincaid_medio:.1f}"
                    )
                
                if metricas.disparate_impact:
                    self.logger.info(
                        f"Disparate Impact: {metricas.disparate_impact:.3f}"
                    )
            
            self._log_transition("GenerateReportState", {})
            
            return GenerateReportState()
        
        except Exception as e:
            self._log_error(e)
            raise
