"""
doc_generator.py (v2)
=====================
Módulo de geração de documento via padrão MCP-queue.

Fluxo:
  1. Monta dict de substituições {placeholder: valor}
  2. Salva pending_doc_{ticket_id}.json na fila
  3. Retorna status "pendente_mcp" (doc_id=None)
  4. Quando o Planner processa a fila → salva doc_result_{ticket_id}.json
  5. Pipeline continua lendo doc_result para Slack + Jira

O Planner usa:
  - GoogleWorkspace_copy_drive_file(template_id, nome_doc, pasta_id)
  - GoogleWorkspace_find_and_replace_doc(doc_id, find, replace) × N campos
  - GoogleWorkspace_manage_document_comment(doc_id, score_info)
"""

import json
import logging
import re
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / "config.json"
PENDING_DIR = BASE_DIR / "data" / "pending_docs"
RESULTS_DIR = BASE_DIR / "data" / "doc_results"

# Módulos com texto pré-definido (texto fixo, sem customização LLM)
TEXTO_MODULOS_FIXOS = {
    "retirada_renovacao_automatica": (
        "1.1. As Partes concordam em eliminar a cláusula de prorrogação automática "
        "do Contrato. A cláusula 10.2 dos Termos e Condições Gerais passa a vigorar: "
        "'10.2. Renovação. Uma vez transcorrido o prazo de vigência inicial, o Contrato "
        "poderá ser prorrogado mediante celebração de termo aditivo firmado pelas Partes.'"
    ),
    "cessao": (
        "1.1. As Partes acordam em alterar a Cláusula 16.6 dos Termos e Condições Gerais: "
        "'16.6. Cessão. O iFood Benefícios poderá ceder seus direitos e obrigações "
        "independentemente de autorização da CONTRATANTE. A CONTRATANTE não poderá ceder "
        "sem prévia e expressa anuência por escrito do iFood Benefícios.'"
    ),
    "ifood_pago_ip": (
        "1.1. O iFood Benefícios declara que possui acordo com IFOOD PAGO INSTITUIÇÃO DE "
        "PAGAMENTO S.A. (CNPJ: 19.468.242/0001-32), que atua na intermediação dos "
        "pagamentos recebidos pelo iFood Benefícios."
    ),
    "retirada_subsidio_colab": (
        "1.1. As Partes formalizam a exclusão do Programa Colab+, subsidiado pelo "
        "iFood Benefícios aos Colaboradores da Empresa."
    ),
}

# Mapeamento módulo → marcador no template
MODULE_MARKERS = {
    "retirada_renovacao_automatica":                  "{{#MODULE: retirada_renovacao_automatica}}",
    "prorrogacao_vigencia":                            "{{#MODULE: prorrogacao_vigencia}}",
    "prorrogacao_vigencia_com_renovacao_automatica":    "{{#MODULE: prorrogacao_vigencia_com_renovacao_automatica}}",
    "cessao":                                          "{{#MODULE: cessao}}",
    "aviso_previo":                                    "{{#MODULE: aviso_previo}}",
    "alteracao_cnpjs_grupo":                            "{{#MODULE: alteracao_cnpjs_grupo}}",
    "ifood_pago_ip":                                   "{{#MODULE: ifood_pago_ip}}",
    "retirada_subsidio_colab":                         "{{#MODULE: retirada_subsidio_colab}}",
    "alteracao_valor":                                "{{#MODULE: alteracao_valor}}",
    "alteracao_produto":                              "{{#MODULE: alteracao_produto}}",
    "isa":                                             "{{#MODULE: isa}}",
    "saldo_extra":                                     "{{#MODULE: saldo_extra}}",
    "saldo_natal":                                     "{{#MODULE: saldo_natal}}",
}

ALL_MODULES = set(MODULE_MARKERS.keys())


