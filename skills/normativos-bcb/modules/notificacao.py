"""
Módulo 7 — notificacao.py
Constrói e envia notificação Slack com blocos estruturados (Slack Blocks API)
para novos normativos analisados pelo pipeline BCB.

Entradas:
    normativo (Normativo): Normativo capturado.
    classificacao (ClassificacaoNormativo): Resultado do reasoning.
    avaliacao (AvaliacaoRisco): Resultado da avaliação de risco.
    resumo (ResumoExecutivo): Resumo executivo.
    responsaveis (List[Responsavel]): Lista de responsáveis.
    resultado_persistencia (dict): Resultado da persistência (links GitHub).
    config (dict): Configuração do config.json.

Saídas:
    dict: {"success": bool, "status_code": int, "error": str}

Uso:
    from modules.notificacao import enviar_notificacao_slack
    resultado = enviar_notificacao_slack(normativo, classificacao, avaliacao, resumo, responsaveis)
"""

from __future__ import annotations

import json
import warnings
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import requests

from .captura import Normativo
from .reasoning import ClassificacaoNormativo
from .avaliacao_risco import AvaliacaoRisco
from .resumo import ResumoExecutivo
from .responsaveis import Responsavel

warnings.filterwarnings("ignore")

BRASILIA = timezone(timedelta(hours=-3))

# ─── Emojis e cores ────────────────────────────────────────────────────────────

EMOJI_CLASSIFICACAO = {
    "APLICÁVEL": "🔴",
    "MONITORAR": "🟡",
    "NÃO APLICÁVEL": "🟢",
}

EMOJI_SCORE = {
    "CRÍTICO": "🚨",
    "ALTO": "🔴",
    "MÉDIO": "🟡",
    "BAIXO": "🟢",
}

COLOR_CLASSIFICACAO = {
    "APLICÁVEL": "#FF0000",
    "MONITORAR": "#FFA500",
    "NÃO APLICÁVEL": "#00AA00",
}

EMOJI_PILAR = {
    "Impacto Operacional": "⚙️",
    "Impacto Regulatório": "⚖️",
    "Impacto Financeiro": "💰",
    "Impacto em Clientes": "👥",
    "Impacto Estratégico": "🎯",
}


def _carregar_config(config: Optional[Dict] = None) -> Dict:
    if config:
        return config
    config_path = Path(__file__).parent.parent / "config.json"
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {}


def _truncar(texto: str, max_len: int = 300) -> str:
    """Trunca texto para limite do Slack."""
    if len(texto) <= max_len:
        return texto
    return texto[:max_len - 3] + "..."


