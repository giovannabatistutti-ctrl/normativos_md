# Feedback da Equipe — Análise de Normativos BCB

> Feedbacks recebidos de Giovanna Batistutti (Compliance — iFood Pago) e equipe.
> Consultado automaticamente pelo pipeline a cada execução para ajustar critérios de análise.
> Atualizado pelo Planner (Claw) sempre que um feedback é recebido no chat.

---

## Como usar este arquivo (para o agente)

Antes de classificar qualquer normativo, ler todos os registros neste arquivo e:
1. Verificar se há feedback sobre o normativo específico (buscar pelo código/número)
2. Verificar se há **regras gerais** que afetam critérios de classificação
3. Verificar se há **ajustes de escopo** (palavras-chave a incluir/excluir)
4. Regra absoluta: feedback corretivo de Giovanna **sempre** sobrepõe a classificação automática

---

## Regras Gerais Ativas

> Regras extraídas de feedbacks que se aplicam a qualquer normativo futuro.
> Formato: [DATA] REGRA: {descrição} | ORIGEM: Feedback #{n}

[2026-06-01] REGRA: INs BCB sobre Jornada Otimizada (Open Finance) — o iFood Pago é ITP ✅ e Detentor de Conta ✅, mas NÃO é Transmissor de Dados ❌ nem Receptor de Dados ❌. A oferta da Jornada Otimizada é obrigatória apenas para quem acumula Transmissor de Dados + Detentor de Conta simultaneamente. Para o iFood Pago: classificar como ⚠️ MONITORAR (pode participar opcionalmente como ITP) | ORIGEM: Feedback IN BCB 740 + Giovanna 01/06/2026

[2026-05-22] REGRA: Normas de crédito imobiliário, financiamento habitacional e SFH/SFN habitacional são NÃO APLICÁVEL ao iFood Pago | ORIGEM: Feedback #1

---

## Ajustes de Escopo

> Palavras-chave ou temas adicionados/removidos da triagem com base em feedbacks.

### Incluir na triagem (palavras-chave adicionadas)
*(nenhuma regra registrada ainda)*