def _load_config() -> dict:
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _get_valor(variaveis: dict, campo: str) -> str | None:
    """Extrai valor de uma variável. Retorna None se ausente ou PENDENTE."""
    info = variaveis.get(campo)
    if not info:
        return None
    if isinstance(info, dict):
        valor = info.get("valor", "")
    else:
        valor = str(info)
    if "PENDENTE:" in str(valor):
        return None
    return valor or None


def _pendente_para_colchete(valor: str) -> str:
    """
    Converte marcações PENDENTE para formato [PENDENTE: texto da pergunta].
    """
    resultado = re.sub(
        r"\{\{PENDENTE:\s*(.+?)\}\}",
        r"[PENDENTE: \1]",
        valor,
        flags=re.DOTALL,
    )
    resultado = re.sub(
        r"(?<!\[\[)PENDENTE:\s*(.+?)(?=\s*$|\n|\{\{)",
        r"[PENDENTE: \1]",
        resultado,
        flags=re.DOTALL,
    )
    return resultado


def _nome_documento(empresa: str, ticket_id: str) -> str:
    """Gera o nome do documento no padrão configurado."""
    cfg = _load_config()
    fmt = cfg.get("google_docs", {}).get("doc_nome_formato", "{descricao} — {ticket_id}")
    descricao = f"Aditamento — {empresa}"
    return fmt.format(descricao=descricao, ticket_id=ticket_id)


