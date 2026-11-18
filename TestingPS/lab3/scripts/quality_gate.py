"""Итоговый CI-check не пропускает failed, cancelled, skipped и пустой результат."""

import json
import os

REQUIRED = {"unit", "security", "build", "integration", "e2e"}


def main():
  results = json.loads(os.environ["JOB_RESULTS"])
  for job, value in results.items():
    print(f"{job}: {value['result']}")
  if set(results) != REQUIRED or any(value["result"] != "success" for value in results.values()):
    raise SystemExit("Quality gate failed: every required job must succeed.")
  print("All required jobs passed.")


if __name__ == "__main__":
  main()
