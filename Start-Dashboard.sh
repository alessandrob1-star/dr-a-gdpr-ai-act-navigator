#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

PYTHON_EXE="$ROOT/.venv/bin/python"

export ASSISTANT_NAME="${ASSISTANT_NAME:-Dr. A}"
export DASHBOARD_PORT="${DASHBOARD_PORT:-8771}"
export MODEL_PROVIDER="${MODEL_PROVIDER:-openai}"
case "${MODEL_PROVIDER,,}" in
    local|ollama|qwen)
        export MODEL_PROVIDER="local"
        export LOCAL_MODEL_NAME="${LOCAL_MODEL_NAME:-${QWEN_MODEL:-qwen2.5:14b-instruct}}"
        export LOCAL_MODEL_ENDPOINT="${LOCAL_MODEL_ENDPOINT:-${QWEN_ENDPOINT:-http://localhost:11434/v1/chat/completions}}"
        ;;
    *)
        : "${OPENAI_API_KEY:?Set OPENAI_API_KEY before starting the dashboard, or set MODEL_PROVIDER=local for Ollama/Qwen.}"
        ;;
esac

# Verifica dipendenze di base
if ! command -v curl >/dev/null 2>&1; then
    echo "Errore: curl non è installato."
    exit 1
fi

# Apertura browser multipiattaforma
open_browser() {
    local url="$1"

    if command -v open >/dev/null 2>&1; then
        open "$url"                  # macOS
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$url" >/dev/null 2>&1 &
    elif command -v start >/dev/null 2>&1; then
        start "$url"                 # Git Bash / Windows
    else
        echo "Apri manualmente il browser su:"
        echo "  $url"
    fi
}

# Attende che la dashboard sia pronta e apre il browser
wait_and_open() {
    local url="http://localhost:${DASHBOARD_PORT}/"

    while ! curl -fs "${url}api/health" 2>/dev/null \
      | grep -q '"ok"[[:space:]]*:[[:space:]]*true'; do
        sleep 1
    done

    open_browser "$url"
}

# Se esiste il Python del venv usa quello
if [ -x "$PYTHON_EXE" ]; then
    PY="$PYTHON_EXE"
elif command -v python3 >/dev/null 2>&1; then
    PY="python3"
elif command -v python >/dev/null 2>&1; then
    PY="python"
else
    PY=""
fi

# Reuse only an existing instance of this application. If that process was
# started without an API key, it must be stopped before the current process
# environment can take effect.
EXISTING_HEALTH=$(curl -fs "http://localhost:${DASHBOARD_PORT}/api/health" 2>/dev/null || true)
if printf '%s' "$EXISTING_HEALTH" | grep -q '"ok"[[:space:]]*:[[:space:]]*true'; then
    if ! printf '%s' "$EXISTING_HEALTH" | grep -q '"model_configured"[[:space:]]*:[[:space:]]*true'; then
        echo "The dashboard is already running without a configured model provider."
        echo "Stop the existing dashboard process, then run this launcher again."
        open_browser "http://localhost:${DASHBOARD_PORT}/"
        exit 2
    fi
    open_browser "http://localhost:${DASHBOARD_PORT}/"
    exit 0
fi

if [ -n "$PY" ]; then

    # Installa le dipendenze se mancanti
    if ! "$PY" -c "import docx, reportlab" >/dev/null 2>&1; then
        echo "Installing local report export dependencies..."
        "$PY" -m pip install -r "$ROOT/module_company_profile/requirements.txt"
    fi

    wait_and_open &

    exec "$PY" "$ROOT/module_company_profile/dashboard/dashboard_server.py"

else

    if ! command -v docker >/dev/null 2>&1; then
        echo "Python e Docker non sono installati."
        exit 1
    fi

    if ! docker info >/dev/null 2>&1; then
        echo "Docker Desktop non è in esecuzione."
        exit 1
    fi

    # Compatibilità docker compose / docker-compose
    if docker compose version >/dev/null 2>&1; then
        COMPOSE=(docker compose)
    elif command -v docker-compose >/dev/null 2>&1; then
        COMPOSE=(docker-compose)
    else
        echo "Docker Compose non è installato."
        exit 1
    fi

    wait_and_open &

    exec "${COMPOSE[@]}" -f "$ROOT/module_company_profile/docker-compose.yml" up dashboard

fi
