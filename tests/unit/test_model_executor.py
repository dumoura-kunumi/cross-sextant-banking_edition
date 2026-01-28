"""
Unit tests for ModelExecutor mock functionality.
"""
import pytest
from src.services.model_executor import ModelExecutor
from src.models.domain import Cliente, CasoTeste, TipoCaso, TipoCliente


class TestModelExecutorMock:
    """Tests for mock response generation."""

    def setup_method(self):
        """Setup test fixtures."""
        self.executor = ModelExecutor(use_mock=True)

    def _create_cliente(self, cliente_id: str, score: int, defaults: int = 0) -> Cliente:
        """Create a test cliente."""
        defaults_list = [
            {"data_default": "2024-01-01", "valor": 1000}
            for _ in range(defaults)
        ]
        return Cliente(
            cliente_id=cliente_id,
            tipo=TipoCliente.PF,
            nome="Test Client",
            cpf="123.456.789-00",
            score_atual=score,
            renda_mensal=5000.0,
            defaults_historico=defaults_list if defaults > 0 else []
        )

    def _create_caso(self, tipo: TipoCaso = TipoCaso.ALUCINACAO) -> CasoTeste:
        """Create a test case."""
        return CasoTeste(
            caso_id="TEST_001",
            tipo_cenario=tipo,
            subtipo="test",
            descricao="Test case",
            input={"tipo": "PF"},
            output_esperado={"decisao": "NEGADA"}
        )

    def test_mock_aprovado_score_alto(self):
        """Test that high score gets APROVADA."""
        cliente = self._create_cliente("PF_001", score=780)
        caso = self._create_caso(TipoCaso.INCONSISTENCIA)

        resultado = self.executor._mock_resposta(cliente, caso)

        assert resultado["sucesso"] is True
        assert resultado["resposta_json"]["decisao"] == "APROVADA"
        assert resultado["resposta_json"]["confianca_isr"] >= 0.85
        assert len(resultado["resposta_json"]["explicacao_acessivel"]) > 50

    def test_mock_negado_score_baixo(self):
        """Test that low score gets NEGADA."""
        cliente = self._create_cliente("PF_002", score=450)
        caso = self._create_caso(TipoCaso.INCONSISTENCIA)

        resultado = self.executor._mock_resposta(cliente, caso)

        assert resultado["resposta_json"]["decisao"] == "NEGADA"
        assert "600" in resultado["resposta_json"]["explicacao_acessivel"]

    def test_mock_analise_gerencial_borderline(self):
        """Test that borderline score gets ANALISE_GERENCIAL."""
        cliente = self._create_cliente("PF_003", score=650)
        caso = self._create_caso(TipoCaso.INCONSISTENCIA)

        resultado = self.executor._mock_resposta(cliente, caso)

        assert resultado["resposta_json"]["decisao"] == "ANALISE_GERENCIAL"

    def test_mock_negado_multiplos_defaults(self):
        """Test that 2+ defaults gets NEGADA even with high score."""
        cliente = self._create_cliente("PF_004", score=850, defaults=2)
        caso = self._create_caso(TipoCaso.INCONSISTENCIA)

        resultado = self.executor._mock_resposta(cliente, caso)

        assert resultado["resposta_json"]["decisao"] == "NEGADA"
        assert "2" in resultado["resposta_json"]["explicacao_acessivel"]

    def test_mock_negado_cliente_ficticio(self):
        """Test that fictitious client gets NEGADA."""
        cliente = self._create_cliente("TEMP_FAKE_001", score=800)
        caso = self._create_caso(TipoCaso.ALUCINACAO)

        resultado = self.executor._mock_resposta(cliente, caso)

        assert resultado["resposta_json"]["decisao"] == "NEGADA"
        assert "ALUCINACAO" in str(resultado["resposta_json"]["vieses_detectados"])

    def test_mock_rastreamento_completo(self):
        """Test that response includes complete tracing."""
        cliente = self._create_cliente("PF_005", score=750)
        caso = self._create_caso(TipoCaso.INCONSISTENCIA)

        resultado = self.executor._mock_resposta(cliente, caso)

        rastreamento = resultado["resposta_json"]["rastreamento"]
        assert len(rastreamento) == 5
        assert rastreamento[0]["passo"] == 1
        assert rastreamento[4]["passo"] == 5

    def test_mock_explicacao_acessivel(self):
        """Test that explanation is accessible (Design for All)."""
        cliente = self._create_cliente("PF_006", score=720)
        caso = self._create_caso(TipoCaso.INCONSISTENCIA)

        resultado = self.executor._mock_resposta(cliente, caso)

        explicacao = resultado["resposta_json"]["explicacao_acessivel"]
        # Should use simple language
        assert "você" in explicacao.lower() or "seu" in explicacao.lower()
        # Should include score value
        assert "720" in explicacao
        # Should be long enough
        assert len(explicacao) >= 50
