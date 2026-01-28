"""
Validadores para JSON e Markdown.
"""
import json
from pathlib import Path
from typing import Dict, Any, List
from src.utils.logger import setup_logger


class JSONValidator:
    """Validador de arquivos JSON"""
    
    def __init__(self):
        self.logger = setup_logger("JSONValidator")
    
    def validate(self, path: Path, schema: Dict[str, Any] = None) -> bool:
        """
        Valida um arquivo JSON.
        
        Args:
            path: Caminho do arquivo
            schema: Schema opcional para validação
            
        Returns:
            True se válido
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Validação básica de estrutura
            if schema:
                return self._validate_schema(data, schema)
            
            return True
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in {path}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error validating {path}: {e}")
            return False
    
    def _validate_schema(self, data: Any, schema: Dict[str, Any]) -> bool:
        """Valida dados contra schema"""
        # Implementação básica - pode ser expandida
        required_keys = schema.get("required", [])
        for key in required_keys:
            if key not in data:
                self.logger.error(f"Missing required key: {key}")
                return False
        return True


class MarkdownValidator:
    """Validador de arquivos Markdown"""
    
    def __init__(self):
        self.logger = setup_logger("MarkdownValidator")
    
    def validate(self, path: Path, min_length: int = 100) -> bool:
        """
        Valida um arquivo Markdown.
        
        Args:
            path: Caminho do arquivo
            min_length: Tamanho mínimo esperado
            
        Returns:
            True se válido
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if len(content) < min_length:
                self.logger.warning(f"Markdown file {path} is too short ({len(content)} < {min_length})")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error validating {path}: {e}")
            return False
