---
modulo: "saldo_natal"
versao: "1.0"
produtos: ["Saldo Natal"]
variaveis_obrigatorias:
  - "VALOR_SALDO_NATAL"
  - "ANO_REFERENCIA"
  - "DATA_CREDITO_NATAL"
variaveis_opcionais: []
regras_negocios:
  - "CLÁUSULA OBRIGATÓRIA PÓS-MAI/2025: A responsabilidade pela distribuição do Saldo Natal é do CONTRATANTE, não do iFood Benefícios"
  - "Nunca usar linguagem que atribua ao iFood Benefícios responsabilidade pela distribuição do Saldo Natal"
  - "DATA_CREDITO_NATAL deve ser data futura (normalmente dezembro do ANO_REFERENCIA), apresentada por extenso"
  - "ANO_REFERENCIA deve ser o ano-calendário a que se refere o Saldo Natal (formato AAAA)"
  - "VALOR_SALDO_NATAL expresso em Reais (R$) por usuário elegível"
  - "Saldo Natal é benefício anual — novo Aditivo deve ser celebrado para anos subsequentes"
  - "Não gerar este módulo sem confirmar ANO_REFERENCIA e DATA_CREDITO_NATAL no ticket de solicitação"
---

## INCLUSÃO DO SALDO NATAL — BENEFÍCIO ANUAL

**1.1.** As Partes acordam em disponibilizar o benefício denominado **Saldo Natal** referente ao exercício de **{{ANO_REFERENCIA}}**, com as seguintes características:

| Característica | Condição Acordada |
|---|---|
| Valor por usuário elegível | R$ {{VALOR_SALDO_NATAL}} |
| Ano de referência | {{ANO_REFERENCIA}} |
| Data de crédito na plataforma | {{DATA_CREDITO_NATAL}} |

**1.2.** O Saldo Natal consiste em crédito de caráter comemorativo e não salarial disponibilizado anualmente pela CONTRATANTE aos seus colaboradores elegíveis, por meio da plataforma iFood Benefícios, na data indicada na tabela acima.

> ⚠️ **CLÁUSULA OBRIGATÓRIA — RESPONSABILIDADE PELA DISTRIBUIÇÃO (vigência a partir de maio/2025):**

**1.3. Responsabilidade pela Distribuição.** A responsabilidade pela definição dos critérios de elegibilidade, pela seleção dos colaboradores beneficiários e pela **distribuição do Saldo Natal é exclusivamente do CONTRATANTE**. O iFood Benefícios atuará exclusivamente como plataforma tecnológica de processamento e disponibilização dos créditos, na forma e nos montantes indicados pela CONTRATANTE, não lhe cabendo qualquer responsabilidade pela política de distribuição adotada nem pelos critérios de elegibilidade definidos internamente pela CONTRATANTE.

**1.4.** A CONTRATANTE é responsável por:

a) definir e comunicar internamente os critérios de elegibilidade ao Saldo Natal;

b) fornecer ao iFood Benefícios a lista de usuários elegíveis e os valores individuais com antecedência mínima de **[XX] dias úteis** antes da data de crédito prevista;

c) assegurar o cumprimento da legislação trabalhista e previdenciária aplicável à concessão do benefício, incluindo eventuais obrigações decorrentes do Programa de Alimentação do Trabalhador (PAT) e demais normas vigentes.

**1.5.** O iFood Benefícios não terá responsabilidade por atrasos no crédito do Saldo Natal decorrentes do não cumprimento, pela CONTRATANTE, dos prazos previstos no item 1.4(b) acima.

**1.6.** O Saldo Natal de que trata o presente Aditivo refere-se exclusivamente ao exercício de **{{ANO_REFERENCIA}}**. Eventuais concessões de Saldo Natal em anos subsequentes deverão ser formalizadas mediante novo instrumento contratual, não estando automaticamente autorizadas pelo presente Aditivo.

**1.7.** O saldo não utilizado pelos usuários elegíveis até a data de expiração estabelecida nos Termos e Condições Específicos do benefício será automaticamente cancelado, sem direito a restituição ou compensação.

---
fonte_modelo: "aditamento_ifood_beneficios_v1"
