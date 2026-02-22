from collections import defaultdict
from math import sqrt
from typing import Iterable


def cosine_similarity(a: dict[int, float], b: dict[int, float]) -> float:
    overlap = set(a) & set(b)
    if not overlap:
        return 0.0

    dot = sum(a[movie] * b[movie] for movie in overlap)
    mag_a = sqrt(sum(score * score for score in a.values()))
    mag_b = sqrt(sum(score * score for score in b.values()))

    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def weighted_critic_score(
    critic_reviews: Iterable[tuple[float, float]],
) -> float | None:
    """
    critic_reviews: iterable of (critic_similarity, critic_movie_rating)
    """
    numerator = 0.0
    denominator = 0.0

    for similarity, rating in critic_reviews:
        if similarity <= 0:
            continue
        numerator += similarity * rating
        denominator += similarity

    if denominator == 0:
        return None
    return round(numerator / denominator, 2)


def to_user_rating_map(rows: Iterable[dict]) -> dict[int, dict[int, float]]:
    ratings: dict[int, dict[int, float]] = defaultdict(dict)
    for row in rows:
        ratings[row["user_id"]][row["tmdb_movie_id"]] = row["rating"]
    return dict(ratings)
