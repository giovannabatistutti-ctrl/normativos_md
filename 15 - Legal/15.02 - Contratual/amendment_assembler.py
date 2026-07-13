"""
amendment_assembler.py
======================
Agente Montador — seleciona módulos, preenche variáveis e calcula score.
Implementação completa — Fase 4.

Fluxo:
  1. Identificar módulos aplicáveis (DECISION_MAP)
  2. Preencher variáveis (ticket → contrato → PENDENTE)
  3. Verificar regras do DECISION_LAYER
  4. Calcular score via score_engine
  5. Retornar análise estruturada

Módulos sempre presentes: 01_cabecalho, 08_rodape_assinaturas, 09_clausula_geral
Módulos condicionais: selecionados via analise_leitor["produtos"] e
                      analise_leitor["alteracoes_solicitadas"]
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .score_engine import calcular_score

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------

_BASE_DIR = Path(__file__).parent.parent
_MODULOS_DIR = _BASE_DIR / "data" / "templates" / "modulos"

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

# Módulos sempre incluídos em qualquer aditamento
MODULOS_FIXOS = ["01_cabecalho", "08_rodape_assinaturas", "09_clausula_geral"]

# Mapeamento: número do módulo → nome do arquivo (sem .md)
MODULO_ARQUIVO = {
    1:  "01_cabecalho",
    2:  "02_prorrogacao_vigencia",
    3:  "03_retirada_renovacao_automatica",
    4:  "04_aviso_previo",
    5:  "05_cessao",
    6:  "06_alteracao_produto",
    7:  "07_alteracao_valor",
    8:  "08_rodape_assinaturas",
    9:  "09_clausula_geral",
    10: "10_isa",
    11: "11_saldo_extra",
    12: "12_saldo_natal",
}

# Módulos mutuamente exclusivos (grupos)
EXCLUSOES_MUTUAS = [
    {2, 3},
    {2, 4},
    {3, 4},
]

# Campos obrigatórios globais e sua pergunta PENDENTE
CAMPOS_OBRIGATORIOS_GLOBAIS = {
    "RAZAO_SOCIAL":           "Qual a razão social completa da empresa (CONTRATANTE)?",
    "CNPJ_EMPRESA":           "Qual o CNPJ da empresa no formato XX.XXX.XXX/XXXX-XX?",
    "ENDERECO_EMPRESA":       "Qual o endereço completo da empresa (logradouro, número, bairro, cidade/UF)?",
    "CEP_EMPRESA":            "Qual o CEP da empresa no formato XX.XXX-XXX?",
    "DATA_CONTRATO_ORIGINAL": "Qual a data de assinatura do contrato original (formato: DD de MMMM de AAAA)?",
    "DATA_ADITIVO":           "Qual a data de assinatura deste Aditivo (formato: DD de MMMM de AAAA)?",
}

# Terminologia canônica: termo_proibido → termo_canônico
TERMINOLOGIA_CANONICA: Dict[str, str] = {
    "saldo saúde alimentar":       "ISA",
    "saldo alimentação saudável":  "ISA",
    "incentivo alimentar":         "ISA",
    "vale refeição":               "iFood Refeição",
    "vr ifood":                    "iFood Refeição",
    "refeição ifood":              "iFood Refeição",
    "vale alimentação":            "iFood Alimentação",
    "va ifood":                    "iFood Alimentação",
    "alimentação ifood":           "iFood Alimentação",
    "benefício natal":             "Saldo Natal",
    "crédito natal":               "Saldo Natal",
    "benefício extra":             "Saldo Extra",
    "crédito extra":               "Saldo Extra",
    "colab plus":                  "Programa Colab+",
    "ifood pago":                  "iFood Pago IP",
    "ifood pagamentos":            "iFood Pago IP",
    "zoop":                        "iFood Pago IP",
}

# Palavras-chave de módulos condicionais
KEYWORDS_MODULO: Dict[str, List[str]] = {
    "02_prorrogacao_vigencia":         ["prorrog", "vigência", "prazo"],
    "03_retirada_renovacao_automatica":["retira", "remove", "renovação automática", "sem renovação"],
    "04_aviso_previo":                 ["aviso prévio", "rescisão", "prazo de aviso"],
    "05_cessao":                       ["cessão", "cláusula 16.6", "cessao"],
    "06_alteracao_produto":            ["produto", "alteração de produto", "troca de produto"],
    "07_alteracao_valor":              ["valor", "faturamento", "item viii", "atualização de valor"],
    "10_isa":                          ["isa", "incentivo saúde alimentar", "saldo alimentar"],
    "11_saldo_extra":                  ["saldo extra", "benefício extra", "crédito extra"],
    "12_saldo_natal":                  ["saldo natal", "natal", "benefício natal"],
}


# ---------------------------------------------------------------------------
# Função principal pública
# ---------------------------------------------------------------------------

def montar_aditamento(
    ticket: dict,
    contrato: dict,
    analise_leitor: dict,
) -> dict:
    """
    Monta o aditamento completo.

    Args:
        ticket: dados do ticket Jira (summary, description, empresa, cnpj,
                modulos_solicitados, proposta_comercial_isa, etc.)
        contrato: cláusulas extraídas do contrato (data_assinatura_original,
                  aviso_previo_clausula_10_3, cnpjs_grupo, tem_colabmais, etc.)
        analise_leitor: análise do contract_reader / jira_reader com
                        produtos, alteracoes_solicitadas, etc.

    Returns:
        dict com modulos_selecionados, variaveis, texto_consolidado,
        campos_pendentes, perguntas_para_advogado, score, modulos_md,
        terminologia_corrigida.
    """
    logger.info("amendment_assembler.montar_aditamento() — iniciando")

    regras_violadas: List[str] = []
    terminologia_corrigida: List[Dict[str, str]] = []

    # -----------------------------------------------------------------------
    # 1. Identificar módulos aplicáveis
    # -----------------------------------------------------------------------
    modulos_selecionados = _selecionar_modulos(ticket, analise_leitor)

    # Verificar exclusões mútuas (REGRA-06)
    conflito = _verificar_exclusoes_mutuas(modulos_selecionados)
    if conflito:
        regras_violadas.append("REGRA-06")
        logger.warning("Módulos mutuamente exclusivos detectados: %s", conflito)

    # -----------------------------------------------------------------------
    # 2. Verificar regras do DECISION_LAYER
    # -----------------------------------------------------------------------
    campos_pendentes_regras: List[str] = []

    # REGRA-01: ISA exige Proposta Comercial
    if "10_isa" in modulos_selecionados:
        if not ticket.get("proposta_comercial_isa"):
            campos_pendentes_regras.append("PROPOSTA_COMERCIAL_ISA")
            regras_violadas.append("REGRA-01")

    # REGRA-05: ISA + Saldo Natal → documento único consolidado
    duplo_aditamento = "10_isa" in modulos_selecionados and "12_saldo_natal" in modulos_selecionados
    if duplo_aditamento:
        logger.info("Duplo aditamento ISA + Saldo Natal → documento único consolidado (REGRA-05)")

    # REGRA-10: Colab+ exige confirmação de presença no contrato
    if "09_clausula_geral" in modulos_selecionados and ticket.get("remover_colabmais"):
        if contrato.get("tem_colabmais") is None:
            campos_pendentes_regras.append("CONFIRMACAO_COLABMAIS")
            regras_violadas.append("REGRA-10")

    # -----------------------------------------------------------------------
    # 3. Preencher variáveis
    # -----------------------------------------------------------------------
    variaveis = _preencher_variaveis(ticket, contrato, modulos_selecionados, analise_leitor)

    # -----------------------------------------------------------------------
    # 4. Coletar todos os campos PENDENTES
    # -----------------------------------------------------------------------
    campos_pendentes = _extrair_pendentes(variaveis)
    campos_pendentes = list(set(campos_pendentes + campos_pendentes_regras))

    # -----------------------------------------------------------------------
    # 5. Verificar terminologia canônica
    # -----------------------------------------------------------------------
    texto_raw = _montar_texto_consolidado_raw(modulos_selecionados, variaveis)
    texto_consolidado, terminologia_corrigida = _aplicar_terminologia_canonica(texto_raw)
    if terminologia_corrigida:
        regras_violadas.append("REGRA-04")
        logger.warning(
            "Terminologia não-canônica detectada e corrigida: %s",
            terminologia_corrigida,
        )

    # -----------------------------------------------------------------------
    # 6. Verificar REGRA-09 — CNPJ válido
    # -----------------------------------------------------------------------
    cnpj_raw = _get_val(variaveis, "CNPJ_EMPRESA")
    if cnpj_raw and "PENDENTE:" not in cnpj_raw:
        if not _validar_cnpj(cnpj_raw):
            campos_pendentes.append("CNPJ_EMPRESA_INVALIDO")
            regras_violadas.append("REGRA-09")

    # -----------------------------------------------------------------------
    # 7. Ler conteúdo dos módulos (com variáveis preenchidas)
    # -----------------------------------------------------------------------
    modulos_md = _carregar_modulos_md(modulos_selecionados, variaveis)

    # -----------------------------------------------------------------------
    # 8. Perguntas formatadas para o advogado (campos PENDENTES)
    # -----------------------------------------------------------------------
    perguntas_para_advogado = _formatar_perguntas(campos_pendentes, variaveis, ticket)

    # -----------------------------------------------------------------------
    # 9. Calcular score
    # -----------------------------------------------------------------------
    analise_para_score = {
        "campos_pendentes": campos_pendentes,
        "variaveis": variaveis,
        "modulos_selecionados": modulos_selecionados,
        "regras_violadas": regras_violadas,
        "ticket": ticket,
        "modulos_md": modulos_md,
    }
    score = calcular_score(analise_para_score)

    return {
        "modulos_selecionados": modulos_selecionados,
        "variaveis": variaveis,
        "texto_consolidado": texto_consolidado,
        "campos_pendentes": campos_pendentes,
        "perguntas_para_advogado": perguntas_para_advogado,
        "score": score,
        "modulos_md": modulos_md,
        "terminologia_corrigida": terminologia_corrigida,
        "regras_violadas": regras_violadas,
        "duplo_aditamento_consolidado": duplo_aditamento,
    }


# ---------------------------------------------------------------------------
# 1. Seleção de módulos
# ---------------------------------------------------------------------------

def _selecionar_modulos(ticket: dict, analise_leitor: dict) -> List[str]:
    """
    Seleciona módulos aplicáveis combinando:
      - módulos fixos (cabecalho, rodape, clausula_geral)
      - módulos explicitamente solicitados no ticket
      - módulos inferidos dos produtos e alterações solicitadas
    """
    modulos: List[str] = list(MODULOS_FIXOS)

    # Módulos explicitamente solicitados no ticket (como IDs numéricos ou nomes)
    solicitados = ticket.get("modulos_solicitados", []) or []
    for m in solicitados:
        nome = _resolver_modulo(m)
        if nome and nome not in modulos:
            modulos.append(nome)

    # Módulos inferidos de produtos
    produtos = analise_leitor.get("produtos", []) or []
    for produto in produtos:
        nome = _modulo_por_produto(produto)
        if nome and nome not in modulos:
            modulos.append(nome)

    # Módulos inferidos de alterações solicitadas
    alteracoes = analise_leitor.get("alteracoes_solicitadas", []) or []
    texto_alteracoes = " ".join(str(a) for a in alteracoes).lower()
    texto_summary = (ticket.get("summary", "") or "").lower()
    texto_descricao = (ticket.get("description", "") or "").lower()
    texto_tudo = texto_alteracoes + " " + texto_summary + " " + texto_descricao

    for nome_mod, keywords in KEYWORDS_MODULO.items():
        if nome_mod not in modulos:
            for kw in keywords:
                if kw.lower() in texto_tudo:
                    modulos.append(nome_mod)
                    break

    return modulos


def _resolver_modulo(m: Any) -> Optional[str]:
    """Resolve um módulo por ID inteiro ou nome de arquivo."""
    if isinstance(m, int):
        return MODULO_ARQUIVO.get(m)
    if isinstance(m, str):
        if m.isdigit():
            return MODULO_ARQUIVO.get(int(m))
        nome_base = m.replace(".md", "")
        if nome_base in MODULO_ARQUIVO.values():
            return nome_base
    return None


def _modulo_por_produto(produto: str) -> Optional[str]:
    """Mapeia produto específico para módulo correspondente."""
    mapa = {
        "ISA":         "10_isa",
        "Saldo Extra": "11_saldo_extra",
        "Saldo Natal": "12_saldo_natal",
    }
    return mapa.get(produto)


def _verificar_exclusoes_mutuas(modulos: List[str]) -> Optional[set]:
    """Retorna o par conflitante se houver, None caso contrário."""
    # Mapear nomes para IDs numéricos
    ids_numericos = set()
    arquivo_para_id = {v: k for k, v in MODULO_ARQUIVO.items()}
    for m in modulos:
        nid = arquivo_para_id.get(m)
        if nid:
            ids_numericos.add(nid)

    for par in EXCLUSOES_MUTUAS:
        if par.issubset(ids_numericos):
            return par
    return None


# ---------------------------------------------------------------------------
# 2. Preenchimento de variáveis
# ---------------------------------------------------------------------------

def _preencher_variaveis(ticket: dict, contrato: dict, modulos: List[str], analise_leitor: Optional[dict] = None) -> dict:
    """
    Preenche todas as variáveis do aditamento.
    Fonte primária: ticket. Fonte secundária: contrato.
    Campo ausente → {{PENDENTE: [pergunta]}}.
    """
    variaveis: Dict[str, Dict[str, str]] = {}

    def _v(campo: str, valor: Any, fonte: str) -> None:
        """Registra variável com valor e fonte."""
        variaveis[campo] = {"valor": str(valor) if valor is not None else "", "fonte": fonte}

    def _pend(campo: str, pergunta: str) -> None:
        """Registra variável como PENDENTE."""
        variaveis[campo] = {
            "valor": f"{{{{PENDENTE: {pergunta}}}}}",
            "fonte": "PENDENTE",
        }

    def _get_ou_pend(campo: str, pergunta: str, *fontes: Tuple[Any, str]) -> None:
        """Tenta preencher campo das fontes em ordem; se não encontrar, marca PENDENTE."""
        for valor, fonte in fontes:
            if valor:
                _v(campo, valor, fonte)
                return
        _pend(campo, pergunta)

    # -----------------------------------------------------------------------
    # Variáveis globais (todos os módulos)
    # -----------------------------------------------------------------------
    _get_ou_pend(
        "RAZAO_SOCIAL",
        CAMPOS_OBRIGATORIOS_GLOBAIS["RAZAO_SOCIAL"],
        (ticket.get("empresa"), f"campo empresa do ticket {ticket.get('key', '')}"),
        (ticket.get("razao_social"), f"campo razao_social do ticket {ticket.get('key', '')}"),
        (contrato.get("razao_social"), "contrato anexo — seção de partes"),
    )

    cnpj_bruto = ticket.get("cnpj_empresa") or ticket.get("cnpj") or contrato.get("cnpj")
    if cnpj_bruto:
        _v("CNPJ_EMPRESA", cnpj_bruto, f"campo cnpj do ticket {ticket.get('key', '')}")
    else:
        _pend("CNPJ_EMPRESA", CAMPOS_OBRIGATORIOS_GLOBAIS["CNPJ_EMPRESA"])

    _get_ou_pend(
        "ENDERECO_EMPRESA",
        CAMPOS_OBRIGATORIOS_GLOBAIS["ENDERECO_EMPRESA"],
        (ticket.get("endereco"), f"campo endereco do ticket {ticket.get('key', '')}"),
        (contrato.get("endereco"), "contrato anexo — Item VIII do Formulário"),
    )

    _get_ou_pend(
        "CEP_EMPRESA",
        CAMPOS_OBRIGATORIOS_GLOBAIS["CEP_EMPRESA"],
        (ticket.get("cep"), f"campo cep do ticket {ticket.get('key', '')}"),
        (contrato.get("cep"), "contrato anexo — Item VIII do Formulário"),
    )

    _get_ou_pend(
        "DATA_CONTRATO_ORIGINAL",
        CAMPOS_OBRIGATORIOS_GLOBAIS["DATA_CONTRATO_ORIGINAL"],
        (contrato.get("data_assinatura_original"), "contrato anexo — data de assinatura"),
        (ticket.get("data_contrato_original"), f"campo data_contrato_original do ticket {ticket.get('key', '')}"),
    )

    _get_ou_pend(
        "DATA_ADITIVO",
        CAMPOS_OBRIGATORIOS_GLOBAIS["DATA_ADITIVO"],
        (ticket.get("data_aditivo"), f"campo data_aditivo do ticket {ticket.get('key', '')}"),
        (ticket.get("data_assinatura"), f"campo data_assinatura do ticket {ticket.get('key', '')}"),
    )

    # Cidade de assinatura — default "Osasco"
    _v("CIDADE_ASSINATURA",
       ticket.get("cidade_assinatura") or "Osasco",
       ticket.get("cidade_assinatura") and f"campo cidade_assinatura do ticket {ticket.get('key', '')}" or "default")

    # Representante legal (cabeçalho)
    _get_ou_pend(
        "REPRESENTANTE_LEGAL",
        "Qual o nome completo do representante legal da empresa (CONTRATANTE)?",
        (ticket.get("representante_legal"), f"campo representante_legal do ticket {ticket.get('key', '')}"),
        (contrato.get("representante_legal"), "contrato anexo — seção de partes"),
    )

    _get_ou_pend(
        "CPF_REPRESENTANTE",
        "Qual o CPF do representante legal da empresa (formato XXX.XXX.XXX-XX)?",
        (ticket.get("cpf_representante"), f"campo cpf_representante do ticket {ticket.get('key', '')}"),
        (contrato.get("cpf_representante"), "contrato anexo — seção de partes"),
    )

    # Número do contrato original
    _get_ou_pend(
        "NUMERO_CONTRATO",
        "Qual o número/identificador do contrato original?",
        (ticket.get("numero_contrato"), f"campo numero_contrato do ticket {ticket.get('key', '')}"),
        (contrato.get("numero_contrato"), "contrato anexo"),
    )

    # -----------------------------------------------------------------------
    # Rodapé de assinaturas
    # -----------------------------------------------------------------------
    _get_ou_pend(
        "NOME_REPRESENTANTE_IFOOD",
        "Qual o nome do representante do iFood Benefícios que assina o aditivo?",
        (ticket.get("nome_representante_ifood"), f"campo nome_representante_ifood do ticket {ticket.get('key', '')}"),
    )

    _get_ou_pend(
        "CARGO_REPRESENTANTE_IFOOD",
        "Qual o cargo do representante do iFood Benefícios que assina o aditivo?",
        (ticket.get("cargo_representante_ifood"), f"campo cargo_representante_ifood do ticket {ticket.get('key', '')}"),
    )

    # Data de assinatura para rodapé
    if "DATA_ADITIVO" in variaveis and "PENDENTE:" not in variaveis["DATA_ADITIVO"]["valor"]:
        _v("DATA_ASSINATURA", variaveis["DATA_ADITIVO"]["valor"],
           "derivado de DATA_ADITIVO")
    else:
        _pend("DATA_ASSINATURA",
              "Qual a data de assinatura do aditivo (formato: DD de MMMM de AAAA)?")

    cidade = variaveis.get("CIDADE_ASSINATURA", {}).get("valor", "Osasco")
    _v("CIDADE", cidade, variaveis.get("CIDADE_ASSINATURA", {}).get("fonte", "default"))

    # -----------------------------------------------------------------------
    # Variáveis por módulo condicional
    # -----------------------------------------------------------------------

    # Módulo 02 — Prorrogação de Vigência
    if "02_prorrogacao_vigencia" in modulos:
        _get_ou_pend(
            "DATA_NOVA_VIGENCIA",
            "Qual a nova data de vigência do contrato após a prorrogação (formato: DD de MMMM de AAAA)?",
            (ticket.get("data_nova_vigencia"), f"campo data_nova_vigencia do ticket {ticket.get('key', '')}"),
        )
        _get_ou_pend(
            "PRAZO_MESES",
            "Por quantos meses o contrato será prorrogado?",
            (ticket.get("prazo_meses"), f"campo prazo_meses do ticket {ticket.get('key', '')}"),
        )
        if "PRAZO_MESES" in variaveis and "PENDENTE:" not in variaveis["PRAZO_MESES"]["valor"]:
            try:
                n = int(variaveis["PRAZO_MESES"]["valor"])
                _v("PRAZO_MESES_EXTENSO", _numero_por_extenso(n), "gerado automaticamente de PRAZO_MESES")
            except (ValueError, TypeError):
                _pend("PRAZO_MESES_EXTENSO", "Prazo em meses por extenso (ex: doze)")

    # Módulo 04 — Aviso Prévio
    if "04_aviso_previo" in modulos:
        aviso_dias = ticket.get("aviso_previo_dias")
        aviso_original = contrato.get("aviso_previo_clausula_10_3")

        if aviso_dias:
            try:
                aviso_int = int(aviso_dias)
                if aviso_original and aviso_int >= int(aviso_original):
                    logger.warning(
                        "REGRA-03: aviso prévio negociado (%d) >= original (%s)", aviso_int, aviso_original
                    )
                _v("PRAZO_AVISO_PREVIO_DIAS", str(aviso_int),
                   f"campo aviso_previo_dias do ticket {ticket.get('key', '')}")
                _v("PRAZO_AVISO_PREVIO_EXTENSO", _numero_por_extenso(aviso_int), "gerado automaticamente")
            except (ValueError, TypeError):
                _pend("PRAZO_AVISO_PREVIO_DIAS",
                      "Quantos dias de aviso prévio foram negociados? (número inteiro positivo)")
        else:
            _pend("PRAZO_AVISO_PREVIO_DIAS",
                  "Qual o prazo de aviso prévio negociado (número inteiro de dias)?")
            _pend("PRAZO_AVISO_PREVIO_EXTENSO",
                  "Prazo por extenso gerado automaticamente após informar PRAZO_AVISO_PREVIO_DIAS.")

    # Módulo 05 — Cessão (Cláusula 16.6) — versão ASSIMÉTRICA (DECISION_LAYER)
    if "05_cessao" in modulos:
        # REGRA: Versão assimétrica — iFood pode ceder; Empresa precisa de anuência
        _v(
            "CLAUSULA_CESSAO_TIPO",
            "assimetrica",
            "DECISION_LAYER — Cláusula 16.6 sempre usa versão assimétrica: iFood pode ceder livremente; Empresa precisa de anuência expressa.",
        )

        # Módulo 06 — Alteração de Produto
    if "06_alteracao_produto" in modulos:
        _get_ou_pend(
            "PRODUTO_NOVO",
            "Qual o novo produto a ser incluído/alterado (nomenclatura oficial iFood Benefícios)?",
            (ticket.get("produto_novo"), f"campo produto_novo do ticket {ticket.get('key', '')}"),
        )
        _get_ou_pend(
            "VALOR_BENEFICIO",
            "Qual o valor do benefício por usuário/mês (em R$)?",
            (ticket.get("valor_beneficio"), f"campo valor_beneficio do ticket {ticket.get('key', '')}"),
        )
        _get_ou_pend(
            "DATA_VIGENCIA_PRODUTO",
            "Qual a data de vigência do novo produto (formato: DD de MMMM de AAAA)?",
            (ticket.get("data_vigencia_produto"), f"campo data_vigencia_produto do ticket {ticket.get('key', '')}"),
        )

    # Módulo 07 — Alteração de Valor
    if "07_alteracao_valor" in modulos:
        _get_ou_pend(
            "PRODUTO",
            "Qual o produto cujo valor será alterado?",
            (ticket.get("produto"), f"campo produto do ticket {ticket.get('key', '')}"),
            (analise_leitor.get("produto_principal"), "analise_leitor — produto_principal"),
        )
        _get_ou_pend(
            "VALOR_ANTERIOR",
            "Qual o valor anterior do benefício (conforme contrato atual, em R$)?",
            (ticket.get("valor_anterior"), f"campo valor_anterior do ticket {ticket.get('key', '')}"),
            (contrato.get("valor_beneficio_atual"), "contrato anexo — Item VIII"),
        )
        _get_ou_pend(
            "VALOR_NOVO",
            "Qual o novo valor do benefício (em R$)?",
            (ticket.get("valor_novo"), f"campo valor_novo do ticket {ticket.get('key', '')}"),
        )
        _get_ou_pend(
            "DATA_VIGENCIA_NOVO_VALOR",
            "A partir de qual data o novo valor entra em vigor (formato: DD de MMMM de AAAA)?",
            (ticket.get("data_vigencia_novo_valor"), f"campo data_vigencia_novo_valor do ticket {ticket.get('key', '')}"),
        )

    # Módulo 10 — ISA
    if "10_isa" in modulos:
        _get_ou_pend(
            "VALOR_ISA_MENSAL",
            "Qual o valor do ISA por usuário/período (conforme Proposta Comercial ISA)?",
            (ticket.get("valor_isa_mensal"), f"campo valor_isa_mensal do ticket {ticket.get('key', '')}"),
        )
        _get_ou_pend(
            "PERIODICIDADE",
            "Qual a periodicidade do ISA? ('mensal' ou 'semestral' — conforme Proposta Comercial)",
            (ticket.get("periodicidade_isa"), f"campo periodicidade_isa do ticket {ticket.get('key', '')}"),
        )
        _get_ou_pend(
            "CUMULATIVO",
            "O saldo ISA é cumulativo entre períodos? ('sim' ou 'não' — conforme Proposta Comercial)",
            (ticket.get("isa_cumulativo"), f"campo isa_cumulativo do ticket {ticket.get('key', '')}"),
        )
        _get_ou_pend(
            "DATA_INICIO_ISA",
            "Qual a data de início do ISA (formato: DD de MMMM de AAAA)?",
            (ticket.get("data_inicio_isa"), f"campo data_inicio_isa do ticket {ticket.get('key', '')}"),
        )
        _get_ou_pend(
            "FORMA_PAGAMENTO",
            "Qual a forma de pagamento/crédito do ISA (ex: crédito em carteira digital)?",
            (ticket.get("forma_pagamento_isa"), f"campo forma_pagamento_isa do ticket {ticket.get('key', '')}"),
        )
        # PROPOSTA_COMERCIAL_ISA — pré-condição
        if not ticket.get("proposta_comercial_isa"):
            _pend(
                "PROPOSTA_COMERCIAL_ISA",
                "A Proposta Comercial ISA não foi localizada nos anexos do ticket. "
                "Por favor, anexe o documento antes do processamento.",
            )
        else:
            _v("PROPOSTA_COMERCIAL_ISA", "Anexada", f"anexo do ticket {ticket.get('key', '')}")

    # Módulo 11 — Saldo Extra
    if "11_saldo_extra" in modulos:
        _get_ou_pend(
            "VALOR_SALDO_EXTRA",
            "Qual o valor do Saldo Extra por usuário elegível (em R$)?",
            (ticket.get("valor_saldo_extra"), f"campo valor_saldo_extra do ticket {ticket.get('key', '')}"),
        )
        _get_ou_pend(
            "DATA_CREDITO",
            "Qual a data de crédito do Saldo Extra (formato: DD de MMMM de AAAA)?",
            (ticket.get("data_credito_saldo_extra"), f"campo data_credito_saldo_extra do ticket {ticket.get('key', '')}"),
        )
        _get_ou_pend(
            "DESCRICAO_OCASIAO",
            "Qual a ocasião/finalidade do Saldo Extra (ex: aniversário da empresa)?",
            (ticket.get("descricao_ocasiao"), f"campo descricao_ocasiao do ticket {ticket.get('key', '')}"),
        )
        _get_ou_pend(
            "PUBLICO_ELEGIVEL",
            "Quais colaboradores são elegíveis para receber o Saldo Extra?",
            (ticket.get("publico_elegivel"), f"campo publico_elegivel do ticket {ticket.get('key', '')}"),
        )

    # Módulo 12 — Saldo Natal (REGRA-02: incluir cláusula de responsabilidade do cliente)
    if "12_saldo_natal" in modulos:
        _get_ou_pend(
            "VALOR_SALDO_NATAL",
            "Qual o valor do Saldo Natal por usuário elegível (em R$)?",
            (ticket.get("valor_saldo_natal"), f"campo valor_saldo_natal do ticket {ticket.get('key', '')}"),
        )
        _get_ou_pend(
            "ANO_REFERENCIA",
            "A qual ano-calendário se refere o Saldo Natal (formato AAAA)?",
            (ticket.get("ano_referencia_natal"), f"campo ano_referencia_natal do ticket {ticket.get('key', '')}"),
        )
        _get_ou_pend(
            "DATA_CREDITO_NATAL",
            "Qual a data de crédito do Saldo Natal na plataforma (formato: DD de MMMM de AAAA)?",
            (ticket.get("data_credito_natal"), f"campo data_credito_natal do ticket {ticket.get('key', '')}"),
        )
        # Cláusula de responsabilidade pós-mai/2025 — sempre presente (REGRA-02)
        _v(
            "CLAUSULA_RESPONSABILIDADE_NATAL",
            (
                "A responsabilidade pela distribuição do Saldo Natal aos usuários finais é "
                "exclusivamente da Empresa (cliente), não cabendo ao iFood Benefícios qualquer "
                "obrigação de distribuição."
            ),
            "DECISION_LAYER REGRA-02 — obrigatório pós-mai/2025",
        )

    return variaveis


# ---------------------------------------------------------------------------
# 3. Terminologia canônica
# ---------------------------------------------------------------------------

def _aplicar_terminologia_canonica(texto: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Detecta e corrige termos não-canônicos no texto.
    Retorna (texto_corrigido, lista_de_correcoes).
    """
    correcoes: List[Dict[str, str]] = []
    texto_corrigido = texto

    for termo_proibido, termo_canonico in TERMINOLOGIA_CANONICA.items():
        padrao = re.compile(re.escape(termo_proibido), re.IGNORECASE)
        ocorrencias = padrao.findall(texto_corrigido)
        if ocorrencias:
            for ocorrencia in set(ocorrencias):
                correcoes.append({"original": ocorrencia, "canonica": termo_canonico})
            texto_corrigido = padrao.sub(termo_canonico, texto_corrigido)

    return texto_corrigido, correcoes


