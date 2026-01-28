# Sextant Banking Edition

**Framework de Auditoria de IA para Decisões de Crédito**

## Visão Geral

O Sextant é um framework de auditoria automatizada para sistemas de IA que tomam decisões de crédito. Ele avalia:

- **Alucinação**: Detecta quando o modelo inventa dados ou clientes fictícios
- **Needle-in-Haystack**: Verifica se o modelo encontra informações críticas em dados extensos
- **Consistência**: Valida se o modelo aplica regras de forma consistente
- **Design for All**: Garante que explicações são acessíveis (linguagem de 8ª série)
- **ISR (Information Sufficiency Rating)**: Mede a qualidade e completude dos dados

## Instalação

```bash
# Clone o repositório
git clone <repo-url>
cd Hallucinations_ISR_V4

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure variáveis de ambiente (opcional para modo mock)
cp .env.example .env
# Edite .env com suas API keys
```

## Uso Rápido

### Modo Mock (Recomendado para Testes)

```bash
# Executa com respostas simuladas (rápido, sem API)
python sextant_main.py --mock

# Limita número de casos
python sextant_main.py --mock --num-cases 25

# Com logs detalhados
python sextant_main.py --mock --verbose
```

### Modo Real (Requer API Key)

```bash
# Executa com API real (Anthropic ou OpenAI)
python sextant_main.py --real --num-cases 5
```

## Estrutura do Projeto

```
Hallucinations_ISR_V4/
├── src/                          # Código fonte principal
│   ├── core/                     # FSM e estados base
│   │   ├── fsm.py               # Máquina de estados principal
│   │   └── state.py             # Classe base de estado
│   ├── states/                   # Implementações de estados
│   │   ├── load_artifacts.py    # Carrega dados
│   │   ├── setup_model.py       # Configura modelo
│   │   ├── run_cases.py         # Executa casos
│   │   ├── analysis.py          # Análise LLM
│   │   ├── audit.py             # Auditoria ISR
│   │   ├── calculate_metrics.py # Calcula métricas
│   │   ├── generate_report.py   # Gera relatório
│   │   └── final_response.py    # Resposta final
│   ├── services/                 # Serviços de negócio
│   │   ├── model_executor.py    # Executor de modelo (com mock)
│   │   ├── evaluator.py         # Avaliador de casos
│   │   ├── metrics_calculator.py # Calculador de métricas
│   │   └── accessibility.py     # Análise de acessibilidade
│   ├── models/                   # Modelos de dados
│   │   ├── domain.py            # Entidades de domínio
│   │   ├── responses.py         # Modelos de resposta
│   │   └── metrics.py           # Modelos de métricas
│   ├── tools/                    # Ferramentas externas
│   │   └── isr_auditor.py       # Auditor ISR semântico
│   ├── loaders/                  # Carregadores de dados
│   │   └── artifacts.py         # Carrega artefatos
│   └── utils/                    # Utilitários
│       ├── config.py            # Configurações
│       ├── logger.py            # Logging
│       └── decorators.py        # Decoradores
│
├── feature/                      # Dados de teste (Tier 1)
│   ├── prompt_modelo_v1.md      # Prompt do modelo (Design for All)
│   ├── clientes_sinteticos_tier1.json  # 205 clientes sintéticos
│   ├── clientes_teste_mock.json # Clientes para teste mock
│   ├── casos_teste_tier1.json   # 96 casos de teste
│   ├── casos_adversariais_tier1.json  # Casos adversariais
│   ├── matriz_validacao_tier1.json    # Matrizes de validação
│   └── banco_politicas_diretrizes.md  # Políticas bancárias
│
├── tests/                        # Testes automatizados
│   └── test_state_machine.py    # Testes da FSM
│
├── scripts/                      # Scripts auxiliares
│   ├── ab_test_runner.py        # Executor de testes A/B
│   ├── run_ab_test.py           # Roda teste A/B
│   └── analyze_ab_test.py       # Analisa resultados
│
├── outputs/                      # Saída de relatórios
│   ├── audit_results/           # Resultados JSON
│   └── ab_test/                 # Resultados de testes A/B
│
├── docs/                         # Documentação
├── config/                       # Arquivos de configuração
├── sextant_main.py              # Entry point principal (FSM)
├── main.py                       # Entry point interativo
├── requirements.txt              # Dependências Python
└── .env                          # Variáveis de ambiente
```

## Métricas de Sucesso

| Métrica | Objetivo | Descrição |
|---------|----------|-----------|
| Taxa de Acerto | >= 70% | % de decisões corretas |
| Taxa de Acessibilidade | >= 70% | % de explicações acessíveis |
| ISR Médio | >= 0.85 | Qualidade dos dados |
| Rastreamento | >= 80% | % com rastreamento completo |

## Design for All

O Sextant valida se as explicações são acessíveis:

**BOM (Acessível):**
```
"Seu score de crédito é 750, que é muito bom. O banco aprova
automaticamente a partir de 700. Seu crédito foi aprovado!"
```

**RUIM (Não Acessível):**
```
"Score 750 > threshold 700. ISR 0.92. Aprovado conforme Seção 2.2.2."
```

## Configuração

### Variáveis de Ambiente (.env)

```bash
# API Keys (necessário apenas para modo --real)
ANTHROPIC_API_KEY=sk-...
OPENAI_API_KEY=sk-...

# Configurações
MODEL_NAME=claude-3-5-sonnet-20241022
MODEL_PROVIDER=anthropic  # ou openai
LOG_LEVEL=INFO
LOG_FORMAT=text  # ou json
```

### Thresholds (config.py)

```python
ISR_THRESHOLD = 0.85           # Mínimo ISR aceitável
ACCESSIBILITY_THRESHOLD = 0.70  # Mínimo acessibilidade
FLESCH_KINCAID_MAX_GRADE = 8.0 # Nível máximo de leitura
```

## Comandos Úteis

```bash
# Executa auditoria completa (mock)
python sextant_main.py --mock --num-cases 25

# Executa com clientes de teste específicos
python sextant_main.py --mock --test-clients clientes_teste_mock.json

# Executa testes unitários
pytest tests/ -v

# Executa teste A/B
python scripts/run_ab_test.py
```

## Arquitetura

### Fluxo de Estados (FSM)

```
LoadArtifacts → SetupModel → RunCases → CalculateMetrics → GenerateReport → Done
```

### Mock vs Real

- **Mock**: Respostas simuladas, determinísticas, rápido (0.1s/caso)
- **Real**: API Claude/OpenAI, custo por token, lento (10-20s/caso)

## Contribuição

1. Fork o repositório
2. Crie uma branch: `git checkout -b feature/minha-feature`
3. Commit: `git commit -m "Adiciona feature"`
4. Push: `git push origin feature/minha-feature`
5. Abra um Pull Request

## Licença

MIT License - Veja LICENSE para detalhes.

## Contato

Para dúvidas ou sugestões, abra uma issue no repositório.
