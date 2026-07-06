#!/bin/bash
# Flood Risk DSS — Azure App Service startup script
#
# Usage:
#   Azure App Service Linux Python stack runs this script
#   automatically when configured as the startup command.
#
#   Reference in Azure Portal or az CLI:
#     az webapp config set --startup-file startup.sh
#
# Environment:
#   PORT  — assigned by Azure (default 8000)

set -e

echo "=== Flood Risk DSS Startup ==="
echo "Python: $(python --version)"
echo "PORT: ${PORT:-8000}"

# Install dependencies (Azure does this automatically during build,
# but running it ensures no missing packages at startup)
pip install -r requirements.txt --quiet 2>/dev/null || true

echo "Starting uvicorn on 0.0.0.0:${PORT:-8000}..."
exec uvicorn backend.app:app --host 0.0.0.0 --port "${PORT:-8000}" --log-level info
