"""
llm_agente2.py
==============
Agente 2: Montador-Validador — valida dados e monta o aditamento via LLM.

Responsabilidades:
  - Receber saída do Agente 1
  - Validar contra as 10 regras do DECISION_LAYER
  - Selecionar módulos aplicáveis
  - Gerar texto customizado para casos não-padrão
  - Calcular score de confiança
  - Retornar campos finais + textos para substituição no template
"""

import json
import logging
from pathlib import Path

from .llm_client import chamar_llm

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
PROMPT_PATH = BASE_DIR / "skills" / "layers" / "PROMPT_AGENTE2_MONTADOR.md"
AUDIT_CSV_PATH = BASE_DIR / "data" / "audit" / "DECISION_AUDIT.csv"
FEEDBACK_PATH = BASE_DIR / "skills" / "layers" / "FEEDBACK.md"


def _carregar_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _carregar_historico_relevante(produto: str, n: int = 5) -> str:
    """
    Carrega casos similares bem-sucedidos do DECISION_AUDIT.csv.
    Injetados como few-shot examples no prompt.
    """
    try:
        import csv
        with open(AUDIT_CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [r for r in reader if r.get("status_final") in ("sucesso", "aprovado", "autonomo")]

        # Filtrar por produto/módulo similar
        similares = [r for r in rows if produto.lower() in r.get("produto", "").lower()]
        if not similares:
            similares = rows  # fallback: qualquer caso bem-sucedido

        recentes = similares[-n:]
        if not recentes:
            return ""

        linhas = ["## Casos similares bem-sucedidos (referência)"]
        for r in recentes:
            linhas.append(
                f"- {r.get('ticket_jira')} | {r.get('empresa')} | {r.get('modulos_aplicados')} "
                f"| Score: {r.get('score_confianca')} | {r.get('feedback', '')}"
            )
        return "\n".join(linhas)
    except Exception as exc:
        logger.warning("llm_agente2: não foi possível carregar histórico — %s", exc)
        return ""


def _montar_user_message(saida_agente1: dict, historico: str) -> str:
    """Monta mensagem do usuário para o Agente 2."""
    partes = []

    partes.append("## DADOS EXTRAÍDOS PELO AGENTE 1")
    partes.append(json.dumps(saida_agente1, ensure_ascii=False, indent=2, default=str))

    if historico:
        partes.append(f"\n{historico}")

    partes.append("\n## INSTRUÇÃO")
    partes.append(
        "Processe os dados acima seguindo o sistema prompt. "
        "Valide todas as 10 regras, selecione os módulos, gere textos customizados "
        "quando necessário e calcule o score. Retorne JSON estruturado."
    )

    return "\n\n".join(partes)


def executar(saida_agente1: dict) -> dict:
    """
    Executa o Agente 2 — Montador-Validador.

    Args:
        saida_agente1: dict retornado por llm_agente1.executar()

    Returns:
        dict com módulos selecionados, validações, score, campos finais e textos customizados
    """
    system_prompt = _carregar_prompt()

    # Carregar histórico baseado nos módulos detectados
    modulos = saida_agente1.get("modulos_detectados", [])
    produto = modulos[0] if modulos else ""
    historico = _carregar_historico_relevante(produto)
    if historico:
        system_prompt += "\n\n" + historico

    # Carregar feedbacks
    try:
        feedback_text = FEEDBACK_PATH.read_text(encoding="utf-8")
        if "FEEDBACK-" in feedback_text:
            system_prompt += "\n\n## Aprendizados do feedback jurídico\n" + feedback_text
    except Exception:
        pass

    user_message = _montar_user_message(saida_agente1, historico)

    logger.info(
        "llm_agente2: iniciando validação/montagem para %s",
        saida_agente1.get("ticket_id", "?")
    )

    llm_cfg = json.loads(Path(__file__).parent.parent.joinpath("config.json").read_text())
    agent_id = llm_cfg.get("llm", {}).get("agente2_id")
    resposta = chamar_llm(
        system_prompt=system_prompt,
        user_message=user_message,
        agent_id=agent_id,
    )

    if resposta.get("erro"):
        logger.error("llm_agente2: falha na chamada LLM — %s", resposta["erro"])
        return {
            "agente": "montador_validador",
            "ticket_id": saida_agente1.get("ticket_id", ""),
            "erro": resposta["erro"],
            "modulos": {},
            "validacoes": {},
            "score": {"score_final": 0.0, "decisao": "REVISAO_HUMANA"},
            "campos_finais": {},
            "textos_customizados": [],
        }

    try:
        resultado = json.loads(resposta["content"])
        resultado["tokens_input"] = resposta.get("tokens_input", 0)
        resultado["tokens_output"] = resposta.get("tokens_output", 0)
        resultado["duracao_ms"] = resposta.get("duracao_ms", 0)
        score_final = resultado.get("score", {}).get("score_final", 0.0)
        decisao = resultado.get("score", {}).get("decisao", "REVISAO_HUMANA")
        logger.info(
            "llm_agente2: montagem concluída — score=%.2f decisao=%s módulos=%s",
            score_final, decisao, list(resultado.get("modulos", {}).keys())
        )
        return resultado
    except (json.JSONDecodeError, KeyError) as exc:
        logger.error("llm_agente2: resposta inválida — %s", exc)
        return {
            "agente": "montador_validador",
            "ticket_id": saida_agente1.get("ticket_id", ""),
            "erro": f"Resposta LLM inválida: {exc}",
            "score": {"score_final": 0.0, "decisao": "REVISAO_HUMANA"},
        }
