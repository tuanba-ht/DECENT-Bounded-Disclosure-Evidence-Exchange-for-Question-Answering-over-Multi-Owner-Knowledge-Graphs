from __future__ import annotations

import argparse
import json

from decent.datasets.metaqa import convert_metaqa_kb, prepare_metaqa_split, synthesize_path_queries
from decent.datasets.webqsp import prepare_webqsp_split
from decent.runner import run_experiment


def main() -> None:
    parser = argparse.ArgumentParser(description="DECENT command-line interface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    synth = subparsers.add_parser("synthesize-metaqa", help="Create synthetic path queries from a MetaQA-style KB TSV")
    synth.add_argument("--kb-path", required=True)
    synth.add_argument("--output-path", required=True)
    synth.add_argument("--num-queries", type=int, default=200)
    synth.add_argument("--max-hops", type=int, default=3)
    synth.add_argument("--seed", type=int, default=13)
    synth.add_argument("--partition-method", choices=["relation_family", "hash"])
    synth.add_argument("--num-owners", type=int, default=0)
    synth.add_argument("--min-owners-spanned", type=int, default=1)

    convert = subparsers.add_parser("convert-metaqa-kb", help="Convert MetaQA kb.txt to TSV triples")
    convert.add_argument("--raw-kb-path", required=True)
    convert.add_argument("--output-path", required=True)
    convert.add_argument("--no-inverse", action="store_true")

    prep = subparsers.add_parser("prepare-metaqa-split", help="Infer relation chains for a MetaQA split")
    prep.add_argument("--kb-path", required=True)
    prep.add_argument("--qa-path", required=True)
    prep.add_argument("--output-path", required=True)
    prep.add_argument("--hops", type=int, required=True)
    prep.add_argument("--limit", type=int)

    webqsp = subparsers.add_parser("prepare-webqsp-split", help="Prepare WebQSP queries with per-question subgraphs")
    webqsp.add_argument("--official-json", required=True)
    webqsp.add_argument("--simple-jsonl", required=True)
    webqsp.add_argument("--subgraph-dir", required=True)
    webqsp.add_argument("--output-path", required=True)
    webqsp.add_argument("--limit", type=int)

    rog = subparsers.add_parser("prepare-rog-split", help="Prepare WebQSP/CWQ from the RoG parquet release")
    rog.add_argument("--parquet", nargs="+", required=True)
    rog.add_argument("--subgraph-dir", required=True)
    rog.add_argument("--output-path", required=True)
    rog.add_argument("--dataset", required=True)
    rog.add_argument("--limit", type=int)
    rog.add_argument("--min-chain-f1", type=float, default=0.5)

    rep = subparsers.add_parser("report", help="Aggregate run directories into tables and Pareto fronts")
    rep.add_argument("--run-dirs", nargs="+", required=True)
    rep.add_argument("--out-dir", required=True)

    run = subparsers.add_parser("run-experiment", help="Run one experiment cell from a JSON config")
    run.add_argument("--config", required=True)

    args = parser.parse_args()

    if args.command == "synthesize-metaqa":
        synthesize_path_queries(
            kb_path=args.kb_path,
            output_path=args.output_path,
            num_queries=args.num_queries,
            max_hops=args.max_hops,
            seed=args.seed,
            partition_method=args.partition_method,
            num_owners=args.num_owners,
            min_owners_spanned=args.min_owners_spanned,
        )
    elif args.command == "convert-metaqa-kb":
        convert_metaqa_kb(
            raw_kb_path=args.raw_kb_path,
            output_tsv_path=args.output_path,
            add_inverse=not args.no_inverse,
        )
    elif args.command == "prepare-metaqa-split":
        stats = prepare_metaqa_split(
            kb_path=args.kb_path,
            qa_path=args.qa_path,
            output_path=args.output_path,
            hops=args.hops,
            limit=args.limit,
        )
        print(json.dumps(stats, indent=2, ensure_ascii=True))
    elif args.command == "prepare-webqsp-split":
        stats = prepare_webqsp_split(
            official_json_path=args.official_json,
            simple_jsonl_path=args.simple_jsonl,
            subgraph_dir=args.subgraph_dir,
            output_path=args.output_path,
            limit=args.limit,
        )
        print(json.dumps(stats, indent=2, ensure_ascii=True))
    elif args.command == "prepare-rog-split":
        from decent.datasets.rog import prepare_rog_split

        stats = prepare_rog_split(
            parquet_paths=args.parquet,
            subgraph_dir=args.subgraph_dir,
            output_path=args.output_path,
            dataset=args.dataset,
            limit=args.limit,
            min_chain_f1=args.min_chain_f1,
        )
        print(json.dumps(stats, indent=2, ensure_ascii=True))
    elif args.command == "report":
        from decent.analysis import report

        payload = report(run_dirs=args.run_dirs, out_dir=args.out_dir)
        print(json.dumps({"pareto_front": payload["pareto_front"]}, indent=2))
    elif args.command == "run-experiment":
        summary = run_experiment(args.config)
        print(json.dumps(summary, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
