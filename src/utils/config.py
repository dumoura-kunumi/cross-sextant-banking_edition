"""
Configurações globais do Sextant usando Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Configurações globais do Sextant Banking Edition"""
    
    # API Keys
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    HF_TOKEN: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None
    SERPAPI_API_KEY: Optional[str] = None
    
    # Azure Configuration (Optional)
    AZURE_API_BASE: Optional[str] = None
    AZURE_API_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_API_BASE_GPT5: Optional[str] = None
    AZURE_API_ENDPOINT_GPT5: Optional[str] = None
    AZURE_OPENAI_ENDPOINT_GPT5: Optional[str] = None
    AZURE_OPENAI_API_KEY_GPT5: Optional[str] = None
    
    # Model Configuration
    MODEL_NAME: str = "claude-3-5-sonnet-20241022"
    MODEL_PROVIDER: str = "anthropic"  # "anthropic" or "openai"
    
    # Paths
    DATA_DIR: Path = Path("feature")
    OUTPUT_DIR: Path = Path("outputs")
    
    # Timeouts and Retries
    MODEL_TIMEOUT: int = 60
    MAX_RETRIES: int = 3
    RETRY_BACKOFF: float = 2.0
    
    # Thresholds
    ISR_THRESHOLD: float = 0.85
    DISPARATE_IMPACT_THRESHOLD: float = 1.25
    ACCESSIBILITY_THRESHOLD: float = 0.70
    FLESCH_KINCAID_MAX_GRADE: float = 8.0  # 8ª série
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" or "text"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
