from __future__ import annotations

from math import isclose
from typing import Any, Callable

from decent.audit import NoUnionAudit
from decent.baselines_lit import (
    run_asksafely_suppress,
    run_centralised_join,
    run_clause_adapted,
    run_splitrag_adapted,
)
from decent.protocols import (
    OwnerAgent,
    run_broadcast_all,
    run_decent,
    run_oracle_semijoin,
    run_random_gossip,
    run_single_broker,
    run_single_union,
    run_star_coordinator,
)
from decent.types import QueryExample, RunResult, Triple

PROTOCOLS: dict[str, Callable[..., dict[str, Any]]] = {
    "single_broker": run_single_broker,
    "broadcast_all": run_broadcast_all,
    "decent": run_decent,
    "oracle_semijoin": run_oracle_semijoin,
    "random_gossip": run_random_gossip,
    "star_coordinator": run_star_coordinator,
    "splitrag_adapted": run_splitrag_adapted,
    "clause_adapted": run_clause_adapted,
    "asksafely_suppress": run_asksafely_suppress,
    "centralised_join": run_centralised_join,
    "single_union": run_single_union,
}

# Arms that intentionally break the ownership constraint; reference rows only.
CEILINGS = {"single_union", "centralised_join"}


def _answer_f1(predicted: set[str], gold: set[str]) -> float:
    if not predicted and not gold:
        return 1.0
    if not predicted or not gold:
        return 0.0
    overlap = len(predicted & gold)
    precision = overlap / len(predicted)
    recall = overlap / len(gold)
    if isclose(precision + recall, 0.0):
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _hits_at_1(predicted: set[str], gold: set[str]) -> float:
    """Hits@1 under uniform random tie-breaking.

    The protocols return an answer set, not a ranking, so the score is the expected
    value of picking one predicted answer at random: |pred & gold| / |pred|. It
    equals the usual Hits@1 when a single answer is returned.
    """
    if not predicted:
        return 0.0
    return len(predicted & gold) / len(predicted)


def run_method(
    method: str,
    query: QueryExample,
    owners: list[OwnerAgent],
    params: dict[str, Any] | None = None,
    witness_triples: list[Triple] | None = None,
) -> RunResult:
    audit = NoUnionAudit([owner.name for owner in owners])
    union_size = 0
    for owner in owners:
        audit.register_local_graph(owner.name, owner.kg.triples)
        union_size += len(owner.kg.triples)

    base = method.split("@", 1)[0]
    if base not in PROTOCOLS:
        raise ValueError(f"Unsupported method: {method}")
    protocol = PROTOCOLS[base]

    raw = protocol(query, owners, audit, **(params or {}))
    predicted = set(raw["answers"])
    gold = set(query.answers)
    exact_match = 1.0 if predicted == gold else 0.0
    f1 = _answer_f1(predicted, gold)
    coverage = len(predicted & gold) / max(1, len(gold))
    hits_at_1 = _hits_at_1(predicted, gold)
    # Wire volume over the distinct triples that crossed an owner boundary. A triple
    # shared by several certificates is counted once.
    disclosed_bytes = sum(len(repr(triple).encode("utf-8")) for triple in audit.disclosed_triples)
    audit_summary = audit.summary(
        union_size=union_size,
        disclosures_by_owner=raw["disclosures_by_owner"],
        witness_triples=witness_triples,
    )

    # Certificates that share an evidence list reference it by index, so each distinct
    # list is stored once.
    evidence_tables: list[list[tuple[str, str, str]]] = []
    table_index: dict[int, int] = {}
    certificates: list[dict[str, Any]] = []
    for cert in raw["certificates"]:
        key = id(cert.supporting_triples)
        if key not in table_index:
            table_index[key] = len(evidence_tables)
            evidence_tables.append([triple.as_tuple() for triple in cert.supporting_triples])
        certificates.append(
            {
                "answer": cert.answer,
                "evidence_ref": table_index[key],
                "num_supporting_triples": len(cert.supporting_triples),
                "owner_path": cert.owner_path,
            }
        )

    metadata = dict(query.metadata)
    metadata["method_params"] = params or {}
    metadata["disclosure_spent"] = raw.get("disclosure_spent")
    metadata["budget_exhausted"] = raw.get("budget_exhausted", False)
    metadata["is_ceiling"] = base in CEILINGS

    result = RunResult(
        query_id=query.query_id,
        method=method,
        predicted_answers=sorted(predicted),
        gold_answers=sorted(gold),
        exact_match=exact_match,
        answer_f1=f1,
        hits_at_1=hits_at_1,
        coverage=coverage,
        rounds=raw["rounds"],
        messages=raw["messages"],
        disclosed_triples=int(audit_summary["disc_T"]),
        disclosed_bytes=disclosed_bytes,
        owner_entropy=float(audit_summary["owner_entropy"]),
        abstained=not predicted,
        certificates=certificates,
        evidence_tables=evidence_tables,
        audit_summary=audit_summary,
        metadata=metadata,
    )
    result.transcript = audit.transcript
    return result
