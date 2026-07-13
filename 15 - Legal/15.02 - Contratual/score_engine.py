"""
score_engine.py
===============
Motor de cálculo do score de confiança do aditamento — Fase 4.

Score de confiança (0.0 a 1.0) calculado com base em 5 fatores ponderados:
  - completude_dados    (0.35): campos obrigatórios todos preenchidos
  - match_historico     (0.20): casos similares bem-sucedidos no DECISION_AUDIT.csv
  - conformidade_regras (0.20): regras do DECISION_LAYER satisfeitas
  - clareza_pedido      (0.15): descrição do ticket clara e sem contradições
  - modulos_conhecidos  (0.10): todos os módulos selecionados existem no catálogo

REGRA ABSOLUTA: score = 0.0 se len(campos_pendentes) > 0.
Threshold autônomo: 0.90.

Calibração dos pesos (Opção A — v2):
  Um ticket ISA completo (todos os 6 campos obrigatórios preenchidos, zero regras violadas,
  todos os módulos no catálogo, descrição > 100 chars) com match_historico neutro (0.5)
  atinge exatamente score = 0.90:
    completude(1.0 × 0.35) + historico(0.5 × 0.20) + regras(1.0 × 0.20)
    + clareza(1.0 × 0.15) + modulos(1.0 × 0.10) = 0.35 + 0.10 + 0.20 + 0.15 + 0.10 = 0.90

Histórico — tratamento de entradas dry_run:
  Entradas com status_final == "dry_run" são ignoradas no cálculo de match_historico.
  Se não houver casos reais (apenas dry_run ou CSV vazio), retorna 0.5 (neutro).
"""

import csv
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

THRESHOLD = 0.90

PESOS = {
    "completude_dados": 0.35,    # Aumentado de 0.30 → 0.35 (Opção A, v2)
    "match_historico": 0.20,     # Reduzido de 0.25 → 0.20 (Opção A, v2)
    "conformidade_regras": 0.20,
    "clareza_pedido": 0.15,
    "modulos_conhecidos": 0.10,
}

# Módulos conhecidos do catálogo (IDs numéricos)
MODULOS_CATALOGADOS = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}

# Módulos como nomes de arquivo (sem .md)
MODULOS_CATALOGADOS_NOMES = {
    "01_cabecalho", "02_prorrogacao_vigencia", "03_retirada_renovacao_automatica",
    "04_aviso_previo", "05_cessao", "06_alteracao_produto", "07_alteracao_valor",
    "08_rodape_assinaturas", "09_clausula_geral", "10_isa", "11_saldo_extra",
    "12_saldo_natal",
}

# Campos obrigatórios globais (REGRA-07)
CAMPOS_OBRIGATORIOS_GLOBAIS = {
    "RAZAO_SOCIAL", "CNPJ_EMPRESA", "ENDERECO_EMPRESA",
    "CEP_EMPRESA", "DATA_CONTRATO_ORIGINAL", "DATA_ADITIVO",
}

# Regras do DECISION_LAYER com identificador
REGRAS_DECISION_LAYER = [
    "REGRA-01",  # ISA exige Proposta Comercial
    "REGRA-02",  # Saldo Natal — responsabilidade do cliente
    "REGRA-03",  # Aviso prévio — validação numérica e de consistência
    "REGRA-04",  # Terminologia canônica obrigatória
    "REGRA-05",  # Duplo aditamento — documento consolidado
    "REGRA-06",  # Exclusão mútua — Módulos de Prorrogação
    "REGRA-07",  # Campos obrigatórios globais
    "REGRA-08",  # Produto não mapeado
    "REGRA-09",  # CNPJ válido
    "REGRA-10",  # Colab+ exige confirmação
]

# Caminho padrão do DECISION_AUDIT.csv
_BASE_DIR = Path(__file__).parent.parent
AUDIT_CSV_PATH = _BASE_DIR / "data" / "audit" / "DECISION_AUDIT.csv"

