"""
audit_logger.py — Registro estruturado de decisões de ambos os agentes LLM.

Dois níveis de audit:
  1. DECISION_AUDIT.csv — resumo por execução (já existe)
  2. data/audit/agentes/{ticket_id}_leitor_extrator.json — reasoning do Agente 1 (Leitor-Extrator)
  3. data/audit/agentes/{ticket_id}_montador_validador.json — reasoning do Agente 2 (Montador-Validador)

Criado em 2026-07-12 — Task 28e0969b-1568-4efa-b32d-cae63011f295.
"""

import json
import csv
import logging
import copy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent.parent
AUDIT_CSV_PATH = BASE_DIR / "data" / "audit" / "DECISION_AUDIT.csv"
AUDIT_AGENTES_DIR = BASE_DIR / "data" / "audit" / "agentes"

# ---------------------------------------------------------------------------
# Schema do log Agente 1 (Leitor-Extrator)
# ---------------------------------------------------------------------------

SCHEMA_AGENTE1: Dict[str, Any] = {
    "agent": "leitor_extrator",
    "versao": "1.0",
    "timestamp": "",
    "ticket_id": "",
    "fontes_lidas": [],
    "campos": {},
    "campos_pendentes": [],
    "perguntas_geradas": [],
    "duracao_ms": 0,
    "tokens_input": 0,
    "tokens_output": 0,
}

# ---------------------------------------------------------------------------
# Schema do log Agente 2 (Montador-Validador)
# ---------------------------------------------------------------------------

SCHEMA_AGENTE2: Dict[str, Any] = {
    "agent": "montador_validador",
    "versao": "1.0",
    "timestamp": "",
    "ticket_id": "",
    "modulos": {},
    "validacoes": {},
    "score": {
        "completude_dados":    {"valor": 0.0, "peso": 0.35, "contribuicao": 0.0, "detalhes": ""},
        "match_historico":   {"valor": 0.0, "peso": 0.20, "contribuicao": 0.0, "detalhes": ""},
        "conformidade_regras": {"valor": 0.0, "peso": 0.20, "contribuicao": 0.0, "detalhes": ""},
        "clareza_pedido":     {"valor": 0.0, "peso": 0.15, "contribuicao": 0.0, "detalhes": ""},
        "modulos_conhecidos": {"valor": 0.0, "peso": 0.10, "contribuicao": 0.0, "detalhes": ""},
        "score_final": 0.0,
        "decisao": "REVISAO_HUMANA",
        "justificativa": "",
    },
    "textos_customizados": [],
    "duracao_ms": 0,
    "tokens_input": 0,
    "tokens_output": 0,
}

# ---------------------------------------------------------------------------
# Funções de registro
# ---------------------------------------------------------------------------


def _slug_ticket(ticket_id: str) -> str:
    """Normaliza ticket_id para uso em nomes de arquivo."""
    return ticket_id.replace("/", "-").replace(":", "-")


