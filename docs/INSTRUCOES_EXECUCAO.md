# 🚀 Instruções de Execução - Sextant Banking Edition

## Pré-requisitos

1. **Python 3.11+** instalado
2. **Chave de API** (Anthropic ou OpenAI)
3. **Artefatos de dados** em `feature/`

## Passo 1: Instalação

```bash
# Criar ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

## Passo 2: Configuração

```bash
# Copiar template de configuração
cp .env.example .env

# Editar .env com suas chaves
nano .env  # ou seu editor preferido
```

**Configuração mínima no `.env`:**
```env
# Escolha um provider
ANTHROPIC_API_KEY=sua_chave_aqui
# OU
OPENAI_API_KEY=sua_chave_aqui

MODEL_PROVIDER=anthropic
MODEL_NAME=claude-3-5-sonnet-20241022
```

## Passo 3: Verificar Artefatos

Certifique-se de que os seguintes arquivos existem em `feature/`:

- ✅ `banco_politicas_diretrizes.md`
- ✅ `clientes_sinteticos_tier1.json`
- ✅ `casos_teste_tier1.json`
- ✅ `matriz_validacao_tier1.json`
- ✅ `casos_adversariais_tier1.json` (opcional)
- ✅ `prompt_modelo_v1.md` (opcional - usa template padrão se não existir)

## Passo 4: Executar Auditoria

```bash
# Execução completa
python3 sextant_main.py

# Ou com Python
python sextant_main.py
```

## Passo 5: Analisar Resultados

Os relatórios serão gerados em `outputs/audit_results/`:

- **`audit_report_YYYYMMDD_HHMMSS.md`**: Relatório completo em Markdown
- **`audit_results_YYYYMMDD_HHMMSS.csv`**: Dados tabulares para análise
- **`audit_metrics_YYYYMMDD_HHMMSS.json`**: Métricas em JSON

## Exemplo de Saída

```
[INFO] Starting Sextant FSM execution
[INFO] Loading Tier 1 artifacts...
[INFO] Loaded: 205 clients, 96 test cases, 5 adversarial cases
[INFO] Setting up model client...
[INFO] Model connected successfully: claude-3-5-sonnet-20241022
[INFO] Starting test case execution...
[INFO] Executing case 1/96: ALCINACAO_001
...
[INFO] Metrics calculated: Taxa Acerto: 75.00%, ISR Médio: 0.870, Taxa Acessibilidade: 68.00%
[INFO] Generating audit report...
[INFO] ✅ Sextant completed successfully
[INFO] 📊 Report available at: outputs/audit_results/audit_report_20260125_143022.md
```

## Limitar Número de Casos (Testes)

Para testar com menos casos (útil para desenvolvimento):

Edite `sextant_main.py` e descomente:
```python
fsm.context["num_cases"] = 10  # Limita a 10 casos
```

## Troubleshooting

### Erro: "ANTHROPIC_API_KEY não configurada"
- Verifique se o arquivo `.env` existe
- Verifique se a chave está correta
- Certifique-se de que `python-dotenv` está instalado

### Erro: "FileNotFoundError: Políticas não encontradas"
- Verifique se os arquivos estão em `feature/`
- Verifique os nomes dos arquivos (case-sensitive)

### Erro: "ModuleNotFoundError"
- Execute `pip install -r requirements.txt`
- Verifique se está no ambiente virtual correto

### Timeout em chamadas de API
- Aumente `MODEL_TIMEOUT` no `.env`
- Verifique sua conexão com a internet
- Verifique limites de rate da API

## Próximos Passos

1. **Analisar relatório**: Abra o `.md` gerado
2. **Verificar métricas**: ISR > 0.85? Acessibilidade > 70%?
3. **Identificar vieses**: Há disparate impact?
4. **Iterar**: Ajuste prompts, políticas, ou casos de teste

## Suporte

Para questões ou problemas, consulte:
- `README_SEXTANT.md` para documentação completa
- Logs em `outputs/logs/` (se configurado)

---

**Boa auditoria! 🎯**