# Status que identificam entradas de teste/simulação (não contam como histórico real)
STATUS_DRY_RUN = {"dry_run", "teste", "simulacao"}


# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------

def calcular_score(analise: dict) -> dict:
    """
    Calcula score de confiança (0.0 a 1.0) para o aditamento montado.

    Args:
        analise: dict retornado por amendment_assembler.montar_aditamento()
                 Deve conter: campos_pendentes, variaveis, modulos_selecionados,
                              regras_violadas, ticket (com summary/description),
                              modulos_md.

    Returns:
        dict com score, decisao, threshold, detalhamento, campos_pendentes,
        regras_violadas, justificativa.
    """
    campos_pendentes: List[str] = analise.get("campos_pendentes", [])
    regras_violadas: List[str] = analise.get("regras_violadas", [])
    modulos_selecionados: List[str] = analise.get("modulos_selecionados", [])
    variaveis: Dict[str, Any] = analise.get("variaveis", {})
    ticket: dict = analise.get("ticket", {})
    historico_ticket_key: str = ticket.get("key", "") if ticket else ""
    produto: str = ticket.get("produto", "") if ticket else ""

    # -----------------------------------------------------------------------
    # REGRA ABSOLUTA: qualquer campo PENDENTE → score = 0.0
    # -----------------------------------------------------------------------
    if campos_pendentes:
        return _build_result(
            score=0.0,
            detalhamento={f: 0.0 for f in PESOS},
            campos_pendentes=campos_pendentes,
            regras_violadas=regras_violadas,
            justificativa=(
                f"Score zerado automaticamente: {len(campos_pendentes)} campo(s) PENDENTE(s) "
                f"encontrado(s): {', '.join(campos_pendentes)}. "
                "Nenhum campo pode estar PENDENTE para aprovação autônoma."
            ),
        )

    # -----------------------------------------------------------------------
    # Fator 1 — completude_dados (peso 0.35)
    # -----------------------------------------------------------------------
    score_completude = _calcular_completude(variaveis)

    # -----------------------------------------------------------------------
    # Fator 2 — match_historico (peso 0.20)
    # -----------------------------------------------------------------------
    score_historico = _calcular_match_historico(historico_ticket_key, produto)

    # -----------------------------------------------------------------------
    # Fator 3 — conformidade_regras (peso 0.20)
    # -----------------------------------------------------------------------
    score_regras = _calcular_conformidade_regras(regras_violadas)

    # -----------------------------------------------------------------------
    # Fator 4 — clareza_pedido (peso 0.15)
    # -----------------------------------------------------------------------
    score_clareza = _calcular_clareza_pedido(ticket)

    # -----------------------------------------------------------------------
    # Fator 5 — modulos_conhecidos (peso 0.10)
    # -----------------------------------------------------------------------
    score_modulos = _calcular_modulos_conhecidos(modulos_selecionados)

    # -----------------------------------------------------------------------
    # Score ponderado final
    # -----------------------------------------------------------------------
    detalhamento = {
        "completude_dados": round(score_completude, 4),
        "match_historico": round(score_historico, 4),
        "conformidade_regras": round(score_regras, 4),
        "clareza_pedido": round(score_clareza, 4),
        "modulos_conhecidos": round(score_modulos, 4),
    }

    score_final = sum(
        detalhamento[fator] * peso
        for fator, peso in PESOS.items()
    )
    score_final = round(min(1.0, max(0.0, score_final)), 4)

    # Se alguma regra de SCORE=0 foi violada, zerar
    if regras_violadas:
        score_final = 0.0

    justificativa = _montar_justificativa(score_final, detalhamento, campos_pendentes, regras_violadas)

    return _build_result(
        score=score_final,
        detalhamento=detalhamento,
        campos_pendentes=campos_pendentes,
        regras_violadas=regras_violadas,
        justificativa=justificativa,
    )


# ---------------------------------------------------------------------------
# Helpers de cálculo por fator
# ---------------------------------------------------------------------------

