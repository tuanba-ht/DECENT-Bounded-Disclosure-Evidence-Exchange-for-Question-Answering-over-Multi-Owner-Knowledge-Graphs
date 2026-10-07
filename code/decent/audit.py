from __future__ import annotations

from collections import defaultdict
from math import log2

from decent.messages import Message
from decent.types import Triple


class NoUnionAudit:
    """Disclosure ledger and no-union-view audit.

    Tracks what crosses an owner boundary:

    * ``disc_T``: distinct triples (explicit channel);
    * ``disc_B``: distinct bindings, i.e. entity ids. A filter or binding message
      reveals these without revealing any triple.

    A per-query transcript is kept for the reconstruction adversary.
    """

    def __init__(self, owner_names: list[str]) -> None:
        self.visible_triples: dict[str, set[tuple[str, str, str]]] = defaultdict(set)
        # Received triples are stored separately from the owner's own shard.
        self.received_triples: dict[str, set[tuple[str, str, str]]] = defaultdict(set)
        self.visible_bindings: dict[str, set[str]] = defaultdict(set)
        self.messages: list[Message] = []
        self.owner_names = owner_names
        # (sender, kind, triples, bindings) -- the wire log the adversary reads.
        self.transcript: list[dict[str, object]] = []
        self.disclosed_triples: set[tuple[str, str, str]] = set()
        self.disclosed_bindings: set[str] = set()
        # Distinct entities and relations that crossed a boundary, in addition to triples.
        self.disclosed_relations: set[str] = set()
        self.disclosed_entities: set[str] = set()
        self.bits_leaked: float = 0.0

    def register_local_graph(self, owner: str, triples: list[Triple]) -> None:
        for triple in triples:
            self.visible_triples[owner].add(triple.as_tuple())

    def record_message(
        self,
        message: Message,
        disclosed_triples: list[Triple] | None = None,
        disclosed_bindings: list[str] | None = None,
        bits: float = 0.0,
    ) -> None:
        disclosed_triples = disclosed_triples or []
        disclosed_bindings = disclosed_bindings or []
        self.messages.append(message)
        self.bits_leaked += bits
        for triple in disclosed_triples:
            key = triple.as_tuple()
            self.visible_triples[message.recipient].add(key)
            if message.recipient != message.sender:
                self.received_triples[message.recipient].add(key)
                self.disclosed_triples.add(key)
                self.disclosed_relations.add(triple.relation)
                self.disclosed_entities.update((triple.head, triple.tail))
        for binding in disclosed_bindings:
            self.visible_bindings[message.recipient].add(binding)
            if message.recipient != message.sender:
                self.disclosed_bindings.add(binding)
                self.disclosed_entities.add(binding)
        self.transcript.append(
            {
                "sender": message.sender,
                "recipient": message.recipient,
                "kind": message.kind,
                "relation": message.payload.get("relation"),
                "triples": [triple.as_tuple() for triple in disclosed_triples],
                "bindings": list(disclosed_bindings),
                "source_bindings": list(message.payload.get("source_bindings", [])),
            }
        )

    def union_violation(self, union_size: int) -> bool:
        return any(len(visible) >= union_size for visible in self.visible_triples.values())

    def witness_violation(self, witness_triples: list[Triple]) -> bool:
        """True if some party holds a complete gold witness it could not assemble alone.

        Stricter than the union-size check: one full support chain is enough. An owner
        is judged on what it received, so a witness already contained in its own shard
        does not count.
        """
        if not witness_triples:
            return False
        witness = {triple.as_tuple() for triple in witness_triples}
        for party, visible in self.visible_triples.items():
            if not witness <= visible:
                continue
            if party in self.owner_names:
                local_only = visible - self.received_triples.get(party, set())
                if witness <= local_only:
                    continue  # it already held the whole chain; nothing was disclosed to it
            return True
        return False

    def witness_parties(self, witness_triples: list[Triple]) -> int:
        """Number of parties holding a complete gold witness they could not assemble alone.

        Separates topologies that ``witness_violation`` cannot: a star coordinator
        exposes the chain to one hub, a broadcast bus to every owner on the bus.
        """
        if not witness_triples:
            return 0
        witness = {triple.as_tuple() for triple in witness_triples}
        count = 0
        for party, visible in self.visible_triples.items():
            if not witness <= visible:
                continue
            if party in self.owner_names:
                local_only = visible - self.received_triples.get(party, set())
                if witness <= local_only:
                    continue
            count += 1
        return count

    def owner_entropy(self, disclosures_by_owner: dict[str, int]) -> float:
        """Shannon entropy (bits) of how disclosure is spread across owners.

        Zero means one owner carried the whole cost; log2(k) means k owners shared it
        evenly.
        """
        total = sum(count for count in disclosures_by_owner.values() if count > 0)
        if total <= 0:
            return 0.0
        entropy = 0.0
        for count in disclosures_by_owner.values():
            if count > 0:
                p = count / total
                entropy -= p * log2(p)
        return round(entropy, 4)

    def summary(
        self,
        union_size: int,
        disclosures_by_owner: dict[str, int],
        witness_triples: list[Triple] | None = None,
    ) -> dict[str, object]:
        return {
            "union_violation": self.union_violation(union_size),
            "witness_violation": self.witness_violation(witness_triples or []),
            "witness_parties": self.witness_parties(witness_triples or []),
            "message_count": len(self.messages),
            "disc_T": len(self.disclosed_triples),
            "disc_B": len(self.disclosed_bindings),
            "disc_R": len(self.disclosed_relations),
            "disc_E": len(self.disclosed_entities),
            "bits_leaked": round(self.bits_leaked, 3),
            "owner_visible_sizes": {owner: len(self.visible_triples[owner]) for owner in self.owner_names},
            "owner_entropy": self.owner_entropy(disclosures_by_owner),
        }
