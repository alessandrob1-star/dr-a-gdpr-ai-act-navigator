#!/usr/bin/env sh
set -eu
ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$ROOT_DIR"
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker was not found. Install and start Docker Desktop, then try again."
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "Docker is installed but not running. Start Docker Desktop, then try again."
  exit 1
fi
: "${OPENAI_API_KEY:?Set OPENAI_API_KEY before starting the dashboard.}"
echo "Starting Dr. G.D.P.R. & AI Act navigator with gpt-5.6-sol through the OpenAI API."
docker compose -f module_company_profile/docker-compose.yml up -d --build dashboard
echo "Waiting for the dashboard..."
attempt=0
until curl --fail --silent http://localhost:8771/api/health 2>/dev/null \
  | grep -q '"ok"[[:space:]]*:[[:space:]]*true'; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 90 ]; then
    echo "The dashboard did not become ready within three minutes."
    docker compose -f module_company_profile/docker-compose.yml ps
    exit 1
  fi
  sleep 2
done
echo "The demo is available at http://localhost:8771"
case "$(uname -s)" in
  Darwin) open http://localhost:8771 ;;
  Linux) command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:8771 >/dev/null 2>&1 || true ;;
esac
