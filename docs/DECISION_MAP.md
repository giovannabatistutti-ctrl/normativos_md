# Mapa de Decisão — Análise de Normativos BCB | iFood Pago

> **Versão:** 1.0
> **Última atualização:** 2026-05-22
> **Responsável técnico:** Claw (agente automatizado)
> **Responsável negócio:** Giovanna Batistutti — Compliance, iFood Pago
> **Referência:** Este documento descreve os critérios aplicados pelo agente de captura de normativos BCB. Deve ser lido em conjunto com o `REASONING_LAYER.md`.

---

## 1. Fluxo Geral de Decisão

O fluxo abaixo descreve o percurso completo de um normativo — desde sua captura no feed BCB até o envio no Slack:

```
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 1 — CAPTURA                                                   │
│  Leitura do feed público BCB (API normativos)                       │
│  • Filtro de data: apenas publicações do dia corrente               │
│  • Anti-duplicata: verifica enviados.json antes de processar        │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2 — APLICABILIDADE (Seção 2 deste documento)                  │
│  Para cada normativo novo:                                          │
│  a) Identificar tipo, escopo declarado e datas                      │
│  b) Verificar se o escopo atinge o iFood Pago                       │
│  c) Verificar tema vs. produtos ativos                              │
│  d) Aplicar princípios de raciocínio (Seção 9)                      │
│  └─ Resultado: APLICÁVEL / MONITORAR / NÃO APLICÁVEL               │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
               ┌────────────┼────────────┐
               ▼            ▼            ▼
         APLICÁVEL      MONITORAR   NÃO APLIC.
               │            │            │
               │            │        Apenas log
               │            │        (sem arquivo,
               │            │         sem Slack)
               ▼            ▼
┌──────────────────────────────────────────┐
│  STEP 3 — AVALIAÇÃO DE RISCO             │
│  (somente APLICÁVEL e MONITORAR)         │
│  a) Avaliar 5 pilares de impacto (1-4)   │
│  b) Calcular impacto médio               │
│  c) Determinar probabilidade (1-4)       │
│  d) Calcular pontuação: Impacto × Prob.  │
│  e) Mapear quadrante (A-P)               │
│  f) Aplicar fatores de ajuste            │
│  └─ Resultado: CRÍTICO/ALTO/MÉDIO/BAIXO  │
└───────────────┬──────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 4 — GERAÇÃO DO ARQUIVO .md                                    │
│  • Reprodução de artigos, incisos e alíneas com marcação            │
│    (novo) / (alterado)                                              │
│  • Tabela de risco completa (pilares, impacto, probabilidade)       │
│  • Prazo recomendado de adequação                                   │
│  • Times a acionar (mapa norma → área)                              │
│  Salvo em: data/normativos-bcb/{data}/{id_normativo}.md             │
└───────────────┬─────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 5 — PUSH GITHUB                                               │
│  • Upload do .md para giovannabatistutti-ctrl/normativos_md         │
│  • Atualização do README.md do repositório                          │
│  (Requer token com escopo de escrita configurado em Integrations)   │
└───────────────┬─────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 6 — NOTIFICAÇÃO SLACK                                         │
│  Canal: #agenda-normativa-ifoodpago                                 │
│  Formato: Slack Blocks com:                                         │
│  • Header com emoji de criticidade                                  │
│  • Tipo, data, vigência, aplicabilidade                             │
│  • Ementa e criticidade calculada                                   │
│  • Botões: [Ver no BCB] [Ver .md GitHub] [Feedback ao Claw]         │
│  Normativos MONITORAR: marcação explícita ⚠️ MONITORAR              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Critério 1 — Aplicabilidade

### 2.1 Definição dos Três Resultados Possíveis

#### ✅ APLICÁVEL

**Definição precisa:** A norma cria, altera ou extingue obrigação que incide diretamente sobre o iFood Pago (IP líder, SCD, ou o conglomerado Tipo 3), sobre um de seus produtos ativos ou sobre processos e atividades já exercidos.

**Condições de ativação:**
- O escopo declarado da norma menciona explicitamente IPs, SCDs, conglomerados prudenciais Tipo 3, participantes do Pix, ITP, subcredenciadores ou credenciadores; **ou**
- O tema da norma recai sobre produto ou atividade ativa: Conta de Pagamento, cartão de crédito, cartão de benefícios (PAT), BNPL, antecipação de recebíveis, POS, Pix, Open Finance/ITP, BaaS; **ou**
- O tema é transversal obrigatório: PLD/FT, LGPD, proteção ao consumidor, segurança cibernética, CADOCs, COSIF, patrimônio líquido, tarifas.

**Racional:** O iFood Pago é uma instituição regulada pelo BCB. Qualquer norma que alcance seu perímetro legal ou operacional gera obrigação de adequação, podendo resultar em sanção pelo descumprimento. A não-identificação de uma norma aplicável é risco direto de não-conformidade.

**Exemplos típicos:**
- Resolução BCB alterando requisitos de capital para IPs
- Instrução Normativa BCB sobre relatórios CADOC exigidos de IPs
- Circular BCB com novas regras do Regulamento Pix
- Resolução CMN sobre PLD/FT aplicável a instituições de pagamento

**Consequência após classificação:**
1. Gerar arquivo `.md` completo com resumo executivo e avaliação de risco
2. Notificar #agenda-normativa-ifoodpago no Slack com criticidade calculada
3. Indicar times a acionar e prazo recomendado de adequação
4. Atualizar enviados.json (anti-duplicata)
5. Push para repositório GitHub (quando credencial disponível)

---

#### ⚠️ MONITORAR

**Definição precisa:** A norma não impacta diretamente o iFood Pago hoje, mas pode tornar-se relevante em virtude de: (a) evolução planejada do negócio; (b) operações de parceiros ou clientes BaaS; (c) posição ambígua da norma quanto ao escopo; ou (d) tendência regulatória que sinaliza mudanças futuras.

**Condições de ativação:**
- Norma que se aplica a tipo de instituição adjacente (ex: SCFI, bancos) mas afeta produtos ou parceiros do ecossistema iFood Pago; **ou**
- Norma sobre produto em fase de lançamento (ex: Carteira Digital); **ou**
- Norma que regula tema relevante para reclassificação de segmento (S5 → S4/S3) ou transição subcredenciador → credenciador; **ou**
- Norma cujo escopo é ambíguo e pode ser estendido ao iFood Pago por interpretação futura do BCB.

**Racional:** O radar regulatório exige antecipação. Normas que hoje não obrigam o iFood Pago podem criar obrigações amanhã, especialmente considerando a expansão de produtos e a reclassificação de segmento em discussão. O monitoramento evita surpresas.

**Exemplos típicos:**
- Normas sobre financeiras (SCFI) com cláusulas que afetam parceiros BaaS
- Normas sobre carteiras digitais ainda em fase de consulta pública
- Normas de segmento S4/S3 que serão aplicáveis após reclassificação
- Normas sobre credenciamento aplicáveis quando a transição for concluída

**Consequência após classificação:**
1. Gerar arquivo `.md` com tag `[MONITORAR]`
2. Notificar #agenda-normativa-ifoodpago com marcação explícita ⚠️ MONITORAR
3. Registrar no radar regulatório
4. Sem prazo de adequação imediato — acompanhamento periódico

---

#### ❌ NÃO APLICÁVEL

**Definição precisa:** A norma regula exclusivamente setor ou produto fora do perímetro atual e futuro do iFood Pago, sem qualquer interseção com suas entidades, atividades ou parceiros.

**Condições de ativação:**
- Norma exclusivamente sobre câmbio, crédito rural, crédito imobiliário, ativos virtuais/criptoativos, seguros (SUSEP), mercado de capitais (CVM) ou cooperativas de crédito; **e**
- Não há cláusula ou disposição que se estenda a IPs, SCDs ou conglomerados Tipo 3.

**Racional:** Eficiência operacional. O volume de publicações do BCB é alto. Filtrar o que é irrelevante permite foco nos normativos que realmente exigem ação do iFood Pago.

**Exemplos típicos:**
- Resolução CMN sobre taxas de juros para crédito rural
- Circular BCB regulamentando operações de câmbio
- Instrução Normativa BCB sobre reporte de operações com criptoativos
- Norma sobre cooperativas de crédito

**Consequência após classificação:**
1. Apenas registrar no log de execução (data, número, ementa)
2. Não gerar arquivo `.md`
3. Não notificar o Slack
4. Não atualizar enviados.json

---

### 2.2 Hierarquia de Verificação

A verificação de aplicabilidade segue esta ordem obrigatória:

**1º) Escopo declarado na norma**
Verificar a ementa e os artigos iniciais: para quais instituições a norma se aplica explicitamente?

| Se menciona... | Relevância |
|---|---|
| Instituições de Pagamento (IPs) | ✅ Potencialmente aplicável |
| Sociedades de Crédito Direto (SCD) | ✅ Potencialmente aplicável |
| Conglomerados prudenciais Tipo 3 | ✅ Potencialmente aplicável |
| Segmento S5, S4, S3 | ✅ Potencialmente aplicável |
| Participantes do Pix | ✅ Potencialmente aplicável |
| Open Finance / Open Banking | ✅ Potencialmente aplicável |
| ITP (Iniciadores de Transação de Pagamento) | ✅ Potencialmente aplicável |
| Subcredenciadores / Credenciadores | ✅ Potencialmente aplicável |
| Arranjos de pagamento | ✅ Potencialmente aplicável |
| Detentores de conta (Open Finance) | ✅ Potencialmente aplicável |
| Apenas bancos comerciais / múltiplos | ⚠️ Avançar para 2º passo |
| Apenas seguradoras / CVM / cooperativas | ❌ Provavelmente NÃO APLICÁVEL |
| Normas internas do Banco Central | ❌ Provavelmente NÃO APLICÁVEL |

**2º) Tema vs. produtos ativos**
Se o escopo for ambíguo ou mencionar "instituições financeiras" em geral, verificar se o tema coincide com algum produto ou atividade do iFood Pago (ver tabela completa na Seção 2 do REASONING_LAYER.md).

**3º) Exceções e fora de escopo**
Verificar se a norma é exclusivamente sobre câmbio, seguros, CVM, crédito rural, crédito imobiliário, criptoativos ou cooperativas de crédito. Se sim → NÃO APLICÁVEL.

**4º) Palavras-chave de triagem**

As seguintes palavras-chave indicam relevância para o iFood Pago quando encontradas na ementa ou no texto da norma:

| Palavra-chave | Justificativa de inclusão |
|---|---|
| `instituição de pagamento` / `IP` | Entidade principal do conglomerado |
| `sociedade de crédito direto` / `SCD` | Entidade do conglomerado |
| `conglomerado prudencial` / `tipo 3` | Classificação regulatória do grupo |
| `Pix` | Produto ativo (acesso direto) |
| `arranjo de pagamento` | Operação de cartões e Pix |
| `credenciador` / `subcredenciador` | Atividade atual e em transição |
| `conta de pagamento` / `conta pré-paga` | Produto core |
| `Open Finance` / `Open Banking` | Atividade de ITP e detentor de conta |
| `ITP` / `iniciador de transação` | Atividade de Open Finance |
| `PLD` / `lavagem de dinheiro` / `COAF` | Obrigação transversal |
| `LGPD` / `proteção de dados` / `privacidade` | Obrigação transversal |
| `proteção ao consumidor` / `usuário de SF` | Obrigação transversal |
| `segurança cibernética` / `cyber` | Obrigação transversal |
| `CADOC` | Obrigação de reporte regulatório |
| `COSIF` | Plano de contas obrigatório |
| `patrimônio de referência` / `capital` | Obrigação prudencial |
| `BaaS` / `banking as a service` | Modelo de negócio |
| `correspondente bancário` | Canal de distribuição |
| `PAT` / `benefício alimentar` | Produto ativo |
| `BNPL` / `crédito ao consumidor` | Produto ativo (via SCD) |
| `antecipação de recebíveis` | Produto ativo B2B |
| `tarifas` / `precificação de serviços` | Obrigação de transparência |

---

### 2.3 Casos de Borda Documentados

**Caso 1: Norma com escopo misto (bancos + IPs)**
A norma se aplica a bancos comerciais E a instituições de pagamento. → **APLICÁVEL** (partes relativas a IPs devem ser analisadas; partes exclusivas de bancos podem ser desconsideradas).

**Caso 2: Norma sobre tema adjacente com cláusula de IP**
Ex: Norma sobre crédito imobiliário que contém parágrafo sobre portabilidade via IP. → **APLICÁVEL** somente para o dispositivo que menciona IP, com nota de escopo parcial.

**Caso 3: Norma regulando produto em lançamento (Carteira Digital)**
O iFood Pago ainda não opera Carteira Digital, mas o produto está "em breve". → **MONITORAR**, com nota de revisão ao lançar o produto.

**Caso 4: Alteração de norma existente vs. norma completamente nova**
- Norma que *altera* norma já mapeada como APLICÁVEL: verificar se a alteração cria obrigação nova, apenas ajusta texto ou revoga obrigação. Reclassificar conforme impacto.
- Norma que *revoga* norma APLICÁVEL: verificar se a revogação elimina obrigação ou se há norma substituta. Atualizar arquivo e registrar revogação.
- Norma completamente nova: seguir fluxo padrão desde o Passo 1.

**Caso 5: Consulta pública (minuta de norma)**
A norma ainda não foi publicada em caráter definitivo. → **MONITORAR**, com nota de que está em consulta pública. A criticidade calculada é reduzida em 1 nível (ver Seção 5.2).

---

## 3. Critério 2 — Avaliação de Impacto por Pilar

> Aplicar somente para normas classificadas como ✅ APLICÁVEL.
> Para cada pilar, atribuir nível de **1 a 4** com base nas perguntas-chave.

---

### 3.1 — Pilar Compliance

**O que este pilar mede:** Grau de exposição à não-conformidade regulatória — ou seja, qual o tipo de infração que o descumprimento desta norma pode configurar perante o BCB e demais reguladores.

| Nível | Critérios concretos |
|---|---|
| **1 — Baixo** | A norma não cria obrigação legal nova; recomenda melhores práticas ou alinha com associações de classe. Ex: Comunicado BCB com orientações voluntárias. |
| **2 — Médio-Baixo** | A norma cria obrigação legal (resolução ou instrução normativa), mas não há histórico de fiscalização intensa pelo BCB nesse tema. Ex: nova obrigação de reporte CADOC sem precedente de sanção. |
| **3 — Médio-Alto** | A norma regula tema em que o BCB já realizou inspeções, enviou ofícios ou instaurou processos administrativos contra IPs ou entidades similares. Ex: norma PLD/FT em tema já investigado pelo BCB. |
| **4 — Alto** | O BCB já aplicou multas, advertências ou cassou autorizações por descumprimento de normas similares. Ex: norma de proteção ao consumidor após ciclo de sanções públicas. |

**Racional:** O iFood Pago opera em segmento sujeito à supervisão direta do BCB. A probabilidade de fiscalização e o histórico de sanções no setor de pagamentos é crescente. Este pilar calibra o risco de enforcement regulatório.

**Exemplos por nível:**
- Nível 1: Comunicado BCB com orientação sobre boas práticas de governança
- Nível 2: Nova IN BCB criando obrigação de reporte trimestral
- Nível 3: Resolução BCB sobre PLD/FT em área com inspeções recentes
- Nível 4: Norma de proteção ao consumidor após período de multas públicas a IPs

---

### 3.2 — Pilar Estratégico

**O que este pilar mede:** Interferência da norma nos objetivos estratégicos (OKRs) do iFood Pago no exercício vigente e na sustentabilidade do negócio a médio prazo.

| Nível | Critérios concretos |
|---|---|
| **1 — Baixo** | A norma não interfere em nenhum OKR do exercício vigente. Adequação não exige mudança de produto ou modelo de negócio. |
| **2 — Médio-Baixo** | A norma pode impactar até 1 OKR (ex: atrasa lançamento de feature, exige adequação em produto secundário). |
| **3 — Médio-Alto** | A norma pode impactar até 2 OKRs (ex: restringe modelo de precificação de produto core, exige redesenho de jornada). |
| **4 — Alto** | A norma impacta 3 ou mais OKRs, ameaça a sustentabilidade do negócio ou inviabiliza produto estratégico (ex: Conta de Pagamento, Pix). |

**Racional:** O iFood Pago tem produtos core (Conta de Pagamento, Pix, cartão) que sustentam a estratégia B2C e B2B. Normas que afetam esses produtos têm impacto estratégico direto, especialmente em momentos de lançamento (Carteira Digital) ou transição (subcredenciador → credenciador).

**Exemplos por nível:**
- Nível 1: Norma exigindo alteração de modelo de e-mail de comunicação com o BCB
- Nível 2: Norma que exige novo campo em relatório, atrasando release de produto
- Nível 3: Norma que altera regras de tarifas do Pix, impactando modelo de receita
- Nível 4: Norma que eleva requisitos de capital a ponto de limitar crescimento da carteira de crédito

---

### 3.3 — Pilar Financeiro

**O que este pilar mede:** Custo financeiro estimado de adequação ou multa potencial, expresso como percentual do Patrimônio de Referência (PR) do conglomerado prudencial.

| Nível | Critérios concretos | Referência absoluta |
|---|---|---|
| **1 — Baixo** | Custo de adequação ou multa potencial abaixo de 0,5% do PR | Abaixo de R$ 175.000 |
| **2 — Médio-Baixo** | Entre 0,6% e 3% do PR | R$ 175.000 a R$ 1.000.000 |
| **3 — Médio-Alto** | Entre 3,1% e 5% do PR | R$ 1.000.000 a R$ 1.750.000 |
| **4 — Alto** | Acima de 5% do PR | Acima de R$ 1.750.000 |

**Racional:** O Patrimônio de Referência é a métrica de dimensionamento financeiro do conglomerado prudencial. Expressar o impacto financeiro em % do PR permite comparação consistente entre normativos e alinhamento com a metodologia interna de gestão de riscos do iFood Pago.

**Exemplos por nível:**
- Nível 1: Norma exigindo nova funcionalidade de relatório com custo de TI estimado em R$ 50.000
- Nível 2: Norma exigindo contratação de auditor externo anual (R$ 500.000/ano)
- Nível 3: Norma exigindo aumento de capital regulatório (R$ 1,2M de imobilização)
- Nível 4: Multa potencial por descumprimento de norma PLD/FT (> R$ 2M)

---

### 3.4 — Pilar Legal

**O que este pilar mede:** Natureza e severidade da sanção jurídica pelo descumprimento da norma — do extrajudicial ao criminal.

| Nível | Critérios concretos |
|---|---|
| **1 — Baixo** | O descumprimento pode gerar apenas notificações extrajudiciais ou recomendações de órgãos de classe. |
| **2 — Médio-Baixo** | O descumprimento pode gerar disputas legais formais, ações civis ou necessidade de provisões contábeis. |
| **3 — Médio-Alto** | O descumprimento pode resultar em condenações civis ou administrativas (multas, restrições operacionais, acordos). |
| **4 — Alto** | O descumprimento pode resultar em condenações criminais (responsáveis) e/ou suspensão ou encerramento das atividades do iFood Pago. |

**Racional:** O Nível 4 é o pior cenário possível: cassação da autorização de funcionamento pelo BCB ou responsabilização criminal de diretores. Este pilar alerta para normas cuja violação vai além da multa financeira e compromete a própria existência jurídica do negócio.

**Exemplos por nível:**
- Nível 1: Norma de boas práticas com recomendação da Abipag
- Nível 2: Norma que, se descumprida, gera reclamação em juízo por cliente lesado
- Nível 3: Norma de tarifas com sanção administrativa de multa pelo BCB
- Nível 4: Norma PLD/FT cuja violação pode ensejar crime de lavagem e cassação da IP

---

### 3.5 — Pilar Operacional

**O que este pilar mede:** Amplitude do impacto nos processos e na base de clientes — percentual de clientes afetados e grau de mobilização interna necessário para adequação.

| Nível | Clientes afetados | Mobilização interna |
|---|---|---|
| **1 — Baixo** | Até 5% da base de clientes | Colaboradores até grade 10 (nível operacional) |
| **2 — Médio-Baixo** | Até 10% da base | Grades 11–12 (coordenação) |
| **3 — Médio-Alto** | Até 20% da base | Grades 13–14 (gerência / diretoria) |
| **4 — Alto** | 30% ou mais da base | Acima de grade 14 / situação de crise |

**Racional:** O iFood Pago atende milhões de usuários B2C e restaurantes B2B. Normas que impactam produtos core (Pix, Conta de Pagamento) atingem a totalidade da base e exigem mobilização da alta gestão para adequação em prazo regulatório.

**Exemplos por nível:**
- Nível 1: Norma que altera modelo de relatório interno, sem impacto no cliente final
- Nível 2: Norma que exige novo campo no cadastro de ~10% dos clientes pessoa jurídica
- Nível 3: Norma que altera limites de operação do Pix para PF (20% da base afetada)
- Nível 4: Norma que suspende ou restringe operações de Conta de Pagamento (toda a base)

---

### 3.6 — Pilar Segurança da Informação *(aplicar somente quando relevante)*

**O que este pilar mede:** Risco de violação dos pilares de Confidencialidade, Integridade e Disponibilidade (CIA) dos sistemas e dados do iFood Pago.

> **Nota:** Este pilar deve ser incluído na avaliação apenas quando a norma tiver relação com segurança cibernética, proteção de dados, disponibilidade de sistemas ou LGPD. Para normas sem componente de SI, omitir este pilar do cálculo da média.

| Nível | Pilares CIA violados | Clientes afetados | Indisponibilidade |
|---|---|---|---|
| **1 — Baixo** | Nenhum ou 1 pilar em ativos não críticos | Até 5% | Até 1 hora |
| **2 — Médio-Baixo** | 1 pilar em ativos críticos | Até 10% | Até 4 horas |
| **3 — Médio-Alto** | 2 pilares em ativos críticos | Até 20% | Até 8 horas |
| **4 — Alto** | 3 pilares em ativos críticos | 30% ou mais | Mais de 8 horas |

---

## 4. Critério 3 — Probabilidade

### 4.1 Escala de Probabilidade (4 Níveis)

| Nível | Nome | Frequência / Circunstância |
|---|---|---|
| **1** | Remota | A cada 5+ anos / ocorre apenas em circunstâncias excepcionais |
| **2** | Possível | A cada 1–5 anos / pode se manifestar em algum momento |
| **3** | Provável | Uma vez ao ano / manifesta-se com frequência |
| **4** | Certamente | Várias vezes ao ano / manifesta-se com alta frequência |

**Definição de cada nível:**

**Remota (1):** O risco de não-cumprimento ou impacto negativo é improvável dado o contexto atual. A norma é informativa ou esclarecedora, não cria novas obrigações, ou o iFood Pago já possui controle plenamente implementado.

**Possível (2):** O risco existe e pode se manifestar, mas não é iminente. A norma cria obrigação com prazo futuro ou altera norma existente de forma incremental.

**Provável (3):** O risco de impacto negativo é realista e provável dado o contexto atual. A norma já está em vigor ou tem prazo imediato, exigindo adequação próxima.

**Certamente (4):** O risco é quase certo de se materializar. O BCB fiscaliza ativamente o tema, há histórico documentado de sanções, e a ausência de adequação é detectável na próxima inspeção.

---

**Critérios de identificação por situação do normativo:**

| Situação da norma | Probabilidade atribuída | Racional |
|---|---|---|
| Norma nova com prazo já em vigor | **Provável (3)** | A obrigação é imediata e o BCB pode exigir comprovação de conformidade a qualquer momento |
| Norma nova com prazo futuro | **Possível (2)** | Há tempo para adequação; o risco só se materializa se o prazo não for cumprido |
| Norma que altera norma existente | **Possível (2)** | A base já existe; o risco é de não-atualização pontual |
| Norma com histórico documentado de fiscalização BCB | **Certamente (4)** | O BCB demonstrou interesse ativo no tema; o próximo ciclo de supervisão pode incluir verificação |
| Norma informativa / esclarecedora (sem novas obrigações) | **Remota (1)** | Não há nova obrigação; risco de impacto negativo é mínimo |

**Racional da abordagem especial para normativos BCB:**

Em gestão de riscos clássica, probabilidade refere-se à chance de um evento adverso ocorrer. Para normativos BCB, a lógica é diferente: a publicação da norma é um **fato certo** — ela foi publicada e existe. A probabilidade que avaliamos aqui é a probabilidade de **não-cumprimento** ou de **impacto negativo** sobre o negócio, ou seja:

- A probabilidade de o iFood Pago não estar em conformidade quando exigido; ou
- A probabilidade de o BCB identificar e sancionar uma eventual não-conformidade.

Por isso, normas com prazo vencido ou histórico de fiscalização intensa recebem probabilidade mais alta — não porque são mais prováveis de existir, mas porque o risco de impacto negativo por não-conformidade é maior.

---

## 5. Critério 4 — Criticidade Final

### 5.1 Matriz Impacto × Probabilidade

**Fórmula:**
```
Pontuação = Impacto (média dos pilares, arredondada) × Probabilidade (1-4)
Faixa: 1 a 16 pontos
```

**Tabela de Quadrantes A–P:**

| Quadrante | Pontuação | Impacto | Probabilidade | Criticidade |
|---|---|---|---|---|
| **A** | 16 | Muito Alto (4) | Certamente (4) | 🔴 CRÍTICO MÁXIMO |
| **E** | 15 | Muito Alto (4) | Provável (3) | 🔴 CRÍTICO |
| **B** | 14 | Alto (3,5→4*) | Certamente (4) | 🔴 CRÍTICO |
| **F** | 13 | Alto (3,5→4*) | Provável (3) | 🔴 CRÍTICO |
| **I** | 12 | Muito Alto (4) | Possível (2)* | 🟠 ALTO |
| **C** | 11 | Médio (3) | Certamente (4) | 🟠 ALTO |
| **J** | 10 | Alto (3,5→4*) | Possível (2)* | 🟠 ALTO |
| **G** | 9 | Médio (3) | Provável (3) | 🟠 ALTO |
| **M** | 8 | Muito Alto (4) | Remota (1)* | 🟡 MÉDIO |
| **D** | 7 | Médio-Baixo (2) | Certamente (4) | 🟡 MÉDIO |
| **K** | 6 | Médio (3) | Possível (2) | 🟡 MÉDIO |
| **N** | 5 | Alto (3,5→4*) | Remota (1)* | 🟡 MÉDIO |
| **H** | 4 | Médio-Baixo (2) | Provável (3) | 🟢 BAIXO |
| **O** | 3 | Médio (3) | Remota (1) | 🟢 BAIXO |
| **L** | 2 | Médio-Baixo (2) | Possível (2) | 🟢 BAIXO |
| **P** | 1 | Baixo (1) | Remota (1) | 🟢 BAIXO — BAIXÍSSIMO |

*Alguns quadrantes refletem arredondamentos da média de pilares.

**Lógica de cada faixa de criticidade:**

| Criticidade | Pontuação | Lógica |
|---|---|---|
| 🔴 **CRÍTICO** | 13–16 | Combinação de alto impacto E alta probabilidade. Risco de dano grave e iminente. Ação imediata. |
| 🟠 **ALTO** | 9–12 | Impacto elevado OU probabilidade alta (mas não ambos no máximo). Ação urgente planejada. |
| 🟡 **MÉDIO** | 5–8 | Impacto ou probabilidade moderados. Adequação no ciclo normal de compliance. |
| 🟢 **BAIXO** | 1–4 | Impacto baixo e/ou probabilidade remota. Monitoramento regular suficiente. |

**Racional dos limiares:**

Os limiares foram definidos com base na metodologia interna de gestão de riscos do iFood Pago (Calculadora de Riscos — apontamentos_ifoodpago_v2.xlsx), que usa escala quadrada 4×4 (máximo 16 pontos). A divisão em 4 faixas segue o princípio da distribuição equilibrada:
- Faixa CRÍTICO (13–16): 4 quadrantes — os piores cenários que exigem resposta imediata.
- Faixa ALTO (9–12): 4 quadrantes — risco significativo que exige plano estruturado.
- Faixa MÉDIO (5–8): 4 quadrantes — risco gerenciável no ciclo normal.
- Faixa BAIXO (1–4): 4 quadrantes — risco aceitável com monitoramento.

Esta distribuição é consistente com o perfil de risco de uma instituição S5 em transição — conservadora o suficiente para não subestimar riscos, mas sem criar alarmes desnecessários para normas verdadeiramente de baixo impacto.

---

### 5.2 Fatores de Ajuste de Criticidade

Situações que podem elevar ou reduzir a criticidade calculada pela fórmula base:

#### Fatores que ELEVAM a criticidade:

| Fator | Ajuste | Racional |
|---|---|---|
| Prazo de adequação ≤ 30 dias corridos | +1 nível | Urgência comprimida exige mobilização imediata e pode inviabilizar adequação completa |
| Prazo de adequação ≤ 15 dias úteis | +1 nível adicional | Urgência crítica — quase impossível de adequar sem impacto operacional |
| Sanção prevista: cassação de autorização ou suspensão de atividades | +1 nível | Risco existencial para o negócio, independentemente da probabilidade |
| Norma afeta produto core (Conta de Pagamento, Pix, cartão de crédito) | +1 nível | Impacto na operação principal do iFood Pago, com efeito cascata em receita e clientes |
| BCB em processo ativo de fiscalização do tema declarado | +1 nível | A probabilidade de detecção de não-conformidade é alta no curto prazo |

#### Fatores que REDUZEM a criticidade:

| Fator | Ajuste | Racional |
|---|---|---|
| Política interna existente já atende parcialmente a norma | -1 nível | Controle compensatório reduz esforço e risco de não-conformidade |
| Controle compensatório documentado e testado | -1 nível | Evidência de mitigação parcial reduz probabilidade de impacto negativo |
| Norma em fase de consulta pública (não vigente) | -1 nível | Ainda não é obrigação; pode ser alterada antes de publicação definitiva |
| Normativo informativo sem nova obrigação material | -1 nível | Sem obrigação nova, risco de não-conformidade é mínimo |

> **Regra:** O ajuste pode mover a criticidade no máximo 1 nível acima ou abaixo do calculado. Não é possível, por exemplo, elevar BAIXO diretamente para CRÍTICO apenas por fatores de ajuste.

---

### 5.3 Relação entre Criticidade e Prazo Recomendado

| Criticidade | Prazo de Adequação Recomendado | Times a Acionar Obrigatoriamente |
|---|---|---|
| 🔴 **CRÍTICO** | **5 dias úteis** | Liderança de Compliance + Jurídico + Área(s) impactada(s) + C-Level se necessário |
| 🟠 **ALTO** | **15 dias úteis** | Compliance + Área(s) impactada(s) + Gestores diretos |
| 🟡 **MÉDIO** | **30 dias corridos** | Compliance + Área(s) impactada(s) |
| 🟢 **BAIXO** | **Ciclo regular de revisão** | Compliance (registro e acompanhamento periódico) |

---

## 6. Critério 5 — Identificação de Áreas e Times

### 6.1 Mapeamento Norma → Área

A lógica de acionamento de áreas é baseada no tema principal da norma:

| Tema da Norma | Áreas a Acionar |
|---|---|
| Capital / Patrimônio Líquido / Prudencial | Finanças + Riscos + Compliance |
| Pix (regulamento e normas específicas) | Produto Pix + Tecnologia + Compliance |
| Conta de Pagamento / wallets digitais | Produto + Compliance + Jurídico |
| Cartão de crédito / benefícios (PAT) | Produto Cartão + Compliance |
| BNPL / crédito ao consumidor | Crédito + Compliance + Jurídico |
| Antecipação de recebíveis | Crédito + Produto B2B + Compliance |
| PLD/FT / Prevenção a Fraudes | PLD/AML team + Compliance + Jurídico |
| LGPD / Privacidade / Proteção de dados | DPO + Jurídico + Compliance |
| Proteção ao consumidor / Usuário de SF | SAC + Compliance |
| Tecnologia / Segurança cibernética | CISO + Tecnologia + Compliance |
| CADOCs / COSIF / Reporte prudencial | Contabilidade + Regulatório + Compliance |
| Open Finance / ITP | Produto Open Finance + Compliance |
| Credenciamento / Subcredenciamento | Operações + Produto POS + Compliance |
| BaaS / Correspondente bancário | BaaS team + Jurídico + Compliance |
| Tesouraria / Liquidez / Gestão de ativos | Finanças + Riscos + Compliance |
| Tarifas / Precificação de serviços | Produto + Financeiro + Compliance |
| Auditoria / Controles internos | Controles Internos + Compliance |
| Segmentação (S5/S4/S3) | Riscos + Finanças + Compliance + C-Level |

### 6.2 Times Sempre Acionados (Independente do Tema)

Para qualquer normativo classificado como ✅ **APLICÁVEL**, as seguintes ações são sempre realizadas:

1. **Giovanna Batistutti (Compliance iFood Pago)** — notificada via Slack #agenda-normativa-ifoodpago
2. **Registro no log de execução** — data, número da norma, classificação, criticidade
3. **Arquivo .md gerado** — com íntegra relevante, resumo executivo e avaliação de risco

Para normativos com criticidade 🔴 **CRÍTICO** ou 🟠 **ALTO**, o Slack blocks inclui link para o arquivo completo e botão de feedback ao agente.

---

## 7. Critério 6 — Resumo Executivo

### 7.1 O que Deve Constar no Resumo Executivo

**Por que reproduzir artigos, incisos e alíneas ao invés de resumir genericamente:**

O resumo genérico ("a norma estabelece regras sobre X") é insuficiente para Compliance. É necessário reproduzir os dispositivos específicos que impactam o iFood Pago porque:
1. O texto legal vincula — é o artigo que cria a obrigação, não o resumo.
2. O auditor ou gestor precisa ver exatamente o que é exigido, não uma interpretação.
3. A marcação (novo)/(alterado) permite identificar imediatamente o que mudou em relação à versão anterior.

**Estrutura do resumo executivo:**

```markdown
## Resumo Executivo