def _construir_blocos_slack(
    normativo: Normativo,
    classificacao: ClassificacaoNormativo,
    avaliacao: AvaliacaoRisco,
    resumo: ResumoExecutivo,
    responsaveis: List[Responsavel],
    resultado_persistencia: Optional[Dict] = None,
) -> List[Dict]:
    """
    Constrói lista de blocos Slack (Blocks API) para o normativo.

    Estrutura:
      1. Header — nome da norma
      2. Classificação + score (section com fields)
      3. Divider
      4. Resumo executivo (O que determina)
      5. Pilares de risco impactados
      6. Áreas responsáveis
      7. Links (BCB + GitHub)
      8. Footer
    """
    emoji_class = EMOJI_CLASSIFICACAO.get(classificacao.classificacao, "⚪")
    emoji_score = EMOJI_SCORE.get(avaliacao.score_consolidado, "⚪")

    blocos = []

    # ── 1. Header ──────────────────────────────────────────────────────────────
    blocos.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"📋 {_truncar(normativo.titulo, 150)}",
            "emoji": True,
        },
    })

    # ── 2. Classificação + Score ────────────────────────────────────────────────
    blocos.append({
        "type": "section",
        "fields": [
            {
                "type": "mrkdwn",
                "text": f"*Classificação:*\n{emoji_class} *{classificacao.classificacao}*",
            },
            {
                "type": "mrkdwn",
                "text": f"*Criticidade:*\n{emoji_score} *{avaliacao.score_consolidado}*",
            },
            {
                "type": "mrkdwn",
                "text": f"*Tipo:*\n{normativo.tipo}",
            },
            {
                "type": "mrkdwn",
                "text": f"*Publicação:*\n{normativo.data_publicacao[:10] if normativo.data_publicacao else 'N/D'}",
            },
        ],
    })

    # ── Urgência ────────────────────────────────────────────────────────────────
    if avaliacao.urgente:
        blocos.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "⚠️ *PRAZO DE ADEQUAÇÃO IMINENTE* — Priorizar análise e ação imediata.",
            },
        })

    blocos.append({"type": "divider"})

    # ── 3. Resumo executivo ────────────────────────────────────────────────────
    o_que = _truncar(resumo.o_que_determina, 600)
    blocos.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*📝 O que a norma determina:*\n{o_que}",
        },
    })

    # Prazo de adequação
    if resumo.prazo_adequacao and resumo.prazo_adequacao != "Não identificado — verificar norma":
        blocos.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📅 Prazo de Adequação:* {resumo.prazo_adequacao}",
            },
        })

    blocos.append({"type": "divider"})

    # ── 4. Pilares de risco ────────────────────────────────────────────────────
    pilares_texto = []
    for pilar_obj in [
        avaliacao.pilar_operacional,
        avaliacao.pilar_regulatorio,
        avaliacao.pilar_financeiro,
        avaliacao.pilar_clientes,
        avaliacao.pilar_estrategico,
    ]:
        emoji_p = EMOJI_PILAR.get(pilar_obj.pilar, "•")
        emoji_s = EMOJI_SCORE.get(pilar_obj.score, "⚪")
        pilares_texto.append(f"{emoji_p} *{pilar_obj.pilar}:* {emoji_s} {pilar_obj.score}")

    blocos.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*📊 Avaliação por Pilar:*\n" + "\n".join(pilares_texto),
        },
    })

    blocos.append({"type": "divider"})

    # ── 5. Ações requeridas ────────────────────────────────────────────────────
    if resumo.acoes_requeridas:
        acoes_str = "\n".join(f"• {a}" for a in resumo.acoes_requeridas[:4])
        blocos.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*✅ Ações Requeridas:*\n{_truncar(acoes_str, 500)}",
            },
        })

    # ── 6. Áreas responsáveis ──────────────────────────────────────────────────
    if responsaveis:
        resp_alta = [r for r in responsaveis if r.prioridade == "ALTA"][:3]
        resp_media = [r for r in responsaveis if r.prioridade == "MÉDIA"][:2]

        resp_linhas = []
        for r in resp_alta:
            resp_linhas.append(f"🔴 *{r.area} / {r.time}* — {_truncar(r.acao, 80)}")
        for r in resp_media:
            resp_linhas.append(f"🟡 *{r.area} / {r.time}* — {_truncar(r.acao, 80)}")

        if resp_linhas:
            blocos.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*👥 Áreas Responsáveis:*\n" + "\n".join(resp_linhas),
                },
            })

    # ── 7. Políticas a revisar ─────────────────────────────────────────────────
    if resumo.politicas_revisar:
        pol_str = "\n".join(f"• {p}" for p in resumo.politicas_revisar[:3])
        blocos.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📋 Políticas a Revisar:*\n{_truncar(pol_str, 400)}",
            },
        })

    blocos.append({"type": "divider"})

    # ── 8. Links ───────────────────────────────────────────────────────────────
    elementos_links = []

    if normativo.link:
        elementos_links.append({
            "type": "button",
            "text": {"type": "plain_text", "text": "📄 Íntegra no BCB", "emoji": True},
            "url": normativo.link,
            "action_id": "btn_bcb",
        })

    # Link GitHub (se persistência foi bem sucedida)
    if resultado_persistencia:
        github_md = resultado_persistencia.get("github_md", {})
        if github_md.get("success"):
            github_url = f"https://github.com/{_carregar_config().get('github_repo', 'giovannabatistutti-ctrl/normativos_md')}"
            elementos_links.append({
                "type": "button",
                "text": {"type": "plain_text", "text": "📁 Análise no GitHub", "emoji": True},
                "url": github_url,
                "action_id": "btn_github",
            })

    if elementos_links:
        blocos.append({
            "type": "actions",
            "elements": elementos_links,
        })

    # ── 9. Footer ─────────────────────────────────────────────────────────────
    data_analise = datetime.now(BRASILIA).strftime("%d/%m/%Y %H:%M")
    justificativa_curta = _truncar(classificacao.justificativa, 200)
    blocos.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": (
                    f"*Pipeline normativos-bcb | iFood Pago Compliance* — {data_analise}\n"
                    f"Confiança da classificação: {classificacao.confianca} | "
                    f"Justificativa: {justificativa_curta}"
                ),
            }
        ],
    })

    return blocos


