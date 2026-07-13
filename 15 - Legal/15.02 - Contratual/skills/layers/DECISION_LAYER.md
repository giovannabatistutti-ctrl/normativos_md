# DECISION LAYER — Regras de Negócio Codificadas

**Versão:** 1.0  
**Data:** 2025-07-08  
**Projeto:** 15-aditamentos — iFood Pago Compliance  
**Referência:** `analise_estrutura_aditamento.md` — seções 4.3, 5.3, 5.2

---

## Visão Geral

Este arquivo contém as **regras de negócio codificadas** que governam a geração automática de aditamentos iFood Benefícios. Cada regra tem nome único, condição, ação e impacto no score.

**Impacto de violação:** Regras marcadas com `SCORE=0` zeram o score de confiança, bloqueando o envio autônomo ao Netlex e exigindo revisão manual pelo advogado.

---

## REGRA-01 — ISA exige Proposta Comercial anexa

| Atributo | Valor |
|---|---|
| **ID** | REGRA-01 |
| **Nome** | ISA exige Proposta Comercial |
| **Módulo** | 11 (ISA) |
| **Condição** | Módulo ISA selecionado E Proposta Comercial não encontrada nos anexos do ticket |
| **Ação** | Marcar `{{PENDENTE: A Proposta Comercial ISA não foi localizada nos anexos. Anexe ao ticket antes do processamento.}}` |
| **Impacto** | **SCORE = 0** — bloqueia geração do módulo ISA |
| **Racional** | O ISA é um produto com condições comerciais específicas negociadas. A Proposta Comercial formaliza os valores acordados e é documento pré-requisito para o aditamento. |

```python
# Pseudocódigo
if 11 in modulos_selecionados:
    if not proposta_comercial_isa_anexa:
        campos_pendentes.append("PROPOSTA_COMERCIAL_ISA")
        score = 0
```

---

## REGRA-02 — Saldo Natal 2025+: responsabilidade de distribuição é do cliente

| Atributo | Valor |
|---|---|
| **ID** | REGRA-02 |
| **Nome** | Saldo Natal — responsabilidade do cliente |
| **Módulo** | 13 (Saldo Natal) |
| **Condição** | Módulo Saldo Natal selecionado |
| **Ação** | Incluir obrigatoriamente no texto do módulo: *"A responsabilidade pela distribuição do Saldo Natal aos usuários finais é exclusivamente da Empresa (cliente), não cabendo ao iFood Benefícios qualquer obrigação de distribuição."* |
| **Impacto** | Se cláusula de responsabilidade ausente no rascunho → **SCORE = 0** |
| **Racional** | Desde 2025, o iFood Benefícios não assume responsabilidade de distribuição do Saldo Natal. Cláusula obrigatória para reduzir risco contratual. |

---

## REGRA-03 — Aviso prévio: campo `xx` deve ser preenchido com valor do contrato original

| Atributo | Valor |
|---|---|
| **ID** | REGRA-03 |
| **Nome** | Aviso prévio — validação numérica e de consistência |
| **Módulo** | 6 (Diminuição do Aviso Prévio) |
| **Condição** | Módulo 6 selecionado |
| **Ação 1** | `AVISO_PREVIO_DIAS` deve ser inteiro positivo (> 0) |
| **Ação 2** | `AVISO_PREVIO_DIAS` deve ser MENOR que o prazo de aviso prévio original do contrato (Cláusula 10.3) |
| **Ação 3** | `AVISO_PREVIO_EXTENSO` é gerado automaticamente a partir de `AVISO_PREVIO_DIAS` |
| **Ação 4** | Se prazo original não encontrado no contrato → `{{PENDENTE: Qual o prazo de aviso prévio previsto na Cláusula 10.3 do contrato original desta empresa?}}` |
| **Impacto** | Valor ausente ou inválido → **SCORE = 0** |
| **Racional** | O marcador `xx ([xxxxxxxxxx])` no template é indefinido — preenchimento incorreto invalida a cláusula. A "diminuição" pressupõe que o novo prazo é efetivamente menor que o original. |

