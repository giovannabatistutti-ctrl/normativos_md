"""
slack_notifier.py
=================
Módulo de notificação Slack — canal #aditamentos iFood Benefícios.

Função principal: notificar_thread(canal_id, thread_ts, resultado) -> tuple[bool, str]

Comportamento por score:
  - Score >= 0.90: mensagem de aditamento gerado automaticamente
  - Score <  0.90: rascunho pronto para revisão com campos pendentes

Canal configurado: C033DR3282G
API: https://slack.com/api/chat.postMessage (proxy injeta auth).
"""

import logging
import requests

logger = logging.getLogger(__name__)

SLACK_API_URL = "https://slack.com/api/chat.postMessage"
THRESHOLD_AUTONOMO = 0.90


def notificar_thread(canal_id: str, thread_ts: str, resultado: dict) -> tuple[bool, str]:
    """
    Posta notificação na thread Slack do canal informado.

    Args:
        canal_id: ID do canal Slack (ex: "C033DR3282G").
        thread_ts: Timestamp da mensagem pai para reply em thread.
                   Se vazio, posta como nova mensagem no canal.
        resultado: dict combinado de montagem + doc com chaves:
            - doc_url       (str): link do documento
            - doc_nome      (str): nome do documento
            - score         (float): score de confiança
            - decisao       (str): "AUTONOMO" ou "REVISAO_HUMANA"
            - campos_pendentes (list[str]): campos pendentes
            - perguntas_para_advogado (list[str]): perguntas formatadas
            - modulos_selecionados (list[str]): módulos incluídos
            - advogado_responsavel (str|None): nome do advogado

    Returns:
        Tuple (sucesso: bool, message_ts: str).
        message_ts é o timestamp da mensagem enviada (vazio em caso de falha).
    """
    score_val = resultado.get("score", {})
    if isinstance(score_val, dict):
        score = float(score_val.get("score", 0.0))
        decisao = score_val.get("decisao", "REVISAO_HUMANA")
    else:
        score = float(score_val) if score_val else 0.0
        decisao = resultado.get("decisao", "REVISAO_HUMANA")

    doc_url = resultado.get("doc_url") or "[sem link]"
    modulos = resultado.get("modulos_selecionados", [])
    campos_pendentes = resultado.get("campos_pendentes", [])
    perguntas = resultado.get("perguntas_para_advogado", [])
    advogado = resultado.get("advogado_responsavel") or "advogado-responsavel"

    if score >= THRESHOLD_AUTONOMO:
        texto = _montar_msg_autonomo(score, doc_url, modulos)
    else:
        texto = _montar_msg_revisao(score, doc_url, campos_pendentes, perguntas, advogado)

    return _postar_mensagem(canal_id, thread_ts, texto)

# ---------------------------------------------------------------------------
# Templates de mensagem
# ---------------------------------------------------------------------------

def _montar_msg_autonomo(score: float, doc_url: str, modulos: list) -> str:
    """Mensagem para score >= 0.90 (geração autônoma)."""
    modulos_str = ", ".join(modulos) if modulos else "padrão"
    return (
        f"✅ *Aditamento gerado automaticamente*\n"
        f"📄 *Documento:* <{doc_url}|Abrir no Google Docs>\n"
        f"🎯 *Score de confiança:* {score:.2f}\n"
        f"📋 *Módulos:* {modulos_str}\n"
        f"📤 *Próximo passo:* Documento enviado ao Netlex automaticamente"
    )


def _montar_msg_revisao(
    score: float,
    doc_url: str,
    campos_pendentes: list,
    perguntas: list,
    advogado: str,
) -> str:
    """Mensagem para score < 0.90 (revisão manual necessária)."""
    n = len(campos_pendentes)

    # Montar lista de perguntas para o advogado
    if perguntas:
        # Pegar somente as perguntas formatadas (após o cabeçalho)
        itens = [p for p in perguntas if p.startswith("  •")]
        lista_perguntas = "\n".join(itens) if itens else "\n".join(f"  • {c}" for c in campos_pendentes)
    else:
        lista_perguntas = "\n".join(f"  • {c}" for c in campos_pendentes)

    advogado_mention = f"@{advogado.replace(' ', '-').lower()}"

    msg = (
        f"📋 *Rascunho de aditamento pronto para revisão*\n"
        f"📄 *Documento:* <{doc_url}|Abrir no Google Docs>\n"
        f"🎯 *Score de confiança:* {score:.2f} — requer revisão\n"
    )
    if n > 0:
        msg += f"⚠️ *Campos pendentes ({n}):*\n{lista_perguntas}\n"

    msg += f"👤 *Advogado responsável:* {advogado_mention}"
    return msg


# ---------------------------------------------------------------------------
# Envio via API Slack
# ---------------------------------------------------------------------------

def _postar_mensagem(canal_id: str, thread_ts: str, texto: str) -> tuple[bool, str]:
    """
    Posta mensagem no Slack via chat.postMessage.
    O proxy injeta o token automaticamente.

    Returns:
        Tuple (sucesso: bool, message_ts: str).
    """
    payload: dict = {
        "channel": canal_id,
        "text": texto,
        "mrkdwn": True,
    }
    if thread_ts:
        payload["thread_ts"] = thread_ts

    try:
        resp = requests.post(SLACK_API_URL, json=payload, timeout=30)
    except requests.exceptions.RequestException as exc:
        logger.error("notificar_thread: erro de conexão Slack — %s", exc)
        return False, ""

    if resp.status_code in (401, 403, 407):
        logger.error(
            "notificar_thread: credencial Slack não configurada no proxy (HTTP %d)",
            resp.status_code,
        )
        return False, ""

    if not resp.ok:
        logger.error(
            "notificar_thread: erro HTTP %d — %s",
            resp.status_code, resp.text[:300],
        )
        return False, ""

    try:
        data = resp.json()
    except ValueError:
        logger.error("notificar_thread: resposta Slack inválida")
        return False, ""

    ok = data.get("ok", False)
    ts = data.get("ts", "")
    if not ok:
        logger.error("notificar_thread: Slack retornou ok=False — %s", data.get("error"))
        return False, ""

    logger.info(
        "notificar_thread: mensagem postada no canal %s ts=%s",
        canal_id, ts,
    )
    return ok, ts

# ---------------------------------------------------------------------------
# Compatibilidade com classe legada SlackNotifier
# ---------------------------------------------------------------------------

class SlackNotifier:
    """Wrapper de classe para compatibilidade com pipeline_aditamentos.py legado."""
    def __init__(self, config: dict):
        self.canal = config.get("canal_aditamentos", "C033DR3282G")
        self.api_url = SLACK_API_URL
    def notify(self, ticket_data: dict, score_result: dict) -> None:
        """Delega para notificar_thread() com thread_ts vazio."""
        resultado = {**ticket_data, **score_result}
        notificar_thread(self.canal, ticket_data.get("slack_ts", ""), resultado)