def enviar_notificacao_slack(
    normativo: Normativo,
    classificacao: ClassificacaoNormativo,
    avaliacao: AvaliacaoRisco,
    resumo: ResumoExecutivo,
    responsaveis: List[Responsavel],
    resultado_persistencia: Optional[Dict] = None,
    config: Optional[Dict] = None,
) -> Dict:
    """
    Constrói e envia notificação Slack com blocos estruturados para um normativo analisado.

    Usa a Slack Blocks API para uma mensagem rica com:
      - Header com nome da norma
      - Classificação (APLICÁVEL/MONITORAR) com emoji
      - Score de criticidade
      - Resumo executivo (O que determina)
      - Pilares impactados
      - Áreas responsáveis
      - Link para íntegra no BCB e análise no GitHub

    Entradas:
        normativo (Normativo): Normativo capturado.
        classificacao (ClassificacaoNormativo): Resultado do reasoning.
        avaliacao (AvaliacaoRisco): Resultado da avaliação de risco.
        resumo (ResumoExecutivo): Resumo executivo.
        responsaveis (List[Responsavel]): Lista de responsáveis.
        resultado_persistencia (dict): Resultado da persistência (links GitHub). Opcional.
        config (dict): Configuração. Se None, carrega do config.json.

    Saídas:
        dict: {"success": bool, "status_code": int, "error": str}
    """
    cfg = _carregar_config(config)
    webhook_url = cfg.get("slack_webhook", "")

    if not webhook_url:
        return {"success": False, "status_code": 0, "error": "slack_webhook não configurado"}

    # Não enviar para NÃO APLICÁVEL (evitar spam)
    if classificacao.classificacao == "NÃO APLICÁVEL":
        return {
            "success": True,
            "status_code": 200,
            "error": "",
            "skipped": True,
            "reason": "NÃO APLICÁVEL — notificação suprimida",
        }

    blocos = _construir_blocos_slack(
        normativo, classificacao, avaliacao, resumo, responsaveis, resultado_persistencia
    )

    emoji_class = EMOJI_CLASSIFICACAO.get(classificacao.classificacao, "⚪")
    emoji_score = EMOJI_SCORE.get(avaliacao.score_consolidado, "⚪")

    payload = {
        "text": (
            f"{emoji_class} *Novo Normativo BCB* — {normativo.tipo} nº {normativo.numero} | "
            f"{classificacao.classificacao} | {emoji_score} {avaliacao.score_consolidado}"
        ),
        "blocks": blocos,
        "attachments": [
            {
                "color": COLOR_CLASSIFICACAO.get(classificacao.classificacao, "#808080"),
                "fallback": f"{normativo.titulo} — {classificacao.classificacao}",
            }
        ],
    }

    try:
        resp = requests.post(
            webhook_url,
            json=payload,
            verify=False,
            timeout=30,
            headers={"Content-Type": "application/json"},
        )
        success = resp.status_code == 200
        return {
            "success": success,
            "status_code": resp.status_code,
            "error": "" if success else resp.text[:300],
        }
    except Exception as exc:
        return {"success": False, "status_code": 0, "error": str(exc)}