### Dispositivos Aplicáveis ao iFood Pago

**Art. X — [Título do artigo]** *(novo)*
Texto integral do artigo...

  **§ 1º** Texto do parágrafo...
  **I —** Texto do inciso...
  **a)** Texto da alínea...

**Art. Y — [Título do artigo]** *(alterado)*
[Texto anterior]: ...
[Novo texto]: ...
```

**Como identificar artigos novos vs. alterados:**
- **(novo):** O número do artigo não existia na norma anterior ou é artigo em norma completamente nova.
- **(alterado):** A norma em análise usa expressões como "passa a vigorar com a seguinte redação", "fica acrescido", "fica revogado" referindo-se a artigos de normas anteriores.
- Verificar se há referência a artigo de norma estruturante em vigília permanente (Seção 5 do REASONING_LAYER.md).

**Como extrair a data de vigência:**
- Os artigos finais de toda resolução/instrução normativa BCB contêm a data de vigência.
- Padrão de busca: "Esta Resolução entra em vigor em [data]" ou "Esta Instrução Normativa entra em vigor na data de sua publicação."
- Se a data de vigência for "na data de publicação", usar a data da publicação no DOU.
- Se houver vigência escalonada por tipo de instituição (ex: S1/S2 antes de S3/S4/S5), identificar qual prazo se aplica ao iFood Pago.

**Regra de marcação:**
- `*(novo)*` — artigo, inciso ou alínea que não existia antes desta publicação
- `*(alterado)*` — artigo, inciso ou alínea que existia e foi modificado por esta publicação
- Sem marcação — dispositivo reproduzido integralmente sem alteração (contexto de norma nova)

---

## 8. Registro de Ajustes e Feedbacks Incorporados

> Esta seção é atualizada automaticamente quando feedbacks da equipe são registrados via botão "💬 Feedback ao Claw" nas notificações Slack ou via mensagem direta no canal #agenda-normativa-ifoodpago.

### 8.1 Como os Feedbacks Alteram os Critérios

**Feedback positivo (classificação correta):**
- Reforça o critério atual — sem alteração no DECISION_MAP.md.
- Registrado no log de execução como confirmação de acerto.
- Contribui para calibração estatística de acurácia.

**Feedback corretivo (classificação errada):**
- O responsável humano (Giovanna ou equipe de Compliance) informa: (a) qual deveria ser a classificação correta; (b) qual foi o critério mal-aplicado; (c) se há regra a ser adicionada.
- O agente documenta: normativo em questão, classificação automática, classificação correta, e a nova regra derivada.
- A nova regra é adicionada ao REASONING_LAYER.md e ao DECISION_MAP.md (Seção relevante).
- A classificação corrigida sobrepõe o critério automático (ver Princípio do Feedback, Seção 9).

**Feedback de escopo (normativo fora do radar):**
- Se um normativo relevante não foi capturado → adicionar palavra-chave à lista de triagem (Seção 2.2).
- Se um normativo irrelevante foi notificado → adicionar palavra-chave de exclusão ou refinar critério de tema.
- Ambos os casos são documentados com justificativa.

---

### 8.2 Log de Ajustes

| Data | Normativo | Feedback recebido | Critério ajustado | Responsável |
|---|---|---|---|---|
| *(a ser preenchido conforme feedbacks chegarem)* | | | | |

---

## 9. Princípios de Raciocínio

Os princípios abaixo guiam as decisões do agente em casos ambíguos, onde os critérios dos itens anteriores não produzem resultado inequívoco.

**1. Princípio da Precaução Regulatória**
> Na dúvida entre MONITORAR e APLICÁVEL, sempre classificar como APLICÁVEL.

*Racional:* O custo de notificar desnecessariamente é baixo (Giovanna avalia e descarta se necessário). O custo de não notificar um normativo realmente aplicável pode ser uma sanção do BCB. O erro do tipo "falso negativo" (deixar de identificar normativo aplicável) é mais grave que o erro do tipo "falso positivo" (notificar normativo de monitoramento).

---

**2. Princípio da Anterioridade**
> Sempre verificar se a norma revoga ou altera norma anterior já mapeada como APLICÁVEL.

*Racional:* Uma nova resolução BCB muitas vezes apenas altera artigos específicos de normas estruturantes (ex: Resolução BCB 80/2021). O agente deve cruzar com as Normas Estruturantes em Vigília Permanente (Seção 5 do REASONING_LAYER.md) e identificar o impacto sobre obrigações já conhecidas.

---

**3. Princípio da Especificidade**
> Norma específica para IPs prevalece sobre norma geral para IFs na determinação de aplicabilidade.

*Racional:* Quando uma norma é direcionada especificamente a IPs (mesmo que bancos também sejam mencionados), os dispositivos específicos para IPs têm maior peso na avaliação de impacto. Da mesma forma, norma exclusiva de banco comercial não se aplica a IP por extensão automática.

---

**4. Princípio do Prazo**
> Prazo de adequação curto (≤ 30 dias) eleva automaticamente a criticidade calculada em 1 nível.

*Racional:* O prazo de adequação é fator de risco independente da gravidade do impacto. Uma norma de impacto médio com prazo de 10 dias pode ser mais urgente que uma norma de impacto alto com prazo de 6 meses. O prazo curto é um multiplicador de urgência.

---

**5. Princípio do Feedback**
> Classificação corrigida por Giovanna ou equipe de Compliance sempre sobrepõe o critério automático.

*Racional:* O agente é uma ferramenta de auxílio, não substituto do julgamento humano especializado. A Analista de Compliance tem contexto de negócio, histórico de relacionamento com o regulador, e conhecimento de riscos não documentados que o agente não possui. Sua correção é a decisão final e deve atualizar as regras para aprendizado contínuo.

---

*Documento gerado automaticamente pelo Claw com base no REASONING_LAYER.md e nas políticas internas do iFood Pago.*
*Atualizado em: 2026-05-22 — Horário de Brasília (BRT)*

---

## 10. Arquitetura RAG — Memória do Pipeline BCB

> Esta seção descreve a arquitetura de memória do pipeline BCB, implementada como
> um sistema RAG (Retrieval-Augmented Generation) para melhorar a qualidade das análises
> ao longo do tempo.

### 10.1 Visão Geral

O pipeline BCB usa uma estrutura de memória hierárquica em dois níveis:

```
data/normativos-bcb/
  memoria/
    normativos/          ← NÍVEL 1: uma unidade atômica por normativo
      {ID}.md            → avaliação + raciocínio + resultado + feedbacks
    temas/               ← NÍVEL 2: padrões acumulados por tema (RAG temático)
      cosif.md
      pix.md
      open_finance.md
      pld_ft.md
      credito.md
      seguranca_cibernetica.md
      protecao_consumidor.md
      lgpd_dados.md
      arranjos_pagamento.md
      geral.md
