# Skill: normativos-bcb

Pipeline completo de monitoramento, análise e notificação de normativos publicados pelo **Banco Central do Brasil (BCB)** para o iFood Pago.

## Visão Geral

Esta skill automatiza o ciclo de vida completo de um normativo BCB:
1. **Captura** RSS do BCB + texto integral da norma
2. **Análise** de aplicabilidade usando o Reasoning Layer (REASONING_LAYER.md)
3. **Avaliação de risco** nos 5 pilares institucionais
4. **Resumo executivo** estruturado em PT-BR
5. **Mapeamento** de áreas e times responsáveis
6. **Persistência** local (JSON) + push para GitHub
7. **Notificação** via Slack (Blocks API)

## Estrutura de Arquivos

```
skills/normativos-bcb/
├── SKILL.md                  # Este arquivo
├── init.py                   # Entry point do pipeline
├── config.json               # Configurações (repo, webhook, feeds, paths)
├── modules/
│   ├── __init__.py           # Exporta todos os módulos
│   ├── captura.py            # Módulo 1: Captura RSS + íntegra
│   ├── reasoning.py          # Módulo 2: Reasoning layer + políticas
│   ├── avaliacao_risco.py    # Módulo 3: Avaliação 5 pilares
│   ├── resumo.py             # Módulo 4: Resumo executivo
│   ├── responsaveis.py       # Módulo 5: Áreas/times responsáveis
│   ├── persistencia.py       # Módulo 6: GitHub + memória semântica
│   └── notificacao.py        # Módulo 7: Slack com blocos estruturados
└── tests/
    └── test_modules.py       # Suite de testes
```

## Como Usar

### Execução completa (entry point)

```bash
# Monitorar normativos do ano atual
python3 skills/normativos-bcb/init.py

# Monitorar ano específico
python3 skills/normativos-bcb/init.py --ano 2026

# Executar sem buscar texto integral (mais rápido)
python3 skills/normativos-bcb/init.py --sem-integra

# Dry-run: analisar sem enviar para Slack/GitHub
python3 skills/normativos-bcb/init.py --dry-run

# Processar IDs específicos
python3 skills/normativos-bcb/init.py --ids normativos_52913,normativos_52914
```

### Uso modular (importação)

```python
import sys
sys.path.insert(0, "skills/normativos-bcb")

from modules import (
    capturar_normativos,
    classificar_normativo,
    avaliar_risco,
    gerar_resumo,
    mapear_responsaveis,
    salvar_analise,
    enviar_notificacao_slack,
)

# Carregar config
import json
config = json.loads(open("skills/normativos-bcb/config.json").read())

# Pipeline
normativos = capturar_normativos(ano=2026, config=config)
for norm in normativos:
    clf = classificar_normativo(norm, config=config)
    av = avaliar_risco(norm, clf, config=config)
    resp = mapear_responsaveis(norm, clf, av, config=config)
    resumo = gerar_resumo(norm, clf, av, resp, config=config)
    salvar_analise(norm, clf, av, resumo, resp, config=config)
    enviar_notificacao_slack(norm, clf, av, resumo, resp, config=config)
```

## Módulos — Entradas e Saídas

### Módulo 1 — captura.py

**Função principal:** `capturar_normativos(ano, enviados, config, buscar_integra)`

| Entrada | Tipo | Descrição |
|---|---|---|
| `ano` | int | Ano a monitorar (padrão: atual) |
| `enviados` | dict | Normativos já processados (anti-duplicata) |
| `config` | dict | Configuração do config.json |
| `buscar_integra` | bool | Se True, busca texto integral via HTTP |

| Saída | Tipo | Descrição |
|---|---|---|
| retorno | `List[Normativo]` | Lista de normativos novos com texto_integral |

**Dataclass `Normativo`:**
- `id`, `titulo`, `ementa`, `data_publicacao`, `data_vigencia`
- `link`, `tipo`, `numero`, `ano_norma`
- `texto_integral` ← **busca íntegra via HTTP no site BCB**
- `texto_fonte` ← "html", "pdf" ou "fallback"

---

### Módulo 2 — reasoning.py

