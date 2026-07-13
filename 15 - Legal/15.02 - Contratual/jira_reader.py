"""
jira_reader.py
==============
Módulo de leitura de tickets Jira — iFood Benefícios Aditamentos.
Agente Leitor: captura dados brutos do ticket sem interpretar ou inventar.

Responsabilidades:
- Buscar tickets do tipo "Aditivos não padrão" para iFood Benefícios
- Extrair dados estruturados: empresa, CNPJ, módulos solicitados, anexos
- Identificar o advogado revisor responsável pelo ticket

Fonte de dados: API Jira (https://api.atlassian.com/ex/jira/{cloudId}) via proxy autenticado.

Padrão MCP-queue:
- Leitura direta via HTTP (api.atlassian.com) tenta primeiro
- Se falhar (404/401/407) → salva pending_jira_read/{ticket_id}.json
- Planner detecta o pending e processa via Ifood-AtlassianFintechB2b_getJiraIssue
- Salva jira_result/{ticket_id}.json para consumo do pipeline

REGRA DE INTEGRIDADE: Nenhum campo é inventado.
Campos ausentes retornam None — nunca valores fabricados.
"""

import json
import logging
import re
import requests
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Campos Jira mapeados para o pipeline de aditamentos
CAMPOS_RELEVANTES = [
    "summary",
    "description",
    "issuetype",
    "status",
    "assignee",
    "reporter",
    "customfield_empresa",       # Empresa contratante
    "customfield_cnpj",          # CNPJ da empresa
    "customfield_modulos",       # Módulos de aditamento selecionados
    "customfield_proposta_com",  # Proposta Comercial (ISA)
    "attachment",                # Anexos (contrato, proposta, etc.)
    "comment",
    "created",
    "updated",
]

# URL base da API Jira (sem credenciais — proxy injeta auth)
JIRA_CLOUD_ID = "accc6d18-01aa-4469-a840-d3f2a47e2502"
JIRA_BASE_URL = f"https://api.atlassian.com/ex/jira/{JIRA_CLOUD_ID}"

# Diretórios de fila (padrão MCP-queue)
BASE_DIR = Path(__file__).parent.parent
PENDING_JIRA_DIR = BASE_DIR / "data" / "pending_jira_reads"
JIRA_RESULTS_DIR = BASE_DIR / "data" / "jira_results"


# ---------------------------------------------------------------------------
# Helpers de parsing
# ---------------------------------------------------------------------------

def _limpar_adf_para_texto(node: object) -> str:
    """
    Converte Atlassian Document Format (ADF) para texto puro.
    Não fabrica conteúdo — retorna exatamente o que está no nó.
    """
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        tipo = node.get("type", "")
        conteudo = node.get("content", [])
        texto_node = node.get("text", "")

        if tipo == "text":
            return texto_node
        if tipo in ("doc", "paragraph", "bulletList", "orderedList",
                    "listItem", "blockquote", "panel"):
            return " ".join(_limpar_adf_para_texto(c) for c in conteudo).strip()
        if tipo == "hardBreak":
            return "\n"
        if tipo == "heading":
            return " ".join(_limpar_adf_para_texto(c) for c in conteudo).strip()
        if tipo == "codeBlock":
            return " ".join(_limpar_adf_para_texto(c) for c in conteudo).strip()
        # Qualquer outro nó: percorrer filhos
        return " ".join(_limpar_adf_para_texto(c) for c in conteudo).strip()
    if isinstance(node, list):
        return " ".join(_limpar_adf_para_texto(c) for c in node).strip()
    return ""


def _extrair_texto_campo(valor: object) -> str | None:
    """
    Extrai texto de um campo que pode ser string, ADF dict ou None.
    Retorna None se não houver valor — nunca inventa.
    """
    if valor is None:
        return None
    if isinstance(valor, str):
        return valor.strip() or None
    if isinstance(valor, dict):
        # ADF
        texto = _limpar_adf_para_texto(valor)
        return texto.strip() or None
    return None


