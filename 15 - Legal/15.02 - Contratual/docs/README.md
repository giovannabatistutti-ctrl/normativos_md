# Pipeline 15 — Aditamentos Contratuais iFood Benefícios

## Visão Geral

Pipeline de aditamentos contratuais iFood Benefícios — **Módulo 15**. Orquestração automática de análise e geração de aditivos contratuais.

## Arquitetura

O pipeline é composto por dois agentes LLM especializados:

- **Agente 1 — Leitor/Extrator**: Lê tickets Jira (projeto JURFIN), extrai detalhes do aditamento solicitado e lê o contrato base (PDF/TXT).
- **Agente 2 — Montador/Validador**: Monta o texto do aditamento com base nos módulos templates e valida consistência.

## Fluxo

1. `pipeline_aditamentos.py` — Orquestração principal (lê Jira → chama Agente 1 → chama Agente 2 → gera Google Docs)
2. `monitor_pos_revisao.py` — Monitoramento de tickets em pós-revisão
3. `web_app.py` — Interface web (Flask/Streamlit)

## Módulos (skills/layers)

| Arquivo | Descrição |
|---|---|
| `REASONING_LAYER.md` | Camada de raciocínio regulatório |
| `DECISION_LAYER.md` | Árvore de decisão de aplicabilidade |
| `DECISION_MAP.md` | Mapa de decisões por módulo |
| `FEEDBACK.md` | Loop de feedback e validação |
| `PROMPT_AGENTE1_LEITOR.md` | Prompt do Agente 1 |
| `PROMPT_AGENTE2_MONTADOR.md` | Prompt do Agente 2 |

## Templates de Módulos

- `01_cabecalho.md` — Cabeçalho do aditamento
- `02_prorrogacao_vigencia.md` — Prorrogação de vigência
- `03_retirada_renovacao_automatica.md` — Retirada de renovação automática
- `04_aviso_previo.md` — Aviso prévio
- `05_cessao.md` — Cessão
- `06_alteracao_produto.md` — Alteração de produto
- `07_alteracao_valor.md` — Alteração de valor
- `08_rodape_assinaturas.md` — Rodapé / assinaturas
- `09_clausula_geral.md` — Cláusula geral
- `10_isa.md` — ISA (Índice de Saldo Agregado)
- `11_saldo_extra.md` — Saldo extra
- `12_saldo_natal.md` — Saldo natal

## Base Regulatória

- Contrato base: `termos_condicoes_gerais_ifood_beneficios_nov2025.txt`
- Decisões auditadas: `data/audit/DECISION_AUDIT.csv`

## Tecnologias

- Python 3.11+
- Jira API (JURFIN)
- Google Docs API
- LLM (OpenAI compatible)
- Flask / Streamlit (web)
- Slack notifications
