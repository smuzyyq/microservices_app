#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

echo "Inspecting recent container logs for known failure patterns..."
echo

docker compose logs --tail=200 |
  grep -E -i "database|connection refused|failed to connect|unauthorized|traceback|exception|error|restart" ||
  echo "No matching error patterns were found in the latest logs."
