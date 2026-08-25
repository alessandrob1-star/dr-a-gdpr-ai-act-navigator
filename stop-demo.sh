#!/usr/bin/env sh
set -eu
ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$ROOT_DIR"
docker compose -f module_company_profile/docker-compose.yml down
echo "Dr. G.D.P.R. & AI Act navigator has stopped."
