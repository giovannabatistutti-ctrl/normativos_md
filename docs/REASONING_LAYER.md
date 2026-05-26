# Reasoning Layer — iFood Pago | Análise de Normativos BCB

> **Propósito:** Este documento é a camada de raciocínio utilizada pelo agente para analisar cada normativo publicado pelo Banco Central do Brasil (BCB) e classificar sua aplicabilidade ao iFood Pago. Deve ser carregado como instrução de contexto antes de qualquer análise de normativo.

---

## Seção 1 — Quem é o iFood Pago

### 1.1 Entidades do Conglomerado

| Entidade | Tipo | Papel |
|---|---|---|
| **iFood Pago Instituição de Pagamento S.A.** | IP (Instituição de Pagamento) | Líder do conglomerado |
| **iFood Pago Sociedade de Crédito Direto S.A. (SCD)** | SCD | Operações de crédito |

### 1.2 Classificação Regulatória

- **Segmento regulatório:** S5 (em discussão para reclassificação para S4 ou S3)
- **Tipo de conglomerado:** Tipo 3 (conglomerado prudencial)
- **Regulador principal:** Banco Central do Brasil (BCB)
- **Regulador secundário relevante:** N/A (câmbio, seguros e CVM estão fora do escopo)

### 1.3 Autorizações e Atividades Autorizadas

| Autorização/Atividade | Status |
|---|---|
| Subcredenciador | ✅ Ativo (atual) |
| Credenciador | 🔄 Em breve (transição em curso) |
| Participante facultativo do Pix (acesso direto) | ✅ Ativo |
| Detentor de conta (Open Finance) | ✅ Ativo |
| ITP — Iniciador de Transação de Pagamento (Open Finance) | ✅ Ativo |

### 1.4 Produtos e Serviços Ativos

| Produto/Serviço | Segmento | Status |
|---|---|---|
| Conta de Pagamento | B2C, B2B | ✅ Ativo |
| Cartão de crédito | B2C,B2B | ✅ Ativo |
| Cartão de benefícios (PAT — Programa de Alimentação do Trabalhador) | B2C, B2B | ✅ Ativo |
| BNPL (Buy Now Pay Later) | B2C | ✅ Ativo |
| Antecipação de recebíveis | B2B (Restaurantes) | ✅ Ativo |
| POS (máquina de cartão) | B2B (Restaurantes) | ✅ Ativo |
| Pix | B2C, B2B | ✅ Ativo |
| Open Finance / ITP | B2C, B2B | ✅ Ativo |
| Representante de Seguros | B2C,B2B | 🔄 Em breve |
| Carteira Digital | B2C | 🔄 Em breve |
| Credenciamento / Adquirência | B2B | 🔄 Em breve |


### 1.5 Público Atendido

| Segmento | Descrição |
|---|---|
| **B2B — Restaurantes** | Banco do Restaurante: conta, antecipação, POS, cartão |
| **B2C — Pessoa física** | Conta, cartão de crédito, benefícios, Pix, BNPL |
| **BaaS** | Banking as a Service para parceiros/clientes corporativos |
| **Credenciador/Adquirente** | Banking as a Service para parceiros/clientes corporativos |

### 1.6 Fora do Escopo — O iFood Pago NÃO opera com

- Câmbio / operações de câmbio
- Crédito rural
- Crédito imobiliário
- Ativos virtuais / criptoativos
- Seguros (regulação SUSEP)
- Mercado de capitais (regulação CVM)
- Cooperativas de crédito

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
| Crédito / SCD | ✅ APLICÁVEL | BNPL, Antecipação de recebíveis, Cartão crédito, crédito pessoal, crédito capital de giro |
| PAT / Benefícios alimentares / auxílio ao trabalhador | ✅ APLICÁVEL | Cartão de benefícios |
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
| Representante de Seguros | ⚠️ MONITORAR | Pode afetar parcerias com seguradoras |
| BNDES / FGI | ⚠️ MONITORAR | produto sendo estruturado |
| Financeiras (SCFI) | ⚠️ MONITORAR | Pode afetar parceiros/BaaS |
| Câmbio | ❌ NÃO APLICÁVEL | Não opera |
| Crédito rural | ❌ NÃO APLICÁVEL | Não opera |
| Crédito imobiliário | ❌ NÃO APLICÁVEL | Não opera |
| Ativos virtuais / Criptoativos | ❌ NÃO APLICÁVEL | Não opera |
| Seguros / SUSEP | ❌ NÃO APLICÁVEL | Fora do regulador principal |
| Mercado de capitais / CVM | ❌ NÃO APLICÁVEL | Fora do regulador principal |
| Cooperativas de crédito | ❌ NÃO APLICÁVEL | Não se aplica à estrutura |
| Aviões / Aeronáutica | ❌ NÃO APLICÁVEL | Não se aplica à estrutura |
| Marítimo | ❌ NÃO APLICÁVEL | Não se aplica à estrutura |

### PASSO 4 — Classificação final

Com base nos passos anteriores, atribuir uma das três classificações:

