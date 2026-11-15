#!/usr/bin/env python3
"""
⚡ Fast Knowledge Bank & GitHub Discovery Engine ⚡
Author: frac1ur3d-hash & Antigravity
Repository: https://github.com/frac1ur3d-hash/knowledge-bank
"""

import sys
import os
import json
import sqlite3
import subprocess
import argparse
import time
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.resolve()
DB_PATH = BASE_DIR / "knowledge_bank.db"
REPOS_DIR = Path("E:/skills-repos")
DEFAULT_WORKSPACE = Path("C:/Users/N0N3Follows/.gemini/antigravity/scratch")
CATALOG_MD = BASE_DIR / "CATALOG.md"
INDEX_JSON = BASE_DIR / "index.json"

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS repositories (
                full_name TEXT PRIMARY KEY,
                name TEXT,
                owner TEXT,
                url TEXT,
                description TEXT,
                stars INTEGER DEFAULT 0,
                language TEXT,
                domain TEXT,
                tags TEXT,
                notes TEXT,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                local_path TEXT
            )
        """)
        # FTS5 table for sub-millisecond full text search
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS repo_fts USING fts5(
                full_name,
                description,
                domain,
                tags,
                notes,
                content='repositories',
                content_rowid='rowid'
            )
        """)
        # Trigger to keep FTS updated
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS repo_ai AFTER INSERT ON repositories BEGIN
                INSERT INTO repo_fts(rowid, full_name, description, domain, tags, notes)
                VALUES (new.rowid, new.full_name, new.description, new.domain, new.tags, new.notes);
            END;
        """)
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS repo_ad AFTER DELETE ON repositories BEGIN
                INSERT INTO repo_fts(repo_fts, rowid, full_name, description, domain, tags, notes)
                VALUES ('delete', old.rowid, old.full_name, old.description, old.domain, old.tags, old.notes);
            END;
        """)
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS repo_au AFTER UPDATE ON repositories BEGIN
                INSERT INTO repo_fts(repo_fts, rowid, full_name, description, domain, tags, notes)
                VALUES ('delete', old.rowid, old.full_name, old.description, old.domain, old.tags, old.notes);
                INSERT INTO repo_fts(rowid, full_name, description, domain, tags, notes)
                VALUES (new.rowid, new.full_name, new.description, new.domain, new.tags, new.notes);
            END;
        """)
    return conn

def upsert_repo(repo_data: dict, conn=None):
    close_after = False
    if conn is None:
        conn = get_db()
        close_after = True

    full_name = repo_data.get("full_name") or repo_data.get("fullName")
    if not full_name:
        return False

    parts = full_name.split("/")
    owner = parts[0] if len(parts) > 1 else ""
    name = parts[1] if len(parts) > 1 else full_name

    url = repo_data.get("url") or f"https://github.com/{full_name}"
    desc = repo_data.get("description") or ""
    stars = repo_data.get("stars") or repo_data.get("stargazersCount") or 0
    lang = repo_data.get("language") or ""
    domain = repo_data.get("domain") or infer_domain(full_name, desc, repo_data.get("tags", ""))
    tags = repo_data.get("tags") or ""
    notes = repo_data.get("notes") or ""
    local_path = repo_data.get("local_path") or ""

    with conn:
        conn.execute("""
            INSERT INTO repositories (full_name, name, owner, url, description, stars, language, domain, tags, notes, local_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(full_name) DO UPDATE SET
                url=excluded.url,
                description=COALESCE(NULLIF(excluded.description, ''), repositories.description),
                stars=MAX(excluded.stars, repositories.stars),
                language=COALESCE(NULLIF(excluded.language, ''), repositories.language),
                domain=COALESCE(NULLIF(excluded.domain, ''), repositories.domain),
                tags=COALESCE(NULLIF(excluded.tags, ''), repositories.tags),
                notes=COALESCE(NULLIF(excluded.notes, ''), repositories.notes),
                local_path=COALESCE(NULLIF(excluded.local_path, ''), repositories.local_path)
        """, (full_name, name, owner, url, desc, stars, lang, domain, tags, notes, local_path))

    if close_after:
        conn.close()
    return True

def infer_domain(name: str, desc: str, tags: str) -> str:
    combined = f"{name} {desc} {tags}".lower()
    if any(k in combined for k in ["agent", "llm", "rag", "langchain", "prompt", "transformer", "gpt", "fine-tuning", "vllm", "ollama", "eval"]):
        return "AI & Autonomous Agents"
    if any(k in combined for k in ["security", "exploit", "cve", "pentest", "redteam", "recon", "burp", "fuzz", "malware", "osint", "subdomain"]):
        return "Cybersecurity & Red Teaming"
    if any(k in combined for k in ["solidity", "web3", "mev", "ethereum", "blockchain", "arbitrage", "smart contract", "crypto", "defi", "solana"]):
        return "Web3, Blockchain & MEV"
    if any(k in combined for k in ["free-for-dev", "cloud", "docker", "kubernetes", "k8s", "terraform", "serverless", "hosting", "devops", "ci/cd", "infra"]):
        return "Cloud, Infra & Free Tiers"
    if any(k in combined for k in ["synth", "audio", "dsp", "sound", "music", "game", "graphics", "shader", "canvas", "threejs", "webgl"]):
        return "Creative, Audio & GameDev"
    if any(k in combined for k in ["api", "cli", "compiler", "parser", "typescript", "python", "rust", "database", "orm", "library", "framework"]):
        return "Developer Tooling & Systems"
    return "General Knowledge & Utilities"

def search_local(query: str, domain: str = None, limit: int = 15):
    t0 = time.time()
    conn = get_db()
    cursor = conn.cursor()

    # Clean query for FTS5 syntax
    clean_q = "".join(c if c.isalnum() or c in " *_-." else " " for c in query).strip()
    results = []

    if clean_q:
        try:
            fts_query = " ".join(f'"{word}"*' for word in clean_q.split() if word)
            sql = """
                SELECT r.*, rank 
                FROM repo_fts(?) 
                JOIN repositories r ON repo_fts.rowid = r.rowid
            """
            params = [fts_query]
            if domain:
                sql += " WHERE r.domain = ?"
                params.append(domain)
            sql += " ORDER BY rank LIMIT ?"
            params.append(limit)
            cursor.execute(sql, params)
            results = cursor.fetchall()
        except sqlite3.OperationalError:
            pass

    # Fallback to LIKE if FTS produced 0 results
    if not results:
        sql = """
            SELECT *, 0 as rank FROM repositories
            WHERE (full_name LIKE ? OR description LIKE ? OR tags LIKE ? OR notes LIKE ?)
        """
        like_arg = f"%{query}%"
        params = [like_arg, like_arg, like_arg, like_arg]
        if domain:
            sql += " AND domain = ?"
            params.append(domain)
        sql += " ORDER BY stars DESC LIMIT ?"
        params.append(limit)
        cursor.execute(sql, params)
        results = cursor.fetchall()

    conn.close()
    elapsed_ms = (time.time() - t0) * 1000
    return results, elapsed_ms

def search_github_live(query: str, limit: int = 10, save: bool = True):
    t0 = time.time()
    print(f"[*] Querying GitHub live index for '{query}' (limit {limit})...")
    cmd = [
        "gh", "search", "repos", query,
        "--limit", str(limit),
        "--json", "fullName,stargazersCount,description,url,updatedAt"
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        items = json.loads(proc.stdout)
    except Exception as e:
        print(f"[-] GitHub search error: {e}")
        return [], 0

    elapsed_ms = (time.time() - t0) * 1000
    if save and items:
        conn = get_db()
        for it in items:
            upsert_repo({
                "full_name": it["fullName"],
                "stars": it.get("stargazersCount", 0),
                "description": it.get("description", ""),
                "url": it.get("url", f"https://github.com/{it['fullName']}")
            }, conn=conn)
        conn.close()
        print(f"[+] Cached {len(items)} live GitHub results into local database.")
    return items, elapsed_ms

def pull_repo(repo_name_or_url: str, destination: str = None):
    """Ultra-fast shallow clone into E:/skills-repos or custom path for immediate modification and use."""
    name = repo_name_or_url.strip()
    if name.startswith("http"):
        url = name
        clean_name = name.rstrip("/").split("/")[-1].replace(".git", "")
    else:
        url = f"https://github.com/{name}.git"
        clean_name = name.split("/")[-1]

    target_dir = Path(destination) if destination else (REPOS_DIR / clean_name)
    if target_dir.exists():
        print(f"[!] Target path already exists at: {target_dir}")
        print(f"[*] Updating repository via git pull...")
        subprocess.run(["git", "-C", str(target_dir), "pull"])
    else:
        print(f"[*] Fast-cloning {url} into {target_dir} (--depth 1)...")
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        res = subprocess.run(["git", "clone", "--depth", "1", url, str(target_dir)])
        if res.returncode != 0:
            print(f"[-] Clone failed.")
            return None

    # Record local path in DB
    conn = get_db()
    with conn:
        conn.execute("UPDATE repositories SET local_path = ? WHERE name = ? OR full_name LIKE ?", 
                     (str(target_dir), clean_name, f"%/{clean_name}"))
    conn.close()

    print(f"\n[+] REPO READY FOR USE & MODIFICATION:")
    print(f"    Path: {target_dir}")
    print(f"    Inspect: python E:/knowledge-bank/kb.py inspect {clean_name}")
    return target_dir

def export_catalogs():
    """Generates CATALOG.md and index.json for GitHub and fast agent reading."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM repositories ORDER BY domain ASC, stars DESC")
    rows = cursor.fetchall()
    conn.close()

    domains = {}
    json_list = []
    for r in rows:
        d = r["domain"] or "General Knowledge & Utilities"
        domains.setdefault(d, []).append(r)
        json_list.append({
            "full_name": r["full_name"],
            "url": r["url"],
            "description": r["description"],
            "stars": r["stars"],
            "domain": r["domain"],
            "tags": r["tags"],
            "local_path": r["local_path"]
        })

    with open(INDEX_JSON, "w", encoding="utf-8") as f:
        json.dump(json_list, f, indent=2)

    md = [
        "# ⚡ Universal Knowledge Bank & GitHub Catalog ⚡",
        "",
        "> Autonomous knowledge vault, repository indexer, and deployment engine.",
        f"> **Total Repositories Indexed**: `{len(rows)}`",
        "",
        "---",
        ""
    ]

    for dom, items in sorted(domains.items()):
        md.append(f"## 📁 {dom} (`{len(items)}` repos)")
        md.append("")
        md.append("| Repository | Stars | Description | Status / Action |")
        md.append("|---|---|---|---|")
        for item in items:
            stars_fmt = f"⭐ {item['stars']:,}" if item['stars'] else "-"
            local = "💾 Cloned" if item['local_path'] and os.path.exists(item['local_path']) else "🌐 Remote"
            desc = (item['description'] or "").replace("|", "-")
            md.append(f"| [{item['full_name']}]({item['url']}) | {stars_fmt} | {desc} | `{local}` |")
        md.append("")

    with open(CATALOG_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"[+] Exported {len(rows)} repositories to {CATALOG_MD.name} and {INDEX_JSON.name}")

