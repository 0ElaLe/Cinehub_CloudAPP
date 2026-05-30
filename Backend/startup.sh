#!/bin/bash
# =============================================================================
# startup.sh — Comando de inicio para Azure App Service (Linux Python)
# =============================================================================
# Configurar en Azure Portal:
#   App Service > Configuration > General settings > Startup Command:
#   bash /home/site/wwwroot/startup.sh
#
# O directamente como startup command:
#   python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
# =============================================================================
set -e

cd /home/site/wwwroot

echo "[CineHub] Iniciando servidor Uvicorn en puerto ${PORT:-8000}..."
exec python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --workers 2 \
    --log-level info
