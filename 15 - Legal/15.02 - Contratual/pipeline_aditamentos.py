#!/usr/bin/env python3
"""
pipeline_aditamentos.py
=======================
Orquestrador principal do app 15-aditamentos — iFood Benefícios.

Uso:
    python3 pipeline_aditamentos.py --ticket JURFIN-1234
    python3 pipeline_aditamentos.py --ticket MOCK-001 --dry-run

Fluxo:
    1. jira_reader.ler_ticket(ticket_id)
    2. jira_reader.eh_aditamento_ifb(ticket)  — ignora se False
    3. contract_reader.ler_contrato_anexo()  — lê contrato anexo (PDF/Word)
    4. amendment_assembler.montar_aditamento(ticket, contrato, {})
    5. Se não dry-run: doc_generator → adicionar_link_doc_jira → slack_notifier → tracking file
    6. registrar_audit() em DECISION_AUDIT.csv
    7. Imprimir resultado

Em dry-run: imprime aditamento montado + score + pendentes sem chamar APIs externas,
           mas cria o tracking file para validação do fluxo pós-revisão.

Threshold autônomo: score >= 0.90 (zero campos PENDENTES)
"""

import argparse
import csv
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from modules.audit_logger import registrar_audit_agentes

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
AUDIT_PATH = BASE_DIR / "data" / "audit" / "DECISION_AUDIT.csv"
TRACKING_DIR = BASE_DIR / "data" / "audit" / "pending_review"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("pipeline_aditamentos")


def load_config(path: Path = CONFIG_PATH) -> dict:
    """Carrega configurações do arquivo config.json."""
    if not path.exists():
        return {
            "jira": {"base_url": "https://ifood.atlassian.net", "project": "JURFIN"},
            "slack": {"canal_aditamentos": "C033DR3282G"},
            "score": {"threshold_autonomo": 0.90},
        }
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Mock de ticket para testes (ticket_id inicia com "MOCK-")
# ---------------------------------------------------------------------------

def _mock_ticket(ticket_id: str) -> dict:
    """Cria ticket ISA completo mock para testes."""
    return {
        "key": ticket_id,
        "ticket_id": ticket_id,
        "titulo": f"[MOCK] Aditamento ISA — Empresa Teste Ltda. [{ticket_id}]",
        "tipo": "Aditivos não padrão",
        "empresa": "iFood Benefícios",
        "empresa_contratante": "Empresa Teste Ltda.",
        "cnpj_empresa": "11.222.333/0001-81",
        "endereco": "Rua das Flores, 100, Centro, São Paulo/SP",
        "cep": "01.001-000",
        "data_contrato_original": "10 de janeiro de 2023",
        "data_aditivo": "10 de julho de 2026",
        "representante_legal": "João da Silva",
        "cpf_representante": "123.456.789-09",
        "numero_contrato": "CTR-2023-001",
        "nome_representante_ifood": "Maria Oliveira",
        "cargo_representante_ifood": "Diretora Jurídica",
        "modulos_solicitados": [10],  # ISA
        "proposta_comercial_isa": "Proposta-ISA-Mock.pdf",
        "valor_isa_mensal": "R$ 150,00",
        "periodicidade_isa": "mensal",
        "isa_cumulativo": "não",
        "data_inicio_isa": "01 de agosto de 2026",
        "forma_pagamento_isa": "crédito em carteira digital",
        "summary": "Solicitação de aditamento ISA para Empresa Teste Ltda.",
        "description": "Inclusão de ISA conforme proposta comercial aprovada.",
        "advogado_responsavel": "Maria Oliveira",
        "status": "Em análise",
        "anexos": [],
    }


def _mock_contrato(ticket: dict) -> dict:
    """Cria contrato mock para testes."""
    return {
        "razao_social": "Empresa Teste Ltda.",
        "cnpj": "11.222.333/0001-81",
        "endereco": "Rua das Flores, 100, Centro, São Paulo/SP",
        "cep": "01.001-000",
        "data_assinatura_original": "10 de janeiro de 2023",
        "aviso_previo_clausula_10_3": 60,
        "tem_colabmais": None,
        "clausulas": {},
        "fonte": "mock",
    }


# ---------------------------------------------------------------------------
# Registro de auditoria
# ---------------------------------------------------------------------------

