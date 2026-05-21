# Dify dev-only services

This directory isolates the developer-mode middleware from the production Docker stack.

Data roots:

- Postgres: `.dev-services/volumes/db/data`
- Redis: `.dev-services/volumes/redis/data`
- Weaviate: `.dev-services/volumes/weaviate`
- Plugin daemon: `.dev-services/volumes/plugin_daemon`
- API file storage: `.dev-services/storage/api`

Ports are kept compatible with `api/.env`:

- Postgres: `127.0.0.1:25432`
- Redis: `127.0.0.1:26379`
- Weaviate HTTP/gRPC: `127.0.0.1:28080` / `127.0.0.1:25051`
- Sandbox through SSRF proxy: `127.0.0.1:28194`
- Plugin daemon: `127.0.0.1:25002`
- Plugin remote install: `127.0.0.1:25003`

Use:

```bash
cd /home/duxianghe/dify/.dev-services
cp middleware.env.example middleware.env
docker compose up -d
docker compose ps
```

Restart developer API/Worker/Beat:

```bash
/home/duxianghe/dify/.dev-services/start-dev-runtime.sh
```

Stop developer API/Worker/Beat:

```bash
/home/duxianghe/dify/.dev-services/stop-dev-runtime.sh
```

Do not run production Docker Compose from this directory.
