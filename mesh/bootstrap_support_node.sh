#!/usr/bin/env bash
# ==============================================================================
# ⚡ Aether-Ego Support Node: 1-Click Zero-Cost Bootstrapper ⚡
# Works on: Full Linux VMs (Oracle, GCP, AWS, Azure), Cloud Shell, Containers
# ==============================================================================

set -e

# Suppress cloudshell warning if present
if [ -d "$HOME/.cloudshell" ]; then
    touch "$HOME/.cloudshell/no-apt-get-warning" 2>/dev/null || true
fi

echo "=== [1/4] Checking Runtime & Dependencies ==="
if ! command -v python3 >/dev/null 2>&1 || ! command -v sqlite3 >/dev/null 2>&1; then
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update -qq && sudo apt-get install -y -qq python3 curl git sqlite3
    elif command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y -q python3 curl git sqlite3
    elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y -q python3 curl git sqlite3
    elif command -v apk >/dev/null 2>&1; then
        sudo apk add --no-cache python3 curl git sqlite3 bash
    fi
else
    echo "[+] Python3 and SQLite are already installed."
fi

echo "=== [2/4] Deploying Universal Fractal Node ==="
# Use /opt/aether-ego if root/sudo available, else use $HOME/aether-ego
if [ -w "/opt" ] || sudo -n true 2>/dev/null || [ "$EUID" -eq 0 ]; then
    INSTALL_DIR="/opt/aether-ego"
    SUDO="sudo"
else
    INSTALL_DIR="$HOME/aether-ego"
    SUDO=""
fi

$SUDO mkdir -p "$INSTALL_DIR/data" "$INSTALL_DIR/logs" "$INSTALL_DIR/config"
cd "$INSTALL_DIR"

NODE_URL="https://raw.githubusercontent.com/frac1ur3d-hash/knowledge-bank/main/mesh/aether_node.py"
echo "[*] Downloading standalone node from GitHub..."
$SUDO curl -sSL "$NODE_URL" -o "$INSTALL_DIR/aether_node.py"
$SUDO chmod +x "$INSTALL_DIR/aether_node.py"

echo "=== [3/4] Configuring Support Node ==="
cat << 'EOF' | $SUDO tee "$INSTALL_DIR/config/node_config.json" > /dev/null
{
  "node_id": "cloud-support-node",
  "role": "support",
  "platform": "linux",
  "heartbeat_interval_seconds": 60,
  "autonomy_level": 2,
  "dense_protocol_version": "1.0-MNDCP"
}
EOF

echo "=== [4/4] Starting Background Service ==="
# Check if systemd is running as PID 1
HAS_SYSTEMD=false
if command -v systemctl >/dev/null 2>&1 && [ -d /run/systemd/system ]; then
    HAS_SYSTEMD=true
fi

if [ "$HAS_SYSTEMD" = true ]; then
    echo "[*] Detected systemd. Installing 24/7 service..."
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
    echo "[+] Systemd service 'aether-ego' is active!"
else
    echo "[*] Non-systemd environment (Cloud Shell / Container). Starting persistent nohup daemon..."
    pkill -f "aether_node.py" 2>/dev/null || true
    nohup python3 "$INSTALL_DIR/aether_node.py" --role support --daemon > "$INSTALL_DIR/logs/thought_stream.log" 2>&1 &
    sleep 2
    if pgrep -f "aether_node.py" > /dev/null; then
        echo "[+] Aether-Ego background process is running (PID: $(pgrep -f 'aether_node.py'))!"
    else
        echo "[-] Failed to start background process. Check logs."
    fi
fi

echo ""
echo "====================================================================="
echo "⚡ Aether-Ego Support Node is LIVE! ⚡"
echo "Inspect thoughts: tail -f $INSTALL_DIR/logs/thought_stream.log"
echo "Check status:     python3 $INSTALL_DIR/aether_node.py --status"
echo "====================================================================="