def registrar_audit(ticket_id: str, resultado: dict) -> None:
    """Registra resultado do processamento no DECISION_AUDIT.csv."""
    try:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        escrever_header = not AUDIT_PATH.exists() or AUDIT_PATH.stat().st_size == 0

        score_val = resultado.get("score", {})
        if isinstance(score_val, dict):
            score = score_val.get("score", 0.0)
            decisao = score_val.get("decisao", "REVISAO_HUMANA")
        else:
            score = float(score_val) if score_val else 0.0
            decisao = "AUTONOMO" if score >= 0.90 else "REVISAO_HUMANA"

        campos_pend = resultado.get("campos_pendentes", [])
        modulos = resultado.get("modulos_selecionados", [])

        linha = {
            "data_hora": datetime.now().isoformat(timespec="seconds"),
            "ticket_jira": ticket_id,
            "empresa": resultado.get("empresa", ""),
            "produto": ", ".join(modulos) if modulos else "",
            "modulos_aplicados": ", ".join(modulos),
            "variaveis_preenchidas": len(resultado.get("variaveis", {})),
            "campos_pendentes": len(campos_pend),
            "score_confianca": round(score, 4),
            "decisao": decisao,
            "advogado_revisor": resultado.get("advogado_responsavel", ""),
            "status_final": "dry_run" if resultado.get("dry_run") else ("sucesso" if score >= 0.90 else "revisao_manual"),
            "feedback": "",
        }

        with open(AUDIT_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(linha.keys()))
            if escrever_header:
                writer.writeheader()
            writer.writerow(linha)

        logger.info("registrar_audit: entrada salva em %s", AUDIT_PATH)
    except Exception as exc:
        logger.error("registrar_audit: erro — %s", exc)


# ---------------------------------------------------------------------------
# Salvar tracking file para pós-revisão
# ---------------------------------------------------------------------------

def salvar_tracking(ticket_id: str, canal: str, slack_ts: str,
                     doc_url: str, doc_nome: str, advogado: str,
                     empresa: str, score: float, decisao: str) -> Path | None:
    """
    Salva arquivo JSON de tracking para acompanhamento pós-revisão.

    Returns:
        Path do arquivo criado ou None em caso de erro.
    """
    try:
        TRACKING_DIR.mkdir(parents=True, exist_ok=True)
        tracking_file = TRACKING_DIR / f"{ticket_id}.json"
        tracking_file.write_text(json.dumps({
            "ticket_id": ticket_id,
            "slack_channel": canal,
            "slack_message_ts": slack_ts,
            "doc_url": doc_url,
            "doc_nome": doc_nome,
            "advogado": advogado,
            "empresa": empresa,
            "score": float(score),
            "decisao": decisao,
            "status": "aguardando_revisao",
            "criado_em": datetime.now().isoformat(timespec="seconds")
        }, ensure_ascii=False, indent=2))
        logger.info("salvar_tracking: arquivo salvo em %s", tracking_file)
        return tracking_file
    except Exception as exc:
        logger.error("salvar_tracking: erro — %s", exc)
        return None


# ---------------------------------------------------------------------------
# Processador principal
# ---------------------------------------------------------------------------

