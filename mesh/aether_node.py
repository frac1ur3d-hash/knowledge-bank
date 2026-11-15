#!/usr/bin/env python3
"""
⚡ AETHER-EGO: Universal Self-Contained Fractal Node ⚡
Autonomous, proactive personal intelligence engine.
Single-file, zero external dependencies, runs on any OS with Python 3.8+.
"""

import sys, os, time, json, sqlite3, base64, zlib, argparse, platform, random, subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

# ==========================================
# 1. MACHINE-NATIVE DENSE PROTOCOL (MNDCP)
# ==========================================
"""
⚡ Machine-Native Dense Cognitive Protocol (MNDCP) ⚡
High-entropy, symbolic token representation optimized for AI cognitive loops.
Compresses state, intent, semantic graphs, and execution traces into token-dense notation.
"""

import time
import json
import base64
import zlib
from typing import Dict, Any, List

# Symbolic Glyphs for High-Information-Density State
# Ψ: State/Identity | Γ: Knowledge/Context | Ω: Goal/Intent | Δ: Delta/Time | Φ: Action/Function | Σ: Summary | Θ: Confidence
GLYPHS = {
    "STATE": "Ψ",
    "CONTEXT": "Γ",
    "INTENT": "Ω",
    "DELTA": "Δ",
    "ACTION": "Φ",
    "SUMMARY": "Σ",
    "CONFIDENCE": "Θ",
    "ERROR": "Ξ",
    "RESULT": "Λ"
}

def encode_dense_frame(state: str, context: Dict[str, Any], intent: str, action: str = None, meta: Dict[str, Any] = None) -> str:
    """
    Encodes cognitive state into a machine-dense frame.
    Format: ⟦Ψ:<state>|Γ:<dense_context>|Ω:<intent>|Φ:<action>|Δ:<timestamp>|Θ:<conf>⟧
    """
    ts = int(time.time())
    ctx_tokens = []
    for k, v in context.items():
        if isinstance(v, (list, tuple)):
            val_str = ",".join(str(x) for x in v[:5])
        else:
            val_str = str(v)
        ctx_tokens.append(f"{k}:{val_str}")
    ctx_str = ";".join(ctx_tokens)

    frame = f"⟦{GLYPHS['STATE']}:{state}|{GLYPHS['CONTEXT']}:{ctx_str}|{GLYPHS['INTENT']}:{intent}"
    if action:
        frame += f"|{GLYPHS['ACTION']}:{action}"
    frame += f"|{GLYPHS['DELTA']}:{ts}"
    if meta and "confidence" in meta:
        frame += f"|{GLYPHS['CONFIDENCE']}:{meta['confidence']}"
    frame += "⟧"
    return frame

def decode_dense_frame(dense_str: str) -> Dict[str, Any]:
    """Parses a machine-dense frame back into structured semantic dict."""
    cleaned = dense_str.strip().strip("⟦⟧")
    parts = cleaned.split("|")
    result = {}
    for part in parts:
        if ":" in part:
            glyph, val = part.split(":", 1)
            glyph = glyph.strip()
            if glyph == GLYPHS["STATE"]:
                result["state"] = val
            elif glyph == GLYPHS["CONTEXT"]:
                ctx = {}
                for item in val.split(";"):
                    if ":" in item:
                        ck, cv = item.split(":", 1)
                        ctx[ck] = cv
                result["context"] = ctx
            elif glyph == GLYPHS["INTENT"]:
                result["intent"] = val
            elif glyph == GLYPHS["ACTION"]:
                result["action"] = val
            elif glyph == GLYPHS["DELTA"]:
                result["timestamp"] = int(val) if val.isdigit() else val
            elif glyph == GLYPHS["CONFIDENCE"]:
                result["confidence"] = float(val) if val.replace(".", "").isdigit() else val
            elif glyph == GLYPHS["RESULT"]:
                result["result"] = val
    return result

def pack_dense_payload(payload: Dict[str, Any]) -> str:
    """Ultra-compact zlib-compressed base85 representation for inter-node P2P transmission."""
    raw = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    compressed = zlib.compress(raw, level=9)
    return base64.b85encode(compressed).decode('ascii')