def _montar_substituicoes(montagem: dict, campos_agente2: dict = None) -> dict:
    """
    Monta o dict de substituições {placeholder: valor}.
    Usa campos_agente2 (output do Agente 2) se disponível; senão usa montagem do assembler.
    """
    subs = {}

    # Fonte principal: campos_finais do Agente 2 (se disponível)
    campos = campos_agente2 if campos_agente2 else {}

    # Fallback: variáveis do assembler
    variaveis = montagem.get("variaveis", {})
    for campo, info in variaveis.items():
        if campo not in campos:
            valor = info.get("valor", "") if isinstance(info, dict) else str(info)
            if valor and "PENDENTE:" not in str(valor):
                campos[campo] = valor
            elif valor and "PENDENTE:" in str(valor):
                campos[campo] = (
                    f"[PENDENTE: {info.get('pergunta', campo)}]"
                    if isinstance(info, dict)
                    else "[PENDENTE]"
                )

    # Campos substituídos pelo pipeline — template v3
    # NOTA: Assinaturas (representantes, testemunhas) NÃO substituídas:
    #       o time comercial preenche manualmente na plataforma de assinatura.
    mapping = {
        "CONTRATO_ORIGINAL":               "{{CONTRATO_ORIGINAL}}",
        "RAZAO_SOCIAL":                    "{{RAZAO_SOCIAL}}",
        "CNPJ_EMPRESA":                    "{{CNPJ_EMPRESA}}",
        "ENDERECO_EMPRESA":                "{{ENDERECO_EMPRESA}}",
        "CEP_EMPRESA":                     "{{CEP_EMPRESA}}",
        "DATA_CONTRATO_ORIGINAL":          "{{DATA_CONTRATO_ORIGINAL}}",
        "DATA_ADITIVO":                    "{{DATA_ADITIVO}}",
        "CIDADE_ASSINATURA":               "{{CIDADE_ASSINATURA}}",
        "PRAZO_MESES":                     "{{PRAZO_MESES}}",
        "PRAZO_MESES_EXTENSO":             "{{PRAZO_MESES_EXTENSO}}",
        "DATA_NOVA_VIGENCIA":              "{{DATA_NOVA_VIGENCIA}}",
        "PRAZO_AVISO_PREVIO_DIAS":         "{{PRAZO_AVISO_PREVIO_DIAS}}",
        "PRAZO_AVISO_PREVIO_EXTENSO":      "{{PRAZO_AVISO_PREVIO_EXTENSO}}",
        "CNPJS_INCLUIR":                   "{{CNPJS_INCLUIR}}",
        "CNPJS_RETIRAR":                   "{{CNPJS_RETIRAR}}",
        "BLOCOS_ASSINATURA_ADICIONAIS":    "{{BLOCOS_ASSINATURA_ADICIONAIS}}",
    }

    # Default para campos com valor fixo
    # CONTRATO_ORIGINAL: dinâmico por tipo de produto
    # Maquinona/POS/credenciamento → "DE CREDENCIAMENTO"
    # iFood Benefícios → padrão
    produtos_credenciamento = ["Maquinona", "POS", "maquina", "credenciamento", "pos_machine"]
    tipo_contrato = "CONTRATO DE PRESTAÇÃO DE SERVIÇOS"
    descricao = str(campos.get("description", "") or montagem.get("description", "") or "").lower()
    produto = str(campos.get("PRODUTO", "") or "").lower()
    if any(p in descricao or p in produto for p in ["maquinona", "pos", "credenciamento", "maquina"]):
        tipo_contrato = "CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE CREDENCIAMENTO"

    DEFAULTS = {
        "CONTRATO_ORIGINAL": tipo_contrato,
        "CIDADE_ASSINATURA": "Osasco",
        "BLOCOS_ASSINATURA_ADICIONAIS": "",  # preenchido dinamicamente abaixo
    }

    # Gerar blocos de assinatura para empresas novas (alteracao_cnpjs_grupo)
    cnpjs_incluir = campos.get("CNPJS_INCLUIR")
    if cnpjs_incluir and str(cnpjs_incluir) != "[PENDENTE: CNPJS_INCLUIR]":
        blocos_ass = []
        empresas = cnpjs_incluir if isinstance(cnpjs_incluir, list) else [{"nome": str(cnpjs_incluir)}]
        for emp in empresas:
            nome = emp.get("nome", str(emp)) if isinstance(emp, dict) else str(emp)
            if nome:
                blocos_ass.append(
                    f"_________________________________________________\n"
                    f"{nome}\n"
                    f"Nome: Cargo:"
                )
        if blocos_ass:
            DEFAULTS["BLOCOS_ASSINATURA_ADICIONAIS"] = "\n\n".join(blocos_ass)

    for campo_key, placeholder in mapping.items():
        if campo_key in campos:
            valor = str(campos[campo_key])
            subs[placeholder] = valor if valor else DEFAULTS.get(campo_key, f"[PENDENTE: {campo_key}]")
        else:
            subs[placeholder] = DEFAULTS.get(campo_key, f"[PENDENTE: {campo_key}]")

    # Cidade + data assinatura (combinados)
    cidade = campos.get("CIDADE_ASSINATURA", "Osasco")
    data_aditivo = campos.get("DATA_ADITIVO", "")
    if "{{CIDADE_ASSINATURA}}, {{DATA_ADITIVO}}." in subs:
        subs["{{CIDADE_ASSINATURA}}, {{DATA_ADITIVO}}."] = f"{cidade}, {data_aditivo}."

    return subs


def _montar_substituicoes_modulos(
    modulos_selecionados: list,
    textos_customizados: list = None,
    campos: dict = None,
) -> list:
    """
    Monta UMA ÚNICA substituição: {{ALTERACOES_CONTENT}} → conteúdo montado.
    Concatena apenas os módulos selecionados — zero parágrafos vazios.
    Retorna: [{"find": "{{ALTERACOES_CONTENT}}", "replace": "..."}]
    """
    textos_custom = {t.get("modulo"): t.get("texto_gerado", "") for t in (textos_customizados or [])}
    campos = campos or {}

    blocos = []
    for modulo_id in modulos_selecionados:
        if modulo_id in textos_custom and textos_custom[modulo_id]:
            texto = textos_custom[modulo_id]
        elif modulo_id in TEXTO_MODULOS_FIXOS:
            texto = TEXTO_MODULOS_FIXOS[modulo_id]
        else:
            texto = _texto_modulo_com_campos(modulo_id, campos)

        if texto:
            blocos.append(texto)

    # Juntar módulos com linha em branco entre eles
    conteudo = "\n\n".join(blocos) if blocos else "[Sem alterações contratuais especificadas]"

    return [{"find": "{{ALTERACOES_CONTENT}}", "replace": conteudo}]


