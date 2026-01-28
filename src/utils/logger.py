"""
Logging estruturado com JSON para o Sextant.
"""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
from src.utils.config import settings


class JSONFormatter(logging.Formatter):
    """Formatter que produz logs em JSON estruturado"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata o log como JSON"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.name,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Adiciona campos extras se existirem
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data
        
        # Adiciona exception info se houver
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """Formatter tradicional para logs legíveis"""
    
    def __init__(self):
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )


def setup_logger(name: str, log_file: Optional[Path] = None, verbose: bool = False) -> logging.Logger:
    """
    Configura um logger com formatação estruturada.

    Args:
        name: Nome do logger (geralmente __name__)
        log_file: Arquivo opcional para salvar logs
        verbose: Se True, usa nível DEBUG

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)

    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    
    # Remove handlers existentes para evitar duplicação
    logger.handlers.clear()
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    
    if settings.LOG_FORMAT == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(TextFormatter())
    
    logger.addHandler(console_handler)
    
    # Handler para arquivo se especificado
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
    
    # Evita propagação para root logger
    logger.propagate = False
    
    return logger
