---
modulo: "saldo_extra"
versao: "1.0"
produtos: ["Saldo Extra"]
variaveis_obrigatorias:
  - "VALOR_SALDO_EXTRA"
  - "DATA_CREDITO"
  - "DESCRICAO_OCASIAO"
  - "PUBLICO_ELEGIVEL"
variaveis_opcionais: []
regras_negocios:
  - "Saldo Extra é benefício NÃO RECORRENTE — uso pontual e eventual, vinculado a uma ocasião específica"
  - "DATA_CREDITO deve ser data futura, apresentada por extenso"
  - "DESCRICAO_OCASIAO deve descrever objetivamente o motivo do crédito (ex: aniversário da empresa, premiação trimestral)"
  - "PUBLICO_ELEGIVEL deve indicar claramente quais colaboradores receberão o crédito"
  - "Não usar linguagem que sugira periodicidade ou recorrência neste benefício"
  - "Novo Saldo Extra em momento futuro exige novo Aditivo — este instrumento não cria direito adquirido à repetição"
  - "VALOR_SALDO_EXTRA expresso em Reais (R$) por usuário elegível"
---

## INCLUSÃO DE SALDO EXTRA — BENEFÍCIO PONTUAL NÃO RECORRENTE

**1.1.** As Partes acordam em disponibilizar, em caráter **pontual e não recorrente**, um crédito adicional denominado **Saldo Extra**, com as seguintes características:

| Característica | Condição Acordada |
|---|---|
| Valor por usuário elegível | R$ {{VALOR_SALDO_EXTRA}} |
| Data de crédito | {{DATA_CREDITO}} |
| Ocasião/finalidade | {{DESCRICAO_OCASIAO}} |
| Público elegível | {{PUBLICO_ELEGIVEL}} |

**1.2.** O Saldo Extra de que trata a presente cláusula constitui **benefício de caráter eventual e não recorrente**, concedido exclusivamente em razão da ocasião descrita na tabela acima, não gerando direito adquirido à sua repetição ou periodicidade futura para a CONTRATANTE ou para seus colaboradores.

**1.3.** A CONTRATANTE é responsável por comunicar aos seus colaboradores elegíveis a disponibilização do Saldo Extra, bem como os termos e condições para sua utilização conforme os Termos e Condições Gerais e Específicos do Contrato.

**1.4.** O Saldo Extra não creditado ou não utilizado pelos usuários elegíveis até a data de expiração estabelecida nos Termos e Condições Específicos do benefício será automaticamente cancelado, sem direito a restituição ou compensação.

**1.5.** Eventuais concessões futuras de Saldo Extra deverão ser formalizadas mediante novo instrumento contratual, não estando automaticamente autorizadas pelo presente Aditivo.

**1.6.** O custeio do Saldo Extra é de responsabilidade da CONTRATANTE, na forma e condições de pagamento previstas no Contrato.

---
fonte_modelo: "aditamento_ifood_beneficios_v1"
