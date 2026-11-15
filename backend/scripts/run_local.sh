#!/usr/bin/env bash
# Run the web app, API, worker, and scheduler together. Redis runs separately.
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root/backend"
venv/bin/python - <<'PY'
import os, socket
from app.core.config import SECRET_KEY
from redis import Redis
url = os.getenv('REDIS_URL')
if not url:
    raise SystemExit('Set REDIS_URL in backend/.env before starting the workers.')
Redis.from_url(url, socket_connect_timeout=3).ping()
for port in (8000, 5173):
    with socket.socket() as sock:
        if sock.connect_ex(('127.0.0.1', port)) == 0:
            raise SystemExit(f'Port {port} is already in use. Use the running app or stop its existing terminal first.')
PY
mkdir -p "$repo_root/work/logs"
process_ids=()
cleanup() { if ((${#process_ids[@]})); then kill "${process_ids[@]}" 2>/dev/null || true; fi; }
trap cleanup EXIT
trap 'exit 130' INT TERM
venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > "$repo_root/work/logs/api.log" 2>&1 &
process_ids+=("$!")
venv/bin/celery -A app.workers.celery_app:celery_app worker -Q agricstat-phase1 --hostname=foundation@%h --pool=solo --concurrency=1 --loglevel=info > "$repo_root/work/logs/worker.log" 2>&1 &
process_ids+=("$!")
venv/bin/celery -A app.workers.celery_app:celery_app worker -Q agricstat-markets --hostname=markets@%h --pool=solo --concurrency=1 --loglevel=info > "$repo_root/work/logs/markets.log" 2>&1 &
process_ids+=("$!")
venv/bin/celery -A app.workers.celery_app:celery_app beat --loglevel=info --schedule="$repo_root/work/celerybeat-schedule" > "$repo_root/work/logs/beat.log" 2>&1 &
process_ids+=("$!")
cd "$repo_root/web"
./node_modules/.bin/vite --host 127.0.0.1 > "$repo_root/work/logs/web.log" 2>&1 &
process_ids+=("$!")
echo 'Starting AgricStat at http://localhost:5173/market-prices'
echo 'Keep this terminal open. Ctrl+C stops these processes. Logs: work/logs/'
wait -n "${process_ids[@]}"
