"""
tests/test_pipeline_mock.py
===========================
Testes do pipeline completo com ticket ISA mock e dry-run.

Casos de teste:
  1. processar_ticket("MOCK-001", dry_run=True) — ISA completo → score > 0 e módulos
  2. Verificar módulos selecionados incluem 10_isa
  3. Verificar que dry_run não chama APIs externas
  4. Verificar registro de auditoria

Execução:
    cd data/ifb-aditamentos/app
    python -m pytest tests/test_pipeline_mock.py -v
"""

import sys
import os

# Garantir imports do diretório raiz do app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


# ---------------------------------------------------------------------------
# Testes principais
# ---------------------------------------------------------------------------

def test_processar_ticket_mock_dry_run_basico():
    """
    Teste 1: processar_ticket("MOCK-001", dry_run=True)
    - Deve retornar dict com status, score, módulos e campos_pendentes
    - Não deve levantar exceção
    """
    from pipeline_aditamentos import processar_ticket

    resultado = processar_ticket("MOCK-001", dry_run=True)

    assert isinstance(resultado, dict), "Resultado deve ser dict"
    assert resultado.get("ticket") == "MOCK-001", "ticket_id deve ser MOCK-001"
    assert resultado.get("dry_run") is True, "dry_run deve ser True"
    assert "modulos_selecionados" in resultado, "Deve conter modulos_selecionados"
    assert "campos_pendentes" in resultado, "Deve conter campos_pendentes"
    assert "score" in resultado, "Deve conter score"


def test_processar_ticket_mock_inclui_isa():
    """
    Teste 2: Ticket ISA completo (MOCK-001) deve incluir módulo 10_isa.
    """
    from pipeline_aditamentos import processar_ticket

    resultado = processar_ticket("MOCK-001", dry_run=True)

    modulos = resultado.get("modulos_selecionados", [])
    assert "10_isa" in modulos, f"Módulo ISA deve estar nos módulos. Módulos: {modulos}"


def test_processar_ticket_mock_score_positivo():
    """
    Teste 3: ISA com todos os campos preenchidos deve ter score > 0.
    """
    from pipeline_aditamentos import processar_ticket

    resultado = processar_ticket("MOCK-001", dry_run=True)

    score_info = resultado.get("score", {})
    if isinstance(score_info, dict):
        score = score_info.get("score", 0.0)
    else:
        score = float(score_info or 0.0)

    assert score >= 0.0, "Score deve ser >= 0.0"
    # ISA completo com todos os campos preenchidos → score deve ser alto
    assert score > 0.0, f"Score deve ser positivo para ticket ISA completo: score={score}"


def test_processar_ticket_mock_modulos_fixos():
    """
    Teste 4: Módulos fixos (cabecalho, rodape, clausula_geral) sempre presentes.
    """
    from pipeline_aditamentos import processar_ticket

    resultado = processar_ticket("MOCK-001", dry_run=True)

    modulos = resultado.get("modulos_selecionados", [])
    assert "01_cabecalho" in modulos, f"Módulo cabecalho deve estar presente. Módulos: {modulos}"
    assert "08_rodape_assinaturas" in modulos, f"Módulo rodape deve estar presente. Módulos: {modulos}"
    assert "09_clausula_geral" in modulos, f"Módulo clausula_geral deve estar presente. Módulos: {modulos}"


def test_processar_ticket_mock_sem_chamadas_externas():
    """
    Teste 5: Em dry_run=True, o pipeline não deve tentar chamar APIs externas
    (doc_generator, slack_notifier, jira_updater).
    Verificado indiretamente pela ausência de doc_url no resultado.
    """
    from pipeline_aditamentos import processar_ticket

    resultado = processar_ticket("MOCK-001", dry_run=True)

    # Em dry-run, doc_url deve ser None (não tentou gerar documento)
    assert resultado.get("doc_url") is None, "Em dry-run, doc_url deve ser None"
    assert resultado.get("status") == "dry_run", "Status deve ser dry_run"


