# DECISION_AUDIT.csv — Registro Persistente de Decisões

## Propósito

Fonte **DINÂMICA** de contexto para:
- **RAG do agente Toqan** (aprendizado contínuo via `consultar_decisoes_recentes()`)
- **Análise temporal** de decisões (padrões, tendências, evolução)
- **Auditoria completa** do sistema (rastreabilidade end-to-end)
- **Futuro treinamento em Databricks** (dataset rotulado de alta qualidade)

## Conceito

> **NUNCA sobrescrever — sempre adicionar (append-only)**

Cada avaliação gera uma **nova linha** com timestamp único.
Reanálises adicionam novas linhas referenciando a avaliação original via `normativo_id`.

```
Linha 1: avaliação_inicial (pipeline_bcb)
Linha 2: reanalise_feedback (pipeline_reanalise) — mesmo normativo_id
Linha 3: nova avaliação inicial de outro normativo
...
```

## Separação Estático vs. Dinâmico

| Tipo | Arquivos | Função |
|---|---|---|
| **ESTÁTICO** | `CONTEXTO_IFOOD_PAGO.md`, `DECISION_LAYER.md`, `REASONING_LAYER.md`, `REASONING_LAYER_POLITICAS.md` | Regras, políticas, contexto institucional |
| **DINÂMICO** | `DECISION_AUDIT.csv` | Histórico de todas as avaliações + racionais |

## Schema — 32 Colunas

| # | Coluna | Tipo | Descrição | Exemplo |
|---|---|---|---|---|
| 1 | `audit_id` | string | ID único da avaliação | `audit_2026_05_28_a1b2c3d4` |
| 2 | `timestamp` | datetime | ISO 8601 com timezone | `2026-05-28T08:15:32-03:00` |
| 3 | `normativo_id` | string | ID do normativo | `normativos_52913` |
| 4 | `normativo_tipo` | string | Tipo da norma | `Resolução CMN` |
| 5 | `normativo_numero` | string | Número da norma | `5306` |
| 6 | `normativo_ano` | string | Ano da norma | `2026` |
| 7 | `normativo_titulo` | string | Título completo | `Resolução CMN nº 5306...` |
| 8 | `avaliacao_tipo` | string | Tipo de avaliação | `inicial` / `reanalise_feedback` / `reanalise_automatica` |
| 9 | `avaliacao_origem` | string | Quem fez a avaliação | `pipeline_bcb` / `agente_toqan` / `pipeline_reanalise` |
| 10 | `classificacao_final` | string | Resultado | `APLICÁVEL` / `MONITORAR` / `NÃO APLICÁVEL` |
| 11 | `classificacao_anterior` | string | Classificação anterior | `MONITORAR` / `null` |
| 12 | `racional_classificacao` | text | Racional COMPLETO da classificação | Ver exemplo abaixo |
| 13 | `reasoning_layer_aplicado` | text | Como o reasoning layer foi usado | `"Camada 1 CONTEXTO: IP S5..."` |
| 14 | `decision_map_aplicado` | text | Como o decision map foi usado | `"PASSO 2: norma menciona IPs → Relevante"` |
| 15 | `avaliacao_risco` | string | Score de risco | `CRÍTICO` / `ALTO` / `MÉDIO` / `BAIXO` |
| 16 | `racional_risco` | text | Racional da avaliação de risco | `"Impacto Operacional: ALTO..."` |
| 17 | `pilares_risco_detalhado` | JSON | Detalhamento dos 4 pilares | `{"operacional":"ALTO","regulatorio":"CRÍTICO"...}` |
| 18 | `resumo_logica` | text | Lógica por trás do resumo | `"Resumo focou em: objeto da norma (Art 1º)..."` |
| 19 | `areas_responsaveis` | JSON | Áreas mapeadas | `["Produto — PIX","Compliance Regulatório"]` |
| 20 | `feedback_id` | string | ID do feedback | `feedback_1` / `null` |
| 21 | `feedback_tipo` | string | Tipo de feedback | `Corretivo` / `Confirmação` / `null` |
| 22 | `feedback_autor` | string | Quem deu feedback | `Giovanna Batistutti` / `null` |
| 23 | `feedback_texto` | text | Texto do feedback | `"Esse normativo não se aplica..."` / `null` |
| 24 | `correcao_aplicada` | text | Como a análise foi corrigida | `"Classificação alterada de MONITORAR para..."` / `null` |
| 25 | `nova_logica_pos_correcao` | text | Nova lógica após correção | `"Reavaliado: crédito imobiliário fora escopo..."` |
| 26 | `politicas_impactadas` | JSON | Políticas internas citadas | `["iFP-POL-002","iFP-POL-015"]` |
| 27 | `palavras_chave_matched` | JSON | Keywords que dispararam classificação | `["instituição de pagamento","pix"]` |
| 28 | `texto_integral_fonte` | string | Fonte do texto | `dou_pdf` / `agregador` / `ementa` |
| 29 | `confianca_analise` | string | Nível de confiança | `alta` / `media` / `baixa` |
| 30 | `observacoes` | text | Observações adicionais | Qualquer nota relevante |
| 31 | `github_commit_sha` | string | SHA do commit no GitHub | `1d1811fd8b86` / `null` |
| 32 | `slack_message_ts` | string | Timestamp da mensagem Slack | `1234567890.123456` / `null` |

## Exemplo de racional_classificacao (campo mais rico)

