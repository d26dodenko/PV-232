import json
import sys
from pathlib import Path


def check(paths):
    for filename in paths:
        report = json.loads(Path(filename).read_text(encoding="utf-8"))
        for name, metrics in report.items():
            for metric in ("lines", "statements", "functions", "branches"):
                value = metrics[metric]["pct"]
                if not isinstance(value, (int, float)) or value < 80:
                    raise ValueError(f"{filename}: {name}: {metric}={value}, expected >=80")
        print(f"Coverage >=80%: {filename}")


if __name__ == "__main__":
    check(sys.argv[1:])