def _extrair_nome_usuario(user_obj: object) -> str | None:
    """Extrai displayName de um objeto de usuário Jira. Retorna None se ausente."""
    if not isinstance(user_obj, dict):
        return None
    return user_obj.get("displayName") or None


def _extrair_texto_comentario(body: object) -> str:
    """Extrai texto limpo de um corpo de comentário (pode ser ADF ou string)."""
    if isinstance(body, dict):
        return _limpar_adf_para_texto(body)
    if isinstance(body, str):
        return body
    return ""


# ---------------------------------------------------------------------------
# Funções do padrão MCP-queue
# ---------------------------------------------------------------------------

def _salvar_pending_read(ticket_id: str) -> Path:
    """
    Salva pending file para o Planner processar via MCP.

    Arquivo salvo em data/pending_jira_reads/{ticket_id}_pending.json.
    """
    PENDING_JIRA_DIR.mkdir(parents=True, exist_ok=True)
    path = PENDING_JIRA_DIR / f"{ticket_id}_pending.json"
    path.write_text(json.dumps({
        "ticket_id": ticket_id,
        "cloud_id": JIRA_CLOUD_ID,
        "status": "aguardando_mcp",
        "criado_em": datetime.now().isoformat(timespec="seconds"),
    }, ensure_ascii=False, indent=2))
    logger.info("jira_reader: pending_read salvo — aguardando Planner. Arquivo: %s", path)
    return path


def _verificar_resultado_disponivel(ticket_id: str) -> dict | None:
    """
    Verifica se o Planner já processou este ticket.

    Args:
        ticket_id: ID do ticket (ex: "JURFIN-1234").

    Returns:
        dict com dados normalizados se o resultado existir, None caso contrário.
    """
    result_path = JIRA_RESULTS_DIR / f"{ticket_id}_result.json"
    if result_path.exists():
        logger.info("jira_reader: resultado MCP existente encontrado para %s", ticket_id)
        return json.loads(result_path.read_text(encoding="utf-8"))
    return None


def salvar_resultado_jira(ticket_id: str, dados: dict) -> Path:
    """
    Chamado pelo Planner após ler o ticket via MCP.
    Salva resultado normalizado no diretório de resultados.

    Args:
        ticket_id: ID do ticket (ex: "JURFIN-1234").
        dados: dict com campos do ticket no formato normalizado do pipeline.

    Returns:
        Path do arquivo salvo.
    """
    JIRA_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = JIRA_RESULTS_DIR / f"{ticket_id}_result.json"
    dados["_source"] = "mcp_planner"
    dados["_processado_em"] = datetime.now().isoformat(timespec="seconds")
    path.write_text(json.dumps(dados, ensure_ascii=False, indent=2, default=str))
    logger.info("jira_reader: resultado salvo em %s", path)
    return path


def listar_jira_pendentes() -> list:
    """
    Lista tickets aguardando leitura pelo Planner.

    Retorna apenas os pending files que ainda não têm resultado correspondente.
    """
    if not PENDING_JIRA_DIR.exists():
        return []
    pendentes = []
    for f in PENDING_JIRA_DIR.glob("*_pending.json"):
        ticket_id = f.name.replace("_pending.json", "")
        result = JIRA_RESULTS_DIR / f"{ticket_id}_result.json"
        if not result.exists():
            pendentes.append(json.loads(f.read_text(encoding="utf-8")))
    return pendentes