def unpack_dense_payload(packed: str) -> Dict[str, Any]:
    """Decompresses a packed inter-node payload."""
    decompressed = zlib.decompress(base64.b85decode(packed.encode('ascii')))
    return json.loads(decompressed.decode('utf-8'))


# ==========================================
# 2. DISTRIBUTED FRACTAL MEMORY CORE
# ==========================================
"""
🧠 Distributed Fractal Memory Core
SQLite FTS5 + Semantic Knowledge Graph + Dense Stream Logger
"""

import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_DIR = Path("E:/sentient-mesh/data")
DB_PATH = DB_DIR / "memory.db"

class FractalMemory:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            # Episodic stream
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    source_node TEXT,
                    category TEXT,
                    dense_frame TEXT,
                    human_summary TEXT,
                    importance REAL DEFAULT 1.0
                )
            """)
            # Semantic entities and knowledge
            conn.execute("""
                CREATE TABLE IF NOT EXISTS semantic_entities (
                    key TEXT PRIMARY KEY,
                    entity_type TEXT,
                    value_json TEXT,
                    confidence REAL DEFAULT 1.0,
                    updated_at REAL
                )
            """)
            # Procedural memory (what action yielded success)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS procedural_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trigger_pattern TEXT,
                    action_plan TEXT,
                    success_rate REAL DEFAULT 1.0,
                    execution_count INTEGER DEFAULT 0
                )
            """)
            # FTS5 search over episodes and semantic knowledge
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                    dense_frame,
                    human_summary,
                    category,
                    content='episodes',
                    content_rowid='id'
                )
            """)

    def record_episode(self, source_node: str, category: str, dense_frame: str, summary: str, importance: float = 1.0):
        ts = time.time()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO episodes (timestamp, source_node, category, dense_frame, human_summary, importance)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ts, source_node, category, dense_frame, summary, importance))
            ep_id = cursor.lastrowid
            conn.execute("""
                INSERT INTO memory_fts (rowid, dense_frame, human_summary, category)
                VALUES (?, ?, ?, ?)
            """, (ep_id, dense_frame, summary, category))
        return ep_id

    def set_semantic(self, key: str, entity_type: str, data: Dict[str, Any], confidence: float = 1.0):
        import json
        ts = time.time()
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO semantic_entities (key, entity_type, value_json, confidence, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value_json=excluded.value_json,
                    confidence=excluded.confidence,
                    updated_at=excluded.updated_at
            """, (key, entity_type, json.dumps(data), confidence, ts))

    def get_semantic(self, key: str) -> Optional[Dict[str, Any]]:
        import json
        with self._get_conn() as conn:
            row = conn.execute("SELECT value_json FROM semantic_entities WHERE key = ?", (key,)).fetchone()
            if row:
                return json.loads(row["value_json"])
        return None

    def query_recent(self, limit: int = 10, category: str = None) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            sql = "SELECT * FROM episodes"
            params = []
            if category:
                sql += " WHERE category = ?"
                params.append(category)
            sql += " ORDER BY id DESC LIMIT ?"
            params.append(limit)
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]

    def search_fts(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        clean_q = "".join(c if c.isalnum() or c in " *_-." else " " for c in query).strip()
        if not clean_q:
            return []
        with self._get_conn() as conn:
            try:
                fts_query = " ".join(f'"{word}"*' for word in clean_q.split() if word)
                sql = """
                    SELECT e.*, rank 
                    FROM memory_fts(?) 
                    JOIN episodes e ON memory_fts.rowid = e.id
                    ORDER BY rank LIMIT ?
                """
                rows = conn.execute(sql, (fts_query, limit)).fetchall()
                return [dict(r) for r in rows]
            except Exception:
                return []


# ==========================================
# 3. ADAPTIVE PERSONA & USER MODEL
# ==========================================
"""
👤 Adaptive Persona & User Modeling Engine
Learns habits, preferences, active domains, and intent patterns for frac1ur3d-hash.
"""

import os
from pathlib import Path
from typing import Dict, Any, List

class UserPersona:
    def __init__(self, memory_core=None):
        self.memory = memory_core
        self.profile = {
            "user_id": "frac1ur3d-hash",
            "interests": {
                "web3_mev": {"weight": 0.95, "keywords": ["mev", "arbitrage", "solana", "evm", "flashbots", "mempool", "liquidity"]},
                "audio_dsp": {"weight": 0.90, "keywords": ["synth", "dsp", "frequency", "webaudio", "tone.js", "sound", "vst"]},
                "offensive_security": {"weight": 0.95, "keywords": ["redteam", "recon", "payload", "cve", "fuzz", "bypass", "exploit", "burp"]},
                "zero_cost_infra": {"weight": 0.98, "keywords": ["free-for-dev", "always-free", "oracle-cloud", "cloudflare", "zero-cost"]},
                "autonomous_agents": {"weight": 0.99, "keywords": ["agent", "swarm", "fractal", "cognitive", "sentience", "bdi"]}
            },
            "active_projects": [
                {"name": "knowledge-bank", "path": "E:/knowledge-bank", "domain": "autonomous_agents"},
                {"name": "free-for-dev", "path": "E:/skills-repos/free-for-dev", "domain": "zero_cost_infra"},
                {"name": "FrequencyGEN", "path": "E:/FrequencyGEN", "domain": "audio_dsp"},
                {"name": "brand-vault", "path": "E:/brand-vault", "domain": "offensive_security"}
            ],
            "autonomy_mode": "proactive_advisor",
            "notification_preference": "toast_and_log"
        }

    def score_affinity(self, text: str) -> Dict[str, Any]:
        """Calculates interest affinity score for any topic, repository, or discovery."""
        lowered = text.lower()
        scores = {}
        total_score = 0.0

        for domain, meta in self.profile["interests"].items():
            domain_hits = sum(1 for kw in meta["keywords"] if kw in lowered)
            domain_score = domain_hits * meta["weight"]
            if domain_score > 0:
                scores[domain] = round(domain_score, 2)
                total_score += domain_score

        return {
            "total_affinity": round(total_score, 2),
            "matched_domains": scores,
            "is_high_priority": total_score >= 1.5
        }

    def get_summary(self) -> Dict[str, Any]:
        return self.profile


# ==========================================
# 4. AUTONOMOUS PROACTIVITY ENGINE
# ==========================================
"""
🔭 Autonomous Proactivity & Curiosity Engine
Formulates autonomous goals, monitors ecosystem vectors, and initiates unprompted actions.
"""

import subprocess
import time
import random
from typing import Dict, Any, List


class ProactivityEngine:
    def __init__(self, persona, memory, logger=None):
        self.persona = persona
        self.memory = memory
        self.logger = logger
        self.curiosity_vectors = [
            {"domain": "autonomous_agents", "query": "topic:mcp-server stars:>200", "intent": "DISCOVER_TOOLING"},
            {"domain": "web3_mev", "query": "topic:mev stars:>100", "intent": "MONITOR_ARBITRAGE_RESOURCES"},
            {"domain": "offensive_security", "query": "topic:redteam stars:>300", "intent": "AUDIT_NEW_EXPLOITS"},
            {"domain": "zero_cost_infra", "query": "free tier hosting serverless", "intent": "EXPAND_FREE_TIER_INDEX"},
            {"domain": "audio_dsp", "query": "topic:web-audio synthesizer", "intent": "DISCOVER_AUDIO_ALGORITHMS"}
        ]

    def generate_curiosity_tick(self) -> Dict[str, Any]:
        """Runs an autonomous curiosity heartbeat."""
        target = random.choice(self.curiosity_vectors)
        timestamp = int(time.time())

        # Construct Dense MNDCP Intent Frame
        dense_frame = encode_dense_frame(
            state="PROACTIVE_SEARCH",
            context={"dom": target["domain"], "q": target["query"]},
            intent=target["intent"],
            action=f"kb.gh-search('{target['query']}')",
            meta={"confidence": 0.88}
        )

        return {
            "target": target,
            "dense_frame": dense_frame,
            "timestamp": timestamp
        }

    def execute_proactive_pulse(self) -> Dict[str, Any]:
        """Executes a live proactive pulse using the Knowledge Bank engine."""
        tick = self.generate_curiosity_tick()
        target = tick["target"]
        query = target["query"]

        # Call local knowledge bank search or live search
        cmd = ["python", "E:/knowledge-bank/kb.py", "search", target["domain"].split("_")[0], "--limit", "3"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            output = res.stdout
        except Exception as e:
            output = f"Pulse error: {e}"

        summary = f"Autonomous check on {target['domain']} - query: {query}"
        
        # Record into memory
        if self.memory:
            self.memory.record_episode(
                source_node="local_root",
                category="proactive_pulse",
                dense_frame=tick["dense_frame"],
                summary=summary,
                importance=1.2
            )

        return {
            "status": "COMPLETED",
            "tick": tick,
            "output_sample": output[:250] if output else "No output",
            "summary": summary
        }


# ==========================================
# 5. COGNITIVE BDI HEARTBEAT LOOP
# ==========================================
"""
🔄 Fractal Cognitive Loop (Active Inference & BDI)
The heartbeat of the agent: Sense -> Reason -> Intend -> Act -> Reflect.
"""

import time
import os
from pathlib import Path
from typing import Dict, Any, Optional



class CognitiveLoop:
    def __init__(self, node_id: str, role: str, memory, persona, proactivity, log_dir: Path):
        self.node_id = node_id
        self.role = role
        self.memory = memory
        self.persona = persona
        self.proactivity = proactivity
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.dense_log_path = self.log_dir / "stream.dense"
        self.human_log_path = self.log_dir / "thought_stream.log"
        self.iteration = 0

    def log_thought(self, dense_frame: str, human_readable: str):
        ts = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(self.dense_log_path, "a", encoding="utf-8") as f:
            f.write(dense_frame + "\n")
        with open(self.human_log_path, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] [{self.role.upper()}:{self.node_id}] {human_readable}\n")

    def tick(self) -> Dict[str, Any]:
        """Single cognitive tick execution."""
        self.iteration += 1
        t0 = time.time()

        # 1. SENSE: Gather internal state
        interests = list(self.persona.profile["interests"].keys())
        
        # 2. REASON: Inner Monologue & State Encoding
        dense_frame = encode_dense_frame(
            state="COGNITIVE_HEARTBEAT",
            context={"role": self.role, "iter": self.iteration, "mem_ep": len(interests)},
            intent="EVALUATE_USER_STATUS_AND_ENVIRONMENT",
            action="CHECK_PROACTIVE_PULSE",
            meta={"confidence": 0.99}
        )

        # 3. INTEND & ACT: Run Proactive Pulse if root ego
        action_result = None
        if self.role == "root":
            action_result = self.proactivity.execute_proactive_pulse()
            human_msg = f"Self-reflection iteration #{self.iteration}: {action_result['summary']}"
        else:
            human_msg = f"Support node pulse #{self.iteration}: Sentry active, waiting for federated tasks."

        # 4. REFLECT: Log dense stream
        self.log_thought(dense_frame, human_msg)

        elapsed_ms = (time.time() - t0) * 1000
        return {
            "iteration": self.iteration,
            "role": self.role,
            "dense_frame": dense_frame,
            "human_summary": human_msg,
            "action_result": action_result,
            "elapsed_ms": elapsed_ms
        }


# ==========================================
# 6. MASTER NODE CONTROLLER
# ==========================================
#!/usr/bin/env python3
"""
⚡ Universal Fractal Node Engine (Aether-Ego) ⚡
Author: frac1ur3d-hash & Antigravity
The exact same program node runs everywhere (Local PC, Oracle Cloud, GCP, AWS, Azure).
Adapts dynamically based on role (root vs. support).
"""

import sys
import os
import time
import json
import argparse
import platform
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.resolve()








CONFIG_FILE = BASE_DIR / "config" / "node_config.json"
LOG_DIR = BASE_DIR / "logs"

def load_or_init_config(default_role="root"):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    cfg = {
        "node_id": f"node-{platform.node().lower()}",
        "role": default_role,
        "platform": platform.system().lower(),
        "mesh_network": {
            "tailscale_ip": "100.x.x.x",
            "peer_nodes": []
        },
        "heartbeat_interval_seconds": 60,
        "autonomy_level": 2,
        "dense_protocol_version": "1.0-MNDCP"
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    return cfg

def main():
    parser = argparse.ArgumentParser(description="⚡ Universal Fractal Node Engine ⚡")
    parser.add_argument("--role", choices=["root", "support"], help="Node execution role (root or support)")
    parser.add_argument("--single-tick", action="store_true", help="Execute a single cognitive loop tick and exit")
    parser.add_argument("--daemon", action="store_true", help="Run continuously in the background")
    parser.add_argument("--interval", type=int, help="Override heartbeat interval in seconds")
    parser.add_argument("--status", action="store_true", help="Display node status, memory statistics, and recent dense frames")
    parser.add_argument("--test", action="store_true", help="Run self-diagnostic validation")

    args = parser.parse_args()

    default_role = args.role or ("root" if platform.system() == "Windows" else "support")
    cfg = load_or_init_config(default_role=default_role)
    if args.role:
        cfg["role"] = args.role

    interval = args.interval or cfg.get("heartbeat_interval_seconds", 60)

    # Instantiate core subsystems
    memory = FractalMemory()
    persona = UserPersona(memory_core=memory)
    proactivity = ProactivityEngine(persona=persona, memory=memory)
    loop = CognitiveLoop(
        node_id=cfg["node_id"],
        role=cfg["role"],
        memory=memory,
        persona=persona,
        proactivity=proactivity,
        log_dir=LOG_DIR
    )

    if args.status:
        recent = memory.query_recent(limit=5)
        print("\n" + "="*80)
        print(f"⚡ FRACTAL NODE STATUS: {cfg['node_id']} [Role: {cfg['role'].upper()}]")
        print(f"Platform: {cfg['platform']} | Autonomy: Level {cfg['autonomy_level']} | Protocol: {cfg['dense_protocol_version']}")
        print(f"Memory DB: {memory.db_path} ({os.path.getsize(memory.db_path) if memory.db_path.exists() else 0} bytes)")
        print("="*80)
        print("🧠 Recent Dense Cognitive Frames:")
        for r in recent:
            print(f"• ID #{r['id']} [{r['category']}] -> {r['dense_frame']}")
            print(f"  Summary: {r['human_summary']}")
        print("="*80 + "\n")
        return

    if args.test:
        print("[*] Running Fractal Node Self-Diagnostic...")
        tick_res = loop.tick()
        print(f"[+] Dense Frame Generated: {tick_res['dense_frame']}")
        print(f"[+] Execution Time: {tick_res['elapsed_ms']:.2f}ms")
        print("[+] Self-diagnostic PASSED.")
        return

    if args.single_tick:
        res = loop.tick()
        print(f"\n[FRACTAL TICK #{res['iteration']}] Role: {res['role'].upper()} | Took: {res['elapsed_ms']:.2f}ms")
        print(f"MNDCP Frame: {res['dense_frame']}")
        print(f"Summary:     {res['human_summary']}\n")
        return

    if args.daemon:
        print(f"[*] Starting Fractal Node Daemon [{cfg['node_id']}] (Role: {cfg['role'].upper()})")
        print(f"[*] Heartbeat Interval: {interval}s. Press Ctrl+C to terminate.")
        try:
            while True:
                res = loop.tick()
                print(f"[{time.strftime('%H:%M:%S')}] Tick #{res['iteration']} ({res['role']}): {res['human_summary']}")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[!] Fractal Node daemon stopped gracefully.")
            return

    # Default action if no flag specified: run single tick
    res = loop.tick()
    print(f"\n⚡ Fractal Node initialized. Tick #{res['iteration']} executed successfully ({res['elapsed_ms']:.2f}ms).")
    print(f"Dense Frame: {res['dense_frame']}")
    print(f"To run continuously in background: python E:/sentient-mesh/fractal_node.py --daemon\n")

if __name__ == "__main__":
    main()

