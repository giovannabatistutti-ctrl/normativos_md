"""
Módulo 4 — resumo.py
Gera resumo executivo estruturado em português brasileiro para um normativo analisado,
consolidando informações dos módulos anteriores.

Entradas:
    normativo (Normativo): Normativo capturado com texto_integral.
    classificacao (ClassificacaoNormativo): Resultado do módulo reasoning.
    avaliacao (AvaliacaoRisco): Resultado do módulo avaliacao_risco.
    responsaveis (List[Responsavel]): Resultado do módulo responsaveis.
    config (dict): Configuração do config.json.

Saídas:
    ResumoExecutivo: Objeto com resumo estruturado pronto para publicação.

Uso:
    from modules.resumo import gerar_resumo
    resumo = gerar_resumo(normativo, classificacao, avaliacao, responsaveis)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from .captura import Normativo
from .reasoning import ClassificacaoNormativo
from .avaliacao_risco import AvaliacaoRisco

BRASILIA = timezone(timedelta(hours=-3))


@dataclass
class ResumoExecutivo:
    """Resumo executivo de um normativo BCB para o iFood Pago."""

    # Identificação
    normativo_id: str
    titulo: str
    tipo: str
    numero: str

    # Classificação e risco
    classificacao: str          # APLICÁVEL / MONITORAR / NÃO APLICÁVEL
    score_criticidade: str      # CRÍTICO / ALTO / MÉDIO / BAIXO

    # Resumo narrativo (PT-BR)
    o_que_determina: str        # O que a norma determina
    para_quem_se_aplica: str    # Entidades e produtos afetados
    prazo_adequacao: str        # Data de vigência / prazo
    acoes_requeridas: List[str] # Ações que o iFood Pago precisa tomar
    politicas_revisar: List[str]# Políticas internas que precisam ser revisadas
    areas_responsaveis: List[str]  # Áreas/times responsáveis

    # Metadados
    link_integra: str           # Link para a norma no BCB
    data_publicacao: str
    data_analise: str = field(
        default_factory=lambda: datetime.now(BRASILIA).strftime("%Y-%m-%d %H:%M")
    )

    # Resumo markdown completo
    markdown: str = field(default="")


def _carregar_config(config: Optional[Dict] = None) -> Dict:
    if config:
        return config
    config_path = Path(__file__).parent.parent / "config.json"
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {}


def _sintetizar_texto(texto: str, max_chars: int = 600) -> str:
    """
    Extrai as primeiras sentenças relevantes do texto integral.
    Foca em artigos que descrevem obrigações.
    """
    if not texto or texto.startswith("["):
        return "Texto integral não disponível. Consultar norma original no link fornecido."

    # Remover cabeçalhos técnicos (HTML artifacts)
    texto_limpo = re.sub(r"\s+", " ", texto).strip()

    # Tentar extrair Art. 1 ou primeiro parágrafo substantivo
    m = re.search(
        r"(Art\.\s*1[°º]?.+?(?:Art\.\s*2|$))",
        texto_limpo,
        re.DOTALL | re.IGNORECASE,
    )
    if m:
        trecho = m.group(1).strip()
        if len(trecho) > 100:
            return trecho[:max_chars] + ("..." if len(trecho) > max_chars else "")

    # Fallback: primeiras 600 chars com sentença completa
    if len(texto_limpo) <= max_chars:
        return texto_limpo

    truncado = texto_limpo[:max_chars]
    ultimo_ponto = truncado.rfind(".")
    if ultimo_ponto > 100:
        return truncado[:ultimo_ponto + 1]
    return truncado + "..."


def _identificar_entidades_afetadas(texto: str, temas: List[str]) -> str:
    """Identifica entidades e produtos afetados."""
    entidades = []
    produtos = []

    mapa_entidades = {
        "instituição de pagamento": "iFood Pago IP",
        "sociedade de crédito direto": "iFood Pago SCD",
        "scd": "iFood Pago SCD",
        "conglomerado prudencial": "Conglomerado Prudencial Tipo 3",
        "subcredenciador": "iFood Pago (Subcredenciador)",
        "credenciador": "iFood Pago (Credenciador — em transição)",
        "participante do pix": "iFood Pago (Pix)",
        "open finance": "iFood Pago (Open Finance / ITP)",
        "itp": "iFood Pago (ITP)",
    }

    mapa_produtos = {
        "conta de pagamento": "Conta de Pagamento",
        "cartão": "Cartão de Crédito / Benefícios",
        "pix": "Pix",
        "bnpl": "BNPL",
        "antecipação": "Antecipação de Recebíveis",
        "pos": "POS (Máquina de Cartão)",
        "open finance": "Open Finance / ITP",
        "carteira digital": "Carteira Digital",
    }

    texto_lower = texto.lower()
    for kw, entidade in mapa_entidades.items():
        if kw in texto_lower and entidade not in entidades:
            entidades.append(entidade)

    for kw, produto in mapa_produtos.items():
        if kw in texto_lower and produto not in produtos:
            produtos.append(produto)

    partes = []
    if entidades:
        partes.append("**Entidades:** " + ", ".join(entidades[:4]))
    if produtos:
        partes.append("**Produtos:** " + ", ".join(produtos[:5]))

    return " | ".join(partes) if partes else "A verificar — consultar norma original."


def _extrair_acoes(texto: str, avaliacao: AvaliacaoRisco, classificacao: ClassificacaoNormativo) -> List[str]:
    """Extrai ações requeridas com base na análise dos pilares."""
    acoes = []

    if classificacao.classificacao == "APLICÁVEL":
        acoes.append("Realizar análise de gap entre a norma e os processos/políticas atuais do iFood Pago")

    if avaliacao.pilar_regulatorio.score in ("CRÍTICO", "ALTO"):
        acoes.append("Mapear obrigações regulatórias específicas e definir plano de adequação com prazos")

    if avaliacao.pilar_operacional.score in ("CRÍTICO", "ALTO"):
        acoes.append("Avaliar impacto em sistemas e processos operacionais; envolver TI e Produtos")

    if avaliacao.pilar_financeiro.score in ("CRÍTICO", "ALTO"):
        acoes.append("Estimar custo de adequação e potenciais penalidades; informar área Financeira")

    if avaliacao.pilar_clientes.score in ("CRÍTICO", "ALTO"):
        acoes.append("Verificar impacto nos contratos/termos com clientes B2C e B2B; avaliar comunicação necessária")

    if avaliacao.pilar_estrategico.score in ("CRÍTICO", "ALTO"):
        acoes.append("Avaliar impacto nos projetos estratégicos (transição credenciador, S5→S4/S3, Carteira Digital)")

    if avaliacao.urgente:
        acoes.insert(0, "⚠️ URGENTE: Prazo de adequação iminente — priorizar análise e ação imediata")

    if classificacao.feedback_aplicado and classificacao.feedback_notas:
        acoes.append(f"Considerar feedback anterior da equipe: {classificacao.feedback_notas}")

    if not acoes:
        acoes.append("Monitorar norma e avaliar aplicabilidade em revisão periódica")

    return acoes


def _gerar_markdown(resumo: ResumoExecutivo) -> str:
    """Gera o markdown completo do resumo executivo."""
    emoji_class = {
        "APLICÁVEL": "🔴",
        "MONITORAR": "🟡",
        "NÃO APLICÁVEL": "🟢",
    }.get(resumo.classificacao, "⚪")

    emoji_score = {
        "CRÍTICO": "🚨",
        "ALTO": "🔴",
        "MÉDIO": "🟡",
        "BAIXO": "🟢",
    }.get(resumo.score_criticidade, "⚪")

    acoes_md = "\n".join(f"- {a}" for a in resumo.acoes_requeridas)
    politicas_md = "\n".join(f"- {p}" for p in resumo.politicas_revisar) if resumo.politicas_revisar else "- Nenhuma política identificada"
    areas_md = "\n".join(f"- {a}" for a in resumo.areas_responsaveis) if resumo.areas_responsaveis else "- A definir"

    return f"""# {resumo.titulo}

