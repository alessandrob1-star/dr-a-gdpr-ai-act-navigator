#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
export MODEL_PROVIDER="local"
export LOCAL_MODEL_NAME="${LOCAL_MODEL_NAME:-${QWEN_MODEL:-qwen2.5:14b-instruct}}"
export LOCAL_MODEL_ENDPOINT="${LOCAL_MODEL_ENDPOINT:-${QWEN_ENDPOINT:-http://localhost:11434/v1/chat/completions}}"

exec "$ROOT/Start-Dashboard.sh"