def sync_github():
    """Commits and pushes updates directly to https://github.com/frac1ur3d-hash/knowledge-bank."""
    export_catalogs()
    print("[*] Synchronizing Knowledge Bank with remote GitHub repository...")
    os.chdir(str(BASE_DIR))
    subprocess.run(["git", "add", "."])
    msg = f"chore(sync): update catalog and knowledge database ({time.strftime('%Y-%m-%d %H:%M')})"
    subprocess.run(["git", "commit", "-m", msg])
    res = subprocess.run(["git", "push", "-u", "origin", "main"])
    if res.returncode != 0:
        # Fallback to master if default branch was master
        subprocess.run(["git", "push", "-u", "origin", "HEAD"])
    print("[+] Knowledge Bank synchronized with GitHub!")

def seed_essential_catalogs():
    """Seeds the knowledge bank with the most powerful curated GitHub repositories."""
    seeds = [
        # Free Tier & Cloud Infra
        {"full_name": "ripienaar/free-for-dev", "stars": 105000, "domain": "Cloud, Infra & Free Tiers",
         "description": "Exhaustive list of SaaS, PaaS and IaaS offerings that have free tiers for devs.", "local_path": "E:/skills-repos/free-for-dev"},
        {"full_name": "sindresorhus/awesome", "stars": 350000, "domain": "General Knowledge & Utilities",
         "description": "Curated list of awesome lists covering every software ecosystem."},
        {"full_name": "kamranahmedse/developer-roadmap", "stars": 310000, "domain": "Developer Tooling & Systems",
         "description": "Interactive roadmaps, guides and other educational content for developers."},

        # AI & Autonomous Agents
        {"full_name": "langgenius/dify", "stars": 161000, "domain": "AI & Autonomous Agents",
         "description": "Open-source LLM app development platform with agentic workflows and RAG."},
        {"full_name": "OpenHands/OpenHands", "stars": 93500, "domain": "AI & Autonomous Agents",
         "description": "Autonomous AI software engineer capable of writing code and orchestrating dev tasks."},
        {"full_name": "Significant-Gravitas/AutoGPT", "stars": 172000, "domain": "AI & Autonomous Agents",
         "description": "Visionary open-source autonomous agent builder and runner."},
        {"full_name": "crewAIInc/crewAI", "stars": 28000, "domain": "AI & Autonomous Agents",
         "description": "Top multi-agent orchestration framework for collaborative autonomous AI agents."},
        {"full_name": "vllm-project/vllm", "stars": 42000, "domain": "AI & Autonomous Agents",
         "description": "High-throughput and memory-efficient LLM inference and serving engine."},
        {"full_name": "ollama/ollama", "stars": 128000, "domain": "AI & Autonomous Agents",
         "description": "Get up and running with Llama 3, Mistral, and other large language models locally."},
        {"full_name": "microsoft/autogen", "stars": 39000, "domain": "AI & Autonomous Agents",
         "description": "Multi-agent conversation framework for building next-generation AI applications."},

        # Cybersecurity & Red Teaming
        {"full_name": "swisskyrepo/PayloadsAllTheThings", "stars": 63000, "domain": "Cybersecurity & Red Teaming",
         "description": "A list of useful payloads and bypass for Web Application Security and Pentest."},
        {"full_name": "projectdiscovery/nuclei", "stars": 23000, "domain": "Cybersecurity & Red Teaming",
         "description": "Fast and customizable vulnerability scanner based on simple YAML DSL."},
        {"full_name": "ffuf/ffuf", "stars": 14000, "domain": "Cybersecurity & Red Teaming",
         "description": "Fast web fuzzer written in Go for discovering endpoints, vhosts, and parameters."},
        {"full_name": "sqlmapproject/sqlmap", "stars": 34000, "domain": "Cybersecurity & Red Teaming",
         "description": "Automatic SQL injection and database takeover tool."},
        {"full_name": "danielmiessler/SecLists", "stars": 60000, "domain": "Cybersecurity & Red Teaming",
         "description": "The security tester's companion: collection of usernames, passwords, URLs, webshells."},

        # Web3, Blockchain & MEV
        {"full_name": "paradigmxyz/reth", "stars": 5000, "domain": "Web3, Blockchain & MEV",
         "description": "Modular, contributor-friendly and blazing-fast full node Ethereum execution client in Rust."},
        {"full_name": "foundry-rs/foundry", "stars": 16000, "domain": "Web3, Blockchain & MEV",
         "description": "Blazing fast, portable and modular toolkit for Ethereum application development in Rust."},
        {"full_name": "flashbots/mev-boost", "stars": 1500, "domain": "Web3, Blockchain & MEV",
         "description": "MEV-Boost is a service for validators to outsource block building to a network of builders."},
        {"full_name": "Uniswap/v3-core", "stars": 5200, "domain": "Web3, Blockchain & MEV",
         "description": "Core smart contracts of Uniswap v3 decentralized exchange protocol."},

        # Creative, Audio & Game Development
        {"full_name": "mrdoob/three.js", "stars": 105000, "domain": "Creative, Audio & GameDev",
         "description": "JavaScript 3D Library that makes WebGL simple and expressive."},
        {"full_name": "godotengine/godot", "stars": 92000, "domain": "Creative, Audio & GameDev",
         "description": "Free and open source 2D and 3D game engine."},
        {"full_name": "Tonejs/Tone.js", "stars": 15000, "domain": "Creative, Audio & GameDev",
         "description": "A Web Audio framework for making interactive music in the browser."},
        {"full_name": "makepad/makepad", "stars": 6000, "domain": "Creative, Audio & GameDev",
         "description": "Next-gen hybrid vector-based 2D/3D visual studio and UI framework in Rust."},

        # User's Own Arsenal (frac1ur3d-hash)
        {"full_name": "frac1ur3d-hash/knowledge-bank", "stars": 1, "domain": "Developer Tooling & Systems",
         "description": "Universal Knowledge Bank & GitHub Indexing Engine — Discover, index, search, and deploy any repo.", "local_path": "E:/knowledge-bank"},
        {"full_name": "frac1ur3d-hash/brand-vault", "stars": 1, "domain": "Developer Tooling & Systems",
         "description": "Brand clearance engine with live DNS/DoH, social handles, and 50-state LLC search.", "local_path": "E:/brand-vault"},
        {"full_name": "frac1ur3d-hash/FrequencyGEN", "stars": 1, "domain": "Creative, Audio & GameDev",
         "description": "Advanced Web Audio Laboratory Synthesizer and Frequency Generator.", "local_path": "E:/FrequencyGEN"},
        {"full_name": "frac1ur3d-hash/Aether-MEV-Core", "stars": 1, "domain": "Web3, Blockchain & MEV",
         "description": "Aether Dynamics Flash Arbitrage Router and EVM Mempool Scanner."}
    ]

    conn = get_db()
    for s in seeds:
        upsert_repo(s, conn=conn)
    conn.close()
    print(f"[+] Seeded {len(seeds)} foundational repositories into knowledge bank database.")

