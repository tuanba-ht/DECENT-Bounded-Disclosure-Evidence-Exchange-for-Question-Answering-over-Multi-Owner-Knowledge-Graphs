from __future__ import annotations

from collections import defaultdict

from decent.types import Triple


class KnowledgeGraph:
    def __init__(self, triples: list[Triple]) -> None:
        self.triples = triples
        self.forward: dict[tuple[str, str], list[str]] = defaultdict(list)
        self.forward_triples: dict[str, list[Triple]] = defaultdict(list)
        self.by_relation: dict[str, list[Triple]] = defaultdict(list)
        for triple in triples:
            self.forward[(triple.head, triple.relation)].append(triple.tail)
            self.forward_triples[triple.head].append(triple)
            self.by_relation[triple.relation].append(triple)

    @classmethod
    def from_tsv(cls, path: str) -> "KnowledgeGraph":
        triples: list[Triple] = []
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                head, relation, tail = line.split("\t")
                triples.append(Triple(head=head, relation=relation, tail=tail))
        return cls(triples)

    def follow_chain(self, start_entity: str, relations: list[str]) -> tuple[set[str], list[Triple]]:
        frontier = {start_entity}
        evidence: list[Triple] = []
        for relation in relations:
            next_frontier: set[str] = set()
            for entity in frontier:
                tails = self.forward.get((entity, relation), [])
                for tail in tails:
                    next_frontier.add(tail)
                    evidence.append(Triple(entity, relation, tail))
            frontier = next_frontier
            if not frontier:
                break
        return frontier, evidence

    def relation_chains_between(
        self,
        start_entity: str,
        target_entity: str,
        hops: int,
        limit: int = 100,
    ) -> list[list[str]]:
        chains: list[list[str]] = []

        def dfs(current: str, depth: int, chain: list[str]) -> None:
            if len(chains) >= limit:
                return
            if depth == hops:
                if current == target_entity:
                    chains.append(chain.copy())
                return
            for triple in self.forward_triples.get(current, []):
                chain.append(triple.relation)
                dfs(triple.tail, depth + 1, chain)
                chain.pop()

        dfs(start_entity, 0, [])
        return chains
