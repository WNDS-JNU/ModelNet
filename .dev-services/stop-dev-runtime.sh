#!/usr/bin/env bash
set -euo pipefail

pgrep -f "/home/duxianghe/dify/api/.venv/bin/(flask|celery)|/home/duxianghe/.local/bin/uv run flask run --host 0.0.0.0 --port=5001|/home/duxianghe/.local/bin/uv run celery -A app.celery" | xargs -r kill
