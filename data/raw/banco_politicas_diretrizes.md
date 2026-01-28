# MANUAL DE POLÍTICAS E DIRETRIZES OPERACIONAIS
## Banco Patriota S.A. — Instituição Financeira

**Versão**: 3.2  
**Data de Vigência**: 01 de março de 2024  
**Data da Última Revisão**: 15 de janeiro de 2026  
**Classificação**: Interno - Acesso Restrito  
**Responsável**: Diretoria de Compliance e Risco Operacional

---

## PARTE 1: FUNDAMENTOS INSTITUCIONAIS

### 1.1 Missão, Visão e Valores

**Missão**  
Ser uma instituição financeira responsável que promove inclusão financeira com segurança, inovação e sustentabilidade, servindo pessoas físicas, pequenas e médias empresas com produtos e serviços de qualidade.

**Visão**  
Ser o banco de confiança preferido para a classe média emergente e micro/pequenos empresários no Brasil nos próximos cinco anos.

**Valores Corporativos**
- **Integridade**: Cumprimento rigoroso de leis, regulações e padrões éticos
- **Prudência**: Gestão conservadora de riscos e alocação responsável de capital
- **Inclusão**: Acesso equitativo a serviços financeiros sem discriminação
- **Transparência**: Comunicação clara sobre produtos, taxas e riscos
- **Sustentabilidade**: Responsabilidade ambiental e social nas operações
- **Inovação Responsável**: Adoção de tecnologia dentro de marcos de segurança

### 1.2 Princípios de Conformidade

Todas as operações devem estar em conformidade com:
- Lei nº 4.595/1964 (Lei do Banco Central)
- Resolução CMN nº 4.657/2018 (Diretrizes de Prevenção ao Lavagem de Dinheiro)
- Resolução BCB nº 166/2022 (Framework de Responsabilidade por IA)
- Lei nº 12.965/2014 (Marco Civil da Internet)
- LGPD - Lei nº 13.709/2018 (Proteção de Dados Pessoais)
- Normas ISO 31000 (Gestão de Riscos)
- Código de Defesa do Consumidor

---

## PARTE 2: POLÍTICA DE CONCESSÃO DE CRÉDITO

### 2.1 Princípios Gerais de Concessão

Toda concessão de crédito (empréstimos, financiamentos, limite de cheque, cartões) deve considerar:

**2.1.1 Critérios Básicos Não-Negociáveis**
- Capacidade de pagamento comprovada
- Não ter qualquer restrição nos bancos de dados de inadimplência pública (SPC, SERASA) relacionada a crédito pessoal ou PJ nos últimos **60 meses**
- Possuir CPF ou CNPJ válido e regularizado
- Não estar incluído em lista de PEPs (Pessoas Politicamente Expostas) ou sanções internacionais
- Origem comprovável e legal dos recursos
- Estar maior de 18 anos (PF) ou regularmente constituído há mínimo 12 meses (PJ)

**2.1.2 Vedações Absolutas**
- Clientes com antecedentes criminais relacionados a fraude, estelionato ou crimes financeiros
- Clientes que apresentem padrões de comportamento indicativos de lavagem de dinheiro
- Clientes cujos beneficiários finais não possam ser identificados
- Operações que violem sanções internacionais (OFAC, UNSC, EU sanctions, etc.)

### 2.2 Scoring de Crédito

**2.2.1 Componentes de Pontuação**

O scoring de crédito é composto por cinco eixos principais:

| Eixo | Peso | Componentes |
|------|------|------------|
| **Histórico Creditício** | 40% | SPC/SERASA, atrasos, defaults, utilização de limite |
| **Capacidade Financeira** | 25% | Renda, patrimônio, fluxo de caixa (PJ) |
| **Tempo de Relacionamento** | 15% | Antiguidade de conta, produtos, estabilidade |
| **Estabilidade Profissional** | 15% | Tempo de emprego, setor, formalização |
| **Perfil Comportamental** | 5% | Transações, movimento de conta, padrões |

**2.2.2 Faixas de Score e Decisão**

```
Score 800-1000: APROVAÇÃO AUTOMÁTICA
  - Decisão: Automática via sistema
  - Documentação: Simplificada
  - Limite: Até R$ 500.000 (PF) / R$ 2.000.000 (PJ)
  - Tempo processamento: Até 24 horas

Score 700-799: APROVAÇÃO COM ANÁLISE
  - Decisão: Gerente de relacionamento + 1 analista
  - Documentação: Padrão (3 últimos contracheques + comprovante renda)
  - Limite: Até R$ 150.000 (PF) / R$ 500.000 (PJ)
  - Tempo processamento: 2-3 dias úteis

Score 650-699: ANÁLISE GERENCIAL OBRIGATÓRIA
  - Decisão: Gerente de relacionamento + diretor de agência (PF) ou gestor de PJ
  - Documentação: Completa (6 últimos contracheques, extratos, comprovante patrimônio)
  - Limite: Até R$ 50.000 (PF) / R$ 150.000 (PJ)
  - Tempo processamento: 5-7 dias úteis
  - Restrições: Não deve ser primeira concessão na instituição

Score 600-649: ANÁLISE ESPECIALIZADA
  - Decisão: Comitê de Risco (gerente + 2 analistas + diretor)
  - Documentação: Completa + referências + confirmação renda
  - Limite: Até R$ 20.000 (PF) / R$ 50.000 (PJ)
  - Tempo processamento: 10-15 dias úteis
  - Restrições: Exige pré-aprovação de comitê, análise comportamental aprofundada

Score < 600: RECUSA OU FILA DE ESPERA
  - Decisão: Recusa automática OU fila para reavaliação em 90 dias
  - Recomendação: Orientar cliente sobre melhorias necessárias
  - Exceção: Apenas com aprovação de diretor executivo com justificativa escrita
```