def processar_ticket(ticket_id: str, dry_run: bool = False) -> dict:
    """
    Processa um ticket de aditamento iFood Benefícios.

    Args:
        ticket_id: ID do ticket Jira (ex: "JURFIN-1234" ou "MOCK-001")
        dry_run: Se True, não chama APIs externas (doc/slack/jira)

    Returns:
        dict com resultado completo do processamento
    """
    config = load_config()
    logger.info("Pipeline 15-aditamentos — ticket=%s dry_run=%s", ticket_id, dry_run)
    # -------------------------------------------------------------------------
    # 1. Leitura do ticket Jira (ou mock para MOCK-*)
    # -------------------------------------------------------------------------
    logger.info("[1/7] Lendo ticket Jira...")

    if ticket_id.startswith("MOCK-"):
        ticket = _mock_ticket(ticket_id)
        logger.info("Usando ticket MOCK para teste: %s", ticket_id)
    else:
        from modules.jira_reader import ler_ticket
        ticket_raw = ler_ticket(ticket_id)
        if "erro" in ticket_raw:
            logger.error("Erro ao ler ticket: %s", ticket_raw["erro"])
            return {"status": "erro_jira", "erro": ticket_raw["erro"], "score": 0.0}
        ticket = ticket_raw

    # -------------------------------------------------------------------------
    # 2. Verificar elegibilidade
    # -------------------------------------------------------------------------
    logger.info("[2/7] Verificando elegibilidade do ticket...")

    if not ticket_id.startswith("MOCK-"):
        from modules.jira_reader import eh_aditamento_ifb
        if not eh_aditamento_ifb(ticket):
            logger.info("Ticket %s não é aditamento iFood Benefícios — ignorando.", ticket_id)
            return {
                "status": "nao_elegivel",
                "ticket": ticket_id,
                "motivo": "Não é aditamento iFood Benefícios",
                "score": 0.0,
            }

    # -------------------------------------------------------------------------
    # 3. Leitura do contrato anexo
    # -------------------------------------------------------------------------
    logger.info("[3/7] Lendo contrato anexo...")

    if ticket_id.startswith("MOCK-"):
        contrato = _mock_contrato(ticket)
        logger.info("Usando contrato MOCK para teste")
    else:
        from modules.contract_reader import ler_contrato_anexo
        anexos = ticket.get("anexos", [])
        if anexos:
            contrato = ler_contrato_anexo(anexos[0])
        else:
            logger.warning("Nenhum anexo encontrado no ticket — usando contrato vazio")
            contrato = {}

    # -------------------------------------------------------------------------
    # 4. Montar aditamento
    # -------------------------------------------------------------------------
    logger.info("[4/7] Montando aditamento...")

    from modules.amendment_assembler import montar_aditamento

    # Normalizar campos do ticket para o assembler
    ticket_normalizado = {**ticket}
    if "empresa_contratante" in ticket and "empresa" not in ticket_normalizado:
        ticket_normalizado["empresa"] = ticket["empresa_contratante"]

    analise_leitor = {
        "produtos": ticket.get("produtos", []),
        "alteracoes_solicitadas": ticket.get("alteracoes_solicitadas", []),
    }

    montagem = montar_aditamento(ticket_normalizado, contrato, analise_leitor)

    score_info = montagem.get("score", {})
    score = score_info.get("score", 0.0) if isinstance(score_info, dict) else float(score_info or 0.0)
    decisao = score_info.get("decisao", "REVISAO_HUMANA") if isinstance(score_info, dict) else "REVISAO_HUMANA"
    campos_pendentes = montagem.get("campos_pendentes", [])
    modulos = montagem.get("modulos_selecionados", [])

    logger.info("Score: %.2f (%s) | Campos pendentes: %d | Módulos: %s",
                score, decisao, len(campos_pendentes), modulos)
    # -----------------------------------------------------------------------
    # Audit de agentes — ambos os logs (Agente 1: leitor_extrator / Agente 2: montador_validador)
    # -----------------------------------------------------------------------
    try:
        path_a1, path_a2 = registrar_audit_agentes(ticket_id, ticket, montagem)
        logger.info("Audit agentes: Agente1=%s  Agente2=%s", path_a1.name, path_a2.name)
    except Exception as exc:
        logger.error("Erro no audit de agentes — %s", exc)


    # -------------------------------------------------------------------------
    # Resultado parcial (usado em dry-run)
    # -------------------------------------------------------------------------
    resultado = {
        "ticket": ticket_id,
        "empresa": ticket.get("empresa_contratante") or ticket.get("empresa", ""),
        "advogado_responsavel": ticket.get("advogado_responsavel", ""),
        "score": score_info,
        "decisao": decisao,
        "campos_pendentes": campos_pendentes,
        "modulos_selecionados": modulos,
        "variaveis": montagem.get("variaveis", {}),
        "perguntas_para_advogado": montagem.get("perguntas_para_advogado", []),
        "doc_url": None,
        "dry_run": dry_run,
    }

    if dry_run:
        # -------------------------------------------------------------------------
        # DRY-RUN: Imprimir resultado sem chamar APIs externas
        # -------------------------------------------------------------------------
        logger.info("=== DRY-RUN: Nenhuma API externa será chamada ===")
        resultado["status"] = "dry_run"
        registrar_audit(ticket_id, resultado)

        # Criar tracking file mock para validação do fluxo pós-revisão
        salvar_tracking(
            ticket_id=ticket_id,
            canal=config.get("slack", {}).get("canal_aditamentos", "C033DR3282G"),
            slack_ts="MOCK_TS_0000000000.000000",
            doc_url="https://docs.google.com/mock/MOCK-DOC-ID",
            doc_nome=f"Minuta MOCK — {ticket_id}",
            advogado=ticket.get("advogado_responsavel", ""),
            empresa=resultado["empresa"],
            score=score,
            decisao=decisao,
        )
        logger.info("salvar_tracking: arquivo de tracking criado para dry-run %s", ticket_id)

        return resultado

    # -------------------------------------------------------------------------
    # 5. Gerar documento Google Docs
    # -------------------------------------------------------------------------
    logger.info("[5/7] Gerando documento Google Docs...")

    from modules.doc_generator import gerar_google_doc

    doc_resultado = gerar_google_doc(montagem, ticket_id)
    resultado["doc_id"] = doc_resultado.get("doc_id")
    resultado["doc_url"] = doc_resultado.get("doc_url")
    resultado["doc_nome"] = doc_resultado.get("doc_nome")
    if doc_resultado.get("doc_id"):
        logger.info("Documento gerado: %s", doc_resultado["doc_url"])
    else:
        logger.error("Falha ao gerar documento: %s", doc_resultado.get("erro"))

    # -------------------------------------------------------------------------
    # 5b. Jira: remote link com o Google Doc
    # -------------------------------------------------------------------------
    logger.info("[5b/7] Adicionando remote link do Google Doc no Jira...")

    from modules.jira_updater import adicionar_link_doc_jira

    if doc_resultado.get("doc_id"):
        jira_link_ok = adicionar_link_doc_jira(
            ticket_id,
            doc_resultado.get("doc_url", ""),
            doc_resultado.get("doc_nome", ""),
            score,
            decisao,
        )
        resultado["jira_link_ok"] = jira_link_ok
    else:
        resultado["jira_link_ok"] = False

    # -------------------------------------------------------------------------
    # 6. Notificação Slack + salvar tracking file
    # -------------------------------------------------------------------------
    logger.info("[6/7] Enviando notificação Slack...")

    from modules.slack_notifier import notificar_thread

    canal = config.get("slack", {}).get("canal_aditamentos", "C033DR3282G")
    thread_ts = ticket.get("slack_ts", "")
    resultado_slack = {**montagem, **doc_resultado}
    slack_ok, slack_ts = notificar_thread(canal, thread_ts, resultado_slack)
    resultado["slack_ok"] = slack_ok
    resultado["slack_ts"] = slack_ts

    # Salvar tracking file para pós-revisão
    salvar_tracking(
        ticket_id=ticket_id,
        canal=canal,
        slack_ts=slack_ts,
        doc_url=doc_resultado.get("doc_url", ""),
        doc_nome=doc_resultado.get("doc_nome", ""),
        advogado=ticket.get("advogado_responsavel", ""),
        empresa=resultado["empresa"],
        score=score,
        decisao=decisao,
    )

    # -------------------------------------------------------------------------
    # 7. Atualizar ticket Jira (comentário)
    # -------------------------------------------------------------------------
    logger.info("[7/7] Atualizando ticket Jira...")

    from modules.jira_updater import atualizar_ticket

    jira_ok = atualizar_ticket(ticket_id, {**montagem, **doc_resultado})
    resultado["jira_ok"] = jira_ok

    # -------------------------------------------------------------------------
    # 8. Registrar auditoria
    # -------------------------------------------------------------------------
    resultado["status"] = "concluido" if score >= 0.90 else "revisao_manual"
    registrar_audit(ticket_id, resultado)

    return resultado


