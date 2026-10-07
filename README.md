# DECENT

Code for "Bounded-Disclosure Evidence Exchange for Question Answering over
Multi-Owner Knowledge Graphs".

A knowledge graph is split into shards held by different owners. No party,
including the coordinator, may hold the union of the shards. DECENT answers
multi-hop questions in this setting: owners exchange evidence certificates under
a per-query disclosure budget, and the coordinator abstains on answers whose
support the budget cannot pay for. An audit logs what every party can see at
every turn and reports witness exposure and the number of exposed parties.

## Layout

```
code/decent/          package
  protocols.py        DECENT and the comparison protocols
  baselines_lit.py    mechanisms adapted from related systems
  audit.py            disclosure ledger and no-union-view audit
  adversary.py        transcript reconstruction adversary
  partition.py        hash, relation-family and community partitioners
  agents.py, llm.py   LLM parser and reader (optional)
  datasets/           MetaQA, WebQSP and CWQ loaders
code/tests/           unit tests
scripts/              experiment drivers and report generators
experiments/configs/  one JSON config per experiment cell
results/              tables and JSON outputs
```

## Install

Python 3.11 or newer. The protocols and the audit use only the standard library.

```bash
pip install -e .            # core
pip install -e ".[data]"    # WebQSP / CWQ loaders (pyarrow)
pip install -e ".[llm]"     # parser and reader experiments
pip install -e ".[plots]"   # figure script
pip install -e ".[test]" && pytest code/tests
```

## Data

MetaQA: download the dataset and place it under `data/raw/metaqa/MetaQA/`, then

```bash
python -m decent.cli convert-metaqa-kb \
  --raw-kb-path data/raw/metaqa/MetaQA/kb.txt \
  --output-path data/raw/metaqa/kb.tsv
python scripts/prepare_metaqa_qtype.py --hops 2 \
  --output-path data/processed/metaqa/metaqa_2hop_qtype_300.jsonl
```

Relation chains are taken from MetaQA's question-type labels. The script refuses
to write a split unless the chains reach the gold answers in the KB.

WebQSP and CWQ (RoG release):

```bash
bash scripts/fetch_data.sh
python -m decent.cli prepare-rog-split --dataset webqsp \
  --parquet data/raw/rog_webqsp/data/*.parquet \
  --subgraph-dir data/processed/rog_webqsp/subgraphs \
  --output-path data/processed/rog_webqsp/webqsp_test.jsonl
```

## Running

Main sweep (DECENT budget grid plus the protocol baselines) for one dataset:

```bash
python scripts/sweep.py --dataset metaqa2hop \
  --query-path data/processed/metaqa/metaqa_2hop_qtype_300.jsonl \
  --kb-path data/raw/metaqa/kb.tsv \
  --partitions hash relation_family community --owner-counts 5 --seeds 1 2 3
```

Adapted baselines on the same shards:

```bash
python scripts/run_baselines.py --dataset metaqa2hop \
  --query-path data/processed/metaqa/metaqa_2hop_qtype_300.jsonl \
  --kb-path data/raw/metaqa/kb.tsv
```

A single cell can be run from its config:

```bash
python -m decent.cli run-experiment --config experiments/configs/metaqa2hop_hash_n5_s1.json
```

Each cell writes one JSONL file per arm and a `summary.json` under
`experiments/runs/`. Every record carries the audit summary for that question.

Reports:

```bash
python scripts/make_table1.py        # results/main_results.md
python scripts/report_audit.py       # audit, adversary, risk-coverage
python scripts/report_strata.py --dataset webqsp --arms broadcast_all decent_hash_Binf single_broker
python scripts/make_frontier_figure.py
```

Experiments that need a language model (`DECENT_MODEL_DIR` points at the weights):

```bash
python scripts/run_parser.py --query-path <queries.jsonl> --output-path <parsed.jsonl>
python scripts/build_parsed_queries.py --query-path <queries.jsonl> \
  --parser-path <parsed.jsonl> --output-path <end_to_end_queries.jsonl>
python scripts/necessity_factorial.py --dataset metaqa2hop \
  --query-path data/processed/metaqa/metaqa_2hop_qtype_300.jsonl \
  --kb-path data/raw/metaqa/kb.tsv
python scripts/ablation_selector.py --dataset metaqa2hop \
  --query-path data/processed/metaqa/metaqa_2hop_qtype_300.jsonl \
  --kb-path data/raw/metaqa/kb.tsv
```

## Results

`results/main_results.md` holds the main table for all five datasets at five
owners, pooled over three partition treatments and three seeds, with a
breakdown by the number of owners a gold witness spans. `results/necessity/`
and `results/ablation/` hold the outputs of the 2x2 experiment and the
owner-selector ablation.

## Arms

| Name in code | Description |
|---|---|
| `decent` | DECENT (hashed or raw certificates, optional budget) |
| `single_broker` | one owner asked per hop |
| `broadcast_all` | every owner replies to every party |
| `star_coordinator` | every owner replies to a central hub |
| `random_gossip` | DECENT backward pass, raw certificates, random order |
| `oracle_semijoin` | classical distributed semijoin |
| `splitrag_adapted` | neighbourhood retrieval over partitions |
| `clause_adapted` | three budgeted agents |
| `asksafely_suppress` | semijoin with values suppressed |
| `single_union`, `centralised_join` | ceilings that break the ownership constraint |