**2.2.3 Regras Específicas de Score**

- **Score 701-719 (Zona Cinzenta)**: Embora acima de 700, se cliente teve algum atraso nos últimos 12 meses, deve ser reclassificado para 650-699
- **Score Aumentado**: +50 pontos se cliente é correntista há mais de 2 anos com movimentação regular (mínimo 10 transações/mês)
- **Score Reduzido**: -100 pontos se cliente teve mais de 2 defaults NOS ÚLTIMOS 36 MESES (não incluir defaults com mais de 36 meses)
- **Score Setorial**: PJ de setores de risco (jogo, armas, bebidas alcoólicas acima de 40% vol) recebem -50 pontos
- **Score Temporal**: Score é válido por 30 dias. Após este período, nova consulta SPC/SERASA obrigatória

### 2.3 Análise de Renda e Capacidade de Pagamento

**2.3.1 Métodos de Comprovação Aceitos**

| Categoria | Métodos Aceitos | Documentação Obrigatória |
|-----------|-----------------|-------------------------|
| **Empregado Formal** | Contracheque + CTPS | 3 últimos contracheques + CTPS eletrônico |
| **Autônomo Registrado** | RPA/CCMEI/Imposto de Renda | Documento de registro + 6 últimos recibos + última declaração IR |
| **Empresário/PJ** | Faturamento comprovado | Balanço patrimonial + DRE + extrato conta PJ |
| **Aposentado** | Comprovante INSS/Privado | Contracheque de aposentadoria + documentação da fonte |
| **Aluguel/Royalties** | Contrato + comprovantes | Contrato registrado em cartório + 6 últimos comprovantes |
| **Investimentos** | Extrato corretora | Extrato dos últimos 3 meses + tipo de investimento |

**2.3.1.1 Documentação Falsificada**
- Qualquer suspeita de falsificação de documentação resulta em: recusa imediata, registro em banco de dados interno, reporte a autoridades competentes
- Padrão: Qualquer discrepância entre renda declarada e extratos deve ser investigada

**2.3.2 Renda Mínima**

- **Pessoa Física**: Renda mínima de 2 salários mínimos (R$ 3.044/mês em 2026)
- **Pessoa Jurídica**: Faturamento mínimo anual de R$ 360.000 (média R$ 30.000/mês)
- **Microempreendedor Individual (MEI)**: Faturamento mínimo anual de R$ 120.000

**2.3.3 Índice de Endividamento**

- **Máximo Permitido**: 40% da renda líquida pode ser comprometida com todas as dívidas (incluindo nova operação)
- **Cálculo**: (Nova parcela + Dívidas existentes) / Renda Líquida ≤ 40%
- **Exceção**: PJ com faturamento acima de R$ 5.000.000/ano: máximo 50%
- **Dívidas Consideradas**: Todas as operações de crédito, financiamentos, cartões, cheque especial

**Exemplo de Cálculo:**
```
Renda mensalmente: R$ 5.000
Limite de endividamento: R$ 2.000/mês
Dívidas existentes: R$ 800/mês (financiamento carro)
Disponível para nova operação: R$ 1.200/mês
Se solicita empréstimo com parcela de R$ 1.500/mês: NEGA
```

### 2.4 Análise de Inadimplência Histórica

**2.4.1 Critério de Default nos últimos 60 meses**

Uma ou mais ocorrências de default (atraso superior a 90 dias OU indicativo de não-intenção de pagar) nos últimos **60 meses corridos** resultam em:

- **Score automático máximo**: 600 (categoria Análise Especializada)
- **Análise adicional**: Verificar tipo de default, recuperação, comportamento pós-default
- **Tempo mínimo de espera**: 24 meses da resolução do default para considerar reclassificação

**2.4.2 Múltiplos Defaults**

- **2 ou mais defaults nos últimos 36 meses**: Recusa automática, sem exceção
- **1 default nos últimos 36 meses + 1 default entre 36-60 meses**: Score máximo 550

**2.4.3 Atrasos (menos de 90 dias)**

Atrasos de 30-90 dias são penalizados conforme:
- **1-2 atrasos nos últimos 24 meses**: -30 pontos por atraso
- **3+ atrasos nos últimos 24 meses**: Reclassificar para categoria imediatamente inferior + análise especializada
- **Atrasos acima de 6 meses**: Considerar como default

**2.4.4 Recuperação de Clientes**

Cliente que tinha default mas conseguiu recuperação completa (quitação + 24 meses sem negativação):
- Score aumentado em +100 pontos
- Pode passar de recusa automática para Análise Especializada
- Requer documentação comprovando fonte de recursos para quitação

### 2.5 Limite de Crédito e Produtos Específicos

**2.5.1 Determinação de Limite**

```
Limite = Menor entre:
  (a) Renda Mensal × Fator de Limite × Índice de Endividamento
  (b) Limite Máximo por Score
  (c) Limite do Produto
  (d) Limite Agregado por Pessoa/Grupo
```

