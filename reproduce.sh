#!/usr/bin/env bash
# reproduce.sh — Single-command reproduction for paper-spec
#
# Conforms to PUBLIC_MIRROR_STANDARD.md v1.0.0.
#
# What this does:
#   1. Syncs Python dependencies via `uv sync` (creates .venv, installs paper-spec).
#   2. Validates every example in examples/ against the JSON Schema.
#   3. Runs the test suite (pytest) if tests are present.
#   4. Writes run log to output/logs/master_run.log.
#
# Usage:
#   ./reproduce.sh                  # Run full reproduction
#   ./reproduce.sh --check-only     # Verify dependencies; do not run validation
#
# Outputs land in output/ split by type: figures/ tables/ logs/

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

mkdir -p output/figures output/tables output/logs
LOG_FILE="output/logs/master_run.log"

echo "==================================================" | tee -a "$LOG_FILE"
echo "Pipeline run: $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LOG_FILE"
echo "Repo: $REPO_ROOT" | tee -a "$LOG_FILE"
echo "Git SHA: $(git rev-parse HEAD 2>/dev/null || echo 'not-a-repo')" | tee -a "$LOG_FILE"
echo "==================================================" | tee -a "$LOG_FILE"

# Parse flags
CHECK_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --check-only) CHECK_ONLY=1 ;;
    *) echo "Unknown flag: $arg"; exit 2 ;;
  esac
done

# 1. Dependency sync via uv
echo ">>> Syncing dependencies with uv..." | tee -a "$LOG_FILE"
if command -v uv >/dev/null 2>&1; then
  uv sync 2>&1 | tee -a "$LOG_FILE"
else
  echo "ERROR: uv not found. Install via 'curl -LsSf https://astral.sh/uv/install.sh | sh'" | tee -a "$LOG_FILE"
  exit 1
fi

if [[ "$CHECK_ONLY" == "1" ]]; then
  echo ">>> Check-only mode; exiting before validation." | tee -a "$LOG_FILE"
  exit 0
fi

# 2. Validate every example paper.yaml against the JSON Schema
echo ">>> Validating examples/ against schema/paper-spec-v0.1.0.json..." | tee -a "$LOG_FILE"
if [[ -f schema/paper-spec-v0.1.0.json ]]; then
  uv run python tools/validate.py examples/*.yaml 2>&1 | tee -a "$LOG_FILE" || true
else
  echo "(schema file not found; skipping example validation)" | tee -a "$LOG_FILE"
fi

# 3. Run tests if a test suite is present
if [[ -d tests ]] || find . -maxdepth 3 -name "test_*.py" -not -path "./.venv/*" -not -path "./.mypy_cache/*" | grep -q .; then
  echo ">>> Running test suite..." | tee -a "$LOG_FILE"
  uv run pytest 2>&1 | tee -a "$LOG_FILE" || true
else
  echo ">>> No tests found; skipping pytest." | tee -a "$LOG_FILE"
fi

echo "==================================================" | tee -a "$LOG_FILE"
echo "Pipeline complete: $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LOG_FILE"
echo "==================================================" | tee -a "$LOG_FILE"
