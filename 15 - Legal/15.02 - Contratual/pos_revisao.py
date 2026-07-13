"""
pos_revisao.py
==============
Módulo de notificação pós-revisão jurídica.

Fluxo:
  1. Advogado adiciona comentário "APROVADO" no Jira (ou muda status)
  2. Este módulo detecta a aprovação via poll do Jira
  3. Envia reply na thread original do Slack com link do documento final
  4. Notifica time comercial para enviar ao cliente / solicitar assinatura

Acionamento: chamado pelo monitor (scheduled task) ou pelo pipeline após
detectar mudança de status no Jira.
"""

import logging
import json
import requests
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

JIRA_BASE_URL = "https://ifood.atlassian.net"
SLACK_API_URL = "https://slack.com/api/chat.postMessage"
TRACKING_DIR = Path(__file__).parent.parent / "data" / "audit" / "pending_review"

# Palavras-chave que indicam aprovação do advogado no Jira
KEYWORDS_APROVACAO = ["APROVADO", "Aprovado", "aprovado", "REVISADO E APROVADO", "OK PARA ENVIO"]

# Palavras-chave que indicam que precisa de ajustes
KEYWORDS_AJUSTE = ["AJUSTE", "CORRIGIR", "PENDENTE", "RETORNAR"]


def verificar_aprovacao_jira(ticket_id: str) -> dict | None:
    """
    Verifica se o advogado aprovou o ticket no Jira.
    Retorna o comentário de aprovação ou None se não aprovado.
    """
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}/comment"
    params = {"orderBy": "-created", "maxResults": 10}

    try:
        resp = requests.get(url, params=params, timeout=20)
    except requests.exceptions.RequestException as exc:
        logger.error("verificar_aprovacao_jira: erro — %s", exc)
        return None

    if not resp.ok:
        logger.error("verificar_aprovacao_jira: HTTP %d", resp.status_code)
        return None

    data = resp.json()
    comentarios = data.get("comments", [])

    for comentario in comentarios:
        # Extrair texto do comentário (ADF → texto)
        texto = _extrair_texto_adf(comentario.get("body", {}))
        autor = comentario.get("author", {}).get("displayName", "")

        for keyword in KEYWORDS_APROVACAO:
            if keyword in texto:
                return {
                    "aprovado": True,
                    "autor": autor,
                    "texto": texto,
                    "comentario_id": comentario.get("id"),
                    "timestamp": comentario.get("created", "")
                }

    return None


def _extrair_texto_adf(node: object) -> str:
    """Converte ADF para texto plano."""
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        tipo = node.get("type", "")
        if tipo == "text":
            return node.get("text", "")
        return " ".join(_extrair_texto_adf(c) for c in node.get("content", [])).strip()
    if isinstance(node, list):
        return " ".join(_extrair_texto_adf(c) for c in node).strip()
    return ""


def notificar_aprovacao_slack(tracking_file: Path, aprovacao: dict) -> bool:
    """
    Envia reply na thread original do Slack após aprovação do advogado.

    Args:
        tracking_file: arquivo JSON com dados do acompanhamento
        aprovacao: dados do comentário de aprovação no Jira

    Returns:
        True se reply enviado com sucesso
    """
    dados = json.loads(tracking_file.read_text(encoding="utf-8"))

    canal = dados.get("slack_channel")
    thread_ts = dados.get("slack_message_ts")
    doc_url = dados.get("doc_url", "")
    doc_nome = dados.get("doc_nome", "Minuta")
    empresa = dados.get("empresa", "")
    ticket_id = dados.get("ticket_id", "")
    advogado = aprovacao.get("autor", dados.get("advogado", ""))

    if not canal or not thread_ts:
        logger.error("notificar_aprovacao_slack: sem canal/thread_ts para %s", ticket_id)
        return False

    mensagem = (
        f"✅ *Minuta revisada e aprovada pelo Jurídico — {empresa}*\n\n"
        f"📄 *Documento final:* <{doc_url}|{doc_nome}>\n"
        f"👤 *Aprovado por:* {advogado}\n"
        f"🎫 *Ticket:* {ticket_id}\n\n"
        f"📤 *Próximos passos para o time Comercial:*\n"
        f"  • Enviar o documento ao cliente para revisão; *ou*\n"
        f"  • Solicitar assinatura via Netlex/DocuSign\n\n"
        f"_Minuta gerada automaticamente pelo Pipeline de Aditamentos iFood Benefícios_"
    )

    payload = {
        "channel": canal,
        "thread_ts": thread_ts,
        "text": mensagem,
        "mrkdwn": True,
        "reply_broadcast": True   # também posta no canal, não só na thread
    }

    try:
        resp = requests.post(SLACK_API_URL, json=payload, timeout=30)
    except requests.exceptions.RequestException as exc:
        logger.error("notificar_aprovacao_slack: erro — %s", exc)
        return False

    if not resp.ok:
        logger.error("notificar_aprovacao_slack: HTTP %d", resp.status_code)
        return False

    data = resp.json()
    if not data.get("ok"):
        logger.error("notificar_aprovacao_slack: Slack error — %s", data.get("error"))
        return False

    logger.info("notificar_aprovacao_slack: reply enviado para thread %s do canal %s", thread_ts, canal)

    # Atualizar tracking file
    dados["status"] = "aprovado_e_notificado"
    dados["aprovado_em"] = datetime.now().isoformat(timespec="seconds")
    dados["aprovado_por"] = advogado
    tracking_file.write_text(json.dumps(dados, ensure_ascii=False, indent=2))

    return True


def processar_pendentes() -> dict:
    """
    Verifica todos os tickets pendentes de revisão e notifica os aprovados.
    Chamado pelo scheduler (monitor periódico).
    """
    if not TRACKING_DIR.exists():
        return {"verificados": 0, "aprovados": 0, "pendentes": 0}

    arquivos = list(TRACKING_DIR.glob("*.json"))
    verificados = 0
    aprovados = 0
    pendentes = 0

    for arquivo in arquivos:
        try:
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
            if dados.get("status") != "aguardando_revisao":
                continue

            ticket_id = dados.get("ticket_id")
            verificados += 1

            aprovacao = verificar_aprovacao_jira(ticket_id)
            if aprovacao and aprovacao.get("aprovado"):
                ok = notificar_aprovacao_slack(arquivo, aprovacao)
                if ok:
                    aprovados += 1
                    logger.info("processar_pendentes: %s aprovado e notificado", ticket_id)
            else:
                pendentes += 1
        except Exception as exc:
            logger.error("processar_pendentes: erro em %s — %s", arquivo.name, exc)

    return {"verificados": verificados, "aprovados": aprovados, "pendentes": pendentes}
