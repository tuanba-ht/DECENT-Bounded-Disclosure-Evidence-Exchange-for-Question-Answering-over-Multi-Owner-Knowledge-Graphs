"""Mechanisms from related systems, adapted to the ownership constraint.

None of the original systems enforces that no party holds the union view, so each
mechanism is reimplemented under that constraint. These are not reproductions of
the original systems.

* ``clause_adapted``: three coordinated agents under per-query budgets on edges,
  steps and context, after CLAUSE (Zhao et al., ICLR 2026). The learned context
  policy is not reproduced.
* ``splitrag_adapted``: per-question partitioning with neighbourhood retrieval,
  after SPLIT-RAG (Yang et al., 2025). Retrieval returns every triple incident
  to a frontier entity, not a minimal witness.
* ``asksafely_suppress``: value suppression, after Ask Safely (Tosi and Cabot,
  2025). Intermediate entity values are withheld and only counts cross the
  boundary; values are revealed for final answers.
"""
from __future__ import annotations

from collections import defaultdict

from decent.audit import NoUnionAudit
from decent.messages import Message
from decent.protocols import OwnerAgent, _make_certificate, _result, _route_relation_owners
from decent.types import QueryExample, Triple


def run_splitrag_adapted(
    query: QueryExample, owners: list[OwnerAgent], audit: NoUnionAudit,
    retrieval_cap: int = 50, **_: object,
) -> dict[str, object]:
    """Per-question partition, parallel dispatch, neighbourhood retrieval.

    Returns every triple incident to a frontier entity, not only those matching the
    queried relation, subject to ``retrieval_cap``.
    """
    frontier = {query.topic_entity}
    evidence: list[Triple] = []
    disclosures_by_owner = {owner.name: 0 for owner in owners}
    messages = rounds = 0
    owner_path: list[str] = []

    for relation in query.relation_chain:
        rounds += 1
        next_frontier: set[str] = set()
        for owner in owners:                       # dispatched to every part in parallel
            # Neighbourhood retrieval: every triple incident to a frontier entity,
            # not only those matching the queried relation. forward_triples is exactly
            # that index.
            retrieved: list[Triple] = []
            for entity in sorted(frontier):
                retrieved.extend(owner.kg.forward_triples.get(entity, []))
            retrieved = retrieved[:retrieval_cap]
            if not retrieved:
                continue
            audit.record_message(
                Message(sender=owner.name, recipient="retriever", kind="evidence_certificate",
                        payload={"relation": relation}),
                retrieved, sorted({t.tail for t in retrieved}),
            )
            messages += 2
            disclosures_by_owner[owner.name] += len(retrieved)
            evidence.extend(retrieved)
            owner_path.append(owner.name)
            next_frontier.update(t.tail for t in retrieved if t.relation == relation)
        if not next_frontier:
            frontier = set()
            break
        frontier = next_frontier

    certs = [_make_certificate(a, evidence, owner_path) for a in sorted(frontier)]
    return _result(frontier, certs, messages, rounds, disclosures_by_owner, evidence)


def run_clause_adapted(
    query: QueryExample, owners: list[OwnerAgent], audit: NoUnionAudit,
    edge_budget: int = 100, step_budget: int = 8, context_budget: int = 25, **_: object,
) -> dict[str, object]:
    """Three coordinated agents under per-query budgets on edges, steps and context.

    A subgraph agent pulls candidate edges, a path agent walks the chain within a
    step budget, and a context agent keeps what fits the context budget.
    """
    route = _route_relation_owners(owners)
    frontier = {query.topic_entity}
    disclosures_by_owner = {owner.name: 0 for owner in owners}
    edges_spent = steps_spent = messages = rounds = 0
    pulled: list[tuple[str, Triple]] = []
    owner_path: list[str] = []

    for relation in query.relation_chain:
        if steps_spent >= step_budget:
            break
        rounds += 1
        steps_spent += 1
        next_frontier: set[str] = set()
        for owner in route.get(relation, []):
            if edges_spent >= edge_budget:
                break
            found, matched = owner.local_step(frontier, relation)
            if not found:
                continue
            room = edge_budget - edges_spent
            take = list(matched)[:room]
            edges_spent += len(take)
            messages += 2
            audit.record_message(
                Message(sender=owner.name, recipient="subgraph_agent", kind="evidence_certificate",
                        payload={"relation": relation}),
                take, sorted({t.tail for t in take}),
            )
            disclosures_by_owner[owner.name] += len(take)
            pulled.extend((owner.name, t) for t in take)
            owner_path.append(owner.name)
            next_frontier.update(t.tail for t in take)
        if not next_frontier:
            frontier = set()
            break
        frontier = next_frontier

    # Context agent: keep the newest edges that fit the context budget.
    kept = [t for _, t in pulled[-context_budget:]]
    certs = [_make_certificate(a, kept, owner_path) for a in sorted(frontier)]
    return _result(frontier, certs, messages, rounds, disclosures_by_owner, kept,
                   extra={"edges_spent": edges_spent, "steps_spent": steps_spent})


