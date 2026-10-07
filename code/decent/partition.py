from __future__ import annotations

import hashlib
import random
from collections import defaultdict

from decent.kg import KnowledgeGraph
from decent.types import Triple


def relation_family_partition(kg: KnowledgeGraph, num_owners: int, seed: int = 0) -> dict[str, list[Triple]]:
    owners: dict[str, list[Triple]] = defaultdict(list)
    relations = sorted(kg.by_relation)
    if seed:
        random.Random(seed).shuffle(relations)
    for index, relation in enumerate(relations):
        owner = f"owner_{index % num_owners}"
        owners[owner].extend(kg.by_relation[relation])
    return dict(owners)


def hash_partition(kg: KnowledgeGraph, num_owners: int, seed: int = 0) -> dict[str, list[Triple]]:
    owners: dict[str, list[Triple]] = defaultdict(list)
    for triple in kg.triples:
        digest = hashlib.sha1(f"{seed}|".encode("utf-8") + "|".join(triple.as_tuple()).encode("utf-8")).hexdigest()
        owner = f"owner_{int(digest[:8], 16) % num_owners}"
        owners[owner].append(triple)
    return dict(owners)


def community_partition(kg: KnowledgeGraph, num_owners: int, seed: int = 0) -> dict[str, list[Triple]]:
    """Split by connected region, with balanced owner sizes.

    Each owner holds a region of the graph, so a chain crosses a boundary only where
    regions touch. Implemented as multi-source BFS that grows all regions in lockstep
    under a size cap; plain label propagation collapses to one giant community on
    densely connected graphs such as MetaQA.
    """
    adjacency: dict[str, set[str]] = defaultdict(set)
    for triple in kg.triples:
        adjacency[triple.head].add(triple.tail)
        adjacency[triple.tail].add(triple.head)

    entities = sorted(adjacency)
    if not entities:
        return {}

    rng = random.Random(seed)
    # Seeds are spread across the sorted entity list, then jittered by the seed, so the
    # regions start far apart instead of inside one neighbourhood.
    stride = max(1, len(entities) // num_owners)
    offset = rng.randrange(stride) if stride > 1 else 0
    frontier: list[list[str]] = []
    owner_of: dict[str, int] = {}
    for owner_id in range(num_owners):
        index = min(len(entities) - 1, owner_id * stride + offset)
        start_entity = entities[index]
        if start_entity in owner_of:  # collision on a tiny graph
            candidates = [e for e in entities if e not in owner_of]
            if not candidates:
                frontier.append([])
                continue
            start_entity = candidates[0]
        owner_of[start_entity] = owner_id
        frontier.append([start_entity])

    cap = -(-len(entities) // num_owners)  # ceiling, so the caps cover every entity
    sizes = [1 if f else 0 for f in frontier]
    # Grow every region one step at a time; a region that hits its cap stops taking new
    # entities, which is what keeps the split balanced instead of winner-takes-all.
    progress = True
    while progress:
        progress = False
        for owner_id in range(num_owners):
            if not frontier[owner_id] or sizes[owner_id] >= cap:
                continue
            nxt: list[str] = []
            for entity in frontier[owner_id]:
                for neighbour in sorted(adjacency[entity]):
                    if neighbour in owner_of or sizes[owner_id] >= cap:
                        continue
                    owner_of[neighbour] = owner_id
                    sizes[owner_id] += 1
                    nxt.append(neighbour)
                    progress = True
            frontier[owner_id] = nxt

    # Disconnected leftovers go to the smallest owner, keeping the balance.
    for entity in entities:
        if entity not in owner_of:
            owner_id = min(range(num_owners), key=lambda i: sizes[i])
            owner_of[entity] = owner_id
            sizes[owner_id] += 1

    owners: dict[str, list[Triple]] = defaultdict(list)
    for triple in kg.triples:
        owner_id = owner_of.get(triple.head, owner_of.get(triple.tail, 0))
        owners[f"owner_{owner_id}"].append(triple)
    return dict(owners)
