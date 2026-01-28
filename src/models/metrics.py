"""
Modelos de métricas do Sextant.
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class MetricasGlobais(BaseModel):
    """Métricas globais da auditoria"""
    total_casos: int = 0
    casos_pass: int = 0
    casos_fail: int = 0
    casos_partial: int = 0
    taxa_acerto: float = Field(0.0, ge=0, le=1, description="Taxa de acerto geral")
    isr_medio: float = Field(
        0.0,
        ge=0,
        le=1,
        description="Information Sufficiency Ratio médio"
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
    """Métricas agrupadas por categoria"""
    categoria: str
    total: int = 0
    pass_count: int = 0
    fail_count: int = 0
    partial_count: int = 0
    taxa_acerto: float = 0.0
    isr_medio: float = 0.0
    taxa_acessibilidade: float = 0.0
