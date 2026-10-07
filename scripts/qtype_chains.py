"""Map MetaQA question types to relation chains.

Each hop directory ships qa_{split}_qtype.txt, one line per question, naming the
question type ("movie_to_actor", "director_to_movie_to_genre"). A type is a node
path, so the relation chain follows directly.
"""
from __future__ import annotations

# Relation reached when leaving a movie node towards the named node type.
FROM_MOVIE = {
    "actor": "starred_actors",
    "director": "directed_by",
    "writer": "written_by",
    "genre": "has_genre",
    "language": "in_language",
    "year": "release_year",
    "tags": "has_tags",
    "tag": "has_tags",      # 1-hop uses the singular in "tag_to_movie"
    "imdbrating": "has_imdb_rating",
    "imdbvotes": "has_imdb_votes",
}


def chain_for(qtype: str) -> list[str]:
    """'actor_to_movie_to_genre' -> ['starred_actors__inv', 'has_genre']"""
    nodes = qtype.strip().split("_to_")
    chain: list[str] = []
    for left, right in zip(nodes, nodes[1:]):
        if left == "movie":
            if right not in FROM_MOVIE:
                raise ValueError(f"unknown node: {right} in {qtype}")
            chain.append(FROM_MOVIE[right])
        elif right == "movie":
            if left not in FROM_MOVIE:
                raise ValueError(f"unknown node: {left} in {qtype}")
            chain.append(FROM_MOVIE[left] + "__inv")
        else:
            raise ValueError(f"step does not pass through movie: {left}->{right} in {qtype}")
    return chain


def load_qtypes(path: str) -> list[str]:
    return [line.strip() for line in open(path, encoding="utf-8") if line.strip()]


if __name__ == "__main__":
    import sys

    for qt in sys.argv[1:] or ["movie_to_actor", "actor_to_movie_to_genre",
                               "movie_to_director_to_movie_to_year"]:
        print(f"{qt:40s} -> {chain_for(qt)}")
