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
| Transmissor de Dados (Open Finance) | Inativo |
| Receptor de Dados (Open Finance) | Inativo |


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

## Seção 4 — Open Finance & Pix: Status Operacional e Obrigações em Aberto

> Esta seção registra o contexto regulatório real do iFood Pago como participante do ecossistema Open Finance Brasil e do arranjo Pix, incluindo não conformidades em aberto junto à AOFB e o plano de adequação vigente.

### 4.1 Histórico de Ingresso no Open Finance

| Marco | Data | Descrição |
|---|---|---|
| Autorização BCB como IP regulada | 31/10/2023 | Zoop obtém autorização para atuar como Instituição de Pagamento |
| Registro do Conglomerado iFood Pago IP Prudencial | 12/03/2025 | Formalização do conglomerado prudencial Tipo 3 |
| Renomeação para iFood Pago IP | Dez/2025 | BCB autoriza alteração da denominação social da Zoop |
| Reconhecimento como participante obrigatório do Pix | 2025 | Crescimento da base de contas superou 500.000 contas, tornando a ES participante obrigatória do Pix como provedora de conta transacional, e consequentemente do Open Finance como detentor de conta |

**Nota estratégica:** A iFood Pago havia comunicado à AOFB (Tickets #120054 e #111467, de 31/10/2025 e 05/12/2025) a expectativa de manter base inferior a 500.000 contas após processo de saneamento. O crescimento concomitante ao saneamento frustrou essa expectativa, tornando a ES participante obrigatória.

### 4.2 Obrigações Ativas como Participante Obrigatório

| Papel | Status regulatório | Base normativa |
|---|---|---|
| Participante obrigatório do Pix (provedor de conta transacional) | ✅ Ativo | Regulamento Pix + Art. 3º, §2º, Res. BCB nº 1/2020 |
| Detentor de Conta (Open Finance) | ✅ Ativo | Resolução BCB nº 1/2020 |
| ITP — Iniciador de Transação de Pagamento | ✅ Ativo | Resolução BCB nº 1/2020 |
| Transmissor de Dados (Open Finance) | ⚠️ Inativo — adequação pendente | Resolução BCB nº 1/2020 |
| Receptor de Dados (Open Finance) | ⚠️ Inativo — adequação pendente | Resolução BCB nº 1/2020 |

### 4.3 Comunicação Formal Pendente ao BCB

- **Ação em aberto:** Notificação oficial ao BCB do iFood Pago como participante obrigatório do Pix na qualidade de provedor de conta transacional, nos termos do **Art. 3º, §2º da Resolução BCB nº 1/2020**.
- Status: pendente de envio formal.

### 4.4 Status das Implantações Open Finance (Detentor de Conta)

| Entrega | Prazo comprometido | Status |
|---|---|---|
| Backoffice (plataforma) | Jan/2026 | ✅ Concluído |
| Front-end PF (experiência do usuário — pessoa física) | Jun/2026 | ✅ Concluído |
| Front-end PJ (experiência do usuário — pessoa jurídica) | Abr/2026 | ✅ Concluído |

### 4.5 Não Conformidades em Aberto (AOFB)

| Item | Descrição | Previsão de regularização |
|---|---|---|
| Tempo de Resposta | Indicador de tempo de resposta das APIs Open Finance fora do padrão exigido | Nov/2027 (após conclusão de Vínculo de Dispositivo) |
| Taxa de Conversão da ITP | Taxa de conversão da Iniciação de Transação de Pagamento abaixo do requerido | Nov/2027 |
| Taxa de Conversão de Vínculo | Indicador de conversão de vínculo abaixo do requerido | Nov/2027 |

**Dependência-chave:** a regularização dos três indicadores acima está condicionada à conclusão da implementação do **Vínculo de Dispositivo (JSR)**, prevista para **agosto/2027**, mais o período mínimo de acumulação dos indicadores de engajamento.

### 4.6 Plano de Adequação — Pedido à AOFB/BCB

A iFood Pago IP solicitou formalmente à AOFB e ao BCB:
1. **Implantação progressiva em produção:** subida faseada de funcionalidades à medida que cada uma seja concluída e validada, em vez de implantação simultânea.
2. **Orientação de critérios por entrega:** definição, pela Estrutura OF Brasil e pelo BCB, dos requisitos para cada implantação individual (ex.: homologação prévia, envio de vídeo de experiência do usuário, atingimento de indicadores de engajamento mínimos).

Objetivos declarados da abordagem faseada:
- Antecipar benefícios ao usuário final com segurança
- Reduzir risco operacional de implantação simultânea
- Alinhar às boas práticas de gestão de riscos tecnológicos da regulação vigente

### 4.7 Impacto Regulatório Mapeado

| Dimensão | Impacto |
|---|---|
| Compliance Open Finance | NCs abertas em 3 indicadores; prazo de regularização nov/2027 |
| Comunicação ao BCB | Notificação formal de participante obrigatório ainda não enviada — risco regulatório |
| Transmissor/Receptor de Dados | Capacidades ainda inativas — obrigações futuras quando ativadas |
| Proteção ao Consumidor | Interfaces PF e PJ concluídas, mas fluxo integral depende da entrega do Vínculo de Dispositivo |

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
| 🔴 **Alta** | Open Finance — NCs junto à AOFB | Não conformidades abertas em Tempo de Resposta, Taxa de Conversão ITP e Vínculo; regularização prevista para nov/2027 | Res. BCB nº 1/2020; comunicados AOFB |


---

## Seção 7 — Políticas Internas

> Detalhes em **[`REASONING_LAYER_POLITICAS.md`](./REASONING_LAYER_POLITICAS.md)** (34 documentos).
> Verificar se política interna atende normativo (reduz criticidade), há lacuna (aumenta criticidade) ou se a norma exige atualização ou criação de política. Acionar área responsável conforme listado.
