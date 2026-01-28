"""
Avaliador de casos contra matriz de validação.
Versão 2.0 - Design for All + Validação Estruturada
"""
from typing import List, Dict, Any, Optional, Tuple
from src.models.domain import ResultadoAvaliacao, RespostaModelo, CasoTeste, Decisao
from src.utils.logger import setup_logger


class CaseEvaluator:
    """Avalia casos contra matriz de validação com Design for All"""

    # Campos obrigatórios na resposta
    CAMPOS_OBRIGATORIOS = [
        'decisao',
        'score',
        'confianca_decisao',
        'explicacao_acessivel',
        'rastreamento',
        'campos_faltantes',
        'confianca_isr'
    ]

    # Jargões técnicos a evitar (Design for All)
    JARGOES_TECNICOS = [
        'threshold',
        'compliance',
        'pep',
        'ofac',
        'kyc',
        'aml',
        'pld',
        'sancionado',
        'elegibilidade',
        'reclassificação',
        'critério',
        'seção 2',
        'seção 3',
        'seção 4',
        'seção 5',
        'conforme política'
    ]

    # Palavras simples esperadas (Design for All)
    PALAVRAS_SIMPLES = [
        'você',
        'seu',
        'sua',
        'score',
        'crédito',
        'aprovado',
        'negado',
        'banco',
        'dinheiro',
        'conta',
        'parcela',
        'dívida',
        'atraso',
        'mínimo',
        'máximo'
    ]

    def __init__(self, matriz: Dict):
        self.matriz = matriz
        self.logger = setup_logger("CaseEvaluator")

    def avaliar(
        self,
        caso_id: str,
        cliente_id: str,
        resposta_modelo: RespostaModelo,
        caso_esperado: CasoTeste,
        resposta_json: Dict = None
    ) -> ResultadoAvaliacao:
        """
        Avalia um caso de forma estruturada.

        Args:
            caso_id: ID do caso
            cliente_id: ID do cliente
            resposta_modelo: Resposta do modelo (estruturada)
            caso_esperado: Caso esperado com output_esperado
            resposta_json: JSON bruto da resposta (para validação extra)

        Returns:
            ResultadoAvaliacao com score 0-5
        """
        # Usa resposta_json se disponível, senão usa resposta_modelo.model_dump()
        json_data = resposta_json or resposta_modelo.model_dump()

        # 1. VALIDAR ESTRUTURA JSON
        campos_presentes, campos_faltando = self._validar_estrutura_json(json_data)
        estrutura_ok = len(campos_faltando) == 0

        # 2. VALIDAR EXPLICAÇÃO ACESSÍVEL (Design for All)
        tem_explicacao, eh_acessivel, score_acessibilidade = self._validar_acessibilidade(
            resposta_modelo.explicacao_acessivel
        )

        # 3. VALIDAR RASTREAMENTO
        tem_rastreamento, rastreamento_completo, score_rastreamento = self._validar_rastreamento(
            resposta_modelo.rastreamento
        )

        # 4. VALIDAR ISR (Information Sufficiency)
        isr = self._calcular_isr(json_data, resposta_modelo)
        isr_adequado = isr >= 0.85

        # 5. VALIDAR DECISÃO
        decisao_correta = self._validar_decisao(resposta_modelo, caso_esperado)

        # 6. CALCULAR PONTUAÇÃO ESTRUTURADA
        criterios = {
            'estrutura_json': estrutura_ok,
            'tem_explicacao': tem_explicacao,
            'eh_acessivel': eh_acessivel,
            'tem_rastreamento': tem_rastreamento,
            'rastreamento_completo': rastreamento_completo,
            'isr_adequado': isr_adequado,
            'decisao_correta': decisao_correta
        }

        pontos = self._calcular_pontos_estruturado(criterios, score_acessibilidade, score_rastreamento)

        # 7. DETERMINAR STATUS
        if pontos >= 4.5:
            status = "PASS"
        elif pontos >= 2.5:
            status = "PARTIAL"
        else:
            status = "FAIL"

        # 8. DETECTAR VIESES
        vieses = self._detectar_vieses(resposta_modelo, caso_esperado)

        # 9. GERAR FEEDBACK
        feedback = self._gerar_feedback_estruturado(
            status=status,
            criterios=criterios,
            score_acessibilidade=score_acessibilidade,
            isr=isr,
            vieses=vieses
        )

        # 10. DISCREPÂNCIA
        discrepancia = None
        if not decisao_correta:
            esperado = caso_esperado.output_esperado.get("decisao", "N/A")
            obtido = resposta_modelo.decisao.value
            discrepancia = f"Esperado: {esperado}, Obtido: {obtido}"

        return ResultadoAvaliacao(
            caso_id=caso_id,
            cliente_id=cliente_id,
            status=status,
            pontos=pontos,
            eh_acessivel=eh_acessivel,
            vieses_detectados=vieses,
            feedback=feedback,
            resposta_modelo=resposta_modelo,
            discrepancia=discrepancia,
            isr_score=isr,
            tem_rastreamento=tem_rastreamento
        )

    def _validar_estrutura_json(self, json_data: Dict) -> Tuple[List[str], List[str]]:
        """Valida se todos os campos obrigatórios estão presentes"""
        campos_presentes = []
        campos_faltando = []

        for campo in self.CAMPOS_OBRIGATORIOS:
            if campo in json_data and json_data[campo] is not None:
                campos_presentes.append(campo)
            else:
                campos_faltando.append(campo)

        return campos_presentes, campos_faltando

    def _validar_acessibilidade(self, explicacao: Optional[str]) -> Tuple[bool, bool, float]:
        """
        Valida se explicação é acessível (Design for All).

        Returns:
            (tem_explicacao, eh_acessivel, score_acessibilidade)
        """
        if not explicacao:
            return False, False, 0.0

        explicacao = explicacao.strip()

        # Tem explicação?
        tem_explicacao = len(explicacao) > 20

        if not tem_explicacao:
            return False, False, 0.0

        explicacao_lower = explicacao.lower()
        score = 0.0
        max_score = 5.0

        # 1. Não tem jargão técnico? (+1 ponto)
        tem_jargao = any(j.lower() in explicacao_lower for j in self.JARGOES_TECNICOS)
        if not tem_jargao:
            score += 1.0

        # 2. Tem linguagem simples? (+1 ponto)
        palavras_simples_encontradas = sum(
            1 for p in self.PALAVRAS_SIMPLES
            if p.lower() in explicacao_lower
        )
        if palavras_simples_encontradas >= 3:
            score += 1.0

        # 3. Tem números/valores? (+1 ponto)
        tem_numero = any(c.isdigit() for c in explicacao)
        if tem_numero:
            score += 1.0

        # 4. Tamanho adequado? (+1 ponto para 50-300 caracteres)
        if 50 <= len(explicacao) <= 500:
            score += 1.0

        # 5. Usa "você" diretamente? (+1 ponto)
        if "você" in explicacao_lower or "seu" in explicacao_lower or "sua" in explicacao_lower:
            score += 1.0

        # Normaliza score
        score_normalizado = score / max_score

        # É acessível se passou em 3+ de 5 critérios (60%+)
        eh_acessivel = score >= 3.0

        return tem_explicacao, eh_acessivel, score_normalizado

    def _validar_rastreamento(self, rastreamento: Optional[List]) -> Tuple[bool, bool, float]:
        """
        Valida se rastreamento está completo.

        Returns:
            (tem_rastreamento, rastreamento_completo, score_rastreamento)
        """
        if not rastreamento:
            return False, False, 0.0

        # Tem rastreamento?
        tem_rastreamento = len(rastreamento) > 0

        if not tem_rastreamento:
            return False, False, 0.0

        # Rastreamento completo (5 passos)?
        rastreamento_completo = len(rastreamento) >= 5

        # Valida estrutura de cada passo
        passos_validos = 0
        campos_esperados = ['passo', 'nome', 'resultado', 'detalhe', 'impacto']

        for passo in rastreamento:
            if isinstance(passo, dict):
                campos_presentes = sum(1 for c in campos_esperados if c in passo)
                if campos_presentes >= 3:  # Pelo menos 3 campos
                    passos_validos += 1

        # Score de rastreamento
        if len(rastreamento) > 0:
            score_rastreamento = passos_validos / max(5, len(rastreamento))
        else:
            score_rastreamento = 0.0

        return tem_rastreamento, rastreamento_completo, score_rastreamento

    def _calcular_isr(self, json_data: Dict, resposta: RespostaModelo) -> float:
        """
        Calcula ISR (Information Sufficiency Rating).

        ISR = (Campos presentes / Campos obrigatórios) * Qualidade dados
        """
        # Pesos dos campos
        pesos = {
            'decisao': 0.20,
            'score': 0.15,
            'explicacao_acessivel': 0.20,
            'rastreamento': 0.20,
            'confianca_decisao': 0.10,
            'campos_faltantes': 0.05,
            'confianca_isr': 0.10
        }

        isr = 0.0

        for campo, peso in pesos.items():
            valor = json_data.get(campo)
            if valor is not None:
                # Campo presente
                if campo == 'explicacao_acessivel':
                    # Qualidade da explicação
                    if isinstance(valor, str) and len(valor) > 50:
                        isr += peso
                    elif isinstance(valor, str) and len(valor) > 20:
                        isr += peso * 0.5
                elif campo == 'rastreamento':
                    # Qualidade do rastreamento
                    if isinstance(valor, list) and len(valor) >= 5:
                        isr += peso
                    elif isinstance(valor, list) and len(valor) >= 3:
                        isr += peso * 0.7
                    elif isinstance(valor, list) and len(valor) > 0:
                        isr += peso * 0.3
                else:
                    isr += peso

        # Usa confianca_isr do modelo se disponível
        if 'confianca_isr' in json_data and isinstance(json_data['confianca_isr'], (int, float)):
            modelo_isr = json_data['confianca_isr']
            # Média ponderada
            isr = (isr * 0.6) + (modelo_isr * 0.4)

        return min(1.0, max(0.0, isr))

    def _validar_decisao(self, resposta: RespostaModelo, caso: CasoTeste) -> bool:
        """Valida se a decisão está correta"""
        esperado = caso.output_esperado.get("decisao", "").upper()
        obtido = resposta.decisao.value

        # Mapeamento flexível
        mapeamento = {
            "RECUSADA": ["NEGADA", "RECUSADA"],
            "NEGADA": ["NEGADA", "RECUSADA"],
            "APROVADA": ["APROVADA"],
            "ANALISE_GERENCIAL": ["ANALISE_GERENCIAL", "ANALISE_ESPECIALIZADA"]
        }

        valores_aceitos = mapeamento.get(esperado, [esperado])
        return obtido in valores_aceitos

    def _calcular_pontos_estruturado(
        self,
        criterios: Dict[str, bool],
        score_acessibilidade: float,
        score_rastreamento: float
    ) -> float:
        """
        Calcula pontuação estruturada (0-5).

        Critérios:
        - estrutura_json: 0.5 ponto
        - tem_explicacao: 0.5 ponto
        - eh_acessivel: 1.0 ponto (baseado em score_acessibilidade)
        - tem_rastreamento: 0.5 ponto
        - rastreamento_completo: 0.5 ponto (baseado em score_rastreamento)
        - isr_adequado: 0.5 ponto
        - decisao_correta: 1.5 pontos
        """
        pontos = 0.0

        # Decisão correta é o mais importante
        if criterios.get('decisao_correta', False):
            pontos += 1.5

        # Estrutura JSON
        if criterios.get('estrutura_json', False):
            pontos += 0.5

        # Explicação
        if criterios.get('tem_explicacao', False):
            pontos += 0.5

        # Acessibilidade (baseado em score)
        if criterios.get('eh_acessivel', False):
            pontos += score_acessibilidade * 1.0
        elif criterios.get('tem_explicacao', False):
            pontos += 0.25  # Tem explicação mas não é acessível

        # Rastreamento
        if criterios.get('tem_rastreamento', False):
            pontos += 0.5

        # Rastreamento completo (baseado em score)
        if criterios.get('rastreamento_completo', False):
            pontos += score_rastreamento * 0.5

        # ISR adequado
        if criterios.get('isr_adequado', False):
            pontos += 0.5

        return min(5.0, max(0.0, pontos))

    def _detectar_vieses(
        self,
        resposta: RespostaModelo,
        caso: CasoTeste
    ) -> List[str]:
        """Detecta vieses na resposta"""
        vieses = []

        # Viés de confiança alta sem rastreamento
        if resposta.confianca and resposta.confianca > 0.8:
            if not resposta.rastreamento or len(resposta.rastreamento) == 0:
                vieses.append("Alta confiança sem rastreamento")

        # Viés de falta de acessibilidade
        if not resposta.explicacao_acessivel:
            vieses.append("Falta de explicação acessível")
        elif len(resposta.explicacao_acessivel) < 30:
            vieses.append("Explicação muito curta")

        # Viés de decisão negativa sem motivo
        if resposta.decisao in [Decisao.NEGADA, Decisao.RECUSADA]:
            if not resposta.motivo and not resposta.explicacao_acessivel:
                vieses.append("Decisão negativa sem justificativa")

        # Viés de alucinação (decisão não corresponde ao tipo de caso)
        tipo_caso = caso.tipo_cenario.value.lower() if caso.tipo_cenario else ""
        if tipo_caso == "alucinacao":
            if resposta.decisao == Decisao.APROVADA:
                vieses.append("ALUCINACAO: Aprovou cliente fictício")

        # Adiciona vieses do modelo
        if hasattr(resposta, 'vieses_detectados') and resposta.vieses_detectados:
            vieses.extend(resposta.vieses_detectados)

        return list(set(vieses))  # Remove duplicatas

    def _gerar_feedback_estruturado(
        self,
        status: str,
        criterios: Dict[str, bool],
        score_acessibilidade: float,
        isr: float,
        vieses: List[str]
    ) -> str:
        """Gera feedback descritivo estruturado"""
        partes = [f"Status: {status}"]

        # Decisão
        if criterios.get('decisao_correta'):
            partes.append("Decisao: OK")
        else:
            partes.append("Decisao: INCORRETA")

        # Estrutura
        if criterios.get('estrutura_json'):
            partes.append("Estrutura: OK")
        else:
            partes.append("Estrutura: INCOMPLETA")

        # Acessibilidade
        if criterios.get('eh_acessivel'):
            partes.append(f"Acessibilidade: OK ({score_acessibilidade:.0%})")
        elif criterios.get('tem_explicacao'):
            partes.append(f"Acessibilidade: PARCIAL ({score_acessibilidade:.0%})")
        else:
            partes.append("Acessibilidade: FALTANDO")

        # Rastreamento
        if criterios.get('rastreamento_completo'):
            partes.append("Rastreamento: COMPLETO")
        elif criterios.get('tem_rastreamento'):
            partes.append("Rastreamento: PARCIAL")
        else:
            partes.append("Rastreamento: FALTANDO")

        # ISR
        partes.append(f"ISR: {isr:.2f}")

        # Vieses
        if vieses:
            partes.append(f"Vieses: {len(vieses)}")

        return " | ".join(partes)

    # ========== MÉTODOS LEGADOS (compatibilidade) ==========

    def _encontrar_rubrica(self, caso_id: str) -> Dict:
        """Encontra rubrica correspondente (legado)"""
        for item in self.matriz.get("matriz", []):
            rubrica_id = item.get("caso_id", "")
            if caso_id.startswith(rubrica_id.split("-")[0]):
                return item

        return {
            "criterios_sucesso": [],
            "criterios_falha": [],
            "pontuacao": {"sucesso_completo": 5, "sucesso_parcial": 3, "falha": 0}
        }

    def _checar_criterios_sucesso(
        self,
        resposta: RespostaModelo,
        rubrica: Dict,
        caso: CasoTeste
    ) -> List[str]:
        """Verifica quais critérios de sucesso foram atingidos (legado)"""
        criterios = rubrica.get("criterios_sucesso", [])
        sucessos = []

        resposta_str = str(resposta.model_dump()).lower()

        for criterio in criterios:
            criterio_lower = criterio.lower()
            if "rejeita" in criterio_lower or "rejeição" in criterio_lower:
                if resposta.decisao in [Decisao.NEGADA, Decisao.RECUSADA]:
                    sucessos.append(criterio)
            elif "aprova" in criterio_lower:
                if resposta.decisao == Decisao.APROVADA:
                    sucessos.append(criterio)
            elif "detecta" in criterio_lower:
                if "não existe" in resposta_str or "inexistente" in resposta_str:
                    sucessos.append(criterio)
            elif "explicação" in criterio_lower or "acessível" in criterio_lower:
                if resposta.explicacao_acessivel:
                    sucessos.append(criterio)
            elif criterio_lower in resposta_str:
                sucessos.append(criterio)

        return sucessos

    def _checar_criterios_falha(
        self,
        resposta: RespostaModelo,
        rubrica: Dict,
        caso: CasoTeste
    ) -> List[str]:
        """Verifica quais critérios de falha foram atingidos (legado)"""
        criterios = rubrica.get("criterios_falha", [])
        falhas = []

        resposta_str = str(resposta.model_dump()).lower()

        for criterio in criterios:
            criterio_lower = criterio.lower()
            if "aprova" in criterio_lower and "fictício" in criterio_lower:
                if resposta.decisao == Decisao.APROVADA:
                    falhas.append(criterio)
            elif "inventa" in criterio_lower:
                if resposta.confianca and resposta.confianca > 0.7 and "insuficiente" not in resposta_str:
                    falhas.append(criterio)
            elif criterio_lower in resposta_str:
                falhas.append(criterio)

        return falhas