**Fator de Limite por Produto:**
- Empréstimo Pessoal: Até 12x renda mensal
- Cheque Especial: Até 3x renda mensal
- Cartão de Crédito: Até 5x renda mensal
- Financiamento: Até 20x renda mensal (para bem durável)
- Desconto em Duplicatas (PJ): Até 40% do faturamento mensal

**2.5.2 Limite Agregado**

Cada pessoa física ou jurídica tem um limite agregado máximo de TODAS as operações:

| Categoria | Limite Máximo | Exceções |
|-----------|---------------|----------|
| PF - Score 800+ | R$ 500.000 | Apenas com aprovação diretor geral |
| PF - Score 700-799 | R$ 150.000 | Nenhuma |
| PF - Score 650-699 | R$ 50.000 | Com comitê |
| PF - Score < 650 | R$ 10.000 | Recusa padrão |
| PJ - Receita < R$ 1M/ano | R$ 100.000 | Comitê especializado |
| PJ - Receita R$ 1M-5M/ano | R$ 500.000 | Diretor de PJ |
| PJ - Receita > R$ 5M/ano | R$ 2.000.000 | Comitê diretoria |

**2.5.3 Cartão de Crédito**

Limite de Cartão = Menor entre:
- 5x renda mensal (limite máximo padrão)
- Limite agregado disponível
- Score mínimo 650 para primeira concessão

**Exceções de Score para Cartão:**
- Score 600-649 com comprovante de renda + análise gerencial: Limite reduzido a 2x renda
- Score < 600: Não é elegível para cartão de crédito

**2.5.4 Cheque Especial**

- Limite máximo: 3x renda comprovada
- Remuneração: Taxa média de mercado + 3% para inadimplência
- Score mínimo: 700 para primeira concessão
- Clientes com atraso nos últimos 12 meses: Cancelamento automático

### 2.6 Situações Especiais e Exceções

**2.6.1 Clientes Pessoa Física**

**Primeira Concessão em Banco:**
- Exige score mínimo de 650
- Limite máximo inicial: R$ 15.000 ou 3x renda (o que for menor)
- Documentação completa obrigatória
- Após 12 meses sem atraso, limite pode ser aumentado em até 50%

**Clientes com Histórico de Atraso (30-90 dias)**
- Limite reduzido em 30-50%
- Requer renda verificável de última fonte comprovada
- Se voltarem a atrasar nos próximos 12 meses, operação é cancelada

**Clientes Desempregados**
- Não são elegíveis para empréstimo pessoal
- Podem receber limite de cartão de crédito máximo R$ 5.000 SE tiverem renda alternativa comprovada
- Cheque especial é vedado

**Clientes Idosos (65+)**
- Mesmos critérios de score aplicam-se
- Limite máximo reduzido a 80% do permitido para score
- Exigir beneficiário legal se houver manifestação de vulnerabilidade

**2.6.2 Clientes Pessoa Jurídica**

**Empresas em Situação de Reestruturação**
- Com processo de recuperação judicial: Recusa automática
- Com processo de insolvência: Recusa automática
- Sem distrato/falência mas com recesso: Análise especializada + relatório de viabilidade

**Startups e Novas Empresas**
- Constituição há menos de 24 meses: Score reduzido em 150 pontos
- Constituição entre 24-36 meses: Score reduzido em 75 pontos
- Não elegível se: Sem faturamento comprovado OU sem demonstração de operação real

**Empresas Familiares**
- Se há mudança de sócios nos últimos 12 meses: Análise de continuidade operacional obrigatória
- Verificar ausência de conflitos societários

**2.6.3 Setores de Risco Elevado**

**Vedação Total:**
- Atividades ilícitas (tráfico, contrabando)
- Jogos de azar e apostas
- Fabricação de armas
- Atividades nucleares/armas químicas

**Restrição Severa (Limite reduzido em 60%):**
- Comércio de bebidas alcoólicas (acima de 40% vol)
- Tabacaria
- Bens de luxo (joias, arte)
- Agiotagem/títulos de crédito de risco

**Atenção Específica (Análise aprofundada em compliance):**
- Imóveis (avaliar origem de fundos para construção)
- Mineração (impacto ambiental)
- Agropecuária (verificar créditos rurais)
- Importação/Exportação (comprovar regularidade fiscal)

### 2.7 Processo de Aprovação

**2.7.1 Fluxo de Aprovação**

```
1. SUBMISSÃO
   ↓
2. VERIFICAÇÃO DOCUMENTAL
   └─ Documentos incompletos? → Retorna cliente
   ↓
3. CONSULTA SPC/SERASA
   └─ Restrição fatal? → Recusa imediata
   ↓
4. CÁLCULO DE SCORE
   ├─ Score ≥ 800 → Vai para APROVAÇÃO AUTOMÁTICA
   ├─ 700 ≤ Score < 800 → Vai para ANÁLISE GERENCIAL
   ├─ 650 ≤ Score < 700 → Vai para ANÁLISE ESPECIALIZADA
   └─ Score < 650 → Vai para COMITÊ DE RISCO
   ↓
5. ANÁLISE E APROVAÇÃO
   ↓
6. GERAÇÃO DE CONTRATO
   ↓
7. DESEMBOLSO
```

**2.7.2 Prazos de Aprovação**

