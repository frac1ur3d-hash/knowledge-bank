#!/usr/bin/env bash
# ==============================================================================
# ⚡ Aether-Ego Support Node: 1-Click Zero-Cost Cloud Bootstrapper ⚡
# Runs on: Oracle Cloud Always Free (ARM/x86), GCP e2-micro, AWS, Azure, Fly.io
# ==============================================================================

set -e

echo "=== [1/4] Detecting Environment & Installing Runtime ==="
if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -qq && sudo apt-get install -y -qq python3 curl git sqlite3
elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y -q python3 curl git sqlite3
elif command -v yum >/dev/null 2>&1; then
    sudo yum install -y -q python3 curl git sqlite3
elif command -v apk >/dev/null 2>&1; then
    sudo apk add --no-cache python3 curl git sqlite3 bash
fi

echo "=== [2/4] Deploying Universal Fractal Node ==="
INSTALL_DIR="/opt/aether-ego"
sudo mkdir -p "$INSTALL_DIR/data" "$INSTALL_DIR/logs" "$INSTALL_DIR/config"
cd "$INSTALL_DIR"

NODE_URL="https://raw.githubusercontent.com/frac1ur3d-hash/knowledge-bank/main/mesh/aether_node.py"
echo "[*] Downloading standalone node from GitHub ($NODE_URL)..."
sudo curl -sSL "$NODE_URL" -o "$INSTALL_DIR/aether_node.py"
sudo chmod +x "$INSTALL_DIR/aether_node.py"

echo "=== [3/4] Configuring Support Node Persona ==="
cat << 'EOF' | sudo tee "$INSTALL_DIR/config/node_config.json" > /dev/null
{
  "node_id": "cloud-support-node",
  "role": "support",
  "platform": "linux",
  "heartbeat_interval_seconds": 60,
  "autonomy_level": 2,
  "dense_protocol_version": "1.0-MNDCP"
}
EOF

echo "=== [4/4] Setting Up 24/7 Systemd Service ==="
cat << 'EOF' | sudo tee /etc/systemd/system/aether-ego.service > /dev/null
[Unit]
Description=Aether-Ego Distributed Fractal Support Node
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/aether-ego
ExecStart=/usr/bin/python3 /opt/aether-ego/aether_node.py --role support --daemon
Restart=always
RestartSec=10
StandardOutput=append:/opt/aether-ego/logs/thought_stream.log
StandardError=append:/opt/aether-ego/logs/thought_stream.log

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable aether-ego.service
sudo systemctl restart aether-ego.service

echo ""
echo "====================================================================="
echo "⚡ Aether-Ego Cloud Support Node is LIVE and running 24/7! ⚡"
echo "Status check:  sudo systemctl status aether-ego"
echo "Inspect thoughts: tail -f /opt/aether-ego/logs/thought_stream.log"
echo "Single tick:   python3 /opt/aether-ego/aether_node.py --status"
echo "====================================================================="
