"""
jira_updater.py
===============
Módulo de atualização de tickets Jira após processamento do aditamento.

Função principal: atualizar_ticket(ticket_id, resultado) -> bool

Comportamento por score:
  - Score >= 0.90: comentário de sucesso com link do documento
  - Score < 0.90: comentário com link + lista de campos pendentes

API: https://ifood.atlassian.net/rest/api/3/issue/{ticket}/comment (proxy injeta auth)
"""

import logging
import requests

logger = logging.getLogger(__name__)

JIRA_BASE_URL = "https://ifood.atlassian.net"
THRESHOLD_AUTONOMO = 0.90


def atualizar_ticket(ticket_id: str, resultado: dict) -> bool:
    """
    Atualiza o ticket Jira com comentário sobre o resultado do processamento.

    Args:
        ticket_id: ID do ticket Jira (ex: "JURFIN-1234")
        resultado: dict combinado de montagem + doc com chaves:
            - doc_url       (str): link do documento
            - doc_nome      (str): nome do documento
            - score         (float): score de confiança
            - decisao       (str): "AUTONOMO" ou "REVISAO_HUMANA"
            - campos_pendentes (list[str]): campos pendentes
            - perguntas_para_advogado (list[str]): perguntas formatadas
            - modulos_selecionados (list[str]): módulos incluídos

    Returns:
        True se comentário foi postado com sucesso, False caso contrário.
    """
    score_val = resultado.get("score", {})
    if isinstance(score_val, dict):
        score = float(score_val.get("score", 0.0))
        decisao = score_val.get("decisao", "REVISAO_HUMANA")
    else:
        score = float(score_val) if score_val else 0.0
        decisao = resultado.get("decisao", "REVISAO_HUMANA")

    doc_url = resultado.get("doc_url") or "[sem link]"
    campos_pendentes = resultado.get("campos_pendentes", [])
    perguntas = resultado.get("perguntas_para_advogado", [])
    modulos = resultado.get("modulos_selecionados", [])

    if score >= THRESHOLD_AUTONOMO:
        texto = _montar_comentario_sucesso(score, doc_url, modulos)
    else:
        texto = _montar_comentario_pendente(score, doc_url, campos_pendentes, perguntas)

    return _postar_comentario(ticket_id, texto)


# ---------------------------------------------------------------------------
# Templates de comentário
# ---------------------------------------------------------------------------

def _montar_comentario_sucesso(score: float, doc_url: str, modulos: list) -> str:
    """Comentário para score >= 0.90 (geração autônoma)."""
    modulos_str = ", ".join(modulos) if modulos else "padrão"
    return (
        f"*Pipeline de Aditamentos — Concluído*\n\n"
        f"O aditamento foi gerado automaticamente com score *{score:.0%}*.\n\n"
        f"*Documento:* {doc_url}\n\n"
        f"*Módulos incluídos:* {modulos_str}"
    )


def _montar_comentario_pendente(
    score: float,
    doc_url: str,
    campos_pendentes: list,
    perguntas: list,
) -> str:
    """Comentário para score < 0.90 (revisão manual necessária)."""
    n = len(campos_pendentes)

    msg = (
        f"*Pipeline de Aditamentos — Campos Pendentes*\n\n"
        f"O aditamento foi processado com score *{score:.0%}* (abaixo do threshold de 90%).\n\n"
        f"*Documento (rascunho):* {doc_url}\n\n"
    )

    if n > 0:
        if perguntas:
            # Pegar somente as perguntas formatadas (após o cabeçalho)
            itens = [p for p in perguntas if p.strip().startswith("•")]
            if itens:
                lista_perguntas = "\n".join(itens)
            else:
                lista_perguntas = "\n".join(f"• {c}" for c in campos_pendentes)
        else:
            lista_perguntas = "\n".join(f"• {c}" for c in campos_pendentes)

        msg += f"Os seguintes campos precisam ser informados:\n\n{lista_perguntas}\n\n"
        msg += "Por favor responda cada ponto acima para que o aditamento possa ser gerado automaticamente."

    return msg


# ---------------------------------------------------------------------------
# Envio via API Jira
# ---------------------------------------------------------------------------