def _calcular_completude(variaveis: dict) -> float:
    """
    Fator completude_dados (0.35).
    1.0 se todos campos obrigatórios preenchidos sem PENDENTE.
    Proporcional se parcial. 0.0 se qualquer PENDENTE detectado.
    """
    if not variaveis:
        return 0.0

    obrigatorios_presentes = 0
    obrigatorios_total = len(CAMPOS_OBRIGATORIOS_GLOBAIS)

    for campo in CAMPOS_OBRIGATORIOS_GLOBAIS:
        v = variaveis.get(campo)
        if v is None:
            continue
        valor = v.get("valor", "") if isinstance(v, dict) else str(v)
        if valor and "PENDENTE:" not in str(valor):
            obrigatorios_presentes += 1

    if obrigatorios_total == 0:
        return 1.0

    completude = obrigatorios_presentes / obrigatorios_total

    # Verificar se há qualquer PENDENTE em qualquer variável
    for campo, v in variaveis.items():
        valor = v.get("valor", "") if isinstance(v, dict) else str(v)
        if "PENDENTE:" in str(valor):
            return 0.0

    return completude


def _calcular_match_historico(ticket_key: str, produto: str) -> float:
    """
    Fator match_historico (0.20).
    Lê DECISION_AUDIT.csv, calcula % de casos similares bem-sucedidos.

    Entradas com status_final == "dry_run" (ou outros valores de STATUS_DRY_RUN)
    são ignoradas — tratadas como neutras, não como falhas.

    Se não houver casos reais (apenas dry_run ou CSV vazio), retorna 0.5 (neutro).
    Nunca retorna 0.0 apenas por falta de histórico real.
    """
    if not AUDIT_CSV_PATH.exists():
        return 0.5

    try:
        with open(AUDIT_CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as exc:
        logger.warning("Erro ao ler DECISION_AUDIT.csv: %s", exc)
        return 0.5

    if not rows:
        return 0.5

    # Filtrar entradas dry_run — não contam como histórico real
    rows_reais = [
        r for r in rows
        if r.get("status_final", "").lower().strip() not in STATUS_DRY_RUN
    ]

    # Se não houver casos reais, retornar neutro (0.5) — sem penalizar
    if not rows_reais:
        logger.debug(
            "match_historico: CSV possui %d entradas, todas dry_run — retornando neutro 0.5",
            len(rows),
        )
        return 0.5

    # Filtrar casos similares (mesmo produto ou qualquer caso se produto vazio)
    casos_similares = [
        r for r in rows_reais
        if not produto or (r.get("produto", "") == produto)
    ]

    if not casos_similares:
        casos_similares = rows_reais  # fallback: todos os casos reais

    sucessos = [
        r for r in casos_similares
        if r.get("status_final", "").lower() in ("sucesso", "aprovado", "autonomo")
    ]

    return round(len(sucessos) / len(casos_similares), 4)


def _calcular_conformidade_regras(regras_violadas: List[str]) -> float:
    """
    Fator conformidade_regras (0.20).
    1.0 se zero regras violadas. -0.2 por regra violada (mínimo 0).
    """
    if not regras_violadas:
        return 1.0
    penalidade = 0.2 * len(regras_violadas)
    return max(0.0, 1.0 - penalidade)


def _calcular_clareza_pedido(ticket: dict) -> float:
    """
    Fator clareza_pedido (0.15).
    1.0: descrição > 100 chars e sem contradições.
    0.5: ticket vago/curto.
    0.0: contradição detectada.
    """
    if not ticket:
        return 0.5

    summary = ticket.get("summary", "") or ""
    description = ticket.get("description", "") or ""
    texto_completo = summary + " " + description

    # Detectar contradições explícitas
    contradicoes = _detectar_contradicoes(texto_completo)
    if contradicoes:
        return 0.0

    # Clareza por tamanho
    if len(texto_completo.strip()) > 100:
        return 1.0

    return 0.5


def _detectar_contradicoes(texto: str) -> List[str]:
    """
    Detecta padrões de contradição no texto do ticket.
    Retorna lista de contradições encontradas.
    """
    contradicoes = []
    texto_lower = texto.lower()

    # Exemplo: prorrogar E remover prorrogação
    if "prorrog" in texto_lower and "remov" in texto_lower and "prorrog" in texto_lower:
        if re.search(r"(remov|retir).{0,50}prorrog", texto_lower) and \
           re.search(r"prorrog.{0,50}(manter|manutenção)", texto_lower):
            contradicoes.append("prorrogar_e_remover_prorrogacao")

    return contradicoes


def _calcular_modulos_conhecidos(modulos_selecionados: List[str]) -> float:
    """
    Fator modulos_conhecidos (0.10).
    1.0 se todos módulos estão no catálogo. 0.0 se qualquer desconhecido.
    """
    if not modulos_selecionados:
        return 1.0

    for modulo in modulos_selecionados:
        modulo_str = str(modulo).replace(".md", "")
        # Aceitar número inteiro ou nome de arquivo
        if isinstance(modulo, int) or (isinstance(modulo, str) and modulo.isdigit()):
            if int(modulo) not in MODULOS_CATALOGADOS:
                return 0.0
        else:
            # Comparar por nome (sem extensão, sem path)
            nome_base = Path(modulo_str).name
            if nome_base not in MODULOS_CATALOGADOS_NOMES:
                return 0.0

    return 1.0


# ---------------------------------------------------------------------------
# Helpers de resultado
# ---------------------------------------------------------------------------

def _build_result(
    score: float,
    detalhamento: dict,
    campos_pendentes: List[str],
    regras_violadas: List[str],
    justificativa: str,
) -> dict:
    """Monta o dict de retorno padronizado."""
    decisao = "AUTONOMO" if score >= THRESHOLD else "REVISAO_HUMANA"
    return {
        "score": round(score, 4),
        "decisao": decisao,
        "threshold": THRESHOLD,
        "detalhamento": detalhamento,
        "campos_pendentes": campos_pendentes,
        "regras_violadas": regras_violadas,
        "justificativa": justificativa,
    }


def _montar_justificativa(
    score: float,
    detalhamento: dict,
    campos_pendentes: List[str],
    regras_violadas: List[str],
) -> str:
    """Gera texto explicativo para o advogado."""
    partes = []

    if score >= THRESHOLD:
        partes.append(
            f"Score {score:.2f} ≥ {THRESHOLD} — aditamento aprovado para envio autônomo ao Netlex."
        )
    else:
        partes.append(
            f"Score {score:.2f} < {THRESHOLD} — revisão manual necessária antes do envio ao Netlex."
        )

    # Detalhamento por fator
    partes.append("Detalhamento por fator:")
    for fator, valor in detalhamento.items():
        peso = PESOS.get(fator, 0)
        contrib = round(valor * peso, 4)
        partes.append(f"  • {fator}: {valor:.2f} (peso {peso:.0%}, contribuição {contrib:.4f})")

    if campos_pendentes:
        partes.append(f"Campos PENDENTES ({len(campos_pendentes)}): {', '.join(campos_pendentes)}")

    if regras_violadas:
        partes.append(f"Regras violadas: {', '.join(regras_violadas)}")

    return " | ".join(partes)


# ---------------------------------------------------------------------------
# Compatibilidade com classe legada ScoreEngine (Fase 3)
# ---------------------------------------------------------------------------

class ScoreEngine:
    """Wrapper de classe para compatibilidade com pipeline_aditamentos.py."""

    def __init__(self, config: dict):
        self.threshold = config.get("score", {}).get("threshold_autonomo", THRESHOLD)

    def calculate(self, amendment: dict) -> dict:
        """
        Compatibilidade com API anterior. Delega para calcular_score().
        """
        return calcular_score(amendment)
