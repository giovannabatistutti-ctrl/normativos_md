# Decision Layer — Camada 2 de 2

> **Propósito:** Define COMO avaliar normativos — árvore de decisão de aplicabilidade,
> avaliação de risco em 4 pilares e ações recomendadas.
> Lê a Camada 1 (CONTEXTO_IFOOD_PAGO.md) para aplicar as regras ao contexto do iFood Pago.
>
> **4 Pilares de Risco:** Operacional | Regulatório | Financeiro | Clientes

---

## Seção 2 — Árvore de Decisão de Aplicabilidade

> Aplicar os passos abaixo sequencialmente para cada normativo analisado.

### PASSO 1 — Identificar o tipo e escopo declarado da norma

Verificar:
- **Tipo:** Resolução CMN / Resolução BCB / Instrução Normativa BCB / Circular / Carta Circular / Comunicado
- **Escopo declarado no texto:** Para quais tipos de instituições a norma se aplica explicitamente?
- **Data de publicação** e **data de vigência** (verificar se já está em vigor ou é futura)

### PASSO 2 — Verificar se o escopo atinge o iFood Pago

Responder às perguntas abaixo. Uma resposta "SIM" já indica que a norma é potencialmente relevante:

| Pergunta | Se SIM → |
|---|---|
| A norma menciona **Instituições de Pagamento (IPs)**? | → Relevante |
| A norma menciona **Sociedades de Crédito Direto (SCD)**? | → Relevante |
| A norma menciona **conglomerados prudenciais Tipo 3**? | → Relevante |
| A norma menciona **capital regulatório**? | → Relevante |
| A norma menciona **Segmento S5** (ou S4/S3)? | → Relevante |
| A norma menciona **participantes do Pix**? | → Relevante |
| A norma menciona **Open Finance / Open Banking**? | → Relevante |
| A norma menciona **ITP** (Iniciadores de Transação de Pagamento)? | → Relevante |
| A norma menciona **subcredenciadores** ou **credenciadores**? | → Relevante |
| A norma menciona **arranjos de pagamento**? | → Relevante |
| A norma menciona **detentores de conta** (Open Finance)? | → Relevante |
| A norma menciona **apenas** bancos múltiplos, bancos comerciais, seguradoras, corretoras de valores, cooperativas de crédito? | → Provavelmente NÃO aplicável — verificar PASSO 3 |

### PASSO 3 — Verificar tema vs. produtos do iFood Pago

| Tema da norma | Aplicável? | Produtos impactados |
|---|---|---|
| Arranjos/instrumentos de pagamento | ✅ APLICÁVEL | Conta pagamento, cartão, Pix, POS |
| Credenciamento/subcredenciamento | ✅ APLICÁVEL | POS, cartão, Pix |
| Pix (normas específicas) | ✅ APLICÁVEL | Pix, Conta pagamento |
| Open Finance / Open Banking | ✅ APLICÁVEL | Open Finance, ITP |
| Conta de pagamento | ✅ APLICÁVEL | Conta pagamento, Carteira Digital |
| Crédito / SCD | ✅ APLICÁVEL | BNPL, Antecipação de recebíveis, Cartão crédito |
| PAT / Benefícios alimentares | ✅ APLICÁVEL | Cartão de benefícios |
| PLD/FT (prevenção à lavagem de dinheiro e financiamento ao terrorismo) | ✅ APLICÁVEL | Todos os produtos |
| Fraudes e segurança | ✅ APLICÁVEL | Todos os produtos |
| LGPD / Privacidade financeira | ✅ APLICÁVEL | Todos os produtos |
| Proteção ao consumidor / usuário de SF | ✅ APLICÁVEL | B2C, restaurantes |
| CADOCs (documentos prudenciais) | ✅ APLICÁVEL | Obrigação regulatória |
| COSIF (plano de contas) | ✅ APLICÁVEL | Contabilidade |
| Patrimônio Líquido / Capital regulatório | ✅ APLICÁVEL | Gestão prudencial |
| Conglomerado prudencial | ✅ APLICÁVEL | IP líder + SCD |
| Tarifas de serviços financeiros | ✅ APLICÁVEL | Todos os produtos |
| Correspondente bancário | ✅ APLICÁVEL | BaaS, distribuição |
| Tesouraria / liquidez / gestão de ativos | ✅ APLICÁVEL | Gestão financeira |
| Segurança cibernética (IFs) | ✅ APLICÁVEL | Infraestrutura |
| BaaS / Banking as a Service | ✅ APLICÁVEL | BaaS |
| Normas de aplicação interna do Banco Central do Brasil | ❌ NÃO APLICÁVEL | 
| Câmbio | ❌ NÃO APLICÁVEL | Não opera |
| Crédito rural | ❌ NÃO APLICÁVEL | Não opera |
| Crédito imobiliário | ❌ NÃO APLICÁVEL | Não opera |
| Ativos virtuais / Criptoativos | ❌ NÃO APLICÁVEL | Não opera |
| Seguros / SUSEP | ❌ NÃO APLICÁVEL | Fora do regulador principal |
| Mercado de capitais / CVM | ❌ NÃO APLICÁVEL | Fora do regulador principal |
| Cooperativas de crédito | ❌ NÃO APLICÁVEL | Não se aplica à estrutura |
| Financeiras (SCFI) | ⚠️ MONITORAR | Pode afetar parceiros/BaaS |

