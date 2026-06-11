<div align="center">

<img src="./static/image/mirofish-offline-banner.png" alt="MiroFish Offline" width="100%"/>

# MiroFish-Offline

**Self-hosted fork of [MiroFish](https://github.com/666ghj/MiroFish). Bring your own OpenAI-compatible API.**

[![GitHub Stars](https://img.shields.io/github/stars/nikmcfly/MiroFish-Offline?style=flat-square&color=DAA520)](https://github.com/nikmcfly/MiroFish-Offline/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/nikmcfly/MiroFish-Offline?style=flat-square)](https://github.com/nikmcfly/MiroFish-Offline/network)
[![Docker](https://img.shields.io/badge/Docker-Build-2496ED?style=flat-square&logo=docker&logoColor=white)](https://hub.docker.com/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue?style=flat-square)](./LICENSE)

</div>

## What is this?

Upload a document (press release, policy draft, financial report) and MiroFish builds a knowledge graph from it, generates hundreds of AI agent personas, and simulates their reaction on social media: posts, arguments, and opinion shifts. It then writes an analysis report.

The [original MiroFish](https://github.com/666ghj/MiroFish) targets the Chinese market and depends on cloud services (Zep Cloud, DashScope). [MiroFish-Offline](https://github.com/nikmcfly/MiroFish-Offline) made it self-hosted and English; this fork builds on it to make it provider-agnostic.

## What this fork brings

- **Any OpenAI-compatible API.** Chat goes through a standard `/chat/completions` endpoint: OpenRouter, OpenAI, vLLM, whatever you run. Swap models with one line in `.env`. No DashScope lock-in.
- **OpenRouter embeddings.** Embeddings also use the OpenAI-compatible `/embeddings` endpoint (default: `openai/text-embedding-3-small`, 1536 dims). The embedding dimension is configurable, and the Neo4j vector indexes migrate automatically when it changes.
- **Lighter Docker image.** CPU-only torch instead of the default CUDA build keeps the image around 3.8 GB and skips the multi-GB nvidia wheel downloads you don't need without a GPU.

Plus: knowledge graphs on self-hosted **Neo4j Community Edition** instead of Zep Cloud, an **English UI** (1,000+ strings translated), and a frontend reachable from any host on your network, not just localhost.

## Workflow

1. **Graph Build**: extracts entities and relationships from your document into a Neo4j knowledge graph
2. **Env Setup**: generates hundreds of agent personas with unique personality, bias, and influence
3. **Simulation**: agents post, reply, argue, and shift opinions on a simulated social platform
4. **Report**: a ReportAgent interviews agents, searches the graph, and writes a structured analysis
5. **Interaction**: chat with any agent from the simulated world, memory and personality intact

<div align="center">
<img src="./static/image/mirofish-offline-screenshot.jpg" alt="MiroFish Offline English UI" width="100%"/>
</div>

## Quick Start

You need an [OpenRouter](https://openrouter.ai/keys) API key (or any OpenAI-compatible endpoint).

### Docker (easiest)

```bash
git clone https://github.com/nikmcfly/MiroFish-Offline.git
cd MiroFish-Offline
cp .env.example .env   # paste your API key into LLM_API_KEY and OPENAI_API_KEY
docker compose up -d
```

Open `http://localhost:3000`.

### Manual

Requires Python 3.11+, Node.js 18+, [uv](https://docs.astral.sh/uv/).

```bash
# Neo4j
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/mirofish neo4j:5.18-community

# Backend (port 5001)
cp .env.example .env   # paste your API key
cd backend && uv sync && uv run python run.py

# Frontend (port 3000)
cd frontend && npm install && npm run dev
```

## Configuration

Everything lives in `.env` (copy from `.env.example`):

```bash
# LLM: any OpenAI-compatible API (OpenRouter by default)
LLM_API_KEY=sk-or-v1-...
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL_NAME=deepseek/deepseek-v4-flash

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=mirofish

# Embeddings: OpenAI-compatible /embeddings endpoint
EMBEDDING_BASE_URL=https://openrouter.ai/api/v1
EMBEDDING_MODEL=openai/text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
```

`EMBEDDING_DIMENSIONS` must match the embedding model's vector size; if you change it, the Neo4j vector indexes are dropped and recreated on next startup (existing graphs must be re-built to re-embed).

## Architecture notes

- `GraphStorage` is an abstract interface; swapping Neo4j for another graph DB means implementing one class
- Dependency injection via Flask `app.extensions`, with no global singletons
- Hybrid search: 0.7 × vector similarity + 0.3 × BM25 keyword search
- Synchronous NER/RE extraction via LLM (replaces Zep's async episodes)
- Simulation engine: [OASIS](https://github.com/camel-ai/oasis) by CAMEL-AI, run as a separate OS process

## License & Credits

AGPL-3.0, same as upstream. Fork of [MiroFish-Offline](https://github.com/nikmcfly/MiroFish-Offline) by [nikmcfly](https://github.com/nikmcfly), itself a fork of [MiroFish](https://github.com/666ghj/MiroFish) by [666ghj](https://github.com/666ghj); simulation engine powered by [OASIS](https://github.com/camel-ai/oasis) from the CAMEL-AI team.