**Função principal:** `classificar_normativo(normativo, config)`

Aplica a árvore de decisão do `REASONING_LAYER.md` em 5 passos:
1. Tipo e escopo declarado
2. Verifica se atinge iFood Pago (IP, SCD, Tipo 3, S5, Pix, Open Finance, ITP)
3. Verifica tema vs. produtos iFood Pago
4. Classifica: **APLICÁVEL / MONITORAR / NÃO APLICÁVEL**
5. Identifica políticas internas impactadas (via `REASONING_LAYER_POLITICAS.md`)

| Saída | Tipo | Descrição |
|---|---|---|
| retorno | `ClassificacaoNormativo` | Classificação com justificativa e políticas |

**Campos relevantes de `ClassificacaoNormativo`:**
- `classificacao`: APLICÁVEL / MONITORAR / NÃO APLICÁVEL
- `confianca`: ALTA / MÉDIA / BAIXA
- `justificativa`: explicação textual
- `passo2_razoes`: entidades do iFood Pago encontradas
- `passo3_temas`: keywords identificadas
- `passo5_politicas`: list de `PoliticaImpactada` (código, nome, área, ação)
- `data_vigencia`: extraída do texto

---

### Módulo 3 — avaliacao_risco.py

**Função principal:** `avaliar_risco(normativo, classificacao, config)`

Avalia 5 pilares institucionais:

| Pilar | O que avalia |
|---|---|
| **Impacto Operacional** | Processos, sistemas, produtos afetados |
| **Impacto Regulatório** | Sanções, prazo de adequação, obrigações |
| **Impacto Financeiro** | Custo de adequação, multas potenciais |
| **Impacto em Clientes** | B2C/B2B, proteção ao consumidor, LGPD |
| **Impacto Estratégico** | Transição credenciador, S5→S4/S3, Carteira Digital |

Score por pilar: **CRÍTICO / ALTO / MÉDIO / BAIXO**

Score consolidado usa média ponderada (Regulatório e Estratégico têm peso 1.5).

---

### Módulo 4 — resumo.py

**Função principal:** `gerar_resumo(normativo, classificacao, avaliacao, responsaveis, config)`

Gera `ResumoExecutivo` com:
- `o_que_determina`: síntese do texto integral (extrai Art. 1 quando possível)
- `para_quem_se_aplica`: entidades e produtos afetados
- `prazo_adequacao`: data de vigência identificada
- `acoes_requeridas`: lista de ações para o iFood Pago
- `politicas_revisar`: políticas internas a revisar
- `areas_responsaveis`: áreas/times (do módulo 5)
- `markdown`: documento Markdown completo pronto para publicação

---

### Módulo 5 — responsaveis.py

**Função principal:** `mapear_responsaveis(normativo, classificacao, avaliacao, config)`

Lógica de mapeamento:
1. Temas identificados → mapa tema → área/time (ex: PLD → Compliance/PLD-FT)
2. Políticas impactadas → área responsável da política
3. Pilares com score alto → acionar áreas específicas (TI, Financeiro, Diretoria)
4. Compliance sempre coordenador para normas APLICÁVEIS

Retorna `List[Responsavel]` ordenada por prioridade (ALTA → MÉDIA → BAIXA).

---

### Módulo 6 — persistencia.py

**Função principal:** `salvar_analise(normativo, classificacao, avaliacao, resumo, responsaveis, config)`

Operações:
1. Salva `data/normativos-bcb/{data}/{id}.json` — análise completa (memória semântica)
2. Salva `data/normativos-bcb/{data}/{nome}.md` — markdown do resumo
3. Push `normativos/{data}/{id}.json` → GitHub
4. Push `normativos/{data}/{nome}.md` → GitHub
5. Atualiza `README.md` do repo GitHub (tabela de normativos)
6. Atualiza `enviados.json` (anti-duplicata)

**Função auxiliar:** `push_github(remote_path, content, commit_msg, config)` → dict

---

### Módulo 7 — notificacao.py

**Função principal:** `enviar_notificacao_slack(normativo, classificacao, avaliacao, resumo, responsaveis, resultado_persistencia, config)`