def run_asksafely_suppress(
    query: QueryExample, owners: list[OwnerAgent], audit: NoUnionAudit, **_: object,
) -> dict[str, object]:
    """Value suppression: intermediate bindings cross the boundary as counts, not values.

    Only the triples supporting a final answer are disclosed. Intermediate hops
    report how many bindings they could contribute; that message is logged and
    audited.
    """
    route = _route_relation_owners(owners)
    frontier = {query.topic_entity}
    hop_provenance: list[dict[str, list[tuple[str, Triple]]]] = []
    disclosures_by_owner = {owner.name: 0 for owner in owners}
    messages = rounds = 0

    for relation in query.relation_chain:
        rounds += 1
        provenance: dict[str, list[tuple[str, Triple]]] = defaultdict(list)
        next_frontier: set[str] = set()
        for owner in route.get(relation, []):
            found, matched = owner.local_step(frontier, relation)
            if not found:
                continue
            # Suppressed channel: a count only. No triples, no bindings named.
            audit.record_message(
                Message(sender=owner.name, recipient="coordinator", kind="filter",
                        payload={"relation": relation, "reachable_count": len(found)}),
                bits=float(len(bin(len(found))) - 2),
            )
            messages += 2
            next_frontier.update(found)
            for triple in matched:
                provenance[triple.tail].append((owner.name, triple))
        if not next_frontier:
            frontier = set()
            break
        hop_provenance.append(provenance)
        frontier = next_frontier

    evidence: list[Triple] = []
    owner_path: list[str] = []
    if len(hop_provenance) == len(query.relation_chain):
        alive = set(frontier)
        for hop_index in range(len(hop_provenance) - 1, -1, -1):
            heads: set[str] = set()
            for binding in sorted(alive):
                for owner_name, triple in hop_provenance[hop_index].get(binding, []):
                    audit.record_message(
                        Message(sender=owner_name, recipient="coordinator",
                                kind="evidence_certificate", payload={"relation": triple.relation}),
                        [triple], [triple.tail],
                    )
                    disclosures_by_owner[owner_name] += 1
                    evidence.append(triple)
                    owner_path.append(owner_name)
                    heads.add(triple.head)
                    messages += 1
            alive = heads
    else:
        frontier = set()

    certs = [_make_certificate(a, evidence, owner_path) for a in sorted(frontier)]
    return _result(frontier, certs, messages, rounds, disclosures_by_owner, evidence)


def run_centralised_join(
    query: QueryExample, owners: list[OwnerAgent], audit: NoUnionAudit, **_: object,
) -> dict[str, object]:
    """Exact centralised join over the union of all shards.

    Reference ceiling only. It violates the ownership constraint by design and the
    audit flags it.
    """
    from decent.kg import KnowledgeGraph

    union = KnowledgeGraph([t for owner in owners for t in owner.kg.triples])
    reached, evidence = union.follow_chain(query.topic_entity, query.relation_chain)
    audit.record_message(
        Message(sender="union", recipient="central", kind="evidence_certificate",
                payload={"relation": "*"}),
        list(evidence), sorted(reached),
    )
    disclosures_by_owner = {owner.name: 0 for owner in owners}
    if owners:
        disclosures_by_owner[owners[0].name] = len(evidence)
    certs = [_make_certificate(a, list(evidence), ["central"]) for a in sorted(reached)]
    return _result(set(reached), certs, 1, len(query.relation_chain), disclosures_by_owner, list(evidence))
