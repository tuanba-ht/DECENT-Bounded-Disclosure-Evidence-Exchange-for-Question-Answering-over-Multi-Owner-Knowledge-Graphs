from __future__ import annotations

import json
from pathlib import Path


class JsonlCheckpoint:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def completed_ids(self) -> set[str]:
        if not self.path.exists():
            return set()
        done: set[str] = set()
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                done.add(record["query_id"])
        return done

    def append(self, record: dict[str, object]) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")
