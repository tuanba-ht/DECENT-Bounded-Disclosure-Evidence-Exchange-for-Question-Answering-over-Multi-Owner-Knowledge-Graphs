from __future__ import annotations

import random
from collections import defaultdict
from math import log2

from decent.audit import NoUnionAudit
from decent.kg import KnowledgeGraph
from decent.messages import Message
from decent.types import EvidenceCertificate, QueryExample, Triple

INF_BUDGET = float("inf")


class OwnerAgent:
    def __init__(self, name: str, triples: list[Triple]) -> None:
        self.name = name
        self.kg = KnowledgeGraph(triples)

    def local_step(self, frontier: set[str], relation: str) -> tuple[set[str], list[Triple]]:
        found: set[str] = set()
        evidence: list[Triple] = []
        for entity in frontier:
            tails = self.kg.forward.get((entity, relation), [])
            for tail in tails:
                found.add(tail)
                evidence.append(Triple(entity, relation, tail))
        return found, evidence


def _route_relation_owners(owners: list[OwnerAgent]) -> dict[str, list[OwnerAgent]]:
    route: dict[str, list[OwnerAgent]] = defaultdict(list)
    for owner in owners:
        for relation in owner.kg.by_relation:
            route[relation].append(owner)
    return route


def _make_certificate(answer: str, evidence: list[Triple], owner_path: list[str]) -> EvidenceCertificate:
    return EvidenceCertificate(answer=answer, supporting_triples=evidence, owner_path=owner_path)


def _result(
    answers: set[str],
    certificates: list[EvidenceCertificate],
    messages: int,
    rounds: int,
    disclosures_by_owner: dict[str, int],
    all_evidence: list[Triple],
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "answers": answers,
        "certificates": certificates,
        "messages": messages,
        "rounds": rounds,
        "disclosures_by_owner": disclosures_by_owner,
        "all_evidence": all_evidence,
    }
    payload.update(extra or {})
    return payload


# --------------------------------------------------------------------------
# Comparison arms
# --------------------------------------------------------------------------
def run_broadcast_all(query: QueryExample, owners: list[OwnerAgent], audit: NoUnionAudit, **_: object) -> dict[str, object]:
    """Every owner that can answer a hop pushes its full evidence onto a shared bus."""
    route = _route_relation_owners(owners)
    frontier = {query.topic_entity}
    all_evidence: list[Triple] = []
    disclosures_by_owner = {owner.name: 0 for owner in owners}
    messages = 0
    rounds = 0
    owner_path: list[str] = []

    for relation in query.relation_chain:
        rounds += 1
        next_frontier: set[str] = set()
        for owner in route.get(relation, []):
            found, evidence = owner.local_step(frontier, relation)
            if not evidence:
                continue
            # Every owner on the bus receives the message, so each is recorded as a recipient.
            for listener in owners:
                if listener.name == owner.name:
                    continue
                audit.record_message(
                    Message(
                        sender=owner.name,
                        recipient=listener.name,
                        kind="evidence_certificate",
                        payload={"relation": relation, "source_bindings": sorted({t.head for t in evidence})},
                    ),
                    evidence,
                    sorted(found),
                )
            messages += 1
            disclosures_by_owner[owner.name] += len(evidence)
            next_frontier.update(found)
            all_evidence.extend(evidence)
            owner_path.append(owner.name)
        frontier = next_frontier
        if not frontier:
            break

    certificates = [_make_certificate(answer, all_evidence, owner_path) for answer in sorted(frontier)]
    return _result(frontier, certificates, messages, rounds, disclosures_by_owner, all_evidence)