```python
# Pseudocódigo
if 6 in modulos_selecionados:
    aviso_negociado = ticket.get("aviso_previo_dias")
    aviso_original = contrato.get("aviso_previo_clausula_10_3")
    if not aviso_negociado:
        campos_pendentes.append("AVISO_PREVIO_DIAS")
        score = 0
    elif aviso_original and aviso_negociado >= aviso_original:
        raise ValueError("Aviso prévio negociado >= prazo original")
    else:
        aviso_extenso = numero_por_extenso(aviso_negociado)
```

---

## REGRA-04 — Terminologia canônica obrigatória

| Atributo | Valor |
|---|---|
| **ID** | REGRA-04 |
| **Nome** | Terminologia canônica — ISA |
| **Escopo** | Todo o pipeline (leitura + geração) |
| **Condição** | Qualquer texto gerado ou extraído contém termos não-canônicos |
| **Termos proibidos** | "Saldo Saúde Alimentar", "Saldo Alimentação Saudável", "Incentivo Alimentar" |
| **Termo correto** | `ISA` (exclusivamente) |
| **Ação** | Detectar ocorrência → bloquear geração, reportar no ticket |
| **Impacto** | **SCORE = 0** ao detectar qualquer termo não-canônico |
| **Racional** | A nomenclatura "ISA" é a terminologia oficial interna. Uso de variações cria ambiguidade jurídica e dificulta rastreabilidade. |

**Tabela completa de termos canônicos:**

| Produto | Nome canônico | Proibido |
|---|---|---|
| ISA | `ISA` | "Saldo Saúde Alimentar", "Saldo Alimentação Saudável" |
| iFood Refeição | `iFood Refeição` | "Vale Refeição", "VR", "Refeição iFood" |
| iFood Alimentação | `iFood Alimentação` | "Vale Alimentação", "VA", "Alimentação iFood" |
| Saldo Natal | `Saldo Natal` | "Benefício Natal", "Crédito Natal" |
| Saldo Extra | `Saldo Extra` | "Benefício Extra", "Crédito Extra" |
| Programa Colab+ | `Programa Colab+` | "Colab Plus", "Colab+" (sem "Programa" em contexto formal) |

---

## REGRA-05 — Duplo aditamento ISA + Saldo Natal: documento único consolidado

| Atributo | Valor |
|---|---|
| **ID** | REGRA-05 |
| **Nome** | Duplo aditamento — documento consolidado |
| **Módulos** | 11 (ISA) + 13 (Saldo Natal) |
| **Condição** | Módulos 11 E 13 selecionados simultaneamente |
| **Ação** | Gerar **um único documento** com ambos os módulos incluídos — **NÃO gerar dois documentos separados** |
| **Impacto** | Geração de dois documentos separados quando ambos foram solicitados → **SCORE = 0** |
| **Racional** | Dois aditamentos separados simultâneos criam risco de conflito numeração de cláusulas e ambiguidade sobre qual prevalece. Um documento consolidado é mais seguro e eficiente. |

```python
# Pseudocódigo
if 11 in modulos and 13 in modulos:
    usar_documento_consolidado = True
    # Incluir módulo ISA + módulo Saldo Natal no mesmo documento
    # Não gerar dois documentos separados
```

---

## REGRA-06 — Módulos Cláusula 10.2 são mutuamente exclusivos

| Atributo | Valor |
|---|---|
| **ID** | REGRA-06 |
| **Nome** | Exclusão mútua — Módulos de Prorrogação |
| **Módulos** | 2, 3, 4 |
| **Condição** | Dois ou mais dos módulos {2, 3, 4} selecionados simultaneamente |
| **Ação** | Bloquear geração com mensagem: *"Selecione apenas um tipo de alteração para a Cláusula 10.2: (2) Remover prorrogação automática, (3) Prorrogar vigência sem automática, ou (4) Prorrogar vigência com automática."* |
| **Impacto** | **SCORE = 0** |
| **Racional** | Todos os módulos 2, 3 e 4 alteram a Cláusula 10.2. Combiná-los cria contradição textual (ex: remover prorrogação automática E adicionar prorrogação automática no mesmo documento). |

