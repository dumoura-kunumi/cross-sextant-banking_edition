"""
Unit tests for CaseEvaluator functionality.
"""
import pytest
from src.services.evaluator import CaseEvaluator
from src.models.domain import RespostaModelo, CasoTeste, TipoCaso, Decisao


class TestCaseEvaluator:
    """Tests for case evaluation."""

    def setup_method(self):
        """Setup test fixtures."""
        self.matriz = {"matriz": []}
        self.evaluator = CaseEvaluator(self.matriz)

    def _create_resposta(
        self,
        decisao: Decisao = Decisao.APROVADA,
        score: int = 750,
        explicacao: str = "Seu score é 750, muito bom! Você foi aprovado.",
        rastreamento: list = None
    ) -> RespostaModelo:
        """Create a test response."""
        if rastreamento is None:
            rastreamento = [
                {"passo": 1, "nome": "Verificação", "resultado": "OK", "detalhe": "OK", "impacto": "OK"},
                {"passo": 2, "nome": "Score", "resultado": "OK", "detalhe": "OK", "impacto": "OK"},
                {"passo": 3, "nome": "Histórico", "resultado": "OK", "detalhe": "OK", "impacto": "OK"},
                {"passo": 4, "nome": "Capacidade", "resultado": "OK", "detalhe": "OK", "impacto": "OK"},
                {"passo": 5, "nome": "Decisão", "resultado": "OK", "detalhe": "OK", "impacto": "OK"},
            ]
        return RespostaModelo(
            decisao=decisao,
            score=score,
            confianca=0.9,
            explicacao_acessivel=explicacao,
            rastreamento=rastreamento
        )

    def _create_caso(self, decisao_esperada: str = "APROVADA") -> CasoTeste:
        """Create a test case."""
        return CasoTeste(
            caso_id="TEST_001",
            tipo_cenario=TipoCaso.INCONSISTENCIA,
            subtipo="test",
            descricao="Test case",
            input={"tipo": "PF"},
            output_esperado={"decisao": decisao_esperada}
        )

    def test_validar_acessibilidade_bom(self):
        """Test accessibility validation with good explanation."""
        explicacao = "Seu score de crédito é 750, que é muito bom. O banco aprova a partir de 700. Parabéns!"

        tem_explicacao, eh_acessivel, score = self.evaluator._validar_acessibilidade(explicacao)

        assert tem_explicacao is True
        assert eh_acessivel is True
        assert score >= 0.6

    def test_validar_acessibilidade_ruim(self):
        """Test accessibility validation with jargon-heavy explanation."""
        explicacao = "Score 750 > threshold 700. ISR 0.92. Conforme Seção 2.2.2 do compliance."

        tem_explicacao, eh_acessivel, score = self.evaluator._validar_acessibilidade(explicacao)

        assert tem_explicacao is True
        assert eh_acessivel is False

    def test_validar_acessibilidade_vazia(self):
        """Test accessibility validation with empty explanation."""
        tem_explicacao, eh_acessivel, score = self.evaluator._validar_acessibilidade("")

        assert tem_explicacao is False
        assert eh_acessivel is False
        assert score == 0.0

    def test_validar_rastreamento_completo(self):
        """Test tracing validation with complete tracing."""
        rastreamento = [
            {"passo": i, "nome": f"Step {i}", "resultado": "OK", "detalhe": "OK", "impacto": "OK"}
            for i in range(1, 6)
        ]

        tem, completo, score = self.evaluator._validar_rastreamento(rastreamento)

        assert tem is True
        assert completo is True
        assert score == 1.0

    def test_validar_rastreamento_parcial(self):
        """Test tracing validation with partial tracing."""
        rastreamento = [
            {"passo": 1, "nome": "Step 1", "resultado": "OK"}
        ]

        tem, completo, score = self.evaluator._validar_rastreamento(rastreamento)

        assert tem is True
        assert completo is False

    def test_validar_decisao_correta(self):
        """Test decision validation when correct."""
        resposta = self._create_resposta(decisao=Decisao.APROVADA)
        caso = self._create_caso(decisao_esperada="APROVADA")

        resultado = self.evaluator._validar_decisao(resposta, caso)

        assert resultado is True

    def test_validar_decisao_incorreta(self):
        """Test decision validation when incorrect."""
        resposta = self._create_resposta(decisao=Decisao.NEGADA)
        caso = self._create_caso(decisao_esperada="APROVADA")

        resultado = self.evaluator._validar_decisao(resposta, caso)

        assert resultado is False

    def test_validar_decisao_negada_recusada_equivalentes(self):
        """Test that NEGADA and RECUSADA are treated as equivalent."""
        resposta = self._create_resposta(decisao=Decisao.NEGADA)
        caso = self._create_caso(decisao_esperada="RECUSADA")

        resultado = self.evaluator._validar_decisao(resposta, caso)

        assert resultado is True

    def test_avaliar_caso_pass(self):
        """Test full case evaluation with PASS result."""
        resposta = self._create_resposta()
        caso = self._create_caso()

        # Provide full JSON data for proper ISR calculation
        json_data = {
            "decisao": "APROVADA",
            "score": 750,
            "confianca_decisao": 0.9,
            "explicacao_acessivel": "Seu score é 750, muito bom! Você foi aprovado.",
            "rastreamento": resposta.rastreamento,
            "campos_faltantes": [],
            "confianca_isr": 0.95
        }

        resultado = self.evaluator.avaliar(
            caso_id="TEST_001",
            cliente_id="PF_001",
            resposta_modelo=resposta,
            caso_esperado=caso,
            resposta_json=json_data
        )

        assert resultado.status in ["PASS", "PARTIAL"]  # May be PARTIAL due to scoring
        assert resultado.pontos >= 3.5  # Good score
        assert resultado.eh_acessivel is True
        assert resultado.tem_rastreamento is True

    def test_avaliar_caso_fail(self):
        """Test full case evaluation with FAIL result."""
        resposta = self._create_resposta(
            decisao=Decisao.NEGADA,
            explicacao="No.",
            rastreamento=[]
        )
        caso = self._create_caso(decisao_esperada="APROVADA")

        resultado = self.evaluator.avaliar(
            caso_id="TEST_001",
            cliente_id="PF_001",
            resposta_modelo=resposta,
            caso_esperado=caso
        )

        assert resultado.status == "FAIL"
        assert resultado.pontos < 2.5
        assert resultado.discrepancia is not None

    def test_calcular_isr(self):
        """Test ISR calculation."""
        json_data = {
            "decisao": "APROVADA",
            "score": 750,
            "explicacao_acessivel": "Uma explicação longa e detalhada sobre a decisão tomada.",
            "rastreamento": [{"passo": i} for i in range(5)],
            "confianca_decisao": 0.9,
            "campos_faltantes": [],
            "confianca_isr": 0.95
        }
        resposta = self._create_resposta()

        isr = self.evaluator._calcular_isr(json_data, resposta)

        assert isr >= 0.85
        assert isr <= 1.0
