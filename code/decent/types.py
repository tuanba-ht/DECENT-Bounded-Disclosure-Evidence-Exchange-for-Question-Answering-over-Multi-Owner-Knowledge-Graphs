from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Triple:
    head: str
    relation: str
    tail: str

    def as_tuple(self) -> tuple[str, str, str]:
        return (self.head, self.relation, self.tail)


@dataclass
class QueryExample:
    query_id: str
    question: str
    topic_entity: str
    relation_chain: list[str]
    answers: set[str]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceCertificate:
    answer: str
    supporting_triples: list[Triple]
    owner_path: list[str]


@dataclass
class RunResult:
    query_id: str
    method: str
    predicted_answers: list[str]
    gold_answers: list[str]
    exact_match: float
    answer_f1: float
    hits_at_1: float
    coverage: float
    rounds: int
    messages: int
    disclosed_triples: int
    disclosed_bytes: int
    owner_entropy: float
    abstained: bool
    certificates: list[dict[str, Any]]
    audit_summary: dict[str, Any]
    evidence_tables: list[list[tuple[str, str, str]]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    transcript: list[dict[str, Any]] = field(default_factory=list)

    def to_record(self, include_details: bool = False) -> dict[str, Any]:
        record = {
            "query_id": self.query_id,
            "method": self.method,
            "exact_match": self.exact_match,
            "answer_f1": self.answer_f1,
            "hits_at_1": self.hits_at_1,
            "coverage": self.coverage,
            "rounds": self.rounds,
            "messages": self.messages,
            "disclosed_triples": self.disclosed_triples,
            "disclosed_bindings": int(self.audit_summary.get("disc_B", 0)),
            "witness_parties": int(self.audit_summary.get("witness_parties", 0)),
            "disclosed_relations": int(self.audit_summary.get("disc_R", 0)),
            "disclosed_entities": int(self.audit_summary.get("disc_E", 0)),
            "disclosure_cost": self.disclosed_triples + int(self.audit_summary.get("disc_B", 0)),
            "disclosed_bytes": self.disclosed_bytes,
            "owner_entropy": self.owner_entropy,
            "abstained": self.abstained,
            "num_predicted_answers": len(self.predicted_answers),
            "num_gold_answers": len(self.gold_answers),
            "audit_summary": self.audit_summary,
            "metadata": self.metadata,
        }
        if include_details:
            record["predicted_answers"] = self.predicted_answers
            record["gold_answers"] = self.gold_answers
            record["certificates"] = self.certificates
            record["evidence_tables"] = self.evidence_tables
        else:
            record["predicted_answers_sample"] = self.predicted_answers[:5]
            record["gold_answers_sample"] = self.gold_answers[:5]
            record["certificate_sizes"] = [cert["num_supporting_triples"] for cert in self.certificates[:10]]
            record["certificate_count"] = len(self.certificates)
        return record
