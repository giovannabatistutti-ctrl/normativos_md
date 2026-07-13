#!/usr/bin/env python3
"""
monitor_pos_revisao.py
======================
Monitor horário de pós-revisão — Pipeline 15-Aditamentos iFood Benefícios.

Executa a cada hora em dias úteis brasileiros.
Verifica tickets aguardando aprovação jurídica e notifica o time comercial
via Slack quando o advogado aprova no Jira.

Uso (chamado pela task recorrente):
    python3 monitor_pos_revisao.py

Retorna:
    0 — execução normal (0 ou mais tickets processados)
    1 — erro fatal
"""

import sys
import logging
import json
from datetime import datetime
from pathlib import Path

# Adicionar diretório raiz do app ao path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("monitor_pos_revisao")

LOG_DIR = Path(__file__).parent / "data" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def _e_dia_util_brasil() -> bool:
    """
    Verifica se hoje é dia útil no Brasil usando a skill dias-uteis-brasil.
    Fallback: considera dias úteis como segunda a sexta, sem feriados.
    """
    hoje = datetime.now()

    # Fallback rápido: fim de semana
    if hoje.weekday() >= 5:  # 5=Saturday, 6=Sunday
        return False

    # Tentar usar a skill de dias úteis
    try:
        skill_path = Path("/workspace/skills/dias-uteis-brasil/scripts/business_days.py")
        if skill_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("business_days", skill_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            # check_business_day(dt, time_str=None) → dict com is_business_day
            resultado = mod.check_business_day(hoje.date())
            return resultado.get("is_business_day", True)
    except Exception as exc:
        logger.warning("_e_dia_util_brasil: skill indisponível, usando fallback — %s", exc)

    # Fallback: seg-sex, sem verificação de feriados
    return True


def _registrar_log(resultado: dict) -> None:
    """Salva log de execução em JSON diário."""
    data_str = datetime.now().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"monitor_pos_revisao_{data_str}.log"

    entrada = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        **resultado
    }

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entrada, ensure_ascii=False) + "\n")


def main() -> int:
    agora = datetime.now()
    logger.info("=" * 60)
    logger.info("Monitor pós-revisão — %s", agora.strftime("%Y-%m-%d %H:%M"))

    # 1. Verificar se é dia útil
    if not _e_dia_util_brasil():
        logger.info("Não é dia útil — execução cancelada.")
        _registrar_log({"acao": "cancelado", "motivo": "nao_e_dia_util", "dia_semana": agora.strftime("%A")})
        return 0

    # 2. Executar verificação de pendentes
    logger.info("Verificando tickets aguardando aprovação...")

    try:
        from modules.pos_revisao import processar_pendentes
        resultado = processar_pendentes()
    except Exception as exc:
        logger.error("Erro fatal ao executar processar_pendentes: %s", exc, exc_info=True)
        _registrar_log({"acao": "erro", "motivo": str(exc)})
        return 1

    verificados = resultado.get("verificados", 0)
    aprovados = resultado.get("aprovados", 0)
    pendentes = resultado.get("pendentes", 0)

    logger.info(
        "Resultado: %d verificados | %d aprovados e notificados | %d ainda pendentes",
        verificados, aprovados, pendentes
    )

    # 3. Registrar log
    _registrar_log({
        "acao": "executado",
        "verificados": verificados,
        "aprovados": aprovados,
        "pendentes": pendentes,
    })

    logger.info("Monitor concluído.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
