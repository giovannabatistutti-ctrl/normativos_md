---
modulo: "isa"
versao: "1.0"
produtos: ["ISA", "Incentivo Saúde Alimentar"]
variaveis_obrigatorias:
  - "VALOR_ISA_MENSAL"
  - "PERIODICIDADE"
  - "CUMULATIVO"
  - "DATA_INICIO_ISA"
  - "FORMA_PAGAMENTO"
variaveis_opcionais:
  - "DATA_RETROATIVIDADE"
regras_negocios:
  - "PRÉ-CONDIÇÃO OBRIGATÓRIA: A inclusão do ISA exige Proposta Comercial aprovada anexa ao ticket. Ausência = PENDENTE."
  - "Verificar número e data de aprovação da Proposta Comercial antes de gerar este módulo"
  - "PERIODICIDADE deve ser: 'mensal' ou 'semestral' (apenas esses dois valores aceitos)"
  - "CUMULATIVO deve ser: 'sim' ou 'não' — indica se o saldo acumula entre períodos"
  - "DATA_INICIO_ISA deve ser data futura ou igual à data de assinatura, apresentada por extenso"
  - "FORMA_PAGAMENTO deve indicar o mecanismo de crédito (ex: crédito em carteira digital, débito em folha)"
  - "DATA_RETROATIVIDADE é opcional — preencher SOMENTE se o ticket mencionar retroatividade explicitamente"
  - "Retroatividade jamais deve ser inferida ou assumida — exige confirmação expressa no ticket e aprovação comercial"
  - "VALOR_ISA_MENSAL expresso em Reais (R$) por usuário/período conforme PERIODICIDADE"
---

## INCLUSÃO DO BENEFÍCIO ISA — INCENTIVO SAÚDE ALIMENTAR

> ⚠️ **PRÉ-CONDIÇÃO OBRIGATÓRIA:**
> A inclusão do benefício ISA (Incentivo Saúde Alimentar) **exige Proposta Comercial aprovada**, devidamente anexa ao ticket de solicitação. Na ausência de Proposta Comercial aprovada, este módulo **não deve ser gerado** — marcar como **PENDENTE** e aguardar documentação.

**1.1.** As Partes acordam em incluir no objeto contratual o benefício denominado **ISA — Incentivo Saúde Alimentar**, com as seguintes características:

| Característica | Condição Acordada |
|---|---|
| Valor por usuário/período | R$ {{VALOR_ISA_MENSAL}} |
| Periodicidade de crédito | {{PERIODICIDADE}} |
| Acumulativo entre períodos | {{CUMULATIVO}} |
| Forma de pagamento | {{FORMA_PAGAMENTO}} |
| Data de início de vigência | {{DATA_INICIO_ISA}} |

**1.2.** O ISA consiste em crédito de incentivo ao consumo alimentar saudável, disponibilizado pela CONTRATANTE aos seus colaboradores elegíveis por meio da plataforma iFood Benefícios, nos termos e condições acordados na Proposta Comercial aprovada, que integra o presente Aditivo como Anexo.

**1.3.** A elegibilidade dos usuários ao ISA é de exclusiva responsabilidade da CONTRATANTE, que definirá os critérios internos de concessão em conformidade com sua política de benefícios e com as normas trabalhistas aplicáveis, inclusive o Programa de Alimentação do Trabalhador (PAT), quando pertinente.

**1.4. Cumulatividade.** O saldo do ISA **{{#if CUMULATIVO_SIM}}será acumulado{{else}}não será acumulado{{/if}}** de um período para o seguinte, expirando ao final de cada ciclo de {{PERIODICIDADE}} nos casos em que a cumulatividade não se aplique.

{{#if DATA_RETROATIVIDADE}}
**1.5. Retroatividade.** A pedido da CONTRATANTE e conforme expressamente autorizado na Proposta Comercial aprovada, o ISA terá efeito retroativo a partir de **{{DATA_RETROATIVIDADE}}**, data a partir da qual os créditos correspondentes serão apurados e disponibilizados na forma acordada.
{{/if}}

**1.6.** O iFood Benefícios reserva-se o direito de atualizar os Termos e Condições Específicas ("TCE") do ISA, com comunicação prévia à CONTRATANTE, nos prazos e formas previstos no Contrato.

---
fonte_modelo: "aditamento_ifood_beneficios_v1"
