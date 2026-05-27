# Contexto iFood Pago — Camada 1 de 2

> **Propósito:** Define QUEM é o iFood Pago — entidades, autorizações, produtos, público
> e o que está fora do escopo. Esta camada é estática e contextual.
> A Camada 2 (DECISION_LAYER.md) usa este contexto para tomar decisões.
>
> **Expansão futura:** contextos específicos por produto serão adicionados como
> CONTEXTO_PIX.md, CONTEXTO_BNPL.md, CONTEXTO_CREDITO.md — ainda não criados.

---

## Seção 1 — Quem é o iFood Pago

### 1.1 Entidades do Conglomerado

| Entidade | Tipo | Papel |
|---|---|---|
| **iFood Pago Instituição de Pagamento S.A.** | IP (Instituição de Pagamento) | Líder do conglomerado | Segmento S5
| **iFood Pago Sociedade de Crédito Direto S.A. (SCD)** | SCD | Operações de crédito |



### 1.2 Classificação Regulatória

- **Segmento regulatório:** S5 (em discussão para reclassificação para S4 ou S3)
- **Tipo de conglomerado:** Tipo 3 (conglomerado prudencial)
- **Regulador principal:** Banco Central do Brasil (BCB)
- **Regulador secundário relevante:** N/A (câmbio, seguros e CVM estão fora do escopo)

### 1.3 Autorizações e Atividades Autorizadas

| Autorização/Atividade | Status |
|---|---|
| Subcredenciador | ✅ Ativo (atual) |
| Credenciador | 🔄 Em breve (transição em curso) |
| Participante facultativo do Pix (acesso direto) | ✅ Ativo |
| Detentor de conta (Open Finance) | ✅ Ativo |
| ITP — Iniciador de Transação de Pagamento (Open Finance) | ✅ Ativo |
| Emissor de Cartão de Crédito (IP)| ✅ Ativo |

### 1.4 Produtos e Serviços Ativos

| Produto/Serviço | Segmento | Status |
|---|---|---|
| Conta de Pagamento | B2C, B2B | ✅ Ativo |
| Cartão de crédito | B2C, B2B | ✅ Ativo |
| Cartão de benefícios (PAT — Programa de Alimentação do Trabalhador) e auxílios | B2C, B2B | ✅ Ativo |
| BNPL (Buy Now Pay Later) | B2C | ✅ Ativo |
| Antecipação de recebíveis | B2B (Restaurantes) | ✅ Ativo |
| Crédito Fumaça / Crédito Capital de Giro / Crédito / Garantia de Recebíveis de Cartão de Crédito| B2B (Restaurantes) | ✅ Ativo |
| POS (máquina de cartão) | B2B (Restaurantes) | ✅ Ativo |
| Pix | B2C, B2B | ✅ Ativo |
| Open Finance / ITP / Detentor de Conta | B2C, B2B | ✅ Ativo |
| Representante de Seguro | B2C, B2B | ✅ Ativo |
| Carteira Digital | B2C, B2B | 🔄 Em breve |
| Credenciador | B2B | 🔄 Em breve |


### 1.5 Público Atendido

| Segmento | Descrição |
|---|---|
| **B2B — Restaurantes** | Banco do Restaurante: conta, antecipação, POS, cartão de crédito, crédito |
| **B2C — Pessoa física** | Conta, cartão de crédito, benefícios, Pix, BNPL |
| **BaaS** | Banking as a Service para parceiros/clientes corporativos |

### 1.6 Fora do Escopo — O iFood Pago NÃO opera com

- Câmbio / operações de câmbio
- Crédito rural
- Crédito imobiliário
- Ativos virtuais / criptoativos
- Seguros (regulação SUSEP) - exceto Representante de Seguro
- Mercado de capitais (regulação CVM) - exceto FIDC
- Cooperativas de crédito
- Aeronáutica / Financiamento Aviões
- 

---

## Seção 5 — Normas Estruturantes em Vigília Permanente

> Estas normas formam a base regulatória do iFood Pago e devem ser **sempre consideradas** no contexto de qualquer nova regulação analisada. Verificar se a nova norma altera, complementa ou revoga alguma delas.

| Norma | Tema | Relevância |
|---|---|---|
| **Resolução BCB nº 80/2021** | Instituições de Pagamento — regulação prudencial e operacional | Base para toda operação do IP |
| **Resolução BCB nº 1/2020** | Open Finance / Open Banking | Base para ITP e detentor de conta |
| **Resolução Conjunta nº 1/2020** | Compartilhamento de dados e proteção no Sistema Financeiro | LGPD aplicada ao SF |
| **Resolução CMN nº 4.893/2021** | Política de segurança cibernética e ambiente de nuvem | Obrigação de segurança |
| **Circular BCB nº 3.978/2020** | PLD/FT — Prevenção à lavagem de dinheiro e financiamento ao terrorismo | Obrigação PLD para IPs |
| **Regulamento do Pix (BCB)** | Regras operacionais e participação no arranjo Pix | Participação facultativa direta |
| **Lei nº 12.865/2013** | Arranjos de pagamento e instituições de pagamento | Lei habilitadora das IPs |
| **Lei nº 13.709/2018** | Lei Geral de Proteção de Dados (LGPD) | Proteção de dados de clientes |


---

## Seção 6 — Radar Regulatório

| Prioridade | Tema | Implicações | Monitorar |
|---|---|---|---|
| 🔴 **Alta** | Reclassificação S5→S4/S3 | Requisitos prudenciais (capital, governança, reporte) | Normativos sobre critérios de segmento |
| 🔴 **Alta** | Subcredenciador→Credenciador | Novos requisitos operacionais, técnicos e regulatórios | Normas sobre credenciamento e arranjos de pagamento |
| 🟡 **Média** | Carteira Digital (em implantação) | KYC, limites operacionais e proteção ao consumidor | Normativos sobre contas de pagamento e wallets |
| 🟡 **Média** | Evolução do Open Finance | Novas obrigações para ITP e detentor de conta | Resoluções BCB sobre Open Finance |
| 🟡 **Média** | Proteção ao Consumidor para IPs | Mudanças em SAC, ouvidoria, tarifas e comunicação | Res. CMN e BCB sobre atendimento e tarifas |


---

## Seção 7 — Políticas Internas

> Detalhes em **[`REASONING_LAYER_POLITICAS.md`](./REASONING_LAYER_POLITICAS.md)** (34 documentos).
> Verificar se política interna atende normativo (reduz criticidade), há lacuna (aumenta criticidade) ou se a norma exige atualização ou criação de política. Acionar área responsável conforme listado.
