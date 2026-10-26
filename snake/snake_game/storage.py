import json
from pathlib import Path


def load_record(path: Path) -> int:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))["best"]
        if type(value) is int and value >= 0:
            return value
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return 0


def save_record(path: Path, score: int) -> bool:
    temporary = path.with_suffix(".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(json.dumps({"best": score}), encoding="utf-8")
        temporary.replace(path)
    except OSError:
        return False
    return True
