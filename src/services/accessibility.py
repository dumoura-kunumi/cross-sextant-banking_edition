"""
Serviço de avaliação de acessibilidade (Design for All).
Usa Flesch-Kincaid para medir nível de leitura.
"""
from typing import Optional
from src.models.domain import RespostaModelo
from src.utils.logger import setup_logger
from src.utils.config import settings

try:
    import textstat
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False
    setup_logger("AccessibilityService").warning(
        "textstat não disponível. Instale com: pip install textstat"
    )


class AccessibilityService:
    """Avalia acessibilidade de explicações (Design for All)"""
    
    def __init__(self):
        self.logger = setup_logger("AccessibilityService")
        self.textstat_available = TEXTSTAT_AVAILABLE
    
    def avaliar_explicacao(
        self,
        explicacao: Optional[str]
    ) -> dict:
        """
        Avalia acessibilidade de uma explicação.
        
        Args:
            explicacao: Texto da explicação
            
        Returns:
            Dict com métricas de acessibilidade
        """
        if not explicacao or not explicacao.strip():
            return {
                "tem_explicacao": False,
                "nivel_leitura": None,
                "eh_acessivel": False,
                "tamanho": 0
            }
        
        explicacao = explicacao.strip()
        tamanho = len(explicacao)
        
        if not self.textstat_available:
            # Fallback: avaliação simples baseada em tamanho e palavras
            palavras = explicacao.split()
            palavras_medias = sum(len(p) for p in palavras) / len(palavras) if palavras else 0
            
            # Heurística simples
            eh_acessivel = tamanho >= 20 and tamanho <= 500 and palavras_medias < 8
            
            return {
                "tem_explicacao": True,
                "nivel_leitura": None,
                "eh_acessivel": eh_acessivel,
                "tamanho": tamanho,
                "palavras": len(palavras),
                "palavras_medias": palavras_medias,
                "metodo": "heuristica"
            }
        
        # Usa Flesch-Kincaid Grade Level
        try:
            nivel = textstat.flesch_kincaid_grade(explicacao)
            eh_acessivel = nivel <= settings.FLESCH_KINCAID_MAX_GRADE
            
            # Flesch Reading Ease (0-100, maior = mais fácil)
            facilidade = textstat.flesch_reading_ease(explicacao)
            
            return {
                "tem_explicacao": True,
                "nivel_leitura": nivel,
                "eh_acessivel": eh_acessivel,
                "facilidade_leitura": facilidade,
                "tamanho": tamanho,
                "palavras": len(explicacao.split()),
                "metodo": "flesch_kincaid"
            }
        except Exception as e:
            self.logger.warning(f"Erro ao calcular Flesch-Kincaid: {e}")
            return {
                "tem_explicacao": True,
                "nivel_leitura": None,
                "eh_acessivel": False,
                "tamanho": tamanho,
                "erro": str(e)
            }
    
    def avaliar_resposta(self, resposta: RespostaModelo) -> dict:
        """
        Avalia acessibilidade de uma resposta completa.
        
        Args:
            resposta: RespostaModelo
            
        Returns:
            Dict com métricas
        """
        explicacao = resposta.explicacao_acessivel
        resultado = self.avaliar_explicacao(explicacao)
        
        # Adiciona informações da resposta
        resultado["decisao"] = resposta.decisao.value
        resultado["tem_motivo"] = bool(resposta.motivo)
        resultado["tem_rastreamento"] = len(resposta.rastreamento) > 0
        
        return resultado
