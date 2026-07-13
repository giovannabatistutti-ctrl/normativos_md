# DECISION MAP — Módulos de Aditamento iFood Benefícios

**Versão:** 1.0  
**Data:** 2025-07-08  
**Referência:** `analise_estrutura_aditamento.md` — 9 módulos existentes + 3 a criar

---

## 1. Visão Geral dos 12 Módulos

| # | Módulo | Status | Complexidade | Template atual? |
|---|---|---|---|---|
| 1  | Correção de Faturamento Mínimo (Item VIII) | ✅ Existente | Média | ✅ |
| 2  | Retirada de Prorrogação Automática (Cláusula 10.2) | ✅ Existente | Simples | ✅ |
| 3  | Prorrogação de Vigência (sem renovação automática) | ✅ Existente | Simples | ✅ |
| 4  | Prorrogação de Vigência + Renovação Automática | ✅ Existente | Simples | ✅ |
| 5  | Retirada de Cessão de Poderes sem autorização (Cláusula 16.6) | ✅ Existente | Simples | ✅ |
| 6  | Diminuição do Aviso Prévio para rescisão imotivada (Cláusula 10.3) | ✅ Existente | Simples | ✅ |
| 7  | Inclusão de novos CNPJs do grupo | ✅ Existente | Média | ✅ |
| 8  | Retirada de CNPJs do grupo | ✅ Existente | Média | ✅ |
| 9  | Declaração iFood Pago IP / ZOOP | ✅ Existente | Simples | ✅ |
| 10 | Retirada de Subsídio (Programa Colab+) | ✅ Existente | Simples | ✅ |
| 11 | ISA (Incentivo ao Saldo Alimentar) | 🔨 A criar | Média | ❌ |
| 12 | Saldo Extra | 🔨 A criar | Média | ❌ |
| 13 | Saldo Natal | 🔨 A criar | Simples | ❌ |

---

## 2. Mapa de Aplicabilidade por Produto/Situação

### 2.1 Situações → Módulos aplicáveis

| Situação / Produto | Módulos obrigatórios | Módulos opcionais | Pré-condição |
|---|---|---|---|
| Atualizar valores contratados | 1 | — | Item VIII atualizado no ticket |
| Remover renovação automática | 2 | — | Contrato atual com renovação automática |
| Prorrogar contrato (fim de vigência) — sem auto | 3 | 1, 5, 6 | — |
| Prorrogar contrato (fim de vigência) — com auto | 4 | 1, 5 | — |
| Reduzir prazo de rescisão | 6 | — | Prazo atual > prazo negociado |
| Remover cessão unilateral | 5 | — | Cláusula 16.6 original permite cessão unilateral |
| Adicionar empresas do grupo | 7 | — | Lista de CNPJs válidos |
| Remover empresas do grupo | 8 | — | Lista de CNPJs presentes no contrato |
| Esclarecer papel do iFood Pago IP | 9 | — | — |
| Remover Colab+ | 10 | — | Contrato original com Colab+ |
| Contratar ISA | 11 | — | **Proposta Comercial ISA anexa ao ticket** |
| Contratar Saldo Extra | 12 | — | Instrução explícita do advogado |
| Contratar Saldo Natal | 13 | — | — |
| ISA + Saldo Natal simultaneamente | 11 + 13 | — | Proposta Comercial ISA; documento **único consolidado** |

### 2.2 Produtos → Módulos esperados

| Produto | Módulos tipicamente envolvidos |
|---|---|
| iFood Refeição | 1 (faturamento) |
| iFood Alimentação | 1 (faturamento) |
| Alimentação + Refeição | 1 (faturamento) |
| Saldo Mobilidade | 1 (faturamento) |
| Saldo Cultura e Entretenimento | 1 (faturamento) |
| Saldo Home Office | 1 (faturamento) |
| Saldo Educação | 1 (faturamento) |
| Saldo Saúde e Bem-Estar | 1 (faturamento) |
| Saldo Farmácia | 1 (faturamento) |
| Saldo Livre | 1 (faturamento) |
| ISA (Incentivo ao Saldo Alimentar) | 11 (módulo a criar) |
| Saldo Extra | 12 (módulo a criar) |
| Saldo Natal | 13 (módulo a criar) |

---

## 3. Exclusões Mútuas (módulos incompatíveis)

```
GRUPO A — Cláusula 10.2 (prorrogação): escolher APENAS UM
  ┌─────────────────────────────────────────────┐
  │  Módulo 2  XOR  Módulo 3  XOR  Módulo 4    │
  │  (remover)     (simples)   (com auto)        │
  └─────────────────────────────────────────────┘
  Razão: todos alteram a Cláusula 10.2 — combiná-los cria contradição textual.

GRUPO B — Módulo 2 e Módulo 4 são semanticamente opostos
  ┌─────────────────────────────────────────────┐
  │  Módulo 2 (remover auto) + Módulo 4 (add auto) = CONTRADIÇÃO │
  └─────────────────────────────────────────────┘
```

