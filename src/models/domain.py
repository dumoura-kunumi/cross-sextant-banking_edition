"""
Modelos de domínio do Sextant usando Pydantic V2.
Representa entidades do negócio: Clientes, Casos de Teste, Resultados.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Literal, Any
from enum import Enum
from datetime import datetime, date


class TipoCaso(str, Enum):
    """Tipos de cenários de teste"""
    ALUCINACAO = "alucinacao"
    NEEDLE = "needle"
    NEEDLE_IN_HAYSTACK = "needle_in_haystack"
    INCONSISTENCIA = "inconsistencia"
    ADVERSARIAL = "adversarial"
    ACESSIBILIDADE = "acessibilidade"


class Severidade(str, Enum):
    """Níveis de severidade"""
    CRITICA = "critica"
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"


class TipoCliente(str, Enum):
    """Tipos de cliente"""
    PF = "PF"
    PJ = "PJ"


class Decisao(str, Enum):
    """Decisões possíveis"""
    APROVADA = "APROVADA"
    NEGADA = "NEGADA"
    RECUSADA = "RECUSADA"
    ANALISE_GERENCIAL = "ANALISE_GERENCIAL"


class Cliente(BaseModel):
    """Representa um cliente para auditoria"""
    cliente_id: str = Field(..., description="ID único do cliente")
    tipo: TipoCliente
    nome: Optional[str] = None
    nome_ou_razao: Optional[str] = None
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    email: Optional[str] = None
    data_nascimento: Optional[date] = None
    data_fundacao: Optional[date] = None
    endereco: Optional[str] = None
    profissao: Optional[str] = None
    setor: Optional[str] = None
    tempo_emprego_meses: Optional[int] = None
    score_atual: int = Field(..., ge=0, le=1000, description="Score de crédito 0-1000")
    score_componentes: Optional[Dict[str, int]] = None
    renda_mensal: Optional[float] = Field(None, ge=0, description="Renda mensal em R$ (PF only)")
    fonte_renda: Optional[str] = None
    saldo_conta: Optional[float] = None
    movimentacao_media_mensal: Optional[float] = None
    tempo_correntista_meses: Optional[int] = None
    atrasos_historico: Optional[List[Dict]] = None
    defaults_historico: Optional[List[Dict]] = None
    limite_atual: Optional[float] = None
    saldo_devedor: Optional[float] = None
    ultima_consulta_spc: Optional[date] = None
    pep: Optional[bool] = False
    sancionado: Optional[bool] = False
    literacia_presumida: int = Field(
        default=50,
        ge=0,
        le=100,
        description="0-100: % de literacia financeira presumida (Design for All)"
    )
    
    @field_validator("nome_ou_razao", mode="before")
    @classmethod
    def validate_nome_ou_razao(cls, v, info):
        """Garante que nome_ou_razao existe"""
        if v is None and info.data.get("nome"):
            return info.data.get("nome")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "cliente_id": "PF_001",
                "tipo": "PF",
                "nome_ou_razao": "João Silva",
                "score_atual": 750,
                "renda_mensal": 5000.0,
                "literacia_presumida": 60
            }
        }


class CasoTeste(BaseModel):
    """Um caso de teste de auditoria"""
    caso_id: str = Field(..., description="ID único do caso")
    tipo_cenario: TipoCaso
    subtipo: str
    descricao: str
    cliente_ref: Optional[str] = Field(None, description="Referência ao cliente_id")
    input: Dict[str, Any] = Field(..., description="Input do caso")
    output_esperado: Dict[str, Any] = Field(..., description="Output esperado")
    criterios_validacao: Optional[List[str]] = Field(
        default_factory=list,
        description="Critérios de validação"
    )
    dificuldade: Literal["easy", "medium", "hard"] = "medium"
    severity: Optional[Severidade] = None
    tags: List[str] = Field(default_factory=list)


class RespostaModelo(BaseModel):
    """Resposta estruturada do modelo IA"""
    decisao: Decisao
    score: Optional[int] = Field(None, ge=0, le=1000)
    confianca: float = Field(0.5, ge=0, le=1, description="Confiança na decisão 0-1")
    rastreamento: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Rastreamento de qual política foi usada"
    )
    avisos: List[str] = Field(default_factory=list)
    explicacao_acessivel: Optional[str] = Field(
        None,
        description="Explicação em linguagem simples (8ª série) - CRITÉRIO DE DESIGN FOR ALL"
    )
    motivo: Optional[str] = None
    politica_usada: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "decisao": "APROVADA",
                "score": 750,
                "confianca": 0.85,
                "explicacao_acessivel": "Seu pedido foi aprovado porque você tem um bom histórico de pagamento."
            }
        }


class ResultadoAvaliacao(BaseModel):
    """Resultado de um caso de teste"""
    caso_id: str
    cliente_id: Optional[str] = None
    status: Literal["PASS", "FAIL", "PARTIAL"] = "FAIL"
    pontos: float = Field(0.0, ge=0, le=5, description="Pontuação 0-5")
    eh_acessivel: bool = Field(
        False,
        description="Consumidor consegue entender decisão? (Design for All)"
    )
    vieses_detectados: List[str] = Field(default_factory=list)
    feedback: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)
    resposta_modelo: Optional[RespostaModelo] = None
    discrepancia: Optional[str] = None
    isr_score: float = Field(
        0.0,
        ge=0,
        le=1,
        description="Information Sufficiency Rating (0-1)"
    )
    tem_rastreamento: bool = Field(
        False,
        description="Resposta inclui rastreamento dos passos?"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "caso_id": "NEEDLE_001",
                "status": "PASS",
                "pontos": 4.5,
                "eh_acessivel": True,
                "isr_score": 0.92,
                "tem_rastreamento": True,
                "feedback": "Caso passou em todos os critérios"
            }
        }


class LoanPolicy(BaseModel):
    """Política de empréstimo"""
    policy_id: str
    titulo: str
    conteudo: str
    secoes: List[str] = Field(default_factory=list)
    vigencia_inicio: Optional[date] = None
    vigencia_fim: Optional[date] = None


class AuditResult(BaseModel):
    """Resultado agregado de uma auditoria"""
    auditoria_id: str
    data_inicio: datetime
    data_fim: Optional[datetime] = None
    total_casos: int = 0
    casos_pass: int = 0
    casos_fail: int = 0
    casos_partial: int = 0
    resultados: List[ResultadoAvaliacao] = Field(default_factory=list)
    metricas: Optional[Dict[str, Any]] = None
