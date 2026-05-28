# Instruções para o Planner — Processamento de Feedbacks

> Este arquivo define o protocolo que o Planner (Claw) deve seguir ao receber feedbacks
> de Giovanna Batistutti (ou equipe) sobre normativos classificados pelo pipeline BCB.
> Acionado automaticamente quando Giovanna clica "💬 Feedback ao Claw" no Slack e envia
> mensagem no chat Toqan.

---

## Quando acionar este protocolo

Acionar sempre que Giovanna enviar uma mensagem que:
- Corrija a classificação de um normativo (ex: "esse não se aplica", "esse é APLICÁVEL")
- Confirme uma classificação automática (ex: "correto", "está certo")
- Ajuste o escopo de triagem (ex: "adiciona a palavra X", "X é um falso positivo")
- Ajuste a criticidade de um normativo (ex: "a criticidade deveria ser ALTO, não MÉDIO")
- Faça qualquer observação sobre como o pipeline está classificando normativos

---

## Fluxo de processamento

Quando Giovanna enviar feedback sobre um normativo:

1. **Identificar** os elementos do feedback:
   - Qual normativo (tipo + número, ex: Resolução BCB nº 123) — ou "Geral"
   - Qual era a classificação automática (APLICÁVEL / MONITORAR / NÃO APLICÁVEL)
   - Qual é a avaliação de Giovanna (o texto exato do feedback)

2. **Determinar o tipo** de feedback:
   - **Corretivo** — a classificação automática estava errada
   - **Confirmação** — a classificação automática estava certa
   - **Ajuste de escopo** — adicionar/remover palavra-chave da triagem
   - **Ajuste de criticidade** — mudar o nível de risco/urgência
   - **Outro** — qualquer outro tipo de observação

3. **Criar tarefa** com título: `"Registrar feedback — {Tipo} {número}"`
   - Exemplo: `"Registrar feedback — Resolução BCB nº 456"`
   - Exemplo: `"Registrar feedback — Geral (ajuste de escopo)"`

4. **A tarefa deve executar** os seguintes passos:

   a. **Ler FEEDBACK.md** em `data/normativos-bcb/FEEDBACK.md`
   b. **Incrementar o contador** de feedbacks (localizar o último `### Feedback #N` e usar N+1)
   c. **Preencher o template** com os dados do feedback:
      ```markdown
      ### Feedback #{n}
      - **Data:** {YYYY-MM-DD HH:MM} (Brasília)
      - **Normativo:** {Tipo + número} ou "Geral"
      - **Classificação automática:** {APLICÁVEL / MONITORAR / NÃO APLICÁVEL}
      - **Feedback de Giovanna:** {texto exato do feedback}
      - **Tipo de feedback:** {Corretivo | Confirmação | Ajuste de escopo | Ajuste de criticidade | Outro}
      - **Ajuste aplicado:**
        - Aplicabilidade: {mantida / alterada para X}
        - Criticidade: {mantida / alterada para X}
        - Área acionada: {adicionada/removida X}
        - Regra geral criada: {sim/não — se sim, qual}
      - **Status:** Incorporado
      ```
   d. **Se for Ajuste de escopo — Incluir:** adicionar a palavra-chave na seção
      `### Incluir na triagem (palavras-chave adicionadas)`
   e. **Se for Ajuste de escopo — Excluir:** adicionar a palavra-chave na seção
      `### Excluir da triagem (falsos positivos identificados)`
   f. **Se criar Regra Geral:** adicionar em `## Regras Gerais Ativas` no formato:
      `[DATA] REGRA: {descrição} | ORIGEM: Feedback #{n}`
   g. **Salvar FEEDBACK.md** com o conteúdo atualizado
   h. **Se for Corretivo:** também atualizar o arquivo `.md` do normativo no GitHub
      com a classificação corrigida (alterar a linha `**Aplicabilidade iFood Pago:**`)
   i. **Se for Corretivo:** após registrar o feedback, criar uma segunda tarefa para reanálise:
      - Título: `"Reanálise automática — {Tipo Normativo nº X} (Feedback #{n})"`
      - Comando: `source /workspace/.venv/bin/activate && python3 /workspace/data/normativos-bcb/pipeline_reanalise.py`
      - Essa tarefa gera nova análise, atualiza GitHub e notifica o Slack automaticamente

