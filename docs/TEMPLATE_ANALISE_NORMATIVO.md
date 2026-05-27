# Template de Análise de Normativo — iFood Pago

> Documento de referência para o pipeline de monitoramento BCB.
> Usado pelo agente para estruturar o resumo de normativos APLICÁVEL e MONITORAR
> enviados ao canal #agenda-normativa-ifoodpago.
> Versão: 1.0 | Última atualização: 2026-05-27

---

## Formato da Mensagem Slack

### [Menções aos responsáveis]
`@responsável1 @responsável2 @responsável3`
*(Base de áreas responsáveis a ser configurada — pendente)*

---

### 1. Identificação do Normativo
Foi publicada/publicado a/o **[tipo do ato normativo + número/ano]** que **[breve descrição do que trata/altera]**.

---

### 2. Vigência
**Vigência:** [data ou "a partir de dd/mm/aaaa"]
*(Incluir nota sobre data-base de aplicação se houver período de transição)*

---

### 3. Resumo do Conteúdo
*(i)* [ponto principal 1]
*(ii)* [ponto principal 2]
*(iii)* [impacto em CADOCs/reportes, se aplicável]
*(iv)* [pontos de atenção / monitoramento]

> **Importante:** O resumo deve ser claro e direto. Caso a norma altere outra já existente,
> evidenciar as diferenças em relação ao texto anterior.

---

### 4. Íntegra do Normativo
[Link para o texto integral no DOU ou BCB]

---

### 5. Próximos Passos / Solicitação
Peço por gentileza que [avaliem / verifiquem / nos avisem sobre] [o que precisa ser feito].
[Se necessário, podemos marcar uma agenda / Irei agendar um GT.]

---

## Instruções para o Agente

Ao gerar o resumo de um normativo classificado como APLICÁVEL ou MONITORAR:

1. **Identificação:** Usar o tipo e número exatos conforme publicado no DOU/BCB.
   Exemplo: "Foi publicada a Resolução BCB nº 570, de 19/05/2026, que altera a Resolução BCB nº 517/2025..."

2. **Vigência:** Extrair do texto integral (Art. final geralmente contém).
   Se vigência imediata: "Vigência: a partir de [data de publicação]".
   Se há faseamento: detalhar cada fase com datas.

3. **Resumo:** Máximo 4-6 bullet points. Priorizar:
   - O que muda na prática para o iFood Pago
   - Obrigações novas ou alteradas
   - Prazos de implementação
   - Impacto em CADOCs, COSIF, reportes regulatórios (se aplicável)
   - Diferenças em relação à norma anterior (se for alteração)

4. **Íntegra:** Sempre incluir o link do DOU ou BCB. Se PDF disponível, preferir link direto.

5. **Próximos Passos:** Ser específico sobre o que se solicita:
   - Para APLICÁVEL: "Peço que avaliem o impacto no [produto/processo específico] e nos avisem se há necessidade de adequação até [prazo]."
   - Para MONITORAR: "Peço que verifiquem se há impacto indireto para [área] e confirmem se precisamos de alguma ação."

---

## Referência de Tipos de Ato Normativo BCB

| Tipo | Artigo | Exemplo |
|---|---|---|
| Resolução CMN | feminino | "Foi publicada a Resolução CMN nº X..." |
| Resolução BCB | feminino | "Foi publicada a Resolução BCB nº X..." |
| Instrução Normativa BCB | feminino | "Foi publicada a Instrução Normativa BCB nº X..." |
| Circular BCB | feminino | "Foi publicada a Circular BCB nº X..." |
| Carta-Circular BCB | feminino | "Foi publicada a Carta-Circular BCB nº X..." |
| Comunicado BCB | masculino | "Foi publicado o Comunicado BCB nº X..." |
| Ato do Presidente BCB | masculino | "Foi publicado o Ato do Presidente BCB nº X..." |
| Ato de Diretor BCB | masculino | "Foi publicado o Ato de Diretor BCB nº X..." |

---

## Exemplo Preenchido

**@compliance @juridico @ti**

Foi publicada a **Resolução BCB nº 569, de 19/05/2026**, que altera a Resolução BCB nº 343/2023 para incluir operadoras de apostas não autorizadas como indício de fraude no sistema Fraud Marker do Pix.

**Vigência:** A partir de 19/05/2026 (imediata), com prazos de implementação técnica em 30/10/2026 e 01/12/2026.

*(i)* Amplia o escopo do Fraud Marker para incluir transações relacionadas a bets ilegais (operadoras sem licença SPA/MF)
*(ii)* IPs e SCDs devem adaptar sistemas de monitoramento para identificar contas vinculadas a bets não autorizadas
*(iii)* Prazo 1: monitoramento de criptoativos ligados a bets ilegais até **30/10/2026**
*(iv)* Prazo 2: monitoramento geral de contas suspeitas de bets ilegais até **01/12/2026**
*(v)* Marcações sob sigilo — LGPD aplicável; dados não podem ser divulgados ao titular

**Diferença em relação à Res. 343/2023:** Inclui nova categoria de fraude (bets ilegais) que antes não estava prevista no Fraud Marker.

📄 Íntegra: https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?numero=569&tipo=Resolu%C3%A7%C3%A3o+BCB

Peço por gentileza que **TI e Compliance** avaliem o gap de implementação do Fraud Marker e nos avisem sobre o esforço necessário para adequação até outubro. Se necessário, posso agendar um GT.
