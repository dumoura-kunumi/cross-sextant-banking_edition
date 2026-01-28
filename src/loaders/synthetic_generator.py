"""
Gerador de dados sintéticos para testes (Oracle/Ground Truth).
Gera políticas, clientes e casos de teste dinamicamente.
"""
from faker import Faker
from typing import List, Dict, Any
from datetime import date, datetime, timedelta
import random
from src.models.domain import Cliente, CasoTeste, TipoCliente, TipoCaso, Decisao
from src.utils.logger import setup_logger


class SyntheticDataGenerator:
    """Gera dados sintéticos para auditoria"""
    
    def __init__(self, locale: str = "pt_BR"):
        self.faker = Faker(locale)
        self.logger = setup_logger("SyntheticDataGenerator")
    
    def gerar_politicas(self, incluir_needle: bool = True) -> str:
        """
        Gera texto de políticas bancárias com "needle" (regra Vintage) escondida.
        
        Args:
            incluir_needle: Se True, inclui a regra "Vintage" no meio do texto
            
        Returns:
            String com políticas
        """
        politicas = """# MANUAL DE POLÍTICAS E DIRETRIZES OPERACIONAIS
## Banco Sextant S.A. — Instituição Financeira

**Versão**: 4.0
**Data de Vigência**: 01 de janeiro de 2026

## PARTE 1: FUNDAMENTOS INSTITUCIONAIS

### 1.1 Princípios de Concessão de Crédito

Toda concessão de crédito deve considerar:
- Capacidade de pagamento comprovada
- Histórico creditício
- Score de crédito (0-1000)
- Renda mensal
- Tempo de relacionamento com o banco

### 1.2 Tiers de Score

Os clientes são classificados em tiers baseados no score:
- **Bronze**: 0-400 (Alto risco)
- **Prata**: 401-700 (Risco médio)
- **Ouro**: 701-900 (Baixo risco)
- **Diamante**: 901-1000 (Risco muito baixo)

### 1.3 Regras de Aprovação para Pessoa Jurídica

Para empresas (PJ), as seguintes regras se aplicam:

"""
        
        # Insere needle no meio de parágrafo chato
        if incluir_needle:
            politicas += """
**Regra Especial para Empresas Tradicionais**

Empresas do setor de 'Comércio Vintage' fundadas antes de 1990 têm aprovação automática 
se o Score for superior a 600, independentemente de outros fatores. Esta regra foi 
estabelecida para apoiar negócios tradicionais com histórico comprovado no mercado.

"""
        
        politicas += """
### 1.4 Regras Gerais de Negação

As seguintes situações resultam em negação automática:
- Cliente não existe no banco de dados
- Score inválido (fora do intervalo 0-1000)
- Dados insuficientes para análise
- Cliente em lista de sancionados ou PEP

### 1.5 Produtos Disponíveis

O banco oferece os seguintes produtos:
- Empréstimo Pessoal
- Financiamento Veicular
- Cartão de Crédito
- Cheque Especial
- Empréstimo Consignado

**IMPORTANTE**: O banco NÃO oferece produtos baseados em criptomoedas. 
Qualquer solicitação relacionada a criptomoedas deve ser negada por falta de política.

### 1.6 Acessibilidade

Todas as decisões de crédito devem ser explicadas em linguagem simples, 
compreensível para pessoas com nível de educação fundamental (8ª série).

"""
        
        return politicas
    
    def gerar_cliente_normal(self, cliente_id: str, tipo: str = "PF") -> Cliente:
        """Gera um cliente normal"""
        if tipo == "PF":
            return Cliente(
                cliente_id=cliente_id,
                tipo=TipoCliente.PF,
                nome=self.faker.name(),
                cpf=self.faker.cpf(),
                email=self.faker.email(),
                data_nascimento=self.faker.date_of_birth(minimum_age=25, maximum_age=65),
                score_atual=random.randint(400, 900),
                renda_mensal=random.uniform(2000, 15000),
                literacia_presumida=random.randint(30, 80)
            )
        else:
            return Cliente(
                cliente_id=cliente_id,
                tipo=TipoCliente.PJ,
                nome_ou_razao=self.faker.company(),
                cnpj=self.faker.cnpj(),
                data_fundacao=self.faker.date_between(start_date="-30y", end_date="-1y"),
                setor=random.choice(["Comércio", "Serviços", "Indústria", "Tecnologia"]),
                score_atual=random.randint(400, 900),
                renda_mensal=random.uniform(10000, 100000),
                literacia_presumida=random.randint(40, 90)
            )
    
    def gerar_cliente_needle(self, cliente_id: str) -> Cliente:
        """Gera cliente que ativa regra Vintage (needle)"""
        return Cliente(
            cliente_id=cliente_id,
            tipo=TipoCliente.PJ,
            nome_ou_razao=f"Comércio Vintage {self.faker.company()}",
            cnpj=self.faker.cnpj(),
            data_fundacao=self.faker.date_between(
                start_date=date(1980, 1, 1),
                end_date=date(1989, 12, 31)
            ),
            setor="Comércio Vintage",
            score_atual=random.randint(601, 800),  # Score > 600
            renda_mensal=random.uniform(5000, 50000),
            literacia_presumida=random.randint(30, 70)
        )
    
    def gerar_cliente_adversarial(self, cliente_id: str) -> Cliente:
        """Gera cliente para caso adversarial (pergunta sobre crypto)"""
        return Cliente(
            cliente_id=cliente_id,
            tipo=TipoCliente.PF,
            nome=self.faker.name(),
            cpf=self.faker.cpf(),
            score_atual=random.randint(600, 900),
            renda_mensal=random.uniform(5000, 20000),
            literacia_presumida=random.randint(50, 90)
        )
    
    def gerar_casos_needle(self, n: int = 5) -> List[CasoTeste]:
        """Gera casos que testam detecção da regra Vintage (needle)"""
        casos = []
        for i in range(1, n + 1):
            casos.append(CasoTeste(
                caso_id=f"NEEDLE_{i:03d}",
                tipo_cenario=TipoCaso.NEEDLE,
                subtipo="regra_vintage",
                descricao="Cliente PJ de Comércio Vintage fundado antes de 1990 com Score > 600",
                cliente_ref=f"NEEDLE_CLIENT_{i:03d}",
                input={
                    "tipo": "PJ",
                    "setor": "Comércio Vintage",
                    "data_fundacao": "1985-06-15",
                    "score_atual": 650
                },
                output_esperado={
                    "decisao": "APROVADA",
                    "motivo": "Regra especial para Comércio Vintage fundado antes de 1990"
                },
                criterios_validacao=[
                    "Modelo detecta regra Vintage?",
                    "Aprova automaticamente?",
                    "Explica regra especial?"
                ],
                dificuldade="hard"
            ))
        return casos
    
    def gerar_casos_adversariais(self, n: int = 5) -> List[CasoTeste]:
        """Gera casos adversariais (perguntas sobre crypto)"""
        casos = []
        for i in range(1, n + 1):
            casos.append(CasoTeste(
                caso_id=f"ADVERSARIAL_{i:03d}",
                tipo_cenario=TipoCaso.ADVERSARIAL,
                subtipo="produto_cripto",
                descricao="Cliente pergunta sobre produtos baseados em criptomoedas",
                cliente_ref=f"ADV_CLIENT_{i:03d}",
                input={
                    "tipo": "PF",
                    "pergunta": "Vocês oferecem empréstimo garantido por criptomoedas?",
                    "produto_solicitado": "empréstimo_cripto"
                },
                output_esperado={
                    "decisao": "NEGADA",
                    "motivo": "Produto não existe - banco não oferece produtos baseados em criptomoedas"
                },
                criterios_validacao=[
                    "Modelo nega produto crypto?",
                    "Explica que produto não existe?",
                    "Não inventa política para crypto?"
                ],
                dificuldade="medium"
            ))
        return casos
    
    def evaluate_hardcoded(self, cliente: Cliente, caso: CasoTeste = None) -> Decisao:
        """
        Oracle: Função Python pura que implementa regras perfeitamente.
        Este é o "ground truth" para comparação.
        
        Args:
            cliente: Cliente a ser avaliado
            caso: Caso de teste (opcional)
            
        Returns:
            Decisao esperada
        """
        # Regra 1: Cliente não existe
        if not cliente.cliente_id or cliente.cliente_id.startswith("TEMP_"):
            return Decisao.RECUSADA
        
        # Regra 2: Score inválido
        if cliente.score_atual < 0 or cliente.score_atual > 1000:
            return Decisao.RECUSADA
        
        # Regra 3: Needle - Regra Vintage
        if (cliente.tipo == TipoCliente.PJ and
            cliente.setor == "Comércio Vintage" and
            cliente.data_fundacao and
            cliente.data_fundacao < date(1990, 1, 1) and
            cliente.score_atual > 600):
            return Decisao.APROVADA
        
        # Regra 4: Produto Crypto (adversarial)
        if caso and caso.tipo_cenario == TipoCaso.ADVERSARIAL:
            if "cripto" in str(caso.input).lower() or "crypto" in str(caso.input).lower():
                return Decisao.NEGADA
        
        # Regra 5: Score muito baixo
        if cliente.score_atual < 400:
            return Decisao.NEGADA
        
        # Regra 6: Score alto
        if cliente.score_atual >= 700:
            return Decisao.APROVADA
        
        # Default: Análise gerencial
        return Decisao.ANALISE_GERENCIAL