5. **Confirmar para Giovanna** que o feedback foi incorporado, informando:
   - Número do feedback registrado (Feedback #N)
   - O que foi ajustado
   - Se houver regra geral criada, descrevê-la
   - **Se for Corretivo:** informar que a reanálise automática foi acionada e chegará em breve no Slack

---

## Exemplos de feedbacks e mapeamento

| Mensagem de Giovanna | Tipo | Ação |
|---|---|---|
| "A Resolução BCB 456 não se aplica ao iFood Pago, somos IP e não banco" | Corretivo | Alterar classificação para NÃO APLICÁVEL + atualizar .md no GitHub |
| "Correto, essa Circular é APLICÁVEL mesmo" | Confirmação | Registrar confirmação apenas |
| "Adiciona 'arranjo de pagamento fechado' como palavra-chave" | Ajuste de escopo | Adicionar em `### Incluir na triagem` |
| "A palavra 'banco' está gerando muitos falsos positivos" | Ajuste de escopo | Mover de APLICÁVEL/MONITORAR para `### Excluir da triagem` |
| "A criticidade da Instrução Normativa 789 deveria ser CRÍTICO, não ALTO" | Ajuste de criticidade | Registrar + atualizar .md no GitHub |
| "Normas de crédito rural não se aplicam nunca ao iFood Pago" | Corretivo / Regra geral | Registrar + criar regra geral + adicionar "crédito rural" em Excluir |

---

## Localização dos arquivos

- **FEEDBACK.md:** `data/normativos-bcb/FEEDBACK.md`
- **Pipeline:** `data/normativos-bcb/pipeline_bcb.py`
- **Normativos no GitHub:** `github.com/giovannabatistutti-ctrl/normativos_md`
- **Log do pipeline:** `data/normativos-bcb/logs/log_YYYY-MM-DD_HHh.md`

---

## Regras de ouro

1. **Feedback corretivo de Giovanna sempre sobrepõe** a classificação automática — sem exceção
2. **Nunca alterar o texto exato do feedback de Giovanna** — copiar literalmente no campo "Feedback de Giovanna"
3. **Sempre confirmar para Giovanna** — ela deve saber que o feedback foi incorporado
4. **Incrementar sequencialmente** — o contador de feedbacks nunca deve voltar ou pular
5. **Regras gerais têm efeito futuro** — aplicam-se a todos os normativos processados após o registro
6. **Feedback corretivo sempre aciona reanálise automática** — criar a tarefa `pipeline_reanalise.py` imediatamente após registrar o feedback; nunca esperar agendamento externo

---

*Criado em 2026-05-22 | Pipeline BCB v3.0 | iFood Pago Compliance*

---

## Mapeamento Formulário → Template FEEDBACK.md

Quando Giovanna responder o formulário estruturado:

| Pergunta | Campo no template |
|---|---|
| 1 — Aplicabilidade | Tipo de feedback + Ajuste: Aplicabilidade |
| 2 — Criticidade | Ajuste: Criticidade |
| 3 — Áreas e times | Ajuste: Área acionada |
| 4 — Resumo | Observação livre + Ajuste de escopo se relevante |
| 5 — Prazo | Observação livre |
| 6 — Observações gerais | Regra geral (se aplicável) + Feedback de Giovanna |

### Lógica de processamento por tipo de resposta

**Se pergunta 1 → "Não":**
- Tipo de feedback = Corretivo
- Aplicabilidade alterada para o valor informado
- Atualizar .md do normativo no GitHub
- Verificar se justifica nova palavra-chave de triagem

**Se pergunta 2 → "Deveria ser mais alto/baixo":**
- Tipo de feedback = Ajuste de criticidade
- Registrar o ajuste
- Se padrão recorrente: criar regra geral de calibração

**Se pergunta 3 → "Falta incluir" ou "Retirar":**
- Tipo de feedback = Ajuste de escopo
- Atualizar mapeamento norma → área no DECISION_MAP.md

**Se pergunta 6 → texto com padrão aplicável a futuros normativos:**
- Criar entrada em "Regras Gerais Ativas" no FEEDBACK.md
- Documentar no DECISION_MAP.md Seção 8.2 Log de ajustes

---

## Protocolo Complementar — Arquitetura RAG (v2.0)

> Atualizado em 2026-05-22 com a nova arquitetura de memória RAG.
>
> **Fonte de verdade única para regras ativas:** `FEEDBACK.md`
> - **FEEDBACK.md** = fonte de regras ativas lidas pelo pipeline a cada execução
> - **memoria/temas/** = índice RAG para busca semântica por tema (complementar, não substituto)
>
> O protocolo abaixo descreve como estruturar a memória complementar RAG,
> mas NÃO substitui o FEEDBACK.md como fonte de regras ativas.

### Novo Fluxo ao Receber Feedback de Giovanna

Quando Giovanna enviar feedback sobre um normativo:

1. **Identificar o normativo:**
   - Localizar o ID no formato `{tipo_normalizado}_{numero}`
   - Ex: `resolucao_bcb_569`, `instrucao_normativa_bcb_737`

2. **Localizar o arquivo de memória do normativo:**
   - Path: `data/normativos-bcb/memoria/normativos/{ID}.md`
   - Se não existir: criar no formato unificado definido no DECISION_MAP.md Seção 10

3. **Adicionar o feedback na seção "Feedbacks Recebidos":**
   ```markdown
   ### Feedback #1 — {YYYY-MM-DD HH:MM}
   - **Pergunta 1 (Aplicabilidade):** {resposta}
   - **Pergunta 2 (Criticidade):** {resposta}
   - **Pergunta 3 (Áreas):** {resposta}
   - **Pergunta 4 (Resumo):** {resposta}
   - **Pergunta 5 (Prazo):** {resposta}
   - **Pergunta 6 (Observações):** {resposta}
   - **Ajustes aplicados:** {lista de ajustes feitos}
   - **Classificação corrigida:** {nova classificação, se alterada}
   ```

4. **Atualizar o arquivo temático correspondente:**
   - Path: `data/normativos-bcb/memoria/temas/{tema}.md`
   - Adicionar na seção "📝 Regras Aprendidas (de Feedbacks)":
     `[DATA] REGRA: {descrição} | ORIGEM: Feedback #{n}`

5. **Se for regra geral (aplica a qualquer normativo futuro):**
   - Adicionar também no DECISION_MAP.md Seção 10.6 "Regras Gerais Aprendidas"
   - Formato: `[DATA] REGRA: {descrição} | ORIGEM: Feedback #{n} ({normativo})`

6. **Se for corretivo (classificação errada):**
   - Atualizar também o arquivo `.md` do normativo no GitHub com classificação corrigida
   - Alterar a linha de classificação no arquivo `memoria/normativos/{ID}.md`
   - Atualizar o campo **Status** para "Revisado por feedback"

### Tabela de Arquivos a Atualizar por Tipo de Feedback

| Tipo de Feedback | memoria/normativos/{ID}.md | memoria/temas/{tema}.md | DECISION_MAP.md S10.6 | GitHub .md |
|---|---|---|---|---|
| Corretivo | ✅ Atualizar classificação + status | ✅ Adicionar regra | Se padrão geral | ✅ Atualizar + 🔄 Acionar pipeline_reanalise.py |
| Confirmação | ✅ Registrar feedback | — | — | — |
| Ajuste de criticidade | ✅ Atualizar criticidade | ✅ Calibração | Se padrão geral | Opcional |
| Ajuste de escopo | ✅ Registrar feedback | ✅ Adicionar padrão | — | — |
| Regra geral | ✅ Registrar feedback | ✅ Adicionar regra | ✅ Adicionar | — |

---

*Atualizado em 2026-05-22 — Protocolo RAG v2.0 | Pipeline BCB | iFood Pago Compliance*

---

## Protocolo — Atualização de Status de Adequação (v3.0)

> Adicionado em 2026-05-22. Ativo junto com o Adequação Tracking.

### Quando acionar

Quando Giovanna enviar mensagem que informe mudança de status de adequação de uma norma:
- "Estamos trabalhando na adequação da Resolução BCB 499" → **Em andamento**
- "A adequação da IN BCB 737 foi concluída" → **Concluída**
- "A Resolução CMN 5303 não se aplica, descartamos" → **Não aplicável**
- "O prazo da Resolução BCB 570 é 30/06/2026" → atualizar **Prazo interno**
- "Maria Silva é responsável pela IN BCB 736" → atualizar **Responsável**

### Fluxo de atualização de adequação

1. **Identificar o normativo** pelo ID (`{tipo_normalizado}_{numero}`)
2. **Localizar** `data/normativos-bcb/memoria/normativos/{ID}.md`
3. **Atualizar a seção "## 📋 Controle de Adequação"**:

   a. Alterar a linha `| **Status** |` para o novo status:
   - `🔵 Pendente de avaliação`
   - `🟡 Em andamento`
   - `🟢 Concluída`
   - `🔴 Atrasada`
   - `⬜ Não aplicável`

   b. Se informado, atualizar `| **Responsável** |`, `| **Prazo interno** |`, `| **Data de conclusão** |`, `| **Observações** |`

   c. **Adicionar linha no Histórico**:
   ```
   | {YYYY-MM-DD} | {descrição da atualização} | {quem atualizou} |
   ```
   Exemplos:
   - `| 2026-06-01 | Status alterado para Em andamento | Giovanna (manual) |`
   - `| 2026-06-15 | Adequação concluída | Giovanna (manual) |`
   - `| 2026-06-20 | Prazo interno definido: 30/06/2026 | Giovanna (manual) |`

4. **Confirmar para Giovanna** que o arquivo foi atualizado, informando:
   - Normativo atualizado
   - Novo status de adequação
   - Histórico registrado

### Tabela de status de adequação

| Status | Emoji | Significado |
|---|---|---|
| Pendente de avaliação | 🔵 | Notificada, aguardando análise da equipe |
| Em andamento | 🟡 | Adequação iniciada |
| Concluída | 🟢 | Adequação implementada |
| Atrasada | 🔴 | Prazo vencido sem conclusão (pode ser automático) |
| Não aplicável | ⬜ | Reavaliada como não aplicável após análise manual |

### Nota sobre atualizações automáticas
- O `pipeline_alertas_prazo.py` atualiza automaticamente para `🔴 Atrasada` quando o prazo vence
- O `pipeline_bcb.py` cria novos normativos com `🔵 Pendente de avaliação`
- Todas as outras atualizações de status são manuais (via Giovanna → Planner)

---

*Protocolo Adequação v3.0 adicionado em 2026-05-22 | Pipeline BCB | iFood Pago Compliance*

---

## Automação de Feedback via Slack (v4.0)

> Adicionado em 2026-05-26 como parte da correção do gap G-03.

### Visão Geral

O sistema monitora automaticamente o canal Slack `#agenda-normativa-ifoodpago` em busca de feedbacks de Giovanna sobre normativos. Quando feedbacks são detectados, eles são salvos em `feedback_pendente.json` e processados automaticamente.

### Como funciona a detecção automática

**Pipeline:** `data/normativos-bcb/pipeline_feedback_slack.py`

**Execução:** Sob demanda — acionado pelo Planner somente quando Giovanna envia feedback via chat Toqan (event-driven, não por agendamento fixo)

**Modo de operação:**
1. **PRIMARY (Slack API):** Tenta buscar mensagens do canal via Slack API (`conversations.history`)
   - **Status atual:** Indisponível — requer Slack Bot Token configurado no proxy
   - **Quando configurado:** Detecta automaticamente mensagens e threads no canal
   - **Scopes necessários:** `channels:history`, `groups:history`, `users:read`

2. **FALLBACK (feedback_inbox.json):** Se a Slack API não estiver disponível, lê feedbacks do arquivo `data/normativos-bcb/feedback_inbox.json`
   - Giovanna pode adicionar feedbacks manualmente neste arquivo
   - Formato: lista JSON com objetos `{id, normativo, texto, autor, timestamp}`

### O que o sistema detecta automaticamente

**Padrões de feedback reconhecidos:**
- "não se aplica" / "nao se aplica"
- "deveria ser APLICÁVEL" / "deveria ser MONITORAR"
- "classificação errada" / "classificação incorreta"
- "correto" / "confirmo" / "confirmado"
- "criticidade: ALTO" / "criticidade deveria ser MÉDIO"
- "falta incluir" / "retirar"
- Menções a normas: "Resolução BCB nº 569", "Instrução Normativa BCB nº 737", etc.
- "falso positivo"
- "impacta o iFood" / "devemos monitorar"

**Tipos de feedback classificados:**
- **Corretivo — NÃO APLICÁVEL:** Normativo foi marcado como APLICÁVEL mas não é
- **Corretivo — APLICÁVEL:** Normativo foi marcado como NÃO APLICÁVEL mas deveria ser
- **Corretivo — MONITORAR:** Classificação deveria ser MONITORAR
- **Ajuste de criticidade:** Mudar nível de criticidade (CRÍTICO, ALTO, MÉDIO, BAIXO)
- **Ajuste de escopo — Incluir:** Adicionar palavra-chave de triagem
- **Ajuste de escopo — Excluir:** Remover palavra-chave (falso positivo)
- **Confirmação:** A classificação automática estava correta
- **Outro:** Qualquer outro tipo de observação

### Arquivos gerados

| Arquivo | Descrição |
|---|---|
| `feedback_pendente.json` | Fila de feedbacks aguardando processamento pelo Planner |
| `feedbacks_processados.json` | IDs de mensagens já tratadas (evita duplicatas) |
| `feedback_inbox.json` | Arquivo de entrada manual (FALLBACK) |
| `logs/feedback_YYYY-MM-DD.log` | Log diário de execução do pipeline |

### Workflow de processamento

```
┌─────────────────────────────────────────┐
│ Giovanna clica "💬 Feedback ao Claw"    │
│ no Slack e envia mensagem no Toqan      │
└───────────────┬─────────────────────────┘
                │
                v
┌─────────────────────────────────────────┐
│ Planner (Claw) — protocolo imediato     │
│ - Identifica normativo e tipo           │
│ - Registra em FEEDBACK.md              │
│ - Push para GitHub                      │
└───────────────┬─────────────────────────┘
                │
         ┌──────┴──────────────────────┐
         │ Corretivo?                  │ Confirmação / Ajuste?
         v                             v
┌─────────────────────┐     ┌──────────────────────────┐
│ Cria tarefa:        │     │ Confirma para Giovanna    │
│ pipeline_reanalise  │     │ — nenhuma ação adicional  │
│ .py (event-driven)  │     └──────────────────────────┘
└─────────┬───────────┘
          v
┌─────────────────────────────────────────┐
│ pipeline_reanalise.py executa:          │
│ - Relê normativo + REASONING_LAYER      │
│ - Gera nova análise corrigida           │
│ - Atualiza GitHub                       │
│ - Notifica Slack (🔄 REANÁLISE)         │
└─────────────────────────────────────────┘
```

### Gap residual (G-03 parcial)

**Limitação atual:** A Slack API requer bot token que não está configurado no proxy do Toqan.

**Workaround ativo:** Sistema opera em modo FALLBACK usando `feedback_inbox.json`.

**Para habilitar detecção automática 100%:**
1. Configurar Slack Bot Token em **Settings > Integrations**
2. Domínio: `slack.com/api`
3. Scopes necessários:
   - `channels:history` — ler mensagens de canais públicos/privados
   - `groups:history` — ler mensagens de canais privados
   - `users:read` — identificar autores de mensagens

**Status de resolução:**
- ✅ Script de detecção criado e funcionando
- ✅ Fallback via `feedback_inbox.json` implementado
- ✅ Log de execução gerado automaticamente
- ✅ Bloco de orientação adicionado à notificação Slack
- ⚠️  Detecção via Slack API aguarda configuração de token (bloqueio externo ao Claw)

### Como usar o modo FALLBACK

**Para Giovanna:**

Quando quiser registrar feedback sobre um normativo sem usar o chat Toqan:

1. Abra `data/normativos-bcb/feedback_inbox.json`
2. Adicione uma entrada na lista JSON:
   ```json
   [
     {
       "id": "fb_2026_05_26_001",
       "normativo": "Resolução BCB nº 569",
       "texto": "Esse normativo não se aplica ao iFood Pago, somos IP não banco.",
       "autor": "Giovanna",
       "timestamp": "2026-05-26T14:00:00-03:00"
     }
   ]
   ```
3. O próximo agendamento do pipeline detectará e processará automaticamente

**Campos obrigatórios:** `id`, `texto`
**Campos opcionais:** `normativo`, `autor`, `timestamp`

---

*Automação de Feedback v5.0 — Event-driven (sem agendamento fixo) — 2026-05-28 | iFood Pago Compliance*