> **Análise iFood Pago | Compliance** — {resumo.data_analise}

---

## Identificação

| Campo | Valor |
|---|---|
| **Tipo** | {resumo.tipo} |
| **Número** | {resumo.numero} |
| **Data de Publicação** | {resumo.data_publicacao} |
| **Link BCB** | [{resumo.link_integra}]({resumo.link_integra}) |

---

## Classificação e Criticidade

| Classificação | Score de Criticidade |
|---|---|
| {emoji_class} **{resumo.classificacao}** | {emoji_score} **{resumo.score_criticidade}** |

---

## O Que a Norma Determina

{resumo.o_que_determina}

---

## Para Quem se Aplica

{resumo.para_quem_se_aplica}

---

## Prazo de Adequação

{resumo.prazo_adequacao or "Não identificado — consultar norma original."}

---

## Ações Requeridas

{acoes_md}

---

## Políticas Internas a Revisar

{politicas_md}

---

## Áreas Responsáveis

{areas_md}

---

*Gerado automaticamente pelo pipeline normativos-bcb | iFood Pago Compliance*
"""


def gerar_resumo(
    normativo: Normativo,
    classificacao: ClassificacaoNormativo,
    avaliacao: AvaliacaoRisco,
    responsaveis: Optional[List] = None,
    config: Optional[Dict] = None,
) -> ResumoExecutivo:
    """
    Gera resumo executivo estruturado em PT-BR para um normativo analisado.

    Consolida informações dos módulos 1 (captura), 2 (reasoning) e 3 (avaliação de risco).

    Entradas:
        normativo (Normativo): Normativo com texto_integral.
        classificacao (ClassificacaoNormativo): Resultado do reasoning.
        avaliacao (AvaliacaoRisco): Resultado da avaliação de risco.
        responsaveis (List[Responsavel]): Lista de responsáveis (pode ser None).
        config (dict): Configuração. Se None, carrega do config.json.

    Saídas:
        ResumoExecutivo: Objeto com resumo completo, incluindo markdown.
    """
    cfg = _carregar_config(config)

    texto_analise = " ".join([normativo.titulo, normativo.ementa, normativo.texto_integral[:3000]])

    # O que determina
    o_que = _sintetizar_texto(normativo.texto_integral or normativo.ementa)

    # Para quem se aplica
    para_quem = _identificar_entidades_afetadas(texto_analise, classificacao.passo3_temas)

    # Prazo
    prazo = avaliacao.prazo_adequacao or classificacao.data_vigencia or "Não identificado — verificar norma"
    if avaliacao.urgente:
        prazo = f"⚠️ URGENTE — {prazo}"

    # Ações
    acoes = _extrair_acoes(texto_analise, avaliacao, classificacao)

    # Políticas
    politicas_revisar = [
        f"{p.codigo} — {p.nome} ({p.area_responsavel})"
        for p in classificacao.passo5_politicas[:8]
    ]

    # Áreas responsáveis
    areas = []
    if responsaveis:
        for r in responsaveis:
            areas.append(f"{r.area} / {r.time} — {r.acao}")

    resumo = ResumoExecutivo(
        normativo_id=normativo.id,
        titulo=normativo.titulo,
        tipo=normativo.tipo,
        numero=normativo.numero,
        classificacao=classificacao.classificacao,
        score_criticidade=avaliacao.score_consolidado,
        o_que_determina=o_que,
        para_quem_se_aplica=para_quem,
        prazo_adequacao=prazo,
        acoes_requeridas=acoes,
        politicas_revisar=politicas_revisar,
        areas_responsaveis=areas,
        link_integra=normativo.link,
        data_publicacao=normativo.data_publicacao,
    )

    # Gerar markdown
    resumo.markdown = _gerar_markdown(resumo)

    return resumo