#### ✅ APLICÁVEL
> A norma impacta **diretamente** o iFood Pago, algum de seus produtos, processos ou obrigações regulatórias.

**Ações:**
- Salvar íntegra do normativo em `data/normativos-bcb/<data>/<arquivo>.md`
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

---

## Seção 3 — Calculadora de Riscos iFood Pago

> Aplicar somente para normas classificadas como ✅ **APLICÁVEL**.
> Esta seção substitui a avaliação qualitativa anterior por uma metodologia quantitativa baseada na Calculadora de Riscos oficial do iFood Pago, extraída dos apontamentos internos (apontamentos_ifoodpago_v2.xlsx).

---

### 3.1 — Avaliação do Impacto por Pilar

Para cada normativo **APLICÁVEL**, avaliar os pilares abaixo e atribuir nível de **1 a 4**:

#### 📋 Pilar Compliance

| Nível | Descrição |
|---|---|
| **1** | Não conformidade com recomendações de associações de classe e/ou regras internas |
| **2** | Não conformidade com legislação (leis e resoluções publicadas por reguladores) |
| **3** | Não conformidade com legislação onde já houve questionamentos, investigações ou inspeções por autoridades públicas |
| **4** | Não conformidade com legislação onde já houve multas e sanções aplicadas |

**Pergunta-chave:** A norma cria nova obrigação legal que ainda não seguimos? Há histórico de sanções do BCB por descumprimento similar?

#### 📈 Pilar Estratégico

| Nível | Descrição |
|---|---|
| **1** | Pouca/nenhuma interferência nos OKRs do FY vigente |
| **2** | Alguma interferência, podendo impactar até 1 OKR |
| **3** | Grande interferência, podendo impactar até 2 OKRs |
| **4** | Altíssima interferência, impactando pelo menos 3 OKRs ou ameaçando sustentabilidade do negócio |

**Pergunta-chave:** Quantos OKRs do iFood Pago são afetados? A norma muda o modelo de negócio ou algum produto estratégico?

#### 💰 Pilar Financeiro

| Nível | Percentual do PR | Valor absoluto (referência) |
|---|---|---|
| **1** | Menos de 0,5% do PR do conglomerado prudencial | Abaixo de R$ 175.000 |
| **2** | 0,6% a 3% do PR | Entre R$ 175.000 e R$ 1.000.000 |
| **3** | 3,1% a 5% do PR | Entre R$ 1.000.000 e R$ 1.750.000 |
| **4** | Acima de 5% do PR | Acima de R$ 1.750.000 |

**Pergunta-chave:** Qual o custo estimado de adequação ou multa potencial em percentual do Patrimônio de Referência (PR) do conglomerado?

#### ⚖️ Pilar Legal

| Nível | Descrição |
|---|---|
| **1** | Disputas e notificações extrajudiciais |
| **2** | Disputas legais e necessidade de provisões contábeis |
| **3** | Ocorrência de condenações civis ou administrativas |
| **4** | Ocorrência de condenações criminais e/ou suspensão ou encerramento das atividades |

**Pergunta-chave:** Qual o tipo de sanção possível pelo descumprimento? Administrativa, civil ou criminal?

#### ⚙️ Pilar Operacional

| Nível | Clientes afetados | Grau de mobilização interna |
|---|---|---|
| **1** | Até 5% dos clientes | Envolvimento de colaboradores até grade 10 |
| **2** | Até 10% dos clientes | Colaboradores de grade 11-12 |
| **3** | Até 20% dos clientes | Colaboradores de grade 13-14 |
| **4** | 30% ou mais dos clientes | Colaboradores acima de grade 14 / situação de crise |

**Pergunta-chave:** Qual percentual de clientes pode ser afetado? Qual grau de mobilização interna é necessário para adequação?

#### 🔐 Pilar Segurança da Informação

| Nível | Pilares CIA violados | Clientes afetados | Indisponibilidade |
|---|---|---|---|
| **1** | Nenhum ou 1 pilar em ativos não críticos | Até 5% | Até 1 hora |
| **2** | 1 pilar em ativos críticos | Até 10% | Até 4 horas |
| **3** | 2 pilares em ativos críticos | Até 20% | Até 8 horas |
| **4** | 3 pilares em ativos críticos | 30% ou mais | Mais de 8 horas |

> **Nota:** O Pilar de Segurança da Informação deve ser avaliado quando a norma tiver relação com segurança cibernética, proteção de dados, disponibilidade de sistemas ou LGPD. Para normas sem componente de SI, desconsiderar este pilar no cálculo da média.

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

### 3.3 — Cálculo do Risco Inerente e Quadrantes de Criticidade

#### Fórmula do Risco Inerente

```
Pontuação = Impacto (média dos pilares, arredondada) × Probabilidade (1-4)
Faixa: 1 a 16 pontos
```

**Escala de Impacto (média dos pilares):**
- 1 = **Baixo**
- 2 = **Médio**
- 3 = **Alto**
- 4 = **Muito Alto**

#### Tabela de Quadrantes A–P

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

### 3.4 — Referência: Categorias de Risco da Biblioteca Interna (relevantes para normativos)