# ---------------------------------------------------------------------------
# 4. Montagem do texto consolidado
# ---------------------------------------------------------------------------

def _montar_texto_consolidado_raw(modulos: List[str], variaveis: dict) -> str:
    """
    Lê os arquivos de módulo, substitui variáveis e concatena em texto único.
    """
    partes: List[str] = []

    for nome_mod in modulos:
        caminho = _MODULOS_DIR / f"{nome_mod}.md"
        if not caminho.exists():
            logger.warning("Arquivo de módulo não encontrado: %s", caminho)
            partes.append(f"\n<!-- MÓDULO {nome_mod} NÃO ENCONTRADO -->\n")
            continue

        texto = caminho.read_text(encoding="utf-8")

        # Remover frontmatter YAML (--- ... ---)
        texto = re.sub(r"^---\n.*?\n---\n", "", texto, flags=re.DOTALL)

        # Substituir variáveis {{VAR}} pelo valor preenchido
        for campo, info in variaveis.items():
            valor = info.get("valor", "") if isinstance(info, dict) else str(info)
            texto = texto.replace(f"{{{{{campo}}}}}", valor)

        partes.append(texto.strip())

    return "\n\n---\n\n".join(partes)


def _carregar_modulos_md(modulos: List[str], variaveis: dict) -> List[str]:
    """Retorna lista com conteúdo de cada módulo após preenchimento."""
    resultado: List[str] = []

    for nome_mod in modulos:
        caminho = _MODULOS_DIR / f"{nome_mod}.md"
        if not caminho.exists():
            resultado.append(f"<!-- MÓDULO {nome_mod} NÃO ENCONTRADO -->")
            continue

        texto = caminho.read_text(encoding="utf-8")
        texto = re.sub(r"^---\n.*?\n---\n", "", texto, flags=re.DOTALL)

        for campo, info in variaveis.items():
            valor = info.get("valor", "") if isinstance(info, dict) else str(info)
            texto = texto.replace(f"{{{{{campo}}}}}", valor)

        resultado.append(texto.strip())

    return resultado


