from __future__ import annotations

import json
from pathlib import Path


def prepare_webqsp_split(
    official_json_path: str,
    simple_jsonl_path: str,
    subgraph_dir: str,
    output_path: str,
    limit: int | None = None,
) -> dict[str, int]:
    simple_index = _load_simple_index(simple_jsonl_path)
    official = json.load(open(official_json_path, "r", encoding="utf-8"))
    questions = official["Questions"]
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    subgraph_root = Path(subgraph_dir)
    subgraph_root.mkdir(parents=True, exist_ok=True)

    total = 0
    written = 0
    skipped = 0
    with out_path.open("w", encoding="utf-8") as out:
        for question in questions:
            if limit is not None and written >= limit:
                break
            total += 1
            record = simple_index.get(question["QuestionId"])
            if record is None:
                skipped += 1
                continue
            parse = _pick_parse(question)
            if parse is None:
                skipped += 1
                continue
            kb_path = subgraph_root / f"{question['QuestionId']}.tsv"
            _write_subgraph_tsv(record["subgraph"]["tuples"], kb_path)
            prepared = {
                "query_id": question["QuestionId"],
                "question": question["ProcessedQuestion"],
                "topic_entity": parse["TopicEntityMid"],
                "relation_chain": list(parse["InferentialChain"]),
                "answers": [answer["AnswerArgument"] for answer in parse["Answers"]],
                "metadata": {
                    "dataset": "WebQSP",
                    "kb_path": str(kb_path),
                    "max_answers": 10,
                },
            }
            out.write(json.dumps(prepared, ensure_ascii=True) + "\n")
            written += 1
    return {"total": total, "written": written, "skipped": skipped}


def _load_simple_index(path: str) -> dict[str, dict]:
    index: dict[str, dict] = {}
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            obj = json.loads(line)
            index[obj["id"]] = obj
    return index


def _pick_parse(question: dict) -> dict | None:
    for parse in question.get("Parses", []):
        chain = parse.get("InferentialChain") or []
        answers = parse.get("Answers") or []
        if chain and answers and len(chain) <= 3:
            return parse
    return None


def _write_subgraph_tsv(tuples: list[list[str]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as out:
        for head, relation, tail in tuples:
            out.write(f"{head}\t{relation}\t{tail}\n")
            out.write(f"{tail}\t{relation}__inv\t{head}\n")