As categorias abaixo representam os riscos mapeados internamente pelo iFood Pago com maior criticidade para normativos regulatórios:

| Categoria de Risco | Subcategoria | Criticidade Biblioteca |
|---|---|---|
| Risco de Compliance | Controles Regulatórios → Normas emitidas por Órgãos Reguladores | 🔴 MUITO ALTO × Certamente |
| Risco de Compliance | Lavagem de Dinheiro / Financiamento ao Terrorismo (PLD/FT) | 🔴 MUITO ALTO × Certamente |
| Risco de Compliance | Conduta com o Cliente | 🔴 MUITO ALTO × Certamente |
| Risco Operacional | Onboarding / Identificação de Usuário | 🔴 MUITO ALTO × Certamente |
| Risco de Segurança Cibernética | Ataques (cibernéticos) | 🟠 ALTO × Possível |

> Estas categorias devem ser usadas como referência de calibração. Normativos que se enquadrem nestas categorias tendem a receber avaliação de impacto alto ou muito alto.

---

### 3.5 — Formato de Saída Padronizado nos Arquivos `.md` dos Normativos

Para cada normativo classificado como ✅ **APLICÁVEL**, adicionar o seguinte bloco **após o resumo executivo** do arquivo `.md`:

```markdown
## 🎯 Avaliação de Risco — Calculadora iFood Pago

| Pilar | Nível | Justificativa |
|---|---|---|
| Compliance | {1-4} | {motivo} |
| Estratégico | {1-4} | {motivo} |
| Financeiro | {1-4} | {motivo} |
| Legal | {1-4} | {motivo} |
| Operacional | {1-4} | {motivo} |

**Impacto médio:** {valor} ({Baixo/Médio/Alto/Muito Alto})
**Probabilidade:** {Remota/Possível/Provável/Certamente}
**Pontuação:** {Impacto × Probabilidade} — Quadrante {letra}
**Criticidade:** {🔴 CRÍTICO | 🟠 ALTO | 🟡 MÉDIO | 🟢 BAIXO}
**Prazo recomendado para adequação:** {prazo}
```

> **Nota:** O Pilar de Segurança da Informação deve ser incluído na tabela apenas quando relevante para o normativo em questão. Incluir na linha de Pilares como `Seg. Informação | {1-4} | {motivo}` quando aplicável.
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

---

## Seção 5 — Normas Estruturantes em Vigília Permanente

> Estas normas formam a base regulatória do iFood Pago e devem ser **sempre consideradas** no contexto de qualquer nova regulação analisada. Verificar se a nova norma altera, complementa ou revoga alguma delas.

| Norma | Tema | Relevância |
|---|---|---|
| **Resolução BCB nº 80/2021** | Instituições de Pagamento — regulação prudencial e operacional | Base para toda operação do IP |
| **Resolução BCB nº 1/2020** | Open Finance / Open Banking | Base para ITP e detentor de conta |
| **Resolução Conjunta nº 1/2020** | Compartilhamento de dados e proteção no Sistema Financeiro | LGPD aplicada ao SF |
| **Resolução CMN nº 4.893/2021** | Política de segurança cibernética e ambiente de nuvem | Obrigação de segurança |
| **Circular BCB nº 3.978/2020** | PLD/FT — Prevenção à lavagem de dinheiro e financiamento ao terrorismo | Obrigação PLD para IPs |
| **Regulamento do Pix (BCB)** | Regras operacionais e participação no arranjo Pix | Participação facultativa direta |
| **Lei nº 12.865/2013** | Arranjos de pagamento e instituições de pagamento | Lei habilitadora das IPs |
| **Lei nº 13.709/2018** | Lei Geral de Proteção de Dados (LGPD) | Proteção de dados de clientes |


---

## Seção 6 — Radar Regulatório

| Prioridade | Tema | Implicações | Monitorar |
|---|---|---|---|
| 🔴 **Alta** | Reclassificação S5→S4/S3 | Requisitos prudenciais mais rigorosos (capital, governança, reporte) | Normativos sobre critérios de segmento |
| 🔴 **Alta** | Subcredenciador→Credenciador | Novos requisitos operacionais, técnicos e regulatórios | Normas sobre credenciamento e arranjos de pagamento |
| 🟡 **Média** | Carteira Digital (em implantação) | KYC, limites operacionais e proteção ao consumidor | Normativos sobre contas de pagamento e wallets |
| 🟡 **Média** | Evolução do Open Finance | Novas obrigações para ITP e detentor de conta | Resoluções BCB sobre Open Finance |
| 🟡 **Média** | Proteção ao Consumidor para IPs | Mudanças em SAC, ouvidoria, tarifas e comunicação | Res. CMN e BCB sobre atendimento e tarifas |


---

## Seção 7 — Políticas Internas

> Detalhes em **[`REASONING_LAYER_POLITICAS.md`](./REASONING_LAYER_POLITICAS.md)** (34 documentos).
> Verificar se política interna atende normativo (reduz criticidade) ou há lacuna (aumenta criticidade). Acionar área responsável conforme listado.

