#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if ! command -v hermes >/dev/null 2>&1; then
  echo "hermes command not found in PATH" >&2
  exit 127
fi

hermes chat \
  --source wis-manual \
  --toolsets terminal,web \
  --skills while-i-sleep \
  -q "$(< prompts/nightly-run.md)"
