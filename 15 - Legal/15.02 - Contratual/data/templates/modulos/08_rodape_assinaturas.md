---
modulo: "rodape_assinaturas"
versao: "1.0"
produtos: ["todos"]
variaveis_obrigatorias:
  - "CIDADE"
  - "DATA_ASSINATURA"
  - "NOME_REPRESENTANTE_IFOOD"
  - "CARGO_REPRESENTANTE_IFOOD"
variaveis_opcionais:
  - "NOME_REPRESENTANTE_IFOOD_2"
  - "CARGO_REPRESENTANTE_IFOOD_2"
  - "NOME_TESTEMUNHA_1"
  - "CPF_TESTEMUNHA_1"
  - "NOME_TESTEMUNHA_2"
  - "CPF_TESTEMUNHA_2"
regras_negocios:
  - "CIDADE default: Osasco (sede do iFood Benefícios) — alterar somente se assinatura ocorrer em outra localidade"
  - "DATA_ASSINATURA deve ser apresentada por extenso (ex: 07 de julho de 2026)"
  - "Bloco de assinaturas sempre inclui pelo menos 1 representante do iFood Benefícios e 1 da CONTRATANTE"
  - "Testemunhas são opcionais mas recomendadas para validade jurídica"
  - "Para contratos com múltiplos CNPJs (grupos empresariais), pode ser necessário adicionar representantes adicionais"
---

## LOCAL E DATA

{{CIDADE}}, {{DATA_ASSINATURA}}.

---

**ASSINATURAS**

**iFood Benefícios e Serviços Ltda.**

___________________________________________
{{NOME_REPRESENTANTE_IFOOD}}
{{CARGO_REPRESENTANTE_IFOOD}}
CNPJ: 33.157.312/0001-62

{{#if NOME_REPRESENTANTE_IFOOD_2}}
___________________________________________
{{NOME_REPRESENTANTE_IFOOD_2}}
{{CARGO_REPRESENTANTE_IFOOD_2}}
CNPJ: 33.157.312/0001-62
{{/if}}

---

**{{RAZAO_SOCIAL}}**

___________________________________________
{{REPRESENTANTE_LEGAL}}
{{CARGO_REPRESENTANTE_CONTRATANTE}}
CPF: {{CPF_REPRESENTANTE}}
CNPJ: {{CNPJ}}

---

**TESTEMUNHAS:**

{{#if NOME_TESTEMUNHA_1}}
1. ___________________________________________
   Nome: {{NOME_TESTEMUNHA_1}}
   CPF: {{CPF_TESTEMUNHA_1}}
{{else}}
1. ___________________________________________
   Nome: ________________________________
   CPF: __________________________________
{{/if}}

{{#if NOME_TESTEMUNHA_2}}
2. ___________________________________________
   Nome: {{NOME_TESTEMUNHA_2}}
   CPF: {{CPF_TESTEMUNHA_2}}
{{else}}
2. ___________________________________________
   Nome: ________________________________
   CPF: __________________________________
{{/if}}

---
fonte_modelo: "aditamento_ifood_beneficios_v1"
