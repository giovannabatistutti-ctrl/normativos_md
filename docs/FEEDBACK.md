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