def _normalizar_ticket_mcp(raw_mcp: dict) -> dict:
    """
    Normaliza a resposta do MCP (Ifood-AtlassianFintechB2b_getJiraIssue)
    para o formato interno do pipeline.

    Args:
        raw_mcp: resultado de Ifood-AtlassianFintechB2b_getJiraIssue.

    Returns:
        dict no mesmo formato que ler_ticket() retorna via HTTP direto.
    """
    fields = raw_mcp.get("fields", {})

    # Extrair texto da descrição (ADF ou string)
    descricao_raw = fields.get("description")
    descricao = _extrair_texto_campo(descricao_raw) if descricao_raw else None

    # Assignee
    assignee = fields.get("assignee") or {}
    advogado_responsavel = _extrair_nome_usuario(assignee)

    # Tipo do issue
    issuetype = fields.get("issuetype") or {}
    tipo = issuetype.get("name") if isinstance(issuetype, dict) else None

    # Status
    status_obj = fields.get("status") or {}
    status = status_obj.get("name") if isinstance(status_obj, dict) else None

    # Reporter
    reporter = fields.get("reporter") or {}
    solicitante = _extrair_nome_usuario(reporter)

    # Empresa: campo customizado ou fallback em summary
    empresa = _extrair_texto_campo(fields.get("customfield_empresa"))
    if empresa is None:
        cf_emp = fields.get("customfield_empresa")
        if isinstance(cf_emp, dict):
            empresa = cf_emp.get("value") or None

    # Anexos
    anexos_raw = fields.get("attachment") or []
    anexos = []
    for att in (anexos_raw if isinstance(anexos_raw, list) else []):
        if not isinstance(att, dict):
            continue
        anexos.append({
            "id": att.get("id") or None,
            "nome": att.get("filename") or None,
            "tipo_mime": att.get("mimeType") or None,
            "url_download": att.get("content") or None,
            "tamanho_bytes": att.get("size") if isinstance(att.get("size"), int) else None,
        })

    # Comentários (últimos 20)
    comentarios_raw = fields.get("comment") or {}
    comentarios_lista = comentarios_raw.get("comments", []) if isinstance(comentarios_raw, dict) else []
    comentarios = []
    for c in comentarios_lista[-20:]:
        if not isinstance(c, dict):
            continue
        autor_obj = c.get("author")
        comentarios.append({
            "autor": _extrair_nome_usuario(autor_obj),
            "data": c.get("created") or None,
            "texto": _extrair_texto_comentario(c.get("body")),
        })

    # Campos customizados relevantes extras
    campos_customizados = {}
    for chave, valor in fields.items():
        if chave.startswith("customfield_") and chave not in (
            "customfield_empresa", "customfield_cnpj",
            "customfield_modulos", "customfield_proposta_com",
        ):
            if valor is not None:
                campos_customizados[chave] = valor

    return {
        "ticket_id": raw_mcp.get("key"),
        "titulo": _extrair_texto_campo(fields.get("summary")),
        "descricao": descricao,
        "tipo": tipo,
        "empresa": empresa,
        "solicitante": solicitante,
        "advogado_responsavel": advogado_responsavel,
        "status": status,
        "data_criacao": fields.get("created") or None,
        "data_atualizacao": fields.get("updated") or None,
        "anexos": anexos,
        "comentarios": comentarios,
        "campos_customizados": campos_customizados,
        "_raw_mcp": raw_mcp,
    }


# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------

