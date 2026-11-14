set -eu
mkdir -p reports
python3 -m bandit -r scripts/check_coverage.py -lll -f json -o reports/bandit.json
if test -s requirements-python.txt; then
  python3 -m safety check --file requirements-python.txt --output json > reports/safety.json
else
  python3 -c 'import json; from pathlib import Path; Path("reports/safety.json").write_text(json.dumps({"status": "not_applicable", "reason": "No Python application dependencies; check_coverage.py uses only the standard library. JS dependencies are audited by npm audit."}, indent=2))'
  echo "Safety: no Python application dependencies to scan; npm audit checks JavaScript dependencies."
fi
