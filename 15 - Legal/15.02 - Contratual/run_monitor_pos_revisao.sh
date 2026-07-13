#!/usr/bin/env bash
# run_monitor_pos_revisao.sh
# Ponto de entrada para o monitor horário de pós-revisão do pipeline 15-aditamentos.
# Chamado pela task recorrente do Toqan.

set -e
cd /workspace/data/ifb-aditamentos/app

# Usar venv do pipeline
if [ -d "/workspace/.venv-adit" ]; then
    source /workspace/.venv-adit/bin/activate
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Monitor pós-revisão iniciado"
python3 monitor_pos_revisao.py
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Monitor pós-revisão concluído"
