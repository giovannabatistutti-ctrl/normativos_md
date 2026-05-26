"""
Módulo 5 — responsaveis.py
Mapeia as áreas e times responsáveis por cada normativo com base no tema, políticas
impactadas e segmento (B2C/B2B).

Entradas:
    normativo (Normativo): Normativo capturado.
    classificacao (ClassificacaoNormativo): Resultado do reasoning (com políticas impactadas).
    avaliacao (AvaliacaoRisco): Resultado da avaliação de risco.
    config (dict): Configuração do config.json.

Saídas:
    List[Responsavel]: Lista de responsáveis com área, time e ação sugerida.

Uso:
    from modules.responsaveis import mapear_responsaveis
    responsaveis = mapear_responsaveis(normativo, classificacao, avaliacao)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .captura import Normativo
from .reasoning import ClassificacaoNormativo
from .avaliacao_risco import AvaliacaoRisco


@dataclass
class Responsavel:
    """Responsável pelo acompanhamento e adequação ao normativo."""
    area: str           # Área principal (ex: "Compliance", "Tecnologia", "Produtos")
    time: str           # Time específico (ex: "PLD/FT", "Pix", "Cartões")
    acao: str           # Ação requerida
    prioridade: str     # ALTA / MÉDIA / BAIXA
    segmento: str       # B2C / B2B / AMBOS / N/A


# ─── Mapa tema → responsáveis ──────────────────────────────────────────────────

MAPA_TEMA_RESPONSAVEL = {
    # PLD/FT
    "pld": {"area": "Compliance", "time": "PLD/FT", "acao": "Revisar política e procedimentos de PLD/FT"},
    "prevenção à lavagem": {"area": "Compliance", "time": "PLD/FT", "acao": "Revisar política e procedimentos de PLD/FT"},
    "financiamento ao terrorismo": {"area": "Compliance", "time": "PLD/FT", "acao": "Revisar política de PLD/FT"},
    "coaf": {"area": "Compliance", "time": "PLD/FT", "acao": "Verificar obrigações COAF e atualizar procedimentos"},

    # Pix
    "pix": {"area": "Produtos", "time": "Pix", "acao": "Avaliar impacto no produto Pix e adequações necessárias"},
    "arranjo de pagamento": {"area": "Produtos", "time": "Arranjos de Pagamento", "acao": "Verificar conformidade do arranjo"},

    # Open Finance / ITP
    "open finance": {"area": "Produtos", "time": "Open Finance / ITP", "acao": "Avaliar impacto no Open Finance e ITP"},
    "open banking": {"area": "Produtos", "time": "Open Finance / ITP", "acao": "Avaliar impacto no Open Finance e ITP"},
    "itp": {"area": "Produtos", "time": "Open Finance / ITP", "acao": "Verificar obrigações do ITP"},
    "iniciador de transação": {"area": "Produtos", "time": "Open Finance / ITP", "acao": "Verificar obrigações do ITP"},

    # Segurança cibernética / LGPD
    "segurança cibernética": {"area": "Tecnologia", "time": "Segurança da Informação", "acao": "Avaliar requisitos de segurança cibernética"},
    "lgpd": {"area": "Jurídico / DPO", "time": "Privacidade", "acao": "Avaliar impacto LGPD e consentimento"},
    "dados pessoais": {"area": "Jurídico / DPO", "time": "Privacidade", "acao": "Revisar tratamento de dados pessoais"},
    "proteção de dados": {"area": "Jurídico / DPO", "time": "Privacidade", "acao": "Revisar política de proteção de dados"},

    # Proteção ao consumidor
    "proteção ao consumidor": {"area": "Atendimento", "time": "SAC / Ouvidoria", "acao": "Revisar políticas de atendimento e proteção ao consumidor"},
    "consumidor": {"area": "Atendimento", "time": "SAC / Ouvidoria", "acao": "Avaliar impacto nos processos de atendimento"},
    "sac": {"area": "Atendimento", "time": "SAC / Ouvidoria", "acao": "Verificar conformidade do SAC"},
    "ouvidoria": {"area": "Atendimento", "time": "SAC / Ouvidoria", "acao": "Verificar conformidade da Ouvidoria"},

    # Crédito / SCD
    "crédito": {"area": "Risco de Crédito", "time": "SCD / Crédito", "acao": "Avaliar impacto nas operações de crédito (SCD)"},
    "scd": {"area": "Risco de Crédito", "time": "SCD / Crédito", "acao": "Revisar processos da SCD"},
    "bnpl": {"area": "Produtos", "time": "Crédito / BNPL", "acao": "Avaliar impacto no BNPL"},
    "antecipação de recebíveis": {"area": "Produtos", "time": "B2B / Restaurantes", "acao": "Verificar impacto na antecipação de recebíveis"},

    # Cartão
    "cartão": {"area": "Produtos", "time": "Cartões", "acao": "Avaliar impacto no produto de cartões"},
    "emissor": {"area": "Produtos", "time": "Cartões", "acao": "Verificar obrigações do emissor"},
    "credenciador": {"area": "Produtos", "time": "Credenciamento", "acao": "Avaliar impacto na transição para credenciador"},
    "subcredenciador": {"area": "Produtos", "time": "Credenciamento", "acao": "Verificar obrigações atuais de subcredenciador"},

    # COSIF / CADOC / Patrimônio
    "cosif": {"area": "Contabilidade / Financeiro", "time": "Contabilidade Regulatória", "acao": "Revisar adequação COSIF"},
    "cadoc": {"area": "Contabilidade / Financeiro", "time": "Contabilidade Regulatória", "acao": "Verificar impacto nos documentos CADOC"},
    "patrimônio líquido": {"area": "Financeiro / Tesouraria", "time": "Tesouraria", "acao": "Avaliar requisitos de patrimônio líquido"},
    "capital": {"area": "Financeiro / Tesouraria", "time": "Tesouraria", "acao": "Verificar requisitos de capital"},

    # Fraudes
    "fraude": {"area": "Risco Operacional", "time": "Prevenção a Fraudes", "acao": "Avaliar impacto nas políticas de prevenção a fraudes"},
    "autenticação": {"area": "Tecnologia", "time": "Segurança da Informação", "acao": "Verificar requisitos de autenticação"},

    # Tarifas
    "tarifas": {"area": "Produtos / Jurídico", "time": "Pricing / Regulatório", "acao": "Revisar estrutura tarifária conforme nova regulação"},
    "tarifa": {"area": "Produtos / Jurídico", "time": "Pricing / Regulatório", "acao": "Verificar conformidade tarifária"},

    # Governança
    "governança": {"area": "Compliance", "time": "Governança Corporativa", "acao": "Avaliar impacto nas estruturas de governança"},
    "conglomerado prudencial": {"area": "Compliance / Riscos", "time": "Risco Prudencial", "acao": "Avaliar obrigações do conglomerado prudencial"},

    # Correspondente bancário
    "correspondente bancário": {"area": "Operações", "time": "Correspondentes Bancários", "acao": "Verificar conformidade dos correspondentes bancários"},

    # PAT / Benefícios
    "pat": {"area": "Produtos", "time": "Benefícios / PAT", "acao": "Verificar conformidade com regulação PAT"},
    "programa de alimentação": {"area": "Produtos", "time": "Benefícios / PAT", "acao": "Revisar conformidade PAT"},

    # Conta de pagamento
    "conta de pagamento": {"area": "Produtos", "time": "Conta de Pagamento", "acao": "Avaliar impacto na conta de pagamento"},
    "moeda eletrônica": {"area": "Produtos", "time": "Conta de Pagamento", "acao": "Verificar conformidade com regulação de moeda eletrônica"},
}

# Compliance como responsável padrão para normas APLICÁVEIS
RESPONSAVEL_PADRAO_COMPLIANCE = {
    "area": "Compliance",
    "time": "Compliance Regulatório",
    "acao": "Analisar norma e coordenar adequação entre áreas",
}


def _carregar_config(config: Optional[Dict] = None) -> Dict:
    if config:
        return config
    config_path = Path(__file__).parent.parent / "config.json"
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {}


def _inferir_segmento(texto: str) -> str:
    """Infere segmento (B2C/B2B/AMBOS) com base no texto."""
    texto_lower = texto.lower()
    b2c = any(k in texto_lower for k in ["pessoa física", "consumidor", "usuário final", "b2c", "varejo", "cliente"])
    b2b = any(k in texto_lower for k in ["restaurante", "estabelecimento", "parceiro", "b2b", "empresa", "pj"])
    if b2c and b2b:
        return "AMBOS"
    elif b2c:
        return "B2C"
    elif b2b:
        return "B2B"
    return "N/A"


def _inferir_prioridade(pilar_score: str, classificacao: str) -> str:
    """Infere prioridade com base no score do pilar e classificação."""
    if classificacao == "APLICÁVEL" and pilar_score in ("CRÍTICO", "ALTO"):
        return "ALTA"
    elif classificacao == "APLICÁVEL":
        return "MÉDIA"
    elif pilar_score in ("CRÍTICO", "ALTO"):
        return "MÉDIA"
    return "BAIXA"


def mapear_responsaveis(
    normativo: Normativo,
    classificacao: ClassificacaoNormativo,
    avaliacao: AvaliacaoRisco,
    config: Optional[Dict] = None,
) -> List[Responsavel]:
    """
    Mapeia áreas e times responsáveis pelo acompanhamento e adequação ao normativo.

    Lógica de mapeamento:
      1. Verifica temas identificados no reasoning (keywords APLICÁVEL e MONITORAR)
      2. Cruza com políticas impactadas (que têm área responsável definida)
      3. Considera segmento (B2C/B2B) para direcionar ao time correto
      4. Compliance é sempre incluído como coordenador para normas APLICÁVEIS

    Entradas:
        normativo (Normativo): Normativo capturado.
        classificacao (ClassificacaoNormativo): Com temas e políticas identificadas.
        avaliacao (AvaliacaoRisco): Com scores por pilar.
        config (dict): Configuração. Se None, carrega do config.json.

    Saídas:
        List[Responsavel]: Lista dedupada de responsáveis com área, time e ação.
    """
    cfg = _carregar_config(config)

    texto_analise = " ".join([
        normativo.titulo,
        normativo.ementa,
        normativo.texto_integral[:2000],
    ])

    segmento = _inferir_segmento(texto_analise)
    responsaveis_map: Dict[str, Responsavel] = {}  # chave: "area|time"

    # 1. Compliance sempre como coordenador para normas APLICÁVEIS
    if classificacao.classificacao == "APLICÁVEL":
        key = f"{RESPONSAVEL_PADRAO_COMPLIANCE['area']}|{RESPONSAVEL_PADRAO_COMPLIANCE['time']}"
        responsaveis_map[key] = Responsavel(
            area=RESPONSAVEL_PADRAO_COMPLIANCE["area"],
            time=RESPONSAVEL_PADRAO_COMPLIANCE["time"],
            acao=RESPONSAVEL_PADRAO_COMPLIANCE["acao"],
            prioridade="ALTA",
            segmento=segmento,
        )

    # 2. Mapear por temas identificados
    for tema in classificacao.passo3_temas:
        kw = tema.split("] ")[-1].strip().lower()
        for mapa_kw, resp_info in MAPA_TEMA_RESPONSAVEL.items():
            if mapa_kw.lower() in kw or kw in mapa_kw.lower():
                key = f"{resp_info['area']}|{resp_info['time']}"
                if key not in responsaveis_map:
                    # Determinar prioridade com base no pilar mais relevante
                    prioridade = "MÉDIA"
                    if classificacao.classificacao == "APLICÁVEL":
                        prioridade = "ALTA" if avaliacao.score_consolidado in ("CRÍTICO", "ALTO") else "MÉDIA"

                    responsaveis_map[key] = Responsavel(
                        area=resp_info["area"],
                        time=resp_info["time"],
                        acao=resp_info["acao"],
                        prioridade=prioridade,
                        segmento=segmento,
                    )
                break

    # 3. Mapear por políticas impactadas (cada política tem área responsável)
    for pol in classificacao.passo5_politicas[:5]:
        if not pol.area_responsavel:
            continue
        area_raw = pol.area_responsavel.split(";")[0].strip()
        time_raw = pol.codigo
        key = f"{area_raw}|{time_raw}"
        if key not in responsaveis_map:
            responsaveis_map[key] = Responsavel(
                area=area_raw,
                time=f"Responsável por {pol.codigo}",
                acao=f"Revisar {pol.codigo} — {pol.nome} para adequação ao normativo",
                prioridade=_inferir_prioridade(avaliacao.score_consolidado, classificacao.classificacao),
                segmento=segmento,
            )

    # 4. Pilares com score alto → acionar áreas específicas
    if avaliacao.pilar_operacional.score in ("CRÍTICO", "ALTO"):
        key = "Tecnologia / Produtos|Engineering"
        if key not in responsaveis_map:
            responsaveis_map[key] = Responsavel(
                area="Tecnologia / Produtos",
                time="Engineering",
                acao="Avaliar impacto em sistemas e plataformas; estimar esforço de adequação",
                prioridade="ALTA" if avaliacao.pilar_operacional.score == "CRÍTICO" else "MÉDIA",
                segmento=segmento,
            )

    if avaliacao.pilar_financeiro.score in ("CRÍTICO", "ALTO"):
        key = "Financeiro / Tesouraria|Financeiro"
        if key not in responsaveis_map:
            responsaveis_map[key] = Responsavel(
                area="Financeiro / Tesouraria",
                time="Financeiro",
                acao="Estimar custo de adequação e provisionar para potenciais penalidades",
                prioridade="ALTA" if avaliacao.pilar_financeiro.score == "CRÍTICO" else "MÉDIA",
                segmento=segmento,
            )

    if avaliacao.pilar_estrategico.score in ("CRÍTICO", "ALTO"):
        key = "Diretoria / Strategy|Estratégia"
        if key not in responsaveis_map:
            responsaveis_map[key] = Responsavel(
                area="Diretoria / Strategy",
                time="Estratégia",
                acao="Avaliar impacto nos planos estratégicos (credenciador, S4/S3, Carteira Digital)",
                prioridade="ALTA",
                segmento=segmento,
            )

    # Ordenar por prioridade
    ordem_prioridade = {"ALTA": 0, "MÉDIA": 1, "BAIXA": 2}
    resultado = sorted(
        responsaveis_map.values(),
        key=lambda r: ordem_prioridade.get(r.prioridade, 3),
    )

    return resultado
