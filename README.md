# ⚡ Knowledge Bank & GitHub Discovery Engine

> A high-speed, local-first knowledge bank, repository discovery engine, and deployment pipeline linked directly to GitHub.

[![GitHub Repository](https://img.shields.io/badge/GitHub-frac1ur3d--hash%2Fknowledge--bank-blue?logo=github)](https://github.com/frac1ur3d-hash/knowledge-bank)
[![Engine](https://img.shields.io/badge/Engine-Python%20%7C%20SQLite%20FTS5-brightgreen)](kb.py)
[![Local Storage](https://img.shields.io/badge/Storage-E%3A%2Fknowledge--bank-orange)](.)

---

## 🎯 Purpose & Scope

The **Knowledge Bank** serves as an autonomous, persistent index of GitHub. It allows you and Antigravity to:
1. **Search All of GitHub in Real-Time**: Query any topic, star threshold, language, or ecosystem across GitHub.
2. **Sub-Millisecond Local Retrieval**: Query the pre-indexed database via SQLite FTS5 in `< 5ms` with zero API latency or rate limits.
3. **Instant "Pull & Modify"**: Shallow-clone (`--depth 1`) any repository directly to `E:\skills-repos\` or current workspace to immediately inspect, refactor, strip, or deploy into projects.
4. **Permanent Bi-Directional GitHub Sync**: Catalog additions and categorizations automatically export to [CATALOG.md](CATALOG.md) and push to [frac1ur3d-hash/knowledge-bank](https://github.com/frac1ur3d-hash/knowledge-bank).

---

## 🚀 Quick Start CLI

Run `kb.py` from anywhere:

```bash
# Instant sub-millisecond local search
python E:\knowledge-bank\kb.py search "agent"
python E:\knowledge-bank\kb.py search "free-tier" --domain "Cloud, Infra & Free Tiers"

# Live search across ALL of GitHub (automatically caches high-value results locally)
python E:\knowledge-bank\kb.py gh-search "topic:mcp-server stars:>500" --limit 10

# Fast-pull a repository to E:\skills-repos for instant use and modification
python E:\knowledge-bank\kb.py pull owner/repo

# Manually add a specific repo to your knowledge vault
python E:\knowledge-bank\kb.py add owner/repo --domain "AI & Autonomous Agents" --tags "rag,evals"

# Export catalogs and sync updates to GitHub
python E:\knowledge-bank\kb.py sync
```

---

## 📁 Repository Structure

```
E:\knowledge-bank\
├── kb.py               # Core CLI & Discovery Engine
├── knowledge_bank.db   # Local SQLite database with FTS5 full-text search
├── index.json          # Fast JSON dump for agent context & tooling
├── CATALOG.md          # Human-readable categorized markdown catalog
└── README.md           # Documentation and guides
```

---

## 🗂️ Cataloged Domains

- ☁️ **Cloud, Infra & Free Tiers**: Zero-cost hosting, DBaaS, serverless, CI/CD, and developer tooling (e.g., `free-for-dev`).
- 🤖 **AI & Autonomous Agents**: Multi-agent swarms, RAG architectures, local LLM runners, inference engines.
- 🛡️ **Cybersecurity & Red Teaming**: Payloads, fuzzers, vulnerability scanners, OSINT, and exploit toolkits.
- ⛓️ **Web3, Blockchain & MEV**: Smart contract architectures, mempool sniffers, flash arbitrage routers, execution clients.
- 🎨 **Creative, Audio & GameDev**: Browser synthesizers, Web Audio, 2D/3D engines, shaders, and visual systems.
- 🛠️ **Developer Tooling & Systems**: Compilers, CLIs, high-performance engines, and utilities.
