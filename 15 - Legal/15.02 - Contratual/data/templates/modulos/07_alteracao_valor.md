---
modulo: "alteracao_valor"
versao: "1.0"
produtos:
  - "iFood Refeição"
  - "iFood Alimentação"
  - "Alimentação+Refeição"
  - "Saldo Mobilidade"
  - "Saldo Cultura e Entretenimento"
  - "Saldo Home Office"
  - "Saldo Educação"
  - "Saldo Saúde e Bem-Estar"
  - "Saldo Farmácia"
  - "Saldo Livre"
  - "ISA"
  - "Saldo Extra"
  - "Saldo Natal"
variaveis_obrigatorias:
  - "PRODUTO"
  - "VALOR_ANTERIOR"
  - "VALOR_NOVO"
  - "DATA_VIGENCIA_NOVO_VALOR"
variaveis_opcionais: []
regras_negocios:
  - "PRODUTO deve corresponder à nomenclatura oficial do portfólio iFood Benefícios"
  - "VALOR_ANTERIOR deve ser o valor vigente no contrato atual — nunca estimado"
  - "VALOR_NOVO deve ser maior que zero e expresso em Reais (R$)"
  - "DATA_VIGENCIA_NOVO_VALOR deve ser data futura, apresentada por extenso"
  - "A alteração afeta o Item VIII do Formulário de Contratação"
  - "Para múltiplos produtos com valores distintos, replicar a cláusula 1.1 para cada produto"
---

## ALTERAÇÃO DO ITEM VIII DO FORMULÁRIO DE CONTRATAÇÃO — VALOR DO BENEFÍCIO

**1.1.** As Partes acordam em alterar o valor mínimo do benefício **{{PRODUTO}}**, previsto no Item VIII do Formulário de Contratação, que passará do valor atual de **R$ {{VALOR_ANTERIOR}}** ({{VALOR_ANTERIOR_EXTENSO}}) para o novo valor de **R$ {{VALOR_NOVO}}** ({{VALOR_NOVO_EXTENSO}}) por usuário/mês.

**1.2.** O novo valor estabelecido na Cláusula 1.1 acima entrará em vigor em **{{DATA_VIGENCIA_NOVO_VALOR}}**, data a partir da qual o Item VIII do Formulário de Contratação passará a refletir o valor ora acordado.

**1.3.** Fica expressamente estabelecido que a alteração de valor ora acordada aplica-se exclusivamente ao benefício **{{PRODUTO}}**, permanecendo inalterados os valores dos demais benefícios eventualmente contratados, salvo disposição expressa em contrário neste Aditivo.

**1.4.** A CONTRATANTE declara estar ciente de que a alteração do valor mínimo do benefício pode impactar o custeio total do programa de benefícios, sendo de sua exclusiva responsabilidade o planejamento orçamentário correspondente.

---
fonte_modelo: "aditamento_ifood_beneficios_v1"