---

## 4. Combinações Possíveis (módulos compatíveis entre si)

| Combinação | Módulos | Situação típica |
|---|---|---|
| Renovação + correção de valores | 3 + 1 | Prorrogação com atualização de faturamento |
| Renovação + redução de aviso | 3 + 6 | Prorrogação com novo prazo de rescisão |
| Renovação + cessão bilateral | 3 + 5 | Prorrogação com ajuste de cessão |
| Correção + grupo + cessão | 1 + 7 + 5 | Atualização completa para grupo empresarial |
| ISA + Saldo Natal | 11 + 13 | Duplo aditamento → documento único consolidado |
| Prorrogação + CNPJs + aviso | 4 + 7 + 6 | Renovação automática com inclusão de filiais |
| Faturamento + remoção CNPJs | 1 + 8 | Atualização com saída de empresa do grupo |

**Regra geral:** Qualquer combinação de módulos é permitida, EXCETO combinações nos grupos de exclusão mútua acima.

---

## 5. Lógica Condicional Detalhada

### 5.1 Módulo 11 — ISA

```
SE módulo_solicitado == 11 (ISA):
    SE proposta_comercial_isa_anexa == FALSE:
        MARCAR: {{PENDENTE: A Proposta Comercial ISA não foi localizada nos anexos do ticket.
                            Por favor, anexe o documento antes do processamento.}}
        BLOQUEAR geração do módulo ISA
    SENÃO:
        VERIFICAR terminologia: "ISA" (não "Saldo Saúde Alimentar")
        INCLUIR módulo 11 no documento
```

### 5.2 Módulo 13 — Saldo Natal

```
SE módulo_solicitado == 13 (Saldo Natal):
    INCLUIR cláusula: "A responsabilidade de distribuição do Saldo Natal
                       é da Empresa (cliente), não do iFood Benefícios."
    SE módulo 11 (ISA) TAMBÉM selecionado:
        GERAR documento único consolidado (não dois separados)
```

### 5.3 Módulo 6 — Aviso Prévio

```
SE módulo_solicitado == 6 (Aviso Prévio):
    aviso_original = extrair_clausula_10_3(contrato_anexo)
    aviso_negociado = ticket["aviso_previo_dias"]
    SE aviso_negociado >= aviso_original:
        ERRO: "O aviso prévio negociado deve ser MENOR que o prazo original nos TCG"
        BLOQUEAR geração
    aviso_extenso = numero_por_extenso(aviso_negociado)
    PREENCHER: {{AVISO_PREVIO_DIAS}} = aviso_negociado
    PREENCHER: {{AVISO_PREVIO_EXTENSO}} = aviso_extenso
```

### 5.4 Módulo 10 — Colab+

```
SE módulo_solicitado == 10 (Colab+):
    SE contrato_tem_colabmais == NULL (não verificado):
        MARCAR: {{PENDENTE: O contrato original desta empresa inclui o Programa Colab+?
                            Confirme antes do processamento.}}
    SE contrato_tem_colabmais == FALSE:
        ERRO: "Não é possível remover Colab+ de um contrato que não o contém"
        BLOQUEAR geração
```

---

## 6. Estrutura de Templates (a criar em `data/templates/modulos/`)

| Arquivo | Módulo | Status |
|---|---|---|
| `m01_correcao_faturamento.md` | Módulo 1 | 🔨 A criar (Fase 2) |
| `m02_remove_prorrogacao_auto.md` | Módulo 2 | 🔨 A criar |
| `m03_prorrogacao_simples.md` | Módulo 3 | 🔨 A criar |
| `m04_prorrogacao_com_auto.md` | Módulo 4 | 🔨 A criar |
| `m05_remove_cessao.md` | Módulo 5 | 🔨 A criar |
| `m06_aviso_previo.md` | Módulo 6 | 🔨 A criar |
| `m07_inclusao_cnpjs.md` | Módulo 7 | 🔨 A criar |
| `m08_remocao_cnpjs.md` | Módulo 8 | 🔨 A criar |
| `m09_ifood_pago_ip.md` | Módulo 9 | 🔨 A criar |
| `m10_colabmais.md` | Módulo 10 | 🔨 A criar |
| `m11_isa.md` | Módulo 11 | 🔨 A criar (Fase 2) |
| `m12_saldo_extra.md` | Módulo 12 | 🔨 A criar (Fase 2) |
| `m13_saldo_natal.md` | Módulo 13 | 🔨 A criar (Fase 2) |
