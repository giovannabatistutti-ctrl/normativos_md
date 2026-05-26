#!/usr/bin/env bash
# run.sh — Atalho de execução do orquestrador normativos-bcb
#
# Uso:
#   bash skills/normativos-bcb/run.sh                    # produção
#   bash skills/normativos-bcb/run.sh --dry-run          # sem Slack/GitHub
#   bash skills/normativos-bcb/run.sh --ano 2025         # ano específico
#   bash skills/normativos-bcb/run.sh --sem-integra      # sem íntegra (rápido)
#
# Variáveis de ambiente opcionais:
#   VENV_PATH   Caminho para o venv Python (padrão: /workspace/.venv)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV_PATH="${VENV_PATH:-$WORKSPACE_DIR/.venv}"

# ── Garantir venv e dependências ─────────────────────────────────────────────
if [ ! -f "$VENV_PATH/bin/python3" ]; then
    echo "[run.sh] Criando venv em $VENV_PATH..."
    python3 -m venv "$VENV_PATH"
fi

# Ativar venv
# shellcheck disable=SC1091
source "$VENV_PATH/bin/activate"

# Instalar dependências se necessário
if ! python3 -c "import requests, bs4" 2>/dev/null; then
    echo "[run.sh] Instalando dependências..."
    pip install requests beautifulsoup4 --quiet
fi

# ── Executar orquestrador ─────────────────────────────────────────────────────
cd "$WORKSPACE_DIR"
echo "[run.sh] $(date '+%Y-%m-%d %H:%M:%S') — Iniciando orquestrador normativos-bcb..."

python3 skills/normativos-bcb/init.py "$@"

echo "[run.sh] $(date '+%Y-%m-%d %H:%M:%S') — Concluído."
