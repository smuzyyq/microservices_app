#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STACK_NAME="${1:-foodrushswarm}"

docker info --format '{{.Swarm.LocalNodeState}}' | grep -q '^active$' || docker swarm init >/dev/null

docker stack deploy -c "$ROOT_DIR/docker-stack.yml" "$STACK_NAME"

echo
echo "Swarm stack deployed: $STACK_NAME"
docker stack services "$STACK_NAME"
