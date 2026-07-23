#!/bin/bash

# ================== CONFIG ==================
# Absolute path to your project
PROJECT_DIR="/home/jetsonboii/Final_agri_scan"

# Python virtual environment path
VENV_PATH="/home/jetsonboii/nidar"

# MAVProxy command
MAVPROXY_CMD="mavproxy.py \
  --master=/dev/ttyACM0 \
  --out=udp:127.0.0.1:14550 \
  --out=udp:127.0.0.1:14551"

# Python program to run
PYTHON_CMD="python3 main.py"

# ================== SCRIPT ==================
echo "===== STARTING AUTONOMOUS SYSTEM ====="

# Go to project directory
cd "$PROJECT_DIR" || {
  echo "[ERROR] Project directory not found"
  exit 1
}

# Activate virtual environment
echo "[INFO] Activating virtual environment"
source "$VENV_PATH/bin/activate" || {
  echo "[ERROR] Failed to activate virtualenv"
  exit 1
}

# Start MAVProxy in new terminal (non-blocking)
echo "[INFO] Starting MAVProxy"
gnome-terminal -- bash -c "$MAVPROXY_CMD; exec bash"

# Optional delay to allow MAVProxy to fully connect
sleep 3

# Run main mission program
echo "[INFO] Running main mission"
 $PYTHON_CMD

# ================== CLEANUP ==================
echo "[INFO] Mission script finished"

