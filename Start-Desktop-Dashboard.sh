#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PYTHON_EXE="$ROOT/.venv/bin/python"

export ASSISTANT_NAME="${ASSISTANT_NAME:-Dr. A}"
export LOCAL_MODEL_NAME="${LOCAL_MODEL_NAME:-${QWEN_MODEL:-qwen2.5:14b-instruct}}"
export LOCAL_MODEL_ENDPOINT="${LOCAL_MODEL_ENDPOINT:-${QWEN_ENDPOINT:-http://localhost:11434/v1/chat/completions}}"

if [ -x "$PYTHON_EXE" ]; then
    PY="$PYTHON_EXE"
elif command -v python3 >/dev/null 2>&1; then
    PY="python3"
elif command -v python >/dev/null 2>&1; then
    PY="python"
else
    echo "Python is not available. Install Python 3.12 or create .venv first."
    exit 1
fi

if ! "$PY" -c "import PySide6, docx, reportlab" >/dev/null 2>&1; then
    echo "Installing desktop UI dependencies..."
    "$PY" -m pip install -r "$ROOT/module_company_profile/requirements.txt"
fi

exec "$PY" "$ROOT/module_company_profile/desktop_app.py"
