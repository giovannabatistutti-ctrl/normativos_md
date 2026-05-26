"""
Módulo 2 — reasoning.py
Aplica o reasoning layer (REASONING_LAYER.md + REASONING_LAYER_POLITICAS.md + FEEDBACK.md)
para classificar a aplicabilidade de um normativo ao iFood Pago.

Entradas:
    normativo (Normativo): Objeto Normativo capturado pelo módulo 1.
    config (dict): Configuração carregada do config.json.

Saídas:
    ClassificacaoNormativo: Objeto com classificação, justificativa, políticas impactadas
                            e metadados de raciocínio.

Uso:
    from modules.reasoning import classificar_normativo
    classificacao = classificar_normativo(normativo, config=config)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .captura import Normativo


# ─── Constantes de classificação ──────────────────────────────────────────────

APLICAVEL = "APLICÁVEL"
MONITORAR = "MONITORAR"
NAO_APLICAVEL = "NÃO APLICÁVEL"

# Entidades do iFood Pago que tornam uma norma relevante
ENTIDADES_IFOOD = [
    "instituição de pagamento",
    "instituições de pagamento",
    "ip ",
    "sociedade de crédito direto",
    "scd ",
    "conglomerado prudencial",
    "conglomerado tipo 3",
    "segmento s5",
    "segmento s4",
    "segmento s3",
    "participante do pix",
    "participantes do pix",
    "open finance",
    "open banking",
    "itp ",
    "iniciador de transação de pagamento",
    "subcredenciador",
    "credenciador",
    "arranjo de pagamento",
    "detentor de conta",
]

# Fora do escopo do iFood Pago — se a norma menciona APENAS estes, provavelmente não aplica
FORA_ESCOPO = [
    "câmbio",
    "crédito rural",
    "crédito imobiliário",
    "ativo virtual",
    "criptoativo",
    "seguro",
    "resseguro",
    "mercado de capitais",
    "cooperativa de crédito",
    "banco comercial exclusivamente",
]


@dataclass
class PoliticaImpactada:
    """Política interna impactada pelo normativo."""
    codigo: str
    nome: str
    area_responsavel: str
    acao_sugerida: str


@dataclass
class ClassificacaoNormativo:
    """Resultado da classificação de um normativo pelo reasoning layer."""

    # Identificação
    normativo_id: str
    normativo_titulo: str

    # Classificação principal
    classificacao: str          # APLICÁVEL / MONITORAR / NÃO APLICÁVEL
    confianca: str              # ALTA / MÉDIA / BAIXA
    justificativa: str          # Explicação da classificação

    # Detalhes da árvore de decisão
    passo1_tipo: str            # Tipo e escopo declarado
    passo2_atinge_ifood: bool   # Atinge iFood Pago?
    passo2_razoes: List[str]    # Por que atinge (ou não)
    passo3_temas: List[str]     # Temas identificados vs. produtos iFood
    passo4_classificacao: str   # Classificação resultante (igual a `classificacao`)
    passo5_politicas: List[PoliticaImpactada]  # Políticas internas impactadas

    # Data de vigência extraída
    data_vigencia: Optional[str] = None

    # Metadados
    reasoning_layer_versao: str = "REASONING_LAYER.md"
    feedback_aplicado: bool = False
    feedback_notas: str = ""


def _carregar_config(config: Optional[Dict] = None) -> Dict:
    """Carrega config.json se não fornecido."""
    if config:
        return config
    config_path = Path(__file__).parent.parent / "config.json"
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {}


def _carregar_arquivo(caminho: str) -> str:
    """Lê um arquivo de texto, retornando string vazia se não existir."""
    p = Path(caminho)
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""


def _extrair_politicas_do_md(politicas_md: str) -> List[Dict]:
    """
    Extrai lista de políticas do REASONING_LAYER_POLITICAS.md.
    Retorna lista de dicts com: codigo, nome, area_responsavel, gatilhos.
    """
    politicas = []
    blocos = re.split(r"#{3,4}\s+", politicas_md)
    for bloco in blocos:
        codigo_m = re.search(r"(iFP-\w+-\d+)", bloco)
        if not codigo_m:
            continue
        codigo = codigo_m.group(1)

        nome_m = re.search(r"(iFP-\w+-\d+)\s*[—\-–]\s*(.+)", bloco)
        nome = nome_m.group(2).strip() if nome_m else ""

        area_m = re.search(r"\*\*Áreas responsáveis\*\*\s*\|\s*(.+?)(?:\||\n)", bloco)
        area = area_m.group(1).strip() if area_m else ""

        gatilhos_m = re.search(r"\*\*Gatilhos regulatórios\*\*\s*\|\s*(.+?)(?:\n---|\Z)", bloco, re.DOTALL)
        gatilhos = gatilhos_m.group(1).strip() if gatilhos_m else ""

        politicas.append({
            "codigo": codigo,
            "nome": nome,
            "area_responsavel": area,
            "gatilhos": gatilhos,
        })
    return politicas


def _verificar_feedback(
    normativo: Normativo,
    feedback_md: str,
) -> tuple[bool, str]:
    """
    Verifica se há feedbacks ativos que afetam a classificação do normativo.
    Retorna (feedback_aplicado, notas).
    """
    if not feedback_md or "a preencher" in feedback_md.lower():
        return False, ""

    texto_busca = (normativo.titulo + " " + normativo.ementa).lower()
    notas = []

    # Verificar regras gerais
    secao_regras = re.search(
        r"## Regras Gerais Ativas(.+?)(?:##|\Z)", feedback_md, re.DOTALL
    )
    if secao_regras:
        regras_texto = secao_regras.group(1)
        regras = re.findall(r"\[.+?\]\s*REGRA:\s*(.+?)(?:\||\n)", regras_texto)
        for regra in regras:
            notas.append(f"Regra ativa: {regra.strip()}")

    # Verificar se há feedback específico para este normativo
    if normativo.numero and normativo.numero in feedback_md:
        notas.append(f"Feedback específico encontrado para normativo nº {normativo.numero}")

    return bool(notas), "; ".join(notas)


def _identificar_temas(texto: str, keywords_aplicavel: List[str], keywords_monitorar: List[str]) -> List[str]:
    """Identifica temas relevantes no texto do normativo."""
    texto_lower = texto.lower()
    temas = []
    for kw in keywords_aplicavel:
        if kw.lower() in texto_lower:
            temas.append(f"[APLICÁVEL] {kw}")
    for kw in keywords_monitorar:
        if kw.lower() in texto_lower:
            temas.append(f"[MONITORAR] {kw}")
    return temas


def _extrair_data_vigencia(texto: str) -> Optional[str]:
    """Extrai data de vigência do texto da norma."""
    padroes = [
        r"entr[ae](?:r[aá])?\s+em\s+vigor\s+(?:a\s+partir\s+de\s+)?(\d{1,2}[°/\-\.]\s*(?:\d{2}|\w+)[/\-\.]\s*\d{4})",
        r"vigência\s*(?:a\s*partir\s*de)?\s*:?\s*(\d{1,2}[°/\-\.]\s*\w+[/\-\.]\s*\d{4})",
        r"a\s+partir\s+de\s+(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})",
        r"vigência\s+(?:a\s+partir\s+de\s+)?(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})",
    ]
    for padrao in padroes:
        m = re.search(padrao, texto, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def _cruzar_politicas(
    temas: List[str],
    texto_normativo: str,
    politicas_lista: List[Dict],
) -> List[PoliticaImpactada]:
    """
    Cruza temas identificados e texto do normativo com políticas internas.
    Retorna políticas potencialmente impactadas.
    """
    impactadas = []
    texto_lower = texto_normativo.lower()

    for pol in politicas_lista:
        gatilhos = pol.get("gatilhos", "").lower()
        nome = pol.get("nome", "").lower()
        codigo = pol.get("codigo", "")

        # Verificar se algum tema ou palavra-chave dos gatilhos está presente
        relevante = False
        acao = "Revisar para adequação ao novo normativo"

        # Temas APLICÁVEL têm mais peso
        for tema in temas:
            kw = tema.split("] ")[-1].strip().lower()
            if kw in gatilhos or kw in nome:
                relevante = True
                acao = f"Verificar impacto do normativo nos procedimentos cobertos por {codigo}"
                break

        # Verificar keywords diretamente no texto dos gatilhos da política
        if not relevante:
            for kw in [
                "pix", "pagamento", "crédito", "pld", "lgpd", "fraude",
                "segurança cibernética", "consumidor", "tarifas", "cosif",
                "cadoc", "patrimônio", "governança", "risco",
            ]:
                if kw in texto_lower and kw in gatilhos:
                    relevante = True
                    break

        if relevante:
            impactadas.append(PoliticaImpactada(
                codigo=codigo,
                nome=pol.get("nome", ""),
                area_responsavel=pol.get("area_responsavel", ""),
                acao_sugerida=acao,
            ))

    return impactadas


def classificar_normativo(
    normativo: Normativo,
    config: Optional[Dict] = None,
) -> ClassificacaoNormativo:
    """
    Classifica a aplicabilidade de um normativo ao iFood Pago usando o reasoning layer.

    Aplica a árvore de decisão do REASONING_LAYER.md em 5 passos:
      1. Identifica tipo e escopo da norma
      2. Verifica se atinge o iFood Pago (IP, SCD, conglomerado Tipo 3, S5)
      3. Verifica tema vs. produtos do iFood Pago
      4. Classifica: APLICÁVEL / MONITORAR / NÃO APLICÁVEL
      5. Identifica políticas internas impactadas

    Entradas:
        normativo (Normativo): Normativo capturado (com texto_integral).
        config (dict): Configuração. Se None, carrega do config.json.

    Saídas:
        ClassificacaoNormativo: Resultado estruturado da análise.
    """
    cfg = _carregar_config(config)

    # Carregar arquivos de contexto
    reasoning_md = _carregar_arquivo(cfg.get("reasoning_layer_path", "data/normativos-bcb/REASONING_LAYER.md"))
    politicas_md = _carregar_arquivo(cfg.get("politicas_path", "data/normativos-bcb/REASONING_LAYER_POLITICAS.md"))
    feedback_md = _carregar_arquivo(cfg.get("feedback_path", "data/normativos-bcb/FEEDBACK.md"))

    politicas_lista = _extrair_politicas_do_md(politicas_md)
    keywords_ap = cfg.get("keywords_aplicavel", [])
    keywords_mon = cfg.get("keywords_monitorar", [])

    # Texto unificado para análise
    texto_analise = " ".join([
        normativo.titulo,
        normativo.ementa,
        normativo.texto_integral[:5000],  # Primeiros 5000 chars do texto integral
    ]).lower()

    # ──────────────────────────────────────────────────────────────────────────
    # PASSO 1 — Tipo e escopo declarado
    # ──────────────────────────────────────────────────────────────────────────
    passo1_tipo = f"{normativo.tipo} nº {normativo.numero} ({normativo.ano_norma})"

    # ──────────────────────────────────────────────────────────────────────────
    # PASSO 2 — Verificar se atinge iFood Pago
    # ──────────────────────────────────────────────────────────────────────────
    razoes_atinge = []
    for entidade in ENTIDADES_IFOOD:
        if entidade.lower() in texto_analise:
            razoes_atinge.append(entidade)

    # Verificar exclusões (fora do escopo)
    fora_escopo_encontrado = [f for f in FORA_ESCOPO if f.lower() in texto_analise]
    atinge_ifood = bool(razoes_atinge)

    # ──────────────────────────────────────────────────────────────────────────
    # PASSO 3 — Verificar tema vs. produtos iFood
    # ──────────────────────────────────────────────────────────────────────────
    temas = _identificar_temas(texto_analise, keywords_ap, keywords_mon)
    temas_aplicavel = [t for t in temas if "[APLICÁVEL]" in t]
    temas_monitorar = [t for t in temas if "[MONITORAR]" in t]

    # ──────────────────────────────────────────────────────────────────────────
    # PASSO 4 — Classificação
    # ──────────────────────────────────────────────────────────────────────────
    if atinge_ifood and temas_aplicavel:
        classificacao = APLICAVEL
        confianca = "ALTA" if len(razoes_atinge) >= 2 or len(temas_aplicavel) >= 3 else "MÉDIA"
        justificativa = (
            f"A norma menciona explicitamente entidades/atividades do iFood Pago "
            f"({', '.join(razoes_atinge[:3])}) e aborda temas diretamente aplicáveis: "
            f"{', '.join(t.split('] ')[-1] for t in temas_aplicavel[:3])}."
        )
    elif atinge_ifood and temas_monitorar:
        classificacao = MONITORAR
        confianca = "MÉDIA"
        justificativa = (
            f"A norma menciona entidades relacionadas ao iFood Pago "
            f"({', '.join(razoes_atinge[:2])}) mas aborda temas de monitoramento: "
            f"{', '.join(t.split('] ')[-1] for t in temas_monitorar[:3])}."
        )
    elif not atinge_ifood and temas_aplicavel and not fora_escopo_encontrado:
        classificacao = MONITORAR
        confianca = "MÉDIA"
        justificativa = (
            f"A norma aborda temas relevantes ao iFood Pago "
            f"({', '.join(t.split('] ')[-1] for t in temas_aplicavel[:3])}) "
            f"mas não menciona explicitamente as entidades do conglomerado. Monitorar."
        )
    elif fora_escopo_encontrado and not razoes_atinge:
        classificacao = NAO_APLICAVEL
        confianca = "ALTA"
        justificativa = (
            f"A norma aborda exclusivamente temas fora do escopo do iFood Pago: "
            f"{', '.join(fora_escopo_encontrado[:3])}."
        )
    elif not temas and not razoes_atinge:
        classificacao = NAO_APLICAVEL
        confianca = "MÉDIA"
        justificativa = "Nenhum tema ou entidade relevante ao iFood Pago identificado na norma."
    else:
        classificacao = MONITORAR
        confianca = "BAIXA"
        justificativa = "Análise inconclusiva. Recomenda-se leitura manual da norma."

    # ──────────────────────────────────────────────────────────────────────────
    # PASSO 5 — Políticas internas impactadas
    # ──────────────────────────────────────────────────────────────────────────
    politicas_impactadas = []
    if classificacao in (APLICAVEL, MONITORAR):
        politicas_impactadas = _cruzar_politicas(
            temas_aplicavel + temas_monitorar,
            texto_analise,
            politicas_lista,
        )

    # Data de vigência
    data_vigencia = _extrair_data_vigencia(normativo.texto_integral or normativo.ementa)

    # Verificar feedback
    feedback_aplicado, feedback_notas = _verificar_feedback(normativo, feedback_md)

    return ClassificacaoNormativo(
        normativo_id=normativo.id,
        normativo_titulo=normativo.titulo,
        classificacao=classificacao,
        confianca=confianca,
        justificativa=justificativa,
        passo1_tipo=passo1_tipo,
        passo2_atinge_ifood=atinge_ifood,
        passo2_razoes=razoes_atinge,
        passo3_temas=temas,
        passo4_classificacao=classificacao,
        passo5_politicas=politicas_impactadas,
        data_vigencia=data_vigencia,
        feedback_aplicado=feedback_aplicado,
        feedback_notas=feedback_notas,
    )