# ---------------------------------------------------------------------------
# 5. Campos PENDENTES e perguntas
# ---------------------------------------------------------------------------

def _extrair_pendentes(variaveis: dict) -> List[str]:
    """Retorna lista de campos PENDENTES (nome da variável)."""
    return [
        campo for campo, info in variaveis.items()
        if isinstance(info, dict) and "PENDENTE:" in info.get("valor", "")
    ]


def _formatar_perguntas(
    campos_pendentes: List[str],
    variaveis: dict,
    ticket: dict,
) -> List[str]:
    """
    Formata perguntas para postar no Jira ao advogado.
    Inclui contexto do ticket.
    """
    if not campos_pendentes:
        return []

    ticket_key = ticket.get("key", "N/A")
    perguntas: List[str] = [
        f"*Campos pendentes no ticket {ticket_key} — aguardando resposta do advogado:*"
    ]

    for campo in campos_pendentes:
        info = variaveis.get(campo, {})
        if isinstance(info, dict):
            valor = info.get("valor", "")
            # Extrair texto da pergunta do marcador PENDENTE
            match = re.search(r"\{\{PENDENTE:\s*(.+?)\}\}", valor, re.DOTALL)
            pergunta = match.group(1).strip() if match else f"Informar {campo}"
        else:
            pergunta = f"Informar {campo}"

        perguntas.append(f"  • *{campo}*: {pergunta}")

    return perguntas


