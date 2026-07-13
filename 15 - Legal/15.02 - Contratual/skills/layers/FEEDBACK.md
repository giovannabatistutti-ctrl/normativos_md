# FEEDBACK — Correções e Aprendizados Jurídicos

**Versão:** 1.0  
**Data de criação:** 2025-07-08  
**Projeto:** 15-aditamentos — iFood Pago Compliance

---

## Propósito

Este arquivo registra correções feitas pelo time jurídico em aditamentos gerados pelo pipeline.
Cada entrada documenta o problema identificado, a correção aplicada e o aprendizado a incorporar
nas regras do sistema (DECISION_LAYER.md, REASONING_LAYER.md).

**Processo:**
1. Advogado revisa aditamento gerado e identifica problema
2. Anota a correção neste arquivo com os campos padronizados abaixo
3. Equipe de Compliance analisa e atualiza as regras afetadas
4. Regra nova ou corrigida é adicionada ao DECISION_LAYER.md com referência a este feedback

---

## Registro de Feedbacks

_Nenhum feedback registrado ainda. Esta seção será preenchida conforme o pipeline entrar em operação._


---
### FEEDBACK-001

| Campo | Valor |
|---|---|
| **ID** | FEEDBACK-001 |
| **Data** | 2026-07-13 |
| **Ticket Jira** | SWANCRG-180 (caso real: JURFIN-5749) |
| **Empresa** | MB FOOD LTDA / Grupo Medieval |
| **Advogado** | Giovanna Batistutti (Compliance) |
| **Módulo afetado** | alteracao_cnpjs_grupo + cabeçalho + rodapé |

#### Problema 1 — Título do contrato incompleto

**Gerado pelo pipeline:**
> `TERMO ADITIVO AO CONTRATO DE PRESTAÇÃO DE SERVIÇOS`

**Correto (com adendo após revisão):**
> `TERMO ADITIVO AO CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE CREDENCIAMENTO`

**Aprendizado:**
- O `{{CONTRATO_ORIGINAL}}` deve incluir o tipo específico do contrato quando disponível
- Para contratos de credenciamento (Maquinona, POS), o título correto é "CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE CREDENCIAMENTO"
- O Agente 1 deve extrair o tipo do contrato da thread Slack ou do contrato anexo e preencher `CONTRATO_ORIGINAL` com o título completo
- **Regra:** Se o produto for Maquinona/POS/credenciamento → `CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE CREDENCIAMENTO`; se for iFood Benefícios → `CONTRATO DE PRESTAÇÃO DE SERVIÇOS`

#### Problema 2 — Erro de digitação na cláusula 1.1

**Gerado pelo pipeline:**
> `passará a compor o Contrato, como Parte do ContratoContratante`

**Correto:**
> `passará a compor o Contrato, como Parte do Contratante`

**Aprendizado:**
- Erro de duplicação: "Contrato" + "Contratante" ficou "ContratoContratante"
- **Causa:** o texto do módulo tinha a palavra "Contrato" logo antes de "Contratante" e a função `_montar_texto_cnpjs()` gerou texto com duplicação
- **Fix necessário:** revisar a string do texto gerado em `_montar_texto_cnpjs()`: trocar `"Parte do Contrato, como Parte do Contratante"` por `"Parte do Contratante"`

#### Problema 3 — Signatária nova empresa não aparecia no rodapé

**Gerado pelo pipeline:**
> Rodapé com apenas: IFOOD BENEFÍCIOS E SERVIÇOS LTDA + MB FOOD LTDA + Testemunhas

**Correto (após revisão):**
> Rodapé adicionou bloco de assinatura para: **MP MEDIEVAL ITAP LTDA**

**Aprendizado:**
- Quando o módulo `alteracao_cnpjs_grupo` inclui um novo CNPJ, a empresa incluída deve assinar o aditivo também
- O Agente 2 deve incluir `CNPJS_ASSINAR` nos campos_finais com a lista de empresas novas que precisam de bloco de assinatura
- O template precisa de um placeholder `{{BLOCOS_ASSINATURA_ADICIONAIS}}` após o bloco de assinatura da Empresa pai

---
### Template de registro

```markdown
---
### FEEDBACK-[NNN]

| Campo | Valor |
|---|---|
| **ID** | FEEDBACK-NNN |
| **Data** | AAAA-MM-DD |
| **Ticket Jira** | JURFIN-XXXX |
| **Empresa** | [Razão social da empresa] |
| **Advogado** | [Nome do advogado que identificou o problema] |
| **Módulo afetado** | [Número e nome do módulo] |
| **Problema identificado** | [Descrição clara do problema no documento gerado] |
| **Correção aplicada** | [O que foi corrigido no documento final] |
| **Regra a criar/atualizar** | [REGRA-XX no DECISION_LAYER.md] |
| **Status** | [Pendente / Incorporado / Descartado] |

**Contexto adicional:**
[Texto livre com detalhes do problema, se necessário]
---
```

---

## Histórico de Versões das Regras (baseado em feedbacks)

_Nenhuma atualização de regra baseada em feedback ainda._

| Data | Regra | Mudança | Feedback origem |
|---|---|---|---|
| — | — | — | — |
