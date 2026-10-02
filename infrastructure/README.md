# infrastructure/

Local development infrastructure only. No production hosting, credentials, or integrations live here.

| Path | Purpose |
|---|---|
| `../docker-compose.yml` | PostgreSQL 17 + pgvector, bound to `127.0.0.1:5432` |
| `docker/` | Reserved for future Dockerfiles once hosting is approved (OQ-07) |
| `local/documents/` | `LOCAL_STORAGE_PATH` for the local document provider; git-ignored, references only |

Docker is optional: the API runs on the in-memory SIMULATED_DATA store without a database.
Kubernetes, Redis, and message brokers are intentionally absent (AGENTS.md).
See `docs/03-architecture/deployment-architecture.md`.
