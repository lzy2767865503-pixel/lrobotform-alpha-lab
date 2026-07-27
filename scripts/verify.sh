#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv"
PYTHON="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Python 3 was not found." >&2
  exit 1
fi

if [[ ! -x "$VENV/bin/python" ]]; then
  "$PYTHON" -m venv "$VENV"
fi

"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install -e "$ROOT"
"$VENV/bin/python" -m unittest discover -s "$ROOT/tests" -v
"$VENV/bin/lrobotform-alpha" "$ROOT/examples/questionnaire.json" \
  --responses 200 \
  --seed 20260724 \
  --target-min 0.70 \
  --target-max 0.90 \
  --csv "$ROOT/output/synthetic_responses.csv" \
  --report "$ROOT/output/alpha_report.json"

"$VENV/bin/python" - "$ROOT/output/alpha_report.json" <<'PY'
import json
import sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
serialized = json.dumps(report, ensure_ascii=False).lower()
if "synthetic" not in serialized:
    raise SystemExit("Generated report does not identify its synthetic-data boundary.")
PY

test -f "$ROOT/output/synthetic_responses.csv"
"$VENV/bin/python" - "$ROOT/output/synthetic_responses.csv" <<'PY'
import csv
import sys
from pathlib import Path

with Path(sys.argv[1]).open(encoding="utf-8-sig", newline="") as handle:
    rows = list(csv.DictReader(handle))
if len(rows) != 200:
    raise SystemExit("Expected exactly 200 deterministic synthetic rows.")
if any(row.get("data_origin") != "synthetic_simulation" for row in rows):
    raise SystemExit("Every CSV row must be explicitly labelled synthetic.")
if any(row.get("simulation_seed") != "20260724" for row in rows):
    raise SystemExit("Every CSV row must preserve the simulation seed.")
PY

test -f "$ROOT/web/index.html"
test -f "$ROOT/web/app.js"
test -f "$ROOT/web/styles.css"

echo "Reproducibility verification passed."
