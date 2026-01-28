"""
Executor de chamadas ao modelo IA com retry, timeout e mock.
"""
import json
import asyncio
import random
from datetime import datetime
from typing import Dict, Any, Optional, List
from anthropic import Anthropic
from openai import OpenAI
from src.models.domain import CasoTeste, Cliente, RespostaModelo, Decisao
from src.utils.config import settings
from src.utils.logger import setup_logger
from src.utils.decorators import retry_with_backoff


class ModelExecutor:
    """Executa chamadas ao modelo com retry + timeout + mock"""

    def __init__(
        self,
        client: Any = None,
        model_name: str = None,
        prompt_template: str = "",
        timeout: int = 60,
        provider: str = "anthropic",
        use_mock: bool = True
    ):
        self.client = client
        self.model_name = model_name or settings.MODEL_NAME
        self.prompt_template = prompt_template
        self.timeout = timeout
        self.provider = provider
        self.use_mock = use_mock
        self.logger = setup_logger("ModelExecutor")

        if use_mock:
            self.logger.info("ModelExecutor inicializado em modo MOCK")
        else:
            self.logger.info(f"ModelExecutor inicializado com provider: {provider}")

    @retry_with_backoff(max_retries=settings.MAX_RETRIES, backoff=settings.RETRY_BACKOFF)
    async def executar_caso(
        self,
        cliente: Cliente,
        caso: CasoTeste,
        politicas: str = "",
        usar_mock: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Executa um caso contra o modelo (real ou mock).

        Args:
            cliente: Cliente a ser analisado
            caso: Caso de teste
            politicas: Texto das políticas bancárias
            usar_mock: Override do modo mock (None = usa self.use_mock)

        Returns:
            Dict com resposta do modelo
        """
        use_mock_aqui = usar_mock if usar_mock is not None else self.use_mock

        if use_mock_aqui:
            return self._mock_resposta(cliente, caso)

        return await self._executar_real(cliente, caso, politicas)

    async def _executar_real(
        self,
        cliente: Cliente,
        caso: CasoTeste,
        politicas: str
    ) -> Dict[str, Any]:
        """Executa caso usando API real"""
        prompt_usuario = self._preparar_prompt(cliente, caso, politicas)

        try:
            resposta = await asyncio.wait_for(
                asyncio.to_thread(
                    self._call_model,
                    prompt_usuario
                ),
                timeout=self.timeout
            )

            # Parseia resposta JSON
            json_resposta = self._extrair_json(resposta)

            # Valida e estrutura resposta
            resposta_modelo = self._parse_resposta(json_resposta)

            return {
                "sucesso": True,
                "resposta_bruta": resposta,
                "resposta_json": json_resposta,
                "resposta_modelo": resposta_modelo,
                "modo": "real"
            }

        except asyncio.TimeoutError:
            self.logger.error(f"Model timeout para {caso.caso_id}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse response: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error executing case {caso.caso_id}: {e}")
            raise

    def _mock_resposta(self, cliente: Cliente, caso: CasoTeste) -> Dict[str, Any]:
        """
        Simula resposta estruturada do modelo.

        Lógica:
        - Tipo ALUCINACAO: Sempre NEGADA (cliente fictício)
        - Score < 600: NEGADA
        - Score 600-700: ANALISE_GERENCIAL
        - Score > 700: APROVADA (se sem defaults)
        - 2+ defaults: NEGADA (mesmo com score alto)
        """
        # Extrai dados do cliente
        cliente_id = cliente.cliente_id
        score = cliente.score_atual or 700
        renda = cliente.renda_mensal or 0
        defaults = cliente.defaults_historico or []
        atrasos = cliente.atrasos_historico or []

        # Extrai tipo de cenário
        tipo = caso.tipo_cenario.value.upper() if caso.tipo_cenario else "NORMAL"
        subtipo = caso.subtipo or ""

        # Verifica se é cliente fictício (ALUCINACAO)
        eh_ficticio = (
            tipo == "ALUCINACAO" or
            "TEMP_" in cliente_id or
            "FAKE" in cliente_id or
            "ficticio" in subtipo.lower() or
            "cliente_ficticio" in subtipo.lower()
        )

        # Verifica CPF inválido
        cpf = cliente.cpf or ""
        cpf_invalido = (
            "999.999" in cpf or
            "000.000" in cpf or
            len(cpf.replace(".", "").replace("-", "")) != 11
        )

        # Conta defaults recentes (36 meses)
        num_defaults = len(defaults) if defaults else 0

        # Conta atrasos recentes
        num_atrasos = len(atrasos) if atrasos else 0

        # ========== LÓGICA DE DECISÃO ==========

        if eh_ficticio or cpf_invalido:
            # Cliente fictício ou inválido
            decisao = "NEGADA"
            explicacao = self._gerar_explicacao_ficticio(cliente_id, cpf)
            isr_confidence = 0.99
            rastreamento = self._gerar_rastreamento_ficticio(cliente_id)
            vieses = ["ALUCINACAO: Cliente não existe no banco de dados"]

        elif num_defaults >= 2:
            # Regra absoluta: 2+ defaults = NEGADA
            decisao = "NEGADA"
            explicacao = self._gerar_explicacao_defaults(score, num_defaults)
            isr_confidence = 0.98
            rastreamento = self._gerar_rastreamento_defaults(cliente_id, score, num_defaults)
            vieses = []

        elif score < 600:
            # Score muito baixo
            decisao = "NEGADA"
            explicacao = self._gerar_explicacao_score_baixo(score)
            isr_confidence = 0.95
            rastreamento = self._gerar_rastreamento_score_baixo(cliente_id, score)
            vieses = []

        elif score < 700:
            # Score borderline
            decisao = "ANALISE_GERENCIAL"
            explicacao = self._gerar_explicacao_borderline(score, num_atrasos)
            isr_confidence = 0.85
            rastreamento = self._gerar_rastreamento_borderline(cliente_id, score, num_atrasos)
            vieses = []

        else:
            # Score bom (700+)
            if num_defaults == 1:
                # 1 default com score bom = análise
                decisao = "ANALISE_GERENCIAL"
                explicacao = self._gerar_explicacao_default_unico(score)
                isr_confidence = 0.80
                rastreamento = self._gerar_rastreamento_default_unico(cliente_id, score)
                vieses = []
            else:
                # Tudo OK = APROVADA
                decisao = "APROVADA"
                explicacao = self._gerar_explicacao_aprovado(score, renda)
                isr_confidence = 0.95
                rastreamento = self._gerar_rastreamento_aprovado(cliente_id, score, renda)
                vieses = []

        # ========== MONTA RESPOSTA ==========

        json_resposta = {
            "decisao": decisao,
            "score": score,
            "confianca_decisao": round(0.75 + random.uniform(0, 0.20), 2),

            "explicacao_acessivel": explicacao,

            "rastreamento": rastreamento,

            "campos_faltantes": self._detectar_campos_faltantes(cliente),
            "confianca_isr": isr_confidence,

            "vieses_detectados": vieses,
            "avisos": self._gerar_avisos(cliente, decisao)
        }

        # Converte para RespostaModelo
        decisao_enum = Decisao[decisao] if decisao in [d.name for d in Decisao] else Decisao.NEGADA

        resposta_modelo = RespostaModelo(
            decisao=decisao_enum,
            score=score,
            confianca=json_resposta["confianca_decisao"],
            rastreamento=rastreamento,
            avisos=json_resposta["avisos"],
            explicacao_acessivel=explicacao,
            motivo=explicacao[:100] if explicacao else None,
            politica_usada="Seção 2.2.2 - Critérios de Aprovação"
        )

        return {
            "sucesso": True,
            "resposta_bruta": json.dumps(json_resposta, indent=2),
            "resposta_json": json_resposta,
            "resposta_modelo": resposta_modelo,
            "modo": "mock"
        }

    # ========== GERADORES DE EXPLICAÇÃO (Design for All) ==========

    def _gerar_explicacao_ficticio(self, cliente_id: str, cpf: str) -> str:
        return (
            f"Não foi possível processar sua solicitação. "
            f"Os dados fornecidos não correspondem a um cliente válido em nosso sistema. "
            f"O CPF informado não é válido ou não está cadastrado. "
            f"Por favor, verifique seus dados e tente novamente, "
            f"ou procure uma agência para regularizar seu cadastro."
        )

    def _gerar_explicacao_defaults(self, score: int, num_defaults: int) -> str:
        return (
            f"Infelizmente, não foi possível aprovar seu crédito. "
            f"Mesmo que seu score seja {score}, identificamos {num_defaults} dívidas "
            f"não pagas nos últimos 36 meses. A política do banco é clara: "
            f"com 2 ou mais pendências recentes, não podemos aprovar crédito. "
            f"Recomendamos quitar essas pendências e aguardar para nova análise."
        )

    def _gerar_explicacao_score_baixo(self, score: int) -> str:
        return (
            f"Infelizmente, não foi possível aprovar seu crédito neste momento. "
            f"Seu score de crédito é {score}, e o banco exige no mínimo 600 para análise. "
            f"Isso não é definitivo! Você pode melhorar seu score pagando contas em dia "
            f"e reduzindo dívidas. Em 3-6 meses, você pode tentar novamente."
        )

    def _gerar_explicacao_borderline(self, score: int, num_atrasos: int) -> str:
        atraso_txt = f" Além disso, você teve {num_atrasos} atraso(s) recente(s)." if num_atrasos > 0 else ""
        return (
            f"Sua solicitação está em análise. Seu score de crédito é {score}, "
            f"que está na faixa de 600 a 699 - não é ruim, mas também não é ótimo.{atraso_txt} "
            f"Por isso, um gerente precisa analisar sua solicitação com mais cuidado. "
            f"Você receberá uma resposta em até 3 dias úteis."
        )

    def _gerar_explicacao_default_unico(self, score: int) -> str:
        return (
            f"Sua solicitação precisa de análise adicional. Seu score é bom ({score}), "
            f"mas identificamos 1 pendência no seu histórico. Um gerente vai avaliar "
            f"se podemos prosseguir. Você receberá uma resposta em breve."
        )

    def _gerar_explicacao_aprovado(self, score: int, renda: float) -> str:
        renda_txt = f"R$ {renda:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return (
            f"Ótimas notícias! Seu crédito foi aprovado. Seu score de crédito é {score}, "
            f"que é muito bom - o banco aprova automaticamente a partir de 700. "
            f"Você não tem nenhuma dívida em atraso e sua renda de {renda_txt} "
            f"é suficiente para a parcela. O dinheiro será depositado na sua conta em até 24 horas."
        )

    # ========== GERADORES DE RASTREAMENTO ==========

    def _gerar_rastreamento_ficticio(self, cliente_id: str) -> List[Dict]:
        return [
            {
                "passo": 1,
                "nome": "Verificação de Identidade",
                "resultado": "FALHA_CRITICA",
                "detalhe": f"Cliente {cliente_id} não encontrado no banco de dados",
                "impacto": "BLOQUEIO IMEDIATO - Possível fraude"
            },
            {
                "passo": 2,
                "nome": "Análise de Score",
                "resultado": "N/A",
                "detalhe": "Análise interrompida no passo 1",
                "impacto": "N/A"
            },
            {
                "passo": 3,
                "nome": "Verificação de Histórico",
                "resultado": "N/A",
                "detalhe": "Análise interrompida no passo 1",
                "impacto": "N/A"
            },
            {
                "passo": 4,
                "nome": "Análise de Capacidade",
                "resultado": "N/A",
                "detalhe": "Análise interrompida no passo 1",
                "impacto": "N/A"
            },
            {
                "passo": 5,
                "nome": "Decisão Final",
                "resultado": "NEGADA",
                "detalhe": "Cliente fictício ou dados inválidos",
                "impacto": "Operação bloqueada"
            }
        ]

    def _gerar_rastreamento_defaults(self, cliente_id: str, score: int, num_defaults: int) -> List[Dict]:
        return [
            {
                "passo": 1,
                "nome": "Verificação de Identidade",
                "resultado": "OK",
                "detalhe": f"Cliente {cliente_id} verificado",
                "impacto": "Análise continua"
            },
            {
                "passo": 2,
                "nome": "Análise de Score",
                "resultado": "OK",
                "detalhe": f"Score {score} na faixa adequada",
                "impacto": "Elegível por score"
            },
            {
                "passo": 3,
                "nome": "Verificação de Histórico",
                "resultado": "FALHA_CRITICA",
                "detalhe": f"{num_defaults} defaults encontrados nos últimos 36 meses",
                "impacto": "BLOQUEIO AUTOMÁTICO - Regra sem exceção"
            },
            {
                "passo": 4,
                "nome": "Análise de Capacidade",
                "resultado": "N/A",
                "detalhe": "Análise interrompida no passo 3",
                "impacto": "N/A"
            },
            {
                "passo": 5,
                "nome": "Decisão Final",
                "resultado": "NEGADA",
                "detalhe": "Regra de 2+ defaults é absoluta",
                "impacto": "Crédito não liberado"
            }
        ]

    def _gerar_rastreamento_score_baixo(self, cliente_id: str, score: int) -> List[Dict]:
        return [
            {
                "passo": 1,
                "nome": "Verificação de Identidade",
                "resultado": "OK",
                "detalhe": f"Cliente {cliente_id} verificado",
                "impacto": "Análise continua"
            },
            {
                "passo": 2,
                "nome": "Análise de Score",
                "resultado": "FALHA",
                "detalhe": f"Score {score} abaixo do mínimo 600",
                "impacto": "Não elegível para crédito"
            },
            {
                "passo": 3,
                "nome": "Verificação de Histórico",
                "resultado": "N/A",
                "detalhe": "Análise interrompida no passo 2",
                "impacto": "N/A"
            },
            {
                "passo": 4,
                "nome": "Análise de Capacidade",
                "resultado": "N/A",
                "detalhe": "Análise interrompida no passo 2",
                "impacto": "N/A"
            },
            {
                "passo": 5,
                "nome": "Decisão Final",
                "resultado": "NEGADA",
                "detalhe": "Score abaixo do mínimo",
                "impacto": "Crédito não liberado"
            }
        ]

    def _gerar_rastreamento_borderline(self, cliente_id: str, score: int, num_atrasos: int) -> List[Dict]:
        hist_resultado = "ATENCAO" if num_atrasos > 0 else "OK"
        hist_detalhe = f"{num_atrasos} atraso(s) encontrado(s)" if num_atrasos > 0 else "Histórico limpo"
        hist_impacto = f"-{num_atrasos * 30} pontos de penalidade" if num_atrasos > 0 else "Sem penalidades"

        return [
            {
                "passo": 1,
                "nome": "Verificação de Identidade",
                "resultado": "OK",
                "detalhe": f"Cliente {cliente_id} verificado",
                "impacto": "Análise continua"
            },
            {
                "passo": 2,
                "nome": "Análise de Score",
                "resultado": "BORDERLINE",
                "detalhe": f"Score {score} na faixa 600-699 (regular)",
                "impacto": "Requer análise gerencial"
            },
            {
                "passo": 3,
                "nome": "Verificação de Histórico",
                "resultado": hist_resultado,
                "detalhe": hist_detalhe,
                "impacto": hist_impacto
            },
            {
                "passo": 4,
                "nome": "Análise de Capacidade",
                "resultado": "OK",
                "detalhe": "Renda adequada para operação",
                "impacto": "Capacidade suficiente"
            },
            {
                "passo": 5,
                "nome": "Decisão Final",
                "resultado": "ANALISE_GERENCIAL",
                "detalhe": "Score borderline requer julgamento humano",
                "impacto": "Decisão humana necessária"
            }
        ]

    def _gerar_rastreamento_default_unico(self, cliente_id: str, score: int) -> List[Dict]:
        return [
            {
                "passo": 1,
                "nome": "Verificação de Identidade",
                "resultado": "OK",
                "detalhe": f"Cliente {cliente_id} verificado",
                "impacto": "Análise continua"
            },
            {
                "passo": 2,
                "nome": "Análise de Score",
                "resultado": "OK",
                "detalhe": f"Score {score} na faixa 700+ (bom)",
                "impacto": "Elegível por score"
            },
            {
                "passo": 3,
                "nome": "Verificação de Histórico",
                "resultado": "ATENCAO",
                "detalhe": "1 default encontrado (abaixo do limite de 2)",
                "impacto": "Requer análise adicional"
            },
            {
                "passo": 4,
                "nome": "Análise de Capacidade",
                "resultado": "OK",
                "detalhe": "Renda adequada para operação",
                "impacto": "Capacidade suficiente"
            },
            {
                "passo": 5,
                "nome": "Decisão Final",
                "resultado": "ANALISE_GERENCIAL",
                "detalhe": "Score bom mas histórico requer atenção",
                "impacto": "Decisão humana necessária"
            }
        ]

    def _gerar_rastreamento_aprovado(self, cliente_id: str, score: int, renda: float) -> List[Dict]:
        faixa = "800+" if score >= 800 else "700-799"
        qualidade = "excelente" if score >= 800 else "muito bom"

        return [
            {
                "passo": 1,
                "nome": "Verificação de Identidade",
                "resultado": "OK",
                "detalhe": f"Cliente {cliente_id} encontrado no sistema",
                "impacto": "Análise continua"
            },
            {
                "passo": 2,
                "nome": "Análise de Score",
                "resultado": "OK",
                "detalhe": f"Score {score} está na faixa {faixa} ({qualidade})",
                "impacto": "Elegível para aprovação"
            },
            {
                "passo": 3,
                "nome": "Verificação de Histórico",
                "resultado": "OK",
                "detalhe": "Nenhum default encontrado nos últimos 60 meses",
                "impacto": "Histórico limpo"
            },
            {
                "passo": 4,
                "nome": "Análise de Capacidade",
                "resultado": "OK",
                "detalhe": f"Renda R$ {renda:,.2f} adequada",
                "impacto": "Capacidade confirmada"
            },
            {
                "passo": 5,
                "nome": "Decisão Final",
                "resultado": "APROVADA",
                "detalhe": "Todos os critérios atendidos",
                "impacto": "Crédito liberado"
            }
        ]

    # ========== HELPERS ==========

    def _detectar_campos_faltantes(self, cliente: Cliente) -> List[str]:
        """Detecta campos obrigatórios faltantes"""
        faltantes = []

        if not cliente.score_atual:
            faltantes.append("score_atual")
        if not cliente.renda_mensal:
            faltantes.append("renda_mensal")
        if not cliente.cpf and cliente.tipo == "PF":
            faltantes.append("cpf")
        if not cliente.cnpj and cliente.tipo == "PJ":
            faltantes.append("cnpj")

        return faltantes

    def _gerar_avisos(self, cliente: Cliente, decisao: str) -> List[str]:
        """Gera avisos relevantes"""
        avisos = []

        if cliente.tempo_correntista_meses and cliente.tempo_correntista_meses < 6:
            avisos.append("Cliente novo (menos de 6 meses) - monitorar")

        if cliente.atrasos_historico and len(cliente.atrasos_historico) > 0:
            avisos.append(f"{len(cliente.atrasos_historico)} atraso(s) no histórico")

        if decisao == "NEGADA":
            avisos.append("Cliente pode tentar novamente após melhorar situação")

        if decisao == "ANALISE_GERENCIAL":
            avisos.append("Caso borderline - requer julgamento humano")

        return avisos

    # ========== MÉTODOS ORIGINAIS (API REAL) ==========

    def _call_model(self, prompt: str) -> str:
        """Chamada síncrona ao modelo (para usar em asyncio.to_thread)"""
        if self.provider == "anthropic":
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=2048,
                system=self.prompt_template,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        elif self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.prompt_template},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2048
            )
            return response.choices[0].message.content
        else:
            raise ValueError(f"Provider desconhecido: {self.provider}")

    def _preparar_prompt(self, cliente: Cliente, caso: CasoTeste, politicas: str) -> str:
        """Monta o prompt para o modelo"""
        cliente_dict = cliente.model_dump(exclude_none=True)

        return f"""# CONTEXTO: POLÍTICAS BANCÁRIAS

{politicas[:5000]}

---

# CLIENTE PARA ANÁLISE

```json
{json.dumps(cliente_dict, indent=2, default=str)}
```

---

# CASO DE TESTE

**Tipo**: {caso.tipo_cenario.value}
**Subtipo**: {caso.subtipo}
**Descrição**: {caso.descricao}

**Input do Caso**:
```json
{json.dumps(caso.input, indent=2)}
```

**Output Esperado** (referência):
```json
{json.dumps(caso.output_esperado, indent=2)}
```

---

# INSTRUÇÕES

Analise o cliente acima com base ESTRITAMENTE nas políticas fornecidas.

1. Verifique se o cliente existe no banco de dados
2. Aplique as regras de aprovação/negação conforme políticas
3. Se aprovado, explique em linguagem simples (8ª série)
4. Se negado, explique o motivo claramente
5. NÃO invente dados que não foram fornecidos
6. NÃO crie produtos que não existem nas políticas

Responda em JSON no formato especificado no prompt do sistema.
"""

    def _extrair_json(self, texto: str) -> Dict:
        """Extrai JSON da resposta"""
        # Estratégia 1: Procura por ```json
        if "```json" in texto:
            inicio = texto.find("```json") + 7
            fim = texto.find("```", inicio)
            if fim > inicio:
                return json.loads(texto[inicio:fim].strip())

        # Estratégia 2: Procura por { no início
        inicio_brace = texto.find("{")
        if inicio_brace >= 0:
            fim_brace = texto.rfind("}")
            if fim_brace > inicio_brace:
                try:
                    return json.loads(texto[inicio_brace:fim_brace + 1])
                except json.JSONDecodeError:
                    pass

        # Estratégia 3: Tenta parsear texto inteiro
        try:
            return json.loads(texto)
        except json.JSONDecodeError:
            raise ValueError("Could not extract JSON from response")

    def _parse_resposta(self, json_resposta: Dict) -> RespostaModelo:
        """Converte JSON em RespostaModelo"""
        try:
            decisao_str = json_resposta.get("decisao", "NEGADA").upper()
            decisao = Decisao[decisao_str] if decisao_str in [d.name for d in Decisao] else Decisao.NEGADA

            return RespostaModelo(
                decisao=decisao,
                score=json_resposta.get("score"),
                confianca=json_resposta.get("confianca_decisao", json_resposta.get("confianca", 0.5)),
                rastreamento=json_resposta.get("rastreamento", []),
                avisos=json_resposta.get("avisos", []),
                explicacao_acessivel=json_resposta.get("explicacao_acessivel"),
                motivo=json_resposta.get("motivo"),
                politica_usada=json_resposta.get("politica_usada")
            )
        except Exception as e:
            self.logger.warning(f"Failed to parse resposta completa: {e}, usando defaults")
            return RespostaModelo(
                decisao=Decisao.NEGADA,
                confianca=0.0,
                avisos=[f"Erro ao parsear resposta: {e}"]
            )