def main():
    parser = argparse.ArgumentParser(description="⚡ Fast Knowledge Bank & GitHub Discovery Engine ⚡")
    subparsers = parser.add_subparsers(dest="command")

    # search
    p_search = subparsers.add_parser("search", help="Instant sub-millisecond local search")
    p_search.add_argument("query", help="Keyword, topic, or phrase")
    p_search.add_argument("--domain", "-d", help="Filter by domain")
    p_search.add_argument("--limit", "-n", type=int, default=10, help="Result limit")

    # gh-search
    p_gh = subparsers.add_parser("gh-search", help="Live search across all of GitHub")
    p_gh.add_argument("query", help="Query or topics (e.g. 'topic:agent stars:>1000')")
    p_gh.add_argument("--limit", "-n", type=int, default=10, help="Number of results")
    p_gh.add_argument("--no-save", action="store_true", help="Do not cache into local knowledge bank")

    # pull
    p_pull = subparsers.add_parser("pull", help="Fast clone repo to local drive for editing or use")
    p_pull.add_argument("repo", help="Repository full_name (owner/repo) or URL")
    p_pull.add_argument("--dest", help="Custom destination folder")

    # add
    p_add = subparsers.add_parser("add", help="Add or index a specific repo")
    p_add.add_argument("repo", help="owner/repo or GitHub URL")
    p_add.add_argument("--domain", help="Knowledge domain")
    p_add.add_argument("--tags", help="Comma separated tags")
    p_add.add_argument("--notes", help="Custom notes or evaluation")

    # seed
    subparsers.add_parser("seed", help="Seed curated repositories into local database")

    # sync
    subparsers.add_parser("sync", help="Export markdown catalogs and sync to GitHub remote")

    # export
    subparsers.add_parser("export", help="Regenerate CATALOG.md and index.json")

    args = parser.parse_args()

    if args.command == "search":
        results, elapsed = search_local(args.query, domain=args.domain, limit=args.limit)
        print(f"\n⚡ Search results for '{args.query}' ({len(results)} found in {elapsed:.2f}ms):")
        print("=" * 80)
        for r in results:
            loc = f" [💾 {r['local_path']}]" if r['local_path'] else ""
            print(f"• {r['full_name']} (⭐ {r['stars']:,}) - {r['domain']}{loc}")
            print(f"  URL: {r['url']}")
            print(f"  {r['description']}")
            print()

    elif args.command == "gh-search":
        items, elapsed = search_github_live(args.query, limit=args.limit, save=not args.no_save)
        print(f"\n🌐 Live GitHub results ({len(items)} found in {elapsed:.2f}ms):")
        print("=" * 80)
        for it in items:
            print(f"• {it['fullName']} (⭐ {it.get('stargazersCount', 0):,})")
            print(f"  URL: {it.get('url')}")
            print(f"  {it.get('description', '')}")
            print()

    elif args.command == "pull":
        pull_repo(args.repo, destination=args.dest)

    elif args.command == "add":
        clean = args.repo.replace("https://github.com/", "").strip("/").replace(".git", "")
        upsert_repo({
            "full_name": clean,
            "domain": args.domain,
            "tags": args.tags,
            "notes": args.notes
        })
        print(f"[+] Added '{clean}' to Knowledge Bank.")

    elif args.command == "seed":
        seed_essential_catalogs()
        export_catalogs()

    elif args.command == "sync":
        sync_github()

    elif args.command == "export":
        export_catalogs()

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
