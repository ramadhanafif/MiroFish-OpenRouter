# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

MiroFish-Offline is a self-hosted fork of [MiroFish](https://github.com/666ghj/MiroFish): a multi-agent simulation engine that ingests a document, builds a knowledge graph, generates hundreds of agent personas, and simulates their social-media reaction (via CAMEL-AI's OASIS). The fork replaces Zep Cloud with Neo4j, and the UI is English-only. All LLM/embedding calls go through any OpenAI-compatible API, with OpenRouter as the default (`deepseek/deepseek-v4-flash` for chat, `openai/text-embedding-3-small` for embeddings).

## Commands

```bash
npm run setup:all     # install root + frontend (npm) and backend (uv sync)
npm run dev           # run backend + frontend concurrently
npm run backend       # backend only: cd backend && uv run python run.py  (Flask, port 5001)
npm run frontend      # frontend only: cd frontend && npm run dev  (Vite, port 3000)
npm run build         # frontend production build
cd backend && uv run pytest   # pytest is in dev deps; only scripts/test_profile_format.py exists
```

No linter is configured. The Vite dev server proxies `/api` → `http://localhost:5001`.

**Required external services** (the backend starts without them but endpoints return 503):
- Neo4j ≥ **5.18** (`neo4j:5.18-community`, auth `neo4j/mirofish`). 5.18 is a hard floor because relationship vector indexes don't exist before it
- An OpenRouter API key in `LLM_API_KEY` and `OPENAI_API_KEY` (or any OpenAI-compatible endpoint via `LLM_BASE_URL`)

Configuration lives in `.env` at the repo root (copy from `.env.example`); `backend/app/config.py` loads it and is the single source of all settings. `EMBEDDING_DIMENSIONS` must match the embedding model's vector size (text-embedding-3-small = 1536); on mismatch with existing Neo4j vector indexes, `Neo4jStorage._ensure_schema()` drops and recreates them at startup; existing graphs must be re-built to re-embed. In `docker compose`, the backend container gets `NEO4J_URI=bolt://neo4j:7687` via a compose-level `environment` override (the `.env` value points at localhost for local dev).

## Architecture

Three layers, dependency-injected top to bottom:

1. **Flask API** (`backend/app/api/`): blueprints `graph.py`, `simulation.py`, `report.py` mounted at `/api/graph`, `/api/simulation`, `/api/report`. The app factory (`backend/app/__init__.py`) creates one `Neo4jStorage` and stores it in `app.extensions['neo4j_storage']`; endpoints fetch it via `current_app.extensions` and construct services per-request (e.g. `GraphToolsService(storage=storage)`). There are no global singletons; if you add a service that needs the graph, take storage as a constructor argument. On Neo4j connection failure the extension is `None`, and endpoints must handle that with a 503.

2. **Services** (`backend/app/services/`): the pipeline stages: `ontology_generator` → `graph_builder` → `oasis_profile_generator` + `simulation_config_generator` → `simulation_manager`/`simulation_runner` → `report_agent` (uses `graph_tools.py`, which holds the dataclasses and LLM tools: InsightForge, Panorama, agent interviews). `graph_memory_updater` writes simulation events back into the graph.

3. **Storage** (`backend/app/storage/`): `GraphStorage` is the abstract interface; `Neo4jStorage` is the only implementation and composes `EmbeddingService` (OpenAI-compatible `/embeddings` endpoint, dimension from `EMBEDDING_DIMENSIONS`), `NERExtractor` (synchronous NER/RE via the LLM, ontology-guided), and `SearchService` (hybrid search: 0.7 × vector similarity + 0.3 × BM25 fulltext). Swapping the graph DB means implementing `GraphStorage` once.

**Simulations run as separate OS processes**, not threads: `SimulationRunner` spawns `backend/scripts/run_parallel_simulation.py` (or the twitter/reddit variants) with `subprocess.Popen`. Flask talks to the running simulation through filesystem IPC (`simulation_ipc.py`): commands are JSON files in a `commands/` dir, the script polls and writes to `responses/`. This is how agent interviews and env shutdown work mid-simulation. A cleanup hook registered in the app factory kills orphaned simulation processes on server shutdown.

**Persistence is file-based**: there is no SQL database. Projects (`backend/app/models/project.py`) and simulation state are JSON under `backend/uploads/`. Accepted upload types: pdf, md, txt, markdown (50 MB max).

**OASIS/CAMEL-AI** doesn't read this app's config directly: it reads `OPENAI_API_KEY`/`OPENAI_API_BASE_URL` from the environment, which `.env` points at OpenRouter.

**Frontend** (`frontend/src/`): Vue 3 + Vite + vue-router, d3 for graph visualization, axios wrappers in `src/api/`. The 5-step workflow maps 1:1 to `components/Step1GraphBuild.vue` … `Step5Interaction.vue`.

## Conventions

- All user-facing strings and LLM outputs must be English. The original project was Chinese; a regression here is a bug (the report agent was specifically fixed to force English-only output). Code comments in older files may still be Chinese; don't add new ones. Avoid em dashes in all writing (the project owner explicitly dislikes them).
- Python backend uses `uv` (lockfile `uv.lock`, deps in `pyproject.toml`); keep `requirements.txt` in sync since the README's manual path and Docker use it.
