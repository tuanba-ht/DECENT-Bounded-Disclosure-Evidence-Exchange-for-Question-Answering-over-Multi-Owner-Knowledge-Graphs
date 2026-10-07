"""Build query files whose relation chain comes from the LLM parser.

Produces the end-to-end counterpart of the oracle query files: the same questions
with the parser's predicted chain substituted in. Gold answers are unchanged.
Queries the parser left empty are kept with an empty chain, so both modes share
one denominator.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query-path", required=True)
    ap.add_argument("--parser-path", required=True)
    ap.add_argument("--output-path", required=True)
    args = ap.parse_args()

    predicted = {}
    for line in Path(args.parser_path).open():
        record = json.loads(line)
        predicted[record["query_id"]] = record.get("predicted_chain") or []

    kept = missing = empty = 0
    out = Path(args.output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as fh:
        for line in Path(args.query_path).open():
            query = json.loads(line)
            qid = query["query_id"]
            if qid not in predicted:
                missing += 1
                continue
            chain = predicted[qid]
            if not chain:
                empty += 1
            query["relation_chain"] = chain
            query.setdefault("metadata", {})["chain_source"] = "llm_parser_v2"
            query["metadata"]["gold_relation_chain"] = json.loads(line)["relation_chain"]
            fh.write(json.dumps(query) + "\n")
            kept += 1
    print(f"wrote {out}: {kept} queries ({empty} empty chains, {missing} without a prediction)")


if __name__ == "__main__":
    main()
