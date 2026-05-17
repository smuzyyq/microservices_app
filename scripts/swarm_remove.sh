#!/bin/bash
set -euo pipefail

STACK_NAME="${1:-foodrushswarm}"

docker stack rm "$STACK_NAME"

echo "Swarm stack removal requested: $STACK_NAME"
