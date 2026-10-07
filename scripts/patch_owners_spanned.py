"""Backfill owners_spanned on run records written before the field existed."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "code")
from decent.datasets.metaqa import load_prepared_queries  # noqa: E402
from decent.kg import KnowledgeGraph  # noqa: E402
from decent.partition import hash_partition, relation_family_partition  # noqa: E402


def main(run_dirs: list[str]) -> None:
    for run_dir in run_dirs:
        run = Path(run_dir)
        cfg = json.loads((run / "summary.json").read_text())["config"]
        kg = KnowledgeGraph.from_tsv(cfg["kb_path"])
        seed = int(cfg.get("partition_seed", 0))
        parts = (
            relation_family_partition(kg, cfg["num_owners"], seed=seed)
            if cfg["partition_method"] == "relation_family"
            else hash_partition(kg, cfg["num_owners"], seed=seed)
        )
        owner_of = {t.as_tuple(): o for o, ts in parts.items() for t in ts}
        spanned: dict[str, int] = {}
        for q in load_prepared_queries(cfg["query_path"], limit=cfg.get("limit")):
            _, evidence = kg.follow_chain(q.topic_entity, q.relation_chain)
            spanned[q.query_id] = len({owner_of[t.as_tuple()] for t in evidence if t.as_tuple() in owner_of})
        for path in run.glob("*.jsonl"):
            rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
            for row in rows:
                row["owners_spanned"] = spanned.get(row["query_id"], 0)
            path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        print(f"patched {run_dir} ({len(spanned)} queries)")


if __name__ == "__main__":
    main(sys.argv[1:])