def run_single_broker(query: QueryExample, owners: list[OwnerAgent], audit: NoUnionAudit, **_: object) -> dict[str, object]:
    """A non-negotiating broker asks exactly one owner per hop (the widest one)."""
    route = _route_relation_owners(owners)
    frontier = {query.topic_entity}
    certificate_evidence: list[Triple] = []
    disclosures_by_owner = {owner.name: 0 for owner in owners}
    messages = 0
    rounds = 0
    owner_path: list[str] = []

    for relation in query.relation_chain:
        rounds += 1
        best_owner = None
        best_found: set[str] = set()
        best_evidence: list[Triple] = []
        for owner in route.get(relation, []):
            found, evidence = owner.local_step(frontier, relation)
            if len(found) > len(best_found):
                best_owner, best_found, best_evidence = owner, found, evidence
        if best_owner is None or not best_found:
            frontier = set()
            break
        msg = Message(
            sender=best_owner.name,
            recipient="broker",
            kind="evidence_certificate",
            payload={"relation": relation, "source_bindings": sorted({t.head for t in best_evidence})},
        )
        audit.record_message(msg, best_evidence, sorted(best_found))
        messages += 1
        disclosures_by_owner[best_owner.name] += len(best_evidence)
        owner_path.append(best_owner.name)
        certificate_evidence.extend(best_evidence)
        frontier = best_found

    certificates = [_make_certificate(answer, certificate_evidence, owner_path) for answer in sorted(frontier)]
    return _result(frontier, certificates, messages, rounds, disclosures_by_owner, certificate_evidence)


def run_star_coordinator(query: QueryExample, owners: list[OwnerAgent], audit: NoUnionAudit, **_: object) -> dict[str, object]:
    """Every owner answers every hop; a central coordinator merges the replies.

    Each owner replies with the bindings it can contribute and the triples that
    justify them. Coverage matches broadcast-all, but owners never talk to each
    other: the hub is the only party with a cross-shard view.
    """
    route = _route_relation_owners(owners)
    frontier = {query.topic_entity}
    certificate_evidence: list[Triple] = []
    disclosures_by_owner = {owner.name: 0 for owner in owners}
    messages = 0
    rounds = 0
    owner_path: list[str] = []

    for relation in query.relation_chain:
        rounds += 1
        next_frontier: set[str] = set()
        hop_owners: list[str] = []
        for owner in route.get(relation, []):
            found, evidence = owner.local_step(frontier, relation)
            messages += 1          # the coordinator asks, whether or not the owner has anything
            if not found:
                continue
            msg = Message(
                sender=owner.name,
                recipient="coordinator",
                kind="evidence_certificate",
                payload={"relation": relation, "source_bindings": sorted({t.head for t in evidence})},
            )
            audit.record_message(msg, evidence, sorted(found))
            messages += 1
            disclosures_by_owner[owner.name] += len(evidence)
            certificate_evidence.extend(evidence)
            next_frontier.update(found)
            hop_owners.append(owner.name)
        if not next_frontier:
            frontier = set()
            break
        owner_path.extend(sorted(set(hop_owners)))
        frontier = next_frontier

    certificates = [_make_certificate(answer, certificate_evidence, owner_path) for answer in sorted(frontier)]
    return _result(frontier, certificates, messages, rounds, disclosures_by_owner, certificate_evidence)


def run_oracle_semijoin(query: QueryExample, owners: list[OwnerAgent], audit: NoUnionAudit, **_: object) -> dict[str, object]:
    """Classical distributed semijoin over the gold chain (no LLM).

    The forward pass reveals bindings; the backward pass pulls the supporting
    triples for surviving bindings only.
    """
    route = _route_relation_owners(owners)
    frontier = {query.topic_entity}
    hop_provenance: list[dict[str, list[tuple[str, Triple]]]] = []
    disclosures_by_owner = {owner.name: 0 for owner in owners}
    messages = 0
    rounds = 0

    for relation in query.relation_chain:
        rounds += 1
        next_frontier: set[str] = set()
        provenance: dict[str, list[tuple[str, Triple]]] = defaultdict(list)
        for owner in route.get(relation, []):
            found, evidence = owner.local_step(frontier, relation)
            if not found:
                continue
            msg = Message(
                sender=owner.name,
                recipient="coordinator",
                kind="binding_set",
                payload={"relation": relation, "source_bindings": sorted({t.head for t in evidence})},
            )
            audit.record_message(msg, [], sorted(found), bits=log2(len(found) + 1))
            messages += 2
            next_frontier.update(found)
            for triple in evidence:
                provenance[triple.tail].append((owner.name, triple))
        if not next_frontier:
            frontier = set()
            break
        hop_provenance.append(provenance)
        frontier = next_frontier

    # Classical backward pass: every triple that survived the reduction is shipped,
    # with no per-answer minimisation. This is the non-LLM protocol floor.
    evidence: list[Triple] = []
    if len(hop_provenance) == len(query.relation_chain):
        alive = set(frontier)
        for hop_index in range(len(hop_provenance) - 1, -1, -1):
            heads: set[str] = set()
            for binding in sorted(alive):
                for owner_name, triple in hop_provenance[hop_index].get(binding, []):
                    audit.record_message(
                        Message(sender=owner_name, recipient="coordinator", kind="evidence_certificate", payload={"relation": triple.relation}),
                        [triple],
                        [triple.tail],
                    )
                    disclosures_by_owner[owner_name] = disclosures_by_owner.get(owner_name, 0) + 1
                    evidence.append(triple)
                    heads.add(triple.head)
                    messages += 1
            alive = heads
    else:
        frontier = set()
    certificates = [_make_certificate(a, evidence, ["semijoin"]) for a in sorted(frontier)]
    return _result(frontier, certificates, messages, rounds, disclosures_by_owner, evidence)