def _montar_texto_cnpjs(campos: dict) -> str:
    """
    Monta o texto da cláusula de inclusão/retirada de CNPJs do grupo.
    Usa CNPJS_INCLUIR e CNPJS_RETIRAR do campos_finais do Agente 2.
    Cada item pode ser str ou dict com chaves nome/cnpj/endereco.
    """
    blocos = []
    clausula_num = 1

    # Inclusão de CNPJs
    cnpjs_incluir = campos.get("CNPJS_INCLUIR")
    if cnpjs_incluir and str(cnpjs_incluir) != "[PENDENTE: CNPJS_INCLUIR]":
        if isinstance(cnpjs_incluir, list):
            empresas_str = ""
            for emp in cnpjs_incluir:
                if isinstance(emp, dict):
                    nome = emp.get("nome", "")
                    cnpj = emp.get("cnpj", "")
                    end = emp.get("endereco", "")
                    cep = emp.get("cep", "")
                    linha = f"{nome}, inscrita no CNPJ/MF sob o n.º {cnpj}"
                    if end:
                        linha += f", com sede em {end}"
                    if cep:
                        linha += f", CEP {cep}"
                    empresas_str += f"\n{linha}."
                else:
                    empresas_str += f"\n{emp}."
            bloco = (
                f"1.{clausula_num}. Resolvem as Partes ajustar que, a partir da data de "
                f"assinatura deste instrumento, passará(ão) a compor o Contrato, como "
                f"Parte do Contratante, a(s) seguinte(s) empresa(s) pertencente(s) ao "
                f"grupo empresarial da Empresa:{empresas_str}"
            )
        else:
            bloco = (
                f"1.{clausula_num}. Resolvem as Partes ajustar que, a partir da data de "
                f"assinatura deste instrumento, passará a compor o Contrato, como Parte "
                f"do Contratante, a seguinte empresa pertencente ao grupo empresarial da "
                f"Empresa:\n{cnpjs_incluir}."
            )
        blocos.append(bloco)
        clausula_num += 1

    # Retirada de CNPJs
    cnpjs_retirar = campos.get("CNPJS_RETIRAR")
    if cnpjs_retirar and str(cnpjs_retirar) != "[PENDENTE: CNPJS_RETIRAR]":
        if isinstance(cnpjs_retirar, list):
            empresas_str = "\n".join(
                f"{e.get('nome', e) if isinstance(e, dict) else e}"
                for e in cnpjs_retirar
            )
        else:
            empresas_str = str(cnpjs_retirar)
        bloco = (
            f"1.{clausula_num}. As Partes ajustam que, a partir da data de assinatura "
            f"deste instrumento, deixará(ão) de compor o Contrato, como Parte do "
            f"Contratante, a(s) seguinte(s) empresa(s):\n{empresas_str}."
        )
        blocos.append(bloco)

    if not blocos:
        return "[Módulo alteracao_cnpjs_grupo — CNPJS_INCLUIR e CNPJS_RETIRAR não informados]"

    return "\n\n".join(blocos)