def registrar_audit_agente(
    ticket_id: str,
    schema: Dict[str, Any],
    dados: Dict[str, Any],
) -> Path:
    """
    Salva o log de um agente em JSON estruturado.

    Args:
        ticket_id: ID do ticket (ex: "JURFIN-5504" ou "MOCK-001")
        schema: SCHEMA_AGENTE1 ou SCHEMA_AGENTE2
        dados: dict com os dados do agente para preencher o schema

    Returns:
        Path do arquivo criado
    """
    AUDIT_AGENTES_DIR.mkdir(parents=True, exist_ok=True)

    log = copy.deepcopy(schema)
    log.update(dados)
    log["timestamp"] = datetime.now().isoformat(timespec="seconds")
    log["ticket_id"] = ticket_id

    agente = log["agent"]
    slug = _slug_ticket(ticket_id)
    path = AUDIT_AGENTES_DIR / f"{slug}_{agente}.json"

    path.write_text(
        json.dumps(log, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    logger.info("audit_logger: log do %s salvo em %s", agente, path)
    return path


def atualizar_audit_csv_com_agentes(
    ticket_id: str,
    path_agente1: Optional[Path],
    path_agente2: Optional[Path],
) -> None:
    """
    Adiciona colunas de referência aos logs dos agentes no DECISION_AUDIT.csv.
    Atualiza a última linha que corresponde ao ticket_id.
    """
    if not AUDIT_CSV_PATH.exists():
        logger.warning("audit_logger: DECISION_AUDIT.csv não existe — ignorando update")
        return

    rows: List[Dict[str, str]] = []
    fieldnames: List[str] = []

    with open(AUDIT_CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        rows = list(reader)

    # Adicionar colunas de referência se não existirem
    extra_cols = ["log_agente1_path", "log_agente2_path"]
    for col in extra_cols:
        if col not in fieldnames:
            fieldnames.append(col)

    # Atualizar última linha do ticket
    for i in range(len(rows) - 1, -1, -1):
        if rows[i].get("ticket_jira") == ticket_id:
            rows[i]["log_agente1_path"] = str(path_agente1) if path_agente1 else ""
            rows[i]["log_agente2_path"] = str(path_agente2) if path_agente2 else ""
            break

    with open(AUDIT_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    logger.info(
        "audit_logger: DECISION_AUDIT.csv atualizado com referências dos agentes para %s",
        ticket_id,
    )


# ---------------------------------------------------------------------------
# Construtores de log a partir dos dados do pipeline
# ---------------------------------------------------------------------------


def construir_log_agente1(ticket: Dict[str, Any]) -> Dict[str, Any]:
    """
    Constrói o dict de dados do Agente 1 (Leitor-Extrator) a partir do ticket lido.

    Mapeia os campos do ticket para o schema SCHEMA_AGENTE1 com confiança,
    fonte, evidência e decisão por campo.
    """
    log = copy.deepcopy(SCHEMA_AGENTE1)

    # Fontes lidas pelo Agente 1
    fontes: List[str] = []
    if ticket.get("key"):
        fontes.append(f"Jira ticket {ticket['key']}")
    if ticket.get("slack_ts"):
        fontes.append("Slack thread")
    if ticket.get("anexos"):
        fontes.append(f"Anexos do ticket: {len(ticket.get('anexos', []))} arquivo(s)")
    log["fontes_lidas"] = fontes

    # Campos extraídos
    campos_extraidos: Dict[str, Any] = {}

    # Campos globais
    campos_ticket = [
        ("RAZAO_SOCIAL",        ticket.get("empresa_contratante") or ticket.get("empresa"),         "ticket"),
        ("CNPJ_EMPRESA",       ticket.get("cnpj_empresa"),                                           "ticket"),
        ("ENDERECO_EMPRESA",   ticket.get("endereco"),                                               "ticket"),
        ("CEP_EMPRESA",        ticket.get("cep"),                                                    "ticket"),
        ("DATA_CONTRATO_ORIGINAL", ticket.get("data_contrato_original"),                             "ticket"),
        ("DATA_ADITIVO",       ticket.get("data_aditivo") or ticket.get("data_assinatura"),           "ticket"),
        ("REPRESENTANTE_LEGAL", ticket.get("representante_legal"),                                   "ticket"),
        ("CPF_REPRESENTANTE",  ticket.get("cpf_representante"),                                      "ticket"),
        ("NUMERO_CONTRATO",    ticket.get("numero_contrato"),                                        "ticket"),
        ("NOME_REPRESENTANTE_IFOOD", ticket.get("nome_representante_ifood"),                        "ticket"),
        ("CARGO_REPRESENTANTE_IFOOD", ticket.get("cargo_representante_ifood"),                       "ticket"),
        ("CIDADE_ASSINATURA",  ticket.get("cidade_assinatura") or "Osasco",                          "ticket"),
    ]

    for campo, valor, fonte in campos_ticket:
        if valor:
            campos_extraidos[campo] = {
                "valor": str(valor),
                "confianca": 1.0,
                "fonte": fonte,
                "evidencia": f"Extraído do campo {campo} do ticket",
                "decisao": "Valor presente no ticket — extração direta",
                "status": "preenchido",
            }
        else:
            campos_extraidos[campo] = {
                "valor": "",
                "confianca": 0.0,
                "fonte": "ticket",
                "evidencia": "",
                "decisao": f"Campo {campo} não encontrado no ticket",
                "status": "pendente",
            }

    # Campos ISA (se módulo 10 solicitado)
    if ticket.get("modulos_solicitados") and 10 in ticket.get("modulos_solicitados", []):
        isa_campos = [
            ("VALOR_ISA_MENSAL",       ticket.get("valor_isa_mensal")),
            ("PERIODICIDADE_ISA",      ticket.get("periodicidade_isa")),
            ("ISA_CUMULATIVO",         ticket.get("isa_cumulativo")),
            ("DATA_INICIO_ISA",        ticket.get("data_inicio_isa")),
            ("FORMA_PAGAMENTO_ISA",    ticket.get("forma_pagamento_isa")),
            ("PROPOSTA_COMERCIAL_ISA", ticket.get("proposta_comercial_isa")),
        ]
        for campo, valor in isa_campos:
            if valor:
                campos_extraidos[campo] = {
                    "valor": str(valor),
                    "confianca": 1.0,
                    "fonte": "ticket",
                    "evidencia": f"Extraído do campo {campo} do ticket (módulo ISA)",
                    "decisao": "Valor presente no ticket — extração direta",
                    "status": "preenchido",
                }
            else:
                campos_extraidos[campo] = {
                    "valor": "",
                    "confianca": 0.0,
                    "fonte": "ticket",
                    "evidencia": "",
                    "decisao": f"Campo {campo} não encontrado no ticket",
                    "status": "pendente",
                }

    log["campos"] = campos_extraidos
    log["campos_pendentes"] = [
        c for c, v in campos_extraidos.items() if v["status"] == "pendente"
    ]

    # Perguntas geradas para o advogado (a partir dos campos pendentes)
    log["perguntas_geradas"] = [
        f"Por favor, informe o campo {campo} para prosseguir com o aditamento."
        for campo in log["campos_pendentes"]
    ]

    return log


def construir_log_agente2(
    ticket: Dict[str, Any],
    montagem: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Constrói o dict de dados do Agente 2 (Montador-Validador) a partir
    do ticket e do resultado de montar_aditamento().

    A estrutura real de score retornada por calcular_score() é:
        {
            "score": float,
            "decisao": "AUTONOMO" | "REVISAO_HUMANA",
            "threshold": float,
            "detalhamento": {
                "completude_dados": float,
                "match_historico": float,
                "conformidade_regras": float,
                "clareza_pedido": float,
                "modulos_conhecidos": float,
            },
            "campos_pendentes": [...],
            "regras_violadas": [...],
            "justificativa": str,
        }
    """
    log = copy.deepcopy(SCHEMA_AGENTE2)

    # Módulos selecionados
    modulos_selecionados = montagem.get("modulos_selecionados", [])
    modulos_log: Dict[str, Any] = {}

    for m in modulos_selecionados:
        modulos_log[m] = {
            "selecionado": True,
            "razao": (
                f"Módulo {m} selecionado pelo Agente 2 com base no ticket "
                f"e DECISION_MAP — ticket: {ticket.get('key', 'N/A')}"
            ),
            "regras_verificadas": [],
            "tipo_geracao": "padrao",
            "customizacao_razao": "",
        }

    log["modulos"] = modulos_log

    # Validações (regras do DECISION_LAYER)
    regras_violadas = set(montagem.get("regras_violadas", []))
    validacoes: Dict[str, Any] = {}

    regras_map = {
        "REGRA-01": "ISA exige Proposta Comercial",
        "REGRA-02": "Saldo Natal — cláusula de responsabilidade do cliente",
        "REGRA-03": "Aviso prévio — consistência numérica",
        "REGRA-04": "Terminologia canônica",
        "REGRA-05": "Duplo aditamento ISA + Saldo Natal — documento consolidado",
        "REGRA-06": "Exclusão mútua de módulos",
        "REGRA-07": "Campos obrigatórios globais",
        "REGRA-08": "Produto não mapeado no catálogo",
        "REGRA-09": "CNPJ válido",
        "REGRA-10": "Colab+ exige confirmação no contrato",
    }

    for regra, desc in regras_map.items():
        if regra in regras_violadas:
            validacoes[regra] = {
                "status": "violada",
                "detalhes": desc,
                "acao": f"Campo(s) pendente(s) adicionado(s) à lista de campos pendentes",
            }
        else:
            validacoes[regra] = {
                "status": "ok",
                "detalhes": desc,
                "acao": "",
            }

    log["validacoes"] = validacoes

    # Score detalhado — mapear estrutura real do calcular_score()
    score_raw = montagem.get("score", {})
    detalhamento = score_raw.get("detalhamento", {}) if isinstance(score_raw, dict) else {}

    # Pesos fixos (devem coincidir com score_engine.py)
    PESOS: Dict[str, float] = {
        "completude_dados": 0.35,
        "match_historico": 0.20,
        "conformidade_regras": 0.20,
        "clareza_pedido": 0.15,
        "modulos_conhecidos": 0.10,
    }

    score_score = score_raw.get("score", 0.0) if isinstance(score_raw, dict) else float(score_raw or 0.0)
    score_decisao = score_raw.get("decisao", "REVISAO_HUMANA") if isinstance(score_raw, dict) else "REVISAO_HUMANA"
    score_justificativa = score_raw.get("justificativa", "") if isinstance(score_raw, dict) else ""

    for fator, peso in PESOS.items():
        val = detalhamento.get(fator, 0.0)
        log["score"][fator] = {
            "valor": val,
            "peso": peso,
            "contribuicao": round(val * peso, 4),
            "detalhes": f"Valor={val:.4f} × peso={peso} = {val*peso:.4f}",
        }

    log["score"]["score_final"] = round(score_score, 4)
    log["score"]["decisao"] = score_decisao
    log["score"]["justificativa"] = score_justificativa

    # Textos customizados (se houver terminologia corrigida)
    terminologia = montagem.get("terminologia_corrigida", [])
    if terminologia:
        log["textos_customizados"] = [
            {
                "tipo": "terminologia_canonica",
                "correcoes": terminologia,
            }
        ]

    return log


def registrar_audit_agentes(
    ticket_id: str,
    ticket: Dict[str, Any],
    montagem: Dict[str, Any],
) -> tuple:
    """
    Função de alto nível — registra o audit de ambos os agentes.

    Args:
        ticket_id: ID do ticket (ex: "JURFIN-5504")
        ticket: dados do ticket lido (Agente 1 output)
        montagem: resultado de montar_aditamento() (Agente 2 output)

    Returns:
        tuple: (path_agente1, path_agente2)
    """
    # Agente 1
    dados_a1 = construir_log_agente1(ticket)
    path_a1 = registrar_audit_agente(ticket_id, SCHEMA_AGENTE1, dados_a1)

    # Agente 2
    dados_a2 = construir_log_agente2(ticket, montagem)
    path_a2 = registrar_audit_agente(ticket_id, SCHEMA_AGENTE2, dados_a2)

    # Atualizar CSV com referências
    atualizar_audit_csv_com_agentes(ticket_id, path_a1, path_a2)

    logger.info(
        "audit_logger: audit completo registrado para %s — Agente1=%s Agente2=%s",
        ticket_id,
        path_a1.name,
        path_a2.name,
    )

    return path_a1, path_a2
