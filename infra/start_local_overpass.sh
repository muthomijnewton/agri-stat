#!/usr/bin/env bash
# Run from the user's terminal with sudo. Does not delete volumes or reset data.
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
compose=(docker compose --env-file infra/.env -f infra/compose.yaml)
"${compose[@]}" config --quiet
"${compose[@]}" up --build -d
printf '\nKenya Overpass import is starting. It may take a while on the first run.\n'
printf 'Progress: sudo docker compose --env-file infra/.env -f infra/compose.yaml logs -f --tail=30 overpass\n'
printf 'Local endpoint: http://127.0.0.1:8082/api/interpreter\n'