| Tipo | Prazo Máximo | Ação se Vencer |
|------|-------------|----------------|
| Aprovação Automática | 1 dia útil | Comunicar cliente em até 24h |
| Análise Gerencial | 3 dias úteis | Apresentar justificativa de atraso |
| Análise Especializada | 7 dias úteis | Convocar comitê de risco |
| Comitê de Risco | 10 dias úteis | Retornar cliente com resposta |

**Prorrogação:**
- Máximo 5 dias úteis adicionais (via autorização de diretor)
- Ultrapassados 15 dias úteis: Devolução automática de documentos, cliente pode reaplicar

---

## PARTE 3: GESTÃO DE RISCO DE CRÉDITO

### 3.1 Monitoramento Pós-Concessão

**3.1.1 Frequência de Revisão**

Todos os clientes com operações ativas devem ser monitorados conforme:

```
Score 800+: Trimestral
Score 700-799: Bimestral
Score 650-699: Mensal
Score < 650: Quinzenal
Clientes em atraso: Semanal
Clientes em default: Diário
```

**3.1.2 Gatilhos de Revisão**

Reavaliação imediata (em até 48 horas) é obrigatória se:

- Novo atraso detectado (mesmo que pequeno)
- Pessoa aparece em nova negativação (SPC/SERASA)
- Alteração significativa de renda (redução > 30%)
- Movimento anormal em conta (saques massivos, transferências suspeitas)
- Falecimento do cliente (reclassificação para beneficiários)
- Mudança de setor ou ramo de atividade (PJ)
- Detecção em lista de PEPs ou sanções

### 3.2 Política de Cobrança e Inadimplência

**3.2.1 Procedimento de Atraso**

```
DIA 1-30 (Atraso Leve):
  → SMS de cobrança
  → Email de cobrança
  → Contato telefônico
  → SPC ainda não reporta

DIA 31-60 (Atraso Moderado):
  → Encaminhamento a call center de cobrança
  → Envio de carta de aviso
  → Possível redução de limite

DIA 61-90 (Atraso Grave):
  → Notificação formal em cartório (para PJ com dívida > R$ 50k)
  → Bloqueio de novas operações
  → Inclusão em SPC/SERASA (já está inserido no dia 91)
  → Envio a departamento de recuperação de crédito

DIA 91+ (Default):
  → Posição é reportada como default
  → Possível encaminhamento para cobrança judicial
  → Renegociação com descontos de até 30% (com aprovação de diretor)
  → Possível securitização em fundo de investimento
```

**3.2.2 Renegociação**

Clientes em atraso de 31-90 dias podem ser oferecidos:
- Reestruturação de dívida (alongamento de prazo em até 36 meses adicionais)
- Redução de taxa de juros (máximo 30% de desconto)
- Parcelamento de atraso (em até 12 parcelas)

**Condições:**
- Exigir renda atualizada comprovada
- Apenas com aprovação de gerente de relacionamento
- Cliente não pode ter tido renegociação nos últimos 12 meses

**3.2.3 Cancelamento de Operação**

Cancelamento automático de produtos ocorre em:
- Atraso superior a 120 dias em qualquer produto
- Inclusão em SPC/SERASA por mais de uma operação
- Terceiro default em 60 meses
- Detecção de fraude
- Morte do cliente (PF)

---

## PARTE 4: CONFORMIDADE E COMPLIANCE

### 4.1 Prevenção de Lavagem de Dinheiro (PLD)

**4.1.1 Devida Diligência Simplificada**

Aplicável a: Clientes de baixo risco (score 800+, renda < R$ 3.000/mês, operações < R$ 10.000)

**Documentação:**
- CPF ou CNPJ válido
- Comprovante de endereço (até 3 meses)
- Verificação SPC/SERASA

**4.1.2 Devida Diligência Padrão**

Aplicável a: Maioria dos clientes

**Documentação:**
- Identidade válida
- CPF/CNPJ
- Comprovante de endereço
- Comprovante de renda/patrimônio
- Formulário de informação do cliente (PEP, origem de fundos)
- Consulta em listas de sanções

**4.1.3 Devida Diligência Intensificada (Enhanced Due Diligence)**

Obrigatória para:
- Clientes em lista de PEPs
- Clientes com operações > R$ 500.000
- Clientes de jurisdições de alto risco
- Empresas sem identificação clara de beneficiário final
- Operações com origem de fundos não-clara

**Documentação Adicional:**
- Documentação de beneficiários finais (até UBO - Ultimate Beneficial Owner)
- Verificação de patrimônio via Receita Federal
- Entrevista presencial obrigatória
- Análise de origem de fundos
- Verificação em listas internacionais (OFAC, UNSC, EU)

**4.1.4 Reporte Obrigatório**

Qualquer suspeita de atividade suspeita deve ser reportada imediatamente a:
1. Gerência de Compliance
2. Coaf (Conselho de Atividades Financeiras)
3. Polícia Federal (se suspeita de crime)

Documentação de reporte deve ser mantida por 5 anos.

### 4.2 Pessoa Politicamente Exposta (PEP)

**4.2.1 Definição**

Pessoa que exerce, ou exerceu nos últimos 5 anos, função pública relevante:
- Presidente, vice-presidente
- Senadores, deputados
- Ministros, secretários de estado
- Autoridades judiciárias/policiais de nível superior
- Executivos de empresas estatais
- Dirigentes de partidos políticos

**4.2.2 Procedimento para PEPs**

- Rejeição automática EXCETO com aprovação de diretor executivo
- Devida diligência intensificada obrigatória
- Monitoramento mensal de transações
- Limite de operação reduzido em 70%
- Consulta em listas internacionais de sanções obrigatória

