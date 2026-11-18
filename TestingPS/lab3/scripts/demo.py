"""Изолированные причины отказа quality gates для учебных прогонов."""

import argparse
import os
from pathlib import Path

import bookshop

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = Path(bookshop.__file__).resolve().parent
PROBES = [
  ROOT / "tests/unit/test_failure_probe.py",
  PACKAGE / "coverage_probe.py",
  ROOT / "src/bookshop/security_probe.py",
]


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("stage", choices=["unit", "coverage", "security", "clean"])
  stage = parser.parse_args().stage
  mode = os.environ.get("LAB3_DEMO", "none")
  if mode not in {"none", "unit", "coverage", "security", "e2e"}:
    raise SystemExit("Unknown LAB3_DEMO mode")
  if stage == "clean":
    for path in PROBES:
      path.unlink(missing_ok=True)
    return
  if mode != stage:
    return
  if stage == "unit":
    target = PROBES[0]
    content = (
      "from bookshop.domain import money\n\n"
      "def test_quality_gate_probe():\n"
      '  assert money(129000) == "1 290,01 ₽"\n'
    )
  elif stage == "coverage":
    target = PROBES[1]
    content = (
      "def uncovered_path():\n"
      + "".join(f"  value = {i}\n" for i in range(100))
      + "  return value\n"
    )
  else:
    target = PROBES[2]
    content = (
      "import subprocess\n\n"
      "def security_probe(command):\n"
      "  return subprocess.run(command, shell=True, check=True)\n"
    )
  if target.exists():
    raise SystemExit(f"Probe already exists: {target}. Run demo.py clean first.")
  target.write_text(content, encoding="utf-8")
  print(f"Prepared {stage} gate probe: {target.name}")


if __name__ == "__main__":
  main()