def _texto_modulo_com_campos(modulo_id: str, campos: dict) -> str:
    """Gera texto básico para módulos que precisam de campos específicos."""
    c = campos
    templates = {
        "aviso_previo": (
            f"1.1. As Partes alteram a Cláusula 10.3 dos TCG: "
            f"'10.3. A Empresa poderá solicitar rescisão enviando aviso por escrito com "
            f"no mínimo {c.get('PRAZO_AVISO_PREVIO_DIAS', '[PENDENTE]')} "
            f"({c.get('PRAZO_AVISO_PREVIO_EXTENSO', '[PENDENTE]')}) dias de antecedência.'"
        ),
        "prorrogacao_vigencia": (
            f"1.1. As Partes prorrogam a vigência do Contrato por "
            f"{c.get('PRAZO_MESES', '[PENDENTE]')} "
            f"({c.get('PRAZO_MESES_EXTENSO', '[PENDENTE]')}) meses a partir da assinatura "
            f"deste Aditivo, encerrando-se em {c.get('DATA_NOVA_VIGENCIA', '[PENDENTE]')}."
        ),
        "alteracao_cnpjs_grupo": _montar_texto_cnpjs(c),
        "isa": (
            f"1.1. As Partes acordam em incluir o ISA — Incentivo Saúde Alimentar, "
            f"com valor de R$ {c.get('VALOR_ISA_MENSAL', '[PENDENTE]')}, "
            f"periodicidade {c.get('PERIODICIDADE', '[PENDENTE]')}, "
            f"cumulativo: {c.get('CUMULATIVO', '[PENDENTE]')}, "
            f"início em {c.get('DATA_INICIO_ISA', '[PENDENTE]')}."
        ),
    }
    return templates.get(
        modulo_id,
        f"[Módulo {modulo_id} — texto pendente de customização]"
    )


def preparar_pending_doc(
    ticket_id: str,
    montagem: dict,
    resultado_agente2: dict = None,
) -> Path:
    """
    Salva pending_doc_{ticket_id}.json com todas as substituições necessárias.
    Retornado pelo Planner para geração via MCP tools.
    """
    PENDING_DIR.mkdir(parents=True, exist_ok=True)

    cfg = _load_config()
    template_id = cfg.get("google_docs", {}).get(
        "modelo_aditamento_id", "1FMnV6-U3TNfB1LJVDlQDkVufKB38Hzn3yuswrC4cSfI"
    )
    pasta_id = cfg.get("google_docs", {}).get(
        "drive_folder_id", "1GXGZtSP9LIuKLmAgMXdCcH1cwqi07bh8"
    )

    # Dados do Agente 2 (se disponíveis)
    campos_agente2 = (
        resultado_agente2.get("campos_finais", {}) if resultado_agente2 else {}
    )
    textos_custom = (
        resultado_agente2.get("textos_customizados", []) if resultado_agente2 else []
    )
    modulos = resultado_agente2.get("modulos", {}) if resultado_agente2 else {}
    modulos_selecionados = [
        m for m, info in modulos.items()
        if isinstance(info, dict) and info.get("selecionado", True)
    ]

    if not modulos_selecionados:
        modulos_selecionados = montagem.get("modulos_selecionados", [])

    # Score info
    score_info = (
        resultado_agente2.get("score", {}) if resultado_agente2
        else montagem.get("score", {})
    )
    score_val = (
        score_info.get("score_final", score_info.get("score", 0.0))
        if isinstance(score_info, dict)
        else 0.0
    )
    decisao = (
        score_info.get("decisao", "REVISAO_HUMANA")
        if isinstance(score_info, dict)
        else "REVISAO_HUMANA"
    )

    # Nome do documento
    empresa = (
        campos_agente2.get("RAZAO_SOCIAL")
        or montagem.get("variaveis", {}).get("RAZAO_SOCIAL", {}).get("valor", "Empresa")
    )
    doc_nome = _nome_documento(empresa, ticket_id)

    # Montar substituições
    subs_campos = _montar_substituicoes(montagem, campos_agente2)
    subs_modulos = _montar_substituicoes_modulos(
        modulos_selecionados, textos_custom, campos_agente2
    )

    pending = {
        "ticket_id": ticket_id,
        "template_id": template_id,
        "pasta_id": pasta_id,
        "doc_nome": doc_nome,
        "score": score_val,
        "decisao": decisao,
        "modulos_selecionados": modulos_selecionados,
        "substituicoes_campos": subs_campos,
        "substituicoes_modulos": subs_modulos,
        "comentario_score": (
            f"Pipeline 15-Aditamentos | Score: {score_val:.2f} | Decisão: {decisao} | "
            f"Ticket: {ticket_id} | Módulos: {', '.join(modulos_selecionados)} | "
            f"Agentes Toqan: Leitor-Extrator + Montador-Validador"
        ),
        "status": "aguardando_mcp",
    }

    path = PENDING_DIR / f"{ticket_id}_pending_doc.json"
    path.write_text(json.dumps(pending, ensure_ascii=False, indent=2, default=str))
    logger.info("doc_generator: pending_doc salvo em %s", path)
    return path