def _postar_comentario(ticket_id: str, body: str) -> bool:
    """
    Posta comentário no Jira via rest/api/3/issue/{ticket_id}/comment.
    O proxy injeta autenticação automaticamente.
    """
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}/comment"

    # Jira API v3 usa formato ADF (Atlassian Document Format)
    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": body
                        }
                    ]
                }
            ]
        }
    }

    try:
        resp = requests.post(url, json=payload, timeout=30)
    except requests.exceptions.RequestException as exc:
        logger.error("atualizar_ticket: erro de conexão Jira — %s", exc)
        return False

    if resp.status_code in (401, 403, 407):
        logger.error(
            "atualizar_ticket: credencial Jira não configurada no proxy (HTTP %d)",
            resp.status_code,
        )
        return False

    if not resp.ok:
        logger.error(
            "atualizar_ticket: erro HTTP %d — %s",
            resp.status_code, resp.text[:300],
        )
        return False

    logger.info("atualizar_ticket: comentário postado no ticket %s", ticket_id)
    return True


# ---------------------------------------------------------------------------
# Remote link do Google Doc no ticket Jira
# ---------------------------------------------------------------------------

def adicionar_link_doc_jira(ticket_id: str, doc_url: str, doc_nome: str,
                             score: float, decisao: str) -> bool:
    """
    Adiciona o Google Doc gerado como remote link no ticket Jira.
    Usa a API de remote issue links para criar um link clicável no painel do ticket.

    Args:
        ticket_id: ID do ticket Jira (ex: "JURFIN-1234")
        doc_url: URL completa do Google Doc
        doc_nome: Nome/title do documento
        score: Score de confiança (0.0 a 1.0)
        decisao: "AUTONOMO" ou "REVISAO_HUMANA"

    Returns:
        True se remote link ou fallback comentário foi postado com sucesso.
    """
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}/remotelink"

    status_icon = "✅" if score >= 0.90 else "⚠️"
    summary_text = f"{status_icon} Score: {score:.0%} | Decisão: {decisao}"

    payload = {
        "globalId": f"google-doc-{ticket_id}",
        "application": {
            "type": "com.google.drive",
            "name": "Google Drive — iFood Benefícios"
        },
        "relationship": "Minuta gerada pelo pipeline",
        "object": {
            "url": doc_url,
            "title": doc_nome,
            "icon": {
                "url16x16": "https://drive.google.com/favicon.ico",
                "title": "Google Docs"
            },
            "status": {
                "resolved": False,
                "icon": {
                    "url16x16": "https://www.google.com/images/icons/product/docs-16.png",
                    "title": summary_text,
                    "link": doc_url
                }
            }
        }
    }

    try:
        resp = requests.post(url, json=payload, timeout=30)
    except requests.exceptions.RequestException as exc:
        logger.error("adicionar_link_doc_jira: erro de conexão — %s", exc)
        return False

    if resp.status_code in (200, 201):
        logger.info("adicionar_link_doc_jira: remote link adicionado ao ticket %s", ticket_id)
        return True

    # Fallback: se remote link falhar, adiciona como comentário rico
    logger.warning("adicionar_link_doc_jira: remote link falhou (HTTP %d) — usando comentário", resp.status_code)
    return _adicionar_comentario_com_link(ticket_id, doc_url, doc_nome, score, decisao)


def _adicionar_comentario_com_link(ticket_id: str, doc_url: str, doc_nome: str,
                                    score: float, decisao: str) -> bool:
    """Fallback: adiciona o doc como comentário rico no Jira."""
    status_icon = "✅" if score >= 0.90 else "⚠️"
    body = (
        f"**Pipeline de Aditamentos — Minuta Gerada {status_icon}**\n\n"
        f"**Documento:** {doc_url}\n"
        f"**Nome:** {doc_nome}\n"
        f"**Score:** {score:.0%} | **Decisão:** {decisao}\n\n"
        f"*Clique no link acima para revisar a minuta no Google Docs.*\n\n"
        f"Após revisão, adicione um comentário com **`APROVADO`** para notificar o time comercial via Slack."
    )
    return _postar_comentario(ticket_id, body)


# ---------------------------------------------------------------------------
# Compatibilidade com classe legada JiraUpdater
# ---------------------------------------------------------------------------

class JiraUpdater:
    """Wrapper de classe para compatibilidade com pipeline_aditamentos.py legado."""

    def __init__(self, config: dict):
        self.base_url = config.get("base_url", JIRA_BASE_URL)

    def update(self, ticket_id: str, score_result: dict) -> None:
        """Delega para atualizar_ticket()."""
        atualizar_ticket(ticket_id, score_result)