---

## PARTE 5: PROTEÇÃO DE DADOS E PRIVACIDADE

### 5.1 Coleta e Tratamento de Dados Pessoais

**5.1.1 Princípios LGPD**

Toda coleta de dados pessoais deve respeitar:
- **Finalidade específica**: Dados coletados apenas para análise de crédito
- **Necessidade**: Coletar apenas o essencial
- **Transparência**: Informar cliente sobre o que será coletado
- **Segurança**: Dados criptografados em trânsito e repouso
- **Retenção**: Deletar dados após 5 anos da operação encerrada

**5.1.2 Compartilhamento de Dados**

Dados podem ser compartilhados apenas com:
- SPC, SERASA (para atualizações de crédito)
- BCB (para aplicação de regulações)
- Órgãos reguladores (BCB, CVM, COAF)
- Órgãos de inteligência (via autorização judicial)

**Vedado:**
- Vender dados para terceiros
- Usar dados para marketing sem consentimento explícito
- Compartilhar com agências de score privadas sem consentimento

### 5.2 Sigilo Bancário e Direitos do Cliente

**5.2.1 Direitos Garantidos**

- Acesso a informações sobre sua operação (em até 5 dias úteis)
- Conhecer score de crédito e fatores de rejeição (se negada)
- Rectificação de dados incorretos
- Exclusão de dados após 5 anos da operação

**5.2.2 Denúncia e Reclamações**

Cliente pode apresentar reclamação a:
1. Gerente de relacionamento (resposta em 5 dias)
2. Ouvidoria do Banco (resposta em 10 dias)
3. Banco Central (se não satisfeito com resposta)

---

## PARTE 6: OPERAÇÕES E TRANSAÇÕES

### 6.1 Limites Operacionais por Tipo

**6.1.1 Transferências Eletrônicas**

| Tipo | Limite Diário | Limite Mensal | Aprovação |
|------|---------------|---------------|-----------|
| TED (para bancos) | Sem limite | Sem limite | Automática |
| DOC (lento) | Sem limite | Sem limite | Automática |
| PIX | R$ 10.000 | R$ 100.000 | Automática |
| PIX para conta não-cadastrada | R$ 1.000 | R$ 10.000 | Automática |
| Transferência Internacional | R$ 50.000 | Sem limite* | Análise compliance |

*Acima de USD 10.000 equivalentes requer análise de origem de fundos

**6.1.2 Saques**

- Limite diário: Até saldo disponível
- Saques acima de R$ 10.000: Cliente deve avisar com 24h antecedência
- Saques acima de R$ 50.000: Deve ser feito cheque de gerência (em até 2 dias)

### 6.2 Fraude e Segurança

**6.2.1 Detecção de Padrões Anormais**

Sistema deve bloquear/alertar se:
- Transferência 5x acima da média mensal do cliente
- 3 transferências para contas diferentes em 1 hora
- Saque/transferência durante madrugada (00h-06h) para cliente que nunca fez
- Movimentação em múltiplos bancos no mesmo dia
- PIX para conta recém-criada (< 30 dias) com valor > R$ 5.000

**6.2.2 Detecção de Fraude em Crédito**

Suspeita de fraude em concessão de crédito deve resultar em:
1. Congelamento imediato da operação
2. Análise forense de documentos
3. Reporte a autoridades
4. Possível anulação de contrato

---

## PARTE 7: PRODUTOS E SERVIÇOS

### 7.1 Conta Corrente Pessoa Física

**Pré-requisitos:**
- Maior de 18 anos
- CPF válido
- Comprovante de endereço
- Sem restrição de contas (não pode ter mais de 3 contas simultâneas no grupo)

**Tarifas:**
- Abertura: Gratuita
- Manutenção: Gratuita (com mínimo 2 movimentações/mês) ou R$ 15/mês
- Cheque devolvido: R$ 50/devolução

**Limite de Cheque Especial:**
- Máximo 3x renda comprovada
- Juros: Taxa média de mercado + 3%
- Cancelamento automático se atraso > 30 dias

### 7.2 Conta Corrente Pessoa Jurídica

**Pré-requisitos:**
- CNPJ ativo e regularizado
- 12 meses de funcionamento mínimo
- Inscrição municipal/estadual ativa
- Verificação de beneficiários

**Tarifas:**
- Abertura: R$ 500
- Manutenção: R$ 100/mês
- DOC: R$ 5
- TED: R$ 10

**Limite de Cheque Especial:**
- Máximo 30% do faturamento mensal comprovado
- Juros: Taxa média de mercado + 2%

### 7.3 Empréstimo Pessoal

**Características:**
- Taxa média: 18-25% a.a. (varia conforme score)
- Prazo: 12-60 meses
- Sem garantia real
- Documentação: Contracheques + CPF + endereço

**Restrições por Score:**
```
Score 800+: Taxa 18%, até R$ 500k, 60 meses
Score 700-799: Taxa 20%, até R$ 150k, 48 meses
Score 650-699: Taxa 22%, até R$ 50k, 36 meses
Score 600-649: Taxa 25%, até R$ 20k, 24 meses
```

### 7.4 Financiamento Imóvel