# ---------------------------------------------------------------------------
# 6. Helpers
# ---------------------------------------------------------------------------

def _get_val(variaveis: dict, campo: str) -> Optional[str]:
    """Retorna o valor de uma variável ou None."""
    info = variaveis.get(campo)
    if isinstance(info, dict):
        return info.get("valor")
    return None


def _numero_por_extenso(n: int) -> str:
    """Converte inteiro (0-999) para texto em português."""
    unidades = [
        "", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove",
        "dez", "onze", "doze", "treze", "quatorze", "quinze", "dezesseis",
        "dezessete", "dezoito", "dezenove",
    ]
    dezenas = [
        "", "", "vinte", "trinta", "quarenta", "cinquenta",
        "sessenta", "setenta", "oitenta", "noventa",
    ]
    centenas = [
        "", "cem", "duzentos", "trezentos", "quatrocentos",
        "quinhentos", "seiscentos", "setecentos", "oitocentos", "novecentos",
    ]

    if n == 0:
        return "zero"
    if n < 0 or n >= 1000:
        return str(n)

    partes: List[str] = []

    if n >= 100:
        c = n // 100
        resto = n % 100
        if resto == 0:
            partes.append(centenas[c])
        else:
            partes.append(centenas[c].replace("cem", "cento") if c == 1 else centenas[c])
        n = resto

    if n >= 20:
        d = n // 10
        u = n % 10
        partes.append(dezenas[d])
        if u:
            partes.append(unidades[u])
    elif n > 0:
        partes.append(unidades[n])

    return " e ".join(partes)


