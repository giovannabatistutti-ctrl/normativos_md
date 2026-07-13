---
modulo: "alteracao_produto"
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
variaveis_obrigatorias:
  - "PRODUTO_NOVO"
  - "VALOR_BENEFICIO"
  - "DATA_VIGENCIA_PRODUTO"
variaveis_opcionais:
  - "PRODUTO_ANTERIOR"
regras_negocios:
  - "PRODUTO_ANTERIOR é obrigatório nos casos de substituição de produto; omitir apenas em inclusão pura"
  - "PRODUTO_NOVO deve corresponder à nomenclatura oficial do portfólio iFood Benefícios"
  - "VALOR_BENEFICIO deve ser expresso em Reais (R$) e representar o valor mínimo por usuário/mês"
  - "DATA_VIGENCIA_PRODUTO deve ser data futura, apresentada por extenso"
  - "Alterações de produto afetam o Item VIII do Formulário de Contratação"
  - "Verificar TCE (Termos e Condições Específicas) aplicável ao produto novo antes de incluir"
---

## ALTERAÇÃO DO ITEM VIII DO FORMULÁRIO DE CONTRATAÇÃO — PRODUTO

**1.1.** As Partes acordam em alterar o Item VIII do Formulário de Contratação, originalmente celebrado em {{DATA_CONTRATO_ORIGINAL}}, conforme segue:

{{#if PRODUTO_ANTERIOR}}
**1.1.1.** Fica excluído do objeto contratual o benefício denominado **{{PRODUTO_ANTERIOR}}**, que deixará de ser disponibilizado aos usuários da CONTRATANTE a partir da data de vigência estabelecida na Cláusula 1.1.3 abaixo.
{{/if}}

**1.1.2.** Fica incluído no objeto contratual o benefício denominado **{{PRODUTO_NOVO}}**, no valor mínimo de **R$ {{VALOR_BENEFICIO}}** ({{VALOR_BENEFICIO_EXTENSO}}) por usuário/mês, a ser disponibilizado aos usuários indicados pela CONTRATANTE.

**1.1.3.** As alterações de que trata a presente cláusula entrarão em vigor em **{{DATA_VIGENCIA_PRODUTO}}**, data a partir da qual o item VIII do Formulário de Contratação passará a refletir a nova configuração de benefícios acordada.

**1.2.** O benefício {{PRODUTO_NOVO}} será regido pelos Termos e Condições Específicas ("TCE") correspondentes, disponibilizados pelo iFood Benefícios, os quais a CONTRATANTE declara conhecer e aceitar integralmente.

**1.3.** Demais benefícios eventualmente contratados permanecem inalterados, salvo expressa disposição em contrário neste Aditivo.

---
fonte_modelo: "aditamento_ifood_beneficios_v1"