**Pré-requisitos:**
- Entrada mínima: 20% do valor do imóvel
- Score mínimo: 700
- Não ter defaults nos últimos 60 meses
- Renda mínima: 3x a parcela mensal
- Prazo máximo: 360 meses (30 anos)
- Simulação obrigatória com TAC, IOF e seguro

**Aprovação:**
- Análise gerencial obrigatória
- Avaliação do imóvel por perito independente
- Seguro habitacional obrigatório
- Certidão de regularidade do imóvel
- Pesquisa de ônus (para garantia hipotecária)

### 7.5 Cartão de Crédito

**Tipos:**

| Tipo | Score Mín | Limite Máx | Taxa Juros | Taxa Anuidade |
|------|-----------|-----------|-----------|--------------|
| Básico | 650 | 5k | 25% a.m. | Gratuita |
| Gold | 750 | 20k | 22% a.m. | R$ 120/ano |
| Platinum | 800 | 50k | 18% a.m. | R$ 250/ano |

**Regras de Utilização:**
- Limite disponível = Limite total - Saldo devedor anterior
- Fatura mínima: Pelo menos 5% da fatura ou R$ 100 (o maior)
- Programa de pontos: 1 ponto por real gasto (resgate em pontos)
- Cashback: 0,5% em compras (eletrônico) / 0,25% (crédito parcelado)

**Cancelamento:**
- Cliente solicita e aguarda confirmação em 15 dias
- Automático se não utilizado por 12 meses (aviso prévio via SMS)
- Automático se pagamento em atraso > 60 dias

---

## PARTE 8: ATENDIMENTO AO CLIENTE

### 8.1 Princípios de Atendimento

Todo atendimento deve ser:
- **Respeitoso**: Sem discriminação de qualquer tipo
- **Claro**: Evitar jargão financeiro sem explicar
- **Rápido**: Resposta em máximo 15 minutos presencialmente
- **Resolutivo**: Atender no primeiro contato sempre que possível
- **Documentado**: Registrar interação no sistema

### 8.2 Tempo de Atendimento

| Tipo de Atendimento | Tempo Máximo |
|-------------------|-------------|
| Atendimento Presencial | 15 minutos |
| Ligação Telefônica | 5 minutos + resolução |
| Email | Resposta em 24h |
| Redes Sociais | Resposta em 4h |
| Reclama Aqui | Resposta em 48h |

### 8.3 Acessibilidade

**Obrigatório:**
- Rampa de acesso (ou elevador) para agências
- Caixa de atendimento adaptado para PCD
- Atendimento com intérprete de LIBRAS (sob agendamento)
- Documentos em fonte maior (tamanho 14+) ou braile

### 8.4 Educação Financeira

Todas as agências devem oferecer:
- Workshop mensal de educação financeira (gratuito)
- Orientação de planejamento (até 3 sessões/ano por cliente)
- Material de educação financeira (cartilhas, vídeos)

---

## PARTE 9: SEGURANÇA E PREVENÇÃO DE FRAUDE

### 9.1 Autenticação e Acesso

**9.1.1 Canais de Atendimento**

| Canal | Autenticação | Limite de Operação |
|-------|-------------|-------------------|
| Agência Física | Documento + Biometria | Sem limite |
| ATM | Cartão + Senha | R$ 5.000/dia |
| Internet Banking | CPF + Senha + Token | R$ 10.000/dia (TED) |
| App Mobile | Biometria | R$ 5.000/dia (PIX) |
| Telefone | Validação de dados | Consultas apenas |

**9.1.2 Trocar Senha**

- Mínimo a cada 90 dias (para operações de alto risco)
- Senha deve ter: Mínimo 8 caracteres, letras + números + símbolos
- Não pode reutilizar últimas 5 senhas

### 9.2 Criptografia de Dados

**Em Trânsito:**
- TLS 1.2 mínimo (obrigatório desde 2024)
- 256-bit encryption para dados sensíveis

**Em Repouso:**
- AES-256 para informações PII
- Tokenização de cartões

### 9.3 Identificação de Fraude

**9.3.1 Sinais de Alerta**

Sistema deve bloquear e revisar se:
- Cliente tenta criar múltiplas contas com documentos diferentes
- Email de cadastro é disposable/temporário
- Número de telefone é VoIP
- Endereço não corresponde ao histórico
- Documentação com sinais de falsificação

**9.3.2 Responsabilidade por Fraude**

- **Fraude externa** (roubo de dados): Banco responsável, cliente isento
- **Fraude interna** (funcionário): Banco responsável, cliente isento
- **Negligência do cliente** (compartilhou senha): Cliente responsável por 50% da perda

---

## PARTE 10: SANÇÕES INTERNACIONAIS E RESTRIÇÕES

### 10.1 Listas de Sanção

**Consulta Obrigatória em:**
- OFAC (Office of Foreign Assets Control - EUA)
- UNSC (Nações Unidas)
- EU Sanctions
- Listas nacionais de terrorismo (COAF)

**Procedimento:**
- Consulta ao abrir conta
- Consulta mensal enquanto conta ativa
- Consulta antes de operação > R$ 50.000

**Se encontrado:**
- Congelamento de conta imediatamente
- Aviso ao COAF em até 24h
- Não liberar fundos sem autorização de autoridade
- Manter documentação por 10 anos

### 10.2 Restrições de Jurisdição

**Países de Alto Risco (requer Enhanced Due Diligence):**
- Coreia do Norte
- Irã
- Síria
- Cuba (com exceções)
- Qualquer país em lista OFAC