def _validar_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ brasileiro (dígitos verificadores).
    Aceita formatos: XX.XXX.XXX/XXXX-XX ou apenas dígitos.
    """
    apenas_digitos = re.sub(r"\D", "", cnpj)
    if len(apenas_digitos) != 14:
        return False
    if len(set(apenas_digitos)) == 1:
        return False

    def _calc_digito(nums: str, pesos: List[int]) -> int:
        total = sum(int(d) * p for d, p in zip(nums, pesos))
        resto = total % 11
        return 0 if resto < 2 else 11 - resto

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    d1 = _calc_digito(apenas_digitos[:12], pesos1)
    d2 = _calc_digito(apenas_digitos[:13], pesos2)

    return apenas_digitos[12] == str(d1) and apenas_digitos[13] == str(d2)


# ---------------------------------------------------------------------------
# Compatibilidade com classe legada AmendmentAssembler (Fase 3)
# ---------------------------------------------------------------------------

class AmendmentAssembler:
    """Wrapper de classe para compatibilidade com pipeline_aditamentos.py."""

    def __init__(self, config: dict):
        self.config = config

    def assemble(self, ticket_data: dict, contract_data: dict) -> dict:
        """Delega para montar_aditamento() com analise_leitor mínimo."""
        analise_leitor = {
            "produtos": ticket_data.get("produtos", []),
            "alteracoes_solicitadas": ticket_data.get("alteracoes_solicitadas", []),
        }
        return montar_aditamento(ticket_data, contract_data, analise_leitor)