def run_single_union(query: QueryExample, owners: list[OwnerAgent], audit: NoUnionAudit, **_: object) -> dict[str, object]:
    """Reference ceiling: one reasoner holds the union view. Violates ownership by design."""
    all_triples: list[Triple] = []
    for owner in owners:
        all_triples.extend(owner.kg.triples)
        msg = Message(sender=owner.name, recipient="union_reasoner", kind="shard_dump", payload={})
        audit.record_message(msg, owner.kg.triples, sorted({t.tail for t in owner.kg.triples}))
    union = KnowledgeGraph(all_triples)
    answers, evidence = union.follow_chain(query.topic_entity, query.relation_chain)
    disclosures_by_owner = {owner.name: len(owner.kg.triples) for owner in owners}
    certificates = [_make_certificate(answer, evidence, ["union_reasoner"]) for answer in sorted(answers)]
    return _result(answers, certificates, len(owners), len(query.relation_chain), disclosures_by_owner, evidence)


# --------------------------------------------------------------------------
# DECENT
# --------------------------------------------------------------------------
def run_decent(
    query: QueryExample,
    owners: list[OwnerAgent],
    audit: NoUnionAudit,
    budget: float | None = None,
    binding_cost: float = 1.0,
    certificate_mode: str = "raw",
    challenge_rate: float = 1.0,
    selector: str = "coverage",
    seed: int = 0,
    **_: object,
) -> dict[str, object]:
    """DECENT: bounded-disclosure evidence exchange.

    Per hop, owners first reply with a filter (how many bindings they could
    contribute and at what triple cost). The coordinator then requests binding sets
    greedily, never exceeding the per-query disclosure budget. Answers whose
    certificates cannot be paid for are abstained on.
    """
    budget = INF_BUDGET if budget is None else float(budget)
    route = _route_relation_owners(owners)
    frontier = {query.topic_entity}
    disclosures_by_owner = {owner.name: 0 for owner in owners}
    hop_provenance: list[dict[str, list[tuple[str, Triple]]]] = []
    messages = 0
    rounds = 0
    spent = 0.0
    budget_exhausted = False

    for relation in query.relation_chain:
        rounds += 1
        candidates: list[tuple[OwnerAgent, set[str], list[Triple]]] = []
        for owner in route.get(relation, []):
            found, evidence = owner.local_step(frontier, relation)
            if not found:
                continue
            # Free channel: a counting filter, zero triples, zero bindings.
            audit.record_message(
                Message(sender="coordinator", recipient=owner.name, kind="request", payload={"relation": relation, "mode": "filter"}),
            )
            audit.record_message(
                Message(
                    sender=owner.name,
                    recipient="coordinator",
                    kind="filter",
                    payload={"relation": relation, "reachable_count": len(found), "triple_cost": len(evidence)},
                ),
                bits=log2(len(found) + 1),
            )
            messages += 2
            candidates.append((owner, found, evidence))

        covered: set[str] = set()
        provenance: dict[str, list[tuple[str, Triple]]] = defaultdict(list)
        remaining = list(candidates)
        selector_rng = random.Random((seed, rounds).__hash__())
        while remaining:
            # Owner selection rule:
            #   coverage             most new bindings first (default)
            #   marginal_disclosure  fewest triples revealed per new binding
            #   latency              smallest local shard first
            #   random               uniform at random
            if selector == "marginal_disclosure":
                remaining.sort(key=lambda item: (
                    len(item[2]) / max(1, len(item[1] - covered)),
                    -len(item[1] - covered),
                    item[0].name,
                ))
            elif selector == "latency":
                remaining.sort(key=lambda item: (len(item[0].kg.triples), item[0].name))
            elif selector == "random":
                selector_rng.shuffle(remaining)
            else:
                remaining.sort(key=lambda item: (-len(item[1] - covered), item[0].name))
            owner, found, evidence = remaining.pop(0)
            new_bindings = sorted(found - covered)
            if not new_bindings:
                continue
            room = budget - spent
            if binding_cost <= 0 or room == INF_BUDGET:
                affordable = len(new_bindings)
            else:
                affordable = int(room // binding_cost)
            take = new_bindings[: max(0, affordable)]
            if not take:
                budget_exhausted = True
                break
            audit.record_message(
                Message(
                    sender=owner.name,
                    recipient="coordinator",
                    kind="binding_set",
                    payload={"relation": relation, "source_bindings": sorted({t.head for t in evidence})},
                ),
                [],
                take,
            )
            messages += 1
            spent += binding_cost * len(take)
            taken = set(take)
            covered |= taken
            for triple in evidence:
                if triple.tail in taken:
                    provenance[triple.tail].append((owner.name, triple))
            if len(take) < len(new_bindings):
                budget_exhausted = True
                break

        if not covered:
            frontier = set()
            break
        hop_provenance.append(provenance)
        frontier = covered
        if budget_exhausted:
            break

    if len(hop_provenance) < len(query.relation_chain):
        # The walk stopped early; nothing downstream can be certified.
        frontier = set() if len(hop_provenance) < len(query.relation_chain) else frontier

    return _backward_certificate_pass(
        query=query,
        answers=frontier,
        hop_provenance=hop_provenance,
        audit=audit,
        disclosures_by_owner=disclosures_by_owner,
        messages=messages,
        rounds=rounds,
        budget=budget,
        spent=spent,
        certificate_mode=certificate_mode,
        challenge_rate=challenge_rate,
        seed=seed,
        extra={"budget_exhausted": budget_exhausted},
    )


def _backward_certificate_pass(
    query: QueryExample,
    answers: set[str],
    hop_provenance: list[dict[str, list[tuple[str, Triple]]]],
    audit: NoUnionAudit,
    disclosures_by_owner: dict[str, int],
    messages: int,
    rounds: int,
    budget: float,
    spent: float,
    certificate_mode: str = "raw",
    challenge_rate: float = 1.0,
    seed: int = 0,
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    """Pull minimal support for each candidate answer, cheapest answer first.

    Support already disclosed for an earlier answer is reused at no additional cost.
    """
    max_answers = int(query.metadata.get("max_answers", 0) or 0)
    candidates = sorted(answers)
    if len(hop_provenance) < len(query.relation_chain):
        candidates = []

    rng = random.Random(f"{seed}:{query.query_id}:cert")
    disclosed: set[tuple[str, str, str]] = set()
    certificates: list[EvidenceCertificate] = []
    certificate_evidence: list[Triple] = []
    accepted: set[str] = set()
    plans: dict[str, list[tuple[str, Triple]]] = {}

    for answer in candidates:
        plan = _support_plan(answer, hop_provenance, disclosed)
        if plan is not None:
            plans[answer] = plan

    def undisclosed_cost(answer: str) -> tuple[int, str]:
        plan = plans[answer]
        return (sum(1 for _, triple in plan if triple.as_tuple() not in disclosed), answer)

    pending = sorted(plans, key=undisclosed_cost)
    for answer in pending:
        if max_answers > 0 and len(accepted) >= max_answers:
            break
        plan = _support_plan(answer, hop_provenance, disclosed)
        if plan is None:
            continue
        new_triples = [(o, t) for o, t in plan if t.as_tuple() not in disclosed]
        # In hash mode the owner returns a commitment instead of the triples. Raw support
        # crosses the boundary only when challenged, at rate ``challenge_rate``.
        challenged = certificate_mode == "raw" or rng.random() < challenge_rate
        if not challenged:
            for owner_name, triple in new_triples:
                audit.record_message(
                    Message(sender=owner_name, recipient="coordinator", kind="certificate_hash", payload={"relation": triple.relation, "answer": answer}),
                    [],
                    [],
                    bits=1.0,
                )
            messages += 2 * len(new_triples)
            accepted.add(answer)
            certificates.append(_make_certificate(answer, [t for _, t in plan], [o for o, _ in plan]))
            continue
        if spent + len(new_triples) > budget:
            continue  # cannot certify this answer within budget -> abstain on it
        for owner_name, triple in new_triples:
            audit.record_message(
                Message(sender="coordinator", recipient=owner_name, kind="request", payload={"relation": triple.relation, "mode": "certificate"}),
            )
            audit.record_message(
                Message(sender=owner_name, recipient="coordinator", kind="evidence_certificate", payload={"relation": triple.relation, "answer": answer}),
                [triple],
                [triple.tail],
            )
            disclosed.add(triple.as_tuple())
            disclosures_by_owner[owner_name] = disclosures_by_owner.get(owner_name, 0) + 1
            certificate_evidence.append(triple)
            spent += 1
        messages += 2 * len(new_triples)
        accepted.add(answer)
        certificates.append(
            _make_certificate(answer, [t for _, t in plan], [o for o, _ in plan])
        )

    payload = dict(extra or {})
    payload["disclosure_spent"] = spent
    return _result(accepted, certificates, messages, rounds, disclosures_by_owner, certificate_evidence, payload)


def _support_plan(
    answer: str,
    hop_provenance: list[dict[str, list[tuple[str, Triple]]]],
    disclosed: set[tuple[str, str, str]],
) -> list[tuple[str, Triple]] | None:
    """Cheapest backward support chain for one answer, preferring already-disclosed triples."""
    current = answer
    plan: list[tuple[str, Triple]] = []
    for hop_index in range(len(hop_provenance) - 1, -1, -1):
        options = hop_provenance[hop_index].get(current)
        if not options:
            return None
        options = sorted(options, key=lambda item: (item[1].as_tuple() not in disclosed, item[0], item[1].as_tuple()))
        owner_name, triple = options[0]
        plan.append((owner_name, triple))
        current = triple.head
    plan.reverse()
    return plan


def run_random_gossip(
    query: QueryExample,
    owners: list[OwnerAgent],
    audit: NoUnionAudit,
    seed: int = 0,
    **_: object,
) -> dict[str, object]:
    """Ownership-respecting control: owners are polled in random order per hop."""
    rng = random.Random(f"{seed}:{query.query_id}")
    route = _route_relation_owners(owners)
    frontier = {query.topic_entity}
    hop_provenance: list[dict[str, list[tuple[str, Triple]]]] = []
    disclosures_by_owner = {owner.name: 0 for owner in owners}
    messages = 0
    rounds = 0

    for relation in query.relation_chain:
        rounds += 1
        pool = list(route.get(relation, []))
        rng.shuffle(pool)
        covered: set[str] = set()
        provenance: dict[str, list[tuple[str, Triple]]] = defaultdict(list)
        for owner in pool:
            found, evidence = owner.local_step(frontier, relation)
            if not found:
                continue
            audit.record_message(
                Message(sender=owner.name, recipient="coordinator", kind="binding_set", payload={"relation": relation}),
                [],
                sorted(found),
            )
            messages += 1
            covered |= found
            for triple in evidence:
                provenance[triple.tail].append((owner.name, triple))
        if not covered:
            frontier = set()
            break
        hop_provenance.append(provenance)
        frontier = covered

    return _backward_certificate_pass(
        query=query,
        answers=frontier,
        hop_provenance=hop_provenance,
        audit=audit,
        disclosures_by_owner=disclosures_by_owner,
        messages=messages,
        rounds=rounds,
        budget=INF_BUDGET,
        spent=0.0,
    )