**Vedação Total:**
- Transações com pessoas/entidades sancionadas
- Financiamento de operações em jurisdições de alto risco

---

## PARTE 11: GOVERNANÇA DE IA

### 11.1 Uso de Sistemas de IA em Decisões de Crédito

**11.1.1 Princípios**

Qualquer sistema de IA (modelos de ML, LLM, agentes) utilizado em:
- Previsão de inadimplência
- Cálculo de scoring
- Recomendação de limite
- Avaliação de documentação
- Aprovação de operações

Deve cumprir:

**Transparency**
- Cliente deve saber que IA foi usada
- Explicação dos principais fatores de rejeição (em linguagem simples)
- Possibilidade de revisão humana sempre

**Fairness & Non-Discrimination**
- IA não pode usar como variável: raça, gênero, orientação sexual, religião, origem
- Teste de viés (bias testing) obrigatório semestralmente
- Análise de disparate impact em populações

**Accountability**
- Auditoria técnica de modelo a cada atualização
- Rastreabilidade completa (log) de cada decisão tomada
- Responsável técnico designado para cada modelo

**Robustness & Safety**
- Teste de adversarial inputs
- Validação de hallucinations (alucinações)
- Validação de Information Sufficiency Ratio (ISR)
- Plano de contingência se modelo falhar

**Human Oversight**
- Humano sempre pode revisar decisão da IA
- Limiar de confiança abaixo do qual escala para humano
- Funcionários treinados para avaliar outputs de IA

**11.1.2 Auditoria de Modelos**

Todos os modelos utilizados devem passar por:

1. **Auditoria de Conformidade**: Verifica se modelo respeita políticas deste documento
2. **Auditoria de Viés**: Testa se há discriminação contra grupos protegidos
3. **Auditoria de Segurança**: Testa vulnerabilidades (prompt injection, data poisoning)
4. **Auditoria de Confiabilidade**: Valida accuracy, false negative rate, false positive rate
5. **Auditoria de Explicabilidade**: Valida se decisões podem ser justificadas para cliente

**Frequência:**
- Modelos novos: Auditoria antes do deployment
- Modelos em produção: Auditoria trimestral mínimo
- Após mudança de dados de treinamento: Auditoria antes de voltar para produção

**Documentação:**
- Relatório de auditoria mantido por 7 anos
- Assinado por especialista independente (não desenvolvedor do modelo)
- Disponível para revisão regulatória

**11.1.3 Feedback Loop e Atualização de Modelos**

- Modelo deve ser retreinado se: Accuracy cair abaixo de 85%, ou Viés detectado
- Antes de retreinar: Nova auditoria de dados de treinamento
- Aprovação de diretor antes de redeploy de modelo retreinado

**11.1.4 Alucinações e Hallucinations**

**Definição:** Modelo gera informações falsas ou não-suportadas pelos dados

**Detecção:**
- Score de confiança < 60%: Rejeitar automaticamente
- Inconsistência com política: Flag para revisão
- Referência a cliente/documento inexistente: Rejeição automática

**Processo se Alucinação Detectada:**
1. Registrar em log de aucinações
2. Notificar ao responsável técnico em até 24h
3. Avaliar escopo (quantas decisões afetadas?)
4. Se > 5 alucinações em 30 dias: Retirar modelo de produção
5. Executar auditoria de segurança

**11.1.5 Explicabilidade de Decisão**

Cliente negado por IA tem direito a:
- Saber qual modelo foi usado
- Top 3 fatores que levaram à rejeição
- Explicação em linguagem simples (máximo nível secundário)
- Opção de apelação com revisão humana

**Exemplo de Explicação:**
❌ Ruim: "Pontuação insuficiente (score 580, mínimo 650)"
✅ Bom: "Você teve dois atrasos de pagamento nos últimos 2 anos, o que reduziu sua pontuação de confiança. Recomendamos esperar 12 meses sem atrasos para reaplicar."

---

## PARTE 12: CASOS ESPECIAIS E EXCEÇÕES

### 12.1 Override de Decisão Automática

Gerentes podem fazer override (anular) decisão automática de IA APENAS se:

**Condições Necessárias:**
- Score entre 600-699 (zona crítica)
- Cliente é correntista há > 24 meses
- Cliente não teve atraso nos últimos 12 meses
- Limite solicitado ≤ 30% acima do máximo automático
- Renda verificada e atualizada

**Processo:**
1. Gerente documenta razão do override
2. Requer aprovação de diretor de agência
3. Transação é auditada em até 15 dias
4. Se decisão se prova incorreta (cliente atrasa): Gerente tem repercussão na avaliação

**Proibido fazer override se:**
- Score < 600
- Cliente teve default nos últimos 36 meses
- Cliente tem atraso > 30 dias atualmente

### 12.2 Clientes VIP

**Critério de VIP:**
- Saldo investido > R$ 500.000, OU
- Renda comprovada > R$ 50.000/mês, OU
- Operações > R$ 10.000.000/ano

**Benefícios VIP:**
- Gerente de relacionamento dedicado
- Taxa preferencial de 2% a menos em operações
- Limite aumentado em até 50% (dentro de políticas)
- Análise de limite em até 48h

**Restrições:**
- Mesmos critérios de score e conformidade aplicam-se
- Não conseguem fazer override sem documentação
- Cancelamento de status se houver inadimplência

### 12.3 Clientes em Vulnerabilidade Social