def ler_ticket(ticket_id: str) -> dict:
    """
    Lê um ticket Jira e retorna campos estruturados.

    Fluxo MCP-queue:
      1. Verifica se resultado do Planner já existe (jira_results/)
      2. Tenta GET direto em https://api.atlassian.com/ex/jira/{cloudId}/rest/api/3/issue/{ticket_id}
      3. Se falhar (401/407/404/outro) → salva pending_jira_reads/{ticket_id}_pending.json
         e retorna {"status": "pendente_mcp", ...}

    Args:
        ticket_id: ID do ticket (ex: "JURFIN-1234").

    Returns:
        dict com campos extraídos. Campos ausentes → None (nunca inventados).
        Em caso de erro HTTP, retorna dict com chave "status": "pendente_mcp".
    """
    # 1. Verificar se o Planner já processou este ticket
    resultado_existente = _verificar_resultado_disponivel(ticket_id)
    if resultado_existente:
        logger.info("jira_reader: usando resultado MCP existente para %s", ticket_id)
        return resultado_existente

    # 2. Tentar leitura direta via HTTP
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}"
    params = {"fields": ",".join(CAMPOS_RELEVANTES), "expand": "renderedFields"}

    logger.info("ler_ticket: GET %s", url)
    resultado_http = None
    try:
        resp = requests.get(url, params=params, timeout=30)
    except requests.exceptions.RequestException as exc:
        logger.error("ler_ticket: erro de conexão — %s", exc)
        # Falhou → salvar pending para o Planner
        path = _salvar_pending_read(ticket_id)
        return {
            "status": "pendente_mcp",
            "ticket_id": ticket_id,
            "pending_path": str(path),
            "mensagem": f"Leitura direta falhou (conexão). pending_read salvo em {path}. Planner deve processar via MCP.",
        }

    # 3. Processar resposta HTTP
    if resp.status_code in (401, 407):
        logger.warning("ler_ticket: 401/407 — credencial Jira não configurada no proxy")
        path = _salvar_pending_read(ticket_id)
        return {
            "status": "pendente_mcp",
            "ticket_id": ticket_id,
            "pending_path": str(path),
            "mensagem": f"Credencial Jira não configurada (HTTP {resp.status_code}). pending_read salvo em {path}. Planner deve processar via MCP.",
        }
    if resp.status_code == 404:
        logger.warning("ler_ticket: 404 — ticket não encontrado: %s", ticket_id)
        path = _salvar_pending_read(ticket_id)
        return {
            "status": "pendente_mcp",
            "ticket_id": ticket_id,
            "pending_path": str(path),
            "mensagem": f"Ticket não encontrado (HTTP 404). pending_read salvo em {path}. Planner deve processar via MCP.",
        }
    if not resp.ok:
        logger.warning("ler_ticket: erro HTTP %s — salvando pending para Planner", resp.status_code)
        path = _salvar_pending_read(ticket_id)
        return {
            "status": "pendente_mcp",
            "ticket_id": ticket_id,
            "pending_path": str(path),
            "mensagem": f"Erro HTTP {resp.status_code}. pending_read salvo em {path}. Planner deve processar via MCP.",
        }

    # 4. Sucesso HTTP — parsear e retornar normalmente
    try:
        raw = resp.json()
    except ValueError as exc:
        logger.error("ler_ticket: resposta inválida da API — %s", exc)
        path = _salvar_pending_read(ticket_id)
        return {
            "status": "pendente_mcp",
            "ticket_id": ticket_id,
            "pending_path": str(path),
            "mensagem": f"Resposta inválida da API: {exc}. pending_read salvo em {path}. Planner deve processar via MCP.",
        }

    fields = raw.get("fields") or {}

    # ---- extração de campos padrão ---------------------------------------
    titulo = _extrair_texto_campo(fields.get("summary"))
    descricao_raw = fields.get("description")
    descricao = _extrair_texto_campo(descricao_raw)

    tipo_obj = fields.get("issuetype")
    tipo = (tipo_obj.get("name") if isinstance(tipo_obj, dict) else None)

    status_obj = fields.get("status")
    status = (status_obj.get("name") if isinstance(status_obj, dict) else None)

    solicitante = _extrair_nome_usuario(fields.get("reporter"))
    advogado_responsavel = _extrair_nome_usuario(fields.get("assignee"))

    data_criacao = fields.get("created") or None
    data_atualizacao = fields.get("updated") or None

    # ---- empresa: campo customizado ou fallback em summary ---------------
    empresa = _extrair_texto_campo(fields.get("customfield_empresa"))
    if empresa is None:
        cf_emp = fields.get("customfield_empresa")
        if isinstance(cf_emp, dict):
            empresa = cf_emp.get("value") or None

    # ---- anexos ----------------------------------------------------------
    anexos_raw = fields.get("attachment") or []
    anexos = []
    for att in (anexos_raw if isinstance(anexos_raw, list) else []):
        if not isinstance(att, dict):
            continue
        anexos.append({
            "id": att.get("id") or None,
            "nome": att.get("filename") or None,
            "tipo_mime": att.get("mimeType") or None,
            "url_download": att.get("content") or None,
            "tamanho_bytes": att.get("size") if isinstance(att.get("size"), int) else None,
        })

    # ---- comentários (últimos 20) ----------------------------------------
    comentarios_raw = fields.get("comment") or {}
    comentarios_lista = comentarios_raw.get("comments", []) if isinstance(comentarios_raw, dict) else []
    comentarios = []
    for c in comentarios_lista[-20:]:
        if not isinstance(c, dict):
            continue
        autor_obj = c.get("author")
        comentarios.append({
            "autor": _extrair_nome_usuario(autor_obj),
            "data": c.get("created") or None,
            "texto": _extrair_texto_comentario(c.get("body")),
        })

    # ---- campos customizados relevantes extras ---------------------------
    campos_customizados = {}
    for chave, valor in fields.items():
        if chave.startswith("customfield_") and chave not in (
            "customfield_empresa", "customfield_cnpj",
            "customfield_modulos", "customfield_proposta_com",
        ):
            if valor is not None:
                campos_customizados[chave] = valor

    return {
        "ticket_id": raw.get("key") or ticket_id,
        "titulo": titulo,
        "descricao": descricao,
        "tipo": tipo,
        "empresa": empresa,
        "solicitante": solicitante,
        "advogado_responsavel": advogado_responsavel,
        "status": status,
        "data_criacao": data_criacao,
        "data_atualizacao": data_atualizacao,
        "anexos": anexos,
        "comentarios": comentarios,
        "campos_customizados": campos_customizados,
    }


