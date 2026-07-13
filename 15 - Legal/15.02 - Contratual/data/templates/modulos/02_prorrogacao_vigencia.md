---
modulo: "prorrogacao_vigencia"
versao: "1.0"
produtos: ["todos"]
variaveis_obrigatorias:
  - "DATA_NOVA_VIGENCIA"
  - "PRAZO_MESES"
variaveis_opcionais: []
regras_negocios:
  - "Este módulo só deve ser incluído quando o pedido envolver prorrogação de vigência"
  - "DATA_NOVA_VIGENCIA deve ser posterior à data de expiração atual do contrato"
  - "PRAZO_MESES deve ser número inteiro positivo (ex: 12, 24, 36)"
  - "DATA_NOVA_VIGENCIA deve ser apresentada por extenso (ex: 07 de julho de 2026)"
  - "Módulo exclusivo com 03_retirada_renovacao_automatica.md — verificar combinação"
---

## CLÁUSULA DE PRORROGAÇÃO DE VIGÊNCIA

**1.1.** As Partes acordam em prorrogar o prazo de vigência do Contrato pelo período de **{{PRAZO_MESES}} ({{PRAZO_MESES_EXTENSO}}) meses**, contados a partir da assinatura do presente Aditivo, encerrando-se em **{{DATA_NOVA_VIGENCIA}}**.

**1.2.** A partir desta prorrogação, o Contrato não mais se renovará automaticamente ao término do prazo ora estabelecido, podendo ser prorrogado somente mediante a celebração de novo Termo Aditivo firmado pelas Partes, em substituição à redação atual da Cláusula 10.2 dos Termos e Condições Gerais, que passará a vigorar com a seguinte redação:

> *"10.2. Renovação. Uma vez transcorrido o prazo de vigência inicial, o Contrato poderá ser prorrogado mediante a celebração de termo aditivo firmado pelas Partes."*

**1.3.** Todas as demais condições do Contrato permanecem válidas e inalteradas durante o período de prorrogação ora acordado.

---
fonte_modelo: "aditamento_ifood_beneficios_v1"