Constrói mensagem com **Slack Blocks API**:

| Bloco | Conteúdo |
|---|---|
| Header | Nome da norma |
| Section | Classificação + Score (4 fields) |
| Section | ⚠️ Urgência (se prazo iminente) |
| Section | O que determina (síntese) |
| Section | Prazo de adequação |
| Section | 5 pilares com scores e emojis |
| Section | Ações requeridas |
| Section | Áreas responsáveis (alta/média prioridade) |
| Section | Políticas a revisar |
| Actions | Botões: Íntegra BCB + Análise GitHub |
| Context | Footer com data + justificativa |

**Regra:** Normas NÃO APLICÁVEL são suprimidas automaticamente.

---

## Configuração (config.json)

| Campo | Descrição |
|---|---|
| `github_repo` | Repositório GitHub para push |
| `slack_webhook` | URL do webhook Slack (#agenda-normativa-ifoodpago) |
| `bcb_feed` | URL do RSS BCB (com `{ano}` como placeholder) |
| `reasoning_layer_path` | Caminho para REASONING_LAYER.md |
| `politicas_path` | Caminho para REASONING_LAYER_POLITICAS.md |
| `feedback_path` | Caminho para FEEDBACK.md |
| `enviados_path` | Caminho para enviados.json (anti-duplicata) |
| `branch` | Branch do GitHub (main) |
| `keywords_aplicavel` | Keywords que indicam norma APLICÁVEL |
| `keywords_monitorar` | Keywords que indicam norma a MONITORAR |

---

## Como Adicionar Novas Políticas Internas

1. Abrir `data/normativos-bcb/REASONING_LAYER_POLITICAS.md`
2. Adicionar seção no formato padrão:
   ```
   #### iFP-POL-XXX — Nome da Política
   | Campo | Conteúdo |
   |---|---|
   | **Código** | iFP-POL-XXX |
   | **Áreas responsáveis** | Compliance (monitoramento) |
   | **Gatilhos regulatórios** | Normas BCB sobre [tema] |
   ```
3. O módulo `reasoning.py` carrega automaticamente as políticas a cada execução

---

## Como Interpretar Feedbacks

O arquivo `data/normativos-bcb/FEEDBACK.md` contém:

- **Regras Gerais Ativas**: aplicadas a todos os normativos futuros
- **Ajustes de Escopo**: keywords a incluir/excluir da triagem
- **Registro de Feedbacks**: feedbacks específicos de Giovanna sobre normativos já analisados

O módulo `reasoning.py` lê este arquivo antes de classificar e:
1. Verifica regras gerais ativas
2. Busca feedback específico pelo número do normativo
3. Sinaliza `feedback_aplicado=True` e inclui notas na classificação

Para adicionar um feedback, usar o template em `FEEDBACK.md` e avisar o agente.

---

## Arquivos de Referência

| Arquivo | Descrição |
|---|---|
| `data/normativos-bcb/REASONING_LAYER.md` | Árvore de decisão de aplicabilidade |
| `data/normativos-bcb/REASONING_LAYER_POLITICAS.md` | Sínteses das políticas internas |
| `data/normativos-bcb/FEEDBACK.md` | Feedbacks e regras ativas |
| `data/normativos-bcb/enviados.json` | Normativos já processados (anti-duplicata) |
| `data/normativos-bcb/pipeline_bcb.py` | Pipeline legado (v3.0) — referência |

---

## Executar Testes

```bash
# Instalar dependências (se necessário)
pip install requests beautifulsoup4

# Executar suite de testes
python3 skills/normativos-bcb/tests/test_modules.py

# Com pytest
python3 -m pytest skills/normativos-bcb/tests/ -v
```

---

## Dependências Python

- `requests` — HTTP (captura RSS + íntegra + Slack + GitHub)
- `beautifulsoup4` — Parsing HTML das páginas BCB
- `xml.etree.ElementTree` — Parsing RSS (stdlib)
- `dataclasses`, `pathlib`, `json`, `re`, `base64` — stdlib

---

*Skill criada em 2026-05-27 | iFood Pago — Compliance | Giovanna Batistutti*