### Excluir da triagem (falsos positivos identificados)
- financiamento habitacional, crédito imobiliário, SFH, SFN habitacional (Feedback #1)

---

## Registro de Feedbacks

### Feedback #1
- **Data:** 2026-05-22 10:00 (Brasília)
- **Normativo:** Resolução CMN nº 5304
- **Classificação automática:** ⚠️ MONITORAR — Criticidade 🟡 MÉDIO
- **Feedback de Giovanna:** "A Resolução CMN 5304 trata de financiamento habitacional — isso está fora do escopo do iFood Pago. A classificação deveria ser NÃO APLICÁVEL, não MONITORAR."
- **Tipo de feedback:** Corretivo
- **Ajuste aplicado:**
  - Aplicabilidade: alterada para ❌ NÃO APLICÁVEL
  - Criticidade: não aplicável (norma fora de escopo)
  - Área acionada: nenhuma (fora de escopo)
  - Regra geral criada: sim — crédito imobiliário/habitacional é NÃO APLICÁVEL ao iFood Pago
- **Status:** Incorporado

---

## Template para novos feedbacks

Cada novo feedback deve seguir este formato:

### Feedback #{n}
- **Data:** {YYYY-MM-DD HH:MM} (Brasília)
- **Normativo:** {Tipo + número, ex: Resolução BCB nº 123} ou "Geral"
- **Classificação automática:** {APLICÁVEL / MONITORAR / NÃO APLICÁVEL}
- **Feedback de Giovanna:** {texto exato do feedback}
- **Tipo de feedback:** {Corretivo | Confirmação | Ajuste de escopo | Ajuste de criticidade | Outro}
- **Ajuste aplicado:**
  - Aplicabilidade: {mantida / alterada para X}
  - Criticidade: {mantida / alterada para X}
  - Área acionada: {adicionada/removida X}
  - Regra geral criada: {sim/não — se sim, qual}
- **Status:** {Incorporado | Pendente}

---

## Formulário de Feedback Estruturado

As perguntas abaixo são enviadas automaticamente na mensagem do Slack.
Ao clicar em "Feedback ao Claw" e abrir o Toqan, responda identificando:

### Perguntas do formulário

**1. Aplicabilidade** — A classificação automática está correta?
   - Opções: Sim / Não (especificar) / Parcialmente (especificar)

**2. Criticidade** — O nível de criticidade está adequado?
   - Opções: Sim / Deveria ser mais alto / Deveria ser mais baixo / Observação livre

**3. Áreas e times** — As áreas identificadas estão corretas?
   - Opções: Sim / Falta incluir (quais) / Retirar (quais)

**4. Resumo executivo** — O resumo capturou os pontos essenciais?
   - Opções: Sim, completo / Faltou (o quê) / Está incorreto em (o quê)

**5. Prazo de adequação** — O prazo sugerido é realista?
   - Opções: Sim / Deve ser alterado para (qual)

**6. Observações gerais** — Alguma informação para análises futuras?
   - Campo livre

### Como o Claw processa o feedback

Ao receber suas respostas:
1. Identifica o normativo referenciado
2. Registra no FEEDBACK.md com todos os campos preenchidos
3. Se corretivo: atualiza o .md do normativo no GitHub
4. Se regra geral: adiciona em "Regras Gerais Ativas" para influenciar análises futuras
5. Confirma o registro para você no chat

---
## Feedback: IN BCB 738 — 2026-05-27

**Normativo:** Instrução Normativa BCB nº 738, de 27/05/2026
**ID:** normativos_52915
**Classificação automática:** NÃO APLICÁVEL (confiança: MÉDIA)
**Feedback da Giovanna:** ✅ CORRETO
**Data do feedback:** 2026-05-27
**Observações:** Classificação confirmada como correta pela analista. Confiança pode ser elevada para ALTA em futuras análises de normativos do mesmo tipo/escopo.

**Impacto no reasoning layer:** Reforça padrão de classificação NÃO APLICÁVEL para este tipo de IN BCB. Sem alteração necessária nas regras.

---
## Feedback: IN BCB 740 — 2026-06-01

**Normativo:** Instrução Normativa BCB nº 740, de 29/05/2026
**ID:** normativos_52919
**Classificação automática:** ✅ APLICÁVEL — Criticidade 🟡 MÉDIO
**Feedback da Giovanna (via Slack thread #agenda-normativa-ifoodpago, 01/06/2026 09:41):**
> "Errado: A Instrução Normativa BCB nº 740 estabelece as orientações, as condições e os prazos para a realização de testes em produção pelas instituições participantes relativos ao compartilhamento de serviço otimizado de iniciação de transação de pagamento com compartilhamento de dados (jornada otimizada) no Open Finance."

**Tipo de feedback:** Corretivo — a justificativa automática estava incorreta (mencionou "vigilância sanitária" erroneamente). A classificação APLICÁVEL estava **correta**, mas o resumo/justificativa estava errado.

**Ajuste aplicado:**
- Aplicabilidade: **mantida como ✅ APLICÁVEL** (a norma de fato se aplica ao iFood Pago como ITP/Open Finance)
- Justificativa corrigida: A IN BCB nº 740 trata de testes em produção da jornada otimizada de ITP (Iniciador de Transação de Pagamento) no Open Finance — aplicável diretamente ao iFood Pago como ITP
- Crítica ao conteúdo do resumo: a análise LLM gerou justificativa de "não aplicável por vigilância sanitária", completamente equivocada — indica problema no texto integral capturado
- Regra geral criada: sim — INs BCB sobre jornada otimizada / ITP / Open Finance são APLICÁVEIS ao iFood Pago (ITP)
- Área acionada: Compliance + Produtos Open Finance / ITP (mantidas)

**Status:** Incorporado

---
## Feedback: Regra Geral — Filtro de Órgão Emitente — 2026-06-01

**Data:** 2026-06-01 (Brasília)
**Normativo:** Geral (todos os normativos)
**Tipo de feedback:** Regra de sistema — filtro de órgão emitente

[2026-06-01] REGRA: O sistema analisa EXCLUSIVAMENTE normativos de BCB/CMN. Qualquer texto integral capturado que pertença a outro órgão regulador (ANVISA, ANATEL, ANEEL, SUSEP, CVM, etc.) deve ser descartado e o normativo reprocessado sem texto integral, usando a ementa como fallback | ORIGEM: Feedback Giovanna Batistutti — 01/06/2026

**Contexto:** O texto de uma Resolução-RE da ANVISA foi capturado erroneamente como texto integral da IN BCB 740 (publicados no mesmo DOU, na mesma data/seção). O fallback `if hits: return hits` em `captura_dou.py` retornava qualquer resultado sem validar o órgão emitente.

**Correções implementadas:**
- `captura_dou.py`: Removido fallback que retornava hits de outros órgãos; adicionada função `_texto_e_de_orgao_valido()`
- `pipeline_bcb.py`: Adicionada função `_texto_pertence_ao_normativo_bcb()` com chamada em `fetch_full_text()`
- `DECISION_LAYER.md`: PASSO 0 adicionado como regra absoluta de filtro por órgão emitente

**Status:** Incorporado

---
## Feedback: Resolução BCB 571 — 2026-06-01

**Normativo:** Resolução BCB nº 571, de 28/05/2026
**ID:** normativos_52916
**Classificação automática:** ⚠️ MONITORAR (confiança: MÉDIA)
**Feedback da Giovanna (via chat Toqan, 01/06/2026):**

> "Monitorar está correto, mas o resumo deveria ser mais completo, segue o resumo que elaborei:
> 
> A Res. BCB 571/2026 altera o art. 81 da Res. BCB 352/2023 que determina os níveis de provisão para perdas esperadas (ECL) associadas ao risco de crédito em cada tipo de carteira.
> 
> Vigência: 28/05/2026
> 
> A Res. 571 ajusta a Carteira 1 (C1) para provisão de perdas de crédito, incluindo: (a) créditos com alienação fiduciária de imóveis; (b) créditos com garantia fidejussória soberana (União, governos centrais estrangeiros, BCs) e multilaterais; (c) créditos garantidos por fundo garantidor com participação majoritária da União.
> 
> Impacto iFood Pago: Se não há carteira de crédito com essas garantias (imobiliária/soberana/fundos garantidores federais), o efeito contábil direto tende a ser nulo. Exposições típicas de antecipação/desconto de recebíveis (cessão/penhor/cessão fiduciária de recebíveis) permanecem enquadradas em C3 (inalterado).
> 
> IMPORTANTE: Estamos discutindo a participação no programa do BNDES (FGI) que conta com garantia pelo BNDES. Precisamos entender se o fundo garantidor possui participação majoritária da União (art. 81, I, c) ou qual a forma de garantia do programa.
> 
> Eventuais reflexos em CADOCs 4010/4016 (balancetes/balanços), 4111 (saldos diários) e DFs/notes (9010/9011), por variação de contas de provisão, ECL e resultado do período."

**Tipo de feedback:** Complementação de resumo executivo

**Ajuste aplicado:**
- Classificação: **mantida como ⚠️ MONITORAR** (estava correta)
- Resumo: substituído pelo resumo elaborado pela analista (muito mais preciso e completo)
- Ponto de atenção: adicionada análise do programa BNDES/FGI com tabela de enquadramento por tipo de garantia
- Áreas acionadas: Contabilidade/COSIF, Crédito/SCD, Compliance Regulatório
- Pessoa a acionar: @gabriela.gusella para verificar Regulamento FGI

**Impacto no reasoning layer:** Demonstra que análise automática acertou a classificação (MONITORAR), mas o resumo gerado estava incompleto porque o texto integral capturado estava errado (Portaria TRT em vez da Res. BCB). Reforça a importância do filtro de órgão emitente implementado hoje.

**Status:** Incorporado
