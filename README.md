<div align="center">

<img src="./static/image/mirofish-offline-banner.png" alt="MiroFish Offline" width="100%"/>

# MiroFish-Offline

**Self-hosted fork of [MiroFish](https://github.com/666ghj/MiroFish) — bring your own OpenAI-compatible API. English UI.**

*A multi-agent swarm intelligence engine that simulates public opinion, market sentiment, and social dynamics. On your hardware, with the LLM provider of your choice.*

[![GitHub Stars](https://img.shields.io/github/stars/nikmcfly/MiroFish-Offline?style=flat-square&color=DAA520)](https://github.com/nikmcfly/MiroFish-Offline/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/nikmcfly/MiroFish-Offline?style=flat-square)](https://github.com/nikmcfly/MiroFish-Offline/network)
[![Docker](https://img.shields.io/badge/Docker-Build-2496ED?style=flat-square&logo=docker&logoColor=white)](https://hub.docker.com/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue?style=flat-square)](./LICENSE)

</div>

## What is this?

MiroFish is a multi-agent simulation engine: upload any document (press release, policy draft, financial report), and it generates hundreds of AI agents with unique personalities that simulate the public reaction on social media. Posts, arguments, opinion shifts — hour by hour.

The [original MiroFish](https://github.com/666ghj/MiroFish) was built for the Chinese market (Chinese UI, Zep Cloud for knowledge graphs, DashScope API). This fork keeps the data layer self-hosted and works with any OpenAI-compatible LLM API:

| Original MiroFish | MiroFish-Offline |
|---|---|
| Chinese UI | **English UI** (1,000+ strings translated) |
| Zep Cloud (graph memory) | **Neo4j Community Edition** (self-hosted) |
| DashScope API (LLM) | **Any OpenAI-compatible API** (OpenRouter by default) |
| Zep Cloud embeddings | **OpenAI-compatible embeddings** (configurable dimension) |
| Locked to one provider | **Swap models with one line of config** |

## Workflow

1. **Graph Build** — Extracts entities (people, companies, events) and relationships from your document. Builds a knowledge graph with individual and group memory via Neo4j.
2. **Env Setup** — Generates hundreds of agent personas, each with unique personality, opinion bias, reaction speed, influence level, and memory of past events.
3. **Simulation** — Agents interact on simulated social platforms: posting, replying, arguing, shifting opinions. The system tracks sentiment evolution, topic propagation, and influence dynamics in real time.
4. **Report** — A ReportAgent analyzes the post-simulation environment, interviews a focus group of agents, searches the knowledge graph for evidence, and generates a structured analysis.
5. **Interaction** — Chat with any agent from the simulated world. Ask them why they posted what they posted. Full memory and personality persists.

## Screenshot

<div align="center">
<img src="./static/image/mirofish-offline-screenshot.jpg" alt="MiroFish Offline — English UI" width="100%"/>
</div>

## Quick Start

### Prerequisites

- An [OpenRouter](https://openrouter.ai/keys) API key (or any OpenAI-compatible endpoint)
- Docker & Docker Compose (recommended), **or**
- Python 3.11+, Node.js 18+, Neo4j 5.18+

### Option A: Docker (easiest)

```bash
git clone https://github.com/nikmcfly/MiroFish-Offline.git
cd MiroFish-Offline
cp .env.example .env
# Edit .env: paste your OpenRouter API key into LLM_API_KEY and OPENAI_API_KEY
docker compose up -d
```

Open `http://localhost:3000` — that's it.

### Option B: Manual

**1. Start Neo4j**

```bash
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/mirofish \
  neo4j:5.18-community
```

**2. Configure & run backend**

```bash
cp .env.example .env
# Edit .env: paste your OpenRouter API key

cd backend
uv sync
uv run python run.py
```

**3. Run frontend**

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Configuration

All settings are in `.env` (copy from `.env.example`):

```bash
# LLM — any OpenAI-compatible API (OpenRouter by default)
LLM_API_KEY=sk-or-v1-...
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL_NAME=deepseek/deepseek-v4-flash

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=mirofish

# Embeddings — OpenAI-compatible /embeddings endpoint
EMBEDDING_BASE_URL=https://openrouter.ai/api/v1
EMBEDDING_MODEL=openai/text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
```

`EMBEDDING_DIMENSIONS` must match the chosen embedding model's vector size. If you change it, the Neo4j vector indexes are dropped and recreated automatically on next startup (existing graphs must be re-built to re-embed).

Works with any OpenAI-compatible API — point `LLM_BASE_URL` at OpenAI, a local vLLM/Ollama server, or any other provider.

## Architecture

This fork introduces a clean abstraction layer between the application and the graph database:

```
┌─────────────────────────────────────────┐
│              Flask API                   │
│  graph.py  simulation.py  report.py     │
└──────────────┬──────────────────────────┘
               │ app.extensions['neo4j_storage']
┌──────────────▼──────────────────────────┐
│           Service Layer                  │
│  EntityReader  GraphToolsService         │
│  GraphMemoryUpdater  ReportAgent         │
└──────────────┬──────────────────────────┘
               │ storage: GraphStorage
┌──────────────▼──────────────────────────┐
│         GraphStorage (abstract)          │
│              │                            │
│    ┌─────────▼─────────┐                │
│    │   Neo4jStorage     │                │
│    │  ┌───────────────┐ │                │
│    │  │ EmbeddingService│ ← OpenAI-compat │
│    │  │ NERExtractor   │ ← LLM API       │
│    │  │ SearchService  │ ← Hybrid search │
│    │  └───────────────┘ │                │
│    └───────────────────┘                │
└─────────────────────────────────────────┘
               │
        ┌──────▼──────┐
        │  Neo4j CE   │
        │  5.18       │
        └─────────────┘
```

**Key design decisions:**

- `GraphStorage` is an abstract interface — swap Neo4j for any other graph DB by implementing one class
- Dependency injection via Flask `app.extensions` — no global singletons
- Hybrid search: 0.7 × vector similarity + 0.3 × BM25 keyword search
- Synchronous NER/RE extraction via LLM (replaces Zep's async episodes)
- Configurable embedding dimension with automatic vector index migration
- All original dataclasses and LLM tools (InsightForge, Panorama, Agent Interviews) preserved

## Use Cases

- **PR crisis testing** — simulate the public reaction to a press release before publishing
- **Trading signal generation** — feed financial news and observe simulated market sentiment
- **Policy impact analysis** — test draft regulations against simulated public response
- **Creative experiments** — someone fed it a classical Chinese novel with a lost ending; the agents wrote a narratively consistent conclusion

## License

AGPL-3.0 — same as the original MiroFish project. See [LICENSE](./LICENSE).

## Credits & Attribution

This is a modified fork of [MiroFish](https://github.com/666ghj/MiroFish) by [666ghj](https://github.com/666ghj), originally supported by [Shanda Group](https://www.shanda.com/). The simulation engine is powered by [OASIS](https://github.com/camel-ai/oasis) from the CAMEL-AI team.

**Modifications in this fork:**
- Backend migrated from Zep Cloud to self-hosted Neo4j CE + any OpenAI-compatible LLM/embedding API
- Entire frontend translated from Chinese to English (20 files, 1,000+ strings)
- All Zep references replaced with Neo4j across the UI
- Rebranded to MiroFish Offline
