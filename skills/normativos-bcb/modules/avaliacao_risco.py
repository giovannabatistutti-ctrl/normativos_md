"""
Módulo 3 — avaliacao_risco.py
Avalia o risco de um normativo classificado nos 5 pilares definidos para o iFood Pago,
gerando um score de criticidade consolidado.

Entradas:
    normativo (Normativo): Normativo capturado (com texto_integral).
    classificacao (ClassificacaoNormativo): Resultado do módulo reasoning.
    config (dict): Configuração do config.json.

Saídas:
    AvaliacaoRisco: Objeto com avaliação por pilar e score consolidado.

Uso:
    from modules.avaliacao_risco import avaliar_risco
    avaliacao = avaliar_risco(normativo, classificacao, config=config)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .captura import Normativo
from .reasoning import ClassificacaoNormativo


# ─── Constantes de score ────────────────────────────────────────────────────

SCORE_CRITICO = "CRÍTICO"
SCORE_ALTO = "ALTO"
SCORE_MEDIO = "MÉDIO"
SCORE_BAIXO = "BAIXO"

SCORE_PESOS = {SCORE_CRITICO: 4, SCORE_ALTO: 3, SCORE_MEDIO: 2, SCORE_BAIXO: 1}
SCORE_LABELS = {4: SCORE_CRITICO, 3: SCORE_ALTO, 2: SCORE_MEDIO, 1: SCORE_BAIXO}


@dataclass
class PilarAvaliacao:
    """Resultado da avaliação de um pilar específico."""
    pilar: str                # Nome do pilar
    score: str                # CRÍTICO / ALTO / MÉDIO / BAIXO
    score_numerico: int       # 4/3/2/1
    justificativa: str        # Explicação
    elementos_identificados: List[str] = field(default_factory=list)  # Evidências no texto


@dataclass
class AvaliacaoRisco:
    """Avaliação completa de risco de um normativo nos 5 pilares."""

    normativo_id: str
    normativo_titulo: str
    classificacao: str        # Herdado do reasoning

    # 5 Pilares
    pilar_operacional: PilarAvaliacao
    pilar_regulatorio: PilarAvaliacao
    pilar_financeiro: PilarAvaliacao
    pilar_clientes: PilarAvaliacao
    pilar_estrategico: PilarAvaliacao

    # Score consolidado
    score_consolidado: str    # CRÍTICO / ALTO / MÉDIO / BAIXO
    score_numerico: float     # Média ponderada
    justificativa_consolidada: str

    # Prazo de adequação
    prazo_adequacao: Optional[str] = None
    urgente: bool = False     # True se prazo < 90 dias ou já vigente


def _carregar_config(config: Optional[Dict] = None) -> Dict:
    if config:
        return config
    config_path = Path(__file__).parent.parent / "config.json"
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {}


def _buscar_keywords(texto: str, keywords: List[str]) -> List[str]:
    """Retorna keywords encontradas no texto (case-insensitive)."""
    encontrados = []
    texto_lower = texto.lower()
    for kw in keywords:
        if kw.lower() in texto_lower:
            encontrados.append(kw)
    return encontrados


def _avaliar_pilar_operacional(texto: str, classificacao: ClassificacaoNormativo) -> PilarAvaliacao:
    """
    Pilar 1 — Impacto Operacional
    Avalia impacto em processos, sistemas e produtos do iFood Pago.
    """
    keywords_critico = [
        "alteração de sistema", "mudança de processo", "redesenho", "implantação obrigatória",
        "prazo de adequação", "sistema de pagamento", "infraestrutura tecnológica",
        "plataforma", "integração", "api", "certificação", "homologação",
    ]
    keywords_alto = [
        "procedimento", "processo", "controle", "monitoramento", "relatório",
        "cadastro", "registro", "documentação obrigatória", "workflow", "fluxo",
    ]
    keywords_medio = [
        "orientação", "recomendação", "boas práticas", "treinamento", "capacitação",
    ]

    encontrados_critico = _buscar_keywords(texto, keywords_critico)
    encontrados_alto = _buscar_keywords(texto, keywords_alto)
    encontrados_medio = _buscar_keywords(texto, keywords_medio)

    # Produtos iFood Pago afetados
    produtos_ifood = [
        "conta de pagamento", "cartão", "pix", "pos", "open finance",
        "bnpl", "antecipação", "carteira digital", "itp",
    ]
    produtos_afetados = _buscar_keywords(texto, produtos_ifood)

    if encontrados_critico and len(encontrados_critico) >= 2 and produtos_afetados:
        score = SCORE_CRITICO
        just = f"Mudanças estruturais em sistemas/processos identificadas: {', '.join(encontrados_critico[:3])}. Produtos afetados: {', '.join(produtos_afetados[:3])}."
    elif encontrados_critico or (encontrados_alto and produtos_afetados):
        score = SCORE_ALTO
        just = f"Impacto em processos operacionais: {', '.join((encontrados_critico + encontrados_alto)[:3])}."
    elif encontrados_alto or encontrados_medio:
        score = SCORE_MEDIO
        just = f"Ajustes pontuais em procedimentos: {', '.join((encontrados_alto + encontrados_medio)[:3])}."
    else:
        score = SCORE_BAIXO
        just = "Impacto operacional não identificado ou mínimo."

    todos = encontrados_critico + encontrados_alto + encontrados_medio
    return PilarAvaliacao(
        pilar="Impacto Operacional",
        score=score,
        score_numerico=SCORE_PESOS[score],
        justificativa=just,
        elementos_identificados=todos[:5],
    )


def _avaliar_pilar_regulatorio(texto: str, classificacao: ClassificacaoNormativo) -> PilarAvaliacao:
    """
    Pilar 2 — Impacto Regulatório
    Avalia sanções, prazo de adequação, complexidade e obrigações.
    """
    keywords_critico = [
        "cancelamento de autorização", "revogação", "cassação", "multa", "sanção administrativa",
        "responsabilidade dos administradores", "intervenção", "liquidação",
        "prazo improrrogável", "vedação", "proibição", "punição",
    ]
    keywords_alto = [
        "obrigação", "dever", "deve", "é vedado", "é obrigatório", "prazo para adequação",
        "requerimento", "condição para funcionamento", "autorização", "licença",
        "relatório obrigatório", "limite regulatório",
    ]
    keywords_medio = [
        "recomendação", "orientação regulatória", "boa prática regulatória", "expectativa do regulador",
    ]

    encontrados_critico = _buscar_keywords(texto, keywords_critico)
    encontrados_alto = _buscar_keywords(texto, keywords_alto)
    encontrados_medio = _buscar_keywords(texto, keywords_medio)

    # Confiança da classificação como fator
    alta_confianca = classificacao.confianca == "ALTA"

    if encontrados_critico and alta_confianca:
        score = SCORE_CRITICO
        just = f"Risco regulatório severo identificado: {', '.join(encontrados_critico[:3])}."
    elif encontrados_critico or (encontrados_alto and alta_confianca and len(encontrados_alto) >= 3):
        score = SCORE_ALTO
        just = f"Obrigações regulatórias significativas: {', '.join((encontrados_critico + encontrados_alto)[:3])}."
    elif encontrados_alto:
        score = SCORE_MEDIO
        just = f"Obrigações regulatórias identificadas: {', '.join(encontrados_alto[:3])}."
    elif encontrados_medio:
        score = SCORE_BAIXO
        just = f"Orientações regulatórias sem obrigação imediata: {', '.join(encontrados_medio[:3])}."
    else:
        score = SCORE_BAIXO
        just = "Impacto regulatório não identificado ou mínimo."

    todos = encontrados_critico + encontrados_alto + encontrados_medio
    return PilarAvaliacao(
        pilar="Impacto Regulatório",
        score=score,
        score_numerico=SCORE_PESOS[score],
        justificativa=just,
        elementos_identificados=todos[:5],
    )


def _avaliar_pilar_financeiro(texto: str, classificacao: ClassificacaoNormativo) -> PilarAvaliacao:
    """
    Pilar 3 — Impacto Financeiro
    Avalia custo de adequação, multas potenciais e impacto em produtos.
    """
    keywords_critico = [
        "multa", "penalidade financeira", "ressarcimento obrigatório", "indenização",
        "recolhimento compulsório", "patrimônio mínimo", "capital mínimo",
        "limite de exposição", "provisão obrigatória", "perda de receita",
    ]
    keywords_alto = [
        "custo de adequação", "investimento em tecnologia", "taxa", "tarifa",
        "limite de cobrança", "tarifação", "pricing", "remuneração",
        "limite de spread", "juros", "encargo",
    ]
    keywords_medio = [
        "receita", "despesa", "orçamento", "custo operacional",
    ]

    encontrados_critico = _buscar_keywords(texto, keywords_critico)
    encontrados_alto = _buscar_keywords(texto, keywords_alto)
    encontrados_medio = _buscar_keywords(texto, keywords_medio)

    if encontrados_critico:
        score = SCORE_CRITICO
        just = f"Risco financeiro direto identificado: {', '.join(encontrados_critico[:3])}."
    elif encontrados_alto and len(encontrados_alto) >= 2:
        score = SCORE_ALTO
        just = f"Impacto financeiro relevante: {', '.join(encontrados_alto[:3])}."
    elif encontrados_alto or encontrados_medio:
        score = SCORE_MEDIO
        just = f"Impacto financeiro moderado: {', '.join((encontrados_alto + encontrados_medio)[:3])}."
    else:
        score = SCORE_BAIXO
        just = "Impacto financeiro não identificado ou mínimo."

    todos = encontrados_critico + encontrados_alto + encontrados_medio
    return PilarAvaliacao(
        pilar="Impacto Financeiro",
        score=score,
        score_numerico=SCORE_PESOS[score],
        justificativa=just,
        elementos_identificados=todos[:5],
    )


def _avaliar_pilar_clientes(texto: str, classificacao: ClassificacaoNormativo) -> PilarAvaliacao:
    """
    Pilar 4 — Impacto em Clientes
    Avalia impacto em B2C/B2B, proteção ao consumidor.
    """
    keywords_critico = [
        "cancelamento de serviço", "bloqueio de conta", "suspensão de produto",
        "proibição de oferta", "reembolso obrigatório", "ressarcimento ao cliente",
        "direito de arrependimento", "portabilidade obrigatória",
    ]
    keywords_alto = [
        "usuário", "consumidor", "cliente", "proteção ao consumidor",
        "transparência", "divulgação obrigatória", "informação ao cliente",
        "atendimento", "sac", "ouvidoria", "reclamação", "prazo de resposta",
        "lgpd", "dados pessoais", "consentimento",
    ]
    keywords_medio = [
        "comunicado", "notificação ao cliente", "aviso", "informação",
    ]

    # Segmento
    b2c_keywords = ["pessoa física", "consumidor", "usuário final", "b2c", "varejo"]
    b2b_keywords = ["restaurante", "estabelecimento", "parceiro", "b2b", "empresa", "pj "]

    encontrados_critico = _buscar_keywords(texto, keywords_critico)
    encontrados_alto = _buscar_keywords(texto, keywords_alto)
    encontrados_medio = _buscar_keywords(texto, keywords_medio)
    b2c = _buscar_keywords(texto, b2c_keywords)
    b2b = _buscar_keywords(texto, b2b_keywords)

    segmentos = []
    if b2c:
        segmentos.append("B2C")
    if b2b:
        segmentos.append("B2B")
    segmento_str = "/".join(segmentos) if segmentos else "não especificado"

    if encontrados_critico:
        score = SCORE_CRITICO
        just = f"Impacto direto nos clientes ({segmento_str}): {', '.join(encontrados_critico[:3])}."
    elif encontrados_alto and len(encontrados_alto) >= 3:
        score = SCORE_ALTO
        just = f"Impacto relevante em clientes ({segmento_str}): {', '.join(encontrados_alto[:3])}."
    elif encontrados_alto:
        score = SCORE_MEDIO
        just = f"Impacto moderado em clientes ({segmento_str}): {', '.join(encontrados_alto[:3])}."
    elif encontrados_medio:
        score = SCORE_BAIXO
        just = f"Impacto mínimo em clientes ({segmento_str})."
    else:
        score = SCORE_BAIXO
        just = "Impacto em clientes não identificado."

    todos = encontrados_critico + encontrados_alto + encontrados_medio
    return PilarAvaliacao(
        pilar="Impacto em Clientes",
        score=score,
        score_numerico=SCORE_PESOS[score],
        justificativa=just,
        elementos_identificados=todos[:5],
    )


def _avaliar_pilar_estrategico(texto: str, classificacao: ClassificacaoNormativo) -> PilarAvaliacao:
    """
    Pilar 5 — Impacto Estratégico
    Avalia impacto na transição subcredenciador→credenciador, S5→S4/S3, Carteira Digital.
    """
    keywords_critico = [
        "credenciador", "subcredenciador",
        "s4", "s3", "reclassificação de segmento",
        "carteira digital", "wallet",
        "autorização", "habilitação obrigatória",
        "capital mínimo regulatório",
    ]
    keywords_alto = [
        "open finance", "itp", "iniciador de transação",
        "conglomerado prudencial", "tipo 3",
        "pix", "arranjo de pagamento",
        "expansão de atividades", "novo produto",
        "risco sistêmico",
    ]
    keywords_medio = [
        "competitividade", "mercado de pagamentos",
        "inovação", "fintech", "sandbox regulatório",
    ]

    encontrados_critico = _buscar_keywords(texto, keywords_critico)
    encontrados_alto = _buscar_keywords(texto, keywords_alto)
    encontrados_medio = _buscar_keywords(texto, keywords_medio)

    # Projetos estratégicos do iFood Pago
    projetos = []
    if any(k in texto.lower() for k in ["credenciador", "subcredenciador"]):
        projetos.append("Transição subcredenciador→credenciador")
    if any(k in texto.lower() for k in ["s4", "s3", "reclassificação"]):
        projetos.append("Reclassificação S5→S4/S3")
    if any(k in texto.lower() for k in ["carteira digital", "wallet"]):
        projetos.append("Lançamento Carteira Digital")

    if encontrados_critico and projetos:
        score = SCORE_CRITICO
        just = f"Impacto estratégico crítico nos projetos em andamento: {', '.join(projetos)}. Elementos: {', '.join(encontrados_critico[:3])}."
    elif encontrados_critico or (encontrados_alto and projetos):
        score = SCORE_ALTO
        just = f"Impacto estratégico relevante: {', '.join((encontrados_critico + encontrados_alto)[:3])}."
    elif encontrados_alto:
        score = SCORE_MEDIO
        just = f"Impacto estratégico moderado: {', '.join(encontrados_alto[:3])}."
    elif encontrados_medio:
        score = SCORE_BAIXO
        just = f"Impacto estratégico de monitoramento: {', '.join(encontrados_medio[:3])}."
    else:
        score = SCORE_BAIXO
        just = "Impacto estratégico não identificado."

    todos = encontrados_critico + encontrados_alto + encontrados_medio
    return PilarAvaliacao(
        pilar="Impacto Estratégico",
        score=score,
        score_numerico=SCORE_PESOS[score],
        justificativa=just,
        elementos_identificados=todos[:5],
    )


def _calcular_score_consolidado(pilares: List[PilarAvaliacao]) -> tuple[str, float, str]:
    """
    Calcula score consolidado a partir dos 5 pilares.
    Usa média ponderada com peso maior para pilares regulatório e estratégico.
    """
    pesos = {
        "Impacto Operacional": 1.0,
        "Impacto Regulatório": 1.5,
        "Impacto Financeiro": 1.0,
        "Impacto em Clientes": 1.0,
        "Impacto Estratégico": 1.5,
    }

    total_peso = 0.0
    soma_ponderada = 0.0
    max_score = 0

    for pilar in pilares:
        peso = pesos.get(pilar.pilar, 1.0)
        soma_ponderada += pilar.score_numerico * peso
        total_peso += peso
        max_score = max(max_score, pilar.score_numerico)

    media = soma_ponderada / total_peso if total_peso > 0 else 1.0

    # Regra: se qualquer pilar é CRÍTICO, score consolidado é no mínimo ALTO
    if max_score == 4:
        score_final = SCORE_CRITICO if media >= 3.5 else SCORE_ALTO
    elif media >= 3.0:
        score_final = SCORE_ALTO
    elif media >= 2.0:
        score_final = SCORE_MEDIO
    else:
        score_final = SCORE_BAIXO

    criticos = [p.pilar for p in pilares if p.score == SCORE_CRITICO]
    altos = [p.pilar for p in pilares if p.score == SCORE_ALTO]

    just_parts = []
    if criticos:
        just_parts.append(f"Pilares CRÍTICOS: {', '.join(criticos)}")
    if altos:
        just_parts.append(f"Pilares ALTOS: {', '.join(altos)}")
    just_parts.append(f"Score médio ponderado: {media:.2f}/4.0")

    return score_final, media, ". ".join(just_parts)


def avaliar_risco(
    normativo: Normativo,
    classificacao: ClassificacaoNormativo,
    config: Optional[Dict] = None,
) -> AvaliacaoRisco:
    """
    Avalia o risco de um normativo nos 5 pilares definidos para o iFood Pago.

    Pilares avaliados:
      1. Impacto Operacional  — processos, sistemas, produtos afetados
      2. Impacto Regulatório  — sanções, prazo de adequação, complexidade
      3. Impacto Financeiro   — custo de adequação, multas potenciais
      4. Impacto em Clientes  — B2C/B2B, proteção ao consumidor
      5. Impacto Estratégico  — transição credenciador, S5→S4/S3, Carteira Digital

    Entradas:
        normativo (Normativo): Normativo com texto_integral.
        classificacao (ClassificacaoNormativo): Resultado do módulo reasoning.
        config (dict): Configuração. Se None, carrega do config.json.

    Saídas:
        AvaliacaoRisco: Avaliação estruturada com score consolidado.
    """
    cfg = _carregar_config(config)

    # Texto para análise
    texto = " ".join([
        normativo.titulo,
        normativo.ementa,
        normativo.texto_integral[:8000],
    ]).lower()

    # Avaliar cada pilar
    pilar_op = _avaliar_pilar_operacional(texto, classificacao)
    pilar_reg = _avaliar_pilar_regulatorio(texto, classificacao)
    pilar_fin = _avaliar_pilar_financeiro(texto, classificacao)
    pilar_cli = _avaliar_pilar_clientes(texto, classificacao)
    pilar_est = _avaliar_pilar_estrategico(texto, classificacao)

    pilares = [pilar_op, pilar_reg, pilar_fin, pilar_cli, pilar_est]
    score_consolidado, score_num, just_consolidada = _calcular_score_consolidado(pilares)

    # Prazo de adequação
    prazo = classificacao.data_vigencia
    urgente = False
    if prazo:
        from datetime import datetime, timezone, timedelta
        BRASILIA = timezone(timedelta(hours=-3))
        try:
            # Tentar extrair ano
            m = re.search(r"(\d{4})", prazo)
            if m:
                ano = int(m.group(1))
                mes_atual = datetime.now(BRASILIA).month
                ano_atual = datetime.now(BRASILIA).year
                if ano == ano_atual and mes_atual >= 10:
                    urgente = True
                elif ano < ano_atual:
                    urgente = True
        except Exception:
            pass

    return AvaliacaoRisco(
        normativo_id=normativo.id,
        normativo_titulo=normativo.titulo,
        classificacao=classificacao.classificacao,
        pilar_operacional=pilar_op,
        pilar_regulatorio=pilar_reg,
        pilar_financeiro=pilar_fin,
        pilar_clientes=pilar_cli,
        pilar_estrategico=pilar_est,
        score_consolidado=score_consolidado,
        score_numerico=score_num,
        justificativa_consolidada=just_consolidada,
        prazo_adequacao=prazo,
        urgente=urgente,
    )
