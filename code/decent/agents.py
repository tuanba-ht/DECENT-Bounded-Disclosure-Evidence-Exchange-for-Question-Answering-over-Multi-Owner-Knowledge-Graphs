"""LLM agent roles. Only the parser is load-bearing for the protocol study."""
from __future__ import annotations

import json
import re
from typing import Any

from decent.llm import LocalLLM
from decent.types import QueryExample

# Inverse relations are written `<relation>__inv`. The prompt states this convention
# because the vocabulary lists both directions and many chains need a reverse hop.
# Only the schema is described; no hint about typical chain shapes is given.
PARSER_SYSTEM = (
    "You translate a natural-language question into a relation path over a knowledge graph. "
    "You never see the graph itself, only the published relation vocabulary. "
    "A relation written NAME__inv is NAME traversed in the reverse direction: if NAME goes "
    "from A to B, then NAME__inv goes from B to A. A path may use a relation and its "
    "inverse, and may revisit a relation, whenever the question requires moving back along "
    "an edge. "
    "Answer with JSON only."
)

PARSER_TEMPLATE = """Question: {question}
Topic entity: {topic}
Allowed relations (choose only from this list):
{relations}

Return JSON: {{"relation_chain": ["<relation>", ...]}} with {hops} relation(s), in order from the topic entity to the answer."""


def _format_relations(relations: list[str], limit: int = 60) -> str:
    return "\n".join(f"- {relation}" for relation in relations[:limit])


def parse_chains(
    llm: LocalLLM,
    queries: list[QueryExample],
    relation_vocab: dict[str, list[str]],
    hops_hint: bool = True,
) -> list[dict[str, Any]]:
    """Predict a relation chain per query. Returns one record per query."""
    prompts = []
    for query in queries:
        vocab = relation_vocab.get(query.query_id) or relation_vocab.get("__global__", [])
        prompts.append(
            PARSER_TEMPLATE.format(
                question=query.question,
                topic=query.topic_entity,
                relations=_format_relations(vocab),
                hops=len(query.relation_chain) if hops_hint else "1 to 3",
            )
        )
    raw_outputs = llm.chat(prompts, system=PARSER_SYSTEM)

    records = []
    for query, raw in zip(queries, raw_outputs):
        vocab = set(relation_vocab.get(query.query_id) or relation_vocab.get("__global__", []))
        chain = _extract_chain(raw, vocab)
        records.append(
            {
                "query_id": query.query_id,
                "gold_chain": query.relation_chain,
                "predicted_chain": chain,
                "exact_chain_match": chain == query.relation_chain,
                "raw": raw[:400],
            }
        )
    return records


def _extract_chain(raw: str, vocab: set[str]) -> list[str]:
    match = re.search(r"\{.*\}", raw, re.S)
    if match:
        try:
            payload = json.loads(match.group(0))
            chain = payload.get("relation_chain") or []
            chain = [str(relation) for relation in chain if str(relation) in vocab]
            if chain:
                return chain
        except json.JSONDecodeError:
            pass
    # Fallback: any known relation mentioned, in order of appearance.
    hits = [(raw.find(relation), relation) for relation in vocab if relation in raw]
    return [relation for _, relation in sorted(hits) if _ >= 0][:3]