def test_processar_ticket_mock_campos_preenchidos():
    """
    Teste 6: Variaveis do ticket MOCK-001 devem conter campos básicos preenchidos.
    """
    from pipeline_aditamentos import processar_ticket

    resultado = processar_ticket("MOCK-001", dry_run=True)

    variaveis = resultado.get("variaveis", {})
    assert len(variaveis) > 0, "Variáveis devem estar preenchidas"

    # RAZAO_SOCIAL deve estar presente e não PENDENTE (vem do mock)
    razao_social = variaveis.get("RAZAO_SOCIAL", {})
    if isinstance(razao_social, dict):
        valor = razao_social.get("valor", "")
        assert valor and "PENDENTE:" not in valor, \
            f"RAZAO_SOCIAL não deve ser PENDENTE no ticket mock: {valor}"


def test_mock_ticket_gera_dados_validos():
    """
    Teste 7: Mock de ticket deve gerar dados válidos para o assembler.
    """
    from pipeline_aditamentos import _mock_ticket, _mock_contrato

    ticket = _mock_ticket("MOCK-001")
    contrato = _mock_contrato(ticket)

    assert ticket["key"] == "MOCK-001"
    assert ticket["tipo"] == "Aditivos não padrão"
    assert "iFood Benefícios" in ticket["empresa"]
    assert ticket["proposta_comercial_isa"] is not None
    assert 10 in ticket["modulos_solicitados"]  # módulo ISA

    assert contrato.get("razao_social") is not None
    assert contrato.get("data_assinatura_original") is not None


def test_processar_ticket_mock_audit_registrado(tmp_path, monkeypatch):
    """
    Teste 8: Auditoria deve ser registrada após dry-run.
    """
    import pipeline_aditamentos as pipe

    # Redirecionar AUDIT_PATH para tmp
    audit_path = tmp_path / "DECISION_AUDIT.csv"
    monkeypatch.setattr(pipe, "AUDIT_PATH", audit_path)

    resultado = pipe.processar_ticket("MOCK-001", dry_run=True)

    assert audit_path.exists(), "DECISION_AUDIT.csv deve ser criado"
    conteudo = audit_path.read_text(encoding="utf-8")
    assert "MOCK-001" in conteudo, "DECISION_AUDIT.csv deve conter MOCK-001"


# ---------------------------------------------------------------------------
# Teste de integração mínima do assembler com mock
# ---------------------------------------------------------------------------

def test_assembler_com_ticket_isa_completo():
    """
    Teste de integração: amendment_assembler com dados mock de ISA completo.
    """
    from modules.amendment_assembler import montar_aditamento

    ticket = {
        "key": "MOCK-999",
        "empresa": "Empresa Teste Ltda.",
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
        "modulos_solicitados": [10],
        "proposta_comercial_isa": "Proposta-ISA-Mock.pdf",
        "valor_isa_mensal": "R$ 150,00",
        "periodicidade_isa": "mensal",
        "isa_cumulativo": "não",
        "data_inicio_isa": "01 de agosto de 2026",
        "forma_pagamento_isa": "crédito em carteira digital",
        "summary": "ISA completo mock",
        "description": "Teste unitário",
    }

    contrato = {
        "razao_social": "Empresa Teste Ltda.",
        "cnpj": "11.222.333/0001-81",
        "endereco": "Rua das Flores, 100, Centro, São Paulo/SP",
        "cep": "01.001-000",
        "data_assinatura_original": "10 de janeiro de 2023",
    }

    montagem = montar_aditamento(ticket, contrato, {})

    assert "modulos_selecionados" in montagem
    assert "10_isa" in montagem["modulos_selecionados"]
    assert "score" in montagem

    score_info = montagem["score"]
    score = score_info.get("score", 0.0) if isinstance(score_info, dict) else float(score_info or 0)
    assert score >= 0.0, f"Score deve ser >= 0: {score}"