---

## REGRA-07 — Campo obrigatório ausente zera o score

| Atributo | Valor |
|---|---|
| **ID** | REGRA-07 |
| **Nome** | Campos obrigatórios globais |
| **Escopo** | Todos os aditamentos |
| **Campos obrigatórios** | RAZAO_SOCIAL, CNPJ_EMPRESA, ENDERECO_EMPRESA, CEP_EMPRESA, DATA_CONTRATO_ORIGINAL, DATA_ADITIVO |
| **Condição** | Qualquer campo obrigatório ausente ou com valor `{{PENDENTE:...}}` |
| **Ação** | Marcar campo como PENDENTE com pergunta específica; bloquear geração |
| **Impacto** | **SCORE = 0** por campo obrigatório ausente |
| **Racional** | Estes campos formam a identidade jurídica do aditamento. Documento sem qualquer um deles é nulo ou ineficaz. |

---

## REGRA-08 — Produto não mapeado bloqueia geração

| Atributo | Valor |
|---|---|
| **ID** | REGRA-08 |
| **Nome** | Produto não mapeado |
| **Condição** | Módulo solicitado no ticket não corresponde a nenhum dos 13 módulos mapeados |
| **Ação** | `{{PENDENTE: O produto/módulo solicitado "[valor]" não está mapeado no sistema. Consulte o advogado para definição do módulo correto.}}` |
| **Impacto** | **SCORE = 0** |
| **Racional** | Produtos não mapeados não têm template validado. Gerar aditamento com texto não padronizado cria risco jurídico. |

---

## REGRA-09 — CNPJ deve ser válido (dígitos verificadores)

| Atributo | Valor |
|---|---|
| **ID** | REGRA-09 |
| **Nome** | Validação de CNPJ |
| **Campo** | `CNPJ_EMPRESA` |
| **Condição** | CNPJ no formato correto mas com dígitos verificadores inválidos |
| **Ação** | Erro de validação; marcar como `{{PENDENTE: O CNPJ informado "[valor]" possui dígitos verificadores inválidos. Confirme o CNPJ correto.}}` |
| **Impacto** | **SCORE = 0** |
| **Racional** | CNPJ com dígitos verificadores inválidos indica erro de digitação. Documento com CNPJ incorreto é juridicamente ineficaz. |

---

## REGRA-10 — Módulo Colab+ exige confirmação de presença no contrato original

| Atributo | Valor |
|---|---|
| **ID** | REGRA-10 |
| **Nome** | Colab+ — confirmação de pré-existência |
| **Módulo** | 10 (Retirada de Colab+) |
| **Condição** | Módulo 10 selecionado E confirmação de que contrato original inclui Colab+ não está no ticket |
| **Ação** | `{{PENDENTE: Confirme que o contrato original desta empresa inclui o Programa Colab+ antes de gerar este módulo de retirada.}}` |
| **Impacto** | **SCORE = 0** sem confirmação |
| **Racional** | Não é possível remover o que não existe. Retirar Colab+ de um contrato que não o prevê cria inconsistência jurídica. |

---

## Resumo: Causas de SCORE = 0

| # | Causa | Regra |
|---|---|---|
| 1 | Campo obrigatório ausente | REGRA-07 |
| 2 | Qualquer campo `{{PENDENTE:...}}` | REGRA-07 + todas as regras de PENDENTE |
| 3 | Termo não-canônico detectado | REGRA-04 |
| 4 | Produto/módulo não mapeado | REGRA-08 |
| 5 | Módulos mutuamente exclusivos combinados | REGRA-06 |
| 6 | ISA sem Proposta Comercial | REGRA-01 |
| 7 | Aviso prévio inválido ou inconsistente | REGRA-03 |
| 8 | CNPJ com dígitos verificadores inválidos | REGRA-09 |
| 9 | Saldo Natal sem cláusula de responsabilidade do cliente | REGRA-02 |
| 10 | Colab+ sem confirmação de presença no contrato | REGRA-10 |
| 11 | ISA + Saldo Natal gerando documentos separados | REGRA-05 |
