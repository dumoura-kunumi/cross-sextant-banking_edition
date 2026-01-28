"""
Estado: Configura cliente do modelo IA.
"""
from anthropic import Anthropic
from openai import OpenAI
from src.core.state import SextantState
from src.states.run_cases import RunCasesState
from src.utils.config import settings
from src.utils.logger import setup_logger


class SetupModelState(SextantState):
    """Inicializa cliente do modelo IA"""
    
    async def execute(self, context):
        try:
            self.logger.info("Setting up model client...")
            
            provider = settings.MODEL_PROVIDER.lower()
            model_name = settings.MODEL_NAME
            
            # Inicializa cliente apropriado
            if provider == "anthropic":
                api_key = settings.ANTHROPIC_API_KEY
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY não configurada")
                
                context["model_client"] = Anthropic(api_key=api_key)
                context["model_provider"] = "anthropic"
                
            elif provider == "openai":
                api_key = settings.OPENAI_API_KEY
                if not api_key:
                    raise ValueError("OPENAI_API_KEY não configurada")
                
                context["model_client"] = OpenAI(api_key=api_key)
                context["model_provider"] = "openai"
            else:
                raise ValueError(f"Provider desconhecido: {provider}")
            
            context["model_name"] = model_name
            
            # Testa conexão com chamada simples
            self.logger.info(f"Testing connection to {model_name}...")
            
            if provider == "anthropic":
                response = context["model_client"].messages.create(
                    model=model_name,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Test"}]
                )
            else:
                response = context["model_client"].chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=10
                )
            
            self.logger.info(f"Model connected successfully: {model_name}")
            self._log_transition("RunCasesState", {
                "model": model_name,
                "provider": provider
            })
            
            return RunCasesState()
        
        except Exception as e:
            self._log_error(e)
            raise
