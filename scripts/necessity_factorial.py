"""2x2 necessity experiment: controller topology crossed with evidence access.

                       | one controller | n owner agents
  union reachable      | Single-Union   | Multi-Union
  evidence stays local | Single-Broker  | DECENT

Every cell uses the same reader model, the same decoding parameters and the same
cap on evidence triples, so remaining differences come from who may see what.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, "code")
from decent.baselines import run_method  # noqa: E402
from decent.datasets.metaqa import load_prepared_queries  # noqa: E402
from decent.llm import LLMConfig, LocalLLM  # noqa: E402
from decent.runner import _witness, build_owners  # noqa: E402

ANSWER_SYSTEM = (
    "You answer a question using ONLY the evidence triples provided. "
    "Each triple is written as: subject | relation | object. "
    "Reply with JSON only: {\"answers\": [\"...\"]}. "
    "If the evidence does not support an answer, reply {\"answers\": []}."
)

# Protocol that supplies each cell's evidence. "Union reachable" gives every owner
# the whole graph instead of a private shard.
ARMS = {
    "single_union": {"method": "single_union", "union": True, "multi_agent": False},
    "multi_union": {"method": "decent", "union": True, "multi_agent": True},
    "single_broker": {"method": "single_broker", "union": False, "multi_agent": False},
    "decent": {"method": "decent", "union": False, "multi_agent": True},
}


def verbalise(triples: list[tuple[str, str, str]], cap: int) -> str:
    return "\n".join(f"{h} | {r} | {t}" for h, r, t in triples[:cap])


def parse_answers(raw: str) -> list[str]:
    raw = raw.strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start >= 0 and end > start:
        try:
            data = json.loads(raw[start : end + 1])
            answers = data.get("answers", [])
            if isinstance(answers, list):
                return [str(a).strip() for a in answers if str(a).strip()]
        except json.JSONDecodeError:
            pass
    return []


def f1(pred: set[str], gold: set[str]) -> float:
    if not pred and not gold:
        return 1.0
    if not pred or not gold:
        return 0.0
    hit = len(pred & gold)
    if not hit:
        return 0.0
    p, r = hit / len(pred), hit / len(gold)
    return 2 * p * r / (p + r)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query-path", required=True)
    ap.add_argument("--kb-path", default=None,
                    help="shared KB; leave empty when each question carries its own subgraph (WebQSP/CWQ)")
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--owners", type=int, default=5)
    ap.add_argument("--partition", default="hash")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--token-budgets", nargs="+", type=int, default=[2000, 4000, 8000])
    ap.add_argument("--triple-budgets", nargs="+", type=int, default=[25, 50, 100])
    ap.add_argument("--model", default=None)
    ap.add_argument("--out", default="results/necessity/factorial.json")
    args = ap.parse_args()

    queries = load_prepared_queries(args.query_path, limit=args.limit)
    # WebQSP/CWQ carry a per-question subgraph in metadata, so shards cannot be built
    # once for the dataset. Build per question there, and cache by path so repeated
    # subgraphs are not re-read.
    per_query_kb = args.kb_path is None
    private = None if per_query_kb else build_owners(args.kb_path, args.partition, args.owners, seed=args.seed)
    # Union cells: every owner holds the whole graph.
    from decent.kg import KnowledgeGraph
    from decent.protocols import OwnerAgent

    shard_cache: dict[str, list] = {}
    union_cache: dict[str, list] = {}
    full = None if per_query_kb else KnowledgeGraph.from_tsv(args.kb_path)
    union_owners = None if per_query_kb else [OwnerAgent(f"owner_{i}", full.triples) for i in range(args.owners)]

    def owners_for(query, union: bool):
        if not per_query_kb:
            return union_owners if union else private
        kb = query.metadata["kb_path"]
        cache = union_cache if union else shard_cache
        if kb not in cache:
            if union:
                g = KnowledgeGraph.from_tsv(kb)
                cache[kb] = [OwnerAgent(f"owner_{i}", g.triples) for i in range(args.owners)]
            else:
                cache[kb] = build_owners(kb, args.partition, args.owners, seed=args.seed)
        return cache[kb]

    def witness_for(query):
        graph = full if not per_query_kb else KnowledgeGraph.from_tsv(query.metadata["kb_path"])
        return _witness(graph, query)

    llm = LocalLLM(LLMConfig(model_path=args.model) if args.model else LLMConfig())
    # Witnesses are computed against the complete graph, not a shard, so the audit asks
    # the same question of every arm regardless of who happens to hold the triples.

    results = {}
    for arm, spec in ARMS.items():
        for triple_budget in args.triple_budgets:
            # Evidence first: the symbolic protocol decides WHICH triples cross the cut,
            # capped at the same number for every arm.
            evidence_per_query = []
            audit_rows = []
            for query in queries:
                params = {"certificate_mode": "raw", "budget": float(triple_budget)} if spec["method"] == "decent" else {}
                r = run_method(spec["method"], query, owners_for(query, spec["union"]), params,
                               witness_triples=witness_for(query))
                triples = []
                for cert in r.certificates:
                    for t in r.evidence_tables[cert["evidence_ref"]]:
                        if t not in triples:
                            triples.append(t)
                evidence_per_query.append(triples[:triple_budget])
                # Disclosure and witness statistics are recorded next to F1.
                audit_rows.append((
                    r.disclosed_triples,
                    float(r.audit_summary.get("witness_violation", 0)),
                    float(r.audit_summary.get("witness_parties", 0)),
                ))

            for token_budget in args.token_budgets:
                prompts = [
                    f"Question: {q.question}\nEvidence:\n{verbalise(ev, triple_budget)}"
                    for q, ev in zip(queries, evidence_per_query)
                ]
                outs, counts = llm.chat_counted(prompts, system=ANSWER_SYSTEM, max_new_tokens=min(token_budget, 256))
                scores, spent = [], []
                for q, out, n in zip(queries, outs, counts):
                    scores.append(f1(set(parse_answers(out)), set(q.answers)))
                    spent.append(n)
                key = f"{arm}_T{token_budget}_D{triple_budget}"
                results[key] = {
                    "arm": arm, "token_budget": token_budget, "triple_budget": triple_budget,
                    "f1": sum(scores) / len(scores),
                    "tokens_mean": sum(spent) / len(spent),
                    "tokens_max": max(spent),
                    "evidence_mean": sum(len(e) for e in evidence_per_query) / len(evidence_per_query),
                    "disclosed_mean": sum(a[0] for a in audit_rows) / len(audit_rows),
                    "witness_violation": sum(a[1] for a in audit_rows) / len(audit_rows),
                    "witness_parties": sum(a[2] for a in audit_rows) / len(audit_rows),
                }
                print(f"  {key:38s} F1={results[key]['f1']:.3f} "
                      f"token_tb={results[key]['tokens_mean']:6.1f} evi={results[key]['evidence_mean']:6.1f} "
                      f"lo={results[key]['disclosed_mean']:6.2f} thay_n.chung={results[key]['witness_violation']:.0%} "
                      f"so_ben={results[key]['witness_parties']:.2f}", flush=True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"dataset": args.dataset, "n": len(queries),
                               "partition": args.partition, "owners": args.owners,
                               "results": results}, indent=2))
    print(f"\n  wrote {out}")


if __name__ == "__main__":
    main()