### PASSO 4 — Classificação final

Com base nos passos anteriores, atribuir uma das três classificações:

#### ✅ APLICÁVEL
> A norma impacta **diretamente** o iFood Pago, algum de seus produtos, processos ou obrigações regulatórias.

**Ações:**
- Salvar íntegra do normativo em `data/normativos-bcb/<data>/<arquivo>.md`
- Analisar o inteiro teor da norma
- Notificar canal Slack de Compliance (#compliance-normativos ou equivalente)
- Classificar nível de impacto (ver Seção 3)
- Identificar ações recomendadas (ver Seção 4)

#### ⚠️ MONITORAR
> A norma **não impacta diretamente** o iFood Pago, mas pode afetar parceiros, clientes corporativos, operações BaaS, ou pode tornar-se relevante com a evolução do negócio (ex.: expansão de produtos, reclassificação de segmento).

**Ações:**
- Salvar íntegra do normativo com tag `[MONITORAR]`
- Notificar canal Slack com marcação explícita de monitoramento
- Registrar no radar regulatório

#### ❌ NÃO APLICÁVEL
> A norma é específica para setores fora do escopo do iFood Pago (câmbio, seguros, crédito rural, cripto, CVM, cooperativas).

**Ações:**
- Apenas registrar no log de execução
- **Não** salvar íntegra
- **Não** notificar Slack

### PASSO 5 — Verificar Políticas Internas

> Consultar REASONING_LAYER_POLITICAS.md para verificar se existe política interna que já trata o tema da norma.
> Se existe: reduz criticidade (pode já estar conforme). Se não existe: aumenta criticidade (lacuna potencial).

---

## Seção 3 — Calculadora de Riscos iFood Pago (4 Pilares)

> Aplicar somente para normas classificadas como ✅ **APLICÁVEL**.
> Metodologia quantitativa baseada na Calculadora de Riscos oficial do iFood Pago.

---

### 3.1 — Avaliação do Impacto por Pilar (4 Pilares)

Para cada normativo **APLICÁVEL**, avaliar os 4 pilares abaixo e atribuir nível de **1 a 4**:

#### ⚙️ Pilar Operacional

| Nível | Clientes afetados | Grau de mobilização interna |
|---|---|---|
| **1** | Até 5% dos clientes | Envolvimento de colaboradores até grade 10 |
| **2** | Até 10% dos clientes | Colaboradores de grade 11-12 |
| **3** | Até 20% dos clientes | Colaboradores de grade 13-14 |
| **4** | 30% ou mais dos clientes | Colaboradores acima de grade 14 / situação de crise |

**Pergunta-chave:** Qual percentual de clientes pode ser afetado? Qual grau de mobilização interna é necessário para adequação?

#### ⚖️ Pilar Regulatório

| Nível | Descrição |
|---|---|
| **1** | Não conformidade com recomendações de associações de classe e/ou regras internas |
| **2** | Não conformidade com legislação (leis e resoluções publicadas por reguladores) |
| **3** | Não conformidade com legislação onde já houve questionamentos, investigações ou inspeções por autoridades públicas |
| **4** | Não conformidade com legislação onde já houve multas e sanções aplicadas |

**Pergunta-chave:** A norma cria nova obrigação legal que ainda não seguimos? Há histórico de sanções do BCB por descumprimento similar?

#### 💰 Pilar Financeiro

| Nível | Percentual do PR | Valor absoluto (referência) |
|---|---|---|
| **1** | Menos de 0,5% do PR do conglomerado prudencial | Abaixo de R$ 175.000 |
| **2** | 0,6% a 3% do PR | Entre R$ 175.000 e R$ 1.000.000 |
| **3** | 3,1% a 5% do PR | Entre R$ 1.000.000 e R$ 1.750.000 |
| **4** | Acima de 5% do PR | Acima de R$ 1.750.000 |

**Pergunta-chave:** Qual o custo estimado de adequação ou multa potencial em percentual do Patrimônio de Referência (PR) do conglomerado?

#### 👥 Pilar Clientes

| Nível | Descrição |
|---|---|
| **1** | Impacto mínimo — apenas notificação informativa |
| **2** | Ajuste pontual em produto ou comunicação com clientes |
| **3** | Mudança relevante em produto ou condições contratuais |
| **4** | Suspensão/bloqueio de produto ou impacto massivo na experiência |

**Pergunta-chave:** Qual o impacto nos clientes B2C e B2B do iFood Pago? Há necessidade de comunicação obrigatória?

---

### 3.2 — Probabilidade (4 Níveis)

| Nível | Nome | Frequência / Circunstância |
|---|---|---|
| **1** | Remota | A cada 5+ anos / ocorre apenas em circunstâncias excepcionais |
| **2** | Possível | A cada 1-5 anos / pode se manifestar em algum momento |
| **3** | Provável | Uma vez ao ano / manifesta-se com frequência |
| **4** | Certamente | Várias vezes ao ano / manifesta-se com alta frequência |

#### Regra de avaliação da probabilidade para normativos BCB:

| Situação da norma | Probabilidade |
|---|---|
| Norma nova com prazo já em vigor | **Provável (3)** |
| Norma nova com prazo futuro | **Possível (2)** |
| Norma que altera norma existente | **Possível (2)** |
| Norma com histórico documentado de fiscalização BCB | **Certamente (4)** |
| Norma informativa ou esclarecedora (sem novas obrigações) | **Remota (1)** |

---

### 3.3 — Cálculo do Score Consolidado (4 Pilares)

#### Média Ponderada dos 4 Pilares

| Pilar | Peso |
|---|---|
| Impacto Operacional | 1.0 |
| Impacto Regulatório | **1.5** (peso maior — pilar de conformidade) |
| Impacto Financeiro | 1.0 |
| Impacto em Clientes | 1.0 |

**Fórmula:** `Score = soma_ponderada / 4.5`

#### Escala de Criticidade

| Score Ponderado | Criticidade |
|---|---|
| 3.5 – 4.0 | 🔴 **CRÍTICO** |
| 3.0 – 3.4 | 🔴 **ALTO** |
| 2.0 – 2.9 | 🟡 **MÉDIO** |
| 1.0 – 1.9 | 🟢 **BAIXO** |

> **Regra extra:** Se qualquer pilar isolado for CRÍTICO (score 4), o consolidado é no mínimo ALTO.

#### Tabela de Quadrantes A–P (Risco Inerente)

```
Pontuação = Impacto (média ponderada, arredondada) × Probabilidade (1-4)
Faixa: 1 a 16 pontos
```

| Quadrante | Pontuação | Impacto | Probabilidade | Criticidade |
|---|---|---|---|---|
| **A** | 16 | Muito Alto | Certamente | 🔴 CRÍTICO MÁXIMO |
| **E** | 15 | Muito Alto | Provável | 🔴 CRÍTICO |
| **B** | 14 | Alto | Certamente | 🔴 CRÍTICO |
| **F** | 13 | Alto | Provável | 🔴 CRÍTICO |
| **I** | 12 | Muito Alto | Possível | 🟠 ALTO |
| **C** | 11 | Médio | Certamente | 🟠 ALTO |
| **J** | 10 | Alto | Possível | 🟠 ALTO |
| **G** | 9 | Médio | Provável | 🟠 ALTO |
| **M** | 8 | Muito Alto | Remota | 🟡 MÉDIO |
| **D** | 7 | Baixo | Certamente | 🟡 MÉDIO |
| **K** | 6 | Médio | Possível | 🟡 MÉDIO |
| **N** | 5 | Alto | Remota | 🟡 MÉDIO |
| **H** | 4 | Baixo | Provável | 🟢 BAIXO |
| **O** | 3 | Médio | Remota | 🟢 BAIXO |
| **L** | 2 | Baixo | Possível | 🟢 BAIXO |
| **P** | 1 | Baixo | Remota | 🟢 BAIXO — BAIXÍSSIMO |

#### Definição de Criticidade e Prazos

| Criticidade | Quadrantes | Ação | Prazo máximo |
|---|---|---|---|
| 🔴 **CRÍTICO** | A, E, B, F | Ação imediata — escalar para liderança Compliance + áreas impactadas | **5 dias úteis** |
| 🟠 **ALTO** | I, C, J, G | Ação urgente — acionar áreas e iniciar plano de adequação | **15 dias úteis** |
| 🟡 **MÉDIO** | M, D, K, N | Monitorar e planejar — incluir no ciclo de adequação | **30 dias corridos** |
| 🟢 **BAIXO** | H, O, L, P | Registrar e acompanhar — revisão regular de compliance | **Ciclo regular** |

---

### 3.4 — Formato de Saída Padronizado nos Arquivos `.md` dos Normativos

Para cada normativo classificado como ✅ **APLICÁVEL**, adicionar o seguinte bloco **após o resumo executivo** do arquivo `.md`:

```markdown
## 🎯 Avaliação de Risco — Calculadora iFood Pago (4 Pilares)

| Pilar | Nível | Justificativa |
|---|---|---|
| Operacional | {1-4} | {motivo} |
| Regulatório | {1-4} | {motivo} |
| Financeiro | {1-4} | {motivo} |
| Clientes | {1-4} | {motivo} |

**Score ponderado:** {valor} ({Baixo/Médio/Alto/Muito Alto})
**Probabilidade:** {Remota/Possível/Provável/Certamente}
**Criticidade:** {🔴 CRÍTICO | 🟠 ALTO | 🟡 MÉDIO | 🟢 BAIXO}
**Prazo recomendado para adequação:** {prazo}
```

---

## Seção 4 — Ações Recomendadas por Tipo de Norma

> Mapa de acionamento de áreas internas com base no tema da norma classificada.

| Tema da Norma | Áreas a Acionar |
|---|---|
| Capital / Patrimônio Líquido / Prudencial | Finanças + Riscos + Compliance |
| Produtos (cartão, Pix, conta de pagamento, BNPL) | Product + Compliance |
| PLD/FT / Prevenção a Fraudes | PLD/AML team + Compliance |
| LGPD / Privacidade / Proteção de dados | DPO + Jurídico + Compliance |
| Operacional / Processos internos | Operações + Compliance |
| CADOCs / COSIF / Reporte prudencial | Contabilidade + Regulatório + Compliance |
| Proteção ao consumidor / Usuário de SF | SAC + Compliance |
| Tecnologia / Segurança cibernética | CISO + Tecnologia + Compliance |
| Open Finance / ITP | Product Open Finance + Compliance |
| Credenciamento / Subcredenciamento | Operações + Produto POS + Compliance |
| BaaS / Correspondente bancário | BaaS team + Jurídico + Compliance |
| Tesouraria / Liquidez | Finanças + Riscos + Compliance |
| PAT / Benefícios | Produto Benefícios + Compliance |
| Pix (regulamento e normas específicas) | Produto Pix + Tecnologia + Compliance |