```

### 10.2 Nível 1 — Normativos (`memoria/normativos/{ID}.md`)

**Formato do ID:** `{tipo_normalizado}_{numero}`

Exemplos:
- `resolucao_bcb_570`
- `instrucao_normativa_bcb_737`
- `resolucao_cmn_5303`

Cada arquivo é a **unidade atômica de memória** do normativo. Contém:
- Identificação completa (ementa, publicação, vigência, fonte)
- Linha de raciocínio completa (5 passos)
- Resultado final (classificação, criticidade, áreas, prazo)
- Feedbacks recebidos de Giovanna (seção cumulativa)
- Tags para RAG (temas, produtos, políticas, resultado, criticidade)

### 10.3 Nível 2 — Temas (`memoria/temas/{tema}.md`)

Cada arquivo de tema acumula padrões observados em **todas** as normas daquele tema.
É o que alimenta o RAG quando chega uma norma nova sobre o mesmo assunto.

Contém:
- Histórico de normas analisadas (tabela)
- Padrões identificados (observações repetidas)
- Calibração de criticidade para o tema
- Regras aprendidas de feedbacks de Giovanna
- Normativos relacionados (relações entre normas)

### 10.4 Como o Pipeline Consome a Memória

No início de cada execução, o pipeline carrega como contexto:

1. **REASONING_LAYER.md** — sempre (contexto estático de negócio)
2. **DECISION_MAP.md** — sempre (regras de decisão)
3. **memoria/temas/{tema_da_norma}.md** — por norma, se existir
4. **memoria/normativos/** — 3 normativos mais recentes do mesmo tema (por similaridade)

### 10.5 Como o Pipeline Grava na Memória

Ao processar cada normativo:
1. Cria/atualiza `memoria/normativos/{ID}.md` com o formato unificado
2. Ao finalizar, atualiza `memoria/temas/{tema}.md` com o novo normativo no histórico

Ao receber feedback (via FEEDBACK_INSTRUCOES_PLANNER):
1. Localiza `memoria/normativos/{ID}.md`
2. Adiciona o feedback na seção "Feedbacks Recebidos"
3. Atualiza `memoria/temas/{tema}.md` com a regra aprendida
4. Se for regra geral: adiciona no DECISION_MAP.md Seção 8.2

### 10.6 Regras Gerais Aprendidas (de Feedbacks)

> Regras gerais extraídas de feedbacks de Giovanna que se aplicam a qualquer normativo.
> Migradas de FEEDBACK.md (agora deprecated).
> Formato: [DATA] REGRA: {descrição} | ORIGEM: Feedback #{n}

*(A ser preenchido conforme feedbacks chegarem)*

---

*Documento atualizado pelo pipeline BCB — Claw | iFood Pago Compliance*
*Atualizado em: 2026-05-22 — Refatoração para arquitetura RAG*
