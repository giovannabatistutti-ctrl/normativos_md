#!/usr/bin/env python3
"""
Entry point — Skill normativos-bcb  (orquestrador completo)
Pipeline de monitoramento de normativos BCB para o iFood Pago.

Uso:
    python3 skills/normativos-bcb/init.py [--ano 2026] [--sem-integra] [--dry-run] [--ids ID1,ID2]

Opções:
    --ano ANO           Ano a monitorar (padrão: ano atual)
    --sem-integra       Não buscar texto integral das normas (mais rápido)
    --dry-run           Executar sem enviar para Slack/GitHub
    --ids ID1,ID2       Processar apenas os IDs específicos
    --config CAMINHO    Caminho para config.json customizado

Exemplo:
    python3 skills/normativos-bcb/init.py --ano 2026
    python3 skills/normativos-bcb/init.py --dry-run
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# ── Path setup ────────────────────────────────────────────────────────────────
_SKILL_DIR = Path(__file__).parent
sys.path.insert(0, str(_SKILL_DIR))

# ── Módulos da skill ──────────────────────────────────────────────────────────
from modules.captura import capturar_normativos, Normativo
from modules.reasoning import classificar_normativo, ClassificacaoNormativo
from modules.avaliacao_risco import avaliar_risco, AvaliacaoRisco
from modules.resumo import gerar_resumo, ResumoExecutivo
from modules.responsaveis import mapear_responsaveis, Responsavel
from modules.persistencia import salvar_analise, push_planilha
from modules.notificacao import enviar_notificacao_slack

# ── Timezone ──────────────────────────────────────────────────────────────────
BRASILIA = timezone(timedelta(hours=-3))


# ─────────────────────────────────────────────────────────────────────────────
# Configuração / carregamento
# ─────────────────────────────────────────────────────────────────────────────

def carregar_config(config_path: Optional[str] = None) -> dict:
    """Carrega configuração do config.json."""
    if config_path:
        p = Path(config_path)
    else:
        p = _SKILL_DIR / "config.json"

    if not p.exists():
        raise FileNotFoundError(f"config.json não encontrado: {p}")

    return json.loads(p.read_text(encoding="utf-8"))


def carregar_enviados(config: dict) -> dict:
    """Carrega enviados.json (anti-duplicata)."""
    enviados_path = Path(config.get("enviados_path", "data/normativos-bcb/enviados.json"))
    if enviados_path.exists():
        try:
            return json.loads(enviados_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


# ─────────────────────────────────────────────────────────────────────────────
# Log de execução
# ─────────────────────────────────────────────────────────────────────────────

def _log_path() -> Path:
    """Retorna o caminho do arquivo de log desta execução."""
    agora = datetime.now(BRASILIA)
    logs_dir = Path("data/normativos-bcb/logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    nome = f"pipeline_{agora.strftime('%Y-%m-%d_%Hh%M')}.log"
    return logs_dir / nome


def criar_logger(log_path: Path) -> logging.Logger:
    """Configura logger que escreve no arquivo e no stdout."""
    logger = logging.getLogger("normativos_bcb")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")

    # Handler arquivo
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # Handler console
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return logger


# ─────────────────────────────────────────────────────────────────────────────
# Backlog NÃO APLICÁVEL
# ─────────────────────────────────────────────────────────────────────────────

def registrar_nao_aplicavel(normativo: Normativo, classificacao: ClassificacaoNormativo) -> None:
    """Registra normativo NÃO APLICÁVEL no backlog local CSV."""
    backlog_dir = Path("data/normativos-bcb")
    backlog_dir.mkdir(parents=True, exist_ok=True)
    backlog_path = backlog_dir / "backlog_nao_aplicaveis.csv"

    escrever_cabecalho = not backlog_path.exists()

    with open(backlog_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "data_registro",
            "normativo_id",
            "tipo",
            "numero",
            "titulo",
            "data_publicacao",
            "link",
            "classificacao",
            "confianca",
            "justificativa",
        ])
        if escrever_cabecalho:
            writer.writeheader()

        writer.writerow({
            "data_registro": datetime.now(BRASILIA).strftime("%Y-%m-%d %H:%M"),
            "normativo_id": normativo.id,
            "tipo": normativo.tipo,
            "numero": normativo.numero,
            "titulo": normativo.titulo[:200],
            "data_publicacao": normativo.data_publicacao,
            "link": normativo.link,
            "classificacao": classificacao.classificacao,
            "confianca": classificacao.confianca,
            "justificativa": classificacao.justificativa[:300],
        })


# ─────────────────────────────────────────────────────────────────────────────
# Processamento de um normativo
# ─────────────────────────────────────────────────────────────────────────────

def processar_normativo(
    normativo: Normativo,
    config: dict,
    dry_run: bool = False,
    logger: Optional[logging.Logger] = None,
) -> dict:
    """
    Executa o pipeline completo para um único normativo:

      Módulo 1 (captura)        — já executado antes desta função
      Módulo 2 (reasoning)      → classificação + políticas impactadas
      Se APLICÁVEL ou MONITORAR:
        Módulo 3 (avaliacao)    → 5 pilares
        Módulo 4 (resumo)       → resumo executivo
        Módulo 5 (responsaveis) → áreas/times
        Módulo 6 (persistencia) → JSON local + GitHub
        Módulo 7 (notificacao)  → Slack
      Se NÃO APLICÁVEL:
        Registra em backlog CSV
        Notificação simples "Sem aplicabilidade"

    Retorna dict com resultado de cada etapa.
    """
    log = logger or logging.getLogger("normativos_bcb")
    resultado: dict = {"normativo_id": normativo.id, "titulo": normativo.titulo}

    # ── Módulo 2 — Reasoning ─────────────────────────────────────────────────
    try:
        classificacao = classificar_normativo(normativo, config=config)
        resultado["classificacao"] = classificacao.classificacao
        resultado["confianca"] = classificacao.confianca
        log.info(f"  ✅ [2-reasoning] {classificacao.classificacao} (conf: {classificacao.confianca})")
    except Exception as exc:
        log.error(f"  ❌ [2-reasoning] Erro: {exc}", exc_info=True)
        resultado["erro_reasoning"] = str(exc)
        # Não há como continuar sem classificação
        return resultado

    # ── Ramificação por classificação ────────────────────────────────────────
    if classificacao.classificacao == "NÃO APLICÁVEL":
        # Registrar no backlog
        try:
            registrar_nao_aplicavel(normativo, classificacao)
            log.info(f"  📋 [backlog] Registrado em backlog_nao_aplicaveis.csv")
            resultado["backlog"] = "registrado"
        except Exception as exc:
            log.warning(f"  ⚠️  [backlog] Erro ao registrar backlog: {exc}")
            resultado["backlog_erro"] = str(exc)

        # Notificação simples "Sem aplicabilidade"
        if not dry_run:
            try:
                notif = enviar_notificacao_slack(
                    normativo, classificacao,
                    avaliacao=None,
                    resumo=None,
                    responsaveis=[],
                    resultado_persistencia={},
                    config=config,
                )
                resultado["slack"] = notif.get("success", False)
                if notif.get("skipped"):
                    log.info(f"  ⏭️  [7-slack] Suprimido: {notif.get('reason')}")
                elif notif.get("success"):
                    log.info(f"  ✅ [7-slack] Notificação enviada (Sem aplicabilidade)")
                else:
                    log.warning(f"  ❌ [7-slack] Erro: {notif.get('error', '')[:100]}")
            except Exception as exc:
                log.warning(f"  ⚠️  [7-slack] Erro ao notificar NÃO APLICÁVEL: {exc}")
                resultado["slack_erro"] = str(exc)
        else:
            log.info("  🔸 Dry-run: slack ignorado")
            resultado["slack"] = {"dry_run": True}

        return resultado

    # A partir daqui: APLICÁVEL ou MONITORAR
    # ── Módulo 3 — Avaliação de risco ────────────────────────────────────────
    avaliacao: Optional[AvaliacaoRisco] = None
    try:
        avaliacao = avaliar_risco(normativo, classificacao, config=config)
        resultado["score"] = avaliacao.score_consolidado
        log.info(f"  ✅ [3-avaliacao] Criticidade: {avaliacao.score_consolidado}")
    except Exception as exc:
        log.error(f"  ❌ [3-avaliacao] Erro: {exc}", exc_info=True)
        resultado["erro_avaliacao"] = str(exc)

    # ── Módulo 5 — Responsáveis (antes do resumo — resumo precisa da lista) ──
    responsaveis_lista: List[Responsavel] = []
    try:
        responsaveis_lista = mapear_responsaveis(normativo, classificacao, avaliacao, config=config)
        resultado["responsaveis"] = len(responsaveis_lista)
        log.info(f"  ✅ [5-responsaveis] {len(responsaveis_lista)} mapeado(s)")
    except Exception as exc:
        log.error(f"  ❌ [5-responsaveis] Erro: {exc}", exc_info=True)
        resultado["erro_responsaveis"] = str(exc)

    # ── Módulo 4 — Resumo executivo ─────────────────────────────────────────
    resumo: Optional[ResumoExecutivo] = None
    try:
        resumo = gerar_resumo(normativo, classificacao, avaliacao, responsaveis_lista, config=config)
        resultado["resumo_ok"] = True
        n_acoes = len(resumo.acoes_requeridas) if resumo else 0
        log.info(f"  ✅ [4-resumo] Gerado ({n_acoes} ação(ões))")
    except Exception as exc:
        log.error(f"  ❌ [4-resumo] Erro: {exc}", exc_info=True)
        resultado["erro_resumo"] = str(exc)

    persist_result: dict = {}

    if not dry_run:
        # ── Módulo 6 — Persistência ──────────────────────────────────────────
        try:
            persist_result = salvar_analise(
                normativo, classificacao, avaliacao, resumo, responsaveis_lista, config=config
            )
            resultado["persistencia"] = {
                "local_json": persist_result.get("local_json"),
                "github_json": persist_result.get("github_json", {}).get("success", False),
                "github_md": persist_result.get("github_md", {}).get("success", False),
            }
            log.info(f"  ✅ [6-persistencia] Salvo localmente e no GitHub")
        except Exception as exc:
            log.error(f"  ❌ [6-persistencia] Erro: {exc}", exc_info=True)
            resultado["erro_persistencia"] = str(exc)
            resultado["persistencia"] = {"erro": str(exc)}

        # ── Módulo 7 — Notificação Slack ─────────────────────────────────────
        try:
            notif_result = enviar_notificacao_slack(
                normativo, classificacao, avaliacao, resumo, responsaveis_lista,
                persist_result, config=config,
            )
            resultado["slack"] = notif_result.get("success", False)
            if notif_result.get("skipped"):
                log.info(f"  ⏭️  [7-slack] Suprimido: {notif_result.get('reason')}")
            elif notif_result.get("success"):
                log.info(f"  ✅ [7-slack] Notificação enviada")
            else:
                log.warning(f"  ❌ [7-slack] Erro: {notif_result.get('error', '')[:100]}")
        except Exception as exc:
            log.error(f"  ❌ [7-slack] Erro ao notificar: {exc}", exc_info=True)
            resultado["slack_erro"] = str(exc)
    else:
        log.info("  🔸 Dry-run: persistência e notificação ignoradas")
        resultado["persistencia"] = {"dry_run": True}
        resultado["slack"] = {"dry_run": True}

    return resultado


# ─────────────────────────────────────────────────────────────────────────────
# Geração do relatório de log estruturado
# ─────────────────────────────────────────────────────────────────────────────

def gerar_relatorio_log(
    resultados: List[dict],
    inicio: datetime,
    normativos: List[Normativo],
    dry_run: bool,
    log_path: Path,
) -> None:
    """Grava relatório markdown de execução no log_path."""
    agora = datetime.now(BRASILIA)
    duracao = int((agora - inicio).total_seconds())

    aplicaveis = sum(1 for r in resultados if r.get("classificacao") == "APLICÁVEL")
    monitorar = sum(1 for r in resultados if r.get("classificacao") == "MONITORAR")
    nao_aplic = sum(1 for r in resultados if r.get("classificacao") == "NÃO APLICÁVEL")
    erros = sum(1 for r in resultados if any(k.startswith("erro_") for k in r))

    linhas = [
        f"# Log Pipeline normativos-bcb — {agora.strftime('%Y-%m-%d %Hh%M')}",
        "",
        f"**Início:** {inicio.strftime('%Y-%m-%d %H:%M:%S')} (Brasília)",
        f"**Fim:** {agora.strftime('%Y-%m-%d %H:%M:%S')} (Brasília)",
        f"**Duração:** {duracao}s",
        f"**Modo:** {'DRY-RUN' if dry_run else 'PRODUÇÃO'}",
        "",
        "---",
        "",
        "## Sumário",
        "",
        f"| Categoria | Qtd |",
        f"|---|---|",
        f"| 🔴 APLICÁVEL | {aplicaveis} |",
        f"| 🟡 MONITORAR | {monitorar} |",
        f"| 🟢 NÃO APLICÁVEL | {nao_aplic} |",
        f"| ❌ COM ERROS | {erros} |",
        f"| 📋 TOTAL | {len(resultados)} |",
        "",
        "---",
        "",
        "## Normativos Processados",
        "",
    ]

    for i, (norm, res) in enumerate(zip(normativos, resultados), 1):
        classif = res.get("classificacao", "ERRO")
        emoji = {"APLICÁVEL": "🔴", "MONITORAR": "🟡", "NÃO APLICÁVEL": "🟢"}.get(classif, "❌")
        linhas.append(f"### {i}. {emoji} {norm.titulo[:80]}")
        linhas.append(f"- **ID:** `{norm.id}`")
        linhas.append(f"- **Tipo:** {norm.tipo} nº {norm.numero}")
        linhas.append(f"- **Publicação:** {norm.data_publicacao}")
        linhas.append(f"- **Classificação:** {classif} (conf: {res.get('confianca', '-')})")
        if res.get("score"):
            linhas.append(f"- **Criticidade:** {res['score']}")
        if res.get("responsaveis"):
            linhas.append(f"- **Responsáveis:** {res['responsaveis']}")
        if res.get("persistencia") and isinstance(res["persistencia"], dict):
            p = res["persistencia"]
            if not p.get("dry_run"):
                linhas.append(f"- **GitHub JSON:** {'✅' if p.get('github_json') else '❌'}")
                linhas.append(f"- **GitHub MD:** {'✅' if p.get('github_md') else '❌'}")
        if res.get("slack") is True:
            linhas.append("- **Slack:** ✅")
        erros_etapa = [k for k in res if k.startswith("erro_")]
        if erros_etapa:
            linhas.append(f"- **Erros:** {', '.join(erros_etapa)}")
        linhas.append("")

    linhas += [
        "---",
        f"*Orquestrador normativos-bcb v4.0 — gerado em {agora.strftime('%Y-%m-%d %H:%M')} (Brasília)*",
    ]

    # Sobrescrever o arquivo de log com o relatório markdown
    log_path.write_text("\n".join(linhas), encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> Optional[List[dict]]:
    parser = argparse.ArgumentParser(
        description="Orquestrador normativos-bcb — iFood Pago Compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--ano", type=int, default=None,
                        help="Ano a monitorar (padrão: ano atual)")
    parser.add_argument("--sem-integra", action="store_true",
                        help="Não buscar texto integral (mais rápido)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Executar sem enviar para Slack/GitHub")
    parser.add_argument("--ids", type=str, default=None,
                        help="Processar apenas IDs específicos (vírgula)")
    parser.add_argument("--config", type=str, default=None,
                        help="Caminho para config.json customizado")
    args = parser.parse_args()

    # ── Setup de log ──────────────────────────────────────────────────────────
    log_path = _log_path()
    logger = criar_logger(log_path)
    inicio = datetime.now(BRASILIA)

    logger.info("=" * 60)
    logger.info("🔍 Orquestrador normativos-bcb | iFood Pago Compliance")
    logger.info(f"⏰ {inicio.strftime('%Y-%m-%d %H:%M')} (Brasília)")
    if args.dry_run:
        logger.info("🔸 MODO DRY-RUN — sem Slack/GitHub")
    logger.info("=" * 60)

    # ── 1. Carregar configurações ─────────────────────────────────────────────
    try:
        config = carregar_config(args.config)
        logger.info("✅ [config] Configuração carregada")
    except Exception as exc:
        logger.error(f"❌ [config] Erro ao carregar config: {exc}")
        sys.exit(1)

    # ── 2. Carregar enviados.json ─────────────────────────────────────────────
    enviados = carregar_enviados(config)
    logger.info(f"📋 [enviados] {len(enviados)} normativo(s) já processado(s) (anti-duplicata)")

    ano = args.ano or datetime.now(BRASILIA).year
    logger.info(f"📡 Capturando normativos do ano {ano}...")

    # ── Módulo 1 — Captura ───────────────────────────────────────────────────
    try:
        normativos = capturar_normativos(
            ano=ano,
            enviados=enviados,
            config=config,
            buscar_integra=not args.sem_integra,
        )
        logger.info(f"✅ [1-captura] {len(normativos)} normativo(s) novo(s) capturado(s)")
    except Exception as exc:
        logger.error(f"❌ [1-captura] Erro na captura: {exc}", exc_info=True)
        sys.exit(1)

    # Filtrar por IDs específicos se solicitado
    if args.ids:
        ids_filtro = set(args.ids.split(","))
        normativos = [n for n in normativos if n.id in ids_filtro]
        logger.info(f"🔍 Filtro por IDs: {len(normativos)} normativo(s) após filtro")

    if not normativos:
        logger.info("✅ Nenhum normativo novo para processar.")
        # Ainda gravar relatório vazio
        gerar_relatorio_log([], inicio, [], args.dry_run, log_path)
        return []

    # ── Processar cada normativo ──────────────────────────────────────────────
    resultados: List[dict] = []
    for i, normativo in enumerate(normativos, 1):
        logger.info(f"\n[{i}/{len(normativos)}] {normativo.titulo[:80]}")
        logger.info(f"  ID: {normativo.id} | Link: {normativo.link}")
        try:
            res = processar_normativo(normativo, config, dry_run=args.dry_run, logger=logger)
        except Exception as exc:
            logger.error(f"  ❌ Erro fatal ao processar normativo {normativo.id}: {exc}",
                         exc_info=True)
            res = {"normativo_id": normativo.id, "titulo": normativo.titulo,
                   "erro_fatal": str(exc)}
        resultados.append(res)

    # ── Sumário ───────────────────────────────────────────────────────────────
    logger.info("\n" + "=" * 60)
    logger.info("📊 SUMÁRIO FINAL")
    logger.info("=" * 60)
    aplicaveis = sum(1 for r in resultados if r.get("classificacao") == "APLICÁVEL")
    monitorar  = sum(1 for r in resultados if r.get("classificacao") == "MONITORAR")
    nao_aplic  = sum(1 for r in resultados if r.get("classificacao") == "NÃO APLICÁVEL")
    erros      = sum(1 for r in resultados if any(k.startswith("erro") for k in r))
    logger.info(f"  🔴 APLICÁVEL:     {aplicaveis}")
    logger.info(f"  🟡 MONITORAR:     {monitorar}")
    logger.info(f"  🟢 NÃO APLICÁVEL: {nao_aplic}")
    logger.info(f"  ❌ COM ERROS:     {erros}")
    logger.info(f"  📋 TOTAL:         {len(resultados)}")
    logger.info(f"\n📝 Log salvo em: {log_path}")
    logger.info("✅ Pipeline concluído.")

    # ── Gravar relatório markdown no log ─────────────────────────────────────
    gerar_relatorio_log(resultados, inicio, normativos, args.dry_run, log_path)

    # ── Push planilha para GitHub ─────────────────────────────────────────────
    if not args.dry_run:
        try:
            planilha_result = push_planilha(config)
            if planilha_result.get("status") == "ok":
                logger.info("✅ [planilha] normativos_radar.xlsx enviada ao GitHub")
            else:
                logger.warning(f"⚠️  [planilha] Erro ao enviar planilha: {planilha_result.get('msg', '')}")
        except Exception as exc:
            logger.warning(f"⚠️  [planilha] Exceção ao enviar planilha: {exc}")
    else:
        logger.info("🔸 Dry-run: push da planilha ignorado")

    return resultados


if __name__ == "__main__":
    main()