# ---------------------------------------------------------------------------
# Entrypoint CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de aditamentos iFood Benefícios"
    )
    parser.add_argument(
        "--ticket",
        help="ID do ticket Jira (ex: JURFIN-1234 ou MOCK-001)",
        required=True,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Não chamar APIs externas — apenas montar e imprimir resultado",
    )
    args = parser.parse_args()

    resultado = processar_ticket(ticket_id=args.ticket, dry_run=args.dry_run)

    if args.dry_run:
        print("\n" + "=" * 60)
        print("DRY-RUN — Resultado do Pipeline")
        print("=" * 60)
        print(f"Ticket:          {resultado['ticket']}")
        print(f"Empresa:         {resultado.get('empresa', '')}")
        print(f"Módulos:         {', '.join(resultado.get('modulos_selecionados', []))}")

        score_info = resultado.get("score", {})
        score = score_info.get("score", 0.0) if isinstance(score_info, dict) else float(score_info or 0)
        decisao = score_info.get("decisao", "REVISAO_HUMANA") if isinstance(score_info, dict) else "REVISAO_HUMANA"

        print(f"Score:           {score:.2f}")
        print(f"Decisão:         {decisao}")

        campos_pend = resultado.get("campos_pendentes", [])
        print(f"Campos pendentes: {len(campos_pend)}")
        for campo in campos_pend:
            print(f"  - {campo}")

        perguntas = resultado.get("perguntas_para_advogado", [])
        if perguntas:
            print("\nPerguntas para advogado:")
            for p in perguntas:
                print(f"  {p}")

        print("=" * 60)
        print("Auditoria registrada em:", AUDIT_PATH)
        print("Tracking file pendente:", TRACKING_DIR / f"{args.ticket}.json")
    else:
        print(json.dumps(resultado, ensure_ascii=False, indent=2, default=str))


# ---------------------------------------------------------------------------
# Compatibilidade com pipeline legado (run_pipeline)
# ---------------------------------------------------------------------------

def run_pipeline(ticket_id=None, dry_run=False) -> dict:
    """Alias para compatibilidade com chamadas legadas."""
    if ticket_id:
        return processar_ticket(ticket_id, dry_run=dry_run)
    return {"status": "sem_tickets", "score": 0.0}


if __name__ == "__main__":
    main()
