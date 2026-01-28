"""
Estado: Executa todos os casos de teste.
"""
import asyncio
from src.core.state import SextantState
from src.services.model_executor import ModelExecutor
from src.services.evaluator import CaseEvaluator
from src.states.calculate_metrics import CalculateMetricsState
from src.utils.config import settings
from src.utils.logger import setup_logger


class RunCasesState(SextantState):
    """Executa todos os casos de teste contra o modelo"""
    
    async def execute(self, context):
        try:
            self.logger.info("Starting test case execution...")
            
            # Inicializa executor e avaliador
            executor = ModelExecutor(
                client=context["model_client"],
                model_name=context["model_name"],
                prompt_template=context["prompt_template"],
                timeout=settings.MODEL_TIMEOUT,
                provider=context["model_provider"]
            )
            
            evaluator = CaseEvaluator(
                matriz=context["matriz_validacao"]
            )
            
            resultados = []
            casos = context["casos"]
            clientes_map = {c.cliente_id: c for c in context["clientes"]}
            politicas_text = context["politicas"]["markdown"]
            
            total_casos = len(casos)
            self.logger.info(f"Executing {total_casos} test cases...")
            
            for i, caso in enumerate(casos, 1):
                self.logger.info(f"Executing case {i}/{total_casos}: {caso.caso_id}")
                
                # Encontra cliente se houver referência
                cliente = None
                if caso.cliente_ref:
                    cliente = clientes_map.get(caso.cliente_ref)
                
                if not cliente:
                    # Tenta criar cliente mínimo do input do caso
                    try:
                        from src.models.domain import Cliente, TipoCliente
                        input_data = caso.input.copy()
                        input_data["cliente_id"] = caso.cliente_ref or f"TEMP_{caso.caso_id}"
                        input_data["tipo"] = TipoCliente(input_data.get("tipo", "PF"))
                        input_data["score_atual"] = input_data.get("score_atual", 500)
                        input_data["renda_mensal"] = input_data.get("renda_mensal", 1000.0)
                        cliente = Cliente(**input_data)
                    except Exception as e:
                        self.logger.warning(
                            f"Could not create client for case {caso.caso_id}: {e}"
                        )
                        # Cria resultado de falha
                        from src.models.domain import ResultadoAvaliacao
                        resultados.append(ResultadoAvaliacao(
                            caso_id=caso.caso_id,
                            status="FAIL",
                            pontos=0.0,
                            feedback=f"Cliente não encontrado: {e}"
                        ))
                        continue
                
                try:
                    # Executa caso contra modelo
                    resposta_dict = await executor.executar_caso(
                        cliente=cliente,
                        caso=caso,
                        politicas=politicas_text
                    )
                    
                    resposta_modelo = resposta_dict.get("resposta_modelo")
                    resposta_json = resposta_dict.get("resposta_json", {})

                    # Avalia resultado
                    resultado = evaluator.avaliar(
                        caso_id=caso.caso_id,
                        cliente_id=cliente.cliente_id,
                        resposta_modelo=resposta_modelo,
                        caso_esperado=caso,
                        resposta_json=resposta_json
                    )
                    
                    resultados.append(resultado)
                    
                    self.logger.info(
                        f"  Case {caso.caso_id}: {resultado.status} "
                        f"(Points: {resultado.pontos:.2f}, "
                        f"Accessible: {resultado.eh_acessivel})"
                    )
                    
                    # Pequeno delay para não sobrecarregar API
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    self.logger.error(f"Error executing case {caso.caso_id}: {e}", exc_info=True)
                    # Cria resultado de falha
                    from src.models.domain import ResultadoAvaliacao
                    resultados.append(ResultadoAvaliacao(
                        caso_id=caso.caso_id,
                        status="FAIL",
                        pontos=0.0,
                        feedback=f"Erro na execução: {str(e)}"
                    ))
            
            context["resultados"] = resultados
            
            self.logger.info(
                f"Completed execution: {len(resultados)} results "
                f"({sum(1 for r in resultados if r.status == 'PASS')} PASS, "
                f"{sum(1 for r in resultados if r.status == 'FAIL')} FAIL)"
            )
            
            self._log_transition("CalculateMetricsState", {
                "total_resultados": len(resultados)
            })
            
            return CalculateMetricsState()
        
        except Exception as e:
            self._log_error(e)
            raise
