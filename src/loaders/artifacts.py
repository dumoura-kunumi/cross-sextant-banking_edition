"""
Carregador de artefatos do Tier 1.
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from src.models.domain import CasoTeste, Cliente
from src.utils.config import settings
from src.utils.logger import setup_logger


class ArtifactLoader:
    """Carrega todos os artefatos do Tier 1"""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or settings.DATA_DIR
        self.logger = setup_logger("ArtifactLoader")
    
    def carregar_politicas(self) -> Dict[str, str]:
        """
        Carrega banco_politicas_diretrizes.md
        
        Returns:
            Dict com markdown e path
        """
        path = self.data_dir / "banco_politicas_diretrizes.md"
        if not path.exists():
            raise FileNotFoundError(f"Políticas não encontradas: {path}")
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        self.logger.info(f"Loaded policies from {path} ({len(content)} chars)")
        return {
            "markdown": content,
            "path": str(path)
        }
    
    def carregar_clientes(self) -> List[Cliente]:
        """
        Carrega clientes_sinteticos_tier1.json
        
        Returns:
            Lista de objetos Cliente
        """
        path = self.data_dir / "clientes_sinteticos_tier1.json"
        if not path.exists():
            raise FileNotFoundError(f"Clientes não encontrados: {path}")
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        clientes = []
        for item in data.get("clientes", []):
            try:
                cliente = Cliente(**item)
                clientes.append(cliente)
            except Exception as e:
                self.logger.warning(f"Failed to parse cliente {item.get('cliente_id')}: {e}")
        
        self.logger.info(f"Loaded {len(clientes)} clientes from {path}")
        return clientes
    
    def carregar_casos_teste(self) -> List[CasoTeste]:
        """
        Carrega casos_teste_tier1.json
        
        Returns:
            Lista de objetos CasoTeste
        """
        path = self.data_dir / "casos_teste_tier1.json"
        if not path.exists():
            raise FileNotFoundError(f"Casos de teste não encontrados: {path}")
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        casos = []
        for item in data.get("casos", []):
            try:
                caso = CasoTeste(**item)
                casos.append(caso)
            except Exception as e:
                self.logger.warning(f"Failed to parse caso {item.get('caso_id')}: {e}")
        
        self.logger.info(f"Loaded {len(casos)} casos from {path}")
        return casos
    
    def carregar_prompt_template(self) -> str:
        """
        Carrega prompt_modelo_v1.md
        
        Returns:
            String com template do prompt
        """
        path = self.data_dir / "prompt_modelo_v1.md"
        if not path.exists():
            self.logger.warning(f"Prompt template não encontrado: {path}, usando template padrão")
            return self._get_default_prompt_template()
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        self.logger.info(f"Loaded prompt template from {path} ({len(content)} chars)")
        return content
    
    def carregar_matriz_validacao(self) -> Dict:
        """
        Carrega matriz_validacao_tier1.json
        
        Returns:
            Dict com matriz de validação
        """
        path = self.data_dir / "matriz_validacao_tier1.json"
        if not path.exists():
            raise FileNotFoundError(f"Matriz de validação não encontrada: {path}")
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.logger.info(f"Loaded validation matrix from {path}")
        return data
    
    def carregar_casos_adversariais(self) -> List[Dict]:
        """
        Carrega casos_adversariais_tier1.json
        
        Returns:
            Lista de casos adversariais
        """
        path = self.data_dir / "casos_adversariais_tier1.json"
        if not path.exists():
            self.logger.warning(f"Casos adversariais não encontrados: {path}")
            return []
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        casos = data.get("casos", [])
        self.logger.info(f"Loaded {len(casos)} adversarial cases from {path}")
        return casos
    
    def _get_default_prompt_template(self) -> str:
        """Template padrão caso arquivo não exista"""
        return """Você é um gerente de risco de crédito de um banco.

Sua função é analisar solicitações de crédito e tomar decisões baseadas ESTRITAMENTE nas políticas fornecidas.

REGRAS CRÍTICAS:
1. Use APENAS informações fornecidas no contexto. Não invente dados.
2. Se uma informação não estiver disponível, marque como "INSUFICIENTE" e negue.
3. Explique sua decisão em linguagem simples (nível 8ª série) para que qualquer pessoa entenda.
4. Se o cliente não existe no banco de dados, RECUSE imediatamente.
5. Não invente produtos que não existem nas políticas (ex: produtos baseados em criptomoedas).

FORMATO DE RESPOSTA (JSON):
{
  "decisao": "APROVADA" | "NEGADA" | "RECUSADA" | "ANALISE_GERENCIAL",
  "score": <0-1000>,
  "confianca": <0.0-1.0>,
  "motivo": "explicação técnica",
  "explicacao_acessivel": "explicação em linguagem simples para o cliente",
  "politica_usada": "seção da política usada",
  "avisos": ["lista de avisos"],
  "rastreamento": [{"secao": "...", "criterio": "..."}]
}
"""
