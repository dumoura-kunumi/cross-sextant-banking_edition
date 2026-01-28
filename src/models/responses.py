"""
Modelos de resposta do modelo IA.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from src.models.domain import Decisao


class ModelResponse(BaseModel):
    """Resposta bruta do modelo"""
    raw_text: str
    parsed_json: Optional[Dict[str, Any]] = None
    success: bool = True
    error: Optional[str] = None
    tokens_used: Optional[int] = None
    model_name: Optional[str] = None
