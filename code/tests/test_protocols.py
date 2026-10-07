from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from decent.audit import NoUnionAudit
from decent.baselines import run_method
from decent.protocols import OwnerAgent
from decent.types import QueryExample, Triple


def build_case():
    # Two-hop chain split across three owners, with a redundant owner.
    owners = [
        OwnerAgent("owner_0", [Triple("a", "r1", "b"), Triple("a", "r1", "c")]),
        OwnerAgent("owner_1", [Triple("b", "r2", "x"), Triple("c", "r2", "y")]),
        OwnerAgent("owner_2", [Triple("b", "r2", "x")]),
    ]
    query = QueryExample(
        query_id="q1",
        question="test",
        topic_entity="a",
        relation_chain=["r1", "r2"],
        answers={"x", "y"},
    )
    witness = [Triple("a", "r1", "b"), Triple("a", "r1", "c"), Triple("b", "r2", "x"), Triple("c", "r2", "y")]
    return query, owners, witness


def test_broadcast_reaches_full_coverage():
    query, owners, witness = build_case()
    result = run_method("broadcast_all", query, owners, witness_triples=witness)
    assert result.coverage == 1.0
    assert result.disclosed_triples > 0


def test_decent_matches_broadcast_accuracy_at_lower_cost():
    query, owners, witness = build_case()
    broadcast = run_method("broadcast_all", query, owners, witness_triples=witness)
    decent = run_method("decent", query, owners, {"certificate_mode": "hash", "challenge_rate": 0.0}, witness)
    assert decent.coverage == broadcast.coverage
    assert decent.disclosed_triples < broadcast.disclosed_triples


def test_budget_is_never_exceeded():
    query, owners, witness = build_case()
    for budget in (0, 1, 2, 3):
        decent = run_method("decent", query, owners, {"budget": budget}, witness)
        cost = decent.disclosed_triples + decent.audit_summary["disc_B"]
        assert cost <= budget, (budget, cost)


def test_tighter_budget_never_increases_coverage():
    query, owners, witness = build_case()
    previous = 0.0
    for budget in (0, 1, 2, 3, 4, 8, 16):
        cov = run_method("decent", query, owners, {"budget": budget}, witness).coverage
        assert cov >= previous - 1e-9
        previous = cov


def test_certificates_are_sound():
    query, owners, witness = build_case()
    shard = {t.as_tuple() for o in owners for t in o.kg.triples}
    for method in ("single_broker", "broadcast_all", "decent", "oracle_semijoin", "random_gossip"):
        result = run_method(method, query, owners, witness_triples=witness)
        for cert in result.certificates:
            triples = [tuple(t) for t in result.evidence_tables[cert["evidence_ref"]]]
            assert cert["num_supporting_triples"] == len(triples), method
            assert all(t in shard for t in triples), method
            if method in ("decent", "oracle_semijoin", "single_broker"):
                chain = [t for t in triples if t[1] in query.relation_chain]
                assert chain, method


def test_hash_certificates_avoid_witness_violation():
    query, owners, witness = build_case()
    raw = run_method("decent", query, owners, {"challenge_rate": 1.0}, witness)
    hashed = run_method("decent", query, owners, {"certificate_mode": "hash", "challenge_rate": 0.0}, witness)
    assert hashed.audit_summary["disc_T"] == 0
    assert hashed.audit_summary["disc_T"] < raw.audit_summary["disc_T"]


def test_audit_flags_union_holder():
    query, owners, witness = build_case()
    ceiling = run_method("single_union", query, owners, witness_triples=witness)
    assert ceiling.audit_summary["witness_violation"] is True


def test_shared_evidence_is_materialised_once():
    """Certificates of one query share a single evidence table."""
    query, owners, witness = build_case()
    result = run_method("oracle_semijoin", query, owners, witness_triples=witness)
    if len(result.certificates) > 1:
        assert len(result.evidence_tables) == 1
        assert len({cert["evidence_ref"] for cert in result.certificates}) == 1


def build_noisy_case():
    """Same chain, but each entity also carries unrelated edges.

    Without irrelevant edges a neighbourhood retriever and an exact-match protocol
    fetch the same triples, so the arms could not be told apart.
    """
    noise = [Triple("a", "rx", "n1"), Triple("a", "ry", "n2"),
             Triple("b", "rx", "n3"), Triple("c", "rz", "n4")]
    owners = [
        OwnerAgent("owner_0", [Triple("a", "r1", "b"), Triple("a", "r1", "c")] + noise[:2]),
        OwnerAgent("owner_1", [Triple("b", "r2", "x"), Triple("c", "r2", "y")] + noise[2:]),
        OwnerAgent("owner_2", [Triple("b", "r2", "x")]),
    ]
    query = QueryExample(query_id="q1", question="test", topic_entity="a",
                         relation_chain=["r1", "r2"], answers={"x", "y"})
    witness = [Triple("a", "r1", "b"), Triple("a", "r1", "c"),
               Triple("b", "r2", "x"), Triple("c", "r2", "y")]
    return query, owners, witness


def test_literature_baselines_run_and_are_distinct():
    """The adapted baselines must differ from each other in answers or disclosure."""
    query, owners, witness = build_noisy_case()
    out = {}
    for method in ("splitrag_adapted", "clause_adapted", "asksafely_suppress",
                   "centralised_join", "decent", "single_broker"):
        r = run_method(method, query, owners, witness_triples=witness)
        out[method] = (r.answer_f1, r.disclosed_triples)

    # A neighbourhood retriever discloses the irrelevant edges too; an exact-match
    # protocol does not. That gap is the reason the arm exists.
    assert out["splitrag_adapted"][1] > out["single_broker"][1], out

    # Value suppression must not disclose more than neighbourhood retrieval.
    assert out["asksafely_suppress"][1] <= out["splitrag_adapted"][1], out

    # The ceiling sees the union, so nothing may beat it on accuracy.
    assert out["centralised_join"][0] >= out["decent"][0] - 1e-9, out

    # And they must not all collapse onto one behaviour.
    assert len(set(out.values())) > 1, out
