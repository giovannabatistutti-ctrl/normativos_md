"""
test_integracao_modulos.py
==========================
Testes de integração com mocks para os módulos de saída do pipeline 15-aditamentos.
Cobre doc_generator (MCP-queue), slack_notifier e jira_updater.

Para doc_generator: nenhum teste faz chamada HTTP real — todos usam pathlib para
manipular os arquivos de fila (pending_docs / doc_results).

Para slack_notifier e jira_updater: unittest.mock.patch em requests.post.
"""

import json
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ajustar sys.path para importar os módulos do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.doc_generator import gerar_google_doc, preparar_pending_doc
from modules.slack_notifier import notificar_thread
from modules.jira_updater import atualizar_ticket
from modules.doc_result_writer import salvar_resultado, listar_pendentes


# ===========================================================================
# Helpers compartilhados
# ===========================================================================

BASE_DIR = Path(__file__).parent.parent
PENDING_DIR = BASE_DIR / "data" / "pending_docs"
RESULTS_DIR = BASE_DIR / "data" / "doc_results"


def _mock_resp(status_code=200, json_data=None, ok=None, text=""):
    """Cria um MagicMock de resposta HTTP."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.ok = ok if ok is not None else (status_code < 400)
    if json_data is not None:
        resp.json.return_value = json_data
    resp.text = text
    return resp


def _montagem_base(score=0.95, decisao="AUTONOMO", campos_pendentes=None):
    """Montagem mínima válida para testes de doc_generator."""
    return {
        "variaveis": {
            "RAZAO_SOCIAL": {"valor": "Empresa Teste Ltda."},
            "CNPJ_EMPRESA": {"valor": "12.345.678/0001-99"},
        },
        "score": {"score": score, "decisao": decisao},
        "campos_pendentes": campos_pendentes or [],
        "modulos_selecionados": ["01_cabecalho", "10_isa"],
    }


def _resultado_base(score=0.95, decisao="AUTONOMO", campos_pendentes=None):
    """Resultado combinado mínimo para testes de Slack e Jira."""
    return {
        "doc_url": "https://docs.google.com/document/d/DOC_FAKE_123/edit",
        "doc_nome": "Aditamento - Empresa Teste Ltda. - MOCK-001",
        "score": {"score": score, "decisao": decisao},
        "campos_pendentes": campos_pendentes or [],
        "perguntas_para_advogado": [],
        "modulos_selecionados": ["01_cabecalho", "10_isa"],
        "advogado_responsavel": "Dr. Teste",
    }


def _extrair_texto_slack(mock_post):
    """Extrai o campo 'text' do payload JSON enviado ao Slack."""
    call_kwargs = mock_post.call_args
    json_payload = call_kwargs[1].get("json") or {}
    return json_payload.get("text", "")


def _extrair_payload_jira(mock_post):
    """Extrai o payload JSON enviado ao Jira."""
    call_kwargs = mock_post.call_args
    return call_kwargs[1].get("json") or {}


# ===========================================================================
# doc_generator — 4 testes (MCP-queue pattern)
# ===========================================================================

def test_doc_generator_sucesso_retorna_doc_id_e_url():
    """
    Teste 1: Quando existe doc_result_{ticket_id}.json, gerar_google_doc()
    deve retornar doc_id e doc_url do arquivo (fluxo Planner → pipeline).
    """
    ticket_id = "MOCK-DOC-001"
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Simular que o Planner já gerou o documento
    path_result = RESULTS_DIR / f"{ticket_id}_doc_result.json"
    path_result.write_text(json.dumps({
        "ticket_id": ticket_id,
        "doc_id": "DOC_FAKE_123",
        "doc_url": "https://docs.google.com/document/d/DOC_FAKE_123/edit",
        "doc_nome": "Aditamento - Empresa Teste Ltda. - MOCK-DOC-001",
        "score": 0.95,
        "decisao": "AUTONOMO",
        "campos_pendentes": [],
        "status": "gerado",
    }, ensure_ascii=False))

    montagem = _montagem_base()

    resultado = gerar_google_doc(montagem, ticket_id)

    assert resultado["doc_id"] == "DOC_FAKE_123", (
        f"Esperava doc_id='DOC_FAKE_123', obteve {resultado['doc_id']!r}"
    )
    assert "DOC_FAKE_123" in resultado["doc_url"], (
        f"Esperava 'DOC_FAKE_123' na doc_url, obteve {resultado['doc_url']!r}"
    )
    assert resultado["status"] == "gerado"
    assert "erro" not in resultado, "Não deveria haver chave 'erro' no resultado"

    # Cleanup
    path_result.unlink(missing_ok=True)


def test_doc_generator_403_retorna_doc_id_none_com_pending_doc():
    """
    Teste 2: Quando NÃO existe doc_result, gerar_google_doc() deve salvar
    pending_doc e retornar status='pendente_mcp' com doc_id=None.
    """
    ticket_id = "MOCK-DOC-002"
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Garantir que não existe resultado prévio
    results = list(RESULTS_DIR.glob(f"{ticket_id}_*"))
    for r in results:
        r.unlink(missing_ok=True)
    pendings = list(PENDING_DIR.glob(f"{ticket_id}_*"))
    for p in pendings:
        p.unlink(missing_ok=True)

    montagem = _montagem_base()

    resultado = gerar_google_doc(montagem, ticket_id)

    assert resultado["doc_id"] is None, (
        f"Esperava doc_id=None, obteve {resultado['doc_id']!r}"
    )
    assert resultado["status"] == "pendente_mcp", (
        f"Esperava status='pendente_mcp', obteve {resultado['status']!r}"
    )
    assert resultado.get("pending_doc_path") is not None, (
        "Esperava pending_doc_path no resultado"
    )
    # Verificar que o arquivo pending foi criado
    path_pending = Path(resultado["pending_doc_path"])
    assert path_pending.exists(), f"Arquivo pending_doc não foi criado: {path_pending}"

    # Cleanup
    path_pending.unlink(missing_ok=True)


def test_doc_generator_200_completo_fluxo_mcp_queue_sem_excecao():
    """
    Teste 3: Fluxo completo MCP-queue — pending_doc salvo,
    Planner processa, salva doc_result, pipeline lê de volta.
    """
    ticket_id = "MOCK-DOC-003"
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Limpar estado prévio
    for f in RESULTS_DIR.glob(f"{ticket_id}_*"):
        f.unlink(missing_ok=True)
    for f in PENDING_DIR.glob(f"{ticket_id}_*"):
        f.unlink(missing_ok=True)

    montagem = _montagem_base()

    # Etapa 1: Pipeline salva pending_doc
    resultado_pendente = gerar_google_doc(montagem, ticket_id)
    assert resultado_pendente["status"] == "pendente_mcp"

    # Etapa 2: Planner processa e salva doc_result
    salvar_resultado(
        ticket_id=ticket_id,
        doc_id="DOC_COMPLETO_001",
        doc_url="https://docs.google.com/document/d/DOC_COMPLETO_001/edit",
        doc_nome="Aditamento - Empresa Teste Ltda. - MOCK-DOC-003",
        score=0.95,
        decisao="AUTONOMO",
        campos_pendentes=[],
    )

    # Etapa 3: Pipeline lê de volta
    resultado_final = gerar_google_doc(montagem, ticket_id)
    assert resultado_final["doc_id"] == "DOC_COMPLETO_001"
    assert resultado_final["status"] == "gerado"

    # Cleanup
    (RESULTS_DIR / f"{ticket_id}_doc_result.json").unlink(missing_ok=True)
    (PENDING_DIR / f"{ticket_id}_pending_doc.json").unlink(missing_ok=True)


def test_doc_generator_pendente_no_pending_doc_contem_colchete():
    """
    Teste 4: Variável com valor 'PENDENTE: informar data de vigência' deve
    aparecer como '[PENDENTE: informar data de vigência]' no pending_doc.
    """
    ticket_id = "MOCK-DOC-004"
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Garantir estado limpo
    for f in RESULTS_DIR.glob(f"{ticket_id}_*"):
        f.unlink(missing_ok=True)
    for f in PENDING_DIR.glob(f"{ticket_id}_*"):
        f.unlink(missing_ok=True)

    montagem = {
        "variaveis": {
            "RAZAO_SOCIAL": {"valor": "Empresa Pendente Ltda."},
            "VIGENCIA": {"valor": "PENDENTE: informar data de vigência"},
        },
        "score": {"score": 0.75, "decisao": "REVISAO_HUMANA"},
        "campos_pendentes": ["VIGENCIA"],
        "modulos_selecionados": ["01_cabecalho"],
    }

    gerar_google_doc(montagem, ticket_id)

    path_pending = PENDING_DIR / f"{ticket_id}_pending_doc.json"
    assert path_pending.exists(), f"Arquivo pending_doc não foi criado: {path_pending}"

    with open(path_pending, encoding="utf-8") as f:
        pending = json.load(f)

    # Procurar qualquer placeholder que contenha [PENDENTE:
    subs_campos = pending.get("substituicoes_campos", {})
    encontrou_pendente = any(
        "[PENDENTE:" in str(v) for v in subs_campos.values()
    )
    assert encontrou_pendente, (
        f"Esperava '[PENDENTE:' em alguma substituição, mas obteve: {subs_campos}"
    )

    # Cleanup
    path_pending.unlink(missing_ok=True)


# ===========================================================================
# slack_notifier — 4 testes
# ===========================================================================

def test_slack_score_alto_retorna_true_mensagem_gerado_automaticamente():
    """
    Teste 5: Mock requests.post retornando {"ok": True, "ts": "12345"} com score >= 0.90
    → retorna (True, ts) e mensagem contém 'gerado automaticamente'.
    """
    mock_resp = _mock_resp(200, {"ok": True, "ts": "12345"})
    resultado = _resultado_base(score=0.95, decisao="AUTONOMO")
    with patch("modules.slack_notifier.requests.post",
               return_value=mock_resp) as mock_post:
        retorno = notificar_thread("C033DR3282G", "1234567890.000001", resultado)
    # notificar_thread retorna tuple[bool, str]
    assert retorno[0] is True, f"Esperava (True, ts), obteve {retorno!r}"

    posted_text = _extrair_texto_slack(mock_post)
    assert "gerado automaticamente" in posted_text, (
        f"Esperava 'gerado automaticamente' na mensagem, obteve: {posted_text!r}"
    )


def test_slack_score_baixo_retorna_true_mensagem_com_revisao():
    """
    Teste 6: Mock retornando {"ok": True} com score < 0.90
    → retorna (True, ts) e mensagem contém 'revisão'.
    """
    mock_resp = _mock_resp(200, {"ok": True, "ts": "99999"})
    resultado = _resultado_base(
        score=0.75,
        decisao="REVISAO_HUMANA",
        campos_pendentes=["CNPJ", "VIGENCIA"],
    )

    with patch("modules.slack_notifier.requests.post",
               return_value=mock_resp) as mock_post:
        retorno = notificar_thread("C033DR3282G", "", resultado)

    assert retorno[0] is True, f"Esperava (True, ts), obteve {retorno!r}"

    posted_text = _extrair_texto_slack(mock_post)
    assert "revis" in posted_text.lower(), (
        f"Esperava 'revisão' na mensagem, obteve: {posted_text!r}"
    )


def test_slack_ok_false_retorna_false():
    """
    Teste 7: Mock retornando {"ok": False, "error": "channel_not_found"}
    → retorna (False, '').
    """
    mock_resp = _mock_resp(200, {"ok": False, "error": "channel_not_found"})
    resultado = _resultado_base()
    with patch("modules.slack_notifier.requests.post", return_value=mock_resp):
        retorno = notificar_thread("CANAL_INVALIDO", "", resultado)

    assert retorno[0] is False, f"Esperava (False, ''), obteve {retorno!r}"


def test_slack_http_407_retorna_false():
    """
    Teste 8: Mock retornando HTTP 407
    → retorna (False, '') (credencial não configurada no proxy).
    """
    mock_resp = _mock_resp(407, ok=False, text="Proxy Authentication Required")
    resultado = _resultado_base()
    with patch("modules.slack_notifier.requests.post", return_value=mock_resp):
        retorno = notificar_thread("C033DR3282G", "", resultado)

    assert retorno[0] is False, f"Esperava (False, ''), obteve {retorno!r}"


# ===========================================================================
# jira_updater — 4 testes
# ===========================================================================

def test_jira_score_alto_http_201_retorna_true():
    """
    Teste 9: Mock requests.post retornando HTTP 201 com score >= 0.90
    → retorna True.
    """
    mock_resp = _mock_resp(201, {})
    resultado = _resultado_base(score=0.95, decisao="AUTONOMO")

    with patch("modules.jira_updater.requests.post", return_value=mock_resp):
        retorno = atualizar_ticket("JURFIN-9999", resultado)

    assert retorno is True, "Esperava retorno True para HTTP 201"


def test_jira_http_401_retorna_false():
    """
    Teste 10: Mock retornando HTTP 401 → retorna False.
    """
    mock_resp = _mock_resp(401, ok=False, text="Unauthorized")
    resultado = _resultado_base()
    with patch("modules.jira_updater.requests.post", return_value=mock_resp):
        retorno = atualizar_ticket("JURFIN-9999", resultado)

    assert retorno is False, "Esperava retorno False para HTTP 401"


def test_jira_payload_e_adf_valido():
    """
    Teste 11: Payload enviado ao Jira deve ser ADF válido:
    body.type == "doc" e body.version == 1.
    """
    mock_resp = _mock_resp(201, {})
    resultado = _resultado_base(score=0.92, decisao="AUTONOMO")

    with patch("modules.jira_updater.requests.post",
               return_value=mock_resp) as mock_post:
        retorno = atualizar_ticket("JURFIN-1111", resultado)

    assert retorno is True

    payload = _extrair_payload_jira(mock_post)
    body = payload.get("body", {})

    assert body.get("type") == "doc", (
        f"Esperava body.type='doc', obteve {body.get('type')!r}"
    )
    assert body.get("version") == 1, (
        f"Esperava body.version=1, obteve {body.get('version')!r}"
    )
    assert "content" in body, "Esperava chave 'content' no body ADF"
    assert isinstance(body["content"], list) and len(body["content"]) > 0, (
        "body.content deve ser lista não-vazia"
    )


def test_jira_score_baixo_com_campos_pendentes_menciona_campos():
    """
    Teste 12: Score < 0.90 com campos_pendentes → corpo do comentário Jira
    menciona os campos pendentes.
    """
    mock_resp = _mock_resp(201, {})
    campos = ["CNPJ_EMPRESA", "DATA_VIGENCIA", "VALOR_CONTRATO"]
    resultado = _resultado_base(
        score=0.70,
        decisao="REVISAO_HUMANA",
        campos_pendentes=campos,
    )

    with patch("modules.jira_updater.requests.post",
               return_value=mock_resp) as mock_post:
        retorno = atualizar_ticket("JURFIN-2222", resultado)

    assert retorno is True

    # Extrair texto do body ADF
    payload = _extrair_payload_jira(mock_post)
    body = payload.get("body", {})
    content_blocks = body.get("content", [])

    full_text = ""
    for block in content_blocks:
        for inner in block.get("content", []):
            if inner.get("type") == "text":
                full_text += inner.get("text", "")

    at_least_one = any(campo in full_text for campo in campos)
    assert at_least_one, (
        f"Esperava campos pendentes no comentário Jira, mas obteve: {full_text!r}"
    )
