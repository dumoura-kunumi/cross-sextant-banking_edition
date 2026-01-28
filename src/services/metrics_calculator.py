"""
Calculadora de métricas globais (ISR, disparate impact, acessibilidade).
"""
from typing import List, Dict, Optional
from collections import defaultdict
from src.models.domain import ResultadoAvaliacao, TipoCaso
from src.models.metrics import MetricasGlobais, MetricasPorCategoria
from src.services.accessibility import AccessibilityService
from src.utils.logger import setup_logger
from src.utils.config import settings


class MetricsCalculator:
    """Calcula métricas globais da auditoria"""
    
    def __init__(self):
        self.logger = setup_logger("MetricsCalculator")
        self.accessibility_service = AccessibilityService()
    
    def calcular(self, resultados: List[ResultadoAvaliacao]) -> MetricasGlobais:
        """
        Calcula todas as métricas globais.
        
        Args:
            resultados: Lista de resultados de avaliação
            
        Returns:
            MetricasGlobais
        """
        if not resultados:
            return MetricasGlobais()
        
        total = len(resultados)
        passes = len([r for r in resultados if r.status == "PASS"])
        fails = len([r for r in resultados if r.status == "FAIL"])
        partials = len([r for r in resultados if r.status == "PARTIAL"])
        
        # Taxa de acerto
        taxa_acerto = passes / total if total > 0 else 0.0
        
        # ISR médio (Information Sufficiency Ratio)
        # ISR = pontos / 5.0 (normalizado)
        isr_medio = sum(r.pontos for r in resultados) / total / 5.0 if total > 0 else 0.0
        
        # Acessibilidade
        acessiveis = len([r for r in resultados if r.eh_acessivel])
        taxa_acessibilidade = acessiveis / total if total > 0 else 0.0
        
        # Flesch-Kincaid médio
        niveis = []
        for r in resultados:
            if r.resposta_modelo and r.resposta_modelo.explicacao_acessivel:
                acess = self.accessibility_service.avaliar_explicacao(
                    r.resposta_modelo.explicacao_acessivel
                )
                if acess.get("nivel_leitura") is not None:
                    niveis.append(acess["nivel_leitura"])
        
        flesch_kincaid_medio = sum(niveis) / len(niveis) if niveis else None
        
        # Taxa por tipo de caso
        taxa_por_tipo = self._calcular_taxa_por_tipo(resultados)
        
        # Disparate Impact
        disparate_impact = self._calcular_disparate_impact(resultados)
        
        # Vieses detectados (agregado)
        vieses_unicos = set()
        for r in resultados:
            vieses_unicos.update(r.vieses_detectados)
        
        return MetricasGlobais(
            total_casos=total,
            casos_pass=passes,
            casos_fail=fails,
            casos_partial=partials,
            taxa_acerto=taxa_acerto,
            isr_medio=isr_medio,
            taxa_acessibilidade=taxa_acessibilidade,
            taxa_por_tipo=taxa_por_tipo,
            disparate_impact=disparate_impact,
            flesch_kincaid_medio=flesch_kincaid_medio,
            vieses_detectados=list(vieses_unicos)
        )
    
    def _calcular_taxa_por_tipo(self, resultados: List[ResultadoAvaliacao]) -> Dict[str, float]:
        """Calcula taxa de acerto por tipo de caso"""
        por_tipo = defaultdict(lambda: {"pass": 0, "total": 0})
        
        for r in resultados:
            # Extrai tipo do caso_id (ex: "ALUCINACAO_001" -> "ALUCINACAO")
            tipo = r.caso_id.split("_")[0] if "_" in r.caso_id else "OUTRO"
            por_tipo[tipo]["total"] += 1
            if r.status == "PASS":
                por_tipo[tipo]["pass"] += 1
        
        return {
            k: v["pass"] / v["total"] if v["total"] > 0 else 0.0
            for k, v in por_tipo.items()
        }
    
    def _calcular_disparate_impact(self, resultados: List[ResultadoAvaliacao]) -> Optional[float]:
        """
        Calcula Disparate Impact Ratio.
        
        DI = taxa_aprovacao_grupo_protegido / taxa_aprovacao_grupo_nao_protegido
        
        Se DI < 0.8 ou > 1.25, há disparidade.
        """
        # Agrupa por literacia presumida (proxy para grupo protegido)
        # Grupo protegido: literacia < 50
        # Grupo não protegido: literacia >= 50
        
        protegido_aprovados = 0
        protegido_total = 0
        nao_protegido_aprovados = 0
        nao_protegido_total = 0
        
        for r in resultados:
            if not r.resposta_modelo:
                continue
            
            # Tenta inferir literacia do cliente (se disponível no contexto)
            # Por enquanto, usa heurística baseada no caso
            # TODO: Melhorar com dados reais do cliente
            
            # Se decisão foi APROVADA, conta como aprovação
            if r.resposta_modelo.decisao.value == "APROVADA":
                # Heurística: casos de acessibilidade são mais prováveis de ter baixa literacia
                if "ACESSIBILIDADE" in r.caso_id:
                    protegido_aprovados += 1
                    protegido_total += 1
                else:
                    nao_protegido_aprovados += 1
                    nao_protegido_total += 1
            else:
                if "ACESSIBILIDADE" in r.caso_id:
                    protegido_total += 1
                else:
                    nao_protegido_total += 1
        
        if protegido_total == 0 or nao_protegido_total == 0:
            return None
        
        taxa_protegido = protegido_aprovados / protegido_total
        taxa_nao_protegido = nao_protegido_aprovados / nao_protegido_total
        
        if taxa_nao_protegido == 0:
            return None
        
        disparate_impact = taxa_protegido / taxa_nao_protegido
        
        return disparate_impact
    
    def calcular_por_categoria(
        self,
        resultados: List[ResultadoAvaliacao]
    ) -> List[MetricasPorCategoria]:
        """Calcula métricas agrupadas por categoria"""
        por_categoria = defaultdict(lambda: {
            "total": 0,
            "pass": 0,
            "fail": 0,
            "partial": 0,
            "pontos": [],
            "acessiveis": 0
        })
        
        for r in resultados:
            categoria = r.caso_id.split("_")[0] if "_" in r.caso_id else "OUTRO"
            por_categoria[categoria]["total"] += 1
            
            if r.status == "PASS":
                por_categoria[categoria]["pass"] += 1
            elif r.status == "FAIL":
                por_categoria[categoria]["fail"] += 1
            else:
                por_categoria[categoria]["partial"] += 1
            
            por_categoria[categoria]["pontos"].append(r.pontos)
            if r.eh_acessivel:
                por_categoria[categoria]["acessiveis"] += 1
        
        metricas = []
        for categoria, dados in por_categoria.items():
            total = dados["total"]
            isr_medio = sum(dados["pontos"]) / total / 5.0 if total > 0 else 0.0
            
            metricas.append(MetricasPorCategoria(
                categoria=categoria,
                total=total,
                pass_count=dados["pass"],
                fail_count=dados["fail"],
                partial_count=dados["partial"],
                taxa_acerto=dados["pass"] / total if total > 0 else 0.0,
                isr_medio=isr_medio,
                taxa_acessibilidade=dados["acessiveis"] / total if total > 0 else 0.0
            ))
        
        return metricas
