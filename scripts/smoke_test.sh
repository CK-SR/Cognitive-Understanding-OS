#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

cat > "$TMP_DIR/config.yaml" <<CFG
workspace_dir: $TMP_DIR/.cuos_workspace
parser:
  default: mock
  adapters:
    mock: {}
llm:
  provider: mock
  model: mock-model
prompts:
  dir: $ROOT_DIR/prompts
CFG

cd "$ROOT_DIR"
python -m cuos.cli --config "$TMP_DIR/config.yaml" init
python -m cuos.cli --config "$TMP_DIR/config.yaml" ingest examples/sample_paper.md --parser mock
PAPER_ID="$(find "$TMP_DIR/.cuos_workspace/papers" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | head -n1)"
python -m cuos.cli --config "$TMP_DIR/config.yaml" map "$PAPER_ID" --llm mock
python -m cuos.cli --config "$TMP_DIR/config.yaml" session "$PAPER_ID" --non-interactive-demo
SESSION_ID="$(find "$TMP_DIR/.cuos_workspace/papers/$PAPER_ID/sessions" -name 'session_*.json' -printf '%f\n' | sed 's/.json$//' | head -n1)"
python -m cuos.cli --config "$TMP_DIR/config.yaml" audit "$PAPER_ID" --session "$SESSION_ID" --llm mock
python -m cuos.cli --config "$TMP_DIR/config.yaml" review --llm mock --non-interactive-demo
python -m pytest -q