def verificar_doc_gerado(ticket_id: str) -> dict | None:
    """
    Verifica se o Planner já gerou o documento para este ticket.
    Retorna dict com doc_id e doc_url, ou None se ainda pendente.
    """
    result_path = RESULTS_DIR / f"{ticket_id}_doc_result.json"
    if result_path.exists():
        return json.loads(result_path.read_text(encoding="utf-8"))
    return None


def gerar_google_doc(
    montagem: dict,
    ticket_id: str,
    resultado_agente2: dict = None,
) -> dict:
    """
    Interface principal — compatível com a assinatura anterior.
    Agora usa o padrão MCP-queue:
      1. Verificar se já foi gerado (doc_result existe)
      2. Se não, salvar pending_doc e retornar status pendente
    """
    # Verificar se já foi gerado
    existente = verificar_doc_gerado(ticket_id)
    if existente and existente.get("doc_id"):
        logger.info(
            "doc_generator: documento já gerado para %s: %s",
            ticket_id, existente["doc_url"]
        )
        return {
            "doc_id": existente["doc_id"],
            "doc_url": existente["doc_url"],
            "doc_nome": existente.get("doc_nome", ""),
            "score": existente.get("score", 0.0),
            "decisao": existente.get("decisao", "REVISAO_HUMANA"),
            "campos_pendentes": existente.get("campos_pendentes", []),
            "status": "gerado",
        }

    # Salvar pending_doc para o Planner processar
    path = preparar_pending_doc(ticket_id, montagem, resultado_agente2)

    empresa = (
        montagem.get("variaveis", {}).get("RAZAO_SOCIAL", {}).get("valor", "Empresa")
    )
    doc_nome = _nome_documento(empresa, ticket_id)

    logger.info(
        "doc_generator: pending_doc salvo — aguardando Planner para gerar doc via MCP. "
        "Arquivo: %s", path
    )

    return {
        "doc_id": None,
        "doc_url": None,
        "doc_nome": doc_nome,
        "pending_doc_path": str(path),
        "score": 0.0,
        "decisao": "PENDENTE_MCP",
        "campos_pendentes": [],
        "status": "pendente_mcp",
        "mensagem": f"pending_doc salvo em {path}. Planner deve processar via MCP tools.",
    }


# Compatibilidade com DocGenerator class legada
class DocGenerator:
    """Wrapper de classe para compatibilidade com pipeline_aditamentos.py legado."""

    def __init__(self, config: dict):
        self.template_id = config.get("google_docs", {}).get(
            "modelo_aditamento_id", "1FMnV6-U3TNfB1LJVDlQDkVufKB38Hzn3yuswrC4cSfI"
        )

    def generate(self, amendment: dict, ticket_data: dict) -> str:
        """
        Compatibilidade com API anterior. Delega para gerar_google_doc().
        Retorna URL do documento gerado ou path do pending_doc.
        """
        ticket_id = ticket_data.get("id") or ticket_data.get("key") or "TICKET"
        resultado = gerar_google_doc(amendment, ticket_id)
        return (
            resultado.get("doc_url")
            or resultado.get("pending_doc_path")
            or "PENDENTE_MCP"
        )