# ---------------------------------------------------------------------------
# Filtro de elegibilidade
# ---------------------------------------------------------------------------

def eh_aditamento_ifb(ticket: dict) -> bool:
    """
    Retorna True se o ticket é um aditamento elegível de iFood Benefícios.

    Critérios:
    - ticket["tipo"] == "Aditivos não padrão"
    - ticket["empresa"] contém "iFood Benefícios" (case-insensitive)

    Args:
        ticket: dict retornado por ler_ticket().

    Returns:
        bool — True se elegível, False caso contrário.
        Retorna False (não True) se campos obrigatórios forem None.
    """
    tipo = ticket.get("tipo")
    empresa = ticket.get("empresa")

    if tipo is None or empresa is None:
        return False

    tipo_ok = tipo.strip() == "Aditivos não padrão"
    empresa_ok = "ifood benefícios" in empresa.lower()

    return tipo_ok and empresa_ok


# ---------------------------------------------------------------------------
# Classe de compatibilidade (mantida para não quebrar pipeline existente)
# ---------------------------------------------------------------------------
class JiraReader:
    """
    Wrapper de classe para compatibilidade com pipeline_aditamentos.py.
    Delega para as funções standalone ler_ticket() e eh_aditamento_ifb().
    """

    def __init__(self, config: dict):
        self.base_url = config.get("base_url", JIRA_BASE_URL)
        self.project = config.get("project", "JURFIN")
        self.filtro_tipo = config.get("filtro_tipo", "Aditivos não padrão")
        self.filtro_empresa = config.get("filtro_empresa", "iFood Benefícios")

    def read(self, ticket_id: str | None = None) -> dict | None:
        """
        Lê um ticket específico.
        Retorna None se ticket_id não informado ou em caso de erro.
        """
        if not ticket_id:
            logger.warning("JiraReader.read(): ticket_id não informado")
            return None
        resultado = ler_ticket(ticket_id)
        if resultado.get("status") == "pendente_mcp":
            logger.info("JiraReader.read(): ticket %s pendente MCP — path: %s",
                        ticket_id, resultado.get("pending_path"))
            return None
        if "erro" in resultado:
            logger.error("JiraReader.read(): %s", resultado["erro"])
            return None
        return resultado

    def _build_jql(self) -> str:
        """Monta JQL para busca de tickets de aditamento em aberto."""
        return (
            f'project = "{self.project}" '
            f'AND issuetype = "{self.filtro_tipo}" '
            f'AND "Empresa" = "{self.filtro_empresa}" '
            f'AND status NOT IN ("Concluído", "Cancelado") '
            f'ORDER BY created DESC'
        )
