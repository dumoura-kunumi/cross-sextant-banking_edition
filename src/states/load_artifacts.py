"""
Estado: Carrega todos os artefatos do Tier 1.
"""
from pathlib import Path
from src.core.state import SextantState
from src.loaders.artifacts import ArtifactLoader
from src.states.setup_model import SetupModelState
from src.utils.config import settings


class LoadArtifactsState(SextantState):
    """Carrega artefatos necessários para auditoria"""
    
    async def execute(self, context):
        try:
            self.logger.info("Loading Tier 1 artifacts...")
            
            # Determina diretório de dados
            data_dir = context.get("data_dir", settings.DATA_DIR)
            if isinstance(data_dir, str):
                data_dir = Path(data_dir)
            
            loader = ArtifactLoader(data_dir=data_dir)
            
            # Carrega cada artefato
            context["politicas"] = loader.carregar_politicas()
            context["clientes"] = loader.carregar_clientes()
            context["casos"] = loader.carregar_casos_teste()
            context["prompt_template"] = loader.carregar_prompt_template()
            context["matriz_validacao"] = loader.carregar_matriz_validacao()
            context["casos_adversariais"] = loader.carregar_casos_adversariais()
            
            # Limita número de casos se especificado
            num_cases = context.get("num_cases")
            if num_cases and num_cases > 0:
                context["casos"] = context["casos"][:num_cases]
                self.logger.info(f"Limited to {num_cases} cases")
            
            self.logger.info(
                f"Loaded: {len(context['clientes'])} clients, "
                f"{len(context['casos'])} test cases, "
                f"{len(context['casos_adversariais'])} adversarial cases"
            )
            
            self._log_transition("SetupModelState", {
                "clientes_loaded": len(context["clientes"]),
                "casos_loaded": len(context["casos"])
            })
            
            return SetupModelState()
        
        except Exception as e:
            self._log_error(e, {"data_dir": str(context.get("data_dir"))})
            raise
