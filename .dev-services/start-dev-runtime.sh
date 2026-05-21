#!/usr/bin/env bash
set -euo pipefail

ROOT=/home/duxianghe/dify
RUN_DIR="$ROOT/.codex-run"
DEV_DIR="$ROOT/.dev-services"
UV=/home/duxianghe/.local/bin/uv
QUEUES=dataset,dataset_summary,priority_dataset,priority_pipeline,pipeline,mail,ops_trace,app_deletion,plugin,workflow_storage,conversation,workflow,schedule_poller,schedule_executor,triggered_workflow_dispatcher,trigger_refresh_executor,retention,workflow_based_app_execution

mkdir -p "$RUN_DIR" "$DEV_DIR/celery"

require_env() {
  local key="$1"
  local value="$2"
  if ! grep -qx "${key}=${value}" "$ROOT/api/.env"; then
    echo "Refusing to start dev runtime: expected ${key}=${value} in $ROOT/api/.env" >&2
    exit 1
  fi
}

require_env DB_HOST 127.0.0.1
require_env DB_PORT 25432
require_env REDIS_HOST 127.0.0.1
require_env REDIS_PORT 26379

pgrep -f "/home/duxianghe/dify/api/.venv/bin/(flask|celery)|/home/duxianghe/.local/bin/uv run flask run --host 0.0.0.0 --port=5001|/home/duxianghe/.local/bin/uv run celery -A app.celery" | xargs -r kill
sleep 1

cd "$ROOT"
nohup bash -lc "cd '$ROOT/api' && '$UV' run flask db upgrade && exec '$UV' run flask run --host 0.0.0.0 --port=5001 --debug" > "$RUN_DIR/api.log" 2>&1 &
echo $! > "$RUN_DIR/api.pid"

nohup bash -lc "cd '$ROOT/api' && exec '$UV' run celery -A app.celery worker -P gevent -c 1 --loglevel INFO -Q '$QUEUES'" > "$RUN_DIR/worker.log" 2>&1 &
echo $! > "$RUN_DIR/worker.pid"

nohup bash -lc "cd '$ROOT/api' && exec '$UV' run celery -A app.celery beat --loglevel INFO --scheduler celery.beat:PersistentScheduler --schedule '$DEV_DIR/celery/celerybeat-schedule'" > "$RUN_DIR/beat.log" 2>&1 &
echo $! > "$RUN_DIR/beat.pid"

sleep 2
pgrep -af '^uv --directory api run celery -A app.celery beat|^uv run celery -A app.celery worker|^uv run flask run --host 0.0.0.0 --port=5001|/home/duxianghe/dify/api/.venv/bin/(celery|flask)' || true
