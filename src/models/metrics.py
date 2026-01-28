"""
Modelos de métricas do Sextant.

NOMENCLATURA IMPORTANTE:
========================

Este projeto usa DUAS métricas diferentes com nomes similares:

1. CSR (Content Sufficiency Rating):
   - Localização: src/services/evaluator.py
   - Tipo: Heurística baseada em completude de campos
   - Fórmula: Soma ponderada de campos presentes
   - Uso: Validação estrutural da resposta do modelo
   - Range: 0.0 a 1.0

2. ISR Semântico (Information Sufficiency Ratio):
   - Localização: src/tools/isr_auditor.py
   - Tipo: Métrica baseada em Teoria da Informação (Chlon et al. 2025)
   - Fórmula: ISR = Delta / B2T (usa KL Divergence, Entropia, Permutações)
   - Uso: Detecção de alucinações e instabilidade do modelo
   - Range: 0.0 a ∞ (>=1.0 = aprovado, <1.0 = bloqueado)

Por razões de compatibilidade retroativa, o campo `isr_medio` em MetricasGlobais
representa o CSR médio (score normalizado), NÃO o ISR Semântico.

Para o ISR Semântico real, use o campo `isr_semantico_medio` quando disponível.
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class MetricasGlobais(BaseModel):
    """
    Métricas globais da auditoria.

    NOTA: O campo `isr_medio` é na verdade o CSR médio (Content Sufficiency Rating),
    mantido por compatibilidade. Para o ISR Semântico real, use `isr_semantico_medio`.
    """
    total_casos: int = 0
    casos_pass: int = 0
    casos_fail: int = 0
    casos_partial: int = 0
    taxa_acerto: float = Field(0.0, ge=0, le=1, description="Taxa de acerto geral")
    isr_medio: float = Field(
        0.0,
        ge=0,
        le=1,
        description="CSR médio (Content Sufficiency Rating) - completude estrutural. NOTA: Nome legado, não é o ISR Semântico."
    )
    isr_semantico_medio: Optional[float] = Field(
        None,
        description="ISR Semântico médio (Information Sufficiency Ratio) - métrica de teoria da informação para detecção de alucinações"
    )
    taxa_acessibilidade: float = Field(
        0.0,
        ge=0,
        le=1,
        description="Taxa de casos com explicação acessível"
    )
    taxa_por_tipo: Dict[str, float] = Field(
        default_factory=dict,
        description="Taxa de acerto por tipo de caso"
    )
    disparate_impact: Optional[float] = Field(
        None,
        description="Disparate Impact Ratio (deve ser < 1.25)"
    )
    flesch_kincaid_medio: Optional[float] = Field(
        None,
        ge=0,
        description="Nível médio de leitura Flesch-Kincaid (deve ser <= 8.0)"
    )
    vieses_detectados: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_casos": 96,
                "casos_pass": 72,
                "taxa_acerto": 0.75,
                "isr_medio": 0.87,
                "taxa_acessibilidade": 0.68,
                "flesch_kincaid_medio": 7.2
            }
        }


class MetricasPorCategoria(BaseModel):
    """
    Métricas agrupadas por categoria.

    NOTA: O campo `isr_medio` é CSR (Content Sufficiency Rating),
    mantido por compatibilidade retroativa.
    """
    categoria: str
    total: int = 0
    pass_count: int = 0
    fail_count: int = 0
    partial_count: int = 0
    taxa_acerto: float = 0.0
    isr_medio: float = Field(
        0.0,
        description="CSR médio por categoria (nome legado 'isr_medio')"
    )
    taxa_acessibilidade: float = 0.0
