"""
llm_client.py
=============
Cliente LLM para o pipeline 15-aditamentos.
Provider: Toqan (https://api.toqan.ai) — mesmo padrão do monitor BCB.

Fluxo:
  1. POST /create_conversation com user_message = system_prompt + separador + user_message
  2. Poll GET /get_answer a cada 3s até 'answer' retornar
  3. Retornar answer como string

O proxy do Toqan injeta as credenciais automaticamente.
Não é necessário configurar API key ou Authorization header.
"""

import json
import logging
import time
import warnings
from pathlib import Path
from typing import Optional

import re
import requests

logger = logging.getLogger(__name__)

def _extrair_json(texto: str) -> str:
    """
    Extrai JSON puro de uma resposta que pode estar envolvida em markdown.
    Remove blocos ```json ... ``` e ``` ... ```.
    """
    if not texto:
        return texto
    # Remover bloco ```json ... ``` ou ``` ... ```
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', texto, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Tentar extrair JSON direto (começa com { ou [)
    texto_strip = texto.strip()
    if texto_strip.startswith('{') or texto_strip.startswith('['):
        return texto_strip
    return texto



BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / "config.json"

# Endpoints Toqan
TOQAN_CREATE_URL = "https://api.toqan.ai/api/create_conversation"
TOQAN_POLL_URL   = "https://api.toqan.ai/api/get_answer"

# Defaults
DEFAULT_TIMEOUT  = 120   # segundos de espera máxima pelo Toqan
DEFAULT_INTERVAL = 3     # segundos entre polls


def _load_llm_config() -> dict:
    """Carrega configuração LLM do config.json."""
    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return cfg.get("llm", {})
    except Exception:
        return {}


def _montar_prompt_completo(system_prompt: str, user_message: str) -> str:
    """
    Concatena system_prompt + user_message em uma única string.
    O Toqan não usa roles separados — tudo vai em user_message.
    """
    separador = "\n\n" + "=" * 60 + "\n## DADOS PARA PROCESSAR:\n" + "=" * 60 + "\n\n"
    instrucao_json = "\n\n" + "=" * 60 + "\nRetorne EXCLUSIVAMENTE um objeto JSON válido, sem texto adicional antes ou depois.\n" + "=" * 60
    return system_prompt + separador + user_message + instrucao_json


def _chamar_toqan(prompt_completo: str, agent_id: Optional[str] = None,
                  timeout: int = DEFAULT_TIMEOUT) -> Optional[str]:
    """
    Envia o prompt ao Toqan e aguarda a resposta via polling.
    Implementação idêntica à do monitor BCB (analise_llm_v3.py).

    Returns:
        Texto da resposta ou None em caso de falha.
    """
    payload = {"user_message": prompt_completo}
    if agent_id:
        payload["agent_id"] = agent_id

    # 1. Criar conversa
    try:
        r = requests.post(TOQAN_CREATE_URL, json=payload, timeout=30)
    except Exception as exc:
        logger.error("llm_client: erro ao criar conversa Toqan — %s", exc)
        return None

    if r.status_code in (401, 403):
        logger.error("llm_client: credencial Toqan não configurada no proxy (HTTP %d)", r.status_code)
        return None

    if r.status_code != 200:
        logger.error("llm_client: create_conversation HTTP %d — %s", r.status_code, r.text[:200])
        return None

    try:
        data = r.json()
        request_id      = data.get("request_id")
        conversation_id = data.get("conversation_id")
        if not request_id or not conversation_id:
            logger.error("llm_client: create_conversation sem request_id/conversation_id — %s", data)
            return None
    except Exception as exc:
        logger.error("llm_client: resposta create_conversation inválida — %s", exc)
        return None

    # 2. Polling
    elapsed  = 0
    interval = DEFAULT_INTERVAL

    while elapsed < timeout:
        time.sleep(interval)
        elapsed += interval

        try:
            rp = requests.get(
                TOQAN_POLL_URL,
                json={"request_id": request_id, "conversation_id": conversation_id},
                timeout=15,
            )
        except Exception:
            continue

        if rp.status_code != 200:
            continue

        try:
            poll_data = rp.json()
        except Exception:
            continue

        status = poll_data.get("status", "")
        answer = poll_data.get("answer")

        # Resposta direta no campo 'answer'
        if answer and isinstance(answer, str) and len(answer) > 0:
            return answer.strip()

        # Tentar campos alternativos
        for campo in ["response", "content", "text", "message", "output", "result"]:
            if campo in poll_data and poll_data[campo]:
                valor = poll_data[campo]
                if isinstance(valor, str) and len(valor) > 10:
                    return valor.strip()
                elif isinstance(valor, dict):
                    for subcampo in ["text", "content", "message"]:
                        if subcampo in valor and valor[subcampo]:
                            return str(valor[subcampo]).strip()

        # Aguardar se ainda processando
        if status in ("in_progress", "pending", "processing", "running", ""):
            continue

        # Erro fatal
        if status in ("error", "failed", "cancelled"):
            logger.error("llm_client: Toqan retornou status=%s", status)
            return None

        # Status desconhecido — logar e continuar
        if poll_data:
            warnings.warn(
                f"Toqan get_answer status={status} keys={list(poll_data.keys())} data={str(poll_data)[:200]}"
            )

    logger.error("llm_client: timeout após %ds aguardando Toqan", timeout)
    return None


def chamar_llm(
    system_prompt: str,
    user_message: str,
    timeout: int | None = None,
    agent_id: str | None = None,
    **kwargs,  # ignorar model/temperature/max_tokens — controlados pelo Toqan
) -> dict:
    """
    Chama o Toqan com system_prompt e user_message.
    O proxy injeta as credenciais automaticamente.

    Args:
        system_prompt: Instruções do sistema (prompt do agente)
        user_message:  Dados de entrada para o agente processar
        timeout:       Timeout em segundos (padrão: config.json ou 120)
        agent_id:      ID do agente Toqan (opcional — usa o padrão da conta se omitido)

    Returns:
        dict com:
            - content:       texto da resposta (str) ou None
            - tokens_input:  0 (Toqan não reporta tokens)
            - tokens_output: 0
            - model_used:    "toqan"
            - duracao_ms:    tempo de resposta em ms
            - erro:          None se ok, mensagem de erro se falhou
    """
    llm_cfg = _load_llm_config()
    _timeout  = timeout or llm_cfg.get("timeout", DEFAULT_TIMEOUT)
    _agent_id = agent_id or llm_cfg.get("toqan_agent_id")

    prompt_completo = _montar_prompt_completo(system_prompt, user_message)

    logger.info("llm_client: chamando Toqan (timeout=%ds agent_id=%s)", _timeout, _agent_id or "padrão")

    t0 = time.time()
    answer = _chamar_toqan(prompt_completo, agent_id=_agent_id, timeout=_timeout)
    duracao_ms = int((time.time() - t0) * 1000)

    if answer is None:
        return {
            "content":       None,
            "tokens_input":  0,
            "tokens_output": 0,
            "model_used":    "toqan",
            "duracao_ms":    duracao_ms,
            "erro":          "Toqan não retornou resposta (timeout ou erro de credencial)",
        }

    logger.info("llm_client: Toqan respondeu em %dms (%d chars)", duracao_ms, len(answer))

    answer_clean = _extrair_json(answer)
    return {
        "content":       answer_clean,
        "tokens_input":  0,
        "tokens_output": 0,
        "model_used":    "toqan",
        "duracao_ms":    duracao_ms,
        "erro":          None,
    }
