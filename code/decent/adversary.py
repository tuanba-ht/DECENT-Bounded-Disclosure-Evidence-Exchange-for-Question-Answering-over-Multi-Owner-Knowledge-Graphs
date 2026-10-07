from __future__ import annotations

from collections import defaultdict


class ShardReconstructionAdversary:
    """Transcript-only reconstruction adversary (implicit disclosure channel).

    Reads the message log, never a shard, and guesses each owner's triples:

    1. a triple sent by owner ``o`` belongs to ``o``'s shard;
    2. a ``binding_set`` from ``o`` for relation ``r`` implies a triple ``(h, r, t)``
       in ``o``'s shard for some source binding ``h`` and returned binding ``t``.

    Scored by precision and recall against each true shard, restricted to the
    triples the query set touches.
    """

    def __init__(self) -> None:
        self.certain: dict[str, set[tuple[str, str, str]]] = defaultdict(set)
        self.inferred: dict[str, set[tuple[str, str, str]]] = defaultdict(set)

    def observe(self, transcript: list[dict[str, object]]) -> None:
        for entry in transcript:
            sender = str(entry["sender"])
            if not sender.startswith("owner_"):
                continue
            for triple in entry.get("triples", []) or []:
                self.certain[sender].add(tuple(triple))
            relation = entry.get("relation")
            bindings = entry.get("bindings") or []
            sources = entry.get("source_bindings") or []
            if not relation or not bindings or not sources:
                continue
            if len(bindings) * len(sources) > 5000:
                sources = sources[:50]
                bindings = bindings[:100]
            for head in sources:
                for tail in bindings:
                    self.inferred[sender].add((head, str(relation), tail))

    def report(
        self,
        true_shards: dict[str, set[tuple[str, str, str]]],
        relevant: set[tuple[str, str, str]] | None = None,
    ) -> dict[str, object]:
        rows: dict[str, dict[str, float]] = {}
        tot_hit = tot_guess = tot_relevant = 0
        for owner, truth in true_shards.items():
            target = truth if relevant is None else (truth & relevant)
            guess = self.certain[owner] | self.inferred[owner]
            hit = len(guess & truth)
            rows[owner] = {
                "guessed": len(guess),
                "certain": len(self.certain[owner]),
                "hits": hit,
                "precision": hit / len(guess) if guess else 0.0,
                "recall_relevant": len(guess & target) / len(target) if target else 0.0,
            }
            tot_hit += hit
            tot_guess += len(guess)
            tot_relevant += len(target)
        micro_recall = 0.0
        if tot_relevant:
            micro_recall = sum(
                len((self.certain[o] | self.inferred[o]) & (t if relevant is None else t & relevant))
                for o, t in true_shards.items()
            ) / tot_relevant
        return {
            "disc_I_precision": tot_hit / tot_guess if tot_guess else 0.0,
            "disc_I_recall_relevant": micro_recall,
            "reconstructed_triples": tot_hit,
            "guessed_triples": tot_guess,
            "relevant_triples": tot_relevant,
            "per_owner": rows,
        }