**Identificação:**
- Idoso (65+) sem suporte familiar
- Pessoa com deficiência severa
- Imigrante/refugiado sem documentação completa
- Vítima de violência (com comprovação)

**Proteções:**
- Não pode ser cobrado taxa em operações básicas
- Cartão de débito em vez de crédito para controle
- Limite reduzido em 50% mas acesso garantido
- Acompanhante em atendimentos (se solicitado)
- Orientação de planejamento financeiro

---

## PARTE 13: RELATÓRIOS E DOCUMENTAÇÃO

### 13.1 Documentação Obrigatória

Toda operação deve ter arquivo contendo:

**Documentação do Cliente:**
- Cópia de ID e CPF/CNPJ
- Comprovante de renda
- Comprovante de endereço
- Comprovante de profissão (se solicitado)

**Análise Interna:**
- Resultado SPC/SERASA
- Cálculo de score (passo a passo)
- Análise de capacidade de pagamento
- Resultado de compliance/PLD

**Contratual:**
- Contrato assinado
- Condições gerais
- Taxa de juros e prazos
- Comprovante de desembolso

**Retenção:**
- Clientes ativos: Mínimo 5 anos
- Clientes inativos: Mínimo 5 anos após encerramento
- Operações fraudulentas: 10 anos

### 13.2 Relatórios Regulatórios

**BCB - Relatórios Mensais:**
- Carteira de crédito por categoria
- Taxa média de inadimplência
- Provisionamento de perdas esperadas

**CMN - Relatórios Trimestrais:**
- Conformidade com resoluções
- Incidentes de segurança
- Operações suspeitas reportadas

**CVM - Se aplicável:**
- Operações de títulos
- Advertências de riscos

---

## PARTE 14: MÉTRICAS E MONITORAMENTO

### 14.1 KPIs de Crédito

**Monitoramento Mensal:**

| KPI | Meta | Alerta |
|-----|------|--------|
| Taxa de Aprovação | 45-55% | < 40% ou > 60% |
| Taxa de Inadimplência 90+ | < 2% | > 2.5% |
| Taxa de Default | < 0.5% | > 0.7% |
| Tempo Médio Aprovação | 3 dias | > 5 dias |
| Score Médio Carteira | 750+ | < 700 |

### 14.2 Auditoria Interna

**Trimestral:**
- Revisão de 50 casos aprovados e 50 negados
- Verificar consistência com políticas
- Testar documentação

**Anual:**
- Auditoria completa de compliance
- Teste de modelos de IA
- Revisão de limites e taxa

---

## PARTE 15: GLOSSÁRIO

| Termo | Definição |
|-------|-----------|
| **Default** | Atraso de > 90 dias ou declaração de insolvência |
| **Score** | Pontuação de risco creditício (0-1000) |
| **PEP** | Pessoa Politicamente Exposta |
| **PLD** | Prevenção de Lavagem de Dinheiro |
| **SPC** | Serviço de Proteção de Crédito |
| **SERASA** | Sociedade Brasileira de Serviços de Proteção ao Crédito |
| **TED** | Transferência Eletrônica Disponível (rápida) |
| **DOC** | Documento de Ordem de Crédito (lenta, até 2 dias) |
| **PIX** | Pagamento Instantâneo (em tempo real) |
| **TAC** | Taxa de Abertura de Crédito |
| **IOF** | Imposto sobre Operações de Crédito |
| **ISR** | Information Sufficiency Ratio (validação de dados) |
| **Enhanced Due Diligence** | Análise intensificada de origem de fundos/cliente |
| **UBO** | Ultimate Beneficial Owner (beneficiário final real) |
| **Disparate Impact** | Impacto discriminatório ainda que não intencional |

---

## PARTE 16: VIGÊNCIA E REVISÃO

**Próxima Revisão:** 01 de setembro de 2026

**Responsável pela Revisão:** Diretoria de Compliance e Risco Operacional

**Assinatura de Aprovação:**

Diretora de Conformidade: ___________________________  
Data: 01/03/2024

Diretor Executivo: ___________________________  
Data: 01/03/2024

---

## ÍNDICE REMISSIVO

- **Alucinações de IA**: Seção 11.1.4
- **Análise de Renda**: Seção 2.3
- **Atendimento ao Cliente**: Seção 8
- **Cancela, Manutenção de Conta**: Seção 7.1
- **Casos Especiais**: Seção 12
- **Cheque Especial**: Seção 2.5.4
- **Clientes em Vulnerabilidade**: Seção 12.3
- **Clientes VIP**: Seção 12.2
- **Conformidade**: Seção 4
- **Conformidade em IA**: Seção 11
- **Dados Pessoais**: Seção 5
- **Default e Inadimplência**: Seção 3.2
- **Documentação**: Seção 13.1
- **Endividamento Máximo**: Seção 2.3.3
- **Exceções de Score**: Seção 2.6
- **Fraude**: Seção 9.3
- **Fluxo de Aprovação**: Seção 2.7
- **Limites Agregados**: Seção 2.5.2
- **Limites de Operações**: Seção 6.1
- **Monitoramento**: Seção 3.1, 14.1
- **Pagamentos em Atraso**: Seção 3.2
- **PEP e Sanções**: Seção 10
- **Produtos Financeiros**: Seção 7
- **Renegociação de Dívida**: Seção 3.2.2
- **Scoring**: Seção 2.2
- **Setores de Risco**: Seção 2.6.2
