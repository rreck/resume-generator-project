#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# Copyright (c) RRECKTEK LLC
# Project: CrewAI Pandoc Agent
# Version: 1.0.0
# Built: @EPOCH
#
# Safe Docker runner for when script lives in ./app
# ------------------------------------------------------------------------------

set -euo pipefail

IMAGE="${IMAGE:-rrecktek/crewai-pandoc:1.0.0}"
SLEEP="${SLEEP:-5}"
MODE="${1:-batch}"   # batch | watch

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

mkdir -p ../input ../output

if [[ ! -f "main.py" ]]; then
  echo "ERROR: main.py not found in $(pwd)" >&2
  exit 2
fi
if [[ ! -f "template.tex" ]]; then
  echo "NOTE: template.tex not found in $(pwd); will try without template"
fi

run_batch() {
  docker run --rm \
    --user "$(id -u):$(id -g)" \
    -v "$(pwd)":/work/app \
    -v "$(pwd)/../input":/work/input \
    -v "$(pwd)/../output":/work/output \
    -w /work/app \
    "$IMAGE" \
    python main.py -i /work/input -o /work/output -t /work/app/template.tex
}

run_watch() {
  docker run --rm \
    --user "$(id -u):$(id -g)" \
    -v "$(pwd)":/work/app \
    -v "$(pwd)/../input":/work/input \
    -v "$(pwd)/../output":/work/output \
    -w /work/app \
    "$IMAGE" \
    python main.py -i /work/input -o /work/output -t /work/app/template.tex -w -s "$SLEEP"
}

case "$MODE" in
  batch) run_batch ;;
  watch) run_watch ;;
  *)
    echo "Usage: ./run.sh [batch|watch]" >&2
    exit 1
    ;;
esac
