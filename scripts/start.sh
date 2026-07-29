#!/usr/bin/env bash
# CHAMP-QN Crypto Readiness Scanner launcher (Linux / macOS).
#
# Docker Compose cannot reliably pick-and-print a free host port through a
# static port mapping, so this script finds one starting at 8080, exports it
# for docker-compose.yml to consume, brings the stack up, and prints the
# final browser URL.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

is_port_free() {
  local port="$1"
  if command -v nc >/dev/null 2>&1; then
    ! nc -z 127.0.0.1 "$port" >/dev/null 2>&1
  elif command -v ss >/dev/null 2>&1; then
    ! ss -ltn 2>/dev/null | awk '{print $4}' | grep -q ":${port}\$"
  else
    # Fallback: try to open a TCP connection with bash's /dev/tcp.
    ! (exec 3<>"/dev/tcp/127.0.0.1/${port}") 2>/dev/null
  fi
}

START_PORT="${CHAMPQN_HOST_PORT:-8080}"
PORT="$START_PORT"
for _ in $(seq 0 20); do
  if is_port_free "$PORT"; then
    break
  fi
  PORT=$((PORT + 1))
done

export CHAMPQN_HOST_PORT="$PORT"

echo "Starting CHAMP-QN Crypto Readiness Scanner..."
echo "Selected host port: ${PORT}"

docker compose up --build -d

echo ""
echo "CHAMP-QN Crypto Readiness Scanner is available at:"
echo "http://localhost:${PORT}"