```
Normativo: Resolução CMN nº 5306 (2026).
Reasoning Layer aplicado:
- Camada 1 (CONTEXTO): iFood Pago = IP S5 + SCD.
- Camada 2 (DECISION): PASSO 2 - norma menciona crédito imobiliário.
- Verificação tema vs produto: crédito imobiliário NÃO operado.
- Regra geral ativa (Feedback #1): crédito imobiliário sempre NÃO APLICÁVEL.
Resultado: ❌ NÃO APLICÁVEL.
Confiança: ALTA (regra geral confirmada).
```

## Uso

### Pipeline (automático — Step 12)

```python
from skills.normativos_bcb.modules.auditoria import registrar_avaliacao_inicial

racional_completo = {
    "reasoning_layer": f"Camada 1: {contexto_aplicado}. Camada 2: {decision_aplicado}",
    "decision_map": f"PASSO 2 aplicado: {passos_executados}",
    "risco_detalhado": {
        "operacional": avaliacao.impacto_operacional,
        "regulatorio": avaliacao.impacto_regulatorio,
        "financeiro": avaliacao.impacto_financeiro,
        "clientes": avaliacao.impacto_clientes,
    },
    "resumo_foco": f"Resumo priorizou: {resumo.aspectos_priorizados}",
    "politicas": classificacao.politicas_impactadas,
    "keywords": classificacao.palavras_chave_matched,
}

audit_id = registrar_avaliacao_inicial(
    normativo=norm,
    classificacao=classificacao,
    avaliacao_risco=avaliacao,
    resumo=resumo,
    responsaveis=resp,
    racional_completo=racional_completo,
    config=config,
)
# Retorna audit_id, ex: "audit_2026_05_28_a1b2c3d4"
```

### Reanálise (automático)

```python
from skills.normativos_bcb.modules.auditoria import registrar_reanalise

audit_id = registrar_reanalise(
    normativo_id=normativo_id,
    feedback_id=feedback_id,
    classificacao_anterior="MONITORAR",
    classificacao_nova="NÃO APLICÁVEL",
    racional_correcao={
        "reasoning_layer": novo_reasoning,
        "decision_map": novo_decision_map,
        "justificativa_mudanca": "Crédito imobiliário fora do escopo",
        "nova_logica": "Regra geral: crédito imobiliário = NÃO APLICÁVEL",
    },
    feedback_autor="Giovanna Batistutti",
    feedback_texto="Esse normativo não se aplica ao iFood Pago.",
    config=config,
)
```

### Agente Toqan (RAG dinâmico)

```python
from skills.normativos_bcb.modules.auditoria import (
    formatar_contexto_rag,
    consultar_historico_normativo,
)

# Contexto dos últimos 60 dias
contexto_dinamico = formatar_contexto_rag(dias=60)

# Histórico completo de um normativo específico (para reanálise)
historico = consultar_historico_normativo("normativos_52913")

# Injetar no prompt:
prompt = f"""
{contexto_dinamico}

{historico_formatado}

Agora avalie o normativo atual...
"""
```

## Sincronização GitHub

**Localização GitHub:** `audit/DECISION_AUDIT.csv` em `giovannabatistutti-ctrl/normativos_md`

**Fluxo:**
1. Append local em `data/normativos-bcb/DECISION_AUDIT.csv`
2. Push automático para GitHub via API (PUT com SHA para update)
3. SHA do commit atualizado no registro (campo `github_commit_sha`)
4. **Fallback:** Se GitHub falhar, dados ficam seguros localmente

## Queries Úteis (Python)

```python
import csv
from pathlib import Path

audit = Path("data/normativos-bcb/DECISION_AUDIT.csv")

# Carregar todos os registros
with open(audit) as f:
    registros = list(csv.DictReader(f))

# Filtrar por classificação
aplicaveis = [r for r in registros if r["classificacao_final"] == "APLICÁVEL"]

# Filtrar por período
from datetime import datetime, timedelta, timezone
BRASILIA = timezone(timedelta(hours=-3))
limite = datetime.now(BRASILIA) - timedelta(days=30)
recentes = [
    r for r in registros
    if datetime.fromisoformat(r["timestamp"]) >= limite
]

# Evolução de um normativo
historico = [r for r in registros if r["normativo_id"] == "normativos_52913"]

# Feedbacks corretivos
feedbacks = [r for r in registros if r["avaliacao_tipo"] == "reanalise_feedback"]

# Estatísticas
from collections import Counter
clf_counts = Counter(r["classificacao_final"] for r in registros)
print(clf_counts)  # Counter({'APLICÁVEL': N, 'MONITORAR': M, 'NÃO APLICÁVEL': K})
```

## Databricks (Futuro)

Para importar no Databricks:

```python
# PySpark
df = spark.read.option("header", "true") \
               .option("quote", '"') \
               .option("escape", '"') \
               .csv("dbfs:/mnt/ifoodpago/normativos/DECISION_AUDIT.csv")

# Analisar padrões
df.groupBy("classificacao_final", "normativo_tipo").count().show()
df.filter(df.avaliacao_tipo == "reanalise_feedback").select("feedback_texto", "correcao_aplicada").show()
```

## Localização dos Arquivos

| Arquivo | Localização |
|---|---|
| CSV local | `data/normativos-bcb/DECISION_AUDIT.csv` |
| CSV GitHub | `audit/DECISION_AUDIT.csv` (repo: `giovannabatistutti-ctrl/normativos_md`) |
| Módulo Python | `skills/normativos-bcb/modules/auditoria.py` |
| README | `data/normativos-bcb/DECISION_AUDIT_README.md` |
