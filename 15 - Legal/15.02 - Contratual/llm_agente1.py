"""
llm_agente1.py
==============
Agente 1: Leitor-Extrator — executa a extração estruturada de dados via LLM.

Responsabilidades:
  - Ler ticket Jira + thread Slack + contrato/proposta
  - Extrair campos com confiança, fonte e evidência
  - Retornar JSON estruturado com log de auditoria
"""

import json
import logging
from pathlib import Path

from .llm_client import chamar_llm

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
PROMPT_PATH = BASE_DIR / "skills" / "layers" / "PROMPT_AGENTE1_LEITOR.md"
FEEDBACK_PATH = BASE_DIR / "skills" / "layers" / "FEEDBACK.md"


def _carregar_prompt() -> str:
    """Carrega o system prompt do Agente 1."""
    return PROMPT_PATH.read_text(encoding="utf-8")


def _carregar_feedbacks_relevantes(n: int = 5) -> str:
    """
    Carrega os N feedbacks mais recentes como few-shot examples.
    Injetados no system prompt para melhoria contínua.
    """
    try:
        feedback_text = FEEDBACK_PATH.read_text(encoding="utf-8")
        # Extrair seções de feedback (marcadas com ### FEEDBACK-)
        linhas = feedback_text.split("\n")
        feedbacks = []
        atual = []
        for linha in linhas:
            if linha.startswith("### FEEDBACK-"):
                if atual:
                    feedbacks.append("\n".join(atual))
                atual = [linha]
            elif atual:
                atual.append(linha)
        if atual:
            feedbacks.append("\n".join(atual))

        # Pegar os N mais recentes
        recentes = feedbacks[-n:] if feedbacks else []
        if not recentes:
            return ""
        return "\n\n## Feedbacks recentes (aprender com estes casos)\n\n" + "\n\n---\n\n".join(recentes)
    except Exception as exc:
        logger.warning("llm_agente1: não foi possível carregar feedbacks — %s", exc)
        return ""


def _montar_user_message(ticket: dict, contrato: dict, slack_thread: list) -> str:
    """
    Monta a mensagem do usuário com todos os dados de entrada formatados.
    """
    partes = []

    # Ticket Jira
    partes.append("## TICKET JIRA")
    partes.append(f"ID: {ticket.get('key', 'desconhecido')}")
    partes.append(f"Resumo: {ticket.get('summary', '')}")
    partes.append(f"Descrição:\n{ticket.get('description', '(sem descrição)')}")

    campos_extras = {k: v for k, v in ticket.items()
                     if k not in ('key', 'summary', 'description', 'anexos')}
    if campos_extras:
        partes.append(f"Campos customizados: {json.dumps(campos_extras, ensure_ascii=False, indent=2, default=str)}")

    if ticket.get('anexos'):
        partes.append(f"Anexos declarados: {', '.join(str(a) for a in ticket['anexos'])}")

    # Thread Slack
    if slack_thread:
        partes.append("\n## THREAD SLACK")
        for msg in slack_thread:
            ts = msg.get('ts', '')
            user = msg.get('username', msg.get('user', 'desconhecido'))
            text = msg.get('text', '')
            partes.append(f"[{ts}] {user}: {text}")

    # Contrato
    if contrato and contrato.get('fonte') != 'mock':
        partes.append("\n## CONTRATO ANEXO")
        partes.append(json.dumps(contrato, ensure_ascii=False, indent=2, default=str))
    else:
        partes.append("\n## CONTRATO ANEXO")
        partes.append("(Contrato não disponível ou não localizado nos anexos)")

    return "\n\n".join(partes)


def executar(
    ticket: dict,
    contrato: dict,
    slack_thread: list | None = None,
) -> dict:
    """
    Executa o Agente 1 — Leitor-Extrator.

    Args:
        ticket: dict do ticket Jira normalizado
        contrato: dict do contrato anexo (pode ser vazio)
        slack_thread: lista de mensagens da thread Slack

    Returns:
        dict com resultado estruturado (campos, confiança, fontes, pendentes)
        ou erro se a chamada LLM falhou
    """
    system_prompt = _carregar_prompt()
    feedbacks = _carregar_feedbacks_relevantes()
    if feedbacks:
        system_prompt += feedbacks

    user_message = _montar_user_message(ticket, contrato, slack_thread or [])

    logger.info("llm_agente1: iniciando extração para %s", ticket.get('key', '?'))

    llm_cfg = json.loads(Path(__file__).parent.parent.joinpath("config.json").read_text())
    agent_id = llm_cfg.get("llm", {}).get("agente1_id")
    resposta = chamar_llm(
        system_prompt=system_prompt,
        user_message=user_message,
        agent_id=agent_id,
    )

    if resposta.get("erro"):
        logger.error("llm_agente1: falha na chamada LLM — %s", resposta["erro"])
        return {
            "agente": "leitor_extrator",
            "ticket_id": ticket.get("key", ""),
            "erro": resposta["erro"],
            "campos": {},
            "campos_pendentes": [],
            "modulos_detectados": [],
            "tokens_input": 0,
            "tokens_output": 0,
        }

    try:
        resultado = json.loads(resposta["content"])
        resultado["tokens_input"] = resposta.get("tokens_input", 0)
        resultado["tokens_output"] = resposta.get("tokens_output", 0)
        resultado["duracao_ms"] = resposta.get("duracao_ms", 0)
        logger.info(
            "llm_agente1: extração concluída — %d campos, %d pendentes",
            len(resultado.get("campos", {})),
            len(resultado.get("campos_pendentes", []))
        )
        return resultado
    except (json.JSONDecodeError, KeyError) as exc:
        logger.error(
            "llm_agente1: resposta inválida — %s\nConteúdo: %s",
            exc, resposta.get("content", "")[:300]
        )
        return {
            "agente": "leitor_extrator",
            "ticket_id": ticket.get("key", ""),
            "erro": f"Resposta LLM inválida: {exc}",
            "campos": {},
            "campos_pendentes": [],
            "modulos_detectados": [],
        }
